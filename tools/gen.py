# -*- coding: utf-8 -*-
"""팔레트 표(tools/themes.py)에서 테마 소스 전부를 만든다.

    python tools/gen.py

결과는 build-src/<key>/ 아래. 빌드 스크립트가 그걸 읽어 .ktheme 과 .apk 로 포장한다.
생성물은 저장소에 넣지 않는다 — 원본은 팔레트 표 하나뿐이어야 한다.

iOS 와 안드로이드는 같은 그림을 다른 형식으로 요구한다.
  iOS     @2x / @3x 두 장. 늘어나는 범위는 CSS 의 cap inset 숫자로 따로 적는다.
  Android 9-patch 한 장. 늘어나는 범위를 이미지 1픽셀 테두리에 그려 넣는다.
"""
import colorsys
import math
import multiprocessing
import os
import random
import zlib
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

# 말풍선 여백 = 대화 밀도. 색을 한 글자도 안 바꾸고 인상을 바꾸는 축이다.
# 세로 여백은 말풍선 사이 간격으로도 나타나므로 가로보다 조금씩만 움직인다.
DENSITY = {
    'tight': (7, 13),
    'normal': (INSET_V, INSET_H),
    'loose': (13, 21),
}


def insets_of(t):
    """테마의 글자 여백. density 를 안 적으면 normal 이다."""
    d = t.get('density', 'normal')
    if d not in DENSITY:
        raise ValueError('%s: 모르는 density "%s". %s 중 하나'
                         % (t['key'], d, ' / '.join(DENSITY)))
    return DENSITY[d]
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


def glow_tint(h, f):
    """빛나는 가장자리 색. 흰쪽으로 당기지 않고 밝기만 올린다.

    lighten() 은 채널마다 255 쪽으로 당기므로 어둡고 진한 색일수록 회색이 된다.
    레드의 받은 말풍선(#3B0B16)이 채도 0.81 에서 0.09 로 떨어져 테두리가 잿빛이었다.
    빨간 테마인데 테두리만 회색이면 빛이 아니라 덧그린 선으로 보인다.

    밝은 파스텔은 원래 채도가 낮아 lighten 이어도 티가 안 났다 — 그래서 어떤
    테마는 예쁘고 어떤 테마는 아니었다. 색상은 그대로 두고 명도만 올린다.
    """
    r, g, b = (v / 255.0 for v in rgb(h))
    hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
    vv = vv + (1.0 - vv) * f
    ss = ss * (1.0 - f * SAT_LOSS)     # 실제 빛도 아주 밝아지면 조금은 옅어진다
    r, g, b = colorsys.hsv_to_rgb(hh, ss, vv)
    return '#%02X%02X%02X' % tuple(round(v * 255) for v in (r, g, b))


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

# 글로우가 밝아질 때 잃는 채도. 0 이면 색이 그대로라 형광펜처럼 뜨고,
# 1 이면 흰색이 되어 몸통 색과 남남이 된다.
SAT_LOSS = 0.38

# 맨 위 반사광. 순백을 얼마나 글로우 색 쪽으로 당길지(TINT)와 얼마나 진하게
# 얹을지(ALPHA). 진하면 아래 깔린 빛 띠를 덮어 위쪽만 흰 선이 된다.
SPEC_TINT, SPEC_ALPHA = 0.60, 0.35


def bubble_box(w, h, colors, radius, style='solid', alpha=255, glow=None, pad=0,
               flat=False, rim=None, frost=0.0):
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
        # 유리판의 가장자리에서 빛은 두 번 꺾인다. 위쪽에 밝은 선이 서고
        # 아래쪽에는 어두운 선이 남는다. 밝은 선만 그리면 흰 바탕 위에서는
        # 아무것도 안 보인다 — 라이트 유리가 밋밋했던 게 이것 때문이다.
        # 색 테두리는 흰 선보다 굵어야 보인다. 흰 선은 밝기로 눈에 띄지만
        # 색은 1픽셀이면 그냥 어두운 선으로 뭉개진다.
        rim_w = int(SS * (2.0 if rim else 1.0))

        def edge(color, ramp_fn):
            rim_img = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
            ImageDraw.Draw(rim_img).rounded_rectangle(
                [SS // 2, SS // 2, w * SS - SS // 2 - 1, h * SS - SS // 2 - 1],
                radius=radius * SS, outline=color, width=rim_w)
            rim_img = rim_img.resize((w, h), Image.LANCZOS)
            ramp = Image.new('L', (1, h))
            px = ramp.load()
            for y in range(h):
                px[0, y] = max(0, min(255, ramp_fn(y / max(h - 1, 1))))
            faded = ImageChops.multiply(rim_img.getchannel('A'), ramp.resize((w, h)))
            rim_img.putalpha(ImageChops.multiply(faded, mask))
            return rim_img

        # 위아래 테두리 색. 기본은 흰 선과 검은 선이고, rim 을 주면 그 두 색으로
        # 갈라진다 — 유리 모서리에서 빛이 파장별로 꺾이는 것을 흉내내는 자리다.
        top_c = rgb(rim[0]) + (255,) if rim else (255, 255, 255, 230)
        bot_c = rgb(rim[1]) + (235,) if rim else (0, 0, 0, 105)
        out.alpha_composite(edge(top_c,
                                 lambda t: int(255 * max(0.0, 1.0 - t * 1.45))))
        out.alpha_composite(edge(bot_c,
                                 lambda t: int(255 * max(0.0, (t - 0.30) * 1.5))))

        # 판 안쪽 위에 옅은 띠 하나. 유리가 종이가 아니라 두께가 있는 판으로 읽힌다.
        sheen_h = max(3, int(h * 0.45))
        grad = Image.new('L', (1, sheen_h))
        gp = grad.load()
        for y in range(sheen_h):
            gp[0, y] = int(64 * (1.0 - y / max(sheen_h - 1, 1)) ** 1.5)
        sh = Image.new('L', (w, h), 0)
        sh.paste(grad.resize((w, sheen_h)), (0, 0))
        band = Image.new('RGBA', (w, h), (255, 255, 255, 255))
        band.putalpha(ImageChops.multiply(sh, mask))
        out.alpha_composite(band)

        if frost:
            # 젖빛. 진짜 젖빛 유리는 뒤를 흐리게 하는데 우리는 PNG 한 장만 줄 수
            # 있어서 그건 안 된다. 대신 유리 안에 밝고 어두운 알갱이를 뿌려
            # 표면이 거칠어 보이게 한다. Image.effect_noise 는 씨앗을 못 줘서
            # 돌릴 때마다 그림이 달라지므로 직접 뽑는다.
            rnd = random.Random(w * 7919 + h * 104729 + int(frost * 1000))
            grain = Image.new('L', (w, h))
            gp = grain.load()
            amp = int(110 * frost)
            for y in range(h):
                for x in range(w):
                    gp[x, y] = 128 + rnd.randint(-amp, amp)
            # 흐려서 알갱이를 뭉친다. 픽셀 하나짜리 잡음은 유리가 아니라 TV 화면이다.
            # 흐리면 높은 주파수가 빠져서 PNG 도 같이 작아진다.
            grain = grain.filter(ImageFilter.GaussianBlur(max(1.0, w * 0.018)))
            lay = Image.new('RGBA', (w, h), (255, 255, 255, 255))
            lay.putalpha(ImageChops.multiply(
                grain.point(lambda v: int(max(0, v - 128) * 3.2)), mask))
            out.alpha_composite(lay)
            dk = Image.new('RGBA', (w, h), (0, 0, 0, 255))
            dk.putalpha(ImageChops.multiply(
                grain.point(lambda v: int(max(0, 128 - v) * 2.2)), mask))
            out.alpha_composite(dk)

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

        inner = Image.new('RGBA', (w, h), rgb(glow_tint(base, 0.66)) + (255,))
        inner.putalpha(band.point(lambda v: min(255, int(v * 2.1))))
        out.alpha_composite(inner)

        # 맨 위 모서리에만 얇은 반사광. 유리나 금속에서 보이는 그 선
        spec_h = max(2, int(h * 0.16))
        sp = ImageChops.subtract(
            mask, mask.filter(ImageFilter.GaussianBlur(max(1.0, min(w, h) * 0.012))))
        top = Image.new('L', (w, h), 0)
        top.paste(sp.crop((0, 0, w, spec_h)), (0, 0))
        top = ImageChops.multiply(top, mask)
        # 반사광은 환경의 흰빛이라 흰색이 맞지만, 순백을 진하게 얹으면 아래 깔린
        # 빛 띠를 덮어버려 위쪽만 색이 사라진다. 진한 색 위에서 그게 흰 연필선으로
        # 보였다. 글로우 색을 조금 섞고 옅게 얹어, 띠 위에 덧나게만 한다.
        spec_c = mix('#FFFFFF', glow_tint(base, 0.88), SPEC_TINT)
        sheen = Image.new('RGBA', (w, h), rgb(spec_c) + (255,))
        sheen.putalpha(top.point(lambda v: min(255, int(v * SPEC_ALPHA))))
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
    halo.paste(Image.new('RGB', (gw, gh), rgb(glow_tint(base, 0.55))), (0, 0), core)
    halo.putalpha(acc.point(lambda v: int(v * ga / 255)))
    halo.alpha_composite(out, (pad, pad))
    return halo


def bubble(scale, colors, style='solid', alpha=255, glow=None, pad=0, flat=False,
           rim=None, frost=0.0):
    """안드로이드 9-patch 와 iOS 용 정사각 말풍선."""
    return bubble_box(SIZE * scale, SIZE * scale, colors, RADIUS * scale,
                      style, alpha, glow, pad * scale, flat, rim, frost)


def glass_of(t):
    """유리 테마가 말풍선에 넘기는 값 — 테두리 색 두 개와 젖빛 세기.

    rim 을 안 적으면 흰 선과 검은 선이다. 프리즘은 여기에 시안과 마젠타를 넣어
    유리 모서리에서 빛이 갈라지는 것을 흉내낸다.
    """
    return t.get('rim'), t.get('frost', 0.0)


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
    seed = o.get('seed', 20260912)
    unit = w / 500.0
    img = vgradient(w, h, rgb(spec[1]), rgb(spec[2])).convert('RGB')

    # 하늘에 아주 옅은 잡음을 섞는다. 매끈한 그라데이션은 띠(밴딩)가 보인다
    # 잡음을 살짝 흐려서 섞는다. 픽셀 단위 잡음은 PNG 가 못 줄여서 파일이 몇 배로 커진다.
    # 흐린 잡음도 띠를 깨는 데는 충분하다.
    #
    # 잡음도 씨앗을 받아야 한다. PIL 의 effect_noise 는 파이썬 random 이 아니라
    # C 쪽 난수를 쓰고 씨앗을 줄 자리가 없어서, 별만 고정되고 잡음은 돌릴 때마다
    # 달라졌다. 그래서 심야 그림 여덟 장이 미리보기를 돌릴 때마다 diff 에 떴다.
    #
    # 픽셀 하나씩 뽑는다. 절반 크기로 만들어 키우면 1.2초가 0.4초가 되지만,
    # 키울 때 생긴 두 픽셀짜리 알갱이가 1.1 픽셀 흐림을 견뎌서 PNG 가 두 배로
    # 커진다(108KB -> 197KB). 흐림을 1.6 으로 올리면 크기는 돌아오지만 그때는
    # 그림이 예전과 달라진다. 여기서는 속도보다 예전 그대로가 낫다.
    # 별과는 다른 난수를 쓴다 — 같은 것을 쓰면 뽑는 차례가 밀려 별자리까지 바뀐다.
    nr = random.Random(seed ^ 0x5EED)
    noise = Image.frombytes('L', (w, h), bytes(
        min(255, max(0, int(nr.gauss(128, 7)))) for _ in range(w * h)))
    noise = noise.filter(ImageFilter.GaussianBlur(1.1)).convert('RGB')
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
    rnd = random.Random(seed)
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
        cr = random.Random(_opts(spec).get('seed', 77) + 77)
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



def _opts(spec):
    """배경 규격 끝에 붙는 선택값 묶음. 없으면 빈 것."""
    return spec[3] if len(spec) > 3 and isinstance(spec[3], dict) else {}


def seeded(spec, t):
    """배경 그림의 난수 씨앗을 테마마다 다르게 준다.

    장면마다 씨앗이 하나씩 박혀 있으면 같은 장면을 쓰는 테마가 전부 같은 그림이 된다.
    한 계열 안에서도 마찬가지라 심야 배경과 심야 글로우+배경이 별 하나까지 똑같았다.
    파일은 둘인데 그림이 같으면 왜 둘인지 알 수 없다.

    씨앗은 키에서 만든다 — 같은 테마를 다시 돌리면 같은 그림이 나와야 한다.
    """
    o = dict(_opts(spec))
    if 'seed' not in o:
        o['seed'] = zlib.crc32(t['key'].encode('utf-8')) % 90000000 + 10000000
    base = tuple(spec[:3]) if len(spec) >= 3 else tuple(spec)
    return base + (o,)


def chat_bg(spec, w, h):
    kind = spec[0]
    if kind == 'night':
        return scene_night(spec, w, h)
    import scenes                          # 늦게 부른다. scenes 가 gen 을 쓴다
    fn = getattr(scenes, kind, None)
    if fn:
        return fn(spec, w, h)
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
        base = base.filter(ImageFilter.GaussianBlur(radius=w // 5))
        # 예전에는 0.7 로 섞어서 색 덩어리가 거의 안 보였다. 뒤가 비어 있으면
        # 반투명 말풍선이 그냥 흐린 판으로 보인다 — 유리로 안 읽힌다.
        return Image.blend(Image.new('RGB', (w, h), rgb(spec[1])), base, 0.88)
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


def light_wash(img, color, strength):
    """배경에 빛을 얹는다.

    사방 테두리를 똑같이 밝히면 액자처럼 보인다 — 실제 빛은 한 방향에서 든다.
    화면 밖 왼쪽 위에 광원을 두고 대각선으로 흘린 뒤, 반대쪽 아래 구석을 살짝 누른다.
    밝은 쪽과 어두운 쪽이 생겨야 평면이 아니라 공간으로 읽힌다.
    """
    w, h = img.size
    out = img.convert('RGBA')

    # 광원. 화면 밖에 두어 가장자리에 경계가 안 생기게 한다
    lx, ly = -w * 0.25, -h * 0.15
    r = max(w, h) * 1.45
    glow = Image.new('L', (w, h), 0)
    gd = ImageDraw.Draw(glow)
    steps = 56
    for i in range(steps, 0, -1):
        f = i / steps
        rr = r * f
        gd.ellipse([lx - rr, ly - rr, lx + rr, ly + rr],
                   fill=int(strength * (1 - f) ** 1.8))
    glow = glow.filter(ImageFilter.GaussianBlur(w * 0.06))
    layer = Image.new('RGBA', (w, h), rgb(color) + (255,))
    layer.putalpha(glow)
    out.alpha_composite(layer)

    # 반대쪽 구석을 눌러 깊이를 만든다
    shade = Image.new('L', (w, h), 0)
    sd = ImageDraw.Draw(shade)
    sx, sy = w * 1.2, h * 1.15
    sr = max(w, h) * 1.3
    for i in range(steps, 0, -1):
        f = i / steps
        rr = sr * f
        sd.ellipse([sx - rr, sy - rr, sx + rr, sy + rr],
                   fill=int(strength * 0.55 * (1 - f) ** 2.0))
    shade = shade.filter(ImageFilter.GaussianBlur(w * 0.08))
    dark = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    dark.putalpha(shade)
    out.alpha_composite(dark)
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
    -kakaotalk-theme-id: 'com.kakao.talk.theme.{pkg}';
}}

TabBarStyle-Main
{{
    background-color: {bg};
{tabicons}}}

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

ButtonStyle-AddFriend
{{
    -ios-image: 'findBtnAddFriend.png';
}}

DefaultProfileStyle
{{
    -ios-profile-images: {profiles};
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
    -ios-keypad-number-highlighted-image: 'passcodeKeypadPressed.png';
{bullets}}}

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


def background(t, spec, w, h, flat=False):
    """배경 이미지 한 장. 테마에 글로우가 있으면 빛을 얹는다.

    flat 은 목록 화면용이다. 카톡이 목록 위에 불투명한 것을 잔뜩 얹는다 —
    칩 줄, 광고 카드, 셀. 배경에 굴곡이 있으면 얹힌 자리마다 잘린 자국이 보인다.
    그래서 목록 배경은 그림이 아니라 질감이어야 한다. 크게 흐리고 대비를 죽인다.
    채팅방과 잠금화면은 얹히는 게 적어서 그림 그대로 쓴다.
    """
    img = chat_bg(seeded(spec, t), w, h)
    # 나무결처럼 방향만 있고 굴곡이 없는 질감은 흐리지 않는다. 어디서 잘라도
    # 같은 무늬라 위에 무엇이 얹혀도 잘린 자국이 안 생긴다 — 흐리면 그냥 갈색 판이 된다.
    if flat and not t.get('flat_list', True):
        flat = False
    if flat:
        img = img.filter(ImageFilter.GaussianBlur(w * 0.14))
        mid_c = img.resize((1, 1), Image.LANCZOS).getpixel((0, 0))
        img = Image.blend(img, Image.new('RGB', (w, h), mid_c), 0.55)
    g = t.get('glow')
    if g:
        # 배경에는 말풍선처럼 따라갈 색이 없다. auto 면 포인트색을 쓴다
        color = t['accent'] if g[0] == 'auto' else g[0]
        # 배경은 면적이 넓어서 말풍선과 같은 세기로 넣으면 화면이 뿌예진다
        img = light_wash(img, color, int(g[1] * 0.8))
    return img


def gen_ios(t, root):
    img_dir = os.path.join(root, 'Images')
    os.makedirs(img_dir, exist_ok=True)

    style, alpha = t.get('bubble_style', 'solid'), t.get('bubble_alpha', 255)
    glow, pad = glow_of(t)
    rim, frost = glass_of(t)
    for side, key in (('Send', 'send'), ('Receive', 'recv')):
        for variant, pal in (('01', t[key]), ('02', t[key + '_alt'])):
            for scale in (2, 3):
                name = 'chatroomBubble%s%s@%dx.png' % (side, variant, scale)
                bubble(scale, pal, style, alpha, glow, pad,
                       t.get('flat', False), rim, frost).save(
                    os.path.join(img_dir, name))

    icon(t, 120).save(os.path.join(img_dir, 'commonIcoTheme.png'))

    # 탭 아이콘 7종 × 보통/선택. 보통은 보조색, 선택은 포인트색 —
    # 둘이 다른 그림이라 탭을 누를 때 카톡이 사이를 이어준다.
    tab_lines = []
    for kind in TAB_KINDS:
        name = 'maintabIco' + kind.capitalize()
        for suffix, col in (('', t['subtext']), ('Selected', t['accent'])):
            for scale in (2, 3):
                tab_icon(kind, 28 * scale, col).save(
                    os.path.join(img_dir, '%s%s@%dx.png' % (name, suffix, scale)))
        tab_lines.append("    -ios-%s-normal-icon-image: '%s.png';" % (kind, name))
        tab_lines.append("    -ios-%s-selected-icon-image: '%sSelected.png';"
                         % (kind, name))
    tabicons = chr(10).join(tab_lines) + chr(10)

    # 친구추가 단추. iOS 는 눌린 그림 자리가 따로 없어 한 장만 쓴다
    for scale, px in ((2, 48), (3, 72)):
        add_friend_icon(t, px).save(
            os.path.join(img_dir, 'findBtnAddFriend@%dx.png' % scale))

    # 잠금화면 — 키패드 눌림과 네 자리 동그라미
    for scale, px in ((2, 128), (3, 192)):
        keypad_pressed(t, px).save(
            os.path.join(img_dir, 'passcodeKeypadPressed@%dx.png' % scale))
    bullet_lines = []
    for i, slot in enumerate(BULLET_SLOTS):
        nm = 'passcodeImgCode%02d' % (i + 1)
        for scale, px in ((2, 36), (3, 54)):
            bullet_image(t, i, px, False).save(
                os.path.join(img_dir, '%s@%dx.png' % (nm, scale)))
            bullet_image(t, i, px, True).save(
                os.path.join(img_dir, '%sSelected@%dx.png' % (nm, scale)))
        bullet_lines.append("    -ios-bullet-%s-image: '%s.png';" % (slot, nm))
        bullet_lines.append("    -ios-bullet-selected-%s-image: '%sSelected.png';"
                            % (slot, nm))
    bullets = chr(10).join(bullet_lines) + chr(10)

    names = []
    for i in range(3):
        nm = 'profileImg%02d' % (i + 1)
        for scale, px in ((2, 108), (3, 162)):
            profile_image(t, i, px).save(
                os.path.join(img_dir, '%s@%dx.png' % (nm, scale)))
        names.append("'%s.png'" % nm)
    profiles = ' '.join(names)

    chatbg = ''
    if t['chat_bg']:
        background(t, t['chat_bg'], 600, 1300).save(os.path.join(img_dir, 'chatroomBgImage@2x.png'))
        background(t, t['chat_bg'], 900, 1950).save(os.path.join(img_dir, 'chatroomBgImage@3x.png'))
        chatbg = "\n    -ios-background-image: 'chatroomBgImage.png';"

    mainbg = ''
    if t.get('main_bg'):
        background(t, t['main_bg'], 600, 1300, flat=True).save(
            os.path.join(img_dir, 'mainBgImage@2x.png'))
        background(t, t['main_bg'], 900, 1950, flat=True).save(
            os.path.join(img_dir, 'mainBgImage@3x.png'))
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
    fields['pkg'] = themes.pkg_slug(t)
    fields.pop('cell_alpha', None)          # 아래에서 문자열로 다시 넣는다
    iv, ih = insets_of(t)
    ins = '%dpx %dpx %dpx %dpx' % (iv + pad, ih + pad, iv + pad, ih + pad)
    css = CSS.format(version=themes.VERSION, cap=CAP + pad, ins=ins,
                     tabicons=tabicons, profiles=profiles, bullets=bullets,
                     chatbg=chatbg, mainbg=mainbg, passbg=passbg,
                     cell_alpha='%.2f' % ca,
                     cell_alpha_sel='%.2f' % min(1.0, ca + 0.15), **fields)
    with open(os.path.join(root, 'KakaoTalkTheme.css'), 'w', encoding='utf-8', newline='\n') as f:
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
    package="com.kakao.talk.theme.{pkg}"
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

    with open(os.path.join(root, 'AndroidManifest.xml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(MANIFEST.format(pkg=themes.pkg_slug(t), version=themes.VERSION,
                                code=code))

    with open(os.path.join(values, 'strings.xml'), 'w', encoding='utf-8', newline='\n') as f:
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
    with open(os.path.join(values, 'colors.xml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))

    style, alpha = t.get('bubble_style', 'solid'), t.get('bubble_alpha', 255)
    glow, pad = glow_of(t)
    for who, key in (('me', 'send'), ('you', 'recv')):
        for variant, pal in (('01', t[key]), ('02', t[key + '_alt'])):
            name = 'theme_chatroom_bubble_%s_%s_image.9.png' % (who, variant)
            ninepatch(bubble(3, pal, style, alpha, glow, pad, t.get('flat', False),
                             *glass_of(t)),
                      (CAP + pad) * 3).save(os.path.join(draw, name))

    for kind in TAB_KINDS:
        for suffix, col in (('', t['subtext']), ('_focused', t['accent'])):
            tab_icon(kind, 84, col).save(
                os.path.join(draw, 'theme_maintab_ico_%s%s_image.png' % (kind, suffix)))

    for i in range(3):
        profile_image(t, i, 162).save(
            os.path.join(draw, 'theme_profile_%02d_image.png' % (i + 1)))

    tabbar_image(t).save(os.path.join(draw, 'theme_maintab_cell_image.png'))

    # 친구추가 단추. 안드로이드는 눌린 그림을 따로 받는다
    add_friend_icon(t, 72).save(
        os.path.join(draw, 'theme_find_add_friend_button_image.png'))
    add_friend_icon(t, 72, pressed=True).save(
        os.path.join(draw, 'theme_find_add_friend_button_pressed_image.png'))

    # 잠금화면 동그라미 네 자리 × 빈 것/채운 것
    for i in range(4):
        bullet_image(t, i, 54).save(
            os.path.join(draw, 'theme_passcode_%02d_image.png' % (i + 1)))
        bullet_image(t, i, 54, True).save(
            os.path.join(draw, 'theme_passcode_%02d_checked_image.png' % (i + 1)))

    splash(t, 1080, 1920).save(os.path.join(draw, 'theme_splash_image.png'), optimize=True)
    if t['chat_bg']:
        background(t, t['chat_bg'], 1080, 1920).save(
            os.path.join(draw, 'theme_chatroom_background_image.png'), optimize=True)
    if t.get('main_bg'):
        background(t, t['main_bg'], 1080, 1920, flat=True).save(
            os.path.join(draw, 'theme_background_image.png'), optimize=True)
    if t.get('passcode_bg'):
        background(t, t['passcode_bg'], 1080, 1920).save(
            os.path.join(draw, 'theme_passcode_background_image.png'), optimize=True)


# 미리보기와 갤러리는 tools/preview.py 가 만든다
DOCS = os.path.join(ROOT, 'docs')        # 문서만 — spec.md, index.html
ASSETS = os.path.join(ROOT, 'assets')    # 생성된 그림 — 미리보기, 아이콘, QR


def build_one(t):
    """테마 한 벌을 만들고 한 줄 보고를 돌려준다. 워커 프로세스가 이걸 부른다.

    테마끼리 공유하는 것이 없다 — 폴더가 다르고, build-tmp 도 따로 쓰고, 난수
    씨앗은 키에서 나온다. 그래서 몇 개를 동시에 돌려도 나오는 그림이 같다.
    """
    # 폴더 이름이 곧 배포 파일 이름이 된다. 빌드 스크립트가 폴더명을 그대로 쓴다.
    root = os.path.join(OUT, themes.file_slug(t))
    gen_ios(t, os.path.join(root, 'ios'))
    gen_android(t, os.path.join(root, 'android'), code=version_code(t))
    n = sum(len(f) for _, _, f in os.walk(root))
    extra = '  + 채팅방 배경' if t['chat_bg'] else ''
    return '%-18s %-14s 파일 %2d개%s' % (themes.file_slug(t), t['name'], n, extra)


def workers():
    """동시에 돌릴 수. 코어를 다 쓰되 8을 넘기지 않는다.

    테마 하나가 1080x1920 배경을 여러 장 물고 있어서, 코어가 많은 기계에서
    전부 띄우면 메모리로 먼저 막힌다. 그 위로는 더 빨라지지도 않는다.
    """
    return max(1, min(os.cpu_count() or 1, 8))


def main():
    import preview                      # 순환 임포트를 피하려고 여기서 부른다
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(DOCS, exist_ok=True)
    os.makedirs(ASSETS, exist_ok=True)

    # 테마를 여러 프로세스에 나눠 만든다. 시간을 먹는 것은 배경 그림인데 그건
    # 순수 계산이라 파이썬 스레드로는 못 나눈다(GIL). imap 은 끝난 차례가 아니라
    # 건네준 차례로 돌려주므로 출력 순서는 직렬로 돌릴 때와 같다.
    n = workers()
    with multiprocessing.Pool(n) as pool:
        for line in pool.imap(build_one, themes.THEMES):
            print(line, flush=True)
    print('\n%d 개 테마 -> build-src/  (%d개씩 동시에)' % (len(themes.THEMES), n))
    preview.generate(themes.THEMES)
    print('미리보기 -> docs/index.html')


# --- 기본 프로필 ---------------------------------------------------------
# 사진 없는 친구에게 뜨는 그림. 규격에서 유일하게 여러 장을 받는 자리다 —
# 세 장을 주면 앱이 친구마다 돌려가며 배정해서 목록에 세 가지가 섞여 보인다.
# 가이드에 162x162 px 로 적혀 있다.

def profile_image(t, idx, px):
    """기본 프로필 한 장. 세 장이 서로 다른 색이라야 목록에서 섞인 티가 난다."""
    ss = 4
    S = px * ss
    tone = (t['accent'], t['subtext'], t['accent_dim'])[idx % 3]
    back = (t['surface'], t['pressed'], t['bg_deep'])[idx % 3]
    img = Image.new('RGBA', (S, S), rgb(back) + (255,))
    d = ImageDraw.Draw(img)
    c = rgb(tone) + (255,)
    d.ellipse([S * 0.32, S * 0.20, S * 0.68, S * 0.56], fill=c)      # 머리
    d.pieslice([S * 0.16, S * 0.52, S * 0.84, S * 1.10], 180, 360, fill=c)
    return img.resize((px, px), Image.LANCZOS)


# --- 탭 아이콘 -----------------------------------------------------------
# 7종 × 보통/선택. 규격에 있는데 지금까지 안 써서 스물한 테마가 전부 카톡 기본
# 아이콘을 쓰고 있었다. 팔레트 색으로 그리면 테마마다 하단이 달라진다.
# 보통과 선택이 별개 그림이라 탭을 누를 때 전환도 생긴다.

# --- 잠금화면과 친구추가 단추 ---------------------------------------------
# 규격에서 마지막까지 안 쓰고 남아 있던 자리들이다. 색만 바꾸면 이 자리들은
# 카톡 기본 그림 그대로 남아서, 테마를 깔아도 여기만 남의 집처럼 보인다.

def bullet_color(t, idx):
    """비밀번호 네 자리의 색.

    자리마다 다른 이미지를 넣을 수 있다. 말풍선 네 칸에서 색을 하나씩 빌려와
    다 채웠을 때 팔레트가 한 줄로 늘어서게 한다. 받은 말풍선의 어두운 칸은
    빼고 쓴다 — 어두운 바탕에 어두운 점을 찍으면 안 보인다.
    """
    pals = (t['send'], t['send_alt'], t['recv_alt'])
    cols = [mid(*p) for p in pals] + [t['accent']]
    c = cols[idx % 4]

    # 바탕과 밝기가 비슷하면 점이 안 보인다. 빈 점은 테두리뿐이라 특히 그렇다.
    # 그럴 때만 글자색 쪽으로 당긴다 — 색상은 살리고 밝기만 벌린다.
    def lum(h):
        r, g, b = rgb(h)
        return (r * 299 + g * 587 + b * 114) / 1000
    base = t.get('bg_deep') or t['bg']
    if abs(lum(c) - lum(base)) < 70:
        c = mix(c, t['text'], 0.45)
    return c


def bullet_image(t, idx, px, checked=False):
    """비밀번호 점 하나. 빈 것은 테두리만, 채운 것은 속까지 칠한다."""
    c = rgb(bullet_color(t, idx))
    S = px * SS
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = int(S * 0.32)                      # 둘레에 여백을 남긴다. 글로우가 들어갈 자리다
    box = [S // 2 - r, S // 2 - r, S // 2 + r, S // 2 + r]
    if checked:
        d.ellipse(box, fill=c + (255,))
    else:
        d.ellipse(box, outline=c + (130,), width=max(SS, int(S * 0.055)))
    img = img.resize((px, px), Image.LANCZOS)

    if checked and t.get('glow'):
        halo = img.getchannel('A').filter(ImageFilter.GaussianBlur(px * 0.10))
        lay = Image.new('RGBA', (px, px), rgb(lighten(bullet_color(t, idx), 0.5)) + (255,))
        lay.putalpha(halo.point(lambda v: int(v * 0.55)))
        out = Image.new('RGBA', (px, px), (0, 0, 0, 0))
        out.alpha_composite(lay)
        out.alpha_composite(img)
        return out
    return img


def keypad_pressed(t, px):
    """키패드 숫자를 눌렀을 때 뒤에 깔리는 동그라미."""
    S = px * SS
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = int(S * 0.46)
    d.ellipse([S // 2 - r, S // 2 - r, S // 2 + r, S // 2 + r],
              fill=rgb(t['pressed']) + (255,))
    if t.get('glow'):
        d.ellipse([S // 2 - r, S // 2 - r, S // 2 + r, S // 2 + r],
                  outline=rgb(t['accent']) + (160,), width=max(SS, int(S * 0.02)))
    return img.resize((px, px), Image.LANCZOS)


def add_friend_icon(t, px, pressed=False):
    """친구 탭 머리의 친구추가 단추. 사람 옆에 더하기 하나."""
    c = rgb(t['accent'] if pressed else t['text'])
    S = px * SS
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 사람 — 머리와 어깨. 어깨는 반원이라 아래를 잘라 쓴다
    hr = int(S * 0.145)
    hx, hy = int(S * 0.37), int(S * 0.30)
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=c + (255,))
    bw, bh = int(S * 0.23), int(S * 0.22)
    d.pieslice([hx - bw, hy + int(S * 0.10), hx + bw, hy + int(S * 0.10) + bh * 2],
               180, 360, fill=c + (255,))

    # 더하기
    px_, py = int(S * 0.76), int(S * 0.30)
    th = max(SS, int(S * 0.045))
    arm = int(S * 0.11)
    d.rounded_rectangle([px_ - arm, py - th, px_ + arm, py + th],
                        radius=th, fill=c + (255,))
    d.rounded_rectangle([px_ - th, py - arm, px_ + th, py + arm],
                        radius=th, fill=c + (255,))
    return img.resize((px, px), Image.LANCZOS)

def tabbar_image(t, w=12, h=168):
    """탭바 배경. 위로 갈수록 밝은 아주 옅은 그라데이션과 머리선 하나.

    안드로이드에만 넣는다(`theme_maintab_cell_image`). iOS 가이드에는 탭바에
    이미지를 넣는 속성이 없어서 색으로만 칠한다 — 이름을 지어내지 않는다.

    셀마다 깔리는 그림일 수도 있어서 가로로는 아무 변화를 주지 않는다.
    가로로 무늬가 있으면 셀이 나뉜 자리마다 끊긴 자국이 보인다.
    """
    img = vgradient(w, h, rgb(t['surface']), rgb(t['bg'])).convert('RGBA')
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 1], fill=rgb(t['border']) + (255,))
    a = int(round(t.get('cell_alpha', 1.0) * 255))
    if a < 255:                      # 유리 테마는 탭바도 비쳐야 한다
        img.putalpha(Image.new('L', (w, h), a))
    return img

BULLET_SLOTS = ('first', 'second', 'third', 'fourth')

TAB_KINDS = ('friends', 'chats', 'browse', 'find', 'piccoma', 'shopping', 'more')


def tab_icon(kind, px, color, ss=4):
    """탭 아이콘 하나. 채운 도형으로 그린다 — 작은 크기에서 선보다 잘 읽힌다."""
    S = px * ss
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = rgb(color) + (255,)
    u = S / 100.0                      # 100 기준 좌표로 그린다
    lw = max(1, int(7 * u))

    if kind == 'friends':
        d.ellipse([36 * u, 16 * u, 64 * u, 44 * u], fill=c)
        d.pieslice([20 * u, 44 * u, 80 * u, 96 * u], 180, 360, fill=c)
    elif kind == 'chats':
        d.rounded_rectangle([14 * u, 20 * u, 86 * u, 70 * u], radius=16 * u, fill=c)
        d.polygon([(30 * u, 66 * u), (48 * u, 66 * u), (30 * u, 88 * u)], fill=c)
    elif kind == 'browse':
        d.ellipse([16 * u, 16 * u, 84 * u, 84 * u], outline=c, width=lw)
        d.polygon([(42 * u, 34 * u), (70 * u, 50 * u), (42 * u, 66 * u)], fill=c)
    elif kind == 'find':
        d.ellipse([20 * u, 18 * u, 68 * u, 66 * u], outline=c, width=lw)
        d.line([(62 * u, 60 * u), (82 * u, 82 * u)], fill=c, width=lw)
    elif kind == 'piccoma':
        d.rounded_rectangle([20 * u, 18 * u, 80 * u, 82 * u], radius=8 * u, fill=c)
        d.line([(50 * u, 22 * u), (50 * u, 78 * u)],
               fill=(0, 0, 0, 0), width=max(2, int(5 * u)))
        d.rectangle([47 * u, 18 * u, 53 * u, 82 * u], fill=(0, 0, 0, 0))
    elif kind == 'shopping':
        d.rounded_rectangle([22 * u, 38 * u, 78 * u, 84 * u], radius=8 * u, fill=c)
        d.arc([36 * u, 14 * u, 64 * u, 54 * u], 180, 360, fill=c, width=lw)
    elif kind == 'more':
        for k in (-26, 0, 26):
            d.ellipse([(50 + k - 8) * u, 42 * u, (50 + k + 8) * u, 58 * u], fill=c)
    else:
        raise ValueError('모르는 탭 아이콘: %s' % kind)

    return img.resize((px, px), Image.LANCZOS)


if __name__ == '__main__':
    main()
