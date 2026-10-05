# -*- coding: utf-8 -*-
"""Chapter 9, Lesson 2 — host health monitoring across three data centres."""
from lib import *

lesson_header('9.2', 'Design host health monitoring across three data centres',
              'Agent push &middot; time series &middot; current state vs history &middot; the engineer UI',
              dict(reports='InterviewTV list; the metrics family has 3 reports (lesson 2.3)',
                   latest='September 2025', level='Staff, Infrastructure',
                   conf='MEDIUM-HIGH &mdash; family corroborated',
                   sources='InterviewTV.io + Blind &times;2, Glassdoor'), 16,
              """Chapter nine, lesson two: host health monitoring. LinkedIn runs three data centres with """
              """hundreds of thousands of hosts. Collect health signals, know the current health of """
              """every host, keep history, and give engineers a U-I to troubleshoot past incidents. """
              """This is the sibling of the metrics lesson in two point three, and the thing worth """
              """getting right here is that &ldquo;current health&rdquo; and &ldquo;history&rdquo; are """
              """two different systems that people try to build as one.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff, Infrastructure',
  'Three data centres, <b>hundreds of thousands of hosts</b>. Collect signals, current health, '
  'history, <b>UI for engineers</b>, troubleshoot historical issues'),
 ('Research pass 3 &mdash; metrics gathering', 'Sep 2025', 'Senior / Staff',
  '<b>3 independent reports</b> for the metrics family (lesson 2.3). Shares the ingestion machinery'),
], """Medium-high, because the family has three independent reports even though this exact framing is """
     """single-source. Watch lesson two point three first if you have not.""",
 ["""What is different here is the emphasis: current health and a U-I for troubleshooting historical """
  """issues. Those are named explicitly, and they pull in opposite directions &mdash; which is the """
  """whole lesson."""],
 caveat='The metrics family is well attested. This host-health framing adds the current-state and UI '
        'requirements.',
 narration_caveat="""The metrics family is well attested. This host-health framing adds the """
                  """current-state and troubleshooting-U-I requirements, which is where the """
                  """interesting tension lives.""")

sid = beat('Why this is interesting', 'Two questions that want opposite storage',
           '<div style="font-size:28px;line-height:1.72">'
           '<b>&ldquo;Is host X healthy right now?&rdquo;</b><br>'
           'One row per host. Overwritten constantly. Must be <b>fast and current</b>. '
           '<span style="color:#a8e6a3">300k rows total &mdash; it fits in memory.</span><br><br>'
           '<b>&ldquo;What was happening on host X at 3 a.m. last Tuesday?&rdquo;</b><br>'
           'Append-only, never updated, <b>enormous</b>, and read rarely but deeply. '
           '<span style="color:#a8e6a3">Billions of points &mdash; it belongs in a time-series '
           'store.</span><br><br>'
           '<span style="color:#ff9a9a">Trying to serve both from one store means either a current-state '
           'query that scans history, or a history store you keep updating. Both are wrong.</span>'
           '<br><br>'
           '<b>And a third requirement hides in &ldquo;three data centres&rdquo;:</b> if a DC is '
           'cut off, you must still be able to see that it is cut off. '
           '<span style="color:#ffd483">A monitoring system that goes dark exactly when something '
           'breaks is worse than no monitoring, because it is silent rather than absent.</span><br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: when two access patterns disagree about '
           'mutability and size, build two stores from one stream.</span></div>',
           """Why is this interesting? Because it contains two questions that want opposite kinds of """
           """storage.""", step=0)
seg(sid, 1, """&ldquo;Is host X healthy right now?&rdquo; is one row per host, overwritten constantly, """
            """and it must be fast and current. Three hundred thousand rows total &mdash; it fits in """
            """memory comfortably.""")
seg(sid, 2, """&ldquo;What was happening on host X at three in the morning last Tuesday?&rdquo; is """
            """append-only, never updated, enormous, and read rarely but deeply. Billions of points, """
            """belonging in a time-series store.""")
seg(sid, 3, """Trying to serve both from one store gives you either a current-state query that scans """
            """history, or a history store you keep mutating. Both are wrong, and the mistake is """
            """natural because both questions are about the same hosts.""")
seg(sid, 4, """And there is a third requirement hiding in the phrase &ldquo;three data centres&rdquo;. If """
            """one data centre is cut off, you must still be able to see that it is cut off. A """
            """monitoring system that goes dark exactly when something breaks is worse than no """
            """monitoring at all, because it is silent rather than obviously absent &mdash; and silence """
            """looks like health.""")
seg(sid, 5, """So the staff-level insight: when two access patterns disagree about mutability and size, """
            """build two stores from one stream. Do not compromise one structure to serve both.""")

think('A data centre loses its network link. Every host in it stops reporting. Your dashboard now shows '
      'those hosts as... what? And how does your system tell the difference between "100,000 hosts just '
      'died" and "we cannot see them"?',
      25,
      """Pause. A data centre loses its network link and every host in it stops reporting. What does """
      """your dashboard show for those hosts? And how does your system tell the difference between a """
      """hundred thousand hosts dying and simply not being able to see them? Say it out loud.""",
      """Hold that. Absence of data is not the same as bad data, and conflating them is how monitoring """
      """systems lie to you during exactly the incident you built them for.""")

clarify('What I would clarify first', [
 ('What counts as a &ldquo;health signal&rdquo;?',
  'CPU and memory is a handful of numbers per host. Add per-process, per-disk and per-interface and '
  'you are at <b>hundreds of series per host</b> &mdash; a 100&times; difference in everything.'),
 ('What resolution, and for how long?',
  '10-second resolution for 13 months is ~100&times; the data of 1-minute for 30 days. '
  '<b>Downsampling policy is the main cost lever.</b>'),
 ('Is this for alerting, for dashboards, or for post-incident forensics?',
  'Alerting needs <b>seconds</b> of freshness on a few series. Forensics needs <b>months</b> of '
  'history at good resolution. Different systems.'),
 ('Who defines &ldquo;healthy&rdquo; &mdash; us, or each service team?',
  'A central definition does not fit every service. Per-team definitions mean <b>the health check is '
  'configuration</b>, which has to be distributed and versioned.'),
 ('Must monitoring survive a data centre being isolated?',
  '<b>Almost certainly yes</b>, and it forces per-DC collection with cross-DC replication &mdash; you '
  'cannot have a single central collector.'),
 ('How quickly must a dead host be noticed?',
  'Decides the reporting interval and therefore the entire data volume. <b>30 seconds vs 5 seconds is '
  'a 6&times; difference in everything.</b>'),
], [
 """What counts as a health signal? C-P-U and memory is a handful of numbers per host. Add per-process, """
 """per-disk and per-network-interface metrics and you are at hundreds of series per host &mdash; a """
 """hundred-fold difference in storage, bandwidth and cost. Ask before you compute anything.""",
 """What resolution, and for how long? Ten second resolution for thirteen months is about a hundred """
 """times the data of one minute for thirty days. The downsampling policy is the main cost lever in """
 """this entire system.""",
 """Is this for alerting, dashboards, or post-incident forensics? Alerting needs seconds of freshness """
 """on a few series. Forensics needs months of history at decent resolution. Those are genuinely """
 """different systems and the question names both.""",
 """Who defines healthy &mdash; us, or each service team? A central definition will not fit every """
 """service. Per-team definitions mean the health check is configuration, which then has to be """
 """distributed and versioned &mdash; which is the denylist problem from chapter four again.""",
 """Must monitoring survive a data centre being isolated? Almost certainly yes, and that forces """
 """per-data-centre collection with cross-replication. You cannot have a single central collector, and """
 """realising that early shapes the whole topology.""",
 """And how quickly must a dead host be noticed? That decides the reporting interval and therefore all """
 """your volumes. Thirty seconds versus five seconds is a six-fold difference in everything.""",
])

capacity('Capacity', [
 ('300k hosts &times; 50 series &times; every 10 s', '300k &times; 50 &divide; 10',
  '&asymp; 1.5M points / s', 'The headline ingestion rate across all three DCs'),
 ('Point size ~16 B (ts + value, compressed)', '1.5M &times; 16 B', '&asymp; 24 MB / s',
  '&asymp; 2 TB / day raw. <b>Time series compress extremely well &mdash; see below</b>'),
 ('Delta-of-delta + XOR compression', 'typical 10&ndash;20&times; on metrics',
  '&asymp; 100&ndash;200 GB / day', '<b>This is why dedicated TSDBs exist.</b> A generic store would '
  'cost 10&times; more'),
 ('Current state: 300k hosts &times; ~1 KB', '300k &times; 1 KB', '&asymp; 300 MB',
  '<b>Fits in memory trivially.</b> Entirely separate from history'),
 ('Retention: 10 s for 7 d, 1 min for 30 d, 5 min for 13 mo', 'downsample as it ages',
  '&asymp; 15&ndash;20 TB total', 'Manageable. <b>Downsampling is what makes 13 months affordable</b>'),
 ('Query: one host, one day, 10 s resolution', '8,640 points &times; 50 series',
  '&asymp; 432k points', 'Fast if indexed by (host, metric, time). <b>Slow if you index by time '
  'alone</b>'),
], [
 """Numbers. Three hundred thousand hosts times fifty series each, reported every ten seconds, is about """
 """one and a half million points a second across all three data centres.""",
 """At roughly sixteen bytes a point that is twenty-four megabytes a second, about two terabytes a day """
 """raw.""",
 """But time series compress extraordinarily well &mdash; delta-of-delta encoding on timestamps and """
 """X-O-R encoding on values typically gives ten to twenty times, so a hundred to two hundred gigabytes """
 """a day. That compression is precisely why dedicated time-series databases exist, and why storing """
 """metrics in a generic database costs roughly ten times more. Worth saying, because it justifies the """
 """technology choice with a number.""",
 """Current state is three hundred thousand hosts at about a kilobyte, so three hundred megabytes. """
 """Fits in memory trivially, and it is entirely separate from the history store.""",
 """Retention with downsampling &mdash; ten second resolution for seven days, one minute for thirty """
 """days, five minutes for thirteen months &mdash; comes to fifteen or twenty terabytes total. """
 """Manageable, and downsampling is what makes thirteen months affordable at all.""",
 """And a typical query, one host for one day at ten second resolution, is about four hundred and """
 """thirty thousand points. Fast if you index by host, metric and time. Slow if you index by time """
 """alone &mdash; which is the classic mistake, because it makes every query scan every host.""",
])

A = Arch('Health monitoring &mdash; per-DC collection, two stores', kicker='Architecture', height=800)

A.zone(60, 140, 420, 330, 'DATA CENTRE A — collection stays local')

A.box('h1',   95, 200, 150, 75, 'Hosts', '100k', kind='neutral', step=0, focus=0, small=True)
A.box('ag1',  95, 310, 150, 75, 'Agents', 'push', kind='ok', step=0, focus=0, small=True)
A.arrow('h1', 'ag1', step=0, focus=0)

A.box('col1', 290, 250, 165, 105, 'Collector', 'local, per DC', kind='ok', step=1, focus=1)
A.arrow('ag1', 'col1', step=1, focus=1)

A.box('col2', 290, 520, 165, 95, 'Collector DC-B', '', kind='ok', step=2, focus=2, small=True)
A.box('col3', 290, 645, 165, 95, 'Collector DC-C', '', kind='ok', step=2, focus=2, small=True)

A.box('cur',  560, 180, 220, 110, 'Current state', '300k rows<br>in memory', kind='ok', step=3,
      focus=[3, 5])
A.arrow('col1', 'cur', step=3, focus=3)

A.box('tsdb', 560, 400, 220, 125, 'Time-series DB', 'compressed,<br>downsampled', kind='dp', step=4,
      focus=[4, 5])
A.arrow('col1', 'tsdb', step=4, focus=4)
A.arrow('col2', 'tsdb', step=4, focus=4, dashed=True)
A.arrow('col3', 'tsdb', step=4, focus=4, dashed=True)
A.arrow('col2', 'cur', step=3, focus=3, dashed=True)
A.arrow('col3', 'cur', step=3, focus=3, dashed=True)

A.box('alert', 860, 180, 200, 105, 'Alerting', 'on current state', kind='info', step=5, focus=5, small=True)
A.arrow('cur', 'alert', step=5, focus=5)

A.box('ui',   860, 400, 200, 110, 'Engineer UI', 'fleet view + drill', kind='info', step=6, focus=6)
A.arrow('cur', 'ui', step=6, focus=6, dashed=True)
A.arrow('tsdb', 'ui', step=6, focus=6)

A.box('rep',  1140, 400, 200, 110, 'Replicated', 'across DCs', kind='shared', step=7, focus=7, small=True)
A.arrow('tsdb', 'rep', step=7, focus=7, dashed=True)

A.note(1140, 180, 'Two stores, one stream. Current state is overwritten and tiny; history is append-only and huge.',
       step=4, kind='info', w=440)

A.narrate(0, """Hosts run an agent that pushes metrics. Push rather than pull, and I will justify that """
             """in the trade-off &mdash; at three hundred thousand hosts, discovering and polling them """
             """all is its own problem.""",
          A.flow([(170, 275), (170, 310)]))
A.narrate(1, """Agents report to a collector that is local to their own data centre. That locality is """
             """deliberate: collection must not depend on a cross-data-centre network link, because the """
             """link failing is one of the things you need to monitor.""",
          A.flow([(245, 347), (290, 302)]))
A.narrate(2, """Same in the other two data centres. Three independent collection paths.""")
A.narrate(3, """Collectors write to two places. First, current state &mdash; one row per host, """
             """overwritten on every report, three hundred megabytes, in memory. This answers """
             """&ldquo;is host X healthy right now&rdquo; in microseconds.""",
          A.flow([(455, 290), (560, 235)]))
A.narrate(4, """And second, the time-series database: append-only, compressed, downsampled as it ages. """
             """Same stream, two destinations, because the two questions want opposite storage.""",
          A.flow([(455, 310), (560, 462)]))
A.narrate(5, """Alerting runs off current state, because alerting is about now and needs to be fast.""",
          A.flow([(780, 235), (860, 232)]))
A.narrate(6, """The engineer U-I reads both: current state for the fleet view, and the time-series """
             """database when someone drills into what happened at three in the morning. One screen, """
             """two backends, and the U-I is where that split becomes visible to users.""",
          A.flow([(780, 462), (860, 455)]))
A.narrate(7, """And the time-series data is replicated across data centres, so that losing a data centre """
             """does not lose its history &mdash; which you will want precisely when investigating why """
             """you lost it.""")
A.build()

sid = beat('Deep dive 1', 'Absence of data is not bad data',
           '<div style="font-size:27px;line-height:1.7">'
           'A host stops reporting. Three completely different causes:<br>'
           '&bull; The host is <b>dead</b><br>'
           '&bull; The <b>agent</b> crashed, host is fine<br>'
           '&bull; The <b>network</b> between us is down &mdash; host is fine and still serving traffic'
           '<br><br>'
           '<span style="color:#ff9a9a">Showing all three as &ldquo;unhealthy&rdquo; is wrong and '
           'dangerous &mdash; during a network partition your dashboard reports a catastrophe that is '
           'not happening.</span><br><br>'
           '<b>So model three states, not two:</b> <span style="color:#a8e6a3">HEALTHY</span> / '
           '<span style="color:#ff9a9a">UNHEALTHY</span> / '
           '<span style="color:#ffd483">UNKNOWN</span> &mdash; and UNKNOWN is a first-class state with '
           'its own alerts and its own colour on the dashboard.<br><br>'
           '<b>Distinguishing the causes:</b><br>'
           '&bull; <b>One host silent</b>, others in the rack fine &rarr; probably that host or its '
           'agent<br>'
           '&bull; <b>Every host in a rack silent</b> &rarr; a switch<br>'
           '&bull; <b>Every host in a DC silent</b> &rarr; <span style="color:#ffd483">it is almost '
           'certainly us, not them</span><br>'
           '&bull; Collector tracks <b>how many hosts it expects</b> &mdash; a sudden drop in '
           '<i>reporters</i> is the signal, not a drop in values<br><br>'
           '<span style="color:#ffd483">Alert on &ldquo;we lost visibility&rdquo; separately from '
           '&ldquo;things are broken&rdquo;. They need different humans and different runbooks.</span>'
           '</div>',
           """Deep dive one, and this is the answer to what I asked you to pause on. A host stops """
           """reporting. There are three completely different causes: the host is dead, the agent """
           """crashed but the host is fine, or the network between us is down and the host is fine and """
           """still happily serving traffic.""", step=0)
seg(sid, 1, """Showing all three as &ldquo;unhealthy&rdquo; is both wrong and dangerous. During a """
            """network partition your dashboard reports a catastrophe that is not happening, and """
            """somebody will start failing over services that were perfectly healthy &mdash; which """
            """turns a network problem into a real outage.""")
seg(sid, 2, """So model three states rather than two: healthy, unhealthy, and unknown. And unknown is a """
            """first-class state with its own alerts and its own colour on the dashboard, not a shade """
            """of red.""")
seg(sid, 3, """Then you can distinguish the causes by scope. One host silent while its rack neighbours """
            """report fine is probably that host or its agent. Every host in a rack going silent is a """
            """switch. Every host in a data centre going silent is almost certainly us rather than """
            """them &mdash; our collector, or our link.""")
seg(sid, 4, """And the mechanism that makes this work: the collector tracks how many hosts it expects to """
            """hear from. A sudden drop in the number of reporters is the signal &mdash; not a drop in """
            """the values themselves. You are monitoring the monitoring.""")
seg(sid, 5, """So alert on &ldquo;we have lost visibility&rdquo; separately from &ldquo;things are """
            """broken&rdquo;. They need different humans and different runbooks, and conflating them """
            """means the network team gets paged about C-P-U.""")

sid = beat('Deep dive 2', 'Two stores from one stream, and the downsampling that pays for history',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Current state</b> &mdash; one row per host, overwritten. 300k rows, ~300 MB, in memory. '
           'Answers &ldquo;is X healthy&rdquo; and &ldquo;show me the fleet&rdquo; in microseconds. '
           '<span style="color:#a8e6a3">Completely rebuildable from the stream, so it needs no '
           'durability.</span><br><br>'
           '<b>History</b> &mdash; append-only, compressed, never updated. Billions of points.<br><br>'
           '<b>Why a time-series DB rather than a normal database:</b><br>'
           '&bull; <b>Delta-of-delta</b> on timestamps &mdash; regular intervals compress to almost '
           'nothing<br>'
           '&bull; <b>XOR</b> on values &mdash; consecutive CPU readings differ in few bits<br>'
           '&bull; Together: <span style="color:#a8e6a3">10&ndash;20&times;</span>, which is the '
           'difference between 2 TB/day and 150 GB/day<br>'
           '&bull; Indexed by <code>(host, metric, time)</code> &mdash; so one host&rsquo;s day is a '
           'contiguous read<br><br>'
           '<b>Downsampling is what makes 13 months affordable:</b><br>'
           '10 s for 7 days &rarr; 1 min for 30 days &rarr; 5 min for 13 months. '
           '<span style="color:#ffd483">Nobody debugging a 6-month-old incident needs 10-second '
           'resolution &mdash; and if they do, that is a different (and much more expensive) '
           'product.</span></div>',
           """Deep dive two: two stores from one stream. Current state is one row per host, overwritten """
           """on every report &mdash; three hundred thousand rows, three hundred megabytes, in memory. """
           """It answers &ldquo;is X healthy&rdquo; and &ldquo;show me the fleet&rdquo; in """
           """microseconds.""", step=0)
seg(sid, 1, """And it is completely rebuildable from the stream, so it needs no durability at all. """
            """Saying what does not need to be durable is as useful as saying what does &mdash; it tells """
            """the interviewer you know what you are not paying for.""")
seg(sid, 2, """History is append-only, compressed, never updated. Billions of points. And it is worth """
            """being specific about why a dedicated time-series database rather than a normal one.""")
seg(sid, 3, """Delta-of-delta encoding on timestamps: because readings come at regular intervals, the """
            """difference between successive gaps is almost always zero, which compresses to nearly """
            """nothing. And X-O-R encoding on values: consecutive C-P-U readings differ in only a few """
            """bits, so the X-O-R is mostly zeros.""")
seg(sid, 4, """Together that is ten to twenty times compression, which is the difference between two """
            """terabytes a day and a hundred and fifty gigabytes. And indexing by host, metric and time """
            """means one host's day is a contiguous read rather than a scan.""")
seg(sid, 5, """Then downsampling, which is what makes thirteen months affordable. Ten second resolution """
            """for seven days, one minute for thirty days, five minutes for thirteen months. Nobody """
            """debugging a six-month-old incident needs ten-second resolution &mdash; and if somebody """
            """genuinely does, that is a different and much more expensive product, and it should be a """
            """conscious decision rather than an accident of retention settings.""")

tradeoff('Agents push, or collectors pull', [
 ('Pull &mdash; collector scrapes each host', 'info',
  ['Collector controls the rate &mdash; no thundering herd', 'Easy to tell a host is down: the scrape '
   'fails', 'Central config of what to collect'],
  ['<b>Must discover and track 300k hosts</b>', 'Scraping across a DC boundary is fragile',
   'Hosts behind NAT or firewalls are hard to reach', 'Scrape interval is a hard floor on freshness']),
 ('Push &mdash; agent sends to a collector', 'ok',
  ['<b>No discovery problem</b> &mdash; new hosts just start reporting',
   'Works through firewalls and NAT', 'Agent can buffer locally when the collector is unreachable'],
  ['Collector must handle unpredictable load', '<b>Silence is ambiguous</b> &mdash; dead host or dead '
   'agent?', 'Agent config must be distributed to every host']),
 ('Push to a local collector, pull between DCs', 'shared',
  ['Local push avoids discovery', 'Cross-DC is a controlled, batched transfer',
   'Collection survives DC isolation'],
  ['Two mechanisms to operate', 'Collector becomes a per-DC single point of failure &mdash; so it '
   'needs its own redundancy']),
], 'Push to a local per-DC collector, with cross-DC replication of the aggregated stream. At 300k hosts '
   'the discovery problem alone rules out pull.',
 'If the fleet were small and stable &mdash; a few thousand hosts, centrally managed &mdash; I would '
 'pull, because unambiguous &ldquo;the scrape failed&rdquo; is genuinely easier to reason about than '
 'interpreting silence.',
 [
 """Trade-off: do agents push, or do collectors pull? Pull means the collector controls the rate so """
 """there is no thundering herd, it is easy to tell a host is down because the scrape simply fails, and """
 """configuration of what to collect is central. The costs are that you must discover and track three """
 """hundred thousand hosts, scraping across a data centre boundary is fragile, hosts behind N-A-T are """
 """hard to reach, and the scrape interval becomes a hard floor on freshness.""",
 """Push means no discovery problem &mdash; a new host just starts reporting &mdash; it works through """
 """firewalls, and the agent can buffer locally when the collector is unreachable. The costs are """
 """unpredictable load on the collector, ambiguous silence, and having to distribute agent """
 """configuration to every host.""",
 """Pushing to a local collector with controlled cross-data-centre transfer is the combination: local """
 """push avoids discovery, the cross-D-C hop is batched and controlled, and collection survives """
 """isolation.""",
 """I would take that. At three hundred thousand hosts the discovery problem alone rules out pull """
 """&mdash; maintaining an accurate list of every host in a fleet that size is its own distributed """
 """systems problem, and you would be solving it in order to solve monitoring.""",
 """And what would flip it: a small stable fleet of a few thousand centrally managed hosts. Then I """
 """would pull, because &ldquo;the scrape failed&rdquo; is unambiguous and genuinely easier to reason """
 """about than interpreting silence &mdash; which, as we saw, needs a whole three-state model.""",
])

failures('What happens when each piece dies', [
 ('A host&rsquo;s agent crashes', 'That host shows UNKNOWN, not unhealthy',
  '<b>Three-state model earns its keep.</b> Alert on UNKNOWN separately; a crashed agent is an agent '
  'problem, not a host problem'),
 ('A collector in one DC fails', 'That DC goes dark',
  'Agents <b>buffer locally</b> and drain when it returns. Run collectors redundantly per DC &mdash; '
  'a single collector is a single point of failure for an entire data centre'),
 ('Cross-DC link is lost', 'Central views miss one DC',
  '<b>Local collection and local alerting keep working.</b> This is the main argument for per-DC '
  'collection &mdash; an isolated DC can still page its own on-call'),
 ('The TSDB is unavailable', 'History queries fail; current state is fine',
  '<b>Alerting is unaffected</b>, because it reads current state. A forensics outage is not an '
  'alerting outage &mdash; keeping them separate is why'),
 ('An engineer queries 6 months at 10 s resolution', 'Enormous query, possible OOM',
  'Downsampling means that data <b>does not exist</b> at that resolution. Enforce resolution by age, '
  'and reject rather than attempt'),
 ('Monitoring system itself goes down', 'Total blindness &mdash; and silence looks like health',
  '<b>Monitor the monitoring, from somewhere else.</b> A dead-man&rsquo;s switch: if the system stops '
  'reporting that it is alive, page someone'),
], [
 """Failures. A host's agent crashes and that host shows unknown rather than unhealthy. The three-state """
 """model earns its keep immediately, and alerting on unknown separately means a crashed agent is """
 """triaged as an agent problem rather than waking someone to investigate a healthy machine.""",
 """A collector in one data centre fails and that data centre goes dark. Agents buffer locally and """
 """drain when it comes back. And run collectors redundantly per data centre &mdash; a single collector """
 """is a single point of failure for a hundred thousand hosts, which is not a risk worth taking to save """
 """one machine.""",
 """Cross-data-centre link lost: central views miss one data centre, but local collection and local """
 """alerting keep working. This is the main argument for collecting locally &mdash; an isolated data """
 """centre can still page its own on-call engineer, which is exactly when you need it to.""",
 """Time-series database unavailable means history queries fail while current state is fine, so """
 """alerting is entirely unaffected. A forensics outage is not an alerting outage, and the only reason """
 """that is true is that you kept them in separate stores.""",
 """An engineer querying six months at ten second resolution would be an enormous query &mdash; except """
 """that downsampling means the data does not exist at that resolution. Enforce resolution by age and """
 """reject the query with a clear message rather than attempting it and falling over.""",
 """And the monitoring system itself going down is total blindness, where silence looks exactly like """
 """health. So monitor the monitoring, from somewhere else &mdash; a dead man's switch, where if the """
 """system stops reporting that it is alive, something external pages a human. Every mature monitoring """
 """setup has one, and candidates almost never mention it.""",
])

say('What I should actually say in the room', [
 'There are two questions here that want opposite storage. &ldquo;Is this host healthy now&rdquo; is '
 'one overwritten row per host &mdash; 300k rows, 300 MB, in memory. &ldquo;What happened last '
 'Tuesday&rdquo; is append-only and enormous. So: two stores, one stream.',
 'Current state is rebuildable from the stream, so it needs no durability at all.',
 'History goes in a time-series database, and I would justify that specifically: delta-of-delta on '
 'timestamps plus XOR on values gives 10&ndash;20&times; compression, which is 2 TB a day versus 150 '
 'GB.',
 'Downsampling is what makes 13 months affordable &mdash; 10 seconds for a week, a minute for a month, '
 'five minutes for a year.',
 'Agents push to a collector local to their own data centre, because at 300k hosts the discovery '
 'problem alone rules out pull &mdash; and because collection must not depend on the cross-DC link, '
 'since that link failing is one of the things I am monitoring.',
 'The most important modelling decision is three states, not two: healthy, unhealthy, and unknown. A '
 'silent host might be dead, or its agent might be dead, or the network might be down &mdash; and '
 'showing all three as unhealthy means your dashboard reports a catastrophe during a network partition.',
 'So I alert on &ldquo;we lost visibility&rdquo; separately from &ldquo;things are broken&rdquo;, and I '
 'put a dead-man&rsquo;s switch on the monitoring system itself.',
], [
 """The sentences. Open with the two-stores observation, because it is the structural insight and it """
 """takes ten seconds.""",
 """Then the compression and downsampling numbers, which justify the technology choice rather than """
 """asserting it. Then push-versus-pull with the discovery argument.""",
 """Then the three-state model, which is the thing most candidates miss and the thing an infrastructure """
 """interviewer will care most about. Finish on the dead man's switch &mdash; it is a short sentence """
 """that signals operational experience.""",
])

followups([
 'How do agents collect and report?',
 'How do you ingest at this volume?',
 'How do you store current health?',
 'How do you store history?',
 'What retention and downsampling?',
 'How does the engineer UI query it?',
 'How do you handle a DC being isolated?',
 'How do you alert?',
], [
 'How do you detect a slow degradation rather than a hard failure?',
 'An engineer wants to compare two incidents six months apart. Can you?',
 'How do you avoid alert fatigue across 300k hosts?',
 'What does this cost, and what would you cut first?',
 'How would you add per-team custom health definitions without a deploy?',
],
 """The reported follow-ups are the lesson. On the engineer U-I specifically: the fleet view reads """
 """current state, and drilling into a host reads the time-series store &mdash; and the U-I should make """
 """that boundary invisible to the user while the engineer building it keeps it very visible.""",
 """The staff-level follow-ups go after what monitoring is actually for. Slow degradation is not caught """
 """by thresholds, it needs comparison against a baseline &mdash; this host versus its peers, or this """
 """week versus last. Comparing two incidents six months apart is exactly why you keep thirteen months, """
 """and it is the justification for the retention bill. Alert fatigue at three hundred thousand hosts """
 """is the real operational problem &mdash; you alert on services and aggregates rather than on """
 """individual hosts, because a single host being unhealthy is normal at that fleet size. Cost: history """
 """dominates, so the first cut is shorter retention at high resolution. And per-team health """
 """definitions without a deploy is configuration distribution &mdash; the versioned push with a pull """
 """fallback from lesson four point four, reused.""")

cheatsheet('Host health monitoring &mdash; the one-page card', [
 ('Requirements', 'Collect signals from 300k hosts in 3 DCs; current health; history; an engineer UI '
                  'for forensics'),
 ('Scale', '~1.5M points/s, ~2 TB/day raw &rarr; ~150 GB/day compressed; current state ~300 MB; '
           '~15&ndash;20 TB retained'),
 ('Core architecture', 'Agent push &rarr; per-DC collector &rarr; <b>two stores</b>: in-memory current '
                       'state, and a compressed downsampled TSDB'),
 ('Data store', 'Current state in memory (rebuildable, no durability needed); TSDB indexed by '
                '<code>(host, metric, time)</code>'),
 ('Partition key', '<code>hostId</code> (or host+metric) &mdash; so one host&rsquo;s history is a '
                   'contiguous read rather than a scan'),
 ('Cache', 'Current state <i>is</i> the cache. Recent query results for dashboards'),
 ('Queue', 'Agent-local buffer so a collector outage loses nothing; cross-DC replication stream'),
 ('Consistency', 'Eventual. Freshness bounded by the reporting interval (~10 s)'),
 ('Failure handling', '<b>Three states: healthy / unhealthy / UNKNOWN</b>; alert on lost visibility '
                      'separately; dead-man&rsquo;s switch on the monitoring itself'),
 ('Key deep dives', 'Absence of data &ne; bad data &middot; two stores from one stream'),
 ('Biggest trade-off', 'Resolution and retention vs cost &mdash; resolved by <b>downsampling by '
                       'age</b>'),
], [
 """The card. Scale carries the compression win: two terabytes a day raw down to a hundred and fifty """
 """compressed.""",
 """Architecture is agent push to a per-data-centre collector feeding two stores. Note the data store """
 """row &mdash; current state needs no durability because it is rebuildable, and the T-S-D-B is indexed """
 """by host, metric and time so a host's day is contiguous.""",
 """Failure handling leads with the three-state model and ends with the dead man's switch. And the """
 """biggest trade-off is resolution and retention against cost, resolved by downsampling by age.""",
])

say('The 60-second answer', [
 'There are two questions here that want opposite storage. &ldquo;Is this host healthy right now&rdquo; '
 'is one row per host, overwritten constantly &mdash; 300,000 rows, about 300 MB, which fits in memory. '
 '&ldquo;What was happening at 3 a.m. last Tuesday&rdquo; is append-only and enormous. So I build two '
 'stores from one stream.',
 'Current state is fully rebuildable from the stream, so it needs no durability, and alerting runs off '
 'it &mdash; which means a history outage is never an alerting outage.',
 'History goes into a time-series database, and the justification is concrete: delta-of-delta on '
 'timestamps plus XOR on values gives ten to twenty times compression, so 2 TB a day becomes about 150 '
 'GB. Downsampling by age &mdash; 10 seconds for a week, a minute for a month, five minutes for a year '
 '&mdash; is what makes 13 months affordable.',
 'Agents push to a collector local to their own data centre. At 300,000 hosts the discovery problem '
 'alone rules out pull, and collection must not depend on the cross-DC link, because that link failing '
 'is one of the things I am monitoring.',
 'The most important modelling decision is three states rather than two: healthy, unhealthy, and '
 'unknown. A silent host might be dead, or its agent might be dead, or the network might be down '
 '&mdash; and showing all three as unhealthy means your dashboard reports a catastrophe during a '
 'network partition.',
 'So I alert on lost visibility separately from things being broken, and I put a dead-man&rsquo;s '
 'switch on the monitoring system itself &mdash; because if monitoring dies, silence looks exactly like '
 'health.',
], [
 """The sixty-second answer. The two-stores opening is the structural insight, and the compression """
 """numbers make the technology choice an argument rather than a preference.""",
 """The last two sentences are what an infrastructure interviewer is listening for. Practise """
 """&ldquo;silence looks exactly like health&rdquo; &mdash; it is short, it is true, and it is the """
 """sentence that tells them you have been on call.""",
], kicker='60-second interview answer')
