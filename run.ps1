if (-not (Test-Path .\.venv\Scripts\python.exe)) {
    Write-Error "Primero ejecuta setup.ps1"
    exit 1
}
& .\.venv\Scripts\python.exe app.py
