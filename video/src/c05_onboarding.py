# -*- coding: utf-8 -*-
from engine import *

chapter(5, "Onboarding a tenant, end to end", "How the control plane builds an isolated environment, and how an existing customer moves in without losing a write.",
 """Chapter five. Onboarding a tenant, end to end. There are really two flows here, and interviewers often blur them, so keep them separate in your head. First, how a brand new isolated environment gets built. Second, how an existing commercial customer's data moves into it. We'll animate both.""")

sid = cards("Provisioning is declarative", [
 (0, "A versioned spec per environment", "region · accounts · IP ranges · data stores · keys · shard descriptors", 'cp'),
 (1, "Every step: “make sure this exists and matches”", "Not “create this”. So a rerun resumes instead of duplicating.", 'ok'),
], cols=1, note=(2, "Pilot bank: about **two days**, mostly manual checks. By phase two: about **five hours**, hands off."))
seg(sid, 0, """Start with the mindset, because it's the thing an infra interviewer is really probing. Provisioning is declarative. The control plane holds a versioned spec for each environment: the region, the accounts, the IP ranges, the data stores, the keys, and the shard descriptors. The workflow's job is to drive reality toward that spec.""")
seg(sid, 1, """And every step is written as make sure this exists and matches, not create this. That sounds like a small wording choice. It isn't. It means that if provisioning fails halfway, you rerun it and it resumes from where it stopped, instead of creating duplicates or leaving orphaned resources. Idempotent, resumable steps are the Staff-level answer to what happens when provisioning fails.""")
seg(sid, 2, """And the timing, which you should know cold. The first environment, for the pilot bank, took about two days, mostly manual checks between steps. By phase two, a new environment took around five hours end to end, hands off. Most of those five hours are creating multi-availability-zone databases and the first deploy of every shard.""")

D = Diagram("Building a new isolated environment")
D.box('spec', 60, 10, 840, 90, 'Control plane · versioned environment spec', 'drives reality toward the spec, step by step', kind='cp', step=0)
steps = [
 ('0 · Quota check', 'fail fast, before anything exists', 'cp'),
 ('1 · Claim account set', 'minutes, from a pre-built pool', 'cp'),
 ('2 · Guardrails + baseline', 'logging · network baseline', 'cp'),
 ('3 · IP ranges + VPC', 'across 3 availability zones', 'cp'),
 ('4 · Management channel', 'one-way private endpoint', 'cp'),
 ('5 · Verify key grant', 'the most common stall', 'deny'),
 ('6 · Databases + storage', 'multi-AZ · about two hours', 'cp'),
 ('7 · Deploy shards', 'L0 → L1 → L2 · about two hours', 'cp'),
 ('8 · Verify health', 'end to end', 'cp'),
 ('9 · Register in Tenant Context', 'only now can traffic arrive', 'ok'),
]
for k, (t, s, kind) in enumerate(steps):
    col, row = k // 5, k % 5
    D.box('p%d' % k, 60 + col * 430, 125 + row * 108, 410, 92, t, s, kind=kind, step=k, hl=str(k), small=True)
D.zone(980, 20, 880, 700, 'Isolated environment · dedicated OU + accounts', kind='dp', step=1)
D.label(1010, 60, 'guardrails · logging · network baseline applied', kind='dp', step=2, w=820, size='s')
D.box('vpc', 1010, 100, 820, 80, 'VPC across 3 availability zones', 'non-overlapping range from the address manager', kind='dp', step=3, small=True)
D.box('ep', 1010, 205, 380, 90, 'Private endpoint', 'control plane connects in, one way', kind='cp', step=4, small=True)
D.arrow('spec', 'ep', step=4, kind='cp', fs='r', ts='l', fo=0.5, via=[(940, 55), (940, 250)], dashed=True, name='cp-ep')
D.box('reg', 1410, 205, 420, 90, 'Registered in Tenant Context', 'the Router can now route here', kind='ok', step=9, hl='9', small=True)
D.box('db', 1010, 320, 820, 90, 'Dedicated databases + storage', 'multi-AZ', kind='dp', step=6, small=True)
for k, lvl in enumerate(('L0 shards', 'L1 shards', 'L2 product shards')):
    D.box('sh%d' % k, 1010 + k * 280, 435, 260, 100, lvl, ('identity, edge', 'shared platform', 'Jira, JSM, Confluence')[k], kind='dp', step=7, small=True)
D.label(1010, 560, '✓ health verified end to end', kind='ok', step=8, w=390, size='m')
D.box('keys', 1420, 610, 410, 90, 'Customer-managed keys', 'grant verified', kind='deny', step=5, hl='5', small=True)
D.box('cust', 60, 690, 840, 100, "Customer's own AWS account · KMS keys", 'grants encrypt + decrypt on specific keys', kind='deny', step=5, small=True)
D.arrow('cust', 'keys', step=5, kind='deny', fs='r', ts='b', via=[(1625, 740)], name='cust-k')
sid = D.build()
P = D.paths
seg(sid, 0, """Here's the pipeline, step by step, and watch the right-hand side assemble as each step completes. On the left is the control plane with the versioned spec. Step zero is a quota check. Before anything is created, the workflow checks the AWS quotas it will need. Why first? Because early in phase one, a shard deploy failed halfway through when a fresh account hit its database instance quota. A quota check up front turns a half-built environment into a clean, early failure.""")
seg(sid, 1, """Step one claims a set of AWS accounts. This is where the dedicated organizational unit and accounts come from. It takes minutes, not days, because the platform keeps a pool of accounts that are already baselined and already have their quotas raised. Creating accounts and raising quotas from scratch can take days, so you pay that cost ahead of demand.""")
seg(sid, 2, """Step two applies guardrails, logging and the network baseline to those accounts. Nothing customer-specific yet. This is making the empty environment safe and observable before anything goes into it.""")
seg(sid, 3, """Step three allocates IP ranges and builds the VPC across three availability zones. The ranges come from a central address manager: a slash twenty by default, a slash nineteen for large tenants, carved from a range reserved only for isolated environments. They never overlap, even though environments never talk to each other, because flow logs, security tooling and incident debugging all key on addresses.""")
seg(sid, 4, """Step four opens the management channel. Watch the direction of that arrow. The control plane never gets a network route into the environment. The environment exposes one private endpoint that only the control plane's account may connect to, and connections open from the control plane side only. The environment can't start anything back over it. This is how you answer the question, how do you deploy into an environment that has no route to commercial.""",
    travel=travel(P['cp-ep'], 'cp'))
seg(sid, 5, """Step five verifies the customer's key grant, and this is the step to remember, because it was the most common stall, and it wasn't Atlassian's fault. The encryption keys live in the customer's own AWS account, and the customer grants encrypt and decrypt on specific keys. If their key policy is missing one permission, step five fails. The fix was twofold: make that failure name the exact missing permission, and give customers a pre-check to run before they hand over their keys. The Staff-level point here is recognising a dependency you don't control, and designing the failure to be actionable for someone outside your team.""",
    travel=travel(P['cust-k'], 'deny'))
seg(sid, 6, """Step six creates the dedicated databases and storage, across availability zones. This is one of the two slow steps, about two hours.""")
seg(sid, 7, """Step seven deploys the shards, in tier order. L zero first, the foundations like identity and the edge. Then L one, the shared platform services. Then L two, the products this customer actually uses. That order isn't cosmetic. Nothing can come up before what it depends on. This is the other slow step, also about two hours.""")
seg(sid, 8, """Step eight verifies health, end to end. Not just, did every step succeed, but does the environment actually work as a whole.""")
seg(sid, 9, """And step nine, last, registers the environment in Tenant Context. Only now can traffic arrive, because only now can the Router route this tenant here. Here's the principle to say out loud. Register last. Nothing is registered until verification passes, so a half-built environment can never receive traffic. If an interviewer asks what stops a broken environment from serving customers, this ordering is your answer.""")

sid = table("What makes the pipeline safe", ["Choice", "Why"], [
 (0, ["Pre-built account pool", "Account creation and quota increases can take days; claiming takes minutes"]),
 (1, ["Quota check first", "A phase-one deploy failed halfway on a database-instance quota"]),
 (2, ["Resumable steps", "A failure leaves “failed at step N”; rerunning continues from there"]),
 (3, ["Register last", "A half-built environment can never receive traffic"], [None, 'ok']),
 (4, ["Drift reconciliation", "Scheduled re-check against the spec; repaired or paged, never silently kept"]),
], widths=[30, 70])
seg(sid, 0, """Let's collect the five design choices that make that pipeline production-safe, because an infra panel will ask about each of them. A pre-built account pool, because creating accounts and raising quotas can take days.""")
seg(sid, 1, """A quota check first, because of that real phase-one failure. Always tie a design choice to the event that caused it. It's far more convincing than a best practice.""")
seg(sid, 2, """Resumable steps. A failure leaves the environment marked failed at step N, and rerunning continues from there.""")
seg(sid, 3, """Register last, so a half-built environment can never receive traffic.""")
seg(sid, 4, """And drift reconciliation. The control plane re-checks every environment against its spec on a schedule. If someone changes something out of band, it's either repaired or someone is paged. It's never silently kept. A likely follow-up is, what happens if someone changes a resource by hand? This is the answer.""")

sid = table("Moving an existing customer: the options", ["Option", "What it means", "Verdict"], [
 (0, ["Start fresh", "Customers re-import their own data", "Pushes our risk onto customers with years of history"], [None, None, 'deny']),
 (1, ["Move whole databases", "Lift the stores across as they are", "Impossible: a shared store holds thousands of tenants"], [None, None, 'deny']),
 (2, ["Dual-write", "Write to both environments during transition", "Both look authoritative; keeps the tenant wired to commercial"], [None, None, 'deny']),
 (3, ["Copy, then switch", "Copy one tenant, then flip its tenant context", "One authoritative home at every moment. Chosen."], [None, None, 'ok']),
], widths=[20, 34, 46])
seg(sid, 0, """Now the second flow: an existing commercial customer moving in. Their data already lives in shared, multi-tenant stores. So the first decision isn't how to copy data. It's whether to copy it at all. Option one, start fresh and have customers re-import. That was out quickly. These customers had years of history, permissions and audit trails. Asking a bank to re-import all of that just moves your risk onto them.""")
seg(sid, 1, """Option two, move whole databases. Impossible. A shared store holds thousands of tenants. There's no such thing as moving one customer's database.""")
seg(sid, 2, """Option three, dual-write to both environments during the transition. It looks attractive, especially for rollback. But it changes the write path in every migrating service, for a while both environments look authoritative, and it keeps the isolated tenant wired to commercial, which is exactly what you're trying to end. If an interviewer asks why not dual-write, that last reason is your strongest one.""")
seg(sid, 3, """Option four, copy, then switch. Copy one tenant's data across, then flip its tenant context. That was the choice, because at every moment the tenant has exactly one authoritative home.""")

sid = statement("The rule", "A tenant has one home at a time.", "Commercial until the switch. Isolated after it. Never both. That's also what makes “no fallback” possible.", kind='ok')
seg(sid, 0, """So here's the rule, and it's worth repeating in every review, exactly as you did. A tenant has one home at a time.""")
seg(sid, 1, """Commercial until the switch, isolated after it, never both. And notice what that rule buys you later. Because there's never a second live copy, there's nothing to fall back to. The no-fallback guarantee in the failures chapter isn't a separate idea. It grows directly out of this rule.""")

D = Diagram("Copy, then switch — one tenant")
D.zone(60, 150, 560, 460, 'Commercial · shared', kind='com', step=0)
D.box('shared', 100, 210, 480, 120, 'Shared stores', 'Tenant A rows mixed with thousands of others', kind='com', step=0, small=True)
D.label(100, 350, '🔒 Tenant A locked on commercial side', kind='shared', step=3, w=480, size='m', hide=6)
D.label(100, 350, '🔒 commercial copy locked, read-only', kind='shared', step=6, w=480, size='m', hide=7)
D.label(100, 350, '✕ commercial copy deleted, deletion verified', kind='deny', step=7, w=480, size='m')
D.zone(1300, 150, 560, 460, 'Isolated · Tenant A', kind='dp', step=0)
D.box('ishard', 1340, 420, 480, 110, 'Isolated shard', 'provisioned + registered first', kind='dp', step=0, small=True)
D.box('idata', 1340, 210, 480, 120, 'Dedicated data stores', 'receives the copy', kind='dp', step=1, small=True)
D.box('router', 720, 10, 480, 100, 'Router', 'where does Tenant A live?', kind='shared', step=0, hl='5')
D.arrow('router', 'shared', step=0, kind='com', fs='l', ts='t', fo=0.5, to=0.5, via=[(340, 60)], hide=5, name='r-com')
D.arrow('router', 'ishard', step=5, kind='ok', fs='r', ts='r', fo=0.5, to=0.5, via=[(1885, 60), (1885, 475)], name='r-iso')
D.label(1230, 72, 'tenant context: isolated\nevery Router confirms', kind='ok', step=5, w=360, size='s')
D.arrow('shared', 'idata', step=1, kind='info', fs='r', ts='l', fo=0.3, to=0.3, label='bulk copy · tenant-scoped · encrypted', lpos=0.5, loff=(0, -16), name='copy1')
D.arrow('shared', 'idata', step=2, kind='info', fs='r', ts='l', fo=0.72, to=0.72, dashed=True, name='copy2')
D.label(780, 318, 'catch-up runs, each smaller', kind='info', step=2, w=360, size='s', hide=4, align='center')
D.label(640, 470, '✓ ownership · counts · checksums', kind='ok', step=4, w=620, size='m', align='center')
tl = ['provision', 'bulk copy', 'catch-up', 'freeze', 'validate', 'switch', 'rollback window', 'delete']
for k, t in enumerate(tl):
    D.box('tl%d' % k, 60 + k * 225, 650, 205, 80, '%d · %s' % (k + 1, t), '', kind='ok' if k == 5 else 'dp', step=0, hl=str(k), small=True)
sid = D.build()
P = D.paths
seg(sid, 0, """Let's animate one tenant. On the left, the shared commercial stores, where tenant A's rows sit mixed with thousands of other customers'. On the right, tenant A's isolated environment. First, the isolated shard is provisioned and registered. At this point the Router still sends tenant A to commercial, because tenant context still says commercial. Nothing has changed for the customer.""",
    travel=travel(P['r-com'], 'com'))
seg(sid, 1, """Step two, the bulk copy, while the source stays live. The copy is tenant-scoped and encrypted. And here's the part people underestimate. In a shared store, copy too little and you lose data. Copy too much, and another customer's data ends up inside someone else's isolated environment. That second failure is worse than any outage. So each service owner wrote the tenant-scoped extraction, because only they know their schema, and the platform ran the encrypted transfer.""",
    travel=travel(P['copy1'], 'info'))
seg(sid, 2, """Step three, incremental catch-up runs, each smaller than the last, because the customer is still working and still writing. You're chasing a moving target, and each pass narrows the gap.""",
    travel=travel(P['copy2'], 'info'))
seg(sid, 3, """Step four, a short write freeze. The tenant is locked on the commercial side. That lock is doing two jobs. It stops new writes landing during the final copy. And later, it's one of the three locks that stops an isolated tenant's request ever being served by commercial.""")
seg(sid, 4, """Step five, copy the final changes, then validate. Three checks: every copied record belongs to this tenant, the counts match, and the checksums match. Traffic doesn't switch until all three pass.""",
    travel=travel(P['copy2'], 'info'))
seg(sid, 5, """Step six, the switch. Tenant context flips from commercial to isolated. And here's the detail that came from a real production incident, which we'll cover later. The switch is not complete until every Router confirms it has the new context. Watch the Router's arrow move. From this moment, tenant A's requests go to the isolated environment.""",
    travel=travel(P['r-iso'], 'ok'))
seg(sid, 6, """Step seven, the rollback window. The commercial copy stays locked and read-only. Before the switch, rollback was free: the tenant just stayed commercial. After customers write in the isolated environment, rolling back would lose those writes. So the window was agreed with each customer before cutover, and after it, you fix forward. Having that conversation up front, not during an incident, is the point.""")
seg(sid, 7, """And step eight. After the window, the commercial copy is deleted, and the deletion is verified. Regulated customers need to know their data is gone from shared infrastructure, and a leftover copy is a standing temptation for someone to serve from it one day. Security and compliance signed off on that step before the first cutover. One honest limit to mention if you're asked: data in commercial backups isn't surgically deleted. It ages out with retention, and that was written into the migration agreement.""")

sid = cards("Onboarding, in one breath", [
 (0, "New environment", "Declarative spec · quota check · account pool · baseline · VPC · one-way channel · key grant · data · shards by tier · verify · **register last**", 'cp'),
 (1, "Existing customer", "Provision shard · bulk copy · catch-up · freeze + lock · validate · **switch, every Router confirms** · rollback window · delete + verify", 'dp'),
], cols=1)
seg(sid, 0, """Let's compress both flows into something you can say in an interview. A new environment: a declarative spec drives a pipeline. Quota check, claim from the account pool, apply the baseline, build the VPC, open the one-way management channel, verify the customer's key grant, create the data stores, deploy shards in tier order, verify, and register last so a half-built environment never takes traffic.""")
seg(sid, 1, """An existing customer: provision and register the shard, bulk copy, catch-up runs, a short freeze with the tenant locked on commercial, validate ownership, counts and checksums, switch tenant context and wait for every Router to confirm, hold the rollback window, then delete and verify. If you can say both of those without looking, you understand onboarding better than most people who built parts of it.""")
