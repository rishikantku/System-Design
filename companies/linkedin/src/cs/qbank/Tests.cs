using System.Diagnostics;

static class T {
    static int pass = 0, fail = 0;
    public static void Eq<TV>(string what, TV got, TV want) {
        bool ok = EqualityComparer<TV>.Default.Equals(got, want);
        if (ok) { pass++; }
        else { fail++; Console.WriteLine($"  FAIL {what}: got {got}, want {want}"); }
    }
    public static void True(string what, bool cond) { Eq(what, cond, true); }
    public static void Seq(string what, IEnumerable<int> got, params int[] want) {
        var g = got.ToArray();
        bool ok = g.Length == want.Length && g.Zip(want).All(p => p.First == p.Second);
        if (ok) pass++;
        else { fail++; Console.WriteLine($"  FAIL {what}: got [{string.Join(",", g)}], want [{string.Join(",", want)}]"); }
    }
    public static void Section(string s) => Console.WriteLine($"--- {s}");
    public static int Report() {
        Console.WriteLine($"\n{pass} passed, {fail} failed");
        return fail == 0 ? 0 : 1;
    }
}

class Program {
    static int Main() {
        Q1(); Q2(); Q3(); Q4(); Q5(); Q6(); Q7(); Q8(); Q9();
        Q10(); Q11(); Q12(); Q13(); Q14(); Q15(); Q16(); Q17();
        return T.Report();
    }

    // ---------------------------------------------------------------- Q1
    static void Q1() {
        T.Section("Q1 LRU + TTL");
        long now = 0;
        var c = new LruTtlCache(2, () => now);
        c.Put(1, 100, 10);
        c.Put(2, 200, 10);
        T.Eq("get 1 live", c.Get(1), 100);
        now = 9;
        T.Eq("get 2 at t=9 still live", c.Get(2), 200);
        now = 10;
        T.Eq("get 1 expired at exactly ttl", c.Get(1), -1);
        T.Eq("count drops after lazy reclaim", c.Count, 1);
        T.Eq("get 2 also expired", c.Get(2), -1);
        T.Eq("empty now", c.Count, 0);

        // eviction order is LRU, not insertion order
        now = 0;
        var d = new LruTtlCache(2, () => now);
        d.Put(1, 1, 1000); d.Put(2, 2, 1000);
        d.Get(1);                       // 1 becomes most recent, so 2 is the victim
        d.Put(3, 3, 1000);
        T.Eq("1 survives", d.Get(1), 1);
        T.Eq("2 evicted", d.Get(2), -1);
        T.Eq("3 present", d.Get(3), 3);

        // re-put renews the TTL
        now = 0;
        var e = new LruTtlCache(2, () => now);
        e.Put(7, 70, 10);
        now = 8; e.Put(7, 71, 10);      // expires at 18 now
        now = 17;
        T.Eq("renewed by re-put", e.Get(7), 71);
        now = 18;
        T.Eq("renewed then expires", e.Get(7), -1);

        // sweeper
        now = 0;
        var s = new SweptLruTtlCache(10, () => now);
        for (int i = 0; i < 5; i++) s.Put(i, i, 10);
        s.Put(99, 99, 1000);
        now = 10;
        T.Eq("sweep budget respected", s.Sweep(3), 3);
        T.Eq("count after partial sweep", s.Count, 3);
        T.Eq("sweep the rest", s.Sweep(100), 2);
        T.Eq("live entry survives sweep", s.Get(99), 99);
        // stale heap entry must not remove a renewed key
        now = 0;
        var s2 = new SweptLruTtlCache(10, () => now);
        s2.Put(5, 50, 10);
        now = 5; s2.Put(5, 51, 100);    // now expires at 105; heap still holds the t=10 record
        now = 10;
        T.Eq("stale expiry ignored", s2.Sweep(100), 0);
        T.Eq("renewed key survives", s2.Get(5), 51);
    }

    // ---------------------------------------------------------------- Q2
    static void Q2() {
        T.Section("Q2 bipartite");
        var a = new Dictionary<int, List<int>> { [1] = new() { 2 }, [3] = new() { 1, 2 } };
        T.Eq("stated example 1 -> invalid", AnimalGrouping.CanSplit(a), false);

        var b = new Dictionary<int, List<int>> { [1] = new() { 2 }, [2] = new() { 1, 3 } };
        T.Eq("stated example 2 -> valid", AnimalGrouping.CanSplit(b), true);

        T.Eq("empty", AnimalGrouping.CanSplit(new Dictionary<int, List<int>>()), true);
        T.Eq("null", AnimalGrouping.CanSplit(null), true);
        T.Eq("self conflict", AnimalGrouping.CanSplit(new Dictionary<int, List<int>> { [1] = new() { 1 } }), false);
        T.Eq("no conflicts at all", AnimalGrouping.CanSplit(new Dictionary<int, List<int>> { [1] = new(), [2] = new() }), true);

        // even cycle is fine, odd cycle is not
        var even4 = new Dictionary<int, List<int>> { [1] = new() { 2 }, [2] = new() { 3 }, [3] = new() { 4 }, [4] = new() { 1 } };
        T.Eq("4-cycle valid", AnimalGrouping.CanSplit(even4), true);
        var odd5 = new Dictionary<int, List<int>> { [1] = new() { 2 }, [2] = new() { 3 }, [3] = new() { 4 }, [4] = new() { 5 }, [5] = new() { 1 } };
        T.Eq("5-cycle invalid", AnimalGrouping.CanSplit(odd5), false);

        // two components, second one bad
        var comps = new Dictionary<int, List<int>> {
            [1] = new() { 2 }, [10] = new() { 11 }, [11] = new() { 12 }, [12] = new() { 10 } };
        T.Eq("bad second component caught", AnimalGrouping.CanSplit(comps), false);

        // one-way declaration still symmetric
        var oneWay = new Dictionary<int, List<int>> { [1] = new() { 2, 3 }, [2] = new() { 3 } };
        T.Eq("one-way declared triangle invalid", AnimalGrouping.CanSplit(oneWay), false);

        var (l, r) = AnimalGrouping.Split(b);
        T.Seq("split left", l, 1, 3);
        T.Seq("split right", r, 2);
    }

    // ---------------------------------------------------------------- Q3
    static void Q3() {
        T.Section("Q3 artificial island");
        T.Eq("basic", ArtificialIsland.MaxIsland(new[] { 1, 0, 0, 1, 1, 0, 1 }, 1), 4);
        T.Eq("k=0 longest run", ArtificialIsland.MaxIsland(new[] { 1, 1, 0, 1 }, 0), 2);
        T.Eq("all ocean, k covers it", ArtificialIsland.MaxIsland(new[] { 0, 0, 0 }, 3), 3);
        T.Eq("all ocean, k short", ArtificialIsland.MaxIsland(new[] { 0, 0, 0 }, 2), 2);
        T.Eq("all land", ArtificialIsland.MaxIsland(new[] { 1, 1, 1 }, 0), 3);
        T.Eq("empty", ArtificialIsland.MaxIsland(new int[0], 5), 0);
        T.Eq("single ocean no material", ArtificialIsland.MaxIsland(new[] { 0 }, 0), 0);
        T.Eq("k larger than array", ArtificialIsland.MaxIsland(new[] { 0, 1, 0 }, 99), 3);

        T.Eq("circular wraps", ArtificialIsland.MaxIslandCircular(new[] { 1, 0, 0, 0, 1 }, 1), 3);
        T.Eq("circular capped at n", ArtificialIsland.MaxIslandCircular(new[] { 1, 0, 1 }, 1), 3);
        T.Eq("circular whole ring affordable", ArtificialIsland.MaxIslandCircular(new[] { 0, 0 }, 2), 2);
        T.Eq("circular uses the wrap", ArtificialIsland.MaxIslandCircular(new[] { 1, 1, 0, 0, 0, 1 }, 1), 4);

        T.Eq("obstacle splits", ArtificialIsland.MaxIslandWithObstacles(new[] { 1, 0, 1, -1, 1, 0, 1, 1 }, 1), 4);
        T.Eq("obstacle blocks everything", ArtificialIsland.MaxIslandWithObstacles(new[] { -1, -1 }, 5), 0);
        T.Eq("obstacle at ends", ArtificialIsland.MaxIslandWithObstacles(new[] { -1, 1, 0, 1, -1 }, 1), 3);

        var cells = new[] { 1, 0, 0, 1 };
        var cost  = new[] { 0, 5, 1, 0 };
        T.Eq("weighted budget 1", ArtificialIsland.MaxIslandWeighted(cells, cost, 1), 2);
        T.Eq("weighted budget 6", ArtificialIsland.MaxIslandWeighted(cells, cost, 6), 4);
        T.Eq("weighted budget 0", ArtificialIsland.MaxIslandWeighted(cells, cost, 0), 1);

        // brute-force cross-check for all four variants
        var rnd3 = new Random(808);
        bool allOk = true;
        for (int trial = 0; trial < 3000 && allOk; trial++) {
            int n = 1 + rnd3.Next(10);
            var a  = new int[n];
            var cw = new int[n];
            for (int i = 0; i < n; i++) { a[i] = rnd3.Next(2); cw[i] = rnd3.Next(1, 5); }
            int k = rnd3.Next(0, 4);

            if (ArtificialIsland.MaxIsland(a, k) != BruteLinear(a, k)) { allOk = false; Console.WriteLine("  linear mismatch [" + string.Join(",", a) + "] k=" + k); }
            if (ArtificialIsland.MaxIslandCircular(a, k) != BruteCircular(a, k)) { allOk = false; Console.WriteLine("  circular mismatch [" + string.Join(",", a) + "] k=" + k); }
            if (ArtificialIsland.MaxIslandWeighted(a, cw, k) != BruteWeighted(a, cw, k)) { allOk = false; Console.WriteLine("  weighted mismatch [" + string.Join(",", a) + "] budget=" + k); }

            var withObs = (int[])a.Clone();
            for (int i = 0; i < n; i++) if (rnd3.Next(5) == 0) withObs[i] = -1;
            if (ArtificialIsland.MaxIslandWithObstacles(withObs, k) != BruteObstacles(withObs, k)) { allOk = false; Console.WriteLine("  obstacle mismatch [" + string.Join(",", withObs) + "] k=" + k); }
        }
        T.True("3000 random trials match brute force across all four variants", allOk);
    }

    static int BruteLinear(int[] a, int k) {
        int best = 0;
        for (int i = 0; i < a.Length; i++)
            for (int j = i; j < a.Length; j++) {
                int z = 0; for (int t = i; t <= j; t++) if (a[t] == 0) z++;
                if (z <= k) best = Math.Max(best, j - i + 1);
            }
        return best;
    }
    static int BruteCircular(int[] a, int k) {
        int n = a.Length, best = 0;
        for (int i = 0; i < n; i++)
            for (int len = 1; len <= n; len++) {
                int z = 0; for (int t = 0; t < len; t++) if (a[(i + t) % n] == 0) z++;
                if (z <= k) best = Math.Max(best, len);
            }
        return best;
    }
    static int BruteWeighted(int[] a, int[] cost, int budget) {
        int best = 0;
        for (int i = 0; i < a.Length; i++)
            for (int j = i; j < a.Length; j++) {
                long c = 0; for (int t = i; t <= j; t++) if (a[t] == 0) c += cost[t];
                if (c <= budget) best = Math.Max(best, j - i + 1);
            }
        return best;
    }
    static int BruteObstacles(int[] a, int k) {
        int best = 0;
        for (int i = 0; i < a.Length; i++)
            for (int j = i; j < a.Length; j++) {
                int z = 0; bool blocked = false;
                for (int t = i; t <= j; t++) { if (a[t] == -1) blocked = true; else if (a[t] == 0) z++; }
                if (!blocked && z <= k) best = Math.Max(best, j - i + 1);
            }
        return best;
    }

    // ---------------------------------------------------------------- Q4
    static void Q4() {
        T.Section("Q4 biased -> uniform");
        foreach (double p in new[] { 0.5, 0.2, 0.9, 0.05 }) {
            var rng = new Random(12345);
            var g = new UniformFromBiased(() => rng.NextDouble() < p ? 0 : 1);

            int n = 700_000;
            var counts = new int[7];
            for (int i = 0; i < n; i++) counts[g.Next0To6()]++;

            double expected = n / 7.0;
            double chi = counts.Sum(c => (c - expected) * (c - expected) / expected);
            // 6 degrees of freedom: chi-square above ~24.1 is a 1-in-1000 event.
            T.True($"p={p} uniform (chi2={chi:F1})", chi < 24.1);
            T.True($"p={p} all values seen", counts.All(c => c > 0));
            double callsPerDraw = g.BiasedCalls / (double)n;
            double predicted = 24.0 / (7.0 * p * (1 - p));
            T.True($"p={p} cost ~24/(7p(1-p)): got {callsPerDraw:F2} predicted {predicted:F2}",
                   Math.Abs(callsPerDraw - predicted) / predicted < 0.05);
        }
    }

    // ---------------------------------------------------------------- Q5
    class M : IMember {
        readonly int _id; public List<IMember> C = new();
        public M(int id) { _id = id; }
        public int GetMemberId() => _id;
        public IList<IMember> GetConnections() => C;
    }
    static void Link(M a, M b) { a.C.Add(b); b.C.Add(a); }

    static void Q5() {
        T.Section("Q5 connection distance");
        var bob = new M(1); var alice = new M(2); var frank = new M(3); var zoe = new M(4);
        Link(bob, alice); Link(alice, frank);

        T.Eq("stated example bob->frank", ConnectionDistance.Distance(bob, frank), 2);
        T.Eq("bidirectional agrees", ConnectionDistance.DistanceBidirectional(bob, frank), 2);
        T.Eq("adjacent", ConnectionDistance.Distance(bob, alice), 1);
        T.Eq("self", ConnectionDistance.Distance(bob, bob), 0);
        T.Eq("unreachable", ConnectionDistance.Distance(bob, zoe), -1);
        T.Eq("unreachable bidi", ConnectionDistance.DistanceBidirectional(bob, zoe), -1);
        T.Eq("null", ConnectionDistance.Distance(null, bob), -1);

        // random graph: both implementations must agree everywhere
        var rnd = new Random(7);
        var nodes = Enumerable.Range(0, 60).Select(i => new M(i)).ToArray();
        for (int i = 1; i < nodes.Length; i++) Link(nodes[i], nodes[rnd.Next(i)]);   // a tree, so connected
        for (int i = 0; i < 120; i++) {
            var x = nodes[rnd.Next(nodes.Length)]; var y = nodes[rnd.Next(nodes.Length)];
            int a = ConnectionDistance.Distance(x, y);
            int b = ConnectionDistance.DistanceBidirectional(x, y);
            if (a != b) { T.Eq($"agree {x.GetMemberId()}->{y.GetMemberId()}", b, a); return; }
        }
        T.True("bfs and bidirectional agree on 120 random pairs", true);

        // lopsided: one hub with 5000 connections
        var hub = new M(9000); var tiny = new M(9001);
        for (int i = 0; i < 5000; i++) Link(hub, new M(10_000 + i));
        Link(tiny, (M)hub.C[2500]);
        T.Eq("lopsided distance", ConnectionDistance.DistanceBidirectional(tiny, hub), 2);
    }

    // ---------------------------------------------------------------- Q6
    static void Q6() {
        T.Section("Q6 parentheses");
        T.Eq("()()()()", ParenCheck.IsBalanced("()()()()"), true);
        T.Eq("((45+)*a3)", ParenCheck.IsBalanced("((45+)*a3)"), true);
        T.Eq("empty", ParenCheck.IsBalanced(""), true);
        T.Eq("null", ParenCheck.IsBalanced(null), true);
        T.Eq("no parens", ParenCheck.IsBalanced("abc123"), true);
        T.Eq("close first", ParenCheck.IsBalanced(")("), false);
        T.Eq("unclosed", ParenCheck.IsBalanced("(()"), false);
        T.Eq("extra close", ParenCheck.IsBalanced("())"), false);
        T.Eq("single open", ParenCheck.IsBalanced("("), false);
        T.Eq("nested deep", ParenCheck.IsBalanced("((((a))))"), true);
        T.Eq("multi-type ([)] rejected", ParenCheck.IsBalancedMultiType("([)]"), false);
        T.Eq("multi-type ([]) ok", ParenCheck.IsBalancedMultiType("([])"), true);
        T.Eq("counter says yes to ([)]", ParenCheck.IsBalanced("([)]"), true);   // documents the limit
    }

    // ---------------------------------------------------------------- Q7
    static void Q7() {
        T.Section("Q7 delay scheduler");
        using var s = new DelayScheduler();
        var order = new List<string>();
        object gate = new();
        void Rec(string n) { lock (gate) order.Add(n); }

        s.Schedule(() => Rec("A-150"), TimeSpan.FromMilliseconds(150));
        s.Schedule(() => Rec("B-40"),  TimeSpan.FromMilliseconds(40));
        s.Schedule(() => Rec("C-90"),  TimeSpan.FromMilliseconds(90));
        Thread.Sleep(350);
        lock (gate) T.True("ran in deadline order, not submission order: " + string.Join(",", order),
                           order.SequenceEqual(new[] { "B-40", "C-90", "A-150" }));

        // an earlier task scheduled while the worker sleeps must still be on time
        var s2 = new DelayScheduler();
        var hits = new List<string>();
        s2.Schedule(() => { lock (gate) hits.Add("late"); }, TimeSpan.FromMilliseconds(400));
        Thread.Sleep(30);
        s2.Schedule(() => { lock (gate) hits.Add("early"); }, TimeSpan.FromMilliseconds(30));
        Thread.Sleep(150);
        lock (gate) T.True("late sleeper woken for an earlier task: " + string.Join(",", hits),
                           hits.SequenceEqual(new[] { "early" }));
        s2.Shutdown(drainPending: false);

        // cancellation
        var s3 = new DelayScheduler();
        int ran = 0;
        var h = s3.Schedule(() => Interlocked.Increment(ref ran), TimeSpan.FromMilliseconds(120));
        T.Eq("cancel succeeds", h.Cancel(), true);
        T.Eq("second cancel is a no-op", h.Cancel(), false);
        Thread.Sleep(220);
        T.Eq("cancelled task did not run", Volatile.Read(ref ran), 0);

        // a throwing task must not kill the worker
        int after = 0;
        s3.Schedule(() => throw new InvalidOperationException("boom"), TimeSpan.Zero);
        Thread.Sleep(40);
        s3.Schedule(() => Interlocked.Increment(ref after), TimeSpan.FromMilliseconds(20));
        Thread.Sleep(150);
        T.Eq("worker survived a throwing task", Volatile.Read(ref after), 1);

        // shutdown rejects new work, and drains what is pending
        int drained = 0;
        var s4 = new DelayScheduler();
        s4.Schedule(() => Interlocked.Increment(ref drained), TimeSpan.FromMilliseconds(30));
        s4.Shutdown(drainPending: true);
        bool threw = false;
        try { s4.Schedule(() => { }, TimeSpan.Zero); } catch (InvalidOperationException) { threw = true; }
        T.Eq("schedule after shutdown throws", threw, true);
        T.Eq("terminated", s4.AwaitTermination(TimeSpan.FromSeconds(2)), true);
        T.Eq("pending task drained", Volatile.Read(ref drained), 1);

        // load: 500 tasks, every one runs exactly once
        var s5 = new DelayScheduler();
        int count = 0;
        for (int i = 0; i < 500; i++) s5.Schedule(() => Interlocked.Increment(ref count), TimeSpan.FromMilliseconds(i % 50));
        Thread.Sleep(400);
        T.Eq("500 tasks each ran once", Volatile.Read(ref count), 500);
        s5.Shutdown(false);
        s3.Shutdown(false);
    }

    // ---------------------------------------------------------------- Q8
    static void Q8() {
        T.Section("Q8 word transformation");
        var dict = new[] { "APE", "APT", "OPT", "OAT", "MAT", "MAN", "OPE", "CAT", "COT" };
        var w = new WordTransformer(dict);
        T.Eq("stated example APE->MAN", w.MinTransformations("APE", "MAN"), 5);
        T.Eq("bidirectional agrees", w.MinTransformationsBidirectional("APE", "MAN"), 5);
        T.Eq("same word", w.MinTransformations("APE", "APE"), 0);
        T.Eq("one step", w.MinTransformations("APE", "APT"), 1);
        T.Eq("target not in dictionary", w.MinTransformations("APE", "ZZZ"), -1);
        T.Eq("different length", w.MinTransformations("APE", "APES"), -1);

        var isolated = new WordTransformer(new[] { "AAA", "AAB", "XXX" });
        T.Eq("unreachable", isolated.MinTransformations("AAA", "XXX"), -1);
        T.Eq("unreachable bidi", isolated.MinTransformationsBidirectional("AAA", "XXX"), -1);

        var dyn = new WordTransformer(new[] { "AAA", "XXX" });
        T.Eq("before adding words", dyn.MinTransformations("AAA", "XXX"), -1);
        dyn.AddWord("XAA"); dyn.AddWord("XXA");
        T.Eq("after adding words", dyn.MinTransformations("AAA", "XXX"), 3);

        // LeetCode 127 counts WORDS; this counts EDGES. hit->cog is 5 words / 4 edges.
        var lc = new WordTransformer(new[] { "hot", "dot", "dog", "lot", "log", "cog" });
        T.Eq("LC127 hit->cog is 4 edges (LeetCode reports 5)", lc.MinTransformations("hit", "cog"), 4);

        // both implementations agree on random pairs
        var rnd = new Random(99);
        var words = new HashSet<string>();
        while (words.Count < 250) {
            var cs = new char[4];
            for (int i = 0; i < 4; i++) cs[i] = (char)('a' + rnd.Next(4));
            words.Add(new string(cs));
        }
        var big = new WordTransformer(words);
        var arr = words.ToArray();
        bool agree = true;
        for (int i = 0; i < 200; i++) {
            string x = arr[rnd.Next(arr.Length)], y = arr[rnd.Next(arr.Length)];
            if (big.MinTransformations(x, y) != big.MinTransformationsBidirectional(x, y)) { agree = false; break; }
        }
        T.True("bfs and bidirectional agree on 200 random pairs", agree);
    }

    // ---------------------------------------------------------------- Q9
    static void Q9() {
        T.Section("Q9 covered size");
        var t = new CoveredIntervals();
        T.Eq("empty", t.GetCoveredSize(), 0L);
        t.AddInterval(1, 5);
        T.Eq("one interval", t.GetCoveredSize(), 4L);
        t.AddInterval(10, 12);
        T.Eq("disjoint adds", t.GetCoveredSize(), 6L);
        t.AddInterval(3, 11);                       // bridges both
        T.Eq("bridging merge", t.GetCoveredSize(), 11L);
        T.Eq("collapsed to one interval", t.IntervalCount, 1);
        t.AddInterval(2, 4);                        // fully inside
        T.Eq("contained interval adds nothing", t.GetCoveredSize(), 11L);
        t.AddInterval(1, 12);                       // exactly the same span
        T.Eq("duplicate adds nothing", t.GetCoveredSize(), 11L);
        t.AddInterval(12, 15);                      // adjacent, half-open so it coalesces
        T.Eq("adjacent coalesces", t.GetCoveredSize(), 14L);
        T.Eq("still one interval", t.IntervalCount, 1);
        t.AddInterval(7, 7);
        T.Eq("empty interval ignored", t.GetCoveredSize(), 14L);
        t.AddInterval(9, 3);
        T.Eq("reversed interval ignored", t.GetCoveredSize(), 14L);

        // negative coordinates
        var n = new CoveredIntervals();
        n.AddInterval(-10, -5);
        n.AddInterval(-7, 3);
        T.Eq("negative range", n.GetCoveredSize(), 13L);

        // brute-force cross-check on random input
        var rnd = new Random(2024);
        for (int trial = 0; trial < 300; trial++) {
            var st = new CoveredIntervals();
            var marked = new bool[200];
            for (int i = 0; i < 25; i++) {
                int a = rnd.Next(0, 200), b = a + rnd.Next(0, 20);
                b = Math.Min(b, 200);
                st.AddInterval(a, b);
                for (int x = a; x < b; x++) marked[x] = true;
            }
            long want = marked.Count(x => x);
            if (st.GetCoveredSize() != want) { T.Eq($"trial {trial}", st.GetCoveredSize(), want); return; }
            // the stored set must stay disjoint and sorted
            var snap = st.Snapshot();
            for (int i = 1; i < snap.Count; i++)
                if (snap[i - 1].End >= snap[i].Start) { T.True($"trial {trial} disjoint", false); return; }
        }
        T.True("300 random trials match a brute-force bitmap, set stays disjoint", true);
    }

    // ---------------------------------------------------------------- Q10
    static TreeNode Build(int?[] level) {
        // level-order with nulls
        if (level.Length == 0 || level[0] == null) return null;
        var root = new TreeNode(level[0].Value);
        var q = new Queue<TreeNode>(); q.Enqueue(root);
        int i = 1;
        while (q.Count > 0 && i < level.Length) {
            var n = q.Dequeue();
            if (i < level.Length && level[i] != null) { n.Left = new TreeNode(level[i].Value); q.Enqueue(n.Left); }
            i++;
            if (i < level.Length && level[i] != null) { n.Right = new TreeNode(level[i].Value); q.Enqueue(n.Right); }
            i++;
        }
        return root;
    }

    static void Q10() {
        T.Section("Q10 leaf peeling");
        //        1
        //      2   3
        //    4  5
        var root = Build(new int?[] { 1, 2, 3, 4, 5 });
        var levels = LeafPeeling.PeelLevels(root);
        T.Eq("3 rounds", levels.Count, 3);
        T.Seq("round 1", levels[0].OrderBy(x => x), 3, 4, 5);
        T.Seq("round 2", levels[1].OrderBy(x => x), 2);
        T.Seq("round 3", levels[2].OrderBy(x => x), 1);

        T.Eq("null tree", LeafPeeling.PeelLevels(null).Count, 0);
        T.Eq("single node", LeafPeeling.PeelLevels(new TreeNode(9))[0][0], 9);

        // a right-leaning chain peels one node per round
        var chain = new TreeNode(1) { Right = new TreeNode(2) { Right = new TreeNode(3) } };
        var cl = LeafPeeling.PeelLevels(chain);
        T.Eq("chain rounds", cl.Count, 3);
        T.Seq("chain order", cl.Select(l => l[0]), 3, 2, 1);

        // mutating version must agree with the non-mutating one
        var m = Build(new int?[] { 1, 2, 3, 4, 5 });
        var rounds = LeafPeeling.PeelAndMutate(ref m);
        T.Eq("tree destroyed", m, null);
        T.Eq("same round count", rounds.Count, 3);
        T.Seq("mutating round 1", rounds[0].OrderBy(x => x), 3, 4, 5);
        T.Seq("mutating round 3", rounds[2].OrderBy(x => x), 1);

        // n-ary
        var n1 = new NaryNode(1);
        var n2 = new NaryNode(2); var n3 = new NaryNode(3); var n4 = new NaryNode(4);
        n1.Children.Add(n2); n1.Children.Add(n3);
        n2.Children.Add(n4);
        var nl = NaryLeafPeeling.PeelLevels(n1);
        T.Eq("n-ary rounds", nl.Count, 3);
        T.Seq("n-ary round 1", nl[0].OrderBy(x => x), 3, 4);
        T.Seq("n-ary round 2", nl[1].OrderBy(x => x), 2);
        T.Seq("n-ary round 3", nl[2].OrderBy(x => x), 1);
    }

    // ---------------------------------------------------------------- Q11
    static void Q11() {
        T.Section("Q11 phone keypad");
        var known = new[] { "careers", "linkedin", "hiring", "interview", "linkedgo" };
        var kd = new KeypadDictionary(known);

        T.Eq("careers signature", KeypadDictionary.Signature("careers"), "2273377");
        T.Eq("linkedin signature", KeypadDictionary.Signature("linkedin"), "54653346");
        T.Eq("linkedgo signature", KeypadDictionary.Signature("linkedgo"), "54653346");
        T.Eq("hiring signature", KeypadDictionary.Signature("hiring"), "447464");
        T.Eq("interview signature", KeypadDictionary.Signature("interview"), "468378439");

        T.Seq("2273377 -> careers", kd.WordsFor("2273377").Select(w => w.Length), 7);
        T.True("2273377 is exactly [careers]", kd.WordsFor("2273377").SequenceEqual(new[] { "careers" }));
        var both = kd.WordsFor("54653346").OrderBy(x => x).ToArray();
        T.True("54653346 -> linkedin + linkedgo, in that set", both.SequenceEqual(new[] { "linkedgo", "linkedin" }));
        T.Eq("unknown number", kd.WordsFor("9999999").Count, 0);
        T.Eq("empty number", kd.WordsFor("").Count, 0);
        T.Eq("prefix is not a match", kd.WordsFor("227337").Count, 0);

        var trie = new KeypadTrie();
        foreach (var w in known) trie.Add(w);
        T.True("trie exact", trie.Exact("2273377").SequenceEqual(new[] { "careers" }));
        T.Eq("trie prefix 5465 finds both", trie.WithPrefix("5465").Count, 2);
        T.Eq("trie prefix 4 finds hiring + interview", trie.WithPrefix("4").Count, 2);
        T.Eq("trie prefix 1 invalid digit", trie.WithPrefix("1").Count, 0);
        T.Eq("trie prefix nothing", trie.WithPrefix("99").Count, 0);
    }

    // ---------------------------------------------------------------- Q12
    static void Q12() {
        T.Section("Q12 random bag");
        var b = new RandomBag(seed: 42);
        T.Eq("insert new", b.Insert(5), true);
        T.Eq("insert duplicate rejected", b.Insert(5), false);
        b.Insert(6); b.Insert(7);
        T.Eq("count", b.Count, 3);
        T.Eq("remove present", b.Remove(6), true);
        T.Eq("remove absent", b.Remove(6), false);
        T.Eq("count after remove", b.Count, 2);

        // removing the last slot is the case that breaks a careless swap
        var s = new RandomBag(seed: 1);
        s.Insert(1); s.Insert(2);
        T.Eq("remove the last element", s.Remove(2), true);
        T.Eq("the other survives", s.PeekRandom(), 1);
        T.Eq("remove the only element", s.Remove(1), true);
        T.Eq("now empty", s.Count, 0);

        bool threw = false;
        try { s.RemoveRandomElement(); } catch (InvalidOperationException) { threw = true; }
        T.Eq("removing from empty throws", threw, true);

        // drain: every value comes out exactly once
        var d = new RandomBag(seed: 7);
        for (int i = 0; i < 500; i++) d.Insert(i);
        var seen = new HashSet<int>();
        while (d.Count > 0) if (!seen.Add(d.RemoveRandomElement())) { T.True("no value twice", false); return; }
        T.Eq("drained all 500 exactly once", seen.Count, 500);

        // RemoveRandom is uniform
        var counts = new int[10];
        for (int trial = 0; trial < 40_000; trial++) {
            var x = new RandomBag(seed: trial);
            for (int i = 0; i < 10; i++) x.Insert(i);
            counts[x.RemoveRandomElement()]++;
        }
        double exp = 4000, chi = counts.Sum(c => (c - exp) * (c - exp) / exp);
        T.True($"first removal uniform (chi2={chi:F1}, 9 dof)", chi < 27.9);

        // duplicates variant
        var mb = new RandomMultiBag(seed: 3);
        mb.Insert(1); mb.Insert(1); mb.Insert(2);
        T.Eq("multibag count", mb.Count, 3);
        T.Eq("remove one copy", mb.Remove(1), true);
        T.Eq("still holds the other copy", mb.Count, 2);
        T.Eq("remove second copy", mb.Remove(1), true);
        T.Eq("now gone", mb.Remove(1), false);
        var mseen = new List<int>();
        while (mb.Count > 0) mseen.Add(mb.RemoveRandomElement());
        T.Seq("multibag drained", mseen, 2);
    }

    // ---------------------------------------------------------------- Q13
    class Src : IRankedDataSource<string, int> {
        public int Calls;
        readonly Dictionary<string, int> _rank;
        public Src(Dictionary<string, int> rank) { _rank = rank; }
        public int Get(string key) { Calls++; return key.Length; }
        public int GetRank(string key) => _rank[key];
    }

    static void Q13() {
        T.Section("Q13 rank cache");
        var ranks = new Dictionary<string, int> { ["a"] = 10, ["b"] = 20, ["c"] = 30, ["d"] = 5, ["e"] = 40 };
        var src = new Src(ranks);
        var c = new RankCache<string, int>(3, src);

        c.Get("a"); c.Get("b"); c.Get("c");
        T.Eq("3 source calls", src.Calls, 3);
        T.Eq("full", c.Count, 3);
        c.Get("a");
        T.Eq("hit avoids the source", src.Calls, 3);
        T.Eq("hits", c.Hits, 1L);

        c.Get("e");                             // rank 40 beats the lowest (a, 10)
        T.Eq("lowest rank evicted", c.Contains("a"), false);
        T.Eq("high rank admitted", c.Contains("e"), true);
        T.Eq("lowest rank is now b", c.LowestRank, 20);

        c.Get("d");                             // rank 5 is below everything held
        T.Eq("weak newcomer not cached", c.Contains("d"), false);
        T.Eq("rejected counter", c.Rejected, 1L);
        T.Eq("nothing was evicted for it", c.Count, 3);
        T.True("still holds b, c, e", c.Contains("b") && c.Contains("c") && c.Contains("e"));

        // value is returned even when not admitted
        T.Eq("value still correct for a rejected key", c.Get("d"), 1);

        bool threw = false;
        try { new RankCache<string, int>(0, src); } catch (ArgumentOutOfRangeException) { threw = true; }
        T.Eq("capacity 0 rejected", threw, true);
    }

    // ---------------------------------------------------------------- Q14
    static void Q14() {
        T.Section("Q14 theatre seating");
        var row = new[] { 1, 0, 0, 0, 0, 0, 1, 0, 0 };
        T.Eq("stated row fits 3", TheatreSeating.MaxAdditional(row), 3);
        T.Eq("3 -> true", TheatreSeating.CanSeat(row, 3), true);
        T.Eq("4 -> false", TheatreSeating.CanSeat(row, 4), false);
        T.Eq("input not mutated", row[2], 0);

        T.Eq("second stated row fits 1", TheatreSeating.MaxAdditional(new[] { 1, 0, 0, 1, 0, 0, 1, 0, 0 }), 1);
        T.Eq("[0] fits 1", TheatreSeating.MaxAdditional(new[] { 0 }), 1);
        T.Eq("[1] fits 0", TheatreSeating.MaxAdditional(new[] { 1 }), 0);
        T.Eq("empty", TheatreSeating.MaxAdditional(new int[0]), 0);
        T.Eq("null", TheatreSeating.MaxAdditional(null), 0);
        T.Eq("n=0 always true", TheatreSeating.CanSeat(new[] { 1, 1 }, 0), true);
        T.Eq("all empty row of 5", TheatreSeating.MaxAdditional(new[] { 0, 0, 0, 0, 0 }), 3);
        T.Eq("all full", TheatreSeating.MaxAdditional(new[] { 1, 1, 1 }), 0);
        T.Eq("gap of one between taken", TheatreSeating.MaxAdditional(new[] { 1, 0, 1 }), 0);
        T.Eq("gap of two between taken", TheatreSeating.MaxAdditional(new[] { 1, 0, 0, 1 }), 0);
        T.Eq("gap of three between taken", TheatreSeating.MaxAdditional(new[] { 1, 0, 0, 0, 1 }), 1);

        // constant-space version must agree, on every row of length <= 12
        var rnd = new Random(5);
        for (int trial = 0; trial < 4000; trial++) {
            int n = 1 + rnd.Next(12);
            var r = new int[n];
            for (int i = 0; i < n; i++) r[i] = rnd.Next(2);
            // skip rows that are already invalid (two adjacent people)
            bool ok = true;
            for (int i = 1; i < n; i++) if (r[i] == 1 && r[i - 1] == 1) ok = false;
            if (!ok) continue;
            if (TheatreSeating.MaxAdditional(r) != TheatreSeating.MaxAdditionalNoCopy(r)) {
                T.True("O(1)-space version agrees on [" + string.Join(",", r) + "]", false); return;
            }
        }
        T.True("O(1)-space version agrees on every valid random row", true);
    }

    // ---------------------------------------------------------------- Q15
    class Tk : ITask {
        readonly string _id; public List<ITask> Subs = new();
        public Tk(string id) { _id = id; }
        public string GetId() => _id;
        public IList<ITask> GetSubTasks() => Subs;
    }

    static void Q15() {
        T.Section("Q15 task manager");
        // deploy depends on build; build depends on compile
        var compile = new Tk("compile");
        var build = new Tk("build"); build.Subs.Add(compile);
        var deploy = new Tk("deploy"); deploy.Subs.Add(build);

        var m = new TaskManager();
        m.AddTask(deploy);
        T.Eq("whole closure registered", m.TaskCount, 3);
        T.Eq("only the leaf is runnable", m.ReadyCount, 1);
        T.Eq("first poll is compile", m.PollNextTask().GetId(), "compile");
        T.Eq("nothing else runnable yet", m.PollNextTask(), null);

        m.CompleteTask("compile");
        T.Eq("build unlocked", m.PollNextTask().GetId(), "build");
        m.CompleteTask("build");
        T.Eq("deploy unlocked", m.PollNextTask().GetId(), "deploy");
        m.CompleteTask("deploy");
        T.Eq("drained", m.PollNextTask(), null);
        m.CompleteTask("deploy");           // idempotent

        // a diamond: two independent subtasks
        var leafA = new Tk("a"); var leafB = new Tk("b");
        var top = new Tk("top"); top.Subs.Add(leafA); top.Subs.Add(leafB);
        var m2 = new TaskManager();
        m2.AddTask(top);
        T.Eq("two runnable", m2.ReadyCount, 2);
        var f1 = m2.PollNextTask().GetId(); var f2 = m2.PollNextTask().GetId();
        T.True("both leaves issued", new[] { f1, f2 }.OrderBy(x => x).SequenceEqual(new[] { "a", "b" }));
        m2.CompleteTask("a");
        T.Eq("one dependency left, so nothing runnable", m2.PollNextTask(), null);
        m2.CompleteTask("b");
        T.Eq("top unlocked only after both", m2.PollNextTask().GetId(), "top");

        // a cycle inside the new material
        var x = new Tk("x"); var y = new Tk("y");
        x.Subs.Add(y); y.Subs.Add(x);
        var m3 = new TaskManager();
        bool threw = false;
        try { m3.AddTask(x); } catch (CycleException e) { threw = true; T.True("cycle reported: " + e.Message, e.Cycle.Count >= 2); }
        T.Eq("cycle throws", threw, true);
        T.Eq("manager untouched after the throw", m3.TaskCount, 0);
        T.Eq("no ready tasks after the throw", m3.ReadyCount, 0);

        // a cycle formed only by combining with what is already registered
        var p = new Tk("p"); var q = new Tk("q");
        p.Subs.Add(q);
        var m4 = new TaskManager();
        m4.AddTask(p);                       // p -> q
        T.Eq("two registered", m4.TaskCount, 2);
        var q2 = new Tk("q"); var p2 = new Tk("p");
        q2.Subs.Add(p2);                     // q -> p closes the loop
        bool threw2 = false;
        try { m4.AddTask(q2); } catch (CycleException) { threw2 = true; }
        T.Eq("cross-batch cycle caught", threw2, true);
        T.Eq("still two registered", m4.TaskCount, 2);

        // self dependency
        var selfish = new Tk("s");
        selfish.Subs.Add(selfish);
        bool threw3 = false;
        try { new TaskManager().AddTask(selfish); } catch (CycleException) { threw3 = true; }
        T.Eq("self dependency caught", threw3, true);

        // a shared subtask counted once
        var shared = new Tk("shared");
        var l = new Tk("l"); l.Subs.Add(shared);
        var r = new Tk("r"); r.Subs.Add(shared);
        var rootT = new Tk("root"); rootT.Subs.Add(l); rootT.Subs.Add(r);
        // re-adding a registered task with a NEW, acyclic dependency must take effect
        var u = new Tk("u"); var v = new Tk("v");
        var m6 = new TaskManager();
        m6.AddTask(u);
        var u2 = new Tk("u"); u2.Subs.Add(v);
        m6.AddTask(u2);                      // u now depends on v
        T.Eq("v registered", m6.TaskCount, 2);
        T.Eq("v is the runnable one", m6.PollNextTask().GetId(), "v");
        T.Eq("u is blocked by its new dependency", m6.PollNextTask(), null);
        m6.CompleteTask("v");
        T.Eq("u runnable once v is done", m6.PollNextTask().GetId(), "u");

        // but adding a dependency to a task already handed out is refused, not guessed at
        var g = new Tk("g");
        var m6b = new TaskManager();
        m6b.AddTask(g);
        T.Eq("g issued", m6b.PollNextTask().GetId(), "g");
        var g2 = new Tk("g"); g2.Subs.Add(new Tk("h"));
        bool threwIssued = false;
        try { m6b.AddTask(g2); } catch (InvalidOperationException) { threwIssued = true; }
        T.Eq("new dependency on an issued task refused", threwIssued, true);
        T.Eq("nothing registered by the refused call", m6b.TaskCount, 1);

        // a task handed out and dropped can be requeued
        var w = new Tk("w");
        var m7 = new TaskManager();
        m7.AddTask(w);
        T.Eq("issued", m7.PollNextTask().GetId(), "w");
        T.Eq("issued only once", m7.PollNextTask(), null);
        m7.RequeueTask("w");
        T.Eq("requeued", m7.PollNextTask().GetId(), "w");
        m7.CompleteTask("w");
        m7.RequeueTask("w");
        T.Eq("requeue after completion is a no-op", m7.PollNextTask(), null);

        var m5 = new TaskManager();
        m5.AddTask(rootT);
        T.Eq("shared node registered once", m5.TaskCount, 4);
        T.Eq("only shared is runnable", m5.PollNextTask().GetId(), "shared");
        m5.CompleteTask("shared");
        T.Eq("both parents unlocked", m5.ReadyCount, 2);
    }

    // ---------------------------------------------------------------- Q16
    static void Q16() {
        T.Section("Q16 tournament tree");
        //          2
        //       2     7
        //      2 5   7 9
        var root = new TreeNode(2) {
            Left  = new TreeNode(2) { Left = new TreeNode(2), Right = new TreeNode(5) },
            Right = new TreeNode(7) { Left = new TreeNode(7), Right = new TreeNode(9) }
        };
        T.Eq("second smallest", TournamentTree.SecondSmallest(root), 5);

        // the runner-up can be all the way at the top
        var r2 = new TreeNode(1) {
            Left  = new TreeNode(1) { Left = new TreeNode(1), Right = new TreeNode(50) },
            Right = new TreeNode(3) { Left = new TreeNode(3), Right = new TreeNode(4) }
        };
        T.Eq("runner-up on the far side", TournamentTree.SecondSmallest(r2), 3);

        // two leaves only
        var r3 = new TreeNode(4) { Left = new TreeNode(4), Right = new TreeNode(9) };
        T.Eq("two leaves", TournamentTree.SecondSmallest(r3), 9);

        bool threw = false;
        try { TournamentTree.SecondSmallest(new TreeNode(1)); } catch (InvalidOperationException) { threw = true; }
        T.Eq("single leaf throws", threw, true);

        // cross-check against sorting the leaves, on random tournaments
        var rnd = new Random(31);
        for (int trial = 0; trial < 500; trial++) {
            int leafCount = 1 << (1 + rnd.Next(5));
            var vals = new HashSet<int>();
            while (vals.Count < leafCount) vals.Add(rnd.Next(100_000));
            var level = vals.Select(v => new TreeNode(v)).ToList();
            var leaves = level.Select(n => n.Value).OrderBy(v => v).ToList();

            while (level.Count > 1) {
                var next = new List<TreeNode>();
                for (int i = 0; i < level.Count; i += 2) {
                    var p = new TreeNode(Math.Min(level[i].Value, level[i + 1].Value)) {
                        Left = level[i], Right = level[i + 1] };
                    next.Add(p);
                }
                level = next;
            }
            int got = TournamentTree.SecondSmallest(level[0]);
            if (got != leaves[1]) { T.Eq($"trial {trial}", got, leaves[1]); return; }
        }
        T.True("500 random tournaments match the sorted leaves", true);
    }

    // ---------------------------------------------------------------- Q17
    static MetaNode N(string k, long v, params MetaNode[] kids) {
        var n = new MetaNode(k, v);
        foreach (var c in kids) n.Children[c.Key] = c;
        return n;
    }

    static void Q17() {
        T.Section("Q17 merge metadata trees");
        //  s: root 10 { a 6 { x 2 }, b 1 }        own(root)=3
        //  t: root 12 { a 4, c 5 }
        var s = N("root", 10, N("a", 6, N("x", 2)), N("b", 1));
        var t = N("root", 12, N("a", 4), N("c", 5));

        var m = MetaTreeMerge.Merge(s, t);
        T.Eq("root summed", m.Value, 22L);
        T.Eq("three children", m.Children.Count, 3);
        T.Eq("shared child summed", m.Children["a"].Value, 10L);
        T.Eq("branch only in s carried", m.Children["b"].Value, 1L);
        T.Eq("branch only in t created", m.Children["c"].Value, 5L);
        T.Eq("grandchild survives", m.Children["a"].Children["x"].Value, 2L);
        T.Eq("inputs untouched: s", s.Value, 10L);
        T.Eq("inputs untouched: t children", t.Children.Count, 2);
        T.True("merged tree is consistent", MetaTreeMerge.IsConsistent(m, out _));
        T.Eq("own value of root", MetaTreeMerge.OwnValue(m), 22L - 10L - 1L - 5L);

        // iterative agrees with recursive
        var mi = MetaTreeMerge.MergeIterative(s, t);
        T.Eq("iterative root", mi.Value, 22L);
        T.Eq("iterative shared child", mi.Children["a"].Value, 10L);
        T.Eq("iterative grandchild", mi.Children["a"].Children["x"].Value, 2L);
        T.Eq("iterative child count", mi.Children.Count, 3);

        // self merge is safe in the pure version
        var self = MetaTreeMerge.Merge(s, s);
        T.Eq("self merge doubles", self.Value, 20L);
        T.Eq("source untouched by self merge", s.Value, 10L);
        bool threw = false;
        try { MetaTreeMerge.MergeInto(s, s); } catch (InvalidOperationException) { threw = true; }
        T.Eq("in-place self merge refused", threw, true);

        // nulls, and mismatched roots
        T.Eq("merge with null returns a copy", MetaTreeMerge.Merge(s, null).Value, 10L);
        T.True("the copy is a different object", !ReferenceEquals(MetaTreeMerge.Merge(s, null), s));
        bool threw2 = false;
        try { MetaTreeMerge.Merge(N("p", 1), N("q", 1)); } catch (ArgumentException) { threw2 = true; }
        T.Eq("different root keys rejected", threw2, true);

        // in-place merge produces the same values as the pure one
        var s2 = MetaTreeMerge.Clone(s);
        MetaTreeMerge.MergeInto(s2, t);
        T.Eq("in-place root", s2.Value, 22L);
        T.Eq("in-place child a", s2.Children["a"].Value, 10L);
        T.Eq("in-place child count", s2.Children.Count, 3);

        // side-heavy round trip
        var enc = SideHeavy.Encode(m);
        T.Eq("encoded root key", enc.Key, "root");
        T.Eq("first child is Left", enc.Left.Key, "a");
        T.Eq("second child is Left.Right", enc.Left.Right.Key, "b");
        T.Eq("third child", enc.Left.Right.Right.Key, "c");
        T.Eq("no fourth", enc.Left.Right.Right.Right, null);
        var dec = SideHeavy.Decode(enc);
        T.Eq("round trip root", dec.Value, 22L);
        T.Eq("round trip child count", dec.Children.Count, 3);
        T.Eq("round trip grandchild", dec.Children["a"].Children["x"].Value, 2L);
        T.Eq("round trip a", dec.Children["a"].Value, 10L);

        // deep tree: the recursive merge is the one that would blow up, the iterative one must not
        MetaNode deep1 = new MetaNode("n0", 1), cur1 = deep1;
        MetaNode deep2 = new MetaNode("n0", 1), cur2 = deep2;
        for (int i = 1; i < 60_000; i++) {
            var a = new MetaNode("n" + i, 1); cur1.Children[a.Key] = a; cur1 = a;
            var b = new MetaNode("n" + i, 1); cur2.Children[b.Key] = b; cur2 = b;
        }
        var deepMerged = MetaTreeMerge.MergeIterative(deep1, deep2);
        int depth = 0; var walk = deepMerged;
        while (walk != null) { depth++; walk = walk.Children.Count > 0 ? walk.Children.Values.First() : null; }
        T.Eq("iterative merge handles a 60k-deep chain", depth, 60_000);
        T.Eq("deep values summed", deepMerged.Value, 2L);
    }
}
