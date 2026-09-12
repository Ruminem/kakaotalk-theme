# -*- coding: utf-8 -*-
"""릴리스 다운로드 링크의 QR 코드를 만든다.

    python tools/gen-qr.py

폰으로 링크를 옮기는 가장 빠른 방법이다. 카메라로 찍으면 바로 내려받는다.
링크가 releases/latest 를 가리키므로 새 릴리스를 내도 이 QR 은 그대로 쓴다.
"""
import os
import qrcode
from qrcode.image.styledpil import StyledPilImage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
# 테마가 여러 개라 특정 파일이 아니라 릴리스 목록으로 보낸다.
# 거기서 원하는 테마를 고르게 하는 편이 낫다.
BASE = 'https://github.com/Ruminem/kakaotalk-theme/releases/latest'

TARGETS = {
    'qr-ios.png': BASE,
    'qr-android.png': BASE,
}


def main():
    os.makedirs(ASSETS, exist_ok=True)
    for name, url in TARGETS.items():
        # 흑백 그대로 둔다. 테마 색을 입히면 예쁘지만 인식률이 떨어진다
        qr = qrcode.QRCode(box_size=8, border=2,
                           error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        p = os.path.join(ASSETS, name)
        img.save(p)
        print(f'{os.path.relpath(p, ROOT):24} {os.path.getsize(p):>7,} bytes  {url}')


if __name__ == '__main__':
    main()
