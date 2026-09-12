# 카카오톡 테마로 할 수 있는 것 전부

공식 가이드에서 뽑은 목록임. iOS 속성 57개, 안드로이드 리소스 68개.
**여기 없는 건 안 되는 것임** — 없는 이름을 써도 오류가 아니라 그냥 무시됨.

지금 쓰는 것과 안 쓰는 것을 나눠서 적음. 안 쓰는 쪽이 곧 남은 재료임.

---

## 한눈에

| | iOS | Android | 지금 |
|---|---|---|---|
| 색 | 32곳 | 42곳 | **거의 다 씀** |
| 투명도 | 셀·글자·테두리 | `#AARRGGBB` | 유리 테마에서 씀 |
| 말풍선 | PNG만 | PNG 우선, 색도 됨 | 씀 |
| 목록/채팅방 배경 이미지 | 됨 | 됨 | 씀 |
| 실행화면 | **없음** | 됨 | 안드로이드만 |
| 잠금화면 배경 이미지 | 됨 | 됨 | 심야에서 씀 |
| 탭 아이콘 8종 | 됨 | 됨 | **안 씀** |
| 기본 프로필 | 됨 | 됨 | **안 씀** |
| 친구추가 버튼 | 됨 | 됨 | **안 씀** |
| 잠금화면 동그라미 | 됨 | 됨 | **안 씀** |
| 애니메이션 | 없음 | 사실상 없음 | — |

---

## 색으로 되는 것 (이미 다 쓰고 있음)

화면별로 바꿀 수 있는 색임. 괄호 안은 팔레트 표의 토큰.

**목록 화면**
- 배경 (`bg`), 눌린 줄 (`pressed`), 구분선 (`border`)
- 이름 (`text`), 상태메시지·마지막 메시지 (`subtext`)
- "친구 24" 머리줄 (`subtext`), 강조 글자 (`accent`)
- 2차 화면 배경 (`surface`)

**채팅방**
- 바닥 (`bg_deep`), 안 읽은 수 (`accent`)
- 입력바 배경 (`surface`), 입력 글자 (`text`), 메뉴 아이콘 (`subtext`)
- 전송 버튼 배경 (`accent`) / 눌림 (`accent_dim`) / 아이콘 (`on_accent`)
- 말풍선 글자 (`send_text` / `recv_text`)

**그 밖**
- 상단 제목줄, 알림 배너, 공유 시트, 하단 배너, 잠금화면 키패드

**투명도** — iOS 는 `-ios-normal-background-alpha` / `-ios-selected-background-alpha` /
`-ios-text-alpha` / `border-alpha`, 안드로이드는 색 자체에 알파를 넣음(`#AARRGGBB`).
1 미만이면 뒤에 깐 배경 이미지가 비침. 유리 테마가 이걸로 만들어짐.

---

## 이미지로만 되는 것

색으로는 못 바꾸고 PNG 를 그려 넣어야 하는 자리임.

### 지금 쓰는 것

| 자리 | iOS | Android |
|---|---|---|
| 말풍선 (보낸/받은 × 보통/눌림) | `chatroomBubbleSend01` 등 4장 | `theme_chatroom_bubble_me_01_image` 등 4장 |
| 채팅방 배경 | `chatroomBgImage` | `theme_chatroom_background_image` |
| 목록 배경 | `mainBgImage` | `theme_background_image` |
| 실행화면 | **없음** | `theme_splash_image` |
| 잠금화면 배경 | `passcodeBgImage` | `theme_passcode_background_image` |

### 아직 안 쓰는 것 — 남은 재료

| 자리 | iOS | Android | 메모 |
|---|---|---|---|
| **탭 아이콘 8종** | `-ios-{friends,chats,find,browse,view,piccoma,shopping,more}-{normal,selected}-icon-image` | `theme_maintab_ico_*_image` / `*_focused_image` | 보통/선택 두 장씩. 남은 것 중 제일 티가 남 |
| **탭바 배경** | `TabBarStyle-Main` 의 `-ios-background-image` | `theme_maintab_cell_image` | 지금은 색만 씀 |
| **기본 프로필** | `-ios-profile-images` | `theme_profile_01_image` 등 | 사진 없는 친구에게 뜨는 그림 |
| **친구추가 버튼** | `ButtonStyle-AddFriend` 의 `-ios-image` | `theme_find_add_friend_button_image` (+`_pressed`) | |
| **잠금화면 동그라미 4개** | `-ios-bullet-{first..fourth}-image` (+`selected`) | `theme_passcode_0X_image` (+`_checked`) | 비밀번호 입력 점 |
| **키패드 눌림** | `-ios-keypad-number-highlighted-image` | — | |

---

## 지금까지 쓴 기법

이미지로 만들어낸 효과들임. 전부 `tools/gen.py` 에 있음.

| 기법 | 어떻게 | 쓰는 곳 |
|---|---|---|
| **세로 그라데이션** | 위아래 두 색을 섞어 채움 | 먹빛 민트, 오로라, 유리 |
| **단색** | 두 색의 중간값 하나로 채움 (`flat`) | 믹스드, 캔디 팝 |
| **반투명** | 알파를 낮춰 배경이 비치게 (`bubble_alpha`) | 유리 둘 |
| **유리 테두리** | 위쪽 테두리에 흰 선, 아래로 갈수록 흐리게 (`bubble_style='glass'`) | 유리 둘 |
| **바깥 글로우** | 반경 다른 흐림 셋을 겹치고 가장자리는 0 으로 (`glow`) | v2 둘, 유리 둘 |
| **안쪽 발광** | `mask - blur(mask)` 로 모서리를 따라가는 얇은 띠 | 위와 같음 |
| **색 덩어리 배경** | 큰 원을 뿌리고 크게 흐림 (`blobs`) | 유리 둘 |
| **선형 배경** | 위아래 두 색 (`linear`) | 벚꽃, 캔디 팝 |
| **오로라 배경** | 색 띠를 겹치고 크게 흐림 (`aurora`) | 오로라 |
| **밤하늘 그림** | 별·십자 광채·초승달·능선을 직접 그림 (`night`) | 심야 |
| **가장자리 빛** | 화면 테두리에서 안쪽으로 번지는 빛 | 글로우 있는 테마 |
| **네 칸 다른 색** | 보통/눌림/그룹 칸에 서로 다른 색 | 믹스드, 캔디 팝 |

배경은 두 갈래임 — **색면**(`linear` / `blobs` / `aurora`)과 **그림**(`night`).
사진은 저작권 때문에 못 씀. 필요한 그림은 코드로 그림. 시드를 고정해서 빌드할 때마다 바뀌지 않게 함.

아직 안 해본 것: **패턴·질감**(격자·노이즈·도트), **테두리만 있는 말풍선**(속 비우기),
**꼬리 달린 말풍선**, **그림자**, 밤하늘 말고 다른 **그림**(바다·숲·도시 실루엣 등).

---

## 안 되는 것

- **애니메이션.** 양쪽 가이드에 시간 개념이 있는 속성이 하나도 없음. iOS 는 PNG 만 받고
  APNG 를 넣어도 첫 프레임만 나옴. 안드로이드는 `animation-list` 를 넣어볼 수는 있지만
  누군가 `start()` 를 불러줘야 도는데 카톡이 그럴 이유가 없음
- **폰트.** 글꼴을 바꾸는 속성이 없음
- **모서리 둥글기·크기 같은 수치.** 말풍선 모양은 PNG 로만 정함
- **레이아웃.** 요소 위치를 옮길 수 없음. 색과 그림을 정해진 자리에 끼워 넣는 구조임
- **iOS 실행화면.** 블록 자체가 없음

---

## 만들 때 걸리는 것

- **cap inset** — 이미지에서 늘어나지 않는 가장자리. `'파일.png' 18px 18px` 의 숫자 두 개.
  모서리 둥글기보다 커야 하고, 글로우를 넣으면 그 여백만큼 더 키워야 함
- **edgeinsets** — 글자와 프레임 사이 여백. 글로우 여백이 프레임 안에 들어가므로
  같이 키우지 않으면 글자가 말풍선 가장자리에 붙음
- **세로 여백 = 말풍선 사이 간격.** 프레임 높이가 곧 간격이라 세로로 키우면 대화가 성겨 보임
- **말풍선은 가로로 늘어남.** 그래서 세로 그라데이션은 살고 가로 그라데이션은 뭉개짐
- **안드로이드는 9-patch.** 늘어나는 범위를 1픽셀 테두리에 그려 넣는 형식

---

## 출처

- [iOS 사용자 테마 가이드 (9.2.5)](https://t1.kakaocdn.net/kakaocorp/Service/Theme/KakaoTalk/9.2.5_UserThemeGuide_iOS.pdf)
- [Android 사용자 테마 가이드 (9.2.5)](https://t1.kakaocdn.net/kakaocorp/Service/Theme/KakaoTalk/9.2.5_UserThemeGuide_Android.pdf)

PDF 는 폰트 인코딩이 밀려 있어서 그냥 열면 안 읽힘. 글자 코드에 +31 하면 영문이 나옴
(`0x42`~`0x5B` → `a`~`z`, `0x40` → `_`, `0x0E` → `-`, `0x0F` → `.`, `0x11`~`0x1A` → `0`~`9`).
