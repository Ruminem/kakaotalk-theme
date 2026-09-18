// SPDX-License-Identifier: Apache-2.0
//
// APK 에 v2 서명을 붙인다. 브라우저와 node 양쪽에서 돈다(WebCrypto 만 쓴다).
//
// 왜 필요한가: 안드로이드 테마는 설치되는 앱이라 서명이 있어야 하고, 매니페스트가
// targetSdkVersion 34 라 옛 v1(JAR) 서명만으로는 안드로이드 11 이상이 거부한다.
// 브라우저에서 커스텀 테마를 만들려면 여기서 다시 서명해야 한다.
//
// v2 서명이 무엇인가: zip 엔트리 구역 · 중앙 디렉터리 · EOCD 를 1MB 씩 끊어 해시하고,
// 그 해시들을 다시 해시한 값에 서명해서, 엔트리와 중앙 디렉터리 사이에 APK Signing
// Block 을 끼워 넣는 것이다. 엔트리는 자리가 그대로라 정렬(zipalign)이 깨지지 않는다 —
// 안드로이드 11 부터 resources.arsc 는 압축 없이 4바이트 정렬이어야 설치된다.
//
// 규격: https://source.android.com/docs/security/features/apksigning/v2
// 고치면 `node tools/check-apksign.mjs` 를 돌린다 — 실제 APK 에 붙여 보고
// 안드로이드 SDK 의 apksigner 로 검증한다.

const CHUNK = 1048576;
const MAGIC = 'APK Sig Block 42';
const V2_ID = 0x7109871a;
// RSASSA-PKCS1-v1_5 + SHA2-256. 내용 해시도 SHA-256 이다
const ALG_RSA_SHA256 = 0x0103;

function cat(parts) {
  let n = 0;
  for (const p of parts) n += p.length;
  const out = new Uint8Array(n);
  let at = 0;
  for (const p of parts) { out.set(p, at); at += p.length; }
  return out;
}

function u32(v) {
  const a = new Uint8Array(4);
  new DataView(a.buffer).setUint32(0, v, true);
  return a;
}

function u64(v) {
  const a = new Uint8Array(8);
  new DataView(a.buffer).setBigUint64(0, BigInt(v), true);
  return a;
}

// uint32 길이를 앞에 붙인다. v2 규격의 거의 모든 자리가 이 꼴이다
function lp(...parts) {
  const body = cat(parts);
  return cat([u32(body.length), body]);
}

function b64(s) {
  const bin = typeof atob === 'function'
    ? atob(s) : Buffer.from(s, 'base64').toString('binary');
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function ascii(u8, at, n) {
  let s = '';
  for (let i = 0; i < n; i++) s += String.fromCharCode(u8[at + i]);
  return s;
}

// --- zip 뜯기 ---------------------------------------------------------------

/** EOCD 자리를 찾는다. 뒤에서부터 시그니처를 훑는다 */
function findEocd(u8) {
  for (let i = u8.length - 22; i >= 0 && i > u8.length - 65558; i--) {
    if (u8[i] === 0x50 && u8[i + 1] === 0x4b && u8[i + 2] === 0x05 && u8[i + 3] === 0x06) return i;
  }
  throw new Error('zip 이 아니다 (EOCD 없음)');
}

/**
 * 중앙 디렉터리에서 META-INF/ 엔트리를 뺀 것을 새로 만든다.
 * 엔트리 데이터는 건드리지 않는다 — 자리가 움직이면 정렬이 깨진다. 빠진 엔트리의
 * 데이터는 죽은 바이트로 남고, 목록에 없으니 안드로이드는 못 본다.
 * 옛 v1 서명을 이렇게 떼어 낸다.
 */
function stripMetaInf(u8, cdAt, cdSize) {
  const keep = [];
  let at = cdAt, n = 0;
  const end = cdAt + cdSize;
  while (at < end) {
    const dv = new DataView(u8.buffer, u8.byteOffset + at);
    if (dv.getUint32(0, true) !== 0x02014b50) throw new Error('중앙 디렉터리가 깨졌다');
    const nameLen = dv.getUint16(28, true);
    const extraLen = dv.getUint16(30, true);
    const cmtLen = dv.getUint16(32, true);
    const size = 46 + nameLen + extraLen + cmtLen;
    const name = ascii(u8, at + 46, nameLen);
    if (!name.startsWith('META-INF/')) { keep.push(u8.subarray(at, at + size)); n++; }
    at += size;
  }
  return { cd: cat(keep), count: n };
}

// --- 해시 -------------------------------------------------------------------

/** 1MB 씩 끊어 해시하고 그 해시들을 다시 해시한다 */
async function chunkedSha256(parts) {
  const digests = [];
  let n = 0;
  for (const p of parts) {
    for (let off = 0; off < p.length; off += CHUNK) {
      const c = p.subarray(off, Math.min(off + CHUNK, p.length));
      const head = new Uint8Array(5);
      head[0] = 0xa5;
      new DataView(head.buffer).setUint32(1, c.length, true);
      digests.push(new Uint8Array(await crypto.subtle.digest('SHA-256', cat([head, c]))));
      n++;
    }
  }
  const head = new Uint8Array(5);
  head[0] = 0x5a;
  new DataView(head.buffer).setUint32(1, n, true);
  return new Uint8Array(await crypto.subtle.digest('SHA-256', cat([head, ...digests])));
}

// --- 서명 -------------------------------------------------------------------

/**
 * APK 바이트에 v2 서명을 붙여 돌려준다. 이미 있던 서명 블록과 META-INF 는 뗀다.
 *
 * @param {Uint8Array} apk
 * @param {{cert: string, pubkey: string, privkey: string}} key base64 DER 세 벌
 */
export async function resign(apk, key) {
  const eocdAt = findEocd(apk);
  const eocd = new DataView(apk.buffer, apk.byteOffset + eocdAt);
  let cdAt = eocd.getUint32(16, true);
  const cdSize = eocd.getUint32(12, true);

  // 이미 붙어 있는 서명 블록을 뗀다. 블록은 중앙 디렉터리 바로 앞에서 끝나고
  // [크기(8)][내용][크기(8)][매직(16)] 꼴이다
  let entriesEnd = cdAt;
  if (cdAt >= 24 && ascii(apk, cdAt - 16, 16) === MAGIC) {
    const size2 = new DataView(apk.buffer, apk.byteOffset + cdAt - 24).getBigUint64(0, true);
    entriesEnd = cdAt - (Number(size2) + 8);
  }

  const entries = apk.subarray(0, entriesEnd);
  const { cd, count } = stripMetaInf(apk, cdAt, cdSize);

  // EOCD 는 서명 뒤의 모습으로 만들되, 중앙 디렉터리 위치만은 '서명 블록이 시작하는
  // 자리' 를 담아야 한다. 규격이 그렇게 정했다 — 검증할 때 블록 앞이 곧 그 값이다
  const tail = apk.subarray(eocdAt, apk.length).slice();
  const tv = new DataView(tail.buffer, tail.byteOffset);
  tv.setUint16(8, count, true);
  tv.setUint16(10, count, true);
  tv.setUint32(12, cd.length, true);
  tv.setUint32(16, entriesEnd, true);

  const digest = await chunkedSha256([entries, cd, tail]);

  const cert = b64(key.cert);
  const signedData = cat([
    lp(lp(u32(ALG_RSA_SHA256), lp(digest))),  // 해시 목록
    lp(lp(cert)),                              // 인증서 목록
    lp(),                                      // 딸린 속성 없음
  ]);
  const priv = await crypto.subtle.importKey(
    'pkcs8', b64(key.privkey),
    { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['sign']);
  const sig = new Uint8Array(await crypto.subtle.sign('RSASSA-PKCS1-v1_5', priv, signedData));

  const signer = cat([
    lp(signedData),
    lp(lp(u32(ALG_RSA_SHA256), lp(sig))),
    lp(b64(key.pubkey)),
  ]);
  const value = lp(lp(signer));                // 서명자 목록
  const pair = cat([u64(4 + value.length), u32(V2_ID), value]);
  const size = pair.length + 24;               // 뒤 크기(8) + 매직(16) 포함
  const block = cat([u64(size), pair, u64(size),
    Uint8Array.from(MAGIC, (c) => c.charCodeAt(0))]);

  // 이제 진짜 자리로 고친다
  tv.setUint32(16, entriesEnd + block.length, true);
  return cat([entries, block, cd, tail]);
}

export const _test = { findEocd, stripMetaInf, chunkedSha256 };
