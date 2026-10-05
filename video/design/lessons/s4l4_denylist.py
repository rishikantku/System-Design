# -*- coding: utf-8 -*-
"""Chapter 4, Lesson 4 — the malicious-IP denylist."""
from lib import *

lesson_header('4.4', 'Design a malicious-IP denylist',
              'Control plane &middot; propagation to a fleet &middot; staleness budget',
              dict(reports='InterviewTV list, and 1 report in research pass 3',
                   latest='2026', level='Staff',
                   conf='MEDIUM &mdash; corroborated, thin detail',
                   sources='InterviewTV.io + research pass 3'), 16,
              """Chapter four, lesson four, and the one that ties the chapter together. LinkedIn receives """
              """malicious traffic. You are given a function, isMalicious, that tells you whether a """
              """request is bad. Design the system that denylists those I-P addresses, and make sure """
              """every web server has an up-to-date copy of the list. Note where the emphasis is: not """
              """detection — you were handed that — but <i>distribution</i>. This is a propagation """
              """problem wearing a security costume.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  '<code>isMalicious()</code> is <b>given</b>. The named focus is detection, central denylist, '
  'distribution, propagation, caching, consistency, update latency, <b>millions of web servers</b>, '
  'stale lists, recovery'),
 ('Research pass 3 &mdash; candidate report', '2026', 'Staff',
  '&ldquo;Design a system that intercepts and blocks malicious requests&rdquo; &mdash; one report, '
  'thin detail'),
], """Two sources, so medium confidence. And read the framing carefully, because it is unusually """
     """generous: isMalicious is given to you. The hard algorithmic bit has been removed on purpose.""",
 ["""What is left in the named focus list is distribution, propagation, update latency, millions of web """
  """servers, stale lists and recovery. Six of those ten words are about getting data to machines. The """
  """interviewer has told you what the question is about — the trick is believing them and not spending """
  """twenty minutes on detection heuristics you were explicitly excused from."""],
 caveat='Two sources, both thin. The propagation machinery here is the same shape as config '
        'distribution and feature flags, so it generalises well.',
 narration_caveat="""Two sources, both thin on detail. But the propagation machinery is the same shape """
                  """as config distribution and feature flags, so it generalises well beyond this """
                  """question.""")

sid = beat('Why this is interesting', 'Two clocks, running in opposite directions',
           '<div style="font-size:28px;line-height:1.72">'
           'Every decision in this system sits between two clocks:<br><br>'
           '<b>The attacker&rsquo;s clock.</b> From the first malicious packet to the block taking '
           'effect, the attacker is being served. Every second of propagation delay is damage.<br><br>'
           '<b>The fleet&rsquo;s clock.</b> Millions of servers cannot each poll a central service '
           'every second. That is millions of QPS to protect against something measured in thousands.'
           '<br><br>'
           '<span style="color:#ffd483">So: what is the acceptable staleness? Everything follows from '
           'that one number, and the interviewer will not volunteer it.</span><br><br>'
           'And the asymmetry that shapes the whole design:<br>'
           '&bull; <b>Adding</b> an IP late &rarr; an attacker gets a few more seconds. Annoying.<br>'
           '&bull; <b>Removing</b> an IP late &rarr; an innocent user (behind carrier-grade NAT, with '
           'thousands of others) stays blocked. <span style="color:#ff9a9a">Much worse.</span><br><br>'
           '<span style="color:#a8e6a3">Removals need to propagate faster than additions.</span></div>',
           """Why is this interesting? Because every decision sits between two clocks running in """
           """opposite directions.""", step=0)
seg(sid, 1, """The attacker's clock: from the first malicious packet to the block actually taking """
            """effect, you are still serving them. Every second of propagation delay is damage, so you """
            """want propagation to be instant.""")
seg(sid, 2, """The fleet's clock: millions of servers cannot each poll a central service every second. """
            """That is millions of queries per second spent protecting yourself from something measured """
            """in thousands. So you want propagation to be infrequent. Those two pull directly against """
            """each other, and the question that resolves them is — what staleness is acceptable? The """
            """interviewer will not volunteer that number. Ask for it.""")
seg(sid, 3, """And then there is an asymmetry that shapes the whole design, which almost nobody raises. """
            """Adding an I-P late means an attacker gets a few more seconds of service. Annoying, """
            """survivable. Removing an I-P late means an innocent user stays blocked — and behind """
            """carrier-grade NAT that one I-P might be thousands of real people.""")
seg(sid, 4, """So removals need to propagate faster than additions. Same system, two different urgency """
            """budgets, and the reason is who gets hurt. That is a sentence worth saying out loud early, """
            """because it reframes the problem from &ldquo;distribute a list&rdquo; to """
            """&ldquo;distribute two things with different SLAs&rdquo;.""")

think('You have one million web servers and a denylist that must be at most 10 seconds stale. Polling a '
      'central service every 10 seconds is 100,000 requests per second, just for the list. What would you '
      'do instead — and what does your answer cost you when a server has been disconnected for an hour?',
      25,
      """Pause here. One million web servers, denylist must be at most ten seconds stale. Polling """
      """centrally every ten seconds is a hundred thousand requests a second just to distribute a list. """
      """What would you do instead? And what does your answer cost you when a server has been """
      """disconnected for an hour? Say it out loud.""",
      """Hold onto that second half. The disconnected-server case is where most propagation designs """
      """quietly fall apart, and we will come back to it.""")

clarify('What I would clarify first', [
 ('What staleness is acceptable &mdash; seconds, or minutes?',
  '<b>The number that picks the whole architecture.</b> Minutes means simple polling. Sub-second means '
  'push, and a much more expensive system.'),
 ('How many entries will the list hold?',
  'Ten thousand fits in a hash set anywhere. A hundred million needs a <b>compact structure</b> and '
  'changes how you ship it.'),
 ('Block at the edge, or at every web server?',
  'The prompt says every web server &mdash; but I would push back. <b>Blocking at the edge stops the '
  'traffic before it costs you anything</b>, and there are far fewer edge nodes to update.'),
 ('What is the false-positive tolerance?',
  'Decides whether a probabilistic structure is allowed at all. With CGNAT, one bad IP can be '
  'thousands of real users.'),
 ('Do entries expire, or are they permanent?',
  'TTLs make the list <b>self-cleaning</b> and shrink the removal problem enormously. Permanent entries '
  'grow forever and make removal a first-class workflow.'),
 ('Is <code>isMalicious</code> called inline or offline?',
  'Inline means it is on the latency path of every request &mdash; a completely different budget. I '
  'would assume offline over a sample and confirm.'),
], [
 """What staleness is acceptable — seconds or minutes? This is the number that picks the entire """
 """architecture, and it is the first thing I would ask. Minutes means simple polling and a very easy """
 """system. Sub-second means push, and a considerably more expensive one.""",
 """How many entries? Ten thousand fits in a hash set literally anywhere and needs no cleverness. A """
 """hundred million needs a compact structure and changes how you ship it. Ask before you pick a data """
 """structure.""",
 """Block at the edge or at every web server? The prompt says every web server, but I would push back """
 """politely — blocking at the edge stops the traffic before it costs you anything, and there are far """
 """fewer edge nodes to keep updated. Pushing back on a premise, with a reason, is usually rewarded.""",
 """What is the false-positive tolerance? That decides whether a probabilistic structure is allowed at """
 """all. Remember carrier-grade NAT: one bad I-P can be thousands of real users sharing it.""",
 """Do entries expire? T-T-Ls make the list self-cleaning and shrink the removal problem enormously. """
 """Permanent entries grow forever and turn removal into a first-class workflow someone has to own.""",
 """And is isMalicious called inline or offline? Inline means it sits on the latency path of every """
 """single request, which is a completely different budget. I would assume offline over a sample and """
 """say so, rather than silently assuming either way.""",
])

capacity('Capacity', [
 ('1M web servers, 10 s staleness target', '1M &divide; 10 s',
  '&asymp; 100,000 poll / s', '<b>Rules out naive polling.</b> The distribution costs more than the attack'),
 ('Denylist size: 1M IPs &times; 4 B (v4)', '1M &times; ~20 B with metadata', '&asymp; 20 MB full list',
  'Too big to re-ship every 10 s to 1M servers &mdash; that is 20 TB/s'),
 ('Deltas instead: ~1,000 changes / min', '1,000 &times; 20 B', '&asymp; 20 KB / min',
  '<b>A million times smaller.</b> Ship deltas, not the list'),
 ('Delta fanout to 1M servers', '20 KB &times; 1M &divide; 60 s', '&asymp; 330 MB / s',
  'Fine for a <b>tiered</b> fanout; fatal for a single origin. Hence a distribution tree'),
 ('Bloom filter for 1M IPs, 0.1% FP', '~1.8 MB', '<b>1.8 MB, fixed</b>',
  'Cheap to hold everywhere &mdash; but FPs block real users. <b>Use as a pre-filter only</b>'),
 ('Lookup cost per request', 'in-process hash set', '&asymp; 50&ndash;100 ns',
  'Effectively free. <b>The check is never the problem; the update is</b>'),
], [
 """Numbers. A million web servers and a ten second staleness target means a hundred thousand polls a """
 """second just to distribute a list. That rules out naive polling immediately — your distribution """
 """system would cost more to run than the attack costs you.""",
 """The list itself: a million I-Ps with metadata is about twenty megabytes. Re-shipping that to a """
 """million servers every ten seconds is twenty terabytes a second, which is an absurd number and worth """
 """saying out loud precisely because it is absurd.""",
 """Deltas instead. Roughly a thousand changes a minute at twenty bytes each is twenty kilobytes a """
 """minute. A million times smaller. So the first architectural decision falls straight out: ship """
 """deltas, not the list.""",
 """Fanning twenty kilobytes to a million servers every minute is about three hundred and thirty """
 """megabytes a second. That is completely fine through a tiered distribution tree and fatal from a """
 """single origin. So you need a tree, and the arithmetic told you rather than your instinct.""",
 """A Bloom filter over a million I-Ps at a tenth of a percent false positive rate is one point eight """
 """megabytes, fixed size regardless of growth. Cheap to hold everywhere — but false positives block """
 """real users, so I would use it as a pre-filter and confirm against the exact set, never as the final """
 """answer.""",
 """And the lookup itself is an in-process hash set probe: fifty to a hundred nanoseconds. Effectively """
 """free. That is the line I want you to remember for this question — the check is never the problem, """
 """the update is.""",
])

A = Arch('Denylist &mdash; a control plane and a distribution tree', kicker='Architecture', height=800)

A.zone(540, 120, 560, 250, 'CONTROL PLANE — decides')
A.zone(540, 420, 900, 330, 'DATA PLANE — enforces')

A.box('req',  60, 250, 155, 85, 'Traffic', '', kind='neutral', step=0, focus=0, small=True)
A.box('edge', 260, 240, 205, 105, 'Edge / LB', 'enforce here first', kind='ok', step=0, focus=[0, 6])
A.arrow('req', 'edge', step=0, focus=0)

A.box('samp', 580, 160, 200, 90, 'Sampler', 'async, off-path', kind='shared', step=1, focus=1, small=True)
A.box('det',  830, 160, 235, 90, 'isMalicious()', 'given to us', kind='info', step=1, focus=1, small=True)
A.arrow('edge', 'samp', step=1, focus=1, dashed=True)
A.arrow('samp', 'det', step=1, focus=1)

A.box('dec',  700, 275, 250, 85, 'Decision service', 'threshold + TTL', kind='ok', step=2, focus=2, small=True)
A.arrow('det', 'dec', step=2, focus=2)

A.box('db',  1140, 265, 210, 95, 'Denylist store', 'source of truth', kind='dp', step=3, focus=3, small=True)
A.arrow('dec', 'db', step=3, focus=3)

A.box('pub',  580, 470, 200, 90, 'Delta publisher', 'versioned', kind='shared', step=4, focus=4, small=True)
A.arrow('db', 'pub', step=4, focus=4, dashed=True)

A.box('t1',  830, 470, 185, 90, 'Regional relay', '~100 nodes', kind='info', step=5, focus=5, small=True)
A.box('t2',  830, 600, 185, 90, 'Regional relay', '', kind='info', step=5, focus=5, small=True)
A.arrow('pub', 't1', step=5, focus=5); A.arrow('pub', 't2', step=5, focus=5)

A.box('srv', 1140, 470, 230, 90, 'Web servers', '1M, local set', kind='ok', step=6, focus=6, small=True)
A.box('srv2',1140, 600, 230, 90, 'Web servers', 'in-process', kind='ok', step=6, focus=6, small=True)
A.arrow('t1', 'srv', step=6, focus=6); A.arrow('t2', 'srv2', step=6, focus=6)

A.note(1400, 160, 'Detection is OFF the request path. A slow detector must never slow a request.',
       step=1, kind='info', w=420)
A.note(1400, 600, 'Every server holds the full set in process. Lookup is a hash probe: ~100 ns.',
       step=6, kind='info', w=420)

A.narrate(0, """Traffic arrives at the edge. I am putting the first enforcement point here rather than """
             """only at the web servers, and I would argue for it: blocking at the edge means the """
             """malicious request never consumes a connection, a thread, or a database query """
             """downstream.""",
          A.flow([(215, 292), (260, 292)]))
A.narrate(1, """Detection. The edge asynchronously samples traffic to a detector that calls the given """
             """isMalicious function. Note the word asynchronously and note the dashed line — detection """
             """is off the request path. If the detector is slow, requests must not be. That is the """
             """single most important structural choice on this slide.""",
          A.flow([(465, 270), (580, 205), (830, 205)]))
A.narrate(2, """A decision service turns detections into denylist entries. Not one-to-one — you want a """
             """threshold, because a single malicious packet from an I-P that serves a university """
             """campus is not grounds for blocking thousands of people. And every entry gets a """
             """T-T-L.""",
          A.flow([(1065, 205), (950, 275)]))
A.narrate(3, """The denylist store is the source of truth. Small, versioned, and boring on purpose — """
             """this is the thing everything else reconciles against.""",
          A.flow([(950, 318), (1140, 312)]))
A.narrate(4, """A delta publisher emits versioned changes. Versioned matters enormously and we will come """
             """back to it: a server that has been offline needs to be able to say &ldquo;I am at """
             """version four thousand and twelve, what have I missed?&rdquo;""",
          A.flow([(1140, 330), (680, 470)]))
A.narrate(5, """Then a distribution tree. Regional relays — maybe a hundred of them — fan the deltas out. """
             """This is the tier that turns an impossible single-origin fanout into an easy one, and it """
             """exists because the arithmetic said so.""",
          A.flow([(780, 515), (830, 515)]))
A.narrate(6, """And every web server holds the full set in process. The lookup is a hash probe, about a """
             """hundred nanoseconds, so enforcement is effectively free. All of the engineering in this """
             """design is in keeping that in-process set fresh — not in using it.""",
          A.flow([(1015, 515), (1140, 515)]))
A.build()

sid = beat('Deep dive 1', 'Push vs pull, and the version number that saves you',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Pure pull</b> &mdash; every server polls every N seconds.<br>'
           '<span style="color:#a8e6a3">Dead simple; self-healing; a restarted server just polls.</span> '
           '<span style="color:#ff9a9a">100k QPS at 10 s staleness, and the load is constant whether '
           'anything changed or not.</span><br><br>'
           '<b>Pure push</b> &mdash; publisher streams deltas to every server.<br>'
           '<span style="color:#a8e6a3">Near-instant; traffic proportional to <i>changes</i>, not to '
           'fleet size.</span> '
           '<span style="color:#ff9a9a">1M long-lived connections; a missed message is missed forever.</span>'
           '<br><br>'
           '<b>What actually works &mdash; push with a versioned pull fallback:</b><br>'
           '&bull; Each server holds <code>version</code>. Publisher pushes <code>(version, delta)</code>.<br>'
           '&bull; Gap detected (<code>received &ne; local + 1</code>) &rarr; server pulls a snapshot '
           '+ deltas since its version.<br>'
           '&bull; A server offline for an hour reconnects, sees the gap, and <b>self-heals</b>.<br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: push for latency, pull for correctness. '
           'The version number is what lets you have both.</span></div>',
           """Deep dive one, and this is the answer to what I asked you to pause on. Push or pull?""",
           step=0)
seg(sid, 1, """Pure pull — every server polls every N seconds — is dead simple and self-healing. A """
            """restarted server just polls and it is correct. The cost is a hundred thousand queries a """
            """second at ten second staleness, and that load is constant whether anything changed or """
            """not. You are paying full price for silence.""")
seg(sid, 2, """Pure push streams deltas out and is near-instant, and its traffic is proportional to the """
            """number of changes rather than the size of the fleet, which is a much better shape. The """
            """cost is a million long-lived connections to manage, and the fatal flaw: a missed message """
            """is missed forever. A server that was briefly disconnected is now silently wrong, and """
            """nothing in the system will ever notice.""")
seg(sid, 3, """What actually works is push with a versioned pull fallback. Each server tracks a version """
            """number. The publisher pushes version and delta together. If a server receives version """
            """four thousand and twenty when it holds four thousand and twelve, it knows it has a gap """
            """and pulls a snapshot plus the deltas since its version.""")
seg(sid, 4, """So a server offline for an hour reconnects, immediately detects the gap, and self-heals """
            """without anyone intervening. That is the staff-level insight: push for latency, pull for """
            """correctness, and the version number is the mechanism that lets you have both. This exact """
            """pattern shows up in config distribution, feature flags, service discovery and schema """
            """registries — learn it once here and you will recognise it everywhere.""")

sid = beat('Deep dive 2', 'Removal, false positives, and the blast radius of one bad entry',
           '<div style="font-size:28px;line-height:1.72">'
           'Adding is easy. <b>Removing is the dangerous direction</b>, and the reason is who is hurt.'
           '<br><br>'
           '<b>One IP is not one person.</b> Carrier-grade NAT, corporate proxies and university '
           'gateways put <i>thousands</i> of users behind a single address. Blocking it is a '
           'small outage.<br><br>'
           '<b>So:</b><br>'
           '&bull; <b>TTL on every entry.</b> The list self-heals even if removal breaks. Default to '
           'hours, not forever.<br>'
           '&bull; <b>Removals propagate on the fast path</b> &mdash; higher priority than additions, '
           'because the cost of lateness is asymmetric.<br>'
           '&bull; <b>Never fully block on a probabilistic structure.</b> Bloom filter says maybe &rarr; '
           'confirm against the exact set.<br>'
           '&bull; <b>Always maintain an allowlist</b> that wins over the denylist &mdash; your own '
           'office, your monitoring, your partners.<br>'
           '&bull; <b>Degrade instead of blocking</b> where you can: CAPTCHA or rate-limit before an '
           'outright 403.<br><br>'
           '<span style="color:#a8e6a3">A denylist with no removal path is an outage generator with a '
           'security label on it.</span></div>',
           """Deep dive two: removal. Adding is easy. Removing is the dangerous direction, and it is """
           """dangerous because of who gets hurt.""", step=0)
seg(sid, 1, """One I-P is not one person. Carrier-grade NAT, corporate proxies and university gateways """
            """put thousands of users behind a single address. Blocking one of those is not a security """
            """action, it is a small outage that you have chosen to cause.""")
seg(sid, 2, """So: a T-T-L on every entry, so the list self-heals even if your removal path is broken. """
            """Default to hours rather than forever. And removals propagate on the fast path, at higher """
            """priority than additions — because the cost of being late is asymmetric, which is the """
            """point I made at the start now turning into an actual design decision.""")
seg(sid, 3, """Never block outright on a probabilistic structure. If the Bloom filter says maybe, confirm """
            """against the exact set. A false positive in a Bloom filter is a real user seeing a """
            """four-oh-three for no reason they can discover.""")
seg(sid, 4, """Always maintain an allowlist that wins over the denylist — your own offices, your """
            """monitoring, your major partners. And where you can, degrade rather than block: a CAPTCHA """
            """or a rate limit before an outright rejection. The sentence I would leave the interviewer """
            """with is that a denylist with no removal path is an outage generator with a security """
            """label on it.""")

tradeoff('Where enforcement happens', [
 ('At every web server only', 'info',
  ['What the prompt asked for', 'Enforcement is close to the application, which can add context'],
  ['1M servers to keep in sync', 'The malicious request has already consumed a connection and a thread',
   '<b>You pay for the attack before you block it</b>']),
 ('At the edge only', 'shared',
  ['~1,000 nodes instead of 1M &mdash; propagation is 1000&times; easier',
   'Traffic dies before it costs anything downstream'],
  ['Edge may not see what the app sees', 'Internal/east-west traffic bypasses it entirely']),
 ('Edge primary, servers as defence in depth', 'ok',
  ['Blocks almost everything at the cheapest point', 'Servers still protected if the edge is bypassed',
   'Server-side list can be staler &mdash; it is a backstop, not the front line'],
  ['Two enforcement points to keep consistent', 'Two places to debug when something is wrongly blocked']),
], 'Edge primary with servers as defence in depth &mdash; and crucially, the <b>server-side list is '
   'allowed to be staler</b>, which makes the million-server propagation problem far less urgent.',
 'If a significant share of the abuse were internal, east-west traffic that never crosses the edge, I '
 'would invert this and make the server-side list the primary enforcement point.',
 [
 """Trade-off: where does enforcement happen? At every web server is what the prompt asked for, and it """
 """means a million servers to keep in sync — and the malicious request has already consumed a """
 """connection and a thread before you reject it. You are paying for the attack and then blocking """
 """it.""",
 """At the edge only means about a thousand nodes instead of a million, so propagation becomes a """
 """thousand times easier, and traffic dies before it costs you anything. The gap is that the edge may """
 """not see what the application sees, and internal east-west traffic bypasses it completely.""",
 """Edge primary with the servers as defence in depth blocks almost everything at the cheapest point """
 """while keeping the servers protected if the edge is bypassed. Two enforcement points to keep """
 """consistent, and two places to look when someone is wrongly blocked.""",
 """That is what I would choose — and here is the part worth saying explicitly, because it is the """
 """cleverest move available in this question. If the edge is the primary enforcement point, the """
 """server-side list is allowed to be staler, because it is a backstop rather than the front line. """
 """Which means the terrifying million-server ten-second propagation problem from the capacity slide """
 """largely evaporates. You solved the hard problem by making it not need solving.""",
 """What would flip it: if a meaningful share of the abuse were internal traffic that never crosses the """
 """edge, I would invert this and make the server-side list primary.""",
])

failures('What happens when each piece dies', [
 ('Publisher is down', 'Nothing immediately',
  'Servers keep their last-known list and keep enforcing. <b>Staleness grows silently</b> &mdash; so '
  'every server must export the <i>age</i> of its list and you alert on that, not on the publisher'),
 ('A server misses a delta', 'That server under-blocks',
  'Version gap detected on the next push &rarr; snapshot pull. <b>The version number is the entire '
  'recovery mechanism</b>'),
 ('Server offline for an hour, then returns', 'Briefly serves blocked IPs',
  'Reconnects, sees a large version gap, pulls a full snapshot before accepting traffic. <b>Gate '
  'readiness on list freshness</b>, not just on process start'),
 ('Denylist store is unavailable', 'Nothing &mdash; enforcement is local',
  '<b>Fail open on the control plane</b>: no new entries, existing enforcement continues. Detection '
  'stalls, protection freezes rather than disappearing'),
 ('A bad entry blocks a huge CGNAT range', 'Thousands of real users get 403s',
  'This is the <b>most likely real incident</b>. Needs: a fast global kill-switch, an allowlist that '
  'wins, and TTLs so it expires even if nobody acts'),
 ('Detector is compromised or buggy &mdash; floods entries', 'Widespread wrongful blocking',
  '<b>Rate-limit the control plane itself.</b> Cap additions per minute and require review above a '
  'threshold. The system that blocks needs limits on how fast it can block'),
], [
 """Failures. Publisher down: nothing happens immediately, servers keep their last list and keep """
 """enforcing. Staleness grows silently, which is the dangerous part. So every server exports the age """
 """of its list, and you alert on list age rather than on publisher health — because the thing you """
 """actually care about is freshness at the edge, not liveness at the source.""",
 """A server misses a delta and under-blocks until the next push reveals the version gap, at which """
 """point it pulls a snapshot. The version number is not a nice-to-have, it is the entire recovery """
 """mechanism.""",
 """A server offline for an hour comes back and briefly serves blocked I-Ps. The fix is to gate """
 """readiness on list freshness rather than on the process having started — do not take traffic until """
 """your list is current. That is a one-line health check that removes a whole class of incident.""",
 """Denylist store unavailable: enforcement is local so nothing visible happens. Fail open on the """
 """control plane — no new entries get added, existing enforcement continues. Protection freezes rather """
 """than disappearing, which is the right failure mode.""",
 """A bad entry blocks a huge NAT range and thousands of real users get four-oh-threes. I would say """
 """plainly that this is the most likely real incident this system will ever have — far likelier than """
 """any attack it prevents. It needs a fast global kill-switch, an allowlist that wins, and T-T-Ls so """
 """it expires even if nobody is awake to act.""",
 """And the one that shows security thinking: what if the detector itself is buggy or compromised and """
 """floods entries? Rate-limit the control plane. Cap additions per minute and require review above a """
 """threshold. The system that does the blocking needs limits on how fast it is allowed to block — and """
 """notice that we are now using lesson 4.1 to protect lesson 4.4.""",
])

say('What I should actually say in the room', [
 'Detection is given to me, and the focus list is mostly about distribution &mdash; so I am going to '
 'treat this as a propagation problem, not a security-heuristics problem.',
 'First question: what staleness is acceptable? That single number decides whether this is simple '
 'polling or a push tree.',
 'I would push back gently on enforcing at every web server. Blocking at the edge kills the traffic '
 'before it costs anything, and it is a thousand nodes rather than a million.',
 'If the edge is primary, the server-side list can be staler, because it is defence in depth. That '
 'makes the hardest part of the stated problem much less urgent.',
 'Detection runs asynchronously off the request path. A slow detector must never slow a request.',
 'Distribution is push with a versioned pull fallback: servers hold a version, detect gaps, and pull a '
 'snapshot to self-heal. Push for latency, pull for correctness.',
 'Every entry has a TTL and removals propagate faster than additions, because one IP behind CGNAT can '
 'be thousands of real users &mdash; being late to unblock is worse than being late to block.',
 'And I would rate-limit the control plane itself, so a buggy detector cannot block the world.',
], [
 """The sentences. Open by naming what kind of problem this actually is — that reframing alone is worth """
 """a lot, because it tells the interviewer you read the question rather than the title.""",
 """Then the staleness question, then the push-back on enforcement location with the consequence """
 """attached: if the edge is primary, the scary part of the problem gets easier. Then detection off the """
 """path.""",
 """Then the distribution mechanism in one memorable line — push for latency, pull for correctness. """
 """Then the removal asymmetry with the reason. And finally rate-limiting your own control plane, which """
 """is the sentence that makes an interviewer think you have operated something like this rather than """
 """only designed it.""",
])

followups([
 'How does the denylist get to every server?',
 'What is the propagation latency, and how do you measure it?',
 'What happens when a server has a stale list?',
 'How do you handle millions of web servers?',
 'How do entries get removed?',
 'What if the central service is down?',
 'How do you recover a server that was disconnected?',
], [
 'You wrongly blocked a major ISP. Walk me through the next ten minutes.',
 'How do you test a change to this system without blocking real users?',
 'What stops an attacker from getting <i>your</i> IPs onto the list?',
 'How would you measure whether this system is actually working?',
 'Would you build this or buy a WAF? Where is the line?',
],
 """The reported follow-ups are almost entirely about distribution, which confirms the reading: how it """
 """gets everywhere, what the propagation latency is and how you measure it, stale lists, a million """
 """servers, removal, central service down, and disconnected-server recovery. Every one of those is """
 """answered by the push-with-versioned-pull design plus T-T-Ls.""",
 """The staff-level follow-ups are where this gets interesting. You wrongly blocked a major I-S-P — """
 """walk me through the next ten minutes, which is really asking whether you built a kill switch. How """
 """do you test a change without blocking real users, which wants shadow mode: evaluate the list, log """
 """what you would have blocked, block nothing. What stops an attacker getting your own I-Ps onto the """
 """list, which is a genuinely nasty question and the answer is the allowlist plus control-plane rate """
 """limits. How you measure whether it is working at all — and the honest answer is that you measure """
 """blocked volume and false-positive reports, and both are hard. And finally build versus buy a W-A-F, """
 """where the line is usually that you buy it until your detection logic is specific enough to your """
 """own product that nobody sells it.""")

cheatsheet('IP denylist &mdash; the one-page card', [
 ('Requirements', 'Block malicious IPs; every server current; detection is <b>given</b>'),
 ('Scale', '1M servers, ~1M entries (20 MB), ~1k changes/min (20 KB/min). Lookup ~100 ns'),
 ('Core architecture', 'Edge enforce &rarr; async detect &rarr; decision service (threshold + TTL) &rarr; '
                       'versioned delta publisher &rarr; regional relays &rarr; in-process set'),
 ('Data store', 'Small versioned store as source of truth; in-process hash set at each enforcement point'),
 ('Partition key', 'None needed &mdash; the list is small enough to replicate <b>whole</b>, everywhere. '
                   'Say that: recognising you do not need to partition is a real answer'),
 ('Cache', 'The in-process set <i>is</i> the cache. Freshness measured as list age, not hit rate'),
 ('Queue', 'Delta stream, versioned. Traffic scales with <b>changes</b>, not fleet size'),
 ('Consistency', 'Eventual, with an explicit staleness budget. Removals propagate faster than additions'),
 ('Failure handling', 'Keep last list and alert on <b>list age</b>; version gap triggers snapshot pull; '
                      'TTLs self-heal; kill switch + allowlist'),
 ('Key deep dives', 'Push vs pull &middot; version numbers &middot; removal asymmetry &middot; '
                    'enforcement location'),
 ('Biggest trade-off', 'Propagation latency vs fanout cost. <b>Resolved by moving enforcement to the '
                       'edge so the huge fleet is allowed to be staler.</b>'),
], [
 """The card. Requirements, and note that detection being given is the framing. Scale: a million """
 """servers, a twenty megabyte list, twenty kilobytes a minute of change, a hundred nanosecond """
 """lookup.""",
 """Architecture in one line. And look at the partition key row — there is no partition key, because """
 """the list is small enough to replicate whole everywhere. Recognising that you do not need to """
 """partition something is a real answer and it is worth saying confidently rather than inventing a """
 """sharding scheme to look thorough.""",
 """Consistency is eventual with an explicit staleness budget and asymmetric urgency. Failure handling """
 """alerts on list age. And the biggest trade-off, which is also the best move in the question: """
 """propagation latency versus fanout cost, resolved by moving enforcement to the edge so that the """
 """enormous fleet is allowed to be staler.""",
])

say('The 60-second answer', [
 'Detection is given to me, so this is a distribution problem rather than a security one &mdash; the '
 'question is how a decision reaches a million servers before it stops mattering.',
 'First I would ask what staleness is acceptable, because that one number decides between simple '
 'polling and a push tree.',
 'I would enforce primarily at the edge rather than only at web servers: it is a thousand nodes instead '
 'of a million, and the traffic dies before it costs us a connection. The server-side list then becomes '
 'defence in depth, and is allowed to be staler.',
 'Detection runs asynchronously off the request path, feeding a decision service that applies a '
 'threshold and a TTL &mdash; one bad packet from a university gateway should not block the campus.',
 'Distribution is a versioned delta stream through regional relays: push for latency, pull for '
 'correctness. A server that misses messages sees a version gap and pulls a snapshot, so a machine '
 'offline for an hour self-heals on reconnect.',
 'Every entry has a TTL, removals propagate ahead of additions, and there is an allowlist plus a kill '
 'switch &mdash; because the most likely incident here is not an attack, it is us blocking a carrier '
 'NAT and taking out thousands of real users.',
], [
 """The sixty-second answer. It opens by reclassifying the problem, which is the highest-leverage """
 """sentence you can say on this question.""",
 """Then the clarifying question, the enforcement push-back with its consequence, the off-path """
 """detection, the distribution mechanism in one phrase, and the removal story ending on the incident """
 """that is actually going to happen. Say it out loud once — the last sentence in particular is the one """
 """that sounds like someone who has been on call.""",
], kicker='60-second interview answer')
