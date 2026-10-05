# -*- coding: utf-8 -*-
"""Chapter 10 — the patterns, and how to recognise them in a new question."""
from lib import *

lesson_header('10.1', 'Patterns you should recognise &mdash; and how to spot them',
              'Seven reusable shapes, and the tell that identifies each one',
              None, 22,
              """Chapter ten, and the last lesson. This is not a summary &mdash; summarising twenty-one """
              """designs would be useless, because you will not be asked any of them verbatim. What """
              """transfers is the shapes underneath them. There are seven, they recur constantly, and """
              """each one has a <i>tell</i> &mdash; a phrase in the question that identifies it. Learn """
              """the tells and a question you have never seen stops being a blank page.""")

sid = beat('How to use this', 'Pattern-matching is not cheating. It is what experience <i>is</i>.',
           '<div style="font-size:29px;line-height:1.75">'
           'A Staff engineer does not derive every system from first principles in forty minutes. They '
           'recognise the shape, apply the known solution, and <b>spend their time on what is '
           'different about this one</b>.<br><br>'
           'So the method for a new question is:<br><br>'
           '<b>1.</b> Listen for the tell &rarr; name the pattern<br>'
           '<b>2.</b> Apply the known skeleton &mdash; fast, and out loud<br>'
           '<b>3.</b> Then ask: <i>what about this question breaks the standard answer?</i><br>'
           '<b>4.</b> Spend the remaining time there<br><br>'
           '<span style="color:#ffd483">Step 3 is the interview. Steps 1 and 2 just buy you the time '
           'to get to it.</span><br><br>'
           '<span style="color:#a8e6a3">The seven patterns, and where you met each one:</span></div>',
           """How to use this chapter. A Staff engineer does not derive every system from first """
           """principles in forty minutes. They recognise the shape, apply the known solution quickly, """
           """and spend their time on what is different about this particular one.""", step=0)
seg(sid, 1, """So the method for a question you have never seen is four steps. Listen for the tell and """
            """name the pattern. Apply the known skeleton, fast and out loud. Then ask what about this """
            """question breaks the standard answer. And spend the remaining time there.""")
seg(sid, 2, """Step three is the interview. Steps one and two simply buy you the time to reach it. If you """
            """spend thirty minutes carefully deriving a standard inverted index, you never get to the """
            """part where you would have shown judgement.""")

sid = beat('Pattern 1', 'Precompute vs compute on demand &mdash; decided by the read/write ratio',
           '<div style="font-size:26px;line-height:1.65">'
           '<b>The tell:</b> &ldquo;show the user a list of things derived from other things&rdquo;. '
           'Feeds, timelines, recommendations, search results, dashboards.<br><br>'
           '<b>The skeleton:</b> compute the ratio. Do the work on the <i>rarer</i> operation.<br>'
           '&bull; Reads &gg; writes &rarr; <b>precompute on write</b> (fanout, materialised views, '
           'cached top-K)<br>'
           '&bull; Writes &ge; reads, or personalised &rarr; <b>compute on read</b><br><br>'
           '<b>What breaks it:</b> a <b>skewed distribution</b>. Precomputing is affordable on average '
           'and catastrophic in the tail &mdash; one celebrity, one hot key, one huge tenant.<br>'
           '<b>The fix is always the same:</b> split the distribution and use a different strategy for '
           'each part.<br><br>'
           '<span style="color:#a8e6a3">Where you met it: news feed (7.1, celebrity), typeahead '
           '(2.2/5.3, personalisation kills the cache), job recs (9.1, offline candidates + online '
           'ranking), top-N (4.3).</span><br><br>'
           '<span style="color:#ffd483">Say the ratio out loud. It turns an opinion into a '
           'derivation.</span></div>',
           """Pattern one: precompute versus compute on demand, decided by the read-write ratio.""",
           step=0)
seg(sid, 1, """The tell is a question that asks you to show a user a list of things derived from other """
            """things. Feeds, timelines, recommendations, search results, dashboards. Whenever the """
            """answer is assembled rather than stored, this pattern applies.""")
seg(sid, 2, """The skeleton: compute the ratio, and do the work on the rarer operation. If reads vastly """
            """outnumber writes, precompute on write. If writes are comparable, or the answer is """
            """personalised so there is nothing shared to precompute, compute on read.""")
seg(sid, 3, """What breaks it is a skewed distribution. Precomputing is affordable on average and """
            """catastrophic in the tail &mdash; one celebrity, one hot key, one enormous tenant. And """
            """the fix is always the same: split the distribution and use a different strategy for each """
            """part. That is what the hybrid feed is, and it is also what splitting a hot counter """
            """is.""")
seg(sid, 4, """You met this in the news feed with celebrities, in typeahead where personalisation """
            """destroys the shared cache, in job recommendations as offline candidates with online """
            """ranking, and in top-N. Four questions, one decision.""")

sid = beat('Pattern 2', 'Store events, derive state',
           '<div style="font-size:26px;line-height:1.65">'
           '<b>The tell:</b> the question mentions <b>history, replay, audit, or &ldquo;what happened '
           'at time T&rdquo;</b>. Or anything where a late-arriving fact must change a past '
           'conclusion.<br><br>'
           '<b>The skeleton:</b> an append-only log is the source of truth; current state is a '
           '<i>derived</i>, rebuildable view.<br>'
           '&bull; Current state = the log folded up<br>'
           '&bull; History = the log itself<br>'
           '&bull; <b>Snapshots</b> bound how far you must replay &mdash; for reads <i>and</i> for '
           'recovery<br><br>'
           '<b>Why it keeps winning:</b> you can always rebuild the derived thing, so every failure '
           'downstream is a <i>delay</i> rather than a loss.<br><br>'
           '<b>What breaks it:</b> unbounded log growth &rarr; compaction, and compaction brings write '
           'amplification and the need for free space to reclaim free space.<br><br>'
           '<span style="color:#a8e6a3">Where you met it: disk KV store (6.1), CoderPad replay (8.1), '
           'logistics scans (8.2), quota counters rebuilt from the usage log (4.2), feed timelines as '
           'derived data (7.1).</span></div>',
           """Pattern two: store events, derive state.""", step=0)
seg(sid, 1, """The tell is a question that mentions history, replay, audit, or &ldquo;what happened at """
            """time T&rdquo;. Or anything where a late-arriving fact has to change a conclusion you """
            """already reached.""")
seg(sid, 2, """The skeleton: an append-only log is the source of truth, and current state is a derived, """
            """rebuildable view. Current state is the log folded up; history is the log itself; and """
            """snapshots bound how far you have to replay &mdash; for reads and, importantly, for """
            """recovery.""")
seg(sid, 3, """Why it keeps winning is that you can always rebuild the derived thing. Which means every """
            """downstream failure becomes a delay rather than a loss, and that single property is worth """
            """an enormous amount operationally.""")
seg(sid, 4, """What breaks it is unbounded log growth, so you need compaction &mdash; and compaction """
            """brings write amplification, and the awkward fact that you need free space in order to """
            """reclaim free space.""")
seg(sid, 5, """You met this in the disk key-value store, in CoderPad replay, in logistics scan events, in """
            """quota counters rebuilt from the usage log, and in feed timelines as derived data. Five """
            """questions, one inversion.""")

sid = beat('Pattern 3', 'Generate candidates cheaply, then rank',
           '<div style="font-size:26px;line-height:1.65">'
           '<b>The tell:</b> &ldquo;return the best <b>N</b> out of <b>millions</b>&rdquo; &mdash; with '
           'a latency budget.<br><br>'
           '<b>The skeleton &mdash; a funnel, where each stage buys the next its budget:</b><br>'
           '&bull; <b>Generate</b>: millions &rarr; ~1,000. Cheap, precomputed, optimised for '
           '<i>recall</i>. Use <b>several sources</b>, because each has a different blind spot<br>'
           '&bull; <b>Filter</b>: hard constraints. Binary, non-negotiable, before the model<br>'
           '&bull; <b>Rank</b>: expensive model &mdash; affordable only because the set is now small<br>'
           '&bull; <b>Re-rank</b>: diversity, freshness, business rules<br><br>'
           '<b>The arithmetic that forces it:</b> 10M candidates &times; 1 ms = 3 hours. State it; it '
           'makes the funnel inevitable rather than optional.<br><br>'
           '<b>What breaks it:</b> the ranker never sees what generation missed. '
           '<span style="color:#ffd483">Recall failures are invisible &mdash; you cannot see what was '
           'never retrieved.</span><br><br>'
           '<span style="color:#a8e6a3">Where you met it: job recs (9.1), typeahead ranking (5.3), feed '
           'ranking (7.1), spell-check suggestions (5.1).</span></div>',
           """Pattern three: generate candidates cheaply, then rank.""", step=0)
seg(sid, 1, """The tell is &ldquo;return the best N out of millions&rdquo;, with a latency budget """
            """attached.""")
seg(sid, 2, """The skeleton is a funnel where each stage buys the next one its budget. Generate takes """
            """millions down to about a thousand &mdash; cheap, precomputed, optimised for recall """
            """rather than precision &mdash; and you use several sources, because each has a different """
            """blind spot. Filter applies hard binary constraints before the model. Rank runs the """
            """expensive model on what survives. And re-rank applies diversity and business rules.""")
seg(sid, 3, """The arithmetic that forces it: ten million candidates at a millisecond each is three """
            """hours. State that number and the funnel becomes inevitable rather than a design """
            """preference.""")
seg(sid, 4, """What breaks it is that the ranker never sees what candidate generation missed. And recall """
            """failures are invisible &mdash; you cannot see what was never retrieved, so the system """
            """looks fine while quietly failing. That is why multiple generation sources matter more """
            """than a better ranker.""")
seg(sid, 5, """You met this in job recommendations, typeahead ranking, feed ranking and spell-check """
            """suggestions.""")

sid = beat('Pattern 4', 'Distribute the decision, do not centralise the check',
           '<div style="font-size:26px;line-height:1.65">'
           '<b>The tell:</b> a check that must happen on <b>every request</b> across a <b>large '
           'fleet</b> &mdash; rate limits, permissions, denylists, feature flags, config.<br><br>'
           '<b>The arithmetic:</b> N requests/s &times; one network call = a central service that is '
           'bigger than everything it protects, and on the critical path of all of it.<br><br>'
           '<b>The skeleton:</b><br>'
           '&bull; Evaluate <b>locally</b>, in process<br>'
           '&bull; <b>Push</b> a signed, <b>versioned</b> bundle to every node<br>'
           '&bull; Node detects a version gap &rarr; <b>pulls</b> to self-heal<br>'
           '&bull; Alert on <b>data age at the node</b>, never on whether the push job succeeded<br>'
           '&bull; <span style="color:#ffd483">Push for latency, pull for correctness. The version '
           'number is what lets you have both.</span><br><br>'
           '<b>What breaks it:</b> staleness. So ask for the staleness budget &mdash; it decides '
           'everything &mdash; and note that <b>removals usually need to propagate faster than '
           'additions</b>, because the cost of being late is asymmetric.<br><br>'
           '<span style="color:#a8e6a3">Where you met it: IP denylist (4.4), service permissions (9.4), '
           'rate limiter config (4.1), spell-check dictionary updates (5.1).</span></div>',
           """Pattern four: distribute the decision, do not centralise the check.""", step=0)
seg(sid, 1, """The tell is a check that must happen on every request across a large fleet &mdash; rate """
            """limits, permissions, denylists, feature flags, configuration.""")
seg(sid, 2, """The arithmetic kills the obvious design immediately. N requests a second times one """
            """network call gives you a central service bigger than everything it protects, sitting on """
            """the critical path of all of it.""")
seg(sid, 3, """So the skeleton: evaluate locally in process. Push a signed, versioned bundle to every """
            """node. When a node detects a version gap, it pulls to self-heal. And alert on data age at """
            """the node rather than on whether the push job succeeded &mdash; because the job can """
            """succeed while a thousand nodes sit on a stale bundle.""")
seg(sid, 4, """The phrase to remember is push for latency, pull for correctness, and the version number """
            """is what lets you have both.""")
seg(sid, 5, """What breaks it is staleness, so ask for the staleness budget &mdash; it decides the whole """
            """architecture. And note that removals usually need to propagate faster than additions, """
            """because the cost of being late is asymmetric: a late add means an attacker gets a few """
            """more seconds, a late removal means an innocent user stays blocked.""")
seg(sid, 6, """You met this in the I-P denylist, service permissions, rate limiter configuration and """
            """spell-check dictionary updates.""")

sid = beat('Pattern 5', 'Two access patterns, two stores, one stream',
           '<div style="font-size:26px;line-height:1.65">'
           '<b>The tell:</b> the question asks for <b>both</b> &ldquo;what is the current '
           'state?&rdquo; <b>and</b> &ldquo;what happened over time?&rdquo; &mdash; or mixes a hot '
           'small query with a cold huge one.<br><br>'
           '<b>Why one store cannot serve both:</b> they disagree about <b>mutability</b> (overwritten '
           'vs append-only) and <b>size</b> (megabytes vs terabytes). Compromise and you get a '
           'current-state query that scans history, or a history store you keep mutating.<br><br>'
           '<b>The skeleton:</b> one ingest stream, fanned out to purpose-built stores. Each one '
           'optimised for its own question; each one independently failing.<br><br>'
           '<b>The bonus:</b> failure isolation falls out free. In host health, the history store dying '
           'does not affect alerting &mdash; <i>because they are different stores</i>.<br><br>'
           '<b>What breaks it:</b> consistency between the stores. <b>Name which one is the source of '
           'truth</b>, and make the others rebuildable from it.<br><br>'
           '<span style="color:#a8e6a3">Where you met it: host health (9.2, current vs history), quota '
           '(4.2, enforcement vs accounting), logging (6.3, hot indexed vs cold raw), photos (6.2, '
           'bytes vs metadata), InMail (7.2, message vs per-recipient state).</span></div>',
           """Pattern five: two access patterns, two stores, one stream.""", step=0)
seg(sid, 1, """The tell is a question that asks for both &ldquo;what is the current state&rdquo; and """
            """&ldquo;what happened over time&rdquo; &mdash; or that mixes a hot small query with a """
            """cold enormous one.""")
seg(sid, 2, """One store cannot serve both, because they disagree about mutability and about size. One """
            """is overwritten and tiny; the other is append-only and vast. Compromise and you get """
            """either a current-state query that scans history, or a history store you keep """
            """mutating.""")
seg(sid, 3, """The skeleton is one ingest stream fanned out to purpose-built stores, each optimised for """
            """its own question and each failing independently.""")
seg(sid, 4, """And the bonus is that failure isolation falls out for free. In host health, the history """
            """store dying does not affect alerting &mdash; not because you engineered a fallback, but """
            """because they are different stores. Structure giving you reliability without extra work """
            """is worth noticing.""")
seg(sid, 5, """What breaks it is consistency between the stores, so name which one is the source of """
            """truth and make the others rebuildable from it. You met this in host health, quotas, """
            """logging, photos and InMail.""")

sid = beat('Pattern 6', 'The log as a shock absorber',
           '<div style="font-size:26px;line-height:1.65">'
           '<b>The tell:</b> a producer you <b>do not control</b> feeding a consumer that can be slow '
           '&mdash; especially if volume <b>spikes exactly when things go wrong</b>.<br><br>'
           '<b>The skeleton:</b> a durable, partitioned, retained log between them.<br>'
           '&bull; Producers never block on consumers<br>'
           '&bull; Retention (say 24 h) means a consumer can be <b>down for hours</b> and lose nothing<br>'
           '&bull; Several independent consumers, each with its own offset<br>'
           '&bull; Partition key gives you <b>ordering within a key</b> and parallelism across keys<br>'
           '<br>'
           '<b>And the question it forces you to answer:</b> what happens when the buffer is full?<br>'
           '&bull; <b>Never block the producer</b> if the producer is serving users<br>'
           '&bull; Decide the <b>drop order in advance</b> &mdash; by severity, by priority<br>'
           '&bull; <span style="color:#ffd483">Always count what you dropped. Silent loss is far worse '
           'than visible loss.</span><br><br>'
           '<span style="color:#a8e6a3">Where you met it: logging (6.3), message queue (3.3), top-N '
           'sketches (4.3), photo processing (6.2), notifications (7.3), quota usage events '
           '(4.2).</span></div>',
           """Pattern six: the log as a shock absorber.""", step=0)
seg(sid, 1, """The tell is a producer you do not control feeding a consumer that can be slow &mdash; and """
            """especially a producer whose volume spikes exactly when things go wrong. Logs are the """
            """clearest case: an application in trouble logs a hundred times more.""")
seg(sid, 2, """The skeleton is a durable, partitioned, retained log between them. Producers never block """
            """on consumers. Retention of say twenty-four hours means a consumer can be down for hours """
            """and lose nothing. Several independent consumers each track their own offset. And the """
            """partition key gives you ordering within a key and parallelism across keys.""")
seg(sid, 3, """And it forces you to answer one question that candidates often skip: what happens when """
            """the buffer is full?""")
seg(sid, 4, """Never block the producer if the producer is serving users &mdash; that is how an """
            """observability system takes down the service it monitors. Decide the drop order in """
            """advance, by severity or priority, rather than discovering it during an incident. And """
            """always count what you dropped, because silent loss is far worse than visible loss: """
            """somebody will spend an outage looking for a log line that was never written and conclude """
            """the code never ran.""")
seg(sid, 5, """You met this in logging, the message queue, top-N sketch shipping, photo processing, """
            """notifications and quota usage events.""")

sid = beat('Pattern 7', 'Shared object, per-participant state',
           '<div style="font-size:26px;line-height:1.65">'
           '<b>The tell:</b> several people interact with <b>one thing</b>, and each has their '
           '<i>own</i> relationship to it &mdash; read, archived, accepted, dismissed, muted.<br><br>'
           '<b>The mistake:</b> putting the state on the shared object. '
           '<span style="color:#ff9a9a">One <code>read</code> boolean cannot hold two people&rsquo;s '
           'state, let alone eight.</span><br><br>'
           '<b>The skeleton:</b><br>'
           '&bull; The object is <b>shared and immutable</b><br>'
           '&bull; A row per <code>(participant, object)</code> holds <i>their</i> state<br>'
           '&bull; Partition by <b>participant</b>, so one person&rsquo;s whole view is single-shard<br>'
           '&bull; Aggregates (unread counts) are <b>maintained incrementally</b>, never computed with '
           'COUNT(*) &mdash; and <b>they will drift, so design the reconciliation</b><br><br>'
           '<b>What it explains:</b> why deletion is per-participant (I delete, you still have it), and '
           'why GDPR erasure is genuinely hard &mdash; erasing my data must not erase your copy of a '
           'conversation we both had.<br><br>'
           '<span style="color:#a8e6a3">Where you met it: InMail (7.2), calendar invitations (8.3), '
           'notifications (7.3), in-app notification centre.</span></div>',
           """Pattern seven: shared object, per-participant state.""", step=0)
seg(sid, 1, """The tell is that several people interact with one thing, and each has their own """
            """relationship to it &mdash; read, archived, accepted, dismissed, muted.""")
seg(sid, 2, """The mistake is putting that state on the shared object. One read boolean cannot hold two """
            """people's state, let alone eight, and it fails the moment you add a second """
            """participant.""")
seg(sid, 3, """The skeleton: the object is shared and immutable, and a row per participant per object """
            """holds their state. Partition by participant so one person's entire view is single-shard. """
            """And aggregates like unread counts are maintained incrementally rather than computed with """
            """a count &mdash; and they will drift, so design the reconciliation rather than just the """
            """increment.""")
seg(sid, 4, """And this pattern explains two things that otherwise look like edge cases. Why deletion is """
            """per participant &mdash; I delete a conversation and you still have it. And why G-D-P-R """
            """erasure is genuinely hard, because erasing my data must not erase your copy of a """
            """conversation we both participated in.""")
seg(sid, 5, """You met this in InMail, calendar invitations, notifications and the in-app notification """
            """centre.""")

sid = beat('The tells, in one table', 'What to listen for, and what to reach for',
           '<div style="font-size:24px;line-height:1.6">'
           '<table style="width:100%;border-collapse:collapse">'
           '<tr><td style="padding:7px 10px;color:#ffd483"><b>&ldquo;show the user a list of&hellip;&rdquo;</b></td>'
           '<td style="padding:7px 10px">Precompute vs on-demand &rarr; <b>compute the read/write ratio</b></td></tr>'
           '<tr><td style="padding:7px 10px;color:#ffd483"><b>&ldquo;replay / history / audit / at time T&rdquo;</b></td>'
           '<td style="padding:7px 10px">Event log is truth, state is derived</td></tr>'
           '<tr><td style="padding:7px 10px;color:#ffd483"><b>&ldquo;best N out of millions&rdquo;</b></td>'
           '<td style="padding:7px 10px">Candidate generation &rarr; filter &rarr; rank</td></tr>'
           '<tr><td style="padding:7px 10px;color:#ffd483"><b>&ldquo;every request / every server&rdquo;</b></td>'
           '<td style="padding:7px 10px">Local evaluation + versioned push with pull fallback</td></tr>'
           '<tr><td style="padding:7px 10px;color:#ffd483"><b>&ldquo;current state AND history&rdquo;</b></td>'
           '<td style="padding:7px 10px">Two stores, one stream</td></tr>'
           '<tr><td style="padding:7px 10px;color:#ffd483"><b>&ldquo;spikes / bursty / untrusted producer&rdquo;</b></td>'
           '<td style="padding:7px 10px">Durable log as a buffer + an explicit drop policy</td></tr>'
           '<tr><td style="padding:7px 10px;color:#ffd483"><b>&ldquo;multiple people, one item&rdquo;</b></td>'
           '<td style="padding:7px 10px">Shared object + per-participant state rows</td></tr>'
           '<tr><td style="padding:7px 10px;color:#a8e6a3"><b>&ldquo;exactly / must not be wrong&rdquo;</b></td>'
           '<td style="padding:7px 10px">Idempotency key from the <b>client</b>, and one atomic op</td></tr>'
           '<tr><td style="padding:7px 10px;color:#a8e6a3"><b>&ldquo;one key is very popular&rdquo;</b></td>'
           '<td style="padding:7px 10px">Split into sub-keys and sum, or replicate rather than shard</td></tr>'
           '</table></div>',
           """Here are the tells in one table, and this is the slide to photograph. Left column is what """
           """you hear in the question; right column is what you reach for.""", step=0)
seg(sid, 1, """Show the user a list of things, derived from other things &mdash; compute the read-write """
            """ratio. Replay, history, audit, or what happened at time T &mdash; event log is truth, """
            """state is derived. Best N out of millions &mdash; the funnel.""")
seg(sid, 2, """Every request or every server &mdash; local evaluation with a versioned push and a pull """
            """fallback. Current state and history together &mdash; two stores, one stream. Spiky or """
            """untrusted producers &mdash; a durable log as a buffer with an explicit drop policy. """
            """Multiple people interacting with one item &mdash; shared object with per-participant """
            """state.""")
seg(sid, 3, """And two more that are not full patterns but recur constantly. &ldquo;Exactly&rdquo; or """
            """&ldquo;must not be wrong&rdquo; means an idempotency key generated by the client, and a """
            """single atomic operation. And &ldquo;one key is very popular&rdquo; means split it into """
            """sub-keys and sum, or replicate the whole thing rather than sharding it.""")

sid = beat('The three questions that work on anything', 'When you genuinely do not recognise it',
           '<div style="font-size:27px;line-height:1.7">'
           'Sometimes no pattern fits. These three still work:<br><br>'
           '<b>1. &ldquo;What is the read/write ratio, and what is the biggest single number here?&rdquo;</b><br>'
           '<span style="color:#a8e6a3">Arithmetic decides more design questions than taste does. The '
           'biggest number is usually the constraint &mdash; bytes for photos, latency for typeahead, '
           'fanout for feeds.</span><br><br>'
           '<b>2. &ldquo;What is the cost of being wrong, in each direction?&rdquo;</b><br>'
           '<span style="color:#a8e6a3">Asymmetry drives design. Late add vs late remove. Dropped '
           'notification vs annoying one. Over-counting a quota vs rejecting a request. The expensive '
           'direction gets the engineering.</span><br><br>'
           '<b>3. &ldquo;What is this allowed to be wrong about, and for how long?&rdquo;</b><br>'
           '<span style="color:#a8e6a3">This is the consistency question in a form the interviewer can '
           'actually answer. Nobody says &ldquo;I want linearizability&rdquo;; everybody can say '
           '&ldquo;30 seconds stale is fine&rdquo;.</span><br><br>'
           '<span style="color:#ffd483">All three convert a vague question into a decision with a '
           'stated cost. That conversion <i>is</i> the Staff-level skill.</span></div>',
           """And when no pattern fits &mdash; which will happen &mdash; three questions still """
           """work.""", step=0)
seg(sid, 1, """One: what is the read-write ratio, and what is the biggest single number here? Arithmetic """
            """decides more design questions than taste does, and the biggest number is usually the """
            """constraint. Bytes for photos, latency for typeahead, fanout for feeds. Find it and the """
            """design argues for itself.""")
seg(sid, 2, """Two: what is the cost of being wrong, in each direction? Asymmetry drives design. A late """
            """add versus a late removal. A dropped notification versus an annoying one. Over-counting """
            """a quota versus rejecting a legitimate request. The expensive direction is where the """
            """engineering goes.""")
seg(sid, 3, """Three: what is this allowed to be wrong about, and for how long? That is the consistency """
            """question asked in a form the interviewer can actually answer. Nobody says &ldquo;I want """
            """linearizability&rdquo;. Everybody can say &ldquo;thirty seconds stale is fine&rdquo;, and """
            """that answer will shape half your design.""")
seg(sid, 4, """All three convert a vague question into a decision with a stated cost. And that """
            """conversion is the staff-level skill &mdash; more than any architecture you could """
            """memorise.""")

sid = beat('Senior vs Staff', 'The same diagram, said differently',
           '<div style="font-size:25px;line-height:1.6">'
           '<table style="width:100%;border-collapse:collapse">'
           '<tr><td style="width:46%;padding:8px 12px;color:#9fd1ff"><b>Senior</b></td>'
           '<td style="padding:8px 12px;color:#a8e6a3"><b>Staff</b></td></tr>'
           '<tr><td style="padding:8px 12px">Builds the right architecture</td>'
           '<td style="padding:8px 12px">Builds it, and says <b>what they are not building, and why '
           'that is safe</b></td></tr>'
           '<tr><td style="padding:8px 12px">&ldquo;I would use Kafka here&rdquo;</td>'
           '<td style="padding:8px 12px">&ldquo;Kafka, because producers must not block on consumers '
           '&mdash; and <b>here is what would make me drop it</b>&rdquo;</td></tr>'
           '<tr><td style="padding:8px 12px">Handles the failure when asked</td>'
           '<td style="padding:8px 12px">Names the failure that will <i>actually</i> happen, which is '
           'usually <b>not the one being asked about</b></td></tr>'
           '<tr><td style="padding:8px 12px">Scales the system</td>'
           '<td style="padding:8px 12px">Says where it <b>stops</b> scaling, and what they would build '
           'instead</td></tr>'
           '<tr><td style="padding:8px 12px">Answers the question</td>'
           '<td style="padding:8px 12px">Notices when the question is <b>ambiguous or '
           'self-contradictory</b>, and says so</td></tr>'
           '<tr><td style="padding:8px 12px">Optimises</td>'
           '<td style="padding:8px 12px">Asks <b>what we are optimising for</b> &mdash; and makes the '
           'choice falsifiable</td></tr>'
           '</table><br>'
           '<span style="color:#ffd483">Notice: not one row is about knowing more technology.</span>'
           '</div>',
           """Senior versus Staff, which is really the same diagram said differently.""", step=0)
seg(sid, 1, """A senior engineer builds the right architecture. A staff engineer builds it and says what """
            """they are deliberately not building, and why that is safe.""")
seg(sid, 2, """Senior says &ldquo;I would use Kafka here&rdquo;. Staff says &ldquo;Kafka, because """
            """producers must not block on consumers &mdash; and here is what would make me drop """
            """it&rdquo;. The condition that would change your mind is what turns a preference into """
            """engineering.""")
seg(sid, 3, """Senior handles the failure when asked. Staff names the failure that will actually happen """
            """&mdash; which is usually not the one being asked about. In the denylist question it is """
            """not the attack, it is you blocking a carrier N-A-T. In notifications it is not a provider """
            """outage, it is a bug sending ten million messages.""")
seg(sid, 4, """Senior scales the system. Staff says where it stops scaling and what they would build """
            """instead &mdash; a billion keys for the K-V store, five hundred participants for the """
            """messaging model.""")
seg(sid, 5, """Senior answers the question. Staff notices when the question is ambiguous or """
            """self-contradictory and says so &mdash; the spell checker's own example contradicts its """
            """description, and the logistics requirements are four adjectives.""")
seg(sid, 6, """And senior optimises; staff asks what we are optimising for, and makes the choice """
            """falsifiable. Now look down that right-hand column: not a single row is about knowing """
            """more technology. That is the whole message of this course.""")

cheatsheet('The course, on one card', [
 ('The method', 'Clarify &rarr; requirements &rarr; capacity &rarr; architecture &rarr; deep dives '
                '&rarr; trade-offs &rarr; failures &rarr; evolution. <b>Lesson 1.1</b>'),
 ('Open with', 'The read/write ratio, or the biggest number. <b>Make the arithmetic decide</b>'),
 ('Pattern 1', 'Precompute vs on-demand &mdash; the ratio decides; <b>the tail breaks it</b>'),
 ('Pattern 2', 'Store events, derive state &mdash; history, replay, audit, late-arriving facts'),
 ('Pattern 3', 'Generate &rarr; filter &rarr; rank &mdash; best N of millions under a budget'),
 ('Pattern 4', 'Local evaluation + versioned push, pull on gap &mdash; checks on every request'),
 ('Pattern 5', 'Two access patterns &rarr; two stores, one stream'),
 ('Pattern 6', 'Durable log as a buffer &mdash; and an <b>explicit drop policy</b>'),
 ('Pattern 7', 'Shared object + per-participant state &mdash; and maintained, reconciled aggregates'),
 ('Always ask', 'What is it allowed to be wrong about, and for how long?'),
 ('Always say', 'What you are <b>not</b> building, and what would change your mind'),
 ('Never', 'Shard before you check it fits; reach for OT/CRDT before checking the writer count; '
           'put a model on a latency-critical path without a timeout'),
], [
 """The whole course on one card. The method from lesson one point one, and the habit of opening with """
 """the ratio or the biggest number so the arithmetic decides rather than your taste.""",
 """Then the seven patterns, each in one line. If you remember nothing else from twenty-two lessons, """
 """remember these seven and the tells that identify them.""",
 """Then the two habits: always ask what the system is allowed to be wrong about and for how long, and """
 """always say what you are not building and what would change your mind.""",
 """And the three nevers, which are the specific mistakes this course has watched people make. Do not """
 """shard before checking whether it fits &mdash; three separate questions in this course needed no """
 """partitioning at all. Do not reach for operational transformation before counting the writers. And """
 """never put a model on a latency-critical path without a timeout and a fallback.""",
])

say('The last thing I would say', [
 'You will not get a question from this course. You will get something adjacent, and the useful '
 'question is not &ldquo;do I know this system&rdquo; but &ldquo;which shape is this?&rdquo;',
 'Name the pattern out loud. It tells the interviewer you have seen the shape before, and it buys you '
 'the time to get to the part that is actually interesting.',
 'Then find what is different. Every question in this course had one thing that broke the standard '
 'answer &mdash; the celebrity, the offline scanner, the daylight saving change, the interviewer who '
 'cannot edit.',
 'Spend your time there. That is the whole interview.',
 'And when you are stuck: what is the ratio, what does it cost to be wrong in each direction, and what '
 'is this allowed to be wrong about and for how long?',
], [
 """And the last thing I would say. You will not get a question from this course &mdash; you will get """
 """something adjacent. So the useful question is never &ldquo;do I know this system&rdquo;, it is """
 """&ldquo;which shape is this?&rdquo;""",
 """Name the pattern out loud, because it tells the interviewer you have seen the shape before and it """
 """buys you the time to reach the interesting part. Then find what is different &mdash; every single """
 """question in this course had one thing that broke the standard answer. The celebrity. The offline """
 """scanner. The daylight saving change. The interviewer who cannot edit.""",
 """Spend your time there, because that is the whole interview. And when you are genuinely stuck, fall """
 """back on the three questions: what is the ratio, what does it cost to be wrong in each direction, """
 """and what is this allowed to be wrong about and for how long. Good luck.""",
], kicker='Closing')
