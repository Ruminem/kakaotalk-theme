# 갤럭시 스토어 제출 준비 (2026-09-22)

한 벌만 올려 보는 **실험**이다. 파는 것이 목적이 아니라 재는 것이 목적이다.

> **재려는 것 하나** — 갤럭시 스토어가 코드 없고 런처 액티비티도 없는
> **리소스 전용 APK** 를 받아 주는가?

통과하면 자동 차단 문제가 통째로 사라진다. 스토어는 자동 차단이 믿는 두 출처 중 하나라,
거기서 받은 것은 보안을 끄지 않아도 깔린다. README 맨 위의 경고문을 지울 수 있게 된다.

막히면 거기서 방향이 갈린다 — 아래 `결과에 따라` 를 본다.

## 왜 갤럭시 스토어가 먼저인가

막는 것이 삼성 기능(`보안 위험 자동 차단`, One UI 6.1.1 부터 기본 켜짐)인데 그 삼성이
스토어를 갖고 있다. 그리고 거기에 **이미 카카오톡 테마가 유통되고 있다**. 계정 비용도 없다.

Play 는 네임스페이스가 뚫려 있는 것을 확인했지만(`com.kakao.talk.theme.Terminal` 등이
이미 등재돼 있다) `반복 콘텐츠` 정책 때문에 292벌은 못 올린다. 대표작 소수만 가능한 길이라
두 번째로 둔다.

## 올릴 테마

| | |
|---|---|
| 이름 | 설원 글로우+배경 |
| 파일 이름 | `snow-glow-image` |
| 패키지 | `com.kakao.talk.theme.snow_glow_image` |
| `versionCode` | 4703901 |
| `versionName` | 0.39.1 |
| `minSdkVersion` | 21 |
| `targetSdkVersion` | 34 |
| 권한 | 0개 |

이 계열을 고른 까닭은 **유일하게 진짜 폰에서 화면을 본 적이 있어서다**. 미리보기를 3배로
그리기로 한 결정이 이 테마의 폰 화면과 나란히 놓고 비교하면서 나왔다(CLAUDE.md 의 미리보기
규칙). 첫 제출은 변수를 줄이는 것이 맞고, 심사에서 뭔가 걸리면 「이 테마 탓」 이 아니라
「구조 탓」 이라고 바로 가를 수 있다.

## 준비된 자산

`build-tmp/galaxy/snow-glow-image/` 에 있다. 저장소 밖이라 커밋되지 않는다.

| 파일 | 크기 | 무엇 |
|---|---|---|
| `icon-512.png` | 512×512 | 스토어 아이콘 |
| `list.png` | 1206×2622 | 채팅 목록 |
| `chat.png` | 1206×2622 | 채팅방 |
| `passcode.png` | 1206×2622 | 잠금화면 |
| `splash.png` | 1206×2622 | 실행화면 |

`assets/` 의 미리보기는 1.5배로 줄인 603×1311 이라 스토어에 올리기엔 작다. 그래서
`.claude/galaxy/make-assets.py` 가 `preview.py` 의 화면 함수를 직접 불러 **줄이기 전
3배 원본**을 받는다. 아이콘도 128 을 늘리지 않고 `gen.icon(t, 512)` 로 그 크기에 새로 그린다.

```
python3 .claude/galaxy/make-assets.py snow-glow-image
```

`assets/` 와 `docs/` 는 건드리지 않는다 — 워킹 트리가 더러워지면 `release.ps1` 이 멈춘다.

### 제출용 그림에서만 이름을 바꾼다

`preview.NAMES` 는 카카오프렌즈 열 마리다(라이언·어피치·무지·프로도·네오·튜브·제이지·
콘·춘식이·죠르디). README 안에서는 카톡이 캡처할 때 이름을 가리는 방식을 흉내 낸 것이라
문제가 없다. **스토어 등재 그림은 남에게 파는 물건의 사진이라 거기에 카카오 상표가 박히면
안 된다.** 프렌즈와 안 겹치는 동물로 바꾼다.

`preview.ROWS` 는 모듈을 불러올 때 `NAMES` 로 이미 엮여 있어서 `NAMES` 만 갈면 채팅방은
바뀌고 **목록은 옛 이름이 남는다**. 한 번 그렇게 뽑아 놓고 그림을 보고 알았다.
`swap_names()` 가 둘을 같이 옮긴다.

```
python3 .claude/galaxy/check-names.py
```

그려지는 글자를 전부 모아 프렌즈 이름이 있는지 본다. 바꾸기 **전에** 안 걸리면 검사가
헛도는 것이므로 그때도 멈춘다 — 통과만 보면 아무것도 안 잡는 검사인지 알 수 없다.

### 그림은 PC 에서 진짜 글꼴로 다시 뽑았다 (2026-09-23)

컨테이너에서는 `NotoSansKR-VF.ttf` 가 없어 Noto Sans CJK KR 로 대신 그렸었다. PC 에서 같은
명령으로 다시 뽑았고 글꼴 대체 경고가 안 떴다. 목록·채팅방을 눈으로 봐서 말풍선·글로우·
바뀐 이름이 다 들어간 것을 확인했다.

## PC 에서 할 일

**1–3 은 끝났다 (2026-09-23).** 빌드 대신 0.39.1 릴리스 자산을 받아
`build-tmp/galaxy/snow-glow-image/snow-glow-image.apk`(696KB)에 두었다. `aapt2 dump badging`
으로 패키지·`versionCode`·SDK 가 위 표와 같고, `apksigner verify` 가 v1·v2·v3 을 통과하며,
인증서 SHA-256 이 `theme.keystore` 와 같다(`1cb5e723…cfa834`). `check-names.py` 통과.
**남은 것은 4–6, 계정을 만들고 제출하는 일이라 사람이 한다.**

여기서는 APK 빌드도 업로드도 못 한다. Android SDK 와 `theme.keystore` 가 PC 에 있고
삼성 도메인은 이 컨테이너에서 막혀 있다.

1. `powershell -ExecutionPolicy Bypass -File build.ps1` 로 `dist/android/snow-glow-image.apk` 를 얻는다
   (또는 이미 나간 0.39.1 릴리스 자산의 같은 파일을 쓴다 — 바이트가 같다)
2. `python .claude\galaxy\make-assets.py snow-glow-image` 로 그림을 다시 뽑는다(진짜 글꼴로)
3. `python .claude\galaxy\check-names.py` 가 통과하는지 본다
4. [seller.samsungapps.com](https://seller.samsungapps.com) 에 가입하고 `Add New App`
5. 아래 등재 문구를 넣고 자산을 올린다
6. 심사에 넣고 **결과와 사유를 이 문서에 적는다**

**서명은 반드시 기존 `theme.keystore` 로 한다.** 다른 키로 올리면 GitHub 에서 깐 사람이
스토어 버전으로 업데이트가 안 되고 서명 충돌로 설치가 막힌다. 서명은 「누구인지」가 아니라
「같은 사람인지」를 증명하는 것이라, 키가 갈리는 순간 두 앱이 된다.

## 등재 문구

### 앱 이름

```
카카오톡 테마 - 설원 글로우+배경
```

### 짧은 소개

```
설원 배경에 빛나는 말풍선. 권한을 하나도 요구하지 않는 카카오톡 테마입니다.
```

### 긴 소개 (한국어)

```
눈 덮인 들판 위로 말풍선이 은은하게 빛나는 카카오톡 테마입니다.

· 채팅 목록, 채팅방, 잠금화면, 실행화면까지 전부 바뀝니다
· 말풍선 네 칸(보낸 첫 말 / 이어지는 말 / 받은 첫 말 / 이어지는 말)이 서로 다른 색입니다
· 기본 프로필과 탭 아이콘도 테마에 맞춰 그렸습니다

■ 권한을 하나도 요구하지 않습니다
그림과 색만 들어 있는 테마입니다. 설치할 때 권한 안내가 뜨지 않습니다.
연락처, 저장공간, 네트워크 — 아무것도 읽지 않습니다.

■ 사용 방법
설치한 뒤 카카오톡을 열고 [더보기] → [설정] → [테마] 에서 고르면 적용됩니다.
이 앱 자체는 실행할 화면이 없습니다. 카카오톡이 설치된 테마를 찾아 목록에 보여줍니다.

■ 만든 곳
직접 만들어 오픈소스로 공개하는 테마 모음의 하나입니다.
전체 목록: https://github.com/Ruminem/kakaotalk-theme

카카오 및 카카오톡은 주식회사 카카오의 상표입니다. 이 앱은 카카오와 제휴하거나
카카오가 보증하는 앱이 아닙니다.
```

### 긴 소개 (영어)

```
A KakaoTalk theme: message bubbles glowing softly over a snowfield.

· Changes the chat list, chat room, lock screen and splash screen
· Four distinct bubble colors (sent first / sent follow-up / received first / received follow-up)
· Default profile images and tab icons are drawn to match

■ Requests no permissions
This is a resource-only theme — images and colors. No permission prompt on install.
It reads nothing: no contacts, no storage, no network.

■ How to use
After installing, open KakaoTalk and choose it under [More] → [Settings] → [Theme].
This app has no screen of its own. KakaoTalk finds installed themes and lists them.

■ About
One of an open-source collection of hand-made themes.
Full list: https://github.com/Ruminem/kakaotalk-theme

Kakao and KakaoTalk are trademarks of Kakao Corp. This app is not affiliated with
or endorsed by Kakao.
```

**상표 고지 문단은 빼지 않는다.** 패키지 이름이 `com.kakao.talk.theme.*` 라 남의
네임스페이스를 쓰는 셈이고, 「제휴 아님」 을 우리가 먼저 적어 두는 것이 심사에서도
쓰는 사람에게도 낫다.

### 그 밖의 칸

| 칸 | 값 | 까닭 |
|---|---|---|
| 카테고리 | 테마 / 개인화 | One UI 테마가 아니라 일반 앱으로 올린다. `Themes Seller Pledge` 는 One UI 테마용이라 해당 없음 |
| 가격 | 무료 | |
| 연령 | 전체 이용가 | 그림과 색뿐이다 |
| 개인정보 처리방침 | 필요하면 Pages 에 한 장 만든다 | 수집하는 것이 없다는 한 줄이면 된다. 권한 0개라 적을 것도 없다 |
| 지원 이메일 | 계정 이메일 | |

## 위험 — 걸린다면 여기다

1. **런처 액티비티가 없다.** `hasCode="false"` 에 액티비티 0개라 앱 아이콘조차 안 생긴다.
   Play 의 카톡테마 앱들은 대개 「적용하기」 버튼이 달린 액티비티를 갖고 있다. 스토어가
   「실행되지 않는 앱」 으로 볼 수 있다. **이것이 이번 실험의 진짜 질문이다.**
2. **64비트 바이너리 · 16KB 페이지 요건.** 네이티브 코드가 0개라 해당 없음이 맞지만,
   포털이 기계적으로 검사하면 걸릴 수 있다.
3. **패키지 네임스페이스.** Play 에는 같은 접두사가 이미 여럿 올라가 있으나 갤럭시 스토어는
   확인 전이다.
4. **`targetSdkVersion` 34.** 갤럭시 스토어 요건이 33 이상이라 지금은 통과한다. 요건이
   올라가면 `gen.py` 의 `MANIFEST` 한 줄이다.

## 결과 — 심사 전에 막혔다 (2026-09-23)

판매자 가입(무료 판매자)은 끝났는데 `신규 앱 등록` → `Android` 에서 이 안내가 떴다.

> Android 콘텐츠를 판매하려는 경우 사업자 유료 셀러 전환이 필요합니다. 사업자 유료 셀러가 아닐
> 경우 기존 Android 콘텐츠는 판매 중지되며 Android 콘텐츠 등록이 불가능합니다.

**무료 앱이어도 Android 앱은 사업자(Commercial) 셀러만 올린다.** 전환은 프로필에서 신청하고
신분증이나 사업자 서류로 심사받는다(법인은 D-U-N-S 번호). 테마·워치페이스 같은 비(非)Android
콘텐츠만 개인 판매자로 남을 수 있다. 가입 첫 화면의 「무료 애플리케이션을 등록할 수 있다」 는
문구는 이 제한을 말하지 않는다 — 계획을 세울 때 이것을 몰랐다.

유료 셀러 전환을 누르자 한 번 더 떴다.

> 개인 유료 셀러로는 워치 앱만 판매 가능합니다. 안드로이드 앱은 사업자 유료 셀러 전환이 필요하며,
> 테마, 워치페이스, 스티커 앱 등은 사전 승인이 필요합니다.

**개인으로는 길이 없다.** 사업자등록을 해야 Android 앱을 올릴 수 있다. 실험 하나 때문에 사업자등록을 하지
않기로 하고 **여기서 접는다.** 실험의 질문(리소스 전용 APK 를 받아 주는가)은 답을 못 얻은 채로 남는다.
README 의 안드로이드 경고문과 `install.html` 안내는 그대로 간다. 다시 파려면 사업자등록부터다.

## 결과에 따라

### 통과하면

- 292벌을 같은 틀로 올릴 수 있는지 본다. **갤럭시 스토어에도 반복 콘텐츠 제한이 있는지가
  다음 질문이다** — 지금 모른다. 포털 FAQ 를 읽거나 문의를 넣는다
- 되면 `make-assets.py` 를 `tools/` 로 옮기고 292벌을 도는 모드를 붙인다.
  지금 `.claude/` 에 둔 것은 **통과할지 모르는 것을 빌드 도구로 올리지 않으려는 것**이다 —
  `build-tmp/` 는 커밋되지 않아 컨테이너가 회수되면 스크립트가 같이 사라진다
- README 맨 위의 안드로이드 경고문을 고친다

### 막히면

- **사유를 그대로 적는다.** 「실행 액티비티가 없다」 면 길이 하나 남는다 — 테마를 고르고
  적용을 안내하는 작은 액티비티를 붙이는 것. 대신 권한 0개는 지킬 수 있는지 같이 본다
  (액티비티를 붙이는 것만으로는 권한이 안 늘어난다)
- 네임스페이스나 상표가 사유면 Play 쪽도 같은 벽이므로 길 C(카카오 제휴제안)만 남는다
- 어느 쪽이든 지금 구조(GitHub + `install.html`)는 그대로 돈다. 잃는 것은 없다
