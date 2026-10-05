// A03 — LFU cache with GetRank(), LRU as the tie-breaker. Reported Feb 2026 (Hello Interview)
// as the Staff-level variant of the AI round's cache question.
//
// Rank is defined as the key's position in KEEP order: rank 1 is the entry the cache would
// evict last (highest frequency, most recent among equals); rank Count is the next victim.
// State that definition before writing code — the statement does not fix it.

public sealed class LfuRankCache<TKey, TValue> {
    private sealed class Entry { public TKey Key; public TValue Value; public int Freq; }

    private readonly int _capacity;
    private readonly Dictionary<TKey, LinkedListNode<Entry>> _byKey = new();
    // frequency → entries at that frequency, First = most recent. One list per frequency
    // is what gives O(1) Get/Put: a touch moves a node from list f to list f+1.
    private readonly Dictionary<int, LinkedList<Entry>> _buckets = new();
    // frequency → number of keys, kept sorted so GetRank can sum "everyone more frequent".
    private readonly SortedDictionary<int, int> _freqCounts = new();
    private int _minFreq;

    public LfuRankCache(int capacity) {
        if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        _capacity = capacity;
    }

    public int Count => _byKey.Count;

    public bool TryGet(TKey key, out TValue value) {
        if (!_byKey.TryGetValue(key, out var node)) { value = default; return false; }
        Touch(node);
        value = node.Value.Value;
        return true;
    }

    public void Put(TKey key, TValue value) {
        if (_byKey.TryGetValue(key, out var node)) {
            node.Value.Value = value;
            Touch(node);
            return;
        }
        if (_byKey.Count == _capacity) {
            var list = _buckets[_minFreq];
            var victim = list.Last;                    // least recent among the least frequent
            Detach(victim);
            _byKey.Remove(victim.Value.Key);
        }
        var fresh = new LinkedListNode<Entry>(new Entry { Key = key, Value = value, Freq = 1 });
        Attach(fresh);
        _byKey[key] = fresh;
        _minFreq = 1;                                  // a new key always has the lowest frequency
    }

    // O(F + B): F = distinct frequencies above this key's, B = size of its own bucket.
    // Not O(1), and that is fine as long as it is said. An order-statistics tree gets O(log n).
    // GetRank does NOT count as a use — reading the rank must not change it.
    public int GetRank(TKey key) {
        if (!_byKey.TryGetValue(key, out var node)) return -1;
        int f = node.Value.Freq, rank = 1;
        foreach (var (freq, count) in _freqCounts)
            if (freq > f) rank += count;
        for (var n = _buckets[f].First; n != node; n = n.Next) rank++;
        return rank;
    }

    private void Touch(LinkedListNode<Entry> node) {
        int f = node.Value.Freq;
        Detach(node);
        if (f == _minFreq && !_buckets.ContainsKey(f)) _minFreq = f + 1;
        node.Value.Freq = f + 1;
        Attach(node);
    }

    private void Attach(LinkedListNode<Entry> node) {
        int f = node.Value.Freq;
        if (!_buckets.TryGetValue(f, out var list)) _buckets[f] = list = new LinkedList<Entry>();
        list.AddFirst(node);
        _freqCounts[f] = _freqCounts.GetValueOrDefault(f) + 1;
    }

    // Empty buckets are deleted, not left behind: otherwise _minFreq bookkeeping and the
    // GetRank walk both slow down over time.
    private void Detach(LinkedListNode<Entry> node) {
        int f = node.Value.Freq;
        var list = _buckets[f];
        list.Remove(node);
        if (list.Count == 0) _buckets.Remove(f);
        if (--_freqCounts[f] == 0) _freqCounts.Remove(f);
    }
}
