# 릴리스를 만든다. 모든 테마를 빌드해서 GitHub 릴리스에 자산으로 붙인다.
#   powershell -ExecutionPolicy Bypass -File release.ps1 -Version 0.3 -NotesFile notes.md
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

# 버전은 팔레트 표 한 곳에만 있다. CSS 와 매니페스트는 거기서 생성된다.
$themes = Get-Content (Join-Path $root 'tools\themes.py') -Raw -Encoding UTF8
$declared = ([regex]"VERSION\s*=\s*'([^']*)'").Match($themes).Groups[1].Value
Write-Host "요청 버전      : $Version"
Write-Host "themes.py      : $declared"
if ($declared -ne $Version) {
    throw "버전이 어긋납니다. tools\themes.py 의 VERSION 을 $Version 로 맞추세요."
}

if (git tag --list $tag) { throw "$tag 태그가 이미 있습니다." }
if (git status --porcelain) { throw "커밋 안 된 변경이 있습니다. 먼저 정리하세요." }

# --- 빌드 ---
& powershell -ExecutionPolicy Bypass -File (Join-Path $root 'build.ps1')
if ($LASTEXITCODE -ne 0) { throw "빌드 실패" }

# --- 자산 ---
# 파일 이름에 버전을 넣지 않는다. README 가 releases/latest/download 로 바로 거는데,
# 이름에 버전이 들어가면 릴리스마다 그 링크가 깨진다. 버전은 태그가 갖는다.
$assets = @(Get-ChildItem (Join-Path $root 'dist') -Recurse -File | Sort-Object Name |
            ForEach-Object { $_.FullName })
if ($assets.Count -eq 0) { throw "붙일 자산이 없습니다." }
Write-Host ""
Write-Host "자산 $($assets.Count) 개:"
$assets | ForEach-Object { "  " + (Split-Path -Leaf $_) }

# --- 태그와 릴리스 ---
git tag -a $tag -m "카카오톡 테마 $Version"
if ($LASTEXITCODE -ne 0) { throw "태그 생성 실패" }
git push origin $tag
if ($LASTEXITCODE -ne 0) { throw "태그 푸시 실패" }

gh release create $tag $assets --title "카카오톡 테마 $Version" --notes-file $NotesFile
if ($LASTEXITCODE -ne 0) { throw "릴리스 생성 실패" }

Write-Host ""
Write-Host "완료: $tag  (자산 $($assets.Count) 개)"
