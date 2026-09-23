# -*- coding: utf-8 -*-
"""Chapter 1, Lesson 1 — how to approach a Staff-level system design interview."""
from lib import *

lesson_header('1.1', 'How to approach a Staff-level system design interview',
              'The twenty steps, and what to say at each one', None, 30,
              """Welcome to the LinkedIn system design course. This first lesson is the most important one, """
              """and it contains no architecture at all. It is about method — how to open, how to scope, how """
              """to move through a design in the right order, and above all what to say while you do it. """
              """Here is why that matters more than any particular answer. You cannot revise every possible """
              """question. What you can do is arrive with a method so solid that a question you have never """
              """seen becomes routine. That is what a Staff-level interviewer is actually testing, and it is """
              """what this lesson gives you.""")

# ------------------------------------------------------------------ what is scored
sid = beat('The round', 'What this round actually scores',
           '<div style="font-size:31px;line-height:1.75">'
           'LinkedIn&rsquo;s own preparation pack describes the Systems and Infrastructure design module in '
           'five words:<br><br>'
           '<b>&bull; completeness</b><br>'
           '<b>&bull; quality of decisions</b><br>'
           '<b>&bull; reasoning about scalability and performance</b><br>'
           '<b>&bull; reliability and fault tolerance</b><br>'
           '<b>&bull; extensibility</b><br><br>'
           'Notice what is <i>not</i> on that list: knowing the answer.</div>',
           """Start with what is being scored, because it should shape everything you do. LinkedIn's own """
           """preparation pack — the one the recruiter sends — describes this module in five phrases. """
           """Completeness. Quality of decisions. Reasoning about scalability and performance. Reliability """
           """and fault tolerance. Extensibility.""", step=0)
seg(sid, 1, """Read that list again and notice what is missing from it. Nowhere does it say "arrives at the """
            """correct architecture". Every one of those five is about how you reason, not about what you """
            """land on. Quality of decisions, not correctness of decisions. That distinction is the whole """
            """round.""")

sid = compare('The two candidates I see most often',
 ('The encyclopedia', 'deny', 0,
  ['Recognises the question, recites a known architecture',
   'Draws the full diagram in the first five minutes',
   'Every component is correct; none is <b>justified</b>',
   'Falls apart on "why?" and on any twist',
   'Reads as: <i>has memorised designs</i>']),
 ('The engineer', 'ok', 1,
  ['Scopes the problem before drawing anything',
   'Derives the architecture from numbers and requirements',
   'Names a trade-off at every decision',
   'A twist is interesting rather than fatal',
   'Reads as: <i>has built systems</i>']))
seg(sid, 0, """There are two candidates I see over and over. The first recognises the question, recites a """
            """known architecture, and draws the whole diagram in five minutes. Every box is correct. Not """
            """one of them is justified. Then the interviewer asks why, or changes one requirement, and the """
            """whole thing falls over — because it was recalled, not derived.""")
seg(sid, 1, """The second scopes the problem first, derives the architecture from the numbers, and names a """
            """trade-off at every decision. When the interviewer adds a twist, that candidate finds it """
            """interesting rather than fatal, because they know which decisions the twist actually touches. """
            """One reads as someone who has memorised designs. The other reads as someone who has built """
            """systems. The method in this lesson is how you become the second one — and I want to be """
            """clear, it is a method, not a talent.""")

# ------------------------------------------------------------------ the shape
sid = beat('The shape', 'The twenty steps, in four movements',
           '<div style="font-size:29px;line-height:1.7">'
           '<b>1. SCOPE</b> &nbsp;<span style="color:#9fb4cc">clarify &middot; functional &middot; '
           'non-functional &middot; scale</span><br>'
           '<b>2. SIZE</b> &nbsp;<span style="color:#9fb4cc">traffic &middot; storage &middot; bandwidth '
           '&middot; what the numbers force</span><br>'
           '<b>3. SHAPE</b> &nbsp;<span style="color:#9fb4cc">API &middot; data model &middot; '
           'architecture &middot; bottlenecks</span><br>'
           '<b>4. STRESS</b> &nbsp;<span style="color:#9fb4cc">deep dive &middot; failures &middot; '
           'consistency &middot; observability &middot; security &middot; cost &middot; trade-offs '
           '&middot; summary</span>'
           '</div>',
           """Twenty steps sounds like a lot to hold in your head under pressure, so group them into four """
           """movements. Scope: clarify, functional requirements, non-functional requirements, scale. Size: """
           """traffic, storage, bandwidth, and what those numbers force. Shape: the API, the data model, the """
           """architecture, and where it bottlenecks. Stress: deep dive, failures, consistency, """
           """observability, security, cost, trade-offs, and a summary.""", step=0)
seg(sid, 1, """Four words: scope, size, shape, stress. If you remember nothing else from this lesson, """
            """remember those four and their order. Almost every candidate who struggles does so because """
            """they jumped straight to shape — they started drawing before they scoped and sized, and then """
            """every later decision had nothing to stand on.""")

sid = beat('The clock', 'How to spend a sixty-minute round',
           '<table class="cap" style="top:60px"><thead><tr><th>Minutes</th><th>Movement</th>'
           '<th>What must exist by the end of it</th></tr></thead><tbody>'
           '<tr data-step="0"><td class="mono">0&ndash;8</td><td>Scope</td>'
           '<td class="imp">An agreed, written list of what you are building &mdash; and what you are not</td></tr>'
           '<tr data-step="1"><td class="mono">8&ndash;15</td><td>Size</td>'
           '<td class="imp">Numbers on the board, and one sentence on what they rule out</td></tr>'
           '<tr data-step="2"><td class="mono">15&ndash;30</td><td>Shape</td>'
           '<td class="imp">API, data model, and an architecture you built up in front of them</td></tr>'
           '<tr data-step="3"><td class="mono">30&ndash;50</td><td>Stress</td>'
           '<td class="imp">Two deep dives, the failure story, and the trade-offs named out loud</td></tr>'
           '<tr data-step="4"><td class="mono">50&ndash;60</td><td>Close</td>'
           '<td class="imp">Summary, biggest risk, what you would build first</td></tr>'
           '</tbody></table>',
           """Here is how to spend the hour, and I want you to internalise the timings because running out """
           """of clock is one of the most common ways strong candidates lose this round. Eight minutes on """
           """scope. By the end of it there is an agreed written list of what you are building and what you """
           """are explicitly not building.""", step=0)
seg(sid, 1, """Seven minutes on size. By the end there are numbers on the board and one sentence about what """
            """they rule out. The numbers are not decoration — they exist to eliminate designs.""")
seg(sid, 2, """Fifteen minutes on shape: API, data model, and an architecture you built up in front of them """
            """rather than presented whole.""")
seg(sid, 3, """Twenty minutes on stress, which is where the level is decided: two deep dives, the failure """
            """story, and the trade-offs named out loud.""")
seg(sid, 4, """And ten minutes to close: summary, biggest risk, what you would build first. If you are still """
            """drawing boxes at minute fifty, you have already lost marks you cannot get back — not for """
            """being wrong, but for never reaching the part where the level is judged.""")

# ------------------------------------------------------------------ movement 1
sid = beat('Movement 1 — scope', 'Do not design the question you were asked',
           '<div class="bigidea">Every interview question is deliberately under-specified. '
           'The first thing being tested is whether you notice.</div>'
           '<div style="margin-top:28px;font-size:29px;line-height:1.7">'
           '&ldquo;Design a URL shortener&rdquo; could mean a weekend project or a system serving a '
           'hundred thousand redirects a second. Those are <b>not the same design</b>, and nothing in '
           'the sentence tells you which one they want.<br><br>'
           'So the first move is never architecture. It is <b>turning an ambiguous sentence into an '
           'agreed specification</b>.</div>',
           """Movement one, scope. And the principle underneath it is this: every system design question """
           """is deliberately under-specified, and the first thing being tested is whether you notice.""",
           step=0)
seg(sid, 1, """Design a URL shortener could mean a weekend project or a system serving a hundred thousand """
            """redirects per second. Those are not the same design — different storage, different caching, """
            """possibly different consistency model. And nothing in the sentence tells you which one they """
            """want.""")
seg(sid, 2, """So your first move is never architecture. It is turning an ambiguous sentence into an agreed """
            """specification. And notice the word agreed. You are not guessing privately, you are """
            """negotiating publicly, and that negotiation is itself scored.""")

clarify('The seven questions that actually change the architecture', [
 ('How many users, and how much traffic should I design for?',
  'The single highest-leverage question. It decides single-node versus distributed, and it is the '
  'input to every later number.'),
 ('What is the read to write ratio?',
  'Read-heavy means <b>caching and replicas</b>. Write-heavy means <b>partitioning and ingestion</b>. '
  'These are different systems.'),
 ('What latency do we need, and at which percentile?',
  '<b>p99 is the design constraint, not p50.</b> A 100 ms p99 rules out cross-region round trips on the '
  'request path.'),
 ('Does this need to be strongly consistent, or is eventual acceptable?',
  'Decides whether you can replicate freely and cache aggressively, or whether you are pinned to a '
  'single writer.'),
 ('How long do we keep the data?',
  'Retention multiplied by daily volume <b>is</b> your storage bill, and it decides whether you need '
  'tiering and archival at all.'),
 ('Is this one region or global?',
  'Global means replication strategy, data residency and failover. Do not volunteer it &mdash; but '
  'ask, because it changes everything.'),
 ('What is out of scope?',
  'The most under-used question. Getting auth, billing or the ML model explicitly excluded buys you '
  'the time to go deep where it counts.'),
], [
 """Here are the seven questions that actually change the architecture. There are dozens you could ask; """
 """these are the ones whose answers make you draw something different. How many users and how much """
 """traffic — the highest-leverage question there is, because it decides single node versus distributed """
 """and feeds every later number.""",
 """What is the read to write ratio. This one genuinely splits the design space: read-heavy leads you to """
 """caching and replicas, write-heavy leads you to partitioning and ingestion pipelines. Those are """
 """different systems, and knowing which one you are building in the first five minutes saves you from """
 """rebuilding at minute forty.""",
 """What latency, and at which percentile — and say the percentile yourself, because p ninety-nine is """
 """the design constraint while p fifty is a vanity number. A hundred millisecond p ninety-nine quietly """
 """rules out a cross-region round trip on the request path, and you want to discover that now rather """
 """than after you have drawn one.""",
 """Do we need strong consistency or is eventual acceptable. That decides whether you may replicate """
 """freely and cache aggressively, or whether you are pinned to a single writer.""",
 """How long do we keep the data. Retention times daily volume is your storage bill, and it is the """
 """number that decides whether you need tiering and archival at all.""",
 """One region or global. Do not volunteer multi-region — it is the classic way to over-engineer an """
 """answer — but do ask, because if they say global, replication, residency and failover all enter the """
 """design.""",
 """And the most under-used question in the entire interview: what is out of scope? Getting """
 """authentication, billing or the recommendation model explicitly excluded is not laziness. It buys you """
 """the minutes to go deep where the marks actually are, and it demonstrates the scoping instinct the """
 """pack says it is looking for.""",
])

say('What I should say — opening the round', [
 'Before I design anything, I want to pin down scale and latency, because those two decide most of the architecture.',
 'Can I assume this is read-heavy? If reads dominate writes by a hundred to one, I will lean on caching and replicas.',
 'What p99 latency are we targeting? I am asking because anything under about a hundred milliseconds rules out a cross-region hop on the request path.',
 'I am going to treat authentication and billing as out of scope so I can go deep on the data path — tell me if you want them in.',
 'Let me write these down as functional and non-functional requirements so we agree before I draw anything.',
], [
 """Now, the words. This is the part of the course I most want you to practise out loud, because in this """
 """round the reasoning only counts if it leaves your head. Open like this: before I design anything, I """
 """want to pin down scale and latency, because those two decide most of the architecture. That sentence """
 """does two jobs — it starts the scoping, and it tells the interviewer you know why you are scoping.""",
 """Then ask about the read-write ratio with your hypothesis attached. Not "is it read-heavy?" but "can I """
 """assume this is read-heavy, and if so I will lean on caching and replicas". You are showing the """
 """consequence of the answer, which is much stronger than asking a bare question.""",
 """Same with latency: ask for the number and say what it would rule out. And then explicitly park what """
 """is out of scope, offering to bring it back if they want it.""",
 """Finally, write the requirements down and say you are writing them down. That single habit — """
 """summarising the agreement before moving on — is what completeness looks like from the other side of """
 """the table.""",
])

sid = beat('Requirements', 'Functional and non-functional are not the same list',
           '<div class="to-grid" style="top:40px">'
           '<div class="to-opt k-ok" data-step="0"><div class="to-h">Functional</div>'
           '<div style="font-size:25px;line-height:1.5;color:#cfe0f2">What the system <b>does</b>. '
           'Verbs. A user can shorten a URL. A user can follow a short link.<br><br>'
           'Keep it to <b>three or four</b>. Then say which one is quietly doing all the work.</div></div>'
           '<div class="to-opt k-shared" data-step="1"><div class="to-h">Non-functional</div>'
           '<div style="font-size:25px;line-height:1.5;color:#cfe0f2">What the system must <b>be</b>. '
           'Adjectives with numbers attached. Available. Fast at p99. Durable.<br><br>'
           'Each one must come with a <b>number</b> and with <b>what it forces</b>.</div></div></div>'
           '<div class="to-dec" data-step="2"><b>The Staff move:</b> after listing them, say which single '
           'requirement dominates the design &mdash; and design for that one first.</div>',
           """Requirements come in two lists and candidates routinely blur them. Functional requirements are """
           """what the system does — verbs. A user can shorten a URL. A user can follow a short link. Keep """
           """the list to three or four, then say which one is quietly doing all the work.""", step=0)
seg(sid, 1, """Non-functional requirements are what the system must be — adjectives, but each one has to """
            """come with a number and with what it forces. "Highly available" is not a requirement. """
            """"Ninety-nine point nine nine percent availability, which means no single points of failure """
            """on the read path" is a requirement, because it constrains the drawing.""")
seg(sid, 2, """And here is the Staff-level move on top of both lists: after you have listed them, say which """
            """single requirement dominates the design, and then design for that one first. In a URL """
            """shortener it is read latency. In a metrics system it is ingest cardinality. Naming the """
            """dominant constraint tells the interviewer you can prioritise, which is most of what """
            """seniority is.""")

# ------------------------------------------------------------------ movement 2
sid = beat('Movement 2 — size', 'Numbers exist to eliminate designs',
           '<div class="bigidea">A capacity estimate is not arithmetic homework. '
           'It is how you <b>rule things out</b> in front of the interviewer.</div>'
           '<div style="margin-top:26px;font-size:29px;line-height:1.7">'
           'Ten thousand writes a second means one database instance will not do it &rarr; '
           'partitioning is now justified, not assumed.<br><br>'
           'Forty terabytes a year means retention is a design problem &rarr; tiering earns its place.'
           '<br><br>'
           'A ninety-nine to one read ratio means a cache changes the whole load profile &rarr; '
           'and now you can say by how much.</div>',
           """Movement two, size. And the mindset shift I want you to make is this: a capacity estimate is """
           """not arithmetic homework that you do because the format demands it. It is how you rule things """
           """out, out loud, in front of the interviewer.""", step=0)
seg(sid, 1, """Ten thousand writes a second means one database instance will not carry it, so partitioning """
            """becomes justified rather than assumed. Forty terabytes a year means retention is a design """
            """problem, so tiered storage earns its place instead of appearing by reflex.""")
seg(sid, 2, """A ninety-nine to one read ratio means a cache changes the entire load profile, and now you can """
            """say by how much rather than waving at it. Every number should end in a sentence that starts """
            """"so". That is the difference between estimating and performing estimation, and the next """
            """lesson is entirely about doing it well.""")

say('What I should say — while estimating', [
 'Let me put rough numbers on this — I will keep them round, and tell me if any assumption looks wrong.',
 'A hundred million daily actives, about one write each, is roughly twelve hundred writes a second average — call it four thousand at peak.',
 'So a single write node is out. That is what pushes me to partition, rather than partitioning because it is the default.',
 'Storage: five hundred bytes a record, a billion records a year, is about half a terabyte a year before replication — small. So storage is not my constraint here; latency is.',
 'I am rounding hard on purpose. I care about the order of magnitude, because that is what changes the design.',
], [
 """The words for this movement matter as much as the arithmetic. Open by asking permission to round, and """
 """invite correction: let me put rough numbers on this, I will keep them round, tell me if any """
 """assumption looks wrong. That protects you — if your assumption is off, they will say so now rather """
 """than letting you design on sand.""",
 """Then do the calculation in the open, at a pace they can follow, and land on the "so". A hundred """
 """million dailies, one write each, is about twelve hundred a second average and four thousand at peak. """
 """So a single write node is out — and that is what pushes me to partition. Notice how the partitioning """
 """decision arrives with a reason attached rather than as a reflex.""",
 """Then do the same for storage, and — this is the part people miss — be willing to conclude that a """
 """dimension is not your problem. Saying "half a terabyte a year, so storage is not my constraint here, """
 """latency is" is a strong sentence. It shows the estimate changed your focus.""",
 """And say out loud that you are rounding on purpose and care about the order of magnitude. Nobody is """
 """checking your long division. They are checking whether you know which magnitude changes the """
 """architecture.""",
])

# ------------------------------------------------------------------ movement 3
sid = beat('Movement 3 — shape', 'API and data model come before boxes',
           '<div style="font-size:29px;line-height:1.7">'
           'Most candidates draw the architecture first. Do the <b>API</b> and the <b>data model</b> first, '
           'and the architecture almost draws itself.<br><br>'
           '<b>The API</b> pins down what is synchronous and what is not &mdash; and anything you cannot '
           'do inside the latency budget becomes an async path.<br><br>'
           '<b>The data model</b> pins down the access pattern &mdash; and the access pattern, not the '
           'data, chooses the database.<br><br>'
           '<span style="color:#ffd483">Say the primary key and the partition key out loud. That one '
           'sentence tells an infrastructure interviewer more about you than the whole diagram.</span></div>',
           """Movement three, shape. And here is a sequencing tip that will make you look considerably more """
           """experienced than it costs: do the API and the data model before you draw the architecture. """
           """Most candidates draw boxes first. If you define the interface and the storage first, the boxes """
           """almost place themselves.""", step=0)
seg(sid, 1, """The API pins down what is synchronous and what is not. Anything that cannot finish inside the """
            """latency budget becomes an asynchronous path — and now your queue exists for a reason you can """
            """state, rather than because queues are in every diagram.""")
seg(sid, 2, """The data model pins down the access pattern, and it is the access pattern, not the shape of """
            """the data, that chooses the database. People say "it is relational data so I will use """
            """Postgres". The better sentence is "the only query I need is by short code, and I need it in """
            """single-digit milliseconds at a hundred thousand a second, so I want a key-value store".""")
seg(sid, 3, """And whatever you are designing, say the primary key and the partition key out loud. In an """
            """infrastructure round, that single sentence tells the interviewer more about you than the """
            """whole diagram does, because hot partitions and rebalancing all follow from it.""")

# progressive architecture demo
A = Arch('Movement 3 — build it up, do not reveal it', kicker='Progressive disclosure', height=760)
A.box('c',   90, 300, 210, 110, 'Client', kind='neutral', step=0, focus=0)
A.box('api', 380, 300, 230, 110, 'API service', 'stateless', kind='info', step=1, focus=1)
A.arrow('c', 'api', step=1, focus=1)
A.box('db',  690, 300, 230, 110, 'Database', 'source of truth', kind='shared', step=1, focus=1)
A.arrow('api', 'db', step=1, focus=1)

A.box('lb',  380, 140, 230, 90, 'Load balancer', kind='info', step=2, focus=2, small=True)
A.box('api2',380, 450, 230, 90, 'API service &times;N', kind='info', step=2, focus=2, small=True)
A.box('cache',690, 140, 230, 90, 'Cache', 'read path', kind='ok', step=3, focus=3, small=True)
A.arrow('api', 'cache', step=3, focus=3, dashed=True)

A.box('q',   1000, 300, 220, 110, 'Queue', 'async work', kind='dp', step=4, focus=4)
A.arrow('api', 'q', step=4, focus=4)
A.box('w',   1300, 300, 220, 110, 'Workers', kind='dp', step=4, focus=4)
A.arrow('q', 'w', step=4, focus=4)

A.box('shard', 690, 450, 230, 90, 'Partitioned', 'by key', kind='shared', step=5, focus=5, small=True)
A.note(1000, 470, 'Each box arrives **because a number or a requirement demanded it** &mdash;\\n'
                  'and you say which one as you draw it.', step=6, kind='ok', w=760, size='l')
A.narrate(0, """Let me show you what progressive disclosure means, because this is how the drawing should """
              """actually go. You start with the smallest honest thing: a client.""")
A.narrate(1, """Then the simplest system that satisfies the functional requirement — one service, one """
              """database. Say out loud that this works and state the load at which it stops working. """
              """Starting simple is not naivety; it is what lets every later box have a justification.""")
A.narrate(2, """Now the traffic number you computed says one instance is not enough, so you add a load """
              """balancer and horizontal instances — and you say "because four thousand requests a second """
              """at peak is more than one node should carry".""")
A.narrate(3, """The read-write ratio says reads dominate, so a cache goes on the read path, and you name """
              """what it protects: the database, from ninety-nine percent of the reads.""")
A.narrate(4, """Anything that cannot fit in the latency budget moves off the request path into a queue with """
              """workers behind it. Again, the reason comes first, the box second.""")
A.narrate(5, """And when the storage or write numbers exceed one node, the database partitions — by a key """
              """you name.""")
A.narrate(6, """Six steps, and every single box arrived because a number or a requirement demanded it. That """
              """is the difference between a diagram that grows in front of the interviewer and a diagram """
              """that is revealed. The grown one shows your reasoning; the revealed one hides it.""")
A.build()

# ------------------------------------------------------------------ movement 4
sid = beat('Movement 4 — stress', 'Where the level is actually decided',
           '<div style="font-size:29px;line-height:1.72">'
           'Everything up to here, a strong senior engineer also does. The level is decided in what '
           'follows:<br><br>'
           '<b>Deep dive</b> &mdash; pick the two components where this system is genuinely hard, and go '
           'three levels down.<br>'
           '<b>Failure</b> &mdash; for each component, what the user sees and what the system does.<br>'
           '<b>Consistency</b> &mdash; say which model, and why it is acceptable <i>here</i>.<br>'
           '<b>Observability</b> &mdash; what you would alert on, not a list of metrics.<br>'
           '<b>Security</b> &mdash; where it sits in the path, not a paragraph at the end.<br>'
           '<b>Cost</b> &mdash; what dominates the bill, and the one change that would halve it.<br>'
           '<b>Trade-offs</b> &mdash; what you chose, and what would make you choose otherwise.</div>',
           """Movement four, stress. Be honest with yourself about this part: everything up to here, a """
           """strong senior engineer also does. The level is decided by what follows.""", step=0)
seg(sid, 1, """Deep dive. Pick the two components where this system is genuinely hard and go three levels """
            """down into them. Not six components at one level — two, deeply. Breadth is completeness, """
            """which you have already shown; depth is what is being tested now.""")
seg(sid, 2, """Failure. For each component, what does the user see and what does the system do? We will do a """
            """whole table of this in every design lesson.""")
seg(sid, 3, """Consistency: name the model and justify it here specifically, not in general. Observability: """
            """say what you would alert on, which is a much sharper answer than listing metrics. Security: """
            """put it in the request path where it belongs rather than appending a paragraph at the end.""")
seg(sid, 4, """Cost: say what dominates the bill and name the one change that would halve it. And """
            """trade-offs: what you chose, and — the sentence that separates candidates — what would make """
            """you choose otherwise.""")

sid = beat('The deep dive', 'How to choose what to go deep on',
           '<div class="bigidea">Go deep where the system is <b>hard</b>, not where you are '
           '<b>comfortable</b>.</div>'
           '<div style="margin-top:26px;font-size:28px;line-height:1.7">'
           'Ask yourself: if this system were built badly, <b>which component would be the reason?</b>'
           '<br><br>'
           '&bull; URL shortener &rarr; unique id generation, and the read path under cache miss<br>'
           '&bull; Typeahead &rarr; the latency budget, and how the index gets refreshed<br>'
           '&bull; Metrics &rarr; cardinality, and what happens when ingest outruns storage<br>'
           '&bull; Job scheduler &rarr; exactly-once execution, and clock skew<br><br>'
           '<span style="color:#ffd483">If you deep dive on the load balancer, you have told the '
           'interviewer you could not find the hard part.</span></div>',
           """A word on choosing your deep dive, because this choice is itself a signal. Go deep where the """
           """system is hard, not where you happen to be comfortable.""", step=0)
seg(sid, 1, """The question that finds it: if this system were built badly, which component would be the """
            """reason? For a URL shortener it is unique id generation and the read path on a cache miss. """
            """For typeahead it is the latency budget and index refresh. For metrics it is cardinality and """
            """what happens when ingestion outruns storage. For a job scheduler it is exactly-once """
            """execution and clock skew.""")
seg(sid, 2, """And the warning: if you choose to deep dive on the load balancer, you have told the """
            """interviewer that you could not identify the hard part. That is a worse signal than saying """
            """nothing. The choice of deep dive is an answer in itself.""")

say('What I should say — in the deep dive and the close', [
 'The two places this design is genuinely hard are id generation and the cache-miss path, so I want to spend my time there.',
 'If the cache dies, we do not just get slower — we get a thundering herd onto the database. So I would add request coalescing, not just a bigger cache.',
 'I am choosing eventual consistency here because a redirect that is stale for one second is invisible to a user, while the coordination cost of strong consistency is on every single read.',
 'The trade-off I am making is more storage in exchange for lower read latency. If storage cost became the binding constraint, I would flip that.',
 'If I had to build this in a quarter, I would build the redirect path and skip analytics — because the redirect is the product and analytics can arrive later.',
 'The biggest risk in this design is the hot key. I would want a load test that deliberately creates one before I trusted it in production.',
], [
 """These six sentences are the ones I would drill. The first announces your deep dive and why, so the """
 """interviewer knows the structure of the next ten minutes.""",
 """The second is failure reasoning done properly: not "we add a cache" but "when the cache dies we get a """
 """thundering herd, so I would add request coalescing". You have named a second-order effect, which is """
 """exactly what fault-tolerance reasoning means on that scorecard.""",
 """The third justifies a consistency choice in terms of what the user experiences and what the """
 """alternative costs — not by reciting definitions.""",
 """The fourth is the trade-off sentence with its reversal attached. The fifth is prioritisation: what """
 """you would build first and what you would leave out, which is a question about judgement rather than """
 """knowledge.""",
 """And the sixth is the strongest closing line available to you: name the biggest risk in your own """
 """design and say how you would go looking for it. Candidates think admitting a weakness costs them. It """
 """does the opposite — it demonstrates that you have operated systems, because operating systems is """
 """mostly finding out where your design was wrong.""",
])

# ------------------------------------------------------------------ data model
sid = beat('Data model', 'The access pattern chooses the database, not the data',
           '<div style="font-size:29px;line-height:1.72">'
           'The weak sentence: <i>&ldquo;this data is relational, so I will use Postgres.&rdquo;</i><br><br>'
           'The strong sentence: <i>&ldquo;the only query I need is by short code, single-digit '
           'milliseconds, a hundred thousand a second, no joins &mdash; so I want a key-value store, '
           'and here is the key.&rdquo;</i><br><br>'
           'Work in this order:<br>'
           '<b>1.</b> List the queries the system must serve. All of them.<br>'
           '<b>2.</b> For each, say how often and how fast.<br>'
           '<b>3.</b> <i>Then</i> choose the store that serves the hottest one naturally.<br>'
           '<b>4.</b> Name the primary key and the partition key.<br>'
           '<b>5.</b> Ask what becomes expensive &mdash; that is your secondary index problem.</div>',
           """A moment on data modelling, because this is where an infrastructure interviewer starts """
           """listening closely. The weak sentence is: this data is relational, so I will use Postgres. """
           """The strong sentence is: the only query I need is by short code, in single-digit """
           """milliseconds, a hundred thousand times a second, with no joins — so I want a key-value """
           """store, and here is the key.""", step=0)
seg(sid, 1, """The difference is that the second derives the store from the access pattern. So work in this """
            """order. List every query the system must serve. For each one, say how often and how fast. """
            """Only then choose the store that serves the hottest query naturally.""")
seg(sid, 2, """Then name the primary key and the partition key explicitly. And finish with the question that """
            """finds the trouble: what query becomes expensive under this model? That is your secondary """
            """index problem, and volunteering it before they ask is a genuine signal, because it is the """
            """thing that bites in production six months later.""")

# ------------------------------------------------------------------ observability & security
sid = compare('The two sections candidates rush &mdash; and shouldn&rsquo;t',
 ('Observability', 'info', 0,
  ['Weak: a list of metrics &mdash; CPU, memory, latency',
   'Strong: <b>what would page me at 3am</b>, and why',
   'One golden signal per component: saturation, errors, latency',
   'Name the <b>leading</b> indicator: queue depth and consumer lag move <i>before</i> users notice',
   'Say which dashboard you open first during an incident']),
 ('Security', 'shared', 1,
  ['Weak: a paragraph about TLS bolted on at the end',
   'Strong: <b>where it sits in the request path</b>',
   'Authn at the edge, authz at the service, both stated',
   'Encryption in transit and at rest &mdash; and who holds the keys',
   'Tenant isolation and abuse limits, if the system is multi-tenant']))
seg(sid, 0, """Two sections candidates rush and shouldn't. Observability first. The weak version is a list of """
            """metrics: CPU, memory, latency. The strong version answers a different question — what would """
            """page me at three in the morning, and why. Give one golden signal per component: saturation, """
            """errors, latency.""")
seg(sid, 1, """Then name a leading indicator, because that is what experience sounds like. Queue depth and """
            """consumer lag move before users notice anything; error rate moves after. Saying "I would """
            """alert on consumer lag because it rises minutes before the user-visible failure" is worth """
            """more than ten metric names. And say which dashboard you would open first in an incident.""")
seg(sid, 2, """Security second. The weak version is a paragraph about TLS at the end. The strong version puts """
            """it in the request path: authentication at the edge, authorisation at the service, and say """
            """both. Encryption in transit and at rest, and who holds the keys — which matters enormously """
            """if the system is multi-tenant. Then rate limiting and abuse prevention if the endpoint is """
            """public. Security placed in the flow reads as architecture; security appended at the end """
            """reads as a checklist item you remembered.""")

# ------------------------------------------------------------------ trade-offs
sid = beat('Trade-offs', 'The sentence pattern that carries the whole round',
           '<div class="bigidea">&ldquo;I am choosing X over Y, because <b>this</b> requirement dominates. '
           'If <b>that</b> changed, I would choose Y.&rdquo;</div>'
           '<div style="margin-top:28px;font-size:28px;line-height:1.7">'
           'Three parts, and all three matter:<br><br>'
           '<b>The choice</b> &mdash; unambiguous. Do not present two options and stop.<br>'
           '<b>The reason</b> &mdash; tied to a requirement you agreed at minute five, not to taste.<br>'
           '<b>The reversal</b> &mdash; what would make you choose differently.<br><br>'
           '<span style="color:#ffd483">The reversal is the part almost nobody says, and it is the part '
           'that sounds most like a Staff engineer &mdash; because it proves the decision was reasoned '
           'rather than remembered.</span></div>',
           """Now the single sentence pattern that carries this entire round. I am choosing X over Y because """
           """this requirement dominates; if that changed, I would choose Y.""", step=0)
seg(sid, 1, """Three parts and all three matter. The choice, stated unambiguously — do not lay out two """
            """options and trail off, because an interviewer reads that as indecision. The reason, tied to """
            """a requirement you agreed at minute five rather than to personal taste.""")
seg(sid, 2, """And the reversal: what would make you choose differently. Almost nobody says the third part, """
            """and it is the part that sounds most like a Staff engineer — because it proves the decision """
            """was reasoned rather than remembered. Anyone can recall that Kafka gives you durable replay. """
            """Only someone who has weighed it can tell you the circumstances under which they would not """
            """use it.""")

# ------------------------------------------------------------------ mistakes
sid = cards('The seven ways strong candidates lose this round', [
 (0, 'Drawing before scoping', 'Every later decision is unjustified, because nothing constrains it. The single most common failure.', 'deny'),
 (0, 'Numbers with no "so"', 'An estimate that does not eliminate anything was a waste of five minutes. Always finish on the consequence.', 'deny'),
 (1, 'Breadth instead of depth', 'Six components at one level looks thorough and scores as shallow. Two components, three levels down.', 'deny'),
 (1, 'Unrequested multi-region', 'Global replication nobody asked for reads as over-engineering &mdash; and it eats the clock you needed for depth.', 'deny'),
 (2, 'Component names instead of reasons', '&ldquo;I will use Kafka&rdquo; is not a decision. &ldquo;I need durable replay and ordering per key, so Kafka&rdquo; is.', 'deny'),
 (2, 'Silence while thinking', 'The interviewer cannot score what stays in your head. Narrate the dead ends too.', 'shared'),
 (3, 'Defending instead of updating', 'When they push, they are usually offering information. Take it, change the design, say what changed.', 'shared'),
], cols=2)
seg(sid, 0, """The seven ways strong candidates lose this round. Drawing before scoping — the most common """
            """failure by a distance, because it leaves every later decision unjustified. And numbers with """
            """no "so": an estimate that eliminates nothing was five minutes you did not have.""")
seg(sid, 1, """Breadth instead of depth. Six components explained at one level looks thorough to the """
            """candidate and scores as shallow to the interviewer. And volunteering multi-region when """
            """nobody asked reads as over-engineering, while eating the clock you needed for the deep """
            """dive.""")
seg(sid, 2, """Naming components instead of giving reasons. "I will use Kafka" is not a decision; "I need """
            """durable replay and ordering per key, so Kafka" is a decision. And silence — the interviewer """
            """cannot score what stays inside your head, so narrate the dead ends as well as the """
            """conclusions.""")
seg(sid, 3, """And the last one is the most fixable. When an interviewer pushes back, they are usually """
            """handing you information, not attacking you. Take it, change the design, and say out loud """
            """what changed and why. Candidates who defend a design against new information look rigid. """
            """Candidates who update look like colleagues.""")

sid = beat('The checklist', 'What to run through in your head, every time',
           '<div class="cs" style="top:34px">'
           + ''.join('<div class="cs-row" data-step="%d"><div class="cs-h">%s</div>'
                     '<div class="cs-v">%s</div></div>' % (i // 4, h, v)
                     for i, (h, v) in enumerate([
                       ('Requirements', 'Agreed, written, and scoped &mdash; including what is out'),
                       ('Scale', 'Users, RPS, peak multiplier, read/write ratio'),
                       ('Capacity', 'Traffic, storage, bandwidth &mdash; each ending in a &ldquo;so&rdquo;'),
                       ('API', 'What is synchronous, and what moved off the request path'),
                       ('Data model', 'Primary key, partition key, access pattern'),
                       ('Architecture', 'Built up in levels, each box justified as it appears'),
                       ('Storage', 'Chosen by access pattern, not by data shape'),
                       ('Cache', 'What, why, TTL, invalidation &mdash; and stampede'),
                       ('Partitioning', 'Key, distribution, hot-partition risk, rebalancing'),
                       ('Consistency', 'Which model, and why it is acceptable here'),
                       ('Async', 'What is deferred, and what the user sees meanwhile'),
                       ('Failures', 'Per component: user impact, system response'),
                       ('Retries', 'Backoff, jitter, budget &mdash; and idempotency to make them safe'),
                       ('Backpressure', 'What sheds load first, and who notices'),
                       ('Observability', 'What you would alert on, and the one dashboard you would open'),
                       ('Security', 'Authn, authz, encryption, tenant isolation, abuse'),
                       ('Cost', 'What dominates, and the one change that halves it'),
                       ('Trade-offs', 'Chosen, rejected, and what would flip it'),
                       ('Evolution', 'What breaks at ten times, and what you would build first'),
                       ('Summary', 'Dominant constraint, biggest risk, first milestone'),
                     ])) + '</div>',
           """Here is the checklist to run in your head, and I mean literally run it — in the last five """
           """minutes of the interview, walk it silently and see which line you have not spoken about. """
           """Requirements, scale, capacity. API, data model, architecture.""", step=0)
seg(sid, 1, """Storage, cache, partitioning, consistency. Each one with its own one-line test: storage """
            """chosen by access pattern, cache with an invalidation story, partitioning with a hot-key """
            """risk, consistency justified here rather than in general.""")
seg(sid, 2, """Async, failures, retries, backpressure. Notice that retries and idempotency are on the same """
            """line, because a retry without idempotency is a bug generator, and every serious """
            """interviewer knows it.""")
seg(sid, 3, """Observability, security, cost, trade-offs, evolution, summary. Twenty lines. You will not """
            """cover all twenty in an hour, and you are not supposed to. But if you notice at minute fifty """
            """that you have said nothing about failure or cost, you can still fix it in a sentence each — """
            """and that recovery is worth real marks.""")

sid = statement('Lesson 1', 'The method is the answer.',
                'You cannot revise every question. You can arrive with a way of working that makes an unseen question routine — and that is exactly what is being scored.',
                kind='ok')
seg(sid, 0, """One line to close. The method is the answer.""")
seg(sid, 1, """You cannot revise every question that might come up, and trying is a losing strategy. What you """
            """can do is arrive with a way of working so practised that a question you have never seen """
            """becomes routine — scope, size, shape, stress, narrating as you go. That is precisely what """
            """the scorecard is measuring. Next lesson: capacity estimation, done properly, because that """
            """is the movement candidates fake most often and the one interviewers probe hardest.""")
