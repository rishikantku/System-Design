# -*- coding: utf-8 -*-
"""Chapter 9, Lesson 1 — LinkedIn job recommendations."""
from lib import *

lesson_header('9.1', 'Design LinkedIn job recommendations',
              'Candidate generation &rarr; filter &rarr; rank &middot; offline vs online &middot; feature store',
              dict(reports='InterviewTV list only', latest='2026', level='Staff',
                   conf='MEDIUM &mdash; single source, and squarely LinkedIn-shaped',
                   sources='InterviewTV.io'), 20,
              """Chapter nine, lesson one: job recommendations. Millions of jobs, recommend the top """
              """three, reasonable latency, use the member profile, filter for basic qualification, """
              """high personalisation accuracy, optionally real-time interests. One billion members, a """
              """hundred million daily active. This is the most LinkedIn-shaped question in the course """
              """&mdash; it is literally the company's product &mdash; and it is the one where the """
              """right answer is a pipeline rather than an architecture.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  'Millions of jobs, <b>top 3</b>, reasonable latency, member profile, qualification filtering, high '
  'personalisation, optional real-time interests. <b>1B members, 100M DAU.</b> Deep dives: candidate '
  'generation, filtering, ranking, feature store, offline training, online inference, real-time '
  'signals, caching, freshness, partitioning, evaluation'),
], """Single source, so medium confidence. But it is unusually detailed &mdash; it gives the scale, the """
     """output size, and eleven named deep dives.""",
 ["""And those deep dives are the standard recommender pipeline, in order: candidate generation, """
  """filtering, ranking, feature store, offline training, online inference. If you know that pipeline, """
  """you have the skeleton of the answer before you start."""],
 caveat='Single source. But this is LinkedIn\'s actual product, so an interviewer asking it will have '
        'real depth &mdash; prepare the pipeline properly.',
 narration_caveat="""Single source. But this is LinkedIn's actual core product, so an interviewer """
                  """asking it will have genuine depth. Prepare the pipeline properly rather than """
                  """superficially.""")

sid = beat('Why this is interesting', 'Millions of candidates, three slots, and ~200 ms',
           '<div style="font-size:28px;line-height:1.72">'
           'You cannot score millions of jobs per request. A good ranking model takes '
           '<b>~1 ms per candidate</b>. 10 million jobs &times; 1 ms = <span style="color:#ff9a9a">'
           'nearly 3 hours per request.</span><br><br>'
           '<b>So the pipeline is a funnel, and each stage buys the next one its budget:</b><br>'
           '&bull; <b>Candidate generation</b> &mdash; millions &rarr; ~1,000. Cheap, recall-oriented, '
           'mostly precomputed<br>'
           '&bull; <b>Filtering</b> &mdash; 1,000 &rarr; ~500. Hard constraints: location, '
           'qualification, already applied<br>'
           '&bull; <b>Ranking</b> &mdash; 500 &rarr; ordered. Expensive model, affordable only because '
           'there are 500 and not 10 million<br>'
           '&bull; <b>Re-rank</b> &mdash; diversity, freshness, business rules &rarr; <b>top 3</b><br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: the funnel is not an optimisation, it is '
           'the architecture. Each stage exists so the next one can afford to be smarter.</span><br><br>'
           '<span style="color:#a8e6a3">You have seen this shape twice already &mdash; typeahead '
           'ranking and feed ranking. Third time. Name it.</span></div>',
           """Why is this interesting? Because of a simple arithmetic impossibility. You cannot score """
           """millions of jobs per request. A good ranking model takes roughly a millisecond per """
           """candidate, so ten million jobs is nearly three hours for one page load.""", step=0)
seg(sid, 1, """So the pipeline is a funnel, and the key idea is that each stage exists to buy the next """
            """one its budget. Candidate generation takes millions down to about a thousand &mdash; """
            """cheap, recall-oriented, and mostly precomputed.""")
seg(sid, 2, """Filtering takes a thousand down to maybe five hundred by applying hard constraints: """
            """location, basic qualification, jobs you have already applied to. Then ranking orders """
            """those five hundred with an expensive model &mdash; and it is only affordable because """
            """there are five hundred rather than ten million.""")
seg(sid, 3, """And a final re-rank applies diversity, freshness and business rules to produce the top """
            """three.""")
seg(sid, 4, """The staff-level insight is that the funnel is not an optimisation layered onto a design. """
            """It is the architecture. Each stage exists so that the next stage can afford to be """
            """smarter, and that framing is what separates a recommender answer from a list of """
            """components.""")
seg(sid, 5, """And you have now seen this shape three times &mdash; typeahead ranking in chapter five, """
            """feed ranking in chapter seven, and now here. Name it out loud when you spot it. """
            """Recognising that three different products share one pipeline is worth more than any """
            """individual design.""")

think('A member opens the jobs tab. You have 10 million open jobs and about 200 milliseconds. Before any '
      'model runs, how do you get from 10 million to roughly 1,000 candidates &mdash; and what work has '
      'to have happened before the request arrived?',
      25,
      """Pause. A member opens the jobs tab. Ten million open jobs, about two hundred milliseconds. """
      """Before any model runs, how do you get from ten million down to roughly a thousand candidates? """
      """And what work must already have happened before the request even arrived? Say it out loud.""",
      """Hold that. The phrase &ldquo;before the request arrived&rdquo; is the whole answer to """
      """recommender latency.""")

clarify('What I would clarify first', [
 ('What are we optimising &mdash; applications, hires, or clicks?',
  '<b>The most important question.</b> Clicks optimise for clickbait. Applications optimise for '
  'volume. <b>Hires</b> are what the product is for, and the feedback loop is months long.'),
 ('Is this a feed the member browses, or a notification we push?',
  'Browsing means on-demand and latency matters. Pushing means it can be <b>fully precomputed '
  'offline</b>, and the whole latency problem disappears.'),
 ('&ldquo;Basic qualification filtering&rdquo; &mdash; how strict?',
  'A hard filter on years of experience <b>removes career changers</b>. Is that intended? Filtering is '
  'a product decision with fairness consequences.'),
 ('What is &ldquo;reasonable latency&rdquo;?',
  'Say it back as a number. ~200 ms gives roughly 500 candidates through a real model; 50 ms does '
  'not.'),
 ('How fresh must new jobs be?',
  'A job posted an hour ago that is already filled is a bad recommendation. <b>Freshness is both a '
  'quality and a trust issue.</b>'),
 ('Is there a two-sided constraint &mdash; do recruiters care who applies?',
  'Jobs is a <b>marketplace</b>. Sending 10,000 unqualified applicants to one posting is a failure '
  'even if every member clicked.'),
], [
 """What are we optimising &mdash; applications, hires, or clicks? This is the most important question """
 """in the whole problem. Optimise clicks and you get clickbait job titles. Optimise applications and """
 """you get volume regardless of fit. Hires are what the product is actually for, and the feedback loop """
 """for a hire is months long, which makes training genuinely hard. Say that.""",
 """Is this a feed the member browses, or notifications we push? Browsing means on-demand and latency """
 """matters. Pushing means it can be fully precomputed offline overnight, and the entire latency """
 """problem disappears. That is a huge simplification to ask for.""",
 """Basic qualification filtering &mdash; how strict? A hard filter on years of experience removes """
 """career changers, who are often exactly the people a job board should serve. Filtering is a product """
 """decision with fairness consequences, not a technical detail.""",
 """What is reasonable latency? Say it back as a number. Two hundred milliseconds gets you roughly five """
 """hundred candidates through a real model. Fifty milliseconds does not.""",
 """How fresh must new jobs be? A job posted an hour ago that has already been filled is a bad """
 """recommendation, and that is both a quality problem and a trust problem.""",
 """And is there a two-sided constraint &mdash; do recruiters care who applies? Jobs is a marketplace. """
 """Sending ten thousand unqualified applicants to one posting is a failure even if every single member """
 """clicked. Raising the two-sided nature unprompted is a strong signal, because most candidates design """
 """this as if only the member matters.""",
])

capacity('Capacity', [
 ('100M DAU &times; ~2 jobs-page views', '200M requests / day &divide; 86,400',
  '&asymp; 2,300 req / s', 'Peak ~10,000/s. Each one runs the full funnel'),
 ('10M open jobs &times; 1 ms model inference', 'if we scored everything', '&asymp; 3 hours / request',
  '<b>Impossible.</b> This number is the justification for the entire funnel'),
 ('Candidate generation &rarr; ~1,000', 'precomputed ANN / inverted index lookups',
  '&asymp; 10&ndash;20 ms', 'Mostly precomputed. <b>The work happened before the request</b>'),
 ('Ranking 500 candidates &times; ~0.2 ms', '500 &times; 0.2 ms, batched', '&asymp; 100 ms',
  'Fits the budget <b>only because it is 500</b>. Batching is essential'),
 ('Feature store lookups', '~50 features &times; 500 candidates', '&asymp; 25,000 lookups / request',
  '<b>The hidden cost.</b> Must be one batched call, not 25,000 round trips'),
 ('Embeddings: 10M jobs &times; 128 dims &times; 4 B', '10M &times; 512 B', '&asymp; 5 GB',
  'Fits in memory for ANN search. <b>1B member embeddings = 512 GB</b> &mdash; sharded, or computed '
  'on the fly'),
], [
 """Numbers. A hundred million daily actives viewing the jobs page twice is two hundred million """
 """requests a day, about twenty-three hundred a second, maybe ten thousand at peak. Each one runs the """
 """full funnel.""",
 """Now the number that justifies everything: ten million open jobs at a millisecond of model inference """
 """each would be three hours per request. Impossible by four orders of magnitude. I would put that on """
 """the board early, because it turns the funnel from a design choice into a necessity.""",
 """Candidate generation down to about a thousand costs ten to twenty milliseconds, because it is """
 """mostly precomputed lookups &mdash; approximate nearest neighbour over embeddings, or inverted index """
 """lookups. The work happened before the request arrived, which is the answer to what I asked you to """
 """pause on.""",
 """Ranking five hundred candidates at about point two milliseconds each, batched, is roughly a hundred """
 """milliseconds. That fits the budget only because it is five hundred, and only because you batch """
 """&mdash; five hundred separate model calls would not fit.""",
 """And here is the hidden cost people miss: fifty features times five hundred candidates is """
 """twenty-five thousand feature lookups per request. That has to be one batched call to a feature """
 """store, not twenty-five thousand round trips. If you get that wrong, the feature store becomes the """
 """bottleneck and the model never gets a chance.""",
 """Embeddings: ten million jobs at a hundred and twenty-eight dimensions is about five gigabytes, """
 """which fits in memory for nearest-neighbour search. A billion member embeddings would be five """
 """hundred and twelve gigabytes, so those are sharded or computed on the fly from the profile.""",
])

A = Arch('The recommender funnel &mdash; offline builds, online serves', kicker='Architecture', height=800)

A.zone(60, 500, 820, 250, 'OFFLINE — hours, and most of the real work')

A.box('req',   60, 190, 150, 90, 'Jobs page', '10k/s peak', kind='neutral', step=0, focus=0, small=True)
A.box('svc',  245, 180, 180, 110, 'Rec service', '~200 ms', kind='ok', step=0, focus=[0, 1, 2, 3])
A.arrow('req', 'svc', step=0, focus=0)

A.box('cg',   505, 160, 205, 110, 'Candidate gen', '10M &rarr; 1,000', kind='ok', step=1, focus=1)
A.arrow('svc', 'cg', step=1, focus=1)

A.box('flt',  770, 160, 190, 110, 'Filters', '1,000 &rarr; 500', kind='info', step=2, focus=2)
A.arrow('cg', 'flt', step=2, focus=2)

A.box('rank',1020, 160, 200, 110, 'Ranker', '500 scored', kind='ok', step=3, focus=[3, 4])
A.arrow('flt', 'rank', step=3, focus=3)

A.box('fs',  1020, 330, 200, 105, 'Feature store', 'batched lookup', kind='shared', step=4, focus=4, small=True)
A.arrow('rank', 'fs', step=4, focus=4, dashed=True)

A.box('rr',  1280, 160, 190, 110, 'Re-rank', 'diversity &rarr; top 3', kind='ok', step=5, focus=5)
A.arrow('rank', 'rr', step=5, focus=5)

A.box('emb',  105, 560, 200, 105, 'Embeddings', 'jobs + members', kind='dp', step=6, focus=6, small=True)
A.box('idx',  360, 560, 200, 105, 'ANN index', 'rebuilt hourly', kind='dp', step=6, focus=6, small=True)
A.box('train',615, 560, 215, 105, 'Model training', 'on logged outcomes', kind='dp', step=7, focus=7, small=True)
A.arrow('emb', 'idx', step=6, focus=6)
A.arrow('idx', 'cg', step=6, focus=6, dashed=True)
A.arrow('train', 'rank', step=7, focus=7, dashed=True)

A.box('log',  615, 330, 215, 105, 'Interaction log', 'impressions, clicks,<br>applies, hires',
      kind='shared', step=7, focus=7, small=True)
A.arrow('rr', 'log', step=7, focus=7, dashed=True)
A.arrow('log', 'train', step=7, focus=7, dashed=True)

A.note(1280, 330, 'Each stage exists so the next can afford to be smarter. The funnel IS the architecture.',
       step=3, kind='info', w=420)

A.narrate(0, """A member opens the jobs page. The recommendation service has about two hundred """
             """milliseconds.""",
          A.flow([(210, 235), (245, 235)]))
A.narrate(1, """Candidate generation takes ten million jobs down to about a thousand, using a precomputed """
             """approximate nearest neighbour index over embeddings, plus simpler sources like """
             """&ldquo;jobs at companies you follow&rdquo;. Recall-oriented: it is fine to include """
             """mediocre candidates, but a job that never enters here can never be recommended.""",
          A.flow([(425, 215), (505, 215)]))
A.narrate(2, """Filters cut that to about five hundred with hard constraints &mdash; location, work """
             """authorisation, already applied, already dismissed. These are binary and """
             """non-negotiable, which is why they come before the model rather than inside it.""",
          A.flow([(710, 215), (770, 215)]))
A.narrate(3, """Then the ranker scores five hundred candidates with a real model. Affordable only """
             """because of the two stages before it.""",
          A.flow([(960, 215), (1020, 215)]))
A.narrate(4, """The ranker pulls features from a feature store in one batched call &mdash; roughly """
             """twenty-five thousand feature values per request, which must not be twenty-five thousand """
             """round trips.""",
          A.flow([(1120, 270), (1120, 330)]))
A.narrate(5, """Then re-ranking for diversity &mdash; not three jobs at the same company &mdash; """
             """freshness and business rules, producing the top three.""",
          A.flow([(1220, 215), (1280, 215)]))
A.narrate(6, """Underneath, offline: embeddings for jobs and members, and an approximate nearest """
             """neighbour index rebuilt hourly. This is where the heavy computation lives, and it is """
             """why candidate generation can be ten milliseconds instead of three hours.""",
          A.flow([(305, 612), (360, 612), (505, 270)]))
A.narrate(7, """And the loop that makes it a recommender rather than a search engine: every impression, """
             """click, application and hire is logged, and models are trained on those outcomes. Note """
             """the loop is slow &mdash; hires take months to observe &mdash; which is the hardest """
             """thing about this system and worth saying out loud.""",
          A.flow([(722, 435), (722, 560), (1020, 270)]))
A.build()

sid = beat('Deep dive 1', 'Candidate generation &mdash; and why one source is not enough',
           '<div style="font-size:26px;line-height:1.65">'
           '<b>The job:</b> 10M &rarr; ~1,000, in ~10 ms, optimising for <b>recall</b>. A job that does '
           'not get generated can never be recommended, no matter how good your ranker is.<br><br>'
           '<b>Use several sources and union them &mdash; each has a different blind spot:</b><br>'
           '&bull; <b>Embedding similarity (ANN)</b> &mdash; member vector vs job vectors. Catches '
           'semantic matches a keyword search would miss. <span style="color:#ff9a9a">Blind to brand '
           'new jobs not yet embedded.</span><br>'
           '&bull; <b>Inverted index on skills/title/location</b> &mdash; precise, explainable, and '
           '<span style="color:#a8e6a3">instantly fresh</span>. Blind to semantic equivalence.<br>'
           '&bull; <b>Collaborative</b> &mdash; &ldquo;members like you applied to these&rdquo;. '
           'Strong signal. <span style="color:#ff9a9a">Cold-start fails for new members and new '
           'jobs.</span><br>'
           '&bull; <b>Graph</b> &mdash; jobs at companies where your connections work. Uniquely '
           'LinkedIn, and a strong engagement signal.<br><br>'
           '<span style="color:#ffd483">Each source covers another&rsquo;s blind spot. Union, '
           'deduplicate, and let the ranker sort it out &mdash; that is cheaper than making one source '
           'perfect.</span></div>',
           """Deep dive one: candidate generation. The job is ten million down to about a thousand in """
           """ten milliseconds, and it optimises for recall rather than precision &mdash; because a job """
           """that never gets generated can never be recommended, no matter how good your ranker """
           """is.""", step=0)
seg(sid, 1, """And the key point is to use several sources and union them, because each one has a """
            """different blind spot.""")
seg(sid, 2, """Embedding similarity with approximate nearest neighbour search: the member vector against """
            """job vectors. It catches semantic matches that keyword search misses &mdash; someone """
            """whose profile says &ldquo;distributed systems&rdquo; matching a job titled """
            """&ldquo;infrastructure engineer&rdquo;. Its blind spot is brand new jobs that have not """
            """been embedded yet.""")
seg(sid, 3, """An inverted index on skills, title and location: precise, explainable, and instantly """
            """fresh &mdash; which directly covers the embedding index's blind spot. Its own blind spot """
            """is semantic equivalence.""")
seg(sid, 4, """Collaborative filtering &mdash; members like you applied to these. A strong signal, and it """
            """fails on cold start for both new members and new jobs.""")
seg(sid, 5, """And a graph source: jobs at companies where your connections work. That one is uniquely """
            """LinkedIn, it is a strong engagement signal, and it is worth calling out because it uses """
            """an asset no competitor has.""")
seg(sid, 6, """Union them, deduplicate, and let the ranker sort it out. That is substantially cheaper """
            """than trying to make any single source perfect &mdash; and it is the general lesson of """
            """candidate generation: breadth from cheap diverse sources, precision from one expensive """
            """model afterwards.""")

sid = beat('Deep dive 2', 'Offline vs online, and the feature consistency trap',
           '<div style="font-size:26px;line-height:1.65">'
           '<b>What happens offline (hours):</b> embedding computation, ANN index build, model '
           'training, batch feature computation. <span style="color:#a8e6a3">Expensive, and it is why '
           'serving can be fast.</span><br><br>'
           '<b>What happens online (milliseconds):</b> ANN lookup, filters, feature fetch, inference, '
           're-rank.<br><br>'
           '<b>And the trap that breaks real recommenders &mdash; training/serving skew:</b><br>'
           'The model is trained on features computed by a <i>batch</i> job. At serving time, features '
           'are computed by <i>different code</i> on a different path. '
           '<span style="color:#ff9a9a">If &ldquo;days since last application&rdquo; is computed '
           'differently in the two places, the model sees inputs it was never trained on &mdash; and '
           'quality degrades silently.</span><br><br>'
           '<b>The fix is a feature store with one definition used by both paths:</b><br>'
           '&bull; Offline: materialise features for training<br>'
           '&bull; Online: serve the <i>same</i> features, from the <i>same</i> definition<br>'
           '&bull; <b>Point-in-time correctness</b> for training &mdash; use the feature value as it '
           'was <i>then</i>, not now, or you leak the future into training<br><br>'
           '<span style="color:#ffd483">That is what a feature store is actually for. It is not a '
           'cache &mdash; it is a consistency guarantee between two codebases.</span></div>',
           """Deep dive two: offline versus online, and the trap that breaks real recommenders in """
           """production.""", step=0)
seg(sid, 1, """Offline, over hours: embedding computation, nearest-neighbour index building, model """
            """training, batch feature computation. Expensive, and it is precisely why serving can be """
            """fast. The online path is only quick because the offline path did the work.""")
seg(sid, 2, """Online, in milliseconds: the nearest neighbour lookup, filters, feature fetch, inference """
            """and re-ranking.""")
seg(sid, 3, """And now the trap, which is called training-serving skew. The model is trained on features """
            """computed by a batch job. At serving time, features are computed by different code on a """
            """different path.""")
seg(sid, 4, """If &ldquo;days since last application&rdquo; is computed even slightly differently in """
            """those two places &mdash; a different rounding, a different timezone, a different """
            """handling of nulls &mdash; the model is seeing inputs it was never trained on. And """
            """quality degrades silently. There is no error, no alert, just worse recommendations that """
            """nobody can explain.""")
seg(sid, 5, """The fix is a feature store with one definition used by both paths: materialise features """
            """offline for training, serve the same features from the same definition online. And """
            """point-in-time correctness for training &mdash; when you build a training example from """
            """last March, you must use the feature value as it was in March, not as it is now, or you """
            """leak future information into training and your offline metrics look wonderful while """
            """production does not improve.""")
seg(sid, 6, """And that is what a feature store is actually for. It is not a cache. It is a consistency """
            """guarantee between two codebases, and describing it that way is a much better answer than """
            """naming it as a component.""")

tradeoff('Precompute recommendations, or compute on request', [
 ('Fully precompute per member, nightly', 'info',
  ['<b>Serving is a single lookup</b>', 'Unlimited compute budget &mdash; use the best model',
   'Trivially cheap at read time'],
  ['Stale &mdash; cannot react to what the member did five minutes ago',
   '<b>100M members &times; full ranking every night</b> is enormous and mostly wasted',
   'A job posted this morning cannot appear today']),
 ('Compute everything on request', 'shared',
  ['Always fresh', 'Reflects real-time signals immediately', 'Compute only for members who show up'],
  ['<b>Full funnel inside ~200 ms</b>', 'Expensive at 10,000 req/s',
   'Model complexity is capped by the latency budget']),
 ('Precompute candidates, rank on request', 'ok',
  ['Heavy lifting (embeddings, ANN index) offline', 'Ranking sees real-time signals',
   '<b>Compute only for members who actually visit</b>', 'Fresh jobs enter via the index rebuild'],
  ['Two systems to keep consistent', 'Index freshness bounds how new a job can be',
   'Feature skew risk between offline and online']),
], 'Precompute candidates and the index; rank on request. It is the only option that is both fresh and '
   'affordable, and it spends compute only on members who actually arrive.',
 'If this were a <b>push</b> notification rather than a browsed page, I would precompute everything '
 'offline &mdash; there is no latency budget to protect, so you may as well use the biggest model you '
 'can afford.',
 [
 """Trade-off: precompute recommendations per member, or compute on request? Full precomputation makes """
 """serving a single lookup with an unlimited compute budget, so you can use the best model you have. """
 """It is stale &mdash; it cannot react to what the member did five minutes ago &mdash; and ranking a """
 """hundred million members every night is enormous and mostly wasted, because most of them will not """
 """visit. And a job posted this morning cannot appear today.""",
 """Computing everything on request is always fresh, reflects real-time signals immediately, and only """
 """spends compute on members who actually show up. The cost is running the full funnel inside two """
 """hundred milliseconds at ten thousand requests a second, and your model complexity is capped by the """
 """latency budget.""",
 """Precomputing candidates and ranking on request puts the heavy lifting offline &mdash; embeddings """
 """and the index &mdash; while ranking still sees real-time signals, you only compute for members who """
 """visit, and fresh jobs enter through the index rebuild.""",
 """That is what I would build. It is the only option that is both fresh and affordable, and the """
 """point about spending compute only on members who actually arrive is worth saying &mdash; it is a """
 """large cost saving that falls out of the structure rather than from optimisation.""",
 """And what would flip it: if this were a push notification rather than a browsed page, I would """
 """precompute everything offline. There is no latency budget to protect, so you may as well use the """
 """biggest model you can afford &mdash; which is the same observation as the clarifying question """
 """about browse versus push.""",
])

failures('What happens when each piece dies', [
 ('Ranking model is slow or unavailable', 'Recommendations are worse but present',
  '<b>Hard timeout, fall back to a simpler model</b>, then to a heuristic ordering. Never let the '
  'model take out the page &mdash; same rule as the feed'),
 ('Feature store is slow', 'Latency budget blown, inference starves',
  'Batch the lookups, cache hot features locally, and <b>serve with defaults for missing features</b>. '
  'A model must tolerate nulls, which has to be a training-time decision'),
 ('ANN index rebuild fails', 'New jobs are not recommended &mdash; silently',
  '<b>Alert on index age, not on job success.</b> And keep the inverted index source, which is '
  'instantly fresh &mdash; multiple sources is a reliability property too'),
 ('A new member has no profile data', 'Nothing to recommend from &mdash; cold start',
  'Fall back to <b>popularity and location</b>. Say this explicitly: every recommender needs a '
  'cold-start answer and it is the first thing a new user experiences'),
 ('Training data is corrupted by a logging bug', 'Model degrades over weeks, invisibly',
  '<b>The scariest failure here.</b> Validate feature distributions before training; compare against '
  'the previous model offline; hold out a control group permanently'),
 ('The model learns a harmful bias', 'Systematically worse recommendations for a group',
  'Not a bug you can catch with uptime metrics. <b>Evaluate per-segment, not just in aggregate</b> '
  '&mdash; and for jobs this is a legal exposure, not only an ethical one'),
], [
 """Failures. Ranking model slow or unavailable: recommendations get worse but stay present. Hard """
 """timeout, fall back to a simpler model, then to a heuristic ordering. Never let the model take out """
 """the page &mdash; the same rule as the feed, and it is worth noticing that it recurs.""",
 """Feature store slow blows the latency budget. Batch the lookups, cache hot features locally, and """
 """serve with defaults for missing features. That last one matters: the model has to tolerate nulls, """
 """and that is a training-time decision, not something you can bolt on when the feature store is """
 """struggling.""",
 """Index rebuild fails and new jobs silently stop being recommended. Alert on index age rather than on """
 """job success. And here is where having multiple candidate sources pays off a second time &mdash; the """
 """inverted index is instantly fresh, so it covers for the embedding index being stale. Diversity of """
 """sources is a reliability property, not just a quality one.""",
 """A new member with no profile data is the cold start problem. Fall back to popularity and location, """
 """and say so explicitly &mdash; every recommender needs a cold-start answer, and it is the very first """
 """thing a new user experiences, so it deserves more thought than it usually gets.""",
 """Training data corrupted by a logging bug degrades the model over weeks, invisibly. I would call """
 """this the scariest failure in the system. Validate feature distributions before training, compare """
 """each new model against the previous one offline, and hold out a control group permanently so you """
 """can detect long-term drift.""",
 """And the model learning a harmful bias &mdash; systematically worse recommendations for some group. """
 """That is not a bug any uptime metric will catch. Evaluate per segment rather than only in aggregate. """
 """And for jobs specifically this is legal exposure in many jurisdictions, not only an ethical """
 """question, which is worth stating plainly.""",
])

say('What I should actually say in the room', [
 'Let me start with the constraint that shapes everything: 10 million jobs at about a millisecond of '
 'inference each is three hours per request. So I cannot score everything, and the architecture is a '
 'funnel.',
 'Candidate generation gets 10 million to about 1,000 in ten milliseconds, because that work is '
 'precomputed &mdash; embeddings and an ANN index built offline and rebuilt hourly.',
 'I would use several candidate sources rather than one: embeddings, an inverted index, collaborative '
 'filtering and the connection graph. Each covers another&rsquo;s blind spot, and that is also what '
 'keeps the system working when one of them is stale.',
 'Then hard filters &mdash; location, authorisation, already applied &mdash; take it to about 500, and '
 'the ranker scores those. 500 is affordable; 10 million is not.',
 'The hidden cost is features: 50 features across 500 candidates is 25,000 lookups per request, so that '
 'must be one batched call.',
 'And the trap I would call out is training/serving skew &mdash; if features are computed differently '
 'offline and online, the model sees inputs it was never trained on and degrades silently. That is what '
 'the feature store is for: it is a consistency guarantee between two codebases, not a cache.',
 'Finally I would ask what we are optimising for. Clicks give clickbait; hires are what the product is '
 'for, and that feedback loop is months long &mdash; which is the hardest thing about this system.',
], [
 """The sentences. Open with the three-hours number, because it converts the funnel from a choice into """
 """a necessity in one line.""",
 """Then candidate generation with the multiple-sources argument, the filter stage, and the hidden """
 """feature cost.""",
 """Then training-serving skew, framed as what a feature store is actually for &mdash; that framing """
 """will separate you from candidates who just name the component. And finish on the objective """
 """question, because it is the one that shows you understand what the product is for rather than how """
 """it is built.""",
])

followups([
 'How does candidate generation work?',
 'How do you filter?',
 'How do you rank?',
 'What is in the feature store?',
 'How does offline training work?',
 'How does online inference work?',
 'How do you use real-time signals?',
 'How do you cache?',
 'How do you keep jobs fresh?',
 'How do you partition?',
 'How do you evaluate?',
], [
 'A job gets 10,000 applicants. Is that success or failure?',
 'How do you handle a brand-new job with no interaction data?',
 'How do you know the model is better, given hires take months to observe?',
 'How would you detect and correct bias in these recommendations?',
 'What would you cut first if this cost had to halve?',
],
 """The reported follow-ups walk the whole pipeline. On real-time signals: the clean way is to keep """
 """them as features fetched at ranking time &mdash; what you searched for in this session, what you """
 """just dismissed &mdash; rather than rebuilding candidates, so the expensive offline work stays """
 """valid. On evaluation: offline metrics on held-out data for iteration speed, then online A-B tests """
 """for the truth, and hold out a permanent control group.""",
 """The staff-level follow-ups are the better questions. Ten thousand applicants for one job is a """
 """marketplace failure even though every member engaged &mdash; which is why you need two-sided """
 """objectives. A brand new job with no interaction data is cold start on the item side, handled by """
 """content-based candidate sources until behavioural signal accumulates. Knowing a model is better """
 """when hires take months means using proxy metrics with known correlation to hires, and being honest """
 """that they are proxies. Bias detection needs per-segment evaluation, and for jobs it is a legal """
 """question. And halving the cost &mdash; the honest answer is reduce the ranked candidate set from """
 """five hundred to two hundred, because ranking cost is linear in candidates and the quality loss is """
 """usually small.""")

cheatsheet('Job recommendations &mdash; the one-page card', [
 ('Requirements', 'Top 3 jobs from millions, personalised, qualification-filtered, reasonable latency'),
 ('Scale', '1B members, 100M DAU, ~2,300 req/s (10k peak), 10M open jobs. <b>Scoring all = 3 h per '
           'request</b>'),
 ('Core architecture', '<b>Funnel:</b> candidate generation (10M&rarr;1k) &rarr; filters (&rarr;500) '
                       '&rarr; ranker &rarr; re-rank &rarr; top 3. Offline: embeddings, ANN index, '
                       'training'),
 ('Data store', 'ANN index over job embeddings (~5 GB); feature store; interaction log for training'),
 ('Partition key', '<code>memberId</code> for features and history; job embeddings replicated for ANN '
                   'search'),
 ('Cache', 'Candidate sets per member for a short window; hot features locally. <b>Not final results '
           '&mdash; they must reflect session signals</b>'),
 ('Queue', 'Interaction events to the training pipeline; index rebuild jobs'),
 ('Consistency', 'Eventual throughout. Index freshness (~1 h) bounds how quickly a new job appears'),
 ('Failure handling', 'Timeout &rarr; simpler model &rarr; heuristic; alert on <b>index age</b>; '
                      'cold-start fallback to popularity + location'),
 ('Key deep dives', 'Multi-source candidate generation &middot; training/serving skew and the feature '
                    'store'),
 ('Biggest trade-off', 'Precompute vs compute-on-request &mdash; resolved by <b>precomputing '
                       'candidates and ranking live</b>'),
], [
 """The card. The scale row carries the number that justifies the architecture: scoring everything """
 """would be three hours per request.""",
 """The funnel is the architecture, written as one line. Partition features by member I-D; job """
 """embeddings are replicated because nearest-neighbour search needs them all.""",
 """Note the cache row &mdash; cache candidate sets, not final results, because the final ordering has """
 """to reflect what the member did in this session. Failure handling degrades through two levels. And """
 """the biggest trade-off is precompute versus compute on request, resolved by doing each where it """
 """belongs.""",
])

say('The 60-second answer', [
 'The constraint that shapes everything is arithmetic: ten million open jobs at about a millisecond of '
 'model inference each would be three hours per request. So scoring everything is impossible, and the '
 'architecture has to be a funnel.',
 'Candidate generation takes ten million down to about a thousand in roughly ten milliseconds, and it '
 'is fast only because the work already happened offline &mdash; embeddings and an approximate '
 'nearest-neighbour index, rebuilt hourly.',
 'I would use several candidate sources and union them: embedding similarity, an inverted index on '
 'skills and location, collaborative filtering, and the connection graph. Each covers another&rsquo;s '
 'blind spot &mdash; and that redundancy is also what keeps the system working when one source goes '
 'stale.',
 'Hard filters then cut it to around 500 &mdash; location, authorisation, already applied &mdash; and '
 'the ranking model scores those, which is affordable precisely because the earlier stages bought it '
 'the budget.',
 'The hidden cost is features: fifty features across five hundred candidates is twenty-five thousand '
 'lookups per request, so that has to be one batched call to a feature store.',
 'And the trap I would flag is training/serving skew &mdash; if a feature is computed differently in '
 'the training job and the serving path, the model sees inputs it never trained on and quality degrades '
 'silently. The feature store exists to prevent that; it is a consistency guarantee between two '
 'codebases, not a cache.',
], [
 """The sixty-second answer. The opening number does the work &mdash; it makes the funnel inevitable """
 """rather than a design preference.""",
 """The last sentence is the one that will distinguish you. Plenty of candidates will name a feature """
 """store; very few will say what it is actually for. Practise &ldquo;a consistency guarantee between """
 """two codebases, not a cache&rdquo; until it is fluent.""",
], kicker='60-second interview answer')
