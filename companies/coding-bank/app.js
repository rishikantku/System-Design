/* LinkedIn Staff AI Coding — interview simulator (browser side).
   Talks only to the local server (same origin). Every /api call carries the per-launch token the
   server embedded in this page. No API key ever reaches this file. */
(function () {
  'use strict';
  const TOKEN = document.querySelector('meta[name="sim-token"]').content;
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const app = $('#app');
  let STATUS = { dotnet: '', claude: false };
  let cleanup = [];

  function toast(msg, ms) {
    const t = $('#toast'); t.textContent = msg; t.classList.add('on');
    clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('on'), ms || 2200);
  }
  // Static (website) mode: the exported read-only copy sets window.SIM_STATIC and ships the data as JSON
  // files. Everything that needs the local server (running C#, Claude, sessions) answers with a clear note.
  const STATIC = !!window.SIM_STATIC;
  const LOCAL_ONLY = 'This needs the local setup (it runs your C# and talks to Claude). On the website you can browse, learn and read solutions.';
  async function staticApi(path) {
    const get = async (f) => { const r = await fetch(f); if (!r.ok) throw new Error('Not found'); return r.json(); };
    if (path === 'problems') return get('data/index.json');
    if (path === 'status') return { dotnet: '', claude: false, model: '', static: true };
    let m = /^problem\/([\w-]+)\/solution$/.exec(path); if (m) return get('data/solution/' + m[1] + '.json');
    m = /^problem\/([\w-]+)\?mode=learn$/.exec(path); if (m) return get('data/learn/' + m[1] + '.json');
    throw new Error(LOCAL_ONLY);
  }
  async function api(path, opts) {
    if (STATIC) return staticApi(path);
    opts = opts || {};
    const r = await fetch('/api/' + path, {
      method: opts.method || (opts.body ? 'POST' : 'GET'),
      headers: { 'x-sim-token': TOKEN, 'content-type': 'application/json' },
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(data.error || ('HTTP ' + r.status));
    return data;
  }
  // POST that answers with server-sent events. handlers: { delta, done, error, stage, flaw, end }
  async function stream(path, body, handlers) {
    const r = await fetch('/api/' + path, { method: 'POST', headers: { 'x-sim-token': TOKEN, 'content-type': 'application/json' }, body: JSON.stringify(body) });
    if (!r.ok || !(r.headers.get('content-type') || '').includes('event-stream')) {
      const d = await r.json().catch(() => ({}));
      (handlers.error || (() => {}))({ message: d.error || ('HTTP ' + r.status) });
      return;
    }
    const reader = r.body.getReader(); const dec = new TextDecoder(); let buf = '';
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      let i;
      while ((i = buf.indexOf('\n\n')) >= 0) {
        const chunk = buf.slice(0, i); buf = buf.slice(i + 2);
        const ev = /^event: (.*)$/m.exec(chunk), da = /^data: (.*)$/m.exec(chunk);
        if (ev && da && handlers[ev[1]]) handlers[ev[1]](JSON.parse(da[1]));
      }
    }
  }

  // ---------------------------------------------------------------- markdown (escapes first; AI output is untrusted)
  function inline(s) {
    return s.replace(/`([^`]+)`/g, (m, c) => '<code>' + c + '</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')
      .replace(/(^|[^*\w])\*([^*\s][^*]*?)\*(?![*\w])/g, '$1<i>$2</i>')
      .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+|\.\.\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  }
  function md(src) {
    const lines = esc(src).split('\n');
    let out = '', i = 0;
    const codeId = () => 'cb' + Math.random().toString(36).slice(2, 9);
    while (i < lines.length) {
      const l = lines[i];
      const fence = /^\s*```\s*([\w#+-]*)\s*$/.exec(l);
      if (fence) {
        const lang = (fence[1] || '').toLowerCase(); const buf = []; i++;
        while (i < lines.length && !/^\s*```\s*$/.test(lines[i])) buf.push(lines[i++]);
        i++;
        const id = codeId();
        out += '<div class="codewrap"><button class="copy" data-copy="' + id + '">Copy</button><pre id="' + id + '" data-lang="' +
          (lang === 'c#' || lang === 'cs' || lang === 'csharp' || lang === '' ? 'csharp' : lang) + '">' + buf.join('\n') + '</pre></div>';
        continue;
      }
      if (/^\s*\|.*\|\s*$/.test(l) && i + 1 < lines.length && /^\s*\|[\s:|-]+\|\s*$/.test(lines[i + 1])) {
        const row = (x) => x.trim().replace(/^\||\|$/g, '').split(/(?<!\\)\|/).map((c) => inline(c.trim().replace(/\\\|/g, '|')));
        let t = '<div class="tw"><table><thead><tr>' + row(l).map((c) => '<th>' + c + '</th>').join('') + '</tr></thead><tbody>';
        i += 2;
        while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) t += '<tr>' + row(lines[i++]).map((c) => '<td>' + c + '</td>').join('') + '</tr>';
        out += t + '</tbody></table></div>'; continue;
      }
      const h = /^(#{1,4})\s+(.*)$/.exec(l);
      if (h) { out += '<h' + (h[1].length + 1) + '>' + inline(h[2]) + '</h' + (h[1].length + 1) + '>'; i++; continue; }
      if (/^\s*&gt;\s?/.test(l)) {
        const buf = []; while (i < lines.length && /^\s*&gt;\s?/.test(lines[i])) buf.push(lines[i++].replace(/^\s*&gt;\s?/, ''));
        out += '<blockquote>' + inline(buf.join('\n')) + '</blockquote>'; continue;
      }
      if (/^\s*([-*]|\d+\.)\s+/.test(l)) {
        const ordered = /^\s*\d+\./.test(l); const buf = [];
        while (i < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[i])) buf.push(lines[i++].replace(/^\s*([-*]|\d+\.)\s+/, ''));
        out += (ordered ? '<ol>' : '<ul>') + buf.map((x) => '<li>' + inline(x) + '</li>').join('') + (ordered ? '</ol>' : '</ul>'); continue;
      }
      if (!l.trim()) { i++; continue; }
      const buf = [];
      while (i < lines.length && lines[i].trim() && !/^\s*(```|#{1,4}\s|[-*]\s|\d+\.\s|&gt;|\|)/.test(lines[i])) buf.push(lines[i++]);
      if (!buf.length) buf.push(lines[i++]);
      out += '<p>' + inline(buf.join('<br>')) + '</p>';
    }
    return out;
  }
  function decorate(root) {
    $$('button[data-copy]', root).forEach((b) => {
      if (b._w) return; b._w = 1;
      b.addEventListener('click', () => {
        const pre = document.getElementById(b.dataset.copy);
        navigator.clipboard.writeText(pre.textContent).then(() => { toast('Copied — you decide whether it goes in the editor'); b.dispatchEvent(new CustomEvent('ai-copy', { bubbles: true })); });
      });
    });
    withMonaco(() => $$('pre[data-lang="csharp"]', root).forEach((pre) => {
      // Code boxes are dark, but colorize uses the global theme (light 'vs' outside the pad), which
      // painted keywords dark blue on black. Only switch when no editor is open — the theme is global.
      if (!monaco.editor.getEditors().length) monaco.editor.setTheme('vs-dark');
      if (pre._c) return; pre._c = 1;
      const txt = pre.textContent;
      monaco.editor.colorize(txt, 'csharp', { tabSize: 4 }).then((html) => { pre.innerHTML = html; });
    }));
  }

  // ---------------------------------------------------------------- Monaco
  let monacoReady = null;
  function withMonaco(fn) {
    if (!monacoReady) {
      monacoReady = new Promise((res) => {
        require.config({ paths: { vs: window.SIM_MONACO || '/vs' } });
        require(['vs/editor/editor.main'], () => res());
      });
    }
    return monacoReady.then(fn);
  }

  // ---------------------------------------------------------------- helpers
  const prio = (p) => '<span class="tag prio ' + p + '">' + p + '</span>';
  const lab = (x) => '<span class="tag lab ' + esc(x.label) + '">' + esc(x.labelText) + '</span>';
  const REL = { exact: 'same problem', twin: 'closest public twin', variation: 'variation', followup: 'harder follow-up', pattern: 'same technique' };
  // compact chips for tables; `full` adds the title, difficulty and relation for the Learn page and the pad
  const lcRefs = (refs, full) => (refs || []).map((r) => '<a class="lcref rel-' + esc(r.rel) + '" href="' + esc(r.url) + '" target="_blank" rel="noopener" title="' +
      esc('LeetCode ' + r.num + ' · ' + r.title + ' · ' + r.diff + (r.premium ? ' · premium' : '') + ' — ' + (REL[r.rel] || r.rel)) + '">' +
      (r.premium ? '🔒' : '') + r.num + (full ? ' · ' + esc(r.title) + ' <span class="lcmeta">' + esc(r.diff) + ' · ' + esc(REL[r.rel] || r.rel) + '</span>' : '') + '</a>').join(full ? '' : ' ');
  window.lcRefs = lcRefs;
  const fmt = (sec) => { sec = Math.max(0, Math.round(sec)); return Math.floor(sec / 60) + ':' + String(sec % 60).padStart(2, '0'); };
  function modal(html, onMount) {
    const bg = document.createElement('div'); bg.className = 'modal-bg';
    bg.innerHTML = '<div class="modal">' + html + '</div>';
    document.body.appendChild(bg);
    const close = () => bg.remove();
    bg.addEventListener('click', (e) => { if (e.target === bg) close(); });
    if (onMount) onMount(bg, close);
    return close;
  }
  function setNav(key) { $$('.top nav a').forEach((a) => a.classList.toggle('on', a.dataset.nav === key)); }
  function claudeNote() {
    return STATUS.claude ? '' : '<div class="note warn"><b>Claude is not configured.</b> The assistant, the live interviewer and Claude grading are off. ' +
      'Add <code>ANTHROPIC_API_KEY=…</code> to the local <code>.env</code> file and restart <code>npm run dev</code>. Everything else — editor, real C# compile and tests, ' +
      'the scripted interviewer, verification training and self-assessment — works without it.</div>';
  }
  function dotnetNote() {
    return STATUS.dotnet ? '' : '<div class="note bad"><b>Simulation only — C# execution is not enabled.</b> The .NET SDK (<code>dotnet</code>) was not found. Run and Run Tests will refuse rather than pretend.</div>';
  }

  // ---------------------------------------------------------------- router
  async function route() {
    cleanup.forEach((f) => { try { f(); } catch (e) { /* ignore */ } }); cleanup = [];
    document.body.classList.remove('ws-on'); delete document.documentElement.dataset.ui;
    // tolerate a link copied with trailing punctuation ("#/bank." from the end of a sentence)
    const h = location.hash.replace(/^#\/?/, '').replace(/[.,;:!?)\]]+$/, '');
    const [view, a, b] = h.split('/');
    try {
      // Every view is awaited, so an error inside one is shown here rather than lost as an
      // unhandled rejection (that is how a real bug in the workspace once went unnoticed).
      if (STATIC && ['practice', 'mock', 'sim', 'w', 'session', 'verify', 'history'].includes(view)) return staticNote(view, a);
      if (!view) return STATIC ? await bank() : await home();
      if (view === 'bank') return await bank();
      if (view === 'learn') return await learn(a);
      if (view === 'solution') return await solution(a);
      if (view === 'practice') return await startSession(a, 'practice', 0, false);
      if (view === 'mock') return await mockSetup(a);
      if (view === 'sim') return await simSetup();
      if (view === 'w') return await workspace(a);
      if (view === 'session') return await report(a);
      if (view === 'verify') return await verify();
      if (view === 'history') return await history();
      app.innerHTML = '<div class="page"><h1>Not found</h1></div>';
    } catch (e) {
      console.error(e);
      document.body.classList.remove('ws-on');
      app.innerHTML = '<div class="page"><div class="note bad"><b>Something went wrong.</b> ' + esc(e.message) + '</div><p><a href="#/">Back to the dashboard</a></p></div>';
    }
  }
  function staticNote(view, id) {
    setNav('bank');
    const what = { practice: 'Practice', mock: 'Mock interview', sim: 'Full simulation', w: 'The coding pad', session: 'Session reports', verify: 'Verification training', history: 'History' }[view] || 'This';
    app.innerHTML = '<div class="page"><h1>' + esc(what) + ' runs locally</h1><div class="note">' + esc(LOCAL_ONLY) + '</div><p>' +
      (id ? '<a class="btn" href="#/learn/' + esc(id) + '">Learn this question</a> <a class="btn sol" href="#/solution/' + esc(id) + '">Solution</a> ' : '') +
      '<a class="btn pri" href="#/bank">Back to the question bank</a></p></div>';
  }
  window.addEventListener('hashchange', route);
  window.addEventListener('unhandledrejection', (e) => { console.error(e.reason); toast('Error: ' + ((e.reason && e.reason.message) || e.reason), 5000); });

  // ---------------------------------------------------------------- dashboard
  async function home() {
    setNav('home');
    const [d, idx] = await Promise.all([api('dashboard'), api('problems')]);
    const titles = Object.fromEntries(idx.problems.map((p) => [p.id, p.title]));
    const prog = d.byProblem.sort((x, y) => y.latest - x.latest).map((p) =>
      '<tr><td>' + esc(titles[p.problemId] || p.title) + '</td><td><b>' + (p.latest / 10).toFixed(1) + '</b>/10</td><td>' + (p.best / 10).toFixed(1) +
      '</td><td>' + p.sessions + '</td><td><div class="bar" style="width:140px"><i style="width:' + p.latest + '%"></i></div></td></tr>').join('');
    const NAMES = { problem_solving: 'Problem solving', algorithm: 'Algorithm', data_structures: 'Data structures', csharp: 'C# implementation', testing: 'Testing',
      prompt_quality: 'Prompt quality', verification: 'Verification', ai_judgment: 'AI judgment', delegation: 'Delegation', architecture: 'Architecture',
      concurrency: 'Concurrency', scalability: 'Scalability', production: 'Production thinking', communication: 'Communication', judgment: 'Engineering judgment' };
    const weak = d.weak.slice(0, 4).map((w) => '<li><b>' + esc(NAMES[w.key] || w.key) + '</b> — ' + w.avg.toFixed(1) + '/10</li>').join('');
    const ai = d.aiRecent;
    const avg = (f) => ai.length ? (ai.reduce((s, x) => s + (f(x) || 0), 0) / ai.length) : 0;
    app.innerHTML = '<div class="page">' +
      '<h1>LinkedIn Staff Engineer — AI Coding Interview Simulator</h1>' +
      '<p class="lead">A local CoderPad-style workspace: write C#, compile and test it for real on this machine, use Claude as a pair programmer, and get interviewed — with requirements that change, follow-ups that escalate, and AI output you have to catch before you ship it.</p>' +
      dotnetNote() + claudeNote() +
      '<div class="grid g4" style="margin-top:16px">' +
      tile('Learn', 'Study any question: 17 sections, from the clarifications to the reference solution.', '#/bank', 'Open the bank') +
      tile('Practice', 'Editor, real tests, Claude for hints and reviews. The solution stays hidden until you ask.', '#/bank', 'Pick a problem') +
      tile('Mock interview', 'Design first, then AI. The interviewer reveals requirements one at a time.', '#/bank', 'Pick a problem') +
      tile('Full simulation', '60 minutes, random P0 question, no reference, planted AI defects, final evaluation.', '#/sim', 'Start', true) + '</div>' +
      '<h2>LinkedIn AI Coding Progress</h2>' +
      (prog ? '<div class="card tw"><table class="t"><thead><tr><th>Problem</th><th>Latest</th><th>Best</th><th>Sessions</th><th></th></tr></thead><tbody>' + prog + '</tbody></table></div>'
            : '<div class="card muted">No evaluated sessions yet. Finish a practice or mock session and evaluate it — scores appear here.</div>') +
      '<div class="grid g2"><div class="card"><h3>Weakest areas (last 5 sessions)</h3>' + (weak ? '<ol style="margin:8px 0 0 20px">' + weak + '</ol>' : '<p class="muted">—</p>') + '</div>' +
      '<div class="card"><h3>How you use the AI (last 5 sessions)</h3>' + (ai.length ?
        '<p>Average prompts <b>' + avg((x) => x.prompts).toFixed(1) + '</b> · full-solution requests <b>' + avg((x) => x.full).toFixed(1) +
        '</b> · seconds before first AI request <b>' + Math.round(avg((x) => x.secondsBeforeFirstAi)) + '</b> · AI pastes never tested <b>' + avg((x) => x.aiPastesUntested).toFixed(1) + '</b></p>' : '<p class="muted">—</p>') + '</div></div>' +
      '<h2>Recent sessions</h2>' + sessionsTable(d.recent) + '</div>';
  }
  function tile(t, d, href, cta, pri) {
    return '<div class="card"><h3>' + t + '</h3><p class="small muted" style="min-height:62px">' + d + '</p><a class="btn ' + (pri ? 'pri' : '') + '" href="' + href + '">' + cta + ' →</a></div>';
  }
  function sessionsTable(list) {
    if (!list.length) return '<div class="card muted">None yet.</div>';
    return '<div class="card tw"><table class="t"><thead><tr><th>When</th><th>Problem</th><th>Mode</th><th>Time</th><th>Stages</th><th>AI prompts</th><th>Score</th><th>Verdict</th></tr></thead><tbody>' +
      list.map((s) => '<tr><td>' + new Date(s.startedAt).toLocaleString() + '</td><td><a href="#/session/' + s.id + '">' + esc(s.title) + '</a></td><td>' + s.mode +
        '</td><td>' + s.minutes + ' min</td><td>' + s.stagesPassed + '/' + (s.stages || '—') + '</td><td>' + s.prompts + '</td><td>' + (s.overall == null ? '—' : s.overall + '/100') +
        '</td><td>' + (s.verdict ? '<span class="verdict ' + s.verdict.split(' ')[0] + '" style="font-size:12px;padding:2px 8px">' + s.verdict + '</span>' : '<a href="#/session/' + s.id + '">evaluate</a>') + '</td></tr>').join('') +
      '</tbody></table></div>';
  }

  // ---------------------------------------------------------------- bank
  async function bank() {
    setNav('bank');
    const idx = await api('problems');
    const CO = { linkedin: 'LinkedIn', agoda: 'Agoda' };
    let saved = 'all'; try { saved = localStorage.getItem('bank.company') || 'all'; } catch (e) { /* ignore */ }
    const f = { company: CO[saved] ? saved : 'all', round: 'all', prio: new Set(), label: new Set(), q: '', recent: false, psort: '' };
    try { f.psort = ['asc', 'desc'].includes(localStorage.getItem('bank.psort')) ? localStorage.getItem('bank.psort') : ''; } catch (e) { /* ignore */ }
    const PRI = { P0: 0, P1: 1, P2: 2, P3: 3 };
    const RD = { ai: 'AI round', coding: 'Coding round' };
    const rds = (p) => p.rounds || ['coding'];
    const count = (c) => idx.problems.filter((p) => (p.companies || ['linkedin']).includes(c)).length;
    app.innerHTML = '<div class="page"><h1>Question bank</h1>' +
      '<p class="lead">Coding questions per company, ranked by evidence: independent candidate reports, your own first-party lists (InterviewDB, your past questions), recency and level. Rank 1 is the strongest evidence — a ranking, not a probability. Every question is labelled by how it is evidenced; nothing inferred is presented as confirmed.</p>' +
      '<div class="cotabs" id="cot">' + [['all', 'All companies', idx.problems.length], ['linkedin', 'LinkedIn', count('linkedin')], ['agoda', 'Agoda', count('agoda')]]
        .map(([k, v, n]) => '<button class="cotab' + (f.company === k ? ' on' : '') + '" data-c="' + k + '">' + v + ' <span class="n">' + n + '</span></button>').join('') +
      '<span class="rdsep"></span>' + [['all', 'Every round'], ['coding', 'Coding round'], ['ai', 'AI round']]
        .map(([k, v]) => '<button class="rdtab' + (k === 'all' ? ' on' : '') + '" data-r="' + k + '">' + v + '</button>').join('') + '</div>' +
      '<div class="filters" id="pf"><button class="chip recentchip" data-k="recent" data-v="1" title="In your list of recently asked LinkedIn questions (Oct 2026)">★ Recently asked</button>' +
      ['P0', 'P1', 'P2'].map((p) => '<button class="chip" data-k="prio" data-v="' + p + '">' + p + '</button>').join('') +
      [['idb', 'InterviewDB'], ['idb-list', 'InterviewDB-listed'], ['multi', 'Multiple candidate reports'], ['single', 'Reported LinkedIn'], ['derived', 'Research-derived'], ['pattern', 'Pattern-based practice'],
       ['ag-multi', 'Multiple Agoda reports'], ['ag-single', 'Reported Agoda'], ['ag-recon', 'Agoda — reconstructed'], ['ag-list', 'Agoda frequency list only']]
        .map(([k, v]) => '<button class="chip" data-k="label" data-v="' + k + '">' + v + '</button>').join('') +
      '<input class="search" id="pq" placeholder="Search…"></div><div class="card tw"><table class="t"><thead><tr><th class="sortable" id="rsort" title="Order by rank (evidence)">Rank <span id="rsortic"></span></th><th class="sortable" id="psort" title="Sort by priority — click again to reverse">Priority <span id="psortic">⇅</span></th><th>Question</th><th>Company</th><th>LeetCode</th><th>Provenance</th><th>Category</th><th>Stages</th><th></th></tr></thead><tbody id="pt"></tbody></table></div>' +
      '<h2>Your LeetCode list (LinkedIn)</h2><p class="muted small">The 42 numbers you supplied plus 11 closest public twins, each verified against LeetCode\'s own index. 30 of them are also full questions above, tagged <b>InterviewDB-listed</b> — with tests, a Learn page and a Solution; the rest are covered by the question named in the relation column.</p>' +
      '<div class="card tw"><table class="t"><thead><tr><th>#</th><th>Problem</th><th>Difficulty</th><th>Relation to the InterviewDB set</th><th></th></tr></thead><tbody>' +
      idx.leetcode.map((x) => '<tr><td>' + x.number + '</td><td><a href="' + esc(x.url) + '" target="_blank" rel="noopener">' + esc(x.title) + '</a>' + (x.premium ? ' <span class="tag lab single">premium</span>' : '') +
        '</td><td>' + esc(x.diff) + '</td><td class="small">' + esc(x.rel) + (x.linked.length ? ' · ' + x.linked.join(', ') : '') + '</td><td style="white-space:nowrap">' +
        (x.full ? '<a class="btn sm" href="#/learn/' + x.full + '">Learn</a> <a class="btn sm" href="#/practice/' + x.full + '">Practice</a> <a class="btn sm sol" href="#/solution/' + x.full + '">Solution</a>'
                : '<a class="btn sm" href="#/practice/' + x.id + '">Practice</a>') + '</td></tr>').join('') +
      '</tbody></table></div></div>';
    const cos = (p) => p.companies || ['linkedin'];
    const rankOf = (p) => f.company !== 'all' ? (p.rank || {})[f.company] : Math.min(...Object.values(p.rank || {}).concat([999]));
    function rankCell(p) {
      const r = p.rank || {};
      if (f.company !== 'all') return r[f.company] ? '<span class="rk">#' + r[f.company] + '</span>' : '<span class="muted">—</span>';
      return Object.entries(r).map(([c, n]) => '<span class="rk">' + (c === 'agoda' ? 'AG' : 'LI') + ' #' + n + '</span>').join(' ') || '<span class="muted">—</span>';
    }
    function draw() {
      const rows = idx.problems.filter((p) => (f.company === 'all' || cos(p).includes(f.company)) && (f.round === 'all' || rds(p).includes(f.round)) && (!f.prio.size || f.prio.has(p.prio)) && (!f.label.size || f.label.has(p.label)) && (!f.recent || p.recent) &&
        (!f.q || (p.title + ' ' + p.cat).toLowerCase().includes(f.q)))
        .sort((a, b) => (f.psort ? ((PRI[a.prio] ?? 9) - (PRI[b.prio] ?? 9)) * (f.psort === 'asc' ? 1 : -1) : 0) ||   // priority only when chosen
          (rankOf(a) ?? 999) - (rankOf(b) ?? 999) || cos(a)[0].localeCompare(cos(b)[0]) || a.title.localeCompare(b.title));
      $('#psortic').textContent = f.psort === 'asc' ? '▲' : f.psort === 'desc' ? '▼' : '⇅';
      $('#psort').classList.toggle('on', !!f.psort);
      $('#rsort').classList.toggle('on', !f.psort); $('#rsortic').textContent = f.psort ? '' : '▲';
      $('#pt').innerHTML = rows.map((p) => '<tr><td style="white-space:nowrap">' + rankCell(p) + '</td><td>' + prio(p.prio) + '</td><td><b>' + esc(p.title) + '</b>' + (p.recent ? ' <span class="tag recent" title="In your list of recently asked LinkedIn questions (Oct 2026)">★ recent</span>' : '') + '</td><td>' +
        cos(p).map((c) => '<span class="cotag ' + c + '">' + esc(CO[c] || c) + '</span>').join(' ') + '<br>' + rds(p).map((r) => '<span class="rdtag ' + r + '">' + esc(RD[r]) + '</span>').join(' ') + '</td><td class="lccell">' + (lcRefs(p.lcrefs) || '<span class="muted small">—</span>') + '</td><td>' + lab(p) + '</td><td class="small">' + esc(p.cat) +
        '</td><td>' + p.stages + '</td><td style="white-space:nowrap"><a class="btn sm" href="#/learn/' + p.id + '">Learn</a> <a class="btn sm" href="#/practice/' + p.id +
        '">Practice</a> <a class="btn sm pri" href="#/mock/' + p.id + '">Mock</a>' +
        (p.hasSolution ? ' <a class="btn sm sol" href="#/solution/' + p.id + '">Solution</a>' : '') + '</td></tr>').join('') || '<tr><td colspan="9" class="muted">No match.</td></tr>';
    }
    $$('#cot .cotab').forEach((b) => b.addEventListener('click', () => {
      f.company = b.dataset.c; try { localStorage.setItem('bank.company', f.company); } catch (e) { /* ignore */ }
      $$('#cot .cotab').forEach((x) => x.classList.toggle('on', x === b)); draw(); }));
    $$('#cot .rdtab').forEach((b) => b.addEventListener('click', () => { f.round = b.dataset.r; $$('#cot .rdtab').forEach((x) => x.classList.toggle('on', x === b)); draw(); }));
    $('#rsort').addEventListener('click', () => { f.psort = ''; try { localStorage.setItem('bank.psort', ''); } catch (e) { /* ignore */ } draw(); });
    $('#psort').addEventListener('click', () => {
      f.psort = f.psort === 'asc' ? 'desc' : 'asc';      // toggles P0-first ↔ P2-first; the Rank header returns to rank order
      try { localStorage.setItem('bank.psort', f.psort); } catch (e) { /* ignore */ }
      draw();
    });
    $$('#pf .chip').forEach((c) => c.addEventListener('click', () => {
      if (c.dataset.k === 'recent') f.recent = !f.recent;
      else { const s = f[c.dataset.k]; s.has(c.dataset.v) ? s.delete(c.dataset.v) : s.add(c.dataset.v); }
      c.classList.toggle('on'); draw(); }));
    $('#pq').addEventListener('input', (e) => { f.q = e.target.value.toLowerCase(); draw(); });
    draw();
  }

  // ---------------------------------------------------------------- solution
  async function solution(id) {
    setNav('bank');
    const p = await api('problem/' + id + '/solution');
    app.innerHTML = '<div class="page solpage"><p><a href="#/bank">← Question bank</a> · <a href="#/learn/' + esc(id) + '">Learn</a> · ' +
      '<a href="#/practice/' + esc(id) + '">Practice</a> · <a href="#/mock/' + esc(id) + '">Mock</a></p>' +
      '<h1>' + esc(p.title) + ' — solution</h1>' +
      ((p.leetcode || []).length ? '<div class="lclist">' + lcRefs(p.leetcode, true) + '</div>' : '') +
      '<div class="note small">Try it first in <b>Practice</b>. This page is for checking your approach afterwards — the code below compiled and passed every part of this question\'s tests.</div>' +
      (p.aiGuide ? '<div class="filters soltabs"><button class="chip on" data-t="guide">AI-round tutorial</button><button class="chip" data-t="code">Solution and code</button></div>' : '') +
      (p.aiGuide ? '<div id="t-guide">' + aiGuide(p.aiGuide, p.id) + '</div>' : '') +
      '<div id="t-code" class="md"' + (p.aiGuide ? ' hidden' : '') + '>' + md(p.md) + '</div></div>';
    decorate(app);
    if (p.aiGuide) {
      $$('.soltabs .chip').forEach((c) => c.addEventListener('click', () => {
        $$('.soltabs .chip').forEach((x) => x.classList.toggle('on', x === c));
        $('#t-guide').hidden = c.dataset.t !== 'guide'; $('#t-code').hidden = c.dataset.t !== 'code';
      }));
      wireGuide(p.id, p.aiGuide);
    }
  }

  // ---------------------------------------------------------------- the AI-round tutorial (Solution page)
  const KIND_LABEL = { boundary: 'Boundary', edge: 'Edge case', concurrency: 'Concurrency', input: 'Bad input', growth: 'Growth', complexity: 'Complexity' };
  const rich = (t) => inline(esc(t || ''));
  function aiGuide(g, pid) {
    const role = (r) => '<span class="aig-role r-' + r + '">' + esc(g.roles[r][0]) + '</span>';
    const plan = '<table class="aig-plan"><thead><tr><th>Minutes</th><th>What you do</th><th>AI</th></tr></thead><tbody>' +
      g.plan.map(([t, what, r]) => '<tr><td>' + esc(t) + '</td><td>' + rich(what) + '</td><td>' + role(r) + '</td></tr>').join('') + '</tbody></table>';
    const roles = '<div class="aig-roles">' + Object.entries(g.roles).map(([k, [name, what]]) => '<div>' + role(k) + ' <span class="small muted">' + esc(what) + '</span></div>').join('') + '</div>';
    const check = '<div class="aig-check">' + g.checklist.map(([k, name, what, ex], i) =>
      '<div class="aig-ck"><b>' + (i + 1) + ' · ' + esc(name) + '</b><span>' + esc(what) + '</span><code>' + esc(ex) + '</code></div>').join('') + '</div>';
    const stage = (st, i) => {
      const step = (n, title, body, cls) => '<div class="aig-step ' + (cls || '') + '"><div class="aig-n">' + n + '</div><div class="aig-sb"><h4>' + title + '</h4>' + body + '</div></div>';
      const [bp, bgot, bwhy] = st.bad, [gp, gwhy] = st.good;
      const prompts = '<div class="aig-pp">' +
        '<div class="aig-p bad"><div class="aig-pt">✗ Bad prompt</div><pre class="aig-ptext">' + esc(bp) + '</pre>' +
          '<div class="aig-got"><b>What comes back:</b> ' + rich(bgot) + '</div><ul>' + bwhy.map((w) => '<li>' + rich(w) + '</li>').join('') + '</ul></div>' +
        '<div class="aig-p good"><div class="aig-pt">✓ Good prompt <button class="btn sm aig-copy" data-copytext="' + esc(gp) + '">Copy</button></div><pre class="aig-ptext">' + esc(gp) + '</pre>' +
          '<ul>' + gwhy.map((w) => '<li>' + rich(w) + '</li>').join('') + '</ul></div></div>';
      const val = '<ul class="aig-val">' + st.validate.map(([k, t]) => '<li><span class="aig-k k-' + k + '">' + esc(KIND_LABEL[k] || k) + '</span>' + rich(t) + '</li>').join('') + '</ul>';
      const tryit = '<div class="aig-try" data-stage="' + i + '"><textarea class="fld" rows="4" placeholder="Write the prompt YOU would send at this stage, then check it…"></textarea>' +
        '<p><button class="btn sm aig-local">Check instantly</button> <button class="btn sm pri aig-claude">Grade with Claude</button> ' +
        '<span class="small muted">Instant = a checklist of the six parts (keyword-based, not a grade). Claude = a real grade with a rewrite.</span></p><div class="aig-res"></div></div>';
      return '<section class="aig-stage"><h3><span class="aig-sn">Stage ' + (i + 1) + '</span> ' + esc(st.name) + ' <span class="muted small">· ' + esc(st.when) + '</span></h3>' +
        '<div class="aig-req"><b>Interviewer:</b> <i>"' + esc(st.say_iv) + '"</i><br><span class="small">' + rich(st.require) + '</span></div>' +
        step(1, 'Before any AI — you decide', '<p>' + rich(st.yours) + '</p>', 'own') +
        step(2, 'When to bring the AI in', '<p>' + rich(st.ai) + '</p>') +
        step(3, 'The prompt — bad vs good', prompts) +
        step(4, 'What comes back — and the defect to look for', '<p>' + rich(st.reply) + '</p>', 'warn') +
        step(5, 'Validate the output before you trust it', val) +
        step(6, 'The tests you write <span class="aig-ok">✓ compiled and passed against the reference</span>', md('```csharp\n' + st.tests.trim() + '\n```')) +
        step(7, 'Fix it — by hand or with a narrow follow-up', '<p>' + rich(st.fix) + '</p>', 'fix') +
        step(8, 'Say it out loud', '<p class="aig-say">' + rich(st.say) + '</p>') +
        step(9, 'Try it — grade your own prompt for this stage', tryit, 'try') + '</section>';
    };
    return '<div class="aig">' +
      '<p class="aig-intro">' + rich(g.intro) + '</p>' +
      '<details class="acc" open><summary>The round, minute by minute — and when the AI is used</summary><div class="body">' + plan + roles + '</div></details>' +
      '<details class="acc" open><summary>The six parts of a good prompt</summary><div class="body">' + check +
        '<p class="small muted">Every good prompt below has these parts; every bad one is missing most of them.</p></div></details>' +
      (g.flaw ? '<p class="note small">This question\'s verified "would you ship this?" exercise (' + esc(g.flaw.id) + ', ' + esc(g.flaw.kind) + ') is on the <a href="#/learn/' + encodeURIComponent(pid) + '">Learn page</a> — real AI-style code with a defect a test reproduces.</p>' : '') +
      g.stages.map(stage).join('') + '</div>';
  }

  // The instant check: which of the six parts the prompt shows. Keyword-based — it says so on the page.
  function localPromptCheck(st, prompt) {
    const t = prompt.toLowerCase(); const has = (re) => re.test(prompt);
    const camel = (st.good[0].match(/\b[A-Z][a-z]+[A-Z]\w*|\b[A-Z]\w*\(|_\w+/g) || []).map((x) => x.replace('(', ''));
    const kwHits = st.kw.filter((k) => t.includes(k.toLowerCase()));
    return [
      ['scope', has(/\b(below|pasted|this class|my class)\b/i) || camel.some((w) => prompt.includes(w)), 'Name the method and class, and paste your class.'],
      ['rules', kwHits.length >= 2, 'State the rules: ' + st.kw.join(', ') + (kwHits.length ? ' (you have: ' + kwHits.join(', ') + ')' : '')],
      ['shape', has(/keep my|no new public|don.?t change|do not change|same signature|my fields/i), 'Freeze the shape: "Keep my fields; no new public members."'],
      ['exclude', has(/\bno [a-z]|don.?t use|do not use|\bwithout\b|\bnever\b|\bnot (a|an|the)\b/i), 'Exclude the likely wrong answer by name.'],
      ['check', has(/assumption|\bwhy\b|reason|explain|complexity/i), 'Ask for assumptions first, or a reason per test.'],
      ['size', has(/\bonly\b|minimal|\bdiff\b|do not rewrite|don.?t rewrite|no code|show only/i), 'Keep the reply small: "show only…", "change only…".'],
    ];
  }
  function wireGuide(pid, g) {
    const root = $('#t-guide');
    $$('.aig-copy', root).forEach((b) => b.addEventListener('click', () => navigator.clipboard.writeText(b.dataset.copytext).then(() => toast('Prompt copied'))));
    $$('.aig-try', root).forEach((box) => {
      const st = g.stages[+box.dataset.stage]; const ta = $('textarea', box); const res = $('.aig-res', box);
      $('.aig-local', box).addEventListener('click', () => {
        const v = ta.value.trim(); if (v.length < 10) { res.innerHTML = '<p class="note small">Write a prompt first.</p>'; return; }
        const rows = localPromptCheck(st, v); const ok = rows.filter((r) => r[1]).length;
        const names = Object.fromEntries(g.checklist.map(([k, n]) => [k, n]));
        res.innerHTML = '<div class="aig-score">' + ok + ' / 6 parts present</div><ul class="aig-parts">' +
          rows.map(([k, good, hint]) => '<li class="' + (good ? 'y' : 'n') + '">' + (good ? '✓' : '✗') + ' <b>' + esc(names[k]) + '</b>' + (good ? '' : ' — ' + esc(hint)) + '</li>').join('') + '</ul>';
      });
      $('.aig-claude', box).addEventListener('click', async (e) => {
        const v = ta.value.trim(); if (v.length < 10) { res.innerHTML = '<p class="note small">Write a prompt first.</p>'; return; }
        e.target.disabled = true; res.innerHTML = '<p class="muted small">Claude is grading…</p>';
        try {
          const r = await api('prompt-grade', { body: { problemId: pid, stage: +box.dataset.stage, prompt: v } });
          res.innerHTML = '<div class="aig-score">' + r.score + ' / 10 — ' + esc(r.verdict) + '</div><ul class="aig-parts">' +
            r.parts.map((x) => '<li class="' + (x.ok ? 'y' : 'n') + '">' + (x.ok ? '✓' : '✗') + ' <b>' + esc(x.part) + '</b> — ' + esc(x.note) + '</li>').join('') + '</ul>' +
            '<p class="small"><b>Biggest risk:</b> ' + esc(r.missing_risk) + '</p><p class="small"><b>Stronger version:</b></p><pre class="aig-ptext">' + esc(r.improved) + '</pre>';
        } catch (err) { res.innerHTML = '<p class="note bad small">' + esc(err.message) + '</p>'; }
        e.target.disabled = false;
      });
    });
  }

  // ---------------------------------------------------------------- learn
  async function learn(id) {
    setNav('bank');
    const p = await api('problem/' + id + '?mode=learn');
    app.innerHTML = '<div class="page"><p><a href="#/bank">← Question bank</a></p><h1>' + esc(p.title) + '</h1><p>' + prio(p.prio) + ' ' + lab(p) + ' <span class="muted small">' + esc(p.cat) + '</span></p>' +
      '<div class="note">' + md(p.provenance) + '<p class="small">' + p.sources.map((s) => s.url ? '<a href="' + esc(s.url.startsWith('../') ? (STATIC ? '../linkedin/' : '/workspace/') + s.url.slice(3) : s.url) + '" target="_blank" rel="noopener">' + esc(s.name) + '</a> <span class="muted">(' + esc(s.date) + ')</span>' : esc(s.name)).join(' · ') + '</p>' + ((p.leetcode || []).length ? '<p class="small"><b>LeetCode:</b></p><div class="lclist">' + lcRefs(p.leetcode, true) + '</div>' : '') + '</div>' +
      '<p><a class="btn" href="#/practice/' + p.id + '">Practice this</a> <a class="btn pri" href="#/mock/' + p.id + '">Mock interview</a>' +
      (p.solutionMd ? ' <a class="btn sol" href="#/solution/' + p.id + '">Solution</a>' : '') + '</p>' +
      p.learn.map((s, i) => '<details class="acc"' + (i < 3 ? ' open' : '') + '><summary>' + esc(s.title) + '</summary><div class="body md">' + md(s.md) + '</div></details>').join('') +
      (p.flaw ? '<details class="acc"><summary>Would you ship this? — verification exercise</summary><div class="body" id="lflaw"></div></details>' : '') +
      (p.csharp.length ? '<details class="acc"><summary>C# deep-dive — asked only if your solution uses it</summary><div class="body md">' +
        p.csharp.map((c) => '<h4>' + esc(c.feature) + '</h4>' + c.qa.map((x) => '<p><b>' + inline(esc(x.q)) + '</b><br>' + inline(esc(x.a)) + '</p>').join('')).join('') + '</div></details>' : '') +
      '<details class="acc"><summary>Stages and what the interviewer listens for</summary><div class="body md">' +
      p.stages.map((s, i) => '<h4>' + s.id + ' · ' + esc(s.title) + '</h4><p><i>"' + esc(s.say) + '"</i></p><p>' + inline(esc(s.require)) + '</p><ul>' + p.listen[i].map((x) => '<li>' + esc(x) + '</li>').join('') + '</ul>').join('') +
      '</div></details></div>';
    decorate(app);
    if (p.flaw) flawExercise($('#lflaw'), { ctx: p.flaw.ctx, code: p.flaw.code }, async (verdict, reason) => ({ answer: p.flaw.answer, fix: p.flaw.fix, kind: p.flaw.kind, correct: verdict === 'no' }));
  }

  function flawExercise(root, f, submit) {
    root.innerHTML = '<p>' + esc(f.ctx) + '</p>' + md('```csharp\n' + f.code + '\n```') +
      '<p><b>Would you ship this?</b></p><div class="filters"><button class="chip" data-v="yes">Ship it</button><button class="chip" data-v="no">Do not ship</button></div>' +
      '<textarea class="fld" placeholder="The defect, the input or interleaving that breaks it, and the fix. Decide before you reveal."></textarea>' +
      '<p style="margin-top:8px"><button class="btn pri">Submit my review</button></p><div class="res"></div>';
    decorate(root);
    let v = null;
    $$('.chip', root).forEach((c) => c.addEventListener('click', () => { v = c.dataset.v; $$('.chip', root).forEach((x) => x.classList.toggle('on', x === c)); }));
    $('.btn.pri', root).addEventListener('click', async () => {
      const reason = $('textarea', root).value.trim();
      if (!v || reason.length < 10) return toast('Choose ship / do not ship and write your reasoning first');
      $('.btn.pri', root).disabled = true;
      try {
        const r = await submit(v, reason);
        $('.res', root).innerHTML = '<div class="note ' + (r.correct ? 'good' : 'bad') + '"><b>' + (r.correct ? 'Right call — this should not ship.' : 'This had a real defect.') + '</b> <span class="tag lab single">' + esc(r.kind) + '</span>' +
          md(r.answer) + '<p><b>Fix.</b> ' + inline(esc(r.fix)) + '</p>' + (r.grade ? (r.grade.error ? '<p class="small">' + esc(r.grade.error) + '</p>' :
          '<p><b>Claude on your review:</b> ' + (r.grade.found_defect ? 'found the defect' : 'did not find the actual defect') + ' — ' + r.grade.score + '/10. ' + esc(r.grade.comment) + '</p>') : '') +
          (r.verified ? '<p class="small muted">' + esc(r.verified) + '</p>' : '') + '</div>';
      } catch (e) { toast(e.message); $('.btn.pri', root).disabled = false; }
    });
  }

  // ---------------------------------------------------------------- session setup
  function mockSetup(id) {
    setNav('bank');
    app.innerHTML = '<div class="page"></div>';
    modal('<h2>Mock interview</h2><p class="muted">No reference solution, no follow-ups revealed in advance. You explain your design before the AI unlocks. The interviewer reveals requirements as you go.</p>' +
      '<label>Time</label><div class="filters" id="tm">' + [30, 45, 60, 0].map((m) => '<button class="chip' + (m === 60 ? ' on' : '') + '" data-m="' + m + '">' + (m ? m + ' min' : 'Untimed') + '</button>').join('') + '</div>' +
      '<label><input type="checkbox" id="real"> CoderPad-realistic — Run only, no visible tests, as in the real pad. Hidden tests run silently when you say you are done; only the interviewer and the evaluation see them.</label>' +
      '<label><input type="checkbox" id="trap"> Verification training — some AI answers that contain code will carry one planted defect. You will be told which, afterwards.</label>' +
      '<p style="margin-top:14px"><button class="btn pri" id="go">Start</button> <a class="btn" href="#/bank">Cancel</a></p>', (bg, close) => {
      let mins = 60;
      $$('#tm .chip', bg).forEach((c) => c.addEventListener('click', () => { mins = +c.dataset.m; $$('#tm .chip', bg).forEach((x) => x.classList.toggle('on', x === c)); }));
      $('#go', bg).addEventListener('click', () => { close(); startSession(id, 'mock', mins, $('#trap', bg).checked, $('#real', bg).checked); });
    });
  }
  function simSetup() {
    setNav('sim');
    app.innerHTML = '<div class="page"><h1>LinkedIn Staff AI Coding — Full Simulation</h1>' +
      '<p class="lead">The closest thing to the real round. A P0 question you have practised least, hidden until you start. CoderPad-style workspace, C# only, Claude available. Sixty minutes on the clock.</p>' +
      dotnetNote() + claudeNote() +
      '<div class="card"><ul style="margin-left:20px"><li>No reference solution, no hints, no follow-ups shown in advance.</li><li>Explain your understanding and design before the assistant unlocks.</li>' +
      '<li>Requirements arrive one at a time; at least one concurrency and one scale or production follow-up.</li><li>Verification training is on: some AI answers carry a planted defect. You are told which at the end.</li>' +
      '<li><b>CoderPad-realistic:</b> a dark multi-file pad with AI Assist on the right, Run only — no visible tests. You test with your own code; hidden tests run silently for the interviewer.</li>' +
      '<li>When you finish (or time runs out), you get the full evaluation.</li></ul>' +
      '<p style="margin-top:12px"><button class="btn pri" id="go">Start the 60-minute simulation</button></p></div></div>';
    $('#go').addEventListener('click', () => startSession('surprise', 'sim', 60, true));
  }
  async function startSession(problemId, mode, mins, trap, realistic) {
    const r = await api('session/start', { body: { problemId, mode, mins, trap, realistic: !!realistic } });
    location.hash = '#/w/' + r.session.id;
  }

  window.SIM = { api, stream, md, decorate, esc, $, $$, toast, modal, withMonaco, prio, lab, fmt, inline, claudeNote, dotnetNote, setNav, sessionsTable, flawExercise,
                 status: () => STATUS, onCleanup: (f) => cleanup.push(f) };
  window.SIM_VIEWS = {};
  function workspace(id) { return window.SIM_VIEWS.workspace(id); }
  function report(id) { return window.SIM_VIEWS.report(id); }
  function verify() { return window.SIM_VIEWS.verify(); }
  function history() { return window.SIM_VIEWS.history(); }

  api('status').then((s) => {
    STATUS = s;
    const el = $('#status');
    el.className = 'pill ' + (s.static ? 'ok' : s.dotnet && s.claude ? 'ok' : s.dotnet ? 'warn' : 'bad');
    el.textContent = s.static ? 'Read-only · practice and mock run locally' : (s.dotnet ? 'C# ' + s.dotnet : 'C# off') + ' · ' + (s.claude ? 'Claude ' + s.model : 'Claude not configured');
    el.title = 'Session data: ' + s.dataDir;
  }).catch((e) => { $('#status').textContent = 'server error'; toast(e.message); }).finally(() => {
    if (STATIC) return route();                     // the website has no pad: draw the page straight away
    const s = document.createElement('script'); s.src = '/workspace.js';
    s.onload = () => { const p = document.createElement('script'); p.src = '/pad.js'; p.onload = route; document.body.appendChild(p); };
    document.body.appendChild(s);
  });
})();
