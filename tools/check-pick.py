# SPDX-License-Identifier: Apache-2.0
"""테마 고르기가 맞게 도는지 본다.

    python tools/check-pick.py

고르기가 틀리면 조용히 엉뚱한 테마를 그리거나, 더 나쁘게는 갤러리에서 나머지
291벌이 사라진다. 둘 다 눈으로 보기 전에는 모른다.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen
import themes


def pick(*args):
    sys.argv = ['gen.py'] + list(args)
    return gen.picked()


# 인자가 없으면 전부다. 옵션은 고르는 말이 아니다.
assert pick() is None
assert pick('--no-preview') is None

# 조각 하나로 계열이 통째로 잡힌다.
four = pick('neonlounge')
assert len(four) == 4, len(four)
assert all('neonlounge' in themes.file_slug(t) for t in four)

# 파일 이름·키·테마 이름 어디로든 잡힌다.
assert pick('neonlounge-octagon')[0] is pick('네온사인 v5 팔각')[0]

# 조각을 여럿 주면 합집합이다.
both = pick('neonlounge', 'camp-light')
assert len(both) == len(four) + len(pick('camp-light'))
assert len(both) == len(set(id(t) for t in both))       # 겹쳐도 한 번만

# 맞는 것이 없으면 조용히 0벌을 그리지 않고 멈춘다.
try:
    pick('그런테마없다')
except SystemExit:
    pass
else:
    raise AssertionError('없는 이름인데 안 멈췄다')

# 고른 것만 그려도 페이지는 전부를 담아야 한다. generate 가 그림(only)과
# 페이지(ts)를 따로 받는지 확인한다 — 한 인자로 합치면 갤러리가 비어 버린다.
import inspect

import preview
sig = inspect.signature(preview.generate)
assert list(sig.parameters) == ['ts', 'only'], sig
assert sig.parameters['only'].default is None

print('고르기 검사 통과 (%d벌 중 neonlounge %d벌)' % (len(themes.THEMES), len(four)))
