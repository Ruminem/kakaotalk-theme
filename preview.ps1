# 테마 미리보기를 만들고 브라우저로 연다.
#   powershell -ExecutionPolicy Bypass -File preview.ps1
#
# 폰에 하나씩 적용해보지 않고 색을 확인하려고 만든 것이다.

$ErrorActionPreference = Stop
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

& python (Join-Path $root tools\gen.py)
if ($LASTEXITCODE -ne 0) { throw "생성 실패" }

$page = Join-Path $root docs\index.html
Write-Host ""
Write-Host "여는 중: $page"
Start-Process $page
