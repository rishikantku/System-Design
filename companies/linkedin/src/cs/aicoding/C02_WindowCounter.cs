// C02 — a sliding-window event counter ("hits in the last 5 minutes"). PATTERN PRACTICE:
// not a reported LinkedIn AI-round question. It is here because "metrics and counters" is the
// natural production follow-up to the reported cache and data-processing problems, and it
// is the smallest problem that forces a time-bucketing decision and a thread-safety decision.

public sealed class WindowCounter {
    private readonly int _windowSecs;
    private readonly long[] _stamp;      // which second each slot currently holds
    private readonly int[] _count;       // events in that second
    private readonly object _gate = new();

    // Memory is O(window), not O(events): one slot per second, reused as time moves on.
    // An exact-timestamp queue would hold every event for five minutes — at 10k events/s,
    // three million entries for a number nobody needs to millisecond precision.
    public WindowCounter(int windowSecs = 300) {
        if (windowSecs <= 0) throw new ArgumentOutOfRangeException(nameof(windowSecs));
        _windowSecs = windowSecs;
        _stamp = new long[windowSecs];
        _count = new int[windowSecs];
        Array.Fill(_stamp, -1);
    }

    public void Record(long nowSecs, int n = 1) {
        int slot = (int)(nowSecs % _windowSecs);
        lock (_gate) {
            if (_stamp[slot] != nowSecs) { _stamp[slot] = nowSecs; _count[slot] = 0; }   // slot was a stale second
            _count[slot] += n;
        }
    }

    // O(window) per read. If reads dominate, keep a running total and subtract slots as they
    // are recycled — that makes reads O(1) and writes do the bookkeeping. State which you chose.
    public long Count(long nowSecs) {
        long total = 0;
        lock (_gate) {
            for (int i = 0; i < _windowSecs; i++)
                if (_stamp[i] > nowSecs - _windowSecs && _stamp[i] <= nowSecs) total += _count[i];
        }
        return total;
    }
}
