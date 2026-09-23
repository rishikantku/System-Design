# -*- coding: utf-8 -*-
"""Chapter 1, Lesson 2 — capacity estimation masterclass."""
from lib import *

lesson_header('1.2', 'Capacity estimation masterclass',
              'Assumption &rarr; calculation &rarr; result &rarr; architectural implication', None, 32,
              """Lesson two: capacity estimation. This is the movement candidates fake most often and the """
              """one interviewers probe hardest, which makes it the highest-return half hour in this """
              """course. And I want to reframe it before we start a single calculation. Estimation is not """
              """a maths test. Nobody cares whether you can divide by eighty-six thousand four hundred. """
              """Estimation is how you eliminate designs out loud — how you get from "I could build this """
              """several ways" to "only one of those survives these numbers". Every calculation in this """
              """lesson ends in an architectural consequence, and if yours do not, you are doing arithmetic """
              """rather than engineering.""")

sid = beat('The point', 'An estimate that eliminates nothing was wasted time',
           '<div class="bigidea">Every number you compute must end in a sentence beginning '
           '<b>&ldquo;so&hellip;&rdquo;</b></div>'
           '<div style="margin-top:28px;font-size:29px;line-height:1.72">'
           '&ldquo;Forty writes a second&rdquo; &mdash; and? <span style="color:#ff8f8f">Nothing. '
           'Wasted.</span><br><br>'
           '&ldquo;Forty writes a second, <b>so a single node handles writes comfortably and I will not '
           'shard for write throughput</b>&rdquo; &mdash; <span style="color:#5ad7c0">that is '
           'engineering.</span><br><br>'
           '&ldquo;Twelve thousand reads a second at peak, <b>so the database needs a cache in front of '
           'it, and here is how big</b>&rdquo; &mdash; <span style="color:#5ad7c0">that is '
           'engineering.</span></div>',
           """Here is the test for every number you produce. Does it end in a sentence beginning with """
           """"so"? Forty writes a second — and? On its own, nothing. You have spent thirty seconds and """
           """changed no decision.""", step=0)
seg(sid, 1, """Forty writes a second, so a single node handles writes comfortably and I will not shard for """
            """write throughput. Now the number has done work. It has removed a component from your """
            """design and, more importantly, it has stopped you adding sharding by reflex — which is """
            """something interviewers watch for.""")
seg(sid, 2, """Twelve thousand reads a second at peak, so the database needs a cache in front of it, and """
            """here is how big it has to be. Again: number, consequence, decision. Get into this rhythm """
            """and estimation stops being a hoop and becomes the most persuasive five minutes of your """
            """interview.""")

# ------------------------------------------------------------------ numbers to know
sid = beat('Know these cold', 'The handful of numbers you should never have to derive',
           '<div class="cs" style="top:30px">'
           '<div class="cs-row" data-step="0"><div class="cs-h">Seconds / day</div>'
           '<div class="cs-v">86,400 &mdash; <b>round it to 100,000</b>. You are now 16% high, which '
           'is conservative and makes the division trivial</div></div>'
           '<div class="cs-row" data-step="0"><div class="cs-h">1 million / day</div>'
           '<div class="cs-v">&asymp; <b>12 per second</b></div></div>'
           '<div class="cs-row" data-step="0"><div class="cs-h">1 billion / day</div>'
           '<div class="cs-v">&asymp; <b>12,000 per second</b></div></div>'
           '<div class="cs-row" data-step="1"><div class="cs-h">Peak multiplier</div>'
           '<div class="cs-v"><b>2&ndash;3&times;</b> daily average for a normal diurnal product. '
           '10&times;+ only for events, launches or a thundering herd</div></div>'
           '<div class="cs-row" data-step="1"><div class="cs-h">1 KB &times; 1M / day</div>'
           '<div class="cs-v">= <b>1 GB / day</b> &asymp; 365 GB / year</div></div>'
           '<div class="cs-row" data-step="1"><div class="cs-h">Replication</div>'
           '<div class="cs-v"><b>&times;3</b> on every storage number, before you quote it</div></div>'
           '<div class="cs-row" data-step="2"><div class="cs-h">Memory read</div>'
           '<div class="cs-v">~100 ns &mdash; <b>free</b> at interview granularity</div></div>'
           '<div class="cs-row" data-step="2"><div class="cs-h">SSD random read</div>'
           '<div class="cs-v">~100 &micro;s &mdash; <b>1,000&times;</b> memory</div></div>'
           '<div class="cs-row" data-step="2"><div class="cs-h">Same-datacentre RTT</div>'
           '<div class="cs-v">~0.5 ms</div></div>'
           '<div class="cs-row" data-step="3"><div class="cs-h">Cross-continent RTT</div>'
           '<div class="cs-v">~70&ndash;150 ms &mdash; <b>physics, not engineering</b></div></div>'
           '<div class="cs-row" data-step="3"><div class="cs-h">One modern server</div>'
           '<div class="cs-v">Tens of thousands of simple requests/s; <b>a few thousand</b> if each '
           'touches a database</div></div>'
           '<div class="cs-row" data-step="3"><div class="cs-h">One database node</div>'
           '<div class="cs-v">Order <b>10,000 writes/s</b> &mdash; a useful line for &ldquo;do I need '
           'to shard?&rdquo;</div></div>'
           '</div>',
           """First, the numbers you should never have to derive. Seconds in a day: eighty-six thousand """
           """four hundred — and round it to a hundred thousand. That makes you about sixteen percent """
           """high, which is conservative in the right direction and turns every division into moving a """
           """decimal point. From that: a million a day is roughly twelve per second, and a billion a day """
           """is roughly twelve thousand per second.""", step=0)
seg(sid, 1, """Peak multiplier: two to three times the daily average for a normal product with a day-night """
            """cycle. Reserve ten times and above for launches, events or a thundering herd, and say which """
            """you are assuming. One kilobyte times a million a day is one gigabyte a day, which is about """
            """three hundred and sixty-five gigabytes a year. And multiply every storage number by three """
            """for replication before you quote it — quoting un-replicated storage is a small tell that """
            """you have not run the thing.""")
seg(sid, 2, """Then the latency ladder, which matters more than the storage numbers because latency is """
            """usually the binding constraint. A memory read is about a hundred nanoseconds — effectively """
            """free at interview granularity. A random SSD read is about a hundred microseconds, a """
            """thousand times slower. A round trip inside a datacentre is about half a millisecond.""")
seg(sid, 3, """A cross-continent round trip is seventy to a hundred and fifty milliseconds, and that one is """
            """physics rather than engineering — no amount of cleverness removes it, you can only avoid """
            """making the trip. One modern server does tens of thousands of simple requests per second, """
            """or a few thousand if each one touches a database. And one database node handles order ten """
            """thousand writes a second, which is the line I use to answer "do I need to shard?".""")

# ------------------------------------------------------------------ the template
sid = beat('The template', 'Six steps, every time, in this order',
           '<div style="font-size:30px;line-height:1.8">'
           '<b>1.</b> Users &rarr; <b>daily actives</b> &nbsp;<span style="color:#9fb4cc">(state the '
           'ratio you assume)</span><br>'
           '<b>2.</b> Actions per active per day &rarr; <b>total daily actions</b><br>'
           '<b>3.</b> Divide by 100,000 &rarr; <b>average requests per second</b><br>'
           '<b>4.</b> &times; peak multiplier &rarr; <b>peak RPS</b> &nbsp;'
           '<span style="color:#ffd483">this is the number you design for</span><br>'
           '<b>5.</b> Bytes per record &times; records per day &rarr; <b>storage per day, per year</b> '
           '&nbsp;<span style="color:#9fb4cc">&times;3 for replication</span><br>'
           '<b>6.</b> Request size &times; peak RPS &rarr; <b>bandwidth</b><br><br>'
           '<span style="color:#5ad7c0">Then the only step that matters: <b>what does each number rule '
           'out?</b></span></div>',
           """Now the template. Six steps, in this order, every single time — and having a fixed order is """
           """what stops you freezing when the question is unfamiliar. Users to daily actives, stating the """
           """ratio you assume. Actions per active per day, giving total daily actions. Divide by a """
           """hundred thousand for average requests per second.""", step=0)
seg(sid, 1, """Multiply by the peak multiplier to get peak requests per second — and that is the number you """
            """design for. Average load is a billing number; peak load is an architecture number. """
            """Candidates who size against the average are building a system that falls over every evening """
            """at eight.""")
seg(sid, 2, """Then bytes per record times records per day for storage, multiplied by three for """
            """replication. Then request size times peak requests per second for bandwidth.""")
seg(sid, 3, """And then the only step that actually matters: for each number, what does it rule out? Let us """
            """do that three times now, on three genuinely different systems, because the shape of the """
            """answer changes completely depending on whether you are read-heavy, write-heavy, or """
            """latency-bound.""")

# ------------------------------------------------------------------ example 1
sid = beat('Worked example 1', 'A URL shortener — the read-heavy shape',
           '<div style="font-size:30px;line-height:1.7">Stated assumptions, agreed with the interviewer '
           'before any arithmetic:<br><br>'
           '&bull; <b>100 million</b> new links per month<br>'
           '&bull; read : write ratio of <b>100 : 1</b><br>'
           '&bull; <b>500 bytes</b> stored per link<br>'
           '&bull; links kept for <b>5 years</b><br>'
           '&bull; peak is <b>3&times;</b> the daily average</div>',
           """Worked example one: a URL shortener, which is the read-heavy shape and also happens to be """
           """the question LinkedIn's own pack names. State your assumptions first and get them agreed. A """
           """hundred million new links a month. A read to write ratio of a hundred to one. Five hundred """
           """bytes stored per link. Links kept five years. Peak is three times the daily average. Five """
           """assumptions, all round, all challengeable — and by saying them out loud you have invited the """
           """interviewer to correct the one that is wrong.""")

capacity('URL shortener — the arithmetic, and what each line decides', [
 ('100M new links / month', '100M &divide; 30 days &divide; 100k s', '&asymp; 35 writes / s',
  'Trivial. <b>One node handles writes.</b> Do not shard for write throughput'),
 ('Reads are 100&times; writes', '35 &times; 100', '&asymp; 3,500 reads / s',
  'Still modest, but this is the path that matters &mdash; everything else follows the read'),
 ('Peak is 3&times; average', '3,500 &times; 3', '&asymp; 10,500 reads / s peak',
  'Around the limit of one database node. <b>A cache stops being optional</b>'),
 ('500 B &times; 100M / month', '50 GB / month &times; 12', '600 GB / year',
  'Small. &times;3 replication = <b>1.8 TB/yr</b>. Storage is <b>not</b> the constraint here'),
 ('5-year retention', '600 GB &times; 5 &times; 3', '&asymp; 9 TB total',
  'One cluster. No tiering, no archival. <b>Say so</b> &mdash; ruling things out is the job'),
 ('Hot set: 20% of links, 80% of reads', '20M links &times; 500 B', '10 GB working set',
  '<b>Fits in memory.</b> So cache hit ratio is high and the database sees a trickle'),
], [
 """Now the arithmetic, and watch the fourth column, because that is where the engineering lives. A """
 """hundred million a month, divided by thirty days, divided by a hundred thousand seconds, is about """
 """thirty-five writes a second. That is trivial, so one node handles writes and I will not shard for """
 """write throughput. Already one design eliminated.""",
 """Reads are a hundred times writes, so three and a half thousand reads a second. Still modest, but """
 """this is the path that matters — in a read-heavy system every later decision follows the read.""",
 """Peak at three times gives about ten and a half thousand reads a second. Now compare that to the line """
 """we learned earlier: one database node is order ten thousand. We are at the limit. So a cache stops """
 """being optional — and notice I did not add the cache because caches are normal. I added it because a """
 """number crossed a threshold I can name.""",
 """Storage: five hundred bytes times a hundred million a month is fifty gigabytes a month, six hundred """
 """gigabytes a year, one point eight terabytes with replication. That is small. So storage is not the """
 """constraint here — and saying that out loud is valuable, because it tells the interviewer you know """
 """which dimension to stop worrying about.""",
 """Over five years, about nine terabytes. That still fits one cluster, so no tiering and no archival. """
 """Rule it out explicitly. Candidates add cold storage tiers to systems that will never need them, and """
 """it reads as pattern-matching rather than thinking.""",
 """And the last line is the one that wins the design. If twenty percent of links take eighty percent of """
 """reads, the hot set is twenty million links at five hundred bytes, which is ten gigabytes. That fits """
 """comfortably in memory. So your cache hit ratio is high, the database sees a trickle, and you can """
 """state the resulting load rather than hand-waving that caching helps.""",
], note='Six lines of arithmetic have already decided: no write sharding, a cache on the read path, '
        'one storage cluster, no tiering, and a 10 GB cache. <b>That is the design, derived.</b>')

# ------------------------------------------------------------------ example 2
sid = beat('Worked example 2', 'A metrics platform — the write-heavy shape',
           '<div style="font-size:30px;line-height:1.7">Completely different shape. Assumptions:<br><br>'
           '&bull; <b>10,000</b> hosts<br>'
           '&bull; <b>200</b> metrics per host<br>'
           '&bull; scraped every <b>10 seconds</b><br>'
           '&bull; raw point = timestamp + value = <b>16 bytes</b><br>'
           '&bull; retention: <b>13 months</b></div>',
           """Worked example two: a metrics platform. This is the write-heavy shape, and it is one of the """
           """three questions with the strongest evidence in our research, so it is worth doing carefully. """
           """Ten thousand hosts, two hundred metrics each, scraped every ten seconds. A raw point is a """
           """timestamp plus a value, sixteen bytes. Retention thirteen months.""")

capacity('Metrics platform — where the numbers go somewhere else entirely', [
 ('10k hosts &times; 200 metrics', '10,000 &times; 200', '2 million <b>series</b>',
  'Series count, not request count, is the number that matters. Remember it'),
 ('Every 10 seconds', '2M &divide; 10', '<b>200,000 points / s</b>',
  'Two orders of magnitude above the shortener. <b>Ingestion is now a subsystem</b>, not an endpoint'),
 ('200k/s &times; 16 B raw', '3.2 MB/s &times; 86,400', '&asymp; 276 GB / day raw',
  '100 TB/yr before replication. <b>Storing raw points is not viable</b>'),
 ('Delta-of-delta + compression', '~16 B &rarr; ~2 B per point', '&asymp; 35 GB / day',
  '12.6 TB/yr, &times;3 = 38 TB. <b>Compression is load-bearing, not an optimisation</b>'),
 ('13-month retention at full resolution', '38 TB &times; 1.1', '&asymp; 42 TB',
  'Viable &mdash; but only because we downsample. <b>Rollups earn their place</b>'),
 ('Add one label: user_id, 1M values', '2M series &times; up to 1M', '<b>cardinality explosion</b>',
  'The system dies. <b>This &mdash; not throughput &mdash; is the real failure mode</b>'),
], [
 """And immediately the numbers behave differently. Ten thousand hosts times two hundred metrics is two """
 """million series. Notice the unit: series, not requests. In a metrics system the series count is the """
 """number that governs everything, and recognising that is the first sign you have thought about this """
 """domain rather than pattern-matched it.""",
 """Scraped every ten seconds, two million divided by ten is two hundred thousand points per second. """
 """That is two orders of magnitude above the shortener. So ingestion is now a subsystem in its own """
 """right rather than an endpoint on a service.""",
 """Two hundred thousand a second at sixteen bytes is three point two megabytes a second, which is two """
 """hundred and seventy-six gigabytes a day, about a hundred terabytes a year before replication. So """
 """storing raw points is simply not viable, and we have discovered that in one line.""",
 """Time-series compression — delta-of-delta on timestamps and XOR on values — takes you from about """
 """sixteen bytes to about two bytes per point. That is thirty-five gigabytes a day, twelve and a half """
 """terabytes a year, thirty-eight with replication. Say this clearly: compression is load-bearing here, """
 """not an optimisation. A design that omits it is wrong by a factor of eight.""",
 """Thirteen months at full resolution is about forty-two terabytes, which is viable, but only because """
 """we also downsample older data. So rollups earn their place — again, derived rather than assumed.""",
 """And now the line that actually matters. Add one innocent label — user id, with a million possible """
 """values — and your two million series becomes potentially billions. The system does not slow down; it """
 """falls over. Cardinality, not throughput, is the real failure mode of every metrics platform, and if """
 """you say that sentence in the interview you have demonstrated domain knowledge that cannot be faked """
 """by arithmetic.""",
], note='Same template, completely different conclusions: ingestion pipeline, columnar time-series '
        'storage, compression as a requirement, rollups, and <b>cardinality limits as a first-class '
        'design concern</b>.')

# ------------------------------------------------------------------ example 3
sid = beat('Worked example 3', 'Typeahead — the latency-bound shape',
           '<div style="font-size:30px;line-height:1.7">A third shape, where throughput is easy and the '
           '<b>budget</b> is everything:<br><br>'
           '&bull; <b>100 million</b> daily actives<br>'
           '&bull; <b>5</b> searches per active per day<br>'
           '&bull; a request on roughly every <b>4th keystroke</b><br>'
           '&bull; p99 target: <b>100 ms end to end</b></div>',
           """Worked example three: typeahead, which is the latency-bound shape. A hundred million daily """
           """actives, five searches each, and a request on roughly every fourth keystroke — because you """
           """debounce rather than firing on every character, and saying that shows you have built one of """
           """these. p ninety-nine target of a hundred milliseconds end to end.""")

capacity('Typeahead — the budget is the architecture', [
 ('100M DAU &times; 5 searches &times; 4 requests', '2 billion requests / day', '&asymp; 23,000 req / s',
  'High, but horizontally scalable. Throughput is <b>not</b> the hard part'),
 ('Peak 3&times;', '23,000 &times; 3', '&asymp; 70,000 req / s peak',
  'Fan-out across a fleet. Each node needs the index <b>locally</b>'),
 ('100 ms p99 budget', '&minus; 40 ms client network &minus; 10 ms LB/TLS', '<b>~50 ms server-side</b>',
  'Everything &mdash; lookup, rank, serialise &mdash; fits in 50 ms or you miss the SLA'),
 ('Within 50 ms: one DB round trip', '0.5 ms RTT + 100 &micro;s SSD + queueing', '&asymp; 5&ndash;20 ms under load',
  'Affordable <b>once</b>. A scatter-gather across 20 shards is not'),
 ('Index: 100M entities &times; ~100 B', '10 GB, or ~3 GB as an FST', '<b>fits in RAM per node</b>',
  'So <b>replicate the whole index</b> to every node rather than sharding it. No network hop at all'),
 ('Head prefixes: top 10k cover ~50%', '10k &times; 10 results &times; 200 B', '20 MB cache',
  'Tiny. <b>Half the traffic never touches the index</b>'),
], [
 """A hundred million times five times four is two billion requests a day, about twenty-three thousand a """
 """second. High, but this is throughput, and throughput scales horizontally. It is not the hard part """
 """here, and saying so redirects the conversation to where the difficulty actually is.""",
 """At three times peak, seventy thousand a second, which means fanning out across a fleet — and each """
 """node will need the index locally, for reasons the next lines make obvious.""",
 """Now the budget, and this is the calculation most candidates never do. A hundred millisecond p """
 """ninety-nine, minus roughly forty milliseconds of client network on a mobile connection, minus ten """
 """for load balancer and TLS, leaves about fifty milliseconds of server time. Everything — lookup, """
 """ranking, serialisation — must fit inside fifty milliseconds.""",
 """What fits? One database round trip is half a millisecond of network plus a hundred microseconds of """
 """SSD, but under real load with queueing, call it five to twenty milliseconds. So you can afford one. """
 """A scatter-gather across twenty shards, where you wait for the slowest, does not fit — and that single """
 """observation eliminates an entire architecture that many candidates draw.""",
 """So look at the index size: a hundred million entities at roughly a hundred bytes is ten gigabytes, or """
 """about three as a compressed finite state transducer. That fits in RAM on one node. So replicate the """
 """whole index to every node instead of sharding it, and remove the network hop entirely. That is a """
 """genuinely non-obvious design decision, and it came straight out of comparing two numbers.""",
 """And the head of the distribution: the top ten thousand prefixes cover about half the traffic, and """
 """caching ten results each is about twenty megabytes. Trivial. So half your traffic never touches the """
 """index at all.""",
], note='Same six steps. Here they produced: <b>replicate rather than shard</b>, one hop maximum, '
        'and a tiny head-prefix cache &mdash; none of which are obvious until you compute the budget.')

# ------------------------------------------------------------------ bandwidth, shards, replication
capacity('The three dimensions candidates forget', [
 ('<b>Bandwidth</b>: 70k req/s &times; 2 KB response', '70,000 &times; 2 KB', '140 MB/s &asymp; 1.1 Gbps',
  'Fine on modern NICs &mdash; but &times;3 for replication traffic, and now <b>cross-AZ transfer is a '
  'real line on the bill</b>'),
 ('Same, but responses are 200 KB', '70,000 &times; 200 KB', '14 GB/s &asymp; 112 Gbps',
  '<b>Now the network is the bottleneck</b>, not the CPU. You need a CDN, or to shrink the payload'),
 ('<b>Shard count</b>: 20 TB, 2 TB per node', '20 &divide; 2', '10 shards minimum',
  'But size for <b>throughput too</b>: 200k writes/s &divide; 10k per node = <b>20 shards</b>. Take '
  'the larger'),
 ('Growth over 2 years: 3&times;', '20 shards &times; 3', '60 shards eventually',
  'So start with <b>64 virtual shards</b> mapped onto 20 physical nodes. Rebalancing becomes '
  'a remap, not a migration'),
 ('<b>Replication</b>: 3 replicas, quorum writes', 'W=2, R=2, N=3', 'W + R &gt; N',
  'Strong reads, tolerates <b>one</b> node down. Costs 3&times; storage and 3&times; write bandwidth'),
 ('Same, but W=1 for speed', 'W=1, R=1, N=3', 'W + R &lt; N',
  '<b>Eventual consistency.</b> Faster writes, and now you owe an answer on read-after-write'),
], [
 """Three dimensions candidates routinely skip, and each one can decide an architecture on its own. """
 """First, bandwidth. Seventy thousand requests a second at a two-kilobyte response is a hundred and """
 """forty megabytes a second, about one point one gigabits. That is fine on a modern network card — but """
 """multiply by three for replication traffic, and cross-availability-zone transfer becomes a real line """
 """on your cloud bill.""",
 """Change one thing: make the responses two hundred kilobytes, say because they carry images. Now you """
 """need fourteen gigabytes a second, a hundred and twelve gigabits. The network is the bottleneck, not """
 """the CPU, and the answer is a content delivery network or a smaller payload. Same request rate, """
 """completely different system — which is why you compute bandwidth rather than assuming it is fine.""",
 """Second, shard count, and there are two ways to size it. By capacity: twenty terabytes at two """
 """terabytes a node is ten shards minimum. By throughput: two hundred thousand writes a second at ten """
 """thousand per node is twenty shards. Take the larger of the two — twenty. Candidates usually compute """
 """one and forget the other.""",
 """Then think about growth. If you expect three times the data in two years, you will eventually want """
 """sixty shards. So start with sixty-four virtual shards mapped onto twenty physical nodes. Growing """
 """then means remapping virtual shards to new machines rather than re-hashing and migrating every key. """
 """That single decision, made at design time, is the difference between a weekend of work and a quarter """
 """of work later — and it is exactly the kind of foresight this round is looking for.""",
 """Third, replication and what it costs. Three replicas with quorum writes and reads — W equals two, R """
 """equals two, N equals three — gives W plus R greater than N, so reads see the latest write and you """
 """tolerate one node down. The cost is three times the storage and three times the write bandwidth, and """
 """you should say that cost out loud rather than presenting replication as free.""",
 """Drop to W equals one for faster writes and now W plus R is less than N, so you have eventual """
 """consistency — and you immediately owe the interviewer an answer about read-after-write. Notice that """
 """the consistency conversation arrived out of an arithmetic choice, which is exactly how it happens in """
 """real systems.""",
], note='Bandwidth decides whether you need a CDN. Shard count decides your rebalancing story. '
        'Quorum arithmetic decides your consistency model. <b>None of these are optional dimensions.</b>')

# ------------------------------------------------------------------ sensitivity
sid = beat('Sensitivity', 'Change one assumption, and watch the architecture move',
           '<table class="cap" style="top:50px"><thead><tr><th>Change</th><th>New number</th>'
           '<th>What has to change in the design</th></tr></thead><tbody>'
           '<tr data-step="0"><td>Shortener: 100M &rarr; <b>10B</b> links/month</td>'
           '<td class="mono res">3,500 writes/s</td>'
           '<td class="imp">Now writes need sharding, and id generation must work <b>without '
           'coordination</b></td></tr>'
           '<tr data-step="1"><td>Typeahead p99: 100 ms &rarr; <b>30 ms</b></td>'
           '<td class="mono res">~10 ms server</td>'
           '<td class="imp">Cross-region is dead. Index must be in-process; <b>edge deployment</b> '
           'becomes the answer</td></tr>'
           '<tr data-step="2"><td>Metrics: 10k &rarr; <b>1M</b> hosts</td>'
           '<td class="mono res">20M points/s</td>'
           '<td class="imp">Single ingestion pipeline is gone. <b>Shard by series hash</b>, and '
           'pre-aggregate at the agent</td></tr>'
           '<tr data-step="3"><td>Shortener: reads 100:1 &rarr; <b>1:1</b></td>'
           '<td class="mono res">writes dominate</td>'
           '<td class="imp">The cache stops helping. <b>The entire design inverts</b> toward write '
           'throughput</td></tr>'
           '<tr data-step="4"><td>Retention: 5 yr &rarr; <b>forever</b></td>'
           '<td class="mono res">unbounded</td>'
           '<td class="imp">Tiering and archival are now mandatory, and <b>deletion becomes a feature</b> '
           '(GDPR)</td></tr>'
           '</tbody></table>',
           """Now the part that separates a candidate who computed numbers from one who understands them. """
           """Change one assumption and watch the architecture move. This is also the most common Staff """
           """follow-up you will get, so rehearse it.""", step=0)
seg(sid, 1, """Take the shortener from a hundred million links a month to ten billion. Writes go from """
            """thirty-five a second to three and a half thousand. Now writes need sharding, and — the """
            """interesting consequence — id generation has to work without coordination, because a central """
            """counter becomes the bottleneck. One assumption changed, and the hardest part of the design """
            """changed with it.""")
seg(sid, 2, """Tighten typeahead's p ninety-nine from a hundred milliseconds to thirty. Your server budget """
            """collapses to about ten milliseconds. Cross-region is now dead, the index has to be """
            """in-process, and edge deployment becomes the answer rather than a luxury.""")
seg(sid, 3, """Take metrics from ten thousand hosts to a million. Twenty million points a second. A single """
            """ingestion pipeline is gone; you shard by series hash and push pre-aggregation down to the """
            """agent on each host.""")
seg(sid, 4, """Flip the shortener's read-write ratio from a hundred to one down to one to one. The cache """
            """stops helping, and the entire design inverts toward write throughput. And make retention """
            """unbounded: tiering and archival become mandatory, and deletion turns into a product feature """
            """with regulatory weight behind it.""")

say('What I should say — while estimating', [
 'Let me put rough numbers on this. I will round hard, because I care about the order of magnitude, not the exact figure.',
 'I am going to assume a hundred million daily actives and about five actions each — tell me if that is far off.',
 'That is roughly twenty-three thousand requests a second average, and I will design for three times that at peak.',
 'Seventy thousand a second is more than one node, so this has to fan out — that is why there is a fleet here, not one service.',
 'Storage is about two terabytes a year with replication. That is small, so storage is not my constraint. Latency is.',
 'Let me check the latency budget before I go further, because it decides whether I can afford a network hop at all.',
 'If you told me the p99 target was thirty milliseconds instead, I would change this design — the index would have to be in-process.',
], [
 """The words, which matter as much as the arithmetic. Open by asking to round and saying why: I care """
 """about the order of magnitude, not the exact figure. That inoculates you against someone checking """
 """your division.""",
 """State assumptions as invitations to correct. I am going to assume a hundred million daily actives and """
 """five actions each — tell me if that is far off. If they correct you, that is a gift: you are now """
 """designing against their numbers rather than yours.""",
 """Give the average, then immediately give the peak and say you are designing for the peak. Then land """
 """the consequence: seventy thousand a second is more than one node, so this has to fan out — that is """
 """why there is a fleet here, not one service. The box has a reason before it is drawn.""",
 """Be willing to dismiss a dimension. Storage is about two terabytes a year, that is small, so storage """
 """is not my constraint, latency is. Interviewers notice candidates who can say what does not matter.""",
 """Check the latency budget explicitly before designing further, because it is the thing that decides """
 """whether a network hop is affordable.""",
 """And the last sentence is the one that makes you sound senior: if you told me the target was thirty """
 """milliseconds instead, I would change this design, and here is how. Volunteering the sensitivity """
 """before they test it shows you understand which assumption is load-bearing.""",
])

sid = cards('The estimation mistakes that get noticed', [
 (0, 'Designing for the average', 'Peak is 2&ndash;3&times;. A system sized to the average falls over every evening at eight.', 'deny'),
 (0, 'Forgetting replication', 'Quoting un-replicated storage understates the bill by 3&times; and reads as inexperience.', 'deny'),
 (1, 'Precision theatre', '&ldquo;86,400 seconds&rdquo; to four digits, then a wild guess at bytes per record. Round <i>everything</i> or nothing.', 'deny'),
 (1, 'No consequence', 'The number with no &ldquo;so&rdquo;. Five minutes spent, zero decisions made.', 'deny'),
 (2, 'Ignoring the latency budget', 'Throughput is usually easy. The budget is what rules architectures out &mdash; and most candidates never compute it.', 'deny'),
 (2, 'Never revisiting', 'You sized for 10k/s and later added a fan-out that multiplies it. Go back and say so.', 'shared'),
], cols=2)
seg(sid, 0, """The mistakes that get noticed. Designing for the average rather than the peak — a system sized """
            """to the average falls over every evening at eight, and interviewers have watched that """
            """happen for real. And forgetting replication, which understates your storage by three times """
            """and reads as inexperience.""")
seg(sid, 1, """Precision theatre: quoting eighty-six thousand four hundred to four significant figures and """
            """then guessing wildly at bytes per record. Round everything or round nothing. And the """
            """cardinal sin we started with — the number with no consequence attached.""")
seg(sid, 2, """Ignoring the latency budget, which is the one I would most like you to fix, because """
            """throughput is usually the easy dimension and the budget is what actually eliminates """
            """architectures. And never revisiting: if you sized for ten thousand a second and then added """
            """a fan-out that multiplies requests by five, go back and say so out loud. Updating your own """
            """estimate mid-design is a strong signal, not an admission of error.""")

cheatsheet('Capacity estimation — the revision card', [
 ('Seconds/day', '86,400 &rarr; use 100,000'),
 ('1M/day', '&asymp; 12/s'),
 ('1B/day', '&asymp; 12,000/s'),
 ('Peak', '2&ndash;3&times; average'),
 ('Storage', 'bytes &times; rate &times; retention &times; 3'),
 ('Memory', '~100 ns'),
 ('SSD read', '~100 &micro;s'),
 ('Same-DC RTT', '~0.5 ms'),
 ('Cross-continent', '~70&ndash;150 ms'),
 ('One server', '10ks of simple req/s'),
 ('One DB node', '~10,000 writes/s'),
 ('Cache working set', '20% of keys &asymp; 80% of reads'),
 ('The six steps', 'DAU &rarr; actions &rarr; RPS &rarr; peak &rarr; storage &rarr; bandwidth'),
 ('The only rule', 'Every number ends in &ldquo;so&hellip;&rdquo;'),
], [
 """Here is the revision card. Seconds per day rounded to a hundred thousand; a million a day is twelve a """
 """second; a billion a day is twelve thousand. Peak is two to three times average. Storage is bytes """
 """times rate times retention times three.""",
 """The latency ladder: memory a hundred nanoseconds, SSD a hundred microseconds, same-datacentre half a """
 """millisecond, cross-continent seventy to a hundred and fifty. One server does tens of thousands of """
 """simple requests; one database node about ten thousand writes.""",
 """The working-set rule of thumb: twenty percent of keys take about eighty percent of reads, which is """
 """how you size a cache in one line. The six steps in order. And the only rule that really matters — """
 """every number ends in "so".""",
])

sid = statement('Lesson 1.2', 'Estimation is how you eliminate designs out loud.',
                'Three systems, one template, three completely different architectures — and every decision was derived rather than recalled.',
                kind='ok')
seg(sid, 0, """One line to close. Estimation is how you eliminate designs out loud.""")
seg(sid, 1, """We ran one template across three systems and got three completely different architectures: a """
            """cache and a single cluster for the shortener, an ingestion pipeline with compression and """
            """cardinality limits for metrics, and a replicated in-process index for typeahead. Not one of """
            """those was recalled. Every one was derived from two or three numbers. That is the skill. """
            """Next lesson we take the question LinkedIn actually published — the URL shortener — and run """
            """the entire method end to end.""")
