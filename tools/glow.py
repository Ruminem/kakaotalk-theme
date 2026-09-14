# -*- coding: utf-8 -*-
"""말풍선 글로우 모양 사전.

글로우는 카톡이 그리는 것이 아니라 우리가 말풍선 그림 안에 그려 넣는다. 그래서 모양을 마음대로
바꿀 수 있는데, 테마마다 손으로 짜면 계열마다 빛이 제각각이 되고 같은 실수를 되풀이한다.
이름 붙은 모양을 여기 모아 두고 테마는 이름으로 고른다.

고르는 차례
  1. 테마에 glow_style 이 있으면 그것
  2. 없으면 재질(material)의 기본값(MATERIAL)
  3. 둘 다 없고 char_glow 가 있으면 'char' — 0.29 부터 나간 캐릭터 계열의 글로우 그대로

지키는 것
  - 흐림은 반경의 세 배까지 퍼지는데 여백은 그보다 좁다. 장 끝에서 빛이 잘리면 말풍선 둘레에
    네모가 뜨므로 새 모양은 전부 가장자리에서 0 으로 사그라든다(_edge_fade).
  - 글로우 여백은 카톡이 말풍선 칸으로 친다. 넓게 번질수록 말풍선 사이가 벌어진다(MAX_MARGIN).
  - 말풍선은 한 줄을 늘여 긴 말을 만든다. 둘레에 고르거나 위아래로만 세기가 바뀌는 빛만 쓴다.
    점박이·줄무늬처럼 한 줄씩 무늬가 있는 빛은 늘어날 때 뭉개지므로 모양으로 넣지 않는다.
  - 'char' 는 기존 테마의 그림이 한 픽셀도 바뀌면 안 되므로 옛 계산을 그대로 옮겼다. 고치지 않는다.

치수는 pt 다. s 를 곱해 픽셀로 바꾼다.
"""
import colorsys
import math

from PIL import Image, ImageChops, ImageFilter

MAX_MARGIN = 18      # pt. 이보다 넓게 번지면 연달아 보낸 말풍선 사이가 너무 벌어진다
RIM = 2.6            # pt. 빛이 나오는 테두리 띠의 굵기


def _g():
    """gen 을 늦게 불러온다. gen → charbubble → glow 순으로 불러오므로 위에서 부르면 순환한다."""
    import gen
    return gen


def _c(v):
    return v[0] if isinstance(v, (tuple, list)) else v


def _rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hue(col, dh):
    r, g, b = (v / 255.0 for v in _rgb(col))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    r, g, b = colorsys.hsv_to_rgb((h + dh) % 1.0, s, v)
    return '#%02X%02X%02X' % tuple(int(q * 255) for q in (r, g, b))


def _gain(m, k):
    return m.point(lambda v: min(255, int(v * k)))


def _cut(m, c=10):
    """옅은 꼬리를 자른다. 남겨두면 장 전체에 알파가 깔려 네모가 된다."""
    return m.point(lambda v: 0 if v < c else v)


def _layers(src, s, spec):
    """(반경pt, 세기) 여러 겹을 흐려 더한다. 가까운 빛과 먼 빛을 한 번에 만든다."""
    out = Image.new('L', src.size, 0)
    for r, k in spec:
        out = ImageChops.add(out, _gain(src.filter(ImageFilter.GaussianBlur(r * s)), k))
    return out


# --- 모양 -----------------------------------------------------------------
# fn(rim, a, s, col) -> [(색, 알파), ...] 아래에서 위로 얹는다.
#   rim 은 말풍선 테두리 띠, a 는 말풍선 전체 알파, col 은 빛의 색이다.

def g_soft(rim, a, s, col):
    return [(_g().mix(col, '#FFFFFF', 0.2), _cut(_layers(rim, s, [(0.8, 1.4), (2.2, 1.3), (5.0, 1.1)])))]


def g_bloom(rim, a, s, col):
    wide = _cut(_gain(_layers(rim, s, [(9.0, 2.6)]), 0.75), 6)
    mid = _cut(_layers(rim, s, [(3.0, 2.0)]))
    hot = _cut(_layers(rim, s, [(1.0, 2.4)]))
    return [(col, wide), (col, mid), (_g().glow_tint(col, 0.6), hot)]


def g_led(rim, a, s, col):
    return [(col, _cut(_layers(rim, s, [(0.6, 1.9), (1.4, 1.3)]), 16))]


def g_wall(rim, a, s, col):
    wash = _cut(_gain(_layers(rim, s, [(12.0, 3.2)]), 0.55), 5)
    near = _cut(_layers(rim, s, [(1.0, 1.4), (3.0, 1.1)]))
    return [(_g().mix(col, '#000000', 0.15), wash), (col, near)]


def g_drop(rim, a, s, col):
    near = _cut(_layers(rim, s, [(1.0, 1.4), (2.5, 1.0)]))
    w, h = rim.size
    shifted = Image.new('L', (w, h), 0)
    shifted.paste(rim, (0, int(5 * s)))
    fall = _layers(shifted, s, [(4.5, 2.6)])
    # 세로로만 세기가 바뀐다. 가로로 늘어나도 괜찮다
    ramp = Image.new('L', (1, h))
    ramp.putdata([int(255 * (0.25 + 0.75 * (y / max(1, h - 1)) ** 1.6)) for y in range(h)])
    fall = _cut(ImageChops.multiply(fall, ramp.resize((w, h))), 6)
    return [(col, fall), (col, near)]


def g_ring(rim, a, s, col):
    near = _cut(_layers(rim, s, [(1.0, 1.4), (2.5, 1.1)]))
    k1, k0 = int(2 * 9 * s) | 1, int(2 * 7 * s) | 1
    ring = ImageChops.subtract(rim.filter(ImageFilter.MaxFilter(k1)), rim.filter(ImageFilter.MaxFilter(k0)))
    ring = _cut(_gain(ring.filter(ImageFilter.GaussianBlur(1.3 * s)), 0.5), 6)
    # 링은 바깥에만 뜬다. 몸통 안까지 두르면 어두운 몸통 너머로 과녁처럼 비쳤다
    inside = a.filter(ImageFilter.MaxFilter(int(2 * s) | 1))
    ring = ImageChops.multiply(ring, ImageChops.invert(inside))
    return [(_g().mix(col, '#FFFFFF', 0.15), ring), (col, near)]


def g_shift(rim, a, s, col):
    outer = _cut(_gain(_layers(rim, s, [(7.0, 2.8)]), 0.95), 6)
    inner = _cut(_layers(rim, s, [(1.0, 1.4), (2.5, 1.2)]))
    return [(_hue(col, 0.17), outer), (col, inner)]


# 이름 -> 모양. margin 은 (왼, 위, 오른, 아래) pt. 'char' 는 char_glow 가 여백을 정한다
PRESETS = {
    'char':  dict(label='캐릭터 기본', margin=None, fn=None,
                  note='두 겹 흐림. 0.29 부터 나간 캐릭터 계열(오락실·캠핑)이 쓴다. 고치지 않는다'),
    'soft':  dict(label='부드러운 기본', margin=(8, 8, 8, 8), fn=g_soft,
                  note='은은하게 번진다. 무난한 기준'),
    'bloom': dict(label='강한 블룸', margin=(13, 13, 13, 13), fn=g_bloom,
                  note='관 가까이가 하얗게 타고 멀리 퍼진다. 네온으로 읽힌다'),
    'led':   dict(label='또렷한 LED', margin=(4, 4, 4, 4), fn=g_led,
                  note='빛이 짧고 경계가 또렷하다. 간격이 가장 좁다'),
    'wall':  dict(label='벽에 번지는 빛', margin=(18, 18, 18, 18), fn=g_wall,
                  note='뒤 벽에 넓고 옅게 번진다. 간격이 가장 넓다'),
    'drop':  dict(label='아래로 떨어지는 빛', margin=(6, 6, 6, 18), fn=g_drop,
                  note='빛이 아래 벽으로 흘러내린다. 벽에 매단 간판'),
    'ring':  dict(label='두 겹 링', margin=(13, 13, 13, 13), fn=g_ring,
                  note='관 바깥에 간격을 두고 옅은 테가 한 겹 더 뜬다. 폰 크기에서는 옅다'),
    'shift': dict(label='색이 변하는 빛', margin=(12, 12, 12, 12), fn=g_shift,
                  note='가까이는 제 색, 멀어질수록 옆 색으로 번진다'),
}

# 재질 -> 기본 글로우. 테마에 glow_style 을 적으면 그게 이긴다
MATERIAL = {
    'tube': 'bloom',     # 네온관
    'sign': 'drop',      # 벽에 매단 간판
    'pixel': 'led',      # 픽셀. 경계가 또렷해야 픽셀로 읽힌다
    'party': 'shift',    # 파티·사탕처럼 들뜬 것
    'light': 'soft',     # 그 밖에 스스로 빛나는 것
}

# 글로우를 넣으면 멈추는 재질과 그 까닭
NO_GLOW = {
    'paper': '종이에 빛을 두르면 빛이 아니라 번진 테두리로 보인다',
    'glass': '반투명 말풍선은 테두리로 이미 떠 보이고, 빛이 번질 자리가 없어 뿌연 테두리가 된다',
}


def pick(t):
    """이 테마의 글로우 모양 이름. 글로우가 없으면 None."""
    name = t.get('glow_style')
    mat = t.get('material')
    if mat in NO_GLOW and (name or t.get('char_glow')):
        raise ValueError('%s: 재질이 %s 인데 글로우가 있다 — %s'
                         % (t.get('key', '?'), mat, NO_GLOW[mat]))
    if name:
        if name not in PRESETS:
            raise ValueError('%s: 없는 글로우 모양 %s. 있는 것: %s'
                             % (t.get('key', '?'), name, ', '.join(PRESETS)))
        if name == 'char' and not t.get('char_glow'):
            return None
        return name
    if MATERIAL.get(mat):
        return MATERIAL[mat]
    if t.get('char_glow'):
        return 'char'
    return None


def margin(t):
    """글로우가 번질 여백 (왼, 위, 오른, 아래) pt."""
    name = pick(t)
    if name is None:
        return (0, 0, 0, 0)
    if name == 'char':
        G = t.get('char_glow') or 0
        return (G, G, G, G)
    m = PRESETS[name]['margin']
    if max(m) > MAX_MARGIN:
        raise ValueError('%s: 글로우 여백 %dpt 가 한도 %dpt 를 넘는다 — 말풍선 사이가 너무 벌어진다'
                         % (t.get('key', '?'), max(m), MAX_MARGIN))
    return m


def grow(t):
    """글로우가 소품 둘레로 번지는 폭 pt. 이 안에서도 늘어나는 줄이 지나면 안 된다."""
    name = pick(t)
    if name is None:
        return 0
    if name == 'char':
        return math.ceil((t.get('char_glow') or 0) * 0.6)
    return math.ceil(max(PRESETS[name]['margin']) * 0.4)


def _edge_fade(size, geo, s):
    """장 가장자리로 갈수록 0 이 되는 가림막. 세기가 여백 칸 안에서만 바뀌어 늘어나는 줄을 안 건드린다."""
    W, H = size

    def ramp(n, a, b):
        a, b = max(1.0, a * s * 0.85), max(1.0, b * s * 0.85)
        out = []
        for i in range(n):
            f = min(1.0, i / a, (n - 1 - i) / b)
            out.append(int(255 * f * f * (3 - 2 * f)))
        return out

    fx = Image.new('L', (W, 1))
    fx.putdata(ramp(W, geo['ml'], geo['mr']))
    fy = Image.new('L', (1, H))
    fy.putdata(ramp(H, geo['mt'], geo['mb']))
    return ImageChops.multiply(fx.resize((W, H)), fy.resize((W, H)))


def _char(t, img, size, scale, ck, fl):
    """0.29 부터 나간 캐릭터 계열의 글로우. 옮기기만 했다 — 바꾸면 이미 깐 테마의 그림이 달라진다."""
    g = _g()
    G = t.get('char_glow') or 0
    a = img.getchannel('A')
    halo = Image.new('L', size, 0)
    for rr, k in ((0.3, 0.8), (0.75, 0.55)):
        b = a.filter(ImageFilter.GaussianBlur(G * rr * scale))
        halo = ImageChops.add(halo, b.point(lambda v, k=k: int(v * k)))
    # 옅은 꼬리를 잘라낸다. 장 끝까지 알파가 남으면 말풍선 둘레에 네모가 뜬다
    gk = t.get('char_glow_k', 1.35)
    halo = halo.point(lambda v: 0 if v < 16 else min(255, int((v - 16) * gk)))
    if fl is not None:
        # 불 쪽 귀퉁이 둘레만 빛이 짙다. 아래변 전체를 짙게 두면 형광펜 밑줄로 보였다
        halo = ImageChops.add(halo, ImageChops.multiply(halo, fl))
    # 빛 색은 기본이 말풍선 색이다. 갈색 팻말처럼 몸통이 탁한 색이면 탁한 빛이 번져
    # 빛이 아니라 얼룩으로 보이므로, 빛의 출처가 따로 있는 계열은 그 색을 준다(모닥불)
    col = _rgb(t.get('char_glow_color') or g.mix(_c(t[ck]), '#FFFFFF', 0.25))
    glow = Image.new('RGBA', size, col + (255,))
    glow.putalpha(halo)
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(img)
    return out


def render(t, img, geo, scale, ck, fl=None):
    """말풍선 그림 아래에 글로우를 깐다. 받은 쪽 장 좌표로 받고, 뒤집기는 부르는 쪽이 한다."""
    name = pick(t)
    if name is None:
        return img
    size = img.size
    if name == 'char':
        return _char(t, img, size, scale, ck, fl)
    a = img.getchannel('A')
    k = int(RIM * scale) * 2 + 1
    rim = ImageChops.subtract(a, a.filter(ImageFilter.MinFilter(k)))
    col = t.get('char_glow_color') or _c(t[ck])
    fade = _edge_fade(size, geo, scale)
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    for c, al in PRESETS[name]['fn'](rim, a, scale, col):
        lay = Image.new('RGBA', size, _rgb(c) + (255,))
        lay.putalpha(ImageChops.multiply(al, fade))
        out.alpha_composite(lay)
    out.alpha_composite(img)
    return out
