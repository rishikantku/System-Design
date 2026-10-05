# -*- coding: utf-8 -*-
"""Chapter 8, Lesson 1 — CoderPad: collaborative editing and replay."""
from lib import *

lesson_header('8.1', 'Design CoderPad &mdash; collaborative editing and replay',
              'WebSockets &middot; session affinity &middot; ordered event log &middot; replay',
              dict(reports='InterviewTV list &mdash; and LinkedIn interviews run on this tool',
                   latest='2026', level='Staff',
                   conf='MEDIUM &mdash; single source, high plausibility',
                   sources='InterviewTV.io'), 20,
              """Chapter eight, lesson one: CoderPad. A code editor where the interviewee types and the """
              """interviewer watches in real time, a shared drawing pad, invitations by link and """
              """email, and &mdash; the requirement that makes this interesting &mdash; replay the """
              """entire interview showing what happened at what timestamp. That last one changes """
              """everything, and most candidates treat it as a feature to bolt on at the end. It is """
              """the opposite: it is the thing that should shape the design from minute one.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  'Code editor with real-time view, <b>interviewer cannot edit</b>, drawing pad, invite by link and '
  'email, and <b>replay the entire interview with timestamps</b>'),
 ('Context', '&mdash;', '&mdash;',
  'LinkedIn runs its own interviews on a tool like this, so an interviewer asking it has real '
  'intuition about the requirements'),
], """Single source, so medium confidence &mdash; but unusually plausible, because LinkedIn conducts """
     """its interviews on exactly this kind of tool. An interviewer asking it will have strong """
     """intuitions about what matters.""",
 ["""And read the constraints: the interviewer cannot edit. That is a one-way data flow for the code, """
  """which is a dramatic simplification &mdash; and noticing it early saves you from designing """
  """conflict resolution you do not need."""],
 caveat='Single source. The real-time collaboration machinery is standard, so it transfers to any '
        'shared-document question.',
 narration_caveat="""Single source. The real-time collaboration machinery is standard though, so it """
                  """transfers to any shared-document or collaborative-editing question.""")

sid = beat('Why this is interesting', 'Replay is not a feature. It is the <b>storage model</b>.',
           '<div style="font-size:28px;line-height:1.72">'
           'The obvious design: hold the document in memory, broadcast changes, save the final text.'
           '<br><br>'
           '<span style="color:#ff9a9a">Then &ldquo;replay the interview with timestamps&rdquo; arrives '
           'and you have thrown away everything you need.</span> The final text cannot tell you what '
           'happened at 11:42.<br><br>'
           '<b>Invert it.</b> The document is not the thing you store. The <b>ordered event log</b> is '
           'the thing you store, and the document is just the log folded up.<br><br>'
           '&bull; Current state = replay the log to now<br>'
           '&bull; Replay = replay the log more slowly<br>'
           '&bull; <span style="color:#a8e6a3">They are the same operation with a different '
           'speed.</span><br><br>'
           '<b>And one constraint makes this far easier than Google Docs:</b> the interviewer cannot '
           'edit. <span style="color:#a8e6a3">One writer per surface means no concurrent edits, which '
           'means no OT and no CRDT.</span> Say that out loud &mdash; it is a large simplification you '
           'were handed.<br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: when a requirement asks for history, '
           'store events and derive state. Storing state and bolting on history never works.</span>'
           '</div>',
           """Why is this interesting? Because replay is not a feature you add at the end &mdash; it is """
           """the storage model, and if you get that wrong at minute five you cannot recover at minute """
           """forty.""", step=0)
seg(sid, 1, """The obvious design is to hold the document in memory, broadcast changes to the other """
            """participant, and save the final text when the session ends. Then the replay requirement """
            """arrives and you have thrown away exactly the information you need. The final text cannot """
            """tell you what happened at eleven forty-two.""")
seg(sid, 2, """So invert it. The document is not the thing you store. The ordered event log is the thing """
            """you store, and the document is just that log folded up.""")
seg(sid, 3, """Current state is the log replayed up to now. Replay is the log replayed more slowly. They """
            """are literally the same operation at a different speed, and once you see that, the """
            """requirement stops being extra work and becomes free.""")
seg(sid, 4, """And there is a second constraint that makes this much easier than Google Docs: the """
            """interviewer cannot edit. One writer per surface means there are no concurrent edits, """
            """which means no operational transformation and no C-R-D-T. That is an enormous """
            """simplification and you were handed it in the question &mdash; say so out loud, because """
            """a lot of candidates will spend fifteen minutes on conflict resolution that the """
            """requirements already removed.""")
seg(sid, 5, """The staff-level insight generalises well beyond this: when a requirement asks for """
            """history, store events and derive state. Storing state and bolting history on afterwards """
            """never works, and you will meet that pattern again in the logistics lesson.""")

think('The interview is over. The interviewer wants to scrub to 11:42 and watch what the candidate typed '
      'next. What exactly did you have to store during the session for that to be possible &mdash; and '
      'how is that different from storing the code?',
      25,
      """Pause. The interview is over, and the interviewer wants to scrub to eleven forty-two and watch """
      """what the candidate typed next. What exactly did you have to store during the session for that """
      """to be possible? And how is that different from storing the code? Say it out loud.""",
      """Hold that. If your answer was &ldquo;every keystroke, with a timestamp and a sequence """
      """number&rdquo;, you have the design.""")

clarify('What I would clarify first', [
 ('Replay &mdash; exact reconstruction, or just a video?',
  '<b>The single most valuable question here.</b> A screen recording is a completely different and far '
  'simpler system. Exact reconstruction means an event log and a deterministic player.'),
 ('Can the interviewer really never edit &mdash; not even to paste a prompt?',
  'If they can edit <i>anything</i>, you have concurrent writers and need conflict resolution. '
  '<b>Confirm it, because it changes the hardest part of the design.</b>'),
 ('How many participants &mdash; two, or can observers join?',
  'Two is a channel. Twenty observers is a broadcast problem, and the fanout per keystroke matters.'),
 ('Does code execution happen here too?',
  'Running untrusted code is a <b>whole separate system</b> &mdash; sandboxing, resource limits, '
  'timeouts. If it is in scope, say it is a separate service.'),
 ('How long must sessions be retained?',
  'Hiring records often have a legal retention period. That decides storage format and cost, and '
  'whether replay must work in two years.'),
 ('What happens if someone disconnects mid-interview?',
  'The most likely real failure. <b>Reconnect must restore exact state</b>, not approximately &mdash; '
  'and that is another thing the event log gives you free.'),
], [
 """Replay &mdash; exact reconstruction, or just a video? I would ask this first and I would push on """
 """it, because it is the single most valuable question in this problem. A screen recording is a """
 """completely different and far simpler system: you record pixels, you store a file, you are done. """
 """Exact reconstruction means an event log and a deterministic player.""",
 """Can the interviewer really never edit &mdash; not even to paste in a prompt? If they can edit """
 """anything at all, you have concurrent writers and you need conflict resolution. Confirm it """
 """explicitly, because it changes the single hardest part of the design.""",
 """How many participants &mdash; two, or can observers join? Two is a channel. Twenty observers is a """
 """broadcast problem and the fanout per keystroke starts to matter.""",
 """Does code execution happen here? Running untrusted code is an entire separate system &mdash; """
 """sandboxing, resource limits, timeouts, isolation. If it is in scope I would scope it as a separate """
 """service rather than let it swallow the session design.""",
 """How long must sessions be retained? Hiring records often carry a legal retention period, which """
 """decides your storage format and cost, and whether replay has to still work in two years' time.""",
 """And what happens if someone disconnects mid-interview? That is the most likely real failure in this """
 """system. Reconnect has to restore exact state rather than approximate state &mdash; and that is """
 """another thing the event log gives you for free.""",
])

capacity('Capacity &mdash; and the number that reframes the problem', [
 ('Concurrent interviews', 'say 2,000 at peak', '2,000 sessions',
  'Small. <b>This is not a scale problem</b> &mdash; say so early'),
 ('Keystrokes: ~5 / s while typing, ~30% of the time', '2,000 &times; 5 &times; 0.3',
  '&asymp; 3,000 events / s', 'Trivial throughput. The challenge is <b>latency and routing</b>'),
 ('Event size ~60 B (op, position, char, ts, seq)', '3,000 &times; 60 B', '&asymp; 180 KB / s',
  'Nothing. <b>The whole system moves less data than one video stream</b>'),
 ('One 60-minute interview', '60 min &times; 5 ev/s &times; 0.3 &times; 60 B', '&asymp; 3 MB / session',
  'Including drawing. <b>An entire interview fits in a few megabytes</b>'),
 ('50,000 interviews / year', '50,000 &times; 3 MB', '&asymp; 150 GB / year',
  '<b>You can keep every interview forever</b> for the price of a laptop SSD'),
 ('Latency budget for a keystroke', 'typed &rarr; seen by the interviewer', '<b>&lt; 100 ms</b>',
  'One network hop, no queue, no database on the path. <b>This is the real constraint</b>'),
], [
 """Numbers, and in this question they reframe the problem entirely. Say two thousand concurrent """
 """interviews at peak. That is small, and I would say so early &mdash; this is not a scale """
 """problem.""",
 """Keystrokes at about five a second while someone is actually typing, which is maybe thirty percent """
 """of the time, gives roughly three thousand events a second across the whole platform. Trivial """
 """throughput. The challenge here is latency and routing, not volume.""",
 """Each event is around sixty bytes &mdash; an operation, a position, a character, a timestamp and a """
 """sequence number &mdash; so a hundred and eighty kilobytes a second in total. The entire system """
 """moves less data than a single video stream.""",
 """One sixty-minute interview is about three megabytes including the drawing events. An entire """
 """interview fits in a few megabytes, which is a lovely fact and it is worth saying out loud because """
 """of what it implies.""",
 """Fifty thousand interviews a year is about a hundred and fifty gigabytes. You can keep every """
 """interview your company has ever conducted, forever, for the price of a laptop S-S-D. That means """
 """retention is a policy question, not an engineering one &mdash; and that is a genuinely useful """
 """conclusion to hand the interviewer.""",
 """And the one constraint that actually binds: a keystroke must reach the interviewer in under a """
 """hundred milliseconds. One network hop, no queue, no database on the path. Everything in the design """
 """follows from protecting that number.""",
])

A = Arch('CoderPad &mdash; one writer, ordered log, two readers', kicker='Architecture', height=800)

A.box('cand',  60, 180, 160, 95, 'Candidate', 'writes code', kind='ok', step=0, focus=[0, 1], small=True)
A.box('intv',  60, 450, 160, 95, 'Interviewer', 'read-only code', kind='neutral', step=0, focus=[0, 3], small=True)

A.box('lb',   270, 310, 175, 105, 'LB (sticky)', 'by sessionId', kind='info', step=1, focus=1)
A.arrow('cand', 'lb', step=1, label='WebSocket', focus=1)
A.arrow('intv', 'lb', step=1, focus=1)

A.box('sess', 520, 290, 230, 145, 'Session server', 'owns ONE session:<br>state + seq counter',
      kind='ok', step=2, focus=[2, 3])
A.arrow('lb', 'sess', step=2, focus=2)

A.box('log',  830, 170, 220, 110, 'Event log', 'append-only<br>seq ordered', kind='ok', step=4,
      focus=[4, 6])
A.arrow('sess', 'log', step=4, label='append', focus=4)

A.box('snap', 830, 330, 220, 105, 'Snapshots', 'every 1,000 events', kind='shared', step=5, focus=5, small=True)
A.arrow('log', 'snap', step=5, focus=5, dashed=True)

A.box('store',1130, 250, 210, 110, 'Durable store', 'session archive', kind='dp', step=5, focus=5, small=True)
A.arrow('log', 'store', step=5, focus=5)
A.arrow('snap', 'store', step=5, focus=5, dashed=True)

A.box('play', 1130, 450, 210, 110, 'Replay player', 'seek + play', kind='info', step=6, focus=6, small=True)
A.arrow('store', 'play', step=6, focus=6)

A.box('inv',  520, 560, 230, 105, 'Invite service', 'link + email', kind='neutral', step=7, focus=7, small=True)
A.arrow('inv', 'sess', step=7, focus=7, dashed=True)

A.note(830, 560, 'Same log serves three things: live sync, reconnect, and replay. One structure, three requirements.',
       step=6, kind='info', w=460)

A.narrate(0, """Two participants. The candidate writes code; the interviewer watches. The drawing pad is """
             """the one surface both can write to, and I will come back to that.""")
A.narrate(1, """Both connect over web sockets through a load balancer that is sticky on session I-D. """
             """Sticky routing matters enormously here: both participants in one interview must land on """
             """the same server, or they are not in the same room.""",
          A.flow([(220, 227), (270, 340)]))
A.narrate(2, """A session server owns exactly one session. It holds the current document state in memory """
             """and, critically, a monotonic sequence counter. Because one server owns the session, that """
             """counter is trivially correct &mdash; no distributed consensus, no clock """
             """synchronisation. A single owner is what buys you ordering for free.""",
          A.flow([(445, 345), (520, 360)]))
A.narrate(3, """A keystroke arrives, gets the next sequence number, is applied to in-memory state and is """
             """broadcast to the other participant immediately. That path has no database on it, which """
             """is how you hold a hundred milliseconds.""")
A.narrate(4, """And asynchronously, the event is appended to an ordered log. Note the ordering: """
             """broadcast first, persist after. The interviewer sees the keystroke before it is """
             """durable, which is the right trade for a live collaboration tool &mdash; but it is a """
             """trade, and I would name it.""",
          A.flow([(750, 340), (830, 225)]))
A.narrate(5, """Periodically we write a snapshot &mdash; the full document every thousand events &mdash; """
             """and both log and snapshots go to durable storage. Snapshots are purely a replay """
             """optimisation: without them, seeking to minute fifty means replaying fifty minutes of """
             """events.""",
          A.flow([(1050, 225), (1130, 305)]))
A.narrate(6, """Then the replay player reads from the archive: load the nearest snapshot before the """
             """target time, then apply events forward. And here is what I would emphasise &mdash; the """
             """same log serves live sync, reconnection, and replay. One structure, three """
             """requirements.""",
          A.flow([(1235, 360), (1235, 450)]))
A.narrate(7, """And an invite service generating the unique link and sending email. Small, but it is in """
             """the requirements, and it carries the access control for the whole session.""")
A.build()

sid = beat('Deep dive 1', 'Why there is no OT or CRDT here &mdash; and where one is still needed',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Google Docs is hard because two people edit the same text concurrently.</b> Two '
           'insertions at the same position must converge to the same result on every client. That is '
           'what OT and CRDTs are for, and they are genuinely difficult.<br><br>'
           '<b>CoderPad gave us a constraint that removes it:</b> the interviewer cannot edit the code. '
           '<span style="color:#a8e6a3">One writer, one surface &rarr; no concurrent edits &rarr; '
           'sequence numbers are enough.</span><br><br>'
           'The session server assigns a monotonic sequence number. Clients apply in sequence order. '
           'That is the entire concurrency story for the editor.<br><br>'
           '<b>But the drawing pad is different.</b> Both participants draw. So:<br>'
           '&bull; Drawing ops are mostly <b>commutative</b> &mdash; two strokes in either order give '
           'the same canvas. <span style="color:#a8e6a3">No transformation needed.</span><br>'
           '&bull; The exceptions are <i>erase</i> and <i>clear</i>, which are order-dependent<br>'
           '&bull; Simplest correct answer: <b>server-assigned sequence on the drawing channel too</b>, '
           'last-writer-wins per stroke<br><br>'
           '<span style="color:#ffd483">Say what you are NOT building and why. Declining OT with a '
           'reason is stronger than implementing it unnecessarily.</span></div>',
           """Deep dive one: why there is no operational transformation or C-R-D-T here, which is the """
           """thing most candidates reach for and do not need.""", step=0)
seg(sid, 1, """Google Docs is hard because two people edit the same text concurrently. Two insertions at """
            """the same position have to converge to the same result on every client, including when """
            """messages arrive out of order. That is what O-T and C-R-D-Ts solve, and they are """
            """genuinely difficult to get right.""")
seg(sid, 2, """CoderPad handed us a constraint that removes the whole problem: the interviewer cannot """
            """edit the code. One writer on one surface means no concurrent edits, which means sequence """
            """numbers are sufficient.""")
seg(sid, 3, """The session server assigns a monotonic sequence number, clients apply operations in """
            """sequence order, and that is the entire concurrency story for the editor. Four """
            """lines.""")
seg(sid, 4, """But the drawing pad is genuinely different, because both participants draw on it. The """
            """good news is that drawing operations are mostly commutative &mdash; two strokes applied """
            """in either order give the same canvas, so no transformation is needed. The exceptions are """
            """erase and clear, which are order-dependent.""")
seg(sid, 5, """So the simplest correct answer is a server-assigned sequence on the drawing channel too, """
            """with last-writer-wins per stroke. And the broader point: say what you are not building """
            """and why. Declining O-T with a reason is a much stronger answer than implementing it """
            """because it is the impressive thing to mention.""")

sid = beat('Deep dive 2', 'Replay, reconnect, and the snapshot that makes seeking fast',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>The event log gives you three things for one piece of work:</b><br><br>'
           '<b>1. Live sync</b> &mdash; broadcast each event as it is sequenced.<br><br>'
           '<b>2. Reconnect</b> &mdash; the client remembers the last sequence number it saw and asks '
           'for everything after it. <span style="color:#a8e6a3">No special code: reconnection is just '
           'replay at full speed.</span> This is the most likely real failure and it costs you '
           'nothing.<br><br>'
           '<b>3. Replay</b> &mdash; the same stream, played with the original inter-event delays.<br><br>'
           '<b>Why snapshots:</b> seeking to minute 50 without them means replaying 50 minutes of '
           'events. With a snapshot every ~1,000 events, seeking is <b>load nearest snapshot, then '
           'apply at most 1,000 events</b> &mdash; effectively instant.<br><br>'
           '<b>Determinism is the requirement people miss.</b> Replay must produce exactly what '
           'happened. So:<br>'
           '&bull; Store the <b>operation</b>, not the resulting text<br>'
           '&bull; Store <b>server</b> timestamps, never client ones &mdash; client clocks are wrong '
           'and will reorder your replay<br>'
           '&bull; Version the event format, because you will keep these for years<br><br>'
           '<span style="color:#ffd483">The same insight as the KV store in 6.1: the log is truth, '
           'everything else is derived.</span></div>',
           """Deep dive two: replay, reconnect and snapshots. The event log gives you three things for """
           """one piece of work, which is why it is worth building properly.""", step=0)
seg(sid, 1, """One: live sync. Broadcast each event as it is sequenced. That is the thing you were """
            """building anyway.""")
seg(sid, 2, """Two: reconnect. The client remembers the last sequence number it saw and asks for """
            """everything after it. There is no special reconnection code &mdash; reconnection is """
            """simply replay at full speed. Given that a dropped connection is the most likely real """
            """failure in an hour-long interview, getting it for free is a significant win.""")
seg(sid, 3, """Three: replay, which is the same stream played back with the original inter-event delays """
            """so it looks like watching someone type.""")
seg(sid, 4, """Snapshots exist purely to make seeking fast. Without them, jumping to minute fifty means """
            """replaying fifty minutes of events. With a snapshot every thousand events, seeking is """
            """load the nearest snapshot and then apply at most a thousand events &mdash; effectively """
            """instant.""")
seg(sid, 5, """And the requirement people miss is determinism. Replay must produce exactly what happened, """
            """so store the operation rather than the resulting text, store server timestamps and never """
            """client ones &mdash; client clocks are wrong and will reorder your replay in confusing """
            """ways &mdash; and version the event format, because you are keeping these for years and """
            """your schema will change.""")
seg(sid, 6, """This is the same insight as the key-value store in lesson six point one: the log is """
            """truth, everything else is derived. Two completely different systems, same structural """
            """idea, and recognising that is worth more than either design on its own.""")

tradeoff('How replay is implemented', [
 ('Screen recording (video)', 'info',
  ['Trivially faithful &mdash; it is literally what was on screen', 'No determinism concerns',
   'Works regardless of client version'],
  ['<b>~1 GB/hour vs ~3 MB</b>', 'Cannot search, diff, or extract the code',
   'Cannot seek precisely to an event', 'Needs a capture pipeline on every client']),
 ('Event log + deterministic player', 'ok',
  ['<b>~3 MB per interview</b>', 'Searchable, diffable, and the code is extractable',
   'Reconnect and replay are the same mechanism', 'Seek anywhere with snapshots'],
  ['Replay must stay deterministic as the client evolves', 'Event format must be versioned forever',
   'Replaying a 2-year-old session needs an old player']),
 ('Periodic full-document snapshots only', 'shared',
  ['Simplest possible', 'No event machinery at all'],
  ['<b>Loses what happened between snapshots</b>',
   'Cannot show typing &mdash; the thing interviewers actually want to see',
   'Fails the stated requirement']),
], 'Event log plus deterministic player, with periodic snapshots for fast seeking.',
 'If the requirement were only &ldquo;show me roughly what happened&rdquo; rather than exact '
 'reconstruction, I would take the video &mdash; it is far simpler and the storage cost is affordable. '
 '<b>That is exactly why I asked which one up front.</b>',
 [
 """Trade-off: how is replay implemented? A screen recording is trivially faithful, has no determinism """
 """concerns, and works regardless of client version. It costs roughly a gigabyte an hour against three """
 """megabytes, you cannot search or diff it or extract the code, you cannot seek precisely to an event, """
 """and you need a capture pipeline running on every client.""",
 """An event log with a deterministic player is three megabytes per interview, searchable, diffable, """
 """the code is extractable, and reconnect and replay become the same mechanism. The costs are real: """
 """replay has to stay deterministic as the client evolves, the event format must be versioned forever, """
 """and replaying a two-year-old session may need an old player.""",
 """Periodic full-document snapshots alone is the simplest option and it fails the requirement, because """
 """it loses what happened between snapshots and cannot show typing &mdash; which is the thing """
 """interviewers actually want to watch.""",
 """I would take the event log with a deterministic player and periodic snapshots for seeking.""",
 """And what would flip it: if the requirement were only &ldquo;show me roughly what happened&rdquo; """
 """rather than exact reconstruction, I would take the video. It is far simpler and the storage cost is """
 """affordable at this volume. Which is exactly why I asked which one they meant in the first five """
 """minutes &mdash; that one question can halve the system.""",
])

failures('What happens when each piece dies', [
 ('Session server crashes mid-interview', '<b>Both participants disconnect</b> &mdash; the worst '
                                          'failure in this system',
  'Reconnect to a new server, rebuild state from the log (snapshot + tail). <b>Recovery time is '
  'bounded by snapshot frequency</b> &mdash; which is why snapshots are a reliability feature, not '
  'just a replay one'),
 ('A participant&rsquo;s connection drops', 'They briefly see a frozen screen',
  'Client holds its last sequence number and requests everything after it. <b>Reconnection is replay '
  '&mdash; no special path</b>'),
 ('Events broadcast but not yet persisted', 'Crash loses the last few keystrokes',
  'Deliberate: broadcast first, persist after, to protect the 100 ms budget. <b>Name the trade.</b> '
  'Persist in small batches to bound the loss'),
 ('Sticky routing breaks &mdash; participants hit different servers', 'They see different documents',
  '<b>The scariest failure, because it looks like it works.</b> Session ownership must be explicit: a '
  'server claims a session with a lease, others redirect'),
 ('Replay is requested for a 2-year-old session', 'Player cannot interpret old events',
  '<b>Version every event.</b> Keep old interpreters, or migrate archived logs forward on format '
  'change'),
 ('Candidate pastes 10,000 lines at once', 'One enormous event; UI stalls',
  'Cap event size and split large pastes into chunks. Rate-limit per session &mdash; <b>a shared '
  'session server is a shared resource</b>'),
], [
 """Failures. Session server crashes mid-interview and both participants disconnect &mdash; the worst """
 """failure in this system, because it happens to a live human conversation. They reconnect to a new """
 """server which rebuilds state from the log: nearest snapshot plus the tail. And notice that recovery """
 """time is bounded by snapshot frequency, which means snapshots are a reliability feature and not just """
 """a replay optimisation. One mechanism, two jobs.""",
 """A participant's connection drops and they see a frozen screen briefly. The client holds its last """
 """sequence number and asks for everything after it. Reconnection is replay, so there is no special """
 """code path to get wrong.""",
 """Events broadcast but not yet persisted means a crash loses the last few keystrokes. That is """
 """deliberate &mdash; we broadcast first and persist after, to protect the hundred millisecond budget. """
 """I would name that trade explicitly and bound it by persisting in small batches.""",
 """Sticky routing breaking so that participants land on different servers is the scariest failure """
 """here, because it looks like it is working. Both people see a functioning editor showing different """
 """documents. So session ownership must be explicit: a server claims a session with a lease and other """
 """servers redirect rather than silently serving.""",
 """Replay requested for a two-year-old session where the player cannot interpret old events. Version """
 """every event, and either keep old interpreters or migrate archived logs forward when the format """
 """changes.""",
 """And a candidate pasting ten thousand lines at once produces one enormous event and stalls the U-I. """
 """Cap event size, split large pastes into chunks, and rate limit per session &mdash; because a shared """
 """session server is a shared resource and one participant should not be able to degrade it.""",
])

say('What I should actually say in the room', [
 'My first question is whether replay means exact reconstruction or just a video, because those are '
 'completely different systems and one of them is much simpler.',
 'Assuming exact reconstruction: replay is not a feature I add at the end, it is the storage model. I '
 'store an ordered event log and derive the document from it, rather than storing the document.',
 'Current state is the log replayed to now; replay is the log replayed more slowly. They are the same '
 'operation at different speeds.',
 'The second thing I want to confirm is that the interviewer genuinely cannot edit. One writer per '
 'surface means no concurrent edits, so I need neither OT nor a CRDT &mdash; just server-assigned '
 'sequence numbers. That is a large simplification handed to me by the requirements.',
 'The scale is small &mdash; around 3,000 events a second across the platform, and an entire interview '
 'is about 3 MB. The binding constraint is latency: under 100 ms from keystroke to the interviewer '
 'seeing it, so there is no database on that path.',
 'A session server owns exactly one session, which makes the sequence counter trivially correct, and '
 'the load balancer is sticky on session ID so both participants land on the same server.',
 'Snapshots every thousand events make seeking fast &mdash; and they double as the recovery mechanism '
 'if a session server crashes.',
], [
 """The sentences. The first one is the highest-value question in the whole problem and it takes five """
 """seconds to ask.""",
 """Then the inversion &mdash; log as the storage model, document as derived &mdash; and the """
 """observation that state and replay are the same operation. Then confirm the one-writer constraint """
 """and explicitly decline O-T.""",
 """Then the numbers that establish this is a latency problem rather than a scale one, the single-owner """
 """session server, and snapshots doing double duty. Seven sentences and you have covered every stated """
 """requirement.""",
])

followups([
 'How does real-time synchronisation work?',
 'How do you store the event log?',
 'How do you scale WebSockets?',
 'How do you handle conflicts and ordering?',
 'How does replay work with timestamps?',
 'How do invitations work?',
 'What if a participant disconnects?',
], [
 'Now the interviewer <i>can</i> edit. What changes?',
 'Add 50 silent observers to the session. What breaks?',
 'The candidate runs code. How do you execute untrusted code safely?',
 'How would you prove the replay is faithful &mdash; that it shows what really happened?',
 'Two interviewers in different regions, high latency between them. Now what?',
],
 """The reported follow-ups are the lesson. On scaling web sockets: each connection is cheap but """
 """stateful, so you size by concurrent connections rather than requests per second, and the routing """
 """&mdash; sticky by session I-D &mdash; matters far more than the connection count. Invitations are a """
 """signed token in a U-R-L carrying the session I-D and a role, plus an email send; the role is what """
 """enforces that the interviewer cannot write to the code channel.""",
 """The staff-level follow-ups attack the simplifying assumptions. If the interviewer can edit, you """
 """have concurrent writers and now you genuinely do need O-T or a C-R-D-T &mdash; and I would reach """
 """for a C-R-D-T, because it needs no central transformation server and this system already has one """
 """owner per session. Fifty observers makes it a broadcast problem, so you fan out from the session """
 """server rather than having every observer in the write path. Running untrusted code is a separate """
 """sandboxed service with hard C-P-U and memory limits and no network. Proving replay is faithful """
 """means checksumming the derived document against a snapshot at known points &mdash; a lovely """
 """question, because it is really asking whether you trust your own determinism. And two interviewers """
 """in different regions means someone is far from the session owner, so you either accept asymmetric """
 """latency or move to regional servers with a replicated log, which reintroduces ordering """
 """problems.""")

cheatsheet('CoderPad &mdash; the one-page card', [
 ('Requirements', 'Real-time code view (interviewer read-only), shared drawing, invite by link/email, '
                  '<b>timestamped replay</b>'),
 ('Scale', '~2,000 concurrent sessions, ~3,000 events/s, ~3 MB per interview, ~150 GB/year. '
           '<b>&lt;100 ms keystroke latency</b>'),
 ('Core architecture', 'Sticky LB by sessionId &rarr; session server owning one session (state + seq) '
                       '&rarr; broadcast, then append to the event log &rarr; snapshots &rarr; archive'),
 ('Data store', '<b>Append-only event log is the source of truth</b>; document state is derived; '
                'snapshots every ~1,000 events'),
 ('Partition key', '<code>sessionId</code> &mdash; one session, one owner, which makes the sequence '
                   'counter correct with no coordination'),
 ('Cache', 'In-memory document state on the session server. That <i>is</i> the working copy'),
 ('Queue', 'None on the live path. Persistence is an async append behind the broadcast'),
 ('Consistency', 'Total order per session via server-assigned sequence. <b>No OT/CRDT needed, because '
                 'there is one writer per surface</b>'),
 ('Failure handling', 'Rebuild from snapshot + log tail; reconnect = replay from last seq; explicit '
                      'session leases so routing cannot silently split'),
 ('Key deep dives', 'Why no OT &middot; the log serving sync, reconnect and replay'),
 ('Biggest trade-off', 'Event log vs video &mdash; 3 MB and searchable against 1 GB and faithful. '
                       '<b>Decided by whether replay must be exact</b>'),
], [
 """The card. Requirements with replay in bold, because it drives the design. Scale &mdash; and the """
 """number that matters is the hundred millisecond latency, not any of the volumes.""",
 """Architecture in one line, and note the order: broadcast, then append. The data store row carries """
 """the central inversion &mdash; the log is truth and the document is derived.""",
 """Partition by session I-D so one session has one owner, which is what makes the sequence counter """
 """correct without any coordination. Consistency is a total order per session with no O-T needed. And """
 """the biggest trade-off is event log versus video, decided entirely by whether replay must be """
 """exact.""",
])

say('The 60-second answer', [
 'First I would ask whether replay means exact reconstruction or just a video, because a screen '
 'recording is a far simpler system and the answer changes everything.',
 'Assuming exact: replay is not a feature to add at the end, it is the storage model. I store an '
 'ordered event log and derive the document from it &mdash; current state is the log replayed to now, '
 'and replay is the same log played more slowly.',
 'I would also confirm the interviewer truly cannot edit the code, because one writer per surface means '
 'no concurrent edits, and therefore no operational transformation and no CRDT &mdash; just '
 'server-assigned sequence numbers. That is a large simplification the requirements handed me.',
 'The scale is small: a few thousand events a second platform-wide, and an entire interview is about '
 '3 MB, so you could keep every interview forever. The binding constraint is latency &mdash; under '
 '100 ms from keystroke to the interviewer seeing it &mdash; so nothing slow goes on that path.',
 'So: a load balancer sticky on session ID, a session server that owns exactly one session and holds '
 'both the document and a monotonic sequence counter, broadcasting immediately and appending to the log '
 'asynchronously.',
 'Snapshots every thousand events make seeking fast, and they double as the recovery path &mdash; if a '
 'session server dies, the participants reconnect and state is rebuilt from the nearest snapshot plus '
 'the log tail.',
], [
 """The sixty-second answer. The opening question is the one that most differentiates you, because """
 """almost nobody asks it and it genuinely changes which system you build.""",
 """The second and third sentences are the technical heart &mdash; the inversion, and declining O-T """
 """with a reason. Practise saying &ldquo;so I need neither O-T nor a C-R-D-T&rdquo; confidently; """
 """refusing complexity you were not required to build is a staff-level move, not a gap.""",
], kicker='60-second interview answer')
