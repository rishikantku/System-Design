# -*- coding: utf-8 -*-
from engine import *

chapter(14, "Deep-dive follow-up chains", "Forty minutes on one project means five to seven levels on a single thread. Here are the five threads they'll pull.",
 """Chapter fourteen. Follow-up chains. In a retrospective, the interviewer rarely changes topic. They pick a thread and keep pulling. Why this? What happens when it fails? What did you get wrong? How do you know? Each chain here goes five or six levels deep, the way a real interviewer drills. Watch how each answer sets up the next question, because good answers deliberately leave a door open to the follow-up you're strongest on.""")


def chain(title, levels, intro, closing):
    """levels: (question, short answer, kind, narration)"""
    D = Diagram(title)
    n = len(levels)
    gap = 820 // n
    for k, (q, a, kind, _) in enumerate(levels):
        y = 10 + k * gap
        D.box('q%d' % k, 60, y, 760, gap - 22, 'L%d · %s' % (k + 1, q), '', kind='info', step=k, hl=str(k), small=True)
        D.label(870, y + 10, a, kind=kind, step=k, w=990, size='m')
        if k: D.arrow('q%d' % (k - 1), 'q%d' % k, step=k, kind='neutral', fs='b', ts='t', fo=0.12, to=0.12)
    sid = D.build()
    for k, (_, _, _, narr) in enumerate(levels):
        seg(sid, k, (intro + ' ' if k == 0 else '') + narr + (' ' + closing if k == n - 1 else ''))


chain("Chain 1: the separation", [
 ("Why a separate Shard Manager?", "Placement changes on failure, maintenance, deploys, migrations, capacity — none change the tenant. Identity is static; placement moves.", 'ok',
  """Level one. Why a separate Shard Manager? Your answer: every event that changes placement leaves tenant identity untouched. Identity is static and cacheable. Placement is operational and moves."""),
 ("What happens when a shard fails?", "Replica failure: absorbed, mapping unchanged. Shard replaced: repository → invalidate cache → route.", 'dp',
  """Level two, the natural follow-up. What happens when a shard fails? Separate replica failure, absorbed with no mapping change, from shard replacement: update the repository, invalidate the cache, then route."""),
 ("Did you ever get that order wrong?", "Yes. Invalidated first; cache refilled from old placement; requests reached a retiring shard. Fixed the order, added an alert.", 'deny',
  """Level three. Did you ever get that order wrong? Yes. During maintenance, the cache was invalidated first and refilled from the old placement before the repository update landed, so some requests reached a shard being retired. You fixed the order and added an alert for requests reaching a retired shard."""),
 ("What if the placement cache is lost?", "Nothing is lost. The repository is the source of truth — slower until it refills, still correct.", 'ok',
  """Level four. What if the placement cache is lost? Nothing is lost. The repository is the source of truth. Lookups are slower until the cache refills, but still correct."""),
 ("How did you convince people it was worth a component?", "The same event list that changed my own mind. Evidence, not a principle.", 'shared',
  """Level five. How did you convince people the extra component was worth it? You'd favoured the Router approach yourself, so you used the same event list that changed your mind. Once that list was on the table, coupling was obviously wrong."""),
 ("What would you do differently?", "Design cache invalidation in from day one — three rounds of hardening came from one root.", 'cp',
  """Level six, where many chains end. What would you do differently? Design cache invalidation in from day one."""),
], """Chain one: the separation. This is the chain you most want them to pull, because every level is strong.""",
 """Notice how the whole chain is one idea, identity versus placement, examined from six angles. That's what depth looks like.""")

chain("Chain 2: the isolation boundary", [
 ("Can an isolated request ever reach commercial?", "No fallback path exists. No healthy shard → error + retry. No tenant context → reject.", 'ok',
  """Level one. Can an isolated tenant's request ever reach commercial? There is no fallback path by design. No healthy shard means error and retry. No tenant context means reject."""),
 ("Isn't serving from commercial better than an outage?", "Not for these customers. Outage = reliability problem. Shared infrastructure = compliance failure.", 'deny',
  """Level two. Isn't serving from commercial better than an outage? Give a clear no. An outage is a reliability problem. Serving from shared infrastructure is a compliance failure. Availability comes from replicas."""),
 ("What stops a bug from sending it anyway?", "Three locks: Router fails closed · commercial refuses locked tenants · no data left after the window. Plus an alert.", 'dp',
  """Level three. What stops a bug from sending it anyway? Three independent locks, and an alert on any isolated request seen by commercial."""),
 ("Has a lock ever been tested for real?", "The ~10-minute cutover mis-route: some Routers missed invalidation; lock 2 refused the requests.", 'shared',
  """Level four. Has that ever been tested for real? Yes, the ten-minute cutover mis-route. A few Routers missed invalidation, and lock two refused the requests. Users saw errors, not data served from the wrong place."""),
 ("And the other direction — calls out?", "Network, Egress Gateway, isolated dependencies, readiness check, denial monitoring.", 'cp',
  """Level five. And the other direction? Layers: no network route, the Egress Gateway treating commercial like any destination, dependencies pointing at isolated counterparts, the readiness check, and denial monitoring."""),
 ("How do you know the guarantees hold?", "Commercial-side alert reads zero; egress denials to commercial are zero or explained — checked every cutover.", 'ok',
  """Level six. How do you know the guarantees actually hold? The commercial-side alert should always read zero, and egress denials to commercial services should be zero or explained. Every cutover checks both."""),
], """Chain two: the isolation boundary. This is where interviewers test whether you'll bend a hard guarantee.""",
 """The pattern: a principle, a mechanism, evidence it worked in production, and a way to verify it continuously.""")

chain("Chain 3: infrastructure", [
 ("How does the control plane reach in?", "One private endpoint, connections from the control plane only. In: desired state. Back: metadata.", 'cp',
  """Level one. How does the control plane reach into an isolated environment? One private endpoint that only the control plane's account can connect to, opened from its side only."""),
 ("What about emergency human access?", "No standing access. Break-glass: time-limited, two approvals, every session logged.", 'deny',
  """Level two. What about emergency human access? No standing access. Break-glass is time-limited, needs two approvals, and every session is logged."""),
 ("How does a release roll out?", "Commercial → wave 0 → canaries (24h bake) → everyone in change windows. Shard by shard, own-baseline gates.", 'shared',
  """Level three. How does a release roll out? Commercial, then wave zero, then canaries with a twenty-four hour bake, then everyone within change windows. Inside an environment, shard by shard behind gates against that tenant's own baseline."""),
 ("Can you roll back one tenant?", "Yes — per-environment pointer. Until a schema contract step runs; those ship separately.", 'dp',
  """Level four. Can you roll back one tenant? Yes, each environment has its own deployment pointer, until a schema contract step runs, which is why those ship separately and bake longer."""),
 ("What about customers who freeze changes?", "Max two versions of skew, APIs compatible across it, security patches exempt.", 'info',
  """Level five. What about customers who freeze changes? At most two versions of skew, APIs compatible across that window, and security patches exempt. It came from the pilot bank's first quarter-end."""),
 ("What does a region failure mean?", "No automatic cross-region failover — residency. Restore-based recovery into an allowed region.", 'ok',
  """Level six. And what does a region failure mean for them? No automatic cross-region failover, because copying data elsewhere can break residency. Recovery is restore-based, into a region their rules allow, with targets agreed per customer."""),
], """Chain three: infrastructure. An infra panel will drill from access, to deployment, to recovery.""",
 """Every answer here is a rule with an origin story or a reason. That's what makes infrastructure answers sound operated rather than designed on paper.""")

chain("Chain 4: the GraphQL gateway", [
 ("What was the hardest problem?", "The gateway. Every other service is one box; the gateway is every edge at once.", 'shared',
  """Level one. What was the hardest problem? The GraphQL gateway. Every other service is one box on the dependency map. The gateway is every edge of it at once."""),
 ("Why not keep one shared gateway?", "Query results are customer data. One routing bug calls commercial. Gateway runs inside each environment.", 'deny',
  """Level two. Why not keep one shared gateway? Query results are customer data, and one routing bug would call a commercial backend. So it runs inside each isolated environment."""),
 ("How does each gateway get its schema?", "Composed from services actually present. Pushed in by the control plane at deploy — never pulled.", 'cp',
  """Level three. How does each gateway get its schema? Composed per environment from the services actually present, and pushed in by the control plane at deploy time. Never pulled from commercial."""),
 ("What went wrong with hydration?", "The gateway makes the call, not the service — invisible to per-service readiness. Check extended to the hydration graph.", 'dp',
  """Level four. What went wrong with hydration? The gateway makes the hydration call, not the service, so per-service readiness couldn't see it. The check was extended to the hydration graph, failing composition at build time."""),
 ("And DataLoader?", "Batch ran on another thread without tenant context; default endpoint was commercial. Context captured at loader creation; fail closed.", 'deny',
  """Level five. And DataLoader? The batch ran later on another thread without tenant context, and its default endpoint was commercial. Context is now captured into the loader at creation, and a batch without it fails closed."""),
 ("Why didn't normal testing catch it?", "Normal tests check what comes back. We checked where every downstream call went.", 'ok',
  """Level six. Why didn't normal testing catch it? Because normal testing checks what comes back. A query can return the right answer while one call went to commercial. You checked where every call went."""),
], """Chain four: the GraphQL gateway. This is the deepest technical chain, and it can easily go past six levels.""",
 """If they go further, per-request loaders and the tenant-keyed platform cache are your seventh level. Don't invent latency numbers. Say you watched batch counts and latency.""")

chain("Chain 5: execution across 178 teams", [
 ("How did you plan across 178 teams?", "Planned dependencies, not migrations. A three-question form; catalogue was out of date.", 'shared',
  """Level one. How did you plan across a hundred and seventy-eight teams? You planned dependencies, not migrations, starting from a three-question form because the catalogue was out of date."""),
 ("Why that order?", "Dependency is the only hard constraint; priority, traffic, risk and readiness shaped the rest.", 'dp',
  """Level two. Why that order? Dependencies are the only hard constraint. Business priority, traffic, risk and readiness shaped the rest."""),
 ("A team had no capacity. What did you do?", "Moved them later on purpose after checking dependents. If blocking: priority conversation with the map.", 'info',
  """Level three. A team had no capacity. What did you do? Moved them later in their tier on purpose, after checking nothing depended on them. If something did, it became a priority conversation with leadership, with the dependency map in front of everyone."""),
 ("What if a team refused?", "The custom-scripts team: not resistance — a real gap. Added to the model; 4–5 teams reused it.", 'ok',
  """Level four. What if a team simply refused? Tell the custom-scripts team. It looked like resistance, it was a real gap in the model, and four or five teams used the addition."""),
 ("Where did it stall?", "Phase two — an adoption problem. Office hours, visible status, chasing owners, fixing blockers once.", 'deny',
  """Level five. Where did it stall? Phase two. It was an adoption problem, and what moved it was unglamorous."""),
 ("How did you know a team was really done?", "Status computed by the tool. Self-reported status was always greener than reality.", 'cp',
  """Level six. How did you know a team was really done? The tool computed status from its own checks, because self-reported status was always greener than reality."""),
], """Chain five: execution. This is the chain that decides whether you get the Staff signal for leadership.""",
 """Across all five chains, notice that you never needed a new fact. Depth comes from connecting the same consistent story from different angles.""")

sid = cards("How to handle any chain", [
 (0, "Answer the level you're asked", "Don't pre-empt three levels down. Let them pull.", 'info'),
 (0, "Leave a door open", "End on a detail that invites your strongest follow-up.", 'ok'),
 (1, "When you hit the edge of what you know", "Say where your ownership stopped. Don't invent.", 'deny'),
 (1, "Come back up", "After a deep dive, tie it back to the decision it came from.", 'cp'),
], cols=2)
seg(sid, 0, """Four rules for any chain. Answer the level you're asked, not three levels down. Let the interviewer pull. And leave a door open. End your answer on a detail that invites the follow-up you're strongest on. We learned that order the hard way is an invitation.""")
seg(sid, 1, """When you reach the edge of what you know, say where your ownership stopped. Never invent a number or a mechanism to survive one more level. It will contradict something later. And after a deep dive, come back up. Tie the detail back to the decision it came from. That's what shows you still see the whole system.""")
