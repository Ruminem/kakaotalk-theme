# -*- coding: utf-8 -*-
"""테마 미리보기 그림과 갤러리 페이지를 만든다.

gen.py 가 부른다. 직접 돌려도 된다:

    python tools/preview.py

하나씩 폰에 적용해보지 않고 색을 확인하려고 만든 것이다.
화면 세 장을 그린다 — 채팅 목록, 채팅방, 실행화면.
실행화면은 안드로이드에만 있는 화면이지만 색 확인용으로 같이 그린다.

말풍선은 9-slice 로 늘리지 않고 필요한 크기로 직접 그린다. 늘리는 방식은
목표 크기가 고정 가장자리(cap)의 두 배보다 작아지면 모서리가 겹쳐 깨진다.
어차피 둥근 사각형이라 어떤 크기로든 정확히 그릴 수 있다.
"""
import os
import sys

# 윈도우 파이썬은 기본 출력 인코딩이 cp949 라 한글이 깨진다.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen  # noqa: E402

rgb = gen.rgb
W, H = 460, 820
HEAD, FOOT = 96, 100
RADIUS = 15          # 말풍선 모서리. 실제 PNG 의 cap inset 과 같은 느낌으로 맞춘다
SS = 4               # 계단현상을 없애려고 이 배율로 그렸다 줄인다


def _font(size, bold=False):
    """맑은 고딕. 없으면 기본 폰트로 떨어진다(한글은 깨지지만 그림은 나온다)."""
    for name in (('malgunbd.ttf', 'malgun.ttf') if bold else ('malgun.ttf',)):
        for base in (r'C:\Windows\Fonts', '/usr/share/fonts/truetype/nanum'):
            p = os.path.join(base, name)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F_TITLE = _font(19, bold=True)
F_NAME = _font(14)
F_MSG = _font(16)
F_TIME = _font(11)
F_LIST_NAME = _font(16, bold=True)
F_LIST_MSG = _font(13)
F_TAB = _font(11)
F_ICON = _font(20)

# 주고받는 내용. 색을 보려고 만든 그림이라 내용은 최소한으로 둔다.
CHAT = [
    ('them', '안녕! 오랜만이야'),
    ('me', '오 아무개1 반갑다'),
    ('them', '테마 새로 만들었다며?'),
    ('me', '응 여섯 개 나왔어'),
]


def _text_w(d, s, font):
    return d.textbbox((0, 0), s, font=font)[2]


def _round(d, box, r, fill):
    d.rounded_rectangle(box, radius=r, fill=fill)


def bubble_box(w, h, colors, radius=RADIUS):
    """말풍선 하나를 정확히 w x h 로 그린다. 세로 그라데이션."""
    mask = Image.new('L', (w * SS, h * SS), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, w * SS - 1, h * SS - 1], radius=radius * SS, fill=255)
    mask = mask.resize((w, h), Image.LANCZOS)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.paste(gen.vgradient(w, h, rgb(colors[0]), rgb(colors[1])), (0, 0), mask)
    return out


def avatar(size, t, i):
    """프로필. 카톡은 둥근 사각형이다."""
    img = Image.new('RGBA', (size * SS, size * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size * SS - 1, size * SS - 1],
                        radius=int(size * SS * 0.32), fill=rgb(t['surface']))
    c = rgb(t['accent'] if i % 2 == 0 else t['subtext'])
    r = size * SS
    d.ellipse([r * 0.32, r * 0.20, r * 0.68, r * 0.56], fill=c)          # 머리
    d.ellipse([r * 0.16, r * 0.58, r * 0.84, r * 1.30], fill=c)          # 몸
    return img.resize((size, size), Image.LANCZOS)


# --- 아이콘 --------------------------------------------------------------
# 글꼴 글리프(⌕ ☰ 같은 것)를 쓰면 맑은 고딕에 없는 문자가 네모로 나온다.
# 필요한 것만 도형으로 직접 그린다.

def ic_search(d, cx, cy, c, r=9):
    d.ellipse([cx - r, cy - r, cx + r - 3, cy + r - 3], outline=c, width=2)
    d.line([(cx + r - 5, cy + r - 5), (cx + r + 2, cy + r + 2)], fill=c, width=2)


def ic_menu(d, cx, cy, c, w=18):
    for k in (-6, 0, 6):
        d.line([(cx - w // 2, cy + k), (cx + w // 2, cy + k)], fill=c, width=2)


def ic_plus(d, cx, cy, c, r=9):
    d.line([(cx - r, cy), (cx + r, cy)], fill=c, width=2)
    d.line([(cx, cy - r), (cx, cy + r)], fill=c, width=2)


def ic_send(d, cx, cy, c, r=8):
    d.line([(cx, cy + r), (cx, cy - r)], fill=c, width=2)
    d.line([(cx - r + 2, cy - r + 6), (cx, cy - r)], fill=c, width=2)
    d.line([(cx + r - 2, cy - r + 6), (cx, cy - r)], fill=c, width=2)


def ic_person(d, cx, cy, c):
    d.ellipse([cx - 6, cy - 10, cx + 6, cy + 2], fill=c)
    d.pieslice([cx - 11, cy - 2, cx + 11, cy + 18], 180, 360, fill=c)


def ic_bubble(d, cx, cy, c):
    d.rounded_rectangle([cx - 11, cy - 9, cx + 11, cy + 6], radius=5, fill=c)
    d.polygon([(cx - 5, cy + 5), (cx - 1, cy + 5), (cx - 5, cy + 11)], fill=c)


def ic_circle(d, cx, cy, c):
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], outline=c, width=2)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=c)


def ic_bag(d, cx, cy, c):
    d.rounded_rectangle([cx - 9, cy - 4, cx + 9, cy + 10], radius=3, fill=c)
    d.arc([cx - 6, cy - 12, cx + 6, cy + 2], 180, 360, fill=c, width=2)


def ic_dots(d, cx, cy, c):
    for k in (-8, 0, 8):
        d.ellipse([cx + k - 2, cy - 2, cx + k + 2, cy + 2], fill=c)


def _header(img, t, title, back=False):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, HEAD], fill=rgb(t['bg']))
    x = 22
    if back:
        d.text((x, 46), '‹', font=_font(30), fill=rgb(t['text']), anchor='lm')
        x += 26
    d.text((x, 47), title, font=F_TITLE, fill=rgb(t['text']), anchor='lm')
    ic_search(d, W - 74, 47, rgb(t['subtext']))
    ic_menu(d, W - 32, 47, rgb(t['subtext']))
    d.line([(0, HEAD - 1), (W, HEAD - 1)], fill=rgb(t['border']))


def chat(t):
    """채팅방. 말풍선 네 칸을 모두 보여준다 — 알록달록한 테마는 여기서 드러난다."""
    img = Image.new('RGB', (W, H), rgb(t['bg']))
    body = H - HEAD - FOOT
    if t['chat_bg']:
        img.paste(gen.chat_bg(t['chat_bg'], W, body), (0, HEAD))
    else:
        img.paste(Image.new('RGB', (W, body), rgb(t['bg_deep'])), (0, HEAD))
    _header(img, t, '아무개1', back=True)
    d = ImageDraw.Draw(img)

    pad_x, pad_y = 14, 10
    y = HEAD + 18
    for i, (side, msg) in enumerate(CHAT):
        # 짝수/홀수로 01 과 02 를 번갈아 쓴다. 두 칸의 색 차이가 눈에 보이게
        key = ('recv' if side == 'them' else 'send') + ('' if i % 4 < 2 else '_alt')
        colors = t[key]
        tc = rgb(t['recv_text'] if side == 'them' else t['send_text'])

        tw = _text_w(d, msg, F_MSG)
        bw, bh = tw + pad_x * 2, 26 + pad_y * 2

        if side == 'them':
            if i == 0 or CHAT[i - 1][0] != 'them':
                av = avatar(42, t, i)
                img.paste(av, (18, y), av)
                d.text((70, y + 2), '아무개1', font=F_NAME, fill=rgb(t['subtext']))
                y += 24
            bx = 70
            b = bubble_box(bw, bh, colors)
            img.paste(b, (bx, y), b)
            d.text((bx + pad_x, y + pad_y + 1), msg, font=F_MSG, fill=tc)
            d.text((bx + bw + 8, y + bh - 12), '오후 2:43',
                   font=F_TIME, fill=rgb(t['subtext']), anchor='lm')
        else:
            bx = W - 18 - bw
            b = bubble_box(bw, bh, colors)
            img.paste(b, (bx, y), b)
            d.text((bx + pad_x, y + pad_y + 1), msg, font=F_MSG, fill=tc)
            d.text((bx - 8, y + bh - 12), '오후 2:43',
                   font=F_TIME, fill=rgb(t['subtext']), anchor='rm')
            d.text((bx - 8, y + 12), '1', font=F_TIME, fill=rgb(t['accent']), anchor='rm')
        y += bh + 14

    # 입력바
    d.rectangle([0, H - FOOT, W, H], fill=rgb(t['surface']))
    ic_plus(d, 32, H - FOOT + 48, rgb(t['subtext']))
    _round(d, [54, H - FOOT + 26, W - 84, H - FOOT + 70], 22, rgb(t['pressed']))
    d.text((70, H - FOOT + 48), '메시지 입력', font=F_LIST_MSG,
           fill=rgb(t['subtext']), anchor='lm')
    d.ellipse([W - 74, H - FOOT + 26, W - 30, H - FOOT + 70], fill=rgb(t['accent']))
    ic_send(d, W - 52, H - FOOT + 48, rgb(t['on_accent']))
    return img


ROWS = [
    ('아무개1', '응 여섯 개 나왔어', '오후 2:43', 0),
    ('아무개2', '내일 몇 시에 볼까?', '오후 1:20', 2),
    ('아무개3', '사진 보냈어 확인해줘', '오전 11:05', 0),
    ('아무개4', 'ㅋㅋㅋㅋㅋㅋ', '어제', 0),
    ('아무개5', '고마워!', '어제', 1),
]


def chat_list(t):
    """채팅 목록. 목록 쪽 색과 눌린 줄이 여기서 드러난다."""
    img = Image.new('RGB', (W, H), rgb(t['bg']))
    _header(img, t, '채팅')
    d = ImageDraw.Draw(img)

    y = HEAD + 12
    d.text((22, y + 8), '채팅 5', font=F_LIST_MSG, fill=rgb(t['subtext']))
    y += 34

    for i, (name, msg, when, unread) in enumerate(ROWS):
        rh = 84
        if y + rh > H - FOOT:
            break
        d.rectangle([0, y, W, y + rh], fill=rgb(t['pressed'] if i == 1 else t['bg']))
        av = avatar(52, t, i)
        img.paste(av, (22, y + 16), av)
        d.text((90, y + 22), name, font=F_LIST_NAME, fill=rgb(t['text']))
        d.text((90, y + 48), msg, font=F_LIST_MSG, fill=rgb(t['subtext']))
        d.text((W - 22, y + 26), when, font=F_TIME, fill=rgb(t['subtext']), anchor='rm')
        if unread:
            r = 11
            cx, cy = W - 34, y + 56
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb(t['accent']))
            d.text((cx, cy - 1), str(unread), font=F_TIME,
                   fill=rgb(t['on_accent']), anchor='mm')
        d.line([(90, y + rh - 1), (W, y + rh - 1)], fill=rgb(t['border']))
        y += rh

    # 탭바
    d.rectangle([0, H - FOOT, W, H], fill=rgb(t['bg']))
    d.line([(0, H - FOOT), (W, H - FOOT)], fill=rgb(t['border']))
    tabs = [('친구', ic_person), ('채팅', ic_bubble), ('오픈채팅', ic_circle),
            ('쇼핑', ic_bag), ('더보기', ic_dots)]
    for i, (label, icon) in enumerate(tabs):
        cx = int(W * (i + 0.5) / len(tabs))
        c = rgb(t['accent'] if i == 1 else t['subtext'])
        icon(d, cx, H - FOOT + 34, c)
        d.text((cx, H - FOOT + 64), label, font=F_TAB, fill=c, anchor='mm')
    return img


def splash(t):
    """안드로이드 실행화면. iOS 규격에는 이 블록이 없다."""
    img = gen.splash(t, W, H)
    d = ImageDraw.Draw(img)
    d.text((W // 2, int(H * 0.42)), '카카오톡', font=_font(26, bold=True),
           fill=rgb(t['text']), anchor='mm')
    d.text((W // 2, H - 60), t['name'], font=F_LIST_MSG,
           fill=rgb(t['subtext']), anchor='mm')
    return img


SHOTS = (('list', '채팅 목록'), ('chat', '채팅방'), ('splash', '실행화면'))

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
  <p class="dl"><a href="../dist/iOS/%(key)s.ktheme">iOS .ktheme</a> &middot;
     <a href="../dist/android/%(key)s.apk">Android .apk</a></p>
</section>"""


def generate(ts):
    os.makedirs(gen.DOCS, exist_ok=True)
    cards = []
    for t in ts:
        for kind, draw in (('list', chat_list), ('chat', chat), ('splash', splash)):
            draw(t).save(os.path.join(gen.DOCS, 'preview-%s-%s.png' % (t['key'], kind)),
                         optimize=True)
        chips = ''.join('<span class="chip" style="background:%s" title="%s"></span>'
                        % (t[k], k) for k in ('bg', 'bg_deep', 'surface', 'accent', 'text'))
        shots = ''.join('<figure><img src="preview-%s-%s.png" alt="%s %s">'
                        '<figcaption>%s</figcaption></figure>'
                        % (t['key'], kind, t['name'], label, label) for kind, label in SHOTS)
        cards.append(CARD % dict(name=t['name'], key=t['key'], chips=chips, shots=shots))
    with open(os.path.join(gen.DOCS, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(PAGE % '\n'.join(cards))


if __name__ == '__main__':
    import themes
    generate(themes.THEMES)
    print('미리보기 -> docs/index.html')
