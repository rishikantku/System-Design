# -*- coding: utf-8 -*-
"""Chapter 2, Lesson 1 — design a URL shortener (Bit.ly). The official example question."""
from lib import *

lesson_header('2.1', 'Design a URL shortener (Bit.ly)',
              'Read-heavy KV &middot; unique id generation &middot; analytics',
              dict(reports="LinkedIn's own recruiter pack, with four named sub-questions",
                   latest='September 2026', level='Staff, Systems &amp; Infrastructure',
                   conf='HIGHEST &mdash; official', sources='Staff SI Onsite Prep pack'), 34,
              """Chapter two, lesson one. We start with the URL shortener, and the reason is not that it is """
              """the hardest question in this course — it is not. It is that this is the only system design """
              """question LinkedIn has put in writing. It appears as the worked example in the Systems and """
              """Infrastructure preparation pack the recruiter sends, together with four named """
              """sub-questions. Whatever else you prepare, prepare the one they told you about. And it is a """
              """better question than it looks: it appears easy, which means the marks are not in the """
              """architecture, they are in the depth you bring to two specific places.""")

evidence('Where this question comes from', [
 ('LinkedIn recruiter pack &mdash; <b>Staff SI Onsite Prep</b>', 'Sep 2026', 'Staff, SI',
  'Named as the worked example, with four sub-questions: the core service, scaling reads, '
  'guaranteeing unique codes, and click analytics'),
 ('General interview canon', '&mdash;', 'all',
  'Also the most-practised question in the industry &mdash; which <b>raises</b> the bar rather than '
  'lowering it'),
], """Where this comes from, stated honestly. The recruiter pack names it as the worked example for the """
     """Systems and Infrastructure design module, and it lists four sub-questions: the core service, how """
     """you scale reads, how you guarantee unique short codes, and analytics on click traffic. That is as """
     """close to knowing the question as you will ever get.""",
 ["""But here is the catch, and it matters. This is also the most-practised system design question in """
  """the industry. Everyone has seen it. That raises the bar rather than lowering it — an interviewer who """
  """has heard four hundred URL shortener answers is not impressed by the standard one. They are """
  """listening for the two places where this problem is genuinely interesting, and we are going to spend """
  """most of this lesson there."""],
 caveat='The pack names it as an example, not a guarantee. Prepare it because it shows you what kind of '
        'reasoning is wanted &mdash; not because it will certainly be asked.',
 narration_caveat="""And the honest caveat, which I will repeat for every question in this course: the pack """
                  """names this as an example, not a promise. Prepare it because it tells you what kind of """
                  """reasoning LinkedIn wants to see - not because it will certainly be the question you get.""")

sid = beat('Why this is interesting', 'It looks trivial, and it is not',
           '<div style="font-size:29px;line-height:1.75">'
           'The naive answer &mdash; hash the URL, store it, redirect &mdash; takes ninety seconds and '
           'scores nothing.<br><br>'
           'The question is interesting in exactly <b>two</b> places:<br><br>'
           '<b>1. Generating unique short codes</b> at scale, without coordination, without collisions, '
           'and without leaking how many links exist.<br><br>'
           '<b>2. The read path</b>: a hundred-to-one read ratio, single-digit-millisecond redirects, '
           'and what happens the moment the cache is cold or a key goes hot.<br><br>'
           '<span style="color:#ffd483">Everything else is scaffolding. Spend your time on those two, '
           'and say that you are choosing to.</span></div>',
           """So let us be clear about where the marks are. The naive answer — hash the URL, store it, """
           """redirect — takes ninety seconds and scores nothing, because every candidate produces it.""",
           step=0)
seg(sid, 1, """This question is genuinely interesting in exactly two places. First, generating unique short """
            """codes at scale: without coordination, without collisions, and without leaking how many """
            """links exist in your system. That last constraint is one most candidates never mention and """
            """it changes the answer.""")
seg(sid, 2, """Second, the read path: a hundred-to-one read ratio, redirects that must complete in single """
            """digit milliseconds, and what happens the moment your cache is cold or one key goes viral. """
            """Everything else — the load balancer, the stateless service tier — is scaffolding. Spend """
            """your time on those two and, importantly, say out loud that you are choosing to. Announcing """
            """your priorities is itself a Staff signal.""")

think('Before any architecture: what would you clarify? Name the three questions whose answers would change your design most.',
      25,
      """Pause here. Before I show you my clarifying questions, name your own three — the three whose """
      """answers would most change what you draw. Say them out loud.""",
      """Here are mine, and more importantly, here is what each answer changes.""")

clarify('What I would clarify in the first five minutes', [
 ('How many links created per month, and what read-to-write ratio should I assume?',
  'Decides whether writes need sharding at all, and whether the read path needs a cache. '
  '<b>Everything downstream depends on it.</b>'),
 ('Do users need custom aliases?',
  'Custom aliases mean a <b>uniqueness check on write</b>, which changes id generation from '
  '"generate" to "generate or verify". A real branch in the design.'),
 ('Do links expire?',
  'Expiry turns storage from unbounded growth into a <b>bounded working set</b>, and it gives you '
  'a reclamation job to talk about.'),
 ('What latency for the redirect, at p99?',
  'The redirect <i>is</i> the product. A 50 ms p99 rules out anything but a cache hit on the '
  'common path.'),
 ('Do we need click analytics in real time, or is a delay acceptable?',
  'This is the single biggest architectural fork. <b>Real time puts analytics on the request path; '
  'a delay lets it be fully async.</b>'),
 ('Should short codes be unguessable?',
  'Sequential codes are enumerable &mdash; anyone can walk your entire link database. Security '
  'requirement that <b>invalidates the simplest id scheme</b>.'),
], [
 """How many links per month and what read-to-write ratio. Everything downstream depends on these two """
 """numbers, so they come first.""",
 """Do users need custom aliases? This one matters more than it sounds. A custom alias means a """
 """uniqueness check on write, which changes id generation from "generate one" to "generate or verify """
 """one" — a genuine branch in the design.""",
 """Do links expire? Expiry converts storage from unbounded growth into a bounded working set, and it """
 """hands you a reclamation job to discuss later.""",
 """What is the redirect latency target at p ninety-nine? The redirect is the product — nobody cares how """
 """fast you create a link — so a fifty millisecond target rules out anything except a cache hit on the """
 """common path.""",
 """Do we need click analytics in real time, or is a delay acceptable? This is the single biggest """
 """architectural fork in the whole question. Real-time analytics puts work on the request path. An """
 """acceptable delay lets the entire analytics pipeline be asynchronous, and I will show you why that """
 """changes the drawing.""",
 """And the one that impresses: should short codes be unguessable? If they are sequential, anyone can """
 """enumerate your entire database by counting. That is a security requirement, and it invalidates the """
 """simplest id scheme — which is exactly the kind of interaction between requirements that this round """
 """rewards you for spotting.""",
])

sid = beat('Requirements', 'Agreed before anything is drawn',
           '<div class="to-grid" style="top:30px">'
           '<div class="to-opt k-ok" data-step="0"><div class="to-h">Functional</div>'
           '<div style="font-size:24px;line-height:1.5;color:#cfe0f2">'
           '1. Shorten a long URL &rarr; short code<br>'
           '2. Redirect a short code &rarr; original URL<br>'
           '3. Optional custom alias<br>'
           '4. Optional expiry<br>'
           '5. Click analytics<br><br>'
           '<b style="color:#ffd483">#2 is doing all the work.</b> It is ~99% of traffic and the only '
           'one on the user-visible latency path.</div></div>'
           '<div class="to-opt k-shared" data-step="1"><div class="to-h">Non-functional</div>'
           '<div style="font-size:24px;line-height:1.5;color:#cfe0f2">'
           '&bull; Redirect p99 <b>&lt; 50 ms</b><br>'
           '&bull; Availability <b>99.99%</b> on reads &mdash; a dead redirect breaks every link ever '
           'shared<br>'
           '&bull; Durability: losing a mapping is <b>unrecoverable</b><br>'
           '&bull; Codes unguessable<br>'
           '&bull; Analytics may lag <b>minutes</b><br><br>'
           '<b style="color:#ffd483">Dominant constraint: read availability and latency.</b></div></div></div>'
           '<div class="to-dec" data-step="2"><b>Out of scope</b> (agreed): user accounts, billing, '
           'the web UI, spam/malware scanning of target URLs</div>',
           """Here are the requirements I would write on the board. Functionally: shorten, redirect, """
           """optional custom alias, optional expiry, click analytics. And immediately name the one doing """
           """all the work — redirect. It is about ninety-nine percent of traffic and the only operation on """
           """the user-visible latency path.""", step=0)
seg(sid, 1, """Non-functionally, each with a number and a consequence. Redirect p ninety-nine under fifty """
            """milliseconds. Availability of four nines on reads, and here is why that is not a generic """
            """ask: a dead redirect breaks every link ever shared, including ones printed on paper. """
            """Durability matters because losing a mapping is unrecoverable — you cannot regenerate it """
            """from anywhere. Codes must be unguessable. And analytics may lag by minutes.""")
seg(sid, 2, """Then say what is out of scope and get agreement: accounts, billing, the web interface, and """
            """malware scanning of target URLs. That last one is worth naming explicitly because a real """
            """link shortener absolutely needs it, and showing you know that while deliberately excluding """
            """it is stronger than not mentioning it.""")

capacity('Capacity — and what each line decides', [
 ('100M new links / month', '100M &divide; 30 &divide; 100k s', '&asymp; 35 writes / s',
  '<b>One node handles writes.</b> No write sharding needed for throughput'),
 ('Read : write = 100 : 1', '35 &times; 100', '3,500 reads / s',
  'The path that matters. Everything is designed around this'),
 ('Peak 3&times;', '3,500 &times; 3', '&asymp; 10,500 reads / s',
  'At one DB node&rsquo;s limit &rarr; <b>cache is mandatory, not optional</b>'),
 ('500 B &times; 100M/mo &times; 5 yr', '600 GB/yr &times; 5 &times; 3 replicas', '&asymp; 9 TB',
  'One cluster. <b>No tiering, no archival</b> &mdash; say so explicitly'),
 ('Hot 20% of links = 80% of reads', '20M &times; 500 B', '<b>10 GB working set</b>',
  'Fits in RAM &rarr; ~95% hit rate &rarr; DB sees <b>~500 reads/s</b>, not 10,500'),
 ('Code space: 7 chars, base62', '62&#8311;', '3.5 &times; 10&sup1;&sup2; codes',
  '6 billion links over 5 years uses <b>0.2%</b> of the space &mdash; 7 characters is plenty'),
], [
 """The capacity work, run with the template from lesson two. A hundred million links a month is about """
 """thirty-five writes a second, so one node handles writes and I will not shard for write throughput.""",
 """A hundred-to-one read ratio gives three and a half thousand reads a second — and that is the path """
 """everything else gets designed around.""",
 """Three times at peak is about ten and a half thousand reads a second, which sits right at the limit of """
 """a single database node. So the cache is mandatory rather than decorative, and I can say precisely """
 """why.""",
 """Storage over five years with replication is about nine terabytes. One cluster, no tiering, no """
 """archival — and I would say that out loud, because ruling out complexity is as valuable as adding """
 """it.""",
 """The hot set: twenty percent of links taking eighty percent of reads is a ten gigabyte working set, """
 """which fits in memory comfortably. At roughly a ninety-five percent hit rate, the database sees about """
 """five hundred reads a second instead of ten and a half thousand. That is the cache earning its place, """
 """quantified.""",
 """And the code space: seven base-sixty-two characters is three and a half trillion codes. Six billion """
 """links over five years uses two tenths of one percent of it. So seven characters is plenty — which """
 """sets up the question we are about to spend real time on.""",
])

# ------------------------------------------------------------------ API
sid = beat('API design', 'Small surface, and one decision hiding in it',
           '<div class="say" style="top:40px">'
           '<div class="say-l" data-step="0" style="background:rgba(96,165,250,.10);border-left-color:#60a5fa">'
           '<b>POST /v1/links</b> &nbsp;{ url, alias?, expires_at? } &rarr; <b>201</b> { short_code, '
           'short_url }<br>'
           '<span style="font-size:22px;color:#9fb4cc">Idempotency-Key header &rarr; a retry returns the '
           '<i>same</i> code rather than minting a second one</span></div>'
           '<div class="say-l" data-step="1" style="background:rgba(90,215,192,.10)">'
           '<b>GET /{short_code}</b> &rarr; <b>301</b> or <b>302</b> + Location<br>'
           '<span style="font-size:22px;color:#9fb4cc">The whole product. Must be cacheable, must be '
           'fast, must never 500</span></div>'
           '<div class="say-l" data-step="2" style="background:rgba(255,212,131,.10);border-left-color:#ffd483">'
           '<b>GET /v1/links/{code}/stats</b> &rarr; { clicks, by_day, by_country }<br>'
           '<span style="font-size:22px;color:#9fb4cc">Served from the analytics store, never from the '
           'redirect path</span></div></div>',
           """The API is small, and there are two decisions hiding in it. Create a link is a POST that """
           """returns the code. Note the Idempotency-Key header: with it, a client retry returns the same """
           """code instead of minting a second one for the same request. That is a one-line addition that """
           """prevents a whole class of duplicate-creation bugs, and mentioning it early signals """
           """experience.""", step=0)
seg(sid, 1, """The redirect is a GET that returns a three-oh-one or three-oh-two with a Location header. """
            """This is the entire product. It has to be cacheable, it has to be fast, and it must never """
            """return a five hundred.""")
seg(sid, 2, """And stats, served from the analytics store — never, ever from the redirect path. Keeping """
            """those two apart is the architectural decision this API is quietly encoding.""")

sid = beat('301 or 302?', 'A two-line choice with large consequences',
           '<div class="to-grid" style="top:40px">'
           '<div class="to-opt k-info" data-step="0"><div class="to-h">301 Permanent</div>'
           '<ul class="to-p"><li>Browsers and CDNs cache it &mdash; huge load reduction</li>'
           '<li>Fastest possible repeat redirect: zero server hops</li></ul>'
           '<ul class="to-c"><li><b>You stop seeing the clicks</b> &mdash; analytics goes blind</li>'
           '<li>You cannot change or expire the target &mdash; it is cached everywhere</li></ul></div>'
           '<div class="to-opt k-ok" data-step="1"><div class="to-h">302 Found</div>'
           '<ul class="to-p"><li>Every click reaches you &rarr; <b>analytics works</b></li>'
           '<li>You retain control: retarget, expire, block</li></ul>'
           '<ul class="to-c"><li>Every click costs a request &mdash; that is your 10,500/s</li></ul></div>'
           '</div>'
           '<div class="to-dec" data-step="2"><b>Chosen: 302</b> &mdash; because analytics is a stated '
           'functional requirement, and because link takedown is non-negotiable for a public shortener. '
           'The traffic cost is what the cache is for.</div>'
           '<div class="to-flip" data-step="3"><b>What would flip it:</b> if analytics were dropped and '
           'links were immutable, 301 would be strictly better &mdash; and would remove most of the read '
           'load from my system entirely.</div>',
           """Here is a decision candidates skip past in four words and interviewers love to probe: three """
           """oh one or three oh two? Permanent or temporary redirect?""", step=0)
seg(sid, 1, """Three oh one, permanent, gets cached by browsers and CDNs. That is a huge reduction in load — """
            """repeat clicks never reach you at all. But the cost is severe: you stop seeing the clicks, """
            """so analytics goes blind, and you can no longer change or expire the target because the """
            """redirect is cached in a million browsers you do not control.""")
seg(sid, 2, """Three oh two, temporary, means every click reaches you, so analytics works and you keep """
            """control — you can retarget, expire, or block a malicious link. The cost is that every click """
            """is a request, and that is exactly the ten and a half thousand a second we sized for.""")
seg(sid, 3, """I would choose three oh two, and justify it with the requirement: analytics is functional, """
            """and takedown is non-negotiable for a public shortener. The traffic cost is what the cache is """
            """for. And then the reversal sentence: if analytics were dropped and links were immutable, """
            """three oh one would be strictly better and would remove most of the read load from my system """
            """entirely. That is a complete trade-off in thirty seconds.""")

sid = beat('Data model', 'The access pattern picks the store',
           '<div style="font-size:28px;line-height:1.7">'
           '<b>links</b><br>'
           '<span style="font-family:JetBrains Mono,monospace;font-size:24px;color:#9fb4cc">'
           'short_code &nbsp;&nbsp;VARCHAR(11) &nbsp;&larr; <b style="color:#5ad7c0">partition key '
           'and primary key</b><br>'
           'long_url &nbsp;&nbsp;&nbsp;&nbsp;TEXT<br>'
           'created_at &nbsp;&nbsp;TIMESTAMP<br>'
           'expires_at &nbsp;&nbsp;TIMESTAMP NULL<br>'
           'owner_id &nbsp;&nbsp;&nbsp;&nbsp;BIGINT NULL</span><br><br>'
           'Exactly <b>one</b> query matters: <code>short_code &rarr; long_url</code>. No joins, no '
           'range scans, no secondary index on the hot path.<br><br>'
           '<span style="color:#ffd483">So: a key-value store, partitioned by hash of short_code. '
           'The code is random, so the hash distributes perfectly and <b>hot partitions cannot happen '
           'structurally</b> &mdash; only hot <i>keys</i> can.</span></div>',
           """The data model, and I want to work in the order lesson one described: queries first, store """
           """second. There is exactly one query that matters — short code to long URL. No joins, no range """
           """scans, no secondary index on the hot path.""", step=0)
seg(sid, 1, """So: a key-value store, partitioned by the hash of the short code, which is both the primary """
            """key and the partition key. And here is a nice property worth saying out loud — because the """
            """code is random, the hash distributes perfectly, so hot partitions cannot happen """
            """structurally. Only hot individual keys can, which is a different and much easier problem. """
            """Noticing that distinction is exactly the kind of partitioning reasoning an infrastructure """
            """interviewer is listening for.""")
seg(sid, 2, """The analytics data is a completely different shape — append-only, queried by time range and """
            """grouped by dimensions — so it gets a completely different store. Trying to serve both from """
            """one database is the most common structural mistake in this question.""")

# ------------------------------------------------------------------ architecture
A = Arch('Architecture — built up, not revealed', kicker='Progressive disclosure', height=790)
A.box('cl',   70, 330, 180, 100, 'Client', kind='neutral', step=0, focus=0)
A.box('svc', 330, 330, 210, 100, 'Link service', 'stateless', kind='info', step=0, focus=0)
A.box('db',  1120, 330, 230, 100, 'Key-value store', 'short_code &rarr; url', kind='shared', step=0, focus=[0, 5])
A.arrow('cl', 'svc', step=0, focus=0)
A.arrow('svc', 'db', step=0, focus=0, dashed=True)

A.box('lb',  330, 180, 210, 80, 'Load balancer', kind='info', step=1, focus=1, small=True)
A.box('svc2',330, 470, 210, 80, 'Link service &times;N', kind='info', step=1, focus=1, small=True)

A.box('ca',  760, 330, 230, 100, 'Cache', '10 GB hot set', kind='ok', step=2, focus=2)
A.arrow('svc', 'ca', step=2, focus=2)
A.arrow('ca', 'db', step=2, focus=[2, 5])

A.box('idg', 760, 170, 230, 90, 'ID service', 'pre-minted ranges', kind='dp', step=3, focus=3, small=True)
A.arrow('svc', 'idg', step=3, focus=3, dashed=True)

A.box('q',   760, 500, 230, 90, 'Click events', 'async queue', kind='dp', step=4, focus=4, small=True)
A.box('an',  1120, 500, 230, 90, 'Analytics store', 'columnar', kind='dp', step=4, focus=4, small=True)
A.arrow('svc', 'q', step=4, focus=4)
A.arrow('q', 'an', step=4, focus=4)

A.note(1420, 180, '**Every box has a reason:**\\n'
                  '&bull; cache &larr; 10,500 reads/s\\n'
                  '&bull; ID service &larr; no coordination\\n'
                  '&bull; queue &larr; analytics off the\\n&nbsp;&nbsp; request path\\n'
                  '&bull; KV store &larr; one access pattern',
       step=5, kind='ok', w=430, size='m')
A.narrate(0, """Now the architecture, built up rather than revealed. Start with the smallest honest system: """
              """a client, a stateless link service, and a key-value store. This works. It serves the """
              """functional requirement completely — and it falls over at about ten thousand reads a """
              """second. Say both of those things.""")
A.narrate(1, """Peak is ten and a half thousand reads a second, which is more than one service instance """
              """should carry, so a load balancer and horizontal instances. The service is stateless, """
              """which is what makes that trivial — and it is stateless because all the state lives in the """
              """store.""")
A.narrate(2, """The read-to-write ratio says reads dominate a hundred to one, and we computed a ten """
              """gigabyte hot set, so a cache goes on the read path. It absorbs about ninety-five percent """
              """of reads, taking the database from ten and a half thousand a second down to about five """
              """hundred.""")
A.narrate(3, """Writes need unique codes without coordinating on every request, so an id service hands out """
              """pre-minted ranges. That is the first deep dive and we will spend real time on it in a """
              """moment.""")
A.narrate(4, """And analytics must not sit on the redirect path, because the redirect has a fifty """
              """millisecond budget and analytics has a minutes-level tolerance. So clicks are emitted as """
              """events to a queue and land in a columnar store designed for aggregation. Different shape, """
              """different store.""")
A.narrate(5, """Five steps. Every box arrived because a number or a requirement demanded it: the cache """
              """because of ten thousand reads a second, the id service because coordination on every """
              """write is unacceptable, the queue because analytics must stay off a fifty-millisecond """
              """path, and the key-value store because there is exactly one access pattern. If you can """
              """narrate a diagram like that, you have already separated yourself from most candidates.""")
A.build()

# ------------------------------------------------------------------ deep dive 1
sid = beat('Deep dive 1', 'Generating unique short codes — the real question',
           '<div class="bigidea">This is sub-question three in LinkedIn&rsquo;s own pack. '
           'It is where the design is actually decided.</div>'
           '<div style="margin-top:26px;font-size:28px;line-height:1.7">'
           'Four candidate schemes, and each fails somewhere interesting:<br><br>'
           '<b>1. Hash the URL</b> (MD5 &rarr; first 7 chars)<br>'
           '<b>2. Random 7 characters</b><br>'
           '<b>3. A global counter</b>, base62-encoded<br>'
           '<b>4. Pre-minted ranges</b> handed to each node</div>',
           """Deep dive one: generating unique short codes. This is sub-question three in LinkedIn's own """
           """pack, and it is where the design is genuinely decided. There are four candidate schemes and """
           """every one of them fails somewhere interesting, which is what makes it a good interview """
           """question.""")

think('Six billion links over five years, into a seven-character base62 space of 3.5 trillion. If I generate codes at random, how often do I collide?',
      30,
      """Pause on this one, because the arithmetic gives a genuinely surprising answer and it decides """
      """between two of the four schemes. Six billion links, three and a half trillion possible codes. If """
      """you pick codes at random, how often do you collide? Work it out.""",
      """Most people's instinct is "hardly ever — we are only using two tenths of a percent of the space". """
      """That instinct is wrong, and here is why.""")

sid = beat('The birthday arithmetic', 'Why random codes collide constantly',
           '<div style="font-size:29px;line-height:1.75">'
           'Expected collisions &asymp; <b>n&sup2; &divide; 2N</b><br><br>'
           'n = 6 &times; 10&#8313; links &nbsp;&nbsp; N = 3.5 &times; 10&sup1;&sup2; codes<br><br>'
           '<span style="font-family:JetBrains Mono,monospace;color:#9fb4cc">'
           '(6&times;10&#8313;)&sup2; &divide; (2 &times; 3.5&times;10&sup1;&sup2;)<br>'
           '= 3.6&times;10&sup1;&#8313; &divide; 7&times;10&sup1;&sup2;</span><br><br>'
           '&asymp; <b style="color:#ff8f8f">5 million collisions</b><br><br>'
           '<span style="color:#ffd483">So random generation <b>requires a read before every write</b> '
           'to check uniqueness &mdash; and on collision, retry. You have just added a database round '
           'trip to every single link creation.</span></div>',
           """The formula for expected collisions is n squared over two N. Six billion squared is three """
           """point six times ten to the nineteen. Two times three and a half trillion is seven times ten """
           """to the twelve. Divide, and you get about five million collisions.""", step=0)
seg(sid, 1, """Five million. Not "hardly ever" — constantly. The intuition fails because collisions scale """
            """with the square of the number of items, not with how full the space is. This is the """
            """birthday paradox, and it is the single best piece of arithmetic you can produce in this """
            """question.""")
seg(sid, 2, """And it has a direct architectural consequence: random generation requires a read before """
            """every write to check uniqueness, and a retry loop on collision. You have just added a """
            """database round trip to every link creation, and a rare but real retry. That is not fatal at """
            """thirty-five writes a second — but you should know you are paying it, and at ten thousand """
            """writes a second it becomes the bottleneck.""")

tradeoff('Four schemes, honestly compared', [
 ('Hash the URL', 'deny', ['Deterministic: same URL &rarr; same code, free deduplication',
                           'No state needed'],
  ['Collisions still need resolution', '<b>Leaks that two users shortened the same URL</b>',
   'Cannot support custom aliases cleanly', 'Same URL cannot have two different expiries']),
 ('Random 7 chars', 'shared', ['Unguessable &mdash; satisfies the security requirement',
                               'No coordination between nodes'],
  ['<b>~5M collisions</b> at our scale', 'Read-before-write on every creation',
   'Retry loop under contention']),
 ('Global counter', 'deny', ['Zero collisions by construction', 'Shortest possible codes'],
  ['<b>Sequential &rarr; enumerable</b>: anyone can walk your whole database',
   'The counter is a single point of coordination', 'Leaks your growth rate to competitors']),
 ('Pre-minted ranges', 'ok', ['No coordination per write &mdash; one round trip per <b>10,000</b> codes',
                              'Zero collisions by construction',
                              'Unguessable if the range is <b>shuffled</b> before handing out',
                              'Node death loses at most one range &mdash; and codes are not scarce'],
  ['Slightly more moving parts', 'Needs a durable range allocator']),
], decision='Pre-minted, shuffled ranges. A node claims a block of 10,000 codes from a durable '
            'allocator, shuffles it, and serves from memory. One coordination round trip per 10,000 '
            'writes instead of one per write &mdash; and no collisions, ever.',
 flip='If codes did not need to be unguessable, a plain counter with range allocation is simpler and '
      'I would take it. If deduplication of identical URLs were a hard requirement, I would hash '
      'instead and accept the privacy leak.',
 narration=[
  """Here are the four schemes side by side. Hashing the URL is deterministic, so you get free """
  """deduplication — but it leaks that two users shortened the same URL, which is a genuine privacy """
  """problem, and it cannot cleanly support two users wanting different expiries on the same target.""",
  """Random seven characters is unguessable and needs no coordination, but we just showed it costs five """
  """million collisions and a read before every write.""",
  """A global counter has zero collisions by construction and gives the shortest codes — and it fails the """
  """security requirement completely, because sequential codes are enumerable. Anyone can walk your """
  """entire database by counting, and they can measure your growth rate by watching the codes get """
  """longer. Competitors have literally done this.""",
  """Pre-minted ranges: a node claims a block of ten thousand codes from a durable allocator, shuffles """
  """the block, and serves from memory. One coordination round trip per ten thousand writes instead of """
  """one per write. Zero collisions by construction. Unguessable because the block was shuffled. And if """
  """a node dies you lose at most one block of ten thousand codes — which is nothing, because we """
  """calculated the space is two tenths of one percent used.""",
  """So I would choose pre-minted shuffled ranges, and I would say the reversal out loud: if codes did """
  """not need to be unguessable, a plain counter with range allocation is simpler and I would take it. """
  """If deduplicating identical URLs were a hard requirement, I would hash and accept the privacy """
  """leak. That is how you demonstrate the decision was reasoned rather than remembered.""",
 ])

# ------------------------------------------------------------------ deep dive 2
sid = beat('Deep dive 2', 'The read path, and what happens when the cache is not there',
           '<div style="font-size:29px;line-height:1.72">'
           'Happy path: <b>cache hit &rarr; 302</b>. One memory lookup, under a millisecond. 95% of '
           'traffic. Easy.<br><br>'
           'The interesting cases are the other 5%:<br><br>'
           '<b>&bull; Cold cache</b> after a deploy or restart &rarr; 10,500 req/s hit the database at '
           'once<br>'
           '<b>&bull; A viral link</b> &rarr; one key takes 50,000 req/s &mdash; a <b>hot key</b>, not a '
           'hot partition<br>'
           '<b>&bull; A cache miss stampede</b> &rarr; 10,000 concurrent requests for the <i>same</i> '
           'missing key, all going to the database<br><br>'
           '<span style="color:#ffd483">Each has a different fix. Naming all three is the deep dive.</span></div>',
           """Deep dive two: the read path. The happy path is boring — cache hit, three oh two, one memory """
           """lookup, under a millisecond, ninety-five percent of traffic. Nobody gets marks for that.""",
           step=0)
seg(sid, 1, """The interesting cases are the other five percent, and there are three distinct ones. A cold """
            """cache after a deploy or a restart, where suddenly ten and a half thousand requests a second """
            """all reach the database at once. A viral link, where a single key takes fifty thousand """
            """requests a second — and note that is a hot key, not a hot partition, which we established """
            """cannot happen here. And a cache miss stampede, where ten thousand concurrent requests for """
            """the same missing key all go to the database simultaneously.""")
seg(sid, 2, """Each has a different fix, and naming all three with their distinct remedies is what the deep """
            """dive actually is. Candidates who say "add a cache" and stop have described the happy path """
            """and nothing else.""")

sid = beat('The three fixes', 'Different problems, different answers',
           '<table class="fail" style="top:50px"><thead><tr><th>Problem</th><th>Why it hurts</th>'
           '<th>Fix</th></tr></thead><tbody>'
           '<tr data-step="0"><td class="f-c">Cold cache</td>'
           '<td>Deploy or restart &rarr; 0% hit rate &rarr; DB takes 20&times; its normal load</td>'
           '<td><b>Warm on start</b> from the top-N list; roll deploys so only a fraction of the fleet '
           'is cold at once</td></tr>'
           '<tr data-step="1"><td class="f-c">Hot key</td>'
           '<td>One viral link &rarr; 50k req/s to a single cache node &rarr; that node saturates</td>'
           '<td><b>Local in-process cache</b> in front of the shared cache. A hot key is hot '
           '<i>everywhere</i>, so a 1-second local TTL absorbs it completely</td></tr>'
           '<tr data-step="2"><td class="f-c">Miss stampede</td>'
           '<td>10k concurrent misses for the same key &rarr; 10k identical DB queries</td>'
           '<td><b>Request coalescing</b>: first miss fetches, the rest wait on that one in-flight '
           'request. One DB query, not 10,000</td></tr>'
           '<tr data-step="3"><td class="f-c">Cache down</td>'
           '<td>Entire cache tier lost &rarr; 10,500 req/s onto a DB sized for 500</td>'
           '<td><b>Do not fail open blindly.</b> Local caches absorb the head; shed or queue the tail. '
           'Better a slow 5% than a dead 100%</td></tr>'
           '</tbody></table>',
           """Cold cache: warm it on start from a stored top-N list, and roll your deploys so only a """
           """fraction of the fleet is cold at any moment. That turns a cliff into a ripple.""", step=0)
seg(sid, 1, """Hot key: put a small in-process cache in front of the shared cache. The insight is that a hot """
            """key is hot on every node simultaneously, so even a one-second local time-to-live absorbs it """
            """completely — fifty thousand requests a second becomes one request per node per second. """
            """This is a genuinely good answer and very few candidates reach for it.""")
seg(sid, 2, """Miss stampede: request coalescing, sometimes called single-flight. The first miss goes to the """
            """database; every other request for that same key waits on the in-flight result. Ten thousand """
            """identical queries become one. This is the fix people most often miss, and it is the one """
            """that actually saves you during an incident.""")
seg(sid, 3, """And the whole cache tier dying. The naive answer is "fail open, go to the database" — but """
            """that puts ten and a half thousand requests a second onto a database sized for five hundred, """
            """so you have converted a degradation into an outage. The better answer: local caches absorb """
            """the head of the distribution, and you shed or queue the tail. A slow five percent beats a """
            """dead hundred percent, and saying that trade-off out loud is exactly the reliability """
            """reasoning the scorecard asks for.""")

# ------------------------------------------------------------------ async + failures
sid = beat('Async', 'Click analytics: the fork that keeps the redirect fast',
           '<div style="font-size:29px;line-height:1.7">'
           'Every redirect emits an event: <span style="font-family:JetBrains Mono,monospace;font-size:23px;'
           'color:#9fb4cc">{ code, ts, ip&rarr;country, referrer, user_agent }</span><br><br>'
           '<b>Fire-and-forget to a local buffer, flushed in batches</b> &mdash; never a synchronous '
           'write on the redirect path. The redirect must not slow down or fail because analytics is '
           'having a bad day.<br><br>'
           'Then: queue &rarr; stream processor &rarr; columnar store, with rollups per minute, hour '
           'and day.<br><br>'
           '<span style="color:#ffd483">Delivery guarantee: <b>at-least-once</b>, and dedupe on a '
           'click id at aggregation time. Nobody needs exactly-once click counting &mdash; and saying '
           'that, rather than reaching for exactly-once, is the senior answer.</span></div>',
           """Async processing, which for this system means click analytics. Every redirect emits an event """
           """with the code, a timestamp, a country derived from the IP, referrer and user agent.""",
           step=0)
seg(sid, 1, """Crucially, that emit is fire-and-forget into a local buffer that flushes in batches. It is """
            """never a synchronous write on the redirect path. The redirect must not slow down, and must """
            """certainly not fail, because the analytics pipeline is having a bad day. If you take one """
            """thing from this section: the availability of your product should never depend on the """
            """availability of your reporting.""")
seg(sid, 2, """Then queue, stream processor, columnar store, with rollups per minute, hour and day so the """
            """stats endpoint reads a pre-aggregated row rather than scanning raw events.""")
seg(sid, 3, """And the delivery guarantee — this is a favourite follow-up. At-least-once, with """
            """deduplication on a click id at aggregation time. And I would add: nobody needs exactly-once """
            """click counting. A count that is correct to within a tenth of a percent is fine for this """
            """product, and exactly-once would cost coordination on the hottest path in the system. """
            """Pushing back on an unnecessary guarantee is a strong signal — juniors accept requirements, """
            """seniors interrogate them.""")

failures('What happens when each piece dies', [
 ('Link service instance', 'Nothing &mdash; the load balancer routes around it',
  'Stateless, so recovery is replacement. Capacity must assume N&minus;1'),
 ('Cache node', 'Slightly higher latency for the keys that node held',
  'Consistent hashing means only <b>1/N of keys</b> move; the rest are untouched'),
 ('Whole cache tier', 'Slower redirects; some requests shed',
  'Local caches take the head. <b>Do not blindly fail open</b> &mdash; that converts degradation '
  'into an outage'),
 ('Database primary', 'Writes fail; <b>reads continue from cache and replicas</b>',
  'Failover to a replica. Creation is 1% of traffic, so 99% of the product still works'),
 ('ID allocator', 'New links cannot be created after the current range is exhausted',
  'Each node holds 10,000 codes &mdash; <b>hours of headroom</b>. Alert on range depletion, not on '
  'allocator death'),
 ('Analytics queue', '<b>Nothing user-visible</b>',
  'Buffer locally, drop oldest under pressure. Stats lag. <b>This is the correct thing to sacrifice</b>'),
 ('Entire region', 'Depends entirely on whether you agreed multi-region at minute five',
  'If single-region: an outage, with an RTO you should state. Do not invent multi-region unasked'),
], [
 """The failure table, and I would walk this in the interview rather than wait to be asked. A link """
 """service instance dying is invisible — the load balancer routes around it, it is stateless, and """
 """recovery is replacement. But say the consequence: your capacity planning must assume N minus one.""",
 """A single cache node: slightly higher latency for the keys it held. With consistent hashing only one """
 """Nth of keys move, and everything else is untouched — which is the reason to use consistent hashing """
 """rather than modulo hashing, and worth saying.""",
 """The whole cache tier, which we covered: local caches take the head, and do not blindly fail open.""",
 """The database primary: writes fail, but reads continue from cache and replicas. Failover to a """
 """replica. And here is the reassuring arithmetic — creation is one percent of traffic, so during a """
 """primary failure ninety-nine percent of your product still works perfectly. That is a direct """
 """consequence of the read-write ratio, and connecting the two shows the design hangs together.""",
 """The id allocator dying: new links cannot be created once the current range is exhausted. But each """
 """node holds ten thousand codes, which at thirty-five writes a second across the fleet is hours of """
 """headroom. So the alert is on range depletion, not on allocator death — you have time.""",
 """The analytics queue: nothing user-visible at all. Buffer locally, drop the oldest under pressure, """
 """stats lag behind. This is the correct thing to sacrifice, and saying "this is what I would choose to """
 """lose" is a mature answer.""",
 """And an entire region, which depends completely on whether you agreed multi-region at minute five. If """
 """single-region, it is an outage and you should state your recovery time objective rather than pretend """
 """otherwise. Do not invent multi-region that nobody asked for.""",
])

sid = beat('Observability, security, cost', 'The three sections candidates rush',
           '<div class="to-grid" style="top:24px">'
           '<div class="to-opt k-info" data-step="0"><div class="to-h">What I would alert on</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; <b>Redirect p99</b> &mdash; the product<br>'
           '&bull; <b>Cache hit ratio</b> &mdash; drops <i>before</i> latency does<br>'
           '&bull; <b>ID range remaining</b> &mdash; leading indicator, hours of warning<br>'
           '&bull; 4xx rate &mdash; a spike means enumeration<br>'
           '&bull; Queue lag &mdash; stats freshness<br><br>'
           '<span style="color:#ffd483">Hit ratio and range depletion are <b>leading</b>; latency is '
           '<b>lagging</b>.</span></div></div>'
           '<div class="to-opt k-shared" data-step="1"><div class="to-h">Security</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; Codes <b>unguessable</b> &mdash; already designed in<br>'
           '&bull; Rate limit creation per account and per IP<br>'
           '&bull; <b>Open redirect</b>: validate scheme, block internal IP ranges &mdash; or you are a '
           'proxy into the VPC<br>'
           '&bull; Malware/phishing scan (async) + takedown path<br>'
           '&bull; TLS everywhere; encrypt at rest</div></div>'
           '<div class="to-opt k-ok" data-step="2"><div class="to-h">Cost</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; 9 TB storage is <b>trivial</b> &mdash; hundreds of dollars<br>'
           '&bull; The bill is <b>bandwidth and request volume</b><br>'
           '&bull; Biggest lever: <b>301 instead of 302</b> would remove most traffic &mdash; but '
           'costs analytics<br>'
           '&bull; Second lever: longer cache TTL<br><br>'
           '<span style="color:#ffd483">Cost and product are the same conversation here.</span></div></div></div>',
           """Observability, security and cost — three sections candidates rush and where a couple of """
           """sharp sentences go a long way. On observability, do not list metrics; say what you would """
           """alert on. Redirect p ninety-nine because it is the product. Cache hit ratio, because it """
           """drops before latency does. Id range remaining, which gives you hours of warning. A spike in """
           """four-oh-fours, because that means somebody is enumerating you. And queue lag for stats """
           """freshness.""", step=0)
seg(sid, 1, """The framing that sounds experienced: hit ratio and range depletion are leading indicators; """
            """latency is a lagging one. You want to be paged by the leading indicator, because by the """
            """time latency moves, users have already noticed.""")
seg(sid, 2, """On security, one item matters more than the rest and almost nobody raises it: open redirect. """
            """If you let anyone shorten any URL and then redirect to it, you must validate the scheme and """
            """block internal IP ranges — otherwise your shortener is a proxy into your own private """
            """network, and it will be used as one. Plus rate limiting creation, async malware scanning """
            """with a takedown path, and the standard encryption story.""")
seg(sid, 3, """On cost: nine terabytes of storage is trivial, a few hundred dollars. Your bill is bandwidth """
            """and request volume. The biggest lever is the three-oh-one versus three-oh-two decision we """
            """made earlier — switching would remove most of your traffic but costs you analytics. So cost """
            """and product are the same conversation here, and pointing that out is a Staff-level """
            """observation rather than an engineering one.""")

# ------------------------------------------------------------------ staff follow-ups
sid = cards('Staff-level follow-ups, and how I would answer', [
 (0, '&ldquo;Traffic goes 10&times;. What changes?&rdquo;',
  '105k reads/s. The <b>cache tier</b> scales horizontally &mdash; it is already the answer. The DB barely notices, because it still only sees misses. <b>Nothing structural changes</b>, and saying that confidently is the answer.', 'ok'),
 (0, '&ldquo;One link goes viral &mdash; 500k req/s on one key.&rdquo;',
  'Hot key, not hot partition. Local in-process cache with a 1s TTL collapses it to one fetch per node per second. If still hot, serve it from the edge/CDN.', 'ok'),
 (1, '&ldquo;Now we need custom aliases.&rdquo;',
  'A different write path: <b>conditional insert</b> on the alias, 409 on conflict. Keeps the generated-code path untouched. Reserve a namespace so aliases cannot collide with generated codes.', 'ok'),
 (1, '&ldquo;Make analytics real-time.&rdquo;',
  'Push back first: real-time <i>for whom</i>? If a dashboard, a 10s rollup is real-time enough. If it must be sub-second, that is a streaming aggregation with approximate counters &mdash; and I would use HyperLogLog for uniques.', 'shared'),
 (2, '&ldquo;GDPR: delete everything for a user.&rdquo;',
  'Links are easy &mdash; delete by owner. The hard part is the <b>analytics store and its rollups</b>, which are aggregated and immutable. Either keep raw events addressable by user, or aggregate so no individual is identifiable. <b>Decide at design time.</b>', 'deny'),
 (2, '&ldquo;Cost tripled. Where do you look?&rdquo;',
  'Bandwidth first &mdash; it dominates. Check cache hit ratio (a drop multiplies DB and egress), check whether a bot is enumerating, and re-examine 302 vs 301 for links that no longer need analytics.', 'ok'),
], cols=2)
seg(sid, 0, """Now the Staff-level follow-ups, and I want to model the answers because the shape matters. """
            """Traffic goes ten times: a hundred and five thousand reads a second. The cache tier scales """
            """horizontally and it is already the answer; the database barely notices because it still """
            """only sees misses. So nothing structural changes — and being able to say that confidently, """
            """rather than inventing new components to look busy, is the right answer. Knowing when your """
            """design already handles something is as valuable as changing it.""")
seg(sid, 1, """One link goes viral at half a million requests a second on a single key: hot key, not hot """
            """partition, and the local cache with a one-second time-to-live collapses it to one fetch per """
            """node per second. If it is still hot, push it to the edge.""")
seg(sid, 2, """Custom aliases: a separate write path with a conditional insert and a four-oh-nine on """
            """conflict, leaving the generated path untouched — plus reserving a namespace so aliases """
            """cannot collide with generated codes. That last detail is the one interviewers wait for.""")
seg(sid, 3, """Make analytics real-time: push back first. Real time for whom? If it is a dashboard, a """
            """ten-second rollup is real-time enough, and you have saved an enormous amount of """
            """complexity. If it genuinely must be sub-second, that is streaming aggregation with """
            """approximate counters, and I would name HyperLogLog for unique counts.""")
seg(sid, 4, """The GDPR question, which is the hardest one here. Deleting links is easy — delete by owner. """
            """The hard part is the analytics store, because rollups are aggregated and immutable. You """
            """either keep raw events addressable by user, or you aggregate so that no individual is """
            """identifiable. And the real answer is that you decide this at design time, not when the """
            """request arrives, because retrofitting deletion into an aggregation pipeline is brutal.""")
seg(sid, 5, """And cost tripled: look at bandwidth first because it dominates, check whether the cache hit """
            """ratio dropped — since that multiplies both database load and egress — check whether a bot """
            """is enumerating you, and revisit the three-oh-two decision for links that no longer need """
            """analytics.""")

followups(
 ['Scaling reads &mdash; <b>named in the pack</b>',
  'Guaranteeing unique short codes &mdash; <b>named in the pack</b>',
  'Click analytics &mdash; <b>named in the pack</b>',
  'Custom aliases and expiry'],
 ['"Why 302 and not 301?" &mdash; and the analytics consequence',
  '"What happens when the cache tier dies?" &mdash; do not fail open blindly',
  '"How do you stop someone enumerating every link?"',
  '"Delete a user\'s data, including from rollups"',
  '"Ten times the traffic" &mdash; and the correct answer may be "nothing changes"'],
 """The pack names four follow-ups explicitly: scaling reads, guaranteeing unique codes, click """
 """analytics, and the core service itself. Custom aliases and expiry come up constantly alongside """
 """them. If you prepare nothing else for this question, prepare those.""",
 """And these are the ones I would expect on top, based on where the design has genuine tension. Why """
 """three-oh-two rather than three-oh-one. What happens when the cache tier dies — with the trap being """
 """that failing open sounds right and is wrong. How you stop enumeration. Deletion including from """
 """rollups. And the ten-times question, where the strongest answer may well be "nothing structural """
 """changes, and here is why".""")

say('What I should say — the sentences that carry this design', [
 'The redirect is about ninety-nine percent of traffic and the only thing on the user-visible latency path, so I am going to optimise for it and treat creation as a background concern.',
 'Seven base-62 characters gives three and a half trillion codes, and we need six billion — but if I generate randomly, the birthday bound says about five million collisions, so random needs a read before every write.',
 'That is why I am pre-minting shuffled ranges: one coordination round trip per ten thousand writes instead of one per write, no collisions, and the codes stay unguessable.',
 'I am choosing 302 over 301 because analytics is a stated requirement and I need to be able to take a link down. If we dropped analytics, 301 would be strictly better.',
 'When the cache tier dies I would not fail open — that puts ten thousand requests a second onto a database sized for five hundred and turns a degradation into an outage.',
 'Analytics is at-least-once with dedupe at aggregation. Nobody needs exactly-once click counting, and it would cost coordination on my hottest path.',
 'The biggest risk in this design is a viral link creating a hot key, so I would load test that deliberately before trusting it.',
], [
 """These are the seven sentences I would drill for this question. The first establishes your priority """
 """and gives you permission to spend the hour where the marks are.""",
 """The second is the birthday arithmetic, and it is the single most impressive thing you can say here, """
 """because it is a real calculation with a surprising result that changes the design.""",
 """The third is your id decision with its justification attached, stated as a rate comparison rather """
 """than as a preference.""",
 """The fourth is the three-oh-two trade-off with the reversal — choice, reason, and what would flip """
 """it.""",
 """The fifth is the failure insight that most candidates get backwards, and it will be remembered.""",
 """The sixth pushes back on an unnecessary guarantee, which is a senior move.""",
 """And the seventh names your own biggest risk and says how you would go looking for it. Close on that """
 """one. Candidates think naming a weakness costs them; it does the opposite, because operating real """
 """systems is mostly discovering where your design was wrong.""",
])

cheatsheet('URL shortener — the revision card', [
 ('Problem', 'Shorten, redirect, analytics. Redirect is 99% of traffic'),
 ('Scale', '35 writes/s &middot; 10.5k reads/s peak &middot; 9 TB over 5 yr'),
 ('Dominant constraint', 'Read latency and availability'),
 ('Architecture', 'LB &rarr; stateless service &rarr; cache &rarr; KV store; async click pipeline'),
 ('Data store', 'KV, partitioned by hash(short_code); analytics in columnar'),
 ('Key', 'short_code = primary <i>and</i> partition key'),
 ('ID generation', '<b>Pre-minted shuffled ranges</b>, 10k per node'),
 ('Why not random', 'Birthday bound &rarr; ~5M collisions &rarr; read-before-write'),
 ('Why not counter', 'Sequential codes are enumerable'),
 ('Cache', '10 GB hot set, ~95% hit, local L1 for hot keys'),
 ('Stampede', 'Request coalescing &mdash; one fetch, not 10,000'),
 ('Consistency', 'Eventual is fine; a link is immutable once created'),
 ('Redirect code', '302, to keep analytics and takedown'),
 ('Analytics', 'At-least-once, dedupe on click id, rollups'),
 ('Failure', 'Cache tier down &rarr; do <b>not</b> fail open; shed the tail'),
 ('Alert on', 'Hit ratio and ID range &mdash; both <b>leading</b> indicators'),
 ('Security', 'Unguessable codes; <b>block open redirect to internal IPs</b>'),
 ('Cost', 'Bandwidth dominates; 301 is the big lever, at a product cost'),
 ('10&times; traffic', 'Scale the cache tier. <b>Nothing structural changes</b>'),
 ('Biggest risk', 'Hot key from a viral link'),
], [
 """The revision card, and this is the page to reread the morning of the interview. Problem, scale, and """
 """the dominant constraint — read latency and availability.""",
 """Architecture in one line, the two stores and why they are different, and the key that is both """
 """primary and partition key.""",
 """Then the id decision with both rejections attached, because that is the deep dive: pre-minted """
 """shuffled ranges, not random because of the birthday bound, not a counter because sequential codes """
 """are enumerable.""",
 """The cache facts: ten gigabyte hot set, ninety-five percent hit rate, a local first-level cache for """
 """hot keys, and coalescing for stampedes.""",
 """Consistency, the redirect code choice, and the analytics guarantee.""",
 """The failure line that matters most — do not fail open — and the two leading indicators to alert on.""",
 """Security, cost, the ten-times answer, and your biggest risk. Twenty lines. If you can reconstruct """
 """the whole design from this card, you are ready for this question.""",
])

sid = statement('Lesson 2.1', 'The easy-looking question is where depth shows most.',
                'Everyone can draw the boxes. Almost nobody computes the birthday bound, distinguishes a hot key from a hot partition, or refuses to fail open.',
                kind='ok')
seg(sid, 0, """One line to close. The easy-looking question is where depth shows most.""")
seg(sid, 1, """Everyone can draw these boxes. Almost nobody computes the birthday bound and lets it choose """
            """the id scheme, almost nobody distinguishes a hot key from a hot partition, and almost """
            """nobody refuses to fail open when the cache dies. Those three moments are the whole """
            """interview, and they took about six minutes of the hour. Next lesson: typeahead — three """
            """independent candidate reports, the most LinkedIn-shaped question in the set, and one where """
            """the latency budget does the deciding.""")
