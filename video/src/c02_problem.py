# -*- coding: utf-8 -*-
from engine import *

chapter(2, "The problem, and why it was hard", "The assumption that broke, the decision that followed, and how to answer “isn't this just dedicated hardware?”",
 """Chapter two. The problem. This chapter matters more than it looks, because the most common pushback you'll get in this interview is that the project was just an infrastructure exercise. By the end of this chapter you'll be able to take that pushback apart calmly.""")

D = Diagram("The assumption that broke")
D.zone(90, 40, 780, 560, 'Before: multi-tenant', kind='com', step=0)
D.box('svc', 280, 110, 400, 110, 'One deployment of a service', 'serves every tenant', kind='com', step=0)
for k, x in enumerate((140, 330, 520, 710)):
    D.box('t%d' % k, x - 20, 340, 150, 80, 'Tenant %s' % 'ABCD'[k], '', kind='com', step=0, small=True)
    D.arrow('svc', 't%d' % k, step=0, kind='com', fs='b', ts='t', fo=0.2 + 0.2 * k)
D.label(130, 460, 'Tenancy is a **field in a request**,\nnot a deployment.', kind='com', step=0, w=700, size='m', align='center')
D.zone(1050, 40, 780, 560, 'After: Isolated Cloud', kind='dp', step=1)
for k, y in enumerate((100, 250, 400)):
    D.box('ia%d' % k, 1110, y, 300, 100, 'Tenant %s runtime' % 'ABC'[k], 'its own deployment', kind='dp', step=1, small=True)
    D.box('ib%d' % k, 1470, y, 300, 100, 'Dedicated data', 'this tenant only', kind='dp', step=1, small=True)
    D.arrow('ia%d' % k, 'ib%d' % k, step=1, kind='dp')
D.label(1070, 520, 'Tenancy becomes a **deployment**.', kind='dp', step=1, w=740, size='m', align='center')
D.label(90, 660, 'Every one of ~178 teams’ services was built on the left-hand assumption.', kind='deny', step=2, w=1740, size='l', align='center')
sid = D.build()
seg(sid, 0, """Here's the assumption that broke. In multi-tenant cloud, one deployment of a service serves every tenant. Tenant A, B, C, D, all handled by the same running service. Tenancy is just a field in the request. A tenant ID in a query. The service filters by it.""")
seg(sid, 1, """Isolated Cloud flips that. Now a tenant needs its own deployment. Its own runtime, its own dedicated data. Tenancy stops being a field you filter by, and becomes a deployment you have to provision, route to, scale, replace and protect.""")
seg(sid, 2, """And here's why that's a big deal. About a hundred and seventy-eight engineering teams owned services built on the left-hand assumption. Every one of them assumed one deployment serves all tenants. Isolated Cloud didn't break one service. It broke an assumption baked into the whole platform.""")

sid = compare("Two ways to fix it",
 ("Each product fixes itself", 'deny', 0, ["~178 teams each build provisioning, placement, lifecycle", "178 different answers that never converge", "Product 179 starts from nothing"]),
 ("The platform fixes it once", 'ok', 1, ["Platform owns provisioning, routing, placement, lifecycle, egress", "Teams adopt a configuration model", "Future products get isolation for free"]))
seg(sid, 0, """There were two ways to fix it. The first is that each product fixes itself. Each team builds its own provisioning, its own placement, its own lifecycle management. You'd get a hundred and seventy-eight different answers. They'd never behave the same, and the next product would start from zero. And think about egress. If every team writes its own outbound data policy, your compliance story is only as strong as the weakest team's implementation.""")
seg(sid, 1, """The second way is that the platform fixes it once. The platform owns provisioning, routing, placement, lifecycle and egress. Product teams adopt a configuration model instead of rewriting their business logic. And any future product gets isolation for free, just by being on the platform.""")

sid = statement("The sentence everything comes from", "Isolation is a platform capability, not a product feature.",
 "Every component in this architecture exists because of that choice.", kind='ok')
seg(sid, 0, """So here's the sentence everything comes from. Isolation is a platform capability, not a product feature.""")
seg(sid, 1, """Every single component we'll cover exists because of that choice. The control plane, the Router, tenant context, the Shard Manager, shard descriptors, the Egress Gateway. If an interviewer asks what your most important architectural decision was, this is it. Not a component. The decision the components came from.""")

sid = cards("Why this was a Staff problem, not a Senior one", [
 (0, "The engineering move is normal", "Pushing a cross-cutting concern into the platform is a well-known pattern.", 'com'),
 (1, "The organisational move is hard", "~178 teams accepting an abstraction they didn't design.", 'shared'),
 (2, "Every team had a fair case", "Each one could reasonably argue to be the exception.", 'deny'),
 (3, "Holding the line is the work", "One exception makes the abstraction optional for everyone.", 'ok'),
], cols=2)
seg(sid, 0, """Now, why is this a Staff problem and not a Senior one? Be honest here, because the interviewer will respect it. The engineering move itself is normal. Pushing a cross-cutting concern into the platform is a well-known pattern.""")
seg(sid, 1, """The hard part is organisational. You're asking a hundred and seventy-eight teams to accept an abstraction they didn't design.""")
seg(sid, 2, """And each of those teams has a fair case for being the exception. Their service is special. Their scaling is unusual. Their deadline is tight.""")
seg(sid, 3, """Holding the line is the actual work. Because the moment you make one exception, the abstraction becomes optional for everyone. The Staff-level signal here is showing that you understood the organisational difficulty, not just the technical pattern.""")

sid = quote_slide("The pushback you will get", "Isn't this just an infrastructure decision? You gave each tenant its own hardware. It's a fancy way of saying single-tenant hosting.",
 sub="It is right about the easy part, and wrong about everything after it.")
seg(sid, 0, """Now the pushback. You've told me you've heard this in real interviews, so let's handle it properly. The interviewer says: isn't this just an infrastructure decision? You gave each tenant its own hardware. It's a fancy way of saying single-tenant hosting.""")
seg(sid, 1, """Here's the key insight. That framing is right about the easy part, and wrong about everything after it. Dedicated hardware isolates where the code runs. It does not change what the code assumes. The services still assume they share one runtime with every tenant. Putting them in a private box is day one. The hard part is day two, and every day after that.""")

D = Diagram("The difficulty ladder")
D.box('l1', 160, 60, 1600, 150, 'Level 1 · Give one tenant its own infrastructure', 'accounts, VPC, databases, storage, keys  —  easy. This is what the pushback describes.', kind='ok', step=0)
D.box('l2', 160, 260, 1600, 150, 'Level 2 · Make one service work inside that box', 'config, scaling, deployment for one tenant  —  moderate.', kind='shared', step=1)
D.box('l3', 160, 460, 1600, 230, 'Level 3 · Make ~178 interdependent services run as isolated runtimes for many customers', 'routed on every request · deployed · replaced · observed · restricted · migrated live · by one platform · without product rewrites  —  the real problem', kind='deny', step=2)
sid = D.build()
seg(sid, 0, """Use this ladder to show the interviewer where the problem actually starts. Level one. Give one tenant its own infrastructure. Accounts, VPC, databases, storage, keys. That's easy. It's a provisioning job. And that's exactly what the pushback is describing.""")
seg(sid, 1, """Level two. Make one service work inside that box. Configuration, scaling, deployment for one tenant. Moderate. Still not the interesting part.""")
seg(sid, 2, """Level three is the real problem. Make about a hundred and seventy-eight interdependent services run as isolated runtimes for many customers. Routed correctly on every request, deployed, replaced when they fail, observed, restricted from sending data out, and migrated live, all by one platform, and without asking product teams to rewrite their products. When you say this ladder out loud, you move the conversation from level one, where the interviewer was, to level three, where your work was.""")

sid = table("Day two: what dedicated hardware doesn't answer", ["What happens", "“Just give them hardware”", "What it actually took"], [
 (0, ["A request arrives", "Which box? The entry path is shared.", "Router decides commercial or isolated; Shard Manager picks the shard"], [None, 'deny', 'ok']),
 (0, ["A runtime fails", "Traffic keeps going to the old box", "Replace, update placement, invalidate cache, then route"], [None, 'deny', 'ok']),
 (1, ["A security patch ships", "Every team deploys to every customer's copy", "The platform deploys shards; teams ship once"], [None, 'deny', 'ok']),
 (1, ["A service sends data out", "The box doesn't stop it", "Egress Gateway with policy; destinations declared"], [None, 'deny', 'ok']),
 (2, ["An existing customer moves in", "Copy and hope nothing is written", "Bulk copy, catch-up, freeze, checksums, switch, Routers confirm"], [None, 'deny', 'ok']),
 (2, ["Services call each other", "Which copy of the dependency?", "Dependency map and tiers"], [None, 'deny', 'ok']),
 (3, ["The bill arrives", "Everyone sized like the largest", "Shard descriptors size each shard for its tenant"], [None, 'deny', 'ok']),
], widths=[22, 34, 44])
seg(sid, 0, """Here's the day-two table. It's your strongest weapon against the pushback, so let's walk through it. A request arrives. With just hardware, which box does it go to? The entry path is shared by commercial and isolated tenants. What it actually took was the Router deciding commercial or isolated on every request, and the Shard Manager picking the shard. A runtime fails. With just hardware, traffic keeps going to the old box. What it actually took was a shard lifecycle: replace it, update placement in the source of truth, invalidate the cache, then route. And the order matters. You got that order wrong once, which we'll cover in the failures chapter.""")
seg(sid, 1, """A security patch ships. With just hardware, every product team deploys to the commercial copy plus every customer's copy. What it took was the platform deploying shards, so teams ship once. A service sends data out. A private box doesn't stop software that was built to send telemetry, analytics and integration calls. What it took was the Egress Gateway, with every destination declared.""")
seg(sid, 2, """An existing customer moves in. With just hardware, you copy the data and hope nothing is written during the copy. What it took was a bulk copy, catch-up runs, a short freeze, checksums, a tenant context switch, and every Router confirming. And services call each other. Which copy of the dependency? Does it even exist in the box yet? That's why the dependency map and the tiers existed.""")
seg(sid, 3, """And finally, the bill. With just hardware, every customer is provisioned like the largest one. What it took was shard descriptors sizing each shard for its own tenant's traffic. Now here's the line to finish with. Every row in the right-hand column is something the platform had to own. None of it is hardware.""")

sid = cards("Why it was hard", [
 (0, "Design: assumptions lived in the software", "You can't fix a request field with a VPC.", 'dp'),
 (0, "Design: two routing decisions per request", "No added latency — which forced the cache, which forced the split.", 'dp'),
 (1, "Design: placement moves, and can't be wrong", "A stale answer sends a request to the wrong runtime.", 'dp'),
 (1, "Design: isolation multiplies everything", "Per-environment cost must be close to zero.", 'dp'),
 (2, "Process: ~178 teams, no authority", "Adoption had to be cheaper than resistance.", 'shared'),
 (2, "Process: nothing could stop", "Teams kept shipping while we moved them.", 'shared'),
], cols=2)
seg(sid, 0, """If they want the deeper version of why it was hard, split it into design and process. On design: the assumptions were in the software, not the infrastructure. Tenancy was a field in a request. You can't fix that with a VPC. And there are two routing decisions on every request, commercial or isolated, then which shard, with no added latency. That constraint forced the Router cache, and the cache forced the split between stable tenant identity and moving placement.""")
seg(sid, 1, """Placement is a moving target that must never be wrong. Shards get replaced by failures, maintenance, deployments and migrations. A stale cache doesn't slow a request down, it sends it to the wrong runtime. And isolation multiplies everything. Every environment is another thing to deploy, patch, scale and monitor. Anything that costs one unit of effort per environment becomes unaffordable.""")
seg(sid, 2, """On process. A hundred and seventy-eight teams, with no authority over any of them, so adoption had to be cheaper than resistance. The dependency graph was partly unknown, because the service catalogue was out of date. And nothing could stop. Product teams kept shipping features while you moved them. You were migrating a moving target.""")

sid = statement("The point that usually ends the pushback", "The dedicated-box-per-customer model already exists. It's essentially Data Center.",
 "Isolated Cloud had to give dedicated isolation while keeping cloud economics and cloud speed. Getting both is the hard problem.", kind='shared')
seg(sid, 0, """And here's the point that usually ends the pushback. The dedicated box per customer model already exists. It's essentially what Data Center is. Customers run their own copy.""")
seg(sid, 1, """Its cost and its slow upgrades are exactly why the industry moved to multi-tenant cloud in the first place. So Isolated Cloud had to give customers dedicated isolation while keeping cloud economics and cloud speed. One platform, one deployment pipeline, one team operating many isolated environments. Getting both at once is the hard problem. When you say this, you're not defending your project. You're reframing the question, and that's a Staff move.""")

sid = table("If they push again", ["They say", "You say"], [
 (0, ["“Accounts and VPCs are just Terraform.”", "Agreed, that's the control plane's easy job. The hard part starts after provisioning."]),
 (1, ["“Why not a full copy of Atlassian per customer?”", "Every deploy, patch and incident multiplies per customer. That's the model cloud replaced."]),
 (2, ["“So what was technically new?”", "A multi-tenant ecosystem running as isolated runtimes without rewriting it."]),
 (3, ["“Sounds like mostly project management.”", "The migration was organisational. Why teams could adopt without rewrites was a design decision."]),
], widths=[40, 60])
seg(sid, 0, """If they push again, you have four short replies. If they say accounts and VPCs are just Terraform, agree with them. That's the control plane's easy job. The hard part starts after provisioning: routing, replacement, deploys and data boundaries at runtime. Agreeing first is disarming, and it shows you're not defensive.""")
seg(sid, 1, """If they say, why not run a full copy of Atlassian per customer? Then every deploy, patch and incident multiplies by the number of customers, and every team operates many copies. That's exactly the model cloud replaced.""")
seg(sid, 2, """If they ask what was technically new, say: making a multi-tenant ecosystem run as isolated per-customer runtimes without rewriting it. Tenant-aware routing, dynamic placement that's never wrong, per-shard configuration, and platform-enforced egress.""")
seg(sid, 3, """And if they say it sounds like mostly project management, don't get defensive. Say: the migration was organisational, yes. But the reason a hundred and seventy-eight teams could adopt it without rewrites was a design decision. The platform owns isolation, not the products.""")
