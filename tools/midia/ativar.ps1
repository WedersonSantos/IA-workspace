$root = $PSScriptRoot
if (-not $env:CONTEUDO_DIR) { $env:CONTEUDO_DIR = "F:/AI-Workspace/conteudo" }
& "$root\.venv\Scripts\Activate.ps1"
$env:HF_HOME = "$root\modelos"
$env:TEMP = "$root\.tmp"
$env:TMP = "$root\.tmp"
Write-Host "Ambiente midia ativo (modelos em $env:HF_HOME)"
