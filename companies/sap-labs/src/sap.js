(function () {
  'use strict';
  var KEY = 'sap.v1', H = document.documentElement;
  var st = { done: {}, bm: {}, open: {}, last: null, depth: '2', be: false, im: false, nav: null };
  try { var s = JSON.parse(localStorage.getItem(KEY) || '{}'); for (var k in s) st[k] = s[k]; } catch (e) {}
  function save() { try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {} }
  function $(q, r) { return (r || document).querySelector(q); }
  function $$(q, r) { return Array.prototype.slice.call((r || document).querySelectorAll(q)); }

  /* ---------- top-bar height drives the sidebar offset */
  var top = $('.top'), side = $('#side');
  function fitTop() { side.style.top = top.offsetHeight + 'px'; }
  window.addEventListener('resize', fitTop); fitTop();

  /* ---------- nav drawer */
  var wide = function () { return window.innerWidth >= 1100; };
  function setNav(open, remember) {
    H.classList.toggle('nav-open', open);
    if (remember && wide()) { st.nav = open; save(); }
  }
  setNav(wide() ? st.nav !== false : false);
  $('#navbtn').onclick = function () { setNav(!H.classList.contains('nav-open'), true); };
  $('#backdrop').onclick = function () { setNav(false); };

  /* ---------- modes */
  function applyModes() {
    H.setAttribute('data-depth', st.depth);
    $$('.seg button').forEach(function (b) { b.classList.toggle('on', b.getAttribute('data-d') === st.depth); });
    H.classList.toggle('be', !!st.be); H.classList.toggle('im', !!st.im);
    $('#be').checked = !!st.be; $('#im').checked = !!st.im;
  }
  $$('.seg button').forEach(function (b) { b.onclick = function () { st.depth = b.getAttribute('data-d'); save(); applyModes(); }; });
  $('#be').onchange = function () { st.be = this.checked; save(); applyModes(); };
  $('#im').onchange = function () {
    st.im = this.checked; save(); applyModes();
  };
  applyModes();

  /* ---------- cards: open / done / bookmark */
  var cards = $$('.card');
  function setOpen(c, open) {
    c.classList.toggle('open', open);
    $('.ct', c).setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  cards.forEach(function (c) {
    var id = c.getAttribute('data-card');
    setOpen(c, !!st.open[id]);
    if (st.done[id]) { c.classList.add('done'); $('.dn input', c).checked = true; }
    if (st.bm[id]) { $('.bm', c).classList.add('on'); $('.bm', c).textContent = '★'; }
    $('.ct', c).onclick = function () {
      var o = !c.classList.contains('open'); setOpen(c, o);
      if (o) st.open[id] = 1; else delete st.open[id]; save();
    };
    $('.dn input', c).onchange = function () {
      if (this.checked) st.done[id] = 1; else delete st.done[id];
      c.classList.toggle('done', this.checked); save(); progress();
    };
    $('.bm', c).onclick = function () {
      var on = !st.bm[id]; if (on) st.bm[id] = 1; else delete st.bm[id];
      this.classList.toggle('on', on); this.textContent = on ? '★' : '☆'; save(); bookmarks();
    };
    $$('.tab', c).forEach(function (t) {
      t.onclick = function () {
        var w = t.getAttribute('data-t'), box = t.closest('.ans');
        $$('.tab', box).forEach(function (x) { x.classList.toggle('on', x === t); });
        $$('.tp', box).forEach(function (x) { x.classList.toggle('on', x.getAttribute('data-t') === w); });
      };
    });
  });

  /* ---------- progress */
  function progress() {
    var total = 0, done = 0, per = {};
    cards.forEach(function (c) {
      var s = c.getAttribute('data-sec'), id = c.getAttribute('data-card');
      per[s] = per[s] || [0, 0]; per[s][1]++; total++;
      if (st.done[id]) { per[s][0]++; done++; }
    });
    var pct = total ? Math.round(100 * done / total) : 0;
    $('#pf').style.width = pct + '%'; $('#pt').textContent = pct + '% (' + done + '/' + total + ')';
    $$('[data-np]').forEach(function (n) {
      var p = per[n.getAttribute('data-np')];
      n.textContent = p ? p[0] + '/' + p[1] : '';
      n.style.color = p && p[0] === p[1] ? '' : 'var(--mute)';
    });
  }
  progress();

  /* ---------- bookmarks list */
  function bookmarks() {
    var box = $('#bml'), ids = Object.keys(st.bm);
    if (!ids.length) { box.innerHTML = '<span class="muted">None yet — star a concept.</span>'; return; }
    box.innerHTML = '';
    ids.forEach(function (id) {
      var c = document.querySelector('[data-card="' + id + '"]'); if (!c) return;
      var a = document.createElement('a');
      a.href = '#' + c.getAttribute('data-sec') + '/' + id;
      a.textContent = $('.ct', c).textContent; box.appendChild(a);
    });
  }
  bookmarks();

  /* ---------- routing: #section or #section/card */
  var secs = $$('.sec');
  function route() {
    var h = (location.hash || '').slice(1), parts = h.split('/'), sid = parts[0], cid = parts[1];
    if (!document.getElementById(sid) || !document.getElementById(sid).classList.contains('sec')) {
      sid = st.last && document.getElementById(st.last) ? st.last : secs[0].id;
    }
    secs.forEach(function (s) { s.hidden = s.id !== sid; });
    $$('.nl').forEach(function (a) { a.classList.toggle('on', a.getAttribute('data-sec') === sid); });
    st.last = sid; save();
    document.title = document.getElementById(sid).getAttribute('data-title') + ' — SAP Labs FDE Prep';
    if (!wide()) setNav(false);
    if (cid) {
      var c = document.querySelector('[data-card="' + cid + '"]');
      if (c) { setOpen(c, true); st.open[cid] = 1; save(); c.scrollIntoView({ block: 'start' }); c.classList.add('flash'); setTimeout(function () { c.classList.remove('flash'); }, 1400); return; }
    }
    window.scrollTo(0, 0);
  }
  window.addEventListener('hashchange', route); route();

  /* ---------- question bank filter */
  var qf = $('#qfilter');
  function qfilter() {
    var t = (qf.value || '').toLowerCase(), tiers = {};
    $$('.qf [data-tier]').forEach(function (x) { tiers[x.getAttribute('data-tier')] = x.checked; });
    $$('.qcard').forEach(function (c) {
      var ok = tiers[c.getAttribute('data-tier')] && (!t || c.textContent.toLowerCase().indexOf(t) >= 0);
      c.style.display = ok ? '' : 'none';
    });
  }
  if (qf) { qf.oninput = qfilter; $$('.qf [data-tier]').forEach(function (x) { x.onchange = qfilter; }); }

  /* ---------- search */
  var sr = $('#sr'), sq = $('#sq'), res = $('#sres'), sel = 0, hits = [];
  function norm(s) { return s.toLowerCase(); }
  function stem(w) { return w.replace(/(ing|ed|es|s)$/, ''); }
  function search(q) {
    var toks = norm(q).split(/\s+/).filter(Boolean);
    if (!toks.length) return IDX.filter(function (x) { return x.k === 'Section'; });
    var out = [];
    IDX.forEach(function (x) {
      var hay = norm(x.t + ' ' + x.x), score = 0, ok = true;
      toks.forEach(function (t) {
        var i = hay.indexOf(t); if (i < 0) i = hay.indexOf(stem(t));
        if (i < 0) { ok = false; return; }
        score += norm(x.t).indexOf(t) >= 0 ? 10 : 2; if (i === 0 || /\W/.test(hay[i - 1])) score += 3;
      });
      if (ok) out.push([score + (x.k === 'Concept' ? 2 : 0), x]);
    });
    out.sort(function (a, b) { return b[0] - a[0]; });
    return out.slice(0, 40).map(function (p) { return p[1]; });
  }
  function draw() {
    hits = search(sq.value); sel = Math.min(sel, Math.max(hits.length - 1, 0));
    res.innerHTML = hits.length ? '' : '<div class="muted" style="padding:8px">No matches.</div>';
    hits.forEach(function (x, i) {
      var a = document.createElement('a'); a.className = 'sr' + (i === sel ? ' on' : '');
      a.href = '#' + x.h + (x.c ? '/' + x.c : '');
      a.innerHTML = '<span class="k"></span><span class="t"></span><span class="x2"></span>';
      a.children[0].textContent = x.k; a.children[1].textContent = x.t; a.children[2].textContent = x.x || '';
      a.onclick = function () { closeSearch(); };
      res.appendChild(a);
    });
  }
  function openSearch() { sr.hidden = false; sq.value = ''; sel = 0; draw(); sq.focus(); }
  function closeSearch() { sr.hidden = true; }
  $('#searchbtn').onclick = openSearch;
  sr.onclick = function (e) { if (e.target === sr) closeSearch(); };
  sq.oninput = function () { sel = 0; draw(); };
  sq.onkeydown = function (e) {
    if (e.key === 'ArrowDown') { sel = Math.min(sel + 1, hits.length - 1); draw(); e.preventDefault(); }
    else if (e.key === 'ArrowUp') { sel = Math.max(sel - 1, 0); draw(); e.preventDefault(); }
    else if (e.key === 'Enter' && hits[sel]) { var x = hits[sel]; closeSearch(); location.hash = x.h + (x.c ? '/' + x.c : ''); route(); }
  };

  /* ---------- cheat sheet */
  var ch = $('#cheat');
  $$('[data-open-cheat]').forEach(function (b) { b.onclick = function () { ch.hidden = false; }; });
  $$('[data-close-cheat]').forEach(function (b) { b.onclick = function () { ch.hidden = true; }; });
  ch.onclick = function (e) { if (e.target === ch) ch.hidden = true; };

  /* ---------- keys */
  document.addEventListener('keydown', function (e) {
    var typing = /INPUT|TEXTAREA/.test((document.activeElement || {}).tagName || '');
    if (e.key === 'Escape') { closeSearch(); ch.hidden = true; if (!wide()) setNav(false); return; }
    if ((e.key === 'k' && (e.metaKey || e.ctrlKey)) || (e.key === '/' && !typing)) { e.preventDefault(); openSearch(); }
  });
})();
