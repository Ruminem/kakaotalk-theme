// SPDX-License-Identifier: Apache-2.0
//
// 안드로이드 커스텀 테마를 브라우저에서 만든다. 템플릿 APK 한 벌에 배경 쪽 테마의
// 배경 그림과 말풍선 쪽 테마의 나머지 그림을 담고, 색과 테마 이름을 고쳐 다시 서명한다.
//
// 왜 템플릿이 필요한가 — 패키지 이름과 색과 테마 이름은 압축된 이진 파일
// (`AndroidManifest.xml`·`resources.arsc`) 안에 있어서 길이가 바뀌면 자리가 밀린다.
// 그래서 템플릿을 미리 빌드해 둔다. 패키지 이름은 `com.kakao.talk.theme.custom` 으로
// 박혀 있고, 색은 찾아 바꾸기 쉬운 표식 값(`#FF0000xx`)으로, 테마 이름은 넉넉한
// 고정 길이 자리로 구워져 있다. 브라우저는 **같은 길이로 덮어쓰기만** 한다.
//
// 자세한 까닭과 뚫은 과정은 CLAUDE.md 의 `커스텀 테마 제작`. 고치면
// `node tools/check-apkmix.mjs` 를 돌린다 — 실제 테마로 섞어 apksigner 로 검증하고
// 안드로이드 에뮬레이터에 깔아 본다.
import { readZip, writeZip, crc32 } from './zip.js';
import { resign } from './apksign.js';

const DIR = 'res/drawable-xxhdpi-v4/';
// 배경 쪽 테마에서 가져오는 것. tools/mix.py 의 BG_KEYS 와 짝이다 —
// 실행화면(splash)은 말풍선 쪽 팔레트로 그려지므로 여기 넣지 않는다
export const BG_FILES = [
  `${DIR}theme_chatroom_background_image.png`,
  `${DIR}theme_passcode_background_image.png`,
  `${DIR}theme_background_image.png`,
];
const ARSC = 'resources.arsc';
// 안드로이드 11 부터 resources.arsc 는 압축 없이 4바이트 정렬이어야 설치된다
const ALIGN = 4;

/** 같은 길이로만 덮어쓴다. 길이가 바뀌면 문자열 풀의 자리가 전부 밀린다 */
function overwrite(buf, at, bytes) {
  buf.set(bytes, at);
}

function findAll(buf, needle) {
  const out = [];
  for (let i = 0; i + needle.length <= buf.length; i++) {
    let ok = true;
    for (let j = 0; j < needle.length; j++) {
      if (buf[i + j] !== needle[j]) { ok = false; break; }
    }
    if (ok) out.push(i);
  }
  return out;
}

/** `#AARRGGBB` -> arsc 안에 담긴 네 바이트 (리틀엔디언 ARGB) */
export function colorBytes(hex) {
  const v = parseInt(hex.replace('#', ''), 16) >>> 0;
  return new Uint8Array([v & 255, v >> 8 & 255, v >> 16 & 255, v >>> 24]);
}

/**
 * 표식 색을 실제 색으로 바꾼다.
 *
 * @param {Uint8Array} arsc 템플릿의 resources.arsc (제자리에서 고친다)
 * @param {string[]} marks 표식 색 목록 (`#FF000001` …). 템플릿과 같은 차례
 * @param {string[]} colors 그 자리에 들어갈 색. 같은 길이여야 한다
 */
export function patchColors(arsc, marks, colors) {
  if (marks.length !== colors.length) throw new Error('표식과 색의 개수가 다르다');
  marks.forEach((mark, i) => {
    const at = findAll(arsc, colorBytes(mark));
    // 표식은 딱 한 번 나와야 한다. 여러 번 나오면 색이 아닌 자리를 건드리게 된다
    if (at.length !== 1) throw new Error(`표식 ${mark} 가 ${at.length}번 나온다`);
    overwrite(arsc, at[0], colorBytes(colors[i]));
  });
}

/**
 * 테마 이름을 바꾼다. 템플릿에는 자리만큼의 채움 글자가 구워져 있고, 새 이름을 쓰고
 * 남는 자리는 공백으로 메운다 — **바이트 수가 같아야** 문자열 풀이 안 밀린다.
 * arsc 의 UTF-8 문자열은 [utf16 길이][utf8 길이][바이트들][0] 꼴이라 길이 두 칸도 고친다.
 */
export function patchName(arsc, filler, name) {
  const enc = new TextEncoder();
  const room = enc.encode(filler);
  const at = findAll(arsc, room);
  if (at.length !== 1) throw new Error(`이름 자리가 ${at.length}번 나온다`);
  let bytes = enc.encode(name);
  if (bytes.length > room.length) {
    // 자리에 안 들어가면 글자 단위로 줄인다. 반쪽 글자를 남기면 글자가 깨진다
    let cut = name;
    while (enc.encode(cut).length > room.length) cut = cut.slice(0, -1);
    bytes = enc.encode(cut);
  }
  const padded = new Uint8Array(room.length).fill(0x20);  // 남는 자리는 공백
  padded.set(bytes);
  overwrite(arsc, at[0], padded);
  // 길이 두 칸. 공백은 UTF-16 으로도 한 칸이라 utf16 길이 = 글자 수 + 공백 수
  const chars = [...new TextDecoder().decode(padded)].length;
  if (chars > 127 || room.length > 127) throw new Error('이름 자리가 127 바이트를 넘는다');
  arsc[at[0] - 2] = chars;
  arsc[at[0] - 1] = room.length;
}

/**
 * 커스텀 테마 APK 를 만든다.
 *
 * @param {ArrayBuffer} template 템플릿 APK
 * @param {ArrayBuffer} bubble 말풍선 쪽 테마 APK
 * @param {ArrayBuffer} bg 배경 쪽 테마 APK
 * @param {object} opt `{name, filler, marks, colors, key}`
 * @returns {Promise<Uint8Array>} 서명까지 끝난 APK
 */
export async function mixApk(template, bubble, bg, opt) {
  const tpl = readZip(template), bub = readZip(bubble), back = readZip(bg);
  const items = [];
  for (const [name, rec] of tpl) {
    let src = rec;
    if (name.startsWith(DIR)) {
      // 그림은 전부 두 테마에서 온다. 템플릿 것은 자리만 잡아 둔 것이다
      const from = BG_FILES.includes(name) ? back : bub;
      if (from.has(name)) src = from.get(name);
    }
    if (name === ARSC) {
      const arsc = rec.data.slice();          // 템플릿 것을 고쳐 쓴다
      if (opt.marks) patchColors(arsc, opt.marks, opt.colors);
      if (opt.filler) patchName(arsc, opt.filler, opt.name);
      src = { method: 0, crc: 0, csize: arsc.length, usize: arsc.length, data: arsc };
    }
    items.push({
      name, method: src.method, crc: src.crc,
      csize: src.csize, usize: src.usize, data: src.data,
    });
  }
  // arsc 만 우리가 새로 담은 것이라 CRC 를 다시 센다. 나머지는 압축된 채로 옮겨
  // 원래 값을 그대로 쓴다
  for (const it of items) if (it.name === ARSC) it.crc = crc32(it.data);

  return resign(writeZip(items, ALIGN), opt.key);
}
