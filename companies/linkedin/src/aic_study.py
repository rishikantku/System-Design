# -*- coding: utf-8 -*-
"""Study mode (13 parts) and interview mode (6 rounds) for every question in aic_research.Q.

Code references are (caption, file, type) or (caption, file, 'Type|member') tuples resolved by
qbank_cs against src/cs/aicoding/, which `dotnet run` compiles and tests (105 assertions).
"""

F = 'aicoding/'

# Follow-up ladders: (level prompt, the answer that scores)
STUDY = {}

STUDY['lru'] = dict(
 problem='Build a key-value cache with a fixed capacity. When it is full and a new key arrives, evict the least recently used entry. Both reads and writes count as use. '
         'Then the requirements grow: entries expire, many threads call it, traffic reaches millions of requests.',
 reqs=['`TryGet(key, out value)` and `Put(key, value)`, both O(1)', 'A read is a use — it changes the eviction order',
       'Re-putting an existing key updates it in place and counts as a use', 'Capacity ≤ 0 is rejected at construction'],
 insight='Two jobs need two structures. A dictionary finds a key in O(1) but has no order. A linked list keeps order and moves a node in O(1) — if you already hold the node. '
         'Store the list node in the dictionary and you get both. Everything after that — TTL, threads, shards — is a change to one of those two structures, never a rewrite.',
 design='`Dictionary<TKey, LinkedListNode<…>>` for lookup; `LinkedList<…>` for recency, most recent at `First`. **Invariant: both hold exactly the same keys.** '
        'Every method that touches one touches the other before returning. That one sentence is also the synchronization boundary later.',
 structs=[('Dictionary<TKey, LinkedListNode<T>>', 'O(1) lookup that returns the list handle, so unlinking needs no search'),
          ('LinkedList<T>', 'O(1) `Remove(node)`, `AddFirst`, `RemoveLast`; the BCL type is one less thing to get wrong than a hand-rolled list'),
          ('IClock (injected)', 'Makes TTL testable without `Thread.Sleep`'),
          ('object _gate + lock', 'The whole operation is the critical section, because a read writes')],
 algo=['Get: look up; if absent, miss. (TTL: if expired, remove from both and miss.) Move the node to the front. Return.',
       'Put: if present, update, move to front, return. If full, evict (TTL: prefer an expired entry near the cold end; else `Last`). Add to front and to the map.',
       'Sweep (TTL): walk at most *budget* nodes from the cold end, removing expired ones. Bounded work per call.'],
 code=[('Level 1 — plain LRU', F + 'A01_Lru.cs', 'LruCache'),
       ('Level 2 — TTL with lazy expiry and a bounded sweep', F + 'A01_Lru.cs', 'LruTtlCache'),
       ('Level 3 — thread-safe: one lock, because Get writes', F + 'A01_Lru.cs', 'SyncLruTtlCache'),
       ('Level 4 — sharded for throughput; approximate LRU', F + 'A01_Lru.cs', 'ShardedLruTtlCache'),
       ('Runtime resize (memory pressure)', F + 'A01_Lru.cs', 'LruTtlCache|public void Resize')],
 tests=['Capacity two: put 1, put 2, get 1, put 3 → 2 is gone, 1 survives (a read is a use).', 'Re-put updates in place: count unchanged, new value returned.',
        'Capacity one: the newest key always wins.', 'TTL: live at 99 ms, dead at exactly 100 ms — test the boundary, not one past it.',
        'An expired entry is reclaimed on read (count drops).', 'Eviction prefers an expired entry over a live LRU one.',
        'Sweep honours its budget: 1,000 expired entries, budget 100 → exactly 100 reclaimed.',
        '8 threads × 20,000 mixed operations: count never exceeds capacity, no torn values.',
        'Resize 4 → 2 keeps the two hottest; resize up admits more.'],
 cx='Get and Put O(1). Sweep O(budget). Memory O(capacity) — but only if expired entries are reclaimed; that is why the sweep exists.',
 ladder=[('Implement LRU.', 'Dictionary of list nodes + linked list. State the invariant. Test eviction after a read.'),
         ('Resize it at runtime.', 'Shrinking evicts immediately — expired first, then from the cold end — until Count ≤ the new capacity. Growing just raises the bound. `Resize` in the listing; tested both ways.'),
         ('Add TTL.', 'Absolute expiry per entry, injected clock, lazy check on read. Re-put renews. Decide and say whether an expired entry counts toward capacity until reclaimed.'),
         ('Make it thread-safe.', 'One lock around each operation, because Get mutates the list. Reject `ConcurrentDictionary` alone — it protects the map, not the list.'),
         ('Millions of requests.', 'The lock serialises everything. Shard by key hash, N independent caches. Each shard is exact LRU; the whole is approximate. Measure the hit-ratio cost.'),
         ('Expired-entry memory growth.', 'Lazy expiry alone leaks keys that are never read again. Add a bounded sweep from the cold end, on a timer or piggy-backed on writes. Never a full scan under the lock.'),
         ('Memory limits, not entry counts.', 'Entries vary in size: track a byte weight per entry and evict until under a byte budget. Under memory pressure (GC notifications, a container limit), Resize down.'),
         ('Hot keys and high contention.', 'One hot key lands on one shard and one lock. Options: a small per-thread or read-replicated front cache for the hottest keys, or approximate recency so reads stop writing.'),
         ('Observability.', 'Hit ratio, eviction rate split by reason (capacity vs expiry), expired-on-read rate, lock wait time, size in entries and bytes. Alert on a relative hit-ratio drop.'),
         ('Distribute it.', 'Consistent hashing across nodes; a client-side or proxy router; replication only if a miss is expensive. This is now a design question — Memcached/Redis Cluster, and say when you would just use one.')],
 conc='Shared state: the map and the list. The invariant spans both, so they must change together — one critical section per operation. Two threads in Get on different keys '
      'both call `_order.Remove` and `AddFirst`; without a lock the list\'s internal pointers interleave and corrupt. That is exactly what review exercise R3 does in 20/20 trials.',
 prod=['Bound memory: capacity in entries is not bytes — for variable-size values, cap by weight.', 'Hit ratio, eviction rate, expired-on-read rate as metrics; alert on hit-ratio drop.',
       'A slow source behind the cache: collapse concurrent misses (cache the in-flight `Lazy`), and add a timeout.', 'Warm-up after deploy: a cold cache is a thundering herd on the source.'],
 ai=['Write the interface and the two field declarations yourself; ask only for the method bodies.',
     'For TTL: "Add per-entry TTL using the injected IClock. Do not change eviction. List the members that change first."',
     'For threads: use the concurrency template — ask for the breaking interleaving, then decide the boundary yourself.'],
 traps=['Swapping in `ConcurrentDictionary` and calling it thread-safe (R3).', 'Get not moving the node to the front (R1) — passes put/get tests, fails eviction-after-read.',
        'TTL with expired entries left in place: returns -1 correctly, leaks memory, and evicts live entries first (R2).',
        '`DateTime.Now` instead of an injected clock — tests then need `Thread.Sleep`.', 'A full-map sweep under the lock (R10).'],
)

STUDY['lrucount'] = dict(
 problem='Add hit, miss and eviction counters to an LRU cache, then — before running anything — predict the hit ratio for several workloads. Then measure, and explain any gap.',
 reqs=['Read-through `GetOrLoad(key, load)`: a miss calls the source and inserts', 'Counters for hits, misses, evictions; a `Stats` snapshot',
       'Predictions for: a cyclic scan larger than the cache, a working set that fits, uniform random, skewed (Zipf-like)'],
 insight='The counters are trivial. The question is whether you can reason about LRU\'s behaviour without running it. The famous result: **a cyclic scan of capacity + 1 keys gets '
         'zero hits** — every key is evicted just before it is needed again. Uniform random over D keys gives about capacity/D. Skew is where LRU shines.',
 design='Wrap the existing `LruCache` rather than editing it — the counters are a separate concern. A readonly `CacheStats` record struct with a computed `HitRatio`.',
 structs=[('LruCache<TKey,TValue>', 'Reused unchanged — the requirement change touches nothing in it'), ('long counters', 'Plain fields single-threaded; `Interlocked` if read outside the lock'),
          ('record struct CacheStats', 'An immutable snapshot, so a reader never sees hits from one moment and misses from another')],
 algo=['GetOrLoad: TryGet → hit++. Else miss++, load, and if full eviction++, then Put.', 'Workloads are generators (`IEnumerable<int>`), seeded, so predictions are reproducible.'],
 code=[('Counting wrapper', F + 'A02_CountingLru.cs', 'CountingLruCache'), ('Workloads and the simulator', F + 'A02_CountingLru.cs', 'Workloads')],
 tests=['Cyclic over 5 keys, capacity 4: **0 hits** in 1,000 requests (predicted, then confirmed).', 'Cyclic over 5 keys, capacity 5: exactly 5 misses (cold), 0 evictions.',
        'Uniform over 1,000 keys, capacity 100: 9.8% measured vs 10% predicted.', 'Skewed (s=1) over 1,000 keys, capacity 100: 57.8% — far above uniform.'],
 cx='O(1) per request; the simulation is O(requests).',
 ladder=[('Add counters.', 'Wrap, do not edit. Snapshot record. Say what a hit ratio is *for*: it is the fraction of requests that do not touch the slow source.'),
         ('Predict the ratios.', 'Cyclic > capacity: 0. Fits: (n − distinct)/n. Uniform: ≈ capacity/distinct. Skewed: much higher — say why.'),
         ('Make the counters thread-safe.', 'Inside the cache lock if the cache has one. If a scraper reads them without the lock, `Interlocked.Increment` and `Interlocked.Read`.'),
         ('A nightly batch job scans every key once. What happens?', 'It flushes the hot set — LRU\'s weakness. Options: a scan-resistant policy (2Q, SLRU, W-TinyLFU as in Caffeine), or route batch reads around the cache.'),
         ('What would you alert on?', 'Hit-ratio drop relative to baseline, not an absolute number; eviction rate spike; source latency. A hit ratio without request rate is meaningless.')],
 conc='The counters ride inside the cache lock if there is one. The trap is a cheap "lock-free" read of three separate counters: you can observe hits from after a request and '
      'misses from before it. Take the snapshot under the same lock, or accept and say it is approximate.',
 prod=['Export as metrics with the cache name as a label; the ratio is computed by the dashboard from counts, never stored.', 'Track per-key-class ratios if one tenant\'s scan can wreck another\'s hits.'],
 ai=['Ask for the wrapper only: "Wrap this LruCache with hit/miss/eviction counters without modifying it."',
     'Do the predictions yourself first, out loud. Then ask the assistant to write the workload generators — and check its Zipf sampler (the CDF and the binary search are where it slips).',
     'If measurement disagrees with prediction, ask for two hypotheses, not a fix.'],
 traps=['Counting an eviction when the key was already present (an update is not an eviction).', 'An unseeded `Random` — the numbers change every run, so a prediction cannot be checked.',
        'Off-by-one in the Zipf CDF lookup (`~idx` handling from `BinarySearch`).', 'Claiming "LRU is optimal" — it is not; Belady\'s algorithm is, and it needs the future.'],
)

STUDY['lfurank'] = dict(
 problem='A cache that evicts the least frequently used key, breaking ties by least recently used, with `GetRank(key)`: the key\'s position in keep-order.',
 reqs=['Get and Put as close to O(1) as rank allows — state the cost', 'Evict min frequency; among equals, least recent', '`GetRank(key)`: 1 = safest, Count = next victim; −1 if absent',
       'GetRank is a read of metadata — it must not change frequency (say this; the statement does not)'],
 insight='O(1) LFU needs one linked list *per frequency* and a `minFreq` pointer: a touch moves a node from list f to list f+1. **Rank cannot be O(1) with that structure** — '
         'it needs to know how many keys sit above you. A sorted count per frequency gives O(distinct frequencies + bucket size). Say that before the assistant claims O(1).',
 design='`byKey: key → node`, `buckets: freq → LinkedList`, `freqCounts: SortedDictionary<freq, count>`, `minFreq`. Empty buckets are deleted, not left behind.',
 structs=[('Dictionary<int, LinkedList<Entry>>', 'One recency list per frequency; First = most recent'), ('SortedDictionary<int,int>', 'Ordered counts per frequency, for rank'),
          ('int _minFreq', 'The eviction bucket, in O(1); reset to 1 on every insert')],
 algo=['Touch: detach from bucket f; if that bucket emptied and f was min, min = f+1; attach to bucket f+1 at the front.',
       'Put new: if full, evict `buckets[minFreq].Last`; insert at freq 1; minFreq = 1.',
       'GetRank: 1 + Σ counts of frequencies above f + position of the node from the front of its bucket.'],
 code=[('LFU with GetRank', F + 'A03_LfuRank.cs', 'LfuRankCache')],
 tests=['a touched twice, b once, c never → ranks 1, 2, 3.', 'GetRank does not change rank (call it twice).', 'Tie at freq 1: the more recent key ranks higher; the older one is evicted.',
        'Capacity one under churn: minFreq resets correctly after evicting a high-frequency key.', 'Missing key → −1.'],
 cx='Get/Put O(log F), not O(1): the sorted count map that GetRank needs costs a log per touch (F = distinct frequencies, small in practice). Drop it and Get/Put are O(1) — that is the price of rank, and saying so is the point. GetRank O(F + B); an order-statistics tree makes it O(log n).',
 ladder=[('Implement LFU.', 'Buckets + minFreq. State the tie-break.'), ('Add GetRank.', 'Define rank first. Then admit the complexity honestly.'),
         ('Make GetRank O(log n).', 'Fenwick tree indexed by frequency for the "above me" count; within-bucket position still needs an order-statistic per bucket, or a global order-statistics tree keyed (freq, lastUse).'),
         ('Thread-safe.', 'One lock — every operation touches several structures. Rank reads also need the lock.'),
         ('Old popular keys never leave.', 'LFU\'s known flaw. Age frequencies (halve them periodically) or use W-TinyLFU.')],
 conc='A touch updates four things (two buckets, the counts, minFreq). Any partial view breaks eviction. One lock; no reader/writer lock, because Get writes.',
 prod=['Frequency aging, or the cache fossilises around yesterday\'s hot keys.', 'Rank is a debugging/observability feature — say how often it is called before optimising it.'],
 ai=['Give it your fields and ask for Touch only — that is where the minFreq bug lives.', 'Ask: "What is the complexity of GetRank as written? Do not claim O(1) unless every step is O(1)."'],
 traps=['Claiming O(1) GetRank.', 'Forgetting to reset minFreq to 1 on insert.', 'Leaving empty buckets in the map, so minFreq advances past them incorrectly.',
        'GetRank calling Touch — reading the rank changes it.'],
)

STUDY['intervals'] = dict(
 problem='A class that accepts intervals one at a time, merges overlaps, and answers questions about coverage. You choose the bookkeeping.',
 reqs=['`Add(start, end)` merges with anything it overlaps or touches', '`Remove(start, end)` — may split an interval in two', '`Contains(point)`, `CoveredLength`',
       'State the convention: half-open [start, end)'],
 insight='"Sort then merge" is for a batch. For a stream you want a sorted structure with a **floor lookup** — the interval starting at or before x — because only the floor and '
         'the intervals starting inside the new one can overlap it. That makes Add O(log n + k), and each interval is absorbed once, so amortised O(log n).',
 design='`SortedSet<(Start, End)>` ordered by start; intervals kept disjoint and non-touching. `GetViewBetween(min, (x,_)).Max` is the floor. `CoveredLength` maintained on every change.',
 structs=[('SortedSet<(int,int)> + custom comparer', 'Ordered, O(log n) insert/remove, range views; .NET has no TreeMap.floorKey, this is the idiom'),
          ('long CoveredLength', 'Maintained incrementally, so reading it is O(1)')],
 algo=['Add: if floor reaches start, absorb it. Absorb every interval starting in [start, end]. Insert the union.',
       'Remove: collect the floor (if it reaches in) and every interval starting in [start, end); remove each; re-add the left and right remnants.'],
 code=[('IntervalSet', F + 'E01_IntervalSet.cs', 'IntervalSet')],
 tests=['[1,3) + [5,7) + [3,5) → one interval: touching merges under half-open.', 'Contained add changes nothing.', 'Remove [3,4) from [1,7) splits into two.',
        '7 is not in [1,7).', '**Property test**: 300 random trials of 25 add/remove operations against a 60-cell bitmap — coverage, membership and disjointness all match.'],
 cx='Add/Remove amortised O(log n); Contains O(log n); CoveredLength O(1). Memory O(n).',
 ladder=[('Add with merging.', 'Floor + range view. Say half-open.'), ('Remove.', 'Splits. Remnants re-added.'), ('Covered length fast.', 'Maintain it on every change.'),
         ('Millions of intervals.', 'Still log n. If memory is the issue, coarsen; if queries are range sums, a segment tree over compressed coordinates.'),
         ('Concurrent writers.', 'One lock (a merge touches several entries). Readers that only need CoveredLength can read a volatile snapshot.')],
 conc='A merge removes several entries and inserts one; a concurrent reader can see the gap. One lock per operation; CoveredLength updated inside it.',
 prod=['Integer overflow on `end - start` with large coordinates: use long.', 'Inverted or empty intervals: reject or ignore — decide and test it.'],
 ai=['Tell it the convention: "half-open [start, end); touching intervals merge".', 'Ask for Add only, given your SortedSet field and comparer.',
     'Ask for a property test against a bitmap — then read it, because the oracle must be obviously correct.'],
 traps=['`List` + `Sort` on every insert: O(n log n) per Add.', 'Merging with `last.End = cur.End` instead of `Math.Max` — loses containment (R4).',
        'Closed vs half-open mismatch: [1,2] and [2,3] merge or not.', 'Forgetting the floor interval that starts before the new one but reaches into it.'],
)

STUDY['records'] = dict(
 problem='Read JSON-like event records, one per line, build typed objects, aggregate per action, and handle malformed input without losing the rest of the batch.',
 reqs=['Typed model classes built from scratch', 'Per action: count, mean and max latency, distinct users', 'Malformed lines counted by reason, never thrown',
       'Streams: holds aggregates, not the input'],
 insight='Bad input is data. The design question is the **error model**: a result type with a reason, counted per reason, so a million-line batch with three bad rows produces '
         'a million-minus-three results and an explanation — not an exception, and not a silent drop.',
 design='`Event` record; `ParseResult` with `Reject?` reason; `EventParser.Parse` returning a result; `Aggregator.Consume(IEnumerable<string>)` holding only per-action accumulators.',
 structs=[('record Event', 'Immutable, value equality, one line to declare'), ('enum Reject', 'Enumerable reasons → countable, testable'),
          ('JsonDocument', 'Parses without binding, so type errors are per field and reportable'), ('HashSet<string> per action', 'Distinct users — the one part that grows')],
 algo=['Per line: parse JSON → must be an object → each field present and correctly typed → range checks → Event.', 'Accumulate per action; summary sorted by count, then name.'],
 code=[('Parser', F + 'C01_Records.cs', 'EventParser'), ('Aggregator', F + 'C01_Records.cs', 'Aggregator')],
 tests=['Ten lines: four good, one of each reject reason, one blank → accepted 4, each reason counted once.', 'view: count 3, mean 200, max 300, 2 distinct users.'],
 cx='O(lines). Memory O(actions + distinct users per action).',
 ladder=[('Parse and aggregate.', 'Model, parser, aggregator — three small types.'), ('Malformed input.', 'Result type; count per reason; keep going.'),
         ('A 50 GB file.', 'Already streaming. Distinct users becomes a HyperLogLog sketch; say the error (~1–2%).'),
         ('Parallelise.', 'Partition lines, aggregate per partition, merge accumulators (counts and sums add; max takes max; sets union / HLL merge).'),
         ('Late or duplicate events.', 'Idempotency by event id; windowing by event time with a lateness bound.')],
 conc='Parallel aggregation should not share accumulators; give each worker its own and merge at the end — no locks on the hot path.',
 prod=['Emit reject counts as metrics; alert on a reject-rate jump (a schema change upstream).', 'Keep a sample of rejected lines for debugging, with PII redaction.'],
 ai=['This is where to delegate most: "Write record types and a JsonDocument-based parser for this schema, returning a result with a Reject reason instead of throwing."',
     'Then audit the error handling line by line — that is what is being scored.', 'Ask it for malformed test lines, one per reason.'],
 traps=['A try/catch around the whole loop: the first bad line silently drops every line after it (R7).', '`int.Parse` on a JSON number that is a float or too large.',
        'Deserialising straight into the model: one bad field throws for the whole record with no reason.', 'Mean computed in int — integer division.'],
)

STUDY['maze'] = dict(
 problem='You are handed a maze class with bugs. Fix it, then extend it: validate that it is well formed, find the shortest path, and generate mazes that always have a path.',
 reqs=['Parse a grid of `#`, `.`, `S`, `E`', '`IsWellFormed`: closed outer wall except S/E openings; S ≠ E', '`ShortestPath`: BFS step count or −1', '`Generate(rows, cols, seed)` with a guaranteed path'],
 insight='Debug-first rounds score reading. Read the class, state its invariants, write the failing test, then fix. For generation: carving a **spanning tree** over the cells '
         '(randomised DFS) connects every open cell, so S and E are connected by construction — no need to generate-and-check.',
 design='Constructor validates shape (non-empty, rectangular). BFS marks distance on enqueue. Generator is iterative so a large maze cannot overflow the stack.',
 structs=[('bool[,]', 'Walls; O(1) lookup'), ('int[,] dist (−1 = unseen)', 'Visited and distance in one array'), ('Queue<(int,int)>', 'BFS frontier'),
          ('Stack<(int,int)>', 'Iterative DFS carving')],
 algo=['BFS: mark on enqueue; bounds check before indexing.', 'Generate: odd dimensions; start at (1,1); repeatedly carve to a random unvisited cell two steps away, knocking out the wall between.'],
 code=[('Maze', F + 'B01_Maze.cs', 'Maze')],
 tests=['Hand-made 5×7 maze: well formed, path 8.', 'A hole in the outer wall is detected.', 'A walled-off E returns −1.',
        '200 generated mazes (seeds 0–199, 21×31): every one well formed and solvable.'],
 cx='BFS O(rows × cols). Generation O(rows × cols).',
 ladder=[('Fix the bugs.', 'Failing test first, then the fix, keep the test.'), ('Well formed including the outer wall.', 'Border all wall except openings; S/E distinct and open.'),
         ('Always a path.', 'Spanning-tree carving, or union-find (Kruskal) — say why both guarantee connectivity.'),
         ('Why did you choose the AI\'s approach?', 'Have a reason: "It suggested DFS backtracking and Kruskal. DFS is simpler to verify and iterative avoids stack depth; Kruskal gives less biased mazes. Simplicity won here."'),
         ('How would you test each change?', 'One test per change, plus the property test over many seeds.'), ('Production?', 'Validate input size, bound generation time, make seeds reproducible for support tickets.')],
 conc='Not inherently concurrent. If asked: the maze is immutable after construction, so concurrent path queries need no locks — say that, it is the right answer.',
 prod=['Reject huge dimensions before allocating.', 'Seeded generation so a reported maze can be reproduced.'],
 ai=['Start with: "Summarise this class, its invariants, and any method inconsistent with the others. Quote line numbers."',
     'Do not ask it to "fix the bugs" — ask for hypotheses, verify, then fix.', 'Ask for two generation algorithms and their trade-offs, then choose.'],
 traps=['Recursive DFS generator: stack overflow on a large maze.', 'BFS marking visited on dequeue (D3).', 'Bounds check after the array access.',
        'Even dimensions with the step-2 carving: the last row/column is unreachable.'],
)

STUDY['rand10'] = dict(
 problem='Given `rand7()` uniform on 1..7, produce `rand10()` uniform on 1..10. Explain why it is uniform before writing code.',
 reqs=['Exactly uniform, not approximately', 'Expected number of rand7 calls', 'Generalise: uniform on [0, n) from any uniform [0, m)'],
 insight='You cannot map 7 outcomes onto 10 evenly — 10 does not divide 7. Two calls give 49 equally likely outcomes. Keep the first 40 (they split into 10 groups of 4), '
         'reject the other 9 and try again. Uniform because every output has exactly 4 of the 49 outcomes and rejection does not favour any.',
 design='Inject the source as `Func<int>` so tests can enumerate every outcome deterministically.',
 structs=[('Func<int>', 'An injected source makes an exact proof-by-enumeration test possible')],
 algo=['idx = (a−1)·7 + (b−1) ∈ [0,48]; if idx < 40 return idx % 10 + 1; else retry.',
       'General: build a base-m number until its range ≥ n; accept if below the largest multiple of n; else retry.'],
 code=[('Rand10 and the general form', F + 'G01_Sampling.cs', 'Sampling'), ('Fair coin from a biased one (InterviewDB Q4)', F + 'G01_Sampling.cs', 'FairCoin')],
 tests=['**Exact**: all 49 pairs enumerated — 40 accepted, each output from exactly 4.', 'General form, exact: uniform below 6 from a fair coin — 6 of 8 three-bit strings accepted, each value once.',
        'Von Neumann on a 70/30 coin: 50% ± 1% over 100,000 flips.'],
 cx='Accept probability 40/49, expected 49/40 rounds = 2 × 49/40 ≈ 2.45 rand7 calls. Worst case unbounded (geometric), which is fine — say so.',
 ladder=[('Implement rand10.', 'Explain first, then code.'), ('Prove uniformity.', 'Count preimages: 4 each.'), ('Expected calls.', '≈ 2.45.'),
         ('Fewer calls?', 'Reuse the rejected remainder (9 leftover outcomes) as entropy for the next attempt — expected calls drop.'),
         ('Biased source instead.', 'Von Neumann pairs.')],
 conc='`Random` is not thread-safe; share `Random.Shared` (thread-safe since .NET 6) or one per thread.',
 prod=['For anything security-relevant: `RandomNumberGenerator`, not `Random`.', 'Seeded sources for reproducible tests and simulations.'],
 ai=['Do the maths yourself, out loud, before any prompt. This is the round\'s clearest test of whether you can check the assistant.',
     'Then: "Write Rand10 using this rejection scheme; inject rand7 as Func<int>."', 'Ask for an exact enumeration test, not a sampling test — sampling cannot prove uniformity.'],
 traps=['`(rand7() + rand7()) % 10 + 1` — looks plausible, is biased; enumeration gives counts 5 4 4 4 4 4 5 6 7 6 (R6).', '`rand7() * rand7()` — products are not uniform either.',
        'A chi-square test presented as proof.', '`rand5`-style answers copied from a different problem.'],
)

STUDY['queue'] = dict(
 problem='A bounded queue shared by producer and consumer threads: producers block when full, consumers block when empty. Then add cancellation and graceful shutdown.',
 reqs=['`Enqueue` blocks while full', '`TryDequeue` blocks while empty; returns false once completed and drained', '`CancellationToken` on both', '`Complete()` for shutdown'],
 insight='In production C# you say `Channel.CreateBounded<T>` and move on. Built by hand, everything rests on two rules: **wait in a `while` loop** (re-check the condition after '
         'every wake), and **`PulseAll`** when producers and consumers share one monitor (a `Pulse` can wake the wrong kind of waiter).',
 design='One `object` gate, a `Queue<T>`, a completed flag. Cancellation registers a callback that pulses the monitor, because `Monitor.Wait` cannot observe a token.',
 structs=[('Queue<T>', 'FIFO storage'), ('Monitor.Wait / PulseAll', 'Condition waiting inside the lock'), ('CancellationToken.Register', 'Wakes blocked waiters on cancel'),
          ('bool _completed', 'Shutdown signal; consumers drain then exit')],
 algo=['Enqueue: lock; while full and not completed: wait. Throw if cancelled or completed. Enqueue; PulseAll.',
       'TryDequeue: lock; while empty and not completed: wait. If empty now, return false (completed). Dequeue; PulseAll.'],
 code=[('BoundedBlockingQueue', F + 'D01_BoundedQueue.cs', 'BoundedBlockingQueue')],
 tests=['4 producers × 5,000 items, 4 consumers: sum and count of consumed = produced — nothing lost or duplicated.', 'Consumers exit after Complete.',
        'A producer blocked on a full queue throws on cancellation within 100 ms.', 'Enqueue after Complete throws; remaining item drains; then false.'],
 cx='O(1) per operation plus waiting. PulseAll wakes every waiter — fine at small thread counts; two condition variables (or SemaphoreSlim pairs) scale better.',
 ladder=[('Implement it.', 'While-loop waits, PulseAll.'), ('Cancellation.', 'Token + registration that pulses.'), ('Shutdown.', 'Complete(); drain; false.'),
         ('Async.', '`Channel<T>`, or two `SemaphoreSlim`s with `WaitAsync` — never block a thread-pool thread.'),
         ('In production.', 'Bounded capacity *is* back-pressure. Metrics: depth, wait time, drops. Decide what happens when full: block, drop oldest, or reject.')],
 conc='This *is* the concurrency question. Answer both: two producers at once — both wait in the loop, each re-checks after waking, so neither overfills. The boundary is the whole operation.',
 prod=['Queue depth and producer wait time as metrics.', 'A poison item that crashes a consumer: catch per item, dead-letter it, keep the loop alive.'],
 ai=['Name `Channel<T>` first. Then, if building by hand: ask for the implementation, then ask "where must this use while instead of if, and why?" and check its answer against the code.',
     'Ask for a stress test that asserts conservation (sum consumed = sum produced), not ordering.'],
 traps=['`if` instead of `while` around Wait (R9).', '`Pulse` instead of `PulseAll` with one shared monitor (R9) — hung or threw in 10/10 trials.',
        'Ignoring the cancellation token while blocked.', 'No completion signal, so consumers can never exit (the InterviewDB Q15 interface has the same flaw).'],
)

STUDY['window'] = dict(
 problem='Count events in the last five minutes, at high rates, from many threads.',
 reqs=['`Record(nowSecs)`, `Count(nowSecs)`', 'Memory bounded regardless of event rate', 'Thread-safe'],
 insight='You do not need every event\'s timestamp — you need counts per second. A ring of 300 one-second buckets, each tagged with the second it holds, is O(window) memory '
         'whatever the rate. A stale bucket is detected by its tag and reset on reuse.',
 design='Two arrays (stamp, count) indexed by `second % window`; one lock.',
 structs=[('long[] stamp, int[] count', 'The ring; the stamp detects stale slots'), ('lock', 'A Record is check-tag-then-increment — two steps, one invariant')],
 algo=['Record: slot = now % W; if stamp[slot] ≠ now, reset it; count[slot] += n.', 'Count: sum slots whose stamp is in (now − W, now].'],
 code=[('WindowCounter', F + 'C02_WindowCounter.cs', 'WindowCounter')],
 tests=['Events at 1, 1, 299, 300 → 4 at t=300; 2 at t=301 (second 1 left).', 'A slot reused 600 s later is reset, not added to.', '8 threads × 10,000 records → exactly 80,000.'],
 cx='Record O(1); Count O(W). Make Count O(1) with a running total adjusted as slots are recycled.',
 ladder=[('Implement.', 'Ring of buckets.'), ('Thread-safe.', 'One lock; or per-thread striped counters summed on read.'), ('O(1) reads.', 'Running total.'),
         ('Per user, millions of users.', 'Memory now matters: coarser buckets, or approximate (count-min sketch).'), ('Across machines.', 'Local counters, periodic aggregation; accept staleness.')],
 conc='Without the lock, two threads can both see a stale tag and both reset — losing one increment — or interleave reset and increment. Check-tag-then-act is the race.',
 prod=['This is the core of a rate limiter; say so if the conversation drifts there.'],
 ai=['Specify the structure ("ring of per-second buckets with a stamp array") — otherwise the assistant reaches for a queue of timestamps.'],
 traps=['A `Queue<long>` of timestamps — O(events) memory.', 'Not resetting a reused slot.', '`Interlocked` on count alone while the stamp reset is unprotected.'],
)

# ---------------------------------------------------------------- questions studied on the bank page
LINKED = {
 'scheduler': dict(insight='A min-heap ordered by due time, one worker thread waiting on the earliest deadline, woken early when a sooner task arrives.',
   ai=['Ask for the heap-and-wait skeleton; own the wake-up logic.'], traps=['Sleeping for a fixed tick instead of until the next deadline.', 'Not waking the worker when an earlier task is scheduled.'],
   ladder=[('Schedule and run.', 'Heap + condition wait with timeout.'), ('Cancel.', 'Lazy deletion with a cancelled flag.'), ('Many workers.', 'Shared heap, one lock, PulseAll.'), ('Shutdown.', 'Drain or discard — decide.')],
   conc='The heap and the wake-up must be under one lock, or a new earliest task is missed.'),
 'rankcache': dict(insight='Eviction by a caller-supplied rank: a heap or sorted set keyed (rank, recency), with lazy deletion on rank updates.',
   ai=['Ask it to compare a heap with lazy deletion against a SortedSet.'], traps=['Heap entries left stale after a rank update.'],
   ladder=[('Implement.', 'SortedSet<(rank, seq, key)>.'), ('Rank updates.', 'Remove and re-add.'), ('Thread-safe.', 'One lock.')], conc='Map and ordered set change together: one lock.'),
 'distance': dict(insight='BFS from one side visits b^d nodes; from both sides 2·b^(d/2). On a social graph that is the difference between feasible and not.',
   ai=['Own the "expand the smaller frontier" rule; delegate the adjacency plumbing.'], traps=['Marking visited on dequeue (D3).', 'Stopping when frontiers touch without finishing the level.'],
   ladder=[('Distance.', 'BFS.'), ('Faster.', 'Bidirectional.'), ('Graph too big.', 'Precomputed 2-hop neighbourhoods; distributed BFS.')], conc='Read-only graph: no locks needed.'),
 'taskmgr': dict(insight='A dependency graph; adding an edge that closes a cycle must be rejected — including a cycle closed across two separate AddTask calls.',
   ai=['Ask for tests that close a cycle across two calls.'], traps=['Overwriting a task\'s dependency edges instead of unioning them — my own first answer did this.'],
   ladder=[('Add tasks.', 'Adjacency + cycle check.'), ('Run order.', 'Kahn\'s algorithm.'), ('Parallel waves.', 'Levels of in-degree zero.')], conc='Completion from many workers decrements in-degrees: one lock or Interlocked per node.'),
 'covered': dict(insight='The Tier 1 interval manager plus a maintained covered size.', ai=['Ask for a bitmap property test.'], traps=['Amortised claimed as worst case.'],
   ladder=[('Add + size.', 'Maintained total.'), ('Remove.', 'Splits.')], conc='One lock.'),
 'mergetrees': dict(insight='Merge keyed n-ary trees by key; the trap is aliasing — returning nodes or collections that belong to an input.',
   ai=['Ask: "Does the result share any object with either input?"'], traps=['Reusing an input\'s Children dictionary (D8).'],
   ladder=[('Merge.', 'Recursive by key.'), ('Conflicts.', 'Explicit policy.'), ('Do not mutate inputs.', 'Fresh nodes all the way down.'), ('Concurrent readers.', 'Build new, swap one reference.')],
   conc='Build the merged tree privately, publish with one reference swap — readers never see a half-merged tree.'),
 'wordladder': dict(insight='BFS over words; a wildcard index (h*t → hot, hat) finds neighbours in O(L) instead of O(N·L).', ai=['Check whether it counts edges or words.'],
   traps=['LeetCode 127 counts words; InterviewDB Q8 counts edges.'], ladder=[('Shortest.', 'BFS.'), ('Faster neighbours.', 'Wildcard index.'), ('All shortest paths.', 'BFS layers + backtrack.')], conc='—'),
 'leaves': dict(insight='Height from the bottom: leaves are 0; remove level by level is grouping by that height.', ai=['Ask for the iterative version.'], traps=['Mutating the tree while iterating it.'],
   ladder=[('Levels.', 'Post-order height.'), ('Do not mutate.', 'Return lists.')], conc='—'),
 'biased': dict(insight='Von Neumann: pairs HT/TH have equal probability.', ai=['Do the maths yourself first.'], traps=['Assuming the bias is known.'],
   ladder=[('Fair from biased.', 'Pairs.'), ('Expected flips.', '1/(p(1−p)).')], conc='—'),
 'randbag': dict(insight='Array + index map; remove by swapping with the last element.', ai=['Ask it to handle duplicates and check the index-map update order.'],
   traps=['Updating the moved element\'s index after removing the key, not before.'], ladder=[('O(1) ops.', 'Swap-remove.'), ('Duplicates.', 'Map to a set of indices.')], conc='One lock.'),
 'topk': dict(insight='Counts in a map + a size-k min-heap, or a bucket sort by count for exact answers on demand.', ai=['Ask for complexity per Add and per Top call.'],
   traps=['Sorting the whole map on every Top call (R5).'], ladder=[('Top k.', 'Heap of size k.'), ('Streaming at scale.', 'Count-min sketch + heap.'), ('Across shards.', 'Merge per-shard counts, not per-shard top-k.')], conc='Per-thread counts merged on read.'),
}

# ---------------------------------------------------------------- interview mode (6 rounds)
# round: (interviewer says, what they are listening for)
def _rounds(problem, implement, change, test, review, prod):
    return [('Problem', problem[0], problem[1]), ('Implement', implement[0], implement[1]), ('Requirement change', change[0], change[1]),
            ('Test', test[0], test[1]), ('Review the AI\'s code', review[0], review[1]), ('Production', prod[0], prod[1])]

INTERVIEW = {
 'lru': _rounds(
   ('"We need an in-memory cache for user profiles. Fixed capacity; when it is full, drop whatever was used least recently. Talk me through it before you write anything."',
    ['Restates: capacity + recency', 'Asks whether a read counts as use, what a miss returns, capacity 0', 'Names map + list, the invariant, O(1)']),
   ('"Go ahead and build it. Use the assistant however you like."',
    ['Writes the interface first', 'Delegates bodies with constraints, not "write an LRU"', 'Reads output before running', 'Narrates']),
   ('"Profiles go stale. Each entry should expire after a TTL — and get should return a miss for an expired entry even if it is still in memory."',
    ['Asks: per-entry or global TTL? does re-put renew? does expired count toward capacity?', 'Injects a clock', 'Changes only the entry and the read path']),
   ('"How do you know it works? Show me."',
    ['Boundary at exactly the TTL', 'Eviction after a read', 'Capacity one', 'Audits generated expected values']),
   ('"Here is what the assistant suggested for thread safety." (Show review exercise R3.) "Would you ship it?"',
    ['Rejects it: map protected, list not', 'Gives the interleaving', 'Proposes one lock and says why reader/writer does not help']),
   ('"This now serves millions of requests a second. What breaks first, and what happens to memory over a week?"',
    ['Lock contention → shard; approximate LRU', 'Expired keys never read again leak → bounded sweep', 'Metrics: hit ratio, evictions', 'Slow source: stampede'])),
 'lrucount': _rounds(
   ('"Add hit and miss counters to this LRU. Before we run anything — what hit ratio do you expect if a client cycles through capacity-plus-one keys?"',
    ['Predicts zero, and explains why', 'Asks what counts as a hit for a read-through']),
   ('"Build the counters and a small simulator."', ['Wraps instead of editing', 'Seeds randomness', 'Snapshot record']),
   ('"Now a uniform workload over ten times the capacity, and a skewed one."', ['Predicts ≈10% uniform, much higher skewed — before measuring']),
   ('"Your uniform number came out 9.8%, not 10%. Is something wrong?"', ['Warm-up and sampling noise; not a bug', 'Would increase length to check convergence']),
   ('"The assistant\'s Zipf generator — would you trust it?"', ['Checks the CDF and BinarySearch complement handling', 'Asks for a seed']),
   ('"A nightly batch scans every key. What happens to daytime hit ratio, and what would you change?"', ['Scan flushes hot set', 'Scan-resistant policy or bypass', 'Alert on relative drop'])),
 'lfurank': _rounds(
   ('"Evict the least frequently used key; break ties by least recently used. Also give me GetRank(key)."',
    ['Defines rank before coding', 'Asks whether GetRank counts as a use', 'States O(1) Get/Put via buckets + minFreq']),
   ('"Implement it."', ['Owns the minFreq logic', 'Delegates list plumbing', 'Deletes empty buckets']),
   ('"What is GetRank\'s complexity? Can you do better?"', ['O(F + B), honestly', 'Fenwick / order-statistics tree for log n']),
   ('"Test it."', ['Tie-break case', 'GetRank does not mutate', 'minFreq reset after eviction']),
   ('"The assistant claims its GetRank is O(1). Here it is." (It walks the buckets.)', ['Catches the false claim', 'Explains the walk']),
   ('"Old popular keys never leave the cache. What do you do?"', ['Frequency aging / W-TinyLFU', 'Metrics to detect fossilisation'])),
 'intervals': _rounds(
   ('"I\'ll call addInterval with ranges one at a time. Keep them merged. I\'ll also want to ask how much is covered."',
    ['Asks closed vs half-open', 'Asks whether touching merges', 'Chooses a sorted structure with floor lookup and says why not re-sorting a list']),
   ('"Build it."', ['SortedSet idiom', 'Maintained covered length']),
   ('"Now support removing a range."', ['Recognises splits', 'Re-adds remnants', 'Keeps Add untouched']),
   ('"How would you test this thoroughly?"', ['Property test against a bitmap', 'Touching, containment, split']),
   ('"Here is the assistant\'s merge." (Show R4.) "Accept?"', ['Spots End = cur.End instead of Max', 'Gives [1,10]+[2,3] as the counterexample']),
   ('"Millions of intervals and several writers."', ['Still log n', 'One lock; snapshot for readers', 'long for lengths'])),
 'records': _rounds(
   ('"Here is a log of JSON events. Build classes for them and give me per-action counts and latency stats. Some lines are garbage."',
    ['Asks what to do with bad lines: skip, count, fail?', 'Proposes a result type', 'Asks the schema']),
   ('"Implement it."', ['Delegates the model and parser boilerplate', 'Audits error handling line by line']),
   ('"We also need distinct users per action — and the file is 50 GB."', ['Already streaming', 'Distinct users grows → HyperLogLog']),
   ('"Test it."', ['One malformed line per reject reason', 'Mean as double']),
   ('"Here is the assistant\'s parser." (Show R7.) "Ship it?"', ['Catches the loop-wide catch that drops everything after the first bad line']),
   ('"It runs every hour in production. What do you monitor?"', ['Reject rate by reason', 'Sampled rejected lines with redaction', 'Schema-change alerting'])),
 'maze': _rounds(
   ('"This Maze class has bugs. Find them, then we\'ll extend it." (Use debugging exercise D3 as the starting code.)',
    ['Reads before prompting', 'Writes a failing test first', 'States invariants']),
   ('"Add IsWellFormed — including the outer wall."', ['Border check with S/E openings', 'S ≠ E']),
   ('"Given a start and end, generate a maze that always has a path."', ['Spanning-tree carving; why it guarantees a path', 'Iterative, not recursive']),
   ('"How would you test each change?"', ['One test per change', 'Property test over many seeds']),
   ('"Why did you choose this AI-generated approach over the other options?"', ['Names the alternatives and the reason', 'Not "the AI chose it"']),
   ('"If this went to production, what would you change?"', ['Size limits', 'Reproducible seeds', 'Immutability → lock-free reads'])),
 'rand10': _rounds(
   ('"You have rand7. Give me rand10. Explain it mathematically before you write code."', ['49 outcomes, keep 40, reject 9', 'Why uniform: 4 preimages each']),
   ('"Code it."', ['Injects the source', 'Short code']),
   ('"What is the expected number of rand7 calls? Can you reduce it?"', ['≈ 2.45', 'Reuse rejected entropy']),
   ('"How would you test that it is uniform?"', ['Exact enumeration, not sampling']),
   ('"The assistant suggests (rand7() + rand7()) % 10 + 1. Thoughts?"', ['Biased; counts 5 4 4 4 4 4 5 6 7 6']),
   ('"Many threads call it."', ['Random.Shared or per-thread Random', 'Crypto RNG if security-relevant'])),
 'queue': _rounds(
   ('"Producers and consumers share a buffer of fixed size. Producers block when it is full. Design it."', ['Names Channel<T> first', 'Then while-loop waits, PulseAll']),
   ('"Build it by hand."', ['Owns the wait conditions']),
   ('"We need to shut down cleanly, and callers need to be able to cancel."', ['Complete + drain + false', 'Token registration that pulses']),
   ('"Prove nothing is lost."', ['Conservation stress test — sum and count']),
   ('"The assistant\'s version." (Show R9.) "Ship it?"', ['if → while', 'Pulse → PulseAll', 'Explains the hang']),
   ('"In production the consumer is ten times slower than producers."', ['Bounded capacity is back-pressure', 'Block vs drop vs reject', 'Depth + wait-time metrics'])),
 'window': _rounds(
   ('"Count requests in the last five minutes, at ten thousand a second."', ['Rejects a timestamp queue on memory', 'Ring of buckets']),
   ('"Build it."', ['Stamp array for stale detection']), ('"Now many threads record at once."', ['Check-then-act on the stamp is the race; one lock']),
   ('"Test it."', ['Window edge', 'Slot reuse', 'Concurrent total']), ('"The assistant used Interlocked on the counts only. OK?"', ['Reset is unprotected — no']),
   ('"Per user, ten million users."', ['Memory per key', 'Sketches', 'This is a rate limiter'])),
}

def _generic(qid, title, ladder):
    l = ladder + [('', '')] * 6
    return _rounds(
        ('"%s — talk me through your approach before writing code."' % title, ['Restates; asks the questions that change the code', 'Names the structure and complexity']),
        ('"Build it. The assistant is available."', ['Delegates mechanical parts with constraints', 'Reviews before running']),
        ('"%s"' % (l[1][0] or 'Change the requirement.'), [l[1][1] or 'Changes the smallest component']),
        ('"Show me it works."', ['Edges', 'Audited generated tests']),
        ('"Here is what the assistant produced for that change. Accept it?"', ['Finds the defect listed under "what assistants get wrong"']),
        ('"%s"' % (l[2][0] or 'What changes in production?'), [l[2][1] or 'Concurrency, memory, failure']))

for _q, _d in LINKED.items():
    if _q not in INTERVIEW:
        from aic_research import Q as _Q
        _t = next(x['title'] for x in _Q if x['id'] == _q)
        INTERVIEW[_q] = _generic(_q, _t, _d['ladder'])

# ---------------------------------------------------------------- review exercises
REVIEW = [
 dict(id='R1', title='"An O(1) LRU cache"', cls='R1_LruCache', kind='Bug',
      ctx='You asked for an LRU cache. It passes put-then-get.',
      answer='**Get never moves the node to the front**, so reads do not count as use. Put 1, put 2, get 1, put 3 → key 1 (just read) is evicted. Passes put/get tests; fails the first eviction-after-read test.',
      fix='Move the node to the front in Get, exactly as Put does.', test='"R1: Get does not refresh recency, so the just-read key 1 is evicted"'),
 dict(id='R2', title='"TTL support — expired entries return -1"', cls='R2_LruTtl', kind='Memory leak',
      ctx='You asked for TTL. The expiry test passes.',
      answer='Expired entries are **never removed**: Get returns -1 but leaves them in the map and list. They count toward capacity, so the next Put evicts a *live* LRU entry while the dead '
             'one stays. Keys that are never read again stay forever — unbounded growth in a long-running process.',
      fix='Remove on an expired read; prefer expired victims at eviction; add a bounded sweep (see LruTtlCache).', test='"R2: live key 2 evicted while dead key 1 kept"'),
 dict(id='R3', title='"Thread-safe via ConcurrentDictionary"', cls='R3_ConcurrentLru', kind='Race condition',
      ctx='You asked to make the LRU thread-safe.',
      answer='`ConcurrentDictionary` makes each *map* call atomic. The `LinkedList` is unprotected, and Get mutates it. Two Gets interleaving `Remove`/`AddFirst` corrupt the list; '
             'Put\'s check-then-evict is also a race. **Corrupted or threw in 20 of 20 stress trials.**',
      fix='One lock around each whole operation (SyncLruTtlCache). The invariant spans two structures, so the boundary does too.', test='R3 stress note: 20/20'),
 dict(id='R4', title='"Merge intervals — sort, then merge neighbours"', cls='R4_Merge', kind='Incorrect logic',
      ctx='You asked for merge intervals.', answer='`result[^1] = (start, cur.End)` should be `Math.Max(result[^1].End, cur.End)`. **[1,10] + [2,3] becomes [1,3]** — a contained interval shrinks the cover.',
      fix='Take the max of the two ends.', test='"R4: [1,10]+[2,3] collapses to [1,3]"'),
 dict(id='R5', title='"TopK — counts in a dictionary"', cls='R5_TopK', kind='Complexity',
      ctx='Called once per incoming event to update a live leaderboard.',
      answer='Correct output, wrong cost: **every Top(k) sorts the whole map** — O(n log n) per call. Called per event, that is O(events × n log n). The assistant optimised for brevity, not for the call pattern you described.',
      fix='A size-k min-heap over counts (O(n log k)) on demand, or maintain the top-k incrementally if Top is called per event.', test='"R5: answer is right — the defect is cost"'),
 dict(id='R6', title='"rand10 from rand7: add two draws, mod 10"', cls='R6_Rand10', kind='Incorrect assumption',
      ctx='You asked for rand10 using rand7.',
      answer='Sums of two dice are not uniform, and mod 10 does not fix it. Enumerating all 49 pairs gives counts **5 4 4 4 4 4 5 6 7 6** for outputs 1–10 — 9 comes up 7 times in 49, 2 only 4: 75% more likely.',
      fix='Rejection sampling over 49 outcomes (Sampling.Rand10).', test='R6 enumeration note'),
 dict(id='R7', title='"Skips anything malformed so bad input never crashes"', cls='R7_Parse', kind='Edge case / silent data loss',
      ctx='You asked for a tolerant parser.',
      answer='The try/catch wraps the **whole loop**, so the first bad line ends parsing. Every good line after it is dropped, silently, with no count and no reason. 4 lines with the 2nd bad → 1 parsed.',
      fix='Per-line result with a reason (EventParser), counted; never a blanket catch.', test='"R7: one bad line silently drops every line after it"'),
 dict(id='R8', title='"GetOrAdd is atomic, so each profile is loaded once"', cls='R8_ReadThrough', kind='Incorrect assumption / slow dependency',
      ctx='A read-through cache in front of a slow profile service.',
      answer='`GetOrAdd(key, factory)` may run the factory **more than once** under a race — only one result is stored, but every racer pays for a load. **8 concurrent first reads made 8 calls** to the slow source. At a cache miss storm that is a stampede.',
      fix='Store `Lazy<T>` with ExecutionAndPublication: `GetOrAdd(k, _ => new Lazy<…>(…)).Value` → exactly 1 load (tested). For async, `Lazy<Task<T>>`, and evict faulted tasks.', test='"R8 fixed: Lazy collapses concurrent loads to one"'),
 dict(id='R9', title='"Blocking queue with Monitor.Wait/Pulse"', cls='R9_BlockingQueue', kind='Race condition',
      ctx='You asked for a bounded blocking queue.',
      answer='Two defects. `if` instead of `while`: a woken consumer does not re-check, so two consumers woken for one item both dequeue → exception. `Pulse` with one shared monitor: a producer can wake another producer, and the consumer that needed waking sleeps forever. **Hung or threw in 10 of 10 trials.**',
      fix='`while` around every Wait; `PulseAll` (or separate conditions). See BoundedBlockingQueue.', test='R9 stress note: 10/10'),
 dict(id='R10', title='"Background sweeper keeps memory bounded"', cls='R10_Sweeper', kind='Latency / complexity',
      ctx='You asked for cleanup of expired entries without hurting Get latency.',
      answer='The sweep scans **every entry under the lock** to find the expired ones. With 100,000 entries and 10 expired, it examines 100,000 while every reader waits. It bounds memory by moving the cost into a periodic latency spike — the exact thing the requirement said to avoid.',
      fix='A bounded sweep from the cold end of the recency list (budget per tick), or an expiry-ordered structure so expired entries are found without a scan.', test='"R10: removes 10 dead entries by examining all 100,000"'),
]

DEBUG = [
 dict(id='D1', title='LRU evicts the wrong entry', cls='D1_Lru', symptom='"The entry I used most recently is the one that disappears."',
      hint='Which end of the list is "most recent"? Which end does Put evict from?',
      answer='The list keeps most-recent at `First`, and Put evicts `First` — it evicts the MRU entry. Should be `Last`.', fix='`_order.Last` / `RemoveLast()`.'),
 dict(id='D2', title='TTL race: a fresh value vanishes', cls='D2_TtlCache', symptom='"Under load, a value I just wrote is sometimes gone on the next read."',
      hint='Find the gap between deciding an entry is expired and removing it.',
      answer='Get checks expiry outside the lock, then removes **by key** in a second lock. Another thread can Put a fresh value in the gap; the remove deletes the fresh value. Reproduced deterministically with a test seam.',
      fix='Check and remove under one lock — or remove only if the map still holds the same entry you judged.'),
 dict(id='D3', title='BFS visited handling', cls='D3_Bfs', symptom='"Distance is right, but the queue holds about twice as many entries as there are cells."',
      hint='When is a cell marked as seen, and when is it checked?',
      answer='Cells are marked visited on **dequeue**, so a cell can be enqueued once per neighbour before it is processed. **7,081 enqueues for 3,600 cells** on a 60×60 grid; on a word graph with ~25 neighbours per node the factor is ~25×.',
      fix='Mark when enqueued (Maze.ShortestPath does).'),
 dict(id='D4', title='ConcurrentDictionary misuse', cls='D4_Counter', symptom='"Page-view counts are lower than the access log says."',
      hint='Two calls, each atomic. Is the pair atomic?',
      answer='`TryGetValue` then indexer-set is check-then-act: two threads read 5, both write 6. **160,000 hits recorded as ~28–32k** (varies per run).',
      fix='`AddOrUpdate(page, 1, (_, c) => c + 1)` — one atomic read-modify-write. Tested exact.'),
 dict(id='D5', title='Deadlock', cls='D5_Bank', symptom='"The transfer service hangs a few times a day; thread dumps show two threads each waiting on a lock."',
      hint='Transfer(a, b) and Transfer(b, a) at the same moment.', answer='Locks are taken in argument order. Opposite transfers each hold one lock and wait for the other.',
      fix='Acquire in a global order (by account Id). Tested: completes, money conserved.'),
 dict(id='D6', title='Interval merging', cls='D6_Merge', symptom='"Merged coverage is smaller than the input coverage for some batches."',
      hint='What does the merge loop assume about its input?', answer='It assumes sorted input and never sorts. [1,3), [8,10), [2,4) → [2,4) is absorbed into [8,10) and its coverage vanishes.',
      fix='Sort by start first.'),
 dict(id='D7', title='Biased shuffle', cls='D7_Shuffle', symptom='"The shuffled feed puts some orders up far more often than others."',
      hint='How many equally likely paths does the loop have for n = 3? How many orders are there?',
      answer='`pick(a.Length)` instead of `pick(i + 1)`: n=3 makes 3×3 = 9 equally likely paths onto 6 orders — 9 does not divide by 6. Enumeration: counts **1 1 1 2 2 2**.',
      fix='`pick(i + 1)` — Fisher–Yates: 3×2×1 = 6 paths, one per order (tested exactly).'),
 dict(id='D8', title='Tree mutation through aliasing', cls='D8_TreeMerge', symptom='"After merging two config trees, editing the result changed one of the inputs."',
      hint='Which objects in the result are new, and which belong to an input?',
      answer='The result reuses `a.Children` — the same dictionary object. Merging adds b\'s children into **input a**, and editing the result edits a.',
      fix='Build new nodes and new collections all the way down (Fixes.D8_Merge).'),
]

# ================================================================ added Oct 2026 (reader's priority list)
STUDY['logging'] = dict(
 problem='Build a logging library in the four reported phases — severity filtering, tests, throttling identical logs within a window, aggregating what was suppressed — '
         'then make it survive production: many threads, slow or failing sinks, bounded memory.',
 reqs=['`Log(severity, function, line, message)`; levels DEBUG < INFO < WARN < ERROR; print only ≥ the configured minimum',
       'Identical = same severity, function, line and message; within the window, print the first only',
       'When the window has expired and the next identical log arrives, print a summary: count suppressed, stamped with the first occurrence',
       'Multiple sinks; one failing sink must not affect the others or the caller', 'Thread-safe; logging must never become the request path\'s bottleneck'],
 insight='Two different problems hide in one class. **Deciding** what to print is small, shared state (the throttle table) — guard it with a short lock. **Writing** is slow I/O — '
         'never do it under that lock, and in production never do it on the caller\'s thread at all: enqueue into a bounded buffer and let one background writer drain it. '
         'When the buffer is full you drop and count, because a logger that blocks requests has turned an observability tool into an outage.',
 design='Phases 1–4: `Logger` with an injected `IClock`, a `Dictionary<Key, Window>` (key = severity, function, line, message) under one lock, sinks written outside the lock. '
        'Production: `AsyncLogger` over `Channel.CreateBounded` with `FullMode = Wait` and non-blocking `TryWrite`, one pump task, per-sink try/catch, Interlocked metrics, '
        'and a bounded `DisposeAsync` that drains.',
 structs=[('enum Severity', 'Ordered values make filtering one comparison'), ('readonly record struct Key', 'Value equality and hashing for "identical" for free'),
          ('Dictionary<Key, Window>', 'The throttle table: window start, first timestamp, suppressed count'), ('IClock', 'Window tests without sleeping'),
          ('Channel<string> (bounded)', 'Back-pressure and a single reader, without writing a queue by hand'), ('Interlocked counters', 'Metrics read by a scraper without taking a lock')],
 algo=['Filter by severity before anything else — no lock for discarded logs.', 'Under the lock: look up the key. Inside the window → count it, return. Expired → capture a summary if anything was suppressed, reset the window. New → open a window.',
       'Outside the lock: write the summary (if any), then the line, to every sink, each in its own try/catch.',
       'Async: TryWrite into the bounded channel; false → increment dropped. The pump drains with `ReadAllAsync`.'],
 code=[('Phases 1–4 — Logger', F + 'L01_Logger.cs', 'Logger'), ('Production — AsyncLogger', F + 'L01_Logger.cs', 'AsyncLogger')],
 tests=['DEBUG under an INFO minimum is filtered.', 'Three identical WARNs within 1 s → one line.', 'Same message on a different line number is not identical.',
        'After the window, the next identical log prints a summary stamped with the first occurrence ("suppressed 2"), then itself.', 'No summary when nothing was suppressed.',
        'PurgeExpired removes 1,000 one-off windows — the throttle table is bounded.', 'A throwing sink does not stop the next sink.',
        '**10,000 concurrent callers** (32-way): accepted + dropped = 10,000 exactly, and written = accepted (2,291 / 7,709 at capacity 1,024 in one run).',
        'A sink that always throws: 5 failures counted, the pump keeps running.'],
 cx='Log is O(1) expected: one dictionary lookup under a short lock, plus the writes. AsyncLogger.Log is O(1) and never waits. Memory: O(distinct live keys) for throttling, O(capacity) for the buffer.',
 ladder=[('Severity filtering.', 'Ordered enum, one comparison, before any locking.'), ('Unit tests.', 'Inject the clock and a recording sink; test window edges exactly.'),
         ('Throttle identical logs.', 'Key = (severity, function, line, message) as a record struct; window per key.'),
         ('Aggregate the suppressed.', 'Summary on the first identical log after expiry, stamped with the first occurrence.'),
         ('10,000 threads logging at once.', 'The throttle lock is held for a lookup only; writes happen outside it. Beyond that: per-thread buffers or the async logger.'),
         ('Logging must not become the bottleneck.', 'Callers enqueue into a bounded channel and return; one background writer does the I/O.'),
         ('Do not overwhelm downstream.', 'Bounded buffer + drop-and-count; per-key throttling; sampling of DEBUG; batching writes to the sink.'),
         ('A sink fails.', 'Per-sink try/catch, a failure counter, and a fallback (stderr) — never an exception into the caller.')],
 conc='Shared state: the throttle table (and, async, the channel). Two threads logging the same key at once must not both print it: the read-decide-update of the window is one '
      'critical section. Writing to sinks is deliberately outside it — the review exercise R11 holds the lock across I/O and serialised 200 calls into ~460 ms.',
 prod=['Metrics: accepted, dropped, written, sink failures, buffer depth. **Alert on drops** — that is data loss in your observability.',
       'Configuration: minimum level and window per logger, changeable at runtime without a restart.',
       'Shutdown: complete the channel, drain with a deadline, report what was lost.', 'Never log secrets; redact at the call site or in a sink filter.'],
 ai=['Delegate the enum, the record key and the sink interface — pure boilerplate.', 'Own the throttle state machine (new / inside window / expired-with-suppressed) — write it yourself or specify it exactly.',
     'Ask for tests with the Tests template, and check every expected timestamp in the summaries.',
     'If the assistant proposes `BoundedChannelFullMode.DropWrite` with a drop counter, ask what `TryWrite` returns when it drops — then check the docs.'],
 traps=['Writing to the sink inside the lock (R11).', '`DropWrite` with a counter on `TryWrite == false` — under DropWrite, TryWrite returns **true** when it drops, so drops are silent (R14). '
        '**My own first version did exactly this**; the 10,000-thread test reported 10,000 accepted, 0 dropped, 1,026 written.',
        'An unbounded throttle table keyed on messages that contain request ids.', '`DateTime.Now` in the throttle — tests then depend on wall-clock timing.',
        'Summary stamped with the expiry time instead of the first occurrence (the reported spec says first occurrence).'],
)

INTERVIEW['logging'] = _rounds(
   ('"We need a logging library. Start with this: it is created with a minimum severity — DEBUG, INFO, WARN, ERROR — and only prints logs at or above it."',
    ['Asks how severities order', 'Asks the log signature (function, line, message)', 'Keeps phase 1 tiny: one comparison']),
   ('"Implement it, and show me it is testable."', ['Injects a clock and a sink', 'Writes the tests, not just the code']),
   ('"Our console is being spammed. If an identical log — same severity, function, line and message — repeats within a time window, print only the first. '
    'Then: when the window expires and the next identical log arrives, print a summary of how many were suppressed, using the first occurrence\'s timestamp."',
    ['Asks window length and whether it is per key', 'Record-struct key', 'State machine: new / inside / expired-with-suppressed', 'Does not restart the class']),
   ('"Test the throttling and the summary."', ['Window edges exactly', 'Different line number is not identical', 'No summary when nothing was suppressed']),
   ('"Here is what the assistant wrote to make it production-ready." (R14.)', ['Asks what TryWrite returns under DropWrite', 'Spots the silent drop']),
   ('"10,000 threads are logging at once. What breaks?"', ['Lock scope', 'I/O off the caller thread', 'Bounded buffer, drop and count', 'Alert on drops']))

# ---------------------------------------------------------------- review additions
REVIEW += [
 dict(id='R11', title='"A thread-safe logger: one lock so lines never interleave"', cls='R11_Logger', kind='Bottleneck / contention',
      ctx='You asked for a thread-safe logger.',
      answer='The lock is held **across the sink write** — slow I/O. Every logging thread queues behind it. With a 2 ms sink, 8 threads × 25 logs took **~460 ms**: the callers were fully serialised, so a slow disk now throttles every request.',
      fix='Hold a lock only for shared decision state; do the I/O outside it — in production, on a background writer behind a bounded channel (AsyncLogger: callers returned in ~0 ms).',
      test='"R11: 200 logs × 2 ms sink take ≥ 400 ms"'),
 dict(id='R12', title='"Async read-through cache — SemaphoreSlim, since you cannot await inside a lock"', cls='R12_AsyncCache', kind='Incorrect async behaviour',
      ctx='You asked for an async read-through cache.',
      answer='`Release()` is not in a `finally`. When the load throws, the semaphore is **never released** — every later call waits forever. One failed load and the cache is dead. '
             'It also serialises every load behind one semaphore, so one slow key blocks all keys.',
      fix='`try { … } finally { _gate.Release(); }`; better, cache `Lazy<Task<T>>` per key (no global gate) and evict faulted tasks so a failure is retried.',
      test='"R12: one failed load leaves the semaphore held — every later call hangs"'),
 dict(id='R13', title='"Counts events in the last N seconds"', cls='R13_Window', kind='Off-by-one',
      ctx='You asked for a 5-minute event counter.',
      answer='`_stamp[i] >= now - _w` includes the second exactly `window` seconds ago — a 301-second window. An event at t=0 is still counted at t=300.',
      fix='`> now - _w` (WindowCounter). Test exactly at the boundary, not one past it.', test='"R13: event from exactly 300 s ago still counted"'),
 dict(id='R14', title='"Non-blocking logger: a bounded channel that drops when full, with a drop counter"', cls='R14_AsyncLogger', kind='Incorrect API assumption',
      ctx='You asked for a logger that never blocks callers and reports how much it dropped.',
      answer='Under `BoundedChannelFullMode.DropWrite`, **`TryWrite` returns true even when it drops the item**. The drop counter never moves. Measured: **accepted 10,000, dropped 0, written ~1,050**. '
             'The dashboard says nothing was lost while nine in ten logs were. (My own first AsyncLogger had this bug; the 10,000-thread test caught it.)',
      fix='`FullMode = Wait` with non-blocking `TryWrite` (returns false when full), or the `itemDropped` callback overload of `CreateBounded`.',
      test='"R14: reports zero drops while writing far fewer than it accepted"'),
]

# Which flawed listing the simulator shows in its "Would you ship this?" round, per question.
REVIEW_FOR = {
 'lru': 'R3', 'lrucount': 'R2', 'lfurank': 'R1', 'rankcache': 'R1', 'logging': 'R14', 'records': 'R7', 'intervals': 'R4', 'covered': 'R4',
 'distance': 'D3', 'taskmgr': 'R12', 'wordladder': 'D3', 'maze': 'D3', 'rand10': 'R6', 'biased': 'R6', 'randbag': 'D7',
 'queue': 'R9', 'scheduler': 'R10', 'mergetrees': 'D8', 'leaves': 'D8', 'topk': 'R5', 'window': 'R13',
}

# ---------------------------------------------------------------- follow-up engine, five levels
# Only follow-ups that arise naturally from each problem. (question, what a strong answer covers)
FU = {
 'lru': {1: [('Capacity 0? Re-put of an existing key? Get on a key that expired exactly now?', 'Reject 0 at construction; update in place + renew; now == expiry is expired')],
         2: [('Complexity of Get, Put and the sweep?', 'O(1), O(1), O(budget) — and why the sweep is bounded'), ('Where is the bottleneck?', 'Not the algorithm — the single lock')],
         3: [('Two threads call Get on different keys at once. What shared state do they touch?', 'Both move nodes in one list: map + list invariant → one critical section'),
             ('Lock or ConcurrentDictionary?', 'Lock — the invariant spans two structures'), ('Can this deadlock? Can the lock become a bottleneck?', 'One lock, no callouts → no deadlock; yes under contention → shard')],
         4: [('100× traffic, one hot key.', 'Shard by hash; hot key still one shard → front cache or approximate recency'), ('Memory pressure.', 'Byte-weighted capacity; Resize down')],
         5: [('What do you measure and alert on?', 'Hit ratio (relative drop), evictions by reason, lock wait, size'), ('The source behind it goes down.', 'Serve stale with a bound, circuit breaker, collapse concurrent misses'),
             ('What happens during a deploy?', 'Cold cache → stampede on the source; warm up or ramp traffic')]},
 'lrucount': {1: [('What counts as an eviction — does an update?', 'No; only inserting a new key into a full cache')], 2: [('Cost of the counters?', 'O(1); the simulator is O(requests)')],
              3: [('A scraper reads the counters while requests run.', 'Snapshot under the cache lock, or Interlocked.Read and accept approximation')],
              4: [('A nightly scan of every key.', 'Flushes the hot set — scan-resistant policy or bypass')], 5: [('What do you alert on?', 'Relative hit-ratio drop with request rate alongside')]},
 'lfurank': {1: [('GetRank on a missing key? Ties at the minimum frequency?', '−1; least recent loses')], 2: [('Complexity of GetRank — and of Get/Put given the sorted counts?', 'O(F + B); O(log F)'), ('Can GetRank be O(log n)?', 'Order-statistics / Fenwick')],
             3: [('Thread-safety — reader/writer lock?', 'One lock; Get writes, so RW does not help')], 4: [('Millions of keys; frequencies grow forever.', 'Aging (halve periodically) or W-TinyLFU')], 5: [('How would you know the cache has fossilised?', 'Age of evicted entries, hit ratio on new keys')]},
 'logging': {1: [('Null or empty message? Unknown severity? Window of 0?', 'Validate or log as-is — decide; window 0 disables throttling')],
             2: [('Cost per Log call?', 'O(1) expected; filter before the lock'), ('Where is the bottleneck?', 'Sink I/O — it must not be under the lock')],
             3: [('10,000 threads logging simultaneously — what is shared?', 'Throttle table → short lock; the sink → off-thread'), ('Lock or ConcurrentDictionary for the throttle table?', 'Read-decide-update per key: one lock (or AddOrUpdate with care)'),
                 ('Could synchronisation become the bottleneck?', 'Only if I/O is inside it; otherwise stripe the table by key hash')],
             4: [('Logs overwhelm downstream.', 'Bounded buffer, drop-and-count, sampling, batching'), ('Millions of distinct messages.', 'Purge expired windows; cap the table')],
             5: [('What do you alert on?', 'Drops and sink failures'), ('The log sink is down for ten minutes.', 'Buffer then drop with counts; fallback sink'), ('Deploying a config change to the level.', 'Runtime-reloadable, no restart')]},
 'records': {1: [('Missing fields, wrong types, nested objects, an empty file?', 'Result type with a reason per line; empty → empty summary')],
             2: [('Time and memory?', 'O(lines); O(actions + distinct users)'), ('What if N is very large?', 'Already streaming')],
             3: [('Make it thread-safe / parallel.', 'Per-worker accumulators, merge at the end — no shared lock')],
             4: [('The JSON is 1 GB. Can we avoid loading it?', 'Line-by-line streaming; for one big array, Utf8JsonReader'), ('Distinct users at scale.', 'HyperLogLog, ~1–2% error')],
             5: [('What do you monitor?', 'Reject rate by reason'), ('Upstream changes the schema.', 'Reject spike alert; tolerant reader for additive changes')]},
 'intervals': {1: [('Touching intervals? Inverted? Duplicate add?', 'Half-open → touching merges; reject inverted; idempotent')],
               2: [('Brute force vs this?', 'Re-sort list O(n log n) per add vs O(log n) amortised'), ('Very large N?', 'Still log n; memory is the limit')],
               3: [('Concurrent writers and readers.', 'One lock per op; volatile snapshot for CoveredLength')], 4: [('Millions of intervals, range-sum queries.', 'Segment tree over compressed coordinates')],
               5: [('How do you test it in CI?', 'Property test vs a bitmap oracle')]},
 'maze': {1: [('Empty, ragged, no S or E, S equals E?', 'Constructor validation; IsWellFormed rules')], 2: [('BFS cost? Generation cost?', 'O(cells) each'), ('Very large maze?', 'Iterative generation; memory O(cells)')],
          3: [('Many path queries at once.', 'Immutable after construction → no locks')], 4: [('A 10,000 × 10,000 maze.', 'Bit-packed walls; bidirectional BFS')], 5: [('A user reports a broken maze.', 'Seeded generation reproduces it')]},
 'rand10': {1: [('What if rand7 is not uniform?', 'Then nothing downstream is — state the assumption')], 2: [('Expected calls? Worst case?', '≈2.45; unbounded but geometric')],
            3: [('Many threads call it.', 'Random is not thread-safe: Random.Shared or per-thread')], 4: [('Billions of calls — reduce source calls.', 'Reuse rejected entropy')],
            5: [('How do you test uniformity in CI?', 'Exact enumeration with an injected source, not a chi-square on samples')]},
 'queue': {1: [('Capacity 0? Dequeue after complete? Enqueue after complete?', 'Reject; false when drained; throw')], 2: [('Cost of PulseAll?', 'Wakes all waiters — fine small, use two conditions at scale')],
           3: [('Two producers, queue has one slot.', 'Both wait in the while loop; one wins'), ('Could this deadlock?', 'Not with one monitor and while-loops')],
           4: [('Consumers 10× slower.', 'Bounded capacity is back-pressure; block, drop or reject')], 5: [('Shutdown with items in flight.', 'Complete, drain with a deadline'), ('A poison item.', 'Per-item catch, dead-letter')]},
 'window': {1: [('Window edge — is an event exactly W seconds old counted?', 'No: (now − W, now]')], 2: [('Read cost?', 'O(W); O(1) with a running total')],
            3: [('Record from many threads.', 'Stamp check-and-reset is the race → lock')], 4: [('Per user, ten million users.', 'Sketches; coarser buckets')], 5: [('Across machines.', 'Local counters, periodic aggregation')]},
}
_GENERIC_FU = {
 1: [('What are the edge cases — empty, duplicates, missing values, invalid input?', 'Names them and says what the code does for each')],
 2: [('Time and space complexity? Can it be improved? What happens as N grows?', 'States both, names the bottleneck')],
 3: [('Can multiple threads call this? What is shared, and where is the race?', 'Names the shared invariant and the boundary — or says why none is needed')],
 4: [('10× and 100× the load or the input size — what breaks first?', 'Memory, contention or algorithmic cost, in that order of likelihood')],
 5: [('How would you test, monitor and debug this in production?', 'Tests, the one metric that matters, the failure mode')],
}
for _q, _d in LINKED.items():
    if _q not in FU:
        lad = _d['ladder']
        FU[_q] = {1: _GENERIC_FU[1], 2: _GENERIC_FU[2],
                  3: [('What happens if two threads use this at once?', _d['conc'] if _d['conc'] != '—' else 'Nothing shared → say so; do not add locks')],
                  4: [(lad[-1][0], lad[-1][1])] if lad else _GENERIC_FU[4], 5: _GENERIC_FU[5]}

LEVELS = {1: 'Correctness', 2: 'Complexity', 3: 'Concurrency', 4: 'Scale', 5: 'Productionisation'}

# ---------------------------------------------------------------- C# deep-dive bank
# Asked only when the solution uses the feature. (question, answer)
CSHARP = {
 'Dictionary': [
   ('Expected complexity?', 'O(1) average for lookup, insert, remove; O(n) worst case if many keys collide. Enumeration is O(n) and order is not guaranteed.'),
   ('How are collisions handled?', 'Separate chaining, but without node objects: an `int[] buckets` of indices into an `Entry[]` array, each entry carrying its hash, key, value and a `next` index. Colliding keys form a chain through `next`.'),
   ('What happens on resize?', 'When the entries array is full it grows to a larger prime (about double) and every entry is rehashed into new buckets — O(n) for that insert, amortised O(1). Pre-size with the constructor capacity when you know n.'),
   ('Memory behaviour?', 'Removing does not shrink anything: freed slots go on a free list for reuse. `TrimExcess()` shrinks. A struct key that is large is copied into every entry.')],
 'ConcurrentDictionary': [
   ('Which operations are atomic?', 'Each single call: `TryAdd`, `TryRemove`, `TryUpdate` (compare-and-swap on the value), `TryGetValue`, the indexer. `AddOrUpdate`/`GetOrAdd` atomically *store* — but see the next question.'),
   ('Does a read take a lock?', 'No — reads are lock-free. Writes lock one stripe of buckets (lock striping), not the whole table. `Count` and `ToArray` take *all* the locks, so avoid them on a hot path.'),
   ('Is a read-modify-write across two calls safe?', 'No. `TryGetValue` then `d[k] = v + 1` is check-then-act (debugging exercise D4 lost ~80% of increments). Use `AddOrUpdate`, or a `TryUpdate` loop.'),
   ('Do GetOrAdd / AddOrUpdate run the factory once?', 'Not guaranteed: the delegate runs outside the lock and can run on several racing threads; only one result is stored. For an expensive factory, store `Lazy<T>` (review exercise R8).')],
 'lock': [
   ('What exactly is synchronised?', 'Only code that locks the *same object*. `lock (x)` is `Monitor.Enter/Exit` on x\'s object header, in a try/finally. It also acts as a full memory barrier, so writes inside are visible to the next locker.'),
   ('Can this deadlock?', 'Yes, with two locks taken in different orders (D5), or with a call out to unknown code while holding the lock. One lock and no callouts cannot deadlock. `Monitor` is re-entrant for the same thread.'),
   ('How does contention affect throughput?', 'Uncontended, a lock is tens of nanoseconds. Contended, threads spin briefly then block, causing context switches; throughput collapses toward one thread\'s worth. The fix is less work under the lock, or more locks (striping).'),
   ('Anything to avoid locking on?', '`this`, a `Type`, a string — other code can lock them too. Use a private readonly object (or `System.Threading.Lock` in .NET 9+).')],
 'async/await': [
   ('Does async create a new thread?', 'No. `async` lets a method be suspended; `await` on an incomplete task returns to the caller and schedules the rest as a continuation. No thread exists for the waiting.'),
   ('What happens while awaiting I/O?', 'The OS completes the I/O (I/O completion ports on Windows, epoll on Linux) and the continuation is queued to the thread pool or the captured context. The thread was free the whole time — that is the point.'),
   ('How does cancellation work?', 'Cooperatively. You pass a `CancellationToken` down; APIs that accept it observe it and throw `OperationCanceledException`. Nothing is aborted from outside. Blocked primitives need a registration to wake them (BoundedBlockingQueue does this).'),
   ('Can you await inside a lock?', 'No — the compiler forbids it, because the continuation may run on another thread. Use `SemaphoreSlim.WaitAsync` with `Release` in a `finally` (R12 is what happens without the finally).')],
 'LINQ': [
   ('Deferred or immediate?', 'Most operators (`Where`, `Select`, `OrderBy`) are deferred: nothing runs until enumeration. `ToList`, `ToArray`, `Count()`, `First`, `Sum` execute immediately. `OrderBy` is deferred but buffers everything when enumerated.'),
   ('What does enumerating twice cost?', 'The whole pipeline runs twice — including any I/O behind the source. Materialise once with `ToList()` if you need it twice.'),
   ('Allocations?', 'An enumerator per operator, plus delegate and closure allocations for captured variables. Negligible for setup code, measurable in a per-request hot path.'),
   ('When is an explicit loop better?', 'Hot paths, early exit with complex state, mutating as you go, or when you need to state complexity exactly — R5 hid an O(n log n) sort per call inside one readable line.')],
 'LinkedList': [
   ('Why LinkedList<T> for LRU?', 'O(1) `Remove(node)`, `AddFirst`, `RemoveLast` given a `LinkedListNode<T>` handle. Storing the handle in the dictionary avoids an O(n) search.'),
   ('Is it thread-safe?', 'No. Concurrent `Remove`/`AddFirst` corrupts its pointers (R3 corrupted in 20/20 runs).')],
 'SortedSet / SortedDictionary': [
   ('Complexity?', 'Red-black tree: O(log n) insert, remove, lookup; in-order enumeration.'),
   ('How do you get a floor (largest ≤ x)?', '`GetViewBetween(min, x).Max` — O(log n). There is no `floorKey` like Java\'s TreeMap.')],
 'Channel / Interlocked / SemaphoreSlim': [
   ('What does a bounded Channel do when full?', 'Depends on `FullMode`. `Wait`: `WriteAsync` waits, `TryWrite` returns false. `DropWrite/DropNewest/DropOldest`: drops and `TryWrite` returns **true** (R14).'),
   ('When Interlocked instead of a lock?', 'A single-word update with no invariant tying it to other fields — counters. Two fields that must agree need a lock.'),
   ('SemaphoreSlim vs lock?', 'SemaphoreSlim can be awaited (`WaitAsync`) and counts beyond 1; it is not re-entrant and must be released in a `finally`.')],
}
FEATURES = {
 'lru': ['Dictionary', 'LinkedList', 'lock', 'ConcurrentDictionary'], 'lrucount': ['Dictionary', 'LinkedList', 'Channel / Interlocked / SemaphoreSlim', 'LINQ'],
 'lfurank': ['Dictionary', 'SortedSet / SortedDictionary', 'LinkedList', 'lock'], 'rankcache': ['SortedSet / SortedDictionary', 'Dictionary', 'lock'],
 'logging': ['Dictionary', 'lock', 'Channel / Interlocked / SemaphoreSlim', 'async/await'], 'records': ['Dictionary', 'LINQ', 'async/await'],
 'intervals': ['SortedSet / SortedDictionary', 'LINQ', 'lock'], 'covered': ['SortedSet / SortedDictionary'],
 'distance': ['Dictionary', 'LINQ'], 'taskmgr': ['Dictionary', 'lock', 'async/await'], 'wordladder': ['Dictionary', 'LINQ'], 'maze': ['LINQ'],
 'rand10': [], 'biased': [], 'randbag': ['Dictionary', 'lock'], 'queue': ['lock', 'Channel / Interlocked / SemaphoreSlim', 'async/await'],
 'scheduler': ['lock', 'async/await', 'SortedSet / SortedDictionary'], 'mergetrees': ['Dictionary', 'LINQ'], 'leaves': ['LINQ'], 'topk': ['Dictionary', 'LINQ'],
 'window': ['lock', 'Channel / Interlocked / SemaphoreSlim'],
}
