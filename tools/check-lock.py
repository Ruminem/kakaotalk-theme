# SPDX-License-Identifier: Apache-2.0
"""빌드 락이 실제로 막는지 본다.

    python tools/check-lock.py

막지 못하면 두 세션이 같은 build-src/ 를 만들고, 그 증상은 몇 분 뒤 엉뚱한
곳에서 「파일이 없다」 로 나타난다. 락이 조용히 고장 나 있는 것이 제일 나쁘다.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lock

HERE = os.path.dirname(os.path.abspath(__file__))


def clean():
    os.environ.pop(lock.ENV, None)
    if os.path.exists(lock.PATH):
        os.unlink(lock.PATH)


def cli(*args):
    return subprocess.run([sys.executable, os.path.join(HERE, 'lock.py')] + list(args),
                          capture_output=True, text=True, encoding='utf-8',
                          env={k: v for k, v in os.environ.items() if k != lock.ENV})


clean()

# 잡으면 파일이 생기고 주인이 나다.
assert lock.take(os.getpid(), '검사') is True
assert os.path.exists(lock.PATH)
assert lock._read()[0] == os.getpid()

# 살아 있는 남이 쥐고 있으면 멈춘다. 다른 프로세스로 물어본다.
r = cli('take', '4242', '남의 빌드')          # 파일의 주인(나)이 아직 살아 있다
assert r.returncode != 0, '살아 있는 락인데 안 막았다'
assert '다른 작업이' in (r.stdout + r.stderr), r.stdout + r.stderr

# 남은 내 락을 못 푼다.
cli('free', '999999')
assert os.path.exists(lock.PATH), '남이 내 락을 풀었다'

lock.free()
assert not os.path.exists(lock.PATH)

# 쥔 채로 죽은 락은 뺏는다. 다시 못 돌면 빌드가 영영 막힌다.
dead = 999999                                            # 없는 PID
with open(lock.PATH, 'w', encoding='utf-8') as f:
    f.write('%d\n0.0\n죽은 빌드' % dead)
assert lock.take(os.getpid(), '검사') is True, '죽은 락을 못 뺏었다'
assert lock._read()[0] == os.getpid()
lock.free()

# 위에서 이미 잡았으면(환경변수) 그냥 지나간다. build.ps1 안의 gen.py 가 이 경우다.
os.environ[lock.ENV] = str(os.getpid())
assert lock.take(os.getpid(), '안쪽') is False
assert not os.path.exists(lock.PATH), '안쪽에서 락을 또 만들었다'
clean()

# 락 파일은 저장소 밖에 있어야 한다. 안에 있으면 release.ps1 이 멈춘다.
repo = os.path.dirname(HERE)
assert not os.path.abspath(lock.PATH).startswith(os.path.abspath(repo) + os.sep), lock.PATH

print('락 검사 통과 (%s)' % lock.PATH)
