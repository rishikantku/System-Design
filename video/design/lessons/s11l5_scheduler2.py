# -*- coding: utf-8 -*-
"""Chapter 11, Lesson 5 — job scheduler part two: a machine API, execution, and alerts. A delta on 3.2."""
from lib import *

lesson_header('11.5', 'Job scheduler, part two: fetch machines, execute, and alert',
              'Delta on 3.2 &middot; machine leases &middot; executor heartbeats &middot; job state machine &middot; alerting',
              dict(reports='Candidate report, onsite R3 (HLD)', latest='2025&ndash;26', level='Onsite, HLD round',
                   conf='HIGH as a family &mdash; schedulers recur across LinkedIn reports',
                   sources='LeetCode Discuss (supplied by you) + the 3.2 Blind report'), 16,
              """Lesson five builds on lesson three point two rather than repeating it. A candidate reported """
              """this prompt in an onsite high-level design round: design a distributed job scheduler. You are """
              """given an API to fetch machines for running jobs. Design a system that schedules jobs, executes """
              """them, and triggers alerts. Three point two taught you when a job should run and how to make it """
              """run once. This lesson is about the two words that prompt adds: <i>machines</i> and """
              """<i>alerts</i>.""")

evidence('Where this question comes from', [
 ('LeetCode Discuss &mdash; LinkedIn onsite, round 3 (HLD)', '2025–26', 'Onsite, HLD',
  '<b>&ldquo;Design a distributed job scheduler. You are given an API to fetch machines for running jobs. '
  'Design a system that schedules jobs, executes them, and triggers alerts.&rdquo;</b>'),
 ('Blind &mdash; Senior SWE Infrastructure (lesson 3.2)', '30 Sep 2025', 'Senior SWE, Infra',
  'Job scheduler: exactly-once, missed jobs, leader election, back-pressure'),
], """Two independent reports of a scheduler question, so the family is high confidence. This version adds """
   """resource acquisition and alerting.""",
 ["""Watch the wording: &ldquo;you are given an API to fetch machines&rdquo;. You do not design the cluster """
  """manager. You design around an API you do not control &mdash; which means you must assume it is slow, """
  """rate-limited, and sometimes says no."""],
 caveat='Supplied by you from LeetCode Discuss; exact date not recorded.',
 narration_caveat="""You supplied this one from LeetCode Discuss, and the exact date was not recorded.""")

sid = beat('Why this is interesting', 'Three systems: when, where, and who gets told',
           '<div style="font-size:28px;line-height:1.72">'
           '<b>When</b> &mdash; the timing wheel, leases, exactly-once. <span style="color:#a8e6a3">That is '
           'lesson 3.2. Reuse it in two minutes.</span><br><br>'
           '<b>Where</b> &mdash; <i>new</i>: get machines from an API you do not own, run the job on one, and '
           'know whether it is still alive.<br><br>'
           '<b>Who gets told</b> &mdash; <i>new</i>: job owners must hear about failures, timeouts, and '
           '<b>jobs that never started</b>.<br><br>'
           '<span style="color:#ff9a9a">The trap: calling the machine API once per job, synchronously, on the '
           'scheduling path.</span> It is slow and rate-limited &mdash; your scheduler&rsquo;s throughput becomes '
           'its throughput.<br><br>'
           '<span style="color:#ffd483">And the alert nobody designs: the one for silence.</span></div>',
           """Why is this interesting? Because there are three systems: when, where, and who gets told.""", step=0)
seg(sid, 1, """When a job runs is lesson three point two &mdash; the timing structure, leases and exactly-once. """
            """Reuse it in two minutes and say that you are doing so.""")
seg(sid, 2, """Where it runs is new: get machines from an API you do not own, run the job on one, and know """
            """whether that machine is still alive.""")
seg(sid, 3, """And who gets told is new too: job owners have to hear about failures, timeouts, and jobs that """
            """never started at all.""")
seg(sid, 4, """The trap is calling the machine API once per job, synchronously, on the scheduling path. That API """
            """is slow and rate-limited, so your scheduler's throughput silently becomes its throughput.""")
seg(sid, 5, """And the alert nobody designs is the one for silence &mdash; the job that should have run and """
            """did not, which produces no error at all.""")

think('The machine API takes 2 seconds and allows 50 calls a second. You need to start 2,000 jobs at the top of the '
      'hour. What happens if you call it once per job?',
      20,
      """Pause. The machine API takes two seconds and allows fifty calls a second. Two thousand jobs are due at """
      """the top of the hour. What happens if you call it once per job?""",
      """Hold that. It is the reason for the warm pool in deep dive one.""")

clarify('What I would clarify first', [
 ('What does the machine API return &mdash; a whole machine, or capacity on a shared one?',
  'Whole machines suggests <b>one job per machine</b> or bin-packing yourself; slots means the API packs.'),
 ('How fast and how limited is it? Can it refuse?',
  'Slow or rate-limited forces a <b>warm pool</b>; refusal forces queueing and back-pressure.'),
 ('Who must be alerted, about what, through which channels?',
  'Owner-facing alerts are a <b>product</b>: rules, routing, dedup &mdash; not just ops dashboards.'),
 ('Job duration range &mdash; seconds or hours?',
  'Long jobs need <b>heartbeats and checkpoints</b>; short ones can simply be retried.'),
 ('Retries &mdash; how many, and are jobs idempotent?',
  'Non-idempotent jobs need <b>fencing</b> so a presumed-dead executor cannot finish late.'),
 ('Do we release machines after each job?',
  'Release costs another slow call later; keep them warm with an <b>idle TTL</b>.'),
], [
 """What does the machine API return &mdash; a whole machine or capacity on a shared one? Whole machines """
 """means you either run one job per machine or bin-pack yourself.""",
 """How fast and how limited is it, and can it refuse? Slow or rate-limited forces a warm pool. Refusal """
 """forces queueing and back-pressure.""",
 """Who must be alerted, about what, through which channels? Owner-facing alerts are a product with rules, """
 """routing and deduplication, not just an ops dashboard.""",
 """Job durations? Long jobs need heartbeats and checkpoints; short ones can just be retried.""",
 """Retries, and are jobs idempotent? Non-idempotent jobs need fencing, so an executor you presumed dead """
 """cannot finish late and double-apply.""",
 """And do we release machines after each job? Releasing costs another slow call later, so keep them warm """
 """with an idle timeout.""",
])

capacity('Capacity', [
 ('Jobs', 'assume 1M jobs / day', '&asymp; 12 / s avg',
  'But <b>top-of-hour bursts</b>: ~20k jobs in the first minute'),
 ('Machine API', '2 s latency, 50 calls / s', '<b>3,000 machines / minute max</b>',
  'A 20k burst would take <b>7 minutes</b> just to acquire machines'),
 ('Warm pool', 'size for the burst minus API rate', '&asymp; 17k idle slots at the hour',
  'Or <b>batch acquisition</b> (ask for 100 per call) and pre-warm before the hour'),
 ('Heartbeats', '20k running jobs / 10 s interval', '2k heartbeats / s',
  'Small. A detection delay of ~30 s (3 missed beats)'),
 ('Alert events', 'failure rate ~1%', '&asymp; 10k failures / day',
  'After grouping and dedup, <b>far fewer notifications</b> &mdash; that is the point'),
], [
 """Numbers. A million jobs a day is only twelve a second on average, but schedules cluster at the top of the """
 """hour &mdash; say twenty thousand in the first minute.""",
 """The machine API at two seconds and fifty calls a second gives at most three thousand machines a minute. """
 """Twenty thousand jobs would take seven minutes just to acquire machines. That is the answer to the """
 """pause.""",
 """So a warm pool sized for the burst, or batch acquisition &mdash; a hundred machines per call &mdash; and """
 """pre-warming a few minutes before the hour, because the schedule tells you exactly when the burst is """
 """coming.""",
 """Heartbeats from twenty thousand running jobs every ten seconds is two thousand a second, small, with about """
 """thirty seconds to detect a dead executor.""",
 """And with a one percent failure rate, ten thousand failure events a day, which grouping and deduplication """
 """turn into far fewer notifications.""",
])

A = Arch('Scheduler — when, where, and who gets told', kicker='Architecture', height=800)

A.zone(60, 120, 520, 600, 'WHEN — reuse lesson 3.2')
A.zone(640, 120, 640, 600, 'WHERE — machines and execution')
A.zone(1340, 120, 440, 600, 'WHO GETS TOLD')

A.box('api',   100, 160, 220, 95, 'Job API', 'create, cron, cancel', kind='info', step=0, focus=0, small=True)
A.box('sch',   100, 320, 440, 120, 'Scheduler (3.2)', 'due-time index, leases, exactly-once claim', kind='ok', step=0, focus=0)
A.arrow('api', 'sch', step=0, focus=0, fs='b', ts='t')
A.box('q',     100, 540, 440, 100, 'Ready queue', 'jobs due now, by priority', kind='shared', step=1, focus=1, small=True)
A.arrow('sch', 'q', step=1, focus=1, fs='b', ts='t')

A.box('disp',  680, 540, 260, 100, 'Dispatcher', 'match job to machine', kind='ok', step=2, focus=[2, 3])
A.arrow('q', 'disp', step=2, focus=2)
A.box('pool',  680, 330, 260, 120, 'Machine pool', 'warm, leased, idle TTL', kind='dp', step=2, focus=2)
A.arrow('pool', 'disp', step=2, focus=2, fs='b', ts='t')
A.box('mapi',  680, 160, 260, 95, 'Machine API', 'given — slow, rate-limited', kind='bad', step=2, focus=2, small=True)
A.arrow('mapi', 'pool', step=2, focus=2, fs='b', ts='t', label='batch acquire')

A.box('agent', 1010, 330, 240, 120, 'Executor agent', 'runs job, heartbeats', kind='ok', step=3, focus=[3, 4])
A.arrow('disp', 'agent', step=3, focus=3, label='job + epoch')
A.box('state', 1010, 540, 240, 100, 'Job state store', 'state machine, attempts', kind='dp', step=4, focus=4, small=True)
A.arrow('agent', 'state', step=4, focus=4, fs='b', ts='t')

A.box('rules', 1380, 330, 360, 120, 'Alert engine', 'rules: failed, timed out, never started', kind='shared', step=5, focus=[5, 6])
A.arrow('state', 'rules', step=5, focus=5)
A.box('route', 1380, 540, 360, 100, 'Routing + dedup', 'owner, severity, channel', kind='info', step=6, focus=6, small=True)
A.arrow('rules', 'route', step=6, focus=6, fs='b', ts='t')
A.box('dms',   1380, 160, 360, 95, 'Dead-man check', 'expected runs vs actual', kind='bad', step=7, focus=7, small=True)
A.arrow('dms', 'rules', step=7, focus=7, fs='b', ts='t')

A.narrate(0, """The left third is lesson three point two, and I would say exactly that: a job A-P-I, and a """
             """scheduler with a due-time index, leases and an exactly-once claim. Two minutes, not twenty.""")
A.narrate(1, """When a job becomes due, the scheduler claims it and puts it on a ready queue, ordered by """
             """priority. This queue is what decouples timing from machines.""",
          A.flow([(320, 440), (320, 540)]))
A.narrate(2, """The machine side. The given machine A-P-I is slow and rate-limited, so we never call it per job. A """
             """pool manager acquires machines in batches ahead of demand &mdash; the schedule tells us when the """
             """burst is coming &mdash; and keeps them warm with an idle timeout. The dispatcher matches ready jobs """
             """to free machines.""",
          A.flow([(810, 255), (810, 330), (810, 540)]))
A.narrate(3, """The dispatcher sends the job to an executor agent on the machine, stamped with an attempt epoch. """
             """The agent runs it.""",
          A.flow([(940, 590), (1010, 390)]))
A.narrate(4, """The agent heartbeats while the job runs and reports the result. A job state store holds the state """
             """machine for every attempt: scheduled, dispatched, running, succeeded, failed, timed out.""")
A.narrate(5, """Every state change flows to an alert engine evaluating rules: the job failed, it exceeded its """
             """timeout, it retried too many times.""",
          A.flow([(1250, 590), (1380, 390)]))
A.narrate(6, """Routing and deduplication decide who hears about it and how: the owning team, by severity, """
             """grouped so one broken dependency is one page rather than four hundred.""")
A.narrate(7, """And the dead-man check compares expected runs, derived from the schedules, against actual """
             """starts. It is the only way to alert on a job that never ran, because that job produced no event """
             """at all.""")
A.build()

sid = beat('Deep dive 1', 'Machines you do not own &mdash; pool, leases, heartbeats, fencing',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Treat the machine API as a slow external dependency:</b><br>'
           '&bull; <b>Warm pool</b> + batch acquisition, pre-warmed from the known schedule<br>'
           '&bull; Machines are <b>leased</b> from the pool with an idle TTL; release when idle, not after each job<br>'
           '&bull; If the API refuses: jobs <b>wait in the ready queue</b> (back-pressure), priority first<br><br>'
           '<b>Liveness:</b> agents heartbeat every ~10 s. Three misses &rarr; mark the attempt <b>lost</b>, '
           'quarantine the machine, retry elsewhere.<br><br>'
           '<b>The subtle bug:</b> the machine was only <i>partitioned</i>, not dead. The job finishes on '
           'it <i>and</i> on the retry. <span style="color:#ff9a9a">Double execution.</span><br>'
           '&bull; <span style="color:#a8e6a3"><b>Fencing</b>: every attempt carries an epoch; the job state '
           'store and the job&rsquo;s side effects accept only the current epoch</span><br>'
           '&bull; Long jobs <b>checkpoint</b>, so a retry resumes rather than restarts</div>',
           """Deep dive one: machines you do not own.""", step=0)
seg(sid, 1, """Treat the machine A-P-I as a slow external dependency. Keep a warm pool with batch acquisition, """
            """and pre-warm it from the schedule, because unlike most bursts this one is predictable to the """
            """second.""")
seg(sid, 2, """Machines are leased from the pool with an idle timeout and released when idle, not after every """
            """job. And if the A-P-I refuses capacity, jobs wait in the ready queue by priority &mdash; that is """
            """back-pressure, and it is far better than failing them.""")
seg(sid, 3, """Liveness: agents heartbeat every ten seconds or so. Three missed beats and the attempt is marked """
            """lost, the machine is quarantined, and the job is retried elsewhere.""")
seg(sid, 4, """And here is the subtle bug. The machine was not dead, only partitioned. The job finishes there and """
            """on the retry &mdash; double execution.""")
seg(sid, 5, """The fix is fencing. Every attempt carries an epoch, and the state store &mdash; ideally the job's """
            """own side effects too &mdash; accepts results only from the current epoch. And long jobs """
            """checkpoint, so a retry resumes instead of starting over.""")

sid = beat('Deep dive 2', 'Alerting as a product &mdash; rules, routing, and the alert for silence',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Three kinds of alert, three mechanisms:</b><br>'
           '&bull; <b>Failed</b> &mdash; an event: state became FAILED after the last retry<br>'
           '&bull; <b>Too slow</b> &mdash; a timer: running longer than its timeout or SLA<br>'
           '&bull; <b>Never ran</b> &mdash; <span style="color:#ffd483">an absence</span>: expected start passed, '
           'no start recorded. Needs a <b>dead-man check</b> that knows the schedule<br><br>'
           '<b>Routing:</b> each job has an <b>owner</b> and a severity; alerts go to that team&rsquo;s channel '
           '&mdash; page, chat, email &mdash; using the notification system from lesson 7.3.<br><br>'
           '<b>Noise control:</b> group by cause (one database down = one alert, not 400), dedup repeats, '
           '<b>alert on the last retry</b>, not the first failure.<br><br>'
           '<span style="color:#a8e6a3"><b>Who watches the scheduler?</b> A canary job every minute, monitored from '
           '<i>outside</i> the scheduler. If the canary is silent, the whole system is.</span></div>',
           """Deep dive two: alerting as a product.""", step=0)
seg(sid, 1, """There are three kinds of alert, and each needs a different mechanism. Failed is an event: the """
            """state became failed after the final retry.""")
seg(sid, 2, """Too slow is a timer: the job has been running longer than its timeout or its service level.""")
seg(sid, 3, """And never ran is an absence. The expected start time passed and no start was recorded. Nothing """
            """emits an event for that, so you need a dead-man check that knows the schedule and compares """
            """expected against actual. This is the alert most designs forget, and it is the one owners care """
            """about most.""")
seg(sid, 4, """Routing: each job has an owner and a severity, and alerts go to that team's channel &mdash; page, """
            """chat or email &mdash; reusing the notification system from lesson seven point three.""")
seg(sid, 5, """Noise control: group by cause, so one database outage is one alert rather than four hundred, """
            """deduplicate repeats, and alert on the last retry rather than the first failure.""")
seg(sid, 6, """And who watches the scheduler itself? A canary job every minute, monitored from outside the """
            """scheduler. If the canary goes quiet, the whole system has, and nothing inside it would tell you.""")

tradeoff('How to get machines', [
 ('Call the machine API per job, on demand', 'info',
  ['Simple; no idle capacity'],
  ['<b>2 s and 50/s cap</b> on your scheduling throughput', 'Bursts take minutes to start',
   'API outage = scheduler outage']),
 ('Warm pool, batch acquisition, pre-warmed from the schedule', 'ok',
  ['Starts in milliseconds', '<b>Survives API slowness and brief outages</b>', 'Predictable bursts handled'],
  ['Idle machines cost money', 'Pool sizing to tune']),
 ('Fixed dedicated fleet', 'shared',
  ['Simplest operations'],
  ['Pays for peak all day', 'Ignores the API you were given']),
], 'A warm pool with batch acquisition, pre-warmed from the known schedule, released on an idle TTL.',
 'If jobs were rare and latency did not matter &mdash; a nightly batch &mdash; calling the API on demand is fine and '
 'cheaper.',
 [
 """Trade-off: how to get machines. Calling the A-P-I per job on demand is simple with no idle capacity, but it """
 """caps scheduling throughput at the A-P-I's rate, makes bursts take minutes, and turns an A-P-I outage into a """
 """scheduler outage.""",
 """A warm pool with batch acquisition, pre-warmed from the schedule, starts jobs in milliseconds and survives """
 """A-P-I slowness and brief outages. The cost is idle machines and pool sizing to tune.""",
 """A fixed dedicated fleet is simplest to operate, but pays for peak all day and ignores the A-P-I you were """
 """given.""",
 """I would take the warm pool, pre-warmed from the schedule and released on an idle timeout.""",
 """And what would flip it: rare jobs where start latency does not matter, like a nightly batch &mdash; there, """
 """on-demand calls are fine and cheaper.""",
])

failures('What happens when each piece dies', [
 ('Machine API is down', 'No new machines',
  'Warm pool keeps running jobs; ready queue absorbs the rest; <b>alert on pool exhaustion</b>, not on the API'),
 ('Executor machine dies', 'Heartbeats stop',
  'After 3 misses: attempt LOST, machine quarantined, job retried with a new epoch'),
 ('Machine partitioned, not dead', 'Job finishes twice',
  '<b>Epoch fencing</b>: only the current attempt&rsquo;s result is accepted'),
 ('Scheduler down', 'Jobs not dispatched',
  'Lesson 3.2: leases and catch-up. <b>Canary + dead-man check</b> from outside detect it'),
 ('Alert storm from one root cause', 'Hundreds of pages',
  'Group by cause and dependency; one incident, linked jobs'),
 ('Alerting pipeline itself fails', 'Failures go unreported',
  'Alerting must be monitored by a <b>separate</b> path &mdash; the canary again'),
], [
 """Failures. The machine A-P-I going down means no new machines, but the warm pool keeps jobs running and the """
 """ready queue absorbs the rest. Alert on pool exhaustion, which is the thing that actually hurts.""",
 """An executor machine dying stops heartbeats; after three misses the attempt is lost, the machine is """
 """quarantined, and the job is retried with a new epoch.""",
 """A machine that was only partitioned would finish the job twice, which epoch fencing prevents.""",
 """The scheduler going down is lesson three point two's leases and catch-up, and the canary and dead-man check """
 """from outside are how you find out.""",
 """An alert storm from one root cause is grouped into one incident with the affected jobs linked.""",
 """And if the alerting pipeline itself fails, failures go unreported, so alerting is monitored by a separate """
 """path. The canary, again.""",
])

say('What I should actually say in the room', [
 'The timing part &mdash; due-time index, leases, exactly-once claim &mdash; is the standard scheduler design, '
 'so I will cover it briefly and spend time on machines and alerts.',
 'The machine API is slow and rate-limited, so I never call it per job. A pool manager acquires machines in '
 'batches, pre-warms before predictable bursts, and releases on an idle TTL.',
 'Executors heartbeat; three misses marks the attempt lost and retries it elsewhere, and every attempt carries '
 'an epoch so a partitioned machine cannot complete a stale attempt.',
 'Job state is an explicit state machine, and every transition feeds an alert engine.',
 'There are three alerts: failed after the last retry, running too long, and never started &mdash; the last '
 'needs a dead-man check against the schedule because nothing emits an event for it.',
 'Alerts route to the job owner by severity, grouped by root cause, and a canary job monitored from outside '
 'watches the scheduler itself.',
], [
 """The sentences. The first one is the time-management move: name the part you already know and move on.""",
 """Then the machine pool, heartbeats and fencing.""",
 """Then the three alerts, with the never-started one as the highlight, and the canary to close.""",
])

followups([
 'Schedule jobs given an API to fetch machines',
 'Execute them',
 'Trigger alerts',
], [
 'The API returns machines of different sizes. How do you place jobs?',
 'A job must run on exactly one machine at a time. How do you guarantee it?',
 'A team wants to be alerted if their job runs 50% slower than usual. How?',
 'How do you stop one team&rsquo;s million jobs from starving everyone else?',
 'How do you upgrade the executor agent on 20,000 busy machines?',
],
 """The reported prompt has three verbs &mdash; schedule, execute, alert &mdash; and the lesson answers each, """
 """with the scheduling verb delegated to three point two.""",
 """The likely follow-ups. Different machine sizes means bin-packing on resource requests, best-fit with """
 """headroom. One machine at a time is the epoch fence plus a lease on the job. Fifty percent slower than """
 """usual is an anomaly rule against each job's own duration history. Starvation is per-team quotas and fair """
 """queueing in the ready queue, the same idea as lesson four point two. And upgrading agents on busy machines """
 """is a drain-then-upgrade rollout in waves, letting running jobs finish.""")

cheatsheet('Scheduler part two — the one-page card', [
 ('Requirements', 'Schedule (3.2), acquire machines via a given API, execute, alert owners'),
 ('Scale', '1M jobs/day, <b>~20k at the top of the hour</b>; machine API 2 s, 50 calls/s'),
 ('Core architecture', 'Scheduler &rarr; ready queue &rarr; dispatcher + <b>warm machine pool</b> &rarr; '
                       'executor agents &rarr; state store &rarr; alert engine'),
 ('Data store', 'Job definitions; due-time index; attempt state machine with epochs'),
 ('Partition key', 'Job id for state; time bucket for the due index (3.2)'),
 ('Cache', 'The warm pool is the cache &mdash; of machines'),
 ('Queue', 'Ready queue with priorities and per-team quotas'),
 ('Consistency', 'One current attempt per job, enforced by <b>epoch fencing</b>'),
 ('Failure handling', 'Heartbeats, quarantine, retry; back-pressure when the API refuses'),
 ('Key deep dives', 'Machine pool, heartbeats and fencing &middot; three alert types and the dead-man check'),
 ('Biggest trade-off', 'Idle cost vs start latency &mdash; <b>pre-warm from the schedule</b>'),
], [
 """The card. The scale row has the burst and the A-P-I limits that force the warm pool.""",
 """The consistency row is epoch fencing.""",
 """And the trade-off: idle cost against start latency, resolved by pre-warming from a schedule you already """
 """know.""",
])

say('The 60-second answer', [
 'Timing is the standard part &mdash; a due-time index with leases and an exactly-once claim &mdash; so I '
 'reuse that and focus on machines and alerts.',
 'The machine API is slow and rate-limited, so a pool manager acquires machines in batches, pre-warms before '
 'the top-of-hour burst the schedule predicts, and releases idle machines on a TTL. If the API refuses, jobs '
 'wait in a priority queue with per-team quotas.',
 'Executor agents heartbeat; three misses mark the attempt lost and it is retried elsewhere with a new epoch, '
 'so a partitioned machine can never complete a stale attempt.',
 'Every job state change feeds an alert engine with three rule types: failed after final retry, exceeded its '
 'timeout, and never started &mdash; which needs a dead-man check against the schedule.',
 'Alerts route to the owning team by severity, grouped by root cause, and a canary job monitored from outside '
 'tells us if the scheduler itself has gone quiet.',
], [
 """The sixty-second answer. The never-started alert is the detail that most candidates miss and every """
 """interviewer remembers.""",
 """And opening by reusing the standard scheduler shows judgement about where the time should go.""",
], kicker='60-second interview answer')
