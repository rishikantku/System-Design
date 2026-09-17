# -*- coding: utf-8 -*-
from engine import *

chapter(6, "Why the architecture looks like this", "Every component is a decision. Here are the reasons, the alternatives, and what each one cost.",
 """Chapter six. Why the architecture looks like this. You now know what the components are and how the two flows run. This chapter is the one that actually gets you the level. In a retrospective, describing a component is Senior. Explaining why it exists, what you rejected, and what it cost you, is Staff. So for every piece, we're going to ask: why this, and not the obvious alternative.""")

sid = compare("Two ways to answer a question",
 ("Senior: what it does", 'com', 0, ["“The Shard Manager owns placement.”", "“It maps a tenant to a shard.”", "“It handles lifecycle.”", "Correct. And it gets you Senior."]),
 ("Staff: why it exists", 'ok', 1, ["“Two facts change at different rates.”", "“Coupling them makes every placement change touch identity.”", "“We paid one more component and one more hop.”", "Decision, reason, cost."]))
seg(sid, 0, """Let's start with the difference, because it frames the whole chapter. Here's a Senior answer to, why a Shard Manager? It owns placement. It maps a tenant to a shard. It handles lifecycle. Every word is correct. And it describes the system.""")
seg(sid, 1, """Here's the Staff answer. Two facts change at different rates. Coupling them would make every placement change touch tenant identity. We accepted one more component and one more hop to avoid that. Notice the shape: a decision, a reason, and a cost. If you catch yourself listing what a component does, add one sentence: we did it that way because the alternative would have... That single sentence usually moves the answer a level.""")

# ---- Router vs Shard Manager diagram
D = Diagram("The design we started with, and why it changed")
D.zone(60, 20, 820, 520, 'First version', kind='com', step=0)
D.box('r1', 120, 90, 700, 130, 'Router', 'commercial or isolated?  +  which shard?', kind='shared', step=0)
D.box('tc1', 120, 330, 330, 110, 'Tenant context', 'identity', kind='shared', step=0, small=True)
D.box('pl1', 490, 330, 330, 110, 'Shard placement', 'operational', kind='dp', step=0, small=True)
D.arrow('r1', 'tc1', step=0, kind='shared', fs='b', ts='t', fo=0.2, to=0.5)
D.arrow('r1', 'pl1', step=0, kind='dp', fs='b', ts='t', fo=0.8, to=0.5)
D.label(120, 460, 'One component. One lookup. Simpler.', kind='com', step=0, w=700, size='m', align='center')
D.zone(1000, 20, 860, 520, 'Events that change placement', kind='deny', step=1)
for k, e in enumerate(['a shard fails', 'maintenance', 'a deployment', 'a migration', 'a capacity change']):
    D.label(1060, 110 + k * 62, '•  ' + e, kind='neutral', step=1, w=500, size='m')
D.label(1060, 440, 'Events that change **who the tenant is**:  none of them.', kind='deny', step=2, w=780, size='m')
D.zone(60, 600, 1800, 240, 'What we built', kind='ok', step=3)
D.box('r2', 120, 670, 480, 120, 'Router', 'commercial or isolated?', kind='shared', step=3)
D.box('sm2', 720, 670, 480, 120, 'Shard Manager', 'which shard, right now?', kind='dp', step=3)
D.box('rep2', 1320, 670, 480, 120, 'Shard configuration repository', 'source of truth · cache in front', kind='dp', step=3, small=True)
D.arrow('r2', 'sm2', step=3, kind='dp', name='r-sm')
D.arrow('sm2', 'rep2', step=3, kind='dp', name='sm-rep')
sid = D.build()
seg(sid, 0, """Here's the design we started with. The Router did both jobs. It decided commercial or isolated, and it also resolved which shard. One component, one lookup. It was simpler, and be honest in the interview: you favoured it at first. Saying that is a strength, not a weakness. It shows the decision was reasoned, not assumed.""")
seg(sid, 1, """What changed your mind was a list. You wrote down every event that changes placement. A shard fails. Maintenance. A deployment. A migration. A capacity change. These happen all the time. Placement is operational. It moves.""")
seg(sid, 2, """Then the key question. How many of those events change who the tenant is? None of them. Not one. So if the Router owns placement, the component that sits on every single request is chasing operational changes all day, for a fact that has nothing to do with the tenant's identity.""")
seg(sid, 3, """So placement moved out. The Router only answers commercial or isolated. The Shard Manager answers which shard, right now, backed by the shard configuration repository as the source of truth. And the payoff sentence: a shard can be replaced without anything about the tenant changing. When you're persuading people in a review, use the event list, not a principle. Separation of concerns is an opinion. The event list is evidence.""",
    travel=travel(D.paths['r-sm'] + D.paths['sm-rep'][1:], 'dp'))

sid = table("Two facts that behave differently", ["", "Tenant context", "Shard placement"], [
 (0, ["Changes", "Rarely", "Often"], [None, 'shared', 'dp']),
 (1, ["Changes when", "A tenant moves environment or entitlement", "Failure, maintenance, deployment, migration, capacity"]),
 (2, ["Cacheable?", "Very", "Only against a moving truth"], [None, 'ok', 'deny']),
 (3, ["Nature", "Identity", "Operational"], [None, 'shared', 'dp']),
], widths=[22, 39, 39])
seg(sid, 0, """Here's that reasoning as a table you can draw on a whiteboard. Tenant context changes rarely. Shard placement changes often.""")
seg(sid, 1, """Tenant context changes when a tenant moves environment or changes entitlement. Placement changes on failure, maintenance, deployment, migration and capacity.""")
seg(sid, 2, """Tenant context is very cacheable. Placement is only cacheable against a moving truth, which is exactly why the repository is the source of truth and the cache is only an accelerator.""")
seg(sid, 3, """And the nature of the two facts. One is identity. The other is operational. Putting both in the Router ties a stable thing to a volatile one. That's the sentence to have automatic.""")

sid = cards("What the separation cost, and the catch", [
 (0, "Cost: one more component", "Something else to build, run, and page someone for.", 'shared'),
 (0, "Cost: one more hop", "Only for isolated tenants. Commercial is unchanged.", 'shared'),
 (1, "The catch: the Router still caches", "When a tenant moves commercial → isolated, the cached context is wrong until invalidated.", 'deny'),
 (1, "Correctness, not performance", "Until it's invalidated, requests go to the wrong place. Volunteer this before you're asked.", 'ok'),
], cols=2)
seg(sid, 0, """Every decision has a cost, so name it. One more component to build and operate. And one more hop, only for isolated tenants. Commercial traffic doesn't pay it. You took that trade, and say so plainly.""")
seg(sid, 1, """And here's the catch worth volunteering. The Router still caches tenant context. When a tenant moves from commercial to isolated, that cached answer is wrong until it's invalidated. Until then, requests go to the wrong place. That's a correctness problem, not a performance one. Say it before the interviewer asks. It shows you thought about the transition, not only the end state. And it's the thread that leads straight to your rehearsal finding and your worst production cutover, which we'll cover in the failures chapter.""")

# ---- Shard vs replica
D = Diagram("A shard is not a replica")
D.box('tenant', 70, 40, 360, 110, 'Tenant A', 'identity · environment', kind='shared', step=0)
D.zone(560, 20, 820, 560, 'Jira · Shard-123  (logical)', kind='dp', step=0)
for k in range(3):
    D.box('rep%d' % k, 600 + k * 190, 120, 170, 110, 'Replica %d' % (k + 1), 'AZ %s' % 'abc'[k], kind='dp', step=0, small=True, dim='3')
D.arrow('tenant', 'rep1', step=0, kind='shared', fs='r', ts='t', fo=0.5, to=0.5, via=[(875, 95)], hide=4, name='t-sh')
D.label(620, 270, 'Traffic rises → **replicas scale** with AWS Auto Scaling.\nThe shard does not change.', kind='ok', step=1, w=720, size='m', hide=2)
D.box('rep3', 1170, 120, 170, 110, 'Replica 4', 'added', kind='ok', step=1, small=True, hide=2)
D.label(620, 270, 'A replica fails → **infrastructure replaces it**.\nTenant → shard mapping does not change.', kind='shared', step=2, w=720, size='m', hide=3)
D.label(620, 440, 'Tenant A → Shard-123   (unchanged)', kind='neutral', step=1, w=720, size='m', hide=3)
D.zone(1470, 20, 390, 560, 'Shard-456  (replacement)', kind='ok', step=3)
D.box('new', 1510, 120, 310, 110, 'New shard', 'replicas start', kind='ok', step=3, small=True)
D.arrow('tenant', 'new', step=4, kind='ok', fs='b', ts='b', fo=0.5, to=0.5, via=[(250, 610), (1665, 610)], name='t-new')
D.label(560, 660, '**Shard replaced** → Tenant A → Shard-456.\nUpdate placement, invalidate the cache, then route.', kind='deny', step=3, w=900, size='m')
D.label(70, 780, 'Replica failure ≠ shard replacement. Only a shard change touches placement.', kind='neutral', step=5, w=1790, size='l', align='center')
sid = D.build()
seg(sid, 0, """Now the single most important correction in this whole course. A shard is not a replica, and it's not a machine. Tenant A's Jira is a shard. Shard one two three. It's a logical, isolated deployment for one tenant and one product. Underneath it are replicas, spread across availability zones.""")
seg(sid, 1, """When traffic rises, replicas scale with AWS Auto Scaling. A fourth replica appears. The shard doesn't change. Tenant A still maps to shard one two three. Nothing about placement moved, so nothing in the Router or the Shard Manager's cache needs to change.""")
seg(sid, 2, """When a replica fails, infrastructure replaces it. The shard absorbs it. The tenant to shard mapping still doesn't change. This is the answer that separates people who built the system from people who read about it.""")
seg(sid, 3, """Only when the shard itself is replaced does placement change. Now tenant A maps to shard four five six. And that change has a strict order: update the shard configuration repository first, then invalidate the cache, then route new traffic.""")
seg(sid, 4, """And then new traffic flows to the replacement shard. Remember that order, because you got it wrong once in production, and the story of how is one of your best answers.""",
    travel=travel(D.paths['t-new'], 'ok'))
seg(sid, 5, """So the line to say: replica failure is not shard replacement. Only a shard change touches placement and invalidates the cache. If an interviewer asks what happens when a replica fails, and you start talking about updating placement, you've just told them you don't know the system.""")

sid = cards("Two more decisions about placement", [
 (0, "The repository is the source of truth", "A cache sits in front for speed. Lose the cache: slower, still correct.", 'dp'),
 (1, "Why not add an orchestration layer", "Isolation multiplies environments. Every extra moving part is multiplied too.", 'cp'),
 (1, "AWS-native Auto Scaling", "Already handled replica scaling inside a shard. A second platform per environment wasn't worth it.", 'cp'),
], cols=3)
seg(sid, 0, """Two more decisions about placement. First, the shard configuration repository is the source of truth. A cache sits in front of it purely for speed. If the cache is lost, you pay latency while it refills. You don't lose correctness. That answer only works because you never let the cache become authoritative.""")
seg(sid, 1, """Second, you'll be asked why you didn't add a separate orchestration layer for shards. You looked at it and dropped it. Here's the reason that's specific to this system: isolation multiplies environments, so every extra moving part is multiplied too. Another orchestration layer would have been a second platform to operate inside every isolated environment, for a problem AWS-native Auto Scaling already solved. Don't sound like you never considered it. Say you considered it, and give the multiplication argument.""")

# ---- Shard descriptor diagram
D = Diagram("From one service descriptor to shard descriptors")
D.box('sd', 70, 60, 560, 200, 'Service descriptor', 'CPU · memory · keys · database · scaling strategy\nassumes ONE deployment', kind='com', step=0, dim='1')
D.box('svc', 70, 380, 560, 200, 'Service descriptor', 'what is common to the service', kind='cp', step=1)
for k, (n, s) in enumerate([('Shard A descriptor', 'Tenant A · sized for its traffic'), ('Shard B descriptor', 'Tenant B · larger'), ('Shard C descriptor', 'Tenant C · low traffic')]):
    D.box('sh%d' % k, 900, 300 + k * 150, 560, 120, n, s, kind='dp', step=2, small=True, hl='3' if k == 1 else None)
    D.arrow('svc', 'sh%d' % k, step=2, kind='cp', fs='r', ts='l', fo=0.3 + 0.2 * k)
D.label(900, 170, 'compute · memory · networking · storage · keys · monitoring', kind='dp', step=2, w=900, size='m')
D.label(1500, 460, 'one tenant resized\nno other tenant touched', kind='ok', step=3, w=360, size='m')
D.label(70, 790, 'Teams adopted a **configuration model** instead of rewriting business logic.', kind='ok', step=4, w=1790, size='l', align='center')
sid = D.build()
seg(sid, 0, """Now the shard descriptor, which is the decision that made adoption cheap. Each service used to have a service descriptor: CPU, memory, keys, database, scaling strategy. That worked when there was one deployment. It breaks when every tenant needs their own.""")
seg(sid, 1, """So the model split. The service descriptor still describes the service: whatever is common.""")
seg(sid, 2, """And a shard descriptor describes one tenant's runtime of that service. Its own compute, memory, networking, storage, keys and monitoring. Shard A, shard B, shard C, each with its own configuration.""")
seg(sid, 3, """Now one tenant can be resized for its traffic without touching the service definition, and without touching any other tenant. That's also your cost lever, which we'll come back to.""")
seg(sid, 4, """And here's why this matters beyond configuration. Teams didn't rewrite business logic. They adopted a configuration model. That is the link between the technical design and a hundred and seventy-eight teams actually finishing. If you present shard descriptors as a config format change, you've undersold your best adoption decision.""")

sid = table("Shard descriptors: the challenge and the honest answer", ["They say", "You say"], [
 (0, ["“You multiplied your config surface by the number of tenants.”", "Fair. The service level holds what's common. The shard descriptor holds what's specific, and it lives in the repository, not in 178 hand-edited places."], [None, 'ok']),
 (1, ["“What's the real risk?”", "Drift. Overrides get added during an incident or a load test and nobody removes them."], [None, 'deny']),
 (2, ["“What did you do about it?”", "Every override needs an owner and a reason. The override report became a monthly review."], [None, 'ok']),
], widths=[36, 64])
seg(sid, 0, """Expect this challenge: you just multiplied your config surface by the number of tenants. Start with, fair. The service level still holds what's common. The shard descriptor holds what's specific, and it lives in the repository, not in a hundred and seventy-eight hand-edited places.""")
seg(sid, 1, """Then concede the real risk before they find it. Drift. Per-shard settings are easy to add and nobody removes them. About two months into the migrations you pulled a report of every override. A lot had been added during an incident or a load test, and nobody could say why they were there.""")
seg(sid, 2, """So every override now needs an owner and a reason, and the report became a monthly review. Conceding a weakness and showing the mechanism you put around it is far stronger than defending the design as perfect.""")

# ---- Egress
D = Diagram("Why egress is centralised")
D.zone(60, 20, 860, 560, 'Option: each team writes its own policy', kind='deny', step=0)
for k in range(4):
    D.box('p%d' % k, 110, 90 + k * 115, 360, 90, 'Team %s policy' % 'ABCD'[k], 'strict' if k != 2 else 'too permissive', kind='deny' if k == 2 else 'com', step=0, small=True, hl='1' if k == 2 else None)
    D.arrow('p%d' % k, (520, 135 + k * 115), step=0, kind='deny' if k == 2 else 'com')
D.label(550, 110, 'The guarantee is only as\nstrong as the **weakest**\npolicy.', kind='deny', step=1, w=340, size='m')
D.label(550, 420, 'A loose policy throws\n**no error**. You find out\nat an audit.', kind='deny', step=1, w=340, size='m')
D.zone(1000, 20, 860, 560, 'What we built', kind='ok', step=2)
D.box('prod', 1050, 110, 320, 110, 'Product service', 'any team', kind='dp', step=2, small=True)
D.box('eg', 1050, 290, 320, 130, 'Egress Gateway', 'one policy check', kind='deny', step=2)
D.box('ext', 1500, 290, 300, 130, 'External system', 'only if declared + allowed', kind='neutral', step=2, small=True)
D.arrow('prod', 'eg', step=2, kind='dp', fs='b', ts='t', name='p-e')
D.arrow('eg', 'ext', step=2, kind='ok', name='e-x')
D.label(1050, 470, 'Denials became our **best early warning**.', kind='ok', step=3, w=760, size='m')
sid = D.build()
seg(sid, 0, """The Egress Gateway. Picture the alternative first. Each team writes its own outbound policy. Team A strict, team B strict, team C too permissive, team D strict.""")
seg(sid, 1, """Your compliance guarantee is only as strong as the weakest one. And here's the part that makes it dangerous: a policy that's too permissive produces no error. Nothing fails. You find out in an audit, or from a customer. That's the risk that worried you most at the start of the project.""")
seg(sid, 2, """So outbound data goes through one place, the Egress Gateway, where policy is checked, and it only reaches an external system if the destination was declared and allowed. One policy instead of a hundred and seventy-eight. And again, say policy-driven enforcement. Don't name a policy engine.""",
    travel=travel(D.paths['p-e'] + D.paths['e-x'][1:], 'deny'))
seg(sid, 3, """And an outcome you didn't expect. Egress denials became your best early warning. When a service started trying to send data somewhere it hadn't declared, the denial count moved before anything else did. When a design decision gives you something you didn't plan for, mention it. It shows you were watching the system, not just shipping it.""")

question("Why a separate Shard Manager? Why not resolve the shard in the Router?", 10,
 "The first version did it in the Router, and I favoured that. Listing every event that changes placement changed my mind: failure, maintenance, deploys, migrations, capacity. None of them change who the tenant is. Identity is static and caches well; placement moves constantly. So placement moved out. The cost was one more component and one more hop.",
 "It's a real decision with evidence, an admitted first instinct, and a named cost.",
 "Whether you can reason from how data behaves, not from principles like ‘separation of concerns’.",
 ["What happens when a shard fails?", "How did you convince people the extra component was worth it?", "What went wrong with the Router's cache?"],
 answer_long="Add the payoff: a shard can be replaced without anything about the tenant changing. And volunteer the catch: the Router still caches tenant context, so a tenant switch needs explicit invalidation — a correctness problem, not a performance one.",
 narr=dict(
  short="""Thirty seconds. The first version resolved the shard in the Router, and honestly I favoured it. What changed my mind was listing every event that changes placement: a shard failing, maintenance, a deployment, a migration, a capacity change. None of them change who the tenant is. Tenant context is static and caches well. Placement is operational and moves constantly. So placement moved into the Shard Manager. The cost was one more component and one more hop for isolated tenants.""",
  long="""For the sixty to ninety second version, add the payoff and the catch. The payoff: a shard can be replaced without anything about the tenant changing. The catch: the Router still caches tenant context, so when a tenant switches from commercial to isolated, invalidation has to be an explicit step. That's a correctness problem, not a performance one, and we found it in rehearsal.""",
  strong="""Why this lands. It's past tense with a verdict. It admits your first instinct. It argues from evidence, the event list, rather than from a principle. And it names the cost without being asked.""",
  testing="""What they're testing is whether you reason from how the data actually behaves. Anyone can say separation of concerns. Very few people can say which two facts change at different rates and why that matters on the hot path.""",
  follow="""The follow-ups are predictable. What happens when a shard fails, which is your replica versus shard answer and the ordering. How did you convince people, which is: I used the same event list that changed my own mind. And what went wrong with the cache, which leads into your rehearsal and the ten-minute production mis-route."""))
