// dotnet run -c Release   — every number quoted in the tutorial video is printed by a "note:" line here.
using System.Diagnostics;

static class T {
    static int pass = 0, fail = 0;
    public static void Eq<TV>(string what, TV got, TV want) {
        if (EqualityComparer<TV>.Default.Equals(got, want)) pass++;
        else { fail++; Console.WriteLine($"  FAIL {what}: got {got}, want {want}"); }
    }
    public static void True(string what, bool c) => Eq(what, c, true);
    public static void Section(string s) => Console.WriteLine($"--- {s}");
    public static void Note(string s) => Console.WriteLine($"    note: {s}");
    public static int Report() { Console.WriteLine($"\n{pass} passed, {fail} failed"); return fail == 0 ? 0 : 1; }
}

class Program {
    const int Threads = 8, PerThread = 1_000_000;

    static void Many(Action body) {
        var ts = Enumerable.Range(0, Threads).Select(_ => new Thread(() => { for (int i = 0; i < PerThread; i++) body(); })).ToList();
        ts.ForEach(t => t.Start()); ts.ForEach(t => t.Join());
    }

    static int Main() {
        T.Section("DS1 record struct key");
        var d = new Dictionary<LogKey, int> { [new LogKey(Level.Warn, "Pay", 42, "slow")] = 1 };
        T.True("an equal new instance finds the entry", d.ContainsKey(new LogKey(Level.Warn, "Pay", 42, "slow")));
        T.True("a different line is a different key", !d.ContainsKey(new LogKey(Level.Warn, "Pay", 43, "slow")));

        T.Section("DS2 PriorityQueue, lazy cancel, tie-break");
        var q = new JobQueue();
        q.Add("b", 10); var a = q.Add("a", 5); q.Add("c", 10);
        a.Cancelled = true;
        T.Eq("nothing due at 4", q.PopDue(4), null);
        T.Eq("cancelled head skipped; b before c (same due, earlier seq)", q.PopDue(10)?.Name, "b");
        T.Eq("then c", q.PopDue(10)?.Name, "c");

        T.Section("DS3 LinkedList move-to-front by node");
        var list = new LinkedList<int>(new[] { 1, 2, 3 });
        ListOps.MoveToFront(list, list.Last);
        T.Eq("3 moved to front", string.Join(",", list), "3,1,2");

        T.Section("DS4 floor / ceiling on SortedSet");
        var s = new SortedSet<int> { 10, 20, 30 };
        T.Eq("floor 25", SortedOps.Floor(s, 25), 20);
        T.Eq("floor 5", SortedOps.Floor(s, 5), null);
        T.Eq("ceiling 25", SortedOps.Ceiling(s, 25), 30);
        T.Eq("ceiling 31", SortedOps.Ceiling(s, 31), null);
        T.Eq("ceiling exact", SortedOps.Ceiling(s, 20), 20);

        T.Section("DS5 ring");
        var r = new Ring(60);
        r.Add(5, 2); r.Add(5, 3); r.Add(65, 7);         // 65 % 60 == 5: the stale slot is reset
        T.Eq("t=65 sees only its own value", r.Get(65), 7L);
        T.Eq("t=5 is gone", r.Get(5), 0L);

        T.Section("F1 thread, pool, task");
        T.Eq("new Thread + Join", RunWays.OnNewThread(() => 6 * 7), 42);
        T.Eq("Task.Run on the pool", RunWays.OnThreadPool(() => 6 * 7).GetAwaiter().GetResult(), 42);
        var waits = Enumerable.Range(0, 200).Select(_ => RunWays.WaitWithoutAThread(100)).ToArray();
        var swf = System.Diagnostics.Stopwatch.StartNew(); Task.WaitAll(waits);
        T.True($"200 concurrent 100 ms waits finish in ~100 ms ({swf.ElapsedMilliseconds} ms) — waiting needs no thread", swf.ElapsedMilliseconds < 1000);

        T.Section("F2 lock protects an invariant");
        int overdrawn = 0, okNeg = 0;
        for (int trial = 0; trial < 300; trial++) {
            var acct = new Account(100); var safeAcct = new Account(100);
            using var go = new Barrier(4);
            var ts = Enumerable.Range(0, 4).Select(_ => new Thread(() => { go.SignalAndWait(); acct.WithdrawUnsafe(100); safeAcct.Withdraw(100); })).ToList();
            ts.ForEach(t => t.Start()); ts.ForEach(t => t.Join());
            if (acct.Balance < 0) overdrawn++;
            if (safeAcct.Balance < 0) okNeg++;
        }
        T.Note($"check-then-act overdrew the account in {overdrawn} of 300 trials");
        T.Eq("with the lock: never negative", okNeg, 0);

        T.Section("F3 CPU-bound: Parallel.For");
        long expect = 0; for (long i = 0; i < 2_000_000; i++) expect += i * i;
        T.Eq("Parallel.For with per-thread totals is exact", CpuWork.SumOfSquares(2_000_000), expect);

        T.Section("M modern C#");
        var o = new Order("A1", 1500m);
        T.Eq("record value equality", o, new Order("A1", 1500m));
        T.Eq("with-expression copies", (o with { Status = "cancelled" }).Status, "cancelled");
        T.Eq("switch patterns: large", Modern.Classify(o), "large");
        T.Eq("switch patterns: cancelled first", Modern.Classify(o with { Status = "cancelled" }), "ignore");
        T.Eq("switch patterns: invalid", Modern.Classify(new Order("B", 0m)), "invalid");
        T.True("collection expression + spread", Modern.Merge([1, 2], [3]).SequenceEqual(new[] { 1, 2, 3, 99 }));
        var inv = new Inventory(8); inv.Add("x", 5);
        T.True("primary constructor + TryGetValue", inv.Capacity == 8 && inv.TryTake("x", 3) && !inv.TryTake("x", 3));
        T.Eq("required member", new Modern.Config { Name = "svc" }.Retries, 3);

        T.Section("C1 race on count++");
        long expected = (long)Threads * PerThread;
        long worst = expected;
        for (int trial = 0; trial < 5 && worst == expected; trial++) {
            var u = new UnsafeCounter(); Many(u.Inc); worst = Math.Min(worst, u.Value);
        }
        T.True("unsafe counter lost updates", worst < expected);
        T.Note($"unsafe: {worst:N0} of {expected:N0} ({100.0 * (expected - worst) / expected:F0}% lost)");
        var sw = Stopwatch.StartNew(); var lc = new LockedCounter(); Many(lc.Inc); var tLock = sw.ElapsedMilliseconds;
        sw.Restart(); var ac = new AtomicCounter(); Many(ac.Inc); var tAtomic = sw.ElapsedMilliseconds;
        T.Eq("lock exact", lc.Value, expected);
        T.Eq("Interlocked exact", ac.Value, expected);
        T.Note($"lock {tLock} ms, Interlocked {tAtomic} ms for {expected:N0} increments");

        T.Section("C2 check-then-act on ConcurrentDictionary");
        long cWorst = expected;
        for (int trial = 0; trial < 5 && cWorst == expected; trial++) {
            var pv = new UnsafePageViews();
            var ts = Enumerable.Range(0, Threads).Select(_ => new Thread(() => { for (int i = 0; i < 200_000; i++) pv.Hit("home"); })).ToList();
            ts.ForEach(t => t.Start()); ts.ForEach(t => t.Join());
            cWorst = Math.Min(cWorst, pv.Get("home"));
        }
        T.True("TryGetValue then set loses hits", cWorst < Threads * 200_000);
        T.Note($"unsafe page views: {cWorst:N0} of {Threads * 200_000:N0}");
        var ok = new PageViews();
        var t2 = Enumerable.Range(0, Threads).Select(_ => new Thread(() => { for (int i = 0; i < 200_000; i++) ok.Hit("home"); })).ToList();
        t2.ForEach(t => t.Start()); t2.ForEach(t => t.Join());
        T.Eq("AddOrUpdate exact", ok.Get("home"), Threads * 200_000);

        T.Section("C3 GetOrAdd factory runs more than once");
        int maxLoads = 0;
        for (int trial = 0; trial < 5; trial++) {
            int loads = 0;
            var barrier = new Barrier(Threads);
            var ul = new UnsafeLoader(k => { Interlocked.Increment(ref loads); Thread.Sleep(50); return "v"; });
            var ts = Enumerable.Range(0, Threads).Select(_ => new Thread(() => { barrier.SignalAndWait(); ul.Get("profile:1"); })).ToList();
            ts.ForEach(t => t.Start()); ts.ForEach(t => t.Join());
            maxLoads = Math.Max(maxLoads, loads);
        }
        T.True("GetOrAdd ran the slow factory more than once", maxLoads > 1);
        T.Note($"GetOrAdd: up to {maxLoads} loads for {Threads} concurrent first reads");
        int onceLoads = 0;
        var b2 = new Barrier(Threads);
        var ol = new OnceLoader(k => { Interlocked.Increment(ref onceLoads); Thread.Sleep(50); return "v"; });
        var t3 = Enumerable.Range(0, Threads).Select(_ => new Thread(() => { b2.SignalAndWait(); ol.Get("profile:1"); })).ToList();
        t3.ForEach(t => t.Start()); t3.ForEach(t => t.Join());
        T.Eq("Lazy: exactly one load", onceLoads, 1);

        T.Section("C4 Monitor wait/pulse gate");
        var g = new Gate(); int passed = 0;
        var waiters = Enumerable.Range(0, 4).Select(_ => new Thread(() => { g.WaitOpen(); Interlocked.Increment(ref passed); })).ToList();
        waiters.ForEach(t => t.Start());
        Thread.Sleep(50);
        T.Eq("nobody passes before Open", Volatile.Read(ref passed), 0);
        g.Open();
        T.True("all waiters released", waiters.All(t => t.Join(2000)) && passed == 4);

        T.Section("C5 deadlock and lock ordering");
        var x = new Acct { Id = 1, Balance = 1000 }; var y = new Acct { Id = 2, Balance = 1000 };
        var meet = new Barrier(2);
        var d1 = new Thread(() => Transfers.Unsafe(x, y, 1, () => meet.SignalAndWait(500))) { IsBackground = true };
        var d2 = new Thread(() => Transfers.Unsafe(y, x, 1, () => meet.SignalAndWait(500))) { IsBackground = true };
        d1.Start(); d2.Start();
        bool finished = d1.Join(2000) && d2.Join(2000);
        T.True("opposite transfers deadlock with unordered locks", !finished);
        var p = new Acct { Id = 1, Balance = 1000 }; var r2 = new Acct { Id = 2, Balance = 1000 };
        var o1 = new Thread(() => { for (int i = 0; i < 100_000; i++) Transfers.Ordered(p, r2, 1); });
        var o2 = new Thread(() => { for (int i = 0; i < 100_000; i++) Transfers.Ordered(r2, p, 1); });
        o1.Start(); o2.Start();
        T.True("ordered locks finish", o1.Join(10_000) && o2.Join(10_000));
        T.Eq("money conserved", p.Balance + r2.Balance, 2000L);

        T.Section("C6 SemaphoreSlim released in finally");
        int calls = 0;
        var cache = new AsyncCache(async k => { await Task.Yield(); if (Interlocked.Increment(ref calls) == 1) throw new InvalidOperationException("db down"); return "v-" + k; });
        bool threw = false;
        try { cache.GetAsync("a").GetAwaiter().GetResult(); } catch (InvalidOperationException) { threw = true; }
        T.True("first load failed", threw);
        var second = cache.GetAsync("a");
        T.True("a later call is not wedged", second.Wait(2000) && second.Result == "v-a");

        T.Section("C7 reader-writer lock");
        var cfg = new Config(); cfg.Set("mode", "on");
        int reads = 0;
        Parallel.For(0, 100_000, _ => { if (cfg.Get("mode") == "on") Interlocked.Increment(ref reads); });
        T.Eq("parallel reads see the value", reads, 100_000);

        T.Section("C8 bounded channel pipeline");
        T.Eq("every item delivered exactly once", Pipeline.RunAsync(100_000, 64).GetAwaiter().GetResult(), 100_000L * 100_001 / 2);

        T.Section("C9 striped counts");
        var sc = new StripedCounts(16);
        Parallel.For(0, 400_000, i => sc.Inc("k" + (i % 10)));
        T.Eq("exact per key", Enumerable.Range(0, 10).Sum(i => sc.Get("k" + i)), 400_000L);

        T.Section("C10 cancellation stops a worker");
        var cts = new CancellationTokenSource();
        var w = Worker.RunAsync(cts.Token);
        Thread.Sleep(20); cts.Cancel();
        T.True("worker stopped", w.Wait(2000));

        T.Section("C11 immutable snapshot swap");
        var snap = new SnapshotConfig();
        snap.Publish(new() { ["a"] = "0", ["b"] = "0" });
        int torn = 0; bool stop = false;
        var writer = new Thread(() => { for (int v = 1; v <= 20_000; v++) snap.Publish(new() { ["a"] = v.ToString(), ["b"] = v.ToString() }); Volatile.Write(ref stop, true); });
        var readers = Enumerable.Range(0, 4).Select(_ => new Thread(() => {
            while (!Volatile.Read(ref stop)) { var s0 = snap.Snapshot; if (s0["a"] != s0["b"]) Interlocked.Increment(ref torn); }
        })).ToList();
        writer.Start(); readers.ForEach(t => t.Start()); writer.Join(); readers.ForEach(t => t.Join());
        T.Eq("readers never see a half-updated version", torn, 0);
        T.Eq("last write wins", snap.Get("a"), "20000");

        T.Section("C12 stress harness");
        var safe = new AtomicCounter(); var unsafeC = new UnsafeCounter();
        Stress.Run(8, 250_000, _ => { safe.Inc(); unsafeC.Inc(); });
        T.Eq("harness: safe counter exact", safe.Value, 2_000_000L);
        T.True("harness exposes the unsafe counter", unsafeC.Value < 2_000_000);
        T.Note($"stress harness: unsafe {unsafeC.Value:N0} of 2,000,000");

        T.Section("C13 async fan-out");
        int inFlight = 0, peak = 0;
        Func<int, Task<int>> fetch = async i => {
            int now = Interlocked.Increment(ref inFlight);
            lock (fetch_lock) peak = Math.Max(peak, now);
            await Task.Delay(50);
            Interlocked.Decrement(ref inFlight);
            return i * i;
        };
        var swa = System.Diagnostics.Stopwatch.StartNew();
        var seq = AsyncFanOut.Sequential(fetch, 10).GetAwaiter().GetResult();
        long seqMs = swa.ElapsedMilliseconds; swa.Restart();
        var con = AsyncFanOut.Concurrent(fetch, 10).GetAwaiter().GetResult();
        long conMs = swa.ElapsedMilliseconds;
        T.True($"sequential awaits take ~10 x 50 ms ({seqMs} ms)", seqMs >= 450);
        T.True($"Task.WhenAll overlaps them ({conMs} ms)", conMs < 250);
        T.True("same results, same order", seq.SequenceEqual(con) && con[9] == 81);
        peak = 0;
        var bnd = AsyncFanOut.Bounded(fetch, 12, 3).GetAwaiter().GetResult();
        T.True($"bounded: never more than 3 in flight (peak {peak})", peak <= 3 && peak > 1);
        T.True("bounded: all results", bnd.Length == 12 && bnd[11] == 121);

        return T.Report();
    }
    static readonly object fetch_lock = new();
}
