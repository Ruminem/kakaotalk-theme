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

VERSION = '0.14'

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
        recv=('#FFFFFF', '#E6EDF7'), recv_alt=('#F3F7FF', '#DCE6F4'),
        send_text='#0B2D50', recv_text='#1F2733',
        bubble_style='glass', bubble_alpha=165, cell_alpha=0.55,
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
        glow=('#8AA4FF', 130, 8),
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


_add_variant('mixed04', 'mixed09', '믹스드 v2',
             '믹스드에 글로우를 얹은 것. 말풍선마다 자기 색으로 빛남',
             glow=('auto', 190, 8))
_add_variant('candy06', 'candy10', '캔디 팝 v2',
             '캔디 팝에 글로우를 얹은 것. 밝은 바탕이라 빛이 은은하게 걸림',
             glow=('auto', 175, 8))

_add_variant('candy10', 'candy12', '캔디 팝 v3',
             '캔디 팝 v2 에 사탕을 흩뿌린 배경을 깔았음',
             chat_bg=('candy', '#FFFDF5', '#FFE9D6',
                      dict(count=22, sprinkles=70, dim=0.42)),
             main_bg=('candy', '#FFFDF5', '#FFF1E2',
                      dict(count=16, sprinkles=50, dim=0.55)),
             passcode_bg=('candy', '#FFF8E8', '#FFD9C0',
                          dict(count=34, sprinkles=110, dim=0.12)))
_add_variant('sakura03', 'sakura13', '벚꽃 그늘 v2',
             '벚꽃 그늘에 가지와 꽃잎을 그려 넣었음',
             chat_bg=('sakura', '#FFF3F6', '#FBE2EC',
                      dict(flowers=16, petals=30, bokeh=12, branch=False, dim=0.38)),
             main_bg=('sakura', '#FFF6F8', '#FCE8F0',
                      dict(flowers=10, petals=22, bokeh=10, branch=False, dim=0.52)),
             passcode_bg=('sakura', '#FFF0F5', '#F8D3E2',
                          dict(flowers=30, petals=46, bokeh=18, branch=True, dim=0.0)))
