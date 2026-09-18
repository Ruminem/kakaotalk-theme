# -*- coding: utf-8 -*-
"""커스텀 테마 제작 — 이미 만들어둔 배경 그림과 말풍선을 섞어 한 벌을 만든다.

폰에서 브라우저만으로 하려면 docs/make.html 을 쓴다. 이쪽은 로컬과 Actions 용이다.

    python tools/mix.py --list
    python tools/mix.py --bg camp-dark-image --bubble bakery-light --name "내 테마"

배경 쪽에서는 세 화면의 그림만, 말풍선 쪽에서는 말풍선과 색을 통째로 가져온다.
말풍선은 char_outline·stamp 같은 부속 값이 제 팔레트에 묶여 있어서 통째로
가져와야 안 깨진다. 포인트색만 따로 덮어쓸 수 있다.

결과는 build-src/<slug>/ 아래. 포장은 build-one.ps1 이 한다.
팔레트 표를 고치는 게 아니라 표에서 두 벌을 골라 섞는 것이라, 여기서 만든 테마는
저장소에 남지 않는다.
"""
import argparse
import colorsys
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import themes  # noqa: E402
import gen  # noqa: E402

# 배경 쪽에서 가져오는 것. flat_list 도 여기 있다 — 목록 배경을 흐릴지 말지는
# 그림의 성질이라 말풍선이 아니라 배경을 따라가야 한다.
BG_KEYS = ('chat_bg', 'main_bg', 'passcode_bg', 'flat_list')


def catalog():
    """받기 링크에 쓰는 이름 -> 테마."""
    return {themes.file_slug(t): t for t in themes.THEMES}


def pick(cat, slug, what):
    if slug not in cat:
        raise SystemExit('%s 로 "%s" 는 없다. python tools/mix.py --list 로 이름을 본다.'
                         % (what, slug))
    return cat[slug]


# 말풍선 색을 바꾸면 그 색을 물려받은 나머지 색도 같이 돌려야 한다. 글자색은 말풍선 색을
# 옅게 뺀 것이고 포인트색은 대개 보낸 말풍선 색이라, 말풍선만 바꾸면 그것들만 옛 색으로 남는다.
# docs/make.html 은 그림을 다시 못 그려서 색상만 돌리는데, 여기서도 같은 계산을 해야
# 어느 쪽에서 만들든 같은 테마가 나온다.
# 채도가 아니라 채도x명도(실제로 눈에 띄는 색기)로 가른다. 어두운 색은 값이 작아 조금만
# 기울어도 채도가 높게 나온다 — 네온의 검은 벽 #100C14 가 채도 0.40 이다. 채도로 가르면
# 그 벽이 같이 돌아 테마가 통째로 물들고, 반대로 옅은 글자색 #FFE0F0(채도 0.12)은 안 돌아
# 옛 색으로 혼자 남는다. 둘 다 겪고 나서 바꾼 기준이다.
RECOLOR_MIN_CHROMA = 0.06
PALETTE_KEYS = ('bg', 'bg_deep', 'surface', 'pressed', 'border', 'text', 'subtext',
                'accent', 'accent_dim', 'on_accent', 'send_text', 'recv_text')


def _hsv(h):
    h = h.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return colorsys.rgb_to_hsv(r, g, b)


def _hex(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return '#%02X%02X%02X' % (round(r * 255), round(g * 255), round(b * 255))


def recolor_palette(t, send, recv):
    """말풍선 색 둘을 바꾸고, 그 색을 따라가는 나머지 색도 같이 돌린다.

    색마다 원래 두 색 중 색상이 가까운 쪽을 찾아 그쪽 변화를 그대로 적용한다.
    채도가 낮은 색은 건드리지 않는다 — 네온의 검은 벽이 돌면 테마가 통째로 물든다.
    """
    pairs = []
    for old, new in ((t['send'][0], send), (t['recv'][0], recv)):
        if not new:
            continue
        oh, os_, _ = _hsv(old)
        nh, ns, _ = _hsv(new)
        pairs.append((oh, nh - oh, (ns / os_) if os_ else 1.0))
    if not pairs:
        return t

    def moved(col):
        h, s, v = _hsv(col)
        if s * v < RECOLOR_MIN_CHROMA:
            return col
        gap = lambda a, b: min(abs(a - b) % 1.0, 1 - abs(a - b) % 1.0)
        _, shift, k = min(pairs, key=lambda p: gap(h, p[0]))
        return _hex(h + shift, s * k, v)

    for k in PALETTE_KEYS:
        if t.get(k):
            t[k] = moved(t[k])
    for k, new in (('send', send), ('recv', recv)):
        if new:
            t[k] = t[k + '_alt'] = (new, new)
    return t


def mix(bg, bubble, accent=None, name='내 테마', slug='custom', send=None, recv=None):
    fam, var = themes._fam_of(bubble)
    t = dict(bubble, key='custom1', slug=slug, name=name, note='',
             family=fam, variant=var)

    for k in BG_KEYS:
        t.pop(k, None)
        if bg.get(k) is not None:
            t[k] = bg[k]
    t.setdefault('chat_bg', None)

    # 배경에 불이 없는데 말풍선만 불빛을 받으면 까닭 없는 얼룩이 된다(캠핑의 모닥불)
    if bg is not bubble:
        t.pop('firelight', None)

    # 유리 0.55·네온 0.5 처럼 계열이 따로 정한 값은 살린다. 0.72 는 themes.py 가 목록
    # 배경이 있는 테마에 자동으로 붙이는 기본값이라, 배경이 바뀌면 다시 정한다.
    ca = bubble.get('cell_alpha', 1.0)
    t['cell_alpha'] = ca if ca < 0.72 else (0.72 if t.get('main_bg') else 1.0)

    if send or recv:
        recolor_palette(t, send, recv)

    if accent:
        t['accent'] = accent
        t['accent_dim'] = gen.mix(accent, '#000000', 0.22)
        # 포인트색 위에 얹는 글자는 대비로 고른다. 알림 숫자와 전송 단추가 이 짝이다
        r, g, b = gen.rgb(accent)
        t['on_accent'] = '#1A1A1A' if (r * 299 + g * 587 + b * 114) / 1000 > 150 else '#FFFFFF'
    return t


def check():
    """섞는 축이 제자리에서 왔는지 본다."""
    cat = catalog()
    bg, bub = cat['camp-dark-image'], cat['bakery-light']
    t = mix(bg, bub, accent='#FF7AA2', name='점검')
    assert t['chat_bg'] == bg['chat_bg'], '배경은 배경 쪽에서 와야 한다'
    assert t['send'] == bub['send'], '말풍선 색은 말풍선 쪽에서 와야 한다'
    assert t['char_style'] == bub['char_style']
    assert t.get('flat_list', True) == bg.get('flat_list', True), '흐림 여부는 배경을 따른다'
    assert t['on_accent'] == '#1A1A1A', '밝은 포인트색 위에는 어두운 글자'
    assert themes.file_slug(t) == 'custom'
    # 배경 없는 쪽을 고르면 목록 셀이 다시 불투명해져야 한다
    t2 = mix(cat['bakery-light'], cat['camp-dark-image'])
    assert t2.get('main_bg') is None and t2['cell_alpha'] == 1.0

    # 말풍선 색을 바꾸면 그 색을 따라가던 색도 같이 돈다. 벽은 안 돈다
    neon = cat['neon-double']
    t3 = mix(neon, neon, send='#4D8CFF', recv='#FF6FD8')
    assert t3['send'] == ('#4D8CFF', '#4D8CFF') and t3['recv'] == ('#FF6FD8', '#FF6FD8')
    assert t3['bg'] == neon['bg'], '채도 낮은 벽은 그대로 있어야 한다'
    assert t3['send_text'] != neon['send_text'], '글자색도 같이 돌아야 한다'
    assert _hsv(t3['send_text'])[0] - _hsv('#4D8CFF')[0] < 0.08, '글자색이 새 말풍선 색을 따라야 한다'
    print('점검 통과')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bg', help='배경 그림을 가져올 테마')
    ap.add_argument('--bubble', help='말풍선과 색을 가져올 테마')
    ap.add_argument('--accent', help='포인트색 #RRGGBB. 없으면 말풍선 테마 것을 쓴다')
    ap.add_argument('--send', help='보낸 말풍선 색 #RRGGBB. 없으면 말풍선 테마 것을 쓴다')
    ap.add_argument('--recv', help='받은 말풍선 색 #RRGGBB')
    ap.add_argument('--name', default='내 테마', help='폰 테마 목록에 뜰 이름')
    ap.add_argument('--slug', default='custom', help='나올 파일 이름')
    ap.add_argument('--list', action='store_true', help='고를 수 있는 이름을 전부 찍는다')
    ap.add_argument('--no-preview', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()

    if a.check:
        return check()
    cat = catalog()
    if a.list or not (a.bg and a.bubble):
        for slug, t in cat.items():
            print('%-28s %-22s %s' % (slug, t['name'], '배경 있음' if t.get('main_bg') else ''))
        if not a.list:
            raise SystemExit('\n--bg 와 --bubble 을 위 이름 중에서 고른다.')
        return

    t = mix(pick(cat, a.bg, '배경'), pick(cat, a.bubble, '말풍선'),
            a.accent, a.name, a.slug, a.send, a.recv)
    print(gen.build_one(t))

    if not a.no_preview:
        import preview
        out = os.path.join(gen.OUT, a.slug, 'preview.png')
        preview.shrink(preview.chat(t)).save(out)
        print('미리보기 -> %s' % out)


if __name__ == '__main__':
    main()
