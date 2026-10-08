$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$reportDir = Join-Path $projectRoot 'report'
$env:LC_ALL = 'C'
Push-Location -LiteralPath $reportDir
try {
  & latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
  if ($LASTEXITCODE -ne 0) { throw "latexmk failed: $LASTEXITCODE" }
  $bad = Select-String -LiteralPath 'main.log' -Pattern '^!','Undefined control sequence','LaTeX Warning:.*undefined','There were undefined references','Missing character:','Overfull \\hbox','Overfull \\vbox'
  if ($bad) { $bad | ForEach-Object { Write-Warning $_.Line }; throw 'Report log requires inspection.' }
  Write-Host (Join-Path $reportDir 'main.pdf')
} finally { Pop-Location }
