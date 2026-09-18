// 실험용. 카톡 인앱 브라우저가 서비스 워커가 만들어 준 .ktheme 를 설치해 주는지 본다.
//
// 브라우저에서 만든 테마는 blob: 주소뿐이라 카톡이 알아보지 못한다. 서비스 워커가
// 진짜 주소처럼 생긴 자리를 가로채 응답하면 카톡이 알아볼지가 궁금한 것이다.
// 갈림길은 하나다 — 카톡이 그 주소를 웹뷰로 받으면 워커를 거치고, 앱이 직접 받으면
// 안 거친다. 안 거치면 사이트에 없는 주소라 404 가 난다.
//
// 결과가 나오면 이 파일과 probe.html 은 지운다. docs/make.html 에 붙이든 안 붙이든.
self.addEventListener('install', function () { self.skipWaiting(); });
self.addEventListener('activate', function (e) { e.waitUntil(self.clients.claim()); });

self.addEventListener('fetch', function (e) {
  var u = new URL(e.request.url);
  // 이 한 자리 말고는 손대지 않는다. 사이트의 다른 요청까지 가로채면 나중에 캐시가
  // 낀 화면을 보게 된다
  if (!/\/custom\/probe\.ktheme$/.test(u.pathname)) return;
  e.respondWith(
    fetch(new URL('../../files/inkmint-basic.ktheme', u).href)
      .then(function (r) { return r.arrayBuffer(); })
      .then(function (b) {
        return new Response(b, { headers: { 'content-type': 'application/octet-stream' } });
      })
  );
});
