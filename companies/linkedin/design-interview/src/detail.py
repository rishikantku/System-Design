# -*- coding: utf-8 -*-
"""Detailed architecture per question — the level an interviewer reaches with "which component, exactly?"

D[qid] = dict(
  rows    = [[(id, component, technology / detail)], ...]   up to 3 rows of up to 4 boxes
  arrows  = [(from, to, label)]                              label = what flows (topic, call, write)
  steps   = [(component, technology, what exactly happens, why this / the alternative)]
)
Technologies are common, defensible choices ("e.g."), not claims about what LinkedIn runs.
"""

D = {}

D['topn'] = dict(
 rows=[[('app', 'App servers', 'in-process counter'), ('k1', 'Kafka topic', 'local-counts, keyed by item'), ('flink', 'Flink job', 'keyed state, 1-min tumbling window')],
       [('k2', 'Kafka topic', 'minute-topk'), ('redis', 'Redis', 'sorted set per window'), ('roll', 'Rollup job', 'minute → hour')],
       [('olap', 'Hour store', 'Cassandra / Pinot'), ('api', 'Query API', 'merge windows'), ('ui', 'Dashboard', 'top K')]],
 arrows=[('app', 'k1', 'flush every 10 s'), ('k1', 'flink', 'consume'), ('flink', 'k2', 'emit top-K'), ('k2', 'redis', 'ZINCRBY'), ('k2', 'roll', ''),
         ('roll', 'olap', 'hourly top-K'), ('redis', 'api', 'ZREVRANGE'), ('olap', 'api', 'read 24 rows'), ('api', 'ui', '')],
 steps=[
  ('Local pre-aggregation', 'In-process hash map (or Count-Min Sketch + min-heap) inside each app server',
   'Every request does map[item]++. Every 10 s the server sends its counts — only the items it saw, or its local top 10×K — and resets.',
   'Turns millions of events into thousands of messages. Without it, Kafka carries one message per request.'),
  ('Ingest buffer', 'Kafka topic local-counts, partitioned by hash(item)',
   'Each message is (item, count, server, time). Same item → same partition → same Flink worker.',
   'Partitioning by item means one worker owns all counts of an item — no cross-worker merge.'),
  ('Stateful aggregation', 'Flink job: keyBy(item) → 1-minute tumbling event-time window → sum',
   'Flink keeps per-item counts in keyed state (RocksDB). Watermarks close a window when late data is unlikely; allowed lateness ~30 s.',
   'Flink gives windows, state, checkpoints and exactly-once with Kafka. Alternatives: Kafka Streams (simpler, in-app), Spark Structured Streaming (micro-batch).'),
  ('Per-window top-K', 'Flink ProcessWindowFunction with a size-K min-heap per partition, then a global merge task',
   'Each parallel task emits its local top-K for the minute; one downstream task merges them into the final minute top-K.',
   'Two-level top-K keeps the final merge tiny.'),
  ('Fault tolerance', 'Flink checkpoints to S3/HDFS every ~30 s; Kafka offsets stored in the checkpoint',
   'If a worker dies, the job restarts from the last checkpoint and replays Kafka from the saved offsets — counts are neither lost nor doubled.',
   'This is why a stateful stream processor beats hand-written consumers here.'),
  ('Serving short windows', 'Redis sorted sets: key topk:min:<minute>, ZINCRBY item count; TTL 25 h',
   '5-minute answer = ZUNIONSTORE of the last 5 minute-sets, then ZREVRANGE 0 K-1.',
   'Sorted sets give ranked reads in O(log n). Small and fast.'),
  ('Long windows', 'Hourly rollup job writes each hour\'s top 10×K to Cassandra/Pinot (key: hour)',
   '24-hour answer = merge 24 hourly lists in the API. Never merge 1,440 minute sets per request.',
   'Rollups keep long-window queries cheap. Exact counts, if required, come from a second pass over candidates.'),
  ('Query API', 'Stateless service + a small result cache (refresh every 10 s)',
   'Picks the source by window: Redis for ≤ 1 h, hourly store for 24 h. Returns items with counts.',
   'No coordination service anywhere — nothing here needs leader election or locks.')])

D['metrics'] = dict(
 rows=[[('agent', 'Agent', 'Telegraf / OTel collector'), ('gw', 'Ingest gateway', 'per DC, stateless'), ('kafka', 'Kafka', 'metrics topic, by series')],
       [('tsdb', 'TSDB writers', 'M3 / VictoriaMetrics / Cassandra'), ('flink', 'Flink rollups', '1-min, 1-hour'), ('alert', 'Alert evaluator', 'rules on the stream')],
       [('query', 'Query service', 'PromQL-style'), ('graf', 'Grafana', 'dashboards'), ('pager', 'Notifier', 'email / PagerDuty')]],
 arrows=[('agent', 'gw', 'batch, gzip, every 10 s'), ('gw', 'kafka', 'produce'), ('kafka', 'tsdb', 'consume'), ('kafka', 'flink', 'consume'), ('kafka', 'alert', 'consume'),
         ('flink', 'tsdb', 'rollup series'), ('tsdb', 'query', 'range scan'), ('query', 'graf', ''), ('alert', 'pager', 'fire / resolve')],
 steps=[
  ('Collection agent', 'Telegraf or OpenTelemetry collector on every host',
   'Scrapes local stats, adds labels (host, cluster, DC), batches 10 s of points, compresses, sends. Buffers to local disk if the gateway is down.',
   'Agent-side batching is the biggest win for write volume.'),
  ('Ingest gateway', 'Stateless HTTP/gRPC service per data centre behind a load balancer',
   'Validates, rejects high-cardinality labels, produces to Kafka with key = series_id (hash of metric + labels).',
   'Keying by series keeps one series in order on one partition.'),
  ('Buffer', 'Kafka topic metrics, ~hundreds of partitions, 24 h retention',
   'Absorbs spikes and lets three independent consumers read: storage, rollups, alerting.',
   'Decouples writers from slow storage; replay after a storage outage.'),
  ('Storage', 'Time-series DB: M3, VictoriaMetrics, or Cassandra with (series_id, time_block) partitions',
   'Writes points into 2-hour blocks per series with delta-of-delta timestamps and XOR-compressed values (Gorilla encoding), ~1.4 bytes per point.',
   'A purpose-built TSDB beats a generic DB 10× on space and range-scan speed.'),
  ('Rollups', 'Flink job: keyBy(series) → 1-min and 1-hour tumbling windows → avg / max / min / count',
   'Writes rollup series back to the TSDB; raw data expires after 14 days.',
   'Long-range graphs read rollups, not raw points.'),
  ('Alerting', 'Alert evaluator (Flink job or Prometheus-style ruler) reading the stream',
   'Keeps per-rule, per-series state: "value > 70% for 5 min" fires only after 5 minutes of consecutive breaches. A missing-data timer fires "no data" alerts.',
   'Evaluating on the stream avoids polling the TSDB and keeps alerts fast.'),
  ('Notification', 'Alertmanager-style router → email, Slack, PagerDuty',
   'Groups alerts by service, dedupes repeats, applies silences during maintenance.',
   'Grouping prevents an incident from sending 500 pages.'),
  ('Query', 'Query service with a PromQL-like language; Grafana for dashboards',
   'Chooses resolution from the range (raw < 2 days, 1-min < 90 days, else 1-hour), fans out to TSDB shards, merges.',
   'Picking resolution by range keeps every graph fast.')])

D['kvstore'] = dict(
 rows=[[('client', 'Client library', 'partition map cached'), ('coord', 'Metadata store', 'ZooKeeper / etcd'), ('leader', 'Partition leader', 'storage node')],
       [('wal', 'Active data file', 'append-only + checksum'), ('idx', 'In-memory index', 'key → file, offset'), ('follow', 'Followers ×2', 'replicate the log')],
       [('compact', 'Compaction thread', 'rewrite live keys'), ('hint', 'Hint files', 'fast restart')]],
 arrows=[('client', 'coord', 'which node owns key?'), ('client', 'leader', 'put / get'), ('leader', 'wal', 'append'), ('leader', 'idx', 'update offset'),
         ('leader', 'follow', 'replicate'), ('wal', 'compact', 'old files'), ('compact', 'hint', 'write')],
 steps=[
  ('Routing', 'Client library with a cached partition map; consistent hashing with virtual nodes',
   'hash(key) → partition → leader node. The map is refreshed from the metadata store when a node replies "not mine".',
   'No extra hop through a proxy. Virtual nodes make adding a node move little data.'),
  ('Cluster metadata', 'ZooKeeper or etcd (Raft)',
   'Stores which node leads which partition and the in-sync followers; runs leader election when a node dies.',
   'Here a coordination service IS justified: exactly one leader per partition.'),
  ('Write path', 'Append (key, value_len, value, CRC32) to the active data file; fsync per batch',
   'Then update the in-memory hash map key → (file_id, offset, size). Acknowledge after the followers have the record (sync replication).',
   'Sequential appends are the fastest disk write; batching fsyncs keeps throughput high.'),
  ('Read path', 'Hash map lookup, then pread(file, offset, size)',
   'Exactly one disk read per get; the OS page cache makes hot values free.',
   'Keys fit in memory, values do not — the Bitcask trade.'),
  ('Replication', 'Leader ships each appended record to 2 followers; quorum or all-sync ack',
   'On leader death, the metadata store promotes the most up-to-date follower.',
   'Leader-per-partition = simple strong consistency. Alternative: leaderless quorum (Dynamo) for higher write availability.'),
  ('Deletes and compaction', 'Tombstone records; background compaction thread with an I/O budget',
   'Compaction copies only the latest value of live keys into new files, writes a hint file, swaps the index atomically, deletes old files.',
   'Reclaims disk without blocking reads.'),
  ('Crash recovery', 'Hint files (key → offset) per data file',
   'On restart, load hint files instead of scanning all data; a bad CRC on the last record means it was torn — ignore it.',
   'Restart in seconds instead of minutes.')])

D['typeahead'] = dict(
 rows=[[('client', 'Browser / app', 'debounce 50 ms'), ('edge', 'CDN / edge cache', 'top prefixes'), ('svc', 'Typeahead service', 'stateless, merges')],
       [('trie', 'Prefix shards', 'in-memory top-K per prefix'), ('pers', 'Personal cache', 'Redis: member → connections'), ('fresh', 'Fresh index', 'last hours')],
       [('spark', 'Spark daily build', 'scores + top-K'), ('kafka', 'Kafka', 'new profiles / companies'), ('s3', 'Index files', 'S3 snapshot')]],
 arrows=[('client', 'edge', 'GET ?q=ry'), ('edge', 'svc', 'miss'), ('svc', 'trie', 'prefix lookup'), ('svc', 'pers', 'my network'), ('svc', 'fresh', ''),
         ('spark', 's3', 'write'), ('s3', 'trie', 'load on deploy'), ('kafka', 'fresh', 'stream')],
 steps=[
  ('Client', 'Debounce ~50 ms, cancel stale requests, cache recent prefixes in the browser',
   'Typing "ryan" sends maybe two requests, not four.',
   'Cuts load 2–3× before any server is touched.'),
  ('Edge cache', 'CDN or edge cache for anonymous / popular short prefixes, TTL ~minutes',
   'Prefixes like "a", "li" are the hottest and identical for many users.',
   'Absorbs the hottest traffic close to the user.'),
  ('Offline build', 'Daily Spark job over members, companies, schools',
   'Scores each entity (popularity, profile quality), generates every prefix up to ~10 chars, keeps the top 20 per prefix, writes sorted shard files to S3.',
   'All ranking work happens offline; query time is a lookup.'),
  ('Serving index', 'In-memory map prefix → top-K list, sharded by prefix range, 3 replicas',
   'Nodes load the latest snapshot from S3 at deploy; a lookup is a hash-map read.',
   'Microseconds per lookup; hot short-prefix shards get extra replicas.'),
  ('Personalisation', 'Redis: member_id → connection names (1st and 2nd degree), loaded at session start',
   'The service prefix-matches the small personal list and merges it above global results.',
   'No per-user trie. Personal results first is what makes it feel like LinkedIn.'),
  ('Freshness', 'Kafka stream of new profiles / companies → small "recent" index updated in near real time',
   'Merged into results until the next daily build absorbs them.',
   'New company pages appear in minutes, not a day.'),
  ('Merge and rank', 'Typeahead service',
   'Calls prefix shard + personal + fresh in parallel with a 30 ms budget, merges, applies privacy filters, returns top 10.',
   'Time-box every call; drop the slow source rather than block typing.')])

D['denylist'] = dict(
 rows=[[('lb', 'Edge / API gateway', 'Envoy filter'), ('svc', 'Web servers', ''), ('tap', 'Request tap', 'sampled copy → Kafka')],
       [('flink', 'Detector job', 'Flink + isMalicious()'), ('db', 'Denylist service', 'MySQL, versioned'), ('kafka', 'Kafka', 'denylist-changes, compacted')],
       [('agent', 'Sidecar agent', 'snapshot + deltas'), ('mem', 'In-memory set', 'IP trie / Bloom')]],
 arrows=[('lb', 'svc', 'allowed requests'), ('lb', 'tap', 'sample'), ('tap', 'flink', 'consume'), ('flink', 'db', 'add IP + TTL'), ('db', 'kafka', 'outbox → delta'),
         ('kafka', 'agent', 'consume'), ('agent', 'mem', 'apply'), ('mem', 'lb', 'lookup per request')],
 steps=[
  ('Enforcement point', 'Edge gateway (e.g. an Envoy filter) on every edge host',
   'Every request: look up the client IP in the local in-memory structure; deny with 403 if present.',
   'Stops bad traffic before it reaches any service. Microseconds, no network call.'),
  ('Lookup structure', 'Prefix trie for CIDR ranges (+ optional Bloom filter in front)',
   'Longest-prefix match covers single IPs and whole subnets; a few million entries fit in ~100 MB.',
   'Ranges matter for IPv6 and for blocking bad subnets.'),
  ('Detection', 'Flink job reading a sampled request stream from Kafka; calls isMalicious()',
   'Expensive classification runs off the request path; offenders are written to the denylist service with reason and TTL.',
   'Never put the expensive check inline.'),
  ('Source of truth', 'Denylist service on MySQL; every change gets a monotonically increasing version',
   'Writes use a transactional outbox: the change row and an outbox row commit together; a relay publishes the outbox to Kafka.',
   'The outbox guarantees the DB and the stream never disagree.'),
  ('Distribution', 'Kafka topic denylist-changes (log-compacted, key = IP prefix)',
   'Agents consume deltas in seconds; compaction keeps the topic small enough to rebuild state from it.',
   'Push gives seconds of propagation without 10,000 servers polling.'),
  ('Agent', 'Sidecar on each edge host',
   'On start: load the latest snapshot (S3, with its version), then consume deltas after that version. Exposes its current version as a metric.',
   'Version gap or stale version → reload snapshot and alert. Servers self-heal.'),
  ('Expiry and appeals', 'TTL per entry; allow-list overrides; an admin path to remove entries',
   'Expired entries are removed by a periodic job that emits "remove" deltas.',
   'IPs get reused; mistakes must expire on their own.')])

D['mq'] = dict(
 rows=[[('prod', 'Producer client', 'batching, idempotent'), ('broker', 'Broker (leader)', 'partition log on disk'), ('f1', 'Follower brokers', 'ISR replicas')],
       [('ctrl', 'Controller', 'KRaft / Raft quorum'), ('seg', 'Log segments', '1 GB files + index'), ('cg', 'Consumer group', 'coordinator + offsets')]],
 arrows=[('prod', 'broker', 'produce (acks=all)'), ('broker', 'f1', 'fetch / replicate'), ('ctrl', 'broker', 'leadership'), ('broker', 'seg', 'append'), ('broker', 'cg', 'fetch from offset')],
 steps=[
  ('Producer', 'Client library with batching (linger ~5 ms), compression, idempotence (producer id + sequence)',
   'hash(key) % partitions picks the partition, so one key stays ordered. Idempotence stops duplicates on retry.',
   'Batching is how one broker takes hundreds of MB/s.'),
  ('Partition log', 'Append-only segment files (~1 GB) with a sparse offset index and time index',
   'Writes go to the OS page cache and are flushed in batches; reads use zero-copy sendfile to the socket.',
   'Sequential I/O + page cache = the core of the throughput.'),
  ('Replication', 'Leader + followers; in-sync replica set (ISR); acks=all with min.insync.replicas=2',
   'A message is committed when all in-sync replicas have it; consumers only see committed messages.',
   'No loss if the leader dies after acknowledging.'),
  ('Controller', 'KRaft (Raft-based metadata quorum; older versions use ZooKeeper)',
   'Tracks partition leaders; on broker death, elects a new leader from the ISR and tells clients.',
   'A consensus quorum is needed here: exactly one leader per partition.'),
  ('Consumer groups', 'Group coordinator assigns partitions; offsets stored in the internal __consumer_offsets topic',
   'Each partition is read by one consumer in the group; the consumer commits its offset after processing.',
   'At-least-once by default; idempotent consumers make duplicates harmless.'),
  ('Retention', 'Delete old segments by time/size, or log compaction (keep latest per key)',
   'Old segments are deleted as whole files — cheap.',
   'Replay is possible within retention; compaction turns a topic into a changelog.')])

D['notify'] = dict(
 rows=[[('svc', 'Product services', 'emit events'), ('k1', 'Kafka', 'notification-requests'), ('engine', 'Notification engine', 'Kafka consumers')],
       [('pref', 'Preference service', 'MySQL + cache'), ('lim', 'Limits', 'Redis user:category:day'), ('tmpl', 'Templates', 'i18n')],
       [('q', 'Channel topics', 'push-high, push-low, email…'), ('w', 'Channel workers', 'APNs / FCM / SES'), ('inbox', 'In-app inbox', 'Cassandra by user')]],
 arrows=[('svc', 'k1', 'event'), ('k1', 'engine', 'consume'), ('engine', 'pref', 'allowed?'), ('engine', 'lim', 'INCR, check'), ('engine', 'tmpl', 'render'),
         ('engine', 'q', 'enqueue by priority'), ('q', 'w', 'consume'), ('engine', 'inbox', 'write')],
 steps=[
  ('Intake', 'Kafka topic notification-requests, keyed by user_id',
   'Services publish "X happened for user U"; nothing calls a provider directly.',
   'Keying by user keeps one user\'s notifications ordered and dedupable.'),
  ('Decision', 'Notification engine (Kafka consumer group)',
   'For each event: resolve recipients, check preferences, check category limits, dedupe by idempotency key, pick channels, maybe hold for a digest.',
   'All business rules in one place; channels stay dumb.'),
  ('Preferences', 'Preference service on MySQL with a read-through cache',
   'Per user, per category, per channel: allowed or not; quiet hours; time zone.',
   'Read on every notification, so it must be cached.'),
  ('Category limits', 'Redis INCR on user:category:yyyymmdd with expiry; Lua for check-and-increment',
   'Over the limit (e.g. 5 marketing/day) → drop or fold into a digest. Security and transactional categories are never limited.',
   'Atomic and cheap; no reset job.'),
  ('Priority queues', 'Separate Kafka topics per channel and priority (push-high, push-low, email-bulk…)',
   'Security codes go to high-priority topics with their own workers.',
   'A marketing burst can never delay an OTP.'),
  ('Delivery', 'Channel workers calling APNs, FCM, an email provider (e.g. SES), SMS gateway',
   'Retry with exponential backoff; circuit breaker per provider; record delivery status; check the idempotency key before sending.',
   'Retries are normal, duplicates are not acceptable.'),
  ('In-app inbox', 'Cassandra table partitioned by user_id, clustered by time desc',
   'The bell icon reads the latest N rows for a user.',
   'One partition read per user.')])

D['scheduler'] = dict(
 rows=[[('api', 'Job API', 'create / cancel'), ('db', 'Job DB', 'MySQL / Postgres'), ('sched', 'Scheduler workers', 'poll due runs')],
       [('mapi', 'Machine API', 'given'), ('agent', 'Worker agent', 'runs job, heartbeats'), ('kafka', 'Kafka', 'run-events')],
       [('mon', 'Monitor', 'expired leases / timeouts'), ('alert', 'Alerting', 'notification system'), ('logs', 'Logs', 'object storage')]],
 arrows=[('api', 'db', 'insert job + next run'), ('sched', 'db', 'claim with lease'), ('sched', 'mapi', 'get machine'), ('sched', 'agent', 'dispatch'),
         ('agent', 'kafka', 'heartbeat / result'), ('kafka', 'mon', 'consume'), ('mon', 'db', 'retry / fail'), ('mon', 'alert', 'failed / late'), ('agent', 'logs', 'upload')],
 steps=[
  ('Job definitions', 'Job API + relational DB (jobs, runs tables)',
   'Creating a job computes next_run_at from its cron expression and inserts a run row in state SCHEDULED.',
   'A relational DB gives transactions for the claim step.'),
  ('Finding due runs', 'Index on (state, next_run_at); runs partitioned into N buckets by hash(job_id)',
   'Each scheduler worker owns some buckets and polls "SELECT … WHERE state=SCHEDULED AND next_run_at <= now LIMIT 100".',
   'Buckets spread the top-of-hour spike across workers.'),
  ('Claiming', 'Atomic UPDATE … SET state=CLAIMED, owner=me, lease_until=now+60s WHERE id=? AND state=SCHEDULED',
   'Only one worker\'s update succeeds (rows affected = 1). Alternatively SELECT … FOR UPDATE SKIP LOCKED.',
   'No coordination service needed: the database row is the lock.'),
  ('Getting a machine', 'The given machine API',
   'Request machine(s) matching the job\'s needs; if none, set state WAITING_CAPACITY and retry with backoff.',
   'Capacity shortage is a normal state, not an error.'),
  ('Running', 'Worker agent on the machine',
   'Starts the job (container/process), heartbeats every 10 s to Kafka run-events, uploads logs to object storage, reports SUCCEEDED/FAILED.',
   'Heartbeats are how we know a machine died.'),
  ('Monitoring', 'Monitor service consuming run-events + a sweep for expired leases',
   'No heartbeat for 3 intervals or past timeout → mark LOST/TIMED_OUT; schedule a retry (new run row, attempt+1) if retries remain.',
   'At-least-once execution — so jobs must be idempotent.'),
  ('Alerts', 'Rules: failed after all retries, timed out, started > N minutes late → notification system',
   'Alert includes job, attempt, machine, last log lines.',
   'Actionable alerts, sent once per incident.')])

D['ratelimit'] = dict(
 rows=[[('client', 'Client', ''), ('gw', 'Gateway filter', 'Envoy / Nginx plugin'), ('svc', 'Backend', '')],
       [('local', 'Local bucket', 'in-process, per key'), ('redis', 'Redis Cluster', 'Lua token bucket'), ('cfg', 'Rules service', 'pushed config')]],
 arrows=[('client', 'gw', 'request'), ('gw', 'local', 'cheap pre-check'), ('gw', 'redis', 'EVALSHA (key)'), ('gw', 'svc', 'allowed'), ('cfg', 'gw', 'limits')],
 steps=[
  ('Where it runs', 'API gateway filter (Envoy rate-limit filter, Nginx/OpenResty plugin)',
   'Builds the key (api_key, user, IP, endpoint) and calls allow(key, cost).',
   'One place for all services; backends stay simple.'),
  ('Algorithm', 'Token bucket: tokens, last_refill; refill = rate × elapsed, cap = burst',
   'allow = tokens ≥ cost; then tokens -= cost.',
   'Controlled bursts and tiny state. Sliding-window counter is the alternative for smoother limits.'),
  ('Shared state', 'Redis Cluster; one Lua script does read-refill-check-decrement atomically',
   'EVALSHA with key = the bucket key; returns allowed + retry-after. Key gets a TTL so idle buckets disappear.',
   'Atomic in one round trip — no race between two gateways.'),
  ('Latency option', 'Local in-process buckets holding a share of the limit, synced every ~1 s',
   'Most decisions are local; only the sync touches Redis.',
   'Trade a small overshoot for sub-millisecond checks.'),
  ('Rules', 'Rules service; config pushed to gateways (watch/poll)',
   'Limits per plan, endpoint and key type; cached in memory.',
   'Changing a limit needs no deploy.'),
  ('Failure policy', 'Per-route setting: fail-open or fail-closed',
   'Redis timeout (e.g. 5 ms) → normal APIs allow, expensive or security-sensitive APIs deny.',
   'Say this out loud — it is what Staff interviewers listen for.')])

D['logging'] = dict(
 rows=[[('app', 'Service', 'JSON logs to file'), ('agent', 'Fluent Bit', 'tail, batch, disk buffer'), ('kafka', 'Kafka', 'logs.<service>')],
       [('proc', 'Flink / Logstash', 'parse, enrich, sample'), ('es', 'Elasticsearch / OpenSearch', 'hot 7 days'), ('s3', 'S3 Parquet', 'cold, 1 year')],
       [('kibana', 'Kibana', 'search'), ('trino', 'Trino / Spark SQL', 'analytics'), ('alert', 'Log alerts', 'error-rate rules')]],
 arrows=[('app', 'agent', 'tail'), ('agent', 'kafka', 'produce'), ('kafka', 'proc', 'consume'), ('proc', 'es', 'bulk index'), ('proc', 's3', 'hourly files'),
         ('es', 'kibana', ''), ('s3', 'trino', ''), ('proc', 'alert', 'counts')],
 steps=[
  ('Emit', 'Services write structured JSON (time, service, level, trace_id, message) to stdout/file',
   'No network call from the service; logging never blocks the request.',
   'Structured logs make both search and SQL easy.'),
  ('Ship', 'Fluent Bit (or Vector) agent on each host',
   'Tails files, batches, compresses, sends to Kafka; buffers to disk if Kafka is slow.',
   'The disk buffer is what protects the service during outages.'),
  ('Buffer', 'Kafka, one topic per service group, partitioned by service',
   'Absorbs spikes; several consumers (index, archive, alerts) read independently.',
   'Decouples producers from the index cluster.'),
  ('Process', 'Flink or Logstash consumers',
   'Parse, add fields (cluster, version), drop noise, sample DEBUG under load, mask secrets.',
   'Cost control happens here.'),
  ('Hot search', 'Elasticsearch/OpenSearch, one index per day per service, 7-day retention',
   'Kibana searches by text, trace_id, level. Old indexes are dropped whole.',
   'Daily indexes make retention a cheap delete.'),
  ('Cold analytics', 'Hourly Parquet files in S3, partitioned by date/service; Trino or Spark SQL',
   'Analysts query months of logs cheaply; compression ~10×.',
   'Columnar files cost a fraction of an index.'),
  ('Alerting', 'Stream job counting error patterns per service per minute',
   'Spike in ERROR rate → alert through the notification system.',
   'Logs become signals, not just storage.')])

D['feed'] = dict(
 rows=[[('post', 'Post service', 'write post'), ('k', 'Kafka', 'post-created'), ('fan', 'Fan-out workers', 'skip big authors')],
       [('redis', 'Feed cache', 'Redis list per member'), ('feed', 'Feed service', 'gather candidates'), ('rank', 'Ranker', 'model on features')],
       [('store', 'Post store', 'Espresso / Cassandra'), ('graph', 'Follow graph', 'who I follow'), ('fs', 'Feature store', 'engagement signals')]],
 arrows=[('post', 'k', 'event'), ('k', 'fan', 'consume'), ('fan', 'graph', 'followers'), ('fan', 'redis', 'LPUSH post_id'), ('feed', 'redis', 'read ids'),
         ('feed', 'store', 'hydrate posts'), ('feed', 'rank', 'score'), ('rank', 'fs', 'features'), ('post', 'store', 'write')],
 steps=[
  ('Write a post', 'Post service → post store (sharded by post_id) + event post-created on Kafka', 'The write commits first; fan-out is asynchronous.', 'Posting stays fast.'),
  ('Fan-out', 'Workers consume post-created; read followers from the graph service', 'For authors under ~10K followers: LPUSH post_id onto each follower\'s Redis list (capped at ~1,000). Big authors are skipped.', 'Push for normal authors, pull for big ones.'),
  ('Read candidates', 'Feed service', 'Reads the member\'s Redis list + recent posts of followed big authors + other sources (connection activity, jobs).', '~500 candidates in a few ms.'),
  ('Hydrate', 'Batch get from the post store and a post cache', 'Fetch post bodies, counts, author info for candidates.', 'Batching avoids 500 round trips.'),
  ('Rank', 'Ranking service: light model first, heavy model on top ~100, features from a feature store', 'Scores likelihood of meaningful engagement; applies diversity rules.', 'Two-stage ranking keeps latency in budget.'),
  ('Paginate', 'Cursor = (last score, last post_id); seen-set per session', 'Next page continues without duplicates.', 'Stable pagination as the feed changes.')])

D['calendar'] = dict(
 rows=[[('client', 'Client', ''), ('api', 'Calendar API', 'create, RSVP, list'), ('db', 'Events DB', 'Postgres, sharded by event')],
       [('outbox', 'Outbox → Kafka', 'event-changed'), ('idx', 'Per-user index', 'Cassandra (user, day)'), ('sched', 'Reminder scheduler', 'minute buckets in Redis')],
       [('notif', 'Notifications', 'email / push'), ('fb', 'Free/busy service', 'merge intervals')]],
 arrows=[('client', 'api', ''), ('api', 'db', 'txn: event + attendees + outbox'), ('db', 'outbox', 'relay'), ('outbox', 'idx', 'fan out to attendees'), ('outbox', 'sched', 'reminders'),
         ('sched', 'notif', 'due'), ('api', 'idx', 'list my week'), ('fb', 'idx', 'busy blocks')],
 steps=[
  ('Create', 'Calendar API → Postgres transaction: event row (UTC + time zone + RRULE), attendee rows, outbox row', 'All or nothing.', 'The outbox makes downstream updates reliable.'),
  ('Fan out', 'Outbox relay → Kafka → index writer', 'Writes (user_id, day) → event rows for each attendee in Cassandra.', 'Async fan-out handles 10K-person all-hands.'),
  ('Read my week', 'Per-user index range query + expand recurrences for the range', 'Recurring events are expanded from the RRULE; exceptions override single dates.', 'One partition read per user per day range.'),
  ('RSVP', 'Update one attendee row; event-changed to update other attendees\' views', 'Organiser sees counts change.', 'Small writes.'),
  ('Reminders', 'Redis sorted set or minute buckets keyed by fire time; scheduler polls every minute', 'Due reminders → notification system; idempotent per (event, user, offset).', 'No scan over all events.'),
  ('Free/busy', 'Service reading busy intervals from the index', 'Merges intervals for N people and finds gaps; respects privacy (busy only, no titles).', 'Scheduling assistant without exposing details.')])

D['cache'] = dict(
 rows=[[('app', 'App + client lib', 'consistent hash ring'), ('node', 'Cache node', 'shards of the keyspace'), ('rep', 'Replica', 'async copy')],
       [('core', 'Cache core', 'map + byte counter'), ('pol', 'Policy plug-in', 'LRU list / priority heap'), ('ttl', 'TTL sweeper', 'sampled expiry')],
       [('db', 'Database', 'source of truth'), ('local', 'Near cache', 'hot keys on clients')]],
 arrows=[('app', 'node', 'GET / SET'), ('node', 'rep', 'replicate'), ('node', 'core', ''), ('core', 'pol', 'onAccess / pickVictim'), ('core', 'ttl', ''),
         ('app', 'db', 'on miss'), ('app', 'local', 'hot keys')],
 steps=[
  ('Single-node core', 'Hash map key → entry {value, size, priority, expires_at}; a used_bytes counter', 'Put: while used + size > capacity, evict policy.pickVictim(). Then insert and call policy.onInsert.', 'Capacity in bytes, as the question says.'),
  ('Policy interface', 'IEvictionPolicy: onInsert, onAccess, onRemove, pickVictim', 'LRU = doubly linked list; Lowest priority = min-heap by (priority, insert seq); LFU = frequency buckets.', 'Adding a policy never changes the core.'),
  ('Concurrency', 'Segmented locks (N shards, each with its own map, lock and policy)', 'Approximate global LRU in exchange for parallelism.', 'Redis avoids locks entirely with one thread per instance.'),
  ('Distribution', 'Client-side consistent hashing with virtual nodes (or Redis Cluster\'s 16,384 slots)', 'Key → node; adding a node moves ~1/N of keys.', 'No central proxy needed.'),
  ('Replication', 'Primary-replica per shard, async', 'Replica promoted on failure; a few writes may be lost — acceptable for a cache.', 'Availability over perfect durability.'),
  ('Hot keys', 'Near cache on clients for hot reads; key splitting (key#1..key#8) or local write batching for hot writes', 'Spreads one key\'s load over several nodes.', 'The write-heavy hot key was the reported deep dive.'),
  ('Miss storms', 'Request coalescing (single-flight) + jittered TTLs', 'One DB read per key on a miss, not thousands.', 'Protects the database after a node failure.')])

D['coderpad'] = dict(
 rows=[[('br', 'Browser editor', 'Monaco, sends ops'), ('ws', 'WebSocket gateway', 'sticky by pad_id'), ('sess', 'Session node', 'in-memory doc, seq')],
       [('kafka', 'Kafka', 'pad-events by pad_id'), ('cas', 'Event store', 'Cassandra (pad_id, seq)'), ('snap', 'Snapshots', 'S3 every 500 ops')],
       [('replay', 'Replay service', 'snapshot + events'), ('mail', 'Invite service', 'signed link + email')]],
 arrows=[('br', 'ws', 'op'), ('ws', 'sess', 'route by pad'), ('sess', 'kafka', 'append (seq)'), ('sess', 'br', 'broadcast'), ('kafka', 'cas', 'persist'),
         ('cas', 'snap', 'compact'), ('replay', 'snap', 'load'), ('replay', 'cas', 'events after')],
 steps=[
  ('Client', 'Monaco editor emits small operations (insert/delete at position) and drawing strokes (batched every 50 ms)', 'Each op carries the client\'s last seen seq.', 'Small ops, not whole files.'),
  ('Routing', 'WebSocket gateway with consistent hashing on pad_id', 'All participants of a pad land on one session node.', 'One place orders the pad\'s events.'),
  ('Ordering', 'Session node assigns seq numbers and appends to Kafka (key = pad_id) before broadcasting', 'Write-then-broadcast means nothing visible is ever lost.', 'Single writer → no OT needed; add OT/CRDT if the interviewer can edit.'),
  ('Persistence', 'Kafka → Cassandra table (pad_id, seq) clustered by seq', 'Range read gives any part of the history in order.', 'One partition per pad.'),
  ('Snapshots', 'Every ~500 ops, store the full document + strokes to S3 with its seq', 'Late joiners and replay seeks start from the nearest snapshot.', 'Join time stays constant however long the pad.'),
  ('Replay', 'Replay service streams snapshot + events with original timing to a replay viewer', 'Seek = nearest snapshot before t, then apply events.', 'No real video recording needed.'),
  ('Invites', 'Signed, expiring pad links; email via the notification system', 'Join checks the token and the invited email.', 'Unguessable and revocable.')])

D['lynda'] = dict(
 rows=[[('s3', 'PDF bucket', 'S3'), ('tika', 'Extraction jobs', 'Apache Tika on Spark'), ('es', 'Elasticsearch / Lucene', 'inverted index')],
       [('api', 'Search API', 'boolean parser'), ('ui', 'Lynda search UI', ''), ('mon', 'Failed docs', 'retry queue')]],
 arrows=[('s3', 'tika', 'read PDFs'), ('tika', 'es', 'bulk index text'), ('tika', 'mon', 'parse errors'), ('ui', 'api', 'red AND green NOT blue'), ('api', 'es', 'bool query')],
 steps=[
  ('Extraction', 'Spark job running Apache Tika (or pdfbox) over the S3 bucket', 'Text per page, title, metadata; failures go to a retry queue.', 'The hardest practical step in a one-month v0.'),
  ('Indexing', 'Elasticsearch / Lucene, bulk API', 'Analyzer lowercases and tokenises; builds posting lists word → sorted doc ids.', 'Months of work for free.'),
  ('Query', 'Search API turns "red AND green NOT blue" into a bool query: must[red, green], must_not[blue]', 'Lucene intersects posting lists (shortest first) using skip lists, then removes blue\'s ids.', 'Exactly the posting-list merge you explain on the whiteboard.'),
  ('Scale later', 'More shards (by document) and replicas; positions for phrases; BM25 ranking', 'Scatter-gather across shards.', 'Clear v1 path.')])

D['jobrec'] = dict(
 rows=[[('ui', '/jobs page', ''), ('reco', 'Reco service', 'orchestrates'), ('cache', 'Precomputed recs', 'Venice / Redis by member')],
       [('ann', 'ANN index', 'FAISS / vector store'), ('search', 'Job search index', 'title / skill match'), ('filter', 'Qualification filter', 'rules')],
       [('rank', 'Ranker', 'GBDT / two-tower'), ('fs', 'Feature store', 'online + offline'), ('stream', 'Kafka → Flink', 'real-time interest')]],
 arrows=[('ui', 'reco', ''), ('reco', 'cache', 'precomputed?'), ('reco', 'ann', 'member embedding'), ('reco', 'search', 'skills'), ('reco', 'filter', 'candidates'),
         ('filter', 'rank', 'qualified'), ('rank', 'fs', 'features'), ('stream', 'fs', 'update')],
 steps=[
  ('Precompute', 'Nightly Spark job → top 50 per active member into a key-value store (e.g. Venice / Redis)', 'The page usually starts from this list.', 'Fast first paint.'),
  ('Retrieval', 'ANN search on member and job embeddings (FAISS / a vector store) + keyword search on skills/titles', 'Returns ~500 candidates.', 'High recall, cheap.'),
  ('Qualification filter', 'Rule engine: seniority gap, required skills, location/remote, visa', 'Hard removal before ranking.', 'Explainable, safe — never left to the model.'),
  ('Ranking', 'Model (GBDT or a small neural net) scoring P(apply) × P(recruiter reply)', 'Features from the feature store; top 3 returned.', 'Two-sided objective.'),
  ('Real-time interest', 'Kafka events (page views, likes) → Flink → online feature store', 'Short-term interest features update within seconds.', 'Phase 2, as the question allows.'),
  ('Feedback', 'Impressions, clicks, applies logged to Kafka → training data', 'Retrain daily; A/B test models.', 'Closes the loop.')])

D['photos'] = dict(
 rows=[[('app', 'Mobile / web', 'multipart upload'), ('up', 'Upload API', 'pre-signed URLs'), ('s3', 'S3 originals', 'multi-region')],
       [('ev', 'S3 event → SQS/Kafka', 'upload complete'), ('w', 'Image workers', 'libvips, autoscaled'), ('meta', 'Metadata DB', 'by owner_id')],
       [('es', 'Search index', 'tags, captions'), ('cdn', 'CDN', 'signed URLs')]],
 arrows=[('app', 'up', 'start upload'), ('app', 's3', 'PUT parts'), ('s3', 'ev', 'notify'), ('ev', 'w', 'consume'), ('w', 's3', 'write sizes'), ('w', 'meta', 'status=ready'),
         ('meta', 'es', 'index'), ('s3', 'cdn', 'origin')],
 steps=[
  ('Upload', 'Upload API returns pre-signed multipart URLs; the client PUTs parts directly to S3', 'Resumable; the progress bar comes from parts sent.', 'API servers never carry file bytes.'),
  ('Trigger', 'S3 event notification → SQS or Kafka "upload-complete"', 'Includes object key and owner.', 'Processing is async and retryable.'),
  ('Processing', 'Worker pool using libvips (fast resize), autoscaled on queue depth; thumbnail queue has priority', 'Thumbnail first (~2 s goal), then other sizes, EXIF strip, moderation scan.', 'Thumbnail-first meets the 2-second target.'),
  ('Metadata', 'MySQL/Espresso table photos sharded by owner_id', 'Status uploading → processing → ready; sizes; tags.', '"My photos" is one shard.'),
  ('Search / catalogue', 'Elasticsearch on tags, captions, dates', 'Updated from metadata changes.', 'Catalogue and search requirement.'),
  ('Delivery', 'CDN in front of S3 with signed URLs for private photos', 'Cache-Control long; purge on delete.', 'Reads are ~100× writes.')])

D['logistics'] = dict(
 rows=[[('dev', 'Scanners / driver app', 'offline queue'), ('ing', 'Ingest API', 'idempotent by scan_id'), ('kafka', 'Kafka', 'scan-events by package')],
       [('sm', 'Package state service', 'state machine'), ('db', 'Package DB', 'by package_id'), ('route', 'Routing service', 'Dijkstra on hub graph')],
       [('track', 'Tracking API', 'cache'), ('notify', 'Notifications', 'status changes')]],
 arrows=[('dev', 'ing', 'sync scans'), ('ing', 'kafka', 'produce'), ('kafka', 'sm', 'consume in order'), ('sm', 'db', 'conditional update'), ('sm', 'route', 'next hop'),
         ('db', 'track', ''), ('sm', 'notify', 'changed')],
 steps=[
  ('Devices', 'Scanner / driver app with a local queue', 'Scans stored with a UUID scan_id and device time; synced when online.', 'Works in warehouses with bad Wi-Fi.'),
  ('Ingest', 'Ingest API → Kafka scan-events keyed by package_id', 'Dedupes by scan_id; same package → same partition → ordered.', 'Idempotent and ordered per package.'),
  ('State machine', 'Package state service', 'Applies only valid transitions with a conditional update (expected state); late scans go to history only.', 'Packages never move backwards.'),
  ('Routing', 'Hub graph in memory; Dijkstra on time with capacity limits', 'Recomputed on exceptions (hub closed, missed truck).', 'Good-enough path, quickly.'),
  ('Tracking', 'Tracking API + cache; history table (package_id, time)', 'Customers read status and events.', 'Read-heavy, cacheable.')])

D['spell'] = dict(
 rows=[[('ed', 'Editor', 'word boundary event'), ('wk', 'Web worker', 'off the UI thread'), ('dawg', 'DAWG dictionary', 'loaded in memory')],
       [('sym', 'SymSpell index', 'delete variants'), ('pers', 'Personal words', 'synced via API'), ('cdn', 'Dictionary CDN', 'versioned files')]],
 arrows=[('ed', 'wk', 'finished word'), ('wk', 'dawg', 'exists?'), ('wk', 'sym', 'suggest'), ('pers', 'wk', 'merge'), ('cdn', 'dawg', 'download')],
 steps=[
  ('Trigger', 'Editor emits finished words (space / punctuation) to a web worker', 'Only changed words are re-checked.', 'UI never stutters.'),
  ('Lookup', 'DAWG (compressed trie) of ~500K words with frequencies, a few MB', 'Membership check in microseconds.', 'Fits on the device; works offline.'),
  ('Suggestions', 'SymSpell-style precomputed delete index (edit distance ≤ 2)', 'Candidates ranked by frequency and the previous word.', 'Much faster than generating all edits.'),
  ('Personal words', 'Small sync API; stored per user', 'Names and jargon stop being flagged.', 'Fewer false alarms.'),
  ('Updates', 'Versioned dictionary files on a CDN; background download', 'Swap atomically when ready.', 'New words without app releases.')])

D['quota'] = dict(
 rows=[[('dev', 'API client', 'company app'), ('gw', 'API gateway', 'quota filter'), ('api', 'Public APIs', '')],
       [('redis', 'Redis Cluster', 'INCR company:user:date'), ('cfg', 'Quota config', 'cached'), ('kafka', 'Kafka', 'api-usage')],
       [('wh', 'Warehouse', 'Spark / Pinot'), ('bill', 'Billing + dashboards', '')]],
 arrows=[('dev', 'gw', 'call'), ('gw', 'redis', 'INCR + check'), ('gw', 'api', 'allowed'), ('cfg', 'gw', 'limits'), ('gw', 'kafka', 'usage event'), ('kafka', 'wh', 'consume'), ('wh', 'bill', '')],
 steps=[
  ('Check', 'Gateway filter: Lua INCR on company:user:yyyymmdd with EXPIRE 48 h', 'If the new count exceeds the limit → 429 with X-Quota-Remaining and reset time.', 'Date in the key = automatic daily reset.'),
  ('Hot keys', 'Split big companies\' counters into N sub-keys; sum on read', 'Spreads load across Redis shards.', 'One company must not overload one shard.'),
  ('Usage events', 'Every call → Kafka api-usage (company, user, endpoint, status, time)', 'Asynchronous; never blocks the call.', 'Complete record for billing.'),
  ('Reports and billing', 'Spark/Pinot aggregates usage per company per day', 'Dashboards and invoices read these tables.', 'Bill from logs, not from counters.'),
  ('Failure', 'Redis timeout → fail open, flag for reconciliation', 'Over-quota calls during the outage are found later in the logs.', 'API stays up.')])

D['geoviz'] = dict(
 rows=[[('reg', 'Registration service', 'emits event'), ('kafka', 'Kafka', 'member-registered'), ('flink', 'Flink job', 'geo-IP → H3 cell, 10-s windows')],
       [('redis', 'Redis', 'latest counts per cell'), ('pinot', 'Pinot', 'time-bucketed history'), ('push', 'SSE / WebSocket service', 'deltas')],
       [('map', 'Map UI', 'Mapbox / deck.gl heat map')]],
 arrows=[('reg', 'kafka', 'event'), ('kafka', 'flink', 'consume'), ('flink', 'redis', 'cell counts'), ('flink', 'pinot', 'append'), ('redis', 'push', 'changed cells'), ('push', 'map', 'every 5 s'), ('pinot', 'map', 'replay')],
 steps=[
  ('Event', 'Registration service publishes member-registered (IP, country from profile) to Kafka', 'No exact location is ever displayed.', 'Privacy by design.'),
  ('Enrich + aggregate', 'Flink: geo-IP lookup → H3 cell (resolution by zoom) → 10-second tumbling window counts', 'Small-count cells are hidden (k-anonymity).', 'Aggregation makes it private and light.'),
  ('Latest view', 'Redis hash of cell → count for the current window', 'Push service diffs against the previous window.', 'Only changed cells go to browsers.'),
  ('History', 'Pinot table (window_start, cell, count)', 'Replay the last 24 hours with a range query.', 'Fast time-range aggregates.'),
  ('Delivery', 'SSE/WebSocket push of deltas; for huge audiences a CDN-cached JSON every few seconds', 'Map renders a heat map with deck.gl/Mapbox.', 'Computed once, served to everyone.')])

D['inmail'] = dict(
 rows=[[('client', 'Sender app', ''), ('msg', 'Messaging API', 'validate'), ('credits', 'Credits ledger', 'MySQL, idempotency key')],
       [('spam', 'Trust & safety', 'scoring service'), ('conv', 'Conversation store', 'Cassandra (conv_id, seq)'), ('kafka', 'Kafka', 'message-sent')],
       [('inbox', 'Inbox index', 'by user_id'), ('rt', 'Real-time gateway', 'WebSocket'), ('notif', 'Notifications', 'email / push')]],
 arrows=[('client', 'msg', 'send'), ('msg', 'credits', 'debit'), ('msg', 'spam', 'score'), ('msg', 'conv', 'append'), ('msg', 'kafka', 'event'),
         ('kafka', 'inbox', 'update both users'), ('kafka', 'rt', 'if online'), ('kafka', 'notif', 'if offline')],
 steps=[
  ('Send', 'Messaging API with an idempotency key per send', 'Checks block lists, sender limits, then debits a credit in the ledger (same key).', 'Retries never double-charge.'),
  ('Trust & safety', 'Scoring service (rules + model)', 'Spammy messages are held or dropped before delivery.', 'InMail\'s defining risk.'),
  ('Store', 'Cassandra conversations table (conversation_id, seq)', 'Message stored once.', 'A thread is one partition.'),
  ('Index', 'Kafka message-sent → inbox writer updates both users\' inbox rows (last message, unread)', 'Inbox = one partition per user.', 'Store once, index twice.'),
  ('Deliver', 'WebSocket gateway if online; notification system otherwise', 'Read receipts flow back as events.', 'Real-time when possible.'),
  ('Refund', 'Job: if the recipient replies within N days, credit back', 'Ledger entry with the original send id.', 'Business rule kept auditable.')])

D['svcauthz'] = dict(
 rows=[[('a', 'Service A', 'Envoy sidecar'), ('b', 'Service B', 'Envoy sidecar + authz filter'), ('opa', 'Local policy engine', 'in the sidecar')],
       [('ca', 'Internal CA', 'SPIFFE IDs, short-lived certs'), ('repo', 'Policy repo', 'Git + review'), ('dist', 'Policy distribution', 'xDS / push')],
       [('audit', 'Audit log', 'Kafka → warehouse')]],
 arrows=[('a', 'b', 'mTLS call'), ('ca', 'a', 'cert'), ('ca', 'b', 'cert'), ('b', 'opa', 'allow(caller, method)?'), ('repo', 'dist', 'compile'), ('dist', 'opa', 'push'), ('opa', 'audit', 'decision')],
 steps=[
  ('Identity', 'Internal CA issuing short-lived certificates with SPIFFE-style IDs (spiffe://linkedin/ns/service)', 'Rotated automatically every few hours.', 'Identity cannot be faked with a header.'),
  ('Transport', 'Sidecar proxies (Envoy) doing mTLS on every call', 'The callee\'s sidecar knows exactly which service called.', 'No code change in services.'),
  ('Decision', 'Policy evaluated locally in the callee sidecar (embedded policy engine)', 'allow(caller_id, method) from in-memory rules; microseconds.', 'No central call per request.'),
  ('Policy management', 'Policies in Git with code review; compiled and pushed to sidecars (xDS-style)', 'Each callee receives only its own rules.', 'Auditable changes, fast rollout.'),
  ('Rollout safety', 'Log-only (shadow) mode before enforcing', 'Collect would-be denials, fix, then enforce.', 'Avoids self-inflicted outages.'),
  ('Audit', 'Decisions sampled/streamed to Kafka → warehouse', 'Investigations and access reviews.', 'Compliance.')])
