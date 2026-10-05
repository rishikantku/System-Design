# -*- coding: utf-8 -*-
"""Chapter 7, Lesson 1 — the LinkedIn news feed."""
from lib import *

lesson_header('7.1', 'Design the LinkedIn news feed',
              'Fanout on write vs read &middot; the hybrid &middot; the celebrity problem',
              dict(reports='InterviewTV list, and recurring via aggregators', latest='2026',
                   level='Staff', conf='MEDIUM-HIGH &mdash; corroborated',
                   sources='InterviewTV.io + research pass 3'), 18,
              """Chapter seven, lesson one: the LinkedIn news feed. This is the most-asked system design """
              """question in the industry, which cuts both ways &mdash; the interviewer has heard the """
              """textbook answer two hundred times, so reciting fanout-on-write earns you very little. """
              """What earns marks is the arithmetic that decides between the options, and the celebrity """
              """case, which is where the textbook answer actually breaks.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  'Named: <b>fanout-on-write, fanout-on-read, hybrid, ranking, celebrity/high-follower users, '
  'caching, partitioning, timeline storage, real-time updates, personalisation</b>'),
 ('Research pass 3', '2026', 'Staff',
  '&ldquo;Design LinkedIn&rsquo;s news feed&rdquo; appears via aggregators &mdash; recurring but '
  'not first-hand'),
], """Two sources, so medium-high. And the follow-up list is unusually complete &mdash; it names both """
     """fanout strategies, the hybrid, and the celebrity problem explicitly.""",
 ["""Which tells you the interviewer is not testing whether you know what fanout is. They are testing """
  """whether you can choose between the two with a number, and whether you know what breaks the """
  """choice. That is a different conversation, and much shorter."""],
 caveat='Corroborated but not first-hand. It is also the most-prepared question in the industry, so '
        'differentiation comes from the trade-offs, not the components.',
 narration_caveat="""Corroborated but not first-hand. And it is the most-prepared question in the """
                  """industry, so your differentiation comes from the trade-offs, not from naming the """
                  """components.""")

sid = beat('Why this is interesting', 'One decision, and it is decided by arithmetic',
           '<div style="font-size:28px;line-height:1.72">'
           'The whole question reduces to: <b>when do you do the work?</b><br><br>'
           '&bull; <b>Fanout on write</b> &mdash; when I post, push it into every follower&rsquo;s '
           'timeline. <span style="color:#a8e6a3">Reads are a single lookup.</span> '
           '<span style="color:#ff9a9a">A post by someone with 1M followers is 1M writes.</span><br>'
           '&bull; <b>Fanout on read</b> &mdash; when you open the app, go and fetch from everyone you '
           'follow. <span style="color:#a8e6a3">Writes are trivial.</span> '
           '<span style="color:#ff9a9a">Every read is a scatter-gather over hundreds of '
           'sources.</span><br><br>'
           '<b>The arithmetic decides it, and for LinkedIn it is lopsided:</b><br>'
           'Reads outnumber writes by roughly <b>100:1</b>. So do the work on the rarer operation '
           '&mdash; write.<br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: &ldquo;precompute vs compute on demand&rdquo; '
           'is decided by the read/write ratio, and almost nothing else. Say the ratio out loud and the '
           'decision makes itself.</span><br><br>'
           '<span style="color:#a8e6a3">Then: the hybrid exists because one input &mdash; the celebrity '
           '&mdash; breaks the chosen answer.</span></div>',
           """Why is this interesting? Because the whole question reduces to one decision: when do you """
           """do the work?""", step=0)
seg(sid, 1, """Fanout on write means that when I post, you push it into every follower's timeline """
            """immediately. Reads become a single lookup, which is lovely. And a post by someone with a """
            """million followers becomes a million writes, which is not.""")
seg(sid, 2, """Fanout on read means that when you open the app, you go and fetch from everyone you """
            """follow and merge. Writes are trivial. Every read becomes a scatter-gather across """
            """hundreds of sources, which at p ninety-nine means waiting for the slowest of """
            """hundreds.""")
seg(sid, 3, """The arithmetic decides it, and for LinkedIn it is lopsided: reads outnumber writes by """
            """something like a hundred to one. So you do the work on the rarer operation, which is the """
            """write.""")
seg(sid, 4, """And that is the staff-level insight, which generalises far beyond feeds: precompute """
            """versus compute-on-demand is decided by the read-write ratio and almost nothing else. Say """
            """the ratio out loud and the decision makes itself &mdash; which also means you have """
            """stopped having an opinion and started having an argument.""")
seg(sid, 5, """Then the hybrid exists for exactly one reason: a single input, the celebrity, breaks the """
            """answer the arithmetic chose. Not because the arithmetic was wrong &mdash; because the """
            """distribution has a tail.""")

think('You chose fanout on write because reads outnumber writes 100 to 1. Then a member with 10 million '
      'followers posts. What does that single write now cost &mdash; and how long will it take before '
      'the last follower sees it?',
      25,
      """Pause. You chose fanout on write because reads outnumber writes a hundred to one. Then someone """
      """with ten million followers posts. What does that single write now cost? And how long before """
      """the last follower actually sees it? Say it out loud.""",
      """Hold that. The answer is why pure fanout-on-write does not survive contact with a real social """
      """graph.""")

clarify('What I would clarify first', [
 ('Chronological, or ranked?',
  '<b>Changes everything.</b> Chronological is a merge. Ranked means a scoring model on the read path '
  'and a feed that is not just a list.'),
 ('What is the follower distribution &mdash; max followers?',
  'The <b>tail is the whole problem</b>. If nobody exceeds 10k followers, pure fanout-on-write works '
  'and you can skip the hybrid entirely.'),
 ('How fresh must a post be &mdash; seconds or minutes?',
  'Seconds forces synchronous-ish fanout. Minutes lets it be a background job, which is far cheaper '
  'and far more robust.'),
 ('How far back does the feed go?',
  'If it is the last few hundred items, timelines are <b>bounded</b> and storage is trivial. Infinite '
  'scroll into history is a different storage problem.'),
 ('Does the feed include things other than follows &mdash; groups, recommendations, ads?',
  'A real feed is a <b>blend of sources</b>, which means the merge step exists regardless of which '
  'fanout you pick.'),
 ('Must every follower see every post?',
  'Almost certainly not &mdash; and if the product is allowed to drop items for inactive users, '
  '<b>fanout cost falls by an order of magnitude</b>.'),
], [
 """Chronological or ranked? This changes everything. Chronological is a merge of sorted lists. Ranked """
 """means a scoring model on the read path, and a feed that is no longer just a list of things in """
 """order.""",
 """What is the follower distribution, and specifically the maximum? The tail is the entire problem """
 """here. If nobody exceeds ten thousand followers, pure fanout-on-write works fine and you can skip """
 """the hybrid altogether &mdash; which is a lovely thing to be able to say.""",
 """How fresh must a post be &mdash; seconds or minutes? Seconds pushes you toward synchronous fanout. """
 """Minutes lets it be a background job, which is dramatically cheaper and more robust.""",
 """How far back does the feed go? If it is the last few hundred items, timelines are bounded and """
 """storage is trivial. Infinite scroll back through history is a different storage problem """
 """entirely.""",
 """Does the feed include things other than follows &mdash; group posts, recommendations, ads? A real """
 """feed is a blend of sources, which means a merge step exists whichever fanout you choose. Worth """
 """establishing early so the merge does not look like an afterthought.""",
 """And the question that can save you an order of magnitude: must every follower see every post? """
 """Almost certainly not. If the product tolerates dropping items for inactive users, fanout cost falls """
 """enormously &mdash; and most of your followers have not opened the app this month.""",
])

capacity('Capacity &mdash; the ratio and the tail', [
 ('100M DAU &times; 10 feed loads / day', '1B feed reads / day &divide; 86,400',
  '&asymp; 11,500 reads / s', 'Peak ~50k/s. The read path is the hot path'),
 ('~1M posts / day', '1M &divide; 86,400', '&asymp; 12 writes / s',
  '<b>Reads outnumber writes ~1,000:1.</b> This number decides the design'),
 ('Average 1,000 connections / member', '12 writes/s &times; 1,000', '&asymp; 12,000 timeline inserts / s',
  'Entirely ordinary. <b>Fanout on write is affordable for the average case</b>'),
 ('One celebrity post, 10M followers', '10M inserts for 1 write',
  '<b>10M writes in one burst</b>', 'At 50k inserts/s that is <b>200 seconds</b> of fanout &mdash; and '
  'the last follower sees it 3 minutes late'),
 ('Timeline storage: 100M users &times; 500 items &times; 100 B', '100M &times; 50 KB',
  '&asymp; 5 TB', 'Cheap, and it fits in a cache tier. <b>Bounded timelines are what make this '
  'affordable</b>'),
 ('If timelines were unbounded', 'grows forever, no natural cap', '&mdash;',
  '<b>Cap at N items.</b> Nobody scrolls past 500; the cap is the storage design'),
], [
 """Numbers, and in this question they do the arguing. A hundred million daily actives loading the feed """
 """ten times a day is a billion reads, about eleven and a half thousand a second, maybe fifty thousand """
 """at peak. The read path is the hot path.""",
 """Posts: about a million a day, which is twelve writes a second. So reads outnumber writes by roughly """
 """a thousand to one. That single number decides the design, and I would say it out loud before I draw """
 """anything.""",
 """With an average of a thousand connections, twelve writes a second becomes twelve thousand timeline """
 """inserts a second. Completely ordinary for any key-value store. So fanout on write is comfortably """
 """affordable &mdash; for the average case.""",
 """Now the tail. One celebrity post to ten million followers is ten million inserts from a single """
 """write. At fifty thousand inserts a second that is two hundred seconds of fanout, so the last """
 """follower sees the post more than three minutes after it was published. That is the answer to the """
 """question I asked you to pause on, and it is why pure fanout-on-write does not survive a real social """
 """graph.""",
 """Timeline storage: a hundred million users times five hundred items times a hundred bytes is about """
 """five terabytes. Cheap, and small enough to live in a cache tier.""",
 """And note why it is only five terabytes &mdash; because timelines are capped at five hundred items. """
 """Nobody scrolls past five hundred. The cap is not an optimisation, it is the storage design.""",
])

A = Arch('Hybrid feed &mdash; push for most, pull for the famous', kicker='Architecture', height=800)

A.box('post',  60, 180, 155, 90, 'Post', '12 / s', kind='neutral', step=0, focus=0, small=True)
A.box('psvc', 255, 170, 195, 110, 'Post service', 'writes once', kind='ok', step=0, focus=0)
A.arrow('post', 'psvc', step=0, focus=0)

A.box('pdb',  530, 170, 210, 105, 'Post store', 'source of truth', kind='dp', step=0, focus=0, small=True)
A.arrow('psvc', 'pdb', step=0, focus=0)

A.box('fan',  530, 320, 210, 110, 'Fanout workers', 'push to timelines', kind='info', step=1, focus=[1, 2])
A.arrow('psvc', 'fan', step=1, label='if < 10k followers', focus=1, dashed=True)

A.box('tl',   830, 320, 215, 110, 'Timelines', 'per user, capped 500', kind='ok', step=2, focus=[2, 4])
A.arrow('fan', 'tl', step=2, focus=2)

A.box('cel',  830, 160, 215, 105, 'Celebrity posts', 'NOT fanned out', kind='shared', step=3, focus=3)
A.arrow('psvc', 'cel', step=3, label='if &ge; 10k', focus=3, dashed=True)

A.box('read',  60, 560, 155, 90, 'Open app', '50k / s', kind='neutral', step=4, focus=4, small=True)
A.box('fsvc', 255, 550, 195, 110, 'Feed service', 'merge + rank', kind='ok', step=4, focus=[4, 5, 6])
A.arrow('read', 'fsvc', step=4, focus=4)
A.arrow('tl', 'fsvc', step=4, label='precomputed', focus=4, dashed=True)
A.arrow('cel', 'fsvc', step=5, label='pulled live', focus=5, dashed=True)

A.box('rank', 830, 550, 215, 110, 'Ranker', 'score + blend', kind='info', step=6, focus=6)
A.arrow('fsvc', 'rank', step=6, focus=6)

A.box('out', 1130, 550, 195, 105, 'Feed', 'top ~50', kind='ok', step=6, focus=6, small=True)
A.arrow('rank', 'out', step=6, focus=6)

A.note(1130, 300, 'Most of the feed is already computed. Only the handful of celebrities you follow are fetched live.',
       step=5, kind='info', w=450)

A.narrate(0, """A post arrives, the post service writes it once to the post store, which is the source """
             """of truth. Everything after this is derived data, and saying that distinction out loud """
             """matters &mdash; derived data can be rebuilt, so it does not need the same guarantees.""",
          A.flow([(215, 222), (255, 222), (530, 222)]))
A.narrate(1, """If the author has fewer than, say, ten thousand followers &mdash; which is almost """
             """everyone &mdash; fanout workers push the post into each follower's timeline """
             """asynchronously.""",
          A.flow([(450, 250), (530, 370)]))
A.narrate(2, """Timelines are per-user lists capped at five hundred items. Precomputed, so a read is one """
             """lookup.""",
          A.flow([(740, 375), (830, 375)]))
A.narrate(3, """But if the author has ten thousand followers or more, we do <i>not</i> fan out. The post """
             """just sits in the celebrity store. That one branch is the entire hybrid, and it is worth """
             """pausing on: we are deliberately not doing the work for the cases where the work is """
             """expensive.""",
          A.flow([(450, 200), (830, 212)]))
A.narrate(4, """On read, the feed service fetches the precomputed timeline &mdash; one lookup, """
             """cheap.""",
          A.flow([(215, 605), (255, 605)]))
A.narrate(5, """And then pulls live from the handful of celebrities this member follows. If I follow five """
             """celebrities, that is five extra fetches, not five hundred. The scatter-gather that made """
             """fanout-on-read unaffordable is now tiny, because it only covers the exceptions.""",
          A.flow([(935, 265), (450, 580)]))
A.narrate(6, """The two sets are merged, ranked and truncated to about fifty items. Ranking on the read """
             """path is what makes personalisation possible &mdash; and it is also where the latency """
             """budget gets spent, so it needs a timeout and a fallback to chronological.""",
          A.flow([(450, 605), (830, 605), (1130, 602)]))
A.build()

sid = beat('Deep dive 1', 'The celebrity problem, and why the hybrid is not a compromise',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>The failure:</b> 10M followers &times; one post = 10M writes. At 50k inserts/s that is '
           '200 seconds of fanout. The last follower sees it <b>3 minutes late</b> &mdash; and during '
           'those 3 minutes your write pipeline is saturated, delaying <i>everyone else&rsquo;s</i> '
           'posts.<br><br>'
           '<span style="color:#ff9a9a">The damage is not to the celebrity. It is to every ordinary '
           'user whose post is stuck behind 10M inserts.</span><br><br>'
           '<b>The hybrid:</b> fan out below a follower threshold; pull above it.<br>'
           '&bull; <b>99.9% of posts</b> are fanned out &mdash; reads stay a single lookup<br>'
           '&bull; <b>The handful you follow who are famous</b> are fetched at read time<br>'
           '&bull; I follow maybe 5 celebrities &rarr; 5 extra fetches, not 500<br><br>'
           '<b>Where to put the threshold:</b> not a round number &mdash; derive it. Fan out while '
           '<code>followers &times; writeCost &lt; followerCount &times; readCost &times; '
           'readsPerFollower</code>. <span style="color:#a8e6a3">In practice 10k&ndash;100k, tuned by '
           'measurement.</span><br><br>'
           '<span style="color:#ffd483">This is not a compromise between two designs. It is '
           'recognising that the follower distribution has a long tail, and applying a different '
           'strategy to each part of it.</span></div>',
           """Deep dive one: the celebrity problem, which is the heart of this question.""", step=0)
seg(sid, 1, """Ten million followers times one post is ten million writes. At fifty thousand inserts a """
            """second that is two hundred seconds of fanout, so the last follower sees it three minutes """
            """late. And during those three minutes your write pipeline is saturated.""")
seg(sid, 2, """Which means the real damage is not to the celebrity at all. It is to every ordinary user """
            """whose perfectly normal post is now stuck in a queue behind ten million inserts. One """
            """user's popularity has become everyone else's latency, and that framing is worth saying """
            """&mdash; it is why this is an architecture problem rather than a capacity problem.""")
seg(sid, 3, """The hybrid: fan out below a follower threshold, pull above it. Ninety-nine point nine """
            """percent of posts are fanned out, so reads stay a single lookup. The handful of famous """
            """accounts you follow are fetched at read time. If I follow five celebrities, that is five """
            """extra fetches, not five hundred.""")
seg(sid, 4, """Where to put the threshold &mdash; and I would resist naming a round number as though it """
            """were obvious. Derive it: fan out while the cost of the writes is less than the cost of """
            """the reads you would otherwise do, which depends on how often followers actually read. In """
            """practice it lands somewhere between ten and a hundred thousand, tuned by measurement, """
            """and it is different for a network where people read daily than one where they read """
            """monthly.""")
seg(sid, 5, """And the framing I would most want to land: this is not a compromise between two designs. """
            """It is recognising that the follower distribution has a long tail, and applying a """
            """different strategy to each part of it. Whenever a distribution is skewed, uniform """
            """strategies lose &mdash; and that applies well beyond feeds.""")

sid = beat('Deep dive 2', 'Ranking, and the latency it must never cost you',
           '<div style="font-size:27px;line-height:1.7">'
           'A chronological feed is a merge. A <b>ranked</b> feed is a model on the read path, and that '
           'puts machine learning inside your latency budget.<br><br>'
           '<b>The shape (and you have seen it twice already):</b><br>'
           '&bull; <b>Candidate generation</b> &mdash; timeline + celebrity pulls + groups + '
           'recommendations &rarr; a few hundred items<br>'
           '&bull; <b>Feature lookup</b> &mdash; author affinity, recency, engagement rate, content type<br>'
           '&bull; <b>Scoring</b> &mdash; one model over all candidates, whatever their source<br>'
           '&bull; <b>Blending rules</b> &mdash; diversity, no three posts from one author, ad slots<br><br>'
           '<span style="color:#ffd483">Same pipeline as typeahead ranking (5.3) and job '
           'recommendations (9.1). Three products, one shape.</span><br><br>'
           '<b>The engineering discipline that matters:</b><br>'
           '&bull; Hard timeout on the model &rarr; <b>fall back to chronological</b><br>'
           '&bull; Cache the <i>ranked</i> feed for a few minutes &mdash; most refreshes are within '
           'minutes of each other<br>'
           '&bull; <span style="color:#a8e6a3">A feed that is a bit stale beats a feed that is '
           'slow, and far beats a feed that is absent.</span></div>',
           """Deep dive two: ranking. A chronological feed is a merge. A ranked feed puts a machine """
           """learning model on the read path, which means inference inside your latency budget.""",
           step=0)
seg(sid, 1, """The shape is one you have now seen three times in this course. Candidate generation """
            """&mdash; the timeline, plus celebrity pulls, plus group posts and recommendations &mdash; """
            """giving a few hundred items.""")
seg(sid, 2, """Then feature lookup: affinity with the author, recency, the post's engagement rate so """
            """far, content type. Then scoring with one model over all candidates regardless of where """
            """they came from &mdash; same trick as blending companies and people in typeahead.""")
seg(sid, 3, """Then blending rules on top: diversity, no three posts in a row from the same author, ad """
            """slots. Those are product rules rather than model output, and keeping them separate from """
            """the model makes both easier to change.""")
seg(sid, 4, """It is worth naming that this is the identical pipeline to typeahead ranking in lesson """
            """five point three and job recommendations in chapter nine. Three completely different """
            """products, one shape: generate candidates cheaply, then rank. Recognising that is worth """
            """more than any individual design.""")
seg(sid, 5, """And the engineering discipline that actually matters. Hard timeout on the model, falling """
            """back to chronological &mdash; a worse feed beats a spinner. Cache the ranked feed for a """
            """few minutes, because most refreshes happen within minutes of each other and recomputing """
            """is pure waste. The principle: a feed that is slightly stale beats a feed that is slow, """
            """and massively beats a feed that failed to load.""")

tradeoff('Fanout on write, on read, or hybrid', [
 ('Fanout on write (push)', 'info',
  ['<b>Read is one lookup</b>', 'Read latency is predictable and low',
   'Correct choice when reads dominate'],
  ['A celebrity post is millions of writes', 'Wasted work for inactive followers',
   '<b>One slow post delays everyone else&rsquo;s</b>']),
 ('Fanout on read (pull)', 'shared',
  ['Writes are trivial', 'No wasted work for users who never log in',
   'No celebrity problem at all'],
  ['<b>Every read is a scatter-gather over hundreds of sources</b>',
   'p99 is the slowest of hundreds', 'Cannot meet a feed latency target at scale']),
 ('Hybrid &mdash; push below a threshold, pull above', 'ok',
  ['Reads stay ~one lookup plus a handful of pulls', 'Celebrity posts cost nothing to publish',
   'Each part of the distribution gets the right strategy'],
  ['Two code paths and a threshold to tune', 'Merge logic at read time',
   'A member who follows 500 celebrities is still slow']),
], 'Hybrid. Reads outnumber writes ~1,000:1 so the default is push, and the celebrity tail is exactly '
   'the case where push is wrong.',
 'If the maximum follower count were small &mdash; a company intranet, say &mdash; I would use pure '
 'fanout-on-write and skip the hybrid entirely. <b>The hybrid exists because of the tail; no tail, no '
 'hybrid.</b>',
 [
 """Trade-off: push, pull, or hybrid. Fanout on write makes the read a single lookup with predictable """
 """low latency, and it is the correct choice whenever reads dominate. It costs you millions of writes """
 """for a celebrity post, wasted work for followers who never log in, and &mdash; the one that hurts """
 """&mdash; one slow post delaying everyone else's.""",
 """Fanout on read makes writes trivial, wastes nothing on inactive users, and has no celebrity problem """
 """whatsoever. It costs you a scatter-gather over hundreds of sources on every single read, where p """
 """ninety-nine is the slowest of hundreds. You cannot meet a feed latency target that way at """
 """scale.""",
 """The hybrid keeps reads at roughly one lookup plus a handful of pulls, makes celebrity posts free to """
 """publish, and gives each part of the distribution the strategy that suits it. It costs two code """
 """paths, a threshold to tune, and merge logic at read time. And it has a residual weakness worth """
 """naming: a member who follows five hundred celebrities is still slow, so you cap the pulls and """
 """accept slightly less complete coverage for them.""",
 """I would take the hybrid, because reads outnumber writes a thousand to one so the default is push, """
 """and the celebrity tail is exactly where push is wrong.""",
 """And what would flip it: if the maximum follower count were small &mdash; a company intranet, say """
 """&mdash; I would use pure fanout-on-write and skip the hybrid entirely. The hybrid exists because of """
 """the tail. No tail, no hybrid. Always check whether you have the problem before you build the """
 """solution to it.""",
])

failures('What happens when each piece dies', [
 ('Fanout workers fall behind', 'Posts appear in feeds minutes late',
  'The post store already has it, so <b>nothing is lost</b> &mdash; only delayed. Alert on fanout lag. '
  'Feeds are derived data and can always be rebuilt'),
 ('Timeline store unavailable', 'Feed is empty or stale',
  '<b>Fall back to pull</b> for everyone, accepting worse latency. Having both code paths means the '
  'fallback already exists &mdash; an underrated benefit of the hybrid'),
 ('Ranking model times out', 'Feed is chronological rather than ranked',
  'Hard timeout and fall back. <b>A worse feed beats no feed</b>, and the user may not even notice'),
 ('A celebrity gains followers and crosses the threshold', 'Inconsistent: some pushed, some pulled',
  'Threshold crossing must be handled explicitly &mdash; <b>deduplicate at merge time</b> by post ID, '
  'or a member sees the same post twice'),
 ('A post is deleted after fanout', 'It lingers in millions of timelines',
  '<b>Filter at read time against the post store</b>; do not try to retract from millions of lists. '
  'Deletion in a fanned-out system is always a read-time filter'),
 ('Fanout duplicates a post (retry)', 'Duplicates in the feed',
  'Timeline insert keyed by <code>(userId, postId)</code> so it is <b>idempotent</b>. At-least-once '
  'delivery makes retries certain'),
], [
 """Failures. Fanout workers fall behind and posts appear minutes late. Nothing is lost, because the """
 """post store already has the post &mdash; only the derived timelines are behind. Alert on fanout lag. """
 """And the general principle: feeds are derived data and can always be rebuilt, which is why this is a """
 """delay rather than a disaster.""",
 """Timeline store unavailable means empty or stale feeds. Fall back to pull for everyone and accept """
 """worse latency. And here is an underrated benefit of the hybrid: because you already have both code """
 """paths, the fallback exists for free. A design that bends gives you failure modes you did not have """
 """to build.""",
 """Ranking model times out and the feed is chronological instead of ranked. Hard timeout, fall back, """
 """and the user may genuinely not notice.""",
 """A celebrity gains followers and crosses the threshold, so some followers got the post pushed and """
 """others will pull it. That must be handled explicitly &mdash; deduplicate at merge time by post I-D, """
 """or a member sees the same post twice. Threshold crossings are the classic bug in hybrid systems and """
 """raising it unprompted is a good signal.""",
 """A post deleted after fanout lingers in millions of timelines. Do not try to retract it from """
 """millions of lists &mdash; filter at read time against the post store. Deletion in a fanned-out """
 """system is always a read-time filter, and the same is true in any precomputed system.""",
 """And fanout duplicating a post on retry. Key the timeline insert on user I-D and post I-D so it is """
 """idempotent. With at-least-once delivery, retries are certain rather than hypothetical.""",
])

say('What I should actually say in the room', [
 'Let me get the ratio first, because it decides the design: roughly a billion feed reads a day against '
 'about a million posts. Reads outnumber writes by around a thousand to one.',
 'So I do the work on the rarer operation &mdash; fanout on write. When you post, I push it into your '
 'followers&rsquo; timelines, and a read becomes a single lookup.',
 'That breaks for one input. Ten million followers means ten million writes for one post, which is '
 'about 200 seconds of fanout &mdash; and during that time ordinary users&rsquo; posts are queued '
 'behind it. The damage is to everyone else, not to the celebrity.',
 'So: hybrid. Fan out below a follower threshold, and for accounts above it, do not fan out at all '
 '&mdash; pull their posts at read time and merge. I follow maybe five famous accounts, so that is '
 'five extra fetches, not five hundred.',
 'The threshold is derived, not guessed: fan out while the write cost is less than the read cost you '
 'would otherwise pay, which depends on how often followers actually read.',
 'Timelines are capped at about 500 items, which is why the whole thing is only ~5 TB and can sit in a '
 'cache tier.',
 'Ranking sits on the read path with a hard timeout and a chronological fallback, because a slightly '
 'worse feed beats a slow one, and massively beats one that fails to load.',
], [
 """The sentences. Lead with the ratio, because it converts a design opinion into a derived decision """
 """&mdash; and interviewers who have heard this question two hundred times will notice immediately.""",
 """Then the choice it implies, then the single input that breaks it with its real cost in seconds. """
 """Then the hybrid, framed as applying different strategies to different parts of the """
 """distribution.""",
 """Then the derived threshold, the storage cap that makes it cheap, and the ranking discipline. Seven """
 """sentences and you have covered every named follow-up.""",
])

followups([
 'Fanout on write or fanout on read?',
 'How does the hybrid work?',
 'How do you handle celebrity / high-follower users?',
 'How do you rank the feed?',
 'How do you cache it?',
 'How do you partition timelines?',
 'How do real-time updates work?',
 'How do you personalise it?',
], [
 'A member follows 500 celebrities. What happens to their read path?',
 'How do you backfill a timeline for someone who has not logged in for a year?',
 'How would you A/B test a ranking change safely?',
 'What does this cost, and what is the first thing you would cut?',
 'Someone posts something harmful and it is already in 10M timelines. Now what?',
],
 """The reported follow-ups are the lesson. On partitioning: timelines partition by user I-D, so one """
 """member's feed lives on one shard and a read is one lookup. And real-time updates are a push over a """
 """web socket for members who currently have the app open, falling back to polling &mdash; that is a """
 """delivery concern layered on top rather than a change to the fanout decision.""",
 """The staff-level follow-ups go after the weak points. Five hundred celebrities is the residual """
 """weakness of the hybrid, and the honest answer is cap the pulls and accept partial coverage for that """
 """member. Backfilling a dormant user's timeline is a pull, which is why you should not fan out to """
 """inactive users in the first place. A-B testing ranking safely means shadow scoring offline before """
 """serving. Cost: the fanout write volume dominates, so the first cut is to stop fanning out to """
 """members who have not opened the app in thirty days. And the harmful post already in ten million """
 """timelines is the read-time filter again &mdash; which is exactly why you filter on read rather """
 """than trusting the copies.""")

cheatsheet('News feed &mdash; the one-page card', [
 ('Requirements', 'Personalised feed; low read latency; survive high-follower accounts'),
 ('Scale', '~11.5k reads/s (50k peak) vs ~12 writes/s &mdash; <b>~1,000:1</b>. 12k timeline inserts/s. '
           '~5 TB of timelines'),
 ('Core architecture', 'Post &rarr; post store (truth) &rarr; fanout workers (if under threshold) '
                       '&rarr; per-user timelines. Read: timeline + celebrity pull &rarr; merge &rarr; '
                       'rank'),
 ('Data store', 'Post store is the source of truth; timelines are <b>derived and rebuildable</b>'),
 ('Partition key', '<code>userId</code> for timelines &mdash; one member&rsquo;s feed on one shard, so '
                   'a read is one lookup'),
 ('Cache', 'Timelines are effectively the cache. Also cache the <i>ranked</i> feed for a few minutes'),
 ('Queue', 'Fanout jobs. Async, so a slow fanout delays feeds but never blocks posting'),
 ('Consistency', 'Eventual. A post appearing seconds late is fine; appearing twice is not &mdash; so '
                 'idempotent inserts keyed on (user, post)'),
 ('Failure handling', 'Fall back to pull; dedupe on merge; <b>delete by read-time filter</b>, never by '
                      'retraction'),
 ('Key deep dives', 'The celebrity problem and the derived threshold &middot; ranking with a '
                    'chronological fallback'),
 ('Biggest trade-off', 'Precompute vs compute-on-demand, decided by the read/write ratio &mdash; then '
                       'split by the <b>tail of the distribution</b>'),
], [
 """The card. The scale row carries the number that decides everything: a thousand to one. Architecture """
 """in two lines, write path and read path.""",
 """Note the data store row &mdash; the post store is truth and timelines are derived and rebuildable. """
 """That is what makes every fanout failure a delay rather than a loss. Partition timelines by user """
 """I-D so a read is one lookup.""",
 """Consistency: appearing late is fine, appearing twice is not, hence idempotent inserts. Deletion is """
 """a read-time filter, never a retraction. And the biggest trade-off is precompute versus compute on """
 """demand, decided by the ratio and then split by the tail.""",
])

say('The 60-second answer', [
 'The decision here is when to do the work, and the ratio decides it: about a billion feed reads a day '
 'against a million posts, so reads outnumber writes roughly a thousand to one. You do the work on the '
 'rarer operation, which means fanout on write.',
 'So when someone posts, workers push it into each follower&rsquo;s timeline asynchronously, and a feed '
 'read becomes a single lookup of a precomputed list.',
 'That breaks on exactly one input. Ten million followers means ten million writes from one post '
 '&mdash; roughly 200 seconds of fanout &mdash; and while that runs, ordinary members&rsquo; posts are '
 'queued behind it. The damage lands on everyone else.',
 'So the design is hybrid: fan out below a follower threshold, and above it do not fan out at all. '
 'Those posts are pulled at read time and merged, and since I follow only a handful of famous accounts '
 'that is a handful of extra fetches rather than hundreds.',
 'The threshold is derived rather than guessed &mdash; fan out while the write cost is below the read '
 'cost you would otherwise pay, which depends on how often followers actually read.',
 'Timelines are capped at around 500 items, which keeps the whole store near 5 TB, and ranking sits on '
 'the read path with a hard timeout and a chronological fallback &mdash; because a slightly worse feed '
 'beats a slow one.',
], [
 """The sixty-second answer. The first sentence is the one that matters: converting the design choice """
 """into arithmetic. Everyone else will assert fanout-on-write; you will derive it.""",
 """And the third sentence &mdash; that the damage lands on everyone else rather than the celebrity """
 """&mdash; is the line that shows you understand why the hybrid exists rather than just that it does. """
 """Practise those two until they are automatic.""",
], kicker='60-second interview answer')
