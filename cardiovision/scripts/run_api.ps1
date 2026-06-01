# Windows: start CardioVision API
Set-Location $PSScriptRoot\..
$env:PYTHONPATH = (Get-Location).Path
if (-not (Test-Path "ml_models\trained\heart_disease_model.pkl")) {
    py -3 scripts/train_model.py
}
py -3 -m uvicorn backend.main:app --reload --port 8000
