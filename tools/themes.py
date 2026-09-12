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

chat_bg
  None 이면 단색. ('linear', 위, 아래) 또는 ('aurora', 바탕, [색...]) 이면 이미지를 그린다.
"""

VERSION = '0.3'

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
        send=('#FFD166', '#FF9F68'), send_alt=('#8AE0C0', '#4FC3D9'),
        recv=('#C2A7FF', '#FF9BC6'), recv_alt=('#9BD6FF', '#7ED7C1'),
        send_text='#4A2E10', recv_text='#3A2440',
        chat_bg=('linear', '#FFFDF5', '#FFE9D6'),
    ),
]


def by_key(key):
    for t in THEMES:
        if t['key'] == key:
            return t
    raise KeyError(key)
