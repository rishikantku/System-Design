# -*- coding: utf-8 -*-
"""Builder for the LinkedIn Staff full-loop prep workspace."""
import html as H, re, json, os, datetime

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # companies/linkedin
TODAY = datetime.date(2026, 9, 21)

# ---------------------------------------------------------------- manifest
MANIFEST = {'rounds': {}, 'research': {}, 'built': TODAY.isoformat()}

def reg(round_id, item_id, topic, label, weight=1, kind='item', level=''):
    r = MANIFEST['rounds'].setdefault(round_id, {'title': round_id, 'items': []})
    r['items'].append({'id': item_id, 'topic': topic, 'label': label,
                       'weight': weight, 'kind': kind, 'level': level})
    return item_id

def esc(s): return H.escape(str(s), quote=False)

def rich(s):
    """**bold**, `code`, [text](url) -> html"""
    s = esc(s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    # allow a tiny inline whitelist to survive escaping
    for tag_ in ('b', 'i', 'br', 'code', 'small'):
        s = s.replace('&lt;%s&gt;' % tag_, '<%s>' % tag_).replace('&lt;/%s&gt;' % tag_, '</%s>' % tag_)
    return s

# ---------------------------------------------------------------- code
CS_KW = r'\b(public|private|protected|internal|static|readonly|const|class|struct|interface|enum|record|sealed|abstract|virtual|override|new|return|if|else|for|foreach|while|do|switch|case|break|continue|var|void|int|long|double|bool|string|char|decimal|true|false|null|using|namespace|try|catch|finally|throw|lock|async|await|Task|yield|in|out|ref|is|as|this|base|get|set|where|default|nameof|when)\b'
CS_TY = r'\b(List|Dictionary|HashSet|Queue|Stack|IEnumerable|IEnumerator|IList|IDictionary|SortedSet|SortedDictionary|LinkedList|LinkedListNode|PriorityQueue|Span|Memory|StringBuilder|Array|Math|Console|Exception|ArgumentException|InvalidOperationException|CancellationToken|ConcurrentDictionary|SemaphoreSlim|ReaderWriterLockSlim|Interlocked|Volatile|Channel|ValueTask|HttpClient|JsonSerializer|Guid|DateTime|TimeSpan|Random|Comparer|IComparer|Func|Action|Tuple|KeyValuePair|Stopwatch|Lazy|Nullable|Regex|Encoding|Convert|Enumerable)\b'

def code(src, lang='csharp', file=None):
    s = esc(src.strip('\n'))
    holes, out = [], s
    def stash(text):
        holes.append(text); return '\x00%d\x00' % (len(holes) - 1)
    out = re.sub(r'//[^\n]*', lambda m: stash('<span class="c">%s</span>' % m.group(0)), out)
    out = re.sub(r'&quot;(?:[^&]|&(?!quot;))*?&quot;', lambda m: stash('<span class="s">%s</span>' % m.group(0)), out)
    if lang == 'csharp':
        out = re.sub(CS_TY, lambda m: '<span class="t">%s</span>' % m.group(0), out)
        out = re.sub(CS_KW, lambda m: '<span class="k">%s</span>' % m.group(0), out)
    out = re.sub(r'\b(\d+)\b', lambda m: '<span class="n">%s</span>' % m.group(0), out)
    out = re.sub(r'\x00(\d+)\x00', lambda m: holes[int(m.group(1))], out)
    head = '<div class="code-h"><span class="fn">%s</span></div>' % esc(file) if file else ''
    return head + '<div class="code">%s</div>' % out

# ---------------------------------------------------------------- blocks
def tags(*items):
    """items: (cls, text)"""
    return '<div class="tags">' + ''.join('<span class="tag %s">%s</span>' % (c, esc(t)) for c, t in items) + '</div>'

def tag(cls, text): return '<span class="tag %s">%s</span>' % (cls, esc(text))

def note(body, kind='', label=None):
    l = '<span class="lbl">%s</span>' % esc(label) if label else ''
    return '<div class="note %s">%s%s</div>' % (kind, l, rich(body))

def card(body, cls='', title=None, id=None):
    t = '<h3>%s</h3>' % rich(title) if title else ''
    i = ' id="%s"' % id if id else ''
    return '<div class="card %s"%s>%s%s</div>' % (cls, i, t, body)

def grid(items, cols='g2'):
    return '<div class="grid %s">%s</div>' % (cols, ''.join(items))

def table(headers, rows, cls=''):
    th = ''.join('<th>%s</th>' % esc(h) for h in headers)
    tr = ''
    for r in rows:
        tr += '<tr>' + ''.join('<td>%s</td>' % rich(c) for c in r) + '</tr>'
    return '<div class="tw"><table class="%s"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (cls, th, tr)

def sec(id, title, body, kicker=None, why=None):
    k = '<span class="kicker">%s</span>' % esc(kicker) if kicker else ''
    w = '<span class="why">%s</span>' % rich(why) if why else ''
    head = '<div class="sec-h"><div>%s<h2 id="%s">%s</h2></div>%s</div>' % (k, id, esc(title), w)
    return '<section class="sec" id="sec-%s">%s%s</section>' % (id, head, body)

def acc(summary, body, meta_tags='', open=False, raw=False):
    return ('<details class="acc"%s><summary><span class="sq">%s</span>'
            '<span class="rt-tags">%s</span></summary><div class="body">%s</div></details>') % (
        ' open' if open else '', summary if raw else rich(summary), meta_tags, body)

def titled(name, sub):
    """accordion title with a dimmed sub-label, pre-escaped"""
    return '<b>%s</b> <span class="src">· %s</span>' % (esc(name), esc(sub))

def senior_staff(senior, staff):
    return ('<div class="senior-staff"><div class="sr"><div class="h">A senior engineer might say</div>%s</div>'
            '<div class="sf"><div class="h">A staff engineer should be thinking</div>%s</div></div>') % (rich(senior), rich(staff))

# ---------------------------------------------------------------- tracker
STATUSES = [('solved', 'Solved'), ('revise', 'Needs revision'), ('failed', 'Failed'),
            ('slow', 'Time exceeded'), ('hint', 'Hint used')]
DONE_STATUSES = [('done', 'Done'), ('revise', 'Needs revision')]

def tracker(item_id, statuses=STATUSES, note_ph='Notes: what tripped you up, what to redo…'):
    btns = ''.join('<button class="sbtn" data-st="%s">%s</button>' % (k, v) for k, v in statuses)
    stars = ''.join('<b>★</b>' for _ in range(5))
    return ('<div class="track"><span class="lbl">Status</span>%s'
            '<span class="lbl" style="margin-left:8px">Confidence</span><span class="conf">%s</span>'
            '<span class="tstamp count" style="margin-left:auto"></span>'
            '<textarea class="tnote" placeholder="%s"></textarea></div>') % (btns, stars, esc(note_ph))

def stage(label, body, hint=''):
    h = '<span class="hint">%s</span>' % esc(hint) if hint else ''
    return ('<div class="stage"><div class="sh"><span class="st">%s</span>%s</div>'
            '<div class="sb">%s</div></div>') % (esc(label), h, body)

def practice(item_id, title, stages, meta_tags='', label=None, statuses=STATUSES, open=False, raw=True):
    body = ('<div class="revall"><button class="sbtn" data-revall>Reveal all</button></div>'
            + ''.join(stages) + tracker(item_id, statuses))
    inner = '<div data-id="%s" data-label="%s">%s</div>' % (item_id, esc(label or title), body)
    return acc(title, inner, meta_tags, open, raw=raw)

def mock_block(item_id, question, round_name, rubric, secs=300, extra=''):
    return ('<div class="mock" data-id="%s" data-mock data-q="%s" data-label="%s" data-timer="%d">'
            '<span class="kicker">Mock · one question at a time</span>'
            '<div class="mq">%s</div>'
            '<div class="bar-row"><span class="timer"></span>'
            '<button class="sbtn" data-t-start>▶ Start</button>'
            '<button class="sbtn" data-t-reset>Reset</button>'
            '<button class="sbtn" data-copy="grade">📋 Grade this with Claude</button></div>'
            '<textarea class="tnote" placeholder="Answer out loud first. Jot the key points you actually said…"></textarea>'
            '%s'
            '<details class="acc"><summary><span class="sq">Show what a strong answer must contain</span></summary>'
            '<div class="body"><ul class="rub">%s</ul>'
            '<div class="bar-row"><span class="lbl">Self-score</span>'
            '<select data-score class="sbtn"><option value="">Score…</option>%s</select></div></div></details>'
            '</div>') % (item_id, esc(question), esc(question[:70]), secs, rich(question), extra,
                         ''.join('<li>%s</li>' % rich(r) for r in rubric),
                         ''.join('<option value="%d">%d/10</option>' % (i, i) for i in range(1, 11)))

# ---------------------------------------------------------------- page shell
ROUNDS = [('coding', '01', 'Staff Coding', '01-coding.html'),
          ('ai', '02', 'Coding with AI', '02-ai-coding.html'),
          ('design', '03', 'Systems &amp; Infra Design', '03-system-design.html'),
          ('hm', '04', 'Host Leader', '04-hiring-manager.html')]

def page(filename, title, subtitle, body, round_id='', round_name='', crumb_tail='',
         hero_chips=None, nav_html='', autonav=True, extra_head='', tail_js='',
         tail_scripts=None):
    chips = ''.join('<span class="chip %s">%s</span>' % (c, esc(t)) for c, t in (hero_chips or []))
    nav_links = ''.join(
        '<a href="%s"%s>%s %s</a>' % (f, ' class="on"' if r == round_id else '', n, t)
        for r, n, t, f in ROUNDS)
    auto = '<h4>On this page</h4><input class="navfilter" placeholder="Filter sections  /"><div id="autonav"></div>' if autonav else ''
    crumb = ('<a href="../../index.html">Interview prep</a> › <a href="../index.html">Companies</a> › '
             '<a href="index.html">LinkedIn</a>')
    if crumb_tail: crumb += ' › <b>%s</b>' % esc(crumb_tail)
    doc = f'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · LinkedIn Staff prep</title>
<meta name="description" content="{esc(subtitle)}">
<link rel="stylesheet" href="assets/prep.css">{extra_head}
</head>
<body data-round="{round_id}" data-round-name="{esc(round_name)}">
<div class="top"><div class="top-in">
  <button class="burger" aria-label="Menu">☰</button>
  <a class="brand" href="index.html"><span class="in">in</span> Staff loop</a>
  <div class="crumb">{crumb}</div>
  <div class="top-sp"></div>
  <a class="tbtn" href="../../specialization-aic.html">AIC retrospective</a>
  <a class="tbtn" href="../../index.html">Design guide</a>
</div></div>
<div class="shell">
<nav class="side" id="side">
  <h4>LinkedIn loop</h4>
  <a href="index.html"{' class="on"' if not round_id else ''}>◆ Dashboard</a>
  {nav_links}
  {nav_html}
  {auto}
  <h4>Course</h4>
  <a href="06-coding-course.html">◆ Video coding course</a>
  <a href="07-practice.html">◆ Code practice</a>
  <a href="08-worked-questions.html">◆ Worked questions</a>
  <h4>Research</h4>
  <a href="05-research.html">◆ Recent interview research</a>
  <h4>Data</h4>
  <a href="#" data-export>Copy progress JSON</a>
  <a href="#" data-reset>Reset progress</a>
</nav>
<div class="backdrop"></div>
<main class="main">
<div class="hero">
  <span class="kicker" style="color:#8ec5ff">{esc(crumb_tail or 'LinkedIn')}</span>
  <h1>{esc(title)}</h1>
  <p class="sub">{rich(subtitle)}</p>
  {'<div class="chips">' + chips + '</div>' if chips else ''}
</div>
{body}
<div class="foot">Built from your own prep material plus public interview reports · research last updated {TODAY.strftime('%d %B %Y')} ·
progress is stored in this browser only.</div>
</main></div>
<script src="assets/manifest.js"></script>
<script src="assets/prep.js"></script>
{''.join('<script src="%s"></script>' % s for s in (tail_scripts or []))}
{('<script>' + tail_js + '</script>') if tail_js else ''}
</body></html>'''
    with open(os.path.join(OUT, filename), 'w', encoding='utf-8') as f:
        f.write(doc)
    return filename

import research as R

def official_module(mid):
    m = next(x for x in R.OFFICIAL_MODULES if x['id'] == mid)
    ex = ''
    if m['example']:
        ex = ('<h4>The example question printed in the pack</h4>'
              '<div class="note good"><span class="lbl">%s</span>%s<ul>%s</ul></div>' % (
                  esc(m['example']['title']), rich(m['example']['prompt']),
                  ''.join('<li>%s</li>' % rich(x) for x in m['example']['subs'])))
    return card(
        '<p class="lead">%s</p>'
        '<h4>What they evaluate</h4><ul>%s</ul>'
        '<h4>What to expect</h4><ul>%s</ul>'
        '<h4>How to run it</h4><ul>%s</ul>%s'
        '<div class="src">Source: %s · %s</div>' % (
            rich(m['what']),
            ''.join('<li>%s</li>' % rich(x) for x in m['evaluated']),
            ''.join('<li>%s</li>' % rich(x) for x in m['expect']),
            ''.join('<li>%s</li>' % rich(x) for x in m['how']), ex,
            esc(R.OFFICIAL_SRC), esc(R.OFFICIAL_DATE)),
        title='%s · %d minutes%s' % (m['name'], m['mins'], ' · AI assisted' if m['ai'] else ''))

def write_manifest(research_summary):
    MANIFEST['research'] = research_summary
    for rid, num, name, fn in ROUNDS:
        if rid in MANIFEST['rounds']:
            MANIFEST['rounds'][rid]['title'] = name
            MANIFEST['rounds'][rid]['file'] = fn
    js = 'window.LP_MANIFEST = %s;\n' % json.dumps(MANIFEST, separators=(',', ':'))
    with open(os.path.join(OUT, 'assets/manifest.js'), 'w', encoding='utf-8') as f:
        f.write(js)
    return len(js)
