# -*- coding: utf-8 -*-
"""Chapter 3, Lesson 1 — design a distributed search index."""
from lib import *

lesson_header('3.1', 'Design a distributed search index',
              'Inverted index &middot; sharding &middot; scatter-gather &middot; near-real-time',
              dict(reports='1 first-hand report, with real detail',
                   latest='12 May 2025', level='Staff Engineer',
                   conf='HIGH', sources='Taro &mdash; Staff loop, India'), 30,
              """Chapter three: distributed infrastructure. These are the three remaining questions with """
              """high-confidence evidence, and they are the ones closest to the round you are actually """
              """sitting — candidates describe the infrastructure design interview as going lower down """
              """the stack than a product design round. We start with distributed search: build an """
              """inverted index across many machines. And here is why this lesson follows typeahead """
              """deliberately. Typeahead taught you to avoid fan-out. This question forces you to embrace """
              """it. Same company, same domain, opposite conclusion — and understanding why is the whole """
              """lesson.""")

evidence('Where this question comes from', [
 ('Taro &mdash; Staff Engineer loop', '12 May 2025', 'Staff Engineer',
  'Asked to design a <b>distributed inverted index / search system</b>, Elasticsearch-like. '
  'Follow-ups: index sharding and replication, near-real-time indexing, query fan-out and merge, '
  'and ranking'),
], """The evidence. One first-hand report, from a Staff Engineer loop in May twenty twenty-five, with """
     """genuine detail: designing a distributed inverted index, Elasticsearch-like, with follow-ups on """
     """sharding and replication, near-real-time indexing, query fan-out and merge, and ranking.""",
 ["""One report is weaker than three, and I will not inflate it. What raises my confidence is the """
  """detail — the follow-ups listed are specific and technically coherent, which is what a real """
  """recollection looks like rather than a summary of a blog post. And search is core LinkedIn """
  """engineering, so it is a natural question for them to ask."""],
 caveat='Single-source. Treat it as a strong preparation topic rather than a likely question &mdash; '
        'and note it shares most of its machinery with typeahead, which has three reports.',
 narration_caveat="""Treat it as a strong preparation topic rather than a likely question. And note """
                  """something practical: it shares most of its machinery with typeahead, which does """
                  """have three reports. So preparing this costs you less than it looks, because half """
                  """of it is already paid for.""")

sid = beat('Why this is interesting', 'The opposite conclusion to the last lesson',
           '<div class="bigidea">Typeahead: the index was small, so <b>replicate it</b> and never fan '
           'out.<br>Search: the index is large, so you <b>must</b> fan out &mdash; and now you own the '
           'tail.</div>'
           '<div style="margin-top:26px;font-size:28px;line-height:1.7">'
           'Three things make full-text search hard that prefix suggestion does not:<br><br>'
           '<b>1. The index does not fit on one machine.</b> Full text over a billion documents is '
           'terabytes, not gigabytes.<br>'
           '<b>2. Queries have multiple terms.</b> You intersect posting lists, and the cost depends '
           'on the <i>rarest</i> term.<br>'
           '<b>3. Ranking needs corpus-wide statistics</b> &mdash; but each shard only sees its own '
           'slice. That tension is the deep dive.<br><br>'
           '<span style="color:#ffd483">If you answer this the way you answered typeahead, you are '
           'wrong. Say why the conclusion flips.</span></div>',
           """Why is this interesting? Because it produces the opposite conclusion to the lesson you just """
           """watched. In typeahead the index was small, so we replicated it and refused to fan out. In """
           """full-text search the index does not fit on one machine, so you must fan out — and the """
           """moment you fan out, you own the tail latency problem we spent the last lesson avoiding.""",
           step=0)
seg(sid, 1, """Three things make this harder than prefix suggestion. First, size: a full-text index over a """
            """billion documents is terabytes rather than gigabytes. Second, queries have multiple terms, """
            """so you are intersecting posting lists, and the cost of that depends on the rarest term in """
            """the query rather than the commonest.""")
seg(sid, 2, """And third, the interesting tension: ranking needs corpus-wide statistics — how rare is this """
            """word across all documents — but each shard only sees its own slice. Resolving that is the """
            """deep dive.""")
seg(sid, 3, """So if you answer this question the way you answered typeahead, you are wrong. And the """
            """strongest thing you can do is say that out loud: explain why the conclusion flips. """
            """Interviewers remember a candidate who knows the boundary conditions of their own """
            """techniques.""")

think('A query for "distributed systems engineer" has three terms. Your index is spread over 50 machines. Sketch what happens between the request arriving and the results going back.',
      30,
      """Pause. A three-term query, an index spread over fifty machines. Describe what happens between """
      """the request arriving and the results going out. Be concrete about what each machine does and """
      """what comes back.""",
      """Let us build that properly, starting with what is actually stored.""")

clarify('What I would clarify first', [
 ('What are we searching &mdash; profiles, posts, jobs, or all of them?',
  'Decides document count and update rate. Posts churn constantly; profiles barely change. '
  '<b>Update rate drives the index design more than size does.</b>'),
 ('How fresh must results be after a write?',
  'Seconds means near-real-time indexing and segment merging. Minutes means a far simpler pipeline.'),
 ('Do queries need boolean logic and filters, or just relevance?',
  'Filters (location, company, connection degree) change the <b>index layout</b> &mdash; you may '
  'want them as separate posting lists rather than post-filtering.'),
 ('What p99 latency, and how many results per page?',
  'Fan-out cost is per shard; result merging is per page. Both matter, and they pull in different '
  'directions.'),
 ('Is ranking personalised?',
  'Personalised means you cannot cache results globally, and you may need a second ranking pass '
  'over the top N after the merge.'),
 ('What is the write rate?',
  'A billion documents that barely change is one system. A billion documents with a million updates '
  'a minute is a <b>completely</b> different one.'),
], [
 """What are we searching? Profiles, posts, jobs, or everything. This decides document count and """
 """update rate — and update rate drives index design more than raw size does, which is a point worth """
 """making early because it is not obvious.""",
 """How fresh must results be after a write? Seconds means near-real-time indexing with segment """
 """merging. Minutes means a much simpler pipeline, and you should find out before designing the """
 """complicated one.""",
 """Do queries need boolean logic and filters, or just relevance? Filters like location, company or """
 """connection degree change the index layout — you may want them as separate posting lists you """
 """intersect, rather than fetching results and filtering afterwards, which wastes most of your work.""",
 """What p ninety-nine, and how many results per page? Fan-out cost is per shard and merge cost is per """
 """page; those pull in different directions, so you need both numbers.""",
 """Is ranking personalised? If so you cannot cache globally, and you probably need a second ranking """
 """pass over the top N after the merge.""",
 """And the write rate. A billion documents that barely change is one system; a billion documents with a """
 """million updates a minute is a completely different one. Ask.""",
])

capacity('Capacity — and the number that forces the architecture', [
 ('1B documents &times; ~1 KB of text', '1B &times; 1 KB', '1 TB of raw text',
  'The <b>index</b> is the interesting number, not the documents'),
 ('Inverted index &asymp; 30&ndash;50% of raw text', '1 TB &times; 0.4', '&asymp; 400 GB index',
  '<b>Does not fit one machine&rsquo;s RAM.</b> This single line forces sharding'),
 ('Shard to fit in RAM: ~20 GB each', '400 GB &divide; 20 GB', '<b>~20 shards</b>',
  'Serving from memory is what keeps p99 sane. Disk seeks per term would not'),
 ('&times;3 replicas for availability and read capacity', '20 &times; 3', '60 nodes',
  'Replicas also <b>absorb query load</b>, not just failure &mdash; say both'),
 ('10k queries/s &times; 20 shards', 'each query touches every shard', '<b>200k shard-queries/s</b>',
  'Fan-out multiplies internal load 20&times;. <b>This is the cost of sharding</b>'),
 ('p99 per shard 20 ms, 20 shards', 'wait for the slowest of 20',
  '<b>p99 of the whole query is far worse</b>',
  'Tail amplification. <b>The central problem of this design</b>'),
], [
 """The capacity work, and watch for the line that forces everything. A billion documents at roughly a """
 """kilobyte of text each is a terabyte of raw text — but the index is the interesting number, not the """
 """documents.""",
 """An inverted index typically runs thirty to fifty percent of the raw text size, so call it four """
 """hundred gigabytes. That does not fit in one machine's memory, and that single line is what forces """
 """sharding. Notice the contrast with typeahead, where the equivalent line said it does fit, and we """
 """made the opposite choice.""",
 """Shard so each piece fits comfortably in RAM — say twenty gigabytes each — and you get about twenty """
 """shards. Serving from memory is what keeps p ninety-nine sane; doing disk seeks per term would """
 """not.""",
 """Three replicas each for availability, so sixty nodes. And say both reasons: replicas absorb query """
 """load as well as failure. People mention only failure and miss half the value.""",
 """Now the cost. Ten thousand queries a second, each touching every shard, is two hundred thousand """
 """shard-queries a second. Fan-out multiplies your internal load twenty times, and that is the price """
 """of sharding stated plainly.""",
 """And the real problem: if each shard is twenty milliseconds at p ninety-nine, the whole query waits """
 """for the slowest of twenty shards, so the query's p ninety-nine is much worse than twenty """
 """milliseconds. That is tail amplification, and it is the central problem of this design rather than """
 """a footnote.""",
])

sid = beat('Data model', 'What an inverted index actually is',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Forward index</b> &mdash; what you naively store:<br>'
           '<span style="font-family:JetBrains Mono,monospace;font-size:23px;color:#9fb4cc">'
           'doc_42 &rarr; "staff engineer distributed systems"</span><br>'
           'Answers &ldquo;what is in document 42?&rdquo; &mdash; which <b>nobody asks</b>.<br><br>'
           '<b>Inverted index</b> &mdash; what search needs:<br>'
           '<span style="font-family:JetBrains Mono,monospace;font-size:23px;color:#5ad7c0">'
           '"distributed" &rarr; [doc_7, doc_42, doc_913, &hellip;]<br>'
           '"engineer" &nbsp;&nbsp;&rarr; [doc_3, doc_42, doc_77, &hellip;]</span><br>'
           'Answers &ldquo;which documents contain this word?&rdquo; &mdash; which is the only '
           'question search asks.<br><br>'
           'Each posting also carries <b>term frequency</b> and <b>positions</b>, so you can rank, and '
           'so you can match phrases rather than loose words.<br><br>'
           '<span style="color:#ffd483">A multi-term query is an <b>intersection of sorted posting '
           'lists</b>. Start with the <i>rarest</i> term &mdash; it has the shortest list, and it '
           'bounds all the work that follows.</span></div>',
           """The data model, briefly, because you need the vocabulary to discuss the rest. A forward """
           """index maps a document to its words, which answers "what is in document forty-two" — a """
           """question nobody asks.""", step=0)
seg(sid, 1, """An inverted index maps each word to the documents containing it, which answers "which """
            """documents contain this word" — the only question search actually asks. That inversion is """
            """the entire idea, and it is why the structure is called what it is.""")
seg(sid, 2, """Each posting also carries term frequency and positions, so you can rank by how often a word """
            """appears, and match phrases rather than loose collections of words.""")
seg(sid, 3, """And the operational fact worth saying: a multi-term query is an intersection of sorted """
            """posting lists, and you start with the rarest term because it has the shortest list and """
            """bounds all the work that follows. If someone searches for "distributed" and "kubernetes", """
            """you start with kubernetes. That one sentence shows you know how the thing executes rather """
            """than just what it stores.""")

tradeoff('The decision that defines this system: how do you shard?', [
 ('Shard by <b>term</b> (partition the dictionary)', 'deny',
  ['A single-term query touches exactly <b>one</b> shard',
   'No fan-out for simple queries'],
  ['A multi-term query must ship <b>whole posting lists</b> across the network to intersect them',
   'Common words create enormous hot shards &mdash; the shard holding "engineer" serves everything',
   'Adding a document touches <b>many</b> shards, one per distinct word',
   '<b>Nobody builds it this way at scale</b>']),
 ('Shard by <b>document</b> (each shard a full mini-index)', 'ok',
  ['Every shard answers any query <b>independently</b> &mdash; no cross-shard data movement',
   'Indexing a document touches exactly <b>one</b> shard',
   'Load distributes evenly if you hash the document id',
   'Adding capacity is adding shards'],
  ['Every query fans out to <b>every</b> shard &mdash; you pay the tail',
   'Corpus-wide ranking statistics are now <b>split across shards</b>',
   'Result merging is required on every query']),
], decision='Shard by document. Every shard holds a complete inverted index over its own slice of '
            'documents, so a query executes independently everywhere and you merge at the end.',
 flip='Nothing realistic flips this at scale. Term-sharding only makes sense for a small corpus with '
      'overwhelmingly single-term queries &mdash; and if you have that, you probably do not need '
      'distribution at all.',
 narration=[
  """Now the decision that defines the system, and it is the one I would spend real time on. You can """
  """shard by term — partition the dictionary, so one machine owns every posting list for words """
  """starting with A through F. A single-term query then touches exactly one shard, which sounds """
  """wonderful.""",
  """And it collapses immediately. A multi-term query has to ship whole posting lists across the network """
  """to intersect them, and posting lists for common words are enormous. Common words also create """
  """catastrophic hot shards — the machine holding "engineer" serves essentially every query on a """
  """professional network. And indexing a single document touches many shards, one per distinct word in """
  """it. Nobody builds it this way at scale, and knowing why is more useful than knowing that.""",
  """Shard by document instead: each shard holds a complete miniature inverted index over its own slice """
  """of the corpus. Every shard can answer any query independently with no cross-shard data movement. """
  """Indexing a document touches exactly one shard. Load distributes evenly if you hash the document """
  """id. And adding capacity is just adding shards.""",
  """The costs are real and you should name them: every query fans out to every shard so you pay the """
  """tail, corpus-wide ranking statistics are now split across shards, and you must merge results on """
  """every query. We will solve two of those three.""",
  """So: shard by document. And the honest reversal — nothing realistic flips this at scale. """
  """Term-sharding only makes sense for a small corpus with overwhelmingly single-term queries, and if """
  """you have that you probably do not need distribution at all. Saying "this one is not really a """
  """trade-off, and here is why" is a legitimate and confident answer.""",
 ])

# ------------------------------------------------------------------ architecture
A = Arch('Architecture — scatter, gather, merge', kicker='Progressive disclosure', height=800)
A.box('cl',   70, 350, 160, 100, 'Client', kind='neutral', step=0, focus=0)
A.box('co',  290, 350, 220, 100, 'Coordinator', 'scatter &amp; merge', kind='ok', step=0, focus=[0, 3])
A.arrow('cl', 'co', step=0, focus=0)

for i, y in enumerate([170, 310, 450, 590]):
    A.box('s%d' % i, 640, y, 210, 90, 'Shard %d' % i, 'full index, 1/20 of docs',
          kind='info', step=1, focus=1, small=True)
    A.arrow('co', 's%d' % i, step=1, focus=1)
A.note(640, 690, '&hellip; &times;20 shards, each replicated 3&times;', step=1, kind='neutral', w=400, size='m')

A.box('idx',  960, 170, 220, 90, 'Indexer', 'doc &rarr; one shard', kind='dp', step=4, focus=4, small=True)
A.box('src',  960, 310, 220, 90, 'Document stream', kind='shared', step=4, focus=4, small=True)
A.arrow('src', 'idx', step=4, focus=4)
A.arrow('idx', 's1', step=4, focus=4, fs='l', ts='r')

A.box('rank', 960, 450, 220, 90, 'Re-rank top N', 'full features', kind='ok', step=5, focus=5, small=True)
A.arrow('co', 'rank', step=5, focus=5, via=[(560, 640), (1070, 640)], ts='b')

A.note(1240, 180, '**The query:**\\n'
                  '1. coordinator scatters to all 20\\n'
                  '2. each shard returns its **top 10**\\n'
                  '&nbsp;&nbsp;&nbsp;(not all matches)\\n'
                  '3. coordinator merges 200 &rarr; 10\\n'
                  '4. optional second-pass re-rank\\n\\n'
                  '**Each shard sends 10 rows, not\\nten thousand.** That is what makes\\nthe merge cheap.',
       step=6, kind='ok', w=560, size='m')
A.narrate(0, """The architecture. A client hits a coordinator, whose two jobs are scattering the query and """
              """merging the answers. It holds no index itself, which keeps it cheap and replaceable.""")
A.narrate(1, """The coordinator scatters to all twenty shards, each holding a complete index over one """
              """twentieth of the documents, each replicated three times. So a query touches twenty """
              """machines, and the coordinator picks one replica per shard — which is also your load """
              """balancing and your failure handling in one mechanism.""")
A.narrate(2, """Each shard executes the full query locally: intersect the posting lists, score the """
              """matches, and — this is the important part — return only its own top ten rather than """
              """every match it found.""")
A.narrate(3, """The coordinator then merges twenty lists of ten into a final ten. Two hundred rows in, ten """
              """rows out. That is a trivial amount of work, and it is trivial precisely because each """
              """shard truncated before sending.""")
A.narrate(4, """Off the query path, an indexer consumes a document stream and writes each document to """
              """exactly one shard, chosen by hashing its id. Indexing does not fan out at all, which is """
              """the dividend of document-sharding.""")
A.narrate(5, """And optionally a second-pass re-ranker over the merged top N, where you can afford """
              """expensive features — a machine-learned model, personalisation — because you are scoring """
              """ten or a hundred documents rather than a million.""")
A.narrate(6, """Step back and note the shape: scatter, gather with truncation, merge, optionally re-rank. """
              """Every shard sends ten rows rather than ten thousand, and that single discipline is what """
              """makes the merge affordable. If you present this and say that sentence, you have """
              """explained the design.""")
A.build()

sid = beat('Deep dive 1', 'The tail, and how you actually fight it',
           '<div class="bigidea">With 20 shards, your query is only as fast as the <b>slowest</b> one. '
           'A 1-in-100 slow shard becomes a <b>1-in-5</b> slow query.</div>'
           '<div style="margin-top:22px;font-size:26px;line-height:1.65">'
           '<b>&bull; Hedged requests.</b> If a shard has not answered by p95, send the same query to '
           'another replica and take whichever returns first. Costs a few percent more load, cuts the '
           'tail dramatically. <b>The single best answer here.</b><br>'
           '<b>&bull; Tied requests.</b> Send to two replicas immediately, each telling the other to '
           'cancel when it starts. Lower latency, more load.<br>'
           '<b>&bull; Return partial results.</b> If 19 of 20 shards answered in budget, return those '
           'and mark the response incomplete. <b>Almost always the right product decision</b> &mdash; '
           'nobody notices 5% of results missing; everybody notices a spinner.<br>'
           '<b>&bull; Shard-level timeouts</b> with a coordinator deadline, so one sick machine cannot '
           'hold the whole query.<br>'
           '<b>&bull; Keep shards small enough</b> that per-shard work is predictable in the first '
           'place.</div>',
           """Deep dive one: the tail, and how you actually fight it — because this is the question the """
           """architecture created and an interviewer will absolutely push on it. With twenty shards your """
           """query is only as fast as the slowest one. Put numbers on it: if a shard is slow one time in """
           """a hundred, then with twenty shards roughly one query in five hits a slow shard. A rare """
           """problem became a common one, purely through fan-out.""", step=0)
seg(sid, 1, """Hedged requests are the single best answer. If a shard has not responded by the ninety-fifth """
            """percentile, send the same query to another replica and take whichever comes back first. It """
            """costs a few percent more load because you only hedge the slow tail, and it cuts p """
            """ninety-nine dramatically. If you know one technique for tail latency, know this one.""")
seg(sid, 2, """Tied requests are the more aggressive version: send to two replicas immediately, each """
            """telling the other to cancel once it starts work. Lower latency, more load.""")
seg(sid, 3, """Returning partial results is the one candidates rarely propose and is almost always right as """
            """a product decision. If nineteen of twenty shards answered inside the budget, return those """
            """and mark the response incomplete. Nobody notices five percent of results missing; """
            """everybody notices a spinner. Framing it as a product decision rather than a technical """
            """compromise is what makes it a senior answer.""")
seg(sid, 4, """Plus shard-level timeouts with an overall coordinator deadline, so a single sick machine """
            """cannot hold an entire query hostage. And keeping shards small enough that per-shard work """
            """is predictable in the first place — prevention before mitigation.""")

sid = beat('Deep dive 2', 'Near-real-time indexing without pausing the reads',
           '<div style="font-size:26px;line-height:1.68">'
           'An inverted index is efficient because it is <b>sorted and immutable</b>. But documents '
           'change constantly. Those two facts fight.<br><br>'
           '<b>The resolution &mdash; segments:</b><br>'
           '&bull; New documents go into a small <b>in-memory segment</b>, searchable within seconds.<br>'
           '&bull; Periodically that segment is <b>flushed to disk</b>, immutable, and a new one '
           'starts.<br>'
           '&bull; A query searches <b>every</b> segment and merges &mdash; the same merge you already '
           'do across shards, one level down.<br>'
           '&bull; Background <b>compaction</b> merges small segments into large ones, or searching '
           'them all gets slow.<br>'
           '&bull; Deletes are <b>tombstones</b>: you cannot edit an immutable segment, so you mark and '
           'filter at query time, and reclaim during compaction.<br><br>'
           '<span style="color:#ffd483">This is the same immutable-base-plus-overlay shape as '
           'typeahead &mdash; and the same shape as an LSM tree. <b>Naming that connection is worth '
           'real credit.</b></span></div>',
           """Deep dive two: how you index in near real time without pausing reads. The tension is that an """
           """inverted index is efficient precisely because it is sorted and immutable, while documents """
           """change constantly. Those two facts fight each other.""", step=0)
seg(sid, 1, """The resolution is segments. New documents go into a small in-memory segment which is """
            """searchable within seconds. Periodically that segment is flushed to disk as an immutable """
            """file and a fresh one starts.""")
seg(sid, 2, """A query then searches every segment and merges the results — which is the same merge you """
            """already do across shards, just one level down. I like pointing that out because it shows """
            """the pattern repeating rather than being two unrelated mechanisms.""")
seg(sid, 3, """Background compaction merges small segments into larger ones, because otherwise searching """
            """hundreds of tiny segments gets slow. And deletes are tombstones: you cannot edit an """
            """immutable file, so you mark the document deleted, filter it at query time, and reclaim the """
            """space during compaction.""")
seg(sid, 4, """And the connection worth making explicitly: this is the same immutable-base-plus-overlay """
            """shape we used in typeahead, and it is also exactly how an LSM tree works underneath a """
            """modern key-value store. Naming that link tells an interviewer you see the pattern rather """
            """than the implementation, which is precisely the difference between senior and staff.""")

sid = beat('Deep dive 3', 'Ranking when no shard can see the whole corpus',
           '<div style="font-size:27px;line-height:1.7">'
           'Relevance scoring needs to know how <b>rare</b> a word is across the <i>entire</i> corpus '
           '&mdash; a match on &ldquo;kubernetes&rdquo; means far more than a match on '
           '&ldquo;engineer&rdquo;.<br><br>'
           'But each shard only sees its own twentieth. Its idea of rare is <b>local</b>.<br><br>'
           '<b>Three options:</b><br>'
           '<b>1. Ignore it.</b> With random document assignment, term frequencies are '
           'statistically similar across shards. <b>Usually good enough</b>, and free.<br>'
           '<b>2. Periodically broadcast global term statistics</b> to every shard. Cheap, slightly '
           'stale, accurate.<br>'
           '<b>3. Two-phase query</b>: gather statistics first, then score. Accurate and <b>doubles '
           'your latency</b> &mdash; rarely worth it.<br><br>'
           '<span style="color:#ffd483">I would take option 1, say <i>why</i> it works (random '
           'assignment), and name option 2 as the fix if measurement showed drift.</span></div>',
           """Deep dive three, and this is the subtle one that the reported follow-ups specifically """
           """mention: ranking when no shard can see the whole corpus. Relevance scoring needs to know """
           """how rare a word is across the entire corpus — a match on kubernetes means far more than a """
           """match on engineer, and that judgement depends on global statistics.""", step=0)
seg(sid, 1, """But each shard sees only its own twentieth, so its notion of rare is local.""")
seg(sid, 2, """Three options. First, ignore it: because documents are assigned to shards randomly, term """
            """frequencies are statistically similar across shards, so local rarity approximates global """
            """rarity well. This is usually good enough and it is free.""")
seg(sid, 3, """Second, periodically broadcast global term statistics to every shard — cheap, slightly """
            """stale, accurate. Third, a two-phase query that gathers statistics and then scores, which """
            """is accurate and doubles your latency, so it is rarely worth it.""")
seg(sid, 4, """I would take the first option, and crucially I would say why it works — random assignment """
            """makes the local distribution representative — then name the second as the fix if """
            """measurement showed drift. That structure, "here is the cheap answer, here is the """
            """condition under which it fails, here is what I would do then", is the most reusable """
            """answer shape in system design interviews.""")

failures('What happens when each piece dies', [
 ('One shard replica', 'Nothing &mdash; the coordinator uses another replica',
  '3 replicas per shard. This is the normal case and should be invisible'),
 ('<b>All</b> replicas of one shard', 'Results are missing ~5% of the corpus, silently',
  '<b>Return partial results and say so in the response.</b> Silently wrong results are worse than '
  'an explicit degradation'),
 ('Coordinator', 'That query fails; the client retries',
  'Stateless, so run many behind a load balancer. Cheap to replace'),
 ('Indexer', 'New documents stop appearing; existing search is unaffected',
  'Reads are wholly unaffected. Alert on <b>indexing lag</b>, and you have hours before anyone '
  'notices'),
 ('A shard falls behind on compaction', 'That shard gets slower, so <b>every</b> query gets slower',
  'The insidious one: <b>one sick shard degrades all queries</b> because of fan-out. Hedging masks '
  'it; monitor segment count per shard'),
 ('Traffic doubles', 'Latency rises everywhere at once',
  'Add <b>replicas</b>, not shards. Replicas add query capacity; shards add index capacity. '
  '<b>Know which problem you have</b>'),
], [
 """The failure table. One replica dying is invisible — the coordinator uses another. That is the """
 """normal case and it should never be noticed.""",
 """All replicas of one shard dying is the interesting one: your results are now missing about five """
 """percent of the corpus, and by default they are missing it silently. So return partial results and """
 """mark the response as incomplete. Silently wrong results are worse than an explicit degradation, """
 """because nobody can act on a problem they cannot see.""",
 """The coordinator dying fails that query and the client retries; it is stateless, so run many behind a """
 """load balancer.""",
 """The indexer dying means new documents stop appearing while existing search is completely unaffected. """
 """Alert on indexing lag, and note you have hours before anyone notices — so it is not a page.""",
 """Now the insidious one, and I would volunteer this because it shows operational experience: a shard """
 """that falls behind on compaction gets slower, and because every query touches every shard, every """
 """query gets slower. One sick machine degrades the entire system. Hedging masks it, which is both good """
 """and dangerous — good because users are protected, dangerous because you stop noticing. So monitor """
 """segment count per shard directly.""",
 """And when traffic doubles, add replicas rather than shards. Replicas add query capacity; shards add """
 """index capacity. Knowing which problem you have is the difference between fixing it and making it """
 """worse — adding shards to a query-capacity problem increases fan-out and makes latency worse.""",
])

sid = beat('Observability, security, cost', 'Specific to this system',
           '<div class="to-grid" style="top:24px">'
           '<div class="to-opt k-info" data-step="0"><div class="to-h">What I would alert on</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; <b>Query p99</b>, and separately <b>slowest-shard p99</b><br>'
           '&bull; <b>Partial-result rate</b> &mdash; how often we are returning incomplete answers<br>'
           '&bull; <b>Indexing lag</b> &mdash; leading indicator<br>'
           '&bull; <b>Segments per shard</b> &mdash; catches compaction falling behind <i>before</i> '
           'latency moves<br>'
           '&bull; Hedge rate &mdash; a rise means a shard is sick<br><br>'
           '<span style="color:#ffd483">Business metric: <b>queries with zero results</b>. Spikes '
           'mean the index is broken, not that users changed.</span></div></div>'
           '<div class="to-opt k-shared" data-step="1"><div class="to-h">Security</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; <b>Visibility filtering must be in the query</b>, not applied afterwards &mdash; '
           'post-filtering leaks existence and breaks pagination<br>'
           '&bull; Private profiles, blocks, and per-viewer rules<br>'
           '&bull; Rate limit: search is a <b>scraping surface</b><br>'
           '&bull; Expensive query protection &mdash; deep pagination and huge boolean queries are '
           'a cheap denial of service</div></div>'
           '<div class="to-opt k-ok" data-step="2"><div class="to-h">Cost</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; Dominated by <b>RAM &times; 60 nodes</b><br>'
           '&bull; Lever 1: <b>fewer replicas</b> if you can accept lower query capacity<br>'
           '&bull; Lever 2: <b>tiered index</b> &mdash; hot recent documents in RAM, cold on SSD<br>'
           '&bull; Lever 3: index fewer fields. Most fields are never searched<br><br>'
           '<span style="color:#ffd483">Lever 3 is usually the biggest and is almost never '
           'taken.</span></div></div></div>',
           """Observability. Alert on query p ninety-nine, and separately on slowest-shard p ninety-nine, """
           """because with fan-out those are different numbers and the second one explains the first. """
           """Alert on partial-result rate, so you know how often you are returning incomplete answers. """
           """Indexing lag as a leading indicator. And segments per shard, which catches compaction """
           """falling behind before latency moves.""", step=0)
seg(sid, 1, """Hedge rate deserves a mention: a rising hedge rate means a shard is sick, and it moves """
            """before user-visible latency does because hedging is hiding the problem. And a business """
            """metric — queries returning zero results. A spike there usually means the index is broken """
            """rather than that users suddenly changed behaviour.""")
seg(sid, 2, """Security has one item specific to search that matters enormously: visibility filtering has """
            """to be part of the query, not applied to the results afterwards. Post-filtering leaks """
            """existence — if you return eight results on a page of ten, the user learns two were hidden """
            """— and it breaks pagination in ways that are very hard to fix later. Plus rate limiting, """
            """because search is a scraping surface, and protection against expensive queries like deep """
            """pagination, which is a cheap denial of service.""")
seg(sid, 3, """Cost is dominated by RAM across sixty nodes. Three levers: fewer replicas if you accept """
            """lower query capacity, a tiered index with hot documents in RAM and cold on SSD, and """
            """indexing fewer fields. That third one is usually the biggest saving available and is """
            """almost never taken, because nobody goes back to check which fields are actually """
            """searched.""")

sid = cards('Staff-level follow-ups', [
 (0, '&ldquo;Ten times the queries.&rdquo;',
  'Add <b>replicas</b>, not shards. Query capacity scales with replicas; shards would increase fan-out and make latency worse. <b>Naming that distinction is the answer.</b>', 'ok'),
 (0, '&ldquo;Ten times the documents.&rdquo;',
  'Now add shards &mdash; and accept worse tail latency, so lean harder on hedging and partial results. Also revisit whether cold documents need to be in RAM at all.', 'ok'),
 (1, '&ldquo;Results must be fresh within one second.&rdquo;',
  'The segment design already gives seconds. Below that you are fighting the immutability that makes it fast. Ask <b>what actually needs it</b> &mdash; usually one document type, which can take a separate faster path.', 'shared'),
 (1, '&ldquo;Add filters: location, company, degree.&rdquo;',
  'Index them as their own posting lists and <b>intersect during the query</b>. Post-filtering after ranking wastes the ranking and breaks result counts.', 'ok'),
 (2, '&ldquo;One shard is hot.&rdquo;',
  'With document-hash sharding it should not be &mdash; so investigate rather than rebalance. Usually a compaction backlog or a noisy neighbour, not skew.', 'ok'),
 (2, '&ldquo;Personalise the ranking.&rdquo;',
  'Second-pass re-rank over the merged top N, where N is ~100. Never personalise inside the shards &mdash; they would each need the viewer\'s graph, and you would destroy cacheability.', 'ok'),
], cols=2)
seg(sid, 0, """Staff-level follow-ups. Ten times the queries: add replicas, not shards. Query capacity """
            """scales with replicas, whereas adding shards increases fan-out and makes latency worse. """
            """Naming that distinction is the whole answer, and it is a distinction a lot of candidates """
            """never make.""")
seg(sid, 1, """Ten times the documents: now you do add shards, and you accept worse tail latency, so you """
            """lean harder on hedging and partial results. Also revisit whether cold documents need to be """
            """in memory at all.""")
seg(sid, 2, """One-second freshness: the segment design already gives you seconds. Below that you are """
            """fighting the immutability that makes the whole thing fast. So ask what actually needs """
            """sub-second freshness — it is usually one document type, and that type can take a separate """
            """faster path rather than slowing everything.""")
seg(sid, 3, """Adding filters: index them as their own posting lists and intersect during the query. """
            """Post-filtering after ranking wastes the ranking you just did and breaks your result """
            """counts, which users notice immediately.""")
seg(sid, 4, """One shard is hot: with document-hash sharding it should not be, so investigate rather than """
            """rebalance. It is usually a compaction backlog or a noisy neighbour rather than genuine """
            """skew — and reaching for rebalancing before diagnosing is a classic mistake.""")
seg(sid, 5, """And personalising the ranking: second-pass re-rank over the merged top hundred. Never """
            """personalise inside the shards, because each shard would need the viewer's graph and you """
            """would destroy any hope of caching. Same conclusion as typeahead, reached for the same """
            """reason — keep personalisation late and small.""")

followups(
 ['Index sharding and replication &mdash; <b>reported</b>',
  'Near-real-time indexing &mdash; <b>reported</b>',
  'Query fan-out and merge &mdash; <b>reported</b>',
  'Ranking &mdash; <b>reported</b>'],
 ['"Why not shard by term?"',
  '"What is your p99 when one shard is slow?"',
  '"How do you score relevance without global statistics?"',
  '"What do you return if a shard never answers?"',
  '"Ten times the queries versus ten times the documents" &mdash; different answers'],
 """The reported follow-ups are unusually well documented for this question, and they map exactly onto """
 """what we covered: index sharding and replication, near-real-time indexing, query fan-out and merge, """
 """and ranking. All four were named in the candidate's account.""",
 """And these are the ones I would expect on top. Why not shard by term — have the collapse ready. What """
 """your p ninety-nine is when one shard is slow, which is the tail amplification conversation. How you """
 """score relevance without global statistics. What you return when a shard never answers. And the """
 """distinction between more queries and more documents, which have genuinely different answers.""")

say('What I should say — the sentences that carry this design', [
 'The index is about four hundred gigabytes, which does not fit one machine, so unlike typeahead I have to shard — and that means I have to deal with fan-out.',
 'I will shard by document, not by term. Term sharding means shipping whole posting lists across the network to intersect them, and common words create hot shards.',
 'Each shard returns only its own top ten, so the coordinator merges two hundred rows rather than a million. That is what makes the merge cheap.',
 'With twenty shards, a shard that is slow one time in a hundred makes one query in five slow. So I would use hedged requests against the replicas.',
 'If nineteen of twenty shards answer in budget, I would return partial results and mark them incomplete — nobody notices five percent missing, everybody notices a spinner.',
 'Indexing uses segments: a small in-memory segment for freshness, flushed to immutable files, with background compaction. It is the same shape as an LSM tree.',
 'Local term statistics approximate global ones well because documents are assigned randomly — and if measurement showed drift, I would broadcast global statistics periodically.',
 'If queries grow I add replicas; if documents grow I add shards. Those are different problems and adding the wrong one makes things worse.',
], [
 """Eight sentences for this question. The first connects it to the previous lesson and explains why the """
 """conclusion flips, which shows you understand both rather than having memorised either.""",
 """The second is the sharding decision with the specific failure of the alternative.""",
 """The third explains why the merge is affordable, which is the detail that makes the architecture """
 """credible.""",
 """The fourth quantifies tail amplification and names the remedy — this is the sentence I would most """
 """want you to have ready, because the follow-up is almost guaranteed.""",
 """The fifth frames partial results as a product decision rather than a technical compromise.""",
 """The sixth names the segment pattern and connects it to LSM trees, which is a strong signal of """
 """breadth.""",
 """The seventh gives the cheap answer to a subtle problem along with the condition under which it """
 """fails. And the eighth separates two scaling axes that candidates routinely conflate. Close on that """
 """one — it sounds like someone who has actually operated a search cluster.""",
])

cheatsheet('Distributed search — the revision card', [
 ('Problem', 'Full-text search over 1B documents, ranked'),
 ('Evidence', '1 first-hand Staff report &middot; May 2025 &middot; HIGH but single-source'),
 ('Scale', '400 GB index &middot; 20 shards &middot; &times;3 replicas &middot; 10k qps'),
 ('Dominant constraint', '<b>Tail latency from fan-out</b>'),
 ('Sharding', '<b>By document</b>, never by term'),
 ('Why not by term', 'Ships posting lists over the network; common words go hot'),
 ('Query flow', 'Scatter &rarr; each shard returns top 10 &rarr; merge 200 &rarr; 10'),
 ('Why merge is cheap', 'Shards truncate <b>before</b> sending'),
 ('Tail fix', '<b>Hedged requests</b> + shard timeouts + partial results'),
 ('Tail maths', '1-in-100 slow shard &rarr; <b>1-in-5 slow query</b> at 20 shards'),
 ('Indexing', 'In-memory segment &rarr; immutable flush &rarr; compaction'),
 ('Deletes', 'Tombstones, filtered at query, reclaimed in compaction'),
 ('Same shape as', 'LSM trees, and typeahead&rsquo;s base + overlay'),
 ('Ranking stats', 'Local &asymp; global (random assignment); broadcast if it drifts'),
 ('Personalisation', 'Second pass over merged top ~100 only'),
 ('Filters', 'Own posting lists, intersected in the query &mdash; never post-filter'),
 ('Failure', 'Shard gone &rarr; <b>partial results, marked</b>, not silence'),
 ('Alert on', 'Slowest-shard p99, partial-result rate, <b>segments per shard</b>, hedge rate'),
 ('More queries', 'Add <b>replicas</b>'),
 ('More documents', 'Add <b>shards</b>, and expect a worse tail'),
], [
 """The revision card. Problem, evidence stated honestly as single-source, scale, and the dominant """
 """constraint — tail latency from fan-out.""",
 """The sharding decision and why the alternative fails. The query flow and the reason the merge is """
 """cheap.""",
 """The tail: the remedy and the arithmetic that justifies it.""",
 """Indexing, deletes, and the pattern connection to LSM trees and to typeahead.""",
 """Ranking statistics, where personalisation goes, and how filters must be indexed rather than """
 """applied afterwards.""",
 """Then the operational lines: what failure looks like, what to alert on, and the two scaling axes with """
 """their different answers. Twenty lines, and they rebuild the design.""",
])

sid = statement('Lesson 3.1', 'The same company, the same domain, the opposite answer.',
                'Typeahead said do not fan out. Search says you must. What separates a Staff answer is knowing which constraint you are actually under.',
                kind='ok')
seg(sid, 0, """One line to close, and it is the reason I put this lesson immediately after typeahead. Same """
            """company, same domain, opposite answer.""")
seg(sid, 1, """Typeahead said do not fan out, because the index was small enough to replicate. Search says """
            """you must fan out, because it is not. Neither answer is right in general — each is right """
            """under its own constraint. What separates a Staff-level answer from a memorised one is """
            """knowing which constraint you are actually under, and being able to say why the other """
            """answer would be wrong here. Next: the job scheduler, reported from an Infrastructure loop, """
            """where the trap is the word exactly-once.""")
