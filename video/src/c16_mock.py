# -*- coding: utf-8 -*-
from engine import *

chapter(16, "Full mock interview", "Forty minutes compressed. One thread at a time, in the order a real interviewer moves. Answer each out loud before the key points appear.",
 """Chapter sixteen. The full mock interview. This runs in the order a real retrospective tends to move: opening, the problem, the architecture, a deep thread, failures, operations, leadership, and reflection. For each question you get about twenty-five seconds. Answer out loud, fully, as if the interviewer is in front of you. Then I'll show only the key points a strong answer must hit. No long explanations this time. You've had those. This is about whether you can produce it under a clock.""")

sid = cards("Mock interview rules", [
 (0, "Answer before the points appear", "If you need longer, pause the video. Don't skip ahead.", 'ok'),
 (0, "Score yourself against the key points", "Hit all of them? Missed one? Said something on the do-not-say list?", 'shared'),
 (1, "Keep it to 30–90 seconds", "Tight first answer. Depth only when pulled.", 'info'),
 (1, "Note the weak ones", "Rewatch that chapter, then redo only those questions.", 'deny'),
], cols=2)
seg(sid, 0, """The rules. Answer before the key points appear. If you need longer, pause the video. And score yourself honestly against the points. Did you hit all of them? Did you miss one? Did anything from the do-not-say list slip out?""")
seg(sid, 1, """Keep each answer between thirty and ninety seconds. And note the weak ones. Afterwards, rewatch the matching chapter and redo only those questions. Let's begin.""")

MOCK = [
 ("Tell me about a project you're proud of, and your role in it.",
  ["Isolated Cloud: dedicated environments for regulated enterprises", "Principal engineer, platform — led the cross-team design", "Owned: the principle, the architecture, tiering ~178 teams, the onboarding tool", "Role stated in the first thirty seconds"],
  """Let's start. Tell me about a project you're proud of, and your role in it."""),
 ("How did it start? What problem did you see?",
  ["Three product design reviews in one week", "Jira and Confluence designing their own stacks; a third team waiting to copy", "“Five or six Isolated Clouds”", "One-page note to your VP; asked to lead"],
  """How did it start? What problem did you actually see?"""),
 ("Isn't this basically single-tenant hosting with extra steps?",
  ["Agree: dedicated infrastructure is the easy part", "~178 services assumed one runtime for every tenant", "Day two: routing, replacement, patching, egress, live migration", "Dedicated boxes = Data Center; the goal was isolation with cloud economics"],
  """I'll push a little. Isn't this basically single-tenant hosting with extra steps?"""),
 ("Walk me through what happens when a request arrives for an isolated tenant.",
  ["Global Edge → Router (commercial or isolated, cached tenant context; miss → Tenant Context Service)", "Shard Manager: which shard right now; repository is source of truth", "Shard = logical runtime for tenant + product, replicas scale with AWS Auto Scaling", "Dedicated data; outbound via the Egress Gateway"],
  """Walk me through what happens when a request arrives for an isolated tenant."""),
 ("Why is placement not handled by the Router?",
  ["You started there — and favoured it", "The event list: failure, maintenance, deploys, migration, capacity", "None change tenant identity — static vs operational", "Cost: one more component, one more hop; catch: cache invalidation on switch"],
  """Why isn't placement handled by the Router? It would be simpler."""),
 ("A shard is unhealthy. Why not route that tenant to commercial for a few minutes?",
  ["Clear no", "Outage = reliability problem; shared infrastructure = compliance failure", "Availability from replicas, not an escape route", "Three locks + an alert that should read zero"],
  """A shard is unhealthy. Why not route that tenant to commercial for a few minutes? Surely that's better for the customer."""),
 ("Tell me about something that went wrong in production.",
  ["Cutover: a few Routers missed invalidation, ~10 minutes", "Commercial refused — tenant locked as migrated; errors, not a breach", "Detected via per-tenant error rate before the customer noticed", "Fix: switch incomplete until every Router confirms"],
  """Tell me about something that went wrong in production."""),
 ("How did you move existing customers' data out of shared stores?",
  ["Rejected: start fresh, move whole DBs, dual-write", "Copy then switch — one home at a time", "Tenant-scoped extraction by owners; platform ran encrypted transfer", "Bulk → catch-up (change log) → freeze → ownership/counts/checksums → switch → rollback window → delete + verify"],
  """How did you move existing customers' data out of the shared stores?"""),
 ("What was the hardest technical problem?",
  ["GraphQL gateway on Nadel — every edge of the dependency map", "Gateway inside each isolated environment; schema pushed in", "Hydration: readiness extended to the hydration graph; fails at build time", "DataLoader lost tenant context → commercial default; caught by checking where calls went"],
  """What was the hardest technical problem you hit?"""),
 ("How do you deploy a release to all these environments?",
  ["Commercial → wave 0 → canaries with 24h bake → everyone in change windows", "Shard by shard, gates against the tenant's own baseline", "Per-tenant rollback until a contract step; contracts ship separately", "Max two versions of skew; security patches exempt"],
  """How do you deploy a release across all these environments?"""),
 ("Your Router and Tenant Context Service are shared. Isn't that a single failure domain?",
  ["Yes — say it directly", "Steady state served from Router cache; only misses hit the service", "Safe: no tenant switch can happen while the service is down", "Stricter target: 99.99% vs 99.95% per environment"],
  """Your Router and Tenant Context Service are shared. Isn't that a single failure domain for everyone?"""),
 ("How did you get 178 teams to adopt something they didn't design?",
  ["No authority — mandates don't work", "Adoption cheaper than resistance: shard descriptors + the onboarding tool", "Two weeks of one-on-ones, the platform contract", "Planned dependencies; tiers L0–L3 plus L2.5"],
  """How did you get about a hundred and seventy-eight teams to adopt something they didn't design?"""),
 ("Tell me about a time a team pushed back hard.",
  ["Years of custom deployment scripts", "Assumed resistance — sat down with the tech lead", "Real gap: a scaling pattern the descriptor couldn't express", "Added to the model; 4–5 teams reused it; two teams → platform problem"],
  """Tell me about a time a team pushed back hard on you."""),
 ("What did it cost, and was it worth it?",
  ["Smallest tenant ~4–6× commercial — mostly a fixed floor", "Levers: per-shard sizing, right-sizing (~⅓ off), tier minimums, no extra orchestration", "Worth it: these customers couldn't use the cloud at all", "Business: regulated customers moved, starting with a large bank"],
  """What did it cost, and was it worth it?"""),
 ("What would you do differently?",
  ["Cache invalidation from day one — three rounds from one root", "Publish the contract and descriptor model before phase one", "The GraphQL gateway as every edge on the dependency map", "Weakest today: centralisation, override discipline"],
  """Last question. Looking back, what would you do differently?"""),
]

for i, (q, points, nq) in enumerate(MOCK, 1):
    label = 'Mock interview · question %d of %d' % (i, len(MOCK))
    qs = new_slide(f'''<div class="qwrap"><div class="qlabel">{esc(label)}</div>
        <div class="qtext">&ldquo;{rich(q)}&rdquo;</div>
        <div class="think" data-step="1"><div class="thinkl">Answer out loud now</div>
        <div class="thinkbar"><i></i></div><div class="thinkc"></div></div></div>''')
    seg(qs, 0, nq)
    seg(qs, 1, '', kind='think', think=25)
    sid = steps_list('Key points a strong answer hits', [(0, p, 'ok') for p in points[:2]] + [(1, p, 'ok') for p in points[2:]], kicker='Mock · question %d' % i)
    seg(sid, 0, "Check yourself. " + points[0].replace('→', 'then').replace('~', 'about ') + ". " + points[1].replace('→', 'then').replace('~', 'about ') + ".")
    seg(sid, 1, points[2].replace('→', 'then').replace('~', 'about ') + ". " + points[3].replace('→', 'then').replace('~', 'about ') + ".")

sid = statement("That's the interview", "Architecture. Judgement. Scope.",
 "Tell one consistent story, in past tense, with the decision, the reason, and the cost. You built this. Now say it like you did.", kind='ok')
seg(sid, 0, """That's the full mock interview. If you hit most of the key points on most questions, you're ready. If not, you now know exactly which chapters to rewatch. Everything in this interview comes back to three things. Architecture. Judgement. Scope.""")
seg(sid, 1, """Tell one consistent story, in past tense, with the decision, the reason, and the cost. Name the trade-off before they do. Fail closed. Keep your numbers identical. You understand this system deeply now. Go into the room and say it like you built it. Good luck.""")
