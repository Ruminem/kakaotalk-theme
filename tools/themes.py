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

VERSION = '0.30'

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
    # --- 원목 글래스 ------------------------------------------------------
    # 유리는 뒤에 볼 것이 있어야 유리로 읽힌다. 색 덩어리는 저주파라 비쳐도 색만
    # 보이는데, 나무결은 선이 있어서 반투명이라는 게 눈에 드러난다.
    # 계열 축은 밝기(오크/월넛) × 배경 유무다. 글로우는 넣지 않는다 —
    # 난색 중명도 바탕에서는 빛이 번질 자리가 없어 뿌연 테두리로만 보인다.
    dict(
        key='wood61', name='원목 글래스 오크',
        note='밝은 참나무 결 위에 반투명 유리 말풍선',
        bg='#E9DAC0', bg_deep='#DCC9A8', surface='#F7EFE1', pressed='#E2D0B2',
        border='#CBB794', text='#3A2C1C', subtext='#7C6A50',
        accent='#B5713A', accent_dim='#8C5427', on_accent='#FFF6EA',
        send=('#E0A45F', '#E0A45F'), send_alt=('#C2803F', '#C2803F'),
        recv=('#FFF6E8', '#FFF6E8'), recv_alt=('#EDDCC0', '#EDDCC0'),
        send_text='#3A2208', recv_text='#3A2C1C',
        bubble_style='glass', bubble_alpha=155, cell_alpha=0.55,
        flat_list=False,
        chat_bg=('wood', '#E8D4B4', '#D8BF98',
                 dict(dark='#7A4E24', light='#FFF3E0', knots=2, planks=3)),
        main_bg=('wood', '#E8D4B4', '#DCC6A2',
                 dict(dark='#7A4E24', light='#FFF3E0', knots=0, planks=0, figure=False)),
        passcode_bg=('wood', '#E3CDA9', '#CFB287',
                     dict(dark='#6E4520', light='#FFF3E0', knots=3, planks=4)),
    ),
    dict(
        key='wood62', name='원목 글래스 오크 단색',
        note='결 없이 나무색 바탕. 유리만 남김',
        bg='#E4D3B6', bg_deep='#D6C29E', surface='#F4EADA', pressed='#DECBAA',
        border='#C6B08B', text='#3A2C1C', subtext='#7C6A50',
        accent='#B5713A', accent_dim='#8C5427', on_accent='#FFF6EA',
        send=('#E0A45F', '#E0A45F'), send_alt=('#C2803F', '#C2803F'),
        recv=('#FFF6E8', '#FFF6E8'), recv_alt=('#EDDCC0', '#EDDCC0'),
        send_text='#3A2208', recv_text='#3A2C1C',
        bubble_style='glass', bubble_alpha=150, cell_alpha=0.55,
        chat_bg=None, main_bg=None, passcode_bg=None,
    ),
    dict(
        key='wood63', name='원목 글래스 월넛',
        note='짙은 호두나무. 결이 유리 너머로 비침',
        bg='#2A1E15', bg_deep='#1B120B', surface='#3A2A1D', pressed='#4A3626',
        border='#59422E', text='#F3E7D8', subtext='#B39C82',
        accent='#E0A860', accent_dim='#B07F3F', on_accent='#241505',
        send=('#8A5A2E', '#8A5A2E'), send_alt=('#A9743C', '#A9743C'),
        recv=('#3F2F22', '#3F2F22'), recv_alt=('#5A4330', '#5A4330'),
        send_text='#FFF3E2', recv_text='#F3E7D8',
        bubble_style='glass', bubble_alpha=175, cell_alpha=0.55,
        flat_list=False,
        chat_bg=('wood', '#3C2C1E', '#261A11',
                 dict(dark='#120A05', light='#C08F57', knots=2, planks=3)),
        main_bg=('wood', '#38281B', '#241810',
                 dict(dark='#120A05', light='#C08F57', knots=0, planks=0, figure=False)),
        passcode_bg=('wood', '#42301F', '#1E1409',
                     dict(dark='#0E0704', light='#CE9A5E', knots=3, planks=4)),
    ),
    dict(
        key='wood64', name='원목 글래스 월넛 단색',
        note='어두운 나무색 바탕에 유리만',
        bg='#2E2118', bg_deep='#1F150D', surface='#3E2E20', pressed='#4E3929',
        border='#5C4530', text='#F3E7D8', subtext='#B39C82',
        accent='#E0A860', accent_dim='#B07F3F', on_accent='#241505',
        send=('#8A5A2E', '#8A5A2E'), send_alt=('#A9743C', '#A9743C'),
        recv=('#3F2F22', '#3F2F22'), recv_alt=('#5A4330', '#5A4330'),
        send_text='#FFF3E2', recv_text='#F3E7D8',
        bubble_style='glass', bubble_alpha=170, cell_alpha=0.55,
        chat_bg=None, main_bg=None, passcode_bg=None,
    ),
    # --- 고요 -------------------------------------------------------------
    # 차분의 두 번째 벌. 기준은 차분과 같다(채도 0.25 근처, 순백·순흑 없음,
    # 글로우·배경 그림 없음). 차분이 무채색에 가까운 중성색이었다면 여기는
    # 색 이름이 하나씩 붙는 쪽이다 — 올리브, 안개, 자두, 먹.
    dict(
        key='calm81', name='고요 올리브',
        note='누런 풀빛 회색. 밝고 흙내 나는 쪽',
        bg='#ECEBE2', bg_deep='#E2E1D6', surface='#F5F4EE', pressed='#DFDED2',
        border='#D3D2C4', text='#34352B', subtext='#72735F',
        accent='#7A785C', accent_dim='#5F5D47', on_accent='#F7F7F2',
        send=('#CFCDB2', '#CFCDB2'), send_alt=('#E0DFCB', '#E0DFCB'),
        recv=('#FAFAF6', '#FAFAF6'), recv_alt=('#E6E5DA', '#E6E5DA'),
        send_text='#2C2D23', recv_text='#34352B',
        flat=True, chat_bg=None, main_bg=None, passcode_bg=None,
    ),
    dict(
        key='calm82', name='고요 안개',
        note='보랏빛 도는 옅은 회색. 밝고 서늘한 쪽',
        bg='#ECEBF0', bg_deep='#E2E1E8', surface='#F5F4F8', pressed='#DEDCE5',
        border='#D3D1DC', text='#33323A', subtext='#747280',
        accent='#7B7494', accent_dim='#605A76', on_accent='#F7F6FA',
        send=('#CFCBDC', '#CFCBDC'), send_alt=('#E0DDE8', '#E0DDE8'),
        recv=('#FAFAFC', '#FAFAFC'), recv_alt=('#E6E4EC', '#E6E4EC'),
        send_text='#2B2A32', recv_text='#33323A',
        flat=True, chat_bg=None, main_bg=None, passcode_bg=None,
    ),
    dict(
        key='calm83', name='고요 자두',
        note='탁한 자줏빛. 어둡고 부드러운 쪽',
        bg='#27222A', bg_deep='#1E1A21', surface='#312B34', pressed='#3B343E',
        border='#443C47', text='#E6DEE8', subtext='#9C92A0',
        accent='#A38CA8', accent_dim='#806C85', on_accent='#1C171E',
        send=('#4A3D4E', '#4A3D4E'), send_alt=('#57495B', '#57495B'),
        recv=('#332C36', '#332C36'), recv_alt=('#3E3641', '#3E3641'),
        send_text='#EEE6F0', recv_text='#E6DEE8',
        flat=True, chat_bg=None, main_bg=None, passcode_bg=None,
    ),
    dict(
        key='calm84', name='고요 먹',
        note='색을 거의 뺀 먹빛. 가장 어둡고 조용함',
        bg='#1F1F21', bg_deep='#18181A', surface='#29292C', pressed='#333336',
        border='#3C3C40', text='#DEDEE0', subtext='#929296',
        accent='#9A9AA2', accent_dim='#78787F', on_accent='#161618',
        send=('#3F3F44', '#3F3F44'), send_alt=('#4B4B50', '#4B4B50'),
        recv=('#2C2C30', '#2C2C30'), recv_alt=('#37373B', '#37373B'),
        send_text='#E6E6E8', recv_text='#DEDEE0',
        flat=True, chat_bg=None, main_bg=None, passcode_bg=None,
    ),

    # --- 스테인드 글래스 --------------------------------------------------
    # 색 유리. 계열 축이 밝기가 아니라 색이라 네 벌이 곧 네 가지 색이다.
    # 바탕은 넷 다 같은 어두운 회보라로 두고 색만 바꾼다 — 납선에 끼운 색유리처럼
    # 색이 유리에서만 나오게 하려는 것이다.
    # 배경은 납선으로 이은 유리 조각이다(scenes.stained). 한때 흐린 색 덩어리였는데
    # 이름만 스테인드 글래스고 조각도 납선도 없어서 어두운 그라데이션으로만 보였다.
    # 유리색은 명도가 다른 같은 계열로 고른다. 옅은 노랑이나 산호색을 섞으면
    # 어둡게 눌렀을 때 카키와 갈색이 되어 흙탕물처럼 탁해진다.
    dict(
        key='stained65', name='스테인드 글래스 앰버',
        note='납선으로 이은 호박색 유리창. 등불이 뒤에서 비침',
        bg='#141218', bg_deep='#0C0A0F', surface='#1E1A24', pressed='#282232',
        border='#342C40', text='#F2ECE2', subtext='#A99C8C',
        accent='#FFB23F', accent_dim='#C8862A', on_accent='#2A1A02',
        send=('#E08A2A', '#E08A2A'), send_alt=('#FFC768', '#FFC768'),
        recv=('#3A2A16', '#3A2A16'), recv_alt=('#5E4420', '#5E4420'),
        send_text='#2A1A02', recv_text='#F2ECE2',
        bubble_style='glass', bubble_alpha=170, cell_alpha=0.55,
        chat_bg=('stained', '#0B0A0D', ['#E8871E', '#FFA62B', '#C2521B', '#8E2A12', '#FFB02E'], dict(dim=0.25)),
        main_bg=('stained', '#0B0A0D', ['#E8871E', '#FFA62B', '#C2521B', '#8E2A12', '#FFB02E'], dict(dim=0.35)),
        passcode_bg=('stained', '#0B0A0D', ['#E8871E', '#FFA62B', '#C2521B', '#8E2A12', '#FFB02E'], dict(dim=0.1, cols=5)),
    ),
    dict(
        key='stained66', name='스테인드 글래스 에메랄드',
        note='초록 유리창. 가장 차분한 쪽',
        bg='#141218', bg_deep='#0C0A0F', surface='#1E1A24', pressed='#282232',
        border='#342C40', text='#E6F2EC', subtext='#95AEA4',
        accent='#3FD9A0', accent_dim='#27A87A', on_accent='#04241A',
        send=('#1FA97A', '#1FA97A'), send_alt=('#6FE8BE', '#6FE8BE'),
        recv=('#123028', '#123028'), recv_alt=('#1D4A3C', '#1D4A3C'),
        send_text='#04241A', recv_text='#E6F2EC',
        bubble_style='glass', bubble_alpha=170, cell_alpha=0.55,
        chat_bg=('stained', '#0B0A0D', ['#1FA97A', '#0E7A56', '#3FD9A0', '#0A5A48', '#5FC8B0'], dict(dim=0.25)),
        main_bg=('stained', '#0B0A0D', ['#1FA97A', '#0E7A56', '#3FD9A0', '#0A5A48', '#5FC8B0'], dict(dim=0.35)),
        passcode_bg=('stained', '#0B0A0D', ['#1FA97A', '#0E7A56', '#3FD9A0', '#0A5A48', '#5FC8B0'], dict(dim=0.1, cols=5)),
    ),
    dict(
        key='stained67', name='스테인드 글래스 자수정',
        note='보라 유리창. 어두운 쪽으로 가장 깊음',
        bg='#141218', bg_deep='#0C0A0F', surface='#1E1A24', pressed='#282232',
        border='#342C40', text='#EFE8F8', subtext='#A498B8',
        accent='#B07CFF', accent_dim='#8552D6', on_accent='#1A0A33',
        send=('#8A56E0', '#8A56E0'), send_alt=('#C79BFF', '#C79BFF'),
        recv=('#2A1F42', '#2A1F42'), recv_alt=('#3F2F63', '#3F2F63'),
        send_text='#F3ECFF', recv_text='#EFE8F8',
        bubble_style='glass', bubble_alpha=170, cell_alpha=0.55,
        chat_bg=('stained', '#0B0A0D', ['#8A56E0', '#5E32B0', '#B07CFF', '#3F2380', '#C06AD8'], dict(dim=0.25)),
        main_bg=('stained', '#0B0A0D', ['#8A56E0', '#5E32B0', '#B07CFF', '#3F2380', '#C06AD8'], dict(dim=0.35)),
        passcode_bg=('stained', '#0B0A0D', ['#8A56E0', '#5E32B0', '#B07CFF', '#3F2380', '#C06AD8'], dict(dim=0.1, cols=5)),
    ),
    dict(
        key='stained68', name='스테인드 글래스 로즈',
        note='분홍 유리창. 가장 따뜻한 쪽',
        bg='#141218', bg_deep='#0C0A0F', surface='#1E1A24', pressed='#282232',
        border='#342C40', text='#F8E9EF', subtext='#B8969F',
        accent='#FF6F9C', accent_dim='#D14670', on_accent='#330A1B',
        send=('#E04A79', '#E04A79'), send_alt=('#FF92B4', '#FF92B4'),
        recv=('#3A1A28', '#3A1A28'), recv_alt=('#5A2A3E', '#5A2A3E'),
        send_text='#FFF0F5', recv_text='#F8E9EF',
        bubble_style='glass', bubble_alpha=170, cell_alpha=0.55,
        chat_bg=('stained', '#0B0A0D', ['#E04A79', '#B02E5A', '#FF6F9C', '#7A1A3E', '#D9408F'], dict(dim=0.25)),
        main_bg=('stained', '#0B0A0D', ['#E04A79', '#B02E5A', '#FF6F9C', '#7A1A3E', '#D9408F'], dict(dim=0.35)),
        passcode_bg=('stained', '#0B0A0D', ['#E04A79', '#B02E5A', '#FF6F9C', '#7A1A3E', '#D9408F'], dict(dim=0.1, cols=5)),
    ),

    # --- 프리즘 글래스 ----------------------------------------------------
    # 유리 모서리에서 빛이 파장별로 꺾여 갈라지는 것. 위 테두리는 시안,
    # 아래 테두리는 마젠타로 준다(`rim`). 지금까지 테두리는 흰 선과 검은 선뿐이었다.
    dict(
        key='prism69', name='프리즘 글래스 라이트',
        note='맑은 바탕. 말풍선 테두리가 무지개로 갈라짐',
        bg='#EEF1F7', bg_deep='#E2E7F0', surface='#FFFFFF', pressed='#DCE3EE',
        border='#CED6E4', text='#1E2430', subtext='#6B7688',
        accent='#3A7BF0', accent_dim='#2659C0', on_accent='#FFFFFF',
        send=('#9FC8FF', '#9FC8FF'), send_alt=('#C3B6FF', '#C3B6FF'),
        recv=('#FFFFFF', '#FFFFFF'), recv_alt=('#E8F0FF', '#E8F0FF'),
        send_text='#0E2648', recv_text='#1E2430',
        bubble_style='glass', bubble_alpha=150, cell_alpha=0.55,
        rim=('#5FE8FF', '#FF5FC8'),
        chat_bg=('blobs', '#EDF1F8', ['#9BD4FF', '#C9B6FF', '#9BF0DC', '#FFC8E4']),
        main_bg=('blobs', '#F1F4FA', ['#BFE2FF', '#DCD0FF', '#C4F3E6', '#FFD9EC']),
        passcode_bg=('blobs', '#E9EEF8', ['#8AC8FF', '#B9A6FF', '#8AE8D2', '#FFB8DC']),
    ),
    dict(
        key='prism70', name='프리즘 글래스 다크',
        note='어두운 바탕. 갈라진 테두리가 더 또렷함',
        bg='#101218', bg_deep='#0A0C11', surface='#191D26', pressed='#222733',
        border='#2C3341', text='#E9EEF8', subtext='#8C97A9',
        accent='#5AB5FF', accent_dim='#3789CC', on_accent='#06192B',
        send=('#3E6FC9', '#3E6FC9'), send_alt=('#6A4FB0', '#6A4FB0'),
        recv=('#2A3140', '#2A3140'), recv_alt=('#3A4356', '#3A4356'),
        send_text='#EAF4FF', recv_text='#E9EEF8',
        bubble_style='glass', bubble_alpha=175, cell_alpha=0.55,
        rim=('#5FE8FF', '#FF5FC8'),
        chat_bg=('blobs', '#0B0E14', ['#2F6FB5', '#6A4FB0', '#2E8C7E', '#B0487F']),
        main_bg=('blobs', '#10131A', ['#27568C', '#4E3C86', '#256B61', '#8A3A64']),
        passcode_bg=('blobs', '#0D1017', ['#3A80CC', '#7A5CC8', '#35A091', '#C8508F']),
    ),
    dict(
        key='prism71', name='프리즘 글래스 라이트 단색',
        note='배경 없이 갈라진 테두리만 남김',
        bg='#E7ECF5', bg_deep='#DAE1EC', surface='#F8FAFD', pressed='#D4DCEA',
        border='#C6CFDF', text='#1E2430', subtext='#6B7688',
        accent='#3A7BF0', accent_dim='#2659C0', on_accent='#FFFFFF',
        send=('#9FC8FF', '#9FC8FF'), send_alt=('#C3B6FF', '#C3B6FF'),
        recv=('#FFFFFF', '#FFFFFF'), recv_alt=('#E8F0FF', '#E8F0FF'),
        send_text='#0E2648', recv_text='#1E2430',
        bubble_style='glass', bubble_alpha=145, cell_alpha=0.55,
        rim=('#5FE8FF', '#FF5FC8'),
        chat_bg=None, main_bg=None, passcode_bg=None,
    ),
    dict(
        key='prism72', name='프리즘 글래스 다크 단색',
        note='어두운 바탕에 갈라진 테두리만',
        bg='#14171F', bg_deep='#0D1016', surface='#1D222C', pressed='#262C38',
        border='#313949', text='#E9EEF8', subtext='#8C97A9',
        accent='#5AB5FF', accent_dim='#3789CC', on_accent='#06192B',
        send=('#3E6FC9', '#3E6FC9'), send_alt=('#6A4FB0', '#6A4FB0'),
        recv=('#2A3140', '#2A3140'), recv_alt=('#3A4356', '#3A4356'),
        send_text='#EAF4FF', recv_text='#E9EEF8',
        bubble_style='glass', bubble_alpha=170, cell_alpha=0.55,
        rim=('#5FE8FF', '#FF5FC8'),
        chat_bg=None, main_bg=None, passcode_bg=None,
    ),

    # --- 프로스트 글래스 --------------------------------------------------
    # 젖빛. 진짜 젖빛 유리는 뒤를 흐리게 하는데 우리는 PNG 한 장만 줄 수 있어서
    # 그건 안 된다. 대신 유리 안에 알갱이를 뿌려 표면이 거칠어 보이게 하고,
    # 알파를 더 낮춰 뒤가 더 많이 비치게 한다.
    dict(
        key='frost73', name='프로스트 글래스 라이트',
        note='젖빛 유리. 알갱이가 도는 뿌연 말풍선',
        bg='#EFF1F4', bg_deep='#E3E6EB', surface='#FAFBFD', pressed='#DDE2E9',
        border='#CFD5DE', text='#232830', subtext='#6E7682',
        accent='#5B8DB8', accent_dim='#3F6B90', on_accent='#FFFFFF',
        send=('#BBD6EA', '#BBD6EA'), send_alt=('#CFE2F0', '#CFE2F0'),
        recv=('#FFFFFF', '#FFFFFF'), recv_alt=('#EDF2F7', '#EDF2F7'),
        send_text='#1B3448', recv_text='#232830',
        bubble_style='glass', bubble_alpha=135, cell_alpha=0.55, frost=0.45,
        chat_bg=('blobs', '#EEF1F5', ['#AFCFE6', '#C6D8E8', '#D8E6EE', '#BFD6E2']),
        main_bg=('blobs', '#F1F3F6', ['#C4DAEA', '#D2E0EC', '#E0EAF0', '#CCDDE8']),
        passcode_bg=('blobs', '#E9EDF2', ['#9FC4DE', '#BAD2E4', '#CFE0EA', '#AECBE0']),
    ),
    dict(
        key='frost74', name='프로스트 글래스 다크',
        note='어두운 젖빛. 알갱이가 빛을 물고 있음',
        bg='#14171B', bg_deep='#0E1013', surface='#1D2126', pressed='#262B31',
        border='#313740', text='#E8ECF1', subtext='#8B939E',
        accent='#7FB3D5', accent_dim='#54809E', on_accent='#0A1A24',
        send=('#3D586E', '#3D586E'), send_alt=('#4E6B82', '#4E6B82'),
        recv=('#2A3038', '#2A3038'), recv_alt=('#39414B', '#39414B'),
        send_text='#EAF2F8', recv_text='#E8ECF1',
        bubble_style='glass', bubble_alpha=160, cell_alpha=0.55, frost=0.45,
        chat_bg=('blobs', '#0F1215', ['#3A5A72', '#4A6A80', '#2C4454', '#5E8098']),
        main_bg=('blobs', '#121519', ['#32505F', '#40606F', '#263A48', '#4E6E82']),
        passcode_bg=('blobs', '#0D1013', ['#456A82', '#56798F', '#314C5C', '#6E90A8']),
    ),
    dict(
        key='frost75', name='프로스트 글래스 라이트 단색',
        note='배경 없이 젖빛 말풍선만',
        bg='#E9ECF0', bg_deep='#DDE1E7', surface='#F7F9FB', pressed='#D6DCE4',
        border='#C8CFD9', text='#232830', subtext='#6E7682',
        accent='#5B8DB8', accent_dim='#3F6B90', on_accent='#FFFFFF',
        send=('#BBD6EA', '#BBD6EA'), send_alt=('#CFE2F0', '#CFE2F0'),
        recv=('#FFFFFF', '#FFFFFF'), recv_alt=('#EDF2F7', '#EDF2F7'),
        send_text='#1B3448', recv_text='#232830',
        bubble_style='glass', bubble_alpha=130, cell_alpha=0.55, frost=0.45,
        chat_bg=None, main_bg=None, passcode_bg=None,
    ),
    dict(
        key='frost76', name='프로스트 글래스 다크 단색',
        note='어두운 바탕에 젖빛 말풍선만',
        bg='#171A1F', bg_deep='#101317', surface='#20242A', pressed='#2A2F36',
        border='#353C45', text='#E8ECF1', subtext='#8B939E',
        accent='#7FB3D5', accent_dim='#54809E', on_accent='#0A1A24',
        send=('#3D586E', '#3D586E'), send_alt=('#4E6B82', '#4E6B82'),
        recv=('#2A3038', '#2A3038'), recv_alt=('#39414B', '#39414B'),
        send_text='#EAF2F8', recv_text='#E8ECF1',
        bubble_style='glass', bubble_alpha=155, cell_alpha=0.55, frost=0.45,
        chat_bg=None, main_bg=None, passcode_bg=None,
    ),
    # --- 차분 -------------------------------------------------------------
    # 오래 봐도 눈이 덜 피로한 쪽. 지금까지 만든 것들이 대체로 채도가 높아서
    # 반대쪽 자리가 비어 있었다. 네 벌 규칙의 축(배경/글로우) 대신 색이 축이다 —
    # 글로우와 배경 그림은 이 계열의 목적과 정면으로 어긋나서 아예 안 쓴다.
    #
    # 숫자로 잡은 기준이 셋이다.
    #   채도 0.25 아래       — 레드가 1.00, 캔디 팝이 0.60 이다
    #   바탕↔말풍선 대비 1.2~2.0 — 말풍선이 구분되면서 경계가 튀지 않는 구간
    #   순백·순흑을 안 쓴다   — #FFF 와 #000 은 그 자체로 눈이 아프다
    dict(
        key='calm77', name='차분 세이지',
        note='탁한 연둣빛 회색. 가장 순한 쪽',
        bg='#EDEFE9', bg_deep='#E3E6DE', surface='#F6F7F3', pressed='#E0E4DA',
        border='#D5D9CE', text='#333A32', subtext='#6E756B',
        accent='#6E8A6A', accent_dim='#566E53', on_accent='#F6F8F4',
        send=('#C7D3C0', '#C7D3C0'), send_alt=('#DCE3D6', '#DCE3D6'),
        recv=('#FBFCF9', '#FBFCF9'), recv_alt=('#E6E9E1', '#E6E9E1'),
        send_text='#252A24', recv_text='#333A32',
        flat=True, chat_bg=None, main_bg=None, passcode_bg=None,
    ),
    dict(
        key='calm78', name='차분 샌드',
        note='누런 기 도는 종이색. 따뜻한 쪽',
        bg='#F1EDE6', bg_deep='#E7E2D9', surface='#F9F6F1', pressed='#E4DED3',
        border='#D9D2C6', text='#3A342D', subtext='#787066',
        accent='#A8845C', accent_dim='#876848', on_accent='#FBF8F3',
        send=('#DCD0BE', '#DCD0BE'), send_alt=('#EBE3D6', '#EBE3D6'),
        recv=('#FDFBF7', '#FDFBF7'), recv_alt=('#EDE8E0', '#EDE8E0'),
        send_text='#2B261F', recv_text='#3A342D',
        flat=True, chat_bg=None, main_bg=None, passcode_bg=None,
    ),
    dict(
        key='calm79', name='차분 슬레이트',
        note='푸른 기 도는 회색. 어두운 쪽',
        bg='#22262B', bg_deep='#1A1D21', surface='#2B3036', pressed='#343A41',
        border='#3C434B', text='#DCE0E4', subtext='#8E969E',
        accent='#7E97A8', accent_dim='#5E7686', on_accent='#151A1E',
        send=('#3C4750', '#3C4750'), send_alt=('#4A555E', '#4A555E'),
        recv=('#2E343A', '#2E343A'), recv_alt=('#394046', '#394046'),
        send_text='#E4E9ED', recv_text='#DCE0E4',
        flat=True, chat_bg=None, main_bg=None, passcode_bg=None,
    ),
    dict(
        key='calm80', name='차분 모카',
        note='탁한 갈회색. 어둡고 따뜻한 쪽',
        bg='#262220', bg_deep='#1D1A18', surface='#302B28', pressed='#3A3431',
        border='#433C38', text='#E4DCD5', subtext='#9A9088',
        accent='#A18A78', accent_dim='#7E6B5C', on_accent='#1A1614',
        send=('#473D37', '#473D37'), send_alt=('#544840', '#544840'),
        recv=('#322C29', '#322C29'), recv_alt=('#3D3632', '#3D3632'),
        send_text='#EDE6DF', recv_text='#E4DCD5',
        flat=True, chat_bg=None, main_bg=None, passcode_bg=None,
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
    'calm77':     ('차분', '세이지'),
    'calm78':     ('차분', '샌드'),
    'calm79':     ('차분', '슬레이트'),
    'calm80':     ('차분', '모카'),
    'calm81':     ('고요', '올리브'),
    'calm82':     ('고요', '안개'),
    'calm83':     ('고요', '자두'),
    'calm84':     ('고요', '먹'),
    'stained65':  ('스테인드 글래스', '앰버'),
    'stained66':  ('스테인드 글래스', '에메랄드'),
    'stained67':  ('스테인드 글래스', '자수정'),
    'stained68':  ('스테인드 글래스', '로즈'),
    'prism69':    ('프리즘 글래스', '라이트'),
    'prism70':    ('프리즘 글래스', '다크'),
    'prism71':    ('프리즘 글래스', '라이트 단색'),
    'prism72':    ('프리즘 글래스', '다크 단색'),
    'frost73':    ('프로스트 글래스', '라이트'),
    'frost74':    ('프로스트 글래스', '다크'),
    'frost75':    ('프로스트 글래스', '라이트 단색'),
    'frost76':    ('프로스트 글래스', '다크 단색'),
    'wood61':     ('원목 글래스', '오크'),
    'wood62':     ('원목 글래스', '오크 단색'),
    'wood63':     ('원목 글래스', '월넛'),
    'wood64':     ('원목 글래스', '월넛 단색'),
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
             'light': 0, 'dark': 1, 'light-plain': 2, 'dark-plain': 3,
             'oak': 0, 'walnut': 1, 'oak-plain': 2, 'walnut-plain': 3,
             'amber': 0, 'emerald': 1, 'amethyst': 2, 'rose': 3,
             'sage': 0, 'sand': 1, 'slate': 2, 'mocha': 3,
             'olive': 0, 'fog': 1, 'plum': 2, 'ink': 3,
             'light-image': 0.5, 'dark-image': 1.5,
             'double': 0, 'sign': 1, 'electrode': 2, 'speech': 3}
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
    ('유리', '말풍선이 반투명하다'),
    ('자연', '배경이 장면을 그린다'),
    ('불빛', '어두운 바탕에 인공 불빛'),
    ('캐릭터', '말풍선 모양과 캐릭터 프로필'),
)

# 분류 -> 분류 문서 파일 이름(docs/themes/<이름>.md). 영문으로 쓴다 — 한글 파일 이름은
# 주소에서 %EB%AC%B4 처럼 깨져 보인다. 분류를 더하면 여기에도 한 줄 쓴다. 안 쓰면 생성이 멈춘다.
CATEGORY_FILE = {
    '무늬': 'pattern',
    '유리': 'glass',
    '자연': 'nature',
    '불빛': 'lights',
    '캐릭터': 'character',
}

# 계열 이름 -> 분류. 새 계열을 더하면 여기에 한 줄 쓴다. 안 쓰면 생성이 멈춘다 —
# 조용히 맨 뒤로 빠지면 README 에서 통째로 사라진 것을 한참 뒤에 안다.
CATEGORY = {
    '먹빛 민트': '무늬',
    '크림 라떼': '무늬',
    '믹스드': '무늬',
    '캔디 팝': '무늬',
    '리퀴드 글래스': '유리',
    '원목 글래스': '유리',
    '스테인드 글래스': '유리',
    '프리즘 글래스': '유리',
    '프로스트 글래스': '유리',
    '도형': '무늬',
    '차분': '무늬',
    '고요': '무늬',

    '벚꽃 그늘': '자연',
    '오로라': '자연',
    '심야': '자연',
    '바다': '자연',
    '숲': '자연',
    '설원': '자연',

    '야경': '불빛',
    '사이버펑크': '불빛',
    '레드': '불빛',
    '불꽃놀이': '불빛',
    '연등': '불빛',
    '알전구': '불빛',
    '고속도로': '불빛',
    '터미널': '불빛',
    '네온사인': '불빛',

    '우체국': '캐릭터',
    '책상': '캐릭터',
    '오락실': '캐릭터',
    '빨래': '캐릭터',
    '영화관': '캐릭터',
    '빵집': '캐릭터',
    '캠핑': '캐릭터',
    '우주': '캐릭터',
    '온실': '캐릭터',
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
    '세이지': 'sage',
    '샌드': 'sand',
    '슬레이트': 'slate',
    '모카': 'mocha',
    '올리브': 'olive',
    '안개': 'fog',
    '자두': 'plum',
    '먹': 'ink',
    '앰버': 'amber',
    '에메랄드': 'emerald',
    '자수정': 'amethyst',
    '로즈': 'rose',
    '오크': 'oak',
    '오크 단색': 'oak-plain',
    '월넛': 'walnut',
    '월넛 단색': 'walnut-plain',
    '밝음': 'light',
    '밝음+배경': 'light-image',
    '어두움': 'dark',
    '어두움+배경': 'dark-image',
    '이중관': 'double',
    '간판': 'sign',
    '전극': 'electrode',
    '말꼬리': 'speech',
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
            if t['variant'] in CHAR_TYPES:
                # 캐릭터 계열은 밝기 × 배경 축이다. 밝음이라고 적고 바탕이 어두우면 멈춘다
                light, pic = CHAR_TYPES[t['variant']]
                got = (_bg_is_light(t), _has_picture(t))
                if got != (light, pic):
                    raise ValueError(
                        '%s(%s %s): 이름표는 밝음=%s 그림=%s 인데 실제는 밝음=%s 그림=%s'
                        % (t['key'], fam, t['variant'], light, pic, got[0], got[1]))
                if got in seen:
                    raise ValueError('%s 계열의 "%s" 와 "%s" 가 내용이 같다'
                                     % (fam, seen[got], t['variant']))
                seen[got] = t['variant']
                continue
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


# --- 캐릭터 --------------------------------------------------------------
# 말풍선에 모양이 있고(편지봉투·포스트잇·픽셀·젤리) 기본 프로필이 캐릭터인 계열.
# 그림은 tools/charbubble.py, 배경은 scenes 의 letters·desk·arcade·laundry 가 그린다.
#
# 축이 기본/배경/글로우가 아니라 밝기 × 배경이다. 모양 있는 말풍선은 그 자체로 이미
# 눈에 띄어서 글로우를 얹을지 말지가 고르는 사람의 관심사가 아니다 — 밝은 방에서 쓸지
# 어두운 방에서 쓸지가 관심사다. 글로우는 계열이 원할 때만 넷 모두에 넣는다(char_glow).
# 종이(편지·포스트잇)에 빛을 두르면 빛이 아니라 번진 테두리로 보인다.

CHAR_TYPES = {
    '밝음': (True, False),
    '밝음+배경': (True, True),
    '어두움': (False, False),
    '어두움+배경': (False, True),
}


def _bg_is_light(t):
    h = t['bg'].lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (r * 299 + g * 587 + b * 114) / 1000 > 128


def _scenes(kind, top, bottom, opts, dims):
    """세 화면의 배경. 같은 장면을 목록은 더 누르고 잠금화면은 거의 안 누른다."""
    return dict(chat_bg=(kind, top, bottom, dict(opts, dim=dims[0])),
                main_bg=(kind, top, bottom, dict(opts, dim=dims[1])),
                passcode_bg=(kind, top, bottom, dict(opts, dim=dims[2])))


def character(slug, no, family, look, light, dark, bg_light, bg_dark, notes, extra=None):
    """캐릭터 계열 네 벌. 밝음 · 밝음+배경 · 어두움 · 어두움+배경.

    look 은 넷이 같이 쓰는 것(말풍선 모양, 캐릭터, 광택), light/dark 는 밝기별 색이다.
    말풍선 색은 한 가지를 (위, 아래) 짝으로 늘여 둔다 — 아이콘과 잠금화면 점이 짝으로 읽는다.
    extra 는 변형 이름 -> 그 변형에만 얹는 값. 배경 그림에 맞춰 말풍선을 바꿀 때 쓴다(캠핑의 불빛).
    """
    if len(notes) != 4:
        raise ValueError('%s: 한 줄 소개를 네 개 줘야 한다' % slug)
    out = []
    for i, variant in enumerate(CHAR_TYPES):
        is_light, pic = CHAR_TYPES[variant]
        pal = dict(look, **(light if is_light else dark))
        for k in ('send', 'send_alt', 'recv', 'recv_alt'):
            pal[k] = (pal[k], pal[k])
        t = dict(key='%s%d' % (slug, no + i), name='%s %s' % (family, variant),
                 note=notes[i], family=family, variant=variant, flat=True, **pal)
        if pic:
            t.update(bg_light if is_light else bg_dark)
        else:
            t.update(chat_bg=None, main_bg=None, passcode_bg=None)
        if extra:
            t.update(extra.get(variant, {}))
        out.append(t)
    return out


THEMES += character(
    'post', 85, '우체국',
    dict(char_style='envelope', char='mailbox'),
    dict(bg='#F6F1E7', bg_deep='#EFE7D8', surface='#FBF8F1', pressed='#EADFCB',
         border='#E0D4BE', text='#3D3129', subtext='#8C7B69',
         accent='#E8483B', accent_dim='#C23A2F', on_accent='#FFFFFF',
         recv='#FFF9EE', recv_alt='#EFE6D6', send='#FFE3DC', send_alt='#F3D2C9',
         recv_text='#3D3129', send_text='#3D3129',
         char_outline='#5A4535', stamp='#FFC2BE',
         char_backs=('#FFF3E0', '#FFE3DC', '#F3E7D3')),
    dict(bg='#1F1A17', bg_deep='#191512', surface='#2A2420', pressed='#352D28',
         border='#3E352F', text='#F2E9DE', subtext='#A69584',
         accent='#FF6B5E', accent_dim='#D9544A', on_accent='#1F1A17',
         recv='#2F2824', recv_alt='#3E3530', send='#5C2B27', send_alt='#733833',
         recv_text='#F2E9DE', send_text='#FFE8E3',
         char_outline='#C9B7A2', stamp='#E89A94',
         char_backs=('#3A302A', '#4A2E2A', '#332B26')),
    _scenes('letters', '#F6F1E7', '#EFE4D2',
            dict(papers=['#FFFFFF', '#FFF3E0', '#FFE3DC', '#EAF2FF'], ink='#8C7B69',
                 stamps=['#E8483B', '#6FA8DC', '#F2B544'], dim_to='#F6F1E7'),
            (0.35, 0.5, 0.1)),
    _scenes('letters', '#221C19', '#191512',
            dict(papers=['#3A302A', '#4A2E2A', '#2F2824', '#34302E'], ink='#A69584',
                 stamps=['#FF6B5E', '#7FB6E6', '#E0B04A'], dim_to='#191512'),
            (0.35, 0.5, 0.1)),
    ['크림빛 편지지 바탕. 첫 말풍선엔 우표 붙은 봉투',
     '편지봉투가 흩어진 우체국 책상',
     '밤의 우체국. 짙은 갈색 바탕에 봉투 말풍선',
     '어둠 속에 흩어진 편지봉투'])

THEMES += character(
    'desk', 89, '책상',
    dict(char_style='postit', char='kongkong'),
    dict(bg='#EEF2E6', bg_deep='#E6ECDB', surface='#F7F9F2', pressed='#DDE6CF',
         border='#D3DDC3', text='#35402B', subtext='#7F8A70',
         accent='#6DBB61', accent_dim='#4F9A44', on_accent='#FFFFFF',
         recv='#FFE98A', recv_alt='#F2CF5B', send='#C9F0D8', send_alt='#A5DCBA',
         recv_fold='#F2CF5B', send_fold='#A5DCBA',
         recv_text='#3E3413', send_text='#1F3D2B',
         char_outline='#3D4A2E', char_backs=('#FFF6CC', '#E4F5E9', '#F1F6E8')),
    dict(bg='#1C2118', bg_deep='#171B13', surface='#262C21', pressed='#2F3629',
         border='#394232', text='#E8EEDD', subtext='#98A488',
         accent='#8BD17E', accent_dim='#6BB25F', on_accent='#1C2118',
         recv='#CDB85E', recv_alt='#A8923F', send='#6FAE8A', send_alt='#558D6F',
         recv_fold='#A8923F', send_fold='#558D6F', tape_a=90,
         recv_text='#2A2410', send_text='#0F261A',
         char_outline='#2A3122', char_backs=('#3A3F2C', '#2F4234', '#353B2E')),
    _scenes('desk', '#E9D2AE', '#DDBF94',
            dict(wood=dict(dark='#8A5A2B', light='#FFF3E0', knots=0, planks=4),
                 notes=['#FFE98A', '#C9F0D8', '#FFD1DC', '#CDE7FF'], ink='#6B7A5A',
                 dim_to='#FFFFFF'),
            (0.25, 0.4, 0.05)),
    _scenes('desk', '#3A2A1D', '#2A1D13',
            dict(wood=dict(dark='#120A05', light='#C08F57', knots=0, planks=4),
                 notes=['#CDB85E', '#6FAE8A', '#C27C8E', '#6F93B8'], ink='#2A2410',
                 dim_to='#000000'),
            (0.35, 0.5, 0.1)),
    ['연둣빛 바탕에 포스트잇 말풍선. 첫 장엔 테이프',
     '나무 책상에 메모지가 붙어 있음',
     '불 끈 책상. 색을 눌러 담은 포스트잇',
     '짙은 원목 책상에 메모지'])

THEMES += character(
    'arcade', 93, '오락실',
    dict(char_style='pixel', char='bulb'),
    dict(bg='#EEF0FF', bg_deep='#E4E7FA', surface='#F7F8FF', pressed='#D9DDF5',
         border='#CDD2EE', text='#1E2140', subtext='#6A6E9A',
         accent='#FF9F1C', accent_dim='#E0850A', on_accent='#1E2140',
         recv='#8BD3FF', recv_alt='#B5E3FF', send='#FFB86B', send_alt='#FFD29E',
         recv_text='#1B1D36', send_text='#2B1A08',
         char_outline='#1E2140', char_glow=5, char_glow_k=1.1,
         char_backs=('#DDE2FF', '#FFE6C7', '#D6EEFF')),
    dict(bg='#1E2140', bg_deep='#171A33', surface='#262A4F', pressed='#2F3460',
         border='#353A6A', text='#EDEBFF', subtext='#9A9CC8',
         accent='#FFD84D', accent_dim='#E0B92E', on_accent='#2B2B40',
         recv='#8BD3FF', recv_alt='#5FA8D8', send='#FFB86B', send_alt='#E08F3F',
         recv_text='#1B1D36', send_text='#2B1A08',
         char_outline='#0E0F24', char_glow=6, char_glow_k=1.5,
         char_backs=('#3A3F78', '#4A3C78', '#2F4A78')),
    _scenes('arcade', '#BFD9FF', '#FFE6F2',
            dict(clouds=7, hills=['#A9C7F2', '#8FB3E8'], ground='#7C8FD6', coins=4,
                 block=0.014, sun='#FFD84D', dim_to='#FFFFFF'),
            (0.3, 0.45, 0.05)),
    _scenes('arcade', '#12132B', '#2A2156',
            dict(stars=70, hills=['#2B2F66', '#353A80'], ground='#1B1D40', coins=3,
                 block=0.014, moon='#FFE9A8', dim_to='#000000'),
            (0.4, 0.5, 0.1)),
    ['연보라 바탕에 빛나는 픽셀 말풍선과 계단 꼬리',
     '픽셀 구름과 동전이 뜬 낮의 오락실',
     '남색 바탕에 네온처럼 빛나는 픽셀 말풍선',
     '픽셀 별이 뜬 밤 화면에 빛나는 말풍선'])

_LAUNDRY_LIGHT = dict(
    bg='#EAF4FB', bg_deep='#E0EEF8', surface='#F5FAFD', pressed='#D4E6F3',
    border='#C9DDEC', text='#2E3A48', subtext='#7C8C9C',
    accent='#6FA8DC', accent_dim='#4F88BC', on_accent='#FFFFFF',
    recv='#FFA3CB', recv_alt='#DB76A6', send='#A6D8FF', send_alt='#6AA9D8',
    recv_edge='#DB76A6', send_edge='#6AA9D8',
    recv_text='#4F1733', send_text='#123A5A',
    char_outline='#3D4A5C', char_backs=('#FFFFFF', '#FFE3EF', '#DDEFFC'))
_LAUNDRY_DARK = dict(
    bg='#1A2230', bg_deep='#151C28', surface='#222B3B', pressed='#2B3547',
    border='#33405A', text='#E3EBF5', subtext='#8E9CB0',
    accent='#7FB6E6', accent_dim='#5F96C6', on_accent='#10161F',
    recv='#D9679C', recv_alt='#F29AC2', send='#4C8FC7', send_alt='#86BDEB',
    recv_edge='#F29AC2', send_edge='#86BDEB',
    recv_text='#FFF0F6', send_text='#F0F8FF',
    char_outline='#9FB1C8', char_backs=('#2B3547', '#40304A', '#243A52'))
_LAUNDRY_SKY = dict(clouds=5, clothes=['#FFA3CB', '#A6D8FF', '#FFFFFF', '#FFE98A'],
                    ink='#3D4A5C', line='#8B9BB0', peg='#FFC24D', dim_to='#FFFFFF')
_LAUNDRY_NIGHT = dict(stars=80, moon='#F4EFD8',
                      clothes=['#D9679C', '#4C8FC7', '#C9D3E0', '#CDB85E'],
                      ink='#0D121B', line='#6F7F98', peg='#D9A33A', dim_to='#000000')

def _seed_of(key):
    """gen.seeded() 가 키에서 씨앗을 만드는 식. 다른 키의 그림을 그대로 물려받을 때 쓴다."""
    import zlib
    return zlib.crc32(key.encode('utf-8')) % 90000000 + 10000000


# 빨래. 0.29.2 까지는 광택만 다른 '빨래'(보통)와 '빨래 반짝'(강함) 두 계열이었다.
# 둘이 같이 있을 까닭이 없어 0.29.3 에서 반짝 쪽을 빨래로 옮기고 보통 광택은 없앴다.
# 키는 빨래 것(laundry97~100)을 쓴다 — 빨래를 깐 사람은 업데이트로 이어지고, 빨래 반짝을 깐
# 사람만 지우고 다시 깔면 된다. 배경은 반짝의 그림을 그대로 쓰려고 반짝 키의 씨앗을 넘긴다.
THEMES += character(
    'laundry', 97, '빨래',
    dict(char_style='jelly', char='sock'),
    _LAUNDRY_LIGHT, _LAUNDRY_DARK,
    _scenes('laundry', '#CFE8FA', '#F2F9FE',
            dict(_LAUNDRY_SKY, lines=2, bubbles=34, seed=_seed_of('sparkle102')),
            (0.3, 0.45, 0.05)),
    _scenes('laundry', '#141B2A', '#24304A',
            dict(_LAUNDRY_NIGHT, lines=2, bubbles=24, seed=_seed_of('sparkle104')),
            (0.25, 0.4, 0.0)),
    ['하늘색 바탕에 반짝이는 젤리 말풍선. 첫 말엔 물방울',
     '비눗방울이 떠다니는 빨랫줄 하늘',
     '밤 빨래. 어두운 바탕에서 광택이 도드라짐',
     '달밤 비눗방울과 반짝이는 말풍선'])


# --- 불빛 두 번째 묶음 ----------------------------------------------------
# 어둠 속 인공 불빛을 다섯 가지 더. 야경·사이버펑크·레드와 겹치지 않게 색과 장면을 갈랐다 —
# 여러 색 불꽃, 분홍·노랑·초록 연등, 따뜻한 금빛 전구, 빨강·흰빛 차 불빛, 초록·호박색 모니터.

THEMES += quartet(
    'firework', 105, '불꽃놀이',
    dict(bg='#0B0D1C', bg_deep='#06070F', surface='#141730', pressed='#1D2142',
         border='#282D55', text='#ECEEFA', subtext='#8E93B8',
         accent='#FFB84D', accent_dim='#D18E2C', on_accent='#1E1203',
         send=('#FFB84D', '#FFB84D'), send_alt=('#FF7FB6', '#FF7FB6'),
         recv=('#1F2548', '#1F2548'), recv_alt=('#5A3F9E', '#5A3F9E'),
         send_text='#241603', recv_text='#ECEEFA'),
    dict(chat_bg=('fireworks', '#0A0C22', '#1E1838', dict(bursts=6, dim=0.34)),
         main_bg=('fireworks', '#0A0C22', '#1A1532', dict(bursts=5, dim=0.46)),
         passcode_bg=('fireworks', '#0C0E28', '#241C44', dict(bursts=8, stars=80, dim=0.04))),
    ['남색 밤 바탕에 금빛·분홍 말풍선',
     '물가 위로 불꽃이 터지는 밤',
     '말풍선이 불꽃처럼 빛남',
     '불꽃 배경 위에 빛나는 말풍선까지'])

THEMES += quartet(
    'lantern', 109, '연등',
    dict(bg='#140F1E', bg_deep='#0C0913', surface='#1E1729', pressed='#2A2038',
         border='#382B48', text='#F5ECF2', subtext='#A897AE',
         accent='#FF8FB1', accent_dim='#D66A8C', on_accent='#2A0B17',
         send=('#FF8FB1', '#FF8FB1'), send_alt=('#FFD36B', '#FFD36B'),
         recv=('#2A2138', '#2A2138'), recv_alt=('#2F6E55', '#2F6E55'),
         send_text='#2A0B17', recv_text='#F5ECF2'),
    dict(chat_bg=('lanterns', '#120C1E', '#2A1630',
                  dict(colors=['#FF8FB1', '#FFD36B', '#7ED99B', '#FF9B5A'], dim=0.32)),
         main_bg=('lanterns', '#120C1E', '#24142C',
                  dict(colors=['#FF8FB1', '#FFD36B', '#7ED99B'], rows=2, dim=0.46)),
         passcode_bg=('lanterns', '#140D22', '#361A3A',
                      dict(colors=['#FF8FB1', '#FFD36B', '#7ED99B', '#FF9B5A'], rows=4,
                           bokeh=40, dim=0.02))),
    ['자줏빛 밤 바탕에 분홍·노랑 연등 색',
     '줄줄이 매달린 연등이 깔림',
     '말풍선이 등불처럼 빛남',
     '연등 아래 빛나는 말풍선까지'])

THEMES += quartet(
    'garland', 113, '알전구',
    dict(bg='#17130F', bg_deep='#0E0B08', surface='#221C16', pressed='#2E261E',
         border='#3B3127', text='#F7EEDF', subtext='#B09D84',
         accent='#FFC766', accent_dim='#D69E43', on_accent='#261803',
         send=('#FFC766', '#FFC766'), send_alt=('#FFE3A8', '#FFE3A8'),
         recv=('#2A2219', '#2A2219'), recv_alt=('#5A4630', '#5A4630'),
         send_text='#261803', recv_text='#F7EEDF'),
    dict(chat_bg=('garland', '#120E0B', '#241A12', dict(bulb=['#FFD27A', '#FFE3A8'], dim=0.3)),
         main_bg=('garland', '#120E0B', '#20170F', dict(bulb=['#FFD27A'], strands=3, dim=0.45)),
         passcode_bg=('garland', '#140F0B', '#2E2014',
                      dict(bulb=['#FFD27A', '#FFE3A8', '#FFB45A'], strands=5, bokeh=34, dim=0.0))),
    ['짙은 갈색 바탕에 금빛 말풍선',
     '늘어진 전선에 알전구가 켜짐',
     '말풍선이 전구처럼 따뜻하게 빛남',
     '알전구 아래 빛나는 말풍선까지'])

THEMES += quartet(
    'highway', 117, '고속도로',
    dict(bg='#0C1119', bg_deep='#070A10', surface='#141B26', pressed='#1C2533',
         border='#263243', text='#EAF0F7', subtext='#8A97A8',
         accent='#FF4D5E', accent_dim='#CC3746', on_accent='#FFF1F2',
         send=('#FF4D5E', '#FF4D5E'), send_alt=('#FFB347', '#FFB347'),
         recv=('#1B2432', '#1B2432'), recv_alt=('#33507A', '#33507A'),
         send_text='#2A0508', recv_text='#EAF0F7'),
    dict(chat_bg=('trails', '#0A0F1C', '#1B2233', dict(dim=0.3)),
         main_bg=('trails', '#0A0F1C', '#161D2C', dict(lanes=6, dim=0.45)),
         passcode_bg=('trails', '#0C1224', '#24304A', dict(lanes=10, horizon=0.36, dim=0.0))),
    ['검푸른 바탕에 빨강·주황 말풍선',
     '밤 고속도로의 빛줄기가 깔림',
     '말풍선이 미등처럼 빛남',
     '빛줄기 배경 위에 빛나는 말풍선까지'])

THEMES += quartet(
    'terminal', 121, '터미널',
    dict(bg='#0A120D', bg_deep='#050A07', surface='#101C15', pressed='#16271D',
         border='#1F3528', text='#D8F5E1', subtext='#7FA38B',
         accent='#39E07A', accent_dim='#23B05E', on_accent='#03170A',
         send=('#39E07A', '#39E07A'), send_alt=('#FFB000', '#FFB000'),
         recv=('#11251A', '#11251A'), recv_alt=('#1E4A33', '#1E4A33'),
         send_text='#03170A', recv_text='#D8F5E1'),
    dict(chat_bg=('terminal', '#07100A', '#0B1A10', dict(dim=0.52)),
         main_bg=('terminal', '#07100A', '#0A160E', dict(dim=0.58)),
         passcode_bg=('terminal', '#08120B', '#0E2014', dict(cell=0.028, dim=0.1))),
    ['검은 초록 바탕에 형광 초록·호박색 말풍선',
     '옛 모니터에 코드가 흐름',
     '말풍선이 모니터 글자처럼 빛남',
     '코드 화면 위에 빛나는 말풍선까지'])


# --- 캐릭터 두 번째 묶음 --------------------------------------------------
# 영화표·식빵·팻말·우주선 판·잎 말풍선. 캐릭터는 팝콘 통·식빵·모닥불·행성·선인장.
# 전부 새로 그렸다. 카카오 프렌즈와 겹치는 동물(고양이·개·토끼·오리·사자)은 피했다.
# 글로우는 넣지 않는다 — 네온 느낌인 계열이 없다.

THEMES += character(
    'cinema', 125, '영화관',
    dict(char_style='ticket', char='popcorn'),
    dict(bg='#FBF3E6', bg_deep='#F4E8D4', surface='#FFFAF1', pressed='#EEDFC6',
         border='#E6D3B5', text='#3B2522', subtext='#8E7466',
         accent='#D93A3A', accent_dim='#B32C2C', on_accent='#FFFFFF',
         recv='#FFFDF7', recv_alt='#F3E2C4', send='#FFD9D2', send_alt='#FFE7A8',
         recv_text='#3B2522', send_text='#3B2522',
         char_outline='#4A2C28', star='#E8B93A',
         char_backs=('#FFF1D6', '#FFE0DA', '#F6E6CC')),
    dict(bg='#1A1216', bg_deep='#130D10', surface='#241A1F', pressed='#2F2228',
         border='#3A2A31', text='#F4E6E4', subtext='#A8908F',
         accent='#FF5A5A', accent_dim='#D94444', on_accent='#1A1216',
         recv='#2C2127', recv_alt='#3C2D33', send='#7A2530', send_alt='#7A5A22',
         recv_text='#F4E6E4', send_text='#FFEDEA',
         char_outline='#D8C0BC', star='#E8B93A',
         char_backs=('#3A2A30', '#4A2A30', '#3A3228')),
    _scenes('cinema', '#FBF3E6', '#F2E2C8',
            dict(tickets=['#FFD9D2', '#FFE7A8', '#FFFFFF', '#D6E8FF'], ink='#8E7466',
                 pop='#FFF8E6', star='#E8B93A', dim_to='#FBF3E6'),
            (0.3, 0.45, 0.05)),
    _scenes('cinema', '#1E1418', '#0E090B',
            dict(screen='#DCE6FF', seats='#5A2632', dim_to='#000000'),
            (0.35, 0.5, 0.05)),
    ['크림빛 바탕에 영화표 말풍선. 첫 장엔 별 도장',
     '영화표와 팝콘이 흩어진 매표소',
     '상영관 조명 끈 어두운 바탕에 영화표',
     '빛나는 스크린 앞 좌석 줄'])

THEMES += character(
    'bakery', 129, '빵집',
    dict(char_style='toast', char='bread'),
    dict(bg='#FFF6E6', bg_deep='#FAEDD5', surface='#FFFBF2', pressed='#F2E2C2',
         border='#EBD7B2', text='#4A3320', subtext='#98795A',
         accent='#E0913A', accent_dim='#BF7428', on_accent='#FFFFFF',
         recv='#FFF8EA', recv_alt='#FCE9C8', send='#FFE6B0', send_alt='#F9D59A',
         recv_crust='#D9A25F', send_crust='#C98A45',
         recv_text='#4A3320', send_text='#4A3320',
         char_outline='#5A3C22', jam='#E8455A',
         char_backs=('#FFF1D2', '#FFE3C2', '#F6ECD8')),
    dict(bg='#211A14', bg_deep='#18130E', surface='#2B221A', pressed='#362B21',
         border='#43362A', text='#F5E9D8', subtext='#AF9A80',
         accent='#F2A652', accent_dim='#CC8538', on_accent='#211A14',
         recv='#3A2E22', recv_alt='#4A3A2A', send='#7A5530', send_alt='#8C6236',
         recv_crust='#6B4A2A', send_crust='#A2743F',
         recv_text='#F5E9D8', send_text='#FFF3E2',
         char_outline='#E6CBA8', jam='#C23A52',
         char_backs=('#3A2E22', '#4A3624', '#33291F')),
    _scenes('bakery', '#FFF6E6', '#FAEDD5',
            dict(check='#F2C58A', ink='#5A3C22', dim_to='#FFF6E6',
                 breads=[('#D08A45', '#FFF1D2'), ('#E3A35C', '#FFF6E0')]),
            (0.3, 0.45, 0.05)),
    _scenes('bakery', '#2A2019', '#211A14',
            dict(check='#5A4230', ink='#1A120B', dim_to='#000000',
                 breads=[('#B8773C', '#E8D2AE'), ('#9A6230', '#D9C09A')]),
            (0.3, 0.45, 0.05)),
    ['버터빛 바탕에 식빵 말풍선. 첫 장엔 흘러내리는 잼',
     '체크무늬 식탁보에 빵이 놓임',
     '문 닫은 빵집. 갈색 바탕에 구운 식빵',
     '어두운 체크 식탁보 위의 빵'])

THEMES += character(
    'camp', 133, '캠핑',
    dict(char_style='sign', char='flame'),
    dict(bg='#EEF3EA', bg_deep='#E4ECDF', surface='#F7FAF4', pressed='#DCE6D4',
         border='#D0DCC6', text='#2F3A2A', subtext='#76836B',
         accent='#E07A3A', accent_dim='#BF6128', on_accent='#FFFFFF',
         recv='#F6E3BF', recv_alt='#EACF9E', send='#E8B67A', send_alt='#D9A263',
         recv_text='#3A2A1C', send_text='#3A2A1C',
         char_outline='#4A3522', post='#9C6B3E', nail='#8A7A6A',
         char_glow=5, char_glow_k=1.1, char_glow_color='#FF9A4A',
         char_backs=('#E4F0DC', '#FFE8CC', '#DCEAF2')),
    # 어두운 쪽은 모닥불 빛이 팻말 모서리에 걸린 것처럼 주황으로 빛나게 한다.
    # 밝은 쪽에도 넣는 것은 계열 안에서 말풍선 재질을 맞추려는 것이다 — 밝은 바탕에서는 거의 안 보인다
    dict(bg='#141A1C', bg_deep='#0E1315', surface='#1C2427', pressed='#253033',
         border='#2F3B3F', text='#EEE8DC', subtext='#97A09A',
         accent='#FF9A4A', accent_dim='#D97A30', on_accent='#141A1C',
         recv='#4A3A2A', recv_alt='#5A4633', send='#8A5A30', send_alt='#9C6A3A',
         recv_text='#FBEFDF', send_text='#FFF3E4',
         char_outline='#D9C3A5', post='#6E4A2A', nail='#C9B79C',
         char_glow=6, char_glow_k=1.25, char_glow_color='#FF9A4A',
         char_backs=('#26343A', '#3A2E24', '#1E2C30')),
    _scenes('camp', '#BFE3F5', '#EAF6EC',
            dict(sun='#FFE38A', clouds=4, hills=['#A9CBB8', '#86B09A'], trees='#4F8A68',
                 ground='#7FB27A', tents=['#E07A3A', '#F2C14E'], ink='#3A2A1C', dim_to='#FFFFFF'),
            (0.3, 0.45, 0.05)),
    _scenes('camp', '#0C1424', '#1E2A3A',
            dict(stars=120, hills=['#1E2C3A', '#18242E'], trees='#0F1A1E', ground='#141E20',
                 tents=['#8A4A2A', '#7A6A2A'], fire='#FF8A3D', ink='#05080A', dim_to='#000000',
                 fire_size=1.7, fire_reach=0.95, fire_y=0.84),
            (0.25, 0.4, 0.0)),
    ['풀빛 바탕에 나무 팻말 말풍선. 첫 장엔 말뚝',
     '산 아래 풀밭에 텐트가 선 낮',
     '밤 캠핑장. 모닥불 빛이 도는 팻말 말풍선',
     '모닥불이 비추는 밤. 팻말도 불빛에 물듦'],
    # 배경에 모닥불이 있는 쪽만 말풍선도 그 불에 비친 것처럼 아래와 불 쪽 귀퉁이를 달군다.
    # 배경이 없는 어두움에 넣으면 빛의 출처가 화면에 없어서 까닭 없는 얼룩이 된다
    extra={'어두움+배경': dict(firelight='#FF9A4A', firelight_k=1.0, char_glow_k=1.4)})

THEMES += character(
    'space', 137, '우주',
    dict(char_style='panel', char='saturn'),
    dict(bg='#EEF0FB', bg_deep='#E4E7F7', surface='#F7F8FE', pressed='#DADEF3',
         border='#CDD2EC', text='#252A4A', subtext='#6E7399',
         accent='#7B6CF6', accent_dim='#5E4FD9', on_accent='#FFFFFF',
         recv='#FFFFFF', recv_alt='#E3E8FF', send='#DCD5FF', send_alt='#FFE0C2',
         recv_text='#252A4A', send_text='#252A4A',
         char_outline='#2E335A', star='#FFC94D',
         char_backs=('#E3E0FF', '#FFE8D6', '#DDF0FF')),
    dict(bg='#10122A', bg_deep='#0A0B1E', surface='#181B38', pressed='#212548',
         border='#2B3058', text='#E8EAFF', subtext='#8F94C4',
         accent='#9D90FF', accent_dim='#7B6CF6', on_accent='#10122A',
         recv='#1F2448', recv_alt='#2C3260', send='#4B3FA8', send_alt='#7A4470',
         recv_text='#E8EAFF', send_text='#F3F0FF',
         char_outline='#AEB4E8', star='#FFD84D',
         char_backs=('#2A2E5A', '#3A2E52', '#1F3050')),
    _scenes('space', '#EEF0FB', '#F8E8F2',
            dict(star='#9D90FF', stars=60, dim_to='#FFFFFF',
                 planets=[('#FFC98A', '#F2A65A', '#B9A6FF'), ('#9FD8FF', '#7ABFEF', None),
                          ('#C9B6FF', '#AA94F0', '#FFC98A')]),
            (0.25, 0.4, 0.0)),
    _scenes('space', '#0A0B1E', '#1A1540',
            dict(dim_to='#000000',
                 planets=[('#FFB86B', '#E08F3F', '#B9A6FF'), ('#6FA8DC', '#4F88BC', None),
                          ('#9D90FF', '#7B6CF6', '#FFD27A')]),
            (0.25, 0.4, 0.0)),
    ['연보라 바탕에 우주선 판 말풍선. 첫 장엔 안테나',
     '파스텔 하늘에 고리 행성이 뜸',
     '깊은 남색 바탕에 우주선 판 말풍선',
     '별과 행성이 뜬 밤 우주'])

THEMES += character(
    'greenhouse', 141, '온실',
    dict(char_style='leaf', char='cactus'),
    dict(bg='#EDF5EC', bg_deep='#E2EFE1', surface='#F7FBF6', pressed='#D6E8D4',
         border='#C8DEC6', text='#24382A', subtext='#6B8570',
         accent='#3FA66A', accent_dim='#2E8753', on_accent='#FFFFFF',
         recv='#FFFFFF', recv_alt='#E3F2DC', send='#C4EBCB', send_alt='#F7DCE6',
         recv_text='#24382A', send_text='#24382A',
         char_outline='#27402E', stem='#5A9A5A', dew='#DFF3FF',
         char_backs=('#E4F5E2', '#FFE6EE', '#F1F6E4')),
    dict(bg='#111C16', bg_deep='#0C1510', surface='#18261E', pressed='#203227',
         border='#2A3F32', text='#E2F2E6', subtext='#88A690',
         accent='#6FD49A', accent_dim='#4FB47A', on_accent='#0C1510',
         recv='#1E3026', recv_alt='#2A4234', send='#2F6B48', send_alt='#6E3A52',
         recv_text='#E2F2E6', send_text='#F0FAF3',
         char_outline='#A9CDB3', stem='#6FB46F', dew='#BFE3F2',
         char_backs=('#1F3328', '#3A2A33', '#26352A')),
    _scenes('greenhouse', '#CFEAF7', '#F2FAF0', dict(rays=True, dim_to='#FFFFFF'),
            (0.3, 0.45, 0.05)),
    _scenes('greenhouse', '#0E1A24', '#16261E',
            dict(frame='#2F4A3A', lamps='#FFD27A', ink='#0A140F', shelf='#4A3A2A',
                 dim_to='#000000'),
            (0.25, 0.4, 0.0)),
    ['연둣빛 바탕에 잎 말풍선. 첫 장엔 잎자루와 이슬',
     '햇살 드는 온실 선반에 화분이 줄지음',
     '밤 온실. 짙은 초록 바탕에 잎 말풍선',
     '전등 켜진 밤 온실의 화분들'])

# --- 네온사인 --------------------------------------------------------------
# 벽돌 벽에 걸린 네온관. 네 벌이 곧 말풍선 디자인 네 가지다 — 스테인드 글래스가 색 네 개로
# 네 벌을 채운 것과 같다. 네온은 밝은 바탕에서 빛이 안 보여서 밝음/어두움 축이 맞지 않는다.
# 글로우는 재질로 붙는다(tools/glow.py). 관은 tube → 강한 블룸, 간판은 sign → 아래로 떨어지는 빛.

_NEON_BASE = dict(bg='#100C14', bg_deep='#0A070D', surface='#1A1520', pressed='#241D2C',
                  border='#2E2638', text='#F2ECF7', subtext='#9A90A8', on_accent='#14000A',
                  char_outline='#111114', flat=True)


def _neon_theme(no, variant, style, material, recv, send, recv_text, send_text, accent_dim,
                signs, note):
    """네온사인 한 벌. 받은 쪽과 보낸 쪽이 서로 다른 네온 색이고, 벽의 낙서도 그 색을 쓴다."""
    wall = lambda count, dim: ('neonwall', '#3A1F1B', '#140C0B',
                               dict(signs=signs, count=count, dim=dim, dim_to='#000000'))
    return dict(_NEON_BASE, key='neon%d' % no, name='네온사인 %s' % variant, note=note,
                family='네온사인', variant=variant, char_style=style, material=material,
                accent=send, accent_dim=accent_dim,
                send=(send, send), send_alt=(send, send), recv=(recv, recv), recv_alt=(recv, recv),
                send_text=send_text, recv_text=recv_text,
                chat_bg=wall(5, 0.45), main_bg=wall(4, 0.6), passcode_bg=wall(6, 0.12))


THEMES += [
    _neon_theme(145, '이중관', 'neon_double', 'tube', '#35E0FF', '#FF3FA4', '#D9F8FF', '#FFE0F0',
                '#C42D7E', [('heart', '#FF3FA4'), ('star', '#35E0FF'), ('moon', '#B45CFF')],
                '벽돌 벽에 관 두 줄 네온. 첫 말엔 네온 별'),
    _neon_theme(146, '간판', 'neon_sign', 'sign', '#4D7CFF', '#FF7A2F', '#DFE7FF', '#FFE6D6',
                '#C85A1E', [('arrow', '#FF7A2F'), ('bolt', '#4D7CFF'), ('star', '#FFD23F')],
                '금속 간판에 박힌 네온. 첫 말은 사슬에 매달림'),
    _neon_theme(147, '전극', 'neon_electrode', 'tube', '#4CFF88', '#B45CFF', '#DDFFE8', '#EFE0FF',
                '#8A40C8', [('moon', '#B45CFF'), ('bolt', '#4CFF88'), ('heart', '#FF3FA4')],
                '끊긴 관 끝에 전극이 달린 진짜 네온관'),
    _neon_theme(148, '말꼬리', 'neon_speech', 'tube', '#FFD23F', '#FF3B6B', '#FFF6D6', '#FFE0E8',
                '#C42A52', [('star', '#FFD23F'), ('heart', '#FF3B6B'), ('arrow', '#35E0FF')],
                '꼬리까지 관 하나로 이어진 네온 말풍선'),
]

check_variants()
