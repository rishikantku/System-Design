# -*- coding: utf-8 -*-
"""Chapter 2, Lesson 2 — design typeahead / autosuggest."""
from lib import *

lesson_header('2.2', 'Design typeahead / autosuggest',
              'Prefix retrieval &middot; ranking &middot; a brutal latency budget',
              dict(reports='3 independent candidate reports',
                   latest='March 2026', level='Senior SWE / L5',
                   conf='HIGH &mdash; recurring', sources='Exponent &times;2, Glassdoor'), 34,
              """Chapter two, lesson two: typeahead. This is the most-reported system design question in our """
              """research — three independent candidate reports, the most recent from March twenty """
              """twenty-six — and it is also the most LinkedIn-shaped question in the set, because it is """
              """prefix retrieval over a people graph with personalised ranking. That is close to what the """
              """company actually builds. And it is the question where the latency budget, not the """
              """throughput, does all the deciding — which makes it a completely different exercise from """
              """the URL shortener we just did.""")

evidence('Where this question comes from', [
 ('Exponent &mdash; candidate report', '&asymp; Mar 2026', 'Senior SWE',
  'Asked to design TypeAhead. Discussion centred on <b>scalability, data structures, ranking of '
  'suggestions</b> and handling large traffic'),
 ('Exponent &mdash; question bank', '2026', 'SWE',
  'Autosuggest appears in the LinkedIn-tagged set'),
 ('Glassdoor &mdash; interview reports', '&asymp; 2025', 'Senior SWE',
  'Reported as &ldquo;typeahead for person search&rdquo;'),
], """The evidence, and this is the strongest in the whole set. Three independent sources. An Exponent """
     """candidate report from around March twenty twenty-six, where the discussion centred on """
     """scalability, data structures, ranking of suggestions and handling large traffic — note that """
     """ranking is called out explicitly, which tells you where the depth is expected.""",
 ["""It also appears in Exponent's LinkedIn-tagged question bank, and separately on Glassdoor, where it """
  """was described as typeahead for person search. Three sources, none of them copies of each other, """
  """and the phrasing differs — which is what makes them independent rather than one report echoed three """
  """times."""],
 caveat='Three reports makes this a strong preparation priority. It does not make it certain. '
        'Recent candidates have reported it; that is all we can honestly say.',
 narration_caveat="""Three independent reports makes this the strongest preparation priority we have. It """
                  """does not make it certain. Recent candidates have reported being asked it — that is """
                  """all anyone can honestly claim, and I would rather you prepared on evidence than on a """
                  """promise.""")

sid = beat('Why this is interesting', 'Throughput is easy. The budget is everything.',
           '<div style="font-size:29px;line-height:1.75">'
           'Typeahead looks like a search problem. It is really a <b>latency budget</b> problem with a '
           'search problem inside it.<br><br>'
           'Three things make it hard:<br><br>'
           '<b>1. The budget.</b> A suggestion that arrives after you have finished typing is worthless. '
           'Under ~100 ms or it did not happen.<br>'
           '<b>2. Every keystroke is a request.</b> The read volume is enormous relative to the number '
           'of actual searches.<br>'
           '<b>3. Ranking.</b> Prefix matching is easy; returning the <i>right ten</i> out of fifty '
           'thousand matches is the actual product.<br><br>'
           '<span style="color:#ffd483">The candidate who only builds a trie has solved the easy '
           'third.</span></div>',
           """Why is this interesting? Because typeahead looks like a search problem and is really a """
           """latency budget problem with a search problem inside it.""", step=0)
seg(sid, 1, """Three things make it hard. First, the budget: a suggestion that arrives after you have """
            """finished typing is worthless. It is not slow, it is useless — the product has failed even """
            """though the system returned a correct answer. Under roughly a hundred milliseconds or it did """
            """not happen.""")
seg(sid, 2, """Second, every keystroke is potentially a request, so read volume is enormous relative to the """
            """number of actual searches. And third, ranking: prefix matching is the easy part, but """
            """returning the right ten results out of fifty thousand matches is the actual product.""")
seg(sid, 3, """The candidate who builds a trie and stops has solved the easy third of this problem. The """
            """interesting two thirds are the budget and the ranking, and that is where we will spend our """
            """time.""")

think('Someone types "sa" into LinkedIn search. Fifty thousand people match that prefix. Which ten do you return — and how do you decide in under fifty milliseconds?',
      30,
      """Pause on this, because it is the question the whole design answers. Someone types s-a. Fifty """
      """thousand people match. Which ten do you return, and how do you decide inside fifty """
      """milliseconds? Say your approach out loud.""",
      """Hold that thought. The answer shapes the entire architecture, and we will get there — but first, """
      """what I would clarify.""")

clarify('What I would clarify first', [
 ('What are we suggesting &mdash; people, companies, jobs, or everything?',
  'People means a <b>personalised social graph</b> problem. Query strings mean a popularity problem. '
  'Completely different ranking, and different index sizes.'),
 ('Is the ranking personalised to the searcher?',
  'The biggest fork in the design. <b>Personalised means you cannot fully precompute the answer</b>, '
  'and a globally cached result no longer works.'),
 ('What p99 latency, and measured where &mdash; server or device?',
  'Server-side 50 ms is very different from end-to-end 50 ms on a mobile network. <b>Ask which.</b>'),
 ('How fresh must the index be? If I join LinkedIn now, when am I findable?',
  'Seconds means a streaming index path. Hours means a nightly batch build, which is far simpler.'),
 ('Do we fire on every keystroke, or debounce?',
  'Changes request volume by <b>3&ndash;5&times;</b>. Worth stating as an assumption, because it '
  'moves every capacity number.'),
 ('Typo tolerance?',
  'Fuzzy matching is a <b>much</b> bigger problem than prefix matching. If it is in scope, say so and '
  'budget for it; if not, park it explicitly.'),
], [
 """What are we suggesting — people, companies, jobs, or everything? People means a personalised social """
 """graph problem; query strings mean a popularity problem. Those have different ranking signals and """
 """very different index sizes, so this question comes first.""",
 """Is ranking personalised to the searcher? This is the biggest fork in the design. Personalised means """
 """you cannot fully precompute the answer, and a globally cached result stops working — so the """
 """architecture changes shape.""",
 """What p ninety-nine, and measured where? Server-side fifty milliseconds and end-to-end fifty """
 """milliseconds on a mobile network are wildly different asks. Always ask which, because the second one """
 """leaves you almost no server budget at all.""",
 """How fresh must the index be — if I join LinkedIn now, when am I findable? Seconds means a streaming """
 """index path. Hours means a nightly batch build, which is dramatically simpler. Getting this answer """
 """can save you half the system.""",
 """Do we fire on every keystroke or debounce? That changes request volume by three to five times, so """
 """state it as an assumption before you compute anything.""",
 """And typo tolerance. Fuzzy matching is a much bigger problem than prefix matching — different data """
 """structure, different cost. If it is in scope, budget for it. If not, park it explicitly rather than """
 """silently ignoring it.""",
])

capacity('Capacity — where the budget does the deciding', [
 ('100M DAU &times; 5 searches &times; 4 requests', '2B requests / day &divide; 100k s',
  '&asymp; 23,000 req / s', 'Throughput is high but horizontally scalable. <b>Not the hard part</b>'),
 ('Peak 3&times;', '23,000 &times; 3', '&asymp; 70,000 req / s peak',
  'A fleet of maybe 100&ndash;200 nodes. Each needs the index <b>locally</b> &mdash; see below'),
 ('100 ms end-to-end target', '&minus;40 ms mobile network &minus;10 ms LB/TLS',
  '<b>~50 ms server budget</b>', 'Everything &mdash; match, rank, serialise &mdash; fits in 50 ms'),
 ('One network hop under load', '0.5 ms RTT + queueing + p99 tail', '&asymp; 5&ndash;20 ms',
  'Affordable <b>once</b>. A scatter-gather over 20 shards waits for the <b>slowest</b> &mdash; not affordable'),
 ('Index: 1B members, ~50 B of name data', '1B &times; 50 B', '&asymp; 50 GB raw',
  'Too big for RAM per node&hellip; <b>unless you shrink it</b>'),
 ('Compressed FST + top-K per prefix only', 'keep 10 results / prefix, not all matches',
  '<b>&asymp; 5&ndash;8 GB</b>', '<b>Now it fits in RAM.</b> So replicate the index everywhere and '
  'never make a network call'),
], [
 """Let us run the numbers, and watch how differently they behave from the shortener. A hundred million """
 """daily actives, five searches each, a request on every fourth keystroke, is two billion requests a """
 """day — about twenty-three thousand a second. High, but throughput scales horizontally, so this is not """
 """the hard part. Say that out loud so the interviewer knows you have correctly identified what is """
 """easy.""",
 """Peak at three times is seventy thousand a second, which means a fleet of perhaps one to two hundred """
 """nodes. Hold that thought, because what each node needs locally is the crux.""",
 """Now the budget. A hundred millisecond end-to-end target, minus roughly forty milliseconds of mobile """
 """network, minus ten for load balancing and TLS, leaves about fifty milliseconds of server time for """
 """matching, ranking and serialisation.""",
 """What does a network hop cost inside that? Half a millisecond of raw round trip, but under real load """
 """with queueing and p ninety-nine tails, call it five to twenty milliseconds. So you can afford one """
 """hop. And critically, a scatter-gather across twenty shards does not cost one hop — it costs the """
 """slowest of twenty, which at p ninety-nine is much worse than the average. That single observation """
 """eliminates the sharded-index architecture most candidates draw.""",
 """So look at index size. A billion members at roughly fifty bytes of name data is about fifty """
 """gigabytes. Too big to hold in RAM on every node — unless you shrink it.""",
 """And you can. Store a compressed finite state transducer, and keep only the top ten results per """
 """prefix rather than every match. That gets you to five to eight gigabytes, which fits comfortably in """
 """RAM. So: replicate the index to every node and never make a network call on the read path at all. """
 """That is the central decision of this design, and it came directly out of comparing two numbers.""",
], note='The shortener was decided by <b>read volume</b>. This one is decided by the <b>latency '
        'budget</b> &mdash; and the budget says: no network hop, so the index must be local, so the '
        'index must be small enough to replicate.')

sid = beat('The key insight', 'Replicate the index. Do not shard it.',
           '<div class="bigidea">Sharding an index is the reflex. Here it is <b>wrong</b>, and the '
           'reason is p99, not throughput.</div>'
           '<div style="margin-top:26px;font-size:28px;line-height:1.7">'
           '<b>Sharded:</b> query hits 20 shards, wait for the slowest. If each shard is 10 ms at p99, '
           'the <i>fan-out</i> p99 is far worse &mdash; you have taken 20 draws from the tail.<br><br>'
           '<b>Replicated:</b> query hits one node, which has everything in memory. <b>No network, no '
           'tail amplification.</b><br><br>'
           'This works only because the index is <b>small</b> (single-digit GB) and <b>read-only</b> '
           'between rebuilds.<br><br>'
           '<span style="color:#ffd483">Say this: &ldquo;I am replicating rather than sharding, '
           'because fan-out multiplies the tail and I have a p99 budget, not an average '
           'budget.&rdquo;</span></div>',
           """Let me make the key insight explicit, because it is the thing that will distinguish your """
           """answer. Sharding an index is the reflex — big data, so split it. Here it is wrong, and the """
           """reason is p ninety-nine, not throughput.""", step=0)
seg(sid, 1, """If you shard across twenty nodes, every query fans out and waits for the slowest response. """
            """Even if each shard is a well-behaved ten milliseconds at p ninety-nine, the fan-out's p """
            """ninety-nine is much worse, because you have taken twenty independent draws from the tail """
            """and kept the worst one. This is tail amplification, and it is one of the most useful """
            """concepts you can bring into an infrastructure interview.""")
seg(sid, 2, """Replicated: the query hits one node which has everything in memory. No network hop, no tail """
            """amplification. And this only works because we made the index small — single-digit """
            """gigabytes — and because it is read-only between rebuilds, so replication is cheap and """
            """consistency is a non-issue.""")
seg(sid, 3, """The sentence to say is: I am replicating rather than sharding, because fan-out multiplies """
            """the tail and I have a p ninety-nine budget rather than an average budget. That one sentence """
            """demonstrates you understand percentiles, fan-out, and the difference between throughput and """
            """latency — three things at once.""")

sid = beat('Data model', 'What actually lives in the index',
           '<div style="font-size:27px;line-height:1.65">'
           'Not &ldquo;a trie of all names&rdquo;. What you store is <b>precomputed answers</b>:'
           '<br><br>'
           '<span style="font-family:JetBrains Mono,monospace;font-size:23px;color:#9fb4cc">'
           'prefix &rarr; [ (entity_id, base_score), &times;10 ]</span><br><br>'
           'So <code>"sa"</code> maps to the <b>ten globally best</b> matches, already ranked, already '
           'truncated.<br><br>'
           '<b>Why this and not a trie walk?</b><br>'
           '&bull; A trie walk on <code>"sa"</code> visits 50,000 nodes, then sorts them. That is the '
           '50 ms budget gone.<br>'
           '&bull; A hash lookup on <code>"sa"</code> is <b>one memory access</b>.<br><br>'
           '<span style="color:#ffd483">Trade: you precompute at build time so you do almost nothing at '
           'query time. Storage is cheap; the budget is not.</span></div>',
           """The data model, and this is where candidates who have only read about tries go wrong. What """
           """you store is not a trie of all names. What you store is precomputed answers: a map from """
           """prefix to the ten best matches, already ranked and already truncated.""", step=0)
seg(sid, 1, """Why? Because a trie walk on the prefix s-a visits fifty thousand nodes and then has to sort """
            """them by score. That is your fifty millisecond budget gone, on one query. Whereas a hash """
            """lookup on the string s-a is a single memory access.""")
seg(sid, 2, """So the trade is: do the work at build time so you do almost nothing at query time. Storage is """
            """cheap, the latency budget is not — and recognising which resource is scarce is the whole """
            """job. A trie is still useful underneath for the build process and for prefix enumeration, """
            """but it is not what serves the query.""")

# ------------------------------------------------------------------ architecture
A = Arch('Architecture — the read path is deliberately tiny', kicker='Progressive disclosure', height=800)
A.box('cl',   70, 340, 170, 100, 'Client', 'debounced', kind='neutral', step=0, focus=0)
A.box('edge', 300, 340, 200, 100, 'Edge / LB', kind='info', step=0, focus=0)
A.arrow('cl', 'edge', step=0, focus=0)
A.box('sug',  560, 340, 230, 110, 'Suggest service', 'index in-process', kind='ok', step=0, focus=[0, 1])
A.arrow('edge', 'sug', step=0, focus=0)

A.box('l1',   560, 190, 230, 80, 'Head cache', 'top 10k prefixes', kind='ok', step=1, focus=1, small=True)
A.arrow('sug', 'l1', step=1, focus=1, dashed=True)

A.box('pers', 850, 340, 220, 110, 'Personalisation', 'connections, recency', kind='shared',
      step=2, focus=2)
A.arrow('sug', 'pers', step=2, focus=2, dashed=True)

A.zone(540, 150, 550, 330, 'One node. No network on the read path.', kind='ok', step=3, dashed=True)

A.box('bld',  560, 570, 230, 90, 'Index builder', 'batch, hourly', kind='dp', step=4, focus=4, small=True)
A.box('src',  250, 570, 230, 90, 'Member data', 'source of truth', kind='shared', step=4, focus=4, small=True)
A.arrow('src', 'bld', step=4, focus=4)
A.arrow('bld', 'sug', step=4, focus=4, dashed=True, ts='b', fs='t')

A.box('str',  880, 570, 210, 90, 'Change stream', 'new members', kind='dp', step=5, focus=5, small=True)
A.arrow('str', 'sug', step=5, focus=5, dashed=True)

A.note(1150, 200, '**The read path is:**\\n'
                  'edge &rarr; one node &rarr; memory.\\n\\n'
                  'Everything else &mdash; building,\\n'
                  'updating, personalising &mdash;\\n'
                  'happens **off** that path.\\n\\n'
                  '<b>That is the design.</b>',
       step=6, kind='ok', w=520, size='l')
A.narrate(0, """The architecture, built up. Client — debounced, so we are not firing on every character. """
              """Edge and load balancer. Then the suggest service, which holds the index in its own """
              """process memory. Notice how short that path already is.""")
A.narrate(1, """In front of the index, a tiny head cache for the top ten thousand prefixes. We computed """
              """that as about twenty megabytes, and it covers roughly half of all traffic — because """
              """prefix popularity is enormously skewed. Half your traffic now never touches the index at """
              """all.""")
A.narrate(2, """Then personalisation, which is the part that makes this LinkedIn rather than a dictionary """
              """lookup. It re-ranks the ten global candidates using the searcher's connections and """
              """recent activity. Crucially it re-ranks ten items, not fifty thousand — so it is """
              """affordable inside the budget.""")
A.narrate(3, """And here is the thing to point at deliberately: everything inside this boundary is one """
              """node, with no network call on the read path. That is what buys the p ninety-nine.""")
A.narrate(4, """Off the read path, an index builder takes member data and produces the prefix-to-top-ten """
              """map on a schedule — hourly, say. It is a batch job. It can be slow. Nobody is waiting on """
              """it.""")
A.narrate(5, """And for freshness, a change stream applies new and updated members incrementally between """
              """full builds, so a member who joins is findable in seconds rather than at the next """
              """rebuild.""")
A.narrate(6, """Step back and look at the shape. The read path is edge, one node, memory. Everything else — """
              """building, updating, personalising — happens off that path or on ten items. When you """
              """present this, say exactly that: the design is about what I kept off the read path.""")
A.build()

# ------------------------------------------------------------------ ranking deep dive
sid = beat('Deep dive 1', 'Ranking — the part that is actually the product',
           '<div style="font-size:28px;line-height:1.68">'
           'Fifty thousand people match <code>"sa"</code>. Ten slots. The ranking decides whether this '
           'feels magical or useless.<br><br>'
           '<b>Two-stage ranking</b>, and the split is the whole trick:<br><br>'
           '<b>Stage 1 &mdash; offline, at build time.</b> Score every entity globally: profile '
           'completeness, connection count, activity, how often this prefix leads to a click on them. '
           'Keep the <b>top 10 per prefix</b>.<br><br>'
           '<b>Stage 2 &mdash; online, at query time.</b> Re-rank those 10 using searcher context: '
           'is this a 1st-degree connection? Same company? Recently viewed?<br><br>'
           '<span style="color:#ffd483">Expensive global scoring happens once per build. Cheap '
           'personal scoring happens on 10 items. <b>That is how you fit ranking into 50 ms.</b></span></div>',
           """Deep dive one: ranking, which is the part that is actually the product. Fifty thousand people """
           """match s-a and you have ten slots. Whether this feels magical or useless is entirely a """
           """ranking question.""", step=0)
seg(sid, 1, """The technique is two-stage ranking, and the split between the stages is the whole trick. """
            """Stage one happens offline at build time: score every entity globally using profile """
            """completeness, connection count, activity, and — the strongest signal — how often this """
            """prefix historically leads to a click on this person. Keep the top ten per prefix.""")
seg(sid, 2, """Stage two happens online at query time: take those ten and re-rank them using the searcher's """
            """context. Is this a first-degree connection? Same company? Someone they viewed last week? """
            """A first-degree connection should almost always outrank a stranger with a bigger network.""")
seg(sid, 3, """And notice the economics, because this is the insight: expensive global scoring happens once """
            """per build across the whole corpus. Cheap personal scoring happens on ten items, per query. """
            """That is how you fit ranking inside fifty milliseconds. If you tried to personalise fifty """
            """thousand candidates per keystroke you would need a different product.""")

tradeoff('The personalisation trade-off', [
 ('Personalise nothing', 'deny',
  ['Fully cacheable &mdash; one global answer per prefix', 'Simplest possible system', 'Lowest cost'],
  ['A first-degree connection ranks below a stranger with more followers',
   '<b>On a social network this is a bad product</b>']),
 ('Personalise the top 10', 'ok',
  ['Connections and recency dominate, as they should', 'Cost is bounded: 10 items, in memory',
   'Head cache still works for the <b>global</b> candidates'],
  ['Final result is per-user, so <b>it cannot be cached globally</b>',
   'Needs the searcher&rsquo;s connection set available fast']),
 ('Personalise the full candidate set', 'deny',
  ['Theoretically the best ranking'],
  ['50,000 scorings per keystroke &mdash; <b>impossible in 50 ms</b>',
   'Requires the whole graph on the query path']),
], decision='Personalise the top 10. The global stage does the heavy lifting offline; the personal '
            'stage is bounded work on a tiny candidate set.',
 flip='If this were suggesting <i>search queries</i> rather than people, I would personalise nothing '
      'and cache globally &mdash; popularity is the right signal for query strings, and the caching '
      'win is enormous.',
 narration=[
  """The trade-off, laid out properly. Personalise nothing: fully cacheable, one global answer per """
  """prefix, simplest and cheapest. But a first-degree connection ranks below a stranger with more """
  """followers, and on a social network that is simply a bad product — users will notice immediately.""",
  """Personalise the top ten: connections and recency dominate as they should, the cost is bounded """
  """because it is ten items already in memory, and the head cache still works for the global candidate """
  """stage. The cost is that the final result is per-user, so it cannot be cached globally, and you need """
  """the searcher's connection set available fast.""",
  """Personalise the full candidate set: theoretically the best ranking, and completely impossible — """
  """fifty thousand scorings per keystroke inside fifty milliseconds, requiring the social graph on the """
  """query path. Name it and dismiss it; showing you considered and rejected the maximal option is """
  """better than not mentioning it.""",
  """So: personalise the top ten. And the reversal, which is a genuinely interesting one — if this were """
  """suggesting search queries rather than people, I would personalise nothing and cache globally, """
  """because popularity is the right signal for query strings and the caching win is enormous. Same """
  """question, different entity type, opposite answer.""",
 ])

sid = beat('Deep dive 2', 'Index freshness — batch plus stream',
           '<div style="font-size:28px;line-height:1.7">'
           'The index is a <b>read-only artefact</b>. That is what makes it fast &mdash; and it is also '
           'the freshness problem.<br><br>'
           '<b>Full rebuild</b>, hourly: recompute global scores, rebuild the prefix map, produce a new '
           'immutable artefact, distribute it, nodes swap atomically.<br><br>'
           '<b>Incremental overlay</b>, seconds: a change stream of new and updated members applies to '
           'a small in-memory delta layer that is consulted <i>alongside</i> the base index.<br><br>'
           'Query = merge(base index, delta). The delta stays small because it is discarded at every '
           'rebuild.<br><br>'
           '<span style="color:#ffd483">This is the standard shape for every near-real-time search '
           'system: <b>an immutable base plus a small mutable overlay.</b> Name it and you sound like '
           'you have built one.</span></div>',
           """Deep dive two: freshness. The index is a read-only artefact, and that is exactly what makes """
           """it fast — no locking, no concurrent mutation, perfect for replication. It is also the """
           """freshness problem, because a read-only thing is stale the moment it is built.""", step=0)
seg(sid, 1, """So two paths. A full rebuild, hourly: recompute global scores, rebuild the prefix map, """
            """produce a new immutable artefact, distribute it, and have nodes swap atomically. Atomic """
            """swap matters — you never want a node serving half an old index and half a new one.""")
seg(sid, 2, """And an incremental overlay, in seconds: a change stream of new and updated members applies """
            """to a small in-memory delta layer, consulted alongside the base index. The query becomes a """
            """merge of base and delta, and the delta stays small because it is discarded at every """
            """rebuild.""")
seg(sid, 3, """This immutable-base-plus-mutable-overlay shape is the standard structure of every """
            """near-real-time search system — it is essentially how Lucene segments work. Naming that """
            """pattern tells an interviewer you have worked with one rather than read about one.""")

failures('What happens when each piece dies', [
 ('One suggest node', 'Nothing &mdash; the load balancer routes elsewhere',
  'Stateless apart from the index, which every other node also has. <b>Replication is the redundancy</b>'),
 ('Head cache', 'Slightly more work per query',
  'Falls through to the in-memory index. <b>No external dependency, so no cliff</b>'),
 ('Personalisation data unavailable', 'Results are less relevant, but <b>still returned</b>',
  '<b>Degrade to global ranking.</b> This is the single most important failure behaviour here'),
 ('Index builder fails', 'Nothing for hours &mdash; the current index keeps serving',
  'Alert on <b>index age</b>, not on job failure. You have hours of headroom, so this is not a page'),
 ('Change stream lags', 'New members are not findable for a while',
  'Degraded freshness, not an outage. Alert on stream lag'),
 ('A bad index is built and shipped', '<b>Results go wrong everywhere at once</b>',
  'The real risk. <b>Validate before distributing</b>: result-count and golden-query checks, then '
  'canary it to 1% of nodes'),
], [
 """The failure table. One suggest node dying is invisible — the load balancer routes elsewhere, and """
 """because every node holds the full index, replication is already the redundancy. That is a pleasant """
 """consequence of the replicate-don't-shard decision, and worth pointing out.""",
 """The head cache dying just means slightly more work per query, falling through to the in-memory """
 """index. There is no external dependency, so there is no cliff — unlike the URL shortener, where the """
 """cache failing was genuinely dangerous.""",
 """Personalisation data being unavailable is the important one. Results become less relevant but are """
 """still returned — you degrade to global ranking. That graceful degradation is the single most """
 """important failure behaviour in this design, and I would volunteer it: the system should get worse, """
 """not unavailable.""",
 """The index builder failing means nothing happens for hours, because the current index keeps serving. """
 """So alert on index age rather than on job failure — you have hours of headroom and it is not worth a """
 """page at three in the morning.""",
 """Change stream lag means new members are not findable for a while: degraded freshness, not an """
 """outage.""",
 """And the real risk, which most candidates never mention: a bad index gets built and shipped, and """
 """results go wrong everywhere simultaneously because every node has the same artefact. The very thing """
 """that made you resilient to node failure makes you vulnerable to bad data. So validate before """
 """distributing — result-count checks and golden queries — and canary the new index to one percent of """
 """nodes first. Naming that inversion is a strong Staff-level observation.""",
])

sid = beat('Observability, security, cost', 'Short, sharp, and specific to this system',
           '<div class="to-grid" style="top:24px">'
           '<div class="to-opt k-info" data-step="0"><div class="to-h">What I would alert on</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; <b>p99 latency</b> &mdash; the product <i>is</i> the budget<br>'
           '&bull; <b>Index age</b> &mdash; leading indicator, hours of warning<br>'
           '&bull; <b>Empty-result rate</b> &mdash; catches a bad index build instantly<br>'
           '&bull; Head cache hit ratio<br>'
           '&bull; Change-stream lag<br><br>'
           '<span style="color:#ffd483">Business metric: <b>click-through on suggestions</b>. '
           'A ranking regression shows up here <i>before</i> anywhere else.</span></div></div>'
           '<div class="to-opt k-shared" data-step="1"><div class="to-h">Security &amp; abuse</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; <b>Scraping is the real threat</b>: walk every two-letter prefix and you have '
           'harvested a chunk of the member base<br>'
           '&bull; Rate limit per account <i>and</i> per IP<br>'
           '&bull; Respect visibility: never suggest someone who has <b>blocked</b> the searcher<br>'
           '&bull; Privacy filters applied <b>at query time</b>, not build time &mdash; they are '
           'per-viewer</div></div>'
           '<div class="to-opt k-ok" data-step="2"><div class="to-h">Cost</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; Dominated by <b>RAM across the fleet</b>: 8 GB &times; 200 nodes<br>'
           '&bull; Biggest lever: <b>shrink the index</b> &mdash; fewer results per prefix, shorter '
           'max prefix length<br>'
           '&bull; Second lever: debounce harder on the client &mdash; free, and cuts requests '
           '30&ndash;50%<br><br>'
           '<span style="color:#ffd483">The cheapest optimisation is on the <b>client</b>.</span></div></div></div>',
           """Observability: alert on p ninety-nine, because here the product literally is the budget. """
           """Alert on index age as a leading indicator. And alert on empty-result rate, which catches a """
           """bad index build within seconds — it is the fastest possible detector for the failure we just """
           """discussed.""", step=0)
seg(sid, 1, """And name a business metric: click-through rate on suggestions. A ranking regression shows up """
            """there before it shows up in any systems metric, because the system is perfectly healthy """
            """while returning useless results. Connecting a systems design to a product metric is a """
            """senior instinct.""")
seg(sid, 2, """Security, and here the real threat is not what candidates usually say. It is scraping: walk """
            """every two-letter prefix and you have harvested a meaningful chunk of the member base. So """
            """rate limit per account and per IP. Respect visibility rules — never suggest someone who has """
            """blocked the searcher. And note that privacy filters must be applied at query time rather """
            """than build time, because they are per-viewer. That is a real constraint that interacts with """
            """the precomputed index, and spotting it is the kind of thing that gets remembered.""")
seg(sid, 3, """Cost is dominated by RAM across the fleet — eight gigabytes times a couple of hundred nodes. """
            """The biggest lever is shrinking the index: fewer results per prefix, shorter maximum prefix """
            """length. The second lever is debouncing harder on the client, which is free and cuts """
            """requests by thirty to fifty percent. Worth saying plainly: the cheapest optimisation in """
            """this entire system is on the client, not the server.""")

sid = cards('Staff-level follow-ups', [
 (0, '&ldquo;p99 must be 30 ms, not 100 ms.&rdquo;',
  'Server budget drops to ~10 ms. Personalisation is now too expensive per query &mdash; precompute per-user candidates for <b>active users only</b>, and fall back to global for everyone else. Or push the index to the <b>edge</b>.', 'ok'),
 (0, '&ldquo;Support typo tolerance.&rdquo;',
  'Different structure entirely: n-gram index or a BK-tree, or precompute common misspellings. <b>Do not pretend a trie does fuzzy matching.</b> Say it costs budget and ask whether it beats ranking improvements.', 'ok'),
 (1, '&ldquo;The index no longer fits in memory.&rdquo;',
  'First shrink it: fewer results per prefix, cap prefix length, better compression. Only if that fails, <b>shard by prefix range</b> and accept the tail cost &mdash; and say that is the trade you are making.', 'ok'),
 (1, '&ldquo;Ten times the traffic.&rdquo;',
  'Add nodes. The index is replicated, so scaling is linear and nothing structural changes. <b>The build pipeline does not scale with query traffic at all</b> &mdash; only with corpus size.', 'ok'),
 (2, '&ldquo;Make results fresh within one second.&rdquo;',
  'The overlay already does most of this. The limit is change-stream lag, not the design. Below ~1 s you are writing to a shared mutable structure on the read path &mdash; and <b>that costs you the p99</b>.', 'shared'),
 (2, '&ldquo;Launch in a new region.&rdquo;',
  'Genuinely easy here: the index is read-only, so <b>ship the artefact</b> and serve locally. No cross-region consistency problem at all &mdash; which is a direct dividend of the immutability decision.', 'ok'),
], cols=2)
seg(sid, 0, """Staff-level follow-ups. Tighten p ninety-nine to thirty milliseconds and your server budget """
            """drops to about ten. Personalisation becomes too expensive per query, so you precompute """
            """per-user candidates for active users only and fall back to global for everyone else — or """
            """you push the index to the edge. Both are real answers; pick one and price it.""")
seg(sid, 1, """Typo tolerance needs a different structure entirely: an n-gram index, a BK-tree, or """
            """precomputed common misspellings. Do not pretend a trie does fuzzy matching. And the senior """
            """move is to ask whether typo tolerance actually beats spending the same budget on better """
            """ranking — often it does not.""")
seg(sid, 2, """The index no longer fitting in memory: shrink it first, by keeping fewer results per prefix """
            """and capping prefix length. Only if that fails do you shard by prefix range, and when you do, """
            """say explicitly that you are accepting tail amplification in exchange for capacity. Naming """
            """the cost of your own fallback is the mark of someone who understands it.""")
seg(sid, 3, """Ten times the traffic: add nodes. The index is replicated so scaling is linear, and nothing """
            """structural changes. Add the observation that the build pipeline does not scale with query """
            """traffic at all — it scales with corpus size. Separating those two axes is exactly the kind """
            """of clarity this round rewards.""")
seg(sid, 4, """One-second freshness: the overlay already does most of it, and the limit is stream lag rather """
            """than your design. Below about a second you are writing to a shared mutable structure on the """
            """read path, and that costs you the p ninety-nine you spent the whole design protecting.""")
seg(sid, 5, """And launching in a new region, which is genuinely easy here: the index is read-only, so you """
            """ship the artefact and serve locally. There is no cross-region consistency problem at all. """
            """That is a direct dividend of the immutability decision you made forty minutes earlier, and """
            """pointing out that connection is a lovely way to close.""")

followups(
 ['Ranking and personalisation &mdash; <b>explicitly reported</b>',
  'Index build and refresh cadence',
  'Latency budget end to end',
  'Typo tolerance'],
 ['"Why replicate instead of shard?" &mdash; tail amplification',
  '"How do you keep it fresh without slowing the read path?"',
  '"What happens if you ship a bad index?"',
  '"How do you stop someone scraping your member base?"',
  '"Now make it 30 ms"'],
 """The reported follow-ups, from the candidate accounts: ranking and personalisation — which was called """
 """out explicitly in the March twenty twenty-six report — index build and refresh, the end-to-end """
 """latency budget, and typo tolerance.""",
 """And these are the ones I would expect on top, based on where this design has real tension. Why """
 """replicate rather than shard, which is your tail amplification answer. How you stay fresh without """
 """touching the read path. What happens when you ship a bad index — the failure that replication makes """
 """worse rather than better. How you stop scraping. And the thirty-millisecond squeeze.""")

say('What I should say — the sentences that carry this design', [
 'Before I design: are we suggesting people or query strings, and is the ranking personalised to the searcher? Those two answers change the architecture more than the scale does.',
 'Throughput here is about seventy thousand a second at peak, which is high but horizontally scalable — so throughput is not the hard part. The latency budget is.',
 'A hundred milliseconds end to end, minus mobile network and TLS, leaves me about fifty milliseconds of server time. That is the number I am designing against.',
 'A fan-out across twenty shards means waiting for the slowest of twenty, so the tail gets much worse. I would rather replicate the index than shard it.',
 'The index compresses to single-digit gigabytes if I keep only the top ten results per prefix, so it fits in RAM on every node and the read path never makes a network call.',
 'Ranking is two-stage: expensive global scoring offline at build time, cheap personal re-ranking of ten items at query time. That is how ranking fits in the budget.',
 'If personalisation data is unavailable, I return global results rather than failing — the system should get worse, not unavailable.',
 'The risk I would watch is shipping a bad index, because every node has the same one. So I would validate and canary before distributing.',
], [
 """Eight sentences to drill for this question. The first is the clarification that matters most, and """
 """notice it claims that the entity type and personalisation matter more than the scale does — which is """
 """true and slightly counterintuitive.""",
 """The second dismisses throughput explicitly, which redirects the conversation to where the difficulty """
 """is. The third computes the budget out loud, which most candidates never do.""",
 """The fourth is your tail amplification argument — this is the single most impressive sentence """
 """available in this question. The fifth is the arithmetic that makes replication possible.""",
 """The sixth explains two-stage ranking as an economic decision rather than a technique.""",
 """The seventh is graceful degradation stated as a principle. And the eighth names your own biggest """
 """risk and the fact that it is caused by your own best decision — which is exactly the kind of """
 """self-aware reasoning that reads as Staff level.""",
])

cheatsheet('Typeahead — the revision card', [
 ('Problem', 'Prefix &rarr; 10 ranked suggestions, under 100 ms end to end'),
 ('Evidence', '3 independent reports &middot; most recent Mar 2026'),
 ('Scale', '~23k req/s avg &middot; ~70k peak &middot; 1B entities'),
 ('Dominant constraint', '<b>The latency budget</b>, not throughput'),
 ('Server budget', '~50 ms after network and TLS'),
 ('Key decision', '<b>Replicate the index, do not shard</b> &mdash; fan-out multiplies the tail'),
 ('Index', 'prefix &rarr; top-10, compressed FST, 5&ndash;8 GB, in-process'),
 ('Why not a trie walk', '50k nodes visited then sorted &mdash; the budget is gone'),
 ('Ranking', 'Two-stage: global offline, personal on 10 items online'),
 ('Cache', 'Top 10k prefixes &asymp; 20 MB &asymp; half of all traffic'),
 ('Freshness', 'Hourly rebuild + seconds-level delta overlay'),
 ('Consistency', 'Staleness is fine. Index is immutable between builds'),
 ('Degradation', 'No personalisation data &rarr; <b>global results, not an error</b>'),
 ('Failure to watch', 'A bad index shipped everywhere at once'),
 ('Alert on', 'p99, index age, <b>empty-result rate</b>, CTR'),
 ('Security', 'Scraping via prefix enumeration; per-viewer privacy at query time'),
 ('Cost', 'RAM &times; fleet. Cheapest lever is client-side debounce'),
 ('10&times; traffic', 'Add nodes &mdash; linear, nothing structural'),
 ('New region', 'Ship the read-only artefact. No consistency problem'),
 ('Biggest risk', 'Bad index build &rarr; validate, then canary'),
], [
 """The revision card. Problem, evidence, scale — and the dominant constraint, which is the budget """
 """rather than the throughput.""",
 """The key decision with its reason: replicate rather than shard, because fan-out multiplies the tail. """
 """The index structure and why a trie walk does not work.""",
 """Two-stage ranking, the head cache and what fraction it covers, and the freshness mechanism.""",
 """Then the operational half: what degrades and how, the failure to watch for, what to alert on — """
 """including empty-result rate, which is the fast detector — and the security threat that is specific """
 """to this system.""",
 """Cost, the ten-times answer, the new-region dividend, and your biggest risk. If you can rebuild this """
 """design from these twenty lines, you are ready. Next lesson: the metrics platform, which is the """
 """write-heavy shape and the question whose evidence we upgraded during research.""",
])

sid = statement('Lesson 2.2', 'The budget chooses the architecture.',
                'Every decision here — replicate not shard, precompute not traverse, rank in two stages — came from one number: fifty milliseconds of server time.',
                kind='ok')
seg(sid, 0, """One line to close. The budget chooses the architecture.""")
seg(sid, 1, """Every single decision in this design came from one number. Replicate rather than shard, """
            """precompute rather than traverse, rank in two stages, keep personalisation to ten items — """
            """all of it falls out of having fifty milliseconds of server time. Compute the budget early """
            """and the design argues for itself. Next: the metrics platform, where the numbers are two """
            """orders of magnitude larger and the thing that kills you is not throughput at all.""")
