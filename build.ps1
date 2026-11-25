$ErrorActionPreference = "Stop"

if (-not (Test-Path .\.venv\Scripts\python.exe)) {
    Write-Error "Primero ejecuta setup.ps1"
    exit 1
}

& .\.venv\Scripts\python.exe -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name "Conversor-Markdown" `
    --collect-all magika `
    --collect-all markitdown `
    --collect-all customtkinter `
    --add-data "assets;assets" `
    app.py

Write-Host "Ejecutable creado en dist\Conversor-Markdown\Conversor-Markdown.exe" -ForegroundColor Green
