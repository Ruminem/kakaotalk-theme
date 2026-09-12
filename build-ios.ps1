# mytheme 폴더를 iOS 용 .ktheme 로 패키징한다.
#   powershell -ExecutionPolicy Bypass -File build-ios.ps1
# 결과: dist\iOS\inkmint01.ktheme

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$src  = Join-Path $root 'mytheme'
$dist = Join-Path $root 'dist\iOS'
$out  = Join-Path $dist 'inkmint01.ktheme'
$css  = Join-Path $src 'KakaoTalkTheme.css'

if (-not (Test-Path $css)) { throw "KakaoTalkTheme.css 가 없습니다: $css" }
# v0 는 이미지가 하나도 없을 수 있다. 없으면 그냥 CSS 만 넣는다.
$imgDir = Join-Path $src 'Images'

$text = Get-Content $css -Raw -Encoding UTF8
$nm = ([regex]"-kakaotalk-theme-name:\s*'([^']*)'").Match($text).Groups[1].Value
$id = ([regex]"-kakaotalk-theme-id:\s*'([^']*)'").Match($text).Groups[1].Value
Write-Host "테마 이름 : $nm"
Write-Host "테마 ID   : $id   <- 기존 테마와 같으면 그걸 덮어씁니다"

if (-not (Test-Path $dist)) { New-Item -ItemType Directory -Path $dist -Force | Out-Null }
if (Test-Path $out) { Remove-Item $out -Force }

# zip 최상단에 KakaoTalkTheme.css 와 Images/ 가 오도록 직접 엔트리를 만든다.
# (Compress-Archive 는 버전에 따라 경로 구분자를 역슬래시로 넣어 카톡이 못 읽는 경우가 있다)
$zip = [System.IO.Compression.ZipFile]::Open($out, 'Create')
try {
    $prefix = (Resolve-Path $src).Path.TrimEnd('\') + '\'
    # 원본 테마에 있던 디렉터리 엔트리도 그대로 넣어준다
    $zip.CreateEntry("Images/") | Out-Null
    $files = Get-ChildItem -Path $src -Recurse -File
    foreach ($f in $files) {
        if ($f.Name -eq '.DS_Store' -or $f.Name -eq 'Thumbs.db' -or $f.Name -eq '.gitkeep') { continue }
        $entry = $f.FullName.Substring($prefix.Length).Replace('\', '/')
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $f.FullName, $entry) | Out-Null
    }
} finally {
    $zip.Dispose()
}

$imgCount = if (Test-Path $imgDir) { (Get-ChildItem $imgDir -File | Where-Object { $_.Name -ne '.gitkeep' }).Count } else { 0 }
Write-Host "이미지     : $imgCount 장"

$kb = [math]::Round((Get-Item $out).Length / 1KB, 1)
Write-Host ""
Write-Host "완료: $out  ($kb KB)"
Write-Host "아이폰으로 옮긴 뒤 파일 앱에서 탭 → 공유 → 카카오톡 으로 적용하세요."
