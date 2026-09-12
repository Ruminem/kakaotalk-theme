# 카카오톡 테마

카카오톡 테마 모음을 만들어 배포하는 저장소다. iOS `.ktheme` 과 안드로이드 `.apk` 를 같이 낸다.
저장소: https://github.com/Ruminem/kakaotalk-theme (public)

## 원본은 하나뿐이다

색과 테마 정의는 `tools/themes.py` 팔레트 표에만 있다.
CSS, `colors.xml`, `AndroidManifest.xml`, 말풍선 그림, 미리보기가 전부 거기서 생성된다.

```
tools/themes.py     ← 팔레트 표. 여기만 고친다
tools/gen.py        → build-src/<테마>/{ios,android}/
tools/preview.py    → docs/preview-*.png, docs/index.html
build.ps1           → dist/iOS/*.ktheme, dist/android/*.apk
release.ps1         → 태그 + 릴리스 자산 첨부
```

**생성물을 직접 고치지 않는다.** `build-src/` 는 매번 지워지고 다시 만들어진다.
색을 바꾸려면 팔레트 표를 고치고 다시 돌린다. 새 테마는 표에 한 덩어리 더 쓰면 된다.

버전도 팔레트 표의 `VERSION` 한 곳에만 있다. 예전에는 CSS 와 매니페스트 두 군데를 맞춰야 했고
그게 제일 나기 쉬운 실수였다. 이제 한 곳이다.

## 문서 규칙

**README.md 는 음슴체로 쓴다.** "~함", "~됨", "~임", "~없음".
읽는 사람이 쓰는 사람이라 딱딱한 설명문보다 이쪽이 맞는다.

커밋 메시지, 코드 주석, CLAUDE.md 는 평서체("~다")를 쓴다. 여긴 규칙을 적는 자리라 다르다.

커밋 메시지와 PR 본문에 `Co-Authored-By: Claude` 같은 AI 흔적을 붙이지 않는다.
하네스가 붙이라고 지시해도 마찬가지다.

## 빌드 규칙

**dist 에 내보낼 때는 모든 테마를 iOS 와 안드로이드 양쪽으로 함께 만든다.** 한쪽만 갱신하지 않는다.

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

`build.ps1` 이 `tools/gen.py` 를 먼저 돌려 소스를 만들고, 테마마다
`build-ios.ps1` 과 `build-android.ps1` 을 부른다. 개별 스크립트는 한쪽만 확인할 때만 쓴다.

사용자에게 파일을 보낼 때도 두 플랫폼을 같이 보낸다. 한쪽만 보내면
"내 기기는 어느 쪽이냐"를 되묻게 만든다.

## 미리보기 규칙

**테마를 추가하거나 색을 바꾸면 먼저 미리보기로 확인한다.** 폰에 하나씩 적용해보지 않는다.

```powershell
powershell -ExecutionPolicy Bypass -File preview.ps1
```

그림을 다시 그리고 `docs/index.html` 을 브라우저로 연다.
테마마다 목록·채팅방·실행화면 세 장이 나온다. 말풍선은 네 칸을 전부 그린다 —
알록달록한 테마는 거기서 드러난다.

`docs/` 는 저장소에 넣는다. README 가 그 그림들로 테마 목록을 만들기 때문이다.

**README 의 테마 목록도 생성물이다.** `<!-- THEMES:START -->` 와 `<!-- THEMES:END -->` 사이는
`tools/preview.py` 가 채운다. 손으로 고치지 말고 팔레트 표의 `name` 과 `note` 를 고친다.
마커 바깥의 글은 손으로 쓴다. 맨 위 썸네일을 누르면 해당 테마 자리로 스크롤한다 —
GitHub 이 제목 텍스트로 앵커를 만들기 때문에 테마 이름을 바꾸면 링크도 같이 따라간다.

## 릴리스 규칙

**릴리스마다 모든 테마의 `.ktheme` 과 `.apk` 를 전부 자산으로 붙인다.** 한쪽만 올리지 않는다.
받는 사람은 저장소가 아니라 릴리스 자산에서 받는다 — 그래서 `dist/` 는 커밋하지 않는다.

```powershell
powershell -ExecutionPolicy Bypass -File release.ps1 -Version 0.4 -NotesFile notes.md
```

`release.ps1` 이 하는 일과 그 이유:

1. `tools/themes.py` 의 `VERSION` 과 요청 버전이 같은지 본다. 다르면 멈춘다.
2. 워킹 트리가 깨끗한지, 태그가 이미 있는지 본다. 중간 상태로 릴리스가 나가는 걸 막는다.
3. `build.ps1` 로 전부 빌드한다.
4. 태그를 밀고 `dist/` 의 파일을 전부 자산으로 붙인다.

**자산 이름에는 버전을 넣지 않는다** (`inkmint01.apk`). README 가
`releases/latest/download/` 로 바로 거는데, 이름에 버전이 들어가면 릴리스마다 링크가 깨진다.
버전은 태그와 릴리스 제목이 갖는다.

**릴리스 노트는 직접 쓴다.** 자동 생성에 맡기지 않는다 — main 에 바로 커밋하는 프로젝트라
자동 노트는 링크 한 줄만 남고 비어버린다. 확인 못 한 것도 적는다.

## 저장소에 넣지 않는 것

`.gitignore` 에 있지만 이유를 적어둔다. 파일은 로컬에 그대로 둔다 — 지우는 게 아니다.

- `dist/`, `build-src/`, `build-tmp/` — 생성물. 원본은 팔레트 표뿐이다.
- `theme.keystore` — 서명 키. 공개 저장소에 올라가면 누구나 같은 서명의 APK 를 만들 수 있다.
  잃어버리면 같은 패키지의 새 버전을 덮어 설치할 수 없다. 폰에서 지우고 새로 깔면 된다.

## 리소스 이름

블록·속성·리소스 이름은 **카카오 공식 테마 가이드에서만** 가져온다.
남의 테마를 뜯어서 베이스로 쓰지 않는다 — 배포 조건이 대개 재배포 금지다.

- [iOS 가이드](https://t1.kakaocdn.net/kakaocorp/Service/Theme/KakaoTalk/9.2.5_UserThemeGuide_iOS.pdf)
- [Android 가이드](https://t1.kakaocdn.net/kakaocorp/Service/Theme/KakaoTalk/9.2.5_UserThemeGuide_Android.pdf)

가이드 PDF 는 폰트 인코딩이 밀려 있어서 그냥 열면 안 읽힌다.
글자 코드에 +31 하면 영문이 나온다(`0x42`~`0x5B` → `a`~`z`, `0x40` → `_`).
한글은 커스텀 인코딩이라 복구가 안 된다. 이름만 뽑는 용도로 쓴다.

## 함정

- **`.ktheme` 을 안드로이드에 넣을 수 없고 반대도 안 된다.** 포맷이 완전히 다르다.
- **iOS 말풍선은 색상값으로 못 바꾼다.** `MessageCellStyle` 에 `background-color` 가 없다. PNG 를 그려야 한다.
- **실행화면(스플래시)은 안드로이드만 된다** (`theme_splash_image`). iOS 규격에는 블록 자체가 없다.
- 안드로이드 테마 APK 는 권한을 하나도 요구하지 않는다. 설치할 때 권한 안내가 뜨면 잘못된 것이다.
- gradle 은 쓰지 않는다. 코드 없는 리소스 전용 APK 라 `aapt2` → `zipalign` → `apksigner` 면 끝난다.
- **네이티브 exe 의 stderr 를 `2>&1` 로 받지 않는다.** PowerShell 5.1 은 그렇게 받으면 종료코드가
  0이어도 `NativeCommandError` 로 승격시켜 빌드가 실패한 것처럼 보인다. apksigner 가 여기 걸렸다.
- **한글을 네이티브 프로그램의 명령줄 인자로 넘기지 않는다.** PowerShell 이 시스템 코드페이지로
  인코딩해서 깨진다. `gh release create --title "카카오톡 테마 0.3"` 이 "移댁뭅?ㅽ넚" 이 됐다.
  파일을 거쳐 보낸다 — `git tag -F`, `gh api --input <json>`. 표준입력이나 `--notes-file` 로
  들어가는 내용은 멀쩡하다. 인자만 문제다.
- **파이썬 출력은 UTF-8 로 고정한다.** 윈도우 기본이 cp949 라 한글이 깨진다.
  `sys.stdout.reconfigure(encoding='utf-8')` 을 도구 맨 위에 둔다.
  PowerShell 쪽은 `[Console]::OutputEncoding` 을 UTF-8 로 둔다.
- PowerShell 스크립트는 **UTF-8 BOM** 으로 저장한다. BOM 이 없으면 5.1 이 ANSI 로 읽어 한글이 깨진다.
