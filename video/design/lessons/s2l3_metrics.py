# -*- coding: utf-8 -*-
"""Chapter 2, Lesson 3 — design a metrics gathering and aggregation system."""
from lib import *

lesson_header('2.3', 'Design a metrics gathering and aggregation system',
              'High-cardinality ingestion &middot; time series &middot; alerting at scale',
              dict(reports='3 independent candidate reports',
                   latest='September 2025', level='Senior SWE and unspecified',
                   conf='HIGH &mdash; upgraded in research pass 3',
                   sources='Blind &times;2, Glassdoor'), 34,
              """Chapter two, lesson three: a metrics gathering and aggregation system. This question is """
              """here because of something the research turned up. In our earlier pass it was a weak """
              """single source and I had it marked low confidence. This pass found two more independent """
              """first-hand reports — including a candidate stating plainly that they were asked to design """
              """a metric aggregator — which puts it level with typeahead at three reports. It is also """
              """described as a normal question for both software and infrastructure candidates, which """
              """matters given the team you are interviewing with.""")

evidence('Where this question comes from', [
 ('Blind &mdash; System and Infrastructure interview thread', 'Sep 2025', 'unspecified',
  'A candidate states directly: <b>&ldquo;they asked me metric aggregator&rdquo;</b>'),
 ('Blind &mdash; onsite system design review', '2025&ndash;2026', 'Senior SWE, applications',
  'Describes a <b>metrics gathering system</b> as a normal question for both SWE and '
  'Infrastructure candidates: collect, store in a time-series database, render, alert'),
 ('Glassdoor &mdash; interview reports', '2025&ndash;2026', 'SWE',
  'Metrics collection with time-series storage and alerting'),
], """The evidence, and I want to show my working because this one changed. Three independent sources. """
     """A Blind thread from September twenty twenty-five where a candidate says directly that they were """
     """asked to design a metric aggregator.""",
 ["""A separate Blind onsite review describing a metrics gathering system as a normal question for both """
  """software engineering and infrastructure candidates, with the expected scope being collection, """
  """storage in a time-series database, rendering, and alerting on top. And Glassdoor reports """
  """describing the same thing.""",
  """Three sources, none derived from each other. In research pass two I had this marked low confidence """
  """on one weak source; finding two more independent reports is what moved it to high. I am telling """
  """you that because you should know how firm each recommendation in this course actually is."""],
 caveat='Note the honest limit: Blind and Glassdoor both block direct fetching, so these were read '
        'through search summaries rather than the original threads. Graded accordingly.',
 narration_caveat="""And the honest limit on all of this: Blind and Glassdoor both block automated """
                  """fetching, so these were read through search summaries rather than the original """
                  """threads. That is weaker than reading a candidate's own words in full, and I have """
                  """graded it accordingly rather than pretending otherwise.""")

sid = beat('Why this is interesting', 'The thing that kills you is not throughput',
           '<div class="bigidea">Every metrics platform that has ever fallen over fell over because of '
           '<b>cardinality</b>, not because of request volume.</div>'
           '<div style="margin-top:26px;font-size:28px;line-height:1.7">'
           'Two hundred thousand points a second sounds frightening and is genuinely routine &mdash; it '
           'is a well-understood ingestion problem with well-understood answers.<br><br>'
           'Then one engineer adds a label:<br>'
           '<span style="font-family:JetBrains Mono,monospace;font-size:24px;color:#ff8f8f">'
           'http_requests{path="/user/12345", user_id="12345"}</span><br><br>'
           'and your two million series becomes <b>two hundred million</b> overnight. Memory explodes, '
           'the index stops fitting, queries time out, and the system that watches everything else '
           '<b>goes down first.</b><br><br>'
           '<span style="color:#ffd483">Say that in the interview and you have shown you have operated '
           'one of these.</span></div>',
           """Why is this question interesting? Because the thing that kills a metrics platform is not """
           """throughput, and almost every candidate designs against throughput.""", step=0)
seg(sid, 1, """Two hundred thousand points a second sounds frightening and is genuinely routine. It is a """
            """well-understood ingestion problem with well-understood answers, and we will design it in a """
            """few minutes.""")
seg(sid, 2, """Then one engineer, with entirely good intentions, adds a label — a user id, or a full URL """
            """path with an id in it. And your two million series becomes two hundred million overnight. """
            """Memory explodes, the index stops fitting, queries time out, and the system whose entire """
            """purpose is watching everything else goes down first, during the incident when you need it """
            """most.""")
seg(sid, 3, """That is the story to tell. Say it in the interview and you have demonstrated that you have """
            """operated one of these rather than read about one — and for an infrastructure round, that """
            """distinction is most of the signal.""")

think('You have 10,000 hosts emitting 200 metrics each. Should the collectors PUSH to your system, or should your system PULL from them? Name one consequence of each.',
      30,
      """Pause here on a decision that shapes everything downstream. Ten thousand hosts, two hundred """
      """metrics each. Do the hosts push to you, or do you pull from them? Name one real consequence of """
      """each choice.""",
      """This is the first architectural fork, and both answers are defensible — which is exactly why it """
      """makes a good interview question.""")

clarify('What I would clarify first', [
 ('What is the metric volume &mdash; how many hosts, how many series each, at what interval?',
  'Gives you <b>series count</b>, which is the number that governs this entire system. Not RPS.'),
 ('What retention, and at what resolution?',
  '&ldquo;13 months&rdquo; at full resolution is a completely different system from 13 months of '
  '<b>rollups</b>. This is the biggest storage lever.'),
 ('Who queries it &mdash; dashboards, alerts, or ad-hoc exploration?',
  'Dashboards are <b>predictable and cacheable</b>. Ad-hoc exploration is not, and it is what makes '
  'query capacity hard to plan.'),
 ('How fresh must alerting be?',
  'Sub-minute alerting means alert evaluation is on the <b>hot path</b>. Five-minute alerting lets it '
  'run off pre-aggregated rollups.'),
 ('Is this multi-tenant &mdash; one team, or the whole company?',
  'Multi-tenant means <b>one team can destroy everyone else\'s monitoring</b> with a bad label. '
  'Quotas and isolation become first-class.'),
 ('Can we drop data under pressure, and which data?',
  'The question nobody asks and everybody needs. <b>A monitoring system that queues forever during an '
  'incident is useless.</b>'),
], [
 """What is the metric volume — hosts, series per host, and interval? Notice I am asking for series """
 """count rather than requests per second, because series count is what governs this system, and asking """
 """in the right unit signals that you know that.""",
 """What retention and at what resolution? Thirteen months at full resolution is a completely different """
 """system from thirteen months of rollups. This is the single biggest storage lever available and it """
 """is a product decision, not a technical one.""",
 """Who queries it? Dashboards are predictable and cacheable. Ad-hoc exploration is neither, and it is """
 """what makes query capacity genuinely hard to plan for.""",
 """How fresh must alerting be? Sub-minute alerting puts alert evaluation on the hot path. Five-minute """
 """alerting lets it run off pre-aggregated rollups, which is far cheaper.""",
 """Is it multi-tenant? This matters enormously, because in a multi-tenant metrics system one team can """
 """destroy everyone else's monitoring with a single bad label. Quotas and isolation stop being nice to """
 """have.""",
 """And the question nobody asks and everybody needs: can we drop data under pressure, and which data? A """
 """monitoring system that queues forever during an incident is useless precisely when it matters. """
 """Asking permission to drop is a mature question.""",
])

capacity('Capacity — and the one number that is not like the others', [
 ('10,000 hosts &times; 200 metrics', '10,000 &times; 200', '<b>2 million series</b>',
  'The governing number. Memory, index size and query cost all scale with <b>this</b>'),
 ('Scrape every 10 s', '2M &divide; 10', '200,000 points / s',
  'Routine for a modern TSDB. <b>Ingestion is a solved problem</b> &mdash; say so'),
 ('Raw point = 16 B', '200k &times; 16 B &times; 86,400', '&asymp; 276 GB / day',
  '100 TB/yr. <b>Storing raw is not viable</b>'),
 ('Delta-of-delta + XOR compression', '~16 B &rarr; ~1.5&ndash;2 B / point', '&asymp; 35 GB / day',
  '12.6 TB/yr &times;3 = 38 TB. <b>Compression is a requirement, not an optimisation</b>'),
 ('Rollups: 1 m, 5 m, 1 h after 7 days', 'raw 7 d + rollups 13 mo', '&asymp; 10&ndash;15 TB',
  'Most queries hit rollups, which are <b>10&ndash;100&times; smaller</b> and faster'),
 ('One careless label: user_id', '2M series &times; 1M values', '<b>catastrophe</b>',
  'Not a capacity line &mdash; <b>an availability one</b>. This is what you design against'),
], [
 """The capacity work. Ten thousand hosts times two hundred metrics is two million series, and I will """
 """say again that this is the governing number — memory, index size and query cost all scale with """
 """series count rather than with request rate.""",
 """Scraping every ten seconds gives two hundred thousand points a second. That is routine for a modern """
 """time-series database, and saying so explicitly is useful: it tells the interviewer you are not going """
 """to spend the hour over-engineering the easy part.""",
 """At sixteen bytes a raw point that is two hundred and seventy-six gigabytes a day, about a hundred """
 """terabytes a year. Storing raw points is not viable, and we have established that in one line.""",
 """Time-series compression — delta-of-delta encoding on timestamps and XOR on float values — takes you """
 """to roughly one and a half to two bytes per point. Thirty-five gigabytes a day, twelve and a half """
 """terabytes a year, thirty-eight with replication. Compression here is a requirement rather than an """
 """optimisation: a design that leaves it out is wrong by a factor of eight, and interviewers who know """
 """this domain are listening for it.""",
 """Add rollups — one minute, five minute and hourly aggregates, with raw data kept only for seven days """
 """— and you land at ten to fifteen terabytes. Most queries then hit rollups that are ten to a hundred """
 """times smaller and correspondingly faster.""",
 """And then the last line, which is not really a capacity line at all. One careless label with a """
 """million distinct values multiplies your series count into the hundreds of millions. That is an """
 """availability problem, not a storage problem, and it is the thing you actually design against.""",
])

tradeoff('Push or pull? The first real fork', [
 ('Pull &mdash; the system scrapes targets', 'ok',
  ['The system controls its own load &mdash; <b>it cannot be overwhelmed by a client</b>',
   'Scrape failure <i>is</i> a health signal: an unreachable target is meaningful',
   'Targets need no queueing or retry logic',
   'Easy to reason about who is being monitored'],
  ['Needs service discovery to know what to scrape',
   'Awkward for short-lived jobs that finish between scrapes',
   'Network path must allow inbound connections to every target']),
 ('Push &mdash; targets send to the system', 'shared',
  ['Works naturally for short-lived jobs and serverless',
   'No service discovery needed', 'Works through NAT and across network boundaries'],
  ['<b>A misbehaving client can flood you</b> &mdash; you no longer control your own load',
   'Every client needs buffering and retry logic',
   'A silent client is ambiguous: dead, or just quiet?']),
], decision='Pull for long-lived infrastructure, with a small push gateway for short-lived jobs. '
            'The pull model gives the platform control over its own load, which is exactly what you '
            'want in the system that must survive an incident.',
 flip='If the fleet were mostly ephemeral &mdash; serverless, batch jobs, CI runners &mdash; I would '
      'invert it and make push primary, then accept that I need per-tenant rate limiting at the '
      'ingestion edge to protect myself.',
 narration=[
  """Push or pull. Pull means your system scrapes targets on a schedule. The decisive advantage is that """
  """the system controls its own load — it cannot be overwhelmed by a client having a bad day, which is """
  """a very valuable property for the one system that must stay up during an incident. Scrape failure is """
  """also itself a health signal: a target you cannot reach is telling you something. And targets need """
  """no queueing or retry logic at all.""",
  """The costs are real: you need service discovery to know what to scrape, it is awkward for """
  """short-lived jobs that start and finish between scrapes, and your network has to allow inbound """
  """connections to every target.""",
  """Push means targets send to you. It works naturally for short-lived jobs and serverless, needs no """
  """discovery, and traverses NAT and network boundaries easily. But you lose control of your own load — """
  """one misbehaving client can flood you — every client needs buffering and retry logic, and a silent """
  """client is ambiguous in a way a failed scrape is not: is it dead, or just quiet?""",
  """I would choose pull for long-lived infrastructure with a small push gateway for short-lived jobs, """
  """and justify it on that control-of-load property. And the reversal: if the fleet were mostly """
  """ephemeral — serverless, batch, CI runners — I would invert it, make push primary, and then accept """
  """that I need per-tenant rate limiting at the ingestion edge to protect myself. Notice how the """
  """protection requirement appears as soon as I give up control, which is the kind of consequence chain """
  """worth saying out loud.""",
 ])

sid = beat('Data model', 'A series is a name plus a set of labels',
           '<div style="font-size:27px;line-height:1.7">'
           '<span style="font-family:JetBrains Mono,monospace;font-size:24px;color:#9fb4cc">'
           'http_requests_total{host="web-04", region="us-west", status="500"}</span><br><br>'
           'That whole thing &mdash; name <b>plus every label value</b> &mdash; identifies one series. '
           'Change any label value and it is a <b>different series</b> with its own storage and its own '
           'index entry.<br><br>'
           '<b>Storage is two structures, and the split is the design:</b><br>'
           '&bull; <b>Inverted index</b>: label &rarr; series ids. Answers &ldquo;which series match '
           '<code>region=us-west</code>?&rdquo; This lives in <b>memory</b> and is what cardinality '
           'destroys.<br>'
           '&bull; <b>Column chunks</b>: per series, timestamps and values compressed together in '
           'time-ordered blocks. This lives on <b>disk</b> and is cheap.<br><br>'
           '<span style="color:#ffd483">Cardinality is expensive because of the <b>index</b>, not '
           'because of the data.</span></div>',
           """The data model, and getting this right is what makes the cardinality story land. A series is """
           """a metric name plus a set of label key-value pairs. The whole thing together identifies one """
           """series — change any single label value and it is a different series, with its own storage """
           """and its own index entry.""", step=0)
seg(sid, 1, """Storage is two quite different structures, and the split between them is the design. First, """
            """an inverted index from label to series ids, which answers "which series match region """
            """equals us-west". This lives in memory, and this is what cardinality destroys.""")
seg(sid, 2, """Second, column chunks: for each series, timestamps and values compressed together in """
            """time-ordered blocks. This lives on disk and is genuinely cheap — it is the part """
            """compression made small.""")
seg(sid, 3, """So the sentence that ties it together: cardinality is expensive because of the index, not """
            """because of the data. Two hundred million series is not a lot of bytes on disk; it is a """
            """catastrophic amount of in-memory index. If you can explain why, you have explained the """
            """whole failure mode.""")

# ------------------------------------------------------------------ architecture
A = Arch('Architecture — ingest, store, query, alert', kicker='Progressive disclosure', height=810)
A.box('t',   70, 330, 180, 110, 'Targets', '10k hosts', kind='neutral', step=0, focus=0)
A.box('sc',  300, 330, 200, 110, 'Scrapers', 'sharded by target', kind='info', step=0, focus=0)
A.arrow('t', 'sc', step=0, focus=0)
A.box('tsdb',1030, 330, 230, 110, 'Time-series store', 'index + chunks', kind='shared', step=0, focus=[0, 3])
A.arrow('sc', 'tsdb', step=0, focus=0)

A.box('ing', 660, 330, 230, 110, 'Ingest tier', 'validate, limit', kind='ok', step=1, focus=1)
A.arrow('sc', 'ing', step=1, focus=1)
A.arrow('ing', 'tsdb', step=1, focus=1)

A.box('wal', 660, 490, 230, 80, 'WAL + buffer', kind='dp', step=2, focus=2, small=True)
A.arrow('ing', 'wal', step=2, focus=2, dashed=True)

A.box('roll',1030, 490, 230, 80, 'Rollup jobs', '1m / 5m / 1h', kind='dp', step=3, focus=3, small=True)
A.arrow('tsdb', 'roll', step=3, focus=3, dashed=True)

A.box('q',   1330, 330, 210, 110, 'Query engine', kind='info', step=4, focus=4)
A.arrow('tsdb', 'q', step=4, focus=4)
A.box('dash',1630, 250, 200, 90, 'Dashboards', kind='neutral', step=4, focus=4, small=True)
A.box('al',  1630, 400, 200, 90, 'Alerting', 'rule eval', kind='deny', step=5, focus=5, small=True)
A.arrow('q', 'dash', step=4, focus=4)
A.arrow('q', 'al', step=5, focus=5)

A.box('push', 300, 180, 200, 90, 'Push gateway', 'short-lived jobs', kind='info', step=6, focus=6, small=True)
A.arrow('push', 'ing', step=6, focus=6, dashed=True)

A.note(300, 620, '**Ingest tier exists to protect the store**: validate labels, enforce per-tenant\\n'
                 'cardinality quotas, and shed load. Without it, one bad deploy takes down monitoring\\n'
                 'for the entire company &mdash; during the incident that bad deploy caused.',
       step=7, kind='deny', w=1500, size='m')
A.narrate(0, """The architecture. Targets are scraped by a scraper tier, sharded by target so each scraper """
              """owns a slice of the fleet, and the data lands in a time-series store. That is the """
              """skeleton and it would work.""")
A.narrate(1, """Now the piece that matters most and that candidates leave out: an ingest tier between the """
              """scrapers and the store. Its job is validation, per-tenant limits and load shedding. I """
              """will come back to why this is the most important box on the diagram.""")
A.narrate(2, """A write-ahead log and buffer, so that a storage hiccup does not lose the data that is """
              """arriving continuously and cannot be re-requested. Metrics are a stream you cannot """
              """replay — if you drop a scrape, that moment in time is simply gone.""")
A.narrate(3, """Rollup jobs producing one-minute, five-minute and hourly aggregates, so long-range queries """
              """read small pre-aggregated data rather than scanning raw points.""")
A.narrate(4, """A query engine serving dashboards, which are predictable and cacheable.""")
A.narrate(5, """And alerting, which reads through the same query path but on a schedule. I have drawn it """
              """separately because its failure mode is different: a dashboard being slow is annoying, """
              """alerting being slow means nobody finds out about an outage.""")
A.narrate(6, """Plus a push gateway on the side for short-lived jobs, which is the pragmatic answer to the """
              """push-versus-pull trade-off we just made.""")
A.narrate(7, """And now the sentence I would make sure to say while pointing at the ingest tier: this box """
              """exists to protect the store. It validates labels, enforces per-tenant cardinality quotas, """
              """and sheds load. Without it, one bad deploy takes down monitoring for the entire company — """
              """during the incident that the bad deploy just caused. That is the failure that makes this """
              """system different from every other system you will design.""")
A.build()

sid = beat('Deep dive 1', 'Cardinality — how to actually defend against it',
           '<div style="font-size:27px;line-height:1.7">'
           'You cannot rely on good intentions. Engineers add labels at 2am during incidents. '
           'Defend <b>structurally</b>:<br><br>'
           '<b>1. Per-tenant series quota.</b> A team gets N series. At the limit, <b>reject new '
           'series</b> and keep serving existing ones. Crucially: reject the <i>new</i>, never drop '
           'the <i>old</i> &mdash; existing dashboards and alerts keep working.<br><br>'
           '<b>2. Label-value limits.</b> Refuse a label whose distinct values exceed a threshold, and '
           'name the offender in the error.<br><br>'
           '<b>3. Block the known killers</b> at the ingest tier: anything that looks like a user id, '
           'request id, email, or a raw URL path with an id in it.<br><br>'
           '<b>4. Make it visible.</b> A per-team cardinality dashboard, and an alert when a team '
           'crosses 80% of quota &mdash; <b>before</b> they hit it.<br><br>'
           '<span style="color:#ffd483">And the cultural half: the error message must say '
           '<i>which</i> label and <i>what to do</i>. A rejection nobody understands becomes a ticket '
           'for your team.</span></div>',
           """Deep dive one: cardinality, and how to actually defend against it. And the framing matters — """
           """you cannot rely on good intentions here. Engineers add labels at two in the morning during """
           """incidents, because in that moment a user id label is genuinely the most useful thing in the """
           """world. So you defend structurally.""", step=0)
seg(sid, 1, """First, a per-tenant series quota. A team gets N series. At the limit you reject new series """
            """while continuing to serve existing ones — and that asymmetry is the important part. Reject """
            """the new, never drop the old, because existing dashboards and alerts must keep working. A """
            """quota that breaks running alerts has made the outage worse.""")
seg(sid, 2, """Second, label-value limits: refuse a label whose distinct values exceed a threshold, and """
            """name the offending label in the error. Third, block the known killers at the ingest tier — """
            """anything that looks like a user id, a request id, an email address, or a raw URL path with """
            """an id embedded in it.""")
seg(sid, 3, """Fourth, make it visible: a per-team cardinality dashboard and an alert when a team crosses """
            """eighty percent of quota, so they find out before they hit the wall rather than after.""")
seg(sid, 4, """And then the half that is not technical at all, which I would raise deliberately because it """
            """shows you have run a platform: the error message has to say which label caused the """
            """rejection and what to do about it. A rejection nobody understands becomes a support ticket """
            """for your team, at volume. Platform work is as much about the error messages as the """
            """architecture.""")

sid = beat('Deep dive 2', 'Backpressure — what to drop when you cannot keep up',
           '<div class="bigidea">A monitoring system that queues forever during an incident is '
           '<b>useless</b>, because the incident is exactly when you need it.</div>'
           '<div style="margin-top:24px;font-size:27px;line-height:1.68">'
           'When ingest cannot keep up, you must drop something. <b>Decide in advance, in this '
           'order:</b><br><br>'
           '<b>1. Drop raw resolution before dropping series.</b> Ingest at 60 s instead of 10 s &mdash; '
           'you keep every signal, at lower fidelity. <b>Alerts still fire.</b><br>'
           '<b>2. Drop the newest, not the oldest.</b> A partial recent window beats a gap in history.<br>'
           '<b>3. Drop by tenant quota</b>, so the team causing the flood absorbs its own damage rather '
           'than everyone sharing it.<br>'
           '<b>4. Never drop alerting-relevant series.</b> Tag them; protect them.<br><br>'
           '<span style="color:#ffd483">&ldquo;What do you drop first?&rdquo; is the best question an '
           'interviewer can ask here &mdash; and having a ranked answer is the best possible '
           'reply.</span></div>',
           """Deep dive two: backpressure, and what to drop when you cannot keep up. Start from the """
           """principle: a monitoring system that queues forever during an incident is useless, because """
           """the incident is exactly when you need it. Unbounded buffering is not resilience, it is """
           """deferred failure.""", step=0)
seg(sid, 1, """So you will drop something, and the professional move is to decide the order in advance. """
            """First, drop raw resolution before dropping series — ingest at sixty seconds instead of ten. """
            """You keep every signal at lower fidelity, and critically, alerts still fire. Losing """
            """resolution is survivable; losing a signal entirely is not.""")
seg(sid, 2, """Second, drop the newest rather than the oldest, because a partial recent window is more """
            """useful than a gap in your history. Third, drop by tenant quota, so the team causing the """
            """flood absorbs its own damage instead of everyone sharing it — that is fairness as an """
            """engineering property.""")
seg(sid, 3, """And fourth, never drop series that alerts depend on. Tag them and protect them explicitly.""")
seg(sid, 4, """"What do you drop first?" is the single best question an interviewer can ask about this """
            """system, and having a ranked, reasoned answer ready is the best possible reply. Most """
            """candidates answer "we scale up", which does not address the question.""")

failures('What happens when each piece dies', [
 ('One scraper', 'A slice of the fleet goes unmonitored',
  'Scrapers are sharded by target; another takes over the shard. <b>Gaps in that window are permanent</b> '
  '&mdash; metrics cannot be replayed'),
 ('Ingest tier', 'Everything stops arriving',
  'Scrapers buffer briefly, then drop. <b>This is the single point that matters</b>; run it stateless '
  'and over-provisioned'),
 ('Time-series store node', 'Queries touching that shard fail or return partial data',
  'Replicate; prefer <b>returning partial results with a warning</b> over failing the whole query'),
 ('Rollup job', 'Long-range queries get slower, not wrong',
  'They fall back to scanning raw data. Degraded performance only &mdash; not a page'),
 ('Query engine', 'Dashboards dark, <b>and alerts stop evaluating</b>',
  'The dangerous one: <b>silent</b>. Alert on "alert evaluations completed" from a <i>separate</i> '
  'system, or you have no way to know'),
 ('The whole platform', 'Nobody can see anything',
  'Needs an <b>independent</b> heartbeat &mdash; a dead-man switch that pages when the monitoring '
  'system stops reporting'),
], [
 """The failure table, and this system has an unusual one, so let us go carefully. One scraper dying """
 """means a slice of the fleet goes unmonitored; another scraper takes over that shard. But say the """
 """consequence that is specific to metrics: the gap in that window is permanent. Unlike almost every """
 """other system you will design, you cannot go back and re-request the data. The moment is gone.""",
 """The ingest tier dying stops everything arriving. Scrapers buffer briefly and then drop. This is the """
 """single point that matters most, so run it stateless and over-provisioned — it is cheap insurance for """
 """the component whose failure blinds you.""",
 """A storage node dying means queries touching that shard fail or return partial data. Replicate, and """
 """prefer returning partial results with a warning over failing the whole query — during an incident, """
 """eighty percent of your dashboard is vastly better than an error page.""",
 """A rollup job failing makes long-range queries slower but not wrong, because they fall back to """
 """scanning raw data. Degraded performance, not a page.""",
 """The query engine dying is the dangerous one, because dashboards go dark and alert evaluation stops — """
 """and it is silent. Nothing fires, which looks exactly like everything being healthy. So you alert on """
 """"alert evaluations completed" from a separate system.""",
 """And the whole platform failing needs an independent heartbeat: a dead-man switch that pages when the """
 """monitoring system stops reporting. The general principle, which is worth stating out loud, is that """
 """a monitoring system cannot monitor itself — so a small, boring, independent watcher is part of the """
 """design rather than an afterthought.""",
])

sid = beat('Alerting at scale', 'The part that is quietly its own hard problem',
           '<div style="font-size:27px;line-height:1.7">'
           '10,000 alert rules, each evaluated every 30 seconds, each running a query over a time '
           'window. That is <b>333 queries a second of pure alert load</b> &mdash; often more than the '
           'human query load.<br><br>'
           '<b>&bull; Shard rule evaluation</b> across workers, with a consistent assignment so a '
           'worker restart does not re-evaluate everything at once.<br>'
           '<b>&bull; Stagger</b> evaluation times. If every rule fires on the minute boundary you have '
           'built a self-inflicted thundering herd.<br>'
           '<b>&bull; Evaluate against rollups</b> where the rule allows it.<br>'
           '<b>&bull; Deduplicate and group</b> notifications: one bad deploy should produce one page, '
           'not four hundred.<br><br>'
           '<span style="color:#ffd483">Alert <b>fatigue</b> is a design problem, not an ops problem. '
           'Grouping belongs in the architecture.</span></div>',
           """Alerting deserves its own section, because it is quietly a hard problem that candidates """
           """treat as a feature. Ten thousand alert rules, each evaluated every thirty seconds, each """
           """running a query over a time window, is three hundred and thirty-three queries a second of """
           """pure alert load — frequently more than all your human query load combined.""", step=0)
seg(sid, 1, """So shard rule evaluation across workers with a consistent assignment, so that a worker """
            """restart does not cause every rule to be re-evaluated simultaneously. And stagger the """
            """evaluation times: if every rule fires on the minute boundary you have built yourself a """
            """thundering herd, on a schedule, forever.""")
seg(sid, 2, """Evaluate against rollups where the rule permits it, which is often.""")
seg(sid, 3, """And deduplicate and group notifications, so that one bad deploy produces one page rather """
            """than four hundred. I would say this explicitly: alert fatigue is a design problem, not an """
            """operations problem. Grouping and deduplication belong in the architecture, because a """
            """system that pages four hundred times has effectively stopped alerting — people mute it.""")

sid = beat('Observability, security, cost', 'Including the recursive bit',
           '<div class="to-grid" style="top:24px">'
           '<div class="to-opt k-info" data-step="0"><div class="to-h">Watching the watcher</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; <b>Ingest lag</b> &mdash; the leading indicator for everything<br>'
           '&bull; <b>Series count per tenant</b> &mdash; the cardinality early warning<br>'
           '&bull; <b>Dropped points</b>, by reason<br>'
           '&bull; <b>Alert evaluation completion</b> &mdash; silence here is invisible<br>'
           '&bull; Query p99 by type (dashboard vs ad-hoc)<br><br>'
           '<span style="color:#ffd483">All of it exported to a <b>separate, minimal</b> system. '
           'Self-monitoring fails exactly when you need it.</span></div></div>'
           '<div class="to-opt k-shared" data-step="1"><div class="to-h">Security</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; <b>Metrics leak secrets</b>: labels carrying emails, tokens, customer names. '
           'Scrub at ingest<br>'
           '&bull; Per-tenant read isolation &mdash; teams should not read each other&rsquo;s data by '
           'default<br>'
           '&bull; Authenticated scrape targets<br>'
           '&bull; Audit who queries what, if data is sensitive</div></div>'
           '<div class="to-opt k-ok" data-step="2"><div class="to-h">Cost</div>'
           '<div style="font-size:23px;line-height:1.5;color:#cfe0f2">'
           '&bull; Dominated by <b>storage volume &times; retention</b><br>'
           '&bull; Biggest lever by far: <b>shorter raw retention</b> &mdash; 7 days raw instead of 30 '
           'is a ~4&times; saving<br>'
           '&bull; Second lever: cardinality quotas &mdash; cost control and availability control are '
           '<b>the same mechanism</b><br>'
           '&bull; Chargeback per team makes cardinality <b>self-policing</b></div></div></div>',
           """Observability of the observability system, which is the recursive bit. Alert on ingest lag """
           """as the leading indicator for everything. Series count per tenant as the cardinality early """
           """warning. Dropped points, broken down by reason, so you know which of your shedding rules """
           """fired. And alert evaluation completion, because silence there is invisible.""", step=0)
seg(sid, 1, """And the rule that matters: export all of it to a separate, minimal system. Self-monitoring """
            """fails at exactly the moment you need it. A small independent watcher is part of the """
            """design.""")
seg(sid, 2, """Security has one item specific to this domain that is worth raising because few candidates """
            """do: metrics leak secrets. Labels end up carrying email addresses, tokens and customer """
            """names, because someone added them for debugging and never removed them. So you scrub at """
            """ingest. Plus per-tenant read isolation, authenticated scrape targets, and query auditing if """
            """the data is sensitive.""")
seg(sid, 3, """Cost is dominated by storage volume times retention, and the biggest lever by far is shorter """
            """raw retention — seven days of raw instead of thirty is roughly a four times saving with """
            """very little loss, because almost nobody queries raw data from three weeks ago. The second """
            """lever is cardinality quotas, and here is the observation to make: cost control and """
            """availability control are the same mechanism in this system. And per-team chargeback makes """
            """cardinality self-policing, which is a much more durable solution than asking people """
            """nicely.""")

sid = cards('Staff-level follow-ups', [
 (0, '&ldquo;A team adds a user_id label. What happens?&rdquo;',
  'The question this system exists to answer. Quota rejects <b>new</b> series, existing ones keep serving, the team is alerted with the offending label named. <b>Nothing else is affected</b> &mdash; that is the isolation working.', 'ok'),
 (0, '&ldquo;Ten times the hosts &mdash; 100k.&rdquo;',
  '20M series, 2M points/s. Scrapers and ingest shard linearly. The real change: <b>push aggregation down to the agent</b> so a host sends pre-aggregated series instead of raw ones.', 'ok'),
 (1, '&ldquo;Sub-second alerting.&rdquo;',
  'Push back: for what? If it is infrastructure, 30 s is the useful floor &mdash; below that you alert on noise. If it is genuinely needed, that is <b>stream processing on the ingest path</b>, not querying storage.', 'shared'),
 (1, '&ldquo;Queries are slow for long ranges.&rdquo;',
  'Check whether they are hitting rollups or raw. Usually the rollup is missing or the query is not rewritten to use it. <b>Automatic query rewriting to the coarsest acceptable rollup</b> is the fix.', 'ok'),
 (2, '&ldquo;Multi-region.&rdquo;',
  'Keep metrics <b>local to the region</b> and query across regions at read time. Shipping all metrics to one region doubles your cross-region bill and creates a dependency that breaks during the exact failure you are trying to observe.', 'ok'),
 (2, '&ldquo;Build or buy?&rdquo;',
  'A legitimate Staff answer: at 2M series, buy. Building pays off at very large scale, or when cost per series or data residency forces it. <b>Saying &ldquo;buy&rdquo; with reasons is not a cop-out</b> &mdash; it is judgement.', 'shared'),
], cols=2)
seg(sid, 0, """Staff-level follow-ups. A team adds a user id label — which is the question this entire system """
            """exists to answer. The quota rejects new series, existing ones keep serving, and the team is """
            """alerted with the offending label named. Nothing else is affected, and being able to say """
            """"nothing else is affected" is the isolation working.""")
seg(sid, 1, """Ten times the hosts: twenty million series, two million points a second. Scrapers and ingest """
            """shard linearly, so that part is routine. The real change is pushing aggregation down to the """
            """agent, so a host sends pre-aggregated series rather than raw ones — moving work to the edge """
            """of the system, which is the standard answer when the centre cannot scale.""")
seg(sid, 2, """Sub-second alerting: push back and ask what for. For infrastructure, thirty seconds is """
            """roughly the useful floor — below that you are alerting on noise and will cause fatigue. If """
            """it is genuinely needed, that is stream processing on the ingest path rather than querying """
            """storage, and it is a different system.""")
seg(sid, 3, """Slow long-range queries: check whether they are hitting rollups or raw data. It is almost """
            """always that the rollup is missing or that the query was not rewritten to use it, and """
            """automatic rewriting to the coarsest acceptable rollup is the fix.""")
seg(sid, 4, """Multi-region: keep metrics local to the region and query across at read time. Shipping """
            """everything to one region doubles your cross-region bill and — this is the important part — """
            """creates a dependency that breaks during exactly the failure you are trying to observe. """
            """Region-local monitoring survives a region partition; centralised monitoring does not.""")
seg(sid, 5, """And build or buy, which is a legitimate Staff-level answer. At two million series, buy. """
            """Building pays off at very large scale, or when cost per series or data residency forces """
            """your hand. Saying "buy, and here is the threshold where I would change my mind" is not a """
            """cop-out — it is judgement, and it is what you would actually say in a real design """
            """review.""")

followups(
 ['Ingestion rate and metric cardinality &mdash; <b>reported</b>',
  'Downsampling and retention &mdash; <b>reported</b>',
  'Alert evaluation at scale &mdash; <b>reported</b>',
  'The query path for dashboards'],
 ['"What do you drop first under pressure?"',
  '"What happens when a team adds a high-cardinality label?"',
  '"How do you know the monitoring system itself is healthy?"',
  '"Push or pull, and why?"',
  '"Would you build this, or buy it?"'],
 """The reported follow-ups map closely onto what we have covered: ingestion rate and cardinality, """
 """downsampling and retention, and alert evaluation at scale — all three were named in the candidate """
 """accounts — plus the dashboard query path.""",
 """And the ones I would expect on top. What do you drop first under pressure, which is the best question """
 """in this design. What happens when a team adds a high-cardinality label. How you know the monitoring """
 """system itself is healthy. Push versus pull. And build versus buy, where a reasoned "buy" is a """
 """perfectly strong answer.""")

say('What I should say — the sentences that carry this design', [
 'Let me start with series count rather than request rate, because in a metrics system series count is what governs memory, index size and query cost.',
 'Two hundred thousand points a second is routine — ingestion is a solved problem here. What is not solved is cardinality, and that is where I want to spend my time.',
 'Raw storage would be a hundred terabytes a year, so compression is a requirement rather than an optimisation — delta-of-delta on timestamps, XOR on values, about two bytes a point.',
 'I would choose pull over push, because the platform then controls its own load — which is exactly what you want from the one system that has to survive an incident.',
 'The ingest tier exists to protect the store: validate labels, enforce per-tenant quotas, shed load. Without it, one bad deploy blinds the whole company.',
 'When a quota is hit I reject new series and keep serving existing ones, so running dashboards and alerts are never broken by the enforcement.',
 'If I cannot keep up, I drop resolution before I drop series — alerts still fire at sixty-second granularity.',
 'And this system cannot monitor itself, so I would export a few vital signs to a separate minimal watcher with a dead-man switch.',
], [
 """Eight sentences for this question. The first establishes the right unit, which immediately signals """
 """domain familiarity.""",
 """The second dismisses the easy part and names the hard one, which directs the whole conversation.""",
 """The third makes compression a requirement with the arithmetic behind it, and names the actual """
 """techniques.""",
 """The fourth is your push-pull decision justified by a property — control of load — rather than by """
 """preference.""",
 """The fifth is the sentence I would make sure to say while pointing at the ingest tier, because it """
 """explains why the most important box on your diagram exists.""",
 """The sixth shows you have thought about what enforcement does to people who are already running """
 """systems.""",
 """The seventh is your ranked shedding answer in one line. And the eighth closes on the recursive """
 """problem, which is a memorable note to end on and shows you understand what makes this system """
 """different from everything else you might design.""",
])

cheatsheet('Metrics platform — the revision card', [
 ('Problem', 'Collect, store, query and alert on time-series metrics'),
 ('Evidence', '3 independent reports &middot; most recent Sep 2025 &middot; upgraded to HIGH'),
 ('Scale', '2M series &middot; 200k points/s &middot; 38 TB/yr compressed'),
 ('Governing number', '<b>Series count</b> &mdash; not requests per second'),
 ('Dominant risk', '<b>Cardinality</b>, not throughput'),
 ('Collection', 'Pull, + push gateway for short-lived jobs'),
 ('Why pull', 'The platform controls its own load'),
 ('Data model', 'name + labels = series; inverted index + column chunks'),
 ('Why cardinality hurts', 'The <b>in-memory index</b>, not the data on disk'),
 ('Compression', 'Delta-of-delta + XOR &rarr; ~2 B/point. <b>Required</b>'),
 ('Retention', '7 d raw + 1m/5m/1h rollups for 13 months'),
 ('Partitioning', 'By series hash, then by time window'),
 ('The key box', '<b>Ingest tier</b>: validate, quota, shed'),
 ('Quota behaviour', 'Reject <b>new</b> series; never break existing alerts'),
 ('Shed order', 'Resolution &rarr; newest &rarr; by tenant. <b>Never alerting series</b>'),
 ('Alerting', 'Shard rules, stagger evaluation, group notifications'),
 ('Silent failure', 'Alert evaluation stopping. Watch from <b>outside</b>'),
 ('Security', 'Labels leak secrets &mdash; scrub at ingest'),
 ('Cost', 'Raw retention is the big lever; chargeback self-polices cardinality'),
 ('Build or buy', 'At this scale, <b>buy</b> &mdash; and say what would change that'),
], [
 """The revision card. Problem, evidence, scale — and the two lines that matter most: the governing """
 """number is series count, and the dominant risk is cardinality.""",
 """Collection model and why. The data model and the reason cardinality hurts, which is the index rather """
 """than the data.""",
 """Compression as a requirement, the retention scheme, and the partitioning.""",
 """Then the operational core: the ingest tier as the key box, what a quota does when hit, and your """
 """ranked shedding order.""",
 """Alerting mechanics, the silent failure to watch for from outside, the security item specific to this """
 """domain, the cost lever, and the build-or-buy answer with its threshold. Twenty lines, and they """
 """reconstruct the whole design.""",
])

sid = statement('Lesson 2.3', 'Design against the failure mode, not the load.',
                'The load was routine. What makes this system hard is that one label from one team can blind the whole company — so the architecture is built around preventing that.',
                kind='ok')
seg(sid, 0, """One line to close. Design against the failure mode, not the load.""")
seg(sid, 1, """The load in this system was routine — two hundred thousand points a second is a solved """
            """problem. What makes it hard is that one label added by one engineer can blind the entire """
            """company, during the incident that engineer was investigating. Once you see that, the """
            """architecture follows: an ingest tier that exists purely to protect the store, quotas that """
            """reject new work without breaking old work, a ranked shedding order decided in advance, and """
            """an independent watcher because this system cannot watch itself. That is the end of the """
            """pilot — five lessons. Tell me what to change, and we will build the remaining chapters """
            """against your feedback.""")
