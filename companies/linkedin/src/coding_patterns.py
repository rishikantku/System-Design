# -*- coding: utf-8 -*-
"""Pattern library for the coding round. Each entry:
   id, name, prio (p0/p1/p2), topic, concept, recognise, template (C#), example,
   walk, mistakes[], complexity, follow[]"""

PATTERNS = [
 dict(id='hash', name='Hashing and frequency maps', prio='p0', topic='Arrays · Strings · Hashing',
  concept='Trade memory for time: build a map from a value (or a derived key) to whatever you need — count, index, bucket — so the second pass answers in O(1).',
  recognise='"Find pairs / duplicates / anagrams / first unique", anything where a nested loop is scanning for a value you have already seen.',
  template='''// Count, then answer. The derived key is the interesting part.
var freq = new Dictionary<char, int>();
foreach (var c in s) freq[c] = freq.GetValueOrDefault(c) + 1;

// Group by a canonical key (anagrams: sorted letters, or a 26-slot signature)
var groups = new Dictionary<string, List<string>>();
foreach (var w in words) {
    var key = string.Concat(w.OrderBy(c => c));
    if (!groups.TryGetValue(key, out var list)) groups[key] = list = new List<string>();
    list.Add(w);
}''',
  example='Two Sum, Group Anagrams, First Unique Character, Repeated DNA Sequences.',
  walk='For Two Sum you walk once: for each x, ask the map for target-x before inserting x. Asking before inserting is what stops an element pairing with itself.',
  mistakes=['Inserting before querying, so an element matches itself.',
            'Using a `string` key built by concatenation in a hot loop — allocate a 26-int signature instead.',
            'Forgetting that `Dictionary` iteration order is not insertion order in C#.'],
  complexity='O(n) time, O(n) space. Beats sorting (O(n log n)) unless you need order.',
  follow=['What if the input does not fit in memory?', 'What if keys are unbounded — can you bound memory with a sketch?',
          'Make it thread-safe: `ConcurrentDictionary` with `AddOrUpdate`, and know why the update delegate can run twice.']),

 dict(id='twoptr', name='Two pointers', prio='p0', topic='Arrays · Strings',
  concept='Two indices moving under an invariant — from both ends when the data is sorted or symmetric, or same-direction to keep a read/write split.',
  recognise='Sorted array, palindrome, "remove in place", "pair summing to X", merging two ordered sequences.',
  template='''// Opposite ends: shrink toward the middle while an invariant holds.
int l = 0, r = s.Length - 1;
while (l < r) {
    if (s[l] != s[r]) return false;   // or: move the pointer that can improve the answer
    l++; r--;
}

// Same direction: write index lags read index (stable in-place filter).
int w = 0;
for (int rd = 0; rd < a.Length; rd++)
    if (Keep(a[rd])) a[w++] = a[rd];
return w;''',
  example='Valid Palindrome II (one deletion allowed), 3Sum, Remove Duplicates, Merge Sorted Array (fill from the back).',
  walk='Valid Palindrome II: walk inward while characters match; on the first mismatch the answer is "is s[l+1..r] a palindrome, or s[l..r-1]?" — one branch each, so still O(n).',
  mistakes=['Moving both pointers on a mismatch and losing a candidate.',
            'Merging forwards into an array that still holds the data you are reading — fill from the back.',
            'Forgetting duplicate skipping in 3Sum, which produces repeated triples.'],
  complexity='O(n) time, O(1) extra space — the reason interviewers like it as the follow-up to a hash-map answer.',
  follow=['Generalise "one deletion" to k deletions (DP, O(nk)).', 'Return the deleted index, not just a boolean.',
          'What changes for Unicode — surrogate pairs break naive indexing.']),

 dict(id='window', name='Sliding window', prio='p0', topic='Arrays · Strings',
  concept='A window [l,r] with a running summary. Expand right always; contract left while the window is invalid (or while it stays valid, for maximisation).',
  recognise='"Longest / shortest / count of substrings or subarrays satisfying …", contiguous by definition, constraints about at most K of something.',
  template='''// Variable window: shortest window covering all of t (Minimum Window Substring).
var need = new Dictionary<char,int>();
foreach (var c in t) need[c] = need.GetValueOrDefault(c) + 1;
int missing = t.Length, bestL = 0, bestLen = int.MaxValue, l = 0;

for (int r = 0; r < s.Length; r++) {
    if (need.TryGetValue(s[r], out var cnt)) {
        if (cnt > 0) missing--;          // only a needed copy reduces `missing`
        need[s[r]] = cnt - 1;            // may go negative: surplus
    }
    while (missing == 0) {               // valid — try to shrink
        if (r - l + 1 < bestLen) { bestLen = r - l + 1; bestL = l; }
        if (need.TryGetValue(s[l], out var lc)) {
            need[s[l]] = lc + 1;
            if (lc + 1 > 0) missing++;    // we just broke validity
        }
        l++;
    }
}
return bestLen == int.MaxValue ? "" : s.Substring(bestL, bestLen);''',
  example='Minimum Window Substring, Longest Substring Without Repeating Characters, Max Consecutive Ones III, Longest Repeating Character Replacement.',
  walk='The counter can go negative on purpose: negative means surplus copies, so adding one back only breaks validity when it crosses zero. That single test replaces a rescan.',
  mistakes=['Recomputing the window summary from scratch inside the loop (turns O(n) into O(n²)).',
            'Shrinking with `if` instead of `while`.',
            'Tracking "characters matched" instead of "needed copies still missing" — the surplus case then breaks.'],
  complexity='O(n) time (each index enters and leaves once), O(alphabet) space.',
  follow=['Stream the input — you no longer have random access to s[l]; keep a deque of positions.',
          'At most K distinct characters instead of a full cover.', 'Return all minimal windows, not one.']),

 dict(id='bsearch', name='Binary search — including on the answer', prio='p0', topic='Binary search',
  concept='Halve a monotone space. The space is often not the array but the answer: "is a capacity of X enough?" is monotone even when the input is not sorted.',
  recognise='Sorted or rotated array; "minimum X such that …"; "maximise the smallest …"; anything where checking a candidate is cheap and monotone.',
  template='''// Lower bound: first index where pred is true. Keep the invariant in a comment.
int lo = 0, hi = a.Length;              // [lo, hi) is the undecided range
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;       // no overflow
    if (pred(a[mid])) hi = mid;         // answer is mid or left
    else lo = mid + 1;
}
return lo;

// Binary search on the answer.
long lo2 = 1, hi2 = maxPossible;
while (lo2 < hi2) {
    long mid = lo2 + (hi2 - lo2) / 2;
    if (Feasible(mid)) hi2 = mid; else lo2 = mid + 1;
}
return lo2;''',
  example='Search in Rotated Sorted Array I/II, Koko Eating Bananas, Split Array Largest Sum, Find First and Last Position.',
  walk='Rotated with duplicates: when a[lo]==a[mid]==a[hi] you cannot tell which half is sorted, so you shrink by one and the worst case degrades to O(n). Say that out loud — it is the point of the II variant.',
  mistakes=['`(lo+hi)/2` overflow in languages with fixed ints; use `lo + (hi-lo)/2` by habit.',
            'Mixing inclusive and exclusive bounds mid-solution — pick `[lo,hi)` and stay there.',
            'Claiming O(log n) for the duplicate variant.'],
  complexity='O(log n), or O(log(range) × cost of the feasibility check) when searching the answer.',
  follow=['Prove termination and that you return the first true, not any true.',
          'What if the array is distributed across machines?', 'Find the rotation point in the same pass.']),

 dict(id='stack', name='Stacks, monotonic stacks and parsing', prio='p0', topic='Stack · Queue',
  concept='A stack remembers "what is still open". A monotonic stack keeps candidates that can still be the answer for something to their right.',
  recognise='Matching brackets, nested expressions, "next greater element", histogram / rectangle, undo semantics, "peekMax".',
  template='''// Monotonic decreasing stack: next greater element to the right.
var res = new int[a.Length];
Array.Fill(res, -1);
var st = new Stack<int>();               // holds indices, values decreasing
for (int i = 0; i < a.Length; i++) {
    while (st.Count > 0 && a[st.Peek()] < a[i]) res[st.Pop()] = a[i];
    st.Push(i);
}

// Parsing with a stack of contexts (nested lists, expressions)
var stack = new Stack<List<int>>();''',
  example='Valid Parentheses (multi-character tokens), Max Stack, Daily Temperatures, Basic Calculator, Decode String.',
  walk='Max Stack: two stacks give O(1) peekMax but O(n) popMax. For O(log n) popMax use a `SortedSet<(int val,int seq)>` plus a doubly linked list of nodes, so removal from the middle is O(log n) with no rescan.',
  mistakes=['Popping without checking `Count > 0`.',
            'Storing values instead of indices when you later need distances.',
            'For Max Stack, forgetting that duplicates need a tiebreaker (sequence number) or the set collapses them.'],
  complexity='Each element is pushed and popped at most once: O(n) total, O(n) space.',
  follow=['Make popMax O(log n).', 'Support undo of the last k operations.', 'Thread-safe stack: `ConcurrentStack` vs a lock, and why peekMax cannot be lock-free for free.']),

 dict(id='list', name='Linked lists', prio='p1', topic='Linked list',
  concept='Pointer surgery with a dummy head, plus fast/slow traversal for midpoints and cycles.',
  recognise='"Reverse", "reorder", "detect a cycle", "merge k lists", or any O(1)-removal requirement inside a design problem (LRU).',
  template='''// Dummy head removes every "is it the first node?" branch.
var dummy = new ListNode(0) { next = head };
var prev = dummy;
while (prev.next != null) {
    if (Drop(prev.next)) prev.next = prev.next.next;
    else prev = prev.next;
}
return dummy.next;

// Doubly linked node used by LRU-style caches
class Node { public int key, val; public Node prev, next; }
void Remove(Node n) { n.prev.next = n.next; n.next.prev = n.prev; }
void AddFront(Node n) { n.next = head.next; n.prev = head; head.next.prev = n; head.next = n; }''',
  example='Reverse Linked List, Linked List Cycle II, Merge k Sorted Lists, and the list inside LRU/LFU.',
  walk='Use sentinel head and tail nodes in cache problems: every insert and remove then has no null checks, which is the difference between 15 clean lines and 40 buggy ones under time pressure.',
  mistakes=['Losing the rest of the list by reassigning `next` before saving it.',
            'Forgetting to update `prev` in a doubly linked list.', 'No sentinels, then drowning in null checks.'],
  complexity='O(n) time, O(1) space for in-place work.',
  follow=['Reverse in groups of k.', 'Make the list thread-safe for concurrent readers.', 'Why is a linked list a bad fit for CPU caches?']),

 dict(id='treedfs', name='Tree DFS — post-order accumulation', prio='p0', topic='Trees',
  concept='Return a summary from each subtree and combine it in the parent. Most "hard" tree questions are just: decide what each call returns.',
  recognise='Anything asking for height, path sums, "leaves by layer", diameter, or a property of every subtree.',
  template='''// Return the height from the bottom; use it as an index (Find Leaves).
IList<IList<int>> FindLeaves(TreeNode root) {
    var res = new List<IList<int>>();
    Height(root, res);
    return res;
}
int Height(TreeNode n, List<IList<int>> res) {
    if (n == null) return -1;
    int h = 1 + Math.Max(Height(n.left, res), Height(n.right, res));
    if (res.Count == h) res.Add(new List<int>());
    res[h].Add(n.val);                 // node belongs to its height layer
    return h;
}''',
  example='Find Leaves of Binary Tree, Diameter, Balanced Binary Tree, Binary Tree Maximum Path Sum.',
  walk='Notice the trick: you never delete leaves. Height-from-bottom is exactly the round in which a node would be stripped, so one post-order pass replaces repeated pruning.',
  mistakes=['Returning the answer instead of the local summary, then needing globals.',
            'Off-by-one between "height of null = -1" and "= 0" — state your convention.',
            'Deep recursion on a skewed tree: 10⁵ nodes will stack-overflow; mention an explicit stack.'],
  complexity='O(n) time, O(h) stack — O(n) in the worst case.',
  follow=['Iterative version with an explicit stack.', 'What if the tree is stored across machines?',
          'Can you do it without recursion and without extra space (Morris traversal)?']),

 dict(id='treebfs', name='Tree and grid BFS — level order', prio='p0', topic='Trees · Graphs',
  concept='Process by distance. A queue plus a per-level size gives you "layers", which is what most "minimum steps" questions want.',
  recognise='"Level order", "minimum number of moves", "nearest", shortest path on an unweighted graph or grid.',
  template='''var q = new Queue<TreeNode>();
if (root != null) q.Enqueue(root);
while (q.Count > 0) {
    int size = q.Count;                 // freeze the level boundary
    var level = new List<int>(size);
    for (int i = 0; i < size; i++) {
        var n = q.Dequeue();
        level.Add(n.val);
        if (n.left != null) q.Enqueue(n.left);
        if (n.right != null) q.Enqueue(n.right);
    }
    res.Add(level);
}''',
  example='Binary Tree Level Order, Nested List Weight Sum II, Rotting Oranges, Word Ladder, shortest path in a maze.',
  walk='Nested List Weight Sum II wants the *inverse* depth. Either collect level sums and weight them at the end, or use the running-total trick: add the running sum to the answer at every level, which accumulates shallow levels more times.',
  mistakes=['Not freezing `size`, so the loop consumes nodes the next level enqueued.',
            'Marking visited on dequeue instead of enqueue in graph BFS — the queue then holds duplicates.',
            'Using BFS on a weighted graph and calling it shortest path.'],
  complexity='O(n) time, O(width) space.',
  follow=['Bidirectional BFS to halve the frontier.', 'Multi-source BFS (start with every rotten orange).',
          'What if the graph does not fit in memory?']),

 dict(id='graph', name='Graph traversal, cycles and components', prio='p0', topic='Graphs · BFS · DFS',
  concept='Adjacency plus a visited set. The interesting variations are implicit graphs (the nodes are strings, states, builds) and three-colour cycle detection.',
  recognise='Dependencies, connectivity, "can you reach", "is there a cycle", word transformations, state search.',
  template='''// Three-colour DFS: detects a cycle and yields a topological order for free.
const int White = 0, Grey = 1, Black = 2;
var colour = new Dictionary<string,int>();
var order = new List<string>();

bool HasCycle(string u) {
    colour[u] = Grey;
    foreach (var v in Adj(u)) {
        var c = colour.GetValueOrDefault(v, White);
        if (c == Grey) return true;                 // back edge = cycle
        if (c == White && HasCycle(v)) return true;
    }
    colour[u] = Black;
    order.Add(u);                                   // post-order => reverse is topo order
    return false;
}''',
  example='Course Schedule I/II, Word Ladder, Number of Islands, Clone Graph, build-order questions.',
  walk='For implicit graphs, build neighbours lazily. Word Ladder\'s trick is the wildcard bucket: map `h*t` → [hot, hat], so you never compare all pairs of words.',
  mistakes=['Recomputing neighbours inside the loop instead of precomputing buckets.',
            'Visited marked too late (on dequeue) in BFS.',
            'Conflating "grey" (in the current path) with "black" (finished) — only grey means a cycle.'],
  complexity='O(V + E). For Word Ladder with L-letter words: O(N·L²) to build buckets.',
  follow=['Return the cycle itself, not just a boolean.', 'Bidirectional BFS.', 'Parallelise across components.']),

 dict(id='topo', name='Topological sort and dependency ordering', prio='p0', topic='Graphs · Topological sort',
  concept="Kahn's algorithm: repeatedly take nodes with in-degree zero. What remains when the queue empties is a cycle.",
  recognise='Build orders, task scheduling, course prerequisites, migration ordering, anything phrased "X must come before Y".',
  template='''List<string> GetBuildOrder(IEnumerable<string> targets) {
    var indeg = new Dictionary<string,int>();
    var adj   = new Dictionary<string,List<string>>();
    foreach (var t in AllNodes(targets)) {
        indeg.TryAdd(t, 0);
        foreach (var dep in GetDependencies(t)) {          // dep -> t
            adj.TryAdd(dep, new List<string>());
            adj[dep].Add(t);
            indeg[t] = indeg.GetValueOrDefault(t) + 1;
        }
    }
    var q = new Queue<string>(indeg.Where(kv => kv.Value == 0).Select(kv => kv.Key));
    var order = new List<string>();
    while (q.Count > 0) {
        var u = q.Dequeue();
        order.Add(u);
        foreach (var v in adj.GetValueOrDefault(u, new List<string>()))
            if (--indeg[v] == 0) q.Enqueue(v);
    }
    if (order.Count != indeg.Count)
        throw new InvalidOperationException("cycle: " + string.Join(",", indeg.Where(kv => kv.Value > 0).Select(kv => kv.Key)));
    return order;
}''',
  example='getBuildOrder (reported at LinkedIn, Sep 2025), Course Schedule II, Alien Dictionary, parallel task waves.',
  walk='Two upgrades interviewers reach for: name the cycle members rather than returning false, and emit *waves* — every node currently at in-degree zero forms one parallel batch, which is exactly how a migration is sequenced.',
  mistakes=['Counting in-degree on the wrong direction of the edge.',
            'Not detecting the cycle at all (silently returning a short list).',
            'Using recursion for very deep chains.'],
  complexity='O(V + E) time and space.',
  follow=['Emit parallel waves instead of a linear order.', 'Incremental rebuild when one dependency changes.',
          'Deterministic order for reproducible builds — use a priority queue instead of a plain queue.']),

 dict(id='uf', name='Union-Find (disjoint set union)', prio='p1', topic='Union Find',
  concept='Near-constant-time "are these in the same group?" with path compression and union by size.',
  recognise='Merging groups, connectivity queries, "number of components", Kruskal, account merging, dynamic islands.',
  template='''class Dsu {
    private readonly int[] p, size;
    public int Components { get; private set; }
    public Dsu(int n) { p = new int[n]; size = new int[n]; Components = n;
        for (int i = 0; i < n; i++) { p[i] = i; size[i] = 1; } }
    public int Find(int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; }  // halving
    public bool Union(int a, int b) {
        int ra = Find(a), rb = Find(b);
        if (ra == rb) return false;
        if (size[ra] < size[rb]) (ra, rb) = (rb, ra);
        p[rb] = ra; size[ra] += size[rb]; Components--;
        return true;
    }
}''',
  example='Number of Provinces, Accounts Merge, Redundant Connection, Number of Islands II.',
  walk='Union-Find beats BFS when edges arrive over time: you cannot re-run a traversal per query, but you can union in almost O(1) and answer connectivity instantly.',
  mistakes=['No union by size/rank → O(n) finds.', 'Recursive Find on 10⁶ nodes.',
            'Trying to *remove* edges — DSU cannot split; that needs a different structure.'],
  complexity='O(α(n)) amortised per operation — effectively constant.',
  follow=['Support rollback (union by size with an undo stack).', 'Weighted DSU for ratio queries.',
          'Distributed connected components — what changes?']),

 dict(id='heap', name='Heaps and top-K', prio='p0', topic='Heap · Priority Queue',
  concept='Keep only what can still matter: a size-K heap for top-K, or a heap of cursors for merging ordered streams.',
  recognise='"Top K", "k-th largest", "merge k sorted", "median of a stream", scheduling by next-event time.',
  template='''// Top-K largest with a size-K MIN heap (C# PriorityQueue is a min-heap).
var heap = new PriorityQueue<int,int>();
foreach (var x in nums) {
    heap.Enqueue(x, x);
    if (heap.Count > k) heap.Dequeue();      // drop the smallest
}
return heap.Peek();                          // k-th largest

// Merge k sorted lists: heap of (value, listIndex, nodeRef)
var pq = new PriorityQueue<ListNode,int>();
foreach (var head in lists) if (head != null) pq.Enqueue(head, head.val);
while (pq.Count > 0) {
    var n = pq.Dequeue();
    tail = tail.next = n;
    if (n.next != null) pq.Enqueue(n.next, n.next.val);
}''',
  example='Kth Largest Element, Merge k Sorted Lists, Top K Frequent Elements, Find Median from Data Stream (two heaps).',
  walk='Two-heap median is the pattern worth rehearsing: a max-heap of the low half and a min-heap of the high half, rebalanced so sizes differ by at most one.',
  mistakes=['Heapifying everything (O(n log n)) when a size-K heap (O(n log k)) or Quickselect (O(n) average) is wanted.',
            'Forgetting C#\'s `PriorityQueue` is a min-heap and has no decrease-key.',
            'Comparing by the wrong field in the priority tuple.'],
  complexity='Top-K: O(n log k). Merge k lists of total n: O(n log k).',
  follow=['Do it in O(n) average with Quickselect, and say why you would not in production (worst case).',
          'Stream that never ends — bounded memory.', 'Ties: stable ordering with a sequence number.']),

 dict(id='interval', name='Intervals and sweep line', prio='p0', topic='Intervals',
  concept='Sort by start, then either merge with the previous interval or sweep boundary events with a running count.',
  recognise='Meeting rooms, calendars, overlaps, "can all be attended", "maximum concurrent", booking systems.',
  template='''// Merge overlapping intervals.
Array.Sort(iv, (a, b) => a[0].CompareTo(b[0]));
var res = new List<int[]>();
foreach (var cur in iv) {
    if (res.Count > 0 && cur[0] <= res[^1][1]) res[^1][1] = Math.Max(res[^1][1], cur[1]);
    else res.Add(new[] { cur[0], cur[1] });
}

// Sweep line: maximum concurrent intervals (min meeting rooms).
var events = iv.SelectMany(x => new[] { (x[0], +1), (x[1], -1) })
               .OrderBy(e => e.Item1).ThenBy(e => e.Item2);   // end before start at a tie
int cur2 = 0, best = 0;
foreach (var (_, delta) in events) { cur2 += delta; best = Math.Max(best, cur2); }''',
  example='Merge Intervals, Insert Interval, Meeting Rooms II, Calendar booking (double/triple booking).',
  walk='At a tie, process the end before the start if touching intervals are allowed to share a boundary. That single ordering rule is the most common bug in this family.',
  mistakes=['Not sorting, or sorting by end when the merge needs start order.',
            'Mutating the input array the caller owns.',
            'Treating [1,2] and [2,3] as overlapping when the problem says they are not.'],
  complexity='O(n log n) for the sort, O(n) after. A balanced tree gives O(log n) per insert for the streaming variant.',
  follow=['Streaming intervals — keep a `SortedSet<Interval>` and merge neighbours on insert.',
          'Query "what overlaps [a,b]" — interval tree or segment tree.', 'Concurrent bookings without a global lock.']),

 dict(id='dp', name='Dynamic programming', prio='p1', topic='Dynamic programming',
  concept='Define the state so the answer at i depends only on smaller states, then decide top-down memo or bottom-up table.',
  recognise='"Number of ways", "min cost", "longest/largest subsequence", choices with overlapping subproblems.',
  template='''// 1-D: state = best answer ending at i (or using first i items).
var dp = new int[n + 1];
for (int i = 1; i <= n; i++)
    dp[i] = Math.Max(dp[i-1], dp[i-2] + val[i-1]);     // house robber shape

// 2-D with rolling rows to cut memory from O(nm) to O(m).
var prev = new int[m + 1];
var cur  = new int[m + 1];
for (int i = 1; i <= n; i++) {
    for (int j = 1; j <= m; j++)
        cur[j] = a[i-1] == b[j-1] ? prev[j-1] + 1 : Math.Max(prev[j], cur[j-1]);
    (prev, cur) = (cur, prev);
}''',
  example='Coin Change, Longest Common Subsequence, Word Break, Edit Distance, House Robber.',
  walk='Say the state out loud before coding: "dp[i][j] = the longest common subsequence of the first i and first j characters". Interviewers score the definition, not the loop.',
  mistakes=['Coding the loop before defining the state and base case.',
            'Wrong iteration direction for 1-D knapsack (reuse vs single use).',
            'Ignoring that a greedy answer exists and is simpler.'],
  complexity='States × transition cost. Say both, and mention the rolling-array memory cut.',
  follow=['Reconstruct the actual sequence, not only its length.', 'Cut memory to one row.',
          'Is there a greedy or O(n log n) alternative (LIS with patience sorting)?']),

 dict(id='backtrack', name='Backtracking', prio='p1', topic='Backtracking',
  concept='Build a candidate incrementally, undo the last choice, and prune branches that cannot succeed.',
  recognise='Permutations, combinations, subsets, board placement, "all solutions", constraint satisfaction.',
  template='''void Backtrack(List<int> path, int start) {
    res.Add(new List<int>(path));            // copy — path keeps mutating
    for (int i = start; i < nums.Length; i++) {
        if (i > start && nums[i] == nums[i-1]) continue;   // skip duplicates (sorted input)
        path.Add(nums[i]);
        Backtrack(path, i + 1);
        path.RemoveAt(path.Count - 1);       // undo
    }
}''',
  example='Subsets II, Permutations, Combination Sum, N-Queens, Word Search.',
  walk='Two rules cover most bugs: copy the path when you record it, and sort first if you need duplicate skipping.',
  mistakes=['Recording a reference to the mutable path.', 'Forgetting the undo step.',
            'No pruning, so an exponential search that was tractable is not.'],
  complexity='Exponential by nature: O(2ⁿ) subsets, O(n!) permutations — state it and discuss pruning.',
  follow=['Return only the count (often DP instead).', 'Prune with a feasibility bound.', 'Iterative bitmask version for subsets.']),

 dict(id='trie', name='Tries', prio='p2', topic='Tries',
  concept='A tree keyed by character, so prefix work is proportional to the query length instead of the dictionary size.',
  recognise='Autocomplete, prefix search, word dictionaries, longest common prefix, wildcard matching.',
  template='''class TrieNode {
    public readonly Dictionary<char, TrieNode> Next = new();
    public bool IsWord;
    public int Freq;                       // for ranked autocomplete
}
void Insert(string w) {
    var n = root;
    foreach (var c in w) {
        if (!n.Next.TryGetValue(c, out var nxt)) n.Next[c] = nxt = new TrieNode();
        n = nxt;
    }
    n.IsWord = true;
}''',
  example='Implement Trie, Word Search II, Design Add and Search Words, typeahead.',
  walk='For autocomplete, store the top-k completions on each node at build time; the query then becomes a walk plus a read, which is exactly the trick behind typeahead systems.',
  mistakes=['A 26-slot array when the alphabet is Unicode.', 'Not marking word ends, so prefixes count as words.',
            'Rebuilding suggestions per keystroke instead of caching them on the node.'],
  complexity='Insert/search O(L). Memory is the cost — mention compressed tries (radix trees).',
  follow=['Rank completions by frequency.', 'Support fuzzy matching (edit distance ≤ 1).',
          'How would you shard a trie across machines? (This is the typeahead design question.)']),

 dict(id='design', name='Designing data structures under interview pressure', prio='p0', topic='Design · LinkedIn favourite',
  concept='Compose two structures so every operation is O(1) or O(log n): a hash map for lookup plus a list/heap/bucket chain for ordering.',
  recognise='"Implement X with O(1) get and put", caches, "getRandom", "All O(1)", rate limiters, "peekMax".',
  template='''// LRU: map key -> node, doubly linked list with sentinels (most recent at front).
public class LruCache {
    private readonly int _cap;
    private readonly Dictionary<int, Node> _map = new();
    private readonly Node _head = new(), _tail = new();       // sentinels

    public LruCache(int capacity) { _cap = capacity; _head.next = _tail; _tail.prev = _head; }

    public int Get(int key) {
        if (!_map.TryGetValue(key, out var n)) return -1;
        Touch(n);
        return n.val;
    }
    public void Put(int key, int val) {
        if (_map.TryGetValue(key, out var n)) { n.val = val; Touch(n); return; }
        if (_map.Count == _cap) { var lru = _tail.prev; Remove(lru); _map.Remove(lru.key); }
        var node = new Node { key = key, val = val };
        _map[key] = node; AddFront(node);
    }
    private void Touch(Node n) { Remove(n); AddFront(n); }
    private static void Remove(Node n) { n.prev.next = n.next; n.next.prev = n.prev; }
    private void AddFront(Node n) { n.next = _head.next; n.prev = _head; _head.next.prev = n; _head.next = n; }
    private class Node { public int key, val; public Node prev, next; }
}''',
  example='LRU Cache, LFU Cache, All O`one, Max Stack, Insert Delete GetRandom O(1), ranked cache.',
  walk='Every one of these is "map + ordering structure". LFU swaps the single list for a map of frequency → list. All O`one is the same bucket chain keyed by count. Learn one shape, get four problems.',
  mistakes=['Updating the map but not the list (or the reverse) on eviction.',
            'No sentinels.', 'Claiming O(1) while scanning a list for the minimum frequency — keep `minFreq` and maintain it.'],
  complexity='O(1) per operation with map + linked list; O(log n) if you need ordering by an arbitrary key.',
  follow=['Make it thread-safe and discuss the contention cost.', 'Add TTL and lazy expiry.',
          'Add a ranking function (the reported LinkedIn AI-round variant).', 'Bound memory by bytes, not entries.']),

 dict(id='conc', name='Concurrency in C# — the LinkedIn follow-up', prio='p0', topic='Concurrency',
  concept='Make the shared state explicit, pick the cheapest correct synchronisation, and be able to name the race you are preventing.',
  recognise='Any interviewer asking "now make it thread-safe", "what happens with 1,000 concurrent callers", "where is the race?".',
  template='''// 1. Coarse lock — correct, simple, contended.
private readonly object _gate = new();
public int Get(int key) { lock (_gate) { /* ... */ } }

// 2. Reader-heavy: allow concurrent reads, exclusive writes.
private readonly ReaderWriterLockSlim _rw = new(LockRecursionPolicy.NoRecursion);
public int Read(int k) { _rw.EnterReadLock(); try { return _map[k]; } finally { _rw.ExitReadLock(); } }
public void Write(int k, int v) { _rw.EnterWriteLock(); try { _map[k] = v; } finally { _rw.ExitWriteLock(); } }

// 3. Lock-free counters and CAS
Interlocked.Increment(ref _hits);
// 4. Concurrent collection — note GetOrAdd's factory may run more than once
private readonly ConcurrentDictionary<string, Lazy<Value>> _cache = new();
var value = _cache.GetOrAdd(key, k => new Lazy<Value>(() => Load(k))).Value;   // Lazy = single load

// 5. Async coordination without blocking threads
private readonly SemaphoreSlim _limit = new(maxConcurrency);
await _limit.WaitAsync(ct);
try { await CallAsync(ct); } finally { _limit.Release(); }''',
  example='Thread-safe LRU, bounded blocking queue, a rate limiter, a connection pool.',
  walk='For a thread-safe LRU say this: the map can be concurrent, but the recency list cannot — every Get mutates it, so reads become writes. Either lock the list, shard the cache by key hash to cut contention, or accept approximate recency (what real caches do).',
  mistakes=['`lock` around an `await` (you cannot; use `SemaphoreSlim`).',
            'Assuming `ConcurrentDictionary` makes a compound read-modify-write atomic — it does not.',
            'Double-checked locking without `volatile`/`Lazy`.',
            'Claiming lock-free without saying what the CAS loop retries.'],
  complexity='Talk in contention, not Big-O: what is the critical section, how long is it held, how many threads want it.',
  follow=['Shard the lock (stripe by hash) — how do you pick the stripe count?',
          'What is the memory model guarantee you are relying on?',
          'Under 1,000 requests per second, which operation becomes the bottleneck first?']),
]
