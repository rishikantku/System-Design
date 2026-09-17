# -*- coding: utf-8 -*-
from engine import *

chapter(1, "The project", "What Isolated Cloud is, who it is for, and the one sentence that describes it.",
 """Chapter one. The project. Before any architecture, you need to be able to explain what Isolated Cloud is in a way that a non-specialist on the panel understands in thirty seconds, and a specialist respects.""")

sid = compare("Two kinds of Atlassian customer",
 ("Most customers: multi-tenant cloud", 'com', 0, ["Many customers share the same infrastructure", "Logical isolation between tenants", "Works for almost everyone"]),
 ("Regulated enterprises", 'deny', 1, ["Banks, critical infrastructure, regulated industries", "Rules forbid shared infrastructure", "Logical isolation doesn't satisfy **dedicated**"]))
seg(sid, 0, """Atlassian's cloud is multi-tenant. Many customers share the same infrastructure, isolated logically from each other. And that works for almost everyone.""")
seg(sid, 1, """But some enterprises can't use it at all. Banks, critical infrastructure, regulated industries. Their rules say they may not share infrastructure. And here's the important point. No amount of logical isolation satisfies a rule that literally says dedicated. It's not a question of whether the multi-tenant cloud is secure enough. The rule rules it out. So without something new, these customers simply couldn't be cloud customers.""")

sid = table("What an isolated customer gets", ["What they get", "Detail"], [
 (0, ["Dedicated infrastructure", "Their own AWS accounts, VPC, networking, compute, storage, databases"], [None, 'ok']),
 (1, ["Their own keys", "Customer-managed encryption keys, in the customer's own AWS account"], [None, 'ok']),
 (2, ["Egress blocked by default", "Data does not leave unless a policy allows it"], [None, 'ok']),
 (3, ["Their own domain", "Dedicated edge and domain"], [None, None]),
 (4, ["**Not** their own control plane", "Provisioning, deployment and operations stay shared"], [None, 'deny']),
], widths=[32, 68])
seg(sid, 0, """Isolated Cloud gives those customers a dedicated environment, still run by Atlassian. First, dedicated infrastructure. Their own AWS accounts, their own VPC and networking, their own compute, storage and databases.""")
seg(sid, 1, """Second, their own keys. The encryption keys live in the customer's own AWS account, and the customer grants Atlassian permission to use them. That's a real operational detail we'll come back to, because it means a dependency Atlassian doesn't control.""")
seg(sid, 2, """Third, egress is blocked by default. Data doesn't leave the environment unless a policy allows it.""")
seg(sid, 3, """And they get their own domain and edge rather than the shared one.""")
seg(sid, 4, """Now the row that matters most. They do not get their own control plane. Provisioning, deployment and operations stay shared. Atlassian didn't build a separate copy of itself per customer, because that would mean running hundreds of Atlassians. The data plane is dedicated. The control plane is shared. If you remember one structural fact about this system, remember that one, because every hard problem in the design lives at that boundary.""")

sid = statement("Say it in one breath", "Atlassian Cloud, deployed one customer at a time. Dedicated data plane. Shared control plane.",
 "All the hard engineering is at that boundary.", kind='dp')
seg(sid, 0, """Here's how to say it in one breath. Isolated Cloud is Atlassian Cloud deployed one customer at a time. Dedicated infrastructure, dedicated keys, no egress by default.""")
seg(sid, 1, """But the control plane stays shared, because duplicating it per customer doesn't scale. And all the hard engineering is at that boundary. That last sentence is doing a lot of work. It tells the interviewer you understand where the difficulty actually is, before they've asked a single follow-up.""")

sid = compare("What you can cite, and what is yours",
 ("Public", 'ok', 0, ["In Atlassian's public documentation", "Anyone can check it", "Safe to state as fact"]),
 ("Yours", 'cp', 1, ["Your own work and architecture", "Not public, so not citable", "You know it first-hand, which is better"]))
seg(sid, 0, """One quick distinction before we move on. Some of what you'll say is public. It's in Atlassian's documentation, anyone can check it, and you can state it as fact. Dedicated AWS accounts, customer-managed keys, egress blocked by default.""")
seg(sid, 1, """But almost everything the interview is really about is yours. The Router, the Shard Manager, shards, tenant context, the migration of a hundred and seventy-eight teams. That isn't public. And that's fine. In a retrospective, first-hand knowledge is exactly what they want. Just use your own judgement about which internal names you say out loud.""")

sid = cards("Your story in ninety seconds", [
 (0, "The setup", "Multi-tenant cloud. Regulated enterprises need dedicated environments.", 'com'),
 (1, "The problem", "About 178 teams. Per-product isolation doesn't finish.", 'deny'),
 (2, "The position", "Isolation is a platform capability, not a product feature.", 'ok'),
 (3, "The runtime", "Edge → Router → Shard Manager → shard with replicas.", 'dp'),
 (4, "The decision to highlight", "Separate tenant identity from runtime placement.", 'shared'),
], cols=1)
seg(sid, 0, """Let me give you the ninety-second version now, so you have the whole shape in your head before we go deep. Atlassian's cloud is multi-tenant. Regulated enterprises need stronger isolation, and their rules don't accept shared infrastructure. So we built Isolated Cloud, dedicated environments per customer.""")
seg(sid, 1, """The obvious way to build it is for every product to redesign itself for isolation. We had about a hundred and seventy-eight teams. That doesn't finish.""")
seg(sid, 2, """So the position we took was that isolation is a platform capability, not a product feature. The platform owns provisioning, routing, placement, lifecycle and egress. Teams adopt a configuration model instead of rewriting business logic.""")
seg(sid, 3, """At runtime, a request goes from the edge to the Router. The Router decides commercial or isolated. If isolated, the Shard Manager resolves which shard serves them. A shard is a logical isolated runtime for one tenant and product, with replicas underneath it.""")
seg(sid, 4, """And the decision I'd highlight is separating tenant context from shard placement. Identity is static and caches well. Placement is operational and changes constantly. Keeping them apart means a shard can be replaced without anything about the tenant changing. That's the whole story in ninety seconds. Everything else in this course is a drill-down from one of those sentences.""")
