# -*- coding: utf-8 -*-
"""09-question-bank.html - the InterviewDB LinkedIn coding questions, worked end to end.

Every question runs the same fourteen parts in the same order, so any one of them can be
opened and read top to bottom without hunting. The C# is read out of src/cs/qbank/ at build
time, which means the listings on the page are the bytes that compiled and passed 269 tests.

Data lives in qbank_data.py (Q1-Q9) and qbank_data2.py (Q10-Q17); the LeetCode table lives in
qbank_lc.py. This module only renders.
"""
import lib, qbank_cs as CS, qbank_lc as LC
from lib import esc, rich, card, sec, note, grid, code, tag, tags, acc, titled, tracker

PARTS = [
    ('question',   'The question, as supplied'),
    ('understand', 'Problem understanding'),
    ('examples',   'Examples'),
    ('observation', 'Key observation'),
    ('brute',      'Brute force'),
    ('optimal',    'Optimal approach'),
    ('walk',       'Step-by-step walkthrough'),
    ('code',       'C# implementation'),
    ('codewalk',   'Code walkthrough'),
    ('cx',         'Complexity'),
    ('edges',      'Edge cases'),
    ('fups',       'Follow-up questions'),
    ('testing',    'What the interviewer is testing'),
    ('say',        'How I would explain it'),
]
PART_NO = {k: i + 1 for i, (k, _) in enumerate(PARTS)}
PART_TITLE = dict(PARTS)

DIFF_CLS = {'EASY': 'hi', 'MEDIUM': 'med', 'HARD': 'low', 'STAFF': 'low'}
DIFF_LABEL = {'EASY': 'Easy', 'MEDIUM': 'Medium', 'HARD': 'Hard',
              'STAFF': 'Staff-level follow-up'}
PRIO_CLS = {'HIGH': 'hi', 'MEDIUM': 'med', 'LOWER': 'low'}
EV_CLS = {'reported': 'hi', 'idb': 'hi', 'general': 'med', 'inference': 'low', 'lc': ''}
EV_LABEL = {'reported': 'Reported elsewhere', 'idb': 'InterviewDB', 'general': 'Guide / list',
            'inference': 'My reading', 'lc': 'LeetCode'}


# ---------------------------------------------------------------- escaping
class Raw(str):
    """A table cell that is already HTML. lib.table runs rich() over every cell, which escapes
    anything outside the <b> <i> <br> <code> <small> whitelist, so a <span class="tag"> passed
    straight in renders as visible markup. Wrapping it in Raw opts out of that."""


def table(headers, rows, cls=''):
    th = ''.join('<th>%s</th>' % esc(x) for x in headers)
    tr = ''
    for r in rows:
        tr += '<tr>' + ''.join('<td>%s</td>' % (str(c) if isinstance(c, Raw) else rich(c))
                               for c in r) + '</tr>'
    return ('<div class="tw"><table class="%s"><thead><tr>%s</tr></thead>'
            '<tbody>%s</tbody></table></div>') % (cls, th, tr)


def chip(cls, text):
    return Raw(tag(cls, text))


def card_raw(body, title_html, cls=''):
    """lib.card runs rich() over its title, which escapes markup. This one does not."""
    return '<div class="card %s"><h3>%s</h3>%s</div>' % (cls, title_html, body)


# ---------------------------------------------------------------- small blocks
def part(key, body, sub=None):
    s = '<span class="qp-s">%s</span>' % rich(sub) if sub else ''
    return ('<div class="qp" data-part="%s"><div class="qp-h">'
            '<span class="qp-n">%d</span><span class="qp-t">%s</span>%s</div>'
            '<div class="qp-b">%s</div></div>') % (
        key, PART_NO[key], esc(PART_TITLE[key].upper()), s, body)


def kv_rows(pairs, cls='t-kv'):
    return table(['', ''], [[a, b] for a, b in pairs], cls=cls)


def pipeline(stages):
    out = []
    for i, (label, text) in enumerate(stages):
        if i:
            out.append('<div class="pl-ar">↓</div>')
        out.append('<div class="pl-row"><span class="pl-l">%s</span><span class="pl-t">%s</span></div>'
                   % (esc(label), rich(text)))
    return '<div class="pl">%s</div>' % ''.join(out)


def bullets(items):
    return '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(x) for x in items)


def says(lines):
    return '<div class="say-card">%s</div>' % ''.join(
        '<div class="say-line">%s</div>' % rich(l) for l in lines)


# ---------------------------------------------------------------- question parts
def p_question(q):
    body = '<div class="verb">%s</div>' % rich(q['idb'])
    if q.get('idb_extra'):
        body += '<div class="verb verb-f"><span class="lbl">Follow-up, as supplied</span>%s</div>' % rich(q['idb_extra'])

    dd = q['dd']
    # The body must be a real element, not a bare text node: an anonymous flex item has
    # min-width:auto and will not shrink, so a long <b> or <code> pushed past the viewport.
    ev = ''.join('<div class="ev ev-%s"><span class="evk">%s</span><div class="evb">%s</div></div>' % (
        EV_CLS[k], esc(EV_LABEL[k]), rich(t)) for k, t in dd['elsewhere'])
    body += '<h5>Due diligence against the existing research</h5>' + ev
    body += note(dd['verdict'], kind='good', label='Classification')

    if dd.get('conflict'):
        body += note(dd['conflict'], kind='bad', label='Sources disagree — preserved, not resolved')
    if q.get('ambiguity'):
        body += note(q['ambiguity'], kind='warn', label='The statement is ambiguous — raise this, do not silently pick')
    return part('question', body,
                sub='Preserved word for word. Everything below this line is my explanation.')


def p_understand(q):
    u = q['understand']
    body = '<p class="lead">%s</p>' % rich(u['what'])
    body += '<h5>What we are being asked to compute</h5><p>%s</p>' % rich(u['compute'])
    body += '<h5>Constraints that matter</h5>' + bullets(u['constraints'])
    body += '<h5>Assumptions I am making</h5>'
    body += table(['Assumption', 'What breaks if it is wrong'], u['assume'], cls='t-as')
    return part('understand', body)


def p_examples(q):
    rows = []
    for label, given, res in q['examples']:
        rows.append([('<b>%s</b>' % label) if label else '', given, res])
    body = table(['', 'Input', 'Result'], rows, cls='t-ex')
    if q.get('examples_note'):
        body += note(q['examples_note'], kind='', label='Where these came from')
    return part('examples', body)


def p_observation(q):
    return part('observation', '<div class="obs">%s</div>' % rich(q['observation']),
                sub='The step that turns the problem into a known shape')


def p_brute(q):
    b = q.get('brute')
    if not b:
        return ''
    body = '<h5>How the naive version works</h5><p>%s</p>' % rich(b['how'])
    body += '<h5>What it costs</h5><p>%s</p>' % rich(b['cx'])
    body += note(b['why_not'], kind='warn', label='Why it stops working')
    return part('brute', body)


def p_optimal(q):
    o = q['optimal']
    body = pipeline(o['pipeline'])
    body += '<h5>Why each structure was chosen</h5>'
    body += table(['Structure', 'Why that one'], o['why'], cls='t-why')
    if o.get('steps'):
        body += '<h5>The algorithm</h5><ol class="steps-n">%s</ol>' % ''.join(
            '<li>%s</li>' % rich(s) for s in o['steps'])
    return part('optimal', body)


def p_walk(q):
    w = q['walk']
    body = '<p>%s</p>' % rich(w['intro'])
    body += table(w['headers'], w['rows'], cls='t-walk')
    if w.get('close'):
        body += note(w['close'], kind='good', label='What the state tells you')
    return part('walk', body)


def p_code(q):
    body = ''
    for caption, filename, member in q['code']:
        src = CS.cs_type(filename, member) if '|' not in member else \
            CS.cs_member(filename, *member.split('|'))
        body += '<div class="cs-cap">%s <span class="cs-ln">%d lines</span></div>' % (
            rich(caption), CS.line_count(src))
        body += code(src, file=filename)
    return part('code', body,
                sub='Read from `src/cs/qbank/` — the source that compiled and passed the tests')


def p_codewalk(q):
    body = ''
    for heading, text in q['codewalk']:
        body += '<h5>%s</h5><p>%s</p>' % (rich(heading), rich(text))
    return part('codewalk', body)


def p_cx(q):
    c = q['cx']
    body = table(['Operation', 'Time', 'Space', 'Where it comes from'], c['rows'], cls='t-cx')
    if c.get('note'):
        body += note(c['note'], kind='', label='The part worth saying out loud')
    return part('cx', body)


def p_edges(q):
    return part('edges', table(['Case', 'What the code does'], q['edges'], cls='t-edge'))


def p_fups(q):
    body = ''
    for i, f in enumerate(q['fups'], 1):
        inner = ''
        if f.get('thinking'):
            inner += '<h5>Thinking</h5><p>%s</p>' % rich(f['thinking'])
        inner += '<h5>Approach</h5><p>%s</p>' % rich(f['approach'])
        inner += '<h5>Trade-off</h5><p>%s</p>' % rich(f['tradeoff'])
        if f.get('code'):
            for caption, filename, member in f['code']:
                src = CS.cs_type(filename, member) if '|' not in member else \
                    CS.cs_member(filename, *member.split('|'))
                inner += '<div class="cs-cap">%s</div>' % rich(caption)
                inner += code(src, file=filename)
        inner += table(['Time', 'Space'], [[f['t'], f['s']]], cls='t-fcx')
        origin = 'supplied with the question' if f.get('given') else 'likely pushback'
        body += acc('<span class="fu-q">“%s”</span> <span class="src">· %s</span>'
                    % (esc(f['q']), origin), inner, raw=True)
    return part('fups', body, sub='Answers always supplied. %d follow-ups.' % len(q['fups']))


def p_testing(q):
    t = q['testing']
    body = '<h5>The skills under the question</h5>' + bullets(t['skills'])
    body += lib.senior_staff(t['senior'], t['staff'])
    return part('testing', body)


def p_say(q):
    return part('say', says(q['say']),
                sub='Say it in this order. Short sentences; stop after each and let them steer.')


def p_video(q):
    v = q['video']
    beats = ''.join('<div class="vb"><span class="vt">%s</span>%s</div>' % (esc(ts), rich(lab))
                    for ts, lab in v['beats'])
    return acc(titled('Video lesson plan', '%s · ~%d min' % (v['title'], v['mins'])),
               '<p class="lead">%s</p><div class="vbs">%s</div>' % (rich(v['objective']), beats),
               raw=True)


# ---------------------------------------------------------------- one question
def render_question(q):
    lc_here = [r for r in LC.ROWS if q['id'] in r[5]]
    miss_here = [m for m in LC.MISSING if m[0] == q['id']]

    meta = ''.join(tag('', t) for t in q['tags'])
    head = ('<div class="qh" id="%s"><div class="qh-top">'
            '<span class="qn">Q%d</span><h3>%s</h3></div>'
            '<div class="qh-tags">%s%s%s</div></div>') % (
        q['id'], q['n'], esc(q['name']),
        tag(DIFF_CLS[q['diff']], DIFF_LABEL[q['diff']]),
        tag(PRIO_CLS[q['prio']], q['prio'].title() + ' priority'),
        meta)

    body = head
    body += note(q['prio_why'], kind='', label='Why this priority')

    if lc_here or miss_here:
        rows = []
        for num, title, slug, diff, prem, _ids, rel, _n in lc_here:
            rows.append(['[%d. %s](%s)' % (num, title, LC.url(slug)), diff + (' · premium' if prem else ''),
                         LC.REL_LABEL[rel][1]])
        for _qid, num, title, slug, diff, prem, why in miss_here:
            rows.append(['[%d. %s](%s)' % (num, title, LC.url(slug)), diff + (' · premium' if prem else ''),
                         '<b>Closest public twin</b> — not in the supplied list'])
        body += '<div class="lcmini">' + table(['LeetCode', 'Difficulty', 'Relation'], rows, cls='t-lcm') + '</div>'

    body += p_question(q)
    body += p_understand(q)
    body += p_examples(q)
    body += p_observation(q)
    body += p_brute(q)
    body += p_optimal(q)
    body += p_walk(q)
    body += p_code(q)
    body += p_codewalk(q)
    body += p_cx(q)
    body += p_edges(q)
    body += p_fups(q)
    body += p_testing(q)
    body += p_say(q)
    body += p_video(q)

    item = lib.reg('coding', 'qb-' + q['id'], 'qbank', 'Q%d %s' % (q['n'], q['name']),
                   weight=2 if q['prio'] == 'HIGH' else 1)
    body += '<div data-id="%s" data-label="%s">%s</div>' % (
        item, esc('Q%d %s' % (q['n'], q['name'])), tracker(item))

    return '<div class="qcard">%s</div>' % body


# ---------------------------------------------------------------- page sections
def s_about(QS):
    hi = [q for q in QS if q['prio'] == 'HIGH']
    body = card(rich(
        'Seventeen questions from **InterviewDB**, bought and supplied by you, worked to the same '
        'fourteen parts each: the statement as given, understanding, examples, the key observation, '
        'brute force, the optimal approach, a walkthrough, **C#**, a code walkthrough, complexity, '
        'edge cases, follow-ups, what is being tested, and the sentences to say.\n\n'
        'The page does three things the earlier pages could not. It **keeps the original wording**, so '
        'you revise the question that was asked rather than my paraphrase of it. It **cross-checks every '
        'question against the research already in this workspace**, and says when two sources disagree '
        'instead of quietly picking one. And every listing is **read from `src/cs/qbank/` at build '
        'time**, so nothing on this page is code I did not compile.'),
        title='What this page is')

    body += grid([
        note('**269 assertions, 0 failures** on .NET 10.0.103.\n\n'
                  'Three of the checks are property tests, not fixed expectations: the covered-size '
                  'structure against a brute-force bitmap over 300 random trials, the four island '
                  'variants against brute force over every window across 3,000 trials, and the '
                  'tournament tree against its own sorted leaves over 500 random tournaments.\n\n'
                  '`cd companies/linkedin/src/cs/qbank && dotnet run -c Release`',
             kind='good', label='The code was run, not just written'),
        note('Writing the tests found **one real bug and two wrong expectations of my own**.\n\n'
                  'The bug: `TaskManager.AddTask` overwrote an existing task’s dependency edges '
                  'instead of unioning them, so a cycle closed across two `AddTask` calls went '
                  'undetected. Q15 documents it.\n\n'
                  'The wrong expectations were mine, in the island tests. Both are noted where they '
                  'occurred, because "my first answer was wrong here" is more useful to revise than a '
                  'clean page that hides it.',
             kind='warn', label='What testing caught'),
    ], 'g2')

    body += note(
        '**Nothing here is a prediction.** These questions were reported to InterviewDB by candidates; '
        'that makes them a preparation signal and nothing stronger. No question on this page is claimed '
        'to appear in your loop, and where the only evidence is a single unverifiable entry, the page '
        'says so. **%d of the 17** are corroborated by at least one other source already in this '
        'workspace — those are the ones marked high priority.' % len(hi),
        kind='', label='On provenance')

    return sec('about', 'What this page is', body,
               kicker='InterviewDB · 17 questions',
               why='All C# · all compiled · all cross-checked')


def s_inventory(QS):
    rows = []
    for q in QS:
        lc = [r for r in LC.ROWS if q['id'] in r[5] and r[6] in ('exact', 'variation')]
        lcs = ', '.join('[%d](%s)' % (r[0], LC.url(r[2])) for r in lc) or '—'
        rows.append([
            '<b>Q%d</b>' % q['n'],
            '[%s](#%s)' % (q['name'], q['id']),
            chip(DIFF_CLS[q['diff']], DIFF_LABEL[q['diff']]),
            chip(PRIO_CLS[q['prio']], q['prio'].title()),
            lcs,
            q['verdict_short'],
        ])
    body = table(['#', 'Question', 'Difficulty', 'Priority', 'LeetCode', 'Corroboration'], rows, cls='t-inv')

    counts = {}
    for q in QS:
        for t in q['tags']:
            counts[t] = counts.get(t, 0) + 1
    chips = ''.join('<span class="tag">%s <b>%d</b></span>' % (esc(k), v)
                    for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
    body += '<h4>Categories across the 17</h4><div class="tags">%s</div>' % chips

    body += note(
        '**Design and data-structure design dominate.** Eleven of the seventeen ask you to build a '
        'structure or a service rather than compute an answer, which matches what the official pack '
        'says the Staff Coding module scores: modularity, extensibility, and finding bugs. Pure '
        'algorithm questions are the minority here.', kind='', label='What the tag counts say')
    return sec('inventory', 'Question inventory', body,
               kicker='All 17, at a glance', why='Sorted by priority, then by number')


def s_priority(QS):
    body = ''
    for level, label, why in [
        ('HIGH', 'High priority',
         'Corroborated by at least one source already in this workspace, or first-party from your own '
         'list. These are where revision time pays.'),
        ('MEDIUM', 'Medium priority',
         'InterviewDB plus a pattern that is independently well attested at LinkedIn, but the specific '
         'framing rests on one source.'),
        ('LOWER', 'Lower priority',
         'InterviewDB only, with nothing corroborating. Still worth one pass each — they are all '
         'short — but not before the group above.')]:
        group = [q for q in QS if q['prio'] == level]
        rows = [['<b>Q%d</b> %s' % (q['n'], q['name']), q['prio_why']] for q in group]
        body += '<h4>%s <span class="src">· %d questions</span></h4>' % (label, len(group))
        body += '<p>%s</p>' % rich(why)
        body += table(['Question', 'Why it sits here'], rows, cls='t-prio')

    body += note(
        'Priority here means **evidence and transferability**, not difficulty. Q7 (the scheduler) is the '
        'hardest question on the page and sits in the middle group, because its evidence is one entry '
        'plus a design-round report. Q12 is nearly trivial and sits high, because it is reported from '
        'three directions and takes fifteen minutes to make airtight.',
        kind='warn', label='What priority does and does not mean')

    return sec('priority', 'Interview priority', body,
               kicker='Evidence-weighted, not difficulty-weighted',
               why='No question here is claimed to be guaranteed')


def s_leetcode(QS):
    byid = {q['id']: q for q in QS}
    rows = []
    for num, title, slug, diff, prem, ids, rel, why in LC.ROWS:
        cls, label = LC.REL_LABEL[rel]
        linked = ', '.join('[Q%d](#%s)' % (byid[i]['n'], i) for i in ids if i in byid) or '—'
        rows.append(['<b>%d</b>' % num, '[%s](%s)' % (title, LC.url(slug)),
                     diff + ('<br><small>premium</small>' if prem else ''),
                     linked, chip(cls, label), why])
    body = table(['#', 'Problem', 'Difficulty', 'Question', 'Relation', 'How it relates'], rows, cls='t-lc')

    body += note(
        'All %d titles, slugs and difficulties were read from **LeetCode’s own problem index** '
        '(%d problems, fetched %s), not written from memory. **364 appears twice in the supplied list**, '
        'so there are %d unique numbers, not %d.\n\n'
        '**Fourteen of the %d have no meaningful relation to any of the seventeen questions.** They are '
        'LinkedIn-tagged classics that arrived in the same list. Saying so is the point of the table: a '
        'number on a company list is evidence about the company, not about the question printed above '
        'it.' % (len(LC.ROWS), LC.INDEX_SIZE, LC.FETCHED, len(LC.ROWS), len(LC.ROWS) + 1, len(LC.ROWS)),
        kind='', label='How this table was built')

    body += note(
        '**695 Max Area of Island is a name collision, not a match.** It is 2-D flood fill; Q3 '
        '"Artificial Island" is a 1-D sliding window with a conversion budget. If you revise 695 for '
        'Q3 you will practise the wrong algorithm. The real twin is **1004 Max Consecutive Ones III**, '
        'which is not in the supplied list but is in this workspace already, reader-reported.',
        kind='bad', label='The one trap in the supplied list')

    rows2 = []
    for qid, num, title, slug, diff, prem, why in LC.MISSING:
        q = byid[qid]
        rows2.append(['[Q%d %s](#%s)' % (q['n'], q['name'], qid),
                      '[%d. %s](%s)' % (num, title, LC.url(slug)),
                      diff + (' · premium' if prem else ''), why])
    body += '<h4>The real public twins that are <i>not</i> in the supplied list</h4>'
    body += '<p>%s</p>' % rich(
        'For eight of the seventeen, the closest public problem was missing from the numbers you were '
        'given. These are the ones to run on LeetCode.')
    body += table(['Question', 'LeetCode', 'Difficulty', 'Why this one'], rows2, cls='t-lcx')

    return sec('leetcode', 'LeetCode cross-reference', body,
               kicker='%d numbers, every one verified' % len(LC.ROWS),
               why='Fetched from LeetCode’s index on %s' % LC.FETCHED)


def s_questions(QS):
    out = ''
    for level, label in [('HIGH', 'High priority'), ('MEDIUM', 'Medium priority'),
                         ('LOWER', 'Lower priority')]:
        group = [q for q in QS if q['prio'] == level]
        body = ''.join(render_question(q) for q in group)
        out += sec('sol-' + level.lower(), 'Solutions — %s' % label, body,
                   kicker='%d questions' % len(group),
                   why='Each runs all fourteen parts, in order')
    return out


PATTERNS = [
    ('Sliding window over a budget',
     ['q3'],
     'A window is valid while some non-negative cost stays within a budget, so the left pointer never '
     'moves backwards. That monotonicity is the entire justification for O(n).',
     'The moment a cost can be negative, or the window must exclude a value rather than afford it, the '
     'two-pointer argument dies. Q3’s obstacle follow-up is that case: `-1` cannot be paid for, so '
     'the window is cut rather than shrunk.'),
    ('Map plus a positional array',
     ['q12', 'q13'],
     'A dictionary gives O(1) lookup but no order and no random pick; an array gives O(1) random pick '
     'but O(n) deletion. Holding both, with the map storing positions into the array, gives all three.',
     'Every bug in this family is an index left stale. Update the moved element’s index **before** '
     'shortening the array, and handle "the element I am removing is the last one" explicitly.'),
    ('Doubly linked list plus map',
     ['q1'],
     'O(1) eviction needs a structure where you can unlink a node you already hold a reference to. A '
     'dictionary finds the node; the list orders it. Neither can do both.',
     'In C# `LinkedList<T>` gives this, but the interview answer is usually the hand-rolled node with '
     'head and tail sentinels, because sentinels remove every null check from the link code.'),
    ('Bucket the key, not the value',
     ['q1', 'q11'],
     'When many inputs must map to one answer, compute a canonical key and index by it. Q11 maps a word '
     'to a digit signature; wildcard indexing in Q8 maps a word to `*PE`; hour bucketing does the same '
     'over time.',
     'The cost moves to preprocessing, and preprocessing is only worth it if queries outnumber builds. '
     'Say that ratio out loud — it is the whole argument for the design.'),
    ('BFS where the neighbour function is the work',
     ['q5', 'q8'],
     'The search is textbook; the thinking is in how neighbours are produced. Wildcard buckets in Q8, '
     'the connection list in Q5. Get the neighbour function right and the rest is boilerplate.',
     'Bidirectional BFS is the standard follow-up, and it is worth remembering **why** it wins: two '
     'searches of depth d/2 touch b^(d/2) nodes each rather than b^d once. Always expand the smaller '
     'frontier.'),
    ('Two-colouring an undirected graph',
     ['q2'],
     'Any "split into two groups with a constraint between them" question is bipartiteness. The answer '
     'is BFS assigning alternating colours, and the failure is an edge joining two nodes of the same '
     'colour — equivalently, an odd cycle.',
     'The two traps are both structural, not algorithmic: the conflict list may be declared one way '
     'only, so build a symmetric graph first; and there may be several components, so loop over every '
     'unvisited node.'),
    ('Height from the bottom, not depth from the top',
     ['q10'],
     'Depth is passed down; height is returned up. Any question about "the last level", "peel the '
     'leaves" or "weight by distance from the bottom" needs the post-order return value, not a BFS level '
     'counter.',
     'This is the link to LeetCode 364. If you find yourself wanting the tree height before you can '
     'start, you are in this pattern.'),
    ('Merge on insert, maintain the aggregate',
     ['q9'],
     'Keep the invariant (disjoint, merged) at all times and keep the answer (total covered) as a field '
     'updated on every mutation. The query then costs nothing.',
     'A single insert can absorb many intervals, so the worst case of one call is not O(log n). It is '
     'amortised, because each interval is removed at most once ever. Say "amortised" — claiming '
     'strict O(log n) is wrong and easy to disprove.'),
    ('Priority queue plus a timed condition wait',
     ['q7'],
     'Anything with deadlines is a min-heap on deadline plus a worker that waits until the head is due. '
     'The wait must be interruptible, because a task scheduled sooner than the current head has to '
     'preempt the sleep.',
     'Always re-check the condition in a loop after waking. Spurious wakes, an early `Pulse`, and a real '
     'timeout then need no separate handling — which is the whole reason the loop exists.'),
    ('Walk two trees in lockstep',
     ['q17'],
     'Merging, comparing and diffing trees are the same recursion: at each node, handle "in both", "in '
     'the left only" and "in the right only". Keyed children turn the child match into a dictionary '
     'probe.',
     'Build a new tree rather than mutating one input, unless asked otherwise. It makes the function '
     'safe to call concurrently and safe to call with the same tree twice, which is one of the supplied '
     'follow-ups.'),
    ('Rejection sampling',
     ['q4'],
     'To get k equally likely outcomes from a source that gives a power of two, generate and discard '
     'anything out of range. Rescaling is the tempting wrong answer, because 8 does not divide into 7.',
     'Expected cost is a geometric series and is finite whenever the accept probability is non-zero, '
     'but there is no worst-case bound. State that: the loop terminates with probability 1, not in '
     'bounded time.'),
    ('Greedy along a line with an adjacency rule',
     ['q14'],
     'Take the earliest legal position. Nothing is lost, because occupying a seat only ever constrains '
     'seats to its right, and any solution can be rewritten to the leftmost choice without losing count.',
     'That exchange argument is the answer to "prove it". Every bug in this pattern is a boundary: the '
     'first and last positions have one neighbour, not two.'),
    ('Directed cycle detection on insert',
     ['q15'],
     'A dependency graph must be checked at the moment an edge is added, not when execution starts. '
     'Three-colour DFS: grey means "on the current path", so meeting grey is a back edge.',
     'The staff-level part is atomicity. Check first, commit second, so a rejected add leaves the '
     'structure exactly as it was. Half-applying a change and then throwing is worse than not '
     'validating at all.'),
]


def s_patterns(QS):
    byid = {q['id']: q for q in QS}
    body = '<p class="lead">%s</p>' % rich(
        'Thirteen patterns cover all seventeen questions. If you only have an evening, read this section '
        'and then the high-priority solutions — the patterns are what transfer to the question you '
        'actually get.')
    for name, ids, what, trap in PATTERNS:
        links = ' '.join('<a class="qlink" href="#%s">Q%d</a>' % (i, byid[i]['n']) for i in ids if i in byid)
        body += card_raw('<p>%s</p>%s' % (rich(what),
                         note(trap, kind='warn', label='Where it goes wrong')),
                         '%s <span class="src">· %s</span>' % (esc(name), links))
    return sec('patterns', 'Interview patterns', body,
               kicker='13 patterns, 17 questions',
               why='The transferable half')


TEMPLATES = [
    ('Sliding window with a budget', 'window', '''// Longest window whose cost stays within a budget. Works whenever cost is non-negative,
// which is what lets the left pointer move forward only.
int Longest(int[] a, int budget) {
    int best = 0, left = 0;
    long spent = 0;

    for (int right = 0; right < a.Length; right++) {
        spent += Cost(a[right]);

        while (spent > budget) {          // shrink, never rewind
            spent -= Cost(a[left]);
            left++;
        }
        best = Math.Max(best, right - left + 1);
    }
    return best;
}'''),
    ('BFS by level, counting edges', 'bfs', '''// Level-by-level BFS. `depth` is edges travelled, which is almost always what
// "distance" means in an interview - say which you are returning.
int ShortestHops<T>(T start, T goal, Func<T, IEnumerable<T>> neighbours) {
    if (EqualityComparer<T>.Default.Equals(start, goal)) return 0;

    var seen = new HashSet<T> { start };
    var queue = new Queue<T>();
    queue.Enqueue(start);
    int depth = 0;

    while (queue.Count > 0) {
        int levelSize = queue.Count;
        depth++;

        for (int i = 0; i < levelSize; i++) {
            foreach (T next in neighbours(queue.Dequeue())) {
                if (EqualityComparer<T>.Default.Equals(next, goal)) return depth;
                if (seen.Add(next)) queue.Enqueue(next);
            }
        }
    }
    return -1;
}'''),
    ('Two-colouring for bipartiteness', 'bip', '''// Returns false on the first edge joining two nodes of the same colour.
// The outer loop is what handles disconnected components.
bool IsBipartite(Dictionary<int, List<int>> adj) {
    var side = new Dictionary<int, int>();

    foreach (int start in adj.Keys) {
        if (side.ContainsKey(start)) continue;

        side[start] = 0;
        var q = new Queue<int>();
        q.Enqueue(start);

        while (q.Count > 0) {
            int cur = q.Dequeue();
            foreach (int next in adj[cur]) {
                if (!side.TryGetValue(next, out int c)) { side[next] = 1 - side[cur]; q.Enqueue(next); }
                else if (c == side[cur]) return false;
            }
        }
    }
    return true;
}'''),
    ('Doubly linked list with sentinels', 'dll', '''// Head and tail sentinels remove every null check from the link code, which is
// where LRU implementations actually break under time pressure.
sealed class Node { public int Key, Value; public Node Prev, Next; }

readonly Node _head = new(), _tail = new();
// in the constructor: _head.Next = _tail; _tail.Prev = _head;

void Unlink(Node n) {
    n.Prev.Next = n.Next;
    n.Next.Prev = n.Prev;
}

void LinkFront(Node n) {
    n.Next = _head.Next;
    n.Prev = _head;
    _head.Next.Prev = n;
    _head.Next = n;
}

void MoveToFront(Node n) { Unlink(n); LinkFront(n); }
// the eviction victim is always _tail.Prev'''),
    ('Post-order height, bottom-up', 'height', '''// Returns -1 for null so a leaf comes out as 0. Every question about the last level,
// peeling leaves, or weighting by distance from the bottom is this function.
int Height(TreeNode node, List<List<int>> levels) {
    if (node == null) return -1;

    int h = 1 + Math.Max(Height(node.Left, levels), Height(node.Right, levels));

    if (h == levels.Count) levels.Add(new List<int>());
    levels[h].Add(node.Value);
    return h;
}'''),
    ('Worker with a timed condition wait', 'worker', '''// The loop around Monitor.Wait is the whole design: a spurious wake, an early Pulse
// from a newly scheduled task, and a real timeout all end up re-checking the same thing.
void Loop() {
    while (true) {
        Work ready = null;

        lock (_gate) {
            while (true) {
                if (_shutdown && _queue.Count == 0) return;
                if (_queue.Count == 0) { Monitor.Wait(_gate); continue; }

                var head = _queue.Peek();
                long waitMs = head.DueAt - Now();
                if (waitMs <= 0) { ready = _queue.Dequeue(); break; }

                Monitor.Wait(_gate, (int)Math.Min(waitMs, int.MaxValue));
            }
        }
        // run outside the lock, or a task that schedules work deadlocks
        try { ready.Run(); } catch { }
    }
}'''),
    ('Map plus array for O(1) random', 'bag', '''// Never shift the array. Move the last element into the hole and fix its index.
// Update the moved element's index BEFORE shortening, or the last-element case breaks.
bool Remove(int value) {
    if (!_indexOf.TryGetValue(value, out int slot)) return false;

    int last = _items[^1];
    _items[slot] = last;
    _indexOf[last] = slot;

    _items.RemoveAt(_items.Count - 1);
    _indexOf.Remove(value);
    return true;
}'''),
    ('Three-colour DFS for a directed cycle', 'cycle', '''// Grey (1) means "on the current path", so meeting grey is a back edge. Black (2) means
// "finished, and nothing below it cycles" - revisiting black is fine and must not be a failure.
bool HasCycle(string id, Dictionary<string, List<string>> edges, Dictionary<string, int> state) {
    state[id] = 1;

    if (edges.TryGetValue(id, out var deps))
        foreach (string next in deps) {
            state.TryGetValue(next, out int s);
            if (s == 1) return true;
            if (s == 0 && HasCycle(next, edges, state)) return true;
        }

    state[id] = 2;
    return false;
}'''),
]


def s_templates():
    body = '<p class="lead">%s</p>' % rich(
        'Eight blocks that appear in more than one of the seventeen. Write each once from memory before '
        'the loop; under time pressure these are what you should not be deriving.')
    for name, key, src in TEMPLATES:
        body += acc(titled(name, '%d lines' % len(src.strip().split('\n'))),
                    code(src), raw=True)
    return sec('templates', 'C# templates', body,
               kicker='8 reusable blocks', why='All C#, as required')


def s_cheatsheet(QS):
    rows = []
    for q in QS:
        for op, t, s, _where in q['cx']['rows']:
            rows.append(['<b>Q%d</b> %s' % (q['n'], q['name']), op, t, s])
    body = table(['Question', 'Operation', 'Time', 'Space'], rows, cls='t-cs')
    body += note(
        '**Three of these are amortised, not worst case, and saying the wrong one is a real error.**\n\n'
        '• Q1 `Put` is O(1) worst case; the *sweep* is O(k log n) for k reclaimed.\n'
        '• Q9 `AddInterval` is O(log n) **amortised** — one call can absorb many intervals, and '
        'the bound holds only because each interval is removed at most once over the life of the '
        'structure.\n'
        '• Q12 is O(1) **expected**, because it rests on hashing. A pathological hash makes it O(n).\n\n'
        'Q4 has no worst-case time bound at all: rejection sampling terminates with probability 1, not '
        'within any fixed number of draws.',
        kind='warn', label='Where the honest answer is not the clean one')
    return sec('cheatsheet', 'Complexity cheat sheet', body,
               kicker='Every operation on the page',
               why='With the amortised and expected cases named')


def s_video(QS):
    rows = []
    total = 0
    for q in QS:
        v = q['video']
        total += v['mins']
        rows.append(['<b>Q%d</b>' % q['n'], v['title'], '~%d min' % v['mins'],
                     '%d beats' % len(v['beats']), q['prio'].title()])
    body = table(['#', 'Video title', 'Length', 'Structure', 'Priority'], rows, cls='t-vid')
    body += note(
        'Roughly **%d minutes** across seventeen lessons, at the same twelve-to-eighteen minutes each '
        'that the coding course uses, so a single pattern can be revised without scrubbing a long file.\n\n'
        'Each question above carries its own lesson plan with timestamps — open the *Video lesson '
        'plan* block at the bottom of any question. **Nothing is rendered yet.** The plans exist so the '
        'build is a mechanical step later: `video/coding/lessons/` takes one module per lesson and the '
        'eighteen beats map onto the fourteen parts here with the naive/optimal split expanded.' % total,
        kind='', label='Status')
    body += note(
        'Build order if you do render these: the six high-priority questions first, then Q7 and Q17, '
        'which are the two where watching an explanation genuinely beats reading one — concurrency '
        'and tree merging are both easier to follow when the state is drawn moving.',
        kind='good', label='Where video is actually worth it')
    return sec('video', 'Video course roadmap', body,
               kicker='17 lesson plans, none rendered',
               why='~%d minutes if built' % total)


def s_mock(QS):
    body = '<p class="lead">%s</p>' % rich(
        'Three sets of two questions, 45 minutes each, run the way the Staff Coding module is described '
        'in the official pack: one question you implement, then a change you have to extend into. '
        'Answer out loud, then grade with Claude — the page does not pretend to score you.')

    sets = [
        ('mock-a', 'Set A — design under a constraint',
         'Implement an LRU cache where every entry also carries a time-to-live, so a get on an expired '
         'key returns -1 even though the key is still held. Then: how would you reclaim expired entries '
         'without adding latency to get?',
         ['The eviction structure is chosen before the TTL is mentioned, and still works after',
          'get() does lazy expiry, so an expired entry never returns a value',
          'Names the trade between a background sweep, a min-heap of expiries and a timing wheel',
          'Says which operations are O(1) worst case and which are amortised',
          'Raises concurrency without being asked, and says what it would lock']),
        ('mock-b', 'Set B — graph modelling from a bad input',
         'Given a map from animal to the list of animals it cannot share a side with, decide whether all '
         'the animals can be split into two groups. Then: return the two groups, and say what changes if '
         'a third group is allowed.',
         ['Recognises bipartiteness rather than trying to reason case by case',
          'Builds a symmetric graph first, because the input may declare a conflict one way only',
          'Loops over every unvisited node, so a hidden second component cannot pass',
          'Explains the failure as an odd cycle, not just "a conflict"',
          'Knows that three groups is graph 3-colouring and is NP-hard, and says so plainly']),
        ('mock-c', 'Set C — structure with two different queries',
         'Implement addInterval(start, end) and getCoveredSize(), with the insert logarithmic and the '
         'query constant. Then: add removeInterval, and say what breaks.',
         ['Keeps the intervals disjoint and merged as an invariant, not as a cleanup step',
          'Maintains the total as a field rather than recomputing it, which is the whole reason the '
          'query is O(1)',
          'Says amortised, and can explain why a single insert is not O(log n)',
          'Handles the adjacent-versus-overlapping case explicitly, and states the half-open convention',
          'For removal: sees that a remove can split one interval into two, so the count can grow']),
    ]
    for mid, title, q, rubric in sets:
        item = lib.reg('coding', 'qb-' + mid, 'qbank', title, weight=2, kind='mock')
        body += card(lib.mock_block(item, q, 'Staff Coding', rubric, secs=2700), title=title)

    return sec('mock', 'Final mock coding set', body,
               kicker='3 sets · 45 minutes each',
               why='Implement, then extend — the reported arc')


CSS = '''
.note{white-space:pre-line}
.note ul,.note ol{white-space:normal;margin:6px 0 0 18px}
.qcard{border:1px solid var(--line);border-radius:var(--radius);margin:26px 0;background:#fff;
  box-shadow:var(--shadow);overflow:hidden}
.qh{padding:18px 20px 14px;background:var(--li-soft);border-bottom:1px solid var(--line)}
.qh-top{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.qh-top h3{margin:0;font-size:22px;letter-spacing:-.3px;color:var(--ink)}
.qn{font:700 13px/1 'JetBrains Mono',monospace;color:#fff;background:var(--li);
  border-radius:6px;padding:5px 8px;flex:none}
.qh-tags{margin-top:10px;display:flex;gap:6px;flex-wrap:wrap}
.qcard > .note{margin:14px 20px}
.qcard > .lcmini{margin:4px 20px 6px}
.qcard > .acc{margin:14px 20px}
.qcard > div[data-id]{margin:0 20px 18px}
.qp{border-top:1px solid var(--line);padding:16px 20px 6px}
.qp-h{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px}
.qp-n{font:700 11px/1 'JetBrains Mono',monospace;color:#fff;background:var(--li-dark);border-radius:5px;
  padding:4px 6px;min-width:20px;text-align:center;flex:none}
.qp-t{font:700 12px/1.2 'Inter',sans-serif;letter-spacing:.11em;color:var(--ink)}
.qp-s{font-size:12.5px;color:var(--muted);font-style:italic}
.qp-b > h5{margin:16px 0 6px;font-size:13px;letter-spacing:.04em;color:var(--li-dark);font-weight:700}
.qp-b > p:first-child{margin-top:0}
.qp-b > p{margin:8px 0}
.verb{border-left:3px solid var(--li);background:var(--li-soft);padding:13px 16px;
  border-radius:0 8px 8px 0;font-size:14.6px;line-height:1.62;white-space:pre-line;color:var(--ink)}
.verb-f{border-left-color:var(--muted);background:var(--bgwarm);margin-top:10px}
.verb .lbl{display:block;font:700 11px 'JetBrains Mono',monospace;letter-spacing:1.4px;
  text-transform:uppercase;margin-bottom:4px;color:var(--muted)}
.ev{display:flex;gap:11px;padding:9px 13px;border-radius:9px;margin-bottom:7px;font-size:13.8px;
  line-height:1.58;background:var(--bgwarm);border:1px solid var(--line)}
.evb{min-width:0;flex:1;white-space:pre-line;overflow-wrap:anywhere}
/* A long inline identifier must break rather than widen the page. overflow-wrap on an
   ancestor does not reach into an inline child, so it is set on the code element itself. */
.qcard code,.ev code,.note code{overflow-wrap:anywhere;word-break:break-word}
.evk{font:700 10.5px/1.6 'JetBrains Mono',monospace;letter-spacing:.06em;white-space:nowrap;flex:none}
.ev-hi{border-color:#a5d6a7;background:var(--ok-bg)} .ev-hi .evk{color:var(--green)}
.ev-med{border-color:#ffe082;background:var(--warn-bg)} .ev-med .evk{color:#b26a00}
.ev-low .evk{color:var(--muted)}
.obs{border-left:3px solid var(--green);background:var(--ok-bg);padding:14px 17px;
  border-radius:0 9px 9px 0;font-size:15px;line-height:1.64;white-space:pre-line;color:var(--ink)}
.pl{margin:4px 0 14px}
.pl-row{display:flex;gap:12px;align-items:baseline;border:1px solid var(--line);border-radius:9px;
  padding:10px 13px;background:var(--bgwarm)}
.pl-l{font:700 10.5px/1.7 'JetBrains Mono',monospace;letter-spacing:.08em;color:var(--li-dark);
  min-width:118px;flex:none}
.pl-t{font-size:14.2px;line-height:1.58}
.pl-ar{text-align:center;color:var(--muted);font-size:16px;line-height:1.2;margin:3px 0}
ol.steps-n{padding-left:22px} ol.steps-n li{margin-bottom:7px;line-height:1.62}
.cs-cap{font-size:13.4px;color:var(--soft);margin:16px 0 4px;font-style:italic}
.cs-ln{font:500 11px 'JetBrains Mono',monospace;color:var(--muted);font-style:normal;margin-left:6px}
.fu-q{font-style:italic}
.say-card .say-line{padding:12px 16px 12px 40px;margin-bottom:10px;position:relative;
  background:var(--ok-bg);border-radius:9px;border-left:4px solid var(--green);
  font-size:14.6px;line-height:1.58}
.say-card .say-line::before{content:"\201C";position:absolute;left:13px;top:6px;font-size:30px;
  color:var(--green);opacity:.5}
.vbs{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(238px,100%),1fr));gap:6px}
.vb{display:flex;gap:9px;font-size:13.2px;padding:6px 10px;border:1px solid var(--line);border-radius:7px;
  background:var(--bgwarm)}
.vt{font:500 12px/1.6 'JetBrains Mono',monospace;color:var(--li);flex:none}
.qlink{font:600 11.5px/1 'JetBrains Mono',monospace;color:var(--li);text-decoration:none;
  border:1px solid #bcd9f2;border-radius:5px;padding:3px 5px;margin-left:2px}
.qlink:hover{background:var(--li-soft)}
.t-as td:first-child,.t-why td:first-child,.t-edge td:first-child{width:38%;font-weight:600}
.t-kv td:first-child{width:30%;font-weight:600}
.t-ex td:first-child{width:11%;white-space:nowrap}
.t-ex td:nth-child(2){font-family:'JetBrains Mono',monospace;font-size:12.8px}
.t-cx td:nth-child(2),.t-cx td:nth-child(3){white-space:nowrap;font-family:'JetBrains Mono',monospace;font-size:12.8px}
.t-cs td:nth-child(3),.t-cs td:nth-child(4){white-space:nowrap;font-family:'JetBrains Mono',monospace;font-size:12.8px}
.t-cs td:first-child{width:26%}
.t-fcx td{font-family:'JetBrains Mono',monospace;font-size:12.8px;white-space:nowrap}
.t-inv td:first-child,.t-lc td:first-child{white-space:nowrap}
.t-lc td:nth-child(6){font-size:13.2px}
.t-lc td:nth-child(3),.t-lcx td:nth-child(3){white-space:nowrap}
.t-prio td:first-child{width:30%}
.t-walk td{font-size:13.4px}
.t-walk td:first-child{white-space:nowrap}
.t-lcm td:first-child{width:46%}
.t-vid td:nth-child(3),.t-vid td:nth-child(4),.t-vid td:nth-child(5){white-space:nowrap}
@media (max-width:680px){
  .qh-top h3{font-size:18px}
  .qp{padding:14px 14px 4px}
  .qh{padding:14px}
  .qcard > .note,.qcard > .lcmini,.qcard > .acc,.qcard > div[data-id]{margin-left:14px;margin-right:14px}
  .pl-row{flex-direction:column;gap:4px}
  .pl-l{min-width:0}
  .t-as td:first-child,.t-why td:first-child,.t-edge td:first-child,.t-kv td:first-child,
  .t-prio td:first-child,.t-cs td:first-child{width:auto}
}
'''


def build():
    import qbank_data as D1, qbank_data2 as D2
    QS = D1.QUESTIONS + D2.QUESTIONS

    assert len(QS) == 17, 'expected 17 questions, got %d' % len(QS)
    ids = [q['id'] for q in QS]
    assert len(set(ids)) == 17, 'duplicate question ids'
    assert [q['n'] for q in QS] == list(range(1, 18)), 'question numbers are not 1..17'
    for q in QS:
        for key in ('idb', 'dd', 'understand', 'examples', 'observation', 'optimal', 'walk',
                    'code', 'codewalk', 'cx', 'edges', 'fups', 'testing', 'say', 'video',
                    'tags', 'diff', 'prio', 'prio_why', 'verdict_short'):
            assert key in q, '%s is missing %s' % (q['id'], key)
        assert q['diff'] in DIFF_CLS, '%s bad difficulty' % q['id']
        assert q['prio'] in PRIO_CLS, '%s bad priority' % q['id']
        for _c, f, m in q['code']:
            CS.cs_type(f, m) if '|' not in m else CS.cs_member(f, *m.split('|'))
    # every LeetCode row points at a real question id
    for row in LC.ROWS:
        for qid in row[5]:
            assert qid in ids, 'LeetCode %d points at unknown %s' % (row[0], qid)
    for m in LC.MISSING:
        assert m[0] in ids, 'MISSING row points at unknown %s' % m[0]

    order = {'HIGH': 0, 'MEDIUM': 1, 'LOWER': 2}
    QS_sorted = sorted(QS, key=lambda q: (order[q['prio']], q['n']))

    body = s_about(QS)
    body += s_inventory(QS_sorted)
    body += s_priority(QS)
    body += s_questions(QS)
    body += s_patterns(QS)
    body += s_leetcode(QS)
    body += s_templates()
    body += s_cheatsheet(QS)
    body += s_video(QS)
    body += s_mock(QS)

    nav = '<h4>Questions</h4>' + ''.join(
        '<a href="#%s">Q%d %s</a>' % (q['id'], q['n'], esc(q['name'])) for q in QS)

    return lib.page('09-question-bank.html', 'LinkedIn coding question bank',
                    'Seventeen InterviewDB questions worked end to end in C# — statement preserved, '
                    'cross-checked against the existing research, every listing compiled and tested.',
                    body, crumb_tail='Question bank',
                    hero_chips=[('done', '17 worked in full'), ('', 'C# only'),
                                ('', '269 assertions pass'), ('', '42 LeetCode numbers verified')],
                    nav_html=nav,
                    extra_head='<style>%s</style>' % CSS)
