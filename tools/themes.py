# -*- coding: utf-8 -*-
"""테마 팔레트 표. 여기가 유일한 원본이다.

CSS 도 colors.xml 도 이미지도 전부 이 표에서 나온다(tools/gen.py).
새 테마를 만들려면 아래에 한 덩어리를 더 쓰면 된다.

색 토큰
  bg          목록 화면 배경
  bg_deep     채팅방 바닥
  surface     한 단계 올라온 면 — 입력바, 배너, 키패드, 2차 화면
  pressed     눌린 상태
  border      구분선
  text        본문 글자
  subtext     보조 글자
  accent      포인트
  accent_dim  포인트 눌림
  on_accent   포인트 위에 얹는 글자

말풍선
  send / recv        (위색, 아래색) 세로 그라데이션
  send_alt/recv_alt  눌렸을 때와 그룹 채팅용. 일부러 다른 색을 주면 알록달록해진다
  send_text/recv_text

note
  README 와 미리보기 페이지에 그대로 실리는 한 줄 소개. 음슴체로 쓴다.

선택 항목 (없으면 기본값)
  bubble_style  'glass' 면 말풍선을 반투명하게 깔고 테두리에 빛나는 선을 얹는다
  bubble_alpha  말풍선 불투명도 0~255. 낮을수록 채팅방 배경이 비친다
  cell_alpha    목록 셀 불투명도 0.0~1.0. 1 미만이면 뒤의 배경 이미지가 비친다
  main_bg       목록 화면 배경 이미지. chat_bg 와 같은 형식
  passcode_bg   잠금화면 배경 이미지. 같은 형식. 카톡 비밀번호를 걸어야 보이는 화면이다
  flat          True 면 말풍선을 그라데이션 없이 단색으로 채운다. 두 색의 중간값을 쓴다
  glow          (색, 진하기 0~255, 여백pt). 색이 'auto' 면 말풍선마다 자기 색으로 빛난다. 말풍선 바깥으로 빛을 흘리고 배경 가장자리에도 얹는다.
                여백만큼 cap inset 이 자동으로 커진다 — 안 그러면 늘어날 때 글로우가 뭉개진다

chat_bg
  None 이면 단색. ('linear', 위, 아래) 또는 ('aurora', 바탕, [색...]) 이면 이미지를 그린다.
"""

import re

VERSION = '0.23'

THEMES = [
    dict(
        key='inkmint01', name='먹빛 민트',
        note='먹색 바탕에 민트 포인트. 말풍선은 민트에서 하늘로, 보라에서 자주로 흐름',
        bg='#16181C', bg_deep='#101215', surface='#1E2126', pressed='#242830',
        border='#2A2E35', text='#E8EBEE', subtext='#98A1AB',
        accent='#4FD1B0', accent_dim='#2E9E85', on_accent='#10241F',
        send=('#5BE0B4', '#3D9BD9'), send_alt=('#4ECBA6', '#3589C4'),
        recv=('#8C6BE0', '#D96BB0'), recv_alt=('#7C5CD0', '#C45C9E'),
        send_text='#0E2A24', recv_text='#FFFFFF',
        chat_bg=None,
    ),
    dict(
        key='cream02', name='크림 라떼',
        note='밝은 쪽. 베이지 바탕에 브라운. 눈이 제일 안 피로한 조합임',
        bg='#F7F2EA', bg_deep='#EFE7DA', surface='#FFFDF8', pressed='#E6DBC9',
        border='#DCCFB8', text='#3E342A', subtext='#8B7B67',
        accent='#B07A4B', accent_dim='#8A5C34', on_accent='#FFF8EE',
        send=('#E8C79A', '#D3A468'), send_alt=('#DFBC8B', '#C7975B'),
        recv=('#FFFFFF', '#F0E7D8'), recv_alt=('#F7F0E4', '#E6DACA'),
        send_text='#3A2C1C', recv_text='#3E342A',
        chat_bg=None,
    ),
    dict(
        key='sakura03', name='벚꽃 그늘',
        note='밝은 분홍. 채팅방 배경 이미지가 깔림',
        bg='#FFF6F7', bg_deep='#FDEDF0', surface='#FFFFFF', pressed='#FBE0E6',
        border='#F3D3DB', text='#4A3239', subtext='#9E7A84',
        accent='#E0698C', accent_dim='#BF4E70', on_accent='#FFF4F6',
        send=('#FFB3C8', '#F07EA6'), send_alt=('#FFA5BE', '#E56E98'),
        recv=('#FFFFFF', '#FCEAF0'), recv_alt=('#FBE6EE', '#F3D8E2'),
        send_text='#4A2430', recv_text='#4A3239',
        chat_bg=('linear', '#FFF1F5', '#F6DDE8'),
    ),
    dict(
        key='mixed04', name='믹스드',
        note='어두운 보라 바탕. 말풍선 네 칸이 전부 다른 색임',
        bg='#1A1726', bg_deep='#120F1C', surface='#231E33', pressed='#2E2743',
        border='#352D4C', text='#EDE9F7', subtext='#9A91B5',
        accent='#FFC24D', accent_dim='#D89A2B', on_accent='#2A1E05',
        # 네 칸에 전부 다른 색을 넣었다. 눌린 말풍선과 그룹 말풍선이 확 달라진다
        flat=True,
        send=('#FF8A5B', '#FFC24D'), send_alt=('#5BE0B4', '#3D9BD9'),
        recv=('#7C6BE0', '#D96BB0'), recv_alt=('#4DC9E0', '#6BE09B'),
        send_text='#3A1E05', recv_text='#FFFFFF',
        chat_bg=None,
    ),
    dict(
        key='aurora05', name='오로라',
        note='가장 어두운 테마. 채팅방 배경에 오로라가 번짐',
        bg='#0E1A22', bg_deep='#08121A', surface='#14242E', pressed='#1C3140',
        border='#23404F', text='#E4F1F5', subtext='#8FAAB8',
        accent='#5BE8C8', accent_dim='#33B99C', on_accent='#062018',
        send=('#5BE8C8', '#4A9FE0'), send_alt=('#49D3B4', '#3E8CCB'),
        recv=('#2B4B5E', '#1B3444'), recv_alt=('#345A70', '#223E51'),
        send_text='#052420', recv_text='#E4F1F5',
        chat_bg=('aurora', '#08121A', ['#5BE8C8', '#4A9FE0', '#9B6BE0']),
    ),
    dict(
        key='candy06', name='캔디 팝',
        note='밝은 쪽 알록달록. 말풍선 네 칸이 전부 다르고 배경도 있음',
        bg='#FFFDF5', bg_deep='#FFF8E7', surface='#FFFFFF', pressed='#FFEFC9',
        border='#F2E2BE', text='#3A3A46', subtext='#8A8698',
        accent='#FF7AA2', accent_dim='#E0537F', on_accent='#FFFFFF',
        # 라이트 쪽 알록달록. 네 칸이 전부 다르다
        flat=True,
        send=('#FFD166', '#FF9F68'), send_alt=('#8AE0C0', '#4FC3D9'),
        recv=('#C2A7FF', '#FF9BC6'), recv_alt=('#9BD6FF', '#7ED7C1'),
        send_text='#4A2E10', recv_text='#3A2440',
        chat_bg=('linear', '#FFFDF5', '#FFE9D6'),
    ),
    dict(
        key='glass07', name='리퀴드 글래스',
        note='유리 너머로 빛이 번지는 밝은 쪽. 말풍선과 목록이 반투명이라 배경이 비침',
        bg='#F2F4F8', bg_deep='#E9EEF5', surface='#FFFFFF', pressed='#DCE4EF',
        border='#D2DBE8', text='#1F2733', subtext='#6B7789',
        accent='#2F8CF0', accent_dim='#1E6FC4', on_accent='#FFFFFF',
        send=('#8FD3FF', '#5FA8F5'), send_alt=('#A9E7FF', '#79C2F8'),
        recv=('#F4F9FF', '#DCE8F8'), recv_alt=('#EAF3FF', '#D2E2F6'),
        send_text='#0B2D50', recv_text='#1F2733',
        bubble_style='glass', bubble_alpha=150, cell_alpha=0.55,
        glow=('#6FB6FF', 140, 8),
        chat_bg=('blobs', '#EFF3FA', ['#9BD4FF', '#C9B6FF', '#9BF0DC', '#FFC8E4']),
        main_bg=('blobs', '#F4F6FB', ['#BFE2FF', '#DCD0FF', '#C4F3E6', '#FFD9EC']),
    ),
    dict(
        key='glass08', name='리퀴드 글래스 다크',
        note='같은 유리를 어두운 쪽으로. 빛이 유리 모서리에만 걸림',
        bg='#12151C', bg_deep='#0B0E14', surface='#1A1F29', pressed='#232A37',
        border='#2B3342', text='#E8EDF6', subtext='#8D99AC',
        accent='#5AB5FF', accent_dim='#3789CC', on_accent='#06192B',
        send=('#3E7FC9', '#2A5C9B'), send_alt=('#4E93DC', '#3468AA'),
        recv=('#39404F', '#262C38'), recv_alt=('#454D5E', '#2F3542'),
        send_text='#EAF4FF', recv_text='#E8EDF6',
        bubble_style='glass', bubble_alpha=175, cell_alpha=0.55,
        glow=('#5AB5FF', 180, 8),
        chat_bg=('blobs', '#0B0E14', ['#2F6FB5', '#6A4FB0', '#2E8C7E', '#B0487F']),
        main_bg=('blobs', '#10131A', ['#27568C', '#4E3C86', '#256B61', '#8A3A64']),
    ),
    dict(
        key='midnight11', name='심야',
        note='밤하늘을 그려 넣은 테마. 잠금화면에 달과 능선이 나옴',
        bg='#0F1320', bg_deep='#080B14', surface='#171C2B', pressed='#1F2637',
        border='#29314A', text='#E6EAF5', subtext='#8C95AE',
        accent='#8AA4FF', accent_dim='#5C76D6', on_accent='#060A1A',
        send=('#6E86E6', '#42589E'), send_alt=('#5F79DC', '#374C8E'),
        recv=('#2A3450', '#1B2236'), recv_alt=('#343F5E', '#232B42'),
        send_text='#F0F4FF', recv_text='#E6EAF5',
        glow=None,
        # 잠금화면은 글자가 적으니 달과 능선까지 다 그린다.
        # 채팅방은 말풍선이 얹히므로 별만 두고 어둡게 덮는다.
        chat_bg=('night', '#0B1020', '#121A30',
                 dict(stars=150, glints=4, moon=None, ridge=None, dim=0.25)),
        main_bg=('night', '#0D1222', '#151B2E',
                 dict(stars=110, glints=3, moon=None, ridge=None, dim=0.35)),
        passcode_bg=('night', '#070B18', '#16203C',
                     dict(stars=260, glints=8, moon='#E8ECFF', ridge='#05070F',
                          moon_x=0.74, moon_y=0.16, moon_r=0.09)),
    ),
]


def by_key(key):
    for t in THEMES:
        if t['key'] == key:
            return t
    raise KeyError(key)


def _index(key):
    for i, t in enumerate(THEMES):
        if t['key'] == key:
            return i
    raise KeyError(key)


def _variant(src, key, name, note, **over):
    """기존 테마를 베껴 일부만 바꾼 변형.

    팔레트를 두 벌 관리하면 원본을 고칠 때 변형이 따라오지 않는다.
    색은 원본 하나에만 두고 여기서는 바뀌는 것만 적는다.
    """
    t = dict(by_key(src))
    t.update(key=key, name=name, note=note, **over)
    return t


def _add_variant(src, key, name, note, **over):
    """변형을 원본 바로 뒤에 끼워 넣는다.

    목록 순서가 곧 README 와 갤러리 순서다. 뒤에 몰아 붙이면 원본과 떨어져서
    무엇을 고친 것인지 안 보인다.
    """
    THEMES.insert(_index(src) + 1, _variant(src, key, name, note, **over))


def _add_plain_variant(src, key, name, note, **over):
    """배경 그림을 걷어낸 변형. 반투명 말풍선만 남는다.

    반투명은 뒤에 그림이 있어야 값을 한다고 생각하기 쉬운데, 단색 바탕에서도
    말풍선이 바탕색을 머금어 팔레트에 없는 중간색이 생긴다. 그림이 깔린 쪽보다
    차분해서 배경을 싫어하는 사람이 쓸 자리가 된다.
    """
    t = _variant(src, key, name, note, **over)
    for k in ('chat_bg', 'main_bg', 'passcode_bg'):
        t[k] = None
    THEMES.insert(_index(src) + 1, t)


_add_variant('mixed04', 'mixed09', '믹스드 v2',
             '믹스드에 글로우를 얹은 것. 말풍선마다 자기 색으로 빛남',
             glow=('auto', 190, 8))
_add_variant('candy06', 'candy10', '캔디 팝 v2',
             '캔디 팝에 글로우를 얹은 것. 밝은 바탕이라 빛이 은은하게 걸림',
             glow=('auto', 175, 8))

_add_variant('candy10', 'candy12', '캔디 팝 v3',
             '사탕을 흩뿌린 배경. 글로우는 빼서 글로우+배경과 구분됨',
             glow=None,
             chat_bg=('candy', '#FFFDF5', '#FFE9D6',
                      dict(count=22, sprinkles=70, dim=0.42)),
             main_bg=('candy', '#FFFDF5', '#FFF1E2',
                      dict(count=16, sprinkles=50, dim=0.55)),
             passcode_bg=('candy', '#FFF8E8', '#FFD9C0',
                          dict(count=34, sprinkles=110, dim=0.12)))
_add_plain_variant('glass07', 'glass51', '리퀴드 글래스 단색',
                   '배경 그림 없이 유리만. 바탕색을 머금어 색이 가라앉음',
                   bg='#DCE7F6', bg_deep='#CFDCEF', bubble_alpha=140)
_add_plain_variant('glass08', 'glass52', '리퀴드 글래스 다크 단색',
                   '어두운 바탕에 유리만. 빛나는 것 없이 테두리만 남음',
                   bg='#171D28', bg_deep='#10151E', bubble_alpha=170)

_add_variant('sakura03', 'sakura13', '벚꽃 그늘 v2',
             '벚꽃 그늘에 가지와 꽃잎을 그려 넣었음',
             chat_bg=('sakura', '#FFF3F6', '#FBE2EC',
                      dict(flowers=16, petals=30, bokeh=12, branch=False, dim=0.38)),
             main_bg=('sakura', '#FFF6F8', '#FCE8F0',
                      dict(flowers=10, petals=22, bokeh=10, branch=False, dim=0.52)),
             passcode_bg=('sakura', '#FFF0F5', '#F8D3E2',
                          dict(flowers=30, petals=46, bokeh=18, branch=True, dim=0.0)))


# --- 기본 생성 규칙 -------------------------------------------------------

def standard(key, name, note, **kw):
    """새 테마는 이 규칙으로 만든다.

    1. 글로우 없음
    2. 말풍선에 그라데이션 없음 — 단색
    3. 말풍선 네 칸이 서로 다른 색
    4. 배경 이미지가 세 화면에 다 있음 (목록·채팅방·잠금화면)
    5. 아이콘 — 모든 테마에 자동으로 생성되므로 따로 할 일 없음

    어기면 여기서 멈춘다. 규칙을 글로만 적어두면 다음에 만들 때 잊는다.
    앞서 만든 테마들은 이 규칙 이전에 나온 것이라 그대로 둔다.
    """
    t = dict(key=key, name=name, note=note, flat=True, **kw)
    t.pop('glow', None)
    t.pop('bubble_style', None)

    # 배경은 여기서 강제하지 않는다. 네 벌 중 둘은 배경이 없는 것이 정상이다.
    # 대신 quartet() 이 계열에 배경 있는 변형이 포함되게 보장한다.
    got = [slot for slot in ('chat_bg', 'main_bg', 'passcode_bg') if t.get(slot)]
    if got and len(got) != 3:
        raise ValueError('%s: 배경을 넣으려면 세 화면에 다 넣는다. 지금 %s 뿐이다'
                         % (key, ', '.join(got)))

    # 단색으로 칠할 때 쓰는 값이 네 칸 모두 달라야 한다
    seen = {}
    for slot in ('send', 'send_alt', 'recv', 'recv_alt'):
        a, b = t[slot]
        c = '#%02X%02X%02X' % tuple(
            (int(a.lstrip('#')[i:i + 2], 16) + int(b.lstrip('#')[i:i + 2], 16)) // 2
            for i in (0, 2, 4))
        if c in seen:
            raise ValueError('%s: %s 와 %s 의 말풍선 색이 같다(%s)'
                             % (key, seen[c], slot, c))
        seen[c] = slot
    return t


THEMES += [
    standard(
        'sea14', '바다',
        '수평선 너머로 해가 지는 바다. 말풍선 네 칸이 산호·모래·물빛·하늘색',
        bg='#0E1E2A', bg_deep='#081520', surface='#16303F', pressed='#1E3E51',
        border='#27506A', text='#E6F1F7', subtext='#8FAABB',
        accent='#FFC489', accent_dim='#D19455', on_accent='#1B2A16',
        send=('#FF9A76', '#FF9A76'), send_alt=('#FFD6A5', '#FFD6A5'),
        recv=('#2E6E86', '#2E6E86'), recv_alt=('#7FC4D8', '#7FC4D8'),
        send_text='#3A1B0C', recv_text='#EAF6FA',
        chat_bg=('sea', '#14344A', '#2E6A7E',
                 dict(horizon=0.40, sun_x=0.72, water_top='#1E4B63',
                      water_bottom='#0A1A26', waves=70, dim=0.30)),
        main_bg=('sea', '#14344A', '#2E6A7E',
                 dict(horizon=0.34, water_top='#1A4257', water_bottom='#08141D',
                      waves=50, dim=0.45)),
        passcode_bg=('sea', '#1B3E56', '#D98A5C',
                     dict(horizon=0.46, sun_x=0.66, sun_y=0.72, sun='#FFD9A0',
                          water_top='#2A5E76', water_bottom='#0A1A26', waves=80)),
    ),
    standard(
        'forest15', '숲',
        '안개 낀 침엽수 숲. 이끼·호박·하늘·흙빛 말풍선',
        bg='#16241D', bg_deep='#0E1A15', surface='#1E322A', pressed='#284034',
        border='#33513F', text='#E4F0E8', subtext='#93AC9D',
        accent='#8FD6A0', accent_dim='#5FA872', on_accent='#0C1A11',
        send=('#7CB98C', '#7CB98C'), send_alt=('#D8B06A', '#D8B06A'),
        recv=('#2C4A3B', '#2C4A3B'), recv_alt=('#6E93A8', '#6E93A8'),
        send_text='#10261A', recv_text='#E4F0E8',
        chat_bg=('forest', '#20404F', '#5B8A78',
                 dict(layers=['#1A3329', '#224134', '#2C5241'], dim=0.34)),
        main_bg=('forest', '#1C3743', '#4F7A6A',
                 dict(layers=['#162C23', '#1E3A2E'], dim=0.48)),
        passcode_bg=('forest', '#27505F', '#7FB49C',
                     dict(layers=['#1A3329', '#224134', '#2C5241', '#3A6A52'],
                          fog='#CFE4D8')),
    ),
]

THEMES += [
    standard(
        'snow17', '설원',
        '눈 내리는 언덕. 얼음·살구·민트·라벤더 말풍선',
        bg='#F2F6FB', bg_deep='#E7EEF7', surface='#FFFFFF', pressed='#DCE6F2',
        border='#CBD9E8', text='#26323F', subtext='#6D7E90',
        accent='#5C93C4', accent_dim='#3E6E9B', on_accent='#FFFFFF',
        send=('#A8CFEE', '#A8CFEE'), send_alt=('#F7C9A8', '#F7C9A8'),
        recv=('#FFFFFF', '#FFFFFF'), recv_alt=('#C9BDEA', '#C9BDEA'),
        send_text='#17303F', recv_text='#26323F',
        chat_bg=('snow', '#DCE8F5', '#F4F8FC',
                 dict(flakes=200, hills=[(0.76, '#EDF3FA'), (0.86, '#F8FBFE')], dim=0.30)),
        main_bg=('snow', '#E4EDF7', '#F7FAFD',
                 dict(flakes=140, hills=[(0.82, '#F2F7FC')], dim=0.45)),
        passcode_bg=('snow', '#C9DCEF', '#EFF5FB',
                     dict(flakes=300, hills=[(0.70, '#E7F0F9'), (0.80, '#F3F8FC'),
                                             (0.90, '#FBFDFE')])),
    ),
    standard(
        'geo18', '도형',
        '큰 도형이 겹친 무늬. 주황·민트·보라·하늘 말풍선',
        bg='#FBFAF7', bg_deep='#F4F2EE', surface='#FFFFFF', pressed='#EDEAE3',
        border='#E0DCD3', text='#2B2A27', subtext='#7A776F',
        accent='#FF7A45', accent_dim='#D65A2A', on_accent='#FFFFFF',
        send=('#FFA86B', '#FFA86B'), send_alt=('#6FD9BE', '#6FD9BE'),
        recv=('#FFFFFF', '#FFFFFF'), recv_alt=('#A99BE8', '#A99BE8'),
        send_text='#3A1B08', recv_text='#2B2A27',
        chat_bg=('geo', '#FBFAF7', '#F2EFE8',
                 dict(count=8, alpha_lo=18, alpha_hi=40, blur=0.012)),
        main_bg=('geo', '#FBFAF7', '#F5F2EC',
                 dict(count=6, alpha_lo=14, alpha_hi=30, blur=0.02)),
        passcode_bg=('geo', '#F7F4EE', '#EDE8DE',
                     dict(count=12, alpha_lo=30, alpha_hi=72)),
    ),
]


# --- 계열 ----------------------------------------------------------------
# README 는 테마가 아니라 계열 단위로 나열한다. 변형이 늘어날 때 목록이 같이
# 길어지면 훑어보기가 안 된다. 계열은 고정되고 변형은 그 안에서 옆으로 늘어난다.

FAMILY = {
    'inkmint01':  ('먹빛 민트', '기본'),
    'cream02':    ('크림 라떼', '기본'),
    'sakura03':   ('벚꽃 그늘', '기본'),
    'sakura13':   ('벚꽃 그늘', '벚꽃 배경'),
    'mixed04':    ('믹스드', '기본'),
    'mixed09':    ('믹스드', '글로우'),
    'aurora05':   ('오로라', '배경'),
    'candy06':    ('캔디 팝', '기본'),
    'candy10':    ('캔디 팝', '글로우'),
    'candy12':    ('캔디 팝', '사탕 배경'),
    'glass07':    ('리퀴드 글래스', '라이트'),
    'glass08':    ('리퀴드 글래스', '다크'),
    'glass51':    ('리퀴드 글래스', '라이트 단색'),
    'glass52':    ('리퀴드 글래스', '다크 단색'),
    'midnight11': ('심야', '배경'),
    'sea14':      ('바다', '배경'),
    'forest15':   ('숲', '배경'),
    'city16':     ('야경', '기본'),
    'snow17':     ('설원', '배경'),
    'geo18':      ('도형', '배경'),
}

def _fam_of(t):
    """테마가 속한 계열과 변형 이름.

    quartet() 이 만든 테마는 자기가 들고 있고, 그 전 테마는 FAMILY 표에서 찾는다.
    표에도 없으면 혼자 계열이 된다.
    """
    if t.get('family'):
        return t['family'], t.get('variant', '기본')
    return FAMILY.get(t['key'], (t['name'], '기본'))


def families():
    """계열 순서대로 (계열이름, [테마...]) 를 돌려준다. THEMES 순서를 따른다."""
    order = {'basic': 0, 'image': 1, 'glow': 2, 'glow-image': 3,
             'light': 0, 'dark': 1, 'light-plain': 2, 'dark-plain': 3}
    out, seen = [], {}
    for t in THEMES:
        t['family'], t['variant'] = _fam_of(t)
        if t['family'] not in seen:
            seen[t['family']] = []
            out.append((t['family'], seen[t['family']]))
        seen[t['family']].append(t)
    # 계열 안은 늘 기본 → 배경 → 글로우 → 글로우+배경 순으로 읽히게 한다.
    # THEMES 에 붙은 순서대로 두면 계열마다 차례가 달라 비교가 안 된다.
    for _, members in out:
        members.sort(key=lambda t: order.get(file_slug(t).rsplit('-', 1)[-1]
                                             if file_slug(t).count('-') == 1
                                             else file_slug(t).split('-', 1)[1], 9))
    return out


# --- 분류 ----------------------------------------------------------------
# 계열이 열다섯이 되면서 격자 하나로는 훑어보기가 안 된다. 배경 그림이 무엇을
# 그리는지로 묶는다.
#
# 다른 축은 전부 막힌다. 색으로 나누면 먹빛 민트나 믹스드처럼 대표색이 없는
# 계열이 갈 곳이 없고, 단색/배경으로 나누면 네 벌 규칙과 축이 겹친다 —
# 모든 계열이 단색 변형을 하나씩 갖고 있어서 전부 같은 칸에 들어간다.
# 밝기로 나누는 것도 썸네일이 이미 말하는 것이라 줄만 늘어난다.
#
# 순서는 담백한 쪽에서 센 쪽으로 간다. 무늬는 색과 도형만 있고, 자연은 장면을
# 그리고, 불빛은 어둠 속에서 빛난다.
#
# '기타' 는 두지 않는다. 분류가 아니라 유보라서 아무도 열지 않는다.
# 어디에도 안 맞는 계열이 생기면 분류를 하나 더 만든다.
CATEGORIES = (
    ('무늬', '바탕에 색과 도형만. 담백한 쪽'),
    ('자연', '배경이 장면을 그린다'),
    ('불빛', '어두운 바탕에 인공 불빛'),
)

# 계열 이름 -> 분류. 새 계열을 더하면 여기에 한 줄 쓴다. 안 쓰면 생성이 멈춘다 —
# 조용히 맨 뒤로 빠지면 README 에서 통째로 사라진 것을 한참 뒤에 안다.
CATEGORY = {
    '먹빛 민트': '무늬',
    '크림 라떼': '무늬',
    '믹스드': '무늬',
    '캔디 팝': '무늬',
    '리퀴드 글래스': '무늬',
    '도형': '무늬',

    '벚꽃 그늘': '자연',
    '오로라': '자연',
    '심야': '자연',
    '바다': '자연',
    '숲': '자연',
    '설원': '자연',

    '야경': '불빛',
    '사이버펑크': '불빛',
    '레드': '불빛',
}


def categorized():
    """분류 순서대로 (분류, 설명, [(계열, [테마...]), ...]) 를 돌려준다.

    분류 안의 계열 순서는 THEMES 순서 그대로다. 분류가 생기면서 README 순서는
    '팔레트 표 순서' 에서 '분류 순 -> 그 안에서 팔레트 순' 으로 바뀌었다.
    """
    fams = families()
    names = [n for n, _ in fams]
    known = [n for n, _ in CATEGORIES]

    bad = sorted({c for c in CATEGORY.values() if c not in known})
    if bad:
        raise ValueError('CATEGORIES 에 없는 분류를 썼다: %s' % ', '.join(bad))
    missing = [n for n in names if n not in CATEGORY]
    if missing:
        raise ValueError('분류가 없는 계열: %s. CATEGORY 에 한 줄 쓴다 — '
                         '안 쓰면 README 목록에서 통째로 빠진다' % ', '.join(missing))
    stale = [n for n in CATEGORY if n not in names]
    if stale:
        raise ValueError('없는 계열이 CATEGORY 에 남아 있다: %s' % ', '.join(stale))
    # README 안에서 분류와 계열이 같은 앵커를 쓴다. 이름이 겹치면 링크가
    # 엉뚱한 자리로 뛴다.
    clash = [n for n in names if n in known]
    if clash:
        raise ValueError('계열 이름과 분류 이름이 같다: %s. README 앵커가 겹친다'
                         % ', '.join(clash))

    out = []
    for name, note in CATEGORIES:
        members = [(f, ms) for f, ms in fams if CATEGORY[f] == name]
        if not members:
            raise ValueError('%s 분류가 비었다. 넣을 계열이 생길 때 만든다 — '
                             '미리 만들면 README 에 빈 표가 나온다' % name)
        out.append((name, note, members))
    return out


# 네 벌의 이름표. 폰의 테마 목록에도 이대로 붙는다 — 넷을 나란히 깔았을 때
# 어느 것이 어느 것인지 목록에서 바로 구분돼야 한다.
TYPES = (
    ('기본', False, False),
    ('배경', True, False),
    ('글로우', False, True),
    ('글로우+배경', True, True),
)


def quartet(slug, no, family, palette, bg, notes, glow=('auto', 170, 8), keys=None):
    """테마 하나를 더할 때 네 벌을 함께 만든다.

        1 기본            2 기본 + 배경 이미지
        3 글로우          4 글로우 + 배경 이미지

    색을 한 벌 정하면 네 가지 인상이 나온다. 배경 없는 쪽은 담백하고 배경 있는 쪽은
    분위기가 있으며, 글로우는 같은 색이 떠 보인다. 고르는 사람마다 원하는 게 달라서
    하나만 내면 절반은 아쉬워한다.

    키는 slug + 번호로 넷을 연달아 쓴다(no, no+1, no+2, no+3).
    번호는 versionCode 에 쓰이므로 이미 쓴 번호와 겹치면 안 된다.
    keys 를 주면 그 키를 그대로 쓴다 — 이미 나간 테마를 네 벌 중 하나로 편입할 때 쓴다.
    키를 바꾸면 이미 깐 사람이 업데이트를 못 받는다.

    notes 는 네 벌의 한 줄 소개 — 길이 검사는 preview 가 한다.
    """
    if len(notes) != 4:
        raise ValueError('%s: 한 줄 소개를 네 개 줘야 한다' % slug)
    for k in ('chat_bg', 'main_bg', 'passcode_bg'):
        if k not in bg:
            raise ValueError('%s: bg 에 %s 가 없다' % (slug, k))

    out = []
    for i, (variant, use_bg, use_glow) in enumerate(TYPES):
        kw = dict(palette)
        if use_bg:
            kw.update(bg)
        else:
            kw.update(chat_bg=None, main_bg=None, passcode_bg=None)
        key = keys[i] if keys else '%s%d' % (slug, no + i)
        t = standard(key, '%s %s' % (family, variant), notes[i], **kw)
        if use_glow:
            t['glow'] = glow
        t['family'] = family
        t['variant'] = variant
        out.append(t)
    return out


# 야경 — 네 벌. city16 은 이미 나간 키라 그대로 두고 '배경' 자리에 넣는다.
THEMES += quartet(
    'city', 0, '야경',
    dict(bg='#0F1320', bg_deep='#080B14', surface='#191F32', pressed='#232B44',
         border='#2E3854', text='#E9EDF8', subtext='#8C96B2',
         accent='#FFD98A', accent_dim='#CFA55E', on_accent='#1E1605',
         send=('#FFC24D', '#FFC24D'), send_alt=('#FF6FA5', '#FF6FA5'),
         recv=('#2A3352', '#2A3352'), recv_alt=('#4FD1D9', '#4FD1D9'),
         send_text='#2A1C02', recv_text='#E9EDF8'),
    dict(chat_bg=('city', '#1A2340', '#3A4A72', dict(lit=0.28, dim=0.34)),
         main_bg=('city', '#161D36', '#2C3960', dict(lit=0.22, dim=0.48)),
         passcode_bg=('city', '#1E2748', '#4A5A88', dict(lit=0.40))),
    ['담백한 남색 바탕. 네온 네 색 말풍선',
     '창문 불빛이 켜진 도시가 깔림',
     '말풍선이 네온처럼 빛남',
     '도시 배경 위에 네온 말풍선까지'],
    keys=['city19', 'city16', 'city20', 'city21'])


# 사이버펑크 — 네 벌
THEMES += quartet(
    'cyber', 53, '사이버펑크',
    dict(bg='#0C0718', bg_deep='#05030E', surface='#170E28', pressed='#211536',
         border='#33204F', text='#EDE4FF', subtext='#9A8AC4',
         accent='#FF2E88', accent_dim='#C41E68', on_accent='#14000A',
         send=('#FF3D8B', '#FF3D8B'), send_alt=('#8A5BFF', '#8A5BFF'),
         recv=('#0E3E52', '#0E3E52'), recv_alt=('#1D2A66', '#1D2A66'),
         send_text='#1A0010', recv_text='#D8F6FF'),
    dict(chat_bg=('neon', '#1B0A2E', '#42104A',
                  dict(sun='#FF5FB0', sun_bottom='#FFC85C', glow='#FF2E88',
                       grid='#31E8FF', ground='#0A0514', horizon=0.50,
                       stars=60, dim=0.40)),
         main_bg=('neon', '#170826', '#3A0E42',
                  dict(sun='#FF5FB0', sun_bottom='#FFC85C', glow='#FF2E88',
                       grid='#31E8FF', ground='#08040F', horizon=0.44,
                       stars=40, dim=0.52)),
         passcode_bg=('neon', '#220D3A', '#55155A',
                      dict(sun='#FF6FBC', sun_bottom='#FFD27A', sun_r=0.32,
                           glow='#FF2E88', grid='#3BF0FF', ground='#0C0618',
                           horizon=0.56, stars=90, dim=0.06))),
    ['검붉은 보라 바탕. 마젠타·시안 네온 말풍선',
     '네온 격자와 가로로 잘린 해가 깔림',
     '말풍선이 간판처럼 빛남',
     '네온 격자 위에 빛나는 말풍선까지'])


# 레드 — 네 벌
THEMES += quartet(
    'red', 57, '레드',
    dict(bg='#160509', bg_deep='#0B0205', surface='#240A0F', pressed='#310D15',
         border='#4A121F', text='#FFECEF', subtext='#C08E96',
         accent='#FF1B3D', accent_dim='#C4122E', on_accent='#FFF2F4',
         send=('#E60026', '#E60026'), send_alt=('#FF5C7A', '#FF5C7A'),
         recv=('#3B0B16', '#3B0B16'), recv_alt=('#8E0F2E', '#8E0F2E'),
         send_text='#FFF2F4', recv_text='#FFE8EC'),
    dict(chat_bg=('ember', '#1A0207', '#5A0016',
                  dict(glow='#FF0033', spark='#FF6B85', smoke='#2E0410',
                       count=70, dim=0.30)),
         main_bg=('ember', '#150106', '#4A0012',
                  dict(glow='#E60030', spark='#FF5C7A', smoke='#280310',
                       count=50, dim=0.46)),
         passcode_bg=('ember', '#22030A', '#75001C',
                      dict(glow='#FF1B45', spark='#FF8DA0', smoke='#360616',
                           count=110, pool_alpha=150, dim=0.04))),
    ['검붉은 바탕에 새빨간 말풍선 네 칸',
     '어둠 속에서 붉은 불티가 떠오름',
     '말풍선이 빨갛게 달아오름',
     '불티 배경 위에 달아오른 빨강까지'])

# --- 배포 파일 이름 -------------------------------------------------------
# city21.ktheme 은 뭐가 뭔지 알 수 없다. 계열과 변형이 드러나게 바꾼다.
# 키(city21)는 그대로 둔다 — 안드로이드 패키지 이름과 versionCode 가 거기서 나오고,
# 그걸 바꾸면 이미 깐 사람이 업데이트를 못 받는다. 파일 이름만 따로 만든다.

VARIANT_SLUG = {
    '기본': 'basic',
    '배경': 'image',
    '글로우': 'glow',
    '글로우+배경': 'glow-image',
    '벚꽃 배경': 'image',
    '사탕 배경': 'image',
    '라이트': 'light',
    '다크': 'dark',
    '라이트 단색': 'light-plain',
    '다크 단색': 'dark-plain',
}


def _has_picture(t):
    """배경에 그림이 깔렸는지. 단색이나 세로 그라데이션은 그림이 아니다."""
    cb = t.get('chat_bg')
    return bool(cb) and cb[0] != 'linear'


# 옛 이름표도 뜻은 넷 중 하나다
_MEANS = {'기본': (False, False), '배경': (True, False),
          '글로우': (False, True), '글로우+배경': (True, True),
          '벚꽃 배경': (True, False), '사탕 배경': (True, False)}


def check_variants():
    """이름표가 실제 내용과 맞는지 본다.

    한 계열 안에서 이름만 다르고 내용이 같은 변형이 생기면 고르는 사람이
    무엇을 고른 건지 알 수 없다. 심야 배경이 글로우를 달고 있어서
    글로우+배경과 사실상 같은 테마였던 적이 있다 — 배경 그림까지 똑같았다.
    """
    for fam, members in families():
        seen = {}
        for t in members:
            want = _MEANS.get(t['variant'])
            got = (_has_picture(t), bool(t.get('glow')))
            if want and got != want:
                raise ValueError(
                    '%s(%s %s): 이름표는 그림=%s 글로우=%s 인데 실제는 그림=%s 글로우=%s'
                    % (t['key'], fam, t['variant'], want[0], want[1], got[0], got[1]))
            if want is None:
                continue          # 다른 축의 계열(리퀴드 글래스의 라이트/다크)
            if got in seen:
                raise ValueError('%s 계열의 "%s" 와 "%s" 가 내용이 같다 — 그림=%s 글로우=%s'
                                 % (fam, seen[got], t['variant'], got[0], got[1]))
            seen[got] = t['variant']


def file_slug(t):
    """배포 파일 이름. 예: city-glow-image

    URL 에 들어가므로 영문으로 쓴다. 한글은 퍼센트 인코딩돼서 링크가 지저분해진다.
    """
    fam, var = _fam_of(t)
    base = re.sub(r'\d+$', '', t['key'])            # city21 -> city
    tail = VARIANT_SLUG.get(var)
    if not tail:
        raise ValueError('%s: 변형 "%s" 의 파일 이름 조각이 VARIANT_SLUG 에 없다'
                         % (t['key'], var))
    return '%s-%s' % (base, tail)


def pkg_slug(t):
    """패키지 이름 / iOS 테마 ID 에 들어갈 조각. 예: city_glow_image

    파일 이름과 같은 말을 쓰되 하이픈을 밑줄로 바꾼다 —
    안드로이드 패키지 이름은 자바 식별자 규칙을 따라서 하이픈을 못 쓴다.

    키(city21)는 이제 versionCode 를 매기는 번호로만 쓴다. 겉으로 드러나지 않는다.
    """
    return file_slug(t).replace('-', '_')


# --- 계열 채우기 ----------------------------------------------------------

def fill_family(base_key, family, add, no, bg=None, glow=('auto', 170, 8)):
    """이미 있는 테마를 기준으로 계열의 빈 칸을 채운다.

    quartet() 은 색부터 새로 정할 때 쓰고, 이건 이미 나간 테마에 형제를 붙일 때 쓴다.
    바탕 테마의 말풍선 성격(그라데이션이냐 단색이냐)을 그대로 물려받는다 —
    계열 안에서 말풍선 재질이 제각각이면 같은 계열로 안 보인다.

    add 는 만들 변형 이름 목록. bg 를 주면 그걸 쓰고, 없으면 바탕 테마의 배경을 쓴다.
    """
    base = by_key(base_key)
    src_bg = bg or {k: base.get(k) for k in ('chat_bg', 'main_bg', 'passcode_bg')}
    if any(v for v in add if v in ('배경', '글로우+배경')) and not src_bg.get('chat_bg'):
        raise ValueError('%s: 배경 변형을 만들려면 bg 가 필요하다' % family)

    out = []
    for i, variant in enumerate(add):
        t = dict(base)
        t['key'] = '%s%d' % (re.sub(r'\d+$', '', base_key), no + i)
        t['name'] = '%s %s' % (family, variant)
        t['family'] = family
        t['variant'] = variant
        t['note'] = NOTES.get((family, variant), base['note'])
        if '배경' in variant:
            t.update(src_bg)
        else:
            t.update(chat_bg=None, main_bg=None, passcode_bg=None)
        if '글로우' in variant:
            t['glow'] = glow
        else:
            t.pop('glow', None)
        out.append(t)
    return out


# 변형마다 한 줄 소개를 따로 둔다. 같은 문장을 네 번 쓰면 목록에서 구분이 안 된다.
NOTES = {}


def set_notes(family, basic=None, image=None, glow=None, glow_image=None):
    for v, n in (('기본', basic), ('배경', image),
                 ('글로우', glow), ('글로우+배경', glow_image)):
        if n:
            NOTES[(family, v)] = n


# --- 계열을 네 벌로 채운다 ------------------------------------------------
# 리퀴드 글래스는 라이트/다크 축이라 예외로 둔다. 나머지 열두 계열을 채운다.
# 배경이 없던 계열에는 배경을 새로 지정한다.

set_notes('먹빛 민트',
          image='먹빛 위에 민트 빛 덩어리가 번짐',
          glow='말풍선이 민트와 보라로 빛남',
          glow_image='배경과 글로우를 함께')
THEMES += fill_family('inkmint01', '먹빛 민트', ['배경', '글로우', '글로우+배경'], 22,
                      bg=dict(
                          chat_bg=('blobs', '#101215', ['#4FD1B0', '#3D9BD9', '#8C6BE0']),
                          main_bg=('blobs', '#16181C', ['#2E9E85', '#2F6FB5']),
                          passcode_bg=('blobs', '#0C0E12', ['#4FD1B0', '#8C6BE0', '#3D9BD9'])))

set_notes('크림 라떼',
          image='크림빛 바탕에 둥근 도형이 겹침',
          glow='브라운 말풍선이 은은하게 빛남',
          glow_image='도형 배경에 빛나는 말풍선')
THEMES += fill_family('cream02', '크림 라떼', ['배경', '글로우', '글로우+배경'], 25,
                      bg=dict(
                          chat_bg=('geo', '#F7F2EA', '#EFE7DA',
                                   dict(count=7, alpha_lo=16, alpha_hi=34, blur=0.015,
                                        colors=['#B07A4B', '#D3A468', '#8B7B67'])),
                          main_bg=('geo', '#F7F2EA', '#F2ECE1',
                                   dict(count=5, alpha_lo=12, alpha_hi=26, blur=0.022,
                                        colors=['#B07A4B', '#D3A468'])),
                          passcode_bg=('geo', '#F2EADD', '#E4D8C4',
                                       dict(count=11, alpha_lo=28, alpha_hi=64,
                                            colors=['#B07A4B', '#D3A468', '#8B7B67']))))

set_notes('벚꽃 그늘',
          glow='분홍 말풍선이 빛남',
          glow_image='벚꽃 배경에 빛나는 말풍선')
THEMES += fill_family('sakura03', '벚꽃 그늘', ['글로우'], 28)
THEMES += fill_family('sakura13', '벚꽃 그늘', ['글로우+배경'], 29)

set_notes('믹스드',
          image='어두운 보라 위에 큰 도형이 겹침',
          glow_image='도형 배경에 네 색 말풍선이 빛남')
THEMES += fill_family('mixed04', '믹스드', ['배경', '글로우+배경'], 30,
                      bg=dict(
                          chat_bg=('geo', '#120F1C', '#1A1726',
                                   dict(count=8, alpha_lo=22, alpha_hi=46, blur=0.014,
                                        colors=['#FF8A5B', '#5BE0B4', '#7C6BE0', '#FFC24D'])),
                          main_bg=('geo', '#1A1726', '#221E32',
                                   dict(count=6, alpha_lo=16, alpha_hi=32, blur=0.02,
                                        colors=['#7C6BE0', '#FF8A5B'])),
                          passcode_bg=('geo', '#0E0C16', '#1E1A2C',
                                       dict(count=12, alpha_lo=34, alpha_hi=78,
                                            colors=['#FF8A5B', '#5BE0B4', '#7C6BE0']))))

set_notes('오로라',
          basic='오로라를 걷어낸 가장 어두운 바탕',
          glow='말풍선이 오로라 색으로 빛남',
          glow_image='오로라 배경에 빛나는 말풍선')
THEMES += fill_family('aurora05', '오로라', ['기본', '글로우', '글로우+배경'], 32)

set_notes('캔디 팝', glow_image='사탕 배경에 빛나는 말풍선')
THEMES += fill_family('candy12', '캔디 팝', ['글로우+배경'], 35)

set_notes('심야',
          basic='밤하늘을 걷어낸 남색 바탕',
          glow='말풍선이 달빛처럼 빛남',
          glow_image='밤하늘에 빛나는 말풍선')
THEMES += fill_family('midnight11', '심야', ['기본', '글로우', '글로우+배경'], 36)

set_notes('바다',
          basic='바다를 걷어낸 짙은 물빛 바탕',
          glow='산호와 물빛 말풍선이 빛남',
          glow_image='바다 배경에 빛나는 말풍선')
THEMES += fill_family('sea14', '바다', ['기본', '글로우', '글로우+배경'], 39)

set_notes('숲',
          basic='숲을 걷어낸 이끼빛 바탕',
          glow='이끼와 호박빛 말풍선이 빛남',
          glow_image='숲 배경에 빛나는 말풍선')
THEMES += fill_family('forest15', '숲', ['기본', '글로우', '글로우+배경'], 42)

set_notes('설원',
          basic='눈을 걷어낸 얼음빛 바탕',
          glow='파스텔 말풍선이 은은하게 빛남',
          glow_image='설원 배경에 빛나는 말풍선')
THEMES += fill_family('snow17', '설원', ['기본', '글로우', '글로우+배경'], 45)

set_notes('도형',
          basic='도형을 걷어낸 미색 바탕',
          glow='주황과 민트 말풍선이 빛남',
          glow_image='도형 배경에 빛나는 말풍선')
THEMES += fill_family('geo18', '도형', ['기본', '글로우', '글로우+배경'], 48)

check_variants()
