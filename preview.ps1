# 테마 미리보기를 만들고 브라우저로 연다.
#   powershell -ExecutionPolicy Bypass -File preview.ps1
#
# 폰에 하나씩 적용해보지 않고 색을 확인하려고 만든 것이다.
#
# 테마 조각을 주면 그 몇 벌만 다시 그린다. 292벌을 다 그리면 7분 35초가 걸려서,
# 색 하나 고쳐 보는 데 그걸 매번 기다리게 된다. 페이지에는 늘 전부가 담긴다.
#   powershell -ExecutionPolicy Bypass -File preview.ps1 neonlounge
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Themes)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

& python (Join-Path $root tools\gen.py) @Themes
if ($LASTEXITCODE -ne 0) { throw "생성 실패" }

$page = Join-Path $root docs\index.html
Write-Host ""
Write-Host "여는 중: $page"
Start-Process $page
