// Q1 — LRU cache with per-entry TTL.
public class LruTtlCache {

    private sealed class Node {
        public int Key, Value;
        public long ExpiresAt;              // absolute time, in the clock's own units
        public Node Prev, Next;
    }

    private readonly int _capacity;
    private readonly Func<long> _clock;
    private readonly Dictionary<int, Node> _map;
    private readonly Node _head = new();   // sentinel: most-recently-used side
    private readonly Node _tail = new();   // sentinel: eviction side

    public LruTtlCache(int capacity, Func<long> clock = null) {
        if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        _capacity = capacity;
        _clock    = clock ?? (() => DateTimeOffset.UtcNow.ToUnixTimeMilliseconds());
        _map      = new Dictionary<int, Node>(capacity);
        _head.Next = _tail;
        _tail.Prev = _head;
    }

    public int Get(int key) {
        if (!_map.TryGetValue(key, out var node)) return -1;

        if (IsExpired(node)) {              // lazy expiry: dead on read, so drop it now
            Remove(node);
            return -1;
        }
        MoveToFront(node);
        return node.Value;
    }

    public void Put(int key, int value, long ttl) {
        long expiresAt = _clock() + ttl;

        if (_map.TryGetValue(key, out var existing)) {
            existing.Value     = value;     // a re-put renews the TTL
            existing.ExpiresAt = expiresAt;
            MoveToFront(existing);
            return;
        }

        if (_map.Count == _capacity) {
            var victim = _tail.Prev;        // strict O(1): always the LRU end
            Remove(victim);
        }

        var node = new Node { Key = key, Value = value, ExpiresAt = expiresAt };
        _map[key] = node;
        LinkFront(node);
    }

    // An entry is dead the moment the clock reaches its expiry.
    private bool IsExpired(Node n) => _clock() >= n.ExpiresAt;

    private void Remove(Node n) {
        Unlink(n);
        _map.Remove(n.Key);
    }

    private void Unlink(Node n) {
        n.Prev.Next = n.Next;
        n.Next.Prev = n.Prev;
    }

    private void LinkFront(Node n) {
        n.Next = _head.Next;
        n.Prev = _head;
        _head.Next.Prev = n;
        _head.Next = n;
    }

    private void MoveToFront(Node n) {
        Unlink(n);
        LinkFront(n);
    }

    public int Count => _map.Count;         // includes entries that are expired but not yet reclaimed
}
