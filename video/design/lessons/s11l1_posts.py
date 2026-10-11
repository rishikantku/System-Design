# -*- coding: utf-8 -*-
"""Chapter 11, Lesson 1 — LinkedIn posts and comments, then analytics on top."""
from lib import *

lesson_header('11.1', 'Design LinkedIn posts and comments &mdash; then add analytics',
              'Thread-local storage &middot; hot-post counters &middot; event stream &rarr; OLAP',
              dict(reports='1 candidate report', latest='2025', level='Software engineer, onsite design round',
                   conf='MEDIUM &mdash; single report, very LinkedIn-native', sources='LeetCode Discuss'), 17,
              """Chapter eleven is new. These are system design questions that candidates reported on """
              """LeetCode Discuss with a LinkedIn tag and that the earlier chapters did not cover. Lesson """
              """one: design LinkedIn posts and comments. And then the interviewer extends it &mdash; now """
              """add analytics, so an author can see who saw their post and how it performed. The trap is """
              """that the two halves look like one system and are actually two, with completely different """
              """shapes.""")

evidence('Where this question comes from', [
 ('LeetCode Discuss &mdash; LinkedIn interview experience', '~mid 2025', 'Software engineer, onsite',
  'Round 3, design: <b>&ldquo;Design LinkedIn post and comment functionality&rdquo;</b>, later '
  '<b>extended to add analytics</b>'),
], """One report, so medium confidence. Two things make it worth a full lesson anyway. It is LinkedIn's """
   """own product, which is exactly the kind of question a product-minded interviewer reaches for.""",
 ["""And the shape &mdash; build the feature, then bolt on analytics &mdash; is a classic staff-level """
  """move. The interviewer wants to see whether you notice that the second requirement changes the """
  """write path of the first."""],
 caveat='Single report. The date is approximate, inferred from the post number.',
 narration_caveat="""Single report, and the date is approximate &mdash; I inferred it from the post """
                  """number, since the page itself could not be read directly.""")

sid = beat('Why this is interesting', 'Two systems hiding inside one question',
           '<div style="font-size:28px;line-height:1.72">'
           '<b>Posts and comments</b> are an <b>OLTP</b> problem: small writes, read by id, read a '
           'thread at a time. <span style="color:#a8e6a3">Correctness and latency matter.</span><br><br>'
           '<b>Analytics</b> is a <b>firehose</b> problem: every <i>impression</i> of every post is an '
           'event. <span style="color:#ffd483">Billions a day, aggregated, approximate is fine.</span>'
           '<br><br>'
           '<b>The trap:</b> putting a <code>view_count</code> column on the post row and incrementing '
           'it. <span style="color:#ff9a9a">A viral post turns one row into the hottest lock in the '
           'company.</span><br><br>'
           '<b>The move:</b> keep the post store small and boring; send every interaction to a stream; '
           'compute analytics somewhere built for it.</div>',
           """Why is this interesting? Because there are two systems hiding inside one question.""", step=0)
seg(sid, 1, """Posts and comments are a transactional problem. Small writes, read by identifier, and """
            """mostly read one thread at a time. Correctness and latency matter there.""")
seg(sid, 2, """Analytics is a firehose problem. Every impression of every post is an event &mdash; """
            """billions a day &mdash; and it gets aggregated, so an approximate answer is perfectly """
            """acceptable.""")
seg(sid, 3, """The trap is the obvious design: a view count column on the post row, incremented on every """
            """view. It works in the demo. Then one post goes viral and that single row becomes the """
            """hottest lock in the company.""")
seg(sid, 4, """So the move is to keep the post store small and boring, send every interaction to a """
            """stream, and compute analytics in a system built for it. If you say that early, the """
            """extension the interviewer is holding back stops being a surprise.""")

think('A post by a celebrity gets 40,000 likes in a minute. Where does the like count live, and what '
      'happens to that storage when 40,000 writes hit it?',
      20,
      """Pause. A post by someone with ten million followers gets forty thousand likes in one minute. """
      """Where does the like count live, and what happens to that storage when forty thousand writes """
      """land on it?""",
      """Hold that. We come back to it in the first deep dive.""")

clarify('What I would clarify first', [
 ('Comment nesting &mdash; flat, one level of replies, or arbitrary depth?',
  'LinkedIn shows <b>one level of replies</b>. Arbitrary depth changes storage and pagination '
  'completely &mdash; ask, do not assume.'),
 ('How are comments ordered &mdash; newest, or &ldquo;most relevant&rdquo;?',
  'Relevance means a <b>ranking step</b> and a precomputed order per post. Time order is just an index.'),
 ('Which counts must be exact?',
  'Usually <b>none in real time</b>. &ldquo;1,203 reactions&rdquo; can lag a few seconds. That one answer '
  'unlocks the whole counter design.'),
 ('Analytics for whom &mdash; the author, or internal teams?',
  'Author-facing means <b>per-post, low-latency reads</b> and privacy rules. Internal means big batch scans.'),
 ('What analytics &mdash; impressions, unique viewers, viewer demographics?',
  'Unique viewers needs <b>distinct counting</b>. Demographics needs a join with member data and '
  '<b>minimum-group thresholds</b> for privacy.'),
 ('Edits and deletes &mdash; and who can moderate?',
  'Deletes must propagate to <b>counts, notifications and analytics</b>, not just the row.'),
], [
 """Comment nesting. Flat, one level of replies, or arbitrary depth? LinkedIn shows one level of """
 """replies. Arbitrary depth changes storage and pagination completely, so ask rather than assume.""",
 """Ordering. Newest first, or most relevant? Relevance means a ranking step and a precomputed order per """
 """post. Time order is just an index.""",
 """Which counts must be exact? Usually none of them in real time &mdash; a reaction count can lag a few """
 """seconds and nobody notices. That one answer unlocks the entire counter design, so get it said.""",
 """Analytics for whom? Author-facing analytics means per-post, low-latency reads and privacy rules. """
 """Internal analytics means large batch scans. Different stores.""",
 """Which analytics? Impressions are a count. Unique viewers needs distinct counting. Viewer demographics """
 """needs a join with member data, and minimum group sizes so you never reveal an individual.""",
 """And edits and deletes. A delete has to reach the counts, the notifications and the analytics, not """
 """just the row &mdash; that is where most designs quietly leak.""",
])

capacity('Capacity', [
 ('Daily active members', 'assume ~100M', '100M DAU',
  'Assumption &mdash; state it and move on'),
 ('New posts', '~1% of DAU post daily', '&asymp; 1M posts / day',
  '&asymp; 12 / s. <b>Post writes are tiny</b>'),
 ('Comments + reactions', '~20M comments, ~200M reactions / day', '&asymp; 2.5k writes / s avg',
  'Still modest on average &mdash; <b>the problem is skew</b>, not volume'),
 ('One viral post', '40k reactions / minute', '&asymp; 670 writes / s <b>to one key</b>',
  '<b>Rules out a single counter row.</b> This is the number that matters'),
 ('Impressions (analytics)', '100M DAU &times; ~50 post views', '&asymp; 5B events / day',
  '&asymp; 60k / s avg, ~150k / s peak. <b>A stream, never the OLTP store</b>'),
 ('Impression storage, raw', '5B &times; ~100 B', '&asymp; 500 GB / day',
  'Keep raw for days; keep <b>rollups</b> for years'),
], [
 """Numbers, and I will label them as assumptions. About a hundred million daily active members.""",
 """If one percent post each day, that is a million posts a day, about twelve a second. Post writes are """
 """tiny.""",
 """Comments and reactions: say twenty million comments and two hundred million reactions a day, about """
 """two and a half thousand writes a second on average. Still modest. The problem here is skew, not """
 """volume.""",
 """Because one viral post can take forty thousand reactions in a minute. That is nearly seven hundred """
 """writes a second to one key, and it rules out a single counter row. This is the number that """
 """matters.""",
 """Impressions for analytics: a hundred million members each seeing about fifty posts is five billion """
 """events a day &mdash; sixty thousand a second on average, a hundred and fifty thousand at peak. That """
 """belongs in a stream and must never touch the transactional store.""",
 """And raw impressions at about a hundred bytes each are five hundred gigabytes a day. Keep raw for """
 """days, keep rollups for years.""",
])

A = Arch('Posts and comments, with an analytics side-car', kicker='Architecture', height=800)

A.zone(60, 120, 820, 560, 'SERVING — posts, comments, counts')
A.zone(940, 120, 840, 560, 'ANALYTICS — every interaction as an event')

A.box('cli',   100, 160, 200, 95, 'Client', 'web, mobile', kind='info', step=0, focus=0, small=True)
A.box('api',   380, 160, 220, 95, 'Post service', 'create, edit, delete', kind='ok', step=0, focus=[0, 1])
A.arrow('cli', 'api', step=0, focus=0)

A.box('pdb',   380, 330, 220, 110, 'Post store', 'sharded by post_id', kind='dp', step=1, focus=1)
A.arrow('api', 'pdb', step=1, focus=1, fs='b', ts='t')

A.box('cdb',   100, 330, 220, 110, 'Comment store', 'sharded by post_id', kind='dp', step=2, focus=2)
A.arrow('api', 'cdb', step=2, focus=2, fs='b', ts='t')

A.box('cnt',   650, 330, 200, 110, 'Counters', 'sharded per key', kind='shared', step=3, focus=3, small=True)
A.box('cache', 650, 520, 200, 100, 'Count cache', 'read path', kind='ok', step=3, focus=3, small=True)
A.arrow('cnt', 'cache', step=3, focus=3, fs='b', ts='t')

A.box('kafka', 1000, 330, 220, 110, 'Event stream', 'views, reactions, comments', kind='shared', step=4, focus=[4, 5])
A.arrow('api', 'kafka', step=4, focus=4, dashed=True, label='every interaction')

A.box('agg',   1280, 160, 220, 110, 'Stream aggregator', 'per post, per minute', kind='ok', step=5, focus=5)
A.arrow('kafka', 'agg', step=5, focus=5)
A.arrow('agg', 'cnt', step=5, focus=5, dashed=True, label='batched increments')

A.box('olap',  1280, 400, 220, 110, 'OLAP store', 'Pinot-style, per-post rollups', kind='dp', step=6, focus=6)
A.arrow('agg', 'olap', step=6, focus=6, fs='b', ts='t')
A.box('dash',  1560, 400, 180, 110, 'Author analytics', 'impressions, viewers', kind='info', step=6, focus=6, small=True)
A.arrow('olap', 'dash', step=6, focus=6)

A.box('lake',  1000, 540, 220, 100, 'Raw event lake', 'days of raw, years of rollups', kind='dp', step=7, focus=7, small=True)
A.arrow('kafka', 'lake', step=7, focus=7, fs='b', ts='t')

A.narrate(0, """The client talks to a post service that handles create, edit and delete for posts and """
             """comments.""")
A.narrate(1, """Posts live in a store sharded by post identifier. A post is small and read by id, so this """
             """is the most boring box on the screen, which is exactly what you want.""",
          A.flow([(490, 255), (490, 330)]))
A.narrate(2, """Comments are also sharded by <i>post</i> identifier, not by comment identifier. That is the """
             """key decision: a thread is always read together, so every comment for a post lives on one """
             """shard, and loading a thread is one query to one place.""",
          A.flow([(380, 220), (210, 330)]))
A.narrate(3, """Counts are separate from the post row. A counter service with sharded counters, and a cache """
             """in front of it for the read path. The post row never gets incremented.""")
A.narrate(4, """And every interaction &mdash; a view, a reaction, a comment &mdash; is also published as an """
             """event. This is the line that makes the analytics extension cheap later.""",
          A.flow([(600, 207), (1000, 385)]))
A.narrate(5, """A stream aggregator rolls events up per post per minute. It feeds the counters with """
             """batched increments &mdash; one write per post per few seconds instead of one per """
             """reaction. That is the answer to the viral post.""",
          A.flow([(1220, 385), (1280, 215)]))
A.narrate(6, """The same aggregates land in an OLAP store &mdash; Apache Pinot was built at LinkedIn for """
             """exactly this kind of member-facing analytics &mdash; and the author's analytics page reads """
             """per-post rollups from there.""",
          A.flow([(1390, 270), (1390, 400), (1560, 455)]))
A.narrate(7, """And the raw events go to a lake: days of raw for reprocessing, years of rollups for """
             """history.""")
A.build()

sid = beat('Deep dive 1', 'Counters on a viral post',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Naive:</b> <code>UPDATE posts SET likes = likes + 1</code>. '
           '<span style="color:#ff9a9a">670 writes/s on one row = lock contention, replication lag, '
           'timeouts for everyone on that shard.</span><br><br>'
           '<b>Fix 1 &mdash; store the fact, derive the count.</b> The source of truth is the '
           '<i>reaction row</i> (<code>post_id, member_id, type</code>), unique per member. '
           'That also makes reactions <b>idempotent</b>: a double-tap is the same row.<br><br>'
           '<b>Fix 2 &mdash; aggregate before you write.</b> The stream aggregator sums reactions per '
           'post every few seconds and applies <b>one</b> increment. 40,000 writes become ~20.<br><br>'
           '<b>Fix 3 &mdash; shard the hot counter.</b> Split a hot key into N sub-counters '
           '(<code>post:123#0..15</code>); writes spread, reads sum N values.<br><br>'
           '<span style="color:#a8e6a3"><b>Say why it is safe:</b> the displayed count is a cached, '
           'slightly-stale view of a truth you can always recompute from reaction rows.</span></div>',
           """Deep dive one, and the question I asked you to hold: counters on a viral post.""", step=0)
seg(sid, 1, """The naive design increments a column on the post row. At nearly seven hundred writes a """
            """second on one row you get lock contention, replication lag, and timeouts for every other """
            """post that happens to share that shard.""")
seg(sid, 2, """Fix one: store the fact and derive the count. The source of truth is the reaction row &mdash; """
            """post, member, reaction type &mdash; unique per member. As a bonus that makes reactions """
            """idempotent: a double tap writes the same row twice and still counts once.""")
seg(sid, 3, """Fix two: aggregate before you write. The stream aggregator sums reactions per post every """
            """few seconds and applies one increment. Forty thousand writes a minute become about """
            """twenty.""")
seg(sid, 4, """Fix three, for the extreme case: shard the hot counter itself. Split it into sixteen """
            """sub-counters, spread writes across them, and sum the sixteen on read.""")
seg(sid, 5, """And say why all of this is safe. The number on screen is a cached, slightly stale view of a """
            """truth you can always recompute from the reaction rows. Nothing is lost if a counter """
            """drifts &mdash; you rebuild it.""")

sid = beat('Deep dive 2', 'The analytics extension — impressions and viewers',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>When the interviewer says &ldquo;now add analytics&rdquo;</b>, the good answer is: '
           '<i>the events are already flowing &mdash; I only add consumers.</i><br><br>'
           '<b>Impressions:</b> count &ldquo;viewed&rdquo; events per post per minute; roll up to hour '
           'and day. <b>Define an impression</b> (on screen &ge; 50% for &ge; 300 ms) &mdash; or the '
           'number is meaningless.<br><br>'
           '<b>Unique viewers:</b> exact distinct counts need every member id per post. '
           '<span style="color:#a8e6a3"><b>HyperLogLog</b>: ~12 KB per post per window, ~1% error, and '
           'sketches <b>merge</b> &mdash; minute sketches union into a day.</span><br><br>'
           '<b>Demographics</b> (&ldquo;viewers by industry, seniority&rdquo;): enrich events with member '
           'attributes in the stream. <span style="color:#ffd483">Suppress any group below a minimum size '
           '&mdash; otherwise &ldquo;1 viewer from Company X&rdquo; identifies a person.</span><br><br>'
           '<b>Serving:</b> pre-aggregated rollups in an OLAP store, read by post id &mdash; '
           'milliseconds, never a scan of raw events.</div>',
           """Deep dive two: the analytics extension. When the interviewer says &ldquo;now add """
           """analytics&rdquo;, the strongest answer is that the events are already flowing and you only """
           """add consumers.""", step=0)
seg(sid, 1, """Impressions: count viewed events per post per minute and roll up to hours and days. And """
            """define what an impression is &mdash; say, at least half the post on screen for three """
            """hundred milliseconds &mdash; because otherwise the number is meaningless and different """
            """teams will compute it differently.""")
seg(sid, 2, """Unique viewers. An exact distinct count needs every member identifier per post. HyperLogLog """
            """does it in about twelve kilobytes per post per window with roughly one percent error, and """
            """the sketches merge &mdash; minute sketches union into an hour, hours into a day.""")
seg(sid, 3, """Demographics &mdash; viewers by industry or seniority &mdash; means enriching events with """
            """member attributes in the stream. And you suppress any group below a minimum size, because """
            """&ldquo;one viewer from Company X&rdquo; identifies a person. Saying that unprompted is a """
            """strong signal at LinkedIn specifically.""")
seg(sid, 4, """And serving reads pre-aggregated rollups from the OLAP store by post id &mdash; milliseconds, """
            """never a scan of raw events.""")

tradeoff('Where the like count lives', [
 ('Counter column on the post row', 'info',
  ['Simplest possible design', 'Exact, transactional'],
  ['<b>Hot row on viral posts</b>', 'Contention spills onto every post on that shard',
   'Count and content now share a failure mode']),
 ('Reaction rows + aggregated counter + cache', 'ok',
  ['Truth is the reaction row &mdash; <b>idempotent and recomputable</b>', 'Writes batched &mdash; viral posts are cheap',
   'Same stream feeds analytics'],
  ['Count lags a few seconds', 'More moving parts']),
 ('Sharded sub-counters only', 'shared',
  ['Spreads write load on hot keys'],
  ['Reads must sum N values', 'Still no source of truth if a sub-counter drifts']),
], 'Reaction rows as truth, a stream-aggregated counter for display, sub-counter sharding only for the hottest '
   'keys.',
 'If a count had to be exact and transactional &mdash; a poll closing at a deadline, a paid action &mdash; I '
 'would count from the fact rows synchronously for that feature and accept the cost.',
 [
 """Trade-off: where does the like count live? A counter column on the post row is the simplest design and """
 """it is exact, but it creates a hot row on every viral post, the contention spills onto other posts on the """
 """same shard, and content and counts now share a failure mode.""",
 """Reaction rows as truth with an aggregated counter and a cache: the truth is idempotent and """
 """recomputable, writes are batched so viral posts are cheap, and the same stream feeds analytics. The """
 """cost is a few seconds of lag and more moving parts.""",
 """Sharded sub-counters alone spread the write load but make reads sum several values, and still leave """
 """you without a source of truth if a counter drifts.""",
 """I would take reaction rows as truth, a stream-aggregated counter for display, and sub-counter """
 """sharding only for the very hottest keys.""",
 """And what would flip it: if a count had to be exact and transactional &mdash; a poll that closes at a """
 """deadline, or anything involving money &mdash; I would count synchronously from the fact rows for that """
 """one feature and pay for it.""",
])

failures('What happens when each piece dies', [
 ('Comment-store shard is down', 'Threads on that shard fail to load',
  'Posts still render. <b>Degrade the comment section</b>, never the post. Shard by post_id keeps the blast '
  'radius to whole threads, not random comments'),
 ('Event stream lags', 'Counts and analytics fall behind',
  '<b>Posting is unaffected.</b> Alert on consumer lag; counts catch up when the lag clears'),
 ('Aggregator crashes mid-window', 'A window is lost or double-counted',
  'Commit offsets <b>with</b> the aggregate (exactly-once sink), or make increments idempotent per '
  '(post, window)'),
 ('A post is deleted', 'Counts, notifications and analytics still reference it',
  'Publish a <b>delete event</b>; every consumer handles it. A tombstone, not a silent row removal'),
 ('Counter drifts from truth', 'Displayed count is wrong',
  '<b>Periodic reconciliation</b> from reaction rows for active posts. Drift is a bug signal, not a disaster'),
 ('Bot floods reactions on one post', 'Inflated counts, hot key',
  'Rate-limit per member (lesson 4.1); unique (post, member) constraint caps it at one reaction each'),
], [
 """Failures. A comment shard going down means threads on that shard fail to load. Posts still render, so """
 """degrade the comment section, never the post. And because comments are sharded by post, the blast """
 """radius is whole threads rather than random missing comments, which is much easier to explain to a """
 """user.""",
 """The event stream lagging means counts and analytics fall behind while posting carries on unaffected. """
 """Alert on consumer lag, and it catches up on its own.""",
 """The aggregator crashing mid-window can lose or double-count a window. Commit offsets together with """
 """the aggregate, or make the increment idempotent per post and window.""",
 """A deleted post is still referenced by counts, notifications and analytics. Publish a delete event and """
 """make every consumer handle it &mdash; a tombstone, not a silent row removal.""",
 """A counter drifting from the truth is fixed by periodic reconciliation from reaction rows for active """
 """posts. Drift is a bug signal, not a disaster, because the truth is intact.""",
 """And a bot flooding reactions is capped by the unique constraint &mdash; one reaction per member per """
 """post &mdash; plus per-member rate limiting from lesson four point one.""",
])

say('What I should actually say in the room', [
 'There are two systems here: a small transactional one for posts and comments, and a firehose for '
 'interactions. I will keep them apart from the start.',
 'Comments are sharded by post id, not comment id, because a thread is always read together &mdash; one '
 'query to one shard.',
 'The like count is not a column on the post. Reaction rows are the truth, unique per member, which also '
 'makes them idempotent; the displayed count is aggregated from a stream and cached.',
 'That matters for viral posts: 40,000 reactions a minute become a few batched increments instead of a hot '
 'row.',
 'Every interaction is published as an event, so when you ask for analytics I only add consumers: '
 'impressions as rollups, unique viewers with HyperLogLog, demographics with a minimum group size.',
 'Author analytics reads pre-aggregated rollups from an OLAP store by post id, never raw events.',
], [
 """The sentences. Open by naming the two systems, because that is the insight the extension is testing.""",
 """Then the comment sharding key with its reason, the counter design, and the viral-post arithmetic.""",
 """Then the line that makes the extension trivial &mdash; the events are already flowing &mdash; and the """
 """three analytics answers, ending on the privacy threshold.""",
])

followups([
 'Design post and comment functionality',
 'Extend it to add analytics',
], [
 'How do you paginate a thread with 50,000 comments, newest and &ldquo;most relevant&rdquo;?',
 'A post is edited after 10,000 comments. What do readers see?',
 'How do you show &ldquo;3 of your connections reacted&rdquo;?',
 'Unique viewers must be exact for a paid feature. What changes?',
 'How do you backfill analytics after fixing a bug in the impression definition?',
],
 """The reported shape is two prompts: build it, then extend it. The extension is the test, and the """
 """answer is that a well-shaped write path makes it a consumer, not a redesign.""",
 """The staff follow-ups go deeper. Pagination uses a cursor, not an offset &mdash; an index on post and """
 """time for newest, and a precomputed ranked list per post for relevance, refreshed as engagement """
 """changes. Edits keep a version and show &ldquo;edited&rdquo;; comments stay attached to the post, not """
 """the version. &ldquo;Three of your connections reacted&rdquo; is an intersection of the viewer's """
 """connection set with the reactors &mdash; done at read time against a small set, or precomputed for """
 """high-fan-out posts. Exact unique viewers for a paid feature means storing the member set per post, """
 """which is affordable for the posts that pay. And backfill is why raw events are kept: replay the lake """
 """through the corrected job and swap the rollups.""")

cheatsheet('Posts, comments and analytics — the one-page card', [
 ('Requirements', 'Create/edit/delete posts and comments, reactions with counts; then author analytics'),
 ('Scale', '~1M posts/day, ~2.5k interaction writes/s avg; <b>670/s on one viral post</b>; ~5B impressions/day'),
 ('Core architecture', 'Post + comment stores &rarr; counters + cache; every interaction &rarr; event stream '
                       '&rarr; aggregator &rarr; OLAP'),
 ('Data store', 'Posts by post_id; <b>comments by post_id</b>; reaction rows unique per (post, member)'),
 ('Partition key', 'post_id &mdash; a thread is read together'),
 ('Cache', 'Counts and hot threads; counts are a derived, rebuildable view'),
 ('Queue', 'Interaction stream; it is what makes analytics an add-on'),
 ('Consistency', 'Posts and comments read-your-writes; <b>counts eventually consistent</b>'),
 ('Failure handling', 'Degrade comments not posts; delete events to every consumer; reconcile counters'),
 ('Key deep dives', 'Viral-post counters &middot; impressions, HyperLogLog, privacy thresholds'),
 ('Biggest trade-off', 'Exact counts vs hot rows &mdash; <b>store facts, derive counts</b>'),
], [
 """The card. The scale row carries the viral-post number, which drives the counter design.""",
 """Partition key is post id for comments, because a thread is read together. Counts are a derived, """
 """rebuildable view.""",
 """And the biggest trade-off in four words: store facts, derive counts.""",
])

say('The 60-second answer', [
 'I see two systems: a small transactional store for posts and comments, and a stream of interactions '
 'that drives counts and analytics.',
 'Comments are sharded by post id so a thread is one query on one shard, with a cursor for pagination.',
 'Counts are not columns. Reaction rows unique per member are the truth; a stream aggregator applies '
 'batched increments to a counter that is cached for reads. A viral post becomes a few writes a second, '
 'not hundreds.',
 'For analytics, every view, reaction and comment is already an event. I add consumers: impression '
 'rollups per minute, hour and day; unique viewers with mergeable HyperLogLog sketches; demographics '
 'enriched in the stream with a minimum group size so no individual is exposed.',
 'Authors read pre-aggregated rollups from an OLAP store &mdash; Pinot-style &mdash; in milliseconds, '
 'and raw events stay in a lake so I can backfill when a definition changes.',
], [
 """The sixty-second answer. The opening sentence &mdash; two systems &mdash; is the move that """
 """separates this from a CRUD answer.""",
 """And the privacy threshold on demographics is the detail that shows you know whose product this is.""",
], kicker='60-second interview answer')
