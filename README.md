# 먹빛 민트 — 카카오톡 테마

직접 만드는 카카오톡 테마. 남의 테마를 고친 게 아니라 빈 파일에서 시작한다.
iOS 와 안드로이드는 방식이 완전히 달라서 소스도 빌드도 따로 간다.

```
ios/                     ← iOS 소스
  KakaoTalkTheme.css
  Images/                ← v0 에서는 비어 있다
android/                 ← 안드로이드 소스
  AndroidManifest.xml
  res/values/colors.xml
  res/values/strings.xml
build-ios.ps1            → dist/iOS/inkmint01.ktheme
build-android.ps1        → dist/android/inkmint01.apk
```

## 받기

[릴리스](https://github.com/Ruminem/kakaotalk-theme/releases)에서 받는다.
릴리스마다 iOS `.ktheme` 과 안드로이드 `.apk` 가 같이 올라간다.

## 빌드

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

두 플랫폼을 함께 만든다. **배포는 항상 이걸로 한다** — 한쪽만 갱신하면 두 버전이 어긋난다.
한쪽만 빠르게 확인할 때는 `build-ios.ps1` / `build-android.ps1` 을 따로 돌려도 된다.

`dist/` 와 `theme.keystore` 는 저장소에 넣지 않는다.

## 두 플랫폼의 차이

|  | iOS | Android |
|---|---|---|
| 파일 | `.ktheme` (확장자만 바꾼 zip) | `.apk` (앱) |
| 내용 | 유사 CSS + PNG | `colors.xml` + 9-patch PNG |
| 빌드 | 텍스트 편집 + 압축 | aapt2 → zipalign → apksigner |
| 적용 | 파일 앱에서 탭 → 공유 → 카카오톡 | 설치 후 카톡에서 선택 |
| 말풍선 색 | **PNG 로만 가능** | **색상값으로 가능** |

같은 디자인이라도 리소스 이름이 전혀 달라서 두 번 만드는 셈이다.
`.ktheme` 을 안드로이드에 넣을 수 없고 그 반대도 안 된다.

### iOS

`dist\iOS\inkmint01.ktheme` 을 아이폰으로 옮긴 뒤(카톡 나에게 보내기, 에어드롭, iCloud 아무거나)
파일 앱에서 탭 → 공유 → 카카오톡 → 설정 > 테마 에서 선택.

일반 CSS가 아니다. 셀렉터가 없고 **블록 이름이 카카오에 의해 고정**되어 있다.
없는 이름을 쓰면 오류가 아니라 그냥 무시된다. 속성은 대부분 `-ios-` 로 시작한다.

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

- 이미지는 `'파일명.png' 20px 20px` 형태. 뒤의 숫자 두 개가 **늘어나는 여백(cap inset)** 이고
  안드로이드 9-patch 에 해당한다. 모서리 둥글기를 바꾸면 같이 손봐야 한다.
- 파일명은 `@2x` / `@3x` 없이 쓰고, 실제 파일만 `Images/name@2x.png` 로 둔다.
- `-ios-*-alpha` 는 0.0~1.0. 1 미만이면 뒤 배경이 비친다.

### Android

`dist\android\inkmint01.apk` 를 폰으로 옮겨 설치한 뒤
카톡 **더보기 > 설정 > 테마 설정** 에서 선택. 출처를 알 수 없는 앱 설치 허용이 필요하다.

- 패키지 이름이 `com.kakao.talk.theme.` 로 시작해야 테마로 인식된다.
  뒷부분은 고유해야 한다 — 겹치면 서로 덮어쓴다.
- **권한을 하나도 요구하지 않는다.** 설치할 때 권한 안내가 뜨면 뭔가 잘못된 것이다.
- 리소스 이름은 가이드에 정의된 것만 먹는다. 색은 `colors.xml`, 이미지는 `res/drawable-xxhdpi/`.
- 서명은 아무 키나 상관없다. 다만 **같은 키로 계속 서명해야** 덮어 설치가 된다.
  키를 잃어버리면 폰에서 기존 테마를 지우고 새로 깔아야 한다.
- gradle 을 쓰지 않는다. 코드가 없는 리소스 전용 APK 라 aapt2 세 줄이면 끝난다.

## 현재 상태

v0 은 양쪽 다 이미지를 한 장도 쓰지 않는다. 색만 지정해서
"색으로 어디까지 바뀌는지"를 실물로 확인하는 게 목적이다.

- iOS: 말풍선은 `background-color` 속성이 아예 없어서 기본값(노랑/흰색)이 뜬다.
  그래서 글자색을 어두운 쪽으로 맞춰놨다. PNG 를 넣는 순간 밝은 쪽으로 뒤집어야 한다.
- Android: 말풍선 색이 먹으므로 v0 만으로도 꽤 바뀐다. 탭 아이콘만 기본값.

## 참고

- [iOS 사용자 테마 가이드 (9.2.5)](https://t1.kakaocdn.net/kakaocorp/Service/Theme/KakaoTalk/9.2.5_UserThemeGuide_iOS.pdf)
- [Android 사용자 테마 가이드 (9.2.5)](https://t1.kakaocdn.net/kakaocorp/Service/Theme/KakaoTalk/9.2.5_UserThemeGuide_Android.pdf)

리소스 이름은 전부 위 공식 가이드에서 가져왔다.
