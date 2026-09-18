# 모든 테마를 iOS 와 안드로이드 양쪽으로 빌드한다. 배포는 항상 이걸로 한다.
#   powershell -ExecutionPolicy Bypass -File build.ps1
# 결과: dist\iOS\<테마>.ktheme, dist\android\<테마>.apk

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# build-src/·dist/·assets/ 는 브랜치로 나뉘지 않는다. 남이 같이 만들고 있으면
# 여기서 멈춘다 - 0.39.1 첫 릴리스가 그렇게 296벌이 깨졌다. 자세한 것은 tools/lock.py.
& python (Join-Path $root 'tools\lock.py') take $PID '배포 빌드'
if ($LASTEXITCODE -ne 0) { exit 1 }
$env:KTHEME_BUILD_LOCK = $PID

# 소스는 팔레트 표에서 생성된다. 원본은 tools/themes.py 하나뿐이다.
# 미리보기는 다시 그리지 않는다 — 커밋 전에 preview.ps1 로 만들어 두고, 릴리스는 깨끗한 트리에서만 돈다.
Write-Host "tools/gen.py 로 소스를 만듭니다"
& python (Join-Path $root 'tools\gen.py') --no-preview
if ($LASTEXITCODE -ne 0) { throw "소스 생성 실패" }

# 브라우저가 안드로이드 커스텀 테마를 만들 때 쓰는 템플릿도 같이 만든다. 표식 색과
# 이름 자리가 구워진 한 벌이고, 사이트가 릴리스 자산에서 받아 간다.
# 자세한 것은 CLAUDE.md 의 `커스텀 테마 제작`.
Write-Host "커스텀 테마 템플릿을 만듭니다"
& python (Join-Path $root 'tools\mix.py') --template --no-preview
if ($LASTEXITCODE -ne 0) { throw "템플릿 생성 실패" }

$src = Join-Path $root 'build-src'
$dist = Join-Path $root 'dist'
if (Test-Path $dist) { Remove-Item $dist -Recurse -Force }

# 테마마다 aapt2 -> zipalign -> apksigner 가 도는데 apksigner 는 JVM 이라 시작만으로
# 몇 초가 간다. 테마끼리는 아무것도 공유하지 않으므로(폴더도 build-tmp 도 따로) 동시에
# 띄운다. PowerShell 5.1 에는 ForEach-Object -Parallel 이 없어서 프로세스를 직접 띄우고
# 수를 센다.
$parallel = [Environment]::ProcessorCount
$themes = @(Get-ChildItem $src -Directory | Sort-Object Name)

# 첫 테마는 혼자 돌린다. theme.keystore 가 없으면 build-android.ps1 이 만드는데,
# 여러 개가 동시에 없는 키를 만들려 들면 서로 덮어쓴다. 한 번 만들어지면 그 뒤로는
# 읽기만 한다.
$logs = Join-Path $env:TEMP ("ktheme-build-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $logs -Force | Out-Null

$failed = @()
$procs = @()          # @{ key; proc; log }
$done = 0
$total = $themes.Count

function Show-Finished($p) {
    # HasExited 가 참이어도 ExitCode 는 아직 $null 이다. Start-Process -PassThru 가 준
    # 객체는 WaitForExit() 를 불러야 종료코드가 채워진다. 안 부르면 $null -ne 0 이 참이라
    # 다 만들어진 테마가 전부 실패로 찍힌다.
    $p.proc.WaitForExit()
    if (Test-Path $p.log) { Get-Content $p.log -Encoding UTF8 | Write-Host }
    if ($p.proc.ExitCode -ne 0) {
        Write-Host "  실패: $($p.key)"
        # apksigner 는 JVM 경고를 stderr 로 뱉는다. 성공했을 때는 보여줄 게 아니라
        # 따로 받아 두고, 실패했을 때만 꺼내 본다.
        if (Test-Path $p.err) { Get-Content $p.err -Encoding UTF8 | Write-Host }
        return $p.key
    }
    return $null
}

for ($i = 0; $i -lt $total; $i++) {
    $theme = $themes[$i]
    # 첫 테마가 끝날 때까지는 둘째를 안 띄운다. 키스토어가 그때 만들어질 수 있어서다.
    $limit = if ($i -eq 1) { 1 } else { $parallel }
    while ($procs.Count -ge $limit) {
        $fin = @($procs | Where-Object { $_.proc.HasExited })
        if ($fin.Count -gt 0) {
            # 끝난 것을 뽑아 두고, 뺄 때도 그 목록으로 뺀다. HasExited 를 다시 물으면
            # 그새 끝난 프로세스가 보고도 없이 목록에서 사라진다 — 76개를 돌렸는데
            # 75줄만 찍혔던 게 이것이다.
            foreach ($p in $fin) {
                $bad = Show-Finished $p
                if ($bad) { $failed += $bad }
                $done++
            }
            $keys = $fin | ForEach-Object { $_.key }
            $procs = @($procs | Where-Object { $keys -notcontains $_.key })
        } else {
            Start-Sleep -Milliseconds 120
        }
    }
    $log = Join-Path $logs ($theme.Name + '.log')
    $err = Join-Path $logs ($theme.Name + '.err')
    $proc = Start-Process -FilePath 'powershell' -PassThru -NoNewWindow `
        -ArgumentList @('-ExecutionPolicy', 'Bypass', '-File',
                        (Join-Path $root 'build-one.ps1'),
                        '-Theme', $theme.FullName, '-Dist', $dist) `
        -RedirectStandardOutput $log -RedirectStandardError $err
    # 핸들을 한 번 읽어 붙잡아 둔다. 안 그러면 프로세스가 끝난 뒤 ExitCode 가 계속
    # $null 이고, $null -ne 0 이 참이라 다 만들어진 테마가 전부 실패로 찍힌다.
    # WaitForExit() 를 불러도 마찬가지다 — 핸들이 이미 닫혔으면 읽을 데가 없다.
    $null = $proc.Handle
    $procs += @{ key = $theme.Name; proc = $proc; log = $log; err = $err }
}

foreach ($p in $procs) {
    $bad = Show-Finished $p
    if ($bad) { $failed += $bad }
}
Remove-Item $logs -Recurse -Force -ErrorAction SilentlyContinue

if (Test-Path (Join-Path $root 'build-tmp')) {
    Remove-Item (Join-Path $root 'build-tmp') -Recurse -Force -ErrorAction SilentlyContinue
}

# 템플릿은 안드로이드에서만 쓴다. 아이폰 쪽은 .ktheme 를 통째로 가져다 섞으므로
# 필요 없고, 이름이 자리표(~~~~)라 테마 목록에 나가면 안 된다
Remove-Item (Join-Path $dist 'iOS\custom-template.ktheme') -ErrorAction SilentlyContinue

& python (Join-Path $root 'tools\lock.py') free $PID

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
