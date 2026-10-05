# -*- coding: utf-8 -*-
"""Chapter 8, Lesson 3 — a calendar system."""
from lib import *

lesson_header('8.3', 'Design a calendar system',
              'Recurrence expansion &middot; time zones &middot; invitation state &middot; conflicts',
              dict(reports='InterviewTV list, and 1 very recent report', latest='2026', level='Staff',
                   conf='MEDIUM-HIGH &mdash; corroborated',
                   sources='InterviewTV.io + research pass 3'), 18,
              """Chapter eight, lesson three: a calendar. Create an event, invite people, accept or """
              """reject, view your calendar. It sounds like the easiest question in the course and it """
              """is one of the hardest, because calendars contain two genuinely nasty problems that """
              """have nothing to do with scale: recurring events, and time zones. Both will be in the """
              """follow-ups, and both are where candidates who breezed through the architecture come """
              """apart.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  'Named: <b>calendar data model, recurring events, time zones, invitations, conflicts, '
  'notifications, consistency, query patterns, partitioning</b>'),
 ('Research pass 3 &mdash; candidate report', '2026', 'Staff',
  '&ldquo;Design a calendar (low-level design)&rdquo; &mdash; recent, flagged as a <b>low-level '
  'design</b> question'),
], """Two sources, so medium-high confidence. And one detail in the second one matters: it was """
     """described as a low-level design question.""",
 ["""Which means the expected depth is the data model and the correctness of recurrence and time zones, """
  """not the distributed systems. Do not spend twenty minutes sharding a calendar that could run on one """
  """machine &mdash; spend it on getting the model right."""],
 caveat='Corroborated, and one source says low-level design. Weight the data model heavily.',
 narration_caveat="""Corroborated, and one source explicitly calls it low-level design. So weight the """
                  """data model heavily and the distributed systems lightly.""")

sid = beat('Why this is interesting', 'Two problems that are hard for reasons that are not scale',
           '<div style="font-size:28px;line-height:1.72">'
           '<b>1. Recurrence.</b> &ldquo;Every Tuesday at 10&rdquo; has no end. You cannot store the '
           'instances &mdash; there are infinitely many. So you store a <i>rule</i> and expand it on '
           'read. <span style="color:#ff9a9a">And then someone moves one instance, and your rule no '
           'longer describes reality.</span><br><br>'
           '<b>2. Time zones.</b> A meeting at &ldquo;9 a.m. London&rdquo; is <i>not</i> a fixed UTC '
           'instant &mdash; because of daylight saving, 9 a.m. London is sometimes 09:00 UTC and '
           'sometimes 08:00. <span style="color:#ff9a9a">Storing it as UTC loses the information you '
           'need to be right next March.</span><br><br>'
           '<b>Neither is a scale problem.</b> A calendar for a large company is a few hundred million '
           'rows. It fits on one machine.<br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: some systems are hard because of volume, '
           'and some are hard because the domain is genuinely subtle. Recognising which kind you are '
           'in &mdash; and not reaching for sharding when the problem is semantics &mdash; is the '
           'signal here.</span></div>',
           """Why is this interesting? Because it contains two problems that are hard for reasons that """
           """have nothing to do with scale.""", step=0)
seg(sid, 1, """First, recurrence. &ldquo;Every Tuesday at ten&rdquo; has no end, so you cannot store the """
            """instances &mdash; there are infinitely many of them. You store a rule and expand it when """
            """someone reads. And then somebody moves one instance to Wednesday, and your rule no """
            """longer describes reality.""")
seg(sid, 2, """Second, time zones. A meeting at nine a.m. London is not a fixed U-T-C instant, because """
            """of daylight saving. Nine a.m. London is sometimes nine hundred U-T-C and sometimes eight """
            """hundred. So storing it as U-T-C throws away the information you need in order to still """
            """be right next March.""")
seg(sid, 3, """And neither of those is a scale problem. A calendar for a very large company is a few """
            """hundred million rows. It fits on one machine comfortably.""")
seg(sid, 4, """Which gives the staff-level insight: some systems are hard because of volume, and some """
            """are hard because the domain is genuinely subtle. Recognising which kind you are in """
            """&mdash; and not reaching for sharding when the actual problem is semantics &mdash; is """
            """what is being tested here.""")

think('You create a weekly team meeting, every Tuesday at 10 a.m., with no end date. Someone moves just '
      'the 14th of March to Wednesday. Then you change the time of the whole series to 11 a.m. What '
      'should happen to the 14th of March &mdash; and what does your data model need in order to get '
      'that right?',
      30,
      """Pause, and take a bit longer on this one. A weekly meeting, every Tuesday at ten, no end date. """
      """Someone moves just the fourteenth of March to Wednesday. Then you change the time of the whole """
      """series to eleven. What should happen to the fourteenth of March? And what does your data model """
      """need in order to get that right? Say it out loud.""",
      """Hold that. There is no universally correct answer &mdash; which is exactly why the data model """
      """has to be able to express the distinction.""")

clarify('What I would clarify first', [
 ('Personal calendar, or shared/organisational?',
  'Shared means <b>permissions and delegation</b> &mdash; assistants booking on behalf of executives '
  '&mdash; which is a whole access-control layer.'),
 ('Do we need free/busy search across many people?',
  '<b>Changes the query pattern completely.</b> &ldquo;Show me my week&rdquo; is one person. '
  '&ldquo;Find a slot for these 8 people&rdquo; is an intersection across 8 calendars with '
  'permissions.'),
 ('How are conflicts handled &mdash; prevented, or just shown?',
  'Preventing double-booking is a <b>correctness</b> requirement needing transactions. Showing a '
  'warning is a UI feature. Very different systems.'),
 ('Do invitations have per-recipient state?',
  'Yes, almost certainly &mdash; accept, decline, tentative, propose-new-time. <b>Same shape as InMail '
  'in 7.2</b>: a shared object with per-participant state.'),
 ('Is there external federation &mdash; inviting someone on Google or Outlook?',
  'That means <b>iCalendar / iMIP over email</b>, and you no longer control both sides. A very large '
  'scope increase, so confirm it.'),
 ('How far ahead and behind can people view?',
  'Bounds how far recurrence must be expanded, and whether expansion can be <b>materialised</b> at all.'),
], [
 """Personal calendar or shared and organisational? Shared means permissions and delegation &mdash; """
 """assistants booking on behalf of executives &mdash; which is an entire access control layer that """
 """people forget to scope.""",
 """Do we need free-busy search across many people? That changes the query pattern completely. """
 """&ldquo;Show me my week&rdquo; is one person's data. &ldquo;Find a slot for these eight """
 """people&rdquo; is an intersection across eight calendars, with permissions applied to each.""",
 """How are conflicts handled &mdash; prevented or just shown? Preventing double-booking is a """
 """correctness requirement that needs transactions. Showing a warning is a U-I feature. Those are very """
 """different systems and the question does not say which.""",
 """Do invitations have per-recipient state? Almost certainly yes &mdash; accept, decline, tentative, """
 """propose a new time. And that is the same shape as InMail in lesson seven point two: a shared object """
 """with per-participant state. Worth saying, because you can reuse the reasoning.""",
 """Is there external federation &mdash; inviting someone on Google or Outlook? That means iCalendar """
 """and iMIP over email, and you no longer control both sides of the conversation. A very large scope """
 """increase, so confirm it rather than assuming.""",
 """And how far ahead and behind can people view? That bounds how far recurrence has to be expanded, """
 """and whether you can materialise the expansion at all.""",
])

capacity('Capacity &mdash; and why this is not a scale problem', [
 ('500M users &times; ~5 events / week', '500M &times; 5 &divide; 7', '&asymp; 360M events / day created? no',
  'Realistically ~50M event <b>creations</b>/day &mdash; &asymp; 580 / s. Small'),
 ('Stored events: 500M users &times; 500 events', '250B rows? No &mdash; most are recurrences',
  '&asymp; 5&ndash;10B rows', 'Large but ordinary. <b>Recurrence rules keep this bounded</b>'),
 ('Row size ~500 B', '10B &times; 500 B', '&asymp; 5 TB',
  'A single large database, or a modest shard set. <b>Not a distributed systems problem</b>'),
 ('Calendar views: 500M &times; 10 / day', '5B reads / day &divide; 86,400', '&asymp; 58,000 reads / s',
  '<b>Read-dominated, ~100:1.</b> Caching and read replicas, not sharding'),
 ('Expanding a weekly recurrence over 1 year', '52 instances per rule', '52&times; amplification',
  '<b>Expansion on read is the cost.</b> A year view of 20 recurring meetings = 1,000 instances'),
 ('Free/busy across 8 people for a week', '8 calendars &times; ~40 instances', '&asymp; 320 instances',
  'Trivial per query. <b>The cost is permissions, not data</b>'),
], [
 """Numbers, and the point of running them is to establish that scale is not the problem. Five hundred """
 """million users creating a handful of events a week is roughly fifty million creations a day, about """
 """five hundred and eighty a second. Small.""",
 """Stored events &mdash; and note the first instinct, five hundred million users times five hundred """
 """events, overcounts badly, because most of those are recurrences stored as a single rule rather than """
 """as individual rows. Realistically five to ten billion rows.""",
 """At five hundred bytes a row that is about five terabytes. A single large database or a modest set """
 """of shards. I would say explicitly that this is not a distributed systems problem, because resisting """
 """the urge to shard is part of the answer.""",
 """Calendar views at ten a day per user is five billion reads, about fifty-eight thousand a second. """
 """Read-dominated, roughly a hundred to one &mdash; so read replicas and caching, not sharding.""",
 """Expanding a weekly recurrence over a year is fifty-two instances from one rule, so a fifty-two """
 """times amplification. That expansion on read is the real cost: a year view containing twenty """
 """recurring meetings generates a thousand instances.""",
 """And free-busy across eight people for a week is about three hundred and twenty instances. Trivial """
 """as data. The cost there is permissions &mdash; checking what each of eight people has allowed you """
 """to see &mdash; not the volume.""",
])

A = Arch('Calendar &mdash; rules stored, instances derived', kicker='Architecture', height=800)

A.box('cl',   60, 300, 150, 90, 'Client', '', kind='neutral', step=0, focus=0, small=True)
A.box('api', 250, 290, 190, 110, 'Calendar API', '', kind='ok', step=0, focus=0)
A.arrow('cl', 'api', step=0, focus=0)

A.box('ev',  530, 150, 230, 125, 'Events', 'rule + local time<br>+ IANA zone', kind='ok', step=1,
      focus=[1, 4])
A.arrow('api', 'ev', step=1, label='create', focus=1)

A.box('exc', 530, 320, 230, 110, 'Exceptions', 'moved / cancelled<br>single instances', kind='info',
      step=2, focus=2)
A.arrow('api', 'exc', step=2, focus=2, dashed=True)

A.box('part',530, 490, 230, 110, 'Participation', 'per-invitee state', kind='info', step=3, focus=3)
A.arrow('api', 'part', step=3, focus=3, dashed=True)

A.box('exp',  850, 230, 215, 125, 'Expander', 'rule + exceptions<br>&rarr; instances', kind='shared',
      step=4, focus=[4, 5])
A.arrow('ev', 'exp', step=4, focus=4)
A.arrow('exc', 'exp', step=4, focus=4, dashed=True)

A.box('view',1140, 230, 200, 110, 'Calendar view', 'a date range', kind='ok', step=5, focus=5, small=True)
A.arrow('exp', 'view', step=5, focus=5)

A.box('fb',  1140, 400, 200, 110, 'Free/busy', 'intersect N users', kind='neutral', step=6, focus=6, small=True)
A.arrow('exp', 'fb', step=6, focus=6, dashed=True)

A.box('notif',850, 490, 215, 110, 'Notifications', 'invites, reminders', kind='neutral', step=6,
      focus=6, small=True)
A.arrow('part', 'notif', step=6, focus=6, dashed=True)

A.note(850, 650, 'Never store infinite instances. Store the rule, store the exceptions, expand for the window being viewed.',
       step=4, kind='info', w=520)

A.narrate(0, """A client hits the calendar A-P-I. Nothing surprising yet.""",
          A.flow([(210, 345), (250, 345)]))
A.narrate(1, """Events are stored as a rule plus a local time plus an I-A-N-A time zone identifier """
             """&mdash; Europe slash London, not a U-T-C offset. That choice is the whole time zone """
             """deep dive and I will come back to it.""",
          A.flow([(440, 320), (530, 212)]))
A.narrate(2, """Exceptions are stored separately: the instances that were moved, cancelled or edited """
             """individually. The rule describes the pattern; exceptions describe where reality """
             """departed from it. Keeping them apart is what lets you answer the question I asked you """
             """to pause on.""",
          A.flow([(440, 345), (530, 375)]))
A.narrate(3, """Participation is its own table &mdash; per-invitee accept, decline, tentative. Same """
             """pattern as InMail: a shared object with per-participant state, because one status field """
             """on the event cannot represent eight people.""",
          A.flow([(440, 370), (530, 545)]))
A.narrate(4, """The expander takes a rule and its exceptions and produces concrete instances for a """
             """requested window. This is the core operation of the whole system, and it runs on """
             """read.""",
          A.flow([(760, 212), (850, 292)]))
A.narrate(5, """Which gives a calendar view for a date range. Note what we are not doing: we never """
             """materialise infinite instances, and we never store a row per occurrence of a weekly """
             """meeting that runs forever.""",
          A.flow([(1065, 292), (1140, 285)]))
A.narrate(6, """Free-busy intersects expanded instances across several users, with permissions applied """
             """per calendar. And notifications hang off participation for invites and reminders """
             """&mdash; which is chapter seven's system, reused.""")
A.build()

sid = beat('Deep dive 1', 'Recurrence &mdash; rule, exceptions, and the edit that splits a series',
           '<div style="font-size:26px;line-height:1.65">'
           '<b>Store the rule, not the instances.</b> RFC 5545 RRULE: '
           '<code>FREQ=WEEKLY;BYDAY=TU;INTERVAL=1</code>. One row, infinite occurrences.<br><br>'
           '<b>Then reality intervenes, in three distinct ways:</b><br>'
           '&bull; <b>One instance moved</b> &rarr; an <i>exception</i> row keyed by the original '
           'occurrence date<br>'
           '&bull; <b>One instance cancelled</b> &rarr; an exception row marked deleted (you cannot '
           'delete what was never materialised)<br>'
           '&bull; <b>The whole series changed</b> &rarr; update the rule<br><br>'
           '<b>And the hard case &mdash; &ldquo;this and all future events&rdquo;:</b><br>'
           'You cannot edit the rule, because that would change the past too. '
           '<span style="color:#a8e6a3">So you <b>split the series</b>: end the old rule with an UNTIL '
           'date, and create a new rule starting from the edit point.</span><br><br>'
           '<b>Back to the question:</b> you moved 14 March, then changed the series time. Does 14 '
           'March follow? <span style="color:#ffd483">There is no universally right answer &mdash; '
           'which is exactly why exceptions must be stored as <i>explicit overrides</i> with their own '
           'fields, so the product can decide and the data model can express either choice.</span>'
           '</div>',
           """Deep dive one: recurrence. Store the rule, not the instances. R-F-C five five four five """
           """gives you an R-RULE &mdash; frequency weekly, by day Tuesday &mdash; which is one row """
           """describing infinite occurrences.""", step=0)
seg(sid, 1, """Then reality intervenes, in three distinct ways. One instance is moved, which becomes an """
            """exception row keyed by the original occurrence date. One instance is cancelled, which """
            """becomes an exception row marked deleted &mdash; and note you cannot simply delete """
            """something that was never materialised, so a cancellation is a positive assertion rather """
            """than an absence. And the whole series changes, which updates the rule.""")
seg(sid, 2, """Then the genuinely hard case, which every calendar U-I has a menu item for: """
            """&ldquo;this and all future events&rdquo;. You cannot just edit the rule, because that """
            """would retroactively change the past as well.""")
seg(sid, 3, """So you split the series. End the old rule with an UNTIL date at the edit point, and create """
            """a new rule starting from there. Two rules where there was one. That is why real calendar """
            """data is messier than people expect &mdash; a meeting that has been rescheduled four """
            """times is four linked rules.""")
seg(sid, 4, """And back to the question I asked you to pause on. You moved the fourteenth of March, then """
            """changed the time of the whole series. Does the fourteenth follow the change?""")
seg(sid, 5, """There is no universally right answer. Google and Outlook actually behave differently """
            """here. Which is precisely why exceptions must be stored as explicit overrides with their """
            """own fields &mdash; so the product can decide the policy, and the data model is capable of """
            """expressing either choice. If you store an exception as a diff you have made the decision """
            """implicitly, and badly.""")

sid = beat('Deep dive 2', 'Time zones &mdash; why UTC is the wrong answer',
           '<div style="font-size:26px;line-height:1.65">'
           '<b>The instinct: store everything in UTC.</b> Correct for logs. '
           '<span style="color:#ff9a9a">Wrong for calendars.</span><br><br>'
           '<b>Why:</b> a weekly 9 a.m. London meeting is 09:00 UTC in winter and 08:00 UTC in summer. '
           'Store it as UTC and it drifts an hour twice a year. The user said &ldquo;9 a.m.&rdquo; '
           '&mdash; they meant 9 a.m. <i>forever</i>.<br><br>'
           '<b>So store three things:</b><br>'
           '&bull; the <b>local wall-clock time</b> (09:00)<br>'
           '&bull; the <b>IANA zone identifier</b> (<code>Europe/London</code>, never an offset like '
           '+01:00)<br>'
           '&bull; the recurrence rule<br>'
           'Then <b>convert to UTC at expansion time</b>, using the zone rules in force on that date.'
           '<br><br>'
           '<b>The consequences that catch people:</b><br>'
           '&bull; <b>Zone rules change</b> &mdash; governments alter DST with months of notice. Future '
           'instances <i>must</i> be recomputed, which is only possible if you kept the local time<br>'
           '&bull; <b>Some local times do not exist</b> (clocks spring forward) or <b>happen '
           'twice</b> (clocks go back) &mdash; your expander needs a documented policy<br>'
           '&bull; <b>All-day events have no time zone at all</b> &mdash; a birthday is the 3rd of June '
           'everywhere. <span style="color:#a8e6a3">Storing it as an instant is how birthdays show up a '
           'day early in Sydney.</span></div>',
           """Deep dive two: time zones, and the headline is that U-T-C is the wrong answer here.""",
           step=0)
seg(sid, 1, """The instinct to store everything in U-T-C is correct for logs and for almost everything """
            """else in this course. It is wrong for calendars, and the reason is specific.""")
seg(sid, 2, """A weekly nine a.m. London meeting is nine hundred U-T-C in winter and eight hundred U-T-C """
            """in summer. If you store the U-T-C instant, the meeting drifts by an hour twice a year. """
            """The user said nine a.m., and they meant nine a.m. forever &mdash; the local time is the """
            """intent, and U-T-C is a lossy encoding of it.""")
seg(sid, 3, """So store three things: the local wall-clock time, the I-A-N-A zone identifier &mdash; """
            """Europe slash London, never a numeric offset like plus one hour &mdash; and the """
            """recurrence rule. Then convert to U-T-C at expansion time using the zone rules in force on """
            """that particular date.""")
seg(sid, 4, """And then three consequences that catch people. Zone rules change &mdash; governments """
            """alter daylight saving with a few months' notice, and it happens every year somewhere. """
            """Future instances have to be recomputed, and that is only possible if you kept the local """
            """time rather than a baked U-T-C instant.""")
seg(sid, 5, """Some local times do not exist, because the clocks sprang forward over them, and some """
            """happen twice. If someone schedules a meeting at one thirty a.m. on a transition night, """
            """your expander needs a documented policy rather than an exception.""")
seg(sid, 6, """And all-day events have no time zone at all. A birthday is the third of June everywhere """
            """in the world. Storing it as an instant is exactly how birthdays end up showing a day """
            """early in Sydney, which is a bug every calendar has shipped at least once.""")

tradeoff('Expand recurrences on read, or materialise them', [
 ('Expand on read, every time', 'ok',
  ['<b>One row per rule</b> &mdash; storage stays small', 'An edit to the series is a single update',
   'Always correct, including after a timezone rule change'],
  ['CPU on every view', 'Free/busy across N people expands N calendars',
   'Complex queries ("find all meetings with Bob") must expand to answer']),
 ('Materialise instances into rows', 'info',
  ['Queries are plain SQL over a table', 'Free/busy and search are easy',
   'Indexing by time just works'],
  ['<b>Infinite recurrences cannot be materialised</b> &mdash; you must pick a horizon',
   'A series edit rewrites thousands of rows',
   '<b>A DST rule change invalidates every future row</b>']),
 ('Hybrid: materialise a rolling window, expand beyond it', 'shared',
  ['Fast for the common case (this month)', 'Correct for the far future',
   'Search and free/busy work on the materialised window'],
  ['Two code paths that must agree', 'The window must be maintained as time advances',
   'Invalidation on edit is fiddly']),
], 'Expand on read, with a cache of expanded instances per user per window. It is the only option that '
   'stays correct when timezone rules change, and correctness is the whole difficulty here.',
 'If free/busy search across thousands of users were the dominant query, I would materialise a rolling '
 '90-day window, because that query cannot afford to expand thousands of calendars on demand.',
 [
 """Trade-off: expand recurrences on read, or materialise them into rows? Expanding on read keeps one """
 """row per rule, storage stays small, a series edit is a single update, and it is always correct """
 """&mdash; including after a timezone rule change. It costs C-P-U on every view, and free-busy across """
 """N people means expanding N calendars.""",
 """Materialising instances makes queries plain S-Q-L, free-busy and search easy, and indexing by time """
 """just works. But infinite recurrences cannot be materialised, so you must pick a horizon. A series """
 """edit rewrites thousands of rows. And the one that really hurts: a daylight saving rule change """
 """invalidates every future materialised row, so you are rebuilding them anyway.""",
 """The hybrid materialises a rolling window and expands beyond it &mdash; fast for this month, correct """
 """for the far future. Two code paths that must agree, and fiddly invalidation.""",
 """I would expand on read, with a cache of expanded instances per user per window. It is the only """
 """option that stays correct when timezone rules change, and correctness is the entire difficulty in """
 """this problem.""",
 """What would flip it: if free-busy search across thousands of users were the dominant query, I would """
 """materialise a rolling ninety-day window &mdash; because that particular query cannot afford to """
 """expand thousands of calendars on demand, and at that point the invalidation cost is worth """
 """paying.""",
])

failures('What happens when each piece dies', [
 ('A government changes DST rules', 'Future meetings shift by an hour',
  '<b>Only recoverable because you stored local time + zone.</b> Update the tz database and '
  're-expand. Anyone who stored UTC instants has silently wrong meetings and no way to fix them'),
 ('A meeting is scheduled at a non-existent local time', 'Expansion fails or picks arbitrarily',
  'Document the policy &mdash; typically shift forward by the gap. <b>Do not let it throw</b>; a '
  'calendar that cannot render a week is worse than one with a debatable hour'),
 ('Two people accept the same slot concurrently (a bookable room)', 'Double booking',
  'If booking must be <b>prevented</b>, it needs a transaction on the room &mdash; the '
  '<b>invariant on one row</b> pattern. Showing a warning needs none of that'),
 ('Invitation delivered, event write fails', 'An invite to a meeting that does not exist',
  'Write the event first, then invitations &mdash; <b>same ordering rule as every two-store system</b> '
  'in this course'),
 ('Organiser deletes a series with 200 attendees', '200 calendars must update',
  'Fan out cancellations asynchronously, idempotently. <b>Attendees&rsquo; copies are derived from the '
  'participation table</b>, so a missed update is repairable'),
 ('A single calendar has 100,000 events', 'Views become slow',
  'Expansion is bounded by the <i>window</i>, not the calendar size &mdash; so this mostly does not '
  'bite. <b>Index by (userId, startTime)</b> and the window query stays cheap'),
], [
 """Failures, and the first one is the interesting one. A government changes daylight saving rules and """
 """future meetings shift by an hour. This is only recoverable because you stored local time plus zone """
 """&mdash; you update the timezone database and re-expand. Anyone who stored U-T-C instants now has """
 """silently wrong meetings and genuinely no way to fix them, because the original intent was """
 """discarded. That is the strongest argument for the data model.""",
 """A meeting scheduled at a local time that does not exist, because the clocks sprang forward over it. """
 """Document the policy &mdash; typically shift forward by the size of the gap &mdash; and do not let """
 """it throw. A calendar that cannot render a week is far worse than one that put a meeting at a """
 """debatable hour.""",
 """Two people accepting the same slot for a bookable room gives a double booking. If booking must be """
 """prevented rather than warned about, that needs a transaction on the room row &mdash; the """
 """invariant-on-one-row pattern. If a warning is enough, it needs none of that, which is why the """
 """clarifying question mattered.""",
 """Invitation delivered but the event write failed gives an invite to a meeting that does not exist. """
 """Write the event first, then invitations &mdash; the same ordering rule as every two-store system in """
 """this course.""",
 """An organiser deleting a series with two hundred attendees means two hundred calendars must update. """
 """Fan out cancellations asynchronously and idempotently, and note that attendees' views are derived """
 """from the participation table, so a missed update is repairable rather than lost.""",
 """And a single calendar with a hundred thousand events. Views stay fast, because expansion is bounded """
 """by the window being viewed rather than by the size of the calendar. Index by user and start time """
 """and the window query remains cheap &mdash; which is a nice case of the design already handling """
 """something without special effort.""",
])

say('What I should actually say in the room', [
 'One source describes this as a low-level design question, so I want to spend my time on the data '
 'model rather than on sharding &mdash; a calendar for 500 million users is a few terabytes and is not '
 'a distributed systems problem.',
 'The two genuinely hard parts are recurrence and time zones, and neither is about scale.',
 'For recurrence I store a rule, not instances &mdash; an RRULE with one row for infinitely many '
 'occurrences &mdash; plus a separate exceptions table for instances that were moved or cancelled.',
 '&ldquo;This and all future events&rdquo; cannot edit the rule, because that would change the past. '
 'It splits the series: end the old rule with an UNTIL and start a new one.',
 'For time zones, UTC is the wrong answer. 9 a.m. London is a different UTC instant in summer and '
 'winter, so I store local time plus an IANA zone identifier and convert at expansion time.',
 'That matters because governments change DST rules. If you stored UTC instants, every future meeting '
 'is silently wrong and unrecoverable; if you stored local time, you update the tz database and '
 're-expand.',
 'Invitations have per-recipient state &mdash; accept, decline, tentative &mdash; which is the same '
 'shared-object-with-per-participant-state shape as the messaging question.',
], [
 """The sentences. Open by naming what kind of question this is, because it stops you spending twenty """
 """minutes on sharding that earns nothing.""",
 """Then the two hard parts, the recurrence model with the series-split case, and the time zone """
 """decision with the reason U-T-C is wrong.""",
 """The sixth sentence is the one that proves the point &mdash; the D-S-T rule change, where one data """
 """model is recoverable and the other is not. Finish by connecting invitations back to InMail, which """
 """shows you are carrying patterns across questions.""",
])

followups([
 'How do you model the calendar data?',
 'How do you handle recurring events?',
 'How do you handle time zones?',
 'How do invitations work?',
 'How do you detect conflicts?',
 'How do notifications fit in?',
 'What consistency do you need?',
 'What are the query patterns, and how do you partition?',
], [
 'Find a 30-minute slot that works for 8 people next week. How?',
 'A recurring meeting has been edited 50 times. How do you keep reads fast?',
 'Now support booking rooms, where double-booking must be impossible.',
 'How do you federate with Google Calendar and Outlook?',
 'How do you handle an organiser leaving the company?',
],
 """The reported follow-ups are the lesson. On partitioning: by user I-D, so one person's calendar is """
 """on one shard and a week view is a single-shard read. Consistency only needs to be strong for """
 """bookable resources where double-booking must be prevented; everything else is fine eventual.""",
 """The staff-level follow-ups are where it gets real. Finding a slot for eight people is expanding """
 """eight calendars for the window, intersecting the free time, and applying permissions &mdash; the """
 """cost is the permission checks rather than the data. A meeting edited fifty times means fifty """
 """exception rows, so you cache the expanded window per user and invalidate on edit. Room booking """
 """needs a real transaction on the room, which is the invariant-on-one-row idea. Federation means """
 """iCalendar over email and accepting that you do not control the other side, so state can diverge and """
 """you need reconciliation. And an organiser leaving is a lovely operational question &mdash; their """
 """recurring meetings outlive them, so ownership has to be transferable, and most calendar systems """
 """handle this badly.""")

cheatsheet('Calendar &mdash; the one-page card', [
 ('Requirements', 'Create events, invite, accept/decline, view. <b>Recurrence and time zones are the '
                  'hard parts</b>'),
 ('Scale', '~580 creations/s, ~58k reads/s, ~5&ndash;10B rows, ~5 TB. <b>Not a scale problem</b>'),
 ('Core architecture', 'API &rarr; events (rule + local time + IANA zone), exceptions, participation '
                       '&rarr; expander &rarr; view / free-busy'),
 ('Data store', 'One row per <b>rule</b>, not per instance; exceptions as explicit overrides; '
                'participation as per-invitee state'),
 ('Partition key', '<code>userId</code> &mdash; one person&rsquo;s calendar on one shard, so a week '
                   'view is a single-shard read'),
 ('Cache', 'Expanded instances per user per window, invalidated on edit. <b>Expansion is the cost</b>'),
 ('Queue', 'Invitation fanout, cancellations and reminders &mdash; all async and idempotent'),
 ('Consistency', 'Eventual everywhere <b>except bookable resources</b>, where preventing a double '
                 'booking needs a transaction on one row'),
 ('Failure handling', 'Document the non-existent-local-time policy; event before invitations; '
                      're-expand after a tz database update'),
 ('Key deep dives', 'Rule + exceptions + series splitting &middot; why UTC is wrong'),
 ('Biggest trade-off', 'Expand on read vs materialise &mdash; and <b>only expansion survives a '
                       'timezone rule change</b>'),
], [
 """The card. Scale is on here mainly to say it is not the problem. Architecture in one line, and the """
 """data store row carries the two decisions that matter: one row per rule, and exceptions as explicit """
 """overrides.""",
 """Partition by user I-D so a week view is single-shard. Cache expanded instances, because expansion """
 """is the actual cost.""",
 """Consistency is eventual except for bookable resources. Failure handling includes re-expanding after """
 """a timezone database update. And the biggest trade-off: expand on read versus materialise, where """
 """only expansion survives a timezone rule change.""",
])

say('The 60-second answer', [
 'One report describes this as a low-level design question, and the numbers agree &mdash; about 5 TB '
 'and 58,000 reads a second &mdash; so I am going to spend my time on the data model rather than on '
 'sharding.',
 'The two hard parts are recurrence and time zones, and neither is about scale.',
 'For recurrence I store a rule rather than instances: one RRULE row describes infinitely many '
 'occurrences, with a separate exceptions table for instances that were individually moved or '
 'cancelled. &ldquo;This and all future events&rdquo; cannot simply edit the rule, because that would '
 'rewrite the past &mdash; it ends the old rule with an UNTIL and starts a new one.',
 'For time zones, UTC is the wrong answer. Nine a.m. London is a different UTC instant in summer and '
 'winter, so storing the instant means the meeting drifts an hour twice a year. I store local wall-clock '
 'time plus an IANA zone identifier, and convert at expansion time.',
 'That pays off when a government changes daylight saving rules: with local time stored, I update the '
 'timezone database and re-expand. If I had stored UTC instants, every future meeting is silently wrong '
 'and there is no way back.',
 'Invitations carry per-recipient state, which is the same shared-object-with-per-participant-state '
 'shape as messaging &mdash; and I expand recurrences on read with a per-user cache, because '
 'materialised instances cannot survive a timezone rule change anyway.',
], [
 """The sixty-second answer. It opens by classifying the question, which earns you permission to skip """
 """the distributed systems theatre.""",
 """The fifth sentence is the strongest thing in this answer &mdash; one data model is recoverable """
 """after a D-S-T change and the other is not. That is a concrete, checkable consequence of a modelling """
 """decision, and it is exactly the kind of reasoning a Staff interviewer is listening for.""",
], kicker='60-second interview answer')
