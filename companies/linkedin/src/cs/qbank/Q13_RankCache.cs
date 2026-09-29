// Q13 — fixed-capacity cache that evicts the lowest static rank.
public interface IRankedDataSource<TKey, TValue> {
    TValue Get(TKey key);      // slow: this is what the cache exists to avoid
    int    GetRank(TKey key);  // static and distinct across keys
}

public class RankCache<TKey, TValue> {

    // Ranks are distinct, so comparing on rank alone is a total order and nothing is lost.
    // If ranks could repeat, this comparer would silently drop entries — worth saying out loud.
    private sealed class ByRank : IComparer<(int Rank, TKey Key)> {
        public int Compare((int Rank, TKey Key) a, (int Rank, TKey Key) b) => a.Rank.CompareTo(b.Rank);
    }

    private readonly int _capacity;
    private readonly IRankedDataSource<TKey, TValue> _source;
    private readonly Dictionary<TKey, (TValue Value, int Rank)> _entries = new();
    private readonly SortedSet<(int Rank, TKey Key)> _byRank = new(new ByRank());

    public long Hits { get; private set; }
    public long Misses { get; private set; }
    public long Admitted { get; private set; }
    public long Rejected { get; private set; }

    public RankCache(int capacity, IRankedDataSource<TKey, TValue> source) {
        if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        _capacity = capacity;
        _source   = source ?? throw new ArgumentNullException(nameof(source));
    }

    public TValue Get(TKey key) {
        if (_entries.TryGetValue(key, out var hit)) { Hits++; return hit.Value; }

        Misses++;
        TValue value = _source.Get(key);
        int    rank   = _source.GetRank(key);
        Admit(key, value, rank);
        return value;                                   // returned either way; caching is separate
    }

    private void Admit(TKey key, TValue value, int rank) {
        if (_entries.Count == _capacity) {
            var lowest = _byRank.Min;

            // The newcomer is worth less than everything already held. Evicting something better
            // to store something worse is strictly wrong, so decline to cache it.
            if (rank < lowest.Rank) { Rejected++; return; }

            _byRank.Remove(lowest);
            _entries.Remove(lowest.Key);
        }
        _entries[key] = (value, rank);
        _byRank.Add((rank, key));
        Admitted++;
    }

    public bool Contains(TKey key) => _entries.ContainsKey(key);
    public int  Count => _entries.Count;
    public int  LowestRank => _byRank.Count == 0 ? int.MinValue : _byRank.Min.Rank;
}
