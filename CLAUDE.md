# 카카오톡 테마

## 배포 규칙

**dist 에 내보낼 때는 iOS 와 안드로이드 두 버전을 항상 함께 만든다.** 한쪽만 갱신하지 않는다.

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

`build.ps1` 이 `build-ios.ps1` 과 `build-android.ps1` 을 둘 다 돌린다.
결과는 `dist/iOS/inkmint01.ktheme` 과 `dist/android/inkmint01.apk`.
개별 스크립트는 한쪽만 빠르게 확인할 때만 쓰고, 배포는 항상 `build.ps1` 로 한다.

한쪽 소스를 고쳤으면 반대쪽도 같은 값으로 고친 뒤에 빌드한다.
두 소스는 리소스 이름이 완전히 달라서 자동으로 맞춰지지 않는다:

| 고칠 것 | iOS | Android |
|---|---|---|
| 색 | `mytheme/KakaoTalkTheme.css` | `android/res/values/colors.xml` |
| 이름 | `-kakaotalk-theme-name` | `res/values/strings.xml` 의 `theme_title` |
| 버전 | `-kakaotalk-theme-version` | `AndroidManifest.xml` 의 `versionCode` / `versionName` |
| 이미지 | `mytheme/Images/name@3x.png` | `android/res/drawable-xxhdpi/name.png` |

사용자에게 파일을 보낼 때도 두 개를 같이 보낸다. 한쪽만 보내면
"내 기기는 어느 쪽이냐"를 되묻게 만든다.

## 리소스 이름

블록·속성·리소스 이름은 **카카오 공식 테마 가이드에서만** 가져온다.
남의 테마를 뜯어서 베이스로 쓰지 않는다 — 배포 조건이 대개 재배포 금지다.

- [iOS 가이드](https://t1.kakaocdn.net/kakaocorp/Service/Theme/KakaoTalk/9.2.5_UserThemeGuide_iOS.pdf)
- [Android 가이드](https://t1.kakaocdn.net/kakaocorp/Service/Theme/KakaoTalk/9.2.5_UserThemeGuide_Android.pdf)

가이드 PDF 는 폰트 인코딩이 한 칸 밀려 있다. 글자 코드에 +31 하면 읽힌다.

## 안 되는 것

- `.ktheme` 을 안드로이드에 넣을 수 없고 그 반대도 안 된다. 포맷이 완전히 다르다.
- iOS 말풍선은 색상값으로 못 바꾼다. `MessageCellStyle` 에 `background-color` 가 없다. PNG 를 그려야 한다.
- 안드로이드는 말풍선 색이 먹는다 (`theme_chatroom_bubble_me_color`).
