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

# 두 스크립트를 같은 프로세스에서 부른다. `powershell -File` 로 띄우면 테마마다
# 프로세스가 둘 더 생기는데, 열두 개가 동시에 뜨는 자리라 하나에 0.75초가 든다 —
# 재 보니 iOS 쪽 시간의 76% 가 프로세스 생성이었고 실제 zip 작업은 23% 였다.
# 293벌이면 양쪽 합쳐 442초 CPU 다.
#
# `&` 는 점 소싱(`.`)과 달리 제 스코프에서 돌아서 변수가 섞이지 않는다. 대신
# 종료코드 대신 예외가 올라오므로 try 로 받는다 — 두 스크립트 모두 실패는 throw 다.
try {
    & (Join-Path $root 'build-ios.ps1') `
        -Source (Join-Path $Theme 'ios') `
        -Out (Join-Path $Dist "iOS\$key.ktheme")
} catch {
    Write-Host "  실패: iOS - $_"
    exit 1
}

try {
    & (Join-Path $root 'build-android.ps1') `
        -Source (Join-Path $Theme 'android') `
        -Out (Join-Path $Dist "android\$key.apk")
} catch {
    Write-Host "  실패: Android - $_"
    exit 1
}

exit 0
