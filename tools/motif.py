# -*- coding: utf-8 -*-
"""캐릭터가 없는 계열의 기본 프로필 세 장.

목록 화면에서 테마가 바꿀 수 있는 자리 중 프로필이 제일 크게 보인다. 예전에는 모든 계열이
같은 사람 모양을 색만 바꿔 썼고, 목록이 아무 테마나 같아 보였다. 계열마다 그 계열의 물건
세 가지(MOTIFS)를 두고, 그리는 방식은 테마에서 정한다.

  유리 계열         배경을 거꾸로 비추는 유리구슬(marble). 판 위에 도형을 올렸더니 상자 안의
                    상자가 되어 앱 아이콘 자리표시처럼 보였다 — 유리는 두께와 굴절로 읽힌다
  글로우 + 어두움   도형 윤곽을 따라 긋는 네온관
  글로우 + 밝음     채운 도형에 옅은 후광. 밝은 바탕에서는 관이 안 보인다
  나머지            채운 도형 한 가지 색

새 계열을 더하면 MOTIFS 에 한 줄 쓴다. 안 쓰면 생성이 멈춘다 — 사람 모양으로 조용히
돌아가면 목록만 다시 아무 테마나 같아진다.
"""
import math

from PIL import Image, ImageChops, ImageDraw, ImageFilter

import gen
import themes

MOTIFS = {
    '먹빛 민트': ('leaf', 'drop', 'moon'),
    '크림 라떼': ('cup', 'bean', 'heart'),
    '믹스드': ('chat', 'heart', 'star'),
    '캔디 팝': ('candy', 'lollipop', 'star'),
    '도형': ('circle', 'triangle', 'square'),
    '차분': ('pebble', 'leaf', 'cup'),
    '고요': ('ripple', 'moon', 'cloud'),
    '벚꽃 그늘': ('blossom', 'petal', 'cloud'),
    '오로라': ('aurora', 'pine', 'star'),
    '심야': ('moon', 'star', 'mountain'),
    '바다': ('wave', 'fish', 'sun'),
    '숲': ('pine', 'leaf', 'mushroom'),
    '설원': ('snowflake', 'snowman', 'mitten'),
    '야경': ('building', 'moon', 'star'),
    '사이버펑크': ('bolt', 'chip', 'diamond'),
    '레드': ('flame', 'heart', 'diamond'),
    '오렌지': ('sun', 'bulb', 'star'),
    '옐로': ('bolt', 'star', 'bulb'),
    '라임': ('leaf', 'bolt', 'circle'),
    '그린': ('leaf', 'pine', 'drop'),
    '민트': ('drop', 'leaf', 'ripple'),
    '시안': ('wave', 'drop', 'snowflake'),
    '블루': ('moon', 'wave', 'star'),
    '바이올렛': ('diamond', 'moon', 'star'),
    '퍼플': ('comet', 'diamond', 'moon'),
    '핑크': ('heart', 'blossom', 'star'),
    '불꽃놀이': ('burst', 'comet', 'star'),
    '연등': ('lantern', 'lotus', 'moon'),
    '알전구': ('bulb', 'garland', 'star'),
    '고속도로': ('car', 'signal', 'sign'),
    '터미널': ('prompt', 'code', 'monitor'),
}

SS = 3

# 네온관으로 그려도 구멍을 남기는 모티프. 구멍이 떨어져 있어 관이 서로 붙지 않는다
KEEP_HOLES = {'signal'}


def _lum(h):
    def ch(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = gen.rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def legible(col, back, text, need=2.2):
    """도형 색이 바탕에 묻히면 글자색 쪽으로 당긴다. 색상은 두고 대비만 벌린다.

    포인트색 셋을 돌려 쓰다 보니 눌림 색이 짙은 판 위에 오면 36pt 에서 도형이 사라졌다
    (고요의 달, 크림 라떼의 원두).
    """
    lb = _lum(back)
    for i in range(11):
        c = gen.mix(col, text, i / 10.0)
        lc = _lum(c)
        if (max(lc, lb) + 0.05) / (min(lc, lb) + 0.05) >= need:
            return c
    return text


def erode(m, n):
    """n 픽셀만큼 깎는다. 큰 MinFilter 한 번은 느려서 3x3 을 되풀이한다 — 결과는 같은 네모 창이다."""
    for _ in range(max(0, n)):
        m = m.filter(ImageFilter.MinFilter(3))
    return m


def _put(img, col, alpha):
    lay = Image.new('RGBA', img.size, gen.rgb(col) + (255,))
    lay.putalpha(alpha)
    img.alpha_composite(lay)


def mask(kind, S, fine=True):
    """모티프 실루엣. 100 칸 기준 좌표, 255 가 도형이다.

    fine 이 거짓이면 창문·조개 줄무늬 같은 잔구멍을 뺀다 — 네온관은 윤곽을 따라 관을 긋는데
    구멍마다 관이 생겨 서로 붙으면 덩어리가 된다.
    """
    m = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(m)
    u = S / 100.0

    def P(*pts):
        return [(x * u, y * u) for x, y in pts]

    def W(v):
        return max(1, int(v * u))

    def star(cx, cy, r1, r2, n=5, rot=-90):
        return P(*[(cx + math.cos(math.radians(rot + i * 180 / n)) * (r1 if i % 2 == 0 else r2),
                    cy + math.sin(math.radians(rot + i * 180 / n)) * (r1 if i % 2 == 0 else r2))
                   for i in range(2 * n)])

    if kind == 'heart':
        pts = []
        for i in range(72):
            a = 2 * math.pi * i / 72
            x = 16 * math.sin(a) ** 3
            y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
            pts.append((50 + x * 2.2, 52 - y * 2.2))
        d.polygon(P(*pts), fill=255)
    elif kind == 'star':
        d.polygon(star(50, 54, 38, 16), fill=255)
    elif kind == 'moon':
        d.ellipse(P((18, 16), (84, 82)), fill=255)
        d.ellipse(P((38, 6), (100, 68)), fill=0)
    elif kind == 'drop':
        d.ellipse(P((26, 40), (74, 88)), fill=255)
        d.polygon(P((50, 8), (27, 56), (73, 56)), fill=255)
    elif kind == 'leaf':
        leaf = Image.new('L', (S, S), 0)
        ld = ImageDraw.Draw(leaf)
        ld.ellipse(P((30, 10), (70, 90)), fill=255)
        if fine:
            ld.line(P((50, 20), (50, 82)), fill=0, width=W(4))
        ld.line(P((50, 84), (50, 98)), fill=255, width=W(6))
        m = leaf.rotate(-35, resample=Image.BICUBIC, center=(S / 2, S / 2))
    elif kind == 'cup':
        d.rounded_rectangle(P((20, 36), (66, 76)), radius=10 * u, fill=255)
        d.ellipse(P((58, 42), (82, 66)), fill=255)
        d.ellipse(P((64, 48), (76, 60)), fill=0)
        d.ellipse(P((12, 74), (80, 86)), fill=255)
        for x in (34, 50):
            d.line(P((x, 30), (x - 3, 22), (x + 1, 12)), fill=255, width=W(5), joint='curve')
    elif kind == 'bean':
        bean = Image.new('L', (S, S), 0)
        bd = ImageDraw.Draw(bean)
        bd.ellipse(P((28, 14), (72, 86)), fill=255)
        bd.line(P((50, 20), (44, 40), (56, 60), (50, 80)), fill=0, width=W(6), joint='curve')
        m = bean.rotate(-30, resample=Image.BICUBIC)
    elif kind == 'chat':
        d.rounded_rectangle(P((12, 18), (88, 70)), radius=18 * u, fill=255)
        d.polygon(P((26, 64), (48, 64), (24, 88)), fill=255)
        if fine:
            for x in (32, 50, 68):
                d.ellipse(P((x - 5, 39), (x + 5, 49)), fill=0)
    elif kind == 'candy':
        d.ellipse(P((30, 30), (70, 70)), fill=255)
        d.polygon(P((32, 50), (8, 32), (12, 50), (8, 68)), fill=255)
        d.polygon(P((68, 50), (92, 32), (88, 50), (92, 68)), fill=255)
        if fine:
            d.line(P((40, 34), (58, 66)), fill=0, width=W(4))
    elif kind == 'lollipop':
        d.line(P((50, 56), (50, 96)), fill=255, width=W(7))
        d.ellipse(P((20, 6), (80, 66)), fill=255)
        if fine:
            d.arc(P((32, 18), (68, 54)), 0, 270, fill=0, width=W(5))
    elif kind == 'circle':
        d.ellipse(P((16, 16), (84, 84)), fill=255)
    elif kind == 'triangle':
        d.polygon(P((50, 12), (88, 82), (12, 82)), fill=255)
    elif kind == 'square':
        sq = Image.new('L', (S, S), 0)
        ImageDraw.Draw(sq).rounded_rectangle(P((22, 22), (78, 78)), radius=6 * u, fill=255)
        m = sq.rotate(15, resample=Image.BICUBIC)
    elif kind == 'pebble':
        d.ellipse(P((10, 50), (70, 86)), fill=255)
        d.ellipse(P((30, 24), (82, 54)), fill=255)
        d.ellipse(P((44, 8), (74, 26)), fill=255)
    elif kind == 'cloud':
        d.ellipse(P((10, 44), (46, 80)), fill=255)
        d.ellipse(P((28, 24), (70, 66)), fill=255)
        d.ellipse(P((54, 40), (90, 76)), fill=255)
        d.rectangle(P((28, 58), (72, 80)), fill=255)
    elif kind == 'ripple':
        for r, wd in ((8, 16), (24, 7), (40, 6)):
            d.ellipse(P((50 - r, 50 - r * 0.62), (50 + r, 50 + r * 0.62)), outline=255, width=W(wd))
    elif kind == 'blossom':
        for i in range(5):
            a = math.radians(-90 + i * 72)
            cx, cy = 50 + math.cos(a) * 22, 52 + math.sin(a) * 22
            d.ellipse(P((cx - 19, cy - 19), (cx + 19, cy + 19)), fill=255)
        if fine:
            d.ellipse(P((42, 44), (58, 60)), fill=0)
    elif kind == 'petal':
        pt = Image.new('L', (S, S), 0)
        pd = ImageDraw.Draw(pt)
        pd.ellipse(P((28, 14), (72, 90)), fill=255)
        pd.polygon(P((42, 14), (50, 26), (58, 14)), fill=0)
        m = pt.rotate(30, resample=Image.BICUBIC)
    elif kind == 'aurora':
        for i, y0 in enumerate((30, 52, 74)):
            pts = [(10 + j * 2, y0 + math.sin(j / 40 * math.pi * 1.6 + i) * 10 - j * 0.3) for j in range(41)]
            d.line(P(*pts), fill=255, width=W(10 - i * 2), joint='curve')
    elif kind == 'pine':
        for y0, hw in ((10, 18), (30, 28), (52, 38)):
            d.polygon(P((50, y0), (50 + hw, y0 + 32), (50 - hw, y0 + 32)), fill=255)
        d.rectangle(P((44, 84), (56, 96)), fill=255)
    elif kind == 'mountain':
        d.polygon(P((4, 84), (38, 26), (58, 56), (70, 40), (96, 84)), fill=255)
        if fine:
            d.polygon(P((38, 26), (30, 40), (38, 36), (46, 40)), fill=0)
    elif kind == 'wave':
        for y0 in (36, 62):
            pts = [(10 + i * 2, y0 + math.sin(i / 40 * 2 * math.pi * 1.5) * 8) for i in range(41)]
            d.line(P(*pts), fill=255, width=W(10), joint='curve')
    elif kind == 'fish':
        d.ellipse(P((8, 26), (72, 74)), fill=255)
        d.polygon(P((62, 50), (94, 24), (86, 50), (94, 76)), fill=255)
        if fine:
            d.ellipse(P((20, 40), (30, 50)), fill=0)
            d.arc(P((34, 32), (54, 68)), 300, 60, fill=0, width=W(4))
    elif kind == 'sun':
        d.ellipse(P((31, 31), (69, 69)), fill=255)
        for i in range(8):
            a = math.radians(i * 45)
            d.line(P((50 + math.cos(a) * 27, 50 + math.sin(a) * 27),
                     (50 + math.cos(a) * 42, 50 + math.sin(a) * 42)), fill=255, width=W(8))
    elif kind == 'mushroom':
        d.pieslice(P((10, 14), (90, 86)), 180, 360, fill=255)
        d.rounded_rectangle(P((36, 46), (64, 92)), radius=8 * u, fill=255)
        if fine:
            d.rectangle(P((10, 50), (90, 54)), fill=0)
            for x, y, r in ((32, 32, 6), (58, 26, 5), (72, 40, 4)):
                d.ellipse(P((x - r, y - r), (x + r, y + r)), fill=0)
    elif kind == 'snowflake':
        for i in range(6):
            a = math.radians(i * 60 - 90)
            x1, y1 = 50 + math.cos(a) * 40, 50 + math.sin(a) * 40
            d.line(P((50, 50), (x1, y1)), fill=255, width=W(7))
            for s in (-1, 1):
                b = a + s * math.radians(40)
                mx, my = 50 + math.cos(a) * 26, 50 + math.sin(a) * 26
                d.line(P((mx, my), (mx + math.cos(b) * 13, my + math.sin(b) * 13)), fill=255, width=W(6))
    elif kind == 'snowman':
        d.ellipse(P((22, 44), (78, 96)), fill=255)
        d.ellipse(P((32, 12), (68, 48)), fill=255)
        if fine:
            for x in (43, 57):
                d.ellipse(P((x - 3, 25), (x + 3, 31)), fill=0)
            for y in (60, 74):
                d.ellipse(P((47, y - 3), (53, y + 3)), fill=0)
    elif kind == 'mitten':
        mt = Image.new('L', (S, S), 0)
        md = ImageDraw.Draw(mt)
        md.rounded_rectangle(P((34, 12), (74, 74)), radius=20 * u, fill=255)
        md.ellipse(P((18, 34), (42, 58)), fill=255)
        md.polygon(P((26, 50), (40, 38), (44, 60)), fill=255)
        md.rounded_rectangle(P((32, 70), (76, 90)), radius=4 * u, fill=255)
        if fine:
            md.line(P((32, 72), (76, 72)), fill=0, width=W(4))
        m = mt.rotate(-12, resample=Image.BICUBIC)
    elif kind == 'building':
        d.rectangle(P((18, 34), (46, 88)), fill=255)
        d.rectangle(P((50, 14), (82, 88)), fill=255)
        for x0, x1, ys in (((23, 41, (42, 54, 66)), (55, 77, (22, 34, 46, 58, 70))) if fine else ()):
            for y in ys:
                d.rectangle(P((x0, y), ((x0 + x1) / 2 - 2, y + 6)), fill=0)
                d.rectangle(P(((x0 + x1) / 2 + 2, y), (x1, y + 6)), fill=0)
    elif kind == 'bolt':
        d.polygon(P((58, 6), (20, 56), (46, 56), (38, 94), (80, 40), (54, 40)), fill=255)
    elif kind == 'chip':
        d.rounded_rectangle(P((26, 26), (74, 74)), radius=6 * u, fill=255)
        for k in (36, 50, 64):
            for a, b in (((k, 10), (k, 26)), ((k, 74), (k, 90)), ((10, k), (26, k)), ((74, k), (90, k))):
                d.line(P(a, b), fill=255, width=W(6))
        if fine:
            d.rectangle(P((38, 38), (62, 62)), fill=0)
            d.rectangle(P((43, 43), (57, 57)), fill=255)
    elif kind == 'diamond':
        d.polygon(P((30, 20), (70, 20), (90, 42), (50, 90), (10, 42)), fill=255)
        if fine:
            d.line(P((10, 42), (90, 42)), fill=0, width=W(4))
            d.line(P((36, 42), (50, 86)), fill=0, width=W(3))
            d.line(P((64, 42), (50, 86)), fill=0, width=W(3))
    elif kind == 'flame':
        d.ellipse(P((22, 42), (78, 94)), fill=255)
        d.polygon(P((50, 4), (78, 64), (22, 64)), fill=255)
        d.polygon(P((24, 58), (30, 30), (44, 52)), fill=255)
        if fine:
            d.ellipse(P((38, 64), (62, 88)), fill=0)
            d.polygon(P((50, 44), (62, 76), (38, 76)), fill=0)
    elif kind == 'burst':
        d.ellipse(P((42, 42), (58, 58)), fill=255)
        for i in range(12):
            a = math.radians(i * 30)
            r0, r1 = (16, 44) if i % 2 == 0 else (18, 32)
            d.line(P((50 + math.cos(a) * r0, 50 + math.sin(a) * r0),
                     (50 + math.cos(a) * r1, 50 + math.sin(a) * r1)), fill=255, width=W(6))
            d.ellipse(P((50 + math.cos(a) * r1 - 4, 50 + math.sin(a) * r1 - 4),
                        (50 + math.cos(a) * r1 + 4, 50 + math.sin(a) * r1 + 4)), fill=255)
    elif kind == 'comet':
        d.ellipse(P((56, 14), (86, 44)), fill=255)
        d.polygon(P((60, 40), (82, 18), (18, 82)), fill=255)
        d.polygon(P((56, 26), (68, 18), (26, 60)), fill=255)
    elif kind == 'lantern':
        d.ellipse(P((18, 22), (82, 86)), fill=255)
        d.rectangle(P((36, 14), (64, 26)), fill=255)
        d.rectangle(P((36, 82), (64, 90)), fill=255)
        d.line(P((50, 2), (50, 16)), fill=255, width=W(4))
        d.line(P((50, 88), (50, 98)), fill=255, width=W(5))
        if fine:
            d.arc(P((34, 22), (66, 86)), 0, 360, fill=0, width=W(4))
    elif kind == 'lotus':
        d.ellipse(P((36, 20), (64, 78)), fill=255)
        for s in (-1, 1):
            pl = Image.new('L', (S, S), 0)
            ImageDraw.Draw(pl).ellipse(P((38, 28), (62, 80)), fill=255)
            pl = pl.rotate(-s * 38, resample=Image.BICUBIC, center=(50 * u, 80 * u))
            m = ImageChops.lighter(m, pl)
        d = ImageDraw.Draw(m)
        d.ellipse(P((14, 72), (86, 90)), fill=255)
    elif kind == 'bulb':
        d.ellipse(P((24, 10), (76, 62)), fill=255)
        d.polygon(P((32, 50), (68, 50), (62, 72), (38, 72)), fill=255)
        d.rounded_rectangle(P((38, 72), (62, 90)), radius=3 * u, fill=255)
        if fine:
            for y in (77, 84):
                d.line(P((38, y), (62, y)), fill=0, width=W(3))
    elif kind == 'garland':
        d.arc(P((-6, -34), (106, 46)), 25, 155, fill=255, width=W(4))
        for x, y in ((18, 26), (50, 42), (82, 26)):
            d.rectangle(P((x - 4, y), (x + 4, y + 10)), fill=255)
            d.ellipse(P((x - 9, y + 8), (x + 9, y + 34)), fill=255)
    elif kind == 'car':
        d.rounded_rectangle(P((8, 44), (92, 74)), radius=10 * u, fill=255)
        d.polygon(P((24, 46), (34, 24), (66, 24), (78, 46)), fill=255)
        for x in (28, 72):
            d.ellipse(P((x - 12, 62), (x + 12, 86)), fill=255)
        if fine:
            d.polygon(P((32, 44), (38, 30), (48, 30), (48, 44)), fill=0)
            d.polygon(P((54, 44), (54, 30), (63, 30), (70, 44)), fill=0)
            for x in (28, 72):
                d.ellipse(P((x - 5, 69), (x + 5, 79)), fill=0)
    elif kind == 'signal':
        d.rounded_rectangle(P((30, 6), (70, 94)), radius=12 * u, fill=255)
        for y in (22, 50, 78):
            d.ellipse(P((39, y - 11), (61, y + 11)), fill=0)
    elif kind == 'sign':
        d.rectangle(P((46, 50), (54, 96)), fill=255)
        d.polygon(P((50, 6), (88, 44), (50, 82), (12, 44)), fill=255)
        if fine:
            d.polygon(P((50, 22), (60, 36), (54, 36), (54, 58), (46, 58), (46, 36), (40, 36)), fill=0)
    elif kind == 'prompt':
        d.line(P((16, 28), (42, 50), (16, 72)), fill=255, width=W(12), joint='curve')
        d.rectangle(P((50, 66), (86, 78)), fill=255)
    elif kind == 'code':
        d.line(P((34, 24), (12, 50), (34, 76)), fill=255, width=W(10), joint='curve')
        d.line(P((66, 24), (88, 50), (66, 76)), fill=255, width=W(10), joint='curve')
        d.line(P((57, 18), (43, 82)), fill=255, width=W(9))
    elif kind == 'monitor':
        d.rounded_rectangle(P((8, 14), (92, 70)), radius=6 * u, fill=255)
        d.rectangle(P((42, 70), (58, 84)), fill=255)
        d.rounded_rectangle(P((26, 82), (74, 90)), radius=3 * u, fill=255)
        if fine:
            d.rectangle(P((16, 22), (84, 62)), fill=0)
            d.line(P((24, 32), (34, 40), (24, 48)), fill=255, width=W(5))
            d.rectangle(P((40, 46), (56, 51)), fill=255)
    else:
        raise ValueError('모르는 모티프: %s' % kind)
    return m


def profile(t, idx, px):
    """계열 모티프 한 장. 바탕은 판 색 셋을 돌려 쓰고 도형은 포인트색 셋을 돌려 쓴다."""
    if t['family'] not in MOTIFS:
        raise SystemExit('%s: 기본 프로필 모티프가 없다 — tools/motif.py 의 MOTIFS 에 한 줄 쓴다'
                         % t['family'])
    S = px * SS
    light = themes._bg_is_light(t)
    glow = bool(t.get('glow'))
    tube = glow and not light
    kind = MOTIFS[t['family']][idx % 3]
    back = (t['surface'], t['pressed'], t['bg_deep'])[idx % 3]
    col = legible((t['accent'], gen.mid(*t['send']), t['accent_dim'])[idx % 3], back, t['text'])

    img = Image.new('RGBA', (S, S), gen.rgb(back) + (255,))
    small = mask(kind, S, fine=not tube or kind in KEEP_HOLES).resize((int(S * 0.7), int(S * 0.7)), Image.LANCZOS)
    m = Image.new('L', (S, S), 0)
    m.paste(small, (int(S * 0.15), int(S * 0.15)))
    if tube:
        k = max(1, int(S * 0.045))
        pipe = ImageChops.subtract(m, erode(m, k))
        _put(img, col, pipe.filter(ImageFilter.GaussianBlur(S * 0.05)).point(lambda v: min(255, v * 2)))
        _put(img, col, pipe)
        _put(img, gen.glow_tint(col, 0.75), erode(pipe, max(1, k // 3)))
    else:
        if glow:
            _put(img, col, m.filter(ImageFilter.GaussianBlur(S * 0.06)).point(lambda v: v * 150 // 255))
        _put(img, col, m)
    return img.resize((px, px), Image.LANCZOS)


# --- 유리구슬 --------------------------------------------------------------

_BACK = {}


def _backdrop(t, S):
    """구슬 뒤에 깔 그림. 배경이 없는 단색 변형은 판 색 그라데이션에 말풍선 색 번짐을 얹는다."""
    if t['key'] not in _BACK:
        spec = t.get('main_bg') or t.get('chat_bg')
        if spec and spec[0] != 'linear':
            img = gen.background(t, spec, 300, 650, flat=False).convert('RGB')
        else:
            img = gen.vgradient(300, 650, gen.rgb(t['surface']), gen.rgb(t['bg_deep'])).convert('RGBA')
            d = ImageDraw.Draw(img)
            for (cx, cy), c in zip(((70, 150), (240, 330), (90, 520)),
                                   (gen.mid(*t['send']), gen.mid(*t['recv']), gen.mid(*t['send_alt']))):
                d.ellipse([cx - 120, cy - 120, cx + 120, cy + 120], fill=gen.rgb(c) + (120,))
            img = img.filter(ImageFilter.GaussianBlur(50)).convert('RGB')
        _BACK[t['key']] = img
    return _BACK[t['key']]


def marble(t, idx, px):
    """배경 위에 놓인 유리구슬. 구슬 안에는 뒤 그림이 확대돼 거꾸로 비친다.

    채팅방 유리 말풍선과 같은 문법으로 테를 두른다 — 위는 흰 테, 아래는 어두운 테. 가장자리
    안쪽은 짙게(유리가 두꺼워 보이는 자리), 왼쪽 위에 반사, 아래에 굴절돼 모인 빛. 세 장은 같은
    구슬이고 뒤 그림을 자르는 자리만 달라서 색이 다르게 나온다.
    """
    S = px * SS
    light = themes._bg_is_light(t)
    y = 40 + idx % 3 * 150                    # 뒤 그림 높이 650 안에서 300 씩 자른다
    back = _backdrop(t, S).crop((0, y, 300, y + 300)).resize((S, S), Image.LANCZOS)
    img = back.convert('RGBA')

    r = S * 0.30
    ball = Image.new('L', (S, S), 0)
    ImageDraw.Draw(ball).ellipse([S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r], fill=255)

    sh = Image.new('L', (S, S), 0)
    sh.paste(ball, (int(S * 0.03), int(S * 0.06)))
    _put(img, gen.mix(t['accent_dim'], '#000000', 0.5),
         sh.filter(ImageFilter.GaussianBlur(S * 0.04)).point(lambda v: v * 70 // 255))

    w = int(S / 1.9)
    ref = back.crop((S // 2 - w // 2, S // 2 - w // 2, S // 2 + w // 2, S // 2 + w // 2))
    img.paste(ref.resize((S, S), Image.LANCZOS).transpose(Image.ROTATE_180).convert('RGBA'), (0, 0), ball)

    edge = ImageChops.subtract(ball, erode(ball, int(S * 0.045))).filter(ImageFilter.GaussianBlur(S * 0.03))
    _put(img, gen.mix(t['accent_dim'], '#000000', 0.2) if light else '#000000',
         ImageChops.multiply(edge, ball).point(lambda v: v * (120 if light else 170) // 255))

    rim = ImageChops.subtract(ball, erode(ball, max(1, int(S * 0.012))))
    ramp = Image.linear_gradient('L').resize((S, S))
    top = ramp.point(lambda v: int(255 * max(0.0, 1 - v / 255 * 1.6)))
    bottom = ramp.point(lambda v: int(255 * max(0.0, (v / 255 - 0.45) * 1.8)))
    _put(img, '#FFFFFF', ImageChops.multiply(rim, top).point(lambda v: v * 240 // 255))
    _put(img, '#000000', ImageChops.multiply(rim, bottom).point(lambda v: v * (90 if light else 140) // 255))

    spot = Image.new('L', (S, S), 0)
    ImageDraw.Draw(spot).ellipse([S * 0.33, S * 0.27, S * 0.47, S * 0.37], fill=230)
    _put(img, '#FFFFFF', spot.filter(ImageFilter.GaussianBlur(S * 0.012)))
    pool = Image.new('L', (S, S), 0)
    ImageDraw.Draw(pool).ellipse([S * 0.36, S * 0.62, S * 0.66, S * 0.78], fill=150)
    _put(img, gen.glow_tint(t['accent'], 0.7),
         ImageChops.multiply(ball, pool.filter(ImageFilter.GaussianBlur(S * 0.03))))
    return img.resize((px, px), Image.LANCZOS)
