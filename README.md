# YouTube Downloader (Flet)

A simple Flet-based YouTube downloader app.

## Setup

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Run

Start the app from the repo root:
```bash
python main.py
```

## Build / Package

If you want to package the app, install Flet and use the Flet CLI:
```bash
python -m pip install flet
flet pack .
```

Then open the generated package or distribution files.

## Notes

- The app is located in `main.py`.
- `ytdlp_impl.py` handles the download logic.
- No special Flet folder structure is required for this repo.
