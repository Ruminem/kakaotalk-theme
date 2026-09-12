# 모든 테마를 iOS 와 안드로이드 양쪽으로 빌드한다. 배포는 항상 이걸로 한다.
#   powershell -ExecutionPolicy Bypass -File build.ps1
# 결과: dist\iOS\<테마>.ktheme, dist\android\<테마>.apk

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# 소스는 팔레트 표에서 생성된다. 원본은 tools/themes.py 하나뿐이다.
Write-Host "tools/gen.py 로 소스를 만듭니다"
& python (Join-Path $root 'tools\gen.py')
if ($LASTEXITCODE -ne 0) { throw "소스 생성 실패" }

$src = Join-Path $root 'build-src'
$dist = Join-Path $root 'dist'
if (Test-Path $dist) { Remove-Item $dist -Recurse -Force }

$failed = @()
foreach ($theme in Get-ChildItem $src -Directory | Sort-Object Name) {
    $key = $theme.Name
    Write-Host ""
    Write-Host "===== $key ====="
    try {
        & powershell -ExecutionPolicy Bypass -File (Join-Path $root 'build-ios.ps1') `
            -Source (Join-Path $theme.FullName 'ios') `
            -Out (Join-Path $dist "iOS\$key.ktheme")
        if ($LASTEXITCODE -ne 0) { throw "iOS 실패" }

        & powershell -ExecutionPolicy Bypass -File (Join-Path $root 'build-android.ps1') `
            -Source (Join-Path $theme.FullName 'android') `
            -Out (Join-Path $dist "android\$key.apk")
        if ($LASTEXITCODE -ne 0) { throw "Android 실패" }
    } catch {
        Write-Host "  실패: $_"
        $failed += $key
    }
}

if (Test-Path (Join-Path $root 'build-tmp')) {
    Remove-Item (Join-Path $root 'build-tmp') -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "===== 결과 ====="
Get-ChildItem $dist -Recurse -File | Sort-Object FullName | ForEach-Object {
    "{0,-42} {1,8:N1} KB" -f $_.FullName.Substring($root.Length + 1), ($_.Length / 1KB)
}

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "실패한 테마: $($failed -join ', ')"
    exit 1
}
