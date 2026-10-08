# -*- coding: utf-8 -*-
"""Host Manager playbook — the personal content.

SOURCES OF TRUTH, in order:
  RESUME  Rishikant.pdf (repo root, git-ignored)
  YOURS   the reader's own account of Isolated Cloud (the architecture, ~178 teams, L0–L3 + L2.5, no Kubernetes)
  STORY   the constructed principal-engineer story in specialization-aic.html (data-src="story").
          Coherent and plausible, but NOT supplied by the reader. Every use is labelled; confirm before saying it.
Unknowns are marked [USER INPUT REQUIRED]; numbers that no source supplies are [METRIC TO VERIFY].
Inline markers in text: [STORY — confirm], [USER INPUT REQUIRED: …], [METRIC TO VERIFY: …].
"""

# ---------------------------------------------------------------- the facts the whole module stands on
FACTS = [
 ('Career', '16+ years; Siemens → McAfee → Intuit → Microsoft → Adobe → Compass → Salesforce → Atlassian → xAI', 'RESUME'),
 ('Now', 'xAI, Engineering Specialist (Nov 2025 – present): evaluating AI-generated code for post-training (RLHF/DPO preference data, SFT examples, failure analysis)', 'RESUME'),
 ('Atlassian', 'Principal Engineer, Jan 2025 – Sep 2025', 'RESUME'),
 ('Scale', "Cross-product GraphQL Gateway at ~76K QPS — architected and drove the rollout", 'RESUME'),
 ('Isolated Cloud', 'Led architecture and execution: tenant-level isolation and compliance boundaries for regulated enterprises', 'RESUME'),
 ('178 teams', "About 178 teams' services migrated onto the platform; tiers L0–L3 plus an inserted L2.5", 'YOURS'),
 ('The principle', 'Isolation is a platform capability, not a product feature', 'YOURS'),
 ('Key decision', 'Router decides commercial vs isolated only; Shard Manager owns placement; tenant context separated from placement', 'YOURS'),
 ('Cloud', 'AWS-native; Auto Scaling for replicas; deliberately no extra orchestration layer (no Kubernetes)', 'YOURS'),
 ('Strategy', 'Drove platform strategy across Platform, Subscription and API Externalisation streams; established GraphQL as the standard integration layer', 'RESUME'),
 ('AI', 'Atlassian: designed AI features using LLM orchestration and RAG (LangChain, GitHub API). xAI: evaluation and failure analysis of AI-generated code', 'RESUME'),
 ('Earlier leadership', 'Salesforce: led architecture of consumption billing. Compass: Sell Side Design Squad (architecture reviews, standards); proposed a reusable 3P platform. Microsoft: tech lead, Bing Shopping (Black Friday / Cyber Monday). McAfee: tech lead, SaaS email security', 'RESUME'),
]

# The things the Host Manager will notice in the resume — address them before they become doubts.
RISKS = [
 ('Current role is not a Staff role', 'Engineering Specialist at xAI after Principal at Atlassian. Expect "tell me about your current role and team" and "why that move?".',
  '[USER INPUT REQUIRED: the real reason, in one forward-looking sentence.] Frame: what you went to learn (how AI fails at real engineering work), and why you now want to bring it back to platform leadership.'),
 ('Short recent tenures', 'Atlassian ~9 months, Salesforce ~14 months; most roles 1–2 years.',
  '[USER INPUT REQUIRED: the honest reasons.] Have one calm sentence per move, and be exact about what was yours in each — especially what happened on Isolated Cloud inside nine months.'),
 ('Big claims, short window', 'Isolated Cloud + 178 teams + the gateway rollout, all in Jan–Sep 2025.',
  '[USER INPUT REQUIRED: what existed when you joined, what you did, what continued after you left.] Precision here makes everything else credible.'),
 ('No people-growth story yet', 'The material has platform stories but no named person you mentored and no team culture you built — two of the pack\'s five areas.',
  '[USER INPUT REQUIRED: one mentoring story, one culture story.] Seeds from the resume: Compass design squad, Microsoft and McAfee tech-lead roles.'),
 ('AI depth', 'The resume says DESIGNED the RAG features; xAI is evaluation, not model training.',
  'Say exactly that. It is a strength when stated precisely.'),
]

POSITIONING = dict(
 one_line='A platform-architecture Staff engineer: I find the problem many teams are each solving badly, turn it into one platform capability, and get the teams to adopt it.',
 archetype=('Architect + Tech Lead', 'You set technical direction for a domain (isolation, API composition) and drove execution across teams you did not manage. Not a "Solver" parachuted into one fire, not a "Right Hand" to an executive.'),
 strengths=['Platform thinking: one implementation instead of ~178', 'Distributed systems at scale (gateway ~76K QPS)',
            'Influence without authority across ~178 teams', 'Architectural judgment with named trade-offs (Router vs Shard Manager)',
            'AI: building with it (RAG) and judging it (xAI evaluation)'],
 avoid=['Narrating components instead of decisions', 'Claiming the whole programme as yours inside a nine-month tenure',
        'Inflating AI depth beyond "designed" and "evaluate"', 'Reciting constructed story details you cannot defend at the third follow-up',
        'Having no answer for mentoring or culture'],
 gaps=['A mentoring story (named person, what you did, what they did)', 'A culture story (a practice you created that outlived you)',
       'A real failure you own', 'A disagreement with your own manager', 'Real numbers for Isolated Cloud impact'],
)

# ---------------------------------------------------------------- narrative and TMAY
NARRATIVE = [
 ('Foundation', 'Systems engineering from first principles: C++/C# at Siemens, McAfee and Intuit — instrumentation, core-dump analysis, payroll correctness.', 'RESUME'),
 ('Scale', 'Microsoft Bing Shopping: tech lead for peak-traffic events like Black Friday.', 'RESUME'),
 ('Platforms', 'Adobe licensing and entitlements; Compass: a reusable 3P platform and the design squad; Salesforce: consumption billing on an event-driven platform.', 'RESUME'),
 ('Staff scope', 'Atlassian: the cross-product GraphQL Gateway (~76K QPS) and Isolated Cloud — isolation as a platform capability across ~178 teams.', 'RESUME / YOURS'),
 ('AI', 'RAG features at Atlassian; now at xAI, evaluating where AI-generated engineering work fails.', 'RESUME'),
 ('Next', 'Why LinkedIn: [USER INPUT REQUIRED — one sentence that is genuinely yours].', 'VERIFY'),
]

TMAY = {
 '30 seconds': [
  "I'm a platform engineer with about sixteen years in distributed systems. Most recently I was a principal engineer at Atlassian, where I led Isolated Cloud — dedicated, compliant environments for regulated enterprises — by making isolation a platform capability that about 178 teams adopted, instead of each team rebuilding it. Today I'm at xAI, judging how AI handles real engineering work. [USER INPUT REQUIRED: one line on why LinkedIn.]"],
 '60 seconds': [
  "I'm a platform engineer with about sixteen years building distributed systems — Microsoft, Adobe, Salesforce, Atlassian.",
  "The thread is leverage: finding the problem many teams are each solving badly, and turning it into one capability they adopt.",
  "At Atlassian I architected and drove the rollout of the cross-product GraphQL Gateway, about 76 thousand queries a second, and led Isolated Cloud, where about 178 teams' services had to run per customer. The decision that mattered was making isolation a platform capability, not a product feature.",
  "Since November I've been at xAI evaluating AI-generated code, which has sharpened how I think about AI in production. [USER INPUT REQUIRED: why LinkedIn, one sentence.]"],
 '90 seconds': [
  "I'm a platform engineer with about sixteen years in distributed systems — from systems programming at Siemens and McAfee, through scale work at Microsoft on Bing Shopping's peak events, to platform roles at Adobe, Compass and Salesforce.",
  "What I'm best at is leverage: spotting the problem many teams are each solving badly, and turning it into one capability they actually adopt.",
  "At Atlassian, as a principal engineer, I did that twice. I architected and drove the rollout of the cross-product GraphQL Gateway, about 76 thousand queries a second, which made GraphQL the standard integration layer. And I led Isolated Cloud: dedicated environments for regulated enterprises. About 178 teams' services assumed a shared runtime; the obvious answer was for every product to redesign, and that doesn't finish. We made isolation a platform capability instead, and sequenced the migration by dependency.",
  "Since November I've been at xAI, evaluating AI-generated code for post-training — a very direct view of where AI helps and where it fails.",
  "[USER INPUT REQUIRED: why LinkedIn and why this team, in your own words.]"],
 '2 minutes': [
  "I'm a platform engineer with about sixteen years in distributed systems.",
  "I started close to the metal — C++ and C# at Siemens, McAfee and Intuit — which taught me to debug from first principles. At Microsoft I led customer-facing work on Bing Shopping, including Black Friday traffic, and at Adobe, Compass and Salesforce I moved into platforms: entitlements, a reusable third-party platform, and consumption billing on an event-driven system.",
  "The Staff-level work is Atlassian. Two things. First, I architected and drove the rollout of the cross-product GraphQL Gateway at about 76 thousand queries a second, which became the standard integration layer across products. Second, I led the architecture and execution of Isolated Cloud. Regulated customers needed dedicated environments, and about 178 teams' services assumed one shared runtime. Asking every team to redesign would have produced 178 versions of a compliance guarantee. So the principle was: isolation is a platform capability, not a product feature. The platform owns routing, placement, lifecycle and egress; teams adopt configuration. Then the hard part was organisational — sequencing the migration by dependency, making adoption cheaper than resistance, and fixing shared blockers once.",
  "[USER INPUT REQUIRED: exactly what was yours inside the Jan–Sep 2025 window.]",
  "Since November I've been at xAI, evaluating AI-generated code and coding-agent behaviour for post-training. It's made me precise about where AI is useful in engineering and where it fails quietly.",
  "I'm looking for Staff scope again, on platform and distributed-systems problems at real scale — [USER INPUT REQUIRED: why LinkedIn specifically]."],
}
TMAY_WHY = [
 'It is a thesis ("leverage"), not a chronology — the HM hears what kind of Staff engineer you are in ten seconds.',
 'Scale and scope are concrete: ~76K QPS, ~178 teams, regulated enterprises.',
 'It names one decision, which invites the follow-up you want: "tell me more about Isolated Cloud".',
 'xAI is presented as deliberate learning, not drift — but only once you fill in the real reason.',
 'It ends on LinkedIn, so the motivation question is half-answered before it is asked.',
]

# ---------------------------------------------------------------- the most impactful project, three lengths
PROJECT = {
 'short': "Isolated Cloud at Atlassian: dedicated environments for regulated enterprises. The obvious approach — every product redesigning for isolation — didn't scale to about 178 teams, so I made isolation a platform capability and drove adoption across teams I didn't manage.",
 'two_minutes': [
  ('Problem', "Regulated enterprises couldn't accept shared infrastructure, however good our logical isolation. Every service assumed one deployment served every tenant."),
  ('Why it was hard', "About 178 teams' services. Left to each team, that's 178 implementations of the same compliance guarantee, as strong as the weakest one."),
  ('My role', "I led the platform architecture and execution. [USER INPUT REQUIRED: the exact boundary of your role, and what existed before Jan 2025.]"),
  ('Decision', "Isolation as a platform capability: the platform owns provisioning, routing, placement, lifecycle and egress; teams adopt a configuration model — shard descriptors."),
  ('Architecture', "Router decides commercial or isolated, and nothing else. A Shard Manager owns placement. Tenant context is static, placement is operational, so they live apart."),
  ('Execution', "I planned dependencies, not 178 migrations: tiers L0 to L3, plus an L2.5 inserted rather than renumbering everything."),
  ('Outcome', "Regulated customers could adopt Atlassian cloud; new products inherit isolation without redesign. [METRIC TO VERIFY: customers or environments live, adoption numbers you can share.]"),
 ],
 'deep': [
  ('Context', 'Commercial cloud is multi-tenant: tenancy is a field or a column, not a deployment.', 'YOURS'),
  ('Scale', '~178 teams; [METRIC TO VERIFY: number of services, environments].', 'YOURS / METRIC'),
  ('Alternatives', 'Product-specific isolation (fast start, team control; 178 implementations) vs platform-driven (one implementation; centralisation risk).', 'YOURS'),
  ('Trade-offs', 'Centralisation and shared fate; teams lose some deployment control; new components to run; dedicated runtime cost. No extra orchestration layer because isolation multiplies environments.', 'YOURS'),
  ('Cross-team challenge', 'Product teams feared losing control of deployments and waiting on a platform backlog. [STORY — confirm: the Jira lead\'s "pager" objection; resolved with shard descriptors and a written platform contract.]', 'STORY'),
  ('Leadership', 'No authority over the teams: adoption made cheaper than resistance, sequenced by dependency, shared blockers fixed once. [STORY — confirm: one-on-ones with the largest product leads before the review.]', 'YOURS / STORY'),
  ('Execution', 'Phases by tier. [STORY — confirm: pilot customer, cutover rehearsals, onboarding tool, computed status.]', 'STORY'),
  ('Outcome', 'Isolation became a platform property. [METRIC TO VERIFY: customers live, teams migrated by Sep 2025, time to onboard.]', 'METRIC'),
  ('Lessons', '[STORY — confirm, or replace with yours: design cache invalidation in from day one; publish the platform contract before phase one.]', 'STORY'),
 ],
}

# ---------------------------------------------------------------- frameworks (taught, not memorised)
FRAMEWORKS = {
 'staff': ('The Staff engineer', ['Technical depth', 'Cross-team influence', 'Architecture', 'Business impact'], 'Staff engineer = all four, applied to problems bigger than one team.'),
 'influence': ('How influence actually works', ['Understand', 'Align on criteria', 'Propose options', 'Address objections', 'Decide', 'Execute', 'Measure'], 'The mechanism, not "I convinced everyone".'),
 'decision': ('A decision, told well', ['Problem', 'Constraints', 'Options', 'Trade-offs', 'Decision', 'Outcome', 'Learning'], 'Past tense, with a verdict on each rejected option.'),
 'disagree': ('Technical disagreement', ['Listen', 'Understand constraints', 'Agree decision criteria', 'Bring evidence', 'Make trade-offs explicit', 'Decide', 'Commit', 'Measure'], 'Disagree on the criteria first; the decision usually follows.'),
 'exec': ('Executive communication', ['Problem', 'Impact', 'Options', 'Recommendation', 'Risk', 'Decision needed', 'Ask'], 'Lead with the ask; keep implementation detail for the follow-up.'),
 'prioritise': ('Prioritising', ['Business impact', 'Customer impact', 'Risk', 'Urgency', 'Dependencies', 'Reversibility', 'Cost', 'Strategic fit', 'Leverage'], 'Say which two criteria dominate this time, and why.'),
 'ninety': ('First 90 days', ['Learn', 'Map stakeholders', 'Understand architecture', 'Find pain points', 'Find leverage', 'Build relationships', 'Early value', 'Technical direction'], 'Earn the right to propose before proposing.'),
}

SENIOR_VS_STAFF = [
 ('Core claim', '"I can solve difficult problems."', '"I can make several teams more effective at solving the right problems."'),
 ('Scope', 'A system', 'A domain across teams'),
 ('Influence', 'Through code and reviews', 'Through direction, mechanisms and other people'),
 ('Decisions', 'Makes good ones', 'Makes the important ones visible, with trade-offs and owners'),
 ('Ambiguity', 'Clarifies requirements', 'Decides what the problem is'),
 ('Impact story', 'What I built', 'What changed for the organisation, and what it cost'),
 ('Failure story', 'A bug and its fix', 'What it revealed, and the mechanism that prevents recurrence'),
]

EVAL_SIGNALS = ['operate independently', 'identify the important problem', "influence teams you don't manage", 'make architecture decisions',
                'align stakeholders', 'unblock organisations', 'manage ambiguity', 'make trade-offs explicit', 'communicate with senior leadership',
                'create leverage', 'mentor senior engineers', 'connect technical decisions to business outcomes']

# ---------------------------------------------------------------- story bank
# fields: situation, task, action, decision, tradeoff, people, influence, result, metrics, learning — each (text, prov)
def S(id, title, prov, answers, **f): return dict(id=id, title=title, prov=prov, answers=answers, f=f)

STORIES = [
 S('ic', 'Isolated Cloud — isolation as a platform capability', 'RESUME / YOURS',
   ['Most impactful project', 'Technical decision', 'Architecture', 'Business impact', 'Ambiguity', 'Leadership'],
   situation=('Regulated enterprises needed dedicated environments; every service assumed a shared runtime.', 'YOURS'),
   task=('Make ~178 teams\' services run per customer without each redesigning.', 'YOURS'),
   action=('Defined the principle and the platform architecture; sequenced the migration by dependency.', 'RESUME / YOURS'),
   decision=('Platform-driven isolation; Router vs Shard Manager split.', 'YOURS'),
   tradeoff=('Centralisation and shared fate; dedicated runtime cost; teams lose some deployment control.', 'YOURS'),
   people=('Product teams feared losing control. [STORY — confirm the specific objections.]', 'STORY'),
   influence=('Adoption made cheaper than resistance. [STORY — confirm: pre-alignment one-on-ones, written contract.]', 'STORY'),
   result=('Regulated customers could adopt the cloud; new products inherit isolation.', 'YOURS'),
   metrics=('~178 teams. [METRIC TO VERIFY: customers live, teams migrated by Sep 2025.]', 'METRIC'),
   learning=('[STORY — confirm, or yours: design invalidation in from day one.]', 'STORY')),
 S('migration', 'The ~178-team migration', 'YOURS / STORY',
   ['Influence without authority', 'Execution at scale', 'Prioritisation', 'Resistance', 'Measuring progress'],
   situation=('Every team\'s service had to move, in an order the dependency graph allowed.', 'YOURS'),
   task=('Sequence it so nobody was blocked, without authority over any team.', 'YOURS'),
   action=('Tiers L0 identity/edge, L1 shared platform, L2 first-customer products, L2.5 inserted, L3 tail.', 'YOURS'),
   decision=('Insert L2.5 rather than renumber, because dashboards and runbooks were keyed to tiers.', 'YOURS'),
   tradeoff=('Plan precision vs keeping others\' tooling stable.', 'YOURS'),
   people=('[STORY — confirm: the team with custom deployment scripts whose scaling pattern the descriptor could not express.]', 'STORY'),
   influence=('[STORY — confirm: status computed by tooling, office hours, publishing team status to leadership.]', 'STORY'),
   result=('[STORY — confirm: onboarding went from weeks to days.]', 'STORY'),
   metrics=('[METRIC TO VERIFY: teams migrated by Sep 2025; time to onboard.]', 'METRIC'),
   learning=('If two teams hit the same blocker, it is a platform problem, not a team problem. [STORY — confirm.]', 'STORY')),
 S('decision', 'Separating tenant context from placement', 'YOURS / STORY',
   ['Most important technical decision', 'Decision you changed', 'Evaluating alternatives'],
   situation=('Every request needs two answers: commercial or isolated, and which shard.', 'YOURS'),
   task=('Decide where each answer lives.', 'YOURS'),
   action=('Router answers only commercial vs isolated; Shard Manager owns placement; repository is the source of truth.', 'YOURS'),
   decision=('Separate by volatility: identity is static, placement is operational.', 'YOURS'),
   tradeoff=('One more component and lookup, in exchange for scoped invalidation and a stable hot path.', 'YOURS'),
   people=('[STORY — confirm: you initially favoured the simpler design yourself.]', 'STORY'),
   influence=('Listed every event that moves placement; none changes who the tenant is.', 'STORY'),
   result=('Shards can be replaced without touching tenant identity.', 'YOURS'),
   metrics=('[METRIC TO VERIFY: routing overhead.]', 'METRIC'),
   learning=('Separate state by how often it changes.', 'YOURS')),
 S('gateway', 'GraphQL Gateway — a standard integration layer', 'RESUME',
   ['High-scale systems', 'Cross-team influence', 'Recommendations adopted', 'Technical decision'],
   situation=('Products integrated service by service.', 'RESUME'),
   task=('A composition layer across products.', 'RESUME'),
   action=('Architected and drove the rollout; partnered with product and infrastructure teams to make GraphQL the standard.', 'RESUME'),
   decision=('[USER INPUT REQUIRED: your key architecture decision on the gateway.]', 'VERIFY'),
   tradeoff=('One composition layer = shared fate; contained with timeouts, bulkheads, partial results. [GENERAL — confirm which you used.]', 'GENERAL'),
   people=('[USER INPUT REQUIRED: who had to be persuaded, and what they feared.]', 'VERIFY'),
   influence=('Standardisation adopted across products.', 'RESUME'),
   result=('A scalable composition layer at ~76K QPS.', 'RESUME'),
   metrics=('~76K QPS. [METRIC TO VERIFY: services composed, latency overhead.]', 'RESUME / METRIC'),
   learning=('[USER INPUT REQUIRED]', 'VERIFY')),
 S('jira', 'The product lead who would not hand over their pager', 'STORY',
   ['Disagreement', 'Difficult stakeholder', 'How you got buy-in', 'Compromise vs stand your ground'],
   situation=('[STORY — confirm] The largest product lead objected to centralising deployment control.', 'STORY'),
   task=('Keep the principle without losing the biggest team.', 'STORY'),
   action=('[STORY — confirm] One-on-ones before the review; treated the objection as design input.', 'STORY'),
   decision=('Teams keep business logic and size their own shards; a written platform contract.', 'STORY'),
   tradeoff=('Gave up some centralisation; held routing, placement and egress in the platform.', 'STORY'),
   people=('A fair fear: availability depending on someone else\'s backlog.', 'STORY'),
   influence=('Changed the design instead of winning the argument.', 'STORY'),
   result=('The architecture review was short once the largest teams agreed.', 'STORY'),
   metrics=('—', 'STORY'),
   learning=('Objections are information about the design.', 'STORY')),
 S('sre', 'Fail closed: the availability-vs-compliance disagreement', 'STORY',
   ['Holding a line', 'Disagreement with a senior engineer', 'Judgment under pressure'],
   situation=('[STORY — confirm] An SRE lead proposed falling back to commercial when a shard is unhealthy.', 'STORY'),
   task=('Answer a fair reliability instinct.', 'STORY'),
   action=('Named the asymmetry: an outage is a reliability problem; serving from shared infrastructure is a compliance failure.', 'STORY'),
   decision=('No fallback anywhere; reliability from replicas inside the boundary.', 'STORY'),
   tradeoff=('Accepted errors over a breach.', 'STORY'),
   people=('A respected peer with a legitimate concern.', 'STORY'),
   influence=('Reframed the criteria, then designed the alternative.', 'STORY'),
   result=('Fail-closed became a platform rule.', 'STORY'),
   metrics=('An alert whose expected value is zero.', 'STORY'),
   learning=('Agree the criteria first; the decision usually follows.', 'STORY')),
 S('failure', 'A failure you own', 'VERIFY',
   ['Project that failed', 'Decision you got wrong', 'Underestimated complexity', 'What would you do differently'],
   situation=('[USER INPUT REQUIRED: a real failure. The practice candidate below is constructed.]', 'VERIFY'),
   task=('—', 'VERIFY'),
   action=('[STORY — practice candidate only: an early cutover where some Router instances missed invalidation; the second lock held, so users saw errors, not a breach.]', 'STORY'),
   decision=('[STORY] A switch is incomplete until every Router confirms.', 'STORY'),
   tradeoff=('—', 'STORY'),
   people=('[USER INPUT REQUIRED]', 'VERIFY'),
   influence=('—', 'VERIFY'),
   result=('[STORY] Process changed so the class of failure cannot recur.', 'STORY'),
   metrics=('[METRIC TO VERIFY]', 'METRIC'),
   learning=('[USER INPUT REQUIRED: what YOU would do differently.]', 'VERIFY')),
 S('mentor', 'Growing another engineer', 'VERIFY',
   ['Mentoring senior engineers', 'Creating leaders', 'Feedback', 'Culture'],
   situation=('[USER INPUT REQUIRED: a named person (initials are fine), where they started.]', 'VERIFY'),
   task=('—', 'VERIFY'),
   action=('[USER INPUT REQUIRED: what you specifically did — gave them the hard design, reviewed with questions, sponsored them.]', 'VERIFY'),
   decision=('—', 'VERIFY'), tradeoff=('Speed now vs their growth.', 'GENERAL'),
   people=('—', 'VERIFY'), influence=('—', 'VERIFY'),
   result=('[USER INPUT REQUIRED: what they did that was theirs; where they are now.]', 'VERIFY'),
   metrics=('—', 'VERIFY'),
   learning=('Seeds from your resume: Compass Sell Side Design Squad (architecture reviews, standards); Microsoft and McAfee tech-lead roles.', 'RESUME')),
 S('ai', 'AI: building with it and judging it', 'RESUME',
   ['AI experience', 'Learning a new area', 'Why now'],
   situation=('Atlassian: AI features grounded in real repository context.', 'RESUME'),
   task=('Design LLM orchestration + RAG with LangChain and the GitHub API.', 'RESUME'),
   action=('Designed the features; now at xAI evaluating AI-generated code and agent failure modes.', 'RESUME'),
   decision=('[USER INPUT REQUIRED: one design decision on the RAG features.]', 'VERIFY'),
   tradeoff=('Context size vs cost and latency. [GENERAL]', 'GENERAL'),
   people=('—', 'VERIFY'), influence=('—', 'VERIFY'),
   result=('[METRIC TO VERIFY: users, quality measure.]', 'METRIC'),
   metrics=('[METRIC TO VERIFY]', 'METRIC'),
   learning=('The gap from pilot to production is mostly evaluation. [From xAI work — say it in your words.]', 'RESUME')),
 S('cloud', 'AWS-native over another orchestration layer', 'YOURS',
   ['Cloud', 'Deciding what not to build', 'Simplicity'],
   situation=('Isolation multiplies environments.', 'YOURS'),
   task=('Decide how replicas scale inside each shard.', 'YOURS'),
   action=('AWS-native Auto Scaling; no Kubernetes.', 'YOURS'),
   decision=('Every extra component is multiplied by the number of customer environments.', 'YOURS'),
   tradeoff=('Less portability for far less per-environment operating cost.', 'YOURS'),
   people=('—', 'YOURS'), influence=('—', 'YOURS'),
   result=('Replicas scale without the shard or its placement changing.', 'YOURS'),
   metrics=('[METRIC TO VERIFY]', 'METRIC'),
   learning=('The cost of a component is its complexity times how many times you run it.', 'YOURS')),
 S('scale', 'Peak traffic at Bing Shopping', 'RESUME',
   ['High-scale systems', 'Execution under deadline'],
   situation=('Black Friday and Cyber Monday campaigns.', 'RESUME'),
   task=('Tech lead for customer-facing work under seasonal peaks.', 'RESUME'),
   action=('[USER INPUT REQUIRED: what you did to prepare — forecasting, load tests, degradation plans.]', 'VERIFY'),
   decision=('[USER INPUT REQUIRED]', 'VERIFY'), tradeoff=('—', 'VERIFY'), people=('—', 'VERIFY'), influence=('—', 'VERIFY'),
   result=('[USER INPUT REQUIRED]', 'VERIFY'), metrics=('[METRIC TO VERIFY: peak QPS]', 'METRIC'), learning=('—', 'VERIFY')),
 S('ambiguity', 'Turning "make it isolated" into a decision', 'YOURS / STORY',
   ['Ambiguity', 'Identifying the important problem', 'Taking initiative'],
   situation=('Several product teams were designing their own isolation. [STORY — confirm.]', 'STORY'),
   task=('Decide what belongs in the platform.', 'YOURS'),
   action=('[STORY — confirm] Listed everything a service does differently for an isolated tenant; classified each product-specific or common with product leads.', 'STORY'),
   decision=('Isolation is a platform capability.', 'YOURS'),
   tradeoff=('Paused team-level designs to decide the boundary first.', 'STORY'),
   people=('[STORY — confirm: a one-page note to your VP asking to pause product-level designs.]', 'STORY'),
   influence=('Made the decision checkable rather than deciding faster.', 'YOURS'),
   result=('A principle every later decision could be tested against.', 'YOURS'),
   metrics=('—', 'YOURS'),
   learning=('Resolve ambiguity by making the decision checkable.', 'YOURS')),
]

MATRIX_COLS = ['Impactful project', 'Leadership', 'Influence', 'Architecture', 'Ambiguity', 'Conflict', 'Migration', 'Business impact',
               'Decision', 'Failure', 'Cross-team', 'Mentoring']
MATRIX = {
 'ic':        [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0],
 'migration': [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0],
 'decision':  [0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0],
 'gateway':   [1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0],
 'jira':      [0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0],
 'sre':       [0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
 'failure':   [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
 'mentor':    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
 'ai':        [0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0],
 'cloud':     [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
 'scale':     [0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
 'ambiguity': [0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0],
}

# ---------------------------------------------------------------- red flags, checklist, questions to ask, 90 days
RED_FLAGS = [
 ('"I designed everything."', '"I led the platform design; [names] owned [parts]. My part was the principle, the architecture and the sequencing."'),
 ('"I convinced everyone."', '"Two leads objected. Here is what they were worried about, and what we changed in the design."'),
 ('"We just implemented…"', '"We chose X over Y because Z; it cost us W."'),
 ('"My manager told us to…"', '"Leadership set the goal; the approach was mine to propose. Here is what I proposed."'),
 ('"The team handled that."', '"That was [owner]\'s area; I made sure [the interface / the risk] was covered by [mechanism]."'),
 ('"I don\'t remember."', '"I don\'t have the exact number; it was roughly [order of magnitude], and here is how we measured it."'),
 ('"That wasn\'t my responsibility."', '"It wasn\'t mine to own, so I [raised it / made the dependency visible] — here is what happened."'),
 ('"My weakness is that I work too hard."', 'A real gap, what it cost once, and the mechanism you use now.'),
]

CHECKLIST = [
 'I can explain my career in 90 seconds, as a thesis — not a chronology.', 'I can explain my most impactful project in 2 minutes, and survive 10 minutes of drilling.',
 'I know exactly what was mine on Isolated Cloud inside Jan–Sep 2025.', 'I know the three major trade-offs and what each cost.',
 'I can tell the 178-team migration as an organisational story.', 'I have a conflict story I can defend to the third follow-up.',
 'I have a real failure story, with what I would do differently.', 'I have an influence story with the mechanism, not "I convinced them".',
 'I have a mentoring story with a named person.', 'I have a culture story — a practice that outlived me.',
 'I have a disagreement-with-my-manager story.', 'I can explain measurable impact, and say honestly where I lack a number.',
 'I can explain the xAI move and my tenure pattern in one calm sentence each.', 'I can answer "Why LinkedIn?" in my own words.',
 'I can answer "Why Staff?"', 'I can say what I want from a manager.', 'I can describe my first 90 days as an approach, not a checklist.',
 'I have three questions for the Host Manager.',
]

ASK_HM = [
 ('What would make someone in this role clearly successful in the first year?', 'Tells you the real expectations, and shows you think in outcomes.'),
 ('What is the hardest technical problem the team has not solved yet — and why not?', 'Shows where the leverage is; opens a technical conversation you are good at.'),
 ('How do Staff engineers and managers split technical direction here?', 'Tells you whether this is an Architect / Tech Lead role or something else.'),
 ('Which other teams does this team depend on most, and how is that going?', 'Cross-team influence is the job; this finds where it will be needed.'),
 ('How do decisions get made when two senior engineers disagree?', 'Culture signal; mirrors what they asked you.'),
 ('What does the team need most that it does not have today?', 'Lets you connect your experience to their gap in your closing minute.'),
]
