# -*- coding: utf-8 -*-
"""Chapter 3, Lesson 3 — design a Kafka-like distributed message queue."""
from lib import *

lesson_header('3.3', 'Design a Kafka-like distributed message queue',
              'Partitioned log &middot; replication &middot; consumer groups &middot; delivery semantics',
              dict(reports='2 independent reports',
                   latest='June 2025', level='Staff SWE',
                   conf='HIGH &mdash; and LinkedIn wrote Kafka',
                   sources='LeetCode Discuss, Blind ID3 thread'), 32,
              """Chapter three, lesson three: design a Kafka-like distributed message queue. Two """
              """independent reports, a Staff-level one from June twenty twenty-five, plus repeated """
              """mentions in the infrastructure interview threads. And this question comes with a """
              """condition attached that none of the others do: Kafka was built at LinkedIn. You are """
              """being asked to design the house speciality, in front of people who may well have worked """
              """on it. The bar for depth is higher here than anywhere else in this course, and a generic """
              """answer will land worse than it would elsewhere.""")

evidence('Where this question comes from', [
 ('LeetCode Discuss &mdash; Staff SWE loop', 'Jun 2025', 'Staff SWE',
  'Asked to design a <b>Kafka-like distributed message queue</b>. Follow-ups: partitioning and '
  'ordering, replication and in-sync replicas, consumer groups, exactly-once semantics'),
 ('Blind &mdash; ID3 / infrastructure threads', '2025&ndash;2026', 'Senior / Staff, Infra',
  'Message queues named repeatedly as a design topic for the Systems &amp; Infrastructure round'),
], """The evidence. A LeetCode Discuss report from a Staff loop in June twenty twenty-five, asked to """
     """design a Kafka-like distributed message queue, with follow-ups on partitioning and ordering, """
     """replication and in-sync replicas, consumer groups, and exactly-once semantics.""",
 ["""And separately, message queues are named repeatedly as a design topic in the Blind threads about """
  """the infrastructure design round. Two independent sources, and the second is weaker — it names a """
  """topic rather than reporting a question — so I am counting this as two reports rather than """
  """three."""],
 caveat='One thing to hold in mind throughout: Kafka originated at LinkedIn. Expect deeper follow-ups '
        'here than on any other question, and expect them to know when an answer is hand-waving.',
 narration_caveat="""And hold one thing in mind throughout this lesson. Kafka originated at LinkedIn. """
                  """Expect deeper follow-ups here than on any other question, and expect your """
                  """interviewer to know immediately when an answer is hand-waving. That is not a reason """
                  """to avoid the question — it is a reason to actually understand the mechanism rather """
                  """than the diagram.""")

sid = beat('Why this is interesting', 'The log is the idea. Everything else is consequence.',
           '<div class="bigidea">A queue deletes a message when it is consumed. <b>A log does not.</b> '
           'That single difference produces every property that matters.</div>'
           '<div style="margin-top:24px;font-size:27px;line-height:1.68">'
           'Because the log is an <b>append-only, immutable sequence</b>:<br><br>'
           '&bull; Writes are <b>sequential</b> &mdash; even on spinning disks that is fast, and on SSDs '
           'it is very fast<br>'
           '&bull; Many consumers can read the <b>same</b> data independently, each at its own '
           'position<br>'
           '&bull; A consumer can <b>rewind</b> and reprocess &mdash; replay is free, not a feature '
           'you build<br>'
           '&bull; The broker holds <b>no per-consumer state</b> except an offset, so it stays simple '
           'and fast<br>'
           '&bull; Reads mostly hit the <b>page cache</b>, because consumers read recent data<br><br>'
           '<span style="color:#ffd483">Say this early: <b>&ldquo;I am building a log, not a '
           'queue.&rdquo;</b> Everything that follows is a consequence of that one choice.</span></div>',
           """Why is this interesting? Because there is exactly one idea in it, and everything else is a """
           """consequence. A traditional queue deletes a message once it is consumed. A log does not — it """
           """keeps the message and each consumer tracks its own position.""", step=0)
seg(sid, 1, """From that single difference, everything follows. Writes are sequential appends, which is """
            """fast even on spinning disks and very fast on SSDs. Many consumers can read the same data """
            """independently, each at its own position, without interfering.""")
seg(sid, 2, """A consumer can rewind and reprocess, so replay is free rather than a feature you have to """
            """build. The broker holds no per-consumer state except an offset, which is what keeps it """
            """simple and fast. And reads mostly hit the operating system page cache, because consumers """
            """are usually reading data that was written seconds ago and is still in memory.""")
seg(sid, 3, """So say it early and explicitly: I am building a log, not a queue. That one sentence frames """
            """the entire design, and it tells an interviewer who knows this domain that you understand """
            """what the thing actually is — rather than treating it as a box labelled Kafka.""")

think('Producers write a million messages a second. Consumers must see messages for the same user in order. How do you get both — the throughput and the ordering?',
      30,
      """Pause. A million messages a second, and messages for the same user must be consumed in order. """
      """Those two requirements pull in opposite directions — throughput wants parallelism, ordering """
      """wants serialisation. How do you get both?""",
      """This is the central trade in the whole system, and the answer is the thing that makes Kafka """
      """Kafka.""")

sid = beat('The key insight', 'Ordering is per partition, and that is a feature',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Global ordering</b> across a topic means one writer, one reader, no parallelism. It does '
           'not scale, and almost nobody actually needs it.<br><br>'
           '<b>Per-partition ordering</b> means: messages within a partition are strictly ordered, and '
           'partitions are independent. So you get parallelism equal to your partition count.<br><br>'
           'You then choose the <b>partition key</b> to make ordering land where it matters:<br>'
           '&bull; key = <code>user_id</code> &rarr; all events for a user are ordered, and different '
           'users run in parallel<br>'
           '&bull; key = <code>null</code> &rarr; round-robin, maximum throughput, no ordering<br><br>'
           '<span style="color:#ffd483">&ldquo;I do not need global ordering. I need ordering '
           '<b>per key</b>, and I will make the key the thing that must be ordered.&rdquo; That '
           'sentence resolves the whole tension.</span></div>',
           """Here is the resolution. Global ordering across a topic means one writer and one reader and """
           """no parallelism at all. It does not scale — and the important observation is that almost """
           """nobody actually needs it.""", step=0)
seg(sid, 1, """Per-partition ordering means messages within a partition are strictly ordered, and """
            """partitions are independent of each other. So your parallelism equals your partition """
            """count, and your ordering guarantee is scoped to a partition.""")
seg(sid, 2, """Then you choose the partition key to make ordering land exactly where it matters. Key by """
            """user id and every event for a given user is ordered, while different users process in """
            """parallel. Key by nothing and you round-robin for maximum throughput with no ordering at """
            """all.""")
seg(sid, 3, """The sentence that resolves the tension is: I do not need global ordering, I need ordering """
            """per key, and I will make the partition key the thing that must be ordered. That reframing """
            """— from a global requirement to a scoped one — is the single most useful move in this """
            """design, and it is the same move as "make the constraint local" that runs through """
            """distributed systems generally.""")

clarify('What I would clarify first', [
 ('What ordering is actually required &mdash; global, per key, or none?',
  'Decides your partition key and therefore your parallelism. <b>Global ordering caps you at one '
  'partition</b>, so establish early that it is not needed.'),
 ('What delivery guarantee does the consumer need?',
  'At-most-once, at-least-once, or effectively-once. Each costs something different, and '
  '<b>at-least-once plus idempotent consumers</b> is usually the right answer.'),
 ('How long must messages be retained?',
  'Retention is a storage decision <i>and</i> a replay capability. Seven days means a consumer can '
  'recover from a week-old bug.'),
 ('How many consumers read the same topic?',
  'The log model shines here &mdash; each consumer group reads independently. If there is only ever '
  'one consumer, a simpler queue may genuinely be the better answer.'),
 ('Message size, and is it uniform?',
  '1 KB events and 10 MB payloads are different systems. Large messages usually belong in object '
  'storage with a <b>pointer</b> on the log.'),
 ('Can we lose messages on broker failure?',
  'Decides acks and replication settings &mdash; and this is the one where the honest answer costs '
  'latency, so make it explicit.'),
], [
 """What I would clarify. What ordering is actually required — global, per key, or none? This decides """
 """your partition key and therefore your parallelism, and establishing early that global ordering is """
 """not needed saves the design.""",
 """What delivery guarantee does the consumer need? At-most-once, at-least-once, or effectively-once. """
 """Each costs something different, and at-least-once with idempotent consumers is usually the right """
 """answer — the same conclusion we reached in the scheduler, for the same reason.""",
 """How long must messages be retained? Retention is both a storage decision and a capability: seven """
 """days of retention means a consumer can recover from a bug you shipped a week ago by rewinding, """
 """which is enormously valuable and is not obvious from the word retention.""",
 """How many consumers read the same topic? This is where the log model shines, since each consumer """
 """group reads independently. And be willing to say the opposite: if there is only ever one consumer """
 """and no replay requirement, a simpler queue may genuinely be the better answer.""",
 """Message size and uniformity. One-kilobyte events and ten-megabyte payloads are different systems, """
 """and large messages usually belong in object storage with only a pointer on the log.""",
 """And can we lose messages on broker failure? That decides your acknowledgement and replication """
 """settings, and it is the one where the honest answer costs latency — so make the trade explicit """
 """rather than quietly choosing.""",
])

capacity('Capacity — and what the numbers force', [
 ('1M messages / s &times; 1 KB', '1M &times; 1 KB', '<b>1 GB / s ingest</b>',
  'Serious but ordinary. <b>Sequential</b> writes are what make it possible'),
 ('&times;3 replication', '1 GB/s &times; 3', '3 GB/s of disk writes, 2 GB/s network',
  'Replication traffic is <b>the dominant network cost</b> &mdash; not client traffic'),
 ('7-day retention', '1 GB/s &times; 604,800 s', '&asymp; 600 TB raw',
  '1.8 PB with replication. <b>Storage, not throughput, sets your cluster size</b>'),
 ('Per broker: ~100 MB/s sustained write', '3 GB/s &divide; 100 MB/s', '<b>~30 brokers minimum</b>',
  'Disk throughput per broker is the real limit, not CPU'),
 ('Partitions: target ~10 MB/s each', '1 GB/s &divide; 10 MB/s', '<b>~100 partitions</b>',
  'Also the <b>maximum consumer parallelism</b> &mdash; partitions cap consumers, not the reverse'),
 ('5 consumer groups read everything', '1 GB/s &times; 5', '5 GB/s read',
  'Reads are <b>5&times; writes</b>. Mostly served from page cache because consumers are near the tail'),
], [
 """The capacity work. A million messages a second at a kilobyte each is one gigabyte a second of """
 """ingest. That is serious but ordinary for this kind of system, and it is possible specifically """
 """because the writes are sequential appends rather than random updates.""",
 """With three-way replication that is three gigabytes a second of disk writes and about two gigabytes """
 """a second of network traffic between brokers. Worth saying plainly: replication traffic is the """
 """dominant network cost here, not client traffic. People size networks for producers and get """
 """surprised.""",
 """Seven days of retention at a gigabyte a second is roughly six hundred terabytes raw, or one point """
 """eight petabytes with replication. So storage, not throughput, sets your cluster size — which is the """
 """opposite of what most people assume about a messaging system.""",
 """Each broker sustains perhaps a hundred megabytes a second of writes, so three gigabytes a second """
 """needs at least thirty brokers. And note the limit is disk throughput rather than CPU, which is why """
 """these clusters look the way they do.""",
 """Partitions: target around ten megabytes a second each, so about a hundred partitions. And here is """
 """the line to remember — your partition count is also your maximum consumer parallelism. Partitions """
 """cap consumers, not the other way round, so you choose partition count for the parallelism you will """
 """need later, not the throughput you need today.""",
 """And with five consumer groups reading everything, reads are five times writes. Most of that is """
 """served from the page cache, because consumers generally read data that was written seconds ago and """
 """is still in memory — which is why this works at all.""",
])

sid = beat('Data model', 'The log, the offset, and what a broker does not store',
           '<div style="font-size:26px;line-height:1.68">'
           '<b>Topic</b> &rarr; N <b>partitions</b> &rarr; each an ordered, append-only sequence.<br>'
           'A message&rsquo;s address is <code>(topic, partition, offset)</code>. Offsets are '
           'monotonic within a partition and mean nothing across partitions.<br><br>'
           '<b>On disk</b>, a partition is not one file. It is a series of <b>segments</b>:<br>'
           '<span style="font-family:JetBrains Mono,monospace;font-size:21px;color:#9fb4cc">'
           '00000000.log &nbsp; 00524288.log &nbsp; 01048576.log &hellip;</span><br>'
           'plus a sparse index mapping offset &rarr; byte position. Retention deletes <b>whole '
           'segments</b> &mdash; which is why expiry is nearly free, and why you cannot delete one '
           'message.<br><br>'
           '<b>What the broker does not store:</b> which messages a consumer has seen. That is just an '
           'offset the consumer commits. <b>The broker does not track delivery at all</b> &mdash; and '
           'that absence is what lets one broker serve thousands of consumers.</div>',
           """The data model. A topic has N partitions, each an ordered append-only sequence, and a """
           """message's address is the triple of topic, partition and offset. Offsets are monotonic """
           """within a partition and mean nothing across partitions — which is worth saying, because """
           """people assume a global ordering that does not exist.""", step=0)
seg(sid, 1, """On disk a partition is not one enormous file. It is a series of segments, each covering a """
            """range of offsets, plus a sparse index mapping offsets to byte positions. That structure """
            """has a lovely consequence: retention deletes whole segments, so expiring old data is """
            """nearly free — you unlink a file. It also means you cannot delete an individual message, """
            """which becomes a real problem when we get to the privacy question later.""")
seg(sid, 2, """And the most important line: the broker does not store which messages a consumer has seen. """
            """That is just an offset the consumer commits. The broker does not track delivery at all.""")
seg(sid, 3, """That absence is the whole trick. A traditional queue tracks per-message, per-consumer """
            """delivery state, and that bookkeeping is what limits it. Removing it is what lets one """
            """broker serve thousands of consumers cheaply — and pointing out what a system deliberately """
            """does not do is often the sharpest way to explain why it is fast.""")

# ------------------------------------------------------------------ architecture
A = Arch('Architecture — producers, partitions, replicas, groups', kicker='Progressive disclosure',
         height=810)
A.box('p1',   70, 250, 170, 85, 'Producer', kind='neutral', step=0, focus=0, small=True)
A.box('p2',   70, 380, 170, 85, 'Producer', kind='neutral', step=0, focus=0, small=True)

A.box('b0',  340, 180, 250, 95, 'Broker 1', 'leader: P0, P3', kind='ok', step=0, focus=[0, 1])
A.box('b1',  340, 320, 250, 95, 'Broker 2', 'leader: P1', kind='ok', step=0, focus=[0, 1])
A.box('b2',  340, 460, 250, 95, 'Broker 3', 'leader: P2', kind='ok', step=0, focus=[0, 1])
A.arrow('p1', 'b0', step=0, focus=0)
A.arrow('p2', 'b1', step=0, focus=0)

A.note(340, 600, 'Each partition has **one leader**. Producers write only to the leader;\\n'
                 'that is what makes ordering within a partition well defined.',
       step=1, kind='neutral', w=640, size='m')

A.box('r1',  680, 180, 210, 95, 'Followers', 'replicate P0', kind='shared', step=2, focus=2, small=True)
A.box('r2',  680, 320, 210, 95, 'Followers', 'replicate P1', kind='shared', step=2, focus=2, small=True)
A.arrow('b0', 'r1', step=2, focus=2)
A.arrow('b1', 'r2', step=2, focus=2)
A.note(680, 440, '**ISR** = replicas caught up\\nwith the leader.\\nacks=all waits for these.',
       step=3, kind='shared', w=300, size='m')

A.box('g1',  1010, 180, 240, 95, 'Consumer group A', '3 consumers', kind='info', step=4, focus=4)
A.box('g2',  1010, 320, 240, 95, 'Consumer group B', '1 consumer', kind='info', step=4, focus=4)
A.arrow('b0', 'g1', step=4, focus=4, via=[(960, 227)])
A.arrow('b1', 'g2', step=4, focus=4, via=[(960, 367)])

A.note(1310, 180, '**Each group reads everything,\\nindependently.**\\n\\n'
                  'Within a group, each partition\\ngoes to exactly one consumer.\\n\\n'
                  'So group A parallelises across\\n3 consumers; group B reads it\\nall with 1.\\n\\n'
                  '**Partitions cap consumers.**',
       step=5, kind='ok', w=520, size='m')
A.narrate(0, """The architecture. Producers write to brokers, and each partition has exactly one leader """
              """broker that owns it. A producer writing to partition zero always writes to whichever """
              """broker leads partition zero.""")
A.narrate(1, """That single-leader rule is what makes ordering within a partition well defined — there is """
              """one place where the order is decided, so there is no ambiguity to resolve later. """
              """Ordering is not an algorithm here; it is a consequence of having one writer.""")
A.narrate(2, """Followers replicate from the leader, pulling rather than being pushed, which keeps the """
              """leader simple.""")
A.narrate(3, """The in-sync replica set — the ISR — is the set of replicas that are caught up with the """
              """leader. When a producer asks for acks equals all, it is waiting for the ISR, not for """
              """every replica. That distinction matters and we will come back to it.""")
A.narrate(4, """Then consumer groups. Group A has three consumers, group B has one, and both read """
              """everything independently — because the log is not consumed destructively.""")
A.narrate(5, """Within a group, each partition is assigned to exactly one consumer, which is what """
              """preserves ordering per partition while allowing parallelism across partitions. So group """
              """A parallelises its work across three consumers while group B reads the same data with """
              """one. And the consequence to say out loud: partitions cap consumers. If you have a """
              """hundred partitions you can never usefully run more than a hundred consumers in a """
              """group — the hundred and first sits idle.""")
A.build()

tradeoff('The durability trade: what does a producer wait for?', [
 ('acks = 0 &mdash; fire and forget', 'deny',
  ['Lowest possible latency', 'Highest throughput'],
  ['<b>Messages are lost silently</b> if the broker is down',
   'No confirmation of anything', 'Only defensible for metrics-style data you can afford to lose']),
 ('acks = 1 &mdash; leader only', 'shared',
  ['Fast: one disk write, no waiting for followers', 'Confirms the leader received it'],
  ['<b>If the leader dies before followers replicate, the message is gone</b>',
   'A silent data-loss window during exactly the failure you care about']),
 ('acks = all &mdash; the full ISR', 'ok',
  ['<b>No data loss</b> while at least one in-sync replica survives',
   'The only setting you can honestly call durable',
   'Combined with min.insync.replicas, gives a real guarantee'],
  ['Higher latency &mdash; you wait for the slowest in-sync replica',
   'Throughput drops', 'If the ISR shrinks to one, you are silently back to acks=1']),
], decision='acks = all, with min.insync.replicas = 2. That combination says: do not accept a write '
            'unless at least two replicas have it. It is the only configuration that survives a single '
            'broker loss without losing data.',
 flip='For high-volume, low-value telemetry where losing a second of data is acceptable, acks=1 or '
      'even 0 is the right economic choice. Match the guarantee to what the data is worth &mdash; '
      'paying for durability you do not need is a real cost.',
 narration=[
  """Now the durability trade, and this is where a knowledgeable interviewer will press hardest. What """
  """does a producer wait for before considering a write successful? Acks equals zero is fire and """
  """forget: lowest latency, highest throughput, and messages vanish silently if the broker is down. """
  """Only defensible for data you can genuinely afford to lose.""",
  """Acks equals one waits for the leader only. Fast, and it confirms the leader received it. But if """
  """the leader dies before followers replicate, the message is gone — and notice when that happens: """
  """during exactly the failure you were trying to protect against. It is a silent data-loss window at """
  """the worst possible moment.""",
  """Acks equals all waits for the full in-sync replica set, and it is the only setting you can honestly """
  """call durable. You lose nothing as long as one in-sync replica survives. The costs are real: higher """
  """latency because you wait for the slowest in-sync replica, and lower throughput. And there is a """
  """subtle trap — if the ISR shrinks to just the leader, acks equals all silently degrades to acks """
  """equals one, because the set you are waiting for has one member.""",
  """Which is why the answer is acks equals all combined with minimum in-sync replicas of two. Together """
  """they say: do not accept a write unless at least two replicas have it, and if you cannot manage """
  """that, fail the write rather than pretending. Naming both settings together is the answer that """
  """shows you have operated this, because the trap is exactly what catches people in production.""",
  """And the reversal: for high-volume low-value telemetry where losing a second of data is fine, acks """
  """equals one or even zero is the right economic choice. Match the guarantee to what the data is """
  """worth — paying for durability you do not need is a real and often invisible cost.""",
 ])

sid = beat('Deep dive 1', 'Why the log is fast — and it is not clever code',
           '<div style="font-size:26px;line-height:1.68">'
           'Four mechanisms, and none of them is a clever algorithm:<br><br>'
           '<b>1. Sequential I/O.</b> Appending to a file is the fastest thing a disk does. Random '
           'writes are orders of magnitude slower. The log never updates in place, so it <b>never does '
           'a random write</b>.<br><br>'
           '<b>2. The page cache.</b> The broker does not maintain its own cache. It writes to the OS '
           'page cache and lets the kernel flush. Consumers reading recent data hit memory &mdash; and '
           '<b>consumers almost always read recent data</b>.<br><br>'
           '<b>3. Zero-copy.</b> Sending a segment to a consumer goes disk &rarr; socket via '
           '<code>sendfile</code>, never through application memory. No serialisation, no copying, '
           'no garbage.<br><br>'
           '<b>4. Batching.</b> Producers batch, brokers store batches, consumers fetch batches. '
           'Per-message overhead is amortised, and compression works far better across a batch than '
           'per message.<br><br>'
           '<span style="color:#ffd483">The lesson generalises: <b>this system is fast because of what '
           'it refuses to do</b> &mdash; no per-message state, no random writes, no copying.</span></div>',
           """Deep dive one: why the log is fast. And the thing I want you to take from this is that none """
           """of the four mechanisms is a clever algorithm. They are all about doing less.""", step=0)
seg(sid, 1, """First, sequential input-output. Appending to a file is the fastest thing a disk does, and """
            """random writes are orders of magnitude slower. Because the log never updates in place, it """
            """never performs a random write at all.""")
seg(sid, 2, """Second, the page cache. The broker does not maintain its own cache in application memory — """
            """it writes to the operating system page cache and lets the kernel handle flushing. """
            """Consumers reading recent data hit memory rather than disk, and consumers almost always """
            """read recent data. Letting the kernel do the caching rather than reimplementing it is the """
            """decision here.""")
seg(sid, 3, """Third, zero-copy. Sending a segment to a consumer goes from disk to socket directly via the """
            """sendfile system call, without passing through application memory. No deserialising, no """
            """copying, no garbage collection pressure. If you mention sendfile by name in an """
            """infrastructure interview, that lands.""")
seg(sid, 4, """Fourth, batching at every level: producers batch, brokers store batches, consumers fetch """
            """batches. Per-message overhead is amortised, and compression works far better across a """
            """batch than on individual messages.""")
seg(sid, 5, """And the generalisable lesson, which is worth stating: this system is fast because of what """
            """it refuses to do. No per-message state, no random writes, no copying into user space. """
            """That framing is more valuable than the four facts, because you can apply it to designs """
            """you have never seen.""")

sid = beat('Deep dive 2', 'Consumer groups, offsets, and the rebalance problem',
           '<div style="font-size:26px;line-height:1.68">'
           '<b>The assignment:</b> within a group, each partition is owned by exactly one consumer. '
           'Add a consumer and partitions are redistributed; lose one and its partitions move.<br><br>'
           '<b>Offsets</b> are committed by the consumer, to the broker, per group. Commit <b>after</b> '
           'processing gives at-least-once; commit <b>before</b> gives at-most-once. '
           '<b>That one ordering choice is your delivery guarantee</b> &mdash; not a config flag.<br><br>'
           '<b>The rebalance problem:</b> a naive rebalance <b>stops the whole group</b> &mdash; every '
           'consumer pauses, reassigns, resumes. With a slow consumer flapping in and out, the group '
           'spends its life rebalancing and processes almost nothing.<br><br>'
           '<b>Fixes:</b> sticky assignment so consumers keep their partitions across rebalances; '
           'incremental rebalancing so only affected partitions move; and generous session timeouts so '
           'a GC pause is not mistaken for death.<br><br>'
           '<span style="color:#ffd483">&ldquo;The most common production problem with this system is '
           'not throughput &mdash; it is <b>rebalance storms</b>.&rdquo;</span></div>',
           """Deep dive two: consumer groups, offsets, and the problem that actually bites people. The """
           """assignment rule is that within a group, each partition is owned by exactly one consumer. """
           """Add a consumer and partitions are redistributed; lose one and its partitions move """
           """elsewhere.""", step=0)
seg(sid, 1, """Offsets are committed by the consumer to the broker, per group. And here is a detail worth """
            """dwelling on: committing after processing gives at-least-once delivery, while committing """
            """before processing gives at-most-once. That single ordering choice in the consumer loop is """
            """your delivery guarantee. It is not a configuration flag you set on the broker — it is """
            """where you put one line of code.""")
seg(sid, 2, """Now the rebalance problem, which is the most common production issue with these systems. A """
            """naive rebalance stops the entire group: every consumer pauses, partitions are reassigned, """
            """everyone resumes. If you have one slow consumer flapping in and out of the group, the """
            """group spends its life rebalancing and processes almost nothing — and the symptom looks """
            """like a throughput problem when it is really a stability problem.""")
seg(sid, 3, """The fixes are sticky assignment, so consumers keep their existing partitions across a """
            """rebalance rather than being shuffled randomly; incremental rebalancing, so only the """
            """affected partitions move instead of all of them; and generous session timeouts, so a """
            """garbage collection pause is not mistaken for a dead consumer.""")
seg(sid, 4, """The sentence to say is: the most common production problem with this system is not """
            """throughput, it is rebalance storms. That is the kind of statement that only comes from """
            """having operated one, and it will be recognised as such.""")

sid = beat('Deep dive 3', 'Delivery semantics, honestly',
           '<table class="fail" style="top:44px"><thead><tr><th>Guarantee</th><th>How</th>'
           '<th>What it costs</th></tr></thead><tbody>'
           '<tr data-step="0"><td class="f-c">At-most-once</td>'
           '<td>Commit the offset <b>before</b> processing</td>'
           '<td>Messages are lost if the consumer dies mid-processing. Rarely what anyone wants</td></tr>'
           '<tr data-step="1"><td class="f-c">At-least-once</td>'
           '<td>Commit the offset <b>after</b> processing</td>'
           '<td>Duplicates on retry. <b>The sane default</b>, paired with idempotent consumers</td></tr>'
           '<tr data-step="2"><td class="f-c">&ldquo;Exactly-once&rdquo;</td>'
           '<td>Idempotent producer (sequence numbers dedupe retries) + transactions spanning the '
           'consume-process-produce cycle</td>'
           '<td>Real, but <b>only within the system</b>. Latency cost, complexity cost, and it '
           '<b>does not extend to your database or a third-party API</b></td></tr>'
           '</tbody></table>'
           '<div class="to-flip" data-step="3"><b>Say this:</b> exactly-once here means '
           '&ldquo;exactly-once processing <i>within</i> the log&rsquo;s world&rdquo;. The moment your '
           'consumer writes to an external system, you are back to at-least-once plus idempotency '
           '&mdash; the same conclusion as the scheduler.</div>',
           """Deep dive three: delivery semantics, and I want to handle this honestly because it was a """
           """named follow-up. At-most-once means committing the offset before processing, so messages """
           """are lost if the consumer dies mid-processing. That is rarely what anyone wants.""", step=0)
seg(sid, 1, """At-least-once means committing after processing, so you get duplicates on retry. This is """
            """the sane default, paired with idempotent consumers — exactly the conclusion we reached in """
            """the scheduler lesson, reached again by the same reasoning.""")
seg(sid, 2, """Exactly-once in this system is real, and it is more subtle than the scheduler case. It """
            """comes from two mechanisms: an idempotent producer, where sequence numbers let the broker """
            """discard duplicate retries, and transactions that span the consume-process-produce cycle so """
            """that reading, processing and writing commit atomically. That genuinely works.""")
seg(sid, 3, """But — and this is the part to say clearly — it works only within the system's own world. """
            """The moment your consumer writes to an external database or calls a third-party API, you """
            """are back to at-least-once plus idempotency. So exactly-once here means exactly-once """
            """processing within the log's boundary, not exactly-once effects on the outside world. """
            """Being precise about that boundary is exactly the kind of answer that separates someone who """
            """has read the documentation from someone who has debugged it.""")

failures('What happens when each piece dies', [
 ('A follower replica', 'Nothing',
  'It falls out of the ISR and catches up later. If the ISR drops below min.insync.replicas, '
  '<b>writes start failing</b> &mdash; which is correct, not a bug'),
 ('A partition leader', 'Brief unavailability for that partition only',
  'A new leader is elected from the ISR. Other partitions are unaffected &mdash; <b>failure is '
  'scoped to a partition</b>'),
 ('A whole broker', 'Every partition it led is briefly unavailable',
  'Leadership moves. Then the cluster re-replicates its data, which is a <b>large background load '
  'spike</b> &mdash; expect a latency bump'),
 ('A consumer', 'Its partitions stop being processed',
  'Rebalance reassigns them. Work resumes from the <b>last committed offset</b>, so recent messages '
  'are reprocessed &mdash; hence idempotency'),
 ('A slow consumer', '<b>Lag grows silently</b>',
  'The broker does not care &mdash; it is unaffected. <b>This is the failure that hides</b>: '
  'everything looks healthy while a consumer falls hours behind'),
 ('Disk fills', 'Writes fail across the cluster',
  'Retention must be enforced by <b>both</b> time and size. A size cap is the one that saves you'),
 ('A hot partition', 'One consumer is overloaded; its partition lags',
  'Caused by a skewed key &mdash; too many messages for one user. Repartitioning is <b>expensive and '
  'breaks ordering</b>, so choose the key carefully up front'),
], [
 """The failure table. A follower replica dying is a non-event: it falls out of the in-sync set and """
 """catches up later. But note the consequence — if the ISR drops below your minimum, writes start """
 """failing. That is correct behaviour rather than a bug, and being able to say so confidently matters, """
 """because the instinct is to treat failed writes as the problem when they are the protection.""",
 """A partition leader dying means brief unavailability for that partition only, while a new leader is """
 """elected from the in-sync set. Other partitions are unaffected, so failure is scoped to a partition """
 """rather than the cluster.""",
 """A whole broker dying makes every partition it led briefly unavailable, leadership moves, and then """
 """the cluster re-replicates its data — which is a large background load spike. Expect a latency bump """
 """during recovery, and say so, because people are surprised when recovery hurts.""",
 """A consumer dying triggers a rebalance, and work resumes from the last committed offset, so recent """
 """messages are reprocessed. Which is precisely why consumers must be idempotent.""",
 """Now the failure that hides: a slow consumer. Lag grows silently. The broker is entirely unaffected """
 """and every broker metric looks perfect while a consumer falls hours behind. This is the one to """
 """volunteer, because it is invisible from the place people are looking.""",
 """Disk filling causes writes to fail across the cluster, so retention must be enforced by both time """
 """and size — and the size cap is the one that actually saves you, because time-based retention """
 """assumes a volume that can change.""",
 """And a hot partition, caused by a skewed key — too many messages for one user. Repartitioning is """
 """expensive and it breaks ordering, so the key has to be chosen carefully up front. That is a """
 """decision you cannot cheaply reverse, which is worth flagging at design time.""",
])

sid = beat('Observability, security, cost', 'One metric matters more than the rest',
           '<div class="to-grid" style="top:24px">'
           '<div class="to-opt k-info" data-step="0"><div class="to-h">What I would alert on</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; <b>Consumer lag</b> &mdash; the metric for this system. It rises <i>before</i> '
           'anything else moves<br>'
           '&bull; <b>ISR size</b> &mdash; shrinking ISR means durability is quietly degrading<br>'
           '&bull; <b>Under-replicated partitions</b><br>'
           '&bull; Rebalance rate &mdash; a rise means a flapping consumer<br>'
           '&bull; Disk usage vs retention<br><br>'
           '<span style="color:#ffd483">Lag is measured in <b>messages and in time</b>. &ldquo;Ten '
           'thousand behind&rdquo; means nothing; <b>&ldquo;four minutes behind&rdquo;</b> is '
           'actionable.</span></div></div>'
           '<div class="to-opt k-shared" data-step="1"><div class="to-h">Security</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; Per-topic ACLs for read and write<br>'
           '&bull; TLS in transit; encryption at rest<br>'
           '&bull; <b>The log is immutable, so GDPR deletion is genuinely hard</b><br>'
           '&bull; Answer: <b>store a key reference, not personal data</b>, and delete from the '
           'referenced store &mdash; or use compacted topics with tombstones<br>'
           '&bull; Quotas per client so one producer cannot saturate a broker</div></div>'
           '<div class="to-opt k-ok" data-step="2"><div class="to-h">Cost</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; Dominated by <b>disk &times; retention &times; replication</b><br>'
           '&bull; Lever 1: <b>shorter retention</b> &mdash; linear saving, straight trade against '
           'replay ability<br>'
           '&bull; Lever 2: <b>compression</b> &mdash; 3&ndash;5&times; on text payloads, and it is '
           'nearly free because you batch anyway<br>'
           '&bull; Lever 3: tier old segments to object storage<br><br>'
           '<span style="color:#ffd483">Cross-AZ replication traffic is a large and frequently '
           'forgotten line on the bill.</span></div></div></div>',
           """Observability, and one metric matters more than all the others: consumer lag. It is the """
           """metric for this system, and it rises before anything else moves — brokers look healthy, """
           """producers look healthy, and lag is already climbing.""", step=0)
seg(sid, 1, """And measure lag in both messages and time. Ten thousand messages behind means nothing on its """
            """own, because it depends entirely on throughput. Four minutes behind is actionable, and it """
            """is the number a human can reason about during an incident.""")
seg(sid, 2, """Also alert on ISR size, because a shrinking in-sync set means your durability is quietly """
            """degrading while everything still appears to work. Under-replicated partitions. Rebalance """
            """rate, where a rise means a flapping consumer. And disk usage against retention.""")
seg(sid, 3, """Security has one item that is genuinely hard and specific to this design: the log is """
            """immutable, so deleting an individual person's data is difficult by construction. You """
            """cannot edit a segment. The real answers are to store a key reference rather than personal """
            """data on the log and delete from the referenced store, or to use compacted topics where a """
            """tombstone eventually removes a key. Raising this unprompted is strong, because it shows """
            """you understand that immutability has a cost as well as a benefit.""")
seg(sid, 4, """Cost is disk times retention times replication. Shorter retention is a linear saving traded """
            """directly against replay ability. Compression gives three to five times on text payloads """
            """and is nearly free because you are batching anyway. Tiering old segments to object storage """
            """is the third lever. And cross-availability-zone replication traffic is a large and """
            """frequently forgotten line on the bill — worth naming, because it surprises people.""")

sid = cards('Staff-level follow-ups', [
 (0, '&ldquo;How do you add partitions to a live topic?&rdquo;',
  'You can add them &mdash; but existing keys now hash differently, so <b>ordering for a key is broken across the change</b>. Either over-provision partitions up front, or accept a migration. <b>This is the question that catches people.</b>', 'deny'),
 (0, '&ldquo;A consumer group is hours behind.&rdquo;',
  'First: is it slow processing or too few consumers? Consumers are capped by partitions, so if it is already at the partition count, adding consumers does <b>nothing</b>. Then: process in parallel within a partition, or accept lag and prioritise recent data.', 'ok'),
 (1, '&ldquo;Ten times the throughput.&rdquo;',
  'Add brokers and partitions. It scales linearly because partitions are independent. The limits you hit first are <b>partition count per broker</b> and replication network bandwidth &mdash; not CPU.', 'ok'),
 (1, '&ldquo;Guarantee no message is ever lost.&rdquo;',
  'acks=all, min.insync.replicas=2, disable unclean leader election. <b>Name that last one</b> &mdash; unclean election trades data for availability, and most people leave the default without knowing.', 'ok'),
 (2, '&ldquo;Multi-region.&rdquo;',
  'Do <b>not</b> stretch a cluster across regions &mdash; replication is synchronous within the ISR and 70 ms RTT destroys write latency. Run a cluster per region and <b>mirror asynchronously</b>, accepting eventual consistency between them.', 'ok'),
 (2, '&ldquo;Why not just use a database table as a queue?&rdquo;',
  'Legitimate at low volume, and I would say so. It breaks down on: polling cost, lock contention on the claim, no replay, and no independent consumers. <b>Below a few thousand messages a second, the table is the better engineering choice.</b>', 'shared'),
], cols=2)
seg(sid, 0, """Staff-level follow-ups. How do you add partitions to a live topic? You can add them, but """
            """existing keys now hash to different partitions, so ordering for a key is broken across the """
            """change. Either over-provision partitions up front or accept a migration. This is the """
            """question that catches people, because adding capacity sounds harmless and quietly violates """
            """the guarantee your consumers depend on.""")
seg(sid, 1, """A consumer group hours behind: first diagnose whether it is slow processing or too few """
            """consumers. And remember consumers are capped by partitions — so if the group is already at """
            """the partition count, adding consumers does literally nothing, and people do this for hours """
            """before realising. Then either parallelise within a partition or accept lag and prioritise """
            """recent data.""")
seg(sid, 2, """Ten times the throughput: add brokers and partitions, which scales linearly because """
            """partitions are independent. The limits you hit first are partition count per broker and """
            """replication network bandwidth, not CPU.""")
seg(sid, 3, """Guarantee no message is ever lost: acks equals all, minimum in-sync replicas of two, and """
            """disable unclean leader election. Name that third one specifically — unclean leader """
            """election lets an out-of-sync replica become leader, which trades your data for """
            """availability, and most people run the default without knowing which way it is set.""")
seg(sid, 4, """Multi-region: do not stretch one cluster across regions, because replication within the """
            """in-sync set is synchronous and a seventy millisecond round trip destroys your write """
            """latency. Run a cluster per region and mirror asynchronously, accepting eventual """
            """consistency between regions.""")
seg(sid, 5, """And my favourite: why not just use a database table as a queue? That is legitimate at low """
            """volume and I would say so plainly. It breaks down on polling cost, lock contention when """
            """claiming rows, no replay, and no independent consumers. But below a few thousand messages """
            """a second, the table genuinely is the better engineering choice — and being willing to say """
            """that in an interview about building a message queue is a strong signal of judgement rather """
            """than enthusiasm.""")

followups(
 ['Partitioning and ordering &mdash; <b>reported</b>',
  'Replication and in-sync replicas &mdash; <b>reported</b>',
  'Consumer groups &mdash; <b>reported</b>',
  'Exactly-once semantics &mdash; <b>reported</b>'],
 ['"What does acks=all actually wait for?"',
  '"What happens when you add partitions?"',
  '"Why is the log fast?" &mdash; sequential I/O, page cache, zero-copy, batching',
  '"A consumer group is lagging" &mdash; and why adding consumers may not help',
  '"Would you use this at all, at my scale?"'],
 """All four reported follow-ups are ones we have covered directly: partitioning and ordering, """
 """replication and in-sync replicas, consumer groups, and exactly-once semantics. Given this question """
 """came from a Staff loop, I would rehearse all four until they are fluent.""",
 """And these are the ones I would expect on top, because they probe whether you understand the """
 """mechanism. What acks equals all actually waits for. What happens when you add partitions. Why the """
 """log is fast. Why adding consumers may not help a lagging group. And whether you would use this at """
 """all at a given scale — where the right answer is sometimes no.""")

say('What I should say — the sentences that carry this design', [
 'First, a framing: I am designing a log, not a queue. Messages are not deleted on consumption, each consumer tracks its own offset, and everything else follows from that.',
 'I do not need global ordering — I need ordering per key. So I will partition by the key that must be ordered, and get parallelism equal to the partition count.',
 'Partition count is also the cap on consumer parallelism, so I would over-provision partitions now, because adding them later breaks ordering for existing keys.',
 'For durability I would use acks=all with min.insync.replicas=2 — otherwise, if the in-sync set shrinks to one, acks=all silently becomes acks=1.',
 'It is fast because of what it does not do: no per-message state, no random writes, no copying into user space — sequential appends, page cache, and sendfile.',
 'Committing the offset after processing gives at-least-once; before gives at-most-once. That single line in the consumer loop is the delivery guarantee.',
 'Exactly-once is real inside this system, via the idempotent producer and transactions — but it stops at the boundary. Writing to an external database puts you back on at-least-once plus idempotency.',
 'The metric I would watch is consumer lag, measured in time rather than messages, because it moves before anything else looks wrong.',
], [
 """Eight sentences. The first is the framing that should open your answer, and it signals immediately """
 """that you know what you are building.""",
 """The second resolves the ordering-versus-throughput tension by scoping the requirement rather than """
 """satisfying it globally.""",
 """The third is foresight — a decision made now because it is expensive later — which is precisely the """
 """extensibility thinking the official pack asks for.""",
 """The fourth is the durability configuration with the trap attached. The fifth explains performance in """
 """terms of omission, and names sendfile.""",
 """The sixth locates the delivery guarantee in the consumer's code rather than in configuration, which """
 """is the precise answer.""",
 """The seventh draws the boundary around exactly-once honestly. And the eighth names the one metric """
 """that matters, with the detail about measuring in time. Close on that — it is an operator's """
 """sentence, and this is an operator's question.""",
])

cheatsheet('Message queue &mdash; the revision card', [
 ('Problem', 'Durable, ordered, replayable messaging at 1M msg/s'),
 ('Evidence', '2 reports &middot; Staff, Jun 2025 &middot; <b>LinkedIn wrote Kafka</b>'),
 ('Scale', '1 GB/s in &middot; 3 GB/s with replication &middot; 600 TB at 7 days'),
 ('Sizing driver', '<b>Storage</b>, not throughput'),
 ('The core idea', '<b>A log, not a queue</b> &mdash; nothing is deleted on consumption'),
 ('Ordering', '<b>Per partition only.</b> Choose the key to match the requirement'),
 ('Partition count', 'Caps consumer parallelism. <b>Over-provision</b>'),
 ('Adding partitions', 'Breaks ordering for existing keys &mdash; expensive'),
 ('Durability', '<b>acks=all + min.insync.replicas=2</b>'),
 ('The acks trap', 'ISR shrinks to 1 &rarr; acks=all silently becomes acks=1'),
 ('Why it is fast', 'Sequential I/O, page cache, <b>zero-copy sendfile</b>, batching'),
 ('On disk', 'Segments + sparse index. Retention drops whole segments'),
 ('Broker state', 'None per consumer &mdash; just a committed offset'),
 ('Delivery', 'Commit after = at-least-once; before = at-most-once'),
 ('Exactly-once', 'Real <i>inside</i> the system; <b>stops at the boundary</b>'),
 ('Rebalance', 'The real production problem. Sticky + incremental'),
 ('Alert on', '<b>Consumer lag in time</b>, ISR size, under-replicated partitions'),
 ('GDPR', 'Immutable log &rarr; store references, or compacted topics'),
 ('Multi-region', 'Cluster per region + async mirror. <b>Never stretch the ISR</b>'),
 ('When not to', 'Below a few thousand msg/s, <b>a database table is better</b>'),
], [
 """The revision card. Problem, evidence, scale — and the line that storage rather than throughput """
 """drives your cluster size.""",
 """The core idea, the ordering guarantee, and the two partition-count facts: it caps consumers, and """
 """changing it later is expensive.""",
 """Durability configuration with its trap, and the four reasons the log is fast.""",
 """The on-disk structure, the absence of broker-side consumer state, and where the delivery guarantee """
 """actually lives.""",
 """The boundary around exactly-once, rebalancing as the real operational problem, and what to alert """
 """on.""",
 """Then GDPR, multi-region, and — the line I would not leave out — when not to use this at all. """
 """Twenty lines, and they rebuild the design and the judgement around it.""",
])

sid = statement('Lesson 3.3', 'Understand the mechanism, not the diagram.',
                'You are designing the house speciality in front of people who may have built it. Sequential I/O, the page cache, zero-copy, the ISR — these are what separate an answer that lands from one that does not.',
                kind='ok')
seg(sid, 0, """One line to close. Understand the mechanism, not the diagram.""")
seg(sid, 1, """On this question more than any other, you are designing the house speciality in front of """
            """people who may well have built it. Boxes labelled broker and consumer will not carry you. """
            """Sequential input-output, the page cache, zero-copy, the in-sync replica set, where the """
            """delivery guarantee actually lives — those are what separate an answer that lands from one """
            """that does not. And notice that the same theme has now run through all three lessons in """
            """this chapter: search, scheduling and messaging are all won by understanding one mechanism """
            """deeply rather than many components shallowly.""")
