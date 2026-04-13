$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

if (Test-Path build) { Remove-Item build -Recurse -Force }
if (Test-Path dist) { Remove-Item dist -Recurse -Force }
if (Test-Path release) { Remove-Item release -Recurse -Force }
New-Item -ItemType Directory -Force -Path release | Out-Null

python -m pip install -r requirements-build.txt

pyinstaller --noconfirm --clean --name Streamly --windowed --onedir --hidden-import PIL.ImageTk --hidden-import PIL._tkinter_finder --hidden-import PIL._imagingtk streamly_gui.py

New-Item -ItemType Directory -Force -Path dist/Streamly/tools/windows | Out-Null

if (Get-Command ffmpeg.exe -ErrorAction SilentlyContinue) {
  Copy-Item (Get-Command ffmpeg.exe).Source dist/Streamly/tools/windows/ -Force
}
if (Get-Command ffprobe.exe -ErrorAction SilentlyContinue) {
  Copy-Item (Get-Command ffprobe.exe).Source dist/Streamly/tools/windows/ -Force
}

Copy-Item README.md dist/Streamly/ -Force
Copy-Item LICENSE dist/Streamly/ -Force

Compress-Archive -Path dist/Streamly/* -DestinationPath release/Streamly-windows-portable.zip -Force

Write-Host "Build Windows completata. Artifact: release/Streamly-windows-portable.zip"
Write-Host "Per creare installer .exe usa packaging/windows/streamly.iss con Inno Setup."
