# -*- coding: utf-8 -*-
"""Systems & Infrastructure classics — the shapes the pack's own role description points at:
"massively scalable data storage and replication systems, a cutting edge search platform, an
application and service delivery platform, Big Data and Machine Learning platforms"."""

INFRA_DESIGNS = [
 dict(id='kvstore', title='Design a replicated key-value store', topic='Storage · Replication', prio='p0',
  why='The pack names **massively scalable data storage and replication systems** first. This design carries the primitives every '
      'other infrastructure answer leans on: consistent hashing, quorums, failure detection, anti-entropy.',
  ask=['Consistency: linearizable, or eventually consistent with tunable quorums?',
       'Value size and access pattern — small records with point lookups, or large blobs?',
       'Single region or multi-region? (It changes the write path completely.)',
       'Durability bar: must an acknowledged write survive one node failure? Two? A zone?',
       'Do we need range scans, or is hashing enough?'],
  fr=['Get, Put and Delete by key', 'Configurable replication factor',
      'Membership changes (add and remove nodes) without downtime', 'Repair of divergent replicas'],
  nfr=['p99 read latency in single-digit milliseconds', 'No data loss for acknowledged writes',
       'Availability through node and zone failure', 'Predictable rebalancing cost when the cluster grows'],
  scale='1 billion keys × 1 KB = 1 TB of logical data; replication factor 3 → 3 TB, plus compaction headroom, so plan ~5 TB of '
        'disk. 200k reads/s and 20k writes/s across, say, 30 nodes is ~7k reads/s per node — comfortable for SSD-backed storage '
        'with a page cache, which tells you this is a coordination problem, not an IO problem.',
  api='`Get(key, consistency)` → value + version; `Put(key, value, ifVersion?)` → version; `Delete(key, version)`. Versions are '
      'vector clocks or a hybrid logical clock — expose them, because the client needs them for compare-and-set.',
  data='Partition by hash of the key onto a ring with virtual nodes (say 256 per physical node). Each partition has R replicas on '
       'distinct nodes in distinct zones. Storage engine: an LSM tree for write-heavy workloads (memtable → SSTables → compaction) '
       'or a B-tree for read-heavy. Say which and why.',
  arch='''Coordinator (any node) hashes the key, finds the preference list of R replicas, and fans out.

**Writes**: send to R, acknowledge after W respond. **Reads**: ask R, answer after r respond. With W + r > R you get read-your-writes '
on a healthy cluster. Common settings: R=3, W=2, r=2.

**Failure handling**: hinted handoff parks writes for a down replica on a neighbour and replays them on recovery; read repair fixes '
divergence noticed at read time; Merkle-tree anti-entropy sweeps fix the rest in the background.

**Membership**: gossip for liveness, and a coordination service (or a Raft-managed config) for the authoritative ring, so nodes never '
disagree about ownership during a rebalance.''',
  deep=['**Consistent hashing with virtual nodes.** Without vnodes, adding a node moves one neighbour\'s entire range and creates a '
        'hot spot; with 256 vnodes per node, adding one node takes a little from everyone. Also explain why the ring must be '
        'authoritative config rather than gossip-derived — two nodes disagreeing about ownership is how you lose writes.',
        '**Quorum arithmetic.** W + r > R guarantees an overlap on a healthy cluster; it does **not** give linearizability under '
        'failures and concurrent writes. If the interviewer wants linearizable, you need a consensus group per partition (Raft), '
        'and you pay a round trip. Knowing the difference is the point of this question.',
        '**Conflict resolution.** Last-write-wins loses data under clock skew; vector clocks preserve causality but push merging '
        'onto the client; CRDTs solve it for specific types. Pick one and own the consequence.',
        '**LSM internals.** Write path: WAL, memtable, flush, compaction. Read path: memtable, then SSTables newest-first with bloom '
        'filters. Compaction strategy is the real operational lever — levelled gives better reads and more write amplification; '
        'tiered is the reverse.',
        '**Rebalancing.** Moving a partition must be throttled, resumable and observable; the naive version saturates the network '
        'and takes the cluster down while "adding capacity".'],
  fails=['Node down → hinted handoff; reads still satisfied by the other replicas.',
         'Zone down → if replicas are zone-aware, quorum still met; if not, you just discovered your placement bug.',
         'Network partition → both sides may accept writes; you get divergence, and anti-entropy plus conflict resolution repairs it. '
         'Say which side of CAP you chose and why.',
         'Slow node (grey failure) → hedge reads to a second replica after a percentile-based delay; do not wait for the timeout.',
         'Compaction storm → back-pressure writes, and alarm on pending compaction bytes.'],
  scaling=['Add nodes and move vnodes — throttled and resumable.',
           'Read-heavy: add replicas. Write-heavy: add partitions.',
           'Hot key: it cannot be split by hashing — cache it, or shard the key itself with a suffix and fan out reads.',
           'Multi-region: async replication with per-region quorums, and an explicit answer for cross-region conflicts.'],
  obs=['p99 by operation and by partition (skew shows here first)', 'Hinted handoff queue depth and age',
       'Repair progress and divergence rate', 'Compaction backlog', 'Replica lag'],
  sec=['Per-tenant key prefixes with authorisation in the coordinator, not in clients.',
       'Encryption at rest per tenant if the store is shared; TLS between nodes.'],
  cost='Disk and replication factor dominate: R=3 triples storage and network. Say what R=2 would save and what it would cost you '
       '(no quorum tolerance for a single failure) — that trade is the conversation.',
  trade=[('Quorum vs consensus', 'Tunable quorums are cheap and fast, but not linearizable; Raft per partition is correct and costs a round trip'),
         ('LWW vs vector clocks', 'Simplicity versus not silently losing concurrent writes'),
         ('Replication factor', 'Durability and read capacity versus storage and write amplification'),
         ('LSM vs B-tree', 'Write throughput versus read predictability and space amplification')],
  evolve='Phase 1: single region, R=3, quorum reads and writes, LWW with explicit clock discipline. Phase 2: anti-entropy and '
         'hinted handoff. Phase 3: per-partition consensus for the tables that need linearizability, or multi-region async. '
         'Do not start with consensus everywhere — you pay for it on every write forever.',
  senior='"Consistent hashing, three replicas, quorum reads and writes."',
  staff='"Quorums give me overlap, not linearizability — under a partition with concurrent writes I still diverge, so I need a '
        'conflict story: vector clocks with client merge, or Raft per partition where the table genuinely needs it. I would also '
        'make the ring authoritative config rather than gossip-derived, because ownership disagreement during a rebalance is how '
        'you lose acknowledged writes."'),

 dict(id='streamproc', title='Design a stream processing system (Samza-like)', topic='Streaming · State', prio='p0',
  why='LinkedIn built Samza, and the pack lists Big Data platforms as core SI work. Stateful stream processing is the design that '
      'separates people who have used Kafka from people who have operated it.',
  ask=['Processing guarantee: at-least-once, or effectively-once with transactional output?',
       'Is the processing stateful (joins, windows, aggregations) or stateless?',
       'What is the acceptable end-to-end lag — seconds, or minutes?',
       'Do jobs need to be reprocessed from the beginning, and how often?',
       'Who owns the jobs — one team, or hundreds of teams on a shared cluster?'],
  fr=['Run user-defined processors over partitioned input streams', 'Maintain per-key local state with durability',
      'Windowing and joins across streams', 'Reprocess history from an offset or timestamp',
      'Scale a job up and down without losing state'],
  nfr=['End-to-end lag p99 within seconds', 'Exactly-once *effects* where the sink supports it',
       'A failed container must recover state in seconds to low minutes, not hours',
       'One misbehaving job must not starve others on a shared cluster'],
  scale='1 million events/s across 1,000 partitions = 1,000 events/s per task. State: 100 million keys × 200 bytes = 20 GB across '
        'the job, so ~200 MB per task — small enough to keep local on disk with an in-memory cache, which is exactly the argument '
        'for local state over a remote store.',
  api='A processor interface: `Process(message, collector, coordinator)`; a job spec declaring inputs, outputs, parallelism, state '
      'stores and the checkpoint interval. Operational API: deploy, scale, pause, reset-to-offset.',
  data='Input: partitioned logs. State: an embedded key-value store per task (RocksDB-style), **backed by a compacted changelog '
       'topic** so it can be rebuilt. Output: another log, or an external sink with idempotent writes.',
  arch='''One task per input partition; tasks are assigned to containers by a coordinator. Each task reads its partition, updates '
local state, writes state mutations to a compacted changelog, and emits output.

**Recovery**: a container dies, the coordinator reassigns its tasks, and the new task rebuilds local state by replaying the '
changelog — which is why the changelog is compacted (rebuild time is proportional to the state size, not the history).

**Checkpointing**: input offsets are committed only after the corresponding state and output are durable, which is what makes '
replay correct.''',
  deep=['**Local state versus remote state.** Local + changelog gives microsecond reads and fast, bounded recovery; a remote store '
        'gives instant failover and a network round trip per event. At 1,000 events/s per task the round trip is the whole latency '
        'budget, so local wins — and the changelog is what makes local safe.',
        '**Effectively-once.** At-least-once delivery plus idempotent state updates plus transactional or idempotent sinks. Offsets '
        'commit after state and output are durable. Say plainly that end-to-end exactly-once requires cooperation from the sink.',
        '**Windowing and time.** Event time versus processing time; watermarks and allowed lateness; what happens to a very late '
        'event (drop, side output, or update the aggregate). This is the part interviewers push on.',
        '**Joins.** Stream-stream joins need buffered windows on both sides (memory); stream-table joins need the table co-partitioned '
        'with the stream, or every lookup is remote. Co-partitioning is the trick worth naming.',
        '**Rescaling.** Changing parallelism means reassigning partitions and moving state; with more tasks than containers you can '
        'rescale without repartitioning the input — which is why over-partitioning the input up front is good planning.'],
  fails=['Container crash → reassign tasks, rebuild from changelog; lag spikes, correctness holds.',
         'Changelog unavailable → new tasks cannot start; the job stalls rather than serving wrong state. Fail closed.',
         'Poison message → a dead-letter path plus a skip counter; a job that crash-loops on one message is an outage.',
         'State growth without bound → TTL or retention on state stores; alarm on state size per task.',
         'Slow sink → back-pressure through the pipeline; never drop silently.'],
  scaling=['Partitions cap parallelism — over-partition the input at creation.',
           'Scale containers, not tasks; tasks move between containers.',
           'Hot partition (key skew) → salt the key and re-aggregate, or repartition with a better key.',
           'Cluster level: quotas per job so one team cannot starve another.'],
  obs=['Consumer lag per partition (the headline)', 'Processing time per event, p50 and p99',
       'State store size and changelog lag', 'Restore time after failover — track it before you need it',
       'Dead-letter counts'],
  sec=['Multi-tenant cluster: per-job credentials and topic ACLs, plus quotas.',
       'State on disk may hold personal data — encrypt and apply retention.'],
  cost='Container memory and local disk, plus the changelog topics (which double the write volume of stateful jobs). Point that '
       'out: stateful streaming costs about twice what people estimate, and compaction is what keeps it bounded.',
  trade=[('Local vs remote state', 'Latency and recovery time versus instant failover'),
         ('Exactly-once', 'Correctness versus throughput and sink constraints'),
         ('Window size', 'Completeness versus memory and lag'),
         ('Partition count', 'Future parallelism versus metadata and rebalancing cost')],
  evolve='Phase 1: stateless jobs, at-least-once, idempotent sinks. Phase 2: local state with changelog and bounded recovery. '
         'Phase 3: event-time windows with watermarks, then transactional sinks. Most teams never need phase 3 — say so.',
  senior='"Consume from Kafka, process, produce to Kafka, and store state in a database."',
  staff='"The design decision is local state with a compacted changelog, because a remote store puts a network round trip on every '
        'event and makes recovery unbounded. Then the real work is the ordering of offset commits relative to state and output '
        'durability — that ordering is what makes replay safe, and it is where at-least-once quietly becomes duplicated effects."'),

 dict(id='cdc', title='Design change data capture (Brooklin-like)', topic='Data movement · Ordering', prio='p1',
  why='LinkedIn built Brooklin for exactly this. It is also the closest infrastructure analogue to your own tenant-migration work: '
      'bootstrap, catch-up, cutover, verification.',
  ask=['Which sources — relational databases, key-value stores, or both?',
       'Do consumers need strict per-key ordering? Per-transaction ordering?',
       'Is a full bootstrap of existing data required, or only changes from now?',
       'What is the tolerated lag, and what happens when a consumer falls behind retention?',
       'Schema evolution: who owns compatibility?'],
  fr=['Capture inserts, updates and deletes from a source without application changes',
      'Deliver them to one or more destinations in order per key', 'Bootstrap existing rows, then switch to streaming',
      'Resume from a checkpoint after failure'],
  nfr=['End-to-end lag of seconds', 'No lost changes; duplicates acceptable if consumers are idempotent',
       'Negligible load on the source database', 'Schema changes must not break consumers'],
  scale='10,000 changes/s across 500 tables, average 1 KB → 10 MB/s steady state. A bootstrap of a 2 TB table at 100 MB/s takes '
        '~6 hours, during which changes keep arriving — which is why bootstrap and streaming must overlap, exactly like a tenant '
        'migration.',
  api='Declarative: `CreateStream {source, tables, destination, startFrom: bootstrap|now|position}`. Operational: pause, resume, '
      'reset position, inspect lag.',
  data='Read the database\'s own replication log (binlog/WAL) — never poll with `updated_at`, which misses deletes and is a '
       'full-table scan. Emit records keyed by primary key so partitioning preserves per-key order. Carry a schema id per record.',
  arch='''Source connector tails the replication log per source, converts rows to a canonical envelope (before/after images, op type, '
transaction id, position), and publishes to a partitioned log keyed by primary key. Destination connectors consume and apply.

**Bootstrap**: snapshot at a known log position, stream the snapshot, then replay the log from that position. Overlap is handled by '
keying on the primary key and letting later versions win — the same copy-then-catch-up shape as a live tenant migration.

**Checkpointing**: the consumed log position is the resume point; it must be committed only after the data is durable downstream.''',
  deep=['**Why the replication log, not polling.** Polling `updated_at` misses deletes, misses out-of-order commits, and hammers '
        'the source. The log gives you deletes, ordering and low impact. This is the single most important answer in the question.',
        '**Ordering guarantees.** Per-key order comes from partitioning by primary key. Cross-table transactional order does not '
        'survive that, so if a consumer needs it you must either single-partition (throughput ceiling) or expose transaction ids and '
        'let consumers reassemble. Name the trade rather than promising global order.',
        '**Schema evolution.** Register schemas, enforce compatibility at publish time, and carry the schema id with each record. '
        'A column drop is the dangerous one — it breaks consumers silently at read time.',
        '**Bootstrap overlap.** Snapshot at position P, then replay from P. Duplicates are inevitable, so downstream must be '
        'idempotent (upsert by key). If it cannot be, you are back to a freeze window — which is a business conversation.',
        '**Deletes and tombstones.** A delete must propagate, and compacted topics need a null-value tombstone. Forgetting this '
        'resurrects deleted rows downstream, which is a compliance bug, not just a data bug.'],
  fails=['Source failover → the log position changes; use GTIDs or equivalent, not file offsets.',
         'Consumer falls behind retention → it cannot resume; it needs a re-bootstrap. Alarm on lag against retention, not on lag alone.',
         'Log gap or corruption → stop and alert; never skip silently, because a silent gap is invisible data loss.',
         'Destination down → buffer in the log; the source is unaffected, which is the main benefit of the log in the middle.',
         'Schema change mid-stream → reject incompatible changes at publish, and make the failure loud.'],
  scaling=['Partition by primary key; scale partitions per table by write volume.',
           'Separate high-volume tables onto their own streams so one table cannot starve the rest.',
           'Parallelise bootstrap by key range, then merge into the same stream.'],
  obs=['Lag in seconds and in log positions', 'Lag versus retention (the metric that predicts a re-bootstrap)',
       'Rows per second by table', 'Schema rejection count', 'Bootstrap progress and estimated completion'],
  sec=['The stream contains every row of the source: encrypt in transit and at rest, and apply the source\'s access controls to '
       'the stream. A CDC pipeline is a very effective accidental data-exfiltration path.',
       'Redact or tokenise sensitive columns at the connector, not downstream.'],
  cost='Storage in the log (retention × volume) and the destination write amplification. Retention is the lever and also the risk: '
       'short retention is cheap until a consumer falls behind.',
  trade=[('Log tailing vs polling', 'Correctness and low source impact versus implementation complexity'),
         ('Per-key vs transactional order', 'Throughput versus cross-table consistency'),
         ('Retention', 'Cost versus the ability to recover a lagging consumer without a re-bootstrap'),
         ('Duplicates', 'At-least-once plus idempotent consumers, versus a freeze window')],
  evolve='Phase 1: one source type, per-key ordering, idempotent destinations. Phase 2: bootstrap plus overlap. Phase 3: schema '
         'registry with compatibility enforcement, then multi-destination fan-out.',
  senior='"Poll the database for changed rows and publish them to Kafka."',
  staff='"Polling misses deletes and scans the source, so I would tail the replication log and key by primary key for per-key '
        'order — accepting that cross-table transaction order does not survive partitioning, and exposing transaction ids for the '
        'consumers that need it. Bootstrap snapshots at a log position and replays from it, which means duplicates, which means '
        'destinations must upsert. That is the same copy-then-catch-up shape as migrating a live tenant."'),

 dict(id='olap', title='Design a real-time OLAP serving store (Pinot-like)', topic='Analytics · Serving', prio='p1',
  why='Pinot came out of LinkedIn and powers member-facing analytics ("who viewed your profile"). It is the design where '
      '**user-facing latency meets analytical queries** — a genuinely different problem from a data warehouse.',
  ask=['Are these user-facing queries (tens of milliseconds) or analyst queries (seconds are fine)?',
       'What query shapes — filters, group-by and aggregations, or arbitrary joins?',
       'How fresh must the data be: seconds after the event, or next hour?',
       'Retention and cardinality: how many distinct dimension values?',
       'Query concurrency — a dashboard for 50 analysts, or a feature for 50 million members?'],
  fr=['Ingest from a stream and from batch', 'Filter, group and aggregate over billions of rows',
      'Serve queries at interactive latency', 'Support retention and rollup'],
  nfr=['p99 query latency in tens of milliseconds for user-facing queries', 'Freshness of seconds for streaming data',
       'Thousands of concurrent queries', 'Predictable cost per query'],
  scale='10 billion rows × 200 bytes = 2 TB raw; columnar compression and dictionary encoding typically cut that several-fold. '
        '10,000 queries/s at 20 ms each means ~200 concurrent queries — so the design is about bounding the work per query, not '
        'about raw storage.',
  api='SQL-like: `SELECT dim, COUNT(*) FROM table WHERE ts > ? AND filter = ? GROUP BY dim LIMIT 10`. Plus an ingestion spec '
      '(schema, time column, indexes, rollup) and a segment lifecycle API.',
  data='**Columnar segments**: immutable, time-partitioned files with per-column dictionary encoding, inverted indexes on '
       'high-selectivity dimensions, sorted columns for range pruning, and star-tree or pre-aggregated indexes for common group-bys.',
  arch='''Two ingestion paths meeting in one query path:

- **Real-time**: consume the stream, build an in-memory segment, and periodically seal and persist it.
- **Offline**: batch jobs build segments and push them in, often replacing the real-time segments for the same period (the '
"lambda seam" — backfills and corrections land here).

**Query**: broker receives the query, prunes segments by time and by metadata, scatters to servers holding the relevant segments, '
gathers and merges. Pruning is where the latency is won or lost.''',
  deep=['**Segment pruning.** Time partitioning plus per-segment min/max metadata means a query touching one day hits a handful of '
        'segments instead of thousands. Without pruning, nothing else matters.',
        '**Index choice per column.** Inverted for high-selectivity filters, sorted for range scans (only one column can be sorted), '
        'star-tree for pre-aggregated group-bys at a storage cost. This per-column decision is the heart of the design.',
        '**Real-time and offline overlap.** The same period exists in both; the broker must pick one, and hand-off must be atomic or '
        'you double-count. Say how you would detect double counting (a canary query with a known answer).',
        '**High cardinality.** A group-by over millions of distinct values cannot be served in 20 ms — cap it, pre-aggregate it, or '
        'refuse it. Knowing what to refuse is a Staff answer.',
        '**Upserts.** Analytics stores are append-first; supporting updates means a primary key index and last-value-wins per key, '
        'which costs memory. Only add it if the product needs it.'],
  fails=['A server dies → replicas of its segments serve; queries degrade in latency, not correctness.',
         'Stream ingestion stalls → freshness drops; alarm on the newest-row age, not just on consumer lag.',
         'A query that scans everything → per-query time and row budgets, and kill it; one bad dashboard should not take the tier down.',
         'Batch push of a corrupt segment → validate before it becomes queryable, and keep the previous version for rollback.'],
  scaling=['Replicate segments for query concurrency; partition for data volume.',
           'Isolate tenants or query classes onto separate server pools so an analyst query cannot hurt a member-facing one.',
           'Tier by age: recent data on fast servers, old data on cheaper storage with worse latency.'],
  obs=['p99 per query class, segments scanned per query (the leading indicator), newest-row age',
       'Queries killed by budget', 'Segment build and push failures', 'Replica skew'],
  sec=['Row-level filtering by tenant or member must be applied inside the query plan, not by the caller.',
       'Analytics data is often personal data in aggregate form — retention and deletion requests still apply.'],
  cost='Memory and replicas dominate for user-facing latency. The lever is index and rollup choice: a star-tree index can cut query '
       'cost by an order of magnitude at some storage cost, and pre-aggregation can remove whole query classes.',
  trade=[('Index richness', 'Query speed versus storage and build time'),
         ('Real-time vs offline', 'Freshness versus correctness and reprocessing simplicity'),
         ('Pre-aggregation', 'Latency versus flexibility — you can only answer what you pre-computed'),
         ('Upserts', 'Product capability versus memory and complexity')],
  evolve='Phase 1: offline segments, time partitioning, inverted indexes on the obvious filters. Phase 2: real-time ingestion with '
         'hand-off. Phase 3: star-tree for the hot group-bys, then tiering by age. Add upserts last, and only if forced.',
  senior='"Put the events in a data warehouse and query them."',
  staff='"A warehouse answers in seconds, and this is a member-facing feature with a twenty-millisecond budget, so the design is '
        'columnar segments with aggressive pruning and per-column index choices — and the honest part is deciding which queries we '
        'refuse to serve. Real-time and offline segments overlapping for the same period is where double counting creeps in, so I '
        'would have a canary query with a known answer running continuously."'),

 dict(id='coordination', title='Design coordination: leader election, locks and membership', topic='Consensus · Primitives', prio='p1',
  why='Every other infrastructure design leans on this, and interviewers drill into it when you say "a coordination service '
      'handles that". It is also where fencing tokens live — the concept that separates correct locking from folklore.',
  ask=['What is actually needed — mutual exclusion, leader election, membership, or config distribution?',
       'What happens if two processes believe they hold the lock? (Is it a performance problem or a correctness problem?)',
       'How long may a failover take?',
       'How many participants, and how often does leadership change?',
       'Is this a shared service for hundreds of teams, or embedded in one system?'],
  fr=['Elect a single leader per resource, with automatic failover', 'Distributed mutual exclusion with expiry',
      'Membership: who is alive right now', 'Watches: notify participants on change', 'Small, strongly consistent config storage'],
  nfr=['Linearizable reads and writes for the critical metadata', 'Failover within seconds',
       'Survive the loss of a minority of nodes', 'A client\'s pause must never cause two active leaders'],
  scale='This is deliberately small and slow: a 3- or 5-node consensus group, thousands of writes per second at most, holding '
        'megabytes. Say that explicitly — the failure mode of coordination services is people putting hot data in them.',
  api='`Campaign(resource, ttl)` → leadership with a **fencing token**; `Renew`, `Resign`; `Acquire(lock, ttl)` → token; '
      '`Members(group)` with watches; `Get/Put(key, ifVersion)` with linearizable reads.',
  data='A replicated log via Raft: a leader appends, a majority acknowledges, entries commit in order. State is a small key-value '
       'tree with versions, plus ephemeral entries tied to sessions for liveness.',
  arch='''Raft group of 3 or 5 nodes (odd, to make majorities unambiguous). Clients hold sessions with heartbeats; ephemeral keys '
disappear when a session lapses, which is how membership and leader leases expire without a human.

**Leader election** is "create an ephemeral key, lowest sequence wins, watch your predecessor" — which avoids the herd of everyone '
watching one key.

**Every grant carries a monotonically increasing fencing token**, and downstream resources must reject tokens older than the '
highest they have seen.''',
  deep=['**Fencing tokens are the whole answer.** A lock with a TTL is not mutual exclusion: the holder can pause (GC, VM freeze), '
        'the lease can expire, a second holder can be granted, and then the first wakes up and writes. Only the resource rejecting '
        'stale tokens makes this safe. If you say nothing else in this question, say this.',
        '**Why an odd number.** Majority quorum: 3 nodes tolerate 1 failure, 5 tolerate 2. Adding a fourth node does not improve '
        'fault tolerance and slows commits.',
        '**Sessions and heartbeats.** The trade-off between failover speed and false positives: a 2-second session means fast '
        'failover and spurious leadership churn under GC pauses; 30 seconds is stable and slow. Say which side you would pick and why.',
        '**Watch storms.** Thousands of clients watching one key means a thundering herd on every change. Sequence-and-watch-your-'
        'predecessor is the fix.',
        '**What must not live here.** Not queues, not per-request state, not anything high-throughput. Coordination services fall '
        'over because someone stored data in them — a boundary you should state as an operating rule.'],
  fails=['Minority nodes lost → the group continues; latency may rise.',
         'Majority lost → no writes at all; the system is unavailable by design. This is correct behaviour, and every dependent '
         'service should degrade rather than pretend.',
         'Client GC pause → its session expires, leadership moves, its writes are fenced off.',
         'Network partition → only the majority side can elect a leader; the minority side must stop, not guess.',
         'Clock skew → Raft does not depend on synchronised clocks for safety, only leases do; if you use leases, bound the skew '
         'assumption explicitly.'],
  scaling=['Do not scale it — shard the users. One group per domain rather than one global group.',
           'Read-heavy workloads: followers can serve linearizable reads with a read index, or stale reads if the caller opts in.',
           'Cache config locally with a watch and a version, so a coordination blip does not stop the data path.'],
  obs=['Leader elections per hour (churn is the health signal)', 'Commit latency p99', 'Session expiry rate',
       'Watch count and notification fan-out', 'Data size — alarm when it grows, because that means misuse'],
  sec=['Coordination holds the keys to the kingdom: strong authentication between members, ACLs per path, and full audit of writes.',
       'A compromised coordination service means an attacker can redirect every dependent system.'],
  cost='Tiny in resources, expensive in blast radius. The real cost argument is operational: every dependent service inherits its '
       'availability, so the case for embedding Raft in one system versus running a shared service is about coupling, not money.',
  trade=[('Shared service vs embedded', 'Operational economy versus a shared failure domain for everything that uses it'),
         ('Session timeout', 'Failover speed versus leadership churn under pauses'),
         ('Linearizable reads', 'Correctness versus a round trip; stale reads are fine for some callers if they opt in'),
         ('Lease-based locks', 'Simplicity versus needing fencing tokens to be actually safe')],
  evolve='Phase 1: embed a Raft library for the one system that needs it. Phase 2: extract a shared service once three systems need '
         'it, with quotas and per-team paths. Phase 3: local caching with watches so the data path survives coordination outages. '
         'The rule that keeps it healthy: the data path must degrade, never stop, when coordination is unavailable.',
  senior='"Use ZooKeeper for leader election and distributed locks."',
  staff='"A lease-based lock alone is not mutual exclusion — a GC pause at the wrong moment gives you two holders. So every grant '
        'carries a fencing token and the protected resource rejects stale tokens; that is what makes it correct. I would also keep '
        'the coordination group small and boring, cache its state locally with watches, and make sure a coordination outage degrades '
        'the data path rather than stopping it."'),
]
