# -*- coding: utf-8 -*-
"""Chapter 8, Lesson 2 — package logistics and routing."""
from lib import *

lesson_header('8.2', 'Design a package logistics and routing system',
              'State machine &middot; scan events &middot; idempotency &middot; what you do NOT optimise',
              dict(reports='InterviewTV list only', latest='2026', level='Staff',
                   conf='MEDIUM &mdash; single source', sources='InterviewTV.io'), 18,
              """Chapter eight, lesson two: a logistics system for a shipping company. Packages move """
              """from sender to recipient, and the system must be efficient, reliable, adaptable and """
              """scalable. And then the follow-ups are unusual &mdash; where are you optimising, where """
              """are you <i>not</i> optimising, and what are you optimising for? That is not a systems """
              """question. That is asking whether you can identify a goal and defend a scope, which is """
              """the most staff-level thing in this entire course.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  'Efficient, reliable, adaptable, scalable. Follow-ups: <b>where are you optimising, where are you '
  'NOT optimising, what are you optimising for</b> &mdash; efficiency, throughput, safety, '
  'reliability, ease of use'),
], """Single source, medium confidence. And this question is shaped differently from every other one in """
     """the course &mdash; the requirements are four adjectives, and the follow-ups are about scope """
     """rather than mechanism.""",
 ["""That is deliberate. A question with vague requirements is testing whether you will impose """
  """structure on it. If you wait to be told what to optimise for, you have already failed the """
  """question."""],
 caveat='Single source, and deliberately open-ended. The state machine and event-sourcing machinery is '
        'standard and transfers widely.',
 narration_caveat="""Single source and deliberately open-ended. The state machine and event sourcing """
                  """machinery is standard, so it transfers widely.""")

sid = beat('Why this is interesting', 'Four adjectives and no numbers. <b>That is the test.</b>',
           '<div style="font-size:28px;line-height:1.72">'
           '&ldquo;Efficient, reliable, adaptable, scalable&rdquo; are not requirements. They are the '
           'absence of requirements.<br><br>'
           '<span style="color:#ff9a9a">The failure mode is to start drawing boxes and hope structure '
           'emerges.</span> It will not.<br><br>'
           '<b>What I would do instead &mdash; and say out loud:</b><br>'
           '&bull; Pick <b>one</b> thing to optimise for, and justify it<br>'
           '&bull; Name what I am explicitly <b>not</b> optimising, and why that is safe<br>'
           '&bull; Make the choice <i>falsifiable</i>: &ldquo;if X were true instead, I would choose '
           'differently&rdquo;<br><br>'
           '<b>And there is a physical reality here that software questions do not have:</b><br>'
           'A package is a <b>physical object in exactly one place</b>. You cannot replicate it, you '
           'cannot retry it, and the source of truth is a scanner in a warehouse at 3 a.m. that may be '
           'offline. <span style="color:#a8e6a3">The software is a <i>model</i> of reality, and the '
           'model can be wrong.</span><br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: when requirements are adjectives, your '
           'first job is to turn them into a decision with a stated cost.</span></div>',
           """Why is this interesting? Because efficient, reliable, adaptable and scalable are not """
           """requirements. They are the absence of requirements.""", step=0)
seg(sid, 1, """The failure mode is to start drawing boxes and hope structure emerges from the drawing. """
            """It will not, and forty minutes later you will have a diagram nobody can evaluate because """
            """nobody agreed what good looked like.""")
seg(sid, 2, """So what I would do instead, and say out loud: pick one thing to optimise for and justify """
            """it. Name what I am explicitly not optimising and why that is safe. And make the choice """
            """falsifiable &mdash; if this other thing were true, I would choose differently. That last """
            """move is what turns an opinion into engineering.""")
seg(sid, 3, """And there is a physical reality here that pure software questions do not have. A package """
            """is a physical object in exactly one place. You cannot replicate it, you cannot retry it, """
            """and your source of truth is a handheld scanner in a warehouse at three in the morning """
            """that may be offline.""")
seg(sid, 4, """Which means the software is a model of reality, and the model can be wrong. That is a """
            """genuinely different failure mode from anything else in this course &mdash; everywhere """
            """else, the database is the truth. Here the database is a belief about where a box """
            """is.""")
seg(sid, 5, """So the staff-level insight: when requirements are adjectives, your first job is to turn """
            """them into a decision with a stated cost. Not to build faster &mdash; to decide what you """
            """are building toward.""")

think('A scanner in a warehouse records a package as "arrived at hub B". The network is down, so the '
      'event is queued locally. Two hours later it finally uploads &mdash; but by then the package has '
      'already been scanned as "departed hub B" from a different device. What should your system do?',
      25,
      """Pause. A scanner records a package as arrived at hub B, but the network is down so the event """
      """queues locally. Two hours later it uploads &mdash; and by then the package has already been """
      """scanned as departed hub B from a different device. What should your system do? Say it out """
      """loud.""",
      """Hold that. Out-of-order physical events are the defining problem here, and the answer is not """
      """&ldquo;reject it&rdquo;.""")

clarify('What I would clarify first', [
 ('What are we actually optimising for &mdash; cost, speed, or reliability of the <i>promise</i>?',
  '<b>Ask this first and insist on an answer.</b> Cheapest routing, fastest delivery and "arrives when '
  'we said" are three different systems with three different architectures.'),
 ('Are we routing the packages, or tracking packages someone else routes?',
  '<b>Enormous scope difference.</b> Tracking is an event pipeline. Routing is an optimisation problem '
  'with vehicles, capacity and time windows.'),
 ('What is the package volume and the number of facilities?',
  '10M packages/day across 500 hubs is a different system from 100k across 10.'),
 ('How accurate must tracking be &mdash; hub-level or GPS-level?',
  'Hub-level is a handful of events per package. Continuous GPS is a <b>streaming telemetry system</b> '
  'and a hundred times the data.'),
 ('Can facilities operate offline?',
  '<b>Almost certainly yes</b>, and this changes everything: scanners must work without a network, '
  'which forces idempotency and out-of-order tolerance.'),
 ('Who are the users &mdash; customers, drivers, or operations staff?',
  'Three products. The customer wants an ETA; the driver wants a route; operations wants to find the '
  'bottleneck. <b>Different reads, different systems on top of the same events.</b>'),
], [
 """What are we actually optimising for &mdash; cost, speed, or reliability of the promise? I would ask """
 """this first and insist on an answer, because the cheapest routing, the fastest delivery, and """
 """&ldquo;it arrives when we said it would&rdquo; are three different systems. If the interviewer """
 """will not choose, I will choose and say why.""",
 """Are we routing the packages, or tracking packages that someone else routes? That is an enormous """
 """scope difference. Tracking is an event pipeline. Routing is a vehicle routing optimisation problem """
 """with capacity and time windows, and it is N-P-hard.""",
 """What is the volume and the number of facilities? Ten million packages a day across five hundred """
 """hubs is a different system from a hundred thousand across ten.""",
 """How accurate must tracking be &mdash; hub level or G-P-S level? Hub level is a handful of events """
 """per package. Continuous G-P-S is a streaming telemetry system and roughly a hundred times the """
 """data.""",
 """Can facilities operate offline? Almost certainly yes, and this changes everything, because scanners """
 """must work without a network &mdash; which forces idempotency and out-of-order tolerance into the """
 """core of the design rather than the edges.""",
 """And who are the users &mdash; customers, drivers, or operations staff? Those are three products. """
 """The customer wants an E-T-A. The driver wants a route. Operations wants to find the bottleneck. """
 """Different reads, different systems, all sitting on the same events.""",
])

capacity('Capacity', [
 ('10M packages / day', '10M &divide; 86,400', '&asymp; 115 packages / s',
  'Tiny. <b>This is not a throughput problem</b> &mdash; say so'),
 ('~10 scan events per package', '10M &times; 10', '&asymp; 1,150 events / s',
  'Peak maybe 5,000/s during evening sorting. Still modest'),
 ('Event size ~200 B', '100M events/day &times; 200 B', '&asymp; 20 GB / day',
  '~7 TB/year. <b>Keep every event forever</b> &mdash; it is the audit trail'),
 ('Customer tracking lookups', '10M packages &times; ~5 checks', '&asymp; 580 reads / s',
  'Read-heavy relative to writes, and <b>every read wants the current state</b>, not the events'),
 ('Current-state table', '10M in flight &times; ~1 KB', '&asymp; 10 GB',
  'Fits in memory. <b>Derived from events, so rebuildable</b>'),
 ('Routing computation', '500 hubs, vehicle routing per hub per wave',
  '<b>NP-hard, solved heuristically</b>', 'Offline batch, minutes to run. <b>Not on any request path</b>'),
], [
 """Numbers. Ten million packages a day is about a hundred and fifteen a second. Tiny &mdash; and I """
 """would say so immediately, because it tells the interviewer I am not going to waste time on """
 """throughput.""",
 """About ten scan events per package gives roughly eleven hundred events a second, maybe five thousand """
 """during the evening sorting wave. Still modest.""",
 """Events at two hundred bytes give twenty gigabytes a day, around seven terabytes a year. Which means """
 """you can keep every event forever &mdash; and you should, because it is the audit trail for """
 """physical custody of other people's property.""",
 """Customer tracking lookups are about five hundred and eighty a second, so reads outnumber writes. """
 """And critically, every read wants the current state, not the event history &mdash; which tells you """
 """to maintain a current-state view rather than replaying events per request.""",
 """That current-state table is ten million in-flight packages at about a kilobyte, so ten gigabytes. """
 """Fits in memory, and it is derived from the events so it is rebuildable.""",
 """And routing computation: vehicle routing per hub per wave is N-P-hard and solved heuristically, """
 """running offline in minutes. The key point is that it is not on any request path &mdash; so its """
 """latency does not matter and you can afford a good heuristic rather than a fast one.""",
])

A = Arch('Logistics &mdash; events in, state derived, routing offline', kicker='Architecture', height=800)

A.box('scan',  60, 180, 160, 95, 'Scanners', 'hubs, vans,<br>may be offline', kind='neutral', step=0,
      focus=[0, 1], small=True)
A.box('edge', 265, 170, 190, 110, 'Edge buffer', 'local queue', kind='ok', step=1, focus=1)
A.arrow('scan', 'edge', step=0, focus=0)

A.box('ing',  520, 170, 200, 110, 'Ingest', 'dedupe by<br>(pkg, type, ts)', kind='ok', step=2, focus=2)
A.arrow('edge', 'ing', step=1, label='when online', focus=1, dashed=True)

A.box('log',  790, 170, 215, 110, 'Event log', 'append-only,<br>kept forever', kind='ok', step=3,
      focus=[3, 6])
A.arrow('ing', 'log', step=3, focus=3)

A.box('sm',   790, 350, 215, 110, 'State machine', 'validates transition', kind='info', step=4, focus=4)
A.arrow('log', 'sm', step=4, focus=4)

A.box('state',1070, 350, 210, 110, 'Current state', '10M in flight', kind='dp', step=4, focus=[4, 5], small=True)
A.arrow('sm', 'state', step=4, focus=4)

A.box('track',1070, 530, 210, 100, 'Tracking API', 'customer reads', kind='neutral', step=5, focus=5, small=True)
A.arrow('state', 'track', step=5, focus=5)

A.box('ops',  790, 530, 215, 100, 'Ops dashboards', 'find the bottleneck', kind='neutral', step=5,
      focus=5, small=True)
A.arrow('log', 'ops', step=5, focus=5, dashed=True)

A.box('route', 520, 350, 200, 110, 'Routing engine', 'offline batch', kind='shared', step=6, focus=6)
A.arrow('log', 'route', step=6, focus=6, dashed=True)
A.arrow('route', 'edge', step=6, label='manifests', focus=6, dashed=True)

A.note(1330, 170, 'The log is the truth about what was OBSERVED. Current state is a belief derived from it — and beliefs can be wrong.',
       step=3, kind='info', w=440)

A.narrate(0, """Scanners in hubs and vans. They may be offline, and designing as if they are always """
             """online is the mistake that makes this system fail in real warehouses.""",
          A.flow([(220, 227), (265, 225)]))
A.narrate(1, """So each scanner writes to a local buffer first and uploads when it has a network. That """
             """one decision &mdash; buffer locally, upload later &mdash; is what forces idempotency """
             """and out-of-order handling everywhere downstream.""",
          A.flow([(455, 225), (520, 225)]))
A.narrate(2, """Ingest deduplicates on package, event type and timestamp, because a scanner that is """
             """unsure whether its upload succeeded will send again. Duplicates are certain, not """
             """hypothetical.""",
          A.flow([(720, 225), (790, 225)]))
A.narrate(3, """The event log is append-only and kept forever. This is the truth about what was """
             """<i>observed</i> &mdash; and that phrasing matters, because it is not truth about where """
             """the package is. It is truth about what a scanner reported.""")
A.narrate(4, """A state machine consumes the log, validates each transition and maintains current state """
             """for ten million in-flight packages. Current state is derived, so it can always be """
             """rebuilt by replaying &mdash; same pattern as CoderPad and the key-value store.""",
          A.flow([(897, 280), (897, 350), (1070, 405)]))
A.narrate(5, """Customers read current state through a tracking A-P-I. Operations reads the raw log, """
             """because finding a bottleneck means asking questions about the sequence, not the current """
             """position.""",
          A.flow([(1175, 460), (1175, 530)]))
A.narrate(6, """And routing runs offline as a batch, reading the log and producing manifests that go back """
             """out to the hubs and vans. Note it is completely off the request path: routing is """
             """N-P-hard, so being allowed to take five minutes is what makes a good answer """
             """affordable.""",
          A.flow([(790, 405), (720, 405)]))
A.build()

sid = beat('Deep dive 1', 'The state machine, and the out-of-order scan',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>A package has a lifecycle:</b> created &rarr; collected &rarr; at hub &rarr; in transit '
           '&rarr; out for delivery &rarr; delivered. Plus exceptions: failed delivery, returned, lost, '
           'damaged.<br><br>'
           '<b>Modelling it as a state machine buys three things:</b><br>'
           '&bull; <b>Validation</b> &mdash; &ldquo;delivered&rdquo; from &ldquo;created&rdquo; is '
           'impossible and should raise an exception, not be written<br>'
           '&bull; <b>Clarity</b> &mdash; everyone agrees what the states are<br>'
           '&bull; <b>Operations</b> &mdash; &ldquo;how many packages are stuck in <i>at hub</i> for '
           '&gt;24 h&rdquo; is now a real query<br><br>'
           '<b>But the physical world does not respect your state machine.</b> The out-of-order scan:<br>'
           '&bull; A late &ldquo;arrived at B&rdquo; lands after &ldquo;departed B&rdquo;<br>'
           '&bull; <span style="color:#ff9a9a">Rejecting it is wrong</span> &mdash; the event really '
           'happened; your <i>order</i> is wrong, not the event<br>'
           '&bull; <b>Order by the scan timestamp, not arrival time.</b> Accept it, insert it into '
           'history, recompute current state<br>'
           '&bull; Current state = <b>the latest event by scan time</b>, not the last one received<br><br>'
           '<span style="color:#ffd483">That is why state is derived rather than mutated in place: a '
           'late event means recomputing, which is trivial from a log and impossible from a mutated '
           'row.</span></div>',
           """Deep dive one: the state machine, and the out-of-order scan that breaks it. A package has """
           """a lifecycle &mdash; created, collected, at hub, in transit, out for delivery, delivered """
           """&mdash; plus exceptions like failed delivery, returned, lost and damaged.""", step=0)
seg(sid, 1, """Modelling it explicitly as a state machine buys three things. Validation, so that """
            """&ldquo;delivered&rdquo; arriving directly from &ldquo;created&rdquo; raises an exception """
            """rather than being silently written. Clarity, so everyone agrees what the states are. And """
            """operations, because &ldquo;how many packages have been stuck at a hub for more than """
            """twenty-four hours&rdquo; becomes a real query rather than a guess.""")
seg(sid, 2, """But the physical world does not respect your state machine, which is the answer to what I """
            """asked you to pause on. A late &ldquo;arrived at B&rdquo; lands after &ldquo;departed """
            """B&rdquo; has already been processed.""")
seg(sid, 3, """Rejecting it is the wrong answer, and this is the key realisation. The event really """
            """happened. The package genuinely did arrive at B before it departed. Your ordering is """
            """wrong, not the event.""")
seg(sid, 4, """So order by the scan timestamp, not by arrival time at your server. Accept the late event, """
            """insert it into the package's history in its correct chronological position, and """
            """recompute current state. And current state is defined as the latest event by scan time, """
            """not the last one you received.""")
seg(sid, 5, """Which is exactly why state is derived rather than mutated in place. A late event means """
            """recomputing, and recomputing is trivial when you have a log and impossible when you have """
            """a mutated row. This is the third system in this course where storing events and deriving """
            """state is the answer, and that repetition is the point of putting these three questions """
            """in one chapter.""")

sid = beat('Deep dive 2', 'What I am <b>not</b> optimising, and why that is safe',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>I am optimising for: reliability of the promise.</b> Not speed, not cost. The package '
           'arrives within the window we committed to, and the customer always knows where it is.<br><br>'
           '<b>Why that one:</b> in logistics, a missed promise costs a customer; a slightly slower '
           'route costs pennies. <span style="color:#a8e6a3">Optimise the expensive failure, not the '
           'cheap one.</span><br><br>'
           '<b>What I am explicitly NOT optimising, and why it is safe:</b><br>'
           '&bull; <b>Not optimal routing.</b> A 5% better route is worth far less than a route that is '
           'robust to a van breaking down. <span style="color:#ffd483">Heuristic, re-run often, good '
           'enough.</span><br>'
           '&bull; <b>Not real-time GPS tracking.</b> Hub-level events answer &ldquo;where is my '
           'parcel&rdquo; well enough for 100&times; less data.<br>'
           '&bull; <b>Not write throughput.</b> 1,150 events/s is nothing. Any effort here is wasted.<br>'
           '&bull; <b>Not perfect consistency.</b> Tracking being 30 seconds stale is fine; refusing a '
           'scan because the system is busy is not.<br><br>'
           '<b>And make it falsifiable:</b> <span style="color:#a8e6a3">if margins were razor-thin and '
           'fuel dominated cost &mdash; a parcel broker rather than a premium carrier &mdash; I would '
           'optimise routing cost instead and accept a wider delivery window.</span></div>',
           """Deep dive two, and this is the question they actually asked: what am I optimising for, and """
           """what am I not?""", step=0)
seg(sid, 1, """I am optimising for reliability of the promise. Not speed, not cost. The package arrives """
            """within the window we committed to, and the customer always knows where it is.""")
seg(sid, 2, """Why that one? Because in logistics a missed promise costs you a customer, and a slightly """
            """slower route costs pennies. Optimise the expensive failure rather than the cheap one. """
            """That is the justification, and having one is what makes it a decision rather than a """
            """preference.""")
seg(sid, 3, """Now what I am explicitly not optimising. Not optimal routing &mdash; a five percent better """
            """route is worth far less than a route that is robust to a van breaking down, so a """
            """heuristic re-run frequently is good enough. Not real-time G-P-S tracking, because """
            """hub-level events answer &ldquo;where is my parcel&rdquo; well enough for a hundred times """
            """less data.""")
seg(sid, 4, """Not write throughput, because eleven hundred events a second is nothing and any effort """
            """spent there is wasted. And not perfect consistency &mdash; tracking being thirty seconds """
            """stale is fine, whereas refusing a scan because the system is busy is not. Notice each one """
            """comes with the reason it is safe to skip.""")
seg(sid, 5, """And then make it falsifiable, which is the move that elevates the whole answer. If margins """
            """were razor-thin and fuel dominated cost &mdash; if this were a parcel broker rather than """
            """a premium carrier &mdash; I would optimise routing cost instead and accept a wider """
            """delivery window. Stating the condition under which you would choose differently proves """
            """you made a decision rather than had a preference.""")

tradeoff('Where the routing decision is made', [
 ('Centrally, fully planned', 'info',
  ['Globally optimal-ish', 'One place to change policy', 'Easy to audit and explain'],
  ['<b>Breaks the moment reality diverges</b> &mdash; traffic, breakdowns, a hub closing',
   'Needs connectivity to every vehicle', 'Replanning 10M packages is slow']),
 ('Locally, at each hub', 'shared',
  ['Robust &mdash; a hub keeps working when the network is down', 'Fast to recompute locally',
   'Naturally adapts to local conditions'],
  ['No global view &mdash; locally sensible, globally wasteful',
   'Hard to enforce a company-wide policy', 'Each hub can diverge']),
 ('Central plan, local re-plan', 'ok',
  ['Global plan sets the targets', 'Hubs adapt within those constraints',
   '<b>Keeps working when disconnected</b>'],
  ['Two planners to keep consistent', 'Divergence between plan and reality must be reconciled',
   'More complex to reason about']),
], 'Central planning producing manifests, with local re-planning authority at each hub. Hubs must be '
   'able to operate when disconnected, because they will be.',
 'If every vehicle had reliable connectivity and the fleet were small, I would centralise fully '
 '&mdash; the global optimum is worth more when you can actually execute it.',
 [
 """Trade-off: where is the routing decision made? Centrally and fully planned gives you something """
 """close to a global optimum, one place to change policy, and an auditable decision. It breaks the """
 """moment reality diverges &mdash; traffic, a breakdown, a hub closing &mdash; it needs connectivity """
 """to every vehicle, and replanning ten million packages is slow.""",
 """Locally at each hub is robust, because a hub keeps working when the network is down, recomputes """
 """fast, and adapts naturally to local conditions. The cost is no global view, so decisions that are """
 """locally sensible can be globally wasteful, and it is hard to enforce a company-wide policy.""",
 """Central plan with local re-planning is the answer: the global plan sets targets and constraints, """
 """hubs adapt within them, and crucially the hub keeps working when disconnected. The cost is two """
 """planners to keep consistent and divergence that has to be reconciled.""",
 """I would take that, and the deciding argument is the physical one &mdash; hubs must be able to """
 """operate while disconnected, because they will be. Designing around the network being available is """
 """how you get a warehouse full of people unable to scan anything.""",
 """And what would flip it: if every vehicle had reliable connectivity and the fleet were small, I """
 """would centralise fully. The global optimum is worth more when you can actually execute it.""",
])

failures('What happens when each piece dies', [
 ('Scanner is offline', 'Nothing &mdash; it buffers locally',
  '<b>Designed for, not handled.</b> Events upload when connectivity returns, possibly hours later and '
  'out of order. This is normal operation, not an incident'),
 ('The same scan uploads twice', 'Duplicate events in the log',
  'Deduplicate on <code>(packageId, eventType, scanTimestamp, deviceId)</code>. A scanner unsure '
  'whether its upload landed <b>will</b> retry'),
 ('An event arrives out of order', 'State briefly wrong, then corrected',
  '<b>Order by scan time, recompute state.</b> Never reject a real-world event because your model did '
  'not expect it yet'),
 ('An impossible transition arrives', '&ldquo;Delivered&rdquo; for a package still at a hub',
  '<b>Flag it, do not silently accept or reject.</b> Something physical went wrong &mdash; wrong '
  'barcode, wrong package &mdash; and a human needs to look. The system cannot resolve it'),
 ('A package is physically lost', 'No events for days',
  '<b>Absence of events is the signal.</b> Alert on packages with no scan for longer than expected at '
  'their stage &mdash; this is the one failure detected by silence'),
 ('Routing engine is down', 'No new manifests',
  'Hubs continue on the last manifest and local rules. <b>Degraded, not stopped</b> &mdash; which is '
  'the entire argument for local authority'),
], [
 """Failures. Scanner offline: nothing happens, it buffers locally. And I would frame this as designed """
 """for rather than handled &mdash; events upload when connectivity returns, possibly hours later and """
 """out of order, and that is normal operation rather than an incident.""",
 """The same scan uploading twice gives duplicate events. Deduplicate on package, event type, scan """
 """timestamp and device I-D. A scanner that is unsure whether its upload landed will retry, so """
 """duplicates are guaranteed.""",
 """An event arriving out of order makes state briefly wrong and then corrected. Order by scan time and """
 """recompute. The principle worth stating: never reject a real-world event because your model did not """
 """expect it yet. The model is wrong, not the world.""",
 """An impossible transition &mdash; delivered, for a package still sitting at a hub. Flag it, and do """
 """not silently accept or reject it. Something physical has gone wrong: a wrong barcode, the wrong """
 """package scanned. A human needs to look, and the system should be honest that it cannot resolve """
 """it.""",
 """A package physically lost produces no events for days. And here is the interesting one &mdash; the """
 """absence of events is the signal. Alert on packages with no scan for longer than expected at their """
 """current stage. It is the only failure in this course detected by silence rather than by an error, """
 """and it only works because you modelled the expected lifecycle.""",
 """And the routing engine being down means no new manifests. Hubs continue on their last manifest and """
 """local rules &mdash; degraded, not stopped. That is the entire argument for giving hubs local """
 """authority, and it pays off exactly here.""",
])

say('What I should actually say in the room', [
 'The requirements are four adjectives, so before I design anything I want to turn them into a '
 'decision. I am going to optimise for reliability of the promise &mdash; the package arrives in the '
 'window we committed to and the customer always knows where it is.',
 'And I want to say what I am not optimising: not optimal routing, not real-time GPS, not write '
 'throughput. A 5% better route is worth less than a route robust to a van breaking down.',
 'If margins were razor-thin and fuel dominated cost, I would optimise routing cost instead and accept '
 'a wider window &mdash; so that is the condition that would change my mind.',
 'The volumes are small: about 115 packages a second and 1,150 scan events a second. This is not a '
 'throughput problem, so I will not spend time there.',
 'The core model is an event log of scans, kept forever, with current state derived from it. A package '
 'is a physical object, so the log is the truth about what was <i>observed</i>, and current state is a '
 'belief that can be wrong.',
 'Scanners must work offline, which means events arrive late and out of order. I order by scan '
 'timestamp rather than arrival time, accept late events, and recompute &mdash; never reject a real '
 'event because the model did not expect it.',
 'Routing is a central plan with local re-planning authority at each hub, because hubs have to keep '
 'working when disconnected.',
], [
 """The sentences. The first three are the answer to the question they actually asked, and I would """
 """spend real time on them rather than rushing to the diagram.""",
 """Then the numbers that rule out throughput work, then the event-log model with the """
 """observed-versus-belief distinction.""",
 """Then offline scanners forcing out-of-order tolerance, and the routing split. Note that four of """
 """seven sentences are about scope and constraints rather than components &mdash; which is """
 """appropriate for a question whose follow-ups are all about scope.""",
])

followups([
 'Where are you optimising?',
 'Where are you NOT optimising?',
 'What are you optimising for &mdash; efficiency, throughput, safety, reliability, ease of use?',
 'How do you model package state?',
 'How does tracking work?',
 'How do you partition geographically?',
 'How do you handle idempotency and failure recovery?',
], [
 'A hub burns down. What does your system do in the next hour?',
 'How do you give the customer an accurate ETA rather than a status?',
 'How would you detect that one hub is systematically mishandling packages?',
 'Now add international shipping &mdash; customs, multiple carriers. What changes?',
 'How do you prove chain of custody for a disputed delivery?',
],
 """The reported follow-ups lead with the three scope questions, which is unusual and tells you where """
 """the marks are. On geographic partitioning: partition by origin hub or by destination region, """
 """because that keeps the events for one package's journey mostly within one partition &mdash; and """
 """co-locating a package's events makes the state machine cheap.""",
 """The staff-level follow-ups are where the physical reality bites. A hub burning down means """
 """re-routing everything currently destined for it, which is a bulk state transition and should be a """
 """supported operation rather than an emergency script. An accurate E-T-A is a prediction problem """
 """rather than a status lookup &mdash; a model over historical transit times, which is a different """
 """system. Detecting a systematically bad hub is anomaly detection over your event log, and it is a """
 """lovely use of the data you were keeping anyway. International adds customs holds, which are a state """
 """with an unbounded duration, and multiple carriers means you no longer own all the events &mdash; so """
 """your log has gaps. And chain of custody for a dispute is exactly why you keep every event forever """
 """with the device I-D and the operator attached.""")

cheatsheet('Logistics &mdash; the one-page card', [
 ('Requirements', 'Move packages reliably; track them; adapt. <b>Optimising for reliability of the '
                  'promise</b>, explicitly not for optimal routing'),
 ('Scale', '~115 packages/s, ~1,150 scan events/s, ~20 GB/day of events, 10M in flight'),
 ('Core architecture', 'Scanner &rarr; local buffer &rarr; ingest (dedupe) &rarr; append-only event '
                       'log &rarr; state machine &rarr; current state; routing offline'),
 ('Data store', '<b>Event log is truth about what was observed</b>; current state is derived and '
                'rebuildable; both kept, the log forever'),
 ('Partition key', '<code>packageId</code> for events; geography for routing. Co-locating one '
                   'package&rsquo;s events makes the state machine cheap'),
 ('Cache', 'Current-state table (~10 GB) serves tracking reads. The log serves operations'),
 ('Queue', 'Local buffer on every scanner &mdash; <b>offline operation is the normal case</b>'),
 ('Consistency', 'Eventual and deliberately so. <b>Order by scan timestamp, not arrival time</b>'),
 ('Failure handling', 'Dedupe on (package, type, scanTs, device); accept late events and recompute; '
                      'flag impossible transitions for humans; <b>alert on silence</b>'),
 ('Key deep dives', 'State machine and the out-of-order scan &middot; what you are NOT optimising'),
 ('Biggest trade-off', 'Global optimality vs local autonomy &mdash; and <b>hubs must keep working '
                       'disconnected</b>, so autonomy wins'),
], [
 """The card. The requirements row carries the decision, including what you are explicitly not """
 """optimising &mdash; which is unusual for a cheat sheet and appropriate for this question.""",
 """Architecture in one line. The data store row has the phrase worth memorising: the log is truth """
 """about what was observed, and current state is derived. Partition events by package I-D, routing by """
 """geography.""",
 """Consistency is eventual and ordered by scan timestamp rather than arrival. Failure handling ends on """
 """alerting on silence, which is the distinctive one. And the biggest trade-off is global optimality """
 """against local autonomy, where autonomy wins because hubs must keep working disconnected.""",
])

say('The 60-second answer', [
 'The requirements are four adjectives, so my first job is to turn them into a decision. I am '
 'optimising for reliability of the promise &mdash; the package arrives in the window we committed to '
 'and the customer always knows where it is &mdash; because a missed promise costs a customer and a '
 'slightly slower route costs pennies.',
 'And I am explicitly not optimising optimal routing, real-time GPS tracking, or write throughput. If '
 'margins were thin and fuel dominated cost, I would choose differently &mdash; that is the condition '
 'that would change my mind.',
 'The volumes are small: around 115 packages and 1,150 scan events a second, so throughput is not the '
 'problem.',
 'The model is an append-only log of scan events kept forever, with current state derived from it. A '
 'package is a physical object in one place, so the log is truth about what was observed, and current '
 'state is a belief that can be wrong.',
 'Scanners must work offline, so events arrive late and out of order. I order by scan timestamp rather '
 'than arrival time, accept the late event, and recompute &mdash; I never reject a real-world event '
 'because my model did not expect it yet.',
 'Routing is a central plan producing manifests, with local re-planning authority at each hub, because '
 'hubs have to keep operating when the network is down &mdash; and if the routing engine is offline, '
 'hubs degrade rather than stop.',
], [
 """The sixty-second answer. Notice that the first two sentences are entirely about scope, which is """
 """unusual &mdash; and correct, because the follow-ups told you that is what is being """
 """assessed.""",
 """The fourth sentence is the one to land: the log is truth about what was observed, current state is """
 """a belief. That distinction is specific to physical systems and it will not have come up in any """
 """other answer the interviewer hears that day.""",
], kicker='60-second interview answer')
