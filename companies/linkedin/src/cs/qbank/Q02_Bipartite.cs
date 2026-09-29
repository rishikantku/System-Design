// Q2 — can the animals be split into two groups with no conflict inside a group?
public static class AnimalGrouping {

    public static bool CanSplit(Dictionary<int, List<int>> conflicts) {
        if (conflicts == null || conflicts.Count == 0) return true;

        // 1. "cannot share a side" is mutual, but the input may declare it one way only.
        //    Build a symmetric adjacency list before colouring anything.
        var adj = new Dictionary<int, List<int>>();

        void Touch(int a) { if (!adj.ContainsKey(a)) adj[a] = new List<int>(); }

        foreach (var pair in conflicts) {
            Touch(pair.Key);
            foreach (int other in pair.Value ?? new List<int>()) {
                if (other == pair.Key) return false;   // conflicts with itself: unsatisfiable
                Touch(other);
                adj[pair.Key].Add(other);
                adj[other].Add(pair.Key);
            }
        }

        // 2. Two-colour every component. A conflict edge must join different colours.
        var side = new Dictionary<int, int>();

        foreach (int start in adj.Keys) {
            if (side.ContainsKey(start)) continue;      // already coloured in an earlier component

            side[start] = 0;
            var queue = new Queue<int>();
            queue.Enqueue(start);

            while (queue.Count > 0) {
                int cur = queue.Dequeue();
                foreach (int next in adj[cur]) {
                    if (!side.TryGetValue(next, out int colour)) {
                        side[next] = 1 - side[cur];
                        queue.Enqueue(next);
                    } else if (colour == side[cur]) {
                        return false;                  // odd cycle: no two-way split exists
                    }
                }
            }
        }
        return true;
    }

    // Same walk, but hands back the actual two groups — what a follow-up usually wants.
    public static (List<int> Left, List<int> Right) Split(Dictionary<int, List<int>> conflicts) {
        if (!CanSplit(conflicts)) throw new InvalidOperationException("Not bipartite.");

        var adj = new Dictionary<int, List<int>>();
        void Touch(int a) { if (!adj.ContainsKey(a)) adj[a] = new List<int>(); }
        foreach (var pair in conflicts) {
            Touch(pair.Key);
            foreach (int other in pair.Value ?? new List<int>()) {
                Touch(other); adj[pair.Key].Add(other); adj[other].Add(pair.Key);
            }
        }

        var side = new Dictionary<int, int>();
        foreach (int start in adj.Keys) {
            if (side.ContainsKey(start)) continue;
            side[start] = 0;
            var queue = new Queue<int>(); queue.Enqueue(start);
            while (queue.Count > 0) {
                int cur = queue.Dequeue();
                foreach (int next in adj[cur])
                    if (!side.ContainsKey(next)) { side[next] = 1 - side[cur]; queue.Enqueue(next); }
            }
        }

        var left  = side.Where(kv => kv.Value == 0).Select(kv => kv.Key).OrderBy(x => x).ToList();
        var right = side.Where(kv => kv.Value == 1).Select(kv => kv.Key).OrderBy(x => x).ToList();
        return (left, right);
    }
}
