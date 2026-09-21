# -*- coding: utf-8 -*-
"""Worked problems for the coding practice engine.
Each: id, title, level (warm/med/hard), topic, why (why this one, incl. report provenance),
question, think, approach, edges[], code, complexity, follow[], optimise, evalpts[]"""

PROBLEMS = [
 dict(id='nested2', title='Nested List Weight Sum II', level='med', topic='Trees · BFS',
  why='LinkedIn-tagged classic, still on the company list. The inverse weighting is what separates a rehearsed answer from a real one.',
  question='You are given a nested list of integers. Each integer is either an integer or a list whose elements may also be integers or lists. The weight of an integer is `maxDepth - depth + 1`, where maxDepth is the maximum depth of any integer. Return the sum of each integer multiplied by its weight.',
  think='You do not know maxDepth until you have seen everything. Can you avoid two passes? What accumulates naturally if you add the running sum of every level seen so far, at every level?',
  approach='''**Option A — two passes.** Find maxDepth, then DFS again weighting by `maxDepth - depth + 1`. Simple, obviously correct, O(n) twice.

**Option B — one pass, level running-sum.** BFS level by level. Keep `levelSum` (sum of integers at this level) and `total`. At each level do `levelSum += (values at this level)` and `total += levelSum`. Shallow values get added once per remaining level, which is exactly the inverse weighting.

Option B is the one to reach for, but say Option A out loud first — it shows you can get a correct answer before optimising.''',
  edges=['Empty list → 0.', 'A list that contains only lists (no integers at some level).',
         'Single flat list → every weight is 1.', 'Deep nesting — recursion depth on a pathological input.',
         'Negative integers (the running-sum trick still holds).'],
  code='''// One pass, no maxDepth needed.
public int DepthSumInverse(IList<NestedInteger> nestedList) {
    var queue = new Queue<NestedInteger>(nestedList);
    int levelSum = 0, total = 0;

    while (queue.Count > 0) {
        int size = queue.Count;
        for (int i = 0; i < size; i++) {
            var ni = queue.Dequeue();
            if (ni.IsInteger()) levelSum += ni.GetInteger();
            else foreach (var child in ni.GetList()) queue.Enqueue(child);
        }
        total += levelSum;          // every deeper level adds the shallow sums again
    }
    return total;
}''',
  complexity='O(n) time where n is the number of nested elements; O(w) space for the widest level. The two-pass version is also O(n) but touches every node twice.',
  follow=['Do the original version (weight = depth) — one line changes.',
          'Return both sums in a single traversal.',
          'The input arrives as a stream you can only read once — does your approach still work?',
          'Iterative vs recursive: what breaks at depth 10⁵?'],
  optimise='The running-sum version is already optimal in time. The real optimisation talk is memory: BFS holds a whole level, DFS holds a path. If the structure is wide and shallow, DFS with a depth-indexed array is cheaper; if it is deep and narrow, BFS is.',
  evalpts=['Did you state the two-pass solution before the clever one?',
           'Did you explain *why* the running sum produces inverse weights?',
           'Did you name the space trade-off between BFS and DFS?',
           'Did you test with a value at depth 1 and a value at depth 3 in the same input?']),

 dict(id='findleaves', title='Find Leaves of Binary Tree', level='med', topic='Trees',
  why='LinkedIn-tagged. Tests whether you can find the reframing (height from the bottom) instead of simulating the process.',
  question='Given the root of a binary tree, collect the nodes as if you repeatedly removed all leaves: return a list of lists, where the first list is the leaves, the second is the leaves after removing those, and so on.',
  think='Simulating removal is O(n²) in the worst case. What single value, computed once per node, tells you which round a node is removed in?',
  approach='''A node is removed in round `h`, where `h` is its height measured from the bottom (leaf = 0). So one post-order pass that returns height, and appends the node into `result[h]`, produces every layer in order. No deletion required.''',
  edges=['Null root → empty list.', 'Single node → [[root]].', 'Completely skewed tree → n layers, and recursion depth n.',
         'Duplicate values are fine — you collect values, not identities.'],
  code='''public IList<IList<int>> FindLeaves(TreeNode root) {
    var res = new List<IList<int>>();
    Height(root, res);
    return res;
}

private int Height(TreeNode node, List<IList<int>> res) {
    if (node == null) return -1;                       // convention: null = -1, leaf = 0
    int h = 1 + Math.Max(Height(node.left, res), Height(node.right, res));
    if (res.Count == h) res.Add(new List<int>());      // first node at this height
    res[h].Add(node.val);
    return h;
}''',
  complexity='O(n) time, O(h) stack — O(n) for a skewed tree.',
  follow=['Return the nodes, not the values, so the caller can rebuild the tree.',
          'Do it iteratively (explicit stack) for a 10⁵-deep tree.',
          'What if the tree is a general n-ary tree?'],
  optimise='It is already one pass. The interesting optimisation is memory: if you only need the count of layers, you never materialise the lists — just track max height.',
  evalpts=['Did you reject the simulate-and-delete approach with a complexity argument?',
           'Did you state the height convention before coding?',
           'Did you handle the "first node at this height" list creation cleanly?']),

 dict(id='maxstack', title='Max Stack', level='hard', topic='Stack · Design',
  why='On the LinkedIn tag list and a favourite because the naive answer is easy and the O(log n) upgrade is the real question.',
  question='Design a stack supporting push, pop, top, peekMax and popMax. peekMax returns the maximum element; popMax removes and returns it (the topmost one if duplicated).',
  think='Two stacks give O(1) peekMax. Why does popMax then cost O(n)? What structure lets you remove an arbitrary element cheaply, and how do you break ties by recency?',
  approach='''**Level 1 — two stacks.** A value stack plus a "max so far" stack. push/pop/top/peekMax are O(1); popMax pops into a buffer until the max is found, then pushes back: O(n).

**Level 2 — O(log n) popMax.** A doubly linked list holds the stack order, and a `SortedSet<(int value, int seq)>` holds every live node keyed by (value, sequence). `seq` increases on each push, so the largest (value, seq) is the topmost maximum. popMax takes the set maximum, finds its node, and unlinks it in O(1); the set removal is O(log n).''',
  edges=['popMax on an empty stack → throw, and say so in the signature.',
         'Duplicate maxima — the *topmost* one must be removed, hence the sequence tiebreaker.',
         'popMax removing the current top (the list unlink must still be correct).',
         'Sequence counter overflow on a very long-lived stack (use long).'],
  code='''public class MaxStack {
    private class Node { public int Val; public long Seq; public Node Prev, Next; }

    private readonly Node _head = new(), _tail = new();                 // sentinels
    private readonly SortedSet<(int val, long seq)> _index = new();
    private readonly Dictionary<(int, long), Node> _nodes = new();
    private long _seq;

    public MaxStack() { _head.Next = _tail; _tail.Prev = _head; }

    public void Push(int x) {
        var n = new Node { Val = x, Seq = _seq++ };
        n.Next = _tail; n.Prev = _tail.Prev; _tail.Prev.Next = n; _tail.Prev = n;
        _index.Add((n.Val, n.Seq));
        _nodes[(n.Val, n.Seq)] = n;
    }

    public int Pop() { var n = Last(); Unlink(n); return n.Val; }
    public int Top() => Last().Val;
    public int PeekMax() { Require(); return _index.Max.val; }

    public int PopMax() {
        Require();
        var key = _index.Max;                        // largest value, then largest seq = topmost
        Unlink(_nodes[key]);
        return key.val;
    }

    private Node Last() { Require(); return _tail.Prev; }
    private void Require() { if (_head.Next == _tail) throw new InvalidOperationException("stack is empty"); }
    private void Unlink(Node n) {
        n.Prev.Next = n.Next; n.Next.Prev = n.Prev;
        _index.Remove((n.Val, n.Seq));
        _nodes.Remove((n.Val, n.Seq));
    }
}''',
  complexity='push O(log n), pop O(log n), top O(1), peekMax O(1) (SortedSet.Max is O(log n) in .NET — cache it if the interviewer presses), popMax O(log n). Space O(n) with three structures over the same nodes.',
  follow=['Make peekMax genuinely O(1) by caching the max and refreshing it only on removal of the max.',
          'Thread-safety: which operations conflict, and would you shard or lock?',
          'What if values are 64-bit and memory matters — can you drop the dictionary?'],
  optimise='The dictionary is removable: store the node reference inside the set entry by making the set hold a comparer over nodes. That saves an allocation per push and one hash lookup per popMax.',
  evalpts=['Did you give the two-stack answer first and price it honestly?',
           'Did you explain the duplicate-tiebreak requirement before coding it?',
           'Did you keep the list and the index consistent in one Unlink method?',
           'Did you state the empty-stack contract?']),

 dict(id='allone', title='All O`one Data Structure', level='hard', topic='Design · Linked list',
  why='Reported in a LinkedIn Staff screening (Jul 2025) and it is the same bucket-chain shape as LFU — learn once, answer twice.',
  question='Implement a data structure with Inc(key), Dec(key), GetMaxKey() and GetMinKey(), all in O(1) average time.',
  think='A hash map gives counts but not order. What ordered structure supports O(1) neighbour insertion? What if you keep one node per *count*, holding all keys with that count?',
  approach='''Keep a doubly linked list of buckets, each bucket holding a count and a `HashSet<string>` of keys with that count. A map `key → bucket` finds a key\'s bucket in O(1).

Inc: move the key to the next bucket (creating it right after if missing). Dec: move to the previous bucket, or drop it if the count reaches zero. Buckets that become empty are unlinked. Max is the last bucket, min is the first.''',
  edges=['Dec on a key that does not exist → no-op (state the contract).',
         'Dec taking a count to zero → remove the key entirely.', 'Empty structure → GetMaxKey/GetMinKey return "".',
         'Many keys sharing one count — the bucket set must handle that.'],
  code='''public class AllOne {
    private class Bucket { public int Count; public HashSet<string> Keys = new(); public Bucket Prev, Next; }

    private readonly Bucket _head = new(), _tail = new();       // sentinels: head <-> ... <-> tail
    private readonly Dictionary<string, Bucket> _at = new();

    public AllOne() { _head.Next = _tail; _tail.Prev = _head; }

    public void Inc(string key) {
        if (!_at.TryGetValue(key, out var cur)) {
            var first = _head.Next;
            if (first == _tail || first.Count != 1) first = InsertAfter(_head, 1);
            first.Keys.Add(key); _at[key] = first;
            return;
        }
        var next = cur.Next;
        if (next == _tail || next.Count != cur.Count + 1) next = InsertAfter(cur, cur.Count + 1);
        next.Keys.Add(key); _at[key] = next;
        RemoveFrom(cur, key);
    }

    public void Dec(string key) {
        if (!_at.TryGetValue(key, out var cur)) return;          // contract: unknown key is a no-op
        if (cur.Count == 1) { _at.Remove(key); RemoveFrom(cur, key); return; }
        var prev = cur.Prev;
        if (prev == _head || prev.Count != cur.Count - 1) prev = InsertAfter(cur.Prev, cur.Count - 1);
        prev.Keys.Add(key); _at[key] = prev;
        RemoveFrom(cur, key);
    }

    public string GetMaxKey() => _tail.Prev == _head ? "" : _tail.Prev.Keys.First();
    public string GetMinKey() => _head.Next == _tail ? "" : _head.Next.Keys.First();

    private Bucket InsertAfter(Bucket node, int count) {
        var b = new Bucket { Count = count, Prev = node, Next = node.Next };
        node.Next.Prev = b; node.Next = b;
        return b;
    }
    private void RemoveFrom(Bucket b, string key) {
        b.Keys.Remove(key);
        if (b.Keys.Count == 0) { b.Prev.Next = b.Next; b.Next.Prev = b.Prev; }
    }
}''',
  complexity='O(1) average for every operation — hash set operations are O(1) average, bucket moves are pointer surgery. O(number of distinct keys) space.',
  follow=['Return *all* max keys, not one.', 'Make it thread-safe.',
          'What if counts can jump by k instead of 1? (The neighbour trick breaks — you need an ordered map.)'],
  optimise='`Keys.First()` on a HashSet is O(1) but allocates an enumerator in older runtimes; keep a single representative key per bucket if the interviewer cares about allocations.',
  evalpts=['Did you land on bucket-per-count rather than a heap?',
           'Did you handle empty-bucket unlinking?',
           'Did you state what Dec does for an unknown key?',
           'Could you say in one sentence why this is the same structure as LFU?']),

 dict(id='lru', title='LRU Cache — and then make it thread-safe', level='med', topic='Design · Concurrency',
  why='Reported in the LinkedIn AI-enabled round (Feb 2026) with concurrency and productionisation follow-ups. This is the single highest-value problem on the page.',
  question='Design a cache with `Get(key)` and `Put(key, value)` in O(1), evicting the least recently used entry when capacity is exceeded. Then: make it safe for concurrent callers.',
  think='Which structure gives O(1) lookup, and which gives O(1) reordering? Once you combine them — which operations mutate shared state? Is `Get` a read or a write?',
  approach='''Map + doubly linked list with sentinels: map for lookup, list for recency, most recent at the front. `Get` moves a node to the front. `Put` inserts at the front and evicts from the back.

For thread-safety, the key observation is that `Get` mutates the recency list, so reads are writes. Three options, in increasing sophistication:
1. One lock around both structures — correct, simple, contended.
2. Stripe the cache into N shards by `key.GetHashCode()`; each shard has its own lock. Contention drops by roughly N, and LRU becomes per-shard (acceptable in practice).
3. Approximate recency: a concurrent map plus a timestamp per entry, with eviction done by a background sweep. This is what production caches do — no ordering structure on the hot path at all.''',
  edges=['Capacity 0 or negative — reject in the constructor.',
         'Put on an existing key updates the value *and* the recency.',
         'Eviction must remove from both the map and the list.',
         'Get on a missing key — return a sentinel or use TryGet; say which.',
         'Concurrent: two threads inserting the same key; the eviction racing a Get on the victim node.'],
  code='''public class LruCache<TKey, TValue> {
    private readonly int _capacity;
    private readonly Dictionary<TKey, Node> _map;
    private readonly Node _head = new(), _tail = new();
    private readonly object _gate = new();          // step 2: one lock, honest and simple

    private sealed class Node { public TKey Key; public TValue Val; public Node Prev, Next; }

    public LruCache(int capacity) {
        if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        _capacity = capacity;
        _map = new Dictionary<TKey, Node>(capacity);
        _head.Next = _tail; _tail.Prev = _head;
    }

    public bool TryGet(TKey key, out TValue value) {
        lock (_gate) {
            if (!_map.TryGetValue(key, out var n)) { value = default; return false; }
            MoveToFront(n);
            value = n.Val;
            return true;
        }
    }

    public void Put(TKey key, TValue value) {
        lock (_gate) {
            if (_map.TryGetValue(key, out var existing)) { existing.Val = value; MoveToFront(existing); return; }
            if (_map.Count == _capacity) {
                var victim = _tail.Prev;            // least recently used
                Unlink(victim);
                _map.Remove(victim.Key);
            }
            var node = new Node { Key = key, Val = value };
            _map[key] = node;
            AddFront(node);
        }
    }

    private void MoveToFront(Node n) { Unlink(n); AddFront(n); }
    private static void Unlink(Node n) { n.Prev.Next = n.Next; n.Next.Prev = n.Prev; }
    private void AddFront(Node n) {
        n.Next = _head.Next; n.Prev = _head;
        _head.Next.Prev = n; _head.Next = n;
    }
}''',
  complexity='O(1) per operation, O(capacity) memory. With one lock, throughput is bounded by the critical section — it is short (a few pointer writes), so the lock is usually fine until you are at very high request rates.',
  follow=['Where exactly is the race if you drop the lock? (Two threads unlinking neighbouring nodes corrupt the list.)',
          'Shard it — how do you choose the shard count, and what do you lose? (Global LRU ordering.)',
          'Add TTL — lazy expiry on read, or a sweeper?',
          'Productionise it: hit-rate metric, size in bytes rather than entries, eviction counters, warmup.',
          'How would you test it? (Deterministic eviction order test + a concurrent hammer test asserting invariants.)'],
  optimise='The hot path allocates nothing except on insert. If eviction pressure is high, pool the nodes. If reads dominate massively, move to option 3 (approximate recency) — mention that Caffeine/Guava do exactly this with sampled LRU.',
  evalpts=['Did you write it correctly with sentinels, first try?',
           'Did you say "Get is a write" before being told?',
           'Did you give at least two concurrency designs with their trade-offs?',
           'Did you name what you would measure in production?']),

 dict(id='buildorder', title='getBuildOrder — topological sort with cycle reporting', level='med', topic='Graphs · Topological sort',
  why='Reported first-hand at LinkedIn (Senior SWE Infrastructure, 30 Sep 2025). It is also your Isolated Cloud tiering problem in miniature.',
  question='You are given `IEnumerable<string> GetDependencies(string target)`. Implement `GetBuildOrder(IEnumerable<string> targets)` returning an order in which every target can be built after its dependencies. Report cycles.',
  think='Which direction do the edges point, and which nodes start ready? What does it mean if the output is shorter than the input? Can you group the output into parallel batches?',
  approach='''Kahn: compute in-degrees over the transitive closure of the requested targets (discover nodes lazily through `GetDependencies`), start from in-degree zero, and peel.

Two upgrades worth volunteering: (1) if the emitted count is less than the node count, the remainder is exactly the set of nodes on or after a cycle — report those names rather than a bare exception; (2) emit *waves*: everything at in-degree zero simultaneously is a parallel build batch.''',
  edges=['Duplicate dependencies (A depends on B twice).', 'Self-dependency A → A is a cycle of length one.',
         'Targets not reachable from each other — several components.',
         'Missing target (GetDependencies throws or returns empty) — decide and state.',
         'Very deep chain — do not recurse.'],
  code='''public IReadOnlyList<IReadOnlyList<string>> GetBuildWaves(IEnumerable<string> targets) {
    var adj   = new Dictionary<string, List<string>>();   // dep -> dependents
    var indeg = new Dictionary<string, int>();
    var seen  = new HashSet<string>();
    var stack = new Stack<string>(targets);

    while (stack.Count > 0) {                              // discover the graph lazily
        var t = stack.Pop();
        if (!seen.Add(t)) continue;
        indeg.TryAdd(t, 0);
        foreach (var dep in GetDependencies(t)) {
            if (!adj.TryGetValue(dep, out var list)) adj[dep] = list = new List<string>();
            list.Add(t);
            indeg[t] = indeg.GetValueOrDefault(t) + 1;
            stack.Push(dep);
        }
    }

    var ready = indeg.Where(kv => kv.Value == 0).Select(kv => kv.Key).ToList();
    var waves = new List<IReadOnlyList<string>>();
    int emitted = 0;

    while (ready.Count > 0) {
        waves.Add(ready);                                   // one parallel batch
        emitted += ready.Count;
        var next = new List<string>();
        foreach (var u in ready)
            foreach (var v in adj.GetValueOrDefault(u, new List<string>()))
                if (--indeg[v] == 0) next.Add(v);
        ready = next;
    }

    if (emitted != indeg.Count) {
        var stuck = indeg.Where(kv => kv.Value > 0).Select(kv => kv.Key).OrderBy(x => x);
        throw new InvalidOperationException("Dependency cycle involves: " + string.Join(", ", stuck));
    }
    return waves;
}''',
  complexity='O(V + E) time and space, where V and E cover only the reachable subgraph. Waves add no cost.',
  follow=['Return a flat order instead of waves (flatten, or use a queue).',
          'Make the order deterministic for reproducible builds — sort each wave.',
          'Incremental rebuild: one dependency changed, what is the minimal set to rebuild? (Everything downstream — BFS on the dependents map.)',
          'Cap the parallelism per wave to N workers.'],
  optimise='For repeated queries, cache the built graph and invalidate on change. For very large graphs, avoid materialising `adj` lists by storing edges in one flat array with offsets (CSR layout).',
  evalpts=['Did you get the edge direction right the first time?',
           'Did you report *which* nodes form the cycle?',
           'Did you volunteer parallel waves without being asked?',
           'Did you avoid recursion for deep chains?']),

 dict(id='dna', title='Repeated DNA Sequences — with a rolling hash', level='med', topic='Hashing · Sliding window',
  why='Reported first-hand at LinkedIn (30 Sep 2025), with an interviewer who interrupted often — practise narrating under interruption.',
  question='Given a DNA string over {A, C, G, T}, return every 10-letter sequence that occurs more than once, in ascending order.',
  think='The obvious answer takes every substring of length 10. What does that cost in allocations for a 10⁶-character input? Can you represent a window as an integer and roll it forward in O(1)?',
  approach='''**Level 1:** slide a length-10 window, put each substring in a `HashSet`, add to the result on the second sighting. O(n × 10) time, O(n × 10) memory in substrings.

**Level 2:** encode each base in 2 bits (A=00, C=01, G=10, T=11). A 10-letter window is 20 bits, so it fits in an int. Roll: `hash = ((hash << 2) | code) & mask`. Now each window is an integer key: no substring allocation, and comparisons are O(1).

Return sorted — the question asks for ascending order, and a `SortedSet<string>` or a sort at the end handles it.''',
  edges=['Input shorter than 10 → empty result.', 'A sequence occurring three or more times must appear once in the output.',
         'Characters outside ACGT — reject or ignore; state the contract.',
         'Result order — the question asks ascending; do not rely on hash order.'],
  code='''public IList<string> FindRepeatedDnaSequences(string s) {
    const int K = 10, Mask = (1 << (2 * K)) - 1;
    var result = new SortedSet<string>(StringComparer.Ordinal);
    if (s.Length < K) return result.ToList();

    var code = new int[128];
    code['C'] = 1; code['G'] = 2; code['T'] = 3;          // A stays 0

    var seen = new HashSet<int>();
    int hash = 0;

    for (int i = 0; i < s.Length; i++) {
        hash = ((hash << 2) | code[s[i]]) & Mask;          // roll the 20-bit window
        if (i < K - 1) continue;
        if (!seen.Add(hash)) result.Add(s.Substring(i - K + 1, K));
    }
    return result.ToList();
}''',
  complexity='O(n log r) with the sorted output (r = number of repeats), O(n) if you sort once at the end. Memory O(distinct windows) integers instead of strings — about 4 bytes instead of ~40 per window.',
  follow=['A 3-billion-character genome — what changes? (Streaming, external memory, or a Bloom filter first pass.)',
          'Arbitrary k, not 10 — when does the integer trick stop working? (k > 31 for a 64-bit key with 2-bit codes.)',
          'A general alphabet — Rabin-Karp with a prime modulus, and then you must handle collisions.',
          'Return the positions, not just the sequences.'],
  optimise='Two-pass Bloom filter: first pass marks candidates in a bit set, second pass confirms only the candidates. Cuts memory dramatically on huge inputs at the cost of a second read.',
  evalpts=['Did you give the simple version first and then optimise?',
           'Did you explain the 2-bit encoding clearly enough that someone could implement it?',
           'Did you keep narrating while being interrupted?',
           'Did you respect the required output order?']),

 dict(id='wordladder', title='Word Ladder — bidirectional BFS', level='hard', topic='Graphs · BFS',
  why='Reported in a LinkedIn Staff screening (Jul 2025). The expected upgrade is bidirectional search.',
  question='Given beginWord, endWord and a word list, return the number of words in the shortest transformation sequence where each step changes exactly one letter and every intermediate word is in the list.',
  think='How do you avoid comparing every pair of words? What does the branching factor do to a one-directional BFS, and what does searching from both ends do to it?',
  approach='''Build buckets: for each word, for each position, the pattern `h*t` maps to the words matching it. Neighbours are then a dictionary lookup instead of an O(N·L) scan.

Then BFS. The upgrade is bidirectional BFS: expand the smaller frontier each round and stop when the frontiers meet. If the branching factor is b and the answer depth d, you go from b^d to roughly 2·b^(d/2).''',
  edges=['endWord not in the word list → 0.', 'beginWord equal to endWord → decide and state (usually 1 or 0).',
         'beginWord may or may not be in the list — do not require it.',
         'Duplicate words in the list.', 'Words of different lengths — filter them out.'],
  code='''public int LadderLength(string beginWord, string endWord, IList<string> wordList) {
    var dict = new HashSet<string>(wordList);
    if (!dict.Contains(endWord)) return 0;

    var buckets = new Dictionary<string, List<string>>();
    foreach (var w in dict)
        for (int i = 0; i < w.Length; i++) {
            var key = w[..i] + "*" + w[(i + 1)..];
            if (!buckets.TryGetValue(key, out var list)) buckets[key] = list = new List<string>();
            list.Add(w);
        }

    var front = new HashSet<string> { beginWord };
    var back  = new HashSet<string> { endWord };
    var seen  = new HashSet<string> { beginWord, endWord };
    int steps = 1;

    while (front.Count > 0 && back.Count > 0) {
        if (front.Count > back.Count) (front, back) = (back, front);   // always expand the smaller side
        var next = new HashSet<string>();
        foreach (var w in front)
            for (int i = 0; i < w.Length; i++) {
                var key = w[..i] + "*" + w[(i + 1)..];
                foreach (var nb in buckets.GetValueOrDefault(key, new List<string>())) {
                    if (back.Contains(nb)) return steps + 1;           // frontiers met
                    if (seen.Add(nb)) next.Add(nb);
                }
            }
        front = next;
        steps++;
    }
    return 0;
}''',
  complexity='Building buckets: O(N·L²) time and memory for N words of length L. BFS visits each word once: O(N·L²) worst case. Bidirectional search cuts the explored frontier, not the asymptotic bound.',
  follow=['Return all shortest ladders (Word Ladder II) — keep parent lists and backtrack.',
          'What if the dictionary is 10⁷ words? (Shard the buckets; generate neighbours on the fly.)',
          'Weighted transformations — now it is Dijkstra, not BFS.'],
  optimise='Skip the bucket map entirely when the alphabet is small: generate the 25·L neighbours directly and test membership. That trades L² memory for a bit more CPU and is often faster in practice.',
  evalpts=['Did you avoid the O(N²) pairwise comparison?',
           'Did you explain why bidirectional BFS helps in terms of branching factor?',
           'Did you handle "expand the smaller frontier" rather than alternating blindly?',
           'Did you get the +1 in the answer right and test it on a two-word ladder?']),

 dict(id='minwindow', title='Minimum Window Substring', level='hard', topic='Sliding window',
  why='On the LinkedIn tag list and the hardest of the classic window problems — the one worth having automatic.',
  question='Given strings s and t, return the shortest substring of s containing every character of t including duplicates, or "" if none exists.',
  think='What single integer tells you whether the window is valid? What must happen to that integer when a character leaves the window but you still have spares?',
  approach='Counts map for t, `missing` = t.Length. Expand right: if the character is needed *and still owed* (count > 0), decrement `missing`. Always decrement the stored count, so surplus goes negative. While `missing == 0`, record the window and shrink from the left, incrementing the count back and only incrementing `missing` when it crosses back above zero.',
  edges=['t longer than s → "".', 'Duplicates in t (the classic failure case: "ADOBECODEBANC", "ABC" vs "AABC").',
         'Empty s or t → "".', 'Characters in s that are not in t at all.', 'The whole of s being the answer.'],
  code='''public string MinWindow(string s, string t) {
    if (string.IsNullOrEmpty(s) || string.IsNullOrEmpty(t) || t.Length > s.Length) return "";

    var need = new int[128];
    foreach (var c in t) need[c]++;

    int missing = t.Length, bestLen = int.MaxValue, bestStart = 0, left = 0;

    for (int right = 0; right < s.Length; right++) {
        if (need[s[right]]-- > 0) missing--;             // it was still owed
        while (missing == 0) {                           // valid window: shrink it
            if (right - left + 1 < bestLen) { bestLen = right - left + 1; bestStart = left; }
            if (++need[s[left]] > 0) missing++;          // we gave back a needed copy
            left++;
        }
    }
    return bestLen == int.MaxValue ? "" : s.Substring(bestStart, bestLen);
}''',
  complexity='O(|s| + |t|) time — each index enters and leaves the window once. O(1) space for a fixed alphabet (O(k) for Unicode with a dictionary).',
  follow=['Unicode input — swap the array for a dictionary and discuss surrogate pairs.',
          'Return every minimal window.', 'Stream s — you lose random access to s[left]; keep a queue of positions.',
          'Minimum window *subsequence* (different problem: DP or two-pointer with restart).'],
  optimise='The array-of-128 version avoids dictionary hashing entirely, which is the practical speed-up. For very long s with a short t, you can skip ahead to the next character that appears in t.',
  evalpts=['Did you use a single `missing` counter rather than comparing two maps?',
           'Did you let counts go negative and explain why?',
           'Did you test the duplicate case out loud?',
           'Did you keep the shrink loop as a `while`?']),

 dict(id='rotated2', title='Search in Rotated Sorted Array II (duplicates allowed)', level='med', topic='Binary search',
  why='Reported in a LinkedIn phone screen. The point is the honest complexity answer, not the code.',
  question='Given an array sorted in ascending order and then rotated, possibly containing duplicates, determine whether a target exists.',
  think='In each step you must decide which half is sorted. What input makes that decision impossible, and what do you do then?',
  approach='Binary search where, at each step, you identify the sorted half and test whether the target lies in it. When `a[lo] == a[mid] == a[hi]` you cannot tell — shrink both ends by one. That degradation is the whole reason the II variant exists.',
  edges=['All elements identical ([2,2,2,2,2], target 3) → O(n).', 'Array not actually rotated.',
         'Single element, empty array.', 'Target at the pivot boundary.'],
  code='''public bool Search(int[] nums, int target) {
    int lo = 0, hi = nums.Length - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] == target) return true;

        if (nums[lo] == nums[mid] && nums[mid] == nums[hi]) { lo++; hi--; continue; }   // ambiguous

        if (nums[lo] <= nums[mid]) {                       // left half sorted
            if (nums[lo] <= target && target < nums[mid]) hi = mid - 1; else lo = mid + 1;
        } else {                                           // right half sorted
            if (nums[mid] < target && target <= nums[hi]) lo = mid + 1; else hi = mid - 1;
        }
    }
    return false;
}''',
  complexity='O(log n) average, **O(n) worst case** with many duplicates. Say this before the interviewer asks — it is the point of the question.',
  follow=['Return the index instead of a boolean — which index, if duplicates exist?',
          'Find the rotation point in the same pass.', 'How would you search a rotated array spread over several machines?'],
  optimise='No asymptotic improvement is possible with duplicates: an adversary can hide the target behind identical values. That impossibility argument is a strong thing to say out loud.',
  evalpts=['Did you name the O(n) worst case unprompted?',
           'Did you use `<=` correctly when testing which half is sorted?',
           'Did you test the all-duplicates input?']),

 dict(id='palindrome', title='Valid Palindrome II → k edits', level='med', topic='Two pointers · DP',
  why='A 2026 candidate reported "given a string where you can make certain edits, determine whether it can become a palindrome".',
  question='Given a string, decide whether it can become a palindrome by deleting at most one character. Then generalise: at most k deletions.',
  think='On a mismatch there are exactly two repairs. For k, what subproblem repeats, and what are its parameters?',
  approach='''**One deletion:** two pointers inward; on the first mismatch, test `IsPalindrome(l+1, r)` or `IsPalindrome(l, r-1)`. Still O(n) because only one branch each side is explored.

**k deletions:** this is "is the longest palindromic subsequence at least n-k?", or directly a DP over (l, r, budget). O(n²) states with O(1) transitions, or O(n·k) with the two-pointer recursion plus memo.''',
  edges=['Empty string and single character → true.', 'Already a palindrome → true with zero deletions.',
         'k ≥ n → trivially true.', 'Case sensitivity and non-letters — ask before assuming.'],
  code='''public bool ValidPalindrome(string s) {                 // at most one deletion
    int l = 0, r = s.Length - 1;
    while (l < r) {
        if (s[l] != s[r]) return IsPal(s, l + 1, r) || IsPal(s, l, r - 1);
        l++; r--;
    }
    return true;
}
private static bool IsPal(string s, int l, int r) {
    while (l < r) { if (s[l++] != s[r--]) return false; }
    return true;
}

// Generalised: at most k deletions, memoised on (l, r).
public bool CanBePalindrome(string s, int k) {
    var memo = new Dictionary<(int, int), int>();
    return MinDeletions(s, 0, s.Length - 1, memo) <= k;
}
private static int MinDeletions(string s, int l, int r, Dictionary<(int, int), int> memo) {
    if (l >= r) return 0;
    if (memo.TryGetValue((l, r), out var cached)) return cached;
    int res = s[l] == s[r]
        ? MinDeletions(s, l + 1, r - 1, memo)
        : 1 + Math.Min(MinDeletions(s, l + 1, r, memo), MinDeletions(s, l, r - 1, memo));
    return memo[(l, r)] = res;
}''',
  complexity='One deletion: O(n) time, O(1) space. k deletions: O(n²) time and space with memoisation — mention the O(n) space rolling-row bottom-up version.',
  follow=['Return which characters to delete.', 'Allow replacements as well as deletions.',
          'Streaming input.', 'Why is the greedy "delete the mismatching side with more matches" wrong?'],
  optimise='For k deletions, bottom-up with two rows gives O(n) memory. If k is tiny, the branch-and-bound version with a budget beats the full table.',
  evalpts=['Did you spot that one deletion only needs two candidate checks?',
           'Did you connect the k version to longest palindromic subsequence?',
           'Did you ask about case and punctuation before coding?']),

 dict(id='intervals', title='Interval manager (merge + query) as a class', level='med', topic='Intervals · Design',
  why='The AI-enabled round reportedly asks for a merge-intervals variant "requiring data structure selection" — as a class, not a one-shot function.',
  question='Design a structure supporting `Add(start, end)`, `Remove(start, end)` and `Query(start, end)` over half-open intervals, keeping the set non-overlapping at all times.',
  think='Which structure keeps sorted, non-overlapping intervals and supports predecessor lookup? What does Add have to do with its neighbours?',
  approach='''Keep a `SortedList<int,int>` (start → end) or `SortedSet<Interval>` with a comparer on start. Add: find the first interval whose end ≥ start, absorb every overlapping neighbour into one merged interval, and insert. Remove: split the covering interval into at most two pieces. Query: predecessor lookup, then walk forward while start < queryEnd.''',
  edges=['Touching intervals [1,2) and [2,3) — merge or not? Ask, then be consistent.',
         'Add fully inside an existing interval → no change.', 'Remove covering several intervals.',
         'Remove from the middle → two pieces.', 'Empty structure.'],
  code='''public class IntervalSet {
    private readonly SortedList<int, int> _iv = new();   // start -> end (half-open, non-overlapping)

    public void Add(int start, int end) {
        if (end <= start) return;
        int i = FirstIndexWithEndAtLeast(start);
        while (i < _iv.Count && _iv.Keys[i] <= end) {     // absorb every overlapping neighbour
            start = Math.Min(start, _iv.Keys[i]);
            end   = Math.Max(end,   _iv.Values[i]);
            _iv.RemoveAt(i);
        }
        _iv[start] = end;
    }

    public void Remove(int start, int end) {
        if (end <= start) return;
        int i = FirstIndexWithEndAtLeast(start);
        while (i < _iv.Count && _iv.Keys[i] < end) {
            int s = _iv.Keys[i], e = _iv.Values[i];
            _iv.RemoveAt(i);
            if (s < start) { _iv[s] = Math.Min(e, start); i++; }      // left remainder
            if (e > end)   { _iv[end] = e; i++; }                     // right remainder
        }
    }

    public bool Query(int start, int end) {               // any overlap?
        int i = FirstIndexWithEndAtLeast(start);
        return i < _iv.Count && _iv.Keys[i] < end;
    }

    private int FirstIndexWithEndAtLeast(int start) {
        int lo = 0, hi = _iv.Count;
        while (lo < hi) { int mid = (lo + hi) / 2; if (_iv.Values[mid] <= start) lo = mid + 1; else hi = mid; }
        return lo;
    }
}''',
  complexity='Add/Remove O(log n + k) where k is the number of intervals touched (each is removed once, so amortised small). Query O(log n). `SortedList` insert is O(n) for the array shift — say so, and offer a balanced tree or skip list if writes dominate.',
  follow=['Make it thread-safe for concurrent bookings.', 'Count total covered length in O(1) — maintain a running sum.',
          'Support "find the first free slot of length L".', 'Millions of intervals — segment tree or interval tree.'],
  optimise='If the workload is append-mostly and ordered (log-like), a plain list with a tail check is O(1) per add. Recognising the workload shape is the staff-level move.',
  evalpts=['Did you ask about touching intervals before coding?',
           'Did you handle remove-from-the-middle producing two pieces?',
           'Did you price SortedList inserts honestly?',
           'Did you design it as a class with invariants rather than a function?']),

 dict(id='lca', title='Lowest Common Ancestor — and the k-node variant', level='med', topic='Trees',
  why='On the LinkedIn tag list; the follow-ups (parent pointers, k nodes, repeated queries) are where the round goes.',
  question='Given a binary tree and two nodes, return their lowest common ancestor. Then: with parent pointers but no root. Then: for k nodes.',
  think='What does a recursive call need to return so the parent can decide? What changes when you can walk upwards?',
  approach='''**Plain tree:** return the node itself if it is p or q; otherwise recurse both sides. If both sides return non-null, this node is the LCA; otherwise pass up whichever is non-null.

**With parent pointers:** it becomes "intersection of two linked lists" — walk both to the root collecting depths, advance the deeper one, then move together.

**k nodes:** same recursion, but count how many of the k targets each subtree contains; the deepest node whose subtree count equals k is the answer.''',
  edges=['p or q not present in the tree — the classic version silently returns the other; say so and offer a "found both" flag.',
         'p is an ancestor of q → answer is p.', 'Duplicate values — work on node references, not values.',
         'Skewed tree → recursion depth.'],
  code='''public TreeNode LowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
    if (root == null || root == p || root == q) return root;
    var left  = LowestCommonAncestor(root.left,  p, q);
    var right = LowestCommonAncestor(root.right, p, q);
    if (left != null && right != null) return root;        // p and q split here
    return left ?? right;
}

// k targets, with an explicit "all present" guarantee.
public TreeNode LcaOfMany(TreeNode root, HashSet<TreeNode> targets, out int found) {
    found = 0;
    if (root == null) return null;
    var l = LcaOfMany(root.left,  targets, out int lf);
    var r = LcaOfMany(root.right, targets, out int rf);
    found = lf + rf + (targets.Contains(root) ? 1 : 0);
    if (found == targets.Count) return (l ?? r) is null || (l != null && r != null) || targets.Contains(root)
        ? root : (l ?? r);
    return null;
}''',
  complexity='O(n) time, O(h) space. With parent pointers: O(h) time, O(1) space. For many repeated queries: preprocess with binary lifting, O(n log n) build and O(log n) per query.',
  follow=['No parent pointers and you may not modify the tree — can you still do O(1) space? (Not in general.)',
          'Thousands of queries on a static tree → binary lifting or Euler tour + sparse table.',
          'A BST instead — O(h) with a single descent.'],
  optimise='For repeated queries the preprocessing answer is the one they want: Euler tour plus range-minimum query gives O(1) per LCA after O(n log n) preprocessing.',
  evalpts=['Did you state the assumption that both nodes exist?',
           'Did you offer the parent-pointer and repeated-query variants without prompting?',
           'Did you work on references rather than values?']),

 dict(id='maxones', title='Max Consecutive Ones III', level='warm', topic='Sliding window',
  why='On the LinkedIn tag list; a clean warm-up that drills the "window with a budget" shape.',
  question='Given a binary array and an integer k, return the length of the longest subarray of 1s after flipping at most k zeros.',
  think='What makes a window invalid? What is the cheapest way to restore validity?',
  approach='Expand right, counting zeros. While zeros > k, move left forward, decrementing the count when the element leaving is a zero. The window never shrinks below the best answer, so tracking `right - left + 1` at each step suffices.',
  edges=['k = 0 → longest run of ones.', 'All zeros with k ≥ n → n.', 'Empty array → 0.'],
  code='''public int LongestOnes(int[] nums, int k) {
    int left = 0, zeros = 0, best = 0;
    for (int right = 0; right < nums.Length; right++) {
        if (nums[right] == 0) zeros++;
        while (zeros > k) if (nums[left++] == 0) zeros--;
        best = Math.Max(best, right - left + 1);
    }
    return best;
}''',
  complexity='O(n) time, O(1) space.',
  follow=['Return the actual window, not just its length.', 'Stream the input.',
          'At most k distinct values instead of zeros — the same shape with a counts map.'],
  optimise='The non-shrinking window variant (window only grows) computes the same answer in one pass with no inner loop — a nice micro-optimisation to mention.',
  evalpts=['Did you recognise the window-with-budget shape immediately?',
           'Did you handle k = 0?', 'Did you avoid recomputing the zero count?']),
]

# additional tracked bank (title, level, topic, why)
BANK = [
 ('Two Sum / Group Anagrams / First Unique Character', 'warm', 'Hashing', 'Warm-up trio for the hashing pattern'),
 ('Valid Parentheses with multi-character tokens', 'warm', 'Stack', 'Reported phone-screen variant'),
 ('Merge Sorted Array (in place, from the back)', 'warm', 'Two pointers', 'Classic two-pointer warm-up'),
 ('Binary Tree Level Order Traversal', 'warm', 'Trees', 'Foundation for the BFS pattern'),
 ('Number of Islands', 'warm', 'Graphs', 'Grid DFS/BFS baseline'),
 ('Insert Interval', 'med', 'Intervals', 'Pairs with the interval manager'),
 ('Meeting Rooms II', 'med', 'Intervals', 'Sweep line / min-heap'),
 ('Course Schedule II', 'med', 'Topological sort', 'Second rep for Kahn'),
 ('Clone Graph', 'med', 'Graphs', 'Map old→new while traversing'),
 ('Accounts Merge', 'med', 'Union Find', 'DSU with string keys'),
 ('Top K Frequent Elements', 'med', 'Heap', 'Bucket sort vs heap trade-off'),
 ('Kth Largest Element in an Array', 'med', 'Heap', 'Quickselect vs heap — know both'),
 ('Find Median from Data Stream', 'hard', 'Heap', 'Two-heap balance'),
 ('Merge k Sorted Lists', 'hard', 'Heap · Linked list', 'Heap of cursors'),
 ('Longest Substring Without Repeating Characters', 'med', 'Sliding window', 'Window with last-seen index'),
 ('Longest Repeating Character Replacement', 'med', 'Sliding window', 'Window with a budget'),
 ('Koko Eating Bananas', 'med', 'Binary search', 'Binary search on the answer'),
 ('Split Array Largest Sum', 'hard', 'Binary search', 'Feasibility predicate practice'),
 ('Daily Temperatures', 'med', 'Monotonic stack', 'Next greater element'),
 ('Basic Calculator II', 'med', 'Stack · Parsing', 'Parsing with precedence'),
 ('Decode String', 'med', 'Stack', 'Nested context stack'),
 ('Word Search II', 'hard', 'Trie · Backtracking', 'Trie-pruned DFS'),
 ('Implement Trie + autocomplete ranking', 'med', 'Trie', 'Feeds the typeahead design'),
 ('Coin Change', 'med', 'DP', 'Unbounded knapsack shape'),
 ('Word Break', 'med', 'DP', 'DP over string prefixes'),
 ('Edit Distance', 'hard', 'DP', '2-D table with rolling rows'),
 ('Longest Increasing Subsequence (n log n)', 'med', 'DP · Binary search', 'Patience sorting'),
 ('Subsets II / Permutations II', 'med', 'Backtracking', 'Duplicate skipping'),
 ('N-Queens', 'hard', 'Backtracking', 'Pruning with column/diagonal sets'),
 ('Insert Delete GetRandom O(1)', 'med', 'Design', 'Map + array swap-remove'),
 ('Design Hit Counter / sliding-window rate limiter', 'med', 'Design · Concurrency', 'Bridges to the rate-limiter design'),
 ('Bounded blocking queue (producer/consumer)', 'med', 'Concurrency', 'Monitor / SemaphoreSlim practice in C#'),
 ('Thread-safe LFU with a background sweeper', 'hard', 'Concurrency · Design', 'The production version of the AI-round problem'),
]
