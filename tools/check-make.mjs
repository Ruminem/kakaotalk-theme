// docs/make.html 의 zip 읽기·쓰기·섞기가 제대로 도는지 본다.
//
//   node tools/check-make.mjs
//
// 브라우저에서만 도는 코드라 눈으로 확인하기 어렵다. 헤더 자리를 한 칸만 틀려도
// 폰에 넣기 전까지 모른다 — .ktheme 는 zip 이고, 카톡은 못 읽으면 조용히 무시한다.
// 그래서 실제 dist/iOS 의 테마 두 벌로 섞어 보고, 나온 zip 을 다시 읽어 확인한다.
//
// 페이지에서 쓰는 코드를 그대로 떼어 온다. 베껴 두면 두 벌이 되어 한쪽만 고쳐진다.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const html = fs.readFileSync(path.join(ROOT, 'docs', 'make.html'), 'utf8');

// 코드 조각은 페이지의 구역 주석 사이에서 잘라 온다
function section(from, to) {
  const a = html.indexOf(from), b = html.indexOf(to);
  if (a < 0 || b < 0 || b < a) throw new Error(`make.html 에서 "${from}" 구역을 못 찾음`);
  return html.slice(a, b);
}
// 페이지는 DOM 과 themes.json 을 쓴다. 여기서 보려는 것은 zip 과 색 계산뿐이라 그 둘만 채운다
const PRELUDE = `
var BG_NAMES = ['chatroomBgImage', 'mainBgImage', 'passcodeBgImage'];
var ROW = { send: '#FF3FA4', recv: '#35E0FF' };
function find() { return ROW; }
`;
const code = PRELUDE +
             section('function u16(', '// --- 테마 받아두기') +
             section('function idOf(', '// --- 미리보기');

const ROW_SEND = '#FF3FA4', ROW_RECV = '#35E0FF';
const pick = { bg: 'x-bg', bubble: 'x-bub', send: null, recv: null };
const { readZip, writeZip, crc32, mix, recolorCss, hexHsv } = new Function(
  'pick', code + '\nreturn { readZip, writeZip, crc32, mix, inflate, recolorCss, colorMap, hexHsv };')(pick);

function readTheme(slug) {
  const p = path.join(ROOT, 'dist', 'iOS', slug + '.ktheme');
  if (!fs.existsSync(p)) {
    console.log('건너뜀: dist/iOS 에 테마가 없다. build.ps1 을 먼저 돌린다.');
    process.exit(0);
  }
  const b = fs.readFileSync(p);
  return readZip(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength));
}

const BUB = 'bakery-light-image', BG = 'camp-dark-image';
const bub = readTheme(BUB), bg = readTheme(BG);

const blob = await mix(bub, bg, '점검용 테마');
const out = new Uint8Array(await blob.arrayBuffer());
const back = readZip(out.buffer);

let bad = 0;
const fail = (m) => { console.log('  틀림: ' + m); bad++; };

// 1. 엔트리가 하나도 빠지지 않았다
if (back.size !== bub.size) fail(`엔트리 수 ${back.size} != ${bub.size}`);

// 2. 배경 여섯 장은 배경 쪽 테마에서 왔다
for (const n of ['chatroomBgImage', 'mainBgImage', 'passcodeBgImage']) {
  for (const x of ['@2x', '@3x']) {
    const k = `Images/${n}${x}.png`;
    if (back.get(k).crc !== bg.get(k).crc) fail(`${k} 가 배경 테마 것이 아니다`);
    if (back.get(k).crc === bub.get(k).crc) fail(`${k} 가 안 바뀌었다`);
  }
}

// 3. 나머지는 말풍선 쪽 테마 그대로다
for (const [k, rec] of bub) {
  if (k.includes('BgImage') || k === 'KakaoTalkTheme.css') continue;
  if (back.get(k).crc !== rec.crc) fail(`${k} 가 달라졌다`);
}

// 4. CSS 는 이름과 ID 두 줄만 바뀌었다
const dec = new TextDecoder();
const before = dec.decode(await inflateOf(bub.get('KakaoTalkTheme.css')));
const after = dec.decode(back.get('KakaoTalkTheme.css').data);   // 저장 방식(method 0)
if (back.get('KakaoTalkTheme.css').method !== 0) fail('CSS 는 압축 없이 담아야 한다');
if (crc32(back.get('KakaoTalkTheme.css').data) !== back.get('KakaoTalkTheme.css').crc) {
  fail('CSS 의 CRC 가 안 맞는다');
}
if (!after.includes("-kakaotalk-theme-name: '점검용 테마'")) fail('테마 이름이 안 들어갔다');
if (!/-kakaotalk-theme-id: 'com\.kakao\.talk\.theme\.custom_x_bub__x_bg'/.test(after)) {
  fail('테마 ID 가 안 바뀌었다');
}
const diff = before.split('\n').filter((l, i) => l !== after.split('\n')[i]);
if (diff.length !== 2) fail(`CSS 에서 ${diff.length} 줄이 달라졌다 (두 줄이어야 한다)`);

async function inflateOf(rec) {
  if (rec.method === 0) return rec.data;
  const s = new Blob([rec.data]).stream().pipeThrough(new DecompressionStream('deflate-raw'));
  return new Uint8Array(await new Response(s).arrayBuffer());
}

// 5. 말풍선 색 바꾸기 — 페이지와 tools/mix.py 가 같은 색을 내야 한다.
// 한쪽에서 만든 테마와 다른 쪽에서 만든 테마가 달라지면 어느 쪽이 맞는지 알 수 없다.
{
  pick.send = '#4D8CFF';
  pick.recv = '#FF6FD8';
  const SRC = ['#FF3FA4', '#35E0FF', '#100C14', '#F2ECF7', '#FFE0F0', '#D9F8FF', '#C42D7E'];
  const mine = SRC.map((c) => recolorCss(c, [
    { h: hexHsv(ROW_SEND)[0], shift: hexHsv(pick.send)[0] - hexHsv(ROW_SEND)[0],
      k: hexHsv(pick.send)[1] / hexHsv(ROW_SEND)[1] },
    { h: hexHsv(ROW_RECV)[0], shift: hexHsv(pick.recv)[0] - hexHsv(ROW_RECV)[0],
      k: hexHsv(pick.recv)[1] / hexHsv(ROW_RECV)[1] },
  ]));
  const py = execFileSync('python', ['-c', `
import sys; sys.path.insert(0, r'${path.join(ROOT, 'tools')}')
import mix
t = dict(send=('${ROW_SEND}','${ROW_SEND}'), recv=('${ROW_RECV}','${ROW_RECV}'))
for k, c in enumerate(${JSON.stringify(SRC)}):
    t['k%d' % k] = c
mix.PALETTE_KEYS = tuple('k%d' % i for i in range(${SRC.length}))
mix.recolor_palette(t, '${pick.send}', '${pick.recv}')
print(' '.join(t['k%d' % i] for i in range(${SRC.length})))
`], { encoding: 'utf8', env: { ...process.env, PYTHONUTF8: '1' } }).trim().split(' ');
  mine.forEach((v, i) => {
    if (v.toUpperCase() !== py[i].toUpperCase()) {
      fail(`${SRC[i]} -> 페이지 ${v}, mix.py ${py[i]}`);
    }
  });
  console.log(`  색 ${SRC.length}개를 mix.py 와 대조: ${SRC.map((c, i) => c + '->' + mine[i]).join(' ')}`);
  pick.send = pick.recv = null;
}

fs.mkdirSync(path.join(ROOT, 'build-tmp'), { recursive: true });
fs.writeFileSync(path.join(ROOT, 'build-tmp', 'check-make.ktheme'), out);
console.log(bad ? `점검 실패 ${bad}건` : `점검 통과 — ${back.size}개 엔트리, ${(out.length / 1024).toFixed(0)}KB`);
process.exit(bad ? 1 : 0);
