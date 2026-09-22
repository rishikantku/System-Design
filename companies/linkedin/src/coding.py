# -*- coding: utf-8 -*-
from lib import *
import research as R
from coding_patterns import PATTERNS
from coding_problems import PROBLEMS as _PROBLEMS, BANK
from coding_official import OFFICIAL_PROBLEMS
from coding_drills import DRILLS as CODING_DRILLS
from coding_linkedin import LINKEDIN_PROBLEMS
import leetcode as LC
PROBLEMS = OFFICIAL_PROBLEMS + LINKEDIN_PROBLEMS + CODING_DRILLS + _PROBLEMS

PRIO_LABEL = {'p0': 'P0 · do first', 'p1': 'P1 · then these', 'p2': 'P2 · if time'}
LEVEL_LABEL = {'warm': 'Warm-up', 'med': 'Interview level', 'hard': 'Hard'}

def build():
    # ---------------- what reports say ----------------
    rep = [q for q in R.Q if q['r'] == 'coding']
    buckets = {'high': [], 'medium': [], 'one-off': []}
    for q in rep:
        buckets[q['rec']].append(q)
    rep_html = ''
    for key, title, hint in [('high', 'High recurrence', 'Named by several independent sources or appearing across years'),
                             ('medium', 'Medium recurrence', 'Reported more than once, or first-hand with detail'),
                             ('one-off', 'One-off / lower confidence', 'A single report — useful as practice, not as prediction')]:
        items = ''
        for q in buckets[key]:
            srcs = ' · '.join('<a href="%s" target="_blank" rel="noopener">%s</a>'
                              % (R.SOURCES[s]['url'], R.SOURCES[s]['name'].split('—')[0].strip()) for s in q['src'])
            items += acc(q['q'],
                '<p><b>What was asked:</b> %s</p><p><b>Core pattern:</b> %s</p>'
                '<p><b>Reported follow-ups:</b></p><ul>%s</ul>'
                '<p><b>What to practise:</b> %s</p><div class="src">Reported %s · %s · %s · %s</div>' % (
                    esc(q['q']), esc(q['pat']),
                    ''.join('<li>%s</li>' % esc(f) for f in q['fu']),
                    esc(q['prep']), esc(q['d']), esc(q['role']), esc(q['loc']), srcs),
                tag({'A': 'hi', 'B': 'med', 'C': 'low'}[q['conf']], 'conf ' + q['conf']))
        rep_html += '<h3 id="rep-%s">%s <span class="src">— %s</span></h3>%s' % (key, title, hint, items)

    # ---------------- priority map ----------------
    prio_rows = [
        ['**Trees and nested structures** — DFS post-order, BFS levels, LCA', 'P0',
         'Find Leaves, Nested List Weight Sum II and LCA are all on the LinkedIn tag list; a 2026 phone screen reported a nested-object traversal'],
        ['**Graphs** — BFS shortest path, topological sort, cycle detection', 'P0',
         'getBuildOrder reported first-hand (Sep 2025); Word Ladder in a Staff screening (Jul 2025)'],
        ['**Design-flavoured data structures** — LRU, LFU, All O`one, Max Stack', 'P0',
         'Max Stack and All O`one on the tag list; LRU/LFU dominate the AI-enabled round'],
        ['**Sliding window and two pointers**', 'P0',
         'Minimum Window Substring, Max Consecutive Ones III tagged; a 2026 report used a palindrome-with-edits problem'],
        ['**Hashing, including rolling hash**', 'P0', 'Repeated DNA Sequences reported first-hand (Sep 2025)'],
        ['**Concurrency in C#** — locks, concurrent collections, async coordination', 'P0',
         'Every reported AI-round problem pivots to thread-safety; guides describe a dedicated concurrency-flavoured round'],
        ['**Heaps and top-K**', 'P1', 'Standard at this level; merge-k and median-of-stream are the usual shapes'],
        ['**Intervals and sweep line**', 'P1', 'Interval-manager variant reported in the AI round; calendar LLD asked recently'],
        ['**Binary search, including on the answer**', 'P1', 'Rotated-array-with-duplicates reported in a phone screen'],
        ['**Union-Find**', 'P1', 'Connectivity and merge problems; cheap to learn, occasionally decisive'],
        ['**Dynamic programming**', 'P1', 'Appears, but rarely the centrepiece at LinkedIn compared with trees and graphs'],
        ['**Backtracking**', 'P2', 'Lower frequency in reports; know the template and pruning'],
        ['**Tries**', 'P2', 'Mostly relevant through typeahead, which shows up as a design question'],
    ]
    prio = table(['Topic', 'Priority', 'Why this priority (from the reports)'], prio_rows)

    # ---------------- patterns ----------------
    pat_html = ''
    for p in PATTERNS:
        reg('coding', 'pat.' + p['id'], p['topic'], p['name'], weight=1, kind='pattern')
        body = (
            '<div class="pat">'
            '<div class="row"><div class="k">Concept</div><div class="v">%s</div></div>'
            '<div class="row"><div class="k">Recognise it</div><div class="v">%s</div></div>'
            '<div class="row"><div class="k">Template</div><div class="v">%s</div></div>'
            '<div class="row"><div class="k">Example problems</div><div class="v">%s</div></div>'
            '<div class="row"><div class="k">Walkthrough</div><div class="v">%s</div></div>'
            '<div class="row"><div class="k">Common mistakes</div><div class="v"><ul>%s</ul></div></div>'
            '<div class="row"><div class="k">Complexity</div><div class="v">%s</div></div>'
            '<div class="row"><div class="k">Follow-ups</div><div class="v"><ul>%s</ul></div></div>'
            '</div>%s') % (
            rich(p['concept']), rich(p['recognise']), code(p['template']), rich(p['example']), rich(p['walk']),
            ''.join('<li>%s</li>' % rich(m) for m in p['mistakes']), rich(p['complexity']),
            ''.join('<li>%s</li>' % rich(f) for f in p['follow']),
            tracker('pat.' + p['id'], statuses=[('solved', 'Know it cold'), ('revise', 'Needs revision'), ('failed', 'Shaky')],
                    note_ph='Write the template from memory once. Note what you got wrong…'))
        pat_html += acc(titled(p['name'], p['topic']),
                        '<div data-id="pat.%s" data-label="%s">%s</div>' % (p['id'], esc(p['name']), body),
                        tag(p['prio'], PRIO_LABEL[p['prio']].split('·')[0].strip()), raw=True)

    # ---------------- practice engine ----------------
    prob_html = ('<div class="filters" data-filter-scope="#problems > details">'
                 '<input class="search" placeholder="Search problems…">'
                 + ''.join('<button class="fchip" data-fk="level" data-fv="%s">%s</button>' % (k, v) for k, v in LEVEL_LABEL.items())
                 + '<button class="fchip" data-fk="reported" data-fv="yes">Reported at LinkedIn</button>'
                 + '<span class="count"></span></div><div id="problems">')
    for pr in PROBLEMS:
        pid = 'prob.' + pr['id']
        reg('coding', pid, pr['topic'], pr['title'], weight=2, kind='problem', level=pr['level'])
        stages = [
            stage('Question', rich(pr['question'])),
            stage('Think', note(pr['think'], 'warn', 'Before you open anything else'), 'try it first'),
            stage('Approach', rich(pr['approach'])),
            stage('Edge cases', '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(e) for e in pr['edges'])),
            stage('Code (C#)', code(pr['code'])),
            stage('Complexity', rich(pr['complexity'])),
            stage('Follow-up', '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(f) for f in pr['follow'])),
            stage('Optimisation', rich(pr['optimise'])),
            stage('Self-evaluation', '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(e) for e in pr['evalpts'])),
        ]
        reported = 'yes' if any(k in pr['why'].lower() for k in ['reported', 'tag list']) else 'no'
        meta = tag({'warm': 'p2', 'med': 'p1', 'hard': 'p0'}[pr['level']], LEVEL_LABEL[pr['level']])
        if reported == 'yes': meta += tag('new', 'reported')
        meta += LC.chip(LC.CODING, pr['id'])        # run it on the real judge
        block = practice(pid, titled(pr['title'], pr['topic']),
                         [note(pr['why'], '', 'Why this problem')] + stages, meta, label=pr['title'])
        prob_html += block.replace('<details class="acc"',
                                   '<details class="acc" data-level="%s" data-reported="%s"' % (pr['level'], reported), 1)
    prob_html += '</div>'

    bank_rows = ''
    for i, (title, lvl, topic, why) in enumerate(BANK):
        bid = 'bank.%d' % i
        reg('coding', bid, topic, title, weight=1, kind='bank', level=lvl)
        bank_rows += ('<tr data-id="%s" data-label="%s"><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td>'
                      '<td><div class="track" style="margin:0;padding:0;border:none">%s</div></td></tr>') % (
            bid, esc(title), esc(title), LEVEL_LABEL[lvl], esc(topic), esc(why),
            ''.join('<button class="sbtn" data-st="%s">%s</button>' % (k, v)
                    for k, v in [('solved', '✓'), ('revise', '↻'), ('failed', '✗')]))
    bank = ('<div class="tw"><table><thead><tr><th>Problem</th><th>Level</th><th>Topic</th><th>Why</th>'
            '<th>Status</th></tr></thead><tbody>%s</tbody></table></div>' % bank_rows)

    # ---------------- craft sections ----------------
    complexity = card(
        '<p>Say complexity <b>before</b> you are asked, and say it in two parts: the bound, and what dominates it.</p>'
        + table(['Say this', 'Not this'], [
            ['"O(n log k) — the heap is bounded at k, so each of the n pushes costs log k"', '"It is n log n"'],
            ['"O(n) amortised: every index enters and leaves the window once"', '"The while loop makes it n squared, I think"'],
            ['"O(V+E), and E dominates because the graph is dense"', '"Linear"'],
            ['"O(n) worst case with duplicates — the adversary hides the target"', 'Claiming O(log n) for rotated-with-duplicates'],
        ])
        + '<h4>Space too</h4><ul>'
        '<li>Recursion stack counts: O(h) for a tree, O(n) if skewed.</li>'
        '<li>Output size does not always count — say whether you are excluding it.</li>'
        '<li>Allocation matters in C#: substring per window is O(n·k) garbage; an int key is not.</li></ul>',
        title='Complexity analysis — how to say it')

    edges = card(
        '<p>Run this list out loud before you claim you are done. It takes twenty seconds and it is where most "almost passed" '
        'interviews are lost.</p>'
        + table(['Class', 'Ask yourself'], [
            ['Empty / null', 'Empty array, empty string, null root, empty dependency set'],
            ['One element', 'Single node, single interval, k = 1, capacity = 1'],
            ['All the same', 'All duplicates (kills rotated binary search), all zeros, one distinct key'],
            ['Boundaries', 'Target at index 0 or n-1, interval touching at a boundary, window equal to the whole input'],
            ['Too big', 'Depth 10⁵ (stack overflow), 10⁹ values (overflow), input that does not fit in memory'],
            ['Not found', 'Key missing, no path, no valid window — what do you return, and is it distinguishable from a real answer?'],
            ['Contract', 'What happens on invalid input: throw, return false, or silently ignore? Say which and why.'],
        ]),
        title='Edge cases — the twenty-second sweep')

    quality = card(
        '<ul>'
        '<li><b>Name things for the reader.</b> `missing`, `victim`, `waves` — not `tmp`, `x2`, `flag`.</li>'
        '<li><b>Small methods with one job.</b> `Unlink`, `AddFront`, `Require`. Interviewers read structure faster than logic.</li>'
        '<li><b>State the contract at the top.</b> What does it throw, what does it return when nothing is found.</li>'
        '<li><b>Guard clauses first</b>, so the happy path is not nested four levels deep.</li>'
        '<li><b>Prefer the standard library</b> and know its costs: `SortedList` insert is O(n), `PriorityQueue` is a min-heap '
        'with no decrease-key, `Dictionary` has no order.</li>'
        '<li><b>Immutability where it is free</b>: `readonly` fields, no mutation of the caller\'s array unless asked.</li>'
        '<li><b>Testing out loud</b>: one happy case, one edge case, one adversarial case — trace them on the actual code.</li>'
        '</ul>'
        + note('This is the same signal the separate craftsmanship round scores. A candidate who writes clean, testable code in the '
               'coding round is building evidence for two rounds at once.', 'good', 'Cross-round signal'),
        title='Code quality — what a staff-level solution looks like')

    comms = card(
        '<p>One 2025 report described an interviewer who interrupted constantly; another said the round ended early because '
        '"all the trade-offs are covered". Both are communication outcomes, not algorithm outcomes.</p>'
        + table(['Phase', 'What to say', 'Time'], [
            ['Restate', '"So: input is X, output is Y, and I can assume Z. Is that right?"', '~1 min'],
            ['Examples', 'Walk one small example by hand, including one edge case', '~2 min'],
            ['Approach', 'Brute force in one sentence, its cost, then the better idea and why', '~3 min'],
            ['Contract', '"I will throw on invalid input and return -1 when missing"', '~30 s'],
            ['Code', 'Narrate intent per block, not per line. Silence is the failure mode', '~15 min'],
            ['Test', 'Trace the happy path, then the edge case you named earlier', '~4 min'],
            ['Complexity', 'Time and space, with what dominates', '~1 min'],
            ['Production', 'Unprompted: "if this were production I would…"', '~2 min'],
        ])
        + note('When interrupted: acknowledge, answer in one sentence, then say "let me finish this branch and come back to it". '
               'Do not abandon your thread — the report that mentioned interruptions still completed the solution.', 'warn',
               'Handling interruptions'),
        title='Communication during coding')

    fundamentals = grid([
        card(table(['Question', 'The answer that satisfies an infra interviewer'], [
            ['**TCP vs UDP**',
             'TCP: connection, ordered, retransmits, flow and congestion control, head-of-line blocking. UDP: datagrams, no '
             'ordering or delivery guarantee, no congestion control unless you add it. Pick UDP when late data is worthless '
             '(voice, video, telemetry) or when you will build your own reliability (QUIC). Mention the handshake cost: one '
             'round trip for TCP, plus one or two for TLS, which is why connection reuse matters so much.'],
            ['**Where does head-of-line blocking bite?**',
             'One lost TCP segment stalls every stream on that connection — the reason HTTP/2 multiplexing still suffers and '
             'HTTP/3 moved to QUIC over UDP.'],
            ['**Paging and virtual memory**',
             'Each process sees a virtual address space; the MMU maps pages to physical frames, with the TLB caching '
             'translations. A page fault fetches from disk (or the page cache). Thrashing is when the working set exceeds RAM '
             'and you spend all your time faulting — the reason a JVM heap larger than RAM is catastrophic rather than slow.'],
            ['**Stack vs heap**',
             'Stack: per-thread, LIFO, allocation is a pointer bump, freed on return, fixed size (so deep recursion overflows). '
             'Heap: shared, dynamic lifetime, allocation costs more and fragments, reclaimed by GC or free(). In C# this maps '
             'to structs versus classes, with escape analysis and `Span<T>` as the usual "keep it off the heap" tools.'],
            ['**What is the page cache, and why do I care?**',
             'The OS caches file pages in free RAM, so sequential reads from a warm file are near-memory speed. It is why '
             'log-structured systems (Kafka) are fast without their own cache, and why `free -m` showing little free memory is '
             'normal rather than alarming.'],
            ['**Context switch cost**',
             'Roughly a microsecond of direct cost plus cache and TLB pollution that can cost far more. It is the argument for '
             'thread pools sized near the core count, and for async IO over thread-per-request.'],
        ]), title='Operating systems and networking'),
        card(table(['Question', 'The answer'], [
            ['**Latency numbers worth knowing**',
             'L1 ~1 ns · main memory ~100 ns · SSD random read ~100 µs · same-datacentre round trip ~0.5 ms · spinning disk seek '
             '~10 ms · cross-continent round trip ~80–100 ms. Say them as ratios, not decimals: memory is a thousand times '
             'faster than an SSD read, which is a hundred times faster than crossing an ocean.'],
            ['**Process vs thread vs async**',
             'Processes have isolated address spaces (safety, expensive IPC); threads share memory (cheap sharing, data races); '
             'async reuses one thread across many waits (no thread per connection, but one blocking call poisons the pool).'],
            ['**What makes a lock expensive?**',
             'Not the instruction — the contention. An uncontended lock is tens of nanoseconds; a contended one parks the '
             'thread and costs a context switch. Hence striping, per-core structures, and read-mostly designs.'],
            ['**Memory model / visibility**',
             'Without synchronisation, one thread may never see another\'s write. `volatile` gives ordering and visibility, not '
             'atomicity; `Interlocked` gives atomicity; a lock gives both plus mutual exclusion. This is the vocabulary behind '
             '"make it thread-safe".'],
            ['**Why is my p99 bad when my average is fine?**',
             'Queueing, GC pauses, tail amplification across fan-out, and retries. With 100 parallel calls at p99 = 10 ms, the '
             'slowest of the batch dominates — hedged requests or reduced fan-out are the fixes.'],
            ['**Disk durability**',
             'A write is not durable until fsync returns; buffered writes live in the page cache. This is the difference between '
             '"we wrote it" and "we will not lose it", and it is exactly the write-ahead-log conversation in the design round.'],
        ]), title='Concurrency, latency and durability'),
    ], 'g2') + note(
        'A Taro report (Senior SWE, Infrastructure, October 2025) describes a LinkedIn technical screen that was mostly these: '
        'TCP versus UDP, paging, stack versus heap — plus one coding question. Single report, so do not over-weight it; but for '
        'a **Systems and Infrastructure** role these are cheap to revise and embarrassing to fumble.',
        'warn', 'Why this section exists')

    # ---------------- mocks ----------------
    mocks = ''
    mock_sets = [
      ('m1', 'Mock 1 · phone-screen shape (2 problems, 60 min)',
       'Problem 1 (25 min): Given a binary tree, collect nodes layer by layer as if you repeatedly removed all leaves. '
       'Problem 2 (25 min): Given a DNA string, return every 10-letter sequence occurring more than once, in ascending order.',
       ['Restated both problems and asked at least one clarifying question',
        'Named the naive approach and its cost before optimising',
        'Find Leaves: used height-from-bottom rather than simulating removal',
        'DNA: mentioned the rolling-hash/2-bit encoding even if you coded the simple version',
        'Traced one example on the written code, including an edge case',
        'Gave time and space complexity for both, unprompted'], 3600),
      ('m2', 'Mock 2 · design-flavoured coding (45 min)',
       'Design a cache with O(1) Get and Put that evicts the least recently used entry. Then make it safe for concurrent callers, '
       'and tell me how you would run it in production.',
       ['Map + doubly linked list with sentinels, written correctly without hints',
        'Said explicitly that Get mutates the recency list, so reads are writes',
        'Offered at least two concurrency designs (single lock, striping, approximate recency) with trade-offs',
        'Named the race a lock prevents, concretely (two threads unlinking neighbours)',
        'Production: hit rate, eviction counters, size in bytes, warmup, TTL',
        'Said how you would test it, including a concurrency test'], 2700),
      ('m3', 'Mock 3 · graph + follow-ups (45 min)',
       'You are given GetDependencies(target). Implement GetBuildOrder(targets). Then: report cycles usefully, produce parallel '
       'build waves, and support incremental rebuilds when one dependency changes.',
       ['Kahn with correct edge direction, built lazily from the entry targets',
        'Cycle reported by naming the nodes involved, not just throwing',
        'Parallel waves offered (ideally unprompted)',
        'Incremental rebuild: BFS over the dependents map',
        'No recursion for deep chains, and said why',
        'Connected it to a real system you have built, briefly'], 2700),
    ]
    for mid, title, q, rub, secs in mock_sets:
        mocks += card(mock_block(reg('coding', 'mock.' + mid, 'Mock interviews', title, weight=3, kind='mock'),
                                 q, 'Coding', rub, secs), title=title)

    ladder = table(['Level', 'What it means here', 'How to practise it'], [
        ['**L1 · Fundamentals**', 'You can write each pattern template from memory', 'Pattern library above — mark each "know it cold"'],
        ['**L2 · Interview level**', 'You solve a medium in 25 minutes with clean code and no hints', 'Warm-up and medium problems, timed'],
        ['**L3 · Staff level**', 'You state trade-offs, contracts and tests without prompting, and your code reads well', 'Hard problems + the code-quality checklist'],
        ['**L4 · Deep follow-up**', 'You handle "make it thread-safe", "10× the input", "productionise it"', 'Every problem\'s follow-up and optimisation stage'],
        ['**L5 · Pressure**', 'You keep the thread while being interrupted and requirements change mid-solution', 'Mock 2 and 3 with the timer running and no notes'],
    ])

    official = official_module('coding') + grid([
        card('<p>The pack describes this module as <b>day-to-day coding once the design and implementation strategy are '
             'settled</b> — not a pure algorithm sprint. Two sentences carry the weight:</p>'
             '<div class="note"><span class="lbl">Quoted from the pack</span>'
             '"The focus of this interview should be on the <b>modularity and extensibility</b> of the code that you write, as '
             'well as <b>finding and fixing bugs</b> and other errors. Many of these sessions involve <b>pointers, edge cases, '
             'abstraction</b>, or all of the above."</div>'
             '<p>So the scoring is elegance (object-oriented, simple rather than clever), maintainability (documentation, '
             'reusability), a high quality bar (testing and boundary conditions), and clear communication.</p>'
             '<ul><li><b>Expect to extend or repair code</b>, not only to write it from scratch — the first three problems below '
             'are built for exactly that.</li>'
             '<li><b>Any language, including pseudocode</b>, is explicitly allowed. C# is fine.</li>'
             '<li><b>No AI in this module.</b> AI is only in CWAI.</li></ul>',
             title='What this module actually is'),
        card('<p>The pack ends with three reminders. They are worth treating as instructions:</p>'
             '<ul>'
             '<li><b>Brush up on abstraction, recursion, HashMaps, edge cases and corner cases.</b></li>'
             '<li><b>Reiterate the question</b> to confirm what you heard is what the interviewer meant.</li>'
             '<li><b>Spend a short period clarifying requirements before assuming anything.</b></li>'
             '</ul>' +
             note('The first item is a map of the module: abstraction (design seams), recursion (and when to use an explicit '
                  'stack instead), HashMaps (the workhorse), and edge cases — which is what "finding and fixing bugs" means in '
                  'practice.', 'good', 'Read it as a syllabus'),
             title='The pack\'s own reminders'),
    ], 'g2')

    body = (
        sec('official', 'The official module', official,
            kicker='From LinkedIn', why='Authoritative — this overrides the community research below') +
        sec('reports', 'What recent reports say about this round', rep_html,
            kicker='Research first', why='%d catalogued coding reports · updated %s' % (len(rep), R.DATE)) +
        sec('priority', 'Priority map — what to study first', prio + note(
            'Priorities are set by recency and by how many independent reports mention a topic, not by what is most common on '
            'LeetCode generally. Reports are signals, not predictions.', 'warn'),
            kicker='Plan', why='P0 first · then P1 · P2 only if time') +
        sec('patterns', 'Pattern library', note(
            'For each pattern: the concept, how to recognise it, a C# template, an example, the mistakes that cost points, the '
            'complexity and the follow-ups. Write the template from memory before you mark it known.', '', 'How to use this') +
            pat_html, kicker='Recognition', why='%d patterns' % len(PATTERNS)) +
        sec('practice', 'Practice engine', note(
            'Open one stage at a time. Try the problem before revealing the approach — the value is in the attempt, not the '
            'reading. Track honestly: "needs revision" today is worth more than a green tick you cannot reproduce.', '',
            'Progressive reveal') + prob_html,
            kicker='Worked problems', why='%d fully worked · question → think → approach → code → follow-up' % len(PROBLEMS)) +
        sec('bank', 'Extra problem bank', note(
            'Not written up — these are reps. Tick them off as you solve them; they count towards your readiness score.', '') + bank,
            kicker='Volume', why='%d problems' % len(BANK)) +
        sec('fundamentals', 'Systems fundamentals refresher', fundamentals,
            kicker='Infra screen', why='Reported in a 2025 infrastructure screen · cheap to revise') +
        sec('craft', 'Complexity, edge cases, quality, communication',
            grid([complexity, edges], 'g2') + grid([quality, comms], 'g2'), kicker='The other 40%') +
        sec('mock', 'Mock coding rounds', note(
            'Run one end to end with the timer. Answer out loud, then press <b>Grade this with Claude</b> and paste the prompt to '
            'me — I will score it and ask the follow-up you would get.', '', 'How mock mode works') + mocks,
            kicker='Simulation', why='3 mocks · timed') +
        sec('levels', 'Progressive difficulty', ladder, kicker='Ladder'))

    return page('01-coding.html', 'Staff Coding',
                'Patterns, worked problems and timed mocks in C#, prioritised by what LinkedIn candidates have recently reported.',
                body, round_id='coding', round_name='Staff Coding', crumb_tail='01 Staff Coding',
                hero_chips=[('', '%d patterns' % len(PATTERNS)), ('', '%d worked problems' % len(PROBLEMS)),
                            ('', '%d extra reps' % len(BANK)), ('', '3 mocks'), ('', 'C#')])
