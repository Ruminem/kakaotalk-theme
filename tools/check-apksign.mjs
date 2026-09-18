// SPDX-License-Identifier: Apache-2.0
//
// docs/apksign.js 가 붙인 v2 서명을 안드로이드 SDK 의 apksigner 로 검증한다.
// 폰 없이 여기까지는 판정할 수 있다 — apksigner 가 통과시키면 안드로이드도 통과시킨다.
//
//     node tools/check-apksign.mjs [테마이름]
//
// v2 만 붙이므로 minSdk 24 로 잰다. 안드로이드 6 이하(API 21~23)는 v2 를 모르고
// 옛 v1(JAR) 서명을 찾는데, 그건 PKCS#7 이라 브라우저에서 만들 것이 못 된다.
// 커스텀 테마 쪽 매니페스트만 minSdkVersion 을 24 로 올려서 쓴다.
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { resign } from '../docs/apksign.js';
import * as key from '../docs/customkey.js';

const MIN_SDK = 24;

function apksigner() {
  const sdk = process.env.ANDROID_SDK_ROOT || process.env.ANDROID_HOME
    || join(process.env.LOCALAPPDATA || '', 'Android', 'Sdk');
  const bt = join(sdk, 'build-tools');
  if (!existsSync(bt)) throw new Error(`안드로이드 SDK 를 못 찾았다: ${bt}`);
  const ver = readdirSync(bt).sort().pop();
  return join(bt, ver, 'apksigner.bat');
}

const name = process.argv[2] || readdirSync('dist/android').find((f) => f.endsWith('.apk'));
if (!name) throw new Error('dist/android 에 APK 가 없다. build.ps1 을 먼저 돌린다');
const src = join('dist/android', name.endsWith('.apk') ? name : `${name}.apk`);

const before = readFileSync(src);
const after = Buffer.from(await resign(new Uint8Array(before), {
  cert: key.CERT, pubkey: key.PUBKEY, privkey: key.PRIVKEY,
}));

const out = join(tmpdir(), 'apksign-check');
mkdirSync(out, { recursive: true });
const dst = join(out, 'resigned.apk');
writeFileSync(dst, after);
console.log(`${src} ${before.length} 바이트 -> ${after.length} 바이트`);

// 1. 엔트리 자리가 안 움직였는지. 움직이면 resources.arsc 4바이트 정렬이 깨져
//    안드로이드 11 이상이 설치를 거부한다
const head = before.subarray(0, 4096);
if (!after.subarray(0, 4096).equals(head)) throw new Error('엔트리 구역이 움직였다');

// 2. zip 으로 열리는지, META-INF(옛 v1 서명)가 빠졌는지
const names = execFileSync('python', ['-c',
  'import sys,zipfile;print("\\n".join(zipfile.ZipFile(sys.argv[1]).namelist()))', dst],
{ encoding: 'utf8' }).trim().split('\n');
if (names.some((n) => n.startsWith('META-INF/'))) throw new Error('META-INF 가 남아 있다');
console.log(`  엔트리 ${names.length}개, META-INF 없음`);

// 3. resources.arsc 가 압축 없이 4바이트 정렬인지
const arsc = execFileSync('python', ['-c',
  'import sys,zipfile\nz=zipfile.ZipFile(sys.argv[1]);i=z.getinfo("resources.arsc")\n'
  + 'f=z.fp;f.seek(i.header_offset+28);import struct\n'
  + 'n,=struct.unpack("<H",f.read(2));f.seek(i.header_offset+26);m,=struct.unpack("<H",f.read(2))\n'
  + 'print(i.compress_type,(i.header_offset+30+m+n)%4)', dst], { encoding: 'utf8' }).trim();
if (arsc !== '0 0') throw new Error(`resources.arsc 가 압축됐거나 정렬이 깨졌다: ${arsc}`);
console.log('  resources.arsc 압축 없음 · 4바이트 정렬');

// 4. 안드로이드가 쓰는 그 도구로 검증
// node 20 부터 .bat 은 shell 을 거쳐야 뜬다. 자리 표시가 아니라 따옴표로 묶어 넘긴다
const v = execFileSync(`"${apksigner()}"`, ['verify', '--min-sdk-version', String(MIN_SDK),
  '--print-certs', '-v', `"${dst}"`], { encoding: 'utf8', shell: true });
console.log(v.split('\n').filter((l) => l.trim()).slice(0, 6).map((l) => `  ${l}`).join('\n'));
if (!/Verified using v2 scheme \(APK Signature Scheme v2\): true/.test(v)) {
  throw new Error('v2 서명 검증 실패');
}
console.log(`점검 통과 — minSdk ${MIN_SDK} 이상에서 깔린다`);
