# 테마 하나를 iOS 와 안드로이드 양쪽으로 빌드한다.
#   powershell -ExecutionPolicy Bypass -File build-one.ps1 -Theme build-src\red-glow -Dist dist
#
# 보통은 직접 부르지 않는다. build.ps1 이 테마마다 이걸 띄운다 — 여러 개를 동시에
# 띄우려고 한 벌을 한 프로세스에 담은 것이다. 한쪽만 확인할 때는
# build-ios.ps1 / build-android.ps1 을 직접 부른다.

param(
    [Parameter(Mandatory = $true)][string]$Theme,
    [Parameter(Mandatory = $true)][string]$Dist
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$key = Split-Path -Leaf $Theme

Write-Host "===== $key ====="

& powershell -ExecutionPolicy Bypass -File (Join-Path $root 'build-ios.ps1') `
    -Source (Join-Path $Theme 'ios') `
    -Out (Join-Path $Dist "iOS\$key.ktheme")
if ($LASTEXITCODE -ne 0) { Write-Host "  실패: iOS"; exit 1 }

& powershell -ExecutionPolicy Bypass -File (Join-Path $root 'build-android.ps1') `
    -Source (Join-Path $Theme 'android') `
    -Out (Join-Path $Dist "android\$key.apk")
if ($LASTEXITCODE -ne 0) { Write-Host "  실패: Android"; exit 1 }

exit 0
