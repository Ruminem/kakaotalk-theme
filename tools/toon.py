# -*- coding: utf-8 -*-
"""그림 말풍선.

테두리 선이 있고, 모양이 있고(구름·어항·상자), 첫 말풍선에 그림과 꼬리가 붙는다.

카톡은 한쪽 말풍선을 두 장 받는다.
  01  한 사람이 연달아 보낸 말 중 첫 말풍선
  02  그 뒤로 이어지는 말풍선
그림과 꼬리는 01 에만 붙이고 02 는 모양만 남긴다. 묶음의 머리에만 표시가 붙어야
대화가 묶음으로 읽힌다 — 말풍선마다 그림이 붙으면 화면이 그림으로 뒤덮인다.

말풍선 그림은 한 줄을 기준으로 늘어난다. iOS 는 cap inset, 안드로이드는 9-patch 표시가
그 줄을 정한다. 그림·꼬리·봉우리는 그 줄을 피해 늘어나지 않는 모서리 안에만 둔다.
줄에 걸리면 말이 길어질 때 같이 늘어나 뭉개진다.

cap 값은 가로세로 하나로 쓴다. 보낸 쪽은 받은 쪽 그림을 좌우로 뒤집어 만드는데,
뒤집어도 늘어나는 열이 몸통 한가운데를 지나도록 캔버스 폭을 cap 의 두 배보다 넓게 잡는다.

좌우 글자 여백은 같은 값으로 둔다. -ios-title-edgeinsets 가 위·왼·아래·오른 순서인지
위·오른·아래·왼 순서인지 규격에 안 적혀 있다. 좌우가 같으면 어느 쪽이든 결과가 같다.

캐릭터는 새로 그린 것만 쓴다. 남의 테마에 있는 캐릭터를 흉내내지 않는다.

치수는 전부 pt 다. scale 을 곱해 픽셀로 바꾼다.
"""
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SS = 4
BODY_W, BODY_H = 60, 40        # 몸통 기본 크기. 글자가 길면 카톡이 늘린다

# 몸통 위로 솟는 높이, 옆으로 삐져나오는 폭
SHAPE_TOP = {'pill': 0, 'cloud': 9, 'bowl': 3, 'box': 6}
SHAPE_SIDE = {'pill': 0, 'cloud': 0, 'bowl': 2, 'box': 4}
DECO_TOP = {None: 0, 'rainbow': 14, 'critter': 13, 'star': 10}

# 늘어나지 않는 모서리 안에 들어가야 하는 크기. 바깥쪽 폭 / 안쪽 폭 / 아래 높이
OUTER_W = {'cloud': 30, 'box': 16, 'rainbow': 31, 'critter': 27, 'star': 21, 'tail': 18}
INNER_W = {'bowl': 24, 'box': 16}
BOTTOM_H = {'bowl': 16}

TAIL_BOTTOM, TAIL_SIDE = 6, 4

# 모양 때문에 글자에서 더 띄워야 하는 위·아래 여백. 어항은 입구 테두리 아래로 내리고
# 물고기 위로 올린다 — 물고기가 글자 칸 안에 있으면 말 끝에 걸려 보인다.
# 좌우는 늘리지 않는다. 좌우 여백은 대칭이어야 해서 한쪽만 늘릴 수 없다.
EXTRA_V = {'bowl': (3, 8)}


def _g():
    """gen 을 늦게 불러온다. gen 이 이 모듈을 부르므로 위에서 import 하면 순환한다."""
    import gen
    return gen


def _pick(v, side):
    """(보낸 쪽, 받은 쪽) 짝이면 그 쪽 값을 고른다. 짝이 아니면 양쪽이 같은 값이다."""
    if isinstance(v, (tuple, list)) and len(v) == 2:
        return v[0] if side == 'send' else v[1]
    return v


def geometry(t, side, variant):
    """캔버스·몸통·늘어나는 줄·글자 여백(pt). 받은 쪽 기준이고 보낸 쪽은 좌우만 뒤집는다."""
    shape = _pick(t.get('shape', 'pill'), side)
    tail_any = bool(_pick(t.get('tail', False), side))
    tail = tail_any and variant == '01'
    deco = _pick(t.get('deco'), side) if variant == '01' else None
    ow = t.get('outline_w', 1.5)
    edge = math.ceil(ow) + 1

    top = max(SHAPE_TOP[shape], DECO_TOP[deco]) + edge
    bottom = (TAIL_BOTTOM if tail else 0) + edge
    # 꼬리가 있는 쪽은 02 에도 같은 바깥 여백을 둔다. 01 과 02 의 몸통 가장자리가
    # 같은 선에 서야 한 묶음으로 보인다.
    outer = max(TAIL_SIDE if tail_any else 0, SHAPE_SIDE[shape]) + edge
    inner = SHAPE_SIDE[shape] + edge
    radius = 5 if shape == 'box' else 16

    feat_outer = max(OUTER_W.get(shape, 0), OUTER_W.get(deco, 0),
                     OUTER_W['tail'] if tail else 0, radius)
    feat_inner = max(INNER_W.get(shape, 0), radius)
    feat_bottom = max(BOTTOM_H.get(shape, 0), radius)

    cap = max(top + radius + 2, outer + feat_outer + 2, inner + feat_inner + 2)
    w = max(outer + BODY_W + inner, 2 * cap + 4)
    h = max(top + BODY_H + bottom, cap + 3 + bottom + feat_bottom)

    iv, ih = _g().insets_of(t)
    hpad = max(outer, inner) + ih
    ex_top, ex_bottom = EXTRA_V.get(shape, (0, 0))
    return dict(shape=shape, deco=deco, tail=tail, ow=ow, top=top, bottom=bottom,
                outer=outer, inner=inner, radius=radius, cap=cap, w=w, h=h,
                ins=(top + iv + ex_top, hpad, bottom + iv + ex_bottom, hpad))


# --- 소품 ---------------------------------------------------------------

def star_points(cx, cy, r, rot=-90.0, inner=0.45):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 36)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def draw_star(d, cx, cy, r, oc, ow, fill):
    rgb = _g().rgb
    pts = star_points(cx, cy, r)
    d.polygon(pts, fill=rgb(oc) + (255,))
    d.line(pts + [pts[0]], fill=rgb(oc) + (255,), width=max(1, int(round(ow * 2))),
           joint='curve')
    d.polygon(pts, fill=rgb(fill) + (255,))


def draw_critter(d, cx, cy, u, oc, ow, body='#FFFFFF', blush='#FFB3C1'):
    """몽실이. 동그란 얼굴에 짧은 귀 둘. u 는 한 칸 크기(얼굴 반지름이 10u)."""
    rgb = _g().rgb
    ocl, bc, bl = rgb(oc) + (255,), rgb(body) + (255,), rgb(blush) + (255,)
    for ex in (-8, 8):                       # 귀를 먼저 — 얼굴이 아랫부분을 덮는다
        ecx, ecy, er = cx + ex * u, cy - 8 * u, 3.5 * u
        d.ellipse([ecx - er - ow, ecy - er - ow, ecx + er + ow, ecy + er + ow], fill=ocl)
        d.ellipse([ecx - er, ecy - er, ecx + er, ecy + er], fill=bc)
    r = 10 * u
    d.ellipse([cx - r - ow, cy - r - ow, cx + r + ow, cy + r + ow], fill=ocl)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bc)
    for ex in (-3.5, 3.5):
        er = 1.3 * u
        d.ellipse([cx + ex * u - er, cy - 1.5 * u - er, cx + ex * u + er, cy - 1.5 * u + er],
                  fill=ocl)
    for ex in (-6.5, 6.5):
        d.ellipse([cx + (ex - 2.2) * u, cy + 0.7 * u, cx + (ex + 2.2) * u, cy + 3.3 * u],
                  fill=bl)
    d.arc([cx - 1.8 * u, cy + 0.2 * u, cx + 1.8 * u, cy + 3.2 * u], 20, 160, fill=ocl,
          width=max(1, int(ow * 0.8)))


def draw_rainbow(d, cx, cy, u, oc, ow):
    """반원 세 겹. 아래쪽 평평한 면은 몸통 속에 묻힌다."""
    rgb = _g().rgb
    ocl = rgb(oc) + (255,)
    for r, col in ((13, '#FFB3C7'), (9.5, '#FFE08A'), (6, '#A8D8FF')):
        rr = r * u
        d.pieslice([cx - rr - ow, cy - rr - ow, cx + rr + ow, cy + rr + ow], 180, 360, fill=ocl)
        d.pieslice([cx - rr, cy - rr, cx + rr, cy + rr], 180, 360, fill=rgb(col) + (255,))


# --- 말풍선 -------------------------------------------------------------

def bubble(t, side, variant, scale):
    """말풍선 한 장과 그 치수. side 는 'send' / 'recv', variant 는 '01' / '02'."""
    g = _g()
    geo = geometry(t, side, variant)
    key = 'send' if side == 'send' else 'recv'
    colors = t[key] if variant == '01' else t[key + '_alt']
    k = scale * SS
    W, H = geo['w'] * k, geo['h'] * k
    x0, y0 = geo['outer'] * k, geo['top'] * k
    x1, y1 = (geo['w'] - geo['inner']) * k, (geo['h'] - geo['bottom']) * k
    R, ow = geo['radius'] * k, geo['ow'] * k
    ochex = t.get('outline', '#3A3A3A')
    oc = g.rgb(ochex)

    # 선 판과 속 판을 따로 그린다. 선 판은 도형마다 선 굵기만큼 크게 그리므로,
    # 몸통·봉우리·꼬리가 겹친 자리는 속 판이 덮어 한 덩어리의 윤곽만 남는다.
    om = Image.new('L', (W, H), 0)
    fm = Image.new('L', (W, H), 0)
    od, fd = ImageDraw.Draw(om), ImageDraw.Draw(fm)

    def rrect(a, b, c, e, r):
        od.rounded_rectangle([a - ow, b - ow, c + ow, e + ow], radius=r + ow, fill=255)
        fd.rounded_rectangle([a, b, c, e], radius=r, fill=255)

    def circ(cx, cy, r):
        od.ellipse([cx - r - ow, cy - r - ow, cx + r + ow, cy + r + ow], fill=255)
        fd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)

    def poly(pts):
        od.polygon(pts, fill=255)
        od.line(pts + [pts[0]], fill=255, width=max(1, int(round(ow * 2))), joint='curve')
        fd.polygon(pts, fill=255)

    shape = geo['shape']
    rrect(x0, y0, x1, y1, R)
    if shape == 'cloud':
        for cx, cy, r in ((6, 3, 6), (15, -1, 8), (24, 4, 5)):
            circ(x0 + cx * k, y0 + cy * k, r * k)
    elif shape == 'bowl':
        rrect(x0 - 2 * k, y0 - 3 * k, x1 + 2 * k, y0 + 4 * k, 3 * k)
    elif shape == 'box':
        poly([(x0, y0 + k), (x0 - 4 * k, y0 - 6 * k), (x0 + 12 * k, y0 - 6 * k),
              (x0 + 14 * k, y0 + k)])
        poly([(x1, y0 + k), (x1 + 4 * k, y0 - 6 * k), (x1 - 12 * k, y0 - 6 * k),
              (x1 - 14 * k, y0 + k)])
    if geo['tail']:
        poly([(x0 + 8 * k, y1 - 3 * k), (x0 - 4 * k, y1 + 6 * k), (x0 + 18 * k, y1 - 3 * k)])

    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))

    line = Image.new('RGBA', (W, H), oc + (255,))
    line.putalpha(om)
    img.alpha_composite(line)

    a, b = g.rgb(colors[0]), g.rgb(colors[1])
    body = Image.new('RGB', (W, H), a)
    if a != b:
        body.paste(g.vgradient(W, max(1, y1 - y0), a, b), (0, y0))
        body.paste(Image.new('RGB', (W, max(1, H - y1)), b), (0, y1))
    body = body.convert('RGBA')
    body.putalpha(fm)
    img.alpha_composite(body)

    d = ImageDraw.Draw(img)
    lw = max(1, int(round(ow)))
    if shape == 'bowl':
        wl = y0 + 12 * k                  # 물 높이. 늘어나는 줄보다 위라 늘어나도 제자리다
        wm = Image.new('L', (W, H), 0)
        ImageDraw.Draw(wm).rectangle([0, wl, W, H], fill=255)
        water = Image.new('RGBA', (W, H), g.rgb(t.get('water', '#CFEAF7')) + (255,))
        water.putalpha(ImageChops.multiply(wm, fm))
        img.alpha_composite(water)
        d = ImageDraw.Draw(img)
        d.line([(x0 + k, wl), (x1 - k, wl)], fill=oc + (255,), width=lw)
        d.line([(x0 + 6 * k, y0 + 4 * k), (x1 - 6 * k, y0 + 4 * k)], fill=oc + (255,), width=lw)
        # 물풀과 물고기 — 안쪽 아래 모서리. 늘어나지 않는 자리다
        weed = g.rgb(t.get('weed', '#5DBB8A')) + (255,)
        for dx, ph in ((-22, 0.0), (-19, 1.7)):
            pts = [(x1 + dx * k + math.sin(ph + j * 0.9) * 1.6 * k, y1 - (2 + j * 2.2) * k)
                   for j in range(6)]
            d.line(pts, fill=weed, width=max(1, int(round(ow * 1.1))), joint='curve')
        fx, fy = x1 - 13 * k, y1 - 9 * k
        fish = g.rgb(t.get('fish', '#FF9F43')) + (255,)
        tail_pts = [(fx + 5 * k, fy), (fx + 10 * k, fy - 4 * k), (fx + 10 * k, fy + 4 * k)]
        d.polygon(tail_pts, fill=oc + (255,))
        d.line(tail_pts + [tail_pts[0]], fill=oc + (255,), width=lw * 2, joint='curve')
        d.polygon(tail_pts, fill=fish)
        d.ellipse([fx - 6 * k - ow, fy - 4 * k - ow, fx + 6 * k + ow, fy + 4 * k + ow],
                  fill=oc + (255,))
        d.ellipse([fx - 6 * k, fy - 4 * k, fx + 6 * k, fy + 4 * k], fill=fish)
        er = 1.1 * k
        d.ellipse([fx - 3 * k - er, fy - er, fx - 3 * k + er, fy + er], fill=oc + (255,))
    elif shape == 'box':
        d.line([(x0 + 5 * k, y0), (x1 - 5 * k, y0)], fill=oc + (255,), width=lw)

    if geo['deco'] == 'rainbow':
        # 봉우리 앞에 그린다. 처음에는 구름 뒤에서 솟게 했는데 봉우리가 거의 다 가려서
        # 무지개인지 알아볼 수 없었다.
        draw_rainbow(d, x0 + 16 * k, y0 + 1 * k, k, ochex, ow)
    elif geo['deco'] == 'critter':
        draw_critter(d, x0 + 14 * k, y0 + k, k, ochex, ow,
                     t.get('critter', '#FFFFFF'), t.get('blush', '#FFB3C1'))
    elif geo['deco'] == 'star':
        draw_star(d, x0 + 11 * k, y0 + k, 9 * k, ochex, ow, t.get('star', '#FFE27A'))

    out = img.resize((geo['w'] * scale, geo['h'] * scale), Image.LANCZOS)
    if side == 'send':
        out = ImageOps.mirror(out)
    return out, geo


def ninepatch(img, geo, scale):
    """9-patch 표시. 위·왼쪽은 늘어나는 한 줄, 아래·오른쪽은 글자가 들어갈 범위."""
    w, h = img.size
    out = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
    out.paste(img, (1, 1))
    d = ImageDraw.Draw(out)
    black = (0, 0, 0, 255)
    c = geo['cap'] * scale
    d.line([(1 + c, 0), (c + scale, 0)], fill=black)
    d.line([(0, 1 + c), (0, c + scale)], fill=black)
    top, left, bottom, right = (v * scale for v in geo['ins'])
    d.line([(1 + left, h + 1), (w - right, h + 1)], fill=black)
    d.line([(w + 1, 1 + top), (w + 1, h - bottom)], fill=black)
    return out


def stretch(img, cap, width, height):
    """카톡이 하는 그대로 늘린다 — cap 자리의 한 줄만 늘이고 나머지는 그대로 둔다.

    미리보기가 말풍선을 필요한 크기로 새로 그리면 그림과 꼬리가 제자리에 있어
    늘어날 때 뭉개지는 것을 못 잡는다.
    """
    w, h = img.size
    width, height = max(width, w), max(height, h)
    c = cap
    col = Image.new('RGBA', (w, height), (0, 0, 0, 0))
    col.paste(img.crop((0, 0, w, c)), (0, 0))
    col.paste(img.crop((0, c, w, c + 1)).resize((w, height - h + 1), Image.NEAREST), (0, c))
    col.paste(img.crop((0, c + 1, w, h)), (0, c + height - h + 1))
    out = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    out.paste(col.crop((0, 0, c, height)), (0, 0))
    out.paste(col.crop((c, 0, c + 1, height)).resize((width - w + 1, height), Image.NEAREST),
              (c, 0))
    out.paste(col.crop((c + 1, 0, w, height)), (c + width - w + 1, 0))
    return out


def profile(t, idx, px):
    """기본 프로필. 말풍선에 붙는 소품을 크게 그린다. 세 장은 바탕과 몸 색이 다르다."""
    g = _g()
    S = px * SS
    back = (t['surface'], t['pressed'], t['bg_deep'])[idx % 3]
    img = Image.new('RGBA', (S, S), g.rgb(back) + (255,))
    d = ImageDraw.Draw(img)
    u = S / 48.0
    oc = t.get('outline', '#3A3A3A')
    ow = 1.6 * u
    if t['profile_deco'] == 'critter':
        bodies = (t.get('critter', '#FFFFFF'), t['recv'][0], t['send'][0])
        draw_critter(d, 24 * u, 28 * u, 1.55 * u, oc, ow, bodies[idx % 3],
                     t.get('blush', '#FFB3C1'))
    else:
        fills = (t.get('star', t['accent']), t['accent'], t['subtext'])
        draw_star(d, 24 * u, 25.5 * u, 16 * u, oc, ow, fills[idx % 3])
    return img.resize((px, px), Image.LANCZOS)
