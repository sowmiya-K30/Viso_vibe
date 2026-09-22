# Viso Vibe 🎶

Viso Vibe is an AI-powered, emotion-driven music player that recommends music based on your current mood. By using your camera, Viso Vibe analyzes facial expressions, detects your emotional state, and recommends a YouTube music playlist based on the detected mood.

## ✨ Features

* **Live Emotion Detection:** Uses computer vision with OpenCV and ONNX to detect faces and analyze emotions in real time.
* **Dynamic 4-Mood Categorization:** Maps detected emotions to four core moods:

  * ☀️ **Happy** – Radiant & Electric
  * 🌊 **Sad** – Deep & Reflective
  * 🌿 **Calm** – Serene & Balanced
  * 🔥 **Angry** – Raw & Intense
* **Seamless Music Integration:** Recommends curated YouTube playlists based on the detected mood.
* **Premium UI/UX:** Built with Streamlit and customized with modern HTML/CSS, featuring a dark-themed interface, animated visual elements, glassmorphism UI components, and an interactive media player.
* **Audio Feedback:** Uses Text-to-Speech (TTS) to provide audio feedback about the detected emotion.

## 🛠️ Tech Stack

* **UI:** Streamlit, HTML, CSS, JavaScript
* **Programming:** Python
* **Computer Vision:** OpenCV
* **AI/ML:** ONNX Runtime
* **Image Processing:** Pillow (PIL)
* **Audio Processing:** gTTS (Google Text-to-Speech)
* **Music Integration:** YouTube IFrame Player API
* **Fonts:** Google Fonts – Inter, Space Mono

## ⚠️ Model Files

The `emotion.onnx` model file is required for emotion detection but is not included in this repository because the file exceeds GitHub's file upload size limit.

To run the emotion detection feature locally, download the required `emotion.onnx` model file and place it in the project directory as required by the application.

> **Note:** Both `detection.onnx` and `emotion.onnx` are required for the emotion detection functionality to work correctly.

## 🚀 Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/sowmiya-K30/Viso_vibe.git
cd Viso_vibe
```

### 2. Install the dependencies

Make sure Python 3.8 or later is installed.

```bash
pip install -r requirements.txt
```

### 3. Add the emotion model

Place the required `emotion.onnx` file in the project directory.

Your project should contain:

```text
Viso_vibe/
├── app.py
├── util.py
├── requirements.txt
├── detection.onnx
└── emotion.onnx
```

### 4. Run the application

```bash
python -m streamlit run app.py
```

The application will open in your browser.

## ☁️ Deploying on Streamlit Community Cloud

Viso Vibe can be deployed using Streamlit Community Cloud.

1. Push the project to GitHub.
2. Open Streamlit Community Cloud.
3. Click **New App**.
4. Select the GitHub repository:

```text
sowmiya-K30/Viso_vibe
```

5. Select the `main` branch.
6. Set the main file path to:

```text
app.py
```

7. Click **Deploy**.

> **Important:** Since `emotion.onnx` is not included in this GitHub repository, the deployed application will require another method to access the model file.

## 📁 Repository Structure

```text
Viso_vibe/
├── app.py                  # Main Streamlit application
├── util.py                 # Emotion detection and inference utilities
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── detection.onnx         # Face detection model
└── emotion.onnx            # Emotion classification model (not uploaded to GitHub)
```

## 🎯 How It Works

```text
Camera Input
     ↓
Face Detection
     ↓
Emotion Detection
     ↓
Emotion Classification
     ↓
Mood Categorization
     ↓
YouTube Music Recommendation
     ↓
Audio Feedback
```

The application captures an image from the camera, detects the face, analyzes the facial expression using an ONNX emotion recognition model, maps the detected emotion to a mood category, and recommends a corresponding YouTube playlist.

## 🎵 Mood Categories

| Detected Mood | Music Experience              |
| ------------- | ----------------------------- |
| ☀️ Happy      | Energetic and uplifting music |
| 🌊 Sad        | Deep and reflective music     |
| 🌿 Calm       | Relaxing and peaceful music   |
| 🔥 Angry      | Intense and powerful music    |

## 📌 Important Notes

* Python 3.8+ is recommended.
* A working camera is required for live emotion detection.
* Internet access is required for YouTube music integration and Google Text-to-Speech.
* The `emotion.onnx` model must be added locally before running the complete application.
* The project uses `opencv-python-headless` for compatibility with server environments.

## 📜 License

This project is created for educational and entertainment purposes. Please ensure compliance with YouTube's Terms of Service when embedding or streaming YouTube content.
