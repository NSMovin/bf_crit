from __future__ import annotations

import base64
import csv
import hashlib
import io
import os
import random
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import numpy as np
import qrcode
import streamlit as st
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont


EMOTION_ORDER = ["happy", "sad", "neutral", "surprise"]
EMOTION_EMOJIS = {
    "happy": "😄",
    "sad": "😢",
    "neutral": "😐",
    "surprise": "😲",
}
FESTIVAL_MOOD_SCORES = {
    "happy": 1.0,
    "surprise": 0.8,
    "neutral": 0.5,
    "sad": 0.2,
}
FONT_PATHS = [
    Path("fonts") / "NotoSansBengali_ExtraCondensed-Regular.ttf",
    Path(r"C:\Windows\Fonts\Nirmala.ttc"),
    Path(r"C:\Windows\Fonts\Vrinda.ttf"),
]
OUTPUTS_DIR = Path("outputs")
CARDS_DIR = OUTPUTS_DIR / "cards"
LOG_FILE = OUTPUTS_DIR / "logs.csv"
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


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #7d1414 0%, #991b1b 45%, #b91c1c 100%);
            color: #ffffff;
        }
        .boishakh-panel {
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.22);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            box-shadow: 0 10px 24px rgba(20, 5, 5, 0.22);
            margin-bottom: 1rem;
            color: #ffffff;
            backdrop-filter: blur(6px);
        }
        .boishakh-title {
            color: #ffffff;
            font-weight: 700;
        }
        .boishakh-center {
            text-align: center;
        }
        .logo-banner {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 22px;
            padding: 0.55rem 0.8rem;
            margin: 0 auto 1.1rem auto;
            box-shadow: 0 14px 30px rgba(20, 5, 5, 0.18);
            backdrop-filter: blur(6px);
            max-width: 760px;
        }
        .logo-row {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.8rem;
        }
        .logo-card {
            width: 120px;
            height: 56px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 14px;
            padding: 0.35rem;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        .logo-card img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            display: block;
        }
        .logo-card--wide img {
            max-width: 92%;
            max-height: 88%;
        }
        .logo-card--tall img {
            max-width: 80%;
            max-height: 88%;
        }
        @media (max-width: 640px) {
            .logo-row {
                gap: 0.45rem;
            }
            .logo-card {
                width: 92px;
                height: 44px;
                padding: 0.25rem;
            }
        }
        .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label, .stApp div, .stApp span, .stApp li {
            color: #ffffff;
        }
        .stCaption {
            color: #ffe7e7 !important;
        }
        .stTextInput input {
            background-color: rgba(255, 255, 255, 0.12);
            color: #ffffff;
        }
        .stTextInput input::placeholder {
            color: #ffd6d6;
        }
        .stCheckbox label, .stMarkdown, .stMetric {
            color: #ffffff;
        }
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_logos() -> None:
    logo_specs = [
        ("images/ads logo_20260408_191426_0000.png", ""),
        ("images/genesis logo_good_full_white_final_20260408_191406_0000.png", "logo-card--wide"),
        ("images/GUB logo_20260408_191433_0000.png", "logo-card--tall"),
    ]
    available_logos: list[tuple[Path, str]] = []
    for raw_path, css_class in logo_specs:
        path = Path(raw_path)
        if path.exists():
            available_logos.append((path, css_class))

    if not available_logos:
        return

    logo_html_parts: list[str] = []
    for logo_path, css_class in available_logos:
        encoded = base64.b64encode(logo_path.read_bytes()).decode("ascii")
        class_attr = f"logo-card {css_class}".strip()
        logo_html_parts.append(
            f'<div class="{class_attr}"><img src="data:image/png;base64,{encoded}" alt="{logo_path.stem}"></div>'
        )

    st.markdown(
        f'<div class="logo-banner"><div class="logo-row">{"".join(logo_html_parts)}</div></div>',
        unsafe_allow_html=True,
    )


def image_signature(image_bytes: bytes) -> str:
    return hashlib.sha256(image_bytes).hexdigest()


@st.cache_resource(show_spinner=False)
def load_deepface() -> Any:
    from deepface import DeepFace

    try:
        DeepFace.build_model("Emotion")
    except Exception:
        # If model warm-up is unavailable, regular analyze() will still try to load it.
        pass
    return DeepFace


def ensure_model_loaded() -> tuple[bool, str | None]:
    try:
        load_deepface()
    except Exception as exc:  # pragma: no cover - environment-specific import risk
        return False, f"DeepFace could not be imported in this environment: {exc}"
    return True, None


def resize_for_analysis(image: np.ndarray, max_width: int = 480) -> np.ndarray:
    height, width = image.shape[:2]
    if width <= max_width:
        return image

    new_height = max(1, int(height * (max_width / width)))
    resized = Image.fromarray(image).resize((max_width, new_height), Image.Resampling.LANCZOS)
    return np.array(resized)


def fast_detect_emotion(image: np.ndarray) -> tuple[str, str]:
    resized = resize_for_analysis(image, max_width=320)
    brightness = float(np.mean(resized))
    contrast = float(np.std(resized))

    if brightness >= 175:
        emotion = "happy"
    elif brightness <= 85:
        emotion = "sad"
    elif contrast >= 70:
        emotion = "surprise"
    else:
        emotion = "neutral"

    return emotion, "Fast Mode is on, so the app used a lightweight fallback mood estimate."


def capture_image() -> np.ndarray | None:
    """Capture a single image from Streamlit camera input and return it as RGB."""
    uploaded = st.camera_input("Take a photo for mood analysis")
    if uploaded is None:
        st.session_state.current_capture_signature = None
        return None

    image_bytes = uploaded.getvalue()
    st.session_state.current_capture_signature = image_signature(image_bytes)

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        st.error("The captured image could not be read. Please retake the photo.")
        return None

    return np.array(image)


def detect_emotion(image: np.ndarray, fast_mode: bool = False) -> tuple[str, str | None]:
    """
    Analyze the image with DeepFace and normalize the result for the demo UI.

    Returns a tuple of (normalized_emotion, status_message).
    """
    if fast_mode:
        return fast_detect_emotion(image)

    try:
        deepface = load_deepface()
    except Exception as exc:  # pragma: no cover - environment-specific import risk
        return "neutral", f"DeepFace could not be imported in this environment: {exc}"

    resized_image = resize_for_analysis(image, max_width=480)

    try:
        raw_analysis = deepface.analyze(
            img_path=resized_image,
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


def get_message(emotion: str, name: str = "", user_greeting: str = "") -> str:
    """Return a random Bengali greeting for the detected emotion."""
    messages = list(MESSAGE_MAP.get(emotion, MESSAGE_MAP["neutral"]))
    cleaned_user_greeting = user_greeting.strip()
    if cleaned_user_greeting and cleaned_user_greeting not in messages:
        messages.append(cleaned_user_greeting)

    greeting = random.choice(messages)
    cleaned_name = name.strip()
    if greeting == cleaned_user_greeting and cleaned_user_greeting:
        signature = f"-{cleaned_name}" if cleaned_name else "-Guest"
    else:
        signature = "-Crit"

    if cleaned_name:
        return f"{cleaned_name}, {greeting} {signature}"
    return f"{greeting} {signature}"


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for font_path in FONT_PATHS:
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def fix_bengali_text(text: str) -> str:
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def generate_qr_code(url: str, size: int = 120) -> Image.Image:
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return qr_image.resize((size, size), Image.Resampling.LANCZOS)


def create_card(message: str, emotion: str, user_image: np.ndarray | None = None) -> Image.Image:
    """Create a simple Boishakh-themed greeting card image."""
    width, height = 900, 520
    image = Image.new("RGB", (width, height), "#FFF8F8")
    draw = ImageDraw.Draw(image)
    photo_layout: dict[str, int] | None = None

    draw.rectangle((0, 0, width, 120), fill="#F6C5C5")
    draw.rectangle((0, height - 95, width, height), fill="#F8D9D9")
    draw.ellipse((40, 30, 190, 180), fill="#E46E6E")
    draw.ellipse((width - 195, 25, width - 45, 175), fill="#F2A3A3")
    draw.ellipse((width - 210, height - 185, width - 35, height - 20), fill="#F1A6A6")
    draw.rounded_rectangle(
        (95, 105, width - 95, height - 105),
        radius=30,
        fill="#FFFFFF",
        outline="#E28A8A",
        width=4,
    )

    title_font = load_font(34)
    message_font = load_font(38)
    footer_font = load_font(24)

    title_text = "Welsome to Boishakh Festival"
    footer_text = f"Detected mood: {emotion.capitalize()} {EMOTION_EMOJIS.get(emotion, '')}".strip()

    title_box = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_box[2] - title_box[0]
    draw.text(((width - title_width) / 2, 40), title_text, fill="#7D1F1F", font=title_font)

    if user_image is not None:
        try:
            user_photo = Image.fromarray(user_image).convert("RGB").resize((180, 180), Image.Resampling.LANCZOS)
            framed_photo = Image.new("RGBA", (196, 196), (255, 255, 255, 255))
            framed_photo.paste(user_photo, (8, 8))
            rotated_photo = framed_photo.rotate(-10, expand=True, resample=Image.Resampling.BICUBIC)
            paste_x = width - rotated_photo.width - 70
            paste_y = 110
            image.paste(rotated_photo, (paste_x, paste_y), rotated_photo)
            photo_layout = {
                "left": paste_x,
                "top": paste_y,
                "right": paste_x + rotated_photo.width,
                "bottom": paste_y + rotated_photo.height,
            }
        except Exception:
            pass

    text_left = 120
    text_top = 150
    text_bottom = height - 125
    text_align = "center"
    safe_right = width - 120

    if photo_layout is not None:
        safe_right = min(safe_right, photo_layout["left"] - 40)
        text_align = "left"

    available_width = max(220, safe_right - text_left)
    available_height = text_bottom - text_top
    font_size = 38
    line_spacing = 16
    wrapped_lines: list[str] = []
    text_block = message
    text_box = (0, 0, 0, 0)

    while font_size >= 26:
        current_font = load_font(font_size)
        trial_lines: list[str] = []
        current_line = ""
        for word in message.split():
            trial_line = f"{current_line} {word}".strip()
            trial_box = draw.textbbox((0, 0), trial_line, font=current_font)
            if trial_box[2] - trial_box[0] <= available_width:
                current_line = trial_line
            else:
                if current_line:
                    trial_lines.append(current_line)
                current_line = word
        if current_line:
            trial_lines.append(current_line)

        trial_block = "\n".join(trial_lines)
        trial_block = fix_bengali_text(trial_block)
        trial_box = draw.multiline_textbbox((0, 0), trial_block, font=current_font, spacing=line_spacing, align=text_align)
        trial_height = trial_box[3] - trial_box[1]
        if trial_height <= available_height:
            message_font = current_font
            wrapped_lines = trial_lines
            text_block = trial_block
            text_box = trial_box
            break
        font_size -= 2
        line_spacing = max(10, line_spacing - 1)
    else:
        message_font = load_font(26)
        wrapped_lines = [message]
        text_block = fix_bengali_text(message)
        text_box = draw.multiline_textbbox((0, 0), text_block, font=message_font, spacing=10, align=text_align)
        line_spacing = 10

    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]
    if photo_layout is not None:
        text_x = text_left
        text_y = text_top + max(0, (available_height - text_height) / 2)
    else:
        text_x = (width - text_width) / 2
        text_y = (height - text_height) / 2
    draw.multiline_text((text_x, text_y), text_block, fill="#8B1E1E", font=message_font, spacing=line_spacing, align=text_align)

    footer_box = draw.textbbox((0, 0), footer_text, font=footer_font)
    footer_width = footer_box[2] - footer_box[0]
    draw.text(((width - footer_width) / 2, height - 72), footer_text, fill="#7D1F1F", font=footer_font)

    try:
        qr = generate_qr_code("https://www.facebook.com/genesisgub", size=120)
        qr_x = 110
        qr_y = height - 160
        image.paste(qr, (qr_x, qr_y))
        qr_label = "Scan to visit Genesis"
        qr_label_box = draw.textbbox((0, 0), qr_label, font=footer_font)
        qr_label_width = qr_label_box[2] - qr_label_box[0]
        qr_label_x = qr_x + ((120 - qr_label_width) / 2)
        qr_label_y = qr_y + 126
        draw.text((qr_label_x, qr_label_y), qr_label, fill="#7D1F1F", font=footer_font)
    except Exception:
        pass

    return image


def emotion_chart_data(history: list[str]) -> dict[str, list[Any]]:
    counts = Counter(history)
    return {
        "emotion": EMOTION_ORDER,
        "count": [counts.get(emotion, 0) for emotion in EMOTION_ORDER],
    }


def image_to_png_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def save_card(image: Image.Image) -> str:
    OUTPUTS_DIR.mkdir(exist_ok=True)
    CARDS_DIR.mkdir(exist_ok=True)
    filename = f"card_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    file_path = CARDS_DIR / filename
    image.save(file_path, format="PNG")
    return str(file_path)


def log_entry(name: str, emotion: str, fast_mode: bool, file_path: str) -> None:
    OUTPUTS_DIR.mkdir(exist_ok=True)
    file_exists = LOG_FILE.exists()
    with LOG_FILE.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(["timestamp", "name", "emotion", "fast_mode", "file_path"])
        writer.writerow([datetime.now().isoformat(timespec="seconds"), name, emotion, fast_mode, file_path])


def save_temp_png(image: Image.Image) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        image.save(temp_file, format="PNG")
        return temp_file.name


def print_card(image: Image.Image) -> tuple[bool, str]:
    if os.name != "nt":
        return False, "Please download and print manually."

    try:
        temp_path = save_temp_png(image)
        os.startfile(temp_path, "print")
    except Exception:
        return False, "Please download and print manually."

    return True, "Print command sent. If nothing happens, please download and print manually."


def percentage_breakdown(history: list[str]) -> dict[str, float]:
    if not history:
        return {emotion: 0.0 for emotion in EMOTION_ORDER}

    counts = Counter(history)
    total = len(history)
    return {emotion: (counts.get(emotion, 0) / total) * 100 for emotion in EMOTION_ORDER}


def festival_mood_score(history: list[str]) -> float:
    if not history:
        return 0.0
    return sum(FESTIVAL_MOOD_SCORES.get(emotion, 0.5) for emotion in history) / len(history)


def maybe_process_capture(image: np.ndarray, name: str, fast_mode: bool, user_greeting: str = "") -> None:
    current_signature = st.session_state.get("current_capture_signature")
    last_signature = st.session_state.get("last_processed_signature")

    if not current_signature or current_signature == last_signature:
        return

    with st.spinner("Analyzing mood from the captured photo..."):
        emotion, status_message = detect_emotion(image, fast_mode=fast_mode)
        cleaned_user_greeting = user_greeting.strip()
        temp_message_map = MESSAGE_MAP.copy()
        if cleaned_user_greeting and cleaned_user_greeting not in MESSAGE_MAP.get(emotion, MESSAGE_MAP["neutral"]):
            temp_message_map[emotion] = MESSAGE_MAP.get(emotion, MESSAGE_MAP["neutral"]) + [cleaned_user_greeting]
        session_user_greeting = cleaned_user_greeting if cleaned_user_greeting in temp_message_map.get(emotion, []) else ""
        message = get_message(emotion, name=name, user_greeting=session_user_greeting)
        card = create_card(message, emotion, user_image=image)
        saved_file_path = save_card(card)
        log_entry(name.strip(), emotion, fast_mode, saved_file_path)
        card_bytes = image_to_png_bytes(card)

    st.session_state.emotion_history.append(emotion)
    st.session_state.last_processed_signature = current_signature
    st.session_state.last_result = {
        "image": image,
        "emotion": emotion,
        "message": message,
        "card": card,
        "card_bytes": card_bytes,
        "saved_file_path": saved_file_path,
        "status_message": status_message,
        "name": name.strip(),
        "fast_mode": fast_mode,
    }


def render_percentage_breakdown(history: list[str]) -> None:
    percentages = percentage_breakdown(history)
    lines = [
        f"{emotion.capitalize()} {EMOTION_EMOJIS[emotion]}: {percentages[emotion]:.1f}%"
        for emotion in EMOTION_ORDER
    ]
    st.markdown("\n".join(f"- {line}" for line in lines))


def main() -> None:
    st.set_page_config(page_title="Crit by GENESIS", page_icon="🌺", layout="centered")
    apply_theme()

    render_logos()
    st.title("Welcome to GENESIS booth!")
    st.caption("Fully local Boishakh greeting demo with emotion detection, download, printing, and mood analytics.")

    if "emotion_history" not in st.session_state:
        st.session_state.emotion_history = []
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_processed_signature" not in st.session_state:
        st.session_state.last_processed_signature = None
    if "current_capture_signature" not in st.session_state:
        st.session_state.current_capture_signature = None
    if "model_ready" not in st.session_state:
        st.session_state.model_ready = False

    st.markdown('<div class="boishakh-panel">', unsafe_allow_html=True)
    st.subheader("Capture & Generate Greeting Card")
    capture_col, form_col = st.columns([1.3, 0.9], vertical_alignment="top")
    with capture_col:
        captured_image = capture_image()
    with form_col:
        name = st.text_input("Enter your name (optional)")
        user_greeting = st.text_input("Write your own Boishakh greeting (optional)")
        fast_mode = st.checkbox("⚡ Fast Mode", help="Uses a lightweight fallback estimate for faster live demos.")
    st.markdown("</div>", unsafe_allow_html=True)

    if not fast_mode and captured_image is not None and not st.session_state.model_ready:
        with st.spinner("Loading AI model (first run may take time)..."):
            model_ready, model_message = ensure_model_loaded()
        st.session_state.model_ready = model_ready
        if model_message:
            st.warning(model_message)

    if captured_image is not None:
        maybe_process_capture(captured_image, name=name, fast_mode=fast_mode, user_greeting=user_greeting)
    else:
        st.info("Take a camera photo to start the emotion detection demo.")

    result = st.session_state.last_result
    if result:
        st.markdown('<div class="boishakh-panel">', unsafe_allow_html=True)
        st.subheader("Detected Result")

        preview_col, details_col = st.columns([1.05, 0.95])
        with preview_col:
            st.image(result["image"], channels="RGB", use_container_width=True)

        with details_col:
            emoji = EMOTION_EMOJIS.get(result["emotion"], "")
            st.markdown(
                f"<div class='boishakh-title'>Emotion</div><div>{result['emotion'].capitalize()} {emoji}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='boishakh-title' style='margin-top:0.75rem;'>Greeting</div><div>{result['message']}</div>",
                unsafe_allow_html=True,
            )
            if result["status_message"]:
                st.warning(result["status_message"])
            if result["fast_mode"]:
                st.caption("Fast Mode was used for this result.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="boishakh-panel boishakh-center">', unsafe_allow_html=True)
        st.subheader("Greeting Card")
        left_col, center_col, right_col = st.columns([0.08, 0.84, 0.08])
        with center_col:
            st.image(result["card"], use_container_width=True)

        action_col1, action_col2 = st.columns(2)
        with action_col1:
            st.download_button(
                "Download Card (PNG)",
                data=result["card_bytes"],
                file_name="boishakh_greeting_card.png",
                mime="image/png",
                use_container_width=True,
            )
        with action_col2:
            if st.button("Print Card", use_container_width=True):
                success, message = print_card(result["card"])
                if success:
                    st.success(message)
                else:
                    st.warning(message)
        st.markdown("</div>", unsafe_allow_html=True)

    history = st.session_state.emotion_history
    if history:
        st.markdown('<div class="boishakh-panel">', unsafe_allow_html=True)
        st.subheader("Festival Mood Analytics")

        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("Festival Mood Score", f"{festival_mood_score(history):.2f}")
        with metric_col2:
            st.metric("Total Analyses", str(len(history)))

        st.bar_chart(emotion_chart_data(history), x="emotion", y="count")
        st.markdown("**Percentage Breakdown**")
        render_percentage_breakdown(history)
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
