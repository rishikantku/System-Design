# -*- coding: utf-8 -*-
"""Hiring manager round. Every personal detail here comes from specialization-aic.html
(the reader's own retrospective material). Nothing about their experience is invented here."""
from lib import *
import research as R

AIC = '../../specialization-aic.html'

# ---------------------------------------------------------------- story bank
STORIES = [
 dict(id='thesis', title='The platform thesis — spotting the problem nobody owned',
  one='Three product teams designed their own per-customer isolation in one week; I wrote a one-page note to my VP asking to pause that until we decided what belonged in the platform, and was asked to lead the design.',
  beats=['About a month into Isolated Cloud, sat through design reviews from three product teams in the same week.',
         'Jira was planning its own per-customer stack with routing; Confluence something different; a third team waiting to copy whichever looked better.',
         '"We were not building one Isolated Cloud. We were about to build five or six."',
         'Wrote a one-page note to the VP that weekend; the ask was to pause product-level isolation designs until the platform boundary was decided.',
         'Listed everything a service does differently for an isolated tenant and marked each item with the Jira and Confluence leads: product-specific or same for everyone.',
         'Almost everything was the same for everyone → the principle: isolation is a platform capability, not a product feature.'],
  answers=['Tell me about a time you identified a problem nobody else saw', 'Biggest technical decision',
           'How do you influence beyond your team', 'Tell me about taking initiative', 'Describe your most impactful project'],
  signal='Scope: found an organisation-level problem, framed it, and got a mandate for it without being assigned one.'),
 dict(id='migration', title='Migrating ~178 teams onto the platform',
  one='I planned dependencies, not migrations: a three-question form rebuilt the dependency map, tiers L0–L3 (plus L2.5) sequenced the work, and an onboarding tool made adoption cheaper than resistance.',
  beats=['The service catalogue was wrong, so every team got a short form: what do you call, what calls you, do you send data outside Atlassian.',
         'Tiers: L0 identity and edge, L1 shared platform, L2 the products first customers needed, L3 the tail, plus L2.5 inserted during planning to avoid renumbering dashboards and runbooks.',
         'Only the dependency graph was a hard constraint; priority, traffic, risk and team readiness shaped the rest.',
         'Onboarding tool in five steps: readiness check, generated shard descriptor, encrypted transfer, validation, status to a shared dashboard.',
         'Status was computed by the tool, never self-reported — self-reported status was always greener than reality.',
         'Onboarding went from a few weeks with hands-on help to a few days on their own.',
         'Phase two (the tail) took as long as phase one: it was an adoption problem, not an engineering one.'],
  answers=['How would you get thousands of teams to migrate', 'Influence without authority', 'Large-scale execution',
           'Prioritisation', 'Where did it stall and what did you do', 'Stakeholder management'],
  signal='Execution at organisational scale, with a mechanism (cost of adoption) rather than a mandate.'),
 dict(id='jira', title='The Jira lead: "not handing their pager to someone else\'s roadmap"',
  one='The biggest product lead objected to losing deployment control; I spent two weeks in one-on-ones before the review, and answered the fear with shard descriptors and a written platform contract.',
  beats=['Wrote the proposal with both options side by side, then walked the biggest product leads through it one-on-one before any formal review.',
         'If Jira and Confluence said no in the room, the proposal was dead.',
         'The objection was fair: losing control of deployments, and waiting on a platform team\'s backlog.',
         'Answer: teams keep business logic and size their own shards through shard descriptors; plus a written contract — what the platform guarantees, what it does not, how teams ask for changes.',
         'After the big two were on board, the architecture review was short.'],
  answers=['Tell me about a disagreement', 'How do you get buy-in', 'Difficult stakeholder', 'Conflict with a peer'],
  signal='Treated the objection as information about the design, and changed the design rather than winning the argument.'),
 dict(id='sre', title='The SRE lead: should an unhealthy shard fall back to commercial?',
  one='A fair reliability instinct that would have been a compliance breach; the answer was no fallback anywhere, and reliability from replicas instead.',
  beats=['Raised in an architecture review: if the isolated shard is unhealthy, send the tenant to commercial — some service beats none.',
         'In a normal system that is good practice. Here it would serve an isolated customer from shared infrastructure.',
         'An outage is a reliability problem; serving from shared infrastructure is a compliance failure.',
         'Decision: fail closed everywhere, and buy availability with replicas inside the shard, not an escape route.',
         'Backed by three independent locks and an alert whose expected value is zero.'],
  answers=['Disagreement with a senior engineer', 'A time you held a hard line', 'Trade-off between availability and correctness',
           'How do you make irreversible decisions'],
  signal='Distinguished a reliability problem from a compliance failure, and designed the alternative rather than just refusing.'),
 dict(id='overruled', title='Being overruled on the phase-one date',
  one='After the rehearsal I wanted to delay phase one until invalidation could be confirmed on every Router; leadership held the date for the pilot commitment, I committed, and the confirmation step landed after the first production incident.',
  beats=['The staging rehearsal exposed stale tenant context on some Router instances.',
         'I wanted to delay until we could confirm invalidation on every Router.',
         'Leadership held the date because of the pilot commitment. I committed.',
         'We shipped invalidation as an explicit step in the switch; the every-Router confirmation came after the ten-minute production mis-route.',
         'In hindsight we were both partly right: the locks held, the incident was errors rather than data served from the wrong place.'],
  answers=['Tell me about a time you were overruled', 'Disagree and commit', 'A decision you would make differently',
           'How do you handle being wrong'],
  signal='Disagreed, committed without resentment, and drew a design lesson rather than a grievance.'),
 dict(id='scripts', title='The team with years of custom deployment scripts',
  one='What looked like resistance was a real gap in the model: their scaling pattern could not be expressed in a shard descriptor, so we changed the model and four or five teams reused the addition.',
  beats=['They pushed back hard and did not want to touch their scripts.',
         'I assumed resistance to change. Then I sat down with their tech lead.',
         'Their service scaled on a pattern the shard descriptor genuinely could not express.',
         'We added it to the model; they migrated; four or five later teams used the same addition.',
         'After that: if two teams hit the same thing, it is a platform problem, not a team problem.'],
  answers=['A team refused to adopt your thing', 'Mentoring and coaching', 'What did you learn about leading across teams',
           'A time you were wrong about someone'],
  signal='Curiosity over authority, and a systemic fix instead of a one-off exception.'),
 dict(id='incident1', title='The ten-minute cutover mis-route',
  one='A few Router instances missed the tenant-context invalidation during an early production cutover; the second lock held, so users saw errors rather than data from shared infrastructure, and the lasting fix made the switch incomplete until every Router confirms.',
  beats=['Early production cutover; cache invalidation was already a step after the rehearsal.',
         'A few Router instances did not receive it; for about ten minutes a small share of that customer\'s requests hit the commercial runtime.',
         'The commercial side refused them because the tenant was locked as migrated — errors, not a breach.',
         'Detected from the per-tenant error rate before the customer raised it; forced a refresh.',
         'Lasting fix: a switch is not complete until every Router instance confirms the new context.'],
  answers=['Tell me about a failure', 'A production incident you caused', 'How do you handle incidents',
           'What did it reveal about your design'],
  signal='The fix changed the process so the class of failure cannot recur — not "be more careful".'),
 dict(id='incident2', title='The shard-replacement ordering bug',
  one='We invalidated the cache before the repository update landed, so it refilled with stale placement and some requests reached a shard being retired; the fix was the ordering rule plus an alert.',
  beats=['Shard replacement during maintenance: placement updated and cache invalidated, but in the wrong order.',
         'The cache refilled from the old placement before the repository update landed.',
         'Fix: update the shard configuration repository first, then invalidate the cache, then route new traffic.',
         'Added an alert for any request reaching a retired shard.',
         'Both incidents traced to the same root: cache invalidation designed in late.'],
  answers=['A bug that taught you something', 'Failure', 'What would you do differently', 'How do you prevent recurrence'],
  signal='Found the pattern across two incidents rather than treating them as separate bugs.'),
 dict(id='data', title='Moving live customers out of shared stores',
  one='Copy then switch, with one rule repeated in every review — a tenant has one home at a time — because dual-write kept isolated tenants wired to commercial and starting fresh pushed our risk onto the customer.',
  beats=['Three options weighed: start fresh, dual-write, or copy then switch.',
         'Start fresh pushed years of history and audit trails onto the customer; dual-write changed every write path and made both environments look authoritative.',
         'Chosen: copy then switch. Bulk copy, catch-up runs, short freeze, validation (ownership, counts, checksums), switch, rollback window, delete and verify.',
         'Service owners wrote the tenant-scoped extraction because only they knew their schema; the platform ran the encrypted transfer and the ownership check.',
         'The rollback conversation happened with each customer before cutover, not during an incident.'],
  answers=['A difficult technical trade-off', 'Risky change to production', 'How do you de-risk a migration',
           'Customer-facing commitment'],
  signal='Named what makes it irreversible, and negotiated the rollback window in advance.'),
 dict(id='graphql', title='The GraphQL gateway and DataLoader',
  one='The gateway was every edge of the dependency map at once, and DataLoader silently lost tenant context on the batch thread where the default endpoint was commercial — caught because we checked where every downstream call went, not just what came back.',
  beats=['Every other service is one box on the dependency map; the gateway is every edge.',
         'Ran the gateway inside each isolated environment because query results are customer data.',
         'Hydration: the gateway makes the call, not the service, so per-service readiness checks could not see it — extended the check to the hydration graph, failing composition at build time.',
         'DataLoader batches ran on another thread without tenant context; the default endpoint was commercial — a fallback hidden in a library.',
         'Fixes: capture context into the loader at creation, fail closed without it, and make loaders strictly per request.',
         'Accepted slightly less batching for the guarantee.'],
  answers=['Hardest technical problem', 'A subtle bug', 'Deep technical ownership', 'How do you verify correctness'],
  signal='Tested where calls went, not only what came back — a class of verification most people skip.'),
 dict(id='ops', title='Running it in production',
  one='Provisioning went from about two days to around five hours by making every step idempotent and resumable, and the signal that caught most problems early was egress denials.',
  beats=['Declarative provisioning: every step "make sure this exists and matches", so a failure resumes instead of duplicating.',
         'Quota check first, after a fresh account hit a database-instance limit mid-deploy; register last, so a half-built environment can never take traffic.',
         'Four signals watched: shard health, latency and errors per tenant and product, migration progress per team, egress denials.',
         'Egress denials were expected to be a compliance metric and became the best early warning.',
         'Rollout: commercial, then Atlassian-owned environments, then canaries with a bake, then everyone within change windows.'],
  answers=['Operational excellence', 'What do you measure', 'How do you make releases safe', 'On-call and reliability'],
  signal='Chose leading indicators, and made safety a property of the pipeline rather than of careful people.'),
 dict(id='impact', title='Business impact',
  one='Regulated customers who could not use our cloud at all could move, starting with a large bank, and isolation became a platform capability instead of 178 separate redesigns.',
  beats=['These customers\' compliance teams would not sign off on shared infrastructure, however good the logical isolation.',
         'Isolation became a platform capability; new products inherit it without redesigning anything.',
         'Onboarding a team: a few weeks with help → a few days alone.',
         'Measured by teams migrated (computed by the tool), time to onboard, and problems per cutover.',
         'The cost structure was honest: a dedicated environment costs multiples of a shared one, and per-shard sizing was the lever.'],
  answers=['What was the business impact', 'How do you measure success', 'Why did this matter to the company',
           'Connecting engineering to revenue'],
  signal='Ties an architecture decision to a market the company could not otherwise serve.'),
]

# ---------------------------------------------------------------- behavioural questions
def Q(id, q, tests, story, structure, strong, follow, challenges, avoid, signal, level='L3', src=None):
    return dict(id=id, q=q, tests=tests, story=story, structure=structure, strong=strong,
                follow=follow, challenges=challenges, avoid=avoid, signal=signal, level=level, src=src)

QUESTIONS = [
 Q('career', 'Walk me through your career progression.',
   'Whether your scope has grown, and whether you know why it grew.',
   None,
   'Three beats, not a CV reading: what you owned early, the shift in scope, what you own now — each with the trigger that caused the change.',
   'End on platform-wide scope: the Isolated Cloud thesis, ~178 teams, no authority over any of them. Then stop and let them pull.',
   ['What triggered each promotion?', 'Why did you move when you did?', 'What scope changed each time?'],
   ['They may probe a gap or a short stint — answer plainly, without defensiveness.'],
   'Listing every project chronologically. Three minutes of history with no arc.',
   'Scope growth described as a series of decisions, not a series of job titles.', 'L2', 'exp-exp'),
 Q('migrate5000', 'We have a platform product used by 5,000 teams. How would you get those teams to migrate? What about the holdouts?',
   'Influence without authority at platform scale — the closest thing to a LinkedIn-specific behavioural question found in the research.',
   'migration',
   'Principle → mechanism → sequencing → holdouts → evidence.',
   'Make adoption cheaper than resistance (generated config, a tool in their own pipeline), sequence by dependency so nobody is blocked, '
   'publish computed status rather than self-reported, and treat a repeated blocker as a platform problem. For holdouts: find out whether '
   'it is resistance or a real gap — the custom-scripts team turned out to be a gap in our model, and fixing the model moved four or five '
   'teams after them.',
   ['What if a team simply refuses?', 'How do you sequence it?', 'How do you measure adoption?', 'What did you do when it stalled?'],
   ['"Escalate to leadership" as a first move reads as junior — keep it as the last resort, with the dependency map in the room.'],
   'Claiming a mandate did the work. Mandates do not work at that scale, and the interviewer knows it.',
   'A mechanism, not a mandate: the cost of adoption is the lever you control.', 'L4', 'exp-exp'),
 Q('complex', 'Tell me about the most complex project you have led — including its security aspects and the challenges.',
   'Depth of ownership, and whether the complexity was real.',
   'thesis',
   'Context → why it was hard → your decision → what it cost → outcome.',
   'Isolated Cloud: dedicated environments for regulated customers, ~178 teams built on the assumption that one deployment serves every '
   'tenant. Security: isolation guarantees enforced by the platform (fail closed, centralised egress policy, customer-managed keys), not by '
   'each team remembering. Hardest part: the GraphQL gateway, every edge of the dependency map at once.',
   ['What was your role versus the team\'s?', 'What would you do differently?', 'How did the security review go?',
    'What was the hardest technical problem inside it?'],
   ['They may ask what *you* personally built versus what the programme built — be precise and generous.'],
   'Describing the system without saying which decisions were yours.',
   'Names the decision and its cost, not just the architecture.', 'L3', 'lc-staff'),
 Q('conflict', 'Tell me about a conflict or disagreement in a critical project.',
   'Whether you treat disagreement as information, and whether you make the other side look reasonable.',
   'jira',
   'Their position → why it was fair → what you changed → how it resolved → what it cost.',
   'The Jira lead\'s objection — not handing their pager to someone else\'s roadmap — was fair. Two weeks of one-on-ones before any formal '
   'review, then shard descriptors kept sizing with the teams and a written contract set the platform\'s obligations. The review itself was short.',
   ['Did you have to give anything up?', 'What if they had still said no?', 'Were you ever overruled?'],
   ['"Tell me about a conflict you lost" — use the overruled story, told without grievance.'],
   'Making the other person sound unreasonable, or picking a trivial conflict.',
   'Changed the design in response to the objection, rather than winning the argument.', 'L3', 'lc-staff'),
 Q('overruled', 'Tell me about a time you were overruled.',
   'Disagree-and-commit, and whether you carry resentment.',
   'overruled',
   'What you wanted → the decision → how you committed → how it played out → what you learned.',
   'Wanted to delay phase one until invalidation was confirmed on every Router; leadership held the date for the pilot commitment; I '
   'committed, we shipped invalidation as a switch step, and the confirmation step came after the first incident. In hindsight both of us '
   'were partly right — and my own lesson is that I should have designed invalidation in from day one.',
   ['Would you push harder next time?', 'How did you tell your team?', 'What did the incident cost?'],
   ['They may press on whether you sandbagged after losing — have the evidence that you executed fully.'],
   'Telling it as a grievance, or implying the decision was stupid.',
   'Owns the part that was yours (invalidation designed late) instead of blaming the date.', 'L4'),
 Q('failure', 'Tell me about a significant failure.',
   'Whether your fixes remove a class of failure, and whether you self-report honestly.',
   'incident1',
   'What happened → impact → how you found it → the fix → what changed structurally.',
   'The ten-minute cutover mis-route: a few Routers missed the invalidation, the commercial side refused those requests because the tenant '
   'was locked, and we caught it from per-tenant error rates before the customer noticed. The lasting fix made a switch incomplete until '
   'every Router confirms the new context.',
   ['Why had the rehearsal not caught it?', 'What was the second incident?', 'What did it reveal about the design?'],
   ['"What was the customer impact, exactly?" — be precise: errors for a small share of requests for about ten minutes.'],
   'A fix that amounts to "we were more careful afterwards".',
   'Names what the incident revealed about the design, and the mechanism that changed.', 'L3'),
 Q('quality', 'How do you define a quality product or system?',
   'Craftsmanship philosophy, and whether you can enforce it across teams you do not own.',
   'ops',
   'Definition → how you make it observable → how you enforce it without authority.',
   'Quality is what survives contact with production: a system where the unsafe thing is hard to do. Concretely — readiness checks that '
   'fail a service that is not ready, status computed rather than reported, health gates against that tenant\'s own baseline, and overrides '
   'that need an owner and a reason, reviewed monthly.',
   ['How do you enforce it across teams you do not own?', 'What do you measure?', 'Where did this fail?'],
   ['They may push on speed versus quality — have the staged-rollout answer ready.'],
   'Abstract virtue words with no mechanism behind them.',
   'Quality expressed as mechanisms and defaults, not as exhortation.', 'L3', 'gd'),
 Q('review', 'What is your strategy for code reviews, especially as a team grows with more junior engineers?',
   'Mentoring at scale and engineering standards.',
   None,
   'What you optimise for → what you automate → how you teach in review → how you keep latency low.',
   'Automate what a machine can catch so review is about design and intent; separate blocking comments from suggestions; review for the '
   'reader six months from now; keep review latency low because slow review teaches people to batch large changes.',
   ['How do you handle a reviewer who blocks everything?', 'How do you teach without demoralising?'],
   ['If asked for an example, use a concrete one from your own experience rather than a principle.'],
   'Listing lint rules. Or claiming you review everything personally at scale.',
   'Scales judgement through defaults and teaching, not through personal gatekeeping.', 'L3', 'gd'),
 Q('legacy', 'You join a large team that owns a legacy application: poor testing, no monitoring, slow responses and buggy deploys. What do you do in your first 90 days?',
   'Sequencing under ambiguity, and whether you measure before you act.',
   None,
   'Measure → stop the bleeding → make one failure class impossible → automate → then refactor.',
   'First: instrument, because without numbers every argument is opinion. Then stop the bleeding (the deploy path — most bugs reach users '
   'through it). Then make one class of failure impossible rather than fixing instances. Then automate the checks. Only then talk about '
   'architecture. Publish the numbers weekly so progress is visible to the team and to leadership.',
   ['What do you fix first?', 'How do you get the team to care?', 'How do you show progress?', 'What if leadership wants features instead?'],
   ['They may push on delivering features in parallel — say what you would trade and why.'],
   'Proposing a rewrite. Or fixing what annoys you rather than what hurts users.',
   'Sequenced by risk and evidence, with visible progress; no heroics.', 'L4', 'gd'),
 Q('ambiguity', 'Tell me about a time you worked on something genuinely ambiguous.',
   'Whether you can bound a problem nobody has defined.',
   'thesis',
   'The fog → how you bounded it → the decision that unlocked it → what you deliberately left out.',
   'Nobody had defined which parts of isolation belonged to the platform. I made the list of everything a service does differently for an '
   'isolated tenant and marked each item with the two biggest product leads. Almost everything landed on the same-for-everyone side, and '
   'that produced the principle the whole design came from.',
   ['What did you deliberately leave out of scope?', 'How did you know the line was right?', 'What would you move today?'],
   ['"What if the leads had disagreed?" — then the exercise would have produced a different, narrower platform. Say so.'],
   'Pretending there was a plan all along.',
   'Produced the principle from evidence, with the people who had to live with it.', 'L4'),
 Q('priority', 'How do you prioritise when everything is urgent?',
   'Judgement about sequencing and about saying no.',
   'migration',
   'The constraint that is real → the ordering rule → what you dropped → how you communicated it.',
   'Only the dependency graph was a hard constraint; everything else — business priority, traffic, risk, team readiness — was negotiable. '
   'A pure dependency sort gives a valid order and an unworkable plan, so the order was reviewed with leadership every two weeks as customer '
   'commitments moved.',
   ['What did you refuse to do?', 'How did you handle a team with no capacity?', 'Who decided when you disagreed?'],
   ['They may ask about a time you got the priority wrong — phase two taking as long as phase one is the honest answer.'],
   'Saying you worked harder. Or pretending nothing was dropped.',
   'Distinguishes hard constraints from negotiable ones, and re-plans on a cadence.', 'L3'),
 Q('mentor', 'Tell me about mentoring someone.',
   'Whether you grow people, not just systems.',
   'scripts',
   'Situation → what you did → what changed for them → what changed for you.',
   'Use a real example from your own experience. The related platform instinct: after the custom-scripts team, I stopped treating blockers '
   'as team problems — if two teams hit the same thing it went on the platform backlog, which is mentoring at the level of a system.',
   ['What did they struggle with?', 'How did you adapt your approach?', 'Where did it not work?'],
   ['If you do not have a formal mentee story, use pairing during the early migrations — but keep it truthful.'],
   'Claiming credit for someone else\'s growth. Vague "I helped them level up".',
   'Specific behaviour change in the other person, and a systemic version of the same help.', 'L3'),
 Q('whylinkedin', 'Why LinkedIn? And why this role, now?',
   'Genuine motivation and fit. Reported in several experiences including the Sep 2025 infrastructure loop.',
   None,
   'What you want to do next → why this team specifically → what you bring that fits.',
   'This one must be in your own words, and it must be specific to the team you are talking to. See the worksheet below — do not '
   'improvise it on the day, and do not let me write it for you.',
   ['What would you want to work on here?', 'What do you expect to be different from Atlassian?', 'What are you looking for in your next role?'],
   ['A vague answer here is one of the few things that can sink an otherwise strong loop.'],
   'Generic praise for the company. Reciting the careers page. Anything you would say about three other employers.',
   'A specific problem you want to work on, connected to what you have already done.', 'L2', 'blind-in'),
 Q('zookeeper', 'Scenario: how would you secure access to a shared infrastructure component with mTLS across the fleet — and how long would it take?',
   'Estimation realism inside a behavioural round. A Sep 2025 candidate got exactly this (Zookeeper + mTLS) and proposed two quarters; a commenter said the real programme took far longer.',
   'migration',
   'Phases → the unknown that dominates → what you would measure → how you would de-risk the estimate.',
   'Estimate in phases with named risks rather than a single number: inventory and discovery first (the dependency map is always wrong), '
   'then dual-mode support so both authenticated and legacy paths work, then migration by tier with the noisiest consumers first, then '
   'enforcement and removal of the legacy path. The long pole is never the crypto — it is the consumers you have not found.',
   ['What if a team cannot migrate?', 'How do you enforce without breaking production?', 'Why is your estimate different from reality?'],
   ['They may deliberately challenge an optimistic estimate — welcome it and show what would change the number.'],
   'A confident single number with no phases and no unknowns.',
   'Estimates as ranges tied to discovery, and a migration shape you have actually run.', 'L4', 'blind-in'),
 Q('crossfn', 'Tell me about working with people outside engineering.',
   'Cross-functional collaboration, especially where the constraint is not technical.',
   'data',
   'Who → what they needed → what changed in your design → outcome.',
   'Security and compliance signed off on the deletion step before the first cutover, and the rollback window was agreed with each customer '
   'in advance rather than during an incident. Both changed the engineering plan.',
   ['Who pushed back hardest?', 'How did you handle a requirement you disagreed with?'],
   ['Watch for the trap of describing them as obstacles.'],
   'Treating non-engineering stakeholders as blockers to be routed around.',
   'Non-engineering requirements changed the design, and you can say exactly how.', 'L3'),
 Q('deadline', 'Tell me about delivering under a hard deadline.',
   'Trade-off judgement under pressure.',
   'overruled',
   'The commitment → what you cut → what you refused to cut → the outcome.',
   'The pilot date was held. What we cut was the every-Router confirmation step; what we did not cut was invalidation being an explicit '
   'step, the three locks, or the validation before switching. The incident that followed hit the thing we cut, which is exactly the trade '
   'we knowingly made.',
   ['What would you cut differently now?', 'How did you decide what was safe to cut?'],
   ['Do not pretend you cut nothing — that reads as either lucky or dishonest.'],
   'Heroic all-nighters as the answer.',
   'Named what was cut, and connected the later incident to that choice without excuses.', 'L4'),
 Q('disagree_tech', 'Tell me about a technical decision you changed your mind on.',
   'Whether evidence moves you.',
   'thesis',
   'Your first position → what changed it → what you did about it.',
   'I first favoured resolving the shard in the Router — simpler, one component. Listing every event that changes placement (failure, '
   'maintenance, deploys, migrations, capacity) showed none of them change who the tenant is, so placement moved to the Shard Manager. '
   'I used that same list to convince everyone else.',
   ['Who disagreed with the change?', 'What did it cost?', 'How do you decide when evidence is enough?'],
   [],
   'Framing it as though you always knew.',
   'Changed your own mind from evidence, then used the same evidence to align others.', 'L3'),
 Q('measure', 'How do you measure success for a platform team?',
   'Whether you can define success when you do not own the user-facing metric.',
   'impact',
   'Adoption → time-to-value → incidents caused → the business outcome behind them.',
   'Teams fully migrated as computed by the tool (never self-reported), time for a team to onboard (weeks with help → days alone), problems '
   'per cutover, and behind them the business outcome: customers who could not use our cloud at all could move.',
   ['Which metric moved slowest?', 'What did you stop measuring?', 'How do you avoid vanity metrics?'],
   ['"Teams migrated" can be gamed — explain why computed status exists.'],
   'Counting shipped features.',
   'Metrics that a platform can actually be held to, including one that made you look bad.', 'L3'),
 Q('onboard90', 'What would your first 90 days here look like?',
   'Whether you know how to arrive as a senior outsider.',
   None,
   'Learn → find the load-bearing problem → ship something small → propose the bigger thing.',
   'Weeks 1–3: read the systems and the incident history, meet the teams that depend on us, write down the questions nobody can answer. '
   'Weeks 4–8: ship something small in the critical path so I am operating, not just observing. Weeks 9–12: bring a written proposal for the '
   'thing that keeps hurting, with the evidence gathered in the first two phases.',
   ['What would you change first?', 'How do you build credibility?', 'What if you disagree with the current architecture?'],
   ['Avoid promising a rewrite or criticising decisions you do not yet understand.'],
   'Arriving with a plan before you have arrived.',
   'Earns the right to propose by operating first.', 'L2'),
]

CRAFT = [
 ('Code quality and structure', 'Show the seam: how you separated what teams own (business logic, sizing) from what the platform owns.',
  'Talk about the shard-descriptor model as an interface, and why a generated starting file beat writing a spec.'),
 ('Testing', 'Rehearsals in staging before the first production cutover; validation gates (ownership, counts, checksums) that block the switch.',
  '"A rehearsal found stale tenant context before a customer ever saw it — that is what rehearsals are for."'),
 ('CI/CD and release safety', 'Wave-based rollout, bake time, health gates against that tenant\'s own baseline, automatic halt on regression, per-tenant rollback until a schema contract step.',
  'Expand-then-contract for schema is the detail that shows you have actually shipped this way.'),
 ('Metrics', 'Four signals: shard health, per-tenant and per-product latency and errors, migration progress, egress denials.',
  'Say which one was the leading indicator and why it surprised you.'),
 ('Operability', 'Idempotent, resumable provisioning; register last; drift reconciliation; break-glass access with two approvals and full logging.',
  'These are the answers to "how do you run it at 3 a.m." without ever using the phrase.'),
 ('Reactive / async systems', 'Where you used queues and event-driven flows, and where you deliberately did not.',
  'If the interviewer goes deep here, connect to the AI-coding round: back-pressure, idempotency, poison messages.'),
]

def build():
    rep = [q for q in R.Q if q['r'] == 'hm']
    t = R.THEMES['hm']

    rep_html = ''
    for q in rep:
        srcs = ' · '.join('<a href="%s" target="_blank" rel="noopener">%s</a>'
                          % (R.SOURCES[s]['url'], R.SOURCES[s]['name'].split('—')[0].strip()) for s in q['src'])
        rep_html += acc(q['q'],
            '<p><b>Why it is asked:</b> %s</p><p><b>Reported follow-ups:</b></p><ul>%s</ul>'
            '<p><b>What to prepare:</b> %s</p><div class="src">Reported %s · %s · %s · %s</div>' % (
                esc(q['pat']), ''.join('<li>%s</li>' % esc(f) for f in q['fu']), esc(q['prep']),
                esc(q['d']), esc(q['role']), esc(q['loc']), srcs),
            tag({'A': 'hi', 'B': 'med', 'C': 'low'}[q['conf']], 'conf ' + q['conf']) +
            tag({'high': 'hi', 'medium': 'med', 'one-off': 'low'}[q['rec']], q['rec']))

    follow_patterns = card(table(['After almost any story, expect', 'Have ready'], [
        ['"What was your role versus the team\'s?"', 'A precise boundary: the principle, the architecture, the tiering, the tool — and who did the rest'],
        ['"What would you do differently?"', 'Invalidation designed in from day one; the contract published before phase one; the gateway mapped as every edge'],
        ['"What did it cost?"', 'One more component and one more hop; teams gave up some deployment control; a dedicated environment costs multiples'],
        ['"How did you know it worked?"', 'Computed status, validation gates, the commercial-side alert reading zero'],
        ['"What did you learn?"', 'Mandates do not work at 178 teams; if two teams hit the same thing it is a platform problem'],
        ['"Who disagreed?"', 'Jira lead, SRE lead, the custom-scripts team, leadership on the date — four different kinds of disagreement'],
    ]), title='Likely follow-up patterns')

    # story bank
    story_html = ''
    for s in STORIES:
        sid = 'hm.story.' + s['id']
        reg('hm', sid, 'Story bank', s['title'], weight=2, kind='story')
        body = ('<div data-id="%s" data-label="%s">%s<p class="lead">%s</p>'
                '<h4>The beats, in order</h4><ol>%s</ol>'
                '<h4>Questions this story answers</h4><div class="tags">%s</div>'
                '%s%s</div>') % (
            sid, esc(s['title']), tag('exp', 'Your experience'), rich(s['one']),
            ''.join('<li>%s</li>' % rich(b) for b in s['beats']),
            ''.join('<span class="tag gen">%s</span>' % esc(a) for a in s['answers']),
            note(s['signal'], 'good', 'Staff-level signal'),
            tracker(sid, statuses=[('solved', 'Can tell it cold'), ('revise', 'Needs work'), ('failed', 'Rusty')],
                    note_ph='Say it out loud in 90 seconds. Note where you rambled…'))
        story_html += acc(titled(s['title'], '90-second story'), body, tag('exp', 'yours'), raw=True)

    # behavioural questions
    q_html = ('<div class="filters" data-filter-scope="#bq > details">'
              '<input class="search" placeholder="Search questions…">'
              + ''.join('<button class="fchip" data-fk="level" data-fv="%s">%s</button>' % (k, v)
                        for k, v in [('L2', 'L2 fundamentals'), ('L3', 'L3 interview'), ('L4', 'L4 staff pressure')])
              + '<span class="count"></span></div><div id="bq">')
    for qq in QUESTIONS:
        qid = 'hm.q.' + qq['id']
        reg('hm', qid, 'Behavioural', qq['q'][:60], weight=1, kind='question', level=qq['level'])
        st = next((s for s in STORIES if s['id'] == qq['story']), None)
        story_line = ('<p><b>Your story:</b> %s — <a href="#sec-stories">see the story bank</a>.</p>%s' % (esc(st['title']), tag('exp', 'Your experience'))
                      if st else note('No prepared story for this one — it needs your own words. Use the worksheet if it is about motivation.', 'warn', 'Yours to write'))
        src_line = ''
        if qq['src']:
            s = R.SOURCES[qq['src']]
            src_line = '<div class="src">Reported: <a href="%s" target="_blank" rel="noopener">%s</a> · %s</div>' % (s['url'], s['name'], s['date'])
        stages = [
            stage('What the interviewer is testing', rich(qq['tests'])),
            stage('Your story', story_line),
            stage('Structure', rich(qq['structure'])),
            stage('A strong answer', rich(qq['strong'])),
            stage('Follow-up questions', '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(f) for f in qq['follow'])),
            stage('Possible challenges', '<ul>%s</ul>' % (''.join('<li>%s</li>' % rich(c) for c in qq['challenges']) or '<li>None specific.</li>')),
            stage('What to avoid', rich(qq['avoid'])),
            stage('Staff-level signal', note(qq['signal'], 'good') + src_line),
        ]
        block = practice(qid, titled(qq['q'], qq['level']), stages, tag('lv', qq['level']), label=qq['q'][:60],
                         statuses=[('solved', 'Rehearsed'), ('revise', 'Needs work'), ('failed', 'Rusty')])
        q_html += block.replace('<details class="acc"', '<details class="acc" data-level="%s"' % qq['level'], 1)
    q_html += '</div>'

    # why linkedin worksheet
    why_id = reg('hm', 'hm.why.worksheet', 'Motivation', 'Why LinkedIn worksheet', weight=2, kind='worksheet')
    why = card(
        note('I will not write this for you. Motivation that sounds borrowed is worse than motivation that sounds plain. '
             'Answer these five prompts in your own words, then rehearse them until they are 60 seconds.', 'warn', 'Rule') +
        '<div data-id="%s" data-label="Why LinkedIn worksheet">'
        '<ol>'
        '<li><b>What do you want to work on next</b>, stated as a problem rather than a technology?</li>'
        '<li><b>What about this specific team or system</b> at LinkedIn matches that? (Their infrastructure, scale, or the products '
        'built on it — name the actual thing.)</li>'
        '<li><b>What do you bring</b> that is unusually relevant? (Platform-scale migration, isolation guarantees, multi-tenant '
        'infrastructure — pick the one that fits the team.)</li>'
        '<li><b>Why now</b>, said without criticising your current employer?</li>'
        '<li><b>What would make you say yes</b> to an offer? (Interviewers ask, and a crisp answer helps the recruiter.)</li>'
        '</ol>'
        '%s</div>' % (why_id, tracker(why_id, statuses=[('solved', 'Written and rehearsed'), ('revise', 'Draft only')],
                                      note_ph='Draft your answers here — they save in this browser…')) +
        note('LinkedIn interviews are reported to weigh communication and product-mindedness heavily. A specific "I want to work on X '
             'because I have done Y" beats enthusiasm every time.', ''),
        title='Why LinkedIn — your worksheet')

    craft = card(
        note('The India Staff loop (May 2025) reported a separate <b>craftsmanship</b> round assessing code quality, structure, '
             'testing and best practices, with discussion of project metrics, CI/CD and reactive systems. Prepare it as its own round: '
             'it is where your operational detail lands.', '', 'Why this section exists') +
        table(['Area', 'What you have', 'How to say it'], [[a, b, c] for a, b, c in CRAFT]) +
        senior_staff('"We had CI, code reviews and monitoring."',
                     '"Safety was a property of the pipeline: provisioning steps were idempotent so a failure resumed, nothing could take '
                     'traffic before verification passed, releases rolled in waves against each tenant\'s own baseline, and every override '
                     'needed an owner and a reason. The metric that caught the most problems was egress denials, which I had expected to be '
                     'a compliance number."'),
        title='The craftsmanship round')

    mocks = ''
    for mid, title, q, rub, secs in [
        ('m1', 'Mock 1 · the opening twenty minutes',
         'Walk me through your career progression, and then tell me about the most complex project you have led.',
         ['Career arc in three beats with the trigger for each change, under three minutes',
          'Role stated precisely within the first thirty seconds of the project story',
          'Named the decision (isolation as a platform capability) rather than describing the architecture',
          'Mentioned the cost and the trade-off without being asked',
          'Left a hook the interviewer could pull (the gateway, the incident, the migration)'], 1200),
        ('m2', 'Mock 2 · influence and conflict',
         'We have a platform product used by 5,000 teams. How would you get them to migrate? And tell me about a time a team refused.',
         ['Mechanism first (adoption cheaper than resistance), not a mandate',
          'Sequencing by dependency, with the reason',
          'Computed status rather than self-reported',
          'The holdout story told with the other team made reasonable',
          'The systemic lesson: two teams hitting the same thing is a platform problem',
          'Escalation mentioned last, with the dependency map in the room'], 1200),
        ('m3', 'Mock 3 · failure and estimation under pressure',
         'Tell me about a failure you caused. Then: how would you roll out mTLS across a shared infrastructure component, and how long would it take?',
         ['Impact stated precisely, including why it was bounded',
          'Detection before the customer noticed, and how',
          'A structural fix, not "we were more careful"',
          'Estimate given in phases with the dominating unknown named',
          'Migration shape drawn from real experience (discovery, dual-mode, tiered rollout, enforcement)',
          'Comfortable saying "that estimate would change if discovery shows X"'], 1500)]:
        mocks += card(mock_block(reg('hm', 'hm.mock.' + mid, 'Mock interviews', title, weight=3, kind='mock'),
                                 q, 'Hiring Manager', rub, secs), title=title)

    levelling = card(
        note('Blind threads repeatedly describe LinkedIn Staff as L5.5+ and attribute down-levelling to leadership signal across the '
             'manager, craftsmanship and design rounds rather than to technical depth. Treat every behavioural answer as a scope exam.',
             'warn', 'Why this round decides your level') +
        table(['They hear', 'Senior', 'Staff'], [
            ['Ownership', 'I built the component I was assigned', 'I found the problem, framed it, and got the organisation to act'],
            ['Influence', 'Leadership backed me', 'I made adoption cheaper than resistance and sequenced it so nobody was blocked'],
            ['Failure', 'Here is the bug and the fix', 'Here is what it revealed about the design, and the mechanism that changed'],
            ['Trade-offs', 'We chose X because it was better', 'We chose X, gave up Y, and contained the cost with Z'],
            ['Scope', 'My team, my service', '178 teams, no authority, and the line between platform and product'],
        ]), title='Senior versus Staff — what decides the level')

    body = (
        sec('reports', 'What recent reports say about this round', rep_html + follow_patterns,
            kicker='Research first', why='%d catalogued HM reports · updated %s' % (len(rep), R.DATE)) +
        sec('stories', 'Your story bank', note(
            'Every story here comes from your own Isolated Cloud retrospective — nothing invented. Each one is a 90-second telling with '
            'the beats in order and the questions it can answer. Rehearse out loud; the page tracks which ones you can tell cold.', 'exp',
            'Provenance') + story_html,
            kicker='Your material', why='%d stories · source: your AIC retrospective' % len(STORIES)) +
        sec('questions', 'Behavioural question bank', note(
            'Structure: what they are testing → your story → structure → a strong answer → follow-ups → challenges → what to avoid → the '
            'staff signal. Answer out loud before revealing.', '') + q_html,
            kicker='Practice', why='%d questions' % len(QUESTIONS)) +
        sec('craft', 'The craftsmanship round', craft, kicker='Separate round') +
        sec('why', 'Why LinkedIn', why, kicker='Motivation') +
        sec('level', 'Senior versus Staff', levelling, kicker='Levelling') +
        sec('mock', 'Mock hiring-manager rounds', mocks, kicker='Simulation', why='3 mocks · timed · graded in chat'))

    return page('04-hiring-manager.html', 'Hiring Manager round',
                'Your story bank, the behavioural drills that use it, the craftsmanship round, and the scope signal that decides your level.',
                body, round_id='hm', round_name='Hiring Manager', crumb_tail='04 Hiring Manager',
                hero_chips=[('', '%d stories from your own work' % len(STORIES)), ('', '%d questions' % len(QUESTIONS)),
                            ('', 'Craftsmanship round'), ('', '3 mocks')])
