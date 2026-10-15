// Tutorial part 0 — concurrency foundations for someone new to it, before the races in Concurrency.cs.
// Every claim below is exercised by Tests.cs.

// ---- F1. Three ways to run work. A Thread is an OS thread you create and own (about 1 MB of stack —
// expensive, so create few). The ThreadPool keeps a small set of reusable threads. A Task is a unit of
// work, normally run on the pool: Task.Run for CPU work; an async method for WAITING (I/O), which uses
// no thread at all while it waits.
public static class RunWays {
    public static int OnNewThread(Func<int> work) {
        int result = 0;
        var t = new Thread(() => result = work());
        t.Start();
        t.Join();                                   // wait for it to finish
        return result;
    }

    public static Task<int> OnThreadPool(Func<int> work) => Task.Run(work);

    public static async Task<int> WaitWithoutAThread(int ms) {
        await Task.Delay(ms);                       // no thread is blocked while this waits
        return ms;
    }
}

// ---- F2. What a lock protects: an INVARIANT. Here: the balance never goes negative.
public sealed class Account {
    private long _balance;
    private readonly Lock _gate = new();            // System.Threading.Lock (.NET 9+); `lock` uses it directly

    public Account(long opening) => _balance = opening;

    public long Balance { get { lock (_gate) return _balance; } }

    // BROKEN — check-then-act. Two threads both see 100, both pass the check, both subtract 100.
    public bool WithdrawUnsafe(long amount) {
        if (_balance >= amount) {
            Thread.SpinWait(200);                   // the gap between check and act, made visible
            _balance -= amount;
            return true;
        }
        return false;
    }

    // FIXED — the check and the update happen as one step; no other thread can get in between.
    public bool Withdraw(long amount) {
        lock (_gate) {
            if (_balance < amount) return false;
            _balance -= amount;
            return true;
        }
    }
}

// ---- F3. CPU-bound vs I/O-bound. CPU work (computing) speeds up with more cores: Parallel.For.
// I/O work (waiting on a network or disk) speeds up by overlapping the waits: async + Task.WhenAll.
public static class CpuWork {
    // Each worker keeps a private running total and adds it to the shared total ONCE at the end,
    // so the threads almost never contend.
    public static long SumOfSquares(int n) {
        long total = 0;
        Parallel.For(0, n,
            () => 0L,                                        // per-thread starting value
            (i, _, local) => local + (long)i * i,            // runs on many threads, no sharing
            local => Interlocked.Add(ref total, local));      // combine, once per thread
        return total;
    }
}
