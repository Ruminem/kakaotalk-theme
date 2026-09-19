// docs/install.html 의 갈래를 브라우저 없이 돌려 본다. `node tools/check-install.mjs`
//
// 이 페이지는 README 와 카테고리 문서의 Android 링크가 전부 지나는 자리다. 갈래가 넷이고
// (카톡 인앱 · 보통 안드로이드 · 안내만 · 안드로이드 아님) 파일 이름을 정규식으로 거르므로,
// 한 군데만 틀려도 292벌의 받기 링크가 통째로 릴리스 목록으로 튕긴다. 폰에 넣기 전까지
// 모르는 종류라 여기서 본다.
//
// 페이지의 <script> 를 잘라 와서 그대로 돌린다 — 베껴 두면 두 벌이 되어 한쪽만 고쳐진다.
// check-make.mjs 가 make.html 을 같은 방식으로 본다.
//
// 둘째 인자로 다른 파일을 주면 그것을 본다. 일부러 깨뜨린 사본으로 이 검사가 실제로
// 걸리는지 확인할 때 쓴다.
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const target = process.argv[2] || new URL('../docs/install.html', import.meta.url);
const html = readFileSync(target, 'utf8');
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error('install.html 에서 script 를 못 찾음'); process.exit(1); }
const code = m[1];

// 페이지가 쓰는 만큼만 흉내 낸다. 진짜 DOM 이 필요해지면 그때 늘린다.
function run({ ua, search, href }) {
  const nodes = new Map();
  const mk = (id) => ({
    id, innerHTML: '', textContent: '', checked: false,
    classList: {
      _s: new Set(),
      add(c) { this._s.add(c); }, remove(c) { this._s.delete(c); },
      toggle(c, on) { on ? this._s.add(c) : this._s.delete(c); },
      contains(c) { return this._s.has(c); },
    },
    addEventListener() {}, scrollIntoView() {},
  });
  const app = mk('app');
  let replaced = null;
  const store = {};
  const sandbox = {
    document: {
      getElementById(id) {
        if (id === 'app') return app;
        // 그린 뒤에 찾는 것들. 그 id 가 실제로 그려졌을 때만 있는 것으로 친다.
        if (!app.innerHTML.includes('id="' + id + '"')) return null;
        if (!nodes.has(id)) nodes.set(id, mk(id));
        return nodes.get(id);
      },
    },
    navigator: { userAgent: ua, clipboard: null },
    location: { search, href, replace(u) { replaced = u; } },
    localStorage: {
      getItem: (k) => (k in store ? store[k] : null),
      setItem: (k, v) => { store[k] = String(v); },
    },
    URLSearchParams, URL, console,
  };
  sandbox.window = sandbox;
  try { vm.runInNewContext(code, sandbox); } catch (e) { return { error: e.message, html: '' }; }
  return { html: app.innerHTML, replaced };
}

const AND = 'Mozilla/5.0 (Linux; Android 14; SM-S928N) AppleWebKit/537.36 Chrome/131 Mobile Safari/537.36';
const KAKAO = 'Mozilla/5.0 (Linux; Android 14; SM-S928N; wv) AppleWebKit/537.36 Chrome/131 Mobile Safari/537.36 KAKAOTALK';
const PC = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131 Safari/537.36';
const PAGE = 'https://ruminem.github.io/kakaotalk-theme/docs/install.html';
const LATEST = 'https://github.com/Ruminem/kakaotalk-theme/releases/latest';

let fail = 0;
function ok(name, cond, extra) {
  console.log((cond ? '  OK   ' : '  FAIL ') + name);
  if (!cond) { fail++; console.log('         <- ' + String(extra).slice(0, 160)); }
}

console.log('1) 카톡 인앱 — .apk 를 못 받으므로 밖으로 내보낸다');
{
  const r = run({ ua: KAKAO, search: '?f=neonsign-a.apk', href: PAGE + '?f=neonsign-a.apk' });
  ok('다른 브라우저로 안내', /다른 브라우저로 열어야 함/.test(r.html), r.html);
  ok('받기 단추를 안 준다', !/id="get"/.test(r.html), r.html);
  ok('튕겨내지는 않는다', !r.replaced, r.replaced);
}

console.log('2) 보통 안드로이드 + ?f=');
{
  const r = run({ ua: AND, search: '?f=neonsign-a.apk', href: PAGE + '?f=neonsign-a.apk' });
  ok('두 단계가 다 나온다',
     /보안 위험 자동 차단 끄기/.test(r.html) && /출처를 알 수 없는 앱 허용/.test(r.html), r.html);
  ok('받기 단추가 잠겨 있다', /id="get"/.test(r.html) && /btn primary off/.test(r.html), r.html);
  ok('릴리스 자산을 가리킨다',
     r.html.includes('releases/latest/download/neonsign-a.apk'), r.html);
  ok('삼성 기기를 알아본다', /내 폰이 삼성/.test(r.html), r.html);
  ok('되돌리기 안내는 처음엔 접혀 있다', /class="back hide"/.test(r.html), r.html);
  ok('미리보기 그림이 붙는다', /preview-neonsign-a-chat\.webp/.test(r.html), r.html);
}

console.log('3) 안내만 — make.html 이 ?f= 없이 보낸다');
{
  const r = run({ ua: AND, search: '', href: PAGE });
  ok('단계는 나온다', /보안 위험 자동 차단 끄기/.test(r.html), r.html);
  ok('받을 것이 없으니 단추도 없다', !/id="get"/.test(r.html), r.html);
  ok('건너뛸 것이 없으니 체크박스도 없다', !/id="gate"/.test(r.html), r.html);
  ok('되돌리기 안내가 처음부터 펼쳐진다', /class="back"/.test(r.html), r.html);
  ok('그림과 파일 이름은 없다', !/class="shot"/.test(r.html), r.html);
}

console.log('4) 지어낸 파일 이름은 받지 않는다');
for (const bad of ['?f=City_Glow.apk', '?f=../evil.apk', '?f=x.ktheme', '?f=%2Fetc%2Fpasswd']) {
  const r = run({ ua: AND, search: bad, href: PAGE + bad });
  ok(bad + ' → 릴리스 목록으로', r.replaced === LATEST, r.replaced);
}

console.log('5) 안드로이드가 아니면 안내할 것이 없다');
{
  const r = run({ ua: PC, search: '?f=neonsign-a.apk', href: PAGE + '?f=neonsign-a.apk' });
  ok('파일로 바로 보낸다', /releases\/latest\/download\/neonsign-a\.apk$/.test(r.replaced || ''), r.replaced);
}

console.log(fail ? '\n실패 ' + fail + '건' : '\n전부 통과');
process.exit(fail ? 1 : 0);
