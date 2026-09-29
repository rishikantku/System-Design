// Q7 — the C# equivalent of ScheduledExecutorService.schedule(Runnable, long, TimeUnit).
public sealed class DelayScheduler : IDisposable {

    // internal, not private: the public Handle below takes one in its constructor, and C#
    // rejects a less-accessible parameter type (CS0051).
    internal sealed class ScheduledTask {
        public long   DueAt;                 // absolute milliseconds
        public long   Seq;                   // tie-break, so equal deadlines run in submission order
        public Action Work;
        public volatile bool Cancelled;
    }

    public sealed class Handle {
        private readonly ScheduledTask _task;
        internal Handle(ScheduledTask task) { _task = task; }

        // Returns false if it had already been cancelled. A task already running cannot be stopped.
        public bool Cancel() {
            if (_task.Cancelled) return false;
            _task.Cancelled = true;
            return true;
        }
    }

    private readonly object _gate = new();
    private readonly PriorityQueue<ScheduledTask, (long DueAt, long Seq)> _queue = new();
    private readonly Func<long> _clock;
    private readonly Thread _worker;
    private bool _shutdown;
    private bool _drain = true;
    private long _seq;

    public DelayScheduler(Func<long> clock = null) {
        _clock  = clock ?? (() => Environment.TickCount64);
        _worker = new Thread(Loop) { IsBackground = true, Name = "delay-scheduler" };
        _worker.Start();
    }

    public Handle Schedule(Action work, TimeSpan delay) {
        if (work == null) throw new ArgumentNullException(nameof(work));

        var task = new ScheduledTask {
            Work  = work,
            DueAt = _clock() + (long)Math.Max(0, delay.TotalMilliseconds)
        };

        lock (_gate) {
            if (_shutdown) throw new InvalidOperationException("Scheduler is shut down.");
            task.Seq = ++_seq;
            _queue.Enqueue(task, (task.DueAt, task.Seq));

            // The worker may be sleeping until a LATER deadline. Wake it so it re-reads the head.
            Monitor.Pulse(_gate);
        }
        return new Handle(task);
    }

    private void Loop() {
        while (true) {
            ScheduledTask ready = null;

            lock (_gate) {
                while (true) {
                    if (_shutdown && (!_drain || _queue.Count == 0)) return;

                    if (_queue.Count == 0) {
                        Monitor.Wait(_gate);          // nothing to do: wait to be poked
                        continue;
                    }

                    ScheduledTask head = _queue.Peek();

                    if (head.Cancelled) {             // lazy removal: drop it when it surfaces
                        _queue.Dequeue();
                        continue;
                    }

                    long waitMs = head.DueAt - _clock();
                    if (waitMs <= 0) { ready = _queue.Dequeue(); break; }

                    // Timed wait. Re-check the condition on every wake: this loop is what makes
                    // a spurious wake, an earlier Pulse from Schedule, and a real timeout
                    // all behave identically.
                    Monitor.Wait(_gate, (int)Math.Min(waitMs, int.MaxValue));
                }
            }

            // Run OUTSIDE the lock. Holding it here would block every Schedule call for the
            // duration of the task, and a task that itself schedules work would deadlock.
            if (!ready.Cancelled) {
                try { ready.Work(); }
                catch { /* one bad task must not take the worker thread with it */ }
            }
        }
    }

    // drainPending: true  -> run what is already scheduled, accept nothing new  (shutdown)
    //               false -> discard everything queued                          (shutdownNow)
    public void Shutdown(bool drainPending = true) {
        lock (_gate) {
            _shutdown = true;
            _drain    = drainPending;
            if (!drainPending) _queue.Clear();
            Monitor.PulseAll(_gate);
        }
    }

    public bool AwaitTermination(TimeSpan timeout) => _worker.Join(timeout);

    public void Dispose() {
        Shutdown(drainPending: false);
        _worker.Join(TimeSpan.FromSeconds(2));
    }
}
