// G02 — the friendship graph, in three incremental parts. Reported for LinkedIn's AI-assisted
// round on LeetCode Discuss (supplied by the reader, Oct 2026): CoderPad, boilerplate and test
// cases provided, an AI tab. Part 1 shortest path as the sequence of users; Part 2 the distance;
// Part 3 suggest friends by mutual connections. The interviewer watched code reuse and how the
// structure evolved — so all three parts sit on one BFS.

public sealed class FriendGraph {
    private readonly Dictionary<int, HashSet<int>> _adj = new();

    // Friendship is symmetric. The input adjacency list may list an edge once, so normalise it.
    public FriendGraph(IReadOnlyDictionary<int, List<int>> adjacency) {
        foreach (var (u, friends) in adjacency) {
            Node(u);
            foreach (var v in friends) { if (v == u) continue; Node(u).Add(v); Node(v).Add(u); }
        }
    }

    private HashSet<int> Node(int u) {
        if (!_adj.TryGetValue(u, out var s)) _adj[u] = s = new HashSet<int>();
        return s;
    }

    // The shared core: BFS from `from`, recording each user's parent, stopping once `to` is seen.
    // Returns null if `to` is unreachable. Marking on ENQUEUE keeps every user queued once.
    private Dictionary<int, int> ParentsUntil(int from, int to) {
        var parent = new Dictionary<int, int> { [from] = from };
        var queue = new Queue<int>();
        queue.Enqueue(from);
        while (queue.Count > 0) {
            int u = queue.Dequeue();
            if (u == to) return parent;
            foreach (var v in _adj[u]) {
                if (parent.ContainsKey(v)) continue;
                parent[v] = u;
                queue.Enqueue(v);
            }
        }
        return null;
    }

    // Part 1. The users traversed from a to b, inclusive. Empty if unreachable or unknown.
    public IReadOnlyList<int> ShortestPath(int a, int b) {
        if (!_adj.ContainsKey(a) || !_adj.ContainsKey(b)) return Array.Empty<int>();
        var parent = ParentsUntil(a, b);
        if (parent == null) return Array.Empty<int>();
        var path = new List<int>();
        for (int at = b; ; at = parent[at]) { path.Add(at); if (at == a) break; }
        path.Reverse();
        return path;
    }

    // Part 2. Reuses Part 1: hops = users on the path minus one; -1 if there is no path.
    public int Distance(int a, int b) {
        var path = ShortestPath(a, b);
        return path.Count == 0 ? -1 : path.Count - 1;
    }

    // Part 3. Friends of friends who are not already friends, ranked by mutual friends
    // (most first), ties by id so the output is deterministic — and therefore testable.
    public IReadOnlyList<(int User, int Mutual)> SuggestFriends(int user, int k) {
        if (!_adj.TryGetValue(user, out var mine)) return Array.Empty<(int, int)>();
        var mutual = new Dictionary<int, int>();
        foreach (var f in mine)
            foreach (var ff in _adj[f])
                if (ff != user && !mine.Contains(ff))
                    mutual[ff] = mutual.GetValueOrDefault(ff) + 1;
        return mutual.OrderByDescending(kv => kv.Value).ThenBy(kv => kv.Key)
                     .Take(k).Select(kv => (kv.Key, kv.Value)).ToList();
    }
}
