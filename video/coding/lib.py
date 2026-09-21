# -*- coding: utf-8 -*-
"""Lesson scaffolding for the LinkedIn coding video course.

Each lesson is its own short video, built with the same slide engine as the
Isolated Cloud course (../src/engine.py). This module adds:
  - a lesson header slide carrying the research provenance
  - the fixed 18-beat lesson shape, as helpers
  - visual helpers: arrays, trees, graphs, tables, pointer animation
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'src'))

import engine as E
E.BRAND = 'LinkedIn coding course &middot; Staff prep'
from engine import (new_slide, seg, cards, compare, table, statement, steps_list,
                    quote_slide, question, Diagram, travel, rich, esc, W, KIND)

# ------------------------------------------------------------------ lesson header
def lesson_header(num, title, pattern, relevance, reports, latest, confidence, mins, narration):
    """Opening slide: what this lesson is, and why it is in the course."""
    rel_cls = {'Highest': 'ok', 'High': 'ok', 'Medium': 'shared', 'Lower': 'com'}.get(relevance, 'info')
    rows = [('LinkedIn relevance', relevance, rel_cls),
            ('Reported', reports, 'info'),
            ('Latest report', latest, 'info'),
            ('Pattern', pattern, 'dp'),
            ('Confidence', confidence, rel_cls)]
    meta = ''.join(
        '<div class="lh-row"><span class="lh-k">%s</span><span class="lh-v k-%s">%s</span></div>' % (esc(k), c, esc(v))
        for k, v, c in rows)
    inner = ('<div class="lhead"><div class="lh-num">Lesson %s · %s min</div>'
             '<h1 class="lh-t">%s</h1><div class="lh-meta">%s</div></div>') % (esc(num), mins, esc(title), meta)
    sid = new_slide(inner, cls='lesson-head')
    seg(sid, 0, narration, kind='chapter', tail=1.0)
    return sid

def beat(label, title, body_html, narration, kicker=None, step=0):
    """One numbered beat of the lesson (QUESTION, KEY OBSERVATION, …)."""
    sid = new_slide(body_html, title=title, kicker=kicker or label)
    seg(sid, step, narration)
    return sid

def think(prompt, secs, narration_before, narration_after):
    """Interview simulation: the question, then a timed pause, then the resume line."""
    sid = new_slide(
        '<div class="qwrap"><div class="qlabel">Interviewer</div>'
        '<div class="qtext">&ldquo;%s&rdquo;</div>'
        '<div class="think" data-step="1"><div class="thinkl">Take a moment. Say your first approach out loud.</div>'
        '<div class="thinkbar"><i></i></div><div class="thinkc"></div></div></div>' % rich(prompt),
        kicker='Pause and think')
    seg(sid, 0, narration_before)
    seg(sid, 1, '', kind='think', think=secs)
    seg(sid, 2, narration_after) if narration_after else None
    return sid

def code_slide(title, code_text, narration_blocks, kicker='C# implementation', max_lines=17):
    """Code on screen, narrated in blocks. narration_blocks: list of (highlight_lines|None, text).

    A listing longer than max_lines is split across consecutive slides at a narration-block
    boundary, keeping the original line numbers so the highlight ranges still line up.
    Shrinking a 37-line listing to fit one 1080p slide makes it unreadable on a phone.
    """
    lines = code_text.strip('\n').split('\n')
    pages = _paginate(narration_blocks, len(lines), max_lines)
    first = None
    for n, (lo, hi, blocks) in enumerate(pages):
        html = ['<div class="codebox"><pre class="cl">']
        for i in range(lo, hi + 1):
            html.append('<span class="ln" data-l="%d">%s</span>' % (i, _hl(lines[i - 1]) or '&nbsp;'))
        html.append('</pre></div>')
        t = title if n == 0 else title + ' &mdash; continued'
        sid = new_slide(''.join(html), title=t, kicker=kicker, cls='codeslide')
        first = first or sid
        for step, (rng, text) in enumerate(blocks):
            seg(sid, step, text)
        _apply_line_steps(sid, blocks)
    return first

def _paginate(blocks, n_lines, max_lines):
    """[(first_line, last_line, blocks)] - split only at block boundaries."""
    if n_lines <= max_lines:
        return [(1, n_lines, list(blocks))]
    pages, cur, lo, hi = [], [], 1, 0
    for rng, text in blocks:
        top = max(_expand(rng)) if rng else hi
        if cur and top - lo + 1 > max_lines:
            pages.append((lo, hi, cur))
            lo, cur = hi + 1, []
        cur.append((rng, text))
        hi = max(hi, top, lo - 1)
    pages.append((lo, n_lines, cur))
    return pages

def _hl(line):
    """Tiny C# highlighter. Comments and strings are split out first so the
    keyword pass can never rewrite markup it just inserted."""
    import re, html as H
    KW = (r'\b(public|private|protected|internal|static|readonly|const|class|struct|record|interface|var|new|return|if|else|'
          r'for|foreach|while|do|switch|case|break|continue|int|long|double|bool|string|char|void|null|true|false|using|'
          r'namespace|try|catch|finally|throw|lock|async|await|yield|in|out|ref|is|as|this|base|get|set|override|sealed|'
          r'virtual|abstract|default|when|where)\b')
    TY = (r'\b(List|Dictionary|HashSet|Queue|Stack|PriorityQueue|LinkedList|SortedSet|SortedList|StringBuilder|Math|'
          r'TreeNode|Node|IList|IEnumerable|IReadOnlyList|IDictionary|Array|Random|Exception|ArgumentException|'
          r'InvalidOperationException|Task|CancellationToken|Func|Action|Tuple|KeyValuePair|Comparer|IComparer)\b')

    s = H.escape(line, quote=False)
    code, comment = s, ''
    i = s.find('//')
    if i >= 0:
        code, comment = s[:i], s[i:]

    out = []
    for part in re.split(r'(&quot;.*?&quot;)', code):
        if part.startswith('&quot;'):
            out.append('<i class="cs">%s</i>' % part)
            continue
        part = re.sub(KW, r'<i class="ck">\1</i>', part)      # keywords first
        part = re.sub(TY, r'<i class="ct">\1</i>', part)      # then types (no overlap with markup)
        out.append(part)
    res = ''.join(out)
    if comment:
        res += '<i class="cc">%s</i>' % comment
    return res

def _apply_line_steps(sid, blocks):
    """Rewrite the stored slide html so each line knows at which step it lights up."""
    idx = next(i for i, (s, _) in enumerate(E.SLIDES) if s == sid)
    slide_id, html = E.SLIDES[idx]
    for step, (rng, _) in enumerate(blocks):
        if not rng: continue
        for ln in _expand(rng):
            html = html.replace('data-l="%d"' % ln, 'data-l="%d" data-hl="%d"' % (ln, step), 1)
    E.SLIDES[idx] = (slide_id, html)

def _expand(rng):
    out = []
    for part in str(rng).split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-'); out += list(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out

# ------------------------------------------------------------------ visuals
def array_row(D, values, x=120, y=200, cw=130, ch=96, step=0, ids=None, kind='info', labels=True):
    """Draw an array as a row of cells. Returns the list of box ids."""
    made = []
    for i, v in enumerate(values):
        bid = (ids[i] if ids else 'a%d' % i)
        D.box(bid, x + i * (cw + 10), y, cw, ch, str(v), '', kind=kind, step=step, small=True)
        if labels:
            D.label(x + i * (cw + 10), y + ch + 8, str(i), kind='neutral', step=step, w=cw, size='s', align='center')
        made.append(bid)
    return made

def hl_cells(D, ids, x=120, y=200, cw=130, ch=96, marks=None, kind='ok'):
    """Overlay highlight frames on chosen cells at chosen steps.
       marks: {index: 'step' or 'step1,step2'}"""
    for i, steps in (marks or {}).items():
        D.box('hl%d' % i, x + i * (cw + 10) - 4, y - 4, cw + 8, ch + 8, '', '', kind=kind,
              step=0, hl=str(steps), small=True)

def pointer(D, name, index, x=120, y=200, cw=130, step=0, above=True, kind='shared', label='l'):
    """A labelled pointer under or over an array cell."""
    px = x + index * (cw + 10) + cw // 2 - 40
    py = y - 70 if above else y + 130
    D.label(px, py, ('▼ ' if above else '▲ ') + label, kind=kind, step=step, w=80, size='m', align='center')

def tree(D, nodes, edges, x=960, y=120, dx=200, dy=140, step=0, kind='dp',
         node_w=96, node_h=72, hls=None):
    """nodes: {id: (depth, offset, text)}; hls: {id: 'step' or 'step1,step2'}.
    Highlighting is applied to the node itself, so it never covers the label."""
    pos = {}
    for nid, (depth, off, text) in nodes.items():
        cx = x + int(off * dx)
        cy = y + depth * dy
        D.box(nid, cx - node_w // 2, cy, node_w, node_h, str(text), '', kind=kind, step=step,
              small=True, hl=(str((hls or {}).get(nid)) if (hls or {}).get(nid) is not None else None))
        pos[nid] = (cx, cy + node_h // 2)
    for a, b in edges:
        D.arrow(a, b, step=step, kind='neutral', fs='b', ts='t')
    return pos

def node_hl(*_args, **_kw):
    """Deprecated: pass hls={} to tree() instead. Kept so older lessons still import."""
    return None

def graph(D, nodes, edges, step=0, kind='dp', node_w=150, node_h=74):
    """nodes: {id: (x, y, text)}; edges: [(a,b)] — free positioning for graph animations."""
    for nid, (nx, ny, text) in nodes.items():
        D.box(nid, nx, ny, node_w, node_h, str(text), '', kind=kind, step=step, small=True)
    for a, b in edges:
        D.arrow(a, b, step=step, kind='neutral')

def kv_table(D, title, rows, x=120, y=200, w=760, rh=70, step=0, kind='info'):
    """A small key/value panel used for hash maps and DP state."""
    D.label(x, y - 50, '**%s**' % title, kind=kind, step=step, w=w, size='m')
    for i, (k, v) in enumerate(rows):
        D.box('kv%d' % i, x, y + i * rh, w // 2, rh - 8, str(k), '', kind=kind, step=step, small=True)
        D.box('vv%d' % i, x + w // 2 + 10, y + i * rh, w // 2, rh - 8, str(v), '', kind='ok', step=step, small=True)

# ------------------------------------------------------------------ closers
def followups(reported, staff, narration_reported, narration_staff):
    """Two-column follow-up slide: what was actually reported vs what a staff interviewer may add."""
    sid = compare('Follow-ups',
                  ('Reported follow-ups', 'ok', 0, reported),
                  ('Possible staff-level follow-ups', 'shared', 1, staff))
    seg(sid, 0, narration_reported)
    seg(sid, 1, narration_staff)
    return sid

def interview_script(lines, narration):
    """'How I should respond in the interview' — the verbal script.
    Lines are spread evenly across however many narration blocks are supplied."""
    groups = max(1, len(narration))
    per = -(-len(lines) // groups)                      # ceiling division
    items = [(min(i // per, groups - 1), l, 'ok') for i, l in enumerate(lines)]
    sid = steps_list('How to say it in the interview', items, numbered=False)
    for step, text in enumerate(narration):
        seg(sid, step, text)
    return sid
