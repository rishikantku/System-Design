// Code-review exercises: each type below is written the way an assistant plausibly returns it —
// tidy, commented, compiles, passes the obvious test. Each has one defect that matters.
// The page asks "would you accept this?" before revealing which. Tests.cs proves every defect
// is real, so none of these is a straw man.

using System.Collections.Concurrent;
using System.Threading.Channels;

// R1 — "Here is an O(1) LRU cache using a dictionary and a doubly linked list."
public class R1_LruCache {
    private readonly int _capacity;
    private readonly Dictionary<int, LinkedListNode<(int Key, int Value)>> _map = new();
    private readonly LinkedList<(int Key, int Value)> _list = new();

    public R1_LruCache(int capacity) => _capacity = capacity;

    public int Get(int key) {
        // Return the cached value if present.
        return _map.TryGetValue(key, out var node) ? node.Value.Value : -1;
    }

    public void Put(int key, int value) {
        if (_map.TryGetValue(key, out var existing)) {
            _list.Remove(existing);
        } else if (_map.Count == _capacity) {
            // Evict the least recently used entry from the tail.
            _map.Remove(_list.Last.Value.Key);
            _list.RemoveLast();
        }
        _map[key] = _list.AddFirst((key, value));
    }
}

// R2 — "I added TTL support. Expired entries return -1, as required."
public class R2_LruTtl {
    private readonly int _capacity;
    private readonly Func<long> _now;
    private readonly Dictionary<int, LinkedListNode<(int Key, int Value, long Exp)>> _map = new();
    private readonly LinkedList<(int Key, int Value, long Exp)> _list = new();

    public R2_LruTtl(int capacity, Func<long> now) { _capacity = capacity; _now = now; }
    public int Count => _map.Count;

    public int Get(int key) {
        if (!_map.TryGetValue(key, out var node)) return -1;
        if (_now() >= node.Value.Exp) return -1;           // expired
        _list.Remove(node);
        _list.AddFirst(node);
        return node.Value.Value;
    }

    public void Put(int key, int value, long ttl) {
        if (_map.TryGetValue(key, out var old)) _list.Remove(old);
        else if (_map.Count == _capacity) { _map.Remove(_list.Last.Value.Key); _list.RemoveLast(); }
        _map[key] = _list.AddFirst((key, value, _now() + ttl));
    }
}

// R3 — "To make it thread-safe I switched to ConcurrentDictionary, which is lock-free."
public class R3_ConcurrentLru {
    private readonly int _capacity;
    private readonly ConcurrentDictionary<int, LinkedListNode<(int Key, int Value)>> _map = new();
    private readonly LinkedList<(int Key, int Value)> _list = new();

    public R3_ConcurrentLru(int capacity) => _capacity = capacity;

    public int Get(int key) {
        if (!_map.TryGetValue(key, out var node)) return -1;
        _list.Remove(node);
        _list.AddFirst(node);
        return node.Value.Value;
    }

    public void Put(int key, int value) {
        if (_map.TryRemove(key, out var old)) _list.Remove(old);
        if (_map.Count >= _capacity && _list.Last != null) {
            _map.TryRemove(_list.Last.Value.Key, out _);
            _list.RemoveLast();
        }
        _map[key] = _list.AddFirst((key, value));
    }

    public int ListCount => _list.Count;
    public int MapCount => _map.Count;
}

// R4 — "Sort by start, then merge overlapping neighbours. O(n log n)."
public static class R4_Merge {
    public static List<(int Start, int End)> Merge(List<(int Start, int End)> xs) {
        var sorted = xs.OrderBy(x => x.Start).ToList();
        var result = new List<(int Start, int End)>();
        foreach (var cur in sorted) {
            if (result.Count > 0 && cur.Start <= result[^1].End)
                result[^1] = (result[^1].Start, cur.End);   // extend the previous interval
            else
                result.Add(cur);
        }
        return result;
    }
}

// R5 — "TopK keeps counts in a dictionary and returns the k most frequent."
public class R5_TopK {
    private readonly Dictionary<string, int> _counts = new();
    public void Add(string item) => _counts[item] = _counts.GetValueOrDefault(item) + 1;

    public List<string> Top(int k) =>
        _counts.OrderByDescending(kv => kv.Value).ThenBy(kv => kv.Key).Take(k).Select(kv => kv.Key).ToList();
}

// R6 — "rand10 from rand7: add two draws and take it modulo 10."
public static class R6_Rand10 {
    public static int Rand10(Func<int> rand7) => (rand7() + rand7()) % 10 + 1;
}

// R7 — "Parses each line and skips anything malformed, so bad input never crashes the job."
public static class R7_Parse {
    public static List<Event> ParseAll(IEnumerable<string> lines) {
        var result = new List<Event>();
        try {
            foreach (var line in lines) {
                var parts = line.Split(',');
                result.Add(new Event(parts[0], parts[1], long.Parse(parts[2]), int.Parse(parts[3])));
            }
        } catch (Exception) {
            // ignore malformed input
        }
        return result;
    }
}

// R8 — "Read-through cache for the slow profile service. GetOrAdd is atomic, so each profile
//       is loaded only once."
public class R8_ReadThrough {
    private readonly ConcurrentDictionary<string, string> _cache = new();
    private readonly Func<string, string> _load;
    public R8_ReadThrough(Func<string, string> load) => _load = load;
    public string Get(string id) => _cache.GetOrAdd(id, _load);
}

// R9 — "A blocking queue with Monitor.Wait/Pulse."
public class R9_BlockingQueue<T> {
    private readonly Queue<T> _q = new();
    private readonly int _cap;
    private readonly object _lock = new();
    public R9_BlockingQueue(int cap) => _cap = cap;

    public void Enqueue(T item) {
        lock (_lock) {
            if (_q.Count == _cap) Monitor.Wait(_lock);
            _q.Enqueue(item);
            Monitor.Pulse(_lock);
        }
    }

    public T Dequeue() {
        lock (_lock) {
            if (_q.Count == 0) Monitor.Wait(_lock);
            var item = _q.Dequeue();
            Monitor.Pulse(_lock);
            return item;
        }
    }
}

// R10 — "A background sweeper removes expired entries every second so memory stays bounded."
public class R10_Sweeper {
    private readonly Dictionary<int, long> _expiry = new();
    private readonly object _gate = new();
    public void Put(int key, long exp) { lock (_gate) _expiry[key] = exp; }
    public bool Alive(int key, long now) { lock (_gate) return _expiry.TryGetValue(key, out var e) && now < e; }

    // Runs on a timer. Returns how many entries it examined, for the test.
    public int Sweep(long now) {
        lock (_gate) {
            var dead = _expiry.Where(kv => now >= kv.Value).Select(kv => kv.Key).ToList();
            foreach (var k in dead) _expiry.Remove(k);
            return _expiry.Count + dead.Count;
        }
    }
}

// R11 — "A thread-safe logger: one lock so lines never interleave."
public class R11_Logger {
    private readonly ILogSink _sink;
    private readonly object _lock = new();
    public R11_Logger(ILogSink sink) => _sink = sink;
    public void Log(Severity sev, string msg) {
        lock (_lock) {
            _sink.Write($"{DateTime.UtcNow:O} {sev} {msg}");
        }
    }
}

// R12 — "Async read-through cache. A SemaphoreSlim guards the load, since you cannot await
//        inside a lock."
public class R12_AsyncCache {
    private readonly Dictionary<string, string> _cache = new();
    private readonly SemaphoreSlim _gate = new(1, 1);
    private readonly Func<string, Task<string>> _load;
    public R12_AsyncCache(Func<string, Task<string>> load) => _load = load;

    public async Task<string> GetAsync(string key) {
        await _gate.WaitAsync();
        if (_cache.TryGetValue(key, out var v)) { _gate.Release(); return v; }
        v = await _load(key);
        _cache[key] = v;
        _gate.Release();
        return v;
    }
}

// R13 — "Counts events in the last `window` seconds using per-second buckets."
public class R13_Window {
    private readonly int _w;
    private readonly long[] _stamp; private readonly int[] _count;
    public R13_Window(int w) { _w = w; _stamp = new long[w]; _count = new int[w]; Array.Fill(_stamp, -1); }
    public void Record(long now) {
        int s = (int)(now % _w);
        if (_stamp[s] != now) { _stamp[s] = now; _count[s] = 0; }
        _count[s]++;
    }
    public long Count(long now) {
        long t = 0;
        for (int i = 0; i < _w; i++) if (_stamp[i] >= now - _w && _stamp[i] <= now) t += _count[i];
        return t;
    }
}

// R14 — "Non-blocking logger: a bounded channel that drops when full, and a counter of drops."
public class R14_AsyncLogger {
    private readonly Channel<string> _ch = Channel.CreateBounded<string>(
        new BoundedChannelOptions(1024) { FullMode = BoundedChannelFullMode.DropWrite });
    public long Accepted, Dropped, Written;

    public R14_AsyncLogger(ILogSink sink) =>
        _ = Task.Run(async () => { await foreach (var l in _ch.Reader.ReadAllAsync()) { sink.Write(l); Interlocked.Increment(ref Written); } });

    public void Log(string msg) {
        if (_ch.Writer.TryWrite(msg)) Interlocked.Increment(ref Accepted);
        else Interlocked.Increment(ref Dropped);
    }
    public void Complete() => _ch.Writer.TryComplete();
}
