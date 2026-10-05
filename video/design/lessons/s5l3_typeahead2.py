# -*- coding: utf-8 -*-
"""Chapter 5, Lesson 3 — typeahead part two: personalisation and freshness."""
from lib import *

lesson_header('5.3', 'Typeahead, part two: personalisation and freshness',
              'Mixed entity types &middot; per-member signals &middot; a seconds-fresh index',
              dict(reports='3 independent reports (see 2.2), plus the InterviewTV follow-ups',
                   latest='March 2026', level='Senior / Staff',
                   conf='HIGH &mdash; strongest in the set',
                   sources='Exponent &times;2, Glassdoor, InterviewTV.io'), 16,
              """Chapter five, lesson three. We built typeahead in lesson two point two &mdash; the trie, """
              """the fifty millisecond budget, top-K per prefix. This lesson is the follow-ups, and they """
              """are where the question actually gets hard: one billion users, new members findable """
              """immediately, personalised ranking, and mixing companies and people in one list. Each """
              """of those breaks something we built. Watch two point two first; this assumes it.""")

evidence('Where this question comes from', [
 ('Exponent &mdash; candidate report', '&asymp; Mar 2026', 'Senior SWE',
  'Discussion centred on <b>scalability, data structures and ranking of suggestions</b>'),
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  'Follow-ups named: <b>1B users, newly created members appear quickly, personalisation, dynamically '
  'mix company and member results, reduce latency, generate ranking, return top K</b>'),
 ('Glassdoor &mdash; interview reports', '&asymp; 2025', 'Senior SWE',
  'Reported as &ldquo;typeahead for person search&rdquo;'),
], """This is the best-evidenced question in the entire course: three independent reports in the earlier """
     """research, and now a fourth source listing the follow-ups explicitly.""",
 ["""And look at what those follow-ups name &mdash; a billion users, new members findable quickly, """
  """personalisation, mixing companies and members dynamically, latency, ranking, top K. That is not a """
  """list of topics, it is a list of things that each break the simple design. We will take them one """
  """at a time."""],
 caveat='Four sources. Still not a promise &mdash; but if you prepare one design question for LinkedIn, '
        'prepare this one.',
 narration_caveat="""Four sources. Still not a promise. But if you only prepare one design question for """
                  """a LinkedIn loop, I would make it this one.""")

sid = beat('Why part two is harder', 'Personalisation destroys the cache. That is the whole lesson.',
           '<div style="font-size:28px;line-height:1.72">'
           'In lesson 2.2 the design worked because the answer to a prefix was <b>the same for '
           'everyone</b>. Precompute top-10 per prefix, cache it, serve it in microseconds.<br><br>'
           '<span style="color:#ff9a9a">Personalisation breaks that completely.</span> If my results '
           'differ from yours, there is no shared answer to cache. One billion users &times; millions '
           'of prefixes is not a precomputable space.<br><br>'
           '<b>So the design has to split in two:</b><br>'
           '&bull; A <b>global</b> layer that is still precomputable and still cached<br>'
           '&bull; A <b>personal</b> layer that is small, local to the member, and cheap to merge<br><br>'
           'And the other three follow-ups each attack a different assumption:<br>'
           '&bull; <b>1B users</b> &rarr; the index no longer fits where we put it<br>'
           '&bull; <b>New members findable immediately</b> &rarr; the nightly build is dead<br>'
           '&bull; <b>Mix companies and members</b> &rarr; you must compare <i>incomparable</i> scores'
           '<br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: when a requirement kills your cache, do '
           'not abandon caching &mdash; find the part that is still shared.</span></div>',
           """Why is part two harder? Because in lesson two point two the design worked for one reason: """
           """the answer to a prefix was the same for everybody. Precompute the top ten per prefix, """
           """cache it, serve it in microseconds.""", step=0)
seg(sid, 1, """Personalisation destroys that. If my results differ from yours, there is no shared answer """
            """to cache. A billion users times millions of prefixes is not a space you can precompute, """
            """and no amount of hardware changes that.""")
seg(sid, 2, """So the design has to split in two. A global layer that is still precomputable and still """
            """cached, and a personal layer that is small, local to the member, and cheap to merge at """
            """query time. Keep the shared part shared.""")
seg(sid, 3, """And the other three follow-ups each attack a different assumption. A billion users means """
            """the index no longer fits where we put it. New members findable immediately kills the """
            """nightly build. And mixing companies with members means comparing scores that are not """
            """comparable &mdash; which sounds like a ranking detail and is actually the hardest of the """
            """four.""")
seg(sid, 4, """The staff-level insight that ties it together: when a requirement kills your cache, do not """
            """abandon caching. Find the part that is still shared. That instinct generalises to feeds, """
            """recommendations, and almost anything personalised.""")

think('Personalised results mean every member sees something different for the prefix "sa". You cannot '
      'precompute a billion different answers. What part of the answer is still the same for everyone '
      '&mdash; and how small is the part that is not?',
      25,
      """Pause. Personalised results mean every member sees something different for the prefix """
      """&ldquo;s-a&rdquo;. You cannot precompute a billion different answers. So &mdash; what part of """
      """the answer is still the same for everyone? And how small is the part that is not? Say it out """
      """loud.""",
      """Hold that. The answer is that your own network is tiny compared with the global index, and """
      """that asymmetry is what makes the whole thing tractable.""")

clarify('What I would clarify first', [
 ('Personalised how &mdash; my connections, or a learned model?',
  'First-degree connections is a <b>small set I can hold</b>. A learned model means feature lookups '
  'and inference inside 50 ms, which is a much bigger ask.'),
 ('&ldquo;New members appear quickly&rdquo; &mdash; how quickly?',
  'Minutes allows a near-real-time index path. <b>Seconds</b> means the write path must touch the '
  'serving index directly, which is a different system.'),
 ('When you say mix companies and members, is the ratio fixed or dynamic?',
  'Fixed (&ldquo;7 people, 3 companies&rdquo;) is trivial. <b>Dynamic means comparing scores across '
  'entity types</b>, which is the genuinely hard part.'),
 ('Is the 50 ms budget per request, or end-to-end per keystroke?',
  'Changes everything, same as in 2.2. Always re-confirm the budget before adding work to the path.'),
 ('Do we need to handle members who are <i>not</i> findable &mdash; privacy settings?',
  'Visibility filtering at query time means the top-K you precomputed may be <b>mostly '
  'invisible</b> to this searcher. Over-fetch to compensate.'),
 ('Is stale-but-fast acceptable, or must a brand-new member appear in <i>this</i> keystroke?',
  'The honest answer is usually &ldquo;within a minute is fine&rdquo;, and getting that concession '
  'saves an entire subsystem.'),
], [
 """Personalised how &mdash; by my connections, or by a learned model? First-degree connections is a """
 """small set I can hold in memory. A learned model means feature lookups and inference inside fifty """
 """milliseconds, which is a far bigger ask and may not fit the budget at all.""",
 """New members appear quickly &mdash; how quickly? Minutes allows a near-real-time indexing path. """
 """Seconds means the write path has to touch the serving index directly, which is a genuinely """
 """different system. Ask for the number.""",
 """When you say mix companies and members, is the ratio fixed or dynamic? Seven people and three """
 """companies is trivial. Dynamic means comparing a person score against a company score, and those """
 """are not on the same scale. That is the hard one.""",
 """Is the fifty milliseconds per request or end-to-end per keystroke? Same question as part one, and """
 """worth re-confirming before you add any work to the path.""",
 """Do we handle members who are not findable because of privacy settings? Visibility filtering at """
 """query time means the top ten you precomputed might be mostly invisible to this particular searcher, """
 """so you have to over-fetch to compensate.""",
 """And the one that can save you a whole subsystem: is stale-but-fast acceptable, or must a brand new """
 """member appear within this keystroke? The honest answer is usually &ldquo;within a minute is """
 """fine&rdquo;, and getting that concession explicitly is worth a lot.""",
])

capacity('Capacity &mdash; what changes at 1B users', [
 ('1B members &times; ~50 B of name data', '1B &times; 50 B', '&asymp; 50 GB raw',
  'Too big for RAM on a serving node. <b>This is the follow-up that breaks 2.2</b>'),
 ('Top-10 per prefix only, compressed FST', 'keep 10 results / prefix, not all matches',
  '&asymp; 5&ndash;8 GB', '<b>Fits.</b> The compression is what makes replication possible'),
 ('Personal layer: ~500 connections / member', '500 &times; ~60 B', '&asymp; 30 KB / member',
  '<b>Tiny.</b> Can be cached per session, or even pushed to the client'),
 ('1B members &times; 30 KB if stored centrally', '1B &times; 30 KB', '&asymp; 30 TB',
  'Too big to keep hot for everyone &mdash; but only <b>active</b> members matter: ~100M &rarr; 3 TB, '
  'sharded'),
 ('New members / s', '~2 per second globally', 'trivial write volume',
  '<b>Freshness is not a throughput problem.</b> It is a <i>latency-of-propagation</i> problem'),
 ('Query volume (from 2.2)', '~70,000 req/s peak', 'unchanged',
  'Each request now does: global lookup + personal merge + visibility filter, in 50 ms'),
], [
 """What changes at a billion users. A billion members at fifty bytes of name data is fifty gigabytes """
 """raw &mdash; too big for RAM on a serving node, and this is exactly the follow-up that breaks the """
 """design from lesson two point two, where we replicated the index everywhere.""",
 """Keeping only the top ten per prefix, in a compressed finite-state transducer, gets to five or """
 """eight gigabytes. That fits, and the compression is what makes full replication possible again. """
 """Worth noticing that you solved a scale problem by storing less, not by adding machines.""",
 """The personal layer: about five hundred connections per member at sixty bytes is thirty kilobytes. """
 """That is tiny. It can be cached per session, or in some designs pushed to the client """
 """altogether.""",
 """If you stored that centrally for all billion members it is thirty terabytes, which is too much to """
 """keep hot. But only active members matter &mdash; call it a hundred million, so three terabytes, """
 """sharded by member. That is ordinary.""",
 """New members arrive at roughly two per second globally. So freshness is not a throughput problem at """
 """all &mdash; it is a latency-of-propagation problem. That distinction matters, because it means the """
 """answer is a fast path, not a bigger pipeline.""",
 """And query volume is unchanged from part one, about seventy thousand a second at peak. Except now """
 """each request does a global lookup, a personal merge and a visibility filter, all inside fifty """
 """milliseconds.""",
])

A = Arch('Typeahead with personalisation and a fresh path', kicker='Architecture', height=800)

A.box('cl',   60, 330, 150, 90, 'Keystroke', '', kind='neutral', step=0, focus=0, small=True)
A.box('svc', 250, 320, 200, 110, 'Typeahead svc', '50 ms budget', kind='ok', step=0, focus=[0, 1, 2, 3])
A.arrow('cl', 'svc', step=0, focus=0)

A.box('glob', 530, 170, 230, 110, 'Global index', 'FST, 5-8 GB<br>replicated', kind='ok', step=1, focus=1)
A.arrow('svc', 'glob', step=1, label='prefix', focus=1)

A.box('pers', 530, 330, 230, 110, 'Personal layer', 'my network<br>~30 KB', kind='info', step=2, focus=2)
A.arrow('svc', 'pers', step=2, focus=2)

A.box('mrg',  830, 250, 215, 110, 'Blend + rank', 'one score', kind='shared', step=3, focus=[3, 4])
A.arrow('glob', 'mrg', step=3, focus=3)
A.arrow('pers', 'mrg', step=3, focus=3)

A.box('vis',  830, 420, 215, 95, 'Visibility filter', 'privacy', kind='neutral', step=4, focus=4, small=True)
A.arrow('mrg', 'vis', step=4, focus=4, dashed=True)

A.box('out', 1120, 250, 190, 95, 'Top 10', '', kind='ok', step=4, focus=4, small=True)
A.arrow('mrg', 'out', step=4, focus=4)

A.zone(500, 560, 820, 200, 'INDEXING — two paths, two latencies')
A.box('batch', 540, 615, 215, 105, 'Nightly build', 'full FST', kind='dp', step=5, focus=5, small=True)
A.box('fresh', 820, 615, 215, 105, 'Fresh delta', 'last N hours', kind='info', step=6, focus=6, small=True)
A.arrow('batch', 'glob', step=5, focus=5, dashed=True)
A.arrow('fresh', 'glob', step=6, focus=6, dashed=True)

A.box('evt', 1100, 615, 200, 105, 'Signup events', '~2 / s', kind='shared', step=6, focus=6, small=True)
A.arrow('evt', 'fresh', step=6, focus=6)

A.note(1370, 170, 'The global index is the same for everyone, so it stays cached. Only the small personal layer varies.',
       step=2, kind='info', w=440)

A.narrate(0, """A keystroke hits the typeahead service with a fifty millisecond budget. Same starting """
             """point as part one.""",
          A.flow([(210, 375), (250, 375)]))
A.narrate(1, """First lookup: the global index. A compressed F-S-T holding the top ten per prefix, five to """
             """eight gigabytes, replicated onto every serving node so there is no network hop. This is """
             """the part that is identical for every member, which is why it can still be cached.""",
          A.flow([(450, 360), (530, 225)]))
A.narrate(2, """Second lookup: the personal layer. My own network, about thirty kilobytes, which I can """
             """hold per session. Note how asymmetric those two numbers are &mdash; gigabytes shared """
             """versus kilobytes personal. That asymmetry is the entire reason this is tractable.""",
          A.flow([(450, 390), (530, 385)]))
A.narrate(3, """Then blend and rank into a single ordering. This is the deep dive, because blending """
             """results from two sources with different score scales is where this gets genuinely """
             """hard.""",
          A.flow([(760, 225), (830, 305)]))
A.narrate(4, """A visibility filter applies privacy settings, and the top ten goes back. Worth noting """
             """that filtering after ranking means you must over-fetch &mdash; ask for thirty """
             """candidates to return ten, or a searcher with lots of hidden connections gets a short """
             """list.""")
A.narrate(5, """Underneath: indexing, and this is where freshness gets solved. A nightly batch builds the """
             """full F-S-T. Cheap, simple, and hours stale.""")
A.narrate(6, """And a fresh delta index holding only the last few hours of new members, fed directly from """
             """signup events. At two signups a second it stays small enough to rebuild every minute. """
             """The service queries both and merges. Two paths with two latencies, rather than one path """
             """trying to be both fast and complete.""",
          A.flow([(1100, 667), (1035, 667), (820, 667)]))
A.build()

sid = beat('Deep dive 1', 'Blending two sources with <b>incomparable</b> scores',
           '<div style="font-size:27px;line-height:1.7">'
           'The global index scores by <b>global popularity</b>. The personal layer scores by '
           '<b>relationship strength</b>. A company has <b>follower count</b>. '
           '<span style="color:#ff9a9a">These are not on the same scale, and comparing them directly is '
           'meaningless.</span><br><br>'
           '<b>The fix: do not compare raw scores. Compute features, then one model.</b><br>'
           'For every candidate, regardless of type:<br>'
           '&bull; prefix match quality (exact / prefix / fuzzy)<br>'
           '&bull; global prominence, <b>normalised within its own type</b> (percentile, not raw count)<br>'
           '&bull; relationship distance (1st, 2nd, none)<br>'
           '&bull; recent interaction with this searcher<br>'
           '&bull; entity type itself, as a feature &mdash; let the model learn the mix<br><br>'
           '<b>Why normalise within type:</b> Microsoft has 20M followers; a person has 500 '
           'connections. Raw numbers put every company above every person, forever.<br><br>'
           '<span style="color:#ffd483">&ldquo;Dynamically mix company and member results&rdquo; is '
           'answered by making entity type a feature rather than a quota. The model learns that '
           '&ldquo;goog&rdquo; wants a company and &ldquo;sarah&rdquo; wants a person.</span></div>',
           """Deep dive one, and this is the hardest of the four follow-ups: blending sources whose """
           """scores are not comparable. The global index scores by global popularity. The personal """
           """layer scores by relationship strength. A company has a follower count. Those three numbers """
           """are not on the same scale, and comparing them directly is meaningless.""", step=0)
seg(sid, 1, """The fix is to stop comparing raw scores and instead compute features for every candidate, """
            """whatever its type, and feed them to one model that produces a single score.""")
seg(sid, 2, """The features: how good the prefix match is &mdash; exact, prefix, or fuzzy. Global """
            """prominence, normalised within its own type. Relationship distance, first degree, second """
            """degree or none. Recent interaction with this particular searcher. And critically, the """
            """entity type itself as a feature.""")
seg(sid, 3, """Normalising within type is the detail that matters. Microsoft has twenty million """
            """followers. A person has five hundred connections. If you use raw numbers, every company """
            """outranks every person forever, and your people search stops working. Use percentile """
            """within type and the comparison becomes meaningful.""")
seg(sid, 4, """And this is how you answer &ldquo;dynamically mix company and member results&rdquo;. Not """
            """with a quota &mdash; not &ldquo;always seven people and three companies&rdquo; &mdash; """
            """but by making entity type a feature and letting the model learn that someone typing """
            """&ldquo;g-o-o-g&rdquo; wants a company, and someone typing &ldquo;s-a-r-a-h&rdquo; wants a """
            """person. The word &ldquo;dynamically&rdquo; in the question is pointing at exactly this.""")

sid = beat('Deep dive 2', 'Freshness &mdash; a second index, not a faster one',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>The problem:</b> the global FST is built offline and is immutable. That immutability is '
           'why it is fast and compressible. <span style="color:#ff9a9a">You cannot insert into '
           'it.</span><br><br>'
           '<b>The wrong fix:</b> rebuild it more often. A full build over 1B members takes hours; '
           'running it every minute is not a plan.<br><br>'
           '<b>The right fix &mdash; two indexes at two latencies:</b><br>'
           '&bull; <b>Base</b>: full FST, rebuilt nightly. Hours stale, 5&ndash;8 GB.<br>'
           '&bull; <b>Fresh</b>: only members created since the last build. At ~2 signups/s that is '
           '~170k/day &mdash; <span style="color:#a8e6a3">a few MB. Rebuild it every minute.</span><br>'
           '&bull; Query <b>both</b>, merge the results. The fresh index is small enough that searching '
           'it costs almost nothing.<br>'
           '&bull; At the nightly build, the fresh index resets to empty.<br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: this is the same shape as an LSM tree '
           '&mdash; a big immutable structure plus a small mutable one, merged on read, compacted '
           'periodically. Name that connection; it shows the pattern rather than the trick.</span>'
           '</div>',
           """Deep dive two: freshness. The problem is that the global F-S-T is built offline and is """
           """immutable &mdash; and that immutability is exactly why it is fast and compressible. You """
           """cannot insert into it.""", step=0)
seg(sid, 1, """The wrong fix is to rebuild it more often. A full build over a billion members takes """
            """hours. Running it every minute is not a plan, it is a wish.""")
seg(sid, 2, """The right fix is two indexes at two latencies. A base index: the full F-S-T, rebuilt """
            """nightly, hours stale, five to eight gigabytes. And a fresh index containing only members """
            """created since the last build.""")
seg(sid, 3, """And here is why that works &mdash; it is the capacity number from earlier. At two signups """
            """a second, a day's worth of new members is about a hundred and seventy thousand people, """
            """which is a few megabytes. You can rebuild that every minute without thinking about it. """
            """The freshness problem was never a scale problem.""")
seg(sid, 4, """Query both, merge the results, and reset the fresh index to empty at each nightly build.""")
seg(sid, 5, """And the insight worth naming out loud: this is the same shape as an L-S-M tree. A big """
            """immutable structure plus a small mutable one, merged on read, compacted periodically. """
            """It is also how Lucene handles near-real-time indexing. Naming that connection shows you """
            """are recognising a pattern rather than inventing a trick, and it is the kind of thing that """
            """makes an interviewer think you will solve the next problem too.""")

tradeoff('Where personalisation is applied', [
 ('Personalise inside the index', 'info',
  ['One lookup, one ranked list', 'No merge logic at query time'],
  ['<b>Requires a per-member index</b> &mdash; 1B indexes', 'Impossible to cache anything',
   'Rebuild cost explodes']),
 ('Re-rank globally-retrieved candidates', 'ok',
  ['Global index stays shared and cached', 'Personal layer is ~30 KB',
   'Model can use any feature available at query time'],
  ['Needs over-fetch &mdash; retrieve 50 to return 10',
   'A connection outside the global top-50 for a prefix is <b>never seen</b>',
   'Ranking cost is now on the hot path']),
 ('Retrieve from both, then blend', 'shared',
  ['A close connection is found even if globally obscure', 'Two cheap lookups instead of one expensive one'],
  ['Two retrieval paths to maintain', 'Must normalise scores across sources',
   'Slightly more latency than a single lookup']),
], 'Retrieve from both and blend. Retrieving only globally would make my own colleague unfindable if '
   'their name is not globally prominent &mdash; which is the single most embarrassing failure this '
   'product can have.',
 'If the personal network were huge &mdash; tens of thousands of connections &mdash; holding it per '
 'session stops being cheap, and I would move to global retrieval with a re-rank and accept the '
 'recall loss.',
 [
 """Trade-off: where is personalisation applied? Inside the index means one lookup and one ranked list, """
 """and it requires a per-member index &mdash; a billion of them. Nothing is cacheable and the rebuild """
 """cost explodes. Not viable, but worth naming so the interviewer knows you considered and rejected """
 """it.""",
 """Re-ranking globally-retrieved candidates keeps the global index shared and cached, and the personal """
 """layer stays tiny. The cost is that you must over-fetch &mdash; retrieve fifty to return ten &mdash; """
 """and there is a real recall problem hiding in it: a connection who is not in the global top fifty """
 """for that prefix is never retrieved, so they can never be ranked up.""",
 """Retrieving from both and blending fixes exactly that. Your close connection is found even if they """
 """are globally obscure, because you searched the personal layer separately rather than hoping they """
 """surfaced globally.""",
 """That is what I would choose, and here is the reason in one sentence: retrieving only globally means """
 """my own colleague is unfindable if their name is not globally prominent. For a professional network, """
 """that is the single most embarrassing failure this product can have.""",
 """What would flip it: if the personal network were tens of thousands of connections, holding it per """
 """session stops being cheap, and I would go back to global retrieval with a re-rank and accept the """
 """recall loss.""",
])

failures('What happens when each piece dies', [
 ('Personal layer unavailable', 'Results still appear, but generic',
  '<b>Fail soft to global-only.</b> A slightly worse ordering beats a spinner &mdash; and this is why '
  'the two layers are separate rather than one structure'),
 ('Fresh index unavailable', 'Members who joined today are not findable',
  'Serve from base only and alarm. <b>Invisible to the user and visible in the metrics</b>, which is '
  'exactly the right shape for a degradation'),
 ('Nightly build fails', 'Index silently ages; fresh index grows unbounded',
  'Alert on <b>index age</b>, not on job success. And cap the fresh index &mdash; if the base has not '
  'rebuilt for 3 days, the &ldquo;small&rdquo; delta is no longer small'),
 ('Ranking model is slow or unavailable', 'Latency spike &rarr; budget blown',
  '<b>Hard timeout on the model</b> and fall back to a static score. Never let an optional quality '
  'improvement take out a required latency guarantee'),
 ('Visibility filter removes most candidates', 'A short or empty list',
  'Over-fetch (50 &rarr; 10) and re-fetch if the filtered set is too small. <b>Filtering after '
  'ranking always needs headroom</b>'),
 ('One prefix is enormously hot (a viral name)', 'That shard is saturated',
  'The global index is <b>replicated, not sharded by prefix</b>, so there is no single owner to '
  'overload. A design choice made in 2.2 paying off here'),
], [
 """Failures. Personal layer unavailable: results still appear but generic. Fail soft to global only """
 """&mdash; a slightly worse ordering beats a spinner. And notice this is a direct benefit of keeping """
 """the two layers separate rather than fusing them into one structure.""",
 """Fresh index unavailable: members who joined today are not findable. Serve from base only and alarm. """
 """That is invisible to the user and visible in the metrics, which is exactly the right shape for a """
 """degradation.""",
 """Nightly build fails and the index silently ages, while the fresh index grows unbounded. So alert on """
 """index age rather than on job success &mdash; the job can succeed and still be stale. And cap the """
 """fresh index: if the base has not rebuilt for three days, the small delta is no longer small and """
 """your query latency quietly doubles.""",
 """Ranking model slow or unavailable: hard timeout on it and fall back to a static score. Never let an """
 """optional quality improvement take out a required latency guarantee. That sentence applies to about """
 """half the systems in this course.""",
 """Visibility filter removes most candidates and the list comes back short. Over-fetch and re-fetch if """
 """needed. Filtering after ranking always needs headroom, and the amount of headroom is an empirical """
 """question rather than a guess.""",
 """And one prefix going enormously hot &mdash; a name in the news. Because the global index is """
 """replicated rather than sharded by prefix, there is no single owner to overload. That was a design """
 """choice made back in lesson two point two, and it pays off here. Worth pointing out when an earlier """
 """decision protects you from a later problem.""",
])

say('What I should actually say in the room', [
 'Part one worked because the answer to a prefix was the same for everyone, so we could precompute and '
 'cache it. Personalisation breaks exactly that, so the first thing I want to do is find the part that '
 'is still shared.',
 'That split is: a global index of about 5&ndash;8 GB replicated everywhere, and a personal layer of '
 'about 30 KB per member. Gigabytes shared, kilobytes personal &mdash; that asymmetry is what makes it '
 'work.',
 'I retrieve from both rather than retrieving globally and re-ranking, because otherwise my own '
 'colleague is unfindable if their name is not globally prominent.',
 'For mixing companies and members I would not use a fixed quota. I make entity type a feature and let '
 'one model score everything &mdash; and I normalise prominence <i>within</i> type, or every company '
 'outranks every person forever.',
 'For freshness I would not rebuild the big index faster. I would add a second, tiny index holding only '
 'today&rsquo;s new members and query both. At two signups a second that delta is a few megabytes and '
 'rebuilds in a minute.',
 'That is the same shape as an LSM tree &mdash; big immutable structure, small mutable one, merged on '
 'read.',
 'And I would put a hard timeout on the ranking model with a static-score fallback, so a quality '
 'feature can never break the latency guarantee.',
], [
 """The sentences. Open by naming what part one depended on and what personalisation breaks &mdash; """
 """that framing immediately shows you are extending a design rather than starting over.""",
 """Then the two numbers that make it tractable, then the retrieval decision with its one-line """
 """justification. Then the mixing answer, which is the subtlest of the four follow-ups.""",
 """Then freshness as a second index rather than a faster one, with the L-S-M connection named. And """
 """finish on the model timeout, because it shows you protect the guarantee rather than the feature.""",
])

followups([
 'How does this work for 1 billion users?',
 'Newly created members should appear quickly &mdash; how?',
 'How would you personalise the results?',
 'How do you dynamically mix company and member results?',
 'How do you reduce latency further?',
 'How do you generate the ranking?',
 'How do you return the top K quickly?',
], [
 'How would you A/B test a ranking change here without hurting the 50 ms budget?',
 'Someone searches for a name that has just gone viral. What happens?',
 'How do you handle typos &mdash; and what does fuzzy matching cost you?',
 'A member asks why someone appeared in their suggestions. Can you answer?',
 'What would you cut first if you had to halve the cost of this system?',
],
 """The reported follow-ups are the seven this lesson was built around, and we have answered all of """
 """them. On reducing latency further, the remaining levers are debouncing on the client so you do not """
 """fire on every keystroke, returning results on a connection you already have open, and truncating """
 """the ranking model &mdash; all three are worth naming because they are outside the server.""",
 """The staff-level follow-ups go sideways. A-B testing a ranking change inside a fifty millisecond """
 """budget is genuinely awkward and the answer is to score both models offline against logged traffic """
 """rather than online. A viral name is the hot-prefix case, already handled by replication. Typos mean """
 """fuzzy matching, which costs you the clean prefix walk and is why it is usually a separate, slower """
 """path. Explaining why someone appeared is a model interpretability question and it is increasingly """
 """a regulatory one. And halving the cost &mdash; the honest answer is usually the personalisation """
 """layer, which is the expensive half and often the smaller quality win.""")

cheatsheet('Typeahead part 2 &mdash; the one-page card', [
 ('Requirements', '1B users, personalised, new members findable fast, mixed entity types, 50 ms'),
 ('Scale', 'Global index 5&ndash;8 GB compressed; personal layer ~30 KB/member; ~2 signups/s; 70k req/s peak'),
 ('Core architecture', 'Retrieve global (FST) + personal in parallel &rarr; blend with one model &rarr; '
                       'visibility filter &rarr; top 10'),
 ('Data store', 'Immutable FST replicated per node; personal layer cached per session; small fresh '
                'delta index'),
 ('Partition key', '<b>Replicate, do not partition</b> the global index &mdash; it fits once '
                   'compressed, and that removes hot-prefix risk entirely'),
 ('Cache', 'The global index is the cache. Personal layer cached per session. Result cache is useless '
           'once personalised'),
 ('Queue', 'Signup events feed the fresh index; nightly batch rebuilds the base'),
 ('Consistency', 'Eventual, bounded by the fresh-index rebuild interval (~1 min)'),
 ('Failure handling', 'Fail soft to global-only; alert on index <b>age</b>; hard timeout on the model'),
 ('Key deep dives', 'Blending incomparable scores &middot; the two-index freshness pattern'),
 ('Biggest trade-off', 'Personalisation vs cacheability. Resolved by splitting shared from personal '
                       'rather than giving up either'),
], [
 """The card. Requirements are the four follow-ups. Scale carries the asymmetry that makes it work: """
 """gigabytes global, kilobytes personal.""",
 """Architecture is parallel retrieval, one blending model, visibility filter, top ten. The partition """
 """row is worth reading twice &mdash; replicate rather than partition, because it fits once compressed """
 """and that removes hot-prefix risk entirely.""",
 """Note that a result cache is useless once results are personalised, which is why the global index """
 """has to be the cache. Consistency is bounded by the fresh rebuild interval. And the biggest """
 """trade-off: personalisation versus cacheability, resolved by splitting shared from personal rather """
 """than giving up either one.""",
])

say('The 60-second answer', [
 'The simple design works because a prefix has the same answer for everyone, so it can be precomputed '
 'and cached. Personalisation breaks precisely that, so my first move is to find the part that is still '
 'shared.',
 'That gives two layers: a global index of the top candidates per prefix, 5 to 8 GB once compressed, '
 'replicated onto every serving node &mdash; and a personal layer, my own network, about 30 KB. '
 'Gigabytes shared against kilobytes personal is what makes this tractable.',
 'I retrieve from both in parallel rather than retrieving globally and re-ranking, because otherwise a '
 'colleague who is not globally prominent is simply never found.',
 'To mix companies and members I avoid a fixed quota. Entity type becomes a feature and one model '
 'scores everything, with prominence normalised within type &mdash; otherwise every company outranks '
 'every person forever.',
 'For freshness I do not rebuild the big index faster. I add a tiny second index holding only members '
 'created since the last build. At two signups a second that is a few megabytes and rebuilds every '
 'minute, and I query both. Same shape as an LSM tree.',
 'And the ranking model gets a hard timeout with a static fallback, because an optional quality '
 'improvement must never break a required latency guarantee.',
], [
 """The sixty-second answer. It opens by naming what broke, which frames everything that follows as a """
 """response rather than a list of components.""",
 """Practise the second sentence until the two numbers come out cleanly &mdash; gigabytes shared, """
 """kilobytes personal. That contrast is the single most persuasive thing in the whole answer, because """
 """it makes an apparently impossible requirement sound obviously manageable.""",
], kicker='60-second interview answer')
