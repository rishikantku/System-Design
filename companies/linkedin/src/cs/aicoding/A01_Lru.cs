// A01 — the LRU ladder: plain LRU → LRU + TTL → thread-safe → sharded.
// Each level is a separate type so the page can show what changed between them.

// Level 1. The textbook structure: a map for lookup, a list for recency.
// LinkedList<T> is used instead of a hand-rolled node list because its LinkedListNode handle
// gives O(1) unlink, and in an interview the BCL type is one less thing to get wrong.
public class LruCache<TKey, TValue> {
    private readonly int _capacity;
    private readonly Dictionary<TKey, LinkedListNode<(TKey Key, TValue Value)>> _map;
    private readonly LinkedList<(TKey Key, TValue Value)> _order = new();   // First = most recent

    public LruCache(int capacity) {
        if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        _capacity = capacity;
        _map = new Dictionary<TKey, LinkedListNode<(TKey, TValue)>>(capacity);
    }

    public int Count => _map.Count;

    public bool TryGet(TKey key, out TValue value) {
        if (!_map.TryGetValue(key, out var node)) { value = default; return false; }
        _order.Remove(node);                 // a read is a use: move to the front
        _order.AddFirst(node);
        value = node.Value.Value;
        return true;
    }

    public void Put(TKey key, TValue value) {
        if (_map.TryGetValue(key, out var node)) {
            node.Value = (key, value);       // update in place, then treat it as a use
            _order.Remove(node);
            _order.AddFirst(node);
            return;
        }
        if (_map.Count == _capacity) {
            var victim = _order.Last;        // least recently used
            _order.RemoveLast();
            _map.Remove(victim.Value.Key);
        }
        _map[key] = _order.AddFirst((key, value));
    }
}

// The clock is injected. Not for elegance: without it, a TTL test needs Thread.Sleep and
// becomes slow and flaky. This is the first thing to tell an assistant when asking for TTL code.
public interface IClock { long NowMs { get; } }
public sealed class SystemClock : IClock { public long NowMs => Environment.TickCount64; }
public sealed class ManualClock : IClock { public long NowMs { get; set; } }

// Level 2. Every entry carries an absolute expiry. Expiry is checked lazily on read, and a
// bounded sweep reclaims entries that are never read again, so memory does not grow without
// limit and no single call pays for scanning the whole cache.
public class LruTtlCache<TKey, TValue> {
    private sealed class Entry {
        public TKey Key; public TValue Value; public long ExpiresAt;
    }

    private int _capacity;
    private readonly IClock _clock;
    private readonly Dictionary<TKey, LinkedListNode<Entry>> _map;
    private readonly LinkedList<Entry> _order = new();

    public LruTtlCache(int capacity, IClock clock) {
        if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        _capacity = capacity;
        _clock = clock ?? throw new ArgumentNullException(nameof(clock));
        _map = new Dictionary<TKey, LinkedListNode<Entry>>(capacity);
    }

    public int Count => _map.Count;

    public bool TryGet(TKey key, out TValue value) {
        value = default;
        if (!_map.TryGetValue(key, out var node)) return false;
        if (_clock.NowMs >= node.Value.ExpiresAt) {    // dead on read: reclaim it now
            Remove(node);
            return false;
        }
        _order.Remove(node);
        _order.AddFirst(node);
        value = node.Value.Value;
        return true;
    }

    public void Put(TKey key, TValue value, long ttlMs) {
        if (ttlMs <= 0) throw new ArgumentOutOfRangeException(nameof(ttlMs));
        long expiresAt = _clock.NowMs + ttlMs;
        if (_map.TryGetValue(key, out var node)) {
            node.Value.Value = value;
            node.Value.ExpiresAt = expiresAt;          // a re-put renews the TTL — say so out loud
            _order.Remove(node);
            _order.AddFirst(node);
            return;
        }
        if (_map.Count == _capacity) EvictOne();
        var entry = new Entry { Key = key, Value = value, ExpiresAt = expiresAt };
        _map[key] = _order.AddFirst(entry);
    }

    // Prefer an expired victim if one is at the cold end; otherwise evict the LRU entry.
    // Looking at only a few entries keeps Put O(1) — a full scan for "any expired entry" would not.
    private void EvictOne() {
        long now = _clock.NowMs;
        var n = _order.Last;
        for (int i = 0; i < 4 && n != null; i++, n = n.Previous)
            if (now >= n.Value.ExpiresAt) { Remove(n); return; }
        Remove(_order.Last);
    }

    // Bounded, incremental cleanup: walks at most `budget` entries from the cold end.
    // Called from a timer or piggy-backed on writes. Returns how many it reclaimed.
    public int SweepExpired(int budget) {
        long now = _clock.NowMs;
        int reclaimed = 0;
        var n = _order.Last;
        while (n != null && budget-- > 0) {
            var prev = n.Previous;
            if (now >= n.Value.ExpiresAt) { Remove(n); reclaimed++; }
            n = prev;
        }
        return reclaimed;
    }

    // Resizing at runtime (memory pressure, or a config push). Shrinking evicts immediately —
    // expired entries first, then from the cold end — so Count never exceeds the new capacity.
    public void Resize(int capacity) {
        if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        _capacity = capacity;
        while (_map.Count > _capacity) EvictOne();
    }

    private void Remove(LinkedListNode<Entry> n) {
        _order.Remove(n);
        _map.Remove(n.Value.Key);
    }
}

// Level 3. Thread-safe. One lock around the whole operation, because a Get *writes* — it
// moves a node in the recency list. A ConcurrentDictionary would protect the map and leave the
// list unprotected, which is the most common wrong answer an assistant gives here.
public sealed class SyncLruTtlCache<TKey, TValue> {
    private readonly LruTtlCache<TKey, TValue> _inner;
    private readonly object _gate = new();

    public SyncLruTtlCache(int capacity, IClock clock) => _inner = new LruTtlCache<TKey, TValue>(capacity, clock);

    public bool TryGet(TKey key, out TValue value) { lock (_gate) return _inner.TryGet(key, out value); }
    public void Put(TKey key, TValue value, long ttlMs) { lock (_gate) _inner.Put(key, value, ttlMs); }
    public int SweepExpired(int budget) { lock (_gate) return _inner.SweepExpired(budget); }
    public int Count { get { lock (_gate) return _inner.Count; } }
}

// Level 4. Millions of requests: one lock becomes the bottleneck. Split into N independent
// shards by key hash. Each shard is exact LRU; the whole cache is only approximately LRU —
// a hot shard can evict an entry that is younger than the oldest entry in a cold shard.
// That is the trade, and it is the sentence the interviewer wants to hear.
public sealed class ShardedLruTtlCache<TKey, TValue> {
    private readonly SyncLruTtlCache<TKey, TValue>[] _shards;

    public ShardedLruTtlCache(int capacity, int shards, IClock clock) {
        if (shards <= 0 || capacity < shards) throw new ArgumentOutOfRangeException(nameof(shards));
        _shards = new SyncLruTtlCache<TKey, TValue>[shards];
        for (int i = 0; i < shards; i++)
            _shards[i] = new SyncLruTtlCache<TKey, TValue>(capacity / shards, clock);
    }

    private SyncLruTtlCache<TKey, TValue> For(TKey key) =>
        _shards[(int)((uint)EqualityComparer<TKey>.Default.GetHashCode(key) % (uint)_shards.Length)];

    public bool TryGet(TKey key, out TValue value) => For(key).TryGet(key, out value);
    public void Put(TKey key, TValue value, long ttlMs) => For(key).Put(key, value, ttlMs);
    public int Count => _shards.Sum(s => s.Count);
}
