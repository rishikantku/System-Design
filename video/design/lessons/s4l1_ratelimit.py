# -*- coding: utf-8 -*-
"""Chapter 4, Lesson 1 — design a distributed rate limiter."""
from lib import *

lesson_header('4.1', 'Design a distributed rate limiter',
              'Token bucket &middot; distributed counters &middot; fail-open vs fail-closed',
              dict(reports='InterviewTV list, and 1 independent recent report',
                   latest='2026', level='Staff / Senior',
                   conf='MEDIUM-HIGH &mdash; corroborated',
                   sources='InterviewTV.io + research pass 3'), 16,
              """Chapter four, lesson one: the distributed rate limiter. This is the foundation lesson """
              """for the whole chapter, because the next three questions — API quotas, top-N requests, """
              """and the malicious I-P denylist — are all the same underlying problem wearing different """
              """clothes. Count something across a fleet of machines, decide on it, and get the decision """
              """everywhere before it goes stale. Learn the counter properly here and you will get three """
              """more designs almost for free.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  'Listed with the algorithms called out by name: <b>token bucket, leaky bucket, fixed window, '
  'sliding window</b>, plus multi-region and fail-open'),
 ('Research pass 3 &mdash; candidate report', '2026', 'Senior / Staff',
  '&ldquo;Design a rate limiter&rdquo; reported once, thin detail'),
], """The evidence. It is on the InterviewTV list you supplied, and notably that listing names the """
     """algorithms explicitly — token bucket, leaky bucket, fixed window, sliding window — along with """
     """multi-region and fail-open. When a question arrives with its own syllabus attached, that is a """
     """strong hint about where the interviewer expects depth.""",
 ["""It is also corroborated by one candidate report in our earlier research pass, though with thin """
  """detail. So: two sources, medium-high confidence."""],
 caveat='Two sources makes this worth preparing properly. It does not make it certain, and nothing in '
        'this course claims a question will be asked.',
 narration_caveat="""Two sources makes this worth preparing properly. It does not make it certain. """
                  """Nothing in this course claims any question will be asked — we prepare on evidence, """
                  """not on promises.""")

sid = beat('Why this is interesting', 'Everyone can draw it. Almost nobody gets the hard part right.',
           '<div style="font-size:29px;line-height:1.75">'
           'A rate limiter is the most-drawn diagram in system design. Counter in Redis, check it, done.'
           '<br><br>That diagram is correct and it is not the question.<br><br>'
           'The question is the three things underneath it:<br><br>'
           '<b>1. The counter is shared state on the hot path.</b> Every single request now depends on a '
           'network call to one place.<br>'
           '<b>2. What happens when that place is down?</b> Reject everything, or allow everything? '
           'Both answers are defensible and they are very different products.<br>'
           '<b>3. Accuracy costs latency.</b> An exactly-correct limit needs coordination; coordination '
           'is the thing you cannot afford.<br><br>'
           '<span style="color:#ffd483">A rate limiter is an availability problem disguised as a '
           'counting problem.</span></div>',
           """Why is this interesting? Because a rate limiter is the most-drawn diagram in system """
           """design. Counter in Redis, check it, allow or deny, done. And that diagram is correct — it """
           """is just not the question.""", step=0)
seg(sid, 1, """The question is the three things underneath it. First: you have just put shared state on """
            """the hot path of every single request. Every request now depends on a network call to one """
            """place. That is a big architectural claim and most candidates make it without noticing.""")
seg(sid, 2, """Second: what happens when that place is down? Do you reject everything, or allow """
            """everything? Both answers are defensible, and they produce very different products — one """
            """protects your backend and takes your site down with it, the other keeps the site up and """
            """removes your protection at exactly the moment you might need it most.""")
seg(sid, 3, """And third: accuracy costs latency. A limit that is exactly correct needs coordination, """
            """and coordination is precisely the thing you cannot afford on every request. So the real """
            """framing is this — a rate limiter is an availability problem disguised as a counting """
            """problem. Hold onto that sentence; it is the one that makes the rest of the lesson make """
            """sense.""")

think('Redis holds your counters and Redis has just become unreachable. Ten thousand requests a second '
      'are arriving right now. Do you allow them or reject them — and does your answer change if this '
      'is the login endpoint rather than the search endpoint?',
      25,
      """Pause here. Redis holds your counters, and Redis has just become unreachable. Ten thousand """
      """requests a second are arriving right now. Do you allow them or reject them? And does your """
      """answer change if this is the login endpoint rather than the search endpoint? Say it out loud.""",
      """Keep your answer. If you said &ldquo;it depends on what the limit is protecting&rdquo;, you are """
      """already thinking about this correctly, and we will come back to it near the end.""")

clarify('What I would clarify first', [
 ('What are we protecting &mdash; our capacity, or the tenant from themselves?',
  'Capacity protection can be <b>approximate</b>. A billing quota cannot. This single answer decides '
  'how much accuracy you are obliged to buy.'),
 ('What is the limit keyed on &mdash; user, API key, IP, endpoint, or a tuple?',
  'Decides the <b>cardinality</b> of the counter space, which decides whether it fits in memory and '
  'whether one key can go hot.'),
 ('Is the window fixed or rolling?',
  '&ldquo;100 per minute&rdquo; and &ldquo;100 in any 60 seconds&rdquo; are different systems. Fixed '
  'is a single integer; rolling needs <b>per-request timestamps or a sketch</b>.'),
 ('What is the latency budget for the check itself?',
  'Under 1 ms means <b>local only</b>. 5&ndash;10 ms allows a network hop to a shared store. This is '
  'the number that picks the architecture.'),
 ('What is the acceptable error &mdash; can we let through 110 when the limit is 100?',
  'If yes, everything gets easier and cheaper. <b>Ask for the tolerance explicitly</b>; interviewers '
  'usually grant it and candidates rarely ask.'),
 ('One region or several?',
  'A global limit across regions needs cross-region coordination, which costs 100&nbsp;ms+. Usually '
  'the right answer is <b>per-region limits that sum to the global one</b>.'),
], [
 """What are we protecting — our own capacity, or the tenant from themselves? If it is capacity """
 """protection, the count can be approximate; nobody is harmed if we allow a hundred and five requests """
 """against a limit of a hundred. If it is a billing quota, that is a different obligation entirely. """
 """This one answer decides how much accuracy you are required to buy, so ask it first.""",
 """What is the limit keyed on — user, A-P-I key, I-P address, endpoint, or some tuple of those? That """
 """decides the cardinality of your counter space, which in turn decides whether it fits in memory, and """
 """whether any single key can get hot.""",
 """Is the window fixed or rolling? A hundred per minute and a hundred in any sixty seconds are """
 """genuinely different systems. Fixed is one integer per key. Rolling needs per-request timestamps or """
 """a sketch, and costs meaningfully more memory.""",
 """What is the latency budget for the check itself? Under a millisecond means the decision has to be """
 """local, full stop. Five to ten milliseconds lets you make a network call to a shared store. This is """
 """the number that actually picks your architecture, so get it early.""",
 """What error is acceptable — can we let through a hundred and ten when the limit is a hundred? If """
 """yes, everything downstream gets cheaper. Interviewers usually grant a tolerance, and candidates """
 """almost never think to ask for one.""",
 """And one region or several? A truly global limit across regions needs cross-region coordination, """
 """which costs a hundred milliseconds or more. The usual right answer is per-region limits that sum """
 """to the global one — and saying that unprompted is a strong signal.""",
])

capacity('Capacity — and which number actually decides', [
 ('100M DAU &times; 50 API calls / day', '5B requests / day &divide; 86,400',
  '&asymp; 58,000 req / s', 'Every one needs a limit check. <b>The check is now a tier of your stack</b>'),
 ('Peak 4&times;', '58,000 &times; 4', '&asymp; 230,000 checks / s',
  'A single Redis node does ~100k ops/s. <b>One node is not enough</b> &mdash; shard or go local'),
 ('Counter key space: 100M users &times; 20 endpoints', '2B keys, but only actives are live',
  '&asymp; 5&ndash;10M hot keys', 'Fits in RAM comfortably. <b>Memory is not the constraint</b>'),
 ('Fixed window: 1 integer + TTL per key', '10M &times; ~80 B', '&asymp; 800 MB',
  'One Redis node holds it. Cheap'),
 ('Sliding log: 100 timestamps per key', '10M &times; 100 &times; 8 B', '&asymp; 8 GB',
  '<b>10&times; the memory for exactness.</b> This is the accuracy bill, made concrete'),
 ('Latency budget for the check', 'p99 target 10 ms, Redis RTT ~1&ndash;2 ms',
  '<b>Affordable &mdash; once</b>', 'One hop per request. <b>Not two.</b> Rules out chained lookups'),
], [
 """Let us do the numbers, and I want you to watch which one actually decides something. A hundred """
 """million daily actives at fifty A-P-I calls each is five billion requests a day, about fifty-eight """
 """thousand a second. Every one of those needs a limit check, which means the check is now a tier of """
 """your stack, not a function call.""",
 """Peak at four times is roughly two hundred and thirty thousand checks a second. A single Redis node """
 """does on the order of a hundred thousand operations a second, so one node does not cover peak. You """
 """are sharding, or you are going local. That is a real fork and it arrives from arithmetic, not """
 """taste.""",
 """Key space: a hundred million users times twenty endpoints is two billion possible keys, but only """
 """active ones exist at any moment — call it five to ten million. That fits in memory easily, so I """
 """will say out loud that memory is not the constraint here. Naming what is <i>not</i> a problem is """
 """worth marks.""",
 """With a fixed window you store one integer and a T-T-L per key. Ten million keys at eighty bytes is """
 """about eight hundred megabytes. One node holds that. Cheap.""",
 """With a sliding log you store a timestamp per request — say a hundred per key — and now you are at """
 """eight gigabytes. That is ten times the memory, and it buys you exactness. I like putting it that """
 """way because it makes the accuracy trade concrete rather than philosophical: exactness costs you an """
 """order of magnitude of RAM.""",
 """And the budget. A ten millisecond p ninety-nine target against a one to two millisecond Redis round """
 """trip means you can afford one hop. One. Not two. That single line rules out any design where the """
 """limiter looks something up and then looks something else up.""",
])

# ---------------------------------------------------------------- architecture
A = Arch('Rate limiter &mdash; built in three levels', kicker='Architecture', height=780)

A.box('cl',   60, 300, 165, 90, 'Clients', '230k req/s peak', kind='neutral', step=0, focus=0, small=True)
A.box('gw',  290, 290, 215, 110, 'API gateway', 'limiter runs HERE', kind='ok', step=0, focus=[0, 1, 2])
A.box('svc', 1430, 300, 190, 90, 'Backend service', 'the thing we protect', kind='dp', step=0, focus=0, small=True)
A.arrow('cl', 'gw', step=0, focus=0)
A.arrow('gw', 'svc', step=0, label='allowed', focus=0)

A.box('loc',  570, 160, 230, 95, 'Local bucket', 'in-process, 0 ms', kind='ok', step=1, focus=[1, 3])
A.arrow('gw', 'loc', step=1, focus=1, dashed=True)

A.box('red',  570, 420, 230, 100, 'Redis shard', 'shared counter', kind='info', step=2, focus=[2, 3])
A.box('red2', 570, 545, 230, 100, 'Redis shard', 'keyed by limit-key', kind='info', step=2, focus=2)
A.arrow('gw', 'red', step=2, focus=2)

A.box('sync', 880, 420, 230, 100, 'Async reconcile', 'local &harr; global', kind='shared', step=3, focus=3, small=True)
A.arrow('loc', 'sync', step=3, focus=3, dashed=True)
A.arrow('sync', 'red', step=3, focus=3, dashed=True)

A.box('cfg', 1400, 150, 250, 100, 'Config service', 'limits per key/tier', kind='shared', step=4, focus=4, small=True)
A.arrow('cfg', 'gw', step=4, focus=4, dashed=True)

A.note(840, 170, 'Level 1 answers ~99% of traffic without leaving the process.', step=1, kind='info', w=430)
A.note(840, 565, 'Level 2 is consulted only when local state is uncertain.', step=2, kind='info', w=430)
A.note(840, 665, 'Level 3: reconcile asynchronously. Never read-through on the hot path.', step=3, kind='info', w=430)

A.narrate(0, """Let me build this in three levels rather than drawing the final thing, because the """
             """levels are the argument. Level zero: clients hit an A-P-I gateway, the gateway calls the """
             """backend. The limiter lives in the gateway — before the expensive thing, which is the """
             """whole point of having one.""",
          A.flow([(225, 345), (290, 345), (1430, 345)]))
A.narrate(1, """Level one: a token bucket held in the gateway process itself. In-process, zero network, """
             """zero milliseconds. If each gateway node owns a slice of the allowance, it can answer """
             """most requests without talking to anyone. Start here, and say why: the cheapest correct """
             """answer is the one that never leaves the process.""")
A.narrate(2, """Level two: a shared counter in Redis, sharded by the limit key, for the cases where local """
             """state is not enough — a user hopping between gateway nodes, or a limit tight enough that """
             """per-node slices are too coarse. Note the arrow direction: the gateway consults Redis, """
             """Redis never pushes.""",
          A.flow([(505, 345), (570, 470)]))
A.narrate(3, """Level three, and this is the part that separates answers. Rather than reading Redis on """
             """every request, each node keeps its local bucket and asynchronously reconciles its """
             """consumption with the global counter — every couple of hundred milliseconds, say. You """
             """trade a small, bounded overshoot for taking Redis off the hot path entirely. That is the """
             """design I would actually argue for.""",
          A.flow([(800, 470), (880, 470), (1110, 470)]))
A.narrate(4, """And a config service that pushes limits — per key, per tier, per endpoint — to the """
             """gateways. Worth drawing because the first real operational request you will get is """
             """&ldquo;raise this customer's limit right now&rdquo;, and if that needs a deploy, you """
             """have built the wrong thing.""")
A.build()

sid = beat('Deep dive 1', 'Four algorithms, and the one sentence that picks between them',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Fixed window</b> &mdash; one integer per key per minute. Cheapest. <span style="color:#ff9a9a">'
           'Allows a 2&times; burst across the boundary</span>: 100 at 10:00:59 and 100 at 10:01:00.<br><br>'
           '<b>Sliding log</b> &mdash; keep every timestamp. Exact. <span style="color:#ff9a9a">'
           '10&times; the memory</span>, and unbounded per key.<br><br>'
           '<b>Sliding window counter</b> &mdash; weight the previous window by how far into the '
           'current one you are. <span style="color:#a8e6a3">~1% error, 2 integers per key.</span> '
           'The usual production answer.<br><br>'
           '<b>Token bucket</b> &mdash; tokens refill at a rate, requests spend them. '
           '<span style="color:#a8e6a3">Allows a deliberate burst, then enforces the average.</span> '
           'Two numbers per key: token count and last-refill time.<br><br>'
           '<span style="color:#ffd483">Picking sentence: do you want to <i>permit</i> bursts '
           '(token bucket) or <i>prevent</i> them (sliding window)?</span></div>',
           """Deep dive one: the algorithms. There are four worth knowing and I want to give you the one """
           """sentence that picks between them, because listing four algorithms is a senior answer and """
           """choosing one with a reason is a staff answer.""", step=0)
seg(sid, 1, """Fixed window is one integer per key per minute. Cheapest possible. Its flaw is real and """
            """you should name it before the interviewer does: it allows a double burst across the """
            """boundary. A hundred requests at ten-oh-oh fifty-nine and another hundred at ten-oh-one """
            """zero-zero is two hundred requests in one second, both windows perfectly legal.""")
seg(sid, 2, """Sliding log keeps every timestamp and is exactly correct. It costs ten times the memory """
            """and is unbounded per key, which means one abusive client can consume your RAM — the """
            """defence mechanism becomes the attack surface.""")
seg(sid, 3, """Sliding window counter is the compromise, and it is what most production systems actually """
            """run. You keep the current window's count and the previous window's count, and weight the """
            """previous one by how far into the current window you are. About one percent error, two """
            """integers per key. That is the answer I would give as a default.""")
seg(sid, 4, """Token bucket refills tokens at a fixed rate and each request spends one. Two numbers per """
            """key — token count and last refill time — and it allows a deliberate burst before """
            """enforcing the average. And there is the picking sentence: do you want to permit bursts or """
            """prevent them? A-P-I clients that batch benefit from token bucket. A login endpoint """
            """protecting against credential stuffing wants a sliding window, because a burst is exactly """
            """the thing you are trying to stop.""")

sid = beat('Deep dive 2', 'The atomic check, and why **GET then SET** is a bug',
           '<div style="font-size:28px;line-height:1.75">'
           'The naive check:<br>'
           '<code style="font-size:25px">count = GET key<br>'
           'if count &lt; limit: SET key count+1</code><br><br>'
           '<span style="color:#ff9a9a">Two requests read 99 at the same instant. Both write 100. '
           'Both are allowed. The limit is now 101.</span><br><br>'
           'At 230,000 checks/s this is not a rare race &mdash; it is constant.<br><br>'
           '<b>The fix:</b> make read-modify-write one operation.<br>'
           '&bull; <code>INCR</code> is atomic and returns the new value &mdash; check <i>after</i> '
           'incrementing<br>'
           '&bull; A <b>Lua script</b> for anything multi-step (token bucket needs refill + spend '
           'together)<br>'
           '&bull; Both run on <b>one shard</b>, so the key must hash to one place<br><br>'
           '<span style="color:#a8e6a3">STAFF-LEVEL INSIGHT: atomicity is why the partition key and the '
           'limit key must be the same thing.</span></div>',
           """Deep dive two, and this is the one candidates most often get wrong in code even when they """
           """get it right in the diagram. The naive check is: read the count, compare it to the limit, """
           """write the count plus one.""", step=0)
seg(sid, 1, """Two requests read ninety-nine at the same instant. Both decide they are under the limit. """
            """Both write a hundred. Both are allowed, and your limit of a hundred just let through a """
            """hundred and one. At two hundred and thirty thousand checks a second, that is not a rare """
            """race condition — it is the constant state of the system.""")
seg(sid, 2, """The fix is to make read-modify-write a single operation. Redis INCR is atomic and returns """
            """the new value, so you increment first and check afterwards — and if you are over, you """
            """have already consumed a token, which you either accept as slight over-counting or """
            """decrement back. For anything multi-step, like token bucket which must refill and spend """
            """together, use a Lua script, because Redis runs it atomically.""")
seg(sid, 3, """And here is the staff-level insight hiding in this. Both of those only work if the """
            """operation runs on one shard — which means the limit key and the partition key have to be """
            """the same thing. If you shard by user but limit by user-and-endpoint, your atomic """
            """operation is no longer atomic. Say that connection out loud; it links two sections of the """
            """design that most candidates treat separately.""")

tradeoff('Where the limiter lives', [
 ('Local only (per-node buckets)', 'ok',
  ['Zero network on the hot path', 'Survives Redis being down', 'Trivially scales with the fleet'],
  ['Limit is per node, not global', 'A client hitting 10 nodes gets 10&times; the allowance',
   'Useless if the fleet size changes constantly']),
 ('Shared counter, read every request', 'info',
  ['Exactly one global limit', 'Simple to reason about and explain'],
  ['A network hop on <b>every</b> request', 'Redis is now a hard dependency of every API call',
   'One shard can become the hot spot for a popular key']),
 ('Local buckets + async reconciliation', 'shared',
  ['No hop on the hot path', 'Bounded, explainable overshoot', 'Degrades to local-only if Redis dies'],
  ['Overshoot is real &mdash; must be quantified', 'More moving parts to explain and operate']),
], 'Local buckets with asynchronous reconciliation &mdash; each node holds a slice of the allowance and '
   'settles up with the global counter every ~200 ms.',
 'If the limit is a <b>billing quota</b> rather than capacity protection, I would switch to the shared '
 'counter and accept the hop &mdash; because then over-counting costs money and someone is owed a refund.',
 [
 """Trade-off time: where does the limiter actually live? Local-only per-node buckets give you zero """
 """network on the hot path and survive Redis dying, but the limit becomes per node — so a client that """
 """load-balances across ten nodes gets ten times its allowance. That is not a rounding error, that is """
 """a broken limit.""",
 """A shared counter read on every request gives you exactly one global limit and is very easy to """
 """explain, and the cost is that Redis is now a hard dependency of every single A-P-I call you serve. """
 """You have taken a system that was up and made it depend on a system that might not be.""",
 """Local buckets with asynchronous reconciliation is the middle path: each node holds a slice of the """
 """allowance and settles up with the global counter every couple of hundred milliseconds. No hop on """
 """the hot path, bounded overshoot, and it degrades gracefully to local-only if Redis disappears.""",
 """That is what I would choose, and I would quantify the overshoot rather than hand-waving it: with N """
 """nodes and a T millisecond sync interval, worst case you overshoot by roughly N times the per-node """
 """slice. Put a number on it and the interviewer can judge whether it is acceptable.""",
 """And here is what would flip my decision. If the limit is a billing quota rather than capacity """
 """protection, I switch to the shared counter and accept the hop — because now over-counting costs """
 """real money and somebody is owed a refund. The architecture follows the consequence of being wrong, """
 """not the other way round.""",
])

failures('What happens when each piece dies', [
 ('Redis shard for a key is unreachable', 'Nothing &mdash; requests still served',
  '<b>Fail open.</b> Fall back to the local bucket, which is stale but bounded. Alarm loudly &mdash; '
  'protection is degraded and someone must know'),
 ('Redis is down <i>and</i> the endpoint is auth/login', 'Some legitimate logins rejected',
  '<b>Fail closed here.</b> The limit is the security control; allowing unlimited login attempts is '
  'worse than rejecting some real users'),
 ('A gateway node restarts', 'Nothing',
  'Its local bucket is lost, so that node briefly allows a full slice again. Bounded by 1 node&rsquo;s '
  'share &mdash; acceptable, and worth saying you noticed'),
 ('One key goes hot (a scraper, or a popular tenant)', 'That tenant gets limited; others unaffected',
  'The <b>shard</b> holding it gets hot, which is the real risk. Split the key into N sub-counters '
  'and sum &mdash; the standard hot-key fix'),
 ('Clock skew between gateway nodes', 'Windows drift slightly',
  'Fixed windows are computed from <code>floor(now / window)</code>, so skew shifts boundaries. Use a '
  'monotonic source and keep windows &ge; seconds, not milliseconds'),
 ('Config push fails &mdash; nodes have different limits', 'Inconsistent enforcement',
  'Version the config, have nodes report the version they are running, and <b>alert on divergence</b>. '
  'Never let a node run limits of unknown age'),
], [
 """Failure engineering, and this is where the lesson's opening claim gets paid off. Redis shard """
 """unreachable: for capacity protection I fail open. Fall back to the local bucket, which is stale but """
 """bounded, and alarm loudly — because protection is degraded and somebody needs to know that even """
 """though nothing is visibly broken.""",
 """But if Redis is down and the endpoint is login, I fail closed. Here the limit is a security control """
 """rather than a capacity control, and allowing unlimited credential stuffing is worse than rejecting """
 """some genuine users for a few minutes. Same system, opposite decision, and the reason is what the """
 """limit is for. That is the answer to the question I asked you to pause on earlier.""",
 """A gateway node restarts and loses its local bucket, so it briefly allows a full slice again. That """
 """is bounded by one node's share of the allowance, which is acceptable — but say you noticed it, """
 """because an interviewer who spots it before you do will wonder what else you missed.""",
 """One key goes hot — a scraper, or simply a very large customer. The tenant gets limited correctly, """
 """which is the system working. The real risk is that the Redis shard holding that key gets hot. The """
 """standard fix is to split the key into N sub-counters, write to a random one, and sum on read. You """
 """trade a slightly fuzzier count for spreading the load.""",
 """Clock skew. Fixed windows are computed as floor of now divided by window size, so skew between """
 """nodes shifts boundaries and two nodes can disagree about which minute it is. Use a monotonic time """
 """source and keep windows at second granularity rather than milliseconds, where skew would """
 """dominate.""",
 """And config push failure, which is the one nobody mentions. If limits are pushed and a push fails, """
 """different nodes enforce different limits and your system is quietly inconsistent. Version the """
 """config, have every node report the version it is running, and alert on divergence. Never let a node """
 """run limits of unknown age.""",
])

say('What I should actually say in the room', [
 'Before I design this &mdash; is the limit protecting our capacity, or is it a quota someone is billed '
 'against? That changes how much accuracy I have to buy.',
 'Can I let through 110 against a limit of 100? If you can give me a tolerance, I can make this much '
 'cheaper and much more available.',
 'I will put the limiter at the gateway, before the expensive work, and I will start with a token '
 'bucket held in the gateway process itself.',
 'I do not want Redis on the hot path of every request, so each node holds a slice of the allowance and '
 'reconciles asynchronously. Worst-case overshoot is N nodes times the slice &mdash; I can put a number '
 'on that.',
 'The check has to be atomic. GET then SET is a race at this volume, so INCR, or a Lua script for '
 'token bucket.',
 'If Redis dies I fail open for capacity limits and fail closed for auth limits &mdash; because in one '
 'case the limit protects the backend and in the other it <i>is</i> the security control.',
 'For multi-region I would not try to make the limit globally exact. Per-region limits summing to the '
 'global one, and I would say plainly that the seam is deliberate.',
], [
 """Here are the sentences I would actually say, in order. Start by asking what the limit is for, """
 """because it decides the accuracy budget. Then ask for a tolerance explicitly — interviewers """
 """generally grant one and it makes the whole design cheaper.""",
 """Then place it: at the gateway, before the expensive work, starting with an in-process token """
 """bucket. Then state the thing you are refusing to do — Redis on the hot path — and give the """
 """quantified overshoot that buys you.""",
 """Then atomicity, in one line, because it shows you have written this rather than only drawn it. """
 """Then the fail-open versus fail-closed split, with the reason attached. And finally multi-region, """
 """where the strong answer is to refuse global exactness and say the seam is deliberate rather than """
 """accidental.""",
])

followups([
 'Token bucket vs leaky bucket vs fixed vs sliding window &mdash; which and why?',
 'How do you make the counter atomic across a distributed store?',
 'Local limits vs global limits?',
 'What do you do about hot keys?',
 'Multi-region: how do you keep one global limit?',
 'Fail-open or fail-closed?',
 'How accurate does it have to be?',
], [
 'Traffic grows 10&times; overnight &mdash; what breaks first?',
 'A customer says they were limited unfairly. How do you prove what happened?',
 'How would you roll out a limit change safely to a fleet of 10,000 gateways?',
 'What does this cost to run, and what is the cheapest thing you could delete?',
 'Who owns the limits &mdash; your team, or each API owner?',
],
 """The reported follow-ups are essentially the syllabus the question arrived with: the four """
 """algorithms and why, atomicity across a distributed store, local versus global, hot keys, """
 """multi-region, fail-open versus fail-closed, and how accurate it has to be. We have covered every """
 """one of those in this lesson, which is the point — the follow-ups were the lesson plan.""",
 """The staff-level follow-ups are the ones that come from operating this rather than building it. """
 """What breaks first at ten times traffic. How do you prove to an angry customer what actually """
 """happened — which is an observability and audit question hiding inside a support question. How do """
 """you roll a limit change to ten thousand gateways safely. What does it cost. And the one that """
 """most reveals seniority: who owns the limits? If every A-P-I team sets their own, you have a """
 """configuration sprawl problem in eighteen months. If one team owns them all, that team becomes a """
 """bottleneck for every launch. There is no clean answer, and having an opinion is the signal.""")

cheatsheet('Rate limiter &mdash; the one-page card', [
 ('Requirements', 'Limit requests per key per window; protect capacity; degrade gracefully'),
 ('Scale', '~58k checks/s average, ~230k peak; 5&ndash;10M live keys'),
 ('Core architecture', 'Gateway &rarr; local token bucket &rarr; async reconcile &rarr; sharded Redis'),
 ('Data store', 'Redis, in-memory, TTL per window. No durability required &mdash; counters are '
                'disposable'),
 ('Partition key', 'The limit key itself (user / API-key / tuple) &mdash; so the atomic op stays on '
                   'one shard'),
 ('Cache', 'The local bucket <i>is</i> the cache. TTL = window length'),
 ('Queue', 'None on the hot path. Async reconciliation only'),
 ('Consistency', 'Deliberately eventual. Bounded overshoot = N nodes &times; slice'),
 ('Failure handling', 'Fail <b>open</b> for capacity limits, <b>closed</b> for auth limits'),
 ('Key deep dives', 'Algorithm choice &middot; atomicity &middot; hot keys &middot; multi-region'),
 ('Biggest trade-off', 'Accuracy vs availability. Exactness needs coordination; coordination is what '
                       'you cannot afford per request'),
], [
 """The revision card. Requirements, scale, and the core architecture in one line: gateway, local token """
 """bucket, async reconciliation, sharded Redis.""",
 """Store is Redis with a T-T-L per window, and note that durability is not required — counters are """
 """disposable, and saying so tells the interviewer you know what you are not paying for. Partition by """
 """the limit key itself so the atomic operation stays on one shard. The local bucket is the cache. No """
 """queue on the hot path.""",
 """Consistency is deliberately eventual with a bounded overshoot you can compute. Failure handling """
 """splits on what the limit protects. And the biggest trade-off, which is the sentence to leave the """
 """room with: accuracy versus availability. Exactness needs coordination, and coordination is exactly """
 """what you cannot afford on every request.""",
])

say('The 60-second answer', [
 'A rate limiter is an availability problem disguised as a counting problem, so I will start by asking '
 'what the limit protects &mdash; capacity or billing &mdash; because that sets my accuracy budget.',
 'I put the limiter in the API gateway, ahead of the expensive work. Each gateway node holds a token '
 'bucket in process and owns a slice of the allowance, so the common case costs zero network.',
 'Nodes reconcile their consumption with a sharded Redis counter asynchronously, every couple of '
 'hundred milliseconds. That keeps Redis off the hot path and gives a bounded overshoot of roughly N '
 'nodes times the slice.',
 'The check must be atomic &mdash; INCR, or a Lua script for token bucket &mdash; and the limit key '
 'must be the partition key so that stays on one shard.',
 'At about 230,000 checks a second at peak, one Redis node is not enough, so counters shard by limit '
 'key, and hot keys split into sub-counters that I sum.',
 'If Redis is unavailable I fail open for capacity limits and closed for auth limits, and I alarm '
 'either way because protection is degraded even when nothing looks broken.',
], [
 """And here is the sixty-second answer — the thing you say before anyone starts drilling. Notice it """
 """leads with the framing, not the components, and that every claim has a number or a reason attached """
 """to it.""",
 """Read it, then say it out loud once from memory. If you can deliver those six sentences confidently """
 """in ninety seconds, you have bought yourself the rest of the interview to go deep on whatever the """
 """interviewer actually cares about — and that is the real purpose of having a prepared opening.""",
], kicker='60-second interview answer')
