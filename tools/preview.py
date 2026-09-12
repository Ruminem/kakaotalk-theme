# -*- coding: utf-8 -*-
"""테마 미리보기 그림과 갤러리 페이지를 만든다.

gen.py 가 부른다. 직접 돌려도 된다:

    python tools/preview.py

하나씩 폰에 적용해보지 않고 색을 확인하려고 만든 것이다.
화면 네 장을 그린다 — 채팅 목록, 채팅방, 잠금화면, 실행화면.
실행화면은 안드로이드에만 있는 화면이지만 색 확인용으로 같이 그린다.

폰과 같은 좌표(pt)에 배치하고 폰과 같은 3배로 그린 뒤 줄여서 내보낸다.
한때 1배(460px)로 그렸는데, 글로우의 흐림이 몇 픽셀짜리 계단이 되고 글자가
뭉개져서 폰에 깐 것보다 훨씬 싸구려로 보였다. README 에서 그 그림을 보고
지나치면 폰에서 예쁜 것은 아무 소용이 없다.
"""
import multiprocessing
import os
import sys

# 윈도우 파이썬은 기본 출력 인코딩이 cp949 라 한글이 깨진다.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen  # noqa: E402
import charbubble  # noqa: E402

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

rgb = gen.rgb
S = 3                  # 폰의 @3x 와 같은 배율. 말풍선도 테마에 들어가는 @3x 장을 그대로 쓴다
PW, PH = 402, 874      # 화면 크기(pt). 요즘 아이폰 한 대
OUT = 1.5              # 내보내는 배율(603x1311). README 가 200px 로 줄여 보여줘도 폰 화면에서 선명하다
W, H = PW * S, PH * S
NAV_Y = 84             # 머리 단추 줄의 가운데
BAR_H, BAR_B = 48, 30  # 입력창 높이와 그 아래 여백(홈 표시줄 자리)
LINE_H = 22            # 말풍선 글자 한 줄 높이
MSG_PT = 16            # 말풍선 글자 크기


def u(v):
    """pt 를 그리는 픽셀로."""
    return int(round(v * S))


# --- 글자 ----------------------------------------------------------------

_NOTO = r'C:\Windows\Fonts\NotoSansKR-VF.ttf'
_fonts = {}


def font(pt, weight=400):
    """본문 글꼴. Noto Sans KR 이 있으면 그걸 쓴다.

    맑은 고딕은 자간이 넓고 획이 가늘어서 폰 글꼴(애플 SD 산돌고딕)과 인상이 다르다.
    가변 글꼴이라 굵기를 꼭 정한다 — 안 정하면 가장 가는 100 으로 나온다.
    """
    k = (pt, weight)
    if k not in _fonts:
        if os.path.exists(_NOTO):
            f = ImageFont.truetype(_NOTO, u(pt))
            f.set_variation_by_axes([weight])
        else:
            p = os.path.join(r'C:\Windows\Fonts',
                             'malgunbd.ttf' if weight >= 600 else 'malgun.ttf')
            f = ImageFont.truetype(p, u(pt)) if os.path.exists(p) else ImageFont.load_default()
        _fonts[k] = f
    return _fonts[k]


def text(d, x, y, s, pt, fill, weight=400, anchor='la'):
    d.text((u(x), u(y)), s, font=font(pt, weight), fill=fill, anchor=anchor)


def text_w(s, pt, weight=400):
    """글자 폭(pt)."""
    return font(pt, weight).getlength(s) / S


# --- 바탕과 시스템이 그리는 것 ---------------------------------------------
# 상태표시줄, 머리 단추, 입력창은 카톡 테마가 아니라 iOS 가 그린다. 테마 색을 안 받고
# 뒤에 깔린 것에 따라 밝거나 어둡게만 바뀐다. 불투명한 띠로 그리면 배경이 화면
# 가운데에만 보여서 폰에서 본 것보다 답답해진다.

def light(t):
    return gen._is_light(t)


def ink(t):
    """상태표시줄 글자색. 검정 아니면 흰색이다."""
    return (0, 0, 0) if light(t) else (255, 255, 255)


def glyph(t):
    """유리 단추 위 아이콘 색."""
    return (34, 34, 38) if light(t) else (242, 242, 246)


def cover(img, w, h):
    """화면을 꽉 채우도록 늘리고 넘치는 쪽을 자른다. 카톡이 배경을 까는 방식이다."""
    k = max(w / img.width, h / img.height)
    rw, rh = round(img.width * k), round(img.height * k)
    img = img.resize((rw, rh), Image.LANCZOS)
    x, y = (rw - w) // 2, (rh - h) // 2
    return img.crop((x, y, x + w, y + h))


def backdrop(t, spec, fill, flat=False):
    """화면 전체 배경. 테마에 들어가는 @3x 그림(900x1950)을 화면 크기로 늘린다."""
    if not spec:
        return Image.new('RGB', (W, H), rgb(fill))
    return cover(gen.background(t, spec, 900, 1950, flat=flat).convert('RGB'), W, H)


def _rr_mask(size, box, r):
    """둥근 사각형 가림막. 4배로 그려 줄여서 가장자리를 매끈하게 한다."""
    k = 4
    m = Image.new('L', (size[0] * k, size[1] * k), 0)
    x0, y0, x1, y1 = box
    ImageDraw.Draw(m).rounded_rectangle([x0 * k, y0 * k, x1 * k - 1, y1 * k - 1],
                                        radius=r * k, fill=255)
    return m.resize(size, Image.LANCZOS)


def glass(img, box, t, r=None):
    """iOS 26 의 떠 있는 유리 단추. 뒤를 흐리고 밝게(어두운 테마면 어둡게) 덮는다.

    img 는 RGB 이고 제자리에서 바뀐다.
    """
    x0, y0, x1, y1 = (u(v) for v in box)
    R = u(r if r is not None else (box[3] - box[1]) / 2)
    lt = light(t)
    m = u(14)
    bx = (max(0, x0 - m), max(0, y0 - m), min(W, x1 + m), min(H, y1 + m))
    reg = img.crop(bx).convert('RGBA')
    inner = (x0 - bx[0], y0 - bx[1], x1 - bx[0], y1 - bx[1])
    mask = _rr_mask(reg.size, inner, R)

    frost = reg.filter(ImageFilter.GaussianBlur(u(8)))
    tint = Image.new('RGBA', reg.size, (255, 255, 255, 255) if lt else (34, 36, 42, 255))
    frost = Image.blend(frost, tint, 0.55 if lt else 0.45)

    shadow = Image.new('RGBA', reg.size, (0, 0, 0, 255))
    shadow.putalpha(ImageChops.offset(mask, 0, u(2)).filter(ImageFilter.GaussianBlur(u(5)))
                    .point(lambda v: int(v * (0.10 if lt else 0.30))))
    reg.alpha_composite(shadow)
    reg.paste(frost, (0, 0), mask)

    # 유리 가장자리의 가는 빛. 이게 없으면 뿌연 판으로 보인다
    rim = Image.new('RGBA', reg.size, (255, 255, 255, 255))
    edge = ImageChops.subtract(mask, mask.filter(ImageFilter.GaussianBlur(S * 0.6)))
    rim.putalpha(edge.point(lambda v: min(255, int(v * (2.2 if lt else 0.8)))))
    reg.alpha_composite(rim)
    img.paste(reg.convert('RGB'), bx[:2])


def edge_fade(img, t, top=132, bottom=120):
    """화면 위아래 가장자리를 바탕색으로 옅게 덮는다.

    iOS 26 이 머리 단추와 입력창 뒤를 이렇게 처리한다. 대화가 단추 밑으로
    올라가도 글자끼리 겹쳐 읽히지 않는다.
    """
    a = Image.new('L', (1, PH), 0)
    px = a.load()
    for y in range(PH):
        v = 0.0
        if y < 58:                           # 상태표시줄 자리는 거의 덮는다
            v = 0.94
        elif y < top:
            v = 0.94 * (1 - (y - 58) / (top - 58)) ** 1.4
        if PH - y < bottom:
            v = max(v, 0.72 * (1 - (PH - y) / bottom) ** 1.7)
        px[0, y] = int(255 * v)
    lay = Image.new('RGBA', (W, H), rgb(t['bg']) + (255,))
    lay.putalpha(a.resize((W, H), Image.BILINEAR))
    return Image.alpha_composite(img.convert('RGBA'), lay).convert('RGB')


def status_bar(img, t):
    d = ImageDraw.Draw(img)
    c = ink(t)
    text(d, 64, 32, '9:41', 17, c, 600, 'mm')
    x = PW - 106                                  # 신호 네 칸
    for i in range(4):
        hh = 4.5 + i * 2.5
        d.rounded_rectangle([u(x + i * 5), u(37 - hh), u(x + i * 5 + 3.3), u(37)],
                            radius=u(1), fill=c)
    cx, cy = PW - 72, 38                          # 와이파이
    for rr in (11, 7):
        d.arc([u(cx - rr), u(cy - rr), u(cx + rr), u(cy + rr)], 225, 315,
              fill=c, width=u(2.2))
    d.pieslice([u(cx - 3.6), u(cy - 3.6), u(cx + 3.6), u(cy + 3.6)], 225, 315, fill=c)
    bx = PW - 53                                  # 배터리
    d.rounded_rectangle([u(bx), u(26.5), u(bx + 26), u(38.5)], radius=u(3.8),
                        outline=c, width=u(1.1))
    d.rounded_rectangle([u(bx + 2.2), u(28.7), u(bx + 23.8), u(36.3)], radius=u(2),
                        fill=c)
    d.rounded_rectangle([u(bx + 27.2), u(30.5), u(bx + 28.8), u(34.5)], radius=u(0.8),
                        fill=c)


def home_bar(img, t):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([u(PW / 2 - 70), u(PH - 9), u(PW / 2 + 70), u(PH - 4)],
                        radius=u(2.5), fill=ink(t))


# --- 아이콘 --------------------------------------------------------------
# 글꼴 글리프(⌕ ☰ 같은 것)를 쓰면 없는 문자가 네모로 나온다. 도형으로 직접 그린다.

def ic_search(d, cx, cy, c):
    r, ox, oy = 7.5, cx - 1.5, cy - 1.5
    d.ellipse([u(ox - r), u(oy - r), u(ox + r), u(oy + r)], outline=c, width=u(2.2))
    d.line([(u(ox + r * 0.7), u(oy + r * 0.7)), (u(cx + 8.5), u(cy + 8.5))],
           fill=c, width=u(2.4))


def ic_menu(d, cx, cy, c, w=20):
    for k in (-7, 0, 7):
        d.rounded_rectangle([u(cx - w / 2), u(cy + k - 1.1), u(cx + w / 2), u(cy + k + 1.1)],
                            radius=u(1.1), fill=c)


def ic_back(d, cx, cy, c):
    d.line([(u(cx + 5), u(cy - 10)), (u(cx - 5), u(cy)), (u(cx + 5), u(cy + 10))],
           fill=c, width=u(2.6), joint='curve')


def ic_plus(d, cx, cy, c, r=8):
    d.rounded_rectangle([u(cx - r), u(cy - 1.1), u(cx + r), u(cy + 1.1)], radius=u(1.1), fill=c)
    d.rounded_rectangle([u(cx - 1.1), u(cy - r), u(cx + 1.1), u(cy + r)], radius=u(1.1), fill=c)


def ic_smile(d, cx, cy, c, r=10):
    d.ellipse([u(cx - r), u(cy - r), u(cx + r), u(cy + r)], outline=c, width=u(1.8))
    for ex in (-3.6, 3.6):
        d.ellipse([u(cx + ex - 1.4), u(cy - 4.6), u(cx + ex + 1.4), u(cy - 1.8)], fill=c)
    d.arc([u(cx - 5.5), u(cy - 4), u(cx + 5.5), u(cy + 5.5)], 20, 160, fill=c, width=u(1.8))


# --- 말풍선 --------------------------------------------------------------

def avatar(img, t, i, x, y, size):
    """기본 프로필. 테마에 들어가는 그림을 카톡처럼 둥근 사각형으로 잘라 붙인다.

    세 장을 돌려가며 배정하므로 줄마다 다른 장이 나오게 한다.
    """
    px = u(size)
    src = gen.profile_image(t, i, px).convert('RGBA')
    mask = ImageChops.multiply(_rr_mask((px, px), (0, 0, px, px), px * 0.39),
                               src.getchannel('A'))
    img.paste(src.convert('RGB'), (u(x), u(y)), mask)


def bubble_sheet(t, side, variant):
    """테마에 들어가는 @3x 말풍선 한 장과 그 치수(pt).

    ins 는 edgeinsets(위, 왼, 아래, 오), outer/inner/top/bottom 은 그림 가장자리에서
    몸통까지의 투명한 여백이다. 지금은 사방이 글로우 여백으로 같지만, 모양이 한쪽으로
    치우친 말풍선(꼬리 같은 것)이 생기면 여기서 갈라진다.
    """
    if t.get('char_style'):
        return charbubble.sheet(t, side, variant, S)
    glow, pad = gen.glow_of(t)
    rim, frost = gen.glass_of(t)
    pal = t[side] if variant == '01' else t[side + '_alt']
    img = gen.bubble(S, pal, t.get('bubble_style', 'solid'), t.get('bubble_alpha', 255),
                     glow, pad, t.get('flat', False), rim, frost)
    iv, ih = gen.insets_of(t)
    return img, dict(cap=gen.CAP + pad, ins=(iv + pad, ih + pad, iv + pad, ih + pad),
                     outer=pad, inner=pad, top=pad, bottom=pad)


def _stretch_axis(img, cap, n, horizontal):
    size = img.width if horizontal else img.height
    if n == size:
        return img
    if n < size:
        # 늘일 줄이 없으니 통째로 눌린다. 글자가 한 줄이고 여백이 좁으면 프레임이
        # 그림보다 작아지는데, 그때 모서리까지 같이 눌리는 것도 폰과 같다
        return img.resize((n, img.height) if horizontal else (img.width, n), Image.LANCZOS)
    grow = n - size + 1
    if horizontal:
        parts = (img.crop((0, 0, cap, img.height)),
                 img.crop((cap, 0, cap + 1, img.height)).resize((grow, img.height),
                                                                 Image.NEAREST),
                 img.crop((cap + 1, 0, size, img.height)))
        out = Image.new('RGBA', (n, img.height), (0, 0, 0, 0))
        for p, x in zip(parts, (0, cap, cap + grow)):
            out.paste(p, (x, 0))
    else:
        parts = (img.crop((0, 0, img.width, cap)),
                 img.crop((0, cap, img.width, cap + 1)).resize((img.width, grow),
                                                                Image.NEAREST),
                 img.crop((0, cap + 1, img.width, size)))
        out = Image.new('RGBA', (img.width, n), (0, 0, 0, 0))
        for p, y in zip(parts, (0, cap, cap + grow)):
            out.paste(p, (0, y))
    return out


def stretch(img, cap, w, h):
    """카톡(iOS)이 말풍선을 늘리는 방식. cap 자리의 한 줄만 늘이고 나머지는 그대로 둔다.

    필요한 크기로 새로 그리면 그라데이션이 늘어나며 생기는 띠나 그림이 뭉개지는 것을
    못 잡는다. 테마에 넣는 그 장을 그대로 늘려야 폰에서 보는 것이 나온다.
    """
    return _stretch_axis(_stretch_axis(img, cap, w, True), cap, h, False)


# 주고받는 내용. 묶음이 있어야 01(묶음의 첫 말)과 02(이어지는 말)가 둘 다 나온다.
# 입력창 위부터 거꾸로 쌓으므로 화면이 늘 꽉 찬다 — 위로 넘친 말은 머리 단추 밑으로 간다.
CHAT = [
    ('them', '안녕! 오랜만이야'),
    ('them', '요즘 뭐 하고 지내?'),
    ('me', '카톡 테마 만들고 있어'),
    ('me', '주말마다 조금씩'),
    ('them', '오 나도 보여줘'),
    ('me', '링크 보낼게'),
    ('me', '골라서 깔면 돼'),
    ('me', '배경이랑 글로우 따로 있어'),
    ('them', '말풍선 색 예쁘다'),
    ('them', '이걸로 바꿔야지'),
    ('me', 'ㅋㅋ 고마워'),
]


def chat(t):
    """채팅방. 카톡이 말풍선을 잡는 방식 그대로 그린다.

    - 묶음의 첫 말풍선은 01, 이어지는 말은 02 다(`-ios-group-background-image`).
      기존 테마는 둘이 다른 색이라 주고받는 묶음이 있으면 네 칸이 다 나온다.
      알록달록한 테마는 여기서 드러난다.
    - 프레임 = 글자 + edgeinsets 이고, 말풍선 그림은 그 프레임을 통째로 채운다.
      글로우 여백이 프레임 안에 들어가므로 몸통이 안으로 밀리고 말풍선 사이도 벌어진다.
      미리보기만 이상적으로 그리면 폰에서만 생기는 문제를 못 잡는다.
    - 간격은 폰 화면을 잰 값이다 — 묶음 안 6pt, 묶음 사이 12pt, 시각은 프레임 옆 4pt.
    """
    img = backdrop(t, t['chat_bg'], t['bg_deep'])
    d = ImageDraw.Draw(img)
    sheets = {}

    rows = []
    for i, (who, msg) in enumerate(CHAT):
        side = 'recv' if who == 'them' else 'send'
        first = i == 0 or CHAT[i - 1][0] != who
        last = i == len(CHAT) - 1 or CHAT[i + 1][0] != who
        k = (side, '01' if first else '02')
        if k not in sheets:
            sheets[k] = bubble_sheet(t, *k)
        sheet, geo = sheets[k]
        top, left, bottom, right = geo['ins']
        fw = text_w(msg, MSG_PT) + left + right
        fh = LINE_H + top + bottom
        head = 20 if side == 'recv' and first else 0
        gap = (12 if first else 6) if i else 0
        rows.append((side, msg, last, sheet, geo, fw, fh, head, gap))

    bar_top = PH - BAR_B - BAR_H
    y = bar_top - 12 - sum(r[6] + r[7] + r[8] for r in rows)
    unread = max(i for i, r in enumerate(rows) if r[0] == 'send')
    for i, (side, msg, last, sheet, geo, fw, fh, head, gap) in enumerate(rows):
        y += gap
        if head:
            avatar(img, t, i, 10, y, 36)
            text(d, 54, y + 1, '아무개1', 12.5, rgb(t['subtext']), anchor='lt')
        fy = y + head
        fx = 53 - geo['outer'] if side == 'recv' else PW - 12 + geo['outer'] - fw
        b = stretch(sheet, u(geo['cap']), u(fw), u(fh))
        img.paste(b, (u(fx), u(fy)), b)

        top, left = geo['ins'][:2]
        tc = rgb(t['recv_text'] if side == 'recv' else t['send_text'])
        text(d, fx + left, fy + top + LINE_H / 2, msg, MSG_PT, tc, anchor='lm')
        if last:
            base = fy + fh - geo['bottom'] - 1
            tx, an = (fx + fw + 4, 'ls') if side == 'recv' else (fx - 4, 'rs')
            text(d, tx, base, '오후 9:41', 11, rgb(t['subtext']), anchor=an)
            if i == unread:
                text(d, tx, base - 14, '1', 11, rgb(t['accent']), 600, an)
        y = fy + fh

    img = edge_fade(img, t)
    glass(img, (16, NAV_Y - 22, 92, NAV_Y + 22), t)
    glass(img, (PW - 112, NAV_Y - 22, PW - 16, NAV_Y + 22), t)
    d = ImageDraw.Draw(img)
    g = glyph(t)
    ic_back(d, 35, NAV_Y, g)
    text(d, 50, NAV_Y, '12', 17, g, 500, 'lm')
    text(d, PW / 2, NAV_Y, '아무개1', 17, rgb(t['text']), 600, 'mm')
    ic_search(d, PW - 83, NAV_Y, g)
    ic_menu(d, PW - 45, NAV_Y, g)

    top = PH - BAR_B - BAR_H
    glass(img, (10, top, PW - 10, top + BAR_H), t)
    cy = top + BAR_H / 2
    for x in (35, PW - 70, PW - 35):
        c = img.getpixel((u(x), u(cy)))
        k = 0.5 if light(t) else 0.10
        d.ellipse([u(x - 17), u(cy - 17), u(x + 17), u(cy + 17)],
                  fill=tuple(int(v + (255 - v) * k) for v in c))
    ic_plus(d, 35, cy, g)
    text(d, 62, cy, '메시지 입력', 15, rgb(t['subtext']), anchor='lm')
    ic_smile(d, PW - 70, cy, g)
    text(d, PW - 35, cy, '#', 20, g, 500, 'mm')

    status_bar(img, t)
    home_bar(img, t)
    return img


ROWS = [
    ('아무개1', 'ㅋㅋ 고마워', '오후 9:41', 0),
    ('아무개2', '내일 몇 시에 볼까?', '오후 8:20', 2),
    ('아무개3', '사진 보냈어 확인해줘', '오후 6:05', 0),
    ('주말 모임', '장소 정했어?', '오후 3:12', 14),
    ('아무개4', 'ㅋㅋㅋㅋㅋㅋ', '어제', 0),
    ('아무개5', '고마워!', '어제', 1),
    ('아무개6', '다음에 또 보자', '9월 10일', 0),
    ('아무개7', '파일 받았어', '9월 9일', 0),
]
CHIPS = ('전체', '안읽음', '친구', '오픈채팅')
ROW_H, HEAD_B, TAB_H = 76, 152, 84


def chat_list(t):
    """채팅 목록. 목록 쪽 색과 눌린 줄이 여기서 드러난다.

    main_bg 가 있으면 배경을 깔고 셀을 cell_alpha 만큼 투명하게 얹는다.
    실제 테마에서 -ios-normal-background-alpha 가 하는 일과 같다.
    """
    ca = t.get('cell_alpha', 1.0)
    base = backdrop(t, t.get('main_bg'), t['bg'], flat=True).convert('RGBA')

    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    a = int(255 * ca)
    ld.rectangle([0, 0, W, u(HEAD_B)], fill=rgb(t['bg']) + (a,))
    for i in range(len(ROWS)):
        y = HEAD_B + i * ROW_H
        if y >= PH - TAB_H:
            break
        ld.rectangle([0, u(y), W, u(y + ROW_H)],
                     fill=rgb(t['pressed'] if i == 1 else t['bg']) + (a,))
    ld.rectangle([0, u(PH - TAB_H), W, H], fill=rgb(t['bg']) + (a,))
    img = Image.alpha_composite(base, layer).convert('RGB')
    d = ImageDraw.Draw(img)

    text(d, 20, NAV_Y, '채팅', 24, rgb(t['text']), 700, 'lm')
    ic_search(d, PW - 104, NAV_Y, rgb(t['text']))
    ic_plus(d, PW - 66, NAV_Y, rgb(t['text']), 9)
    ic_menu(d, PW - 28, NAV_Y, rgb(t['text']))

    x = 16
    for i, chip in enumerate(CHIPS):
        w = text_w(chip, 14, 500) + 26
        sel = i == 0
        d.rounded_rectangle([u(x), u(112), u(x + w), u(142)], radius=u(15),
                            fill=rgb(t['text'] if sel else t['surface']))
        text(d, x + w / 2, 127, chip, 14, rgb(t['bg'] if sel else t['text']), 500, 'mm')
        x += w + 8

    for i, (name, msg, when, unread) in enumerate(ROWS):
        y = HEAD_B + i * ROW_H
        if y + ROW_H > PH - TAB_H:
            break
        avatar(img, t, i, 16, y + 13, 50)
        text(d, 78, y + 28, name, 16, rgb(t['text']), 600, 'lm')
        text(d, 78, y + 50, msg, 14, rgb(t['subtext']), anchor='lm')
        text(d, PW - 16, y + 28, when, 12, rgb(t['subtext']), anchor='rm')
        if unread:
            s = str(unread)
            w = max(20, text_w(s, 12, 600) + 12)
            d.rounded_rectangle([u(PW - 16 - w), u(y + 40), u(PW - 16), u(y + 60)],
                                radius=u(10), fill=rgb(t['accent']))
            text(d, PW - 16 - w / 2, y + 50, s, 12, rgb(t['on_accent']), 600, 'mm')

    d.line([(0, u(PH - TAB_H)), (W, u(PH - TAB_H))], fill=rgb(t['border']), width=S // 2 + 1)
    # 실제 테마에 들어가는 @3x 아이콘을 그대로 쓴다. 미리보기만 다른 그림을 쓰면
    # 폰에서 어떻게 보일지 알 수 없다.
    tabs = [('친구', 'friends'), ('채팅', 'chats'), ('오픈채팅', 'browse'),
            ('쇼핑', 'shopping'), ('더보기', 'more')]
    for i, (label, kind) in enumerate(tabs):
        cx = PW * (i + 0.5) / len(tabs)
        c = t['accent'] if i == 1 else t['subtext']
        ic = gen.tab_icon(kind, u(28), c)
        img.paste(ic, (u(cx - 14), u(PH - TAB_H + 9)), ic)
        text(d, cx, PH - TAB_H + 48, label, 10.5, rgb(c), 500, 'mm')

    status_bar(img, t)
    home_bar(img, t)
    return img


def splash(t):
    """안드로이드 실행화면. iOS 규격에는 이 블록이 없다."""
    img = gen.splash(t, W, H).convert('RGB')
    d = ImageDraw.Draw(img)
    text(d, PW / 2, PH * 0.42, '카카오톡', 26, rgb(t['text']), 700, 'mm')
    text(d, PW / 2, PH - 60, t['name'], 13, rgb(t['subtext']), anchor='mm')
    return img


def passcode(t):
    """잠금화면. 카톡 비밀번호를 걸어야 보이는 화면이다.

    동그라미와 키패드 눌림은 테마가 넣는 @3x 그림을 그대로 붙인다 — 미리보기가
    따로 그리면 폰에서만 다르게 보이는 것을 못 잡는다.
    """
    img = backdrop(t, t.get('passcode_bg'), t['bg_deep'])
    d = ImageDraw.Draw(img)
    text(d, PW / 2, 236, '비밀번호 입력', 18, rgb(t['text']), 500, 'mm')

    # 입력 점 네 개. 앞의 둘은 채워진 상태. 자리마다 색이 다르다
    img = img.convert('RGBA')
    for i in range(4):
        cx = PW / 2 + (i - 1.5) * 30
        dot = gen.bullet_image(t, i, u(18), checked=i < 2)
        img.alpha_composite(dot, (u(cx) - dot.width // 2, u(286) - dot.height // 2))
    img = img.convert('RGB')
    d = ImageDraw.Draw(img)

    keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '']
    kr = 64 * 0.46                       # keypad_pressed 가 64pt 판에 그리는 동그라미
    for i, k in enumerate(keys):
        if not k:
            continue
        cx = PW / 2 + (i % 3 - 1) * 100
        cy = 468 + (i // 3) * 90
        if k == '5':                                          # 하나는 눌린 상태
            press = gen.keypad_pressed(t, u(64))
            img.paste(press, (u(cx) - press.width // 2, u(cy) - press.height // 2), press)
        else:
            d.ellipse([u(cx - kr), u(cy - kr), u(cx + kr), u(cy + kr)],
                      fill=rgb(t['surface']))
        text(d, cx, cy, k, 30, rgb(t['accent'] if k == '5' else t['text']), 300, 'mm')

    status_bar(img, t)
    home_bar(img, t)
    return img


def shrink(img):
    return img.resize((round(PW * OUT), round(PH * OUT)), Image.LANCZOS)


def _render(t):
    """테마 하나의 그림을 전부 그린다. 여러 프로세스에 나눠 부른다."""
    import themes as T2
    # 그림 이름도 배포 파일과 같은 이름을 쓴다. 키(midnight38)는 겉으로 안 드러나는
    # 번호라 README 에서 어느 변형인지 읽히지 않는다.
    slug = T2.file_slug(t)
    gen.icon(t, 128).save(os.path.join(gen.ASSETS, 'icon-%s.png' % slug), optimize=True)
    for kind, draw in (('list', chat_list), ('chat', chat),
                       ('passcode', passcode), ('splash', splash)):
        shrink(draw(t)).save(os.path.join(gen.ASSETS, 'preview-%s-%s.png' % (slug, kind)),
                             optimize=True)
    return slug


SHOTS = (('list', '채팅 목록'), ('chat', '채팅방'),
         ('passcode', '잠금화면'), ('splash', '실행화면'))

PAGE = """<!doctype html>
<html lang="ko"><meta charset="utf-8">
<title>카카오톡 테마 미리보기</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body { margin:0; padding:32px; background:#0f1115; color:#e6e9ee;
         font:14px/1.6 -apple-system,'Segoe UI','Malgun Gothic',sans-serif; }
  h1 { font-size:20px; margin:0 0 4px; }
  .note { color:#8b95a3; margin:0 0 28px; }
  .card { border:1px solid #232833; border-radius:14px; padding:20px 20px 16px;
          margin-bottom:22px; background:#151922; }
  h2 { font-size:17px; margin:0 0 10px; }
  .cat { font-size:13px; letter-spacing:.14em; color:#8b95a3; margin:30px 0 12px;
        border-top:1px solid #232833; padding-top:18px; }
  .cat:first-of-type { margin-top:0; border-top:0; padding-top:0; }
  .cat b { color:#e6e9ee; letter-spacing:0; font-size:15px; margin-right:10px; }
  h2 small { color:#8b95a3; font-weight:400; font-size:13px; margin-left:8px; }
  .chips { margin-bottom:14px; }
  .chip { display:inline-block; width:26px; height:26px; border-radius:7px;
          border:1px solid #2b3140; margin-right:6px; vertical-align:middle; }
  .shots { display:flex; gap:16px; flex-wrap:wrap; }
  figure { margin:0; }
  figure img { width:230px; border-radius:12px; border:1px solid #2b3140; display:block; }
  figcaption { color:#8b95a3; font-size:12px; margin-top:6px; text-align:center; }
  .dl { margin:14px 0 0; color:#8b95a3; }
  .dl a { color:#4FD1B0; text-decoration:none; }
  .dl a:hover { text-decoration:underline; }
</style>
<h1>카카오톡 테마 미리보기</h1>
<p class="note">python tools/gen.py 가 만든다. 팔레트를 고치고 다시 돌리면 이 페이지도 갱신된다.<br>
실행화면은 안드로이드에만 있는 화면이다. iOS 테마 규격에는 스플래시 블록이 없다.<br>
아래 다운로드 링크는 build.ps1 을 돌린 뒤에만 동작한다.</p>
%s
</html>
"""

CARD = """<section class="card">
  <h2>%(name)s <small>%(key)s</small></h2>
  <div class="chips">%(chips)s</div>
  <div class="shots">%(shots)s</div>
  <p class="dl"><a href="../dist/iOS/%(slug)s.ktheme">iOS .ktheme</a> &middot;
     <a href="../dist/android/%(slug)s.apk">Android .apk</a></p>
</section>"""


# --- README 테마 목록 ----------------------------------------------------
# README 의 마커 사이를 여기서 채운다. 테마를 추가할 때 README 를 따로 손보지 않으려는 것.
# 썸네일을 누르면 해당 테마 자리로 스크롤한다. 앵커는 테마 이름에서 만든다.

START = '<!-- THEMES:START -->'
END = '<!-- THEMES:END -->'
BASE = 'https://github.com/Ruminem/kakaotalk-theme/releases/latest/download/'

# iOS 링크는 Pages 의 공유 페이지를 거친다. 브라우저마다 제일 짧은 길이 달라서,
# 그 페이지가 보고 고른다.
#
# 카카오톡 인앱 브라우저에서는 `files/` 의 파일 주소를 주기만 하면 카톡이 그대로 가로채
# 바로 설치한다. 릴리스 자산으로는 안 되는 일이다 — 거긴 `Content-Disposition: attachment`
# 가 붙어 나와서 브라우저가 내려받는 것 말고 아무것도 못 한다. 사이트의 같은 파일에는
# 그 헤더가 없다. 사파리는 같은 주소를 줘도 그냥 내려받아서, 거기선 공유 시트를 띄운다.
#
# 안드로이드는 그대로 BASE 다. APK 는 카톡이 아니라 시스템이 설치하고,
# 크롬의 공유 API 는 확장자 허용목록이라 .apk 를 받지도 않는다.
IOS = 'https://ruminem.github.io/kakaotalk-theme/docs/share.html?f='

# --- 배치 규칙 (폰에서 보는 것을 기준으로 잡은 값) ---------------------------
# GitHub 은 넓은 표를 가로 스크롤 상자에 넣는다. 칸이 넷을 넘거나 그림이 크면
# 폰에서 옆으로 한참 밀어야 다 본다. 셋과 200px 이 한 화면에 들어오는 한계다.
PER_ROW = 3          # 맨 위 계열 격자. 한 줄에 세 칸
VARIANT_MAX_N = 4    # 한 계열의 변형 수 상한. 넷이면 2x2 로 접는다
W_GRID = 190         # 맨 위 계열 격자 그림 폭
W_VARIANT = 200      # 계열 안 변형 그림 폭
W_DETAIL = 180       # 접어둔 화면 그림 폭
NOTE_MAX = 45        # 한 줄 소개. 길면 표 칸이 세로로 늘어나 폰에서 들쭉날쭉해진다
VARIANT_MAX = 8      # 변형 이름. 길면 칸 안에서 줄바꿈된다
CAT_NOTE_MAX = 20    # 분류 설명. 분류 이름과 한 줄에 들어가야 한다


def _check(fams):
    """배치가 무너질 값을 미리 막는다. 규칙을 글로만 두면 다음에 잊는다."""
    for name, members in fams:
        for m in members:
            if len(m['note']) > NOTE_MAX:
                raise ValueError('%s: 한 줄 소개가 %d자다. %d자 넘으면 폰에서 표가 '
                                 '들쭉날쭉해진다' % (m['key'], len(m['note']), NOTE_MAX))
            if len(m['variant']) > VARIANT_MAX:
                raise ValueError('%s: 변형 이름이 %d자다. %d자 넘으면 칸 안에서 줄바꿈된다'
                                 % (m['key'], len(m['variant']), VARIANT_MAX))
        if len(members) > VARIANT_MAX_N:
            raise ValueError('%s 계열에 변형이 %d개다. %d개까지만 둔다 — 그 이상은 '
                             '폰에서 한 계열로 안 보인다'
                             % (name, len(members), VARIANT_MAX_N))


def _check_cats(cats):
    """분류 줄이 한 줄에 들어가는지."""
    for name, note, _ in cats:
        if len(note) > CAT_NOTE_MAX:
            raise ValueError('%s 분류 설명이 %d자다. %d자 넘으면 폰에서 두 줄이 된다'
                             % (name, len(note), CAT_NOTE_MAX))


def _pad(cells):
    """짧은 줄을 빈 칸으로 채워 늘 세 칸으로 만든다.

    `width="33%"` 는 그 표 안에서만 33% 다. 계열이 둘뿐인 분류는 표가 두 칸짜리가
    되어 칸이 반반으로 벌어지고, 그림이 분류마다 다른 자리에 놓인다.
    지금은 분류가 6/3/6 이라 안 드러나지만 계열 하나만 더해도 드러난다.
    """
    cells = list(cells)
    return cells + ['<td width="33%"></td>'] * (PER_ROW - len(cells))


def slug(name):
    """앵커 이름. 소문자로 바꾸고 공백을 하이픈으로."""
    return name.strip().lower().replace(' ', '-')


def anchor(name):
    """그 계열 자리로 뛰는 링크.

    GitHub 은 문서 안의 id 앞에 `user-content-` 를 붙여 놓고, 링크를 누르면
    자바스크립트가 그 접두사를 붙여 찾아간다. 그 스크립트가 안 도는 자리가 있다 —
    모바일 브라우저와 GitHub 앱. 거기서는 `#먹빛-민트` 를 눌러도 아무 일도 안 난다.
    그래서 처음부터 진짜 id 를 가리킨다. 브라우저가 알아서 찾아가므로 어디서나 같다.
    """
    return '#user-content-' + slug(name)


def readme_block(ts):
    """README 의 테마 절.

    계열 단위로 나열하고, 계열을 다시 분류로 묶는다. 변형이 늘어날 때 목록이
    같이 길어지면 훑어보기가 안 된다 — 계열 수는 고정되고 변형은 계열 안에서
    옆으로 늘어난다. 계열이 열다섯을 넘으면서 그 계열 목록도 한 덩어리로는
    길어져서, 배경 그림이 무엇을 그리는지로 한 겹 더 묶었다.

    개요 격자는 위에 몰아 두고 상세는 그 아래로 내린다. 분류마다 격자와 상세를
    번갈아 놓으면 전체를 한눈에 볼 수 없다 — 둘째 분류를 보려면 첫째 분류의
    상세 여섯 개를 지나쳐야 한다.
    """
    import themes as T
    cats = T.categorized()
    fams = [fm for _, _, ms in cats for fm in ms]
    _check(fams)
    _check_cats(cats)
    out = [START, '']

    # 분류마다 계열 썸네일 격자 하나
    for name, note, members in cats:
        out.append('**[%s](%s)** — %s' % (name, anchor(name), note))
        out.append('')
        out.append('<table>')
        for i in range(0, len(members), PER_ROW):
            row = members[i:i + PER_ROW]
            out.append('<tr>')
            out.extend(_pad(
                '<td width="33%%" align="center"><a href="%s">'
                '<img src="assets/preview-%s-chat.png" width="%d"></a></td>'
                % (anchor(fam), T.file_slug(ms[0]), W_GRID)
                for fam, ms in row))
            out.append('</tr>')
            out.append('<tr>')
            out.extend(_pad(
                '<td align="center"><img src="assets/icon-%s.png" width="20" '
                'valign="middle"> <b><a href="%s">%s</a></b>%s<br>%s</td>'
                % (T.file_slug(ms[0]), anchor(fam), fam,
                   ('' if len(ms) == 1 else '<br><sub>%s</sub>'
                    % ' · '.join(m['variant'] for m in ms)),
                   ms[0]['note'])
                for fam, ms in row))
            out.append('</tr>')
        out.append('</table>')
        out.append('')

    # 분류별 상세. 분류가 제목이고 계열이 그 아래다 — 깃허브가 문서 목차를
    # 그 층으로 접어준다.
    for cat, _, members in cats:
        out.append('<a name="%s"></a>' % slug(cat))
        out.append('')
        out.append('### %s' % cat)
        out.append('')
        for name, ms in members:
            out.extend(_family_block(T, name, ms))

    out.append(END)
    return '\n'.join(out)


def _family_block(T, name, members):
    """계열 하나의 상세. 변형 표와 접어둔 화면들."""
    out = ['<a name="%s"></a>' % slug(name), '']
    out.append('#### <img src="assets/icon-%s.png" width="26" valign="middle"> %s'
               % (T.file_slug(members[0]), name))
    out.append('')

    # 변형 배치. 넷이면 2x2 로 접는다 — 한 줄에 넷을 놓으면 폰에서 옆으로 밀어야 한다.
    # 계열 안에서는 표 하나에 갇혀 있으므로 두 줄이어도 한 묶음으로 읽힌다.
    per = 2 if len(members) == 4 else min(len(members), PER_ROW)
    cell = 100 // per
    out.append('<table>')
    for i in range(0, len(members), per):
        out.append('<tr>')
        for m in members[i:i + per]:
            out.append('<td width="%d%%" align="center">'
                       '<img src="assets/preview-%s-chat.png" width="%d"><br>'
                       '<b>%s</b><br><sub>%s</sub><br>'
                       '<a href="%s%s.ktheme">iOS</a> · <a href="%s%s.apk">Android</a>'
                       '</td>'
                       % (cell, T.file_slug(m), W_VARIANT, m['variant'], m['note'],
                          IOS, T.file_slug(m), BASE, T.file_slug(m)))
        out.append('</tr>')
    out.append('</table>')
    out.append('')

    out.append('<details><summary>화면 더 보기 (목록 · 잠금화면 · 실행화면)</summary>')
    out.append('')
    for m in members:
        out.append('**%s** — %s' % (m['variant'], m['note']))
        out.append('')
        out.append(' '.join(
            '<img src="assets/preview-%s-%s.png" width="%d">' % (T.file_slug(m), kind, W_DETAIL)
            for kind, _ in SHOTS if kind != 'chat'))
        out.append('')
    out.append('</details>')
    out.append('')
    return out


def write_readme(ts):
    p = os.path.join(ROOT_DIR, 'README.md')
    if not os.path.exists(p):
        return
    s = open(p, encoding='utf-8').read()
    if START not in s or END not in s:
        print('README 에 마커가 없어 건너뜀')
        return
    head, rest = s.split(START, 1)
    _, tail = rest.split(END, 1)
    open(p, 'w', encoding='utf-8', newline='\n').write(head + readme_block(ts) + tail)


def generate(ts):
    os.makedirs(gen.ASSETS, exist_ok=True)
    import themes as T2
    cards = {}
    # 3배로 그리면서 테마 하나에 1초를 넘게 됐다. 빌드처럼 여러 프로세스에 나눈다.
    with multiprocessing.Pool(gen.workers()) as pool:
        slugs = pool.map(_render, ts)
    for t, slug in zip(ts, slugs):
        chips = ''.join('<span class="chip" style="background:%s" title="%s"></span>'
                        % (t[k], k) for k in ('bg', 'bg_deep', 'surface', 'accent', 'text'))
        shots = ''.join('<figure><img src="../assets/preview-%s-%s.png" alt="%s %s">'
                        '<figcaption>%s</figcaption></figure>'
                        % (slug, kind, t['name'], label, label) for kind, label in SHOTS)
        cards[t['key']] = CARD % dict(name=t['name'], key=t['key'],
                                      slug=slug, chips=chips, shots=shots)

    # 갤러리도 README 와 같은 순서로 둔다. 두 곳을 다른 순서로 두면 README 에서
    # 본 것을 갤러리에서 다시 찾아야 한다.
    body = []
    for cat, note, members in T2.categorized():
        body.append('<p class="cat"><b>%s</b>%s</p>' % (cat, note))
        for _, ms in members:
            body.extend(cards.pop(m['key']) for m in ms if m['key'] in cards)
    body.extend(cards.values())      # 분류 밖의 테마가 있으면 뒤에 붙인다

    with open(os.path.join(gen.DOCS, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(PAGE % '\n'.join(body))
    write_readme(ts)

if __name__ == '__main__':
    import themes
    generate(themes.THEMES)
    print('미리보기 -> docs/index.html')
