# Viso Vibe 🎶

Viso Vibe is an AI-powered, emotion-driven music player that curates the perfect soundtrack based on your current mood. By simply looking at your camera, Viso Vibe analyzes your facial expression, detects your emotional state, and seamlessly plays a custom-tailored YouTube music playlist to match your frequency.

## ✨ Features

- **Live Emotion Detection:** Uses advanced computer vision (ONNX/OpenCV) to detect faces and analyze your mood in real-time.
- **Dynamic 4-Mood Categorization:** Maps your facial expression to one of four core emotional states:
  - ☀️ **Happy** (Radiant & Electric)
  - 🌊 **Sad** (Deep & Reflective)
  - 🌿 **Calm** (Serene & Balanced)
  - 🔥 **Angry** (Raw & Intense)
- **Seamless Music Integration:** Automatically plays a randomized, curated YouTube playlist corresponding to your detected emotion using a custom, invisible YouTube iframe API integration.
- **Premium UI/UX:** Built with Streamlit but heavily customized with modern HTML/CSS. Features a stunning dark mode aesthetic, animated particle visualizers, glassmorphism UI elements, and a custom interactive media player.
- **Audio Feedback:** Provides text-to-speech (TTS) audio feedback confirming your detected emotion.

## 🛠️ Tech Stack

- **Frontend/UI:** Streamlit, Custom HTML/CSS/JS, Google Fonts (Inter, Space Mono)
- **Backend/Logic:** Python
- **Computer Vision & AI:** OpenCV (`opencv-python-headless`), ONNX Runtime (`onnxruntime`), PIL (Pillow)
- **Audio Processing:** `gTTS` (Google Text-to-Speech)
- **Media Streaming:** YouTube IFrame Player API

## 🚀 Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LORDMOSTER/Viso-Vibe.git
   cd Viso-Vibe/VisoVibe
   ```

2. **Install the dependencies:**
   Make sure you have Python 3.8+ installed.
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python -m streamlit run app.py
   ```

## ☁️ Deploying on Streamlit Community Cloud

Viso Vibe is fully configured to be deployed for free on [Streamlit Community Cloud](https://streamlit.io/cloud). 

1. Push your repository to GitHub (ensure `app.py`, `requirements.txt`, and the `Emotion_onnx-main` folder containing the `.onnx` weight files are included).
2. Log in to Streamlit Community Cloud and click **New App**.
3. Select your GitHub repository, set the branch to `main`, and set the Main file path to `VisoVibe/app.py`.
4. Click **Deploy!**

*Note: The `requirements.txt` specifically uses `opencv-python-headless` to ensure compatibility with Linux server environments that lack GUI libraries.*

## 📁 Repository Structure

```text
Viso-Vibe/
└── VisoVibe/
    ├── app.py                  # Main Streamlit application and UI logic
    ├── requirements.txt        # Python dependencies for deployment
    └── Emotion_onnx-main/      # Local face detection and emotion recognition module
        ├── util.py             # Inference utilities
        └── weights/
            ├── detection.onnx  # Face detection model weights
            └── emotion.onnx    # Emotion classification model weights
```

## 📜 License

This project is created for educational and entertainment purposes. Ensure you comply with YouTube's Terms of Service when embedding and streaming playlists.
