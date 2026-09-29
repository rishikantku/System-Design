// Q5 — shortest connection distance between two members.
public interface IMember {
    int GetMemberId();
    IList<IMember> GetConnections();
}

public static class ConnectionDistance {

    // Plain BFS from one side. Distance is counted in edges (hops).
    public static int Distance(IMember from, IMember to) {
        if (from == null || to == null) return -1;
        if (from.GetMemberId() == to.GetMemberId()) return 0;

        var seen  = new HashSet<int> { from.GetMemberId() };
        var queue = new Queue<IMember>();
        queue.Enqueue(from);
        int depth = 0;

        while (queue.Count > 0) {
            int levelSize = queue.Count;
            depth++;                                   // everything dequeued below is `depth` hops out

            for (int i = 0; i < levelSize; i++) {
                IMember cur = queue.Dequeue();
                foreach (IMember next in cur.GetConnections() ?? new List<IMember>()) {
                    if (next == null) continue;
                    int id = next.GetMemberId();
                    if (id == to.GetMemberId()) return depth;
                    if (seen.Add(id)) queue.Enqueue(next);
                }
            }
        }
        return -1;                                     // different components
    }

    // Bidirectional BFS. Each round expands whichever frontier is smaller, which is the
    // whole point when one member has 30 000 connections and the other has 40.
    public static int DistanceBidirectional(IMember from, IMember to) {
        if (from == null || to == null) return -1;
        if (from.GetMemberId() == to.GetMemberId()) return 0;

        var frontA = new Dictionary<int, IMember> { [from.GetMemberId()] = from };
        var frontB = new Dictionary<int, IMember> { [to.GetMemberId()]   = to   };
        var seenA  = new HashSet<int> { from.GetMemberId() };
        var seenB  = new HashSet<int> { to.GetMemberId()   };
        int depth = 0;

        while (frontA.Count > 0 && frontB.Count > 0) {
            // Expand the cheaper side. Cost of a round is the size of the frontier.
            if (frontA.Count > frontB.Count) {
                (frontA, frontB) = (frontB, frontA);
                (seenA,  seenB)  = (seenB,  seenA);
            }

            var next = new Dictionary<int, IMember>();
            depth++;

            foreach (IMember cur in frontA.Values) {
                foreach (IMember nb in cur.GetConnections() ?? new List<IMember>()) {
                    if (nb == null) continue;
                    int id = nb.GetMemberId();

                    if (seenB.Contains(id)) return depth;   // the two searches met
                    if (seenA.Add(id)) next[id] = nb;
                }
            }
            frontA = next;
        }
        return -1;
    }
}
