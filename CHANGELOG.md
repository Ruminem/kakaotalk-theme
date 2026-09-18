# Changelog

Written back from the GitHub release notes. There are 50 tags, so patch releases are folded
into their minor version and marked inline (`0.35.1:`).

깃허브 릴리스 본문에서 모아 소급해 적은 것임. 태그가 50개라 패치는 마이너 안에 접어 넣고
`0.35.1:` 처럼 표시했음.

## 0.38 — 2026-09-18

- Nine new Neon Sign families, 36 themes. v6–v13 keep the four tube bubbles from v4/v5 but drop the wall: constellations, drifting petals, bokeh, plasma threads, spreading ink, a laser mesh, crystal facets, chromatic aberration.
- **Neon Zoo** — the four sets differ by which neon animal hangs on the wall (sea, forest, ice, mixed). The same animals show up as the default profile pictures in the chat list.
- **Custom themes** — pick a background from one theme and bubbles from another and mix them, in the browser ([make page](https://ruminem.github.io/kakaotalk-theme/docs/make.html)) or on a PC with `tools/mix.py`. 168 backgrounds to choose from.
- Neon Sign families moved from `docs/themes/lights.md` to `docs/themes/lights-neon.md`. Bookmarked links to the old page no longer resolve.
- Apache-2.0 license added. Until now the repo had no license, which legally meant all rights reserved.
- All 256 existing themes are unchanged image-for-image; only the version number moved, so they update in place.

**한국어**

- 네온사인 새 계열 아홉, 36벌. v6~v13 은 v4·v5 의 말풍선 네 가지를 그대로 쓰고 벽을 걷어냄 — 별자리 · 꽃잎 · 보케 · 플라즈마 실 · 잉크 번짐 · 레이저 그물 · 크리스탈 · 색수차.
- **네온 동물** — 벽에 어느 동물이 걸려 있느냐로 네 벌을 가름(바다 · 숲 · 얼음 · 모둠). 같은 동물이 목록 화면 기본 프로필로도 나옴.
- **커스텀 테마** — 배경은 이 테마, 말풍선은 저 테마로 골라 섞을 수 있음. 폰 브라우저([만들기 페이지](https://ruminem.github.io/kakaotalk-theme/docs/make.html))나 PC 의 `tools/mix.py` 로 함. 고를 수 있는 배경이 168벌임.
- 네온사인 계열이 `docs/themes/lights.md` 에서 `docs/themes/lights-neon.md` 로 옮겨짐. 예전 주소를 저장해 뒀으면 안 열림.
- Apache-2.0 라이선스를 넣었음. 여태 표기가 없어서 법적으로는 모든 권리 보유였음.
- 기존 256벌은 그림이 한 장도 안 바뀌었음. 버전만 올라가서 업데이트로 받아짐.

## 0.37 — 2026-09-16

- New family: **Neon Sign v5** — neon hung on a dark plaster wall, swept by two warm uplights. Same four bubbles as v4.
- Neon Sign v4's plank wall redrawn with growth-ring grain and a warm bar light. The old straight-line grain read as a barcode.

**한국어**

- 새 계열 **네온사인 v5** — 짙은 미장 벽에 네온사인을 걸고 따뜻한 간접등 두 개로 벽을 쓸어내림. 말풍선 넷은 v4 와 같음.
- 네온사인 v4 의 판자 벽을 나이테 결과 따뜻한 바 조명으로 다시 그림. 곧은 선으로 그은 옛 결은 바코드처럼 보였음.

## 0.36 — 2026-09-16

- Five new Lights families derived from Red: **Blue, Purple, Green, Gold, Pink**. Same black ground, bright bubbles and rising embers, in a new color. Four variants each.
- Three new Neon Sign families: **v2** (shuttered alley), **v3** (tiled basement bar), **v4** (wooden plank wall with four newly drawn bubbles — octagon, bracket, underline, twin tube). Only lit tubes glow, and they glow in their own color.

**한국어**

- 레드에서 파생한 불빛 계열 다섯: **블루 · 퍼플 · 그린 · 골드 · 핑크**. 검은 바탕, 쨍한 말풍선, 아래서 떠오르는 불티를 색만 바꿔 옮겼음. 각각 네 벌임.
- 네온사인 새 계열 셋: **v2**(셔터 내린 골목), **v3**(지하 바 타일 벽), **v4**(나무 판자 벽에 팔각 · 꺾쇠 · 밑줄 · 두 가닥 말풍선을 새로 그림). 불이 켜진 관에서만, 그 관 제 색으로 빛이 번짐.

## 0.35 — 2026-09-15

- Six new Glass families where the material shows on the bubble surface, not just the border: **Sea Glass, Glass Block, Ice, Reeded Glass, Acrylic, Resin**. Four variants each (light / light+background / dark / dark+background).
- Glass chat lists keep their background unblurred behind translucent cells, so the family is visible in the list too.
- Family icons in the README and category pages now jump to the family instead of opening the raw PNG.
- `0.35.1` (2026-09-16): fixed the seams across the top of the iOS chat list. iOS draws the status bar, title and filter chips as separate bands and restarts the background image in each one, so nearly all 110 themes with a list background showed steps at the band edges. The top of every list background is now filled with a per-column average that fades into the artwork below. Acrylic also got a dedicated list background.

**한국어**

- 유리 새 계열 여섯. 테두리 색만 다른 게 아니라 재질이 말풍선 표면에 드러남: **씨글래스 · 글래스 블록 · 얼음 · 골판 유리 · 아크릴 · 레진**. 각각 네 벌(밝음 / 밝음+배경 / 어두움 / 어두움+배경)임.
- 유리 계열 목록 화면은 배경을 흐리지 않고 깔아, 반투명 셀 너머로 재질이 비침. 목록에서도 계열이 보임.
- README 와 카테고리 문서의 계열 아이콘을 누르면 PNG 파일 화면 대신 그 계열로 감.
- `0.35.1`(2026-09-16): iOS 목록 머리에 층이 지던 것을 고침. iOS 는 상태줄 · 제목 · 필터 칩 줄을 띠마다 따로 그리고 띠마다 배경을 맨 위부터 새로 깔아서, 목록 배경이 있는 110벌 거의 전부가 띠 경계마다 층이 졌음. 이제 모든 목록 배경의 위쪽을 열마다 평균 색으로 채우고 아래 그림으로 서서히 이어감. 아크릴은 목록 배경을 따로 줬음.

## 0.34 — 2026-09-15

- Five new Pattern families on repeating backdrops, with a solid bubble and one prop on the first message: **Gingham, Polka Dot, Terrazzo, Marine Stripe, Checkerboard**. Four variants each.
- Each family gets its own default profile pictures, tiled faintly with the family pattern so the chat list tells them apart.

**한국어**

- 반복 무늬 바탕에 단색 말풍선, 첫 말에 소품 하나를 둔 무늬 계열 다섯: **깅엄 체크 · 폴카 도트 · 테라조 · 마린 스트라이프 · 체커보드**. 각각 네 벌임.
- 계열마다 기본 프로필이 따로 있고, 판에 그 계열 무늬를 옅게 깔아 목록에서 서로 구분됨.

## 0.33 — 2026-09-15

- Four new Comfort families, built for long reading rather than punch: **Watercolor, Ink Wash, Rainy Window, Papercut**. Four variants each.
- Comfort themes are now checked by number — saturation at or below 0.25, bubble-to-floor contrast between 1.2 and 2.0, text contrast at least 4.5, no pure white or black. A theme that misses the mark fails the build.

**한국어**

- 쨍한 쪽이 아니라 오래 보기 편한 쪽으로 만든 편안함 계열 넷: **수채화 · 수묵화 · 비 오는 창가 · 페이퍼컷**. 각각 네 벌임.
- 편안함 계열은 이제 숫자로 검사함 — 채도 0.25 이하, 말풍선↔바닥 대비 1.2~2.0, 글자 대비 4.5 이상, 순백·순흑 안 씀. 어기면 생성이 멈춤.

## 0.32 — 2026-09-15

- Four new Pixel families in real 8-bit: **Pixel Quest** (RPG dialogue box), **Pixel LCD** (four-tone green screen), **Retro PC** (old desktop windows), **Pixel Farm** (nailed wooden signs). One dot is 4pt, so it stays chunky on a phone; tab icons are pixel art too.
- Two new categories. **Comfort** takes Calm and Hush out of Pattern; **Pixel** takes Arcade out of Character. The themes themselves are unchanged, but their category pages moved — Calm and Hush to `docs/themes/comfort.md`, Arcade to `docs/themes/pixel.md`.

**한국어**

- 진짜 8비트로 그린 도트 계열 넷: **도트 모험**(RPG 대화창), **도트 액정**(초록 네 색 액정), **레트로 PC**(옛 컴퓨터 창), **도트 농장**(못 박힌 나무 팻말). 한 칸이 4pt 라 폰에서도 굵게 보이고, 탭 아이콘도 도트임.
- 카테고리 둘이 늘었음. **편안함**은 차분·고요를 무늬에서, **도트**는 오락실을 캐릭터에서 옮겨 옴. 테마 자체는 안 바뀌었지만 카테고리 문서 주소가 바뀜 — 차분·고요는 `docs/themes/comfort.md`, 오락실은 `docs/themes/pixel.md`.

## 0.31 — 2026-09-14

- New family: **Neon Sign**. Glass tubes on a dark brick wall, the center of the tube burning white. The four variants are four bubble designs (twin tube, signboard, electrode, tail).
- Glow shapes are now picked by name from a shared dictionary instead of hand-tuned per theme. Existing themes verified unchanged by hash.
- The README outgrew a phone screen at 1,600 lines, so family details moved into one page per category under `docs/themes/`. The README keeps the thumbnail grids.
- `0.31.1`: redrew the glow on Terminal's two glow variants. The white-tinted edge band read as a gray border on a black-and-green screen, not as light.
- `0.31.2`: Neon Sign's chat list is now neon too — neon profile pictures, neon tab icons that light up only when selected, and the brick wall showing through translucent cells.
- `0.31.3`: that rule extended to every family. 21 families without a character got three motif profile pictures, glow variants got neon tab icons, and any theme with a list background got translucent cells (0.72). Bubbles, chat rooms and lock screens unchanged.

**한국어**

- 새 계열 **네온사인**. 어두운 벽돌 벽에 걸린 유리관이고 관 한가운데가 하얗게 달아오름. 네 벌이 곧 말풍선 디자인 네 가지(이중관 · 간판 · 전극 · 말꼬리)임.
- 글로우를 테마마다 손으로 짜지 않고 사전에서 이름으로 고르게 바꿈. 기존 테마는 해시로 대조해 안 바뀐 것을 확인했음.
- README 가 1600줄을 넘어 폰에서 감당이 안 돼서, 계열 상세를 카테고리마다 문서 한 장(`docs/themes/`)으로 나눔. README 에는 썸네일 격자만 남음.
- `0.31.1`: 터미널 글로우 두 벌의 빛을 다시 그림. 흰 쪽으로 밝힌 가장자리 띠가 검은 초록 화면에서는 빛이 아니라 회백색 테두리로 보였음.
- `0.31.2`: 네온사인 목록 화면도 네온으로 채움 — 네온 프로필, 선택한 탭만 불이 켜지는 네온 탭 아이콘, 반투명 셀 너머로 비치는 벽돌 벽.
- `0.31.3`: 그 규칙을 모든 계열로 넓힘. 캐릭터가 없는 21계열은 계열 물건 프로필 세 장, 글로우 변형은 네온관 탭 아이콘, 목록 배경이 있는 테마는 셀이 반투명(0.72)해짐. 말풍선·채팅방·잠금화면은 그대로임.

## 0.30 — 2026-09-14

- Ten new families, forty themes. 100 themes to 140.
- Lights: **Fireworks, Lanterns, String Lights, Highway, Terminal**.
- Character: **Cinema, Bakery, Camping, Space, Greenhouse** — shaped bubbles with a prop on the first message and a character profile picture.
- Camping's sign glows with firelight; in dark+background the corner nearest the fire catches it.

**한국어**

- 새 계열 열 개, 테마 마흔 개. 100벌에서 140벌이 됐음.
- 불빛: **불꽃놀이 · 연등 · 알전구 · 고속도로 · 터미널**.
- 캐릭터: **영화관 · 빵집 · 캠핑 · 우주 · 온실** — 모양 있는 말풍선에 첫 말 소품이 붙고 프로필이 캐릭터임.
- 캠핑은 팻말이 모닥불 주황빛으로 빛나고, 어두움+배경은 불 쪽 귀퉁이가 그 빛에 물듦.

## 0.29 — 2026-09-12

- New **Character** category, five families, all bubbles and characters newly drawn: **Post Office** (envelope), **Desk** (sticky note), **Arcade** (pixel steps), **Laundry** and **Laundry Shine** (jelly).
- Props (stamp, tape, tail, droplet) sit only on the first bubble of a run, and only where the bubble does not stretch, so they hold their shape on long messages.
- These families use light / light+background / dark / dark+background instead of the usual glow axis.
- `0.29.1`: Stained Glass backgrounds redrawn with real backlight — pieces in front of the source heat up and keep their color instead of just being dimmed further away.
- `0.29.2`: jelly gloss on the Laundry families rebuilt as stacked layers (reflection, hotspot, pooled light, edge thickness, tinted shadow) instead of white pills on a band.
- `0.29.3`: **Laundry Shine merged into Laundry** — two families that differed only in gloss were not worth separating. The new Laundry is the old Laundry Shine. If you had Laundry Shine installed it will not update; delete it and install Laundry. Top-edge gloss redrawn so light always falls from the upper left, on both sent and received bubbles.

**한국어**

- 새 카테고리 **캐릭터**, 계열 다섯. 말풍선과 캐릭터를 전부 새로 그렸음: **우체국**(편지봉투), **책상**(포스트잇), **오락실**(픽셀 계단), **빨래**와 **빨래 반짝**(젤리).
- 우표 · 테이프 · 꼬리 · 물방울 같은 소품은 연달아 보낸 말의 첫 말풍선에만, 그리고 늘어나지 않는 자리에만 붙임. 말이 길어져도 소품은 그대로임.
- 이 계열들은 기존 글로우 축 대신 밝음 / 밝음+배경 / 어두움 / 어두움+배경으로 넷을 만듦.
- `0.29.1`: 스테인드 글래스 배경을 역광으로 다시 그림. 광원 앞 조각이 제 색을 지닌 채 달아오름 — 전에는 먼 곳을 어둡게 누르기만 했음.
- `0.29.2`: 빨래 계열의 젤리 광택을 층으로 다시 쌓음(반사 · 가장 밝은 점 · 고인 빛 · 가장자리 두께 · 물든 그림자). 전에는 흰 알약을 띠에 얹은 정도였음.
- `0.29.3`: **빨래 반짝을 빨래로 합침** — 광택만 다른 두 계열은 나눠 둘 까닭이 없었음. 새 빨래가 옛 빨래 반짝임. 빨래 반짝을 깔았으면 업데이트로 안 이어지니 지우고 빨래를 새로 깔면 됨. 윗쪽 광택도 다시 그려서, 보낸 쪽이든 받은 쪽이든 빛이 늘 왼쪽 위에서 듦.

## 0.28

Withdrawn. The two families it added were drawn too close to a reference screenshot, so the whole release was deleted rather than patched.

**한국어**

물렸음. 이 릴리스에 넣은 두 계열이 참고 화면을 너무 그대로 옮긴 것이라, 고치지 않고 릴리스째 지웠음.

## 0.27 — 2026-09-12

- New family: **Hush** (olive, mist, plum, sumi). Same numeric standard as Calm, but each color has a name rather than being near-neutral.
- `0.27.1`: Stained Glass backgrounds redrawn as leaded glass pieces instead of blurred color; Rosewood Glass grain redrawn with arching figure and knots the grain flows around. Previews now render at 3× like the phone.

**한국어**

- 새 계열 **고요**(올리브 · 안개 · 자두 · 먹). 차분과 같은 숫자 기준으로 만들었지만, 무채색에 가까운 차분과 달리 색 이름이 하나씩 붙는 쪽임.
- `0.27.1`: 스테인드 글래스 배경을 흐린 색 덩어리에서 납선으로 이은 색유리 조각으로 다시 그림. 원목 글래스 결도 아치꼴 무늬결과, 결이 돌아 흐르는 옹이로 다시 그림. 미리보기를 폰과 같은 3배로 그리게 바꿈.

## 0.26 — 2026-09-12

- New family: **Calm** (sage, sand, slate, mocha) — the first set built for tired eyes. Saturation 0.09–0.28, text contrast 7.8–13.1, no pure white or black, no glow and no background image. Its four variants are four colors instead of the usual axis.

**한국어**

- 새 계열 **차분**(세이지 · 샌드 · 슬레이트 · 모카) — 눈이 편한 것을 목적으로 만든 첫 계열임. 채도 0.09~0.28, 글자 대비 7.8~13.1, 순백·순흑 안 씀, 글로우와 배경 그림도 안 씀. 그래서 네 벌의 축이 배경/글로우가 아니라 색임.

## 0.25 — 2026-09-12

- Three new Glass families: **Stained Glass** (four colors as the four variants), **Prism Glass** (cyan top edge, magenta bottom), **Frosted Glass**.
- New **Glass** category — half of Pattern had become glass.
- Includes the 0.24.1 glow border fix.

**한국어**

- 유리 새 계열 셋: **스테인드 글래스**(색 네 개가 곧 네 벌), **프리즘 글래스**(위 테두리는 시안, 아래는 마젠타), **프로스트 글래스**.
- **유리** 카테고리를 새로 만듦 — 무늬 열 계열 중 절반이 유리가 됐었음.
- 0.24.1 의 글로우 테두리 수정도 여기 그대로 들어 있음.

## 0.24 — 2026-09-12

- New family: **Rosewood Glass** — glass bubbles over wood grain, oak and walnut × background and solid. Glass only reads as glass when there is something behind it, and grain gives it lines to cross.
- The list background keeps the straight grain unblurred; knots and plank seams are left out of that copy so nothing shows a cut edge.
- `0.24.1`: glow borders were going gray. Brightening in RGB drains saturation from dark colors — Red's received bubble fell from 0.81 to 0.09, so a red theme had a gray glow. Now hue is kept and only lightness rises. All 32 glow themes changed; the other 32 files are untouched.

**한국어**

- 새 계열 **원목 글래스** — 나무결 위에 유리 말풍선을 얹음. 오크 · 월넛 × 배경 · 단색임. 유리는 뒤에 볼 게 있어야 유리로 읽히는데, 결은 선이 있어서 말풍선을 지나감.
- 목록 배경은 곧은결을 흐리지 않고 그대로 깖. 대신 옹이와 판자 이음새는 뺐음 — 그건 굴곡이라 잘리면 자국이 남음.
- `0.24.1`: 글로우 테두리가 회색이 되던 것을 고침. RGB 로 밝히면 진한 색이 채도를 잃음 — 레드의 받은 말풍선이 0.81 에서 0.09 로 떨어져 빨간 테마인데 테두리만 잿빛이었음. 이제 색상은 두고 명도만 올림. 글로우가 있는 32벌만 바뀌고 나머지 32벌은 파일이 한 장도 안 바뀜.

## 0.23 — 2026-09-12

- Every slot in the spec is now filled. Nine attributes and one block were still unused, so those spots kept KakaoTalk's stock artwork under a themed app.
- Newly themed: the add-friend button, the eight lock-screen dots (a different color per position), the keypad press state, and the Android tab bar background.
- iOS tab bar background stays a flat color — the guide has no attribute for an image there, and invented names are silently ignored.

**한국어**

- 규격에 남아 있던 자리를 전부 채웠음. 속성 아홉 개와 블록 하나를 안 쓰고 있어서, 테마를 깔아도 그 자리만 카톡 기본 그림이 남아 있었음.
- 새로 칠해진 곳: 친구추가 단추, 잠금화면 동그라미 여덟 장(자리마다 색이 다름), 키패드 눌림, 안드로이드 탭바 배경.
- iOS 탭바 배경은 색으로만 둠 — 가이드에 그림을 넣는 속성이 아예 없고, 이름을 지어내면 카톡이 조용히 무시함.

## 0.22 — 2026-09-12

- Two new families: **Cyberpunk** (neon grid horizon and a sliced sun) and **Red** (embers rising over a dark crimson ground). Four variants each.

**한국어**

- 새 계열 둘: **사이버펑크**(지평선까지 뻗은 네온 격자와 가로로 잘린 해)와 **레드**(검붉은 바탕에 아래서 떠오르는 불티). 각각 네 벌임.

## 0.21 — 2026-09-12

- **Liquid Glass Solid** and **Liquid Glass Dark Solid** — the glass without a background image.
- Light glass was invisible on a white ground; the edge now has a bright line above and a dark line below, the way light actually bends through glass.
- Midnight `background` and Candy Pop `candy background` lost their glow. They were labeled as background-only but carried a glow, making them duplicates of their own glow+background sibling. **Those two screens change on update**; the old look is the glow+background variant.
- Background art in the same family used to come out identical down to each star. Each theme now seeds its own image.
- Preview images use the same names as the released files.

**한국어**

- **리퀴드 글래스 단색**과 **리퀴드 글래스 다크 단색** — 배경 그림 없이 유리만 남긴 것임.
- 라이트 유리가 흰 바탕에서 아무것도 안 보였음. 유리 가장자리에서 빛은 두 번 꺾이므로 위에 밝은 선, 아래에 어두운 선을 같이 세웠음.
- 심야 `배경` 과 캔디 팝 `사탕 배경` 에서 글로우를 뺐음. 이름표는 배경인데 글로우가 달려 있어서 같은 계열의 글로우+배경과 사실상 같은 테마였음. **이 두 벌은 업데이트하면 화면이 달라짐** — 예전 모습을 원하면 글로우+배경을 받으면 됨.
- 같은 계열의 배경 그림이 별 하나까지 똑같이 나오던 것을 고침. 이제 테마마다 씨앗이 다름.
- 미리보기 그림도 배포 파일과 같은 이름을 씀.

## 0.20 — 2026-09-12

- **Default profile pictures follow the theme.** Three per theme, the only slot in the spec that takes multiple images, so the chat list shows a mix.
- Previews now draw the real theme artwork instead of their own stand-ins.
- `0.20.1`: the light laid over backgrounds was rebuilt. Lighting all four edges equally looked like a picture frame, not light; the source now sits off the upper-left corner with the opposite corner pressed down.
- `0.20.2`: chat-list backgrounds are blurred into a texture. KakaoTalk stacks opaque things on that list (filter chips, ad cards, cells) and any picture underneath was cut into rectangles at their edges. Chat room and lock screen keep the full image. README thumbnail links now point at the real anchor ids so they work in mobile browsers.

**한국어**

- **기본 프로필이 테마 색을 따라감.** 테마마다 세 장임 — 규격에서 유일하게 여러 장을 받는 자리라 목록에 세 가지가 섞여 보임.
- 미리보기가 자기 그림을 따로 그리지 않고 실제 테마에 들어가는 그림을 씀.
- `0.20.1`: 배경에 얹던 빛을 다시 만듦. 사방을 똑같이 밝히니 빛이 아니라 액자 테두리로 보였음. 이제 광원을 화면 밖 왼쪽 위에 두고 반대쪽 아래 구석은 살짝 누름.
- `0.20.2`: 목록 배경을 크게 흐려 질감으로 바꿈. 카톡이 목록 위에 불투명한 것을 잔뜩 얹어서(필터 칩 줄 · 광고 카드 · 셀) 그 가장자리마다 그림이 네모나게 잘려 보였음. 채팅방과 잠금화면은 그림 그대로임. README 썸네일 링크는 진짜 id 를 가리키게 바꿔 모바일 브라우저에서도 움직임.

## 0.19 — 2026-09-12

- **Every family is now a set of four** — basic, background, glow, glow+background. 21 themes to 50.
- Ink Mint, Cream Latte and Mixed had no background art at all; each got one drawn from its own palette.
- Variants always appear in the same order, so families can be compared side by side.

**한국어**

- **열두 계열이 전부 네 벌이 됐음** — 기본 · 배경 · 글로우 · 글로우+배경. 21벌에서 50벌로.
- 먹빛 민트 · 크림 라떼 · 믹스드는 배경 그림이 아예 없었음. 각 계열 팔레트를 그대로 써서 새로 그렸음.
- 계열 안 차례가 늘 같아서 계열끼리 나란히 비교됨.

## 0.18 — 2026-09-12

- **Tab icons follow the theme.** Seven icons × normal and selected, 14 images per theme. Drawn as filled shapes because lines mush at 28pt. All 21 themes changed.

**한국어**

- **탭 아이콘이 테마 색을 따라감.** 7종 × 보통·선택 = 테마마다 14장임. 28pt 에서는 선이 뭉개져서 채운 도형으로 그렸음. 21벌 전부 바뀜.

## 0.17 — 2026-09-12

- **File names say what they are** — `city21.ktheme` became `city-glow-image.ktheme`. Package names and iOS theme IDs changed with them.
- **Installed themes must be deleted and reinstalled.** The theme ID changed, so the new file installs alongside the old one instead of updating it. Done now, while few people had installed anything; names will not change again.

**한국어**

- **파일 이름만 봐도 무엇인지 알게 됐음** — `city21.ktheme` 가 `city-glow-image.ktheme` 가 됨. 패키지 이름과 iOS 테마 ID 도 같이 바꿨음.
- **이미 깐 테마는 지우고 새로 깔아야 함.** 테마 ID 가 바뀌어서 업데이트로 안 이어지고 별개 테마로 들어감. 받아 간 사람이 거의 없을 때 바꿔두는 게 나아서 지금 했고, 앞으로는 안 바꿈.

## 0.16 — 2026-09-12

- **Night View became four themes** — basic, background, glow, glow+background. Every family added from here on ships as a set of four, and the variant label shows in the phone's theme list.
- An existing Night View updates in place and is renamed to `Night View Background`.

**한국어**

- **야경이 네 벌이 됐음** — 기본 · 배경 · 글로우 · 글로우+배경. 앞으로 테마를 더할 때는 늘 네 벌을 함께 내고, 이름표가 폰의 테마 목록에도 그대로 붙음.
- 기존 야경을 쓰고 있었으면 그대로 업데이트되고 이름만 `야경 배경` 으로 바뀜.

## 0.15 — 2026-09-12

- Five new themes: **Sea, Forest, Night View, Snowfield, Shapes**, each with its own drawn background.
- The rules for new themes are now enforced in code — no glow, no gradient bubbles, four distinct bubble colors, background art on all three screens. Breaking one stops the build. Themes made before the rule are left alone.

**한국어**

- 새 테마 다섯: **바다 · 숲 · 야경 · 설원 · 도형**. 배경 그림을 다섯 종 다 따로 그렸음.
- 새 테마 기본 규칙을 코드로 못 박았음 — 글로우 없음, 말풍선 그라데이션 없음, 말풍선 네 칸이 서로 다른 색, 배경 그림이 세 화면에 다 있음. 어기면 빌드가 멈춤. 규칙 이전 테마는 그대로 둠.

## 0.14 — 2026-09-12

- Two new themes: **Candy Pop v3** (scattered candy background) and **Cherry Blossom Shade v2** (branches and petals).
- Blurred shapes were being clipped to a rectangle by their own canvas. Blur radius is now allowed for as margin.

**한국어**

- 새 테마 둘: **캔디 팝 v3**(사탕을 흩뿌린 배경)와 **벚꽃 그늘 v2**(가지와 꽃잎).
- 흐린 도형이 제 캔버스에 네모로 잘리던 것을 고침. 이제 흐림 반경만큼 여백을 잡음.

## 0.13 — 2026-09-12

- **Midnight's background is a real drawing** — stars with a Milky Way band, a crescent with a halo, three ridge layers, atmospheric light at the horizon. Seeded, so the sky does not change between builds.
- Glow rebuilt as a thin band plus a wide band, brighter at the top, with a gamma curve on the outer bleed.
- `0.13.1`: the rectangle around each bubble is gone. The outer bleed's tail stayed at alpha ~17 all the way to the edge of the margin, so the whole rectangle floated faintly. Per-theme icons added, including the one KakaoTalk shows in its theme list. Quality work now goes out as a patch number.
- `0.13.2`: theme icons redrawn to look like app icons (vignette, shadow, top gloss). Pressed states across list names, status messages, last messages and bubble text now shift toward the accent color — KakaoTalk animates between the two states, but most of them had been identical, so nothing happened.

**한국어**

- **심야 배경이 진짜 그림이 됐음** — 은하수 띠에 몰아 넣은 별, 달무리 두른 초승달, 능선 세 겹, 지평선의 대기 빛. 씨앗을 고정해서 빌드할 때마다 하늘이 바뀌지 않음.
- 글로우를 얇은 띠 + 넓은 띠 두 겹으로 다시 만들고, 위쪽을 더 밝게, 바깥 번짐에 감마를 씌웠음.
- `0.13.1`: 말풍선 둘레의 네모가 없어짐. 바깥 번짐의 꼬리가 알파 17 쯤으로 여백 끝까지 남아서 그 사각형 전체가 옅게 떠 있었음. 테마마다 아이콘을 만들어 카톡 테마 목록에 뜨는 자리에도 넣었음. 이제 품질 개선은 패치 번호로 나감.
- `0.13.2`: 테마 아이콘을 앱 아이콘처럼 다시 그림(비네팅 · 그림자 · 위쪽 광택). 목록의 이름 · 상태메시지 · 마지막 메시지 · 말풍선 글자의 눌림 색이 포인트색 쪽으로 바뀜 — 카톡이 두 상태 사이를 이어주는데 그 둘이 똑같으면 아무 일도 안 일어났음.

## 0.12 — 2026-09-12

- New theme: **Midnight**, the first to put background art on all three screens, drawn differently for each.
- Lock screen background images are now supported (visible only if you have a KakaoTalk passcode set), and the preview gained a lock screen.
- Full spec written up in `docs/spec.md`.

**한국어**

- 새 테마 **심야**. 배경 그림을 세 화면에 다 까는 첫 테마이고, 세 곳을 각각 다르게 그렸음.
- 잠금화면 배경 그림을 넣을 수 있게 됐고(카톡 비밀번호를 걸어야 보이는 화면임) 미리보기에도 잠금화면이 생겼음.
- 규격 전체를 `docs/spec.md` 에 정리했음.

## 0.11 — 2026-09-12

- Glow rebuilt after seeing it on a phone. The blur was being cut off at the image edge, leaving a visible rectangle; it was a single blur, so the falloff read as a band; and the inner glow was a fixed-width ring. Now three stacked blurs windowed to zero at the edge, and an inner band derived by subtracting a blurred mask.

**한국어**

- 폰에서 보니 조잡해서 글로우를 다시 만듦. 흐림이 그림 경계에서 잘려 네모가 보였고, 흐림을 한 번만 걸어 낙차가 일정해 빛이 아니라 띠로 보였고, 안쪽 발광은 두께가 일정한 굵은 링이었음. 이제 반경이 다른 흐림 셋을 겹쳐 가장자리에서 0 이 되게 하고, 안쪽 띠는 마스크에서 흐린 마스크를 빼서 만듦.

## 0.10 — 2026-09-12

- Glow moved inside the bubble body. Shrinking the outer margin in 0.8 had made the halo too thin to see, and widening it again would push the bubbles apart. The inner edge costs no frame space.

**한국어**

- 글로우를 말풍선 몸통 안쪽으로 넣음. 0.8 에서 바깥 여백을 줄이면서 halo 가 너무 얇아져 원본과 구분이 안 됐는데, 여백을 다시 키우면 말풍선 사이가 또 벌어짐. 안쪽 테두리는 프레임 자리를 안 먹음.

## 0.9 — 2026-09-12

- Variants (v2) now sit right after their original in every list.
- **Android `versionCode` no longer follows list order.** Reordering would have lowered Mixed v2's code from 9 to 5, and Android refuses that as a downgrade. It is now derived from the theme key and version.

**한국어**

- 변형(v2)이 어느 목록에서나 원본 바로 뒤에 옴.
- **안드로이드 `versionCode` 를 목록 순서로 매기지 않음.** 그대로 순서를 바꿨으면 믹스드 v2 가 9에서 5로 내려갔고, 안드로이드는 그걸 다운그레이드로 보고 설치를 거부함. 이제 키 번호와 테마 버전으로 만듦.

## 0.8 — 2026-09-12

- **Bubbles sit closer together.** The bubble frame height *is* the gap between bubbles, so 12pt of glow margin showed up as empty space. Margin halved and the glow made denser to compensate.
- The preview now lays bubbles out the way KakaoTalk does — frame is text plus insets, artwork fills the whole frame — instead of drawing whatever looks good.

**한국어**

- **말풍선 사이가 좁아짐.** 말풍선 프레임 높이가 곧 말풍선 사이 간격이라, 글로우 여백 12pt 가 그대로 빈 공간이 됐음. 여백을 절반으로 줄이고 대신 더 진하게 만들어 보이는 정도는 유지했음.
- 미리보기가 카톡과 같은 방식으로 배치함 — 프레임은 글자 + `edgeinsets`, 그림은 프레임을 통째로 채움. 보기 좋게 그리는 게 아님.

## 0.7 — 2026-09-12

- **Glow was invisible on the phone.** The glow margin eats into the bubble frame, which pushed the text against the body, and the glow itself was spread too thin. Insets now grow with the margin, and the glow is denser near the body.

**한국어**

- **폰에서 글로우가 안 보이던 것을 고침.** 글로우 여백이 말풍선 프레임 안쪽에 들어가 글자가 몸통 가장자리에 붙었고, 넓게 흐린 탓에 알파가 얇게 퍼져 있었음. 이제 `edgeinsets` 를 여백만큼 같이 키우고, 몸통 가까운 쪽을 진하게 함.

## 0.6 — 2026-09-12

- Two new themes: **Mixed v2** and **Candy Pop v2**, the originals with glow.
- Glow color follows each bubble, so all four bubble slots glow in their own color.

**한국어**

- 새 테마 둘: **믹스드 v2** 와 **캔디 팝 v2**. 원본에 글로우를 얹은 것임.
- 글로우 색이 말풍선을 따라가서 말풍선 네 칸이 각자 제 색으로 빛남.

## 0.5 — 2026-09-12

- **Glow** added, on both glass themes — around the bubble and along the screen edge. Cap insets grow with the glow margin so the light does not smear when a bubble stretches.
- Mixed and Candy Pop bubbles are now solid color. Two-stop gradients looked messy in a theme that already has four bubble colors.

**한국어**

- **글로우**를 넣었음. 유리 테마 둘에 들어가고, 말풍선 둘레와 화면 가장자리 두 곳에 얹힘. 말풍선이 늘어날 때 빛이 뭉개지지 않게 cap 을 글로우 여백만큼 같이 키웠음.
- 믹스드와 캔디 팝 말풍선을 단색으로 바꿈. 색이 이미 네 가지인 테마에서 두 색을 세로로 흘리니 지저분했음.

## 0.4 — 2026-09-12

- Two new themes: **Liquid Glass** and **Liquid Glass Dark**. Translucent cells and bubbles let the background show through — all within the spec, nothing faked.
- Bubble drawing merged into one place so the preview and the shipped theme cannot drift apart.

**한국어**

- 새 테마 둘: **리퀴드 글래스**와 **리퀴드 글래스 다크**. 셀과 말풍선이 반투명이라 배경이 비침 — 규격 안에서 되는 것만 썼고 억지로 흉내 낸 게 아님.
- 말풍선 그리는 코드를 한 곳으로 합침. 따로 두면 미리보기와 실물이 어긋남.

## 0.3 — 2026-09-12

- Five new themes: **Cream Latte, Cherry Blossom Shade, Mixed, Aurora, Candy Pop**, joining Ink Mint. Six in total.
- Everything now generates from one palette table (`tools/themes.py`) — CSS, `colors.xml`, artwork, previews.
- Preview tool added: run `preview.ps1` and get every theme's screens on one page instead of installing them one by one.
- Android splash screens are drawn per theme. iOS has no splash block in the spec.

**한국어**

- 새 테마 다섯: **크림 라떼 · 벚꽃 그늘 · 믹스드 · 오로라 · 캔디 팝**. 먹빛 민트까지 여섯 개가 됐음.
- 원본을 팔레트 표 하나(`tools/themes.py`)로 모음 — CSS · `colors.xml` · 그림 · 미리보기가 전부 거기서 나옴.
- 미리보기 도구를 더함. `preview.ps1` 을 돌리면 테마마다 화면을 그려 한 페이지에 모아 줌. 폰에 하나씩 적용해보지 않아도 됨.
- 안드로이드 실행화면을 테마마다 따로 그림. iOS 는 규격에 스플래시 블록이 없어서 못 함.

## 0.2 — 2026-09-12

- **Bubbles got artwork** — a vertical gradient, mint to sky for sent, violet to magenta for received. Vertical so it does not smear when a bubble stretches sideways.
- iOS received-bubble text flipped to white; dark text on violet was unreadable.
- Android splash screen added.

**한국어**

- **말풍선이 생겼음** — 세로 그라데이션이고 보낸 쪽은 민트→하늘, 받은 쪽은 보라→자주임. 세로라 말풍선이 가로로 늘어나도 색이 안 뭉개짐.
- iOS 받은 말풍선 글자색을 흰색으로 뒤집었음. 보라 위에 어두운 글자는 안 읽힘.
- 안드로이드 실행화면을 더했음.

## 0.1 — 2026-09-12

- First release. **Ink Mint**, iOS and Android, colors only — not a single image, to see how far color alone gets.
- iOS bubble colors cannot be changed by color at all; `MessageCellStyle` has no `background-color`, only PNGs. Android bubbles do take a color, so the same v0 changes more there.
- Android APKs are built without gradle: `aapt2` → `zipalign` → `apksigner`. The theme requests no permissions.

**한국어**

- 첫 배포. **먹빛 민트**, iOS 와 안드로이드 양쪽 다 그림을 한 장도 안 쓰고 색만 지정한 v0 임. 색으로 어디까지 바뀌는지 실물로 확인하는 게 목적이었음.
- **iOS 는 말풍선 색이 안 바뀜.** `MessageCellStyle` 에 `background-color` 가 아예 없고 PNG 로만 지정됨. 안드로이드는 색이 먹어서 같은 v0 라도 그쪽이 더 많이 바뀌어 보임.
- 안드로이드 APK 는 gradle 없이 `aapt2` → `zipalign` → `apksigner` 로 빌드함. 테마는 권한을 하나도 요구하지 않음.
