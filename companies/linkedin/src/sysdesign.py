# -*- coding: utf-8 -*-
from lib import *
import research as R
from sysdesign_data import DESIGNS, CATALOGUE

STEPS = [
 ('1 · Clarify', 'Ask until the problem is bounded. Five questions, not twenty.', 'What is in scope, what is explicitly out'),
 ('2 · Functional requirements', 'What it must do, in the user\'s language', 'Name the one requirement doing all the work'),
 ('3 · Non-functional requirements', 'Latency, availability, consistency, isolation, compliance', 'Each one must force a design decision'),
 ('4 · Scale estimate', 'Back-of-envelope: QPS, storage, bandwidth, fan-out', 'One number that changes the architecture'),
 ('5 · API', 'A few endpoints with the fields that matter', 'Idempotency keys and pagination betray experience'),
 ('6 · Data model', 'Entities, keys, access patterns', 'Partition key first — it decides everything downstream'),
 ('7 · High-level architecture', 'Boxes and arrows, request path first', 'Say the happy path end to end in one breath'),
 ('8 · Deep dives', 'Two or three components, chosen for risk', 'Go where the difficulty is, not where you are comfortable'),
 ('9 · Bottlenecks', 'What saturates first as traffic grows 10×', 'Name it before you are asked'),
 ('10 · Failure modes', 'Each component: what happens, who notices, what degrades', 'Blast radius and fail-open/closed'),
 ('11 · Scaling', 'Partitioning, replication, caching, tiering', 'Stateful scaling is the hard half'),
 ('12 · Observability', 'The three metrics you would page on', 'Pick metrics that predict, not just describe'),
 ('13 · Security and privacy', 'AuthN/Z, tenant isolation, data handling', 'Enforced by the platform, not by every caller'),
 ('14 · Cost', 'What dominates, and the lever that halves it', 'Cost structure is a staff-level signal'),
 ('15 · Trade-offs', 'The two or three real choices, with what you gave up', 'Say what you rejected and why'),
 ('16 · Evolution', 'Phase 1 to ship, phase 2, phase 3', 'What you would build first, and what you would not build'),
]

NUMBERS = [
 ['Memory read (1 MB sequential)', '~50 µs', 'RAM is 100× faster than SSD, 10,000× faster than a network round trip to another region'],
 ['SSD random read', '~100 µs', 'Fine for a cache miss, not for a fan-out of 100'],
 ['Same-datacentre round trip', '~0.5 ms', 'Budget 5–10 internal hops in a 50 ms p99'],
 ['Cross-region round trip (US–EU)', '~80–100 ms', 'One cross-region hop can blow an entire latency budget'],
 ['1 KB message × 1M/s', '1 GB/s', '×3 replication = 3 GB/s of disk write — this arithmetic decides broker count'],
 ['1 billion rows × 100 bytes', '100 GB', 'Fits on one machine; "big data" starts where indexes stop fitting in RAM'],
 ['Cache hit rate 90% → 95%', 'Halves origin load', 'The cheapest scaling lever you have'],
 ['Fan-out of 100 at p99 10 ms each', 'p99 becomes ~50–100 ms', 'Tail amplification: hedge requests or reduce fan-out'],
]

LENS = [
 ('Architectural judgement', 'Do you pick the boring, correct option and say why? Do you reject options out loud?',
  'Name the alternative you rejected in every major decision. "We considered X, rejected it because Y."'),
 ('Scope', 'Do you design the system, or the whole platform around it?',
  'Mention what this system should *not* own, and which existing platform capability it should reuse.'),
 ('Ambiguity', 'Do you bound an underspecified problem yourself?',
  'State assumptions explicitly and move: "I will assume 100k QPS and a 50 ms budget; tell me if that is wrong."'),
 ('Failure thinking', 'Do you reason about blast radius, not just uptime?',
  'For each component: what fails, who is affected, what degrades, how you detect it.'),
 ('Operations', 'Would you be able to run this at 3 a.m.?',
  'Rollout waves, canaries, rollback, the metric you page on, the runbook step.'),
 ('Evolution', 'Can it be built in phases and changed later?',
  'Phase 1 that ships in a quarter, and the seam that lets phase 3 exist.'),
 ('Cross-team', 'Who else has to change, and how do you get them to?',
  'This is where your 178-team migration story belongs — say it in one sentence.'),
 ('Business', 'Do you connect design choices to cost and revenue?',
  'One cost sentence per design: what dominates and what you would do about it.'),
]

def build():
    rep = [q for q in R.Q if q['r'] == 'design']
    t = R.THEMES['design']

    rep_html = ''
    for key, title in [('high', 'High recurrence'), ('medium', 'Medium recurrence'), ('one-off', 'One-off / lower confidence')]:
        qs = [q for q in rep if q['rec'] == key]
        if not qs: continue
        items = ''
        for q in qs:
            srcs = ' · '.join('<a href="%s" target="_blank" rel="noopener">%s</a>'
                              % (R.SOURCES[s]['url'], R.SOURCES[s]['name'].split('—')[0].strip()) for s in q['src'])
            items += acc(q['q'],
                '<p><b>Core challenge:</b> %s</p><p><b>Typical deep dives / follow-ups:</b></p><ul>%s</ul>'
                '<p><b>What to practise:</b> %s</p><div class="src">Reported %s · %s · %s · %s</div>' % (
                    esc(q['pat']), ''.join('<li>%s</li>' % esc(f) for f in q['fu']), esc(q['prep']),
                    esc(q['d']), esc(q['role']), esc(q['loc']), srcs),
                tag({'A': 'hi', 'B': 'med', 'C': 'low'}[q['conf']], 'conf ' + q['conf']))
        rep_html += '<h3 id="rep-%s">%s</h3>%s' % (key, title, items)

    probe = card(table(['After the architecture, they probe…', 'Have ready'], [
        ['Partitioning', 'Your partition key, why it avoids hot spots, and what resharding would cost'],
        ['Consistency', 'Where you accept eventual consistency and what the user sees during the window'],
        ['Failure modes', 'Per component: blast radius, detection, degradation'],
        ['Scaling', 'What saturates first at 10×, and the next bottleneck after that'],
        ['Caching', 'What you cache, invalidation rule, and what a stale entry costs'],
        ['Storage choice', 'Why this store, and the two you rejected'],
        ['Data modelling', 'Access patterns first, schema second'],
        ['Observability', 'The metric you page on (a leading indicator, not a lagging one)'],
        ['Cost', 'What dominates and the lever that halves it'],
        ['Security', 'Tenant isolation enforced centrally, not per caller'],
        ['ML / ranking trade-offs', 'Candidate generation vs ranking, offline vs online, feedback loops'],
        ['Experimentation', 'How you would A/B it and what metric decides'],
        ['Rollout', 'Waves, canaries, automatic rollback — say it before they ask'],
    ]) + note('LinkedIn design rounds are reported as product-centric, with infrastructure variants. One 2025 report ended early '
              'because "all the trade-offs are covered" — lead with trade-offs rather than saving them for the end.', '',
              'What the reports say about the probing'),
        title='What LinkedIn interviewers probe after the first architecture')

    framework = card(table(['Step', 'What you do', 'The staff-level move'], [[a, b, c] for a, b, c in STEPS]) +
                     note('Use it as a checklist, not a script. In a 45-minute round you will do 1–8 thoroughly and 9–16 as a '
                          'rapid sweep unless the interviewer pulls you somewhere.', ''),
                     title='The 16-step framework')

    numbers = card(table(['Quantity', 'Number', 'Why it matters'], NUMBERS) +
                   note('Memorise these eight. One number stated confidently ("1 GB/s ingress, ×3 replication, so 3 GB/s of disk") '
                        'does more for your credibility than a page of boxes.', 'good'),
                   title='Numbers to have automatic')

    lens = card(table(['Dimension', 'What they are listening for', 'How to show it'], [[a, b, c] for a, b, c in LENS]) +
                note('Blind discussions repeatedly attribute Staff-versus-Senior outcomes at LinkedIn to leadership and scope '
                     'signal rather than raw technical depth. In the design round, scope shows up as these eight behaviours.',
                     'warn', 'Why this matters for levelling'),
                title='The staff-level lens')

    # ---------------- interactive designs ----------------
    designs_html = ('<div class="filters" data-filter-scope="#designs > details">'
                    '<input class="search" placeholder="Search designs…">'
                    '<button class="fchip" data-fk="prio" data-fv="p0">P0 · reported recently</button>'
                    '<span class="count"></span></div><div id="designs">')
    for d in DESIGNS:
        did = 'des.' + d['id']
        reg('design', did, d['topic'], d['title'], weight=3, kind='design')
        stages = [
            stage('The prompt', '<p class="lead">%s</p>%s' % (rich(d['title']), note(d['why'], '', 'Why this design'))),
            stage('Your clarifying questions', note('Write down your five questions before opening this. Compare, then continue.', 'warn') +
                  '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(q) for q in d['ask']), 'ask before you design'),
            stage('Functional requirements', '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(x) for x in d['fr'])),
            stage('Non-functional requirements', '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(x) for x in d['nfr'])),
            stage('Scale estimate', rich(d['scale'])),
            stage('API', rich(d['api'])),
            stage('Data model', rich(d['data'])),
            stage('High-level architecture', rich(d['arch'])),
            stage('Deep dives', '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(x) for x in d['deep'])),
            stage('Failure modes', '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(x) for x in d['fails'])),
            stage('Scaling', '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(x) for x in d['scaling'])),
            stage('Observability', '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(x) for x in d['obs'])),
            stage('Security and privacy', '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(x) for x in d['sec'])),
            stage('Cost', rich(d['cost'])),
            stage('Trade-offs', table(['Axis', 'What you traded'], [[a, b] for a, b in d['trade']])),
            stage('Evolution', rich(d['evolve'])),
            stage('Senior versus staff', senior_staff(d['senior'], d['staff'])),
        ]
        block = practice(did, titled(d['title'], d['topic']), stages,
                         tag(d['prio'], 'P0' if d['prio'] == 'p0' else 'P1'), label=d['title'],
                         statuses=[('solved', 'Designed it'), ('revise', 'Needs revision'), ('failed', 'Struggled')])
        designs_html += block.replace('<details class="acc"', '<details class="acc" data-prio="%s"' % d['prio'], 1)
    designs_html += '</div>'

    cat_rows = []
    for name, focus, link in CATALOGUE:
        cat_rows.append(['[%s](%s)' % (name, link), focus])
    catalogue = card(
        '<p>Your existing guide already contains 26 fully worked designs. Rather than duplicate them, this page covers the '
        'LinkedIn-reported set above and links to the rest. Open them in the guide when a category is weak.</p>'
        + table(['Design (in the guide)', 'What it drills'], cat_rows),
        title='Category coverage — the rest of the map')

    mocks = ''
    for mid, title, q, rub, secs in [
        ('m1', 'Mock 1 · infrastructure (45 min)',
         'Design a rate limiter for our API gateway. I will interrupt with constraints as we go.',
         ['Asked what we are limiting and what happens at the limit, before designing',
          'Named the algorithm and why (token bucket vs sliding window)',
          'Handled distributed state explicitly: central vs local vs leased',
          'Stated the failure behaviour (open or closed) and justified it',
          'Covered hot keys and per-tenant fairness',
          'Gave a cost or latency number with arithmetic',
          'Closed with phases: what ships first'], 2700),
        ('m2', 'Mock 2 · product-centric (45 min)',
         'Design autosuggest for person search on LinkedIn. Backend only.',
         ['Clarified personalisation, latency budget and freshness first',
          'Two-stage design: candidate generation then ranking',
          'Sharding strategy with hot-prefix handling',
          'Debouncing and caching mentioned as cheap wins',
          'Privacy filtering inside candidate generation, not after',
          'Named the quality metric (click-through), not just latency',
          'Phased evolution'], 2700),
        ('m3', 'Mock 3 · your home ground (45 min)',
         'Design a system that gives large regulated customers dedicated, isolated environments on a multi-tenant platform. '
         '(Your own project as a design question — expect the interviewer to push on things you did not do.)',
         ['Separated control plane from data plane, and kept provisioning off the request path',
          'Routing: tenant context vs placement, and why they are separate concerns',
          'Fail-closed isolation guarantees with more than one lock',
          'Migration of existing tenants: copy, validate, switch, verify deletion',
          'Cost structure of dedicated environments and the levers',
          'What you would do differently today — and the limits of the design'], 2700)]:
        mocks += card(mock_block(reg('design', 'des.mock.' + mid, 'Mock interviews', title, weight=3, kind='mock'),
                                 q, 'System Design', rub, secs), title=title)

    ladder = table(['Level', 'What it means here', 'How to practise'], [
        ['**L1 · Fundamentals**', 'You know the primitives: partitioning, replication, caching, queues, consistency', 'The guide\'s theory chapters'],
        ['**L2 · Interview level**', 'You can drive a 45-minute design end to end without prompting', 'Any design above, timed, out loud'],
        ['**L3 · Staff level**', 'You lead with trade-offs, name blast radius, and phase the build', 'The staff-level lens plus the senior-versus-staff stage'],
        ['**L4 · Deep follow-up**', 'You survive five levels of probing on one component', 'Pick one deep dive and go six questions deep with me'],
        ['**L5 · Pressure**', 'Requirements change mid-design and you adapt without losing coherence', 'Mock 1 with interruptions, or ask me to run it adversarially'],
    ])

    body = (
        sec('reports', 'What recent reports say about this round', rep_html + probe,
            kicker='Research first', why='%d catalogued design reports · updated %s' % (len(rep), R.DATE)) +
        sec('framework', 'The framework and the numbers', framework + numbers, kicker='Method') +
        sec('lens', 'The staff-level lens', lens, kicker='Levelling') +
        sec('designs', 'Practice designs — interactive', note(
            'These run like an interview: the prompt first, then <b>your</b> clarifying questions, then the requirements, and only '
            'then the architecture. Write your answer for each stage before you open it.', 'warn', 'How to run a design') +
            designs_html, kicker='Practice', why='%d designs · reported-first ordering' % len(DESIGNS)) +
        sec('catalogue', 'Category coverage', catalogue, kicker='Breadth') +
        sec('mock', 'Mock design rounds', mocks, kicker='Simulation', why='3 mocks · timed · graded in chat') +
        sec('levels', 'Progressive difficulty', ladder, kicker='Ladder'))

    return page('03-system-design.html', 'System Design round',
                'Interactive designs that ask before they tell, prioritised by what LinkedIn candidates recently reported, with a staff-level lens on every one.',
                body, round_id='design', round_name='System Design', crumb_tail='03 System Design',
                hero_chips=[('', '%d practice designs' % len(DESIGNS)), ('', '16-step framework'),
                            ('', '%d linked designs' % len(CATALOGUE)), ('', '3 mocks')])
