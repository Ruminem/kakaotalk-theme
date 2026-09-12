# android 폴더를 카카오톡 테마 APK 로 빌드한다.
#   powershell -ExecutionPolicy Bypass -File build-android.ps1
# 결과: dist\android\inkmint01.apk
#
# gradle 을 쓰지 않는다. 코드가 없는 리소스 전용 APK 라서
# aapt2 → zipalign → apksigner 세 단계면 끝난다.

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$src  = Join-Path $root 'android'
$work = Join-Path $root 'build-tmp'
$dist = Join-Path $root 'dist\android'
$out  = Join-Path $dist 'inkmint01.apk'
$ks   = Join-Path $root 'theme.keystore'
$ksPass = 'inkmint'

# --- SDK 찾기 ---
$sdk = $env:ANDROID_SDK_ROOT
if (-not $sdk) { $sdk = $env:ANDROID_HOME }
if (-not $sdk) { $sdk = Join-Path $env:LOCALAPPDATA 'Android\Sdk' }
if (-not (Test-Path $sdk)) { throw "안드로이드 SDK 를 못 찾았습니다: $sdk" }

$bt = (Get-ChildItem (Join-Path $sdk 'build-tools') -Directory | Sort-Object { [version]$_.Name } -Descending | Select-Object -First 1).FullName
$platform = (Get-ChildItem (Join-Path $sdk 'platforms') -Directory | Sort-Object Name -Descending | Select-Object -First 1).FullName
$androidJar = Join-Path $platform 'android.jar'

$aapt2     = Join-Path $bt 'aapt2.exe'
$zipalign  = Join-Path $bt 'zipalign.exe'
$apksigner = Join-Path $bt 'apksigner.bat'
foreach ($t in @($aapt2, $zipalign, $apksigner, $androidJar)) {
    if (-not (Test-Path $t)) { throw "필요한 도구가 없습니다: $t" }
}
Write-Host "build-tools : $(Split-Path -Leaf $bt)"
Write-Host "platform    : $(Split-Path -Leaf $platform)"

# --- 서명 키 ---
# 없으면 만든다. 이 키를 잃어버리면 같은 패키지의 새 버전을 덮어 설치할 수 없다.
# (서명이 다르면 안드로이드가 거부한다. 그때는 폰에서 기존 테마를 지우고 새로 깔면 된다)
if (-not (Test-Path $ks)) {
    $keytool = Get-Command keytool -ErrorAction SilentlyContinue
    if ($keytool) { $keytool = $keytool.Source }
    else {
        $cand = "C:\Program Files\Android\Android Studio\jbr\bin\keytool.exe"
        if (Test-Path $cand) { $keytool = $cand } else { throw "keytool 을 못 찾았습니다." }
    }
    Write-Host "서명 키를 새로 만듭니다: $(Split-Path -Leaf $ks)"
    & $keytool -genkeypair -v -keystore $ks -alias theme -keyalg RSA -keysize 2048 `
        -validity 10000 -storepass $ksPass -keypass $ksPass -dname "CN=inkmint, O=hobby, C=KR" | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "키 생성 실패" }
}

# --- 빌드 ---
if (Test-Path $work) { Remove-Item $work -Recurse -Force }
New-Item -ItemType Directory -Path $work -Force | Out-Null
if (-not (Test-Path $dist)) { New-Item -ItemType Directory -Path $dist -Force | Out-Null }

$resZip = Join-Path $work 'res.zip'
& $aapt2 compile --dir (Join-Path $src 'res') -o $resZip
if ($LASTEXITCODE -ne 0) { throw "aapt2 compile 실패" }

$unsigned = Join-Path $work 'unsigned.apk'
& $aapt2 link -o $unsigned -I $androidJar --manifest (Join-Path $src 'AndroidManifest.xml') $resZip
if ($LASTEXITCODE -ne 0) { throw "aapt2 link 실패" }

$aligned = Join-Path $work 'aligned.apk'
& $zipalign -f -p 4 $unsigned $aligned
if ($LASTEXITCODE -ne 0) { throw "zipalign 실패" }

if (Test-Path $out) { Remove-Item $out -Force }
# v4 서명(--v4-signing-enabled)은 adb 증분설치용이라 끈다. 켜두면 .idsig 가 같이 나온다.
& $apksigner sign --ks $ks --ks-pass "pass:$ksPass" --key-pass "pass:$ksPass" `
    --v4-signing-enabled false --out $out $aligned
if ($LASTEXITCODE -ne 0) { throw "apksigner 실패" }

& $apksigner verify $out
if ($LASTEXITCODE -ne 0) { throw "서명 검증 실패" }

Remove-Item $work -Recurse -Force

$colors = ([regex]'<color ').Matches((Get-Content (Join-Path $src 'res\values\colors.xml') -Raw)).Count
$kb = [math]::Round((Get-Item $out).Length / 1KB, 1)
Write-Host ""
Write-Host "색상       : $colors 개"
Write-Host "완료: $out  ($kb KB)"
Write-Host "폰으로 옮겨 설치한 뒤 카톡 더보기 > 설정 > 테마 설정 에서 선택하세요."
