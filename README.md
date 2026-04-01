<div align="center">

# 🕶️ Smart Glasses Prototype for the Visually Impaired
**A modular, hybrid-AI wearable system built to make the world accessible.**

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg?logo=opencv&logoColor=white)](https://opencv.org/)
[![Groq](https://img.shields.io/badge/LLaMA%203.2-Powered%20by%20Groq-orange.svg)](https://groq.com)

</div>

---

## 🌟 The Vision
Imagine navigating the physical world when you can't see it. This project is a V1 software prototype for **wearable smart glasses** designed to give visually impaired individuals radical independence. 

Instead of relying on a single slow API or a basic sensor, this architecture uses a **Hybrid-AI approach**:
1. **The Reflex Instinct (Local)**: A lightweight, zero-latency local model that constantly scans for incoming physical hazards (cars, stairs, people) and shouts instantly if something gets too close.
2. **The Analytical Brain (Cloud)**: A powerful Vision Language Model (LLaMA via Groq) that the user can trigger on demand to read texts, analyze scenes, and understand colors.

---

## 🚀 Key Features

### 🛡️ Local Intelligence (Always On. Zero Latency. No WiFi Required)
*   **Real-time Hazard Detection**: Uses a `MobileNet-SSD` model to continuously track the proximity of objects in the camera feed.
*   **Smart Spatial Memory**: To prevent annoying repetitive beeps, the system tracks stationary objects. If you stand in front of a chair, it warns you once and mutes itself for 30 seconds... **unless** that chair suddenly moves toward you, triggering an instant override alert!
*   **Position-Aware Face Tracking (`F`)**: Press `F` to instantly scan the room. It will tell you exactly how many people are nearby and where they are standing (e.g., *"One person detected nearby on your left"*).
*   **Offline Document Reader (`R`)**: Uses `Tesseract OCR` to read street signs, books, and labels instantly without sending data to the cloud.

### 🧠 Cloud Intelligence (On-Demand High-Level Analysis)
*   **Scene Description (`SPACE`)**: Takes a snapshot and asks LLaMA 3.2 Vision: *"What is directly in front of me?"*
*   **Color Check (`C`)**: Identifies the primary color in the center of the frame. Useful for picking clothes or identifying items!
*   **Currency Check (`N`)**: Instantly identifies paper banknotes. 

### 🔊 Advanced Audio Control
Standard text-to-speech tools often freeze the camera or talk over themselves. This project uses a **custom multi-threaded audio queue**. If the system is casually reading a book to you, but a car suddenly approaches, the system *instantly kills the reading queue* and prioritizes the "Danger!" alert.

---

## 🛠️ How to Build It Yourself

### 1. Prerequisites
You need **Tesseract OCR** installed on your computer for the offline `R` key to work.
*   **Windows**: Download and install from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki). 

### 2. Install Dependencies
Clone the repository and install the required Python packages:

```bash
git clone https://github.com/gurneev-singh/blind-assistance-tool.git
cd blind-assistance-tool
pip install -r requirements.txt
```

### 3. Setup Your Keys
This project uses **Groq** because it provides astonishingly fast LLaMA Vision inference (30 requests/minute on the free tier!).

Create a `.env` file in the root folder (use `.env.example` as a template):
```env
GROQ_API_KEY=your_super_secret_groq_api_key
CAMERA_INDEX=0
TESSERACT_PATH="C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### 4. Run It!
```bash
python main.py
```
*(Make sure to click the camera window before pressing the hotkeys `SPACE`, `C`, `N`, `F`, or `R`!)*

---

## 🔮 The Hardware Roadmap (What's Next?)

Right now, this V1 software is optimized to run on a laptop to perfect the AI architecture. But a laptop isn't very wearable. 

**Milestone 2 (The IoT Transition)**
*   **Raspberry Pi 5**: Migrate the codebase to run entirely headlessly on a low-power SBC in a backpack or pocket.
*   **LiDAR / Ultrasonic Fusion**: The current V1 uses AI bounding boxes to approximate distance. V2 will integrate physical `HC-SR04` ultrasonic sensors for millimeter-perfect hazard proximity.
*   **Voice Activation**: Replacing keyboard shortcuts with offline wake-word detection (e.g., *"Hey Glasses, what's in front of me?"*)

---

<br>

<div align="center">
  
### 👨‍💻 About the Developer
**Built with passion by Gurneev Singh (16)**  
*I built this because I believe AI shouldn't just be a chatbot on a screen—it should be a tool that physically empowers people and makes the physical world accessible to everyone.*

</div>
