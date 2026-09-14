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
import colorsys
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


JELLY_SS = 2          # 두 배로 그려 줄인다. 반사의 둥근 끝과 방울 하이라이트가 계단 없이 나온다
JELLY_R = 19          # 몸통 모서리 반경
JELLY_OW = 1.2       # 젤리 윤곽. 두꺼우면 젤리가 아니라 스티커로 읽힌다


def _hsv(h, dv=1.0, ds=1.0):
    """명도와 채도만 곱한다. 그림자와 짙은 가장자리 색."""
    r, g, b = (v / 255.0 for v in hexc(h)[:3])
    hh, s, v = colorsys.rgb_to_hsv(r, g, b)
    r, g, b = colorsys.hsv_to_rgb(hh, min(1.0, s * ds), min(1.0, v * dv))
    return tuple(int(round(c * 255)) for c in (r, g, b))


def _lift(h, f):
    """빛 받은 색. 흰색을 섞지 않고 명도를 올린다 — 흰색을 섞으면 분홍이 탁한 살색이 된다."""
    r, g, b = (v / 255.0 for v in hexc(h)[:3])
    hh, s, v = colorsys.rgb_to_hsv(r, g, b)
    r, g, b = colorsys.hsv_to_rgb(hh, s * (1 - 0.6 * f), v + (1 - v) * f)
    return tuple(int(round(c * 255)) for c in (r, g, b))


def _ramp(size, s, stops, axis='y'):
    """세로 가림막. y 만의 함수라 가로로 늘어나도 모든 열이 같다.

    axis='x' 면 가로 가림막이다. 그때는 세기가 바뀌는 곳을 양 끝 모서리 자리에 가둬야 한다 —
    가운데에서 바뀌면 늘어나는 열이 그 값 하나로 복사된다.

    stops 사이는 smoothstep 으로 잇는다. 선형으로 이으면 끝나는 줄에서 꺾인 자국이 보인다.
    """
    W, H = size
    if axis == 'x':
        return _ramp((H, W), s, stops).transpose(Image.TRANSPOSE)
    col = Image.new('L', (1, H), 0)
    px = col.load()
    ys = [(yy * s, vv) for yy, vv in stops]
    for i in range(H):
        yc = i + 0.5
        if yc <= ys[0][0]:
            v = ys[0][1]
        elif yc >= ys[-1][0]:
            v = ys[-1][1]
        else:
            for (a, va), (b, vb) in zip(ys, ys[1:]):
                if a <= yc <= b:
                    tt = (yc - a) / (b - a) if b > a else 1.0
                    tt = tt * tt * (3 - 2 * tt)
                    v = va + (vb - va) * tt
                    break
        px[0, i] = max(0, min(255, int(round(v))))
    return col.resize((W, H), Image.NEAREST)


def _paint(dst, color, alpha):
    lay = Image.new('RGBA', dst.size, tuple(color[:3]) + (255,))
    lay.putalpha(alpha)
    dst.alpha_composite(lay)


def _k(m, f):
    return m.point(lambda v: max(0, min(255, int(v * f))))


def d_jelly(p, lp, x, y, w, h, first, ck, t):
    """젤리 몸통. 방향이 없는 것만 그린다 — 그림자, 윤곽, 명암, 가장자리 두께, 아래에 고인 빛.

    빛이 드는 방향을 타는 것(위를 감싸는 빛, 휜 반사, 아래 맺힌 빛)은 lit_jelly 가 장을 뒤집은
    뒤에 그린다.
    """
    S = p.s * JELLY_SS
    size = (p.img.width * JELLY_SS, p.img.height * JELLY_SS)
    W_, H_ = size

    def B(*v):
        return [q * S for q in v]

    def blur(m, r):
        return m.filter(ImageFilter.GaussianBlur(r * S))

    fill = _c(t[ck])
    edge = t[ck + '_edge']
    drops = _drops(x, y, w, h, first, 'recv')

    def shape_mask(grow):
        m = Image.new('L', size, 0)
        d = ImageDraw.Draw(m)
        d.rounded_rectangle(B(x - grow, y - grow, x + w + grow, y + h + grow),
                            radius=(JELLY_R + grow) * S, fill=255)
        for cx, cy, rx, ry in drops:
            d.ellipse(B(cx - rx - grow, cy - ry - grow, cx + rx + grow, cy + ry + grow), fill=255)
        return m

    shape = shape_mask(0)
    outer = shape_mask(JELLY_OW)
    out = Image.new('RGBA', size, (0, 0, 0, 0))

    # 1. 그림자. 검정이 아니라 몸통 색을 짙게 한 색이다 — 빛이 젤리를 지나 바닥에 색을 남긴다
    off = int(1.6 * S)
    sh = Image.new('L', size, 0)
    sh.paste(blur(outer, 1.4).crop((0, 0, W_, H_ - off)), (0, off))
    _paint(out, _hsv(fill, 0.55, 1.2), _k(sh, 0.38))

    # 2. 윤곽. 몸통보다 조금 크게 칠하고 그 위에 몸통을 얹는다
    _paint(out, hexc(edge), outer)

    body = Image.new('RGBA', size, hexc(fill))
    deep = _hsv(fill, 0.8, 1.15)

    # 3. 몸통 명암. 아래는 짙다. 가운데는 몸통 색 그대로 둔다 — 늘어나는 줄이 지나는 곳
    _paint(body, deep, _ramp(size, S, [(y + h - 20, 0), (y + h - 3, 170), (y + h + 40, 150)]))

    # 4. 가장자리 띠. 모양에서 흐린 모양을 빼면 테두리 안쪽만 남는다. 곧은 변을 따라 고르다
    inner = _k(ImageChops.subtract(shape, blur(shape, 2.4)), 2.0)
    wide = _k(ImageChops.subtract(shape, blur(shape, 4.0)), 1.7)
    top = _ramp(size, S, [(y, 255), (y + 12, 0)])
    bot = _ramp(size, S, [(y + h - 14, 0), (y + h - 1, 255)])
    #    옆과 아래 가장자리는 짙게 — 두께가 생긴다
    _paint(body, deep, _k(ImageChops.multiply(inner, ImageOps.invert(top)), 0.52))
    #    아래 가장자리 안쪽에 모이는 빛 — 젤리 속을 지나온 빛이 반대편 테두리에 고인다
    _paint(body, _lift(fill, 0.85), _k(ImageChops.multiply(wide, bot), 1.3))
    body.putalpha(shape)
    out.alpha_composite(body)

    p.img.alpha_composite(out.resize(p.img.size, Image.LANCZOS))


def _drops(x, y, w, h, first, side):
    """첫 말풍선의 물방울 둘 (가운데x, 가운데y, 반지름x, 반지름y). 받은 쪽은 안쪽(오른쪽) 아래에 달린다.

    보낸 쪽 장은 뒤집히므로 뒤집은 뒤에 그리는 lit_jelly 는 왼쪽에서 찾는다.
    """
    if not first:
        return []
    if side == 'recv':
        return [(x + w - 20, y + h + 2.5, 6, 7.5), (x + w - 19, y + h + 15.5, 3, 3.8)]
    return [(x + 20, y + h + 2.5, 6, 7.5), (x + 19, y + h + 15.5, 3, 3.8)]


def lit_jelly(img, t, geo, scale, side, first):
    """방향이 있는 빛. 늘 왼쪽 위에서 든다.

    보낸 쪽은 받은 쪽 장을 뒤집어 만든다. 빛까지 같이 뒤집으면 보낸 말풍선만 오른쪽 위에서 빛을
    받아, 한 화면에 해가 둘인 것처럼 보였다. 그래서 뒤집은 뒤에 여기서 그린다.

    위쪽 빛은 몸통 안에 띠를 띄우지 않고 가장자리를 따라 감는다. 몸통 안에 떠 있는 납작한 띠는
    둥근 표면이 아니라 뚜껑을 덮은 것처럼 읽혔다. 둥근 몸에 비친 빛은 곡면을 따라 휜다.
    """
    S = scale * JELLY_SS
    size = (img.width * JELLY_SS, img.height * JELLY_SS)
    x = geo['mr'] if side == 'send' else geo['ml']
    y, w, h = geo['mt'], geo['bw'], geo['bh']

    def B(*v):
        return [q * S for q in v]

    def blur(m, r):
        return m.filter(ImageFilter.GaussianBlur(r * S))

    fill = _c(t[side])
    shape = Image.new('L', size, 0)
    ImageDraw.Draw(shape).rounded_rectangle(B(x, y, x + w, y + h), radius=JELLY_R * S, fill=255)
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    white = (255, 255, 255)

    # 1. 위를 감싸는 빛. 가장자리 넓은 띠를 위쪽만 남기고, 왼쪽이 밝고 오른쪽 끝으로 옅어지게 한다.
    #    가로 세기는 양 끝 모서리 안에서만 바뀌고 가운데는 고르다 — 늘어나는 열이 지나는 곳
    band = _k(ImageChops.subtract(shape, blur(shape, 5.0)), 1.9)
    wrap = ImageChops.multiply(band, _ramp(size, S, [(y, 255), (y + 5, 215), (y + 16, 0)]))
    wrap = ImageChops.multiply(wrap, _ramp(size, S, [(x + 2, 255), (x + 28, 170),
                                                      (x + w - 28, 170), (x + w - 2, 105)],
                                           axis='x'))
    _paint(out, _lift(fill, 0.92), wrap)

    # 2. 가장 밝은 반사. 왼쪽 위 모서리의 곡면을 따라 휜 빛줄기가 윗변으로 조금 이어지다 사라진다.
    #    알약이나 네모로 그리면 표면에 붙인 스티커로 읽혔다
    hs = Image.new('L', size, 0)
    hd = ImageDraw.Draw(hs)
    rr = JELLY_R - 2.4
    cx, cy = x + JELLY_R, y + JELLY_R
    hd.arc(B(cx - rr, cy - rr, cx + rr, cy + rr), 194, 272, fill=255, width=int(round(2.5 * S)))
    hd.rounded_rectangle(B(x + JELLY_R - 1, y + 2.4, x + 27, y + 4.9), radius=1.25 * S, fill=255)
    hd.ellipse(B(x + 28.6, y + 2.7, x + 30.6, y + 4.7), fill=235)       # 떨어져 맺힌 작은 점
    #    양 끝으로 가늘고 옅어져야 빛줄기다. 끝까지 같은 세기면 흰 테이프가 된다
    hs = ImageChops.multiply(hs, _ramp(size, S, [(y + 7, 255), (y + 15.5, 30)]))
    hs = ImageChops.multiply(hs, _ramp(size, S, [(x + 18, 255), (x + 27.5, 90), (x + 28.5, 235)],
                                       axis='x'))
    _paint(out, white, _k(blur(hs, 0.4), 0.97))

    # 3. 오른쪽 아래에 맺힌 빛. 왼쪽 위에서 든 빛이 젤리를 지나 반대편에 모인다.
    #    또렷하게 그리면 흰 줄표로 읽혀서 번진 덩어리로 둔다
    cs = Image.new('L', size, 0)
    ImageDraw.Draw(cs).ellipse(B(x + w - 28, y + h - 7.2, x + w - 13, y + h - 3.2), fill=165)
    _paint(out, white, blur(cs, 0.9))

    # 4. 물방울마다 왼쪽 위에 맺힌 점과 아래에 고인 빛
    ds = Image.new('L', size, 0)
    dd = ImageDraw.Draw(ds)
    for dx, dy, rx, ry in _drops(x, y, w, h, first, side):
        dd.ellipse(B(dx - rx * 0.62, dy - ry * 0.64, dx - rx * 0.05, dy - ry * 0.22), fill=240)
        dd.ellipse(B(dx - rx * 0.1, dy + ry * 0.45, dx + rx * 0.55, dy + ry * 0.72), fill=120)
    _paint(out, white, blur(ds, 0.35))

    img.alpha_composite(out.resize(img.size, Image.LANCZOS))


def f_jelly(t, bw, bh, first):
    # 방향이 있는 빛은 뒤집은 뒤에 늘 왼쪽 위(아래 맺힌 빛은 오른쪽 아래)에 그린다. 받은 쪽 좌표로는
    # 바깥쪽에도 안쪽에도 올 수 있어서 양쪽 자리를 다 잡는다
    f = [((-3, -1.5, bw + 3, bh + 4.5), ()),              # 윤곽과 그림자
         ((0, 0, bw, 17), ('top',)),                       # 위를 감싸는 빛
         ((0, bh - 20, bw, bh), ('bottom',))]              # 아래 명암·고인 빛
    for zone, a, b in (('outer', 0, 31.5), ('inner', bw - 31.5, bw)):
        f.append(((a, 0, b, 17), (zone, 'top')))           # 휜 반사·작은 점·가로 세기
    for zone, a, b in (('outer', 12, 29), ('inner', bw - 29, bw - 12)):
        f.append(((a, bh - 8.5, b, bh - 2), (zone, 'bottom')))   # 아래 맺힌 빛
    if first:
        f.append(((bw - 30, bh - 8, bw - 10, bh + 25), ('inner', 'bottom')))
    return f


STYLES = {
    'envelope': dict(bw=40, bh=44, radius=6, draw=d_envelope, features=f_envelope),
    'postit':   dict(bw=40, bh=44, radius=1, draw=d_postit, features=f_postit),
    'pixel':    dict(bw=40, bh=44, radius=9.5, draw=d_pixel, features=f_pixel),
    # 젤리는 모서리 반경에 가장자리 띠의 흐림이 번지는 폭을 더한다. 늘어나는 줄이 그 안을 지나면
    # 모서리 근처의 옅은 명암이 같이 늘어난다
    'jelly':    dict(bw=40, bh=44, radius=JELLY_R + 3, draw=d_jelly, features=f_jelly,
                     lit=lit_jelly),
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
    if st.get('lit'):
        st['lit'](img, t, geo, scale, 'send' if side == 'send' else 'recv', variant == '01')
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
