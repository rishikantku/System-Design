# -*- coding: utf-8 -*-
"""Chapter 6, Lesson 3 — a distributed logging system."""
from lib import *

lesson_header('6.3', 'Design a distributed logging system',
              'Agents &middot; the log as a buffer &middot; retention tiers &middot; backpressure',
              dict(reports='InterviewTV list; overlaps the metrics question in 2.3',
                   latest='2026', level='Staff, Infrastructure',
                   conf='MEDIUM-HIGH &mdash; the family is well attested',
                   sources='InterviewTV.io + research pass 3'), 16,
              """Chapter six, lesson three: a distributed logging system for an analytics service. This """
              """is the sibling of the metrics question in lesson two point three, and the useful thing """
              """is knowing why they are different systems. Metrics are small, structured and """
              """predictable. Logs are large, unstructured and bursty &mdash; and that burstiness, """
              """rather than the volume, is what the design has to survive.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff, Infrastructure',
  'Named: collection, agents, ingestion, partitioning, Kafka, storage, indexing, <b>retention, query, '
  'aggregation, backpressure, ordering</b>, failure handling'),
 ('Research pass 3 &mdash; metrics question', 'Sep 2025', 'Senior / Staff',
  'Metrics gathering has <b>3 independent reports</b> (lesson 2.3). Same ingestion shape, different '
  'data'),
], """Single-source for this framing, but the family is well attested &mdash; the metrics question has """
     """three independent reports and shares the ingestion machinery.""",
 ["""And look at what is named here that was not named for metrics: retention, backpressure, ordering. """
  """Those three words tell you this is about surviving volume you cannot control, which is the real """
  """difference between logs and metrics."""],
 caveat='Medium-high because the family is corroborated. The specific logging framing is single-source.',
 narration_caveat="""Medium-high confidence because the family is corroborated. The specific logging """
                  """framing is single-source, so hold the details loosely.""")

sid = beat('Why this is interesting', 'You do not control the input. That changes everything.',
           '<div style="font-size:28px;line-height:1.72">'
           'With metrics, <b>you</b> decide the volume: one gauge per host per 10 s. Predictable, '
           'bounded, and it does not change when something goes wrong.<br><br>'
           '<span style="color:#ff9a9a">Logs are the opposite. An application in trouble logs '
           '<i>more</i> &mdash; often 100&times; more &mdash; exactly when your pipeline is already '
           'under stress.</span><br><br>'
           '<b>That one property drives the whole design:</b><br>'
           '&bull; Capacity must be sized for the <b>incident</b>, not the average &mdash; or sized for '
           'the average with a plan for what to drop<br>'
           '&bull; You need <b>backpressure</b> that cannot take down the application doing the logging<br>'
           '&bull; You need to choose, <i>in advance</i>, what gets dropped first<br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: the question is not &ldquo;can you store '
           'the logs?&rdquo; It is &ldquo;what happens on the day you cannot?&rdquo; &mdash; and a '
           'logging system that takes down the service it monitors is a real and common '
           'outage.</span></div>',
           """Why is this interesting? Because you do not control the input, and that changes """
           """everything.""", step=0)
seg(sid, 1, """With metrics, you decide the volume. One gauge per host every ten seconds. Predictable, """
            """bounded, and critically it does not change when something goes wrong.""")
seg(sid, 2, """Logs are the opposite. An application in trouble logs more &mdash; often a hundred times """
            """more, because every request is now throwing an exception with a stack trace. So your """
            """input volume spikes at exactly the moment your pipeline is already under stress, and """
            """exactly when the logs are most valuable.""")
seg(sid, 3, """That single property drives the whole design. Capacity has to be sized for the incident """
            """rather than the average &mdash; or sized for the average with an explicit plan for what """
            """to drop. You need backpressure that cannot take down the application doing the logging. """
            """And you need to decide in advance what gets dropped first, because deciding during an """
            """incident means it gets decided by accident.""")
seg(sid, 4, """So the staff-level framing is: the question is not &ldquo;can you store the logs&rdquo;. """
            """It is &ldquo;what happens on the day you cannot&rdquo;. A logging system that takes down """
            """the service it is monitoring is a real and depressingly common outage, and saying that """
            """early shows you know what this system is actually for.""")

think('Your service starts erroring and log volume goes up 100&times; in thirty seconds. The log agent '
      'cannot ship fast enough. What should the agent do &mdash; block the application, buffer, or drop? '
      'And which logs would you drop first?',
      25,
      """Pause. Your service starts erroring and log volume goes up a hundred times in thirty seconds. """
      """The agent cannot ship fast enough. Should it block the application, buffer, or drop? And if """
      """drop &mdash; which logs would you drop first? Say it out loud.""",
      """Hold that. &ldquo;Never block the application&rdquo; is the only safe answer, and what you drop """
      """first is a product decision you should make before the incident, not during it.""")

clarify('What I would clarify first', [
 ('What are the logs <i>for</i> &mdash; debugging, audit, or analytics?',
  '<b>Debugging tolerates loss.</b> Audit does not &mdash; it needs durability and completeness '
  'guarantees that cost an order of magnitude more.'),
 ('How long must we keep them, and at what granularity?',
  'Retention dominates cost. <b>7 days hot + 90 days cold</b> is a completely different bill from '
  '1 year hot.'),
 ('Structured or free text?',
  'Structured JSON can be indexed by field cheaply. Free text needs full-text indexing, which is '
  '<b>5&ndash;10&times; the storage</b> of the raw logs.'),
 ('What queries matter &mdash; grep by request ID, or aggregate across billions of lines?',
  '<b>Decides the storage engine.</b> Point lookup by trace ID is cheap. Ad-hoc aggregation across '
  'everything is an OLAP problem.'),
 ('Is ordering required &mdash; and within what scope?',
  'Global ordering across a fleet is <b>impossible and unnecessary</b>. Per-host or per-request '
  'ordering is achievable and is almost always what people actually mean.'),
 ('Is loss acceptable under load?',
  'The most important question, and interviewers rarely volunteer it. <b>If yes, say what you drop '
  'first.</b> If no, you need durable buffering at the edge and a much bigger budget.'),
], [
 """What are the logs for &mdash; debugging, audit, or analytics? Debugging tolerates loss; losing one """
 """percent of debug lines costs almost nothing. Audit does not, and needs durability and completeness """
 """guarantees that cost an order of magnitude more. These are different systems and people call them """
 """both logging.""",
 """How long must we keep them and at what granularity? Retention dominates cost. Seven days hot plus """
 """ninety days cold is a completely different bill from a year of everything hot.""",
 """Structured or free text? Structured J-S-O-N can be indexed by field cheaply. Free text needs """
 """full-text indexing, which is five to ten times the storage of the raw logs &mdash; so the index """
 """costs more than the data.""",
 """What queries matter? Grep by request I-D, or aggregate across billions of lines? That decides the """
 """storage engine. A point lookup by trace I-D is cheap. Ad-hoc aggregation across everything is an """
 """O-L-A-P problem and needs a columnar store.""",
 """Is ordering required, and within what scope? Global ordering across a fleet is both impossible and """
 """unnecessary, and saying so confidently is a good move. Per-host or per-request ordering is """
 """achievable and is almost always what people actually mean when they ask.""",
 """And the most important question, which interviewers rarely volunteer: is loss acceptable under """
 """load? If yes, say what you drop first. If no, you need durable buffering at the edge and a much """
 """bigger budget &mdash; and you should make them say which.""",
])

capacity('Capacity', [
 ('10,000 hosts &times; 1,000 lines / s', '10M lines / s', '10M lines / s',
  'The headline number. <b>Lines are the wrong unit</b> though &mdash; bytes decide'),
 ('Average line ~500 B', '10M &times; 500 B', '&asymp; 5 GB / s',
  '&asymp; 430 TB / day raw. <b>This is the real number</b>'),
 ('Incident spike: 100&times; on 5% of hosts', '+ 25 GB/s for a few minutes',
  '<b>5&times; normal, instantly</b>', 'You cannot provision for this. <b>You buffer or you drop</b>'),
 ('Compressed (gzip ~10:1 on logs)', '430 TB &divide; 10', '&asymp; 43 TB / day',
  'Logs compress extremely well &mdash; they are repetitive. <b>Always compress at the agent</b>'),
 ('7 days hot + 90 days cold', '7 &times; 43 TB + 90 &times; 43 TB &times; 0.1 cost',
  '&asymp; 300 TB hot', 'Hot storage dominates. <b>Tiering is the main cost lever</b>'),
 ('Full-text index on everything', '&asymp; 5&times; the data', '&asymp; 215 TB / day of index',
  '<b>The index costs more than the logs.</b> Index selectively, not everything'),
], [
 """Numbers. Ten thousand hosts at a thousand lines a second is ten million lines a second. That is the """
 """headline, but lines are the wrong unit &mdash; bytes decide everything here.""",
 """At about five hundred bytes a line that is five gigabytes a second, or four hundred and thirty """
 """terabytes a day raw. That is the real number.""",
 """Now the incident spike. A hundred times the volume on five percent of hosts adds twenty-five """
 """gigabytes a second for a few minutes &mdash; five times your normal load, arriving instantly. You """
 """cannot provision for that. So you buffer, or you drop, and the design has to say which.""",
 """Logs compress extremely well because they are highly repetitive &mdash; about ten to one with gzip. """
 """That takes you to forty-three terabytes a day. Always compress at the agent, where you have spare """
 """C-P-U, rather than paying to ship uncompressed bytes.""",
 """Seven days hot plus ninety days cold is roughly three hundred terabytes hot. Hot storage dominates """
 """cost, so tiering is the main lever you have.""",
 """And the one that surprises people: a full-text index over everything is about five times the data, """
 """which is two hundred and fifteen terabytes a day of index. The index costs more than the logs it """
 """indexes. So you index selectively &mdash; a few fields, not the whole line &mdash; and that """
 """decision is worth more than any amount of storage optimisation.""",
])

A = Arch('Log pipeline &mdash; and where it is allowed to fail', kicker='Architecture', height=800)

A.box('app',   60, 290, 160, 95, 'Application', 'writes to stdout', kind='neutral', step=0, focus=0, small=True)
A.box('agent', 265, 275, 205, 120, 'Agent', 'local buffer,<br>compress, batch', kind='ok', step=0,
      focus=[0, 1, 2])
A.arrow('app', 'agent', step=0, focus=0)

A.box('kaf',  545, 275, 215, 120, 'Kafka', 'partitioned by host<br>retains 24 h', kind='info', step=1,
      focus=[1, 3])
A.arrow('agent', 'kaf', step=1, label='compressed', focus=1)

A.box('hot',  860, 160, 215, 105, 'Hot store', '7 days, indexed', kind='ok', step=3, focus=3, small=True)
A.box('cold', 860, 300, 215, 105, 'Cold store', '90 days, S3', kind='dp', step=3, focus=3, small=True)
A.box('agg',  860, 440, 215, 105, 'Aggregator', 'counts, rollups', kind='shared', step=4, focus=4, small=True)
A.arrow('kaf', 'hot', step=3, focus=3)
A.arrow('kaf', 'cold', step=3, focus=3)
A.arrow('kaf', 'agg', step=4, focus=4)

A.box('qry', 1160, 230, 215, 105, 'Query service', 'by trace / field', kind='neutral', step=5, focus=5, small=True)
A.arrow('hot', 'qry', step=5, focus=5)
A.arrow('cold', 'qry', step=5, focus=5, dashed=True)

A.box('dash',1160, 440, 215, 105, 'Dashboards', 'and alerts', kind='neutral', step=5, focus=5, small=True)
A.arrow('agg', 'dash', step=5, focus=5)

A.note(265, 480, 'The agent NEVER blocks the application. Bounded buffer; when it is full, drop by level and count what you dropped.',
       step=2, kind='info', w=440)
A.note(545, 620, 'Kafka is the shock absorber. 24 h of retention means a consumer can be down for hours without losing data.',
       step=1, kind='info', w=470)

A.narrate(0, """The application writes to standard output and a local agent picks it up. The application """
             """itself knows nothing about the pipeline &mdash; that decoupling is deliberate, because """
             """the moment the application knows about your log backend, your log backend can break """
             """the application.""",
          A.flow([(220, 337), (265, 335)]))
A.narrate(1, """The agent compresses, batches and ships to Kafka, partitioned by host. Kafka here is the """
             """shock absorber: with twenty-four hours of retention, every consumer downstream can be """
             """down for hours and nothing is lost. That is what buys you the right to have """
             """unreliable consumers.""",
          A.flow([(470, 335), (545, 335)]))
A.narrate(2, """And the single most important rule in this design: the agent never blocks the """
             """application. It has a bounded local buffer, and when that buffer is full it drops """
             """&mdash; by severity &mdash; and counts what it dropped. A logging agent that applies """
             """backpressure all the way into your request threads will take your service down, and it """
             """will do it during an incident.""")
A.narrate(3, """From Kafka, several independent consumers. A hot store holding seven days, indexed for """
             """search. A cold store holding ninety days of compressed raw files in object storage, """
             """cheap and slow.""",
          A.flow([(760, 310), (860, 212)]))
A.narrate(4, """And an aggregator computing counts and roll-ups &mdash; error rates per service, for """
             """instance &mdash; because most log questions are really counting questions, and """
             """answering them from a pre-aggregate is a thousand times cheaper than scanning raw """
             """lines.""",
          A.flow([(760, 360), (860, 492)]))
A.narrate(5, """Then a query service over hot and cold, and dashboards over the aggregates. Note the """
             """consumers are independent: the aggregator falling behind does not affect search, """
             """because each one tracks its own offset in Kafka.""",
          A.flow([(1075, 212), (1160, 282)]))
A.build()

sid = beat('Deep dive 1', 'Backpressure that cannot hurt the application',
           '<div style="font-size:27px;line-height:1.7">'
           'Four options when the agent cannot ship fast enough:<br><br>'
           '&bull; <b>Block the application.</b> <span style="color:#ff9a9a">Never. Logging now causes '
           'outages.</span> If the write is synchronous, a slow log backend becomes slow requests, and '
           'then a thread-pool exhaustion.<br>'
           '&bull; <b>Buffer in memory, unbounded.</b> <span style="color:#ff9a9a">Also never &mdash; '
           'OOM kills the process.</span> Unbounded buffers just move the crash.<br>'
           '&bull; <b>Buffer to local disk.</b> Survives restarts and long outages. Costs disk, and '
           'needs a cap or you fill the volume &mdash; <span style="color:#ffd483">and a full disk takes '
           'down the application anyway</span>.<br>'
           '&bull; <b>Bounded buffer, then drop.</b> <span style="color:#a8e6a3">Predictable, '
           'survivable.</span><br><br>'
           '<b>What I would build:</b> bounded in-memory buffer &rarr; spill to a <b>capped</b> local '
           'disk buffer &rarr; drop by severity when that is full.<br><br>'
           '<b>Drop order, decided now and not during the incident:</b> DEBUG, then INFO, then WARN. '
           '<b>Never drop ERROR.</b> And always emit a <code>logs_dropped</code> counter &mdash; '
           '<span style="color:#ffd483">silent loss is far worse than loss you can see.</span></div>',
           """Deep dive one: backpressure, and this is the answer to what I asked you to pause on. There """
           """are four options when the agent cannot ship fast enough.""", step=0)
seg(sid, 1, """Block the application. Never. Logging now causes outages. If the log write is synchronous, """
            """a slow log backend becomes slow requests, which becomes thread pool exhaustion, which """
            """becomes an outage &mdash; caused entirely by your observability system.""")
seg(sid, 2, """Buffer in memory without a bound. Also never, because you run out of memory and the """
            """process is killed. An unbounded buffer does not prevent the crash, it just moves it """
            """somewhere less obvious.""")
seg(sid, 3, """Buffer to local disk. This genuinely helps &mdash; it survives process restarts and long """
            """outages. It costs disk and needs a cap, and here is the trap: a full disk takes down the """
            """application anyway, so an uncapped disk buffer has reinvented the first problem.""")
seg(sid, 4, """Bounded buffer, then drop. Predictable and survivable. So what I would actually build is """
            """all three in sequence: a bounded in-memory buffer, spilling to a capped local disk """
            """buffer, and dropping by severity when that fills.""")
seg(sid, 5, """And the drop order is decided now, not during the incident. Debug first, then info, then """
            """warn. Never drop error, because errors are what you are going to need. And always emit a """
            """logs-dropped counter, because silent loss is far worse than visible loss &mdash; if you """
            """do not know you dropped lines, you will spend the outage looking for a log that was """
            """never written and concluding the code path did not execute.""")

sid = beat('Deep dive 2', 'Ordering &mdash; what is achievable and what is not',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Global ordering across 10,000 hosts is impossible</b>, and you should say so rather than '
           'attempt it. It would need a single sequencer that every log line passes through, which is '
           'both a bottleneck and a single point of failure &mdash; for logs.<br><br>'
           '<b>What is achievable, and why:</b><br>'
           '&bull; <b>Per-host ordering</b> &mdash; partition Kafka by host ID. One host&rsquo;s lines '
           'land on one partition, which guarantees order within it. '
           '<span style="color:#a8e6a3">Free, because you partitioned by host anyway.</span><br>'
           '&bull; <b>Per-request ordering</b> &mdash; attach a trace ID and a monotonic sequence number '
           '<i>at the source</i>. Reassemble at query time. This is what people actually want when they '
           'say &ldquo;ordering&rdquo;.<br><br>'
           '<b>Clock skew.</b> Host timestamps disagree by milliseconds to seconds. Sorting a merged '
           'view by wall-clock time produces <span style="color:#ff9a9a">lines that appear before the '
           'request that caused them</span>.<br>'
           '&bull; Keep <b>both</b> timestamps: host time and ingest time<br>'
           '&bull; Order <i>within</i> a trace by the sequence number, not by time<br><br>'
           '<span style="color:#ffd483">&ldquo;I will give you per-request ordering, which is what you '
           'actually need, and I will not pretend to give you global ordering, which nobody can.&rdquo;'
           '</span></div>',
           """Deep dive two: ordering, which the question names explicitly and which is mostly about """
           """knowing what to refuse.""", step=0)
seg(sid, 1, """Global ordering across ten thousand hosts is impossible, and you should say so plainly """
            """rather than attempting it. It would require a single sequencer that every log line passes """
            """through, which is simultaneously a throughput bottleneck and a single point of failure """
            """&mdash; for your logging system.""")
seg(sid, 2, """What is achievable: per-host ordering, by partitioning Kafka on host I-D. One host's lines """
            """land on one partition, and a Kafka partition guarantees order within itself. That is """
            """free, because you were partitioning by host anyway for load distribution.""")
seg(sid, 3, """And per-request ordering, which is what people actually mean. Attach a trace I-D and a """
            """monotonic sequence number at the source, and reassemble at query time. Then you can see """
            """exactly what happened to one request across twelve services in the right order, which is """
            """the thing anyone debugging actually wants.""")
seg(sid, 4, """Clock skew is the detail that makes this concrete. Host timestamps disagree by """
            """milliseconds to seconds, so if you sort a merged view by wall-clock time you will produce """
            """lines that appear before the request that caused them. That is deeply confusing when you """
            """are debugging at three in the morning.""")
seg(sid, 5, """So keep both timestamps &mdash; host time and ingest time &mdash; and order within a trace """
            """by the sequence number rather than by time. And the sentence I would say: I will give you """
            """per-request ordering, which is what you actually need, and I will not pretend to give you """
            """global ordering, which nobody can. Declining to promise something impossible is a staff """
            """signal, not a weakness.""")

tradeoff('What to index, and where to store it', [
 ('Full-text index everything, hot', 'info',
  ['Any query works instantly', 'No thought required at ingest time'],
  ['<b>~5&times; the data in index</b> &mdash; 215 TB/day', 'Cost dominates everything else',
   'Indexing throughput becomes the bottleneck during incidents']),
 ('Index selected fields only; raw text in cold storage', 'ok',
  ['Index is a fraction of the size', 'Hot store holds 7 days; cold holds 90 cheaply',
   'Covers the real queries: by trace ID, service, level, time'],
  ['Ad-hoc text search over old logs is slow &mdash; a scan, not a lookup',
   'Someone must choose the fields, and they will get it wrong once']),
 ('Store raw only, grep on demand', 'shared',
  ['<b>Cheapest possible</b>', 'No indexing pipeline at all'],
  ['Every query is a full scan', 'Useless for dashboards and alerting',
   'Fine for audit, hopeless for debugging']),
], 'Index a few structured fields &mdash; trace ID, service, level, timestamp &mdash; keep 7 days hot '
   'and 90 days of compressed raw in object storage.',
 'If the logs were <b>audit</b> records rather than debug output, I would invert this: full durability, '
 'no dropping, write-once storage, and accept the cost &mdash; because the requirement changed from '
 '&ldquo;help me debug&rdquo; to &ldquo;prove what happened&rdquo;.',
 [
 """Trade-off: what to index and where to store it. Full-text indexing everything in a hot store means """
 """any query works instantly and no thought is required at ingest. It costs roughly five times the """
 """data in index alone &mdash; two hundred and fifteen terabytes a day &mdash; which dominates every """
 """other cost in the system. And indexing throughput becomes your bottleneck during exactly the """
 """incidents you built this for.""",
 """Indexing selected fields only, with raw text in cold storage, makes the index a fraction of the """
 """size and covers the queries people actually run: by trace I-D, by service, by level, by time. The """
 """cost is that ad-hoc text search over old logs becomes a scan rather than a lookup, and somebody has """
 """to choose the fields &mdash; and they will choose wrong at least once.""",
 """Storing raw only and grepping on demand is the cheapest possible option and has no indexing """
 """pipeline at all. Every query is a full scan, so it is useless for dashboards and alerting. Fine """
 """for audit, hopeless for debugging.""",
 """I would index a few structured fields and keep seven days hot with ninety days of compressed raw in """
 """object storage.""",
 """And what would flip it: if these were audit records rather than debug output, I would invert """
 """everything &mdash; full durability, no dropping, write-once storage, and accept the cost. Because """
 """the requirement has changed from &ldquo;help me debug&rdquo; to &ldquo;prove what happened&rdquo;, """
 """and those deserve different systems.""",
])

failures('What happens when each piece dies', [
 ('Kafka unavailable', 'Nothing visible; agents buffer',
  'Agents buffer to local disk and drain when it returns. <b>This is why the local buffer exists</b> '
  '&mdash; it is the thing that makes Kafka non-critical'),
 ('Agent buffer fills during an incident', 'Debug and info lines lost',
  'Drop by severity, keep ERROR, and <b>emit a dropped counter</b>. Expected behaviour, not a bug '
  '&mdash; but it must be visible'),
 ('Indexing consumer falls behind', 'Recent logs not searchable yet',
  'Kafka retains 24 h, so it catches up. <b>Alert on consumer lag</b>. Search being minutes stale is '
  'a degradation, not an outage'),
 ('Hot store full', 'Writes rejected; search breaks',
  'Enforce retention <b>aggressively</b> and alert on days-of-headroom, not percent-full. Percent-full '
  'tells you nothing about how long you have'),
 ('A single service starts logging 1,000&times;', 'It drowns out everyone else',
  '<b>Per-service quotas at the agent.</b> One noisy service must not consume the shared pipeline '
  '&mdash; this is the rate limiter from 4.1, applied internally'),
 ('Logs contain passwords or PII', 'A compliance incident, not an outage',
  'Redact <b>at the agent</b>, before it leaves the host. Redacting downstream means the secret was '
  'already written to disk and shipped across the network'),
], [
 """Failures. Kafka unavailable: nothing visible happens, because agents buffer to local disk and drain """
 """when it comes back. That is the whole reason the local buffer exists &mdash; it is what makes Kafka """
 """non-critical rather than a single point of failure.""",
 """Agent buffer fills during an incident and debug and info lines are lost. Drop by severity, keep """
 """errors, and emit a dropped counter. That is expected behaviour rather than a bug &mdash; but it """
 """must be visible, or someone will debug a phantom.""",
 """Indexing consumer falls behind and recent logs are not searchable yet. Kafka retains twenty-four """
 """hours so it catches up. Alert on consumer lag, and treat search being a few minutes stale as a """
 """degradation rather than an outage &mdash; getting that severity right matters at three in the """
 """morning.""",
 """Hot store full means writes rejected and search broken. Enforce retention aggressively, and alert """
 """on days of headroom rather than percent full. Ninety percent full tells you nothing; three days of """
 """headroom tells you whether to act tonight.""",
 """A single service starts logging a thousand times more and drowns out everyone else. Per-service """
 """quotas at the agent. One noisy service must not be able to consume the shared pipeline &mdash; and """
 """notice this is the rate limiter from lesson four point one, applied internally to your own """
 """infrastructure.""",
 """And logs containing passwords or personal data is a compliance incident rather than an outage. """
 """Redact at the agent, before it leaves the host. Redacting downstream is too late &mdash; the secret """
 """has already been written to disk and shipped across the network, and now it is in your backups """
 """too.""",
])

say('What I should actually say in the room', [
 'The thing that makes logs different from metrics is that I do not control the input. An application '
 'in trouble logs 100&times; more, exactly when the pipeline is already stressed.',
 'So the first rule is that the agent never blocks the application. Bounded memory buffer, spill to a '
 'capped disk buffer, then drop by severity &mdash; debug, then info, then warn, never error.',
 'And always emit a dropped-lines counter, because silent loss means someone debugs a code path they '
 'think never ran.',
 'Kafka sits in the middle as a shock absorber with 24 hours of retention, which is what lets every '
 'consumer downstream be unreliable without losing data.',
 'Ten thousand hosts at a thousand lines a second is about 5 GB/s, or 430 TB a day raw &mdash; and logs '
 'compress about 10:1, so compress at the agent where the CPU is free.',
 'I would index only a few fields &mdash; trace ID, service, level, time &mdash; because a full-text '
 'index is about 5&times; the data, and the index would cost more than the logs.',
 'On ordering: I will give per-request ordering using a trace ID and a sequence number from the source. '
 'I will not promise global ordering across the fleet, because that needs a single sequencer and nobody '
 'should build one for logs.',
], [
 """The sentences. Open with what makes logs different from metrics, because it frames every decision """
 """that follows and most candidates treat the two as the same problem.""",
 """Then the agent rule with the explicit drop order, and the dropped counter with its consequence. """
 """Then Kafka as shock absorber, and the arithmetic.""",
 """Then the indexing decision justified by the index being bigger than the data. And finish on """
 """ordering, where the valuable move is declining to promise the impossible while offering the thing """
 """they actually wanted.""",
])

followups([
 'How do agents collect logs?',
 'How do you partition the pipeline?',
 'Why Kafka?',
 'How do you store and index them?',
 'What is your retention policy?',
 'How do you query and aggregate?',
 'How do you handle backpressure?',
 'How do you handle ordering?',
], [
 'Now the logs are an audit trail and loss is unacceptable. What changes?',
 'How do you find all logs for one request across 12 services?',
 'How much does this cost, and what is the first thing you would cut?',
 'A log line contains a customer password. What happens next?',
 'How would you test that your pipeline survives a 100&times; spike?',
],
 """The reported follow-ups walk the pipeline and we have covered all of them. Why Kafka specifically: """
 """because it decouples producers from consumers, retains data so consumers can fail, and partitions """
 """for both ordering and parallelism. It is a buffer, a fan-out and an ordering guarantee in one """
 """component, and that is why it keeps appearing in these designs.""",
 """The staff-level follow-ups push on the assumptions. Audit logs invert the dropping decision """
 """entirely. Finding all logs for one request across twelve services is the trace I-D, which has to be """
 """propagated by every service &mdash; an organisational problem as much as a technical one. Cost: hot """
 """storage and indexing dominate, so the first cut is index fewer fields. A password in a log line """
 """means redaction at the agent plus a rotation of that credential plus a scrub of the backups, which """
 """is genuinely painful and is why you redact at the source. And testing a hundred-times spike means """
 """load testing the pipeline with synthetic log storms, which almost nobody does until after the """
 """first incident.""")

cheatsheet('Distributed logging &mdash; the one-page card', [
 ('Requirements', 'Collect, ship, store, index and query logs from 10k hosts &mdash; and survive a '
                  '100&times; spike'),
 ('Scale', '10M lines/s, ~5 GB/s, 430 TB/day raw, ~43 TB/day compressed. Full-text index would be '
           '5&times; the data'),
 ('Core architecture', 'App &rarr; agent (buffer, compress, redact) &rarr; Kafka &rarr; independent '
                       'consumers: hot store, cold store, aggregator'),
 ('Data store', 'Hot indexed store 7 days; compressed raw in object storage 90 days; pre-aggregates '
                'for dashboards'),
 ('Partition key', '<b>Host ID</b> &mdash; spreads load and gives per-host ordering for free'),
 ('Cache', 'Not really applicable. Pre-aggregates serve the role for dashboards'),
 ('Queue', 'Kafka, 24 h retention. <b>It is the shock absorber</b> that makes consumers allowed to fail'),
 ('Consistency', 'At-least-once. Duplicate log lines are acceptable; missing ERROR lines are not'),
 ('Failure handling', '<b>Agent never blocks the app</b>; drop by severity; count what you drop; '
                      'per-service quotas; redact at source'),
 ('Key deep dives', 'Backpressure and drop policy &middot; achievable vs impossible ordering'),
 ('Biggest trade-off', 'Completeness vs the health of the service being logged. <b>The service always '
                       'wins</b>'),
], [
 """The card. Requirements include surviving the spike, because that is the requirement. Scale &mdash; """
 """and the number to carry is that a full-text index would be five times the data.""",
 """Architecture in one line, with Kafka in the middle and independent consumers. Partition by host """
 """I-D, which spreads load and gives per-host ordering for free &mdash; one decision, two """
 """benefits.""",
 """Consistency is at-least-once: duplicate log lines are fine, missing error lines are not. Failure """
 """handling leads with the agent never blocking. And the biggest trade-off, which is the sentence to """
 """leave with: completeness versus the health of the service being logged, and the service always """
 """wins.""",
])

say('The 60-second answer', [
 'What makes logging different from metrics is that I do not control the volume &mdash; a service in '
 'trouble logs a hundred times more, precisely when my pipeline is already stressed. So the design is '
 'really about what happens on the day I cannot keep up.',
 'Rule one: the agent never blocks the application. Bounded memory buffer, spilling to a capped local '
 'disk buffer, then dropping by severity &mdash; debug, info, warn, never error &mdash; and always '
 'emitting a dropped-lines counter, because silent loss makes people debug code paths they think never '
 'ran.',
 'Agents compress about 10:1 and ship to Kafka, partitioned by host. Kafka with 24 hours of retention '
 'is the shock absorber: it is what lets every downstream consumer fail without losing data.',
 'Ten thousand hosts at a thousand lines a second is around 5 GB/s, 430 TB a day raw and about 43 '
 'compressed.',
 'From Kafka, independent consumers: a hot indexed store for 7 days, compressed raw in object storage '
 'for 90, and an aggregator for dashboards. I index only trace ID, service, level and time, because a '
 'full-text index would be five times the size of the data itself.',
 'And on ordering, I would offer per-request ordering via a trace ID and a source sequence number, and '
 'explicitly decline global ordering across the fleet &mdash; that needs a single sequencer, and nobody '
 'should build one of those for logs.',
], [
 """The sixty-second answer. It opens on the property that distinguishes this from metrics, which """
 """immediately separates you from candidates who recite the same pipeline for both.""",
 """The second sentence is the longest on purpose &mdash; the drop policy is the heart of the design. """
 """And the last sentence is worth landing cleanly, because declining to promise global ordering, with """
 """a reason, reads as confidence rather than evasion.""",
], kicker='60-second interview answer')
