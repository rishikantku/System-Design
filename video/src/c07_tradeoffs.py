# -*- coding: utf-8 -*-
from engine import *

chapter(7, "The trade-offs", "What you gave up, what you got back, and how to say it without sounding defensive.",
 """Chapter seven. The trade-offs. Here's something every strong retrospective answer has in common. It names what the decision cost. People skip the trade-off because it feels like admitting a weakness. It's the opposite. An interviewer can't believe a design that had no downside, so a candidate who names the cost first sounds like the person who actually made the call.""")

sid = statement("The rule for this chapter", "Name the cost before they do.",
 "Then say why it was worth paying, and what you put around it so it didn't hurt.", kind='shared')
seg(sid, 0, """The rule for this chapter. Name the cost before they do.""")
seg(sid, 1, """Then say why it was worth paying, and what mechanism you put around it so the cost didn't hurt. Three parts. Cost, reason, mitigation. Every trade-off in this chapter follows that pattern, and you should practise saying each one in exactly that order.""")

D = Diagram("The biggest trade-off: centralisation")
D.zone(60, 20, 860, 600, 'What teams gave up', kind='deny', step=0)
D.box('g1', 110, 90, 760, 120, 'Some control over deployment configuration', '', kind='deny', step=0, small=True)
D.box('g2', 110, 250, 760, 120, 'Independence', 'every product now depends on the platform', kind='deny', step=1, small=True)
D.box('g3', 110, 410, 760, 150, 'A shared failure mode', 'get the platform wrong, and it is wrong for everyone at once', kind='deny', step=1, hl='1')
D.zone(1000, 20, 860, 600, 'What everyone got back', kind='ok', step=2)
D.box('k1', 1050, 90, 760, 120, 'One implementation', 'not 178', kind='ok', step=2, small=True)
D.box('k2', 1050, 250, 760, 120, 'One egress policy', 'compliance as strong as one gateway, not the weakest team', kind='ok', step=2, small=True)
D.box('k3', 1050, 410, 760, 150, 'Isolation any new product inherits', 'without redesigning anything', kind='ok', step=2)
D.box('m', 260, 680, 1400, 140, 'What made the risk acceptable', 'a written platform contract  ·  platform changes rolled out tenant by tenant, never everywhere at once', kind='shared', step=3, hl='3')
sid = D.build()
seg(sid, 0, """The biggest trade-off was centralisation, and you said so plainly in the architecture review. Product teams gave up some control over their deployment configuration.""")
seg(sid, 1, """They gave up independence. Every product now depended on the platform. And that creates a shared failure mode. If you got the platform wrong, you got it wrong for everyone at once. Say that sentence in the interview. It's the honest cost, and interviewers listen for whether you'll say it.""")
seg(sid, 2, """What everyone got back. One implementation instead of a hundred and seventy-eight. One egress policy, so compliance is as strong as one gateway rather than as weak as the weakest team. And isolation that any new product inherits without redesigning anything.""")
seg(sid, 3, """And here's the mitigation, which is the part that makes it Staff. Two mechanisms made that risk acceptable. A written platform contract: what the platform guarantees, what it doesn't, and how teams ask for changes. And rolling platform changes out tenant by tenant, never everywhere at once. So the shared failure mode exists, but its blast radius is controlled by process, not by hope.""")

sid = table("Every trade-off, in one place", ["We chose", "We gave up", "Why it was worth it"], [
 (0, ["Platform owns isolation", "Team control; a shared dependency", "One implementation; contract + staged rollout"], ['ok', 'deny', None]),
 (1, ["Separate Shard Manager", "One more component, one more hop", "Placement changes never touch tenant identity"], ['ok', 'deny', None]),
 (2, ["Cached tenant context", "Invalidation becomes a correctness step", "No added latency on every request"], ['ok', 'deny', None]),
 (3, ["Dedicated runtime per customer", "Cost: a fixed floor per environment", "It was the requirement; shard descriptors size it"], ['ok', 'deny', None]),
 (4, ["No extra orchestration layer", "An orchestrator's features", "Nothing extra multiplied per environment"], ['ok', 'deny', None]),
 (5, ["Fail closed, no fallback", "Errors instead of degraded service", "An outage is recoverable; a breach isn't"], ['ok', 'deny', None]),
], widths=[30, 34, 36])
seg(sid, 0, """Here's every trade-off in one table. We'll go row by row, briefly, because each one comes up again in the practice questions. Platform owns isolation. You gave up team control and created a shared dependency. Worth it because it's one implementation, protected by a contract and staged rollouts.""")
seg(sid, 1, """A separate Shard Manager. You gave up simplicity: one more component, one more hop for isolated tenants. Worth it because placement changes never touch tenant identity.""")
seg(sid, 2, """Cached tenant context in the Router. You gave up the simplicity of always asking the source. Invalidation becomes a correctness step, not an optimisation. Worth it because the Router is on every request, and calling the Tenant Context Service each time would slow everything.""")
seg(sid, 3, """A dedicated runtime per customer. You gave up cost efficiency. There's a fixed floor per environment. Worth it because it was the requirement. Without it, these customers couldn't use the cloud at all. And shard descriptors kept the waste down.""")
seg(sid, 4, """No extra orchestration layer. You gave up whatever an orchestrator would have offered. Worth it because nothing extra gets multiplied across every isolated environment, and AWS-native Auto Scaling already handled replica scaling.""")
seg(sid, 5, """And fail closed with no fallback. You gave up degraded service. An isolated tenant sees errors rather than being served from commercial. Worth it because an outage is recoverable. Serving an isolated customer from shared infrastructure isn't.""")

sid = table("Trade-offs further down the stack", ["We chose", "We gave up", "Why it was worth it"], [
 (0, ["Copy, then switch", "Free rollback after customers write", "One authoritative home at every moment"], ['ok', 'deny', None]),
 (1, ["GraphQL gateway inside each isolated environment", "Many gateway runtimes, each composing a schema", "Query results never leave the boundary"], ['ok', 'deny', None]),
 (2, ["DataLoader strictly per request", "A little batching efficiency", "A batch only ever holds one tenant's keys"], ['ok', 'deny', None]),
 (3, ["One region per environment, restore-based recovery", "Automatic cross-region failover", "Residency: it's the recovery these customers asked for"], ['ok', 'deny', None]),
 (4, ["Unique IP ranges per environment", "Some address space", "Flow logs and debugging stay unambiguous"], ['ok', 'deny', None]),
], widths=[34, 32, 34])
seg(sid, 0, """There's a second layer of trade-offs further down the stack. These are the ones that show depth when the interviewer drills. Copy, then switch. You gave up free rollback once customers start writing in the isolated environment. Worth it because a tenant has exactly one authoritative home at every moment. And you handled the lost rollback by agreeing a short rollback window with each customer before cutover, then fixing forward.""")
seg(sid, 1, """Running the GraphQL gateway inside each isolated environment. You gave up having one gateway. Now there are many gateway runtimes, each composing its own schema. Worth it because query results are customer data, and they never pass through shared infrastructure.""")
seg(sid, 2, """DataLoader strictly per request. You gave up a little batching efficiency. Worth it because a batch can only ever hold one tenant's keys. You said in your journey you'd make that trade again every time. Say it with that conviction.""")
seg(sid, 3, """One region per environment, with restore-based recovery. You gave up automatic cross-region failover. That will surprise an infra interviewer, so be ready. Copying data to another region can break the customer's residency commitment. Recovery is slower, and it's the one these customers asked for.""")
seg(sid, 4, """And unique IP ranges per environment. Strictly, environments never talk to each other, so ranges could overlap. You kept them unique anyway, because flow logs, security tooling and incident debugging all key on IP addresses. An overlap makes the question, which environment was that address, ambiguous at the worst possible moment. That's a small decision, but it's exactly the kind of operational judgement infra panels love.""")

D = Diagram("The complexity didn't disappear. It moved.")
D.zone(60, 30, 800, 620, 'Option: each team carries part of it', kind='deny', step=0)
for r in range(4):
    for c in range(6):
        D.box('t%d%d' % (r, c), 100 + c * 125, 100 + r * 120, 105, 90, 'team', 'routing · egress', kind='com', step=0, small=True)
D.label(100, 590, '~178 partial implementations', kind='deny', step=0, w=720, size='m', align='center')
D.zone(1060, 30, 800, 620, 'What we did: one platform team carries it', kind='ok', step=1)
for k, n in enumerate(['Router changes', 'Tenant Context Service', 'Shard Manager', 'Shard configuration repository', 'Egress Gateway']):
    D.box('p%d' % k, 1110, 90 + k * 108, 700, 88, n, '', kind='dp' if k in (2, 3) else ('deny' if k == 4 else 'shared'), step=1, small=True)
D.label(60, 720, '“One platform team carrying that was far cheaper than 178 teams each carrying part of it.”', kind='ok', step=2, w=1800, size='l', align='center')
sid = D.build()
seg(sid, 0, """One more trade-off people forget to mention. Avoiding rewrites didn't make the complexity go away. On the left is the alternative: every team carries part of it. Routing logic, egress policy, lifecycle handling, a hundred and seventy-eight partial implementations.""")
seg(sid, 1, """On the right is what you did. The complexity moved to your side. The platform team built and ran the Router changes, the Tenant Context Service, the Shard Manager, the shard configuration repository and the Egress Gateway.""")
seg(sid, 2, """And the sentence to say: one platform team carrying that was far cheaper than a hundred and seventy-eight teams each carrying part of it. Never imply the complexity vanished. An interviewer will immediately ask, so who paid for it? Answer that before they ask.""")

sid = compare("How to say a trade-off",
 ("Defensive", 'deny', 0, ["“There wasn't really a downside.”", "“It was the only option.”", "“Leadership decided that.”", "Sounds like you didn't own the call."]),
 ("Owned", 'ok', 1, ["“We gave up X.”", "“We accepted it because Y.”", "“We contained it with Z.”", "Sounds like the person who decided."]))
seg(sid, 0, """Finally, how to say it. Here are three defensive phrasings. There wasn't really a downside. It was the only option. Leadership decided that. Each one tells the interviewer you didn't own the decision.""")
seg(sid, 1, """Here's the owned version. We gave up this. We accepted it because of that. We contained it with this mechanism. It's the same information, but now you're the person who made the call and lived with the consequences.""")

question("What was the biggest trade-off you made?", 8,
 "Centralisation. Teams gave up some control over deployment config, and every product came to depend on the platform. If we got it wrong, we got it wrong for everyone. We contained that with a written platform contract and by rolling platform changes out tenant by tenant.",
 "Cost, reason and mitigation in three sentences, with no hedging.",
 "Whether you see the downside of your own best decision, and whether you managed it rather than hoped.",
 ["Did a platform change ever hurt several teams at once?", "What was in the platform contract?", "What's the weakest part of the design today?"],
 narr=dict(
  short="""Thirty seconds. Centralisation. Product teams gave up some control over deployment configuration, and every product came to depend on the platform. If we got the platform wrong, we got it wrong for everyone at once. We contained that with a written platform contract, and by rolling platform changes out tenant by tenant, never everywhere at once.""",
  strong="""Why it lands. It picks the trade-off attached to your most important decision, not a minor one. And it goes cost, reason, mitigation, without a single hedge.""",
  testing="""They're testing whether you can see the downside of your own best idea. Candidates who only defend their design sound like they're still selling it. Candidates who name its cost sound like they've operated it.""",
  follow="""Expect: did a platform change ever hurt several teams at once? Don't invent an incident you haven't described. Your contract and staged rollouts are the answer. Then: what was in the contract? What the platform guarantees, what it doesn't, and how teams ask for changes. And: what's the weakest part today? Centralisation still makes the platform a shared dependency, and shard descriptor overrides still need discipline. The monthly review helps, but it depends on people doing it."""))
