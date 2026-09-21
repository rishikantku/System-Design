# -*- coding: utf-8 -*-
"""05-research.html — the research layer, updated independently of the prep content."""
from lib import *
import research as R1
import research2 as R2

ROUND_LABEL = {'coding': 'Coding', 'ai': 'AI Coding', 'design': 'System Design'}
CONF_CLS = {'HIGH': 'hi', 'MEDIUM': 'med', 'LOW': 'low'}

def _src_links(keys):
    out = []
    for k in keys:
        s = R2.SRC[k]
        out.append('<a href="%s" target="_blank" rel="noopener">%s</a>' % (s['url'], esc(s['name'].split('—')[0].strip()))
                   if s['url'] else esc(s['name'].split('—')[0].strip()))
    return ' · '.join(out)

def _year(q):
    d = q['date']
    return '2026' if '2026' in d else ('2025' if '2025' in d else 'older')

def build():
    ALL = [('coding', q) for q in R2.CODING] + [('ai', q) for q in R2.AI] + [('design', q) for q in R2.DESIGN]
    n2026 = sum(1 for _, q in ALL if '2026' in q['date'])
    hi_rec = [q for _, q in ALL if q['conf'] == 'HIGH' and q['rec'] == 'recurring']
    reader = [q for _, q in ALL if 'reader' in q['src']]

    # ---------------- header ----------------
    kpis = grid([
        '<div class="kpi"><div class="n">%s</div><div class="l">Last researched</div></div>' % R2.DATE,
        '<div class="kpi"><div class="n">%d</div><div class="l">Sources analysed (pass 2)</div></div>' % len(R2.SRC),
        '<div class="kpi"><div class="n">%d</div><div class="l">Reports mentioning 2026</div></div>' % n2026,
        '<div class="kpi"><div class="n">%d</div><div class="l">Coding questions</div></div>' % len(R2.CODING),
        '<div class="kpi"><div class="n">%d</div><div class="l">AI coding questions</div></div>' % len(R2.AI),
        '<div class="kpi"><div class="n">%d</div><div class="l">System design questions</div></div>' % len(R2.DESIGN),
        '<div class="kpi"><div class="n">%d</div><div class="l">High-confidence recurring</div></div>' % len(hi_rec),
        '<div class="kpi"><div class="n">%d</div><div class="l">From your own list (first-party)</div></div>' % len(reader),
    ], 'g4')

    method = grid([
        card(
        '<p>Something is a <b>reported question</b> only when a candidate described being asked it, or when you supplied it from '
        'your own collection. Preparation guides, "top LinkedIn questions" articles and recruiter advice are never counted as '
        'reports — they sit in the <a href="#sec-general">general topics</a> section instead.</p>'
        + table(['Label', 'Means'], [
            ['%s <b>HIGH</b>' % tag('hi', 'conf'), 'Several independent recent reports, or supplied by you first-hand'],
            ['%s <b>MEDIUM</b>' % tag('med', 'conf'), 'One strong recent report, or several older ones'],
            ['%s <b>LOW</b>' % tag('low', 'conf'), 'Single report, thin detail, or old'],
            ['<b>recurring</b>', 'Two or more <i>independent</i> sources — copies of the same original report do not count twice'],
            ['<b>single</b>', 'One source. Useful practice, not a pattern'],
        ]), title='How to read this'),
        card(
        '<p>Two passes so far. Pass 1 (21 Sep) mapped the loop; pass 2 (22 Sep) went question-hunting across more sources and '
        'folded in your own list.</p>'
        '<h4>What could not be fetched directly</h4><ul>%s</ul>'
        '<p class="src">Where a page blocked fetching, the finding came from search-result summaries of that page and is graded '
        'down accordingly. Nothing here is invented, and no URL is fabricated — every link is one I actually retrieved or that '
        'you supplied.</p>' % ''.join('<li>%s</li>' % rich(b) for b in R2.BLOCKED),
        title='Method, and its limits'),
    ], 'g2')

    warn = note(
        'Nothing below is a prediction. The right reading is: <b>recent candidates reported these, so they are preparation '
        'signals</b>. Your own list is the strongest signal in the file because it is first-party — but even that is history, '
        'not a forecast. Breadth beats betting.', 'warn', 'Do not overfit')

    # ---------------- master database ----------------
    rows = ''
    for rnd, q in ALL:
        lc = ''
        if q['lc']:
            name, num, url = q['lc']
            lc = '<div class="src" style="margin-top:4px">LeetCode %d · <a href="%s" target="_blank" rel="noopener">%s</a></div>' % (num, url, esc(name))
        fu = ''.join('<li>%s</li>' % rich(f) for f in q['follows']) or '<li>None reported.</li>'
        extra = ''
        if q['variations']: extra += '<p><b>Note:</b> %s</p>' % rich(q['variations'])
        if q['constraints']: extra += '<p><b>Constraints reported:</b> %s</p>' % rich(q['constraints'])
        if q['complexity']: extra += '<p><b>Expected complexity:</b> %s</p>' % rich(q['complexity'])
        covered = ('<a href="%s">in the workspace ↗</a>' % {'coding': '01-coding.html', 'ai': '02-ai-coding.html',
                                                            'design': '03-system-design.html'}[rnd]) if q['covers'] else \
                  '<b style="color:var(--red)">not covered</b>'
        rows += (
            '<tr data-id="r2-%s" data-round="%s" data-year="%s" data-conf="%s" data-rec="%s" data-level="%s" '
            'data-loc="%s" data-prep="no">'
            '<td><b>%s</b></td>'
            '<td><b>%s</b>%s'
            '<details class="acc" style="margin:8px 0 0"><summary><span class="sq">Follow-ups, notes, coverage</span></summary>'
            '<div class="body"><b>Follow-ups reported:</b><ul>%s</ul>%s<p><b>Coverage:</b> %s</p>'
            '<div class="src">Sources (%d independent): %s</div></div></details></td>'
            '<td>%s</td><td>%s<div class="src">%s</div></td><td>%s</td><td>%s</td><td>%s</td>'
            '<td><button class="sbtn qprep">Mark practised</button></td></tr>'
        ) % (
            (q['q'][:28].lower().replace(' ', '-').replace('`', '')), rnd, _year(q), q['conf'], q['rec'],
            'staff' if 'Staff' in q['level'] else ('senior' if 'Senior' in q['level'] else 'other'),
            'india' if 'India' in q['loc'] else ('us' if 'United States' in q['loc'] or 'US' in q['loc'] else 'other'),
            ROUND_LABEL[rnd], esc(q['q']), lc, fu, extra, covered, q['reports'], _src_links(q['src']),
            esc(q['date']), esc(q['level']), esc(q['loc']), esc(q['pattern']),
            tag(CONF_CLS[q['conf']], q['conf']), tag('new' if q['rec'] == 'recurring' else 'low', q['rec']))

    filters = ('<div class="filters" data-filter-scope="#mdb tbody tr">'
               '<input class="search" placeholder="Search every reported question…">'
               + ''.join('<button class="fchip" data-fk="round" data-fv="%s">%s</button>' % (k, v) for k, v in ROUND_LABEL.items())
               + '<button class="fchip" data-fk="year" data-fv="2026">2026</button>'
               + '<button class="fchip" data-fk="year" data-fv="2025">2025</button>'
               + '<button class="fchip" data-fk="level" data-fv="staff">Staff</button>'
               + '<button class="fchip" data-fk="level" data-fv="senior">Senior</button>'
               + '<button class="fchip" data-fk="loc" data-fv="india">India</button>'
               + '<button class="fchip" data-fk="conf" data-fv="HIGH">High confidence</button>'
               + '<button class="fchip" data-fk="rec" data-fv="recurring">Recurring</button>'
               + '<button class="fchip" data-fk="prep" data-fv="no">Not practised</button>'
               + '<span class="count"></span></div>')

    mdb = filters + ('<div class="tw" id="mdb"><table><thead><tr><th>Round</th><th>Question</th><th>Reported</th>'
                     '<th>Level / location</th><th>Pattern</th><th>Confidence</th><th>Recurrence</th><th>Prep</th>'
                     '</tr></thead><tbody>%s</tbody></table></div>' % rows)

    # ---------------- top lists ----------------
    def toplist(items, title, note_text):
        li = ''
        for i, q in enumerate(items, 1):
            lcs = ' <span class="src">(LC %d)</span>' % q['lc'][1] if q['lc'] else ''
            li += '<li><b>%s</b>%s — %s %s %s</li>' % (
                esc(q['q']), lcs, esc(q['pattern']),
                tag(CONF_CLS[q['conf']], q['conf']), tag('new' if q['rec'] == 'recurring' else 'low', q['rec']))
        return card('<p>%s</p><ol>%s</ol>' % (rich(note_text), li), title=title)

    coding_sorted = sorted(R2.CODING, key=lambda q: ({'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}[q['conf']],
                                                     0 if q['rec'] == 'recurring' else 1,
                                                     0 if '2026' in q['date'] else 1))
    design_sorted = sorted(R2.DESIGN, key=lambda q: ({'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}[q['conf']],
                                                     0 if q['rec'] == 'recurring' else 1))
    tops = (grid([
        toplist(coding_sorted, 'Top coding signals (%d)' % len(coding_sorted),
                'Ordered by confidence, then recurrence, then recency. **Research priorities, not predictions.** '
                'Your own list dominates the top because first-party beats aggregated.'),
        toplist(R2.AI, 'Top AI coding signals (%d)' % len(R2.AI),
                'Every one of these is a cache, interval, parsing or debug-and-extend problem — the round is ordinary coding with '
                'an assistant, and the pivot is always concurrency and production.'),
    ], 'g2') + grid([
        toplist(design_sorted, 'Top system design signals (%d)' % len(design_sorted),
                'Infrastructure prompts (rate limiter, scheduler, queue, index) outnumber product prompts in first-hand reports, '
                'which matches the Systems & Infrastructure role you are interviewing for.'),
        card('<h4>Recurring coding patterns</h4>' + table(['Pattern', 'Questions', 'Signal'], PATTERNS_TABLE(R2.CODING)) +
             '<h4>Recurring design patterns</h4>' + table(['Pattern', 'Questions'], PATTERNS_TABLE(R2.DESIGN, simple=True)),
             title='Pattern analysis'),
    ], 'g2'))

    # ---------------- gap analysis ----------------
    covered, revise, missing = [], [], []
    for rnd, q in ALL:
        if q['covers']: covered.append((rnd, q))
        else: missing.append((rnd, q))
    gap = card(
        '<p>Every reported question above was checked against what this workspace already contains. '
        '<b>%d of %d are covered</b> — most of them because your own list drove the new Staff Coding problems.</p>' % (
            len(covered), len(ALL)) +
        table(['Status', 'Questions', 'Action'], [
            ['%s <b>Covered</b>' % tag('hi', 'ok'), '%d' % len(covered),
             'Worked in full in the round pages, with follow-ups and self-evaluation'],
            ['%s <b>Not covered</b>' % tag('p0', 'gap'), '%d' % len(missing),
             'Listed below with what I did about each'],
        ]) +
        '<h4>What was missing, and what I added</h4>' +
        table(['Reported question', 'Round', 'Status now'], [
            ['OS and networking fundamentals (TCP vs UDP, paging, stack vs heap) [Taro, Oct 2025]', 'Coding / screen',
             '**Added** — a systems-fundamentals refresher on the Staff Coding page'],
            ['Design a metrics gathering system [Glassdoor, aggregated]', 'System design',
             '**Added** — as a design brief in the infrastructure set'],
            ['Design a calendar (LLD) [Exponent, ≈Aug 2026]', 'Design / LLD',
             '**Added** — as an LLD brief, which also serves the craftsmanship round'],
            ['Design LinkedIn\'s news feed [aggregated]', 'System design',
             'Covered by the main guide (design-twitter), linked from the design page catalogue'],
            ['DSA rounds "linked lists, BFS, celebrity" [Glassdoor, thin]', 'Coding',
             'Celebrity and BFS now worked; linked-list reps are in the problem bank'],
        ]), title='Coverage and gaps')

    # ---------------- general and inference ----------------
    gen = card(
        '<p>These appear in preparation guides and "top questions" lists but <b>no candidate report</b> surfaced for them in '
        'either pass. Prepare them for breadth; do not treat them as evidence.</p>' +
        table(['Topic', 'Why it is here', 'Source'], [[t, w, _src_links(s)] for t, w, s in R2.GENERAL]),
        title='General preparation topics (not reported questions)')
    inf = card(
        '<p>My readings of the evidence, marked as such so you can discount them.</p>' +
        table(['Inference', 'Basis'], [[a, b] for a, b in R2.INFERENCE]),
        title='Inferences (mine, not reports)')

    # ---------------- summary ----------------
    summary = ''
    for rnd, title, body in [
        ('coding', 'Coding', {
          'Recent questions': 'Your own list is the freshest and most specific evidence: phone-keypad combinations, All O`one, '
            'Word Ladder, The Maze, GetRandom with duplicates, K closest elements, Celebrity, Max Consecutive Ones III, Shortest '
            'Word Distance II, Bulb Switcher, Binary Tree Upside Down, Find Leaves, keyed tree merge, minimum degree of '
            'connection, compact tree, valid triangle, and the booths problem.',
          'Recurring across sources': 'All O`one, Word Ladder, The Maze, GetRandom-with-duplicates, Celebrity, Find Leaves, '
            'Upside Down, topological build order, nested-structure traversal — each appears in your list **and** in an '
            'independent report or the tagged set.',
          'Recurring patterns': 'Trees and n-ary trees, graph BFS (especially bidirectional), data-structure design, sliding '
            'window, two pointers, topological sort. Dynamic programming is conspicuously absent from every report found.',
          'Common follow-ups': '"Make it O(1) space / iterative", "now make it thread-safe", "what if the input is 1000× bigger", '
            '"return the path, not just the distance", "minimise the expensive calls".',
          'Staff-level expectations': 'Clean interfaces, stated contracts, testing out loud, and taking the production follow-up '
            'unprompted. One 2026 report had a concurrency follow-up on the phone screen.',
          'Prioritise': 'The 13 problems from your list that are now worked on the Staff Coding page — they are first-party '
            'evidence and half of them are design-flavoured, which is what the official pack says the module scores.'}),
        ('ai', 'AI Coding', {
          'Recent questions': 'LRU, LFU with GetRank(), a merge-intervals class, JSON-like record processing, and a maze class to '
            'debug and extend.',
          'Recurring across sources': 'Caches and intervals appear in both the Hello Interview and Coditioning write-ups; the '
            'debug → extend → harden arc appears in two independent places.',
          'Recurring patterns': 'Known data structures, modest code volume, and a pivot to concurrency or production every time.',
          'Common follow-ups': 'The verbatim chain from the ≈Mar 2026 report: well-formedness, generate-with-a-guaranteed-path, '
            '"why this AI-generated approach over the alternatives", "how would you test each change", "if this went to '
            'production, what would you change".',
          'Staff-level expectations': 'The official pack is explicit: use AI, but own the solution — understand it, validate it, '
            'explain it, fix it. It is not a prompt-engineering test.',
          'Prioritise': 'The eight CWAI drills, run with a real assistant and a timer. Narrate every acceptance and rejection.'}),
        ('design', 'System Design', {
          'Recent questions': 'Rate limiter (≈Aug 2026), calendar LLD (≈Sep 2026), autosuggest backend (≈Mar 2026), job scheduler '
            '(Sep 2025), distributed inverted index (May 2025, India Staff), Kafka-like queue (Jun 2025).',
          'Recurring across sources': 'Autosuggest/typeahead is the only design prompt with three independent mentions. '
            'Cache-with-pluggable-eviction appears twice.',
          'Recurring patterns': 'Infrastructure primitives dominate first-hand reports; product designs (feed, PYMK, jobs) come '
            'mostly from guides rather than reports.',
          'Common follow-ups': 'Partitioning, consistency, failure modes, caching, storage choice, observability, cost, rollout — '
            'and one report ended early once the trade-offs were covered.',
          'Staff-level expectations': 'Lead with trade-offs; reason about blast radius and evolution; connect to member impact.',
          'Prioritise': 'Rate limiter, job scheduler, autosuggest, inverted index and the Kafka-like queue — plus the newly added '
            'metrics platform and calendar LLD.'}),
    ]:
        summary += card(''.join('<h4>%s</h4><p>%s</p>' % (k, rich(v)) for k, v in body.items()),
                        title=title)

    tail = r'''
    (function(){
      function raw(){ try{ return JSON.parse(localStorage.getItem('lp.v1'))||{} }catch(e){ return {} } }
      function paint(){
        var s = raw().items||{};
        document.querySelectorAll('#mdb tbody tr').forEach(function(tr){
          var it = s[tr.dataset.id]||{};
          tr.dataset.prep = it.st==='done' ? 'yes' : 'no';
          var b = tr.querySelector('.qprep');
          b.textContent = it.st==='done' ? '✓ Practised' : 'Mark practised';
          b.classList.toggle('on', it.st==='done');
        });
      }
      document.addEventListener('click', function(e){
        var b = e.target.closest('.qprep'); if(!b) return;
        var tr = b.closest('tr'), cur = LP.get(tr.dataset.id).st;
        LP.set(tr.dataset.id, {st: cur==='done'? null : 'done'});
        paint();
      });
      paint();
    })();
    '''

    body = (
        sec('header', 'Recent LinkedIn interview research', kpis + warn + method,
            kicker='Pass 2 · %s' % R2.DATE, why='Updated independently of the preparation content') +
        sec('mdb', 'Master question database', mdb, kicker='Every reported question',
            why='%d questions · filter by round, year, level, location, confidence' % len(ALL)) +
        sec('top', 'Top lists and pattern analysis', tops, kicker='Priorities') +
        sec('gaps', 'Coverage against your workspace', gap, kicker='Gap analysis') +
        sec('general', 'General topics and inferences', grid([gen, inf], 'g2'), kicker='Kept separate') +
        sec('showing', 'What recent LinkedIn interviews are actually showing', grid([summary], 'g2'), kicker='Summary') +
        sec('sources', 'Sources', card(table(['Source', 'Date', 'Kind', 'Note'], [
            ['[%s](%s)' % (s['name'], s['url']) if s['url'] else '**%s**' % s['name'], s['date'], s['kind'], s['note']]
            for s in R2.SRC.values()]) +
            note('Pass 1 sources (21 Sep) are listed on the <a href="index.html#sec-sources">dashboard</a> and remain valid. '
                 'To refresh: add entries to `src/research2.py`, bump `DATE`, and rebuild. Old entries stay so passes can be '
                 'compared.', '', 'Refreshing this'), title='Sources analysed in pass 2'), kicker='Provenance'))

    return page('05-research.html', 'Recent LinkedIn interview research',
                'Every question candidates have recently reported, cross-checked across sources, graded for confidence, and mapped onto your preparation.',
                body, round_id='', round_name='Research', crumb_tail='Research',
                hero_chips=[('', '%d reported questions' % len(ALL)), ('', '%d sources' % len(R2.SRC)),
                            ('', '%d high-confidence recurring' % len(hi_rec)), ('', 'Pass 2 · %s' % R2.DATE)],
                tail_js=tail)


def PATTERNS_TABLE(questions, simple=False):
    counts = {}
    for q in questions:
        counts.setdefault(q['pattern'], []).append(q)
    rows = []
    for pat, qs in sorted(counts.items(), key=lambda kv: -len(kv[1])):
        names = ', '.join(x['q'][:34] + ('…' if len(x['q']) > 34 else '') for x in qs[:3])
        if len(qs) > 3: names += ' +%d more' % (len(qs) - 3)
        if simple:
            rows.append(['**%s** (%d)' % (pat, len(qs)), names])
        else:
            indep = sum(1 for x in qs if x['rec'] == 'recurring')
            signal = ('**Recurring** — %d of %d from independent sources' % (indep, len(qs))) if indep >= 2 else 'Single reports'
            rows.append(['**%s** (%d)' % (pat, len(qs)), names, signal])
    return rows
