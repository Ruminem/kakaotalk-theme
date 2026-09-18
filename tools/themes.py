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

VERSION = '0.39.1'

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


# --- 카테고리 ----------------------------------------------------------------
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
# '기타' 는 두지 않는다. 카테고리가 아니라 유보라서 아무도 열지 않는다.
# 어디에도 안 맞는 계열이 생기면 카테고리를 하나 더 만든다.
CATEGORIES = (
    ('무늬', '바탕에 색과 도형만. 담백한 쪽'),
    ('편안함', '채도를 낮춰 눈이 편한 쪽'),
    ('유리', '말풍선이 반투명하다'),
    ('자연', '배경이 장면을 그린다'),
    ('불빛', '어두운 바탕에 인공 불빛'),
    ('불빛 - 네온사인', '벽에 건 네온관 말풍선'),
    ('캐릭터', '말풍선 모양과 캐릭터 프로필'),
    ('도트', '8비트 도트로 그린 말풍선과 화면'),
)

# 카테고리 -> 카테고리 문서 파일 이름(docs/themes/<이름>.md). 영문으로 쓴다 — 한글 파일 이름은
# 주소에서 %EB%AC%B4 처럼 깨져 보인다. 카테고리를 더하면 여기에도 한 줄 쓴다. 안 쓰면 생성이 멈춘다.
CATEGORY_FILE = {
    '무늬': 'pattern',
    '편안함': 'comfort',
    '유리': 'glass',
    '자연': 'nature',
    '불빛': 'lights',
    '불빛 - 네온사인': 'lights-neon',
    '캐릭터': 'character',
    '도트': 'pixel',
}

# 계열 이름 -> 카테고리. 새 계열을 더하면 여기에 한 줄 쓴다. 안 쓰면 생성이 멈춘다 —
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
    '씨글래스': '유리',
    '글래스 블록': '유리',
    '얼음': '유리',
    '골판 유리': '유리',
    '아크릴': '유리',
    '레진': '유리',
    '도형': '무늬',
    '깅엄 체크': '무늬',
    '폴카 도트': '무늬',
    '테라조': '무늬',
    '마린 스트라이프': '무늬',
    '체커보드': '무늬',
    '차분': '편안함',
    '고요': '편안함',
    '수채화': '편안함',
    '수묵화': '편안함',
    '비 오는 창가': '편안함',
    '페이퍼컷': '편안함',

    '벚꽃 그늘': '자연',
    '오로라': '자연',
    '심야': '자연',
    '바다': '자연',
    '숲': '자연',
    '설원': '자연',

    '야경': '불빛',
    '사이버펑크': '불빛',
    '레드': '불빛',
    '블루': '불빛',
    '퍼플': '불빛',
    '그린': '불빛',
    '골드': '불빛',
    '핑크': '불빛',
    '불꽃놀이': '불빛',
    '연등': '불빛',
    '알전구': '불빛',
    '고속도로': '불빛',
    '터미널': '불빛',
    '네온사인': '불빛 - 네온사인',
    '네온사인 v2': '불빛 - 네온사인',
    '네온사인 v3': '불빛 - 네온사인',
    '네온사인 v4': '불빛 - 네온사인',
    '네온사인 v5': '불빛 - 네온사인',
    '네온사인 v6': '불빛 - 네온사인',
    '네온사인 v7': '불빛 - 네온사인',
    '네온사인 v8': '불빛 - 네온사인',
    '네온사인 v9': '불빛 - 네온사인',
    '네온사인 v10': '불빛 - 네온사인',
    '네온사인 v11': '불빛 - 네온사인',
    '네온사인 v12': '불빛 - 네온사인',
    '네온사인 v13': '불빛 - 네온사인',
    '네온 동물': '불빛 - 네온사인',

    '우체국': '캐릭터',
    '책상': '캐릭터',
    '오락실': '도트',
    '빨래': '캐릭터',
    '영화관': '캐릭터',
    '빵집': '캐릭터',
    '캠핑': '캐릭터',
    '우주': '캐릭터',
    '온실': '캐릭터',

    '도트 모험': '도트',
    '도트 액정': '도트',
    '레트로 PC': '도트',
    '도트 농장': '도트',
}

# README 에 카테고리마다 한 줄씩 내놓는 대표 계열 셋. 나머지는 카테고리 문서에서 본다.
# 계열이 예순을 넘으면서 README 에 전부 깔았더니 폰에서 썸네일 예순 장을 지나야 받는 법이 나왔다.
# 앞에서 셋을 자르면 비슷한 것끼리 붙어 나와서(불빛은 레드 파생) 카테고리의 폭이 안 보인다 —
# 서로 다른 셋을 고른다. 적지 않은 카테고리는 팔레트 표 순 앞의 셋이다.
CATEGORY_COVER = {
    '무늬': ('먹빛 민트', '캔디 팝', '깅엄 체크'),
    '편안함': ('수채화', '수묵화', '페이퍼컷'),
    '유리': ('리퀴드 글래스', '스테인드 글래스', '레진'),
    '자연': ('벚꽃 그늘', '오로라', '설원'),
    '불빛': ('야경', '불꽃놀이', '연등'),
    '불빛 - 네온사인': ('네온사인', '네온사인 v7', '네온 동물'),
    '캐릭터': ('우체국', '빵집', '우주'),
    '도트': ('오락실', '도트 모험', '레트로 PC'),
}


def categorized():
    """카테고리 순서대로 (카테고리, 설명, [(계열, [테마...]), ...]) 를 돌려준다.

    카테고리 안의 계열 순서는 THEMES 순서 그대로다. 카테고리가 생기면서 README 순서는
    '팔레트 표 순서' 에서 '카테고리 순 -> 그 안에서 팔레트 순' 으로 바뀌었다.
    """
    fams = families()
    names = [n for n, _ in fams]
    known = [n for n, _ in CATEGORIES]

    bad = sorted({c for c in CATEGORY.values() if c not in known})
    if bad:
        raise ValueError('CATEGORIES 에 없는 카테고리를 썼다: %s' % ', '.join(bad))
    missing = [n for n in names if n not in CATEGORY]
    if missing:
        raise ValueError('카테고리가 없는 계열: %s. CATEGORY 에 한 줄 쓴다 — '
                         '안 쓰면 README 목록에서 통째로 빠진다' % ', '.join(missing))
    stale = [n for n in CATEGORY if n not in names]
    if stale:
        raise ValueError('없는 계열이 CATEGORY 에 남아 있다: %s' % ', '.join(stale))
    # README 안에서 카테고리와 계열이 같은 앵커를 쓴다. 이름이 겹치면 링크가
    # 엉뚱한 자리로 뛴다.
    clash = [n for n in names if n in known]
    if clash:
        raise ValueError('계열 이름과 카테고리 이름이 같다: %s. README 앵커가 겹친다'
                         % ', '.join(clash))

    out = []
    for name, note in CATEGORIES:
        members = [(f, ms) for f, ms in fams if CATEGORY[f] == name]
        if not members:
            raise ValueError('%s 카테고리가 비었다. 넣을 계열이 생길 때 만든다 — '
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


# 블루 — 네 벌. 레드와 같은 짜임(검은 바탕 · 쨍한 말풍선 · 아래서 올라오는 불티)을 파랑으로 옮겼다
THEMES += quartet(
    'blue', 225, '블루',
    dict(bg='#050A16', bg_deep='#02050B', surface='#0A1424', pressed='#0D1B31', border='#122A4A',
         text='#ECF3FF', subtext='#8EA6C0', accent='#1B6BFF', accent_dim='#1250C4', on_accent='#F2F7FF',
         send=('#0057E6', '#0057E6'), send_alt=('#4F8DF5', '#4F8DF5'),
         recv=('#0B1A3B', '#0B1A3B'), recv_alt=('#0F3A8E', '#0F3A8E'),
         send_text='#F2F7FF', recv_text='#E8F0FF'),
    dict(chat_bg=('ember', '#02061A', '#00185A',
                  dict(glow='#0038FF', spark='#6B9BFF', smoke='#04102E',
                       count=70, dim=0.30)),
         main_bg=('ember', '#010516', '#00134A',
                  dict(glow='#0033E6', spark='#5C8FFF', smoke='#030C28',
                       count=50, dim=0.46)),
         passcode_bg=('ember', '#030A22', '#002075',
                      dict(glow='#1B50FF', spark='#8DB4FF', smoke='#061636',
                           count=110, pool_alpha=150, dim=0.04))),
    ['검푸른 바탕에 파랑 말풍선 네 칸',
     '어둠 속에서 푸른 불티가 떠오름',
     '말풍선이 파랗게 달아오름',
     '불티 배경 위에 달아오른 파랑까지'])


# 퍼플 — 네 벌. 레드와 같은 짜임(검은 바탕 · 쨍한 말풍선 · 아래서 올라오는 불티)을 보라로 옮겼다
THEMES += quartet(
    'purple', 229, '퍼플',
    dict(bg='#0F0518', bg_deep='#08020D', surface='#1A0A28', pressed='#240D36', border='#371250',
         text='#F5ECFF', subtext='#A98EC0', accent='#A43BFF', accent_dim='#7A1FC4', on_accent='#F8F2FF',
         send=('#8A00E6', '#8A00E6'), send_alt=('#A45CF5', '#A45CF5'),
         recv=('#260B3B', '#260B3B'), recv_alt=('#560F8E', '#560F8E'),
         send_text='#F8F2FF', recv_text='#F2E8FF'),
    dict(chat_bg=('ember', '#10021A', '#3A005A',
                  dict(glow='#9000FF', spark='#C58DFF', smoke='#1E0430',
                       count=70, dim=0.30)),
         main_bg=('ember', '#0C0116', '#30004A',
                  dict(glow='#8000E6', spark='#B77AFF', smoke='#190328',
                       count=50, dim=0.46)),
         passcode_bg=('ember', '#150322', '#4A0075',
                      dict(glow='#A01BFF', spark='#D4A8FF', smoke='#260636',
                           count=110, pool_alpha=150, dim=0.04))),
    ['검보랏빛 바탕에 보라 말풍선 네 칸',
     '어둠 속에서 보랏빛 불티가 떠오름',
     '말풍선이 보랏빛으로 달아오름',
     '불티 배경 위에 달아오른 보라까지'])


# 그린 — 네 벌. 레드와 같은 짜임(검은 바탕 · 쨍한 말풍선 · 아래서 올라오는 불티)을 초록으로 옮겼다
THEMES += quartet(
    'green', 233, '그린',
    dict(bg='#04130C', bg_deep='#020A06', surface='#092116', pressed='#0C2D1F', border='#114530',
         text='#ECFFF5', subtext='#8EC0A8', accent='#1BE67E', accent_dim='#12A85C', on_accent='#02170C',
         send=('#00C865', '#00C865'), send_alt=('#7CF0B0', '#7CF0B0'),
         recv=('#0B3B24', '#0B3B24'), recv_alt=('#0E7A45', '#0E7A45'),
         send_text='#021A0D', recv_text='#E8FFF2'),
    dict(chat_bg=('ember', '#021A0E', '#005A2E',
                  dict(glow='#00FF73', spark='#8DFFB9', smoke='#042E18',
                       count=70, dim=0.30)),
         main_bg=('ember', '#011608', '#004A26',
                  dict(glow='#00E667', spark='#7AFFAD', smoke='#03281A',
                       count=50, dim=0.46)),
         passcode_bg=('ember', '#03220F', '#00753C',
                      dict(glow='#1BFF84', spark='#B0FFD0', smoke='#063622',
                           count=110, pool_alpha=150, dim=0.04))),
    ['검초록 바탕에 초록 말풍선 네 칸',
     '어둠 속에서 초록 불티가 떠오름',
     '말풍선이 초록으로 달아오름',
     '불티 배경 위에 달아오른 초록까지'])


# 골드 — 네 벌. 레드와 같은 짜임(검은 바탕 · 쨍한 말풍선 · 아래서 올라오는 불티)을 금빛으로 옮겼다
THEMES += quartet(
    'gold', 237, '골드',
    dict(bg='#150F05', bg_deep='#0B0802', surface='#231A0A', pressed='#30230D', border='#483412',
         text='#FFF7EC', subtext='#C0AB8E', accent='#FFB81B', accent_dim='#C48A12', on_accent='#1F1400',
         send=('#EBA400', '#EBA400'), send_alt=('#FFD66B', '#FFD66B'),
         recv=('#3B2A0B', '#3B2A0B'), recv_alt=('#7A540D', '#7A540D'),
         send_text='#1F1400', recv_text='#FFF3E0'),
    dict(chat_bg=('ember', '#1A1002', '#5A3A00',
                  dict(glow='#FFA800', spark='#FFE08D', smoke='#2E1E04',
                       count=70, dim=0.30)),
         main_bg=('ember', '#150C01', '#4A3000',
                  dict(glow='#E69700', spark='#FFD27A', smoke='#281A03',
                       count=50, dim=0.46)),
         passcode_bg=('ember', '#221503', '#754C00',
                      dict(glow='#FFB51B', spark='#FFEAB0', smoke='#362406',
                           count=110, pool_alpha=150, dim=0.04))),
    ['검갈색 바탕에 금빛 말풍선 네 칸',
     '어둠 속에서 금빛 불티가 떠오름',
     '말풍선이 금빛으로 달아오름',
     '불티 배경 위에 달아오른 금빛까지'])


# 핑크 — 네 벌. 레드와 같은 짜임(검은 바탕 · 쨍한 말풍선 · 아래서 올라오는 불티)을 분홍으로 옮겼다
THEMES += quartet(
    'pink', 241, '핑크',
    dict(bg='#16050F', bg_deep='#0B0208', surface='#240A19', pressed='#310D22', border='#4A1234',
         text='#FFECF6', subtext='#C08EAA', accent='#FF1BA0', accent_dim='#C41279', on_accent='#FFF2F9',
         send=('#E0007F', '#E0007F'), send_alt=('#F55CB0', '#F55CB0'),
         recv=('#3B0B28', '#3B0B28'), recv_alt=('#8E0F5C', '#8E0F5C'),
         send_text='#FFF2F9', recv_text='#FFE8F4'),
    dict(chat_bg=('ember', '#1A0212', '#5A0040',
                  dict(glow='#FF00A0', spark='#FF8DD0', smoke='#2E0420',
                       count=70, dim=0.30)),
         main_bg=('ember', '#150110', '#4A0034',
                  dict(glow='#E6008F', spark='#FF7AC4', smoke='#280318',
                       count=50, dim=0.46)),
         passcode_bg=('ember', '#22031A', '#750052',
                      dict(glow='#FF1BAE', spark='#FFB0DD', smoke='#36062A',
                           count=110, pool_alpha=150, dim=0.04))),
    ['검자줏빛 바탕에 분홍 말풍선 네 칸',
     '어둠 속에서 분홍 불티가 떠오름',
     '말풍선이 분홍으로 달아오름',
     '불티 배경 위에 달아오른 분홍까지'])

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
    '팔각': 'octagon',
    '꺾쇠': 'bracket',
    '밑줄': 'underline',
    '두 가닥': 'split',
    '바다': 'sea',
    '숲': 'forest',
    '얼음': 'ice',
    '모둠': 'mixed',
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

    slug 를 직접 들고 있으면 그걸 쓴다 — 커스텀 테마(tools/mix.py)는 계열도 변형도
    없어서 VARIANT_SLUG 에서 이름 조각을 찾을 수 없다.
    """
    if t.get('slug'):
        return t['slug']
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

    `pkg` 를 직접 들고 있으면 그걸 쓴다 — 커스텀 테마 템플릿은 파일 이름
    (custom-template)과 패키지 이름(custom)이 달라야 한다. 패키지 이름은 브라우저가
    못 고치는 자리라 템플릿에 구워지는 값이고, 파일 이름은 사이트에 올릴 때 쓴다.
    """
    if t.get('pkg'):
        return t['pkg']
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
         send_text='#03170A', recv_text='#D8F5E1',
         # 기본 글로우의 흰 테두리와 반사선이 검은 초록 칸에서 광택 스티커로 읽혀서
         # 모니터 창틀처럼 형광 초록으로 빛나게 한다(0.31.1)
         glow_edge='phosphor'),
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
                signs, note, slug='neon', family='네온사인', face=('#3A1F1B', '#140C0B'),
                surface='brick', lit=False, room=None, look=None, animals=None):
    """네온사인 한 벌. 받은 쪽과 보낸 쪽이 서로 다른 네온 색이고, 벽의 낙서도 그 색을 쓴다.

    v2·v3 는 같은 말풍선 네 가지에 색 조합과 벽(surface)만 바꾼다. face 는 벽 면색과 틈 색이다.

    look 을 주면 벽 대신 빛으로 채운 배경을 쓴다(scenes.neonbg, v6~). 그때는 dim 도 가장자리
    어둠도 안 쓴다 — 그 둘이 화면을 아련하게 흐리던 것이라 계열을 새로 판 까닭이 그것이다.
    animals 는 배경에 네온관으로 얹을 동물 셋이다(tools/zoo.py).
    """
    # room 은 채팅방·잠금화면에만 얹는 조명 같은 것. 목록은 위아래로 달라지면 머리 띠마다 층이 져서 뺀다
    wall = lambda count, dim: ('neonwall', face[0], face[1],
                               dict(dict(signs=signs, count=count, dim=dim, dim_to='#000000', wall=surface),
                                    **(room or {})))
    if look:
        # 동물 관 색은 말풍선 두 색에 낙서 셋째 색을 더해 셋이다. 배경만 다른 색을 쓰면
        # 한 화면에 네온 색이 다섯이 되어 어느 것이 말풍선인지 안 읽힌다
        bg = lambda extra: ('neonbg', face[0], face[1],
                            dict(dict(look=look, animals=animals,
                                      colors=(send, recv, signs[2][1])), **extra))
        screens = dict(chat_bg=bg({}), passcode_bg=bg({}), main_bg=bg({'bare': 1}))
    else:
        screens = dict(chat_bg=wall(5, 0.45), passcode_bg=wall(6, 0.12),
                       main_bg=('neonwall', face[0], face[1],
                                dict(signs=[], count=0, dim=0.22, dim_to='#000000', wall=surface)))
    return dict(_NEON_BASE, key='%s%d' % (slug, no), name='%s %s' % (family, variant), note=note,
                family=family, variant=variant, char_style=style, material=material,
                accent=send, accent_dim=accent_dim,
                send=(send, send), send_alt=(send, send), recv=(recv, recv), recv_alt=(recv, recv),
                send_text=send_text, recv_text=recv_text,
                # 프로필은 벽 낙서의 셋째 색까지 세 장. 탭 아이콘도 네온관이다.
                # 동물 계열만 프로필도 그 식구로 바꾼다 — 목록 화면도 테마로 읽혀야 한다
                char='neonzoo' if animals else 'neon', neon_third=signs[2][1], tab_style='neon',
                **(dict(zoo=animals) if animals else {}),
                # 목록 배경은 셀·칩·광고 카드에 잘리므로 큰 것을 빼고 질감만 둔다. 반복되는 무늬나
                # 알갱이라 어디서 잘려도 같아서 흐리지 않고(flat_list=False), 셀을 반투명하게 해 비치게 한다
                flat_list=False, cell_alpha=0.5,
                **(dict(glow_lit=True) if lit else {}),
                **screens)


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

# v2 는 셔터 내린 골목, v3 는 지하 바 타일 벽. 말풍선 네 가지는 같고 색 조합은 v1 에 없던 짝이다
_ALLEY = dict(slug='neonalley', family='네온사인 v2', face=('#2C333D', '#0E1116'), surface='shutter')
_TILE = dict(slug='neontile', family='네온사인 v3', face=('#173338', '#07100F'), surface='tile')

THEMES += [
    _neon_theme(301, '이중관', 'neon_double', 'tube', '#FF5CE1', '#3FFFD2', '#FFE0F8', '#DAFFF5',
                '#22B894', [('star', '#3FFFD2'), ('heart', '#FF5CE1'), ('bolt', '#FFD23F')],
                '셔터 내린 골목에 관 두 줄 네온. 민트와 마젠타', **_ALLEY),
    _neon_theme(302, '간판', 'neon_sign', 'sign', '#FFD23F', '#35E0FF', '#FFF6D6', '#D9F8FF',
                '#2399B0', [('bolt', '#FFD23F'), ('arrow', '#35E0FF'), ('moon', '#FF5CE1')],
                '셔터 위 금속 간판 네온. 노랑과 하늘색', **_ALLEY),
    _neon_theme(303, '전극', 'neon_electrode', 'tube', '#FF7A2F', '#4D7CFF', '#FFE6D6', '#DFE7FF',
                '#3A5CC4', [('arrow', '#FF7A2F'), ('moon', '#4D7CFF'), ('star', '#3FFFD2')],
                '셔터 골목의 전극 달린 네온관. 주황과 파랑', **_ALLEY),
    _neon_theme(304, '말꼬리', 'neon_speech', 'tube', '#B45CFF', '#4CFF88', '#EFE0FF', '#DDFFE8',
                '#2FB860', [('heart', '#B45CFF'), ('star', '#4CFF88'), ('arrow', '#FF7A2F')],
                '셔터 골목에 꼬리까지 이어진 네온. 보라와 초록', **_ALLEY),
    _neon_theme(305, '이중관', 'neon_double', 'tube', '#FFD23F', '#FF3B6B', '#FFF6D6', '#FFE0E8',
                '#C42A52', [('heart', '#FF3B6B'), ('moon', '#FFD23F'), ('star', '#35E0FF')],
                '지하 바 타일 벽에 관 두 줄 네온. 노랑과 빨강', **_TILE),
    _neon_theme(306, '간판', 'neon_sign', 'sign', '#4CFF88', '#FF3FA4', '#DDFFE8', '#FFE0F0',
                '#C42D7E', [('star', '#FF3FA4'), ('bolt', '#4CFF88'), ('moon', '#B45CFF')],
                '타일 벽 금속 간판 네온. 초록과 분홍', **_TILE),
    _neon_theme(307, '전극', 'neon_electrode', 'tube', '#35E0FF', '#FF7A2F', '#D9F8FF', '#FFE6D6',
                '#C85A1E', [('bolt', '#FF7A2F'), ('heart', '#35E0FF'), ('arrow', '#FFD23F')],
                '타일 벽의 전극 달린 네온관. 하늘색과 주황', **_TILE),
    _neon_theme(308, '말꼬리', 'neon_speech', 'tube', '#4D7CFF', '#FFD23F', '#DFE7FF', '#FFF6D6',
                '#C4A02A', [('moon', '#FFD23F'), ('star', '#4D7CFF'), ('heart', '#FF5CE1')],
                '타일 벽에 꼬리까지 이어진 네온. 파랑과 노랑', **_TILE),
]

# v4 는 말풍선부터 새로 그렸다(charbubble 의 팔각·꺾쇠·밑줄·두 가닥). 벽은 바 안쪽 나무 판자
_PLANK = dict(slug='neonbar', family='네온사인 v4', face=('#3A2A20', '#0C0806'), surface='plank', lit=True,
              room=dict(lamp=[0.5], lamp_gain=0.3, grain_light='#A8744A', contrast=0.7))

THEMES += [
    _neon_theme(309, '팔각', 'neon_octagon', 'tube', '#35E0FF', '#FF5CE1', '#D9F8FF', '#FFE0F8',
                '#C43DA8', [('bolt', '#FF5CE1'), ('star', '#35E0FF'), ('heart', '#FFD23F')],
                '모서리를 깎은 팔각 네온관. 첫 말엔 번개', **_PLANK),
    _neon_theme(310, '꺾쇠', 'neon_bracket', 'tube', '#FFD23F', '#4CFF88', '#FFF6D6', '#DDFFE8',
                '#2FB860', [('arrow', '#4CFF88'), ('moon', '#FFD23F'), ('star', '#FF3FA4')],
                '네 모서리에만 불이 들어온 꺾쇠 네온', **_PLANK),
    _neon_theme(311, '밑줄', 'neon_underline', 'tube', '#B45CFF', '#FF7A2F', '#EFE0FF', '#FFE6D6',
                '#C85A1E', [('heart', '#FF7A2F'), ('moon', '#B45CFF'), ('bolt', '#35E0FF')],
                '아래변만 빛나고 양끝이 말려 올라간 네온', **_PLANK),
    _neon_theme(312, '두 가닥', 'neon_split', 'tube', '#FF3B6B', '#35E0FF', '#FFE0E8', '#D9F8FF',
                '#2399B0', [('star', '#35E0FF'), ('heart', '#FF3B6B'), ('moon', '#FFD23F')],
                '두 색 관이 모서리 틈에서 갈리는 네온', **_PLANK),
]

# v5 는 v4 의 말풍선 네 가지를 짙은 미장 벽에 건다. 잎 벽은 요란해 네온과 다퉈서, 무늬 없는 벽에
# 위쪽 간접등만 두고 낙서도 셋으로 줄였다 — 고급 레스토랑 벽의 네온사인이다
_LOUNGE = dict(slug='neonlounge', family='네온사인 v5', face=('#2A2826', '#121110'), surface='plaster', lit=True,
               room=dict(wash_lamps=[0.22, 0.78], lamp_gain=0.55, count=3))

THEMES += [
    _neon_theme(313, '팔각', 'neon_octagon', 'tube', '#FF5CE1', '#FFD23F', '#FFE0F8', '#FFF6D6',
                '#C4A02A', [('star', '#FFD23F'), ('heart', '#FF5CE1'), ('moon', '#35E0FF')],
                '미장 벽에 걸린 팔각 네온관. 분홍과 노랑', **_LOUNGE),
    _neon_theme(314, '꺾쇠', 'neon_bracket', 'tube', '#35E0FF', '#FF7A2F', '#D9F8FF', '#FFE6D6',
                '#C85A1E', [('moon', '#35E0FF'), ('bolt', '#FF7A2F'), ('heart', '#FF5CE1')],
                '미장 벽에 모서리만 켜진 꺾쇠 네온. 하늘색과 주황', **_LOUNGE),
    _neon_theme(315, '밑줄', 'neon_underline', 'tube', '#B45CFF', '#FFD23F', '#EFE0FF', '#FFF6D6',
                '#C4A02A', [('star', '#FFD23F'), ('moon', '#B45CFF'), ('heart', '#FF3B6B')],
                '미장 벽에 아래변만 빛나는 네온. 보라와 노랑', **_LOUNGE),
    _neon_theme(316, '두 가닥', 'neon_split', 'tube', '#4D7CFF', '#FF5CE1', '#DFE7FF', '#FFE0F8',
                '#C43DA8', [('heart', '#FF5CE1'), ('star', '#4D7CFF'), ('bolt', '#FFD23F')],
                '미장 벽에 두 색 관이 갈리는 네온. 파랑과 분홍', **_LOUNGE),
]

# v6~ 는 벽을 걷어내고 빛으로 채운 배경에 건다(scenes.neonbg). v1~v5 가 다섯 계열 모두 벽이라
# 한 카테고리 안에서 서로 구분이 잘 안 됐다 — 벽돌·셔터·타일·판자·미장은 다 '어두운 벽'이다.
#
# 무엇이 달라졌나. neonwall 은 dim 0.45 와 가장자리 어둠을 붙여서 벽을 무엇으로 바꿔도 화면이
# 아련하게 흐려졌다. neonbg 는 둘 다 안 쓰고, 목록도 흐리지 않고 알갱이층만 남겨 깐다.
# 기존 다섯 계열은 neonwall 그대로라 그림이 한 픽셀도 안 바뀐다.
#
# **말풍선 네 가지는 v4·v5 와 같고 배경과 색 조합만 바꾼다.** v2·v3 가 벽만 바꾼 것과 같은 축이다.
# 색은 계열마다 한 벌씩이고 v1~v5 에 없던 짝으로 준다 — 시안 열두 벌에서 골랐다.
_LOOK = dict(lit=True, face=('#0A0A12', '#050508'))


def _neon_look(no, slug, family, look, recv, send, recv_text, send_text, dim, third, notes,
               animals=None):
    """배경 하나를 말풍선 네 가지에 입힌 계열. 넷을 한꺼번에 만든다.

    notes 는 네 벌의 한 줄 소개다. 낙서(signs)는 neonbg 가 안 그리지만 셋째 색을 프로필이
    쓰므로 그대로 넘긴다.
    """
    signs = [('star', send), ('heart', recv), ('moon', third)]
    four = (('팔각', 'neon_octagon'), ('꺾쇠', 'neon_bracket'),
            ('밑줄', 'neon_underline'), ('두 가닥', 'neon_split'))
    return [_neon_theme(no + i, variant, style, 'tube', recv, send, recv_text, send_text, dim,
                        signs, notes[i], slug=slug, family=family, look=look,
                        animals=(animals[i] if animals else None), **_LOOK)
            for i, (variant, style) in enumerate(four)]


THEMES += _neon_look(
    401, 'neonstar', '네온사인 v6', 'star', '#8AD8FF', '#FFA8D8', '#E5F6FF', '#FFECF6',
    '#B7799B', '#FFD23F',
    ['별자리 밤하늘에 걸린 팔각 네온관. 연하늘과 연분홍',
     '은하수 위 모서리만 켜진 꺾쇠 네온. 파스텔',
     '별자리 아래 밑줄만 빛나는 네온. 연분홍',
     '별자리 밤하늘에 두 색 관이 갈리는 네온'])

THEMES += _neon_look(
    405, 'neonpetal', '네온사인 v7', 'petal', '#FF8AD4', '#B58AFF', '#FFE5F5', '#EFE5FF',
    '#8263B7', '#8AE0FF',
    ['흐린 꽃잎이 떠다니는 어둠에 팔각 네온관',
     '꽃잎 사이 모서리만 켜진 꺾쇠 네온. 분홍과 보라',
     '꽃잎 어둠에 밑줄만 빛나는 네온',
     '꽃잎 사이로 두 색 관이 갈리는 네온'])

THEMES += _neon_look(
    409, 'neonbokeh', '네온사인 v8', 'bokeh', '#E8F2FF', '#FF5CE1', '#FAFCFF', '#FFDBF8',
    '#B742A2', '#8AD8FF',
    ['초점 나간 빛 동그라미 위 팔각 네온관',
     '보케 위 모서리만 켜진 꺾쇠 네온. 흰빛과 분홍',
     '보케 위 밑줄만 빛나는 네온',
     '보케 위로 두 색 관이 갈리는 네온'])

THEMES += _neon_look(
    413, 'neonplasma', '네온사인 v9', 'plasma', '#B8FF3F', '#9B5CFF', '#EFFFD5', '#E9DBFF',
    '#6F42B7', '#FF5CE1',
    ['뻗어 나가는 플라즈마 실에 팔각 네온관',
     '플라즈마 위 모서리만 켜진 꺾쇠 네온. 라임과 보라',
     '플라즈마 위 밑줄만 빛나는 네온',
     '플라즈마 위로 두 색 관이 갈리는 네온'])

THEMES += _neon_look(
    417, 'neonink', '네온사인 v10', 'ink', '#3FFFD2', '#FF3FA4', '#D5FFF5', '#FFD5EB',
    '#B72D76', '#FFD23F',
    ['번진 잉크 위에 걸린 팔각 네온관',
     '잉크 위 모서리만 켜진 꺾쇠 네온. 민트와 자홍',
     '번진 잉크에 밑줄만 빛나는 네온',
     '잉크 위로 두 색 관이 갈리는 네온'])

THEMES += _neon_look(
    421, 'neonmesh', '네온사인 v11', 'mesh', '#35E0FF', '#FF7A6B', '#D3F8FF', '#FFE2DE',
    '#B7574D', '#FFD23F',
    ['레이저 그물 위에 걸린 팔각 네온관',
     '그물 위 모서리만 켜진 꺾쇠 네온. 하늘색과 산호',
     '레이저 그물에 밑줄만 빛나는 네온',
     '그물 위로 두 색 관이 갈리는 네온'])

THEMES += _neon_look(
    425, 'neoncrystal', '네온사인 v12', 'crystal', '#FFB03F', '#6A5CFF', '#FFEED5', '#DEDBFF',
    '#4C42B7', '#3FFFD2',
    ['겹친 크리스탈 조각 위 팔각 네온관',
     '조각 위 모서리만 켜진 꺾쇠 네온. 호박과 남보라',
     '크리스탈 조각에 밑줄만 빛나는 네온',
     '조각 위로 두 색 관이 갈리는 네온'])

THEMES += _neon_look(
    429, 'neonchroma', '네온사인 v13', 'chroma', '#FF3B4E', '#2FE6D2', '#FFD4D8', '#D1F9F5',
    '#22A597', '#FFD23F',
    ['세 색으로 어긋난 덩이 위 팔각 네온관',
     '색수차 위 모서리만 켜진 꺾쇠 네온. 빨강과 청록',
     '색수차 위에 밑줄만 빛나는 네온',
     '색수차 위로 두 색 관이 갈리는 네온'])

# 동물 계열만 변형 축이 다르다. 말풍선은 두 가닥 하나로 고정하고 네 벌을 식구로 가른다 —
# 고르는 사람이 여기서 궁금한 것은 관 모양이 아니라 어느 동물이 걸려 있느냐다.
# 프로필 세 장도 그 식구가 된다(charbubble.p_neonzoo). 배경은 가장 조용한 별자리로 고정한다 —
# 동물이 주인공이라 배경이 세면 서로 다툰다.
_ZOO_PACKS = [zoo_pack for zoo_pack in (('jelly', 'whale', 'octopus'),
                                        ('owl', 'fox', 'deer'),
                                        ('penguin', 'bear', 'seahorse'),
                                        ('butterfly', 'jelly', 'owl'))]

THEMES += [
    _neon_theme(433 + i, variant, 'neon_split', 'tube', '#FF8A3F', '#3FD6C8', '#FFE5D5', '#D5F6F3',
                '#2D9A90', [('star', '#3FD6C8'), ('heart', '#FF8A3F'), ('moon', '#FFD23F')],
                note, slug='neonzoo', family='네온 동물', look='star', animals=pack, **_LOOK)
    for i, (variant, pack, note) in enumerate([
        ('바다', _ZOO_PACKS[0], '별밤에 걸린 해파리·고래·문어 네온관'),
        ('숲', _ZOO_PACKS[1], '별밤에 걸린 부엉이·여우·사슴 네온관'),
        ('얼음', _ZOO_PACKS[2], '별밤에 걸린 펭귄·곰·해마 네온관'),
        ('모둠', _ZOO_PACKS[3], '별밤에 걸린 나비·해파리·부엉이 네온관'),
    ])
]

# --- 도트 모험 --------------------------------------------------------------
# 옛날 RPG 의 대화창. 오락실이 옆에서 본 픽셀 풍경에 둥근 픽셀 말풍선이라, 여기는 위에서 본 들판과
# 던전에 모서리를 계단으로 깎은 네모 창으로 갈랐다. 밝음은 양피지색 창, 어두움은 남색 창에 흰 안쪽 테.
# 프로필은 눈 달린 도트 보물상자. 도트는 한 칸이 정수 픽셀이어야 계단이 또렷해서 확대는 NEAREST 로 한다.

_QUEST_FIELD = _scenes('quest', '#8FCB6A', '#7DBB5A',
                       dict(mode='field', path='#E3C88E', path_edge='#C9A96A', leaf='#4E9A4A',
                            leaf_dark='#2F6B34', trunk='#8A5A2E', trees=10, pond='#6EC3E8',
                            flowers=['#FFF3A8', '#FFB3C7', '#FFFFFF'], dim_to='#FFFFFF'),
                       (0.35, 0.5, 0.05))
_QUEST_DUNGEON = _scenes('quest', '#3E4158', '#23243A',
                         dict(mode='dungeon', wall='#4A4266', torch='#FFB347', chests=2, braziers=3,
                              dim_to='#000000'),
                         (0.12, 0.3, 0.0))
# 목록 배경은 흐리면 도트가 뭉개져 그냥 단색 판이 됐다. 길·나무·상자·화로를 빼고 바닥 질감만 남기면
# 어디서 잘려도 같은 무늬라 흐리지 않고 깔 수 있다(flat_list=False, 네온사인 벽돌과 같은 방식)
_QUEST_FIELD['main_bg'] = ('quest', '#8FCB6A', '#7DBB5A',
                           dict(mode='field', bare=True, flowers=['#FFF3A8', '#FFB3C7', '#FFFFFF'],
                                dim=0.3, dim_to='#FFFFFF'))
_QUEST_DUNGEON['main_bg'] = ('quest', '#3E4158', '#23243A',
                             dict(mode='dungeon', bare=True, dim=0.2, dim_to='#000000'))

THEMES += character(
    'quest', 149, '도트 모험',
    dict(char_style='rpg', char='chest', flat_list=False),
    dict(bg='#F4EEDC', bg_deep='#EDE5CE', surface='#FBF7EA', pressed='#E6DCC0',
         border='#D8CCAA', text='#2E2418', subtext='#7A6A52',
         accent='#3F7FD9', accent_dim='#2F66B8', on_accent='#FFFFFF',
         recv='#FFFDF4', recv_alt='#F1E6C8', send='#CFE3FF', send_alt='#FFDDB0',
         recv_text='#2E2418', send_text='#1B2A44',
         char_outline='#2E2418', char_backs=('#E3F0CF', '#FFE4BF', '#D9E6FF')),
    dict(bg='#12142A', bg_deep='#0D0F20', surface='#1A1D38', pressed='#242848',
         border='#2E3358', text='#EEF0FF', subtext='#9A9EC8',
         accent='#FFD24A', accent_dim='#E0B02A', on_accent='#1A1406',
         recv='#22307A', recv_alt='#2C3C8F', send='#6A2C7A', send_alt='#2C6A5A',
         recv_text='#F2F4FF', send_text='#FFF2FF',
         char_outline='#07081A', win_rim='#E8ECFF',
         char_backs=('#26336A', '#43295C', '#234A44')),
    _QUEST_FIELD, _QUEST_DUNGEON,
    ['양피지색 바탕에 도트 대화창. 첫 말엔 ▼ 커서',
     '위에서 본 도트 들판과 오솔길',
     '남색 대화창에 흰 안쪽 테. 옛날 RPG 밤 화면',
     '화로 켜진 던전. 대화창에 불빛이 비침'],
    # 던전의 화로 불빛이 대화창에 비친다. 빛의 출처가 화면에 있는 이 변형에만 넣는다(캠핑과 같은 규칙)
    extra={'어두움+배경': dict(glow_style='soft', char_glow_color='#FFB347',
                               firelight='#FFB347', firelight_k=1.0)})

# --- 도트 액정 · 레트로 PC · 도트 농장 ----------------------------------------
# 픽셀 카테고리의 나머지 셋. 넷 모두 목록 배경은 바닥 질감만 흐리지 않고 깐다(도트 모험과 같다).


def _bare(spec, dim):
    """목록 배경용으로 같은 장면의 질감만 남긴다."""
    return (spec[0], spec[1], spec[2], dict(spec[3], bare=True, dim=dim))


_LCD_SHADES_L = ['#DCEBB0', '#A8C878', '#5E8A48', '#203820']
_LCD_SHADES_D = ['#0E1A12', '#1E3A26', '#2F6A34', '#6FC060']
_LCD_L = _scenes('lcd', '#DCEBB0', '#C8DC98', dict(shades=_LCD_SHADES_L, dim_to='#FFFFFF'),
                 (0.15, 0.35, 0.0))
_LCD_D = _scenes('lcd', '#0E1A12', '#15261A', dict(shades=_LCD_SHADES_D, gap=1.35, dim_to='#000000'),
                 (0.05, 0.25, 0.0))
_LCD_L['main_bg'] = _bare(_LCD_L['main_bg'], 0.25)
_LCD_D['main_bg'] = _bare(_LCD_D['main_bg'], 0.15)

THEMES += character(
    'lcd', 153, '도트 액정',
    dict(char_style='lcd', char='frog', flat_list=False),
    dict(bg='#DCEBB0', bg_deep='#D2E3A2', surface='#E8F4C4', pressed='#C4D994',
         border='#B4CC84', text='#1E3218', subtext='#557048',
         accent='#3C6A30', accent_dim='#2E5424', on_accent='#E8F4C4',
         recv='#EAF5C8', recv_alt='#CFE3A0', send='#9CC47A', send_alt='#B8D690',
         recv_text='#1E3218', send_text='#14240F',
         char_outline='#203820', sprite_mid='#6FA05A', sprite_light='#B7D88C', sprite_hi='#F0F8D8',
         char_backs=('#C8DE9A', '#B6D08A', '#D8EAB0')),
    dict(bg='#0E1A12', bg_deep='#0A140D', surface='#14241A', pressed='#1C3224',
         border='#244030', text='#C8F0A8', subtext='#6F9A70',
         accent='#8FE070', accent_dim='#6CC050', on_accent='#0A140D',
         recv='#1E3A26', recv_alt='#28503A', send='#3E7A3A', send_alt='#2A5E4A',
         recv_text='#D8F8C0', send_text='#E8FFD8',
         char_outline='#050A06', sprite_mid='#5FB060', sprite_light='#9BE08A', sprite_hi='#E0FFD0',
         char_backs=('#1C3A26', '#243F2A', '#16301F')),
    _LCD_L, _LCD_D,
    ['연둣빛 액정에 도트 말풍선. 첫 말엔 하트',
     '네 가지 초록만 쓰는 액정 속 언덕',
     '백라이트 켠 어두운 액정에 초록 도트',
     '불 켜진 액정 화면 속 도트 언덕'])

_PC_L = _scenes('desktop', '#3A8C8C', '#327A7A',
                dict(title='#2A4FA8', screen='#7FD6E6', dim_to='#FFFFFF'), (0.1, 0.35, 0.0))
_PC_D = _scenes('desktop', '#1C2446', '#18203E',
                dict(panel='#3A4256', panel_hi='#5A6480', panel_lo='#20263A', ink='#05070B',
                     title='#5A86E8', screen='#4FA8C8', dim_to='#000000'), (0.05, 0.25, 0.0))
_PC_L['main_bg'] = _bare(_PC_L['main_bg'], 0.45)
_PC_D['main_bg'] = _bare(_PC_D['main_bg'], 0.2)

THEMES += character(
    'retro', 157, '레트로 PC',
    dict(char_style='window', char='floppy', flat_list=False),
    dict(bg='#DCDFE3', bg_deep='#D2D6DB', surface='#EEF0F2', pressed='#C8CDD4',
         border='#B8BEC6', text='#1A1D22', subtext='#5C636E',
         accent='#2A4FA8', accent_dim='#203E86', on_accent='#FFFFFF',
         recv='#F4F4F4', recv_alt='#E2E4E8', send='#CFE0FF', send_alt='#FFF0B8',
         recv_text='#1A1D22', send_text='#10224A',
         char_outline='#14161A', char_backs=('#D8E6FF', '#E6E8EC', '#FFF0C8')),
    dict(bg='#10141E', bg_deep='#0B0E16', surface='#171C28', pressed='#212838',
         border='#2A3244', text='#E6EAF2', subtext='#8A93A6',
         accent='#5A86E8', accent_dim='#4468C0', on_accent='#0B0E16',
         recv='#232A3A', recv_alt='#2E3648', send='#2F4E8C', send_alt='#5A4A1E',
         recv_text='#E6EAF2', send_text='#F0F4FF',
         char_outline='#05070B', char_backs=('#223050', '#2A3040', '#3A3420')),
    _PC_L, _PC_D,
    ['회색 창 말풍선. 첫 말엔 제목 표시줄과 닫기 단추',
     '청록 바탕화면에 도트 아이콘과 작업 표시줄',
     '어두운 창 말풍선. 밤에 켠 옛 컴퓨터',
     '남색 바탕화면에 도트 아이콘'])

_FARM_L = _scenes('farm', '#8CC56A', '#7AB45A',
                  dict(soil='#A8744A', soil_dark='#855836', sprout='#3E8A30', fence='#D8B07A',
                       plots=4, dim_to='#FFFFFF'), (0.3, 0.45, 0.05))
_FARM_D = _scenes('farm', '#22341D', '#1C2C18',
                  dict(soil='#3E2E1E', soil_dark='#2C2016', sprout='#3E6A30', fence='#6A5638',
                       plots=4, fireflies=36, firefly='#FFE36A', dim_to='#000000'), (0.05, 0.25, 0.0))
_FARM_L['main_bg'] = _bare(_FARM_L['main_bg'], 0.35)
_FARM_D['main_bg'] = _bare(_FARM_D['main_bg'], 0.15)

THEMES += character(
    'farm', 161, '도트 농장',
    dict(char_style='board', char='turnip', flat_list=False),
    dict(bg='#F2F0DC', bg_deep='#EAE6CC', surface='#FAF8EA', pressed='#E2DCBE',
         border='#D4CCA8', text='#2E2A18', subtext='#7A7050',
         accent='#5A9A3A', accent_dim='#467E2C', on_accent='#FFFFFF',
         recv='#F6E7C8', recv_alt='#EAD4A8', send='#D4EAB0', send_alt='#FFD9A8',
         recv_text='#3A2A14', send_text='#22330F',
         char_outline='#3A2A14', char_backs=('#DDEFC4', '#F6E2C2', '#E8E0F2')),
    dict(bg='#141A10', bg_deep='#0F140C', surface='#1C2416', pressed='#26301E',
         border='#303C26', text='#EEF2DC', subtext='#99A184',
         accent='#F2D35A', accent_dim='#D4B43C', on_accent='#141A10',
         recv='#3A2E1E', recv_alt='#4A3A26', send='#2E4A26', send_alt='#4A3A5A',
         recv_text='#F4EAD4', send_text='#E8F6DC',
         char_outline='#080A06', char_backs=('#24361E', '#3A2E22', '#2E2A3A')),
    _FARM_L, _FARM_D,
    ['나무 팻말 말풍선. 첫 말엔 새싹이 돋음',
     '위에서 본 밭고랑과 울타리',
     '밤 농장. 어두운 팻말 말풍선',
     '반딧불 날리는 밤 밭'])

# --- 편안함: 수채화 · 수묵화 · 비 오는 창가 · 페이퍼컷 -----------------------------------------
# 네온·원색 계열이 눈 아프다는 의견이 있어 편안함을 채웠다. 처음엔 눈 편함을 채도·대비를 덜어내는 것으로만
# 풀어 종이·린넨·새벽·노을·독서등 다섯을 만들었는데, 색만 다른 회색 판이 줄지어 사용자가 "딱 봤을 때
# 다운받고 싶지 않다" 고 했다. 콘셉트 시안 넷을 한 장씩 그려 고른 뒤 계열로 만들었다 — 그림 스타일은
# 분명하게, 색과 명암 폭은 좁게. 네 벌은 밝음/어두움 × 그림 유무이고 말풍선 모양은 계열마다 다르다.
# 채도·대비는 카테고리 규칙이 잰다(_check_comfort). 캐릭터가 없어 프로필은 계열 모티프다.

THEMES += character(
    'watercolor', 165, '수채화', dict(char_style='wash'),
    dict(bg='#F1EDE4', bg_deep='#E6DFD2', surface='#F8F5EF', pressed='#DFD8CA',
         border='#D3CBBB', text='#3A3833', subtext='#76726A', accent='#7C8A70',
         accent_dim='#65725A', on_accent='#F8F5EF', recv='#FBF9F4', recv_alt='#EDE8DE',
         send='#C0CAB7', send_alt='#E4DFCF', recv_text='#3A3833', send_text='#2D3228',
         char_outline='#A9B39C'),
    dict(bg='#24272B', bg_deep='#1D2024', surface='#2C3035', pressed='#353A40',
         border='#3E434A', text='#E1E3DE', subtext='#999D97', accent='#9DA893',
         accent_dim='#808B77', on_accent='#1D2024', recv='#2E3237', recv_alt='#383D42',
         send='#434F3E', send_alt='#4E5448', recv_text='#E1E3DE', send_text='#EEF1EA',
         char_outline='#6E7868'),
    _scenes('watercolor', '#F3EFE6', '#D8D1C3',
            dict(sky='#C6D3DC', hills=['#B3C2C4', '#B7C3A2', '#C9C49C', '#AEAC86'], trees='#8FA088',
                 dim_to='#F1EDE4'), (0.0, 0.3, 0.0)),
    _scenes('watercolor', '#23272C', '#2E3238',
            dict(dark=True, sky='#2E3A48', hills=['#2C3838', '#303A2E', '#363A2C', '#2E3226'], trees='#2A3428',
                 moon='#8A93A0', dim_to='#1D2024'), (0.0, 0.3, 0.0)),
    ['물감 번진 말풍선. 첫 말엔 물감 방울',
     '종이결 위로 물감이 번진 언덕과 나무',
     '어두운 종이에 물감 말풍선',
     '달 뜬 밤, 물감으로 칠한 들판'])

THEMES += character(
    'inkwash', 169, '수묵화', dict(char_style='hanji'),
    dict(bg='#EEEAE1', bg_deep='#E4DFD4', surface='#F6F3EC', pressed='#DDD7CA',
         border='#D1CABB', text='#2F2D2A', subtext='#6F6A62', accent='#6E6860',
         accent_dim='#57524B', on_accent='#F6F3EC', recv='#FAF8F3', recv_alt='#ECE8DF',
         send='#CBC6BA', send_alt='#E2DDD2', recv_text='#2F2D2A', send_text='#262421',
         char_outline='#4A4640', seal='#A85A4E'),
    dict(bg='#24221F', bg_deep='#1D1B19', surface='#2C2A27', pressed='#35322E',
         border='#3E3B36', text='#E4DFD6', subtext='#9C968D', accent='#A59E93',
         accent_dim='#878075', on_accent='#1D1B19', recv='#33302C', recv_alt='#393633',
         send='#4A4641', send_alt='#54504A', recv_text='#E4DFD6', send_text='#F0ECE4',
         char_outline='#8A847A', seal='#8C4E44'),
    _scenes('inkwash', '#EEEAE1', '#D4CDBE',
            dict(ink='#2E2C29', mist='#EEEAE1', seal='#A85A4E', dim_to='#EEEAE1'), (0.0, 0.3, 0.0)),
    _scenes('inkwash', '#262420', '#34312C',
            dict(ink='#0E0D0B', mist='#2E2B27', moon='#CFC8BA', bird='#8A847A', seal='#8C4E44',
                 dim_to='#1D1B19'), (0.0, 0.3, 0.0)),
    ['한지 말풍선에 먹선. 첫 말엔 붉은 낙관',
     '먹이 번진 겹겹 산자락과 안개',
     '먹빛 바탕에 한지 말풍선',
     '달밤, 짙은 먹 산 위로 달이 뜸'])

THEMES += character(
    'rainy', 173, '비 오는 창가', dict(char_style='frost'),
    dict(bg='#E6E9EC', bg_deep='#DADFE3', surface='#F1F3F5', pressed='#D1D7DC',
         border='#C5CCD2', text='#2F343A', subtext='#6B727A', accent='#6F8090',
         accent_dim='#586878', on_accent='#F1F3F5', recv='#F6F8FA', recv_alt='#E4E8EC',
         send='#BDC7D0', send_alt='#D2D9E0', recv_text='#2F343A', send_text='#242A30',
         char_outline='#9AA5AF'),
    dict(bg='#202329', bg_deep='#1B1D22', surface='#272B32', pressed='#30353E',
         border='#373E49', text='#DDE3EA', subtext='#8E97A2', accent='#8FA3B5',
         accent_dim='#72869A', on_accent='#191D24', recv='#2C3139', recv_alt='#343A43',
         send='#3F4752', send_alt='#47505C', recv_text='#DDE3EA', send_text='#EAF0F6',
         char_outline='#11141A'),
    _scenes('rainwindow', '#DDE2E7', '#CDD3D9',
            dict(dark=False, bokeh=['#FFF4E4', '#EEF4FA', '#FFFFFF', '#F4EEF6'], dim_to='#E6E9EC'),
            (0.0, 0.3, 0.0)),
    _scenes('rainwindow', '#1A1F27', '#2A2F38',
            dict(dark=True, bokeh=['#9C8A6A', '#6E7E92', '#8A7A80', '#A8977A', '#6A8288'], dim_to='#191D24'),
            (0.0, 0.3, 0.0)),
    ['김 서린 유리 말풍선. 첫 말엔 물방울',
     '흐린 낮, 빗방울 너머 번진 거리',
     '어두운 유리 말풍선에 맺힌 물방울',
     '비 오는 밤 창밖으로 번진 불빛'])

THEMES += character(
    'papercut', 177, '페이퍼컷', dict(char_style='cutpaper'),
    dict(bg='#ECE6DC', bg_deep='#E2DACC', surface='#F5F1EA', pressed='#DBD2C4',
         border='#CFC5B5', text='#38342E', subtext='#766F66', accent='#7C8B80',
         accent_dim='#657368', on_accent='#F5F1EA', recv='#F9F6F0', recv_alt='#EDE7DD',
         send='#BDC7BE', send_alt='#E3DBCB', recv_text='#38342E', send_text='#2A302B',
         char_outline='#BDB3A3', paper_shadow='#5C544B'),
    dict(bg='#22252C', bg_deep='#1B1E23', surface='#2A2E35', pressed='#33373F',
         border='#3C414A', text='#DFE1E4', subtext='#969AA1', accent='#9AA7A0',
         accent_dim='#7D8A83', on_accent='#1B1E24', recv='#2D3138', recv_alt='#373B42',
         send='#3F4A45', send_alt='#4A4E55', recv_text='#DFE1E4', send_text='#ECEFF0',
         char_outline='#0F1115', paper_shadow='#050608'),
    _scenes('papercut', '#E9E3D9', '#EFE6DA',
            dict(layers=['#D8DBD5', '#C9D0C8', '#BAC3B9', '#ABB5A9', '#9CA79A'], sun='#F3EADC',
                 cloud='#F4F0EA', shadow='#6E655C', trees=6, dim_to='#ECE6DC'), (0.0, 0.3, 0.0)),
    _scenes('papercut', '#1C2029', '#262A34',
            dict(layers=['#2B303A', '#272C35', '#232730', '#1F232B', '#1B1E25'], sun='#C9C4B8',
                 cloud='#343A45', star='#8C93A0', shadow='#050608', trees=6, stars=60,
                 dim_to='#1B1E24'), (0.0, 0.3, 0.0)),
    ['그림자 진 종이 말풍선. 첫 말엔 접힌 귀퉁이',
     '오려 겹친 종이 능선과 해, 구름',
     '어두운 종이 말풍선',
     '별 뜬 밤, 층층이 오린 종이 산'])


# --- 무늬: 깅엄 · 폴카 · 테라조 · 마린 · 체커보드 ------------------------------------
# 무늬 카테고리의 새 계열도 밝음/어두움 × 배경 축이다. 배경은 반복 무늬라 목록에서도 흐리지 않고
# (flat_list), 프로필 판에 같은 무늬를 옅게 깐다(motif_tile) — 단색 판이면 목록이 다른 무늬 계열과 같아 보인다.
# 무늬 이름은 scenes, 말풍선은 charbubble 의 같은 이름이다.

THEMES += character(
    'gingham', 181, '깅엄 체크', dict(char_style='bow', flat_list=False, motif_tile='gingham'),
    dict(bg='#F4F1EC', bg_deep='#EFEBE4', surface='#FBFAF7', pressed='#E4DED4',
         border='#DAD3C8', text='#2F3A44', subtext='#6E7A84', accent='#5C86A6',
         accent_dim='#4A6E8A', on_accent='#FFFFFF', recv='#FFFFFF', recv_alt='#EEF3F7',
         send='#CFE0EC', send_alt='#E4ECF2', recv_text='#2F3A44', send_text='#23303B',
         char_outline='#8BA3B5'),
    dict(bg='#1E242B', bg_deep='#191E24', surface='#262D35', pressed='#2F3741',
         border='#38414C', text='#E6ECF1', subtext='#94A0AB', accent='#8DB4D3',
         accent_dim='#6F97B8', on_accent='#16202A', recv='#2A323B', recv_alt='#343D47',
         send='#3D5468', send_alt='#475B6C', recv_text='#E6ECF1', send_text='#EEF4F9',
         char_outline='#6F8597'),
    _scenes('gingham', '#F6F3EE', '#9FB8C9', dict(dim_to='#F4F1EC'), (0.0, 0.25, 0.0)),
    _scenes('gingham', '#1E242B', '#3A5064', dict(dim_to='#1E242B'), (0.0, 0.25, 0.0)),
    ['크림 바탕에 리본 단 말풍선',
     '하늘색 깅엄 체크 식탁보',
     '어두운 바탕에 리본 단 말풍선',
     '밤의 남색 깅엄 체크'])

THEMES += character(
    'polka', 185, '폴카 도트', dict(char_style='pill', flat_list=False, motif_tile='polka'),
    dict(bg='#F7EEDC', bg_deep='#F2E6D0', surface='#FCF7EE', pressed='#EADCC2',
         border='#E0D0B3', text='#4A3428', subtext='#8A7262', accent='#D9776A',
         accent_dim='#B85F54', on_accent='#FFFFFF', recv='#FFFBF4', recv_alt='#F3E7D3',
         send='#F2C9BE', send_alt='#F6DCCF', recv_text='#4A3428', send_text='#3E2A20',
         char_outline='#C9A28F'),
    dict(bg='#2A2220', bg_deep='#231C1A', surface='#342B28', pressed='#3E3330',
         border='#4A3E3A', text='#F2E6DC', subtext='#AD9A8E', accent='#E58F80',
         accent_dim='#C77668', on_accent='#2A1A16', recv='#3A302C', recv_alt='#453935',
         send='#6E3F39', send_alt='#5E4540', recv_text='#F2E6DC', send_text='#FFEDE8',
         char_outline='#9A7F72'),
    _scenes('polka', '#F7EEDC', '#E7B8A8', dict(dim_to='#F7EEDC'), (0.0, 0.25, 0.0)),
    _scenes('polka', '#2A2220', '#4E3A34', dict(dim_to='#2A2220'), (0.0, 0.25, 0.0)),
    ['크림 바탕에 알약 말풍선. 첫 말엔 물방울 셋',
     '크림 바탕에 산호색 물방울 무늬',
     '짙은 갈색 바탕에 알약 말풍선',
     '짙은 갈색에 옅은 물방울 무늬'])

THEMES += character(
    'terrazzo', 189, '테라조', dict(char_style='chips', flat_list=False, motif_tile='terrazzo'),
    dict(bg='#F2EFEA', bg_deep='#ECE8E1', surface='#FAF8F5', pressed='#E2DDD4',
         border='#D8D2C8', text='#34312D', subtext='#77716A', accent='#C9785B',
         accent_dim='#A86148', on_accent='#FFFFFF', recv='#FFFFFF', recv_alt='#EEEAE3',
         send='#E9D9CC', send_alt='#DCE3DB', recv_text='#34312D', send_text='#2B2723',
         char_outline='#B9B1A6', chips3=['#E3A488', '#9BB6A5', '#E9C77E']),
    dict(bg='#2A2826', bg_deep='#23211F', surface='#33302D', pressed='#3D3A36',
         border='#48443F', text='#EDE8E1', subtext='#A39C93', accent='#D98E70',
         accent_dim='#BA7458', on_accent='#241510', recv='#35322E', recv_alt='#3F3B37',
         send='#5A4538', send_alt='#3F4A42', recv_text='#EDE8E1', send_text='#F5EEE7',
         char_outline='#7A736A', chips3=['#B97F66', '#6E8A79', '#B89A5C']),
    _scenes('terrazzo', '#F2EFEA', '#E6E1D9',
            dict(chips=['#E3A488', '#9BB6A5', '#E9C77E', '#8FA3C0', '#D98E84', '#C9C2B6'], dim_to='#F2EFEA'),
            (0.0, 0.25, 0.0)),
    _scenes('terrazzo', '#2A2826', '#3A3734',
            dict(chips=['#B97F66', '#6E8A79', '#B89A5C', '#6A7C99', '#A86E66', '#5A5650'], dim_to='#2A2826'),
            (0.0, 0.25, 0.0)),
    ['돌 조각이 박힌 말풍선',
     '알록달록 돌 조각이 박힌 바닥',
     '짙은 돌 바탕에 조각 박힌 말풍선',
     '어두운 돌에 박힌 조각들'])

THEMES += character(
    'marine', 193, '마린 스트라이프', dict(char_style='band', flat_list=False, motif_tile='stripes'),
    dict(bg='#F4F6F8', bg_deep='#EEF2F6', surface='#FFFFFF', pressed='#E1E7EE',
         border='#D5DDE6', text='#1E2B40', subtext='#65738A', accent='#2B4A7A',
         accent_dim='#223C63', on_accent='#FFFFFF', recv='#FFFFFF', recv_alt='#E8EEF5',
         send='#DCE6F2', send_alt='#F6E4E2', recv_text='#1E2B40', send_text='#17243A',
         char_outline='#9AABC2', band='#2B4A7A'),
    dict(bg='#172033', bg_deep='#131B2B', surface='#1E283D', pressed='#263149',
         border='#2F3B55', text='#E7ECF4', subtext='#8F9BB2', accent='#7F9FD1',
         accent_dim='#6583B5', on_accent='#131B2B', recv='#222D44', recv_alt='#2B3752',
         send='#3A5078', send_alt='#5A3A48', recv_text='#E7ECF4', send_text='#F2F5FA',
         char_outline='#5B6A88', band='#6D8CC0'),
    _scenes('stripes', '#F7F9FB', '#BFD0E4', dict(dim_to='#F4F6F8'), (0.0, 0.25, 0.0)),
    _scenes('stripes', '#172033', '#243556', dict(dim_to='#172033'), (0.0, 0.25, 0.0)),
    ['남색 띠를 두른 말풍선',
     '흰 바탕에 남색 줄무늬',
     '밤바다색 바탕에 띠 두른 말풍선',
     '짙은 남색 줄무늬'])

THEMES += character(
    'checker', 197, '체커보드', dict(char_style='flag', flat_list=False, motif_tile='checker'),
    dict(bg='#F3EEF8', bg_deep='#EEE8F5', surface='#FBF9FD', pressed='#E3DBEE',
         border='#D9CFE8', text='#3A3148', subtext='#7B7189', accent='#8A6FB8',
         accent_dim='#735A9C', on_accent='#FFFFFF', recv='#FFFFFF', recv_alt='#F0EAF7',
         send='#DCD0EE', send_alt='#F4DDE6', recv_text='#3A3148', send_text='#2F273C',
         char_outline='#B3A6C6'),
    dict(bg='#231F2B', bg_deep='#1D1924', surface='#2B2634', pressed='#35303F',
         border='#403A4B', text='#ECE6F3', subtext='#A39AAF', accent='#B39BDD',
         accent_dim='#977FC2', on_accent='#1E1828', recv='#2F2A38', recv_alt='#3A3444',
         send='#4B3F66', send_alt='#5A3F52', recv_text='#ECE6F3', send_text='#F4EFFA',
         char_outline='#6F6580'),
    _scenes('checker', '#F3EEF8', '#E3DAF0', dict(dim_to='#F3EEF8'), (0.0, 0.25, 0.0)),
    _scenes('checker', '#231F2B', '#2F2939', dict(dim_to='#231F2B'), (0.0, 0.25, 0.0)),
    ['첫 말에 체크 깃발 꽂은 말풍선',
     '라벤더 체커보드 타일',
     '어두운 보라 바탕에 깃발 말풍선',
     '짙은 보라 체커보드'])


# --- 유리: 씨글래스 · 글래스 블록 · 얼음 · 골판 유리 · 아크릴 · 레진 -------------------------
# 색만 다른 유리는 더 만들지 않는다. 여섯 모두 말풍선 표면(charbubble 의 같은 이름)과 뒤 그림(scenes)이
# 재질을 따로 드러낸다. bubble_style='glass' 라서 프로필은 뒤 그림을 비추는 유리구슬이다.
# 축은 밝음/어두움 × 배경이고, 목록은 흐리지 않되 큰 조각을 뺀 질감만 깐다 — 흐렸더니 일곱 시안이 전부 단색이었다.

def _glass_scenes(kind, top, bottom, opts):
    sc = _scenes(kind, top, bottom, opts, (0.0, 0.0, 0.0))
    sc['main_bg'] = _bare(sc['main_bg'], 0.12)
    return sc


_GLASS_LOOK = dict(bubble_style='glass', cell_alpha=0.55, flat_list=False)

THEMES += character(
    'seaglass', 201, '씨글래스', dict(_GLASS_LOOK, char_style='seaglass'),
    dict(bg='#EDE6DA', bg_deep='#E6DDCE', surface='#F7F3EC', pressed='#E0D6C6',
         border='#D6CBB8', text='#2F3A38', subtext='#6F7A76', accent='#5E9E94',
         accent_dim='#4A8278', on_accent='#FFFFFF', recv='#F4F8F6', recv_alt='#E3EEEA',
         send='#A9D6CC', send_alt='#C6E3F0', recv_text='#2F3A38', send_text='#1F3531',
         char_outline='#8FB3AC'),
    dict(bg='#1F2322', bg_deep='#191C1B', surface='#272C2A', pressed='#303634',
         border='#39403D', text='#E4ECE9', subtext='#94A19C', accent='#7CC2B6',
         accent_dim='#5EA095', on_accent='#0F2420', recv='#2B3230', recv_alt='#343C39',
         send='#3F6E66', send_alt='#40607A', recv_text='#E4ECE9', send_text='#EEF7F4',
         char_outline='#5E706A'),
    _glass_scenes('seaglass', '#E9E1D2', '#CDBFA6',
                  dict(glass=['#9ED3C6', '#BFE3EE', '#F2F4F0', '#B98A5E', '#6F9BD1', '#C9E6B3'], dim_to='#EDE6DA')),
    _glass_scenes('seaglass', '#2A2723', '#1A1815',
                  dict(glass=['#5FA597', '#7FB0C4', '#C8D0CC', '#8A6444', '#4F74A8', '#8DB07A'], dim_to='#1F2322')),
    ['파도에 닳은 유리 조각 같은 무광 말풍선',
     '모래 위에 흩어진 뿌연 유리 조각',
     '어두운 바탕에 닳은 유리 말풍선',
     '밤바다 젖은 모래 위 유리 조각'])

THEMES += character(
    'glassblock', 205, '글래스 블록', dict(_GLASS_LOOK, char_style='gblock'),
    dict(bg='#EEF1F3', bg_deep='#E6EAEE', surface='#FAFBFC', pressed='#DDE3E8',
         border='#D0D8DF', text='#253038', subtext='#6B7780', accent='#3E88A8',
         accent_dim='#2F6D88', on_accent='#FFFFFF', recv='#F7FAFC', recv_alt='#E6EEF3',
         send='#A9D2E4', send_alt='#CBE3D6', recv_text='#253038', send_text='#15303D',
         char_outline='#9FB4C2'),
    dict(bg='#1B1F24', bg_deep='#15181C', surface='#232830', pressed='#2C323B',
         border='#353C46', text='#E6EBF0', subtext='#8F99A4', accent='#6FB6D6',
         accent_dim='#4F94B4', on_accent='#0C1E28', recv='#2A3038', recv_alt='#333A43',
         send='#335A6E', send_alt='#3E5A4C', recv_text='#E6EBF0', send_text='#EEF5F9',
         char_outline='#56626E'),
    _glass_scenes('glassblock', '#E8EDF1', '#C3CDD5',
                  dict(lights=['#FFD9A0', '#A8D8F0', '#C8E8C0', '#F5C6D6', '#FFFFFF'], dim_to='#EEF1F3')),
    _glass_scenes('glassblock', '#1E232A', '#0E1114',
                  dict(lights=['#E0A050', '#4F8FB8', '#6FA070', '#C06E8C', '#F0D8A0'], dim_to='#1B1F24')),
    ['두께 띠가 도는 볼록 유리 말풍선',
     '유리 벽돌 너머로 번진 불빛',
     '어두운 바탕에 볼록 유리 말풍선',
     '밤, 유리 벽돌 너머 켜진 불빛'])

THEMES += character(
    'ice', 209, '얼음', dict(_GLASS_LOOK, char_style='ice'),
    dict(bg='#EAF2F6', bg_deep='#DFEAF0', surface='#F6FAFC', pressed='#D5E3EB',
         border='#C8D9E3', text='#1F2F3A', subtext='#667A87', accent='#3A8FC4',
         accent_dim='#2A71A0', on_accent='#FFFFFF', recv='#F4FAFD', recv_alt='#E2EEF5',
         send='#9FCDEB', send_alt='#BFE0F0', recv_text='#1F2F3A', send_text='#12324A',
         char_outline='#9CB9CA'),
    dict(bg='#141D26', bg_deep='#10171F', surface='#1B2631', pressed='#23303C',
         border='#2C3A47', text='#E2EEF5', subtext='#8BA2B2', accent='#7CC4EE',
         accent_dim='#58A2CE', on_accent='#0A1C28', recv='#223040', recv_alt='#2A394A',
         send='#2E5B7C', send_alt='#35647F', recv_text='#E2EEF5', send_text='#EEF7FC',
         char_outline='#4E6678'),
    _glass_scenes('ice', '#DCEBF3', '#AFCBDC', dict(dim_to='#EAF2F6')),
    _glass_scenes('ice', '#1C3346', '#0B141D', dict(dim_to='#141D26')),
    ['서리 낀 얼음 말풍선. 첫 말엔 기포와 금',
     '금 간 얼음판에 갇힌 기포',
     '짙은 얼음빛 바탕에 서리 낀 말풍선',
     '깊고 푸른 얼음 속 금과 기포'])

THEMES += character(
    'reeded', 213, '골판 유리', dict(_GLASS_LOOK, char_style='reed'),
    dict(bg='#EFEBE4', bg_deep='#E7E2D9', surface='#F9F7F3', pressed='#E0D9CD',
         border='#D5CDBF', text='#2E2A25', subtext='#756E64', accent='#A0784A',
         accent_dim='#84613A', on_accent='#FFFFFF', recv='#FBF9F5', recv_alt='#EDE7DD',
         send='#E4CFAE', send_alt='#CFDDC4', recv_text='#2E2A25', send_text='#2E2418',
         char_outline='#B7AA96'),
    dict(bg='#211E1A', bg_deep='#1A1814', surface='#2A2621', pressed='#332E28',
         border='#3D3730', text='#EFE9E0', subtext='#A39A8E', accent='#E0AE6E',
         accent_dim='#BC8C50', on_accent='#261A0A', recv='#2F2A24', recv_alt='#38322B',
         send='#6A5234', send_alt='#445238', recv_text='#EFE9E0', send_text='#FBF4EA',
         char_outline='#6A6052'),
    _glass_scenes('reeded', '#E9E3D8', '#D8CFBF',
                  dict(blobs=['#F2C277', '#8DB27A', '#F5E3C0', '#6E9A66', '#E7A96A'], dim_to='#EFEBE4')),
    _glass_scenes('reeded', '#231F1A', '#171410',
                  dict(blobs=['#C8862E', '#4E6E3E', '#E8B060', '#3A5A34', '#A85E2E'], dim_to='#211E1A')),
    ['세로 골이 도는 유리 말풍선',
     '세로 골 너머로 쪼개져 비치는 초록과 햇빛',
     '어두운 바탕에 골판 유리 말풍선',
     '밤, 골판 유리 너머 등불'])

THEMES += character(
    'acrylic', 217, '아크릴', dict(_GLASS_LOOK, char_style='acrylic'),
    dict(bg='#F3F2F7', bg_deep='#ECEAF3', surface='#FCFBFE', pressed='#E3E0EC',
         border='#D8D4E4', text='#2A2838', subtext='#727088', accent='#FF5FA2',
         accent_dim='#D94483', on_accent='#FFFFFF', recv='#FAFAFD', recv_alt='#EFEDF6',
         send='#FFD0E4', send_alt='#CDEBFF', recv_text='#2A2838', send_text='#3A1428',
         char_outline='#B7B3C8', edge='#FF5FA2'),
    dict(bg='#17161E', bg_deep='#111018', surface='#1F1E28', pressed='#282632',
         border='#32303E', text='#EEEDF5', subtext='#9A98AE', accent='#FF6FAE',
         accent_dim='#D9508D', on_accent='#2A0A1A', recv='#26243A', recv_alt='#2E2C44',
         send='#5A2E4C', send_alt='#2A4A62', recv_text='#EEEDF5', send_text='#FFF0F7',
         char_outline='#5A5870', edge='#FF6FAE'),
    _glass_scenes('acrylic', '#F1F0F6', '#E4E1EE',
                  dict(sheets=['#FF8FC0', '#7FD3FF', '#FFE07A', '#A8F0C8'], dim_to='#F3F2F7')),
    _glass_scenes('acrylic', '#16151D', '#1E1C28',
                  dict(sheets=['#FF5FA2', '#4FC3FF', '#FFD24A', '#6FE8A8'], shadow='#000000', dim_to='#17161E')),
    ['형광 모서리 아크릴 말풍선. 첫 말엔 나사',
     '겹쳐 놓은 파스텔 아크릴판',
     '어두운 바탕에 형광 모서리가 빛남',
     '어둠 속에 겹친 형광 아크릴판'])

THEMES += character(
    'resin', 221, '레진', dict(_GLASS_LOOK, char_style='resin'),
    dict(bg='#F4E9D4', bg_deep='#EEE0C6', surface='#FBF5EA', pressed='#E8D6B6',
         border='#DECAA6', text='#3A2A14', subtext='#7E6A4C', accent='#C0801E',
         accent_dim='#9C6614', on_accent='#FFFFFF', recv='#FFF8EA', recv_alt='#F3E4C6',
         send='#F2C77E', send_alt='#E0CFA0', recv_text='#3A2A14', send_text='#3A2408',
         char_outline='#B89C70', leaf='#6B8A3A'),
    dict(bg='#221A10', bg_deep='#1A130B', surface='#2C2216', pressed='#372A1B',
         border='#433422', text='#F5EAD8', subtext='#B39E80', accent='#F0B04A',
         accent_dim='#C88C30', on_accent='#2A1A04', recv='#3E3020', recv_alt='#4C3B27',
         send='#B87A2A', send_alt='#8A6A30', recv_text='#F5EAD8', send_text='#FFF4E2',
         char_outline='#7A6448', leaf='#6B8A3A'),
    _glass_scenes('resin', '#F6E2B4', '#E2B96A', dict(flake='#C8901E', leaf='#8A5A1A', dim_to='#F4E9D4')),
    _glass_scenes('resin', '#7A4E14', '#2A1A08', dict(flake='#FFD66B', leaf='#3A2408', dim_to='#221A10')),
    ['꿀빛 레진 말풍선. 첫 말엔 갇힌 잎',
     '밝은 호박색 레진 속 금박과 기포',
     '짙은 호박색 바탕에 레진 말풍선',
     '호박색 레진 속 금박과 마른 잎'])


# --- 카테고리 규칙 ------------------------------------------------------------
# 카테고리의 모든 계열에 같이 붙는 값. 계열 정의에 따로 적은 값이 이긴다(setdefault).
# 도트는 8비트로 읽혀야 한다 — 한 칸 2pt 말풍선은 폰 크기에서 매끈한 네모로 보였다.
# 규칙과 까닭은 CLAUDE.md 의 "도트 카테고리" 에 있다.
DOT_STYLES = {'rpg', 'lcd', 'window', 'board'}      # 칸 크기(pixel_unit)를 따라 그리는 말풍선
CATEGORY_RULES = {
    '도트': dict(pixel_unit=4, pixel_shadow=True, tab_style='pixel', flat_list=False,
                 pixel_block=0.03),
    '편안함': dict(comfort_check=True),
}
# 규칙보다 먼저 나간 계열. 규칙을 붙이면 이미 깐 사람의 화면이 바뀐다.
# 차분·고요는 편안함 검사를 만들기 전에 나갔고, 재 보니 차분 샌드의 눌림 포인트색 채도가 0.47,
# 보낸 말풍선 대비가 1.18 이라 걸린다. 색을 바꾸면 깐 사람의 화면이 바뀌어서 뺀다
CATEGORY_RULE_EXEMPT = {'오락실', '차분', '고요'}

COMFORT_MAX_SAT = 0.25          # 바탕·말풍선·포인트색
COMFORT_BUBBLE = (1.2, 2.0)     # 보낸·받은 말풍선 ↔ 채팅방 바닥 대비
COMFORT_TEXT = 4.5              # 글자 대비


def _hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _sat(h):
    r, g, b = _hex_rgb(h)
    hi = max(r, g, b)
    return 0.0 if hi == 0 else (hi - min(r, g, b)) / hi


def _contrast(a, b):
    def lum(h):
        def ch(v):
            v /= 255.0
            return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
        r, g, bb = _hex_rgb(h)
        return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(bb)
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _check_comfort(t):
    """편안함 기준을 잰다. 눈으로 고르면 "예쁘다" 에 끌려 채도가 올라가서 숫자로 막는다."""
    one = lambda v: v[0] if isinstance(v, (tuple, list)) else v
    bad = []
    for k in ('bg', 'bg_deep', 'surface', 'pressed', 'send', 'send_alt', 'recv', 'recv_alt',
              'accent', 'text', 'subtext'):
        if _sat(one(t[k])) > COMFORT_MAX_SAT:
            bad.append('%s 채도 %.2f' % (k, _sat(one(t[k]))))
    for k, v in t.items():
        if isinstance(v, str) and v.upper() in ('#FFFFFF', '#000000'):
            bad.append('%s 가 순백·순흑' % k)
    lo, hi = COMFORT_BUBBLE
    for k in ('send', 'recv'):
        r = _contrast(one(t[k]), t['bg_deep'])
        if not lo <= r <= hi:
            bad.append('%s↔바닥 대비 %.2f' % (k, r))
    for tk, bk in (('send_text', 'send'), ('recv_text', 'recv'), ('text', 'bg')):
        r = _contrast(t[tk], one(t[bk]))
        if r < COMFORT_TEXT:
            bad.append('%s 대비 %.1f' % (tk, r))
    if bad:
        raise ValueError('%s: 편안함 기준을 어겼다 — %s' % (t['key'], ', '.join(bad)))


def apply_category_rules():
    for t in THEMES:
        fam = _fam_of(t)[0]
        cat = CATEGORY.get(fam)
        rule = CATEGORY_RULES.get(cat)
        if not rule or fam in CATEGORY_RULE_EXEMPT:
            continue
        if cat == '도트' and t.get('char_style') not in DOT_STYLES:
            raise ValueError('%s: 도트 카테고리 말풍선은 칸 크기를 따르는 스타일(%s)이어야 한다'
                             % (t['key'], ', '.join(sorted(DOT_STYLES))))
        for k, v in rule.items():
            if k == 'comfort_check':
                _check_comfort(t)
                continue
            if k != 'pixel_block':
                t.setdefault(k, v)
                continue
            # 배경 한 칸이 화면 폭의 3% 아래면 칸이 작고 그림이 촘촘해 고해상도 그림으로 보인다
            for bg in ('chat_bg', 'main_bg', 'passcode_bg'):
                s = t.get(bg)
                if not s or len(s) < 4:
                    continue
                if s[3].get('block', v) < v:
                    raise ValueError('%s: 도트 배경 한 칸이 폭의 %.3f 다. %.2f 이상이어야 한다'
                                     % (t['key'], s[3]['block'], v))
                t[bg] = (s[0], s[1], s[2], dict(s[3], block=s[3].get('block', v)))


apply_category_rules()

# 목록 배경 그림이 있으면 셀을 반투명하게 둔다. 불투명한 셀이 화면을 덮으면 배경을 넣은 뜻이 없고
# 목록이 배경 없는 형제와 같아 보인다. 0.72 는 글자가 흔들리지 않고 배경이 은은하게 비치는 정도다.
# 유리(0.55)와 네온사인(0.5)처럼 따로 정한 테마는 그 값을 쓴다.
for _t in THEMES:
    if _t.get('main_bg'):
        _t.setdefault('cell_alpha', 0.72)

check_variants()
