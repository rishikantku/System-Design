# -*- coding: utf-8 -*-
"""LinkedIn-tagged problems supplied by the reader from their own collection of past
LinkedIn questions (first-party signal — higher value than any aggregator).
Same 9-stage schema as coding_problems.PROBLEMS."""

LINKEDIN_PROBLEMS = [
 dict(id='letters', title='Letter Combinations of a Phone Number', level='med', topic='Backtracking · Strings',
  why='On your list, and it sits in LeetCode\'s **LinkedIn six-month** tagged set — the closest thing to a live frequency signal. '
      'Easy to code, and the follow-ups (iterative, streaming, huge input) are where the round actually goes.',
  question='Given a string of digits 2–9, return all possible letter combinations the number could represent, in any order. Map '
           'digits to letters as on a telephone keypad.',
  think='Two shapes solve this: recursion that builds one string and undoes, or an iterative queue that grows level by level. '
        'Which one survives the follow-up "the input has 15 digits and you must not hold them all in memory"?',
  approach='Backtracking: index into the digit string, append each mapped letter, recurse, remove. O(4ⁿ · n) output-bound. '
           'The iterative BFS version builds the cross product level by level and is the natural answer if asked to avoid recursion. '
           'For a lazy version, return an `IEnumerable<string>` and `yield return` at the leaves — that is the answer to the '
           'memory follow-up, and it is the one most candidates do not have ready.',
  edges=['Empty input → empty list, not a list containing "".', 'Digits 0 and 1 map to nothing — reject or ignore, state which.',
         'A single digit.', 'All digits mapping to four letters (7 and 9) — the worst case for output size.',
         'Very long input: the output is exponential, so the interviewer is testing whether you say that out loud.'],
  code='''private static readonly string[] Pad = { "", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz" };

public IList<string> LetterCombinations(string digits) {
    var result = new List<string>();
    if (string.IsNullOrEmpty(digits)) return result;         // "" is not a valid combination
    Build(digits, 0, new StringBuilder(digits.Length), result);
    return result;
}

private static void Build(string digits, int i, StringBuilder path, List<string> result) {
    if (i == digits.Length) { result.Add(path.ToString()); return; }
    var letters = Pad[digits[i] - '0'];
    if (letters.Length == 0) { Build(digits, i + 1, path, result); return; }   // 0 and 1: skip, by stated contract
    foreach (var c in letters) {
        path.Append(c);
        Build(digits, i + 1, path, result);
        path.Length--;                                        // undo
    }
}

// Lazy variant: answers "15 digits, do not materialise 4^15 strings".
public IEnumerable<string> LetterCombinationsLazy(string digits) {
    if (string.IsNullOrEmpty(digits)) yield break;
    var stack = new Stack<(int Index, string Prefix)>();
    stack.Push((0, ""));
    while (stack.Count > 0) {
        var (i, prefix) = stack.Pop();
        if (i == digits.Length) { yield return prefix; continue; }
        foreach (var c in Pad[digits[i] - '0']) stack.Push((i + 1, prefix + c));
    }
}''',
  complexity='O(4ⁿ · n) time and output size for n digits; O(n) auxiliary space for the recursion and the path. Say "output-bound" — '
             'it is the correct framing and it sets up the lazy follow-up.',
  follow=['Do it iteratively.', 'Return them lazily so 15 digits does not blow memory.',
          'Rank the combinations by dictionary likelihood (this is T9 predictive text — a nice LinkedIn-flavoured extension).',
          'Now the keypad mapping is configurable at runtime.'],
  optimise='Preallocate the `StringBuilder` to the digit length; use the stack/lazy version when the caller only needs the first k. '
           'If asked for a dictionary-filtered version, walk a trie alongside the recursion and prune dead prefixes — that turns '
           'an exponential search into something practical.',
  evalpts=['Did you handle empty input correctly (empty list, not [""])?',
           'Did you state the output-bound complexity before coding?',
           'Did you have the lazy or iterative variant ready?',
           'Did you ask what to do with 0 and 1?']),

 dict(id='maze', title='The Maze — rolling ball', level='med', topic='Graphs · BFS · Simulation',
  why='On your list **and** a maze class appeared in a 2026 AI-round report. The twist is that the ball rolls until it hits a '
      'wall, so the graph edges are not the grid cells — getting that wrong is the whole failure mode.',
  question='A ball in a maze of empty spaces and walls can roll up, down, left or right, but it does not stop rolling until it '
           'hits a wall. Given start and destination, decide whether the ball can stop at the destination.',
  think='What are the nodes and edges here? If you BFS over neighbouring cells you are solving a different problem. Where does '
        'the ball actually get a choice?',
  approach='Nodes are **stopping positions**, not cells. From a stopping position, for each of four directions, roll until the '
           'next cell is a wall or out of bounds; the cell before the wall is the neighbour. BFS or DFS over those, marking '
           'visited stopping positions. The destination counts only if the ball *stops* there.',
  edges=['Start equals destination → true (it is already stopped there).',
         'Destination is reachable while rolling through, but the ball cannot stop on it → false. This is the case everyone misses.',
         'A 1×N maze — rolling immediately hits the boundary.',
         'Walls surrounding the start → no moves at all.',
         'Very large maze → iterative BFS, not recursion.'],
  code='''public bool HasPath(int[][] maze, int[] start, int[] destination) {
    int rows = maze.Length, cols = maze[0].Length;
    var visited = new bool[rows, cols];                       // visited STOPPING positions
    int[] dr = { 1, -1, 0, 0 }, dc = { 0, 0, 1, -1 };

    var q = new Queue<(int r, int c)>();
    q.Enqueue((start[0], start[1]));
    visited[start[0], start[1]] = true;

    while (q.Count > 0) {
        var (r, c) = q.Dequeue();
        if (r == destination[0] && c == destination[1]) return true;   // stopped here

        for (int d = 0; d < 4; d++) {
            int nr = r, nc = c;
            // roll until the NEXT cell would be a wall or out of bounds
            while (nr + dr[d] >= 0 && nr + dr[d] < rows &&
                   nc + dc[d] >= 0 && nc + dc[d] < cols &&
                   maze[nr + dr[d]][nc + dc[d]] == 0) {
                nr += dr[d]; nc += dc[d];
            }
            if (!visited[nr, nc]) { visited[nr, nc] = true; q.Enqueue((nr, nc)); }
        }
    }
    return false;
}''',
  complexity='O(R·C·max(R,C)) — each stopping position may roll the length of the maze in each direction. Space O(R·C). Say the '
             'rolling factor out loud; most candidates quote O(R·C) and are wrong.',
  follow=['Maze II: return the shortest distance to stop at the destination (Dijkstra, because edge weights are roll lengths).',
          'Maze III: a hole in the floor, and lexicographically smallest instruction string.',
          'Generate a maze guaranteed to have a path (the 2026 AI-round follow-up).',
          'How do you verify the maze is well formed, including the outer wall?'],
  optimise='For Maze II, a priority queue keyed by distance; the rolling means many cells are visited without being expanded, so a '
           'visited-distance array beats a boolean. If the maze is static and queried repeatedly, precompute the stopping graph once.',
  evalpts=['Did you model stopping positions as the nodes?',
           'Did you catch that the destination must be a stopping point?',
           'Did you give the rolling factor in the complexity?',
           'Did you keep it iterative?']),

 dict(id='rgetrandom', title='Insert Delete GetRandom O(1) — duplicates allowed', level='hard', topic='Design · Hashing',
  why='On your list, and a Taro report (Oct 2025) describes a LinkedIn interviewer asking to "design a random set" with a '
      'follow-up — the duplicates variant is that follow-up.',
  question='Design a structure supporting `Insert(val)`, `Remove(val)` and `GetRandom()` in average O(1), where duplicates are '
           'allowed and `GetRandom` must return each value with probability proportional to its multiplicity.',
  think='The no-duplicates version is a list plus a map of value→index, removing by swapping with the last element. What breaks '
        'when a value can appear many times, and what is the smallest change that fixes it?',
  approach='Keep a `List<int>` of all values (including duplicates) and a `Dictionary<int, HashSet<int>>` from value to the set of '
           'indices where it appears. Remove: take any index of the value, swap the last element into it, fix the moved element\'s '
           'index set, then shrink. The subtle part is the self-swap case — when the element being removed *is* the last one, '
           'fixing the moved element first corrupts the set.',
  edges=['Remove a value that is not present → return false, do not throw.',
         'Remove the last remaining element (the self-swap case) — the classic bug.',
         'GetRandom on an empty structure → decide: throw, or a TryGetRandom pattern.',
         'Many duplicates of one value — probability must stay proportional.',
         'Insert returns whether the value was **already** present (the LeetCode contract) — read it carefully.'],
  code='''public sealed class RandomizedCollection {
    private readonly List<int> _values = new();
    private readonly Dictionary<int, HashSet<int>> _indices = new();
    private readonly Random _rng = new();

    /// <returns>true if the collection did NOT already contain the value.</returns>
    public bool Insert(int val) {
        if (!_indices.TryGetValue(val, out var set)) _indices[val] = set = new HashSet<int>();
        bool wasAbsent = set.Count == 0;
        set.Add(_values.Count);
        _values.Add(val);
        return wasAbsent;
    }

    public bool Remove(int val) {
        if (!_indices.TryGetValue(val, out var set) || set.Count == 0) return false;

        int removeAt = set.First();
        int lastIndex = _values.Count - 1;
        int lastValue = _values[lastIndex];

        set.Remove(removeAt);                                  // remove first: handles removeAt == lastIndex safely
        if (removeAt != lastIndex) {
            _values[removeAt] = lastValue;
            _indices[lastValue].Remove(lastIndex);
            _indices[lastValue].Add(removeAt);
        }
        _values.RemoveAt(lastIndex);
        if (set.Count == 0) _indices.Remove(val);
        return true;
    }

    public int GetRandom() {
        if (_values.Count == 0) throw new InvalidOperationException("collection is empty");
        return _values[_rng.Next(_values.Count)];              // proportional by construction
    }
}''',
  complexity='Insert and Remove average O(1) (hash set operations); GetRandom O(1). Space O(n). Worth saying: "average" because '
             'hashing, and the swap-with-last trick is what keeps removal constant.',
  follow=['Remove *all* occurrences of a value in O(1) amortised.',
          'Weighted random by an explicit weight rather than multiplicity.',
          'Make it thread-safe — where is the race between GetRandom and Remove?',
          'Seeded RNG so tests are deterministic.'],
  optimise='`HashSet.First()` allocates an enumerator in older runtimes; keeping a small list per value is faster in practice. If '
           'the workload is mostly GetRandom, nothing beats the flat array — say why you would not switch to a tree.',
  evalpts=['Did you handle the self-swap case (removing the last element)?',
           'Did you keep GetRandom proportional to multiplicity?',
           'Did you get the Insert return-value contract right?',
           'Did you say "average O(1)" rather than O(1)?']),

 dict(id='kclosest', title='Find K Closest Elements', level='med', topic='Binary search · Two pointers',
  why='On your list. The interesting part is that the O(log n + k) answer is a binary search **on the window start**, which is a '
      'step above the obvious heap or two-pointer answer.',
  question='Given a sorted array, an integer k and a value x, return the k closest elements to x, sorted ascending. Ties go to the '
           'smaller element.',
  think='A heap gives O(n log k) and ignores that the array is sorted. Two pointers from the closest element gives O(n) worst case. '
        'What if you binary search for the *left edge of the answer window* instead?',
  approach='The answer is a contiguous window of length k. Binary search `lo` in `[0, n-k]` comparing `x - a[mid]` against '
           '`a[mid+k] - x`: if the left element is farther, the window must move right. That is O(log(n-k) + k), and the tie rule '
           'falls out of using a strict comparison.',
  edges=['k equals the array length → return everything.', 'x smaller than every element, or larger than every element.',
         'Exact ties (x sits exactly between two values) → the smaller wins, which the `>` comparison gives you.',
         'Duplicates in the array.', 'k = 0 → empty result.'],
  code='''public IList<int> FindClosestElements(int[] arr, int k, int x) {
    int lo = 0, hi = arr.Length - k;                    // window start is in [0, n-k]
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        // if the left edge is strictly farther than the element just past the window, shift right
        if (x - arr[mid] > arr[mid + k] - x) lo = mid + 1;
        else hi = mid;                                  // ties keep the smaller element, as required
    }
    return arr.Skip(lo).Take(k).ToList();               // or a manual copy to avoid LINQ allocation
}''',
  complexity='O(log(n−k) + k) time, O(k) output. Compare out loud with the heap (O(n log k)) and the expand-around-closest two '
             'pointers (O(n) worst case) — naming all three and picking one is the signal here.',
  follow=['The array is not sorted — what changes? (Quickselect by distance, O(n) average.)',
          'The data is a stream and k is fixed — a bounded heap by distance.',
          'x changes constantly for the same array — precompute nothing, the binary search is already cheap.',
          'Return them sorted by distance rather than by value.'],
  optimise='Avoid LINQ in the hot path; copy into a preallocated array. If k is close to n, the two-pointer approach touches fewer '
           'elements in practice despite the worse bound — measure rather than assume.',
  evalpts=['Did you spot that the answer is a contiguous window?',
           'Did you get the tie rule right, and test it?',
           'Did you compare the three approaches before choosing?',
           'Did you handle k = n and out-of-range x?']),

 dict(id='celebrity', title='Find the Celebrity', level='med', topic='Elimination · API cost',
  why='On your list, and it appears in recent Glassdoor reports of LinkedIn DSA rounds. It is really a question about minimising '
      'calls to an expensive API — which is a systems instinct dressed as a puzzle.',
  question='Among n people, a celebrity is known by everyone and knows nobody. You may only call `Knows(a, b)`. Find the celebrity '
           'or return -1, minimising calls.',
  think='The brute force is n² calls. Each call eliminates at least one person — why? Use that to get a single candidate in n−1 '
        'calls, then verify. What does verification actually require, and can you skip part of it?',
  approach='Phase 1: hold a candidate, walk the list; `Knows(candidate, i)` true means the candidate is not a celebrity so i '
           'becomes the candidate; false means i is not. One pass, n−1 calls, one survivor. Phase 2: verify the survivor against '
           'everyone (skipping the pairs already implied by phase 1 if you track them). Total ≤ 3(n−1) calls.',
  edges=['No celebrity exists → verification must fail and return -1.', 'n = 1 → that person is trivially the celebrity.',
         'n = 2.', 'Multiple candidates cannot exist — be ready to explain why (a second celebrity would have to know the first).',
         '`Knows` is expensive or flaky → cache results; do not call the same pair twice.'],
  code='''public int FindCelebrity(int n) {
    int candidate = 0;
    for (int i = 1; i < n; i++)
        if (Knows(candidate, i)) candidate = i;         // candidate knows someone => not a celebrity

    for (int i = 0; i < n; i++) {
        if (i == candidate) continue;
        if (Knows(candidate, i) || !Knows(i, candidate)) return -1;   // verify both directions
    }
    return candidate;
}

// If Knows() is expensive (a network call), memoise — the verification pass repeats pairs.
private readonly Dictionary<(int, int), bool> _cache = new();
private bool KnowsCached(int a, int b) {
    if (_cache.TryGetValue((a, b), out var v)) return v;
    return _cache[(a, b)] = Knows(a, b);
}''',
  complexity='O(n) calls: n−1 to find the candidate plus at most 2(n−1) to verify. O(1) space, or O(n) with the cache. The point '
             'is the call count, not the CPU time — say that.',
  follow=['`Knows` costs 50 ms over the network — now what? (Parallelise verification, and cache.)',
          'Prove the elimination argument: why can the discarded people never be the celebrity?',
          'Multiple celebrities allowed — how does the definition break?',
          'The relation is given as an adjacency matrix instead — does your answer change? (It becomes trivial to verify, and the same elimination still saves work.)'],
  optimise='Memoise `Knows`, and run the verification pass in parallel batches when the call is remote. Track the pairs already '
           'answered in phase 1 to skip them — it cuts roughly a third of the calls.',
  evalpts=['Did you get to O(n) calls, not O(n²)?',
           'Could you explain why each call eliminates someone?',
           'Did you verify in both directions?',
           'Did you treat `Knows` as an expensive dependency?']),

 dict(id='swd2', title='Shortest Word Distance II — the design variant', level='med', topic='Design · Two pointers',
  why='On your list. LinkedIn likes the **design** flavour: the single-query version is trivial, so they ask for the class that '
      'answers many queries.',
  question='Design a class initialised with a list of words that answers repeated queries: the shortest distance between two '
           'given words in the list.',
  think='If you rescan the word list per query, repeated queries are O(n) each. What can you precompute once, and what does that '
        'turn each query into?',
  approach='Precompute `word → sorted list of indices` at construction. A query merges the two index lists with two pointers, '
           'advancing whichever is behind, tracking the minimum gap: O(a + b) per query instead of O(n), where a and b are the '
           'occurrence counts. Construction is O(n).',
  edges=['The same word passed twice — Shortest Word Distance III territory; ask whether it is allowed.',
         'A word not in the list → decide: exception or a sentinel.', 'Words adjacent (distance 1).',
         'One word appearing thousands of times and the other once — the merge is still linear in the sum.',
         'Case sensitivity and duplicates in the constructor list.'],
  code='''public sealed class WordDistance {
    private readonly Dictionary<string, List<int>> _positions = new();

    public WordDistance(string[] words) {
        for (int i = 0; i < words.Length; i++) {
            if (!_positions.TryGetValue(words[i], out var list)) _positions[words[i]] = list = new List<int>();
            list.Add(i);                                       // naturally ascending
        }
    }

    public int Shortest(string word1, string word2) {
        if (!_positions.TryGetValue(word1, out var a) || !_positions.TryGetValue(word2, out var b))
            throw new ArgumentException("unknown word");

        int i = 0, j = 0, best = int.MaxValue;
        while (i < a.Count && j < b.Count) {                   // merge two sorted lists
            best = Math.Min(best, Math.Abs(a[i] - b[j]));
            if (a[i] < b[j]) i++; else j++;                    // advance the one that is behind
        }
        return best;
    }
}''',
  complexity='Construction O(n) time and space. Query O(a + b), which is far better than O(n) when the words are rare. Mention the '
             'worst case: both words appear everywhere, so a + b ≈ n.',
  follow=['Support word1 == word2 (Shortest Word Distance III).',
          'The document is updated — how do you keep the index current?',
          'Millions of queries on the same pair — cache the answer per pair.',
          'Now return the positions, not just the distance.'],
  optimise='Cache results per unordered pair if queries repeat. If one list is much shorter, binary search its entries into the '
           'longer list: O(a log b) beats O(a + b) when a ≪ b — a genuinely nice optimisation to volunteer.',
  evalpts=['Did you precompute rather than rescanning?',
           'Did you merge with two pointers rather than a nested loop?',
           'Did you give the asymmetric binary-search optimisation?',
           'Did you ask about the same-word case?']),

 dict(id='bulb', title='Bulb Switcher', level='med', topic='Maths · Reasoning',
  why='On your list. It is not really a coding problem — it is a "can you find the invariant instead of simulating" problem, and '
      'the answer is one line.',
  question='There are n bulbs, initially off. On round i you toggle every i-th bulb. After n rounds, how many bulbs are on?',
  think='A bulb ends on if it is toggled an odd number of times. How many times is bulb k toggled? Which numbers have an odd '
        'number of divisors, and why?',
  approach='Bulb k is toggled once per divisor of k. Divisors pair up (d, k/d) except when d = k/d, which happens only for perfect '
           'squares. So exactly the perfect squares end on, and the answer is ⌊√n⌋. Simulation is O(n log n); the insight is O(1).',
  edges=['n = 0 → 0.', 'n = 1 → 1.', 'Large n (10⁹) — the simulation is impossible, which is the point.',
         'Floating-point `Math.Sqrt` on very large n can be off by one — correct it with an integer check.'],
  code='''public int BulbSwitch(int n) {
    // A bulb is toggled once per divisor; divisors pair except for perfect squares.
    int root = (int)Math.Sqrt(n);
    while ((long)(root + 1) * (root + 1) <= n) root++;         // guard against floating-point drift
    while ((long)root * root > n) root--;
    return root;
}''',
  complexity='O(1) time and space. The simulation you rejected is O(n log n) — say both, and say why the insight matters at n = 10⁹.',
  follow=['Prove that only perfect squares have an odd divisor count.',
          'What if round i toggles every i-th bulb *starting from i*? (Same thing — check the indexing.)',
          'What if there are two passes, or the toggle rule changes? (Now you may genuinely need to simulate — say when the '
          'insight stops applying.)'],
  optimise='Nothing to optimise; the whole problem is refusing to simulate. Mention the floating-point correction — an interviewer '
           'who has seen `(int)Math.Sqrt(999999999)` go wrong will notice that you guarded it.',
  evalpts=['Did you find the invariant rather than simulating?',
           'Could you prove the perfect-square argument?',
           'Did you guard the integer square root?',
           'Did you state both complexities?']),

 dict(id='upsidedown', title='Binary Tree Upside Down', level='med', topic='Trees · Pointer surgery',
  why='On your list twice (including a variant phrased around a 0/1 right child), which makes it one of your highest-signal tree '
      'problems. It is pure pointer rewiring, which is exactly what the Staff Coding module says it probes.',
  question='Given a binary tree where every right child is either a leaf or empty, turn it upside down: the original left child '
           'becomes the new root, the original root becomes its right child, and the original right child becomes its left child.',
  think='Draw three levels and write down, for one node, what its new left, right and parent are. Then ask whether you want to '
        'walk down and rewire on the way back up (recursion) or rewire as you descend while carrying the previous pointers '
        '(iteration).',
  approach='Recursive: recurse on `root.left` until you reach the new root, then on the way back set `root.left.left = root.right`, '
           '`root.left.right = root`, and null out the original root\'s children. Iterative: walk down the left spine carrying '
           '`prev` node and `prevRight`, rewiring as you go — O(1) space, and the version worth showing after the recursive one.',
  edges=['Empty tree → null.', 'Single node → itself.', 'A left spine with no right children at all.',
         'Forgetting to null the original root\'s pointers → a cycle, and an infinite loop in any traversal.',
         'The precondition (right child is a leaf or empty) — say that your answer depends on it.'],
  code='''// Recursive: rewire on the way back up.
public TreeNode UpsideDownBinaryTree(TreeNode root) {
    if (root?.left == null) return root;                   // empty, or we reached the new root

    var newRoot = UpsideDownBinaryTree(root.left);
    root.left.left  = root.right;                          // old right child becomes new left
    root.left.right = root;                                // old parent becomes new right
    root.left = null;                                      // must null, or we build a cycle
    root.right = null;
    return newRoot;
}

// Iterative: O(1) space, rewiring while descending the left spine.
public TreeNode UpsideDownIterative(TreeNode root) {
    TreeNode cur = root, prev = null, prevRight = null;
    while (cur != null) {
        var next = cur.left;                               // save before we overwrite
        cur.left = prevRight;                              // previous node's right child
        prevRight = cur.right;                             // remember for the next level
        cur.right = prev;
        prev = cur;
        cur = next;
    }
    return prev;                                           // the deepest left node is the new root
}''',
  complexity='O(n) time. Recursive: O(h) stack, which is O(n) on a left spine — and this tree *is* a left spine, so mention it. '
             'Iterative: O(1) space, which is the reason to show it.',
  follow=['Do it without recursion (have the iterative version ready before being asked).',
          'Reverse the operation.', 'What breaks if a right child has children of its own?',
          'Verify the result has no cycles — how would you test that?'],
  optimise='The iterative version is the optimisation. Beyond that, the useful move is an invariant check in tests: after the '
           'transform, a traversal must terminate and visit exactly n nodes — that catches the cycle bug immediately.',
  evalpts=['Did you draw it before coding?',
           'Did you null the old pointers (no cycle)?',
           'Did you offer the O(1)-space iterative version?',
           'Did you note that the recursive stack is O(n) for this shape?']),

 dict(id='mergetrees', title='Merge two keyed trees, summing values', level='med', topic='Trees · N-ary · Recursion',
  why='On your list with a precise variant: *"Tree has keys and values, values represent the sum of this and child node values. '
      'When merging, absent branches should be created, and values for existing branches are summed. Keys are unique among child '
      'nodes of a single parent. Child nodes could be stored in any order."* That is an n-ary keyed merge, not the binary '
      'LeetCode version — code the general one.',
  question='Merge two trees whose nodes have a key and a value. Children are keyed uniquely within a parent and stored in any '
           'order. Merging sums values for matching keys and creates branches present in only one tree.',
  think='"Children in any order" kills positional recursion — you need to match by key, which means a dictionary per node. '
        '"Absent branches should be created" raises an ownership question: do you mutate an input tree or build a new one? Ask, '
        'because deep-copying a shared subtree and aliasing it are very different bugs.',
  approach='Recursive merge keyed by child key: build a dictionary of a\'s children, walk b\'s children, sum on match and recurse; '
           'otherwise attach (a copy of) b\'s subtree. Return a **new** tree unless the interviewer explicitly allows mutation — '
           'and say why: aliasing a subtree into two trees means a later edit silently changes both.',
  edges=['One tree null → return a copy of the other (or the other, if aliasing is allowed).',
         'Duplicate keys within one parent — the contract forbids it; validate or state the assumption.',
         'Very deep trees → recursion depth; offer an explicit stack.',
         'Value overflow when summing large values → use long, or say you checked.',
         'Cycles — a "tree" from an untrusted source may not be one.'],
  code='''public sealed class Node {
    public string Key;
    public long Value;
    public Dictionary<string, Node> Children = new();      // keyed, order-independent
}

/// <summary>Returns a new tree; inputs are not mutated and no subtree is aliased.</summary>
public static Node Merge(Node a, Node b) {
    if (a is null) return Clone(b);
    if (b is null) return Clone(a);

    var merged = new Node { Key = a.Key, Value = a.Value + b.Value };

    foreach (var (key, childA) in a.Children)
        merged.Children[key] = b.Children.TryGetValue(key, out var childB)
            ? Merge(childA, childB)                        // present in both: sum and recurse
            : Clone(childA);

    foreach (var (key, childB) in b.Children)
        if (!a.Children.ContainsKey(key))
            merged.Children[key] = Clone(childB);          // absent branch: create it

    return merged;
}

private static Node Clone(Node n) {
    if (n is null) return null;
    var copy = new Node { Key = n.Key, Value = n.Value };
    foreach (var (key, child) in n.Children) copy.Children[key] = Clone(child);
    return copy;
}

// The binary LeetCode 617 version, for comparison — positional, not keyed.
public TreeNode MergeTrees(TreeNode t1, TreeNode t2) {
    if (t1 == null) return t2;
    if (t2 == null) return t1;
    t1.val += t2.val;
    t1.left  = MergeTrees(t1.left,  t2.left);
    t1.right = MergeTrees(t1.right, t2.right);
    return t1;                                             // note: this one DOES mutate t1
}''',
  complexity='O(a + b) nodes visited, plus the clone cost for branches present in only one tree. Space O(result) plus O(depth) '
             'recursion. If you alias instead of cloning you drop the clone cost — and gain the aliasing hazard. Name the trade.',
  follow=['Merge k trees.', 'Do it without recursion for a 10⁵-deep tree.',
          'What if values should be maxed instead of summed? (Pass in a combiner — the extensibility seam.)',
          'What if the invariant "value = sum of this and children" must hold after merging? (Recompute bottom-up, and say that '
          'summing values pairwise already preserves it.)'],
  optimise='Iterate the smaller child dictionary and look up in the larger. If mutation is permitted and one tree is disposable, '
           'merge into it and skip cloning entirely — but make that an explicit, stated decision.',
  evalpts=['Did you match children by key rather than position?',
           'Did you ask about mutation versus a new tree?',
           'Did you handle branches present in only one side?',
           'Did you consider recursion depth and overflow?',
           'Did you offer the combiner seam for max/sum?']),

 dict(id='degree', title='Minimum degree of connection between two users', level='med', topic='Graphs · Bidirectional BFS',
  why='On your list with the expected answer named: *"Expected ans: bidirectional BFS. Follow up: find the path."* This is the '
      'LinkedIn question — the social graph is the product, and at a billion members one-directional BFS is not viable.',
  question='Given users and their direct connections, find the minimum degree of connection between users S and P. Directly '
           'connected users are degree 1. Then: return the actual path.',
  think='With branching factor b and answer depth d, one-directional BFS explores about b^d. What does searching from both ends '
        'do to that? And what do you need to store to reconstruct the path rather than just the distance?',
  approach='Bidirectional BFS: two frontiers and two visited maps (node → parent), always expanding the **smaller** frontier. When '
           'a node appears in the other side\'s visited map, the frontiers have met. Distance is the sum of the two depths; the '
           'path is the meeting node walked back through both parent maps, with the second half reversed.',
  edges=['S == P → degree 0.', 'Directly connected → 1.', 'Disconnected → no path; return -1 or empty, and say which.',
         'A hub user with a million connections — the frontier explodes; cap or sample and say what you traded.',
         'Self-loops and duplicate edges.', 'Privacy: some connections may not be visible to the searcher.'],
  code='''public (int Degree, IReadOnlyList<string> Path) MinDegree(string s, string p) {
    if (s == p) return (0, new[] { s });

    var fromS = new Dictionary<string, string> { [s] = null };   // node -> parent, doubles as visited
    var fromP = new Dictionary<string, string> { [p] = null };
    var frontierS = new List<string> { s };
    var frontierP = new List<string> { p };
    int degree = 0;

    while (frontierS.Count > 0 && frontierP.Count > 0) {
        // always expand the smaller side: this is what makes it bidirectional rather than two BFS runs
        bool expandS = frontierS.Count <= frontierP.Count;
        var frontier = expandS ? frontierS : frontierP;
        var ours     = expandS ? fromS : fromP;
        var theirs   = expandS ? fromP : fromS;

        var next = new List<string>();
        degree++;
        foreach (var node in frontier)
            foreach (var neighbour in Connections(node)) {
                if (ours.ContainsKey(neighbour)) continue;
                ours[neighbour] = node;
                if (theirs.ContainsKey(neighbour))                // frontiers met
                    return (degree, BuildPath(neighbour, fromS, fromP));
                next.Add(neighbour);
            }

        if (expandS) frontierS = next; else frontierP = next;
    }
    return (-1, Array.Empty<string>());                           // no path
}

private static IReadOnlyList<string> BuildPath(string meet, Dictionary<string, string> fromS, Dictionary<string, string> fromP) {
    var left = new List<string>();
    for (var n = meet; n != null; n = fromS[n]) left.Add(n);
    left.Reverse();                                               // s ... meet
    var right = new List<string>();
    for (var n = fromP[meet]; n != null; n = fromP[n]) right.Add(n);   // skip meet, avoid duplicating it
    left.AddRange(right);                                         // ... p
    return left;
}''',
  complexity='Bidirectional BFS explores roughly 2·b^(d/2) instead of b^d — for b = 100 and d = 4, that is ~20,000 nodes instead '
             'of 100 million. Memory is the frontier plus visited maps on both sides. Say those numbers; they are the reason for '
             'the technique.',
  follow=['Return the path (be ready — your own note says this is the follow-up).',
          'Degrees beyond 3 are not shown in the product — cap the search and say why that also bounds cost.',
          'The graph does not fit on one machine — partitioned BFS, or precomputed second-degree sets (this is the PYMK design).',
          'Weighted edges (connection strength) → Dijkstra, not BFS.',
          'Privacy filtering mid-traversal.'],
  optimise='Cap the depth (LinkedIn shows up to 3rd degree). Skip or sample hub nodes above a connection threshold. For repeated '
           'queries from the same user, cache their first- and second-degree sets — which is exactly how the product serves it.',
  evalpts=['Did you expand the smaller frontier each round?',
           'Did you keep parent maps so the path follow-up is free?',
           'Did you quantify the saving with real numbers?',
           'Did you raise hub nodes and the depth cap yourself?']),

 dict(id='compact', title='Build a compact tree (phone-screen report)', level='med', topic='Trees · N-ary · Recursion',
  why='From the LeetCode Discuss LinkedIn phone-screen report on your list: *"form compact tree from a given tree; every node will '
      'have N nodes and at least a node can have 0–N nodes"*. The reporter noted missing one edge case — so the edge cases are '
      'the graded part.',
  question='Given an n-ary tree, produce its compact form: collapse any chain where a node has exactly one child into a single '
           'node, preserving the leaves and the branching structure. (Clarify the exact compaction rule with the interviewer — '
           'the reported wording is loose.)',
  think='First, make the interviewer define "compact": collapse single-child chains? Merge nodes with identical keys? Remove empty '
        'subtrees? The reported failure was an edge case, which usually means the root or an empty child list. Restate before coding.',
  approach='Post-order recursion: compact every child first, drop children that compacted to nothing, then if this node has exactly '
           'one child and no payload of its own, return that child in its place (merging labels if the contract says so). The root '
           'and the leaves are the two cases to handle explicitly.',
  edges=['**The root collapsing to a single child** — the case most people miss.', 'A node whose children all vanish (becomes a leaf).',
         'An empty tree, and a single-node tree.', 'A node with exactly one child but meaningful payload — must not collapse.',
         'Deep single-child chains (10⁵ long) → recursion depth.',
         'Preserving child order, or not — ask.'],
  code='''public sealed class NTreeNode {
    public string Label;
    public object Payload;                                 // null means "structural only"
    public List<NTreeNode> Children = new();
}

/// <summary>Collapses structural single-child chains. Returns null if the subtree disappears entirely.</summary>
public static NTreeNode Compact(NTreeNode node) {
    if (node is null) return null;

    var kept = new List<NTreeNode>(node.Children.Count);
    foreach (var child in node.Children) {
        var c = Compact(child);                            // post-order: children first
        if (c is not null) kept.Add(c);
    }
    node.Children = kept;

    if (kept.Count == 0 && node.Payload is null && !IsRoot(node)) return null;   // structural leaf: drop

    if (kept.Count == 1 && node.Payload is null) {         // collapse a structural chain link
        var only = kept[0];
        only.Label = node.Label + "/" + only.Label;        // merge labels — confirm this rule first
        return only;                                       // NOTE: this applies at the root too
    }
    return node;
}''',
  complexity='O(n) time, O(h) stack. The label merge makes it O(total label length) if chains are long — mention it if labels are '
             'concatenated.',
  follow=['What if two siblings have the same label after compaction — merge them, or keep both?',
          'Do it iteratively for a very deep chain.',
          'Now compact in place versus returning a new tree.',
          'How would you test it? (Round-trip: compacting twice must equal compacting once — idempotence is a great property test.)'],
  optimise='Idempotence is the property worth asserting in tests. If labels are concatenated repeatedly, build them with a '
           '`StringBuilder` during a single downward pass instead of at each level.',
  evalpts=['Did you make the interviewer define "compact" before coding?',
           'Did you handle the root collapsing?',
           'Did you handle a node whose children all disappear?',
           'Did you mention the idempotence property test?']),

 dict(id='triangle', title='Valid triangle — find one, then count them', level='med', topic='Sorting · Two pointers',
  why='From the phone-screen report on your list: *"given a sorted array find a valid triangle and return their sides; follow-up: '
      'find the number of triangles"*. The follow-up is the real question, and the O(n²) counting trick is the thing to have ready.',
  question='Given a sorted array of side lengths, return any three that form a valid triangle (the sum of two sides exceeds the '
           'third). Then: count how many such triples exist.',
  think='For a sorted array, which triple is most likely to work — and which single comparison decides validity? For counting, if '
        'you fix the largest side and use two pointers, how many triples does one successful comparison account for?',
  approach='**Find one:** in a sorted array, only adjacent triples need checking — if `a[i] + a[i+1] > a[i+2]` fails for every i, '
           'none exists. O(n) after sorting.\n\n'
           '**Count all:** fix the largest side at index k descending, two pointers lo = 0, hi = k−1. If `a[lo] + a[hi] > a[k]`, '
           'then every lo\' in [lo, hi) also works with hi, so add `hi − lo` and decrement hi; otherwise increment lo. O(n²).',
  edges=['Fewer than three elements → none.', 'Zeros or negative lengths → no valid triangle; validate.',
         'Degenerate triangles (a + b == c) are invalid — the strict inequality matters.',
         'Duplicates are fine and count separately.', 'Overflow on `a[lo] + a[hi]` for large ints → widen to long.'],
  code='''// Find any one valid triangle: adjacent triples are the only candidates in a sorted array.
public int[] FindTriangle(int[] sorted) {
    for (int i = 0; i + 2 < sorted.Length; i++)
        if ((long)sorted[i] + sorted[i + 1] > sorted[i + 2])
            return new[] { sorted[i], sorted[i + 1], sorted[i + 2] };
    return Array.Empty<int>();
}

// Count all valid triples: fix the largest side, two pointers inside.
public int TriangleNumber(int[] nums) {
    Array.Sort(nums);                                       // O(n log n) if not already sorted
    int count = 0;
    for (int k = nums.Length - 1; k >= 2; k--) {
        int lo = 0, hi = k - 1;
        while (lo < hi) {
            if ((long)nums[lo] + nums[hi] > nums[k]) {
                count += hi - lo;                           // every index in [lo, hi) also works with hi
                hi--;
            } else lo++;
        }
    }
    return count;
}''',
  complexity='Find one: O(n) on sorted input. Count: O(n²) with O(1) extra space — and the key insight is that one successful '
             'comparison contributes `hi − lo` triples rather than one, which is what turns O(n³) into O(n²).',
  follow=['Prove that only adjacent triples matter for the existence question.',
          'Count with duplicates — does anything change? (No; each index is a distinct side.)',
          'Return all triples instead of the count — now you are output-bound, O(n³) worst case.',
          'The input is not sorted — sorting dominates at O(n log n).'],
  optimise='Skip zeros up front (no triangle can include one). If only existence is asked, stop at the first success — the '
           'adjacent-triple scan is already optimal.',
  evalpts=['Did you use the adjacency insight for the existence question?',
           'Did you get `count += hi - lo` rather than counting one at a time?',
           'Did you handle degenerate (a+b==c) and zero cases?',
           'Did you widen the sum to avoid overflow?']),

 dict(id='booths', title='Booths and groups — maximise the experience factor', level='hard', topic='Prefix sums · Range queries',
  why='From your list, and it is the least standard of the set — which makes it a good test of clarifying before coding. The '
      'phrasing leaves the objective genuinely ambiguous, and an interviewer watching you assume is learning something.',
  question='m booths are set up in a row, each displaying robots (0) or drones (1), so the row is a binary string. n groups each '
           'visit booths from position i to j. The experience factor of a visit is (number of drone booths visited) × (number of '
           'robot booths visited). Maximise the experience factor.',
  think='Stop and ask what is being maximised. Three readings: (a) compute the factor for each given [i, j]; (b) for each given '
        '[i, j], choose the best sub-range inside it; (c) choose the ranges yourself. They need different algorithms, and picking '
        'one silently is the failure mode here.',
  approach='**Clarify first**, then:\n\n'
           '(a) **Given ranges** — prefix sums of ones: ones = P[j+1] − P[i], zeros = (j − i + 1) − ones, factor = ones × zeros. '
           'O(m) precompute, O(1) per query.\n\n'
           '(b) **Best sub-range inside [i, j]** — the factor is maximised when ones and zeros are as balanced as possible. Brute '
           'force is O(len²) per query; with prefix sums it is still O(len²) but with O(1) inner work, and you can prune: the '
           'product is bounded by ⌊len/2⌋·⌈len/2⌉, so any window already at that bound is optimal and you can stop.\n\n'
           '(c) **Whole string, best range** — the same balanced-window argument; scan windows with prefix sums, or binary search '
           'on the achievable product.\n\n'
           'Say the bound out loud: for a window of length L the factor can never exceed ⌊L/2⌋·⌈L/2⌉, which is what makes pruning '
           'legitimate.',
  edges=['All robots or all drones → factor 0 for any range.', 'i == j → factor 0 (one booth cannot be both).',
         'Empty range, or i > j → validate the input.', 'Very large m with many queries → prefix sums are the whole point.',
         'Overflow: counts up to 10⁵ each make the product 10¹⁰ — use long.'],
  code='''public sealed class Booths {
    private readonly int[] _prefixOnes;                     // _prefixOnes[i] = number of 1s in [0, i)
    private readonly int _length;

    public Booths(string booths) {
        _length = booths.Length;
        _prefixOnes = new int[_length + 1];
        for (int i = 0; i < _length; i++)
            _prefixOnes[i + 1] = _prefixOnes[i] + (booths[i] == '1' ? 1 : 0);
    }

    /// <summary>Reading (a): the factor for the exact range [i, j].</summary>
    public long Factor(int i, int j) {
        if (i < 0 || j >= _length || i > j) throw new ArgumentOutOfRangeException();
        long ones = _prefixOnes[j + 1] - _prefixOnes[i];
        long zeros = (j - i + 1) - ones;
        return ones * zeros;                                // widen: 10^5 * 10^5 overflows int
    }

    /// <summary>Reading (b): the best sub-range inside [i, j], with the balanced-window bound as a pruning rule.</summary>
    public (long Best, int Start, int End) BestWithin(int i, int j) {
        long best = 0; int bs = i, be = i;
        for (int a = i; a <= j; a++) {
            int maxLen = j - a + 1;
            if ((long)(maxLen / 2) * ((maxLen + 1) / 2) <= best) break;    // no window from here can beat best
            for (int b = a; b <= j; b++) {
                long f = Factor(a, b);
                if (f > best) { best = f; bs = a; be = b; }
                int remaining = j - a + 1;
                if (best == (long)(remaining / 2) * ((remaining + 1) / 2)) return (best, bs, be);   // provably optimal
            }
        }
        return (best, bs, be);
    }
}''',
  complexity='Reading (a): O(m) build, O(1) per query — the answer you want for n groups. Reading (b): O(L²) per query worst case '
             'with O(1) inner work, and the bound-based pruning cuts it hard in practice. Always state which reading you are '
             'costing.',
  follow=['Which reading did you assume, and why?',
          'n is 10⁶ queries — does your per-query cost still work? (Reading (a) yes, reading (b) no.)',
          'Booths can be updated between groups — now you need a Fenwick tree instead of a static prefix array.',
          'Generalise to k types instead of two — the product becomes a product over counts, and the balanced argument extends.'],
  optimise='For updates, swap the prefix array for a Fenwick tree: O(log m) update and query. For reading (b) at scale, the '
           'balanced-window bound plus a sliding window over candidate lengths is far better than the double loop — worth '
           'sketching even if you do not code it.',
  evalpts=['Did you ask which reading before writing code? (This is the whole point of this problem.)',
           'Did you use prefix sums rather than recounting?',
           'Did you widen the product to long?',
           'Did you state the ⌊L/2⌋·⌈L/2⌉ bound and use it to prune?',
           'Did you say what changes if booths become updatable?']),
]
