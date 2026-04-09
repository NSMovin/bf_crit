# AI Boishakh Mood Detector

`AI Boishakh Mood Detector` is a local Streamlit demo app for Pohela Boishakh. It captures a visitor photo, estimates emotion, generates a personalized Bengali greeting, and produces a themed greeting card with download, print, QR, and analytics support.

The app is designed as an offline demo for festival or club showcase use and runs inside a `uv`-managed Python project.

## Features

- Streamlit camera capture with `st.camera_input()`
- Emotion detection with DeepFace and safe fallback behavior
- Optional name personalization
- Optional user-contributed Boishakh greeting input
- Greeting card generation with Pillow
- User photo embedded into the generated card
- QR code linking to the GENESIS Facebook page
- PNG download support for generated cards
- Windows print support with graceful fallback
- Fast Mode for smoother demo performance on low-end laptops
- Session-based analytics with bar chart and festival mood score
- Persistent local card saving in `outputs/cards/`
- CSV logging in `outputs/logs.csv`
- Club footer section with project and contributor information
- Custom Boishakh UI theme with logos and background image support
- Bundled Bengali font support from `fonts/`
- Bengali text shaping attempt using `arabic-reshaper` and `python-bidi`

## Current Status

This version is working as a live demo application, but there are still a few known limitations that should be improved:

- Bengali font rendering in generated cards still needs work. Even with shaping and bundled fonts, some Bangla output can still appear scuffed, improperly spaced, or not fully natural.
- Emotion classification needs more validation across different lighting conditions, camera quality, and facial angles.
- Greeting card output quality still needs broader testing to confirm layout consistency for long text, user-written greetings, QR placement, and user photo placement.
- Printing is best-effort and primarily Windows-oriented.

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

## How To Run On Any System

### Requirements

- Python compatible with the project `pyproject.toml`
- `uv` installed on the system
- Webcam access enabled if you want to use live capture

### Setup

From the `bf_crit_v1.0` directory:

```bash
uv sync
```

This installs and syncs the dependencies defined in `pyproject.toml` and `uv.lock`.

### Run

```bash
uv run streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Cross-System Notes

- The app is designed to run locally and offline.
- The bundled Bengali font in `fonts/` helps portability across different laptops and systems.
- Windows printing is supported through the print action in the app.
- On Linux or macOS, the app still runs, but print behavior may need manual download-and-print instead.
- If the background image is not visible, confirm the file exists at `images/background/background.png`.

## How It Works

1. Capture a photo using the built-in Streamlit camera input.
2. The app analyzes the image locally to estimate the dominant emotion.
3. A Bengali Pohela Boishakh greeting is selected based on the emotion, with support for an optional user-written greeting.
4. A themed greeting card is generated with Bengali text, optional user photo placement, and a QR code.
5. The card is displayed in the app and can be downloaded or printed.
6. The generated card is saved locally and the event is logged to CSV.
7. Emotion history is stored in `st.session_state` for live analytics.

## Outputs

- Saved greeting cards: `outputs/cards/`
- CSV log file: `outputs/logs.csv`

These are runtime-generated files and are meant for local demo output.

## Testing And Validation Still Needed

The project would benefit from more formal testing in the following areas:

- Emotion classification accuracy for `happy`, `sad`, `neutral`, and `surprise`
- Fast Mode versus normal mode output behavior
- Bengali text rendering quality across multiple greetings
- Greeting card layout with long names and long custom greetings
- QR code visibility and scan success from generated cards
- User photo placement and overlap edge cases
- Output saving and logging consistency
- Cross-system behavior on Windows, Linux, and different laptop hardware

## Documentation Still Needed

The project can still be improved with more documentation around:

- deployment and demo setup steps
- font troubleshooting for Bengali text rendering
- expected model load times
- known DeepFace limitations
- sample screenshots and example outputs

## Images And Fonts

- `images/` contains logo and background assets used by the UI
- `fonts/` contains the bundled Bengali font used by the card generator

## Goal

The goal of this project is to create a festival-ready AI demo that combines computer vision, emotion analysis, personalized cultural interaction, and lightweight analytics in a compact local application for GENESIS and the Department of AI & Data Science.
