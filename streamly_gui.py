#!/usr/bin/env python3
"""Focused Streamly GUI with smooth theme/language switching and local library."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk
from tkinter import filedialog, messagebox

from streamly import download_url


TRANSLATIONS = {
    "it": {
        "subtitle": "Incolla un link YouTube e scarica video o audio in pochi secondi.",
        "tab_download": "Scarica",
        "tab_library": "Libreria",
        "promo_title": "Downloader pulito e diretto",
        "promo_text": "Se l'idea ti piace e vuoi parlarne o supportare il progetto, scrivimi su Telegram.",
        "promo_button": "Apri Telegram",
        "new": "NEW",
        "link": "Link",
        "paste": "Incolla",
        "type": "Tipo",
        "video": "Video (MP4)",
        "audio_only": "Solo audio",
        "audio": "Audio",
        "save_in": "Salva in",
        "browse": "Sfoglia",
        "download_now": "Scarica Ora",
        "ready": "Pronto",
        "idle": "Nessun download in corso",
        "library_title": "Playlist Locale",
        "open_folder": "Apri Cartella",
        "refresh": "Aggiorna",
        "library_empty": "La playlist locale è vuota. Scarica qualcosa e comparirà qui.",
        "open": "Apri",
        "folder": "Cartella",
        "download_start": "Download in corso...",
        "connecting": "Connessione a YouTube...",
        "completed": "Completato",
        "completed_text": "Download completato con successo",
        "failed": "Download fallito",
        "error": "Errore",
        "choose_folder": "Scegli cartella di destinazione",
        "missing_url": "Inserisci un link YouTube.",
        "download_done_msg": "Download completato.",
        "download_error_msg": "Si e verificato un errore durante il download.",
        "downloads_label": "file",
        "folder_label": "cartella",
        "placeholder_url": "https://www.youtube.com/watch?v=...",
    },
    "en": {
        "subtitle": "Paste a YouTube link and download video or audio in seconds.",
        "tab_download": "Download",
        "tab_library": "Library",
        "promo_title": "Clean and direct downloader",
        "promo_text": "If you like the idea and want to support the project, contact me on Telegram.",
        "promo_button": "Open Telegram",
        "new": "NEW",
        "link": "Link",
        "paste": "Paste",
        "type": "Type",
        "video": "Video (MP4)",
        "audio_only": "Audio only",
        "audio": "Audio",
        "save_in": "Save to",
        "browse": "Browse",
        "download_now": "Download Now",
        "ready": "Ready",
        "idle": "No download in progress",
        "library_title": "Local Playlist",
        "open_folder": "Open Folder",
        "refresh": "Refresh",
        "library_empty": "Your local playlist is empty. Download something and it will show up here.",
        "open": "Open",
        "folder": "Folder",
        "download_start": "Downloading...",
        "connecting": "Connecting to YouTube...",
        "completed": "Completed",
        "completed_text": "Download completed successfully",
        "failed": "Download failed",
        "error": "Error",
        "choose_folder": "Choose destination folder",
        "missing_url": "Insert a YouTube link.",
        "download_done_msg": "Download completed.",
        "download_error_msg": "An error occurred during the download.",
        "downloads_label": "files",
        "folder_label": "folder",
        "placeholder_url": "https://www.youtube.com/watch?v=...",
    },
}


class StreamlyGUI:
    def __init__(self, root: ctk.CTk) -> None:
        self.root = root
        self.root.title("Streamly")
        self.root.geometry("1120x760")
        self.root.minsize(980, 700)

        self.current_language = "it"
        self.current_theme = "dark"

        self.url_var = ctk.StringVar()
        self.mode_var = ctk.StringVar(value="video")
        self.audio_format_var = ctk.StringVar(value="mp3")
        self.output_var = ctk.StringVar(value=str(Path("downloads").resolve()))
        self.status_var = ctk.StringVar()
        self.library_stats_var = ctk.StringVar(value="")
        self.is_downloading = False

        self.status_message_key: str | None = "ready"
        self.status_message_raw: str | None = None
        self.progress_message_key: str | None = "idle"
        self.progress_message_raw: str | None = None

        self.logo_image: ctk.CTkImage | None = None
        self.window_icon = None
        self.logo_cache: dict[str, tuple[ctk.CTkImage, object]] = {}
        self.library_rows: list[dict[str, object]] = []
        self.library_empty_label: ctk.CTkLabel | None = None
        self.library_count = 0
        self.library_total_size = 0
        self.library_folder = Path(self.output_var.get())

        self._build_ui()
        self._apply_language()
        self._apply_theme(refresh_library=False)
        self._refresh_library()

    def t(self, key: str) -> str:
        return TRANSLATIONS[self.current_language][key]

    def _palette(self) -> dict[str, str]:
        if self.current_theme == "light":
            return {
                "app_bg": "#eef2f6",
                "surface": "#f7f9fb",
                "header": "#ffffff",
                "card": "#ffffff",
                "promo": "#ecf9f0",
                "promo_border": "#9bd5ad",
                "text": "#16202b",
                "muted": "#5e6876",
                "border": "#d8dee7",
                "input": "#fdfefe",
                "accent": "#179b45",
                "accent_hover": "#1db954",
                "accent_text": "#ffffff",
                "secondary": "#e9edf4",
                "secondary_hover": "#dde4ed",
                "secondary_text": "#22303d",
                "progress_bg": "#dde4ec",
                "badge_text": "#ffffff",
                "badge_bg": "#179b45",
                "tab_fg": "#eef2f6",
                "tab_button_fg": "#dfe5ed",
                "tab_button_unselected": "#e5ebf2",
                "tab_button_hover": "#d7e0ea",
                "switch_shell": "#179b45",
                "switch_shell_hover": "#1db954",
                "switch_selected": "#ffffff",
                "switch_selected_text": "#179b45",
                "switch_unselected_text": "#ffffff",
                "switch_border": "#179b45",
                "logo_start": "#de74b8",
                "logo_end": "#b0d5ea",
                "logo_wave": "#0f1014",
            }
        return {
            "app_bg": "#0a0a0a",
            "surface": "#111315",
            "header": "#0e1012",
            "card": "#12161a",
            "promo": "#132017",
            "promo_border": "#2f7f4c",
            "text": "#eff2f5",
            "muted": "#8f9aa3",
            "border": "#252a2f",
            "input": "#0b0d0f",
            "accent": "#179b45",
            "accent_hover": "#1db954",
            "accent_text": "#ffffff",
            "secondary": "#2b3137",
            "secondary_hover": "#39424a",
            "secondary_text": "#f2f5f7",
            "progress_bg": "#242a30",
            "badge_text": "#ffffff",
            "badge_bg": "#179b45",
            "tab_fg": "#111315",
            "tab_button_fg": "#1d2329",
            "tab_button_unselected": "#222931",
            "tab_button_hover": "#2d353e",
            "switch_shell": "#179b45",
            "switch_shell_hover": "#1db954",
            "switch_selected": "#ffffff",
            "switch_selected_text": "#179b45",
            "switch_unselected_text": "#ffffff",
            "switch_border": "#179b45",
            "logo_start": "#de74b8",
            "logo_end": "#a9d3e7",
            "logo_wave": "#0f1014",
        }

    def _build_ui(self) -> None:
        ctk.set_appearance_mode(self.current_theme)
        ctk.set_default_color_theme("green")

        self.font_title = ctk.CTkFont(family="Poppins", size=30, weight="bold")
        self.font_body = ctk.CTkFont(family="Inter", size=14)
        self.font_label = ctk.CTkFont(family="Inter", size=15, weight="bold")
        self.font_button = ctk.CTkFont(family="Inter", size=14, weight="bold")
        self.font_status = ctk.CTkFont(family="Inter", size=14, weight="bold")
        self.font_switch = ctk.CTkFont(family="Inter", size=13, weight="bold")

        colors = self._palette()

        self.container = ctk.CTkFrame(self.root, fg_color=colors["app_bg"], corner_radius=0)
        self.container.pack(fill="both", expand=True)

        self.main_card = ctk.CTkFrame(
            self.container,
            fg_color=colors["surface"],
            corner_radius=12,
            border_color=colors["border"],
            border_width=1,
        )
        self.main_card.pack(fill="both", expand=True, padx=18, pady=18)

        self.header = ctk.CTkFrame(self.main_card, fg_color=colors["header"], corner_radius=12)
        self.header.pack(fill="x", padx=14, pady=(14, 10))

        self.header_top = ctk.CTkFrame(self.header, fg_color="transparent")
        self.header_top.pack(fill="x", padx=16, pady=(14, 0))

        self.brand_row = ctk.CTkFrame(self.header_top, fg_color="transparent")
        self.brand_row.pack(side="left", fill="x", expand=True)

        self.logo_label = ctk.CTkLabel(self.brand_row, text="")
        self.logo_label.pack(side="left", padx=(0, 14))

        self.brand_text = ctk.CTkFrame(self.brand_row, fg_color="transparent")
        self.brand_text.pack(side="left", fill="y")

        self.title_label = ctk.CTkLabel(self.brand_text, text="Streamly", font=self.font_title)
        self.title_label.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(self.header, font=self.font_body, anchor="w")
        self.subtitle_label.pack(anchor="w", padx=16, pady=(4, 14))

        self.toggle_row = ctk.CTkFrame(self.header_top, fg_color="transparent")
        self.toggle_row.pack(side="right")

        self.language_toggle = ctk.CTkSegmentedButton(
            self.toggle_row,
            values=["IT", "EN"],
            width=176,
            height=44,
            corner_radius=22,
            border_width=0,
            font=self.font_switch,
            command=self._on_language_toggle,
        )
        self.language_toggle.pack(side="left", padx=(0, 10))

        self.theme_toggle = ctk.CTkSegmentedButton(
            self.toggle_row,
            values=["☀", "☾"],
            width=124,
            height=44,
            corner_radius=22,
            border_width=0,
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            command=self._on_theme_toggle,
        )
        self.theme_toggle.pack(side="left")

        self.content = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=18, pady=(4, 18))

        self.tabview = ctk.CTkTabview(self.content, corner_radius=12)
        self.tabview.pack(fill="both", expand=True)
        self.tab_name_download = self.t("tab_download")
        self.tab_name_library = self.t("tab_library")
        self.download_tab = self.tabview.add(self.tab_name_download)
        self.library_tab = self.tabview.add(self.tab_name_library)
        self.tabview.set(self.tab_name_download)

        self._build_download_tab()
        self._build_library_tab()
        self._toggle_audio_controls()

    def _build_download_tab(self) -> None:
        self.promo_card = ctk.CTkFrame(self.download_tab, corner_radius=12, border_width=1)
        self.promo_card.pack(fill="x", pady=(8, 12))

        self.promo_top = ctk.CTkFrame(self.promo_card, fg_color="transparent")
        self.promo_top.pack(fill="x", padx=14, pady=(14, 6))
        self.promo_title_label = ctk.CTkLabel(self.promo_top, font=self.font_label)
        self.promo_title_label.pack(side="left")
        self.new_badge = ctk.CTkLabel(self.promo_top, font=self.font_button, corner_radius=999, padx=10, pady=2)
        self.new_badge.pack(side="right")

        self.promo_text_label = ctk.CTkLabel(self.promo_card, font=self.font_body, anchor="w")
        self.promo_text_label.pack(fill="x", padx=14)

        self.promo_bottom = ctk.CTkFrame(self.promo_card, fg_color="transparent")
        self.promo_bottom.pack(fill="x", padx=14, pady=(10, 14))
        self.telegram_label = ctk.CTkLabel(self.promo_bottom, text="@mrnobody4444", font=self.font_status, cursor="hand2")
        self.telegram_label.pack(side="left")
        self.telegram_label.bind("<Button-1>", lambda _event: self._open_telegram())
        self.promo_button = ctk.CTkButton(
            self.promo_bottom,
            command=self._open_telegram,
            height=38,
            width=150,
            corner_radius=12,
            font=self.font_button,
        )
        self.promo_button.pack(side="right")

        self.controls_card = ctk.CTkFrame(self.download_tab, corner_radius=12, border_width=1)
        self.controls_card.pack(fill="both", expand=True)

        url_row = ctk.CTkFrame(self.controls_card, fg_color="transparent")
        url_row.pack(fill="x", padx=12, pady=(14, 8))
        self.link_label = ctk.CTkLabel(url_row, width=90, anchor="w", font=self.font_label)
        self.link_label.pack(side="left")
        self.url_entry = ctk.CTkEntry(url_row, textvariable=self.url_var, height=44, corner_radius=12, font=self.font_body)
        self.url_entry.pack(side="left", fill="x", expand=True)
        self.paste_button = ctk.CTkButton(
            url_row,
            command=self._paste_link,
            height=44,
            width=110,
            corner_radius=12,
            font=self.font_button,
        )
        self.paste_button.pack(side="left", padx=(10, 0))

        opts_row = ctk.CTkFrame(self.controls_card, fg_color="transparent")
        opts_row.pack(fill="x", padx=12, pady=(2, 8))
        self.type_label = ctk.CTkLabel(opts_row, width=90, anchor="w", font=self.font_label)
        self.type_label.pack(side="left")
        self.video_radio = ctk.CTkRadioButton(opts_row, value="video", variable=self.mode_var, command=self._toggle_audio_controls, font=self.font_body)
        self.video_radio.pack(side="left", padx=(0, 14))
        self.audio_radio = ctk.CTkRadioButton(opts_row, value="audio", variable=self.mode_var, command=self._toggle_audio_controls, font=self.font_body)
        self.audio_radio.pack(side="left")

        audio_row = ctk.CTkFrame(self.controls_card, fg_color="transparent")
        audio_row.pack(fill="x", padx=12, pady=(2, 8))
        self.audio_label = ctk.CTkLabel(audio_row, width=90, anchor="w", font=self.font_label)
        self.audio_label.pack(side="left")
        self.audio_combo = ctk.CTkOptionMenu(
            audio_row,
            variable=self.audio_format_var,
            values=["mp3", "m4a", "wav", "flac", "opus"],
            width=180,
            height=38,
            corner_radius=12,
            font=self.font_body,
        )
        self.audio_combo.pack(side="left")

        save_row = ctk.CTkFrame(self.controls_card, fg_color="transparent")
        save_row.pack(fill="x", padx=12, pady=(2, 10))
        self.save_label = ctk.CTkLabel(save_row, width=90, anchor="w", font=self.font_label)
        self.save_label.pack(side="left")
        self.output_entry = ctk.CTkEntry(save_row, textvariable=self.output_var, height=44, corner_radius=12, font=self.font_body)
        self.output_entry.pack(side="left", fill="x", expand=True)
        self.browse_button = ctk.CTkButton(
            save_row,
            command=self._choose_output,
            height=44,
            width=110,
            corner_radius=12,
            font=self.font_button,
        )
        self.browse_button.pack(side="left", padx=(10, 0))

        actions_row = ctk.CTkFrame(self.controls_card, fg_color="transparent")
        actions_row.pack(fill="x", padx=12, pady=(2, 10))
        self.download_button = ctk.CTkButton(
            actions_row,
            command=self._start_download,
            height=46,
            width=170,
            corner_radius=12,
            font=self.font_button,
        )
        self.download_button.pack(side="left")
        self.status_label = ctk.CTkLabel(actions_row, textvariable=self.status_var, font=self.font_status)
        self.status_label.pack(side="left", padx=(14, 0))

        self.progress = ctk.CTkProgressBar(self.controls_card, width=920, height=14, corner_radius=12, border_width=0)
        self.progress.pack(fill="x", padx=12, pady=(4, 8))
        self.progress.set(0)

        self.progress_text = ctk.CTkLabel(self.controls_card, font=self.font_body, anchor="w")
        self.progress_text.pack(fill="x", padx=12, pady=(0, 14))

    def _build_library_tab(self) -> None:
        self.library_header = ctk.CTkFrame(self.library_tab, corner_radius=12, border_width=1)
        self.library_header.pack(fill="x", pady=(8, 12))
        top_row = ctk.CTkFrame(self.library_header, fg_color="transparent")
        top_row.pack(fill="x", padx=14, pady=(14, 4))
        self.library_title_label = ctk.CTkLabel(top_row, font=self.font_label)
        self.library_title_label.pack(side="left")
        self.open_folder_button = ctk.CTkButton(
            top_row,
            command=self._open_output_folder,
            height=36,
            width=140,
            corner_radius=12,
            font=self.font_button,
        )
        self.open_folder_button.pack(side="right")
        self.refresh_button = ctk.CTkButton(
            top_row,
            command=self._refresh_library,
            height=36,
            width=110,
            corner_radius=12,
            font=self.font_button,
        )
        self.refresh_button.pack(side="right", padx=(0, 8))
        self.library_stats_label = ctk.CTkLabel(self.library_header, textvariable=self.library_stats_var, font=self.font_body, anchor="w")
        self.library_stats_label.pack(fill="x", padx=14, pady=(0, 14))

        self.library_frame = ctk.CTkScrollableFrame(self.library_tab, corner_radius=12, border_width=1)
        self.library_frame.pack(fill="both", expand=True)

    def _blend_color(self, start_hex: str, end_hex: str, ratio: float) -> tuple[int, int, int]:
        ratio = max(0.0, min(1.0, ratio))
        start = tuple(int(start_hex[index:index + 2], 16) for index in (1, 3, 5))
        end = tuple(int(end_hex[index:index + 2], 16) for index in (1, 3, 5))
        return tuple(int(start[i] + (end[i] - start[i]) * ratio) for i in range(3))

    def _create_logo_pil(self, size: int) -> Image.Image:
        scale = 4
        width = size * scale
        height = size * scale
        colors = self._palette()

        gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        gradient_draw = ImageDraw.Draw(gradient)
        for x_pos in range(width):
            ratio = x_pos / max(1, width - 1)
            r, g, b = self._blend_color(colors["logo_start"], colors["logo_end"], ratio)
            gradient_draw.line((x_pos, 0, x_pos, height), fill=(r, g, b, 255))

        mask = Image.new("L", (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        radius = int(width * 0.22)
        mask_draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=255)

        logo = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        logo.paste(gradient, (0, 0), mask)

        draw = ImageDraw.Draw(logo)
        wave_color = colors["logo_wave"]
        wave_points = [
            (0, int(height * 0.60)),
            (int(width * 0.16), int(height * 0.60)),
            (int(width * 0.24), int(height * 0.60)),
            (int(width * 0.28), int(height * 0.84)),
            (int(width * 0.33), int(height * 0.18)),
            (int(width * 0.40), int(height * 0.70)),
            (int(width * 0.47), int(height * 0.44)),
            (int(width * 0.54), int(height * 0.59)),
            (int(width * 0.61), int(height * 0.36)),
            (int(width * 0.69), int(height * 0.84)),
            (int(width * 0.75), int(height * 0.60)),
            (width, int(height * 0.60)),
        ]
        draw.line(wave_points, fill=wave_color, width=int(width * 0.10), joint="curve")
        draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, outline=(255, 255, 255, 28), width=2)
        return logo.resize((size, size), Image.Resampling.LANCZOS)

    def _apply_logo(self) -> None:
        cached = self.logo_cache.get(self.current_theme)
        if cached is None:
            logo_small = self._create_logo_pil(58)
            logo_image = ctk.CTkImage(light_image=logo_small, dark_image=logo_small, size=(58, 58))
            try:
                window_icon = ImageTk.PhotoImage(self._create_logo_pil(96))
            except Exception:
                window_icon = None
            cached = (logo_image, window_icon)
            self.logo_cache[self.current_theme] = cached

        self.logo_image, self.window_icon = cached
        self.logo_label.configure(image=self.logo_image)
        if self.window_icon is not None:
            try:
                self.root.iconphoto(False, self.window_icon)
            except Exception:
                pass

    def _set_status_message(self, key: str | None = None, raw: str | None = None) -> None:
        self.status_message_key = key
        self.status_message_raw = raw
        self.status_var.set(self.t(key) if key else raw or "")

    def _set_progress_message(self, key: str | None = None, raw: str | None = None) -> None:
        self.progress_message_key = key
        self.progress_message_raw = raw
        self.progress_text.configure(text=self.t(key) if key else raw or "")

    def _set_language(self, language: str) -> None:
        if language == self.current_language:
            return
        self.current_language = language
        self._apply_language()

    def _on_language_toggle(self, value: str) -> None:
        self._set_language("it" if value == "IT" else "en")

    def _set_theme(self, theme: str) -> None:
        if theme == self.current_theme:
            return
        self.current_theme = theme
        self._apply_theme(refresh_library=True)

    def _on_theme_toggle(self, value: str) -> None:
        self._set_theme("light" if value == "☀" else "dark")

    def _apply_language(self) -> None:
        active_library = self.tabview.get() == self.tab_name_library
        new_download = self.t("tab_download")
        new_library = self.t("tab_library")
        if new_download != self.tab_name_download:
            self.tabview.rename(self.tab_name_download, new_download)
            self.tab_name_download = new_download
        if new_library != self.tab_name_library:
            self.tabview.rename(self.tab_name_library, new_library)
            self.tab_name_library = new_library
        self.tabview.set(self.tab_name_library if active_library else self.tab_name_download)

        self.subtitle_label.configure(text=self.t("subtitle"))
        self.promo_title_label.configure(text=self.t("promo_title"))
        self.new_badge.configure(text=self.t("new"))
        self.promo_text_label.configure(text=self.t("promo_text"))
        self.promo_button.configure(text=self.t("promo_button"))
        self.link_label.configure(text=self.t("link"))
        self.url_entry.configure(placeholder_text=self.t("placeholder_url"))
        self.paste_button.configure(text=self.t("paste"))
        self.type_label.configure(text=self.t("type"))
        self.video_radio.configure(text=self.t("video"))
        self.audio_radio.configure(text=self.t("audio_only"))
        self.audio_label.configure(text=self.t("audio"))
        self.save_label.configure(text=self.t("save_in"))
        self.browse_button.configure(text=self.t("browse"))
        self.download_button.configure(text=self.t("download_now"))
        self.library_title_label.configure(text=self.t("library_title"))
        self.open_folder_button.configure(text=self.t("open_folder"))
        self.refresh_button.configure(text=self.t("refresh"))
        self._set_status_message(self.status_message_key, self.status_message_raw)
        self._set_progress_message(self.progress_message_key, self.progress_message_raw)
        self._update_switches(self._palette())
        self._update_library_texts()

    def _update_switches(self, colors: dict[str, str]) -> None:
        self.language_toggle.configure(
            fg_color=colors["switch_shell"],
            selected_color=colors["switch_selected"],
            selected_hover_color=colors["switch_selected"],
            unselected_color=colors["switch_shell"],
            unselected_hover_color=colors["switch_shell_hover"],
            text_color=colors["switch_selected_text"],
            text_color_disabled=colors["switch_selected_text"],
            border_width=1,
        )
        self.theme_toggle.configure(
            fg_color=colors["switch_shell"],
            selected_color=colors["switch_selected"],
            selected_hover_color=colors["switch_selected"],
            unselected_color=colors["switch_shell"],
            unselected_hover_color=colors["switch_shell_hover"],
            text_color=colors["switch_selected_text"],
            text_color_disabled=colors["switch_selected_text"],
            border_width=1,
        )
        self.language_toggle.set("IT" if self.current_language == "it" else "EN")
        self.theme_toggle.set("☀" if self.current_theme == "light" else "☾")
        self._sync_segmented_text_colors(
            self.language_toggle,
            self.language_toggle.get(),
            colors["switch_selected_text"],
            colors["switch_unselected_text"],
            colors["switch_border"],
        )
        self._sync_segmented_text_colors(
            self.theme_toggle,
            self.theme_toggle.get(),
            colors["switch_selected_text"],
            colors["switch_unselected_text"],
            colors["switch_border"],
        )

    def _sync_segmented_text_colors(
        self,
        segmented: ctk.CTkSegmentedButton,
        active_value: str,
        active_text_color: str,
        inactive_text_color: str,
        border_color: str,
    ) -> None:
        buttons = getattr(segmented, "_buttons_dict", {})
        for value, button in buttons.items():
            button.configure(
                text_color=active_text_color if value == active_value else inactive_text_color,
                border_color=border_color,
                border_width=1,
            )

    def _apply_theme(self, refresh_library: bool) -> None:
        ctk.set_appearance_mode(self.current_theme)
        colors = self._palette()

        self.container.configure(fg_color=colors["app_bg"])
        self.main_card.configure(fg_color=colors["surface"], border_color=colors["border"])
        self.header.configure(fg_color=colors["header"])
        self.title_label.configure(text_color=colors["text"])
        self.subtitle_label.configure(text_color=colors["muted"])
        self.promo_card.configure(fg_color=colors["promo"], border_color=colors["promo_border"])
        self.promo_title_label.configure(text_color=colors["text"])
        self.new_badge.configure(text_color=colors["badge_text"], fg_color=colors["badge_bg"])
        self.promo_text_label.configure(text_color=colors["muted"])
        self.telegram_label.configure(text_color=colors["badge_bg"])
        self.promo_button.configure(
            fg_color=colors["accent"],
            hover_color=colors["accent_hover"],
            text_color=colors["accent_text"],
        )
        self.controls_card.configure(fg_color=colors["card"], border_color=colors["border"])
        self.link_label.configure(text_color=colors["text"])
        self.type_label.configure(text_color=colors["text"])
        self.audio_label.configure(text_color=colors["text"])
        self.save_label.configure(text_color=colors["text"])
        self.url_entry.configure(fg_color=colors["input"], border_color=colors["border"], text_color=colors["text"])
        self.output_entry.configure(fg_color=colors["input"], border_color=colors["border"], text_color=colors["text"])
        self.paste_button.configure(
            fg_color=colors["secondary"],
            hover_color=colors["secondary_hover"],
            text_color=colors["secondary_text"],
        )
        self.browse_button.configure(
            fg_color=colors["secondary"],
            hover_color=colors["secondary_hover"],
            text_color=colors["secondary_text"],
        )
        self.video_radio.configure(
            text_color=colors["text"],
            fg_color=colors["accent"],
            hover_color=colors["accent_hover"],
            border_color=colors["muted"],
        )
        self.audio_radio.configure(
            text_color=colors["text"],
            fg_color=colors["accent"],
            hover_color=colors["accent_hover"],
            border_color=colors["muted"],
        )
        self.audio_combo.configure(
            fg_color=colors["secondary"],
            button_color=colors["tab_button_unselected"],
            button_hover_color=colors["secondary_hover"],
            text_color=colors["secondary_text"],
        )
        self.download_button.configure(
            fg_color=colors["accent"],
            hover_color=colors["accent_hover"],
            text_color=colors["accent_text"],
        )
        self.status_label.configure(text_color=colors["accent"])
        self.progress.configure(fg_color=colors["progress_bg"], progress_color=colors["accent"])
        self.progress_text.configure(text_color=colors["muted"])
        self.library_header.configure(fg_color=colors["card"], border_color=colors["border"])
        self.library_title_label.configure(text_color=colors["text"])
        self.library_stats_label.configure(text_color=colors["muted"])
        self.open_folder_button.configure(
            fg_color=colors["secondary"],
            hover_color=colors["secondary_hover"],
            text_color=colors["secondary_text"],
        )
        self.refresh_button.configure(
            fg_color=colors["secondary"],
            hover_color=colors["secondary_hover"],
            text_color=colors["secondary_text"],
        )
        self.library_frame.configure(
            fg_color=colors["card"],
            border_color=colors["border"],
            scrollbar_button_color=colors["secondary"],
            scrollbar_button_hover_color=colors["secondary_hover"],
        )
        self.tabview.configure(
            fg_color=colors["tab_fg"],
            segmented_button_fg_color=colors["tab_button_fg"],
            segmented_button_selected_color=colors["accent"],
            segmented_button_selected_hover_color=colors["accent_hover"],
            segmented_button_unselected_color=colors["tab_button_unselected"],
            segmented_button_unselected_hover_color=colors["tab_button_hover"],
            text_color=colors["text"],
        )
        self._update_switches(colors)
        self._apply_logo()
        if refresh_library:
            self._restyle_library_rows()

    def _paste_link(self) -> None:
        try:
            clipboard = self.root.clipboard_get().strip()
        except Exception:
            return
        if clipboard:
            self.url_var.set(clipboard)

    def _open_telegram(self) -> None:
        webbrowser.open("https://t.me/mrnobody4444")

    def _open_with_system(self, target: Path) -> None:
        if not target.exists():
            return
        if os.name == "nt":
            os.startfile(target)  # type: ignore[attr-defined]
            return
        if sys.platform == "darwin":
            subprocess.Popen(["open", str(target)])
            return
        subprocess.Popen(["xdg-open", str(target)])

    def _open_output_folder(self) -> None:
        target = Path(self.output_var.get().strip() or "downloads").expanduser()
        target.mkdir(parents=True, exist_ok=True)
        self._open_with_system(target)

    def _format_size(self, size_bytes: int) -> str:
        units = ["B", "KB", "MB", "GB"]
        value = float(size_bytes)
        for unit in units:
            if value < 1024 or unit == units[-1]:
                return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
            value /= 1024
        return f"{size_bytes} B"

    def _clear_library(self) -> None:
        self.library_rows = []
        self.library_empty_label = None
        for child in self.library_frame.winfo_children():
            child.destroy()

    def _update_library_summary(self) -> None:
        self.library_stats_var.set(
            f"{self.library_count} {self.t('downloads_label')} • {self._format_size(self.library_total_size)} • {self.t('folder_label')} {self.library_folder}"
        )

    def _update_library_texts(self) -> None:
        self._update_library_summary()
        if self.library_empty_label is not None:
            self.library_empty_label.configure(text=self.t("library_empty"))
            return
        for row_data in self.library_rows:
            row_data["open_button"].configure(text=self.t("open"))
            row_data["folder_button"].configure(text=self.t("folder"))

    def _restyle_library_rows(self) -> None:
        colors = self._palette()
        if self.library_empty_label is not None:
            self.library_empty_label.configure(text_color=colors["muted"])
            return
        for row_data in self.library_rows:
            row_data["row"].configure(fg_color=colors["surface"], border_color=colors["border"])
            row_data["title_label"].configure(text_color=colors["text"])
            row_data["meta_label"].configure(text_color=colors["muted"])
            row_data["open_button"].configure(
                fg_color=colors["accent"],
                hover_color=colors["accent_hover"],
                text_color=colors["accent_text"],
            )
            row_data["folder_button"].configure(
                fg_color=colors["secondary"],
                hover_color=colors["secondary_hover"],
                text_color=colors["secondary_text"],
            )

    def _bind_scroll_recursive(self, widget) -> None:
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            widget.bind(sequence, self._on_library_scroll, add="+")
        for child in widget.winfo_children():
            self._bind_scroll_recursive(child)

    def _on_library_scroll(self, event):
        if self.tabview.get() != self.tab_name_library:
            return None
        canvas = getattr(self.library_frame, "_parent_canvas", None)
        if canvas is None:
            return None
        if getattr(event, "num", None) == 4:
            canvas.yview_scroll(-1, "units")
            return "break"
        if getattr(event, "num", None) == 5:
            canvas.yview_scroll(1, "units")
            return "break"
        delta = getattr(event, "delta", 0)
        if delta:
            steps = max(1, int(abs(delta) / 120))
            direction = -1 if delta > 0 else 1
            canvas.yview_scroll(direction * steps, "units")
            return "break"
        return None

    def _refresh_library(self) -> None:
        folder = Path(self.output_var.get().strip() or "downloads").expanduser()
        folder.mkdir(parents=True, exist_ok=True)
        media_files = sorted(
            [
                path for path in folder.iterdir()
                if path.is_file() and path.suffix.lower() in {".mp4", ".mkv", ".webm", ".mp3", ".m4a", ".wav", ".flac", ".opus"}
            ],
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        self.library_folder = folder
        self.library_count = len(media_files)
        self.library_total_size = sum(path.stat().st_size for path in media_files)
        self._update_library_summary()
        self._clear_library()

        colors = self._palette()
        if not media_files:
            self.library_empty_label = ctk.CTkLabel(
                self.library_frame,
                text=self.t("library_empty"),
                font=self.font_body,
                text_color=colors["muted"],
            )
            self.library_empty_label.pack(anchor="w", padx=12, pady=12)
            self._bind_scroll_recursive(self.library_frame)
            return

        for index, media_file in enumerate(media_files, start=1):
            row = ctk.CTkFrame(
                self.library_frame,
                fg_color=colors["surface"],
                corner_radius=12,
                border_width=1,
                border_color=colors["border"],
            )
            row.pack(fill="x", padx=10, pady=6)

            left = ctk.CTkFrame(row, fg_color="transparent")
            left.pack(side="left", fill="both", expand=True, padx=12, pady=12)
            ext = media_file.suffix.lower().replace(".", "").upper()
            title_label = ctk.CTkLabel(
                left,
                text=f"#{index}  {media_file.stem}",
                font=self.font_label,
                text_color=colors["text"],
                anchor="w",
            )
            title_label.pack(anchor="w")
            meta = f"{ext} • {self._format_size(media_file.stat().st_size)} • {datetime.fromtimestamp(media_file.stat().st_mtime).strftime('%d/%m/%Y %H:%M')}"
            meta_label = ctk.CTkLabel(
                left,
                text=meta,
                font=self.font_body,
                text_color=colors["muted"],
                anchor="w",
            )
            meta_label.pack(anchor="w", pady=(4, 0))

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.pack(side="right", padx=12, pady=12)
            open_button = ctk.CTkButton(
                actions,
                text=self.t("open"),
                command=lambda path=media_file: self._open_with_system(path),
                height=36,
                width=90,
                corner_radius=12,
                fg_color=colors["accent"],
                hover_color=colors["accent_hover"],
                text_color=colors["accent_text"],
                font=self.font_button,
            )
            open_button.pack(side="left")
            folder_button = ctk.CTkButton(
                actions,
                text=self.t("folder"),
                command=self._open_output_folder,
                height=36,
                width=100,
                corner_radius=12,
                fg_color=colors["secondary"],
                hover_color=colors["secondary_hover"],
                text_color=colors["secondary_text"],
                font=self.font_button,
            )
            folder_button.pack(side="left", padx=(8, 0))

            self.library_rows.append(
                {
                    "row": row,
                    "title_label": title_label,
                    "meta_label": meta_label,
                    "open_button": open_button,
                    "folder_button": folder_button,
                }
            )

        self._bind_scroll_recursive(self.library_frame)

    def _toggle_audio_controls(self) -> None:
        self.audio_combo.configure(state="normal" if self.mode_var.get() == "audio" else "disabled")

    def _choose_output(self) -> None:
        initial_dir = self.output_var.get().strip() or str(Path.home())
        if not Path(initial_dir).exists():
            initial_dir = str(Path.home())
        selected = filedialog.askdirectory(
            parent=self.root,
            title=self.t("choose_folder"),
            initialdir=initial_dir,
            mustexist=False,
        )
        self.root.lift()
        self.root.focus_force()
        if selected:
            self.output_var.set(selected)
            self._refresh_library()

    def _on_progress_update(self, value: float, text: str) -> None:
        self.progress.set(max(0.0, min(1.0, value)))
        if text:
            self._set_progress_message(raw=text)
        else:
            self._set_progress_message(raw=f"{int(value * 100)}%")

    def _on_status_update(self, text: str) -> None:
        self._set_progress_message(raw=text)

    def _start_download(self) -> None:
        if self.is_downloading:
            return
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Streamly", self.t("missing_url"))
            return

        output_dir = Path(self.output_var.get().strip() or "downloads").expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        self._refresh_library()

        self.is_downloading = True
        self.download_button.configure(state="disabled")
        self._set_status_message("download_start")
        self._set_progress_message("connecting")
        self.progress.set(0)

        thread = threading.Thread(
            target=self._run_download,
            args=(url, self.mode_var.get(), self.audio_format_var.get(), str(output_dir)),
            daemon=True,
        )
        thread.start()

    def _run_download(self, url: str, mode: str, audio_format: str, output: str) -> None:
        try:
            code = download_url(
                url=url,
                mode=mode,
                audio_format=audio_format,
                audio_quality="0",
                output=output,
                cookies_from_browser="",
                log_callback=None,
                progress_callback=lambda pct, msg: self.root.after(0, self._on_progress_update, pct, msg),
            )
            self.root.after(0, self._finish_download, code)
        except Exception as exc:  # pragma: no cover
            self.root.after(0, self._on_status_update, f"{self.t('error')}: {exc}")
            self.root.after(0, self._finish_download, 1)

    def _finish_download(self, code: int) -> None:
        self.download_button.configure(state="normal")
        self.is_downloading = False
        if code == 0:
            self._set_status_message("completed")
            self.progress.set(1.0)
            self._set_progress_message("completed_text")
            self._refresh_library()
            messagebox.showinfo("Streamly", self.t("download_done_msg"))
        else:
            self._set_status_message("error")
            self._set_progress_message("failed")
            messagebox.showerror("Streamly", self.t("download_error_msg"))


def main() -> None:
    root = ctk.CTk()
    app = StreamlyGUI(root)
    app.url_entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()
