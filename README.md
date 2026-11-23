# Sleep Music App

A soothing ambient-sound mixer built with **Python + Kivy** for cross-platform support (desktop, iOS, Android).

## Features

| Feature | Description |
|---------|-------------|
| **Ambient Sounds Library** | 11 procedurally generated sounds: Rain, Ocean, Forest, Wind, Thunder, Stream, Campfire, White/Pink/Brown Noise, Heartbeat |
| **Sound Mixing** | Layer multiple sounds simultaneously for a custom soundscape |
| **Volume Controls** | Individual volume slider per sound + master volume |
| **Sleep Timer** | Auto-stop after 15 / 30 / 45 / 60 / 90 / 120 minutes |
| **Favourites / Presets** | Save and load custom sound combinations |
| **Dark UI** | Sleep-friendly dark interface designed for bedtime use |

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python main.py
```

On first launch the app generates 11 ambient-sound WAV files (~10 s each) in `generated_sounds/`. This takes a few seconds and only happens once.

## Project Structure

```
├── main.py                  # App entry point & UI logic
├── sleepmusic.kv            # Kivy layout (dark theme)
├── requirements.txt         # Python dependencies
├── core/
│   ├── __init__.py
│   ├── sound_generator.py   # Procedural WAV generation (numpy)
│   ├── audio_engine.py      # Multi-channel playback engine
│   ├── timer_manager.py     # Sleep-timer countdown
│   └── preset_manager.py    # Save/load JSON presets
├── generated_sounds/        # Auto-created WAV files
└── user_data/
    └── presets.json          # Saved user presets
```

## Building for Mobile

### iOS (requires macOS)
```bash
pip install kivy-ios
toolchain build kivy numpy
toolchain create SleepMusic ~/path/to/this/project
# Open the Xcode project and build
```

### Android
```bash
pip install buildozer
buildozer init          # generates buildozer.spec
buildozer android debug # builds APK
```

## Requirements

- Python 3.9+
- Kivy 2.2+
- NumPy 1.24+

## License

MIT
