# -*- coding: utf-8 -*-
"""Chapter 4, Lesson 3 — top-N requests over the last 24 hours."""
from lib import *

lesson_header('4.3', 'Top-N requests over the last 24 hours',
              'Heavy hitters &middot; count-min sketch &middot; fixed windows &middot; exact vs approximate',
              dict(reports='InterviewTV list only', latest='2026', level='Staff',
                   conf='MEDIUM &mdash; single source', sources='InterviewTV.io'), 16,
              """Chapter four, lesson three: top-N requests over the last twenty-four hours. Hundreds of """
              """machines serving requests, and you need to answer &mdash; what were the N most frequent """
              """requests? Top searched strings, top requested keys. This question has a trap in the """
              """wording that most candidates walk straight past, and it also has the single most """
              """common wrong answer in distributed systems interviews. We will hit both.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  'Explicitly flags: <b>&ldquo;last 24 hours means the fixed previous 24-hour period, not an '
  'arbitrary rolling window&rdquo;</b>'),
 ('Related &mdash; lessons 2.3 and 6.3', '2025&ndash;2026', 'Staff, Infra',
  'The ingestion and aggregation machinery is shared with metrics and logging'),
], """Single source, so medium confidence. But look closely at how the question was written down: it """
     """explicitly flags that &ldquo;last twenty-four hours&rdquo; means the fixed previous """
     """twenty-four hour period, not an arbitrary rolling window.""",
 ["""When a question ships with a clarification already attached, somebody added that because """
  """candidates kept getting it wrong. That sentence is not context — it is the hint."""],
 caveat='Single source. But the machinery here is shared with metrics and logging, so it is good '
        'preparation regardless of whether this exact framing appears.',
 narration_caveat="""Single source, so hold the exact framing loosely. The machinery is shared with """
                  """metrics and logging, so this prepares you either way.""")

sid = beat('Why this is interesting', 'The trap is in the word &ldquo;fixed&rdquo;. The bug is in the merge.',
           '<div style="font-size:28px;line-height:1.72">'
           '<b>Trap 1 &mdash; fixed vs rolling.</b><br>'
           '&ldquo;Any rolling 24h&rdquo; means you must be able to answer for <i>any</i> start time, '
           'so you need per-window counts and a sliding aggregate. Expensive.<br>'
           '&ldquo;The previous fixed 24h&rdquo; means <b>one batch, computed once, served all day.</b> '
           '<span style="color:#a8e6a3">Dramatically cheaper.</span><br><br>'
           '<b>Trap 2 &mdash; the merge that looks right and is wrong.</b><br>'
           'Each machine keeps its own top 100 and you merge them. Obvious. Fast.<br>'
           '<span style="color:#ff9a9a">And wrong: an item ranked #101 on all 300 machines can beat '
           'an item ranked #1 on one machine &mdash; and you threw it away before the merge.</span>'
           '<br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: local top-K does not merge into global '
           'top-K. You need counts, or a sketch with an error bound.</span></div>',
           """Why is this interesting? Two traps, and they are both worth more than the architecture.""",
           step=0)
seg(sid, 1, """Trap one is the word fixed. If the requirement is any rolling twenty-four hours, you must """
            """be able to answer for any start time, which means keeping per-window counts and """
            """maintaining a sliding aggregate. That is genuinely expensive. If it is the previous fixed """
            """twenty-four hours, it is one batch job, computed once, and served all day. Same sentence """
            """in English, an order of magnitude apart in cost.""")
seg(sid, 2, """Trap two is the merge, and this is the one that catches strong candidates. Each machine """
            """keeps its own top hundred, and you merge the three hundred lists. It is obvious, it is """
            """fast, and it is wrong.""")
seg(sid, 3, """Here is why. An item that ranks a hundred-and-first on every single one of three hundred """
            """machines has a large global count — but it never appears in any local top hundred, so you """
            """discarded it before the merge could see it. Meanwhile an item that is number one on a """
            """single machine and absent elsewhere sails through. Local top-K does not merge into global """
            """top-K. That is the staff-level insight, and if you say it unprompted the interviewer will """
            """know you have thought about this before.""")

think('Three hundred machines. You want the global top 100 search strings. If each machine sends you its '
      'own top 100, what is the worst-case error &mdash; and what would each machine have to send '
      'instead for the answer to be exactly right?',
      25,
      """Pause. Three hundred machines, you want the global top hundred. If each sends you its own top """
      """hundred, what is the worst-case error? And what would each machine have to send instead for """
      """the answer to be exactly right? Say it out loud.""",
      """Hold that. The exact answer requires every machine to send every count, which is the whole """
      """dataset — and that is precisely why approximation exists.""")

clarify('What I would clarify first', [
 ('Fixed previous 24h, or any rolling 24h?',
  '<b>The single biggest cost lever in the question.</b> Fixed is one daily batch. Rolling needs '
  'incremental windows and a sliding merge.'),
 ('How exact does it need to be?',
  'If &ldquo;roughly the top 100, with the top 10 definitely right&rdquo; is acceptable, a sketch '
  'solves it in megabytes. If it must be provably exact, you are doing a full aggregation.'),
 ('How many distinct keys are there?',
  'A million distinct searches fits in memory per machine. A billion distinct URLs does not &mdash; '
  'and that is what forces a sketch.'),
 ('How fresh must the answer be &mdash; yesterday&rsquo;s, or the last hour&rsquo;s?',
  'Daily means batch. Near-real-time means a streaming path, which is a much bigger system.'),
 ('Is this a one-off report, or a product surface?',
  'A dashboard an engineer reads twice a week justifies nothing. If it feeds ranking or abuse '
  'detection, latency and correctness both matter.'),
 ('Top-N by count, or by distinct users?',
  'Distinct-user counting is a <b>completely different problem</b> &mdash; that is HyperLogLog, not '
  'a frequency counter. One bot hitting a URL a million times is not a popular URL.'),
], [
 """Fixed or rolling? This is the biggest cost lever in the question and it is already answered in the """
 """prompt — but I would still say it back to confirm, because confirming a constraint you were given """
 """shows you read it.""",
 """How exact does it need to be? If roughly the top hundred, with the top ten definitely correct, is """
 """acceptable, a sketch solves this in megabytes. If it must be provably exact, you are committed to a """
 """full aggregation over the whole dataset.""",
 """How many distinct keys? A million distinct search strings fits in memory on every machine, and then """
 """you barely need cleverness. A billion distinct U-R-Ls does not, and that is what forces a sketch. """
 """Ask before you design.""",
 """How fresh must the answer be — yesterday's, or the last hour's? Daily means batch. Near-real-time """
 """means a streaming path and a much bigger system.""",
 """Is this a one-off report or a product surface? A dashboard an engineer reads twice a week justifies """
 """almost no engineering. If it feeds ranking or abuse detection, both latency and correctness """
 """suddenly matter.""",
 """And the one candidates almost never ask: top N by raw count, or by distinct users? Those are """
 """completely different problems. Distinct counting is HyperLogLog, not a frequency counter. One bot """
 """hitting a U-R-L a million times is not a popular U-R-L, and if nobody asks, you will build the """
 """wrong thing correctly.""",
])

capacity('Capacity', [
 ('300 machines &times; 5,000 req/s', '1.5M req/s &times; 86,400',
  '&asymp; 130B requests / day', 'Far too many to ship centrally as raw events'),
 ('Raw events, if shipped: 100 B each', '130B &times; 100 B', '&asymp; 13 TB / day',
  '<b>Rules out the naive design immediately.</b> Say this number out loud'),
 ('Distinct keys', 'assume ~500M distinct strings / day', '500M keys',
  'An exact hash map at ~50 B/entry is <b>25 GB</b> &mdash; per machine, impossible'),
 ('Local pre-aggregation per machine', '500M distinct, but only ~2M seen per machine',
  '&asymp; 100 MB / machine', '<b>Fits.</b> Aggregate at the edge, ship counts not events'),
 ('Counts shipped per machine per minute', '2M keys &times; 30 B &times; 300 machines',
  '&asymp; 18 GB / min', 'Still too much. <b>Ship only keys above a threshold</b>'),
 ('Count-min sketch, 0.1% error', 'width 20k &times; depth 5 &times; 4 B', '&asymp; 400 KB / machine',
  '<b>120 MB total across the fleet.</b> Five orders of magnitude smaller than raw'),
], [
 """Numbers, and in this question the arithmetic does the arguing for you. Three hundred machines at """
 """five thousand requests a second is one and a half million a second, which is about a hundred and """
 """thirty billion requests a day.""",
 """If you ship those raw at a hundred bytes each, that is thirteen terabytes a day just to count """
 """things. Say that number out loud in the interview, because it rules out the naive design """
 """immediately and shows you are reasoning rather than reciting.""",
 """Distinct keys — call it five hundred million distinct strings a day. An exact hash map at fifty """
 """bytes an entry is twenty-five gigabytes, which you cannot hold on every machine.""",
 """But each individual machine only sees a slice — maybe two million distinct keys. That is about a """
 """hundred megabytes, which fits comfortably. So the first architectural move falls straight out of """
 """the numbers: aggregate at the edge and ship counts, not events.""",
 """Except shipping two million keys per machine per minute across three hundred machines is still """
 """eighteen gigabytes a minute. Still too much. So you ship only keys above a threshold.""",
 """Or you use a count-min sketch. At a tenth of a percent error that is roughly four hundred kilobytes """
 """per machine — a hundred and twenty megabytes across the entire fleet. Five orders of magnitude """
 """smaller than the raw events. That is the number that justifies the whole design.""",
])

A = Arch('Top-N &mdash; aggregate at the edge, merge in the middle', kicker='Architecture', height=780)

A.box('m1',   60, 200, 165, 80, 'Machine 1', '5k req/s', kind='neutral', step=0, focus=0, small=True)
A.box('m2',   60, 310, 165, 80, 'Machine 2', '', kind='neutral', step=0, focus=0, small=True)
A.box('m3',   60, 420, 165, 80, 'Machine 300', '', kind='neutral', step=0, focus=0, small=True)

A.box('lo1', 290, 200, 215, 80, 'Local sketch', 'CMS + top-K heap', kind='ok', step=1, focus=[1, 2], small=True)
A.box('lo2', 290, 310, 215, 80, 'Local sketch', '', kind='ok', step=1, focus=[1, 2], small=True)
A.box('lo3', 290, 420, 215, 80, 'Local sketch', '', kind='ok', step=1, focus=[1, 2], small=True)
A.arrow('m1', 'lo1', step=1, focus=1); A.arrow('m2', 'lo2', step=1, focus=1); A.arrow('m3', 'lo3', step=1, focus=1)

A.box('kaf', 580, 300, 205, 105, 'Kafka', 'sketches, 1/min', kind='info', step=2, focus=2)
A.arrow('lo1', 'kaf', step=2, focus=2); A.arrow('lo2', 'kaf', step=2, focus=2); A.arrow('lo3', 'kaf', step=2, focus=2)

A.box('mrg', 860, 290, 225, 115, 'Merger', 'sum sketches / minute', kind='shared', step=3, focus=3)
A.arrow('kaf', 'mrg', step=3, focus=3)

A.box('min', 1160, 180, 215, 95, 'Minute buckets', '1,440 per day', kind='dp', step=4, focus=[4, 5], small=True)
A.arrow('mrg', 'min', step=4, focus=4)

A.box('day', 1160, 330, 215, 95, 'Daily roll-up', 'the answer', kind='ok', step=5, focus=5, small=True)
A.arrow('min', 'day', step=5, focus=5)

A.box('api', 1160, 480, 215, 95, 'Query API', 'top-N, cached', kind='neutral', step=6, focus=6, small=True)
A.arrow('day', 'api', step=6, focus=6)

A.note(580, 480, 'Sketches are MERGEABLE: summing two count-min sketches gives the sketch of the union. That property is the whole design.',
       step=3, kind='info', w=470)

A.narrate(0, """Three hundred machines serving traffic. That is the input.""")
A.narrate(1, """First move, and it comes straight from the arithmetic: each machine aggregates locally. A """
             """count-min sketch for the counts, plus a small heap holding the local top few thousand """
             """candidates. Nothing leaves the machine per request.""",
          A.flow([(225, 240), (290, 240)]))
A.narrate(2, """Once a minute each machine ships its sketch to Kafka. Four hundred kilobytes, three """
             """hundred machines, once a minute — that is trivial traffic compared with thirteen """
             """terabytes of raw events.""",
          A.flow([(505, 350), (580, 350)]))
A.narrate(3, """A merger sums the sketches. And here is the property that makes the entire design work, """
             """so say it explicitly: count-min sketches are mergeable. Summing two sketches """
             """element-wise gives you exactly the sketch you would have got from the union of both """
             """streams. Not an approximation of a merge — the actual merged sketch. That is why this """
             """decomposes across machines at all.""",
          A.flow([(785, 350), (860, 350)]))
A.narrate(4, """Merged sketches are stored per minute. One thousand four hundred and forty buckets a """
             """day.""",
          A.flow([(1085, 350), (1160, 230)]))
A.narrate(5, """And because they are mergeable, the daily answer is just the sum of the day's minute """
             """buckets. Which quietly gives you the rolling window for free later, if the requirement """
             """ever changes — sum any 1,440 consecutive buckets. I would mention that as headroom """
             """rather than build it now.""",
          A.flow([(1267, 275), (1267, 330)]))
A.narrate(6, """And a query A-P-I serving the precomputed top-N, cached. The answer changes once a day, """
             """so the cache hit rate is effectively one hundred percent.""")
A.build()

sid = beat('Deep dive 1', 'Count-min sketch, and why it never **under**-counts',
           '<div style="font-size:27px;line-height:1.7">'
           'A 2-D array of counters: <b>d</b> rows, <b>w</b> columns, and <b>d</b> hash functions.<br><br>'
           '<b>Increment:</b> for each row i, <code>table[i][hash_i(key) % w] += 1</code><br>'
           '<b>Estimate:</b> take the <b>minimum</b> across the d rows.<br><br>'
           'Collisions only ever <i>add</i> other keys&rsquo; counts, so every row over-estimates. '
           'Taking the minimum picks the row that collided least.<br><br>'
           '<span style="color:#a8e6a3">Guarantee: never under-counts. Over-counts by more than '
           '&epsilon;N with probability &lt; &delta;.</span><br><br>'
           '<b>Why one-sided error matters here:</b> a genuinely heavy hitter can never be hidden by '
           'the sketch. You may admit an impostor; you cannot lose a real one.<br><br>'
           '<span style="color:#ffd483">The sketch gives counts, not identities &mdash; so keep a '
           'separate heap of candidate keys. That pairing <i>is</i> the algorithm.</span></div>',
           """Deep dive one: the count-min sketch, because if you name it you will be asked how it """
           """works. It is a two-dimensional array of counters — d rows, w columns — and d hash """
           """functions.""", step=0)
seg(sid, 1, """To increment a key, you hash it once per row and bump the counter in that row's column. To """
            """estimate its count, you look at all d cells and take the minimum.""")
seg(sid, 2, """Why the minimum? Because collisions only ever add other keys' counts on top of yours. """
            """Every row over-estimates, never under. Taking the smallest picks whichever row happened """
            """to collide least.""")
seg(sid, 3, """That gives you a one-sided guarantee: it never under-counts, and it over-counts by more """
            """than epsilon-N only with probability delta. And one-sided error is exactly the property """
            """this problem needs — a genuinely heavy hitter can never be hidden by the sketch. You """
            """might admit an impostor into your top hundred; you can never lose a real one. Say that """
            """out loud, because it is the reason this structure fits the question rather than just """
            """being a structure you know.""")
seg(sid, 4, """One catch that candidates miss: the sketch stores counts, not keys. It can tell you how """
            """often a key was seen if you hand it the key, but it cannot enumerate. So you keep a """
            """separate bounded heap of candidate keys alongside it. The sketch plus the heap is the """
            """algorithm — neither half works alone.""")

sid = beat('Deep dive 2', 'Exact when you can, approximate when you must',
           '<div style="font-size:28px;line-height:1.72">'
           '<b>Do not reach for a sketch by default.</b> Reach for it when the numbers say you must.<br><br>'
           '<b>Exact is affordable when:</b> distinct keys &times; entry size fits in one machine&rsquo;s '
           'memory after shuffling by key.<br>'
           '500M keys &times; 50 B = 25 GB &mdash; shuffled across 30 reducers that is <b>under 1 GB '
           'each.</b> <span style="color:#a8e6a3">An exact MapReduce is entirely reasonable.</span><br><br>'
           '<b>Approximate is required when:</b> you need the answer <i>continuously</i>, not once a '
           'day, and cannot afford to shuffle 13 TB every time.<br><br>'
           '<b>The honest answer in an interview:</b><br>'
           '&bull; Daily, fixed window &rarr; <b>exact batch</b>. Simple, provable, cheap to operate.<br>'
           '&bull; Continuous / near-real-time &rarr; <b>sketch</b>, with the error bound stated.<br>'
           '&bull; Both &rarr; run the sketch live and reconcile against the batch nightly '
           '(<span style="color:#a8e6a3">lambda architecture, and say why you are paying for it</span>)'
           '</div>',
           """Deep dive two, and this is where I would push back gently on the obvious answer. Do not """
           """reach for a sketch by default. Reach for it when the numbers say you must, and be able to """
           """say when they do not.""", step=0)
seg(sid, 1, """Exact is affordable when the distinct keys times entry size fits in one machine's memory """
            """after you shuffle by key. Five hundred million keys at fifty bytes is twenty-five """
            """gigabytes total — but shuffled across thirty reducers that is under a gigabyte each. An """
            """exact MapReduce over a day of logs is entirely reasonable, and it is provably correct.""")
seg(sid, 2, """Approximate becomes necessary when you need the answer continuously rather than once a """
            """day, and cannot afford to shuffle thirteen terabytes every time you want it.""")
seg(sid, 3, """So the honest interview answer has three branches. Daily and fixed window — which is what """
            """this question actually asks — is an exact batch job. Simple, provable, cheap to operate. """
            """Continuous or near-real-time is the sketch, with the error bound stated out loud.""")
seg(sid, 4, """And if they want both, you run the sketch live for freshness and reconcile against the """
            """exact batch nightly. That is a lambda architecture, and I would name it and then """
            """immediately say what it costs: two implementations of the same logic that must agree, """
            """which is an ongoing operational tax. Choosing it deliberately is fine. Drifting into it """
            """is not.""")

tradeoff('How each machine reports', [
 ('Ship raw events', 'info',
  ['Perfectly exact', 'No cleverness needed at the edge'],
  ['<b>13 TB / day</b>', 'The counting system costs more than the service it measures',
   'Network becomes the bottleneck']),
 ('Ship local top-K', 'shared',
  ['Tiny payloads', 'Obvious and easy to explain'],
  ['<b>Wrong.</b> Local top-K does not merge into global top-K',
   'Error is unbounded and silent &mdash; you cannot tell it is wrong from the output']),
 ('Ship a mergeable sketch', 'ok',
  ['~400 KB / machine / minute', 'Mergeable, so it decomposes cleanly',
   'One-sided error: heavy hitters cannot be lost'],
  ['Approximate &mdash; must state the bound', 'Needs a companion heap for key identity',
   'One more concept to explain to whoever operates it']),
], 'Ship a mergeable sketch plus a bounded candidate heap. For the daily fixed window I would <b>also</b> '
   'run an exact nightly batch, because it is cheap and it makes the sketch auditable.',
 'If distinct keys were small &mdash; say under a million &mdash; I would ship exact per-machine counts '
 'and skip the sketch entirely. <b>The sketch is a response to cardinality, not to scale.</b>',
 [
 """Trade-off: how does each machine report? Shipping raw events is perfectly exact and costs thirteen """
 """terabytes a day, at which point your counting system costs more to run than the service it is """
 """measuring. That is usually enough to kill it on its own.""",
 """Shipping local top-K is tiny and obvious and wrong, for the reason we covered — and the worst part """
 """is that the error is silent. Looking at the output, you cannot tell it is wrong. Systems that are """
 """quietly wrong are worse than systems that are loudly broken.""",
 """Shipping a mergeable sketch is four hundred kilobytes per machine per minute, decomposes cleanly, """
 """and has one-sided error so heavy hitters cannot be lost. The cost is that it is approximate and you """
 """must state the bound, and that it needs a companion heap to know which keys it is talking about.""",
 """I would ship the sketch plus a bounded candidate heap — and for the daily fixed window I would also """
 """run the exact nightly batch, because it is cheap and it makes the sketch auditable. Being able to """
 """check your approximation against ground truth is worth a lot operationally.""",
 """And what would flip it: if distinct keys were small, say under a million, I would ship exact """
 """per-machine counts and skip the sketch entirely. That is the sentence I most want you to take from """
 """this lesson — the sketch is a response to cardinality, not to scale. Lots of traffic over few """
 """distinct keys needs no sketch at all.""",
])

failures('What happens when each piece dies', [
 ('One machine&rsquo;s sketch never arrives', 'Slightly low counts for that slice',
  'Counts are approximate anyway. <b>Alert on the number of reporting machines</b>, not on the counts '
  '&mdash; missing reporters is the observable symptom'),
 ('Kafka is unavailable', 'Yesterday&rsquo;s answer keeps serving',
  'Buffer sketches on the machine and drain later. Sketches are <b>tiny</b>, so an hour of buffering '
  'costs ~24 MB &mdash; buffering is genuinely free here'),
 ('Merger crashes mid-window', 'Nothing &mdash; last completed day still served',
  'Minute buckets are immutable once written, so restart and recompute from Kafka. <b>Idempotent by '
  'construction</b>'),
 ('A sketch is merged twice', 'Counts inflated for that minute',
  'Key each sketch by <code>(machine, minute)</code> and merge into a bucket <b>once</b>. '
  'At-least-once delivery makes duplicates certain'),
 ('One key is catastrophically hot (a bot)', 'It dominates the top-N, correctly',
  'The <b>product</b> problem, not a systems one: is a bot a popular query? This is why you ask about '
  'distinct-user counting up front'),
 ('Clock skew between machines', 'Events land in adjacent minute buckets',
  'Bucket by <b>ingest</b> time, not machine time, or accept ±1 minute smear. At a 24h window the '
  'error is irrelevant &mdash; say so rather than over-engineering it'),
], [
 """Failures. A machine's sketch never arrives: counts are slightly low for that slice, and since they """
 """are approximate anyway nobody notices. So alert on the number of reporting machines rather than on """
 """the counts — the missing reporter is the observable symptom, not the number.""",
 """Kafka unavailable: yesterday's answer keeps serving, and machines buffer locally. Sketches are so """
 """small that an hour of buffering is about twenty-four megabytes across the fleet. Buffering is """
 """genuinely free here, which is not true of most pipelines, and it is worth pointing out.""",
 """Merger crashes mid-window: nothing visible, because the last completed day is still being served. """
 """Minute buckets are immutable once written, so you restart and recompute from Kafka. Idempotent by """
 """construction rather than by effort.""",
 """A sketch merged twice inflates that minute. Key each sketch by machine and minute, and merge into a """
 """bucket exactly once. With at-least-once delivery, duplicates are certain, so this is required.""",
 """One key catastrophically hot — a bot — dominates the top-N, correctly. That is a product problem """
 """rather than a systems one: is a bot a popular query? And this is exactly why you ask about """
 """distinct-user counting in the first five minutes.""",
 """And clock skew puts events in adjacent minute buckets. Bucket by ingest time rather than machine """
 """time, or simply accept a one-minute smear — over a twenty-four hour window that error is """
 """irrelevant. Saying &ldquo;this does not matter at this granularity&rdquo; is as valuable as """
 """fixing it, and much cheaper.""",
])

say('What I should actually say in the room', [
 'Let me confirm the window first &mdash; you said the previous fixed 24 hours, not a rolling window. '
 'That is a big simplification and I want to make sure I am allowed to use it.',
 'Shipping raw events is 13 TB a day, so the counting system would cost more than the service. That '
 'rules it out immediately.',
 'The obvious fix is for each machine to send its local top 100, and I want to flag that it is wrong: '
 'an item ranked 101st on every machine can beat an item ranked 1st on one machine.',
 'So each machine keeps a count-min sketch plus a bounded candidate heap, and ships the sketch once a '
 'minute. Sketches are mergeable, which is the property that makes this decompose at all.',
 'That is about 400 KB per machine per minute &mdash; five orders of magnitude less than raw events.',
 'Because sketches merge, the daily answer is the sum of 1,440 minute buckets &mdash; which also gives '
 'us the rolling window later for free if the requirement changes.',
 'And since the window is fixed and daily, I would also run an exact nightly batch. It is cheap, and it '
 'lets me audit the sketch against ground truth.',
], [
 """The sentences. Open by confirming the window, because it is the biggest cost lever and confirming a """
 """given constraint shows you read the question rather than pattern-matched it.""",
 """Then kill the naive design with a number. Then — and this is the highest-value sentence in the """
 """whole lesson — raise the local top-K trap yourself, before the interviewer does. Volunteering a """
 """subtle bug in the obvious approach is one of the clearest staff signals available.""",
 """Then the sketch, the mergeability property, the size, the free rolling window as headroom, and the """
 """exact batch as an audit. Notice that last one is you choosing to be able to check your own work.""",
])

followups([
 'Exact or approximate &mdash; and how do you decide?',
 'How do you handle the time window?',
 'What if the number of distinct keys explodes?',
 'How do you partition the counting?',
 'What are the memory limits per machine?',
 'How does this work as a streaming system rather than a batch one?',
], [
 'Now make it a rolling 24h window. What changes?',
 'Top-N per country, per device type, per customer &mdash; how does the design hold up?',
 'How would you prove the sketch&rsquo;s error is within bounds in production?',
 'The top query is a bot. How do you tell popularity from abuse?',
 'What would you delete if you had to halve the cost of this system?',
],
 """The reported follow-ups are exact versus approximate, time windows, exploding cardinality, """
 """partitioning, memory limits and streaming versus batch. We have covered all of those, and the """
 """partitioning answer is worth stating crisply: partition by key hash at the merge stage, so all """
 """occurrences of a key land on one merger and its counts can be summed in one place.""",
 """The staff-level follow-ups are the interesting ones. Make it rolling, which is the sum of any """
 """1,440 consecutive buckets — and notice we already built that capability without paying for it. """
 """Top-N per country, per device, per customer, which multiplies your sketch count by the dimension """
 """cardinality and is where this design starts to strain. How you would prove the error bound holds """
 """in production, which is the exact-batch audit earning its place. Telling popularity from abuse, """
 """which is the distinct-user question again. And what you would delete to halve the cost — where the """
 """honest answer is usually the streaming path, if a daily answer was all anyone needed.""")

cheatsheet('Top-N over 24h &mdash; the one-page card', [
 ('Requirements', 'N most frequent requests over the <b>fixed previous 24h</b> across ~300 machines'),
 ('Scale', '~1.5M req/s, ~130B/day, ~500M distinct keys. Raw events would be 13 TB/day'),
 ('Core architecture', 'Local sketch + candidate heap &rarr; Kafka (1/min) &rarr; merge &rarr; minute '
                       'buckets &rarr; daily roll-up &rarr; cached query API'),
 ('Data store', 'Minute buckets of merged sketches; a small table of daily top-N results'),
 ('Partition key', 'Key hash at the merge stage, so all occurrences of a key sum in one place'),
 ('Cache', 'The answer changes once a day &mdash; cache it outright, ~100% hit rate'),
 ('Queue', 'Kafka, carrying sketches rather than events. ~120 MB/min for the whole fleet'),
 ('Consistency', 'Approximate by design, with a stated bound. One-sided: never under-counts'),
 ('Failure handling', 'Buffer locally; immutable buckets make recompute idempotent; dedupe on '
                      '(machine, minute)'),
 ('Key deep dives', 'The local top-K trap &middot; count-min sketch &middot; exact vs approximate'),
 ('Biggest trade-off', 'Exactness vs data movement. The sketch is a response to <b>cardinality</b>, '
                       'not to traffic volume'),
], [
 """The card. Requirements — and note the word fixed is doing real work. Scale: one and a half million """
 """requests a second, thirteen terabytes a day if you were foolish enough to ship them.""",
 """Architecture in one line: local sketch and candidate heap, Kafka once a minute, merge, minute """
 """buckets, daily roll-up, cached A-P-I. Partition by key hash at the merge so a key's counts sum in """
 """one place. Cache the answer outright, since it changes daily.""",
 """Consistency is approximate by design with a stated bound, and one-sided so heavy hitters survive. """
 """Failure handling leans on immutable buckets. And the biggest trade-off, which is the sentence to """
 """leave with: exactness versus data movement — and the sketch is a response to cardinality, not to """
 """traffic volume.""",
])

say('The 60-second answer', [
 'The important word in the question is &ldquo;fixed&rdquo; &mdash; the previous 24 hours, not a '
 'rolling window &mdash; which turns this from a continuous aggregation into one batch computed once '
 'and served all day.',
 'Shipping raw events centrally would be about 13 TB a day, so all the work has to happen at the edge.',
 'The obvious edge optimisation is for each machine to send its local top 100, and that is wrong: an '
 'item ranked 101st on all 300 machines can outrank an item that is 1st on one of them. Local top-K '
 'does not merge into global top-K.',
 'So each machine keeps a count-min sketch plus a bounded candidate heap, and ships the sketch every '
 'minute &mdash; about 400 KB. Sketches are mergeable, so summing them gives exactly the sketch of the '
 'union, and that is what lets the problem decompose.',
 'Merged sketches land in per-minute buckets; the daily answer is the sum of 1,440 of them, which also '
 'gives me a rolling window later at no extra cost.',
 'The sketch never under-counts, so a real heavy hitter can never be lost &mdash; and because the '
 'window is daily I would also run an exact nightly batch to audit it.',
], [
 """The sixty-second answer. It opens on the word that changes the cost of the problem, then kills the """
 """naive design with a number, then volunteers the subtle bug in the obvious fix.""",
 """That third sentence is the one that earns the interview. Practise it until it is automatic — """
 """proactively naming a trap you were not asked about is the single most efficient way to demonstrate """
 """that you have done this before.""",
], kicker='60-second interview answer')
