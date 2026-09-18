// SPDX-License-Identifier: Apache-2.0
//
// docs/apkmix.js 가 만든 안드로이드 커스텀 테마가 제대로 된 APK 인지 본다.
//
//     node tools/check-apkmix.mjs [말풍선테마] [배경테마]
//     node tools/check-apkmix.mjs --install        # 에뮬레이터에 실제로 깔아 본다
//
// 브라우저에서만 도는 코드라 눈으로 확인할 수 없고, 헤더 자리를 한 칸만 틀려도
// 「앱을 설치할 수 없음」 한 줄만 나온다. 그래서 안드로이드 SDK 의 apksigner 로
// 검증하고, --install 이면 에뮬레이터(AVD `spamtest`)에 깔아 본다 — 안드로이드 폰이
// 없어도 여기까지 판정된다.
import { execFileSync, spawn } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { readZip } from '../docs/zip.js';
import { mixApk, BG_FILES } from '../docs/apkmix.js';
import * as key from '../docs/customkey.js';

const MIN_SDK = 24;
const AVD = 'spamtest';
const install = process.argv.includes('--install');
const args = process.argv.slice(2).filter((a) => !a.startsWith('--'));
const BUB = args[0] || 'acrylic-dark-image';
const BG = args[1] || 'camp-dark-image';

function sdk() {
  return process.env.ANDROID_SDK_ROOT || process.env.ANDROID_HOME
    || join(process.env.LOCALAPPDATA || '', 'Android', 'Sdk');
}
function tool(dir, name) {
  const at = join(sdk(), dir);
  if (dir !== 'build-tools') return join(at, name);
  return join(at, readdirSync(at).sort().pop(), name);
}
// node 20 부터 .bat 은 shell 을 거쳐야 뜬다
function run(exe, argv) {
  return execFileSync(`"${exe}"`, argv.map((a) => `"${a}"`), { encoding: 'utf8', shell: true });
}

function apk(slug) {
  const p = join('dist', 'android', `${slug}.apk`);
  if (!existsSync(p)) {
    console.log(`건너뜀: ${p} 가 없다. build.ps1 을 먼저 돌린다.`);
    process.exit(0);
  }
  const b = readFileSync(p);
  return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);
}

// 템플릿이 아직 없으면 말풍선 쪽 APK 를 바탕으로 쓴다. 색과 이름은 못 고치지만
// zip 을 다시 쓰고 정렬을 맞추고 서명하는 길은 그대로 지난다
const tplPath = join('dist', 'android', 'custom-template.apk');
const hasTpl = existsSync(tplPath);
const template = hasTpl
  ? (() => { const b = readFileSync(tplPath); return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength); })()
  : apk(BUB);
if (!hasTpl) console.log('(템플릿이 없어 말풍선 쪽 APK 를 바탕으로 쓴다 — 색·이름 검사는 건너뜀)');

const bub = apk(BUB), bg = apk(BG);
const out = Buffer.from(await mixApk(template, bub, bg, {
  key: { cert: key.CERT, pubkey: key.PUBKEY, privkey: key.PRIVKEY },
}));

const dir = join(tmpdir(), 'apkmix-check');
mkdirSync(dir, { recursive: true });
const dst = join(dir, 'custom.apk');
writeFileSync(dst, out);
console.log(`${BUB} + ${BG} -> ${(out.length / 1024).toFixed(0)}KB`);

let bad = 0;
const fail = (m) => { console.log(`  틀림: ${m}`); bad++; };

const back = readZip(out.buffer.slice(out.byteOffset, out.byteOffset + out.byteLength));
const tz = readZip(template), bz = readZip(bub), gz = readZip(bg);

// 1. 엔트리가 하나도 빠지지 않았다 (옛 서명 META-INF 는 뺀다)
const want = [...tz.keys()].filter((n) => !n.startsWith('META-INF/')).length;
if (back.size !== want) fail(`엔트리 수 ${back.size} != ${want}`);

// 2. 배경 석 장은 배경 쪽 테마에서 왔다
for (const n of BG_FILES) {
  if (!back.has(n)) { fail(`${n} 이 없다`); continue; }
  if (back.get(n).crc !== gz.get(n).crc) fail(`${n} 이 배경 테마 것이 아니다`);
}

// 3. 나머지 그림은 말풍선 쪽 테마 그대로다
for (const [n, rec] of bz) {
  if (!n.startsWith('res/') || BG_FILES.includes(n)) continue;
  if (back.has(n) && back.get(n).crc !== rec.crc) fail(`${n} 이 말풍선 테마 것이 아니다`);
}

// 4. resources.arsc 는 압축 없이 4바이트 정렬이다. 안드로이드 11 부터 이게 아니면
//    설치가 거부된다 — zipalign 이 하던 일을 writeZip 의 align 이 한다
const arsc = execFileSync('python', ['-c',
  'import sys,zipfile,struct\nz=zipfile.ZipFile(sys.argv[1]);i=z.getinfo("resources.arsc")\n'
  + 'f=z.fp;f.seek(i.header_offset+26);m,n=struct.unpack("<HH",f.read(4))\n'
  + 'print(i.compress_type,(i.header_offset+30+m+n)%4)', dst], { encoding: 'utf8' }).trim();
if (arsc !== '0 0') fail(`resources.arsc 가 압축됐거나 정렬이 깨졌다: ${arsc}`);

// 5. 안드로이드가 쓰는 그 도구로 서명을 검증한다. 거부하면 0 이 아닌 값으로 끝난다
try {
  run(tool('build-tools', 'apksigner.bat'),
    ['verify', '--min-sdk-version', String(MIN_SDK), dst]);
} catch (e) {
  fail(`apksigner 가 거부했다: ${String(e.stdout || e.message).split('\n')[0]}`);
}

if (bad) { console.log(`점검 실패 — ${bad}개`); process.exit(1); }
console.log(`점검 통과 — 엔트리 ${back.size}개, arsc 정렬 맞음, v2 서명 유효`);

if (install) {
  const adb = tool('platform-tools', 'adb.exe');
  const devices = run(adb, ['devices']);
  if (!/emulator-\d+\s+device/.test(devices)) {
    console.log(`에뮬레이터 ${AVD} 를 띄운다 (콜드 부팅이라 1~2분)`);
    // 에뮬레이터는 안 끝나는 프로세스다. execFileSync 로 부르면 여기서 영영 기다린다
    spawn(tool('emulator', 'emulator.exe'),
      ['-avd', AVD, '-no-window', '-no-audio', '-no-snapshot', '-no-boot-anim'],
      { detached: true, stdio: 'ignore' }).unref();
  }
  run(adb, ['wait-for-device']);
  for (let i = 0; i < 60; i++) {
    if (run(adb, ['shell', 'getprop', 'sys.boot_completed']).trim() === '1') break;
    execFileSync('python', ['-c', 'import time;time.sleep(3)']);
  }
  const rel = run(adb, ['shell', 'getprop', 'ro.build.version.release']).trim();
  const res = run(adb, ['install', '-r', dst]);
  console.log(`안드로이드 ${rel}: ${res.trim().split('\n').pop()}`);
  if (!/Success/.test(res)) { console.log('설치 실패'); process.exit(1); }
  const on = run(adb, ['shell', 'pm', 'list', 'packages']).split('\n')
    .map((l) => l.trim().replace('package:', ''))
    .filter((l) => l.startsWith('com.kakao.talk.theme'));
  if (!on.length) fail('깔렸다는데 패키지 목록에 없다');
  console.log(`  깔린 테마: ${on.join(' ')}`);
  for (const p of on) run(adb, ['uninstall', p]);
  run(adb, ['emu', 'kill']);
  console.log('설치 확인 끝 — 지우고 에뮬레이터 닫음');
}
