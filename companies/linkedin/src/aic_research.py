# -*- coding: utf-8 -*-
"""Research pass 4 — the Coding with AI (CWAI) round only. Collected 5 Oct 2026.

Grades, applied per claim rather than per source:
  CONFIRMED  — LinkedIn said it: the recruiter pack, or a LinkedIn employee speaking first-hand
  REPORTED   — a candidate described being asked it / experiencing it
  INFERENCE  — my reading of the evidence; nobody reported it in these words
  ADVICE     — general preparation advice, not specific evidence about LinkedIn

Sources that block fetching (LeetCode Discuss returns 403) were read through search-result
summaries. That is stated on each one and those claims are graded down to the weaker reading.
"""

DATE = '5 October 2026'

SOURCES = {
 'pack':     dict(name='LinkedIn recruiter pack — "Staff SI Onsite Prep · CWAI"', date='Sep 2026', url=None,
                  kind='Official — sent to you by the recruiter', grade='CONFIRMED'),
 'li-emp':   dict(name='Blind — "LinkedIn AI assisted coding round", reply by a LinkedIn employee', date='28 Oct 2025',
                  url='https://www.teamblind.com/post/linkedin-ai-assisted-coding-round-qz4kb1gx',
                  kind='First-hand, LinkedIn employee, anonymous', grade='CONFIRMED'),
 'hi-ai':    dict(name='Hello Interview — "LinkedIn\'s AI-Enabled Coding Interview: How to Prepare"', date='20 Feb 2026',
                  url='https://www.hellointerview.com/blog/linkedin-ai-enabled-coding',
                  kind='Guide built on candidate reports', grade='REPORTED'),
 'cond':     dict(name='Coditioning — LinkedIn SWE AI-enabled coding guide', date='updated 25 Jun 2026',
                  url='https://www.coditioning.com/blog/1406/linkedin-swe-ai-enabled-coding',
                  kind='Guide', grade='ADVICE'),
 'prachub':  dict(name='PracHub — LinkedIn SWE, five-round IC2 loop with an AI/coding round', date='Sep 2026',
                  url='https://prachub.com/interview-experiences/linkedin-software-engineer-interview-experience-a-five-round-ic2-loop-with-an-ai-coding-round',
                  kind='First-hand candidate report (IC2)', grade='REPORTED'),
 'lc-aie':   dict(name='LeetCode Discuss — AI Engineer, LinkedIn virtual onsite (rejected)', date='≈ late 2025 (post 7421217)',
                  url='https://leetcode.com/discuss/post/7421217/ai-engineer-linkedin-virtual-onsite-reje-2dhs/',
                  kind='First-hand, IC2 — read via search summary, page returns 403', grade='REPORTED'),
 'lc-ml':    dict(name='LeetCode Discuss — LinkedIn Software Engineer, Machine Learning', date='≈ late 2025 (post 7405614)',
                  url='https://leetcode.com/discuss/post/7405614/linkedin-software-engineer-machine-learn-l9pd/',
                  kind='First-hand — read via search summary, page returns 403', grade='REPORTED'),
 'exp-exp':  dict(name='Exponent / Aced — LinkedIn Senior SWE (Apps) interview experience', date='≈ Mar 2026',
                  url='https://www.tryexponent.com/experiences/linkedin-senior-software-engineer-interview-dc48e8',
                  kind='First-hand, Senior SWE, US', grade='REPORTED'),
 'dg':       dict(name='DesignGurus — "The AI-Assisted Coding Interview at Meta, Google, and LinkedIn"', date='2026',
                  url='https://www.designgurus.io/blog/ai-assisted-coding-interview',
                  kind='Guide', grade='ADVICE'),
 'shahdeo':  dict(name='Vinit Shahdeo — "AI Coding Interviews in 2026: What No One Tells You"', date='21 May 2026',
                  url='https://vinitshahdeo.substack.com/p/ai-assisted-coding-interviews-what-it-means-to-be-an-engineer',
                  kind='First-hand as candidate and interviewer — company not named, so not LinkedIn evidence', grade='ADVICE'),
 'hi-comm':  dict(name='Hello Interview community — "Implement LRU Cache"', date='LinkedIn Senior report, late Sep 2026',
                  url='https://www.hellointerview.com/community/questions/lru-cache-implementation/cmk5avhlo00x708adxjp1vuil',
                  kind='Aggregated reports; round not visible (paywalled)', grade='REPORTED'),
 'gd-lru':   dict(name='Glassdoor — "LRU Cache type question with little modification around locks and multithreading"', date='undated',
                  url='https://www.glassdoor.com/Interview/Technical-round-LRU-Cache-type-question-with-little-modification-around-locks-and-multithreading-Pretty-easy-one-Beh-QTN_2477405.htm',
                  kind='Candidate report; round not stated', grade='REPORTED'),
 'fastprep': dict(name='FastPrep — "Thread-Safe LRU Cache with TTL (LinkedIn Onsite)"', date='undated',
                  url='https://www.fastprep.io/problems/linkedin-thread-safe-lru-cache-with-ttl',
                  kind='Aggregator; no date, round not stated', grade='REPORTED'),
 'blind-st': dict(name='Blind — "LinkedIn staff coding with AI"', date='2 Apr 2026',
                  url='https://www.teamblind.com/post/linkedin-staff-coding-with-ai-5ojxt7wa',
                  kind='A question, not a report — no first-hand detail in the thread', grade='ADVICE'),
 'hi-log':   dict(name='Hello Interview community — "Design a Logging Library with Severity Filtering, Rate Limiting, and Aggregation"',
                  date='Staff early Aug 2026 · Senior late Aug and mid Sep 2026',
                  url='https://www.hellointerview.com/community/questions/logging-rate-limiting-aggregation/cmngssoui03dv08ad7frmgtw5',
                  kind='Aggregated candidate reports, LinkedIn AI-enabled round — 5 reports, 3 visible without premium', grade='REPORTED'),
 'idb':      dict(name='InterviewDB — the 17 LinkedIn questions you supplied', date='supplied Sep 2026',
                  url='09-question-bank.html', kind='Paid question bank; LinkedIn coding, round not stated', grade='REPORTED'),
}

# (claim, grade, [source keys], note)
CLAIMS = [
 # ---- format
 ('The module is 60 minutes, in CoderPad, with the built-in AI Assist chat.', 'CONFIRMED', ['pack'],
  'Supersedes the HackerRank report for your loop. Other teams may run other platforms.'),
 ('Using AI is expected, but there is no expectation that AI solves every part or that you maximise its use.', 'CONFIRMED', ['pack'], ''),
 ('No prescribed workflow: reason first then accelerate, or explore with AI then refine — either is fine if deliberate.', 'CONFIRMED', ['pack'],
  'Note: "understand before you prompt" is my recommendation, not LinkedIn\'s rule. The pack explicitly allows exploring with AI first.'),
 ('It is not a prompt-engineering test. They evaluate when you reach for AI, how you steer it, how you judge its output.', 'CONFIRMED', ['pack'], ''),
 ('"Critically evaluate AI-generated output rather than accepting it at face value."', 'CONFIRMED', ['pack'],
  'The closest thing to LinkedIn\'s own words on "do not blindly trust AI".'),
 ('The interviewer may interrupt to ask about your thought process and how you are using AI.', 'CONFIRMED', ['pack'], ''),
 ('"Very new, we started to let candidates use AI for interviews now … you basically have to know how to prompt well, like test cases, full design specs … it\'s a lot more code to write."',
  'CONFIRMED', ['li-emp'], 'An anonymous LinkedIn employee on Blind, Oct 2025. Strong but unverifiable; "a lot more code" matters for timing.'),
 ('The interview is reviewed by "AI as well + humans".', 'CONFIRMED', ['li-emp'],
  'Same single comment. Treat as plausible, not established.'),
 ('The AI panel sits beside the editor and cannot edit your file — you copy code across yourself.', 'REPORTED', ['hi-ai'],
  'Several candidates via Hello Interview. Practise the copy-adapt step; it costs real minutes.'),
 ('You can choose between a small set of models (Claude reported).', 'REPORTED', ['hi-ai', 'dg'], ''),
 ('The AI round replaced the second traditional coding round; the loop keeps one no-AI coding round.', 'REPORTED', ['hi-ai'],
  'Consistent with the pack, which lists Staff Coding (no AI) as a separate module.'),
 ('The interviewer can see the whole AI conversation — every prompt, every accepted or ignored response.', 'ADVICE', ['shahdeo'],
  'First-hand about CoderPad interviews generally, company not named. Assume it is true: it costs nothing.'),
 # ---- questions and arc
 ('Problems are well-known patterns — caches, intervals, data processing — with manageable code volume.', 'REPORTED', ['hi-ai', 'cond'], ''),
 ('Follow-ups pivot to concurrency, multithreading, synchronisation and "how would you productionise this?"', 'REPORTED', ['hi-ai', 'cond', 'gd-lru'],
  'The single most consistent finding across sources.'),
 ('Phased arc: fix a bug → implement a feature → optimise for edge cases or larger inputs.', 'REPORTED', ['exp-exp', 'dg'],
  'One LinkedIn report (the maze) plus guides. Prepare for it; do not assume it.'),
 ('Interviewers keep adding requirements to the same code ("add a method to validate keys").', 'REPORTED', ['lc-aie'],
  'The candidate reports over-engineering by prompting for each addition. That is the failure to avoid.'),
 ('A candidate was asked to explain and solve mathematically before coding (rejection sampling, rand7 → rand10 style).', 'REPORTED', ['lc-ml'],
  'Read via search summary only.'),
 ('A logging library built in four phases — severity filter, unit tests, throttling identical logs in a window, aggregating the suppressed count — reported five times, including a Staff candidate in Aug 2026.',
  'REPORTED', ['hi-log'], 'The most recent Staff-level AI-round evidence in this file. One report mentions a Python repo — a starter codebase, not a blank pad.'),
 ('A Sep 2026 IC2 round paired an LRU with counters and asked for predicted hit/miss ratios under different workloads.', 'REPORTED', ['prachub'],
  'The most recent AI-round question in this file.'),
 # ---- evaluation
 ('A 4-point scale where 3 passes, on prompt quality, verification, production thinking and communication.', 'REPORTED', ['hi-ai'],
  'Described by Hello Interview; not in the pack. The 70-point rubric on the simulator page is my own and says so.'),
 ('How often you use the assistant is not graded; understanding, critical thinking and decisions are.', 'ADVICE', ['dg'], 'Consistent with the pack.'),
 ('Candidates spend too long on the first implementation and run out of time for the follow-ups.', 'REPORTED', ['hi-ai'],
  'The most-repeated timing mistake. The time plans on this page budget for it.'),
 ('Exact minute-by-minute timing inside the 60 minutes.', 'INFERENCE', [],
  'Nobody has published it. The phase splits on this page are mine, built from the arc above.'),
 ('Staff candidates are held to calibrated judgement: when to use AI, when not to, when to prove correctness yourself.', 'ADVICE', ['cond'], ''),
]

# ---------------------------------------------------------------- question bank
# prio: 'P0' must master · 'P1' high priority · 'P2' supporting practice   (the reader's P0/P1 list, Oct 2026)
# label: one of LABELS below — how the question is evidenced
# tier is kept as the numeric form of prio (1/2/3) for sorting and the simulator
# ev:   STRONG (several sources or AI-round first-hand + corroboration) · MEDIUM (one AI-round report)
#       · ADJACENT (LinkedIn coding, round not stated) · PATTERN (not reported — practice only)
# study: 'full' = studied in full on this page · 'qbank:<id>' = full solution on 09-question-bank.html
#        · 'drill:<id>' = the CWAI drill on this page
Q = [
 dict(id='lru', cat='A', tier=1, title='LRU cache → TTL → thread-safe → scale', ev='STRONG',
      src=['hi-ai', 'cond', 'lc-aie', 'gd-lru', 'hi-comm', 'fastprep', 'idb'], date='Feb–Sep 2026',
      wording='"Implement an LRU cache" with the AI assistant available; follow-ups on concurrency, synchronisation and productionising (Hello Interview). '
              '"Add a method to validate keys" (LeetCode, AI Engineer). InterviewDB: "Implement an LRU Cache with TTL expiry … get() should return -1 if the key has expired even if it is still in the cache."',
      variation='TTL per entry; thread-safe with TTL (FastPrep); "LRU type question with little modification around locks and multithreading" (Glassdoor).',
      follow=['Add TTL', 'Make it thread-safe', 'Millions of requests per second', 'Stop expired entries growing memory', 'Distribute it'],
      why='The best-attested AI-round question: one first-hand AI-round report, two guides, three more LinkedIn reports of the same family. Every follow-up you are likely to get is in this one ladder.',
      study='full'),
 dict(id='lrucount', cat='A', tier=1, title='LRU with counters — predict the hit/miss ratio', ev='MEDIUM',
      src=['prachub'], date='Sep 2026',
      wording='"LRU Cache with Counters" — given different workloads, "predict and calculate the cache\'s hit/miss ratio" (IC2, PracHub, Sep 2026).',
      variation='Exact workloads not published. The obvious ones: a scan larger than the cache, a uniform working set, a skewed one.',
      follow=['Predict before you measure', 'Why does a scan of capacity+1 keys get zero hits?', 'Make the counters thread-safe', 'Which eviction policy fixes scans?'],
      why='The most recent AI-round question in the research, and it tests the thing the round is built on: reasoning about behaviour rather than just producing code.',
      study='full'),
 dict(id='lfurank', cat='A', tier=1, title='LFU cache with GetRank(), LRU tie-break', ev='MEDIUM',
      src=['hi-ai'], date='Feb 2026',
      wording='"LFU Cache — eviction by ranking with an LRU tiebreaker" — reported as the Staff-level variant (Hello Interview).',
      variation='Plain LFU appears in a 2025 phone screen in the earlier research pass.',
      follow=['Complexity of GetRank()', 'Keep O(1) Get/Put while supporting rank', 'Thread-safety', 'Rank in O(log n)'],
      why='Reported specifically at Staff level. The trap is promising O(1) rank: an assistant will happily claim it.',
      study='full'),
 dict(id='intervals', cat='E', tier=1, title='Interval manager — add/insert with your own bookkeeping', ev='STRONG',
      src=['hi-ai', 'cond'], date='Feb–Jun 2026',
      wording='"Not the classic merge intervals" — you are given addInterval() and insertInterval() signatures and must choose the data structure (Hello Interview).',
      variation='Coditioning lists "interval managers with overlap handling".',
      follow=['Remove an interval (splits)', 'Point and overlap queries', 'Total covered length in O(1)', 'Millions of intervals; concurrent writers'],
      why='Two sources, AI-round specific. The decision being tested — sorted structure versus re-sorting a list — is exactly the one an assistant gets lazily wrong.',
      study='full'),
 dict(id='records', cat='C', tier=1, title='Structured data processing — JSON-like records, malformed rows', ev='STRONG',
      src=['hi-ai', 'cond'], date='Feb–Jun 2026',
      wording='"Structured data processing — JSON-like objects requiring class creation and testing from scratch" (Hello Interview); "JSON-like data transformation with malformed records" (Coditioning).',
      variation='Exact schema not published.',
      follow=['Malformed and missing fields', 'Report what was rejected and why', 'Stream a 50 GB file', 'Parallelise the aggregation'],
      why='Two sources. This is where AI legitimately saves the most time (boilerplate) and where blindly trusting it costs the most (silent data loss).',
      study='full'),
 dict(id='logging', cat='C', tier=1, title='Logging library — severity, throttling, aggregation, then production', ev='STRONG',
      src=['hi-log'], date='Aug–Sep 2026 (Staff + Senior)',
      wording='"Design a Logging Library with Severity Filtering, Rate Limiting, and Aggregation" — four phases: (1) a logger initialised with a minimum severity '
              '(DEBUG, INFO, WARN, ERROR) that prints only logs at or above it; (2) unit tests; (3) throttling: an identical log (same severity, function name, line '
              'number and message) repeated within a window prints once; (4) aggregation: when the window expires and the next identical log arrives, print a summary '
              'of the suppressed logs using the timestamp of the first occurrence in that window.',
      variation='One report mentions a Python-based starter repo. Production extensions (multiple sinks, back-pressure, buffering, metrics) are the natural follow-ups, not reported phases.',
      follow=['10,000 threads logging at once', 'Logging must never be the bottleneck', 'Do not overwhelm downstream', 'Memory of the throttle table', 'A sink fails'],
      why='Five reports in Aug–Sep 2026, one of them Staff — the freshest and most level-relevant AI-round question found. Phased exactly the way the round is described.',
      study='full'),
 dict(id='maze', cat='B', tier=2, title='Debug and extend a maze class', ev='MEDIUM',
      src=['exp-exp'], date='≈ Mar 2026',
      wording='A buggy maze class to debug and build out with the built-in assistant. Follow-ups, verbatim: "How would you make sure the maze is well formed, including the outer wall?" · '
              '"Given a start and end position, how would you generate the maze so there is always a path?" · "Why did you choose this AI-generated approach over the other options?" · '
              '"How would you test each change?" · "If this went to production, what would you change?"',
      variation='Reported on HackerRank, not CoderPad — a different team\'s setup.',
      follow=['Well-formedness incl. outer wall', 'Generate with a guaranteed path', 'Why this AI approach?', 'Test each change', 'Productionise'],
      why='One report, but the only one with the follow-ups verbatim, and the debug-then-extend arc it shows is corroborated by the guides.',
      study='full'),
 dict(id='rand10', cat='G', tier=2, title='Rejection sampling — rand7 → rand10, explained first', ev='MEDIUM',
      src=['lc-ml', 'idb'], date='≈ late 2025',
      wording='"Rejection sampling problems similar to rand7() → rand10()", with the expectation to "explain and solve mathematically before coding it" (LeetCode Discuss, read via search summary).',
      variation='rand01 → rand06 is the same idea from a coin (3 bits, keep 6 of 8 outcomes) — the general form below covers both, and is tested exactly. InterviewDB Q4 is the inverse: fair output from a biased generator.',
      follow=['Prove it is uniform', 'Expected calls', 'Generalise to any n from any m', 'Fair from biased (Q4)'],
      why='Single source read second-hand, but it is the one AI-round report that tests mathematical reasoning — the thing AI is worst at checking for you.',
      study='full'),
 dict(id='queue', cat='D', tier=2, title='Producer/consumer — bounded blocking queue', ev='ADJACENT',
      src=['hi-ai', 'cond'], date='2026',
      wording='Not reported as a standalone question. Concurrency is the reported pivot ("thread-safety additions to single-threaded solutions", Coditioning); this is the primitive those follow-ups reduce to.',
      variation='—', follow=['Cancellation', 'Graceful shutdown', 'Async version', 'Back-pressure in production'],
      why='The concurrency pivot is the most consistent finding; this is the cleanest place to practise owning a synchronization boundary.',
      study='full'),
 dict(id='scheduler', cat='D', tier=2, title='Delay scheduler / scheduled executor', ev='ADJACENT',
      src=['idb'], date='supplied Sep 2026', wording='InterviewDB Q7 — see the question bank for the verbatim statement.',
      variation='—', follow=['Cancel a scheduled task', 'Many workers', 'Clock jumps', 'Shutdown with tasks pending'],
      why='LinkedIn coding question with built-in concurrency; round not stated.', study='qbank:q7'),
 dict(id='rankcache', cat='A', tier=2, title='Rank-based cache (caller supplies the rank)', ev='ADJACENT',
      src=['idb'], date='supplied Sep 2026', wording='InterviewDB Q13.', variation='Sits between LRU and LFU+GetRank.',
      follow=['Ties', 'Rank updates', 'Thread-safety'], why='Same family as the Tier 1 caches.', study='qbank:q13'),
 dict(id='distance', cat='B', tier=2, title='Connection distance (degrees of separation)', ev='ADJACENT',
      src=['idb'], date='supplied Sep 2026', wording='InterviewDB Q5.', variation='Bidirectional BFS.',
      follow=['Bidirectional BFS', 'Graph does not fit in memory', 'Friend recommendations'], why='LinkedIn\'s signature graph question; round not stated.', study='qbank:q5'),
 dict(id='taskmgr', cat='B', tier=2, title='Task manager — dependency graph with cycle detection', ev='ADJACENT',
      src=['idb'], date='supplied Sep 2026', wording='InterviewDB Q15.', variation='—',
      follow=['Cycle across two AddTask calls', 'Parallel waves', 'Concurrent completion'],
      why='Writing its tests found a real bug in my own first answer — exactly the verification habit the AI round scores.', study='qbank:q15'),
 dict(id='covered', cat='E', tier=2, title='Interval tree — covered size', ev='ADJACENT',
      src=['idb'], date='supplied Sep 2026', wording='InterviewDB Q9.', variation='The Tier 1 interval manager with an O(1) size query.',
      follow=['Amortised vs worst case', 'Remove'], why='Same structure as the Tier 1 interval question.', study='qbank:q9'),
 dict(id='mergetrees', cat='F', tier=2, title='Merge two metadata trees', ev='ADJACENT',
      src=['idb'], date='supplied Sep 2026', wording='InterviewDB Q17.', variation='Keyed n-ary tree merge.',
      follow=['Conflict policy', 'Do not mutate inputs', 'Concurrent readers during merge'],
      why='Tagged CONCURRENCY in InterviewDB and carries the aliasing trap that debugging exercise D8 is built on.', study='qbank:q17'),
 dict(id='wordladder', cat='B', tier=3, title='Word transformation (word ladder)', ev='ADJACENT',
      src=['idb'], date='supplied Sep 2026', wording='InterviewDB Q8.', variation='Wildcard index.',
      follow=['Edge count vs word count', 'All shortest paths'], why='Graph pattern; round not stated.', study='qbank:q8'),
 dict(id='leaves', cat='F', tier=3, title='Remove leaf levels', ev='ADJACENT',
      src=['idb'], date='supplied Sep 2026', wording='InterviewDB Q10.', variation='Height from the bottom.',
      follow=['Iterative version', 'Do not mutate the input'], why='Tree pattern; round not stated.', study='qbank:q10'),
 dict(id='biased', cat='G', tier=3, title='Biased random generator', ev='ADJACENT',
      src=['idb'], date='supplied Sep 2026', wording='InterviewDB Q4.', variation='Inverse of rand7 → rand10.',
      follow=['Expected flips', 'Unknown bias'], why='Randomisation pattern; round not stated.', study='qbank:q4'),
 dict(id='randbag', cat='G', tier=3, title='Insert / remove / get-random in O(1)', ev='ADJACENT',
      src=['idb'], date='supplied Sep 2026', wording='InterviewDB Q12.', variation='Duplicates allowed.',
      follow=['Duplicates', 'Weighted random'], why='Randomisation + data structure design.', study='qbank:q12'),
 dict(id='topk', cat='C', tier=3, title='Top-K frequent items in a stream', ev='PATTERN',
      src=[], date='—', wording='Not reported for LinkedIn\'s AI round. Pattern practice for "metrics and counters".',
      variation='—', follow=['Exact vs approximate', 'Sliding window', 'Merge across shards'],
      why='The review exercise R5 is built on it.', study='drill:topk'),
 dict(id='window', cat='C', tier=3, title='Sliding-window event counter ("hits in the last 5 minutes")', ev='PATTERN',
      src=[], date='—', wording='Not reported for LinkedIn\'s AI round. Pattern practice.',
      variation='—', follow=['Thread-safety', 'O(1) reads', 'Many keys', 'Across machines'],
      why='The smallest problem that forces a time-bucketing and a locking decision together.', study='full'),
]

LABELS = {
 'multi':   'Multiple candidate reports',
 'single':  'Reported LinkedIn question',
 'idb':     'InterviewDB question',
 'derived': 'Research-derived practice',
 'pattern': 'Pattern-based practice',
}
# The reader's priority list (Oct 2026). P0: caches, logging, structured data, intervals.
# P1: graph/routing, randomisation. Everything else supports the follow-ups.
PRIO = {
 'lru': 'P0', 'lrucount': 'P0', 'lfurank': 'P0', 'rankcache': 'P0', 'logging': 'P0', 'records': 'P0', 'intervals': 'P0', 'covered': 'P0',
 'distance': 'P1', 'taskmgr': 'P1', 'wordladder': 'P1', 'maze': 'P1', 'rand10': 'P1', 'biased': 'P1', 'randbag': 'P1',
 'queue': 'P2', 'scheduler': 'P2', 'mergetrees': 'P2', 'leaves': 'P2', 'topk': 'P2', 'window': 'P2',
}
LABEL = {
 'lru': 'multi', 'intervals': 'multi', 'records': 'multi', 'logging': 'multi',
 'lrucount': 'single', 'lfurank': 'single', 'maze': 'single', 'rand10': 'single',
 'queue': 'derived',
 'topk': 'pattern', 'window': 'pattern',
}
for _q in Q:
    _q['prio'] = PRIO[_q['id']]
    _q['tier'] = {'P0': 1, 'P1': 2, 'P2': 3}[_q['prio']]
    _q['label'] = LABEL.get(_q['id'], 'idb')
Q.sort(key=lambda q: (q['tier'], ['multi', 'single', 'idb', 'derived', 'pattern'].index(q['label'])))

CATS = {'A': 'Cache / data structures', 'B': 'Graph', 'C': 'Data processing', 'D': 'Concurrency',
        'E': 'Interval / range', 'F': 'Tree', 'G': 'Randomisation'}
