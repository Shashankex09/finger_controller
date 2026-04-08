import cv2
import time
import numpy as np
import serial

# ── Config ─────────────────────────────
SERIAL_PORT = "COM21"
BAUD_RATE = 115200
FRAME_W, FRAME_H = 640, 480
CX = FRAME_W // 2
DEAD_X = 50
SERVO_MIN, SERVO_MAX = 20, 160
KP, KI, KD = 0.015, 0.00005, 0.008
COMMAND_DELAY = 0.05
last_send_time = time.time()

# ── Performance Optimizations ──────────
DETECT_EVERY_N_FRAMES = 2  # Run face detection every 2 frames (balanced)
DETECTION_SCALE = 0.75  # Downsize frame for faster detection (75% resolution)
current_frame = 0
last_face_pos = None  # Track last known position for smoothing

# ── PID Class ──────────────────────────
class PID:
    def __init__(self, kp, ki, kd):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.prev_err = 0
        self.integral = 0
        self.last_t = time.time()

    def compute(self, error):
        now = time.time()
        dt = max(now - self.last_t, 1e-4)
        self.last_t = now

        self.integral += error * dt
        derivative = (error - self.prev_err) / dt
        self.prev_err = error

        return self.kp * error + self.ki * self.integral + self.kd * derivative

pid = PID(KP, KI, KD)
servo_angle = 90

# ── Serial Setup ──────────────────────
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("[OK] Serial connected")
except Exception:
    print("[WARN] Serial not connected")
    ser = None


def send_angle(angle):
    global last_send_time
    
    current_time = time.time()
    
    # Only send if enough time has passed
    if current_time - last_send_time < COMMAND_DELAY:
        return False
    
    if ser and ser.is_open:
        cmd = f"A{int(angle):03d}\n"
        try:
            ser.write(cmd.encode())
            ser.flush()
            last_send_time = current_time
            
            # Non-blocking read (don't wait for response)
            try:
                if ser.in_waiting:
                    response = ser.readline().decode('utf-8', errors='ignore').strip()
                    if response and response.startswith("OK"):
                        pass  # Successfully received
            except:
                pass
            
            return True
        except Exception as e:
            print(f"Serial send error: {e}")
            return False
    
    return False

# ── MediaPipe Face Detection ──────────
use_mediapipe_tasks = False
cascade = None
face_detector = None

try:
    from mediapipe.tasks.python import vision
    from mediapipe.tasks.python.vision import FaceDetector, FaceDetectorOptions, VisionRunningMode
    use_mediapipe_tasks = True
    model_candidates = [
        "face_detector.task",
        "face_detection.task",
        "face_detection_short.task",
        "face_detection_front.task",
    ]
    model_asset = None
    for name in model_candidates:
        try:
            model_asset = vision.asset_path(name)
            break
        except Exception:
            continue

    if model_asset is None:
        raise FileNotFoundError("MediaPipe face detector model asset not found")

    face_options = FaceDetectorOptions(
        base_options=vision.BaseOptions(model_asset_path=model_asset),
        running_mode=VisionRunningMode.LIVE_STREAM,
        min_detection_confidence=0.6,
        min_suppression_threshold=0.3,
    )
    face_detector = FaceDetector.create_from_options(face_options)
    print("[OK] Using MediaPipe Tasks FaceDetector")
except Exception:
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml")
    print("[OK] Using OpenCV Haar cascade face detection")


def get_face_center(frame):
    global last_face_pos
    
    # Downscale for faster detection
    detect_frame = cv2.resize(frame, (int(FRAME_W * DETECTION_SCALE), int(FRAME_H * DETECTION_SCALE)))
    
    if use_mediapipe_tasks and face_detector:
        detect_rgb = cv2.cvtColor(detect_frame, cv2.COLOR_BGR2RGB)
        mp_image = vision.Image(image_format=vision.ImageFormat.SRGB, data=detect_rgb)
        detection_result = face_detector.detect_for_video(mp_image, int(time.time() * 1000))
        if not detection_result.detections:
            return None

        best = max(
            detection_result.detections,
            key=lambda d: d.bounding_box.width * d.bounding_box.height,
        )
        bbox = best.bounding_box
        x = int(bbox.origin_x * FRAME_W)
        y = int(bbox.origin_y * FRAME_H)
        w = int(bbox.width * FRAME_W)
        h = int(bbox.height * FRAME_H)
        
        result = (x + w // 2, y + h // 2, w, h)
        last_face_pos = result
        return result

    gray = cv2.cvtColor(detect_frame, cv2.COLOR_BGR2GRAY)
    
    # Better face detection with adjusted parameters for accuracy
    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,  # Smaller scale factor = more thorough
        minNeighbors=7,    # Stricter neighbor requirement = fewer false positives
        flags=cv2.CASCADE_SCALE_IMAGE,
        minSize=(50, 50),  # Lower minimum = better small face detection
    )
    
    if len(faces) == 0:
        return None
    
    # Get largest face
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    
    # Scale coordinates back to original resolution
    x = int(x / DETECTION_SCALE)
    y = int(y / DETECTION_SCALE)
    w = int(w / DETECTION_SCALE)
    h = int(h / DETECTION_SCALE)
    
    result = (x + w // 2, y + h // 2, w, h)
    last_face_pos = result
    return result

# ── Main Loop ──────────────────────────
cap = cv2.VideoCapture(0)
cap.set(3, FRAME_W)
cap.set(4, FRAME_H)

print("Running... Press Q to exit (Detection every {} frames at {}% resolution)".format(DETECT_EVERY_N_FRAMES, int(DETECTION_SCALE*100)))
prev_servo_angle = 90
frame_times = []
smoothed_face_x = CX
alpha = 0.7  # Smoothing factor (0.7 = more weight on current, less on history)

while True:
    frame_start = time.time()
    
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    
    # Run face detection every N frames
    if current_frame % DETECT_EVERY_N_FRAMES == 0:
        result = get_face_center(frame)
    else:
        result = None
    
    current_frame += 1

    if result:
        fx, fy, fw, fh = result
        # Smooth the face position using exponential moving average
        smoothed_face_x = alpha * fx + (1 - alpha) * smoothed_face_x
    elif last_face_pos:
        # Use last known position if detection fails (smoother tracking)
        fx, fy, fw, fh = last_face_pos
        smoothed_face_x = alpha * fx + (1 - alpha) * smoothed_face_x
    else:
        # No face found, don't update servo
        smoothed_face_x = CX
        cv2.putText(frame, "No Face Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
        cv2.imshow("Face Tracking Servo", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    # Use smoothed position for servo control
    err_x = smoothed_face_x - CX
    
    # Dead zone
    if abs(err_x) < DEAD_X:
        err_x = 0
    
    # PID correction
    correction = pid.compute(err_x)
    servo_angle += correction
    servo_angle = np.clip(servo_angle, SERVO_MIN, SERVO_MAX)
    
    # Send command if angle changed significantly
    if abs(servo_angle - prev_servo_angle) >= 1.5:
        send_angle(servo_angle)
        prev_servo_angle = servo_angle

    if result:
        # Draw only when fresh detection
        x1 = int(fx - fw / 2)
        y1 = int(fy - fh / 2)
        x2 = int(fx + fw / 2)
        y2 = int(fy + fh / 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.circle(frame, (int(fx), int(fy)), 5, (0, 255, 0), -1)

    # Performance monitoring (every 30 frames)
    frame_time = time.time() - frame_start
    frame_times.append(frame_time)
    if len(frame_times) > 30:
        frame_times.pop(0)
    
    if current_frame % 30 == 0:
        avg_time = np.mean(frame_times) * 1000
        fps = 1.0 / np.mean(frame_times) if np.mean(frame_times) > 0 else 0
        cv2.putText(frame, f"FPS: {fps:.1f} | Latency: {avg_time:.1f}ms", (10, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    cv2.putText(frame, f"Angle: {int(servo_angle):03d} | Error: {err_x:+.0f}px", (10, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    cv2.imshow("Face Tracking Servo", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
if ser:
    ser.close()
cv2.destroyAllWindows()
