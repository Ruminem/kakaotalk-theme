# -*- coding: utf-8 -*-
"""캐릭터 테마의 말풍선과 프로필 — 편지봉투·포스트잇·픽셀·젤리.

카톡은 한쪽 말풍선을 두 장 받는다.
  01  한 사람이 연달아 보낸 말 중 첫 말풍선 — 우표·테이프·꼬리·방울 같은 소품이 붙는다
  02  이어지는 말풍선 — 모양만 남는다
말풍선마다 소품이 붙으면 화면이 소품으로 뒤덮이고 대화가 묶음으로 안 읽힌다.

말풍선 그림은 한 줄을 기준으로 늘어난다(iOS cap inset, 안드로이드 9-patch).
그 줄에 걸린 소품은 말이 길어질 때 같이 늘어나 뭉개진다. 그래서 줄 위치를 손으로 정하지
않고 소품이 놓인 자리를 보고 geometry() 가 계산한다. 지켜야 하는 것이 넷이다.

  - cap 은 가로세로 하나다. `'file' Npx Npx` 의 두 값이 어느 축인지 규격에 없다.
  - 보낸 쪽은 받은 쪽 장을 좌우로 뒤집는다. 같은 cap 이 뒤집힌 장에서도 안전해야 하므로
    바깥쪽 소품은 cap 보다 앞에, 안쪽 소품은 (폭-1-cap) 보다 뒤에 온전히 있어야 한다.
  - 늘어나는 줄이 모서리의 둥근 곳을 지나면 모서리가 부푼다. 곧은 변 위에 있어야 한다.
  - 좌우 글자 여백은 같은 값이다. edgeinsets 의 좌우 순서도 규격에 없다.

맞지 않으면 몸통을 키운다. 키워도 안 되면 멈춘다 — 조용히 뭉갠 장을 내보내지 않는다.

치수는 pt 다. scale 을 곱해 픽셀로 바꾼다.
"""
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

IV, IH = 11, 16         # 몸통 안에서 글자까지의 여백
LINE = 22               # 글자 한 줄 높이(preview.LINE_H 와 같다). 몸통 44 = 22 + 11 * 2
MIN_TEXT = 16           # 한 글자짜리 말의 폭. 프레임이 이보다 좁아지면 그림이 눌린다
OW = 1.6                # 말풍선 윤곽 굵기
FACE = '#2B2B2B'        # 캐릭터 눈·입. 어두운 테마에서 윤곽이 밝아져도 얼굴은 어둡게 둔다


def _g():
    """gen 을 늦게 불러온다. gen 이 이 모듈을 부르므로 위에서 import 하면 순환한다."""
    import gen
    return gen


def hexc(h, a=255):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def _c(v):
    """팔레트 값에서 색 하나. 말풍선 색은 (위, 아래) 짝으로 적혀 있다."""
    return v[0] if isinstance(v, (tuple, list)) else v


class Pen:
    """pt 좌표로 받아 배율을 곱해 그린다. 윤곽은 도형보다 선 굵기만큼 크게 먼저 칠한다.

    RGBA 판에 반투명을 그리면 PIL 은 섞지 않고 덮어쓴다. 반투명은 따로 만든 판에 그려
    alpha_composite 로 얹는다.
    """

    def __init__(self, img, s, oc):
        self.img = img
        self.d = ImageDraw.Draw(img, 'RGBA')
        self.s = s
        self.oc = hexc(oc) if isinstance(oc, str) else oc

    def _b(self, *v):
        return [x * self.s for x in v]

    def ell(self, cx, cy, rx, ry, fill, ow=3.5, outline=True, oc=None):
        if outline:
            self.d.ellipse(self._b(cx - rx - ow, cy - ry - ow, cx + rx + ow, cy + ry + ow),
                           fill=oc or self.oc)
        self.d.ellipse(self._b(cx - rx, cy - ry, cx + rx, cy + ry), fill=fill)

    def rr(self, x0, y0, x1, y1, r, fill, ow=3.5, outline=True, oc=None):
        if outline:
            self.d.rounded_rectangle(self._b(x0 - ow, y0 - ow, x1 + ow, y1 + ow),
                                     radius=(r + ow) * self.s, fill=oc or self.oc)
        self.d.rounded_rectangle(self._b(x0, y0, x1, y1), radius=max(0, r) * self.s, fill=fill)

    def poly(self, pts, fill, ow=3.5, outline=True, oc=None):
        q = [(x * self.s, y * self.s) for x, y in pts]
        if outline:
            o = oc or self.oc
            self.d.polygon(q, fill=o)
            self.d.line(q + [q[0]], fill=o, width=max(1, int(ow * 2 * self.s)), joint='curve')
        self.d.polygon(q, fill=fill)

    def dot(self, cx, cy, r, fill=None):
        self.d.ellipse(self._b(cx - r, cy - r, cx + r, cy + r), fill=fill or self.oc)

    def arc(self, bbox, a0, a1, w=3, fill=None):
        self.d.arc(self._b(*bbox), a0, a1, fill=fill or self.oc, width=max(1, int(w * self.s)))

    def line(self, pts, fill, w):
        self.d.line([(x * self.s, y * self.s) for x, y in pts], fill=fill,
                    width=max(1, int(w * self.s)), joint='curve')

    def rect(self, x0, y0, x1, y1, fill):
        self.d.rectangle(self._b(x0, y0, x1, y1), fill=fill)

    def pie(self, bbox, a0, a1, fill):
        self.d.pieslice(self._b(*bbox), a0, a1, fill=fill)


# --- 말풍선 스타일 ------------------------------------------------------
# draw(p, lp, x, y, w, h, first, ck, t) — 받은 쪽 방향으로 몸통(x, y, w, h)을 그린다.
#   p 는 장, lp 는 반투명을 모았다가 마지막에 얹는 판. ck 는 'send' / 'recv'.
# features(t, bw, bh, first) — 몸통 좌표의 상자와 그 상자가 있어야 할 자리.
#   outer 바깥쪽 모서리 · inner 안쪽 모서리 · top 위 · bottom 아래. 자리가 비어 있으면
#   늘어나는 줄과 상관없고 여백만 잡는다(몸통 윤곽, 폭 전체에 고르게 퍼진 그림자).

def d_envelope(p, lp, x, y, w, h, first, ck, t):
    p.rr(x, y, x + w, y + h, 6, hexc(_c(t[ck])), ow=OW)
    if first:
        p.line([(x + 4, y + 4), (x + 14, y + 11), (x + 24, y + 4)], p.oc, 1.5)
        sx = x + w - 26                       # 우표는 위로 솟게 둔다 — 글자 칸을 안 먹는다
        p.rr(sx, y - 14, sx + 20, y + 4, 2, hexc(t.get('stamp', '#FFC2BE')), ow=1.4)
        hole = (0, 0, 0, 0)    # 구멍은 투명하게 뚫는다. RGBA 판이라 덮어쓰기가 여기선 맞다
        for k in range(5):
            p.dot(sx + 1.5 + k * 4.25, y - 14, 1.1, fill=hole)
            p.dot(sx + 1.5 + k * 4.25, y + 4, 1.1, fill=hole)
        p.ell(sx + 10, y - 5, 4, 4, hexc(t['accent']), outline=False)


def f_envelope(t, bw, bh, first):
    f = [((-OW, -OW, bw + OW, bh + OW), ())]
    if first:
        f += [((3, 3, 25, 12), ('outer', 'top')),
              ((bw - 27.4, -15.4, bw - 4.6, 5.4), ('inner', 'top'))]
    return f


def d_postit(p, lp, x, y, w, h, first, ck, t):
    fill, fold, f = hexc(_c(t[ck])), hexc(t[ck + '_fold']), 11
    p.rect(x + 2, y + 3, x + w + 2, y + h + 3, (0, 0, 0, 24))     # 그림자가 먼저, 몸통이 위
    p.poly([(x, y), (x + w, y), (x + w, y + h - f), (x + w - f, y + h), (x, y + h)], fill,
           outline=False)
    p.poly([(x + w, y + h - f), (x + w - f, y + h - f), (x + w - f, y + h)], fold, outline=False)
    if first:
        # 테이프는 좁게 둔다. 넓으면 뒤집은 장에서 늘어나는 줄에 걸린다
        lp.poly([(x + 3, y - 6), (x + 17, y - 9), (x + 20, y + 5), (x + 6, y + 8)],
                (255, 255, 255, t.get('tape_a', 150)), outline=False)


def f_postit(t, bw, bh, first):
    f = [((0, 0, bw + 2, bh + 3), ()),
         ((bw - 11, bh - 11, bw, bh), ('inner', 'bottom'))]
    if first:
        f.append(((3, -9, 20, 8), ('outer', 'top')))
    return f


def d_pixel(p, lp, x, y, w, h, first, ck, t):
    s = 4
    fill, oc = hexc(_c(t[ck])), p.oc
    pts = [(x + 2 * s, y), (x + w - 2 * s, y), (x + w - 2 * s, y + s), (x + w - s, y + s),
           (x + w - s, y + 2 * s), (x + w, y + 2 * s), (x + w, y + h - 2 * s),
           (x + w - s, y + h - 2 * s), (x + w - s, y + h - s), (x + w - 2 * s, y + h - s),
           (x + w - 2 * s, y + h), (x + 2 * s, y + h), (x + 2 * s, y + h - s), (x + s, y + h - s),
           (x + s, y + h - 2 * s), (x, y + h - 2 * s), (x, y + 2 * s), (x + s, y + 2 * s),
           (x + s, y + s), (x + 2 * s, y + s)]
    q = [(a * p.s, b * p.s) for a, b in pts]
    p.d.polygon(q, fill=fill)
    p.d.line(q + [q[0]], fill=oc, width=max(1, int(3 * p.s)))
    if first:
        # 계단 꼬리는 말풍선 색으로 채우고 테두리를 두른다. 테두리 색으로만 칠하면
        # 어두운 바탕에 묻혀 꼬리가 없는 것처럼 보인다.
        k, tx, e = 5, x + 2 * s, 1.5
        for i in range(3):
            p.rect(tx - e, y + h + i * k - (e if i == 0 else 0), tx + (3 - i) * k + e,
                   y + h + (i + 1) * k + e, oc)
        for i in range(3):
            p.rect(tx + e, y + h + i * k - e * 2, tx + (3 - i) * k - e,
                   y + h + (i + 1) * k - e, fill)


def f_pixel(t, bw, bh, first):
    f = [((-1.5, -1.5, bw + 1.5, bh + 1.5), ())]
    if first:
        f.append(((6.5, bh - 1.5, 24.5, bh + 16.5), ('outer', 'bottom')))
    return f


def d_jelly(p, lp, x, y, w, h, first, ck, t):
    """젤리. 광택은 보통/강함 두 가지(t['gloss']).

    가로로 긋는 선은 넣지 않는다 — 폭 전체를 지나는 선은 광택이 아니라 취소선이나 밑줄로
    읽혔다. 흐린 빛 덩어리도 넣지 않는다 — 광택이 아니라 얼룩으로 읽혔다.
    """
    fill, edge = hexc(_c(t[ck])), hexc(t[ck + '_edge'])
    strong = t.get('gloss') == 'strong'
    dx = x + w - 20
    if first:
        p.ell(dx, y + h + 2, 6, 7.5, fill, ow=OW, oc=edge)
    p.rr(x, y, x + w, y + h, 19, fill, ow=OW, oc=edge)
    if first:
        p.rect(dx - 4, y + h - 2.5, dx + 4, y + h + 1, fill)      # 몸통과 방울 사이 선을 지운다
        p.ell(dx + 1, y + h + 15, 3, 3.8, fill, ow=1.4, oc=edge)
    white = lambda a: (255, 255, 255, a)
    if strong:
        lp.d.rounded_rectangle(lp._b(x + 2.5, y + h - 18, x + w - 2.5, y + h - 1.8),
                               radius=14 * lp.s, fill=(0, 0, 0, t.get('shade_a', 26)))
        W_, H_ = lp.img.size
        # 윗 광택: 가장자리보다 조금 안쪽이 가장 밝고 위아래로 옅어진다. 맨 윗줄을 가장
        # 밝게 두면 밝기가 몇 줄에 몰려 흰 선으로 읽혔다. 옅어지는 가림막 한 장으로 만든다.
        m = Image.new('L', (W_, H_), 0)
        ImageDraw.Draw(m).rounded_rectangle(lp._b(x + 7, y + 3, x + w - 7, y + 14.5),
                                            radius=8 * lp.s, fill=255)
        ramp = Image.new('L', (1, H_), 0)
        rp = ramp.load()
        y0p, y1p = (y + 3) * lp.s, (y + 14.5) * lp.s
        for yy in range(H_):
            if y0p <= yy <= y1p:
                tt = (yy - y0p) / (y1p - y0p)
                v = tt / 0.3 if tt < 0.3 else (1 - (tt - 0.3) / 0.7) ** 1.4
                rp[0, yy] = int(150 * v)
        m = ImageChops.multiply(m, ramp.resize((W_, H_)))
        m = m.filter(ImageFilter.GaussianBlur(1.2 * lp.s))
        band = Image.new('RGBA', (W_, H_), white(255))
        band.putalpha(m)
        lp.img.alpha_composite(band)
        lp.ell(x + 18, y + 8, 10.5, 3.8, white(240), outline=False)
        lp.dot(x + 26, y + 6.2, 1.8, fill=white(235))
        lp.ell(x + w - 22, y + h - 6.5, 4.5, 1.7, white(150), outline=False)
        if first:
            lp.dot(dx - 1.5, y + h + 3, 1.6, fill=white(220))
            lp.dot(dx + 0.3, y + h + 13.5, 0.9, fill=white(220))
    else:
        lp.d.rounded_rectangle(lp._b(x + 3, y + 2.5, x + w - 3, y + 19), radius=8 * lp.s,
                               fill=white(55))
        lp.ell(x + 16, y + 9.5, 7.5, 3.6, white(210), outline=False)


def f_jelly(t, bw, bh, first):
    f = [((-OW, -OW, bw + OW, bh + OW), ())]
    if t.get('gloss') == 'strong':
        f += [((5, 1, bw - 5, 18.5), ('top',)),
              ((7.5, 4.2, 28.5, 11.8), ('outer', 'top')),
              ((24.2, 4.4, 27.8, 8), ('outer', 'top')),
              ((bw - 26.5, bh - 8.2, bw - 17.5, bh - 4.8), ('inner', 'bottom')),
              ((2.5, bh - 18, bw - 2.5, bh - 1.8), ('bottom',))]
    else:
        f += [((3, 2.5, bw - 3, 19), ('top',)),
              ((8.5, 5.9, 23.5, 13.1), ('outer', 'top'))]
    if first:
        f.append(((bw - 27.6, bh - 5.5, bw - 12.4, bh + 20.2), ('inner', 'bottom')))
    return f


STYLES = {
    'envelope': dict(bw=40, bh=44, radius=6, draw=d_envelope, features=f_envelope),
    'postit':   dict(bw=40, bh=44, radius=1, draw=d_postit, features=f_postit),
    'pixel':    dict(bw=40, bh=44, radius=9.5, draw=d_pixel, features=f_pixel),
    'jelly':    dict(bw=40, bh=44, radius=19, draw=d_jelly, features=f_jelly),
}


def geometry(t, variant):
    """장 크기·몸통·여백·늘어나는 줄·글자 여백(pt). 받은 쪽 기준이다.

    몸통은 작게 시작해 조건이 맞을 때까지 2pt 씩 키운다. 가로는 cap 줄과 뒤집은 장의 줄
    (폭-1-cap) 사이에 소품도 둥근 모서리도 없게 잡으므로, cap 이 '왼쪽에서 한 줄' 이든
    '양옆 여백' 이든 늘어나는 곳에 걸리는 것이 없다. 세로는 '위에서 한 줄' 로만 맞춘다.
    """
    name = t['char_style']
    st = STYLES[name]
    first = variant == '01'
    G = t.get('char_glow') or 0
    grow = math.ceil(G * 0.6)       # 글로우가 소품 둘레로 번지는 폭. 이 안도 늘어나면 안 된다
    bw, bh, r = st['bw'], st['bh'], st['radius']
    for _ in range(80):
        feats = st['features'](t, bw, bh, first)
        ml = math.ceil(max([2.0] + [-b[0] for b, z in feats])) + G
        mr = math.ceil(max([2.0] + [b[2] - bw for b, z in feats])) + G
        mt = math.ceil(max([2.0] + [-b[1] for b, z in feats])) + G
        mb = math.ceil(max([2.0] + [b[3] - bh for b, z in feats])) + G
        W, H = ml + bw + mr, mt + bh + mb

        lo = [ml + r + 1, mr + r + 1, mt + r + 1]
        bottoms = []
        for b, z in feats:
            if not z:
                continue
            x0, y0, x1, y1 = b[0] - grow, b[1] - grow, b[2] + grow, b[3] + grow
            if 'outer' in z:
                lo.append(ml + x1 + 1)
            if 'inner' in z:
                lo.append(W - (ml + x0))        # 뒤집은 장의 줄(폭-1-cap) 보다 뒤
            if 'top' in z:
                lo.append(mt + y1 + 1)
            if 'bottom' in z:
                bottoms.append(mt + y0)
        cap = math.ceil(max(lo))

        ok_w = W - 1 - cap >= cap and cap <= ml + bw - r - 1
        ok_h = cap <= mt + bh - r - 1 and all(cap < y for y in bottoms)
        if ok_w and ok_h:
            break
        if not ok_w:
            bw += 2
        if not ok_h:
            bh += 2
    else:
        raise ValueError('%s %s: 늘어나는 줄을 소품과 모서리 밖에 둘 수 없다' % (name, variant))

    # 세로: 한 줄짜리 프레임 높이가 장 높이와 같게 한다. 몸통이 44 보다 커졌으면 남는 만큼을
    # 위아래로 나눈다. 프레임이 장보다 낮으면 그림이 통째로 눌린다.
    extra = bh - (LINE + IV * 2)
    top = mt + IV + extra // 2
    bottom = mb + IV + extra - extra // 2
    # 가로: 좌우가 같은 값이어야 해서 넓은 쪽 여백에 맞춘다. 한 글자짜리 말에서도 프레임이
    # 장보다 좁아지지 않게 한다 — 좁아지면 우표와 꼬리가 찌그러진다.
    side = max(max(ml, mr) + IH, math.ceil((W - MIN_TEXT) / 2.0))
    return dict(cap=cap, w=W, h=H, bw=bw, bh=bh, ml=ml, mr=mr, mt=mt, mb=mb,
                ins=(top, side, bottom, side),
                outer=ml, inner=mr, top=mt, bottom=mb)


def sheet(t, side, variant, scale):
    """말풍선 한 장과 그 치수. 보낸 쪽은 받은 쪽 장을 뒤집는다.

    글로우는 장을 흐림 반경보다 넉넉히 키운 뒤에 깐다(여백 G 가 geometry 에 들어 있다).
    딱 맞는 장에서 흐리면 빛이 가장자리에서 잘려 네모가 남는다.
    """
    g = _g()
    geo = geometry(t, variant)
    st = STYLES[t['char_style']]
    size = (int(round(geo['w'] * scale)), int(round(geo['h'] * scale)))
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    lay = Image.new('RGBA', size, (0, 0, 0, 0))
    ck = 'send' if side == 'send' else 'recv'
    oc = t['char_outline']
    st['draw'](Pen(img, scale, oc), Pen(lay, scale, oc), geo['ml'], geo['mt'],
               geo['bw'], geo['bh'], variant == '01', ck, t)
    img.alpha_composite(lay)

    G = t.get('char_glow') or 0
    if G:
        a = img.getchannel('A')
        halo = Image.new('L', size, 0)
        for rr, k in ((0.3, 0.8), (0.75, 0.55)):
            b = a.filter(ImageFilter.GaussianBlur(G * rr * scale))
            halo = ImageChops.add(halo, b.point(lambda v, k=k: int(v * k)))
        # 옅은 꼬리를 잘라낸다. 장 끝까지 알파가 남으면 말풍선 둘레에 네모가 뜬다
        gk = t.get('char_glow_k', 1.35)
        halo = halo.point(lambda v: 0 if v < 16 else min(255, int((v - 16) * gk)))
        col = hexc(g.mix(_c(t[ck]), '#FFFFFF', 0.25))[:3]
        glow = Image.new('RGBA', size, col + (255,))
        glow.putalpha(halo)
        out = Image.new('RGBA', size, (0, 0, 0, 0))
        out.alpha_composite(glow)
        out.alpha_composite(img)
        img = out

    if side == 'send':
        img = ImageOps.mirror(img)
    return img, geo


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


# --- 캐릭터 (프로필용, 100 칸 네모를 꽉 채운다) ----------------------------
# 프로필은 36~50pt 라 크게 그린 원본을 줄이면 잔선이 뭉개진다. 잔디테일은 빼고 눈과 선을
# 키운 작은 판만 테마에 넣는다.

def c_kongkong(p):
    """콩콩 — 떡잎 달린 노란 콩나물 머리."""
    face = hexc(FACE)
    q = [(46, 80), (44, 90), (41, 100)]
    p.line(q, p.oc, 11)
    p.line(q, hexc('#F3EBC8'), 6)
    p.poly([(52, 22), (62, 5), (82, 8), (67, 25)], hexc('#7BC96F'), ow=4)
    p.ell(50, 52, 37, 31, hexc('#FFD95A'), ow=4.5)
    p.dot(37, 51, 5, fill=face)
    p.dot(61, 51, 5, fill=face)
    p.ell(24, 64, 7.5, 4.5, hexc('#FFA8A8'), outline=False)
    p.ell(75, 64, 7.5, 4.5, hexc('#FFA8A8'), outline=False)
    p.arc((44, 53, 54, 64), 20, 160, w=3.5, fill=face)


def c_sock(p):
    """짝짝이 — 한 짝만 남은 양말.

    처음엔 얼굴을 발끝에 작게 두고 목에 줄무늬를 둘 넣었는데, 36pt 로 줄이자 줄무늬 네모가
    먼저 읽혀 우유갑처럼 보였다. 양말은 목·뒤꿈치·발끝 색으로 읽힌다 — 목과 발끝만 칠하고
    얼굴은 발등 한가운데에 크게 둔다.
    """
    face = hexc(FACE)
    blue = hexc('#6FA8DC')
    parts = ((28, 4, 62, 66, 8), (28, 44, 94, 90, 23))
    for x0, y0, x1, y1, r in parts:
        p.d.rounded_rectangle(p._b(x0 - 4.5, y0 - 4.5, x1 + 4.5, y1 + 4.5),
                              radius=(r + 4.5) * p.s, fill=p.oc)
    for x0, y0, x1, y1, r in parts:
        p.d.rounded_rectangle(p._b(x0, y0, x1, y1), radius=r * p.s, fill=hexc('#FFFFFF'))
    p.d.rounded_rectangle(p._b(28, 4, 62, 20), radius=8 * p.s, fill=blue)
    p.rect(28, 12, 62, 20, blue)
    p.pie((48, 44, 94, 90), -90, 90, blue)                 # 발끝은 발의 오른쪽 반원
    p.ell(40, 72, 5.5, 3.5, hexc('#FFA8A8'), outline=False)
    p.ell(66, 72, 5.5, 3.5, hexc('#FFA8A8'), outline=False)
    p.dot(45, 62, 5.5, fill=face)
    p.dot(61, 62, 5.5, fill=face)
    p.arc((48, 64, 58, 75), 20, 160, w=3.5, fill=face)


def c_bulb(p):
    """꼬마전구 — 눈웃음 치는 전구."""
    face = hexc(FACE)
    for (x0, y0), (x1, y1) in (((50, 2), (50, 11)), ((16, 14), (23, 21)), ((84, 14), (77, 21))):
        p.line([(x0, y0), (x1, y1)], hexc('#FFC93C'), 5.5)
    p.rr(36, 70, 64, 92, 5, hexc('#B8C0CC'), ow=4.5)
    p.ell(50, 45, 33, 33, hexc('#FFF4B8'), ow=4.5)
    p.arc((30, 35, 46, 49), 200, 340, w=4.5, fill=face)
    p.arc((54, 35, 70, 49), 200, 340, w=4.5, fill=face)
    p.arc((41, 46, 59, 62), 20, 160, w=4.5, fill=face)
    p.ell(26, 55, 6.5, 4, hexc('#FFB38A'), outline=False)
    p.ell(74, 55, 6.5, 4, hexc('#FFB38A'), outline=False)


def c_mailbox(p):
    """빨강 — 편지를 문 동네 우체통. 작아져도 편지 귀퉁이는 남긴다 — 빼면 빨간 유령이 된다."""
    face = hexc(FACE)
    red = hexc('#FF5A4E')
    p.pie((12.5, 4.5, 87.5, 79.5), 180, 360, p.oc)
    p.d.rounded_rectangle(p._b(12.5, 38, 87.5, 97.5), radius=12 * p.s, fill=p.oc)
    p.pie((17, 9, 83, 75), 180, 360, red)
    p.d.rounded_rectangle(p._b(17, 38, 83, 93), radius=8 * p.s, fill=red)
    p.rr(29, 62, 71, 73, 5, hexc('#3A2A24'), outline=False)
    p.poly([(38, 67), (40, 57), (62, 58), (60, 67)], hexc('#FFFFFF'), ow=2.5, oc=face)
    for ex in (37, 63):
        p.dot(ex, 46, 7, fill=hexc('#FFFFFF'))
        p.dot(ex + 1, 47, 3.8, fill=hexc('#3A2A24'))


CHARS = {'kongkong': c_kongkong, 'sock': c_sock, 'bulb': c_bulb, 'mailbox': c_mailbox}


def profile(t, idx, px):
    """기본 프로필. 캐릭터를 바탕 세 가지 색 위에 그린다 — 세 장이 섞여 배정된다."""
    k = 3
    im = Image.new('RGB', (px * k, px * k), hexc(t['char_backs'][idx % 3])[:3])
    CHARS[t['char']](Pen(im, px * k / 100.0, t['char_outline']))
    return im.resize((px, px), Image.LANCZOS).convert('RGBA')


def check_all(themes):
    """캐릭터 테마의 말풍선 치수를 전부 한 번 계산해 본다. 안 맞으면 geometry 가 멈춘다."""
    for t in themes:
        if t.get('char_style'):
            for v in ('01', '02'):
                geometry(t, v)
