# Finger Controller

A computer vision project that enables device control through hand gestures and finger commands using MediaPipe and OpenCV.

## 🎯 Features

- **Hand Gesture Recognition**: Real-time hand tracking using MediaPipe
- **Finger Command Detection**: Control devices based on finger positions
- **Face Detection**: Integrated facial recognition capabilities
- **ESP32 Integration**: Wireless communication with IoT devices
- **Real-time Video Processing**: Live camera feed analysis

## 📋 Requirements

- Python 3.8+
- Webcam
- ESP32 microcontroller (optional, for IoT control)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Shashankex09/finger_controller.git
   cd finger_controller
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Basic Hand Gesture Control
```bash
python src/commands_by_fingers.py
```

### Face Detection
```bash
python src/face_detection.py
```

## 📁 Project Structure

```
finger_controller/
├── src/
│   ├── commands_by_fingers.py    # Main gesture control script
│   ├── face_detection.py         # Face detection module
│   └── hand_landmarker.task      # MediaPipe model file
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── .gitignore                   # Git ignore rules
```

## 🔧 Configuration

- **ESP32_IP**: Set your ESP32's IP address in the scripts
- **Camera Settings**: Adjust camera resolution in the code
- **Detection Confidence**: Modify `min_detection_confidence` values

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## � Hardware Setup (ESP + Servo)

### Required Components
- ESP32 or ESP8266 microcontroller
- Servo motor (SG90 or similar)
- Jumper wires
- Power supply (5V for servo)

### Wiring Diagram
```
ESP32/ESP8266          Servo
─────────────          ─────
  GND  ──────────────  GND
  5V   ──────────────  VCC  (or external 5V supply)
  GPIO 13 ───────────  Signal
```

### ESP32 Pin Options
- **GPIO 13** (recommended - used in code)
- GPIO 12, GPIO 14, GPIO 27, GPIO 26, GPIO 25, GPIO 33, GPIO 32

### ESP8266 Pin Options
- **GPIO 4** (D2)
- GPIO 5 (D1)
- GPIO 12 (D6)
- GPIO 13 (D7)
- GPIO 14 (D5)

### Upload Instructions

1. **Open Arduino IDE** (or PlatformIO)
2. **Install ESP32/ESP8266 board support** if not already installed
3. **Open the sketch**: `face_tracking_servo.ino`
4. **Select your board**:
   - For ESP32: Tools → Board → ESP32 Dev Module
   - For ESP8266: Tools → Board → NodeMCU 1.0
5. **Set COM port**: Tools → Port → (your ESP's COM port)
6. **Upload the code**
7. **Open Serial Monitor** (115200 baud) to see confirmation messages

### Testing the Connection

1. **Test servo first** (without face detection):
   ```bash
   python test_servo.py
   ```
   This will let you manually control the servo to verify wiring.

2. **Run face tracking**:
   ```bash
   python src/face_detection.py
   ```
3. **Move your face** - the servo should follow!
4. **Check Serial Monitor** for "OK" messages

### Troubleshooting

- **"Serial not connected"**: Check COM port and baud rate (115200)
- **Servo not moving**: Check wiring and power supply
- **"Invalid angle"**: Ensure servo limits match Python script (20-160)
- **ESP not responding**: Check if code uploaded successfully

### Advanced Configuration

- **Change servo pin**: Modify `SERVO_PIN` in the ESP code
- **Adjust servo range**: Change `SERVO_MIN` and `SERVO_MAX`
- **Change baud rate**: Update `BAUD_RATE` in both Python and ESP code