// L01 — a logging library. Reported for LinkedIn's AI-enabled round by Hello Interview's
// community page: 5 reports, visible ones Staff (early Aug 2026), Senior (late Aug and mid Sep 2026).
// The reported phases: (1) severity filtering, (2) unit tests, (3) throttle identical logs within
// a time window, (4) aggregate — when the window expires and the next identical log arrives, print
// a summary of what was suppressed, stamped with the first occurrence in that window.
//
// Logger is phases 1–4. AsyncLogger is the production version the follow-ups push toward:
// callers never block on I/O, memory is bounded, a failing sink cannot take the app down.

using System.Threading.Channels;

public enum Severity { Debug = 0, Info = 1, Warn = 2, Error = 3 }

public interface ILogSink { void Write(string line); }

public sealed class ListSink : ILogSink {                  // for tests: records what was written
    private readonly List<string> _lines = new();
    public void Write(string line) { lock (_lines) _lines.Add(line); }
    public IReadOnlyList<string> Lines { get { lock (_lines) return _lines.ToList(); } }
}

// Phases 1–4. Thread-safe: the throttle table is the only shared mutable state.
public sealed class Logger {
    // "Identical" = same severity, function, line and message — the reported definition.
    private readonly record struct Key(Severity Sev, string Func, int Line, string Msg);
    private sealed class Window { public long Start; public long FirstTs; public int Suppressed; }

    private readonly Severity _min;
    private readonly IClock _clock;
    private readonly long _windowMs;
    private readonly ILogSink[] _sinks;
    private readonly Dictionary<Key, Window> _windows = new();
    private readonly object _gate = new();

    public Logger(Severity min, IClock clock, long windowMs, params ILogSink[] sinks) {
        if (windowMs < 0) throw new ArgumentOutOfRangeException(nameof(windowMs));
        if (sinks == null || sinks.Length == 0) throw new ArgumentException("at least one sink");
        _min = min; _clock = clock; _windowMs = windowMs; _sinks = sinks;
    }

    public void Log(Severity sev, string func, int line, string msg) {
        if (sev < _min) return;                            // phase 1: cheapest check first, no lock
        long now = _clock.NowMs;
        var key = new Key(sev, func, line, msg);
        string summary = null;

        lock (_gate) {                                     // phase 3/4: decide under the lock…
            if (_windowMs > 0 && _windows.TryGetValue(key, out var w)) {
                if (now < w.Start + _windowMs) { w.Suppressed++; return; }
                if (w.Suppressed > 0)
                    summary = $"{w.FirstTs} {sev} {func}:{line} {msg} [suppressed {w.Suppressed} identical in {_windowMs}ms]";
                w.Start = now; w.FirstTs = now; w.Suppressed = 0;
            } else if (_windowMs > 0) {
                _windows[key] = new Window { Start = now, FirstTs = now };
            }
        }
        // …write outside it. A slow sink must not serialise every caller (review exercise R11).
        if (summary != null) Emit(summary);
        Emit($"{now} {sev} {func}:{line} {msg}");
    }

    // Memory bound for the throttle table: drop windows that expired with nothing suppressed.
    // Unbounded distinct messages (a message with a request id in it) would otherwise grow forever.
    public int PurgeExpired() {
        long now = _clock.NowMs;
        lock (_gate) {
            var dead = _windows.Where(kv => now >= kv.Value.Start + _windowMs && kv.Value.Suppressed == 0)
                               .Select(kv => kv.Key).ToList();
            foreach (var k in dead) _windows.Remove(k);
            return dead.Count;
        }
    }

    private void Emit(string text) {
        foreach (var s in _sinks) {
            try { s.Write(text); }
            catch (Exception) { /* a broken sink must not break the caller; AsyncLogger counts these */ }
        }
    }
}

// The production shape: Log() enqueues into a bounded channel and returns; one background
// task drains it to the sinks. When the channel is full the NEWEST event is dropped and counted —
// logging must never block the request path, and a drop counter is the honest signal.
//
// FullMode is Wait, not DropWrite, and that is deliberate. My first version used DropWrite and the
// 10,000-thread test caught it: under DropWrite, TryWrite returns TRUE even when it drops the item,
// so "accepted 10,000, dropped 0" was reported while 1,026 were written. Under Wait, a non-blocking
// TryWrite returns false when full — which is the signal the drop counter needs.
public sealed class AsyncLogger : IAsyncDisposable {
    private readonly Channel<string> _ch;
    private readonly ILogSink[] _sinks;
    private readonly Severity _min;
    private readonly Task _pump;
    private long _accepted, _dropped, _written, _sinkFailures;

    public AsyncLogger(Severity min, int capacity, params ILogSink[] sinks) {
        _min = min; _sinks = sinks;
        _ch = Channel.CreateBounded<string>(new BoundedChannelOptions(capacity) {
            FullMode = BoundedChannelFullMode.Wait,          // TryWrite (never WriteAsync) returns false when full
            SingleReader = true, SingleWriter = false });
        _pump = Task.Run(PumpAsync);
    }

    public bool Log(Severity sev, string msg) {
        if (sev < _min) return false;
        if (_ch.Writer.TryWrite($"{sev} {msg}")) { Interlocked.Increment(ref _accepted); return true; }
        Interlocked.Increment(ref _dropped);
        return false;
    }

    private async Task PumpAsync() {
        await foreach (var line in _ch.Reader.ReadAllAsync()) {
            foreach (var s in _sinks) {
                try { s.Write(line); }
                catch (Exception) { Interlocked.Increment(ref _sinkFailures); }   // isolate, count, carry on
            }
            Interlocked.Increment(ref _written);
        }
    }

    public (long Accepted, long Dropped, long Written, long SinkFailures) Metrics =>
        (Interlocked.Read(ref _accepted), Interlocked.Read(ref _dropped), Interlocked.Read(ref _written), Interlocked.Read(ref _sinkFailures));

    // Shutdown: stop accepting, drain what was accepted, with a bound on how long we wait.
    public async ValueTask DisposeAsync() {
        _ch.Writer.TryComplete();
        await Task.WhenAny(_pump, Task.Delay(TimeSpan.FromSeconds(5)));
    }
}
