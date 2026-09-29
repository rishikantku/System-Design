// Q9 — AddInterval in O(log n), GetCoveredSize in O(1).
// Intervals are half-open [start, end), so length is end - start and touching intervals coalesce.
public class CoveredIntervals {

    // Disjoint, merged, sorted by Start. Because they are disjoint, sorting by Start also
    // sorts by End, which is what makes the tuple comparer safe to use directly.
    private readonly SortedSet<(int Start, int End)> _set = new();
    private long _covered;

    // The whole trick: the total is maintained as a field on every mutation, never recomputed.
    public long GetCoveredSize() => _covered;

    public int IntervalCount => _set.Count;

    public void AddInterval(int start, int end) {
        if (end <= start) return;                       // empty or reversed: nothing to cover

        int lo = start, hi = end;

        // 1. The interval immediately at or before `start`. If it reaches start, it merges.
        var before = _set.GetViewBetween((int.MinValue, int.MinValue), (start, int.MaxValue));
        if (before.Count > 0) {
            var prev = before.Max;
            if (prev.End >= start) {
                lo = prev.Start;
                hi = Math.Max(hi, prev.End);
                Drop(prev);
            }
        }

        // 2. Every interval starting inside [lo, hi] is swallowed. Each one is removed exactly
        //    once over the life of the structure, which is what makes the amortised cost O(log n)
        //    even though a single call can remove many.
        while (true) {
            var inside = _set.GetViewBetween((lo, int.MinValue), (hi, int.MaxValue));
            if (inside.Count == 0) break;

            var next = inside.Min;
            hi = Math.Max(hi, next.End);
            Drop(next);
        }

        _set.Add((lo, hi));
        _covered += hi - lo;
    }

    private void Drop((int Start, int End) iv) {
        _set.Remove(iv);
        _covered -= iv.End - iv.Start;
    }

    public List<(int Start, int End)> Snapshot() => _set.ToList();
}
