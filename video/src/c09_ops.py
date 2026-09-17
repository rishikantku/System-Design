# -*- coding: utf-8 -*-
from engine import *

chapter(9, "Scale and operations", "Reaching into environments, shipping releases to all of them, scaling, recovering, observing, and paying for it.",
 """Chapter nine. Scale and operations. Isolation multiplies everything. Every environment is another thing to reach into, deploy to, scale, back up, observe and pay for. An infra panel wants to know how you kept the cost of each of those close to zero per environment. That's the thread through this whole chapter.""")

sid = statement("The operating constraint", "Anything that costs one unit of effort per environment becomes unaffordable.",
 "So every operation had to be done once by the platform, and repeated automatically everywhere.", kind='cp')
seg(sid, 0, """Start with the constraint that shapes every operational decision. Anything that costs one unit of effort per environment becomes unaffordable.""")
seg(sid, 1, """With about a dozen customer environments, each with well over a hundred shards, anything manual per environment or per shard just doesn't scale. So every operation had to be done once, by the platform, and repeated automatically everywhere. Keep that in your head as we go through each area.""")

# ---- management channel
D = Diagram("How the control plane reaches in, without a route out")
D.zone(60, 20, 560, 640, 'Shared control plane', kind='cp', step=0)
D.box('cp', 110, 100, 460, 130, 'Control plane', 'desired state · deploy commands · schema · config', kind='cp', step=0)
D.box('reg', 110, 330, 460, 120, 'Release artefacts', 'copied in before a rollout', kind='cp', step=2, small=True)
D.zone(1100, 20, 760, 640, 'Isolated environment', kind='dp', step=0)
D.box('ep', 1150, 100, 660, 130, 'One private endpoint', 'only the control plane’s account may connect', kind='dp', step=0, hl='0')
D.box('ireg', 1150, 330, 660, 120, 'Registry inside the environment', 'shards pull from inside, never from commercial', kind='dp', step=2, small=True)
D.box('shards', 1150, 520, 660, 110, 'Shards', '', kind='dp', step=2, small=True)
D.arrow('cp', 'ep', step=0, kind='cp', fo=0.4, to=0.4, label='IN · desired state, deploys', loff=(0, -18), name='in')
D.arrow('ep', 'cp', step=1, kind='info', fo=0.75, to=0.75, dashed=True, label='BACK · health, metadata only', loff=(0, 34), name='back')
D.arrow('reg', 'ireg', step=2, kind='cp', name='art')
D.arrow('ireg', 'shards', step=2, kind='dp', fs='b', ts='t')
D.label(110, 520, '**NEVER:** customer data, or a\nconnection started from inside\nthe isolated environment', kind='deny', step=3, w=470, size='m')
D.label(60, 740, 'People: no standing access. Break-glass is time-limited, needs two approvals, every session logged.', kind='neutral', step=4, w=1800, size='m', align='center')
sid = D.build()
seg(sid, 0, """First, how the control plane reaches into an isolated environment. Here's the question behind it: how do you deploy into something that has no route to commercial? The control plane never gets a network route in. Each environment exposes one private endpoint that only the control plane's account may connect to. Connections open from the control plane side only. What goes in: desired state, deploy commands, schema and config.""",
    travel=travel(D.paths['in'], 'cp'))
seg(sid, 1, """What comes back over that connection: health and status. Metadata only.""", travel=travel(D.paths['back'], 'info'))
seg(sid, 2, """Release artefacts are copied into a registry inside the environment's own accounts before a rollout. So shards pull from inside, never from a commercial registry. That closes a gap people forget. Pulling an image from a shared registry is also a call out.""",
    travel=travel(D.paths['art'], 'cp'))
seg(sid, 3, """And what never crosses: customer data, or a connection started from inside the isolated environment. The environment can't start anything back over the channel, and its VPC has no route to commercial.""")
seg(sid, 4, """And people. No standing access. Break-glass access is time-limited, needs two approvals, and every session is logged. If an interviewer asks about emergency access, give all three of those, not just, we have a break-glass process.""")

# ---- scaling
D = Diagram("Scaling: three zones, sized for two")
for k, az in enumerate('abc'):
    D.zone(60 + k * 610, 20, 570, 430, 'Availability zone ' + az, kind='dp', step=0, dashed=True)
    D.box('r%d' % k, 110 + k * 610, 100, 470, 110, 'Replica', 'Jira · Shard-123', kind='dp', step=0, small=True, dim='1' if k == 2 else None)
    D.box('db%d' % k, 110 + k * 610, 280, 470, 110, 'Database', 'primary' if k == 0 else 'standby', kind='cp', step=0, small=True, dim='1' if k == 2 else None)
D.label(1280, 460, 'zone impaired → two zones carry peak', kind='deny', step=1, w=580, size='m')
D.box('min', 60, 560, 880, 190, 'Minimum replicas by tier', 'L0 and L1: at least three\nlow-traffic L3: two, in different zones', kind='shared', step=2)
D.box('grow', 980, 560, 880, 190, 'When a tenant grows', 'replicas scale with AWS Auto Scaling — shard unchanged\nbaseline changes → resize the shard descriptor', kind='ok', step=3)
sid = D.build()
seg(sid, 0, """Scaling. Every shard spreads its replicas across three availability zones, and the databases are multi-AZ.""")
seg(sid, 1, """The sizing rule is the part to remember: sized so that two zones can carry peak traffic. So when a zone is impaired, the remaining two absorb it. That's why zones are routine. In the one real zone impairment, shards stayed up and one tenant saw about two minutes of failed writes while their database failed over.""")
seg(sid, 2, """Minimums depend on tier. L zero and L one shards always run at least three replicas. Low-traffic L three shards can run two, in different zones. That's a cost decision, and it's the kind of tiered thinking an infra panel wants to see: you don't pay the same reliability premium for everything.""")
seg(sid, 3, """And when a tenant's traffic grows, there are two levels. Replicas inside the shard scale with AWS Auto Scaling, and the shard and its placement don't change. If the tenant's baseline needs change, the shard descriptor resizes that shard, without touching the service or any other tenant. Don't confuse scaling replicas with replacing the shard.""")

# ---- rollout waves
D = Diagram("Shipping a release to every environment")
waves = [('Commercial', 'bakes first, on the most traffic', 'com'),
         ('Wave 0', '3 Atlassian-owned isolated environments', 'cp'),
         ('Wave 1', 'canary customer environments · 24h bake', 'shared'),
         ('Wave 2', 'every other environment, within its change window', 'dp')]
for k, (a, b, kind) in enumerate(waves):
    D.box('w%d' % k, 60 + k * 460, 40, 400, 170, a, b, kind=kind, step=k, hl=str(k))
    if k: D.arrow('w%d' % (k - 1), 'w%d' % k, step=k, kind='neutral', name='w%d' % k)
D.zone(60, 300, 1800, 330, 'Inside one environment', kind='dp', step=4)
for k in range(6):
    D.box('s%d' % k, 110 + k * 290, 380, 240, 100, 'Shard %d' % (k + 1), 'health gate', kind='ok' if k < 3 else 'dp', step=4, small=True, dim='5' if k > 3 else None)
    if k: D.arrow('s%d' % (k - 1), 's%d' % k, step=4, kind='ok' if k < 3 else 'neutral')
D.label(110, 520, 'Gates compare against **this tenant’s own baseline**, not a fleet average.', kind='ok', step=4, w=1700, size='m')
D.label(110, 570, 'Regression → rollout halts **for that environment**, automatically.', kind='deny', step=5, w=1700, size='m')
D.label(60, 720, 'A rollout is also a placement change: update the repository, invalidate the cache, then route.', kind='neutral', step=6, w=1800, size='m', align='center')
sid = D.build()
seg(sid, 0, """Now fleet deployment. The control plane owns deployment configuration, and every shard is its own deployment target. A release goes to commercial first, because it bakes on the most traffic.""")
seg(sid, 1, """Then wave zero: three Atlassian-owned isolated environments. You find isolated-specific problems on your own environments before any customer does.""", travel=travel(D.paths['w1'], 'cp'))
seg(sid, 2, """Wave one: canary customer environments, with a twenty-four hour bake.""", travel=travel(D.paths['w2'], 'shared'))
seg(sid, 3, """Wave two: every other environment, within its own change window. Regulated customers have change windows, and the rollout respects them.""", travel=travel(D.paths['w3'], 'dp'))
seg(sid, 4, """Inside each environment, shards roll one at a time behind health gates. And here's the detail that shows real operating experience. The gates compare against that tenant's own baseline, not a fleet average. Because one bank's normal is another bank's regression. A fleet average would hide exactly the kind of problem that only shows up in one tenant.""")
seg(sid, 5, """If a regression is detected, the rollout halts for that environment automatically. Other environments aren't blocked by one tenant's problem.""")
seg(sid, 6, """And connect this back to the architecture. Deployment is one of the events that can replace or move a shard. So a rollout is also a placement change, and it follows the same order: update the repository, invalidate the cache, then route. Linking the deployment system back to the placement design is a nice Staff touch.""")

D = Diagram("Rolling back one tenant, and where rollback stops")
D.box('ptr', 60, 40, 560, 140, 'Per-environment deployment pointer', 'one tenant can go back a version on its own', kind='ok', step=0)
ph = [('Expand', 'add the new shape', 'ok'), ('Migrate', 'move data to it', 'ok'), ('Contract', 'remove the old shape', 'deny')]
for k, (a, b, kind) in enumerate(ph):
    D.box('p%d' % k, 60 + k * 620, 300, 560, 130, a, b, kind=kind, step=1 if k < 2 else 2, hl='2' if k == 2 else None)
    if k: D.arrow('p%d' % (k - 1), 'p%d' % k, step=1 if k < 2 else 2, kind='neutral')
D.label(60, 460, '◀ rollback safe', kind='ok', step=1, w=1180, size='m', align='center')
D.label(1300, 460, 'rollback no longer safe', kind='deny', step=2, w=560, size='m', align='center')
D.label(60, 560, 'So contract steps ship **separately**, never bundled with features, and bake longer.', kind='shared', step=3, w=1800, size='m')
D.box('skew', 60, 650, 1800, 150, 'Version skew: at most two versions', 'banks freeze around quarter-end · APIs compatible across the window · security patches exempt from freezes', kind='cp', step=4)
sid = D.build()
seg(sid, 0, """Can you roll back one tenant on its own? Yes. Every environment has its own deployment pointer, so one tenant can go back a version independently. You used single-tenant rollback a handful of times in the first year, each time for a regression that only showed up in one tenant's data shape.""")
seg(sid, 1, """But don't claim unlimited rollback. The limit is schema. You use expand then contract. Expand: add the new shape. Migrate: move data to it. Rollback is safe through both of those steps.""")
seg(sid, 2, """Contract removes the old shape. Once that runs, rolling back the code no longer works, because the shape it expects is gone.""")
seg(sid, 3, """So contract steps ship separately, never bundled with features, and they bake longer. That's how you keep per-tenant rollback real rather than theoretical.""")
seg(sid, 4, """And version skew. Banks freeze changes around quarter-end, so environments drift behind commercial. You allow at most two versions of skew, keep APIs compatible across that window, and security patches are exempt from customer freezes. That rule came from the pilot bank's first quarter-end, when skew grew faster than planned. Again: a rule tied to the event that created it.""")

sid = table("Backups and recovery", ["Data", "Recovery"], [
 (0, ["Where backups live", "Encrypted with the customer's keys, in a separate backup account inside the isolated OU, same geography"]),
 (1, ["Databases", "Point-in-time recovery. About five minutes of data at risk."]),
 (1, ["Files and attachments", "Versioned and restorable."]),
 (2, ["Search indexes", "Not backed up. Rebuilt from source."]),
 (3, ["Time to recover", "One or two hours for a single shard. Within a day for a whole environment."], [None, 'ok']),
 (4, ["Commercial backups after migration", "Can't delete one tenant surgically. Ages out with retention — agreed up front."], [None, 'deny']),
], widths=[32, 68])
seg(sid, 0, """Backups. They're encrypted with the customer's own keys, and copied to a separate backup account inside the isolated organizational unit, in the same geography. Why a separate account? It protects backups from a compromised or mistaken production account.""")
seg(sid, 1, """Databases have point-in-time recovery, with about five minutes of data at risk. Files and attachments are versioned and restorable.""")
seg(sid, 2, """Search indexes aren't backed up at all. They're rebuilt from source. That's a deliberate choice: an index is derived data.""")
seg(sid, 3, """Recovery time: one or two hours for a single shard, within a day for a whole environment. And regions: recovery is restore-based, into a region the customer's rules allow, with targets agreed per customer.""")
seg(sid, 4, """And one honest limit. After a tenant migrates, their data still sits in commercial backups until those expire. You can't surgically delete one tenant from a shared backup. It ages out with retention, and that was written into the migration agreement up front. Volunteering a limit like this is a trust signal.""")

D = Diagram("What the smallest isolated tenant costs")
D.zone(60, 40, 1000, 520, 'The fixed floor', kind='deny', step=0)
for k, t in enumerate(['multi-AZ databases', 'minimum replicas for every shard', 'the management channel', 'monitoring', 'a backup account']):
    D.label(120, 130 + k * 70, '•  ' + t, kind='neutral', step=0, w=880, size='m')
D.label(120, 490, 'roughly **4–6×** the same customer in commercial', kind='deny', step=0, w=900, size='m')
levers = [('Per-shard sizing', 'shard descriptors, not sized like the largest customer'), ('Right-size after real traffic', 'start from commercial usage; cut back after a few weeks — about a third off'),
          ('Tier minimums', 'low-traffic L3 shards run fewer replicas'), ('No extra orchestration layer', 'nothing else paid for once per environment')]
for k, (a, b) in enumerate(levers):
    D.box('lv%d' % k, 1120, 40 + k * 135, 740, 115, a, b, kind='ok', step=1 + min(k, 1), small=True)
D.label(60, 640, 'A small customer pays the floor whether they have fifty users or five thousand.', kind='shared', step=3, w=1800, size='l', align='center')
sid = D.build()
seg(sid, 0, """Cost. Know this cold, because infra panels ask it. The smallest isolated tenant costs roughly four to six times what the same customer costs in multi-tenant commercial. And almost all of that is a fixed floor, not usage. Multi-AZ databases. Minimum replicas for every shard. The management channel. Monitoring. A backup account.""")
seg(sid, 1, """The levers. Per-shard sizing through shard descriptors, so each shard is sized for its own tenant, not for the largest customer.""")
seg(sid, 2, """Right-sizing after real traffic. New environments start from the tenant's commercial usage and are cut back after a few weeks, which took about a third off a typical environment's baseline. Tier minimums, so low-traffic L three shards run fewer replicas. And no extra orchestration layer, because every added component would be paid for once per environment.""")
seg(sid, 3, """And the implication worth saying: a small customer pays that floor whether they have fifty users or five thousand. That's a business insight, not just an engineering one. It explains which customers Isolated Cloud makes sense for. When an engineer connects cost structure to product fit, that's a Staff signal.""")

sid = cards("Observability: what you watched, and what surprised you", [
 (0, "Shard health", "Tracked by the Shard Manager. Drives failover and replacement.", 'dp'),
 (0, "Latency + errors per tenant and product", "Not per service. One isolated customer's problem vanishes in a service-wide average.", 'info'),
 (1, "Migration progress per team", "Computed by the tool, never self-reported.", 'shared'),
 (1, "Egress denials", "Expected a compliance metric. Became the best early warning.", 'ok'),
], cols=2, note=(2, "Our own telemetry is outbound data too — it goes through the Egress Gateway like everything else."))
seg(sid, 0, """Observability. Monitoring and logging configuration was provisioned per environment by the control plane, like everything else. You watched four things. Shard health, tracked by the Shard Manager, which drives failover and replacement. And latency and error rates per tenant and per product, not just per service. That's what caught the ten-minute cutover mis-route before the customer did.""")
seg(sid, 1, """Migration progress per team, computed by the tool rather than self-reported. And egress denials. That one surprised you. You expected a compliance metric. It became your best early warning. When a service started trying to send data somewhere it hadn't declared, the denial count moved before anything else did.""")
seg(sid, 2, """And one more detail that shows you thought it through. Your own telemetry is outbound data too. So it went through the Egress Gateway like everything else. That forced a conversation with a lot of teams about what their logs actually contained. Logs are data. In a regulated environment, you don't get to forget that.""")

sid = table("What production looked like", ["Measure", "Value"], [
 (0, ["Environments live", "About a dozen customer environments, plus three Atlassian-owned (wave 0)"]),
 (0, ["Shards per environment", "Well over a hundred"]),
 (1, ["Provisioning a new environment", "About two days for the pilot · around five hours by phase two"]),
 (2, ["Customer-impacting incidents we caused, first year", "Two: the cutover mis-route (~10 min) and the shard replacement ordering bug"], [None, 'deny']),
 (3, ["Other notable events", "One zone impairment · one customer key-policy mistake · one subnet exhaustion caught before go-live"]),
], widths=[40, 60])
seg(sid, 0, """Finally, what production looked like. Have these numbers consistent every time you say them. About a dozen customer environments, plus three Atlassian-owned ones used as wave zero. Well over a hundred shards per environment.""")
seg(sid, 1, """Provisioning: about two days for the pilot, around five hours by phase two.""")
seg(sid, 2, """Customer-impacting incidents you caused in the first year: two. The cutover mis-route of about ten minutes, and the shard replacement ordering bug.""")
seg(sid, 3, """And other notable events: one zone impairment, one customer key-policy mistake, and one subnet exhaustion caught in load testing before go-live. Don't inflate any of these. Small, specific, consistent numbers are far more believable than big round ones.""")

question("How did a release roll out across isolated environments, and can you roll back one tenant?", 10,
 "Commercial first, then three Atlassian-owned isolated environments, then canary customers with a 24-hour bake, then everyone else in their change windows. Inside an environment, shards roll one at a time behind gates against that tenant's own baseline. Yes, one tenant can roll back — until a schema contract step runs, so those ship separately.",
 "It gives the waves, the gate design, and the real limit on rollback, instead of claiming unlimited rollback.",
 "Whether you've actually operated fleet deployment across isolated tenants with different change windows.",
 ["How did you handle customers who froze changes?", "What happens if a customer refuses a security patch?", "Why compare against the tenant's own baseline?"],
 narr=dict(
  short="""Thirty seconds. Commercial first, because it bakes on the most traffic. Then our three Atlassian-owned isolated environments. Then canary customer environments with a twenty-four hour bake. Then everyone else within their change windows. Inside each environment, shards roll one at a time behind health gates that compare against that tenant's own baseline. And yes, one tenant can roll back on its own, until a schema contract step runs, which is why contract steps ship separately.""",
  strong="""Why it lands. It covers across environments and within an environment, and it volunteers the limit on rollback. Claiming you can always roll back is a red flag for experienced operators.""",
  testing="""They're testing whether you've run deployment across many isolated tenants, each with its own risk and its own change windows, rather than one global rollout.""",
  follow="""Follow-ups. Customer freezes: at most two versions of skew, APIs compatible across the window, security patches exempt. If they ask what happens when a customer refuses a security patch, stay with what you have: patches are exempt from freezes by agreement. Don't invent an escalation process. And why the tenant's own baseline? Because one bank's normal is another's regression."""))

question("What does the smallest isolated tenant cost to run?", 8,
 "Roughly four to six times the same customer in commercial, and almost all of it is a fixed floor: multi-AZ databases, minimum replicas, the management channel, monitoring and a backup account. We cut it by right-sizing shard descriptors after a few weeks of real traffic — about a third off a typical baseline — and fewer replicas for low-traffic L3 shards.",
 "A specific ratio, what drives it, and the levers — without arguing cost in general terms.",
 "Whether you understand cost structure, not just cost, and what it implies for the business.",
 ["How does that floor affect which customers it makes sense for?", "How often did you resize?", "Why not share more infrastructure to cut the floor?"],
 narr=dict(
  short="""Thirty seconds. Roughly four to six times what the same customer costs in multi-tenant commercial. Almost all of it is a fixed floor, not usage: multi-AZ databases, minimum replicas for every shard, the management channel, monitoring, and a backup account. We cut it by starting from commercial usage and right-sizing shard descriptors after a few weeks of real traffic, which took about a third off a typical baseline, and by running fewer replicas for low-traffic L three shards.""",
  strong="""Why it lands. It separates fixed cost from variable cost, which is the actual insight, and then gives concrete levers with a concrete effect.""",
  testing="""They're testing whether you think about cost structure. Anyone can say isolation is more expensive. The Staff answer explains why, and what that means for which customers it suits.""",
  follow="""Follow-ups. How does the floor affect fit? A small customer pays the floor whether they have fifty users or five thousand. Why not share more infrastructure to cut the floor? Because shared infrastructure is exactly what these customers can't accept. Dedicated was the requirement. The job was making dedicated as lean as possible, not less dedicated."""))
