# -*- coding: utf-8 -*-
"""Chapter 3, Lesson 2 — design a distributed job scheduler."""
from lib import *

lesson_header('3.2', 'Design a distributed job scheduler',
              'Time-ordered work &middot; exactly-once &middot; leases &middot; clock skew',
              dict(reports='1 first-hand report from an Infrastructure loop',
                   latest='30 Sep 2025', level='Senior SWE, Infrastructure',
                   conf='HIGH', sources='Blind &mdash; Infrastructure interview'), 30,
              """Chapter three, lesson two: a distributed job scheduler. Reported first-hand from a LinkedIn """
              """Infrastructure loop on the thirtieth of September twenty twenty-five — which makes it one """
              """of the most directly relevant questions in this course for the team you are interviewing """
              """with. And it contains the single best trap in system design interviewing. One of the """
              """reported follow-ups is exactly-once versus at-least-once execution, and if you answer """
              """that question the way most candidates do, you will spend the rest of the interview """
              """defending something that cannot be built.""")

evidence('Where this question comes from', [
 ('Blind &mdash; Senior SWE Infrastructure interview experience', '30 Sep 2025',
  'Senior SWE, Infrastructure',
  'Asked to design a <b>job scheduler</b>, with functional and non-functional requirements and '
  'trade-off discussion. Reported follow-ups: <b>exactly-once vs at-least-once</b>, missed and '
  'overdue jobs, leader election and partitioning, and back-pressure'),
], """The evidence. A first-hand Blind report from an Infrastructure interview on the thirtieth of """
     """September twenty twenty-five. The candidate was asked to design a job scheduler, covering """
     """functional and non-functional requirements with a trade-off discussion, and they listed four """
     """follow-ups: exactly-once versus at-least-once, missed and overdue jobs, leader election and """
     """partitioning, and back-pressure.""",
 ["""Those four follow-ups are unusually specific, which is what makes me trust the report. They are """
  """also exactly the four hard parts of building a scheduler — so whoever asked this question knew """
  """what they were doing, and we will cover all four."""],
 caveat='Single-source, but recent, detailed, and from the Infrastructure org specifically. '
        'That combination makes it a strong preparation priority for this loop.',
 narration_caveat="""Single-source, so I am not going to oversell it. But it is recent, it is detailed, """
                  """and it comes from the Infrastructure organisation specifically — and that """
                  """combination makes it a strong preparation priority for the loop you are """
                  """sitting.""")

sid = beat('Why this is interesting', 'Time is a different axis from load',
           '<div style="font-size:28px;line-height:1.72">'
           'Most systems you design are driven by <b>arrival</b>: a request comes in, you serve it.<br><br>'
           'A scheduler is driven by <b>time</b>, and that changes everything:<br><br>'
           '<b>&bull; Work arrives in bursts you did not choose.</b> Everyone schedules jobs at the top '
           'of the hour. Your load is <i>spiky by construction</i>.<br>'
           '<b>&bull; &ldquo;Now&rdquo; is not well defined</b> across machines. Clocks disagree.<br>'
           '<b>&bull; Missing work is silent.</b> A dropped request produces an error; a job that never '
           'ran produces <b>nothing at all</b> &mdash; and nobody notices until much later.<br>'
           '<b>&bull; You cannot catch up by going faster</b> if the backlog is itself time-ordered.'
           '<br><br>'
           '<span style="color:#ffd483">The silence is the hard part. Most of this design exists to '
           'make missing work <b>loud</b>.</span></div>',
           """Why is this interesting? Because time is a different axis from load, and almost every other """
           """system you design is driven by arrival — a request comes in, you serve it.""", step=0)
seg(sid, 1, """A scheduler is driven by time, and that changes four things. Work arrives in bursts you did """
            """not choose, because every human being schedules jobs at the top of the hour and at """
            """midnight. Your load is spiky by construction, not by accident.""")
seg(sid, 2, """"Now" is not well defined across machines, because clocks disagree. And missing work is """
            """silent: a dropped request produces an error somewhere, but a job that never ran produces """
            """nothing at all. Nobody notices until the weekly report is missing.""")
seg(sid, 3, """And you cannot always catch up by going faster, if the backlog is itself time-ordered.""")
seg(sid, 4, """The silence is the genuinely hard part, and it is the thing to say early. Most of this """
            """design exists to make missing work loud — and framing it that way will shape every """
            """decision you make in front of the interviewer.""")

think('Your interviewer says: "We need exactly-once execution — a job must never run twice." What do you say back?',
      30,
      """Pause, because this is the moment the interview is decided. Your interviewer says: we need """
      """exactly-once execution, a job must never run twice. What do you say back? Think carefully — """
      """agreeing is the trap.""",
      """Here is the answer, and it is the most valuable thirty seconds in this lesson.""")

sid = beat('The trap', 'Exactly-once execution does not exist',
           '<div class="bigidea">You cannot have exactly-once <b>execution</b>. You can have '
           'at-least-once delivery plus <b>idempotent</b> execution, which is indistinguishable from '
           'the outside &mdash; and is achievable.</div>'
           '<div style="margin-top:24px;font-size:27px;line-height:1.68">'
           '<b>Why it is impossible:</b> a worker takes a job, runs it, and dies before recording that '
           'it finished. The scheduler cannot tell these apart:<br><br>'
           '&bull; the job ran and the acknowledgement was lost &rarr; <b>do not re-run</b><br>'
           '&bull; the job never ran &rarr; <b>must re-run</b><br><br>'
           'No amount of engineering distinguishes them, because the information was destroyed with the '
           'worker. You must choose <b>at-most-once</b> (risk missing work) or <b>at-least-once</b> '
           '(risk duplicates).<br><br>'
           '<span style="color:#ffd483">So: choose at-least-once, and move the problem to the job '
           'itself. <b>&ldquo;Exactly-once effects, not exactly-once execution.&rdquo;</b></span></div>',
           """You cannot have exactly-once execution. What you can have is at-least-once delivery plus """
           """idempotent execution, which from the outside is indistinguishable — and unlike """
           """exactly-once, it is achievable.""", step=0)
seg(sid, 1, """Here is the proof, and it takes twenty seconds to deliver. A worker takes a job, runs it, """
            """and dies before recording that it finished. The scheduler now cannot distinguish two """
            """situations: the job ran and the acknowledgement was lost, in which case re-running is """
            """wrong; or the job never ran, in which case re-running is mandatory.""")
seg(sid, 2, """No amount of engineering distinguishes those two cases, because the information was """
            """destroyed along with the worker. So you must choose: at-most-once, risking missed work, or """
            """at-least-once, risking duplicates.""")
seg(sid, 3, """Therefore choose at-least-once and move the problem into the job itself, with idempotency. """
            """The phrase to use is: exactly-once effects, not exactly-once execution. Say that in the """
            """room and you have demonstrated you understand distributed systems rather than repeating a """
            """marketing term — and crucially, you have done it while giving the interviewer what they """
            """actually want, which is a job that does not run twice in any way that matters.""")

clarify('What I would clarify first', [
 ('One-off jobs, recurring jobs, or both?',
  'Recurring changes the data model: you store a <b>rule</b> plus a next-fire time, and you must '
  'decide what happens when a run overruns its own next slot.'),
 ('What granularity &mdash; and what does &ldquo;on time&rdquo; mean?',
  '&ldquo;Within a second&rdquo; and &ldquo;within a minute&rdquo; are different systems. And '
  '<b>define late</b>: is a job 10 minutes late still useful, or is it now harmful?'),
 ('Can a job run twice, if running twice is harmless?',
  'The whole exactly-once conversation. <b>Ask it early</b>, so you are not retrofitting idempotency.'),
 ('How long can a job run &mdash; seconds, or hours?',
  'Long jobs need <b>lease renewal</b>, not just a timeout. A one-hour job under a five-minute '
  'lease will be executed repeatedly for ever.'),
 ('What happens after an outage &mdash; run everything we missed, or skip?',
  '<b>Catch-up is a thundering herd.</b> For some jobs skipping is correct; for others it is data '
  'loss. This is a per-job policy, not a system-wide one.'),
 ('Is it multi-tenant?',
  'One team scheduling a million jobs must not delay another team&rsquo;s. Fairness becomes a '
  'first-class requirement.'),
], [
 """What I would clarify. One-off, recurring, or both? Recurring changes the data model — you store a """
 """rule plus a next-fire time — and it raises a question people forget: what happens when a run """
 """overruns its own next slot?""",
 """What granularity, and what does on time actually mean? Within a second and within a minute are """
 """different systems. And define late explicitly: is a job ten minutes late still useful, or has it """
 """become harmful? A delayed "send reminder" is fine; a delayed "cancel unpaid order" may not be.""",
 """Can a job run twice if running twice is harmless? This is the exactly-once conversation, and asking """
 """it early means you are designing idempotency in rather than retrofitting it.""",
 """How long can a job run? This one matters more than it sounds. Long jobs need lease renewal rather """
 """than a simple timeout, because a one-hour job under a five-minute lease will be executed over and """
 """over for ever — and that is a genuinely nasty production incident.""",
 """What happens after an outage: run everything we missed, or skip? Catch-up is a thundering herd, and """
 """for some jobs skipping is correct while for others it is data loss. This is a per-job policy rather """
 """than a system-wide one, and saying that is the mature answer.""",
 """And is it multi-tenant? If so, one team scheduling a million jobs must not delay another team's, so """
 """fairness becomes a first-class requirement rather than an afterthought.""",
])

capacity('Capacity — and the number that is not average', [
 ('100M scheduled jobs live', '100M &times; ~500 B', '&asymp; 50 GB',
  'Small. <b>Storage is not the problem here</b> &mdash; say so and move on'),
 ('Average 10M fire per day', '10M &divide; 100k s', '&asymp; 120 jobs / s',
  'Trivially small. <b>And completely misleading</b>'),
 ('Humans schedule on round numbers', '~30% of daily jobs at the top of the hour',
  '<b>&asymp; 3M in one minute</b>', '50,000 / s for 60 seconds. <b>This is the real number</b>'),
 ('Midnight UTC, month end', 'everything cron-like lands together', '<b>10&times; worse again</b>',
  'Design for the <b>spike</b>, and smooth deliberately'),
 ('Worker capacity at 50k/s dispatch', 'each job takes ~200 ms', '<b>10,000 concurrent workers</b>',
  'Or you accept lateness. <b>That is the real trade</b>: capacity vs punctuality'),
 ('After a 1-hour outage', '~400k jobs owed at once', '<b>catch-up storm</b>',
  'Recovery must <b>rate-limit itself</b> or it takes down what it just recovered'),
], [
 """The capacity work, and this system has a number that is unusually misleading. A hundred million """
 """live scheduled jobs at around five hundred bytes each is about fifty gigabytes. Small — storage is """
 """not the problem here, so say so and move on.""",
 """Ten million jobs firing per day averages a hundred and twenty a second. Trivially small. And """
 """completely misleading, which is the point.""",
 """Because humans schedule on round numbers. Something like thirty percent of daily jobs land at the """
 """top of some hour, which means roughly three million jobs inside one minute — fifty thousand a """
 """second for sixty seconds. That is the real number, and it is four hundred times the average.""",
 """And it gets worse at midnight UTC and at month end, when everything cron-like lands together. So """
 """you design for the spike and you smooth deliberately — which is a design decision we will come """
 """back to.""",
 """At fifty thousand dispatches a second, with each job taking about two hundred milliseconds, you need """
 """something like ten thousand concurrent workers — or you accept lateness. And that is the real trade """
 """in this system: capacity versus punctuality. Most organisations quietly choose lateness and never """
 """say so.""",
 """And after a one-hour outage you are owed about four hundred thousand jobs at once. Recovery has to """
 """rate-limit itself, or the catch-up takes down the system you just brought back — which is a failure """
 """mode I would raise unprompted.""",
])

sid = beat('Data model', 'Time buckets, not a sorted index',
           '<div style="font-size:26px;line-height:1.68">'
           '<span style="font-family:JetBrains Mono,monospace;font-size:22px;color:#9fb4cc">'
           'jobs(job_id PK, tenant, payload, schedule_rule, next_fire_at, state,<br>'
           '&nbsp;&nbsp;&nbsp;&nbsp; lease_owner, lease_expires_at, attempt, last_error)</span><br><br>'
           '<b>The hard query:</b> &ldquo;give me every job due in the next second&rdquo;, run '
           'continuously, over a hundred million rows.<br><br>'
           '<b>&bull; A global sorted index on next_fire_at</b> is the obvious answer and it is a '
           '<b>single hot spot</b>: every dispatcher reads and writes the same range, and every job '
           'completion updates the index.<br>'
           '<b>&bull; Time buckets</b> instead: <code>partition = (fire_minute, shard)</code>. A '
           'dispatcher owns specific shards and reads only its own buckets.<br><br>'
           '<span style="color:#ffd483">Partition key = <b>time bucket + shard id</b>. Time gives '
           'locality, the shard spreads the load &mdash; and without the shard, every job in the same '
           'minute lands on one partition. <b>That is the whole design in one line.</b></span></div>',
           """The data model. A jobs table with the payload, the schedule rule, the next fire time, state, """
           """lease fields and attempt count. That part is unremarkable.""", step=0)
seg(sid, 1, """The hard part is the query: give me every job due in the next second, run continuously, over """
            """a hundred million rows. That query is the system.""")
seg(sid, 2, """A global sorted index on next fire time is the obvious answer, and it is a single hot spot. """
            """Every dispatcher reads and writes the same narrow range of that index, and every job """
            """completion updates it. You have built a queue with one lock.""")
seg(sid, 3, """Time buckets instead: partition by fire-minute combined with a shard id. A dispatcher owns """
            """specific shards and reads only its own buckets, so there is no contention between """
            """dispatchers at all.""")
seg(sid, 4, """And say the partition key out loud, because in an infrastructure round this is the sentence """
            """they are waiting for: partition key is time bucket plus shard id. Time gives you locality """
            """so a scan reads contiguous data, and the shard spreads the load — because without the """
            """shard component, every job in the same minute lands on one partition and you have """
            """recreated the hot spot you were avoiding. That is the whole design in one line.""")

# ------------------------------------------------------------------ architecture
A = Arch('Architecture — dispatch, lease, execute, acknowledge', kicker='Progressive disclosure', height=800)
A.box('api',  70, 340, 200, 100, 'Schedule API', kind='neutral', step=0, focus=0)
A.box('st',  330, 340, 230, 100, 'Job store', 'bucketed by time+shard', kind='shared', step=0, focus=[0, 1])
A.arrow('api', 'st', step=0, focus=0)

A.box('d0',  640, 220, 200, 85, 'Dispatcher', 'owns shards 0-4', kind='ok', step=1, focus=1, small=True)
A.box('d1',  640, 340, 200, 85, 'Dispatcher', 'owns shards 5-9', kind='ok', step=1, focus=1, small=True)
A.box('d2',  640, 460, 200, 85, 'Dispatcher', 'owns shards 10-14', kind='ok', step=1, focus=1, small=True)
A.arrow('st', 'd1', step=1, focus=1)

A.box('q',   920, 340, 200, 100, 'Ready queue', kind='dp', step=2, focus=2)
A.arrow('d1', 'q', step=2, focus=2)
A.box('w',  1200, 340, 200, 100, 'Workers', 'take a lease', kind='info', step=2, focus=[2, 3])
A.arrow('q', 'w', step=2, focus=2)
A.arrow('w', 'st', step=3, focus=3, via=[(1300, 640), (445, 640)], fs='b', ts='b', dashed=True,
        label='ack / renew lease')

A.box('coord', 330, 180, 230, 85, 'Coordinator', 'shard assignment', kind='shared', step=4,
      focus=4, small=True)
A.arrow('coord', 'd0', step=4, focus=4)

A.note(1180, 520, '**Lease, not lock:**\\n'
                  'a worker holds a job for N seconds\\n'
                  'and renews while working.\\n\\n'
                  'Worker dies &rarr; lease expires\\n'
                  '&rarr; job becomes eligible again.\\n\\n'
                  '**No distributed lock required.**',
       step=5, kind='ok', w=560, size='m')
A.narrate(0, """The architecture. A schedule API writes jobs into the store, bucketed by time and shard. """
              """Submission is cheap and has nothing to do with execution.""")
A.narrate(1, """Dispatchers each own a set of shards and poll only their own time buckets. Because """
              """ownership is exclusive, two dispatchers never look at the same jobs, so there is no """
              """contention and no coordination on the common path.""")
A.narrate(2, """A dispatcher moves due jobs onto a ready queue, and workers take them from there with a """
              """lease. The queue decouples the rate at which jobs become due from the rate at which """
              """they can be executed — which matters enormously given the spike we calculated.""")
A.narrate(3, """Workers acknowledge completion back to the store, and renew their lease while they are """
              """still working on long jobs.""")
A.narrate(4, """And a coordinator assigns shards to dispatchers, handling the case where a dispatcher dies """
              """and its shards need a new owner. This is the only place that needs consensus, and it """
              """handles a rare event rather than every job.""")
A.narrate(5, """The key mechanism is the lease rather than a lock. A worker holds a job for N seconds and """
              """renews while working. If the worker dies, the lease simply expires and the job becomes """
              """eligible again — no distributed lock, no lock release to forget, no deadlock. Leases """
              """expire on their own, and that self-healing property is exactly why they are the right """
              """primitive for work that outlives the machine doing it.""")
A.build()

sid = beat('Deep dive 1', 'Leases, and the long-job trap',
           '<div style="font-size:26px;line-height:1.68">'
           '<b>The lease protocol:</b><br>'
           '1. Worker atomically claims a job: <code>set lease_owner, lease_expires_at = now + 30 s</code> '
           '<b>where lease_expires_at &lt; now</b> &mdash; a conditional update, so only one worker '
           'can win.<br>'
           '2. Worker runs the job, <b>renewing the lease every 10 s</b>.<br>'
           '3. On success: mark complete. On failure: record the error, schedule a retry.<br>'
           '4. On worker death: the lease expires and another worker claims it.<br><br>'
           '<b>The trap:</b> a job that takes longer than its lease. The lease expires mid-execution, a '
           'second worker claims it, and now <b>two workers are running the same job</b> &mdash; '
           'possibly for ever, in a loop.<br><br>'
           '<b>The fixes:</b> renew from inside the job; make the lease longer than any plausible '
           'runtime; and have the worker <b>check it still owns the lease before committing results</b> '
           '&mdash; a fencing check.<br><br>'
           '<span style="color:#ffd483">Fencing tokens: attach a monotonically increasing number to '
           'each lease, and have the downstream system <b>reject writes from an old token</b>. That is '
           'how you make the check actually safe.</span></div>',
           """Deep dive one: leases, and the trap hiding inside them. The protocol first. A worker claims """
           """a job with a conditional update — set the owner and an expiry thirty seconds out, but only """
           """where the existing lease has already expired. Because that is a single conditional write, """
           """exactly one worker can win, and you have mutual exclusion without a lock service.""",
           step=0)
seg(sid, 1, """The worker then runs the job, renewing its lease every ten seconds. On success it marks """
            """complete; on failure it records the error and schedules a retry. And if the worker dies, """
            """the lease expires on its own and another worker picks the job up.""")
seg(sid, 2, """Now the trap, and this is a real production incident I would want you to name before the """
            """interviewer does. A job takes longer than its lease. The lease expires mid-execution, a """
            """second worker claims the job, and now two workers are running it simultaneously — """
            """potentially for ever, each one being displaced by the next in a loop.""")
seg(sid, 3, """Three fixes, and you want all three. Renew from inside the job, so renewal continues while """
            """work continues. Make the lease comfortably longer than any plausible runtime. And have """
            """the worker check it still owns the lease before committing results.""")
seg(sid, 4, """But that last check is not sufficient on its own, because the check and the commit are not """
            """atomic. The real answer is fencing tokens: attach a monotonically increasing number to """
            """each lease, and have the downstream system reject any write carrying an old token. That is """
            """how you make the check genuinely safe, and mentioning fencing tokens unprompted is one of """
            """the strongest signals available in an infrastructure interview.""")

sid = beat('Deep dive 2', 'Idempotency — where exactly-once actually lives',
           '<div style="font-size:27px;line-height:1.7">'
           'We chose at-least-once. So duplicates <b>will</b> happen, and the job must tolerate them.'
           '<br><br>'
           '<b>The scheduler&rsquo;s job:</b> give every execution attempt a stable '
           '<code>execution_id</code> &mdash; the same id across retries of the same scheduled run, '
           'a different id for the next run.<br><br>'
           '<b>The job&rsquo;s job:</b> use it. Three patterns, in order of preference:<br>'
           '&bull; <b>Naturally idempotent</b> &mdash; &ldquo;set status to X&rdquo; is safe to repeat. '
           'Prefer designing the work this way.<br>'
           '&bull; <b>Conditional write</b> &mdash; insert with the execution_id as a unique key; a '
           'duplicate collides and is discarded.<br>'
           '&bull; <b>Dedupe table</b> &mdash; record completed execution_ids and check first. Needs '
           'its own retention policy.<br><br>'
           '<span style="color:#ffd483">If the job calls a third party with no idempotency key, you '
           '<b>cannot</b> make it safe. Say that plainly rather than pretending &mdash; and make the '
           'lease long and the retry conservative.</span></div>',
           """Deep dive two: idempotency, which is where exactly-once actually lives once you have been """
           """honest that exactly-once execution does not exist. We chose at-least-once, so duplicates """
           """will happen and the job must tolerate them.""", step=0)
seg(sid, 1, """The scheduler's responsibility is to give every execution attempt a stable execution id — """
            """the same id across retries of the same scheduled run, and a different id for the next """
            """run. That distinction matters: retries of Tuesday's run share an id, but Wednesday's run """
            """gets a new one.""")
seg(sid, 2, """The job's responsibility is to use it, and there are three patterns in order of preference. """
            """Naturally idempotent work — setting a status to a value is safe to repeat — and you should """
            """prefer designing the work that way where you can. Conditional writes, where you insert """
            """using the execution id as a unique key so a duplicate simply collides and is discarded. """
            """And a dedupe table recording completed execution ids, which works but needs its own """
            """retention policy or it grows for ever.""")
seg(sid, 3, """And the honest limit, which I would volunteer: if the job calls a third party that offers no """
            """idempotency key, you cannot make it safe. You can only make duplicates less likely by """
            """using a long lease and a conservative retry policy. Saying that plainly, rather than """
            """pretending the problem is solved, is exactly the kind of intellectual honesty that """
            """separates candidates — because every experienced interviewer has been burned by this.""")

sid = beat('The four reported follow-ups', 'All of them, answered',
           '<table class="fail" style="top:40px"><thead><tr><th>Follow-up</th><th>The answer</th>'
           '</tr></thead><tbody>'
           '<tr data-step="0"><td class="f-c">Exactly-once<br>vs at-least-once</td>'
           '<td>Exactly-once execution is impossible &mdash; a worker can die between running and '
           'acknowledging. Choose <b>at-least-once plus idempotent jobs</b>, with a stable execution id. '
           '<b>Exactly-once effects, not exactly-once execution.</b></td></tr>'
           '<tr data-step="1"><td class="f-c">Missed and<br>overdue jobs</td>'
           '<td>Detect with a <b>watchdog</b> that scans for jobs past due and unclaimed &mdash; missing '
           'work is silent, so you must look for it. Then <b>per-job catch-up policy</b>: run all '
           'missed, run only the latest, or skip. And <b>rate-limit the catch-up</b> or it becomes a '
           'second outage.</td></tr>'
           '<tr data-step="2"><td class="f-c">Leader election<br>and partitioning</td>'
           '<td>Do <b>not</b> elect one leader to dispatch everything &mdash; that caps throughput at '
           'one machine. Partition the shards and use consensus only to <b>assign</b> shards. '
           'Leadership is per shard, and rebalancing is rare.</td></tr>'
           '<tr data-step="3"><td class="f-c">Back-pressure</td>'
           '<td>The ready queue has a bounded depth. When full, dispatchers <b>stop dispatching</b> '
           'rather than buffering infinitely &mdash; jobs stay in the store, which is durable, and run '
           'late. <b>Late is recoverable; lost is not.</b></td></tr>'
           '</tbody></table>',
           """Now let us answer the four reported follow-ups directly, because they were listed """
           """explicitly and you should have all four ready. Exactly-once versus at-least-once we have """
           """covered: impossible, so at-least-once with idempotent jobs and a stable execution id.""",
           step=0)
seg(sid, 1, """Missed and overdue jobs. First, detection — and the important framing is that missing work """
            """is silent, so you must actively look for it. A watchdog scans for jobs past their due time """
            """that are unclaimed. Then a per-job catch-up policy: run everything missed, run only the """
            """latest, or skip entirely. And rate-limit the catch-up, or your recovery becomes a second """
            """outage.""")
seg(sid, 2, """Leader election and partitioning, where there is a trap. Do not elect a single leader to """
            """dispatch everything, because that caps your throughput at one machine and we already """
            """calculated fifty thousand dispatches a second at peak. Instead partition the shards and """
            """use consensus only to assign shards to dispatchers. Leadership is per shard, and """
            """rebalancing is a rare event rather than a hot path.""")
seg(sid, 3, """And back-pressure. The ready queue has a bounded depth, and when it is full the dispatchers """
            """stop dispatching rather than buffering infinitely. Jobs stay in the store, which is """
            """durable, and they run late. The sentence to close on is: late is recoverable, lost is """
            """not. That single principle tells the interviewer how you think about degradation.""")

failures('What happens when each piece dies', [
 ('One worker', 'Nothing &mdash; its lease expires and another worker claims the job',
  'The expected case. Design cost: jobs must be idempotent, which we already required'),
 ('One dispatcher', 'Its shards stop dispatching until reassigned',
  'The coordinator reassigns. <b>Jobs are late, not lost</b> &mdash; they are safe in the store'),
 ('The coordinator', 'No rebalancing; existing dispatchers keep working',
  'Not on the hot path, so this degrades slowly. <b>Run it on consensus and do not panic</b>'),
 ('Job store', '<b>Everything stops</b>',
  'The genuine single point. Replicate, and accept that this is the one component whose '
  'availability <i>is</i> the system&rsquo;s'),
 ('A job hangs for ever', 'It holds a lease, renews, and never finishes',
  'Leases alone do not save you. Add an <b>absolute maximum runtime</b>, after which the job is '
  'killed and marked failed'),
 ('Clock skew between nodes', 'Jobs fire early or late; leases expire unexpectedly',
  'Use <b>one clock</b> &mdash; the store&rsquo;s &mdash; for lease decisions, not each worker&rsquo;s. '
  'Compare against server time, and bound acceptable skew'),
 ('After an outage', '<b>400k jobs owed at once</b>',
  'Rate-limited catch-up with per-job policy. <b>The recovery must not become the next incident</b>'),
], [
 """The failure table. A worker dying is the expected case — its lease expires and another worker claims """
 """the job. The design cost is that jobs must be idempotent, which we already required, so this costs """
 """nothing extra.""",
 """A dispatcher dying means its shards stop until the coordinator reassigns them. Jobs are late, not """
 """lost, because they are sitting safely in the store.""",
 """The coordinator dying means no rebalancing while existing dispatchers keep working. It is not on """
 """the hot path, so this degrades slowly — run it on a consensus system and do not over-engineer """
 """around it.""",
 """The job store is the genuine single point: if it is gone, everything stops. Replicate it, and be """
 """honest that this is the one component whose availability simply is the system's availability. """
 """Naming your real single point of failure rather than pretending you have none is a strong move.""",
 """A job that hangs for ever is the subtle one: it holds a lease and keeps renewing, so leases alone """
 """do not save you. You need an absolute maximum runtime, after which the job is killed and marked """
 """failed.""",
 """Clock skew: use one clock — the store's — for lease decisions rather than each worker's local """
 """clock. Compare against server time and bound the acceptable skew. Two machines disagreeing about """
 """now is how leases expire unexpectedly and jobs fire twice.""",
 """And after an outage, four hundred thousand jobs owed at once. Rate-limited catch-up with per-job """
 """policy, because the recovery must not become the next incident.""",
])

sid = beat('Observability, security, cost', 'Making silence loud',
           '<div class="to-grid" style="top:24px">'
           '<div class="to-opt k-info" data-step="0"><div class="to-h">What I would alert on</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; <b>Scheduling lag</b> &mdash; fire time vs actual start, at p99. <i>The</i> metric<br>'
           '&bull; <b>Overdue unclaimed count</b> &mdash; catches silent loss<br>'
           '&bull; Ready-queue depth &mdash; back-pressure indicator<br>'
           '&bull; Lease expiry rate &mdash; a rise means workers are dying or jobs are overrunning<br>'
           '&bull; Retry and failure rate <b>per tenant</b><br><br>'
           '<span style="color:#ffd483">And a <b>canary job</b> scheduled every minute. If it does '
           'not run, the scheduler is broken &mdash; <b>the only way to detect silence</b>.</span></div></div>'
           '<div class="to-opt k-shared" data-step="1"><div class="to-h">Security</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; A scheduler is <b>remote code execution as a service</b>. Treat it that way<br>'
           '&bull; Jobs run with the <b>submitter&rsquo;s</b> permissions, not the scheduler&rsquo;s<br>'
           '&bull; Payloads carry secrets &mdash; encrypt at rest, redact in logs<br>'
           '&bull; Per-tenant quotas: jobs, concurrency, and runtime<br>'
           '&bull; Audit who scheduled what</div></div>'
           '<div class="to-opt k-ok" data-step="2"><div class="to-h">Cost</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; Dominated by <b>worker capacity sized for the spike</b><br>'
           '&bull; Biggest lever: <b>smooth the spike</b> &mdash; jitter scheduled times by a few '
           'minutes and the peak collapses<br>'
           '&bull; Second: autoscale workers on queue depth &mdash; the spike is predictable, so '
           '<b>scale before it</b><br><br>'
           '<span style="color:#ffd483">Adding jitter is nearly free and can halve the fleet. '
           '<b>Offer it.</b></span></div></div></div>',
           """Observability, and here it has a specific mission: making silence loud. Alert on scheduling """
           """lag — the gap between when a job should have fired and when it actually started, at p """
           """ninety-nine. That is the metric for this system. Alert on overdue unclaimed count, which """
           """catches silent loss. Queue depth as your back-pressure indicator. Lease expiry rate, where """
           """a rise means workers are dying or jobs are overrunning their leases.""", step=0)
seg(sid, 1, """And the technique I would make sure to mention: a canary job scheduled every minute that """
            """does nothing but record that it ran. If the canary does not run, the scheduler is broken. """
            """It is the only reliable way to detect silence, because every other metric can look """
            """perfectly healthy while nothing is being dispatched at all.""")
seg(sid, 2, """Security, and the framing is worth saying out loud: a job scheduler is remote code """
            """execution as a service. Treat it that way. Jobs run with the submitter's permissions """
            """rather than the scheduler's, which prevents privilege escalation through job submission. """
            """Payloads carry secrets, so encrypt at rest and redact in logs. Per-tenant quotas on job """
            """count, concurrency and runtime. And audit who scheduled what.""")
seg(sid, 3, """Cost is dominated by worker capacity sized for the spike, and the biggest lever is to """
            """attack the spike itself: jitter scheduled times by a few minutes and the peak collapses. """
            """Most jobs do not actually need to run at exactly nine o'clock — they need to run around """
            """nine o'clock. Adding jitter is nearly free and can halve your fleet, so offer it. Second """
            """lever: autoscale workers on queue depth, and since the spike is predictable, scale before """
            """it rather than reacting to it.""")

sid = cards('Staff-level follow-ups', [
 (0, '&ldquo;Ten times the jobs.&rdquo;',
  'Add shards and dispatchers &mdash; they scale linearly because ownership is exclusive. The store is the limit, so partition it further. <b>Nothing structural changes.</b>', 'ok'),
 (0, '&ldquo;Second-level precision.&rdquo;',
  'Bucket by second rather than minute, and poll more frequently. The cost is more empty polls. Below ~1 s you want a <b>timer wheel in memory</b> for the near horizon, with the store as the durable backstop.', 'ok'),
 (1, '&ldquo;A tenant schedules a million jobs for the same second.&rdquo;',
  'Quota at submit time, plus <b>automatic jitter</b>. And fair dispatch: round-robin across tenants rather than strict time order, so one tenant cannot starve everyone else.', 'ok'),
 (1, '&ldquo;Jobs must run in order within a tenant.&rdquo;',
  'That removes most of your parallelism. Partition by ordering key and run <b>one worker per key</b> &mdash; ordering and throughput are directly opposed, and I would push to make ordering per-key rather than global.', 'shared'),
 (2, '&ldquo;What if a job must not run twice, ever?&rdquo;',
  'Then it needs at-most-once: claim, mark as started <b>before</b> executing, never retry. You have traded duplicates for <b>occasionally never running</b>. Make the caller choose &mdash; and make sure they understand what they chose.', 'deny'),
 (2, '&ldquo;Multi-region.&rdquo;',
  'Schedule in the region that owns the tenant&rsquo;s data. Do <b>not</b> run one global scheduler &mdash; cross-region lease renewal at 70 ms RTT makes leases unreliable and the failure modes horrible.', 'ok'),
], cols=2)
seg(sid, 0, """Staff-level follow-ups. Ten times the jobs: add shards and dispatchers, which scale linearly """
            """because ownership is exclusive and there is no coordination between them. The store """
            """becomes the limit, so partition it further. Nothing structural changes.""")
seg(sid, 1, """Second-level precision: bucket by second rather than minute and poll more often, paying in """
            """empty polls. Below about a second you want an in-memory timer wheel for the near horizon, """
            """with the durable store as the backstop — because at that granularity, a database round """
            """trip per job is the bottleneck.""")
seg(sid, 2, """A tenant scheduling a million jobs for the same second: quota at submission time plus """
            """automatic jitter, and fair dispatch that round-robins across tenants rather than following """
            """strict time order. Strict time order sounds correct and lets one tenant starve everyone """
            """else, which is a nice example of a reasonable-sounding rule being wrong.""")
seg(sid, 3, """Jobs must run in order within a tenant: that removes most of your parallelism. Partition by """
            """ordering key and run one worker per key. And I would push back here — ordering and """
            """throughput are directly opposed, so I would ask whether ordering is genuinely needed """
            """globally or only per key, because the answer is usually per key and that is far """
            """cheaper.""")
seg(sid, 4, """What if a job must never run twice? Then you need at-most-once: claim it, mark it started """
            """before executing, and never retry. You have traded duplicates for occasionally never """
            """running at all. Make the caller choose explicitly, and make sure they understand what they """
            """have chosen — because "never runs twice" sounds obviously desirable right up until the """
            """payroll job silently does not run.""")
seg(sid, 5, """And multi-region: schedule in the region that owns the tenant's data. Do not run one global """
            """scheduler, because cross-region lease renewal at seventy milliseconds round trip makes """
            """leases unreliable and the failure modes genuinely horrible — you get jobs running twice in """
            """two regions during a partition.""")

followups(
 ['Exactly-once vs at-least-once &mdash; <b>reported</b>',
  'Missed and overdue jobs &mdash; <b>reported</b>',
  'Leader election and partitioning &mdash; <b>reported</b>',
  'Back-pressure &mdash; <b>reported</b>'],
 ['"What happens if a job outlives its lease?"',
  '"How do you know a job did not run?"',
  '"A tenant schedules a million jobs at once"',
  '"What do you do after a one-hour outage?"',
  '"Does the job need ordering?"'],
 """This question has the best-documented follow-ups in the whole course: all four were named in the """
 """candidate's report — exactly-once versus at-least-once, missed and overdue jobs, leader election """
 """and partitioning, and back-pressure. We have answered all four directly, and I would rehearse those """
 """four answers until they are automatic.""",
 """And these are the ones I would expect on top, all of which probe the same design. What happens when """
 """a job outlives its lease. How you know a job did not run — the silence problem. A tenant flooding """
 """you. What you do after an outage. And whether ordering is required, which is the question that """
 """quietly destroys your parallelism if the answer is yes.""")

say('What I should say — the sentences that carry this design', [
 'Before I design: can a job run twice if running twice is harmless? That answer changes the entire execution model.',
 'Exactly-once execution is not achievable — a worker can die between running the job and acknowledging it, and nothing can distinguish that from never having run. So I would do at-least-once with idempotent jobs: exactly-once effects, not exactly-once execution.',
 'The average is a hundred and twenty jobs a second, but humans schedule on round numbers, so the top of the hour is nearer fifty thousand a second. I am designing for that, not the average.',
 'I will partition by time bucket plus a shard id. Time alone would put every job in the same minute on one partition.',
 'Workers take a lease rather than a lock, so a dead worker simply lets the lease expire — there is no lock to release and nothing to deadlock.',
 'The trap is a job outliving its lease, so I would renew from inside the job and use a fencing token that downstream systems check.',
 'For back-pressure the queue is bounded, and when it is full dispatchers stop rather than buffering. Jobs run late but are never lost — late is recoverable, lost is not.',
 'Missing work is silent, so I would run a canary job every minute. If it does not fire, the scheduler is broken.',
], [
 """Eight sentences, and the second one is the most important in this entire course. The first is the """
 """clarification that shapes everything.""",
 """The second is the exactly-once refusal with its proof and its replacement, delivered in one breath. """
 """Rehearse it until it is automatic, because it is both a trap and an opportunity.""",
 """The third shows you understand that the average is misleading, which is specific to time-driven """
 """systems.""",
 """The fourth is your partition key with the failure of the naive version attached.""",
 """The fifth explains leases in terms of what they buy you. The sixth names the trap and the fencing """
 """token fix.""",
 """The seventh gives the back-pressure principle in a form you can apply anywhere. And the eighth is """
 """the canary — the answer to the hardest property of this system, which is that its failures are """
 """invisible. Close on that.""",
])

cheatsheet('Job scheduler — the revision card', [
 ('Problem', 'Run jobs at a scheduled time, at scale, reliably'),
 ('Evidence', '1 first-hand Infra report &middot; 30 Sep 2025 &middot; HIGH'),
 ('Scale', '100M live jobs &middot; 120/s average &middot; <b>50k/s at the top of the hour</b>'),
 ('Dominant constraint', 'Spiky load, and <b>silent</b> failure'),
 ('Partition key', '<b>time bucket + shard id</b>'),
 ('Why not sorted index', 'Single hot range; every dispatcher contends'),
 ('Execution model', '<b>At-least-once + idempotent jobs</b>'),
 ('Exactly-once', '<b>Impossible.</b> Worker dies between run and ack'),
 ('The phrase', 'Exactly-once <i>effects</i>, not exactly-once execution'),
 ('Concurrency', '<b>Leases, not locks</b> &mdash; they expire on their own'),
 ('Lease trap', 'Job outlives lease &rarr; two runners. Renew + <b>fencing token</b>'),
 ('Idempotency', 'Stable execution_id; conditional write or dedupe table'),
 ('Leader election', 'Assign <b>shards</b>; never one leader dispatching all'),
 ('Back-pressure', 'Bounded queue; dispatchers stop. <b>Late &gt; lost</b>'),
 ('Missed jobs', 'Watchdog scan + <b>per-job</b> catch-up policy'),
 ('Catch-up', '<b>Rate-limit it</b> or recovery becomes the next outage'),
 ('Clock skew', 'One clock &mdash; the store&rsquo;s &mdash; for lease decisions'),
 ('Alert on', 'Scheduling lag p99, overdue unclaimed, <b>canary job</b>'),
 ('Cost lever', '<b>Jitter</b> the schedule &mdash; nearly free, halves the peak'),
 ('Biggest risk', 'Silent non-execution'),
], [
 """The revision card. Problem, evidence, scale — with the spike called out, because that is the number """
 """that matters.""",
 """The partition key and why the obvious alternative fails.""",
 """Then the centrepiece: the execution model, why exactly-once is impossible, and the phrase to use.""",
 """Leases rather than locks, the long-job trap, the fencing token, and the idempotency mechanism.""",
 """Leader election done per shard, back-pressure with the late-beats-lost principle, missed jobs, """
 """catch-up rate limiting, and clock discipline.""",
 """Then what to alert on including the canary, the jitter cost lever, and the biggest risk — silent """
 """non-execution, which is what the whole design defends against.""",
])

sid = statement('Lesson 3.2', 'Refusing an impossible requirement is a senior move.',
                'The interviewer asks for exactly-once. The best answer explains why it cannot exist, then delivers what they actually wanted — and that exchange is worth more than the architecture.',
                kind='ok')
seg(sid, 0, """One line to close, and it generalises far beyond schedulers. Refusing an impossible """
            """requirement is a senior move.""")
seg(sid, 1, """The interviewer asks for exactly-once execution. The weak answer agrees and then quietly """
            """builds at-least-once while calling it exactly-once. The strong answer explains in twenty """
            """seconds why exactly-once cannot exist, and then delivers what they actually wanted — a job """
            """that never has a duplicate effect. That exchange is worth more than the rest of the """
            """architecture put together, because it is the clearest possible evidence that you """
            """understand distributed systems rather than their vocabulary. Next: the message queue, """
            """which LinkedIn wrote, and where the depth bar is correspondingly higher.""")
