# -*- coding: utf-8 -*-
"""Interview-shaped design data for the 13 questions outside the top 10 (the top 10 live in
video/design/lessons/top10_data.py). Same schema:
  fr / nfr      functional and non-functional requirements
  rows, arrows  the architecture diagram (two rows of (id, title, sub) boxes)
  cap           capacity table rows (assumption, calculation, result, so the design…)
  model         data model rows (table / record, main fields, partition key, why this key)
  trade         ([option, option], chosen, what would flip it); option = (name, kind, pros, cons)
  fail          failure rows (what dies, what the user sees, what the system does)
  staff         what a Staff engineer does differently here
"""

X = {}

X['feed'] = dict(
 fr=['Post text, images, articles', 'See a ranked feed of your network', 'Like, comment, share'],
 nfr=['Feed opens in ~200 ms', 'Huge read volume', 'Influencers with millions of followers'],
 rows=[[('client', 'Client', 'open feed'), ('feed', 'Feed service', 'gather + rank'), ('rank', 'Ranking service', 'model scores'), ('posts', 'Post store', 'by post id')],
       [('write', 'Post service', 'new posts'), ('fan', 'Fan-out workers', 'push ids'), ('cache', 'Feed cache', 'per member list')]],
 arrows=[('client', 'feed'), ('feed', 'rank'), ('feed', 'posts'), ('write', 'fan'), ('fan', 'cache'), ('feed', 'cache')],
 cap=[('300M daily users × 5 opens', '', '~17K feed reads/s', 'Feed lists must be in a cache'),
      ('5M posts/day × 500 followers', '', '~30K inserts/s', 'Fan-out on write works for normal authors'),
      ('Influencer: 20M followers', 'one post', '20M writes', 'Pull their posts at read time instead')],
 model=[('post', 'post_id, author_id, text, media, created_at', 'post_id', 'Posts are fetched by id'),
        ('feed list', 'member_id → recent post_ids', 'member_id', 'One read gives a member\'s candidates'),
        ('follows', 'follower_id, followee_id', 'follower_id', 'Find who I follow quickly')],
 trade=([('Fan-out on write', 'ok', ['Fast reads'], ['Huge writes for big accounts']), ('Fan-out on read', 'shared', ['Cheap writes'], ['Slow feed opens'])],
        'Hybrid: push for normal authors, pull for very large ones, merge at read time.', 'If nobody had large followings, pure push would be enough.'),
 fail=[('Feed cache node lost', 'Feed a little slower', 'Rebuild that member\'s list from follows and recent posts'),
       ('Ranking service slow', 'Less personal order', 'Time-box it; fall back to recency order'),
       ('Fan-out backlog', 'New posts appear late', 'Queue absorbs it; scale workers')],
 staff=['Names the **influencer problem** and solves it with a hybrid.', 'Separates **candidate gathering** from **ranking**.',
        'Defines success beyond clicks: **dwell time, meaningful engagement**.', 'Has a **fallback** when ranking is slow.'])

X['calendar'] = dict(
 fr=['Create events, invite people', 'Accept / reject', 'See my calendar by day / week', 'Recurring events, reminders'],
 nfr=['Correct across time zones', 'Fast range reads', 'Reminders on time'],
 rows=[[('client', 'Client', 'web / app'), ('evt', 'Event service', 'create, RSVP'), ('db', 'Event DB', 'events + attendees')],
       [('idx', 'Calendar index', 'user, start time'), ('sched', 'Reminder scheduler', 'time buckets'), ('notif', 'Notifications', 'invite, remind')]],
 arrows=[('client', 'evt'), ('evt', 'db'), ('evt', 'idx'), ('db', 'sched'), ('sched', 'notif')],
 cap=[('50M events/day', '', '~600 writes/s', 'One DB cluster with sharding is fine'),
      ('Reads ~10× writes', '', '~6K reads/s', 'Per-user time index for "my week"'),
      ('All-hands: 10K invitees', 'one event', '10K index rows', 'Fan out asynchronously')],
 model=[('event', 'event_id, organiser, start_utc, end_utc, time_zone, rrule', 'event_id', 'Stored once, shared by all attendees'),
        ('attendee', 'event_id, user_id, status', 'event_id', 'RSVP updates one row'),
        ('calendar index', 'user_id, start_utc, event_id', 'user_id', '"My week" is one range query')],
 trade=([('Store the recurrence rule', 'ok', ['Tiny storage', 'Easy to change the series'], ['Expand on read']), ('Store every instance', 'shared', ['Simple reads'], ['Unbounded rows, painful edits'])],
        'Store the rule; expand instances for the requested range; store exceptions separately.', 'Very short series (a few instances) could be stored expanded.'),
 fail=[('Reminder scheduler down', 'Late reminders', 'Catch up on restart from time buckets'),
       ('Index write fails for one attendee', 'Event missing from their calendar', 'Retry from the outbox; reconcile job'),
       ('Daylight saving change', 'Nothing', 'Times stored as UTC + time zone')])
X['calendar']['staff'] = ['Stores **UTC + time zone**, never local time alone.', 'Uses a **recurrence rule with exceptions**.',
                          'Handles **large meetings** with async fan-out.', 'Thinks about **free/busy** and privacy of others\' calendars.']

X['cache'] = dict(
 fr=['Get / Put / Remove', 'Capacity in bytes', 'Pluggable eviction (LRU, lowest priority, more later)', 'Then: many nodes'],
 nfr=['O(1) or O(log n) per operation', 'Thread-safe', 'Hot keys must not overload one node'],
 rows=[[('app', 'Application', 'Get / Put'), ('core', 'Cache core', 'tracks bytes'), ('pol', 'Eviction policy', 'interface: LRU, priority')],
       [('ring', 'Consistent hashing', 'key → node'), ('nodes', 'Cache nodes', 'shards + replicas'), ('db', 'Source of truth', 'database')]],
 arrows=[('app', 'core'), ('core', 'pol'), ('app', 'ring'), ('ring', 'nodes'), ('nodes', 'db')],
 cap=[('32 GB per node, 1 KB entries', '', '~30M entries', 'Per-entry overhead matters'),
      ('1M ops/s across 20 nodes', '', '50K ops/s per node', 'Fine in memory'),
      ('One hot key: 200K writes/s', '', 'one node overloaded', 'Split the key or batch locally')],
 model=[('entry', 'key, value, size_bytes, priority, expires_at, policy metadata', 'hash(key) → node', 'Even spread across nodes'),
        ('policy state', 'LRU list / priority heap', '— (per node)', 'Each node evicts on its own')],
 trade=([('Strategy interface for eviction', 'ok', ['New policy = new class', 'Core stays simple'], ['A little indirection']), ('Hard-coded LRU', 'shared', ['Simplest'], ['Fails "customisable"'])],
        'An eviction policy interface the core calls on insert, access, remove and when it needs a victim.', 'If only LRU were ever needed, hard-coding it is fine.'),
 fail=[('A cache node dies', 'Some misses', 'Consistent hashing moves only its keys; protect the DB from the miss spike'),
       ('Hot key', 'Slow responses', 'Split into sub-keys or batch writes; replicate for reads'),
       ('Cache and DB disagree', 'Stale data', 'Invalidate on write, short TTL')],
 staff=['Reads "customisable" as **a policy interface**, not more if-statements.', 'Counts **bytes**, not items.',
        'Knows a **Get is a write** for LRU (needs the lock).', 'Solves **hot keys** and protects the database from miss storms.'])

X['coderpad'] = dict(
 fr=['Live code editor shared with the interviewer', 'Drawing pad', 'Invite by email', 'Replay the whole interview'],
 nfr=['Changes appear in under ~100 ms', 'No lost edits', 'Replay exact and seekable'],
 rows=[[('browser', 'Browsers', 'editor + pad'), ('ws', 'WebSocket gateway', 'route by pad id'), ('sess', 'Pad session service', 'orders events')],
       [('log', 'Event log', 'append-only per pad'), ('snap', 'Snapshots', 'every ~500 events'), ('replay', 'Replay service', 'plays events')]],
 arrows=[('browser', 'ws'), ('ws', 'sess'), ('sess', 'log'), ('log', 'snap'), ('log', 'replay')],
 cap=[('100K interviews/day', '1 hour each', 'many live pads', 'Shard pads across session nodes'),
      ('~5 events/s per typist', '× 1 hour', '~18K events per pad', '~1 MB per pad'),
      ('100K pads × 1 MB', '', '~100 GB/day', 'Cheap to keep replays')],
 model=[('pad', 'pad_id, owner, invited_emails, created_at', 'pad_id', 'Everything is per pad'),
        ('event', 'pad_id, seq, time, type, data', 'pad_id', 'All events of a pad are read in order'),
        ('snapshot', 'pad_id, seq, document', 'pad_id', 'Late joiners and seeks start here')],
 trade=([('Event log', 'ok', ['Live sync, recovery and replay from one store'], ['Need snapshots for fast joins']), ('Save the file every few seconds', 'shared', ['Simple'], ['No replay, loses order'])],
        'Ordered event log per pad, with snapshots.', 'If replay were not needed, periodic saves could do.'),
 fail=[('WebSocket node dies', 'Brief reconnect', 'Client resends from its last seq; events are in the log'),
       ('Two editors at once (later)', 'Conflicting edits', 'OT or CRDT merge'),
       ('Replay of a long pad is slow', 'Slow seek', 'Jump from the nearest snapshot')],
 staff=['Sees that **live sync, recovery and replay are one event log**.', 'Keeps it simple: **one writer means no CRDT** — and names when that changes.',
        'Designs **late join and seek** with snapshots.', 'Secures **invite links** (signed, expiring).'])

X['lynda'] = dict(
 fr=['Search PDFs: AND, OR, NOT on words', 'Return matching documents', 'v0 in one month, two engineers'],
 nfr=['Answers in under ~500 ms', 'Index a huge collection', 'Simple to run'],
 rows=[[('pdf', 'PDF store', 'the collection'), ('extract', 'Text extraction', 'batch job'), ('build', 'Index builder', 'word → doc ids')],
       [('index', 'Inverted index', 'sorted posting lists'), ('query', 'Query service', 'merge lists'), ('ui', 'Search UI', 'members')]],
 arrows=[('pdf', 'extract'), ('extract', 'build'), ('build', 'index'), ('index', 'query'), ('query', 'ui')],
 cap=[('1M PDFs × ~20K words', '', '20B words', 'Batch indexing, not on request'),
      ('~2B (word, doc) postings', 'compressed 1–2 bytes each', 'a few GB', 'Fits on one or a few machines'),
      ('Query: 3 words', 'merge 3 lists', 'milliseconds', 'Start with the shortest list')],
 model=[('posting list', 'word → sorted [doc_id]', 'word (or doc shard)', 'One list read per query word'),
        ('document', 'doc_id, title, url', 'doc_id', 'Show results')],
 trade=([('Use Lucene / Elasticsearch', 'ok', ['Done in days', 'Phrases and ranking later'], ['Less to learn by building it']), ('Build our own index', 'shared', ['Full control'], ['Eats the whole month'])],
        'Use Lucene for v0; spend the month on PDF extraction and the pipeline.', 'A very special query type Lucene cannot do.'),
 fail=[('A PDF fails to parse', 'That document missing', 'Log it, retry later, continue the batch'),
       ('Index grows past one machine', 'Slower queries', 'Shard by document, query all shards'),
       ('Common word ("the")', 'Huge lists', 'Stop words or skip pointers')],
 staff=['Respects the **one-month constraint** and picks a buildable v0.', 'Explains **how AND / NOT run** on sorted lists.',
        'Spots the real risk: **PDF extraction**.', 'Has a clear **v1 path**: phrases, ranking, sharding.'])

X['jobrec'] = dict(
 fr=['Top 3 jobs on /jobs for each member', 'Hard filter: basic qualification', 'Personal ranking from the profile', 'Optional: real-time interest'],
 nfr=['~200 ms page load', '1B members, 100M daily', 'New jobs visible in minutes'],
 rows=[[('member', 'Member opens /jobs', ''), ('reco', 'Recommendation service', 'retrieve → filter → rank'), ('rank', 'Ranking model', 'scores')],
       [('retr', 'Candidate retrieval', 'search + embeddings'), ('feat', 'Feature store', 'profiles, jobs'), ('rt', 'Real-time signals', 'Kafka stream')]],
 arrows=[('member', 'reco'), ('reco', 'retr'), ('reco', 'rank'), ('rank', 'feat'), ('rt', 'feat')],
 cap=[('100M daily users open /jobs', '', '~1.2K req/s, ~5K peak', 'Precompute for active members'),
      ('20M active jobs', '', 'too many to score', 'Retrieve ~500 candidates first'),
      ('Rank 500 per request', '', 'ms each with a light model', 'Two-stage ranking')],
 model=[('member features', 'member_id, skills, title, seniority, location', 'member_id', 'One read per request'),
        ('job', 'job_id, title, skills, seniority, location, posted_at', 'job_id', 'Indexed for retrieval'),
        ('precomputed recs', 'member_id → [job_id, score]', 'member_id', 'Fast page load')],
 trade=([('Precompute nightly + re-rank live', 'ok', ['Fast', 'Still fresh'], ['Storage for active members']), ('Fully online', 'shared', ['Always fresh'], ['Slow and expensive'])],
        'Precompute candidates for active members, re-rank at request time.', 'Tiny job catalogue — then online ranking is cheap.'),
 fail=[('Ranking model slow', 'Less personal', 'Serve precomputed order'),
       ('New member, empty profile', 'Generic jobs', 'Cold start: location, title, popular jobs'),
       ('Popular job flooded', 'Poor match quality', 'Diversity and exposure limits')],
 staff=['Puts the **qualification rule as a hard filter**, not in the model.', 'Designs **retrieve then rank**.',
        'Measures **two-sided success** (recruiter replies), not clicks.', 'Plans **cold start**.'])

X['photos'] = dict(
 fr=['Upload from desktop or phone', 'Process: sizes, thumbnails', 'Store, catalogue, search', 'Deliver fast'],
 nfr=['50M uploads/day', 'Thumbnail in ~2 s', 'Durable — never lose a photo'],
 rows=[[('client', 'Client', 'phone / web'), ('up', 'Upload service', 'pre-signed URL'), ('s3', 'Object storage', 'originals + sizes')],
       [('q', 'Queue', 'upload complete'), ('work', 'Processing workers', 'thumbnail first'), ('cdn', 'CDN', 'delivery')]],
 arrows=[('client', 'up'), ('client', 's3'), ('s3', 'q'), ('q', 'work'), ('work', 's3'), ('s3', 'cdn')],
 cap=[('50M uploads/day', '', '~600/s, 2K peak', 'Workers scale on queue depth'),
      ('3 MB average', '', '~150 TB/day originals', 'Object storage, not a database'),
      ('Reads ~100× writes', '', 'heavy read traffic', 'CDN for every read')],
 model=[('photo', 'photo_id, owner_id, status, sizes, tags, created_at', 'owner_id', '"My photos" is one partition'),
        ('object key', 'owner/photo_id/size', '— (object store)', 'Predictable paths for the CDN')],
 trade=([('Upload straight to storage', 'ok', ['API servers stay small', 'Resumable'], ['Need pre-signed URLs']), ('Upload through API servers', 'shared', ['Simple'], ['Servers carry 3 MB bodies'])],
        'Pre-signed URLs, direct to object storage.', 'Tiny files and low volume.'),
 fail=[('A worker crashes mid-photo', 'Photo stays "processing"', 'Message returns to the queue, retried'),
       ('Storage region down', 'Uploads fail there', 'Multi-region buckets, retry elsewhere'),
       ('Photo deleted', 'Old copy still cached', 'Purge CDN on delete')],
 staff=['Keeps **file bytes off the API servers**.', 'Makes processing **async with the thumbnail first**.',
        'Separates **metadata from blobs**.', 'Plans **video** as a separate pipeline.'])

X['logistics'] = dict(
 fr=['Create shipments', 'Scan at every hub', 'Route packages between hubs', 'Track status'],
 nfr=['Scans arrive late or twice (offline devices)', 'Tracking always available', 'Clear on what we optimise'],
 rows=[[('scan', 'Scanners / driver apps', 'often offline'), ('ingest', 'Scan ingestion', 'idempotent'), ('pkg', 'Package service', 'state machine')],
       [('route', 'Routing service', 'hub graph'), ('track', 'Tracking store', 'history per package'), ('notify', 'Notifications', 'status changes')]],
 arrows=[('scan', 'ingest'), ('ingest', 'pkg'), ('pkg', 'route'), ('pkg', 'track'), ('pkg', 'notify')],
 cap=[('10M packages/day × 10 scans', '', '~1.2K scans/s', 'Modest; reliability matters more than speed'),
      ('A few thousand hubs', '', 'small graph', 'Routing fits in memory'),
      ('Tracking reads ~5× scans', '', '~6K reads/s', 'Read replicas / cache')],
 model=[('package', 'package_id, state, current_hub, route, promise_date', 'package_id', 'Every scan updates one package'),
        ('scan event', 'scan_id, package_id, hub, type, time', 'package_id', 'History read per package'),
        ('hub graph', 'hub, neighbour, travel_time, capacity', '— (in memory)', 'Small, read by routing')],
 trade=([('Good-enough hub routing', 'ok', ['Simple, fast'], ['Not perfectly optimal']), ('Full vehicle routing optimisation', 'shared', ['Lower cost'], ['NP-hard, big project'])],
        'Shortest path over the hub graph; optimise later.', 'If truck cost dominated and the team was large.'),
 fail=[('Scanner offline for hours', 'Tracking looks stale', 'Device syncs later; scan_id makes it idempotent'),
       ('A hub closes', 'Delays', 'Mark it unavailable; re-route; notify customers'),
       ('Late scan after "delivered"', 'Nothing', 'Kept in history; state does not move backwards')],
 staff=['Uses a **state machine** with only valid transitions.', 'Makes scans **idempotent** for offline devices.',
        'Answers "**where not to optimise**" honestly.', 'States the **objective**: on-time first, then cost.'])

X['spell'] = dict(
 fr=['Underline misspelled words while typing', 'Suggest corrections', 'Later: real-time completions'],
 nfr=['Underline within ~50 ms', 'Works offline', 'Per-user custom words'],
 rows=[[('editor', 'Editor', 'word finished'), ('dict', 'Local dictionary', 'compressed trie'), ('sugg', 'Suggestion engine', 'edit distance')],
       [('user', 'Personal dictionary', 'synced'), ('upd', 'Dictionary updates', 'background download')]],
 arrows=[('editor', 'dict'), ('dict', 'sugg'), ('user', 'dict'), ('upd', 'dict')],
 cap=[('~500K English words', '', '~5 MB text, less as a trie', 'Ship it to the client'),
      ('User types ~5 words/s', '', 'tiny load', 'No server call per word'),
      ('100M users', 'if done on servers', 'huge QPS', 'Client-side is the right place')],
 model=[('dictionary', 'trie / DAWG of words + frequency', '— (on device)', 'Fast lookups offline'),
        ('personal words', 'user_id → words', 'user_id', 'Synced across devices')],
 trade=([('Check on the client', 'ok', ['Fast, offline, private'], ['Smaller models']), ('Check on a server', 'shared', ['Smarter, context-aware'], ['Latency and cost per keystroke'])],
        'Client for checking; optional server for smarter suggestions.', 'If suggestions must use a large language model.'),
 fail=[('Dictionary download fails', 'Old dictionary', 'Keep the last version'),
       ('Name flagged as wrong', 'Annoying underline', 'Add to personal dictionary'),
       ('Very long document', 'Slow re-check', 'Only re-check changed words')],
 staff=['Puts the work **on the client**, with reasons.', 'Checks **finished words**, not every key.',
        'Ranks suggestions by **frequency and context**.', 'Plans **languages and personal words**.'])

X['quota'] = dict(
 fr=['Daily quota per company / user', 'Reject over-quota calls', 'Collect usage for reports and billing'],
 nfr=['~1 ms added per call', 'Accurate enough for the business', 'Billing must be exact'],
 rows=[[('dev', 'API callers', 'companies'), ('gw', 'API gateway', 'check quota'), ('api', 'API services', '')],
       [('redis', 'Counter store', 'Redis, key per day'), ('cfg', 'Quota config', 'per plan'), ('kafka', 'Usage log', 'Kafka → warehouse')]],
 arrows=[('dev', 'gw'), ('gw', 'api'), ('gw', 'redis'), ('cfg', 'gw'), ('gw', 'kafka')],
 cap=[('100K calls/s', '', 'one counter update each', 'Redis cluster, atomic increment'),
      ('Millions of (company, user, day) keys', '', 'fits in memory', 'Expire after the day'),
      ('Usage logs 100K/s × 200 B', '', '~1.7 TB/day', 'Warehouse for reports')],
 model=[('counter', 'company:user:date → count', 'company + user', 'One atomic key per day'),
        ('quota config', 'company / plan → daily limit', 'company', 'Cached in gateways'),
        ('usage event', 'company, user, endpoint, time', 'date', 'Billing and reports')],
 trade=([('Central counter per call', 'ok', ['Exact enforcement'], ['~1 ms and a dependency']), ('Local counters, sync every second', 'shared', ['Fast'], ['Small overshoot'])],
        'Central atomic counters; local counting only for the hottest keys.', 'If small overshoot is fine and latency is critical.'),
 fail=[('Redis down', 'Calls allowed briefly', 'Fail open, reconcile from logs'),
       ('Hot company key', 'Slow checks', 'Split the counter, sum the parts'),
       ('Billing dispute', 'Wrong bill', 'Bill from usage logs, not counters')],
 staff=['Puts the **date in the key** — no reset job.', 'Separates **enforcement** from **billing**.',
        'States the **fail-open** choice.', 'Handles **hot keys**.'])

X['geoviz'] = dict(
 fr=['Live map of new sign-ups by location', 'Zoom in and out', 'Optional: replay last 24 hours'],
 nfr=['Updates every few seconds', 'Privacy — no exact locations', 'Many viewers'],
 rows=[[('acct', 'Sign-up service', 'emits events'), ('kafka', 'Kafka', 'events'), ('geo', 'Geo enrichment', 'IP → cell')],
       [('agg', 'Stream aggregator', 'count per cell per 10 s'), ('store', 'Aggregate store', 'history'), ('push', 'Push service', 'deltas to viewers')]],
 arrows=[('acct', 'kafka'), ('kafka', 'geo'), ('geo', 'agg'), ('agg', 'store'), ('agg', 'push')],
 cap=[('~200 sign-ups/s', '', 'low volume', 'One stream job is enough'),
      ('Changed cells per 10 s', '', 'a few thousand', 'Send deltas, not points'),
      ('Thousands of viewers', '', 'same update for all', 'Compute once, broadcast')],
 model=[('cell count', 'cell_id, window_start, count', 'window_start', 'Replay reads time windows'),
        ('sign-up event', 'user_id, time, ip_location', '— (stream)', 'Never stored with exact location on the map')],
 trade=([('Aggregate by grid cell', 'ok', ['Private, small updates'], ['Less precise']), ('Send every point', 'shared', ['Precise'], ['Privacy risk, heavy for browsers'])],
        'Grid cells (geohash / H3) with small-count hiding.', 'An internal tool where exact points are allowed.'),
 fail=[('Stream job restarts', 'Map pauses briefly', 'Resume from Kafka offset'),
       ('Location wrong (VPN)', 'Dot in the wrong place', 'Prefer profile location; it is an estimate'),
       ('Viral moment, many viewers', 'Slow updates', 'Serve the cached update from a CDN')],
 staff=['Puts **privacy first**: cells, small-count hiding.', 'Computes **once per update**, not per viewer.',
        'Uses **deltas** to keep payloads tiny.', 'Supports **zoom** with cell resolutions.'])

X['inmail'] = dict(
 fr=['Send InMail to non-connections', 'Inbox with conversations', 'Reply, read status', 'Credits for senders'],
 nfr=['Delivered in seconds', 'No double charge of credits', 'Spam control'],
 rows=[[('client', 'Sender', 'compose'), ('msg', 'Messaging service', 'credits, spam, store'), ('conv', 'Conversation store', 'messages')],
       [('credits', 'Credits service', 'deduct / refund'), ('inbox', 'Inbox index', 'per user'), ('push', 'Delivery', 'WebSocket + notification')]],
 arrows=[('client', 'msg'), ('msg', 'credits'), ('msg', 'conv'), ('msg', 'inbox'), ('inbox', 'push')],
 cap=[('50M messages/day', '', '~600/s', 'Modest write rate'),
      ('~2 KB each', '', '~100 GB/day', 'Sharded conversation store'),
      ('Inbox reads ≫ writes', '', 'heavy reads', 'Inbox index per user')],
 model=[('message', 'conversation_id, seq, sender, body, time', 'conversation_id', 'A thread is read together'),
        ('inbox entry', 'user_id, conversation_id, last_message, unread', 'user_id', '"My inbox" is one partition'),
        ('credit ledger', 'user_id, change, reason, request_id', 'user_id', 'Idempotent by request_id')],
 trade=([('Store once, index twice', 'ok', ['No duplicate bodies'], ['Two index updates']), ('Copy into both inboxes', 'shared', ['Simple reads'], ['Double storage, harder edits'])],
        'Message stored once in the conversation; both inbox entries point to it.', 'Very small scale.'),
 fail=[('Credit deducted, send fails', 'Lost credit', 'Idempotency key; refund on failure'),
       ('Recipient offline', 'Delivered later', 'Notification + inbox; no live push needed'),
       ('Spam wave', 'Bad experience', 'Sender rate limits, spam scoring')],
 staff=['Treats **credits as a ledger** with idempotency.', 'Builds **spam and abuse** in from the start.',
        'Stores **once, indexes twice**.', 'Defines **ordering** within a conversation.'])

X['svcauthz'] = dict(
 fr=['Decide which service may call which (and which methods)', 'Manage policies with review', 'Audit every decision'],
 nfr=['Check in microseconds', 'No central call per request', 'Policy changes in seconds'],
 rows=[[('caller', 'Service A', 'caller'), ('mtls', 'mTLS', 'proves identity'), ('callee', 'Service B sidecar', 'local policy check')],
       [('ca', 'Internal CA', 'certificates'), ('pol', 'Policy store', 'versioned rules'), ('dist', 'Distribution', 'push to sidecars')]],
 arrows=[('caller', 'mtls'), ('mtls', 'callee'), ('ca', 'mtls'), ('pol', 'dist'), ('dist', 'callee')],
 cap=[('3,000 services, 5M calls/s', '', 'too many for a central check', 'Check locally at the callee'),
      ('~100K rules', '', 'a few MB', 'Fits in every sidecar'),
      ('Policy changes', '', 'a few per minute', 'Push deltas')],
 model=[('policy', 'caller_service, callee_service, method, allow', 'callee_service', 'Each callee loads only its own rules'),
        ('service identity', 'service_id, certificate, rotation', 'service_id', 'Issued by the internal CA'),
        ('audit event', 'caller, callee, method, decision, time', 'date', 'Investigations by time')],
 trade=([('Local decision at the callee', 'ok', ['Microseconds', 'No single point of failure'], ['Need policy distribution']), ('Central policy service per call', 'shared', ['Simple to update'], ['Latency and outage risk on every call'])],
        'Push policies; decide locally; audit asynchronously.', 'Very low call volume.'),
 fail=[('Policy service down', 'Nothing', 'Callees keep the last version'),
       ('Certificate expires', 'Calls fail', 'Automatic rotation with alerts before expiry'),
       ('Wrong deny policy', 'Outage', 'Log-only mode before enforcing; quick rollback')],
 staff=['Separates **authentication (mTLS)** from **authorization (policy)**.', 'Keeps checks **local**.',
        'Rolls out with **log-only mode first**.', 'Plans **revocation** in seconds.'])

# Top 10 from the video data use the same schema (imported in build.py).
