import pathlib
import urllib.request
import urllib.error
import cv2
import numpy as np
import socket
from mediapipe.tasks.python.vision import hand_landmarker
from mediapipe.tasks.python.vision import drawing_utils
from mediapipe.tasks.python.vision.core import image as mp_image

# ================= UDP CONFIG =================
ESP_IP = "192.168.4.1"
PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ================= MODEL =================
MODEL_PATH = pathlib.Path("hand_landmarker.task")
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)

def download_model(path: pathlib.Path, url: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        print(f"Downloading MediaPipe model...")
        urllib.request.urlretrieve(url, path)
    except urllib.error.URLError:
        raise RuntimeError("Download failed. Place model manually.")

def ensure_model(path: pathlib.Path) -> None:
    if not path.exists():
        download_model(path, MODEL_URL)

def to_mp_image(frame: np.ndarray) -> mp_image.Image:
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return mp_image.Image(mp_image.ImageFormat.SRGB, rgb)

def normalized_landmark_to_pixel(landmark, width, height):
    return int(landmark.x * width), int(landmark.y * height)

# ================= MAIN =================
def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Camera not working")

    ensure_model(MODEL_PATH)
    landmarker = hand_landmarker.HandLandmarker.create_from_model_path(
        MODEL_PATH.as_posix()
    )

    prev_cmd = ""

    try:
        while True:

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)

            mp_img = to_mp_image(frame)
            result = landmarker.detect(mp_img)

            cmd = "S"   # default STOP

            if result.hand_landmarks:
                for idx, hand_landmarks in enumerate(result.hand_landmarks):

                    drawing_utils.draw_landmarks(
                        frame,
                        hand_landmarks,
                        hand_landmarker.HandLandmarksConnections.HAND_CONNECTIONS,
                    )

                    lm_list = []
                    h, w, _ = frame.shape

                    for landmark in hand_landmarks:
                        lm_list.append(
                            normalized_landmark_to_pixel(landmark, w, h)
                        )

                    handedness = result.handedness[idx][0].category_name

                    tips = [4, 8, 12, 16, 20]
                    fingers = []

                    # THUMB FIX
                    if handedness == "Right":
                        fingers.append(1 if lm_list[4][0] > lm_list[3][0] else 0)
                    else:
                        fingers.append(1 if lm_list[4][0] < lm_list[3][0] else 0)

                    # Other fingers
                    for i in range(1, 5):
                        if lm_list[tips[i]][1] < lm_list[tips[i] - 2][1] - 10:
                            fingers.append(1)
                        else:
                            fingers.append(0)

                    total_fingers = fingers.count(1)

                    # ================= COMMAND =================
                    if total_fingers == 0:
                        cmd = "S"
                        text = "STOP"
                    elif total_fingers == 1:
                        cmd = "F"
                        text = "FORWARD"
                    elif total_fingers == 2:
                        cmd = "L"
                        text = "LEFT"
                    elif total_fingers == 3:
                        cmd = "R"
                        text = "RIGHT"
                    elif total_fingers == 4:
                        cmd = "B"
                        text = "BACKWARD"
                    elif total_fingers == 5:
                        cmd = "S"
                        text = "STOP"

                    # DISPLAY
                    cv2.putText(frame, f"Fingers: {total_fingers}", (20, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 3)

                    cv2.putText(frame, text, (20, 150),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,0,0), 3)

            # ================= SEND ONLY IF CHANGED =================
            if cmd != prev_cmd:
                sock.sendto(cmd.encode(), (ESP_IP, PORT))
                print("Sent:", cmd)
                prev_cmd = cmd

            cv2.imshow("Hand Gesture Control", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
