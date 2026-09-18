# SPDX-License-Identifier: Apache-2.0
"""aapt2 compile 캐시의 키가 맞게 만들어지는지 본다.

    python tools/check-cache.py

키가 너무 헐거우면 그림을 고쳐도 옛 APK 가 나가고, 너무 빡빡하면 캐시가 늘 빗나가
아무것도 아껴지지 않는다. 둘 다 조용해서 눈으로는 안 보인다.
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen


def make(files):
    """res/ 를 흉내 낸 임시 폴더를 만들고 gen.res_digest 를 돌린다."""
    root = tempfile.mkdtemp(prefix='ktheme-cache-')
    res = os.path.join(root, 'res')
    for rel, body in files.items():
        p = os.path.join(res, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'wb') as f:
            f.write(body)
    gen.res_digest(res)
    with open(os.path.join(root, 'res.sha256'), encoding='utf-8') as f:
        return root, res, f.read().strip()


BASE = {'drawable-xxhdpi/a.png': b'\x89PNG-a',
        'drawable-xxhdpi/b.png': b'\x89PNG-b',
        'values/colors.xml': b'<resources/>'}

root1, res1, k1 = make(BASE)
root2, _, k2 = make(dict(BASE))
try:
    # 같은 내용이면 같은 키. 아니면 캐시가 늘 빗나간다.
    assert k1 == k2, (k1, k2)
    assert len(k1) == 64, k1

    # 해시 파일은 res/ 밖에 있어야 한다. 안에 있으면 aapt2 가 리소스로 집어 가고,
    # 그러면 키가 제 자신을 포함하게 된다.
    assert not os.path.exists(os.path.join(res1, 'res.sha256'))
    assert os.path.exists(os.path.join(root1, 'res.sha256'))

    # 그림 한 바이트가 달라지면 키도 달라져야 한다.
    changed = dict(BASE, **{'drawable-xxhdpi/a.png': b'\x89PNG-A'})
    root3, _, k3 = make(changed)
    assert k3 != k1, '그림이 바뀌었는데 키가 같다'
    shutil.rmtree(root3, ignore_errors=True)

    # 색만 달라져도 마찬가지다. colors.xml 도 compile 의 입력이다.
    changed = dict(BASE, **{'values/colors.xml': b'<resources><color/></resources>'})
    root4, _, k4 = make(changed)
    assert k4 != k1, '색이 바뀌었는데 키가 같다'
    shutil.rmtree(root4, ignore_errors=True)

    # 내용이 같아도 이름이 다르면 다른 키다. 두 파일의 내용을 맞바꾼 경우를 잡는다.
    swapped = dict(BASE, **{'drawable-xxhdpi/a.png': BASE['drawable-xxhdpi/b.png'],
                            'drawable-xxhdpi/b.png': BASE['drawable-xxhdpi/a.png']})
    root5, _, k5 = make(swapped)
    assert k5 != k1, '파일 이름이 뒤바뀌었는데 키가 같다'
    shutil.rmtree(root5, ignore_errors=True)
finally:
    shutil.rmtree(root1, ignore_errors=True)
    shutil.rmtree(root2, ignore_errors=True)

print('캐시 키 검사 통과')
