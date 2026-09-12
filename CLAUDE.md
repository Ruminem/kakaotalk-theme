# 카카오톡 테마

먹빛 민트. iOS `.ktheme` 과 안드로이드 `.apk` 를 한 소스 트리에서 만든다.
저장소: https://github.com/Ruminem/kakaotalk-theme (public)

## 폴더

```
ios/                     ← iOS 소스 (KakaoTalkTheme.css + Images/)
android/                 ← 안드로이드 소스 (AndroidManifest.xml + res/)
build.ps1                → 둘 다 빌드. 배포는 항상 이걸로
build-ios.ps1            → dist/iOS/inkmint01.ktheme
build-android.ps1        → dist/android/inkmint01.apk
release.ps1              → 빌드 + 태그 + 릴리스 자산 첨부
```

양쪽 폴더 이름을 `ios` / `android` 로 맞춰놨다. 한쪽만 이름이 다르면
저장소 목록에서 한 플랫폼이 빠진 것처럼 보인다.

## 빌드 규칙

**dist 에 내보낼 때는 iOS 와 안드로이드 두 버전을 항상 함께 만든다.** 한쪽만 갱신하지 않는다.

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

개별 스크립트는 한쪽만 빠르게 확인할 때만 쓴다. 배포는 항상 `build.ps1`.

한쪽 소스를 고쳤으면 반대쪽도 같은 값으로 고친 뒤에 빌드한다.
두 소스는 리소스 이름이 완전히 달라서 자동으로 맞춰지지 않는다:

| 고칠 것 | iOS | Android |
|---|---|---|
| 색 | `ios/KakaoTalkTheme.css` | `android/res/values/colors.xml` |
| 이름 | `-kakaotalk-theme-name` | `res/values/strings.xml` 의 `theme_title` |
| 버전 | `-kakaotalk-theme-version` | `AndroidManifest.xml` 의 `versionCode` / `versionName` |
| 이미지 | `ios/Images/name@3x.png` | `android/res/drawable-xxhdpi/name.png` |

사용자에게 파일을 보낼 때도 두 개를 같이 보낸다. 한쪽만 보내면
"내 기기는 어느 쪽이냐"를 되묻게 만든다.

## 릴리스 규칙

**릴리스마다 iOS `.ktheme` 과 안드로이드 `.apk` 를 둘 다 자산으로 붙인다.** 한쪽만 올리지 않는다.

```powershell
powershell -ExecutionPolicy Bypass -File release.ps1 -Version 0.2 -NotesFile notes.md
```

`release.ps1` 이 하는 일과, 그렇게 만든 이유:

1. **양쪽 버전이 같은지 확인한다.** 다르면 빌드 전에 멈춘다.
   한쪽만 올리고 빌드하는 게 이 프로젝트에서 제일 나기 쉬운 실수다.
2. **워킹 트리가 깨끗한지, 태그가 이미 있는지 본다.** 중간 상태로 릴리스가 나가는 걸 막는다.
3. `build.ps1` 로 양쪽을 빌드한다.
4. 태그를 밀고 두 파일을 자산으로 붙인다.

**자산 이름에는 버전을 넣지 않는다** (`inkmint01.apk`, `inkmint01.ktheme`).
README 가 `releases/latest/download/` 로 바로 거는데, 이름에 버전이 들어가면
릴리스마다 그 링크가 깨진다. 버전은 태그와 릴리스 제목이 갖는다.

**릴리스 노트는 직접 쓴다.** 자동 생성에 맡기지 않는다 — main 에 바로 커밋하는
프로젝트라 자동 노트는 링크 한 줄만 남고 비어버린다.
직전 태그부터의 커밋 제목을 뽑아 붙이면 된다. 확인 못 한 것도 적는다.

## 저장소에 넣지 않는 것

`.gitignore` 에 있지만 이유를 적어둔다. 파일은 로컬에 그대로 둔다 — 지우는 게 아니다.

- `dist/` — 빌드 결과. 받는 사람은 저장소가 아니라 릴리스 자산에서 받는다.
- `theme.keystore` — 서명 키. 공개 저장소에 올라가면 누구나 같은 서명의 APK 를 만들 수 있다.
  잃어버리면 같은 패키지의 새 버전을 덮어 설치할 수 없다(서명 불일치). 폰에서 지우고 새로 깔면 된다.
- `build-tmp/` — 빌드 중간물. 스크립트가 끝나면 지우지만, 실패로 남을 때를 대비해 넣어뒀다.

## 리소스 이름

블록·속성·리소스 이름은 **카카오 공식 테마 가이드에서만** 가져온다.
남의 테마를 뜯어서 베이스로 쓰지 않는다 — 배포 조건이 대개 재배포 금지다.

- [iOS 가이드](https://t1.kakaocdn.net/kakaocorp/Service/Theme/KakaoTalk/9.2.5_UserThemeGuide_iOS.pdf)
- [Android 가이드](https://t1.kakaocdn.net/kakaocorp/Service/Theme/KakaoTalk/9.2.5_UserThemeGuide_Android.pdf)

가이드 PDF 는 폰트 인코딩이 밀려 있어서 그냥 열면 안 읽힌다.
글자 코드에 +31 하면 영문이 나온다(`0x42`~`0x5B` → `a`~`z`, `0x40` → `_`).
한글은 커스텀 인코딩이라 복구가 안 된다. 이름만 뽑는 용도로 쓴다.

## 안 되는 것

- `.ktheme` 을 안드로이드에 넣을 수 없고 그 반대도 안 된다. 포맷이 완전히 다르다.
- iOS 말풍선은 색상값으로 못 바꾼다. `MessageCellStyle` 에 `background-color` 가 없다. PNG 를 그려야 한다.
- 안드로이드는 말풍선 색이 먹는다 (`theme_chatroom_bubble_me_color`).
- 안드로이드 테마 APK 는 권한을 하나도 요구하지 않는다. 설치할 때 권한 안내가 뜨면 뭔가 잘못된 것이다.
- gradle 은 쓰지 않는다. 코드 없는 리소스 전용 APK 라 `aapt2` → `zipalign` → `apksigner` 면 끝난다.
