# -*- coding: utf-8 -*-
from engine import *

chapter(11, "Personal ownership and leadership", "What you owned, how it started, how you got 178 teams to adopt something they didn't design, and the disagreements along the way.",
 """Chapter eleven. Ownership and leadership. A retrospective isn't testing whether you can design something. It's testing whether you owned something. So this chapter is about you: what you personally did, how it started, how you got alignment with no authority, and the disagreements you had. These answers need to be first person, past tense, and specific.""")

sid = compare("The retrospective is a different interview",
 ("System design round", 'com', 0, ["Tense: “I would…”", "Wants: options", "Last question: “How would you scale it?”"]),
 ("Design retrospective", 'ok', 1, ["Tense: “We did, and here is why”", "Wants: decisions and their consequences", "Last question: “What would you change today?”"]))
seg(sid, 0, """First, reset your mode. In a system design round, you speak in the conditional. I would. The interviewer wants options. And the last question is, how would you scale it?""")
seg(sid, 1, """In a retrospective, it's past tense. We did, and here's why. They want decisions and their consequences. And the last question is, what would you change today? The hour is roughly a short intro, about forty minutes on one project, and about fifteen minutes of your questions. Forty minutes on one project means they go deep, not wide. Expect five to seven levels on a single thread.""")

sid = quote_slide("The failure mode", "You could also do X, and another option would be Y…",
 sub="Alternatives belong in the answer — in past tense, with a verdict: “We considered putting it in the Router. We rejected it because…”")
seg(sid, 0, """Here's the failure mode that sinks strong engineers in this format. Drifting into design mode. You could also do X, and another option would be Y. The moment you list options in the abstract, you sound like someone describing a system they read about.""")
seg(sid, 1, """Alternatives absolutely belong in your answers. But in past tense, with a verdict. We considered putting placement in the Router. We rejected it because every event that changes placement leaves tenant identity untouched. Same content. Completely different signal.""")

sid = cards("What you owned, and what the wider programme owned", [
 (0, "The principle", "Isolation is a platform capability, not a product feature.", 'ok'),
 (0, "The architecture behind it", "Router scope, Shard Manager, shard descriptors, egress, fail-closed guarantees.", 'dp'),
 (1, "The tiering", "Dependency map, L0–L3, and L2.5.", 'shared'),
 (1, "The onboarding tool", "Readiness, shard descriptor, encrypted transfer, validation, status.", 'cp'),
], cols=2, note=(2, "The wider programme: product teams, SRE, identity, edge, a program manager. **Your job was making those pieces fit together.**"))
seg(sid, 0, """Get to your role in the first thirty seconds. Don't spend three minutes on the product pitch. You were a principal engineer in platform engineering, and you led the cross-team platform design. The principle that isolation belongs to the platform. And the architecture behind it: the Router's narrow scope, the Shard Manager, shard descriptors, egress, and the fail-closed guarantees.""")
seg(sid, 1, """You owned the tiering of about a hundred and seventy-eight teams' services: the dependency map, L zero through L three, and L two point five. And the onboarding tool.""")
seg(sid, 2, """And be generous and precise about the wider programme: product teams, SRE, identity, edge, and a program manager. Your job was making those pieces fit together. Claiming everything sounds junior. Being exact about the boundary of your ownership sounds senior.""")

D = Diagram("How it started")
tl = [('Isolated Cloud funded', 'regulated customers — banks, critical infrastructure — couldn’t get compliance sign-off on shared infrastructure', 'com'),
      ('About a month in', 'three product design reviews in one week', 'shared'),
      ('What you saw', 'Jira: its own per-customer stack + routing · Confluence: something different · a third team waiting to copy', 'deny'),
      ('The realisation', '“We weren’t building one Isolated Cloud. We were about to build five or six.”', 'deny'),
      ('That weekend', 'a one-page note to your VP: pause product-level isolation designs until we decide what belongs in the platform', 'ok'),
      ('The outcome', 'your VP agreed, and asked you to lead that design', 'ok')]
for k, (a, b, kind) in enumerate(tl):
    y = 20 + k * 135
    D.box('h%d' % k, 60, y, 440, 110, a, '', kind=kind, step=k, hl=str(k))
    D.label(560, y + 22, b, kind=kind, step=k, w=1300, size='m')
    if k: D.arrow('h%d' % (k - 1), 'h%d' % k, step=k, kind='neutral', fs='b', ts='t')
sid = D.build()
seg(sid, 0, """Now, how it started. Isolated Cloud got funded for a simple commercial reason. Large regulated customers, a lot of them banks and critical-infrastructure companies, wanted to move to the cloud and couldn't. Their compliance teams wouldn't sign off on shared infrastructure, however good the logical isolation was.""")
seg(sid, 1, """About a month in, you sat through design reviews from three product teams in the same week.""")
seg(sid, 2, """Jira was planning its own per-customer stack with its own routing. Confluence was planning something different. And a third team hadn't started, and was waiting to copy whichever looked better.""")
seg(sid, 3, """That was the moment. We weren't building one Isolated Cloud. We were about to build five or six of them. This is the most important part of the story for a Staff interview. You didn't get assigned the problem. You spotted an engineering problem that nobody owned.""")
seg(sid, 4, """That weekend, you wrote a one-page note to your VP. The ask was specific: pause product teams designing isolation on their own, until we'd decided what belonged in the platform.""")
seg(sid, 5, """Your VP agreed, and asked you to lead that design. If the interviewer asks, why was that yours to solve and not each product team's? The answer is that the problem only existed across teams. No single team could see it.""")

D = Diagram("How you drew the line between platform and product")
D.box('list', 60, 30, 1800, 110, 'Everything a service does differently for an isolated tenant', 'marked item by item with the Jira and Confluence tech leads', kind='info', step=0)
D.zone(60, 210, 1100, 470, 'Same for every service → the platform', kind='ok', step=1)
for k, t in enumerate(['provisioning', 'identifying the tenant (tenant context)', 'finding the runtime (routing + placement)', 'lifecycle', 'egress']):
    D.label(110, 280 + k * 72, '•  ' + t, kind='ok', step=1, w=1000, size='m')
D.zone(1240, 210, 620, 470, 'Product-specific → stays with teams', kind='shared', step=2)
D.label(1290, 280, '•  business logic', kind='shared', step=2, w=540, size='m')
D.label(1290, 352, '•  how their own runtime\n   is sized (shard descriptors)', kind='shared', step=2, w=540, size='m')
D.label(60, 740, 'Almost everything landed on the left. That exercise produced the principle.', kind='neutral', step=3, w=1800, size='l', align='center')
sid = D.build()
seg(sid, 0, """How did you come up with the approach? Not in isolation. You made a list of everything a service does differently for an isolated tenant. Then you went through it with the Jira and Confluence tech leads, and marked each item. Is this product-specific, or the same for every service?""")
seg(sid, 1, """Almost everything landed on the same-for-everyone side. Provisioning. Identifying the tenant. Finding the runtime. Lifecycle. Egress.""")
seg(sid, 2, """What stayed with products was their business logic, and how their own runtime should be sized. That second item is important. It's why shard descriptors mattered to adoption: teams kept a real lever.""")
seg(sid, 3, """And that exercise gave you the principle everything is built on. Isolation is a platform capability, not a product feature. Notice the method: you derived the principle from the evidence, with the people who'd have to live with it. That's much stronger than arriving with a principle and defending it. If they ask how you scoped it, what was in and what was out, this slide is the answer.""")

D = Diagram("Getting alignment without authority")
al = [('Proposal written', 'both options side by side', 'info'),
      ('Two weeks of one-on-ones', 'the biggest product leads, before any formal review', 'shared'),
      ('The objection', 'losing control of deployments · waiting on a platform backlog', 'deny'),
      ('What answered it', 'teams keep business logic + size their own shards · a written platform contract', 'ok'),
      ('Architecture review', 'with engineering leadership — short', 'ok')]
for k, (a, b, kind) in enumerate(al):
    D.box('al%d' % k, 60 + k * 364, 60, 330, 250, a, b, kind=kind, step=k, hl=str(k))
    if k: D.arrow('al%d' % (k - 1), 'al%d' % k, step=k, kind='neutral')
D.box('q', 60, 420, 1800, 160, '“They weren’t handing their pager to someone else’s roadmap.”', 'the Jira lead — a fair concern, stated bluntly', kind='deny', step=2)
D.box('ct', 60, 640, 1800, 150, 'The platform contract', 'what the platform guarantees · what it doesn’t · how teams ask for changes', kind='ok', step=3)
sid = D.build()
seg(sid, 0, """Alignment. You wrote it up as an architecture proposal with both options side by side: each product fixes itself, or the platform fixes it once.""")
seg(sid, 1, """And here's the move. You didn't take it straight to review. You spent two weeks walking the biggest product leads through it one on one first. Because if Jira and Confluence said no in the room, the proposal was dead. That's a very concrete example of influence without authority. Pre-wire the decision with the people who can kill it.""")
seg(sid, 2, """The pushback was real, and it was fair. They worried about losing control of their deployments, and waiting on a platform team's backlog whenever they needed something. The Jira lead put it bluntly: they weren't handing their pager to someone else's roadmap. When you tell this, don't make that lead look unreasonable. It was a fair concern.""")
seg(sid, 3, """Two things got you through. Product teams kept their business logic, and sized their own shards through shard descriptors. And you committed to a written platform contract: what the platform guarantees, what it doesn't, and how teams ask for changes. You addressed the fear, not the person.""")
seg(sid, 4, """Once the big two were on board, the architecture review with engineering leadership was short. If an interviewer asks, how did you get alignment, never say leadership mandated it. Mandates don't work at a hundred and seventy-eight teams.""")

sid = table("The disagreements, and how each resolved", ["With", "About", "How it resolved"], [
 (0, ["The Jira lead", "Handing deployments to a platform", "Shard descriptors kept sizing with teams; a written contract"]),
 (1, ["Your SRE lead", "Fall back to commercial if a shard is unhealthy?", "No fallback — outage vs compliance failure; reliability from replicas"]),
 (2, ["A team with years of custom scripts", "Adopting shard descriptors", "Their scaling pattern was a real gap — added to the model"]),
 (3, ["Leadership", "Delaying phase one after the rehearsal", "You were overruled; you committed; confirmation step came after the first incident"], [None, None, 'deny']),
 (4, ["Yourself", "Placement in the Router", "The event list changed your own mind"], [None, None, 'ok']),
], widths=[24, 34, 42])
seg(sid, 0, """Now the disagreements, all in one place, because you'll be asked for at least one. With the Jira lead, about handing deployments to a platform. Resolved with shard descriptors and a written contract.""")
seg(sid, 1, """With your SRE lead, who asked whether an unhealthy shard should fall back to commercial. Resolved with a clear no, and reliability from replicas instead. Remember to say it was a fair question.""")
seg(sid, 2, """With a team that had years of custom deployment scripts. We'll tell that one properly in a moment, because it's your best leadership story.""")
seg(sid, 3, """With leadership, where you were overruled. And we'll tell that one properly too.""")
seg(sid, 4, """And with yourself. You initially favoured putting placement in the Router, and the event list changed your mind. Being willing to say you changed your own mind is one of the strongest signals in a retrospective.""")

D = Diagram("The team that pushed back hardest")
st = [('They refused', 'years of custom deployment scripts; didn’t want to touch them', 'deny'),
      ('Your first assumption', 'resistance to change', 'com'),
      ('You sat down with their tech lead', 'their service scaled on a pattern the shard descriptor genuinely couldn’t express', 'shared'),
      ('You changed the model', 'added the pattern to the shard descriptor', 'ok'),
      ('They migrated', 'and four or five teams after them used the same addition', 'ok')]
for k, (a, b, kind) in enumerate(st):
    y = 20 + k * 140
    D.box('st%d' % k, 60, y, 520, 115, a, '', kind=kind, step=k, hl=str(k))
    D.label(640, y + 36, b, kind=kind, step=k, w=1220, size='m')
    if k: D.arrow('st%d' % (k - 1), 'st%d' % k, step=k, kind='neutral', fs='b', ts='t')
D.label(60, 750, 'If two teams hit the same thing, it’s a platform problem — not a team problem.', kind='ok', step=5, w=1800, size='l', align='center')
sid = D.build()
seg(sid, 0, """Here's the story. One team pushed back hard. They had years of custom deployment scripts, and didn't want to touch them.""")
seg(sid, 1, """You assumed at first it was resistance to change. Say that honestly. It's the assumption most people would make.""")
seg(sid, 2, """Then you sat down with their tech lead. And it wasn't resistance. Their service scaled on a pattern the shard descriptor genuinely couldn't express. The model had a real gap.""")
seg(sid, 3, """So you added that pattern to the model.""")
seg(sid, 4, """They migrated. And four or five teams after them used the same addition. What looked like resistance was actually a signal about your abstraction.""")
seg(sid, 5, """And the lesson you took from it, which is your answer to what did you learn about leading across teams: that's when you stopped treating blockers as team problems. If two teams hit the same thing, it went on the platform backlog. This story works because it shows you being wrong about people, curious enough to find out, and willing to change your own design.""")

sid = cards("The time you were overruled", [
 (0, "What you wanted", "After the rehearsal: delay phase one until invalidation could be confirmed on every Router.", 'shared'),
 (0, "What happened", "Leadership held the date because of the pilot commitment. You committed.", 'com'),
 (1, "What you shipped", "Invalidation as an explicit step in the switch.", 'dp'),
 (1, "How it played out", "The confirmation step came after the first production incident. In hindsight, both partly right.", 'ok'),
], cols=2)
seg(sid, 0, """Were you ever overruled? Yes, and tell it without grievance. After the rehearsal, you wanted to delay phase one until you could confirm invalidation on every Router. Leadership held the date, because of the pilot commitment. And you committed. Disagree and commit, in practice.""")
seg(sid, 1, """You shipped invalidation as an explicit step in the switch. The every-Router confirmation step came after the first production incident, the ten-minute mis-route. And the honest verdict: in hindsight, you were both partly right. The commitment was real, the lock design held, and the incident was errors rather than a breach. Telling it that way shows judgement, not resentment. If they ask whether you'd push harder next time, you can say you'd push to have the confirmation step designed in before the date, which is exactly your reflection about designing cache invalidation in from day one.""")

sid = table("Senior versus Staff: same question, different answer", ["Asked", "Senior", "Staff"], [
 (0, ["Why a Shard Manager?", "What it does: owns placement, handles lifecycle.", "Why it's separate: two facts with different volatility; coupling makes placement changes touch identity."], [None, 'com', 'ok']),
 (1, ["How did teams adopt it?", "“We documented it and leadership backed it.”", "“Mandates don't work at 178 teams. We kept integration cost low and sequenced by dependency.”"], [None, 'com', 'ok']),
 (2, ["What went wrong?", "Names an incident and the fix.", "Names what it revealed about the design, and what changed so the class of failure can't recur."], [None, 'com', 'ok']),
], widths=[22, 34, 44])
seg(sid, 0, """Let's close with the level distinction, because both answers here are correct, and only one gets the level. Why a Shard Manager? Senior says what it does. Staff says why it's separate, and what coupling would have cost.""")
seg(sid, 1, """How did teams adopt it? Senior says, we documented it and leadership backed it. Staff says, mandates don't work at a hundred and seventy-eight teams. We kept integration cost low and sequenced by dependency so nobody was blocked.""")
seg(sid, 2, """What went wrong? Senior names an incident and the fix. Staff names what the incident revealed about the design, and what changed so the class of failure can't recur. Senior describes the system. Staff describes the decision and what it cost.""")

sid = steps_list("The shape of a big answer", [
 (0, "**Context** → **problem** → **constraint**", 'info'),
 (0, "**Options** → **decision** → **why**", 'dp'),
 (1, "**Trade-off** → **execution** → **impact** → **lesson**", 'ok'),
 (2, "Always include the **constraint** and the **trade-off** — the two people skip", 'deny'),
])
seg(sid, 0, """For your two or three big answers, walk this chain. Context, problem, constraint. Options, decision, why.""")
seg(sid, 1, """Trade-off, execution, impact, and lesson. For smaller questions, pick the three or four links that were actually asked about.""")
seg(sid, 2, """And always include the constraint and the trade-off. Those two are what make it a retrospective instead of a description, and they're exactly the two people skip.""")

question("Tell me about a disagreement.", 10,
 "The biggest was with the product leads over the platform approach. The Jira lead said they weren't handing their pager to someone else's roadmap. It was a fair concern. Teams kept business logic and sized their own shards through shard descriptors, and we wrote a platform contract. It took two weeks of one-on-ones before the review.",
 "It picks a disagreement that mattered, respects the other side, and shows what you changed to resolve it.",
 "Whether you can influence without authority, and whether you treat objections as information.",
 ["Did you have to give anything up to win them over?", "Were you ever overruled?", "A team wanted their own deployment approach. What did you do?"],
 narr=dict(
  short="""Thirty seconds. The biggest was with the product leads over the platform approach. The Jira lead put it bluntly: they weren't handing their pager to someone else's roadmap. It was a fair concern. So teams kept their business logic and sized their own shards through shard descriptors, and we wrote a platform contract: what the platform guarantees, what it doesn't, and how teams ask for changes. It took two weeks of one-on-ones before the review, and the review itself was short.""",
  strong="""Why it lands. The disagreement is about something that mattered. The other side is described as reasonable. And the resolution changed the design, rather than just winning the argument.""",
  testing="""They're testing influence without authority, and whether you treat objections as information about your design or as obstacles to push through.""",
  follow="""Follow-ups. Did you give anything up? Yes: teams kept control of sizing, and you committed the platform to a written contract you'd be held to. Were you ever overruled? The phase one date, told without grievance. And the custom-scripts team, which shows the same instinct at the level of a single team: what looked like resistance was a real gap in the model."""))

question("How did this start? What problem did you see?", 8,
 "About a month in, I sat through design reviews from three product teams in one week. Jira and Confluence were each designing their own per-customer stacks, and a third team was waiting to copy one. We were about to build five or six Isolated Clouds. I wrote my VP a one-page note that weekend asking to pause product-level designs until we'd decided what belonged in the platform, and was asked to lead it.",
 "It names the engineering problem you spotted, not just the customer requirement, and shows initiative with a concrete artefact.",
 "Whether you find problems nobody assigned you, at the level of the organisation.",
 ["Why was that yours to solve, not each product team's?", "How did you scope it?", "What did your VP push back on?"],
 narr=dict(
  short="""Thirty seconds. About a month in, I sat through design reviews from three product teams in one week. Jira and Confluence were each designing their own per-customer stacks, and a third team was waiting to copy one of them. We were about to build five or six Isolated Clouds. I wrote my VP a one-page note that weekend asking to pause product-level isolation designs until we'd decided what belonged in the platform, and I was asked to lead that design.""",
  strong="""Why it lands. It's specific: a week, three reviews, a one-page note, a weekend. And it names the engineering problem you spotted, not just the customer requirement everyone already knew.""",
  testing="""They're testing whether you find problems at the level of the organisation that nobody assigned to you. That's close to the definition of the Staff role.""",
  follow="""Follow-ups. Why was it yours? Because the problem only existed across teams, and no single team could see it. How did you scope it? The list you marked with the Jira and Confluence leads. And if they ask what your VP pushed back on, don't invent a conflict. The note was agreed. The hard pushback came later, from the product leads."""))
