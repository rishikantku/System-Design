# -*- coding: utf-8 -*-
"""Guides for the questions added from LeetCode Discuss (15 Oct 2026), and additions to merged questions.
Same simple-English style as guides.py."""

G2 = {}

G2['metrics'] = dict(
 gist='The most reported LinkedIn design question. Collect `[source, metric, value]` from hundreds of machines, store it as **time series**, let people **graph** any metric for any hosts over time, and **alert** on thresholds. The hard parts: very high **write volume**, fast **range queries**, and alerting that does not miss or spam.',
 clarify=[('How many sources and metrics, how often?', 'Decides write rate — the main number in this question.'),
          ('How long to keep data, and at what detail?', 'Raw for days, then downsampled (1-min, 1-hour) — decides storage.'),
          ('How fresh must graphs and alerts be?', 'Alerts within ~1 minute usually; graphs a few seconds behind is fine.'),
          ('Which queries? One metric for a few hosts (t1→t2), or aggregates (p99 across a cluster)?', 'Decides the data layout and pre-aggregation.'),
          ('Push or pull — can we put an agent on every machine?', 'Decides the collection path.')],
 numbers=['500 machines × 2,000 stats × every 10 s = 100K points/s (scale ×100 for LinkedIn-size: 10M/s).',
          'A point ≈ 16 bytes compressed (Gorilla-style delta encoding gets ~1.4 bytes) → small per point, large in total.',
          'Graph query: 3 hosts × 1 week × 1 point/min ≈ 30K points — cheap if data is stored by (metric, source, time).'],
 api=['Agent → POST /ingest (batched points)', 'GET /query?metric=mem&sources=h1,h2,h3&from=t1&to=t2&step=1m', 'POST /alerts {metric, condition: > 70%, for: 5m, notify}'],
 parts=[('Agent on each machine', 'Collects stats, batches every 10 s, compresses, sends. Buffers on local disk if the collector is unreachable.'),
        ('Collectors + Kafka', 'Receive batches and write to Kafka (durable buffer, absorbs spikes, lets several consumers read).'),
        ('Time-series DB', 'Stores points keyed by (metric, source) and time, compressed in time blocks. Sharded by series.'),
        ('Rollup jobs', 'Build 1-min and 1-hour averages/max; delete raw data after N days.'),
        ('Query service', 'Picks the right resolution for the time range (a week → 1-min rollups, not raw).'),
        ('Alerting engine', 'Evaluates rules on the stream (or on recent data every 30 s); dedupes and routes to email/pager.'),
        ('Dashboard UI', 'Graphs from the query service.')],
 deep=[('Data layout', 'Group points by series (metric + source) and time block (e.g. 2 hours). A graph query reads a few contiguous blocks. Compress timestamps and values with deltas — this is why TSDBs are so small.'),
       ('Downsampling', 'Nobody needs 10-second points from last year. Keep raw for ~2 weeks, 1-minute for months, 1-hour for years. The query service chooses the resolution from the range.'),
       ('Alerting that works', '"Above 70% for 5 minutes", not "above 70% once" (avoids flapping). Treat **missing data as a signal** — a dead host sends nothing. Group and dedupe alerts during incidents.'),
       ('Cardinality', 'The real danger: a label like user_id creates millions of series and kills the TSDB. Limit labels, and reject or sample high-cardinality metrics.')],
 followups=[('Write rate goes 10× — what breaks first?', 'The TSDB write path. Add shards by series, batch harder on agents, drop or sample low-value metrics. Kafka absorbs short spikes.'),
            ('Graph a cluster-wide p99 over 30 days fast.', 'Pre-aggregate per cluster in rollups (or store histograms/sketches); never compute it from raw points at query time.'),
            ('The monitoring system itself goes down.', 'Run it per data centre; each DC monitors itself and the others. Agents buffer locally. A separate tiny heartbeat checker watches the monitor.'),
            ('Host health across 3 data centres (the InterviewDB version).', 'Per-DC collectors and storage, a global view that merges them, and a current-state store (latest status per host) for "what is unhealthy now".'),
            ('How do you avoid alert spam?', 'For-duration conditions, grouping by service, dedupe, severity levels, silence windows during maintenance.')],
 mistakes=['Writing every point straight into a SQL table.', 'No downsampling — storage grows forever, week-long graphs are slow.',
           'Alerting on a single sample (flapping).', 'Forgetting that a silent host is a failure.', 'Ignoring cardinality.'],
 say='"Agents batch to Kafka, a sharded time-series store keeps compressed series with rollups, queries pick the resolution from the range, and alerts evaluate for-duration rules on the stream — with missing data treated as an alert."')

G2['scheduler'] = dict(
 gist='Run jobs at the right time on machines you **ask for through an API**, make sure each job runs **once**, survive scheduler crashes, and **alert** on failures. The core: a durable job store, a way to find **due jobs** quickly, **leases** so two schedulers never run the same job, and a clear **job state machine**.',
 clarify=[('One-off jobs, recurring (cron), or both? Dependencies between jobs?', 'Recurring needs a "next run time"; dependencies need a DAG — say if out of scope.'),
          ('Exactly once, or at least once with idempotent jobs?', 'Exactly once is very hard; at-least-once + idempotent jobs is the usual answer.'),
          ('What does the machine API give us — a free machine on request? Can machines die mid-job?', 'Decides retries and heartbeats.'),
          ('How many jobs per day, and how late is acceptable?', 'Decides how we find due jobs (DB index vs time buckets).'),
          ('Alert on what — failure, timeout, too many retries, late start?', 'Defines the alerting rules.')],
 numbers=['Say 10M job runs/day ≈ 120/s average, peaks of 2K/s at the top of the hour (cron jobs bunch up).',
          'Job record ~1 KB → 10 GB/day of run history; keep 30 days.', 'Due-job lookup must handle the top-of-hour spike without scanning everything.'],
 api=['POST /jobs {cron or runAt, command, resources, retries, timeout}', 'GET /jobs/{id}/runs', 'Given: fetchMachines(requirements) → machine(s)', 'Worker → POST /runs/{id}/heartbeat, /complete'],
 parts=[('Job store (DB)', 'Job definitions and run records: id, next_run_at, state, attempt, owner, lease_until.'),
        ('Scheduler nodes', 'Find due runs, claim them with a lease, ask the machine API for a machine, dispatch.'),
        ('Due-time index', 'Index on next_run_at (or time buckets per minute), partitioned so many schedulers can share the work.'),
        ('Executor / worker agent', 'Runs the job on the machine, sends heartbeats, reports result.'),
        ('Monitor', 'Finds runs with expired heartbeats or timeouts → retry or fail.'),
        ('Alerting', 'Failed, timed out, retries exhausted, started late → notification service.')],
 deep=[('No double runs', 'A scheduler **claims** a run with an atomic update: `SET state=claimed, lease_until=now+30s WHERE id=? AND state=due`. Only one wins. If it crashes, the lease expires and another scheduler picks it up.'),
       ('State machine', 'scheduled → claimed → running → succeeded / failed → (retry → scheduled) / dead. Every change is an atomic update with the expected old state, so late messages cannot move a run backwards.'),
       ('Machine failure mid-job', 'Workers heartbeat every few seconds. Missed heartbeats → the monitor marks the run lost and schedules a retry (with backoff), on a new machine from the API. Jobs must be idempotent because a retry may repeat work.'),
       ('Top-of-hour spike', 'Partition due runs by hash across scheduler nodes; add small random jitter for jobs that do not need the exact second.')],
 followups=[('Do you need ZooKeeper / a coordination service?', 'Not for claiming runs — an atomic DB update with a lease is enough. Use one only if you need leader election for something singular. (A candidate lost points for adding one that was not needed.)'),
            ('The machine API is slow or has no free machines.', 'Queue the run as waiting-for-capacity, retry with backoff, alert if it starts too late.'),
            ('Jobs depend on other jobs.', 'Store a DAG; a run becomes due when its parents succeed.'),
            ('Exactly-once execution?', 'Not guaranteed across crashes — make jobs idempotent (unique run id, check before side effects).'),
            ('How do users see what happened?', 'Run history with logs link, status, attempts; dashboards on success rate and lateness.')],
 mistakes=['Two schedulers can pick the same job (no atomic claim).', 'No heartbeats — a dead machine leaves a job "running" forever.',
           'Scanning the whole job table every second.', 'Promising exactly-once.', 'Adding a coordination service you cannot justify.'],
 say='"Durable job store with a due-time index, atomic lease-based claims so a run executes once at a time, heartbeats and timeouts drive retries on new machines from the API, and every terminal failure raises an alert."')

G2['cache'] = dict(
 gist='Starts as **low-level design**: a cache whose **capacity** and **eviction policy** are configurable — so eviction must be a **plug-in (strategy pattern)**, not hard-coded LRU. Then it becomes **high-level design**: many nodes, sharding, replication, and **hot keys** in a write-heavy setup, with some Redis internals.',
 clarify=[('Capacity by number of items or by bytes?', '"Based on memory and data size" → track bytes, so each entry needs its size.'),
          ('Which policies must exist on day one? Can users add their own?', 'LRU and lowest-priority now; an interface so more can be added.'),
          ('TTL as well?', 'Usually yes — expiry is separate from eviction.'),
          ('Thread-safe?', 'Yes for a real cache — decide the lock design.'),
          ('For the distributed part: read-heavy or write-heavy? Consistency needs?', 'The report says write-heavy with hot keys.')],
 numbers=['One node: say 32 GB, entries ~1 KB → ~30M entries; per-entry overhead (pointers, policy data) ~50–100 bytes.',
          'Distributed: 1M ops/s across 20 nodes → 50K ops/s each — fine for in-memory.', 'One hot key at 200K writes/s overloads a single node — this is the hot-key problem.'],
 api=['Cache(capacityBytes, IEvictionPolicy policy)', 'Get(key) / Put(key, value, size, priority?, ttl?) / Remove(key)', 'IEvictionPolicy: OnInsert, OnAccess, OnRemove, PickVictim'],
 parts=[('Cache core', 'Dictionary key → entry (value, size, metadata). Tracks used bytes. Calls the policy on every event.'),
        ('Eviction policy interface', 'OnInsert / OnAccess / OnRemove / PickVictim. The core never knows which policy it has.'),
        ('LRU policy', 'Doubly linked list in recency order — O(1) for every call.'),
        ('Lowest-priority policy', 'Min-heap or SortedSet by (priority, insert order); ties → oldest.'),
        ('Distributed tier', 'Consistent hashing to place keys on nodes; replicas for availability; client library or proxy routes requests.')],
 deep=[('Why a policy interface', 'The question\'s key word is "customisable". With a strategy interface, adding LFU or TTL-first eviction is a new class, not a change to the cache. Evict in a loop until `used + newSize <= capacity` — one big item may need several evictions.'),
       ('Thread safety', 'Simple: one lock around each operation (a Get also changes LRU order, so it writes). Faster: shard the cache into N segments, each with its own lock and policy — approximate global LRU.'),
       ('Hot keys, write-heavy', 'Spread one hot key: split it into sub-keys (key#1..key#N) and combine on read, or batch writes locally and flush. For reads: replicate the hot key or keep a small local cache on clients.'),
       ('Redis internals they may ask', 'Single-threaded command execution (no locks, one core per instance), approximate LRU by sampling a few keys, persistence by RDB snapshots and AOF log, cluster mode with 16,384 hash slots.')],
 followups=[('Add an LFU policy.', 'New class implementing the interface: frequency buckets with a min-frequency pointer, O(1). No change to the cache core.'),
            ('An item bigger than the whole capacity?', 'Reject it (or do not cache it) — say it explicitly.'),
            ('A node dies.', 'Consistent hashing moves only its keys; replicas serve them; the cache refills from the source. Expect a miss spike — protect the database (request coalescing).'),
            ('Cache and database disagree.', 'Cache-aside with invalidation on write, short TTLs, and versioned keys for important data.'),
            ('Why is Redis fast despite one thread?', 'In-memory, no locks, efficient data structures, I/O multiplexing; scale out with more instances.')],
 mistakes=['Hard-coding LRU inside the cache when the question says "customisable".', 'Counting items when capacity is in bytes.',
           'Forgetting a Get changes LRU order (so it needs the lock).', 'Ignoring the hot-key problem in the distributed part.'],
 say='"A cache core that tracks bytes and delegates every eviction decision to a pluggable policy; then consistent hashing, replicas, and key splitting or local batching for hot keys."')

# Additions to the merged questions: appended to the existing guide lists.
ADD = {
 'kvstore': dict(
  deep=[('The distributed version (two of the three LeetCode reports)', 'Partition keys with **consistent hashing** (virtual nodes so adding a node moves little data). Replicate each partition to 3 nodes. Consistency: quorum reads/writes (W + R > N) for strong-ish reads, or leader-per-partition for simple strong consistency. Name the trade: availability during partitions vs fresh reads.')],
  followups=[('Partitioning, replication and consistency — how?', 'Consistent hashing with virtual nodes; replication factor 3; leader-follower per partition (simple, strong) or leaderless quorum N=3, W=2, R=2 (more available). Hinted handoff and read repair for leaderless.'),
             ('Disk cleanup — when do you run compaction, and does it hurt reads?', 'Compact when dead data in a file passes a threshold (e.g. 50%); run in the background with an I/O budget; readers keep using old files until the swap is atomic.'),
             ('How do you know what is safe to delete after compaction?', 'Write the new file fully, fsync, update the index to point at it, then delete the old file. A crash in between leaves extra files, never lost data.')]),
 'topn': dict(
  deep=[('Several windows at once (5 min, 1 hour, 24 hours)', 'Keep minute buckets. 5 min = merge 5 buckets; 1 hour = 60; 24 hours = merge hourly rollups (each hour merged once and stored). Same pipeline, three cheap merges.')],
  followups=[('Do you need a coordination service (ZooKeeper)?', 'No — a candidate lost points adding one. Machines just send counts to aggregators partitioned by key; nothing here needs leader election or locks. Only add a component when you can say exactly what breaks without it.')]),
 'notify': dict(
  deep=[('Per-category limits ("5 marketing notifications per day per user")', 'Counter per (user, category, day) in Redis with expiry — atomic increment, reject or delay when over. Transactional and security categories are never limited. Check limits **after** preferences and **before** sending.')],
  followups=[('Add rate limits per category.', 'Per (user, category, day) counters; different limits per category; over the limit → drop or merge into a digest. Never limit security codes.'),
             ('Where do user preferences sit?', 'A preference service checked first (opt-outs per channel and category, quiet hours); cached because it is read on every notification.')]),
 'denylist': dict(
  deep=[('"Intercept malicious requests" (the second LeetCode wording)', 'Where you intercept matters: at the edge (load balancer / API gateway) so bad traffic never reaches services. The in-memory denylist check runs there. isMaliciousRequest is expensive, so call it asynchronously on a sample or on suspicious traffic and feed results into the denylist, rather than calling it on every request.')],
  followups=[('Must isMaliciousRequest run on every request?', 'Usually no — too slow. Check the cheap in-memory denylist on every request, run the expensive classifier async (or only on suspicious patterns), and add offenders to the list.')]),
}
