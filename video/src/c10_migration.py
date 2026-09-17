# -*- coding: utf-8 -*-
from engine import *

chapter(10, "Migrating 178 teams, and the hard problems", "Tiers, the onboarding tool, two phases, and the migrations that nearly caught you: caches, databases, the GraphQL gateway and DataLoader.",
 """Chapter ten. Migration. This is where the project stopped being an architecture and became an execution problem across about a hundred and seventy-eight teams, none of whom reported to you. Then we'll go deep on the migrations that were genuinely hard. Not the databases people expect, but the things around them. The shared cache, data outside databases, and the hardest one of all, the GraphQL gateway and DataLoader.""")

sid = statement("How you planned it", "I didn't plan 178 migrations. I planned dependencies.",
 "The service catalogue was wrong for more services than expected — so every team got a three-question form.", kind='shared')
seg(sid, 0, """Start with the sentence that frames your planning. I didn't plan a hundred and seventy-eight migrations. I planned dependencies.""")
seg(sid, 1, """You worked with a program manager, the identity and edge leads, and the SRE lead. You started from the service catalogue, and it was wrong for more services than you expected. Dependencies had changed and nobody had updated them. So every team got a short form. What do you call? What calls you? And do you send data outside Atlassian? That form turned out to be the most useful thing produced in planning. From it came the dependency map and the tiers. Planning took about a quarter, and the order was reviewed with leadership every two weeks, because customer commitments moved, and the order had to move with them.""")

D = Diagram("The tiers: nothing moves before what it depends on")
tiers = [('L3', 'The tail · lower priority, less traffic', 'Everything else', 'com', 4),
         ('L2.5', 'Not needed by first customers — but called by L2 on common paths', 'inserted during planning', 'deny', 3),
         ('L2', 'Products the first enterprise tenants need', 'Jira · JSM · Confluence · Trello', 'dp', 2),
         ('L1', 'Near the edge · shared platform', 'shared gateway services · observability', 'cp', 1),
         ('L0', 'Foundation · migrate first', 'Identity · Global Edge', 'shared', 0)]
for k, (t, what, ex, kind, st) in enumerate(tiers):
    y = 20 + k * 150
    D.box('t' + t, 60, y, 260, 120, t, '', kind=kind, step=st, hl=str(st))
    D.label(370, y + 22, what, kind=kind, step=st, w=900, size='m')
    D.label(370, y + 66, ex, kind='neutral', step=st, w=900, size='s')
for k in range(4):
    D.arrow('t' + tiers[k + 1][0], 't' + tiers[k][0], step=max(tiers[k][4], tiers[k + 1][4]), kind='neutral', fs='t', ts='b', dashed=True)
D.zone(1300, 170, 560, 460, 'Ordering considered', kind='info', step=5)
D.label(1340, 240, '**dependency graph**\nthe only hard constraint', kind='info', step=5, w=480, size='m')
D.label(1340, 380, 'business priority\ntraffic\nrisk\noperational readiness', kind='neutral', step=5, w=480, size='m')
sid = D.build()
seg(sid, 0, """Here are the tiers, built from the bottom. L zero is the foundation, and it migrates first: identity and the Global Edge. Why? Nothing isolated works without them. No tenant can log in or reach a service. Everything else waits on L zero.""")
seg(sid, 1, """L one: services near the edge and shared platform services, like shared gateway services and observability.""")
seg(sid, 2, """L two: the major products the first enterprise tenants need. Jira, Jira Service Management, Confluence and Trello.""")
seg(sid, 3, """Then L two point five, which wasn't in the original design. It came out of planning. When you sorted services, one group didn't fit. They weren't products the first customers needed, so not L two. But several L two products called them on common paths, so they couldn't wait in the L three tail either. Rather than renumber everything, which would have broken the dashboards, alerts and runbooks already keyed to the tiers, you inserted L two point five. If an interviewer asks, isn't a half tier a sign the model was wrong? Don't get defensive. It's a sign the model met reality and you changed it cheaply.""")
seg(sid, 4, """And L three, the long tail. Lower priority, smaller share of traffic.""")
seg(sid, 5, """Now the Staff point about ordering. Five things shaped it: the dependency graph, business priority, traffic, risk and operational readiness. But only the dependency graph is a hard constraint. A pure dependency sort gives you a valid order and an unworkable plan, because it ignores whether the team at position forty has any capacity this quarter. So this was an organisational strategy, not a technical one. Say that out loud.""")

D = Diagram("The onboarding tool: five steps")
tsteps = [('1 · Readiness check', 'dependencies migrated?\nevery external destination declared?', 'shared'),
          ('2 · Starting shard descriptor', 'generated from the service descriptor\nteams review, not write', 'cp'),
          ('3 · Data transfer', 'encrypted — always', 'dp'),
          ('4 · Validate', 'ownership · counts · checksums', 'ok'),
          ('5 · Report status', 'shared dashboard\ncomputed, not self-reported', 'info')]
for k, (a, b, kind) in enumerate(tsteps):
    D.box('ts%d' % k, 60 + k * 364, 120, 330, 220, a, b, kind=kind, step=k, hl=str(k))
    if k: D.arrow('ts%d' % (k - 1), 'ts%d' % k, step=k, kind='neutral', name='ts%d' % k)
D.label(60, 50, 'runs as a step in each team’s existing deployment pipeline', kind='neutral', step=0, w=1800, size='m')
D.box('eg', 60, 420, 700, 130, 'Egress check: added later', 'after the third team got blocked at the gateway mid-testing', kind='deny', step=5, hl='5')
D.arrow('eg', 'ts0', step=5, kind='deny', fs='t', ts='b', fo=0.2, to=0.5)
D.box('res', 860, 420, 1000, 130, 'Early teams: a few weeks, with someone from the platform team', 'later waves: most teams in a few days, on their own', kind='ok', step=6)
D.label(60, 640, 'At 178 teams, every manual step becomes 178 different results.', kind='shared', step=7, w=1800, size='l', align='center')
sid = D.build()
seg(sid, 0, """Now the onboarding tool. It came from watching the first few teams. Most of their time wasn't going into hard problems. It went into the same setup work, done slightly differently each time, and slightly wrong in a different way each time. The tool took that work off them, and teams ran it as a step in their existing deployment pipeline. Step one: a readiness check. Are this service's dependencies already migrated? And has the team declared every external destination it sends data to?""")
seg(sid, 1, """Step two: it generated a starting shard descriptor from the service's existing service descriptor. So teams reviewed a file instead of writing one. That's a small thing that removes a lot of friction.""", travel=travel(D.paths['ts1'], 'cp'))
seg(sid, 2, """Step three: it ran the data transfer, and every transfer was encrypted. So no team had to get encryption right on its own. Encrypting in the tool made it one platform guarantee instead of a hundred and seventy-eight separate promises, one of which someone would eventually get wrong.""", travel=travel(D.paths['ts2'], 'dp'))
seg(sid, 3, """Step four: validate the result. Ownership, counts and checksums.""", travel=travel(D.paths['ts3'], 'ok'))
seg(sid, 4, """Step five: report status to a shared dashboard. And that status was computed by the tool from its own checks, not reported by teams. Because self-reported status was always greener than reality.""", travel=travel(D.paths['ts4'], 'info'))
seg(sid, 5, """Here's an honest detail that makes the story credible. The first version of the tool didn't have the egress check. You added it after the third team got blocked at the gateway halfway through testing. Their services sent data to places they'd never written down. The gateway was doing its job, but it cost those teams days.""")
seg(sid, 6, """And the effect. The early teams took a few weeks, with someone from your team working alongside them. By the later waves, most teams got through in a few days, on their own.""")
seg(sid, 7, """The principle underneath it: at a hundred and seventy-eight teams, every manual step becomes a hundred and seventy-eight different results. Automation here wasn't about speed. It was about consistency.""")

sid = compare("Two phases, two different problems",
 ("Phase one · an engineering problem", 'dp', 0, ["L0, L1, and the L2 products the first customers needed", "Pilot: a large bank, cutover rehearsed twice in staging", "Rehearsal exposed stale tenant context", "Before phase two: invalidation step, egress in readiness, shared dashboard"]),
 ("Phase two · an adoption problem", 'shared', 1, ["L2.5 and the L3 tail — more teams, smaller services", "Expected faster. Took about as long as phase one.", "Other priorities; services with no owner after reorgs", "Office hours · status visible to leadership · chasing owners · fix common blockers once"]))
seg(sid, 0, """The migration ran in two phases, and the most useful thing you can say is that they were different kinds of problem. Phase one was L zero, L one, and the L two products the first customers needed. It started with a pilot customer, a large bank. You rehearsed their cutover twice in staging before touching production, and the stale tenant context problem showed up in the first rehearsal. That's exactly what rehearsals are for. Before opening phase two, you changed three things: cache invalidation became an explicit switch step, egress declarations became part of the readiness check, and every team's status went onto the shared dashboard.""")
seg(sid, 1, """Phase two was L two point five and the L three tail. More teams, smaller services, less traffic each. You assumed it would be faster. It wasn't. It took about as long as phase one. Because phase one was an engineering problem, and phase two was an adoption problem. Teams had other priorities, and some services had no real owner left after reorganisations. You found a few of those only because the readiness check failed on a dependency nobody claimed. What moved the tail was unglamorous: weekly office hours, publishing every team's status to leadership so priorities were visible, chasing owners for orphaned services, and fixing common blockers once in the platform instead of team by team. Admitting that your estimate was wrong, and explaining why, is a very strong answer.""")

sid = statement("Now the hard problems", "Moving a tenant sounds like moving rows.",
 "In practice the tenant's data lived in four kinds of place — a shared cache, files and derived data, shared databases, and the GraphQL gateway's call graph — and each broke in its own way.", kind='deny')
seg(sid, 0, """Now the hard problems. Moving a tenant sounds like moving rows.""")
seg(sid, 1, """In practice, the tenant's data and dependencies lived in several kinds of place, and each one broke in its own way. The distributed cache. Data that isn't in a database. The databases themselves. And the GraphQL gateway's call graph. The data moves people ask about are the databases. The ones that nearly caught you were everything around them.""")

D = Diagram("Hard problem 1: the distributed cache")
D.zone(60, 20, 820, 560, 'Commercial: one shared cache', kind='com', step=0)
keys = ['issue:48213', 'tenantB:page:77', 'issue:90412', 'user:5521', 'tenantA:proj:12', 'issue:11873']
for k, key in enumerate(keys):
    D.box('k%d' % k, 110 + (k % 2) * 380, 90 + (k // 2) * 130, 340, 100, key, 'no tenant in key' if not key.startswith('tenant') else '', kind='deny' if not key.startswith('tenant') else 'com', step=0, small=True, hl='1' if not key.startswith('tenant') else None)
D.label(110, 500, 'Cached copies stay behind — and can’t all be found.', kind='deny', step=1, w=740, size='m')
D.zone(1000, 20, 860, 560, 'Isolated: a dedicated cache per shard', kind='ok', step=2)
D.box('ic', 1050, 90, 760, 120, 'Tenant context required in every key', 'enforced by the platform cache client · readiness check fails keys without it', kind='ok', step=2, small=True)
D.box('warm', 1050, 250, 760, 110, 'Pre-warmed during catch-up', "from the tenant's hottest keys", kind='info', step=3, small=True)
D.box('only', 1050, 400, 760, 130, 'Cache-only state found', 'readiness check flagged it · moved to a real store first', kind='shared', step=4, small=True)
D.label(60, 650, 'Old entries: unreachable once the tenant is locked, drained on expiry.', kind='neutral', step=5, w=1800, size='m', align='center')
D.label(60, 720, 'The trap: migrate the database, forget the cache. The data leaves; its copies stay.', kind='deny', step=5, w=1800, size='l', align='center')
sid = D.build()
seg(sid, 0, """Hard problem one, the distributed cache. In commercial, one shared cache held entries for every tenant, side by side. And customer data in a shared cache is customer data in shared infrastructure. Moving the database isn't enough.""")
seg(sid, 1, """Here's what made it hard. Many keys didn't carry the tenant. They were keyed by entity ID alone. Issue four eight two one three. Whose is that? There was no way to find all of this tenant's entries. So when the tenant's database moved, its cached copies stayed behind, and you couldn't even enumerate them.""")
seg(sid, 2, """What you did. Every isolated shard got its own dedicated cache. Nothing tenant-specific lives in a shared cache. And the platform cache client requires tenant context in every key. The readiness check fails any key without it.""")
seg(sid, 3, """Second problem: the isolated cache is empty at the exact moment of cutover. Every read would hit a freshly migrated database at once. So you pre-warmed the isolated cache from the tenant's hottest keys during catch-up.""")
seg(sid, 4, """Third: some services quietly used the cache as their only store. That state existed nowhere else, so there was nothing to copy from a database. The readiness check flagged cache-only state, and it moved to a real store before those services could migrate.""")
seg(sid, 5, """And the old entries you couldn't find? Once the tenant was locked, they became unreachable, and drained on expiry. The trap to name in an interview: migrating the database and forgetting the cache. The data leaves. Its copies stay.""")

sid = table("Hard problem 2: data that isn't in a database", ["Kind of data", "What made it hard, and what we did"], [
 (0, ["Attachments and files", "Rows point at files. Copy rows first and they point at nothing. Files copied **before** the rows that reference them; validation checks every reference resolves."]),
 (1, ["Encrypted data", "Customer's own keys — nothing copied byte for byte. Encrypted transfer, **re-encrypted under the tenant's keys** on arrival."]),
 (2, ["Search indexes and aggregates", "Not copied — risks other tenants' entries and stale state. **Rebuilt** from migrated source. Slower, so it had to finish before the switch."]),
 (3, ["Links inside content", "Absolute links to the old commercial site. Rewritten during migration; old URLs redirect. **Entity IDs unchanged**, so references and bookmarks resolve."]),
], widths=[26, 74])
seg(sid, 0, """Hard problem two: data that isn't in a database. Attachments and files first. Rows point at files. If you copy the rows first, they point at nothing. So files were copied before the rows that reference them, and validation checked that every reference resolves. Ordering by dependency, again, just at the data level.""")
seg(sid, 1, """Encrypted data. Isolated data at rest uses the customer's own keys, so nothing could be copied byte for byte. Data moved over an encrypted transfer and was re-encrypted under the tenant's keys on arrival.""")
seg(sid, 2, """Search indexes and aggregates were not copied at all. Copying an index risks carrying other tenants' entries and stale state. They were rebuilt inside the isolated environment from the migrated source data. Rebuilding is slower, so it had to finish before the switch. That's a nice trade to mention: slower, but it can't leak.""")
seg(sid, 3, """And links inside content. Pages and work items contain absolute links to the old commercial site. Isolated tenants have their own domain. So embedded links were rewritten during migration, and old URLs redirect. Entity IDs stayed the same, so references and bookmarks still resolve. This is the kind of detail that only someone who ran a real migration would think to mention.""")

D = Diagram("Hard problem 3: tenancy isn't on every table")
chain = [('Comment', 'no tenant column', 'deny'), ('Work item', 'no tenant column', 'deny'), ('Project', 'no tenant column', 'com'), ('Tenant', 'the tenancy root', 'ok')]
for k, (a, b, kind) in enumerate(chain):
    D.box('c%d' % k, 60 + k * 470, 60, 400, 130, a, b, kind=kind, step=0 if k < 3 else 1, hl='1' if k == 3 else None)
    if k: D.arrow('c%d' % (k - 1), 'c%d' % k, step=0 if k < 3 else 1, kind='neutral', name='j%d' % k)
D.label(60, 215, 'each arrow: **belongs to**', kind='neutral', step=0, w=1800, size='s', align='center')
D.label(60, 262, 'Miss a join path → lose rows, **or copy someone else’s**.', kind='deny', step=1, w=1800, size='m', align='center')
D.box('fix', 60, 340, 1800, 130, 'Each service declared its tenancy root and the join path for every table', 'readiness check fails any table without one · ownership check runs after every copy', kind='ok', step=2)
D.zone(60, 540, 880, 280, 'Deletes hide during catch-up', kind='deny', step=3)
D.label(100, 600, 'Row deleted after the bulk copy never appears as “updated”.\nIt silently survives in isolated.', kind='deny', step=3, w=800, size='m')
D.label(100, 720, '**Fix:** catch-up reads a change log that records deletes.\nCounts + checksums at the freeze catch anything missed.', kind='ok', step=3, w=800, size='m')
D.zone(980, 540, 880, 280, 'IDs collide', kind='deny', step=4)
D.label(1020, 600, 'Sequences were shared across tenants. The first new row\nin isolated can reuse an existing ID.', kind='deny', step=4, w=820, size='m')
D.label(1020, 720, '**Fix:** start sequences above the migrated maximum\nbefore the first write; validation checks it.', kind='ok', step=4, w=820, size='m')
sid = D.build()
seg(sid, 0, """Hard problem three: the databases. They were shared, and never designed to be split by tenant. And tenancy isn't on every table. A comment belongs to a work item. A work item belongs to a project. None of those rows carry the tenant directly.""", travel=travel(D.paths['j1'] + D.paths['j2'][1:], 'neutral'))
seg(sid, 1, """Only the project leads to the tenant. So if you miss a join path, you either lose rows, or you copy someone else's. And copying someone else's rows into an isolated environment is worse than any outage.""", travel=travel(D.paths['j3'], 'ok'))
seg(sid, 2, """So each service declared its tenancy root and the join path for every table. The readiness check failed any table without one, and the ownership check ran after every copy.""")
seg(sid, 3, """Next, deletes hide during catch-up. Your first catch-up design looked for updated rows. But a row deleted after the bulk copy never shows up as changed. It silently survives in isolated. So catch-up switched to reading a change log that records deletes, and counts and checksums at the freeze catch anything missed. Admitting your first design had this flaw is a strength. It's the kind of bug you only find by doing it.""")
seg(sid, 4, """And ID collisions. IDs came from sequences shared across tenants. The first new row written in isolated could reuse an ID that already exists. So before the first write, sequences in the isolated database start above the migrated maximum, and validation checks it.""")

sid = table("Three more database problems", ["Why it was hard", "What we did"], [
 (0, ["The schema moves while you copy. A change halfway through leaves the copy on the wrong version.", "Schema version pinned for the tenant's migration window; isolated shard runs the same version. A change restarts catch-up for affected tables."]),
 (1, ["The migration can hurt everyone else. Extraction reads hit databases serving thousands of tenants.", "Extraction against read replicas, rate-limited, paused automatically if commercial latency rose."]),
 (2, ["One tenant, many databases, one switch. Tenant context flips for the whole tenant.", "A per-tenant switch gate: every service copied, caught up and validated. One red service holds the whole tenant."], [None, 'ok']),
], widths=[48, 52])
seg(sid, 0, """Three more database problems. The schema moves while you copy. Services deploy all the time, and a schema change halfway through leaves the copy on the wrong version. So the schema version is pinned for the tenant's migration window, and the isolated shard runs the same version. If a schema change happens during the copy, catch-up restarts for the affected tables.""")
seg(sid, 1, """The migration can hurt everyone else. Extraction reads hit databases serving thousands of other tenants. So extraction ran against read replicas, rate-limited, and paused automatically if commercial latency rose. Protecting the customers who aren't migrating is a very Staff-level consideration.""")
seg(sid, 2, """And one tenant, many databases, one switch. Tenant context flips for the whole tenant at once, so every service's data must be ready at the same moment. A per-tenant switch gate: every service copied, caught up and validated before the flip. One red service holds the whole tenant. Here's your line for all of this: it wasn't a database copy. It was a tenant-shaped extraction from databases that were never designed to be split, while they were still being written to.""")

# ---- GraphQL
D = Diagram("The hardest one: the GraphQL gateway")
D.box('q', 60, 60, 340, 120, 'One product query', '', kind='info', step=0)
D.box('gw', 540, 40, 460, 160, 'GraphQL gateway', 'built on Nadel · in front of nearly every request', kind='shared', step=0, hl='0')
svcs = [('Jira service', 'dp'), ('Identity service', 'dp'), ('Confluence service', 'dp'), ('Media service', 'dp')]
for k, (n, kind) in enumerate(svcs):
    D.box('s%d' % k, 1180, 20 + k * 130, 460, 105, n, 'isolated shard', kind=kind, step=0, small=True)
    D.arrow('gw', 's%d' % k, step=0, kind='dp', fs='r', ts='l', fo=0.2 + 0.2 * k, name='f%d' % k)
D.arrow('q', 'gw', step=0, kind='info', name='q-g')
D.label(60, 260, 'Every other service is **one box** on the dependency map.\nThe gateway is **every edge** at once.', kind='shared', step=1, w=1000, size='m')
D.zone(60, 560, 860, 270, 'Option: shared gateway, routing per tenant', kind='deny', step=2)
D.label(100, 620, 'Isolated query results — customer data —\npass through shared infrastructure.\nOne routing bug calls a commercial backend.', kind='deny', step=2, w=780, size='m')
D.zone(1000, 560, 860, 270, 'Chosen: a gateway inside each isolated environment', kind='ok', step=3)
D.label(1040, 620, 'Results never leave the boundary.\nBackend endpoints only resolve to isolated shards.\nCost: many gateway runtimes, each composing a schema.', kind='ok', step=3, w=800, size='m')
sid = D.build()
seg(sid, 0, """And now the hardest one: the GraphQL gateway. Nadel is Atlassian's GraphQL engine. It combines many backend GraphQL services into one API. The gateway built on it sits in front of nearly every product request. One query arrives, and the gateway fans it out to many backend services. For an isolated tenant, every one of those calls has to land on that tenant's isolated shards.""",
    travel=travel(D.paths['q-g'] + D.paths['f2'][1:], 'info'))
seg(sid, 1, """Here's the sentence that explains why it was the hardest. Every other service is one box on the dependency map. The gateway is every edge of the map at once. One wrong call breaks both isolation guarantees. In commercial it was one gateway for every tenant, an L one service.""")
seg(sid, 2, """The first decision: where does the gateway run? Option one, keep a shared gateway that routes per tenant. The problem: isolated query results, which are customer data, would pass through shared infrastructure. And one routing bug calls a commercial backend.""")
seg(sid, 3, """So the gateway runs inside each isolated environment. Query results never leave the boundary, and backend endpoints only resolve to isolated shards. The cost: many gateway runtimes, each composing its own schema. Notice this is a boundary decision, not a deployment choice. Frame it that way.""")

D = Diagram("Hydration is a hidden call")
D.box('gw', 60, 120, 440, 150, 'Gateway', 'hydration config', kind='shared', step=0)
D.box('a', 760, 20, 460, 130, 'Service A', 'returns comment with authorId', kind='dp', step=0)
D.box('b', 760, 260, 460, 130, 'Service B', 'fills in the author', kind='dp', step=1, hl='1')
D.arrow('gw', 'a', step=0, kind='dp', fo=0.3, to=0.5, via=[(630, 165), (630, 85)], name='g-a')
D.arrow('gw', 'b', step=1, kind='deny', fo=0.75, to=0.5, via=[(630, 232), (630, 325)], name='g-b')
D.label(60, 290, 'the **gateway** makes the call to B', kind='deny', step=1, w=560, size='s')
D.label(1300, 60, 'A’s dependency list:\n  nothing about B', kind='neutral', step=2, w=560, size='m')
D.label(1300, 270, 'Readiness check on A\ncan’t see this call.', kind='deny', step=2, w=560, size='m')
D.box('fix1', 60, 480, 880, 190, 'Readiness covers the hydration graph', 'a hydration target missing in isolated → schema composition fails at build time, not at runtime in front of a customer', kind='ok', step=3)
D.box('fix2', 980, 480, 880, 190, 'Schema composed per isolated environment', "only from services actually present · missing features' fields don't exist · config pushed in at deploy time, never pulled", kind='ok', step=4)
D.label(60, 740, 'The dependency lived in gateway configuration, not in any service’s code. That’s why it was a platform problem.', kind='shared', step=5, w=1800, size='m', align='center')
sid = D.build()
seg(sid, 0, """Then hydration bit you, in planning. Here's how hydration works. The gateway calls service A, which returns, say, a comment with an author ID.""", travel=travel(D.paths['g-a'], 'dp'))
seg(sid, 1, """And to fill in the author, the gateway calls service B. Service A never calls B. The gateway does.""", travel=travel(D.paths['g-b'], 'deny'))
seg(sid, 2, """So look at service A's own dependency list. Nothing about B. Which means a readiness check on A's dependencies can't see this call at all. If B doesn't exist in the isolated environment yet, the obvious endpoint left is commercial.""")
seg(sid, 3, """The fix: the readiness check was extended to cover the gateway's hydration graph. If any hydration target doesn't exist in the isolated environment, schema composition fails at build time, not at runtime in front of a customer.""")
seg(sid, 4, """And the schema is composed per isolated environment, only from the services actually present. A missing feature's fields simply don't exist there, instead of quietly calling commercial. Frontend teams handled absent capabilities explicitly, so one missing field didn't fail a whole page. And one more boundary detail: in commercial, the gateway pulled service schemas and config from shared services at runtime. Inside isolated, that pull is a call across the boundary. So the control plane pushes the composed schema and config in at deploy time. Pushed in, never pulled out.""")
seg(sid, 5, """The takeaway: the dependency lived in gateway configuration, not in any service's code. That's exactly why it had to be solved by the platform. No individual team could have found it.""")

# ---- DataLoader
D = Diagram("DataLoader: the part that almost broke the guarantees")
D.zone(60, 20, 820, 400, 'Request thread', kind='info', step=0)
D.box('rq', 110, 90, 720, 110, 'Query for 50 comments', 'tenant context: Tenant A', kind='info', step=0, small=True)
D.box('ld', 110, 250, 720, 110, 'DataLoader queues 50 author keys', 'batched: one call, not fifty', kind='info', step=0, small=True)
D.arrow('rq', 'ld', step=0, kind='info', fs='b', ts='t')
D.zone(1000, 20, 860, 400, 'Batch runs later, on another thread', kind='deny', step=1)
D.box('bt', 1050, 90, 760, 110, 'Batch function', 'tenant context: — missing —', kind='deny', step=1, small=True, hl='1')
D.box('def', 1050, 250, 760, 110, 'Default endpoint', 'commercial  →  that is a fallback', kind='deny', step=2, small=True, hl='2')
D.arrow('ld', 'bt', step=1, kind='deny', dashed=True, fo=0.5, to=0.5, via=[(940, 305), (940, 145)], name='l-b')
D.arrow('bt', 'def', step=2, kind='deny', fs='b', ts='t', name='b-d')
D.label(60, 450, 'Caught in the first isolated test tenant — because we checked **where every downstream call went**, not only what came back.', kind='ok', step=3, w=1800, size='m', align='center')
fixes = [('Context captured into the loader', 'at creation, per request · passed to the batch explicitly · missing → fail closed'),
         ('Loaders strictly per request', 'longer-lived loaders could mix two customers’ keys in one call · less batching accepted'),
         ('DataLoader cache per request only', 'keyed by entity id · anything longer-lived → tenant-keyed platform cache')]
for k, (a, b) in enumerate(fixes):
    D.box('fx%d' % k, 60 + k * 610, 560, 580, 220, a, b, kind='ok', step=4 + k, hl=str(4 + k))
sid = D.build()
seg(sid, 0, """And DataLoader, the part that almost broke the guarantees. DataLoader turns the many small lookups in a query into a few batched calls, and hydration relies on it. A query for fifty comments needs fifty authors. DataLoader queues the fifty author keys and makes one call instead of fifty. On the request thread, tenant context is right there: tenant A.""")
seg(sid, 1, """But the batch runs later, asynchronously, often on another thread. And in your first isolated test tenant, tenant context didn't make it onto that thread. So the batch function didn't know which tenant's shard to call.""", travel=travel(D.paths['l-b'], 'deny'))
seg(sid, 2, """And the default endpoint it would have used was commercial. Think about what that is. It's a fallback. Exactly the thing guarantee one says must be impossible, hidden inside a batching library.""", travel=travel(D.paths['b-d'], 'deny'))
seg(sid, 3, """How did you catch it? Because you were checking where every downstream call went, not just whether the query returned the right data. Here's the trap to name: a query can return exactly the right answer while one hydration call quietly went to commercial. Test where calls go, not only what comes back.""")
seg(sid, 4, """Three fixes. First, tenant context is captured into the loader when it's created for the request, and passed to the batch function explicitly. A batch with no tenant context fails closed.""")
seg(sid, 5, """Second, a few loaders had been made to live longer than one request to squeeze out more batching. That can put two customers' keys into one downstream call. So loaders became strictly per request. A batch only ever holds one tenant's keys. You gave up a little batching efficiency, and you'd make that trade again every time.""")
seg(sid, 6, """Third, DataLoader caches by entity ID. Inside one request, that's fine. Any cache that outlives the request can hand one tenant's object to another. So DataLoader caches stay per request, and anything longer-lived goes through the tenant-keyed platform cache. Notice how the cache lesson from hard problem one shows up again here. Connecting those two in an interview shows you see the pattern, not just the incidents.""")

sid = cards("How you proved it worked for a tenant", [
 (0, "Replayed recorded query shapes", "Not customer data. Against an isolated test tenant, compared with commercial on the same test data.", 'info'),
 (1, "Checked where every call went", "Egress denials and the commercial-side alert both had to read zero.", 'ok'),
 (2, "Watched batch counts and latency", "So per-request, per-tenant batching didn't quietly make pages slower.", 'shared'),
], cols=3, note=(3, "Test where calls go, not only what comes back."))
seg(sid, 0, """Finally, how you proved it worked. You replayed recorded query shapes, not customer data, against an isolated test tenant, and compared results with commercial on the same test data.""")
seg(sid, 1, """You checked where every downstream call went. Egress denials and the commercial-side alert both had to read zero.""")
seg(sid, 2, """And you watched batch counts and latency, so per-request, per-tenant batching didn't quietly make pages slower.""")
seg(sid, 3, """And the principle, one more time, because it's a great closing line for this topic: test where calls go, not only what comes back.""")

question("What was the hardest technical problem in the migration?", 10,
 "The GraphQL gateway, built on Nadel. Every other service is one box on the dependency map; the gateway is every edge at once. We ran it inside each isolated environment, extended readiness to its hydration graph so a missing target fails at build time, and fixed DataLoader losing tenant context on the batch thread — where the default endpoint was commercial.",
 "It says why it was harder than the others, then gives three concrete, layered problems and fixes.",
 "Whether your ‘hardest problem’ is genuinely hard, and whether you can go deep without losing the thread.",
 ["Why didn't you keep one shared gateway?", "Why didn't normal testing catch the DataLoader issue?", "What did per-request loaders cost in latency?"],
 answer_long="Add the proof: replayed recorded query shapes against an isolated test tenant, and checked where every downstream call went — egress denials and the commercial-side alert had to read zero.",
 narr=dict(
  short="""Thirty seconds. The GraphQL gateway, built on Nadel. It sits in front of nearly every product request, and one query fans out to many services. Every other service is one box on the dependency map. The gateway is every edge of it at once. We ran the gateway inside each isolated environment, extended the readiness check to its hydration graph so a missing target fails at build time, and fixed DataLoader losing tenant context on the batch thread, where the default endpoint was commercial.""",
  long="""For the longer version, add how you proved it. We replayed recorded query shapes, not customer data, against an isolated test tenant and compared with commercial. And we checked where every downstream call went. Egress denials and the commercial-side alert both had to read zero. A query can return the right answer while one call quietly went to commercial.""",
  strong="""Why it lands. It justifies why this problem was harder than the others, with the one-box versus every-edge line, instead of just asserting it. Then it layers three problems, each with a fix.""",
  testing="""They're testing whether your hardest problem is actually hard, and whether you can go five levels deep and still come back to the point. This one can go very deep, so keep the thirty-second version tight and let them pull.""",
  follow="""Expect: why not one shared gateway? Query results are customer data, and one routing bug calls commercial. Why didn't normal testing catch DataLoader? Because normal testing checks what comes back, not where calls go. And the latency cost of per-request loaders: stay honest. You accepted slightly less batching, and you watched batch counts and latency so it didn't quietly slow pages. Don't invent a percentage."""))

question("How did you copy one tenant out of shared databases?", 8,
 "Each service owner wrote the tenant-scoped extraction, because only they know their schema, declaring the join path from every table to its tenancy root. The platform ran the encrypted transfer and checked every copied record belonged to that tenant, plus counts and checksums. Catch-up read a change log so deletes weren't missed.",
 "It splits ownership correctly between teams and platform, and covers both failure directions.",
 "Whether you understand that copying too much is worse than copying too little.",
 ["What if the ownership check failed?", "How did catch-up handle deletes?", "How did you avoid ID collisions?"],
 narr=dict(
  short="""Thirty seconds. Each service owner wrote the tenant-scoped extraction, because only they know their schema, and they declared the join path from every table to its tenancy root. The platform ran the encrypted transfer and checked that every copied record belonged to that tenant, alongside counts and checksums. And catch-up read a change log that records deletes, so rows deleted after the bulk copy didn't silently survive.""",
  strong="""Why it lands. It splits ownership sensibly: schema knowledge stays with teams, guarantees stay with the platform. And it covers both failure directions. Copy too little and you lose data. Copy too much and another customer's data is inside someone else's isolated environment.""",
  testing="""They're testing whether you know which failure is worse. Most people only worry about losing data. The Staff answer says leaking another tenant's data is worse than any outage.""",
  follow="""Follow-ups. If the ownership check failed, the tenant doesn't switch. Validation gates the switch, and one red service holds the whole tenant. Deletes: the change log. ID collisions: sequences start above the migrated maximum before the first write."""))
