# -*- coding: utf-8 -*-
"""Chapter 4, Lesson 2 — the LinkedIn API quota system."""
from lib import *

lesson_header('4.2', 'Design the LinkedIn API quota system',
              'Per-tenant counters &middot; atomicity &middot; daily reset &middot; multi-region',
              dict(reports='InterviewTV list only', latest='2026', level='Staff',
                   conf='MEDIUM &mdash; single source, but shares machinery with 4.1',
                   sources='InterviewTV.io'), 16,
              """Chapter four, lesson two: the LinkedIn A-P-I quota system. Daily quotas per company and """
              """per user on the public A-P-Is. Now — you have just built a rate limiter, and your """
              """instinct will be that this is the same thing with a longer window. That instinct is """
              """half right, and the half that is wrong is the whole lesson. A quota is a contractual """
              """promise; a rate limit is a defensive measure. Different obligation, different design.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  'Quota enforcement <b>and usage collection</b>, per company and per user. Deep dives named: '
  'distributed counters, atomicity, partitioning, daily reset, idempotency, multi-region, reporting'),
 ('Related &mdash; lesson 4.1', '2026', 'Staff / Senior',
  'The rate limiter shares the counter machinery. <b>Watch 4.1 first</b>'),
], """The evidence is a single source — the InterviewTV list — so medium confidence, and I will say """
     """that plainly. But look at what the listing names as deep dives: distributed counters, """
     """atomicity, partitioning, daily reset, idempotency, multi-region and reporting.""",
 ["""Note that reporting and usage collection are in there alongside enforcement. That is the tell """
  """that this is not just a rate limiter with a longer window — somebody has to be able to see what """
  """they used, and probably be billed for it."""],
 caveat='Single source. The machinery is shared with 4.1, which is corroborated, so the preparation '
        'transfers even if this exact framing does not appear.',
 narration_caveat="""Single source, so treat the exact framing as uncertain. The machinery is shared """
                  """with the rate limiter, which is corroborated — so the preparation transfers even """
                  """if this precise question never comes up.""")

sid = beat('Why this is interesting', 'Same counter. Completely different obligation.',
           '<div style="font-size:29px;line-height:1.75">'
           '<b>Rate limit:</b> &ldquo;I am protecting myself.&rdquo; Letting 110 through against a '
           'limit of 100 costs nothing. <span style="color:#a8e6a3">Approximate is fine.</span><br><br>'
           '<b>Quota:</b> &ldquo;I sold you 10,000 calls a day.&rdquo; Letting 11,000 through is '
           'revenue I did not collect. Blocking at 9,000 is a customer escalation and possibly a breach '
           'of contract. <span style="color:#ff9a9a">Approximate is a business problem.</span><br><br>'
           'Three consequences fall out of that one difference:<br><br>'
           '&bull; The count must be <b>durable</b>, not disposable &mdash; you have to be able to show '
           'someone what they used<br>'
           '&bull; Retries must not double-count &mdash; <b>idempotency</b> becomes mandatory<br>'
           '&bull; &ldquo;Daily&rdquo; needs a <b>definition</b>: whose midnight?<br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: the architecture follows the cost of being '
           'wrong, not the shape of the request.</span></div>',
           """Why is this interesting? Because the counter is the same and the obligation is not. With a """
           """rate limit I am protecting myself, so letting a hundred and ten through against a limit of """
           """a hundred costs nothing and approximate is fine.""", step=0)
seg(sid, 1, """With a quota, I sold you ten thousand calls a day. Letting eleven thousand through is """
            """revenue I did not collect. Blocking you at nine thousand is a customer escalation and """
            """possibly a contract breach. Approximate is now a business problem rather than an """
            """engineering nicety.""")
seg(sid, 2, """Three consequences fall out of that single difference. The count has to be durable rather """
            """than disposable, because somebody will ask what they used and you must be able to answer. """
            """Retries must not double-count, so idempotency stops being optional. And the word """
            """&ldquo;daily&rdquo; suddenly needs a definition — whose midnight?""")
seg(sid, 3, """That is the staff-level insight and it generalises well beyond this question: the """
            """architecture follows the cost of being wrong, not the shape of the request. Two systems """
            """that look identical on a whiteboard can need completely different guarantees, and the """
            """thing that separates them is what happens when they are wrong.""")

think('A customer is on 10,000 calls a day. Their client retries on timeout. A request times out at your '
      'gateway but actually reached the backend and was served. Does that retry consume one quota unit, '
      'or two — and how would the customer ever know?',
      25,
      """Pause. A customer has a ten thousand call daily quota. Their client retries on timeout. A """
      """request times out at your gateway but actually reached the backend and was served. Does the """
      """retry consume one quota unit or two? And how would the customer ever find out? Say it out """
      """loud.""",
      """Hold that. It is the idempotency question, and it is the single most likely deep dive on this """
      """problem.""")

clarify('What I would clarify first', [
 ('Is the quota <b>billed</b>, or just enforced?',
  'Billed means the count is a financial record: durable, auditable, reconcilable. Enforced-only means '
  'I can be far cheaper and looser.'),
 ('What does &ldquo;daily&rdquo; mean &mdash; UTC midnight, tenant local midnight, or rolling 24h?',
  'UTC gives one global reset and a <b>thundering herd at 00:00</b>. Tenant-local spreads the reset '
  'but means 24 different reset times. Rolling 24h is a different data structure entirely.'),
 ('Quota per company <i>and</i> per user &mdash; do they nest?',
  'If a user&rsquo;s calls also count against the company, one request decrements <b>two</b> counters, '
  'and now you need them to move together or not at all.'),
 ('What happens at the limit &mdash; hard block, or throttle?',
  'Hard block is a 429 and an angry customer. Soft throttle keeps them working and is often the better '
  'product. Worth asking rather than assuming.'),
 ('How quickly must usage be visible to the customer?',
  'Real-time dashboard means the counter <i>is</i> the reporting store. Hourly is enough &rarr; I can '
  'compute reporting from an event log, off the hot path.'),
 ('Is the quota global, or per region?',
  'Global exactness across regions costs a cross-region round trip per call. <b>Almost always the '
  'right answer is per-region sub-quotas.</b>'),
], [
 """Is the quota billed, or only enforced? Billed means the count is a financial record — durable, """
 """auditable, reconcilable against invoices. Enforced-only means I can be dramatically cheaper and """
 """looser. Ask this first because everything downstream hangs on it.""",
 """What does daily actually mean? U-T-C midnight gives you one global reset, and a thundering herd at """
 """midnight when every tenant's quota refills at once. Tenant-local midnight spreads that load out but """
 """means twenty-four different reset times to manage. And a rolling twenty-four hours is not a reset """
 """at all — it is a different data structure.""",
 """Quotas per company and per user — do they nest? If a user's calls also count against their """
 """company's pool, then one request decrements two counters, and now you need both to move together """
 """or neither to move. That is a transaction, and I would rather discover that in minute three than """
 """minute thirty.""",
 """What happens at the limit — hard block or throttle? A hard four-two-nine and an angry customer, or """
 """a soft throttle that keeps them working at reduced speed. The second is often the better product """
 """and candidates rarely ask.""",
 """How fast must usage be visible? If the customer wants a real-time dashboard, the counter is also """
 """the reporting store. If hourly is fine, I can compute reporting from an event log entirely off the """
 """hot path, which is much easier.""",
 """And global or per region. Global exactness costs a cross-region round trip on every call, which """
 """nobody pays. The right answer is nearly always per-region sub-quotas that sum to the contract.""",
])

capacity('Capacity', [
 ('50k partner apps &times; ~2M calls/day', '100B? no &mdash; realistically 2B calls / day',
  '&asymp; 23,000 calls / s', 'Every call decrements at least one counter'),
 ('Peak 4&times;', '23,000 &times; 4', '&asymp; 92,000 decrements / s',
  'Shardable. But each decrement must be <b>atomic</b> and <b>durable</b>'),
 ('Counters: 50k companies + 5M active users', '5.05M keys &times; 2 (company + user)',
  '&asymp; 10M counters', 'Small. Fits in memory easily &mdash; memory is not the constraint'),
 ('Usage events, if we log every call', '2B/day &times; 200 B', '&asymp; 400 GB / day',
  '<b>This is the expensive part</b>, not the counting. Sample or aggregate before storing'),
 ('Aggregated usage: per tenant per hour', '50k &times; 24 &times; ~100 B', '&asymp; 120 MB / day',
  '<b>3,000&times; smaller.</b> Reporting reads this, never the raw events'),
 ('Retention for billing disputes', '13 months of hourly aggregates', '&asymp; 50 GB',
  'Trivial. <b>Durable, cheap, and enough to settle an argument</b>'),
], [
 """Numbers. Say fifty thousand partner applications and two billion A-P-I calls a day — about """
 """twenty-three thousand a second, and every one of them decrements at least one counter.""",
 """Peak at four times is ninety-two thousand decrements a second. That shards fine, but remember each """
 """one must be atomic and, unlike the rate limiter, durable.""",
 """The counters themselves are small: fifty thousand companies plus maybe five million active users, """
 """times two for company and user counters, is around ten million keys. That fits in memory """
 """comfortably. Memory is not the constraint here and I would say so.""",
 """Here is the number that actually decides something. If I log every call as a usage event for """
 """reporting, that is two billion events a day at two hundred bytes, which is four hundred gigabytes """
 """a day. The expensive part of a quota system is not the counting — it is the receipts.""",
 """But if I aggregate to per tenant per hour, it is fifty thousand tenants times twenty-four hours, """
 """about a hundred and twenty megabytes a day. Three thousand times smaller. So reporting reads """
 """aggregates and never touches raw events.""",
 """And thirteen months of hourly aggregates for billing disputes is about fifty gigabytes total. """
 """Trivial, durable, cheap, and enough to settle an argument with a customer — which is exactly what """
 """it is for.""",
])

A = Arch('Quota &mdash; enforcement on the hot path, accounting off it', kicker='Architecture', height=790)

A.box('cl',   60, 320, 160, 90, 'Partner app', 'API key', kind='neutral', step=0, focus=0, small=True)
A.box('gw',  280, 310, 210, 110, 'API gateway', 'enforce here', kind='ok', step=0, focus=[0, 1])
A.box('svc', 1450, 320, 175, 90, 'LinkedIn API', '', kind='dp', step=0, focus=0, small=True)
A.arrow('cl', 'gw', step=0, focus=0)
A.arrow('gw', 'svc', step=0, label='allowed', focus=0)

A.box('ctr',  560, 285, 245, 110, 'Quota counters', 'Redis + AOF, persisted', kind='info', step=1, focus=[1, 2])
A.arrow('gw', 'ctr', step=1, focus=1)

A.box('log',  560, 490, 235, 100, 'Usage events', 'Kafka, async', kind='shared', step=2, focus=[2, 3], small=True)
A.arrow('gw', 'log', step=2, focus=2, dashed=True)

A.box('agg',  870, 490, 215, 100, 'Aggregator', 'per tenant/hour', kind='shared', step=3, focus=3, small=True)
A.box('wh',  1160, 490, 235, 100, 'Usage store', '13 mo, durable', kind='dp', step=3, focus=[3, 4], small=True)
A.arrow('log', 'agg', step=3, focus=3)
A.arrow('agg', 'wh', step=3, focus=3)

A.box('rep', 1160, 645, 235, 95, 'Reporting API', 'customer dashboard', kind='neutral', step=4, focus=4, small=True)
A.arrow('wh', 'rep', step=4, focus=4)

A.box('res',  1400, 150, 215, 95, 'Reset job', 'tenant-local midnight', kind='shared', step=5, focus=5, small=True)
A.arrow('res', 'ctr', step=5, focus=5, dashed=True)

A.note(90, 600, 'Enforcement needs the counter FAST and ATOMIC. Accounting needs it DURABLE and COMPLETE. Serve them with two paths, not one compromised structure.',
       step=2, kind='info', w=400)

A.narrate(0, """Let me build it. Partner app hits the gateway, gateway calls the A-P-I. Enforcement """
             """happens at the gateway, same as the rate limiter, and for the same reason: before the """
             """expensive work.""",
          A.flow([(220, 365), (280, 365), (1450, 365)]))
A.narrate(1, """The quota counters. Redis again, but note the difference from lesson 4.1 — append-only """
             """persistence turned on, because these counters are not disposable. If I lose them I """
             """cannot tell a customer what they used, and that is a conversation I never want to """
             """have.""",
          A.flow([(490, 365), (560, 340)]))
A.narrate(2, """Now the split that makes this design work. The gateway also emits a usage event to Kafka, """
             """asynchronously, off the hot path. Enforcement needs the counter to be fast and atomic. """
             """Accounting needs it durable and complete. Those are different requirements, so I serve """
             """them with different paths rather than compromising one structure to do both.""",
          A.flow([(490, 380), (560, 540)]))
A.narrate(3, """An aggregator rolls the events up to per tenant per hour and writes them to a durable """
             """usage store with thirteen months retention. Remember the arithmetic: raw events are four """
             """hundred gigabytes a day, aggregates are a hundred and twenty megabytes. The aggregation """
             """is not an optimisation, it is what makes the system affordable.""",
          A.flow([(795, 540), (870, 540), (1160, 540)]))
A.narrate(4, """The reporting A-P-I serves the customer dashboard from the aggregate store. It never """
             """touches the live counters — which means a customer refreshing their usage page cannot """
             """slow down enforcement for everyone else. Isolating the read path from the hot path is """
             """worth calling out explicitly.""")
A.narrate(5, """And the reset job, which is the piece people forget. It resets counters at each """
             """tenant's midnight. Staggered on purpose, because if all fifty thousand tenants reset at """
             """U-T-C midnight you get a stampede, and I would rather spread it than survive it.""")
A.build()

sid = beat('Deep dive 1', 'Idempotency &mdash; the retry that bills twice',
           '<div style="font-size:28px;line-height:1.72">'
           'The failure: gateway decrements the quota, calls the backend, then <b>times out</b>. The '
           'client retries. Did the first call succeed?<br><br>'
           '<span style="color:#ff9a9a">If you decrement on arrival: the retry costs a second unit. '
           'The customer is charged twice for one result.</span><br><br>'
           '<b>The fix &mdash; an idempotency key.</b><br>'
           '&bull; Client sends <code>Idempotency-Key: &lt;uuid&gt;</code> (or you derive one)<br>'
           '&bull; Gateway stores <code>key &rarr; outcome</code> with a 24h TTL<br>'
           '&bull; A repeat of a key returns the stored outcome and <b>decrements nothing</b><br><br>'
           '<b>Cost:</b> one extra lookup per request, and a key store sized at 1 day of requests.<br><br>'
           '<span style="color:#ffd483">And the honest limit: this only works if the client sends a '
           'stable key. If they generate a fresh UUID per retry, nothing can save you &mdash; so the '
           'key becomes part of your published API contract.</span></div>',
           """Deep dive one: idempotency, and this is the answer to the question I asked you to pause """
           """on. The gateway decrements the quota, calls the backend, and then times out. The client """
           """retries. Did the first call actually succeed? The gateway does not know.""", step=0)
seg(sid, 1, """If you decrement on arrival, the retry costs a second unit and the customer has been """
            """charged twice for one result. At scale that is not an edge case, it is a steady stream of """
            """small overcharges, and it is exactly the kind of thing that surfaces as a trust problem """
            """rather than a bug report.""")
seg(sid, 2, """The fix is an idempotency key. The client sends one — or you derive a stable one from the """
            """request — and the gateway stores a mapping from key to outcome with a twenty-four hour """
            """T-T-L. A repeat of a key returns the stored outcome and decrements nothing. The cost is """
            """one extra lookup per request and a key store sized at one day of traffic.""")
seg(sid, 3, """And here is the honest limit, which I would volunteer rather than wait to be caught on. """
            """This only works if the client sends a stable key across retries. If they generate a fresh """
            """U-U-I-D each time, nothing you build can save you. Which means the idempotency key is not """
            """an implementation detail — it is part of your published A-P-I contract, and somebody has """
            """to document it and make clients adopt it.""")

sid = beat('Deep dive 2', 'Nested quotas, and the two-counter problem',
           '<div style="font-size:28px;line-height:1.72">'
           'A user&rsquo;s call counts against <b>both</b> the user quota and their company&rsquo;s pool. '
           'One request, two decrements.<br><br>'
           '<span style="color:#ff9a9a">If they are on different shards, you now want a distributed '
           'transaction on the hot path. You cannot afford one.</span><br><br>'
           '<b>Option A &mdash; co-locate.</b> Hash by <code>companyId</code> so a company and all its '
           'users land on one shard. One Lua script decrements both atomically.<br>'
           '<span style="color:#a8e6a3">Atomic and cheap.</span> '
           '<span style="color:#ff9a9a">A huge company is now a hot shard.</span><br><br>'
           '<b>Option B &mdash; check user, settle company async.</b> Enforce the user quota inline; '
           'stream consumption into the company pool.<br>'
           '<span style="color:#a8e6a3">No hot shard.</span> '
           '<span style="color:#ff9a9a">A company can overshoot by up to one sync interval.</span><br><br>'
           '<span style="color:#ffd483">I would take A, and split the largest tenants across '
           'sub-counters &mdash; the same hot-key fix as 4.1.</span></div>',
           """Deep dive two: nested quotas. A user's call counts against both their own quota and their """
           """company's pool. One request, two decrements — and if those two counters live on different """
           """shards, you have just wished for a distributed transaction on the hot path. You cannot """
           """afford one.""", step=0)
seg(sid, 1, """Option A: co-locate them. Hash by company I-D so that a company and all of its users land """
            """on the same shard, then one Lua script decrements both atomically. That is genuinely """
            """cheap and genuinely atomic. The cost is that a very large customer becomes a hot shard, """
            """because all of their traffic hashes to one place.""")
seg(sid, 2, """Option B: enforce the user quota inline and settle the company pool asynchronously. No hot """
            """shard, because user keys spread naturally. The cost is that a company can overshoot its """
            """pool by up to one sync interval's worth of calls.""")
seg(sid, 3, """I would take A, and handle the hot tenant with the same fix as the rate limiter — split """
            """the largest tenants into N sub-counters and sum them. Notice that is the second time """
            """that trick has appeared in this chapter. That repetition is the point of grouping these """
            """questions together: you are not learning four systems, you are learning one toolkit four """
            """times.""")

tradeoff('Where the daily reset happens', [
 ('Reset at UTC midnight, all tenants', 'info',
  ['One job, one time, trivially simple', 'Everyone&rsquo;s day is the same &mdash; easy to explain'],
  ['<b>Stampede at 00:00 UTC</b> &mdash; every tenant refills at once',
   'Tenants in Asia get a reset in the middle of their working day']),
 ('Reset at tenant-local midnight', 'ok',
  ['Load spreads naturally across 24 hours', 'Matches what the customer means by &ldquo;a day&rdquo;'],
  ['24 reset waves to schedule and monitor', 'DST makes some days 23 or 25 hours long']),
 ('No reset &mdash; rolling 24h window', 'shared',
  ['No stampede at all', 'No &ldquo;whose midnight&rdquo; argument'],
  ['Needs per-request timestamps, not a counter', '<b>~10&times; the memory</b>',
   'Much harder for a customer to reason about their own usage']),
], 'Tenant-local midnight, with the reset implemented as a <b>lazy check on read</b> rather than a '
   'sweeping job: if the counter&rsquo;s window stamp is stale, treat it as zero.',
 'If quotas were per-second rather than per-day I would switch to a rolling window &mdash; at that '
 'granularity a hard reset boundary is gameable, and the memory cost is tiny.',
 [
 """Trade-off: where does the daily reset happen? U-T-C midnight for everyone is one job at one time """
 """and is trivially simple, and it gives you a stampede at midnight when fifty thousand tenants refill """
 """simultaneously. It also means a tenant in Asia gets their reset in the middle of their working """
 """day, which will generate support tickets.""",
 """Tenant-local midnight spreads the load across twenty-four hours naturally and matches what the """
 """customer actually means by a day. The cost is twenty-four reset waves to schedule and monitor, and """
 """daylight saving making some days twenty-three or twenty-five hours long — which sounds pedantic """
 """until it silently gives someone an extra hour of quota twice a year.""",
 """A rolling twenty-four hour window avoids the whole argument and costs you roughly ten times the """
 """memory, plus it is genuinely harder for customers to reason about their own usage. That last point """
 """matters more than engineers usually credit.""",
 """I would take tenant-local midnight, and I would implement the reset lazily rather than as a """
 """sweeping job: when I read a counter, if its window stamp is stale, I treat it as zero and stamp it """
 """fresh. No job to run, no stampede, and nothing to fail at three in the morning.""",
 """What would flip it: if quotas were per second rather than per day, I would switch to a rolling """
 """window — at that granularity a hard boundary is gameable, and the memory cost of timestamps """
 """becomes trivial.""",
])

failures('What happens when each piece dies', [
 ('Counter store unavailable', 'Calls still served',
  '<b>Fail open</b> and reconcile from the Kafka usage log afterwards. A quota is a commercial control, '
  'not a security one &mdash; taking the API down to protect revenue is the wrong trade'),
 ('Kafka unavailable', 'Nothing visible',
  'Enforcement is unaffected &mdash; it reads counters, not Kafka. <b>Reporting goes stale.</b> Buffer '
  'locally on the gateway and drain when Kafka returns'),
 ('Aggregator falls behind', 'Dashboard shows old numbers',
  'Enforcement still correct. Alert on consumer lag; this is a <b>reporting</b> incident, not an '
  'availability one &mdash; page accordingly'),
 ('Counter lost (Redis restart, no AOF replay)', 'Tenants get free quota until rebuild',
  '<b>Rebuild from the usage log.</b> This is the reason the event stream exists &mdash; the counter is '
  'a cache <i>of</i> the log, not the source of truth'),
 ('Duplicate usage events', 'Over-reported usage &rarr; wrong bill',
  'Deduplicate on <code>(idempotency key, tenant)</code> in the aggregator. At-least-once delivery '
  'makes this <b>certain</b>, not hypothetical'),
 ('Reset does not run for a tenant', 'That tenant is blocked all day',
  'Lazy reset on read makes this impossible by construction &mdash; <b>which is the best kind of '
  'failure handling: design the failure out</b>'),
], [
 """Failures. Counter store unavailable: fail open, serve the calls, and reconcile from the Kafka usage """
 """log afterwards. A quota is a commercial control, not a security one — taking your public A-P-I down """
 """to protect revenue is the wrong trade, and it is worth saying that reasoning out loud rather than """
 """just asserting fail-open.""",
 """Kafka unavailable: enforcement is completely unaffected, because it reads counters and not Kafka. """
 """Reporting goes stale. Buffer on the gateway and drain when Kafka comes back. Notice how much the """
 """earlier split is paying off here — one system being down degrades one capability instead of all of """
 """them.""",
 """Aggregator falls behind: the dashboard shows old numbers and enforcement stays correct. Alert on """
 """consumer lag, but page it as a reporting incident, not an availability one. Getting the severity """
 """right is an operational judgement interviewers notice.""",
 """Counter lost entirely — Redis restarts without replaying its append-only file. Tenants get free """
 """quota until you rebuild. And you can rebuild, from the usage log. This is the sentence I would """
 """want to say: the counter is a cache of the log, not the source of truth. That inversion is what """
 """makes the whole design recoverable.""",
 """Duplicate usage events lead to over-reported usage and a wrong bill. Deduplicate on idempotency key """
 """and tenant inside the aggregator. With at-least-once delivery, duplicates are certain rather than """
 """hypothetical, so this is required, not defensive.""",
 """And a reset that fails to run for a tenant would block them all day — except that lazy reset on """
 """read makes it impossible by construction. That is the best kind of failure handling: you did not """
 """handle the failure, you removed it.""",
])

say('What I should actually say in the room', [
 'First question: is this quota billed, or only enforced? If someone is invoiced against this number, '
 'it is a financial record and I have to design for durability and audit, not just enforcement.',
 'I will enforce at the gateway with an atomic decrement, exactly like a rate limiter &mdash; but I '
 'will turn on persistence, because unlike a rate limiter these counters are not disposable.',
 'I will emit a usage event to Kafka asynchronously and aggregate it per tenant per hour. Raw events '
 'are ~400 GB a day; the aggregates are ~120 MB. Reporting reads the aggregates and never the counters.',
 'Retries are the real risk. Without an idempotency key a timeout charges the customer twice, so the '
 'key becomes part of the published API contract &mdash; not an internal detail.',
 'Company and user quotas nest, so I co-locate them on one shard by company ID and decrement both in '
 'one Lua script. Large tenants get split into sub-counters to avoid a hot shard.',
 'Reset is lazy at tenant-local midnight &mdash; if the window stamp is stale, the counter reads as '
 'zero. No sweeping job, no stampede.',
 'If the counter store dies I fail open and rebuild from the usage log, because the counter is a cache '
 'of the log rather than the source of truth.',
], [
 """The sentences to say. Lead with billed-versus-enforced, because it is the question that sets every """
 """other decision, and asking it immediately signals that you understand the difference between this """
 """and a rate limiter.""",
 """Then the enforcement path with the one word that distinguishes it — persistence. Then the """
 """accounting split with the two numbers attached, because the arithmetic is what justifies the """
 """separate path.""",
 """Then idempotency framed as an A-P-I contract rather than a code change. Then nesting, with the """
 """co-location decision and the hot-tenant fix. Then lazy reset. And finally the recovery story, """
 """which is the sentence that ties it together: the counter is a cache of the log.""",
])

followups([
 'How do you make the distributed counter atomic?',
 'How do you partition the counters?',
 'How does the daily reset work?',
 'How do you handle idempotency?',
 'How does this work multi-region?',
 'How do customers see their usage?',
 'How do you prevent abuse of the quota system itself?',
], [
 'A customer disputes their bill for last March. Can you prove what they used?',
 'How do you change a customer&rsquo;s quota without a deploy &mdash; and audit who changed it?',
 'A partner has 100&times; the traffic of everyone else. What breaks?',
 'Would you build this, or buy an API management product? What is the line?',
 'Who owns quota policy &mdash; the API teams, or a central platform team?',
],
 """The reported follow-ups map almost one-to-one onto what we covered: atomicity, partitioning, daily """
 """reset, idempotency, multi-region, customer-visible usage, and abuse of the quota system itself. On """
 """multi-region, the answer I would give is per-region sub-quotas summing to the contract, and I would """
 """say explicitly that I am choosing not to make it globally exact because a cross-region round trip """
 """per call is unaffordable.""",
 """The staff-level follow-ups come from running this rather than building it. Can you prove what a """
 """customer used last March — that is your thirteen months of aggregates earning their keep. How do """
 """you change a quota without a deploy, and audit who changed it. What breaks when one partner has a """
 """hundred times everyone else's traffic. Would you build this or buy an A-P-I management product, """
 """which is a genuinely good question and the honest answer is that you buy it until the billing """
 """semantics are specific enough that you cannot. And who owns quota policy, which is an """
 """organisational question wearing a technical costume — and having a view on it is what staff level """
 """actually means.""")

cheatsheet('API quota &mdash; the one-page card', [
 ('Requirements', 'Daily quota per company and per user; enforce, report, and be able to prove usage'),
 ('Scale', '~23k calls/s avg, ~92k peak; ~10M counters; 400 GB/day raw usage &rarr; 120 MB aggregated'),
 ('Core architecture', 'Gateway enforces on Redis counters; usage events to Kafka; hourly aggregates '
                       'to a durable store; reporting reads aggregates'),
 ('Data store', 'Redis <b>with persistence</b> for counters; columnar store for 13 months of aggregates'),
 ('Partition key', '<code>companyId</code> &mdash; co-locates company and user counters so the nested '
                   'decrement stays atomic'),
 ('Cache', 'The counter <i>is</i> the cache; the usage log is the source of truth'),
 ('Queue', 'Kafka, off the hot path, for usage events only'),
 ('Consistency', 'Enforcement eventual and fail-open; <b>accounting must be exactly-once</b>, via '
                 'idempotency keys and dedup in the aggregator'),
 ('Failure handling', 'Fail open, reconcile from the log; lazy reset removes the reset-failure mode'),
 ('Key deep dives', 'Idempotency &middot; nested quotas &middot; reset semantics &middot; reporting split'),
 ('Biggest trade-off', 'Enforcement wants speed, accounting wants durability. <b>Serve them with two '
                       'paths rather than one compromised structure.</b>'),
], [
 """The revision card. Requirements, scale — and note the two numbers worth memorising, four hundred """
 """gigabytes of raw usage a day against a hundred and twenty megabytes aggregated.""",
 """Architecture in one line: gateway enforces on counters, usage events go to Kafka, hourly aggregates """
 """land in a durable store, reporting reads the aggregates. Partition by company I-D so the nested """
 """decrement stays atomic. Kafka is off the hot path.""",
 """Consistency splits: enforcement is eventual and fails open, accounting must be exactly-once. """
 """Failure handling reconciles from the log. And the biggest trade-off, which is the sentence to """
 """remember: enforcement wants speed, accounting wants durability, so serve them with two paths """
 """rather than one compromised structure.""",
])

say('The 60-second answer', [
 'A quota looks like a rate limiter and has a different obligation &mdash; someone is billed against '
 'this number &mdash; so I design for durability and audit, not just enforcement.',
 'Enforcement is at the gateway: an atomic decrement against a Redis counter, persistence on, '
 'partitioned by company ID so a user&rsquo;s call can decrement both their own and their '
 'company&rsquo;s counter in one atomic script.',
 'Separately and asynchronously, the gateway emits a usage event to Kafka. An aggregator rolls those up '
 'per tenant per hour into a durable store kept for thirteen months, and the customer dashboard reads '
 'that &mdash; never the live counters.',
 'Retries are the real correctness risk, so requests carry an idempotency key and a repeat returns the '
 'stored outcome without decrementing. That key is part of the published API contract.',
 'Reset is lazy at tenant-local midnight: a stale window stamp reads as zero, so there is no sweeping '
 'job and no midnight stampede.',
 'If the counters are lost I rebuild them from the usage log, because the counter is a cache of the '
 'log rather than the source of truth &mdash; and if the counter store is simply down, I fail open, '
 'since taking the public API offline to protect revenue is the wrong trade.',
], [
 """And the sixty-second answer. Notice it opens by distinguishing this from the rate limiter, which """
 """immediately tells the interviewer you have not just pattern-matched to the previous question.""",
 """Every claim carries its reason. Say it out loud once from memory — if you can land those six """
 """sentences in ninety seconds, the rest of the hour is yours to go deep wherever the interviewer """
 """wants to push.""",
], kicker='60-second interview answer')
