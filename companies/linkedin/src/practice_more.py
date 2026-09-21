# -*- coding: utf-8 -*-
"""Second batch of practice problems: n-ary trees, graphs, and the design questions.

Design questions set wrap=False, because you are writing the class itself rather than
a method inside Solution. Their harnesses run an operation sequence and assert after
each call, which is how these are actually judged in an interview.

All harness code stays C# 7.0-compatible so it compiles on the fallback engine too.
"""

NARY = r"""public class NaryNode {
    public string Key;
    public int Val;
    public List<NaryNode> Children = new List<NaryNode>();
    public NaryNode(string key, int val) { Key = key; Val = val; }
}

public static class N {
    public static NaryNode Make(string key, int val, params NaryNode[] kids) {
        NaryNode n = new NaryNode(key, val);
        foreach (NaryNode k in kids) n.Children.Add(k);
        return n;
    }
    /// <summary>Children sorted by key, so the order you emit them in never matters.</summary>
    public static string Ser(NaryNode n) {
        if (n == null) return "-";
        List<string> kids = new List<string>();
        foreach (NaryNode c in n.Children) kids.Add(Ser(c));
        kids.Sort(StringComparer.Ordinal);
        return n.Key + ":" + n.Val + (kids.Count == 0 ? "" : "(" + string.Join(",", kids) + ")");
    }
}
"""

NESTED = r"""public class NestedInteger {
    int? _v;
    List<NestedInteger> _list = new List<NestedInteger>();
    public NestedInteger() { }
    public NestedInteger(int value) { _v = value; }
    public bool IsInteger() { return _v.HasValue; }
    public int GetInteger() { return _v.Value; }
    public void Add(NestedInteger ni) { _list.Add(ni); }
    public IList<NestedInteger> GetList() { return _list; }
}

public static class NI {
    /// <summary>Builds a nested list from text such as [[1,1],2,[1,1]]</summary>
    public static IList<NestedInteger> Parse(string s) {
        int i = 0;
        return ParseValue(s, ref i).GetList();
    }
    static NestedInteger ParseValue(string s, ref int i) {
        while (i < s.Length && (s[i] == ' ' || s[i] == ',')) i++;
        if (s[i] == '[') {
            i++;
            NestedInteger node = new NestedInteger();
            while (i < s.Length && s[i] != ']') {
                node.Add(ParseValue(s, ref i));
                while (i < s.Length && (s[i] == ' ' || s[i] == ',')) i++;
            }
            i++;
            return node;
        }
        int start = i;
        if (s[i] == '-') i++;
        while (i < s.Length && char.IsDigit(s[i])) i++;
        return new NestedInteger(int.Parse(s.Substring(start, i - start)));
    }
}
"""

RELATION = r"""public class Relation {
    static bool[,] _k;
    public static int Calls;
    public static void Setup(bool[,] matrix) { _k = matrix; Calls = 0; }
    protected bool Knows(int a, int b) { Calls++; return _k[a, b]; }
}
"""

COMPACT = r"""public class CNode {
    public string Label;
    public object Payload;                       // null means the node is structural only
    public List<CNode> Children = new List<CNode>();
    public CNode(string label, object payload) { Label = label; Payload = payload; }
}

public static class C {
    public static CNode Make(string label, object payload, params CNode[] kids) {
        CNode n = new CNode(label, payload);
        foreach (CNode k in kids) n.Children.Add(k);
        return n;
    }
    public static string Ser(CNode n) {
        if (n == null) return "-";
        List<string> kids = new List<string>();
        foreach (CNode c in n.Children) kids.Add(Ser(c));
        return n.Label + (kids.Count == 0 ? "" : "(" + string.Join(",", kids) + ")");
    }
}
"""


def _P(**kw):
    kw.setdefault('types', '')
    kw.setdefault('hint', '')
    kw.setdefault('wrap', True)
    return kw


MORE = [

 _P(id='keyed-merge', title='Merge two keyed trees', lesson='2.3', chapter='Ch 2',
    diff='Medium', evidence='Your list, with the exact wording', pattern='N-ary trees',
    video='c2l3-keyed-merge/LinkedIn-Coding-2.3-Keyed-Tree-Merge.mp4', types=NARY,
    statement='<p>Merge two n-ary trees whose nodes carry a <b>key</b> and a value. Nodes with '
              'the same key at the same position are merged and their values summed. A node '
              'present in only one tree is carried across.</p>'
              '<p><b>Children are identified by key, not by position</b>, and the inputs must not '
              'be modified. Return a new tree.</p>',
    hint='Pair the children up in a dictionary keyed by child key. Position-by-position is the trap.',
    stub='public NaryNode Merge(NaryNode a, NaryNode b) {\n    \n}',
    harness=r'''NaryNode a = N.Make("root", 1, N.Make("x", 2), N.Make("y", 3));
NaryNode b = N.Make("root", 10, N.Make("y", 30), N.Make("z", 40));
H.Case("keys pair up, order differs", "root:11(x:2,y:33,z:40)", delegate {
    return N.Ser(new Solution().Merge(a, b)); });
H.Case("inputs untouched (a)", "root:1(x:2,y:3)", delegate { return N.Ser(a); });
H.Case("inputs untouched (b)", "root:10(y:30,z:40)", delegate { return N.Ser(b); });
H.Case("one side null", "root:1(x:2,y:3)", delegate {
    return N.Ser(new Solution().Merge(N.Make("root", 1, N.Make("x", 2), N.Make("y", 3)), null)); });
H.Case("both null", "-", delegate { return N.Ser(new Solution().Merge(null, null)); });
H.Case("deep nesting", "r:2(a:2(b:2))", delegate {
    return N.Ser(new Solution().Merge(
        N.Make("r", 1, N.Make("a", 1, N.Make("b", 1))),
        N.Make("r", 1, N.Make("a", 1, N.Make("b", 1))))); });'''),

 _P(id='nested-sum', title='Nested List Weight Sum II', lesson='2.4', chapter='Ch 2',
    diff='Medium', evidence='LinkedIn tagged set + 2026 phone screen', pattern='Level accumulation',
    video='c2l4-nested-sum/LinkedIn-Coding-2.4-Nested-And-Compact.mp4', types=NESTED,
    statement='<p>Each integer in a nested list has a weight of <b>maxDepth &minus; depth + 1</b>, '
              'so the <b>deepest</b> integers weigh 1 and the shallowest weigh most. Return the sum '
              'of each integer times its weight.</p>',
    hint='You can do it in one pass: keep a running level sum and add it into the total after every level.',
    stub='public int DepthSumInverse(IList<NestedInteger> nestedList) {\n    \n}',
    harness=r'''H.Case("[[1,1],2,[1,1]]", 8, delegate {
    return new Solution().DepthSumInverse(NI.Parse("[[1,1],2,[1,1]]")); });
H.Case("[1,[4,[6]]]", 17, delegate {
    return new Solution().DepthSumInverse(NI.Parse("[1,[4,[6]]]")); });
H.Case("flat list", 6, delegate {
    return new Solution().DepthSumInverse(NI.Parse("[1,2,3]")); });
H.Case("empty list", 0, delegate {
    return new Solution().DepthSumInverse(NI.Parse("[]")); });
H.Case("single deep value", 5, delegate {
    return new Solution().DepthSumInverse(NI.Parse("[[[5]]]")); });
H.Case("negatives", -8, delegate {
    return new Solution().DepthSumInverse(NI.Parse("[[-1,-1],-2,[-1,-1]]")); });'''),

 _P(id='compact-tree', title='Compact a tree', lesson='2.4', chapter='Ch 2',
    diff='Medium', evidence='LinkedIn phone-screen write-up', pattern='Bottom-up rebuild',
    video='c2l4-nested-sum/LinkedIn-Coding-2.4-Nested-And-Compact.mp4', types=COMPACT,
    statement='<p><b>The reported wording was ambiguous</b> &mdash; the lesson is about asking which '
              'meaning is wanted. Here is one precise version to implement:</p>'
              '<p>A node is <i>structural</i> when its <code>Payload</code> is null. Collapse every '
              'structural node that has exactly one child, merging its label into that child as '
              '<code>parent/child</code>. Drop structural nodes that end up with no children. '
              'Return the new root, or null if everything disappeared.</p>',
    hint='Go bottom-up and return the possibly-new subtree root. Then the root collapsing is not a special case.',
    stub='public CNode Compact(CNode node) {\n    \n}',
    harness=r'''H.Case("chain collapses", "a/b/c", delegate {
    return C.Ser(new Solution().Compact(C.Make("a", null, C.Make("b", null, C.Make("c", "leaf"))))); });
H.Case("root collapses too", "a/b(x,y)", delegate {
    return C.Ser(new Solution().Compact(
        C.Make("a", null, C.Make("b", "keep", C.Make("x", "p"), C.Make("y", "p"))))); });
H.Case("payload blocks collapse", "a(b)", delegate {
    return C.Ser(new Solution().Compact(C.Make("a", "keep", C.Make("b", "keep")))); });
H.Case("two children, no collapse", "a(x,y)", delegate {
    return C.Ser(new Solution().Compact(C.Make("a", null, C.Make("x", "p"), C.Make("y", "p")))); });
H.Case("empty structural tree disappears", "-", delegate {
    return C.Ser(new Solution().Compact(C.Make("a", null))); });
H.Case("null input", "-", delegate { return C.Ser(new Solution().Compact(null)); });
H.Case("idempotent", true, delegate {
    CNode t = C.Make("a", null, C.Make("b", null, C.Make("c", "leaf")));
    string once = C.Ser(new Solution().Compact(t));
    CNode t2 = C.Make("a", null, C.Make("b", null, C.Make("c", "leaf")));
    string twice = C.Ser(new Solution().Compact(new Solution().Compact(t2)));
    return once == twice; });'''),

 _P(id='min-degree', title='Minimum degree of connection', lesson='3.3', chapter='Ch 3',
    diff='Medium', evidence='Your list, with the path follow-up', pattern='Bidirectional BFS',
    video='c3l3-min-degree/LinkedIn-Coding-3.3-Degrees-Of-Connection.mp4',
    statement='<p>Members are numbered 0..n&minus;1 and connections are undirected. Return the '
              'number of hops on the shortest path between two members: 0 if they are the same '
              'person, 1 if directly connected, and <b>&minus;1</b> if there is no path.</p>',
    hint='BFS, not DFS. If you want the speed-up, expand whichever frontier is smaller.',
    stub='public int MinDegree(int n, int[][] edges, int a, int b) {\n    \n}',
    harness=r'''int[][] e = new int[][] { new int[]{0,1}, new int[]{1,2}, new int[]{2,3}, new int[]{4,5} };
H.Case("three hops", 3, delegate { return new Solution().MinDegree(6, e, 0, 3); });
H.Case("direct connection", 1, delegate { return new Solution().MinDegree(6, e, 0, 1); });
H.Case("same member", 0, delegate { return new Solution().MinDegree(6, e, 2, 2); });
H.Case("different components", -1, delegate { return new Solution().MinDegree(6, e, 0, 5); });
H.Case("isolated member", -1, delegate {
    return new Solution().MinDegree(3, new int[][]{ new int[]{0,1} }, 0, 2); });
H.Case("shortest of two routes", 2, delegate {
    return new Solution().MinDegree(4, new int[][]{ new int[]{0,1}, new int[]{1,3},
        new int[]{0,2}, new int[]{2,3}, new int[]{1,2} }, 0, 3); });'''),

 _P(id='all-oone', title='All O`one Data Structure', lesson='4.1', chapter='Ch 4',
    diff='Hard', evidence='Your list + LeetCode Staff report', pattern='Bucket list', wrap=False,
    video='c4l1-all-oone/LinkedIn-Coding-4.1-All-O-One.mp4',
    statement='<p>Build a structure of string keys and counts where <b>all four operations are '
              'O(1)</b>:</p><p><code>Inc(key)</code> adds one (inserting at 1). '
              '<code>Dec(key)</code> subtracts one, removing the key at 0. '
              '<code>GetMaxKey()</code> / <code>GetMinKey()</code> return any key with the largest '
              'or smallest count, or "" when empty.</p>',
    hint='A heap breaks the requirement. Group keys that share a count, and keep the groups in a sorted doubly linked list.',
    stub='''public class AllOne {

    public AllOne() {

    }

    public void Inc(string key) {

    }

    public void Dec(string key) {

    }

    public string GetMaxKey() {

    }

    public string GetMinKey() {

    }
}''',
    harness=r'''AllOne a = new AllOne();
H.Case("empty -> max is \"\"", "", delegate { return a.GetMaxKey(); });
H.Case("empty -> min is \"\"", "", delegate { return a.GetMinKey(); });

a.Inc("hello"); a.Inc("hello");
H.Case("one key is both ends", "hello", delegate { return a.GetMaxKey(); });
H.Case("min agrees", "hello", delegate { return a.GetMinKey(); });

a.Inc("world");
H.Case("max after a new key", "hello", delegate { return a.GetMaxKey(); });
H.Case("min after a new key", "world", delegate { return a.GetMinKey(); });

a.Inc("world"); a.Inc("world");
H.Case("counts overtake", "world", delegate { return a.GetMaxKey(); });
H.Case("min is now hello", "hello", delegate { return a.GetMinKey(); });

a.Dec("hello"); a.Dec("hello");
H.Case("key removed at zero", "world", delegate { return a.GetMinKey(); });

a.Dec("nosuchkey");
H.Case("Dec on an absent key is a no-op", "world", delegate { return a.GetMaxKey(); });

a.Dec("world"); a.Dec("world"); a.Dec("world");
H.Case("emptied again -> max \"\"", "", delegate { return a.GetMaxKey(); });
H.Case("emptied again -> min \"\"", "", delegate { return a.GetMinKey(); });

AllOne b = new AllOne();
for (int i = 0; i < 20000; i++) b.Inc("k" + (i % 500));
H.Case("20k operations still correct", true, delegate {
    return b.GetMaxKey().StartsWith("k") && b.GetMinKey().StartsWith("k"); });'''),

 _P(id='getrandom', title='Insert Delete GetRandom O(1), duplicates allowed', lesson='4.2',
    chapter='Ch 4', diff='Hard', evidence='Your list + Taro Senior Infra report',
    pattern='Dense array + index map', wrap=False,
    video='c4l2-getrandom/LinkedIn-Coding-4.2-GetRandom-Duplicates.mp4',
    statement='<p>All three operations in average O(1), duplicates allowed:</p>'
              '<p><code>Insert(val)</code> adds a value and returns whether it was newly present. '
              '<code>Remove(val)</code> removes <i>one</i> occurrence and returns whether anything '
              'was removed. <code>GetRandom()</code> returns a value where <b>every element</b> is '
              'equally likely &mdash; so with [4,4,9], 4 must come back two thirds of the time.</p>',
    hint='A hash set cannot be indexed. Keep a dense array and remove by swapping with the last element.',
    stub='''public class RandomizedCollection {

    public RandomizedCollection() {

    }

    public bool Insert(int val) {

    }

    public bool Remove(int val) {

    }

    public int GetRandom() {

    }
}''',
    harness=r'''RandomizedCollection c = new RandomizedCollection();
H.Case("first insert is new", true, delegate { return c.Insert(1); });
H.Case("duplicate insert returns false", false, delegate { return c.Insert(1); });
H.Case("different value is new", true, delegate { return c.Insert(2); });
H.Case("remove present", true, delegate { return c.Remove(1); });
H.Case("remove absent", false, delegate { return c.Remove(99); });
H.Case("one copy of 1 remains", true, delegate { return c.Remove(1); });
H.Case("and now it is gone", false, delegate { return c.Remove(1); });

RandomizedCollection d = new RandomizedCollection();
d.Insert(4); d.Insert(4); d.Insert(9);
H.CaseCheck("GetRandom is uniform over ELEMENTS", "4 about twice as often as 9", delegate {
    int fours = 0, nines = 0, other = 0;
    for (int i = 0; i < 6000; i++) {
        int v = d.GetRandom();
        if (v == 4) fours++; else if (v == 9) nines++; else other++;
    }
    if (other > 0) return "returned a value that is not in the collection";
    double ratio = (double)fours / (fours + nines);
    if (ratio < 0.60 || ratio > 0.73) return "4 came back " + Math.Round(ratio * 100) + "% of the time, expected ~67%";
    return null; });

RandomizedCollection e = new RandomizedCollection();
e.Insert(7); e.Remove(7); e.Insert(8);
H.Case("survives remove-then-insert", 8, delegate { return e.GetRandom(); });'''),

 _P(id='word-distance', title='Shortest Word Distance II', lesson='4.3', chapter='Ch 4',
    diff='Medium', evidence='Your list + LinkedIn tagged set', pattern='Precomputed index',
    wrap=False, video='c4l3-word-distance/LinkedIn-Coding-4.3-Shortest-Word-Distance.mp4',
    statement='<p>The constructor gets the word list <b>once</b>; <code>Shortest</code> is then '
              'called many times, each returning the smallest index distance between occurrences '
              'of two different words. Both words are always present.</p>'
              '<p>Make the repeated query fast.</p>',
    hint='Precompute the inputs to the answer, not the answer. Each query is then a merge of two sorted lists.',
    stub='''public class WordDistance {

    public WordDistance(string[] words) {

    }

    public int Shortest(string word1, string word2) {

    }
}''',
    harness=r'''WordDistance w = new WordDistance(new string[]{"practice","makes","perfect","coding","makes"});
H.Case("coding / practice", 3, delegate { return w.Shortest("coding", "practice"); });
H.Case("makes / coding", 1, delegate { return w.Shortest("makes", "coding"); });
H.Case("repeat query is stable", 3, delegate { return w.Shortest("coding", "practice"); });
H.Case("argument order does not matter", 1, delegate { return w.Shortest("coding", "makes"); });

WordDistance x = new WordDistance(new string[]{"a","b","a","b","a"});
H.Case("interleaved", 1, delegate { return x.Shortest("a", "b"); });

WordDistance y = new WordDistance(new string[]{"a","x","x","x","x","x","b"});
H.Case("far apart", 6, delegate { return y.Shortest("a", "b"); });

WordDistance z = new WordDistance(new string[]{"q","w"});
H.Case("two-word list", 1, delegate { return z.Shortest("q", "w"); });'''),

 _P(id='lfu', title='LFU Cache', lesson='4.4', chapter='Ch 4', diff='Hard',
    evidence='Taro Staff report (Jul 2025)', pattern='Frequency buckets of LRU lists', wrap=False,
    video='c4l4-lfu/LinkedIn-Coding-4.4-LFU-Cache.mp4',
    statement='<p>A cache with a fixed capacity where <code>Get</code> returns the value or '
              '&minus;1, and both a hit and an update count as a <b>use</b>.</p>'
              '<p>When full, evict the entry with the <b>lowest use count</b>; if several tie, '
              'evict the <b>least recently used</b> among them. Both operations O(1).</p>',
    hint='Two orderings means two structures, nested: frequency buckets, each holding an LRU list.',
    stub='''public class LFUCache {

    public LFUCache(int capacity) {

    }

    public int Get(int key) {

    }

    public void Put(int key, int value) {

    }
}''',
    harness=r'''LFUCache c = new LFUCache(2);
c.Put(1, 1); c.Put(2, 2);
H.Case("get 1", 1, delegate { return c.Get(1); });
c.Put(3, 3);                                  // evicts 2: count 1, and least recent among ties
H.Case("2 was evicted", -1, delegate { return c.Get(2); });
H.Case("3 is present", 3, delegate { return c.Get(3); });
c.Put(4, 4);                                  // 1 and 3 both at count 2; 1 is older
H.Case("1 was evicted on the tie", -1, delegate { return c.Get(1); });
H.Case("3 survives", 3, delegate { return c.Get(3); });
H.Case("4 is present", 4, delegate { return c.Get(4); });

LFUCache z = new LFUCache(0);
z.Put(1, 1);
H.Case("capacity 0 stores nothing", -1, delegate { return z.Get(1); });

LFUCache u = new LFUCache(2);
u.Put(1, 1); u.Put(2, 2);
u.Put(1, 10);                                  // an update is ALSO a use
u.Put(3, 3);                                   // so 2 should go, not 1
H.Case("update counts as a use", 10, delegate { return u.Get(1); });
H.Case("2 evicted after the update", -1, delegate { return u.Get(2); });

LFUCache m = new LFUCache(3);
m.Put(1, 1); m.Put(2, 2); m.Put(3, 3);
m.Get(1); m.Get(1); m.Get(2);
m.Put(4, 4);                                   // 3 has the lowest count
H.Case("lowest count evicted", -1, delegate { return m.Get(3); });
H.Case("busiest key survives", 1, delegate { return m.Get(1); });'''),

 _P(id='booths', title='Booths — maximise the experience factor', lesson='6.2', chapter='Ch 6',
    diff='Hard', evidence='Your list, first-hand', pattern='Prefix sums · fixed window',
    video='c6l2-booths/LinkedIn-Coding-6.2-Booths-Experience-Factor.mp4',
    statement='<p>A row of booths, each holding some drones and some robots. The experience factor '
              'of a range is <b>(drones in it) &times; (robots in it)</b>.</p>'
              '<p>The original question was ambiguous &mdash; the lesson is about naming that. Here '
              'is the well-defined version: return the largest factor over any range of '
              '<b>exactly k</b> consecutive booths.</p>',
    hint='Slide a window of width k over both quantities at once. And the product overflows int.',
    stub='public long BestOfWidth(int[] drones, int[] robots, int k) {\n    \n}',
    harness=r'''H.Case("k=2 (3x5 and 5x3)", 15L, delegate { return new Solution().BestOfWidth(
    new int[]{1,2,3}, new int[]{3,2,1}, 2); });
H.Case("k=1 (best single booth)", 4L, delegate { return new Solution().BestOfWidth(
    new int[]{1,2,3}, new int[]{3,2,1}, 1); });
H.Case("whole row", 36L, delegate { return new Solution().BestOfWidth(
    new int[]{1,2,3}, new int[]{3,2,1}, 3); });
H.Case("zeros give zero", 0L, delegate { return new Solution().BestOfWidth(
    new int[]{5,0,5}, new int[]{0,5,0}, 1); });
H.Case("pairing matters", 25L, delegate { return new Solution().BestOfWidth(
    new int[]{5,0,5}, new int[]{0,5,0}, 2); });
H.Case("overflows int", 1000000000000L, delegate { return new Solution().BestOfWidth(
    new int[]{1000000}, new int[]{1000000}, 1); });'''),

 _P(id='celebrity', title='Find the Celebrity', lesson='7.2', chapter='Ch 7', diff='Medium',
    evidence='Your list + a Taro DSA-round report', pattern='Elimination', wrap=False,
    types=RELATION, video='c7l2-celebrity/LinkedIn-Coding-7.2-Find-The-Celebrity.mp4',
    statement='<p>Among n people there may be one celebrity: known by <b>everyone else</b>, and '
              'knowing <b>nobody</b>. You may only call <code>Knows(a, b)</code>, and calls are '
              'expensive. Return the celebrity, or &minus;1 if there is none.</p>'
              '<p>The tests also check your <b>call count</b> &mdash; a quadratic solution fails '
              'the last case even though it returns the right answer.</p>',
    hint='Every call eliminates exactly one candidate, whichever way it answers. Then verify the survivor.',
    stub='''public class Solution : Relation {

    public int FindCelebrity(int n) {

    }
}''',
    harness=r'''// Knows[a, b] - person 2 is the celebrity here
bool[,] m1 = new bool[,] {
    { false, true,  true  },
    { false, false, true  },
    { false, false, false } };
Relation.Setup(m1);
H.Case("finds the celebrity", 2, delegate { return new Solution().FindCelebrity(3); });

// nobody qualifies: 2 knows 0
bool[,] m2 = new bool[,] {
    { false, true,  true  },
    { false, false, true  },
    { true,  false, false } };
Relation.Setup(m2);
H.Case("no celebrity", -1, delegate { return new Solution().FindCelebrity(3); });

// someone is known by all but also knows someone
bool[,] m3 = new bool[,] {
    { false, true  },
    { true,  false } };
Relation.Setup(m3);
H.Case("mutual acquaintance is not a celebrity", -1, delegate {
    return new Solution().FindCelebrity(2); });

bool[,] m4 = new bool[,] { { false } };
Relation.Setup(m4);
H.Case("single person is the celebrity", 0, delegate { return new Solution().FindCelebrity(1); });

// 200 people, celebrity at 137 - checks that you did not write the O(n^2) version
int n5 = 200, star = 137;
bool[,] m5 = new bool[n5, n5];
for (int i = 0; i < n5; i++) for (int j = 0; j < n5; j++) m5[i, j] = (i != j && j == star);
Relation.Setup(m5);
H.CaseCheck("uses O(n) calls, not O(n^2)", "under 3n calls", delegate {
    int got = new Solution().FindCelebrity(n5);
    if (got != star) return "wrong answer: " + got;
    if (Relation.Calls > 3 * n5) return Relation.Calls + " calls for n=" + n5 + " (limit " + (3 * n5) + ")";
    return null; });'''),

 _P(id='threadsafe-lfu', title='Make it thread-safe', lesson='9.1', chapter='Ch 9', diff='Hard',
    evidence='Glassdoor phone screen + a repeated follow-up', pattern='Concurrency', wrap=False,
    video='c9l1-threadsafe/LinkedIn-Coding-9.1-Make-It-Thread-Safe.mp4',
    statement='<p>The reported pivot: you have just finished a cache, and the interviewer says '
              '<i>"now make it thread-safe."</i></p>'
              '<p>Implement a small counter cache that is correct under concurrent use. '
              '<code>Add(key)</code> increments a key, <code>Get(key)</code> reads it, and '
              '<code>Total()</code> returns the sum of all counts &mdash; which must never observe '
              'a half-finished update.</p>',
    hint='Name the invariant before reaching for a primitive. A concurrent collection makes each ACCESS atomic, not each OPERATION.',
    stub='''public class SafeCounters {

    public void Add(string key) {

    }

    public int Get(string key) {

    }

    public int Total() {

    }
}''',
    harness=r'''SafeCounters c = new SafeCounters();
c.Add("a"); c.Add("a"); c.Add("b");
H.Case("counts a key", 2, delegate { return c.Get("a"); });
H.Case("unknown key reads 0", 0, delegate { return c.Get("zzz"); });
H.Case("total", 3, delegate { return c.Total(); });

H.CaseCheck("8 threads x 5000 increments", "exactly 40000, no exceptions", delegate {
    SafeCounters s = new SafeCounters();
    System.Threading.Tasks.Task[] ts = new System.Threading.Tasks.Task[8];
    Exception failure = null;
    for (int t = 0; t < 8; t++) {
        ts[t] = System.Threading.Tasks.Task.Run(delegate {
            try { for (int i = 0; i < 5000; i++) s.Add("shared"); }
            catch (Exception ex) { failure = ex; }
        });
    }
    System.Threading.Tasks.Task.WaitAll(ts);
    if (failure != null) return "threw " + failure.GetType().Name;
    int got = s.Get("shared");
    if (got != 40000) return "lost updates: got " + got + " of 40000";
    return null; });

H.CaseCheck("readers never see a torn total", "no exception, total stays consistent", delegate {
    SafeCounters s = new SafeCounters();
    Exception failure = null;
    System.Threading.Tasks.Task w = System.Threading.Tasks.Task.Run(delegate {
        try { for (int i = 0; i < 20000; i++) s.Add("k" + (i % 50)); }
        catch (Exception ex) { failure = ex; }
    });
    System.Threading.Tasks.Task r = System.Threading.Tasks.Task.Run(delegate {
        try { for (int i = 0; i < 20000; i++) { int t = s.Total(); if (t < 0) throw new Exception("negative total"); } }
        catch (Exception ex) { failure = ex; }
    });
    System.Threading.Tasks.Task.WaitAll(w, r);
    if (failure != null) return "threw " + failure.GetType().Name + ": " + failure.Message;
    if (s.Total() != 20000) return "final total " + s.Total() + ", expected 20000";
    return null; });

H.CaseCheck("note", "this is a smoke test, not a proof", delegate {
    return null; });'''),
]
