from __future__ import annotations

import random
from collections import Counter
from pathlib import Path
from typing import Any, cast

import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


EMOTION_ORDER = ["happy", "sad", "neutral", "surprise"]
FONT_PATHS = [
    Path(r"C:\Windows\Fonts\Nirmala.ttc"),
    Path(r"C:\Windows\Fonts\Vrinda.ttf"),
]
MESSAGE_MAP = {
    "happy": [
        "শুভ নববর্ষ! আনন্দে ভরে উঠুক তোমার পহেলা বৈশাখ।",
        "হাসিতে রাঙুক নতুন বছর, শুভ পহেলা বৈশাখ!",
        "নতুন দিনের উচ্ছ্বাসে কাটুক তোমার বৈশাখী উৎসব।",
    ],
    "sad": [
        "শুভ নববর্ষ। নতুন বছর তোমার মনে শান্তি আর আশার আলো আনুক।",
        "পহেলা বৈশাখের নতুন সূর্য তোমার মন ভালো করে দিক।",
        "নতুন বছরে সব কষ্ট পেরিয়ে আসুক আলো আর সম্ভাবনা।",
    ],
    "neutral": [
        "শুভ পহেলা বৈশাখ! নতুন বছরে থাকুক শান্তি, সৌভাগ্য আর সাফল্য।",
        "নতুন বছরের শুরু হোক মঙ্গল, ভালোবাসা আর আশীর্বাদে।",
        "বৈশাখের শুভেচ্ছা। প্রতিটি দিন হোক নতুন সম্ভাবনায় ভরা।",
    ],
    "surprise": [
        "চমকে ভরা আনন্দে কাটুক তোমার পহেলা বৈশাখ, শুভ নববর্ষ!",
        "নতুন বছর আনুক রঙিন সুখ আর দারুণ সব মুহূর্ত।",
        "বৈশাখের উচ্ছ্বাসে জমে উঠুক তোমার উৎসবের দিন।",
    ],
}
EMOTION_NORMALIZATION = {
    "happy": "happy",
    "sad": "sad",
    "neutral": "neutral",
    "surprise": "surprise",
    "fear": "neutral",
    "angry": "sad",
    "disgust": "sad",
}


def capture_image() -> np.ndarray | None:
    """Capture a single frame from the default webcam and return it as RGB."""
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        st.error("Could not access the webcam. Please check camera permissions and try again.")
        return None

    try:
        success, frame = camera.read()
    finally:
        camera.release()

    if not success or frame is None:
        st.error("Failed to capture an image from the webcam. Please try again.")
        return None

    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def detect_emotion(image: np.ndarray) -> tuple[str, str | None]:
    """
    Analyze the image with DeepFace and normalize the result for the demo UI.

    Returns a tuple of (normalized_emotion, status_message).
    """
    try:
        from deepface import DeepFace
    except Exception as exc:  # pragma: no cover - environment-specific import risk
        return "neutral", f"DeepFace could not be imported in this environment: {exc}"

    try:
        raw_analysis = DeepFace.analyze(
            img_path=image,
            actions=["emotion"],
            enforce_detection=False,
            silent=True,
        )
    except Exception as exc:
        return "neutral", f"Emotion analysis fell back to neutral because DeepFace raised: {exc}"

    if isinstance(raw_analysis, list):
        analysis = cast(dict[str, Any], raw_analysis[0] if raw_analysis else {})
    elif isinstance(raw_analysis, dict):
        analysis = cast(dict[str, Any], raw_analysis)
    else:
        analysis = {}

    dominant_emotion = str(analysis.get("dominant_emotion", "neutral")).lower()
    normalized = EMOTION_NORMALIZATION.get(dominant_emotion, "neutral")

    if dominant_emotion not in EMOTION_NORMALIZATION:
        return normalized, f"Detected '{dominant_emotion}' and mapped it to '{normalized}' for the live demo."

    if dominant_emotion == "neutral" and not analysis.get("region"):
        return normalized, "No clear face was detected, so the app used a safe neutral fallback."

    return normalized, None


def get_message(emotion: str) -> str:
    """Return a random Bengali greeting for the detected emotion."""
    messages = MESSAGE_MAP.get(emotion, MESSAGE_MAP["neutral"])
    return random.choice(messages)


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for font_path in FONT_PATHS:
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def create_card(message: str, emotion: str) -> Image.Image:
    """Create a simple Boishakh-themed greeting card image."""
    width, height = 900, 500
    image = Image.new("RGB", (width, height), "#FFF8F8")
    draw = ImageDraw.Draw(image)

    # Soft themed layers help the card feel celebratory without needing external assets.
    draw.rectangle((0, 0, width, 110), fill="#F6C5C5")
    draw.rectangle((0, height - 90, width, height), fill="#F8D9D9")
    draw.ellipse((40, 40, 190, 190), fill="#E46E6E")
    draw.ellipse((width - 190, height - 170, width - 40, height - 20), fill="#F1A6A6")
    draw.rounded_rectangle((95, 105, width - 95, height - 105), radius=28, fill="#FFFFFF", outline="#E28A8A", width=4)

    title_font = load_font(34)
    message_font = load_font(40)
    footer_font = load_font(24)

    title_text = "AI Boishakh Mood Detector"
    footer_text = f"Detected mood: {emotion.capitalize()}"

    title_box = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_box[2] - title_box[0]
    draw.text(((width - title_width) / 2, 35), title_text, fill="#7D1F1F", font=title_font)

    max_text_width = width - 240
    wrapped_lines: list[str] = []
    current_line = ""
    for word in message.split():
        trial_line = f"{current_line} {word}".strip()
        trial_box = draw.textbbox((0, 0), trial_line, font=message_font)
        if trial_box[2] - trial_box[0] <= max_text_width:
            current_line = trial_line
        else:
            if current_line:
                wrapped_lines.append(current_line)
            current_line = word
    if current_line:
        wrapped_lines.append(current_line)

    text_block = "\n".join(wrapped_lines)
    text_box = draw.multiline_textbbox((0, 0), text_block, font=message_font, spacing=16, align="center")
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]
    text_x = (width - text_width) / 2
    text_y = (height - text_height) / 2
    draw.multiline_text((text_x, text_y), text_block, fill="#8B1E1E", font=message_font, spacing=16, align="center")

    footer_box = draw.textbbox((0, 0), footer_text, font=footer_font)
    footer_width = footer_box[2] - footer_box[0]
    draw.text(((width - footer_width) / 2, height - 70), footer_text, fill="#7D1F1F", font=footer_font)

    return image


def emotion_chart_data(history: list[str]) -> dict[str, list[Any]]:
    counts = Counter(history)
    return {
        "emotion": EMOTION_ORDER,
        "count": [counts.get(emotion, 0) for emotion in EMOTION_ORDER],
    }


def main() -> None:
    st.set_page_config(page_title="AI Boishakh Mood Detector", page_icon="🌺", layout="centered")
    st.title("AI Boishakh Mood Detector")
    st.caption("Capture a webcam photo, detect the mood, and generate a Bengali Pohela Boishakh greeting card.")

    if "emotion_history" not in st.session_state:
        st.session_state.emotion_history = []

    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    st.info("The first DeepFace analysis may take a little longer while the model loads.")

    if st.button("Capture & Analyze", type="primary"):
        with st.spinner("Opening webcam and analyzing mood..."):
            image = capture_image()
            if image is not None:
                emotion, status_message = detect_emotion(image)
                message = get_message(emotion)
                card = create_card(message, emotion)
                st.session_state.emotion_history.append(emotion)
                st.session_state.last_result = {
                    "image": image,
                    "emotion": emotion,
                    "message": message,
                    "card": card,
                    "status_message": status_message,
                }

    result = st.session_state.last_result
    if result:
        st.subheader("Captured Image")
        st.image(result["image"], channels="RGB", use_container_width=True)

        st.subheader("Detected Emotion")
        st.write(result["emotion"].capitalize())

        if result["status_message"]:
            st.warning(result["status_message"])

        st.subheader("Pohela Boishakh Greeting")
        st.write(result["message"])

        st.subheader("Generated Greeting Card")
        st.image(result["card"], use_container_width=True)

    if st.session_state.emotion_history:
        st.subheader("Emotion Distribution")
        st.bar_chart(emotion_chart_data(st.session_state.emotion_history), x="emotion", y="count")


if __name__ == "__main__":
    main()
