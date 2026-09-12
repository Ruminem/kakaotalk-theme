# -*- coding: utf-8 -*-
"""배경으로 쓰는 그림들.

사진을 가져다 쓸 수 없으니(저작권) 전부 코드로 그린다.
시드를 고정한다 — 안 그러면 빌드할 때마다 그림이 바뀌어 diff 가 매번 더러워진다.

gen.chat_bg 가 종류를 보고 여기로 넘긴다. 밤하늘(night)은 gen 에 남아 있다.
"""
import math
import os
import random
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _g():
    """gen 을 늦게 불러온다. gen 이 이 모듈을 부르므로 위에서 import 하면 순환한다."""
    import gen
    return gen


def _soft_blob(r, rgba, blur, cx, cy):
    """흐린 원 하나와 붙일 위치.

    흐림 반경만큼 캔버스를 넉넉히 잡는다. 도형 크기에 딱 맞춰 흐리면 가장자리에서
    잘려서 네모가 남는다 — 글로우에서 겪은 것과 같은 문제다.
    """
    pad = int(blur * 3) + 2
    S = int(r * 2) + pad * 2
    lay = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([pad, pad, S - pad - 1, S - pad - 1], fill=rgba)
    lay = lay.filter(ImageFilter.GaussianBlur(blur))
    return lay, (int(cx - S / 2), int(cy - S / 2))


# --- 사탕 ---------------------------------------------------------------

def _lollipop(r, c1, c2):
    """소용돌이 사탕 한 알. 부채꼴을 번갈아 그려 소용돌이처럼 보이게 한다."""
    gen = _g()
    ss = 3
    S = r * 2 * ss
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, S - 1, S - 1], fill=gen.rgb(c1) + (255,))
    for k in range(6):
        d.pieslice([0, 0, S - 1, S - 1], k * 60, k * 60 + 30,
                   fill=gen.rgb(c2) + (255,))
    for k, f in ((1, 0.62), (2, 0.34)):
        col = c2 if k % 2 else c1
        m = S * (1 - f) / 2
        d.ellipse([m, m, S - m, S - m], fill=gen.rgb(col) + (255,))
    d.ellipse([S * 0.18, S * 0.12, S * 0.52, S * 0.36], fill=(255, 255, 255, 95))
    return img.resize((r * 2, r * 2), Image.LANCZOS)


def _wrapped(w, h, c1, c2):
    """포장 사탕. 가운데 몸통에 양쪽으로 포장지가 접힌 모양."""
    gen = _g()
    ss = 3
    W, H = w * ss, h * ss
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bw = int(W * 0.52)
    x0 = (W - bw) // 2
    d.rounded_rectangle([x0, 0, x0 + bw, H - 1], radius=int(H * 0.42),
                        fill=gen.rgb(c1) + (255,))
    for k in range(3):
        y = H * (0.24 + k * 0.26)
        d.line([(x0 + W * 0.03, y), (x0 + bw - W * 0.03, y)],
               fill=gen.rgb(c2) + (255,), width=max(2, int(H * 0.10)))
    for sx in (0, W):
        sgn = 1 if sx == 0 else -1
        d.polygon([(sx, H * 0.12), (sx + sgn * W * 0.24, H * 0.5),
                   (sx, H * 0.88)], fill=gen.rgb(c2) + (255,))
    d.ellipse([x0 + bw * 0.15, H * 0.10, x0 + bw * 0.55, H * 0.34],
              fill=(255, 255, 255, 85))
    return img.resize((w, h), Image.LANCZOS)


def candy(spec, w, h):
    """사탕이 흩뿌려진 배경. spec = ('candy', 위색, 아래색, 옵션dict)"""
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2])).convert('RGBA')
    pal = o.get('colors', ['#FF7AA2', '#FFC24D', '#7ED7C1', '#9BD6FF', '#C2A7FF'])
    rnd = random.Random(20260913)
    unit = w / 500.0

    for _ in range(o.get('count', 26)):
        x, y = rnd.random() * w, rnd.random() * h
        c1, c2 = rnd.sample(pal, 2)
        size = rnd.uniform(16, 34) * unit

        img.alpha_composite(*_soft_blob(size * 0.85, (120, 90, 70, 50), size * 0.22,
                                        x, y + size * 0.14))

        if rnd.random() < 0.55:
            piece = _lollipop(int(size), c1, c2)
        else:
            piece = _wrapped(int(size * 1.9), int(size), c1, c2)
        piece = piece.rotate(rnd.uniform(0, 360), expand=True, resample=Image.BICUBIC)
        img.alpha_composite(piece, (int(x - piece.size[0] / 2),
                                    int(y - piece.size[1] / 2)))

    d = ImageDraw.Draw(img)
    for _ in range(o.get('sprinkles', 90)):
        x, y = rnd.random() * w, rnd.random() * h
        r = rnd.uniform(1.2, 3.0) * unit
        d.ellipse([x - r, y - r, x + r, y + r], fill=gen.rgb(rnd.choice(pal)) + (150,))

    img = img.convert('RGB')
    dim = o.get('dim', 0.0)
    if dim:
        img = Image.blend(img, Image.new('RGB', (w, h), (255, 255, 255)), dim)
    return img


# --- 벚꽃 ---------------------------------------------------------------

def _blossom(r, c_petal, c_core):
    """벚꽃 한 송이. 꽃잎 다섯 장을 72도씩 돌려 붙인다."""
    gen = _g()
    ss = 3
    S = r * 2 * ss
    pw, ph = int(r * 0.80 * ss), int(r * 0.98 * ss)
    petal = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(petal)
    cx, cy = S // 2, S // 2
    pd.ellipse([cx - pw // 2, cy - ph, cx + pw // 2, cy],
               fill=gen.rgb(c_petal) + (255,))
    pd.ellipse([cx - pw * 0.24, cy - ph - pw * 0.20,
                cx + pw * 0.24, cy - ph + pw * 0.26], fill=(0, 0, 0, 0))

    out = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    for k in range(5):
        out.alpha_composite(petal.rotate(k * 72, resample=Image.BICUBIC,
                                         center=(cx, cy)))
    cr = S * 0.085
    ImageDraw.Draw(out).ellipse([cx - cr, cy - cr, cx + cr, cy + cr],
                                fill=gen.rgb(c_core) + (255,))
    return out.resize((r * 2, r * 2), Image.LANCZOS)


def sakura(spec, w, h):
    """벚꽃. 가지와 꽃송이, 떨어지는 꽃잎. spec = ('sakura', 위색, 아래색, 옵션dict)"""
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2])).convert('RGBA')
    petal_c = o.get('petal', '#FFB7CE')
    deep_c = o.get('deep', '#F58AB0')
    core_c = o.get('core', '#FFE1A0')
    rnd = random.Random(20260914)
    unit = w / 500.0

    for _ in range(o.get('bokeh', 16)):
        x, y = rnd.random() * w, rnd.random() * h
        r = rnd.uniform(18, 52) * unit
        img.alpha_composite(*_soft_blob(r, gen.rgb(petal_c) + (52,), r * 0.45, x, y))

    if o.get('branch', True):
        d = ImageDraw.Draw(img)
        bc = gen.rgb(o.get('branch_color', '#6B4A55'))

        def limb(x0, y0, x1, y1, w0, w1, depth):
            # 굵기가 줄어드는 사각형으로 그린다. 일정한 굵기의 선은 낙서처럼 보인다
            ang = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
            ox, oy = math.cos(ang), math.sin(ang)
            d.polygon([(x0 + ox * w0, y0 + oy * w0), (x1 + ox * w1, y1 + oy * w1),
                       (x1 - ox * w1, y1 - oy * w1), (x0 - ox * w0, y0 - oy * w0)],
                      fill=bc + (255,))
            d.ellipse([x1 - w1, y1 - w1, x1 + w1, y1 + w1], fill=bc + (255,))
            if depth == 0:
                return
            for _ in range(2):
                a = math.atan2(y1 - y0, x1 - x0) + rnd.uniform(-0.75, 0.75)
                ln = math.hypot(x1 - x0, y1 - y0) * rnd.uniform(0.45, 0.7)
                limb(x1, y1, x1 + math.cos(a) * ln, y1 + math.sin(a) * ln,
                     w1, w1 * 0.55, depth - 1)

        # 왼쪽 위 모서리에만 물린다. 길게 뻗으면 화면 글자를 가로지른다
        limb(-w * 0.05, h * 0.01, w * 0.20, h * 0.10, 7 * unit, 4 * unit, 2)

    for _ in range(o.get('flowers', 26)):
        near = rnd.random() < 0.7
        x = rnd.uniform(0, w * 0.45) if near else rnd.random() * w
        y = rnd.uniform(0, h * 0.22) if near else rnd.random() * h
        r = int(rnd.uniform(9, 20) * unit)
        c = petal_c if rnd.random() < 0.7 else deep_c
        fl = _blossom(r, c, core_c).rotate(rnd.uniform(0, 72), resample=Image.BICUBIC)
        img.alpha_composite(fl, (int(x - r), int(y - r)))

    for _ in range(o.get('petals', 40)):
        x, y = rnd.random() * w, rnd.random() * h
        pw2 = max(2, int(rnd.uniform(5, 11) * unit))
        ph2 = int(pw2 * 1.35)
        lay = Image.new('RGBA', (pw2, ph2), (0, 0, 0, 0))
        ImageDraw.Draw(lay).ellipse([0, 0, pw2 - 1, ph2 - 1],
                                    fill=gen.rgb(petal_c) + (rnd.randint(110, 210),))
        img.alpha_composite(lay.rotate(rnd.uniform(0, 360), expand=True,
                                       resample=Image.BICUBIC), (int(x), int(y)))

    img = img.convert('RGB')
    dim = o.get('dim', 0.0)
    if dim:
        img = Image.blend(img, Image.new('RGB', (w, h), (255, 255, 255)), dim)
    return img


# --- 바다 ---------------------------------------------------------------

def sea(spec, w, h):
    """수평선과 물결. spec = ('sea', 하늘위, 하늘아래, 옵션dict)"""
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(20260915)
    unit = w / 500.0
    hz = int(h * o.get('horizon', 0.46))

    img = gen.vgradient(w, hz, gen.rgb(spec[1]), gen.rgb(spec[2])).convert('RGBA')
    full = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    full.alpha_composite(img)

    # 해
    sun_c = o.get('sun', '#FFD9A0')
    sx, sy, sr = w * o.get('sun_x', 0.7), hz * o.get('sun_y', 0.55), w * 0.075
    full.alpha_composite(*_soft_blob(sr * 3.2, gen.rgb(sun_c) + (60,), sr * 1.1, sx, sy))
    ImageDraw.Draw(full).ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                                 fill=gen.rgb(sun_c) + (255,))

    water = gen.vgradient(w, h - hz, gen.rgb(o.get('water_top', '#2E5F7A')),
                          gen.rgb(o.get('water_bottom', '#12293A'))).convert('RGBA')
    full.alpha_composite(water, (0, hz))

    d = ImageDraw.Draw(full)
    # 물결. 아래로 갈수록 굵고 성기게
    for i in range(o.get('waves', 60)):
        t = rnd.random()
        y = hz + (h - hz) * (t ** 1.5)
        ln = rnd.uniform(0.05, 0.22) * w * (0.5 + t)
        x = rnd.random() * w
        a = int(70 + 90 * (1 - t))
        d.line([(x, y), (x + ln, y)], fill=(255, 255, 255, a),
               width=max(1, int((1 + t * 2.2) * unit)))
    # 해가 비친 길
    for i in range(26):
        t = i / 25
        y = hz + (h - hz) * (t ** 1.6)
        ln = w * (0.03 + 0.10 * t) * rnd.uniform(0.5, 1.3)
        d.line([(sx - ln / 2, y), (sx + ln / 2, y)],
               fill=gen.rgb(sun_c) + (int(120 * (1 - t)),),
               width=max(1, int((1 + t * 2) * unit)))

    img = full.convert('RGB')
    dim = o.get('dim', 0.0)
    if dim:
        img = Image.blend(img, Image.new('RGB', (w, h), o.get('dim_to', (0, 0, 0))), dim)
    return img


# --- 숲 -----------------------------------------------------------------

def forest(spec, w, h):
    """겹쳐진 나무 실루엣과 안개. spec = ('forest', 위색, 아래색, 옵션dict)"""
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(20260916)
    unit = w / 500.0
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2])).convert('RGBA')

    layers = o.get('layers', ['#1E3A2E', '#27503E', '#33654D', '#3F7A5C'])
    for li, col in enumerate(layers):
        t = li / max(len(layers) - 1, 1)
        base_y = h * (0.42 + 0.16 * t)
        d = ImageDraw.Draw(img)
        x = -w * 0.05
        while x < w * 1.05:
            tw = rnd.uniform(0.05, 0.11) * w * (0.7 + t * 0.8)
            th = rnd.uniform(0.9, 1.5) * tw * 3.2
            top = base_y - th
            # 침엽수: 삼각형 세 겹
            for k in range(3):
                f = 1 - k * 0.24
                cy = top + th * (0.18 + k * 0.26)
                d.polygon([(x + tw / 2, top + th * k * 0.22),
                           (x + tw * (0.5 - 0.62 * f), cy + th * 0.30),
                           (x + tw * (0.5 + 0.62 * f), cy + th * 0.30)],
                          fill=gen.rgb(col) + (255,))
            d.rectangle([x + tw * 0.45, base_y - th * 0.08, x + tw * 0.55, base_y + 2],
                        fill=gen.rgb(col) + (255,))
            x += tw * rnd.uniform(0.55, 0.95)
        # 층 사이에 안개를 끼워 원근을 만든다
        if li < len(layers) - 1:
            fog = Image.new('RGBA', (w, h), gen.rgb(o.get('fog', '#DCE9E2')) + (0,))
            fd = ImageDraw.Draw(fog)
            band = int(h * 0.14)
            for i in range(band):
                fd.line([(0, base_y - band + i), (w, base_y - band + i)],
                        fill=gen.rgb(o.get('fog', '#DCE9E2')) + (int(60 * (i / band)),))
            img.alpha_composite(fog.filter(ImageFilter.GaussianBlur(w * 0.02)))

    img = img.convert('RGB')
    dim = o.get('dim', 0.0)
    if dim:
        img = Image.blend(img, Image.new('RGB', (w, h), o.get('dim_to', (0, 0, 0))), dim)
    return img


# --- 도시 ---------------------------------------------------------------

def city(spec, w, h):
    """건물 실루엣과 창문 불빛. spec = ('city', 하늘위, 하늘아래, 옵션dict)"""
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(20260917)
    unit = w / 500.0
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2])).convert('RGBA')

    win_c = gen.rgb(o.get('window', '#FFD98A'))
    for li, (col, base, wf) in enumerate(o.get('layers', [
            ('#1A2238', 0.62, 0.9), ('#121829', 0.74, 1.0), ('#0B0F1C', 0.86, 1.1)])):
        d = ImageDraw.Draw(img)
        x = -w * 0.04
        base_y = h * base
        while x < w * 1.04:
            bw = rnd.uniform(0.06, 0.14) * w * wf
            bh = rnd.uniform(0.10, 0.34) * h
            top = base_y - bh
            d.rectangle([x, top, x + bw, h], fill=gen.rgb(col) + (255,))
            if li >= 1:                      # 앞줄 건물에만 창문
                cols = max(2, int(bw / (11 * unit)))
                rows = max(2, int(bh / (15 * unit)))
                for cx in range(cols):
                    for cy in range(rows):
                        if rnd.random() > o.get('lit', 0.34):
                            continue
                        px = x + bw * (cx + 0.28) / cols
                        py = top + bh * (cy + 0.32) / rows
                        d.rectangle([px, py, px + 4 * unit, py + 6 * unit],
                                    fill=win_c + (rnd.randint(120, 235),))
            x += bw * rnd.uniform(1.02, 1.3)

    img = img.convert('RGB')
    dim = o.get('dim', 0.0)
    if dim:
        img = Image.blend(img, Image.new('RGB', (w, h), o.get('dim_to', (0, 0, 0))), dim)
    return img


# --- 눈 -----------------------------------------------------------------

def snow(spec, w, h):
    """내리는 눈과 언덕. spec = ('snow', 위색, 아래색, 옵션dict)"""
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(20260918)
    unit = w / 500.0
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2])).convert('RGBA')

    for base, col in o.get('hills', [(0.72, '#E8EEF6'), (0.82, '#F3F7FC')]):
        prof = gen._fbm(int(base * 100), 200)
        pts = [(0, h)]
        for i in range(200):
            pts.append((w * i / 199, h * base + prof[i] * h * 0.045))
        pts.append((w, h))
        ImageDraw.Draw(img).polygon(pts, fill=gen.rgb(col) + (255,))

    d = ImageDraw.Draw(img)
    for _ in range(o.get('flakes', 260)):
        x, y = rnd.random() * w, rnd.random() * h
        r = rnd.uniform(1.0, 3.4) * unit
        a = rnd.randint(90, 240)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))
        if r > 2.6 * unit:                   # 큰 눈송이는 살짝 흐리게
            img.alpha_composite(*_soft_blob(r * 2.2, (255, 255, 255, 40), r, x, y))

    img = img.convert('RGB')
    dim = o.get('dim', 0.0)
    if dim:
        img = Image.blend(img, Image.new('RGB', (w, h), o.get('dim_to', (255, 255, 255))), dim)
    return img


# --- 도형 ---------------------------------------------------------------

def geo(spec, w, h):
    """큰 도형 몇 개를 겹친 배경. 그림이라기보다 무늬에 가깝다.

    spec = ('geo', 위색, 아래색, 옵션dict)
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(20260919)
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2])).convert('RGBA')
    pal = o.get('colors', ['#FF8A5B', '#5BE0B4', '#7C6BE0'])

    for _ in range(o.get('count', 9)):
        c = gen.rgb(rnd.choice(pal))
        a = rnd.randint(o.get('alpha_lo', 26), o.get('alpha_hi', 64))
        r = rnd.uniform(0.14, 0.42) * w
        x, y = rnd.uniform(-0.1, 1.1) * w, rnd.uniform(-0.05, 1.05) * h
        lay = Image.new('RGBA', (int(r * 2), int(r * 2)), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        kind = rnd.random()
        if kind < 0.45:
            ld.ellipse([0, 0, r * 2 - 1, r * 2 - 1], fill=c + (a,))
        elif kind < 0.8:
            ld.rounded_rectangle([0, 0, r * 2 - 1, r * 2 - 1],
                                 radius=int(r * 0.3), fill=c + (a,))
        else:
            ld.polygon([(r, 0), (r * 2 - 1, r * 1.8), (0, r * 1.8)], fill=c + (a,))
        lay = lay.rotate(rnd.uniform(0, 360), expand=True, resample=Image.BICUBIC)
        img.alpha_composite(lay, (int(x - lay.size[0] / 2), int(y - lay.size[1] / 2)))

    if o.get('blur', 0):
        img = img.filter(ImageFilter.GaussianBlur(w * o['blur']))
    img = img.convert('RGB')
    dim = o.get('dim', 0.0)
    if dim:
        img = Image.blend(img, Image.new('RGB', (w, h), o.get('dim_to', (255, 255, 255))), dim)
    return img
