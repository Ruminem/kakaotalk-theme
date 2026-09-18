# -*- coding: utf-8 -*-
"""커스텀 테마 워크플로가 받은 값을 검사해 GITHUB_ENV 에 적는다.

워크플로는 두 곳에서 값을 받는다 — Actions 의 Run workflow 칸과, 커스텀 테마 제작
페이지가 채워서 연 이슈 폼이다. 이슈 본문은 남이 쓴 것이라 믿을 수 없으므로 여기서
형식을 검사하고, 통과한 값만 환경 변수로 내보낸다. 뒤 단계는 이슈 본문을 직접 보지
않는다 — 본문이 셸에 그대로 들어가는 길을 아예 만들지 않으려는 것이다.

이슈 폼 본문은 `### <칸 이름>` 아래에 값이 오는 마크다운이다. 빈 칸은 `_No response_`.

    python tools/custominput.py          # EVENT/BODY/IN_* 환경 변수를 읽는다
    python tools/custominput.py --check  # 자체 점검
"""
import io
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 이슈 폼의 칸 이름 -> 내보낼 환경 변수. .github/ISSUE_TEMPLATE/custom-theme.yml 의
# label 과 글자까지 같아야 한다. 본문에는 id 가 아니라 label 이 찍힌다
LABELS = (
    ('배경', 'BG'),
    ('말풍선', 'BUBBLE'),
    ('보낸 말풍선 색', 'SEND'),
    ('받은 말풍선 색', 'RECV'),
    ('테마 이름', 'NAME'),
)
KEYS = ('BG', 'BUBBLE', 'SEND', 'RECV', 'ACCENT', 'NAME')

SLUG_RE = re.compile(r'^[a-z0-9-]{1,40}$')
HEX_RE = re.compile(r'^#[0-9A-Fa-f]{6}$')
BAD_NAME = re.compile(r'[\\/:*?"<>|\x00-\x1f]')
NAME_MAX = 40


def parse_issue(body):
    """이슈 폼 본문 -> {칸 이름: 값}."""
    out, key = {}, None
    for line in body.replace('\r\n', '\n').split('\n'):
        if line.startswith('### '):
            key = line[4:].strip()
            out[key] = []
        elif key is not None:
            out[key].append(line)
    got = {}
    for k, v in out.items():
        v = '\n'.join(v).strip()
        got[k] = '' if v == '_No response_' else v
    return got


def clean_name(v):
    v = BAD_NAME.sub('', v or '')
    v = ' '.join(v.split())[:NAME_MAX].strip()
    return v or '내 테마'


def resolve(env):
    """환경 변수 한 벌 -> 검사를 마친 값 한 벌. 어긋나면 SystemExit."""
    if env.get('EVENT') == 'issues':
        got = parse_issue(env.get('BODY') or '')
        vals = {k: got.get(label, '') for label, k in LABELS}
        vals['ACCENT'] = ''
    else:
        vals = {k: (env.get('IN_' + k) or '').strip() for k in KEYS}

    for k in ('BG', 'BUBBLE'):
        vals[k] = vals[k].strip().lower()
        if not SLUG_RE.match(vals[k]):
            raise SystemExit('%s 값이 테마 이름 형식이 아니다: %r' % (k, vals[k]))
    for k in ('SEND', 'RECV', 'ACCENT'):
        vals[k] = vals[k].strip().upper()
        if vals[k] and not HEX_RE.match(vals[k]):
            raise SystemExit('%s 값이 #RRGGBB 가 아니다: %r' % (k, vals[k]))
    vals['NAME'] = clean_name(vals['NAME'])
    return vals


def check():
    body = (u'### 배경\n\ncamp-dark-image\n\n'
            u'### 말풍선\n\nneon-double\n\n'
            u'### 보낸 말풍선 색\n\n#b6ff4d\n\n'
            u'### 받은 말풍선 색\n\n_No response_\n\n'
            u'### 테마 이름\n\n캠핑 어두움 이중관\n')
    v = resolve({'EVENT': 'issues', 'BODY': body})
    assert v == {'BG': 'camp-dark-image', 'BUBBLE': 'neon-double',
                 'SEND': '#B6FF4D', 'RECV': '', 'ACCENT': '',
                 'NAME': '캠핑 어두움 이중관'}, v

    v = resolve({'EVENT': 'workflow_dispatch', 'IN_BG': 'camp-dark-image',
                 'IN_BUBBLE': 'bakery-light', 'IN_NAME': '  내/테마:1*<x>  '})
    assert v['NAME'] == '내테마1x', v['NAME']
    assert resolve({'EVENT': 'issues', 'BODY': body.replace(
        '캠핑 어두움 이중관', ''), })['NAME'] == '내 테마'

    for bad in ('rm -rf /', 'camp dark', '../etc', 'CAMP;ls', ''):
        try:
            resolve({'EVENT': 'issues', 'BODY': u'### 배경\n\n%s\n\n### 말풍선\n\nneon-double\n' % bad})
        except SystemExit:
            continue
        raise AssertionError('통과하면 안 되는 값: %r' % bad)
    try:
        resolve({'EVENT': 'issues', 'BODY': body.replace('#b6ff4d', 'red')})
    except SystemExit:
        pass
    else:
        raise AssertionError('색 형식 검사가 안 먹었다')

    # 이슈 본문에는 칸의 label 이 찍힌다. 폼에서 label 을 고치면 여기 표가 어긋나
    # 값이 통째로 빈 채로 넘어간다 — 주석으로만 두지 않고 대조한다
    form = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        '.github', 'ISSUE_TEMPLATE', 'custom-theme.yml')
    try:
        import yaml
    except ImportError:
        print('(pyyaml 이 없어 이슈 폼 대조는 건너뜀)')
    else:
        with io.open(form, encoding='utf-8') as f:
            got = [b['attributes']['label'] for b in yaml.safe_load(f)['body']
                   if b['type'] == 'input']
        assert got == [label for label, _ in LABELS], got
    print('점검 통과')


def main():
    if '--check' in sys.argv:
        return check()
    vals = resolve(os.environ)
    out = os.environ.get('GITHUB_ENV')
    line = '\n'.join('%s=%s' % (k, vals[k]) for k in KEYS)
    if out:
        with io.open(out, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    print(line)


if __name__ == '__main__':
    main()
