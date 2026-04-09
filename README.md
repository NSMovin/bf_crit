# AI Boishakh Mood Detector

`AI Boishakh Mood Detector` is a local Streamlit demo app for Pohela Boishakh that captures a visitor photo, detects emotion, generates a personalized Bengali greeting, and creates a themed greeting card for download or printing.

The app is designed for live demos on low-end laptops and runs fully offline with a `uv`-managed Python environment.

## Features

- Streamlit camera capture with `st.camera_input()`
- Emotion detection with DeepFace using a safe fallback path
- Optional user name personalization in the greeting
- Boishakh-themed greeting card generation with Pillow
- PNG download support for the generated card
- Windows print support with graceful fallback
- Fast Mode for quicker demo performance
- Session-based emotion tracking and analytics
- Festival mood distribution bar chart and mood score
- Local assets for top banner logos in `images/`

## Tech Stack

- Python
- Streamlit
- DeepFace
- TensorFlow / `tf-keras`
- Pillow
- NumPy

## Project Structure

```text
bf_crit_v1.0/
├── app.py
├── images/
├── pyproject.toml
├── uv.lock
└── README.md
```

## Run The App

From the `bf_crit_v1.0` directory:

```bash
uv run streamlit run app.py
```

## Dependency Management

This project uses `uv`. Do not use `pip` or create a separate virtual environment manually.

If dependencies need to be refreshed:

```bash
uv sync
```

## How It Works

1. Capture a photo using the built-in Streamlit camera input.
2. The app analyzes the image locally to estimate the dominant emotion.
3. A Bengali Pohela Boishakh greeting is selected based on the mood.
4. A themed greeting card is generated and shown in the app.
5. The card can be downloaded as PNG or printed on Windows.
6. Emotion history is stored in `st.session_state` for live analytics.

## Demo Notes

- The first DeepFace model load may take extra time.
- `Fast Mode` gives a quicker fallback estimate for smoother live demos.
- If face detection is unclear or DeepFace fails, the app falls back safely instead of crashing.
- Printing is best-effort and currently Windows-first.

## Images

The `images/` folder contains the banner logos used at the top of the app UI.

## Goal

The project is intended as an interactive Pohela Boishakh festival demo that combines AI-based mood detection, personalized greetings, and simple analytics in a compact local application.
