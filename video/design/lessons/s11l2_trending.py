# -*- coding: utf-8 -*-
"""Chapter 11, Lesson 2 — trending articles (and the Top-K videos variant)."""
from lib import *

lesson_header('11.2', 'Design trending articles on LinkedIn &mdash; and Top-K videos',
              'Velocity not volume &middot; windowed counts &middot; decay &middot; anti-gaming',
              dict(reports='2 candidate reports', latest='2026', level='Staff (offer) and SDE 2',
                   conf='HIGH &mdash; two independent reports, one at Staff', sources='LeetCode Discuss'), 17,
              """Lesson two of the new chapter, and the strongest evidence in it. Design trending """
              """articles on LinkedIn: an API is continuously writing shared article identifiers to a """
              """database, and you need to surface what is trending. A second candidate got a close """
              """cousin &mdash; Top-K YouTube videos. Lesson four point three already taught you how to """
              """count the top N. This lesson is about why &ldquo;trending&rdquo; is a different """
              """question from &ldquo;most popular&rdquo;.""")

evidence('Where this question comes from', [
 ('LeetCode Discuss &mdash; LinkedIn Staff SWE, with offer', 'Jun 2025', 'Staff',
  '<b>&ldquo;Design trending articles on LinkedIn&rdquo;</b> &mdash; APIs write shared article URNs to the '
  'DB continuously'),
 ('LeetCode Discuss &mdash; LinkedIn SDE 2 experience', '~early 2026', 'SDE 2',
  'R3 design: <b>a variation of Top-K YouTube</b>; requirements, estimation, entities, HLD, deep dives'),
], """Two independent reports, one of them a Staff candidate who got the offer, so high confidence that """
   """this family is in the pool.""",
 ["""And notice the Staff version's framing: the shares are already being written to a database. That """
  """is a deliberate detail. The interviewer is checking whether you will run a GROUP BY on the """
  """production table."""],
 caveat='Dates for the second report are approximate, inferred from the post number.',
 narration_caveat="""The second report's date is approximate &mdash; I inferred it from the post number.""")

sid = beat('Why this is interesting', '&ldquo;Trending&rdquo; is not &ldquo;most shared&rdquo;',
           '<div style="font-size:28px;line-height:1.72">'
           '<b>Most shared in 24 h</b> is lesson 4.3: count, rank, done. '
           '<span style="color:#ffd483">It returns the same evergreen articles every day.</span><br><br>'
           '<b>Trending</b> means <i>unusually</i> popular <i>right now</i>:<br>'
           '&bull; an article with 2,000 shares in the last hour that normally gets 20 is trending<br>'
           '&bull; an article with 50,000 shares a day, every day, is <b>not</b><br><br>'
           '<b>So trending = velocity relative to a baseline, with decay.</b><br><br>'
           '<span style="color:#ff9a9a">And the given detail &mdash; &ldquo;APIs write shares to the '
           'DB&rdquo; &mdash; is bait. Never compute this with a query on the OLTP table.</span><br><br>'
           '<span style="color:#a8e6a3">Capture the writes as a stream (CDC or a publish on write), count in '
           'windows, score, serve from a cache.</span></div>',
           """Why is this interesting? Because trending is not the same as most shared.""", step=0)
seg(sid, 1, """Most shared in the last twenty-four hours is lesson four point three: count, rank, done. """
            """And it returns the same evergreen articles every single day, which is useless as a """
            """trending surface.""")
seg(sid, 2, """Trending means unusually popular right now. An article with two thousand shares in the last """
            """hour that normally gets twenty is trending. An article with fifty thousand shares a day, every """
            """day, is not.""")
seg(sid, 3, """So trending is velocity relative to a baseline, with decay. That sentence is the whole """
            """question.""")
seg(sid, 4, """And the detail in the prompt &mdash; APIs write shares to the database &mdash; is bait. """
            """Computing this with a query on the production table is the answer the interviewer is """
            """waiting for you not to give.""")
seg(sid, 5, """Instead: capture the writes as a stream, count in time windows, score against a baseline, """
            """and serve a precomputed list from a cache.""")

think('Article A: 50,000 shares yesterday, 52,000 today. Article B: 30 shares yesterday, 3,000 in the last '
      'hour. Which one is trending, and what number did you compute to decide?',
      20,
      """Pause. Article A had fifty thousand shares yesterday and fifty-two thousand today. Article B had """
      """thirty yesterday and three thousand in the last hour. Which is trending, and what number did you """
      """actually compute to decide?""",
      """Hold that number. It is the scoring function in deep dive one.""")

clarify('What I would clarify first', [
 ('Trending over what horizon &mdash; last hour, today, this week?',
  'Shorter horizons need <b>finer buckets</b> and react faster to spikes. Usually several horizons at once.'),
 ('Global, or per segment &mdash; region, industry, my network?',
  'Per segment multiplies the state by the segment count. <b>Personalised</b> trending is a ranking problem, '
  'not a counting one.'),
 ('How fresh must the list be?',
  'A list recomputed every <b>minute</b> is far cheaper than per-request scoring, and nobody can tell.'),
 ('What counts as a signal &mdash; shares only, or views, reactions, comments?',
  'Weighted signals need a <b>scoring model</b>; share-only keeps it a count.'),
 ('How adversarial is it?',
  'Trending is a <b>target</b>. If yes: unique sharers, account-age weighting, spam filtering before counting.'),
 ('For Top-K videos: which windows &mdash; 1 h, 24 h, 7 d, all-time?',
  'Each window is a separate rollup. All-time is a running total; the others need <b>expiring buckets</b>.'),
], [
 """Over what horizon &mdash; the last hour, today, this week? Shorter horizons need finer buckets and """
 """react faster. Usually you want several at once.""",
 """Global, or per segment &mdash; per region, per industry, per network? Segments multiply the state. And """
 """personalised trending is a ranking problem, not a counting problem.""",
 """How fresh? A list recomputed every minute is far cheaper than scoring per request, and no member can """
 """tell the difference.""",
 """Which signals? Shares only keeps this a count. Weighted shares, views and reactions need a scoring """
 """model.""",
 """How adversarial is it? Trending is a target. If the answer is yes, count unique sharers and filter """
 """spam before counting, not after.""",
 """And for the Top-K videos variant: which windows? Each window is its own rollup. All-time is a running """
 """total; the others need buckets that expire.""",
])

capacity('Capacity', [
 ('Share events', 'assume ~50M shares / day', '&asymp; 600 / s avg, ~2k / s peak',
  'Small stream. <b>Counting is not the hard part</b>'),
 ('Distinct articles in a day', 'long tail', '&asymp; 10M URNs',
  'Most get 1&ndash;2 shares. <b>Only the head matters</b>'),
 ('Exact per-article minute buckets, 24 h', '10M &times; 1,440 &times; 8 B', '&asymp; 115 GB',
  'Too much for the tail. <b>Keep fine buckets only for candidates</b>'),
 ('Count-min sketch for the tail', 'e.g. 4 &times; 2M counters &times; 4 B', '&asymp; 32 MB',
  '<b>Fits in memory</b>; overestimates slightly, never under'),
 ('Candidates with exact buckets', 'top ~100k by recent count', '&asymp; 1 GB',
  'Exact counts where ranking actually happens'),
 ('Serving reads', 'trending module on feed / home', '&asymp; 100k reads / s',
  'A <b>precomputed list in a cache</b>, refreshed each minute. Reads never compute'),
], [
 """Numbers, as assumptions. Fifty million shares a day is about six hundred a second, two thousand at """
 """peak. A small stream. Counting is not the hard part.""",
 """Distinct articles: around ten million in a day, and most of them get one or two shares. Only the head """
 """matters.""",
 """Exact minute buckets for every article for a day would be over a hundred gigabytes, which is wasted """
 """on the tail.""",
 """A count-min sketch for the tail is a few tens of megabytes and fits in memory. It overestimates """
 """slightly and never underestimates, which is the safe direction for finding candidates.""",
 """Then exact minute buckets only for the top hundred thousand candidates &mdash; about a gigabyte, and """
 """exact where ranking actually happens.""",
 """And reads: the trending module is everywhere, maybe a hundred thousand reads a second. That must be """
 """a precomputed list in a cache, refreshed every minute. Reads never compute anything.""",
])

A = Arch('Trending &mdash; stream the writes, score velocity, serve a list', kicker='Architecture', height=800)

A.zone(60, 120, 520, 560, 'CAPTURE — never query the OLTP table')
A.zone(640, 120, 680, 560, 'COUNT + SCORE — every minute')
A.zone(1380, 120, 400, 560, 'SERVE')

A.box('api',   100, 160, 200, 95, 'Share API', 'writes share rows', kind='info', step=0, focus=0, small=True)
A.box('db',    100, 330, 200, 110, 'Shares DB', 'OLTP, source of truth', kind='dp', step=0, focus=0)
A.arrow('api', 'db', step=0, focus=0, fs='b', ts='t')
A.box('cdc',   340, 330, 200, 110, 'CDC / outbox', 'change stream', kind='shared', step=1, focus=1)
A.arrow('db', 'cdc', step=1, focus=1)
A.box('kafka', 340, 520, 200, 100, 'Share topic', 'by article URN', kind='shared', step=1, focus=[1, 2], small=True)
A.arrow('cdc', 'kafka', step=1, focus=1, fs='b', ts='t')

A.box('filt',  690, 520, 220, 100, 'Spam + dedup', 'unique sharers', kind='bad', step=2, focus=2, small=True)
A.arrow('kafka', 'filt', step=2, focus=2)
A.box('cnt',   690, 300, 220, 120, 'Windowed counters', 'sketch for tail, minute buckets for head', kind='ok', step=3, focus=3)
A.arrow('filt', 'cnt', step=3, focus=3, fs='t', ts='b')
A.box('base',  1000, 160, 260, 100, 'Baseline store', 'expected rate per article / topic', kind='dp', step=4, focus=4, small=True)
A.box('score', 1000, 330, 260, 120, 'Scorer', 'velocity vs baseline, decayed', kind='ok', step=4, focus=[4, 5])
A.arrow('cnt', 'score', step=4, focus=4)
A.arrow('base', 'score', step=4, focus=4, fs='b', ts='t')

A.box('list',  1420, 330, 320, 120, 'Trending lists', 'global, per region, per industry', kind='ok', step=5, focus=[5, 6])
A.arrow('score', 'list', step=5, focus=5, label='top-K each minute')
A.box('read',  1420, 540, 320, 100, 'Feed / home module', 'reads the cached list', kind='info', step=6, focus=6, small=True)
A.arrow('list', 'read', step=6, focus=6, fs='b', ts='t')

A.narrate(0, """The prompt gives us this part: a share API writing share rows to a database. That database """
             """is the source of truth, and it is serving production traffic.""")
A.narrate(1, """So we capture changes rather than querying it: change data capture off the database's log, or """
             """an outbox written in the same transaction. Either way, a share topic keyed by article """
             """identifier, and the production table never sees an analytical query.""",
          A.flow([(300, 385), (340, 385), (440, 440), (440, 520)]))
A.narrate(2, """Before counting, filter. Drop obvious spam, and count unique sharers per article rather """
             """than raw shares, so one account sharing a link a thousand times counts once.""",
          A.flow([(540, 570), (690, 570)]))
A.narrate(3, """Windowed counters. A count-min sketch across the whole long tail, and exact minute buckets """
             """only for the candidates near the top.""")
A.narrate(4, """The scorer compares each candidate's recent rate against its baseline &mdash; its own """
             """history, or its topic's normal rate for a new article &mdash; and applies decay.""",
          A.flow([(910, 360), (1000, 390)]))
A.narrate(5, """Every minute it emits top-K lists: global, per region, per industry. Segments are just more """
             """lists from the same counts.""",
          A.flow([(1260, 390), (1420, 390)]))
A.narrate(6, """And the feed reads the cached list. A hundred thousand reads a second cost nothing, because """
             """nothing is computed at read time.""")
A.build()

sid = beat('Deep dive 1', 'The scoring function &mdash; velocity, baseline, decay',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Raw count</b> picks article A (52,000). <span style="color:#ff9a9a">Wrong &mdash; it is '
           'evergreen.</span><br><br>'
           '<b>Velocity ratio:</b> <code>rate_last_hour / (baseline_rate + &alpha;)</code><br>'
           '&bull; A: 2,170/h &divide; 2,080/h &asymp; <b>1.0</b> &mdash; normal<br>'
           '&bull; B: 3,000/h &divide; (1.25/h + &alpha;) &asymp; <b>huge</b> &mdash; trending<br>'
           '&bull; <b>&alpha; is a smoothing prior</b>, so an article going from 0 to 3 shares does not top the '
           'chart<br><br>'
           '<b>Better: a z-score</b> &mdash; (observed &minus; expected) / &radic;expected. Treats counts as '
           'Poisson; rewards surprise that is <i>statistically</i> large.<br><br>'
           '<b>Decay:</b> keep an exponentially decayed count, '
           '<code>score = score &times; e<sup>&minus;&Delta;t/&tau;</sup> + new</code> &mdash; one number per '
           'article, no windows to store. <span style="color:#a8e6a3">&tau; (half-life) is the knob: 1 h for '
           'breaking news, 1 day for a weekly digest.</span><br><br>'
           '<b>New articles have no baseline</b> &mdash; use the topic&rsquo;s or publisher&rsquo;s baseline.</div>',
           """Deep dive one: the scoring function, and the answer to the pause. Raw count picks article A, at """
           """fifty-two thousand. That is wrong &mdash; A is evergreen.""", step=0)
seg(sid, 1, """The velocity ratio fixes it: the last hour's rate divided by the baseline rate plus a """
            """smoothing term. A comes out at about one &mdash; perfectly normal. B comes out enormous. And the """
            """smoothing term matters: without it, an article going from zero shares to three divides by """
            """nearly zero and tops the chart.""")
seg(sid, 2, """Better still is a z-score: observed minus expected, over the square root of expected. It """
            """treats counts as Poisson and rewards surprise that is statistically large rather than just """
            """proportionally large.""")
seg(sid, 3, """For decay, keep an exponentially decayed count per article: multiply by e to the minus elapsed """
            """time over tau, then add the new shares. One number per article and no windows to store. The """
            """half-life is the product knob &mdash; an hour for breaking news, a day for a weekly digest.""")
seg(sid, 4, """And new articles have no baseline of their own, so they borrow the topic's or the """
            """publisher's. That is the cold-start answer, and it is worth saying before you are asked.""")

sid = beat('Deep dive 2', 'Windows, the Top-K videos variant, and anti-gaming',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Multiple windows (1 h, 24 h, 7 d, all-time) from one stream:</b><br>'
           '&bull; Minute buckets roll up into hour buckets, hours into days &mdash; a <b>ring of buckets</b> per '
           'candidate; the window sum is a subtraction, not a rescan<br>'
           '&bull; All-time is a plain running total<br>'
           '&bull; Each window&rsquo;s top-K is recomputed on its own cadence: 1 h every minute, 7 d every '
           '10 minutes<br><br>'
           '<b>Merging across partitions:</b> each partition keeps its local top-K\' (K\' &gt; K, e.g. 10&times;); '
           'a merger takes the union and re-ranks. <span style="color:#ffd483">Local top-K is not globally '
           'correct unless the key is partitioned &mdash; partition by article URN and it is exact.</span>'
           '<br><br>'
           '<b>Anti-gaming &mdash; trending is a target:</b><br>'
           '&bull; Count <b>unique sharers</b>, weight by account age and reputation<br>'
           '&bull; Detect <b>coordinated bursts</b> (many new accounts, same minute)<br>'
           '&bull; <span style="color:#a8e6a3">Hold a newly-spiking item for one or two cycles before it can '
           'enter the list &mdash; cheap, and kills most single-burst attacks</span></div>',
           """Deep dive two: windows, the Top-K videos variant, and gaming.""", step=0)
seg(sid, 1, """For several windows from one stream, keep a ring of buckets per candidate: minutes roll into """
            """hours, hours into days, and a window's sum is maintained by adding the new bucket and """
            """subtracting the one that expired &mdash; never a rescan. All-time is just a running total. """
            """Each window's top-K is recomputed on its own cadence.""")
seg(sid, 2, """Merging across partitions: if you partition by article identifier, every article's count """
            """lives on exactly one partition, so each partition's local top-K is exact for its articles, and """
            """a merger takes the union and re-ranks. If you did not partition by the key, local top-K is not """
            """globally correct, and that is a classic mistake worth naming.""")
seg(sid, 3, """And anti-gaming, because trending is a target. Count unique sharers weighted by account age """
            """and reputation, detect coordinated bursts from many new accounts in the same minute, and hold a """
            """newly spiking item for a cycle or two before it can enter the list. That last one is cheap and """
            """kills most single-burst attacks.""")

tradeoff('How to compute trending', [
 ('Query the shares table on demand', 'info',
  ['No new infrastructure', 'Always exact'],
  ['<b>Analytical load on the production DB</b>', 'Rescans every time', 'Cannot meet read volume']),
 ('Stream, windowed counts, decayed score, cached list', 'ok',
  ['<b>Production DB untouched</b> (CDC)', 'Score computed once a minute', 'Reads are free'],
  ['Minute-level staleness', 'A streaming job to operate']),
 ('Batch job every hour over the lake', 'shared',
  ['Simple, cheap, easy to backfill'],
  ['<b>An hour late &mdash; trending is over</b> by the time it shows']),
], 'Stream from CDC, keep windowed and decayed counts, score against a baseline, publish lists each minute.',
 'If the product were a weekly digest rather than a live module, the hourly batch is cheaper and entirely '
 'adequate &mdash; freshness is the only thing the stream buys.',
 [
 """Trade-off: how to compute trending. Querying the shares table on demand needs no new infrastructure and is """
 """exact, but it puts analytical load on the production database, rescans every time, and cannot meet the """
 """read volume.""",
 """A stream with windowed counts, a decayed score and a cached list leaves the production database untouched, """
 """computes the score once a minute, and makes reads free. The cost is a minute of staleness and a streaming """
 """job to run.""",
 """An hourly batch over the lake is simple, cheap and easy to backfill &mdash; and an hour late, by which time """
 """the trend is over.""",
 """I would stream from change data capture, keep windowed decayed counts, and publish lists each minute.""",
 """What would flip it: if the product were a weekly digest, the batch job is cheaper and entirely adequate. """
 """Freshness is the only thing the stream buys you, so only pay for it when freshness is the product.""",
])

failures('What happens when each piece dies', [
 ('Streaming job falls behind', 'Trending list goes stale',
  'Serve the last good list with its <b>age</b>; alert on lag. A stale list is fine, an empty one is not'),
 ('Counter state lost on restart', 'Windows reset to zero',
  'Checkpoint state; rebuild windows by <b>replaying the topic</b> from the window start'),
 ('CDC connector stops', 'Silent: no new shares counted',
  'Alert on <b>zero throughput</b> as well as on errors &mdash; silence is the failure mode'),
 ('Coordinated spam burst', 'Junk article trends',
  'Unique-sharer counting, burst detection, one-cycle hold, and a <b>manual takedown</b> path'),
 ('Hot article overloads one partition', 'One counter shard lags',
  'The stream is small (~2k/s); pre-aggregate per producer before the shuffle if needed'),
], [
 """Failures. The streaming job falling behind makes the list stale. Serve the last good list with its age and """
 """alert on lag &mdash; a stale list is fine, an empty module is not.""",
 """Counter state lost on restart resets the windows. Checkpoint it, and rebuild by replaying the topic from the """
 """window start, which is why retention on the topic must cover the longest window you serve from it.""",
 """The change-capture connector stopping is silent &mdash; no errors, just no shares. Alert on zero throughput, """
 """not only on errors.""",
 """A coordinated spam burst gets handled by unique-sharer counting, burst detection, the one-cycle hold, and a """
 """manual takedown path for whatever gets through.""",
 """And a hot article on one partition is rarely a real problem at two thousand events a second, but if it is, """
 """pre-aggregate per producer before the shuffle.""",
])

say('What I should actually say in the room', [
 'Trending is not most-shared. Most-shared returns the same evergreen articles every day. Trending is '
 'velocity relative to a baseline, with decay.',
 'The shares are in a production database, so I will not query it. I capture changes with CDC or an outbox '
 'into a topic keyed by article URN.',
 'I count unique sharers in windowed counters: a count-min sketch for the long tail, exact minute buckets '
 'for the candidates at the head.',
 'The score is a z-score of the recent rate against the article&rsquo;s baseline, or its topic&rsquo;s for a '
 'new article, on an exponentially decayed count. The half-life is the product knob.',
 'Every minute I publish top-K lists &mdash; global and per segment &mdash; to a cache, so reads never '
 'compute.',
 'For Top-K videos the same machinery gives every window: buckets roll up, and each window is a running sum.',
], [
 """The sentences. Open with the distinction between trending and most-shared, because it reframes the whole """
 """question.""",
 """Then refuse to query the production table, and say how you capture it instead.""",
 """Then counts, the scoring function with its baseline and half-life, and the cached list. Close by showing """
 """the same machinery answers the Top-K videos variant.""",
])

followups([
 'Design trending articles from shared article URNs written to the DB',
 'Design Top-K videos (YouTube variant)',
], [
 'How do you make trending personal &mdash; trending in my network?',
 'An article trends for the wrong reason. How do you take it down in under a minute?',
 'How do you test that the scoring function is any good?',
 'Count-min sketch overestimates. Can it put the wrong item in the top K?',
 'How do you backfill after the CDC connector was down for two hours?',
],
 """The reported prompts are the two framings: trending from shares in a database, and Top-K videos. Both are """
 """answered by the same pipeline with different windows.""",
 """The staff follow-ups. Personal trending is a re-ranking of global and segment candidates using the """
 """viewer's network &mdash; you do not count per member. Takedown is a deny-list applied at publish and at """
 """read, which is lesson four point four. Testing the score means replaying past days and checking it """
 """surfaced known breaking stories early and evergreen ones never. Count-min can promote a tail item into """
 """the candidate set, but exact buckets for candidates mean it cannot win the final ranking on an inflated """
 """count. And backfill is a replay of the topic, or the database log, through the same job.""")

cheatsheet('Trending — the one-page card', [
 ('Requirements', 'Surface articles that are unusually popular right now; global and per segment'),
 ('Scale', '~50M shares/day (~2k/s peak), ~10M distinct URNs/day, ~100k reads/s'),
 ('Core architecture', 'CDC from shares DB &rarr; topic by URN &rarr; spam/dedup &rarr; windowed counters '
                       '&rarr; scorer &rarr; cached top-K lists'),
 ('Data store', 'Shares DB (truth); count-min sketch + minute buckets; baseline store; list cache'),
 ('Partition key', 'Article URN &mdash; makes local top-K exact'),
 ('Cache', 'Precomputed lists per segment, refreshed each minute'),
 ('Queue', 'Share topic from CDC; retention &ge; longest window'),
 ('Consistency', 'Minute-level staleness, by design'),
 ('Failure handling', 'Serve last good list with age; replay to rebuild; alert on zero throughput'),
 ('Key deep dives', 'Velocity vs baseline, z-score, decay &middot; windows, merging, anti-gaming'),
 ('Biggest trade-off', 'Freshness vs cost &mdash; <b>trending = velocity, not volume</b>'),
], [
 """The card. The architecture row starts at change data capture, which is the answer to the bait in the """
 """prompt.""",
 """The partition key row explains why local top-K is exact.""",
 """And the biggest trade-off line carries the one sentence to remember: trending is velocity, not volume.""",
])

say('The 60-second answer', [
 'Trending is velocity relative to a baseline, not raw volume &mdash; otherwise the same evergreen articles '
 'win every day.',
 'Shares are written to a production database, so I capture them with CDC into a topic keyed by article '
 'URN rather than querying the table.',
 'After spam filtering and unique-sharer dedup, I keep a count-min sketch for the long tail and exact minute '
 'buckets for the candidates near the top.',
 'Each minute the scorer computes a z-score of recent rate against the article&rsquo;s baseline &mdash; or '
 'its topic&rsquo;s for a new article &mdash; on an exponentially decayed count, and publishes top-K lists '
 'globally and per region and industry into a cache.',
 'Reads never compute. The same buckets give the Top-K videos variant every window from one stream, and '
 'partitioning by URN makes the per-partition top-K exact before the merge.',
], [
 """The sixty-second answer. The first sentence earns the most credit, because it shows you know what the """
 """product actually wants.""",
 """And the CDC sentence answers the trap in the prompt before the interviewer has to spring it.""",
], kicker='60-second interview answer')
