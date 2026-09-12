# -*- coding: utf-8 -*-
"""테마 미리보기 그림과 갤러리 페이지를 만든다.

gen.py 가 부른다. 직접 돌려도 된다:

    python tools/preview.py

하나씩 폰에 적용해보지 않고 색을 확인하려고 만든 것이다.
화면 세 장을 그린다 — 목록, 채팅방, 실행화면.
실행화면은 안드로이드에만 있는 화면이지만 색 확인용으로 같이 그린다.

글자는 넣지 않는다. 폰트가 환경마다 다르고, 색만 보이면 목적은 달성된다.
"""
import os
import sys

# 윈도우 파이썬은 기본 출력 인코딩이 cp949 라 한글이 깨진다.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen  # noqa: E402

rgb = gen.rgb
W, H = 460, 820
HEAD, FOOT = 92, 96


def _round(d, box, r, fill):
    d.rounded_rectangle(box, radius=r, fill=fill)


def stretched(pal, w, h):
    """말풍선을 실제 크기로 늘린 그림. 9-slice 라서 모서리가 안 뭉개진다."""
    b = gen.bubble(3, pal)
    s = b.size[0]
    cap = gen.CAP * 3
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    src = [(0, 0, cap, cap), (cap, 0, s - cap, cap), (s - cap, 0, s, cap),
           (0, cap, cap, s - cap), (cap, cap, s - cap, s - cap), (s - cap, cap, s, s - cap),
           (0, s - cap, cap, s), (cap, s - cap, s - cap, s), (s - cap, s - cap, s, s)]
    dst = [(0, 0, cap, cap), (cap, 0, w - cap, cap), (w - cap, 0, w, cap),
           (0, cap, cap, h - cap), (cap, cap, w - cap, h - cap), (w - cap, cap, w, h - cap),
           (0, h - cap, cap, h), (cap, h - cap, w - cap, h), (w - cap, h - cap, w, h)]
    for a, d in zip(src, dst):
        dw, dh = d[2] - d[0], d[3] - d[1]
        if dw > 0 and dh > 0:
            out.paste(b.crop(a).resize((dw, dh), Image.LANCZOS), (d[0], d[1]))
    return out


def _header(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, HEAD], fill=rgb(t['bg']))
    _round(d, [24, 34, 150, 52], 9, rgb(t['text']))
    _round(d, [W - 96, 34, W - 24, 52], 9, rgb(t['accent']))
    d.line([(0, HEAD - 1), (W, HEAD - 1)], fill=rgb(t['border']))


def chat(t):
    """채팅방. 말풍선 네 칸을 전부 보여준다 — 알록달록한 테마는 여기서 드러난다."""
    img = Image.new('RGB', (W, H), rgb(t['bg']))
    body = H - HEAD - FOOT
    if t['chat_bg']:
        img.paste(gen.chat_bg(t['chat_bg'], W, body), (0, HEAD))
    else:
        img.paste(Image.new('RGB', (W, body), rgb(t['bg_deep'])), (0, HEAD))
    _header(img, t)

    rows = [('recv', 'recv', 260), ('recv', 'recv_alt', 180),
            ('send', 'send', 230), ('send', 'send_alt', 150)]
    y = HEAD + 30
    for side, key, bw in rows:
        bh = 78
        x = 26 if side == 'recv' else W - 26 - bw
        b = stretched(t[key], bw, bh)
        img.paste(b, (x, y), b)
        d = ImageDraw.Draw(img)
        tc = rgb(t['recv_text'] if side == 'recv' else t['send_text'])
        _round(d, [x + 22, y + 26, x + bw - 30, y + 40], 7, tc)
        _round(d, [x + 22, y + 48, x + bw - 70, y + 58], 5, tc)
        y += bh + 22

    d = ImageDraw.Draw(img)
    d.rectangle([0, H - FOOT, W, H], fill=rgb(t['surface']))
    _round(d, [24, H - FOOT + 26, W - 96, H - FOOT + 68], 21, rgb(t['pressed']))
    d.ellipse([W - 80, H - FOOT + 26, W - 38, H - FOOT + 68], fill=rgb(t['accent']))
    _round(d, [W - 68, H - FOOT + 42, W - 50, H - FOOT + 52], 5, rgb(t['on_accent']))
    return img


def chat_list(t):
    """친구탭/채팅목록. 목록 쪽 색과 눌린 줄이 여기서 드러난다."""
    img = Image.new('RGB', (W, H), rgb(t['bg']))
    _header(img, t)
    d = ImageDraw.Draw(img)

    y = HEAD + 20
    _round(d, [26, y, 110, y + 14], 6, rgb(t['subtext']))
    d.line([(0, y + 30), (W, y + 30)], fill=rgb(t['border']))
    y += 44

    for i in range(6):
        if y + 92 > H - FOOT:
            break
        d.rectangle([0, y, W, y + 92], fill=rgb(t['pressed'] if i == 1 else t['bg']))
        d.ellipse([26, y + 18, 82, y + 74], fill=rgb(t['surface']))
        d.ellipse([34, y + 26, 74, y + 66], fill=rgb(t['accent'] if i % 3 == 0 else t['subtext']))
        _round(d, [100, y + 28, 250 - i * 12, y + 44], 7, rgb(t['text']))
        _round(d, [100, y + 52, 330 - i * 18, y + 64], 6, rgb(t['subtext']))
        if i % 2 == 0:
            d.ellipse([W - 60, y + 40, W - 32, y + 68], fill=rgb(t['accent']))
        d.line([(100, y + 91), (W, y + 91)], fill=rgb(t['border']))
        y += 92

    d.rectangle([0, H - FOOT, W, H], fill=rgb(t['bg']))
    d.line([(0, H - FOOT), (W, H - FOOT)], fill=rgb(t['border']))
    for i in range(5):
        cx = int(W * (i + 0.5) / 5)
        c = t['accent'] if i == 1 else t['subtext']
        _round(d, [cx - 16, H - FOOT + 28, cx + 16, H - FOOT + 60], 9, rgb(c))
    return img


def splash(t):
    return gen.splash(t, W, H)


SHOTS = (('list', '목록'), ('chat', '채팅방'), ('splash', '실행화면'))

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
