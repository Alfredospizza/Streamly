<p align="center">
  <img src="assets/streamly.svg" alt="Streamly" width="120">
</p>

<h1 align="center">Streamly</h1>

<p align="center">
  <strong>Free &amp; open-source video/audio downloader — clean, fast, no ads.</strong><br>
  Powered by <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a> · Built with <a href="https://github.com/TomSchimansky/CustomTkinter">CustomTkinter</a>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#download">Download</a> •
  <a href="#build-from-source">Build</a> •
  <a href="#usage">Usage</a> •
  <a href="#license">License</a>
</p>

---

## Features

- **GUI & CLI** — Modern graphical interface or command-line, your choice
- **Video (MP4)** or **Audio only** (MP3, M4A, WAV, FLAC, OPUS)
- **Local library** — Browse and replay your downloaded files
- **Light & Dark theme** — Switch with one click
- **English & Italian** — Full bilingual interface
- **Desktop integration** — Linux installer creates app launcher with icon
- **Cross-platform** — Works on Linux and Windows
- **No accounts, no tracking, no ads**

## Download

Go to the [**Releases**](https://github.com/Alfredospizza/Streamly/releases) page and download the latest version for your OS:

| Platform | File | How to use |
|----------|------|------------|
| **Linux** | `Streamly-linux-portable.tar.gz` | Extract → run `./install_linux.sh` or directly `./Streamly` |
| **Windows** | `Streamly-windows-portable.zip` | Extract → double-click `Streamly.exe` |
| **Windows** | `Streamly-Setup-Windows.exe` | Run the installer |

## Build from Source

### Requirements

- Python 3.10+
- `ffmpeg` and `ffprobe` installed on your system
- [`PyInstaller`](https://pyinstaller.org/) (included in `requirements-build.txt`)

### Setup

```bash
git clone https://github.com/Alfredospizza/Streamly.git
cd Streamly
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\Activate.ps1     # Windows PowerShell
pip install -r requirements.txt
```

### Run from Source

```bash
python streamly_gui.py           # GUI
python streamly.py download URL  # CLI
```

### Build Portable Package

**Linux:**
```bash
pip install -r requirements-build.txt
bash scripts/build_linux.sh
# → release/Streamly-linux-portable.tar.gz
```

**Windows (PowerShell):**
```powershell
pip install -r requirements-build.txt
.\scripts\build_windows.ps1
# → release\Streamly-windows-portable.zip
```

### Windows Installer (.exe)

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Open `packaging/windows/streamly.iss`
3. Click Build

## Usage

### GUI

1. Open the app
2. Paste a YouTube link
3. Choose **Video** or **Audio only**
4. Click **Download Now**

Your files appear in the **Library** tab and in the `downloads/` folder.

### CLI

```bash
# Download video
python streamly.py download "https://www.youtube.com/watch?v=VIDEO_ID" --mode video

# Download audio as MP3
python streamly.py download "https://www.youtube.com/watch?v=VIDEO_ID" --mode audio --audio-format mp3

# Custom output folder
python streamly.py download "URL" --mode video --output ./my_downloads
```

**CLI options:**

| Flag | Values | Default |
|------|--------|---------|
| `--mode` | `video`, `audio` | `video` |
| `--audio-format` | `mp3`, `m4a`, `wav`, `flac`, `opus` | `mp3` |
| `--audio-quality` | `0` (best) – `9` (worst) | `0` |
| `--output` | Path to folder | `./downloads` |
| `--cookies-from-browser` | `chrome`, `firefox`, etc. | — |

## Project Structure

```
Streamly/
├── streamly.py            # CLI download engine
├── streamly_gui.py        # GUI application
├── requirements.txt       # Runtime dependencies
├── requirements-build.txt # Build dependencies
├── pyproject.toml         # Python project metadata
├── assets/
│   └── streamly.svg       # App icon
├── scripts/
│   ├── build_linux.sh     # Linux build script
│   ├── build_windows.ps1  # Windows build script
│   └── install_linux.sh   # Linux desktop installer
└── packaging/
    └── windows/
        └── streamly.iss   # Inno Setup installer script
```

## FFmpeg Note

The build scripts automatically bundle `ffmpeg` and `ffprobe` if they are found on your system. If not, you can copy them manually:

- Linux: `dist/Streamly/tools/linux/`
- Windows: `dist/Streamly/tools/windows/`

FFmpeg is required for audio conversion (MP3, FLAC, etc.).

## Legal Notice

> **Streamly** is a tool. Use it only to download content you have the legal right to download.
> Respect terms of service, copyright laws, and local regulations.
> The developers assume no responsibility for misuse.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

## License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">Made with ❤️ by <a href="https://github.com/Alfredospizza">Alfredospizza</a></p>
