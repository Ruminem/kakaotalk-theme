# -*- coding: utf-8 -*-
"""팔레트 표(tools/themes.py)에서 테마 소스 전부를 만든다.

    python tools/gen.py

결과는 build-src/<key>/ 아래. 빌드 스크립트가 그걸 읽어 .ktheme 과 .apk 로 포장한다.
생성물은 저장소에 넣지 않는다 — 원본은 팔레트 표 하나뿐이어야 한다.

iOS 와 안드로이드는 같은 그림을 다른 형식으로 요구한다.
  iOS     @2x / @3x 두 장. 늘어나는 범위는 CSS 의 cap inset 숫자로 따로 적는다.
  Android 9-patch 한 장. 늘어나는 범위를 이미지 1픽셀 테두리에 그려 넣는다.
"""
import os
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
INSET_V, INSET_H = 11, 16   # 글자와 말풍선 사이 기본 여백 (pt)


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def argb(h, alpha=1.0):
    """#RRGGBB 를 안드로이드용 #AARRGGBB 로. alpha 는 0.0~1.0."""
    return '#%02X%s' % (round(max(0.0, min(1.0, alpha)) * 255), h.lstrip('#').upper())


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


def bubble_box(w, h, colors, radius, style='solid', alpha=255, glow=None, pad=0,
               flat=False):
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
        # 테두리에 빛나는 선을 얹고, 위에서 아래로 갈수록 흐리게 만든다.
        # 빛이 한쪽에서만 들어오는 것처럼 보이게 하려는 것이다.
        rim = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
        ImageDraw.Draw(rim).rounded_rectangle(
            [SS // 2, SS // 2, w * SS - SS // 2 - 1, h * SS - SS // 2 - 1],
            radius=radius * SS, outline=(255, 255, 255, 215), width=SS)
        rim = rim.resize((w, h), Image.LANCZOS)

        ramp = Image.new('L', (1, h))
        px = ramp.load()
        for y in range(h):
            px[0, y] = int(255 * max(0.0, 1.0 - (y / max(h - 1, 1)) * 1.5))
        ramp = ramp.resize((w, h))

        faded = ImageChops.multiply(rim.getchannel('A'), ramp)
        rim.putalpha(ImageChops.multiply(faded, mask))
        out.alpha_composite(rim)

    if not pad:
        return out

    # 바깥 글로우: 같은 모양을 글로우 색으로 찍어 흐린 뒤 본체를 그 위에 얹는다
    gw, gh = w + pad * 2, h + pad * 2
    halo = Image.new('RGBA', (gw, gh), (0, 0, 0, 0))
    shape = Image.new('L', (gw, gh), 0)
    ImageDraw.Draw(shape).rounded_rectangle(
        [pad, pad, pad + w - 1, pad + h - 1], radius=radius, fill=255)
    gc, ga = glow
    if gc == 'auto':
        # 말풍선마다 자기 색으로 빛난다. 칸마다 색이 다른 테마에 어울린다
        gc = mid(colors[0], colors[1])
    halo.paste(Image.new('RGBA', (gw, gh), rgb(gc) + (255,)), (0, 0), shape)
    halo = halo.filter(ImageFilter.GaussianBlur(radius=pad * 0.42))
    # 흐리면 알파가 얇게 퍼져서 거의 안 보인다. 몸통 가까운 쪽을 끌어올린다
    halo.putalpha(halo.getchannel('A').point(
        lambda v: min(255, int(v * 2.4 * ga / 255))))
    halo.alpha_composite(out, (pad, pad))
    return halo


def bubble(scale, colors, style='solid', alpha=255, glow=None, pad=0, flat=False):
    """안드로이드 9-patch 와 iOS 용 정사각 말풍선."""
    return bubble_box(SIZE * scale, SIZE * scale, colors, RADIUS * scale,
                      style, alpha, glow, pad * scale, flat)


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


def chat_bg(spec, w, h):
    kind = spec[0]
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
        base = base.filter(ImageFilter.GaussianBlur(radius=w // 4))
        return Image.blend(Image.new('RGB', (w, h), rgb(spec[1])), base, 0.7)
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


def edge_glow(img, color, strength, width_ratio=0.22):
    """배경 가장자리에 빛을 흘린다. 화면 테두리에서 빛이 새어 들어오는 느낌."""
    w, h = img.size
    ramp = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(ramp)
    steps = 40
    bw = int(min(w, h) * width_ratio)
    for i in range(steps):
        t = i / (steps - 1)
        inset = int(bw * t)
        d.rectangle([inset, inset, w - 1 - inset, h - 1 - inset],
                    outline=int(strength * (1 - t) ** 2))
    ramp = ramp.filter(ImageFilter.GaussianBlur(radius=bw // 3 or 1))
    layer = Image.new('RGBA', (w, h), rgb(color) + (255,))
    layer.putalpha(ramp)
    out = img.convert('RGBA')
    out.alpha_composite(layer)
    return out.convert('RGB')


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
    -kakaotalk-theme-id: 'com.kakao.talk.theme.{key}';
}}

/* 탭바. 아이콘 8종은 아직 카톡 기본값이다 */
TabBarStyle-Main
{{
    background-color: {bg};
}}

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
    -ios-highlighted-text-color: {text};

    -ios-description-text-color: {subtext};
    -ios-description-highlighted-text-color: {subtext};

    -ios-paragraph-text-color: {subtext};
    -ios-paragraph-highlighted-text-color: {subtext};

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
    -ios-selected-text-color: {send_text};
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
    -ios-selected-text-color: {recv_text};
    -ios-unread-text-color: {accent};
}}

BackgroundStyle-Passcode
{{
    background-color: {bg_deep};
}}

LabelStyle-PasscodeTitle
{{
    -ios-text-color: {text};
}}

PasscodeStyle
{{
    -ios-keypad-background-color: {surface};
    -ios-keypad-text-normal-color: {text};
}}

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


def background(t, spec, w, h):
    """배경 이미지 한 장. 테마에 글로우가 있으면 가장자리에 빛을 흘린다."""
    img = chat_bg(spec, w, h)
    g = t.get('glow')
    if g:
        # 배경에는 말풍선처럼 따라갈 색이 없다. auto 면 포인트색을 쓴다
        color = t['accent'] if g[0] == 'auto' else g[0]
        # 배경은 면적이 넓어서 말풍선과 같은 세기로 넣으면 화면이 뿌예진다
        img = edge_glow(img, color, int(g[1] * 0.7))
    return img


def gen_ios(t, root):
    img_dir = os.path.join(root, 'Images')
    os.makedirs(img_dir, exist_ok=True)

    style, alpha = t.get('bubble_style', 'solid'), t.get('bubble_alpha', 255)
    glow, pad = glow_of(t)
    for side, key in (('Send', 'send'), ('Receive', 'recv')):
        for variant, pal in (('01', t[key]), ('02', t[key + '_alt'])):
            for scale in (2, 3):
                name = 'chatroomBubble%s%s@%dx.png' % (side, variant, scale)
                bubble(scale, pal, style, alpha, glow, pad,
                       t.get('flat', False)).save(os.path.join(img_dir, name))

    chatbg = ''
    if t['chat_bg']:
        background(t, t['chat_bg'], 600, 1300).save(os.path.join(img_dir, 'chatroomBgImage@2x.png'))
        background(t, t['chat_bg'], 900, 1950).save(os.path.join(img_dir, 'chatroomBgImage@3x.png'))
        chatbg = "\n    -ios-background-image: 'chatroomBgImage.png';"

    mainbg = ''
    if t.get('main_bg'):
        background(t, t['main_bg'], 600, 1300).save(os.path.join(img_dir, 'mainBgImage@2x.png'))
        background(t, t['main_bg'], 900, 1950).save(os.path.join(img_dir, 'mainBgImage@3x.png'))
        mainbg = "\n    -ios-background-image: 'mainBgImage.png';"

    ca = t.get('cell_alpha', 1.0)
    fields = dict(t)
    fields.pop('cell_alpha', None)          # 아래에서 문자열로 다시 넣는다
    ins = '%dpx %dpx %dpx %dpx' % (INSET_V + pad, INSET_H + pad,
                                  INSET_V + pad, INSET_H + pad)
    css = CSS.format(version=themes.VERSION, cap=CAP + pad, ins=ins,
                     chatbg=chatbg, mainbg=mainbg,
                     cell_alpha='%.2f' % ca,
                     cell_alpha_sel='%.2f' % min(1.0, ca + 0.15), **fields)
    with open(os.path.join(root, 'KakaoTalkTheme.css'), 'w', encoding='utf-8') as f:
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
    package="com.kakao.talk.theme.{key}"
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
    ('theme_title_pressed_color', 'text'),
    ('theme_paragraph_color', 'subtext'),
    ('theme_paragraph_pressed_color', 'subtext'),
    ('theme_description_color', 'subtext'),
    ('theme_description_pressed_color', 'subtext'),
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


def gen_android(t, root, code):
    values = os.path.join(root, 'res', 'values')
    draw = os.path.join(root, 'res', 'drawable-xxhdpi')
    os.makedirs(values, exist_ok=True)
    os.makedirs(draw, exist_ok=True)

    with open(os.path.join(root, 'AndroidManifest.xml'), 'w', encoding='utf-8') as f:
        f.write(MANIFEST.format(key=t['key'], version=themes.VERSION, code=code))

    with open(os.path.join(values, 'strings.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
                '    <string name="theme_title">%s</string>\n'
                '    <string name="app_name">%s</string>\n</resources>\n'
                % (t['name'], t['name']))

    lines = ['<?xml version="1.0" encoding="utf-8"?>',
             '<!-- %s. tools/themes.py 에서 생성된다. 직접 고치지 말 것. -->' % t['name'],
             '<resources>', '']
    ca = t.get('cell_alpha', 1.0)
    # 셀 배경만 알파를 먹인다. 글자색까지 투명해지면 안 읽힌다
    faded = {'theme_body_cell_color', 'theme_body_secondary_cell_color',
             'theme_maintab_cell_color', 'theme_header_cell_color'}
    for name, token in COLORS:
        a = ca if name in faded else 1.0
        lines.append('    <color name="%s">%s</color>' % (name, argb(t[token], a)))
    ba = t.get('bubble_alpha', 255) / 255.0
    lines += ['',
              '    <!-- 말풍선은 9-patch 이미지가 이긴다. 아래는 이미지가 안 먹을 때의 대비값 -->',
              '    <color name="theme_chatroom_bubble_me_color">%s</color>' % argb(mid(*t['send']), ba),
              '    <color name="theme_chatroom_bubble_you_color">%s</color>' % argb(mid(*t['recv']), ba),
              '', '</resources>', '']
    with open(os.path.join(values, 'colors.xml'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    style, alpha = t.get('bubble_style', 'solid'), t.get('bubble_alpha', 255)
    glow, pad = glow_of(t)
    for who, key in (('me', 'send'), ('you', 'recv')):
        for variant, pal in (('01', t[key]), ('02', t[key + '_alt'])):
            name = 'theme_chatroom_bubble_%s_%s_image.9.png' % (who, variant)
            ninepatch(bubble(3, pal, style, alpha, glow, pad, t.get('flat', False)),
                      (CAP + pad) * 3).save(os.path.join(draw, name))

    splash(t, 1080, 1920).save(os.path.join(draw, 'theme_splash_image.png'), optimize=True)
    if t['chat_bg']:
        background(t, t['chat_bg'], 1080, 1920).save(
            os.path.join(draw, 'theme_chatroom_background_image.png'), optimize=True)
    if t.get('main_bg'):
        background(t, t['main_bg'], 1080, 1920).save(
            os.path.join(draw, 'theme_background_image.png'), optimize=True)


# 미리보기와 갤러리는 tools/preview.py 가 만든다
DOCS = os.path.join(ROOT, 'docs')


def main():
    import preview                      # 순환 임포트를 피하려고 여기서 부른다
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(DOCS, exist_ok=True)
    for i, t in enumerate(themes.THEMES, start=1):
        root = os.path.join(OUT, t['key'])
        gen_ios(t, os.path.join(root, 'ios'))
        gen_android(t, os.path.join(root, 'android'), code=i)
        n = sum(len(f) for _, _, f in os.walk(root))
        extra = '  + 채팅방 배경' if t['chat_bg'] else ''
        print('%-12s %-9s 파일 %2d개%s' % (t['key'], t['name'], n, extra))
    print('\n%d 개 테마 -> build-src/' % len(themes.THEMES))
    preview.generate(themes.THEMES)
    print('미리보기 -> docs/index.html')


if __name__ == '__main__':
    main()
