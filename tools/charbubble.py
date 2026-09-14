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
import glow  # noqa: E402

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
    gl, gt, gr, gb = glow.margin(t)     # 글로우가 번질 여백. 모양마다 다르다(tools/glow.py)
    grow = glow.grow(t)                 # 글로우가 소품 둘레로 번지는 폭. 이 안도 늘어나면 안 된다
    bw, bh, r = st['bw'], st['bh'], st['radius']
    for _ in range(80):
        feats = st['features'](t, bw, bh, first)
        if t.get('firelight'):
            feats = feats + firelight_features(bw, bh)
        ml = math.ceil(max([2.0] + [-b[0] for b, z in feats])) + gl
        mr = math.ceil(max([2.0] + [b[2] - bw for b, z in feats])) + gr
        mt = math.ceil(max([2.0] + [-b[1] for b, z in feats])) + gt
        mb = math.ceil(max([2.0] + [b[3] - bh for b, z in feats])) + gb
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


# 불빛이 닿는 거리(pt). 안쪽 아래 귀퉁이에서 아래변을 따라 FL_RX, 옆변을 따라 FL_RY 가면 사라진다.
# 둘의 합이 한 줄짜리 말풍선에서 늘어나는 줄이 지날 틈을 남기는 한계(대략 35)를 넘으면 몸통이 커진다.
# 불이 아래에 있으니 아래변 쪽으로 길게 나눴다
FL_RX, FL_RY = 22, 10
FL_FILL, FL_RIM = 0.5, 1.0


def firelight_features(bw, bh):
    """불빛이 차지하는 자리. 세기가 가로세로로 다 바뀌므로 안쪽 아래 모서리 칸 안에 가둔다."""
    return [((bw - FL_RX - 1, bh - FL_RY - 1, bw + OW, bh + OW), ('inner', 'bottom'))]


def _firelight_mask(geo, size, s):
    """안쪽 아래 귀퉁이에서 퍼져 멀어질수록 사라지는 빛. 받은 쪽 장 좌표다.

    거리에 따라 줄인다. 한때 아래변 전체에 고른 띠를 깔았는데 형광펜으로 그은 밑줄처럼
    보였다 — 실제 불빛은 가까운 곳만 밝고 멀어지면 금방 사그라든다. 흐린 원 하나를 쓴 적도 있는데
    가운데가 평평하게 차서 모서리에 묻은 얼룩이 됐다.
    """
    W, H = size
    cx, cy = (geo['ml'] + geo['bw']) * s, (geo['mt'] + geo['bh']) * s
    RX, RY = FL_RX * s, FL_RY * s
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    n = 40
    for i in range(n, 0, -1):
        f = i / n
        d.ellipse([cx - RX * f, cy - RY * f, cx + RX * f, cy + RY * f], fill=int(255 * (1 - f) ** 1.3))
    return m.filter(ImageFilter.GaussianBlur(s))


def _firelit(img, t, mask, s):
    """배경의 모닥불에 비친 말풍선.

    불은 화면 아래 가운데에 있다. 화면 가운데를 향한 안쪽 아래 귀퉁이가 불에 가장 가까워,
    거기서 윤곽선을 따라 아래변과 옆변으로 빛이 번지다 사그라든다. 몸통은 그 귀퉁이 둘레만 옅게 물든다.
    받은 쪽 장의 안쪽은 오른쪽이고 보낸 쪽은 이 장을 뒤집어 쓰므로 양쪽 모두 가운데 쪽이 밝다.
    """
    col = hexc(t['firelight'])[:3]
    k = t.get('firelight_k', 1.0)
    a = img.getchannel('A')
    m = ImageChops.multiply(mask.point(lambda v: int(v * FL_FILL * k)), a)
    rgb = ImageChops.screen(img.convert('RGB'), ImageChops.multiply(
        Image.new('RGB', img.size, col), Image.merge('RGB', [m] * 3)))
    # 윤곽선은 채움보다 빛을 멀리까지 받는다 — 모서리가 빛을 걸어 올리는 자리라서다.
    # 이미 밝은 선이라 screen 으로는 흰 선이 되므로 불빛 색 쪽으로 끌어당긴다
    edge = ImageChops.subtract(a, a.filter(ImageFilter.MinFilter(int(2 * s) * 2 + 1)))
    reach = mask.point(lambda v: int(255 * (v / 255.0) ** 0.5))
    em = ImageChops.multiply(edge, reach).point(lambda v: min(255, int(v * FL_RIM * k)))
    rim = Image.new('RGB', img.size, hexc(_g().mix(t['firelight'], '#FFFFFF', 0.3))[:3])
    out = Image.composite(rim, rgb, em).convert('RGBA')
    out.putalpha(a)
    return out


def sheet(t, side, variant, scale):
    """말풍선 한 장과 그 치수. 보낸 쪽은 받은 쪽 장을 뒤집는다.

    글로우는 장을 흐림 반경보다 넉넉히 키운 뒤에 깐다(여백이 geometry 에 들어 있다).
    모양은 tools/glow.py 의 사전에서 고른다.
    """
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
    fl = None
    if t.get('firelight'):
        fl = _firelight_mask(geo, size, scale)
        img = _firelit(img, t, fl, scale)

    img = glow.render(t, img, geo, scale, ck, fl)

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

# 펜으로 그리지 않고 한 장을 통째로 만드는 프로필. 빛이 번지는 그림처럼 Pen 의 바탕 위 선 그리기로
# 안 되는 것이 여기 온다. 이름 -> fn(t, idx, px)
PROFILES = {}


def profile(t, idx, px):
    """기본 프로필. 캐릭터를 바탕 세 가지 색 위에 그린다 — 세 장이 섞여 배정된다."""
    if t['char'] in PROFILES:
        return PROFILES[t['char']](t, idx, px)
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


# --- 두 번째 묶음: 영화표·식빵·팻말·우주선 판·잎 -----------------------------

def _star_pts(cx, cy, R, r, n=5, rot=-90):
    return [(cx + math.cos(math.radians(rot + i * 180.0 / n)) * (R if i % 2 == 0 else r),
             cy + math.sin(math.radians(rot + i * 180.0 / n)) * (R if i % 2 == 0 else r))
            for i in range(n * 2)]


def d_ticket(p, lp, x, y, w, h, first, ck, t):
    """영화표. 양옆에 반달 홈이 파여 있다.

    홈은 아래에서 잰 자리에 둔다. 늘어나는 줄이 홈 위를 지나므로 말이 길어지면 홈이
    아래쪽을 따라 내려간다. 위에서 잰 자리에 두면 cap 이 홈 아래까지 내려가야 해서
    짧은 말의 말풍선이 쓸데없이 넓어진다.
    """
    nr, ny = 5, y + h - 22
    size = p.img.size

    def mask(e_body, e_hole):
        m = Image.new('L', size, 0)
        md = ImageDraw.Draw(m)
        md.rounded_rectangle(p._b(x - e_body, y - e_body, x + w + e_body, y + h + e_body),
                             radius=(5 + e_body) * p.s, fill=255)
        for cx in (x, x + w):
            md.ellipse(p._b(cx - nr - e_hole, ny - nr - e_hole, cx + nr + e_hole, ny + nr + e_hole),
                       fill=0)
        return m

    p.img.paste(Image.new('RGBA', size, p.oc), (0, 0), mask(OW, 0))
    p.img.paste(Image.new('RGBA', size, hexc(_c(t[ck]))), (0, 0), mask(0, OW))
    if first:
        # 별 도장은 윗변에 걸쳐 붙인다 — 몸통 안에 두면 첫 글자 머리와 겹친다
        p.poly(_star_pts(x + 11, y, 5.2, 2.3), hexc(t.get('star', '#E8B93A')), ow=1.2)


def f_ticket(t, bw, bh, first):
    nr, ny = 5, bh - 22
    f = [((-OW, -OW, bw + OW, bh + OW), ()),
         ((-OW, ny - nr - OW, nr + OW, ny + nr + OW), ('outer', 'bottom')),
         ((bw - nr - OW, ny - nr - OW, bw + OW, ny + nr + OW), ('inner', 'bottom'))]
    if first:
        f.append(((4.5, -6.5, 17.5, 6.5), ('outer', 'top')))
    return f


def d_toast(p, lp, x, y, w, h, first, ck, t):
    """식빵 한 쪽. 위가 어깨처럼 둥글게 넓고 껍질 띠가 두른다. 첫 장엔 흘러내리는 딸기잼."""
    fill, crust = hexc(_c(t[ck])), hexc(t[ck + '_crust'])

    def parts(e, inset=0):
        return [(x - e, y - e, x + w + e, y + 16 + e, 8 + e),
                (x + 2 - e, y + 6, x + w - 2 + e, y + h + e, 5 + e)]

    for e, col in ((OW, p.oc), (0, crust), (-2.6, fill)):
        for a, b, c, d_, r in parts(e):
            p.d.rounded_rectangle(p._b(a, b, c, d_), radius=max(0.5, r) * p.s, fill=col)
    if first:
        _jam(p, lp, x, y, w, t)


def _jam(p, lp, x, y, w, t):
    """식빵 안쪽 위 귀퉁이에 퍼진 딸기잼. 모서리 곡선을 따라 퍼지고 앞면으로 줄기 셋이 흐른다.

    처음엔 한 줄기가 굵기 그대로 옆면 바깥을 타고 내려갔는데 전선처럼 보였고, 말이 길어지면
    그 줄이 말풍선 끝까지 늘어나 파이프가 됐다. 잼 줄기는 위가 굵고 아래로 가늘어지다 방울로
    맺힌다. 줄기는 늘어나는 세로 줄보다 위에서 끝나게 해서 말 길이와 상관없이 같은 모양이다.
    """
    jam = hexc(t.get('jam', '#E8455A'))
    ow = 1.1
    # 퍼진 덩어리. 윗변을 따라 납작하게, 귀퉁이에서는 모서리를 감싸며 조금 흘러넘친다
    blobs = [(x + w - 21.5, y + 0.6, 3.2, 2.6), (x + w - 14, y - 0.4, 6.6, 3.8),
             (x + w - 5.5, y + 0.4, 5.6, 4.0), (x + w - 1.6, y + 4.4, 3.6, 4.4)]
    # (가운데 x, 시작 y, 방울 y, 시작 굵기, 방울 반경)
    drips = [(x + w - 5.2, y + 3.5, y + 18.0, 5.2, 2.9),
             (x + w - 11.5, y + 1.5, y + 7.6, 4.2, 2.2),
             (x + w - 19.0, y + 1.0, y + 4.6, 3.0, 1.7)]

    def drip(cx, y0, yb, top_w, br, e, col):
        pts_l, pts_r = [], []
        for q in range(9):
            f = q / 8
            yy = y0 + (yb - y0) * f
            half = (top_w / 2) * (1 - f) ** 0.9 + br * 0.55 * f + e
            pts_l.append((cx - half, yy))
            pts_r.append((cx + half, yy))
        p.d.polygon([(a * p.s, b * p.s) for a, b in pts_l + pts_r[::-1]], fill=col)
        p.d.ellipse(p._b(cx - br - e, yb - br * 0.95 - e, cx + br + e, yb + br * 1.1 + e), fill=col)

    for e, col in ((ow, p.oc), (0, jam)):
        for cx, cy, rx, ry in blobs:
            p.d.ellipse(p._b(cx - rx - e, cy - ry - e, cx + rx + e, cy + ry + e), fill=col)
        for d_ in drips:
            drip(*d_, e=e, col=col)
    # 윤기. 덩어리 위쪽에 긴 반사 하나, 긴 줄기에 짧은 반사, 방울마다 작은 점.
    # 반사가 없으면 잼이 아니라 붉은 페인트다
    shine = (255, 255, 255, 190)
    lp.ell(x + w - 13, y - 1.8, 3.8, 1.1, shine, outline=False)
    lp.line([(x + w - 6.4, y + 6), (x + w - 6.0, y + 12)], (255, 255, 255, 120), 0.9)
    for cx, _, yb, _, br in drips:
        lp.dot(cx - br * 0.35, yb - br * 0.3, br * 0.3, fill=shine)


def f_toast(t, bw, bh, first):
    f = [((-OW, -OW, bw + OW, bh + OW), ()),
         ((-OW, -OW, bw + OW, 16 + OW), ('top',))]
    if first:
        # 잼은 덩어리와 줄기가 모두 늘어나는 세로 줄보다 위에서 끝난다
        f.append(((bw - 26, -5.6, bw + 3.4, 22.5), ('inner', 'top')))
    return f


def d_sign(p, lp, x, y, w, h, first, ck, t):
    """나무 팻말. 네 귀퉁이에 못, 아래쪽에 판자 두께. 첫 장엔 땅에 박는 말뚝."""
    col = _c(t[ck])
    if first:
        p.rr(x + 12, y + h - 4, x + 20, y + h + 12, 1.5, hexc(t.get('post', '#9C6B3E')), ow=OW)
    p.rr(x, y, x + w, y + h, 3, hexc(_g().mix(col, t['char_outline'], 0.28)), ow=OW)
    p.d.rounded_rectangle(p._b(x, y, x + w, y + h - 3), radius=3 * p.s, fill=hexc(col))
    nail = hexc(t.get('nail', '#8A7A6A'))
    for nx, ny in ((x + 5, y + 5), (x + w - 5, y + 5), (x + 5, y + h - 7), (x + w - 5, y + h - 7)):
        p.dot(nx, ny, 1.7, fill=nail)
        lp.dot(nx - 0.5, ny - 0.5, 0.6, fill=(255, 255, 255, 170))


def f_sign(t, bw, bh, first):
    f = [((-OW, -OW, bw + OW, bh + OW), ()),
         ((0, bh - 6, bw, bh), ('bottom',)),
         ((3, 3, 7, 7), ('outer', 'top')), ((bw - 7, 3, bw - 3, 7), ('inner', 'top')),
         ((3, bh - 9, 7, bh - 5), ('outer', 'bottom')), ((bw - 7, bh - 9, bw - 3, bh - 5), ('inner', 'bottom'))]
    if first:
        f.append(((12 - OW, bh - 4, 20 + OW, bh + 12 + OW), ('outer', 'bottom')))
    return f


def d_panel(p, lp, x, y, w, h, first, ck, t):
    """우주선 판. 둥근 판 안쪽에 한 줄 더 두른다. 첫 장엔 안테나와 반짝이."""
    col = _c(t[ck])
    if first:
        p.line([(x + 14, y + 2), (x + 10, y - 9)], p.oc, 1.8)
        p.ell(x + 10, y - 10.5, 2.8, 2.8, hexc(t['accent']), ow=1.3)
    p.rr(x, y, x + w, y + h, 12, hexc(col), ow=OW)
    p.d.rounded_rectangle(p._b(x + 3.5, y + 3.5, x + w - 3.5, y + h - 3.5), radius=8.5 * p.s,
                          outline=hexc(_g().mix(col, t['char_outline'], 0.3)),
                          width=max(1, int(1.1 * p.s)))
    if first:
        cx, cy = x + w - 12, y - 2
        q = 1.5
        pts = [(cx, cy - 5.5), (cx + q, cy - q), (cx + 5.5, cy), (cx + q, cy + q),
               (cx, cy + 5.5), (cx - q, cy + q), (cx - 5.5, cy), (cx - q, cy - q)]
        p.poly(pts, hexc(t.get('star', '#FFD84D')), ow=1.1)


def f_panel(t, bw, bh, first):
    f = [((-OW, -OW, bw + OW, bh + OW), ())]
    if first:
        f += [((5, -15, 16, 2), ('outer', 'top')),
              ((bw - 19, -9, bw - 5, 5), ('inner', 'top'))]
    return f


def d_leaf(p, lp, x, y, w, h, first, ck, t):
    """잎. 바깥 위와 안쪽 아래 귀퉁이만 크게 둥글다. 첫 장엔 잎자루와 이슬 한 방울.

    잎맥은 넣지 않는다 — 몸통을 가로지르는 선은 취소선으로 읽힌다(젤리에서 겪었다).
    """
    R, r = 16, 4
    if first:
        stem = hexc(t.get('stem', '#5A9A5A'))
        pts = [(x + 8, y + h - 3), (x + 6, y + h + 5), (x + 3, y + h + 10)]
        p.line(pts, p.oc, 3.8)
        p.line(pts, stem, 1.8)
        p.poly([(x + 6.5, y + h + 5), (x + 11, y + h + 3), (x + 15.5, y + h + 6.5), (x + 10, y + h + 8.5)],
               stem, ow=1.1)

    def shape(e, col):
        p.d.rounded_rectangle(p._b(x - e, y - e, x + w + e, y + h + e), radius=(R + e) * p.s, fill=col)
        p.d.rounded_rectangle(p._b(x + w / 2, y - e, x + w + e, y + h / 2), radius=(r + e) * p.s, fill=col)
        p.d.rounded_rectangle(p._b(x - e, y + h / 2, x + w / 2, y + h + e), radius=(r + e) * p.s, fill=col)

    shape(OW, p.oc)
    shape(0, hexc(_c(t[ck])))
    if first:
        p.ell(x + w - 10, y + 5, 2.6, 3.2, hexc(t.get('dew', '#DFF3FF')), ow=1.1)
        lp.dot(x + w - 10.8, y + 3.8, 0.8, fill=(255, 255, 255, 230))


def f_leaf(t, bw, bh, first):
    f = [((-OW, -OW, bw + OW, bh + OW), ())]
    if first:
        f += [((1, bh - 5, 17, bh + 12), ('outer', 'bottom')),
              ((bw - 14, 0.5, bw - 6, 9.5), ('inner', 'top'))]
    return f


STYLES.update({
    'ticket': dict(bw=40, bh=44, radius=5, draw=d_ticket, features=f_ticket),
    'toast':  dict(bw=40, bh=44, radius=8, draw=d_toast, features=f_toast),
    'sign':   dict(bw=40, bh=44, radius=3, draw=d_sign, features=f_sign),
    'panel':  dict(bw=40, bh=44, radius=12, draw=d_panel, features=f_panel),
    'leaf':   dict(bw=40, bh=44, radius=16, draw=d_leaf, features=f_leaf),
})


def c_popcorn(p):
    """톡톡 — 팝콘 통. 줄무늬는 양 가장자리에만 둔다. 가운데까지 칠하면 36pt 에서 줄무늬만 읽힌다."""
    face = hexc(FACE)
    red, white, pop = hexc('#E8413B'), hexc('#FFFFFF'), hexc('#FFF4D6')
    puffs = [(30, 38, 12), (50, 28, 14), (70, 38, 12), (40, 44, 11), (60, 44, 11)]
    for cx, cy, r in puffs:
        p.ell(cx, cy, r, r, pop, ow=4)
    for cx, cy, r in puffs:
        p.ell(cx, cy, r - 0.5, r - 0.5, pop, outline=False)
    p.poly([(16, 50), (84, 50), (74, 97), (26, 97)], white, ow=4.5)
    p.poly([(16, 50), (29, 50), (35, 97), (26, 97)], red, outline=False)
    p.poly([(71, 50), (84, 50), (74, 97), (65, 97)], red, outline=False)
    p.rr(12, 46, 88, 58, 4, red, ow=4)
    p.dot(41, 72, 5, fill=face)
    p.dot(59, 72, 5, fill=face)
    p.ell(33, 81, 5, 3, hexc('#FFA8A8'), outline=False)
    p.ell(67, 81, 5, 3, hexc('#FFA8A8'), outline=False)
    p.arc((45, 73, 55, 84), 20, 160, w=3.5, fill=face)


def c_bread(p):
    """말랑 — 식빵 한 쪽."""
    face = hexc(FACE)
    crust, crumb = hexc('#D08A45'), hexc('#FFF1D2')
    parts = lambda e: [(10 - e, 8 - e, 90 + e, 52 + e, 22 + e), (16 - e, 30, 84 + e, 94 + e, 8 + e)]
    for e, col in ((4.5, p.oc), (0, crust), (-7, crumb)):
        for x0, y0, x1, y1, r in parts(e):
            p.d.rounded_rectangle(p._b(x0, y0, x1, y1), radius=max(1, r) * p.s, fill=col)
    p.dot(38, 56, 5, fill=face)
    p.dot(62, 56, 5, fill=face)
    p.ell(28, 66, 6.5, 4, hexc('#FFB38A'), outline=False)
    p.ell(72, 66, 6.5, 4, hexc('#FFB38A'), outline=False)
    p.arc((44, 57, 56, 69), 20, 160, w=3.5, fill=face)


def c_flame(p):
    """타닥 — 장작 위의 모닥불. 얼굴은 안쪽 노란 불꽃에 둔다."""
    face = hexc(FACE)
    orange, yellow, log = hexc('#FF8A3D'), hexc('#FFD45A'), hexc('#9A6238')
    tri = [(22, 60), (50, 4), (78, 60)]
    p.ell(50, 62, 28, 26, orange, ow=4.5)
    p.poly(tri, orange, ow=4.5)
    p.ell(50, 62, 28, 26, orange, outline=False)
    p.ell(50, 64, 18, 17, yellow, outline=False)
    p.poly([(32, 62), (50, 26), (68, 62)], yellow, outline=False)
    for pts in ([(10, 82), (82, 72), (86, 84), (14, 96)], [(90, 82), (18, 72), (14, 84), (86, 96)]):
        p.poly(pts, log, ow=4)
    p.dot(42, 60, 4.5, fill=face)
    p.dot(58, 60, 4.5, fill=face)
    p.arc((45, 61, 55, 71), 20, 160, w=3.5, fill=face)


def c_saturn(p):
    """링링 — 고리 두른 행성. 고리는 뒤 반쪽을 먼저, 앞 반쪽을 얼굴 아래로 나중에 긋는다."""
    face = hexc(FACE)
    ring, body = hexc('#B9A6FF'), hexc('#FFC98A')
    box = (4, 44, 96, 80)
    p.arc(box, 180, 360, w=11, fill=p.oc)
    p.arc((5.5, 45.5, 94.5, 78.5), 180, 360, w=6, fill=ring)
    p.ell(50, 50, 31, 31, body, ow=4.5)
    p.arc(box, 0, 180, w=11, fill=p.oc)
    p.arc((5.5, 45.5, 94.5, 78.5), 0, 180, w=6, fill=ring)
    p.dot(39, 46, 5, fill=face)
    p.dot(61, 46, 5, fill=face)
    p.ell(30, 56, 5.5, 3.5, hexc('#FF9C7A'), outline=False)
    p.ell(70, 56, 5.5, 3.5, hexc('#FF9C7A'), outline=False)
    p.arc((45, 47, 55, 58), 20, 160, w=3.5, fill=face)


def c_cactus(p):
    """뾰족 — 화분에 심은 선인장. 머리에 꽃 한 송이."""
    face = hexc(FACE)
    green, pot, rim = hexc('#6CC57C'), hexc('#E07A4F'), hexc('#F09062')
    parts = [(30, 18, 70, 76, 18), (10, 32, 26, 56, 8), (18, 46, 36, 57, 5),
             (74, 24, 90, 48, 8), (64, 38, 82, 49, 5)]
    for x0, y0, x1, y1, r in parts:
        p.d.rounded_rectangle(p._b(x0 - 4.5, y0 - 4.5, x1 + 4.5, y1 + 4.5), radius=(r + 4.5) * p.s, fill=p.oc)
    for x0, y0, x1, y1, r in parts:
        p.d.rounded_rectangle(p._b(x0, y0, x1, y1), radius=r * p.s, fill=green)
    for a in range(0, 360, 72):
        p.ell(50 + math.cos(math.radians(a)) * 5, 15 + math.sin(math.radians(a)) * 5, 4, 4,
              hexc('#FF8FB1'), ow=2)
    p.dot(50, 15, 3, fill=hexc('#FFD45A'))
    p.poly([(26, 74), (74, 74), (68, 97), (32, 97)], pot, ow=4.5)
    p.rr(22, 68, 78, 80, 3, rim, ow=4)
    p.dot(41, 44, 4.8, fill=face)
    p.dot(59, 44, 4.8, fill=face)
    p.ell(35, 54, 5, 3, hexc('#FFA8A8'), outline=False)
    p.ell(65, 54, 5, 3, hexc('#FFA8A8'), outline=False)
    p.arc((45, 46, 55, 56), 20, 160, w=3.5, fill=face)


CHARS.update({'popcorn': c_popcorn, 'bread': c_bread, 'flame': c_flame,
              'saturn': c_saturn, 'cactus': c_cactus})


# --- 네온사인: 이중관·간판·전극·말꼬리 ---------------------------------------
# 몸통은 어둡게 두고 테두리가 빛나는 유리관이 된다. 관 한가운데는 하얗게 달아오르고, 관 색이
# 몸통 안쪽으로 번진다. 바깥 글로우는 재질로 고른다(tools/glow.py) — 관은 tube(강한 블룸),
# 간판은 sign(아래로 떨어지는 빛).
#
# 관은 몸통 모양의 가장자리를 가운데에 둔 띠로 만든다. 모양을 그대로 따라 휘므로 꼬리까지
# 이어진 말풍선도 관 하나로 두를 수 있다.

NEON_TW = 2.6                       # 관 굵기(pt)
NEON_BODY = (12, 8, 16, 215)        # 관 안쪽 몸통. 뒤 벽이 살짝 비친다


def _neon_blank(p):
    return Image.new('L', p.img.size, 0)


def _neon_rr(p, x0, y0, x1, y1, r):
    m = _neon_blank(p)
    ImageDraw.Draw(m).rounded_rectangle(p._b(x0, y0, x1, y1), radius=r * p.s, fill=255)
    return m


def _neon_band(m, px):
    """모양의 가장자리를 가운데에 둔 띠."""
    k = max(3, int(round(px)) | 1)
    return ImageChops.subtract(m.filter(ImageFilter.MaxFilter(k)), m.filter(ImageFilter.MinFilter(k)))


def _neon_over(img, rgb, alpha):
    lay = Image.new('RGBA', img.size, tuple(rgb) + (255,))
    lay.putalpha(alpha)
    img.alpha_composite(lay)


def _neon(p, shape, col, tw=NEON_TW, fill=None, cut=None):
    """shape 가장자리에 네온관을 두른다. cut 은 관이 끊긴 자리다."""
    s = p.s
    c = hexc(col)[:3]
    if fill:
        _neon_over(p.img, fill[:3], shape.point(lambda v: v * fill[3] // 255))
    tube = _neon_band(shape, tw * s).filter(ImageFilter.GaussianBlur(0.5))
    if cut is not None:
        tube = ImageChops.subtract(tube, cut)
    # 관에서 번진 빛이 몸통 안쪽을 물들인다
    spill = ImageChops.multiply(tube.filter(ImageFilter.GaussianBlur(3.2 * s)), shape)
    _neon_over(p.img, c, spill.point(lambda v: v * 130 // 255))
    _neon_over(p.img, c, tube)
    core = _neon_band(shape, tw * 0.38 * s).filter(ImageFilter.GaussianBlur(0.4))
    if cut is not None:
        core = ImageChops.subtract(core, cut)
    _neon_over(p.img, hexc(_g().glow_tint(col, 0.72))[:3], core)


def d_neon_double(p, lp, x, y, w, h, first, ck, t):
    """이중관. 바깥 굵은 관 안에 가는 관이 한 줄 더 돈다. 첫 장엔 네온 별."""
    col = _c(t[ck])
    _neon(p, _neon_rr(p, x, y, x + w, y + h, 16), col, fill=NEON_BODY)
    _neon(p, _neon_rr(p, x + 5, y + 5, x + w - 5, y + h - 5, 11), col, tw=1.5)
    if first:
        cx, cy, R, r = x + w - 10, y - 4, 7, 3
        m = _neon_blank(p)
        pts = [(cx + math.cos(math.radians(-90 + i * 36)) * (R if i % 2 == 0 else r),
                cy + math.sin(math.radians(-90 + i * 36)) * (R if i % 2 == 0 else r)) for i in range(10)]
        ImageDraw.Draw(m).polygon([(a * p.s, b * p.s) for a, b in pts], fill=255)
        _neon(p, m, col, tw=1.6, fill=(12, 8, 16, 255))


def f_neon_double(t, bw, bh, first):
    f = [((-NEON_TW, -NEON_TW, bw + NEON_TW, bh + NEON_TW), ())]
    if first:
        f.append(((bw - 18.5, -12.5, bw - 1.5, 4), ('inner', 'top')))
    return f


def d_neon_sign(p, lp, x, y, w, h, first, ck, t):
    """간판. 어두운 금속 판에 네온을 박고 모서리에 볼트. 첫 장은 사슬에 매달린다."""
    col = _c(t[ck])
    if first:
        for cx in (x + 10, x + w - 10):
            for k in range(3):
                yy = y - 13.5 + k * 4.4
                p.d.ellipse(p._b(cx - 1.6, yy, cx + 1.6, yy + 5.4), outline=(110, 104, 118, 255),
                            width=max(1, int(1.0 * p.s)))
    p.rr(x, y, x + w, y + h, 5, hexc('#18141D'), ow=1.4, oc=hexc('#2E2836'))
    p.rect(x + 1, y + 0.6, x + w - 1, y + 1.4, (70, 64, 78, 255))
    _neon(p, _neon_rr(p, x + 5, y + 5, x + w - 5, y + h - 5, 6), col, tw=2.2)
    for bx, by in ((x + 2.5, y + 2.5), (x + w - 2.5, y + 2.5),
                   (x + 2.5, y + h - 2.5), (x + w - 2.5, y + h - 2.5)):
        p.dot(bx, by, 1.1, fill=hexc('#5A5462'))


def f_neon_sign(t, bw, bh, first):
    f = [((-1.4, -1.4, bw + 1.4, bh + 1.4), ()),
         ((1, 1, 4, 4), ('outer', 'top')), ((bw - 4, 1, bw - 1, 4), ('inner', 'top')),
         ((1, bh - 4, 4, bh - 1), ('outer', 'bottom')), ((bw - 4, bh - 4, bw - 1, bh - 1), ('inner', 'bottom'))]
    if first:
        f += [((7.5, -14, 12.5, 1), ('outer', 'top')), ((bw - 12.5, -14, bw - 7.5, 1), ('inner', 'top'))]
    return f


def d_neon_electrode(p, lp, x, y, w, h, first, ck, t):
    """전극. 실제 네온관처럼 바깥 아래 귀퉁이에서 관이 끊기고 양 끝에 전극 캡이 있다.
    첫 장엔 전극에서 전선이 늘어진다."""
    col = _c(t[ck])
    cut = _neon_blank(p)
    ImageDraw.Draw(cut).rectangle(p._b(x + 8, y + h - 6, x + 16, y + h + 6), fill=255)
    _neon(p, _neon_rr(p, x, y, x + w, y + h, 12), col, fill=NEON_BODY, cut=cut)
    if first:
        p.line([(x + 16, y + h + 1.5), (x + 17.5, y + h + 8), (x + 23, y + h + 13)], (14, 14, 16, 255), 1.6)
    for ex in (x + 8, x + 16):
        p.rr(ex - 1.9, y + h - 2.5, ex + 1.9, y + h + 2.5, 1, hexc('#26262B'), ow=0.8, oc=hexc('#08080A'))
        p.rect(ex - 1.2, y + h - 2.0, ex - 0.6, y + h + 2.0, (110, 110, 118, 255))


def f_neon_electrode(t, bw, bh, first):
    f = [((-NEON_TW, -NEON_TW, bw + NEON_TW, bh + NEON_TW), ()),
         ((5, bh - 4, 19, bh + 4), ('outer', 'bottom'))]
    if first:
        f.append(((14, bh, 24.5, bh + 14), ('outer', 'bottom')))
    return f


def d_neon_speech(p, lp, x, y, w, h, first, ck, t):
    """말꼬리. 첫 장은 꼬리까지 관 하나로 이어진다."""
    shape = _neon_rr(p, x, y, x + w, y + h, 18)
    if first:
        pts = [(x + 12, y + h - 6), (x + 27, y + h - 2), (x + 1, y + h + 12)]
        ImageDraw.Draw(shape).polygon([(a * p.s, b * p.s) for a, b in pts], fill=255)
    _neon(p, shape, _c(t[ck]), fill=NEON_BODY)


def f_neon_speech(t, bw, bh, first):
    f = [((-NEON_TW, -NEON_TW, bw + NEON_TW, bh + NEON_TW), ())]
    if first:
        f.append(((-1.5, bh - 8, 28.5, bh + 13.5), ('outer', 'bottom')))
    return f


STYLES.update({
    'neon_double':    dict(bw=40, bh=44, radius=16, draw=d_neon_double, features=f_neon_double),
    'neon_sign':      dict(bw=40, bh=44, radius=6, draw=d_neon_sign, features=f_neon_sign),
    'neon_electrode': dict(bw=40, bh=44, radius=12, draw=d_neon_electrode, features=f_neon_electrode),
    'neon_speech':    dict(bw=40, bh=44, radius=18, draw=d_neon_speech, features=f_neon_speech),
})


def p_neon(t, idx, px):
    """네온사인 기본 프로필. 어두운 벽돌 조각 위에 하트·별·초승달 네온관 하나.

    세 장이 하트는 보낸 색, 별은 받은 색, 초승달은 벽 낙서의 셋째 색이다. 목록 화면에서 가장 많이
    반복되는 그림이라, 색만 바꾼 기본 사람 모양일 때는 목록이 테마와 따로 놀았다.
    36pt 에서 읽혀야 해서 관을 굵게(폭의 7.5%) 두고 모양은 윤곽이 단순한 것만 쓴다.
    """
    import scenes
    g = _g()
    k = 3
    S = px * k
    img = Image.new('RGB', (S, S), (22, 14, 18))
    d = ImageDraw.Draw(img)
    bh = S / 6
    mortar = (34, 22, 26)
    for j in range(7):                                   # 벽돌 줄눈. 아주 옅게
        y = j * bh
        d.line([(0, y), (S, y)], fill=mortar, width=max(1, S // 90))
        off = S / 6 if j % 2 else 0
        for i in range(4):
            x = off + i * S / 3
            d.line([(x, y), (x, y + bh)], fill=mortar, width=max(1, S // 90))
    kind = ('heart', 'star', 'moon')[idx % 3]
    col = (_c(t['send']), _c(t['recv']), t.get('neon_third', '#B45CFF'))[idx % 3]
    lay = Image.new('RGB', (S, S))
    core = Image.new('RGB', (S, S))
    ld, cd = ImageDraw.Draw(lay), ImageDraw.Draw(core)
    cx = S / 2 + (S * 0.04 if kind == 'moon' else 0)
    for line in scenes._neon_doodle(kind, cx, S / 2 + S * 0.02, S * 0.3):
        ld.line(line, fill=g.rgb(col), width=int(S * 0.075), joint='curve')
        cd.line(line, fill=g.rgb(g.glow_tint(col, 0.75)), width=int(S * 0.028), joint='curve')
    halo = lay.filter(ImageFilter.GaussianBlur(S * 0.07)).point(lambda v: min(255, int(v * 1.7)))
    img = ImageChops.screen(img, halo)
    img = ImageChops.screen(img, lay)
    img = ImageChops.screen(img, core)
    return img.resize((px, px), Image.LANCZOS).convert('RGBA')


PROFILES['neon'] = p_neon
