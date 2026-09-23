# -*- coding: utf-8 -*-
"""Scaffolding for the system design course.

Same slide engine as the coding course, different blocks: this course is about
reasoning and communication, so the recurring units are

    evidence      where the question actually comes from, stated honestly
    clarify       the questions to ask before designing anything
    capacity      assumption -> calculation -> result -> architectural implication
    arch          one architecture built up in levels, highlighting what is being discussed
    tradeoff      option A / option B / what I chose / what would flip it
    failures      component dies -> what the user sees -> what the system does
    say           WHAT I SHOULD SAY - the sentence to speak at that moment
    cheatsheet    the one-page revision card

The brief for this course asked for an interviewer that waits for spoken answers and
grades them. A rendered video cannot do that, so it does not pretend to: `think()`
poses the question and pauses, and the grading lives in the workspace's mock mode.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', 'src')))

import engine as E
E.BRAND = 'LinkedIn system design &middot; Staff prep'
from engine import (new_slide, seg, quote_slide, Diagram, travel, chapter, rich, esc)
from engine import (cards as _e_cards, compare as _e_compare, table as _e_table,
                    statement as _e_statement, steps_list as _e_steps_list)

W = 1920


_ENT = {'&bull;': '\u2022', '&larr;': '\u2190', '&rarr;': '\u2192', '&mdash;': '\u2014',
        '&ndash;': '\u2013', '&times;': '\u00d7', '&asymp;': '\u2248', '&middot;': '\u00b7',
        '&le;': '\u2264', '&ge;': '\u2265', '&divide;': '\u00f7', '&hellip;': '\u2026',
        '&amp;': '&', '&lt;': '<', '&gt;': '>', '&nbsp;': ' ',
        '&ldquo;': '\u201c', '&rdquo;': '\u201d', '&micro;': '\u00b5'}


def _plain(s):
    """Diagram text: entities become real characters so they survive rich()'s escaping."""
    s = str(s)
    for k, v in _ENT.items():
        s = s.replace(k, v)
    return s



def _md(s):
    """engine.rich() escapes everything and understands only **bold** and `mono`.
    These lessons author HTML, so translate it into what rich() can render."""
    import re as _re
    s = _plain(s)
    s = _re.sub(r'<b>(.*?)</b>', r'**\1**', s, flags=_re.S)
    s = _re.sub(r'<code>(.*?)</code>', r'`\1`', s, flags=_re.S)
    s = _re.sub(r'<i>(.*?)</i>', r'\1', s, flags=_re.S)
    s = s.replace('<br>', ' ').replace('<br/>', ' ')
    return s


def cards(title, items, **kw):
    return _e_cards(title, [(it[0], _md(it[1]), _md(it[2])) + tuple(it[3:]) for it in items], **kw)


def compare(title, left, right, **kw):
    def col(c):
        head, kind, step, lines = c
        return (_md(head), kind, step, [_md(x) for x in lines])
    return _e_compare(title, col(left), col(right), **kw)


def table(title, headers, rows, **kw):
    return _e_table(title, [_md(x) for x in headers],
                    [(r[0], [_md(c) for c in r[1]]) + tuple(r[2:]) for r in rows], **kw)


def statement(title, big, small=None, **kw):
    return _e_statement(title, _md(big), _md(small) if small else None, **kw)


def steps_list(title, items, **kw):
    return _e_steps_list(title, [(it[0], _md(it[1])) + tuple(it[2:]) for it in items], **kw)


def _h(s):
    """Lesson blocks author HTML directly. rich() would escape it, so only expand
    **bold** and leave entities and tags alone."""
    import re as _re
    return _re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', str(s))



# ------------------------------------------------------------------ lesson header
def lesson_header(num, title, pattern, evidence, mins, narration):
    """evidence: dict(reports=, latest=, level=, conf=, sources=) - or None for method lessons."""
    if evidence:
        rows = [('Reported', evidence['reports']), ('Most recent', evidence['latest']),
                ('Candidate level', evidence['level']), ('Confidence', evidence['conf']),
                ('Sources', evidence['sources'])]
    else:
        rows = [('Chapter', 'Methodology'), ('Applies to', 'Every design question'),
                ('Pattern', pattern)]
    meta = ''.join(
        '<div class="lh-k">%s</div><div class="lh-v k-%s">%s</div>'
        % (esc(k), 'ok' if k == 'Confidence' and 'HIGH' in str(v) else 'neutral', _h(str(v)))
        for k, v in rows)
    inner = ('<div class="lhead"><div class="lh-num">LESSON %s &nbsp;&middot;&nbsp; %d MIN</div>'
             '<h1 class="lh-t">%s</h1><div class="lh-p">%s</div>'
             '<div class="lh-meta">%s</div></div>' % (num, mins, _h(title), _h(pattern), meta))
    sid = new_slide(inner, cls='lesson-head')
    seg(sid, 0, narration)
    return sid


def beat(label, title, body_html, narration, kicker=None, step=0):
    sid = new_slide(body_html, title=title, kicker=kicker or label)
    seg(sid, step, narration)
    return sid


def think(prompt, secs, before, after):
    """Pose it, pause, then teach. No pretence of grading a spoken answer."""
    sid = new_slide(
        '<div class="qwrap"><div class="qlabel">Pause here</div>'
        '<div class="qtext">%s</div>'
        '<div class="think" data-step="1"><div class="thinkl">Take %d seconds. Say your answer out loud.</div></div>'
        '</div>' % (_h(prompt), secs), kicker='Your turn')
    seg(sid, 0, before)
    seg(sid, 1, after, think=secs)
    return sid


# ------------------------------------------------------------------ evidence
def evidence(title, rows, narration_intro, narration_rows, caveat=None, narration_caveat=None):
    """Where the question comes from. rows: (source, date, level, what_was_reported)."""
    body = '<table class="ev"><thead><tr><th>Source</th><th>Reported</th><th>Level</th>'\
           '<th>What was reported</th></tr></thead><tbody>'
    for i, (src, date, lvl, what) in enumerate(rows):
        body += ('<tr data-step="%d"><td>%s</td><td class="mono">%s</td><td>%s</td><td>%s</td></tr>'
                 % (i, _h(src), esc(date), esc(lvl), _h(what)))
    body += '</tbody></table>'
    if caveat:
        body += '<div class="ev-note" data-step="%d">%s</div>' % (len(rows), _h(caveat))
    sid = new_slide(body, title=title, kicker='Where this comes from')
    seg(sid, 0, narration_intro)
    for i, n in enumerate(narration_rows, start=1):
        seg(sid, min(i, len(rows)), n)
    if caveat and narration_caveat:
        seg(sid, len(rows), narration_caveat)
    return sid


# ------------------------------------------------------------------ clarify
def clarify(title, rows, narration):
    """rows: (question_to_ask, what_the_answer_changes). The second column is the point."""
    body = '<div class="cq">'
    for i, (q, changes) in enumerate(rows):
        body += ('<div class="cq-row" data-step="%d"><div class="cq-q">&ldquo;%s&rdquo;</div>'
                 '<div class="cq-w">%s</div></div>' % (i, _h(q), _h(changes)))
    body += '</div>'
    sid = new_slide(body, title=title, kicker='First five minutes')
    for i, n in enumerate(narration):
        seg(sid, min(i, len(rows) - 1), n)
    return sid


# ------------------------------------------------------------------ capacity
def capacity(title, rows, narration, note=None):
    """rows: (assumption, calculation, result, implication) - the last column is why it matters."""
    body = '<table class="cap"><thead><tr><th>Assumption</th><th>Calculation</th>'\
           '<th>Result</th><th>So the architecture&hellip;</th></tr></thead><tbody>'
    for i, (a, c, r, imp) in enumerate(rows):
        body += ('<tr data-step="%d"><td>%s</td><td class="mono">%s</td>'
                 '<td class="mono res">%s</td><td class="imp">%s</td></tr>'
                 % (i, _h(a), _h(c), _h(r), _h(imp)))
    body += '</tbody></table>'
    if note:
        body += '<div class="cap-note" data-step="%d">%s</div>' % (len(rows), _h(note))
    sid = new_slide(body, title=title, kicker='Capacity')
    for i, n in enumerate(narration):
        seg(sid, min(i, len(rows) + (1 if note else 0)), n)
    return sid


# ------------------------------------------------------------------ what to say
def say(title, lines, narration, kicker='What I should say'):
    """The sentences to speak. Communication is half the score in this round."""
    body = '<div class="say">'
    for i, l in enumerate(lines):
        body += '<div class="say-l" data-step="%d"><span class="say-q">&ldquo;</span>%s</div>' % (i, _h(l))
    body += '</div>'
    sid = new_slide(body, title=title, kicker=kicker)
    per = max(1, -(-len(lines) // max(1, len(narration))))
    for i, n in enumerate(narration):
        seg(sid, min(i * per + per - 1, len(lines) - 1), n)
    return sid


# ------------------------------------------------------------------ trade-offs
def tradeoff(title, options, decision, flip, narration):
    """options: [(name, kind, [pros], [cons])] - then what was chosen and what would flip it."""
    body = '<div class="to-grid">'
    for i, (name, kind, pros, cons) in enumerate(options):
        body += ('<div class="to-opt k-%s" data-step="%d"><div class="to-h">%s</div>'
                 '<ul class="to-p">%s</ul><ul class="to-c">%s</ul></div>'
                 % (kind, i, _h(name),
                    ''.join('<li>%s</li>' % _h(p) for p in pros),
                    ''.join('<li>%s</li>' % _h(c) for c in cons)))
    body += '</div>'
    n = len(options)
    body += '<div class="to-dec" data-step="%d"><b>Chosen:</b> %s</div>' % (n, _h(decision))
    body += '<div class="to-flip" data-step="%d"><b>What would flip it:</b> %s</div>' % (n + 1, _h(flip))
    sid = new_slide(body, title=title, kicker='Trade-off')
    for i, nar in enumerate(narration):
        seg(sid, min(i, n + 1), nar)
    return sid


# ------------------------------------------------------------------ failures
def failures(title, rows, narration):
    """rows: (component dies, what the user sees, what the system does, what you say)."""
    body = '<table class="fail"><thead><tr><th>What dies</th><th>What the user sees</th>'\
           '<th>What the system does</th></tr></thead><tbody>'
    for i, (c, user, sysr) in enumerate(rows):
        body += ('<tr data-step="%d"><td class="f-c">%s</td><td>%s</td><td>%s</td></tr>'
                 % (i, _h(c), _h(user), _h(sysr)))
    body += '</tbody></table>'
    sid = new_slide(body, title=title, kicker='Failure engineering')
    for i, n in enumerate(narration):
        seg(sid, min(i, len(rows) - 1), n)
    return sid


# ------------------------------------------------------------------ cheat sheet
def cheatsheet(title, rows, narration):
    """rows: (heading, one-line answer). The revision card."""
    body = '<div class="cs">'
    for i, (h, v) in enumerate(rows):
        body += ('<div class="cs-row" data-step="%d"><div class="cs-h">%s</div>'
                 '<div class="cs-v">%s</div></div>' % (i, esc(h), _h(v)))
    body += '</div>'
    sid = new_slide(body, title=title, kicker='One-page revision')
    per = max(1, -(-len(rows) // max(1, len(narration))))
    for i, n in enumerate(narration):
        seg(sid, min(i * per + per - 1, len(rows) - 1), n)
    return sid


# ------------------------------------------------------------------ follow-ups
def followups(reported, likely, narr_reported, narr_likely):
    body = ('<div class="fu-wrap"><div class="fu-col k-ok" data-step="0">'
            '<div class="fu-h">Reported follow-ups</div><ul>%s</ul></div>'
            '<div class="fu-col k-shared" data-step="1">'
            '<div class="fu-h">Likely Staff-level follow-ups</div><ul>%s</ul></div></div>'
            % (''.join('<li>%s</li>' % _h(x) for x in reported),
               ''.join('<li>%s</li>' % _h(x) for x in likely)))
    sid = new_slide(body, title='Follow-ups', kicker='What they ask next')
    seg(sid, 0, narr_reported)
    seg(sid, 1, narr_likely)
    return sid


# ------------------------------------------------------------------ architecture
class Arch:
    """One architecture, built up in levels.

    Boxes are placed once and revealed by step, so the diagram grows rather than being
    redrawn - which is what makes the animation teach instead of decorate. `focus`
    highlights whatever is being discussed at a given step.
    """

    def __init__(self, title, kicker='Architecture', height=820):
        self.D = Diagram(title, kicker=kicker, height=height)
        self._segs = []

    def box(self, id, x, y, w, h, title, sub='', kind='dp', step=0, focus=None, **kw):
        self.D.box(id, x, y, w, h, _plain(title), _plain(sub), kind=kind, step=step,
                   hl=_steps(focus), **kw)
        return id

    def arrow(self, a, b, step=0, focus=None, **kw):
        self.D.arrow(a, b, step=step, hl=_steps(focus), **kw)

    def zone(self, x, y, w, hgt, label, **kw):
        self.D.zone(x, y, w, hgt, _plain(label), **kw)

    def label(self, *a, **kw):
        if 'focus' in kw:
            kw['hl'] = _steps(kw.pop('focus'))
        self.D.label(*a, **kw)

    def note(self, x, y, text, step=0, kind='neutral', w=520, size='m'):
        self.D.label(x, y, _plain(text), kind=kind, step=step, w=w, size=size)

    def flow(self, points, kind='shared', frames=26):
        return travel(points, kind=kind, frames=frames)

    def narrate(self, step, text, travel_pts=None):
        self._segs.append((step, text, travel_pts))

    def build(self):
        sid = self.D.build()
        for step, text, tp in self._segs:
            seg(sid, step, text, travel=tp)
        return sid


def _steps(v):
    if v is None:
        return None
    if isinstance(v, int):
        return str(v)
    return ','.join(str(x) for x in v)
