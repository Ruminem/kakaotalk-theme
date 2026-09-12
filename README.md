# 먹빛 민트 — iOS 카카오톡 테마

직접 만드는 iOS 카카오톡 테마. 남의 테마를 고친 게 아니라 빈 CSS에서 시작한다.

```
mytheme/
  KakaoTalkTheme.css     ← 소스. 여기만 고친다
  Images/                ← PNG. v0 에서는 비어 있다
build.ps1                ← mytheme/ 을 .ktheme 으로 포장
dist/mytheme.ktheme      ← 빌드 결과. 아이폰으로 보낼 파일 (git 제외)
```

## 빌드

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

`dist\mytheme.ktheme` 이 나온다. 아이폰으로 옮긴 뒤(카톡 나에게 보내기, 에어드롭, iCloud 아무거나)
파일 앱에서 탭 → 공유 → 카카오톡 → 설정 > 테마 에서 선택.

`.ktheme` 은 확장자만 바꾼 zip 이다. **iOS 전용이고 안드로이드와 호환되지 않는다** —
안드로이드는 `colors.xml` + 9-patch PNG 를 담은 apk 를 빌드해 서명하는 완전히 다른 방식이다.

## 규격

일반 CSS가 아니다. 셀렉터가 없고 **블록 이름이 카카오에 의해 고정**되어 있다.
없는 이름을 쓰면 오류가 아니라 그냥 무시된다. 그래서 오타가 제일 위험하다.
속성은 대부분 `-ios-` 로 시작한다.

아래가 쓸 수 있는 이름 전부다.

| 블록 | 무엇 |
|---|---|
| `ManifestStyle` | 테마 이름 / 버전 / 작성자 / ID |
| `TabBarStyle-Main` | 하단 탭바 배경과 아이콘 8종 |
| `HeaderStyle-Main` | 상단 제목줄 |
| `MainViewStyle-Primary` | 친구탭·채팅목록 본문 |
| `MainViewStyle-Secondary` | 설정 등 2차 화면 |
| `SectionTitleStyle-Main` | "친구 24" 같은 구분 머리줄 |
| `FeatureStyle-Primary` | 강조 텍스트 |
| `ButtonStyle-AddFriend` | 친구추가 버튼 이미지 |
| `DefaultProfileStyle` | 기본 프로필 이미지 |
| `BackgroundStyle-ChatRoom` | 채팅방 바닥 |
| `InputBarStyle-Chat` | 채팅 입력바와 전송 버튼 |
| `MessageCellStyle-Send` / `-Receive` | 말풍선 |
| `BackgroundStyle-Passcode`, `LabelStyle-PasscodeTitle`, `PasscodeStyle` | 잠금화면 |
| `BackgroundStyle-MessageNotificationBar`, `LabelStyle-MessageNotificationBar*` | 상단 알림 배너 |
| `BackgroundStyle-DirectShareBar`, `LabelStyle-DirectShareBar*` | 공유 시트 |
| `BottomBannerStyle` | 하단 배너 |

### 알아둘 것

- **지정하지 않은 항목은 카카오 기본 테마가 그대로 나온다.** 부분만 만들어도 앱이 깨지지 않는다.
- **말풍선은 색으로 지정할 수 없다.** `MessageCellStyle-*` 에는 `background-color` 가 없고
  `-ios-background-image` 뿐이다. 말풍선 색을 바꾸려면 PNG 를 그려야 한다.
- 이미지 지정은 `'파일명.png' 20px 20px` 형태이고, 뒤의 숫자 두 개가 **늘어나는 여백(cap inset)** 이다.
  안드로이드 9-patch 에 해당한다. 모서리 둥글기를 바꾸면 이 숫자도 같이 손봐야 한다.
- 파일명은 `@2x` / `@3x` 없이 쓴다. 실제 파일은 `Images/name@2x.png`, `Images/name@3x.png` 로 두면
  iOS 가 해상도에 맞춰 고른다.
- `-ios-*-alpha` 는 0.0~1.0. 1 미만이면 뒤의 배경 이미지가 비친다.
- **테마 ID 가 같으면 기존에 깔린 테마를 덮어쓴다.** 두 개를 나란히 두고 비교하려면 ID 를 다르게.

## 현재 상태

v0 은 이미지를 한 장도 쓰지 않는다. 색만 지정해서
"색으로 바꿀 수 있는 범위가 어디까지인지"를 실물로 확인하는 게 목적이다.
말풍선은 기본값(노랑/흰색)이 뜨므로 글자색을 어두운 쪽으로 맞춰놨다.
말풍선 PNG 를 넣는 순간 받은 말풍선 글자색을 밝은 쪽으로 뒤집어야 한다.
