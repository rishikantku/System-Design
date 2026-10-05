// Debugging exercises: each type is broken. The page states the symptom a user reported and
// asks you to find the cause before revealing it. Tests.cs reproduces every symptom.

using System.Collections.Concurrent;

// D1 — symptom: "the entry I used most recently is the one that disappears."
public class D1_Lru {
    private readonly int _cap;
    private readonly Dictionary<int, LinkedListNode<(int K, int V)>> _map = new();
    private readonly LinkedList<(int K, int V)> _order = new();      // First = most recent
    public D1_Lru(int cap) => _cap = cap;

    public int Get(int k) {
        if (!_map.TryGetValue(k, out var n)) return -1;
        _order.Remove(n); _order.AddFirst(n);
        return n.Value.V;
    }

    public void Put(int k, int v) {
        if (_map.TryGetValue(k, out var n)) { _order.Remove(n); _map.Remove(k); }
        else if (_map.Count == _cap) { _map.Remove(_order.First.Value.K); _order.RemoveFirst(); }
        _map[k] = _order.AddFirst((k, v));
    }
}

// D2 — symptom: "under load, a value I just wrote is sometimes gone on the next read."
// BetweenCheckAndAct is a test seam: it lets the test interleave a second thread exactly there.
public class D2_TtlCache {
    private sealed class Entry { public int Value; public long Exp; }
    private readonly Dictionary<int, Entry> _map = new();
    private readonly object _gate = new();
    private readonly Func<long> _now;
    public Action BetweenCheckAndAct = () => { };
    public D2_TtlCache(Func<long> now) => _now = now;

    public void Put(int k, int v, long ttl) { lock (_gate) _map[k] = new Entry { Value = v, Exp = _now() + ttl }; }

    public int Get(int k) {
        Entry e;
        lock (_gate) { if (!_map.TryGetValue(k, out e)) return -1; }
        if (_now() >= e.Exp) {
            BetweenCheckAndAct();
            lock (_gate) _map.Remove(k);
            return -1;
        }
        return e.Value;
    }
}

// D3 — symptom: "shortest path is correct, but the queue holds about twice as many entries as
// there are cells — and on the word-ladder graph, where nodes have ~25 neighbours, far more."
public static class D3_Bfs {
    public static (int Dist, long Enqueued) Shortest(int n) {
        var seen = new bool[n, n];
        var q = new Queue<(int R, int C, int D)>();
        q.Enqueue((0, 0, 0));
        long enq = 1;
        while (q.Count > 0) {
            var (r, c, d) = q.Dequeue();
            if (seen[r, c]) continue;
            seen[r, c] = true;
            if (r == n - 1 && c == n - 1) return (d, enq);
            foreach (var (dr, dc) in new[] { (1, 0), (0, 1), (-1, 0), (0, -1) }) {
                int nr = r + dr, nc = c + dc;
                if (nr < 0 || nc < 0 || nr >= n || nc >= n || seen[nr, nc]) continue;
                q.Enqueue((nr, nc, d + 1)); enq++;
            }
        }
        return (-1, enq);
    }
}

// D4 — symptom: "page-view counts are lower than the access log says."
public class D4_Counter {
    private readonly ConcurrentDictionary<string, int> _counts = new();
    public void Hit(string page) {
        _counts.TryGetValue(page, out var current);
        _counts[page] = current + 1;
    }
    public int Get(string page) => _counts.GetValueOrDefault(page);
}

// D5 — symptom: "the transfer service hangs a few times a day; thread dumps show two
// threads each waiting on a lock." AfterFirstLock is a test seam.
public sealed class Account { public int Id; public long Balance; }
public class D5_Bank {
    public Action AfterFirstLock = () => { };
    public void Transfer(Account from, Account to, long amount) {
        lock (from) {
            AfterFirstLock();
            lock (to) {
                from.Balance -= amount;
                to.Balance += amount;
            }
        }
    }
}

// D6 — symptom: "merged coverage is smaller than the input coverage for some batches."
public static class D6_Merge {
    public static List<(int S, int E)> Merge(List<(int S, int E)> xs) {
        var res = new List<(int S, int E)>();
        foreach (var x in xs) {
            if (res.Count > 0 && x.S <= res[^1].E) res[^1] = (res[^1].S, Math.Max(res[^1].E, x.E));
            else res.Add(x);
        }
        return res;
    }
}

// D7 — symptom: "the shuffled feed puts some orders up far more often than others."
// pick(n) returns a uniform integer in [0, n); it is a parameter so the test can enumerate.
public static class D7_Shuffle {
    public static void Shuffle<T>(T[] a, Func<int, int> pick) {
        for (int i = a.Length - 1; i > 0; i--) {
            int j = pick(a.Length);
            (a[i], a[j]) = (a[j], a[i]);
        }
    }
}

// D8 — symptom: "after merging two config trees, editing the result changed one of the inputs."
public sealed class TNode {
    public string Name; public string Value;
    public Dictionary<string, TNode> Children = new();
}
public static class D8_TreeMerge {
    // b wins on conflicting values; children are merged by name.
    public static TNode Merge(TNode a, TNode b) {
        if (a == null) return b;
        if (b == null) return a;
        var result = new TNode { Name = a.Name, Value = b.Value ?? a.Value, Children = a.Children };
        foreach (var (name, child) in b.Children)
            result.Children[name] = Merge(a.Children.GetValueOrDefault(name), child);
        return result;
    }
}

// ---------------------------------------------------------------- the fixes, tested alongside
public static class Fixes {
    // D2: remove only if the entry is still the one we judged expired — check and act under ONE lock.
    public static int D2_Get(Dictionary<int, (int V, long Exp)> map, object gate, int k, long now) {
        lock (gate) {
            if (!map.TryGetValue(k, out var e)) return -1;
            if (now >= e.Exp) { map.Remove(k); return -1; }
            return e.V;
        }
    }

    // D4: one atomic read-modify-write.
    public static void D4_Hit(ConcurrentDictionary<string, int> counts, string page) =>
        counts.AddOrUpdate(page, 1, (_, c) => c + 1);

    // D5: acquire locks in a global order (by Id), whatever the direction of the transfer.
    public static void D5_Transfer(Account from, Account to, long amount, Action afterFirst = null) {
        var (first, second) = from.Id < to.Id ? (from, to) : (to, from);
        lock (first) {
            afterFirst?.Invoke();
            lock (second) { from.Balance -= amount; to.Balance += amount; }
        }
    }

    // D7: j must range over [0, i] — the unshuffled prefix — not the whole array.
    public static void D7_Shuffle<T>(T[] a, Func<int, int> pick) {
        for (int i = a.Length - 1; i > 0; i--) {
            int j = pick(i + 1);
            (a[i], a[j]) = (a[j], a[i]);
        }
    }

    // D8: build new nodes all the way down; never hand out an input's collection.
    public static TNode D8_Merge(TNode a, TNode b) {
        if (a == null && b == null) return null;
        var result = new TNode { Name = (a ?? b).Name, Value = b?.Value ?? a?.Value };
        var names = (a?.Children.Keys ?? Enumerable.Empty<string>()).Union(b?.Children.Keys ?? Enumerable.Empty<string>());
        foreach (var name in names)
            result.Children[name] = D8_Merge(a?.Children.GetValueOrDefault(name), b?.Children.GetValueOrDefault(name));
        return result;
    }

    // R8: cache the Lazy<Task>, not the value, so concurrent first readers share one load.
    public sealed class ReadThrough {
        private readonly ConcurrentDictionary<string, Lazy<string>> _cache = new();
        private readonly Func<string, string> _load;
        public ReadThrough(Func<string, string> load) => _load = load;
        public string Get(string id) =>
            _cache.GetOrAdd(id, k => new Lazy<string>(() => _load(k), LazyThreadSafetyMode.ExecutionAndPublication)).Value;
    }
}
