# -*- coding: utf-8 -*-
from engine import *

chapter(8, "Failure modes and isolation guarantees", "What fails, who it hurts, the two guarantees that must be impossible to break, and the incidents that shaped them.",
 """Chapter eight. Failure modes. This is where infra interviewers spend the most time, and where made-up experience falls apart fastest. So we'll go carefully. First, what can fail and who it affects. Then the two isolation guarantees. Then the two production incidents you caused, and exactly what each one changed.""")

D = Diagram("Blast radius: who is affected when something fails")
rows = [('A replica', 'Nobody. The shard absorbs it.', 'ok'),
        ('A shard', "One tenant's one product, until the Shard Manager replaces it.", 'dp'),
        ('An availability zone', 'Usually nobody. Replicas in two other zones; databases fail over.', 'ok'),
        ('The control plane', 'No live traffic. Onboarding, deploys and lifecycle changes wait.', 'cp'),
        ('A region', 'Every environment in that region, until it recovers or a restore completes.', 'shared'),
        ('The shared entry path', 'Potentially every tenant, commercial and isolated.', 'deny')]
for k, (a, b, kind) in enumerate(rows):
    y = 20 + k * 132
    D.box('f%d' % k, 60, y, 520, 110, a, '', kind=kind, step=k, hl=str(k))
    D.label(640, y + 30, b, kind=kind, step=k, w=1220, size='m')
    D.arrow('f%d' % k, (620, y + 55), step=k, kind=kind)
sid = D.build()
seg(sid, 0, """Start with blast radius, from smallest to largest. A replica fails. Nobody is affected. The shard absorbs it, and the tenant to shard mapping doesn't change.""")
seg(sid, 1, """A shard fails. One tenant's one product is affected, until the Shard Manager replaces it. Notice how narrow that is. One customer's Jira, not Jira.""")
seg(sid, 2, """An availability zone fails. Usually nobody notices. Every shard spreads its replicas across three zones, sized so that two zones can carry peak traffic, and databases fail over. In one real zone impairment, shards stayed up, and one tenant saw about two minutes of failed writes while their database failed over. Use that detail. Specifics like that are what make an answer sound lived.""")
seg(sid, 3, """The control plane fails. No live traffic is affected, because it's not on the request path. Onboarding, deploys and lifecycle changes wait.""")
seg(sid, 4, """A region fails. Every environment in that region is affected until the region recovers or a restore completes. That's a deliberate trade for residency, and we'll come back to it.""")
seg(sid, 5, """And the shared entry path: the Global Edge, the Router and the Tenant Context Service. Potentially every tenant, commercial and isolated. This is the honest shared dependency in the design. Don't hide it. Say it before the interviewer does, then explain what shapes its impact.""")

D = Diagram("The honest shared dependency, and why the cache is safe")
D.box('edge', 60, 60, 380, 120, 'Global Edge', '', kind='shared', step=0)
D.box('router', 560, 60, 420, 120, 'Router', 'in-memory tenant context cache', kind='shared', step=0, hl='1')
D.box('tcs', 1120, 60, 560, 120, 'Tenant Context Service', 'DOWN · cache misses fail', kind='deny', step=0)
D.arrow('edge', 'router', step=0, kind='shared', name='e-r')
D.arrow('router', 'tcs', step=2, kind='deny', dashed=True)
D.box('hit', 560, 320, 420, 120, 'Cache hit', 'steady-state traffic keeps flowing', kind='ok', step=1)
D.arrow('router', 'hit', step=1, kind='ok', fs='b', ts='t', name='r-h')
D.box('miss', 1120, 320, 560, 120, 'Uncached isolated tenant', 'rejected — never sent to commercial', kind='deny', step=2)
D.box('why', 60, 560, 1800, 160, 'Why serving from cache is safe during the outage', 'A tenant switch requires the Tenant Context Service to be healthy. While it is down, no tenant’s environment can change — so the cache cannot send anyone to the wrong place.', kind='cp', step=3, hl='3')
D.label(60, 770, 'Targets: **99.95%** a month per environment  ·  **99.99%** for the shared entry path — stricter, because its failure is everyone’s.', kind='neutral', step=4, w=1800, size='m', align='center')
sid = D.build()
seg(sid, 0, """Here's how you answer the challenge: your Router and Tenant Context Service are shared, isn't that a shared failure domain? First word: yes. Then shape the impact. Imagine the Tenant Context Service goes down.""", travel=travel(D.paths['e-r'], 'shared'))
seg(sid, 1, """The Router serves tenant context from its in-memory cache. Only cache misses call the Tenant Context Service. So steady-state traffic, for tenants already in the cache, keeps flowing.""", travel=travel(D.paths['r-h'], 'ok'))
seg(sid, 2, """What's affected is new or uncached lookups. And for an isolated tenant, a lookup that fails is rejected. Never sent to commercial. Failing closed holds even here.""")
seg(sid, 3, """Now the subtle part, and it's a genuinely strong point. Why is it safe to keep serving from a cache when you can't reach the source of truth? Because a tenant switch requires the Tenant Context Service to be healthy. While it's down, no tenant's environment can change. So the cached answer can't be stale in a way that sends anyone to the wrong place. The outage that makes the cache necessary is the same outage that makes it safe. If you say that clearly, most infra interviewers will move on.""")
seg(sid, 4, """And the targets. Tenant-facing availability of ninety-nine point nine five percent a month, per environment. And ninety-nine point nine nine percent for the shared entry path. Stricter on purpose, because its failure is every tenant's failure. Publicly, Isolated Cloud carries the same uptime SLA as Cloud Enterprise. Keep the public commitment and the internal targets clearly separate when you speak.""")

sid = table("The two guarantees", ["Must be impossible", "Why it matters"], [
 (0, ["1. An isolated tenant's request never reaches the commercial environment.", "It would serve an isolated customer from shared infrastructure."], ['dp', None]),
 (1, ["2. Nothing inside an isolated environment calls a commercial or multi-tenant service.", "One call carries customer data into shared infrastructure."], ['dp', None]),
], widths=[55, 45])
seg(sid, 0, """Now the isolation guarantees. Once a tenant is isolated, two things have to be impossible, not just unlikely. Guarantee one: an isolated tenant's request never reaches the commercial environment. Because that would serve an isolated customer from shared infrastructure.""")
seg(sid, 1, """Guarantee two: nothing inside an isolated environment calls a commercial or multi-tenant service. Because a single call carries customer data into shared infrastructure. Notice the words: impossible, not unlikely. That framing tells the interviewer you designed for guarantees, not probabilities.""")

sid = quote_slide("The instinct to resist", "If the isolated shard is down, fall back to commercial. Some service beats none.",
 sub="In a normal system that's good reliability practice. Here it's a breach.")
seg(sid, 0, """Guarantee one first, and the instinct you have to resist. Your SRE lead raised it in an architecture review. If the isolated shard is unhealthy, should the Router send the tenant to commercial? Some service beats none. It's a completely normal reliability instinct. If the new path fails, try the old one.""")
seg(sid, 1, """In a normal system, that's good practice. Here, it's a breach. An outage is a reliability problem. Serving an isolated customer from shared infrastructure is a compliance failure, and it's exactly what they pay to prevent. So the answer was no fallback, anywhere. And when you tell this story, give the SRE lead credit. It was a fair question. Making the other person look reasonable makes you look senior.""")

D = Diagram("Three independent locks")
D.box('req', 60, 60, 360, 120, 'Isolated tenant request', '', kind='dp', step=0)
D.box('l1', 560, 30, 560, 180, 'LOCK 1 · Router', 'fails closed: no healthy shard → error + retry\nno tenant context → reject\nno fallback path exists', kind='ok', step=0, hl='0')
D.box('com', 1300, 60, 540, 120, 'Commercial runtime', '', kind='com', step=1)
D.arrow('req', 'l1', step=0, kind='dp', name='q-l1')
D.arrow('l1', 'com', step=1, kind='deny', dashed=True, label='bug?', name='l1-c')
D.box('l2', 1300, 280, 540, 150, 'LOCK 2 · Commercial side', 'refuses tenants locked as migrated', kind='ok', step=1, hl='1')
D.arrow('com', 'l2', step=1, kind='deny', fs='b', ts='t')
D.box('l3', 1300, 520, 540, 150, 'LOCK 3 · No data left', 'commercial copy deleted after the rollback window', kind='ok', step=2, hl='2')
D.arrow('l2', 'l3', step=2, kind='deny', fs='b', ts='t')
D.box('al', 60, 520, 1100, 150, 'ALERT · any isolated tenant’s request seen by the commercial runtime', 'expected value: zero', kind='deny', step=3, hl='3')
D.label(60, 760, 'A bug in one lock doesn’t become a breach.', kind='neutral', step=4, w=1800, size='l', align='center')
sid = D.build()
seg(sid, 0, """So how do you actually make it impossible? You don't trust one lock. Lock one is the Router, and it fails closed. If tenant context says isolated and no healthy shard is found, the request errors and is retried. If tenant context is unavailable, the request is rejected. There is no default to commercial. There's no fallback path in the code at all.""", travel=travel(D.paths['q-l1'], 'dp'))
seg(sid, 1, """But suppose a bug gets through anyway. Lock two is on the commercial side. It refuses any request for a tenant locked as migrated.""", travel=travel(D.paths['l1-c'], 'deny'))
seg(sid, 2, """Lock three: after the rollback window, the tenant's commercial copy is deleted. There's simply no data there to serve. Even if both other locks failed, there's nothing to leak.""")
seg(sid, 3, """And behind all three, an alert. Any isolated tenant's request seen by the commercial runtime. The expected value is zero. Any non-zero value is an incident.""")
seg(sid, 4, """Three independent locks, so a bug in one doesn't become a breach. And this isn't theory. It's exactly what turned your worst production cutover into about ten minutes of errors, instead of data served from the wrong place. We'll walk through that incident in a moment.""")

D = Diagram("Guarantee 2: layers that stop calls out")
layers = [('Network', 'Dedicated AWS accounts and VPC. No route to commercial. The only way out is the Egress Gateway.', 'cp'),
          ('Egress Gateway', 'Commercial Atlassian services get no special treatment: denied unless explicitly allowed.', 'deny'),
          ('Dependencies', 'Point at isolated counterparts — why a service cannot move before its dependencies.', 'dp'),
          ('Readiness check', 'Any commercial endpoint fails it. Every service runs with outbound denied before cutover.', 'shared'),
          ('Detection', 'Egress denials monitored. A denied call is a bug to fix, never a rule to open.', 'ok')]
for k, (a, b, kind) in enumerate(layers):
    y = 20 + k * 140
    D.box('ly%d' % k, 60 + k * 40, y, 1800 - k * 80, 118, a, b, kind=kind, step=k, hl=str(k))
sid = D.build()
seg(sid, 0, """Guarantee two is harder, because the calls you need to stop are hidden. Services had years of hardcoded dependencies on shared services that nobody had written down. So again, layers. The first wall is the network. Isolated environments sit in their own AWS accounts and VPC with no route to commercial services. The only way out is the Egress Gateway.""")
seg(sid, 1, """The second is the gateway itself. Commercial Atlassian services get no special treatment. They're denied like any other destination unless explicitly allowed. That's a subtle but important choice. Your own company's services are not trusted by default.""")
seg(sid, 2, """The third is dependencies. Inside an isolated environment, a service's dependencies point at their isolated counterparts. And this is the real reason tier order mattered. A service can't move before its dependencies exist in isolated, because otherwise the only thing left for it to call is commercial.""")
seg(sid, 3, """The fourth is the readiness check. Any commercial endpoint in a service's dependencies fails it. And every service ran in isolated with outbound traffic denied before cutover.""")
seg(sid, 4, """The fifth is detection. Egress denials are monitored. And here's the rule that made it hold: a denied call to a commercial service is a bug to fix in the service, never a rule to open. Your line for this is memorable. If a service only works with a hole in the wall, it isn't ready to migrate. And the one sanctioned relationship, the control plane, runs the other way. It provisions, deploys and configures. At request time, isolated services don't call commercial product services.""")

# ---- Incident 1
D = Diagram("Incident 1: the cutover mis-route")
steps1 = [('Rehearsal', 'Test tenant switched; requests kept hitting commercial for a few minutes. Invalidation became an explicit switch step.', 'shared'),
          ('Early production cutover', 'A few Router instances did not receive the invalidation.', 'deny'),
          ('~10 minutes', "A small share of the customer's requests went to the commercial runtime.", 'deny'),
          ('Lock 2 held', 'Commercial refused them — tenant already locked as migrated. Users saw errors, nothing served.', 'ok'),
          ('Detected', 'Per-tenant error rate, before the customer raised it. Forced a refresh.', 'info'),
          ('Lasting fix', 'A switch is not complete until every Router instance confirms the new context.', 'ok')]
for k, (a, b, kind) in enumerate(steps1):
    y = 20 + k * 135
    D.box('i%d' % k, 60, y, 440, 112, a, '', kind=kind, step=k, hl=str(k))
    D.label(560, y + 22, b, kind=kind, step=k, w=1300, size='m')
    if k: D.arrow('i%d' % (k - 1), 'i%d' % k, step=k, kind='neutral', fs='b', ts='t')
sid = D.build()
seg(sid, 0, """Now the incidents, told the way a Staff engineer tells them. Incident one starts before production. In the first staging rehearsal, you switched a test tenant from commercial to isolated, and requests kept landing on the commercial runtime for a few minutes. Some Router instances were still serving from cache. No customer was affected, but it changed the design. Cache invalidation became an explicit step in the switch, not something left to expire.""")
seg(sid, 1, """Then, during an early production cutover, invalidation was already a step. But a few Router instances didn't receive it.""")
seg(sid, 2, """For about ten minutes, a small share of that customer's requests went to the commercial runtime.""")
seg(sid, 3, """And here's why it was an incident and not a breach. Lock two held. The commercial side refused those requests because the tenant was already locked as migrated. Users saw errors. Nothing was served from shared infrastructure.""")
seg(sid, 4, """You detected it from the per-tenant error rate, before the customer raised it, and forced a refresh. Per-tenant metrics matter here: one isolated customer's problem disappears into a service-wide average.""")
seg(sid, 5, """And the lasting fix: a switch isn't complete until every Router instance confirms it has the new context. If any Router reports the old one, the cutover doesn't finish. Notice that the fix is not, be more careful. It changes the process so this class of failure can't happen that way again. That's the exact distinction between a Senior and a Staff incident answer.""")

# ---- Incident 2
D = Diagram("Incident 2: the shard replacement ordering bug")
D.zone(60, 20, 860, 640, 'What happened', kind='deny', step=0)
wrong = [('1', 'Invalidate the cache'), ('2', 'Cache refills — from the OLD placement'), ('3', 'Repository update lands, too late'), ('4', 'Requests reach the shard being retired')]
for k, (n, t) in enumerate(wrong):
    D.box('w%d' % k, 110, 90 + k * 140, 760, 105, n + ' · ' + t, '', kind='deny', step=min(k, 1), small=True)
    if k: D.arrow('w%d' % (k - 1), 'w%d' % k, step=min(k, 1), kind='deny', fs='b', ts='t')
D.zone(1000, 20, 860, 640, 'The fixed order', kind='ok', step=2)
right = [('1', 'Update the shard configuration repository'), ('2', 'Invalidate the cache'), ('3', 'Route new traffic'), ('+', 'Alert: any request reaching a retired shard')]
for k, (n, t) in enumerate(right):
    D.box('rt%d' % k, 1050, 90 + k * 140, 760, 105, n + ' · ' + t, '', kind='ok' if k < 3 else 'info', step=2 if k < 3 else 3, small=True)
    if 0 < k < 3: D.arrow('rt%d' % (k - 1), 'rt%d' % k, step=2, kind='ok', fs='b', ts='t')
D.label(60, 730, 'Source of truth first. Cache second. Traffic last.', kind='neutral', step=4, w=1800, size='l', align='center')
sid = D.build()
seg(sid, 0, """Incident two. A shard replacement during maintenance. The team updated placement and invalidated the cache, but in the wrong order.""")
seg(sid, 1, """The cache was invalidated. It immediately refilled, from the old placement, because the repository update hadn't landed yet. Then the repository update landed, too late. The cache now held a stale answer, and some requests went to a shard that was being retired.""")
seg(sid, 2, """The fix was the order. Update the shard configuration repository first. Then invalidate the cache. Then route new traffic. Once the source of truth is correct before the cache is cleared, a refill can only ever pick up the new placement.""")
seg(sid, 3, """And you added an alert for any request that reaches a retired shard, so if the order is ever broken again, you find out immediately.""")
seg(sid, 4, """The general principle, which is worth saying out loud: source of truth first, cache second, traffic last. And the lesson you drew from both incidents together is your best reflection answer. The rehearsal problem and both production issues came from the same place, cache invalidation. You hardened it in three rounds instead of one. If you did it again, you'd design invalidation in from day one.""")

sid = cards("Two more failure stories infra panels ask about", [
 (0, "The customer revoked our key grant — by accident", "A key policy edit dropped decrypt. Reads failed within minutes; access-denied alarms paged us before their users noticed.", 'deny'),
 (0, "What changed", "The fix was on their side. We added alerts on grant changes, and a pre-check customers run before editing key policies.", 'ok'),
 (1, "Subnet exhaustion, before go-live", "Pre-cutover load test: one zone's subnet ran out while Auto Scaling added replicas. New replicas failed to launch.", 'deny'),
 (1, "What changed", "Added secondary ranges. Block size now comes from the tenant's shard descriptors, not one default.", 'ok'),
], cols=2)
seg(sid, 0, """Two more failure stories that infra panels like. First, the key revocation. Customer-managed keys cut both ways. If a customer revokes the grant, their data, and their backups, become unreadable to you. That's the point of the feature. It happened once by accident. A customer's security team edited a key policy and dropped the decrypt permission. Reads started failing within minutes, and your access-denied alarms paged you before their users noticed. The fix was on their side. Afterwards you added alerts on grant changes, and a pre-check customers run before editing key policies.""")
seg(sid, 1, """Second, subnet exhaustion. Every replica takes IP addresses. In a pre-cutover load test for a large tenant, one zone's subnet ran out while Auto Scaling was adding replicas, and new replicas failed to launch. You caught it before go-live, added secondary ranges, and now size each environment's address block from its shard descriptors instead of one default. The pattern in both: the failure was found by a signal you'd built, and the fix changed a mechanism, not a habit.""")

sid = statement("The pattern an infra panel should hear", "Every step fails closed. Every failure is bounded to one environment.",
 "And the parts that are shared are the ones held to the stricter target.", kind='ok')
seg(sid, 0, """So here's the pattern to leave the infra panel with. Every step fails closed. Every failure is bounded to one environment.""")
seg(sid, 1, """And the parts that are shared are the ones held to the stricter target. If you can say that sentence and back each clause with a specific story from this chapter, you've covered failure modes at Staff level.""")

question("A replica fails. Then a whole shard fails. What's different?", 8,
 "A replica failing is absorbed inside the shard; infrastructure replaces it and the tenant-to-shard mapping doesn't change. A shard being replaced changes placement: update the shard configuration repository first, then invalidate the cache, then route new traffic. We learned that order the hard way.",
 "It separates the two events cleanly and gives the exact ordering, with a hint of real experience behind it.",
 "Whether you actually operated the system, or only heard it described.",
 ["What happened when you got the order wrong?", "What if the placement cache is lost?", "What if the repository is down?"],
 narr=dict(
  short="""Thirty seconds. A replica failing is absorbed inside the shard. Infrastructure replaces it, and the tenant to shard mapping doesn't change. Nothing in placement moves. A shard being replaced does change placement. So the order is: update the shard configuration repository first, then invalidate the cache, then route new traffic. And we learned that order the hard way.""",
  strong="""Why it lands. It treats them as two genuinely different events, and it gives an exact order rather than, we update things. And the last sentence, we learned that order the hard way, invites the follow-up you want, because you have a real story ready.""",
  testing="""They're testing whether you operated this system. Confusing replica failure with shard replacement is the single clearest sign that someone has only heard the architecture described.""",
  follow="""Follow-ups. What happened when you got the order wrong? Tell incident two: cache invalidated first, it refilled from old placement, some requests reached a retiring shard, the order was fixed and an alert added. What if the placement cache is lost? Nothing is lost. It's slower until it refills, but still correct. And if they ask what happens when the repository is down, don't invent a mechanism you haven't described. Say the repository is the source of truth, the cache only accelerates it, and placement changes can't safely happen until it's back."""))

question("Your Router and Tenant Context Service are shared. Isn't that a shared failure domain?", 8,
 "Yes. The Router serves tenant context from its in-memory cache, so a Tenant Context Service outage hits uncached lookups, not steady-state traffic. Serving from cache is safe because a tenant switch requires that service to be healthy — nothing can change while it's down. And a failed lookup for an isolated tenant is rejected, never sent to commercial.",
 "It concedes immediately, then shapes the impact with a mechanism that's safe for a stated reason.",
 "Honesty about shared dependencies, and whether you understand when a cache is safe to serve from.",
 ["What are your availability targets?", "What happens when a zone or region fails?", "Why no cross-region failover?"],
 narr=dict(
  short="""Thirty seconds. Yes, and I'd say that directly. The Router serves tenant context from its in-memory cache, so an outage of the Tenant Context Service hits new or uncached lookups, not steady-state traffic. Serving from cache during that outage is safe, because a tenant switch requires the service to be healthy. While it's down, no tenant's environment can change. And for an isolated tenant, a failed lookup is rejected, never sent to commercial.""",
  strong="""Why it lands. The first word is yes. Denying a shared dependency that obviously exists costs you credibility instantly. Then it explains not only what happens, but why the cache is safe, which is the insight most candidates miss.""",
  testing="""They're testing honesty under pressure, and whether you understand the conditions under which a cache can be trusted without its source.""",
  follow="""Expect the targets next: ninety-nine point nine five a month per environment, ninety-nine point nine nine for the shared entry path. Then zones and regions: zones are routine, regions are a deliberate residency trade with restore-based recovery. And if they push on why there's no cross-region failover, the answer is that copying data to another region can break the customer's residency commitment. Slower recovery is the one these customers asked for."""))
