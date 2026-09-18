# 테마 하나를 iOS 용 .ktheme 로 포장한다.
#   powershell -ExecutionPolicy Bypass -File build-ios.ps1 -Source build-src\inkmint01\ios -Out dist\iOS\inkmint01.ktheme
#
# 보통은 직접 부르지 않는다. build.ps1 이 테마마다 이걸 부른다.

param(
    [Parameter(Mandatory = $true)][string]$Source,
    [Parameter(Mandatory = $true)][string]$Out
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$css = Join-Path $Source 'KakaoTalkTheme.css'
if (-not (Test-Path $css)) { throw "KakaoTalkTheme.css 가 없습니다: $css" }

$text = Get-Content $css -Raw -Encoding UTF8
$nm = ([regex]"-kakaotalk-theme-name:\s*'([^']*)'").Match($text).Groups[1].Value
$id = ([regex]"-kakaotalk-theme-id:\s*'([^']*)'").Match($text).Groups[1].Value

$dir = Split-Path -Parent $Out
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
if (Test-Path $Out) { Remove-Item $Out -Force }

# zip 최상단에 KakaoTalkTheme.css 와 Images/ 가 오도록 직접 엔트리를 만든다.
# (Compress-Archive 는 버전에 따라 경로 구분자를 역슬래시로 넣어 카톡이 못 읽는 경우가 있다)
$zip = [System.IO.Compression.ZipFile]::Open($Out, 'Create')
try {
    $prefix = (Resolve-Path $Source).Path.TrimEnd('\') + '\'
    # CreateEntry 는 만든 시각을 엔트리에 박는다. 그래서 그림이 하나도 안 바뀌어도
    # .ktheme 이 매번 다른 바이트로 나왔다 - 「전과 같은지」 를 해시로 못 보게 만든다.
    # 파일 엔트리는 CreateEntryFromFile 이 파일 시각을 쓰므로 원래 결정적이다.
    $dirEntry = $zip.CreateEntry("Images/")
    $dirEntry.LastWriteTime = [DateTimeOffset]::new(2020, 1, 1, 0, 0, 0, [TimeSpan]::Zero)
    foreach ($f in Get-ChildItem -Path $Source -Recurse -File) {
        if ($f.Name -eq '.DS_Store' -or $f.Name -eq 'Thumbs.db') { continue }
        $entry = $f.FullName.Substring($prefix.Length).Replace('\', '/')
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $f.FullName, $entry) | Out-Null
    }
} finally {
    $zip.Dispose()
}

$imgCount = (Get-ChildItem (Join-Path $Source 'Images') -File -ErrorAction SilentlyContinue).Count
$kb = [math]::Round((Get-Item $Out).Length / 1KB, 1)
Write-Host ("  iOS      {0,-10} {1,-24} 이미지 {2,2}장  {3,6:N1} KB" -f $nm, $id, $imgCount, $kb)
