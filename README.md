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

## 🙏 Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for hand tracking
- [OpenCV](https://opencv.org/) for computer vision
- [Google](https://ai.google.dev/) for AI frameworks

## 📞 Support

If you have any questions or issues, please open an issue on GitHub.

---

**Made with ❤️ for computer vision enthusiasts**