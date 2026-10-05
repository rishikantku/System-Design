# -*- coding: utf-8 -*-
"""02-ai-coding.html — the CWAI training platform page.

Order on the page follows the reader's path: understand the round → the playbook → the
questions (study mode) → exercises → timing and roadmap → the older material. Interview mode
lives on 02b-ai-simulator.html so answers are never one scroll away from the questions.
"""
from lib import *
import aic_research as AR
import aic_content as AC
import aic_study as AS
import qbank_cs as CS
from aicoding import FUND, EX, SCENARIOS, MOCKS
from aicoding_drills import DRILLS

SIM = '02b-ai-simulator.html'
AI_NAV = ('<h4>AI coding platform</h4>'
          '<a href="02-ai-coding.html">◆ Study &amp; playbook</a>'
          '<a href="02b-ai-simulator.html">◆ Interview simulator</a>'
          '<a href="02b-ai-simulator.html#tracker">◆ Weakness tracker</a>')


def src_links(keys):
    out = []
    for k in keys:
        s = AR.SOURCES[k]
        name = s['name'].split('—')[0].strip()
        if s['url']:
            out.append('<a href="%s"%s>%s</a> <small>(%s)</small>' % (
                s['url'], '' if s['url'].endswith('.html') else ' target="_blank" rel="noopener"', esc(name), esc(s['date'])))
        else:
            out.append('%s <small>(%s)</small>' % (esc(name), esc(s['date'])))
    return ' · '.join(out) or '<small>no source — see the grade</small>'


def gr(g): return Raw('<span class="gr %s">%s</span>' % (g, g))


def note_list(label, items, kind='bad'):
    return '<div class="note %s"><span class="lbl">%s</span>%s</div>' % (kind, esc(label), ul(items))


def listing(ref):
    cap, fn, what = ref
    if '|' in what:
        t, m = what.split('|', 1)
        body = CS.cs_member(fn, t, m)
    else:
        body = CS.cs_type(fn, what)
    return '<p class="src" style="margin:10px 0 4px"><b>%s</b></p>' % esc(cap) + code(body, file=fn.split('/')[-1])


def prio(q): return '<span class="prio %s">%s</span>' % (q['prio'], q['prio'])
def lab(q): return '<span class="lab %s">%s</span>' % (q['label'], esc(AR.LABELS[q['label']]))


def ul(items): return '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(x) for x in items)


def ladder(items):
    return '<ol class="ladder">%s</ol>' % ''.join(
        '<li><div><div class="lq">%s</div><div class="la">%s</div></div></li>' % (rich(q), rich(a)) for q, a in items)


# ================================================================ sections
def s_start():
    rows = [
        ('1', 'Understand the round', '#research', 'What is confirmed, what is reported, what is my inference'),
        ('2', 'Learn the playbook', '#workflow', 'The eight-step workflow, the prompt templates, what gets people rejected'),
        ('3', 'Study the questions', '#bank', '%d questions, tiered by evidence; full study mode in C#' % len(AR.Q)),
        ('4', 'Train judgement', '#review', '%d "would you ship this?" reviews, %d debugging exercises' % (len(AS.REVIEW), len(AS.DEBUG))),
        ('5', 'Run interviews', SIM, 'Ten rounds incl. five follow-up levels, five mocks, 30/45/60-minute timers, scored on the Staff standard'),
        ('6', 'Fix weaknesses', SIM + '#tracker', 'Per-skill history across sessions, with the exercises that train each'),
    ]
    cards = ''.join(
        '<a class="round" href="%s" style="text-decoration:none"><div class="num">%s</div><div class="rt">%s</div><div class="rd">%s</div></a>'
        % (h, n, esc(t), esc(d)) for n, t, h, d in rows)
    return sec('start', 'How to use this platform', '<div class="grid g3">%s</div>' % cards +
               note('Everything here assumes the module the recruiter pack describes: **60 minutes, CoderPad AI Assist, ordinary data-structure and algorithm '
                    'problems, AI use expected**. The questions are not predictions — they are what candidates have reported, graded by how well each report is supported.',
                    '', 'Scope'),
               kicker='Start here', why='Study here · interview on the simulator page')


def s_research():
    groups = [('CONFIRMED', 'LinkedIn said it'), ('REPORTED', 'Candidates reported it'), ('ADVICE', 'Preparation advice'), ('INFERENCE', 'My inference')]
    rows = []
    for g, _ in groups:
        for claim, grade, srcs, nt in AR.CLAIMS:
            if grade == g:
                rows.append([gr(grade), claim, Raw(src_links(srcs)), nt or '—'])
    claims = table(['Grade', 'Claim', 'Source and date', 'What it means for you'], rows)
    legend = table(['Grade', 'Means'], [[gr(g), d + {'CONFIRMED': ' — the pack, or a LinkedIn employee first-hand',
                                                                    'REPORTED': ' — a candidate described experiencing it',
                                                                    'ADVICE': ' — general guidance, not evidence about LinkedIn',
                                                                    'INFERENCE': ' — nobody reported it in these words'}[g]] for g, d in groups])
    srcs = table(['Source', 'Date', 'Kind', 'Grade'], [
        [Raw('<a href="%s"%s>%s</a>' % (s['url'], '' if s['url'].endswith('.html') else ' target="_blank" rel="noopener"', esc(s['name'])) if s['url'] else esc(s['name'])),
         s['date'], s['kind'], gr(s['grade'])] for s in AR.SOURCES.values()])
    nuance = note('Your brief says LinkedIn has stated candidates should "understand the problem first". **The pack does not say that.** It says the opposite of a rule: '
                  '"no prescribed workflow — reason first then accelerate, or explore with AI then refine". What it does say, in its own words, is '
                  '"critically evaluate AI-generated output rather than accepting it at face value". This page recommends understanding first because it is the '
                  'cheapest way to have something to check the assistant against — but that is my recommendation, graded INFERENCE, not LinkedIn\'s requirement. '
                  'If you are faster exploring with the assistant first, the pack says that is allowed.', 'warn', 'One correction to the brief')
    fresh = note('This pass (5 Oct 2026) added three reports the workspace did not have: a **Sep 2026 IC2 round with "LRU with counters" and hit/miss prediction**; '
                 'an AI-Engineer AI round where the interviewer **kept adding requirements to an LRU** (and the candidate over-engineered by prompting for each one); '
                 'and an SWE-ML AI round asking for **rejection sampling explained mathematically before coding**. It also found a LinkedIn employee\'s Oct 2025 '
                 'comment that the round means "a lot more code to write". No source publishes the minute-by-minute timing, and no 2026 report is from a Staff '
                 'candidate specifically — the Staff-level evidence is the LFU+GetRank report and the pack itself.', 'good', 'What is new in this pass')
    return sec('research', 'What the research actually says', legend + fresh + nuance + card(claims, title='Claims, by grade') +
               acc('All %d sources, with dates' % len(AR.SOURCES), srcs),
               kicker='Research · pass 4', why='Updated %s · every claim graded and dated' % AR.DATE)


def s_model():
    trad = '<div class="loop">%s</div>' % ' <i>→</i> '.join('<span>%s</span>' % esc(x) for x in AC.TRADITIONAL)
    own = {'Understand', 'Clarify', 'Design', 'Decide what to delegate', 'Inspect output', 'Validate', 'Absorb a requirement change',
           'Reason about production', 'Explain the trade-offs'}
    ai = '<div class="loop">%s</div>' % ' <i>→</i> '.join('<span class="%s">%s</span>' % ('own' if x in own else '', esc(x)) for x in AC.AI_ASSISTED)
    cards = ''.join(card('<p>%s</p>' % rich(b), title=t) for t, b in AC.WHAT_CHANGES)
    return sec('model', 'What is LinkedIn actually testing?',
               card('<h4>Traditional coding round</h4>' + trad +
                    '<h4 style="margin-top:14px">AI-assisted round</h4>' + ai +
                    '<p class="src" style="margin-top:8px">Blue steps are yours alone. The assistant can help with the grey ones.</p>',
                    title='Two different loops') +
               '<div class="principle">%s</div>' % esc(AC.PRINCIPLE) +
               '<div class="grid g2">%s</div>' % cards,
               kicker='The model', why='What changes when typing is free')


def s_staff():
    t = table(['Dimension', 'A senior engineer shows', 'A staff engineer shows'], [[a, b, c] for a, b, c in AC.STAFF])
    return sec('staff', 'The Staff-level bar', t + senior_staff(
        '"I used the AI to write the LFU cache, and it passed the tests."',
        '"I designed frequency buckets with an LRU list inside each, and had the assistant write the list plumbing. I rejected its ConcurrentDictionary suggestion '
        'because it protects the map, not the lists. GetRank is O(distinct frequencies), not O(1) as it claimed; if rank were hot I would add an order-statistics tree."'),
        kicker='Level', why='"I use AI to move faster; I own the decisions."')


def s_playbook():
    items = ''.join(
        '<div class="wf-step"><div class="wf-n">%d</div><div><h3>%s</h3><p>%s</p></div></div>' % (i + 1, esc(t), rich(b))
        for i, (t, b) in enumerate(AC.PLAYBOOK))
    return sec('playbook', 'LinkedIn AI Coding — Interview Playbook', card(items), kicker='Playbook', why='15 parts · each links to its detail below')


def s_workflow():
    out = ''
    for w in AC.WORKFLOW:
        mins = w['mins'] + ' min' if w['mins'][0].isdigit() else ('no fixed slot' if w['mins'] == '—' else w['mins'])
        out += ('<div class="wf-step"><div class="wf-n">%d</div><div><h3 id="wf-%d">%s</h3><div class="mins" style="margin:-4px 0 6px">%s</div>%s'
                '<div class="say">%s</div><div class="kv"><b>AI here</b><div>%s</div><b>Trap</b><div>%s</div></div></div></div>') % (
            w['n'], w['n'], esc('Step %d — %s' % (w['n'], w['name'])), esc(mins), ul(w['do']), esc(w['say']), rich(w['ai']), rich(w['trap']))
    return sec('workflow', 'The core workflow — eight steps', card(out) +
               note('Minutes are for the 60-minute module and are my plan, not a published one. Step 5 has no slot because it happens every time code arrives.', ''),
               kicker='Workflow', why='Understand → design → delegate → generate → review → test → modify → defend')


def s_prompts():
    out = ''
    for i, p in enumerate(AC.PROMPTS):
        out += ('<div class="ptpl"><div class="ph"><b>%s</b><span class="when">%s</span>'
                '<button class="sbtn" data-copytext="%d">Copy</button></div><pre id="ptpl-%d">%s</pre>'
                '<ul>%s</ul></div>') % (esc(p['name']), esc(p['when']), i, i, esc(p['text']),
                                        ''.join('<li>%s</li>' % rich(w) for w in p['why']))
    js_note = note('Every template has the same three parts: **context** (your code or interface), **constraint** (what must not change), **output shape** (only this; '
                   'no rewrite; list first). The *why* under each is the part to learn — the words will differ on the day.', 'good', 'The pattern')
    return sec('prompts', 'AI prompting for the interview', js_note + out, kicker='Prompting', why='%d templates, each with why it works' % len(AC.PROMPTS))


def s_rejected():
    out = ''.join('<h4>%s</h4><div class="bvg"><div class="bad"><div class="h">BAD AI USAGE</div>%s</div>'
                  '<div class="good"><div class="h">GOOD AI USAGE</div>%s</div></div>' % (esc(t), rich(b), rich(g))
                  for t, b, g in AC.REJECTED)
    return sec('rejected', 'What gets candidates rejected', '<div class="rej">%s</div>' % out, kicker='Failure modes',
               why='%d patterns · bad versus good' % len(AC.REJECTED))


def s_checklist():
    out = ''
    for h, qs in AC.CHECKLIST:
        out += '<h4>%s</h4>' % esc(h) + ''.join('<label><input type="checkbox"> <span>%s</span></label>' % esc(q) for q in qs)
    return sec('checklist', 'Staff engineer AI coding checklist', card('<div class="chk">%s</div>' % out +
               '<p class="src" style="margin-top:10px">Ticks are not saved — this is for running through before you say "done", every time.</p>'),
               kicker='Before you submit')


def q_study(q):
    qid = q['id']
    if q['study'] == 'full':
        s = AS.STUDY[qid]
        stages = [
            stage('1 · Problem', '<p class="lead">%s</p>' % rich(s['problem'])),
            stage('2 · Requirements', ul(s['reqs'])),
            stage('3 · Key insight', note(s['insight'], 'good')),
            stage('4 · Design', '<p>%s</p>' % rich(s['design'])),
            stage('5 · Data structures — and why each C# type', table(['Type', 'Why'], [[a, b] for a, b in s['structs']])),
            stage('6 · Algorithm', ul(s['algo'])),
            stage('7 · C# implementation', ''.join(listing(r) for r in s['code']) +
                  '<p class="src">Compiled and tested: <code>src/cs/aicoding</code>, <code>dotnet run -c Release</code> → 126 assertions, 0 failures.</p>'),
            stage('8 · Tests', ul(s['tests'])),
            stage('9 · Complexity', '<p>%s</p>' % rich(s['cx'])),
            stage('10 · Follow-ups — the ladder', ladder(s['ladder'])),
            stage('11 · Concurrency', '<p><b>What happens if two threads run this at once?</b> %s</p>' % rich(s['conc'])),
            stage('12 · Production', ul(s['prod'])),
            stage('13 · AI prompting strategy — and what assistants get wrong here',
                  '<h4>Prompting</h4>' + ul(s['ai']) + note_list('Assistant defects to look for', s['traps'])),
        ] + extra_stages(qid)
    else:
        kind, ref = q['study'].split(':')
        d = AS.LINKED[qid]
        link = ('09-question-bank.html#%s' % ref) if kind == 'qbank' else '#drills'
        where = 'the question bank (14-part worked solution, C#, tested)' if kind == 'qbank' else 'the CWAI drill on this page'
        stages = [
            stage('Full solution', '<div class="note"><b>The complete study mode</b> — statement, walkthrough, C#, tests, complexity — is in '
                                   '<a href="%s">%s</a>. Below is the AI-round layer on top of it.</div>' % (link, esc(where))),
            stage('Key insight', note(d['insight'], 'good')),
            stage('Follow-up ladder', ladder(d['ladder'])),
            stage('Concurrency', '<p><b>What happens if two threads run this at once?</b> %s</p>' % rich(d['conc'])),
            stage('AI prompting strategy — and what assistants get wrong here', '<h4>Prompting</h4>' + ul(d['ai']) +
                  '<h4>Defects to look for</h4>' + ul(d['traps'])),
        ] + extra_stages(qid)
    return stages


def fu_html(qid):
    out = ''
    for lv in range(1, 6):
        items = AS.FU[qid].get(lv, [])
        if not items: continue
        out += '<h4>Level %d — %s</h4><ol class="ladder">%s</ol>' % (lv, AS.LEVELS[lv], ''.join(
            '<li><div><div class="lq">%s</div><div class="la">%s</div></div></li>' % (rich(q), rich(a)) for q, a in items))
    return out


def cs_html(feats):
    if not feats:
        return '<p class="src">No library feature here worth a deep-dive — the questions will be about the maths.</p>'
    return ''.join('<h4>%s</h4>' % esc(f) + ''.join('<p><b>%s</b> %s</p>' % (rich(q), rich(a)) for q, a in AS.CSHARP[f]) for f in feats)


def extra_stages(qid):
    return [stage('Follow-up engine — five levels', fu_html(qid), 'correctness → complexity → concurrency → scale → production'),
            stage('C# deep-dive — asked only if your solution uses it', cs_html(AS.FEATURES[qid]))]


def s_bank():
    summary_rows = []
    for q in AR.Q:
        summary_rows.append([Raw(prio(q)), Raw('<a href="#q-%s">%s</a>' % (q['id'], esc(q['title']))),
                             AR.CATS[q['cat']], Raw(lab(q)), q['date']])
    means = {'multi': 'Two or more independent candidate reports of this question in LinkedIn\'s AI-enabled round',
             'single': 'One candidate report from LinkedIn\'s AI-enabled round (or one first-hand report of the same question)',
             'idb': 'From the InterviewDB set you supplied — LinkedIn coding, round not stated',
             'derived': 'Not reported as a question; built because the research says the follow-ups go here',
             'pattern': 'Not reported; practises a pattern the reported follow-ups need'}
    evleg = table(['Label', 'Means'], [[Raw('<span class="lab %s">%s</span>' % (k, esc(v))), means[k]] for k, v in AR.LABELS.items()]) + \
        table(['Priority', 'Means'], [[Raw('<span class="prio P0">P0</span>'), 'Must master — caches, logging, structured data, intervals'],
                                      [Raw('<span class="prio P1">P1</span>'), 'High priority — graph/routing, randomisation'],
                                      [Raw('<span class="prio P2">P2</span>'), 'Supporting practice for the follow-ups (concurrency primitives, trees, counters)']])
    filt = ('<div class="filters" data-filter-scope="#qcards > details">'
            + ''.join('<button class="fchip" data-fk="prio" data-fv="%s">%s</button>' % (t, t) for t in ('P0', 'P1', 'P2'))
            + ''.join('<button class="fchip" data-fk="lab" data-fv="%s">%s</button>' % (k, esc(v)) for k, v in AR.LABELS.items())
            + ''.join('<button class="fchip" data-fk="cat" data-fv="%s">%s</button>' % (k, esc(v)) for k, v in AR.CATS.items())
            + '<input class="search" placeholder="Search questions…"><span class="count"></span></div>')
    cards = ''
    for q in AR.Q:
        iid = reg('ai', 'ai.q.' + q['id'], AR.CATS[q['cat']], q['title'], weight={1: 3, 2: 2, 3: 1}[q['tier']], kind='question',
                  level='T%d' % q['tier'])
        meta = ('<div class="qmeta">'
                '<div class="row"><b>Reported wording</b><div>%s</div></div>'
                '<div class="row"><b>Source · date</b><div>%s</div></div>'
                '<div class="row"><b>Evidence</b><div>%s</div></div>'
                '<div class="row"><b>Variation</b><div>%s</div></div>'
                '<div class="row"><b>Follow-ups</b><div>%s</div></div>'
                '<div class="row"><b>Why %s</b><div>%s</div></div></div>') % (
            rich(q['wording']), src_links(q['src']), lab(q), rich(q['variation']),
            ' → '.join(esc(f) for f in q['follow']), q['prio'], rich(q['why']))
        modes = ('<div class="modebar"><span class="tag p0">MODE A · STUDY</span> below, step by step'
                 '<a class="tbtn pri" href="%s#q=%s">MODE B · Interview mode →</a></div>') % (SIM, q['id'])
        stages = [stage('Evidence', meta, 'source, date, wording')] + q_study(q)
        body = ('<div data-id="%s" data-label="%s">%s<div class="revall"><button class="sbtn" data-revall>Reveal all</button></div>%s%s</div>' % (
            iid, esc(q['title']), modes, ''.join(stages),
            tracker(iid, statuses=[('solved', 'Can do it cold'), ('revise', 'Needs revision'), ('failed', 'Struggled'), ('hint', 'Needed the answer')])))
        title = '<span id="q-%s"></span>%s <b>%s</b> <span class="src">· %s</span>' % (q['id'], prio(q), esc(q['title']), esc(AR.CATS[q['cat']]))
        cards += acc(title, body, lab(q), raw=True).replace(
            '<details class="acc"', '<details class="acc" data-prio="%s" data-cat="%s" data-lab="%s"' % (q['prio'], q['cat'], q['label']), 1)
    return sec('bank', 'Question bank — prioritised, every question labelled',
               note('No question here is a prediction. **Priority** follows your P0/P1 list; the **label** says how each question is evidenced — read it before trusting the priority. '
                    'Nine questions are studied in full on this page with compiled, tested C#; the InterviewDB ones link to their full worked solutions on the question-bank page, '
                    'with the AI-round layer here: ladder, five-level follow-ups, concurrency, prompting, assistant defects, C# deep-dive.', '', 'How to read it') +
               evleg + table(['Tier', 'Question', 'Category', 'Evidence', 'Reported'], summary_rows) + filt + '<div id="qcards">%s</div>' % cards,
               kicker='Questions', why='%d questions · %d P0 · two modes each' % (len(AR.Q), sum(1 for q in AR.Q if q['prio'] == 'P0')))


def s_concurrency():
    prims = table(['C# primitive', 'What it gives you', 'Where it appears here'], [list(r) for r in AC.CONC_PRIMS])
    topics = ''.join('<h3 id="cc-%d">%s</h3><p>%s</p>' % (i, esc(t), rich(b)) for i, (t, b) in enumerate(AC.CONC_TOPICS))
    rows = []
    for qid in ['lru', 'lrucount', 'lfurank', 'logging', 'intervals', 'records', 'queue', 'window']:
        s = AS.STUDY[qid]
        title = next(q['title'] for q in AR.Q if q['id'] == qid)
        rows.append([Raw('<a href="#q-%s">%s</a>' % (qid, esc(title))), s['conc']])
    two = table(['Problem', '"What happens if two threads run this at once?" → where the boundary is'], rows)
    return sec('concurrency', 'Concurrency — the pivot to expect',
               note('Every source that describes the AI round\'s follow-ups names concurrency. Ask two questions of every method that writes — including reads that write: '
                    '**"What happens if two threads execute this simultaneously?"** and **"Where exactly is the synchronization boundary?"** The boundary is the '
                    'invariant: whatever must be true across several fields must change inside one critical section.', 'warn', 'The two questions') +
               card(two, title='The two questions, answered for each problem') +
               card(prims, title='C# primitives, and why each') + card(topics, title='Topics'),
               kicker='Special focus', why='Thread-safe LRU · races · granularity · deadlock · cleanup · shutdown')


def s_followups():
    lv = table(['Level', 'The interviewer asks', 'Only when'], [
        ['1 · Correctness', 'Edge cases? Empty input? Duplicates? Null or missing values? Invalid input?', 'Always'],
        ['2 · Complexity', 'Time? Space? Can we improve it? Where is the bottleneck? What happens as N grows?', 'Always'],
        ['3 · Concurrency', 'Can several threads call this? What is shared? Where is the race? Lock or concurrent collection? Could it deadlock? Could synchronisation become the bottleneck? Can we reduce contention?', 'There is shared mutable state — otherwise the right answer is "nothing is shared"'],
        ['4 · Scale', '10× traffic? 100×? Millions of objects? Very large input? Memory pressure? Hot keys? High contention?', 'The structure lives in a long-running process or handles real traffic'],
        ['5 · Productionisation', 'Deploy? Metrics? What to log? What to alert on? Tests? A dependency fails? Recovery? During a deployment? Debugging an incident?', 'It would run in production'],
    ])
    arc = '<div class="loop">%s</div>' % ' <i>→</i> '.join('<span>%s</span>' % x for x in
                                                         ['Initial problem', 'Correct solution', 'Requirement change', 'Correctness', 'Complexity', 'Concurrency', 'Scale', 'Productionisation'])
    rows = []
    for q in AR.Q:
        lad = AS.STUDY[q['id']]['ladder'] if q['study'] == 'full' else AS.LINKED[q['id']]['ladder']
        rows.append([Raw('<a href="#q-%s">%s</a>' % (q['id'], esc(q['title']))), Raw(' → '.join('<b>L%d</b> %s' % (i + 1, esc(a)) for i, (a, _) in enumerate(lad)))])
    per = ''.join(acc(titled(q['title'], q['prio']), fu_html(q['id']), raw=True) for q in AR.Q)
    return sec('followups', 'The follow-up engine', card(arc + '<p>The initial question is not where the round is decided. Once your solution is correct the interviewer '
               'changes it, then walks it through five levels. Each question below has its own follow-ups at each level, with what a strong answer covers — and only the '
               'ones that arise naturally from that problem. A question with no shared state gets "nothing is shared" as the strong concurrency answer, not a lock.</p>',
               title='The arc') + lv + card(per, title='Per question — five levels') +
               acc('Requirement-change ladders, all questions', table(['Question', 'Ladder'], rows)),
               kicker='Special focus', why='Correctness → complexity → concurrency → scale → production')


def s_csharp():
    out = ''.join(acc(titled(f, '%d questions' % len(qs)), ''.join('<p><b>%s</b><br>%s</p>' % (rich(q), rich(a)) for q, a in qs), raw=True) for f, qs in AS.CSHARP.items())
    return sec('csharp', 'C# deep-dive questions', note('The interviewer may ask how a C# feature you used actually behaves. **Only when it is in your solution** — this is '
               'not .NET trivia. Each answer below is tied to a defect elsewhere on this page where the behaviour bites.', '', 'When this comes up') + out,
               kicker='C#', why='Dictionary · ConcurrentDictionary · lock · async/await · LINQ · and the types used here')


def s_testing():
    t = table(['Category', 'What to cover', 'Example from this page'], [list(r) for r in AC.TESTING])
    gen = '''// Assistant output for "generate adversarial tests for LruTtlCache(capacity: 2)".
// Exactly one of these expected values is wrong. Which, and why?
clock.NowMs = 0;  c.Put(1, 10, ttlMs: 100);
clock.NowMs = 100; Assert(c.TryGet(1, out _) == true);   // still valid at the TTL boundary
clock.NowMs = 0;  c.Put(2, 20, 100); c.Put(3, 30, 100); c.TryGet(2, out _); c.Put(4, 40, 100);
Assert(c.TryGet(3, out _) == false);                    // 3 was least recently used
c.Put(4, 41, 100);
Assert(c.Count == 2);                                    // update in place, no growth'''
    ans = ('The first: **at `now == expiresAt` the entry is expired** — the contract (and LruTtlCache) uses `now >= ExpiresAt`. The assistant assumed "valid until after '
           'the TTL". A generated test with a wrong expectation does not just fail to catch the bug; it *enforces* it. That is why every generated expected value gets read.')
    return sec('testing', 'Testing — and auditing generated tests',
               t + card('<ol><li>Write the two or three tests that pin the invariant yourself.</li>'
                        '<li>Ask for adversarial tests with the Tests template — including "state why the expected value is correct".</li>'
                        '<li>Read every expected value against your contract, not against the code.</li>'
                        '<li>Run them. A failure is either a bug or a wrong test — decide which before changing anything.</li>'
                        '<li>Keep a regression test for every bug you fix.</li></ol>', title='Asking AI for tests, then verifying them') +
               card(code(gen) + stage('Reveal', note(ans, 'good')), title='Exercise: spot the wrong generated test'),
               kicker='Testing', why='Happy · boundary · empty · invalid · large · duplicate · concurrent')


def s_review():
    out = ''
    for r in AS.REVIEW:
        iid = reg('ai', 'ai.rev.' + r['id'], 'Code review', r['title'], weight=1, kind='review')
        body = CS.cs_type('aicoding/Review.cs', r['cls'], comment=True)
        stages = [
            stage('The assistant\'s answer', '<p>%s</p>' % rich(r['ctx']) + code(body, file='assistant output') +
                  '<div class="verdict-q"><span class="lbl">Would you ship this?</span>'
                  '<span class="src">Decide, name the defect and the input that breaks it, before revealing.</span></div>'),
            stage('Reveal — the defect', '<span class="kind">%s</span>' % esc(r['kind']) + note(r['answer'], 'bad')),
            stage('The fix', '<p>%s</p><p class="src">Proven in Tests.cs: %s</p>' % (rich(r['fix']), esc(r['test']))),
        ]
        out += practice(iid, titled('%s %s' % (r['id'], r['title']), r['kind']), stages, tag('p1', r['kind']), label=r['title'],
                        statuses=[('solved', 'Found it'), ('hint', 'Found it late'), ('failed', 'Missed it')])
    return sec('review', 'AI code review — would you ship this?',
               note('Each listing is written the way an assistant plausibly returns it: tidy, commented, compiles, passes the obvious test. Each has one defect that matters. '
                    'Every defect is reproduced by a test in `src/cs/aicoding/Tests.cs`, so none of them is a straw man — the race conditions corrupted in every stress run.',
                    'warn', 'Do not reveal first') + out,
               kicker='Exercises', why='%d exercises · race · deadlock · eviction · TTL · complexity · leak · off-by-one · async · API' % len(AS.REVIEW))


def s_debugging():
    out = ''
    for d in AS.DEBUG:
        iid = reg('ai', 'ai.dbg.' + d['id'], 'Debugging', d['title'], weight=1, kind='debug')
        body = CS.cs_type('aicoding/Debug.cs', d['cls'], comment=False)
        stages = [
            stage('Symptom and code', '<div class="symptom">%s</div>' % esc(d['symptom']) + code(body, file='Debug.cs')),
            stage('Hint', '<p>%s</p>' % rich(d['hint']), 'only if stuck after 3 minutes'),
            stage('Cause', note(d['answer'], 'bad')),
            stage('Fix', '<p>%s</p>' % rich(d['fix'])),
        ]
        out += practice(iid, titled('%s %s' % (d['id'], d['title']), 'debug'), stages, tag('p1', 'debug'), label=d['title'],
                        statuses=[('solved', 'Found it'), ('hint', 'Needed the hint'), ('failed', 'Missed it')])
    fixes = acc('The tested fixes (Fixes class)', code(CS.cs_type('aicoding/Debug.cs', 'Fixes'), file='Debug.cs'))
    return sec('debugging', 'Debugging exercises', note('Reproduce before you fix: write the test that shows the symptom, form two hypotheses, then read. '
                                                         'The symptoms are phrased as a user would report them, not as the cause.', '', 'Method') + out + fixes,
               kicker='Exercises', why='%d broken implementations' % len(AS.DEBUG))


def s_timing():
    colors = ['#5c6bc0', '#26a69a', '#0a66c2', '#2e7d32', '#ef6c00', '#c62828', '#6a1b9a']
    out = ''
    for mins in (60, 45, 30):
        plan = AC.TIME_PLANS[mins]
        bar = ''
        for i, (rng, what, _) in enumerate(plan):
            a, b = [int(x) for x in rng.split('–')]
            bar += '<div style="flex:%d;background:%s" title="%s min · %s">%s</div>' % (b - a, colors[i % len(colors)], rng, esc(what), esc(what))
        rows = table(['Minutes', 'Phase', 'What'], [[r, w, d or '—'] for r, w, d in plan]) if mins == 60 else ''
        out += '<h4>%d-minute mode%s</h4><div class="tplan">%s</div>%s' % (
            mins, ' — the real module length (pack)' if mins == 60 else ' — practice compression', bar, rows)
    return sec('timing', 'Time management', note('The pack fixes **60 minutes**. Nobody has published how those minutes divide, so the splits below are mine, built from the '
                                                  'reported arc and the most-reported mistake (too long on the first version). The 45 and 30-minute modes are for drilling, not '
                                                  'a claim about the format.', 'warn', 'Graded INFERENCE') + card(out) +
               '<p><a class="tbtn pri" href="%s">Run a timed session on the simulator →</a></p>' % SIM,
               kicker='Timing', why='60 real · 45 and 30 for practice')


def s_roadmap():
    out = ''
    for p in AC.ROADMAP:
        iid = reg('ai', 'ai.phase.%d' % p['n'], 'Roadmap', 'Phase %d — %s' % (p['n'], p['name']), weight=1, kind='phase')
        out += ('<div class="phase" data-id="%s" data-label="%s"><div class="pn">%d</div><div><h3>%s <span class="src">· %s</span></h3>'
                '<div class="grid4"><div><b>STUDY</b>%s</div><div><b>PRACTISE</b>%s</div><div><b>MEASURE</b>%s</div><div><b>MOVE ON WHEN</b>%s</div></div>%s</div></div>') % (
            iid, esc(p['name']), p['n'], esc(p['name']), esc(p['days']), rich(p['study']), rich(p['practice']), rich(p['measure']), rich(p['exit']),
            tracker(iid, statuses=[('done', 'Exit criterion met'), ('revise', 'In progress')], note_ph='What you measured…'))
    return sec('roadmap', 'Study roadmap — ten days', card(out), kicker='Plan', why='Study → practise → measure → move on')


def s_drills():
    html = ('<div class="filters" data-filter-scope="#drills > details"><input class="search" placeholder="Search drills…"><span class="count"></span></div><div id="drills">')
    for d in DRILLS:
        did = reg('ai', 'ai.drill.' + d['id'], d['topic'], d['title'], weight=2, kind='drill')
        stages = [
            stage('Problem', '<p class="lead">%s</p>' % rich(d['problem']), '%d minutes' % d['mins']),
            stage('Clarify first', ul(d['clarify']), 'before you touch the assistant'),
            stage('Your plan — write it before prompting', note(d['plan'], 'warn', 'The structure is yours')),
            stage('Prompts worth using', '<ul>%s</ul>' % ''.join('<li><code>%s</code></li>' % esc(x.strip('"')) for x in d['prompts'])),
            stage('Verify — the tests you run yourself', ul(d['verify'])),
            stage('Reference solution (C#)', code(d['code'])),
            stage('What assistants get wrong here', note_list('Defects to look for', d['traps'])),
            stage('Follow-ups', ul(d['follow'])),
            stage('Self-evaluation', ul(d['evalpts'])),
        ]
        html += practice(did, titled(d['title'], d['topic']), stages, tag('p0', '%d min' % d['mins']), label=d['title'],
                         statuses=[('solved', 'Did it with AI'), ('revise', 'Needs revision'), ('failed', 'Struggled')])
    return sec('drills', 'More CWAI drills — ordinary problems, run the AI way', html + '</div>', kicker='Practice', why='%d drills from the first build' % len(DRILLS))


def s_background():
    fund = ''
    for name, what, angle, gotcha in FUND:
        fid = 'ai.f.' + re.sub(r'[^a-z]+', '', name.lower())[:14]
        reg('ai', fid, 'Fundamentals', name, weight=1, kind='concept')
        fund += acc(titled(name, 'concept'), '<div data-id="%s" data-label="%s"><p>%s</p><p><b>Interview angle.</b> %s</p>%s%s</div>' % (
            fid, esc(name), rich(what), rich(angle), note(gotcha, 'warn', 'Gotcha'),
            tracker(fid, statuses=[('solved', 'Know it cold'), ('revise', 'Needs revision'), ('failed', 'Shaky')], note_ph='Two sentences from memory…')), '', raw=True)
    ex = ''
    for e in EX:
        eid = reg('ai', 'ai.ex.' + e['id'], e['topic'], e['title'], weight=2, kind='exercise')
        stages = [stage('Requirement', rich(e['req'])), stage('Clarify first', ul(e['clarify'])), stage('Design', rich(e['design'])),
                  stage('Code (C#)', code(e['code'])), stage('Failure modes', ul(e['fails'])), stage('Progressive follow-ups', '<ol>%s</ol>' % ''.join('<li>%s</li>' % rich(p) for p in e['prog'])),
                  stage('Production note', rich(e['prod']))]
        ex += practice(eid, titled(e['title'], e['topic']), stages, tag('p0', e['topic']), label=e['title'],
                       statuses=[('solved', 'Built it'), ('revise', 'Needs revision'), ('failed', 'Struggled')])
    sc = ''
    for s in SCENARIOS:
        sid = reg('ai', 'ai.sc.' + s['id'], 'Interview simulation', s['title'], weight=2, kind='scenario')
        stages = [stage(l, '<p class="lead">%s</p>%s' % (rich(r), note(g, 'good', 'What a strong answer covers')), 'interviewer adds this') for l, r, g in s['steps']]
        sc += practice(sid, titled(s['title'], '%d steps' % len(s['steps'])), stages, tag('new', 'progressive'), label=s['title'],
                       statuses=[('solved', 'Ran it'), ('revise', 'Needs revision'), ('failed', 'Struggled')])
    mk = ''
    for mid, title, q, rub, secs in MOCKS:
        mk += card(mock_block(reg('ai', 'ai.mock.' + mid, 'Mock interviews', title, weight=3, kind='mock'), q, 'AI Coding', rub, secs), title=title)
    return sec('background', 'Background — AI engineering, not CWAI',
               note('The first build of this page treated the round as "building AI systems". The pack corrected that: CWAI is ordinary coding with an assistant. '
                    'This material is kept — your progress on it is saved — because it is useful depth for the design round and for ML-platform teams. '
                    'It is not what the AI coding round tests.', 'warn', 'Read this first') +
               acc('AI engineering fundamentals (%d concepts)' % len(FUND), fund) +
               acc('LLM-system coding exercises (%d)' % len(EX), ex) +
               acc('LLM-system scenarios (%d)' % len(SCENARIOS), sc) +
               acc('Earlier mocks (%d)' % len(MOCKS), mk),
               kicker='Reference', why='Collapsed · demoted, not deleted')


COPY_JS = r'''
function openHash(){
  var id = decodeURIComponent(location.hash.slice(1)); if (!id) return;
  var el = document.getElementById(id); if (!el) return;
  var d = el.closest('details'); if (d && !d.open) { d.open = true; setTimeout(function(){ el.scrollIntoView({block:'start'}); }, 30); }
}
window.addEventListener('hashchange', openHash); document.addEventListener('DOMContentLoaded', openHash);
document.querySelectorAll('[data-copytext]').forEach(function(b){
  b.addEventListener('click', function(){
    var pre = document.getElementById('ptpl-' + b.dataset.copytext);
    navigator.clipboard.writeText(pre.textContent).then(function(){ window.LPtoast && LPtoast('Template copied'); });
  });
});
'''


def build():
    body = (s_start() + sec('official', 'The official module', official_module('ai'), kicker='From LinkedIn', why='Authoritative') +
            s_research() + s_model() + s_staff() + s_playbook() + s_workflow() + s_prompts() + s_rejected() + s_checklist() +
            s_bank() + s_followups() + s_concurrency() + s_csharp() + s_testing() + s_review() + s_debugging() + s_timing() + s_roadmap() +
            s_drills() + s_background())
    return page('02-ai-coding.html', 'Coding with AI — Staff training platform',
                'Study, practise and measure for LinkedIn\'s 60-minute AI-assisted coding module: a familiar problem, an assistant in the pad, and follow-ups that '
                'pivot to concurrency and production. You own every decision the assistant types.',
                body, round_id='ai', round_name='Coding with AI', crumb_tail='02 Coding with AI', nav_html=AI_NAV,
                extra_head='\n<link rel="stylesheet" href="assets/aic.css">',
                hero_chips=[('', '%d questions' % len(AR.Q)), ('', '%d code reviews' % len(AS.REVIEW)), ('', '%d debugging' % len(AS.DEBUG)), ('', '5-level follow-ups'),
                            ('', '%d prompt templates' % len(AC.PROMPTS)), ('', 'C# · 126 tests')],
                tail_js=COPY_JS)
