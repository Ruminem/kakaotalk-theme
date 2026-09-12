# iOS 와 안드로이드를 한 번에 빌드한다. 배포는 항상 이걸로 한다.
#   powershell -ExecutionPolicy Bypass -File build.ps1
# 결과: dist\iOS\inkmint01.ktheme, dist\android\inkmint01.apk

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$failed = @()
foreach ($s in @('build-ios.ps1', 'build-android.ps1')) {
    Write-Host ""
    Write-Host "===== $s ====="
    & powershell -ExecutionPolicy Bypass -File (Join-Path $root $s)
    if ($LASTEXITCODE -ne 0) { $failed += $s }
}

Write-Host ""
Write-Host "===== 결과 ====="
Get-ChildItem (Join-Path $root 'dist') -Recurse -File |
    ForEach-Object { "{0,-40} {1,8:N1} KB" -f $_.FullName.Substring($root.Length + 1), ($_.Length / 1KB) }

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "실패: $($failed -join ', ')"
    exit 1
}
