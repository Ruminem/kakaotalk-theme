# SPDX-License-Identifier: Apache-2.0
"""저장소 산출물을 만드는 동안 하나만 돌게 한다.

`build-src/`·`dist/`·`assets/` 는 브랜치로 나뉘지 않는다. 두 세션이 동시에
만들면 한쪽이 지운 파일을 다른 쪽이 읽는다 — 0.39.1 첫 릴리스가 그렇게 296벌이
깨져서 멈췄다. worktree 로 워킹 트리를 갈라도 이 셋은 그대로 겹친다.

락 파일은 저장소 밖(`%TEMP%`)에 둔다. 안에 두면 `release.ps1` 이 커밋 안 된
변경으로 보고 멈춘다 — 0.38 에서 로그 파일로 같은 일을 겪었다.

파이썬에서는 이렇게 쓴다.

    with lock.hold('미리보기'):
        ...

PowerShell 은 CLI 로 쓴다. 제 PID 를 주고, 끝나면 반드시 풀어야 하니
try/finally 에 넣는다.

    python tools/lock.py take $PID "배포 빌드"
    python tools/lock.py free

`KTHEME_BUILD_LOCK` 이 환경에 있으면 이미 위에서 잡은 것으로 보고 그냥 지나간다.
`build.ps1` 이 잡고 그 안의 `gen.py` 가 또 잡으려 드는 것을 막는다 — 환경변수는
자식 프로세스가 물려받으므로 사슬이 몇 겹이든 한 번만 잡힌다.
"""
import contextlib
import os
import sys
import tempfile
import time

PATH = os.path.join(tempfile.gettempdir(), 'kakaotalk-theme-build.lock')
ENV = 'KTHEME_BUILD_LOCK'


def _alive(pid):
    """그 PID 가 아직 도는가. 윈도우만 본다 — 빌드가 윈도우에서만 돈다."""
    if pid <= 0:
        return False
    if os.name != 'nt':                                  # CI 도 windows 러너다
        return True
    import ctypes
    h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)   # QUERY_LIMITED_INFO
    if not h:
        return False
    ctypes.windll.kernel32.CloseHandle(h)
    return True


def _read():
    """(pid, 시작시각, 설명). 락이 없거나 망가졌으면 None."""
    try:
        with open(PATH, encoding='utf-8') as f:
            pid, started, what = f.read().split('\n', 2)
        return int(pid), float(started), what
    except (OSError, ValueError):
        return None


def take(pid, what):
    """락을 잡는다. 남이 쥐고 있으면 안내하고 멈춘다."""
    if os.environ.get(ENV):
        return False                                     # 위에서 이미 잡았다
    body = '%d\n%r\n%s' % (pid, time.time(), what)
    while True:
        try:
            fd = os.open(PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            held = _read()
            if held is None or not _alive(held[0]):
                # 쥔 채로 죽었다. 뺏는다 — 남겨두면 다음 빌드가 영영 못 돈다.
                os.unlink(PATH)
                continue
            mine, started, doing = held
            sys.exit(
                '다른 작업이 저장소 산출물을 만들고 있습니다: %s (PID %d, %d분 전에 시작)\n'
                'build-src/·dist/·assets/ 를 같이 쓰면 한쪽이 지운 파일을 다른 쪽이 읽습니다.\n'
                '끝나기를 기다리세요. 그 작업이 죽었다면 %s 를 지우면 됩니다.'
                % (doing, mine, (time.time() - started) / 60, PATH))
        else:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(body)
            os.environ[ENV] = str(pid)
            return True


def free():
    """내가 잡은 락만 푼다."""
    held = _read()
    if held and held[0] == int(os.environ.get(ENV) or -1):
        os.unlink(PATH)
    os.environ.pop(ENV, None)


@contextlib.contextmanager
def hold(what):
    mine = take(os.getpid(), what)
    try:
        yield
    finally:
        if mine:
            free()


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'take':
        # PowerShell 이 준다. 그 프로세스가 사는 동안이 락이 사는 동안이다.
        take(int(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else '빌드')
    elif cmd == 'free':
        # 제가 잡은 것만 푼다. release.ps1 이 잡은 락을 그 안의 build.ps1 이
        # 푸는 일이 없어야 한다 - 풀리고 나면 업로드 도중에 남이 dist/ 를 지운다.
        held = _read()
        if held and held[0] == (int(sys.argv[2]) if len(sys.argv) > 2 else -1):
            os.unlink(PATH)
    else:
        sys.exit('쓰기: python tools/lock.py take <pid> <설명> | free')
