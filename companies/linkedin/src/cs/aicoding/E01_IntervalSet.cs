// E01 — an interval manager. Reported Feb 2026 (Hello Interview): not "merge this list", but a
// class with addInterval()/insertInterval()-style methods where you choose the bookkeeping.
//
// Intervals are HALF-OPEN [start, end). That makes [1,3) and [3,5) touch and merge into [1,5),
// and makes length = end - start with no +1. Say which convention you chose before coding;
// closed-versus-half-open is the most common silent disagreement with an assistant here.

public sealed class IntervalSet {
    // Disjoint, non-touching intervals keyed by start. SortedSet gives O(log n) floor lookup
    // through GetViewBetween(...).Max — the thing a List + Sort-on-every-insert cannot do.
    private readonly SortedSet<(int Start, int End)> _set =
        new(Comparer<(int Start, int End)>.Create((a, b) => a.Start.CompareTo(b.Start)));

    public long CoveredLength { get; private set; }     // maintained, so reading it is O(1)
    public int Count => _set.Count;

    // O(log n + k), k = intervals absorbed. Amortised O(log n): each interval is absorbed once.
    public void Add(int start, int end) {
        if (start >= end) throw new ArgumentException("empty or inverted interval");
        int s = start, e = end;

        if (Floor(start) is { } f && f.End >= start) {   // the one before may reach into us
            s = Math.Min(s, f.Start);
            e = Math.Max(e, f.End);
            Drop(f);
        }
        // every interval that starts inside [start, end] touches or overlaps
        foreach (var iv in _set.GetViewBetween((start, 0), (end, 0)).ToList()) {
            e = Math.Max(e, iv.End);
            Drop(iv);
        }
        _set.Add((s, e));
        CoveredLength += e - s;
    }

    // Removing can split one interval into two.
    public void Remove(int start, int end) {
        if (start >= end) return;
        // the interval starting before us (if it reaches in), plus every one starting inside
        var hit = _set.GetViewBetween((start, 0), (end - 1, 0)).ToList();
        if (Floor(start) is { } f && f.Start < start && f.End > start) hit.Add(f);
        foreach (var iv in hit) {
            Drop(iv);
            if (iv.Start < start) Put(iv.Start, start);
            if (iv.End > end) Put(end, iv.End);
        }
    }

    public bool Contains(int point) => Floor(point) is { } f && point < f.End;

    public IReadOnlyList<(int Start, int End)> Intervals => _set.ToList();

    private (int Start, int End)? Floor(int x) {
        if (_set.Count == 0 || _set.Min.Start > x) return null;
        return _set.GetViewBetween(_set.Min, (x, 0)).Max;
    }

    private void Drop((int Start, int End) iv) { _set.Remove(iv); CoveredLength -= iv.End - iv.Start; }
    private void Put(int s, int e) { _set.Add((s, e)); CoveredLength += e - s; }
}
