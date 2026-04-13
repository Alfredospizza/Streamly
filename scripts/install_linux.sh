#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.local/opt/Streamly"
BIN_DIR="${HOME}/.local/bin"
APPLICATIONS_DIR="${HOME}/.local/share/applications"
APP_LINK="${BIN_DIR}/streamly-gui"
DESKTOP_FILE_NAME="streamly.desktop"
APPLICATIONS_LAUNCHER="${APPLICATIONS_DIR}/${DESKTOP_FILE_NAME}"

if command -v xdg-user-dir >/dev/null 2>&1; then
	DESKTOP_DIR="$(xdg-user-dir DESKTOP)"
else
	DESKTOP_DIR="${HOME}/Desktop"
fi

if [[ -z "${DESKTOP_DIR}" ]]; then
	DESKTOP_DIR="${HOME}/Desktop"
fi

DESKTOP_LAUNCHER="${DESKTOP_DIR}/${DESKTOP_FILE_NAME}"
ICON_PATH="${TARGET_DIR}/assets/streamly.svg"

mkdir -p "$TARGET_DIR" "$BIN_DIR" "$APPLICATIONS_DIR"

rsync -a --delete --exclude "downloads" "$SOURCE_DIR"/ "$TARGET_DIR"/

cat > "$APP_LINK" <<'EOF'
#!/usr/bin/env bash
exec "$HOME/.local/opt/Streamly/Streamly" "$@"
EOF

chmod +x "$APP_LINK"

cat > "$APPLICATIONS_LAUNCHER" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Streamly
Comment=Download video or audio with Streamly
Exec=${APP_LINK}
Icon=${ICON_PATH}
Terminal=false
Categories=AudioVideo;Utility;
StartupNotify=true
EOF

chmod +x "$APPLICATIONS_LAUNCHER"

if [[ -d "$DESKTOP_DIR" ]]; then
	cp "$APPLICATIONS_LAUNCHER" "$DESKTOP_LAUNCHER"
	chmod +x "$DESKTOP_LAUNCHER"
fi

echo "Installazione completata."
echo "Avvio rapido: streamly-gui"
echo "Launcher applicazioni: $APPLICATIONS_LAUNCHER"
if [[ -d "$DESKTOP_DIR" ]]; then
	echo "Icona desktop creata in: $DESKTOP_LAUNCHER"
fi
echo "Se il comando non viene trovato, aggiungi ~/.local/bin al PATH."
