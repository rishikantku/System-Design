/* LinkedIn prep workspace — state, progress, practice engine, mock mode.
   No dependencies. State lives in localStorage under lp.v1 and is shared by
   every page in this workspace (dashboard reads what the round pages write). */
(function () {
  'use strict';
  var KEY = 'lp.v1';
  var M = window.LP_MANIFEST || { rounds: {}, research: {} };

  /* ---------------- store ---------------- */
  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; }
  }
  function save(s) {
    try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) { /* private mode */ }
  }
  var S = load();
  S.items = S.items || {};   // id -> {st, cf, note, ts}
  S.mocks = S.mocks || [];   // {round, id, score, ts}
  S.log = S.log || [];       // {ts, round, what}

  var LP = {
    get: function (id) { return S.items[id] || {}; },
    set: function (id, patch) {
      var it = S.items[id] || {};
      for (var k in patch) it[k] = patch[k];
      it.ts = Date.now();
      S.items[id] = it;
      save(S);
      document.dispatchEvent(new CustomEvent('lp:change', { detail: { id: id, item: it } }));
      return it;
    },
    logActivity: function (round, what) {
      S.log.unshift({ ts: Date.now(), round: round, what: what });
      S.log = S.log.slice(0, 60); save(S);
    },
    mocks: function (round) { return S.mocks.filter(function (m) { return !round || m.round === round; }); },
    addMock: function (round, id, score) {
      S.mocks.unshift({ round: round, id: id, score: score, ts: Date.now() }); save(S);
    },
    all: function () { return S; },
    reset: function () { S = { items: {}, mocks: [], log: [] }; save(S); },
    /* round progress: weighted by item weight; solved/confident = full credit */
    stats: function (round) {
      var r = (M.rounds || {})[round];
      if (!r) return { pct: 0, done: 0, total: 0, weak: [], remaining: [] };
      var total = 0, got = 0, done = 0, weak = [], remaining = [];
      r.items.forEach(function (it) {
        var w = it.weight || 1, st = (S.items[it.id] || {}).st, cf = (S.items[it.id] || {}).cf || 0;
        total += w;
        var credit = 0;
        if (st === 'solved' || st === 'done') credit = 1;
        else if (st === 'revise' || st === 'slow' || st === 'hint') credit = 0.5;
        else if (st === 'failed') credit = 0.25;
        if (credit === 1 && cf && cf <= 2) credit = 0.8;   // done but low confidence
        got += w * credit;
        if (credit >= 1) done++;
        else remaining.push(it);
        if (st && credit < 1) weak.push(it);
        else if (cf && cf <= 2) weak.push(it);
      });
      return {
        pct: total ? Math.round(got / total * 100) : 0,
        done: done, total: r.items.length,
        weak: weak, remaining: remaining,
        mocks: LP.mocks(round).length
      };
    },
    topics: function (round) {
      var r = (M.rounds || {})[round]; if (!r) return [];
      var by = {};
      r.items.forEach(function (it) {
        var t = it.topic || 'Other';
        by[t] = by[t] || { topic: t, total: 0, done: 0 };
        by[t].total++;
        var st = (S.items[it.id] || {}).st;
        if (st === 'solved' || st === 'done') by[t].done++;
      });
      return Object.keys(by).map(function (k) { return by[k]; })
        .sort(function (a, b) { return (a.done / a.total) - (b.done / b.total); });
    },
    lastActivity: function (round) {
      var best = 0;
      var r = (M.rounds || {})[round];
      if (r) r.items.forEach(function (it) { var t = (S.items[it.id] || {}).ts || 0; if (t > best) best = t; });
      LP.mocks(round).forEach(function (m) { if (m.ts > best) best = m.ts; });
      return best;
    },
    manifest: M
  };
  window.LP = LP;

  /* ---------------- helpers ---------------- */
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function ago(ts) {
    if (!ts) return 'never';
    var d = (Date.now() - ts) / 86400000;
    if (d < 1 / 24) return 'just now';
    if (d < 1) return Math.round(d * 24) + 'h ago';
    if (d < 30) return Math.round(d) + 'd ago';
    return new Date(ts).toLocaleDateString();
  }
  window.LPfmt = { ago: ago };
  function toast(msg) {
    var t = $('.toast') || (function () { var e = document.createElement('div'); e.className = 'toast'; document.body.appendChild(e); return e; })();
    t.textContent = msg; t.classList.add('on');
    clearTimeout(t._t); t._t = setTimeout(function () { t.classList.remove('on'); }, 1900);
  }
  window.LPtoast = toast;

  /* ---------------- nav ---------------- */
  function buildNav() {
    var side = $('#side'); if (!side) return;
    var auto = $('#autonav');
    if (auto) {
      var html = '';
      $$('.sec').forEach(function (sec) {
        var h = $('h2', sec); if (!h || !sec.id) return;
        html += '<a href="#' + sec.id + '" data-nav="' + sec.id + '">' + h.textContent + '</a>';
        $$('h3[id]', sec).forEach(function (h3) {
          html += '<a class="sub" href="#' + h3.id + '" data-nav="' + h3.id + '">' + h3.textContent + '</a>';
        });
      });
      auto.innerHTML = html;
    }
    var f = $('.navfilter');
    if (f) f.addEventListener('input', function () {
      var q = f.value.toLowerCase();
      $$('#side a[data-nav]').forEach(function (a) {
        a.classList.toggle('hide', q && a.textContent.toLowerCase().indexOf(q) < 0);
      });
    });
    var links = $$('#side a[data-nav]');
    var targets = links.map(function (a) { return document.getElementById(a.dataset.nav); });
    var tick = false;
    function spy() {
      if (tick) return; tick = true;
      requestAnimationFrame(function () {
        tick = false;
        var y = window.scrollY + 90, cur = null;
        targets.forEach(function (t, i) { if (t && t.offsetTop <= y) cur = links[i]; });
        links.forEach(function (a) { a.classList.toggle('on', a === cur); });
      });
    }
    window.addEventListener('scroll', spy); spy();
    var b = $('.burger');
    if (b) b.addEventListener('click', function () { document.body.classList.toggle('nav-open'); });
    var bd = $('.backdrop');
    if (bd) bd.addEventListener('click', function () { document.body.classList.remove('nav-open'); });
    $$('#side a').forEach(function (a) { a.addEventListener('click', function () { document.body.classList.remove('nav-open'); }); });
  }

  /* ---------------- progressive reveal ---------------- */
  function wireStages() {
    $$('.stage').forEach(function (st) {
      var head = $('.sh', st); if (!head) return;
      head.addEventListener('click', function () {
        st.classList.toggle('open');
        var box = st.closest('[data-id]');
        if (st.classList.contains('open') && box) {
          var seen = (LP.get(box.dataset.id).seen || 0) + 1;
          LP.set(box.dataset.id, { seen: seen });
        }
      });
    });
    $$('[data-revall]').forEach(function (b) {
      b.addEventListener('click', function () {
        var box = b.closest('[data-id]') || document;
        var stages = $$('.stage', box);
        var anyClosed = stages.some(function (s) { return !s.classList.contains('open'); });
        stages.forEach(function (s) { s.classList.toggle('open', anyClosed); });
        b.textContent = anyClosed ? 'Collapse all' : 'Reveal all';
      });
    });
  }

  /* ---------------- trackers ---------------- */
  function paint(box) {
    var id = box.dataset.id, it = LP.get(id);
    $$('.sbtn[data-st]', box).forEach(function (b) { b.classList.toggle('on', b.dataset.st === it.st); });
    $$('.conf b', box).forEach(function (b, i) { b.classList.toggle('on', (it.cf || 0) > i); });
    var n = $('.tnote', box); if (n && document.activeElement !== n) n.value = it.note || '';
    var stamp = $('.tstamp', box); if (stamp) stamp.textContent = it.ts ? 'saved ' + ago(it.ts) : '';
  }
  function wireTrackers() {
    $$('[data-id]').forEach(function (box) {
      if (!$('.track', box)) return;
      paint(box);
      $$('.sbtn[data-st]', box).forEach(function (b) {
        b.addEventListener('click', function () {
          var cur = LP.get(box.dataset.id).st;
          LP.set(box.dataset.id, { st: cur === b.dataset.st ? null : b.dataset.st });
          paint(box);
          LP.logActivity(document.body.dataset.round || '', box.dataset.label || box.dataset.id);
          renderProgress();
        });
      });
      $$('.conf b', box).forEach(function (b, i) {
        b.addEventListener('click', function () {
          var cur = LP.get(box.dataset.id).cf || 0;
          LP.set(box.dataset.id, { cf: cur === i + 1 ? 0 : i + 1 });
          paint(box); renderProgress();
        });
      });
      var n = $('.tnote', box);
      if (n) {
        var t; n.addEventListener('input', function () {
          clearTimeout(t); t = setTimeout(function () { LP.set(box.dataset.id, { note: n.value }); paint(box); }, 500);
        });
      }
    });
  }

  /* ---------------- timers ---------------- */
  function wireTimers() {
    $$('[data-timer]').forEach(function (wrap) {
      var out = $('.timer', wrap), start = $('[data-t-start]', wrap), reset = $('[data-t-reset]', wrap);
      var secs = parseInt(wrap.dataset.timer, 10) || 0, left = secs, iv = null;
      function show() {
        var m = Math.floor(Math.abs(left) / 60), s = Math.abs(left) % 60;
        out.textContent = (left < 0 ? '-' : '') + m + ':' + (s < 10 ? '0' : '') + s;
        out.style.color = left < 0 ? 'var(--red)' : '';
      }
      show();
      start.addEventListener('click', function () {
        if (iv) { clearInterval(iv); iv = null; start.textContent = '▶ Resume'; return; }
        start.textContent = '⏸ Pause';
        iv = setInterval(function () { left--; show(); if (left === 0) toast('Time is up — wrap up your answer'); }, 1000);
      });
      if (reset) reset.addEventListener('click', function () {
        clearInterval(iv); iv = null; left = secs; show(); start.textContent = '▶ Start';
      });
    });
  }

  /* ---------------- copy prompt for chat grading ---------------- */
  function wireCopy() {
    $$('[data-copy]').forEach(function (b) {
      b.addEventListener('click', function () {
        var box = b.closest('[data-id]');
        var prompt = b.dataset.copy;
        if (prompt === 'grade') {
          var q = (box.dataset.q || $('.mq', box) && $('.mq', box).textContent || '').trim();
          var notes = ($('.tnote', box) || {}).value || '';
          prompt = 'Act as my LinkedIn Staff Engineer interviewer for the ' +
            (document.body.dataset.roundName || 'interview') + ' round.\n\n' +
            'QUESTION I JUST ANSWERED:\n' + q + '\n\n' +
            'MY ANSWER:\n' + (notes || '(I answered out loud — I will paste or say it next)') + '\n\n' +
            'Grade it in this exact format: SCORE x/10, WHAT WAS STRONG, WHAT IS MISSING, ' +
            'STAFF-LEVEL SIGNAL, HOW TO IMPROVE, LIKELY FOLLOW-UP. Be strict, then ask me the follow-up.';
        }
        navigator.clipboard.writeText(prompt).then(function () {
          toast('Prompt copied — paste it to Claude');
        }, function () { toast('Copy failed — select the text manually'); });
      });
    });
  }

  /* ---------------- mock scoring ---------------- */
  function wireMocks() {
    $$('[data-mock]').forEach(function (box) {
      var sel = $('[data-score]', box);
      if (!sel) return;
      sel.addEventListener('change', function () {
        if (!sel.value) return;
        LP.addMock(document.body.dataset.round || '', box.dataset.id, +sel.value);
        LP.set(box.dataset.id, { st: 'done', cf: Math.max(1, Math.round(sel.value / 2)) });
        toast('Logged — score ' + sel.value + '/10');
        renderProgress();
      });
    });
  }

  /* ---------------- filters ---------------- */
  function wireFilters() {
    $$('[data-filter-scope]').forEach(function (scope) {
      var chips = $$('.fchip', scope), search = $('.search', scope);
      var listSel = scope.dataset.filterScope;
      var rows = $$(listSel);
      var count = $('.count', scope);
      function apply() {
        var active = {};
        chips.forEach(function (c) { if (c.classList.contains('on')) { active[c.dataset.fk] = active[c.dataset.fk] || []; active[c.dataset.fk].push(c.dataset.fv); } });
        var q = search ? search.value.toLowerCase().trim() : '';
        var shown = 0;
        rows.forEach(function (r) {
          var ok = true;
          for (var k in active) {
            var vals = (r.dataset[k] || '').toLowerCase().split(/\s*,\s*/);
            if (!active[k].some(function (v) { return vals.indexOf(v.toLowerCase()) >= 0; })) ok = false;
          }
          if (ok && q && r.textContent.toLowerCase().indexOf(q) < 0) ok = false;
          if (ok && active.status) { /* handled above via dataset */ }
          r.classList.toggle('hide', !ok);
          if (ok) shown++;
        });
        if (count) count.textContent = shown + ' of ' + rows.length + ' shown';
      }
      chips.forEach(function (c) {
        c.addEventListener('click', function () {
          if (c.dataset.solo === '1') chips.forEach(function (o) { if (o !== c && o.dataset.fk === c.dataset.fk) o.classList.remove('on'); });
          c.classList.toggle('on'); apply();
        });
      });
      if (search) search.addEventListener('input', apply);
      apply();
    });
  }

  /* ---------------- progress rendering ---------------- */
  function renderProgress() {
    $$('[data-progress-round]').forEach(function (el) {
      var st = LP.stats(el.dataset.progressRound);
      var bar = $('.bar>i', el); if (bar) bar.style.width = st.pct + '%';
      var pc = $('[data-pct]', el); if (pc) pc.textContent = st.pct + '%';
      var dn = $('[data-done]', el); if (dn) dn.textContent = st.done + ' / ' + st.total;
      var mk = $('[data-mocks]', el); if (mk) mk.textContent = st.mocks;
      var la = $('[data-last]', el); if (la) la.textContent = ago(LP.lastActivity(el.dataset.progressRound));
      var rg = $('.ring', el); if (rg) { rg.style.setProperty('--p', st.pct); var s = $('span', rg); if (s) s.textContent = st.pct + '%'; }
      var tp = $('[data-topics]', el);
      if (tp) {
        var t = LP.topics(el.dataset.progressRound);
        var covered = t.filter(function (x) { return x.done === x.total; }).length;
        tp.textContent = covered + ' of ' + t.length + ' topics complete';
      }
      var wk = $('[data-weak]', el);
      if (wk) {
        var w = LP.stats(el.dataset.progressRound).weak.slice(0, 3).map(function (i) { return i.topic || i.label; });
        wk.textContent = w.length ? w.join(' · ') : '—';
      }
    });
    if (typeof window.LPonProgress === 'function') window.LPonProgress(LP);
  }
  window.LPrenderProgress = renderProgress;

  /* ---------------- reset / export ---------------- */
  function wireData() {
    var r = $('[data-reset]');
    if (r) r.addEventListener('click', function () {
      if (confirm('Clear all saved progress for this workspace?')) { LP.reset(); location.reload(); }
    });
    var e = $('[data-export]');
    if (e) e.addEventListener('click', function () {
      navigator.clipboard.writeText(JSON.stringify(LP.all(), null, 2)).then(function () { toast('Progress JSON copied'); });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    buildNav(); wireStages(); wireTrackers(); wireTimers(); wireCopy(); wireMocks(); wireFilters(); wireData();
    renderProgress();
  });
})();
