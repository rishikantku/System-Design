# -*- coding: utf-8 -*-
"""Chapter 12 — the top 10 LinkedIn design questions, one video, run the way an interview runs.

Ranked by independent reports (15 Oct 2026). Simple English on purpose. For every design:
question → what it tests → clarifying questions → functional / non-functional → capacity → API →
data model and partition keys → architecture diagram → deep dives → trade-off → failures →
what a Staff engineer does → follow-ups → mistakes and the closing line.
The questions are in my own words; the InterviewDB wording is paid content and is not reproduced.
"""
import io, json, os, re, sys
from lib import *
import engine as E
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from top10_data import TOP10, STAFF, MODEL

GUIDES = json.load(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'top10_guides.json'), encoding='utf-8'))
NUM = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']


def sp(t):
    """Guide text → something a speech engine reads naturally."""
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', str(t)).replace('`', '')
    t = re.sub(r'\b(GET|POST|PUT|DELETE|WebSocket) /', r'\1 ', t)                 # "POST /alerts" -> "POST alerts"
    t = re.sub(r'\{[^}]*\}', '', t)                                             # JSON bodies are not read aloud
    t = t.replace('TSDB', 'time-series database').replace('(given)', '').replace('— (append order)', 'append order')
    t = re.sub(r'(?<=\w)_(?=\w)', ' ', t)                                        # series_id -> series id
    t = re.sub(r'[\[\]]', '', t).replace(' + ', ' plus ').replace('?', '?')
    for a, b in [('→', ' to '), ('×', ' times '), ('≈', 'about '), ('~', 'about '), ('%', ' percent'), ('/s', ' per second'),
                 ('e.g.', 'for example'), (' vs ', ' versus '), ('&', ' and '), ('—', ', '), ('–', ' to '), (' / ', ' or '),
                 ('p99', 'p ninety-nine'), ('TTL', 'T T L'), ('API', 'A P I'), ('LRU', 'L R U'), ('QPS', 'queries per second')]:
        t = t.replace(a, b)
    t = re.sub(r'\bDB\b', 'database', t)
    t = re.sub(r'(\d+(?:\.\d+)?)\s?K\b', r'\1 thousand', t)
    t = re.sub(r'(\d+(?:\.\d+)?)\s?M\b', r'\1 million', t)
    t = re.sub(r'(\d+(?:\.\d+)?)\s?B\b', r'\1 billion', t)
    for a, b in [('GB', ' gigabytes'), ('TB', ' terabytes'), ('MB', ' megabytes'), (' KB', ' kilobytes'), (' ms', ' milliseconds'), (' s ', ' seconds ')]:
        t = re.sub(r'(\d)\s?' + a.strip() + r'\b', r'\1' + b, t) if a.strip() != 's' else t.replace(a, b)
    return re.sub(r'\s+', ' ', t).strip()


def html(t):
    """Guide text (**bold**, `code`) → slide HTML."""
    t = esc(str(t))
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', t)


def arch(d, g):
    """Lay the two rows out automatically; reveal one box per step, then walk the main path."""
    rows = d['rows']
    A = Arch('High-level design — ' + d['title'], kicker='Architecture', height=780)
    pos, order = {}, []
    W, H, X0, X1 = 330, 120, 70, 1850
    ys = [150, 470]
    for r, row in enumerate(rows):
        n = len(row)
        gap = (X1 - X0 - n * W) / max(1, n - 1) if n > 1 else 0
        for i, (bid, title, sub) in enumerate(row):
            x = X0 + i * (W + gap) if n > 1 else (X0 + X1 - W) / 2
            pos[bid] = (r, x)
            order.append((bid, title, sub))
    kinds = ['info', 'dp', 'shared', 'ok', 'cp', 'neutral']
    step_of = {}
    for s, (bid, title, sub) in enumerate(order):
        r, x = pos[bid]
        A.box(bid, int(x), ys[r], W, H, title, sub, kind=kinds[s % len(kinds)], step=s, focus=s)
        step_of[bid] = s
    for a, b in d['arrows']:
        ra, xa = pos[a]; rb, xb = pos[b]
        if ra == rb: fs, ts = ('r', 'l') if xa < xb else ('l', 'r')
        else: fs, ts = ('b', 't') if ra < rb else ('t', 'b')
        A.arrow(a, b, step=max(step_of[a], step_of[b]), focus=max(step_of[a], step_of[b]))
    parts = g.get('parts') or []
    stop = {'the', 'a', 'on', 'each', 'of', 'and', 'per', 'service', 'store', 'db', 'layer', '+', '/', '(given)'}
    def explain(title):
        words = {w for w in re.findall(r'[a-z]+', title.lower()) if w not in stop and len(w) > 2}
        for name, what in parts:
            if words & {w for w in re.findall(r'[a-z]+', name.lower()) if len(w) > 2}:
                return sp(what)
        return ''
    for s, (bid, title, sub) in enumerate(order):
        A.narrate(s, sp('%s, %s. ' % (title, sub)) + ' ' + explain(title))
    path = ', then '.join(t for _, t, _ in order[:min(4, len(order))])
    A.narrate(len(order) - 1, 'So one request flows like this: ' + sp(path) + '. Draw this first, walk one request end to end out loud, and only then go deep.')
    return A.build()


def design(i, d):
    g = GUIDES[d['id']]
    E.chapter(i + 1, '#%d · %s' % (i + 1, d['title']), '%d independent reports · the interview, step by step' % d['reports'],
              'Number %s. %s. We have %d independent reports of this one. Let us run it the way the interview runs.'
              % (NUM[i], d['title'], d['reports']))

    sid = statement('The question', d['ask'], 'Reported %d time%s for LinkedIn — interview step 0: listen, then say it back in one line.'
                    % (d['reports'], 's' if d['reports'] > 1 else ''), kicker='Step 0 · The question')
    seg(sid, 0, 'Here is the question. ' + sp(d['ask']))
    seg(sid, 1, 'First thing: say it back in one line, so you and the interviewer agree on what you are building.')

    sid = statement('What they are really testing', g['gist'], kicker='Step 1 · Understand')
    seg(sid, 0, 'What are they really testing here? ' + sp(g['gist']))

    clarify('Step 1 · Clarifying questions — and why each one matters', [(html(q), html(w)) for q, w in g['clarify'][:5]],
            ['Now ask a few questions before drawing anything. ' + sp(g['clarify'][0][0]) + ' ' + sp(g['clarify'][0][1])] +
            [sp(q) + ' ' + sp(w) for q, w in g['clarify'][1:5]])

    sid = compare('Step 2 · Requirements',
                  ('Functional — what it does', 'ok', 0, list(d['fr'])),
                  ('Non-functional — how well', 'info', 1, list(d['nfr'])))
    seg(sid, 0, 'Write the requirements down. Functional, meaning what it does: ' + '. '.join(sp(x) for x in d['fr']) + '.')
    seg(sid, 1, 'Non-functional, meaning how well it must do it: ' + '. '.join(sp(x) for x in d['nfr']) + '. These decide the design more than the features do.')

    capacity('Step 3 · Capacity — only the numbers that change a decision', [tuple(html(c) for c in row) for row in d['cap']],
             ['Quick numbers. Only the ones that change a decision.'] +
             ['%s. %s gives %s. So: %s.' % (sp(a), sp(c) if c else 'That', sp(r), sp(imp)) for a, c, r, imp in d['cap']])

    sid = steps_list('Step 4 · API', [(k, '`%s`' % a, 'info') for k, a in enumerate(g['api'])], kicker='Step 4 · API and data model')
    for k, a in enumerate(g['api']):
        seg(sid, k, ('The API. ' if k == 0 else '') + sp(a) + '.')

    rows = MODEL[d['id']]
    sid = table('Step 4 · Data model and partition keys', ['Table / record', 'Main fields', 'Partition key', 'Why this key'],
                [(k, [t, f, '**%s**' % pk, w]) for k, (t, f, pk, w) in enumerate(rows)],
                kicker='Step 4 · API and data model')
    for k, (t, f, pk, w) in enumerate(rows):
        seg(sid, k, ('Now the data model, and the partition key for each table, because the key decides how it scales. ' if k == 0 else '') +
            '%s. Fields: %s. Partition by %s, because %s.' % (sp(t), sp(f), sp(pk), sp(w).lower()))

    think('Before the answer: what are the main boxes for ' + d['title'].lower() + ', and where does the data go first?', 12,
          'Pause here. Try to draw the main boxes yourself, and say where a request goes first.',
          'Here is one good answer, built up box by box.')
    arch(d, g)

    deep = g['deep'][:4]
    for k, (t, x) in enumerate(deep):
        sid = cards('Step 6 · Deep dive %d of %d' % (k + 1, len(deep)), [(0, t, x, 'shared')], cols=1, kicker='Step 6 · Deep dive')
        seg(sid, 0, ('Now go deep on the hard parts. ' if k == 0 else 'Next deep dive. ') + sp(t) + '. ' + sp(x))

    opts, dec, flip = d['trade']
    tradeoff('Step 7 · The key trade-off', [(html(n), kind, [html(p) for p in pros], [html(c) for c in cons]) for n, kind, pros, cons in opts],
             html(dec), html(flip),
             ['The key trade-off. Option one: %s. Good: %s. Cost: %s.' % (sp(opts[0][0]), '; '.join(sp(p) for p in opts[0][2]), '; '.join(sp(c) for c in opts[0][3])),
              'Option two: %s. Good: %s. Cost: %s.' % (sp(opts[1][0]), '; '.join(sp(p) for p in opts[1][2]), '; '.join(sp(c) for c in opts[1][3])),
              'I choose: ' + sp(dec),
              'And say what would change your mind: ' + sp(flip)])

    failures('Step 8 · What breaks, and what happens', [tuple(html(c) for c in r) for r in d['fail']],
             ['Failures. ' + '%s. The user sees: %s. The system: %s.' % tuple(sp(c) for c in d['fail'][0])] +
             ['%s. User sees: %s. System: %s.' % tuple(sp(c) for c in r) for r in d['fail'][1:]])

    sid = steps_list('What a Staff engineer does here', [(k, x, 'cp') for k, x in enumerate(STAFF[d['id']])], kicker='Staff-level signal')
    for k, x in enumerate(STAFF[d['id']]):
        seg(sid, k, ('What makes this a Staff answer, not a Senior one? ' if k == 0 else '') + sp(x))

    fu = g['followups'][:5]
    for part in range(0, len(fu), 3):
        chunk = fu[part:part + 3]
        sid = cards('Step 9 · Follow-ups they will ask' + (' (continued)' if part else ''), [(k, q, a, 'info') for k, (q, a) in enumerate(chunk)],
                    cols=1, kicker='Step 9 · Follow-ups')
        for k, (q, a) in enumerate(chunk):
            seg(sid, k, ('The follow-ups. ' if part == 0 and k == 0 else '') + 'They ask: ' + sp(q) + ' You say: ' + sp(a))

    say('Close the round', [html(m) for m in g['mistakes'][:3]] + ['<b>%s</b>' % html(g['say'].strip('"'))],
        ['Avoid these mistakes. ' + ' '.join(sp(m) for m in g['mistakes'][:3]),
         'And close in two lines: ' + sp(g['say'].strip('"'))],
        kicker='Mistakes to avoid · the closing line')


# ------------------------------------------------------------------------------ the video
lesson_header('12.1', 'The top 10 LinkedIn system design questions — the interview, step by step',
              'Requirements &middot; capacity &middot; API &middot; data model &middot; architecture &middot; trade-offs &middot; failures &middot; Staff signal',
              dict(reports='InterviewDB list + LeetCode Discuss reports + earlier research', latest='October 2026',
                   level='Staff Software Engineer', conf='Ranked by independent reports', sources='InterviewDB, LeetCode Discuss, Blind, Glassdoor, Exponent'), 85,
              """This video covers the ten LinkedIn system design questions with the most independent reports, from your """
              """InterviewDB list and the LeetCode Discuss reports you collected. Each one runs the way the interview runs: """
              """the question, clarifying questions, requirements, numbers, the API and data model, the architecture, """
              """the deep dives, the key trade-off, what breaks, what a Staff engineer does differently, and the follow-ups. """
              """Simple language, no fluff. About eight minutes per design.""")

sid = table('The top 10, by number of reports — 1 to 5', ['#', 'Question', 'Reports'],
            [(k, [str(k + 1), d['title'], str(d['reports'])]) for k, d in enumerate(TOP10[:5])], kicker='The list')
seg(sid, 0, 'The list, most reported first. A report count is evidence, not a promise — but it tells you where to spend time.')
seg(sid, 4, 'Metrics monitoring leads by far, with nine reports. Then key-value store, top-K, typeahead, and the IP denylist.')
sid = table('The top 10, by number of reports — 6 to 10', ['#', 'Question', 'Reports'],
            [(k, [str(k + 6), d['title'], str(d['reports'])]) for k, d in enumerate(TOP10[5:])], kicker='The list')
seg(sid, 4, 'Then message queue, notifications, job scheduler, rate limiter, and logging.')

sid = steps_list('How every design in this video runs — the same order as the interview', [
    (0, '**0–5 min** · Say the question back · ask 4–5 clarifying questions', 'info'),
    (1, '**5–10 min** · Functional and non-functional requirements · capacity numbers', 'info'),
    (2, '**10–15 min** · API · data model and partition keys', 'shared'),
    (3, '**15–25 min** · High-level architecture · walk one request end to end', 'ok'),
    (4, '**25–45 min** · Deep dives · the key trade-off', 'cp'),
    (5, '**45–60 min** · Failures · follow-ups · close in two lines', 'deny'),
], kicker='The method')
for k, t in enumerate(['Every design follows the same order, because the interview does. First five minutes: say the question back and ask four or five clarifying questions.',
                       'Then requirements — what it does, and how well — and a few numbers.',
                       'Then the API, and the data model with its partition keys.',
                       'Then the architecture. Draw the boxes and walk one request through them.',
                       'Then go deep on the two hard parts, and name the trade-off you made.',
                       'Finally failures, follow-ups, and a two-line summary. Let us start.']):
    seg(sid, k, t)

for i, d in enumerate(TOP10):
    design(i, d)

E.chapter(11, 'What the ten have in common', 'The patterns to carry into any design question',
          'Last part. What these ten designs have in common.')
sid = cheatsheet('Patterns you saw again and again', [
    ('Buffer with a log', 'Kafka in front of slow storage — metrics, logging, notifications, denylist'),
    ('Precompute', 'Do the heavy work offline — typeahead prefixes, top-K rollups, metric rollups'),
    ('Partition by the read key', 'series_id, user_id, prefix, key — the key decides how it scales'),
    ('Atomic claim / atomic counter', 'Scheduler leases, rate-limit buckets, notification limits'),
    ('Versioned push to every node', 'Denylist, rules, config — know when a node is stale'),
    ('Idempotency everywhere', 'Retries are normal; duplicates must be harmless'),
    ('Fail open or closed — on purpose', 'Say which, and why, for each component'),
], ['Seven patterns came up again and again. Buffer with a log, like Kafka, in front of anything slow.',
    'Precompute heavy work offline, so the request path is a lookup.',
    'Partition by the key you read with.',
    'Use an atomic claim or an atomic counter instead of a coordination service.',
    'Push versioned config to every node, so each node knows if it is stale.',
    'Make everything idempotent, because retries are normal.',
    'And decide fail open or fail closed on purpose, and say why. Good luck.'])
