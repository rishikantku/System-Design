# -*- coding: utf-8 -*-
"""Write path and read path per question, over the boxes of the detailed architecture (detail.py).
P[qid] = dict(write=('what is being written', [(box_id, what happens)]), read=('what is being read', [(box_id, what happens)]))
build.py asserts every box id exists in that question's detailed diagram."""

P = {}

P['topn'] = dict(
 write=('A request for item "linkedin" is counted', [
  ('app', 'The app server does counts["linkedin"]++ in memory. No network call.'),
  ('k1', 'Every 10 s it sends (linkedin, 37, server-12, minute) to Kafka, keyed by item.'),
  ('flink', 'Flink adds 37 to linkedin\'s keyed state for this minute; at the window end it emits the minute\'s top-K.'),
  ('k2', 'The minute top-K list goes to the minute-topk topic.'),
  ('redis', 'A consumer does ZINCRBY topk:min:<minute> 37 linkedin (key expires in 25 h).'),
  ('roll', 'At the end of each hour the rollup job merges 60 minute lists.'),
  ('olap', '…and stores that hour\'s top 10×K in the hour store.')]),
 read=('"Top 10 for the last 5 minutes / 24 hours?"', [
  ('ui', 'The dashboard asks the Query API for top 10, window = 5 min (or 24 h).'),
  ('api', 'The API checks its 10-second result cache first.'),
  ('redis', '5 min: ZUNIONSTORE of the last 5 minute-sets, then ZREVRANGE 0 9.'),
  ('olap', '24 h: read 24 hourly lists from the hour store and merge them in the API.'),
  ('ui', 'Ranked items with counts are returned and cached for 10 s.')]))

P['metrics'] = dict(
 write=('host-1 reports memory = 72%', [
  ('agent', 'The agent collects 2,000 stats, batches 10 s of points, compresses them.'),
  ('gw', 'The gateway validates labels and rejects high-cardinality ones.'),
  ('kafka', 'It produces to Kafka with key = series_id, so one series stays ordered.'),
  ('tsdb', 'TSDB writers append the point into the series\' current 2-hour block (Gorilla-compressed).'),
  ('flink', 'In parallel, Flink updates the 1-minute and 1-hour rollups.'),
  ('alert', 'And the alert evaluator updates "mem > 70% for 5 min" state for host-1.')]),
 read=('"Graph memory for host-1..3 over the last week"', [
  ('graf', 'Grafana sends the query with the time range and step.'),
  ('query', 'The query service picks the 1-minute rollup (range is a week), finds the 3 series ids.'),
  ('tsdb', 'It range-scans those series\' blocks on their shards in parallel.'),
  ('query', 'Merges and downsamples to the step, returns ~30K points.'),
  ('graf', 'Grafana draws the lines.')]))

P['kvstore'] = dict(
 write=('put("user:42", profile)', [
  ('client', 'The client hashes the key and finds the partition leader from its cached map.'),
  ('leader', 'The leader receives the put.'),
  ('wal', 'It appends (key, length, value, CRC) to the active data file; fsync per batch.'),
  ('idx', 'It updates the index: user:42 → (file 7, offset 9,812, size 1,024).'),
  ('follow', 'It replicates the record to 2 followers and acknowledges after they have it.')]),
 read=('get("user:42")', [
  ('client', 'Hash the key → partition → leader (or a follower if slightly stale reads are fine).'),
  ('leader', 'The node receives the get.'),
  ('idx', 'One in-memory lookup gives (file 7, offset 9,812, size 1,024).'),
  ('wal', 'One pread of 1,024 bytes at that offset (often served by the page cache).'),
  ('client', 'Value returned; CRC checked.')]))

P['typeahead'] = dict(
 write=('A new company page "Ryze Labs" is created (and the daily build)', [
  ('kafka', 'The company-created event lands on Kafka.'),
  ('fresh', 'The fresh index adds "ryze labs" for its prefixes within seconds.'),
  ('spark', 'Overnight, the Spark build scores every entity and computes top-20 per prefix.'),
  ('s3', 'Sorted shard files are written to S3 with a version.'),
  ('trie', 'Prefix shard nodes load the new snapshot on rollout.')]),
 read=('Member types "Ry"', [
  ('client', 'Debounced request for prefix "ry" (browser cache checked first).'),
  ('edge', 'Popular short prefixes may be served by the edge cache.'),
  ('svc', 'On a miss, the typeahead service calls three sources in parallel with a 30 ms budget.'),
  ('trie', 'Global top-K for "ry" from the prefix shard.'),
  ('pers', 'Connections whose names start with "ry" (your Ryan) from the personal cache.'),
  ('fresh', 'Recent additions matching "ry".'),
  ('svc', 'Merge, personal first, privacy filter, return top 10.')]))

P['denylist'] = dict(
 write=('IP 203.0.113.9 is found malicious', [
  ('tap', 'A sample of requests is copied to Kafka.'),
  ('flink', 'The detector job calls isMalicious() and flags 203.0.113.9.'),
  ('db', 'The denylist service writes the entry (reason, TTL) and an outbox row in one transaction; version 51,204.'),
  ('kafka', 'The outbox relay publishes the delta to the compacted topic.'),
  ('agent', 'Every edge sidecar consumes it within seconds.'),
  ('mem', '…and inserts the IP into its in-memory trie; its version becomes 51,204.')]),
 read=('A request arrives from 203.0.113.9', [
  ('lb', 'The edge gateway extracts the client IP.'),
  ('mem', 'Longest-prefix lookup in the local trie — microseconds, no network.'),
  ('lb', 'Found → 403. Not found → the request continues.'),
  ('svc', 'Only allowed requests reach the web servers.')]))

P['mq'] = dict(
 write=('Producer sends an order event with key = order-77', [
  ('prod', 'The producer hashes order-77 to partition 5, batches it for ~5 ms, compresses.'),
  ('broker', 'Partition 5\'s leader appends the batch to its log (page cache).'),
  ('seg', 'It lands in the active 1 GB segment; the offset index is updated.'),
  ('f1', 'Followers fetch and append it; when all in-sync replicas have it, it is committed.'),
  ('prod', 'The producer gets the ack (acks=all).')]),
 read=('Consumer group "billing" reads partition 5', [
  ('cg', 'The group coordinator assigned partition 5 to one billing consumer.'),
  ('broker', 'The consumer fetches from its last committed offset.'),
  ('seg', 'The broker finds the segment by offset index and sends bytes with zero-copy.'),
  ('cg', 'After processing, the consumer commits its new offset.')]))

P['notify'] = dict(
 write=('"Priya viewed your profile" for user 42', [
  ('svc', 'The profile service publishes an event to Kafka, keyed by user 42.'),
  ('k1', 'notification-requests topic.'),
  ('engine', 'The engine consumes it and resolves the recipient.'),
  ('pref', 'Preferences: user 42 allows this category by push, not email.'),
  ('lim', 'Limits: INCR 42:social:20261015 → 3, under the limit.'),
  ('tmpl', 'Render the text in the user\'s language.'),
  ('q', 'Enqueue on push-low; also write to the in-app inbox.'),
  ('w', 'The push worker calls APNs/FCM, retries on failure, records delivery.')]),
 read=('User 42 opens the bell icon', [
  ('inbox', 'Read the latest 20 rows from the Cassandra partition for user 42.'),
  ('inbox', 'Mark them seen; unread count drops to 0.')]))

P['scheduler'] = dict(
 write=('A job "nightly-report" at 02:00 is created, then runs', [
  ('api', 'The API validates the cron and computes next_run_at = 02:00.'),
  ('db', 'Inserts the job and a SCHEDULED run row.'),
  ('sched', 'At 02:00 a worker owning that bucket claims the run with an atomic UPDATE … lease_until.'),
  ('mapi', 'It asks the machine API for a machine.'),
  ('agent', 'Dispatches; the agent starts the job and heartbeats every 10 s.'),
  ('kafka', 'Heartbeats and the final result go to run-events.'),
  ('mon', 'The monitor marks SUCCEEDED (or retries / alerts).')]),
 read=('"Did last night\'s report run?"', [
  ('api', 'GET /jobs/nightly-report/runs.'),
  ('db', 'Read run rows for the job, newest first: state, attempt, times.'),
  ('logs', 'Link to the uploaded logs for each run.')]))

P['ratelimit'] = dict(
 write=('A request from API key K uses one token', [
  ('client', 'The request arrives at the gateway.'),
  ('gw', 'The filter builds the key (K, endpoint) and reads the limit from config.'),
  ('local', 'Optional cheap local pre-check rejects obvious floods.'),
  ('redis', 'EVALSHA: refill, check, decrement — atomically; returns allowed + retry-after.'),
  ('svc', 'Allowed → forwarded to the backend; otherwise 429 with Retry-After.')]),
 read=('Ops checks "how close is K to its limit?"', [
  ('redis', 'Read the bucket for K: tokens and last refill.'),
  ('cfg', 'Compare with K\'s plan limit from the rules service.')]))

P['logging'] = dict(
 write=('A service logs an ERROR line', [
  ('app', 'JSON line written to the local log file.'),
  ('agent', 'Fluent Bit tails it, batches, compresses.'),
  ('kafka', 'Produced to logs.<service>.'),
  ('proc', 'Parsed, enriched with cluster/version, secrets masked.'),
  ('es', 'Bulk-indexed into today\'s index (hot for 7 days).'),
  ('s3', 'Also written into the hourly Parquet file in S3.'),
  ('alert', 'The error counter for the service goes up by one.')]),
 read=('"Show errors for trace abc123"', [
  ('kibana', 'Engineer searches trace_id:abc123 AND level:ERROR.'),
  ('es', 'Searches today\'s and recent daily indexes; returns lines.'),
  ('trino', 'For last month: SQL over Parquet partitions for those dates.')]))

P['feed'] = dict(
 write=('Ananya posts an article', [
  ('post', 'The post service writes the post.'),
  ('store', 'Stored in the post store by post_id.'),
  ('k', 'post-created event on Kafka.'),
  ('fan', 'Fan-out workers read her followers from the graph.'),
  ('graph', 'Follow graph returns ~800 followers.'),
  ('redis', 'LPUSH the post id onto each follower\'s feed list (capped).')]),
 read=('Ravi opens his feed', [
  ('feed', 'The feed service gathers candidates.'),
  ('redis', 'Ravi\'s list of recent post ids (plus big authors\' recent posts).'),
  ('store', 'Batch-hydrate the posts.'),
  ('rank', 'Score ~500 candidates with features.'),
  ('fs', 'Features come from the feature store.'),
  ('feed', 'Return the top 20 with a cursor.')]))

P['calendar'] = dict(
 write=('Meera creates a weekly meeting with 6 people', [
  ('api', 'POST event with UTC times, time zone and RRULE.'),
  ('db', 'One transaction: event row, 6 attendee rows, outbox row.'),
  ('outbox', 'Relay publishes event-changed to Kafka.'),
  ('idx', 'Each attendee\'s per-day index gets the event.'),
  ('sched', 'Reminder entries go into the minute buckets.')]),
 read=('Arjun opens "this week"', [
  ('api', 'GET my calendar for Mon–Sun.'),
  ('idx', 'Range read on (Arjun, day) partitions.'),
  ('api', 'Expand recurrences for the week, apply exceptions, return.')]))

P['cache'] = dict(
 write=('SET product:9 (2 KB, priority 3)', [
  ('app', 'The client library hashes the key to a node.'),
  ('node', 'The node receives the SET.'),
  ('core', 'If used + 2 KB > capacity: ask the policy for victims until it fits.'),
  ('pol', 'The policy picks a victim (LRU tail or lowest priority) and updates its structure.'),
  ('rep', 'The write is copied to the replica asynchronously.')]),
 read=('GET product:9', [
  ('local', 'Hot keys may be served by the near cache on the client.'),
  ('node', 'Otherwise the owning node.'),
  ('core', 'Map lookup; check expiry.'),
  ('pol', 'policy.onAccess (LRU moves it to the front).'),
  ('db', 'On a miss: one coalesced read from the database, then SET.')]))

P['coderpad'] = dict(
 write=('The candidate types a character', [
  ('br', 'The editor emits an insert op with the last seen seq.'),
  ('ws', 'The WebSocket gateway routes it by pad id.'),
  ('sess', 'The session node assigns seq 1,204 and applies it to the in-memory doc.'),
  ('kafka', 'Appended to Kafka (key = pad id) before broadcast.'),
  ('br', 'Broadcast to the interviewer\'s browser.'),
  ('cas', 'Persisted to Cassandra (pad, seq).')]),
 read=('Replay from minute 40', [
  ('replay', 'The replay service finds the snapshot before minute 40.'),
  ('snap', 'Loads it from S3.'),
  ('cas', 'Reads events after that seq, in order.'),
  ('replay', 'Streams them to the viewer with original timing.')]))

P['lynda'] = dict(
 write=('Index a new batch of PDFs', [
  ('s3', 'New PDFs land in the bucket.'),
  ('tika', 'Spark + Tika extract text and metadata.'),
  ('es', 'Bulk-index the text; posting lists are updated.'),
  ('mon', 'Failed files go to the retry queue.')]),
 read=('"red AND green NOT blue"', [
  ('ui', 'The member submits the query.'),
  ('api', 'Parsed into a bool query: must[red, green], must_not[blue].'),
  ('es', 'Intersect the red and green posting lists (shortest first), subtract blue, return doc ids.')]))

P['jobrec'] = dict(
 write=('Signals and nightly recommendations', [
  ('stream', 'Page views and likes stream through Kafka/Flink.'),
  ('fs', 'Short-term interest features update in the online feature store.'),
  ('cache', 'Nightly: top 50 per active member written to the precomputed store.')]),
 read=('Member opens /jobs', [
  ('ui', 'The page asks for 3 recommendations.'),
  ('reco', 'The service starts from precomputed recs if fresh.'),
  ('ann', 'Plus embedding neighbours…'),
  ('search', '…and skill/title matches.'),
  ('filter', 'Hard qualification rules remove bad matches.'),
  ('rank', 'The model scores the rest with fresh features and returns the top 3.')]))

P['photos'] = dict(
 write=('A member uploads a 4 MB photo', [
  ('app', 'The app asks for an upload.'),
  ('up', 'Upload API returns pre-signed multipart URLs.'),
  ('s3', 'The app PUTs the parts straight to S3.'),
  ('ev', 'S3 emits upload-complete.'),
  ('w', 'A worker makes the thumbnail first, then other sizes.'),
  ('meta', 'Metadata status → ready.'),
  ('es', 'Tags and caption indexed for search.')]),
 read=('A friend views the photo', [
  ('meta', 'The page gets the photo record and size URLs.'),
  ('cdn', 'The browser loads the image from the CDN (signed URL).'),
  ('s3', 'On a CDN miss, the CDN fetches from S3 once.')]))

P['logistics'] = dict(
 write=('Package P is scanned at the Pune hub', [
  ('dev', 'The scanner records the scan with a UUID (queued if offline).'),
  ('ing', 'Ingest dedupes by scan id.'),
  ('kafka', 'Produced keyed by package id.'),
  ('sm', 'State machine: AT_HUB is a valid next state.'),
  ('db', 'Conditional update of the package row.'),
  ('route', 'Next hop computed.'),
  ('notify', 'Customer notified of the new status.')]),
 read=('Customer tracks package P', [
  ('track', 'Tracking API (cached) reads status.'),
  ('db', 'Plus the scan history for P.')]))

P['spell'] = dict(
 write=('User adds "Rishikant" to their dictionary', [
  ('pers', 'The word is saved and synced to their other devices.'),
  ('wk', 'The worker merges it into the local word set.')]),
 read=('User finishes typing "recieve"', [
  ('ed', 'Word boundary → the word goes to the worker.'),
  ('wk', 'Check personal words, then the dictionary.'),
  ('dawg', 'Not found → underline.'),
  ('sym', 'Suggestions: "receive" (edit distance 1, very frequent).')]))

P['quota'] = dict(
 write=('Company C makes an API call', [
  ('dev', 'The call reaches the gateway.'),
  ('gw', 'The quota filter builds the key C:user:20261015.'),
  ('redis', 'INCR → 9,412; limit 10,000 → allowed.'),
  ('api', 'Forwarded to the API.'),
  ('kafka', 'Usage event recorded asynchronously.'),
  ('wh', 'Aggregated for reports and billing.')]),
 read=('Company C checks its usage', [
  ('bill', 'The dashboard reads daily aggregates from the warehouse.'),
  ('redis', 'Today\'s live count comes from the counter.')]))

P['geoviz'] = dict(
 write=('A member signs up in Bengaluru', [
  ('reg', 'The registration service emits member-registered.'),
  ('kafka', 'On Kafka.'),
  ('flink', 'Flink maps the IP to an H3 cell and counts it in the current 10-s window.'),
  ('redis', 'The cell\'s latest count is updated.'),
  ('pinot', 'The window\'s counts are appended for history.')]),
 read=('Viewers watch the map', [
  ('push', 'Every 5 s the push service sends changed cells.'),
  ('map', 'The map updates its heat layer.'),
  ('pinot', 'Replay mode reads the last 24 h of windows.')]))

P['inmail'] = dict(
 write=('A recruiter sends an InMail', [
  ('client', 'Send with an idempotency key.'),
  ('msg', 'Validate sender and recipient.'),
  ('credits', 'Debit one credit (same key — retries never double-charge).'),
  ('spam', 'Score for spam.'),
  ('conv', 'Store the message once in the conversation.'),
  ('kafka', 'message-sent event.'),
  ('inbox', 'Both users\' inbox rows updated.'),
  ('notif', 'Recipient offline → notification.')]),
 read=('The candidate opens their inbox', [
  ('inbox', 'Read the inbox partition: conversations with last message and unread count.'),
  ('conv', 'Open one: read messages for that conversation in seq order.')]))

P['svcauthz'] = dict(
 write=('Allow "profile" to call "messaging.Send"', [
  ('repo', 'A policy change is reviewed and merged in Git.'),
  ('dist', 'Compiled and pushed to messaging\'s sidecars.'),
  ('opa', 'The local engine loads the new rule (version bumps).')]),
 read=('profile calls messaging.Send', [
  ('a', 'profile\'s sidecar opens an mTLS connection with its certificate.'),
  ('ca', 'Certificates were issued by the internal CA.'),
  ('b', 'messaging\'s sidecar verifies the caller\'s identity from the certificate.'),
  ('opa', 'allow(profile, Send)? — local, microseconds.'),
  ('audit', 'The decision is logged asynchronously.')]))
