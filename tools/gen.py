# -*- coding: utf-8 -*-
"""팔레트 표(tools/themes.py)에서 테마 소스 전부를 만든다.

    python tools/gen.py

결과는 build-src/<key>/ 아래. 빌드 스크립트가 그걸 읽어 .ktheme 과 .apk 로 포장한다.
생성물은 저장소에 넣지 않는다 — 원본은 팔레트 표 하나뿐이어야 한다.

iOS 와 안드로이드는 같은 그림을 다른 형식으로 요구한다.
  iOS     @2x / @3x 두 장. 늘어나는 범위는 CSS 의 cap inset 숫자로 따로 적는다.
  Android 9-patch 한 장. 늘어나는 범위를 이미지 1픽셀 테두리에 그려 넣는다.
"""
import math
import os
import random
import re
import shutil
import sys

# 윈도우 파이썬은 기본 출력 인코딩이 cp949 라 한글이 깨진다.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import themes  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'build-src')

# 말풍선 기하 (pt). CAP 은 CSS 의 cap inset 과 반드시 같아야 한다
SIZE, RADIUS, CAP = 44, 14, 18
INSET_V, INSET_H = 9, 16    # 글자와 말풍선 사이 기본 여백 (pt)
# 세로를 가로보다 좁게 두는 이유: 말풍선 프레임 높이가 곧 말풍선 사이 간격이 된다.
# 세로 여백을 키우면 글자 주변이 아니라 말풍선끼리 벌어져 보인다.


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def argb(h, alpha=1.0):
    """#RRGGBB 를 안드로이드용 #AARRGGBB 로. alpha 는 0.0~1.0."""
    return '#%02X%s' % (round(max(0.0, min(1.0, alpha)) * 255), h.lstrip('#').upper())


def lighten(h, f):
    """색을 흰쪽으로 f 만큼 당긴다. 0 이면 그대로, 1 이면 흰색."""
    c = rgb(h)
    return '#%02X%02X%02X' % tuple(round(v + (255 - v) * f) for v in c)


def mix(a, b, f):
    """a 에서 b 쪽으로 f 만큼 끌어당긴 색."""
    ca, cb = rgb(a), rgb(b)
    return '#%02X%02X%02X' % tuple(round(ca[i] + (cb[i] - ca[i]) * f) for i in range(3))


def derived(t):
    """눌림·선택 상태 색을 만든다.

    카톡은 normal 과 selected 사이를 스스로 부드럽게 전환한다. 우리가 애니메이션을
    넣을 수는 없지만 양 끝을 다르게 그려두면 그 전환이 눈에 보인다.
    두 끝을 같은 색으로 두면 앱이 아무리 이어줘도 아무 일도 안 일어난다.

    글자는 포인트색 쪽으로 끌어당기고, 말풍선 글자는 배경 대비를 살짝 키운다.
    """
    return dict(
        text_hi=mix(t['text'], t['accent'], 0.55),
        subtext_hi=mix(t['subtext'], t['accent'], 0.6),
        send_text_hi=mix(t['send_text'], t['accent'], 0.45),
        recv_text_hi=mix(t['recv_text'], t['accent'], 0.45),
    )


def mid(a, b):
    ca, cb = rgb(a), rgb(b)
    return '#%02X%02X%02X' % tuple((ca[i] + cb[i]) // 2 for i in range(3))


def vgradient(w, h, top, bottom):
    img = Image.new('RGB', (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return img.resize((w, h), Image.BILINEAR)


SS = 4   # 4배로 그렸다 줄여서 계단현상을 없앤다


def bubble_box(w, h, colors, radius, style='solid', alpha=255, glow=None, pad=0,
               flat=False):
    """말풍선 하나를 정확히 w x h 로 그린다. 세로 그라데이션.

    style 이 glass 면 반투명하게 깔고 위쪽 테두리에 빛나는 선을 얹는다.
    유리 모서리에서 빛이 꺾이는 느낌을 내려는 것이다. 반투명이라 채팅방 배경이 비친다.

    glow 가 있으면 말풍선 바깥으로 빛을 흘린다. 그만큼 pad 만큼 여백이 생기므로
    돌려주는 그림은 (w + 2*pad, h + 2*pad) 다. cap inset 도 pad 만큼 키워야 한다 —
    안 그러면 늘어나는 구간에 글로우가 걸려서 뭉개진다.
    """
    mask = Image.new('L', (w * SS, h * SS), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w * SS - 1, h * SS - 1],
                                           radius=radius * SS, fill=255)
    mask = mask.resize((w, h), Image.LANCZOS)

    if flat:
        c = rgb(mid(colors[0], colors[1]))
        body = Image.new('RGB', (w, h), c).convert('RGBA')
    else:
        body = vgradient(w, h, rgb(colors[0]), rgb(colors[1])).convert('RGBA')
    if alpha < 255:
        body.putalpha(Image.new('L', (w, h), alpha))

    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.paste(body, (0, 0), mask)
    # (글로우는 아래에서 이 그림을 여백 있는 판에 옮겨 담은 뒤 깐다)

    if style == 'glass':
        # 테두리에 빛나는 선을 얹고, 위에서 아래로 갈수록 흐리게 만든다.
        # 빛이 한쪽에서만 들어오는 것처럼 보이게 하려는 것이다.
        rim = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
        ImageDraw.Draw(rim).rounded_rectangle(
            [SS // 2, SS // 2, w * SS - SS // 2 - 1, h * SS - SS // 2 - 1],
            radius=radius * SS, outline=(255, 255, 255, 215), width=SS)
        rim = rim.resize((w, h), Image.LANCZOS)

        ramp = Image.new('L', (1, h))
        px = ramp.load()
        for y in range(h):
            px[0, y] = int(255 * max(0.0, 1.0 - (y / max(h - 1, 1)) * 1.5))
        ramp = ramp.resize((w, h))

        faded = ImageChops.multiply(rim.getchannel('A'), ramp)
        rim.putalpha(ImageChops.multiply(faded, mask))
        out.alpha_composite(rim)

    if glow:
        gc = glow[0]
        ga = glow[1]
        base = mid(colors[0], colors[1]) if gc == 'auto' else gc

        # 안쪽 발광. mask 에서 흐린 mask 를 빼면 가장자리에서 최대가 되는 띠가 나온다.
        # 둥근 모서리를 그대로 따라가므로 테두리를 직접 그리는 것보다 훨씬 매끈하다.
        # 얇고 밝은 띠와 넓고 은은한 띠를 겹친다. 한 겹만 쓰면 두께가 일정한 링이 되어
        # 스티커를 붙인 것처럼 보인다.
        thin = ImageChops.subtract(
            mask, mask.filter(ImageFilter.GaussianBlur(max(1.5, min(w, h) * 0.022))))
        wide = ImageChops.subtract(
            mask, mask.filter(ImageFilter.GaussianBlur(max(3.0, min(w, h) * 0.085))))
        band = ImageChops.add(thin.point(lambda v: int(v * 0.75)),
                              wide.point(lambda v: int(v * 0.5)))
        band = ImageChops.multiply(band, mask)

        # 위쪽을 더 밝게. 사방이 똑같이 빛나면 평평해 보인다 — 빛은 한쪽에서 든다
        ramp = Image.new('L', (1, h))
        rp = ramp.load()
        for y in range(h):
            rp[0, y] = int(255 * (1.0 - 0.55 * (y / max(h - 1, 1)) ** 0.8))
        band = ImageChops.multiply(band, ramp.resize((w, h)))

        inner = Image.new('RGBA', (w, h), rgb(lighten(base, 0.66)) + (255,))
        inner.putalpha(band.point(lambda v: min(255, int(v * 2.1))))
        out.alpha_composite(inner)

        # 맨 위 모서리에만 얇은 반사광. 유리나 금속에서 보이는 그 선
        spec_h = max(2, int(h * 0.16))
        sp = ImageChops.subtract(
            mask, mask.filter(ImageFilter.GaussianBlur(max(1.0, min(w, h) * 0.012))))
        top = Image.new('L', (w, h), 0)
        top.paste(sp.crop((0, 0, w, spec_h)), (0, 0))
        top = ImageChops.multiply(top, mask)
        sheen = Image.new('RGBA', (w, h), (255, 255, 255, 255))
        sheen.putalpha(top.point(lambda v: min(255, int(v * 0.85))))
        out.alpha_composite(sheen)

    if not pad:
        return out

    # 바깥 halo. 반경이 다른 흐림을 겹쳐서 가까이는 진하고 멀리는 길게 끌리게 만든다.
    # 한 번만 흐리면 낙차가 일정해서 띠처럼 보인다.
    gw, gh = w + pad * 2, h + pad * 2
    m = Image.new('L', (gw, gh), 0)
    m.paste(mask, (pad, pad))

    acc = Image.new('L', (gw, gh), 0)
    for r, k in ((pad * 0.30, 0.55), (pad * 0.60, 0.30), (pad * 1.05, 0.15)):
        blurred = m.filter(ImageFilter.GaussianBlur(r))
        acc = ImageChops.add(acc, blurred.point(lambda v, k=k: int(v * k)))
    acc = ImageChops.subtract(acc, m)          # 몸통 안쪽은 뺀다
    # 몸통 바로 바깥이 흐림 때문에 절반쯤으로 깎여 있다. 다시 끌어올린다.
    # 감마를 씌워 가까운 쪽은 살리고 먼 쪽은 더 빨리 떨어뜨린다 — 빛은 선형으로 안 준다
    acc = acc.point(lambda v: min(255, int(255 * ((v / 255.0) ** 0.78) * 1.55)))

    # 꼬리를 잘라 0 으로 만든다.
    # 알파가 10~20 쯤으로 여백 끝까지 남으면, 그 사각형 영역 전체가 옅게 떠서
    # 말풍선 둘레에 네모가 생긴다. 눈에는 "둥근 빛"이 아니라 "네모 상자"로 보인다.
    # 낮은 값을 잘라내면 빛이 모양을 따라가는 부분만 남는다.
    floor = 38
    acc = acc.point(lambda v: 0 if v <= floor
                    else min(255, int((v - floor) * 255.0 / (255 - floor))))

    # 그래도 가장자리는 확실히 0 으로 눌러둔다
    win = Image.new('L', (gw, gh), 0)
    ImageDraw.Draw(win).rectangle([2, 2, gw - 3, gh - 3], fill=255)
    win = win.filter(ImageFilter.GaussianBlur(max(1.0, pad * 0.5)))
    acc = ImageChops.multiply(acc, win)

    ga = glow[1]
    gc = glow[0]
    base = mid(colors[0], colors[1]) if gc == 'auto' else gc
    # 밝은 곳일수록 색이 옅어진다. 실제 빛이 그렇고, 단색으로 두면 색종이처럼 보인다
    core = acc.point(lambda v: int(255 * (v / 255.0) ** 2.2))
    halo = Image.new('RGBA', (gw, gh), rgb(base) + (255,))
    halo.paste(Image.new('RGB', (gw, gh), rgb(lighten(base, 0.55))), (0, 0), core)
    halo.putalpha(acc.point(lambda v: int(v * ga / 255)))
    halo.alpha_composite(out, (pad, pad))
    return halo


def bubble(scale, colors, style='solid', alpha=255, glow=None, pad=0, flat=False):
    """안드로이드 9-patch 와 iOS 용 정사각 말풍선."""
    return bubble_box(SIZE * scale, SIZE * scale, colors, RADIUS * scale,
                      style, alpha, glow, pad * scale, flat)


def glow_of(t):
    """테마의 글로우 설정을 (색, 진하기, 여백pt) 로 푼다. 없으면 여백 0."""
    g = t.get('glow')
    if not g:
        return None, 0
    color, strength, pad = g
    return (color, strength), pad


def ninepatch(img, cap):
    """위/왼쪽 검은 선은 늘어나는 범위, 오른쪽/아래는 내용 여백."""
    w, h = img.size
    out = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
    out.paste(img, (1, 1))
    d = ImageDraw.Draw(out)
    black = (0, 0, 0, 255)
    d.line([(1 + cap, 0), (w - cap, 0)], fill=black)
    d.line([(0, 1 + cap), (0, h - cap)], fill=black)
    pad = cap // 2
    d.line([(1 + pad, h + 1), (w - pad, h + 1)], fill=black)
    d.line([(w + 1, 1 + pad), (w + 1, h - pad)], fill=black)
    return out


def splash(t, w, h):
    """실행화면. 배경에서 살짝 밝은 쪽으로 흐르고 포인트색 빛을 얹는다."""
    img = vgradient(w, h, rgb(t['surface']), rgb(t['bg_deep'])).convert('RGBA')
    glow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    cx, cy, rmax = w // 2, int(h * 0.42), int(w * 0.62)
    for i in range(90, 0, -1):
        rr = int(rmax * i / 90)
        a = int(42 * (1 - i / 90) ** 2.2)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=rgb(t['accent']) + (a,))
    return Image.alpha_composite(img, glow).convert('RGB')


def _fbm(seed, n, octaves=4):
    """부드러운 1차원 잡음. 능선 실루엣에 쓴다.

    주파수를 배로 올리며 진폭을 반으로 줄여 겹친다. 큰 굴곡 위에 작은 굴곡이 얹혀
    자연스러운 산등성이가 된다. 제어점을 그냥 이으면 각진 저폴리가 된다.
    """
    rnd = random.Random(seed)
    out = [0.0] * n
    amp, freq, total = 1.0, 3, 0.0
    for _ in range(octaves):
        ctrl = [rnd.uniform(-1, 1) for _ in range(freq + 1)]
        for i in range(n):
            t = i / (n - 1) * freq
            j = min(int(t), freq - 1)
            f = t - j
            f = f * f * (3 - 2 * f)            # smoothstep
            out[i] += (ctrl[j] + (ctrl[j + 1] - ctrl[j]) * f) * amp
        total += amp
        amp *= 0.5
        freq *= 2
    return [v / total for v in out]


def _star_color(rnd):
    """별빛 색온도. 전부 흰색이면 인쇄물처럼 납작해진다."""
    k = rnd.random()
    if k < 0.62:
        return (255, 255, 255)
    if k < 0.84:
        return (198, 216, 255)                 # 푸른 별
    return (255, 226, 196)                     # 붉은 별


def scene_night(spec, w, h):
    """밤하늘. 별·은하수·달·능선을 그린다.

    사진을 가져다 쓸 수 없으니(저작권) 코드로 그린다.
    시드를 고정한다 — 안 그러면 빌드할 때마다 별자리가 바뀌어 diff 가 매번 더러워진다.

    spec = ('night', 위색, 아래색, 옵션dict)
      moon   달 색. None 이면 안 그림
      ridge  능선 색. None 이면 안 그림
      stars  별 개수
      dim    0~1. 클수록 어둡게 덮는다. 글자가 얹히는 화면은 올린다
    """
    o = spec[3] if len(spec) > 3 else {}
    unit = w / 500.0
    img = vgradient(w, h, rgb(spec[1]), rgb(spec[2])).convert('RGB')

    # 하늘에 아주 옅은 잡음을 섞는다. 매끈한 그라데이션은 띠(밴딩)가 보인다
    # 잡음을 살짝 흐려서 섞는다. 픽셀 단위 잡음은 PNG 가 못 줄여서 파일이 몇 배로 커진다.
    # 흐린 잡음도 띠를 깨는 데는 충분하다.
    noise = Image.effect_noise((w, h), 7).filter(
        ImageFilter.GaussianBlur(1.1)).convert('RGB')
    img = Image.blend(img, noise, 0.05)

    horizon = h * (0.74 if o.get('ridge') else 1.0)

    # --- 은하수. 비스듬한 띠에만 별을 몰아 넣고 옅은 빛을 깐다 ---
    band = Image.new('L', (w, h), 0)
    bd = ImageDraw.Draw(band)
    bd.polygon([(-w * 0.1, h * 0.02), (w * 0.55, -h * 0.05),
                (w * 1.1, h * 0.42), (w * 0.72, h * 0.60),
                (w * 0.05, h * 0.30)], fill=255)
    band = band.filter(ImageFilter.GaussianBlur(w * 0.10))
    wash = Image.new('RGBA', (w, h), (150, 170, 230, 255))
    wash.putalpha(band.point(lambda v: int(v * 0.14)))
    img = Image.alpha_composite(img.convert('RGBA'), wash).convert('RGB')

    d = ImageDraw.Draw(img, 'RGBA')
    rnd = random.Random(20260912)
    bpx = band.load()

    n = o.get('stars', 220)
    for _ in range(n * 2):
        x, y = rnd.random() * w, rnd.random() * horizon
        # 은하수 안쪽은 촘촘하게, 지평선 가까이는 성기게
        p = 0.16 + bpx[int(x), int(y)] / 255.0 * 0.9
        p *= 1.0 - (y / horizon) * 0.45
        if rnd.random() > p:
            continue
        r = rnd.choice([0.5, 0.6, 0.8, 1.0, 1.3, 1.7, 2.2]) * unit
        a = rnd.randint(60, 255)
        c = _star_color(rnd)
        if r > 1.4 * unit:                      # 큰 별엔 옅은 무리를 씌운다
            for k in (3.2, 2.0):
                rr = r * k
                d.ellipse([x - rr, y - rr, x + rr, y + rr],
                          fill=c + (int(a * 0.07),))
        d.ellipse([x - r, y - r, x + r, y + r], fill=c + (a,))

    for _ in range(o.get('glints', 7)):
        x, y = rnd.random() * w, rnd.random() * horizon * 0.85
        L = rnd.uniform(6, 13) * unit
        for dx, dy in ((L, 0), (0, L)):
            d.line([(x - dx, y - dy), (x + dx, y + dy)],
                   fill=(255, 255, 255, 95), width=max(1, int(unit)))

    # --- 달 ---
    moon = o.get('moon')
    if moon:
        mx, my = w * o.get('moon_x', 0.72), h * o.get('moon_y', 0.17)
        mr = w * o.get('moon_r', 0.085)
        halo = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        hd = ImageDraw.Draw(halo)
        for i in range(60, 0, -1):
            rr = mr * (1 + i * 0.16)
            hd.ellipse([mx - rr, my - rr, mx + rr, my + rr],
                       fill=rgb(moon) + (int(26 * (1 - i / 60) ** 2.4),))
        img = Image.alpha_composite(img.convert('RGBA'), halo).convert('RGB')

        ss = 4
        disc = Image.new('RGBA', (int(mr * 3 * ss), int(mr * 3 * ss)), (0, 0, 0, 0))
        dd = ImageDraw.Draw(disc)
        cx = cy = mr * 1.5 * ss
        R = mr * ss
        dd.ellipse([cx - R, cy - R, cx + R, cy + R], fill=rgb(moon) + (255,))
        # 크레이터. 밝은 쪽에만 아주 옅게
        cr = random.Random(77)
        for _ in range(14):
            ang, dist = cr.uniform(0, 6.28), cr.uniform(0.15, 0.8) * R
            px, py = cx + math.cos(ang) * dist, cy + math.sin(ang) * dist
            pr = cr.uniform(0.08, 0.2) * R
            dd.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(0, 0, 0, 12))
        disc = disc.filter(ImageFilter.GaussianBlur(R * 0.03))
        if o.get('crescent', True):
            off = R * 0.62
            dd.ellipse([cx - R + off, cy - R - off * 0.34,
                        cx + R + off, cy + R - off * 0.34], fill=(0, 0, 0, 0))
        disc = disc.resize((int(mr * 3), int(mr * 3)), Image.LANCZOS)
        img = img.convert('RGBA')
        img.alpha_composite(disc, (int(mx - mr * 1.5), int(my - mr * 1.5)))
        img = img.convert('RGB')
        d = ImageDraw.Draw(img, 'RGBA')

    # --- 능선 ---
    ridge = o.get('ridge')
    if ridge:
        # 지평선 부근에 옅은 빛. 대기가 있는 것처럼 보이게 한다
        glowh = int(h * 0.22)
        hg = Image.new('RGBA', (w, glowh), (0, 0, 0, 0))
        hgd = ImageDraw.Draw(hg)
        for i in range(glowh):
            hgd.line([(0, i), (w, i)],
                     fill=rgb(o.get('haze', '#33406B')) + (int(70 * (i / glowh) ** 1.6),))
        hg = hg.filter(ImageFilter.GaussianBlur(w * 0.03))
        img = img.convert('RGBA')
        img.alpha_composite(hg, (0, int(h * 0.74) - glowh))
        img = img.convert('RGB')
        d = ImageDraw.Draw(img, 'RGBA')

        N = 240
        layers = ((0.78, 0.30, 5), (0.86, 0.14, 11), (0.94, 0.0, 23))
        for base_y, haze, seed in layers:
            prof = _fbm(seed, N)
            amp = h * (0.085 if base_y < 0.8 else 0.055)
            pts = [(0, h)]
            for i in range(N):
                pts.append((w * i / (N - 1), h * base_y + prof[i] * amp))
            pts.append((w, h))
            c = rgb(ridge)
            # 멀수록 하늘색이 섞여 흐릿하게 — 대기 원근
            sky = rgb(spec[2])
            c = tuple(round(c[k] + (sky[k] - c[k]) * haze) for k in range(3))
            d.polygon(pts, fill=c + (255,))

    dim = o.get('dim', 0.0)
    if dim:
        img = Image.blend(img, Image.new('RGB', (w, h), (0, 0, 0)), dim)
    return img



def chat_bg(spec, w, h):
    kind = spec[0]
    if kind == 'night':
        return scene_night(spec, w, h)
    if kind == 'linear':
        return vgradient(w, h, rgb(spec[1]), rgb(spec[2]))
    if kind == 'blobs':
        # 색 덩어리를 크게 흐려서 유리 너머로 빛이 번지는 것처럼 만든다
        base = Image.new('RGB', (w, h), rgb(spec[1]))
        d = ImageDraw.Draw(base)
        spots = [(0.22, 0.18, 0.52), (0.82, 0.30, 0.46), (0.35, 0.62, 0.58),
                 (0.88, 0.80, 0.44), (0.10, 0.88, 0.40)]
        for i, (fx, fy, fr) in enumerate(spots):
            c = rgb(spec[2][i % len(spec[2])])
            cx, cy, r = int(w * fx), int(h * fy), int(w * fr)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
        base = base.filter(ImageFilter.GaussianBlur(radius=w // 4))
        return Image.blend(Image.new('RGB', (w, h), rgb(spec[1])), base, 0.7)
    # aurora: 바탕 위에 색 덩어리를 뿌리고 크게 흐린다. 오로라처럼 번지게
    base = Image.new('RGB', (w, h), rgb(spec[1]))
    layer = Image.new('RGB', (w, h), rgb(spec[1]))
    d = ImageDraw.Draw(layer)
    bands = [(0.12, 0.34), (0.30, 0.52), (0.52, 0.74)]
    for c, (y0, y1) in zip(spec[2], bands):
        for i in range(24):
            t = i / 23
            y = int(h * (y0 + (y1 - y0) * t))
            off = int(w * 0.22 * (t - 0.5))
            d.ellipse([-w // 3 + off, y - h // 12, w + w // 3 + off, y + h // 12],
                      fill=rgb(c))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=w // 7))
    return Image.blend(base, layer, 0.55)


def edge_glow(img, color, strength, width_ratio=0.22):
    """배경 가장자리에 빛을 흘린다. 화면 테두리에서 빛이 새어 들어오는 느낌."""
    w, h = img.size
    ramp = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(ramp)
    steps = 40
    bw = int(min(w, h) * width_ratio)
    for i in range(steps):
        t = i / (steps - 1)
        inset = int(bw * t)
        d.rectangle([inset, inset, w - 1 - inset, h - 1 - inset],
                    outline=int(strength * (1 - t) ** 2))
    ramp = ramp.filter(ImageFilter.GaussianBlur(radius=bw // 3 or 1))
    layer = Image.new('RGBA', (w, h), rgb(color) + (255,))
    layer.putalpha(ramp)
    out = img.convert('RGBA')
    out.alpha_composite(layer)
    return out.convert('RGB')


def icon(t, size=128):
    """테마 아이콘. 카톡 테마 목록에 뜨는 그림이자 README 의 이름 앞 표식.

    앱 아이콘처럼 보이게 만든다 — 배경에 비네팅을 깔아 말풍선이 뜨게 하고,
    위에서 빛이 드는 광택과 얇은 안쪽 테두리를 얹는다. 평평한 사각형은 스티커로 보인다.

    두 곳에 쓴다.
      - docs/icon-<key>.png        README 의 테마 이름 왼쪽
      - Images/commonIcoTheme.png  카톡 테마 목록 (iOS 규격에 있는 자리)
    """
    ss = 4
    W = size * ss
    light = _is_light(t)

    if t.get('chat_bg'):
        base = chat_bg(t['chat_bg'], W, W).convert('RGBA')
    else:
        base = vgradient(W, W, rgb(t['bg']), rgb(t['bg_deep'])).convert('RGBA')

    # 비네팅. 가장자리를 눌러 가운데가 떠 보이게 한다
    vig = Image.new('L', (W, W), 0)
    vd = ImageDraw.Draw(vig)
    for i in range(40):
        f = i / 39
        inset = int(W * 0.5 * f)
        vd.ellipse([inset - W * 0.12, inset - W * 0.12,
                    W - inset + W * 0.12, W - inset + W * 0.12],
                   fill=int(90 * (f ** 2)))
    vig = vig.filter(ImageFilter.GaussianBlur(W * 0.06))
    shade = Image.new('RGBA', (W, W), (255, 255, 255, 255) if light else (0, 0, 0, 255))
    shade.putalpha(vig.point(lambda v: int(v * (0.35 if light else 0.8))))
    base.alpha_composite(shade)

    glow, pad = glow_of(t)
    style, alpha = t.get('bubble_style', 'solid'), t.get('bubble_alpha', 255)
    flat = t.get('flat', False)
    gp = max(1, pad * ss // 3) if glow else 0     # 글로우 없으면 여백도 없다

    # 큰 말풍선 하나와 작은 것 하나. 카톡 기본 아이콘도 큰 말풍선이 주인공이다
    big_w, big_h = int(W * 0.54), int(W * 0.21)
    sml_w, sml_h = int(W * 0.33), int(W * 0.16)
    r_big, r_sml = int(big_h * 0.42), int(sml_h * 0.42)

    sml = bubble_box(sml_w, sml_h, t['recv'], r_sml, style, alpha, glow, gp, flat)
    big = bubble_box(big_w, big_h, t['send'], r_big, style, alpha, glow, gp, flat)

    # 큰 것 밑에 옅은 그림자를 깔아 떠 보이게 한다
    sh = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [int(W * 0.20), int(W * 0.52), int(W * 0.20) + big_w, int(W * 0.52) + big_h],
        radius=r_big, fill=(0, 0, 0, 90 if not light else 45))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(W * 0.035)))

    base.alpha_composite(sml, (int(W * 0.13), int(W * 0.20)))
    base.alpha_composite(big, (int(W * 0.20), int(W * 0.52)))

    # 위쪽 광택
    gloss = Image.new('L', (W, W), 0)
    ImageDraw.Draw(gloss).ellipse([-W * 0.45, -W * 0.95, W * 1.45, W * 0.42], fill=255)
    gloss = gloss.filter(ImageFilter.GaussianBlur(W * 0.05))
    sheen = Image.new('RGBA', (W, W), (255, 255, 255, 255))
    sheen.putalpha(gloss.point(lambda v: int(v * (0.10 if light else 0.13))))
    base.alpha_composite(sheen)

    # 둥근 사각형으로 자르고 안쪽에 얇은 테두리
    radius = int(W * 0.22)
    mask = Image.new('L', (W, W), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, W - 1], radius=radius, fill=255)
    out = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    out.paste(base, (0, 0), mask)

    edge = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle(
        [ss, ss, W - ss - 1, W - ss - 1], radius=radius - ss,
        outline=(0, 0, 0, 60) if light else (255, 255, 255, 46), width=ss)
    edge.putalpha(ImageChops.multiply(edge.getchannel('A'), mask))
    out.alpha_composite(edge)
    return out.resize((size, size), Image.LANCZOS)


def _is_light(t):
    """밝은 테마인지. 배경 밝기로 판단한다."""
    c = rgb(t['bg'])
    return (c[0] * 299 + c[1] * 587 + c[2] * 114) / 1000 > 128


# --- iOS ----------------------------------------------------------------

CSS = """/*
 {name} — iOS 카카오톡 테마

 이 파일은 tools/themes.py 에서 생성된다. 직접 고치지 말 것.
 색을 바꾸려면 팔레트 표를 고치고 python tools/gen.py 를 다시 돌린다.

 지정하지 않은 항목은 카카오 기본 테마가 그대로 보인다.
 iOS 테마에는 실행화면(스플래시) 블록이 없다. 안드로이드에만 있다.
*/

ManifestStyle
{{
    -kakaotalk-theme-name: '{name}';
    -kakaotalk-theme-version: '{version}';
    -kakaotalk-author-name: 'Ruminem';
    -kakaotalk-theme-id: 'com.kakao.talk.theme.{key}';
}}

/* 탭바. 아이콘 8종은 아직 카톡 기본값이다 */
TabBarStyle-Main
{{
    background-color: {bg};
}}

HeaderStyle-Main
{{
    -ios-text-color: {text};
    -ios-tab-text-color: {subtext};
    -ios-tab-highlighted-text-color: {accent};
}}

/* 친구탭·채팅목록 본문 */
MainViewStyle-Primary
{{
    background-color: {bg};{mainbg}

    -ios-text-color: {text};
    -ios-highlighted-text-color: {text_hi};

    -ios-description-text-color: {subtext};
    -ios-description-highlighted-text-color: {subtext_hi};

    -ios-paragraph-text-color: {subtext};
    -ios-paragraph-highlighted-text-color: {subtext_hi};

    /* alpha 가 1 미만이면 뒤의 배경 이미지가 비친다. 유리 느낌은 여기서 나온다 */
    -ios-normal-background-color: {bg};
    -ios-normal-background-alpha: {cell_alpha};
    -ios-selected-background-color: {pressed};
    -ios-selected-background-alpha: {cell_alpha_sel};
}}

MainViewStyle-Secondary
{{
    background-color: {surface};
}}

SectionTitleStyle-Main
{{
    border-color: {border};
    border-alpha: 1.0;
    -ios-text-color: {subtext};
    -ios-text-alpha: 1.0;
}}

FeatureStyle-Primary
{{
    -ios-text-color: {accent};
}}

BackgroundStyle-ChatRoom
{{
    background-color: {bg_deep};{chatbg}
}}

InputBarStyle-Chat
{{
    background-color: {surface};

    -ios-send-normal-background-color: {accent};
    -ios-send-normal-foreground-color: {on_accent};
    -ios-send-highlighted-background-color: {accent_dim};
    -ios-send-highlighted-foreground-color: {on_accent};

    -ios-button-normal-foreground-color: {subtext};
    -ios-button-highlighted-foreground-color: {accent};
}}

/*
 말풍선. 배경은 PNG 로만 지정할 수 있고 background-color 속성이 없다.
 세로 그라데이션인 이유는 말풍선이 가로로 늘어날 때 각 줄의 색이 유지되기 때문이다.
 뒤의 숫자 두 개가 늘어나지 않는 가장자리이고 gen.py 의 CAP 과 같아야 한다.

 edgeinsets 는 글자와 프레임 사이 여백이다. 글로우가 있으면 그림 바깥쪽 여백이
 프레임 안에 들어가므로 몸통이 그만큼 안으로 밀린다. 여백을 같이 키우지 않으면
 글자가 몸통 가장자리에 붙어버린다.

 반대로 여백이 크면 말풍선 사이가 벌어진다. 프레임 높이가 곧 간격이기 때문이다.
 그래서 글로우 여백은 필요한 만큼만 두고 세기로 보완한다.

 01 과 02 에 다른 색을 주면 눌린 말풍선과 그룹 말풍선이 달라 보인다.
*/
MessageCellStyle-Send
{{
    -ios-background-image: 'chatroomBubbleSend01.png' {cap}px {cap}px;
    -ios-selected-background-image: 'chatroomBubbleSend02.png' {cap}px {cap}px;
    -ios-group-background-image: 'chatroomBubbleSend02.png' {cap}px {cap}px;
    -ios-group-selected-background-image: 'chatroomBubbleSend01.png' {cap}px {cap}px;

    -ios-title-edgeinsets: {ins};
    -ios-group-title-edgeinsets: {ins};

    -ios-text-color: {send_text};
    -ios-selected-text-color: {send_text_hi};
    -ios-unread-text-color: {accent};
}}

MessageCellStyle-Receive
{{
    -ios-background-image: 'chatroomBubbleReceive01.png' {cap}px {cap}px;
    -ios-selected-background-image: 'chatroomBubbleReceive02.png' {cap}px {cap}px;
    -ios-group-background-image: 'chatroomBubbleReceive02.png' {cap}px {cap}px;
    -ios-group-selected-background-image: 'chatroomBubbleReceive01.png' {cap}px {cap}px;

    -ios-title-edgeinsets: {ins};
    -ios-group-title-edgeinsets: {ins};

    -ios-text-color: {recv_text};
    -ios-selected-text-color: {recv_text_hi};
    -ios-unread-text-color: {accent};
}}

BackgroundStyle-Passcode
{{
    background-color: {bg_deep};{passbg}
}}

LabelStyle-PasscodeTitle
{{
    -ios-text-color: {text};
}}

PasscodeStyle
{{
    -ios-keypad-background-color: {surface};
    -ios-keypad-text-normal-color: {text};
}}

BackgroundStyle-MessageNotificationBar
{{
    background-color: {surface};
}}

LabelStyle-MessageNotificationBarName
{{
    -ios-text-color: {text};
}}

LabelStyle-MessageNotificationBarMessage
{{
    -ios-text-color: {subtext};
}}

BackgroundStyle-DirectShareBar
{{
    background-color: {surface};
}}

LabelStyle-DirectShareBarName
{{
    -ios-text-color: {text};
}}

LabelStyle-DirectShareBarMessage
{{
    -ios-text-color: {subtext};
}}

BottomBannerStyle
{{
    background-color: {surface};
}}
"""


def background(t, spec, w, h):
    """배경 이미지 한 장. 테마에 글로우가 있으면 가장자리에 빛을 흘린다."""
    img = chat_bg(spec, w, h)
    g = t.get('glow')
    if g:
        # 배경에는 말풍선처럼 따라갈 색이 없다. auto 면 포인트색을 쓴다
        color = t['accent'] if g[0] == 'auto' else g[0]
        # 배경은 면적이 넓어서 말풍선과 같은 세기로 넣으면 화면이 뿌예진다
        img = edge_glow(img, color, int(g[1] * 0.7))
    return img


def gen_ios(t, root):
    img_dir = os.path.join(root, 'Images')
    os.makedirs(img_dir, exist_ok=True)

    style, alpha = t.get('bubble_style', 'solid'), t.get('bubble_alpha', 255)
    glow, pad = glow_of(t)
    for side, key in (('Send', 'send'), ('Receive', 'recv')):
        for variant, pal in (('01', t[key]), ('02', t[key + '_alt'])):
            for scale in (2, 3):
                name = 'chatroomBubble%s%s@%dx.png' % (side, variant, scale)
                bubble(scale, pal, style, alpha, glow, pad,
                       t.get('flat', False)).save(os.path.join(img_dir, name))

    icon(t, 120).save(os.path.join(img_dir, 'commonIcoTheme.png'))

    chatbg = ''
    if t['chat_bg']:
        background(t, t['chat_bg'], 600, 1300).save(os.path.join(img_dir, 'chatroomBgImage@2x.png'))
        background(t, t['chat_bg'], 900, 1950).save(os.path.join(img_dir, 'chatroomBgImage@3x.png'))
        chatbg = "\n    -ios-background-image: 'chatroomBgImage.png';"

    mainbg = ''
    if t.get('main_bg'):
        background(t, t['main_bg'], 600, 1300).save(os.path.join(img_dir, 'mainBgImage@2x.png'))
        background(t, t['main_bg'], 900, 1950).save(os.path.join(img_dir, 'mainBgImage@3x.png'))
        mainbg = "\n    -ios-background-image: 'mainBgImage.png';"

    passbg = ''
    if t.get('passcode_bg'):
        background(t, t['passcode_bg'], 600, 1300).save(
            os.path.join(img_dir, 'passcodeBgImage@2x.png'))
        background(t, t['passcode_bg'], 900, 1950).save(
            os.path.join(img_dir, 'passcodeBgImage@3x.png'))
        passbg = "\n    -ios-background-image: 'passcodeBgImage.png';"

    ca = t.get('cell_alpha', 1.0)
    fields = dict(t)
    fields.update(derived(t))          # 눌림 상태 색
    fields.pop('cell_alpha', None)          # 아래에서 문자열로 다시 넣는다
    ins = '%dpx %dpx %dpx %dpx' % (INSET_V + pad, INSET_H + pad,
                                  INSET_V + pad, INSET_H + pad)
    css = CSS.format(version=themes.VERSION, cap=CAP + pad, ins=ins,
                     chatbg=chatbg, mainbg=mainbg, passbg=passbg,
                     cell_alpha='%.2f' % ca,
                     cell_alpha_sel='%.2f' % min(1.0, ca + 0.15), **fields)
    with open(os.path.join(root, 'KakaoTalkTheme.css'), 'w', encoding='utf-8') as f:
        f.write(css)


# --- Android ------------------------------------------------------------

MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<!--
  리소스만 든 APK 다. 코드가 없으므로 hasCode="false".
  카카오톡은 com.kakao.talk.theme.* 로 시작하는 패키지를 테마로 인식한다.
  권한은 하나도 요구하지 않는다. 설치할 때 권한 안내가 뜨면 뭔가 잘못된 것이다.
  tools/themes.py 에서 생성된다.
-->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.kakao.talk.theme.{key}"
    android:versionCode="{code}"
    android:versionName="{version}">

    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="34" />

    <application
        android:label="@string/app_name"
        android:hasCode="false"
        android:allowBackup="false" />
</manifest>
"""

COLORS = [
    ('theme_background_color', 'bg'),
    ('theme_header_color', 'text'),
    ('theme_header_cell_color', 'bg'),
    ('theme_tab_bannerbadge_background_color', 'accent'),
    ('theme_section_title_color', 'subtext'),
    ('theme_title_color', 'text'),
    ('theme_title_pressed_color', 'text_hi'),
    ('theme_paragraph_color', 'subtext'),
    ('theme_paragraph_pressed_color', 'subtext_hi'),
    ('theme_description_color', 'subtext'),
    ('theme_description_pressed_color', 'subtext_hi'),
    ('theme_body_cell_color', 'bg'),
    ('theme_body_cell_pressed_color', 'pressed'),
    ('theme_body_cell_border_color', 'border'),
    ('theme_body_secondary_cell_color', 'surface'),
    ('theme_feature_primary_color', 'accent'),
    ('theme_feature_primary_pressed_color', 'accent_dim'),
    ('theme_feature_browse_tab_color', 'subtext'),
    ('theme_feature_browse_tab_focused_color', 'accent'),
    ('theme_maintab_cell_color', 'bg'),
    ('theme_chatroom_background_color', 'bg_deep'),
    ('theme_chatroom_unread_count_color', 'accent'),
    ('theme_chatroom_input_bar_color', 'text'),
    ('theme_chatroom_input_bar_background_color', 'surface'),
    ('theme_chatroom_input_bar_menu_icon_color', 'subtext'),
    ('theme_chatroom_input_bar_send_button_color', 'accent'),
    ('theme_chatroom_input_bar_send_icon_color', 'on_accent'),
    ('theme_direct_share_color', 'text'),
    ('theme_direct_share_button_color', 'accent'),
    ('theme_direct_share_background_color', 'surface'),
    ('theme_notification_color', 'text'),
    ('theme_notification_background_color', 'surface'),
    ('theme_notification_background_pressed_color', 'pressed'),
    ('theme_passcode_color', 'text'),
    ('theme_passcode_background_color', 'bg_deep'),
    ('theme_passcode_keypad_color', 'text'),
    ('theme_passcode_keypad_pressed_color', 'accent'),
    ('theme_passcode_keypad_background_color', 'surface'),
    ('theme_passcode_keypad_pressed_background_color', 'pressed'),
    ('theme_passcode_pattern_line_color', 'accent'),
]


def version_code(t):
    """안드로이드 versionCode.

    목록 순서로 매기면 안 된다. 테마 순서를 바꾸는 순간 번호가 내려가는 테마가 생기고,
    안드로이드는 versionCode 가 낮아지면 설치를 거부한다(다운그레이드로 본다).

    그래서 키 끝의 번호와 테마 버전으로 만든다. 키 번호는 안 바뀌고 버전은 올라가기만 한다.
    mixed09 + 0.13.1 -> 9 * 100000 + 1301 = 901301.

    자리를 넉넉히 잡은 이유는 품질 개선을 패치 번호로 올리기 때문이다.
    0.13 -> 0.13.1 -> 0.13.2 로 가도 번호가 계속 커져야 한다.
    """
    m = re.search(r'(\d+)$', t['key'])
    no = int(m.group(1)) if m else 1
    parts = (themes.VERSION.split('.') + ['0', '0'])[:3]
    major, minor, patch = (int(x or 0) for x in parts)
    return no * 100000 + major * 10000 + minor * 100 + patch


def gen_android(t, root, code):
    values = os.path.join(root, 'res', 'values')
    draw = os.path.join(root, 'res', 'drawable-xxhdpi')
    os.makedirs(values, exist_ok=True)
    os.makedirs(draw, exist_ok=True)

    with open(os.path.join(root, 'AndroidManifest.xml'), 'w', encoding='utf-8') as f:
        f.write(MANIFEST.format(key=t['key'], version=themes.VERSION, code=code))

    with open(os.path.join(values, 'strings.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
                '    <string name="theme_title">%s</string>\n'
                '    <string name="app_name">%s</string>\n</resources>\n'
                % (t['name'], t['name']))

    lines = ['<?xml version="1.0" encoding="utf-8"?>',
             '<!-- %s. tools/themes.py 에서 생성된다. 직접 고치지 말 것. -->' % t['name'],
             '<resources>', '']
    tok = dict(t)
    tok.update(derived(t))
    ca = t.get('cell_alpha', 1.0)
    # 셀 배경만 알파를 먹인다. 글자색까지 투명해지면 안 읽힌다
    faded = {'theme_body_cell_color', 'theme_body_secondary_cell_color',
             'theme_maintab_cell_color', 'theme_header_cell_color'}
    for name, token in COLORS:
        a = ca if name in faded else 1.0
        lines.append('    <color name="%s">%s</color>' % (name, argb(tok[token], a)))
    ba = t.get('bubble_alpha', 255) / 255.0
    lines += ['',
              '    <!-- 말풍선은 9-patch 이미지가 이긴다. 아래는 이미지가 안 먹을 때의 대비값 -->',
              '    <color name="theme_chatroom_bubble_me_color">%s</color>' % argb(mid(*t['send']), ba),
              '    <color name="theme_chatroom_bubble_you_color">%s</color>' % argb(mid(*t['recv']), ba),
              '', '</resources>', '']
    with open(os.path.join(values, 'colors.xml'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    style, alpha = t.get('bubble_style', 'solid'), t.get('bubble_alpha', 255)
    glow, pad = glow_of(t)
    for who, key in (('me', 'send'), ('you', 'recv')):
        for variant, pal in (('01', t[key]), ('02', t[key + '_alt'])):
            name = 'theme_chatroom_bubble_%s_%s_image.9.png' % (who, variant)
            ninepatch(bubble(3, pal, style, alpha, glow, pad, t.get('flat', False)),
                      (CAP + pad) * 3).save(os.path.join(draw, name))

    splash(t, 1080, 1920).save(os.path.join(draw, 'theme_splash_image.png'), optimize=True)
    if t['chat_bg']:
        background(t, t['chat_bg'], 1080, 1920).save(
            os.path.join(draw, 'theme_chatroom_background_image.png'), optimize=True)
    if t.get('main_bg'):
        background(t, t['main_bg'], 1080, 1920).save(
            os.path.join(draw, 'theme_background_image.png'), optimize=True)
    if t.get('passcode_bg'):
        background(t, t['passcode_bg'], 1080, 1920).save(
            os.path.join(draw, 'theme_passcode_background_image.png'), optimize=True)


# 미리보기와 갤러리는 tools/preview.py 가 만든다
DOCS = os.path.join(ROOT, 'docs')        # 문서만 — spec.md, index.html
ASSETS = os.path.join(ROOT, 'assets')    # 생성된 그림 — 미리보기, 아이콘, QR


def main():
    import preview                      # 순환 임포트를 피하려고 여기서 부른다
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(DOCS, exist_ok=True)
    os.makedirs(ASSETS, exist_ok=True)
    for t in themes.THEMES:
        root = os.path.join(OUT, t['key'])
        gen_ios(t, os.path.join(root, 'ios'))
        gen_android(t, os.path.join(root, 'android'), code=version_code(t))
        n = sum(len(f) for _, _, f in os.walk(root))
        extra = '  + 채팅방 배경' if t['chat_bg'] else ''
        print('%-12s %-9s 파일 %2d개%s' % (t['key'], t['name'], n, extra))
    print('\n%d 개 테마 -> build-src/' % len(themes.THEMES))
    preview.generate(themes.THEMES)
    print('미리보기 -> docs/index.html')


if __name__ == '__main__':
    main()
