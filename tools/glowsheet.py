# -*- coding: utf-8 -*-
"""글로우 모양 비교 그림. 새 말풍선을 만들면 어떤 글로우가 어울리는지 이걸로 먼저 본다.

    python tools/glowsheet.py 영화관          # 계열 이름 — 어두운 쪽 변형을 쓴다
    python tools/glowsheet.py cinema127       # 테마 키

tools/glow.py 의 모양을 전부 한 줄씩 그린다. 줄마다 연달아 보낸 말풍선 두 장(실제 간격 6pt),
보낸 말풍선, 긴 말로 늘인 말풍선을 놓고 여백 크기를 적는다 — 넓게 번지는 빛일수록 말풍선 사이가
벌어지는 것까지 같이 보려는 것이다. 배경은 그 테마의 채팅방 배경이다.

build-tmp/glow-<파일이름>.png 에 저장한다. build-tmp 는 저장소에 들어가지 않는다.
캐릭터 말풍선(char_style) 테마만 된다.
"""
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import charbubble as cb  # noqa: E402
import gen  # noqa: E402
import glow  # noqa: E402
import themes  # noqa: E402

S = 3
MSG = '오늘 밤 여기서 보자'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def font(px, weight=400):
    try:
        f = ImageFont.truetype(r'C:\Windows\Fonts\NotoSansKR-VF.ttf', px)
        f.set_variation_by_axes([weight])
        return f
    except Exception:
        return ImageFont.truetype(r'C:\Windows\Fonts\malgun.ttf', px)


def find(arg):
    for t in themes.THEMES:
        if t['key'] == arg:
            return t
    fams = dict(themes.families())
    if arg in fams:
        members = fams[arg]
        dark = [m for m in members if not themes._bg_is_light(m)]
        pic = [m for m in dark if m.get('chat_bg')]
        return (pic or dark or members)[0]
    raise SystemExit('테마 키나 계열 이름이 아니다: %s' % arg)


def stretch_wide(im, cap, W):
    """cap 자리 한 줄만 옆으로 늘인다. 카톡이 긴 말에 하는 것과 같다."""
    w, h = im.size
    W = max(W, w)
    col = im.crop((cap, 0, cap + 1, h)).resize((W - w + 1, h))
    out = Image.new('RGBA', (W, h), (0, 0, 0, 0))
    out.paste(im.crop((0, 0, cap, h)), (0, 0))
    out.paste(col, (cap, 0))
    out.paste(im.crop((cap + 1, 0, w, h)), (cap + W - w + 1, 0))
    return out


def row(t, name):
    t2 = dict(t, glow_style=name, material=None)
    if name == 'char':
        t2['char_glow'] = t.get('char_glow') or 6
    r1, _ = cb.sheet(t2, 'recv', '01', S)
    r2, g2 = cb.sheet(t2, 'recv', '02', S)
    gap = 6 * S
    stack = Image.new('RGBA', (max(r1.width, r2.width), r1.height + gap + r2.height), (0, 0, 0, 0))
    stack.alpha_composite(r1, (0, 0))
    stack.alpha_composite(r2, (0, r1.height + gap))
    s1, _ = cb.sheet(t2, 'send', '01', S)
    ls, gl = cb.sheet(t2, 'send', '01', S)
    fmsg = font(16 * S)
    long_ = stretch_wide(ls, gl['cap'] * S, int(fmsg.getlength(MSG) + gl['ins'][1] * 2 * S))
    ImageDraw.Draw(long_).text((gl['ins'][1] * S, (gl['ins'][0] + 11) * S), MSG, font=fmsg,
                               anchor='lm', fill=gen.rgb(t['send_text']) + (255,))
    m = glow.margin(t2)
    p = glow.PRESETS[name]
    sub = '%s · 여백 %dpt · 한 줄 %dx%dpt' % (name, max(m), g2['w'], g2['h'])
    return p['label'], sub, [stack, s1, long_]


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    t = find(sys.argv[1])
    if not t.get('char_style'):
        raise SystemExit('%s 는 캐릭터 말풍선 테마가 아니다. 이 도구는 char_style 테마만 그린다' % t['key'])
    mat = t.get('material')
    rows = []
    for name in glow.PRESETS:
        label, sub, tiles = row(t, name)
        if mat in glow.NO_GLOW:
            sub += ' · 이 재질은 글로우 금지'
        if glow.MATERIAL.get(mat) == name:
            label += '  ← 재질 기본값'
        rows.append((label, sub, tiles))
        print('%-6s %s' % (name, sub))

    LW = 360
    W = LW + max(sum(im.width + 50 for im in tl) for _, _, tl in rows) + 20
    H = sum(max(im.height for im in tl) + 40 for _, _, tl in rows) + 30
    if t.get('chat_bg'):
        bg = gen.background(t, t['chat_bg'], W, H).convert('RGBA')
    else:
        bg = Image.new('RGBA', (W, H), gen.rgb(t['bg_deep']) + (255,))
    d = ImageDraw.Draw(bg)
    flab, fsub = font(32, 700), font(22)
    text, sub_c = gen.rgb(t['text']) + (255,), gen.rgb(t['subtext']) + (255,)
    y = 30
    for label, sub, tiles in rows:
        hh = max(im.height for im in tiles)
        d.text((24, y + hh // 2 - 18), label, font=flab, anchor='lm', fill=text)
        d.text((24, y + hh // 2 + 20), sub, font=fsub, anchor='lm', fill=sub_c)
        x = LW
        for im in tiles:
            bg.alpha_composite(im, (x, y + (hh - im.height) // 2))
            x += im.width + 50
        y += hh + 40
    out_dir = os.path.join(ROOT, 'build-tmp')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'glow-%s.png' % themes.file_slug(t))
    bg.convert('RGB').save(path)
    print('->', path)


if __name__ == '__main__':
    main()
