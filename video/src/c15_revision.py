# -*- coding: utf-8 -*-
from engine import *

chapter(15, "Rapid revision", "Everything that matters, fast. Watch this the night before.",
 """Chapter fifteen. Rapid revision. This is the chapter to watch the night before, or an hour before the interview. No new reasoning. Just the things you need to be able to say without thinking.""")

sid = statement("Three sentences to have automatic", "“Isolation is a platform capability, not a product feature.”",
 "“Tenant context is static and cacheable. Shard placement is dynamic and operational. Coupling them would make every placement change touch tenant identity.”", kind='ok')
seg(sid, 0, """Three sentences to have automatic. The thesis. Isolation is a platform capability, not a product feature.""")
seg(sid, 1, """The decision. Tenant context is static and cacheable. Shard placement is dynamic and operational. Coupling them would make every placement change touch tenant identity. And the third, the scale: about a hundred and seventy-eight teams, phased by dependency, priority, traffic, risk and readiness, and you had authority over none of them. Architecture, judgement, scope. Almost every question is a drill-down from one of those three.""")

D = Diagram("The request path, one more time")
path = [('Client', 'info'), ('Global Edge', 'shared'), ('Router', 'shared'), ('Shard Manager', 'dp'), ('Shard', 'dp'), ('Replicas', 'dp'), ('Dedicated data', 'dp'), ('Egress Gateway', 'deny')]
for k, (n, kind) in enumerate(path):
    x = 60 + (k % 4) * 460
    y = 60 if k < 4 else 380
    D.box('p%d' % k, x, y, 380, 130, n, '', kind=kind, step=0 if k < 4 else 1)
for k in range(1, 8):
    if k == 4:
        D.arrow('p3', 'p4', step=1, kind='dp', fs='b', ts='t', via=[(1630, 285), (250, 285)], name='a4')
    else:
        D.arrow('p%d' % (k - 1), 'p%d' % k, step=0 if k < 4 else 1, kind='neutral', name='a%d' % k)
D.label(520, 210, 'commercial or isolated?\ncached tenant context · miss → TCS', kind='shared', step=0, w=880, size='s', align='center')
D.label(60, 560, 'Control plane: shared, **off the request path**.  Repository: **source of truth**.  Fail closed: **no fallback**.', kind='neutral', step=2, w=1800, size='m', align='center')
sid = D.build()
seg(sid, 0, """The request path. Client, Global Edge, Router. The Router decides commercial or isolated from cached tenant context, and on a miss asks the Tenant Context Service. Then the Shard Manager decides which shard, right now.""",
    travel=travel(D.paths['a1'] + D.paths['a2'][1:] + D.paths['a3'][1:], 'shared'))
seg(sid, 1, """Then the shard, its replicas, the tenant's dedicated data, and the Egress Gateway for anything leaving.""",
    travel=travel(D.paths['a4'] + D.paths['a5'][1:] + D.paths['a6'][1:] + D.paths['a7'][1:], 'dp'))
seg(sid, 2, """And three facts that go with it. The control plane is shared and off the request path. The shard configuration repository is the source of truth; the cache is only speed. And everything fails closed. No fallback to commercial.""")

sid = table("Numbers — say them the same way every time", ["What", "Number"], [
 (0, ["Teams", "About 178"]),
 (0, ["Provisioning", "~2 days pilot → ~5 hours by phase two"]),
 (1, ["IP ranges", "/20 default · /19 large tenants"]),
 (1, ["Rollout", "commercial → wave 0 (3 Atlassian-owned) → wave 1 canaries, 24h → wave 2"]),
 (2, ["Availability", "99.95%/month per environment · 99.99% shared entry path"]),
 (2, ["Recovery", "PITR ~5 min at risk · shard 1–2 h · environment within a day"]),
 (3, ["Cost", "smallest tenant ~4–6× commercial · right-sizing took ~⅓ off"]),
 (3, ["Production", "~a dozen customer environments · >100 shards each · 2 self-caused incidents"]),
], widths=[26, 74])
seg(sid, 0, """Numbers. Say them the same way every time. About a hundred and seventy-eight teams. Provisioning: about two days for the pilot, around five hours by phase two.""")
seg(sid, 1, """IP ranges: a slash twenty by default, a slash nineteen for large tenants. Rollout: commercial, wave zero with three Atlassian-owned environments, wave one canaries with a twenty-four hour bake, then wave two.""")
seg(sid, 2, """Availability: ninety-nine point nine five a month per environment, ninety-nine point nine nine for the shared entry path. Recovery: about five minutes of data at risk, one to two hours for a shard, within a day for an environment.""")
seg(sid, 3, """Cost: the smallest tenant is roughly four to six times commercial, and right-sizing took about a third off. Production: about a dozen customer environments, well over a hundred shards each, and two customer-impacting incidents you caused in the first year.""")

sid = cards("The stories to have ready", [
 (0, "How it started", "Three design reviews in a week → one-page note to your VP.", 'shared'),
 (0, "Alignment", "Two weeks of one-on-ones · “not handing their pager to someone else's roadmap” · contract.", 'shared'),
 (1, "Changed your own mind", "Placement out of the Router — the event list.", 'dp'),
 (1, "The fallback question", "SRE lead asked; the answer was no — reliability from replicas.", 'dp'),
 (2, "Incident 1", "~10-minute mis-route; lock 2 held; every Router must confirm.", 'deny'),
 (2, "Incident 2", "Wrong order on shard replacement; repository → cache → route.", 'deny'),
 (3, "The custom-scripts team", "Not resistance — a real gap; 4–5 teams reused the fix.", 'ok'),
 (3, "DataLoader", "Lost tenant context; default was commercial; caught by checking where calls went.", 'ok'),
], cols=2)
seg(sid, 0, """The stories to have ready. How it started: three design reviews in a week, and the one-page note. Alignment: two weeks of one-on-ones, the Jira lead's pager line, and the contract.""")
seg(sid, 1, """Changing your own mind: placement out of the Router, because of the event list. And the fallback question from your SRE lead, answered with no, and reliability from replicas.""")
seg(sid, 2, """Incident one: the ten-minute mis-route, lock two held, and every Router must now confirm. Incident two: the wrong order on shard replacement, fixed to repository, then cache, then route.""")
seg(sid, 3, """The custom-scripts team: not resistance, a real gap, reused by four or five teams. And DataLoader: lost tenant context, a commercial default endpoint, caught because you checked where every call went.""")

sid = compare("Do not say",
 ("Wrong", 'deny', 0, ["“A shard is an instance.”", "“The cache holds placement.”", "“We fell back to commercial.”", "Kubernetes · a named policy engine", "“The edge decides placement.”"]),
 ("Say instead", 'ok', 1, ["A logical isolated runtime for a tenant + product, with replicas", "The repository is the source of truth; the cache is speed", "We fail closed; reliability comes from replicas", "AWS-native Auto Scaling · policy-driven enforcement", "The Router decides commercial or isolated; the Shard Manager decides the shard"]))
seg(sid, 0, """And the do-not-say list. A shard is an instance. The cache holds placement. We fell back to commercial. Kubernetes, or naming a specific policy engine. The edge decides placement. Any one of these tells the interviewer you don't know the system.""")
seg(sid, 1, """Say instead: a shard is a logical isolated runtime for a tenant and product, with replicas. The repository is the source of truth, and the cache is speed. We fail closed, and reliability comes from replicas. AWS-native Auto Scaling, and policy-driven enforcement. And the Router decides commercial or isolated, while the Shard Manager decides the shard.""")

sid = cards("Your fifteen minutes: questions to ask them", [
 (0, "How does a decision affecting several teams actually get made here?", "Listen for a mechanism, not a person.", 'ok'),
 (0, "What's the most recent architectural decision this team got wrong, and how did you find out?", "Is there a real feedback loop?", 'ok'),
 (1, "What would you want someone in this role to have changed a year in?", "The real expectation, not the job description.", 'info'),
 (1, "Is there anything about my background you're unsure about?", "Uncomfortable — and it surfaces a misunderstanding while you can fix it.", 'shared'),
], cols=2)
seg(sid, 0, """Finally, your fifteen minutes. It's a quarter of the interview, and it's scored. Running dry after three questions is noticeable. Lead with these. How does a decision affecting several teams actually get made here? Listen for a mechanism, not a person. And, what's the most recent architectural decision this team got wrong, and how did you find out? That tests whether there's a real feedback loop, and whether it's safe to be wrong.""")
seg(sid, 1, """Then, what would you want someone in this role to have changed a year in? That gets the real expectation. And close with: is there anything about my background you're unsure about? It's slightly uncomfortable, and that's the point. It can surface a misunderstanding while you can still fix it.""")
