// Tutorial part 2 — the concurrency concepts every AI-round follow-up reduces to, in C#.
// Each "Unsafe" type is the plausible first answer; its sibling is the fix. Tests.cs
// measures the difference rather than asserting it from memory.

using System.Collections.Concurrent;
using System.Threading.Channels;

// ---- C1. A race: count++ is read, add, write. Two threads can read the same value.
public sealed class UnsafeCounter { public long Value; public void Inc() => Value++; }

public sealed class LockedCounter {
    private readonly object _gate = new();      // private object: nobody else can lock it
    private long _value;
    public void Inc() { lock (_gate) _value++; }
    public long Value { get { lock (_gate) return _value; } }
}

public sealed class AtomicCounter {
    private long _value;
    public void Inc() => Interlocked.Increment(ref _value);   // one CPU instruction, no lock
    public long Value => Interlocked.Read(ref _value);
}

// ---- C2. Check-then-act. Each ConcurrentDictionary call is atomic; two calls in a row are not.
public sealed class UnsafePageViews {
    private readonly ConcurrentDictionary<string, int> _d = new();
    public void Hit(string page) {
        _d.TryGetValue(page, out var n);        // another thread can hit between these two lines
        _d[page] = n + 1;
    }
    public int Get(string page) => _d.GetValueOrDefault(page);
}

public sealed class PageViews {
    private readonly ConcurrentDictionary<string, int> _d = new();
    public void Hit(string page) => _d.AddOrUpdate(page, 1, (_, n) => n + 1);   // read-modify-write as one call
    public int Get(string page) => _d.GetValueOrDefault(page);
}

// ---- C3. GetOrAdd(key, factory) can run the factory MORE than once under a race; only one
// result is stored, but every racer pays for the load. Lazy<T> makes the load run once.
public sealed class UnsafeLoader {
    private readonly ConcurrentDictionary<string, string> _cache = new();
    private readonly Func<string, string> _load;
    public UnsafeLoader(Func<string, string> load) => _load = load;
    public string Get(string key) => _cache.GetOrAdd(key, _load);
}

public sealed class OnceLoader {
    private readonly ConcurrentDictionary<string, Lazy<string>> _cache = new();
    private readonly Func<string, string> _load;
    public OnceLoader(Func<string, string> load) => _load = load;
    public string Get(string key) =>
        _cache.GetOrAdd(key, k => new Lazy<string>(() => _load(k),
                                                   LazyThreadSafetyMode.ExecutionAndPublication)).Value;
}

// ---- C4. A condition: wait until something is true. Monitor.Wait releases the lock while
// waiting and re-acquires it before returning. ALWAYS re-check in a while loop.
public sealed class Gate {
    private readonly object _lock = new();
    private bool _open;
    public void WaitOpen() {
        lock (_lock) {
            while (!_open)                 // while, not if: wakes can be spurious or stale
                Monitor.Wait(_lock);
        }
    }
    public void Open() {
        lock (_lock) { _open = true; Monitor.PulseAll(_lock); }   // PulseAll: wake every waiter
    }
}

// ---- C5. Deadlock: thread A holds X and wants Y, thread B holds Y and wants X.
// Fix: every thread takes locks in one global order (here, by account id).
public sealed class Acct { public int Id; public long Balance; public readonly object Lock = new(); }

public static class Transfers {
    public static void Unsafe(Acct from, Acct to, long amt, Action between = null) {
        lock (from.Lock) { between?.Invoke(); lock (to.Lock) { from.Balance -= amt; to.Balance += amt; } }
    }
    public static void Ordered(Acct from, Acct to, long amt) {
        var (first, second) = from.Id < to.Id ? (from, to) : (to, from);
        lock (first.Lock) lock (second.Lock) { from.Balance -= amt; to.Balance += amt; }
    }
}

// ---- C6. Async code cannot hold a lock across await (the compiler rejects it, CS1996).
// SemaphoreSlim(1,1) is the async mutex — and Release MUST be in finally, or one failed
// load leaves it held and every later caller waits forever.
public sealed class AsyncCache {
    private readonly Dictionary<string, string> _cache = new();
    private readonly SemaphoreSlim _gate = new(1, 1);
    private readonly Func<string, Task<string>> _load;
    public AsyncCache(Func<string, Task<string>> load) => _load = load;

    public async Task<string> GetAsync(string key) {
        await _gate.WaitAsync();
        try {
            if (_cache.TryGetValue(key, out var v)) return v;
            v = await _load(key);
            _cache[key] = v;
            return v;
        } finally {
            _gate.Release();
        }
    }
}

// ---- C7. Reads far outnumber writes AND reads do not mutate: ReaderWriterLockSlim lets reads
// run in parallel. (Useless for an LRU: its Get moves a node, so every Get is a write.)
public sealed class Config {
    private readonly ReaderWriterLockSlim _rw = new();
    private Dictionary<string, string> _values = new();
    public string Get(string k) {
        _rw.EnterReadLock();
        try { return _values.GetValueOrDefault(k); } finally { _rw.ExitReadLock(); }
    }
    public void Set(string k, string v) {
        _rw.EnterWriteLock();
        try { _values[k] = v; } finally { _rw.ExitWriteLock(); }
    }
}

// ---- C8. Producer/consumer the production way: a bounded Channel. WriteAsync waits when
// full (back-pressure); the reader drains until the writer completes.
public static class Pipeline {
    public static async Task<long> RunAsync(int items, int capacity) {
        var ch = Channel.CreateBounded<int>(new BoundedChannelOptions(capacity) {
            FullMode = BoundedChannelFullMode.Wait, SingleReader = true });
        var producer = Task.Run(async () => {
            for (int i = 1; i <= items; i++) await ch.Writer.WriteAsync(i);
            ch.Writer.Complete();
        });
        long sum = 0;
        await foreach (var x in ch.Reader.ReadAllAsync()) sum += x;
        await producer;
        return sum;
    }
}

// ---- C9. Contention: one lock serialises every caller. Stripe it — N locks, key picks one.
// Exact per key, independent across keys. The same idea as the sharded LRU.
public sealed class StripedCounts {
    private readonly object[] _locks;
    private readonly Dictionary<string, long>[] _maps;
    public StripedCounts(int stripes) {
        _locks = new object[stripes]; _maps = new Dictionary<string, long>[stripes];
        for (int i = 0; i < stripes; i++) { _locks[i] = new object(); _maps[i] = new(); }
    }
    private int Stripe(string k) => (int)((uint)k.GetHashCode() % (uint)_locks.Length);
    public void Inc(string k) {
        int s = Stripe(k);
        lock (_locks[s]) _maps[s][k] = _maps[s].GetValueOrDefault(k) + 1;
    }
    public long Get(string k) { int s = Stripe(k); lock (_locks[s]) return _maps[s].GetValueOrDefault(k); }
}

// ---- C10. Stopping a worker: a CancellationToken, not a plain bool. A plain bool read in a
// loop may be hoisted by the JIT and never re-read; the token is thread-safe and composable.
public static class Worker {
    public static Task<long> RunAsync(CancellationToken ct) => Task.Run(() => {
        long spins = 0;
        while (!ct.IsCancellationRequested) spins++;
        return spins;
    });
}

// ---- C11. Read-mostly config without locks: publish an IMMUTABLE snapshot and swap the
// reference. Readers never lock and always see one complete version; a writer builds a new
// dictionary and swaps it in one atomic reference write.
public sealed class SnapshotConfig {
    private Dictionary<string, string> _current = new();          // never mutated after publish
    public string Get(string k) => Volatile.Read(ref _current).GetValueOrDefault(k);
    public IReadOnlyDictionary<string, string> Snapshot => Volatile.Read(ref _current);
    public void Publish(Dictionary<string, string> next) => Volatile.Write(ref _current, new(next));
}

// ---- C12. Proving thread-safety in a pad with no test framework: release N threads at the
// same instant with a Barrier, run the operation many times, then check an invariant.
public static class Stress {
    public static void Run(int threads, int iterations, Action<int> body) {
        using var start = new Barrier(threads);
        var ts = Enumerable.Range(0, threads).Select(t => new Thread(() => {
            start.SignalAndWait();                       // everyone starts together: maximum overlap
            for (int i = 0; i < iterations; i++) body(t);
        })).ToList();
        ts.ForEach(t => t.Start());
        ts.ForEach(t => t.Join());
    }
}

// ---- C13. Async fan-out. Awaiting calls one by one in a loop runs them IN SEQUENCE; starting them
// all and awaiting Task.WhenAll runs them CONCURRENTLY. Bound the fan-out with SemaphoreSlim.
// Never block on async code with .Result or .Wait(): under a single-threaded SynchronizationContext
// (UI apps, classic ASP.NET) the continuation needs the thread you are blocking — a deadlock;
// everywhere else it wastes a thread-pool thread. Async all the way down.
public static class AsyncFanOut {
    public static async Task<int[]> Sequential(Func<int, Task<int>> fetch, int n) {
        var r = new int[n];
        for (int i = 0; i < n; i++) r[i] = await fetch(i);     // waits for each before starting the next
        return r;
    }

    public static Task<int[]> Concurrent(Func<int, Task<int>> fetch, int n) =>
        Task.WhenAll(Enumerable.Range(0, n).Select(fetch));     // all started first, then awaited together

    public static async Task<int[]> Bounded(Func<int, Task<int>> fetch, int n, int maxInFlight) {
        using var gate = new SemaphoreSlim(maxInFlight);
        return await Task.WhenAll(Enumerable.Range(0, n).Select(async i => {
            await gate.WaitAsync();
            try { return await fetch(i); }
            finally { gate.Release(); }                        // in finally: an exception must not leak a slot
        }));
    }
}
