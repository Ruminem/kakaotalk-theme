// SPDX-License-Identifier: Apache-2.0
//
// zip 을 손으로 읽고 쓴다. `.ktheme`(아이폰)과 `.apk`(안드로이드)가 둘 다 zip 이라
// 커스텀 테마 제작은 전부 이 파일을 거친다. 라이브러리를 들이지 않는다 — 필요한 것은
// 바이트 몇 덩어리뿐이고, 그림은 압축을 풀지도 않고 압축된 채로 옮겨 담는다.
//
// 헤더 자리를 한 칸만 틀려도 폰에 넣기 전까지 모른다. 고치면 두 점검을 돌린다 —
// `node tools/check-make.mjs`(아이폰)와 `node tools/check-apkmix.mjs`(안드로이드).

export function u16(d, o) { return d[o] | d[o + 1] << 8; }
export function u32(d, o) {
  return (d[o] | d[o + 1] << 8 | d[o + 2] << 16 | d[o + 3] << 24) >>> 0;
}

const CRCT = (function () {
  const t = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ c >>> 1 : c >>> 1;
    t[i] = c >>> 0;
  }
  return t;
})();

export function crc32(b) {
  let c = 0xFFFFFFFF;
  for (let i = 0; i < b.length; i++) c = CRCT[(c ^ b[i]) & 255] ^ c >>> 8;
  return (c ^ 0xFFFFFFFF) >>> 0;
}

/**
 * 엔트리 하나의 압축을 푼다. 그림은 풀 일이 없고 CSS 를 고칠 때만 쓴다.
 * `DecompressionStream` 은 iOS 16.4 부터 있다 — 페이지가 그걸로 옛 브라우저를 가린다.
 */
export function inflate(rec) {
  if (rec.method === 0) return Promise.resolve(rec.data);
  const s = new Blob([rec.data]).stream()
    .pipeThrough(new DecompressionStream('deflate-raw'));
  return new Response(s).arrayBuffer().then((b) => new Uint8Array(b));
}

/** zip 바이트 -> Map(이름 -> {method, crc, csize, usize, data}). data 는 압축된 그대로다 */
export function readZip(buf) {
  const d = new Uint8Array(buf);
  let e = d.length - 22;
  while (e >= 0 && u32(d, e) !== 0x06054b50) e--;
  if (e < 0) throw new Error('zip 이 아님');
  const n = u16(d, e + 10), out = new Map(), dec = new TextDecoder();
  let p = u32(d, e + 16);
  for (let i = 0; i < n; i++) {
    const nl = u16(d, p + 28), el = u16(d, p + 30), cl = u16(d, p + 32);
    const name = dec.decode(d.subarray(p + 46, p + 46 + nl));
    const off = u32(d, p + 42);
    const lnl = u16(d, off + 26), lel = u16(d, off + 28), at = off + 30 + lnl + lel;
    const rec = {
      method: u16(d, p + 10), crc: u32(d, p + 16),
      csize: u32(d, p + 20), usize: u32(d, p + 24),
    };
    rec.data = d.subarray(at, at + rec.csize);
    out.set(name, rec);
    p += 46 + nl + el + cl;
  }
  return out;
}

/**
 * 엔트리 목록 -> zip 바이트.
 *
 * `align` 을 주면 압축 없이 담는 엔트리(method 0)의 데이터가 그 배수에서 시작하도록
 * 지역 헤더의 extra 자리를 채운다. APK 는 이게 필요하다 — 안드로이드 11 부터
 * `resources.arsc` 가 압축 없이 4바이트 정렬이어야 설치된다(zipalign 이 하는 일).
 */
export function writeZip(items, align) {
  const enc = new TextEncoder(), parts = [], cen = [];
  let off = 0, total = 0;
  for (const it of items) {
    const nm = enc.encode(it.name);
    let pad = 0;
    if (align && it.method === 0) {
      pad = (align - (off + 30 + nm.length) % align) % align;
    }
    const lh = new Uint8Array(30 + nm.length + pad), v = new DataView(lh.buffer);
    v.setUint32(0, 0x04034b50, true); v.setUint16(4, 20, true);
    v.setUint16(8, it.method, true); v.setUint16(12, 0x21, true);
    v.setUint32(14, it.crc, true); v.setUint32(18, it.csize, true);
    v.setUint32(22, it.usize, true); v.setUint16(26, nm.length, true);
    v.setUint16(28, pad, true);
    lh.set(nm, 30);
    parts.push(lh, it.data);

    // 중앙 디렉터리에는 채움을 적지 않는다. zipalign 도 지역 헤더에만 넣는다
    const ch = new Uint8Array(46 + nm.length), w = new DataView(ch.buffer);
    w.setUint32(0, 0x02014b50, true); w.setUint16(4, 20, true); w.setUint16(6, 20, true);
    w.setUint16(10, it.method, true); w.setUint16(14, 0x21, true);
    w.setUint32(16, it.crc, true); w.setUint32(20, it.csize, true);
    w.setUint32(24, it.usize, true); w.setUint16(28, nm.length, true);
    w.setUint32(42, off, true);
    ch.set(nm, 46);
    cen.push(ch);
    off += lh.length + it.data.length;
    total += ch.length;
  }
  const end = new Uint8Array(22), ev = new DataView(end.buffer);
  ev.setUint32(0, 0x06054b50, true);
  ev.setUint16(8, items.length, true); ev.setUint16(10, items.length, true);
  ev.setUint32(12, total, true); ev.setUint32(16, off, true);

  const all = parts.concat(cen, [end]);
  let n = 0;
  for (const p of all) n += p.length;
  const out = new Uint8Array(n);
  let at = 0;
  for (const p of all) { out.set(p, at); at += p.length; }
  return out;
}
