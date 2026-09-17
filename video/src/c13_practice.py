# -*- coding: utf-8 -*-
from engine import *

chapter(13, "Practice interview questions", "Thirteen questions from across the journey. Pause, answer out loud, then compare.",
 """Chapter thirteen. Practice. From here on, the course changes pace. Each question appears, and a timer runs. Pause the video if you need more time, and answer out loud. Actually say it, don't just think it. Then listen to the thirty-second answer, why it lands, what's being tested, and the follow-ups. You've heard the reasoning in earlier chapters. Now you're practising the delivery.""")

sid = cards("How to use this chapter", [
 (0, "Say it out loud", "Silent answers feel complete. Spoken ones expose the gaps.", 'ok'),
 (0, "Aim for thirty seconds", "Then stop. Let them pull you deeper.", 'info'),
 (1, "Past tense, with a verdict", "“We considered… we rejected it because…”", 'shared'),
 (1, "Keep numbers identical", "Every figure must match what you said in every other answer.", 'deny'),
], cols=2)
seg(sid, 0, """Two rules for this chapter. Say it out loud. Silent answers always feel complete. Spoken ones expose the gaps. And aim for thirty seconds, then stop. In a retrospective, the interviewer controls depth. Give them a tight answer and let them pull.""")
seg(sid, 1, """And two more. Past tense, with a verdict. And keep every number identical across answers. Five hours, not four to six. A dozen environments, not fifteen. Inconsistent numbers are the fastest way to lose credibility with an interviewer who's taking notes.""")

question("Isn't this just giving each tenant dedicated hardware?", 8,
 "Dedicated infrastructure is the easy part — a provisioning job. The hard part is that ~178 teams' services assumed one runtime for every tenant, and a private box doesn't change that. Requests must find the right runtime, runtimes get replaced, patches reach every customer, outbound data gets stopped, live customers move in. The dedicated-box model already exists — it's Data Center. We needed that isolation with cloud economics.",
 "It agrees with the easy part, then moves the conversation to day two, and ends with the Data Center reframe.",
 "Whether you can take a dismissive challenge calmly and reframe it without getting defensive.",
 ["So what was technically new?", "Isn't it mostly project management?", "Why not run a full copy per customer?"],
 narr=dict(
  short="""Thirty seconds. Dedicated infrastructure is the easy part. It's a provisioning job. The hard part is that about a hundred and seventy-eight teams' services assumed they share one runtime with every tenant, and a private box doesn't change that. Every request still has to find the right runtime, runtimes get replaced, patches have to reach every customer, software built to send data out has to be stopped, and live customers have to move in. The dedicated-box model already exists. It's essentially Data Center, and it's expensive to run. We needed that isolation with cloud economics.""",
  strong="""Why it lands. It doesn't fight the premise. It concedes the easy part, then lists day-two problems a box can't solve, and finishes with a reframe the interviewer can't really argue with.""",
  testing="""They're testing composure and framing. This question is often deliberately dismissive, to see whether you get defensive or get precise.""",
  follow="""Next they'll ask what was technically new. Tenant-aware routing, dynamic placement that's never wrong, per-shard configuration, and platform-enforced egress, without product rewrites. And if they say it sounds like project management: the migration was organisational, but the reason teams could adopt without rewrites was a design decision."""))

question("Tell me about the project, and your role in it.", 8,
 "Isolated Cloud gives regulated enterprises a dedicated Atlassian environment. I was a principal engineer in platform engineering, and I led the cross-team platform design: the principle that isolation belongs to the platform, the architecture behind it, the tiering of ~178 teams' services, and the onboarding tool. My job was making product teams, SRE, identity, edge and program management fit together.",
 "Your role appears in the second sentence, with a precise boundary of ownership.",
 "Scope and clarity: can you say what you owned in thirty seconds?",
 ["What did you personally own, versus the wider team?", "How did this start?", "What was technically hard?"],
 narr=dict(
  short="""Thirty seconds. Isolated Cloud gives regulated enterprises a dedicated Atlassian environment. I was a principal engineer in platform engineering, and I led the cross-team platform design. The principle that isolation belongs to the platform, the architecture behind it, the tiering of about a hundred and seventy-eight teams' services, and the onboarding tool. The wider programme included product teams, SRE, identity, edge and a program manager. My job was making those pieces fit together.""",
  strong="""Why it lands. The role arrives in the second sentence. The product pitch is one line. And ownership has a clear boundary.""",
  testing="""They're testing whether you can scope your own contribution. Candidates who take three minutes on the product pitch are signalling that their own part was small.""",
  follow="""Expect: what did you personally own? The four items on your ownership slide. How did it start? Three design reviews in one week and the one-page note. And what made it technically hard? Routing, placement and multiplication."""))

question("Why split the control plane from the data plane?", 8,
 "They do different jobs. The control plane provisions environments — rare, slow, and can fail. The data plane serves requests constantly and is latency-sensitive. So the control plane is shared and off the request path. Provisioned metadata reaches the runtime through tenant context, so no request waits on provisioning.",
 "It explains the split through how each plane behaves, and closes the loop on how provisioned state reaches runtime.",
 "Whether you understand request-path isolation from management operations.",
 ["What happens to customers if the control plane is down?", "How does the control plane reach into an environment?", "What does it provision?"],
 narr=dict(
  short="""Thirty seconds. They do different jobs. The control plane provisions environments: AWS accounts, VPC, databases, storage, keys. That's rare, slow and can fail. The data plane serves requests constantly and is latency-sensitive. So the control plane is shared and stays off the request path. Once a tenant is provisioned, its metadata reaches the runtime through tenant context, so no request ever waits on provisioning.""",
  strong="""Why it lands. The last sentence answers the question most candidates forget: if the control plane isn't on the request path, how does the runtime learn what it provisioned?""",
  testing="""They're testing whether you separate management operations from serving traffic, and understand the failure consequences of mixing them.""",
  follow="""If the control plane is down: live traffic is fine; onboarding, deploys and lifecycle changes wait. How does it reach in: one private endpoint, connections from the control plane side only. What it provisions: accounts, VPC, databases, storage, keys, plus deployment, monitoring and logging configuration."""))

question("What exactly is a shard?", 6,
 "A logical isolated deployment for one tenant and one product — like one customer's Jira. It has several replicas behind it. It's not a machine and not a data partition. When traffic rises, replicas scale; the shard stays the same.",
 "It says what a shard is and what it isn't, in under twenty seconds.",
 "Precision. This one word exposes whether you really know the system.",
 ["What happens when one replica fails?", "What happens when a shard is replaced?", "How do you scale a growing tenant?"],
 narr=dict(
  short="""Thirty seconds, and it should take less. A logical isolated deployment for one tenant and one product. Like one customer's Jira. It has several replicas behind it. It's not a machine, and it's not a data partition. When traffic rises, replicas scale, and the shard stays the same.""",
  strong="""Why it lands. It rules out both common misreadings, machine and data partition, before the interviewer can form them.""",
  testing="""They're testing precision. Calling a shard an instance is the fastest way to reveal you've only heard this architecture described.""",
  follow="""Replica fails: absorbed, mapping unchanged. Shard replaced: repository first, then invalidate the cache, then route. Growing tenant: replicas scale with Auto Scaling; baseline changes resize the shard descriptor."""))

question("Why is tenant context cached in the Router?", 6,
 "The Router is on every request, so calling the Tenant Context Service each time would slow everything. Tenant context rarely changes, so caching is safe. On a miss the Router calls the service. The catch is invalidation when a tenant switches — we learned that in rehearsal, and again in production.",
 "It justifies the cache and immediately names its failure mode, with evidence.",
 "Whether you think about cache correctness, not just cache speed.",
 ["What happened in production?", "What if the Tenant Context Service is down?", "How do you know every Router has the new context?"],
 narr=dict(
  short="""Thirty seconds. The Router is on every request, so calling the Tenant Context Service each time would slow everything down. Tenant context rarely changes, so caching it is safe. On a miss, the Router calls the service. The catch is invalidation when a tenant switches. We learned that in rehearsal, and again in production.""",
  strong="""Why it lands. It doesn't stop at why the cache helps. It names the correctness risk, and hints at real incidents.""",
  testing="""They're testing whether you treat caches as a correctness problem. Many candidates only talk about latency.""",
  follow="""Production: the ten-minute mis-route when a few Routers missed invalidation; lock two held. Tenant Context Service down: steady state serves from cache, safe because no switch can happen. And confirmation: a switch isn't complete until every Router confirms the new context."""))

question("Why split the service descriptor into shard descriptors?", 8,
 "The service descriptor assumed one runtime. With a runtime per tenant, each shard needs its own compute, memory, keys and monitoring. Teams got a generated starting shard descriptor and reviewed it instead of rewriting code. The downside was drift — overrides added in incidents and never removed — so every override needs an owner and a reason, reviewed monthly.",
 "It links a config decision to adoption, and concedes the real downside with its mechanism.",
 "Whether you see configuration design as an adoption lever, and own its long-term cost.",
 ["How did you notice the drift?", "Didn't you multiply your config surface?", "What did teams still have to do themselves?"],
 narr=dict(
  short="""Thirty seconds. The service descriptor assumed one runtime. With a runtime per tenant, each shard needs its own compute, memory, keys and monitoring. Teams got a generated starting shard descriptor and reviewed it instead of rewriting code. The downside was drift. Overrides got added in incidents and never removed. So every override now needs an owner and a reason, and we review the report monthly.""",
  strong="""Why it lands. It treats the descriptor as what made adoption cheap, not as a format change. And it volunteers the downside.""",
  testing="""They're testing whether you understand that configuration models shape organisational behaviour, for better and worse.""",
  follow="""How did you notice drift? About two months in, you pulled a report of every override, and nobody could explain many of them. Config surface: common stays at the service level, specific lives in the repository. And what teams still did: review the descriptor, write their tenant-scoped extraction, and run the tool in their pipeline."""))

question("How do you stop an isolated service calling a commercial or multi-tenant service?", 8,
 "Layers. Network: no route to commercial; the only way out is the Egress Gateway, where commercial services are denied like any other destination. Dependencies point at isolated counterparts — why a service can't move before its dependencies. And the readiness check: any commercial endpoint fails it, and every service ran in isolated with outbound denied before cutover.",
 "Defence in depth, with the reason tier order matters woven in.",
 "Whether you enforce a boundary with mechanisms rather than instructions to teams.",
 ["What did you find when you first turned outbound traffic off?", "What if a feature genuinely needs a commercial service?", "How do you know the guarantee holds?"],
 narr=dict(
  short="""Thirty seconds. Layers. The network: isolated environments have no route to commercial services, and the only way out is the Egress Gateway, where commercial services are denied like any other destination. Dependencies: they point at isolated counterparts, which is why a service can't move before its dependencies do. And the readiness check: any commercial endpoint fails it, and every service ran in isolated with outbound traffic denied before cutover.""",
  strong="""Why it lands. Every layer is a mechanism. There's no, we told teams not to. And it connects the boundary to the migration order.""",
  testing="""They're testing whether you enforce guarantees structurally. Policies that depend on people remembering are not guarantees.""",
  follow="""What you found: hardcoded dependencies nobody had written down; a denial is a bug to fix, never a rule to open. A feature needing commercial: it needs an isolated counterpart first; until then it isn't available in Isolated Cloud. How you know it holds: the commercial-side alert reads zero, and egress denials to commercial are zero or explained, checked at every cutover."""))

question("How did you switch a tenant without breaking requests?", 8,
 "Shard first, then data, then tenant context, then confirmation that every Router had the new context. That last step exists because of a production cutover where a few Routers missed the invalidation and some requests hit the commercial runtime for about ten minutes — refused, because the tenant was locked.",
 "A strict order, and the reason the last step exists.",
 "Whether you think about the transition, not only the end state.",
 ["How did you detect that?", "Why hadn't the rehearsal caught it?", "What was your rollback plan?"],
 narr=dict(
  short="""Thirty seconds. Shard first, then data, then tenant context, then confirmation that every Router has the new context. That last step exists because of a production cutover where a few Routers missed the invalidation, and some of that customer's requests hit the commercial runtime for about ten minutes. They were refused, because the tenant was already locked as migrated.""",
  strong="""Why it lands. It's an order, not a description. And every step has a reason you can defend.""",
  testing="""They're testing transitions. Anyone can describe the end state. Staff engineers get asked about the moment in between.""",
  follow="""Detection: per-tenant error rate, before the customer raised it. Rehearsal: it caught the stale cache, which made invalidation a step, but not that some Routers could miss it. Rollback: free before the switch; after it, a short window agreed with the customer, then fix forward."""))

question("Why did you add an L2.5 tier?", 6,
 "It came out of planning. One group wasn't a product the first customers needed, so not L2, but several L2 products called them on common paths, so they couldn't wait with L3. A half tier avoided renumbering, which would have broken dashboards, alerts and runbooks keyed to the tiers.",
 "It explains the gap in the model and why the fix was cheap, without defensiveness.",
 "Whether you adapt a plan to reality without disrupting what's built on it.",
 ["Isn't a half tier a sign the model was wrong?", "Why were identity and the edge L0?", "A team said they had no capacity. What did you do?"],
 narr=dict(
  short="""Thirty seconds. It came out of planning. One group didn't fit. They weren't products the first customers needed, so not L two. But several L two products called them on common paths, so they couldn't wait with L three. A half tier avoided renumbering, which would have broken the dashboards, alerts and runbooks already keyed to the tiers.""",
  strong="""Why it lands. It shows the operational cost of renumbering, which is the non-obvious reason, and doesn't apologise for adapting.""",
  testing="""They're testing pragmatism: can you change a plan without breaking everything that depends on it?""",
  follow="""Is it a sign the model was wrong? The model met reality, and you changed it cheaply. L zero: nothing isolated works without identity and the edge. No capacity: move them later in their tier on purpose, after checking nothing depended on them. If something did, it became a priority conversation with leadership, with the dependency map in front of everyone."""))

question("What happens if provisioning fails halfway?", 6,
 "Provisioning is declarative, and every step is ‘make sure this exists and matches’, not ‘create this’. A failure leaves the environment marked failed at a step; rerunning resumes without duplicates. Nothing is registered in Tenant Context until verification passes, so a half-built environment can never receive traffic.",
 "Idempotent steps, a clear failure state, and register-last ordering.",
 "Whether you design automation to fail safely, not just to succeed.",
 ["What was the most common failure?", "Did you hit AWS quotas?", "How long did provisioning take?"],
 narr=dict(
  short="""Thirty seconds. Provisioning is declarative, and every step is written as make sure this exists and matches, not create this. A failure leaves the environment marked failed at a step, and rerunning resumes from there without duplicates. Nothing is registered in Tenant Context until verification passes, so a half-built environment can never receive traffic. And a scheduled reconciliation catches drift afterwards.""",
  strong="""Why it lands. It covers recovery, safety, and drift, not just rerun the script.""",
  testing="""They're testing infra maturity. Rerun it from the start is a Senior answer at best.""",
  follow="""Most common failure: a customer key policy missing one permission, so the failure names the exact permission and customers get a pre-check. Quotas: once, early; now a quota check runs first and the account pool is quota-raised in advance. Duration: about two days for the pilot, around five hours by phase two."""))

question("How did you migrate the distributed cache?", 8,
 "We didn't copy the shared cache. Every isolated shard got a dedicated cache, and the platform cache client requires tenant context in every key. Old commercial entries, many keyed by entity ID alone, became unreachable once the tenant was locked and drained on expiry. We pre-warmed from the tenant's hottest keys during catch-up, and moved cache-only state to a real store first.",
 "It avoids the trap of copying, and covers findability, cold start and cache-as-store.",
 "Whether you realise cached copies of customer data are customer data in shared infrastructure.",
 ["How did you find services using the cache as their only store?", "What about DataLoader's cache?", "Why not just flush the shared cache?"],
 narr=dict(
  short="""Thirty seconds. We didn't copy the shared cache. Every isolated shard got its own dedicated cache, and the platform cache client requires tenant context in every key. Old commercial entries, many keyed by entity ID alone, became unreachable once the tenant was locked, and drained on expiry. We pre-warmed the isolated cache from the tenant's hottest keys during catch-up, and moved services that used the cache as their only store onto a real store first.""",
  strong="""Why it lands. It covers three distinct problems: finding the entries, the cold cache at cutover, and cache used as a database.""",
  testing="""They're testing whether you think of the cache as data. The trap is migrating the database and forgetting the cache.""",
  follow="""Cache-only state: the readiness check flagged it. DataLoader's cache: per request only; anything longer-lived goes through the tenant-keyed platform cache. And if they ask why not flush the shared cache, stay with what you did: many keys had no tenant, so you couldn't find all of one tenant's entries to remove them. Locking made them unreachable instead."""))

question("Tell me about a production incident.", 10,
 "During an early production cutover, a few Router instances missed the tenant context invalidation. For about ten minutes some of that customer's requests went to the commercial runtime, which refused them because the tenant was locked as migrated, so users saw errors. We caught it from per-tenant error rates before the customer raised it and forced a refresh. The lasting fix: a switch isn't complete until every Router confirms the new context.",
 "Impact, why it wasn't worse, detection, and a fix that changes the process.",
 "Whether your fixes remove a class of failure, or just add carefulness.",
 ["Why hadn't the rehearsal caught that?", "What was the second incident?", "What did it reveal about the design?"],
 narr=dict(
  short="""Thirty seconds. During an early production cutover, a few Router instances missed the tenant context invalidation. For about ten minutes, some of that customer's requests went to the commercial runtime. The commercial side refused them, because the tenant was already locked as migrated, so users saw errors rather than anything being served from shared infrastructure. We caught it from per-tenant error rates before the customer raised it, and forced a refresh. The lasting fix: a switch isn't complete until every Router instance confirms the new context.""",
  strong="""Why it lands. It explains why the incident was bounded, which is the design paying off, and the fix isn't be more careful.""",
  testing="""They're testing incident maturity. Senior names the fix. Staff names what the incident revealed about the design.""",
  follow="""Rehearsal: it exposed the stale cache, making invalidation a step, but not partial delivery to some Routers. Second incident: the shard replacement ordering bug. And what it revealed: cache invalidation was the recurring weak point, which is why you'd design it in from day one."""))

question("Where did the migration stall?", 6,
 "Phase two. More teams, smaller services, and I expected it to be faster. It took about as long as phase one. Teams had other priorities and some services had no owner left after reorganisations. Office hours, visible status for leadership, chasing owners, and fixing common blockers once in the platform moved it.",
 "It admits a wrong estimate and explains the real cause: adoption, not engineering.",
 "Honesty about execution, and whether you understand organisational friction.",
 ["What would you do differently for the tail?", "How did you find orphaned services?", "A team said they had no capacity — what did you do?"],
 narr=dict(
  short="""Thirty seconds. Phase two. More teams, smaller services, and I expected it to be faster. It took about as long as phase one. Phase one was an engineering problem. Phase two was an adoption problem. Teams had other priorities, and some services had no owner left after reorganisations. What moved it was office hours, visible status for leadership, chasing owners, and fixing common blockers once in the platform.""",
  strong="""Why it lands. Admitting your estimate was wrong, and diagnosing why, is more credible than claiming it went smoothly.""",
  testing="""They're testing whether you can reflect on execution honestly, and whether you understand that the tail of a migration is an organisational problem.""",
  follow="""Orphaned services: the readiness check failed on dependencies nobody claimed. No capacity: move them later on purpose, check dependencies, escalate only with the dependency map. And what you'd do differently for the tail: publish the contract and descriptor model earlier, so less negotiation was left for phase two."""))
