# -*- coding: utf-8 -*-
"""갤럭시 스토어 제출용 자산을 한 테마 분 뽑는다.

미리보기(assets/*.webp)는 1.5배로 줄여 내보낸 603x1311 이라 스토어에 올리기엔 작다.
여기서는 preview.py 의 화면 함수를 직접 불러 줄이기 전 3배 원본(1206x2622)을 PNG 로 받는다.
아이콘도 128 을 늘리지 않고 gen.icon(t, 512) 로 그 크기에 새로 그린다.

  python3 build-tmp/galaxy/make-assets.py <파일이름조각>

assets/ 와 docs/ 는 건드리지 않는다 — 워킹 트리가 더러워지면 release.ps1 이 멈춘다.
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools'))

import gen            # noqa: E402
import preview        # noqa: E402
import themes         # noqa: E402


# --- 글꼴 대체 ------------------------------------------------------------
# preview.font() 는 윈도우의 NotoSansKR-VF.ttf 를 쓴다. 그 파일이 없는 곳(리눅스
# 컨테이너, CI)에서는 PIL 이 기본 비트맵 글꼴로 떨어져 한글이 점으로 뭉개진다.
# 그래서 없을 때만 Noto Sans CJK KR 로 갈아 끼운다 — 있으면 손대지 않으므로
# 윈도우에서 돌린 결과는 커밋된 미리보기와 같다.
_CJK = '/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc'
_KR = 1                       # TTC 안 한국어 얼굴의 차례
_sub = {}


def _font_sub(pt, weight=400):
    from PIL import ImageFont
    k = (pt, weight)
    if k not in _sub:
        # 가변 글꼴이 아니라 굵기가 두 벌뿐이다. 600 이상은 Bold 로 본다.
        path = _CJK % ('Bold' if weight >= 600 else 'Regular')
        _sub[k] = ImageFont.truetype(path, preview.u(pt), index=_KR)
    return _sub[k]


if not os.path.exists(preview._NOTO) and os.path.exists(_CJK % 'Regular'):
    preview.font = _font_sub
    SUBSTITUTED = True
else:
    SUBSTITUTED = False

# --- 사람 이름 ------------------------------------------------------------
# preview.NAMES 는 카카오프렌즈 열 마리다(라이언·어피치·무지...). README 안에서는
# 카톡이 캡처할 때 이름을 가리는 방식을 흉내 낸 것이라 문제가 없지만, 스토어 등재
# 그림은 남에게 파는 물건의 사진이라 거기에 카카오 상표가 박히면 안 된다.
# 프렌즈와 안 겹치는 동물로 바꾼다 — 말투와 자릿수는 그대로 둔다.
STORE_NAMES = ('운동하는 수달', '산책하는 다람쥐', '낮잠 자는 너구리', '춤추는 펭귄',
               '쇼핑하는 여우', '요리하는 사슴', '노래하는 부엉이', '책 읽는 알파카',
               '고구마 먹는 두루미', '여행하는 고슴도치')


OUT = os.path.join(ROOT, 'build-tmp', 'galaxy')

SCREENS = (('list', preview.chat_list), ('chat', preview.chat),
           ('passcode', preview.passcode), ('splash', preview.splash))

# 스토어 아이콘. 128 짜리 계열 아이콘을 늘리면 가장자리가 뭉개진다.
ICON = 512


def swap_names():
    """상표 이름을 그림에 굽지 않는다.

    preview.ROWS 는 모듈을 불러올 때 NAMES 로 이미 엮여 있어서, NAMES 만 갈면
    채팅방은 바뀌고 목록은 옛 이름이 남는다. 옛 이름에서 새 이름으로 표를 만들어
    ROWS 안의 이름 칸도 같이 옮긴다 — ROWS 에 손으로 적은 '주말 모임' 같은 칸은
    표에 없으므로 그대로 남는다.
    """
    table = dict(zip(preview.NAMES, STORE_NAMES))
    preview.ROWS = [(table.get(row[0], row[0]),) + tuple(row[1:])
                    for row in preview.ROWS]
    preview.NAMES = STORE_NAMES
    left = [n for n in preview.NAMES if n in table]
    if left:
        sys.exit('이름이 안 바뀐 것이 있다: %s' % ', '.join(left))


def main(frag):
    picked = [t for t in themes.THEMES if frag in themes.file_slug(t)]
    if not picked:
        sys.exit('그런 테마가 없다: %s' % frag)
    if len(picked) > 1:
        sys.exit('조각이 여러 벌에 걸린다: %s' % ', '.join(themes.file_slug(t) for t in picked))

    swap_names()

    t = picked[0]
    slug = themes.file_slug(t)
    out = os.path.join(OUT, slug)
    os.makedirs(out, exist_ok=True)
    print('%s — %s' % (slug, t['name']))

    gen.icon(t, ICON).save(os.path.join(out, 'icon-%d.png' % ICON), optimize=True)
    print('  icon-%d.png' % ICON)

    if SUBSTITUTED:
        print('  ! 글꼴 대체: Noto Sans CJK KR (윈도우의 NotoSansKR-VF 없음)')
        print('    글자 모양이 커밋된 미리보기와 조금 다르다. 최종본은 PC 에서 뽑는다.')

    for kind, draw in SCREENS:
        img = draw(t)          # 줄이기 전 3배 원본
        path = os.path.join(out, '%s.png' % kind)
        img.save(path, optimize=True)
        print('  %s.png  %dx%d  %d KB' % (kind, img.width, img.height,
                                          os.path.getsize(path) // 1024))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'snow-glow-image')
