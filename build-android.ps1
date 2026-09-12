# 테마 하나를 안드로이드 APK 로 빌드한다.
#   powershell -ExecutionPolicy Bypass -File build-android.ps1 -Source build-src\inkmint01\android -Out dist\android\inkmint01.apk
#
# 보통은 직접 부르지 않는다. build.ps1 이 테마마다 이걸 부른다.
# gradle 을 쓰지 않는다. 코드가 없는 리소스 전용 APK 라서
# aapt2 -> zipalign -> apksigner 세 단계면 끝난다.

param(
    [Parameter(Mandatory = $true)][string]$Source,
    [Parameter(Mandatory = $true)][string]$Out
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ks = Join-Path $root 'theme.keystore'
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

# --- 서명 키 ---
# 없으면 만든다. 이 키를 잃어버리면 같은 패키지의 새 버전을 덮어 설치할 수 없다.
# (서명이 다르면 안드로이드가 거부한다. 그때는 폰에서 지우고 새로 깔면 된다)
if (-not (Test-Path $ks)) {
    $keytool = (Get-Command keytool -ErrorAction SilentlyContinue).Source
    if (-not $keytool) {
        $cand = "C:\Program Files\Android\Android Studio\jbr\bin\keytool.exe"
        if (Test-Path $cand) { $keytool = $cand } else { throw "keytool 을 못 찾았습니다." }
    }
    Write-Host "  서명 키를 새로 만듭니다: theme.keystore"
    & $keytool -genkeypair -v -keystore $ks -alias theme -keyalg RSA -keysize 2048 `
        -validity 10000 -storepass $ksPass -keypass $ksPass -dname "CN=inkmint, O=hobby, C=KR" | Out-Null
}

# --- 빌드 ---
$work = Join-Path $root ('build-tmp\' + (Split-Path -Leaf (Split-Path -Parent $Source)))
if (Test-Path $work) { Remove-Item $work -Recurse -Force }
New-Item -ItemType Directory -Path $work -Force | Out-Null
$dir = Split-Path -Parent $Out
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }

$resZip = Join-Path $work 'res.zip'
& $aapt2 compile --dir (Join-Path $Source 'res') -o $resZip
if ($LASTEXITCODE -ne 0) { throw "aapt2 compile 실패" }

$unsigned = Join-Path $work 'unsigned.apk'
& $aapt2 link -o $unsigned -I $androidJar --manifest (Join-Path $Source 'AndroidManifest.xml') $resZip
if ($LASTEXITCODE -ne 0) { throw "aapt2 link 실패" }

$aligned = Join-Path $work 'aligned.apk'
& $zipalign -f -p 4 $unsigned $aligned
if ($LASTEXITCODE -ne 0) { throw "zipalign 실패" }

if (Test-Path $Out) { Remove-Item $Out -Force }
# v4 서명은 adb 증분설치용이라 끈다. 켜두면 .idsig 가 같이 나온다.
# stderr 를 2>&1 로 받지 않는다. PowerShell 5.1 은 네이티브 exe 의 stderr 를 그렇게 받으면
# 종료코드가 0이어도 NativeCommandError 로 승격시켜 빌드가 실패한 것처럼 보인다.
& $apksigner sign --ks $ks --ks-pass "pass:$ksPass" --key-pass "pass:$ksPass" `
    --v4-signing-enabled false --out $Out $aligned | Out-Null
if ($LASTEXITCODE -ne 0) { throw "apksigner 실패" }

Remove-Item $work -Recurse -Force

$pkg = ([regex]'package="([^"]*)"').Match((Get-Content (Join-Path $Source 'AndroidManifest.xml') -Raw)).Groups[1].Value
$colors = ([regex]'<color ').Matches((Get-Content (Join-Path $Source 'res\values\colors.xml') -Raw)).Count
$kb = [math]::Round((Get-Item $Out).Length / 1KB, 1)
Write-Host ("  Android  {0,-35} 색상 {1,2}개  {2,6:N1} KB" -f $pkg, $colors, $kb)
