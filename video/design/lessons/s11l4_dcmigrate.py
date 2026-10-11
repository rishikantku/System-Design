# -*- coding: utf-8 -*-
"""Chapter 11, Lesson 4 — migrating live data from one data centre to another."""
from lib import *

lesson_header('11.4', 'Migrate live data from one data centre to another',
              'Snapshot + change replay &middot; verify &middot; shadow reads &middot; fenced cut-over &middot; rollback',
              dict(reports='1 candidate report (hiring-manager round)', latest='~late 2025',
                   level='Senior SWE, Systems &amp; Infrastructure',
                   conf='MEDIUM &mdash; single report, very Infra-shaped', sources='LeetCode Discuss'), 17,
              """Lesson four, and an unusual one: this was asked in the hiring manager round, not the """
              """design round. How would you migrate data from one data centre to another, under some """
              """conditions? For a systems and infrastructure loop it is a gift &mdash; if you know the """
              """shape. Every safe migration is the same five moves, and the interviewer is listening for """
              """whether you can get the data across without ever betting the business on one moment.""")

evidence('Where this question comes from', [
 ('LeetCode Discuss &mdash; LinkedIn Senior SWE, Systems &amp; Infra, USA', '~late 2025',
  'Senior SWE, Sys/Infra',
  'Design round: metrics aggregator and monitoring. <b>Host manager round</b> included a design question: '
  '<b>migrate data from one data centre to another, with certain conditions</b>'),
], """One report, and the conditions were not spelled out, so the clarify step carries more weight than """
   """usual. Treat this as a question where you set the conditions by asking.""",
 ["""It is also a natural hiring-manager question for an infrastructure team: it tests judgement about risk """
  """and reversibility as much as technology, and it invites you to tell a migration story of your own."""],
 caveat='Single report; the exact conditions were not given. Date approximate, from the post number.',
 narration_caveat="""Single report, the conditions were not given, and the date is approximate.""")

sid = beat('Why this is interesting', 'The danger is not copying. It is the moment you switch.',
           '<div style="font-size:28px;line-height:1.72">'
           '<b>Copying bytes</b> is solved: snapshots, bulk transfer, checksums.<br><br>'
           '<b>The hard parts:</b><br>'
           '&bull; the data <b>keeps changing</b> while you copy it<br>'
           '&bull; you must <b>prove</b> the copy is right before trusting it<br>'
           '&bull; the switch must never allow <span style="color:#ff9a9a">two writers</span> '
           '&mdash; split-brain corrupts both sides<br>'
           '&bull; you need a way <b>back</b> after you switch<br><br>'
           '<span style="color:#a8e6a3"><b>The five moves:</b> snapshot &rarr; replay changes &rarr; verify '
           '&rarr; shift reads &rarr; fenced write cut-over (with reverse replication for rollback).</span>'
           '<br><br><b>Every step is reversible except the last &mdash; and you make the last one reversible '
           'too.</b></div>',
           """Why is this interesting? Because the danger is not copying. It is the moment you switch.""", step=0)
seg(sid, 1, """Copying bytes is a solved problem: snapshots, bulk transfer, checksums.""")
seg(sid, 2, """The hard parts are that the data keeps changing while you copy it, that you must prove the copy """
            """is correct before you trust it, that the switch must never allow two writers &mdash; split brain """
            """corrupts both sides &mdash; and that you need a way back after you switch.""")
seg(sid, 3, """So every safe migration is five moves: snapshot, replay changes, verify, shift reads, and a """
            """fenced write cut-over with reverse replication for rollback.""")
seg(sid, 4, """Every step is reversible except the last, and the design's job is to make the last one """
            """reversible too.""")

think('You have 500 TB in data centre A and a 10 Gbps link to data centre B. Can you just stop writes and copy '
      'it? How long would the site be read-only?',
      20,
      """Pause. Five hundred terabytes in data centre A, a ten gigabit link to B. Can you just stop writes and """
      """copy it? Work out roughly how long the site would be read-only.""",
      """Hold that number. It is the first row of the capacity slide, and it decides the design.""")

clarify('What I would clarify first — these are the “conditions”', [
 ('Downtime allowed &mdash; zero, minutes, hours?',
  'Zero downtime forces <b>live replication and a fenced cut-over</b>. Hours lets you freeze and copy.'),
 ('How much data, how fast does it change, and how big is the link?',
  'Size &divide; bandwidth tells you if a freeze is even possible. Change rate tells you if replay can '
  '<b>catch up</b>.'),
 ('What is the store &mdash; one database, many, files, a KV store?',
  'Each has its own change log (binlog, WAL, CDC). <b>No change log = dual writes</b>, which are much riskier.'),
 ('Consistency requirements across tables or stores?',
  'Cross-store transactions mean you must cut over <b>together</b> or keep ordering across streams.'),
 ('Can traffic be split by tenant or key range?',
  'If yes, migrate <b>in slices</b> &mdash; small blast radius, practice runs. The single best lever.'),
 ('Rollback window &mdash; how long must A stay able to take over?',
  'Drives how long you run <b>reverse replication</b> and keep A warm.'),
], [
 """These are the &ldquo;certain conditions&rdquo; in the report, so I would ask for them explicitly. Downtime """
 """allowed: zero, minutes or hours? Zero forces live replication and a fenced cut-over. Hours lets you freeze """
 """and copy.""",
 """How much data, how fast it changes, and how big the link is. Size over bandwidth tells you whether a freeze """
 """is even possible. Change rate tells you whether replay can ever catch up.""",
 """What kind of store? Each has its own change log &mdash; a binlog, a write-ahead log, a C-D-C feed. If there """
 """is no change log, you are forced into dual writes, which are much riskier, and you should say so.""",
 """Consistency across tables or stores? Cross-store transactions mean cutting over together, or preserving """
 """ordering across streams.""",
 """Can traffic be split by tenant or key range? If yes, migrate in slices &mdash; small blast radius and """
 """practice runs. That is the single best lever you have.""",
 """And the rollback window: how long must A stay able to take back over? That drives how long you run """
 """reverse replication.""",
])

capacity('Capacity', [
 ('Full copy over the link', '500 TB &times; 8 &divide; 10 Gbps', '&asymp; 400,000 s &asymp; <b>4.6 days</b>',
  'At ~50% usable bandwidth, <b>~9 days</b>. <b>A freeze-and-copy is impossible</b>'),
 ('Change rate during the copy', 'assume 20 MB/s of writes', '&asymp; 1.7 TB / day',
  'Over 9 days &asymp; 15 TB of changes to replay'),
 ('Replay catch-up', 'link spare ~600 MB/s vs 20 MB/s incoming', 'catch-up in hours',
  'Replay is <b>30&times; faster than change</b> &mdash; it converges. If it were not, slice the migration'),
 ('Verification', 'checksum per key range, ~1M ranges', 'parallel, ~hours',
  'Range checksums find <b>where</b> they differ, not just <i>that</i> they differ'),
 ('Cut-over write pause', 'drain replication lag to zero', '<b>seconds</b>',
  'The only downtime &mdash; and only for writes'),
], [
 """Numbers, and the answer to the pause. Five hundred terabytes over ten gigabits is about four hundred """
 """thousand seconds &mdash; four and a half days at full line rate, more like nine at a realistic half. A """
 """freeze-and-copy is impossible. That one calculation decides the design.""",
 """At twenty megabytes a second of writes, that is about one point seven terabytes of changes a day, so """
 """roughly fifteen terabytes accumulate during the copy.""",
 """Replay has about six hundred megabytes a second of spare bandwidth against twenty incoming &mdash; thirty """
 """times faster than the change rate &mdash; so it catches up in hours and converges. If replay were not """
 """faster than change, you would never catch up, and you would have to slice the migration.""",
 """Verification by checksum per key range runs in parallel in hours, and range checksums tell you where the """
 """copies differ, not just that they differ.""",
 """And the cut-over pause is draining replication lag to zero &mdash; seconds, and only for writes.""",
])

A = Arch('Live migration — copy, catch up, verify, switch', kicker='Architecture', height=800)

A.zone(60, 120, 520, 600, 'DATA CENTRE A — current')
A.zone(1220, 120, 560, 600, 'DATA CENTRE B — target')

A.box('app',   100, 160, 420, 90, 'Application', 'reads and writes', kind='info', step=0, focus=[0, 4, 5])
A.box('dba',   100, 330, 220, 120, 'Store A', 'source of truth', kind='dp', step=0, focus=0)
A.arrow('app', 'dba', step=0, focus=0, fs='b', ts='t')
A.box('log',   340, 330, 200, 120, 'Change log', 'binlog / WAL / CDC', kind='shared', step=1, focus=[1, 2])
A.arrow('dba', 'log', step=1, focus=1)

A.box('snap',  680, 180, 440, 100, '1. Snapshot', 'consistent, records log position P', kind='ok', step=1, focus=1)
A.box('rep',   680, 340, 440, 100, '2. Replay changes from P', 'idempotent, ordered per key', kind='ok', step=2, focus=2)
A.box('ver',   680, 500, 440, 100, '3. Verify', 'range checksums + shadow reads', kind='shared', step=3, focus=3)
A.arrow('dba', 'snap', step=1, focus=1, label='bulk copy')
A.arrow('log', 'rep', step=2, focus=2)

A.box('dbb',   1260, 330, 240, 120, 'Store B', 'replica, then primary', kind='dp', step=1, focus=[1, 2, 5])
A.arrow('snap', 'dbb', step=1, focus=1)
A.arrow('rep', 'dbb', step=2, focus=2)
A.arrow('ver', 'dbb', step=3, focus=3, dashed=True)

A.box('fence', 1260, 540, 480, 110, '5. Fenced cut-over', 'epoch++ , A read-only, drain, B primary', kind='bad', step=5, focus=5)
A.box('rev',   100, 560, 420, 110, 'Reverse replication B &rarr; A', 'the rollback path', kind='shared', step=6, focus=6)
A.arrow('dbb', 'rev', step=6, focus=6, dashed=True, label='keeps A warm')

A.note(1260, 170, '4. Shift reads to B gradually, per slice, comparing results.', step=4, kind='info', w=480)

A.narrate(0, """The application writes to store A, which is the source of truth today.""")
A.narrate(1, """Step one: take a consistent snapshot and record the change-log position at which it was taken """
             """&mdash; call it P. Bulk-copy the snapshot to store B. That takes days, and that is fine.""",
          A.flow([(320, 390), (680, 230), (1260, 390)]))
A.narrate(2, """Step two: replay every change from position P onwards into B. Apply them idempotently and in """
             """order per key, so replaying a change twice is harmless. Because replay is faster than the change """
             """rate, B converges to seconds behind A.""",
          A.flow([(540, 390), (680, 390), (1260, 390)]))
A.narrate(3, """Step three: verify. Checksum every key range on both sides to find exactly where they differ, and """
             """run shadow reads &mdash; send real reads to both, compare, serve A's answer.""")
A.narrate(4, """Step four: shift reads to B gradually, slice by slice, watching error rates and comparing """
             """results. Still fully reversible: you just point reads back.""")
A.narrate(5, """Step five, the dangerous one: the write cut-over. Bump an epoch, make A read-only, wait for """
             """replication lag to hit zero, then promote B. Any write still stamped with the old epoch is """
             """rejected, so there is never a moment with two writers. Writes pause for seconds.""")
A.narrate(6, """And before you cut over, start reverse replication from B back to A. That keeps A warm and """
             """current, so rollback is the same fenced switch in the other direction rather than a second """
             """migration.""",
          A.flow([(1380, 450), (520, 615)]))
A.build()

sid = beat('Deep dive 1', 'Snapshot plus replay &mdash; and why not dual writes',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Snapshot + change replay (preferred):</b><br>'
           '&bull; snapshot is <b>consistent at log position P</b> &mdash; that pairing is the whole trick<br>'
           '&bull; replay from P; apply changes <b>idempotently</b> (upsert by key, carry a version, ignore older)<br>'
           '&bull; ordering only matters <b>per key</b> &mdash; partition the replay by key, parallelise<br><br>'
           '<b>Dual writes from the application (avoid if you can):</b><br>'
           '&bull; write A then B &mdash; <span style="color:#ff9a9a">what if B fails? retry? out of order with '
           'another writer? the two drift silently</span><br>'
           '&bull; needs its own reconciliation job, which is a change-log replay anyway<br><br>'
           '<b>Schema or format change on the way?</b> Transform in the replay pipeline; verify against the '
           '<i>transformed</i> expectation.<br><br>'
           '<span style="color:#a8e6a3"><b>Rule:</b> one writer, one ordered log, many readers. Dual writes break '
           'the first rule.</span></div>',
           """Deep dive one: snapshot plus replay, and why not dual writes.""", step=0)
seg(sid, 1, """The snapshot must be consistent at a known log position, and that pairing &mdash; snapshot plus """
            """position &mdash; is the whole trick. Replay starts exactly there, so nothing is missed and nothing """
            """is applied twice in a way that matters.""")
seg(sid, 2, """Apply changes idempotently: upsert by key, carry a version, ignore anything older than what you """
            """have. And ordering only matters per key, so you can partition the replay by key and run it in """
            """parallel.""")
seg(sid, 3, """Dual writes from the application are the tempting alternative and I would avoid them. Write A, """
            """then B &mdash; what if B fails? Retry it? What if another writer interleaves? The two drift """
            """silently, and you end up building a reconciliation job that is really a change-log replay """
            """anyway.""")
seg(sid, 4, """If the schema or format changes on the way, transform inside the replay pipeline and verify """
            """against the transformed expectation.""")
seg(sid, 5, """The rule to say out loud: one writer, one ordered log, many readers. Dual writes break the first """
            """rule, which is why they cause most migration incidents.""")

sid = beat('Deep dive 2', 'The cut-over &mdash; fencing, slices and rollback',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Fenced write cut-over:</b><br>'
           '&bull; bump an <b>epoch</b> in the routing / config service<br>'
           '&bull; A becomes <b>read-only</b>; writes queue or fail fast for seconds<br>'
           '&bull; wait until replication lag = <b>0</b>, verify the last checksum<br>'
           '&bull; promote B; storage rejects writes carrying the old epoch &mdash; '
           '<span style="color:#a8e6a3">a stale writer cannot corrupt anything</span><br><br>'
           '<b>Migrate in slices</b> (by tenant or key range): a 1% slice first, then 10%, then the rest. '
           '<span style="color:#ffd483">Each slice is a rehearsal of the next.</span><br><br>'
           '<b>Rollback:</b> reverse replication B &rarr; A started <i>before</i> cut-over, so rollback is the same '
           'fenced switch backwards. <b>Define the rollback trigger in advance</b> &mdash; error rate, latency, '
           'checksum mismatch &mdash; so nobody debates it at 3 am.<br><br>'
           '<b>Decommission A only after</b> the rollback window passes and a final verification is clean.</div>',
           """Deep dive two: the cut-over, which is the only dangerous moment.""", step=0)
seg(sid, 1, """Bump an epoch in the routing or config service. Make A read-only, so writes queue or fail fast """
            """for a few seconds. Wait until replication lag is zero and check the last checksum. Promote B. """
            """And the storage layer rejects any write carrying the old epoch, so a stale writer that missed """
            """the memo cannot corrupt anything. That is fencing, and it is the same idea as fencing tokens in """
            """the consensus chapter.""")
seg(sid, 2, """Migrate in slices by tenant or key range: one percent first, then ten, then the rest. Each """
            """slice rehearses the next, and the blast radius of a mistake is one slice.""")
seg(sid, 3, """Rollback is reverse replication from B to A, started before the cut-over, so rolling back is """
            """the same fenced switch in the opposite direction. And define the rollback trigger in advance """
            """&mdash; error rate, latency, a checksum mismatch &mdash; so nobody is debating it at three in the """
            """morning.""")
seg(sid, 4, """Only decommission A after the rollback window has passed and a final verification is clean. """
            """If you have done a migration yourself, this is the moment to tell that story &mdash; it is the """
            """hiring manager round after all.""")

tradeoff('How to get changes across', [
 ('Freeze writes, copy, switch', 'info',
  ['Simplest; trivially consistent'],
  ['<b>Days of read-only</b> at this size &mdash; impossible']),
 ('Snapshot + change-log replay, fenced cut-over', 'ok',
  ['<b>Seconds</b> of write pause', 'Verifiable before switching', 'Rollback via reverse replication'],
  ['Needs a change log', 'Replication pipeline to build and operate']),
 ('Application dual writes', 'shared',
  ['Works without a change log', 'Store-agnostic'],
  ['<b>Silent drift</b> on partial failures', 'Ordering across writers is undefined',
   'Still needs reconciliation']),
], 'Snapshot plus change-log replay, verified, reads shifted in slices, then a fenced write cut-over with '
   'reverse replication.',
 'If the data were small &mdash; minutes to copy &mdash; and a short maintenance window were acceptable, a freeze '
 'and copy is simpler and has fewer ways to go wrong. Size over bandwidth decides.',
 [
 """Trade-off: how to get changes across. Freeze, copy and switch is simplest and trivially consistent, but at """
 """this size it means days of read-only, so it is out.""",
 """Snapshot plus change-log replay with a fenced cut-over costs seconds of write pause, can be verified before """
 """you switch, and rolls back through reverse replication. It needs a change log and a pipeline to run.""",
 """Application dual writes work without a change log, but they drift silently on partial failures, have """
 """undefined ordering across writers, and still need reconciliation.""",
 """I would take snapshot plus replay, verified, with reads shifted in slices and a fenced cut-over.""",
 """And what would flip it: if the data were small enough to copy in minutes and a maintenance window were """
 """acceptable, freeze-and-copy is simpler. Size divided by bandwidth decides, which is why I asked.""",
])

failures('What can go wrong', [
 ('Replay cannot catch up', 'B never converges',
  'Change rate &gt; replay rate: <b>slice</b> the migration, or add bandwidth; never cut over with lag'),
 ('Checksums disagree', 'Unknown divergence',
  'Range checksums <b>locate</b> it; re-copy only those ranges; find the cause before continuing'),
 ('Two writers after cut-over', 'Split brain &mdash; corrupted on both sides',
  '<b>Epoch fencing</b> at the storage layer; old-epoch writes are rejected, not merged'),
 ('Problems found a day after cut-over', 'B has bad data or bad performance',
  'Reverse replication kept A current &mdash; <b>roll back</b> with the same fenced switch'),
 ('Replay applies a change twice', 'Duplicates or wrong counters',
  'Idempotent apply with versions; never blind increments in the replay'),
 ('Cross-store transaction split across the cut-over', 'Half-applied business operation',
  'Cut over related stores <b>together</b>, or drain in-flight transactions first'),
], [
 """What can go wrong. Replay not catching up means B never converges. If the change rate beats the replay """
 """rate, slice the migration or add bandwidth &mdash; and never cut over with lag.""",
 """Checksums disagreeing: range checksums locate the divergence, so you re-copy only those ranges, and you """
 """find the cause before continuing rather than after.""",
 """Two writers after cut-over is split brain. Epoch fencing at the storage layer rejects old-epoch writes """
 """rather than merging them.""",
 """Problems found a day later: reverse replication kept A current, so roll back with the same fenced switch.""",
 """Replay applying a change twice is harmless if the apply is idempotent with versions &mdash; never blind """
 """increments.""",
 """And a cross-store transaction split across the cut-over leaves a half-applied operation, so cut related """
 """stores over together or drain in-flight transactions first.""",
])

say('What I should actually say in the room', [
 'First the conditions: allowed downtime, data size, change rate, link bandwidth, and whether we can split by '
 'tenant.',
 'At 500 TB over 10 Gbps a full copy is days, so a freeze is impossible. That forces live replication.',
 'I take a consistent snapshot at a known log position, bulk-copy it, then replay changes from that position '
 'idempotently, ordered per key. Replay is much faster than the change rate, so B converges.',
 'I verify with range checksums and shadow reads, then shift reads to B slice by slice.',
 'Writes cut over with fencing: bump an epoch, make A read-only, drain lag to zero, promote B, reject old-epoch '
 'writes. Seconds of write pause.',
 'Reverse replication starts before the switch, so rollback is the same switch backwards, with triggers agreed '
 'in advance.',
], [
 """The sentences. Lead with the conditions, because the report says &ldquo;with certain conditions&rdquo; and """
 """asking for them is the first thing being tested.""",
 """Then the arithmetic that rules out a freeze, the five moves in order, and the fencing detail.""",
 """And end on rollback &mdash; a hiring manager remembers the candidate who planned the way back.""",
])

followups([
 'Migrate data from one data centre to another, with certain conditions',
], [
 'The store has no change log. What now?',
 'How do you migrate when the schema is changing at the same time?',
 'How do you prove to leadership that nothing was lost?',
 'What would you do if replication lag spiked during cut-over?',
 'Tell me about a migration you led. What went wrong?',
],
 """There is only one reported prompt, and the conditions were not given &mdash; so the clarify slide is the """
 """real answer to the reported question.""",
 """The likely follow-ups. No change log means dual writes with a reconciliation job, or adding change capture """
 """first, and I would argue for the latter. A schema change at the same time means transforming in the replay """
 """pipeline and verifying the transformed result &mdash; or better, separating the two changes. Proving """
 """nothing was lost is the range checksums plus row counts per slice, published as a report. Lag spiking """
 """during cut-over means abort &mdash; A is still writable until the epoch flips. And the last question is """
 """the hiring manager's real one: have a true migration story ready, with what went wrong in it.""")

cheatsheet('Data-centre migration — the one-page card', [
 ('Requirements', 'Move live data A &rarr; B with minimal downtime, no loss, and a way back'),
 ('Scale', '500 TB over 10 Gbps &asymp; <b>5&ndash;9 days</b> to copy &rarr; a freeze is impossible'),
 ('Core architecture', 'Snapshot at log position &rarr; replay changes &rarr; verify &rarr; shift reads '
                       '&rarr; <b>fenced write cut-over</b>'),
 ('Data store', 'A (truth) &rarr; B (replica, then primary); reverse replication B &rarr; A'),
 ('Partition key', 'Slice by tenant or key range; replay ordered per key'),
 ('Cache', 'Invalidate or warm caches in B before shifting reads'),
 ('Queue', 'The change log is the queue'),
 ('Consistency', 'B seconds behind until cut-over; <b>zero lag</b> before promotion'),
 ('Failure handling', 'Epoch fencing; range checksums; pre-agreed rollback triggers'),
 ('Key deep dives', 'Snapshot + replay vs dual writes &middot; fencing, slices and rollback'),
 ('Biggest trade-off', 'Downtime vs complexity &mdash; <b>size &divide; bandwidth decides</b>'),
], [
 """The card. The scale row is the arithmetic that rules out a freeze.""",
 """The architecture row is the five moves.""",
 """And the trade-off line: size divided by bandwidth decides between simple and safe.""",
])

say('The 60-second answer', [
 'I would start by pinning the conditions: allowed downtime, data size, change rate, link bandwidth, and '
 'whether we can migrate by tenant.',
 'Assuming hundreds of terabytes and near-zero downtime, a freeze-and-copy takes days, so I replicate live: a '
 'consistent snapshot at a recorded log position, bulk-copied, then idempotent replay of every change from '
 'that position, ordered per key, until B is seconds behind.',
 'I verify with checksums per key range and shadow reads, then move reads to B slice by slice.',
 'The write cut-over is fenced: bump an epoch, make A read-only, drain lag to zero, promote B, and have storage '
 'reject old-epoch writes, so two writers can never exist. Writes pause for seconds.',
 'Reverse replication from B to A starts before the switch, so rollback is the same fenced switch in reverse, '
 'with the triggers agreed in advance. A is decommissioned only after the rollback window.',
], [
 """The sixty-second answer. Opening with the conditions is the move, because the question was asked with """
 """them deliberately left out.""",
 """And the last sentence &mdash; keep the way back until you are sure &mdash; is what a hiring manager is """
 """listening for.""",
], kicker='60-second interview answer')
