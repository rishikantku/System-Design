# -*- coding: utf-8 -*-
"""Chapter 9, Lesson 3 — live map of new member sign-ups."""
from lib import *

lesson_header('9.3', 'Design a live map of new member sign-ups',
              'Geo aggregation &middot; tiles &middot; k-anonymity &middot; real-time vs batch',
              dict(reports='InterviewTV list only', latest='2026', level='Staff',
                   conf='MEDIUM &mdash; single source', sources='InterviewTV.io'), 15,
              """Chapter nine, lesson three: a data visualisation map showing where newly registered """
              """LinkedIn members are. This is the shortest lesson in the course, and it contains one """
              """genuinely important idea that the other twenty questions do not: you are about to """
              """plot real people's locations on a public map, and if you do the obvious thing you """
              """will build a privacy incident with a nice colour scheme.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  'Named: event ingestion, <b>geo aggregation, geospatial indexing, privacy</b>, aggregation, '
  'real-time vs batch, map tiles, querying geographic regions'),
], """Single source, medium confidence. And note that privacy is named explicitly in the deep dive list, """
     """which is unusual &mdash; most questions leave it to you to raise.""",
 ["""That it is named tells you the interviewer expects it to be a design constraint rather than a """
  """closing remark. So I would raise it in the first two minutes, not the last two."""],
 caveat='Single source. The geo-aggregation and tiling machinery is standard and transfers to any '
        'map or location question.',
 narration_caveat="""Single source. The geo-aggregation and tiling machinery is standard, so it """
                  """transfers to any map or location question you get.""")

sid = beat('Why this is interesting', 'The naive version is a privacy incident',
           '<div style="font-size:28px;line-height:1.72">'
           'The obvious design: on sign-up, record the location; the map queries points in the current '
           'viewport and draws dots.<br><br>'
           '<span style="color:#ff9a9a">Zoom in far enough and a dot is a person &mdash; a new LinkedIn '
           'member, at a location, at a time. In a small town, that identifies someone.</span> On a '
           'public map. From a company that knows their employer.<br><br>'
           '<b>So the design constraint is not a feature, it is a floor:</b><br>'
           '&bull; Never store or serve an individual point for display<br>'
           '&bull; <b>Aggregate before storage</b>, not before display &mdash; if the raw points exist, '
           'they can leak<br>'
           '&bull; Enforce <b>k-anonymity</b>: suppress any cell with fewer than k members<br>'
           '&bull; Cap the zoom level so cells never get small enough to identify<br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: &ldquo;we will anonymise it later&rdquo; '
           'is not a privacy design. Aggregation has to happen on the ingest path, so the identifying '
           'data never lands anywhere it can be queried.</span></div>',
           """Why is this interesting? Because the naive version is a privacy incident with a nice """
           """colour scheme.""", step=0)
seg(sid, 1, """The obvious design is: on sign-up, record the location; the map queries points in the """
            """current viewport and draws dots. Perfectly reasonable-looking, and completely """
            """wrong.""")
seg(sid, 2, """Zoom in far enough and a dot is a person &mdash; a new LinkedIn member, at a location, at """
            """a time. In a small town that identifies somebody. On a public map. From a company that """
            """also knows their employer and their job title.""")
seg(sid, 3, """So the privacy requirement is not a feature to add, it is a floor the design sits on. """
            """Never store or serve an individual point for display. Aggregate before storage rather """
            """than before display &mdash; because if the raw points exist somewhere queryable, they """
            """can leak, whatever your A-P-I does. Enforce k-anonymity by suppressing any cell with """
            """fewer than k members. And cap the zoom so cells never get small enough to identify """
            """anyone.""")
seg(sid, 4, """The staff-level insight is that &ldquo;we will anonymise it later&rdquo; is not a privacy """
            """design. Aggregation has to happen on the ingest path, so the identifying data never """
            """lands anywhere it can be queried in the first place. Where you put the aggregation step """
            """is the entire difference between a safe system and a dangerous one.""")

think('Your map shows a heat map of new sign-ups. Someone zooms all the way in on a village with one '
      'new member this week. What does your system show them &mdash; and at what point in the pipeline '
      'did you make that impossible?',
      25,
      """Pause. Your map shows a heat map of new sign-ups. Someone zooms all the way in on a village """
      """with exactly one new member this week. What does your system show them? And at what point in """
      """the pipeline did you make the wrong answer impossible? Say it out loud.""",
      """Hold that. &ldquo;The A-P-I refuses&rdquo; is a much weaker answer than &ldquo;that data was """
      """never stored&rdquo;.""")

clarify('What I would clarify first', [
 ('Who sees this &mdash; the public, or internal analysts?',
  '<b>Completely different privacy bars.</b> A public marketing map needs heavy aggregation. An '
  'internal tool may legitimately need more detail, with access controls and audit instead.'),
 ('Real-time, or is a daily refresh enough?',
  '<b>The biggest cost lever.</b> &ldquo;Live&rdquo; is usually a product adjective, not a '
  'requirement. A 5-minute refresh looks live and is far cheaper than streaming.'),
 ('What location precision do we actually have &mdash; and want?',
  'IP geolocation is city-level at best and often wrong. <b>Profile location is self-declared.</b> '
  'Neither is precise, which is convenient.'),
 ('What is the k in k-anonymity?',
  'Make it an explicit, named number &mdash; 50, say &mdash; so it can be reviewed by someone other '
  'than me. <b>Privacy thresholds should not be implicit.</b>'),
 ('What is the map actually for &mdash; marketing, ops, or growth analysis?',
  'Marketing wants it to look impressive. Growth wants to compare regions over time. <b>Different '
  'queries, different aggregates.</b>'),
 ('Maximum zoom level?',
  'Bounds the smallest cell, which bounds the identifiability. <b>A product decision with a privacy '
  'consequence</b>, so it should be decided deliberately.'),
], [
 """Who sees this &mdash; the public, or internal analysts? Completely different privacy bars. A public """
 """marketing map needs heavy aggregation. An internal tool may legitimately need more detail, with """
 """access controls and audit logging instead of suppression.""",
 """Real-time, or is a daily refresh enough? This is the biggest cost lever, and &ldquo;live&rdquo; is """
 """usually a product adjective rather than a requirement. A five-minute refresh looks live to a human """
 """watching a map and is dramatically cheaper than streaming.""",
 """What location precision do we actually have, and want? I-P geolocation is city-level at best and is """
 """often simply wrong. Profile location is self-declared. Neither is precise &mdash; which is """
 """convenient here, because imprecision is doing privacy work for you.""",
 """What is the k in k-anonymity? Make it an explicit named number &mdash; fifty, say &mdash; so that """
 """it can be reviewed by someone other than the engineer who wrote it. Privacy thresholds should never """
 """be implicit constants buried in code.""",
 """What is the map actually for &mdash; marketing, operations, or growth analysis? Marketing wants it """
 """to look impressive. Growth wants to compare regions over time. Those are different queries and """
 """different aggregates.""",
 """And what is the maximum zoom level? That bounds the smallest cell, which bounds identifiability. It """
 """is a product decision with a privacy consequence, so it should be made deliberately rather than """
 """inherited from a mapping library's default.""",
])

capacity('Capacity', [
 ('New member sign-ups', '~2 / s globally, ~170k / day', '&asymp; 2 events / s',
  '<b>Tiny.</b> Ingestion is not the problem &mdash; say so immediately'),
 ('Map viewers', 'say 10k concurrent on a public page', '&asymp; 2,000 tile req / s',
  'Reads vastly outnumber writes. <b>This is a read problem</b>'),
 ('Raw points if stored', '170k/day &times; 365 &times; 50 B', '&asymp; 3 GB / year',
  'Trivially small &mdash; <b>which is exactly why the temptation to keep them is dangerous</b>'),
 ('Aggregated: H3 cells at resolution 5', '~2M cells globally, most empty',
  '&asymp; 50k populated cells', '<b>Smaller than the raw data</b>, and safe'),
 ('Pre-rendered tiles: zoom 0&ndash;8', '~87k tiles worldwide &times; ~20 KB', '&asymp; 1.7 GB',
  'Regenerate every 5 min. <b>Serve from a CDN; the map never queries a database</b>'),
 ('Query &ldquo;sign-ups in this viewport&rdquo;', 'over pre-aggregated cells', '&asymp; 1&ndash;5 ms',
  'Because the aggregation already happened. <b>The work was done at write time</b>'),
], [
 """Numbers, and they reframe the problem immediately. New member sign-ups are about two a second """
 """globally, roughly a hundred and seventy thousand a day. Tiny. Ingestion is not the problem here and """
 """I would say so in the first thirty seconds.""",
 """Map viewers &mdash; say ten thousand concurrent on a public page &mdash; generate maybe two """
 """thousand tile requests a second. So reads vastly outnumber writes. This is a read problem wearing """
 """an ingestion costume.""",
 """If you stored raw points it would be about three gigabytes a year. Trivially small &mdash; and that """
 """is exactly why the temptation to keep them is dangerous. The data is cheap to store, so nobody """
 """deletes it, and it sits there being a liability.""",
 """Aggregated into H3 hexagonal cells at resolution five, there are about two million cells globally """
 """and most are empty, so maybe fifty thousand populated ones. Smaller than the raw data and """
 """safe.""",
 """Pre-rendered tiles for zoom levels zero to eight is around eighty-seven thousand tiles worldwide at """
 """twenty kilobytes each, about one point seven gigabytes. Regenerate every five minutes and serve """
 """from a C-D-N &mdash; and then the map never queries a database at all.""",
 """And a viewport query over pre-aggregated cells is one to five milliseconds, because the aggregation """
 """already happened at write time. Which is the general shape: do the work on the rare operation.""",
])

A = Arch('Sign-up map &mdash; aggregate on ingest, serve tiles', kicker='Architecture', height=780)

A.box('su',   60, 180, 155, 90, 'Sign-up', '~2 / s', kind='neutral', step=0, focus=0, small=True)
A.box('ev',  250, 170, 185, 110, 'Event stream', 'member created', kind='ok', step=0, focus=0)
A.arrow('su', 'ev', step=0, focus=0)

A.box('geo',  500, 170, 200, 110, 'Geo resolver', 'to H3 cell', kind='ok', step=1, focus=1)
A.arrow('ev', 'geo', step=1, focus=1)

A.box('agg',  770, 160, 215, 125, 'Aggregator', 'count per cell<br>per time bucket', kind='info',
      step=2, focus=[2, 3])
A.arrow('geo', 'agg', step=2, focus=2)

A.box('supp', 770, 350, 215, 110, 'k-anonymity', 'drop cells &lt; k', kind='shared', step=3, focus=3)
A.arrow('agg', 'supp', step=3, focus=3)

A.box('cells',1060, 160, 210, 110, 'Cell counts', 'the only store', kind='dp', step=4, focus=4, small=True)
A.arrow('supp', 'cells', step=4, focus=4)

A.box('tile', 1060, 340, 210, 110, 'Tile renderer', 'every 5 min', kind='ok', step=5, focus=5, small=True)
A.arrow('cells', 'tile', step=5, focus=5)

A.box('cdn',  1060, 520, 210, 100, 'CDN', 'pre-rendered', kind='ok', step=6, focus=6, small=True)
A.box('map',   770, 520, 215, 100, 'Map client', 'fetches tiles', kind='neutral', step=6, focus=6, small=True)
A.arrow('tile', 'cdn', step=6, focus=6)
A.arrow('map', 'cdn', step=6, focus=6)

A.note(250, 380, 'Nothing downstream of the geo resolver ever sees an individual location. The cell ID is all that moves.',
       step=2, kind='info', w=440)

A.narrate(0, """A sign-up produces an event. About two a second, so this is not a throughput """
             """problem.""",
          A.flow([(215, 225), (250, 225)]))
A.narrate(1, """A geo resolver turns the location into an H3 cell identifier. And this is the critical """
             """boundary &mdash; after this point, the individual location does not exist in the """
             """pipeline. Only a cell I-D moves forward.""",
          A.flow([(435, 225), (500, 225)]))
A.narrate(2, """The aggregator counts members per cell per time bucket. Note what is being stored: a """
             """count, not a list. Even if someone dumped this table, there are no individuals in """
             """it.""",
          A.flow([(700, 225), (770, 222)]))
A.narrate(3, """Then k-anonymity suppression drops any cell with fewer than k members. That village with """
             """one new member produces a cell that is simply not stored, so no A-P-I can return it and """
             """no bug can leak it.""",
          A.flow([(877, 285), (877, 350)]))
A.narrate(4, """Cell counts are the only thing persisted. The raw location was never written anywhere """
             """durable &mdash; which is a much stronger guarantee than an access control rule.""",
          A.flow([(985, 222), (1060, 215)]))
A.narrate(5, """A tile renderer turns cell counts into map tiles every five minutes.""",
          A.flow([(1165, 270), (1165, 340)]))
A.narrate(6, """And tiles go to a C-D-N, which is what the map client actually fetches. So the serving """
             """path never touches a database, and ten thousand concurrent viewers cost you almost """
             """nothing.""",
          A.flow([(1165, 450), (1165, 520)]))
A.build()

sid = beat('Deep dive 1', 'Geospatial indexing &mdash; why hexagons beat lat/long',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>The naive approach:</b> store latitude and longitude, query with a bounding box. '
           '<span style="color:#ff9a9a">It works and it has three problems.</span> It needs a spatial '
           'index, aggregation happens at query time, and you are storing exact points &mdash; which we '
           'already ruled out.<br><br>'
           '<b>The better approach: discretise space on ingest.</b><br>'
           '&bull; <b>Geohash</b> &mdash; a string prefix encodes a rectangle; longer prefix = smaller '
           'cell. <span style="color:#a8e6a3">Prefix search is a range scan.</span> '
           '<span style="color:#ff9a9a">Cells distort badly toward the poles, and neighbours are not '
           'always prefix-adjacent.</span><br>'
           '&bull; <b>H3 (hexagons)</b> &mdash; equal-area cells, and every neighbour is equidistant. '
           '<span style="color:#a8e6a3">Much better for heat maps, because a hexagon&rsquo;s neighbours '
           'are all the same distance away &mdash; squares have diagonal neighbours that are '
           '1.4&times; further.</span><br>'
           '&bull; <b>S2</b> &mdash; squares on a sphere, excellent for coverings and ranges<br><br>'
           '<b>Why it matters here:</b> a fixed cell grid means the count is incremented at '
           '<i>write</i> time, so a viewport query is a <b>lookup of pre-aggregated cells</b>, not a '
           'spatial scan.<br><br>'
           '<span style="color:#ffd483">And the privacy benefit falls out free: a cell ID <i>is</i> the '
           'anonymisation.</span></div>',
           """Deep dive one: geospatial indexing, and specifically why you discretise space rather than """
           """storing coordinates.""", step=0)
seg(sid, 1, """The naive approach stores latitude and longitude and queries with a bounding box. It """
            """works, and it has three problems: it needs a spatial index, aggregation has to happen at """
            """query time, and you are storing exact points &mdash; which we already ruled out on """
            """privacy grounds.""")
seg(sid, 2, """The better approach is to discretise space on ingest. Geohash encodes a rectangle as a """
            """string, where a longer prefix means a smaller cell, so prefix search becomes a range """
            """scan. Its weaknesses are that cells distort badly toward the poles, and neighbouring """
            """cells are not always adjacent in prefix space, which makes &ldquo;cells near this """
            """one&rdquo; awkward.""")
seg(sid, 3, """H3 uses hexagons, which gives equal-area cells and &mdash; the property that matters for """
            """heat maps &mdash; every neighbour is equidistant. With squares, the diagonal neighbours """
            """are one point four times further away than the edge ones, so any smoothing or """
            """neighbourhood calculation is subtly distorted. Hexagons do not have that """
            """problem.""")
seg(sid, 4, """S2 uses squares projected onto a sphere and is excellent for region coverings and range """
            """queries. Any of the three is defensible; what matters is that you discretise and can say """
            """why you picked yours.""")
seg(sid, 5, """And here is why it matters architecturally: a fixed cell grid means the count is """
            """incremented at write time, so a viewport query becomes a lookup of pre-aggregated cells """
            """rather than a spatial scan over points. You moved the work from the frequent operation """
            """to the rare one.""")
seg(sid, 6, """And the privacy benefit falls out for free, which is the elegant part &mdash; the cell I-D """
            """<i>is</i> the anonymisation. You did not add a privacy step; you chose a representation """
            """that does not contain the sensitive information.""")

sid = beat('Deep dive 2', 'Real-time or batch &mdash; and why &ldquo;live&rdquo; is usually a product word',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>&ldquo;Live map&rdquo; sounds like streaming. Check what it actually needs.</b><br><br>'
           '&bull; Sign-ups arrive at <b>~2 per second</b><br>'
           '&bull; A human watching a world map <b>cannot perceive</b> a single new dot among '
           'thousands<br>'
           '&bull; Tiles are rendered for <i>display</i>, and a 5-minute refresh is indistinguishable '
           'from live to the viewer<br><br>'
           '<span style="color:#a8e6a3">So: micro-batch every 5 minutes. It looks live, costs almost '
           'nothing, and removes an entire streaming pipeline from the design.</span><br><br>'
           '<b>When I <i>would</i> go properly real-time:</b><br>'
           '&bull; If the map drives an <b>operational decision</b> &mdash; detecting a sign-up fraud '
           'wave by region<br>'
           '&bull; If there is an animated &ldquo;someone just joined&rdquo; effect that must feel '
           'immediate<br><br>'
           '<b>And even then, the honest version is a hybrid:</b> pre-rendered tiles for the base heat '
           'map, plus a thin real-time event feed for the animation on top. '
           '<span style="color:#ffd483">Two mechanisms, each doing what it is good at &mdash; rather '
           'than making one pipeline serve both and doing neither well.</span></div>',
           """Deep dive two: real-time or batch. &ldquo;Live map&rdquo; sounds like it demands """
           """streaming, and I would check what it actually needs before building one.""", step=0)
seg(sid, 1, """Sign-ups arrive at about two a second. A human watching a world map genuinely cannot """
            """perceive a single new dot among thousands. And tiles are rendered for display, so a """
            """five-minute refresh is indistinguishable from live to the person looking at it.""")
seg(sid, 2, """So: micro-batch every five minutes. It looks live, it costs almost nothing, and it """
            """removes an entire streaming pipeline from the design. Being able to delete a subsystem by """
            """questioning an adjective is a genuinely valuable habit.""")
seg(sid, 3, """When would I go properly real-time? If the map drives an operational decision &mdash; """
            """spotting a sign-up fraud wave concentrated in one region, for instance. Or if there is an """
            """animated &ldquo;someone just joined&rdquo; effect that has to feel immediate.""")
seg(sid, 4, """And even then the honest answer is a hybrid: pre-rendered tiles for the base heat map, """
            """plus a thin real-time event feed for the animation layered on top. Two mechanisms, each """
            """doing what it is good at, rather than forcing one pipeline to serve both and doing """
            """neither well. That pattern &mdash; a cheap bulk path plus a thin fast path &mdash; has """
            """now appeared in typeahead freshness, the feed, and here.""")

tradeoff('Where aggregation happens', [
 ('Store raw points, aggregate at query time', 'info',
  ['Maximum flexibility &mdash; any grouping, any zoom, later',
   'Can re-analyse historically with new questions'],
  ['<b>You are storing individual locations</b> &mdash; a standing privacy liability',
   'Every query does spatial work', 'A bug or a breach exposes people, not statistics']),
 ('Aggregate on ingest, store only cell counts', 'ok',
  ['<b>Raw locations never persisted</b> &mdash; the strongest possible guarantee',
   'Queries are lookups, not scans', 'Smaller than the raw data'],
  ['Cell size and time bucket fixed at ingest &mdash; changing them needs a backfill you cannot do',
   'Cannot answer questions you did not anticipate']),
 ('Aggregate on ingest, keep raw briefly in a locked store', 'shared',
  ['Can re-aggregate at a new resolution for a short window', 'Supports fraud investigation'],
  ['The raw data still exists &mdash; <b>access control is now the only protection</b>',
   'Retention policy must be enforced, and will be forgotten']),
], 'Aggregate on ingest and store only cell counts. The inflexibility is the point: data that does not '
   'exist cannot leak, be subpoenaed, or be misused by a future feature.',
 'If fraud detection genuinely required re-analysing raw locations, I would keep them &mdash; in a '
 'separate, access-controlled, short-retention store that the map pipeline cannot read. <b>Not in the '
 'same database with a flag.</b>',
 [
 """Trade-off: where does aggregation happen? Storing raw points and aggregating at query time gives """
 """maximum flexibility &mdash; any grouping, any zoom level, any new question later. The cost is that """
 """you are storing individual locations, which is a standing liability, every query does spatial work, """
 """and a bug or a breach exposes people rather than statistics.""",
 """Aggregating on ingest and storing only cell counts means raw locations are never persisted, which """
 """is the strongest guarantee available &mdash; stronger than any access control. Queries become """
 """lookups. And the store is smaller than the raw data would have been.""",
 """The cost is real inflexibility: cell size and time bucket are fixed at ingest, and changing them """
 """needs a backfill you cannot perform, because the source data is gone. You cannot answer questions """
 """you did not anticipate.""",
 """I would still choose it, and I would argue the inflexibility is the point. Data that does not exist """
 """cannot leak, cannot be subpoenaed, and cannot be misused by a future feature written by someone who """
 """was not in this conversation. That last one is underrated &mdash; most privacy incidents are a new """
 """feature doing something reasonable with data it should not have had.""",
 """What would flip it: if fraud detection genuinely required re-analysing raw locations, I would keep """
 """them &mdash; in a separate, access-controlled, short-retention store that the map pipeline cannot """
 """read. Not in the same database with a flag on it, because flags get flipped.""",
])

failures('What happens when each piece dies', [
 ('Geo resolution fails for an event', 'That sign-up is not on the map',
  '<b>Drop it and count the drops.</b> Do not guess a location &mdash; a wrong dot is worse than a '
  'missing one on a map people draw conclusions from'),
 ('A cell has fewer than k members', 'That area shows as empty',
  '<b>Working as designed.</b> But say it out loud: the map <i>systematically under-represents rural '
  'areas</i>, which is a real analytical bias someone will eventually misread'),
 ('Tile rendering falls behind', 'Map shows data from 20 minutes ago',
  'Nobody notices. <b>Alert on tile age, not on job success</b> &mdash; and show the timestamp on the '
  'map so viewers are not misled'),
 ('Aggregator loses events', 'Counts are slightly low',
  'Acceptable for a visualisation. <b>Would not be acceptable if the same pipeline fed growth '
  'reporting</b> &mdash; so do not let it'),
 ('Someone requests a tile at zoom 20', 'Potential identification',
  '<b>Enforce max zoom server-side</b>, not in the client. A client-side limit is a suggestion'),
 ('A new feature asks for the raw points', 'The privacy design is quietly undone',
  '<b>The most likely real failure, and it is organisational.</b> The protection is that the data was '
  'never stored &mdash; which is why aggregation on ingest beats a policy document'),
], [
 """Failures. Geo resolution fails for an event and that sign-up does not appear. Drop it and count the """
 """drops &mdash; do not guess a location. On a map that people draw conclusions from, a wrong dot is """
 """worse than a missing one.""",
 """A cell with fewer than k members shows as empty. That is working as designed, and I would still say """
 """it out loud: the map systematically under-represents rural areas. Somebody will eventually look at """
 """it and conclude LinkedIn has no users in the countryside, and that is an analytical bias you """
 """introduced deliberately and should document.""",
 """Tile rendering falls behind and the map shows data from twenty minutes ago. Nobody notices. Alert """
 """on tile age rather than job success, and show the timestamp on the map so viewers are not """
 """misled.""",
 """The aggregator losing events makes counts slightly low. Acceptable for a visualisation &mdash; and """
 """it would not be acceptable if the same pipeline fed growth reporting, so do not let it. Keeping the """
 """pretty map and the business metrics on separate pipelines is a decision worth making """
 """explicitly.""",
 """Someone requesting a tile at zoom twenty is a potential identification, so enforce the maximum zoom """
 """server-side rather than in the client. A client-side limit is a suggestion, not a control.""",
 """And a new feature asking for the raw points quietly undoes the entire privacy design. I would call """
 """this the most likely real failure in this system, and it is organisational rather than technical. """
 """The protection is that the data was never stored in the first place &mdash; which is precisely why """
 """aggregation on the ingest path beats a policy document that someone has to remember.""",
])

say('What I should actually say in the room', [
 'Before anything else: this plots real people&rsquo;s locations, so the privacy constraint is a floor, '
 'not a feature. Zoom in far enough on a naive implementation and a dot is an identifiable person.',
 'So I aggregate on ingest, not at query time. The geo resolver turns a location into an H3 cell ID, '
 'and nothing downstream ever sees an individual location. The raw point is never persisted.',
 'Then k-anonymity suppression drops any cell with fewer than k members &mdash; and I want k to be an '
 'explicit named number that someone other than me reviews.',
 'The numbers make this easy: about two sign-ups a second, so ingestion is trivial. The real load is '
 'read &mdash; maybe 2,000 tile requests a second.',
 'So I pre-render tiles every five minutes and serve them from a CDN. The map never queries a database, '
 'and ten thousand viewers cost almost nothing.',
 'On &ldquo;live&rdquo; &mdash; I would push back gently. A human cannot perceive one new dot among '
 'thousands, so a five-minute refresh is indistinguishable from live and removes a whole streaming '
 'pipeline.',
 'And the failure I would actually worry about is organisational: a future feature asking for the raw '
 'points. The protection is that they were never stored, which is why aggregation has to be on the '
 'ingest path rather than in a policy document.',
], [
 """The sentences. Lead with privacy as a floor, because the question named it and because it genuinely """
 """determines the architecture.""",
 """Then aggregation on ingest with the cell I-D boundary, and k as an explicit reviewable number. Then """
 """the arithmetic that makes it a read problem, and the C-D-N answer.""",
 """Then push back on &ldquo;live&rdquo;, which deletes a subsystem. And finish on the organisational """
 """failure &mdash; naming that the real risk is a future colleague rather than a bug is a very """
 """staff-level observation.""",
])

followups([
 'How do you ingest the sign-up events?',
 'How do you aggregate geographically?',
 'What geospatial index do you use?',
 'How do you protect privacy?',
 'Real-time or batch?',
 'How do map tiles work?',
 'How do you query a geographic region?',
], [
 'Someone wants to compare sign-ups by region year over year. Can you?',
 'How would you add a &ldquo;someone just joined&rdquo; animation without weakening privacy?',
 'The map shows nothing in rural areas. Is that a bug?',
 'How do you stop this becoming the source of truth for growth reporting?',
 'What would a privacy reviewer ask you that I have not?',
],
 """The reported follow-ups are the lesson. On querying a geographic region: because cells are """
 """pre-aggregated, a viewport query is a lookup of the cell I-Ds covering that bounding box &mdash; """
 """both H3 and S2 give you a covering function for exactly this &mdash; and then you sum. No spatial """
 """scan.""",
 """The staff-level follow-ups are the better ones. Year-over-year comparison works if you kept time """
 """buckets, which is why you aggregate by cell <i>and</i> time rather than cell alone. The animation """
 """can be done safely by emitting &ldquo;a sign-up happened in this large cell&rdquo; without """
 """identity or precise location. Nothing in rural areas is not a bug, it is k-anonymity &mdash; and """
 """the map should say so rather than looking like absence. Stopping it becoming the source of truth """
 """for growth reporting is organisational: the suppressed, lossy, display-oriented aggregate is not a """
 """business metric, and if you do not say that loudly someone will put it in a board deck. And the """
 """last one is the best question on the slide &mdash; what would a privacy reviewer ask that I have """
 """not? The honest answer is usually &ldquo;how long do you keep it, who can access it, and what """
 """happens when someone deletes their account?&rdquo;""")

cheatsheet('Sign-up map &mdash; the one-page card', [
 ('Requirements', 'Show where new members are joining, without identifying anyone'),
 ('Scale', '~2 sign-ups/s (trivial); ~2,000 tile reads/s. <b>A read problem, not an ingest one</b>'),
 ('Core architecture', 'Sign-up event &rarr; geo resolver (&rarr; H3 cell) &rarr; aggregate per cell '
                       'per bucket &rarr; k-anonymity suppression &rarr; tile render &rarr; CDN'),
 ('Data store', '<b>Cell counts only.</b> Raw locations are never persisted anywhere queryable'),
 ('Partition key', 'H3 cell ID &mdash; and the cell ID <i>is</i> the anonymisation'),
 ('Cache', 'Pre-rendered tiles on a CDN. The serving path never touches a database'),
 ('Queue', 'The sign-up event stream; micro-batched every ~5 minutes'),
 ('Consistency', 'Eventual, bounded by the tile refresh interval. <b>Show the timestamp on the map</b>'),
 ('Failure handling', 'Drop unresolvable locations and count them; alert on tile <b>age</b>; enforce '
                      'max zoom server-side'),
 ('Key deep dives', 'Aggregate on ingest, not on query &middot; why &ldquo;live&rdquo; is usually a '
                    'product word'),
 ('Biggest trade-off', 'Flexibility vs privacy &mdash; and <b>the inflexibility is the feature</b>: '
                       'data that does not exist cannot leak'),
], [
 """The card. Scale is here mainly to establish that this is a read problem. Architecture in one line, """
 """with the suppression step explicit.""",
 """The data store row is the whole design: cell counts only, raw locations never persisted anywhere """
 """queryable. And the partition key row carries the elegant bit &mdash; the cell I-D is the """
 """anonymisation.""",
 """Consistency is bounded by tile refresh, and show the timestamp so nobody is misled. And the biggest """
 """trade-off is flexibility against privacy, where the inflexibility is the feature: data that does """
 """not exist cannot leak.""",
])

say('The 60-second answer', [
 'The first thing I would say is that this plots real people&rsquo;s locations, so privacy is a floor '
 'rather than a feature &mdash; zoom far enough into a naive version and one dot is an identifiable '
 'person, on a public map, from a company that also knows their employer.',
 'So I aggregate on ingest rather than at query time. A geo resolver converts the location to an H3 cell '
 'ID, and nothing downstream ever sees an individual location; the raw point is never persisted '
 'anywhere queryable.',
 'Then k-anonymity suppression drops any cell with fewer than k members, and k should be an explicit, '
 'named, reviewable number rather than a constant buried in code.',
 'The arithmetic makes the rest easy: about two sign-ups a second, so ingestion is nothing, while '
 'reads might be 2,000 tile requests a second. So I pre-render tiles and serve them from a CDN, and the '
 'map never queries a database at all.',
 'On &ldquo;live&rdquo; I would push back gently &mdash; a person cannot perceive one new dot among '
 'thousands, so a five-minute refresh looks live and removes an entire streaming pipeline from the '
 'design.',
 'And the failure I would genuinely worry about is organisational rather than technical: some future '
 'feature asking for the raw points. The protection is that they were never stored &mdash; which is '
 'exactly why aggregation belongs on the ingest path and not in a policy document.',
], [
 """The sixty-second answer. Leading with privacy is correct here because the question named it, and """
 """because it is the thing that actually decides the architecture.""",
 """The last sentence is the one to land. Recognising that the most likely privacy failure is a """
 """well-meaning colleague in eighteen months, and that the defence is structural rather than """
 """procedural, is a genuinely senior observation and very few candidates make it.""",
], kicker='60-second interview answer')
