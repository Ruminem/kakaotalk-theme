# -*- coding: utf-8 -*-
"""README 의 `받는 법` 으로 가는 QR 코드를 만든다.

    python tools/gen-qr.py

폰으로 링크를 옮기는 가장 빠른 방법이다. 카메라로 찍으면 테마 목록이 열린다.

릴리스 목록으로 보내지 않는다. 거기서 자산을 바로 누르면 iOS 의 share.html 도
안드로이드의 install.html 도 안 거치는데, 안드로이드는 그 안내를 건너뛰면
`보안 위험 자동 차단` 에 막혀 받아도 못 깐다. README 의 테마 표는 두 링크가
이미 그 페이지들을 거치므로, 목록으로 보내면서 안내도 같이 살릴 수 있다.

Pages 갤러리(docs/index.html)로도 보내지 않는다. 거기 받기 링크는 `../dist/` 라
사이트에 없다(404). 로컬에서 build.ps1 을 돌린 뒤에만 동작하는 페이지다.

QR 은 한 장이다. 플랫폼마다 갈라도 주소가 같아서 예전에는 같은 그림 두 장이었다.
"""
import os
import qrcode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = 'https://github.com/Ruminem/kakaotalk-theme#user-content-받는-법'


def main():
    # 흑백 그대로 둔다. 테마 색을 입히면 예쁘지만 인식률이 떨어진다
    qr = qrcode.QRCode(box_size=8, border=2,
                       error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(URL)
    qr.make(fit=True)
    p = os.path.join(ROOT, 'assets', 'qr.png')
    qr.make_image(fill_color='black', back_color='white').save(p)
    print(f'{os.path.relpath(p, ROOT):16} {os.path.getsize(p):>7,} bytes  '
          f'버전 {qr.version}  {URL}')


if __name__ == '__main__':
    main()
