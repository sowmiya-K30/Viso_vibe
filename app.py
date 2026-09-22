import os
import sys
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from gtts import gTTS

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Emotion_onnx-main')))
from util import FaceDetector, HSEmotionRecognizer

det_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Emotion_onnx-main', 'weights', 'detection.onnx'))
emo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Emotion_onnx-main', 'weights', 'emotion.onnx'))
detector = FaceDetector(det_path)
fer = HSEmotionRecognizer(emo_path)

st.set_page_config(
    page_title="Viso Vibe",
    page_icon="🎶",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── Playlists & Metadata (unchanged) ───────────────────────────────────────
zoro_yt = {
    "happy": "PLAzYd4uzG2LrbXNOAugat_pdqF2ueDZ2-",
    "sad":   "PL_DaWb6RFQc1z_KhtsFR3SsOgXXb-E5js",
    "calm":  "PLF0p4MtOouIJl6we_7n5RdWUQ_7EZaCPh",
    "angry": "PLjtEEV8UfHg8U5GoFsyXhSAIiSY3AChNQ"
}

meta_map = {
    "happy": ("Happy Vibes Mix",    "Tamil High Energy"),
    "sad":   ("Soulful Melodies",   "Tamil Heartbreak & Love"),
    "calm":  ("Calm & Breezy Lo-Fi","Tamil Chill Tracks"),
    "angry": ("Rage & Workout BGMs","Tamil Mass Beats")
}

# ─── Mood Palettes ───────────────────────────────────────────────────────────
mood_palettes = {
    "happy": {
        "c1": "255,196,0",   "c2": "255,107,53",  "c3": "255,45,110",
        "accent": "#FFC400", "glow": "#FF6B35",
        "name": "Solar",     "emoji": "☀️",
        "desc": "Radiant & Electric",
        "grad": "linear-gradient(135deg, rgba(255,196,0,0.9) 0%, rgba(255,107,53,0.9) 100%)"
    },
    "sad": {
        "c1": "64,120,255",  "c2": "120,60,220",  "c3": "80,200,255",
        "accent": "#4078FF", "glow": "#7860DC",
        "name": "Cobalt",    "emoji": "🌊",
        "desc": "Deep & Reflective",
        "grad": "linear-gradient(135deg, rgba(64,120,255,0.9) 0%, rgba(120,60,220,0.9) 100%)"
    },
    "calm": {
        "c1": "52,199,145",  "c2": "20,140,180",  "c3": "120,80,220",
        "accent": "#34C791", "glow": "#148CB4",
        "name": "Sage",      "emoji": "🌿",
        "desc": "Serene & Balanced",
        "grad": "linear-gradient(135deg, rgba(52,199,145,0.9) 0%, rgba(20,140,180,0.9) 100%)"
    },
    "angry": {
        "c1": "230,30,30",   "c2": "255,90,0",    "c3": "200,0,90",
        "accent": "#E61E1E", "glow": "#FF5A00",
        "name": "Crimson",   "emoji": "🔥",
        "desc": "Raw & Intense",
        "grad": "linear-gradient(135deg, rgba(230,30,30,0.9) 0%, rgba(255,90,0,0.9) 100%)"
    },
}

# ─── Session State ────────────────────────────────────────────────────────────
for key in ["luffy_vibe", "sai", "rock_artist", "yt_id", "naruto"]:
    if key not in st.session_state:
        st.session_state[key] = None

current_mood = st.session_state.luffy_vibe or "calm"
pal = mood_palettes.get(current_mood, mood_palettes["calm"])
c1, c2, c3 = pal["c1"], pal["c2"], pal["c3"]

# ─── Global CSS ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');

html, body, [data-testid="stApp"] {{
    font-family: 'Inter', system-ui, sans-serif;
    background: #06060F;
    overflow-x: hidden;
    min-height: 100vh;
    margin: 0;
    padding: 0;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

/* ── Ambient background ── */
[data-testid="stApp"]::before {{
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    background:
        radial-gradient(ellipse 90% 70% at 10% 10%,  rgba({c1}, 0.14) 0%, transparent 55%),
        radial-gradient(ellipse 70% 60% at 90% 85%,  rgba({c2}, 0.12) 0%, transparent 55%),
        radial-gradient(ellipse 55% 55% at 50% 45%,  rgba({c3}, 0.07) 0%, transparent 60%),
        radial-gradient(ellipse 100% 40% at 50% 100%, rgba({c1}, 0.06) 0%, transparent 50%),
        #06060F;
    transition: background 1.4s cubic-bezier(0.4,0,0.2,1);
    pointer-events: none;
}}

/* Subtle noise texture overlay */
[data-testid="stApp"]::after {{
    content: "";
    position: fixed;
    inset: 0;
    z-index: 1;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    opacity: 0.4;
}}

/* ── Hide Streamlit chrome ── */
#MainMenu, header[data-testid="stHeader"], footer {{ visibility: hidden; height: 0 !important; }}
[data-testid="stDecoration"] {{ display: none; }}
[data-testid="stToolbar"] {{ display: none; }}
section[data-testid="stSidebar"] {{ display: none; }}

/* ── Layout ── */
.main .block-container {{
    max-width: 460px !important;
    margin: 0 auto !important;
    padding: 0 18px 120px 18px !important;
    position: relative;
    z-index: 2;
}}

/* ── Header ── */
.vv-header {{
    padding: 44px 0 32px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
    position: relative;
}}

.vv-eyebrow {{
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.22);
    margin-bottom: 18px;
}}

/* Logo */
.vv-logo-orbit {{
    position: relative;
    width: 80px;
    height: 80px;
    margin-bottom: 20px;
}}

.vv-orbit-ring {{
    position: absolute;
    border-radius: 50%;
    border: 1px solid transparent;
}}

.vv-orbit-ring-1 {{
    inset: 0;
    border-color: rgba({c1}, 0.35);
    border-top-color: rgba({c1}, 0.9);
    animation: orbitSpin1 3.5s linear infinite;
}}

.vv-orbit-ring-2 {{
    inset: 8px;
    border-color: rgba({c2}, 0.25);
    border-bottom-color: rgba({c2}, 0.7);
    animation: orbitSpin1 2.2s linear infinite reverse;
}}

.vv-orbit-ring-3 {{
    inset: 18px;
    border-color: rgba({c3}, 0.18);
    border-left-color: rgba({c3}, 0.5);
    animation: orbitSpin1 4.8s linear infinite;
}}

.vv-logo-nucleus {{
    position: absolute;
    inset: 26px;
    border-radius: 50%;
    background: {pal["grad"]};
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow:
        0 0 30px rgba({c1}, 0.5),
        0 0 60px rgba({c1}, 0.2),
        inset 0 1px 0 rgba(255,255,255,0.3);
}}

.vv-nucleus-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255,255,255,0.95);
    box-shadow: 0 0 10px rgba(255,255,255,0.8);
    animation: nucleusPulse 2s ease-in-out infinite;
}}

@keyframes orbitSpin1 {{ to {{ transform: rotate(360deg); }} }}
@keyframes nucleusPulse {{
    0%, 100% {{ transform: scale(1);   opacity: 1; }}
    50%       {{ transform: scale(1.3); opacity: 0.7; }}
}}

/* Brand wordmark */
.vv-wordmark {{
    position: relative;
    margin-bottom: 8px;
}}

.vv-brand-main {{
    font-family: 'Space Mono', monospace;
    font-size: 32px;
    font-weight: 700;
    letter-spacing: 8px;
    text-transform: uppercase;
    background: linear-gradient(
        90deg,
        rgba({c1}, 1) 0%,
        rgba(255,255,255,0.95) 40%,
        rgba({c2}, 1) 70%,
        rgba({c3}, 0.9) 100%
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    line-height: 1;
    filter: drop-shadow(0 0 20px rgba({c1}, 0.3));
}}

.vv-tagline {{
    font-size: 9.5px;
    font-weight: 500;
    letter-spacing: 3.5px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.2);
    text-align: center;
    margin-top: 4px;
}}

/* Header divider */
.vv-rule {{
    width: 100%;
    height: 1px;
    position: relative;
    margin: 28px 0 32px;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba({c1}, 0.4) 25%,
        rgba({c2}, 0.4) 50%,
        rgba({c3}, 0.3) 75%,
        transparent 100%
    );
    overflow: visible;
}}

.vv-rule::after {{
    content: "";
    position: absolute;
    top: -1px;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, rgba({c1}, 0.9), rgba({c2}, 0.9));
    border-radius: 2px;
    filter: blur(1px);
}}

/* ── Camera Section ── */
.cam-wrap {{
    position: relative;
    margin-bottom: 4px;
}}

.cam-label-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
    padding: 0 2px;
}}

.cam-label {{
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.3);
}}

.cam-status-dot {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba({c1}, 0.7);
    font-weight: 600;
}}

.cam-status-dot::before {{
    content: "";
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: rgba({c1}, 0.9);
    box-shadow: 0 0 8px rgba({c1}, 0.6);
    animation: liveBlink 2s ease-in-out infinite;
    display: inline-block;
}}

@keyframes liveBlink {{
    0%, 100% {{ opacity: 1; }}
    50%       {{ opacity: 0.3; }}
}}

/* Camera input glassmorphism overrides */
div[data-testid="stCameraInput"] {{
    width: 100% !important;
}}

div[data-testid="stCameraInput"] > div {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}}

div[data-testid="stCameraInput"] video {{
    border-radius: 20px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    width: 100% !important;
    object-fit: cover !important;
    background: #0d0d1c !important;
    box-shadow:
        0 0 0 1px rgba({c1}, 0.08),
        0 20px 60px rgba(0,0,0,0.7),
        inset 0 1px 0 rgba(255,255,255,0.05) !important;
}}

/* Shutter button */
div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"] {{
    all: unset !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 68px !important;
    height: 68px !important;
    border-radius: 50% !important;
    background: rgba(255,255,255,0.03) !important;
    border: 1.5px solid rgba({c1}, 0.3) !important;
    box-shadow:
        0 0 0 8px rgba({c1}, 0.05),
        0 0 30px rgba({c1}, 0.2),
        inset 0 1px 0 rgba(255,255,255,0.1) !important;
    cursor: pointer !important;
    transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
    margin: 18px auto !important;
    position: relative !important;
    overflow: hidden !important;
    backdrop-filter: blur(20px) !important;
    color: transparent !important;
    font-size: 0px !important;
}}

div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"]::before {{
    content: "" !important;
    position: absolute !important;
    inset: 6px !important;
    border-radius: 50% !important;
    border: 1px solid rgba({c1}, 0.4) !important;
}}

div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"]::after {{
    content: "" !important;
    position: absolute !important;
    width: 26px !important;
    height: 26px !important;
    border-radius: 50% !important;
    background: {pal["grad"]} !important;
    box-shadow: 0 0 18px rgba({c1}, 0.7) !important;
}}

div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"]:hover {{
    transform: scale(1.1) !important;
    box-shadow:
        0 0 0 12px rgba({c1}, 0.07),
        0 0 50px rgba({c1}, 0.4),
        inset 0 1px 0 rgba(255,255,255,0.15) !important;
    border-color: rgba({c1}, 0.6) !important;
}}

div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"]:active {{
    transform: scale(0.92) !important;
}}

div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"] p,
div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"] span,
div[data-testid="stCameraInput"] button[data-testid="stCameraInputButton"] div {{
    display: none !important;
}}

/* ── Scan overlay (shown when analyzing) ── */
div[data-testid="stSpinner"] {{
    display: flex;
    align-items: center;
    justify-content: center;
}}

div[data-testid="stSpinner"] > div {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 24px;
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(30px);
    border: 1px solid rgba({c1}, 0.15);
    border-radius: 100px;
}}

div[data-testid="stSpinner"] p {{
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,0.5) !important;
    font-family: 'Space Mono', monospace !important;
    margin: 0 !important;
}}

/* ── Mood result ── */
.mood-reveal-wrap {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
    padding: 28px 0 24px;
    animation: fadeUp 0.6s cubic-bezier(0.22,1,0.36,1) both;
}}

@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

.mood-chip-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}}

.mood-chip {{
    padding: 5px 14px;
    border-radius: 100px;
    background: rgba({c1}, 0.1);
    border: 1px solid rgba({c1}, 0.25);
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba({c1}, 0.9);
    backdrop-filter: blur(10px);
}}

.mood-display {{
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
}}

.mood-emoji {{
    font-size: 48px;
    margin-bottom: 12px;
    animation: emojiDrop 0.7s cubic-bezier(0.34,1.56,0.64,1) both;
    filter: drop-shadow(0 4px 20px rgba({c1}, 0.4));
}}

@keyframes emojiDrop {{
    from {{ transform: scale(0) rotate(-20deg); opacity: 0; }}
    to   {{ transform: scale(1) rotate(0deg);  opacity: 1; }}
}}

.mood-name-large {{
    font-family: 'Space Mono', monospace;
    font-size: 52px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    background: {pal["grad"]};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin-bottom: 8px;
    animation: revealSlide 0.6s 0.15s cubic-bezier(0.22,1,0.36,1) both;
    filter: drop-shadow(0 0 30px rgba({c1}, 0.35));
}}

@keyframes revealSlide {{
    from {{ opacity: 0; transform: translateY(12px) scale(0.95); }}
    to   {{ opacity: 1; transform: translateY(0)    scale(1); }}
}}

.mood-sub {{
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.22);
    animation: revealSlide 0.6s 0.25s cubic-bezier(0.22,1,0.36,1) both;
}}

.mood-palette-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-top: 14px;
    padding: 6px 14px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 100px;
    backdrop-filter: blur(20px);
}}

.mpb-swatch {{
    display: flex;
    gap: 3px;
}}

.mpb-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
}}

.mpb-label {{
    font-size: 8.5px;
    font-weight: 600;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.28);
}}

/* ── Reset button ── */
button[kind="primary"] {{
    border-radius: 14px !important;
    height: 50px !important;
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba({c1}, 0.22) !important;
    color: rgba(255,255,255,0.5) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    backdrop-filter: blur(20px) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05) !important;
    width: 100% !important;
}}

button[kind="primary"] p {{
    font-family: 'Space Mono', monospace !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 3px !important;
    color: rgba(255,255,255,0.5) !important;
    margin: 0 !important;
}}

button[kind="primary"]:hover {{
    background: rgba({c1}, 0.08) !important;
    border-color: rgba({c1}, 0.5) !important;
    color: rgba(255,255,255,0.85) !important;
    box-shadow:
        0 0 30px rgba({c1}, 0.15),
        inset 0 1px 0 rgba(255,255,255,0.08) !important;
    transform: translateY(-1px) !important;
}}

button[kind="primary"]:active {{
    transform: translateY(0) !important;
}}

/* ── Error ── */
div[data-testid="stAlert"] {{
    background: rgba(220,30,30,0.06) !important;
    border: 1px solid rgba(220,30,30,0.18) !important;
    border-radius: 14px !important;
    color: rgba(255,120,120,0.75) !important;
    font-size: 11px !important;
    backdrop-filter: blur(20px) !important;
}}

/* ── Section divider ── */
.section-gap {{ height: 20px; }}
.bottom-gap  {{ height: 24px; }}
</style>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="vv-header">
    <div class="vv-eyebrow">Emotion-driven music</div>
    <div class="vv-logo-orbit">
        <div class="vv-orbit-ring vv-orbit-ring-1"></div>
        <div class="vv-orbit-ring vv-orbit-ring-2"></div>
        <div class="vv-orbit-ring vv-orbit-ring-3"></div>
        <div class="vv-logo-nucleus">
            <div class="vv-nucleus-dot"></div>
        </div>
    </div>
    <div class="vv-wordmark">
        <div class="vv-brand-main">VISO VIBE</div>
    </div>
    <div class="vv-tagline">Emotion · Frequency · Music</div>
</div>
<div class="vv-rule"></div>
""", unsafe_allow_html=True)

# ─── Camera / Detection Flow ─────────────────────────────────────────────────
if st.session_state.luffy_vibe is None:

    st.markdown(f"""
    <div class="cam-label-row">
        <div class="cam-label">Face Capture</div>
        <div class="cam-status-dot">Live</div>
    </div>
    """, unsafe_allow_html=True)

    gojo = st.camera_input("", label_visibility="collapsed")
    
    st.markdown("""
    <div style="text-align: center; margin-top: 5px; margin-bottom: 20px;">
        <span style="font-size: 13px; font-weight: 900; letter-spacing: 4px; text-transform: uppercase; color: rgba(255,255,255,0.6);">TAKE PHOTO</span>
    </div>
    """, unsafe_allow_html=True)

    if gojo is not None:
        with st.spinner("Reading your frequency..."):
            try:
                img_raw = Image.open(gojo).convert("RGB")
                img_arr = np.array(img_raw)

                boxes = detector.detect(img_arr, (640, 640))

                if boxes is not None:
                    box = boxes[0].astype('int32')
                    face_image = img_arr[box[1]:box[3], box[0]:box[2]]
                    pil_image = Image.fromarray(face_image).resize((224, 224))
                    emotion, _ = fer.predict_emotions(np.array(pil_image), logits=False)
                    raw_emotion = emotion.lower()

                    emotion_remap = {
                        "happiness": "happy",
                        "anger":     "angry",
                        "sadness":   "sad",
                        "surprise":  "surprise",
                        "fear":      "fear",
                        "disgust":   "disgust",
                        "neutral":   "neutral",
                    }
                    luffy = emotion_remap.get(raw_emotion, raw_emotion)
                    if luffy not in zoro_yt:
                        luffy = "calm"
                else:
                    luffy = "calm"

                st.session_state.luffy_vibe = luffy

                tts_buf = BytesIO()
                kurama = gTTS(text=f"Vibe detected. You feel {luffy}.", lang="en", slow=False)
                kurama.write_to_fp(tts_buf)
                tts_buf.seek(0)
                st.session_state.naruto = base64.b64encode(tts_buf.read()).decode("utf-8")

                st.session_state.yt_id       = zoro_yt.get(luffy, zoro_yt["calm"])
                st.session_state.sai         = meta_map.get(luffy, meta_map["calm"])[0]
                st.session_state.rock_artist = meta_map.get(luffy, meta_map["calm"])[1]

                st.rerun()

            except Exception:
                st.error("No face detected. Good lighting + face the camera directly.")

else:
    # ─── Mood Result ─────────────────────────────────────────────────────────
    dp = mood_palettes.get(st.session_state.luffy_vibe, mood_palettes["calm"])

    st.markdown(f"""
    <div class="mood-reveal-wrap">
        <div class="mood-chip-row">
            <div class="mood-chip">Detected Mood</div>
        </div>
        <div class="mood-display">
            <div class="mood-emoji">{dp["emoji"]}</div>
            <div class="mood-name-large">{st.session_state.luffy_vibe}</div>
            <div class="mood-sub">{dp["desc"]}</div>
            <div class="mood-palette-badge">
                <div class="mpb-swatch">
                    <div class="mpb-dot" style="background:rgba({dp['c1']},0.9);"></div>
                    <div class="mpb-dot" style="background:rgba({dp['c2']},0.9);"></div>
                    <div class="mpb-dot" style="background:rgba({dp['c3']},0.9);"></div>
                </div>
                <div class="mpb-label">Palette · {dp["name"]}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TTS autoplay ──────────────────────────────────────────────────────────
    if st.session_state.naruto:
        components.html(
            f'<audio autoplay src="data:audio/mp3;base64,{st.session_state.naruto}"></audio>',
            height=0, width=0
        )
        st.session_state.naruto = None

    # ─── Music Player Card ────────────────────────────────────────────────────
    if st.session_state.yt_id:
        dc1, dc2, dc3 = dp["c1"], dp["c2"], dp["c3"]
        daccent        = dp["accent"]
        dglow          = dp["glow"]
        dgrad          = dp["grad"]
        dsai           = st.session_state.sai
        dartist        = st.session_state.rock_artist
        dytid          = st.session_state.yt_id

        player_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

*, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; -webkit-font-smoothing:antialiased; }}

body {{
    font-family: 'Inter', sans-serif;
    background: transparent;
    color: white;
    overflow: hidden;
    padding: 0;
    user-select: none;
}}

/* ── Orbital visualizer canvas ── */
.vis-canvas-wrap {{
    width: 100%;
    height: 100px;
    position: relative;
    margin-bottom: -6px;
}}

#visCanvas {{
    display: block;
    width: 100%;
    height: 100%;
}}

/* ── Player card ── */
.player-card {{
    position: relative;
    background: rgba(8, 8, 20, 0.7);
    backdrop-filter: blur(40px) saturate(180%);
    -webkit-backdrop-filter: blur(40px) saturate(180%);
    border-radius: 24px;
    border: 1px solid rgba(255,255,255,0.07);
    padding: 22px 22px 18px;
    overflow: hidden;
    box-shadow:
        0 0 0 1px rgba({dc1}, 0.08),
        0 30px 80px rgba(0,0,0,0.8),
        0 0 60px rgba({dc1}, 0.08),
        inset 0 1px 0 rgba(255,255,255,0.08);
}}

/* Top shimmer */
.card-shimmer {{
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba({dc1}, 0.6) 30%,
        rgba({dc2}, 0.6) 60%,
        transparent 100%
    );
}}

/* Ambient glow behind card */
.card-ambient {{
    position: absolute;
    top: -60px; left: -40px; right: -40px;
    height: 140px;
    background: radial-gradient(ellipse at 50% 100%, rgba({dc1}, 0.1) 0%, transparent 70%);
    pointer-events: none;
}}

/* ── Track info row ── */
.track-row {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 20px;
}}

/* Animated album art */
.album-art {{
    position: relative;
    width: 52px;
    height: 52px;
    flex-shrink: 0;
}}

.album-ring-outer {{
    position: absolute;
    inset: 0;
    border-radius: 50%;
    border: 1px solid rgba({dc1}, 0.3);
    animation: albumSpin 8s linear infinite;
}}

.album-ring-inner {{
    position: absolute;
    inset: 5px;
    border-radius: 50%;
    background: {dgrad};
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow:
        0 0 20px rgba({dc1}, 0.5),
        inset 0 1px 0 rgba(255,255,255,0.25);
}}

.album-center-hole {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: rgba(8,8,20,0.9);
    border: 1.5px solid rgba(255,255,255,0.3);
}}

@keyframes albumSpin {{ to {{ transform: rotate(360deg); }} }}
.album-ring-outer.paused {{ animation-play-state: paused; }}

/* Track text */
.track-meta {{ flex: 1; overflow: hidden; }}

.track-title {{
    font-size: 14px;
    font-weight: 700;
    color: rgba(255,255,255,0.92);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    letter-spacing: -0.2px;
    line-height: 1.2;
    margin-bottom: 4px;
}}

.track-artist {{
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.3);
}}

/* Live badge */
.live-badge {{
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    background: rgba({dc1}, 0.1);
    border: 1px solid rgba({dc1}, 0.25);
    border-radius: 100px;
    flex-shrink: 0;
    backdrop-filter: blur(10px);
}}

.live-dot {{
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: {daccent};
    box-shadow: 0 0 8px {daccent};
    animation: livePulse 1.6s ease-in-out infinite;
}}

.live-text {{
    font-family: 'Space Mono', monospace;
    font-size: 7.5px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba({dc1}, 0.8);
}}

@keyframes livePulse {{
    0%, 100% {{ opacity: 1;   transform: scale(1);   }}
    50%       {{ opacity: 0.3; transform: scale(0.65); }}
}}

/* ── Seeker (progress + seek) ── */
.seeker-wrap {{
    margin-bottom: 18px;
}}

.time-row {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}}

.time-label {{
    font-family: 'Space Mono', monospace;
    font-size: 9.5px;
    font-weight: 400;
    color: rgba(255,255,255,0.28);
    letter-spacing: 0.5px;
}}

.seek-track {{
    position: relative;
    height: 4px;
    border-radius: 4px;
    background: rgba(255,255,255,0.07);
    cursor: pointer;
    overflow: visible;
}}

.seek-buffer {{
    position: absolute;
    left: 0; top: 0;
    height: 100%;
    border-radius: 4px;
    background: rgba(255,255,255,0.06);
    pointer-events: none;
    transition: width 1s linear;
}}

.seek-fill {{
    position: absolute;
    left: 0; top: 0;
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, rgba({dc1},0.9), rgba({dc2},0.8));
    pointer-events: none;
    transition: width 0.3s linear;
    box-shadow: 0 0 8px rgba({dc1}, 0.4);
}}

.seek-thumb {{
    position: absolute;
    top: 50%;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: white;
    border: 2px solid rgba({dc1}, 0.9);
    transform: translate(-50%, -50%) scale(0);
    box-shadow: 0 0 10px rgba({dc1}, 0.6), 0 2px 6px rgba(0,0,0,0.5);
    pointer-events: none;
    transition: transform 0.15s ease;
}}

.seek-track:hover .seek-thumb {{
    transform: translate(-50%, -50%) scale(1);
}}

.seek-track:active .seek-thumb {{
    transform: translate(-50%, -50%) scale(1.2);
}}

/* ── Controls ── */
.controls-row {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    margin-bottom: 18px;
}}

.ctrl-btn {{
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.34,1.56,0.64,1);
    flex-shrink: 0;
    border: none;
    outline: none;
    position: relative;
    overflow: hidden;
}}

.ctrl-btn::before {{
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: rgba({dc1}, 0);
    transition: background 0.2s ease;
}}

.ctrl-btn:hover::before {{
    background: rgba({dc1}, 0.1);
}}

.ctrl-sm {{
    width: 40px;
    height: 40px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
}}

.ctrl-sm:hover {{
    transform: scale(1.1);
    border-color: rgba({dc1}, 0.3);
}}

.ctrl-sm:active {{ transform: scale(0.9); }}

.ctrl-sm svg {{
    width: 15px;
    height: 15px;
    fill: rgba(255,255,255,0.5);
    position: relative;
    z-index: 1;
}}

.ctrl-play-btn {{
    width: 58px;
    height: 58px;
    background: {dgrad};
    border: none;
    box-shadow:
        0 6px 30px rgba({dc1}, 0.45),
        0 0 60px rgba({dc1}, 0.15),
        inset 0 1px 0 rgba(255,255,255,0.3);
}}

.ctrl-play-btn:hover {{
    transform: scale(1.1);
    box-shadow:
        0 10px 40px rgba({dc1}, 0.6),
        0 0 80px rgba({dc1}, 0.2),
        inset 0 1px 0 rgba(255,255,255,0.35);
}}

.ctrl-play-btn:active {{ transform: scale(0.93); }}

.ctrl-play-btn svg {{
    width: 20px;
    height: 20px;
    fill: white;
    position: relative;
    z-index: 1;
    filter: drop-shadow(0 1px 3px rgba(0,0,0,0.3));
}}

#playIcon {{ margin-left: 2px; }}

/* ── Volume row ── */
.volume-row {{
    display: flex;
    align-items: center;
    gap: 10px;
}}

.vol-icon {{
    width: 14px;
    height: 14px;
    fill: rgba(255,255,255,0.25);
    flex-shrink: 0;
}}

.vol-track {{
    flex: 1;
    position: relative;
    height: 3px;
    border-radius: 3px;
    background: rgba(255,255,255,0.07);
    cursor: pointer;
    overflow: hidden;
}}

.vol-fill {{
    position: absolute;
    left: 0; top: 0;
    height: 100%;
    border-radius: 3px;
    background: linear-gradient(90deg, rgba({dc1},0.7), rgba({dc2},0.7));
    width: 80%;
    transition: width 0.1s ease;
}}

.vol-label {{
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: rgba(255,255,255,0.2);
    letter-spacing: 1px;
    width: 26px;
    text-align: right;
    flex-shrink: 0;
}}

/* ── Hidden YT iframe ── */
.yt-shell {{
    position: absolute;
    width: 1px;
    height: 1px;
    opacity: 0.001;
    z-index: -999;
    pointer-events: none;
    overflow: hidden;
    top: 0; left: 0;
}}
</style>
</head>
<body>
<div class="vis-canvas-wrap">
    <canvas id="visCanvas"></canvas>
</div>

<div class="player-card">
    <div class="card-shimmer"></div>
    <div class="card-ambient"></div>

    <!-- Track info -->
    <div class="track-row">
        <div class="album-art">
            <div class="album-ring-outer" id="albumRing"></div>
            <div class="album-ring-inner">
                <div class="album-center-hole"></div>
            </div>
        </div>
        <div class="track-meta">
            <div class="track-title">{dsai}</div>
            <div class="track-artist">{dartist}</div>
        </div>
        <div class="live-badge">
            <div class="live-dot"></div>
            <div class="live-text">Live</div>
        </div>
    </div>

    <!-- Seeker -->
    <div class="seeker-wrap">
        <div class="time-row">
            <span class="time-label" id="timeNow">0:00</span>
            <span class="time-label" id="timeDur">—:——</span>
        </div>
        <div class="seek-track" id="seekTrack">
            <div class="seek-buffer" id="seekBuffer" style="width:0%"></div>
            <div class="seek-fill"   id="seekFill"   style="width:0%"></div>
            <div class="seek-thumb"  id="seekThumb"  style="left:0%"></div>
        </div>
    </div>

    <!-- Controls -->
    <div class="controls-row">
        <div class="ctrl-btn ctrl-sm" onclick="shuffleToggle()" id="shuffleBtn" title="Shuffle">
            <svg viewBox="0 0 24 24"><path d="M10.59 9.17L5.41 4 4 5.41l5.17 5.17zm4.76-.82l3.15 3.15-3.15 3.15L17 16l4.45-4.45-4.45-4.45zm-.82 8.16L9.17 10.59 4 15.76 5.41 17.17l4.18-4.18 5.35 5.35z"/></svg>
        </div>
        <div class="ctrl-btn ctrl-sm" onclick="prevTrack()" title="Previous">
            <svg viewBox="0 0 24 24"><path d="M6 6h2v12H6zm3.5 6 8.5 6V6z"/></svg>
        </div>
        <div class="ctrl-btn ctrl-play-btn" onclick="togglePlay()" id="playBtnEl">
            <svg id="playIcon" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
        </div>
        <div class="ctrl-btn ctrl-sm" onclick="nextTrack()" title="Next">
            <svg viewBox="0 0 24 24"><path d="M6 18l8.5-6L6 6v12zm2.5-6 8.5 6V6z"/></svg>
        </div>
        <div class="ctrl-btn ctrl-sm" onclick="repeatToggle()" id="repeatBtn" title="Repeat">
            <svg viewBox="0 0 24 24"><path d="M7 7h10v3l4-4-4-4v3H5v6h2zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2z"/></svg>
        </div>
    </div>

    <!-- Volume -->
    <div class="volume-row">
        <svg class="vol-icon" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>
        <div class="vol-track" id="volTrack">
            <div class="vol-fill" id="volFill"></div>
        </div>
        <span class="vol-label" id="volLabel">80%</span>
    </div>
</div>

<div class="yt-shell"><div id="yt-player"></div></div>

<script>
// ── Palette ──────────────────────────────────────────────────────────────────
var C1 = [{dc1}];
var C2 = [{dc2}];
var C3 = [{dc3}];
var palRGB = [
    'rgba(' + C1.join(',') + ',',
    'rgba(' + C2.join(',') + ',',
    'rgba(' + C3.join(',') + ','
];

// ── Visualizer ───────────────────────────────────────────────────────────────
var canvas = document.getElementById('visCanvas');
var ctx    = canvas.getContext('2d');
var DPR    = window.devicePixelRatio || 1;
var W, H;

function resizeCanvas() {{
    var wrap = canvas.parentElement;
    W = wrap.offsetWidth;
    H = wrap.offsetHeight;
    canvas.width  = W * DPR;
    canvas.height = H * DPR;
    canvas.style.width  = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
}}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// Particles
var particles = [];
for (var i = 0; i < 22; i++) {{
    particles.push({{
        x: Math.random() * 600,
        y: Math.random() * H,
        r: 3 + Math.random() * 16,
        maxR: 8 + Math.random() * 28,
        phase: Math.random() * Math.PI * 2,
        speed: 0.008 + Math.random() * 0.016,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.25,
        ci: Math.floor(Math.random() * 3)
    }});
}}

// Bars (waveform strip)
var BAR_COUNT = 48;
var bars = Array.from({{ length: BAR_COUNT }}, function(_, i) {{
    return {{
        h: 0.2 + Math.random() * 0.6,
        target: 0.2 + Math.random() * 0.6,
        speed: 0.05 + Math.random() * 0.08,
        phase: (i / BAR_COUNT) * Math.PI * 2
    }};
}});

var tick = 0;
var isPlayingVis = false;

function drawVisualizer() {{
    requestAnimationFrame(drawVisualizer);
    ctx.clearRect(0, 0, W, H);
    tick += isPlayingVis ? 0.025 : 0.008;

    var barW  = W / BAR_COUNT;
    var barMaxH = H * 0.55;
    var barY  = H * 0.88;

    // Bars
    for (var i = 0; i < BAR_COUNT; i++) {{
        var b = bars[i];
        if (isPlayingVis) {{
            b.target = 0.15 + 0.85 * Math.abs(
                0.5 * Math.sin(tick * 2.1 + b.phase) +
                0.3 * Math.sin(tick * 3.7 + b.phase * 1.4) +
                0.2 * Math.sin(tick * 1.3 + b.phase * 0.7)
            );
        }} else {{
            b.target = 0.05 + 0.08 * Math.abs(Math.sin(tick * 0.8 + b.phase));
        }}
        b.h += (b.target - b.h) * b.speed;

        var bh  = b.h * barMaxH;
        var bx  = i * barW + barW * 0.15;
        var bww = barW * 0.55;
        var ci  = i % 3;
        var opa = 0.15 + b.h * 0.5;

        var grd = ctx.createLinearGradient(bx, barY - bh, bx, barY);
        grd.addColorStop(0,   palRGB[ci] + opa + ')');
        grd.addColorStop(0.5, palRGB[(ci+1)%3] + (opa * 0.7) + ')');
        grd.addColorStop(1,   palRGB[ci] + '0)');

        ctx.beginPath();
        ctx.roundRect(bx, barY - bh, bww, bh, [2, 2, 0, 0]);
        ctx.fillStyle = grd;
        ctx.fill();
    }}

    // Floating particles
    for (var j = 0; j < particles.length; j++) {{
        var p = particles[j];
        p.phase += p.speed * (isPlayingVis ? 1.8 : 0.5);
        var pulse = 0.5 + 0.5 * Math.sin(p.phase);
        var cr = p.r + (p.maxR - p.r) * pulse;

        p.x += p.vx * (isPlayingVis ? 1.2 : 0.4);
        p.y += p.vy * (isPlayingVis ? 1.2 : 0.4);
        if (p.x < -p.maxR)  p.x = W + p.maxR;
        if (p.x > W+p.maxR) p.x = -p.maxR;
        if (p.y < -p.maxR)  p.y = H + p.maxR;
        if (p.y > H+p.maxR) p.y = -p.maxR;

        var pg = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, cr);
        var opa2 = (0.18 + 0.18 * pulse) * (isPlayingVis ? 1 : 0.4);
        pg.addColorStop(0, palRGB[p.ci] + opa2 + ')');
        pg.addColorStop(1, palRGB[p.ci] + '0)');
        ctx.beginPath();
        ctx.arc(p.x, p.y, cr, 0, Math.PI * 2);
        ctx.fillStyle = pg;
        ctx.fill();
    }}
}}
drawVisualizer();

// ── YouTube Player ────────────────────────────────────────────────────────────
var player;
var isPlaying    = false;
var isSeeking    = false;
var seekInterval = null;
var volLevel     = 80;
var isShuffled   = true;
var isRepeat     = false;

var tag = document.createElement('script');
tag.src = 'https://www.youtube.com/iframe_api';
document.body.appendChild(tag);

function onYouTubeIframeAPIReady() {{
    player = new YT.Player('yt-player', {{
        height: '1', width: '1',
        playerVars: {{
            autoplay:  1,
            controls:  0,
            playsinline: 1,
            rel:       0,
            listType: 'playlist',
            list:     '{dytid}',
            index:    Math.floor(Math.random() * 50)
        }},
        events: {{
            onReady:       onPlayerReady,
            onStateChange: onStateChange
        }}
    }});
}}

function onPlayerReady(e) {{
    e.target.setShuffle(true);
    e.target.setVolume(volLevel);
    e.target.playVideo();
}}

function onStateChange(e) {{
    var icon = document.getElementById('playIcon');
    var ring = document.getElementById('albumRing');

    if (e.data === YT.PlayerState.PLAYING) {{
        isPlaying = true;
        isPlayingVis = true;
        icon.innerHTML = '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>';
        ring.classList.remove('paused');
        startSeeker();
    }} else if (e.data === YT.PlayerState.ENDED) {{
        if (isRepeat) {{ player.playVideo(); }}
        else          {{ player.nextVideo(); }}
    }} else {{
        isPlaying = false;
        isPlayingVis = false;
        icon.innerHTML = '<path d="M8 5v14l11-7z"/>';
        ring.classList.add('paused');
        clearInterval(seekInterval);
    }}
}}

// ── Seeker logic ─────────────────────────────────────────────────────────────
function formatTime(s) {{
    if (!s || isNaN(s)) return '0:00';
    var m = Math.floor(s / 60);
    var sec = Math.floor(s % 60);
    return m + ':' + (sec < 10 ? '0' : '') + sec;
}}

function updateSeeker() {{
    if (!player || !player.getDuration || isSeeking) return;
    var dur = player.getDuration()     || 0;
    var cur = player.getCurrentTime()  || 0;
    var pct = dur > 0 ? (cur / dur) * 100 : 0;

    document.getElementById('seekFill').style.width   = pct + '%';
    document.getElementById('seekThumb').style.left   = pct + '%';
    document.getElementById('seekBuffer').style.width = Math.min(pct + 8, 100) + '%';
    document.getElementById('timeNow').textContent    = formatTime(cur);
    document.getElementById('timeDur').textContent    = formatTime(dur);
}}

function startSeeker() {{
    clearInterval(seekInterval);
    seekInterval = setInterval(updateSeeker, 400);
}}

// Clickable / draggable seek
var seekTrack = document.getElementById('seekTrack');
var seeking   = false;

function seekTo(e) {{
    if (!player || !player.getDuration) return;
    var rect = seekTrack.getBoundingClientRect();
    var x    = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
    var pct  = Math.max(0, Math.min(1, x / rect.width));
    var dur  = player.getDuration() || 0;
    player.seekTo(pct * dur, true);
    document.getElementById('seekFill').style.width  = (pct * 100) + '%';
    document.getElementById('seekThumb').style.left  = (pct * 100) + '%';
    document.getElementById('timeNow').textContent   = formatTime(pct * dur);
}}

seekTrack.addEventListener('mousedown',  function(e) {{ seeking = true; isSeeking = true; seekTo(e); }});
seekTrack.addEventListener('touchstart', function(e) {{ seeking = true; isSeeking = true; seekTo(e); }}, {{ passive: true }});
document.addEventListener('mousemove',   function(e) {{ if (seeking) seekTo(e); }});
document.addEventListener('touchmove',   function(e) {{ if (seeking) seekTo(e); }}, {{ passive: true }});
document.addEventListener('mouseup',     function()  {{ if (seeking) {{ seeking = false; setTimeout(function() {{ isSeeking = false; }}, 300); }} }});
document.addEventListener('touchend',    function()  {{ if (seeking) {{ seeking = false; setTimeout(function() {{ isSeeking = false; }}, 300); }} }});

// ── Volume ────────────────────────────────────────────────────────────────────
var volTrack   = document.getElementById('volTrack');
var volFill    = document.getElementById('volFill');
var volLabel   = document.getElementById('volLabel');
var volDragging = false;

function setVolume(e) {{
    var rect = volTrack.getBoundingClientRect();
    var x    = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
    volLevel = Math.round(Math.max(0, Math.min(100, (x / rect.width) * 100)));
    volFill.style.width    = volLevel + '%';
    volLabel.textContent   = volLevel + '%';
    if (player && player.setVolume) player.setVolume(volLevel);
}}

volTrack.addEventListener('mousedown',  function(e) {{ volDragging = true; setVolume(e); }});
volTrack.addEventListener('touchstart', function(e) {{ volDragging = true; setVolume(e); }}, {{ passive: true }});
document.addEventListener('mousemove',  function(e) {{ if (volDragging) setVolume(e); }});
document.addEventListener('touchmove',  function(e) {{ if (volDragging) setVolume(e); }}, {{ passive: true }});
document.addEventListener('mouseup',    function()  {{ volDragging = false; }});
document.addEventListener('touchend',   function()  {{ volDragging = false; }});

// ── Controls ──────────────────────────────────────────────────────────────────
function togglePlay() {{
    if (!player) return;
    if (isPlaying) {{ player.pauseVideo(); }} else {{ player.playVideo(); }}
}}
function nextTrack()  {{ if (player) player.nextVideo();     }}
function prevTrack()  {{ if (player) player.previousVideo(); }}

function shuffleToggle() {{
    isShuffled = !isShuffled;
    if (player) player.setShuffle(isShuffled);
    var btn = document.getElementById('shuffleBtn');
    btn.style.opacity    = isShuffled ? '1' : '0.3';
    btn.querySelector('svg').style.fill = isShuffled
        ? 'rgba({dc1},0.9)'
        : 'rgba(255,255,255,0.35)';
}}

function repeatToggle() {{
    isRepeat = !isRepeat;
    var btn = document.getElementById('repeatBtn');
    btn.style.opacity    = isRepeat ? '1' : '0.3';
    btn.querySelector('svg').style.fill = isRepeat
        ? 'rgba({dc1},0.9)'
        : 'rgba(255,255,255,0.35)';
}}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {{
    if (e.code === 'Space')       {{ e.preventDefault(); togglePlay(); }}
    if (e.code === 'ArrowRight')  {{ if (player && player.getCurrentTime) player.seekTo(player.getCurrentTime() + 10, true); }}
    if (e.code === 'ArrowLeft')   {{ if (player && player.getCurrentTime) player.seekTo(Math.max(0, player.getCurrentTime() - 10), true); }}
    if (e.code === 'ArrowUp')     {{ volLevel = Math.min(100, volLevel + 5); if (player) player.setVolume(volLevel); volFill.style.width = volLevel + '%'; volLabel.textContent = volLevel + '%'; }}
    if (e.code === 'ArrowDown')   {{ volLevel = Math.max(0,   volLevel - 5); if (player) player.setVolume(volLevel); volFill.style.width = volLevel + '%'; volLabel.textContent = volLevel + '%'; }}
}});
</script>
</body>
</html>"""

        components.html(player_html, height=358)

    st.markdown('<div class="bottom-gap"></div>', unsafe_allow_html=True)

    _, col_reset, _ = st.columns([1, 1.6, 1])
    with col_reset:
        if st.button("↺  New Scan", key="reset_btn", type="primary", use_container_width=True):
            for key in ["luffy_vibe", "sai", "rock_artist", "yt_id", "naruto"]:
                st.session_state[key] = None
            st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# REQUIREMENTS FOR STREAMLIT CLOUD HOSTING
# ──────────────────────────────────────────────────────────────────────────────
#
# requirements.txt
# ────────────────
# streamlit>=1.32.0
# numpy>=1.24.0
# opencv-python-headless>=4.8.0
# Pillow>=10.0.0
# gTTS>=2.5.0
# onnxruntime>=1.17.0
#
# packages.txt  (system-level deps for Streamlit Cloud)
# ─────────────
# libgl1-mesa-glx
# libglib2.0-0
#
# Directory structure expected:
# ├── app.py
# ├── requirements.txt
# ├── packages.txt
# └── Emotion_onnx-main/
#     ├── util.py
#     └── weights/
#         ├── detection.onnx
#         └── emotion.onnx
#
# Streamlit Cloud deploy notes:
#  • Push all files to a public GitHub repo
#  • Set "Main file path" to app.py in Streamlit Cloud settings
#  • No secrets / API keys needed
#  • Free tier supports onnxruntime inference fine
# ──────────────────────────────────────────────────────────────────────────────