// Tutorial part 1 — the C# collections the AI-round questions are built from, and the one
// property of each that decides whether a design is O(1), O(log n) or quietly O(n).
// Every snippet here is shown on screen in the video; Tests.cs exercises each one.

// ---- DS1. Composite keys: a record struct gets value equality and hashing for free.
// The logger's "identical log" is four fields. A tuple works too; a class would NOT
// (reference equality: two equal-looking keys would be two different dictionary entries).
public enum Level { Debug, Info, Warn, Error }
public readonly record struct LogKey(Level Level, string Func, int Line, string Msg);

// ---- DS2. PriorityQueue<TElement, TPriority>: a min-heap. Enqueue/Dequeue O(log n), Peek O(1).
// It has NO update and NO remove-by-item. So cancellation is lazy: mark the item, skip it when
// it reaches the head. And equal priorities come out in no particular order — add a sequence
// number to the priority when order matters.
public sealed class Job { public long Due; public string Name; public bool Cancelled; }

public sealed class JobQueue {
    private readonly PriorityQueue<Job, (long Due, long Seq)> _pq = new();
    private long _seq;

    public Job Add(string name, long due) {
        var j = new Job { Name = name, Due = due };
        _pq.Enqueue(j, (due, ++_seq));              // tie-break: submission order
        return j;
    }

    public Job PopDue(long now) {
        while (_pq.TryPeek(out var head, out var pri)) {
            if (head.Cancelled) { _pq.Dequeue(); continue; }   // lazy removal
            if (pri.Due > now) return null;
            return _pq.Dequeue();
        }
        return null;
    }
}

// ---- DS3. LinkedList<T>: O(1) remove ONLY if you hold the node. Remove(value) is a linear
// search. Every LRU stores LinkedListNode<T> handles in its dictionary for exactly this reason.
public static class ListOps {
    public static void MoveToFront<T>(LinkedList<T> list, LinkedListNode<T> node) {
        list.Remove(node);            // O(1): unlinks the node it was given
        list.AddFirst(node);          // O(1): re-links the same node object
    }
}

// ---- DS4. SortedSet / SortedDictionary: red-black trees, O(log n) add/remove/lookup.
// Floor and ceiling come from GetViewBetween(lo, hi).Max / .Min — O(log n).
// Trap: a view's .Count is O(size of the view), it walks the range. The question bank's Q9
// shipped with that bug (an "O(log n)" insert that was O(n)), fixed by checking Min/Max instead.
public static class SortedOps {
    // Largest element <= x, or null. O(log n).
    public static int? Floor(SortedSet<int> s, int x) {
        if (s.Count == 0 || s.Min > x) return null;
        return s.GetViewBetween(s.Min, x).Max;
    }
    // Smallest element >= x, or null. O(log n).
    public static int? Ceiling(SortedSet<int> s, int x) {
        if (s.Count == 0 || s.Max < x) return null;
        return s.GetViewBetween(x, s.Max).Min;
    }
}

// ---- DS5. A fixed array as a ring: index = t % N. Memory is N forever, whatever the event rate.
// The slot remembers which t it holds, so a stale slot is detected and reset, not double-counted.
public sealed class Ring {
    private readonly long[] _stamp; private readonly long[] _value;
    public Ring(int n) { _stamp = new long[n]; _value = new long[n]; Array.Fill(_stamp, -1); }
    public void Add(long t, long v) {
        int i = (int)(t % _stamp.Length);
        if (_stamp[i] != t) { _stamp[i] = t; _value[i] = 0; }   // slot held an older t: reset
        _value[i] += v;
    }
    public long Get(long t) { int i = (int)(t % _stamp.Length); return _stamp[i] == t ? _value[i] : 0; }
}
