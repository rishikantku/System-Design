# -*- coding: utf-8 -*-
"""Host Manager round — research pass (7 Oct 2026), kept separate from the coaching content.

Labels (the reader's scheme, shown on every item):
  OFFICIAL   the recruiter pack itself (authoritative where it disagrees with reports)
  MULTIPLE   several independent candidate reports
  SINGLE     one candidate report
  INFERENCE  my reading of the pattern, not a reported question
  PRACTICE   written for practice

Nothing here is a prediction. LeetCode and Glassdoor block fetching, so their reports were read
through search summaries and are graded down a level; that limitation is stated on the page.
"""

DATE = '7 October 2026'

SOURCES = {
 'pack':     ('LinkedIn recruiter pack — "Staff SI Onsite Prep", Host Leader module', None, 'Sep 2026'),
 'exp-exp':  ('Exponent — LinkedIn Senior SWE interview experience', 'https://www.tryexponent.com/experiences/linkedin-senior-software-engineer-interview-dc48e8', '≈ Mar 2026'),
 'lc-staff': ('LeetCode Discuss — LinkedIn Staff SWE interview experience (read via search summary)', 'https://leetcode.com/discuss/post/6858262/linkedin-staff-software-engineer-intervi-mg5c/', 'Jun 2025'),
 'lc-staff2':('LeetCode Discuss — "Staff Software Engineer" (read via search summary)', 'https://leetcode.com/discuss/post/7103201/', '2025'),
 'taro-in':  ('Taro — LinkedIn Staff Engineer, India (offer)', 'https://www.jointaro.com/interviews/companies/linkedin/experiences/staff-engineer-india-may-12-2025-accepted-offer-neutral-ca8f7d74/', '12 May 2025'),
 'gd-rapid': ('Glassdoor — LinkedIn host manager round question (read via search summary)', 'https://www.glassdoor.com/Interview/Host-manager-round-was-a-bunch-of-hr-questions-asked-as-a-rapid-fire-like-what-i-like-about-technology-how-i-got-into-th-QTN_6833086.htm', 'undated'),
 'gd':       ('Glassdoor — LinkedIn Staff SWE interview questions', 'https://www.glassdoor.com/Interview/LinkedIn-Staff-Software-Engineer-Interview-Questions-EI_IE34865.0,8_KO9,32.htm', '2025–2026'),
 'blind-in': ('Blind — LinkedIn Senior SWE Infrastructure interview', 'https://www.teamblind.com/post/linkedin-senior-software-engineer-infrastructure-interview-', '30 Sep 2025'),
 'blind-hm': ('Blind — "Hiring manager round at LinkedIn"', 'https://www.teamblind.com/post/Hiring-manager-round-at-LinkedIn-EZaxran8', 'Mar 2019 (old)'),
 'blind-lv': ('Blind — LinkedIn Staff interview / down-levelling', 'https://www.teamblind.com/post/linkedin-staff-engineer-interview-k0zkh5s3', 'Mar 2022'),
 'user':     ('Supplied by you (recent Staff report you read — original source not re-verified by me)', None, '2026'),
}

# What the round is, from the sources. (claim, label, sources)
FORMAT = [
 ('60 minutes with a hiring leader who can tell you about teams, culture and LinkedIn\'s direction. A deep dive into your background and leadership, with concrete examples of challenges, decisions and accomplishments.', 'OFFICIAL', ['pack']),
 ('Scored on five areas: Communication, Culture, Influence, Mentorship, Conflict.', 'OFFICIAL', ['pack']),
 ('One host-manager round in a 7-round Staff loop (3 coding, craftsmanship, 2 design, host manager).', 'SINGLE', ['taro-in']),
 ('Described as an informal discussion about past projects, team collaboration and role alignment.', 'MULTIPLE', ['taro-in', 'lc-staff']),
 ('Expect a project walk-through probed for your role versus the team\'s, architecture decisions, challenges and how you kept execution on time.', 'MULTIPLE', ['lc-staff', 'gd']),
 ('Some host managers ask an infrastructure or product scenario inside the round (mTLS rollout; a model relevance-vs-latency trade-off).', 'MULTIPLE', ['blind-in', 'user']),
 ('Down-levelling from Staff is reported to turn largely on leadership evidence — which this round is where you show it.', 'SINGLE', ['blind-lv']),
 ('Some reports describe it as lighter ("rapid-fire" motivation and situational questions; or 15–20 minutes of team discussion). The pack says 60 minutes: prepare for the full depth.', 'INFERENCE', ['gd-rapid', 'taro-in']),
]

# Reported questions. (q, label, sources, date, category, note)
REPORTED = [
 ('Walk me through your career progression.', 'SINGLE', ['exp-exp'], '≈ Mar 2026', 'Career', 'Followed by: what triggered each step, why you moved when you did.'),
 ('We have a platform used by 5,000 teams. How would you get them to migrate? What about the holdouts?', 'SINGLE', ['exp-exp'], '≈ Mar 2026', 'Influence', 'Your 178-team migration answers this almost directly.'),
 ('Tell me about the most complex project you recently led — your role, the customer problem, business impact, key architecture decisions, challenges, and how you kept execution on time.', 'MULTIPLE', ['lc-staff', 'gd'], '2025', 'Project', 'The project deep dive, probed for ownership.'),
 ('Tell me about a conflict or disagreement in a critical project.', 'SINGLE', ['lc-staff'], 'Jun–Jul 2025', 'Conflict', ''),
 ('How do you make sure you are not on the critical path?', 'SINGLE', ['lc-staff2'], '2025', 'Leadership', 'A Staff-specific question: leverage through others.'),
 ('Which recommendations or technical suggestions of yours were adopted?', 'SINGLE', ['lc-staff2'], '2025', 'Influence', ''),
 ('Tell me about your current role and how your team is structured.', 'SINGLE', ['user'], '2026', 'Career', 'You supplied this as part of a recent Staff report.'),
 ('What is the most impactful technical decision you have made?', 'SINGLE', ['user'], '2026', 'Decisions', ''),
 ('How did you get alignment across teams?', 'SINGLE', ['user'], '2026', 'Influence', ''),
 ('A model improves recommendation relevance by 15% but raises latency from 50 ms to 200 ms. What do you do?', 'SINGLE', ['user'], '2026', 'Hypothetical', 'Explored: experimentation, latency cohorts, business impact, rollout and rollback, a faster model variant.'),
 ('When did you last disagree with your manager?', 'SINGLE', ['blind-hm'], '2019 (old)', 'Manager fit', 'Old, but a perennial question.'),
 ('What do you like about technology, and how did you get into this domain?', 'SINGLE', ['gd-rapid'], 'undated', 'Motivation', 'Part of a "rapid-fire" set.'),
 ('How would you secure ZooKeeper access with mTLS, and how long would it take?', 'SINGLE', ['blind-in'], '30 Sep 2025', 'Hypothetical', 'Estimation realism: the reporter said two quarters; a commenter said LinkedIn took years.'),
 ('How do you define a quality product or system?', 'SINGLE', ['gd'], '2025', 'Judgment', ''),
 ('What is your code-review strategy as a team grows with more junior engineers?', 'SINGLE', ['gd'], '2025', 'Mentoring', ''),
 ('You join a team that owns a legacy app with poor tests, no monitoring and buggy deploys. What do you do?', 'SINGLE', ['gd'], '2025', 'Hypothetical', ''),
 ('Why LinkedIn? Why this role, and why now?', 'MULTIPLE', ['gd', 'blind-in'], '2025–2026', 'Motivation', ''),
]

# The pack's five areas → where this module covers each.
FOCUS = [
 ('Communication', 'How you communicate and influence technical decisions in your team and across an organisation', ['influence', 'exec']),
 ('Culture', 'How you have built a team culture — intelligent risks, learning from mistakes', ['mentor', 'failure']),
 ('Influence', 'How you spot improvements and get buy-in across the organisation', ['influence', 'migration']),
 ('Mentorship', 'How you grow engineers at team level or larger', ['mentor']),
 ('Conflict', 'Resolving conflict and difficult situations constructively', ['conflict', 'disagree']),
]
