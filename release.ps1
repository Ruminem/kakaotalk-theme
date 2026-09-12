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
# 한글을 명령줄 인자로 넘기지 않는다. PowerShell 이 네이티브 프로그램에 인자를 넘길 때
# 시스템 코드페이지로 인코딩해서 한글이 깨진다(릴리스 제목이 "移댁뭅?ㅽ넚" 이 됐던 이유).
# 태그 메시지와 릴리스 제목은 파일을 거쳐서 보낸다.
$tagMsg = Join-Path $env:TEMP "ktheme-tag-$Version.txt"
[System.IO.File]::WriteAllText($tagMsg, "카카오톡 테마 $Version", (New-Object System.Text.UTF8Encoding $false))
git tag -a $tag -F $tagMsg
Remove-Item $tagMsg -Force
if ($LASTEXITCODE -ne 0) { throw "태그 생성 실패" }
git push origin $tag
if ($LASTEXITCODE -ne 0) { throw "태그 푸시 실패" }

# 자산만 먼저 올리고(제목 없이), 제목은 JSON 으로 따로 넣는다.
gh release create $tag $assets --notes-file $NotesFile --title $tag
if ($LASTEXITCODE -ne 0) { throw "릴리스 생성 실패" }

$repo = (gh repo view --json nameWithOwner --jq '.nameWithOwner')
$id = (gh api "repos/$repo/releases/tags/$tag" --jq '.id')
$body = Join-Path $env:TEMP "ktheme-title-$Version.json"
$json = '{"name":"카카오톡 테마 ' + $Version + '"}'
[System.IO.File]::WriteAllText($body, $json, (New-Object System.Text.UTF8Encoding $false))
gh api -X PATCH "repos/$repo/releases/$id" --input $body | Out-Null
Remove-Item $body -Force
if ($LASTEXITCODE -ne 0) { throw "릴리스 제목 설정 실패" }

# 사이트의 files/ 도 이 릴리스의 자산으로 바꾼다. iOS 는 릴리스 자산이 아니라 Pages 를
# 거쳐 받기 때문이다(릴리스 자산에는 Content-Disposition: attachment 가 붙어 카톡이
# 가로챌 수 없다). 여기서 안 부르면 사이트만 옛 자산에 머물러, 고친 테마를 냈는데
# iOS 로 받는 사람은 옛것을 깐다 — 0.24 와 0.24.1 이 그렇게 나갔다.
#
# 워크플로의 release: published 트리거로는 안 된다. 그 런은 태그에서 돌고 github-pages
# 환경의 배포 브랜치 정책이 태그를 거부한다. main 에서 불러야 통과한다.
Write-Host ""
Write-Host "사이트를 새 자산으로 갱신합니다"
gh workflow run pages.yml --ref main
if ($LASTEXITCODE -ne 0) {
    Write-Host "  경고: 워크플로 호출 실패. 릴리스는 나갔으므로 직접 돌리세요 —"
    Write-Host "        gh workflow run pages.yml --ref main"
}

Write-Host ""
Write-Host "완료: $tag  (자산 $($assets.Count) 개)"
