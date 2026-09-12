# 릴리스를 만든다. 두 플랫폼을 빌드해서 GitHub 릴리스에 자산으로 붙인다.
#   powershell -ExecutionPolicy Bypass -File release.ps1 -Version 0.1 -NotesFile notes.md
#
# 릴리스 노트는 직접 쓴다. 자동 생성에 맡기지 않는다 —
# main 에 바로 커밋하는 프로젝트라 자동 노트는 링크 한 줄만 남고 비어버린다.

param(
    [Parameter(Mandatory = $true)][string]$Version,
    [Parameter(Mandatory = $true)][string]$NotesFile
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Version = $Version.TrimStart('v')
$tag = "v$Version"

if (-not (Test-Path $NotesFile)) { throw "릴리스 노트 파일이 없습니다: $NotesFile" }

# --- 양쪽 버전이 같은지 먼저 본다 ---
# 한쪽만 올리고 빌드하는 게 이 프로젝트에서 제일 나기 쉬운 실수다.
$css = Get-Content (Join-Path $root 'ios\KakaoTalkTheme.css') -Raw -Encoding UTF8
$iosVer = ([regex]"-kakaotalk-theme-version:\s*'([^']*)'").Match($css).Groups[1].Value
$mf = Get-Content (Join-Path $root 'android\AndroidManifest.xml') -Raw -Encoding UTF8
$aosVer = ([regex]'android:versionName="([^"]*)"').Match($mf).Groups[1].Value

Write-Host "요청 버전   : $Version"
Write-Host "iOS CSS     : $iosVer"
Write-Host "Android     : $aosVer"
if ($iosVer -ne $Version -or $aosVer -ne $Version) {
    throw "버전이 어긋납니다. ios\KakaoTalkTheme.css 와 android\AndroidManifest.xml 을 $Version 로 맞추세요."
}

if (git tag --list $tag) { throw "$tag 태그가 이미 있습니다." }
$dirty = git status --porcelain
if ($dirty) { throw "커밋 안 된 변경이 있습니다. 먼저 정리하세요." }

# --- 빌드 ---
& powershell -ExecutionPolicy Bypass -File (Join-Path $root 'build.ps1')
if ($LASTEXITCODE -ne 0) { throw "빌드 실패" }

# --- 버전 붙인 이름으로 자산 준비 ---
$stage = Join-Path $root 'build-tmp'
New-Item -ItemType Directory -Path $stage -Force | Out-Null
$ktheme = Join-Path $stage "inkmint01-$Version.ktheme"
$apk    = Join-Path $stage "inkmint01-$Version.apk"
Copy-Item (Join-Path $root 'dist\iOS\inkmint01.ktheme')     $ktheme -Force
Copy-Item (Join-Path $root 'dist\android\inkmint01.apk')    $apk    -Force

# --- 태그와 릴리스 ---
git tag -a $tag -m "먹빛 민트 $Version"
if ($LASTEXITCODE -ne 0) { throw "태그 생성 실패" }
git push origin $tag
if ($LASTEXITCODE -ne 0) { throw "태그 푸시 실패" }

gh release create $tag $ktheme $apk --title "먹빛 민트 $Version" --notes-file $NotesFile
if ($LASTEXITCODE -ne 0) { throw "릴리스 생성 실패" }

Remove-Item $stage -Recurse -Force
Write-Host ""
Write-Host "완료: $tag  (iOS .ktheme + Android .apk 첨부)"
