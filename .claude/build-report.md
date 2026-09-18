# 빌드 비용 측정 (2026-09-18)

`.claude/handoff.md` 2단계의 결과다. **핸드오프는 C++ 프로젝트를 전제로 쓰였는데 이 저장소는
C/C++ 파일이 0개다.** include 사슬·무거운 헤더·템플릿 인스턴스화·`compile_commands.json`·
ClangBuildAnalyzer·IWYU·ccache 는 전부 해당 사항이 없다. 그래서 clang 도구 대신 실제 빌드를
단계별로 계측했고, 핸드오프가 요구한 세 순위표는 이 프로젝트의 대응물로 바꿔 냈다.

측정 기계: 12코어, Windows 11. 빌드는 8워커.

## 기준 시간

| | |
|---|---|
| 클린 빌드 (`build.ps1`, 292벌) | **7분 24초** · 실패 0 |
| 증분 빌드 | **없다.** `gen.py` 가 `build-src` 를, `build.ps1` 이 `dist` 를 통째로 지우고 시작한다. 테마 한 벌만 고쳐도 292벌을 전부 다시 그리고 다시 포장한다 |

## 단계별 배분

| 단계 | 시간 | 비중 |
|---|---|---|
| 소스 생성 `gen.py` (그림 30,848장) | 2분 46초 | 37% |
| 커스텀 템플릿 `mix.py` | 7초 | 2% |
| **패키징 (zip + APK, 292벌)** | **4분 31초** | **61%** |

## 1. 가장 비싼 빌드 도구 (핸드오프의 "무거운 헤더" 자리)

테마 한 벌을 순차로 돌려 잰 값. 5벌 표본, 단위 초.

| 도구 | 최소 | 최대 | 성격 |
|---|---|---|---|
| **`aapt2 compile`** | **0.15** | **4.34** | **PNG 재압축(crunch). 편차 30배. 패키징 지배** |
| `apksigner` (JVM) | 0.66 | 0.83 | 거의 고정. 292벌이면 약 220초 CPU |
| `aapt2 link` | 0.16 | 0.19 | |
| iOS `.ktheme` zip | 0.03 | 0.11 | 무시 가능 |
| `zipalign` | 0.04 | 0.06 | |
| `powershell` 프로세스 3개/테마 | 0.54 | | 미미 |

`--no-crunch` 를 붙이면 `aapt2 compile` 이 **4.15초 → 0.05초 (83배)** 로 떨어진다. 다만 산출물이
커지는 정도가 테마마다 다르다: terrazzo-light-image 1,892KB → 2,512KB (+33%),
neonzoo-sea 1,554KB → 1,570KB (+1%). 그냥 끄면 안 되고, Pillow 쪽 저장 형식을 손봐야 한다.

## 2. 가장 비싼 테마 (핸드오프의 "비싼 TU" 자리)

`gen.py` 벽시계 169.7초 · CPU 합 1,198.7초 · 8워커 · **병렬 효율 88%**.
테마당 중앙값 3.18초, 최소 0.30초, 최대 16.62초 — **편차 55배**.

| 테마 | 초 |
|---|---|
| neonlounge-octagon | 16.62 |
| neonlounge-bracket | 16.34 |
| watercolor-dark-image | 15.62 |
| watercolor-light-image | 15.23 |
| midnight-glow-image | 15.09 |
| neonlounge-underline | 14.58 |
| neonlounge-split | 14.57 |
| stained-amber | 13.60 |
| gold-glow-image | 13.32 |
| purple-glow-image | 13.26 |

가장 싼 쪽은 도트 계열(lcd/retro/quest)로 0.30~0.33초다.

## 3. 가장 비싼 연산 (핸드오프의 "템플릿 인스턴스화" 자리)

비싼 두 벌(neonlounge-octagon, watercolor-dark-image)을 cProfile 로 잰 45.07초 기준.

| 항목 | 초 | 비중 | 메모 |
|---|---|---|---|
| `gen.chat_bg` (누적) | 32.66 | 72% | **2벌에 20회 호출 = 테마당 10회** |
| `random.randint` | **21.47** | **48%** | **1,826만 회. 순수 호출 오버헤드가 거의 전부** |
| PNG 인코딩 (`ImagingEncoder.encode`) | 10.56 | 23% | 210장 |
| `scenes.neonwall` | 21.02 | 47% | 10회 |
| `scenes.watercolor` | 11.63 | 26% | 10회 |
| `gaussian_blur` | 3.98 | 9% | 462회 |

### 확인된 중복

`gen.py` 는 같은 배경을 **크기만 바꿔 세 번 그린다** — iOS `@2x`(600×1300), iOS `@3x`(900×1950),
안드로이드(1080×1920). `chat_bg`/`main_bg`/`passcode_bg` 각각에 대해 그래서 테마당 9회,
`splash` 까지 10회다. 저장소 전체에 캐시가 하나도 없다(`lru_cache` 0건).

`random.randint` 1,826만 회는 픽셀 단위 루프에서 나온다. `randint` 는 파이썬 난수 중 가장 비싸다
(`_randbelow_with_getrandbits` → `getrandbits` → `_operator.index` → `bit_length` 를 매번 탄다).
호출 하나당 1.18μs 다.

## 아직 설명 못 한 것

패키징의 병렬 효율이 낮다. 테마당 순차 비용은 약 3.2초인데(도구 2.7 + 프로세스 0.5),
`3.2 × 292 / 8 = 117초` 여야 할 것이 실제로는 **271초** 걸렸다. 효율 43% 다.
표본 편향은 아니다(표본 평균 1,003KB vs 전체 평균 838KB). 후보는 디스크 I/O 경합,
JVM 8개 동시 실행, `build.ps1` 의 120ms 폴링 루프(292회면 최대 35초)다.
`gen.py` 쪽은 같은 8워커로 효율 88% 라 기계 문제는 아니다.

## 측정 방법

저장소 코드는 고치지 않았다. 스크립트는 세션 스크래치패드에 뒀다.

- 단계 배분: `build.ps1` 출력에 경과 시각을 붙여 받음
- 도구별: 테마 5벌에 `aapt2`/`zipalign`/`apksigner` 를 직접 순차 호출
- 테마별: `gen.build_one` 을 `multiprocessing.Pool` 로 돌리며 각각 계시
- 연산별: 비싼 2벌을 단일 프로세스 `cProfile`
