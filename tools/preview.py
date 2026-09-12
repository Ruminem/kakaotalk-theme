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


def bubble_box(t, w, h, colors):
    """말풍선 하나. 유리 테마면 반투명에 테두리 하이라이트가 들어간다.

    9-slice 로 늘리지 않는다. 목표 크기가 고정 가장자리의 두 배보다 작아지면
    모서리가 겹쳐 깨진다. 어차피 둥근 사각형이라 필요한 크기로 바로 그리면 된다.
    """
    glow, pad = gen.glow_of(t)
    img = gen.bubble_box(w, h, colors, RADIUS, t.get('bubble_style', 'solid'),
                         t.get('bubble_alpha', 255), glow, pad, t.get('flat', False))
    return img, pad


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
        img.paste(gen.background(t, t['chat_bg'], W, body), (0, HEAD))
    else:
        img.paste(Image.new('RGB', (W, body), rgb(t['bg_deep'])), (0, HEAD))
    _header(img, t, '아무개1', back=True)
    d = ImageDraw.Draw(img)

    # 실제 테마의 edgeinsets 와 같은 값을 쓴다. 미리보기만 넉넉하면 폰에서 짜쳐 보인다
    # 카톡이 말풍선을 잡는 방식 그대로 그린다.
    #   프레임 = 글자 + edgeinsets, 말풍선 그림은 그 프레임을 통째로 채운다.
    #   글로우가 있으면 그림 바깥 여백이 프레임 안에 들어가므로 몸통이 안으로 밀리고,
    #   프레임 높이가 커진 만큼 말풍선 사이도 벌어진다.
    # 미리보기만 이상적으로 그리면 여기서 생기는 문제를 못 잡는다.
    glow, pad = gen.glow_of(t)
    ins_v, ins_h = gen.INSET_V + pad, gen.INSET_H + pad
    line_h = 22
    gap = 8                      # 카톡이 말풍선 사이에 두는 간격

    y = HEAD + 14
    for i, (side, msg) in enumerate(CHAT):
        key = ('recv' if side == 'them' else 'send') + ('' if i % 4 < 2 else '_alt')
        colors = t[key]
        tc = rgb(t['recv_text'] if side == 'them' else t['send_text'])

        fw = _text_w(d, msg, F_MSG) + ins_h * 2
        fh = line_h + ins_v * 2

        if side == 'them':
            if i == 0 or CHAT[i - 1][0] != 'them':
                av = avatar(42, t, i)
                img.paste(av, (18, y), av)
                d.text((70, y + 2), '아무개1', font=F_NAME, fill=rgb(t['subtext']))
                y += 24
            fx = 70 - pad        # 몸통 왼쪽이 아바타 옆에 오도록 여백만큼 당긴다
        else:
            fx = W - 18 + pad - fw

        b, _ = bubble_box(t, fw - pad * 2, fh - pad * 2, colors)
        img.paste(b, (fx, y), b)
        d.text((fx + ins_h, y + ins_v + 1), msg, font=F_MSG, fill=tc)

        if side == 'them':
            d.text((fx + fw - pad + 6, y + fh - pad - 8), '오후 2:43',
                   font=F_TIME, fill=rgb(t['subtext']), anchor='lm')
        else:
            d.text((fx + pad - 6, y + fh - pad - 8), '오후 2:43',
                   font=F_TIME, fill=rgb(t['subtext']), anchor='rm')
            d.text((fx + pad - 6, y + pad + 10), '1',
                   font=F_TIME, fill=rgb(t['accent']), anchor='rm')
        y += fh + gap

    # 입력바
    ca = t.get('cell_alpha', 1.0)
    bar = Image.new('RGBA', (W, FOOT), rgb(t['surface']) + (int(255 * ca),))
    img.paste(Image.alpha_composite(
        img.crop((0, H - FOOT, W, H)).convert('RGBA'), bar).convert('RGB'),
        (0, H - FOOT))
    d = ImageDraw.Draw(img)
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
    """채팅 목록. 목록 쪽 색과 눌린 줄이 여기서 드러난다.

    main_bg 가 있으면 배경을 깔고 셀을 cell_alpha 만큼 투명하게 얹는다.
    실제 테마에서 -ios-normal-background-alpha 가 하는 일과 같다.
    """
    ca = t.get('cell_alpha', 1.0)
    if t.get('main_bg'):
        base = gen.background(t, t['main_bg'], W, H).convert('RGBA')
    else:
        base = Image.new('RGBA', (W, H), rgb(t['bg']) + (255,))

    # 면은 알파를 먹여 따로 얹는다
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    a = int(255 * ca)
    ld.rectangle([0, 0, W, HEAD], fill=rgb(t['bg']) + (a,))
    y0 = HEAD + 46
    for i in range(6):
        y = y0 + i * 84
        if y + 84 > H - FOOT:
            break
        ld.rectangle([0, y, W, y + 84],
                     fill=rgb(t['pressed'] if i == 1 else t['bg']) + (a,))
    ld.rectangle([0, H - FOOT, W, H], fill=rgb(t['bg']) + (a,))
    img = Image.alpha_composite(base, layer).convert('RGB')

    d = ImageDraw.Draw(img)
    x = 22
    d.text((x, 47), '채팅', font=F_TITLE, fill=rgb(t['text']), anchor='lm')
    ic_search(d, W - 74, 47, rgb(t['subtext']))
    ic_menu(d, W - 32, 47, rgb(t['subtext']))
    d.line([(0, HEAD - 1), (W, HEAD - 1)], fill=rgb(t['border']))

    d.text((22, HEAD + 20), '채팅 5', font=F_LIST_MSG, fill=rgb(t['subtext']))
    d.line([(0, HEAD + 44), (W, HEAD + 44)], fill=rgb(t['border']))

    for i, (name, msg, when, unread) in enumerate(ROWS):
        y = y0 + i * 84
        if y + 84 > H - FOOT:
            break
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
        d.line([(90, y + 83), (W, y + 83)], fill=rgb(t['border']))

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


def passcode(t):
    """잠금화면. 카톡 비밀번호를 걸어야 보이는 화면이다.

    색은 모든 테마에 넣고 있었지만 한 번도 보여준 적이 없어서 여기 추가했다.
    동그라미와 키패드 눌림은 이미지로도 바꿀 수 있는데 아직 안 쓴다.
    """
    if t.get('passcode_bg'):
        img = gen.background(t, t['passcode_bg'], W, H).convert('RGB')
    else:
        img = Image.new('RGB', (W, H), rgb(t['bg_deep']))
    d = ImageDraw.Draw(img)

    d.text((W // 2, 150), '비밀번호 입력', font=_font(17),
           fill=rgb(t['text']), anchor='mm')

    # 입력 점 네 개. 앞의 둘은 채워진 상태
    for i in range(4):
        cx = W // 2 + (i - 1.5) * 34
        r = 8
        if i < 2:
            d.ellipse([cx - r, 208 - r, cx + r, 208 + r], fill=rgb(t['accent']))
        else:
            d.ellipse([cx - r, 208 - r, cx + r, 208 + r],
                      outline=rgb(t['subtext']), width=2)

    # 키패드
    keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '']
    top, kr = 300, 38
    for i, k in enumerate(keys):
        if not k:
            continue
        cx = W // 2 + (i % 3 - 1) * 110
        cy = top + (i // 3) * 104
        fill = t['pressed'] if k == '5' else t['surface']      # 하나는 눌린 상태
        d.ellipse([cx - kr, cy - kr, cx + kr, cy + kr], fill=rgb(fill))
        d.text((cx, cy), k, font=_font(26),
               fill=rgb(t['accent'] if k == '5' else t['text']), anchor='mm')
    return img


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


# --- README 테마 목록 ----------------------------------------------------
# README 의 마커 사이를 여기서 채운다. 테마를 추가할 때 README 를 따로 손보지 않으려는 것.
# 썸네일을 누르면 해당 테마 자리로 스크롤한다 — GitHub 은 제목 텍스트로 앵커를 만든다.

START = '<!-- THEMES:START -->'
END = '<!-- THEMES:END -->'
BASE = 'https://github.com/Ruminem/kakaotalk-theme/releases/latest/download/'
PER_ROW = 3


def anchor(name):
    """GitHub 이 제목에서 만드는 앵커. 소문자로 바꾸고 공백을 하이픈으로."""
    return '#' + name.strip().lower().replace(' ', '-')


def readme_block(ts):
    out = [START, '']

    # 썸네일 격자
    out.append('<table>')
    for i in range(0, len(ts), PER_ROW):
        row = ts[i:i + PER_ROW]
        out.append('<tr>')
        for t in row:
            out.append(
                '<td width="33%%" align="center"><a href="%s">'
                '<img src="docs/preview-%s-chat.png" width="190"></a></td>'
                % (anchor(t['name']), t['key']))
        out.append('</tr>')
        out.append('<tr>')
        for t in row:
            out.append('<td align="center"><b><a href="%s">%s</a></b><br>%s</td>'
                       % (anchor(t['name']), t['name'], t['note']))
        out.append('</tr>')
    out.append('</table>')
    out.append('')

    # 테마별 자세히
    for t in ts:
        # 받기 링크를 제목 줄에 같이 둔다. 다만 GitHub 은 제목 글자로 앵커를 만들기 때문에
        # 링크 글자까지 슬러그에 섞여 썸네일 점프가 깨진다. 앵커를 따로 박아 고정한다.
        out.append('<a name="%s"></a>' % anchor(t['name']).lstrip('#'))
        out.append('')
        out.append('### %s &nbsp; <sub>[iOS 받기](%s%s.ktheme) · '
                   '[Android 받기](%s%s.apk)</sub>'
                   % (t['name'], BASE, t['key'], BASE, t['key']))
        out.append('')
        out.append(' '.join(
            '<img src="docs/preview-%s-%s.png" width="200">' % (t['key'], kind)
            for kind, _ in SHOTS))
        out.append('')
        out.append(t['note'] + '.')
        out.append('')

    out.append(END)
    return '\n'.join(out)


def write_readme(ts):
    p = os.path.join(os.path.dirname(gen.DOCS), 'README.md')
    if not os.path.exists(p):
        return
    s = open(p, encoding='utf-8').read()
    if START not in s or END not in s:
        print('README 에 마커가 없어 건너뜀')
        return
    head, rest = s.split(START, 1)
    _, tail = rest.split(END, 1)
    open(p, 'w', encoding='utf-8').write(head + readme_block(ts) + tail)


def generate(ts):
    os.makedirs(gen.DOCS, exist_ok=True)
    cards = []
    for t in ts:
        for kind, draw in (('list', chat_list), ('chat', chat),
                           ('passcode', passcode), ('splash', splash)):
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
    write_readme(ts)


if __name__ == '__main__':
    import themes
    generate(themes.THEMES)
    print('미리보기 -> docs/index.html')
