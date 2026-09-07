# DDIA — Working Reference

Navigation and synthesis notes for *Designing Data-Intensive Applications* (Martin
Kleppmann, 1st ed, 613 pp), used as the source for enriching
`Distributed_Systems_Deep_Guide.html`.

## What this file is — and is not

**It is not a copy of the book.** It contains no reproduced passages. Two things only:

1. **A structural index** — every section heading with its line number in a text
   extraction of *your own* copy, so a future session can jump straight to any topic
   instead of paging through a 613-page PDF.
2. **My own synthesis notes** — what each chapter argues, in my words, plus how it maps
   into the guide and what has already been used.

To use the index you must regenerate the extraction from your own PDF:

```bash
pdftotext -layout "Designing Data Intensive Applications by Martin Kleppmann.pdf" ddia.txt
wc -l ddia.txt        # expect ~23,854 lines — if it differs, line numbers below will drift
```

Then read any section directly:

```bash
sed -n '1019,1230p' ddia.txt      # Ch 7: Write Skew and Phantoms
sed -n '10679,12579p' ddia.txt    # all of Ch 8
```

Line numbers assume `pdftotext -layout` on the 1st edition. **Verify the total line count
matches before trusting them**; a different edition or extraction flag will shift everything.

---

## Priority for a Google L6 interview

| Tier | Chapters | Why |
|---|---|---|
| **Load-bearing** | 5, 6, 8, 9 | Replication, partitioning, the failure model, and consensus. Nearly every design question touches these. |
| **High** | 3, 7 | Storage engines explain *why* a database behaves as it does. Transactions cover every booking/payment/inventory problem. |
| **Useful** | 1, 4 | Percentiles and load parameters make you sound like you have operated systems. Encoding matters for zero-downtime deploys. |
| **Context** | 2 | Data models. Important but rarely the crux of an interview question. |
| **Out of original scope** | 10, 11, 12 | Batch and stream processing, derived data. Ch 11 is the natural source if guide `ch11` gets enriched. |

---

## The book's argument in four sentences

Chapters 1–4 build an abstraction: a data system with a model, a storage engine, and a way
to evolve. Chapters 5–7 distribute it and try to keep the guarantees. Chapter 8 demolishes
the assumptions those guarantees rested on — the network is asynchronous, clocks lie, and
processes pause arbitrarily. Chapter 9 prices the recovery: coordination costs a majority
quorum and a round trip, and the engineering skill is buying as little of it as possible.

**The single most useful result in the book** is the equivalence in Ch 9: consensus, total
order broadcast, linearizable compare-and-set, and leader election are one problem. That
turns the vague question *"do we need consensus?"* into the answerable *"do we need a total
order?"*

---

## Chapter synthesis notes

Each entry: what the chapter argues, the mental models worth carrying, and its status in
the guide. All wording here is my own synthesis, not the book's text.

### Ch 1 — Reliable, Scalable, Maintainable
**Argument:** three non-functional goals, each made measurable. Reliability is about
tolerating *faults* so they never become *failures*. Scalability is not a property but a
question — which load parameter grows, by how much, holding which metric. Maintainability
splits into operability, simplicity (removing *accidental* complexity), and evolvability.

**Carry:** faults are inevitable and mostly not hardware — correlated software bugs and
human config error cause the big outages, and redundancy helps with neither. Percentiles,
never means. Load parameters are usually *distributions* (followers per user), not averages.
Tail latency amplification: 100 parallel calls at 1% slow each ⇒ 63% slow pages.

**Status:** used. Faults → guide `ch1`; percentiles and load parameters → guide `ch14`.

### Ch 2 — Data Models and Query Languages
**Argument:** the relationship shape picks the model. Self-contained one-to-many trees suit
documents (locality — one read instead of a join). Many-to-one and many-to-many suit
relational. Dense arbitrary connections suit graphs. Also: declarative query languages
survive because they let the engine improve underneath you.

**Carry:** "schemaless" really means schema-on-read — the schema still exists, it just lives
implicitly in every reader. Document locality only pays while you load most of the document.
The models have largely converged (JSONB in Postgres, transactions in MongoDB).

**Status:** used. Folded into the front of guide `ch12`.

### Ch 3 — Storage and Retrieval
**Argument:** the two storage-engine families and why each exists. Log-structured (hash
index → SSTables → LSM-trees, memtables, compaction, Bloom filters) turns random writes into
sequential ones. B-trees update pages in place, giving bounded predictable reads. Second
half: OLTP and OLAP diverge, which motivates column-oriented storage and compression.

**Carry:** trace one write and one read end to end and you understand storage engines. LSM
does not do less work — it defers work into compaction, where it becomes an operational
concern. Column stores win twice: read fewer columns, and compress better because a column
is homogeneous. Note the trap: Cassandra/HBase "column families" are *not* column-oriented.

**Status:** used. Guide `ch12` — write/read traces, amplification, OLAP, column stores.

### Ch 4 — Encoding and Evolution
**Argument:** in any system that deploys gradually, old and new code run at once and old and
new data coexist. That forces backward compatibility (new code reads old data) *and* forward
compatibility (old code reads new data). Formats: JSON/XML, Thrift, Protocol Buffers, Avro.
Then three dataflow modes — through databases, services, and async messages.

**Carry:** field *numbers* rather than names are what make binary formats evolvable, and a
field number is permanent — reusing one silently corrupts old data. Rollback needs the
harder direction of compatibility and is the case everyone forgets. Data outlives code, so
a read-modify-write by old code must not drop unknown fields.

**Status:** used. Guide `ch15` — formats, compatibility directions, expand/contract migration.

### Ch 5 — Replication  ★ load-bearing
**Argument:** three topologies — single-leader, multi-leader, leaderless — and the problems
each creates. Sync vs async. How the replication log is actually shipped (statement, WAL,
logical row-based, trigger). Replication lag produces three named anomalies. Leaderless
brings quorums, sloppy quorums, hinted handoff, read repair, anti-entropy.

**Carry:** the three anomalies by name — read-after-write, monotonic reads, consistent prefix
reads. `W + R > N` is a probability dial, not a guarantee (sloppy quorums void it; concurrent
writes are ambiguous; a rebuilt replica can retroactively break it). Logical logs are what
allow zero-downtime version upgrades and make CDC possible. Snapshot + log position is the
universal pattern for copying moving data.

**Status:** used heavily. Guide `ch4` (1,207 → 5,401 words).

### Ch 6 — Partitioning  ★ load-bearing
**Argument:** key-range vs hash partitioning, skew and hot spots, secondary indexes
(document-partitioned/local vs term-partitioned/global), rebalancing strategies, request
routing, and parallel query.

**Carry:** the local-vs-global secondary index choice is near-irreversible — local means
cheap writes and scatter/gather reads; global means fast reads and distributed (usually
asynchronous) writes. `hash mod N` relocates ~90% of keys when N changes. A hot key is not
fixed by adding shards. Automatic rebalancing plus automatic failure detection is a
cascading-failure generator. Routing secretly depends on consensus.

**Status:** used. Guide `ch5` (1,037 → 3,208 words).

### Ch 7 — Transactions  ★ high
**Argument:** ACID precisely (atomicity means *abortability*; consistency is the
application's job). Then the weak isolation levels and exactly which anomaly each permits:
dirty reads/writes, read skew, lost update, write skew, phantoms. Then the three routes to
serializability — actual serial execution, two-phase locking, and serializable snapshot
isolation.

**Carry:** write skew is the anomaly snapshot isolation cannot stop, and its shape is
*read → decide → write* where the write invalidates the premise. Phantoms defeat
`SELECT FOR UPDATE` because you cannot lock rows that do not exist. Materializing conflicts
is the workaround; true serializability is the real fix. SSI is optimistic and collapses
under high contention on one hot row.

**Status:** used heavily. Guide `ch7` (809 → 5,010 words) — the whole isolation foundation
was missing and now sits *before* the 2PC content.

### Ch 8 — The Trouble with Distributed Systems  ★ load-bearing
**Argument:** the refutation chapter. Unreliable networks, unreliable clocks, and unbounded
process pauses mean you cannot distinguish slow from dead. Ends with system models
(synchronous / partially synchronous / asynchronous; crash-stop / crash-recovery /
Byzantine) and the rule that truth is defined by the majority.

**Carry:** two clocks — monotonic for durations, time-of-day for calendar times; subtracting
wall-clock timestamps is a latent bug. A process cannot detect its own pause, so any
"check then act" has an unbounded gap. Fencing tokens are the fix, and **must be enforced at
the resource** — client-side checking is worthless. Timestamps are intervals, not points.

**Carry the meta-lesson:** do not try to stop the stale actor from acting. Make its action
harmless. Idempotency and fencing are both instances of this.

**Status:** used. Guide `ch8` (757 → 2,935 words) and parts into `ch1`.

### Ch 9 — Consistency and Consensus  ★ load-bearing
**Argument:** linearizability (what it is, how to implement it, what it costs), then ordering
and causality, then consensus. The chapter's spine: replication → ordering → causality →
total order → consensus → leader election → linearizable storage.

**Carry:** linearizability is a *total* order plus real time; causality is a *partial* order,
so concurrency is a well-defined outcome rather than a gap. Linearizability implies causality
but costs latency **always**, not just during partitions — and there is a proof that response
time is bounded below by network delay uncertainty. Multi-core RAM is not linearizable, which
shows the usual motive is speed, not fault tolerance. Causal consistency is the strongest
model that stays fast and available. Lamport timestamps order causally but lack *finality*,
so they cannot enforce a constraint under faults.

**The key result:** consensus ≡ total order broadcast ≡ linearizable compare-and-set ≡ leader
election. Solve one, get all four.

**Status:** used. Guide `ch2` (ordering/causality), `ch3` (cost of linearizability),
`ch6` (the equivalence, epochs, cost of consensus).

### Ch 10 — Batch Processing  ○ not used
MapReduce, the Unix philosophy applied to data, joins in batch context, dataflow engines.
Would strengthen guide `ch12` if derived-data pipelines are ever expanded.

### Ch 11 — Stream Processing  ○ not used — **the natural source for guide `ch11`**
Event streams and message brokers, partitioned logs, change data capture, event sourcing,
processing time vs event time, windowing, stream joins, and fault tolerance
(microbatching, idempotence, exactly-once). Guide `ch11` (Message Queues & Streaming) is
still at original depth and this is where its enrichment should come from.

### Ch 12 — The Future of Data Systems  ○ not used
Derived data, unbundling the database, the "one source of truth, many read models" framing.
Would strengthen the CQRS / materialised-view material in guide `ch12`.

---

## Concepts already promoted into the guide's glossary

The 181-term glossary in `Distributed_Systems_Deep_Guide.html` already covers the DDIA
vocabulary. Notable entries and their slugs:

`partial-failure` `two-generals` `flp-impossibility` `byzantine-fault` `fail-stop`
`linearizability` `causal-consistency` `read-your-writes` `monotonic-reads`
`serializability` `snapshot-isolation` `write-skew` `phantom-read` `mvcc`
`two-phase-locking` `optimistic-concurrency-control` `quorum` `sloppy-quorum`
`hinted-handoff` `read-repair` `anti-entropy` `merkle-tree` `crdt` `last-write-wins`
`leader-follower-replication` `multi-leader-replication` `leaderless-replication`
`replication-lag` `consistent-hashing` `hash-partitioning` `range-partitioning`
`partition-key` `hot-key` `rebalancing` `secondary-index` `scatter-gather`
`consensus` `raft` `paxos` `leader-election` `fencing-token` `lease` `split-brain`
`two-phase-commit` `saga` `outbox-pattern` `change-data-capture` `dual-write`
`clock-skew` `lamport-clock` `vector-clock` `happens-before` `hybrid-logical-clock`
`truetime` `b-tree` `lsm-tree` `sstable` `memtable` `compaction` `wal` `fsync`
`write-amplification` `read-amplification` `bloom-filter` `tail-latency` `slo`

To add a term, edit the `GLOSSARY` object in the first `<script>` block — inline links
regenerate automatically. See `CLAUDE.md` §4.

---

## Structural index — every section, with line numbers

Line numbers refer to `ddia.txt` produced by the `pdftotext -layout` command above.

### Ch 1 — Reliable, Scalable, Maintainable Applications

`lines 606–1501`  ·  `sed -n '606,1501p' ddia.txt`

| line | section |
|---|---|
| `658` | Thinking About Data Systems |
| `707` | Reliability |
| `711` | Scalability |
| `714` | Maintainability |
| `725` | Reliability |
| `769` | Hardware Faults |
| `809` | Software Errors |
| `852` | Human Errors |
| `907` | Scalability |
| `923` | Describing Load |
| `934` | Post tweet |
| `937` | Home timeline |
| `1009` | Describing Performance |
| `1160` | Approaches for Coping with Load |
| `1218` | Maintainability |
| `1235` | Operability |
| `1237` | Simplicity |
| `1241` | Evolvability |
| `1371` | Summary |
| `1410` | References |

### Ch 2 — Data Models and Query Languages

`lines 1502–3167`  ·  `sed -n '1502,3167p' ddia.txt`

| line | section |
|---|---|
| `1555` | Relational Model Versus Document Model |
| `1589` | The Birth of NoSQL |
| `1613` | The Object-Relational Mismatch |
| `1781` | Organizations and schools as entities |
| `1788` | Recommendations |
| `1848` | The network model |
| `1883` | The relational model |
| `1919` | Comparison to document databases |
| `1931` | Relational Versus Document Databases Today |
| `1974` | Schema flexibility in the document model |
| `2042` | Data locality for queries |
| `2067` | Convergence of document and relational databases |
| `2092` | Query Languages for Data |
| `2255` | MapReduce Querying |
| `2400` | Social graphs |
| `2402` | The web graph |
| `2404` | Road or rail networks |
| `2439` | Property Graphs |
| `2465` | CREATE TABLE vertices ( |
| `2470` | CREATE TABLE edges ( |
| `2513` | The Cypher Query Language |
| `2525` | CREATE |
| `2549` | MATCH |
| `2579` | Graph Queries in SQL |
| `2606` | WITH RECURSIVE |
| `2645` | FROM vertices |
| `2672` | Triple-Stores and SPARQL |
| `2736` | The semantic web |
| `2757` | The RDF data model |
| `2990` | Summary |
| `3046` | References |

### Ch 3 — Storage and Retrieval

`lines 3168–4677`  ·  `sed -n '3168,4677p' ddia.txt`

| line | section |
|---|---|
| `3205` | Data Structures That Power Your Database |
| `3370` | File format |
| `3374` | Deleting records |
| `3379` | Crash recovery |
| `3391` | Partially written records |
| `3395` | Concurrency control |
| `3527` | Making an LSM-tree out of SSTables |
| `3551` | Performance optimizations |
| `3576` | B-Trees |
| `3678` | B-tree optimizations |
| `3711` | Comparing B-Trees and LSM-Trees |
| `3767` | Downsides of LSM-trees |
| `3805` | Other Indexing Structures |
| `3827` | Storing values within the index |
| `3864` | Multi-column indexes |
| `3908` | Full-text search and fuzzy indexes |
| `3931` | Keeping everything in memory |
| `4051` | Data Warehousing |
| `4105` | The divergence between OLTP databases and data warehouses |
| `4185` | Column-Oriented Storage |
| `4203` | SELECT |
| `4209` | WHERE |
| `4212` | GROUP BY |
| `4248` | Column Compression |
| `4299` | Memory bandwidth and vectorized processing |
| `4317` | Sort Order in Column Storage |
| `4352` | Several different sort orders |
| `4449` | Summary |
| `4503` | References |

### Ch 4 — Encoding and Evolution

`lines 4678–6058`  ·  `sed -n '4678,6058p' ddia.txt`

| line | section |
|---|---|
| `4723` | Backward compatibility |
| `4725` | Forward compatibility |
| `4740` | Formats for Encoding Data |
| `4770` | Language-Specific Formats |
| `4809` | JSON, XML, and Binary Variants |
| `4864` | Binary encoding |
| `4927` | Thrift and Protocol Buffers |
| `5015` | Field tags and schema evolution |
| `5050` | Datatypes and schema evolution |
| `5153` | Schema evolution rules |
| `5196` | Large file with lots of records |
| `5202` | Database with individually written records |
| `5220` | Sending records over a network connection |
| `5230` | Dynamically generated schemas |
| `5261` | Code generation and dynamically typed languages |
| `5284` | The Merits of Schemas |
| `5327` | Modes of Dataflow |
| `5351` | Dataflow Through Databases |
| `5387` | Different values written at different times |
| `5417` | Archival storage |
| `5478` | Web services |
| `5604` | Current directions for RPC |
| `5636` | Data encoding and evolution for RPC |
| `5668` | Message-Passing Dataflow |
| `5703` | Message brokers |
| `5730` | Distributed actor frameworks |
| `5775` | Summary |
| `5826` | References |
| `5959` | Scalability |
| `5962` | Fault tolerance/high availability |
| `5966` | Latency |
| `5992` | Shared-Nothing Architectures |
| `6024` | Replication Versus Partitioning |
| `6026` | Replication |
| `6031` | Partitioning |
| `6049` | References |

### Ch 5 — Replication

`lines 6059–7872`  ·  `sed -n '6059,7872p' ddia.txt`

| line | section |
|---|---|
| `6110` | Leaders and Followers |
| `6157` | Synchronous Versus Asynchronous Replication |
| `6232` | Setting Up New Followers |
| `6267` | Handling Node Outages |
| `6362` | Implementation of Replication Logs |
| `6366` | Statement-based replication |
| `6406` | Write-ahead log (WAL) shipping |
| `6438` | Logical (row-based) log replication |
| `6468` | Trigger-based replication |
| `6489` | Problems with Replication Lag |
| `6527` | Reading Your Own Writes |
| `6610` | Monotonic Reads |
| `6645` | Consistent Prefix Reads |
| `6693` | Solutions for Replication Lag |
| `6734` | Use Cases for Multi-Leader Replication |
| `6739` | Multi-datacenter operation |
| `6762` | Performance |
| `6770` | Tolerance of datacenter outages |
| `6775` | Tolerance of network problems |
| `6800` | Clients with offline operation |
| `6821` | Collaborative editing |
| `6844` | Handling Write Conflicts |
| `6876` | Conflict avoidance |
| `6892` | Converging toward a consistent state |
| `6927` | Custom conflict resolution logic |
| `6931` | On write |
| `6936` | On read |
| `6998` | Multi-Leader Replication Topologies |
| `7074` | Leaderless Replication |
| `7094` | Writing to the Database When a Node Is Down |
| `7129` | Read repair and anti-entropy |
| `7137` | Read repair |
| `7143` | Anti-entropy process |
| `7154` | Quorums for reading and writing |
| `7222` | Limitations of Quorum Consistency |
| `7284` | Monitoring staleness |
| `7311` | Sloppy Quorums and Hinted Handoff |
| `7358` | Multi-datacenter operation |
| `7377` | Detecting Concurrent Writes |
| `7499` | Capturing the happens-before relationship |
| `7589` | Merging concurrently written values |
| `7622` | Version vectors |
| `7657` | High availability |
| `7660` | Disconnected operation |
| `7663` | Latency |
| `7665` | Scalability |
| `7675` | Single-leader replication |
| `7679` | Multi-leader replication |
| `7683` | Leaderless replication |
| `7704` | Read-after-write consistency |
| `7706` | Monotonic reads |
| `7709` | Consistent prefix reads |
| `7723` | References |

### Ch 6 — Partitioning

`lines 7873–8645`  ·  `sed -n '7873,8645p' ddia.txt`

| line | section |
|---|---|
| `7929` | Partitioning and Replication |
| `7951` | Partitioning of Key-Value Data |
| `8025` | Partitioning by Hash of Key |
| `8090` | Skewed Workloads and Relieving Hot Spots |
| `8141` | Partitioning Secondary Indexes by Document |
| `8197` | Partitioning Secondary Indexes by Term |
| `8242` | Rebalancing Partitions |
| `8289` | Fixed number of partitions |
| `8372` | Partitioning proportionally to nodes |
| `8431` | Request Routing |
| `8503` | Parallel Query Execution |
| `8519` | Summary |
| `8576` | References |

### Ch 7 — Transactions

`lines 8646–10678`  ·  `sed -n '8646,10678p' ddia.txt`

| line | section |
|---|---|
| `8714` | The Slippery Concept of a Transaction |
| `8742` | The Meaning of ACID |
| `8760` | Atomicity |
| `8791` | Consistency |
| `8825` | Isolation |
| `8861` | Durability |
| `8925` | Atomicity |
| `8930` | Isolation |
| `8998` | Single-object writes |
| `9074` | Handling errors and aborts |
| `9167` | Read Committed |
| `9178` | No dirty reads |
| `9216` | No dirty writes |
| `9250` | Implementing read committed |
| `9284` | Snapshot Isolation and Repeatable Read |
| `9332` | Backups |
| `9339` | Analytic queries and integrity checks |
| `9362` | Implementing snapshot isolation |
| `9413` | Visibility rules for observing a consistent snapshot |
| `9452` | Indexes and snapshot isolation |
| `9477` | Repeatable read and naming confusion |
| `9497` | Preventing Lost Updates |
| `9527` | Atomic write operations |
| `9559` | Explicit locking |
| `9613` | Compare-and-set |
| `9664` | Write Skew and Phantoms |
| `9699` | Characterizing write skew |
| `9756` | Meeting room booking system |
| `9782` | Multiplayer game |
| `9806` | Preventing double-spending |
| `9814` | Phantoms causing write skew |
| `9854` | Materializing conflicts |
| `9874` | Serializability |
| `9919` | Actual Serial Execution |
| `9953` | Encapsulating transactions in stored procedures |
| `10034` | Partitioning |
| `10063` | Summary of serial execution |
| `10120` | Implementation of two-phase locking |
| `10159` | Performance of two-phase locking |
| `10189` | Predicate locks |
| `10228` | Index-range locks |
| `10268` | Serializable Snapshot Isolation (SSI) |
| `10285` | Pessimistic versus optimistic concurrency control |
| `10326` | Decisions based on an outdated premise |
| `10356` | Detecting stale MVCC reads |
| `10389` | Detecting writes that affect prior reads |
| `10423` | Performance of serializable snapshot isolation |
| `10455` | Summary |
| `10474` | Dirty reads |
| `10477` | Dirty writes |
| `10480` | Read skew (nonrepeatable reads) |
| `10495` | Write skew |
| `10500` | Phantom reads |
| `10509` | Literally executing transactions in a serial order |
| `10513` | Two-phase locking |
| `10516` | Serializable snapshot isolation (SSI) |

### Ch 8 — The Trouble with Distributed Systems

`lines 10679–12579`  ·  `sed -n '10679,12579p' ddia.txt`

| line | section |
|---|---|
| `10730` | Faults and Partial Failures |
| `10777` | Cloud Computing and Supercomputing |
| `10884` | Unreliable Networks |
| `10941` | Network Faults in Practice |
| `10989` | Detecting Faults |
| `11038` | Timeouts and Unbounded Delays |
| `11077` | Network congestion and queueing |
| `11162` | Synchronous Versus Asynchronous Networks |
| `11277` | Unreliable Clocks |
| `11320` | Monotonic Versus Time-of-Day Clocks |
| `11325` | Time-of-day clocks |
| `11343` | Monotonic clocks |
| `11381` | Clock Synchronization and Accuracy |
| `11448` | Relying on Synchronized Clocks |
| `11472` | Timestamps for ordering events |
| `11543` | Clock readings have a confidence interval |
| `11578` | Synchronized clocks for global snapshots |
| `11624` | Process Pauses |
| `11748` | Response time guarantees |
| `11793` | Limiting the impact of garbage collection |
| `11846` | The Truth Is Defined by the Majority |
| `11892` | The leader and the lock |
| `11981` | Byzantine Faults |
| `12070` | Weak forms of lying |
| `12097` | System Model and Reality |
| `12110` | Synchronous model |
| `12117` | Partially synchronous model |
| `12125` | Asynchronous model |
| `12131` | Crash-stop faults |
| `12136` | Crash-recovery faults |
| `12141` | Byzantine (arbitrary) faults |
| `12151` | Correctness of an algorithm |
| `12161` | Uniqueness |
| `12163` | Monotonic sequence |
| `12166` | Availability |
| `12174` | Safety and liveness |
| `12211` | Mapping system models to the real world |
| `12250` | Summary |
| `12323` | References |

### Ch 9 — Consistency and Consensus

`lines 12580–15220`  ·  `sed -n '12580,15220p' ddia.txt`

| line | section |
|---|---|
| `12640` | Consistency Guarantees |
| `12934` | Locking and leader election |
| `12956` | Constraints and uniqueness guarantees |
| `12992` | Cross-channel timing dependencies |
| `13034` | Implementing Linearizable Systems |
| `13050` | Single-leader replication (potentially linearizable) |
| `13065` | Consensus algorithms (linearizable) |
| `13071` | Multi-leader replication (not linearizable) |
| `13077` | Leaderless replication (probably not linearizable) |
| `13102` | Linearizability and quorums |
| `13139` | The Cost of Linearizability |
| `13176` | The CAP theorem |
| `13254` | Linearizability and network delays |
| `13319` | Ordering and Causality |
| `13383` | The causal order is not a total order |
| `13395` | Linearizability |
| `13400` | Causality |
| `13426` | Linearizability is stronger than causal consistency |
| `13456` | Capturing causal dependencies |
| `13489` | Sequence Number Ordering |
| `13523` | Noncausal sequence number generators |
| `13578` | Lamport timestamps |
| `13636` | Timestamp ordering is not sufficient |
| `13677` | Total Order Broadcast |
| `13701` | Reliable delivery |
| `13704` | Totally ordered delivery |
| `13722` | Using total order broadcast |
| `13825` | Implementing total order broadcast using linearizable storage |
| `13859` | Distributed Transactions and Consensus |
| `13874` | Leader election |
| `13947` | From single-node to distributed atomic commit |
| `14002` | Introduction to two-phase commit |
| `14055` | A system of promises |
| `14113` | Coordinator failure |
| `14151` | Three-phase commit |
| `14186` | Database-internal distributed transactions |
| `14192` | Heterogeneous distributed transactions |
| `14204` | Exactly-once message processing |
| `14231` | XA transactions |
| `14270` | Holding locks while in doubt |
| `14322` | Limitations of distributed transactions |
| `14365` | Fault-Tolerant Consensus |
| `14382` | Uniform agreement |
| `14384` | Integrity |
| `14386` | Validity |
| `14388` | Termination |
| `14443` | Consensus algorithms and total order broadcast |
| `14478` | Single-leader replication and consensus |
| `14617` | Linearizable atomic operations |
| `14624` | Total ordering of operations |
| `14644` | Change notifications |
| `14655` | Allocating work to nodes |
| `14693` | Service discovery |
| `14715` | Membership services |
| `14734` | Summary |
| `14767` | Atomic transaction commit |
| `14769` | Total order broadcast |
| `14771` | Locks and leases |
| `14774` | Membership/coordination service |
| `14777` | Uniqueness constraint |
| `14840` | References |
| `15185` | Systems of record |
| `15191` | Derived data systems |

### Ch 10 — Batch Processing

`lines 15221–17199`  ·  `sed -n '15221,17199p' ddia.txt`

| line | section |
|---|---|
| `15246` | Services (online systems) |
| `15265` | Stream processing systems (near-real-time systems) |
| `15303` | Batch Processing with Unix Tools |
| `15323` | Simple Log Analysis |
| `15379` | Chain of commands versus custom program |
| `15416` | Sorting versus in-memory aggregation |
| `15444` | The Unix Philosophy |
| `15487` | A uniform interface |
| `15541` | Separation of logic and wiring |
| `15573` | Transparency and experimentation |
| `15592` | MapReduce and Distributed Filesystems |
| `15661` | MapReduce Job Execution |
| `15689` | Mapper |
| `15710` | Distributed execution of MapReduce |
| `15781` | MapReduce workflows |
| `15818` | Reduce-Side Joins and Grouping |
| `15898` | Sort-merge joins |
| `15936` | Bringing related data together in the same place |
| `15957` | GROUP BY |
| `15989` | Handling skew |
| `16029` | Map-Side Joins |
| `16073` | Partitioned hash joins |
| `16099` | Map-side merge joins |
| `16113` | MapReduce workflows with map-side joins |
| `16153` | Building search indexes |
| `16188` | Key-value stores as batch process output |
| `16245` | Philosophy of batch process outputs |
| `16298` | Comparing Hadoop to Distributed Databases |
| `16318` | Diversity of storage |
| `16360` | Diversity of processing models |
| `16404` | Designing for frequent faults |
| `16502` | Materialization of Intermediate State |
| `16624` | Fault tolerance |
| `16664` | Discussion of materialization |
| `16735` | The Pregel processing model |
| `16756` | Fault tolerance |
| `16781` | Parallel execution |
| `16805` | High-Level APIs and Languages |
| `16837` | The move toward declarative query languages |
| `16886` | Specialization for different domains |
| `16912` | Summary |
| `16926` | Partitioning |
| `16933` | Fault tolerance |
| `16946` | Sort-merge joins |
| `16951` | Broadcast hash joins |
| `16957` | Partitioned hash joins |
| `16991` | References |

### Ch 11 — Stream Processing

`lines 17200–19168`  ·  `sed -n '17200,19168p' ddia.txt`

| line | section |
|---|---|
| `17249` | Transmitting Event Streams |
| `17294` | Messaging Systems |
| `17345` | Direct messaging from producers to consumers |
| `17379` | Message brokers |
| `17399` | Message brokers compared to databases |
| `17435` | Multiple consumers |
| `17438` | Load balancing |
| `17468` | Acknowledgments and redelivery |
| `17507` | Partitioned Logs |
| `17537` | Using logs for message storage |
| `17570` | Logs compared to traditional messaging |
| `17599` | Consumer offsets |
| `17656` | When consumers cannot keep up with producers |
| `17685` | Replaying old messages |
| `17703` | Databases and Streams |
| `17732` | Keeping Systems in Sync |
| `17818` | Implementing change data capture |
| `17849` | Initial snapshot |
| `17898` | API support for change streams |
| `17919` | Event Sourcing |
| `17964` | Deriving current state from the event log |
| `18024` | State, Streams, and Immutability |
| `18073` | Advantages of immutable events |
| `18105` | Deriving several views from the same event log |
| `18147` | Concurrency control |
| `18177` | Limitations of immutability |
| `18210` | Processing Streams |
| `18254` | Uses of Stream Processing |
| `18271` | Complex event processing |
| `18296` | Stream analytics |
| `18356` | Search on streams |
| `18404` | Reasoning About Time |
| `18430` | Event time versus processing time |
| `18539` | Tumbling window |
| `18547` | Hopping window |
| `18554` | Sliding window |
| `18562` | Session window |
| `18569` | Stream Joins |
| `18583` | Stream-stream join (window join) |
| `18611` | Stream-table join (stream enrichment) |
| `18683` | Time-dependence of joins |
| `18726` | Fault Tolerance |
| `18772` | Atomic commit revisited |
| `18797` | Idempotence |
| `18823` | Rebuilding state after a failure |
| `18853` | Summary |
| `18860` | AMQP/JMS-style message broker |
| `18907` | Stream-stream joins |
| `18917` | Stream-table joins |
| `18934` | References |

### Ch 12 — The Future of Data Systems

`lines 19169–23854`  ·  `sed -n '19169,23854p' ddia.txt`

| line | section |
|---|---|
| `19232` | Combining Specialized Tools by Deriving Data |
| `19260` | Reasoning about dataflows |
| `19292` | Derived data versus distributed transactions |
| `19366` | Ordering events to capture causality |
| `19410` | Batch and Stream Processing |
| `19434` | Maintaining derived state |
| `19464` | Reprocessing data for application evolution |
| `19514` | The lambda architecture |
| `19561` | Unifying batch and stream processing |
| `19620` | Composing Data Storage Technologies |
| `19646` | Creating an index |
| `19663` | The meta-database of everything |
| `19709` | Making unbundling work |
| `19753` | Unbundled versus integrated systems |
| `19809` | Designing Applications Around Dataflow |
| `19880` | Separation of application code and state |
| `19982` | Stream processors and services |
| `20039` | Observing Derived State |
| `20071` | Materialized views and caching |
| `20116` | Stateful, offline-capable clients |
| `20151` | Pushing state changes to clients |
| `20181` | End-to-end event streams |
| `20214` | Reads are events too |
| `20258` | Multi-partition data processing |
| `20284` | Aiming for Correctness |
| `20330` | The End-to-End Argument for Databases |
| `20344` | Exactly-once execution of an operation |
| `20367` | Duplicate suppression |
| `20414` | Operation identifiers |
| `20430` | INSERT INTO requests |
| `20456` | The end-to-end argument |
| `20495` | Applying end-to-end thinking in data systems |
| `20544` | Uniqueness constraints require consensus |
| `20604` | Multi-partition request processing |
| `20661` | Timeliness and Integrity |
| `20677` | Timeliness |
| `20687` | Integrity |
| `20719` | Correctness of dataflow systems |
| `20759` | Loosely interpreted constraints |
| `20816` | Coordination-avoiding data systems |
| `20854` | Trust, but Verify |
| `20890` | Maintaining integrity in the face of software bugs |
| `20938` | A culture of verification |
| `20963` | Designing for auditability |
| `20987` | The end-to-end argument again |
| `21010` | Tools for auditable data systems |
| `21047` | Doing the Right Thing |
| `21074` | Predictive Analytics |
| `21099` | Bias and discrimination |
| `21129` | Responsibility and accountability |
| `21173` | Feedback loops |
| `21198` | Privacy and Tracking |
| `21231` | Surveillance |
| `21274` | Consent and freedom of choice |
| `21314` | Privacy and use of data |
| `21371` | Data as assets and power |
| `21417` | Remembering the Industrial Revolution |
| `21452` | Legislation and self-regulation |
| `21496` | Summary |
| `22151` | ActiveRecord (object-relational mapper), 30,         Amazon |
| `22244` | B-trees (indexes), 79-83 |
| `22659` | Facebook |
| `22793` | HdrHistogram (numerical library), 16                  390 |
| `22881` | Java Database Connectivity (JDBC) |
| `23132` | Network Time Protocol (see NTP)                   offsets |
| `23191` | P                                                 performance |
| `23402` | S                                                 searches |
| `23646` | Tez (dataflow engine), 421-423                           471 |
| `23812` | WS-AtomicTransaction (2PC), 355 |
| `23828` | Colophon |
