# -*- coding: utf-8 -*-
"""Questions 1-9 of the InterviewDB LinkedIn set.

`idb` is the statement as supplied, preserved. Everything else is my explanation, and the
`dd` block says what corroborates the question and what does not.
"""

QUESTIONS = []

# ============================================================ Q1
QUESTIONS.append(dict(
    id='q1', n=1, name='LRU cache with TTL',
    tags=['DESIGN', 'DATA STRUCTURE DESIGN', 'CACHE', 'HASHING', 'LINKED LIST', 'CONCURRENCY'],
    diff='MEDIUM', prio='HIGH',
    verdict_short='InterviewDB + 2 reports of the LRU/LFU family',
    prio_why=(
        'The cache family is the single best-attested coding topic at LinkedIn in this workspace. '
        'Beyond InterviewDB there is a report of **LRU built with the AI assistant available** in the '
        'CWAI round, a report of an **LFU cache with a GetRank() method and LRU as the tiebreaker**, '
        'and `All O’one Data Structure` on the reader’s own list. Different eviction keys, one '
        'skeleton. Learn the skeleton once and all of them fall out.'),
    idb=(
        'Implement an LRU Cache with TTL expiry.\n\n'
        'It is similar to a standard LRU but each entry has a time-to-live.\n\n'
        'get() should return -1 if the key has expired even if it is still in the cache.'),
    idb_extra=(
        'How would you handle cleanup of expired entries without impacting get() latency?\n\n'
        'Discuss: lazy eviction, background cleanup, trade-offs, complexity, concurrency, memory '
        'implications.'),
    dd=dict(elsewhere=[
        ('idb', 'Supplied with a follow-up already attached, which is unusual and useful: the '
                'follow-up tells you the interviewer’s actual interest is **cleanup strategy**, '
                'not the LRU.'),
        ('reported', '**LRU cache, built with the AI assistant available** — Hello Interview’s '
                     'write-up of LinkedIn’s AI-enabled coding round, Feb 2026. Same structure, '
                     'different round.'),
        ('reported', '**LFU cache with a GetRank() function and LRU as the tiebreaker** — LeetCode '
                     'Discuss, Staff SWE with offer, Jun 2025. Sits between this question and Q13.'),
        ('reported', '**All O’one Data Structure (LeetCode 432)** — on the reader’s own '
                     'list of past LinkedIn questions, which is first-party evidence.'),
        ('lc', '146 LRU Cache is the base. 460 LFU Cache is the same skeleton with a different key. '
               'Neither adds TTL, so the TTL half is genuinely InterviewDB-specific here.'),
    ],
        verdict='**InterviewDB reported, and the family is independently reported three times.** The TTL '
                'variation itself rests on InterviewDB alone; the cache skeleton does not.'),
    ambiguity=(
        'Two things the statement leaves open, and both change code.\n\n'
        '**1. Is the TTL per entry or per cache?** "each entry has a time-to-live" reads as per entry, '
        'so `Put` takes a TTL. If it is one TTL for the whole cache it is a constructor argument, and '
        'the expiry field per node becomes just the insertion time.\n\n'
        '**2. Does an expired entry still occupy capacity?** "even if it is still in the cache" says '
        'yes — expiry is logical, not physical. That single sentence is what forces lazy expiry and '
        'is why the follow-up about cleanup exists at all.'),
    understand=dict(
        what='A cache that forgets things for two different reasons at once. It forgets the '
             'least-recently-used entry because it is full, and it forgets any entry whose clock has '
             'run out. Those are independent, and that is the whole difficulty: capacity is about '
             'ordering, expiry is about time, and the two do not agree on who should go first.',
        compute='Three operations. `Get(key)` returns the value, or -1 if the key is absent **or** '
                'expired. `Put(key, value, ttl)` inserts or updates, renewing the expiry. And under '
                'the covers, eviction picks a victim when the cache is full.',
        constraints=[
            'Both operations should be **O(1)**. That rules out scanning for an expired entry on the '
            'hot path.',
            'An expired entry is still physically present until something removes it, so `Count` and '
            'capacity are counted in entries, not in *live* entries.',
            'The clock has to be injectable, or the behaviour is untestable. Passing `Func<long>` in '
            'the constructor costs nothing and is the difference between a design you can test and one '
            'you can only hope about.',
            'Time is monotonic. If it is not — an NTP step backwards — entries can appear to '
            'un-expire. Use a monotonic source, not wall-clock.',
        ],
        assume=[
            ['TTL is supplied per entry, on `Put`.',
             'If it is one cache-wide TTL, the constructor takes it and the node stores an insertion '
             'time instead. Two lines different; ask rather than guess.'],
            ['A re-`Put` of an existing key **renews** the TTL.',
             'If it must not, an update has to preserve the original expiry, and a hot key can then '
             'expire mid-use — which is sometimes exactly what you want for a session cache.'],
            ['Expiry is inclusive: an entry with `expiresAt == now` is dead.',
             'One character in the comparison. Whichever you pick, say it, because a test will sit '
             'exactly on that boundary.'],
            ['Single-threaded unless told otherwise.',
             'Under concurrency the doubly linked list is the problem, not the dictionary: two '
             'threads relinking the same neighbours corrupt it silently. See the follow-up.'],
        ]),
    examples=[
        ('Given', 'capacity 2, clock at t=0', 'empty'),
        ('', 'Put(1,100,ttl=10); Put(2,200,ttl=10)', 'both live'),
        ('', 'Get(1) at t=9', '100 — inside its TTL'),
        ('', 'Get(1) at t=10', '-1 — expiry is inclusive, so it is dead exactly on the boundary'),
        ('Mine', 'Put(1,·); Put(2,·); Get(1); Put(3,·)', '2 is evicted, not 1 — the Get made 1 recent'),
        ('Mine', 'Put(7,70,ttl=10) at t=0; Put(7,71,ttl=10) at t=8', 'expires at t=18, not t=10'),
    ],
    examples_note='The statement supplied no worked example, so only the boundary case above follows '
                  'directly from its wording. The two marked *Mine* are cases I would raise, because '
                  'both are places an implementation can be wrong while passing the obvious test.',
    observation=(
        'Start from what has to be O(1) and work backwards — do not start from "use a HashMap".\n\n'
        'Eviction needs to find the least-recently-used entry and remove it in constant time. A '
        'dictionary can find a node instantly but has no idea which one is oldest. An array knows the '
        'order but costs O(n) to move an element to the front. Neither structure can do both, so you '
        'hold both: a **doubly linked list** for the order, and a **dictionary from key to the list '
        'node**. The list gives O(1) reordering *provided you already have the node*, and the dictionary '
        'is what gives you the node. That pairing is the answer to plain LRU.\n\n'
        'Now the TTL. The tempting move is a second ordered structure keyed on expiry, so you can find '
        'the next entry to die. Resist it for a moment and ask what the requirement actually says: `Get` '
        'must return -1 for an expired key. It does **not** say the entry must be gone. So the cheapest '
        'correct implementation is to check the expiry of the one entry you already hold, on the path '
        'where you already hold it — **lazy expiry**. One comparison, no new structure, no '
        'background work.\n\n'
        'That is the key observation, and it generalises: *a deadline you only have to honour when '
        'someone looks does not need a timer.* The expiry heap only becomes necessary when the '
        'requirement changes from "return -1" to "reclaim the memory", which is precisely what the '
        'supplied follow-up asks.'),
    brute=dict(
        how='Keep a `List<(key, value, expiresAt, lastUsed)>`. On `Get`, scan for the key; if found and '
            'live, stamp `lastUsed` with a counter and return it. On `Put` when full, scan for the '
            'smallest `lastUsed` and remove it.',
        cx='`Get` O(n), `Put` O(n), space O(capacity). Every operation is a linear scan.',
        why_not='It is not that O(n) is slow at capacity 100. It is that a cache exists to be faster '
                'than the thing behind it, and an O(n) cache has a cost that grows with its own '
                'hit rate — the bigger you make it to improve the hit rate, the slower each hit '
                'becomes. The design is self-defeating, which is a better answer than "linear is bad".'),
    optimal=dict(pipeline=[
        ('INPUT', '`Get(key)` / `Put(key, value, ttl)`, plus an injectable clock'),
        ('TRANSFORMATION', 'Every entry becomes a list node carrying the key, the value and an '
                           '**absolute** expiry time. Absolute, not remaining — remaining would '
                           'have to be decremented.'),
        ('DATA STRUCTURE', '`Dictionary<int, Node>` for lookup, plus a doubly linked list with head '
                           'and tail sentinels for recency order'),
        ('ALGORITHM', 'Lookup in the dictionary; check expiry; on a live hit move the node to the '
                      'front; on overflow unlink the node before the tail sentinel'),
        ('OUTPUT', 'The value, or -1 for absent or expired'),
    ],
        why=[
            ['`Dictionary<int, Node>`',
             'O(1) key → node. Storing the **node**, not the value, is the whole trick: it is what '
             'lets the list be reordered without searching it.'],
            ['Doubly linked list',
             'O(1) unlink of a node you already hold. Singly linked will not do it — you would '
             'need the predecessor, which costs a scan.'],
            ['Head and tail sentinels',
             'Removes every null check from `Unlink` and `LinkFront`. This is not tidiness; the '
             'null-handling is where hand-written LRU actually breaks under time pressure.'],
            ['An absolute `ExpiresAt` on the node',
             'Comparing two longs is the entire expiry check, and it works no matter how long the entry '
             'has sat there.'],
            ['No expiry-ordered structure, on purpose',
             'Correctness does not need one. Adding it before the requirement demands it is the most '
             'common over-engineering in this question.'],
        ],
        steps=[
            '`Get`: dictionary lookup. Miss → -1.',
            'Compare `_clock() >= node.ExpiresAt`. Dead → unlink, remove from the dictionary, '
            'return -1. Reclaiming it here is free, because you are already holding the node.',
            'Live → move the node to the front and return its value.',
            '`Put`: if the key exists, overwrite the value, reset `ExpiresAt`, move to front, done.',
            'Otherwise, if at capacity, take `_tail.Prev` — the least recently used — unlink '
            'it and drop its key.',
            'Create the node, insert it in the dictionary, link it at the front.',
        ]),
    walk=dict(
        intro='Capacity 2, clock injected. `[a, b]` means a is most recent. Watch the point where '
              '`Get` **removes** something.',
        headers=['Step', 'List (recent first)', 'Dictionary', 'Returns'],
        rows=[
            ['t=0 Put(1,100,10)', '[1]', '1 → node(exp 10)', '—'],
            ['t=0 Put(2,200,10)', '[2, 1]', '1, 2', '—'],
            ['t=1 Get(1)', '[1, 2]', '1, 2', '100 — live, so 1 moves to the front'],
            ['t=1 Put(3,300,10)', '[3, 1]', '1, 3', 'evicted **2**, because Get(1) made 2 the LRU'],
            ['t=10 Get(1)', '[3]', '3', '-1 — expired, and **unlinked on the read path**'],
            ['t=10 Get(3)', '[]', '(empty)', '-1 — also expired; the cache is now empty'],
        ],
        close='Two things to point at. At t=1 the eviction victim was 2, not 1, because a read counts as '
              'use — that is the LRU half working. At t=10 a **read mutated the cache**, which is '
              'the TTL half working: lazy expiry means `Get` is not a pure function, and saying so before '
              'they ask is worth a mark.'),
    code=[
        ('The cache itself', 'Q01_LruTtl.cs', 'LruTtlCache'),
    ],
    codewalk=[
        ('Why the node holds the key as well as the value',
         'When eviction picks `_tail.Prev`, it has a node and needs to delete the matching dictionary '
         'entry — which needs the key. Without `Node.Key` there is no way back from the list to '
         'the dictionary, and this is the single most common omission in a first attempt.'),
        ('The invariant, stated once',
         'The dictionary and the list hold **exactly the same set of entries** at every point between '
         'operations. Every mutation touches both. `Remove` exists precisely so that pairing cannot '
         'drift: there is one function that unlinks and deletes, and nothing else does either alone.'),
        ('Why `Get` is allowed to mutate',
         'On an expired hit it unlinks and removes. That is not a side effect smuggled in; it is the '
         'cheapest possible reclamation, because the node is already in hand. It also means the cache '
         'self-cleans along whatever access pattern it actually has — hot keys get checked often, '
         'cold keys sit until they are evicted by capacity.'),
        ('Why eviction never scans',
         '`EvictOne` could look for an already-expired victim and prefer it, which would be nicer. It '
         'would also be O(capacity), and the stated requirement is O(1). Keeping the eviction strictly '
         'at `_tail.Prev` preserves the bound; the scan belongs in the sweeper, where it is bounded and '
         'off the hot path.'),
        ('The bug the sentinels prevent',
         'Without sentinels, `Unlink` needs four null checks and `LinkFront` needs two, and the case '
         'that breaks is removing the only node — head and tail both have to be updated. With '
         'sentinels, `n.Prev` and `n.Next` are never null, so the four-line version is correct for '
         'every case including the last one.'),
        ('What `Count` deliberately does not tell you',
         'It counts entries, including expired ones not yet reclaimed. A `LiveCount` would have to walk '
         'the whole list. If a metric is needed, count reclamations instead — a counter is O(1), '
         'a census is not.'),
    ],
    cx=dict(rows=[
        ['`Get`', 'O(1)', 'O(1)', 'One dictionary probe, one comparison, two pointer swaps'],
        ['`Put`', 'O(1)', 'O(1)', 'One probe; eviction is `_tail.Prev`, never a search'],
        ['eviction', 'O(1)', 'O(1)', 'The victim is always the node before the tail sentinel'],
        ['`Sweep(budget)`', 'O(k log n)', 'O(n) heap', 'k reclaimed, each a heap pop; the heap holds one '
                                                      'record per `Put`'],
        ['overall space', '—', 'O(capacity)', 'One node and one dictionary entry per held key'],
    ],
        note='**All O(1) here means expected, not worst case**, because the dictionary is a hash table. '
             'The list operations are genuinely worst-case O(1); the hashing is not. It is a small '
             'distinction and a real one, and saying it unprompted reads very differently from being '
             'corrected on it.'),
    edges=[
        ['`capacity <= 0`', 'Throws in the constructor. A zero-capacity cache that silently accepts '
                            '`Put` and always misses is worse than a loud failure.'],
        ['`Get` on a key never inserted', 'Dictionary miss → -1, nothing mutated.'],
        ['TTL of 0', 'Expires immediately, since `expiresAt == now` and the check is `>=`. It still '
                     'occupies a slot until something reclaims it — worth stating.'],
        ['Negative TTL', 'Already expired on arrival. Accepted as written; if the interviewer wants a '
                         'throw, that is one line, but say which you chose.'],
        ['Re-`Put` of an existing key when full', 'No eviction, because the count does not change. '
                                                 'Getting this wrong evicts a live entry for nothing.'],
        ['Every entry expired', '`Get` reclaims them one at a time as they are touched. The cache never '
                                'holds a stale value, but it can hold stale *memory* — exactly the '
                                'gap the follow-up closes.'],
        ['Clock jumps backwards', 'Entries appear to un-expire. Use a monotonic clock '
                                  '(`Environment.TickCount64`, not `DateTime.Now`).'],
        ['Concurrent `Get` on the same key', 'Two threads can both decide an entry is expired and both '
                                             'unlink it, corrupting the list. Needs a lock; see the '
                                             'follow-up.'],
    ],
    fups=[
        dict(given=True,
             q='How would you handle cleanup of expired entries without impacting get() latency?',
             thinking='The question is not "how do I delete expired entries" — lazy expiry already '
                      'makes them unreachable. It is "how do I reclaim their **memory** without putting '
                      'work on the read path". So the constraint is: `Get` must not get slower. That '
                      'immediately rules out any sweep that runs inside `Get`, and points at work that '
                      'happens somewhere else.',
             approach='Keep lazy expiry exactly as it is — it is what guarantees correctness — '
                      'and add a **bounded background sweep** for reclamation. A min-heap keyed on '
                      'expiry time gives the sweeper the next entry to die in O(1) peek, so a sweep that '
                      'finds nothing due costs one comparison. Each sweep takes a budget, so one pass '
                      'can never stall the process.\n\n'
                      'The subtlety is that a re-`Put` renews the TTL, which leaves a stale record in '
                      'the heap pointing at an entry that is no longer due. Removing from a heap by key '
                      'is O(n), so do not: give each entry a **version** and let the sweeper discard any '
                      'record whose version no longer matches. Stale records cost memory until they '
                      'surface, and nothing else.',
             tradeoff='Three options, and the right answer names all three.\n\n'
                      '**Lazy only** — zero background cost, `Get` stays O(1), but memory is held '
                      'by dead entries until they are touched or evicted. Fine when capacity is the '
                      'binding constraint anyway, which for a fixed-size cache it usually is.\n\n'
                      '**Lazy plus a bounded sweep** — memory is reclaimed promptly, `Get` is '
                      'untouched, and the cost is one heap entry per `Put` plus the version field. This '
                      'is the answer I would give.\n\n'
                      '**A timing wheel** — buckets of entries by coarse expiry slot, O(1) insert '
                      'with no heap and no comparisons. Better than the heap when TTLs are few and '
                      'similar (all 30 seconds, say), because then a bucket per second is cheap and '
                      'exact. Worse when TTLs are arbitrary and wide, because you either get poor '
                      'granularity or a huge wheel. Naming *when* it wins is the point; naming it as a '
                      'buzzword is not.',
             code=[('The sweeping variant — note that `Get` is byte-for-byte the same policy',
                    'Q01b_Sweeper.cs', 'SweptLruTtlCache')],
             t='`Put` O(log n) for the heap insert · `Get` O(1) unchanged · `Sweep(k)` O(k log n)',
             s='O(capacity) plus one heap record per `Put`, including stale ones until they surface'),
        dict(q='Make it thread-safe. What exactly are you protecting?',
             thinking='Name the races before naming the lock. There are two, and they are different. '
                      'The dictionary can be made concurrent off the shelf. The **doubly linked list '
                      'cannot** — two threads relinking overlapping neighbours produce a list that '
                      'is still walkable and quietly wrong, which is the worst failure mode there is.',
             approach='A single lock around the whole operation is the correct first answer, and it is '
                      'not a cop-out: the critical section is a handful of pointer writes, so '
                      'contention is short even if it is frequent. `ConcurrentDictionary` alone is '
                      '**not** enough and claiming it is would be the actual mistake.\n\n'
                      'If measurement says the lock is the bottleneck, the standard escape is sharding: '
                      'N independent caches, each with its own lock, keyed by `hash(key) % N`. Recency '
                      'then becomes per-shard rather than global, which is a real semantic change — '
                      'you are no longer evicting the globally least-recently-used entry. Most '
                      'production caches accept that trade; say that you know you are making it.',
             tradeoff='One lock: simple, obviously correct, serialises every operation including reads. '
                      'Sharded locks: near-linear read scaling, approximate LRU. Lock-free: the recency '
                      'list makes it very hard, and the usual production answer is to abandon strict '
                      'LRU for something sampled — which is what Redis actually does, and it is '
                      'worth knowing that the industry chose approximation here.',
             t='O(1) per operation plus lock acquisition', s='Unchanged, plus one lock per shard'),
        dict(q='The cache is distributed across many nodes now. What changes?',
             thinking='Almost everything, and the honest answer leads with which part of the question '
                      'stops being the interesting one. LRU ordering across nodes needs coordination on '
                      'every read, which no one does.',
             approach='Partition by key with consistent hashing, and make each node an independent local '
                      'cache of exactly this design. Recency becomes per-node. TTL, on the other hand, '
                      'travels very well: it is an absolute timestamp, needs no coordination, and every '
                      'node can decide expiry alone — provided clocks are reasonably synchronised, '
                      'which for second-scale TTLs they are.',
             tradeoff='You lose global LRU and gain linear scale. You also gain a new failure mode: on '
                      'a topology change, keys move and a moved key’s TTL must be interpreted '
                      'against the new node’s clock. Absolute expiries survive that; remaining-time '
                      'TTLs do not — which retroactively justifies storing `ExpiresAt` rather than '
                      '`ttl` in the node.',
             t='O(1) local, plus one network hop', s='O(capacity) per node'),
        dict(q='Why not just use MemoryCache, or Redis with EXPIRE?',
             thinking='In production that is very often the right call, and saying so is not weakness. '
                      'The question is being asked to see whether you know what is inside them.',
             approach='`MemoryCache` gives absolute and sliding expiry and a size limit already. Redis '
                      'gives `EXPIRE` plus `maxmemory-policy allkeys-lru`. Either removes the need for '
                      'this code. I would reach for one of them unless I needed behaviour they do not '
                      'offer — a custom eviction key, a specific memory shape, or no dependency.',
             tradeoff='Building it costs a day and owns a bug surface forever. Adopting one costs a '
                      'dependency and gives up control of the eviction policy. What I would not do is '
                      'build it *and* pretend the library does not exist — the interview answer '
                      'and the production answer are allowed to differ, as long as you say which one '
                      'you are giving.',
             t='—', s='—'),
    ],
    testing=dict(skills=[
        '**Data-structure composition** — recognising that no single structure meets the '
        'requirement, and picking the pair that does.',
        '**Reading the requirement precisely** — "return -1 even if it is still in the cache" is '
        'the sentence that decides the whole design, and it is easy to skim past.',
        '**Knowing when not to add a structure** — the expiry heap is the trap, and declining it '
        'until the follow-up demands it is the signal.',
        '**Complexity honesty** — amortised versus worst case, expected versus guaranteed.',
        '**Concurrency instinct** — identifying that the list, not the map, is the unsafe part.',
        '**Testability** — whether the clock is injectable, which separates people who have '
        'written this in production from people who have written it on a whiteboard.',
    ],
        senior='Builds the dictionary plus doubly linked list correctly, adds an expiry check in `Get`, '
               'and gets all the pointer cases right. That is a complete, correct answer to the '
               'question as asked.',
        staff='Does the same, then says what was deliberately left out and why: no expiry heap until '
              'reclamation is required, eviction stays strictly O(1) rather than preferring expired '
              'victims, the clock is injected so the TTL is testable, and `Get` mutates — stated '
              'before anyone asks. On the follow-up, gives three cleanup strategies with the condition '
              'under which each wins, rather than one with enthusiasm.'),
    say=[
        "Let me start with what has to be O(1), because that decides the structures rather than the "
        "other way round.",
        "Eviction has to find the least-recently-used entry instantly. A dictionary can find a key "
        "instantly but has no order; a list has order but finding a node in it is linear. So I will hold "
        "both — a doubly linked list for recency, and a dictionary from key to the list node, not to the "
        "value. That is the part that makes it work.",
        "Now the TTL. The requirement says get returns -1 for an expired key, but it does not say the "
        "entry has to be gone. So I do not need a timer or an expiry-ordered structure. I store an "
        "absolute expiry on the node and check it in get — lazy expiry.",
        "When get finds an expired entry, I unlink it there and then. It is free, because I am already "
        "holding the node. Worth flagging that this means get mutates the cache.",
        "Eviction always takes the node before the tail sentinel. I could scan for an already-expired "
        "victim instead, which would be nicer, but that is O(capacity) and I would lose the bound.",
        "Two things I would ask before writing: is the TTL per entry or per cache, and does a re-put "
        "renew it? Both change the code.",
        "For your follow-up on cleanup — lazy expiry is already correct, so what is left is reclaiming "
        "memory. I would add a min-heap of expiries and a bounded background sweep, with a version on "
        "each entry so a renewed key leaves a stale heap record that the sweeper can just discard. Get "
        "stays exactly as it is.",
        "A timing wheel is the better structure if the TTLs are few and similar. With arbitrary TTLs the "
        "heap is the safer default.",
    ],
    video=dict(title='LinkedIn Coding — LRU Cache with TTL', mins=18,
               objective='Build the cache from the O(1) requirement rather than from the name, then '
                         'show why lazy expiry is correct and what the follow-up is really asking.',
               beats=[('0:00', 'The question, and the one sentence that decides everything'),
                      ('1:40', 'What must be O(1), and why no single structure can do it'),
                      ('4:00', 'Dictionary to node, not to value — the pairing'),
                      ('6:10', 'Sentinels, and the bug they remove'),
                      ('8:00', 'TTL: why lazy expiry is enough'),
                      ('10:00', 'Get mutates — say it before they ask'),
                      ('11:30', 'The C# implementation'),
                      ('14:00', 'Complexity, and expected versus worst case'),
                      ('15:10', 'Follow-up: cleanup without touching get'),
                      ('16:40', 'Heap versus timing wheel, and when each wins'),
                      ('17:40', 'How to say it')]),
))

# ============================================================ Q2
QUESTIONS.append(dict(
    id='q2', n=2, name='Bipartite animal conflicts',
    tags=['GRAPH', 'BFS', 'DFS', 'HASHING'],
    diff='MEDIUM', prio='MEDIUM',
    verdict_short='InterviewDB only; the pattern is attested by 323 and 261',
    prio_why=(
        'The framing appears only in InterviewDB. The **pattern** is better attested: `323 Number of '
        'Connected Components` and `261 Graph Valid Tree` are both on the LinkedIn-tagged list you '
        'supplied, and both are the same "walk every component of an undirected graph" discipline this '
        'needs. Medium rather than high because no second source describes this question.'),
    idb=(
        'Given a hashmap where:\n\n'
        '• Each key represents an animal.\n'
        '• The value is a list of animals that cannot be placed on the same side as the key animal.\n\n'
        'Determine whether all animals can be divided into two groups such that no conflicting animals '
        'are in the same group.\n\n'
        'Example:\n'
        '{1: [2], 3: [1, 2]} → Not valid\n'
        '{1: [2], 2: [1, 3]} → Valid'),
    dd=dict(elsewhere=[
        ('idb', 'Supplied with two worked examples, which is useful — and they are **consistent '
                'with each other**, which is worth checking rather than assuming. See the examples '
                'section.'),
        ('inference', 'Not found in any other source in this workspace. No Glassdoor, Blind, Taro, '
                      'LeetCode Discuss or Exponent entry describes a LinkedIn bipartition question.'),
        ('lc', '886 Possible Bipartition is this question with people and a dislike list, and 785 Is '
               'Graph Bipartite? is the same check given the adjacency list directly. **Neither is in '
               'the supplied number list**, which is itself mildly interesting — the supplied '
               'numbers include two other graph problems but not the two that match this one.'),
    ],
        verdict='**InterviewDB reported. Not independently corroborated.** The algorithm is standard and '
                'cheap to prepare, so the lack of corroboration matters less here than it would for a '
                'long design question.'),
    ambiguity=(
        'The input is a map, and a map is a bad way to express a symmetric relation. The first example '
        'declares `3: [1, 2]` but does **not** declare `1: [3]`. So either conflicts are mutual and '
        'the input is allowed to state each one once, or they are directional and mean something else.\n\n'
        'Both examples are consistent with **mutual**, and "cannot be placed on the same side as" is '
        'symmetric in plain English, so mutual is the reading to take. Say that you are taking it. If '
        'conflicts were genuinely one-way the problem would be different and considerably stranger.'),
    understand=dict(
        what='You are seating animals on two sides, and some pairs must not share a side. The question '
             'is whether any such seating exists at all — not which one, and not how many.',
        compute='A single boolean: does a valid two-way split exist. A natural follow-up asks for the '
                'two groups, which costs nothing extra.',
        constraints=[
            'Two groups exactly. Not "at most two", and not three — three changes the problem '
            'completely, as the follow-up covers.',
            'An animal may appear only as a **value**, never as a key. It still has to be placed, so it '
            'still has to be in the graph.',
            'The conflict graph may have several disconnected components. Each is coloured '
            'independently, and a single BFS from one start node would miss the rest.',
            'The relation is symmetric even though the input may declare it once.',
        ],
        assume=[
            ['Conflicts are mutual.',
             'If they were directional, "cannot be on the same side" would have to mean something '
             'asymmetric, and the problem is no longer bipartiteness. This is the assumption to state '
             'out loud.'],
            ['An animal listed only as a value must still be placed.',
             'If it can be ignored, the answer can change from invalid to valid. Building the adjacency '
             'symmetrically handles it automatically — which is a good reason to build it that way '
             'rather than colour the input map directly.'],
            ['A duplicate conflict (the same pair twice) is harmless.',
             'It produces a parallel edge. Colouring is unaffected. Worth one sentence, not more.'],
            ['An animal conflicting with itself is unsatisfiable.',
             'It cannot avoid its own side. Returning false is the only sensible answer; silently '
             'ignoring it would return a "valid" split that violates the constraint.'],
        ]),
    examples=[
        ('Given', '{1: [2], 3: [1, 2]}', 'Not valid'),
        ('', 'edges 1–2, 3–1, 3–2', 'triangle → an odd cycle → no two-way split'),
        ('Given', '{1: [2], 2: [1, 3]}', 'Valid'),
        ('', 'edges 1–2, 2–3', 'a path → {1, 3} on one side, {2} on the other'),
        ('Mine', '{1: [2], 2: [3], 3: [4], 4: [1]}', 'Valid — a 4-cycle is even'),
        ('Mine', '{1: [2], 10: [11], 11: [12], 12: [10]}', 'Not valid — the bad component is the second one'),
    ],
    examples_note='The two supplied examples are consistent with each other and with the mutual reading, '
                  'which I checked rather than assumed: the first is a triangle only if `3: [1, 2]` '
                  'implies `1: [3]`. The two marked *Mine* are the cases a test targets — even '
                  'cycles are fine, and the failure may be hiding in a component you never visited.',
    observation=(
        'The words "divided into two groups such that no conflicting pair shares a group" are the '
        'definition of a **bipartite graph**, and recognising that is the whole question. Everything '
        'after it is a standard walk.\n\n'
        'The reason it is worth saying rather than just doing: once it is a graph question, the failure '
        'condition becomes something you can state precisely. A two-way split exists if and only if the '
        'graph contains **no odd cycle**. Walk the graph assigning alternating sides; if you ever reach '
        'a node that already has the same side as the one you came from, you have closed a cycle of odd '
        'length, and no assignment can work — not this one, not any.\n\n'
        'That "not any" is the part a case-by-case attempt cannot give you. Trying to place animals '
        'greedily and backtracking would also find the answer, and would leave you unable to say why. '
        'The colouring argument tells you the answer is a property of the graph rather than of your '
        'search order.\n\n'
        'The two places this goes wrong have nothing to do with the algorithm. The input declares each '
        'conflict once, so **build a symmetric adjacency list first**. And the graph may be in several '
        'pieces, so **loop over every uncoloured node**, not just the first.'),
    brute=dict(
        how='Try every assignment. Each animal goes left or right, so enumerate all 2ⁿ combinations '
            'and check each against the conflict list.',
        cx='O(2ⁿ · E) time, O(n) space.',
        why_not='Twenty animals is a million assignments and forty is a trillion. But the better '
                'objection is that it tells you nothing: it answers "is there one" without ever '
                'explaining why not, so no follow-up about three groups or about which pair caused the '
                'failure can be answered from it. Backtracking with propagation is the same algorithm as '
                'the colouring, arrived at without noticing.'),
    optimal=dict(pipeline=[
        ('INPUT', '`Dictionary<int, List<int>>` — animal to the animals it conflicts with'),
        ('TRANSFORMATION', 'Build a **symmetric** adjacency list, adding both directions and creating an '
                           'entry for any animal seen only as a value'),
        ('DATA STRUCTURE', '`Dictionary<int, int>` for the side of each animal, a `Queue<int>` for the '
                           'BFS frontier'),
        ('ALGORITHM', 'For every uncoloured animal, BFS assigning `1 - side[current]`; fail on an edge '
                      'joining two animals already on the same side'),
        ('OUTPUT', '`true` if every component coloured cleanly, otherwise `false`'),
    ],
        why=[
            ['A separate adjacency dictionary',
             'Colouring the input map directly loses the animals that appear only as values, and forces '
             'you to check both directions on every edge. Building it once is cheaper and removes a '
             'whole class of bug.'],
            ['`Dictionary<int, int>` for sides',
             'Serves as both the visited set and the colour. Two structures would have to be kept '
             'consistent; one cannot drift.'],
            ['`Queue` (BFS) rather than recursion',
             'Either works. BFS avoids a stack overflow on a long chain, and the "colour is the opposite '
             'of the node I came from" rule reads more obviously in the iterative form. DFS with an '
             'explicit stack is equally fine — the recursion depth is the only real argument.'],
        ],
        steps=[
            'Walk the input. For each key and each animal in its list, add the edge in **both** '
            'directions, creating either endpoint if it is new.',
            'Reject immediately if any animal conflicts with itself.',
            'For each animal in the adjacency list with no side yet: assign side 0 and push it.',
            'Pop a node. For each neighbour: if uncoloured, give it the opposite side and push it.',
            'If the neighbour already has a side and it **equals** the current node’s side, return '
            'false — an odd cycle.',
            'If every component finishes, return true.',
        ]),
    walk=dict(
        intro='The first supplied example, `{1: [2], 3: [1, 2]}`. Watch the symmetric build create the '
              'edge that the input never stated.',
        headers=['Step', 'Adjacency', 'Sides', 'Note'],
        rows=[
            ['read 1: [2]', '1↔2', '—', 'both directions added from one declaration'],
            ['read 3: [1, 2]', '1↔2, 3↔1, 3↔2', '—', '**1 now lists 3, although the input never said so**'],
            ['start at 1', '', '1 → side 0', 'first component'],
            ['from 1, see 2', '', '2 → side 1', 'opposite side'],
            ['from 1, see 3', '', '3 → side 1', 'opposite side'],
            ['from 2, see 1', '', 'already 0, current is 1', 'different — fine'],
            ['from 2, see 3', '', 'already **1**, current is **1**', '**same side → return false**'],
        ],
        close='The failure is the edge 2–3 closing a triangle. Note that it was found on the *third* '
              'edge, not the first: the greedy assignment was locally fine twice before it was globally '
              'impossible. That is exactly why the answer is a property of the graph and not of the '
              'order you walked it.'),
    code=[
        ('The check', 'Q02_Bipartite.cs', 'AnimalGrouping'),
    ],
    codewalk=[
        ('Why `Touch` exists at all',
         'It creates an empty adjacency entry for an animal, and it is called for both endpoints of '
         'every edge. That one call is what handles the animal appearing only as a value — without '
         'it, animal 2 in `{1: [2]}` would never be a key in `adj`, and the outer loop would never '
         'consider it. A quietly missing node is the hardest bug to see here, because the answer is '
         'still a plausible boolean.'),
        ('The outer loop is the disconnected-components fix',
         '`foreach (int start in adj.Keys)` with `if (side.ContainsKey(start)) continue;`. A single BFS '
         'from one node explores one component. In my second example the invalid triangle is in the '
         'second component, so a single-start solution returns true — confidently wrong.'),
        ('Why `side` is both colour and visited set',
         '`side.TryGetValue` answers "have I seen this" and "which side" in one probe. Keeping a '
         'separate `HashSet<int> visited` alongside a colour map means two structures that must agree, '
         'and the bug when they disagree is a node coloured twice.'),
        ('The comparison that decides everything',
         '`colour == side[cur]` on an already-coloured neighbour. If it differs, the edge is satisfied '
         'and there is nothing to do — note that we do **not** re-enqueue. If it matches, the graph '
         'has an odd cycle. One comparison is the entire failure detection.'),
        ('Self-conflict, handled before the walk',
         '`if (other == pair.Key) return false;` during the build. A self-loop would otherwise be '
         'coloured as "neighbour already has my side" and produce the right answer by accident; handling '
         'it explicitly means the reason is in the code.'),
        ('Why `Split` re-walks instead of sharing state',
         'It is duplication, and deliberate: `CanSplit` is the answer to the question asked, and keeping '
         'it free of output-collection machinery keeps it readable. In production the two would be one '
         'function returning a result object. In an interview I would write `CanSplit` first, get '
         'agreement, and only then extend.'),
    ],
    cx=dict(rows=[
        ['build adjacency', 'O(V + E)', 'O(V + E)', 'Each declared conflict adds two directed entries'],
        ['`CanSplit`', 'O(V + E)', 'O(V)', 'Every node enqueued once, every edge examined twice'],
        ['`Split`', 'O(V + E)', 'O(V)', 'Same walk, plus the output lists'],
    ],
        note='V is the number of **distinct animals**, which is not the number of keys in the input '
             'map — animals appearing only as values count. That distinction is the complexity '
             'version of the same bug the `Touch` call prevents.'),
    edges=[
        ['Empty or null map', 'Returns true. Nothing to place, so a valid split exists trivially.'],
        ['An animal with an empty conflict list', 'Gets its own component of one node, coloured 0. Fine.'],
        ['An animal only ever a value', 'Created by `Touch` and coloured normally.'],
        ['Self-conflict `{1: [1]}`', 'Returns false during the build, before any colouring.'],
        ['The same conflict declared twice', 'A parallel edge. The neighbour is already coloured and on '
                                            'the opposite side, so it is accepted and nothing is '
                                            're-enqueued.'],
        ['Several components, one invalid', 'Caught, because the outer loop reaches every component. '
                                           'This is the case a naive solution fails.'],
        ['An even cycle', 'Valid. Only **odd** cycles are impossible, and stating that distinction is '
                          'the difference between knowing the theorem and remembering a recipe.'],
        ['A long chain of 100,000 animals', 'BFS is iterative, so no stack overflow. Recursive DFS '
                                           'would need a depth limit or an explicit stack.'],
    ],
    fups=[
        dict(q='Return the two groups, not just whether they exist.',
             thinking='The colouring already computed it — the two groups are the two colour '
                      'classes. Nothing new is needed, which is worth saying so it does not look like '
                      'luck.',
             approach='Partition the `side` dictionary by value. Animals with side 0 form one group, side '
                      '1 the other. Note that the assignment is not unique: any component can be '
                      'flipped independently, so with k components there are 2ᵏ valid answers and '
                      'any one of them is correct.',
             tradeoff='No extra cost. The only decision is what to do when no split exists — throw, '
                      'or return the conflicting pair. Returning the pair is more useful, because a '
                      'caller can then explain the failure to a user, and it costs only carrying the '
                      'edge out of the walk.',
             code=[('Returning the groups', 'Q02_Bipartite.cs',
                    'AnimalGrouping|public static (List<int> Left, List<int> Right) Split')],
             t='O(V + E)', s='O(V)'),
        dict(q='What if three groups were allowed?',
             thinking='The instinct is that it is the same problem with three colours. It is not, and '
                      'this is the most valuable thing to know about this question.',
             approach='Two-colouring is decidable in linear time. **Three-colouring is NP-complete.** '
                      'There is no known polynomial algorithm, so the honest answer changes shape: '
                      'backtracking with constraint propagation for small inputs, a heuristic such as '
                      'DSATUR (colour the most-constrained node first) for larger ones, and if this were '
                      'real, a SAT or CP solver rather than hand-rolled search.',
             tradeoff='Exact and exponential, or approximate and fast. What matters in the interview is '
                      'not the algorithm choice — it is recognising that a one-word change to the '
                      'problem statement moved it across the tractability line, and saying so instead of '
                      'confidently generalising the BFS.',
             t='Exponential in the worst case for exact 3-colouring', s='O(V) for the recursion'),
        dict(q='The conflict list arrives as a stream and never fits in memory. Now what?',
             thinking='Colouring needs the graph. A stream does not give you the graph, so either the '
                      'answer becomes incremental or the data has to be partitioned.',
             approach='Union-find with parity is the right tool: keep, for each animal, its '
                      'representative and whether it is the same side as that representative. Merging '
                      'two animals that already share a representative **and** the same parity is the '
                      'odd cycle, detected the instant the edge arrives. Almost constant time per edge, '
                      'and it needs one pass with no adjacency list.',
             tradeoff='Union-find answers "is it still satisfiable" incrementally, which BFS cannot. It '
                      'does not give you the groups as cheaply, and it cannot be undone — there is '
                      'no efficient way to remove an edge. Trade the groups and deletion for O(1) '
                      'streaming updates.',
             t='O(E · α(V)), effectively O(E)', s='O(V)'),
        dict(q='Why BFS rather than DFS? Does it matter?',
             thinking='It does not matter for correctness, and saying "it does not matter, here is what '
                      'does" is a better answer than picking one and defending it.',
             approach='Both visit every node once and both detect the same failure. BFS is iterative by '
                      'construction, so a 100,000-node chain is fine; recursive DFS would overflow the '
                      'stack. DFS has one genuine advantage: the recursion stack **is** the current '
                      'path, so if you want to report the odd cycle itself, DFS hands it to you and BFS '
                      'makes you reconstruct it from parent pointers.',
             tradeoff='BFS for robustness on deep graphs, DFS if the follow-up asks which cycle broke '
                      'it. Choose on that basis rather than by habit.',
             t='O(V + E) either way', s='O(V) for BFS; O(depth) stack for recursive DFS'),
    ],
    testing=dict(skills=[
        '**Problem recognition** — mapping an English constraint onto a named graph property, which '
        'is the single thing being tested here.',
        '**Input hygiene** — noticing that the map is an asymmetric encoding of a symmetric '
        'relation.',
        '**Graph traversal correctness** — all components, not just the first.',
        '**Knowing the boundary of what you know** — two colours is easy, three is NP-complete, '
        'and confidently generalising is the trap.',
        '**Stating the theorem** — bipartite iff no odd cycle, rather than "it works out".',
    ],
        senior='Recognises bipartiteness, writes a correct BFS two-colouring, and handles both '
               'components and the symmetric build.',
        staff='Does that, and additionally raises the asymmetric-input ambiguity as a clarification '
              'before coding, states the odd-cycle characterisation rather than describing the '
              'mechanics, knows that three groups is NP-complete, and offers union-find with parity for '
              'the streaming case. The signal is the ambiguity being raised first — it is the one '
              'part of this question that is genuinely about reading, not about graphs.'),
    say=[
        "Before I code: the input gives me a map, and the first example declares that 3 conflicts with 1 "
        "but never declares that 1 conflicts with 3. I am going to read conflicts as mutual, because "
        "“cannot be on the same side as” is symmetric. Is that right?",
        "Given that, this is asking whether the conflict graph is bipartite — can I two-colour it. And "
        "the precise answer is: yes, if and only if there is no odd cycle.",
        "So first I build a symmetric adjacency list. That matters for a second reason: an animal might "
        "appear only in a value list, and it still has to be placed. Building the adjacency both ways "
        "creates it for free.",
        "Then I walk. Each node gets the opposite side from the node I reached it through. If I reach a "
        "node that already has the same side as where I came from, I have closed an odd cycle and no "
        "assignment works — not just this one.",
        "The outer loop matters. The graph can be in several pieces, and the invalid piece might not be "
        "the first one I touch, so I start a fresh colouring from every animal I have not coloured yet.",
        "Returning the two groups is free if they want it — they are the two colour classes.",
        "One thing worth flagging: if it were three groups instead of two, this approach does not "
        "generalise. Three-colouring is NP-complete. That is a genuinely different problem, not a harder "
        "version of this one.",
    ],
    video=dict(title='LinkedIn Coding — Two Groups, No Conflicts (Bipartite)', mins=14,
               objective='Get from an English constraint to a named graph property, then show that the '
                         'two real traps are in the input and the component loop, not the algorithm.',
               beats=[('0:00', 'The question and the two supplied examples'),
                      ('1:30', 'Checking the examples agree — the asymmetric map'),
                      ('3:20', 'Recognising bipartiteness'),
                      ('5:00', 'Bipartite iff no odd cycle, and why that matters'),
                      ('6:40', 'Trap 1: build the graph symmetrically'),
                      ('8:00', 'Trap 2: disconnected components'),
                      ('9:20', 'The C# implementation'),
                      ('11:00', 'Walking the triangle to the failure'),
                      ('12:00', 'Follow-up: three groups is NP-complete'),
                      ('13:10', 'How to say it')]),
))

# ============================================================ Q3
QUESTIONS.append(dict(
    id='q3', n=3, name='Artificial island',
    tags=['ARRAY', 'SLIDING WINDOW', 'GREEDY'],
    diff='MEDIUM', prio='HIGH',
    verdict_short='InterviewDB + the same algorithm reader-reported as LC 1004',
    prio_why=(
        'The algorithm is **Max Consecutive Ones III**, which is on your own list of past LinkedIn '
        'questions — first-party evidence, the strongest kind in this workspace. `76 Minimum Window '
        'Substring` on the supplied list is the same window discipline with a harder predicate. High '
        'priority, and it also has the best follow-up ladder on the page: three variations that each '
        'change exactly one thing.'),
    idb=(
        'Given a 1D array:\n\n'
        '1 = land\n'
        '0 = ocean\n\n'
        'You have a limited amount of material that can convert ocean cells into land.\n\n'
        'Find the maximum possible island size.\n\n'
        'Follow-ups:\n'
        '1. Circular array\n'
        '2. Obstacles represented by -1\n'
        '3. Variable ocean depth / conversion cost'),
    dd=dict(elsewhere=[
        ('idb', 'Supplied with three follow-ups and a reference to examples. **The examples themselves '
                'did not come through** — see below.'),
        ('reported', '**Max Consecutive Ones III (LeetCode 1004)** is on your own list of past LinkedIn '
                     'questions. Same problem: longest window containing at most k zeros.'),
        ('reported', '**Minimum Window Substring (LeetCode 76)** appears on the supplied number list '
                     'and is independently reported. Same two-pointer window, harder validity test.'),
        ('lc', '**695 Max Area of Island, which IS on the supplied list, is not this problem.** It is '
               '2-D flood fill. The name matches and the algorithm does not.'),
    ],
        verdict='**InterviewDB reported, and the underlying problem is first-party reported by you.** '
                'The three follow-ups are InterviewDB-specific and are the most valuable part.',
        conflict='The supplied text says *"Include the supplied examples"*, but **no examples came '
                 'through with the statement**. I have not invented any and presented them as given: '
                 'every example in the next section is marked as mine. If the original examples matter '
                 '— in particular whether "material" counts cells or a quantity — they are '
                 'worth going back for.'),
    understand=dict(
        what='A row of cells, some land and some ocean. You may convert up to `material` ocean cells '
             'into land. An island is a **contiguous** run of land. How long is the longest run you can '
             'produce.',
        compute='One integer: the length of the best achievable run. Not which cells to convert, though '
                'the window bounds give you that for free.',
        constraints=[
            'The island must be contiguous. That is what makes this a window problem rather than a '
            'counting problem — if gaps were allowed the answer would just be '
            '`ones + material`.',
            'You may use **fewer** than `material` conversions. The best window is not necessarily the '
            'one that spends everything.',
            'Conversion cost is uniform in the base problem: one unit per ocean cell. Follow-up 3 breaks '
            'exactly that.',
            'One pass, O(1) extra space, is achievable and is what the question is looking for.',
        ],
        assume=[
            ['`material` counts cells, each costing 1.',
             'If it is a quantity of earth and cells have depths, that is follow-up 3 already and the '
             'base answer changes. **This is the clarification to ask**, especially since the examples '
             'that would have settled it are missing.'],
            ['Cells are only 0 or 1 in the base problem.',
             '-1 appears in follow-up 2 and is a different beast: it can never become land at any price.'],
            ['`material` may exceed the number of ocean cells.',
             'Then the answer is the whole array. The window logic gives that without a special case, '
             'which is worth pointing out rather than adding an `if`.'],
            ['An empty array returns 0.',
             'Not 1, and not an exception. Cheap to state and the first thing a test checks.'],
        ]),
    examples=[
        ('Mine', 'cells [1,0,0,1,1,0,1], material 1', '4 — convert index 5, giving 3,4,5,6'),
        ('Mine', 'cells [1,1,0,1], material 0', '2 — no conversions, so the longest existing run'),
        ('Mine', 'cells [0,0,0], material 2', '2 — cannot afford all three'),
        ('Mine', 'cells [0,1,0], material 99', '3 — material to spare, answer is the whole array'),
        ('Mine', 'circular [1,0,0,0,1], material 1', '3 — wrapping, index 4,0 plus one conversion'),
        ('Mine', 'obstacles [1,0,1,-1,1,0,1,1], material 1', '4 — the -1 splits the array; best is 4..7'),
    ],
    examples_note='**Every example here is mine.** The statement said examples were supplied and none '
                  'arrived. I verified all six against a brute-force check over every window, and the '
                  'C# is additionally tested against brute force on 3,000 random arrays across all four '
                  'variants — because on my first pass I got two of my own expected answers wrong, '
                  'which is exactly the argument for not hand-computing them.',
    observation=(
        'Rewrite the problem before solving it. "Convert at most k ocean cells to maximise a contiguous '
        'run of land" is the same sentence as **"find the longest subarray containing at most k '
        'zeros"**. The conversion is a red herring: you never need to decide *which* cells to convert, '
        'because inside any window you would obviously convert all of them.\n\n'
        'That reframing is the whole insight, and it is worth doing out loud, because it turns a '
        'planning problem into a counting one.\n\n'
        'Now, why two pointers rather than checking every window. The window is valid while it contains '
        'at most k zeros, and **adding a cell never makes a window valid and removing one never makes it '
        'invalid**. That monotonicity means once the window at `left` has failed for a given `right`, it '
        'has failed for every larger `right` too — so `left` never needs to move backwards. Each '
        'pointer crosses the array once and the whole thing is O(n).\n\n'
        'Say that monotonicity argument explicitly. Plenty of candidates produce the two-pointer code '
        'from memory; the ones who can say why the left pointer is allowed to be forward-only are the '
        'ones who can adapt it when follow-up 2 breaks the assumption.'),
    brute=dict(
        how='For every start and every end, count the zeros in that window; if the count is within '
            'budget, record the length.',
        cx='O(n³) naively, or O(n²) with a running count as the end extends. O(1) space.',
        why_not='At n = 100,000 — a plausible size for a coastline scan — O(n²) is ten '
                'billion operations. But the more useful observation is that the O(n²) version is '
                'already *doing* the sliding window, just restarting it from every left position. '
                'Noticing that the restart is unnecessary is the step to O(n), and framing it that way '
                'makes the optimisation feel derived rather than recalled.'),
    optimal=dict(pipeline=[
        ('INPUT', '`int[] cells` of 0s and 1s, and an integer `material`'),
        ('TRANSFORMATION', '"Convert at most k cells" becomes "tolerate at most k zeros inside the '
                           'window". Nothing is actually converted.'),
        ('DATA STRUCTURE', 'Two indices and one counter. No collection at all.'),
        ('ALGORITHM', 'Extend `right`, counting zeros. While the count exceeds the budget, advance '
                      '`left`, decrementing when it leaves a zero. Record the best length at every step.'),
        ('OUTPUT', 'The largest window length seen'),
    ],
        why=[
            ['Two indices, no collection',
             'The only state the validity test needs is *how many* zeros are in the window, not which. '
             'A queue of zero positions would also work and would be strictly worse — more memory '
             'for no new capability.'],
            ['A single counter',
             'Updated on entry and on exit. This is the piece that generalises: in follow-up 3 it '
             'becomes a cost sum, and in `76 Minimum Window Substring` it becomes a multiset. The shape '
             'of the loop does not change.'],
            ['`while`, not `if`, on the shrink',
             'With uniform costs one step is always enough, so `if` happens to work. With weighted costs '
             'it is not, and a `while` that was correct all along is better than one you have to '
             'remember to change.'],
        ],
        steps=[
            'Set `best = 0`, `ocean = 0`, `left = 0`.',
            'For each `right`: if `cells[right] == 0`, increment `ocean`.',
            'While `ocean > material`: if `cells[left] == 0`, decrement `ocean`; then `left++`.',
            'Set `best = max(best, right - left + 1)`.',
            'Return `best`.',
        ]),
    walk=dict(
        intro='`[1,0,0,1,1,0,1]` with `material = 1`. The interesting moment is `right = 2`, where the '
              'window becomes unaffordable and has to shrink.',
        headers=['right', 'cell', 'ocean count', 'window', 'best'],
        rows=[
            ['0', '1', '0', '[0,0] = 1', '1'],
            ['1', '0', '1', '[0,1] = 1,0', '2'],
            ['2', '0', '2 → **over budget**', 'shrink: left 0→1 (leaves a 1), left 1→2 (leaves a 0, count 1)', '2'],
            ['3', '1', '1', '[2,3] = 0,1', '2'],
            ['4', '1', '1', '[2,4] = 0,1,1', '3'],
            ['5', '0', '2 → **over budget**', 'shrink: left 2→3 (leaves a 0, count 1)', '3'],
            ['6', '1', '1', '[3,6] = 1,1,0,1', '**4**'],
        ],
        close='Note what happened at `right = 2`: the shrink loop ran **twice**, because the first step '
              'removed a land cell and did not help. That is why the shrink is a `while` and not an '
              '`if`. Also note that `best` never decreased — the window shrinking does not lose a '
              'previously recorded answer, which is why one pass suffices.'),
    code=[
        ('The base problem and all three follow-ups', 'Q03_Island.cs', 'ArtificialIsland'),
    ],
    codewalk=[
        ('Why the shrink loop is a `while`',
         'When the window goes over budget, advancing `left` once may remove a **land** cell, which does '
         'not reduce the zero count. The loop has to keep going until the window is affordable again. An '
         '`if` passes the obvious tests and fails on runs of land before a zero.'),
        ('Why `best` is recorded every iteration',
         'Not only when the window grows. After a shrink the window is smaller, and `Math.Max` keeps the '
         'earlier answer. Recording only on growth is a subtle bug that produces the right answer '
         'whenever the best window happens to be last.'),
        ('The circular version: why two copies, and why the cap',
         'Walking `2n` cells lets a window wrap the join. Without `right - left + 1 > n` in the shrink '
         'condition, a window could wrap all the way round and count cells twice — reporting an '
         'island longer than the array. The early return when the whole ring is affordable is there for '
         'the same reason and is not just an optimisation: with `material` covering every ocean cell, '
         'the window would otherwise try to exceed `n`.'),
        ('The obstacle version: why the window resets rather than shrinks',
         'A `-1` cannot be converted at any price, so no valid window may contain one. That is '
         'categorically different from an expensive cell. `left = right + 1; ocean = 0;` cuts the array '
         'in two at that point. Trying to express an obstacle as "infinite cost" and reusing the '
         'weighted version would also work, and is worse — it invites overflow and hides the '
         'structure.'),
        ('The weighted version: why the same two pointers still work',
         'Costs are non-negative, so the window cost is still monotonic in the window bounds: growing '
         'can only increase it, shrinking can only decrease it. That is the **only** property the '
         'forward-only `left` pointer relies on. If any cost could be negative the technique collapses '
         'entirely and it becomes a prefix-sum problem.'),
        ('`long spent`, not `int`',
         'n cells at a per-cell cost can overflow a 32-bit sum on large inputs. `budget` stays an `int` '
         'because it is compared, not accumulated. Cheap, and the kind of thing the Staff Coding module '
         'explicitly says it looks for.'),
    ],
    cx=dict(rows=[
        ['`MaxIsland`', 'O(n)', 'O(1)', 'Each pointer advances at most n times; the shrink is amortised'],
        ['`MaxIslandCircular`', 'O(n)', 'O(1)', 'Two passes over n, still linear; no array copy is made'],
        ['`MaxIslandWithObstacles`', 'O(n)', 'O(1)', 'A reset is O(1); the total work is still one pass'],
        ['`MaxIslandWeighted`', 'O(n)', 'O(1)', 'Same loop with a sum instead of a count'],
    ],
        note='**The shrink loop looks nested but is not O(n²).** `left` only ever increases, so '
             'across the entire run the inner loop executes at most n times in total. That is an '
             'amortised argument and it is the one to state, because the code visually contains a loop '
             'inside a loop and an interviewer may be waiting to see whether you notice.'),
    edges=[
        ['Empty array', 'Returns 0 in all four variants, checked first.'],
        ['`material = 0`', 'Degenerates to "longest existing run of 1s", which the same loop produces '
                           'with no special case.'],
        ['`material >=` the number of ocean cells', 'Returns `n`. Falls out of the loop; the circular '
                                                   'version needs the explicit early return.'],
        ['All ocean, material short', 'Returns exactly `material`.'],
        ['All land', 'Returns `n` with no conversions used.'],
        ['Single cell `[0]` with `material = 0`', 'Returns 0. The window is never valid, so `best` stays '
                                                 'at its initial 0.'],
        ['Circular, whole ring affordable', 'Returns `n`, via the early return — without it the '
                                            'window would wrap past `n`.'],
        ['Obstacle at index 0 or at the end', 'Handled: the reset sets `left` past the array end '
                                             'harmlessly, and the loop terminates normally.'],
        ['All obstacles', 'Returns 0. No window can contain a `-1`, so none is ever valid.'],
        ['Weighted, a cost that overflows `int`', 'Accumulated in a `long`.'],
    ],
    fups=[
        dict(given=True, q='What if the array is circular?',
             thinking='The wrap means the best window might start near the end and finish near the '
                      'start. The usual trick for circular array problems is to walk two concatenated '
                      'copies — but that introduces a new way to be wrong, because a window is now '
                      'allowed to be longer than the array.',
             approach='Iterate `right` from 0 to `2n - 1`, indexing with `% n`. Add one clause to the '
                      'shrink condition: `|| right - left + 1 > n`, so the window can never exceed the '
                      'array length. Then handle the degenerate case first — if every ocean cell is '
                      'affordable the answer is `n`, and returning early avoids the window trying to '
                      'wrap onto itself.',
             tradeoff='Two passes instead of one, still O(n), still O(1) space because no copy is '
                      'materialised — `% n` is doing the concatenation. The alternative, actually '
                      'building a 2n array, is simpler to read and doubles the memory; at this size I '
                      'would take the modulo.',
             code=[('Circular', 'Q03_Island.cs', 'ArtificialIsland|public static int MaxIslandCircular')],
             t='O(n)', s='O(1)'),
        dict(given=True, q='What if some cells are obstacles, represented by -1?',
             thinking='The question to ask is whether an obstacle is expensive or impossible. "Obstacle" '
                      'reads as impossible — it can never be land. That is not a cost change, it is '
                      'a **structural** change, and it breaks the assumption the sliding window rests on.',
             approach='No valid window may contain a `-1`, so the array becomes a set of independent '
                      'segments separated by obstacles. On meeting one, reset: `left = right + 1`, '
                      '`ocean = 0`. Each segment is then the original problem, and the shared `best` '
                      'across all of them is the answer.',
             tradeoff='This is the follow-up that most rewards saying what changed conceptually. '
                      'Modelling `-1` as infinite cost and reusing the weighted version gives the right '
                      'answer and obscures the reason; the reset says "the window cannot cross this" in '
                      'code.',
             code=[('Obstacles', 'Q03_Island.cs', 'ArtificialIsland|public static int MaxIslandWithObstacles')],
             t='O(n)', s='O(1)'),
        dict(given=True, q='What if each ocean cell has its own conversion cost?',
             thinking='The first thing to check is whether the two-pointer argument survives. It rests '
                      'on the window cost being monotonic in the bounds. Costs are non-negative, so it '
                      'does — and that is the entire answer.',
             approach='Replace the zero **count** with a cost **sum**, and compare against the budget '
                      'instead of against k. The loop is otherwise unchanged. Accumulate in a `long`.',
             tradeoff='No cost at all: same time, same space, same shape. Which is the point worth '
                      'making — the generalisation is free precisely because the original solution '
                      'was built on the right invariant. If costs could be **negative** the technique '
                      'would collapse and this would become a prefix-sum problem with a very different '
                      'answer.',
             code=[('Weighted', 'Q03_Island.cs', 'ArtificialIsland|public static int MaxIslandWeighted')],
             t='O(n)', s='O(1)'),
        dict(q='Return which cells to convert, not just the length.',
             thinking='The window already contains the answer; nothing new needs computing.',
             approach='Track `bestLeft` and `bestRight` whenever `best` is updated. The cells to convert '
                      'are the zeros in that range. If several windows tie, any of them is correct — '
                      'say so, and say which one you return (the first, here).',
             tradeoff='Two extra integers. The only real decision is tie-breaking, and stating that ties '
                      'exist is better than silently returning one.',
             t='O(n), plus O(window) to list the cells', s='O(1) for the bounds'),
        dict(q='It is 2-D now — a grid, and you can convert k water cells.',
             thinking='This is where it stops being the same problem, and the honest answer says so '
                      'quickly. **This is also the question that 695 Max Area of Island looks like, '
                      'which is why the name collision is worth knowing about.**',
             approach='Contiguity in 2-D is connectivity, not an interval, so there is no window to '
                      'slide. For k = 1 there is a good O(rc) solution: flood-fill to label every island '
                      'with its size, then for each water cell sum the sizes of its distinct neighbouring '
                      'labels and add one. For general k it is far harder and I would not claim a clean '
                      'algorithm.',
             tradeoff='The k = 1 case is a genuinely nice problem and worth knowing (it is LeetCode 827). '
                      'For general k I would say plainly that I do not have a polynomial approach in '
                      'mind rather than improvise one, and ask whether k = 1 is the intended case.',
             t='O(rc) for k = 1', s='O(rc) for the labels'),
    ],
    testing=dict(skills=[
        '**Reframing** — turning "convert cells" into "tolerate zeros", which is the whole problem.',
        '**Sliding window** — and specifically whether you can justify the forward-only left '
        'pointer rather than just write it.',
        '**Amortised analysis** — recognising the nested loop is still O(n).',
        '**Adaptability** — three follow-ups that each change one thing: the topology, the '
        'feasibility, the cost model. Two of them keep the algorithm; one breaks it.',
        '**Boundary discipline** — the circular cap and the empty array are where this gets '
        'implemented wrongly.',
    ],
        senior='Reframes it as "at most k zeros", writes the clean two-pointer loop, and handles the '
               'three follow-ups correctly when prompted.',
        staff='Does that, and asks whether `material` counts cells or quantity **before** coding — '
              'which pre-empts follow-up 3 entirely. States the monotonicity that licenses the forward '
              'left pointer, states that the nested loop is amortised O(n), and on the obstacle '
              'follow-up says explicitly that this one **breaks** the window assumption while the other '
              'two do not. That distinction is the staff-level signal in this question.'),
    say=[
        "First, let me restate it. I have a row of land and ocean, I can convert up to k ocean cells, and "
        "I want the longest contiguous run of land. Inside any window I would obviously convert every "
        "ocean cell in it, so I never have to decide which ones.",
        "Which means this is: find the longest subarray containing at most k zeros.",
        "One clarification before I write anything — is the material a count of cells, each costing one, "
        "or a quantity where cells have different depths? Those are different problems, and I think your "
        "third follow-up is the second one.",
        "Brute force is every window, O(n²) with a running count. But that version is already doing "
        "a sliding window and just restarting it from each left position, and the restart is what is "
        "unnecessary.",
        "The reason two pointers work: adding a cell never makes the window valid, and removing one never "
        "makes it invalid. So once a window has failed at this left, it fails for every larger right. The "
        "left pointer never goes backwards, and both pointers cross the array once — O(n), O(1) space.",
        "The shrink is a while loop, not an if, because advancing left might remove a land cell and not "
        "help. And I record the best length every iteration, not only when the window grows.",
        "That nested loop is still O(n) overall, because left only ever increases.",
        "For your follow-ups — circular means walking two copies with a modulo, plus one guard so the "
        "window cannot exceed the array length. Variable cost means the counter becomes a sum, and "
        "nothing else changes, because costs are non-negative so the monotonicity still holds.",
        "The obstacle one is different from the other two. A -1 can never be land at any price, so no "
        "valid window may contain one. That breaks the sliding window rather than reweighting it — the "
        "array becomes independent segments, and I reset the window at each obstacle.",
    ],
    video=dict(title='LinkedIn Coding — Artificial Island (Sliding Window)', mins=16,
               objective='Derive the window from the reframing, prove the left pointer is forward-only, '
                         'then use the three follow-ups to show which changes keep the technique and '
                         'which break it.',
               beats=[('0:00', 'The question, and the missing examples'),
                      ('1:20', 'Reframing: convert cells → tolerate zeros'),
                      ('3:00', 'Brute force, and spotting the wasted restart'),
                      ('4:40', 'Why the left pointer never moves back'),
                      ('6:30', 'The loop, and why shrink is a while'),
                      ('8:00', 'Walking the example to the answer'),
                      ('9:30', 'Amortised O(n) despite the nested loop'),
                      ('10:40', 'Follow-up: circular, and the cap that stops double-counting'),
                      ('12:20', 'Follow-up: weighted costs — free, and why'),
                      ('13:50', 'Follow-up: obstacles — this one breaks it'),
                      ('15:10', 'How to say it')]),
))

# ============================================================ Q4
QUESTIONS.append(dict(
    id='q4', n=4, name='Biased random generator',
    tags=['RANDOMIZATION', 'DESIGN'],
    diff='MEDIUM', prio='MEDIUM',
    verdict_short='InterviewDB only; randomisation attested by 528 and 384',
    prio_why=(
        'No other source in this workspace describes this question. Two randomisation problems are on '
        'the supplied LinkedIn-tagged list — `528 Random Pick with Weight` and `384 Shuffle an '
        'Array` — so the topic is attested even though the question is not. Medium, and worth '
        'preparing because it is short and because **528 is its mirror image**: one turns uniform into '
        'biased, the other biased into uniform.'),
    idb=(
        'Input:\n\n'
        'getRandom01Biased()\n\n'
        'Returns 0 with probability p\n'
        'Returns 1 with probability (1-p)\n\n'
        'Output:\n\n'
        'getRandom06Uniform()\n\n'
        'Returns an integer from [0,6] with uniform probability.'),
    dd=dict(elsewhere=[
        ('idb', 'Stated precisely, with no ambiguity about the range: `[0,6]` inclusive, so **seven** '
                'outcomes.'),
        ('inference', 'Not found elsewhere in this workspace. It is a well-known interview problem in '
                      'general (the classic form is "fair coin from a biased coin"), which is why it '
                      'goes in GENERAL rather than REPORTED for anything beyond InterviewDB.'),
        ('lc', '528 Random Pick with Weight is the exact inverse transformation and is on the supplied '
               'list. 384 Shuffle an Array tests the same instinct — a plausible shortcut that is '
               'subtly non-uniform.'),
    ],
        verdict='**InterviewDB reported. Not independently corroborated as a LinkedIn question**, though '
                'the family is well attested and the problem itself is a classic.'),
    ambiguity=(
        'Is `p` known? The signature says only that the generator is biased, not by how much.\n\n'
        'This matters, and the good answer does not need to know. **A solution that works for unknown p '
        'is strictly better than one that uses it**, and Von Neumann debiasing never refers to p at all. '
        'If p were known you could do better on the expected number of calls — arithmetic coding '
        'gets close to the entropy bound — but you would have bought a small constant factor with '
        'a dependency on a value that is usually only approximately known. Say that you are deliberately '
        'not using p.\n\n'
        'One thing does have to be assumed: `0 < p < 1`. If p is 0 or 1 the source has no entropy and no '
        'algorithm can produce a fair bit from it.'),
    understand=dict(
        what='You have one source of randomness and it is unfair. You need seven equally likely '
             'outcomes out of it. Nothing about the source can be changed, and its bias may be unknown.',
        compute='A single integer in 0..6, with each of the seven values having probability exactly 1/7.',
        constraints=[
            '**Exactly** uniform, not approximately. Any scheme that maps an unequal number of source '
            'outcomes onto the seven values is wrong, however small the error looks.',
            'The number of calls to the source is not fixed. Any exact method must be able to give up '
            'and retry.',
            'Seven is not a power of two, which is the second difficulty and is independent of the bias.',
        ],
        assume=[
            ['Successive calls are independent.',
             'The whole construction relies on it. If the source were correlated — say it alternated '
             '— pairing two draws would produce a **deterministic** result, not a fair bit. Worth '
             'saying, because it is the one assumption that cannot be worked around.'],
            ['p is fixed across calls.',
             'If the bias drifts, the pairing argument still holds **within** a pair but the expected '
             'cost changes over time. Correctness survives; performance predictions do not.'],
            ['`0 < p < 1`.',
             'At the extremes the source is a constant and the task is impossible. Stating it is a '
             'one-line acknowledgement that you know where the method’s domain ends.'],
            ['Unbounded worst-case time is acceptable.',
             'If it is not, no exact method exists. You would have to accept a tiny bias with a call cap, '
             'which is a legitimate engineering trade and should be named as one.'],
        ]),
    examples=[
        ('Pairing', 'draws 0,1', 'accept → return 0'),
        ('', 'draws 1,0', 'accept → return 1'),
        ('', 'draws 0,0 or 1,1', 'reject → draw another pair'),
        ('Assembly', 'three fair bits → 101', 'value 5, in range → return 5'),
        ('', 'three fair bits → 111', 'value 7, out of range → discard all three and redraw'),
        ('Cost', 'p = 0.5', '≈13.7 biased calls per output, measured'),
        ('', 'p = 0.05', '≈72 biased calls per output, measured'),
    ],
    examples_note='The two cost figures are measured, not derived on paper: the test harness draws '
                  '700,000 values at each of four different p and checks both the uniformity '
                  '(chi-square over 6 degrees of freedom) and the observed call count against the '
                  'predicted `24 / (7p(1-p))`. They agree to within 5%.',
    observation=(
        'There are two separate problems here and conflating them is what makes this question hard. '
        '**Solve them one at a time.**\n\n'
        '*Problem one: remove the bias.* Call the source twice. The outcome `01` has probability '
        '`p(1-p)`. The outcome `10` has probability `(1-p)p`. Multiplication commutes, so **those two '
        'are exactly equal whatever p is**. The other two outcomes, `00` and `11`, are the ones carrying '
        'the bias — so throw them away and draw again. Return the first bit of any pair that '
        'disagrees, and you have a perfectly fair bit from a source whose bias you never measured. That '
        'is Von Neumann’s trick, and the whole of it is the observation that `p(1-p) = (1-p)p`.\n\n'
        '*Problem two: get seven outcomes from fair bits.* Three fair bits give eight equally likely '
        'values, 0 through 7. You want seven. Eight does not divide by seven, so **no mapping of the '
        'eight onto the seven can be uniform** — some value would have to receive two of the eight, '
        'making it twice as likely. The only correct move is to **reject**: if the three bits give 7, '
        'discard them and draw three more. This is rejection sampling, and the temptation it defeats is '
        '`value % 7`, which is wrong and looks fine.\n\n'
        'Both halves are the same idea applied twice: *when the outcomes you have do not divide evenly '
        'into the outcomes you want, discard rather than squeeze.* Neither half needs to know p, and '
        'neither has a bounded worst case — both facts are worth stating rather than hoping nobody '
        'asks.'),
    brute=dict(
        how='Call the source three times, treat the bits as a binary number, take it modulo 7.',
        cx='O(1) calls, O(1) space, and **wrong**.',
        why_not='Two independent errors, and being able to name both is the point of the question. '
                'First, the bits are biased, so the eight patterns are not equally likely to begin '
                'with — `000` has probability p³ and `111` has `(1-p)³`. Second, even '
                'with perfectly fair bits, `% 7` maps both 0 and 7 onto 0, so 0 would come out twice as '
                'often as everything else. The second error survives fixing the first, which is why the '
                'modulo shortcut is worth explicitly rejecting out loud.'),
    optimal=dict(pipeline=[
        ('INPUT', '`Func<int> biasedBit` returning 0 with probability p, 1 with probability 1−p'),
        ('TRANSFORMATION', 'Pairs of draws → a fair bit, by keeping only the two outcomes that are '
                           'equally likely by symmetry'),
        ('DATA STRUCTURE', 'None. Two local integers.'),
        ('ALGORITHM', 'Debias to a fair bit; take three fair bits as a value in 0..7; reject 7 and '
                      'redraw'),
        ('OUTPUT', 'A uniform integer in 0..6'),
    ],
        why=[
            ['No data structure at all',
             'Worth saying, because "reach for a structure" is the reflex this question punishes. The '
             'entire solution is two loops and a shift.'],
            ['Pairs, not triples or longer runs',
             'Pairs are the smallest window in which two distinct outcomes have provably equal '
             'probability. Longer windows admit more accepted patterns and are more efficient — '
             'that is the advanced-extraction follow-up — but pairs are the ones you can prove on a '
             'whiteboard in one line.'],
            ['Three fair bits, not a loop up to 7',
             'Three bits is the smallest power of two above seven, so it wastes the least. Two bits '
             'cannot reach 6 at all.'],
            ['Rejection, not modulo or scaling',
             'The only exactly uniform option. Everything else trades a bounded call count for a bias, '
             'and the bias is the thing the question is about.'],
        ],
        steps=[
            '`FairBit()`: draw two bits. If they differ, return the first. If they match, repeat.',
            '`Next0To6()`: build `v = (b₂ << 2) | (b₁ << 1) | b₀` from three fair bits.',
            'If `v <= 6`, return it. Otherwise discard all three bits and start again.',
        ]),
    walk=dict(
        intro='One call to `Next0To6()` with an unlucky run, showing both rejection loops firing. '
              'Suppose the raw draws arrive in this order.',
        headers=['Draws', 'What happens', 'Fair bits so far', 'Running value'],
        rows=[
            ['0, 0', 'pair matches → **reject**, draw again', '—', '—'],
            ['1, 1', 'pair matches → **reject** again', '—', '—'],
            ['1, 0', 'differ → fair bit **1**', '1', 'v = 1'],
            ['0, 1', 'differ → fair bit **0**', '1, 0', 'v = 2'],
            ['1, 0', 'differ → fair bit **1**', '1, 0, 1', 'v = 5'],
            ['—', 'v = 5, which is ≤ 6', '', '**return 5**'],
            ['(alt)', 'had the bits been 1,1,1 → v = 7', '', '**discard all three**, start over'],
        ],
        close='Ten raw draws produced one output, and that was not unusual: at p = 0.5 the expected cost '
              'is about 13.7. Note that the second rejection throws away **three** fair bits, not '
              'one — they cannot be partially reused without introducing correlation, which is a '
              'subtle point worth knowing and not worth improvising.'),
    code=[
        ('The generator', 'Q04_Random.cs', 'UniformFromBiased'),
    ],
    codewalk=[
        ('`if (a != b) return a;` — why returning the first bit is correct',
         'The two accepted patterns are `01` and `10`, with equal probability. Returning the first bit '
         'returns 0 for one and 1 for the other, so each comes out half the time. Returning the '
         '**second** bit would be equally correct, inverted. What would not be correct is returning `a` '
         'on a match, which is where the bias lives.'),
        ('Why the outer loop discards all three bits',
         'On rejecting 7 the code loops and calls `FairBit()` three fresh times. Reusing two of the '
         'three — say keeping the top bits and redrawing the last — would correlate successive '
         'outputs, because the surviving bits are conditioned on having been part of a rejected triple. '
         'The conditioning is easy to miss and it is a real bug.'),
        ('Why `BiasedCalls` is instrumented',
         'It makes the expected cost measurable rather than asserted. The test compares the observed '
         'ratio against `24 / (7p(1-p))` at four values of p. In an interview I would not write the '
         'counter, but I would state the formula — and having actually measured it is why I am '
         'willing to state it.'),
        ('The clock on the wall: termination',
         'Both loops terminate with probability 1 and neither has a worst-case bound. For any '
         '`0 < p < 1` the accept probability per pair is `2p(1-p) > 0`, so the number of attempts is '
         'geometric with finite mean. "Terminates almost surely" is the honest phrase; "O(1)" is not.'),
    ],
    cx=dict(rows=[
        ['`FairBit`', 'expected 1/(p(1−p)) draws', 'O(1)',
         'Each pair accepts with probability 2p(1−p); expected pairs is the reciprocal'],
        ['`Next0To6`', 'expected 24/(7p(1−p)) draws', 'O(1)',
         '3 fair bits × 8/7 for the rejection × 2 draws per pair'],
        ['worst case', 'unbounded', 'O(1)', 'Rejection sampling has no upper bound on attempts'],
    ],
        note='**At p = 0.5 that formula gives 13.7 biased calls per output, and the measured value is '
             '13.7.** At p = 0.05 it predicts 72 and measures 72. The cost blows up as p approaches 0 '
             'or 1, because `p(1-p)` is the accept rate and it goes to zero — which is the honest '
             'answer to "how slow can this get".'),
    edges=[
        ['p = 0 or p = 1', 'The source is constant, every pair matches, and `FairBit` never returns. No '
                           'algorithm can extract entropy that is not there — the right response is '
                           'to state the precondition, not to add a retry limit that silently returns a '
                           'wrong answer.'],
        ['p very close to 0 or 1', 'Correct but slow: cost scales as 1/(p(1−p)). At p = 0.001 that '
                                   'is roughly 3,400 draws per output.'],
        ['Correlated source', 'Breaks correctness, not just speed. An alternating source makes every '
                              'pair differ, so `FairBit` becomes deterministic. This is the assumption '
                              'to state.'],
        ['A range that **is** a power of two, say [0,7]', 'The outer rejection disappears entirely and '
                                                         'the cost drops by 8/7. Worth mentioning as the '
                                                         'reason seven is awkward.'],
        ['Needing many values at once', 'Generate them independently. Batching does not help the fair-bit '
                                        'extraction, but advanced extractors do — see the follow-up.'],
    ],
    fups=[
        dict(q='Generalise it to [0, n-1] for any n.',
             thinking='The same two-step shape, with the number of bits chosen per n. The only trap is '
                      'the case where n is already a power of two.',
             approach='Take `b = ceil(log2(n))` fair bits, giving a value in `0 .. 2^b - 1`. Reject '
                      'anything `>= n` and redraw all b bits. Accept probability is `n / 2^b`, which is '
                      'always greater than 1/2, so the expected number of retries is under 2 regardless '
                      'of n.',
             tradeoff='Simple and exact. The efficiency varies with how close n is to a power of two: '
                      'n = 9 needs 4 bits and wastes 7 of 16 patterns, so it retries nearly half the '
                      'time. A batched scheme that generates several values from one larger draw '
                      'recovers most of that waste, at the cost of state between calls.',
             t='Expected `2^b / n` rounds, each of b fair bits; under 2 rounds in the worst case',
             s='O(1)'),
        dict(q='Von Neumann throws away most of its input. Can you do better?',
             thinking='Yes, substantially, and knowing that there is a known-better answer matters more '
                      'than being able to implement it under time pressure. Von Neumann discards both '
                      'matching pairs entirely, and those discards still carry information — the '
                      '*sequence* of which pairs matched is itself random.',
             approach='Advanced extractors (Peres, or Elias’s method) recurse on the discarded '
                      'information: the sequence of "was this pair a match" and "was the match 00 or 11" '
                      'are two further biased sources to extract from. Peres’s iterated construction '
                      'approaches the Shannon entropy bound, so at p = 0.5 you approach one fair bit per '
                      'input bit rather than one per four.',
             tradeoff='Von Neumann is four lines and provably fair. Peres is recursive, needs buffering, '
                      'and is much harder to convince a reviewer of. I would ship Von Neumann unless the '
                      'source were genuinely expensive — a hardware entropy source, say — and '
                      'then I would use a library, not my own implementation. The interview answer is to '
                      'name the direction and the trade, not to write it.',
             t='Approaches the entropy bound, ~1 fair bit per input bit at p = 0.5',
             s='O(1) amortised with buffering'),
        dict(q='p is known. Does that change your answer?',
             thinking='It permits a better answer and does not require one. The interesting part is '
                      'whether you can say why you would still not use it.',
             approach='With p known you can do arithmetic coding on the source and approach the entropy '
                      'bound directly, which is a large constant-factor win at extreme p. You could also '
                      'pick pairing windows to maximise the accept rate.',
             tradeoff='p is almost never known **exactly** — it is measured, and it drifts. A method '
                      'whose *correctness* depends on p is fragile in a way that a method whose only '
                      '*speed* depends on p is not. Von Neumann is exactly uniform for every p in (0,1), '
                      'including p values you measured wrongly. I would keep it unless profiling proved '
                      'the source was the bottleneck.',
             t='Approaches the entropy bound', s='O(1)'),
        dict(q='Now the reverse: given a uniform generator, produce outcomes with given weights.',
             thinking='This is LeetCode 528 and it is on your supplied list, which makes the pair worth '
                      'preparing together — the interviewer who asks one may well ask the other.',
             approach='Build the prefix sums of the weights once, draw a uniform value in `[0, total)`, '
                      'and binary-search for the first prefix sum strictly greater than it. O(n) to '
                      'build, O(log n) per draw. The alias method gets O(1) per draw with O(n) '
                      'preprocessing if draws vastly outnumber builds.',
             tradeoff='Prefix sums plus binary search is the answer to give: simple, and the '
                      'preprocessing/query split is the same argument as Q11 and Q13. Mention the alias '
                      'method as the O(1) option rather than implementing it.',
             t='O(n) build, O(log n) per draw', s='O(n)'),
    ],
    testing=dict(skills=[
        '**Probability reasoning** — specifically, spotting that `p(1-p) = (1-p)p` is the whole '
        'answer to the first half.',
        '**Knowing that "approximately uniform" is a wrong answer** — and being able to say why '
        '`% 7` is biased even with fair bits.',
        '**Decomposition** — two separate problems, solved separately. Candidates who attack it as '
        'one problem tend not to finish.',
        '**Honesty about termination** — no worst-case bound, terminates with probability 1.',
        '**Not over-engineering** — the correct answer uses no data structure and does not use p.',
    ],
        senior='Gets Von Neumann debiasing, gets three bits with rejection of 7, and can state the '
               'expected cost.',
        staff='Does that, and additionally: rejects the `% 7` shortcut out loud with the reason, notes '
              'that the solution deliberately does **not** use p and why that is a feature, states the '
              'independence assumption as the one thing that cannot be worked around, is precise that '
              'the worst case is unbounded rather than calling it O(1), and knows that better extractors '
              'exist without pretending to implement one. The single strongest signal is the '
              'independence assumption — almost nobody states it, and it is the assumption the '
              'whole construction rests on.'),
    say=[
        "There are two problems in here, and I want to solve them separately rather than together.",
        "First: turn a biased bit into a fair one. I call the source twice. The outcome 0 then 1 has "
        "probability p times (1-p). The outcome 1 then 0 has (1-p) times p. Those are the same number "
        "whatever p is. So if the two draws differ, I return the first one, and if they match I throw the "
        "pair away and draw again.",
        "That gives me a provably fair bit, and notice I never needed to know p. I think that is a "
        "feature — a solution that depends on p would be fragile, because p is usually measured rather "
        "than known.",
        "Second: seven outcomes from fair bits. Three fair bits give me eight equally likely values. I "
        "want seven, and eight does not divide by seven, so there is no way to map eight onto seven "
        "without making one of them twice as likely. So I reject: if the three bits give me 7, I throw "
        "all three away and draw again.",
        "I want to explicitly rule out taking the value modulo 7, because it is the tempting answer and "
        "it is wrong twice — the bits are biased to begin with, and even with fair bits 0 and 7 both map "
        "to 0.",
        "On cost: at p = 0.5 this is about fourteen calls to the source per output. In general it is "
        "24 over 7p(1-p), so it degrades as p approaches 0 or 1.",
        "And I should be precise about termination. This has no worst-case bound. It terminates with "
        "probability 1, not within any fixed number of draws. If a bounded number of calls were a hard "
        "requirement, no exact method exists and we would have to accept a small bias deliberately.",
        "One assumption I am relying on throughout: successive calls are independent. If the source were "
        "correlated — alternating, say — every pair would differ and my fair bit would be deterministic.",
    ],
    video=dict(title='LinkedIn Coding — Fair Randomness from a Biased Coin', mins=15,
               objective='Separate the two sub-problems, prove each in one line, and show why the '
                         'obvious shortcut is wrong twice over.',
               beats=[('0:00', 'The question, and why it is really two questions'),
                      ('1:30', 'The wrong answer: modulo 7, and its two independent bugs'),
                      ('3:10', 'p(1-p) = (1-p)p — the whole first half'),
                      ('5:00', 'Von Neumann in four lines'),
                      ('6:20', 'Seven from eight: why rejection is the only exact option'),
                      ('8:00', 'The C# implementation'),
                      ('9:30', 'Expected cost, derived and then measured'),
                      ('11:00', 'Unbounded worst case — saying it properly'),
                      ('12:10', 'The independence assumption almost nobody states'),
                      ('13:20', 'The mirror problem: LeetCode 528'),
                      ('14:20', 'How to say it')]),
))

# ============================================================ Q5
QUESTIONS.append(dict(
    id='q5', n=5, name='LinkedIn connection distance',
    tags=['GRAPH', 'BFS', 'HASHING', 'DESIGN'],
    diff='MEDIUM', prio='HIGH',
    verdict_short='InterviewDB + your own list (first-party)',
    prio_why=(
        '**On your own list of past LinkedIn questions** — "minimum degree of connection between '
        'two users, follow-up: return the path" — which is first-party evidence and the strongest '
        'in this workspace. It is also the most LinkedIn-shaped question on the page: degrees of '
        'connection is a product feature, so the follow-ups can go from the algorithm straight into '
        'how it would actually be served.'),
    idb=(
        'LinkedIn has users connected to other users.\n\n'
        'Given:\n\n'
        'interface Member {\n'
        '    int getMemberId();\n'
        '    List<Member> getConnections();\n'
        '}\n\n'
        'Find the shortest connection distance between two members.\n\n'
        'Example:\n\n'
        'Bob -> Alice -> Frank\n\n'
        'Distance(Bob, Frank) = 2'),
    idb_extra='What if one member has a very large connection size while the other has a small '
              'connection size?',
    dd=dict(elsewhere=[
        ('idb', 'Supplied with the interface **and** a worked example that pins down the units: Bob to '
                'Frank through Alice is 2, so distance counts **edges**, not people. That single example '
                'removes the off-by-one risk, which is the main thing that goes wrong here.'),
        ('reported', '**"Minimum degree of connection between two users; follow-up: return the path"** '
                     '— your own list of past LinkedIn questions. Already worked in this workspace '
                     'as a bidirectional BFS problem.'),
        ('reported', '`490 The Maze` and celebrity/BFS rounds appear in the Taro and Blind reports, so '
                     'graph traversal in general is well attested.'),
        ('lc', '160 Intersection of Two Linked Lists is on the supplied list and shares the '
               '"two traversals meeting, equalise the cheaper side" instinct.'),
    ],
        verdict='**InterviewDB reported and independently first-party reported by you.** The highest '
                'confidence on the page, alongside Q17.'),
    understand=dict(
        what='The social graph, reachable only through an interface: given a member you can ask for its '
             'id and its connections. There is no adjacency matrix, no id-to-member map, no global view. '
             'You discover the graph by walking it.',
        compute='The number of hops on the shortest path between two members, or a sentinel if they are '
                'in different components. The supplied example fixes hops, not people: 2 for '
                'Bob→Alice→Frank.',
        constraints=[
            'Connections are **unweighted**, so BFS is optimal and Dijkstra would be pointless overhead. '
            'Say that — reaching for Dijkstra here is a recognisable tell.',
            'The graph is undirected in practice (a connection is mutual on LinkedIn) but the interface '
            'does not promise it. The algorithm works either way; only the bidirectional version cares.',
            'Visited must be tracked by **id**, not by object reference. Nothing guarantees that the same '
            'member arrives as the same instance twice, and `Equals` is not specified on the interface.',
            'The graph is enormous. The follow-up about lopsided connection counts is really about this.',
        ],
        assume=[
            ['Ids are unique and stable.',
             'They are the identity for the visited set. If two distinct members could share an id the '
             'search would silently prune real paths.'],
            ['`GetConnections()` may return null or contain nulls.',
             'A real interface like this usually does eventually. Guarding costs two lines and turns a '
             'crash into a correct answer.'],
            ['Distance counts edges. Self is 0, a direct connection is 1.',
             'Pinned by the supplied example. If they wanted people counted it is +1 everywhere — '
             'confirm which, because "degree of connection" in the LinkedIn product means edges.'],
            ['`GetConnections()` is cheap and local.',
             'It is not, in reality — it is a service call. That assumption is exactly what the '
             'distributed follow-up removes, and naming it early sets that up.'],
        ]),
    examples=[
        ('Given', 'Bob – Alice – Frank', 'Distance(Bob, Frank) = 2'),
        ('Mine', 'Bob – Alice', '1 — a direct connection'),
        ('Mine', 'Distance(Bob, Bob)', '0 — the same member'),
        ('Mine', 'Bob and Zoe, no path', '-1 — different components'),
        ('Mine', 'a hub with 5,000 connections, and a member with 1', '2, found by expanding the small side first'),
    ],
    examples_note='The first is supplied and is the one that matters, because it fixes the units. The '
                  'rest are mine. The lopsided case is in the test suite specifically because it is the '
                  'supplied follow-up, and the two implementations are additionally cross-checked '
                  'against each other on 120 random pairs — a bidirectional BFS that disagrees with '
                  'plain BFS is the single most common way to get this wrong.',
    observation=(
        'The first observation is that there is nothing to invent: shortest path on an unweighted graph '
        'is BFS, and BFS is optimal here. Saying that quickly and moving on is the right use of the '
        'first thirty seconds.\n\n'
        'The second observation is the one the question is actually built around, and it is in the '
        'follow-up. **The cost of a BFS round is the size of the frontier you expand, and if you search '
        'from both ends you get to choose which frontier that is.** A single BFS to depth `d` touches '
        'roughly `b^d` nodes, where b is the branching factor. Two searches meeting in the middle touch '
        'about `2 · b^(d/2)`. At LinkedIn’s average connection count that is not a constant '
        'factor — at b = 500 and d = 4 it is 62 billion versus half a million.\n\n'
        'Now the lopsided part. If one member has 30,000 connections and the other has 40, expanding the '
        'hub first costs 30,000 node visits to advance one level; expanding the small side costs 40. '
        'They meet at the same place either way. So the rule is: **each round, expand whichever frontier '
        'is currently smaller.** Not "start from the smaller one" — re-decide every round, because '
        'the small side may become the large one after it touches a hub.\n\n'
        'That is the answer to the supplied follow-up, and it is one `if` plus a swap.'),
    brute=dict(
        how='Depth-first search from the source, recording the length of every path that reaches the '
            'target, then take the minimum.',
        cx='Exponential in the worst case. Even with a visited set, DFS finds *a* path and it is not '
            'necessarily the shortest, so pruning by visited is unsound.',
        why_not='This is the mistake worth naming explicitly, because it is a correctness error and not '
                'a performance one. DFS with a visited set returns the first path it stumbles onto, '
                'which can be arbitrarily longer than the shortest. To make DFS correct you must allow '
                'revisiting nodes at shorter depths, and then you are exploring exponentially many '
                'paths. BFS avoids both problems at once: it visits by increasing distance, so the first '
                'time it reaches a node is the shortest way to reach it, which is what licenses the '
                'visited set.'),
    optimal=dict(pipeline=[
        ('INPUT', 'Two `IMember` references. No global view of the graph.'),
        ('TRANSFORMATION', 'Nothing is precomputed. Neighbours come from `GetConnections()` on demand.'),
        ('DATA STRUCTURE', '`Queue<IMember>` for the frontier and `HashSet<int>` for visited ids. For '
                           'the bidirectional version, two frontiers as `Dictionary<int, IMember>` and '
                           'two visited sets.'),
        ('ALGORITHM', 'Level-by-level BFS, incrementing depth once per level. Bidirectional: expand the '
                      'smaller frontier each round and stop when a node is in the other side’s '
                      'visited set.'),
        ('OUTPUT', 'Hops, or -1 if unreachable'),
    ],
        why=[
            ['`HashSet<int>` keyed by id',
             'O(1) membership, and keyed on the only identity the interface guarantees. Using the member '
             'object would depend on `Equals` and `GetHashCode` that the interface never promises.'],
            ['Level-by-level, not a queue of `(node, depth)` pairs',
             'Both are correct. Levelling is less state and makes the "distance is edges" convention '
             'visible in the code — `depth++` happens exactly once per level, so there is one place '
             'to check the off-by-one.'],
            ['`Dictionary<int, IMember>` for the bidirectional frontiers',
             'A frontier must be countable (to decide which side to expand) and membership-testable (to '
             'detect the meeting). A dictionary does both; a queue does neither.'],
            ['Two separate visited sets',
             'The meeting test is "is this id in the **other** side’s visited set". One shared set '
             'would make the two searches prune each other and report the wrong distance.'],
        ],
        steps=[
            'Handle the trivial cases: either null → -1; same id → 0.',
            'Seed the frontier with the source and mark its id visited.',
            'Take the whole current level. Increment `depth`.',
            'For each node in the level, for each connection: if it is the target, return `depth`.',
            'Otherwise, if the id is new, mark it and add it to the next level.',
            'Repeat until the queue empties, then return -1.',
            '**Bidirectional:** maintain two frontiers; each round swap so `frontA` is the smaller, '
            'expand it, and return `depth` as soon as a discovered id is in `seenB`.',
        ]),
    walk=dict(
        intro='Bidirectional search between `tiny` and `hub`, where `hub` has 5,000 connections and '
              '`tiny` has 1. The point is which side does the work.',
        headers=['Round', 'Frontier A (tiny)', 'Frontier B (hub)', 'Expanded', 'Result'],
        rows=[
            ['seed', '{tiny}', '{hub}', '—', 'sizes 1 and 1'],
            ['1', '{tiny}', '{hub}', '**A**, size 1 — one node visited', 'reaches a mid member; not in seenB yet'],
            ['1 (cont)', '{mid}', '{hub}', '', 'depth = 1'],
            ['2', '{mid} size 1', '{hub} size 1', '**A** again, still smaller', 'mid’s connections include hub'],
            ['2 (cont)', '', '', 'hub **is** in seenB', '**return 2**'],
            ['(compare)', '', '', 'plain BFS from hub first', 'would visit all 5,000 to advance one level'],
        ],
        close='Two node expansions instead of five thousand, and the same answer. Note that the choice '
              'was re-made in round 2 rather than fixed at the start — with a deeper path, A would '
              'eventually grow past B and the algorithm would start expanding B instead. That is the '
              'behaviour the follow-up is asking for.'),
    code=[
        ('The interface, as given, in C#', 'Q05_Distance.cs', 'IMember'),
        ('Plain BFS and the bidirectional version', 'Q05_Distance.cs', 'ConnectionDistance'),
    ],
    codewalk=[
        ('`int levelSize = queue.Count;` before the inner loop',
         'Captured **before** the loop, because the loop enqueues into the same queue. Reading '
         '`queue.Count` inside the condition would consume the next level in the same round and return a '
         'distance that is too small. This is the classic level-BFS bug and it produces a plausible '
         'wrong number rather than a crash.'),
        ('Why the target check is on discovery, not on dequeue',
         'Checking `next == to` as soon as the edge is seen returns `depth` one round earlier than '
         'waiting to dequeue it. Both are correct if the bookkeeping matches; checking on discovery '
         'means `depth` has already been incremented for this level, which is exactly the number of '
         'edges traversed. Checking on dequeue with the same `depth++` placement would be off by one.'),
        ('The tuple swap in the bidirectional version',
         '`(frontA, frontB) = (frontB, frontA);` together with the visited sets. Swapping the frontiers '
         'without swapping the visited sets would test membership against the wrong side and silently '
         'return nonsense — the two lines must move together, which is why they are adjacent.'),
        ('Why `depth++` is right despite the swapping',
         'Each round advances exactly one edge, whichever side was expanded. The depth is the total '
         'number of edges laid down by both searches combined, and the meeting point is the last edge. '
         'This is the part I would not trust on inspection, which is why the test suite cross-checks '
         'both implementations on 120 random pairs.'),
        ('`seen.Add(id)` as the test',
         '`HashSet.Add` returns false if the element was present, so the membership test and the '
         'insertion are one operation. Two calls would be correct and would give a second place for the '
         'two to disagree.'),
        ('Nulls, twice',
         '`cur.GetConnections() ?? new List<IMember>()` and `if (nb == null) continue;`. The interface '
         'promises neither, and a graph served from a real backend will eventually hand you both.'),
    ],
    cx=dict(rows=[
        ['`Distance` (BFS)', 'O(V + E) worst case, O(b^d) typical', 'O(V)',
         'Every node enqueued once, every edge examined once'],
        ['`DistanceBidirectional`', 'O(b^(d/2)) typical', 'O(b^(d/2))',
         'Two shallow searches instead of one deep one'],
        ['lopsided case', 'O(small^d) rather than O(large^d)', 'same',
         'Expanding the smaller frontier each round'],
    ],
        note='**The bidirectional win is not a constant factor.** With branching factor b and distance '
             'd, one search touches b^d and two touch 2b^(d/2). At b = 500, d = 4: about 62 billion '
             'against about 500,000. That is the number to have ready, because "it is about twice as '
             'fast" is the wrong intuition and a common one. The space also drops, which matters more '
             'here than the time — a single BFS frontier at depth 3 in a social graph does not fit '
             'in memory.'),
    edges=[
        ['Either member null', 'Returns -1 rather than throwing. Debatable; state which you chose.'],
        ['Same member', '0, handled before the search starts.'],
        ['Direct connection', '1. Worth testing explicitly — it is the off-by-one case.'],
        ['No path', '-1 in both implementations. The bidirectional version must exit when **either** '
                    'frontier empties, not both.'],
        ['A cycle', 'Handled by the visited set. Without it, BFS on a social graph does not terminate.'],
        ['`GetConnections()` returns null', 'Treated as empty.'],
        ['A self-connection', 'The id is already in `seen`, so it is skipped.'],
        ['One member with 30,000 connections', 'The supplied follow-up. Bidirectional expands the other '
                                              'side and never enumerates the hub.'],
        ['Both members are hubs', 'Bidirectional still helps, because the *depth* halves even when '
                                  'neither side is small.'],
    ],
    fups=[
        dict(given=True,
             q='What if one member has a very large connection size while the other has a small '
               'connection size?',
             thinking='The cost of a round is the size of the frontier being expanded. With two '
                      'searches, that is a choice. So the answer is not "start from the small one" '
                      '— it is "re-choose every round", because a small frontier that touches a hub '
                      'becomes the large one.',
             approach='Bidirectional BFS, expanding whichever frontier is currently smaller each round. '
                      'Keep two visited sets and stop when a newly discovered id appears in the other '
                      'side’s set. One `if` and a swap on top of plain BFS.',
             tradeoff='Two frontiers and two visited sets instead of one, and the code is genuinely '
                      'harder to get right — the depth accounting and the swap are both easy to '
                      'break, and the failure is a wrong number rather than a crash. In exchange you go '
                      'from b^d to b^(d/2), which is the difference between fitting in memory and not. '
                      'It also requires the graph to be traversable **backwards**; on LinkedIn '
                      'connections are mutual so that is free, but on a directed graph like follows you '
                      'would need a reverse index.',
             code=[('Bidirectional', 'Q05_Distance.cs',
                    'ConnectionDistance|public static int DistanceBidirectional')],
             t='O(b^(d/2)) typical', s='O(b^(d/2))'),
        dict(given=True, q='Return the path, not just the distance.',
             thinking='Also on your own list, so worth having ready. BFS already knows the path — it '
                      'just is not recording it.',
             approach='Keep a `Dictionary<int, IMember> parent` alongside the visited set and walk it '
                      'back from the target. For the bidirectional version you need two parent maps and '
                      'must join them at the meeting node, reversing one side — and that is the '
                      'part that gets fumbled, because the meeting node belongs to both.',
             tradeoff='O(V) extra memory for the parent map, which in a social graph is the same order as '
                      'the visited set you already have, so it is nearly free. Storing the full path per '
                      'frontier node instead of a parent pointer is the tempting version and multiplies '
                      'memory by the path length.',
             t='O(b^(d/2)) plus O(d) to reconstruct', s='O(V) for the parent maps'),
        dict(q='Cap it at 3 degrees, which is what the product actually shows.',
             thinking='A cap changes the complexity class of the answer, and it is what makes the real '
                      'feature possible. Worth raising unprompted.',
             approach='Stop expanding past depth 3 and return "3+" or "out of network". With '
                      'bidirectional search each side only ever goes to depth 2, which bounds the work '
                      'hard regardless of hubs.',
             tradeoff='This is the one that turns an intractable graph query into a serveable one. It is '
                      'also a product decision disguised as an optimisation — LinkedIn shows 1st, '
                      '2nd, 3rd and "out of network" precisely because the fourth degree is both '
                      'unhelpful to a user and unaffordable to compute. Saying that connection out loud '
                      'is a strong signal.',
             t='O(b^1.5) with the cap and bidirectional search', s='bounded by the depth-2 frontier'),
        dict(q='The graph does not fit on one machine. How is this actually served?',
             thinking='The interface hid a service call behind `GetConnections()`, and the moment that '
                      'is remote, per-node traversal is the wrong shape entirely — the cost is '
                      'round trips, not comparisons.',
             approach='Two things. Batch the frontier: one request per **level**, asking for the '
                      'connections of every node in the frontier at once, rather than one request per '
                      'node. That turns d round trips out of b^d. And partition the graph by member id '
                      'with the adjacency list co-located, so a level expansion is a scatter-gather '
                      'across partitions.\n\n'
                      'For first-degree and second-degree, precompute. Second-degree sets are large but '
                      'bounded and change slowly, so a bloom filter or a compressed set per member '
                      'answers "are we within 2" without any traversal at all — which is what makes '
                      'the badge on a profile page instant.',
             tradeoff='Batching is a pure win and is the first thing to do. Precomputation trades storage '
                      'and staleness for latency: a bloom filter gives false positives, so "2nd degree" '
                      'might occasionally be wrong in the optimistic direction, which for a badge is an '
                      'acceptable error and for an access-control decision would not be.',
             t='O(d) round trips instead of O(b^d)', s='O(frontier) per request'),
        dict(q='Why not Dijkstra, or A*?',
             thinking='Being able to say why not is better than listing algorithms you know.',
             approach='Dijkstra solves weighted shortest path. All edges here have weight 1, and on a '
                      'unit-weight graph Dijkstra degenerates into BFS with a priority queue bolted on '
                      '— same answer, worse constant, `O(log V)` per operation for nothing. A* needs '
                      'an admissible heuristic estimating distance-to-target, and in a social graph there '
                      'is no coordinate to estimate from.',
             tradeoff='If connections were weighted — interaction strength, say — Dijkstra '
                      'becomes correct and BFS becomes wrong. That is the condition to state, rather '
                      'than dismissing Dijkstra outright.',
             t='O((V + E) log V) for Dijkstra, worse than BFS here', s='O(V)'),
    ],
    testing=dict(skills=[
        '**Recognising unweighted shortest path** — and saying BFS and why, quickly.',
        '**Knowing why DFS is wrong here**, as a correctness issue and not a speed one.',
        '**Bidirectional search** — the supplied follow-up, including re-choosing the side each '
        'round rather than once.',
        '**Interface discipline** — visited by id, nulls guarded, no assumptions the interface does '
        'not make.',
        '**Systems awareness** — `GetConnections()` is a service call, so batching per level is the '
        'real optimisation.',
        '**Product sense** — the 3-degree cap is why the feature is possible at all.',
    ],
        senior='Writes a correct level-by-level BFS with a visited set keyed by id, gets the off-by-one '
               'right, and produces bidirectional BFS when prompted.',
        staff='Does that, then: states that a round costs the size of the frontier and therefore '
              're-chooses which side to expand every round; gives the b^d versus 2b^(d/2) numbers rather '
              'than saying "faster"; notes that bidirectional needs the graph to be traversable '
              'backwards and that connections being mutual is what makes it free; raises the 3-degree '
              'cap unprompted as the reason the real feature is serveable; and points out that the '
              'interface is hiding a network call, so batching per level matters more than any of the '
              'algorithmic work.'),
    say=[
        "Unweighted shortest path, so BFS. Dijkstra would give the same answer with a priority queue I do "
        "not need.",
        "Worth saying why not DFS, because it is a correctness problem rather than a speed one. DFS with a "
        "visited set returns the first path it finds, which can be much longer than the shortest. BFS "
        "visits in order of increasing distance, so the first time it reaches a node is the shortest way "
        "to reach it, and that is what makes the visited set sound.",
        "I will track visited by member id, not by object, because the interface does not promise Equals "
        "or that the same member arrives as the same instance.",
        "From your example, Bob to Frank through Alice is 2, so distance is edges, not people. I will "
        "confirm that: self is 0, a direct connection is 1.",
        "Now your follow-up about lopsided connection counts — that is the interesting part. The cost of "
        "one BFS round is the size of the frontier I expand. If I search from both ends, I get to choose "
        "which frontier that is. So each round I expand whichever side is currently smaller.",
        "Note: each round, not once at the start. A small frontier that touches a hub becomes the large "
        "one, and then I should switch.",
        "The win is not a constant factor. One search touches b to the d, two touch 2 times b to the d "
        "over 2. At 500 connections and distance 4 that is 62 billion against half a million.",
        "One caveat: bidirectional needs to walk the graph backwards. On LinkedIn connections are mutual "
        "so that is free. On something directed like follows, I would need a reverse index.",
        "If I can raise one thing unprompted — the real product only shows up to 3 degrees, and that cap "
        "is what makes this serveable at all. And GetConnections is really a service call, so batching "
        "one request per level rather than per node matters more than any of the algorithmic work here.",
    ],
    video=dict(title='LinkedIn Coding — Degrees of Connection', mins=17,
               objective='Get to BFS fast, then spend the lesson on the follow-up: why the cost of a '
                         'round is the frontier you expand, and what that implies at LinkedIn scale.',
               beats=[('0:00', 'The question, the interface and the units'),
                      ('1:30', 'Why BFS, and why DFS is wrong rather than slow'),
                      ('3:20', 'Visited by id, not by object'),
                      ('4:40', 'The level-BFS off-by-one'),
                      ('6:20', 'The follow-up: lopsided connection counts'),
                      ('8:00', 'Bidirectional BFS, and expanding the smaller side each round'),
                      ('10:10', 'b^d versus 2·b^(d/2), with real numbers'),
                      ('11:40', 'The C# implementation'),
                      ('13:30', 'Returning the path, and joining at the meeting node'),
                      ('14:50', 'The 3-degree cap, and why the product has one'),
                      ('16:00', 'GetConnections is a network call'),
                      ('16:50', 'How to say it')]),
))

# ============================================================ Q6
QUESTIONS.append(dict(
    id='q6', n=6, name='Matched parentheses',
    tags=['STRING', 'STACK'],
    diff='EASY', prio='HIGH',
    verdict_short='InterviewDB + your own list + a 2025 report of this exact variant',
    prio_why=(
        'High priority for its **cost-to-benefit ratio**, not its difficulty. `20 Valid Parentheses` is '
        'on your own list from LinkedIn’s six-month tag, and a 2025 report describes a variant '
        '"with integers and special characters" — which is precisely the mixed-content framing '
        'InterviewDB gives here, from a second source. It takes fifteen minutes to make airtight and it '
        'is very likely to appear as a warm-up.'),
    idb=(
        'Given a string containing alphanumeric characters and parentheses, determine whether the '
        'parentheses are correctly matched.\n\n'
        'Examples:\n\n'
        '()()()() → true\n\n'
        '((45+)*a3) → true'),
    dd=dict(elsewhere=[
        ('idb', 'Two examples supplied, and **the second one contradicts the first sentence** — see '
                'below. That is the most interesting thing in this question.'),
        ('reported', '**Valid Parentheses** is on your own list, tagged by LinkedIn in the six-month '
                     'window.'),
        ('reported', 'A 2025 report describes a Valid Parentheses variant **with integers and special '
                     'characters** rather than brackets alone. That is an independent description of '
                     'this same mixed-content framing.'),
        ('lc', '20 Valid Parentheses is the multi-bracket version. **This question is easier than '
               'LeetCode 20**, because it has only one bracket type — which changes the right '
               'answer, and most candidates do not notice.'),
    ],
        verdict='**InterviewDB reported, independently reported twice, and first-party on your own '
                'list.** The best-attested question on the page. Also the easiest, which is exactly why '
                'it is worth being flawless on.'),
    ambiguity=(
        'The first sentence says the string contains "alphanumeric characters and parentheses". The '
        'second example is `((45+)*a3)`, which contains `+` and `*` — **neither of which is '
        'alphanumeric**.\n\n'
        'So either the description is loose and it means "parentheses plus other stuff", or the examples '
        'are illustrative of a wider input. The safe implementation treats **every** non-parenthesis '
        'character as irrelevant, which satisfies both readings. Say that you noticed and that you chose '
        'the permissive reading; the alternative — validating the character set and rejecting '
        '`+` — would fail the supplied example.'),
    understand=dict(
        what='Scan a string and decide whether its round brackets nest correctly. Everything that is not '
             'a bracket is noise.',
        compute='One boolean. Not the position of the error, not the depth — though both are '
                'natural follow-ups and nearly free.',
        constraints=[
            '**One bracket type only.** That is the constraint that changes the answer, and it is easy '
            'to miss because the problem looks like LeetCode 20.',
            'Two failure modes, and they are different: a `)` arriving with nothing open, and the string '
            'ending with something still open.',
            'Non-bracket characters never affect validity.',
            'A single pass, and with one bracket type, O(1) space.',
        ],
        assume=[
            ['Only `(` and `)` are brackets; `[` and `{` are ordinary characters.',
             'If square and curly brackets must also match, the counter is **wrong** — `([)]` has '
             'balanced counts and is invalid. That needs the stack. This is the clarification worth '
             'asking.'],
            ['Every non-bracket character is ignorable, including `+` and `*`.',
             'Forced by the second supplied example. Validating the character set instead would reject '
             'it.'],
            ['An empty string is valid.',
             'Vacuously true. Cheap to state and the first thing a test checks.'],
            ['Null is valid rather than an exception.',
             'Debatable. Whichever you choose, say it — silently dereferencing null is the actual '
             'error.'],
        ]),
    examples=[
        ('Given', '()()()()', 'true'),
        ('Given', '((45+)*a3)', 'true — and it contains + and *, which are not alphanumeric'),
        ('Mine', '', 'true — vacuously'),
        ('Mine', 'abc123', 'true — no brackets at all'),
        ('Mine', ')(', 'false — a close arrives with nothing open'),
        ('Mine', '(()', 'false — ends with one still open'),
        ('Mine', '([)]', 'true under the stated single-type rule — see the note'),
    ],
    examples_note='The last one is the case that decides which implementation is right. With only round '
                  'brackets in scope, `([)]` **is** valid — the round brackets nest correctly and '
                  'the square ones are ordinary characters. If the interviewer expects false, they want '
                  'multiple bracket types and the counter is the wrong answer. That is a thirty-second '
                  'clarification that changes the code.',
    observation=(
        'The reflex answer to any bracket question is "use a stack", and here the more useful observation '
        'is **why you do not need one**.\n\n'
        'A stack exists to remember *what* was opened, so that a closing bracket can be matched against '
        'the right kind. With exactly one bracket type there is nothing to remember: every `(` is '
        'identical to every other `(`, so a `)` can only ever be matched against "the most recent open '
        'one", and all you need to know is **how many** are open. A single integer replaces the stack, '
        'and the space goes from O(n) to O(1).\n\n'
        'Two conditions make it correct, and they are genuinely different. The counter must never go '
        'negative *during* the scan — that catches `)(`, which has a final count of zero and is '
        'invalid. And it must be exactly zero *at the end* — that catches `(()`. Checking only the '
        'final value accepts `)(`; checking only for negatives accepts `(()`. Both are needed, and being '
        'able to name the string each one catches is the whole of this question.\n\n'
        'Then say where it stops working. The moment a second bracket type exists, counting fails, '
        'because `([)]` has balanced counts of both and is still wrong. Order now matters, and the stack '
        'is what records order. Knowing *which constraint* forces the stack is worth more than reaching '
        'for it by default.'),
    brute=dict(
        how='Repeatedly scan the string deleting every adjacent `()` pair, until a pass makes no change. '
            'Valid if the remaining string has no brackets.',
        cx='O(n²) time — each pass is O(n) and there can be n/2 passes on a nested string — '
            'and O(n) space for the rewritten string.',
        why_not='It is correct, which is worth noting, and it is a reasonable first thing to say. It is '
                'quadratic on exactly the input you would use to test it, `((((()))))`. The single-pass '
                'version is not an optimisation of it so much as the observation that the repeated '
                'deletion is only ever tracking a depth, and the depth can be tracked directly.'),
    optimal=dict(pipeline=[
        ('INPUT', 'A string of mixed characters'),
        ('TRANSFORMATION', 'Ignore everything that is not `(` or `)`'),
        ('DATA STRUCTURE', 'One integer. For the multi-type case, a `Stack<char>`.'),
        ('ALGORITHM', 'Increment on `(`, decrement on `)`; fail on a negative count; require zero at '
                      'the end'),
        ('OUTPUT', 'A boolean'),
    ],
        why=[
            ['A single counter, not a stack',
             'With one bracket type the identity of the open bracket carries no information, so only the '
             'count does. O(1) space instead of O(n), and the early-exit check is one comparison.'],
            ['`Stack<char>`, only for the multi-type version',
             'Once there are several types, order matters, and the stack is the structure that records '
             'order. Introducing it before that is over-engineering; knowing exactly when it becomes '
             'necessary is the point.'],
            ['A `Dictionary<char, char>` of closer → opener in the multi-type version',
             'Rather than a switch. It makes adding a bracket type a data change instead of a code '
             'change, which is the kind of thing the Staff Coding module explicitly says it scores '
             'under extensibility.'],
        ],
        steps=[
            'Null or empty → true.',
            'Walk the string. On `(`, increment.',
            'On `)`, decrement; if the count is now negative, return false **immediately**.',
            'Ignore every other character.',
            'At the end, return whether the count is exactly zero.',
        ]),
    walk=dict(
        intro='`((45+)*a3)` — the supplied example with the non-alphanumeric characters in it.',
        headers=['Char', 'Action', 'Open count', 'Note'],
        rows=[
            ['(', 'increment', '1', ''],
            ['(', 'increment', '2', ''],
            ['4 5 +', 'ignored', '2', '`+` is not alphanumeric and is ignored anyway'],
            [')', 'decrement', '1', 'still non-negative'],
            ['*', 'ignored', '1', ''],
            ['a 3', 'ignored', '1', ''],
            [')', 'decrement', '0', ''],
            ['end', 'check', '**0**', '**true**'],
        ],
        close='Compare with `)(`: the first character takes the count to -1 and the scan returns false '
              'there, even though the final count would have been 0. And `(()` ends at 1, which the '
              'final check catches. Two different tests, two different strings — that pairing is '
              'what the question is looking for.'),
    code=[
        ('The counter version — the right answer for one bracket type', 'Q06_Parens.cs', 'ParenCheck'),
    ],
    codewalk=[
        ('Why the negative check is inside the loop',
         'Moving it after the loop would accept `)(`, whose final count is zero. The invariant is "the '
         'count is never negative at any prefix", and an invariant about every prefix has to be checked '
         'at every prefix. Returning early is not an optimisation here; it is the correctness condition.'),
        ('Why the final check is `== 0` and not `<= 0`',
         'The count cannot be negative at the end, because the loop would have returned. So `<= 0` would '
         'be equivalent and misleading — it suggests a case that cannot happen. `== 0` states the '
         'intent: everything opened was closed.'),
        ('The `else if`, and what falls through',
         '`if ( ... ) else if ( ... )` with no final `else`. Every other character does nothing, which '
         'is the permissive reading of "alphanumeric characters and parentheses" and the only reading '
         'that accepts the supplied example.'),
        ('Why `IsBalancedMultiType` is kept alongside it',
         'Not as the answer, but to make the boundary concrete. It differs in one respect that matters: '
         'a closing bracket is checked against the specific opener on top of the stack, so `([)]` fails. '
         'Having both in front of you is the fastest way to answer "what if there were three bracket '
         'types" — and the test suite asserts that the counter says **true** to `([)]` while the '
         'stack says false, so the difference is documented rather than described.'),
        ('`stack.Count == 0` at the end of the multi-type version',
         'Same second failure mode as the counter’s `== 0`. Both versions need two checks; the stack '
         'version just spells the first one as `stack.Count == 0 || stack.Pop() != want`.'),
    ],
    cx=dict(rows=[
        ['`IsBalanced`', 'O(n)', 'O(1)', 'One pass, one integer'],
        ['`IsBalancedMultiType`', 'O(n)', 'O(n)', 'The stack can hold every character on `((((`'],
    ],
        note='**The space difference is the whole point of the question.** O(1) versus O(n) is not a '
             'micro-optimisation here — it follows from a property of the input, and noticing that '
             'property is what is being tested. It also matters for the streaming follow-up: a counter '
             'can validate an arbitrarily long stream in constant memory, and a stack cannot.'),
    edges=[
        ['Empty string', 'true.'],
        ['Null', 'true as written. State the choice.'],
        ['No brackets at all', 'true — the count never moves.'],
        ['`(`', 'false — caught by the final check.'],
        ['`)`', 'false — caught by the negative check on the first character.'],
        ['`)(`', 'false. The case that requires the in-loop check.'],
        ['`(()`', 'false. The case that requires the final check.'],
        ['Deeply nested, 1,000,000 characters', 'Fine. The counter is O(1) space; the stack version would '
                                               'allocate a million entries but still not overflow, since '
                                               'it is iterative.'],
        ['`([)]`', '**true** under the single-type reading. The case to clarify before coding.'],
    ],
    fups=[
        dict(q='Now there are three bracket types.',
             thinking='This is where the counter dies, and being able to state the counterexample '
                      'immediately is the answer. `([)]` has balanced counts of both types and is '
                      'invalid, so counts are not enough — order is now information.',
             approach='A `Stack<char>`. Push openers. On a closer, fail if the stack is empty or if the '
                      'top is not the matching opener. Succeed only if the stack is empty at the end. '
                      'Keep the pairing in a dictionary so a fourth bracket type is a data change.',
             tradeoff='O(n) space instead of O(1), for the ability to enforce ordering. There is no way '
                      'around it: any structure that validates nesting of multiple types must remember '
                      'the sequence of unclosed openers, and in the worst case that is the whole input.',
             code=[('Multiple bracket types', 'Q06_Parens.cs',
                    'ParenCheck|public static bool IsBalancedMultiType')],
             t='O(n)', s='O(n)'),
        dict(q='The input is a stream and does not fit in memory. Can you still validate it?',
             thinking='The question is what state the validator needs to carry, not how the input '
                      'arrives.',
             approach='For one bracket type, yes, trivially: the counter is the entire state, so an '
                      'arbitrarily long stream validates in O(1) memory and you can reject the moment it '
                      'goes negative. For multiple types you need the stack of unclosed openers, which '
                      'in the worst case is the full stream — so the honest answer is that '
                      'single-type streams are O(1) and multi-type streams are not.',
             tradeoff='If bounded memory is a hard requirement with multiple types, you have to bound the '
                      'nesting depth instead and reject beyond it. That is a real protocol design '
                      'decision — it is why JSON parsers ship with a maximum depth — and '
                      'saying so connects the toy question to something real.',
             t='O(n) streaming', s='O(1) single type; O(depth) multi type'),
        dict(q='Return the index of the first unmatched bracket.',
             thinking='Both failure modes need an index, and they come from different places, which is '
                      'the only subtlety.',
             approach='For an unexpected closer the index is the current position. For an unclosed '
                      'opener, the counter cannot tell you **where** it was — so this follow-up '
                      'forces a stack even with one bracket type, holding indices rather than '
                      'characters. Return the top of the stack at the end.',
             tradeoff='This is the cleanest example of a requirement forcing a structure. Nothing about '
                      'validity needed the stack; wanting to *report* the location does. Worth saying '
                      'explicitly — it shows the structure choice was driven by requirements rather '
                      'than habit.',
             t='O(n)', s='O(n) — now unavoidable'),
        dict(q='What about the `*` wildcard version, where `*` can be an opener, a closer or empty?',
             thinking='That is LeetCode 678 and it is a genuinely different problem. Counting still '
                      'works, but a single counter does not.',
             approach='Track a **range** of possible open counts: `lo` and `hi`. A `(` increments both, '
                      'a `)` decrements both, a `*` decrements `lo` and increments `hi`. Clamp `lo` at '
                      'zero, fail if `hi` ever goes negative, and succeed if `lo` reaches zero at the '
                      'end.',
             tradeoff='Still O(n) time and O(1) space, which is surprising and is why the problem is '
                      'liked. The alternative is two-directional greedy or DP, both heavier. I would not '
                      'volunteer this unless asked, but recognising it as the interval-of-counts trick '
                      'rather than a new idea is the useful part.',
             t='O(n)', s='O(1)'),
    ],
    testing=dict(skills=[
        '**Not reaching for the obvious structure** — the question is whether you notice that one '
        'bracket type makes the stack unnecessary.',
        '**Reading the specification against its examples** — `+` and `*` are not alphanumeric.',
        '**Naming both failure modes** and the string that exposes each.',
        '**Knowing the boundary** — exactly which change forces the stack, with the counterexample '
        'ready.',
        '**Warm-up discipline** — this is usually the first fifteen minutes, and fumbling an easy '
        'question costs more signal than solving a hard one gains.',
    ],
        senior='Writes the stack version, correctly, quickly. That is a perfectly good answer and it is '
               'the most common one.',
        staff='Notices one bracket type and uses a counter, says why, and states the counterexample '
              '`([)]` that would force the stack. Raises the `+` and `*` discrepancy between the '
              'description and the example before writing anything. Names both failure modes with the '
              'string each one catches. Then, for the index follow-up, points out that reporting the '
              'location forces a stack even though validity did not — which is the clearest '
              'demonstration on the whole page of a structure chosen from a requirement.'),
    say=[
        "Quick clarification first: your description says alphanumeric characters and parentheses, but the "
        "second example has a plus and a star in it. I will treat anything that is not a round bracket as "
        "ignorable, which satisfies both.",
        "And the more important one — is it only round brackets? Because if square and curly brackets also "
        "have to match, my answer changes.",
        "Assuming just round brackets: I do not need a stack. A stack remembers what kind of thing was "
        "opened, and with one bracket type there is nothing to remember. Every open paren is "
        "interchangeable, so all I need is how many are open. That is one integer instead of O(n) space.",
        "Two checks, and they catch different strings. The count must never go negative during the scan — "
        "that catches close-paren-then-open, which ends at zero and is invalid. And the count must be "
        "exactly zero at the end — that catches open-open-close, which never goes negative.",
        "If I only did the final check I would accept the first one; if I only checked for negatives I "
        "would accept the second.",
        "Where this stops working: the moment there are two bracket types. Square-open, round-open, "
        "round-close, square-close has balanced counts of both and is invalid. Order becomes information, "
        "and the stack is what records order. So the structure is driven by the number of types, not by "
        "the problem being about brackets.",
        "If you wanted the index of the first unmatched bracket, that forces a stack even with one type — "
        "the counter knows something is open but not where it was. Nice example of a requirement, rather "
        "than a habit, choosing the structure.",
    ],
    video=dict(title='LinkedIn Coding — Matched Parentheses, and Why Not a Stack', mins=12,
               objective='Use the easiest question on the page to show the most transferable habit: let '
                         'the constraint pick the structure, and know the counterexample that changes it.',
               beats=[('0:00', 'The question, and the contradiction in its own examples'),
                      ('1:20', 'The clarification that changes the code'),
                      ('2:40', 'Why a stack is not needed with one bracket type'),
                      ('4:20', 'Two failure modes, two different strings'),
                      ('6:00', 'The C# implementation'),
                      ('7:20', 'Walking the supplied example'),
                      ('8:20', 'Where the counter dies: ([)]'),
                      ('9:40', 'Streaming: O(1) for one type, not for many'),
                      ('10:40', 'Reporting the index forces a stack'),
                      ('11:30', 'How to say it')]),
))

# ============================================================ Q7
QUESTIONS.append(dict(
    id='q7', n=7, name='Scheduled executor service',
    tags=['CONCURRENCY', 'DESIGN', 'HEAP', 'QUEUE', 'DATA STRUCTURE DESIGN'],
    diff='HARD', prio='MEDIUM',
    verdict_short='InterviewDB + a first-hand job-scheduler design report',
    prio_why=(
        'Medium on evidence, hardest on the page by content. InterviewDB has it as a coding question; '
        'separately, **"design a job scheduler" is reported first-hand from a Blind Senior SWE '
        'Infrastructure loop**, which is the same problem at design scale. Two concurrency problems from '
        'the supplied list, `1188 Design Bounded Blocking Queue` and `1117 Building H2O`, are the exact '
        'primitives this needs. Medium rather than high only because no second source describes the '
        'coding-round framing.'),
    idb=(
        'Implement the equivalent of:\n\n'
        'public void schedule(\n'
        '    Runnable command,\n'
        '    long delay,\n'
        '    TimeUnit unit)\n\n'
        'The operation schedules a one-shot action that becomes enabled after the specified delay.\n\n'
        'Implement the concept in C#.\n\n'
        'Explain: priority queue, delayed tasks, worker thread, blocking/waiting, condition signaling, '
        'cancellation, shutdown, thread safety, spurious wakeups where relevant.\n\n'
        'This is a concurrency/design question, not simply a syntax translation from Java.'),
    dd=dict(elsewhere=[
        ('idb', 'Supplied with a full list of the aspects to cover, which is effectively the marking '
                'scheme. **Nine things are named**, and only two of them are the data structure. The '
                'other seven are concurrency.'),
        ('reported', '**"Design a job scheduler"** — Blind, LinkedIn Senior SWE Infrastructure, Sep '
                     '2025, first-hand. Same problem, design round rather than coding round, and already '
                     'worked in this workspace.'),
        ('reported', '**A medium string-manipulation question with a concurrency follow-up** — '
                     'reported separately, which tells you concurrency does appear in LinkedIn coding '
                     'rounds rather than only in design.'),
        ('lc', '1188 Design Bounded Blocking Queue is this minus the delays: the same `lock` plus '
               '`Monitor.Wait`/`PulseAll` skeleton. 1117 Building H2O is condition signalling with '
               'nothing else in the way. Both are on the supplied list, which is a reasonable hint that '
               'the primitives get tested.'),
    ],
        verdict='**InterviewDB reported, with the same problem independently reported first-hand at '
                'design scale.** The InterviewDB framing — write the class — rests on one '
                'source; the topic does not.'),
    ambiguity=(
        'Three things the statement leaves open, and the third is the one that catches people.\n\n'
        '**How many worker threads?** One is enough for correctness and is the right first answer, '
        'because it makes the concurrency reviewable. A pool is the follow-up.\n\n'
        '**What does `schedule` return?** Java returns a `ScheduledFuture`, which is how you cancel. The '
        'supplied signature returns `void`, so cancellation — which the aspect list explicitly '
        'asks about — has nowhere to live. I return a handle and say why, because a `void` signature '
        'and a cancellation requirement are incompatible.\n\n'
        '**Should `Task.Delay` count?** In C# the four-line answer is '
        '`await Task.Delay(delay); work();`. It is legitimate production code and it is almost certainly '
        'not what is being asked, given that the statement says "not simply a syntax translation" and '
        'lists spurious wakeups. Say that the library answer exists, say why you are not giving it, then '
        'build the thing.'),
    understand=dict(
        what='A one-thread scheduler. Callers hand it work and a delay; it runs each piece of work once, '
             'no earlier than its deadline, and it does so without burning CPU while it waits.',
        compute='Not a value — a component. The behaviour to get right is: correct ordering by '
                'deadline, no busy-waiting, a caller-visible way to cancel, a clean shutdown, and no '
                'data race on the shared queue.',
        constraints=[
            'Tasks run in **deadline** order, not submission order. Submitting a 10ms task after a '
            '1000ms one must not delay it.',
            'The worker must not poll. Sleeping in a loop and checking is the answer that fails this '
            'question.',
            'A task scheduled **sooner** than whatever the worker is currently waiting for has to '
            'preempt that wait. This is the single most-missed requirement.',
            'Equal deadlines should run in submission order, which a bare priority queue does not '
            'guarantee.',
            '`Schedule` may be called from any thread, concurrently, including from inside a running '
            'task.',
        ],
        assume=[
            ['One worker thread.',
             'With a pool, tasks no longer run one at a time, so a slow task stops delaying the next '
             'one — but the work must then be handed off rather than executed by the timing thread. '
             'Single worker first; say that you know the trade.'],
            ['`Schedule` returns a handle, despite the `void` in the signature.',
             'Otherwise cancellation is impossible, and the statement asks for cancellation. This is a '
             'contradiction in the question and worth naming rather than resolving silently.'],
            ['A task that throws must not kill the scheduler.',
             'Nothing in the statement says so. If exceptions should propagate to the caller, that needs '
             'a `Task`-based API, which is a different design.'],
            ['Millisecond resolution, from a monotonic clock.',
             '`Monitor.Wait` takes milliseconds, so sub-millisecond scheduling is not achievable this '
             'way regardless. `Environment.TickCount64`, not `DateTime.Now` — a wall-clock step '
             'would reorder deadlines.'],
        ]),
    examples=[
        ('Ordering', 'schedule(A, 150ms); schedule(B, 40ms); schedule(C, 90ms)', 'runs B, C, A'),
        ('Preemption', 'schedule(X, 400ms); wait 30ms; schedule(Y, 30ms)', 'Y runs at ~60ms, not after X'),
        ('Cancel', 'h = schedule(Z, 120ms); h.Cancel()', 'Z never runs; a second Cancel() returns false'),
        ('Throwing', 'a task throws, then another is scheduled', 'the second still runs — the worker survives'),
        ('Shutdown', 'schedule(W, 30ms); Shutdown(drain: true)', 'W runs; further Schedule throws'),
        ('Load', '500 tasks with delays 0–49ms', 'each runs exactly once'),
    ],
    examples_note='All six are in the test suite and all six are behaviours rather than return values, '
                  'which is what makes this question different from the rest of the page. The '
                  'preemption case is the one that fails on a naive implementation: a worker sleeping '
                  'until the 400ms deadline will not notice the 30ms task unless the scheduling call '
                  'wakes it.',
    observation=(
        'There are two mechanisms and the question is really about the second one.\n\n'
        '*The easy half.* Tasks run in deadline order, so keep them in a **min-heap keyed on absolute '
        'deadline**. Absolute, not remaining, so nothing has to be decremented. `PriorityQueue<TElement, '
        'TPriority>` in .NET does this, and tie-breaking on a monotonic sequence number keeps equal '
        'deadlines in submission order — a bare heap does not promise that, and it is the kind of '
        'thing a test targets.\n\n'
        '*The hard half.* How does the worker wait? Two wrong answers are tempting. **Spinning** burns a '
        'core. **Sleeping in fixed increments** trades latency against CPU and gets both wrong. The right '
        'answer is a **timed condition wait**: the worker takes the lock, looks at the head of the heap, '
        'and calls `Monitor.Wait(gate, msUntilDue)`. It consumes nothing while waiting, and it can be '
        'woken early.\n\n'
        'That last property is the observation the whole design turns on. `Schedule` calls '
        '`Monitor.Pulse` after enqueueing, because **the new task may be due sooner than whatever the '
        'worker is currently waiting for**. Without the pulse, a task scheduled for 30ms behind a task '
        'scheduled for 400ms waits 400ms. It is one line, it has no visible effect in any single-threaded '
        'test, and omitting it is the most common failure on this question.\n\n'
        'And the reason the wait sits inside a `while (true)` re-checking the head, rather than trusting '
        'what it saw before waiting: a wake can come from the timeout, from that `Pulse`, or from nothing '
        'at all — a spurious wakeup. **The loop makes all three identical**, which is why you never '
        'need to distinguish them. That is the actual answer to "spurious wakeups" in the supplied aspect '
        'list: not "handle them", but "structure the code so they need no handling".'),
    brute=dict(
        how='One thread per task: on `Schedule`, start a thread that sleeps for the delay and then runs '
            'the work.',
        cx='O(1) per schedule, and O(n) **threads**.',
        why_not='It is correct, and it is the answer to give first precisely because it is correct — '
                'then explain why it does not survive. A thread costs about a megabyte of stack '
                'committed on demand plus a scheduler entry, so ten thousand pending timers is ten '
                'thousand threads, and the OS scheduler starts to thrash long before that. `Task.Delay` '
                'is a much better version of the same idea because it uses a timer rather than a thread, '
                'and is what I would actually ship. What neither version gives you is a place to stand '
                'for the follow-ups — cancellation, ordering guarantees, shutdown semantics and '
                'introspection all want a single owned queue.'),
    optimal=dict(pipeline=[
        ('INPUT', '`Schedule(Action work, TimeSpan delay)` from any thread'),
        ('TRANSFORMATION', 'Delay becomes an **absolute** deadline: `now + delay`. A sequence number is '
                           'attached for tie-breaking.'),
        ('DATA STRUCTURE', '`PriorityQueue<ScheduledTask, (long DueAt, long Seq)>` guarded by one lock; '
                           'a single background worker thread'),
        ('ALGORITHM', 'The worker loops: look at the head, timed-wait until it is due, pop and run it '
                      '**outside the lock**. `Schedule` enqueues and pulses.'),
        ('OUTPUT', 'The work runs once, no earlier than its deadline; the caller gets a cancellation '
                   'handle'),
    ],
        why=[
            ['Min-heap on `(DueAt, Seq)`',
             'O(log n) insert and O(1) peek, which is what lets the worker decide how long to sleep in '
             'constant time. The `Seq` component is what makes equal deadlines FIFO.'],
            ['Absolute deadlines',
             'Nothing needs decrementing when the worker wakes, and a wake for any reason recomputes the '
             'remaining time correctly from the clock.'],
            ['One lock, not a concurrent collection',
             '`ConcurrentQueue` would be useless here: the worker needs to *wait on a condition* '
             '(“the head is due”), and lock-free collections give you atomicity without '
             'signalling. `Monitor.Wait`/`Pulse` is the primitive that matches the requirement.'],
            ['A single worker thread',
             'Makes the concurrency small enough to reason about: exactly one thread touches the heap '
             'outside `Schedule`. Throughput comes later, by handing work to the thread pool.'],
            ['`volatile bool Cancelled` with lazy removal',
             'Removing an arbitrary element from a heap is O(n). Marking it and skipping it when it '
             'surfaces is O(1), at the cost of holding the record until its deadline. For a scheduler '
             'that is the right trade; the follow-up covers when it is not.'],
        ],
        steps=[
            '`Schedule`: compute `DueAt = now + delay`, take the lock, reject if shut down, assign the '
            'next sequence number, enqueue, **`Monitor.Pulse`**, release, return a handle.',
            'Worker: take the lock and enter the inner loop.',
            'If shut down and there is nothing to drain, return — the thread ends.',
            'If the heap is empty, `Monitor.Wait` with no timeout and re-check.',
            'Peek the head. If it is cancelled, pop it and re-check.',
            'If its deadline has passed, pop it and break out to run it.',
            'Otherwise `Monitor.Wait(gate, msUntilDue)` and re-check from the top.',
            'Outside the lock, re-check the cancelled flag and invoke the work inside a `try`/`catch`.',
        ]),
    walk=dict(
        intro='The preemption case, which is the one that separates a working scheduler from a plausible '
              'one. `X` is scheduled for +400ms, then 30ms later `Y` is scheduled for +30ms.',
        headers=['t (ms)', 'Thread', 'Heap head', 'What happens'],
        rows=[
            ['0', 'caller', '—', 'Schedule(X, 400) → heap [(400, X)], **Pulse**'],
            ['0', 'worker', '(400, X)', 'head not due; `Monitor.Wait(gate, 400)`'],
            ['30', 'caller', '(400, X)', 'Schedule(Y, 30) → heap [(60, Y), (400, X)], **Pulse**'],
            ['30', 'worker', '(60, Y)', '**woken by the Pulse, 370ms early.** Re-reads the head — it changed'],
            ['30', 'worker', '(60, Y)', 'not due yet; `Monitor.Wait(gate, 30)`'],
            ['60', 'worker', '(60, Y)', 'timeout; due → pop Y, release lock, run Y'],
            ['60', 'worker', '(400, X)', 'back in the loop; `Monitor.Wait(gate, 340)`'],
            ['400', 'worker', '(400, X)', 'timeout; pop X and run it'],
        ],
        close='Take out the `Pulse` in `Schedule` and nothing here changes except one line of the trace: '
              'at t=30 the worker stays asleep, and Y runs at t=400 instead of t=60. No exception, no '
              'test failure unless you specifically test preemption, and a scheduler that is silently '
              'wrong by up to the length of the longest pending delay. That is why this is the line to '
              'point at when explaining the design.'),
    code=[
        ('The scheduler', 'Q07_Scheduler.cs', 'DelayScheduler'),
    ],
    codewalk=[
        ('`Monitor.Pulse(_gate)` in `Schedule` — the load-bearing line',
         'The worker may be in a timed wait for a later deadline. The pulse makes it re-read the head. '
         'Without it, correctness degrades by up to the longest pending delay, silently. If one line in '
         'this class is worth narrating out loud, it is this one.'),
        ('Why the wait is inside `while (true)`',
         'After any wake the code starts again from "is the scheduler shut down, is the heap empty, what '
         'is the head, is it due". So a timeout, a pulse from `Schedule`, and a spurious wakeup all take '
         'the same path and none needs to be distinguished. That is the whole answer to the spurious '
         'wakeup item on the aspect list — the structure removes the case rather than handling it.'),
        ('Running the task **outside** the lock',
         '`ready` is captured inside the lock, and invoked after the `lock` block closes. Running inside '
         'would block every `Schedule` for the duration of the task, and a task that schedules more work '
         'would deadlock on a non-reentrant pattern. This is the second most common bug on this question '
         'and the more serious one.'),
        ('`internal sealed class ScheduledTask` — why not private',
         'The public `Handle` takes one in its constructor, and C# rejects a parameter type less '
         'accessible than the method (CS0051). A small, real detail: it came out of the compiler, not out '
         'of taste. The alternative is a factory method on the scheduler.'),
        ('Lazy cancellation, and the `volatile`',
         'Removing an element from the middle of a heap is O(n), so `Cancel` just sets a flag. The worker '
         'skips cancelled tasks when they reach the head and checks again after leaving the lock, since '
         'cancellation can land in between. `volatile` is what makes the write visible to the worker '
         'without taking the lock — `Cancel` is deliberately lock-free so it can never block behind '
         'a running task.'),
        ('The tie-break `Seq`',
         'Priority is the tuple `(DueAt, Seq)`. Without `Seq`, two tasks with the same deadline come out '
         'in whatever order the heap happens to hold them, which is not FIFO and is not stable between '
         'runs. Assigning `Seq` **inside** the lock is what makes it monotonic.'),
        ('`Shutdown(bool drainPending)` — two different Java methods',
         '`shutdown()` runs what is queued and accepts nothing new; `shutdownNow()` discards. Rather than '
         'guessing which was meant, both are here behind one flag, and `_drain` is read in the same '
         'condition the worker already evaluates. Note the consequence: draining a task scheduled an hour '
         'out means the shutdown waits an hour — worth stating as a known limitation rather than '
         'pretending it is a feature.'),
        ('`catch { }` around the invocation',
         'Deliberately swallowing. One task throwing must not take the worker thread with it, because '
         'that would silently stop every future task. In production this logs; an empty catch in an '
         'interview should come with the sentence "and this would log".'),
    ],
    cx=dict(rows=[
        ['`Schedule`', 'O(log n)', 'O(1)', 'One heap insert, under the lock'],
        ['`Cancel`', 'O(1)', 'O(1)', 'Sets a flag; no heap surgery, and no lock'],
        ['worker per task', 'O(log n)', 'O(1)', 'One pop, plus the wait which costs nothing'],
        ['`Shutdown`', 'O(1) or O(n)', 'O(1)', 'O(n) only when discarding, which clears the heap'],
        ['space', '—', 'O(n)', 'One record per pending task, including cancelled ones not yet reached'],
    ],
        note='**Cancelled tasks keep their memory until their deadline arrives**, which is the price of '
             'O(1) cancellation. If most tasks are cancelled — a timeout-per-request pattern, where '
             'the normal case is that the request finishes first — the heap fills with tombstones '
             'and this is the wrong trade. Then you want either an index from handle to heap position for '
             'O(log n) real removal, or a timing wheel where cancellation unlinks from a bucket list in '
             'O(1) with no tombstone at all. Knowing which regime you are in is the point.'),
    edges=[
        ['Delay of zero or negative', 'Clamped to 0, runs immediately. Still goes through the queue, so '
                                      'ordering is preserved rather than jumping the line.'],
        ['`Schedule` after `Shutdown`', 'Throws `InvalidOperationException`, matching '
                                        '`RejectedExecutionException` in Java.'],
        ['Cancel a task already running', 'Returns true but has no effect — the work has already '
                                          'started. Documented rather than pretended away; stopping it '
                                          'would need cooperative cancellation via a token.'],
        ['Cancel twice', 'Second call returns false.'],
        ['A task that throws', 'Caught; the worker survives and the next task runs.'],
        ['A task that schedules more work', 'Works, because the invocation is outside the lock. This is '
                                            'the case that deadlocks a naive implementation.'],
        ['Two tasks with identical deadlines', 'Run in submission order, via the `Seq` tie-break.'],
        ['Empty queue', 'The worker waits untimed and costs nothing until a `Pulse` arrives.'],
        ['Delay longer than `int.MaxValue` ms', '`Math.Min(waitMs, int.MaxValue)` caps the wait; the loop '
                                                'simply waits again. ~24 days per iteration.'],
        ['Clock stepping backwards', 'Deadlines would be mis-ordered relative to new arrivals. '
                                     '`Environment.TickCount64` is monotonic, which is why it is the '
                                     'default rather than `DateTime.UtcNow`.'],
    ],
    fups=[
        dict(q='One slow task delays everything behind it. Fix it.',
             thinking='The timing thread and the execution thread are doing two different jobs, and they '
                      'have been conflated. Separate them and the problem disappears.',
             approach='The worker stops executing and starts dispatching: when a task becomes due, hand '
                      'it to the thread pool (`ThreadPool.UnsafeQueueUserWorkItem`, or `Task.Run`) and go '
                      'straight back to waiting. The timing thread then does O(log n) work per task and '
                      'never blocks.',
             tradeoff='You gain isolation between tasks and lose ordering **of execution** — tasks '
                      'become due in order but may finish in any order, and two tasks can now run '
                      'concurrently, so anything they share needs its own synchronisation. That is a real '
                      'semantic change and Java makes the same one: a single-threaded '
                      '`ScheduledExecutorService` guarantees sequential execution and a pooled one does '
                      'not. Say which guarantee you are offering.',
             t='O(log n) per task on the timing thread', s='O(n) plus the pool'),
        dict(q='Support a repeating task — scheduleAtFixedRate.',
             thinking='The interesting part is what "fixed rate" means when a run overtakes its own '
                      'period, and Java has two different answers for a reason.',
             approach='After running, re-enqueue with the next deadline. **Fixed rate** computes it from '
                      'the original start (`due += period`), so the schedule does not drift. **Fixed '
                      'delay** computes it from completion (`due = now + period`), so a slow task simply '
                      'spaces out.',
             tradeoff='Fixed rate preserves long-run frequency and can **burst**: if one run takes three '
                      'periods, three executions are immediately due and fire back to back, which for a '
                      'health check is exactly wrong. Fixed delay never bursts and drifts. Java '
                      'additionally guarantees a fixed-rate task never runs concurrently with itself, '
                      'which is worth matching. I would default to fixed delay and offer fixed rate '
                      'explicitly — the burst behaviour surprises people in production.',
             t='O(log n) per repetition', s='O(1) per repeating task'),
        dict(q='There are a million pending timers. Is the heap still right?',
             thinking='O(log n) at a million is twenty comparisons, so the heap is not obviously wrong. '
                      'The question is really about the **churn** — insert and cancel rates — '
                      'and about the tombstones.',
             approach='A **timing wheel**: an array of buckets, each a list of tasks due in that slot, '
                      'with a cursor advancing one slot per tick. Insert is O(1), and cancel is O(1) by '
                      'unlinking from the bucket’s list with no tombstone. Long delays use '
                      'hierarchical wheels — hours, minutes, seconds — cascading down, which is '
                      'what Netty and Kafka both do.',
             tradeoff='The wheel gives O(1) insert and true O(1) cancel, and costs you exact ordering '
                      'within a tick plus memory proportional to the number of slots rather than the '
                      'number of tasks. It wins when delays cluster in a known range and churn is high. '
                      'The heap wins when delays are arbitrary and wide, because a wheel covering '
                      'milliseconds to days either needs a hierarchy or a vast array. The condition, not '
                      'the name, is the answer.',
             t='O(1) insert, O(1) cancel, O(tasks in slot) per tick', s='O(slots + tasks)'),
        dict(q='Why not `Task.Delay` and four lines?',
             thinking='In production that is very often the right answer, and saying so is not a '
                      'concession. The statement explicitly says this is not a syntax translation, so '
                      'the question is whether you know what you are giving up.',
             approach='`await Task.Delay(delay, token); work();` gets you delayed execution, cancellation '
                      'via the token, and no thread per timer — it is backed by a timer queue, so it '
                      'is not the thread-per-task brute force. What it does not give you is one owned '
                      'queue you can inspect, ordering guarantees across tasks, drain-versus-discard '
                      'shutdown semantics, or a place to change the timing structure later.',
             tradeoff='I would ship `Task.Delay` for a handful of timers and build this for a scheduler '
                      'that is a component of the system — anything that needs to answer "what is '
                      'pending", "shut down cleanly", or "a million of these". What I would not do is '
                      'build it while pretending the library option does not exist.',
             t='O(1) per timer', s='O(1) per timer, plus the runtime timer queue'),
        dict(q='How would you test this? It is time-dependent and concurrent.',
             thinking='Worth raising unprompted, because untestable concurrency is how this kind of '
                      'component rots, and the fix is a design decision rather than a testing technique.',
             approach='The clock is already injected as `Func<long>`, so ordering logic can be tested '
                      'against a virtual clock with no sleeping at all. What the injected clock cannot '
                      'fake is `Monitor.Wait`’s timeout, which is real time — so the behavioural '
                      'tests (preemption, cancellation, survival of a throwing task, 500 tasks each '
                      'running exactly once) do use real delays, with generous margins so they are not '
                      'flaky on a loaded machine.',
             tradeoff='A fully virtual clock would need the wait itself to be abstracted behind an '
                      'interface, which is more indirection than this class earns. Splitting it — '
                      'virtual clock for the decisions, real time for the waiting — gets most of the '
                      'determinism for one constructor parameter. Whether the clock is injectable at all '
                      'is the tell for whether someone has maintained a component like this.',
             t='—', s='—'),
    ],
    testing=dict(skills=[
        '**Concurrency primitives** — `lock`, `Monitor.Wait`, `Monitor.Pulse`, and why a concurrent '
        'collection is not a substitute for condition signalling.',
        '**Condition-variable discipline** — the re-checking loop, and understanding that it is what '
        'makes spurious wakeups a non-issue.',
        '**The preemption insight** — pulsing on schedule. This is the single discriminating detail.',
        '**Lock scope** — running the task outside the lock.',
        '**Lifecycle design** — cancellation semantics, drain versus discard, what happens to a task '
        'already running.',
        '**Knowing the library** — and being able to say why you are not using it.',
        '**Testability** — whether the clock is injectable.',
    ],
        senior='Gets the heap on deadline, one worker thread, a timed `Monitor.Wait`, a lock around the '
               'queue, and lazy cancellation. That is a working scheduler and most candidates do not get '
               'there.',
        staff='Does that, and: pulses on schedule **and explains the failure mode without it**; runs the '
              'task outside the lock and says which bug that avoids; names the `void`-versus-handle '
              'contradiction in the supplied signature; distinguishes `shutdown` from `shutdownNow` '
              'rather than implementing one; says that lazy cancellation leaves tombstones and names the '
              'workload where that becomes the wrong trade; offers the timing wheel **with the condition '
              'under which it wins**; and injects the clock so the thing can be tested. The preemption '
              'pulse and the lock scope are the two that separate people who have written this from '
              'people who have read about it.'),
    say=[
        "Before I build this — in C# the four-line answer is await Task.Delay then run the work, and for a "
        "handful of timers that is what I would ship. Your statement says this is not a syntax "
        "translation, so I will build the component, but I wanted to say the library option exists.",
        "Also, the signature returns void, and you have asked about cancellation. Those are incompatible — "
        "there is nowhere for a cancellation handle to go. Java returns a ScheduledFuture for exactly that "
        "reason, so I will return a handle.",
        "The structure is a min-heap keyed on absolute deadline. Absolute, not remaining, so nothing has "
        "to be decremented when the worker wakes up. And I tie-break on a sequence number, so two tasks "
        "with the same deadline run in submission order.",
        "The interesting half is how the worker waits. Spinning burns a core. Sleeping in fixed increments "
        "trades latency against CPU and loses both. So: take the lock, look at the head, and call "
        "Monitor.Wait with a timeout of however long until it is due.",
        "Now the line that actually matters. When Schedule enqueues, it pulses. Because the worker might "
        "be asleep waiting for a deadline 400 milliseconds out, and the task I just scheduled is due in "
        "30. Without that pulse it sleeps through it. No crash, no exception — the scheduler is just "
        "silently late by up to the longest pending delay.",
        "The wait sits inside a loop that re-reads the head from scratch. That means a timeout, my pulse, "
        "and a genuine spurious wakeup all take the same path. I do not have to tell them apart, which is "
        "the real answer to handling spurious wakeups — structure it so there is nothing to handle.",
        "I run the task outside the lock. Holding it would block every Schedule call for as long as the "
        "task takes, and a task that schedules more work would deadlock.",
        "Cancellation sets a volatile flag and the worker skips it when it surfaces. Removing from the "
        "middle of a heap is O(n), so I take O(1) cancellation and accept that the record sits there until "
        "its deadline. If most tasks were cancelled — a per-request timeout, say — that is the wrong "
        "trade, and I would want a timing wheel where cancel unlinks from a bucket.",
        "For shutdown I would support both Java behaviours: drain what is queued, or discard it. I would "
        "not guess which you meant.",
        "One limitation worth saying: a single worker means a slow task delays everything behind it. The "
        "fix is for the worker to dispatch to the thread pool rather than execute, and the cost is that "
        "tasks no longer run sequentially.",
    ],
    video=dict(title='LinkedIn Coding — Build a Delay Scheduler', mins=18,
               objective='Build the component, then spend most of the lesson on the two details that '
                         'separate a working scheduler from a plausible one: the pulse on schedule, and '
                         'the lock scope.',
               beats=[('0:00', 'The question, and the nine aspects it names'),
                      ('1:30', 'The library answer, and why we are not giving it'),
                      ('2:40', 'The void-versus-handle contradiction'),
                      ('3:50', 'Brute force: a thread per task'),
                      ('5:00', 'Min-heap on absolute deadline, and the tie-break'),
                      ('6:40', 'How does the worker wait? Three options, one right'),
                      ('8:20', 'The pulse on schedule — the load-bearing line'),
                      ('10:10', 'Tracing the preemption case'),
                      ('11:40', 'Why the re-checking loop removes spurious wakeups'),
                      ('12:50', 'Running outside the lock'),
                      ('14:00', 'The C# implementation'),
                      ('15:30', 'Cancellation, tombstones, and when to use a timing wheel'),
                      ('16:50', 'Shutdown: drain or discard'),
                      ('17:40', 'How to say it')]),
))

# ============================================================ Q8
QUESTIONS.append(dict(
    id='q8', n=8, name='Word transformation (doublets)',
    tags=['GRAPH', 'BFS', 'STRING', 'HASHING', 'DESIGN'],
    diff='HARD', prio='HIGH',
    verdict_short='InterviewDB + 2 independent reports of Word Ladder',
    prio_why=(
        '`127 Word Ladder` is on the supplied list **and** has two independent reports in the existing '
        'research, and it is already worked in the coding video course. The InterviewDB framing adds the '
        'part that makes it a Staff question rather than a LeetCode question: *"convert to an online '
        'service with minimal latency"*. High priority, and the follow-ups are where the time should go.'),
    idb=(
        'Given:\n\n'
        '• dictionary\n'
        '• start word\n'
        '• end word\n\n'
        'Each transformation changes exactly one character and the resulting word must exist in the '
        'dictionary.\n\n'
        'Return minimum number of transformations.\n\n'
        'Example:\n\n'
        'APE -> APT -> OPT -> OAT -> MAT -> MAN\n\n'
        'Output:\n\n'
        '5\n\n'
        'Follow-ups:\n'
        '• Convert to an online service with minimal latency\n'
        '• Will cycles be output?\n'
        '• What if letters can be added or removed?'),
    dd=dict(elsewhere=[
        ('idb', 'Supplied with a worked example that settles the units: six words, output **5**. So the '
                'answer counts **edges**, not words. That one number is the most useful thing in the '
                'statement.'),
        ('reported', '**Word Ladder (LeetCode 127)** — two independent reports in the existing '
                     'research, and it is on the reader-supplied list. Already a worked lesson in the '
                     'coding video course.'),
        ('reported', '`490 The Maze` and other BFS problems recur across the Taro and Blind reports, so '
                     'BFS-with-an-interesting-neighbour-function is a well-attested LinkedIn shape.'),
        ('lc', '127 is the same problem. **72 Edit Distance is on the supplied list too**, and it is the '
               'third follow-up in disguise — once letters can be added or removed, adjacency '
               'becomes "edit distance 1".'),
    ],
        verdict='**InterviewDB reported, independently reported twice, and already covered in this '
                'workspace.** High confidence. The three supplied follow-ups are what is new here.',
        conflict='**LeetCode 127 and this question return different numbers for the same input.** '
                 'LeetCode returns the length of the transformation *sequence* (the number of words); '
                 'this returns the number of *transformations* (the number of edges). For `hit → '
                 'cog` LeetCode says 5 and this says 4. Both are correct under their own definition. Do '
                 'not silently convert one to the other — say which you are returning. The test '
                 'suite asserts the edge count, and documents the LeetCode difference in the assertion '
                 'message.'),
    understand=dict(
        what='A dictionary is secretly a graph. Two words are neighbours if they differ in exactly one '
             'position. You are asked for the shortest path between two of them, walking only through '
             'real words.',
        compute='The number of single-character changes on the shortest chain, or a sentinel if no chain '
                'exists.',
        constraints=[
            'Every intermediate word must be in the dictionary. That is what makes it a graph search '
            'rather than a string-distance calculation.',
            'All words are the same length in the base problem. The third follow-up removes that.',
            'Every step costs 1, so BFS is optimal and Dijkstra is unnecessary.',
            'The dictionary can be large — tens of thousands of words — which is why the '
            'neighbour function, not the search, is the design problem.',
        ],
        assume=[
            ['The start word need not be in the dictionary; the end word must be.',
             'LeetCode 127 makes the same choice. If the start must also be present, that is one '
             'validation line. If the **end** need not be, the question is unanswerable — you could '
             'never legally arrive.'],
            ['Case and alphabet are consistent.',
             'The example is uppercase. Mixed case would need normalising, and the wildcard index would '
             'have to be built on the normalised form or it silently misses neighbours.'],
            ['The answer counts edges.',
             'Fixed by the supplied example: six words, output 5. **This is where LeetCode differs**, so '
             'state it.'],
            ['The dictionary is static in the base problem.',
             'The online-service follow-up makes it dynamic, which is why the index is built behind a '
             'method rather than inline in the constructor.'],
        ]),
    examples=[
        ('Given', 'APE → APT → OPT → OAT → MAT → MAN', '5 — six words, five transformations'),
        ('Mine', 'APE → APT', '1'),
        ('Mine', 'APE → APE', '0'),
        ('Mine', 'end word not in the dictionary', '-1'),
        ('Mine', 'AAA → XXX with dictionary {AAA, AAB, XXX}', '-1 — no chain of real words exists'),
        ('LeetCode', 'hit → cog, dictionary {hot,dot,dog,lot,log,cog}', '**4 here, 5 on LeetCode 127**'),
    ],
    examples_note='The last row is the one to remember. It is in the test suite with that discrepancy '
                  'written into the assertion message, because it is the single most likely way to lose '
                  'marks on a question you otherwise know. The two implementations — plain and '
                  'bidirectional — are also cross-checked against each other on 200 random pairs '
                  'over a 250-word generated dictionary.',
    observation=(
        'The words are not the problem. **Finding the neighbours is the problem**, and that is the whole '
        'question.\n\n'
        'Once you see that two words are adjacent when they differ in one position, the search is '
        'textbook BFS. But how do you find the neighbours of `APE`? The obvious way is to compare it '
        'against every word in the dictionary: O(N · L) per expansion, which at N = 50,000 makes '
        'each step of the search a scan of the whole dictionary.\n\n'
        'The trick is to **index by wildcard**. For each word, generate the patterns you get by blanking '
        'each position in turn — `APE` gives `*PE`, `A*E`, `AP*` — and store the word under all '
        'three. Now two words are neighbours exactly when they share a pattern, so the neighbours of '
        '`APE` are the union of three dictionary lookups. Each expansion drops from O(N · L) to '
        'O(L) lookups, and the cost moves to a one-off O(N · L) build.\n\n'
        'That move — **precompute a canonical key so the expensive comparison becomes a hash '
        'lookup** — is the same idea as Q11’s keypad signature and the same idea behind '
        'LeetCode 244. It is worth naming as a pattern rather than as a trick for this problem, because '
        'it is what makes the online-service follow-up answerable: the build happens once at startup, and '
        'every query is then pure BFS over hash lookups.\n\n'
        'The second observation is for the follow-up, and it is the same one as Q5: searching from both '
        'ends turns `b^d` into `2 · b^(d/2)`. Here the branching factor is genuinely large — '
        'each word has up to 25 · L neighbours — so bidirectional BFS matters more than it does '
        'on a social graph.'),
    brute=dict(
        how='BFS, and for each word in the frontier scan the entire dictionary looking for words that '
            'differ in exactly one position.',
        cx='O(N² · L) in the worst case — every one of N words compared against all N, at '
            'L character comparisons each. O(N) space.',
        why_not='At N = 50,000 and L = 5 that is over ten billion character comparisons for one query, '
                'and it repeats the same comparisons on every query. The useful framing is that the '
                'brute force recomputes adjacency **per query** something that is a property of the '
                '**dictionary** — and anything that depends only on the dictionary should be '
                'computed once. That reframing is what leads to the wildcard index, and it is also '
                'exactly the argument the online-service follow-up wants.'),
    optimal=dict(pipeline=[
        ('INPUT', 'A dictionary, a start word and an end word'),
        ('TRANSFORMATION', 'Every word is indexed under L wildcard patterns, one per blanked position'),
        ('DATA STRUCTURE', '`Dictionary<string, List<string>>` from pattern to words; `HashSet<string>` '
                           'for the dictionary and for visited; `Queue<string>` for the frontier'),
        ('ALGORITHM', 'Level-by-level BFS, neighbours via L pattern lookups. Bidirectional: expand the '
                      'smaller frontier and stop when the two searches meet.'),
        ('OUTPUT', 'The number of transformations, or -1'),
    ],
        why=[
            ['`Dictionary<string, List<string>>` keyed on wildcard patterns',
             'Turns neighbour generation from a dictionary scan into L hash lookups. The one-off build '
             'cost is paid back on the first query.'],
            ['`HashSet<string>` with `StringComparer.Ordinal`',
             'Ordinal comparison is both faster and *correct* here — culture-aware comparison can '
             'treat different strings as equal, which in a word-graph silently merges nodes. This is a '
             'real C# footgun and worth one sentence.'],
            ['Level-by-level BFS rather than `(word, depth)` pairs',
             'Less state, and `steps++` happens in exactly one place, which is where the edge-versus-word '
             'convention lives.'],
            ['`HashSet` frontiers in the bidirectional version, not queues',
             'A frontier has to be countable (to pick the smaller side) and membership-testable (to '
             'detect the meeting). A queue is neither.'],
            ['`Index` as a separate method',
             'So `AddWord` can reuse it. The dynamic-dictionary follow-up is then two lines instead of a '
             'redesign.'],
        ],
        steps=[
            'Build: for each dictionary word, for each position, blank it and append the word to that '
            'pattern’s list.',
            'Guard: different lengths → -1; identical words → 0; end word absent → -1.',
            'Seed the frontier with the start word, mark it visited, `steps = 0`.',
            'Take the whole level. `steps++`.',
            'For each word, for each of its L patterns, for each word in that bucket: if it is the end '
            'word, return `steps`; if unseen, mark and queue it.',
            'Queue empties → -1.',
        ]),
    walk=dict(
        intro='The supplied example. Dictionary `{APE, APT, OPT, OAT, MAT, MAN, OPE, CAT, COT}`, from '
              '`APE` to `MAN`. Only the words that matter are shown per level.',
        headers=['steps', 'Frontier', 'Patterns looked up', 'Discovered', 'Note'],
        rows=[
            ['0', '{APE}', '—', '—', 'seeded'],
            ['1', '{APE}', '*PE, A*E, AP*', 'OPE, APT', 'both are one change from APE'],
            ['2', '{OPE, APT}', '*PE/O*E/OP* and *PT/A*T/AP*', 'OPT', 'OPT reachable from both'],
            ['3', '{OPT}', '*PT, O*T, OP*', 'OAT, COT', ''],
            ['4', '{OAT, COT}', '*AT, O*T, OA* …', 'MAT, CAT', ''],
            ['5', '{MAT, CAT}', '*AT, M*T, **MA***', '**MAN**', '`MA*` contains MAN → **return 5**'],
        ],
        close='Five levels, five transformations, matching the supplied output. Note the mechanism at the '
              'last step: `MAT` blanked at position 2 gives `MA*`, and `MAN` is in that bucket. No '
              'comparison against any other word happened — the whole expansion was three hash '
              'lookups. That is the wildcard index doing the work.'),
    code=[
        ('The service: index once, then BFS per query', 'Q08_WordLadder.cs', 'WordTransformer'),
    ],
    codewalk=[
        ('Why `Index` reuses one `char[]` and restores it',
         '`chars[i] = \'*\'` then `chars[i] = keep`. Allocating a fresh array per position would be '
         'L times the garbage for no benefit. `new string(chars)` still allocates the pattern — '
         'unavoidable, since it is the dictionary key — but the buffer is reused. Small, and it is '
         'the difference between a build that scales and one that pressures the GC on a large dictionary.'),
        ('`StringComparer.Ordinal`, deliberately',
         'Passed to every `HashSet` and `Dictionary`. Without it, .NET uses the default comparer, and for '
         'strings the culture-sensitive paths can treat distinct sequences as equal. In a word graph that '
         'means two different words collapse into one node and the shortest path can come out wrong. It '
         'is also measurably faster.'),
        ('The neighbour function is an iterator',
         '`yield return` means the BFS stops as soon as it finds the end word, without materialising the '
         'rest of the neighbours. On a word with 100 neighbours where the second one is the target, that '
         'is 98 fewer set operations.'),
        ('`if (w != word)` inside the bucket',
         'A word is in its own wildcard buckets, so it would otherwise be its own neighbour. Harmless '
         '(the visited set catches it) and worth excluding anyway, because "a word is one change from '
         'itself" is not true and the code should not say it is.'),
        ('Why the end-word check is on discovery',
         'Returning `steps` the moment the end word is seen as a neighbour, rather than waiting to '
         'dequeue it, is what makes `steps` the edge count. `steps++` has already happened for this '
         'level, so it equals the number of edges traversed to reach the neighbour. Moving the check to '
         'the dequeue point without moving `steps++` gives an answer one too large — which, not '
         'coincidentally, is the LeetCode 127 answer.'),
        ('The bidirectional swap',
         '`(frontA, frontB) = (frontB, frontA);` together with `(seenA, seenB)`. Both must move, or the '
         'meeting test checks the wrong set. `steps++` once per round is still correct because each round '
         'lays down exactly one edge, whichever side expanded — and that is the part I would not '
         'trust by inspection, which is why 200 random pairs are cross-checked against plain BFS.'),
        ('`AddWord` is three lines',
         '`if (_words.Add(word)) Index(word);` — the dynamic-dictionary follow-up, for free, because '
         'indexing was factored out. Removal would be harder: it needs the word pulled from L buckets, '
         'so the buckets would want to be sets rather than lists.'),
    ],
    cx=dict(rows=[
        ['build', 'O(N · L²)', 'O(N · L²)',
         'N words × L patterns, each pattern a string of length L'],
        ['`MinTransformations`', 'O(V + E) worst case', 'O(N)',
         'E is bounded by the total bucket sizes; each word is visited once'],
        ['neighbours of one word', 'O(L + bucket sizes)', 'O(1) extra',
         'L hash lookups instead of a dictionary scan'],
        ['`MinTransformationsBidirectional`', 'O(b^(d/2)) typical', 'O(b^(d/2))',
         'Two shallow searches rather than one deep one'],
        ['`AddWord`', 'O(L²)', 'O(L²)', 'L new pattern keys for one word'],
    ],
        note='**The build is O(N · L²), not O(N · L)** — each of the L patterns is '
             'itself a string of length L that has to be constructed and hashed. At N = 50,000 and '
             'L = 5 that is about 1.25 million character operations, which is nothing; at L = 20 it '
             'starts to matter, and a rolling hash would be the fix. Getting the L² right rather '
             'than saying L is a small piece of precision that is easy to be sloppy about.'),
    edges=[
        ['Start equals end', '0, before any search.'],
        ['Different lengths', '-1. Single-character substitution cannot change length in the base '
                              'problem.'],
        ['End word not in the dictionary', '-1, checked up front — otherwise the search runs to '
                                          'exhaustion for nothing.'],
        ['Start word not in the dictionary', 'Allowed. Its neighbours still come from the buckets, which '
                                             'contain only real words, so the path is legal.'],
        ['No path exists', '-1 when the queue empties. The bidirectional version must exit when '
                           '**either** frontier empties.'],
        ['Empty dictionary', '-1, via the end-word check.'],
        ['Single-character words', 'Works; every word is one change from every other, so the answer is '
                                   'almost always 1.'],
        ['Duplicate words in the input', '`HashSet` de-duplicates, so buckets hold each word once.'],
        ['Mixed case', 'Treated as distinct under ordinal comparison. Normalise at the boundary if that '
                       'is wrong.'],
        ['A very large bucket', 'A pattern like `*AT` can hold many words. That is the real branching '
                                'factor, and it is the argument for searching from both ends.'],
    ],
    fups=[
        dict(given=True, q='Convert this to an online service with minimal latency.',
             thinking='The question is which work depends on the **dictionary** and which depends on the '
                      '**query**. Anything in the first category should happen once, at startup, not per '
                      'request. That single split is most of the answer.',
             approach='Four things, in order of payoff.\n\n'
                      '**Build the wildcard index once at startup**, not per request — that is '
                      'already how the class is written, and it is the whole reason the constructor takes '
                      'the dictionary.\n\n'
                      '**Use bidirectional BFS per query**, since it is the single biggest constant '
                      'reduction available and the branching factor here is large.\n\n'
                      '**Cache answers.** Word pairs repeat heavily in any real workload, and the result '
                      'is immutable for a fixed dictionary, so an LRU cache keyed on the unordered pair '
                      'is a near-free win — which is Q1, and worth pointing out that the two '
                      'questions compose.\n\n'
                      '**Shard by word length.** Words of different lengths can never be neighbours, so '
                      'the graph is already partitioned. Each shard is independent, holds a smaller '
                      'index, and can be served by a different process with no coordination at all.',
             tradeoff='Memory for latency, and staleness for speed. The index is roughly L² strings '
                      'per word, so a 500,000-word dictionary at L = 8 is a real amount of memory and is '
                      'the reason sharding by length is attractive. The cache introduces an invalidation '
                      'problem the moment the dictionary changes — and since adding one word can '
                      'shorten arbitrarily many paths, the honest answer is to version the dictionary and '
                      'key the cache on the version, so an update invalidates everything at once rather '
                      'than trying to be clever about which entries changed.',
             t='O(1) on a cache hit; O(b^(d/2)) otherwise', s='O(N · L²) for the index'),
        dict(given=True, q='Will cycles be output?',
             thinking='Two readings, and the useful answer covers both rather than picking one. Either '
                      '"can the algorithm loop forever" or "can the returned path revisit a word".',
             approach='**No, to both, and for the same reason.** The visited set means each word is '
                      'enqueued at most once, so the search cannot loop. And BFS explores in order of '
                      'increasing distance, so the first time it reaches a word is via a shortest path '
                      '— a path that revisited a word would be strictly longer than the same path '
                      'with the loop removed, so it can never be the one found.\n\n'
                      'The graph itself is full of cycles, of course. The point is that a shortest path '
                      'in any graph is always simple, and BFS finds shortest paths.',
             tradeoff='None here — it is a property of the algorithm, not a design decision. Where it '
                      'would matter is if you dropped the visited set to enumerate *all* paths: then '
                      'cycles become possible and you need per-path tracking rather than a global set, '
                      'and the cost goes exponential.',
             t='unchanged', s='unchanged'),
        dict(given=True, q='What if letters can be added or removed?',
             thinking='This is the follow-up that changes the graph rather than the search, and **it is '
                      'LeetCode 72 arriving through the back door** — which is presumably why 72 is '
                      'on the supplied number list.',
             approach='Adjacency becomes "edit distance exactly 1", so words of *different* lengths are '
                      'now neighbours and the graph is no longer partitioned by length. BFS still '
                      'applies; only the neighbour function changes.\n\n'
                      'The wildcard index needs a second half. For substitution, keep the existing '
                      '`A*E`-style patterns. For insertion and deletion, index each word under every '
                      '**deletion** of one character: `APE` also goes under `PE`, `AE`, `AP`. Then a word '
                      'of length L and a word of length L+1 are neighbours exactly when the shorter one '
                      'equals one of the longer one’s deletion patterns — so deletion '
                      'neighbours are, again, hash lookups rather than comparisons.',
             tradeoff='The index roughly doubles, and the branching factor grows a lot, because a word is '
                      'now adjacent to longer and shorter words as well. Length-based sharding is '
                      'lost — which is a real cost, since it was the cleanest scaling axis. '
                      'Bidirectional search becomes more valuable, not less, because b went up. If the '
                      'question were the *distance* rather than the dictionary-constrained *path*, this '
                      'stops being a graph problem and becomes the O(L¹ · L²) DP of '
                      'LeetCode 72 — worth distinguishing the two out loud, because they sound the '
                      'same and are not.',
             t='O(V + E) with a larger E', s='roughly 2× the index'),
        dict(q='Return the path, not just the length.',
             thinking='BFS already knows it; it just is not recording it. Same as Q5.',
             approach='A `Dictionary<string, string> parent` populated when a word is first discovered, '
                      'walked back from the end word. For the bidirectional version, two parent maps '
                      'joined at the meeting word, with one side reversed — and the meeting word '
                      'belongs to both, so it must not be emitted twice.',
             tradeoff='O(N) extra memory, which is the same order as the visited set. Storing the whole '
                      'path per frontier entry instead is the tempting shortcut and multiplies memory by '
                      'the path length. If **all** shortest paths are wanted — which is LeetCode '
                      '126 — the parent becomes a list of parents and the reconstruction becomes a '
                      'DFS over the resulting DAG, and the output can be exponentially large.',
             t='O(b^(d/2)) plus O(d) to reconstruct', s='O(N)'),
        dict(q='The dictionary changes while the service is running.',
             thinking='Additions are easy and removals are not, which is worth saying in that order.',
             approach='`AddWord` indexes the new word into its L buckets — already implemented, '
                      'O(L²). Removal is harder: the word has to be pulled out of L buckets, and '
                      'with `List<string>` buckets that is a linear scan of each. If removal matters, '
                      'make the buckets `HashSet<string>` so it is O(L) instead.\n\n'
                      'The bigger problem is the cache. One added word can shorten unboundedly many '
                      'paths, so there is no cheap partial invalidation — version the dictionary and '
                      'key cached answers on the version.',
             tradeoff='`List` buckets are faster to build and to iterate, and slower to delete from. '
                      '`HashSet` buckets are the opposite. Choose on the read/write ratio, which for a '
                      'dictionary is overwhelmingly reads — so `List` is the right default and '
                      'switching is the right answer only if removals are real.',
             t='O(L²) add; O(L) removal with set buckets', s='unchanged'),
    ],
    testing=dict(skills=[
        '**Modelling** — seeing a dictionary as a graph, which is the step everything else depends '
        'on.',
        '**Locating the real cost** — the neighbour function, not the search.',
        '**Precompute-versus-per-query reasoning** — the same instinct as Q11 and LeetCode 244, and '
        'exactly what the online-service follow-up is testing.',
        '**Bidirectional BFS** — including why the branching factor makes it matter more here than '
        'elsewhere.',
        '**Convention precision** — edges versus words, where LeetCode disagrees with the question.',
        '**Knowing the neighbouring problem** — that the add/remove follow-up is edit distance, and '
        'that the DP and the BFS answer different questions.',
    ],
        senior='Models it as a graph, builds the wildcard index, writes a correct level-by-level BFS, and '
               'produces bidirectional BFS when prompted.',
        staff='Does that, and: states the edge-versus-word convention and that LeetCode 127 differs; '
              'gets the build cost right as O(N · L²) rather than O(N · L); answers the '
              'online-service follow-up by splitting dictionary-dependent from query-dependent work '
              'rather than by listing optimisations; notices that sharding by word length is free in the '
              'base problem **and that the add/remove follow-up destroys it**; recognises the third '
              'follow-up as edit distance and distinguishes the dictionary-constrained path from the '
              'unconstrained DP; and uses `StringComparer.Ordinal` for a stated reason. The sharding '
              'observation and its loss is the sharpest signal here — it shows the follow-up was '
              'evaluated against the earlier design rather than answered in isolation.'),
    say=[
        "Let me restate the structure: a dictionary is a graph where two words are adjacent if they differ "
        "in one position. All edges cost 1, so shortest path means BFS.",
        "From your example — six words, output five — the answer counts transformations, not words. Worth "
        "pinning down, because LeetCode 127 is the same problem and returns the word count, so the same "
        "input gives a different number.",
        "The search is the easy part. The real problem is finding the neighbours of a word. Comparing "
        "against every dictionary entry is O(N times L) per expansion, and it redoes on every query "
        "something that is a property of the dictionary, not of the query.",
        "So I index by wildcard. APE gets stored under star-P-E, A-star-E and A-P-star. Two words are "
        "neighbours exactly when they share a pattern, so neighbours become three hash lookups instead of "
        "a scan. The build is O(N times L squared) — L patterns, each a string of length L.",
        "Then BFS level by level, and I return the level count the moment I see the end word as a "
        "neighbour.",
        "On your online-service follow-up — the key question is what depends on the dictionary and what "
        "depends on the query. The index depends only on the dictionary, so it is built once at startup. "
        "Then bidirectional BFS per query, because the branching factor here is large — up to 25 times L "
        "neighbours per word — so halving the depth is worth a lot. Then cache by word pair, since the "
        "result is immutable for a fixed dictionary. And I would shard by word length, because words of "
        "different lengths can never be neighbours, so the graph is already partitioned for free.",
        "On cycles — no, and for one reason. The visited set means each word is enqueued once, so the "
        "search cannot loop. And any path that revisited a word would be longer than the same path with "
        "the loop cut out, so BFS would never return it. A shortest path is always simple.",
        "On adding and removing letters — that changes the graph, not the search. Adjacency becomes edit "
        "distance one, so different-length words are now neighbours. I would index each word under every "
        "single-character deletion as well, so PE, AE and AP for APE, and then a shorter word is adjacent "
        "to a longer one when it matches one of its deletion patterns.",
        "One consequence worth flagging: that kills the length-based sharding I just proposed, because the "
        "graph is no longer partitioned by length. So that follow-up costs me my cleanest scaling axis.",
        "And if you wanted the distance rather than a path through real words, that is not this algorithm "
        "at all — that is the edit-distance DP.",
    ],
    video=dict(title='LinkedIn Coding — Word Transformation and the Wildcard Index', mins=18,
               objective='Show that the neighbour function is the problem, derive the wildcard index, '
                         'then use the three supplied follow-ups to turn it into a service.',
               beats=[('0:00', 'The question, and what the example tells you about units'),
                      ('1:40', 'Edges or words — and where LeetCode disagrees'),
                      ('3:00', 'A dictionary is a graph'),
                      ('4:20', 'The real cost: finding neighbours'),
                      ('6:00', 'The wildcard index'),
                      ('8:00', 'Walking APE to MAN'),
                      ('9:40', 'The C# implementation'),
                      ('11:20', 'Build cost is N·L², not N·L'),
                      ('12:20', 'Follow-up: the online service, split by what depends on what'),
                      ('14:00', 'Sharding by word length — free, and then lost'),
                      ('15:10', 'Follow-up: cycles, and why shortest paths are simple'),
                      ('16:10', 'Follow-up: add and remove letters is edit distance'),
                      ('17:20', 'How to say it')]),
))

# ============================================================ Q9
QUESTIONS.append(dict(
    id='q9', n=9, name='Interval tree — covered size',
    tags=['INTERVAL TREE', 'SEGMENT TREE', 'DATA STRUCTURE DESIGN', 'DESIGN', 'BINARY SEARCH'],
    diff='HARD', prio='MEDIUM',
    verdict_short='InterviewDB ×2 (title and statement) + a merge-intervals report',
    prio_why=(
        '**InterviewDB twice**: "Interval Tree" was one of the visible titles on the partially-paywalled '
        'list before you bought access, and now the full statement confirms it with the O(log n) / O(1) '
        'constraint. Separately a **merge-intervals variant where you choose the data structure** is '
        'reported, and `57 Insert Interval` is on the supplied number list. Medium rather than high '
        'because the framing is single-source, but the constraint makes it the most technically '
        'interesting question on the page.'),
    idb=(
        'Implement:\n\n'
        'void addInterval(int start, int end)\n\n'
        'Must be O(log n).\n\n'
        'int getCoveredSize()\n\n'
        'Must be O(1).\n\n'
        'Use a segment tree or interval tree.\n\n'
        'Discuss assumptions around: coordinate ranges, overlapping intervals, adjacent intervals, '
        'duplicates, removal if relevant.'),
    dd=dict(elsewhere=[
        ('idb', 'Supplied with **explicit complexity requirements**, which is unusual and is the whole '
                'question. It also names the structures to consider and lists the assumptions to '
                'discuss — effectively the marking scheme.'),
        ('idb', '"Interval Tree" was already a visible title on the interviewdb list before access was '
                'bought, and was worked in this workspace from the title alone. **The statement now '
                'confirms the guess and adds the constraint that makes it hard.**'),
        ('reported', 'A **merge-intervals variant where the candidate chooses the data structure** is '
                     'reported in the existing research — the same problem shape, without the '
                     'complexity bound.'),
        ('lc', '57 Insert Interval is on the supplied list and is the same merge-on-insert logic, '
               'returning the list instead of maintaining a total. **715 Range Module** (Hard, not on the '
               'supplied list) is the closest real match, and its difficulty rating is the honest one for '
               'this.'),
    ],
        verdict='**InterviewDB reported twice, with an independently reported near-neighbour.** The '
                'complexity constraint is the InterviewDB-specific part and is where the answer lives.',
        conflict='**The stated O(log n) for `addInterval` is not achievable as a worst case, and saying '
                 'so is part of the answer.** A single insert can absorb an unbounded number of existing '
                 'intervals — add [0,1), [2,3), [4,5) … then add [0,1000) and one call removes '
                 '500 of them. The bound is **amortised** O(log n), because each interval is removed at '
                 'most once over the life of the structure. Claiming strict O(log n) is wrong and is '
                 'trivially disproved; saying "amortised, and here is the adversarial input" is the '
                 'strongest thing you can do with this question.'),
    ambiguity=(
        'Is the interval closed `[start, end]` or half-open `[start, end)`? It changes the answer to '
        '`getCoveredSize()` and it changes whether `[1,5]` and `[5,9]` merge.\n\n'
        'I take **half-open**, so length is `end - start` and touching intervals coalesce. That is the '
        'convention that makes the arithmetic clean and matches how intervals are represented almost '
        'everywhere in practice. Under the closed reading, `[1,5]` has length 5 rather than 4, and '
        '`[1,5]` followed by `[6,9]` should merge because the integers are adjacent — which means '
        'the merge condition needs `prev.End + 1 >= start` instead of `prev.End >= start`.\n\n'
        'This is not pedantry: it is one of the assumptions the statement explicitly asks you to discuss, '
        'and it is the difference between two implementations that both look right.'),
    understand=dict(
        what='A running total of covered ground. Intervals arrive one at a time, they overlap arbitrarily, '
             'and at any moment you must be able to say how much of the line is covered — counting '
             'overlapped regions once.',
        compute='`getCoveredSize()` returns the total length of the union of everything added. Not the sum '
                'of the lengths — the length of the union.',
        constraints=[
            '`getCoveredSize()` must be **O(1)**. That single requirement is what forces the design: the '
            'answer cannot be computed on demand, so it must be maintained.',
            '`addInterval` must be O(log n), which means finding where the interval belongs by search '
            'rather than by scan.',
            'Intervals may overlap, nest, touch, or duplicate. All four have to be handled and they are '
            'not the same case.',
            'Coordinates are `int`, so the total can exceed `int.MaxValue` and must accumulate in a '
            '`long`.',
        ],
        assume=[
            ['Half-open `[start, end)`; length is `end - start`.',
             'Under the closed convention every length is one larger and the merge condition needs a '
             '+1. **This is the assumption to state first** — the statement asks about adjacent '
             'intervals precisely because of it.'],
            ['`end <= start` is an empty interval and is ignored.',
             'Alternatively throw. Ignoring is friendlier and makes the structure total; either way, say '
             'which, because a test will pass `(7,7)`.'],
            ['No removal in the base problem.',
             'The statement says "removal if relevant". Removal is genuinely harder: it can **split** '
             'one stored interval into two, so the interval count can grow on a remove, which breaks '
             'the amortised argument that makes insertion cheap.'],
            ['Coordinates are arbitrary `int`, not a small bounded range.',
             'This is what rules out a classic array-backed segment tree, which needs a bounded '
             'universe. It is the reason the answer is a sorted set of merged intervals rather than the '
             'structure the statement suggests — and explaining that choice is most of the value '
             'here.'],
        ]),
    examples=[
        ('Sequence', 'add(1,5)', 'covered 4'),
        ('', 'add(10,12)', 'covered 6 — disjoint'),
        ('', 'add(3,11)', 'covered 11 — bridges both into one interval [1,12)'),
        ('', 'add(2,4)', 'covered 11 — fully contained, adds nothing'),
        ('', 'add(1,12)', 'covered 11 — exact duplicate, adds nothing'),
        ('', 'add(12,15)', 'covered 14 — adjacent, so it coalesces under the half-open reading'),
        ('Ignored', 'add(7,7) or add(9,3)', 'covered 14 — empty and reversed'),
    ],
    examples_note='No examples were supplied; these are mine, and they are chosen to hit each of the four '
                  'overlap cases the statement asks about. The implementation is additionally checked '
                  'against a **brute-force bitmap** over 300 random trials of 25 intervals each, '
                  'verifying both the total and that the stored set stays disjoint and sorted — '
                  'which is the only way I would trust merge logic this fiddly.',
    observation=(
        'Read the two constraints together and they tell you the design.\n\n'
        '`getCoveredSize()` is **O(1)**. There is no structure over n intervals that can compute a union '
        'length in constant time on demand, so the answer cannot be computed at query time at all. It has '
        'to be **maintained as a field**, updated on every mutation. That is the first half, and it is '
        'the half people miss because it sounds too simple.\n\n'
        'For the total to be maintainable, the stored intervals must be **disjoint and merged at all '
        'times** — an invariant, not a cleanup step. If overlapping intervals could sit in the '
        'structure, the union length would not be the sum of their lengths and the running total would be '
        'meaningless. So `addInterval` does the merging, and `getCoveredSize` becomes `return _covered;`.\n\n'
        'Now, `addInterval` in O(log n). The new interval merges with its immediate predecessor if that '
        'one reaches it, and swallows every interval starting inside its extended span. Finding the '
        'predecessor is a search, not a scan, which is where the log comes from. Each swallowed interval '
        'is subtracted from the total as it is removed, and the merged result is added once.\n\n'
        'And here is the part worth being precise about: **a single insert can remove many intervals, so '
        'one call is not O(log n)**. It is O(k log n) for k absorbed. But each interval can only ever be '
        'removed once, so across any sequence of m inserts the total removal work is bounded by m — '
        'the cost is **amortised** O(log n). That is the honest statement of the bound, and the adversarial '
        'input that proves the worst case is one line: insert a thousand tiny disjoint intervals, then one '
        'huge one.\n\n'
        'Finally, why not the structure the statement suggests. A classic array-backed **segment tree '
        'needs a bounded coordinate universe** — you size the array to the coordinate range. With '
        'arbitrary `int` coordinates that is four billion slots. The fixes are coordinate compression '
        '(which needs all the intervals up front, and they arrive one at a time) or a dynamic, '
        'lazily-allocated segment tree (which works and is much more code for the same asymptotics). A '
        'sorted set of merged intervals is the right answer here, and being able to say **why** the '
        'suggested structure does not fit is better than using it because it was suggested.'),
    brute=dict(
        how='Keep every interval in a list as given. On `getCoveredSize()`, sort by start, sweep, merge '
            'on the fly and sum.',
        cx='`addInterval` O(1), `getCoveredSize` O(n log n). Space O(n).',
        why_not='It violates the one constraint the question is built on, and it does so in the expensive '
                'direction: queries are usually far more frequent than inserts for a structure like this. '
                'The fix is to move the work from the query to the insert — which is the general '
                'shape of every "maintain an aggregate" problem, and worth naming as such. A middle '
                'option, caching the total and invalidating on insert, is worse than both: it is O(n log '
                'n) on the first query after any insert, so a read-write-read pattern gets the bad case '
                'every time.'),
    optimal=dict(pipeline=[
        ('INPUT', '`AddInterval(int start, int end)`, arriving one at a time'),
        ('TRANSFORMATION', 'The new interval is merged with every interval it touches, producing one '
                           'wider interval'),
        ('DATA STRUCTURE', '`SortedSet<(int Start, int End)>` holding **disjoint, merged** intervals, '
                           'plus a `long _covered` running total'),
        ('ALGORITHM', 'Find the predecessor via `GetViewBetween`; absorb it if it reaches the new start; '
                      'then repeatedly absorb the lowest interval starting inside the span; insert the '
                      'result and adjust the total'),
        ('OUTPUT', '`GetCoveredSize()` returns the field'),
    ],
        why=[
            ['`SortedSet<(int, int)>` rather than `SortedList` or `SortedDictionary`',
             '`SortedList` is array-backed, so insertion is O(n) from the memmove — it looks right '
             'and breaks the bound. `SortedDictionary` is a red-black tree with O(log n) insert but '
             '**no predecessor query**, which is the one operation needed. `SortedSet.GetViewBetween` is '
             'O(log n) and gives both `Min` and `Max` of a range, so it is the only one of the three '
             'that fits. This is a genuinely C#-specific piece of knowledge and worth stating as the '
             'reason.'],
            ['Sorting on the tuple, which orders by `Start` then `End`',
             'Safe **because the intervals are disjoint** — for disjoint intervals, ordering by '
             'start is the same as ordering by end, so the default tuple comparer cannot produce a '
             'wrong order. That is a consequence of the invariant, not a coincidence, and it is why no '
             'custom comparer is needed.'],
            ['A `long _covered` field',
             'The entire reason `getCoveredSize` is O(1). `long` because `int` coordinates can sum past '
             '`int.MaxValue`.'],
            ['Merged intervals as an invariant',
             'Not a tidy-up. The total is only meaningful if the stored intervals are disjoint, so the '
             'invariant is what the O(1) query rests on.'],
        ],
        steps=[
            '`end <= start` → return; nothing to cover.',
            'Set `lo = start`, `hi = end`.',
            'Find the last interval with `Start <= start`. If its `End >= start`, it reaches the new '
            'interval: extend `lo` and `hi` to cover it, and drop it.',
            'Loop: find the lowest interval with `Start` in `[lo, hi]`. If none, stop. Otherwise extend '
            '`hi` to cover it and drop it.',
            'Insert `(lo, hi)` and add its length to the total.',
            '`Drop` both removes from the set **and** subtracts from the total, so the two can never '
            'disagree.',
        ]),
    walk=dict(
        intro='The bridging case, which is the one that exercises everything: `[1,5)` and `[10,12)` are '
              'stored, and `add(3, 11)` arrives and swallows both.',
        headers=['Step', 'lo, hi', 'Set', 'Covered', 'Note'],
        rows=[
            ['start', '3, 11', '[1,5) [10,12)', '4 + 2 = 6', ''],
            ['predecessor of 3', '', '', '', 'last interval with Start ≤ 3 is [1,5)'],
            ['its End 5 ≥ 3', '**1**, 11', '[10,12)', '6 − 4 = **2**', 'absorbed; lo pulled back to 1'],
            ['lowest Start in [1,11]', '', '', '', '[10,12) — 10 is in range'],
            ['absorb it', '1, **12**', '(empty)', '2 − 2 = **0**', 'hi pushed out to 12'],
            ['lowest Start in [1,12]', '', '', '', 'none — stop'],
            ['insert', '1, 12', '[1,12)', '0 + 11 = **11**', '**one interval, covered 11**'],
        ],
        close='The total dipped to 0 mid-operation and came back to 11, which is fine because nothing '
              'observes it between the two. That is worth noticing though: the invariant holds *between* '
              'operations, not *during* one. Under concurrency a reader could see 0, which is why the '
              'thread-safety follow-up is not academic. Note also that the loop re-queries after '
              'extending `hi` — growing the span can bring new intervals into range, and querying '
              'once would miss them.'),
    code=[
        ('The structure', 'Q09_Covered.cs', 'CoveredIntervals'),
    ],
    codewalk=[
        ('`GetViewBetween` is the whole reason this is `SortedSet`',
         '`GetViewBetween((int.MinValue, int.MinValue), (start, int.MaxValue)).Max` is "the last interval '
         'starting at or before `start`" — a predecessor query, in O(log n). `SortedDictionary` '
         'cannot do this at all, and `SortedList` can via `BinarySearch` but then pays O(n) on insert. '
         'The choice of collection is the technical content of this question in C#.'),
        ('Why the absorb loop re-creates the view each iteration',
         'Absorbing an interval can push `hi` further right, which brings intervals into range that were '
         'previously outside it. The view is a **range query**, so it has to be re-taken after `hi` '
         'changes. Taking it once and enumerating would miss the cascade — and would also mutate the '
         'set while enumerating a view of it, which throws.'),
        ('`Drop` does both jobs, deliberately',
         'It removes from the set and subtracts from `_covered` in one place. The invariant "`_covered` '
         'equals the sum of the stored lengths" then cannot drift, because there is exactly one path that '
         'removes an interval. Separate remove and subtract calls would give two places for them to '
         'disagree, and the resulting bug is a silently wrong total with a perfectly correct set.'),
        ('Why the default tuple comparer is safe',
         'Sorting `(Start, End)` compares `End` only when two intervals share a `Start`, which cannot '
         'happen while the set is disjoint. So the comparer never sees the ambiguous case. This follows '
         'from the invariant rather than from luck, and if the invariant were ever broken the ordering '
         'would break too — which is a good argument for the invariant being maintained by one '
         'method rather than by convention.'),
        ('`prev.End >= start`, not `>`',
         'Under the half-open convention, `[1,5)` and `[5,9)` are adjacent with no gap, so they should '
         'merge into `[1,9)`. `>=` merges them; `>` leaves two intervals that happen to touch. Both give '
         'the same **covered total**, but the second lets the interval count grow without bound on '
         'adjacent inserts, which slowly destroys the search performance. The total being right either '
         'way is what makes this bug hard to notice.'),
        ('`long _covered`',
         'Two `int` coordinates can span more than `int.MaxValue`, and summing several such spans '
         'certainly can. `int` would overflow silently to a negative total.'),
        ('`Snapshot()` exists for the tests',
         'It lets the test assert that the stored set really is disjoint and sorted after 300 random '
         'trials, not just that the total is right. A correct total with a corrupt set is a bug waiting '
         'for the next insert, so both are checked.'),
    ],
    cx=dict(rows=[
        ['`GetCoveredSize`', 'O(1)', 'O(1)', 'Returns a field. This is the requirement, met literally.'],
        ['`AddInterval`', 'O(log n) **amortised**', 'O(1)',
         'One predecessor query plus k removals, each O(log n); k is amortised O(1)'],
        ['`AddInterval` worst case', 'O(k log n)', 'O(1)',
         'A single interval spanning k stored intervals absorbs all k'],
        ['space', '—', 'O(n)', 'n is the number of **merged** intervals, which can be far below the '
                                    'number added'],
    ],
        note='**The amortised argument is the answer to the question, not a footnote.** Each interval is '
             'inserted once and removed at most once, so over m inserts the total removal work is O(m log '
             'n) and the per-operation average is O(log n). The worst single call is unbounded in k, and '
             'the adversarial input is trivial: insert [0,1), [2,3), [4,5) … 1,000 times, then insert '
             '[0,2000). That one call removes 1,000 intervals. Stating the bound as strict O(log n) is '
             'wrong; stating it as amortised **and producing the counterexample** is the strongest '
             'available answer, because the statement asked for something that cannot be delivered '
             'literally.'),
    edges=[
        ['Empty structure', '`GetCoveredSize()` returns 0.'],
        ['`end <= start`', 'Ignored. `(7,7)` and `(9,3)` both change nothing.'],
        ['Fully contained interval', 'Absorbed by the predecessor; the total does not change.'],
        ['Exact duplicate', 'Same as contained — no change.'],
        ['Adjacent, `[1,5)` then `[5,9)`', 'Merges to `[1,9)` under the half-open reading. Under the '
                                           'closed reading `[1,5]` and `[6,9]` should also merge, needing '
                                           '`+1` in the condition.'],
        ['Bridging interval', 'Absorbs the predecessor and every interval it reaches, cascading. The '
                              'walkthrough case.'],
        ['Negative coordinates', 'Work. `int.MinValue` sentinels in the view bound mean the predecessor '
                                 'query still finds them.'],
        ['`int.MinValue` / `int.MaxValue` as real coordinates', 'The sentinel bounds collide with genuine '
                                                               'data at the extremes. If those values are '
                                                               'legal, the view bounds need to be '
                                                               '`long`-typed or the comparer needs a '
                                                               'sentinel flag. Worth stating; unlikely to '
                                                               'be tested; wrong to claim it is handled.'],
        ['Total exceeding `int.MaxValue`', 'Accumulated in a `long`.'],
        ['Many adjacent inserts', 'Coalesce, so the interval count stays low and the search stays fast. '
                                  'This is the payoff for using `>=` rather than `>`.'],
    ],
    fups=[
        dict(given=True, q='Support removeInterval. What breaks?',
             thinking='Removal is not the mirror of insertion, and the asymmetry is the whole answer. '
                      'Insertion only ever merges, so the interval count goes down or up by one. '
                      'Removal can **split**.',
             approach='Find every stored interval overlapping the removed range. For each: subtract its '
                      'length from the total, remove it, then re-insert whatever survives — the part '
                      'to the left of the removed range, the part to the right, or both. Removing '
                      '`[4,6)` from `[1,10)` leaves `[1,4)` and `[6,10)`, so **one interval became two**.',
             tradeoff='Two things break. The interval count can now grow on a removal, so the set can be '
                      'larger than the number of inserts — memory is no longer bounded by insert '
                      'count. And the amortised argument for insertion weakens: intervals can be created '
                      'by removals, so "each interval is removed at most once" no longer bounds the work '
                      'by the number of `AddInterval` calls. The bound becomes amortised in the total '
                      'number of **operations** rather than inserts. The O(1) query survives untouched, '
                      'which is the good news. **This is LeetCode 715 Range Module, and it is rated '
                      'Hard** — which is the honest difficulty for the pair.',
             t='O(k log n) for k overlapped, amortised O(log n) per operation', s='O(n), no longer bounded '
                                                                                 'by insert count'),
        dict(given=True, q='Why not the segment tree you were told to use?',
             thinking='The statement suggests a segment tree, and the useful answer explains what about '
                      'the input rules it out, rather than either obeying or ignoring the suggestion.',
             approach='A classic segment tree is an array sized to the **coordinate universe**. With '
                      'arbitrary `int` coordinates that is 2³² leaves, which is not '
                      'allocatable. Two fixes exist. **Coordinate compression** maps the coordinates that '
                      'actually appear onto a small range — but it needs all the intervals up front, '
                      'and here they arrive one at a time, so it does not apply. A **dynamic segment '
                      'tree** allocates nodes lazily as coordinates are touched, which does work: '
                      'O(log C) per operation for coordinate range C, with a covered count maintained at '
                      'the root.\n\n'
                      'A segment tree becomes the better answer when the queries get richer — '
                      '"how much is covered between x and y" rather than "how much in total" — '
                      'because that is a range query the sorted set cannot answer in logarithmic time.',
             tradeoff='The sorted set is far less code, has space proportional to the number of merged '
                      'intervals rather than to the coordinate range, and meets both stated bounds. The '
                      'dynamic segment tree buys range queries and lazy propagation, and costs '
                      'substantially more code and O(log C) with a larger constant. **I would build the '
                      'sorted set and say exactly this** — including that I would switch if range '
                      'queries were added.',
             t='O(log C) per operation for a dynamic segment tree', s='O(operations · log C) nodes'),
        dict(given=True, q='What about the coordinate range, and negative coordinates?',
             thinking='One of the assumptions the statement explicitly lists, and it is the one that '
                      'decides the structure.',
             approach='The sorted set is agnostic: coordinates are only ever compared, never used as '
                      'indices, so negatives and the full `int` range work with no special handling. The '
                      'one genuine wrinkle is that `int.MinValue` and `int.MaxValue` are used as '
                      'sentinels in the `GetViewBetween` bounds, so if those exact values can be real '
                      'coordinates the bounds need widening to `long` or the comparer needs a sentinel '
                      'flag.',
             tradeoff='This agnosticism is precisely the advantage over the array-backed segment tree, '
                      'whose size is the coordinate range. It is the strongest argument for the choice '
                      'and it follows directly from an assumption the statement asked about — so it '
                      'is worth connecting the two out loud.',
             t='unchanged', s='O(n) in intervals, independent of the coordinate range'),
        dict(q='Make it thread-safe.',
             thinking='The walkthrough already showed the exposure: the total dipped to 0 in the middle '
                      'of one insert. Between operations the invariant holds; during one it does not.',
             approach='A `ReaderWriterLockSlim` fits the access pattern: `GetCoveredSize` is a read and '
                      '`AddInterval` is a write, and reads are expected to dominate. Reads are then '
                      'concurrent and writes are exclusive.\n\n'
                      'There is a cheaper option specifically because the query is a single field: '
                      'compute the new total into a local during the insert and publish it **once** with '
                      'a single `Volatile.Write`, so a reader taking no lock at all sees either the old '
                      'value or the new one and never an intermediate. That makes `GetCoveredSize` truly '
                      'lock-free.',
             tradeoff='`ReaderWriterLockSlim` is simple and obviously correct, and it has real acquisition '
                      'cost on a read-heavy path. The single-publish trick makes reads free and requires '
                      'care that no intermediate value is ever written to the field — which means '
                      'restructuring `Drop` so it accumulates into a local rather than mutating the field '
                      'as it goes. I would start with the lock and only do the second if the read path '
                      'were measured as hot.',
             t='O(1) read, O(log n) amortised write, plus synchronisation',
             s='unchanged'),
        dict(q='Also answer "is point p covered?" and "how much is covered in [x, y)?"',
             thinking='The first is easy and the second is the question that changes the structure, which '
                      'is worth separating.',
             approach='**Is p covered** is O(log n) on the existing set: find the predecessor of p and '
                      'test whether its end passes p. Nothing else needed.\n\n'
                      '**How much is covered in [x, y)** cannot be done in logarithmic time by this '
                      'structure — it needs the sum of clipped lengths over a range, which is O(k) '
                      'in the intervals inside it. To get O(log n) you need an order-statistic tree '
                      'augmented with subtree length sums, or the dynamic segment tree from the earlier '
                      'follow-up, where the sum is already maintained per node.',
             tradeoff='**This is the requirement that would make me switch structures**, and that is the '
                      'point worth making: the sorted set is the right answer to the question as asked, '
                      'and the wrong answer to a slightly richer one. Naming the condition under which '
                      'you would change your mind is more useful than defending the first choice.',
             t='O(log n) for point cover; O(k) or O(log n) for a range sum depending on the structure',
             s='O(n)'),
    ],
    testing=dict(skills=[
        '**Reading a constraint as a design instruction** — O(1) query means "maintain, do not '
        'compute", and that is the entire first move.',
        '**Invariant thinking** — disjoint and merged at all times, maintained in one place.',
        '**Amortised analysis** — and the integrity to say the stated bound is not achievable as a '
        'worst case, with the counterexample.',
        '**Knowing the standard library properly** — why `SortedSet` and not `SortedList` or '
        '`SortedDictionary`. This is C#-specific and it is the difference between O(log n) and O(n).',
        '**Convention discipline** — half-open versus closed, which the statement asks about '
        'directly.',
        '**Knowing when the suggested tool is wrong** — and being able to say what about the input '
        'rules the segment tree out.',
    ],
        senior='Keeps a sorted structure of merged intervals, maintains a running total, and gets the '
               'merge cases right including adjacency and containment.',
        staff='Does that, and: states the half-open convention before writing anything, because it '
              'changes the merge condition; says the O(log n) insert is **amortised** and produces the '
              'adversarial input; explains why `SortedSet.GetViewBetween` is the only one of the three '
              'sorted collections that fits, and what is wrong with the other two; explains why a '
              'classic segment tree does not fit unbounded coordinates and what the dynamic version '
              'would buy; notes that removal can split an interval and therefore weakens the amortised '
              'bound; and names the range-sum query as the requirement that would make them change '
              'structure. Pushing back on the stated complexity — politely, with the '
              'counterexample — is the single strongest move available on this question.'),
    say=[
        "First, a convention question, because it changes the code: are the intervals closed or half-open? "
        "I will assume half-open, so length is end minus start, and [1,5) and [5,9) merge because there is "
        "no gap between them. Under the closed reading every length is one larger and the merge condition "
        "needs a plus one.",
        "Now the constraints, because they tell me the design. getCoveredSize has to be O(1). There is no "
        "structure that can compute a union length in constant time on demand, so I cannot compute it at "
        "query time — I have to maintain it as a field.",
        "For that field to be meaningful, the intervals I store have to be disjoint and merged at all "
        "times. That is an invariant, not a cleanup pass. So addInterval does the merging and "
        "getCoveredSize just returns the number.",
        "For the insert: the new interval merges with its predecessor if that one reaches it, then it "
        "swallows every interval starting inside its extended span, cascading as the span grows. Every "
        "removal subtracts from the total and the final merged interval adds back once.",
        "I want to be straight about the complexity, though. A single insert can absorb an unbounded "
        "number of intervals — add a thousand tiny disjoint ones, then add one that spans them all, and "
        "that call removes a thousand. So the O(log n) you asked for is amortised, not worst case. It "
        "holds because each interval can only ever be removed once, so over m inserts the total removal "
        "work is bounded by m.",
        "On the structure: in C# I would use SortedSet of a start-end tuple, specifically for "
        "GetViewBetween, which gives me the predecessor in O(log n). SortedList would be O(n) on insert "
        "because it is array-backed, and SortedDictionary has no predecessor query at all. So it is the "
        "only one of the three that actually fits.",
        "You suggested a segment tree, and I want to say why I am not using one. A classic segment tree is "
        "sized to the coordinate universe, and with arbitrary int coordinates that is four billion slots. "
        "Coordinate compression would fix it but needs all the intervals up front, and here they arrive "
        "one at a time. A dynamic, lazily-allocated segment tree would work and is much more code for the "
        "same asymptotics.",
        "Where I would change my mind: if you wanted to ask how much is covered between x and y, rather "
        "than the total, the sorted set cannot do that in log time and the segment tree can. So that "
        "requirement would flip the decision.",
        "On removal — that is genuinely harder, because removing from the middle of an interval splits it "
        "into two. So the interval count can grow on a remove, and the amortised argument for insertion "
        "gets weaker, since intervals can now be created by something other than an insert.",
    ],
    video=dict(title='LinkedIn Coding — O(1) Covered Size', mins=18,
               objective='Read the two complexity constraints as the design, then be honest that one of '
                         'them cannot be met literally — and show why that honesty is the answer.',
               beats=[('0:00', 'The question, and its two complexity requirements'),
                      ('1:20', 'Half-open or closed — the convention that changes the code'),
                      ('2:40', 'O(1) query means maintain, not compute'),
                      ('4:10', 'Disjoint and merged as an invariant'),
                      ('5:40', 'The insert: predecessor, then cascade'),
                      ('7:40', 'Walking the bridging case'),
                      ('9:20', 'Why SortedSet and not SortedList or SortedDictionary'),
                      ('11:00', 'The C# implementation'),
                      ('12:40', 'The stated O(log n) is amortised — and the input that proves it'),
                      ('14:20', 'Why the suggested segment tree does not fit'),
                      ('15:40', 'Removal splits intervals, and what that costs'),
                      ('16:50', 'The query that would change the structure'),
                      ('17:40', 'How to say it')]),
))
