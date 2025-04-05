Write-Host "🚀 TravelBot Setup Script (Windows PowerShell)" -ForegroundColor Cyan

python -m venv .venv
Write-Host "👉 Activate the virtual environment before continuing:" -ForegroundColor Green
Write-Host ".\.venv\Scripts\Activate.ps1" -ForegroundColor Green
Pause

pip install --upgrade pip
pip install -r requirements.txt

Write-Host ""
Write-Host "Choose the mode:"
Write-Host "1. Local (Ollama)"
Write-Host "2. Codespaces / Hugging Face"
$choice = Read-Host "Enter 1 or 2"

$appPath = "app.py"
$ingestPath = "ingest.py"
$appText = Get-Content $appPath
$ingestText = Get-Content $ingestPath

if ($choice -eq "1") {
    if (!(Get-Command ollama -ErrorAction SilentlyContinue)) {
        Write-Host "⚠️ Ollama not found. Get it from https://ollama.com" -ForegroundColor Red
    } else {
        ollama pull tinyllama
        $appText = $appText -replace 'USE_OLLAMA = False', 'USE_OLLAMA = True'
        $ingestText = $ingestText -replace 'USE_OLLAMA = False', 'USE_OLLAMA = True'
    }
}
elseif ($choice -eq "2") {
    $appText = $appText -replace 'USE_OLLAMA = True', 'USE_OLLAMA = False'
    $ingestText = $ingestText -replace 'USE_OLLAMA = True', 'USE_OLLAMA = False'
} else {
    Write-Host "❌ Invalid choice. Please update manually." -ForegroundColor Red
}

Set-Content $appPath $appText
Set-Content $ingestPath $ingestText

Write-Host "🧠 Running ingestion..." -ForegroundColor Yellow
python ingest.py

Write-Host "✅ Setup complete. Run with: python app.py" -ForegroundColor Cyan
