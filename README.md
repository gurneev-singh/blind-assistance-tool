# 🕶️ Gurneev's Smart Glasses (V1 Prototype)

An advanced, modular, and hybrid-AI software foundation for smart glasses designed to assist visually impaired individuals. The system combines zero-latency local object detection for immediate hazard warnings with powerful cloud-based Vision Language Models (VLMs) for high-level scene understanding and text reading.

## ✨ Features

### 🛡️ Local Intelligence (Zero-Latency / Offline)
*   **Hazard Detection**: Continuously monitors the camera feed using MobileNet-SSD to detect obstacles (people, cars, chairs, etc.) and estimates their proximity.
*   **Smart Spatial Cooldowns**: Intelligently mutes alerts for stationary objects you are already aware of, but instantly overrides the mute if the object moves closer to you.
*   **Face Detection (`F`)**: Uses OpenCV Haar Cascades to instantly scan for human faces, announcing their relative position (left/center/right) and distance without needing internet.
*   **Text Reader (`R`)**: Uses offline Tesseract OCR to instantly read signs, books, and environmental text.

### 🧠 Cloud Intelligence (High-Level Analysis)
*   **Scene Description (`SPACE`)**: Captures a snapshot and sends it to Groq's blazing-fast LLaMA Vision model to provide a concise, natural language description of the environment.
*   **Color Check (`C`)**: Identifies the primary color in the center of the user's view.
*   **Currency ID (`N`)**: Identifies banknotes and currency values.

### 🔊 Audio Architecture
*   Fully threaded `gTTS` and `playsound` implementation.
*   **Non-blocking Priority Queue**: Critical danger alerts instantly clear the audio queue and interrupt lower-priority descriptions to ensure you never miss a hazard warning.

---

## 🛠️ Tech Stack & Architecture

*   **Language**: Python 3.x
*   **Computer Vision**: OpenCV (`cv2`)
*   **Local AI Models**: MobileNet-SSD (Caffe) for objects, Haar Cascades for faces.
*   **Cloud AI Models**: Groq (LLaMA 3.2 Vision)
*   **Text-to-Speech**: Google Text-to-Speech (`gTTS`)
*   **OCR**: Tesseract

---

## 🚀 Setup & Installation

### 1. Prerequisites
You must install Tesseract OCR on your system for the offline reading feature to work.
*   **Windows**: Download and install from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki). Keep note of the installation path.

### 2. Environment Setup
Clone the repository and install the Python dependencies:

```bash
git clone https://github.com/gurneev-singh/blind-assistance-tool.git
cd blind-assistance-tool
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory (you can use `.env.example` as a template) and add your API keys and paths:

```env
GROQ_API_KEY=your_groq_api_key_here
CAMERA_INDEX=0
TESSERACT_PATH="C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## 🎮 Usage & Controls

Run the main application:
```bash
python main.py
```

Click on the camera window that opens, and use the following keyboard shortcuts to interact with the glasses:

| Key | Action | Engine Used | Internet Required? |
| :--- | :--- | :--- | :---: |
| `SPACE` | Summarize the scene | Groq Vision (LLaMA) | Yes |
| `c` | Identify center color | Groq Vision (LLaMA) | Yes |
| `n` | Identify currency | Groq Vision (LLaMA) | Yes |
| `r` | Read visible text | Tesseract OCR | No |
| `f` | Detect faces & position | OpenCV | No |
| `q` | Quit application | System | No |

---

## 🔮 Future Roadmap (The Hardware Transition)

This V1 software prototype is currently designed to run on a laptop to finalize the AI architecture. The future roadmap details the transition into a physical, wearable IoT device.

### Milestone 2: The Edge Transition (Raspberry Pi)
*   **Hardware Porting**: Migrate the codebase to run efficiently on a Raspberry Pi 4 / 5 using a headless Linux environment.
*   **Sensor Fusion**: Replace the simulated camera-based distance estimation (.prototxt bounding boxes) with physical **Ultrasonic (HC-SR04)** or **LiDAR** sensors for millimeter-perfect hazard proximity detection.
*   **Model Quantization**: Optimize the local detectors (TFLite/ONNX INT8) to reduce power draw and battery consumption on portable hardware.

### Milestone 3: The Wearable Form Factor
*   **Voice Activation**: Replace keyboard shortcuts with local wake-word detection (e.g., "Hey Glasses, describe this") using Porcupine or PocketSphinx.
*   **Custom PCB**: Shrink the breadboard electronics down to a custom-printed circuit board.
*   **Enclosure**: 3D print a lightweight, thermal-managed frame that mounts directly to standard eyewear.

---
*Built with precision and care to make the physical world fully accessible.*
