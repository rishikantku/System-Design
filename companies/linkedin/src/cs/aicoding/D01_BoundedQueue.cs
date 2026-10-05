// D01 — producer/consumer: a bounded blocking queue with cancellation and shutdown.
// Concurrency is the most commonly reported pivot in the AI round; this is the primitive
// most of those follow-ups reduce to.
//
// In production C# the answer is System.Threading.Channels.Channel.CreateBounded<T>. Say so
// first. Then build it, because the interviewer wants to see you own the synchronization.

public sealed class BoundedBlockingQueue<T> {
    private readonly Queue<T> _items = new();
    private readonly int _capacity;
    private readonly object _gate = new();
    private bool _completed;

    public BoundedBlockingQueue(int capacity) {
        if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        _capacity = capacity;
    }

    // Blocks while full. Throws OperationCanceledException if cancelled, InvalidOperationException
    // if the queue was completed — a producer must not silently lose an item after shutdown.
    public void Enqueue(T item, CancellationToken ct = default) {
        using var reg = ct.Register(Wake);              // Monitor.Wait has no token: wake waiters on cancel
        lock (_gate) {
            while (_items.Count == _capacity && !_completed) {   // WHILE, not if: re-check after every wake
                ct.ThrowIfCancellationRequested();
                Monitor.Wait(_gate);
            }
            ct.ThrowIfCancellationRequested();
            if (_completed) throw new InvalidOperationException("queue is completed");
            _items.Enqueue(item);
            Monitor.PulseAll(_gate);                    // PulseAll: producers and consumers share one monitor
        }
    }

    // Blocks while empty. Returns false once the queue is completed AND drained — that is the
    // shutdown signal a consumer loop needs, and the reason Complete() exists at all.
    public bool TryDequeue(out T item, CancellationToken ct = default) {
        using var reg = ct.Register(Wake);
        lock (_gate) {
            while (_items.Count == 0 && !_completed) {
                ct.ThrowIfCancellationRequested();
                Monitor.Wait(_gate);
            }
            ct.ThrowIfCancellationRequested();
            if (_items.Count == 0) { item = default; return false; }   // completed and drained
            item = _items.Dequeue();
            Monitor.PulseAll(_gate);
            return true;
        }
    }

    // Graceful shutdown: no new items, consumers drain what is left, then see false.
    public void Complete() { lock (_gate) { _completed = true; Monitor.PulseAll(_gate); } }

    public int Count { get { lock (_gate) return _items.Count; } }

    private void Wake() { lock (_gate) Monitor.PulseAll(_gate); }
}
