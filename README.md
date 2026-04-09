# AI Boishakh Mood Detector

`AI Boishakh Mood Detector` is a local Streamlit demo app for Pohela Boishakh that captures a visitor photo, detects emotion, generates a personalized Bengali greeting, and creates a themed greeting card for download, printing, and sharing.

The app is designed for live demos on low-end laptops and runs fully offline with a `uv`-managed Python environment.

## Features

- Streamlit camera capture with `st.camera_input()`
- Emotion detection with DeepFace using a safe fallback path
- Optional user name personalization in the greeting
- Optional user-contributed Boishakh greeting input
- Boishakh-themed greeting card generation with Pillow
- Proper Bengali text shaping in generated cards
- User photo embedded into the generated greeting card
- QR code linking to the Genesis Facebook page
- PNG download support for the generated card
- Windows print support with graceful fallback
- Fast Mode for quicker demo performance
- Session-based emotion tracking and analytics
- Festival mood distribution bar chart and mood score
- Local assets for top banner logos in `images/`
- Bundled Bengali font in `fonts/`
- Local card saving and CSV logging in `outputs/`

## Tech Stack

- Python
- Streamlit
- DeepFace
- TensorFlow / `tf-keras`
- Pillow
- NumPy
- `arabic-reshaper`
- `python-bidi`
- `qrcode`

## Project Structure

```text
bf_crit_v1.0/
├── app.py
├── fonts/
├── images/
├── outputs/
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
3. A Bengali Pohela Boishakh greeting is selected based on the mood, with support for an optional user-written greeting.
4. A themed greeting card is generated with Bengali text shaping, optional user photo placement, and a QR code.
5. The card is shown in the app, saved locally, and logged to CSV.
6. The card can be downloaded as PNG or printed on Windows.
7. Emotion history is stored in `st.session_state` for live analytics.

## Demo Notes

- The first DeepFace model load may take extra time.
- `Fast Mode` gives a quicker fallback estimate for smoother live demos.
- If face detection is unclear or DeepFace fails, the app falls back safely instead of crashing.
- Printing is best-effort and currently Windows-first.
- Generated cards are saved to `outputs/cards/`.
- Capture logs are appended to `outputs/logs.csv`.

## Images

The `images/` folder contains the banner logos used at the top of the app UI, and `fonts/` contains the bundled Bengali font used for portable text rendering.

## Goal

The project is intended as an interactive Pohela Boishakh festival demo that combines AI-based mood detection, personalized greetings, and simple analytics in a compact local application.
