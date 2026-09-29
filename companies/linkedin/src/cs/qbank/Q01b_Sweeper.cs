// Q1 follow-up — the same cache with a bounded background sweep.
// Get() is untouched: it still does lazy expiry and never waits for the sweeper.
public class SweptLruTtlCache {

    private sealed class Node {
        public int Key, Value;
        public long ExpiresAt;
        public long Version;               // bumped on every re-put, so stale heap entries are detectable
        public Node Prev, Next;
    }

    private readonly int _capacity;
    private readonly Func<long> _clock;
    private readonly Dictionary<int, Node> _map = new();
    private readonly PriorityQueue<(int Key, long Version), long> _expiries = new();  // priority = ExpiresAt
    private readonly Node _head = new(), _tail = new();
    private long _versionCounter;

    public SweptLruTtlCache(int capacity, Func<long> clock) {
        _capacity = capacity;
        _clock    = clock;
        _head.Next = _tail;
        _tail.Prev = _head;
    }

    public void Put(int key, int value, long ttl) {
        long expiresAt = _clock() + ttl;
        long version   = ++_versionCounter;

        if (_map.TryGetValue(key, out var node)) {
            node.Value = value; node.ExpiresAt = expiresAt; node.Version = version;
            MoveToFront(node);
        } else {
            if (_map.Count == _capacity) Remove(_tail.Prev);
            node = new Node { Key = key, Value = value, ExpiresAt = expiresAt, Version = version };
            _map[key] = node;
            LinkFront(node);
        }
        _expiries.Enqueue((key, version), expiresAt);
    }

    public int Get(int key) {
        if (!_map.TryGetValue(key, out var node)) return -1;
        if (_clock() >= node.ExpiresAt) { Remove(node); return -1; }
        MoveToFront(node);
        return node.Value;
    }

    // Called from a timer. budget caps the work so one sweep cannot stall the process.
    public int Sweep(int budget) {
        long now = _clock();
        int reclaimed = 0;

        while (reclaimed < budget && _expiries.TryPeek(out var top, out long due) && due <= now) {
            _expiries.Dequeue();

            // Stale entry: the key was re-put with a later TTL, so this record is not the live one.
            if (!_map.TryGetValue(top.Key, out var node) || node.Version != top.Version) continue;

            Remove(node);
            reclaimed++;
        }
        return reclaimed;
    }

    public int Count => _map.Count;
    public int PendingExpiries => _expiries.Count;

    private void Remove(Node n) { Unlink(n); _map.Remove(n.Key); }
    private void Unlink(Node n) { n.Prev.Next = n.Next; n.Next.Prev = n.Prev; }
    private void LinkFront(Node n) {
        n.Next = _head.Next; n.Prev = _head; _head.Next.Prev = n; _head.Next = n;
    }
    private void MoveToFront(Node n) { Unlink(n); LinkFront(n); }
}
