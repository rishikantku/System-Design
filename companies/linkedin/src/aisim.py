# -*- coding: utf-8 -*-
"""02b-ai-simulator.html — interview mode, mocks, scoring and the weakness tracker.

What the page can and cannot do, stated on the page itself: it runs the interview structure —
ten rounds, interviewer lines, flawed AI output to review, the five-level follow-up engine,
timer, notes, prompt log, scoring, history. It cannot judge free text. For a live interviewer it
hands a ready prompt to Claude; for a second opinion it hands over the transcript.
"""
import json
from lib import *
import aic_research as AR
import aic_content as AC
import aic_study as AS
import qbank_cs as CS
from aic_page import AI_NAV

MOCKS = [
 dict(id='m1', name='Mock 1 — Beginner AI usage', q='lru', mins=45, hints='round',
      focus='Learn the workflow. One familiar problem; "what the interviewer listens for" is revealed after each round so you can correct course.'),
 dict(id='m2', name='Mock 2 — Intermediate', q='records', mins=45, hints='round',
      focus='Multiple requirements on one codebase: typed models, malformed input, a 1 GB file. Delegate the boilerplate; own the error model.'),
 dict(id='m3', name='Mock 3 — Production follow-ups', q='logging', mins=60, hints='end',
      focus='The most recent Staff-level report. Four reported phases, then 10,000 threads, back-pressure and failing sinks. Hints only at the end.'),
 dict(id='m4', name='Mock 4 — Staff level', q='lfurank', mins=60, hints='end',
      focus='Ambiguous requirements and an evolving problem. Rank is undefined until you define it; the assistant will claim a complexity you must catch.'),
 dict(id='m5', name='Mock 5 — Full realistic LinkedIn AI coding round', q='surprise', mins=60, hints='none',
      focus='No hints. No solution. Question hidden until you start, drawn from P0 favouring the ones you have practised least. Strict 60 minutes. '
            'For realistic interviewer behaviour, copy the interviewer prompt into a separate Claude chat and answer there.'),
]


def flawed(rid):
    """The flawed listing for a review id (R*) or a broken one (D*), plus its reveal."""
    if rid.startswith('R'):
        r = next(x for x in AS.REVIEW if x['id'] == rid)
        return dict(id=rid, ctx=r['ctx'], code=code(CS.cs_type('aicoding/Review.cs', r['cls'])), kind=r['kind'], answer=rich(r['answer']), fix=rich(r['fix']))
    d = next(x for x in AS.DEBUG if x['id'] == rid)
    return dict(id=rid, ctx='The assistant produced this. A user later reported: ' + d['symptom'], code=code(CS.cs_type('aicoding/Debug.cs', d['cls'], comment=False)),
                kind='Bug', answer=rich(d['answer']), fix=rich(d['fix']))


def data():
    qs = {}
    for q in AR.Q:
        iv = AS.INTERVIEW[q['id']]
        rounds = [dict(kind='talk', name=n, say=s_, listen=l) for n, s_, l in iv[:4]]
        rounds[1]['cs'] = [dict(f=f, qs=[x[0] for x in AS.CSHARP[f]]) for f in AS.FEATURES[q['id']]]
        rounds.append(dict(kind='ship', name='Would you ship this?',
                           say='"Before we go further — the assistant produced this. Would you ship it?"',
                           listen=['A ship / do-not-ship decision with a reason', 'The specific defect', 'The input or interleaving that breaks it', 'The fix'],
                           flaw=flawed(AS.REVIEW_FOR[q['id']])))
        for lv in range(1, 6):
            items = AS.FU[q['id']].get(lv, [])
            if items:
                rounds.append(dict(kind='fu', name='Follow-up L%d — %s' % (lv, AS.LEVELS[lv]),
                                   say=' '.join('"%s"' % x[0] for x in items), listen=[x[1] for x in items]))
        qs[q['id']] = dict(title=q['title'], prio=q['prio'], label=AR.LABELS[q['label']], cat=AR.CATS[q['cat']], rounds=rounds)
    return dict(
        questions=qs, mocks=MOCKS,
        staff=[dict(key=k, name=n, a1=a, a3=b, a5=c) for k, n, a, b, c in AC.STAFF15],
        ai=[dict(key=k, name=n, q=qq, a1=a, a3=b, a5=c) for k, n, qq, a, b, c in AC.AI7],
        headlines=[dict(name=n, keys=k) for n, k in AC.HEADLINES],
        verdict=AC.VERDICT, plans={str(k): [dict(r=r, w=w) for r, w, _ in v] for k, v in AC.TIME_PLANS.items()},
        train=AC.TRAIN,
    )


def build():
    for m in MOCKS:
        reg('ai', 'ai.sim.' + m['id'], 'Simulator mocks', m['name'], weight=3, kind='mock')

    honesty = [
        ('pasted', 'I pasted AI code I could not explain line by line', 'caps AI-output verification and Verification at 2 — blocks PASS'),
        ('notests', 'I declared it done before running tests', 'caps Testing and Testing-with-AI at 2'),
        ('restart', 'I regenerated a whole class instead of modifying it on a requirement change', 'caps Adaptability at 2'),
        ('norej', 'I never rejected or corrected an AI suggestion', 'caps AI-output verification and Critical thinking at 3'),
        ('notime', 'I ran out of time before the production follow-ups', 'caps Production thinking and Scalability at 2'),
    ]
    honest_html = ''.join('<label><input type="checkbox" data-hon="%s"> <span>%s <small class="src">— %s</small></span></label>' % (k, esc(t), esc(c))
                          for k, t, c in honesty)

    runner = '''
<div class="sim" id="sim">
  <div class="sim-top">
    <select id="sim-q" aria-label="Question"></select>
    <select id="sim-mins" aria-label="Time mode"><option value="60">60 min (real)</option><option value="45">45 min</option><option value="30">30 min</option></select>
    <select id="sim-hints" aria-label="Hints"><option value="round">Hints after each round</option><option value="end">Hints at the end</option><option value="none">No hints (strict)</option></select>
    <button class="sbtn" id="sim-start">▶ Start interview</button>
    <span style="flex:1"></span>
    <span class="sim-clock" id="sim-clock">60:00</span>
    <span class="sim-phase" id="sim-phase"></span>
  </div>
  <div class="sim-body" id="sim-body">
    <p class="empty">Pick a question (or a mock below), a time mode and a hint level, then start. The question stays hidden until you do.</p>
  </div>
</div>'''

    score = '''
<div class="card" id="scorecard" style="display:none">
  <h3>Final evaluation — the Staff Engineer standard</h3>
  <p class="src">Score yourself honestly against the anchors, then use "Grade with Claude" for a second opinion on the same standard. Code that works does not score well on its own.</p>
  <h4>15 dimensions</h4><div class="score-grid" id="score-staff"></div>
  <h4 style="margin-top:14px">How you used AI — 7 checks</h4><div class="score-grid" id="score-ai"></div>
  <h4 style="margin-top:14px">Honesty checks — these cap scores, by design</h4>
  <div class="honest">%s</div>
  <div class="hl-grid" id="hl"></div>
  <div class="vbox"><span class="tot" id="tot">–</span><span class="vd" id="vd">—</span><span class="why2" id="vwhy">Score every item to get a verdict.</span></div>
  <div id="improve"></div>
  <div class="bar-row" style="display:flex;flex-wrap:wrap;gap:8px">
    <button class="sbtn" id="sim-save">💾 Save session to tracker</button>
    <button class="sbtn" id="sim-grade">📋 Grade with Claude</button>
    <button class="sbtn" id="sim-iv">📋 Copy interviewer prompt</button>
  </div>
</div>''' % honest_html

    mocks = ''.join(card('<p>%s</p><p class="src">%s · %d minutes · hints: %s</p><button class="sbtn" data-mock-run="%s">▶ Load this mock</button>%s' % (
        rich(m['focus']), 'random P0' if m['q'] == 'surprise' else esc(next(q['title'] for q in AR.Q if q['id'] == m['q'])),
        m['mins'], {'round': 'after each round', 'end': 'at the end', 'none': 'none'}[m['hints']], m['id'],
        tracker('ai.sim.' + m['id'], statuses=[('solved', 'Passed'), ('revise', 'Borderline'), ('failed', 'Failed')], note_ph='What the score said to fix…')
        .replace('<div class="track">', '<div class="track" style="margin-top:10px">')),
        title=m['name'], cls='mockcard').replace('<div class="card mockcard"', '<div class="card mockcard" data-id="ai.sim.%s" data-label="%s"' % (m['id'], esc(m['name'])), 1)
        for m in MOCKS)

    staff = table(['Dimension', '1 looks like', '3 looks like', '5 looks like'], [[n, a, b, c] for _, n, a, b, c in AC.STAFF15])
    ai = table(['AI check', 'The question', '1', '3', '5'], [[n, q, a, b, c] for _, n, q, a, b, c in AC.AI7])
    names = {k: n for k, n, *_ in AC.STAFF15}
    names.update({k: n for k, n, *_ in AC.AI7})
    heads = table(['Headline score /10', '= 2 × the mean of'], [[n, ', '.join(names[k] for k in ks)] for n, ks in AC.HEADLINES])
    v = AC.VERDICT
    rules = note('**PASS** — the mean of the eight headline scores ≥ %.1f, **and** AI Collaboration ≥ 6, **and** Staff-Level Judgment ≥ 6, **and** AI-output verification ≥ 3, '
                 '**and** nothing scored 1.<br>**BORDERLINE** — mean ≥ %.1f, or a passing mean that failed a gate.<br>**FAIL** — anything else.<br><br>'
                 'The gates are the point: working code with blindly accepted AI output fails the verification gate and cannot pass, however high everything else is. '
                 'This calibration is **mine**. The only published scale is Hello Interview\'s report of a 4-point scale where 3 passes.' % (v['pass_mean'], v['border_mean']),
                 'warn', 'Verdict rules')

    tracker_html = '''
<div class="card"><div id="wk-summary" class="empty">No sessions yet. Run an interview and save it.</div></div>
<div class="card"><h3>Per-skill history</h3><div class="tw"><table class="wk-table"><thead><tr><th>Skill</th><th>Latest</th><th>Average of last 3</th><th>Best</th><th>Trend</th><th>Train it</th></tr></thead><tbody id="wk-rows"></tbody></table></div></div>
<div class="card"><h3>Sessions</h3><div class="tw"><table><thead><tr><th>When</th><th>Question</th><th>Mode</th><th>Headline mean</th><th>Review</th><th>Verdict</th><th></th></tr></thead><tbody id="wk-sessions"></tbody></table></div>
<div class="bar-row" style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px"><button class="sbtn" id="wk-export">Copy history JSON</button><button class="sbtn" id="wk-import">Import history JSON</button><button class="sbtn" id="wk-clear">Clear history</button></div></div>'''

    lab = '''
<div class="card sim" style="padding:16px">
  <textarea class="mono" id="pl-in" placeholder="Paste a prompt you would send the assistant…"></textarea>
  <button class="sbtn" id="pl-go">Check prompt</button>
  <div class="pc-out" id="pl-out"></div>
</div>'''

    body = (
        sec('how', 'How the simulator works',
            card('<ol><li><b>Pick</b> a question or a mock, a time mode (60 is the real module), and a hint level.</li>'
                 '<li><b>Run ten rounds</b>: problem → implement → requirement change → test → <b>"would you ship this?"</b> on flawed AI output → then the follow-up engine, '
                 'level by level: correctness, complexity, concurrency, scale, production. Answer out loud, use your real assistant (CoderPad sandbox, or Claude in another '
                 'window), and log what you said and the prompts you sent.</li>'
                 '<li><b>Review</b>: in round 5 you decide ship or not and name the defect <i>before</i> it is revealed — then grade your own review.</li>'
                 '<li><b>Score</b> on the Staff standard: 15 dimensions and 7 AI-collaboration checks → eight headline scores out of 10 → PASS / BORDERLINE / FAIL → '
                 'your three biggest gaps, each linked to the exercise that trains it.</li>'
                 '<li><b>Second opinion</b>: "Grade with Claude" copies the whole transcript and the standard. <b>Save</b> feeds the weakness tracker.</li></ol>') +
            note('This page cannot read your answers and judge them — nothing static can, and pretending would be worse than useless. It runs the structure, keeps the time, '
                 'hides the answers, and records your scores. For a live interviewer that reacts to what you say, use <b>Copy interviewer prompt</b> and run the round in a '
                 'Claude chat; the prompt tells Claude not to reveal solutions, to show flawed AI output and ask "would you ship this?", to ask C# questions only about what '
                 'you used, and to score on the same standard.', 'warn', 'What it can and cannot do'),
            kicker='Interview mode', why='Mode B for every question on the study page') +
        sec('run', 'Run an interview', runner + score, kicker='Simulator', why='Timed · ten rounds · Staff standard') +
        sec('mocks', 'Mock interviews — five levels', '<div class="grid g2">%s</div>' % mocks, kicker='Mocks', why='Beginner → full realistic round') +
        sec('tracker', 'Personal weakness tracker', tracker_html, kicker='Measure', why='Across sessions · stored in this browser') +
        sec('rubric', 'The Staff Engineer standard', rules + heads + card(staff, title='15 dimensions') + card(ai, title='7 AI-collaboration checks'), kicker='Scoring') +
        sec('promptlab', 'Prompt checker', note('A heuristic, not a grade: it checks for the three parts every good interview prompt has — context, constraint, output shape — '
                                                 'plus whether you asked for something checkable, and flags "solve the whole thing" requests.', '') + lab,
            kicker='Practice', why='Context · constraint · output shape'))

    js = 'window.AISIM = %s;' % json.dumps(data(), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return page('02b-ai-simulator.html', 'AI coding interview simulator',
                'Interview mode for every question: ten rounds including flawed AI output to review and five levels of follow-ups, a real-length timer, your prompts logged, '
                'and the Staff standard — eight scores out of 10, gates that make blind AI use fail, and the three gaps to train next.',
                body, round_id='ai', round_name='Coding with AI', crumb_tail='02b AI coding simulator', nav_html=AI_NAV,
                extra_head='\n<link rel="stylesheet" href="assets/aic.css">', tail_js=js, tail_scripts=['assets/aisim.js'],
                hero_chips=[('', '%d questions' % len(AR.Q)), ('', '5 mocks'), ('', '30 / 45 / 60 min'), ('', '15 + 7 scored'), ('', 'weakness tracker')])
