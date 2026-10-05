using System.Collections.Concurrent;

static class T {
    static int pass = 0, fail = 0;
    public static void Eq<TV>(string what, TV got, TV want) {
        if (EqualityComparer<TV>.Default.Equals(got, want)) pass++;
        else { fail++; Console.WriteLine($"  FAIL {what}: got {got}, want {want}"); }
    }
    public static void True(string what, bool cond) => Eq(what, cond, true);
    public static void Section(string s) => Console.WriteLine($"--- {s}");
    public static void Note(string s) => Console.WriteLine($"    note: {s}");
    public static int Report() { Console.WriteLine($"\n{pass} passed, {fail} failed"); return fail == 0 ? 0 : 1; }
}

class Program {
    static int Main() {
        Lru(); LruTtl(); SyncAndSharded(); Counting(); Lfu(); Intervals(); Records(); Queue(); MazeT(); Sampling_(); Window(); Logging();
        Review(); Debugging();
        return T.Report();
    }

    // ---------------------------------------------------------------- solutions
    static void Lru() {
        T.Section("A01 LRU");
        var c = new LruCache<int, string>(2);
        c.Put(1, "a"); c.Put(2, "b");
        c.TryGet(1, out _);                       // 1 is now most recent
        c.Put(3, "c");                            // evicts 2
        T.True("2 evicted", !c.TryGet(2, out _));
        T.True("1 kept", c.TryGet(1, out var v1) && v1 == "a");
        c.Put(1, "a2");                           // update in place, no eviction
        T.Eq("count after update", c.Count, 2);
        T.True("updated value", c.TryGet(1, out var v2) && v2 == "a2");
        var one = new LruCache<int, int>(1);
        one.Put(1, 1); one.Put(2, 2);
        T.True("capacity 1 keeps newest", one.TryGet(2, out _) && !one.TryGet(1, out _));
        bool threw = false; try { new LruCache<int, int>(0); } catch (ArgumentOutOfRangeException) { threw = true; }
        T.True("capacity 0 rejected", threw);
    }

    static void LruTtl() {
        T.Section("A01 LRU + TTL");
        var clk = new ManualClock();
        var c = new LruTtlCache<int, int>(3, clk);
        c.Put(1, 10, 100);
        clk.NowMs = 99; T.True("live at 99", c.TryGet(1, out _));
        clk.NowMs = 100; T.True("dead at exactly ttl", !c.TryGet(1, out _));
        T.Eq("reclaimed on read", c.Count, 0);

        clk.NowMs = 0;
        c.Put(1, 1, 50); c.Put(2, 2, 1000); c.Put(3, 3, 1000);
        c.TryGet(1, out _);                        // 1 is most recent but will expire first
        clk.NowMs = 60;
        T.Eq("sweep reclaims the expired one", c.SweepExpired(10), 1);
        T.Eq("two live left", c.Count, 2);

        clk.NowMs = 0;
        var d = new LruTtlCache<int, int>(2, clk);
        d.Put(1, 1, 10); d.Put(2, 2, 1000);
        d.TryGet(1, out _);                        // 2 is LRU, 1 is MRU but expiring
        clk.NowMs = 20;
        d.Put(3, 3, 1000);                         // should evict expired 1, not live 2
        T.True("expired preferred as victim", d.TryGet(2, out _));

        clk.NowMs = 0;
        var e = new LruTtlCache<int, int>(2, clk);
        e.Put(5, 1, 10); clk.NowMs = 8; e.Put(5, 2, 10); clk.NowMs = 15;
        T.True("re-put renews ttl", e.TryGet(5, out var v) && v == 2);

        // bounded sweep really is bounded
        clk.NowMs = 0;
        var f = new LruTtlCache<int, int>(1000, clk);
        for (int i = 0; i < 1000; i++) f.Put(i, i, 1);
        clk.NowMs = 5;
        T.Eq("sweep honours budget", f.SweepExpired(100), 100);
        T.Eq("rest remain until next sweep", f.Count, 900);

        clk.NowMs = 0;
        var g = new LruTtlCache<int, int>(4, clk);
        for (int i = 0; i < 4; i++) g.Put(i, i, 1000);
        g.TryGet(0, out _);                                   // 1 is now the coldest
        g.Resize(2);
        T.Eq("resize down evicts to the new capacity", g.Count, 2);
        T.True("resize keeps the hottest", g.TryGet(0, out _) && g.TryGet(3, out _) && !g.TryGet(1, out _));
        g.Resize(3); g.Put(9, 9, 1000);
        T.Eq("resize up admits more", g.Count, 3);
    }

    static void Logging() {
        T.Section("L01 logger");
        var clk = new ManualClock();
        var sink = new ListSink();
        var log = new Logger(Severity.Info, clk, 1000, sink);
        log.Log(Severity.Debug, "f", 1, "noise");
        T.Eq("phase 1: below min filtered", sink.Lines.Count, 0);
        log.Log(Severity.Warn, "f", 1, "disk");
        clk.NowMs = 10; log.Log(Severity.Warn, "f", 1, "disk");
        clk.NowMs = 20; log.Log(Severity.Warn, "f", 1, "disk");
        T.Eq("phase 3: duplicates in window suppressed", sink.Lines.Count, 1);
        clk.NowMs = 25; log.Log(Severity.Warn, "f", 2, "disk");
        T.Eq("different line number is not identical", sink.Lines.Count, 2);
        clk.NowMs = 1500; log.Log(Severity.Warn, "f", 1, "disk");
        var lines = sink.Lines;
        T.Eq("phase 4: summary + new line", lines.Count, 4);
        T.True("summary stamped with first occurrence and count", lines[2].StartsWith("0 Warn f:1 disk") && lines[2].Contains("suppressed 2"));
        clk.NowMs = 3000; log.Log(Severity.Warn, "f", 1, "disk");
        T.Eq("no summary when nothing was suppressed", sink.Lines.Count, 5);

        var many = new Logger(Severity.Info, clk, 1000, sink);
        for (int i = 0; i < 1000; i++) many.Log(Severity.Info, "g", i, "req " + i);
        clk.NowMs = 10_000;
        T.Eq("purge bounds the throttle table", many.PurgeExpired(), 1000);

        var bad = new Logger(Severity.Info, clk, 0, new ThrowingSink(), sink);
        int before = sink.Lines.Count;
        bad.Log(Severity.Error, "h", 1, "x");
        T.Eq("a throwing sink does not stop the others", sink.Lines.Count, before + 1);

        // 10,000 concurrent callers into the async logger
        var slow = new CountingSink();
        var alog = new AsyncLogger(Severity.Info, 1024, slow);
        Parallel.For(0, 10_000, new ParallelOptions { MaxDegreeOfParallelism = 32 }, i => alog.Log(Severity.Info, "m" + i));
        alog.DisposeAsync().AsTask().Wait();
        var m = alog.Metrics;
        T.Eq("every call either accepted or dropped", m.Accepted + m.Dropped, 10_000L);
        T.Eq("everything accepted was written", m.Written, m.Accepted);
        T.Eq("sink saw exactly what was written", (long)slow.N, m.Written);
        T.Note($"async logger: {m.Accepted} accepted, {m.Dropped} dropped at capacity 1024");

        var fl = new AsyncLogger(Severity.Info, 16, new ThrowingSink());
        for (int i = 0; i < 5; i++) fl.Log(Severity.Info, "x");
        fl.DisposeAsync().AsTask().Wait();
        T.Eq("sink failures counted, pump survives", fl.Metrics.SinkFailures, 5L);
    }

    static void SyncAndSharded() {
        T.Section("A01 thread-safe + sharded");
        var clk = new ManualClock();
        var c = new SyncLruTtlCache<int, int>(64, clk);
        Parallel.For(0, 8, t => {
            for (int i = 0; i < 20_000; i++) {
                int k = (i * 7 + t) % 200;
                if (i % 3 == 0) c.Put(k, k, 1_000_000); else c.TryGet(k, out _);
            }
        });
        T.True("never exceeds capacity under contention", c.Count <= 64);
        bool allConsistent = true;
        for (int k = 0; k < 200; k++) if (c.TryGet(k, out var v) && v != k) allConsistent = false;
        T.True("no torn values", allConsistent);

        var s = new ShardedLruTtlCache<int, int>(64, 8, clk);
        Parallel.For(0, 8, t => { for (int i = 0; i < 10_000; i++) s.Put(i % 500, i % 500, 1_000_000); });
        T.True("sharded bounded by total capacity", s.Count <= 64);
    }

    static void Counting() {
        T.Section("A02 counting LRU — predictions");
        var cyc = Workloads.Run(4, Workloads.Cyclic(5, 1000));
        T.Eq("cyclic scan of capacity+1 keys: zero hits", cyc.Hits, 0L);
        var fits = Workloads.Run(5, Workloads.Cyclic(5, 1000));
        T.Eq("working set fits: only cold misses", fits.Misses, 5L);
        T.Eq("evictions when it fits", fits.Evictions, 0L);
        var uni = Workloads.Run(100, Workloads.Uniform(1000, 200_000, 1));
        T.True("uniform ≈ capacity/distinct = 0.10", Math.Abs(uni.HitRatio - 0.10) < 0.01);
        var skew = Workloads.Run(100, Workloads.Skewed(1000, 200_000, 1));
        T.True("skewed beats uniform at same capacity", skew.HitRatio > 0.5);
        T.Note($"uniform {uni.HitRatio:P1}, skewed {skew.HitRatio:P1}, cyclic {cyc.HitRatio:P1}");
    }

    static void Lfu() {
        T.Section("A03 LFU + GetRank");
        var c = new LfuRankCache<string, int>(3);
        c.Put("a", 1); c.Put("b", 2); c.Put("c", 3);
        c.TryGet("a", out _); c.TryGet("a", out _);       // a:3
        c.TryGet("b", out _);                             // b:2, c:1
        T.Eq("a rank 1", c.GetRank("a"), 1);
        T.Eq("b rank 2", c.GetRank("b"), 2);
        T.Eq("c rank 3 = next victim", c.GetRank("c"), 3);
        T.Eq("missing rank", c.GetRank("zz"), -1);
        T.Eq("GetRank is not a use", c.GetRank("c"), 3);
        c.Put("d", 4);                                    // evicts c
        T.True("c evicted", !c.TryGet("c", out _));
        // tie on frequency: LRU loses
        var t = new LfuRankCache<int, int>(2);
        t.Put(1, 1); t.Put(2, 2);                        // both freq 1, 2 more recent
        T.Eq("tie: more recent ranks higher", t.GetRank(2), 1);
        t.Put(3, 3);                                      // evicts 1 (least recent at min freq)
        T.True("tie broken by recency", !t.TryGet(1, out _) && t.TryGet(2, out _));
        // minFreq resets after eviction of the only low-frequency key
        var m = new LfuRankCache<int, int>(1);
        m.Put(1, 1); m.TryGet(1, out _); m.TryGet(1, out _); m.Put(2, 2); m.Put(3, 3);
        T.True("capacity 1 churn", m.TryGet(3, out _) && !m.TryGet(2, out _));
    }

    static void Intervals() {
        T.Section("E01 IntervalSet");
        var s = new IntervalSet();
        s.Add(1, 3); s.Add(5, 7);
        T.Eq("two intervals", s.Count, 2);
        s.Add(3, 5);                                       // touches both: half-open merge
        T.Eq("touching merges to one", s.Count, 1);
        T.Eq("covered", s.CoveredLength, 6L);
        s.Add(2, 4);                                       // contained
        T.Eq("contained no change", s.CoveredLength, 6L);
        s.Remove(3, 4);
        T.Eq("remove splits", s.Count, 2);
        T.Eq("covered after split", s.CoveredLength, 5L);
        T.True("3 not contained", !s.Contains(3));
        T.True("4 contained", s.Contains(4));
        T.True("7 not contained (half-open)", !s.Contains(7));

        // property test against a bitmap
        var rnd = new Random(7); bool ok = true;
        for (int trial = 0; trial < 300 && ok; trial++) {
            var set = new IntervalSet(); var bits = new bool[60];
            for (int op = 0; op < 25; op++) {
                int a = rnd.Next(55), b = a + 1 + rnd.Next(5);
                if (rnd.Next(3) == 0) { set.Remove(a, b); for (int i = a; i < b; i++) bits[i] = false; }
                else { set.Add(a, b); for (int i = a; i < b; i++) bits[i] = true; }
                if (set.CoveredLength != bits.Count(x => x)) ok = false;
                for (int i = 0; i < 60; i++) if (set.Contains(i) != bits[i]) ok = false;
                var ivs = set.Intervals;
                for (int i = 1; i < ivs.Count; i++) if (ivs[i].Start <= ivs[i - 1].End) ok = false;   // disjoint AND non-touching
            }
        }
        T.True("matches bitmap over 300 random trials", ok);
    }

    static void Records() {
        T.Section("C01 records");
        var lines = new[] {
            "{\"user\":\"u1\",\"action\":\"view\",\"ts\":1,\"ms\":100}",
            "{\"user\":\"u2\",\"action\":\"view\",\"ts\":2,\"ms\":300}",
            "{\"user\":\"u1\",\"action\":\"like\",\"ts\":3,\"ms\":50}",
            "not json",
            "[1,2]",
            "{\"user\":\"u3\",\"action\":\"view\",\"ts\":4}",
            "{\"user\":\"u3\",\"action\":\"view\",\"ts\":\"x\",\"ms\":1}",
            "{\"user\":\"u3\",\"action\":\"view\",\"ts\":5,\"ms\":-1}",
            "",
            "{\"user\":\"u1\",\"action\":\"view\",\"ts\":6,\"ms\":200}",
        };
        var agg = new Aggregator().Consume(lines);
        T.Eq("accepted", agg.Accepted, 4);
        T.Eq("not json", agg.Rejected.GetValueOrDefault(Reject.NotJson), 1);
        T.Eq("not object", agg.Rejected.GetValueOrDefault(Reject.NotAnObject), 1);
        T.Eq("missing", agg.Rejected.GetValueOrDefault(Reject.MissingField), 1);
        T.Eq("wrong type", agg.Rejected.GetValueOrDefault(Reject.WrongType), 1);
        T.Eq("out of range", agg.Rejected.GetValueOrDefault(Reject.OutOfRange), 1);
        var view = agg.Summary()[0];
        T.Eq("view first", view.Action, "view");
        T.Eq("view count", view.Count, 3);
        T.Eq("view mean", view.MeanMs, 200.0);
        T.Eq("view max", view.MaxMs, 300);
        T.Eq("view distinct users", view.DistinctUsers, 2);
    }

    static void Queue() {
        T.Section("D01 bounded queue");
        var q = new BoundedBlockingQueue<int>(4);
        long produced = 0, consumed = 0; int consumedCount = 0;
        var producers = Enumerable.Range(0, 4).Select(p => Task.Run(() => {
            for (int i = 1; i <= 5000; i++) { q.Enqueue(i); Interlocked.Add(ref produced, i); }
        })).ToArray();
        var consumers = Enumerable.Range(0, 4).Select(_ => Task.Run(() => {
            while (q.TryDequeue(out var x)) { Interlocked.Add(ref consumed, x); Interlocked.Increment(ref consumedCount); }
        })).ToArray();
        Task.WaitAll(producers);
        q.Complete();
        T.True("consumers exit after complete", Task.WaitAll(consumers, 5000));
        T.Eq("no item lost or duplicated (sum)", consumed, produced);
        T.Eq("no item lost or duplicated (count)", consumedCount, 20000);

        var full = new BoundedBlockingQueue<int>(1);
        full.Enqueue(1);
        using var cts = new CancellationTokenSource(100);
        bool cancelled = false;
        try { full.Enqueue(2, cts.Token); } catch (OperationCanceledException) { cancelled = true; }
        T.True("blocked producer honours cancellation", cancelled);

        full.Complete();
        bool rejected = false; try { full.Enqueue(3); } catch (InvalidOperationException) { rejected = true; }
        T.True("enqueue after complete throws", rejected);
        T.True("drain after complete", full.TryDequeue(out var last) && last == 1);
        T.True("then false", !full.TryDequeue(out _));
    }

    static void MazeT() {
        T.Section("B01 maze");
        var m = new Maze(new[] {
            "#S#####",
            "#...#.#",
            "#.#.#.#",
            "#.#...#",
            "#####E#" });
        T.True("well formed", m.IsWellFormed());
        T.Eq("shortest path", m.ShortestPath(), 8);
        var hole = new Maze(new[] { "#S###", "#...#", "....#", "#..E#", "#####" });
        T.True("hole in outer wall detected", !hole.IsWellFormed());
        var blocked = new Maze(new[] { "#S###", "#.#.#", "###.#", "#..E#", "#####" });
        T.Eq("no path", blocked.ShortestPath(), -1);
        bool allOk = true;
        for (int seed = 0; seed < 200; seed++) {
            var g = Maze.Generate(21, 31, seed);
            if (!g.IsWellFormed() || g.ShortestPath() < 0) allOk = false;
        }
        T.True("200 generated mazes: well formed, always a path", allOk);
    }

    static void Sampling_() {
        T.Section("G01 sampling");
        // exact: enumerate all 49 (a,b) pairs once each and count accepted outputs
        var counts = new int[11]; int accepted = 0;
        for (int a = 1; a <= 7; a++) for (int b = 1; b <= 7; b++) {
            var seq = new Queue<int>(new[] { a, b, 1, 1 });          // 1,1 → idx 0 → accept, if retried
            int calls = 0;
            int r = Sampling.Rand10(() => { calls++; return seq.Dequeue(); });
            if (calls == 2) { counts[r]++; accepted++; }
        }
        T.Eq("40 of 49 pairs accepted", accepted, 40);
        T.True("each output from exactly 4 pairs", counts.Skip(1).All(c => c == 4));

        // general form, exact enumeration: uniform below 6 from a fair coin (m=2)
        var hist = new int[6]; int acceptedPaths = 0;
        for (int bits = 0; bits < 8; bits++) {
            var src = new Queue<int>(new[] { (bits >> 2) & 1, (bits >> 1) & 1, bits & 1, 0, 0, 0 });
            int used = 0;
            int r = Sampling.UniformBelow(6, 2, () => { used++; return src.Dequeue(); });
            if (used == 3) { hist[r]++; acceptedPaths++; }
        }
        T.Eq("6 of 8 three-bit strings accepted", acceptedPaths, 6);
        T.True("each of 0..5 exactly once", hist.All(h => h == 1));

        // von Neumann on a 70/30 coin, sampled
        var rnd = new Random(3); int ones = 0, N = 100_000;
        for (int i = 0; i < N; i++) ones += FairCoin.Flip(() => rnd.NextDouble() < 0.7 ? 1 : 0);
        T.True("fair coin from 70/30 within 1%", Math.Abs(ones / (double)N - 0.5) < 0.01);
    }

    static void Window() {
        T.Section("C02 window counter");
        var w = new WindowCounter(300);
        w.Record(1); w.Record(1); w.Record(299); w.Record(300);
        T.Eq("all four inside window at 300", w.Count(300), 4L);
        T.Eq("second 1 leaves at 301", w.Count(301), 2L);
        w.Record(601);                                    // reuses slot 1, stale second overwritten
        T.Eq("stale slot reset", w.Count(601), 1L);
        var c = new WindowCounter(60);
        Parallel.For(0, 8, t => { for (int i = 0; i < 10_000; i++) c.Record(1000); });
        T.Eq("no lost increments under contention", c.Count(1000), 80_000L);
    }

    // ---------------------------------------------------------------- review exercises
    static void Review() {
        T.Section("Review — each defect reproduced");

        var r1 = new R1_LruCache(2);
        r1.Put(1, 1); r1.Put(2, 2); r1.Get(1); r1.Put(3, 3);
        T.Eq("R1: Get does not refresh recency, so the just-read key 1 is evicted", r1.Get(1), -1);

        long now = 0;
        var r2 = new R2_LruTtl(2, () => now);
        r2.Put(1, 1, 10); r2.Put(2, 2, 1000);
        r2.Get(1);                                        // 1 is MRU
        now = 50;
        T.Eq("R2: expired read returns -1", r2.Get(1), -1);
        T.Eq("R2: …but the dead entry still occupies capacity", r2.Count, 2);
        r2.Put(3, 3, 1000);                               // evicts LRU = live key 2, keeps dead key 1
        T.Eq("R2: live key 2 evicted while dead key 1 kept", r2.Get(2), -1);

        int corrupt = 0;
        for (int trial = 0; trial < 20; trial++) {
            var r3 = new R3_ConcurrentLru(32);
            try {
                Parallel.For(0, 8, t => { for (int i = 0; i < 5000; i++) { r3.Put(i % 64, i); r3.Get((i * 3) % 64); } });
                if (r3.ListCount != r3.MapCount) corrupt++;
            } catch (Exception) { corrupt++; }
        }
        T.Note($"R3: list/map inconsistent or threw in {corrupt}/20 trials (nondeterministic by nature)");

        var merged = R4_Merge.Merge(new() { (1, 10), (2, 3) });
        T.Eq("R4: [1,10]+[2,3] collapses to [1,3]", merged[0].End, 3);

        var r5 = new R5_TopK();
        foreach (var w in "a b a c a b".Split(' ')) r5.Add(w);
        T.Eq("R5: answer is right — the defect is cost, not correctness", string.Join(",", r5.Top(2)), "a,b");

        var dist = new int[11];
        for (int a = 1; a <= 7; a++) for (int b = 1; b <= 7; b++) {
            var s = new Queue<int>(new[] { a, b });
            dist[R6_Rand10.Rand10(() => s.Dequeue())]++;
        }
        T.True("R6: 49 pairs do not split evenly over 10 outputs", dist.Skip(1).Distinct().Count() > 1);
        T.Note("R6 counts per output over all 49 pairs: " + string.Join(" ", dist.Skip(1)));

        var parsed = R7_Parse.ParseAll(new[] { "u1,view,1,10", "u2,view,BAD,10", "u3,view,3,10", "u4,view,4,10" });
        T.Eq("R7: one bad line silently drops every line after it", parsed.Count, 1);

        int loads = 0;
        var r8 = new R8_ReadThrough(id => { Interlocked.Increment(ref loads); Thread.Sleep(50); return id; });
        var barrier = new Barrier(8);
        var tasks = Enumerable.Range(0, 8).Select(_ => Task.Factory.StartNew(() => { barrier.SignalAndWait(); r8.Get("p1"); },
                                                   TaskCreationOptions.LongRunning)).ToArray();
        Task.WaitAll(tasks);
        T.Note($"R8: 8 concurrent first reads triggered {loads} loads of the slow source");
        int fixedLoads = 0;
        var f8 = new Fixes.ReadThrough(id => { Interlocked.Increment(ref fixedLoads); Thread.Sleep(50); return id; });
        var b2 = new Barrier(8);
        Task.WaitAll(Enumerable.Range(0, 8).Select(_ => Task.Factory.StartNew(() => { b2.SignalAndWait(); f8.Get("p1"); },
                                                   TaskCreationOptions.LongRunning)).ToArray());
        T.Eq("R8 fixed: Lazy collapses concurrent loads to one", fixedLoads, 1);

        int failures = 0;
        for (int trial = 0; trial < 10; trial++) {
            var q = new R9_BlockingQueue<int>(1);
            var ex = new ConcurrentBag<Exception>();
            var threads = new List<Thread>();
            for (int c = 0; c < 4; c++) threads.Add(new Thread(() => { try { for (int i = 0; i < 500; i++) q.Dequeue(); } catch (Exception e) { ex.Add(e); } }) { IsBackground = true });
            for (int p = 0; p < 4; p++) threads.Add(new Thread(() => { try { for (int i = 0; i < 500; i++) q.Enqueue(i); } catch (Exception e) { ex.Add(e); } }) { IsBackground = true });
            threads.ForEach(t => t.Start());
            bool finished = threads.All(t => t.Join(2000));
            if (!finished || !ex.IsEmpty) failures++;
        }
        T.Note($"R9: hung or threw in {failures}/10 trials");

        var slowSink = new SlowSink(2);
        var r11 = new R11_Logger(slowSink);
        var sw = System.Diagnostics.Stopwatch.StartNew();
        Parallel.For(0, 8, new ParallelOptions { MaxDegreeOfParallelism = 8 }, _ => { for (int i = 0; i < 25; i++) r11.Log(Severity.Info, "x"); });
        long serialMs = sw.ElapsedMilliseconds;
        T.True("R11: 200 logs × 2 ms sink take ≥ 400 ms — callers fully serialised", serialMs >= 400);
        var alog = new AsyncLogger(Severity.Info, 4096, new SlowSink(2));
        sw.Restart();
        Parallel.For(0, 8, new ParallelOptions { MaxDegreeOfParallelism = 8 }, _ => { for (int i = 0; i < 25; i++) alog.Log(Severity.Info, "x"); });
        long callerMs = sw.ElapsedMilliseconds;
        T.True("R11 fixed: callers return without waiting on the sink", callerMs < 100);
        T.Note($"R11: callers blocked {serialMs} ms with the lock; {callerMs} ms with the async logger");
        alog.DisposeAsync().AsTask().Wait();

        var r12 = new R12_AsyncCache(k => k == "bad" ? Task.FromException<string>(new IOException("down")) : Task.FromResult(k));
        try { r12.GetAsync("bad").Wait(); } catch (AggregateException) { }
        bool hung = !r12.GetAsync("ok").Wait(500);
        T.True("R12: one failed load leaves the semaphore held — every later call hangs", hung);

        var r14 = new R14_AsyncLogger(new SlowSink(0));
        Parallel.For(0, 10_000, new ParallelOptions { MaxDegreeOfParallelism = 32 }, i => r14.Log("m" + i));
        r14.Complete(); Thread.Sleep(300);
        T.True("R14: reports zero drops while writing far fewer than it accepted", r14.Dropped == 0 && Interlocked.Read(ref r14.Written) < r14.Accepted);
        T.Note($"R14: accepted {r14.Accepted}, dropped {r14.Dropped}, written {Interlocked.Read(ref r14.Written)}");

        var r13 = new R13_Window(300); var ok13 = new WindowCounter(300);
        r13.Record(0); ok13.Record(0);
        T.Eq("R13: event from exactly 300 s ago still counted", r13.Count(300), 1L);
        T.Eq("R13 fixed: WindowCounter excludes it", ok13.Count(300), 0L);

        var r10 = new R10_Sweeper();
        for (int i = 0; i < 100_000; i++) r10.Put(i, i < 10 ? 0 : long.MaxValue);
        T.Eq("R10: removes 10 dead entries by examining all 100,000 under the lock", r10.Sweep(1), 100_000);
    }

    // ---------------------------------------------------------------- debugging exercises
    static void Debugging() {
        T.Section("Debug — each symptom reproduced, each fix verified");

        var d1 = new D1_Lru(2);
        d1.Put(1, 1); d1.Put(2, 2); d1.Get(1); d1.Put(3, 3);
        T.Eq("D1: most recently used key 1 is the victim", d1.Get(1), -1);
        T.Eq("D1: …while LRU key 2 survives", d1.Get(2), 2);

        long now = 0;
        var d2 = new D2_TtlCache(() => now);
        d2.Put(7, 1, 10);
        now = 20;
        d2.BetweenCheckAndAct = () => d2.Put(7, 2, 1000);     // another thread writes a fresh value here
        d2.Get(7);
        d2.BetweenCheckAndAct = () => { };
        T.Eq("D2: the fresh value written between check and act is deleted", d2.Get(7), -1);
        var map = new Dictionary<int, (int V, long Exp)> { [7] = (1, 10) };
        var gate = new object();
        T.Eq("D2 fixed: expired read under one lock", Fixes.D2_Get(map, gate, 7, 20), -1);
        map[7] = (2, 1020);
        T.Eq("D2 fixed: fresh value survives", Fixes.D2_Get(map, gate, 7, 20), 2);

        var (dist, enq) = D3_Bfs.Shortest(60);
        T.Eq("D3: distance still correct", dist, 118);
        T.True("D3: enqueued well over one per cell", enq > 3600 * 1.5);
        T.Note($"D3: 3,600 cells, {enq:N0} enqueues ({enq / 3600.0:F2} per cell)");
        var fixedMaze = new Maze(Enumerable.Range(0, 62).Select(r => r == 0 || r == 61 ? new string('#', 62)
                          : "#" + new string('.', 60) + "#").ToArray().Select((row, r) =>
                          r == 1 ? "#S" + row.Substring(2) : r == 60 ? row.Substring(0, 60) + "E#" : row).ToArray());
        T.Eq("D3 fixed (Maze.ShortestPath, mark on enqueue): same distance", fixedMaze.ShortestPath(), 118);

        var d4 = new D4_Counter();
        Parallel.For(0, 8, _ => { for (int i = 0; i < 20_000; i++) d4.Hit("home"); });
        T.Note($"D4: 160,000 hits recorded as {d4.Get("home"):N0}");
        var counts = new ConcurrentDictionary<string, int>();
        Parallel.For(0, 8, _ => { for (int i = 0; i < 20_000; i++) Fixes.D4_Hit(counts, "home"); });
        T.Eq("D4 fixed: AddOrUpdate loses nothing", counts["home"], 160_000);

        var a = new Account { Id = 1, Balance = 100 }; var b = new Account { Id = 2, Balance = 100 };
        var bank = new D5_Bank();
        var bar = new Barrier(2);
        bank.AfterFirstLock = () => bar.SignalAndWait(1000);
        var t1 = new Thread(() => bank.Transfer(a, b, 10)) { IsBackground = true };
        var t2 = new Thread(() => bank.Transfer(b, a, 10)) { IsBackground = true };
        t1.Start(); t2.Start();
        bool done = t1.Join(1500) && t2.Join(1500);
        T.True("D5: opposite transfers deadlock", !done);
        var c1 = new Account { Id = 1, Balance = 100 }; var c2 = new Account { Id = 2, Balance = 100 };
        var bar2 = new Barrier(2);
        var u1 = new Thread(() => Fixes.D5_Transfer(c1, c2, 10, () => bar2.SignalAndWait(300))) { IsBackground = true };
        var u2 = new Thread(() => Fixes.D5_Transfer(c2, c1, 10, () => bar2.SignalAndWait(300))) { IsBackground = true };
        u1.Start(); u2.Start();
        T.True("D5 fixed: lock ordering completes", u1.Join(3000) && u2.Join(3000));
        T.Eq("D5 fixed: money conserved", c1.Balance + c2.Balance, 200L);

        var m6 = D6_Merge.Merge(new() { (1, 3), (8, 10), (2, 4) });
        T.Eq("D6: unsorted input loses coverage — [2,4] vanishes into [8,10]", string.Join(" ", m6), "(1, 3) (8, 10)");
        var s6 = D6_Merge.Merge(new List<(int S, int E)> { (1, 3), (8, 10), (2, 4) }.OrderBy(x => x.S).ToList());
        T.Eq("D6 fixed: sort first", string.Join(" ", s6), "(1, 4) (8, 10)");

        int[] Perms(Action<int[], Func<int, int>> shuffle, int n, out int paths) {
            var hist = new Dictionary<string, int>(); int p = 0;
            void Walk(List<int> choices) {
                int[] arr = Enumerable.Range(0, n).ToArray(); int idx = 0; bool need = false; int needN = 0;
                shuffle(arr, k => { if (idx < choices.Count) return choices[idx++]; if (!need) { need = true; needN = k; } return 0; });
                if (need) { for (int x = 0; x < needN; x++) Walk(new List<int>(choices) { x }); return; }
                p++; var key = string.Join("", arr); hist[key] = hist.GetValueOrDefault(key) + 1;
            }
            Walk(new List<int>());
            paths = p;
            return hist.Values.OrderBy(v => v).ToArray();
        }
        var bad = Perms((arr, pick) => D7_Shuffle.Shuffle(arr, pick), 3, out int badPaths);
        T.Eq("D7: n=3 has 9 equally likely choice paths", badPaths, 9);
        T.True("D7: 9 paths cannot split evenly over 6 orders", bad.Distinct().Count() > 1);
        T.Note("D7 path counts per permutation: " + string.Join(" ", bad));
        var good = Perms((arr, pick) => Fixes.D7_Shuffle(arr, pick), 3, out int goodPaths);
        T.True("D7 fixed: 6 paths, one per permutation", goodPaths == 6 && good.All(v => v == 1));

        TNode Leaf(string n, string v) => new TNode { Name = n, Value = v };
        var A = new TNode { Name = "root" }; A.Children["x"] = Leaf("x", "1");
        var B = new TNode { Name = "root" }; B.Children["y"] = Leaf("y", "2");
        var M = D8_TreeMerge.Merge(A, B);
        T.True("D8: merging added y to input A", A.Children.ContainsKey("y"));
        M.Children["x"].Value = "changed";
        T.Eq("D8: editing the result edits input A", A.Children["x"].Value, "changed");
        var A2 = new TNode { Name = "root" }; A2.Children["x"] = Leaf("x", "1");
        var B2 = new TNode { Name = "root" }; B2.Children["y"] = Leaf("y", "2");
        var M2 = Fixes.D8_Merge(A2, B2);
        M2.Children["x"].Value = "changed";
        T.True("D8 fixed: inputs untouched", A2.Children["x"].Value == "1" && !A2.Children.ContainsKey("y"));
        T.Eq("D8 fixed: merged has both", M2.Children.Count, 2);
    }
}

class ThrowingSink : ILogSink { public void Write(string line) => throw new IOException("sink down"); }
class CountingSink : ILogSink { public int N; public void Write(string line) => Interlocked.Increment(ref N); }
class SlowSink : ILogSink { private readonly int _ms; public SlowSink(int ms) => _ms = ms; public void Write(string line) => Thread.Sleep(_ms); }
