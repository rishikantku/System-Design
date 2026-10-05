# -*- coding: utf-8 -*-
"""Chapter 6, Lesson 2 — photo storage, processing and delivery."""
from lib import *

lesson_header('6.2', 'Photo storage, processing and delivery',
              'Object store + metadata DB &middot; async pipeline &middot; CDN &middot; resumable upload',
              dict(reports='InterviewTV list only, with six follow-ups', latest='2026', level='Staff',
                   conf='MEDIUM &mdash; single source', sources='InterviewTV.io'), 18,
              """Chapter six, lesson two: photo storage, processing and delivery. Upload, process, store """
              """metadata, store files, deliver. And then six follow-ups that each change the """
              """architecture: fifty million uploads a day, two-second processing, multiple formats, """
              """albums, video, and an upload progress bar. I want to do this one slightly differently """
              """&mdash; build the base system quickly, then spend most of the lesson evolving it """
              """follow-up by follow-up, because that evolution is what the question is really """
              """testing.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  'Base: upload, process, store metadata, store files, deliver. Follow-ups: <b>50M+ uploads/day, '
  '2-second processing, JPEG/GIF/TIFF, albums, video, upload progress bar</b>'),
], """Single source, so medium confidence. What is distinctive is the shape: a simple base question """
     """with six follow-ups attached, each one a different direction.""",
 ["""That is a deliberate structure. It is testing whether your first architecture can survive being """
  """changed six times &mdash; which is a much better test of design than whether the first one was """
  """clever."""],
 caveat='Single source. The object-store-plus-metadata pattern is near-universal, so this prepares you '
        'for any media question.',
 narration_caveat="""Single source. The object store plus metadata pattern is near-universal though, so """
                  """this prepares you for any media or file-handling question.""")

sid = beat('Why this is interesting', 'The base design is easy. <b>Surviving six changes</b> is the test.',
           '<div style="font-size:28px;line-height:1.72">'
           'Almost everyone draws the right base system: upload &rarr; object store, metadata in a DB, '
           'serve through a CDN. <span style="color:#a8e6a3">Correct, and not what is being '
           'measured.</span><br><br>'
           'The six follow-ups each attack a <i>different</i> part of it:<br><br>'
           '&bull; <b>50M uploads/day</b> &rarr; attacks the <i>upload path</i><br>'
           '&bull; <b>2-second processing</b> &rarr; attacks the <i>queue and worker model</i><br>'
           '&bull; <b>Many formats</b> &rarr; attacks <i>when</i> you do the work<br>'
           '&bull; <b>Albums</b> &rarr; attacks the <i>data model</i><br>'
           '&bull; <b>Video</b> &rarr; attacks nearly <i>everything</i><br>'
           '&bull; <b>Progress bar</b> &rarr; attacks the <i>client protocol</i><br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: a design that bends in six directions '
           'beats a design that is optimal in one. Build the base deliberately loose &mdash; and say '
           'that you are doing it.</span></div>',
           """Why is this interesting? Because almost everyone draws the correct base system &mdash; """
           """upload to an object store, metadata in a database, serve through a C-D-N. That is right, """
           """and it is not what is being measured.""", step=0)
seg(sid, 1, """The six follow-ups each attack a different part of it. Fifty million uploads a day attacks """
            """the upload path. Two-second processing attacks the queue and worker model. Many formats """
            """attacks when you do the work. Albums attacks the data model.""")
seg(sid, 2, """Video attacks nearly everything at once. And the progress bar, which sounds like the """
            """trivial one, actually attacks the client protocol &mdash; and it is the follow-up most """
            """candidates fumble, because they have never thought about how an upload actually """
            """works.""")
seg(sid, 3, """So the staff-level insight is: a design that bends in six directions beats a design that """
            """is optimal in one. I am going to build the base deliberately loose &mdash; and """
            """critically, I would say out loud that I am doing that, because otherwise it just looks """
            """like I have not optimised anything.""")

think('A user uploads a 5 MB photo on a flaky mobile connection and it fails at 90%. What does your '
      'upload path have to look like for them not to start again from zero &mdash; and what does the '
      'server have to remember between the two attempts?',
      25,
      """Pause. A user uploads a five megabyte photo on a flaky mobile connection and it fails at """
      """ninety percent. What does your upload path have to look like so they do not start again from """
      """zero? And what does the server have to remember between the two attempts? Say it out loud.""",
      """Hold that. It is the progress-bar follow-up and the resumable-upload answer, and they turn out """
      """to be the same mechanism.""")

clarify('What I would clarify first', [
 ('Who views the photos &mdash; public, or permissioned?',
  '<b>Public means a CDN URL is enough.</b> Permissioned means signed, expiring URLs and you cannot '
  'cache as aggressively &mdash; a completely different delivery story.'),
 ('Do originals need to be kept forever?',
  'Originals dominate storage. If they can move to cold storage after 30 days, <b>cost drops by '
  '~5&times;</b> and nothing user-visible changes.'),
 ('Is the photo usable immediately after upload, or only once processed?',
  'Immediately means serving the original while variants are generated. That single answer decides '
  'whether processing is <b>on</b> the critical path.'),
 ('What variants do we need, and who decides &mdash; us or the client?',
  'A fixed set lets you pre-generate. Arbitrary sizes means on-demand resizing with a cache, which '
  'is a different system.'),
 ('Mobile, web, or both?',
  'Mobile means <b>resumable uploads are mandatory</b>, not a nicety. Networks drop; a 5 MB upload '
  'that cannot resume will fail for real users regularly.'),
 ('Any moderation or abuse scanning required?',
  'If yes, it is <b>on the critical path before anything is public</b>, and it dominates the latency '
  'budget &mdash; worth knowing before promising two seconds.'),
], [
 """Who views the photos &mdash; public or permissioned? Public means a C-D-N U-R-L is enough and life """
 """is easy. Permissioned means signed, expiring U-R-Ls, and you cannot cache nearly as aggressively, """
 """which is a completely different delivery story. Ask first.""",
 """Do originals need keeping forever? Originals dominate storage, so if they can move to cold storage """
 """after thirty days, cost drops by roughly five times and nothing user-visible changes. That is one """
 """of the cheapest wins available in this design.""",
 """Is the photo usable immediately after upload, or only once processed? Immediately means serving the """
 """original while variants are generated in the background, and that single answer decides whether """
 """processing sits on the critical path at all.""",
 """What variants do we need, and who decides &mdash; us or the client? A fixed set lets you """
 """pre-generate everything. Arbitrary sizes means on-demand resizing with a cache, which is a """
 """genuinely different system.""",
 """Mobile, web, or both? Mobile means resumable uploads are mandatory rather than a nicety. Networks """
 """drop, and a five megabyte upload that cannot resume will fail for real users regularly.""",
 """And is there moderation or abuse scanning? If so it is on the critical path before anything becomes """
 """public, and it will dominate your latency budget &mdash; which matters a lot before you promise """
 """anyone two-second processing.""",
])

capacity('Capacity', [
 ('50M uploads / day', '50M &divide; 86,400', '&asymp; 580 uploads / s',
  'Modest. <b>The count is not the problem</b> &mdash; the bytes are'),
 ('Peak 4&times;', '580 &times; 4', '&asymp; 2,300 uploads / s',
  'Each holding a connection for seconds. <b>Connection concurrency, not CPU</b>'),
 ('Original 4 MB + 4 variants &asymp; 1.5 MB', '50M &times; 5.5 MB', '&asymp; 275 TB / day',
  '<b>This is the number that matters.</b> 100 PB/year'),
 ('Ingest bandwidth', '275 TB &divide; 86,400 s', '&asymp; 3.2 GB / s sustained',
  'Peak ~13 GB/s. The upload path must <b>not</b> pass through your app servers'),
 ('Processing: 4 variants &times; ~300 ms CPU', '2,300/s &times; 1.2 s CPU', '&asymp; 2,800 cores',
  'Large but ordinary. <b>Scales horizontally &mdash; it is embarrassingly parallel</b>'),
 ('Delivery: ~20 views per photo', '50M &times; 20 &times; 200 KB', '&asymp; 200 TB / day egress',
  '<b>Egress dominates cost.</b> CDN hit ratio is the single biggest cost lever in the system'),
], [
 """Numbers. Fifty million uploads a day is about five hundred and eighty a second. That is modest, and """
 """I would say so &mdash; the count is not the problem here, the bytes are.""",
 """At four times peak, about two thousand three hundred uploads a second, each holding a connection """
 """open for several seconds. So the constraint is connection concurrency, not C-P-U.""",
 """Storage: a four megabyte original plus four variants at roughly one and a half megabytes total is """
 """about two hundred and seventy-five terabytes a day. A hundred petabytes a year. That is the number """
 """that actually matters in this design.""",
 """Ingest bandwidth is three point two gigabytes a second sustained, maybe thirteen at peak. Which """
 """gives the first architectural conclusion: the upload path must not pass through your application """
 """servers. You cannot afford to proxy thirteen gigabytes a second through a tier whose job is """
 """business logic.""",
 """Processing: four variants at about three hundred milliseconds of C-P-U each, at peak, is around two """
 """thousand eight hundred cores. Large but completely ordinary, and it scales horizontally because """
 """resizing images is embarrassingly parallel.""",
 """And delivery, at roughly twenty views per photo, is about two hundred terabytes a day of egress. """
 """Egress dominates the cost of this system, which means the C-D-N hit ratio is the single biggest """
 """cost lever you have. A one percent improvement in hit ratio is worth more than most of the """
 """engineering elsewhere.""",
])

A = Arch('Photo platform &mdash; the base architecture', kicker='Architecture', height=800)

A.box('cl',   60, 300, 150, 90, 'Client', '', kind='neutral', step=0, focus=[0, 1], small=True)
A.box('api', 260, 290, 190, 105, 'Upload API', 'issues a ticket', kind='ok', step=0, focus=0)
A.arrow('cl', 'api', step=0, label='1. request', focus=0)

A.box('obj', 560, 170, 230, 115, 'Object store', 'S3-like', kind='ok', step=1, focus=[1, 2, 5])
A.arrow('cl', 'obj', step=1, label='2. direct PUT', focus=1, via=[(400, 190)])

A.box('meta', 560, 400, 230, 115, 'Metadata DB', 'photoId, owner,<br>status, variants', kind='info',
      step=2, focus=[2, 6])
A.arrow('api', 'meta', step=2, focus=2)

A.box('q',   860, 170, 190, 105, 'Queue', 'process jobs', kind='shared', step=3, focus=3)
A.arrow('obj', 'q', step=3, label='3. event', focus=3, dashed=True)

A.box('wk',  1110, 150, 200, 95, 'Workers', 'resize, strip EXIF', kind='info', step=3, focus=3, small=True)
A.box('wk2', 1110, 265, 200, 95, 'Workers', 'scale out', kind='info', step=3, focus=3, small=True)
A.arrow('q', 'wk', step=3, focus=3)
A.arrow('q', 'wk2', step=3, focus=3)

A.arrow('wk', 'obj', step=4, label='4. variants', focus=4, dashed=True)
A.arrow('wk2', 'meta', step=4, label='5. ready', focus=4, dashed=True)

A.box('cdn', 560, 620, 230, 100, 'CDN', '~95% hit', kind='ok', step=5, focus=5)
A.box('view', 260, 620, 190, 100, 'Viewer', '20 views/photo', kind='neutral', step=5, focus=5, small=True)
A.arrow('view', 'cdn', step=5, focus=5)
A.arrow('cdn', 'obj', step=5, label='miss', focus=5, dashed=True)

A.note(880, 620, 'Egress is ~200 TB/day. The CDN hit ratio is the biggest single cost lever in this system.',
       step=5, kind='info', w=450)

A.narrate(0, """The client asks the upload A-P-I to start an upload, and the A-P-I issues a ticket """
             """&mdash; a pre-signed U-R-L and a photo I-D.""",
          A.flow([(210, 345), (260, 342)]))
A.narrate(1, """And then the client uploads <i>directly</i> to the object store. Not through our """
             """servers. That is the most important arrow on this diagram, and it comes straight from """
             """the arithmetic: thirteen gigabytes a second at peak should not pass through a tier whose """
             """job is business logic. Pre-signed U-R-Ls let the object store do authentication for us """
             """for a bounded window.""",
          A.flow([(135, 300), (400, 190), (560, 215)]))
A.narrate(2, """Metadata goes to a database: photo I-D, owner, status, and which variants exist. Small """
             """rows, high volume. Note that the bytes and the facts about the bytes live in completely """
             """different stores, which is the central pattern of every media system.""",
          A.flow([(450, 360), (560, 450)]))
A.narrate(3, """The object store emits an event on upload, which lands in a queue, and a pool of workers """
             """picks jobs up. Resize to variants, strip E-X-I-F &mdash; which matters, because photos """
             """carry G-P-S coordinates and you should not serve those by accident.""",
          A.flow([(790, 227), (860, 222), (1110, 197)]))
A.narrate(4, """Workers write variants back to the object store and mark the photo ready in metadata. """
             """Processing is entirely off the upload path, so a slow worker pool makes photos appear """
             """late &mdash; it never makes uploads fail.""")
A.narrate(5, """Delivery is through a C-D-N with roughly a ninety-five percent hit ratio, falling back to """
             """the object store on a miss. At two hundred terabytes a day of egress, that hit ratio is """
             """the biggest cost lever in the whole design.""",
          A.flow([(450, 670), (560, 670)]))
A.narrate(6, """That is the base. Now let us break it six times.""")
A.build()

sid = beat('Follow-ups 1&ndash;3', 'Scale, latency, and formats',
           '<div style="font-size:26px;line-height:1.65">'
           '<b>&ldquo;50M+ uploads/day&rdquo;</b> &mdash; the upload path already handles it, because '
           'bytes never touch our servers. What breaks is <b>metadata write volume</b> (2,300 '
           'inserts/s) and <b>cost</b>. Shard metadata by photo ID; move originals to cold storage '
           'after 30 days. <span style="color:#a8e6a3">The design was already right; say which part '
           'actually strains.</span><br><br>'
           '<b>&ldquo;2-second processing&rdquo;</b> &mdash; now latency, not throughput. Three moves:<br>'
           '&bull; <b>Priority queue</b>: the one variant the user will see first (their own feed '
           'thumbnail) jumps the queue<br>'
           '&bull; <b>Parallel fan-out</b>: four variants as four jobs, not one job doing four<br>'
           '&bull; <b>Serve the original immediately</b>, downscaled by the CDN, while variants '
           'generate. <span style="color:#ffd483">The user sees their photo in 2 s even if processing '
           'takes 20.</span><br><br>'
           '<b>&ldquo;JPEG / GIF / TIFF / &hellip;&rdquo;</b> &mdash; do <i>not</i> pre-generate '
           'formats &times; sizes; that multiplies storage. Normalise to one internal format on ingest, '
           'then <b>convert on demand at the CDN edge</b> and cache the result. '
           '<span style="color:#a8e6a3">Storage is the expensive axis; compute at the edge is '
           'not.</span></div>',
           """Follow-ups one to three. First: fifty million uploads a day. And the honest answer is that """
           """the upload path already handles it, because bytes never touch our servers &mdash; so I """
           """would say that rather than inventing work.""", step=0)
seg(sid, 1, """What actually strains is metadata write volume, two thousand three hundred inserts a """
            """second, and cost. So shard metadata by photo I-D, and move originals to cold storage """
            """after thirty days. Being able to say &ldquo;the design was already right, here is """
            """specifically which part strains&rdquo; is much stronger than redesigning reflexively.""")
seg(sid, 2, """Second: two-second processing. This changes the problem from throughput to latency, which """
            """is a different kind of requirement. Three moves. A priority queue, so the one variant the """
            """user will actually see first jumps ahead of the rest.""")
seg(sid, 3, """Parallel fan-out, so four variants become four jobs rather than one job doing four things """
            """in sequence. And the move that actually wins: serve the original immediately, downscaled """
            """at the C-D-N, while the variants generate. The user sees their photo in two seconds even """
            """if processing genuinely takes twenty. You met the requirement by changing what the """
            """requirement was about.""")
seg(sid, 4, """Third: multiple formats. Do not pre-generate every format times every size &mdash; that """
            """multiplies your storage, which we established is the expensive axis. Normalise to one """
            """internal format on ingest, then convert on demand at the C-D-N edge and cache the """
            """result. Storage is expensive; compute at the edge is not. Push work to whichever """
            """resource is cheap.""")

sid = beat('Follow-ups 4&ndash;6', 'Albums, video, and the progress bar',
           '<div style="font-size:26px;line-height:1.65">'
           '<b>&ldquo;Photo albums&rdquo;</b> &mdash; a data model change, not an architecture change. '
           'An album is a row plus a join table <code>(albumId, photoId, position)</code>. '
           '<span style="color:#ffd483">The one real question: does a photo belong to many albums? If '
           'yes, deleting a photo must not break an album &mdash; so albums reference photos, they do '
           'not own them.</span><br><br>'
           '<b>&ldquo;Video&rdquo;</b> &mdash; this one breaks almost everything:<br>'
           '&bull; Files are 100&times; larger &rarr; multipart upload is <b>mandatory</b><br>'
           '&bull; Processing is minutes, not milliseconds &rarr; <b>transcoding</b>, several bitrates<br>'
           '&bull; Delivery is <b>streaming</b>: HLS/DASH, segmented, adaptive bitrate &mdash; not one '
           'file<br>'
           '&bull; <span style="color:#a8e6a3">What survives: object store, metadata DB, queue, workers, '
           'CDN. The shape holds; every component gets bigger.</span><br><br>'
           '<b>&ldquo;Upload progress bar&rdquo;</b> &mdash; and this is the one to get right:<br>'
           '&bull; Split the file into chunks (say 5 MB) and <b>upload each separately</b><br>'
           '&bull; Progress = chunks acknowledged &divide; total. <b>Measured by the client, not the '
           'server</b><br>'
           '&bull; The same chunking gives <b>resumability</b> for free: ask which chunks exist, send '
           'only the missing ones<br>'
           '<span style="color:#ffd483">Progress and resume are the same mechanism. That is the '
           'insight.</span></div>',
           """Follow-ups four to six. Albums first, and this is a data model change rather than an """
           """architecture change &mdash; worth saying, because it stops you redesigning the """
           """pipeline.""", step=0)
seg(sid, 1, """An album is a row plus a join table of album I-D, photo I-D and position. The one real """
            """question is whether a photo can belong to several albums. If it can, then deleting a """
            """photo must not break an album &mdash; so albums reference photos rather than owning """
            """them, and deletion becomes a soft delete with the album showing a placeholder.""")
seg(sid, 2, """Video breaks almost everything. Files are a hundred times larger, so multipart upload """
            """stops being optional. Processing is minutes rather than milliseconds, because you are """
            """transcoding to several bitrates rather than resizing.""")
seg(sid, 3, """And delivery becomes streaming &mdash; H-L-S or DASH, segmented into chunks with adaptive """
            """bitrate, rather than serving one file. But notice what survives: object store, metadata """
            """database, queue, workers, C-D-N. The shape holds and every component gets bigger. Saying """
            """that explicitly is the payoff for building the base loosely.""")
seg(sid, 4, """And the progress bar, which is the follow-up most candidates fumble. Split the file into """
            """chunks &mdash; say five megabytes &mdash; and upload each one separately. Progress is """
            """chunks acknowledged divided by total, and it is measured by the client, not reported by """
            """the server.""")
seg(sid, 5, """And here is the insight: the same chunking gives you resumability for free. On reconnect, """
            """the client asks which chunks the server already has and sends only the missing ones. """
            """Progress and resume are the same mechanism, which is why the answer to the question I """
            """asked you to pause on is also the answer to the progress bar. Two follow-ups, one """
            """design.""")

tradeoff('Upload: through our servers, or direct to the object store', [
 ('Proxy through application servers', 'info',
  ['Full control &mdash; validate, scan, rate-limit inline', 'One code path', 'No pre-signed URL machinery'],
  ['<b>13 GB/s at peak through your app tier</b>', 'Servers tied up for seconds per upload',
   'Bandwidth cost paid twice: in and out']),
 ('Pre-signed URL, client uploads direct', 'ok',
  ['<b>Bytes never touch our servers</b>', 'Object store handles auth for a bounded window',
   'Scales without us doing anything'],
  ['Validation happens <i>after</i> the bytes land', 'Must handle orphans &mdash; a ticket issued, '
   'nothing uploaded', 'Client must be trusted with a URL for a short window']),
 ('Direct upload via a thin edge proxy', 'shared',
  ['Streaming validation as bytes pass', 'Keeps a single entry point for auth and abuse'],
  ['Still carries the bandwidth', 'Another tier to run and scale']),
], 'Pre-signed URLs with a direct client upload. The arithmetic decides it: nothing whose job is '
   'business logic should carry 13 GB/s.',
 'If content had to be scanned <b>before</b> it was ever persisted &mdash; a hard legal or safety '
 'requirement &mdash; I would accept the proxy and its cost, because then validation cannot be allowed '
 'to happen afterwards.',
 [
 """Trade-off: does the upload go through our servers or directly to the object store? Proxying gives """
 """full control &mdash; validate, scan and rate-limit inline &mdash; with one code path and no """
 """pre-signed U-R-L machinery. It costs you thirteen gigabytes a second at peak through your """
 """application tier, servers tied up for seconds per upload, and bandwidth paid for twice, in and """
 """out.""",
 """Pre-signed U-R-Ls mean bytes never touch our servers and the object store handles authentication """
 """for a bounded window. The costs are real: validation happens after the bytes land, you have to """
 """handle orphans where a ticket was issued and nothing arrived, and the client holds a U-R-L with """
 """write access for a short period.""",
 """A thin edge proxy is the middle option &mdash; streaming validation as the bytes pass, keeping one """
 """entry point &mdash; and it still carries the bandwidth, which is the thing you were trying to """
 """avoid.""",
 """I would take pre-signed U-R-Ls and direct upload. The arithmetic decides it: nothing whose job is """
 """business logic should be carrying thirteen gigabytes a second.""",
 """What would flip it: if content had to be scanned before it was ever persisted, as a hard legal or """
 """safety requirement, then validation cannot happen afterwards and I would accept the proxy and pay """
 """its cost. The requirement changes which cost is acceptable, not which design is cleverer.""",
])

failures('What happens when each piece dies', [
 ('Processing queue backs up', 'Photos upload fine, variants appear late',
  '<b>Serve the original, downscaled at the CDN.</b> The user sees their photo; quality catches up. '
  'Alert on queue age, not depth &mdash; depth without age is meaningless'),
 ('A worker crashes mid-processing', 'Nothing &mdash; the job is retried',
  'Make variant generation <b>idempotent</b>: deterministic output key per (photo, variant), so a '
  'retry overwrites rather than duplicating'),
 ('Upload succeeds, metadata write fails', '<b>An orphaned object</b> &mdash; bytes nobody can find',
  'The classic two-store failure. Write metadata <b>first</b> with status=pending, then upload, then '
  'mark ready. Sweep pending rows older than an hour'),
 ('Metadata write succeeds, upload never happens', 'A row pointing at nothing',
  'Same sweeper, other direction. <b>Two stores means two orphan directions</b> &mdash; name both'),
 ('CDN origin is overloaded on a cache miss storm', 'Slow or failed image loads',
  'Request coalescing at the edge so 10,000 misses for one key become <b>one</b> origin fetch. '
  'Classic cache stampede, and the CDN usually has this built in'),
 ('A photo goes viral', 'One object is extremely hot',
  '<b>The CDN absorbs it</b> &mdash; this is exactly what a CDN is for. Worth saying plainly: there is '
  'no hot-key problem here because the hot path never reaches our storage'),
], [
 """Failures. Processing queue backs up: photos upload fine and variants appear late. Serve the """
 """original downscaled at the C-D-N so the user sees their photo, and let quality catch up. And alert """
 """on queue age rather than queue depth &mdash; depth without age tells you nothing, because a deep """
 """queue that is draining fast is healthy.""",
 """A worker crashes mid-processing and the job retries. Make variant generation idempotent with a """
 """deterministic output key per photo and variant, so a retry overwrites rather than creating a """
 """duplicate. At-least-once delivery makes retries certain.""",
 """Upload succeeds but the metadata write fails, and you have an orphaned object &mdash; bytes nobody """
 """can find and nobody will ever delete. This is the classic two-store failure. Write metadata first """
 """with status pending, then upload, then mark ready, and sweep pending rows older than an hour.""",
 """And the other direction: metadata written, upload never happened, so you have a row pointing at """
 """nothing. Same sweeper. The general point is that two stores means two orphan directions, and """
 """naming both shows you have actually thought it through rather than remembering one war story.""",
 """C-D-N origin overloaded during a cache miss storm: request coalescing at the edge, so ten thousand """
 """misses for one key become one origin fetch. That is the cache stampede problem, and most C-D-Ns """
 """have it built in &mdash; knowing it is already solved is as useful as knowing how to solve it.""",
 """And a photo goes viral. The C-D-N absorbs it, because that is precisely what a C-D-N is for. I """
 """would say plainly that there is no hot-key problem in this design, because the hot path never """
 """reaches our storage at all. Identifying where a classic problem does not apply is worth as much as """
 """solving one where it does.""",
])

say('What I should actually say in the room', [
 'The counts are small &mdash; 580 uploads a second &mdash; but the bytes are not: 275 TB a day of '
 'storage and about 3 GB/s of ingest. So the bytes decide the architecture, not the request rate.',
 'That means the client uploads directly to object storage with a pre-signed URL. Nothing whose job is '
 'business logic should be carrying 13 GB/s at peak.',
 'Metadata goes in a separate database &mdash; the bytes and the facts about the bytes live in '
 'different stores, which also means two directions of orphan to sweep.',
 'Processing is fully asynchronous off the upload path, so a slow worker pool makes photos appear late '
 'but never makes uploads fail.',
 'For the two-second requirement I would not try to process faster. I would serve the original '
 'downscaled at the CDN immediately and let variants catch up &mdash; the user sees their photo in two '
 'seconds even if processing takes twenty.',
 'For multiple formats I would convert on demand at the edge rather than pre-generating formats times '
 'sizes, because storage is the expensive axis and edge compute is not.',
 'And for the progress bar: chunked upload, with progress measured client-side as chunks acknowledged. '
 'The same chunking gives resumability for free, which matters because this is mostly mobile.',
], [
 """The sentences. Open by separating request count from byte volume, because that distinction is what """
 """makes every later decision obvious.""",
 """Then the direct upload with its one-line justification, the two-store split with the orphan """
 """consequence, and async processing with its failure mode.""",
 """Then the two cleverest moves &mdash; meeting the latency requirement by changing what is served, """
 """and pushing format conversion to wherever compute is cheap. Finish on chunking, and make the point """
 """that progress and resume are one mechanism.""",
])

followups([
 'How do you handle 50M+ uploads a day?',
 'How do you achieve 2-second photo processing?',
 'How do you support JPEG, GIF, TIFF and other formats?',
 'How do you support photo albums?',
 'How would you support video?',
 'How do you show an upload progress bar?',
], [
 'How do you delete a photo &mdash; everywhere, including the CDN and every variant?',
 'A photo must be removed for legal reasons within an hour. Can you?',
 'How do you detect and handle duplicate uploads of the same image?',
 'What is the cost of this system, and what is the first thing you would cut?',
 'How do you stop someone using your pre-signed URL to upload a 10 GB file?',
],
 """The six reported follow-ups are the lesson, and we answered each by evolving the architecture """
 """rather than starting over &mdash; which is exactly what the question is testing.""",
 """The staff-level follow-ups are the ones that come from running this. Deletion everywhere is """
 """genuinely hard: object store, every variant, the metadata row, and C-D-N caches at hundreds of """
 """edges &mdash; and C-D-N purge is slow, so legal deletion within an hour usually means serving """
 """through a signed U-R-L you can revoke instantly rather than relying on purge. Duplicate detection """
 """is content hashing on ingest, which also saves storage. Cost: egress dominates, so the first thing """
 """I would cut is the number of pre-generated variants. And the pre-signed U-R-L question is a good """
 """one &mdash; you set a content-length limit and a short expiry on the signature, because otherwise """
 """you have handed out unbounded write access to your bucket.""")

cheatsheet('Photo platform &mdash; the one-page card', [
 ('Requirements', 'Upload, process, store, deliver &mdash; and bend for scale, latency, formats, '
                  'albums, video, progress'),
 ('Scale', '580 uploads/s (2,300 peak), 275 TB/day stored, ~3 GB/s ingest, ~200 TB/day egress'),
 ('Core architecture', 'Pre-signed URL &rarr; direct upload to object store &rarr; event &rarr; queue '
                       '&rarr; workers &rarr; variants; metadata in a DB; delivery via CDN'),
 ('Data store', 'Object store for bytes; relational/NoSQL for metadata; <b>they fail independently</b>'),
 ('Partition key', '<code>photoId</code> for metadata. Object keys are content- or ID-derived so the '
                   'store spreads them naturally'),
 ('Cache', 'CDN, ~95% hit. <b>The hit ratio is the biggest cost lever in the system</b>'),
 ('Queue', 'Between upload and processing. Priority lane for the first-visible variant'),
 ('Consistency', 'Eventual. Photo is usable before processing completes &mdash; serve the original '
                 'meanwhile'),
 ('Failure handling', 'Idempotent variant keys; sweep orphans in <b>both</b> directions; alert on queue '
                      '<b>age</b>; request coalescing at the edge'),
 ('Key deep dives', 'Direct upload &middot; meeting 2 s by changing what is served &middot; chunked '
                    'upload = progress + resume'),
 ('Biggest trade-off', 'Pre-generate vs convert on demand. <b>Storage is expensive, edge compute is '
                       'not</b>'),
], [
 """The card. Requirements include the six follow-ups, because bending is the requirement. Scale """
 """&mdash; and the two numbers to carry are two hundred and seventy-five terabytes a day stored and """
 """two hundred egress.""",
 """Architecture in one line. Note the data store row: bytes and metadata fail independently, which is """
 """where orphans come from. Partition metadata by photo I-D. And the cache row is the cost lever.""",
 """Consistency is eventual and the photo is usable before processing finishes. Failure handling """
 """sweeps orphans in both directions. And the biggest trade-off: pre-generate versus convert on """
 """demand, where storage is expensive and edge compute is not.""",
])

say('The 60-second answer', [
 'The request count is small &mdash; under 600 uploads a second &mdash; but the bytes are not, at about '
 '275 TB a day stored and 3 GB/s ingested. So the byte volume drives the architecture, not the QPS.',
 'The client therefore uploads directly to object storage using a pre-signed URL. Nothing whose job is '
 'business logic should be carrying 13 GB/s at peak.',
 'Metadata lives in its own database, so the bytes and the facts about them are in separate stores '
 '&mdash; which means I have to sweep orphans in both directions, and I write metadata first as pending '
 'so a failed upload leaves a row I can find.',
 'Processing is asynchronous: an upload event lands on a queue, workers generate variants and strip '
 'EXIF, and a slow worker pool makes photos appear late rather than making uploads fail.',
 'To hit two-second processing I would not process faster &mdash; I would serve the original downscaled '
 'at the CDN immediately and let variants catch up. And for formats I convert on demand at the edge '
 'instead of pre-generating formats times sizes, because storage is the expensive axis.',
 'For the progress bar, the client uploads in chunks and computes progress from chunks acknowledged '
 '&mdash; and that same chunking gives resumable upload for free, which matters a lot on mobile.',
], [
 """The sixty-second answer. The first sentence does the heavy lifting: separating request count from """
 """byte volume reframes the entire problem and nobody else in the room will open with it.""",
 """Practise the fifth sentence especially &mdash; meeting a latency requirement by changing what you """
 """serve rather than how fast you compute. That is the kind of answer that gets remembered, because """
 """it solves the user's problem rather than the literal one.""",
], kicker='60-second interview answer')
