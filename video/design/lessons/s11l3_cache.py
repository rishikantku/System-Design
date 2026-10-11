# -*- coding: utf-8 -*-
"""Chapter 11, Lesson 3 — an in-memory cache with pluggable eviction, then distributed."""
from lib import *

lesson_header('11.3', 'Design a distributed in-memory cache with pluggable eviction',
              'Strategy-pattern eviction &middot; O(1) LRU / LFU &middot; consistent hashing &middot; Redis internals',
              dict(reports='Candidate reports, LLD then HLD', latest='2025', level='Staff and Senior',
                   conf='MEDIUM &mdash; reported more than once, straddles coding', sources='LeetCode Discuss'), 17,
              """Lesson three. Design a flexible in-memory cache with configurable capacity and eviction """
              """policies &mdash; and then the interviewer zooms out: now make it distributed, and tell me """
              """how Redis does it. This one straddles the coding round and the design round, which is """
              """exactly why it catches people: they answer one half brilliantly and run out of time """
              """before the other.""")

evidence('Where this question comes from', [
 ('LeetCode Discuss &mdash; LinkedIn interview reports', '2025', 'Staff / Senior',
  '<b>Flexible in-memory cache with customisable capacity and eviction policies</b>, extended to an '
  '<b>HLD for distributed systems</b>, with discussion of <b>Redis internals</b>'),
 ('Already in this workspace', '—', '—',
  'The design page lists it as <b>MEDIUM, straddles the coding round</b>; the coding course covers LRU in C#'),
], """Medium confidence: it shows up in candidate summaries, and it matches LinkedIn's habit of asking """
   """design questions that start low-level.""",
 ["""The shape to expect is two halves: an object-oriented design with the right data structures, then """
  """a distributed system. Budget about fifteen minutes for the first half and keep moving."""],
 caveat='Summaries from search results; the individual posts could not be read directly.',
 narration_caveat="""These come from search summaries of the posts, because the posts themselves could not be """
                  """read directly. So treat the exact wording as approximate.""")

sid = beat('Why this is interesting', 'Two interviews in one &mdash; and the clock is the enemy',
           '<div style="font-size:28px;line-height:1.72">'
           '<b>Half one &mdash; low-level design:</b> a <code>Cache</code> with a capacity and a '
           '<i>pluggable</i> eviction policy. The test is <b>abstraction</b>: can a new policy be added '
           'without touching the cache?<br><br>'
           '<b>Half two &mdash; high-level design:</b> spread it over many nodes. The test is '
           '<b>partitioning, replication and hot keys</b>.<br><br>'
           '<span style="color:#ff9a9a">The common failure: 35 minutes perfecting LFU, 5 minutes on the '
           'distributed part.</span><br><br>'
           '<span style="color:#a8e6a3">The move: state the interface and the two O(1) structures fast, '
           'then say &ldquo;each node runs this; now let me distribute it&rdquo;.</span></div>',
           """Why is this interesting? Because it is two interviews in one, and the clock is the enemy.""", step=0)
seg(sid, 1, """Half one is low-level design: a cache with a capacity and a pluggable eviction policy. The """
            """test is abstraction &mdash; can someone add a new policy without editing the cache?""")
seg(sid, 2, """Half two is high-level design: spread it across many nodes. The test is partitioning, """
            """replication and hot keys.""")
seg(sid, 3, """The common failure is spending thirty-five minutes perfecting L-F-U and five minutes on the """
            """distributed part, which is where the staff signal lives.""")
seg(sid, 4, """So state the interface and the two constant-time structures quickly, then say: each node runs """
            """this, now let me distribute it.""")

think('LRU needs get, put and evict all in O(1). Which two data structures, and what does each one hold?',
      15,
      """Pause. L-R-U needs get, put and evict all in constant time. Which two data structures, and what """
      """does each one hold?""",
      """Hold that. It is the first half of deep dive one.""")

clarify('What I would clarify first', [
 ('Capacity in entries or in bytes?',
  '<b>Bytes</b> is what production needs &mdash; values vary wildly. It changes eviction to &ldquo;evict until '
  'it fits&rdquo;.'),
 ('Which policies &mdash; LRU, LFU, FIFO, TTL?',
  'The design must make the policy a <b>strategy</b>; the list only decides which you implement first.'),
 ('Thread-safe? How much concurrency?',
  'One global lock is correct and slow. <b>Segments (lock striping)</b> scale.'),
 ('Cache-aside, or read-through / write-through?',
  'Read-through means the cache calls the loader, which brings <b>stampede protection</b> into scope.'),
 ('For the distributed part: can we lose cached data?',
  'If yes, no replication needed &mdash; a node loss is a miss storm. If no, it is a <b>database</b>, not a cache.'),
 ('Consistency with the source of truth?',
  'TTL-only is simplest; invalidation on write is fresher and harder.'),
], [
 """Capacity in entries or bytes? Bytes is what production needs, because values vary wildly, and it changes """
 """eviction into &ldquo;evict until it fits&rdquo;.""",
 """Which policies? The design must make the policy a strategy; the list only decides which one you write """
 """first.""",
 """Thread safety? One global lock is correct and slow. Segments with their own locks scale.""",
 """Cache-aside, or read-through? Read-through means the cache calls the loader itself, which brings stampede """
 """protection into scope.""",
 """For the distributed part: is it acceptable to lose cached data? If yes, you do not need replication """
 """&mdash; a node loss is just a burst of misses. If no, you are designing a database, and you should say """
 """so.""",
 """And consistency with the source of truth: T-T-L only is simplest; invalidating on write is fresher and """
 """harder.""",
])

capacity('Capacity', [
 ('Working set', 'assume 2 TB of hot data', '2 TB',
  'Far beyond one machine. <b>Partition</b>'),
 ('Node size', '64 GB RAM, ~50 GB usable for data', '&asymp; 40 nodes',
  'Plus headroom &rarr; ~50 nodes'),
 ('Request rate', 'assume 2M ops / s', '&asymp; 40k ops / s per node',
  'Comfortable for one node; <b>a single hot key</b> is not'),
 ('Hot key', '1 key at 200k ops / s', '&gt; one node&rsquo;s budget',
  '<b>Rules out pure hashing for hot keys</b> &mdash; replicate them or cache client-side'),
 ('Per-entry overhead', 'hash entry + list pointers + key', '&asymp; 50&ndash;80 B',
  'Matters for small values: 100M tiny entries = several GB of pointers'),
], [
 """Numbers, as assumptions. Two terabytes of hot data is far beyond one machine, so partition.""",
 """With sixty-four gigabyte nodes and about fifty usable for data, that is forty nodes, call it fifty with """
 """headroom.""",
 """Two million operations a second across fifty nodes is forty thousand per node &mdash; comfortable. A """
 """single hot key is not.""",
 """One key at two hundred thousand operations a second exceeds any one node's budget, which rules out pure """
 """hashing for hot keys. You replicate them or cache them client-side.""",
 """And per-entry overhead &mdash; hash entry, list pointers, the key &mdash; is fifty to eighty bytes, which """
 """dominates when values are small.""",
])

A = Arch('Cache &mdash; one node, then many', kicker='Architecture', height=800)

A.zone(60, 120, 760, 600, 'ONE NODE — the low-level design')
A.zone(880, 120, 900, 600, 'MANY NODES — the high-level design')

A.box('iface', 100, 160, 300, 100, 'Cache<K,V>', 'get, put, remove, capacity', kind='ok', step=0, focus=0)
A.box('pol',   460, 160, 320, 100, 'IEvictionPolicy', 'onAccess, onInsert, victim()', kind='shared', step=0, focus=[0, 1])
A.arrow('iface', 'pol', step=0, focus=0, label='delegates')
A.box('lru',   460, 320, 150, 90, 'LRU', 'map + list', kind='info', step=1, focus=1, small=True)
A.box('lfu',   630, 320, 150, 90, 'LFU', 'freq buckets', kind='info', step=1, focus=1, small=True)
A.arrow('pol', 'lru', step=1, focus=1, fs='b', ts='t')
A.arrow('pol', 'lfu', step=1, focus=1, fs='b', ts='t')
A.box('seg',   100, 320, 300, 110, 'Segments', 'N shards, one lock each', kind='ok', step=2, focus=2)
A.arrow('iface', 'seg', step=2, focus=2, fs='b', ts='t')
A.box('ttl',   100, 500, 300, 100, 'Expiry', 'lazy on read + sampled sweep', kind='shared', step=2, focus=2, small=True)

A.box('cli',   920, 160, 220, 100, 'Client library', 'hash ring, retries', kind='info', step=3, focus=[3, 4])
A.box('ring',  1220, 160, 260, 100, 'Consistent hash ring', 'virtual nodes', kind='ok', step=3, focus=3)
A.arrow('cli', 'ring', step=3, focus=3)
A.box('n1',    920, 380, 200, 110, 'Node A', 'primary + replica', kind='dp', step=4, focus=4, small=True)
A.box('n2',    1170, 380, 200, 110, 'Node B', 'primary + replica', kind='dp', step=4, focus=4, small=True)
A.box('n3',    1420, 380, 200, 110, 'Node C', 'primary + replica', kind='dp', step=4, focus=4, small=True)
A.arrow('ring', 'n1', step=4, focus=4, fs='b', ts='t')
A.arrow('ring', 'n2', step=4, focus=4, fs='b', ts='t')
A.arrow('ring', 'n3', step=4, focus=4, fs='b', ts='t')
A.box('hot',   920, 570, 340, 100, 'Hot-key handling', 'replicate key, or near-cache', kind='bad', step=5, focus=5, small=True)
A.box('cfg',   1320, 570, 300, 100, 'Membership', 'config service / gossip', kind='shared', step=6, focus=6, small=True)

A.narrate(0, """One node first. The cache exposes get, put and remove with a capacity, and delegates every """
             """eviction decision to an eviction-policy interface: notify on access, notify on insert, and """
             """name a victim. That is the strategy pattern, and it is the whole low-level answer to """
             """&ldquo;pluggable&rdquo;.""")
A.narrate(1, """Each policy is a class behind that interface. L-R-U is a hash map plus a doubly linked list. """
             """L-F-U is a hash map plus frequency buckets. Adding FIFO or a size-aware policy means a new class """
             """and no change to the cache.""",
          A.flow([(620, 260), (535, 320)]))
A.narrate(2, """For concurrency, split the cache into segments, each with its own lock and its own policy """
             """instance, chosen by key hash. And expiry is lazy on read plus a sampled background sweep, """
             """which is how Redis does it.""")
A.narrate(3, """Now many nodes. A client library hashes keys onto a consistent hash ring with virtual nodes, """
             """so adding a node moves about one over N of the keys instead of nearly all of them.""",
          A.flow([(1140, 210), (1220, 210)]))
A.narrate(4, """Each node runs the single-node design from the left, with a replica if the data is expensive to """
             """reload.""")
A.narrate(5, """Hot keys get special handling: replicate the hottest keys to several nodes, or put a small """
             """near-cache in the client with a short T-T-L.""")
A.narrate(6, """And membership &mdash; which nodes exist &mdash; comes from a config service or gossip, so clients """
             """agree on the ring.""")
A.build()

sid = beat('Deep dive 1', 'The O(1) structures, and why the policy is a strategy',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>LRU:</b> <code>Dictionary&lt;K, Node&gt;</code> + <b>doubly linked list</b> ordered by recency.<br>'
           '&bull; get: map lookup, move node to head &mdash; O(1)<br>'
           '&bull; evict: remove tail &mdash; O(1). The list needs <i>prev</i> pointers to unlink in O(1)<br><br>'
           '<b>LFU:</b> map key &rarr; node, plus map <b>frequency &rarr; list</b>, plus <code>minFreq</code>.<br>'
           '&bull; access: move node from list f to list f+1 &mdash; O(1)<br>'
           '&bull; evict: tail of list <code>minFreq</code> &mdash; O(1)<br>'
           '&bull; <span style="color:#ffd483">Pure LFU never forgets an old favourite &mdash; add <b>aging</b> '
           '(halve counts periodically)</span><br><br>'
           '<b>The abstraction:</b><br>'
           '<code>interface IEvictionPolicy&lt;K&gt; { void OnAccess(K); void OnInsert(K); void OnRemove(K); K Victim(); }</code>'
           '<br><span style="color:#a8e6a3">The cache owns storage; the policy owns <i>order</i>. Neither knows '
           'the other&rsquo;s internals &mdash; that is what makes it pluggable and testable.</span><br><br>'
           '<b>Capacity in bytes:</b> evict in a loop until <code>used + size(new) &le; capacity</code>.</div>',
           """Deep dive one: the constant-time structures, and the answer to the pause.""", step=0)
seg(sid, 1, """L-R-U is a dictionary from key to node, plus a doubly linked list ordered by recency. Get is a """
            """lookup and a move to the head. Evict removes the tail. And the list must be doubly linked, """
            """because unlinking a node in constant time needs its previous pointer.""")
seg(sid, 2, """L-F-U is a map from key to node, a map from frequency to a list of nodes, and the current """
            """minimum frequency. An access moves a node from list f to list f plus one; eviction takes the """
            """tail of the minimum-frequency list. Both constant time.""")
seg(sid, 3, """And pure L-F-U never forgets an old favourite: something hammered last month stays forever. """
            """Add aging &mdash; halve every count periodically. Saying that shows you have run one.""")
seg(sid, 4, """The abstraction is an eviction-policy interface with on-access, on-insert, on-remove and """
            """victim. The cache owns storage; the policy owns order. Neither knows the other's internals, """
            """which is what makes the policy pluggable and testable in isolation.""")
seg(sid, 5, """And with capacity in bytes, eviction becomes a loop: keep evicting until the new value fits.""")

sid = beat('Deep dive 2', 'Distributing it &mdash; and how Redis actually does it',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Partitioning:</b> consistent hashing with virtual nodes &mdash; a node joining moves ~1/N of '
           'keys. <b>Redis Cluster</b> instead uses <b>16,384 hash slots</b> (CRC16 of the key mod 16384) '
           'assigned to nodes; moving a slot is the unit of rebalancing.<br><br>'
           '<b>Replication:</b> async primary &rarr; replica. A failover can <b>lose recent writes</b> &mdash; '
           'fine for a cache, say so.<br><br>'
           '<b>Redis internals worth naming:</b><br>'
           '&bull; Commands execute on a <b>single thread</b> &mdash; no locks, atomic operations; I/O '
           'threading was added in 6.0<br>'
           '&bull; Eviction is <b>approximated LRU/LFU</b>: sample a few keys (maxmemory-samples, default 5), '
           'evict the best candidate &mdash; no global list, near-LRU quality<br>'
           '&bull; Expiry: lazy on access + a periodic <b>random sampling</b> of keys with TTLs<br>'
           '&bull; Persistence optional: RDB snapshots, AOF log<br><br>'
           '<span style="color:#a8e6a3"><b>The insight:</b> exact LRU across a huge keyspace costs pointers and '
           'locks on every read. Redis trades exactness for a sample &mdash; the same trade you should offer.'
           '</span></div>',
           """Deep dive two: distributing it, and how Redis actually does it.""", step=0)
seg(sid, 1, """Partitioning with consistent hashing and virtual nodes means a node joining moves about one """
            """over N of the keys. Redis Cluster does something slightly different and worth naming: sixteen """
            """thousand three hundred and eighty-four hash slots, a C-R-C sixteen of the key modulo that, with """
            """slots assigned to nodes. Moving a slot is the unit of rebalancing.""")
seg(sid, 2, """Replication is asynchronous, primary to replica, so a failover can lose recent writes. For a """
            """cache that is acceptable &mdash; but say it explicitly.""")
seg(sid, 3, """Redis internals. Commands execute on a single thread, so there are no locks and every """
            """operation is atomic; I-O threading arrived in version six.""")
seg(sid, 4, """Eviction is approximated: Redis samples a handful of keys &mdash; five by default &mdash; and """
            """evicts the best candidate among them. There is no global recency list, and the quality is """
            """close to true L-R-U. Expiry is lazy on access plus a periodic random sample of keys with """
            """T-T-Ls. Persistence, if you want it, is snapshots or an append-only log.""")
seg(sid, 5, """And the insight to land: exact L-R-U across a huge keyspace costs pointer updates and locking """
            """on every read. Redis trades exactness for a sample, and that is the trade you should offer """
            """too, once you are past one node.""")

tradeoff('Exact eviction or approximate', [
 ('Exact LRU, global list per node, one lock', 'info',
  ['Precisely correct eviction order', 'Simple to reason about'],
  ['<b>Every read writes</b> (move to head) under a lock', 'Lock contention caps throughput']),
 ('Segmented exact LRU (lock striping)', 'ok',
  ['Exact within a segment', 'Scales with cores', 'Policy stays pluggable per segment'],
  ['Eviction is per segment &mdash; slightly unfair globally']),
 ('Sampled approximate LRU/LFU (Redis)', 'shared',
  ['<b>No per-read bookkeeping</b> beyond a timestamp', 'Huge keyspaces, minimal memory'],
  ['Not exact', 'Harder to explain in an LLD interview']),
], 'For the LLD half, segmented exact LRU behind the policy interface. For the distributed half, say a '
   'production node would use sampled eviction like Redis.',
 'If the interviewer asked for strict, testable eviction order &mdash; say, a cache of licences where '
 'evicting the wrong one is a correctness bug &mdash; exact LRU with a single lock is the honest choice.',
 [
 """Trade-off: exact or approximate eviction. Exact L-R-U with one global list and one lock is precisely """
 """correct and simple, but every read becomes a write under a lock, and contention caps throughput.""",
 """Segmented exact L-R-U is exact within a segment, scales with cores, and keeps the policy pluggable &mdash; """
 """at the cost of slightly unfair eviction across segments.""",
 """Sampled approximation, as in Redis, has no per-read bookkeeping beyond a timestamp and handles huge """
 """keyspaces &mdash; but it is not exact.""",
 """For the low-level half I would build segmented exact L-R-U behind the policy interface, and for the """
 """distributed half say that a production node would use sampled eviction.""",
 """And if strict eviction order were a correctness requirement, I would take exact L-R-U with a single lock """
 """and accept the throughput.""",
])

failures('What happens when each piece dies', [
 ('A node dies', 'Its keys miss; load hits the database',
  'Consistent hashing limits the shift to that node&rsquo;s keys. <b>Protect the DB</b>: request '
  'coalescing and a rate limit on misses'),
 ('Cache stampede on a hot key expiry', 'Thousands of loaders at once',
  '<b>Single-flight</b> per key (one loader, others wait) and <b>jittered TTLs</b>'),
 ('Clients disagree on membership', 'Same key read from two nodes',
  'Versioned ring from a config service; clients reject stale versions'),
 ('Memory exhausted by large values', 'Eviction thrash',
  'Account in <b>bytes</b>; reject values over a size cap'),
 ('Primary fails before replicating', 'Recent writes lost',
  'Acceptable for a cache; <b>never</b> use it as the only copy'),
], [
 """Failures. A node dies and its keys miss, shifting load to the database. Consistent hashing limits the """
 """shift to that node's keys, and you protect the database with request coalescing and a rate limit on """
 """misses.""",
 """A stampede when a hot key expires sends thousands of loaders at once. Use single-flight per key &mdash; one """
 """loader, everyone else waits on its result &mdash; and jitter the T-T-Ls so keys do not expire together.""",
 """Clients disagreeing on membership read the same key from two nodes. Version the ring from a config """
 """service and have clients reject stale versions.""",
 """Large values exhausting memory cause eviction thrash, so account in bytes and cap value size.""",
 """And a primary failing before replication loses recent writes, which is fine for a cache as long as it is """
 """never the only copy.""",
])

say('What I should actually say in the room', [
 'I will do this in two halves and keep the first one short: the single-node design, then distribution.',
 'The cache owns storage; an eviction-policy interface owns order &mdash; on-access, on-insert, on-remove, '
 'victim. New policies are new classes, nothing else changes.',
 'LRU is a dictionary plus a doubly linked list; LFU is a dictionary plus frequency buckets and a min '
 'frequency, with aging. Both O(1). Capacity is in bytes, so I evict until it fits.',
 'For concurrency I stripe it into segments, each with its own lock and policy instance.',
 'Distributed: consistent hashing with virtual nodes, async replicas, hot keys replicated or near-cached, '
 'and single-flight loading to stop stampedes.',
 'Redis is the reference: single-threaded execution, 16,384 hash slots, and sampled approximate eviction '
 'instead of a global list.',
], [
 """The sentences. Announce the two halves first, which tells the interviewer you are managing the clock.""",
 """Then the interface, the two structures, and segments &mdash; four sentences for the whole low-level half.""",
 """Then distribution and Redis, which is where the staff-level time should go.""",
])

followups([
 'Flexible in-memory cache with customisable capacity and eviction policy',
 'Extend it to a distributed HLD',
 'Redis internals',
], [
 'Write the LRU in C# &mdash; then make it thread-safe.',
 'How would you add a size-aware policy without changing the cache class?',
 'How do you invalidate when the database changes?',
 'Why is Redis single-threaded, and when is that a problem?',
 'How do you warm a new node without hammering the database?',
],
 """The reported prompts are the three stages: the flexible cache, the distributed version, and Redis """
 """internals. All three are answered above.""",
 """The likely drills. The C# LRU is in the coding course &mdash; practise making it thread-safe with lock """
 """striping, not a global lock. A size-aware policy is a new class that weighs size and recency in its """
 """victim choice; the cache stays untouched, which is the point of the interface. Invalidation on database """
 """change is change data capture driving deletes &mdash; delete, do not update, to avoid racing writes. """
 """Redis being single-threaded is a problem only for slow commands, like scanning a huge key, which block """
 """everyone. And warming a new node means copying its slots from the old owner rather than letting misses """
 """refill it from the database.""")

cheatsheet('Pluggable cache — the one-page card', [
 ('Requirements', 'get / put with capacity; pluggable eviction; then distributed'),
 ('Scale', '~2 TB hot data, ~50 nodes, ~2M ops/s; <b>hot keys exceed one node</b>'),
 ('Core architecture', 'Cache + <b>IEvictionPolicy</b> strategy; segments; client-side consistent hashing'),
 ('Data store', 'Dictionary + DLL (LRU); dictionary + frequency buckets (LFU)'),
 ('Partition key', 'Key hash on a ring with virtual nodes (Redis: 16,384 slots)'),
 ('Cache', 'Near-cache in the client for the hottest keys'),
 ('Queue', 'None on the hot path; CDC stream for invalidation'),
 ('Consistency', 'TTL and/or invalidation; async replicas may lose recent writes'),
 ('Failure handling', 'Single-flight loading, jittered TTLs, rate-limit misses to protect the DB'),
 ('Key deep dives', 'O(1) structures and the strategy interface &middot; distribution and Redis internals'),
 ('Biggest trade-off', 'Exact vs sampled eviction &mdash; <b>exactness costs a write on every read</b>'),
], [
 """The card. The core architecture row names the interface, which is the low-level answer in one word.""",
 """The partition key row gives both the textbook ring and the Redis slots.""",
 """And the trade-off line: exact eviction costs a write on every read.""",
])

say('The 60-second answer', [
 'I will keep the single-node design short and spend the time on distribution.',
 'The cache owns storage and delegates order to an eviction-policy interface, so LRU, LFU or a size-aware '
 'policy are separate classes. LRU is a dictionary plus doubly linked list; LFU adds frequency buckets with '
 'aging. Capacity is in bytes, and I stripe the cache into segments for concurrency.',
 'To distribute it: consistent hashing with virtual nodes from a client library, async replicas because '
 'losing cached data is acceptable, and special handling for hot keys &mdash; replication or a near-cache.',
 'To protect the database: single-flight loading, jittered TTLs, and a rate limit on misses.',
 'Redis is the reference design: single-threaded execution with no locks, 16,384 hash slots for '
 'rebalancing, and sampled approximate eviction rather than a global LRU list &mdash; exactness costs a '
 'write on every read, and at scale it is not worth it.',
], [
 """The sixty-second answer. The first sentence is about time management, and saying it out loud is itself """
 """a staff signal.""",
 """And the last sentence shows you understand why the industry's reference design makes the trade it does.""",
], kicker='60-second interview answer')
