# -*- coding: utf-8 -*-
"""제출용 그림에 그려질 글자에 카카오 상표가 남아 있지 않은지 본다."""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import preview                                  # noqa: E402
import importlib                                # noqa: E402
mk = importlib.import_module('make-assets')     # noqa: E402

# 카카오프렌즈. 공식 목록이라 늘어나면 여기 적는다.
FRIENDS = ('라이언', '어피치', '무지', '프로도', '네오', '튜브',
           '제이지', '콘', '춘식이', '죠르디')


def drawn():
    """그림에 실제로 그려지는 글자를 전부 모은다."""
    out = list(preview.NAMES) + list(preview.CHIPS)
    for row in preview.ROWS:
        out += [row[0], row[1], row[2]]
    for who, line in preview.CHAT:
        out.append(line)
    return out


def scan(where):
    return sorted({f for f in FRIENDS for s in where if f in s})


bad = scan(drawn())
print('바꾸기 전 : %s' % (', '.join(bad) if bad else '없음'))
if not bad:
    sys.exit('검사가 아무것도 안 잡는다 — 바꾸기 전에는 걸려야 한다')

mk.swap_names()
bad = scan(drawn())
print('바꾼 뒤   : %s' % (', '.join(bad) if bad else '없음'))
if bad:
    sys.exit('상표가 남았다')
print()
print('통과 — 그려지는 글자 %d 개에 카카오프렌즈 없음' % len(drawn()))
