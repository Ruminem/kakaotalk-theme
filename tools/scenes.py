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

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

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
    rnd = random.Random(o.get('seed', 20260913))
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
    rnd = random.Random(o.get('seed', 20260914))
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
    rnd = random.Random(o.get('seed', 20260915))
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
    rnd = random.Random(o.get('seed', 20260916))
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
    rnd = random.Random(o.get('seed', 20260917))
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
    rnd = random.Random(o.get('seed', 20260918))
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
    rnd = random.Random(o.get('seed', 20260919))
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


# --- 네온 격자 ------------------------------------------------------------

def neon(spec, w, h):
    """지평선까지 뻗은 네온 격자. 사이버펑크의 그 바닥이다.

    spec = ('neon', 하늘 위색, 하늘 아래색, 옵션dict)
      horizon  지평선 높이 0~1
      grid     격자 색
      glow     해와 안개 색
      sun      해 색. None 이면 안 그림
      rows     가로줄 수, cols 세로줄 수
      dim      0~1. 클수록 어둡게 덮는다

    격자는 두 번 그린다. 한 벌은 크게 흐려서 빛으로 깔고, 그 위에 또렷한 선을 얹는다.
    한 겹만 그리면 선이 가늘어서 네온이 아니라 모눈종이가 된다.
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(o.get('seed', 20260920))
    hz = int(h * o.get('horizon', 0.52))
    img = gen.vgradient(w, hz, gen.rgb(spec[1]), gen.rgb(spec[2])).convert('RGBA')
    img = img.resize((w, hz))
    full = Image.new('RGBA', (w, h), gen.rgb(o.get('ground', '#0A0514')) + (255,))
    full.paste(img, (0, 0))

    glow_c = gen.rgb(o.get('glow', '#FF2E88'))
    grid_c = gen.rgb(o.get('grid', '#31E8FF'))

    # 해. 위아래 색이 다르고 가로로 잘린 원 — 레트로웨이브의 그 모양이다.
    # 지평선 아래로는 안 넘긴다. 격자가 해를 가로지르면 바닥에 박힌 것처럼 보인다.
    if o.get('sun'):
        sr = int(w * o.get('sun_r', 0.27))
        top_c, bot_c = o['sun'], o.get('sun_bottom', o['sun'])
        disc = gen.vgradient(sr * 2, sr * 2, gen.rgb(top_c), gen.rgb(bot_c)).convert('RGBA')
        m = Image.new('L', (sr * 2, sr * 2), 0)
        ImageDraw.Draw(m).ellipse([0, 0, sr * 2 - 1, sr * 2 - 1], fill=255)
        md = ImageDraw.Draw(m)
        for i in range(8):                      # 아래로 갈수록 굵어지는 틈
            y = int(sr * (0.90 + i * 0.13))
            md.rectangle([0, y, sr * 2, y + 1 + i], fill=0)
        disc.putalpha(m)
        cx, cy = int(w * o.get('sun_x', 0.5)), int(hz - sr * 0.62)
        bloom, at = _soft_blob(sr * 1.3, glow_c + (170,), w * 0.10, cx, cy)
        full.alpha_composite(bloom, at)
        sun_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        sun_layer.alpha_composite(disc, (cx - sr, cy - sr))
        sun_layer = sun_layer.crop((0, 0, w, hz)).convert('RGBA')
        full.alpha_composite(sun_layer, (0, 0))

    # 격자. 소실점은 지평선 한가운데다
    grid = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    vx, vy = w * 0.5, float(hz)
    cols = o.get('cols', 17)
    for i in range(cols + 1):
        t = i / cols
        x = -w * 1.6 + (w * 4.2) * t
        gd.line([(vx, vy), (x, h)], fill=grid_c + (190,), width=2)
    rows = o.get('rows', 15)
    for i in range(1, rows + 1):
        t = i / rows
        y = vy + (h - vy) * (t ** 2.3)          # 멀수록 촘촘하게
        gd.line([(0, y), (w, y)], fill=grid_c + (190,), width=2)

    # 빛은 두 겹으로 깐다. 가까운 쪽은 진하게, 먼 쪽은 넓게 퍼지게
    full.alpha_composite(grid.filter(ImageFilter.GaussianBlur(w * 0.05)))
    full.alpha_composite(grid.filter(ImageFilter.GaussianBlur(w * 0.015)))
    full.alpha_composite(grid)

    # 지평선의 안개. 바닥과 하늘이 맞닿은 자리를 흐린다
    haze = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    hd.rectangle([0, hz - int(h * 0.03), w, hz + int(h * 0.03)], fill=glow_c + (110,))
    haze = haze.filter(ImageFilter.GaussianBlur(h * 0.035))
    full.alpha_composite(haze)

    # 별 몇 개. 하늘이 비어 있으면 격자만 동동 떠 보인다
    sd = ImageDraw.Draw(full, 'RGBA')
    for _ in range(o.get('stars', 70)):
        x, y = rnd.random() * w, rnd.random() * hz * 0.85
        r = rnd.choice((0.6, 0.8, 1.1))
        a = rnd.randint(60, 170)
        sd.ellipse([x - r, y - r, x + r, y + r], fill=(235, 235, 255, a))

    img = full.convert('RGB')
    dim = o.get('dim', 0.0)
    if dim:
        img = Image.blend(img, Image.new('RGB', (w, h), (0, 0, 0)), dim)
    return img


# --- 캐릭터 테마의 장면 --------------------------------------------------
# 우체국·책상·오락실·빨래. 밝음과 어두움이 같은 함수를 색만 바꿔 쓴다.
# dim 은 dim_to 쪽으로 섞는다 — 밝은 테마는 흰 쪽, 어두운 테마는 검은 쪽으로 눌러야
# 말풍선 뒤가 조용해진다. 한쪽으로만 누르면 밝은 테마가 잿빛이 된다.

def _dim(img, o):
    gen = _g()
    img = img.convert('RGB')
    dim = o.get('dim', 0.0)
    if dim:
        to = gen.rgb(o.get('dim_to', '#000000'))
        img = Image.blend(img, Image.new('RGB', img.size, to), dim)
    return img


def _drop(img, piece, x, y, off, blur, alpha):
    """조각을 그림자와 함께 가운데 (x, y) 에 얹는다. 그림자는 조각의 알파를 흐려 만든다."""
    pad = int(blur * 3) + 2
    a = Image.new('L', (piece.width + pad * 2, piece.height + pad * 2), 0)
    a.paste(piece.getchannel('A').point(lambda v: v * alpha // 255), (pad, pad))
    sh = Image.new('RGBA', a.size, (0, 0, 0, 255))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(blur)))
    x0, y0 = int(x - piece.width / 2), int(y - piece.height / 2)
    img.alpha_composite(sh, (x0 - pad + int(off), y0 - pad + int(off * 1.6)))
    img.alpha_composite(piece, (x0, y0))


def _envelope(ew, eh, fill, ink, stamp, ss=3):
    """편지봉투 한 장. 뒷면 삼각 날개와 우표, 소인 물결."""
    W, H, o = int(ew * ss), int(eh * ss), 2 * ss
    img = Image.new('RGBA', (W + o * 2, H + o * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lw = max(ss, int(W * 0.014))
    d.rounded_rectangle([o, o, o + W, o + H], radius=int(W * 0.04), fill=fill + (255,),
                        outline=ink + (255,), width=lw)
    d.line([(o + lw, o + lw), (o + W / 2, o + H * 0.56), (o + W - lw, o + lw)],
           fill=ink + (255,), width=lw, joint='curve')
    if stamp:
        sw = W * 0.18
        sx, sy = o + W - sw - W * 0.07, o + H * 0.52
        d.rectangle([sx, sy, sx + sw, sy + sw * 1.2], fill=stamp + (255,))
        d.ellipse([sx + sw * 0.3, sy + sw * 0.35, sx + sw * 0.7, sy + sw * 0.8],
                  fill=fill + (255,))
        for k in range(3):
            yy = sy + sw * (0.25 + k * 0.32)
            pts = [(sx - sw * 1.1 + i * sw * 0.12, yy + math.sin(i * 1.3) * sw * 0.07)
                   for i in range(13)]
            d.line(pts, fill=ink + (255,), width=max(1, lw // 2))
    return img.resize((img.width // ss, img.height // ss), Image.LANCZOS)


def _cells(rnd, n, cols):
    """격자 칸을 섞어 n 개 고른다. 그냥 흩뿌리면 몇 개가 한데 뭉치고 빈 곳이 크게 남는다."""
    rows = max(1, math.ceil(n / cols))
    cells = [(i, j) for j in range(rows) for i in range(cols)]
    rnd.shuffle(cells)
    return cells[:n], rows


def letters(spec, w, h):
    """흩어진 편지봉투. spec = ('letters', 위색, 아래색, 옵션dict)

      papers  봉투 색들      ink     윤곽선 색     stamps  우표 색들
      count   봉투 수        marks   소인 동그라미 수
      dim / dim_to
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(o.get('seed', 20261001))
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2])).convert('RGBA')
    unit = w / 500.0
    ink = gen.rgb(o.get('ink', '#5A4535'))
    papers = [gen.rgb(c) for c in o.get('papers', ['#FFFFFF'])]
    stamps = [gen.rgb(c) for c in o.get('stamps', ['#E8483B'])]

    # 소인 동그라미는 따로 만든 판에 그려 얹는다. RGBA 판에 반투명을 바로 그리면 덮어쓴다
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(o.get('marks', 10)):
        x, y, r = rnd.random() * w, rnd.random() * h, rnd.uniform(18, 30) * unit
        d.ellipse([x - r, y - r, x + r, y + r], outline=ink + (60,), width=max(1, int(2 * unit)))
    img.alpha_composite(lay)

    cells, rows = _cells(rnd, o.get('count', 15), 3)
    for i, j in cells:
        ew = rnd.uniform(88, 128) * unit
        env = _envelope(ew, ew * 0.62, rnd.choice(papers), ink,
                        rnd.choice(stamps) if rnd.random() < 0.75 else None)
        env = env.rotate(rnd.uniform(-24, 24), expand=True, resample=Image.BICUBIC)
        x = (i + rnd.uniform(0.2, 0.8)) * w / 3
        y = (j + rnd.uniform(0.2, 0.8)) * h / rows
        _drop(img, env, x, y, 3 * unit, 4 * unit, 55)
    return _dim(img, o)


def desk(spec, w, h):
    """나무 책상에 붙은 메모지. spec = ('desk', 위색, 아래색, 옵션dict)

      wood   나무결 옵션(wood 로 넘긴다)
      notes  메모지 색들    ink  낙서 색    count  메모지 수    dim / dim_to
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    seed = o.get('seed', 20261002)
    img = wood(('wood', spec[1], spec[2], dict(o.get('wood', {}), seed=seed)), w, h)
    img = img.convert('RGBA')
    rnd = random.Random(seed + 1)
    unit = w / 500.0
    ink = gen.rgb(o.get('ink', '#5A6B4A'))
    notes = [gen.rgb(c) for c in o.get('notes', ['#FFE98A'])]

    cells, rows = _cells(rnd, o.get('count', 8), 2)
    for i, j in cells:
        s = rnd.uniform(96, 132) * unit
        ss = 3
        S = int(s * ss)
        f = int(S * 0.16)
        c = rnd.choice(notes)
        piece = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        pd = ImageDraw.Draw(piece)
        pd.polygon([(0, 0), (S, 0), (S, S - f), (S - f, S), (0, S)], fill=c + (255,))
        fold = tuple(int(v * 0.84) for v in c)
        pd.polygon([(S, S - f), (S - f, S - f), (S - f, S)], fill=fold + (255,))
        # 낙서는 줄로만 — 읽히는 글자를 넣으면 말풍선 글자와 다툰다
        lw = max(ss, int(S * 0.02))
        for k in range(rnd.randint(2, 4)):
            yy = S * (0.24 + k * 0.17)
            x1 = S * rnd.uniform(0.55, 0.82)
            pts = [(S * 0.14 + (x1 - S * 0.14) * q / 10,
                    yy + math.sin(q * 1.7 + k) * S * 0.012) for q in range(11)]
            pd.line(pts, fill=ink + (255,), width=lw, joint='curve')
        piece = piece.resize((int(s), int(s)), Image.LANCZOS)
        piece = piece.rotate(rnd.uniform(-14, 14), expand=True, resample=Image.BICUBIC)
        x = (i + rnd.uniform(0.3, 0.7)) * w / 2
        y = (j + rnd.uniform(0.2, 0.8)) * h / rows
        _drop(img, piece, x, y, 3 * unit, 5 * unit, 70)
    return _dim(img, o)


def arcade(spec, w, h):
    """오락실 화면 같은 픽셀 풍경. spec = ('arcade', 위색, 아래색, 옵션dict)

      block   픽셀 한 칸 크기(폭 비율)   stars  별 수    clouds  구름 수
      hills   뒤→앞 언덕 색들            ground 맨 앞 땅 색
      coins   떠 있는 동전 수            sun / moon  해나 달 색
      dim / dim_to

    작게 그려 NEAREST 로 키운다. 부드럽게 키우면 픽셀 경계가 뭉개져 픽셀로 안 읽힌다.
    하늘 그라데이션도 세 칸마다 한 번씩만 바꿔 계단으로 만든다.
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(o.get('seed', 20261003))
    B = max(4, int(w * o.get('block', 0.02)))
    gw, gh = w // B + 1, h // B + 1
    top, bot = gen.rgb(spec[1]), gen.rgb(spec[2])

    def sky(y):
        q = min(1.0, (y // 3 * 3) / max(gh - 1, 1))
        return tuple(int(top[i] + (bot[i] - top[i]) * q) for i in range(3))

    img = Image.new('RGB', (gw, gh))
    d = ImageDraw.Draw(img)
    for y in range(gh):
        d.line([(0, y), (gw, y)], fill=sky(y))

    for _ in range(o.get('stars', 0)):
        x, y = rnd.randrange(gw), rnd.randrange(int(gh * 0.7))
        c = (255, 255, 255) if rnd.random() < 0.7 else gen.rgb(o.get('star2', '#FFE08A'))
        d.point((x, y), fill=c)
        if rnd.random() < 0.12:                       # 반짝이는 별은 십자
            d.point([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], fill=c)

    orb = o.get('sun') or o.get('moon')
    if orb:
        cx, cy, r = int(gw * 0.74), int(gh * 0.16), max(3, gw // 9)
        for yy in range(-r, r + 1):
            for xx in range(-r, r + 1):
                if xx * xx + yy * yy <= r * r:
                    d.point((cx + xx, cy + yy), fill=gen.rgb(orb))
        if o.get('moon'):
            # 초승달로 파내면 칸이 굵어 바나나처럼 보였다. 보름달에 구덩이 두 칸만 찍는다
            pit = tuple(int(v * 0.82) for v in gen.rgb(orb))
            d.rectangle([cx - r // 2, cy - r // 3, cx - r // 2 + 1, cy - r // 3 + 1], fill=pit)
            d.point((cx + r // 3, cy + r // 3), fill=pit)

    for _ in range(o.get('clouds', 0)):
        cx, cy = rnd.randrange(gw), rnd.randrange(3, int(gh * 0.55))
        cw = rnd.randint(10, 15)
        d.rectangle([cx, cy, cx + cw, cy + 2], fill=(255, 255, 255))
        d.rectangle([cx + 2, cy - 2, cx + cw - 3, cy], fill=(255, 255, 255))
        d.rectangle([cx + 4, cy - 3, cx + cw - 6, cy - 2], fill=(255, 255, 255))

    for k, col in enumerate(o.get('hills', [])):
        base = gh * (0.64 + k * 0.08)
        amp = gh * rnd.uniform(0.04, 0.07)
        ph, fr = rnd.uniform(0, 6.28), rnd.uniform(0.08, 0.16)
        for x in range(0, gw, 2):                     # 두 칸씩 끊어 계단 능선
            yy = int(base - amp * (0.5 + 0.5 * math.sin(ph + x * fr)))
            d.rectangle([x, yy, x + 1, gh], fill=gen.rgb(col))
    if o.get('ground'):
        gy = int(gh * 0.9)
        g = gen.rgb(o['ground'])
        d.rectangle([0, gy, gw, gh], fill=g)
        edge = tuple(min(255, int(v * 1.35) + 14) for v in g)
        d.line([(0, gy), (gw, gy)], fill=edge)
        for row, y in enumerate(range(gy + 3, gh, 3)):  # 벽돌 줄눈
            d.line([(0, y), (gw, y)], fill=edge)
            for x in range(row % 2 * 2, gw, 4):
                d.line([(x, y - 2), (x, y - 1)], fill=edge)

    gold, dark = gen.rgb(o.get('coin', '#FFD84D')), gen.rgb(o.get('coin_dark', '#C98A1B'))
    for _ in range(o.get('coins', 0)):
        cx, cy = rnd.randrange(2, gw - 2), rnd.randrange(int(gh * 0.2), int(gh * 0.6))
        d.rectangle([cx - 1, cy - 2, cx + 1, cy + 2], fill=gold)
        d.rectangle([cx - 2, cy - 1, cx + 2, cy + 1], fill=gold)
        d.line([(cx, cy - 1), (cx, cy + 1)], fill=dark)

    img = img.resize((gw * B, gh * B), Image.NEAREST).crop((0, 0, w, h))
    return _dim(img, o)


def _hang(d, kind, x, y, s, c, ink, peg, lw):
    """빨랫줄의 (x, y) 에 걸린 빨래 한 점. s 는 크기 단위. 차지한 폭을 돌려준다."""
    oc = ink + (255,)
    if kind == 'sock':
        d.rounded_rectangle([x, y, x + 22 * s, y + 46 * s], radius=4 * s, fill=c,
                            outline=oc, width=lw)
        d.rounded_rectangle([x, y + 30 * s, x + 44 * s, y + 56 * s], radius=12 * s, fill=c,
                            outline=oc, width=lw)
        d.rectangle([x + lw, y + 28 * s, x + 22 * s - lw, y + 40 * s], fill=c)
        stripe = tuple(int(v * 0.72) for v in c[:3]) + (255,)
        d.rectangle([x + lw, y + 8 * s, x + 22 * s - lw, y + 13 * s], fill=stripe)
        pegs, wide = (x + 11 * s,), 44 * s
    elif kind == 'towel':
        d.rectangle([x, y, x + 50 * s, y + 70 * s], fill=c, outline=oc, width=lw)
        band = tuple(int(v * 0.8) for v in c[:3]) + (255,)
        d.rectangle([x + lw, y + 52 * s, x + 50 * s - lw, y + 58 * s], fill=band)
        pegs, wide = (x + 8 * s, x + 42 * s), 50 * s
    else:
        pts = [(x + 14 * s, y), (x + 50 * s, y), (x + 64 * s, y + 16 * s),
               (x + 54 * s, y + 26 * s), (x + 50 * s, y + 22 * s), (x + 50 * s, y + 66 * s),
               (x + 14 * s, y + 66 * s), (x + 14 * s, y + 22 * s), (x + 10 * s, y + 26 * s),
               (x, y + 16 * s)]
        d.polygon(pts, fill=c)
        d.line(pts + [pts[0]], fill=oc, width=lw, joint='curve')
        pegs, wide = (x + 20 * s, x + 44 * s), 64 * s
    for px_ in pegs:
        d.rectangle([px_ - 3 * s, y - 6 * s, px_ + 3 * s, y + 8 * s], fill=peg + (255,),
                    outline=oc, width=max(1, lw // 2))
    return wide


def laundry(spec, w, h):
    """빨랫줄 하늘. spec = ('laundry', 위색, 아래색, 옵션dict)

      clothes  빨래 색들      ink  윤곽선      line  줄 색     peg  집게 색
      lines    줄 수          bubbles  비눗방울 수
      clouds / stars / moon   하늘            dim / dim_to

    두 배로 그려 줄인다. 빨래는 윤곽선이 있는 그림이라 계단이 바로 보인다.
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(o.get('seed', 20261004))
    k = 2
    W, H = w * k, h * k
    img = gen.vgradient(W, H, gen.rgb(spec[1]), gen.rgb(spec[2])).convert('RGBA')
    unit = W / 500.0

    # 구름은 또렷한 동그라미를 겹친 한 덩어리로 그려 한 번에 얹는다. 흐린 원을 하나씩
    # 얹으면 겹친 자리마다 진해져 솜뭉치 여러 개로 보였다. 바닥은 평평하게 자른다.
    if o.get('clouds'):
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(lay)
        for _ in range(o['clouds']):
            cx, cy = rnd.random() * W, rnd.uniform(0.04, 0.5) * H
            cw = rnd.uniform(110, 170) * unit
            base = cy + 18 * unit
            for q in range(5):
                bx = cx - cw / 2 + cw * (q + 0.5) / 5
                r = (1 - abs(q - 2) / 3.2) * cw * rnd.uniform(0.2, 0.26)
                cd.ellipse([bx - r, base - r * 1.7, bx + r, base + r * 0.3],
                           fill=(255, 255, 255, 255))
            cd.rectangle([cx - cw / 2 - 20 * unit, base, cx + cw / 2 + 20 * unit, base + 60 * unit],
                         fill=(0, 0, 0, 0))
        lay = lay.filter(ImageFilter.GaussianBlur(1.5 * unit))
        lay.putalpha(lay.getchannel('A').point(lambda v: v * 200 // 255))
        img.alpha_composite(lay)
    if o.get('moon'):
        mx, my, mr = W * 0.78, H * 0.1, 34 * unit
        img.alpha_composite(*_soft_blob(mr * 2.2, gen.rgb(o['moon']) + (40,), 24 * unit,
                                        mx, my))

    img = img.convert('RGB')                          # 여기부터는 RGB 판이라 반투명이 섞인다
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(o.get('stars', 0)):
        x, y, r = rnd.random() * W, rnd.random() * H * 0.8, rnd.uniform(0.8, 2.2) * unit
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rnd.randint(120, 230)))
    if o.get('moon'):
        d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=gen.rgb(o['moon']) + (255,))

    ink = gen.rgb(o.get('ink', '#3D4A5C'))
    line_c = gen.rgb(o.get('line', '#8B9BB0')) + (255,)
    peg = gen.rgb(o.get('peg', '#FFC24D'))
    clothes = [gen.rgb(c) + (255,) for c in o.get('clothes', ['#FFFFFF'])]
    lw = max(2, int(2.4 * unit))
    rows = o.get('lines', 3)
    for i in range(rows):
        y0 = H * (0.2 + i * 0.7 / rows) + rnd.uniform(-0.03, 0.03) * H
        sag = rnd.uniform(0.05, 0.09) * W
        tilt = rnd.uniform(-0.05, 0.05) * H

        def yat(x, y0=y0, sag=sag, tilt=tilt):
            return y0 + tilt * x / W + sag * 4 * (x / W) * (1 - x / W)

        d.line([(x, yat(x)) for x in range(-10, W + 11, 20)], fill=line_c, width=lw)
        x = rnd.uniform(0.02, 0.1) * W
        while x < W * 0.9:
            s = rnd.uniform(1.0, 1.35) * unit
            kind = rnd.choice(('sock', 'sock', 'towel', 'shirt'))
            x += _hang(d, kind, x, yat(x + 16 * s), s, rnd.choice(clothes), ink, peg, lw)
            x += rnd.uniform(0.05, 0.13) * W

    for _ in range(o.get('bubbles', 0)):
        x, y, r = rnd.random() * W, rnd.random() * H, rnd.uniform(8, 26) * unit
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 28),
                  outline=(255, 255, 255, 150), width=max(1, int(1.6 * unit)))
        d.ellipse([x - r * 0.55, y - r * 0.6, x - r * 0.15, y - r * 0.3],
                  fill=(255, 255, 255, 190))
    img = img.resize((w, h), Image.LANCZOS)
    return _dim(img, o)


# --- 잔불 ----------------------------------------------------------------

def ember(spec, w, h):
    """어둠 속의 잔불. 아래에서 빛이 올라오고 불티가 떠다닌다.

    spec = ('ember', 위색, 아래색, 옵션dict)
      glow    아래쪽 불빛 색
      count   불티 개수
      smoke   연기 덩어리 개수
      dim     0~1

    불티는 아래쪽일수록 크고 밝게, 위로 갈수록 작고 흐리게 그린다.
    같은 크기로 흩뿌리면 눈송이가 되고 불티로 안 보인다.
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(o.get('seed', 20260921))
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2])).convert('RGBA')
    glow_c = gen.rgb(o.get('glow', '#FF5A3C'))

    # 아래에서 올라오는 불빛
    pool, at = _soft_blob(w * 0.85, glow_c + (o.get('pool_alpha', 120),),
                          w * 0.22, w * 0.5, h * 1.02)
    img.alpha_composite(pool, at)

    # 연기. 아주 옅은 덩어리라 뚜렷하게 보이면 안 된다
    smoke_c = gen.rgb(o.get('smoke', '#3A2030'))
    for _ in range(o.get('smoke_count', 5)):
        r = rnd.uniform(0.22, 0.44) * w
        x = rnd.uniform(0.05, 0.95) * w
        y = rnd.uniform(0.15, 0.85) * h
        lay, pos = _soft_blob(r, smoke_c + (rnd.randint(40, 80),), w * 0.12, x, y)
        img.alpha_composite(lay, pos)

    # 불티
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(o.get('count', 70)):
        near = rnd.random() ** 0.55              # 1 에 가까울수록 아래
        y = h * (0.04 + near * 0.96)
        x = rnd.random() * w
        r = 0.6 + near * 1.6 + rnd.random() * 0.6
        a = int(60 + near * 140)
        c = glow_c if rnd.random() < 0.65 else gen.rgb(o.get('spark', '#FFC46B'))
        # 심지는 흰 쪽으로 당긴다. 바탕이 붉어서 붉은 점만 찍으면 묻힌다
        core = tuple(min(255, int(v + (255 - v) * (0.25 + near * 0.45))) for v in c)
        halo, pos = _soft_blob(r * 4.0, c + (int(a * 0.45),), r * 2.4, x, y)
        img.alpha_composite(halo, pos)
        d.ellipse([x - r, y - r, x + r, y + r], fill=core + (min(255, a + 80),))
        if near > 0.55 and rnd.random() < 0.5:   # 위로 끌린 꼬리
            d.line([(x, y), (x + rnd.uniform(-1.5, 1.5), y - r * rnd.uniform(2.5, 5.0))],
                   fill=c + (int(a * 0.5),), width=1)

    img = img.convert('RGB')
    dim = o.get('dim', 0.0)
    if dim:
        img = Image.blend(img, Image.new('RGB', (w, h), (0, 0, 0)), dim)
    return img


# --- 나무 ----------------------------------------------------------------

def _noise(rnd, nx, ny, w, h):
    """부드러운 2차원 잡음. 성긴 격자에 난수를 찍고 목표 크기로 bicubic 으로 키운다.

    격자 칸이 수십 픽셀이라 알갱이가 아니라 굴곡이 된다. Image.effect_noise 는
    씨앗을 못 줘서 쓰지 않는다.
    """
    g = Image.new('L', (nx, ny))
    g.putdata([rnd.randint(0, 255) for _ in range(nx * ny)])
    return g.resize((w, h), Image.BICUBIC)


def wood(spec, w, h):
    """세로로 흐르는 나무결. 판자 이음새와 옹이를 얹는다.

    spec = ('wood', 위색, 아래색, 옵션dict)
      dark     늦재(나이테의 진한 줄) 색
      light    결 사이 밝은 줄기 색
      ring     나이테 간격. 폭에 대한 비율
      figure   True 면 판자 가운데에 아치꼴 무늬결이 선다. False 면 곧은결
      planks   세로 판자 개수. 0 이면 이음새 없이 한 장
      knots    옹이 개수
      contrast 결의 진하기 0~1
      dim      0~1

    예전에는 가는 세로선을 수백 개 흘렸는데, 간격도 굵기도 제멋대로라 나무가 아니라
    긁힌 자국이나 바코드로 보였다. 옹이도 동심 타원을 겹쳐 그려서 물 위의 파문 같았다.
    진짜 나무결은 나이테를 비스듬히 자른 단면이다. 그래서 선을 긋지 않고 위상을 계산한다 —
    판자 가운데 축에서의 거리가 나이테 번호가 되고, 아래로 갈수록 그 번호를 밀면
    선이 아치꼴로 겹겹이 선다. 옹이는 그 위상을 부풀려 결이 옹이를 돌아 흐르게 한다.

    판자는 결을 따라 세로로 잇는다. 예전 이음새는 가로선이라 결을 가로질렀는데,
    나무는 그렇게 이어 붙이지 않는다.

    결은 세로로만 흐르게 한다. 목록 배경으로 쓸 때 카톡이 위에 불투명한 것을
    얹어도 잘린 자국이 안 보이는 이유가 이것이다 — 어디서 잘라도 같은 무늬다.
    아치와 옹이는 그 성질을 깨므로 목록 쪽에서는 figure=False, knots=0 으로 둔다.

    바탕을 RGB 로 둔 채 그린다. RGBA 이미지에 알파를 섞어 그리면 PIL 은 섞지 않고
    덮어쓴다 — 알파 15 로 칠한 판자가 원색 띠로 나왔다.
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(o.get('seed', 20260922))
    dark = gen.rgb(o.get('dark', '#2A1A0E'))
    light = gen.rgb(o.get('light', '#FFF0DC'))
    k = 256.0 / (w * o.get('ring', 0.030))      # 픽셀당 위상. 256 이 나이테 한 줄
    planks = o.get('planks', 3)
    n_knots = o.get('knots', 0)

    if planks > 1:
        cuts = sorted(i / planks + rnd.uniform(-0.06, 0.06) for i in range(1, planks))
        edges = [0] + [int(w * c) for c in cuts] + [w]
    else:
        edges = [0, w]
    spans = list(zip(edges, edges[1:]))

    # 위상. 판자마다 따로 계산해서 붙인다
    phase = Image.new('L', (w, h))
    for x0, x1 in spans:
        pw = x1 - x0
        # 나이테 간격이 고르면 줄무늬 천이 된다. 거리 축을 잡음으로 늘였다 줄였다 한다.
        # 잡음 길이는 판자 폭이 아니라 화면 폭으로 잡는다. 판자 폭으로 잡으면 좁은 판자에서
        # 굴곡이 촘촘해져 거리가 거꾸로 접히고, 아치 꼭대기가 톱니로 갈라진다
        wob = gen._fbm(rnd.randint(0, 1 << 30), w + 1, octaves=3)
        amp = w * o.get('ring', 0.030) * 1.2
        if o.get('figure', True) and rnd.random() < 0.8:
            lut = bytes(int(math.hypot(d + wob[d] * amp, pw * 0.22) * k) & 255
                        for d in range(pw + 1))
            wander = gen._fbm(rnd.randint(0, 1 << 30), h, octaves=2)
            base = rnd.uniform(0.35, 0.65) * pw
            rows = []
            for y in range(h):
                c = int(base + wander[y] * pw * 0.10)
                c = max(1, min(pw - 1, c))
                rows.append(lut[c:0:-1] + lut[0:pw - c])
            plank = Image.frombytes('L', (pw, h), b''.join(rows))
            # 아래로 갈수록 나이테 번호를 민다. 같은 번호의 선이 바깥으로 벌어지며 아치가 선다
            slope = k * rnd.uniform(0.06, 0.14) * rnd.choice((1, -1))
            col = Image.new('L', (1, h))
            col.putdata([int(y * slope) & 255 for y in range(h)])
            plank = ImageChops.add_modulo(plank, col.resize((pw, h), Image.NEAREST))
        else:
            off = rnd.uniform(0, pw)
            row = bytes(int((x + off + wob[x] * amp) * k) & 255 for x in range(pw))
            plank = Image.frombytes('L', (pw, h), row * h)
        phase.paste(plank, (x0, 0))

    # 결의 물결. 세로로 길쭉한 격자라 선이 느리게 휜다
    wave = _noise(rnd, max(4, w // 70), max(4, h // 260), w, h)
    phase = ImageChops.add_modulo(phase, wave)

    # 옹이. 위상을 부풀리면 나이테가 옹이를 겹겹이 감싸고 주변 결이 비켜 흐른다
    knots = []
    for i in range(n_knots):
        x0, x1 = spans[i % len(spans)]
        rx = rnd.uniform(0.035, 0.055) * w
        ry = rx * rnd.uniform(1.6, 2.4)
        kx = rnd.uniform(x0 + rx * 1.5, x1 - rx * 1.5) if x1 - x0 > rx * 3 else (x0 + x1) / 2
        ky = rnd.uniform(0.12, 0.88) * h
        knots.append((kx, ky, rx, ry))
        bx0, bx1 = max(x0, int(kx - rx * 3)), min(x1, int(kx + rx * 3))
        by0, by1 = max(0, int(ky - ry * 3)), min(h, int(ky + ry * 3))
        top = k * rnd.uniform(5.0, 7.0)
        bump = Image.new('L', (w, h), 0)
        patch = Image.new('L', (bx1 - bx0, by1 - by0))
        patch.putdata([int(top * math.exp(-(((x - kx) / rx) ** 2 + ((y - ky) / ry) ** 2)
                                          * 0.6)) & 255
                       for y in range(by0, by1) for x in range(bx0, bx1)])
        bump.paste(patch, (bx0, by0))
        phase = ImageChops.add_modulo(phase, bump)

    # 위상을 진하기로. 나이테 한 줄 안에서 이른재는 옅게 넓고, 늦재는 좁고 진하다
    prof = []
    for p in range(256):
        v = p / 256.0
        late = math.exp(-((v - 0.80) / 0.075) ** 2)
        prof.append(int(255 * min(1.0, 0.72 * late + 0.30 * v ** 3)))
    grain = phase.point(prof)

    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2]))
    # 결 사이로 긴 줄기 모양의 색 차이. 한 판자 안에서도 밝은 곳과 짙은 곳이 있다
    tone = _noise(rnd, max(6, w // 28), 3, w, h)
    img = Image.composite(Image.new('RGB', (w, h), light), img,
                          tone.point(lambda v: max(0, v - 140) // 2))
    img = Image.composite(Image.new('RGB', (w, h), dark), img,
                          tone.point(lambda v: max(0, 110 - v) // 3))
    con = o.get('contrast', 0.36)
    img = Image.composite(Image.new('RGB', (w, h), dark), img,
                          grain.point(lambda v: int(v * con)))

    # 옹이 심. 가지가 박혀 있던 자리라 결보다 짙고 가장자리가 또렷하다
    for kx, ky, rx, ry in knots:
        m = Image.new('L', (w, h), 0)
        ImageDraw.Draw(m).ellipse([kx - rx * 0.26, ky - ry * 0.18,
                                   kx + rx * 0.26, ky + ry * 0.18], fill=140)
        img = Image.composite(Image.new('RGB', (w, h), dark), img,
                              m.filter(ImageFilter.GaussianBlur(rx * 0.12)))

    # img 를 새로 만드는 합성이 위에서 끝난 뒤에 붓을 쥔다. 먼저 쥐면 옛 그림에 그린다
    d = ImageDraw.Draw(img, 'RGBA')
    # 물관. 결을 따라 짧게 긁힌 점. 이게 있어야 인쇄한 무늬가 아니라 나무 표면이 된다
    s = w / 900.0
    for _ in range(int(w * h / 700)):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        ln = rnd.uniform(3, 11) * s
        d.line([(x, y), (x, y + ln)], fill=dark + (rnd.randint(18, 48),),
               width=max(1, int(s)))


    # 판자. 판자마다 밝기를 조금씩 달리하고, 이음새는 어두운 홈과 밝은 모서리로 판다.
    # 판자 끝의 가로 이음매는 넣지 않는다 — 말풍선 사이를 가로지르면 화면의 구분선으로 읽힌다
    if planks > 1:
        for x0, x1 in spans:
            f = rnd.uniform(-1.0, 1.0)
            d.rectangle([x0, 0, x1, h], fill=(dark if f < 0 else light) + (int(abs(f) * 22),))
        gw = max(2, int(3 * s))
        for x in edges[1:-1]:
            d.line([(x, 0), (x, h)], fill=dark + (150,), width=gw)
            d.line([(x + gw, 0), (x + gw, h)], fill=light + (55,), width=max(1, int(s)))

    img = img.filter(ImageFilter.GaussianBlur(o.get('blur', 0.6) * s))
    dim = o.get('dim', 0.0)
    if dim:
        img = Image.blend(img, Image.new('RGB', (w, h), (0, 0, 0)), dim)
    return img


# --- 색유리 --------------------------------------------------------------

def stained(spec, w, h):
    """납선으로 이은 색유리 조각. 뒤에서 빛이 든다.

    spec = ('stained', 납 색, [유리색...], 옵션dict)
      cols     가로 칸 수. 칸을 대각선이나 가운데로 한 번 더 쪼개므로 조각은 이보다 많다
      lead     납선 굵기. 폭에 대한 비율
      ambient  빛이 안 닿는 곳의 밝기 0~1
      dim      0~1

    예전 스테인드 글래스는 흐린 색 덩어리였다. 이름은 성당 창인데 납선도 조각도 없어서
    어두운 그라데이션일 뿐이었고, 앰버는 흙탕물 색이 됐다. 스테인드 글래스로 읽히게
    하는 것은 색보다 조각과 그 사이의 검은 선이다.

    조각 안을 단색으로 채우면 색종이다. 세 겹을 얹는다 — 조각마다 다른 두께(밝기),
    유리 속의 얼룩, 한쪽에서 드는 빛. 납선 옆은 그늘이 져서 조각 가운데가 떠 보인다.

      backlight  역광 세기. 0 이면 달아오름·후광·빛줄기가 없다
      rays       빛줄기 개수
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(o.get('seed', 20260913))
    lead = gen.rgb(spec[1])
    colors = [gen.rgb(c) for c in spec[2]]
    cols = o.get('cols', 4)
    cw = w / cols
    rows = max(2, round(h / (cw * 1.1)))
    ch = h / rows

    V = [[(i * cw + (rnd.uniform(-0.32, 0.32) * cw if 0 < i < cols else 0),
           j * ch + (rnd.uniform(-0.32, 0.32) * ch if 0 < j < rows else 0))
          for i in range(cols + 1)] for j in range(rows + 1)]

    def lerp(p, q, f):
        return (p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f)

    polys = []
    for j in range(rows):
        for i in range(cols):
            a, b, c, d = V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]
            r = rnd.random()
            if r < 0.40:                      # 대각선으로 쪼갠다
                polys += ([a, b, c], [a, c, d]) if rnd.random() < 0.5 else \
                         ([a, b, d], [b, c, d])
            elif r < 0.65:                    # 위아래 변을 잇는 선으로 쪼갠다
                p, q = lerp(a, b, rnd.uniform(0.3, 0.7)), lerp(d, c, rnd.uniform(0.3, 0.7))
                polys += ([a, p, q, d], [p, b, c, q])
            else:
                polys.append([a, b, c, d])

    S = 2                                     # 납선 가장자리를 매끈하게 두 배로 그린다
    glass = Image.new('RGB', (w * S, h * S))
    mask = Image.new('L', (w * S, h * S), 0)
    gd, md = ImageDraw.Draw(glass), ImageDraw.Draw(mask)
    lw = max(2, int(w * o.get('lead', 0.011) * S))
    for poly in polys:
        pts = [(x * S, y * S) for x, y in poly]
        c = rnd.choice(colors)
        f = rnd.uniform(0.45, 1.15)           # 유리 두께가 조각마다 달라 밝기가 다르다
        gd.polygon(pts, fill=tuple(min(255, int(v * f)) for v in c))
        md.line(pts + [pts[0]], fill=255, width=lw, joint='curve')
    for row in V:                             # 납땜 자리. 선이 만나는 곳이 조금 도톰하다
        for x, y in row:
            r = lw * 0.9
            md.ellipse([x * S - r, y * S - r, x * S + r, y * S + r], fill=255)
    glass = glass.resize((w, h), Image.LANCZOS)
    mask = mask.resize((w, h), Image.LANCZOS)

    # 유리 속 얼룩. 손으로 부은 유리는 두께가 고르지 않다
    mott = _noise(rnd, max(4, w // 70), max(4, h // 70), w, h)
    mott = mott.point(lambda v: int(228 + (v - 128) * 0.22))
    glass = ImageChops.multiply(glass, Image.merge('RGB', (mott, mott, mott)))

    # 빛. 창 뒤 위쪽 한 곳에 광원이 있다. 예전에는 빛 지도를 곱해 먼 곳을 누르기만 해서
    # 빛이 "안 닿는 곳"만 있고 "비쳐 드는 곳"이 없었다. 역광 유리는 광원 앞 조각이 제 색을
    # 지닌 채 달아오르고, 바로 앞은 흰빛에 가깝게 타며, 그 빛이 납선을 넘어 번진다.
    lx, ly = rnd.uniform(0.3, 0.7) * w, rnd.uniform(0.06, 0.24) * h
    amb = o.get('ambient', 0.22)
    power = o.get('backlight', 1.0)

    def radial(radius, expo):
        m = Image.new('L', (w, h), 0)
        d = ImageDraw.Draw(m)
        for i in range(48, 0, -1):
            f = i / 48
            d.ellipse([lx - radius * f, ly - radius * f, lx + radius * f, ly + radius * f],
                      fill=int(255 * (1 - f) ** expo))
        return m.filter(ImageFilter.GaussianBlur(w * 0.04))

    def gray(m):
        return Image.merge('RGB', (m, m, m))

    near = radial(max(w, h) * 0.95, 1.7)          # 멀어질수록 어두워지는 넓은 빛
    hot = radial(w * 0.85, 2.0)                    # 광원 앞 달아오르는 자리
    core_m = radial(w * 0.32, 2.4)                 # 흰빛에 가깝게 타는 한가운데

    raw = glass
    lm = near.point(lambda v: int(255 * amb + v * (1 - amb)))
    glass = ImageChops.multiply(raw, gray(lm))

    # 조각 가운데가 가장자리보다 밝다. 빛이 유리를 통과해 나오는 자리라 납선에서 먼 곳이 더 탄다
    inner = mask.filter(ImageFilter.GaussianBlur(lw / S * 7)).point(
        lambda v: 255 - min(255, int(v * 2.2)))

    # 달아오름. 제 색을 곱한 것을 screen 으로 얹으면 색상은 두고 명도만 오른다.
    # 흰색을 얹으면 색이 빠져 뿌연 창이 된다 — 유리는 빛을 받을수록 제 색이 진해져 보인다
    k = ImageChops.multiply(hot, inner).point(lambda v: min(255, int(v * power)))
    lit = ImageChops.multiply(raw, gray(k))
    glass = ImageChops.screen(glass, lit)
    glass = ImageChops.screen(glass, lit.point(lambda v: int(v * 0.7)))

    # 한가운데는 유리색이 옅게 섞인 흰빛
    tint = tuple(int(v + (255 - v) * 0.30) for v in max(colors, key=sum))
    cm = ImageChops.multiply(core_m, inner).point(lambda v: min(255, int(v * 0.45 * power)))
    glass = ImageChops.screen(glass, ImageChops.multiply(Image.new('RGB', (w, h), tint), gray(cm)))
    # 빛을 받은 유리는 색이 진해 보인다. 밝히기만 하면 광원 쪽이 우유빛으로 뿌예진다
    vivid = ImageEnhance.Color(glass).enhance(1.0 + 0.5 * power)
    glass = Image.composite(vivid, glass, near)
    lit_glass = glass

    # 납선 옆 그늘. 광원 앞에서는 빛이 그늘을 덮으므로 덜 진다
    shade = mask.filter(ImageFilter.GaussianBlur(lw / S * 2.2))
    shade = ImageChops.subtract(shade, hot.point(lambda v: int(v * 0.5)))
    glass = ImageChops.multiply(glass, gray(shade.point(lambda v: 255 - int(v * 0.6))))

    # 납선. 가운데가 살짝 밝아야 납작한 먹선이 아니라 둥근 금속 띠로 보인다
    glass.paste(Image.new('RGB', (w, h), lead), (0, 0), mask)
    core = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(lw / S * 0.3))
    hi = tuple(min(255, int(v + (255 - v) * 0.22)) for v in lead)
    glass.paste(Image.new('RGB', (w, h), hi), (0, 0), core.point(lambda v: int(v * 0.45)))

    # 후광. 밝은 조각의 빛이 납선 위로 넘어온다. 광원 앞에서는 납선이 빛에 먹혀 가늘어 보인다.
    # 없으면 오려 붙인 판화 같다
    bloom = glass.filter(ImageFilter.GaussianBlur(w * 0.025))
    glass = ImageChops.screen(glass, bloom.point(lambda v: int(v * 0.18)))
    halo = ImageChops.multiply(lit_glass.filter(ImageFilter.GaussianBlur(w * 0.03)), gray(hot))
    glass = ImageChops.screen(glass, halo.point(lambda v: min(255, int(v * 0.5 * power))))

    # 빛줄기. 광원에서 아래로 퍼지는 옅은 띠. 창 앞 공기 속의 먼지에 걸린 빛이다
    n_rays = o.get('rays', 7)
    if n_rays:
        rays = Image.new('L', (w, h), 0)
        rd = ImageDraw.Draw(rays)
        far = h * 2.2
        for _ in range(n_rays):
            ang = math.radians(rnd.uniform(35, 145))
            half = math.radians(rnd.uniform(0.8, 2.6))
            rd.polygon([(lx, ly),
                        (lx + math.cos(ang - half) * far, ly + math.sin(ang - half) * far),
                        (lx + math.cos(ang + half) * far, ly + math.sin(ang + half) * far)],
                       fill=rnd.randint(50, 110))
        rays = rays.filter(ImageFilter.GaussianBlur(w * 0.015))
        rays = ImageChops.multiply(rays, near)
        glass = ImageChops.screen(glass, ImageChops.multiply(
            Image.new('RGB', (w, h), tint), gray(rays.point(lambda v: int(v * 0.45 * power)))))

    dim = o.get('dim', 0.0)
    if dim:
        glass = Image.blend(glass, Image.new('RGB', (w, h), (0, 0, 0)), dim)
    return glass
