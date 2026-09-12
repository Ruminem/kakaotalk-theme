# 카카오톡 테마

직접 만든 카카오톡 테마 모음임. iOS(`.ktheme`)와 안드로이드(`.apk`) 양쪽으로 냄.
남의 테마를 고친 게 아니라 빈 파일에서 시작했음.

색은 팔레트 표 한 곳에서만 관리하고, CSS·`colors.xml`·이미지·미리보기가 전부 거기서 생성됨.

---

## 테마

받는 링크는 항상 **최신 릴리스**를 가리킴. 지난 버전은 [릴리스 목록](https://github.com/Ruminem/kakaotalk-theme/releases)에 있음.
세 번째 그림인 실행화면은 **안드로이드에만 있음** — iOS 테마 규격에는 스플래시 블록이 아예 없음.

### 먹빛 민트

<img src="docs/preview-inkmint01-list.png" width="200"> <img src="docs/preview-inkmint01-chat.png" width="200"> <img src="docs/preview-inkmint01-splash.png" width="200">

먹색 바탕에 민트 포인트. 말풍선은 민트→하늘, 보라→자주 그라데이션임.

[iOS 받기](https://github.com/Ruminem/kakaotalk-theme/releases/latest/download/inkmint01.ktheme) · [Android 받기](https://github.com/Ruminem/kakaotalk-theme/releases/latest/download/inkmint01.apk)

### 크림 라떼

<img src="docs/preview-cream02-list.png" width="200"> <img src="docs/preview-cream02-chat.png" width="200"> <img src="docs/preview-cream02-splash.png" width="200">

밝은 쪽. 베이지 바탕에 브라운. 눈이 제일 안 피로한 조합임.

[iOS 받기](https://github.com/Ruminem/kakaotalk-theme/releases/latest/download/cream02.ktheme) · [Android 받기](https://github.com/Ruminem/kakaotalk-theme/releases/latest/download/cream02.apk)

### 벚꽃 그늘

<img src="docs/preview-sakura03-list.png" width="200"> <img src="docs/preview-sakura03-chat.png" width="200"> <img src="docs/preview-sakura03-splash.png" width="200">

밝은 분홍. **채팅방 배경 이미지**가 들어간 테마임.

[iOS 받기](https://github.com/Ruminem/kakaotalk-theme/releases/latest/download/sakura03.ktheme) · [Android 받기](https://github.com/Ruminem/kakaotalk-theme/releases/latest/download/sakura03.apk)

### 믹스드

<img src="docs/preview-mixed04-list.png" width="200"> <img src="docs/preview-mixed04-chat.png" width="200"> <img src="docs/preview-mixed04-splash.png" width="200">

어두운 보라 바탕. **말풍선 네 칸이 전부 다른 색**임 — 보낸 것은 주황→노랑, 눌리면 민트→하늘,
받은 것은 보라→자주, 눌리면 하늘→연두로 바뀜.

[iOS 받기](https://github.com/Ruminem/kakaotalk-theme/releases/latest/download/mixed04.ktheme) · [Android 받기](https://github.com/Ruminem/kakaotalk-theme/releases/latest/download/mixed04.apk)

### 오로라

<img src="docs/preview-aurora05-list.png" width="200"> <img src="docs/preview-aurora05-chat.png" width="200"> <img src="docs/preview-aurora05-splash.png" width="200">

가장 어두운 테마. 채팅방 배경에 오로라가 깔림.

[iOS 받기](https://github.com/Ruminem/kakaotalk-theme/releases/latest/download/aurora05.ktheme) · [Android 받기](https://github.com/Ruminem/kakaotalk-theme/releases/latest/download/aurora05.apk)

### 캔디 팝

<img src="docs/preview-candy06-list.png" width="200"> <img src="docs/preview-candy06-chat.png" width="200"> <img src="docs/preview-candy06-splash.png" width="200">

밝은 쪽 알록달록. 말풍선 네 칸이 전부 다르고 채팅방 배경도 있음.

[iOS 받기](https://github.com/Ruminem/kakaotalk-theme/releases/latest/download/candy06.ktheme) · [Android 받기](https://github.com/Ruminem/kakaotalk-theme/releases/latest/download/candy06.apk)

---

## 받는 법

### 폰에서 바로 받기

PC로 받아서 폰으로 옮길 필요 없음. 카메라로 찍으면 릴리스 목록으로 감.

| iOS | Android |
|---|---|
| <img src="docs/qr-ios.png" width="150"> | <img src="docs/qr-android.png" width="150"> |

**iOS** — 받은 뒤 파일 앱 > 다운로드에서 `.ktheme` 을 길게 눌러 **공유 → 카카오톡**.
카카오톡으로 파일을 건네는 이 단계는 없앨 수 없음. 테마를 받는 경로가 그것뿐임.

**Android** — 받은 뒤 알림을 눌러 설치. "출처를 알 수 없는 앱" 허용이 한 번 필요함.
설치 후 카톡 더보기 > 설정 > 테마 설정.

### 한 번에 하고 싶으면 (iOS 단축어)

단축어 앱에서 세 동작짜리를 만들면 홈 화면 아이콘 한 번으로 공유 시트까지 감.

1. **URL** — `https://github.com/Ruminem/kakaotalk-theme/releases/latest/download/inkmint01.ktheme`
2. **URL의 콘텐츠 가져오기**
3. **공유 시트 보기**

홈 화면에 추가하면 누를 때마다 최신 테마를 받아서 공유 시트를 띄움. 거기서 카카오톡만 고르면 됨.
링크가 `latest` 라 새 버전이 나와도 그대로 씀. 테마를 바꾸려면 URL의 파일 이름만 바꾸면 됨.

---

## 만들기

원본은 [tools/themes.py](tools/themes.py) 팔레트 표 **하나뿐**임.
CSS도 `colors.xml`도 말풍선 그림도 미리보기도 전부 거기서 나옴.
새 테마를 만들려면 그 표에 한 덩어리 더 쓰면 됨.

```powershell
powershell -ExecutionPolicy Bypass -File preview.ps1   # 그림 다시 그리고 브라우저로 열기
powershell -ExecutionPolicy Bypass -File build.ps1     # 전부 빌드 → dist/
```

미리보기는 테마마다 목록·채팅방·실행화면 세 장을 그림.
**폰에 하나씩 적용해보지 않고 색을 확인하려고** 만든 것임.

```
tools/themes.py     ← 팔레트 표. 여기만 고침
tools/gen.py        → build-src/<테마>/{ios,android}/
tools/preview.py    → docs/preview-*.png, docs/index.html
build.ps1           → dist/iOS/*.ktheme, dist/android/*.apk
release.ps1         → 태그 + 릴리스 자산 첨부
```

`dist/`, `build-src/`, `theme.keystore` 는 저장소에 안 들어감. 받는 사람은 릴리스 자산에서 받음.

### 필요한 것

- 파이썬 + Pillow (`pip install Pillow`) — 생성기
- 안드로이드 SDK (aapt2, zipalign, apksigner) + JDK — APK 빌드. gradle은 안 씀
- iOS 쪽은 따로 없음. zip으로 묶는 게 전부임

---

## 규격 메모

두 플랫폼은 방식이 완전히 다름. `.ktheme` 을 안드로이드에 넣을 수 없고 반대도 안 됨.

|  | iOS | Android |
|---|---|---|
| 파일 | `.ktheme` (확장자만 바꾼 zip) | `.apk` (앱) |
| 내용 | 유사 CSS + PNG | `colors.xml` + 9-patch PNG |
| 빌드 | 텍스트 편집 + 압축 | aapt2 → zipalign → apksigner |
| 말풍선 색 | **PNG로만 됨** | 색상값으로도 됨 |
| 실행화면 | **없음** | `theme_splash_image` |

### iOS

일반 CSS가 아님. 셀렉터가 없고 **블록 이름이 카카오에 의해 고정**돼 있음.
없는 이름을 쓰면 오류가 아니라 그냥 무시됨. 그래서 오타가 제일 위험함.

| 블록 | 무엇 |
|---|---|
| `ManifestStyle` | 테마 이름 / 버전 / 작성자 / ID |
| `TabBarStyle-Main` | 하단 탭바 배경과 아이콘 8종 |
| `HeaderStyle-Main` | 상단 제목줄 |
| `MainViewStyle-Primary` / `-Secondary` | 목록 본문 / 2차 화면 |
| `SectionTitleStyle-Main` | "친구 24" 같은 구분 머리줄 |
| `FeatureStyle-Primary` | 강조 텍스트 |
| `ButtonStyle-AddFriend`, `DefaultProfileStyle` | 친구추가 버튼, 기본 프로필 |
| `BackgroundStyle-ChatRoom` | 채팅방 바닥 |
| `InputBarStyle-Chat` | 채팅 입력바와 전송 버튼 |
| `MessageCellStyle-Send` / `-Receive` | 말풍선 |
| `BackgroundStyle-Passcode`, `LabelStyle-PasscodeTitle`, `PasscodeStyle` | 잠금화면 |
| `BackgroundStyle-MessageNotificationBar`, `LabelStyle-MessageNotificationBar*` | 알림 배너 |
| `BackgroundStyle-DirectShareBar`, `LabelStyle-DirectShareBar*` | 공유 시트 |
| `BottomBannerStyle` | 하단 배너 |

- 이미지는 `'파일명.png' 18px 18px` 형태. 뒤의 숫자 두 개가 **늘어나지 않는 가장자리**(cap inset)고
  안드로이드 9-patch에 해당함. 모서리 둥글기를 바꾸면 같이 손봐야 함.
- 파일명은 `@2x` / `@3x` 없이 쓰고, 실제 파일만 `Images/name@2x.png` 로 둠.
- `-ios-*-alpha` 는 0.0~1.0. 1 미만이면 뒤 배경이 비침.

### Android

- 패키지 이름이 `com.kakao.talk.theme.` 로 시작해야 테마로 인식됨. 뒷부분은 고유해야 함.
- **권한을 하나도 요구하지 않음.** 설치할 때 권한 안내가 뜨면 뭔가 잘못된 것임.
- 색은 `colors.xml`, 이미지는 `res/drawable-xxhdpi/`. 말풍선은 이미지가 색상값을 이김.
- 서명은 아무 키나 상관없지만 **같은 키로 계속 서명해야** 덮어 설치가 됨.

### 말풍선을 세로 그라데이션으로 그리는 이유

말풍선은 글자 길이에 따라 가로로 늘어남. 세로 그라데이션이면 각 줄의 색이 유지되지만,
가로 그라데이션이면 늘어나면서 뭉개짐.

---

## 참고

리소스 이름은 전부 카카오 공식 가이드에서 가져왔음.

- [iOS 사용자 테마 가이드 (9.2.5)](https://t1.kakaocdn.net/kakaocorp/Service/Theme/KakaoTalk/9.2.5_UserThemeGuide_iOS.pdf)
- [Android 사용자 테마 가이드 (9.2.5)](https://t1.kakaocdn.net/kakaocorp/Service/Theme/KakaoTalk/9.2.5_UserThemeGuide_Android.pdf)

가이드 PDF는 폰트 인코딩이 밀려 있어서 그냥 열면 안 읽힘. 글자 코드에 +31 하면 영문이 나옴.
