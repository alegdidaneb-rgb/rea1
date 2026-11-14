param(
    [string]$AnalysisRoot = "$HOME\REA-Targets",
    [string]$Model = "qwen2.5-coder:7b"
)
$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $AnalysisRoot)) {
    New-Item -ItemType Directory -Path $AnalysisRoot | Out-Null
}
python "$PSScriptRoot\server.py" --analysis-root "$AnalysisRoot" --model "$Model"
