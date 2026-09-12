# -*- coding: utf-8 -*-
"""말풍선과 스플래시 이미지를 그린다.

    python tools/gen-images.py

손으로 그린 PNG 가 아니라 스크립트가 만든다. 색을 바꾸려면 아래 팔레트만 고치고
다시 돌리면 된다. 결과는 저장소에 커밋한다 — 빌드 스크립트가 파이썬을 요구하지
않도록.

iOS 와 안드로이드는 같은 그림을 다른 형식으로 요구한다.
  iOS      : @2x / @3x 두 장. 늘어나는 범위는 CSS 의 cap inset 숫자로 따로 적는다.
  Android  : 9-patch 한 장. 늘어나는 범위를 이미지 1픽셀 테두리에 그려 넣는다.
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IOS = os.path.join(ROOT, 'ios', 'Images')
AOS = os.path.join(ROOT, 'android', 'res', 'drawable-xxhdpi')

# --- 팔레트 -------------------------------------------------------------
# 말풍선은 세로 그라데이션. 가로로 늘어나도 각 줄의 색이 유지되기 때문이다.
SEND    = ((0x5B, 0xE0, 0xB4), (0x3D, 0x9B, 0xD9))   # 민트 → 하늘
RECEIVE = ((0x8C, 0x6B, 0xE0), (0xD9, 0x6B, 0xB0))   # 보라 → 자주
INK     = (0x10, 0x12, 0x15)
MINT    = (0x4F, 0xD1, 0xB0)

# --- 말풍선 기하 (pt 기준) ----------------------------------------------
SIZE   = 44     # 한 변
RADIUS = 14     # 모서리
CAP    = 18     # 늘어나지 않는 가장자리. CSS 의 cap inset 과 같은 값이어야 한다


def vgradient(w, h, top, bottom):
    """세로 그라데이션 이미지."""
    img = Image.new('RGB', (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return img.resize((w, h), Image.BILINEAR)


def bubble(scale, colors):
    """둥근 사각형 말풍선 한 장. 바깥은 투명."""
    w = h = SIZE * scale
    r = RADIUS * scale
    # 계단현상을 줄이려고 4배로 그린 뒤 줄인다
    ss = 4
    mask = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=r * ss, fill=255)
    mask = mask.resize((w, h), Image.LANCZOS)

    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.paste(vgradient(w, h, *colors), (0, 0), mask)
    return out


def ninepatch(img, cap):
    """9-patch 테두리를 두른다.

    위/왼쪽 검은 선 = 늘어나는 범위, 오른쪽/아래 검은 선 = 내용 여백.
    """
    w, h = img.size
    out = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
    out.paste(img, (1, 1))
    d = ImageDraw.Draw(out)
    black = (0, 0, 0, 255)
    # 늘어나는 범위: 가운데만
    d.line([(1 + cap, 0), (w - cap, 0)], fill=black)
    d.line([(0, 1 + cap), (0, h - cap)], fill=black)
    # 내용 여백: 모서리를 피한 안쪽
    pad = cap // 2
    d.line([(1 + pad, h + 1), (w - pad, h + 1)], fill=black)
    d.line([(w + 1, 1 + pad), (w + 1, h - pad)], fill=black)
    return out


def splash(w, h):
    """안드로이드 실행화면. 먹색 바탕에 민트 빛을 얹는다."""
    img = vgradient(w, h, (0x16, 0x18, 0x1C), INK).convert('RGBA')
    glow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    cx, cy = w // 2, int(h * 0.42)
    steps = 90
    rmax = int(w * 0.62)
    for i in range(steps, 0, -1):
        rr = int(rmax * i / steps)
        a = int(42 * (1 - i / steps) ** 2.2)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=MINT + (a,))
    return Image.alpha_composite(img, glow)


def main():
    os.makedirs(IOS, exist_ok=True)
    os.makedirs(AOS, exist_ok=True)
    made = []

    for name, colors in (('Send', SEND), ('Receive', RECEIVE)):
        for scale in (2, 3):
            img = bubble(scale, colors)
            # 01 = 보통, 02 = 눌린 상태. 지금은 같은 그림을 쓴다
            for variant in ('01', '02'):
                p = os.path.join(IOS, f'chatroomBubble{name}{variant}@{scale}x.png')
                img.save(p)
                made.append(p)

    who = {'Send': 'me', 'Receive': 'you'}
    for name, colors in (('Send', SEND), ('Receive', RECEIVE)):
        img = ninepatch(bubble(3, colors), CAP * 3)
        for variant in ('01', '02'):
            p = os.path.join(AOS, f'theme_chatroom_bubble_{who[name]}_{variant}_image.9.png')
            img.save(p)
            made.append(p)

    p = os.path.join(AOS, 'theme_splash_image.png')
    splash(1080, 1920).convert('RGB').save(p, optimize=True)
    made.append(p)

    for p in made:
        print(f'{os.path.relpath(p, ROOT):58} {os.path.getsize(p):>8,} bytes')
    print(f'\n{len(made)} 장')


if __name__ == '__main__':
    main()
