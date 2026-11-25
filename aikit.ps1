# Wrapper: chama aikit.py com o Python disponivel.
$py = Get-Command python, python3, py -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $py) { Write-Error "Python 3 nao encontrado. Instale com: winget install Python.Python.3.12"; exit 1 }
& $py.Source "$PSScriptRoot\aikit.py" @args
exit $LASTEXITCODE
