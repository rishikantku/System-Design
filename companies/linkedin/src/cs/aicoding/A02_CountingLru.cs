// A02 — LRU with counters, and predicting the hit ratio before measuring it.
// Reported Sep 2026 (PracHub, IC2): "LRU cache with counters", then reason about hit/miss
// under different workloads. The code is small; the point is the prediction.

public readonly record struct CacheStats(long Hits, long Misses, long Evictions) {
    public long Requests => Hits + Misses;
    public double HitRatio => Requests == 0 ? 0 : (double)Hits / Requests;
}

public sealed class CountingLruCache<TKey, TValue> {
    private readonly LruCache<TKey, TValue> _lru;
    private readonly int _capacity;
    private long _hits, _misses, _evictions;

    public CountingLruCache(int capacity) { _capacity = capacity; _lru = new LruCache<TKey, TValue>(capacity); }

    // Read-through: on a miss, load from the source and insert. That is how hit ratio is
    // normally measured — a miss is a trip to the slow thing behind the cache.
    public TValue GetOrLoad(TKey key, Func<TKey, TValue> load) {
        if (_lru.TryGet(key, out var v)) { _hits++; return v; }
        _misses++;
        v = load(key);
        if (_lru.Count == _capacity) _evictions++;
        _lru.Put(key, v);
        return v;
    }

    // Counters are plain longs because this class is single-threaded. If it is made
    // thread-safe with a lock, they ride inside the lock. If they must be read without the
    // lock (a metrics scraper), use Interlocked.Read / Interlocked.Increment.
    public CacheStats Stats => new(_hits, _misses, _evictions);
}

public static class Workloads {
    // 0,1,2,…,n-1 repeated. With n > capacity, LRU hits NOTHING: every key is evicted just
    // before it is needed again. The classic LRU pathology — a scan larger than the cache.
    public static IEnumerable<int> Cyclic(int distinct, int length) {
        for (int i = 0; i < length; i++) yield return i % distinct;
    }

    // Uniform random over `distinct` keys: expected steady-state hit ratio ≈ capacity / distinct.
    public static IEnumerable<int> Uniform(int distinct, int length, int seed) {
        var r = new Random(seed);
        for (int i = 0; i < length; i++) yield return r.Next(distinct);
    }

    // Skewed (Zipf-like, s = 1): a few keys take most traffic, so a small cache does well.
    public static IEnumerable<int> Skewed(int distinct, int length, int seed) {
        var r = new Random(seed);
        var cdf = new double[distinct];
        double sum = 0;
        for (int k = 0; k < distinct; k++) { sum += 1.0 / (k + 1); cdf[k] = sum; }
        for (int i = 0; i < length; i++) {
            double u = r.NextDouble() * sum;
            int idx = Array.BinarySearch(cdf, u);
            yield return idx >= 0 ? idx : ~idx;
        }
    }

    public static CacheStats Run(int capacity, IEnumerable<int> keys) {
        var c = new CountingLruCache<int, int>(capacity);
        foreach (var k in keys) c.GetOrLoad(k, x => x);
        return c.Stats;
    }
}
