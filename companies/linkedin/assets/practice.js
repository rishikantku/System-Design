/* Practice runner. Dependency-free, like the rest of assets/.
 *
 * Assembles PRELUDE + types + your Solution + a generated harness into one C# program,
 * posts it to a relative /api/run, and renders the @@T lines the harness prints.
 * Your code is kept per problem in localStorage; nothing is sent anywhere until you Run.
 */
(function () {
  'use strict';
  if (typeof PROBLEMS === 'undefined') return;

  var KEY = 'lp.practice.v1';
  var host = document.getElementById('practice');
  if (!host) return;

  var state = load();
  var current = state.last && byId(state.last) ? state.last : PROBLEMS[0].id;
  var running = false;

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { return {}; }
  }
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* private mode */ }
  }
  function byId(id) {
    for (var i = 0; i < PROBLEMS.length; i++) if (PROBLEMS[i].id === id) return PROBLEMS[i];
    return null;
  }
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  /* ---------------------------------------------------------------- assemble */
  function program(p, code) {
    /* Design questions define their own class, so their code is not wrapped. */
    var body = p.wrap === false ? code
             : 'public class Solution {\n' + code + '\n}';
    return PRELUDE + '\n' + (p.types || '') + '\n' + body + '\n\n' +
      'public class Program {\n    public static void Main() {\n' +
      p.harness + '\n        H.Done();\n    }\n}\n';
  }

  /* The harness prints:  @@T|name|PASS|expected|actual|ms   and  @@S|passed|total  */
  function parse(stdout) {
    var cases = [], passed = 0, total = 0, junk = [];
    (stdout || '').split('\n').forEach(function (line) {
      if (line.indexOf('@@T|') === 0) {
        var f = line.slice(4).split('|');
        cases.push({ name: f[0], verdict: f[1], expected: f[2], actual: f[3], ms: f[4] });
      } else if (line.indexOf('@@S|') === 0) {
        var s = line.slice(4).split('|');
        passed = +s[0]; total = +s[1];
      } else if (line.trim()) {
        junk.push(line);
      }
    });
    return { cases: cases, passed: passed, total: total, printed: junk };
  }

  /* ---------------------------------------------------------------- render */
  function render() {
    var p = byId(current);
    var saved = (state.code || {})[current];
    var code = saved === undefined ? p.stub : saved;

    host.innerHTML =
      '<div class="pr-wrap">' +
        '<aside class="pr-list">' +
          '<div class="pr-list-h">Problems</div>' +
          PROBLEMS.map(function (q) {
            var st = (state.results || {})[q.id];
            var dot = st === 'pass' ? '<i class="pr-dot ok"></i>'
                    : st === 'fail' ? '<i class="pr-dot bad"></i>' : '<i class="pr-dot"></i>';
            return '<button class="pr-item' + (q.id === current ? ' on' : '') +
              '" data-go="' + q.id + '">' + dot +
              '<span><b>' + esc(q.title) + '</b>' +
              '<em>' + esc(q.chapter) + ' &middot; ' + esc(q.diff) + '</em></span></button>';
          }).join('') +
        '</aside>' +
        '<div class="pr-main">' +
          '<div class="pr-head">' +
            '<div><h3>' + esc(p.title) + '</h3>' +
              '<div class="pr-meta"><span class="tag lv">Lesson ' + esc(p.lesson) + '</span>' +
              '<span class="tag hi">' + esc(p.diff) + '</span>' +
              '<span class="pr-ev">' + esc(p.evidence) + '</span></div>' +
            '</div>' +
            '<div class="pr-links">' + leetLink(p) + videoLink(p) + '</div>' +
          '</div>' +
          '<div class="pr-statement">' + p.statement +
            '<details class="pr-hint"><summary>Hint</summary><div>' + esc(p.hint) + '</div></details>' +
          '</div>' +
          '<div class="pr-bar">' +
            '<button class="pr-run" id="pr-run">Run tests <kbd>&#8984;&#8629;</kbd></button>' +
            '<button class="pr-reset" id="pr-reset">Reset code</button>' +
            '<span class="pr-engine" id="pr-engine"></span>' +
          '</div>' +
          '<textarea class="pr-code" id="pr-code" spellcheck="false" wrap="off"></textarea>' +
          '<div class="pr-out" id="pr-out"><div class="pr-idle">Write your solution, then Run. ' +
            'The tests include the edge cases the lesson calls out.</div></div>' +
        '</div>' +
      '</div>';

    document.getElementById('pr-code').value = code;
    probeEngine();
  }

  /* LeetCode is where you can run these anywhere. Exact matches link straight
     through; near relatives say so rather than pretending to be the same question. */
  function leetLink(p) {
    var lc = p.lc || {};
    if (lc.url) {
      var label = lc.exact ? 'Run on LeetCode ' + lc.num : 'LeetCode ' + lc.num + ' (closest)';
      return '<a class="pr-lc" href="' + lc.url + '" target="_blank" rel="noopener" title="' +
             esc(lc.note || 'Opens on LeetCode, where you can run it against their judge') +
             '">' + label + ' \u2197</a>';
    }
    if (lc.note) return '<span class="pr-lc none" title="' + esc(lc.note) + '">not on LeetCode</span>';
    return '';
  }

  /* The built videos are ~5 GB and deliberately not in git, so they exist only
     on the machine that built them. Offer the link there, and say so elsewhere. */
  function videoLink(p) {
    var local = location.hostname === 'localhost' || location.hostname === '127.0.0.1';
    if (local) {
      return '<a class="pr-vid" href="../../video/build-coding/' + p.video +
             '" target="_blank" rel="noopener">Watch lesson &rarr;</a>';
    }
    return '<span class="pr-vid off" title="The lesson videos are not deployed - ' +
           'run the workspace locally, or watch them on YouTube">Lesson ' + esc(p.lesson) +
           ' (local only)</span>';
  }

  /* ---------------------------------------------------------------- engine probe */
  function probeEngine() {
    var el = document.getElementById('pr-engine');
    if (!el) return;
    el.className = 'pr-engine';
    el.innerHTML = 'Runs on your machine via <code>python3 companies/linkedin/runner.py</code>. ' +
                   'Anywhere else, use the LeetCode link.';
  }

  function showEngine(r) {
    var el = document.getElementById('pr-engine');
    if (!el) return;
    var name = r.engine || 'unknown';
    if (r.dialect === 'csharp7') {
      el.className = 'pr-engine warn';
      el.innerHTML = 'engine: ' + esc(name) +
        ' &mdash; <b>C# 7.0 only</b>. <code>is not null</code>, <code>new()</code> and switch ' +
        'expressions will not compile here. Run locally for modern C#.';
    } else {
      el.className = 'pr-engine ok';
      el.textContent = 'engine: ' + name;
    }
  }

  /* ---------------------------------------------------------------- run */
  function run() {
    if (running) return;
    var p = byId(current);
    var code = document.getElementById('pr-code').value;
    var out = document.getElementById('pr-out');
    var btn = document.getElementById('pr-run');

    state.code = state.code || {};
    state.code[current] = code;
    save();

    running = true;
    btn.disabled = true;
    btn.textContent = 'Running…';
    out.innerHTML = '<div class="pr-idle">Compiling… the first run after a change takes a second.</div>';

    var t0 = Date.now();
    fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ program: program(p, code), problem: p.id })
    })
      .then(function (r) { return r.json().catch(function () { throw new Error('runner returned non-JSON (status ' + r.status + ')'); }); })
      .then(function (r) { show(r, Date.now() - t0); })
      .catch(function (e) {
        var lc = (byId(current) || {}).lc || {};
        out.innerHTML = '<div class="pr-err"><b>No local runner</b>' +
          '<p>Code runs on your own machine, not on the deployed site. Start it with ' +
          '<code>python3 companies/linkedin/runner.py</code> and open the localhost URL it prints.' +
          (lc.url ? ' Or <a href="' + lc.url + '" target="_blank" rel="noopener">run it on LeetCode</a>.' : '') +
          '</p></div>';
      })
      .then(function () {
        running = false;
        btn.disabled = false;
        btn.innerHTML = 'Run tests <kbd>&#8984;&#8629;</kbd>';
      });
  }

  function show(r, wallMs) {
    var out = document.getElementById('pr-out');
    showEngine(r);

    if (r.stage === 'compile') {
      out.innerHTML = '<div class="pr-err"><b>Compile error</b><pre>' +
        esc(r.compile_output || 'unknown') + '</pre></div>';
      mark('fail');
      return;
    }
    if (r.stage === 'request' || r.stage === 'engine') {
      out.innerHTML = '<div class="pr-err"><b>Runner problem</b><pre>' +
        esc(r.stderr || 'unknown') + '</pre></div>';
      return;
    }
    if (r.timeout) {
      out.innerHTML = '<div class="pr-err"><b>Timed out</b><p>' +
        esc(r.stderr || 'Probably an infinite loop.') + '</p></div>';
      mark('fail');
      return;
    }

    var res = parse(r.stdout);
    if (!res.cases.length) {
      out.innerHTML = '<div class="pr-err"><b>No test output</b>' +
        (r.stderr ? '<pre>' + esc(r.stderr) + '</pre>' : '') +
        '<p>Your method probably threw before the first case, or the signature does not match the stub.</p></div>';
      mark('fail');
      return;
    }

    var allPass = res.passed === res.total;
    var html = '<div class="pr-sum ' + (allPass ? 'ok' : 'bad') + '">' +
      '<b>' + res.passed + ' / ' + res.total + ' passed</b>' +
      '<span>' + (r.ms || wallMs) + ' ms total' +
      (r.compile_ms ? ' &middot; ' + r.compile_ms + ' ms compiling' : '') + '</span></div>';

    html += '<table class="pr-tab"><thead><tr><th></th><th>Case</th><th>Expected</th>' +
            '<th>Got</th><th>ms</th></tr></thead><tbody>';
    res.cases.forEach(function (c) {
      var cls = c.verdict === 'PASS' ? 'ok' : (c.verdict === 'ERROR' ? 'err' : 'bad');
      var icon = c.verdict === 'PASS' ? '✓' : (c.verdict === 'ERROR' ? '!' : '✗');
      html += '<tr class="' + cls + '"><td class="pr-ic">' + icon + '</td>' +
        '<td>' + esc(c.name) + '</td>' +
        '<td><code>' + esc(c.expected) + '</code></td>' +
        '<td><code>' + esc(c.actual) + '</code></td>' +
        '<td>' + esc(c.ms || '') + '</td></tr>';
    });
    html += '</tbody></table>';

    if (res.printed.length) {
      html += '<details class="pr-print"><summary>Your output (' + res.printed.length +
              ' line' + (res.printed.length === 1 ? '' : 's') + ')</summary><pre>' +
              esc(res.printed.join('\n')) + '</pre></details>';
    }
    if (r.stderr) {
      html += '<details class="pr-print"><summary>stderr</summary><pre>' + esc(r.stderr) + '</pre></details>';
    }

    out.innerHTML = html;
    mark(allPass ? 'pass' : 'fail');
  }

  function mark(verdict) {
    state.results = state.results || {};
    state.results[current] = verdict;
    save();
    var item = host.querySelector('.pr-item[data-go="' + current + '"] .pr-dot');
    if (item) item.className = 'pr-dot ' + (verdict === 'pass' ? 'ok' : 'bad');
  }

  /* ---------------------------------------------------------------- events */
  host.addEventListener('click', function (e) {
    var go = e.target.closest('[data-go]');
    if (go) {
      var code = document.getElementById('pr-code');
      if (code) { state.code = state.code || {}; state.code[current] = code.value; }
      current = go.getAttribute('data-go');
      state.last = current;
      save();
      render();
      return;
    }
    if (e.target.closest('#pr-run')) run();
    if (e.target.closest('#pr-reset')) {
      var p = byId(current);
      if (confirm('Replace your code with the original stub?')) {
        document.getElementById('pr-code').value = p.stub;
        state.code = state.code || {};
        state.code[current] = p.stub;
        save();
      }
    }
  });

  document.addEventListener('keydown', function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') { e.preventDefault(); run(); }
  });

  /* Tab indents instead of leaving the editor - non-negotiable in a code box. */
  host.addEventListener('keydown', function (e) {
    if (e.target.id !== 'pr-code' || e.key !== 'Tab') return;
    e.preventDefault();
    var t = e.target, s = t.selectionStart, en = t.selectionEnd;
    t.value = t.value.slice(0, s) + '    ' + t.value.slice(en);
    t.selectionStart = t.selectionEnd = s + 4;
  });

  render();
})();
