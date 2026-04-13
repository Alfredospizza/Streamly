#!/usr/bin/env python3
"""Streamly CLI: simple YouTube downloader using yt-dlp.

Usage examples:
  python streamly.py download "https://www.youtube.com/watch?v=..." --mode video
  python streamly.py download "https://www.youtube.com/watch?v=..." --mode audio --audio-format mp3
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Callable

from yt_dlp import DownloadError, YoutubeDL


def runtime_root() -> Path:
    """Resolve runtime root for source and packaged executions."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def find_ffmpeg_location() -> str | None:
    """Return a directory containing ffmpeg and ffprobe, if available."""
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return None

    root = runtime_root()
    platform_dir = "windows" if sys.platform.startswith("win") else "linux"
    candidates = [
        root / "tools" / platform_dir,
        root / "tools",
        root / "bin",
    ]

    ffmpeg_name = "ffmpeg.exe" if sys.platform.startswith("win") else "ffmpeg"
    ffprobe_name = "ffprobe.exe" if sys.platform.startswith("win") else "ffprobe"

    for candidate in candidates:
        if (candidate / ffmpeg_name).exists() and (candidate / ffprobe_name).exists():
            return str(candidate)

    return None


def build_options(
    url: str,
    mode: str = "video",
    audio_format: str = "mp3",
    audio_quality: str = "0",
    output: str = "downloads",
    cookies_from_browser: str = "",
) -> tuple[str, dict]:
    """Build URL and yt-dlp options from input settings."""
    output_template = str(Path(output).expanduser() / "%(title)s.%(ext)s")

    options: dict = {
        "noplaylist": True,
        "outtmpl": output_template,
    }

    if mode == "video":
        options["format"] = "bestvideo*+bestaudio/best"
        options["merge_output_format"] = "mp4"
    else:
        options["format"] = "bestaudio"
        options["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format,
                "preferredquality": audio_quality,
            }
        ]

    if cookies_from_browser:
        options["cookiesfrombrowser"] = (cookies_from_browser,)

    ffmpeg_location = find_ffmpeg_location()
    if ffmpeg_location:
        options["ffmpeg_location"] = ffmpeg_location

    return url, options


class UILogger:
    """yt-dlp logger that forwards messages to a callback."""

    def __init__(self, sink: Callable[[str], None] | None) -> None:
        self.sink = sink

    def debug(self, msg: str) -> None:
        if self.sink and msg.strip():
            self.sink(msg)

    def warning(self, msg: str) -> None:
        if self.sink and msg.strip():
            self.sink("[WARN] " + msg)

    def error(self, msg: str) -> None:
        if self.sink and msg.strip():
            self.sink("[ERROR] " + msg)


def download_url(
    url: str,
    mode: str = "video",
    audio_format: str = "mp3",
    audio_quality: str = "0",
    output: str = "downloads",
    cookies_from_browser: str = "",
    log_callback: Callable[[str], None] | None = None,
    progress_callback: Callable[[float, str], None] | None = None,
) -> int:
    """Download a URL with yt-dlp API. Returns 0 on success, 1 on failure."""
    Path(output).expanduser().mkdir(parents=True, exist_ok=True)
    target_url, options = build_options(
        url=url,
        mode=mode,
        audio_format=audio_format,
        audio_quality=audio_quality,
        output=output,
        cookies_from_browser=cookies_from_browser,
    )

    percent_pattern = re.compile(r"([0-9]+(?:\.[0-9]+)?)%")
    ansi_pattern = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

    def _progress_hook(data: dict) -> None:
        status = data.get("status")
        if status == "downloading":
            pct = ansi_pattern.sub("", data.get("_percent_str", "")).strip()
            speed = ansi_pattern.sub("", data.get("_speed_str", "")).strip()
            eta = ansi_pattern.sub("", data.get("_eta_str", "")).strip()
            msg = f"Download {pct}"
            if speed:
                msg += f" | {speed}"
            if eta:
                msg += f" | ETA {eta}"
            if log_callback:
                log_callback(msg)

            if progress_callback:
                match = percent_pattern.search(pct)
                if match:
                    value = max(0.0, min(100.0, float(match.group(1))))
                    progress_text = f"{int(round(value))}%"
                    if speed:
                        progress_text += f" | {speed}"
                    if eta:
                        progress_text += f" | ETA {eta}"
                    progress_callback(value / 100.0, progress_text)
        elif status == "finished":
            if log_callback:
                log_callback("Download completato, avvio elaborazione...")
            if progress_callback:
                progress_callback(1.0, "Elaborazione finale...")

    if log_callback:
        options["logger"] = UILogger(log_callback)
    if log_callback or progress_callback:
        options["progress_hooks"] = [_progress_hook]

    try:
        with YoutubeDL(options) as ydl:
            ydl.download([target_url])
        if log_callback:
            log_callback("Completato con successo.")
        return 0
    except DownloadError as exc:
        if log_callback:
            log_callback(f"Errore download: {exc}")
        return 1


def download(args: argparse.Namespace) -> int:
    """Run yt-dlp with selected options."""
    print("Avvio download...")
    return download_url(
        url=args.url,
        mode=args.mode,
        audio_format=args.audio_format,
        audio_quality=args.audio_quality,
        output=args.output,
        cookies_from_browser=args.cookies_from_browser,
        log_callback=print,
    )


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="streamly",
        description="Downloader YouTube libero basato su yt-dlp.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    dl = subparsers.add_parser("download", help="Scarica un video o audio da YouTube")
    dl.add_argument("url", help="URL YouTube")
    dl.add_argument(
        "--mode",
        choices=["video", "audio"],
        default="video",
        help="Seleziona download video o solo audio",
    )
    dl.add_argument(
        "--audio-format",
        choices=["mp3", "m4a", "wav", "flac", "opus"],
        default="mp3",
        help="Formato audio se --mode audio",
    )
    dl.add_argument(
        "--audio-quality",
        default="0",
        help="Qualita audio per yt-dlp/ffmpeg (0 migliore, 9 peggiore)",
    )
    dl.add_argument(
        "--output",
        default="downloads",
        help="Cartella di destinazione (default: downloads)",
    )
    dl.add_argument(
        "--cookies-from-browser",
        default="",
        help="Browser per import cookie (es. chrome, firefox) se necessario",
    )
    dl.set_defaults(func=download)

    return parser


def main() -> int:
    parser = make_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
