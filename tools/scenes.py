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


# --- 불빛 두 번째 묶음 ------------------------------------------------------
# 불꽃놀이·연등·알전구·고속도로·터미널. 빛은 검은 판에 따로 그려 screen 으로 얹는다.
# 바탕에 바로 그리면 겹친 빛이 더해지지 않고 덮어써져서, 빛이 아니라 색종이로 보인다.

def _light(img, layer, blur, gain):
    """빛 판을 흐린 것과 또렷한 것 두 겹으로 얹는다. 흐린 것만 있으면 뿌옇고 또렷한 것만 있으면 점이다."""
    halo = layer.filter(ImageFilter.GaussianBlur(blur))
    img = ImageChops.screen(img.convert('RGB'), halo.point(lambda v: min(255, int(v * gain))))
    return ImageChops.screen(img, layer)


def _sag(w, y0, sag, tilt):
    """늘어진 줄의 높이 함수. 양끝을 잇는 기울기에 가운데가 처진다."""
    return lambda x: y0 + tilt * x / w + sag * 4 * (x / w) * (1 - x / w)


def fireworks(spec, w, h):
    """물 위로 터지는 불꽃. spec = ('fireworks', 하늘 위, 하늘 아래, 옵션dict)

      colors  불꽃 색들    bursts  불꽃 수    stars  별 수
      horizon 물가 높이 0~1. 아래는 불꽃이 비친 물이다    shore  물가 실루엣 색
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    seed = o.get('seed', 20261101)
    rnd = random.Random(seed)
    unit = w / 500.0
    hz = int(h * o.get('horizon', 0.82))
    cols = [gen.rgb(c) for c in o.get('colors', ['#FFB84D', '#FF6FAE', '#6FD8FF', '#9DFF8A'])]
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2]))

    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(o.get('stars', 50)):
        x, y, r = rnd.random() * w, rnd.random() * hz, rnd.uniform(0.5, 1.1) * unit
        d.ellipse([x - r, y - r, x + r, y + r], fill=(230, 235, 255, rnd.randint(40, 120)))

    lay = Image.new('RGB', (w, h))
    ld = ImageDraw.Draw(lay)
    cells, rows = _cells(rnd, o.get('bursts', 6), 2)
    for i, j in cells:
        cx = (i + rnd.uniform(0.25, 0.75)) * w / 2
        cy = (j + rnd.uniform(0.25, 0.75)) * hz * 0.92 / rows
        R = rnd.uniform(55, 105) * unit
        c1, c2 = rnd.sample(cols, 2)
        n = rnd.randint(34, 52)
        # 한 줄기는 점 열 개. 끝으로 갈수록 크고 밝고 아래로 처진다 — 곧은 선이면 성게가 된다
        for k in range(n):
            a = 2 * math.pi * k / n + rnd.uniform(-0.05, 0.05)
            L = R * rnd.uniform(0.7, 1.0)
            for s in range(10):
                f = 0.22 + 0.78 * s / 9
                px_ = cx + math.cos(a) * L * f
                py_ = cy + math.sin(a) * L * f + f * f * R * 0.16
                rr = (0.5 + 1.3 * f) * unit
                c = c1 if f < 0.72 else c2
                c = tuple(int(v * (0.3 + 0.7 * f)) for v in c)
                ld.ellipse([px_ - rr, py_ - rr, px_ + rr, py_ + rr], fill=c)
        ld.ellipse([cx - R * 0.12, cy - R * 0.12, cx + R * 0.12, cy + R * 0.12],
                   fill=tuple(int(v * 0.5) for v in c1))
    sky = _light(img, lay, 7 * unit, 1.5)

    # 물. 하늘을 뒤집어 번지게 하고 어둡게 누른 뒤 가로로 끊긴 잔물결을 긋는다
    refl = sky.crop((0, 0, w, hz)).transpose(Image.FLIP_TOP_BOTTOM)
    refl = refl.resize((w, h - hz)).filter(ImageFilter.GaussianBlur(3 * unit))
    refl = ImageEnhance.Brightness(refl).enhance(0.45)
    sky.paste(refl, (0, hz))
    d = ImageDraw.Draw(sky, 'RGBA')
    wd = gen.rgb(spec[1])
    for _ in range(90):
        y = hz + (h - hz) * rnd.random() ** 1.3
        x, ln = rnd.random() * w, rnd.uniform(0.04, 0.2) * w
        d.line([(x, y), (x + ln, y)], fill=wd + (rnd.randint(90, 170),),
               width=max(1, int(1.5 * unit)))
    shore = gen.rgb(o.get('shore', '#05060C'))
    prof = gen._fbm(seed + 7, 120)
    pts = [(0, hz + 2)] + [(w * i / 119, hz - (6 + 10 * (prof[i] + 1)) * unit)
                           for i in range(120)] + [(w, hz + 2)]
    d.polygon(pts, fill=shore + (255,))
    return _dim(sky, o)


def _lantern(r, c, rib, ss=3):
    """연등 한 알. 둥근 몸통에 세로 살, 위아래 뚜껑, 술. 가운데가 밝아야 속에 불이 든 것으로 읽힌다."""
    S = int(r * ss)
    W, H = S * 2, int(S * 2.9)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    top, bot = int(S * 0.35), int(S * 0.35 + S * 1.7)
    d.ellipse([0, top, W - 1, bot], fill=c + (255,))
    core = tuple(min(255, int(v + (255 - v) * 0.55)) for v in c)
    d.ellipse([W * 0.22, top + S * 0.3, W * 0.78, bot - S * 0.3], fill=core + (255,))
    lw = max(1, S // 22)
    for f in (0.28, 0.62):
        d.ellipse([W * (0.5 - f / 2), top, W * (0.5 + f / 2), bot], outline=rib + (255,), width=lw)
    d.rectangle([W * 0.3, top - S * 0.12, W * 0.7, top + S * 0.1], fill=rib + (255,))
    d.rectangle([W * 0.3, bot - S * 0.1, W * 0.7, bot + S * 0.12], fill=rib + (255,))
    d.line([(W / 2, 0), (W / 2, top)], fill=rib + (255,), width=lw)
    d.line([(W / 2, bot), (W / 2, H)], fill=c + (255,), width=lw * 3)
    return img.resize((W // ss, H // ss), Image.LANCZOS)


def lanterns(spec, w, h):
    """줄에 매달린 연등. spec = ('lanterns', 위, 아래, 옵션dict)

      colors  등 색들    rib  살과 뚜껑 색    rows  줄 수    bokeh  먼 불빛 수
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(o.get('seed', 20261102))
    unit = w / 500.0
    cols = [gen.rgb(c) for c in o.get('colors', ['#FF8FB1', '#FFD36B', '#7ED99B', '#FF9B5A'])]
    rib = gen.rgb(o.get('rib', '#3A2230'))
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2]))

    lay = Image.new('RGB', (w, h))
    ld = ImageDraw.Draw(lay)
    for _ in range(o.get('bokeh', 26)):
        x, y, r = rnd.random() * w, rnd.random() * h, rnd.uniform(6, 20) * unit
        c = tuple(int(v * rnd.uniform(0.15, 0.35)) for v in rnd.choice(cols))
        ld.ellipse([x - r, y - r, x + r, y + r], fill=c)
    img = ImageChops.screen(img, lay.filter(ImageFilter.GaussianBlur(5 * unit)))
    img = img.convert('RGBA')

    rows = o.get('rows', 3)
    for i in range(rows):
        near = (i + 1) / rows                      # 아래 줄일수록 가깝고 크다
        y0 = h * (0.06 + 0.8 * i / rows) + rnd.uniform(-0.03, 0.03) * h
        yat = _sag(w, y0, rnd.uniform(0.04, 0.08) * h, rnd.uniform(-0.04, 0.04) * h)
        line = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(line).line([(x, yat(x)) for x in range(-10, w + 11, 10)],
                                  fill=rib + (255,), width=max(1, int(1.6 * unit)))
        img.alpha_composite(line)
        r = (13 + 9 * near) * unit
        x = rnd.uniform(0.02, 0.1) * w
        while x < w * 1.02:
            c = rnd.choice(cols)
            hang = rnd.uniform(4, 22) * unit
            piece = _lantern(r, c, rib)
            img.alpha_composite(*_soft_blob(r * 1.9, c + (70,), r * 1.1, x,
                                            yat(x) + hang + piece.height * 0.45))
            img.alpha_composite(piece, (int(x - piece.width / 2), int(yat(x) + hang)))
            x += r * rnd.uniform(2.6, 3.6)
    return _dim(img, o)


def garland(spec, w, h):
    """늘어진 전선에 달린 알전구. spec = ('garland', 위, 아래, 옵션dict)

      bulb  전구 색들    wire  전선 색    strands  줄 수    bokeh  초점 밖 빛 수
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(o.get('seed', 20261103))
    unit = w / 500.0
    bulbs = [gen.rgb(c) for c in o.get('bulb', ['#FFD27A'])]
    wire = gen.rgb(o.get('wire', '#2A2018'))
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2]))

    # 초점 밖 빛. 크고 옅은 동그라미 — 가장자리가 조금 또렷해야 렌즈 흐림으로 읽힌다
    lay = Image.new('RGB', (w, h))
    ld = ImageDraw.Draw(lay)
    for _ in range(o.get('bokeh', 22)):
        x, y, r = rnd.random() * w, rnd.random() * h, rnd.uniform(14, 42) * unit
        c = tuple(int(v * rnd.uniform(0.12, 0.28)) for v in rnd.choice(bulbs))
        ld.ellipse([x - r, y - r, x + r, y + r], fill=c)
    img = ImageChops.screen(img, lay.filter(ImageFilter.GaussianBlur(2.5 * unit)))

    glow = Image.new('RGB', (w, h))
    gd = ImageDraw.Draw(glow)
    d = ImageDraw.Draw(img)
    heads = []
    strands = o.get('strands', 4)
    for i in range(strands):
        y0 = h * (0.06 + 0.86 * i / strands) + rnd.uniform(-0.03, 0.03) * h
        yat = _sag(w, y0, rnd.uniform(0.05, 0.1) * h, rnd.uniform(-0.06, 0.06) * h)
        d.line([(x, yat(x)) for x in range(-10, w + 11, 8)], fill=wire, width=max(2, int(2 * unit)))
        x = rnd.uniform(0, 0.06) * w
        step = rnd.uniform(46, 60) * unit
        while x < w:
            c = rnd.choice(bulbs)
            heads.append((x, yat(x), c))
            r, cy = 18 * unit, yat(x) + 14 * unit
            gd.ellipse([x - r, cy - r, x + r, cy + r], fill=tuple(int(v * 0.55) for v in c))
            x += step * rnd.uniform(0.85, 1.15)
    img = ImageChops.screen(img, glow.filter(ImageFilter.GaussianBlur(14 * unit)))
    d = ImageDraw.Draw(img)
    s = unit
    for x, y, c in heads:
        d.rectangle([x - 2.5 * s, y, x + 2.5 * s, y + 6 * s], fill=wire)
        d.ellipse([x - 5 * s, y + 5 * s, x + 5 * s, y + 20 * s], fill=c)
        core = tuple(min(255, int(v + (255 - v) * 0.7)) for v in c)
        d.ellipse([x - 2.2 * s, y + 9 * s, x + 2.2 * s, y + 16 * s], fill=core)
    return _dim(img, o)


def trails(spec, w, h):
    """오래 노출한 고속도로 불빛. spec = ('trails', 하늘 위, 하늘 아래, 옵션dict)

      red  멀어지는 차 불빛    white  다가오는 차 불빛    amber  깜빡이·가로등
      ground  땅 색    horizon  지평선 높이 0~1    lanes  차선 수
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    seed = o.get('seed', 20261104)
    rnd = random.Random(seed)
    unit = w / 500.0
    hz = h * o.get('horizon', 0.4)
    red, white = gen.rgb(o.get('red', '#FF3B4E')), gen.rgb(o.get('white', '#FFE9C2'))
    amber = gen.rgb(o.get('amber', '#FFB347'))
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2]))
    d = ImageDraw.Draw(img)
    ground = gen.rgb(o.get('ground', '#06080D'))
    prof = gen._fbm(seed + 3, 100)
    d.polygon([(0, h)] + [(w * i / 99, hz - (4 + 14 * (prof[i] + 1)) * unit) for i in range(100)]
              + [(w, h)], fill=ground)

    lay = Image.new('RGB', (w, h))
    ld = ImageDraw.Draw(lay)
    vx, vy = w * rnd.uniform(0.55, 0.68), hz

    def curve(t, b0, b1):
        u = 1 - t
        return (u * u * b0[0] + 2 * u * t * b1[0] + t * t * vx,
                u * u * b0[1] + 2 * u * t * b1[1] + t * t * vy)

    # 멀어질수록 가늘고 어두워진다. 한 차선에 줄 여러 개를 살짝 어긋나게 겹친다
    lanes = o.get('lanes', 8)
    for lane in range(lanes):
        side = -1 if lane % 2 == 0 else 1
        u = (lane // 2 + 0.5) / (lanes / 2) * side
        b0 = (w * (0.5 + u * 0.95), h * 1.06)
        b1 = (w * (0.18 + u * 0.35), h * 0.62)
        c = red if side < 0 else white
        for k in range(rnd.randint(3, 5)):
            off = rnd.uniform(-7, 7) * unit
            a = rnd.uniform(0.5, 1.0)
            prev = None
            for q in range(61):
                t = q / 60
                x, y = curve(t, (b0[0] + off, b0[1]), (b1[0] + off, b1[1]))
                if prev:
                    lw = max(1, int((1 - t) ** 1.4 * 3.2 * unit + 0.5))
                    col = tuple(int(v * a * (0.35 + 0.65 * (1 - t))) for v in c)
                    ld.line([prev, (x, y)], fill=col, width=lw)
                prev = (x, y)
        if side < 0 and rnd.random() < 0.6:          # 깜빡이. 끊긴 주황 줄
            for q in range(0, 50, 6):
                ld.line([curve(q / 60, b0, b1), curve((q + 3) / 60, b0, b1)],
                        fill=amber, width=max(1, int(2 * unit)))
    # 가로등. 길을 따라 한 줄로 서서 멀어질수록 작다
    lb0, lb1 = (w * -0.2, h * 0.5), (w * 0.05, h * 0.3)
    for q in range(1, 12):
        t = 1 - (1 - q / 12) ** 1.8
        x, y = curve(t, lb0, lb1)
        r = (1 - t) * 5 * unit + 1
        ld.ellipse([x - r, y - r, x + r, y + r], fill=amber)
    img = _light(img, lay, 5 * unit, 1.8).convert('RGBA')
    img.alpha_composite(*_soft_blob(w * 0.35, amber + (40,), w * 0.12, vx, vy))
    return _dim(img, o)


def terminal(spec, w, h):
    """켜진 옛 모니터. 줄마다 글자 같은 점무늬가 흐르고 주사선이 긋는다.

    spec = ('terminal', 위, 아래, 옵션dict)
      ink  글자 색    alt  강조 줄 색    cell  글자 한 칸 크기(폭 비율)

    글자는 3x5 칸에 점을 무작위로 찍은 것이다. 읽히는 글자를 넣으면 말풍선 글자와 다투고,
    네모 막대로 그리면 가린 서류로 보인다. 점무늬여야 코드처럼 읽힌다.
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(o.get('seed', 20261105))
    unit = w / 500.0
    ink, alt = gen.rgb(o.get('ink', '#39FF88')), gen.rgb(o.get('alt', '#FFB000'))
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2]))

    cw = max(4, int(w * o.get('cell', 0.022)))
    px_ = max(1, cw // 4)
    lh = int(cw * 1.9)
    lay = Image.new('RGB', (w, h))
    ld = ImageDraw.Draw(lay)
    cols, rows = w // cw, h // lh
    indent, last = 0, (1, 1)
    for r in range(1, rows - 1):
        if rnd.random() < 0.16:
            continue                                  # 빈 줄
        indent = max(0, min(6, indent + rnd.choice((-2, 0, 0, 2))))
        c = alt if rnd.random() < 0.1 else ink
        c = tuple(int(v * rnd.uniform(0.45, 0.85)) for v in c)
        x = 1 + indent
        end = min(cols - 1, x + rnd.randint(5, max(6, cols - 4 - indent)))
        while x < end:
            for ch in range(rnd.randint(2, 8)):
                if x >= end:
                    break
                bx, by = x * cw, r * lh
                for gy in range(5):
                    for gx in range(3):
                        if rnd.random() < 0.5:
                            ld.rectangle([bx + gx * px_, by + gy * px_,
                                          bx + (gx + 1) * px_ - 1, by + (gy + 1) * px_ - 1], fill=c)
                x += 1
            x += 1
        last = (x, r)
    x, r = last
    ld.rectangle([x * cw, r * lh, x * cw + 3 * px_, r * lh + 5 * px_], fill=ink)   # 커서
    img = _light(img, lay, 4 * unit, 1.6)

    # 주사선과 가장자리 어둠. 둘 다 없으면 초록 글자가 찍힌 검은 판일 뿐이다
    band = max(2, int(2 * unit))
    sl = Image.new('L', (1, h))
    sl.putdata([205 if (y // band) % 2 else 255 for y in range(h)])
    img = ImageChops.multiply(img, Image.merge('RGB', [sl.resize((w, h))] * 3))
    vig = Image.new('L', (w, h), 0)
    ImageDraw.Draw(vig).ellipse([-w * 0.25, -h * 0.15, w * 1.25, h * 1.15], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(w * 0.18)).point(lambda v: 110 + v * 145 // 255)
    img = ImageChops.multiply(img, Image.merge('RGB', [vig] * 3))
    return _dim(img, o)


# --- 캐릭터 두 번째 묶음의 장면 ---------------------------------------------
# 영화관·빵집·캠핑·우주·온실. 밝음과 어두움이 같은 함수를 옵션만 바꿔 쓴다.

def _ticket(tw, th, fill, ink, star, ss=3):
    """영화표 한 장. 양옆 반달 홈, 떼는 자리의 점선, 별 도장."""
    W, H = int(tw * ss), int(th * ss)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lw = max(ss, int(W * 0.012))
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=int(H * 0.08), fill=ink + (255,))
    d.rounded_rectangle([lw, lw, W - 1 - lw, H - 1 - lw], radius=int(H * 0.06), fill=fill + (255,))
    nr = H * 0.14
    for cx in (0, W):
        d.ellipse([cx - nr - lw, H / 2 - nr - lw, cx + nr + lw, H / 2 + nr + lw], fill=ink + (255,))
        d.ellipse([cx - nr, H / 2 - nr, cx + nr, H / 2 + nr], fill=(0, 0, 0, 0))
    sx = W * 0.72
    for k in range(9):
        y = H * (0.1 + k * 0.1)
        d.line([(sx, y), (sx, y + H * 0.05)], fill=ink + (255,), width=lw)
    cx, cy, R = W * 0.86, H / 2, H * 0.17
    pts = [(cx + math.cos(math.radians(-90 + i * 36)) * (R if i % 2 == 0 else R * 0.42),
            cy + math.sin(math.radians(-90 + i * 36)) * (R if i % 2 == 0 else R * 0.42))
           for i in range(10)]
    d.polygon(pts, fill=star + (255,))
    for k in range(3):                                  # 표 위의 줄. 글자는 넣지 않는다
        y = H * (0.3 + k * 0.2)
        d.line([(W * 0.12, y), (W * (0.6 - k * 0.1), y)], fill=ink + (140,), width=lw)
    return img.resize((W // ss, H // ss), Image.LANCZOS)


def _puff(d, x, y, r, fill, ink, lw):
    """팝콘 한 알. 동그라미 네 개를 겹친 덩어리."""
    for dx, dy, f in ((-0.4, 0.1, 0.62), (0.4, 0.15, 0.6), (0, -0.35, 0.66), (0.05, 0.35, 0.55)):
        rr = r * f
        d.ellipse([x + dx * r - rr - lw, y + dy * r - rr - lw, x + dx * r + rr + lw, y + dy * r + rr + lw],
                  fill=ink)
    for dx, dy, f in ((-0.4, 0.1, 0.62), (0.4, 0.15, 0.6), (0, -0.35, 0.66), (0.05, 0.35, 0.55)):
        rr = r * f
        d.ellipse([x + dx * r - rr, y + dy * r - rr, x + dx * r + rr, y + dy * r + rr], fill=fill)


def cinema(spec, w, h):
    """영화관. spec = ('cinema', 위, 아래, 옵션dict)

      screen  주면 어두운 극장을 그린다 — 위에 빛나는 막, 아래에 좌석 줄, 영사기 빛
      seats   좌석 색    tickets  표 색들 (screen 이 없을 때 흩어 놓는다)
      ink / star / pop   윤곽·별 도장·팝콘 색    dim / dim_to
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(o.get('seed', 20261201))
    unit = w / 500.0
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2])).convert('RGBA')
    ink = gen.rgb(o.get('ink', '#4A2C28'))
    pop = gen.rgb(o.get('pop', '#FFF4DA'))

    if o.get('screen'):
        sc = gen.rgb(o['screen'])
        sx0, sx1, sy0, sy1 = w * 0.08, w * 0.92, h * 0.07, h * 0.3
        img.alpha_composite(*_soft_blob(w * 0.6, sc + (60,), w * 0.16, w / 2, (sy0 + sy1) / 2))
        d = ImageDraw.Draw(img)
        d.rectangle([sx0, sy0, sx1, sy1], fill=sc + (255,))
        inner = gen.vgradient(int(sx1 - sx0) - 8, int(sy1 - sy0) - 8, sc,
                              tuple(int(v * 0.78) for v in sc))
        img.paste(inner, (int(sx0) + 4, int(sy0) + 4))
        # 영사기 빛. 뒤쪽 위 한 점에서 막으로 퍼지는 옅은 삼각형과 떠다니는 먼지
        beam = Image.new('L', (w, h), 0)
        ImageDraw.Draw(beam).polygon([(w * 0.5, h * 0.98), (sx0, sy1), (sx1, sy1)], fill=50)
        beam = beam.filter(ImageFilter.GaussianBlur(w * 0.04))
        ray = Image.new('RGBA', (w, h), sc + (255,))
        ray.putalpha(beam)
        img.alpha_composite(ray)
        d = ImageDraw.Draw(img, 'RGBA')
        for _ in range(60):
            t = rnd.random()
            x = w * 0.5 + (rnd.random() - 0.5) * (sx1 - sx0) * (1 - t)
            y = sy1 + (h * 0.98 - sy1) * t
            r = rnd.uniform(0.6, 1.5) * unit
            d.ellipse([x - r, y - r, x + r, y + r], fill=sc + (rnd.randint(40, 130),))
        seat = gen.rgb(o.get('seats', '#3A1C24'))
        rim = tuple(min(255, int(v + (s - v) * 0.35)) for v, s in zip(seat, sc))
        for row in range(5):
            f = row / 4
            y = h * (0.55 + 0.1 * row)
            sw = (38 + 26 * f) * unit
            shade = tuple(int(v * (0.55 + 0.45 * f)) for v in seat)
            x = -sw * rnd.uniform(0, 0.8)
            while x < w:
                d.rounded_rectangle([x + 2 * unit, y, x + sw - 2 * unit, y + sw * 1.2],
                                    radius=int(sw * 0.3), fill=shade + (255,))
                d.arc([x + 4 * unit, y, x + sw - 4 * unit, y + sw * 0.6], 200, 340,
                      fill=rim + (160,), width=max(1, int(1.5 * unit)))
                x += sw
        return _dim(img, o)

    tickets = [gen.rgb(c) for c in o.get('tickets', ['#FFFFFF'])]
    star = gen.rgb(o.get('star', '#E8B93A'))
    cells, rows = _cells(rnd, o.get('count', 12), 3)
    for i, j in cells:
        x = (i + rnd.uniform(0.2, 0.8)) * w / 3
        y = (j + rnd.uniform(0.2, 0.8)) * h / rows
        if rnd.random() < 0.6:
            tw = rnd.uniform(96, 124) * unit
            piece = _ticket(tw, tw * 0.44, rnd.choice(tickets), ink, star)
            piece = piece.rotate(rnd.uniform(-28, 28), expand=True, resample=Image.BICUBIC)
            _drop(img, piece, x, y, 3 * unit, 4 * unit, 50)
        else:
            lay = Image.new('RGBA', (int(90 * unit), int(90 * unit)), (0, 0, 0, 0))
            ld = ImageDraw.Draw(lay)
            for _ in range(rnd.randint(3, 5)):
                _puff(ld, rnd.uniform(0.3, 0.7) * lay.width, rnd.uniform(0.3, 0.7) * lay.height,
                      rnd.uniform(10, 14) * unit, pop + (255,), ink + (255,), max(1, int(1.6 * unit)))
            _drop(img, lay, x, y, 2 * unit, 3 * unit, 40)
    return _dim(img, o)


def _bread(kind, s, crust, crumb, ink, ss=3):
    """빵 한 조각. toast 식빵 · bun 둥근 빵 · stick 바게트."""
    S = int(s * ss)
    img = Image.new('RGBA', (int(S * 1.6), S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lw = max(ss, int(S * 0.025))
    W, H = img.size
    if kind == 'toast':
        x0 = (W - S) / 2
        for e, col in ((lw, ink), (0, crust)):
            d.rounded_rectangle([x0 - e, S * 0.04 - e, x0 + S + e, S * 0.5 + e], radius=S * 0.24 + e, fill=col + (255,))
            d.rounded_rectangle([x0 + S * 0.07 - e, S * 0.3, x0 + S * 0.93 + e, S * 0.96 + e], radius=S * 0.08 + e, fill=col + (255,))
        e = -S * 0.08
        d.rounded_rectangle([x0 - e, S * 0.04 - e, x0 + S + e, S * 0.5], radius=S * 0.18, fill=crumb + (255,))
        d.rounded_rectangle([x0 + S * 0.07 - e, S * 0.3, x0 + S * 0.93 + e, S * 0.96 + e], radius=S * 0.04, fill=crumb + (255,))
    elif kind == 'bun':
        x0 = (W - S) / 2
        d.ellipse([x0 - lw, S * 0.14 - lw, x0 + S + lw, S * 0.94 + lw], fill=ink + (255,))
        d.ellipse([x0, S * 0.14, x0 + S, S * 0.94], fill=crust + (255,))
        d.ellipse([x0 + S * 0.2, S * 0.24, x0 + S * 0.55, S * 0.42], fill=(255, 255, 255, 90))
        for _ in range(7):
            sx, sy = x0 + S * (0.3 + 0.4 * random.random()), S * (0.3 + 0.25 * random.random())
            d.ellipse([sx - lw, sy - lw * 0.6, sx + lw, sy + lw * 0.6], fill=crumb + (255,))
    else:
        d.rounded_rectangle([-lw + W * 0.02, S * 0.3 - lw, W * 0.98 + lw, S * 0.7 + lw], radius=S * 0.2, fill=ink + (255,))
        d.rounded_rectangle([W * 0.02, S * 0.3, W * 0.98, S * 0.7], radius=S * 0.2, fill=crust + (255,))
        for k in range(4):
            cx = W * (0.22 + k * 0.19)
            d.line([(cx - S * 0.06, S * 0.6), (cx + S * 0.08, S * 0.38)], fill=crumb + (255,), width=lw * 2)
    return img.resize((W // ss, H // ss), Image.LANCZOS)


def bakery(spec, w, h):
    """체크무늬 식탁보에 놓인 빵. spec = ('bakery', 바탕 위, 바탕 아래, 옵션dict)

      check  체크 줄 색    band  줄 굵기(폭 비율)    breads  (껍질, 속) 짝들
      ink  윤곽    count  빵 수    dim / dim_to
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(o.get('seed', 20261202))
    unit = w / 500.0
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2]))
    check = gen.rgb(o.get('check', '#F2C58A'))
    band = w * o.get('band', 0.1)
    # 체크는 가로 띠와 세로 띠를 반투명으로 겹친다. 겹친 칸이 진해져야 깅엄으로 읽힌다
    d = ImageDraw.Draw(img, 'RGBA')
    k = 0
    while k * band < max(w, h):
        if k % 2 == 0:
            d.rectangle([k * band, 0, (k + 1) * band, h], fill=check + (95,))
            d.rectangle([0, k * band, w, (k + 1) * band], fill=check + (95,))
        k += 1
    img = img.convert('RGBA')
    ink = gen.rgb(o.get('ink', '#5A3C22'))
    breads = [(gen.rgb(a), gen.rgb(b)) for a, b in o.get('breads', [('#D08A45', '#FFF1D2')])]
    random.seed(o.get('seed', 20261202))            # _bread 의 깨알 자리
    cells, rows = _cells(rnd, o.get('count', 9), 3)
    for i, j in cells:
        x = (i + rnd.uniform(0.25, 0.75)) * w / 3
        y = (j + rnd.uniform(0.25, 0.75)) * h / rows
        crust, crumb = rnd.choice(breads)
        kind = rnd.choice(('toast', 'toast', 'bun', 'stick'))
        piece = _bread(kind, rnd.uniform(62, 84) * unit, crust, crumb, ink)
        piece = piece.rotate(rnd.uniform(-30, 30), expand=True, resample=Image.BICUBIC)
        _drop(img, piece, x, y, 3 * unit, 5 * unit, 60)
    return _dim(img, o)


def camp(spec, w, h):
    """산 아래 텐트. spec = ('camp', 하늘 위, 하늘 아래, 옵션dict)

      hills  뒤→앞 산 색들    trees  숲 실루엣 색    ground  땅 색
      tents  텐트 색들        fire  주면 모닥불과 그 빛을 그린다
      sun / stars / clouds    하늘    dim / dim_to
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    seed = o.get('seed', 20261203)
    rnd = random.Random(seed)
    unit = w / 500.0
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2])).convert('RGBA')
    d = ImageDraw.Draw(img, 'RGBA')

    for _ in range(o.get('stars', 0)):
        x, y, r = rnd.random() * w, rnd.random() * h * 0.5, rnd.uniform(0.6, 1.6) * unit
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 235, rnd.randint(90, 220)))
    if o.get('sun'):
        img.alpha_composite(*_soft_blob(44 * unit, gen.rgb(o['sun']) + (255,), 3 * unit, w * 0.76, h * 0.14))
    for _ in range(o.get('clouds', 0)):
        cx, cy, cw = rnd.random() * w, rnd.uniform(0.05, 0.3) * h, rnd.uniform(70, 120) * unit
        lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        cd = ImageDraw.Draw(lay)
        for q in range(4):
            r = cw * rnd.uniform(0.18, 0.28)
            bx = cx - cw / 2 + cw * (q + 0.5) / 4
            cd.ellipse([bx - r, cy - r * 1.3, bx + r, cy + r * 0.4], fill=(255, 255, 255, 200))
        img.alpha_composite(lay)

    for k, col in enumerate(o.get('hills', ['#8FB0A0', '#6E9484'])):
        prof = gen._fbm(seed + 11 + k, 160, octaves=3)
        base = h * (0.46 + k * 0.08)
        pts = [(0, h)] + [(w * i / 159, base - (prof[i] + 0.6) * h * 0.09) for i in range(160)] + [(w, h)]
        ImageDraw.Draw(img).polygon(pts, fill=gen.rgb(col) + (255,))
    trees = gen.rgb(o.get('trees', '#3F6A55'))
    d = ImageDraw.Draw(img)
    x = -10 * unit
    ty = h * 0.68
    while x < w + 10 * unit:
        tw = rnd.uniform(18, 30) * unit
        th = tw * rnd.uniform(2.0, 2.8)
        for q in range(3):
            f = 1 - q * 0.25
            d.polygon([(x, ty - th + q * th * 0.22), (x - tw * 0.5 * f, ty - th * (0.45 - q * 0.22) + th * 0.2),
                       (x + tw * 0.5 * f, ty - th * (0.45 - q * 0.22) + th * 0.2)], fill=trees)
        x += tw * rnd.uniform(0.6, 1.0)
    ground = gen.rgb(o.get('ground', '#5E8A5A'))
    d.rectangle([0, ty, w, h], fill=ground)

    ink = gen.rgb(o.get('ink', '#3A2A1C'))
    fire = o.get('fire')
    tents = [gen.rgb(c) for c in o.get('tents', ['#E07A3A', '#F2C14E'])]
    spots = [(0.25, 0.8, 1.0), (0.72, 0.76, 0.8), (0.55, 0.92, 1.25)]
    for n, (fx, fy, fs) in enumerate(spots[:o.get('count', 2)]):
        tx, tyy, s = w * fx, h * fy, 90 * unit * fs
        c = tents[n % len(tents)]
        dark = tuple(int(v * 0.7) for v in c)
        lw = max(2, int(2.5 * unit))
        d.polygon([(tx - s * 0.6, tyy), (tx, tyy - s * 0.7), (tx + s * 0.6, tyy)], fill=ink)
        d.polygon([(tx - s * 0.6 + lw, tyy - lw), (tx, tyy - s * 0.7 + lw * 1.5), (tx + s * 0.6 - lw, tyy - lw)], fill=c)
        d.polygon([(tx, tyy - s * 0.7 + lw * 1.5), (tx + s * 0.6 - lw, tyy - lw), (tx + s * 0.25, tyy - lw)], fill=dark)
        d.polygon([(tx - s * 0.14, tyy - lw), (tx, tyy - s * 0.36), (tx + s * 0.14, tyy - lw)],
                  fill=tuple(int(v * 0.35) for v in c))
    if fire:
        img = _campfire(img, rnd, gen.rgb(fire), w * o.get('fire_x', 0.46),
                        h * o.get('fire_y', 0.86), unit * o.get('fire_size', 1.0),
                        o.get('fire_reach', 0.0))
    return _dim(img, o)


def _campfire(img, rnd, fc, fx, fy, s, reach):
    """모닥불과 그 빛.

    처음엔 삼각형 두 겹에 흐린 원 하나였는데, 불이 배경 위에 붙인 스티커로 보였다.
    불은 자기 모양보다 주변을 비추는 것으로 읽힌다 — 텐트의 불 쪽 면, 발밑 땅, 나무 밑동이
    주황으로 물들어야 거기 불이 있다. 그래서 그림을 다 그린 뒤 불 자리에서 퍼지는 빛을 screen 으로
    얹는다. reach 는 그 빛이 닿는 거리(폭 비율)다. 0 이면 빛을 얹지 않는다.
    """
    w, h = img.size
    img = img.convert('RGB')
    if reach:
        m = Image.new('L', (w, h), 0)
        md = ImageDraw.Draw(m)
        R = w * reach
        for i in range(48, 0, -1):
            f = i / 48
            md.ellipse([fx - R * f, fy - R * f * 0.75, fx + R * f, fy + R * f * 0.75],
                       fill=int(235 * (1 - f) ** 2.0))
        # 발밑 땅은 더 밝다. 납작한 타원으로 한 번 더 얹는다
        md.ellipse([fx - R * 0.42, fy - R * 0.05, fx + R * 0.42, fy + R * 0.12], fill=200)
        m = m.filter(ImageFilter.GaussianBlur(w * 0.03))
        lit = ImageChops.multiply(Image.new('RGB', (w, h), fc), Image.merge('RGB', [m] * 3))
        img = ImageChops.screen(img, lit)

    d = ImageDraw.Draw(img, 'RGBA')
    stone = tuple(int(v * 0.35 + 40) for v in fc)
    for k in range(9):                                # 앞쪽 반원만 돌을 둔다. 뒤는 불에 가린다
        a = math.radians(10 + k * 20)
        ex, ey = fx + math.cos(a) * 34 * s, fy + 6 * s + math.sin(a) * 9 * s
        d.ellipse([ex - 6 * s, ey - 4 * s, ex + 6 * s, ey + 4 * s], fill=stone + (255,))
    log = (92, 58, 34, 255)
    d.polygon([(fx - 30 * s, fy + 8 * s), (fx + 24 * s, fy - 4 * s), (fx + 27 * s, fy + 3 * s),
               (fx - 27 * s, fy + 15 * s)], fill=log)
    d.polygon([(fx + 30 * s, fy + 8 * s), (fx - 24 * s, fy - 4 * s), (fx - 27 * s, fy + 3 * s),
               (fx + 27 * s, fy + 15 * s)], fill=log)

    # 불꽃. 혀 여러 개를 겹치고 바깥은 붉게, 안쪽은 노랗게, 심은 거의 흰색으로 둔다.
    # 검은 판에 그려 흐린 빛과 함께 얹어야 가장자리가 타오른다
    flame = Image.new('RGB', (w, h))
    fd = ImageDraw.Draw(flame)
    red = (fc[0], int(fc[1] * 0.55), int(fc[2] * 0.35))
    yellow, white = (255, 214, 96), (255, 246, 220)

    def tongue(xo, hh, ww, col, ph):
        left, right = [], []
        lean = rnd.uniform(-6, 6) * s
        for q in range(13):
            t = q / 12
            y = fy + 2 * s - hh * t
            half = ww * (1 - t) ** 0.75 * (1 + 0.18 * math.sin(t * 7 + ph))
            cx = fx + xo + lean * t * t
            left.append((cx - half, y))
            right.append((cx + half, y))
        fd.polygon(left + right[::-1], fill=col)

    for k in range(5):
        ph = rnd.uniform(0, 6.3)
        edge = abs(k - 2)
        tongue((k - 2) * 8 * s, (52 - edge * 12) * s * rnd.uniform(0.85, 1.15), (13 - edge * 2) * s, red, ph)
    for k in range(3):
        tongue((k - 1) * 6 * s, (34 - abs(k - 1) * 8) * s, 9 * s, yellow, rnd.uniform(0, 6.3))
    tongue(0, 18 * s, 5 * s, white, 0)
    for _ in range(40):                               # 불티. 위로 갈수록 작고 흐리다
        t = rnd.random() ** 1.6
        x = fx + rnd.uniform(-30, 30) * s * (1 + t * 2)
        y = fy - (30 + t * 260) * s
        r = (2.0 - 1.4 * t) * s
        c = tuple(int(v * (1 - t * 0.7)) for v in (yellow if rnd.random() < 0.6 else red))
        fd.ellipse([x - r, y - r, x + r, y + r], fill=c)
        fd.line([(x, y), (x + rnd.uniform(-2, 2) * s, y + r * 4)], fill=c, width=max(1, int(r * 0.8)))
    return _light(img, flame, 9 * s, 1.7).convert('RGBA')


def _planet(r, c, band, ring, ss=3):
    """행성 한 개. 줄무늬를 둥근 가림막으로 오리고, 고리는 앞뒤로 나눠 그린다."""
    S = int(r * ss)
    W = int(S * 3.2)
    img = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    cx = cy = W / 2
    d = ImageDraw.Draw(img)
    lw = max(ss, S // 9)
    ring_box = [cx - S * 1.5, cy - S * 0.42, cx + S * 1.5, cy + S * 0.42]
    if ring:
        d.arc(ring_box, 180, 360, fill=ring + (255,), width=lw)
    disc = Image.new('RGBA', (W, W), c + (255,))
    dd = ImageDraw.Draw(disc)
    for k in range(3):
        y = cy - S * 0.55 + k * S * 0.45
        dd.rectangle([0, y, W, y + S * 0.16], fill=band + (255,))
    dd.ellipse([cx - S * 0.2, cy - S * 1.35, cx + S * 1.9, cy + S * 0.9], fill=(0, 0, 0, 0))
    m = Image.new('L', (W, W), 0)
    ImageDraw.Draw(m).ellipse([cx - S, cy - S, cx + S, cy + S], fill=255)
    shade = Image.new('RGBA', (W, W), tuple(int(v * 0.8) for v in c) + (255,))
    shade.alpha_composite(disc)
    base = Image.new('RGBA', (W, W), c + (255,))
    base.putalpha(m)
    img.alpha_composite(base)
    # 한쪽이 그늘진 동그라미. 둥근 것으로 읽히게 한다
    sh = Image.new('L', (W, W), 0)
    ImageDraw.Draw(sh).ellipse([cx - S * 0.55, cy - S * 1.4, cx + S * 1.7, cy + S * 1.0], fill=255)
    sh = ImageChops.subtract(m, sh.filter(ImageFilter.GaussianBlur(S * 0.15)))
    dark = Image.new('RGBA', (W, W), tuple(int(v * 0.72) for v in c) + (255,))
    dark.putalpha(sh)
    stripes = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripes)
    for k in range(3):
        y = cy - S * 0.55 + k * S * 0.45
        sd.rectangle([0, y, W, y + S * 0.16], fill=band + (150,))
    sm = ImageChops.multiply(stripes.getchannel('A'), m)
    stripes.putalpha(sm)
    img.alpha_composite(stripes)
    img.alpha_composite(dark)
    if ring:
        d = ImageDraw.Draw(img)
        d.arc(ring_box, 0, 180, fill=ring + (255,), width=lw)
    return img.resize((W // ss, W // ss), Image.LANCZOS)


def space(spec, w, h):
    """행성이 뜬 우주. spec = ('space', 위, 아래, 옵션dict)

      planets  (몸통, 줄무늬, 고리 또는 None) 짜리 목록    count  행성 수
      stars  별 수    star  별 색    orbits  궤도 점선 수    dim / dim_to
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(o.get('seed', 20261204))
    unit = w / 500.0
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2])).convert('RGBA')
    star = gen.rgb(o.get('star', '#FFFFFF'))
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(o.get('stars', 120)):
        x, y, r = rnd.random() * w, rnd.random() * h, rnd.uniform(0.5, 1.6) * unit
        d.ellipse([x - r, y - r, x + r, y + r], fill=star + (rnd.randint(70, 230),))
    for _ in range(o.get('sparkles', 8)):
        x, y, r = rnd.random() * w, rnd.random() * h, rnd.uniform(4, 8) * unit
        q = r * 0.22
        d.polygon([(x, y - r), (x + q, y - q), (x + r, y), (x + q, y + q), (x, y + r),
                   (x - q, y + q), (x - r, y), (x - q, y - q)], fill=star + (220,))
    orbit = star + (60,)
    for _ in range(o.get('orbits', 2)):
        cx, cy, rx = rnd.uniform(0.2, 0.8) * w, rnd.uniform(0.2, 0.8) * h, rnd.uniform(0.4, 0.7) * w
        for a in range(0, 360, 4):
            px_ = cx + math.cos(math.radians(a)) * rx
            py_ = cy + math.sin(math.radians(a)) * rx * 0.35
            d.ellipse([px_ - unit, py_ - unit, px_ + unit, py_ + unit], fill=orbit)
    planets = o.get('planets', [('#FFC98A', '#F2A65A', '#B9A6FF')])
    cells, rows = _cells(rnd, o.get('count', 5), 2)
    for n, (i, j) in enumerate(cells):
        body, band, ring = planets[n % len(planets)]
        r = rnd.uniform(26, 48) * unit
        p = _planet(r, gen.rgb(body), gen.rgb(band), gen.rgb(ring) if ring else None)
        p = p.rotate(rnd.uniform(-25, 25), resample=Image.BICUBIC)
        x = (i + rnd.uniform(0.25, 0.75)) * w / 2
        y = (j + rnd.uniform(0.25, 0.75)) * h / rows
        img.alpha_composite(p, (int(x - p.width / 2), int(y - p.height / 2)))
    return _dim(img, o)


def greenhouse(spec, w, h):
    """온실 안. spec = ('greenhouse', 유리 너머 위, 아래, 옵션dict)

      frame  창살 색    shelf  선반 색    pot  화분 색들    leaf  잎 색들
      lamps  주면 매달린 전등을 그린다(어두운 쪽)    rays  햇살(밝은 쪽)    dim / dim_to
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(o.get('seed', 20261205))
    unit = w / 500.0
    img = gen.vgradient(w, h, gen.rgb(spec[1]), gen.rgb(spec[2])).convert('RGBA')
    frame = gen.rgb(o.get('frame', '#FFFFFF'))
    leafs = [gen.rgb(c) for c in o.get('leaf', ['#5FAF6A', '#3F8F55', '#8CCB6E'])]
    pots = [gen.rgb(c) for c in o.get('pot', ['#E07A4F', '#D9A066'])]
    ink = gen.rgb(o.get('ink', '#27402E'))

    if o.get('rays'):
        lay = Image.new('L', (w, h), 0)
        ld = ImageDraw.Draw(lay)
        for k in range(5):
            x = w * (0.1 + k * 0.22)
            ld.polygon([(x, 0), (x + w * 0.1, 0), (x - w * 0.3, h), (x - w * 0.45, h)], fill=40)
        ray = Image.new('RGBA', (w, h), (255, 255, 240, 255))
        ray.putalpha(lay.filter(ImageFilter.GaussianBlur(w * 0.03)))
        img.alpha_composite(ray)

    # 창살. 지붕 삼각 틀 아래로 세로 기둥과 가로 창틀
    d = ImageDraw.Draw(img, 'RGBA')
    fw = max(3, int(5 * unit))
    roof = h * 0.16
    for k in range(5):
        x = w * k / 4
        d.line([(x, roof * (1 - abs(k - 2) / 2) * 0.6), (x, h)], fill=frame + (230,), width=fw)
    d.line([(0, roof), (w / 2, 0), (w, roof)], fill=frame + (230,), width=fw)
    for y in (roof, h * 0.42, h * 0.66):
        d.line([(0, y), (w, y)], fill=frame + (200,), width=fw)

    # 매달린 화분과 늘어진 덩굴
    for k in range(3):
        x = w * (0.17 + k * 0.33) + rnd.uniform(-20, 20) * unit
        cy = h * rnd.uniform(0.22, 0.3)
        d.line([(x, roof), (x, cy)], fill=ink + (200,), width=max(1, int(1.5 * unit)))
        if o.get('lamps') and k % 2 == 0:
            lc = gen.rgb(o['lamps'])
            img.alpha_composite(*_soft_blob(40 * unit, lc + (120,), 18 * unit, x, cy + 8 * unit))
            d = ImageDraw.Draw(img, 'RGBA')
            d.pieslice([x - 16 * unit, cy - 10 * unit, x + 16 * unit, cy + 14 * unit], 180, 360, fill=ink + (255,))
            d.ellipse([x - 6 * unit, cy - 2 * unit, x + 6 * unit, cy + 10 * unit], fill=lc + (255,))
            continue
        for v in range(4):
            px_ = x + (v - 1.5) * 9 * unit
            vl = rnd.uniform(60, 140) * unit
            pts = [(px_ + math.sin(q * 0.5 + v) * 5 * unit, cy + 6 * unit + q * vl / 10) for q in range(11)]
            d.line(pts, fill=leafs[1] + (255,), width=max(1, int(1.5 * unit)))
            for q in range(2, 11, 2):
                lx, ly = pts[q]
                c = rnd.choice(leafs)
                d.ellipse([lx - 5 * unit, ly - 3 * unit, lx + 5 * unit, ly + 3 * unit], fill=c + (255,))
        pc = rnd.choice(pots)
        d.polygon([(x - 18 * unit, cy - 4 * unit), (x + 18 * unit, cy - 4 * unit),
                   (x + 13 * unit, cy + 16 * unit), (x - 13 * unit, cy + 16 * unit)], fill=pc + (255,))

    # 아래 선반 두 칸에 화분
    shelf = gen.rgb(o.get('shelf', '#C9A57A'))
    for sy in (h * 0.66, h * 0.92):
        d.rectangle([0, sy, w, sy + 8 * unit], fill=shelf + (255,))
        x = rnd.uniform(10, 40) * unit
        while x < w - 30 * unit:
            s = rnd.uniform(0.8, 1.2) * unit
            pc, c = rnd.choice(pots), rnd.choice(leafs)
            kind = rnd.random()
            if kind < 0.35:                               # 기둥 선인장
                d.rounded_rectangle([x - 9 * s, sy - 62 * s, x + 9 * s, sy - 12 * s], radius=9 * s, fill=c + (255,))
                d.rounded_rectangle([x + 6 * s, sy - 46 * s, x + 18 * s, sy - 34 * s], radius=5 * s, fill=c + (255,))
                d.rounded_rectangle([x + 12 * s, sy - 58 * s, x + 18 * s, sy - 38 * s], radius=3 * s, fill=c + (255,))
            elif kind < 0.7:                              # 둥근 잎
                for a in range(-60, 61, 30):
                    lx = x + math.sin(math.radians(a)) * 22 * s
                    ly = sy - 30 * s - math.cos(math.radians(a)) * 20 * s
                    d.line([(x, sy - 14 * s), (lx, ly)], fill=leafs[1] + (255,), width=max(1, int(1.4 * s)))
                    d.ellipse([lx - 9 * s, ly - 7 * s, lx + 9 * s, ly + 7 * s], fill=c + (255,))
            else:                                         # 뾰족한 잎
                for a in (-30, -12, 8, 26):
                    tx = x + math.sin(math.radians(a)) * 50 * s
                    ty = sy - 16 * s - math.cos(math.radians(a)) * 56 * s
                    d.polygon([(x - 4 * s, sy - 14 * s), (tx, ty), (x + 4 * s, sy - 14 * s)], fill=c + (255,))
            d.polygon([(x - 16 * s, sy - 16 * s), (x + 16 * s, sy - 16 * s),
                       (x + 12 * s, sy), (x - 12 * s, sy)], fill=pc + (255,))
            x += rnd.uniform(56, 90) * unit
    return _dim(img, o)


# --- 네온 벽 ---------------------------------------------------------------

def _neon_doodle(kind, cx, cy, R):
    """네온 낙서 한 개의 선들. 선마다 점 목록이다."""
    if kind == 'heart':
        pts = []
        for i in range(61):
            a = 2 * math.pi * i / 60
            px_ = 16 * math.sin(a) ** 3
            py_ = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
            pts.append((cx + px_ * R / 17, cy - py_ * R / 17))
        return [pts]
    if kind == 'star':
        pts = [(cx + math.cos(math.radians(-90 + i * 36)) * (R if i % 2 == 0 else R * 0.42),
                cy + math.sin(math.radians(-90 + i * 36)) * (R if i % 2 == 0 else R * 0.42))
               for i in range(11)]
        return [pts]
    if kind == 'arrow':
        return [[(cx - R, cy + R * 0.5), (cx + R * 0.8, cy - R * 0.4)],
                [(cx + R * 0.2, cy - R * 0.55), (cx + R * 0.8, cy - R * 0.4), (cx + R * 0.45, cy + R * 0.12)]]
    if kind == 'moon':
        outer = [(cx + math.cos(math.radians(a)) * R, cy + math.sin(math.radians(a)) * R)
                 for a in range(40, 321, 8)]
        inner = [(cx + R * 0.45 + math.cos(math.radians(a)) * R * 0.78,
                  cy + math.sin(math.radians(a)) * R * 0.78) for a in range(300, 59, -8)]
        return [outer + inner + [outer[0]]]
    # 번개
    z = [(0.15, -1.0), (-0.35, 0.05), (0.05, 0.05), (-0.2, 1.0), (0.45, -0.15), (0.05, -0.15), (0.15, -1.0)]
    return [[(cx + a * R, cy + b * R) for a, b in z]]


def neonwall(spec, w, h):
    """네온 낙서가 걸린 벽돌 벽. spec = ('neonwall', 벽돌색, 줄눈색, 옵션dict)

      signs  [(모양, 색), ...] — heart · star · arrow · moon · bolt
      count  낙서 수    wash  벽에 번지는 빛 세기    dim / dim_to

    낙서는 모양만 있고 글자는 없다. 읽히는 글자를 넣으면 말풍선 글자와 다툰다.
    관은 검은 판에 그려 흐린 빛과 함께 screen 으로 얹는다(_light) — 벽돌 위에 바로 칠하면
    빛이 아니라 형광 페인트로 보인다.
    """
    gen = _g()
    o = spec[3] if len(spec) > 3 else {}
    rnd = random.Random(o.get('seed', 20261301))
    unit = w / 500.0
    brick, mortar = gen.rgb(spec[1]), gen.rgb(spec[2])
    img = Image.new('RGB', (w, h), mortar)
    d = ImageDraw.Draw(img)
    bw_, bh_ = 64 * unit, 26 * unit
    j = 0
    y = 0.0
    while y < h:
        x = -(bw_ / 2 if j % 2 else 0)
        while x < w:
            k = rnd.uniform(0.78, 1.12)
            c = tuple(min(255, int(v * k)) for v in brick)
            d.rectangle([x + 2 * unit, y + 2 * unit, x + bw_ - 2 * unit, y + bh_ - 2 * unit], fill=c)
            x += bw_
        y += bh_
        j += 1

    signs = o.get('signs', [('heart', '#FF3FA4'), ('star', '#35E0FF')])
    lay = Image.new('RGB', (w, h))
    core = Image.new('RGB', (w, h))
    ld, cd = ImageDraw.Draw(lay), ImageDraw.Draw(core)
    cells, rows = _cells(rnd, o.get('count', 5), 2)
    for n, (i, jj) in enumerate(cells):
        kind, col = signs[n % len(signs)]
        cx = (i + rnd.uniform(0.3, 0.7)) * w / 2
        cy = (jj + rnd.uniform(0.25, 0.75)) * h / rows
        R = rnd.uniform(34, 52) * unit
        rgb = gen.rgb(col)
        hot = gen.rgb(gen.glow_tint(col, 0.7))
        for line in _neon_doodle(kind, cx, cy, R):
            ld.line(line, fill=rgb, width=max(2, int(4.5 * unit)), joint='curve')
            cd.line(line, fill=hot, width=max(1, int(1.6 * unit)), joint='curve')
    wash = lay.filter(ImageFilter.GaussianBlur(26 * unit)).point(
        lambda v: min(255, int(v * o.get('wash', 2.2))))
    img = ImageChops.screen(img, wash)
    img = _light(img, lay, 5 * unit, 1.8)
    img = ImageChops.screen(img, core)

    # 가장자리 어둠. 없으면 벽이 화면 끝까지 고르게 밝아 조명이 아니라 벽지로 보인다
    vig = Image.new('L', (w, h), 0)
    ImageDraw.Draw(vig).ellipse([-w * 0.3, -h * 0.1, w * 1.3, h * 1.1], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(w * 0.15)).point(lambda v: 70 + v * 185 // 255)
    img = ImageChops.multiply(img, Image.merge('RGB', [vig] * 3))
    return _dim(img, o)
