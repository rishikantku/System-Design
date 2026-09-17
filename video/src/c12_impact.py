# -*- coding: utf-8 -*-
from engine import *

chapter(12, "Business impact and lessons", "What changed for the business, how you measured it, what you'd do differently, and what's still weak.",
 """Chapter twelve. Impact and lessons. This is the part of the interview where many strong engineers go vague. They say it was a big success and everyone was happy. Don't. Impact needs to be concrete, measured, and tied to the business. And reflection needs to be specific enough that it's clearly yours.""")

D = Diagram("The impact, from engineering to business")
imp = [('Isolation became a platform capability', 'instead of ~178 separate redesigns', 'dp'),
       ('Onboarding a team', 'from a few weeks with platform help → a few days, on their own', 'ok'),
       ('New products', 'inherit isolation without redesigning anything', 'cp'),
       ('Regulated customers could move', 'starting with a large bank — customers who couldn’t use the cloud at all', 'shared')]
for k, (a, b, kind) in enumerate(imp):
    y = 20 + k * 150
    D.box('im%d' % k, 60, y, 700, 125, a, '', kind=kind, step=k, hl=str(k))
    D.label(820, y + 40, b, kind=kind, step=k, w=1040, size='m')
    if k: D.arrow('im%d' % (k - 1), 'im%d' % k, step=k, kind='neutral', fs='b', ts='t')
D.label(60, 650, 'These customers couldn’t be cloud customers at all without it.\nTheir compliance teams wouldn’t sign off on shared infrastructure.', kind='ok', step=4, w=1800, size='l', align='center')
sid = D.build()
seg(sid, 0, """Build the impact from engineering outward to the business. First: isolation became a platform capability, instead of a hundred and seventy-eight separate redesigns.""")
seg(sid, 1, """Second, onboarding a team went from a few weeks with someone from your team alongside them, to a few days on their own by the later waves.""")
seg(sid, 2, """Third, new products get isolation without redesigning anything. That's the lasting leverage. The investment keeps paying back after the migration ends.""")
seg(sid, 3, """And fourth, the one that matters most to the business. Regulated customers who couldn't use the cloud could move, starting with a large bank.""")
seg(sid, 4, """So if they ask, why did this matter to the business, keep it to one sharp sentence. These customers couldn't be cloud customers at all without it. Their compliance teams wouldn't sign off on shared infrastructure. Don't only talk about technology in an impact answer. Start or finish with the business.""")

sid = cards("How you measured success", [
 (0, "Teams fully migrated", "As computed by the tool from its own checks — not self-reported.", 'ok'),
 (1, "Time for a team to onboard", "A few weeks early → a few days by the later waves.", 'info'),
 (2, "Problems per cutover", "Rehearsals first; two customer-impacting incidents we caused in the first year.", 'shared'),
], cols=3, note=(3, "The slowest to move: teams migrated in **phase two** — an adoption problem, not an engineering one."))
seg(sid, 0, """How did you measure success? Three measures. Teams fully migrated, as computed by the tool. Not self-reported, because self-reported status was always greener than reality.""")
seg(sid, 1, """Time for a team to onboard. A few weeks early on, a few days by the later waves.""")
seg(sid, 2, """And problems per cutover. That's why rehearsals came first, and why you can say exactly how many customer-impacting incidents you caused in the first year: two.""")
seg(sid, 3, """And be honest about the measure that moved slowest: teams migrated in phase two. Because phase two was an adoption problem, not an engineering problem. Naming your weakest metric is far more credible than claiming everything went well.""")

sid = steps_list("What you'd do differently", [
 (0, "**Design cache invalidation in from day one.** The rehearsal problem and both production issues came from the same place — hardened in three rounds instead of one.", 'deny'),
 (1, "**Publish the platform contract and the shard descriptor model before phase one.** Weeks of negotiation a written contract would have settled in an afternoon.", 'shared'),
 (2, "**Put the GraphQL gateway on the dependency map as every edge it really is.** Most late surprises came from calls the gateway made on a service's behalf.", 'cp'),
])
seg(sid, 0, """What would you do differently? This question is almost guaranteed, so have three answers, each tied to real evidence. First, design cache invalidation in from day one. The rehearsal problem and both production issues came from the same place, and you hardened it in three rounds instead of one. That's a great answer because it's a pattern across incidents, not a single mistake.""")
seg(sid, 1, """Second, publish the platform contract and the shard descriptor model before phase one, not during it. You spent weeks negotiating things with teams that a written contract would have settled in an afternoon.""")
seg(sid, 2, """Third, put the GraphQL gateway on the dependency map as every edge it really is from day one, instead of as one L one service. Most of your late surprises came from calls the gateway made on a service's behalf. If they ask why you didn't do these at the time, be honest: you learned them by doing it. That's what a retrospective is for.""")

sid = compare("What's weakest today, and what you learned",
 ("Weakest part of the design today", 'deny', 0, ["Centralisation makes the platform a shared dependency", "Shard descriptor overrides still need discipline", "The monthly review helps — but depends on people doing it"]),
 ("What you learned about leading", 'ok', 1, ["Mandates don't work at 178 teams", "What looked like resistance was a real gap in the model", "Two teams hit the same thing → platform problem, not a team problem"]))
seg(sid, 0, """What's the weakest part of the design today? Don't blame things outside your control. Centralisation still makes the platform a shared dependency. And shard descriptor overrides still need discipline. The monthly review helps, but it depends on people doing it. An answer like that shows you still own the design, including its weak spots.""")
seg(sid, 1, """And what did you learn about leading across teams? Mandates don't work at a hundred and seventy-eight teams. The moment it clicked was the team with custom scripts. What looked like resistance was a real gap in your model. After that, if two teams hit the same thing, it was a platform problem, not a team problem. A lesson with a specific moment behind it is believable. A generic lesson isn't.""")

sid = statement("If you joined a team here doing something similar", "Decide early what belongs to the platform and what belongs to the product.",
 "Moving that line later is far more expensive than drawing it at the start.", kind='ok')
seg(sid, 0, """And a question some interviewers use to close: if you joined a team here doing something similar, what would you tell them first? Decide early what belongs to the platform and what belongs to the product.""")
seg(sid, 1, """Moving that line later is far more expensive than drawing it at the start. Notice that's advice, not a re-description of your project. That's exactly what the question is asking for.""")

question("What was the impact?", 8,
 "Isolation became a platform capability instead of 178 separate redesigns. Regulated customers who couldn't use our cloud could move, starting with a large bank. Onboarding a team went from a few weeks with our help to a few days on their own. And new products get isolation without redesigning anything.",
 "Business outcome, platform leverage and a measured improvement, in four sentences.",
 "Whether you connect engineering work to business results, and can back it with measures.",
 ["How did you measure that?", "Why did this matter to the business?", "What would you do differently?"],
 narr=dict(
  short="""Thirty seconds. Isolation became a platform capability instead of a hundred and seventy-eight separate redesigns. Regulated customers who couldn't use our cloud at all could move, starting with a large bank. Onboarding a team went from a few weeks with our help to a few days on their own. And new products get isolation without redesigning anything.""",
  strong="""Why it lands. It mixes three kinds of impact: business, platform leverage, and a measured improvement. And it doesn't inflate anything.""",
  testing="""They're testing whether you see your work through the business's eyes, and whether your claims have measures behind them.""",
  follow="""Follow-ups. How did you measure it? Teams migrated as computed by the tool, onboarding time, and problems per cutover. Why did it matter? These customers couldn't be cloud customers at all without it. And what would you do differently? Invalidation from day one, the contract before phase one, and the gateway as every edge on the dependency map."""))

question("What would you do differently?", 8,
 "Design cache invalidation in from day one — the rehearsal problem and both production issues came from the same place, and we hardened it in three rounds instead of one. And publish the platform contract before phase one; we spent weeks negotiating things a written contract would have settled.",
 "Each answer is a pattern with evidence behind it, not a cosmetic regret.",
 "Self-awareness, and whether you learn at the level of the system rather than the incident.",
 ["Why didn't you do that at the time?", "What's the weakest part of the design today?", "What did you learn about leading across teams?"],
 narr=dict(
  short="""Thirty seconds. Two things. Design cache invalidation in from day one. The rehearsal problem and both production issues came from the same place, and we hardened it in three rounds instead of one. And publish the platform contract before phase one. We spent weeks negotiating things with teams that a written contract would have settled in an afternoon.""",
  strong="""Why it lands. The first answer spots a pattern across three separate events. The second is about leadership, not code. Together they show learning at two levels.""",
  testing="""They're testing self-awareness. Saying nothing, or something cosmetic, is a red flag. So is blaming others.""",
  follow="""Follow-ups. Why didn't you do it at the time? Because the risk wasn't visible until the rehearsal, and the date was held for the pilot. What's weakest today? Centralisation and override discipline. And what did you learn about leading? The custom-scripts team, and the rule that two teams hitting the same thing means a platform problem."""))
