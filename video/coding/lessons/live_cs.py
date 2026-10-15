# -*- coding: utf-8 -*-
"""The C# behind lesson 11.2 (the AI round, step by step).

Every listing shown on the pad is a slice of a RUN below, and every console on screen is the real
output of compiling and running that RUN (live_run.py writes it to live_out.json). The assistant
replies are written to show the mistakes assistants typically make — they are not transcripts of a
particular model — but the code is real code and the failures are real failures.

A RUN = the files in the pad at that moment: CODE (the class under work), TESTS (body of Tests.Run),
TYPES (helper types the tests use). MODELS and the harness T are always present, as in CoderPad.
"""

MODELS = r'''
public interface IClock { long NowMs { get; } }
public sealed class ManualClock : IClock { public long NowMs { get; set; } }

public enum Severity { Debug, Info, Warn, Error }

public interface ILogSink { void Write(string line); }

public sealed class ListSink : ILogSink {
    private readonly List<string> _lines = new();
    public void Write(string line) { lock (_lines) _lines.Add(line); }
    public List<string> Lines { get { lock (_lines) return new List<string>(_lines); } }
}
'''

HARNESS = r'''
static class T {
    static int pass = 0, fail = 0;
    public static void Eq<TV>(string what, TV got, TV want) {
        if (EqualityComparer<TV>.Default.Equals(got, want)) pass++;
        else { fail++; Console.WriteLine($"  FAIL {what}: got {got}, want {want}"); }
    }
    public static void True(string what, bool cond) => Eq(what, cond, true);
    public static void Section(string s) => Console.WriteLine($"--- {s}");
    public static void Note(string s) => Console.WriteLine($"    note: {s}");
    public static int Report() { Console.WriteLine($"\n{pass} passed, {fail} failed"); return fail == 0 ? 0 : 1; }
}

class Program {
    static int Main() {
        try { Tests.Run(); }
        catch (Exception e) { Console.WriteLine($"Unhandled exception. {e.GetType().FullName}: {e.Message}"); return 1; }
        return T.Report();
    }
}
'''

# =============================================================================== LOGGING LIBRARY
# ---- phase 1: severity filter -------------------------------------------------------------
LOGGER1 = r'''
public sealed class Logger {
    private readonly Severity _min;
    private readonly IClock _clock;
    private readonly ILogSink[] _sinks;

    public Logger(Severity min, IClock clock, params ILogSink[] sinks) {
        _min = min; _clock = clock; _sinks = sinks;
    }
%s
}
'''

P1_SKEL = r'''
    // Writes "{now} {sev} {func}:{line} {msg}" to every sink, if sev >= min.
    // A sink that throws must not stop the other sinks.
    public void Log(Severity sev, string func, int line, string msg) {
        throw new NotImplementedException();
    }
'''

P1_AI = r'''
    public void Log(Severity sev, string func, int line, string msg) {
        if (sev <= _min) return;                          // filter
        Emit($"{_clock.NowMs} {sev} {func}:{line} {msg}");
    }

    private void Emit(string text) {
        foreach (var sink in _sinks) {
            try { sink.Write(text); }
            catch (Exception) { }                         // one broken sink can't stop the rest
        }
    }
'''
P1_FIXED = P1_AI.replace('if (sev <= _min) return;                          // filter',
                         'if (sev < _min) return;                           // filter: below the minimum')

P1_BAD = r'''
public enum LogLevel { Trace, Debug, Info, Warning, Error, Fatal }

public static class Logger {
    public static LogLevel MinLevel { get; set; } = LogLevel.Info;

    public static void Log(LogLevel level, string message) {
        if (level < MinLevel) return;
        var ts = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff");
        Console.WriteLine($"[{ts}] [{level.ToString().ToUpper()}] {message}");
    }

    public static void Info(string m) => Log(LogLevel.Info, m);
    public static void Warn(string m) => Log(LogLevel.Warning, m);
    public static void Error(string m) => Log(LogLevel.Error, m);
}
'''

HAND1 = r'''
T.Section("my cases: severity");
{
    var clk = new ManualClock(); var sink = new ListSink();
    var log = new Logger(Severity.Info, clk, sink);
    log.Log(Severity.Debug, "f", 1, "noise");
    T.Eq("below the minimum is dropped", sink.Lines.Count, 0);
    clk.NowMs = 42;
    log.Log(Severity.Warn, "f", 7, "disk");
    T.Eq("format", sink.Lines[0], "42 Warn f:7 disk");
    log.Log(Severity.Info, "f", 8, "at the minimum");
    T.Eq("the minimum itself is written", sink.Lines.Count, 2);
}
'''

# ---- phases 2-3: throttle identical logs, then summarise ----------------------------------
LOGGER2 = r'''
// "Identical" = same severity, function, line and message.
public readonly record struct LogKey(Severity Sev, string Func, int Line, string Msg);

public sealed class Logger {
    private sealed class Window { public long Start; public int Suppressed; }

    private readonly Severity _min;
    private readonly IClock _clock;
    private readonly long _windowMs;                       // 0 = no throttling
    private readonly ILogSink[] _sinks;
    private readonly Dictionary<LogKey, Window> _windows = new();
    private readonly object _gate = new();                 // guards _windows, nothing else

    public Logger(Severity min, IClock clock, params ILogSink[] sinks) : this(min, clock, 0, sinks) { }

    public Logger(Severity min, IClock clock, long windowMs, params ILogSink[] sinks) {
        _min = min; _clock = clock; _windowMs = windowMs; _sinks = sinks;
    }
%s
    private void Emit(string text) {
        foreach (var sink in _sinks) {
            try { sink.Write(text); }
            catch (Exception) { }                         // one broken sink can't stop the rest
        }
    }
}
'''

P2_AI = r'''
    public void Log(Severity sev, string func, int line, string msg) {
        if (sev < _min) return;
        long now = _clock.NowMs;
        string summary = null;
        if (_windowMs > 0) {
            var key = new LogKey(sev, func, line, msg);
            lock (_gate) {                                 // decide under the lock...
                if (_windows.TryGetValue(key, out var w)) {
                    if (now < w.Start + _windowMs) { w.Suppressed++; return; }
                    if (w.Suppressed > 0)
                        summary = $"{now} {sev} {func}:{line} {msg} [suppressed {w.Suppressed}]";
                    w.Start = now; w.Suppressed = 0;
                } else {
                    _windows[key] = new Window { Start = now };
                }
            }
        }
        if (summary != null) Emit(summary);                // ...write outside it
        Emit($"{now} {sev} {func}:{line} {msg}");
    }
'''
P2_FIXED = P2_AI.replace('summary = $"{now} {sev}', 'summary = $"{w.Start} {sev}')

P2_BAD = r'''
    private readonly Dictionary<string, DateTime> _lastSeen = new();

    public void Log(Severity sev, string func, int line, string msg) {
        if (sev < _min) return;
        lock (_lastSeen) {
            if (_lastSeen.TryGetValue(msg, out var last) &&
                DateTime.UtcNow - last < TimeSpan.FromSeconds(1))
                return;                                    // duplicate: drop it
            _lastSeen[msg] = DateTime.UtcNow;
            Emit($"{_clock.NowMs} {sev} {func}:{line} {msg}");
        }
    }
'''

HAND2 = r'''
T.Section("my cases: throttle");
{
    var clk = new ManualClock(); var sink = new ListSink();
    var log = new Logger(Severity.Info, clk, 1000, sink);
    log.Log(Severity.Warn, "f", 1, "disk");                     // t=0: printed, window opens
    clk.NowMs = 10; log.Log(Severity.Warn, "f", 1, "disk");     // suppressed
    clk.NowMs = 20; log.Log(Severity.Warn, "f", 1, "disk");     // suppressed
    T.Eq("inside the window only the first prints", sink.Lines.Count, 1);
    clk.NowMs = 1500; log.Log(Severity.Warn, "f", 1, "disk");
    T.Eq("summary carries the FIRST time", sink.Lines[1], "0 Warn f:1 disk [suppressed 2]");
    T.Eq("then the new line", sink.Lines[2], "1500 Warn f:1 disk");
}
'''

# ---- tests from the assistant ---------------------------------------------------------------
AITESTS_BAD = r'''
using Xunit;

public class LoggerTests {
    [Fact]
    public void Suppresses_Duplicates_Within_Window() {
        var sink = new ListSink();
        var log = new Logger(Severity.Info, new SystemClock(), 1000, sink);
        log.Log(Severity.Warn, "f", 1, "disk");
        log.Log(Severity.Warn, "f", 1, "disk");
        Assert.Single(sink.Lines);
    }

    [Fact]
    public void Prints_Summary_After_Window() {
        var sink = new ListSink();
        var log = new Logger(Severity.Info, new SystemClock(), 1000, sink);
        log.Log(Severity.Warn, "f", 1, "disk");
        log.Log(Severity.Warn, "f", 1, "disk");
        Thread.Sleep(1100);
        log.Log(Severity.Warn, "f", 1, "disk");
        Assert.Equal(3, sink.Lines.Count);
    }
}
'''

AITESTS = r'''
T.Section("generated tests");
{
    var clk = new ManualClock(); var sink = new ListSink();
    var log = new Logger(Severity.Info, clk, 1000, sink);
    // At exactly start + window a NEW window begins, so the second log prints.
    log.Log(Severity.Warn, "g", 1, "x"); clk.NowMs = 1000; log.Log(Severity.Warn, "g", 1, "x");
    T.Eq("exactly at the window end", sink.Lines.Count, 2);
    // A different line number is a different key, so it is not throttled.
    log.Log(Severity.Warn, "g", 2, "x");
    T.Eq("different line, different key", sink.Lines.Count, 3);
}
{
    var sink = new ListSink();
    var log = new Logger(Severity.Info, new ManualClock(), 1000, sink);
    // Three identical logs inside one window are all suppressed, so nothing is written.
    for (int i = 0; i < 3; i++) log.Log(Severity.Error, "h", 9, "y");
    T.Eq("3 identical inside one window", sink.Lines.Count, 0);
}
{
    var after = new ListSink();
    // A sink that throws must not stop the sinks after it.
    new Logger(Severity.Info, new ManualClock(), 1000, new Thrower(), after).Log(Severity.Warn, "k", 1, "z");
    T.Eq("a throwing sink does not stop the next", after.Lines.Count, 1);
}
'''
AITESTS_FIXED = AITESTS.replace(
    '    // Three identical logs inside one window are all suppressed, so nothing is written.\n',
    '    // The first log opens the window and prints; the next two are suppressed.\n').replace(
    'T.Eq("3 identical inside one window", sink.Lines.Count, 0);',
    'T.Eq("3 identical inside one window", sink.Lines.Count, 1);')
THROWER = 'class Thrower : ILogSink { public void Write(string line) => throw new IOException("disk full"); }'

# ---- concurrency ----------------------------------------------------------------------------
P4_BAD = r'''
    public void Log(Severity sev, string func, int line, string msg) {
        lock (_gate) {                                     // one lock: lines never interleave
            if (sev < _min) return;
            long now = _clock.NowMs;
            var key = new LogKey(sev, func, line, msg);
            if (_windowMs > 0 && _windows.TryGetValue(key, out var w)) {
                if (now < w.Start + _windowMs) { w.Suppressed++; return; }
                if (w.Suppressed > 0)
                    Emit($"{w.Start} {sev} {func}:{line} {msg} [suppressed {w.Suppressed}]");
                w.Start = now; w.Suppressed = 0;
            } else if (_windowMs > 0) {
                _windows[key] = new Window { Start = now };
            }
            Emit($"{now} {sev} {func}:{line} {msg}");
        }
    }
'''

STRESS_LOG = r'''
T.Section("stress: 8 threads, one identical message");
{
    var clk = new ManualClock(); var sink = new ListSink();
    var log = new Logger(Severity.Info, clk, 1000, sink);
    const int threads = 8, each = 10_000;
    using var start = new Barrier(threads);
    var workers = new List<Thread>();
    for (int t = 0; t < threads; t++) {
        var th = new Thread(() => {
            start.SignalAndWait();                         // all threads begin together
            for (int i = 0; i < each; i++) log.Log(Severity.Warn, "f", 1, "same");
        });
        workers.Add(th); th.Start();
    }
    foreach (var th in workers) th.Join();
    clk.NowMs = 2000; log.Log(Severity.Warn, "f", 1, "same");
    T.Eq("one line during the burst, then summary + new", sink.Lines.Count, 3);
    T.Eq("no lost counts", sink.Lines[1], "0 Warn f:1 same [suppressed 79999]");
}
'''

TIMING = r'''
T.Section("a slow sink: how long do callers wait?");
{
    var log = new Logger(Severity.Info, new ManualClock(), 1000, new SlowSink(5));   // 5 ms per write
    var sw = System.Diagnostics.Stopwatch.StartNew();
    var workers = new List<Thread>();
    for (int t = 0; t < 8; t++) {
        int id = t;
        var th = new Thread(() => { for (int i = 0; i < 25; i++) log.Log(Severity.Info, "t" + id, i, "work"); });
        workers.Add(th); th.Start();
    }
    foreach (var th in workers) th.Join();
    T.Note($"8 threads x 25 distinct logs, 5 ms sink: {sw.ElapsedMilliseconds} ms");
}
'''
SLOWSINK = 'class SlowSink : ILogSink { private readonly int _ms; public SlowSink(int ms) { _ms = ms; } public void Write(string line) => Thread.Sleep(_ms); }'

# ---- production: never block the caller -----------------------------------------------------
ASYNC_BAD = r'''
public sealed class AsyncLogger {
    private readonly Logger _inner;
    public AsyncLogger(Logger inner) { _inner = inner; }

    // Never blocks the caller: the write happens on the thread pool.
    public void Log(Severity sev, string func, int line, string msg) {
        Task.Run(() => _inner.Log(sev, func, line, msg));
    }
}
'''

ASYNC_BAD_TEST = r'''
T.Section("fire-and-forget");
{
    var sink = new ListSink();
    var alog = new AsyncLogger(new Logger(Severity.Info, new ManualClock(), sink));
    for (int i = 0; i < 1000; i++) alog.Log(Severity.Info, "f", i, "event " + i);
    Thread.Sleep(500);                                     // no way to wait for it properly
    var lines = sink.Lines;
    T.Eq("all 1000 written", lines.Count, 1000);
    bool inOrder = true;
    for (int i = 0; i < lines.Count; i++) if (!lines[i].EndsWith("event " + i)) inOrder = false;
    T.Eq("written in the order they were logged", inOrder, true);
}
'''

ASYNC_AI = r'''
using System.Threading.Channels;

public sealed class AsyncLogger : IAsyncDisposable {
    private readonly Channel<string> _ch;
    private readonly ILogSink[] _sinks;
    private readonly Task _pump;
    private long _accepted, _dropped, _written;

    public AsyncLogger(int capacity, params ILogSink[] sinks) {
        _sinks = sinks;
        _ch = Channel.CreateBounded<string>(new BoundedChannelOptions(capacity) {
            FullMode = BoundedChannelFullMode.DropWrite,   // full: drop, never block the caller
            SingleReader = true });
        _pump = Task.Run(PumpAsync);
    }

    public void Log(string line) {
        if (_ch.Writer.TryWrite(line)) Interlocked.Increment(ref _accepted);
        else Interlocked.Increment(ref _dropped);           // channel full: dropped
    }

    private async Task PumpAsync() {
        await foreach (var line in _ch.Reader.ReadAllAsync()) {
            foreach (var s in _sinks) { try { s.Write(line); } catch (Exception) { } }
            Interlocked.Increment(ref _written);
        }
    }

    public (long Accepted, long Dropped, long Written) Metrics =>
        (Interlocked.Read(ref _accepted), Interlocked.Read(ref _dropped), Interlocked.Read(ref _written));

    public async ValueTask DisposeAsync() { _ch.Writer.TryComplete(); await _pump; }
}
'''
ASYNC_FIXED = ASYNC_AI.replace(
    'FullMode = BoundedChannelFullMode.DropWrite,   // full: drop, never block the caller',
    'FullMode = BoundedChannelFullMode.Wait,        // TryWrite: false when full')

ASYNC_TEST = r'''
T.Section("10,000 calls, capacity 1,024, slow sink");
{
    var slow = new SpinSink();                              // about 20 µs per line
    var alog = new AsyncLogger(1024, slow);
    Parallel.For(0, 10_000, i => alog.Log("m" + i));
    alog.DisposeAsync().AsTask().Wait();                    // drain, then read the counters
    var m = alog.Metrics;
    T.Note($"accepted {m.Accepted}, dropped {m.Dropped}, written {m.Written}");
    T.Eq("each call accepted or dropped", m.Accepted + m.Dropped, 10_000L);
    T.Eq("everything accepted was written", m.Written, m.Accepted);
    T.Eq("the sink saw every written line", (long)slow.N, m.Written);
}
'''
SPINSINK = 'class SpinSink : ILogSink { public int N; public void Write(string line) { Thread.SpinWait(4000); Interlocked.Increment(ref N); } }'

# =============================================================================== LRU → TTL → THREADS
LRU_BAD = r'''
public class LRUCache {
    private readonly int _capacity;
    private readonly Dictionary<int, LinkedListNode<(int Key, int Val)>> _map = new();
    private readonly LinkedList<(int Key, int Val)> _list = new();

    public LRUCache(int capacity) { _capacity = capacity; }

    public int Get(int key) {
        if (!_map.TryGetValue(key, out var node)) return -1;
        _list.Remove(node); _list.AddFirst(node);
        return node.Value.Val;
    }

    public void Put(int key, int value) {
        if (_map.TryGetValue(key, out var node)) _list.Remove(node);
        else if (_map.Count == _capacity) {
            _map.Remove(_list.Last.Value.Key);
            _list.RemoveLast();
        }
        _map[key] = _list.AddFirst((key, value));
    }
}
'''

LRU = r'''
// Fixed capacity; evicts the least recently used. A TryGet counts as a use.
public sealed class LruCache<TKey, TValue> {
    private sealed class Entry { public TKey Key; public TValue Value; }

    private readonly int _capacity;
    private readonly Dictionary<TKey, LinkedListNode<Entry>> _map = new();
    private readonly LinkedList<Entry> _order = new();        // First = most recent

    public LruCache(int capacity) {
        if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        _capacity = capacity;
    }

    public int Count => _map.Count;
%s
}
'''
LRU_SKEL = r'''
    public bool TryGet(TKey key, out TValue value) => throw new NotImplementedException();
    public void Put(TKey key, TValue value) => throw new NotImplementedException();
'''
LRU_AI = r'''
    public bool TryGet(TKey key, out TValue value) {
        if (_map.TryGetValue(key, out var node)) {
            value = node.Value.Value;
            return true;
        }
        value = default;
        return false;
    }

    public void Put(TKey key, TValue value) {
        if (_map.TryGetValue(key, out var node)) {
            node.Value.Value = value;
            _order.Remove(node); _order.AddFirst(node);
            return;
        }
        if (_map.Count == _capacity) {
            _map.Remove(_order.Last.Value.Key);
            _order.RemoveLast();
        }
        _map[key] = _order.AddFirst(new Entry { Key = key, Value = value });
    }
'''
LRU_FIXED = LRU_AI.replace(
    '''            value = node.Value.Value;
            return true;''',
    '''            _order.Remove(node); _order.AddFirst(node);       // a read is a use
            value = node.Value.Value;
            return true;''')

HAND_LRU = r'''
T.Section("my cases: LRU");
{
    var c = new LruCache<int, string>(2);
    c.Put(1, "a"); c.Put(2, "b");
    c.TryGet(1, out _);                       // 1 is now the most recent
    c.Put(3, "c");                            // full: the LRU entry (2) must go
    T.True("2 was evicted", !c.TryGet(2, out _));
    T.True("1 survived its read", c.TryGet(1, out var v) && v == "a");
    c.Put(1, "a2");
    T.Eq("an update does not grow the cache", c.Count, 2);
}
'''

TTL = r'''
%s
public sealed class LruTtlCache<TKey, TValue> {
    private sealed class Entry { public TKey Key; public TValue Value; public long ExpiresAt; }

    private readonly int _capacity;
    private readonly IClock _clock;
    private readonly %s<TKey, LinkedListNode<Entry>> _map = new();
    private readonly LinkedList<Entry> _order = new();        // First = most recent
%s
    public LruTtlCache(int capacity, IClock clock) { _capacity = capacity; _clock = clock; }
%s
}
'''

TTL_METHODS = r'''
    public int Count => _map.Count;

    public bool TryGet(TKey key, out TValue value) {
        value = default;
        if (!_map.TryGetValue(key, out var node)) return false;
        if (_clock.NowMs > node.Value.ExpiresAt) {            // expired: drop it on read
            Remove(node);
            return false;
        }
        _order.Remove(node); _order.AddFirst(node);
        value = node.Value.Value;
        return true;
    }

    public void Put(TKey key, TValue value, long ttlMs) {
        long expiresAt = _clock.NowMs + ttlMs;
        if (_map.TryGetValue(key, out var node)) {
            node.Value.Value = value; node.Value.ExpiresAt = expiresAt;
            _order.Remove(node); _order.AddFirst(node);
            return;
        }
        if (_map.Count == _capacity) Remove(_order.Last);
        _map[key] = _order.AddFirst(new Entry { Key = key, Value = value, ExpiresAt = expiresAt });
    }

    private void Remove(LinkedListNode<Entry> node) { _order.Remove(node); _map.Remove(node.Value.Key); }
'''
TTL_FIXED_METHODS = TTL_METHODS.replace('if (_clock.NowMs > node.Value.ExpiresAt) {            // expired: drop it on read',
                                        'if (_clock.NowMs >= node.Value.ExpiresAt) {           // dead AT the expiry time')

# "Make it thread-safe" → the most common wrong answer: a concurrent map, an unprotected list.
TTL_CONC_METHODS = TTL_FIXED_METHODS.replace(
    '    private void Remove(LinkedListNode<Entry> node) { _order.Remove(node); _map.Remove(node.Value.Key); }',
    '    private void Remove(LinkedListNode<Entry> node) { _order.Remove(node); _map.TryRemove(node.Value.Key, out _); }')

TTL_LOCKED_METHODS = r'''
    public int Count { get { lock (_lock) return _map.Count; } }

    public bool TryGet(TKey key, out TValue value) {
        lock (_lock) {                                         // TryGet WRITES: it moves a node
            value = default;
            if (!_map.TryGetValue(key, out var node)) return false;
            if (_clock.NowMs >= node.Value.ExpiresAt) { Remove(node); return false; }
            _order.Remove(node); _order.AddFirst(node);
            value = node.Value.Value;
            return true;
        }
    }

    public void Put(TKey key, TValue value, long ttlMs) {
        lock (_lock) {
            long expiresAt = _clock.NowMs + ttlMs;
            if (_map.TryGetValue(key, out var node)) {
                node.Value.Value = value; node.Value.ExpiresAt = expiresAt;
                _order.Remove(node); _order.AddFirst(node);
                return;
            }
            if (_map.Count == _capacity) Remove(_order.Last);
            _map[key] = _order.AddFirst(new Entry { Key = key, Value = value, ExpiresAt = expiresAt });
        }
    }

    // Callers already hold _lock.
    private void Remove(LinkedListNode<Entry> node) { _order.Remove(node); _map.Remove(node.Value.Key); }
'''

def ttl(methods, conc=False, locked=False):
    return TTL % ('using System.Collections.Concurrent;\n' if conc else '',
                  'ConcurrentDictionary' if conc else 'Dictionary',
                  '    private readonly object _lock = new();\n' if locked else '',
                  methods)

TTL_BAD_TIMER = r'''
    private readonly Timer _sweeper;

    public LruTtlCache(int capacity, TimeSpan ttl) {
        _capacity = capacity; _ttl = ttl;
        _sweeper = new Timer(_ => Sweep(), null, 1000, 1000);   // clean up every second
    }

    private void Sweep() {
        foreach (var kv in _map)
            if (DateTime.UtcNow >= kv.Value.Value.ExpiresAt) Remove(kv.Value);
    }
'''

HAND_TTL = r'''
T.Section("my cases: TTL");
{
    var clk = new ManualClock();
    var c = new LruTtlCache<int, int>(3, clk);
    c.Put(1, 10, ttlMs: 100);
    clk.NowMs = 99;  T.True("alive one tick before", c.TryGet(1, out _));
    clk.NowMs = 100; T.True("dead exactly at the TTL", !c.TryGet(1, out _));
    T.Eq("the dead entry was removed", c.Count, 0);
}
'''

STRESS_LRU = r'''
T.Section("stress: 8 threads on one cache");
{
    var c = new LruTtlCache<int, int>(64, new ManualClock());
    Exception error = null;
    Parallel.For(0, 8, t => {
        try {
            for (int i = 0; i < 20_000; i++) {
                int k = (i * 7 + t) % 200;
                if (i % 3 == 0) c.Put(k, k, 1_000_000); else c.TryGet(k, out _);
            }
        } catch (Exception e) { error = e; }
    });
    T.Eq("no exception under 8 threads", error == null ? "none" : error.GetType().Name + ": " + error.Message, "none");
    T.True("never above capacity", c.Count <= 64);
}
'''

# =============================================================================== the runs
RUNS = {
    # logging
    'L0':   dict(code=LOGGER1 % P1_SKEL,  tests=HAND1),
    'L1b':  dict(code=P1_BAD,             tests=HAND1),
    'L1':   dict(code=LOGGER1 % P1_AI,    tests=HAND1),
    'L1f':  dict(code=LOGGER1 % P1_FIXED, tests=HAND1),
    'L2b':  dict(code=LOGGER2 % P2_BAD,   tests=HAND1 + HAND2),
    'L2':   dict(code=LOGGER2 % P2_AI,    tests=HAND1 + HAND2),
    'L2f':  dict(code=LOGGER2 % P2_FIXED, tests=HAND1 + HAND2),
    'L3b':  dict(code=LOGGER2 % P2_FIXED, tests=HAND1 + HAND2, extra=AITESTS_BAD),
    'L3':   dict(code=LOGGER2 % P2_FIXED, tests=HAND1 + HAND2 + AITESTS, types=[THROWER]),
    'L3f':  dict(code=LOGGER2 % P2_FIXED, tests=HAND1 + HAND2 + AITESTS_FIXED, types=[THROWER]),
    'L4b':  dict(code=LOGGER2 % P4_BAD,   tests=STRESS_LOG + TIMING, types=[SLOWSINK]),
    'L4':   dict(code=LOGGER2 % P2_FIXED, tests=STRESS_LOG + TIMING, types=[SLOWSINK]),
    'L5b':  dict(code=LOGGER2 % P2_FIXED, code2=ASYNC_BAD, tests=ASYNC_BAD_TEST),
    'L5':   dict(code=LOGGER2 % P2_FIXED, code2=ASYNC_AI,    tests=ASYNC_TEST, types=[SPINSINK]),
    'L5f':  dict(code=LOGGER2 % P2_FIXED, code2=ASYNC_FIXED, tests=ASYNC_TEST, types=[SPINSINK]),
    # LRU
    'R1b':  dict(code=LRU_BAD,            tests=HAND_LRU),
    'R1':   dict(code=LRU % LRU_AI,       tests=HAND_LRU),
    'R1f':  dict(code=LRU % LRU_FIXED,    tests=HAND_LRU),
    'R2':   dict(code=ttl(TTL_METHODS),       tests=HAND_TTL),
    'R2f':  dict(code=ttl(TTL_FIXED_METHODS), tests=HAND_TTL),
    'R3b':  dict(code=ttl(TTL_CONC_METHODS, conc=True), tests=HAND_TTL + STRESS_LRU),
    'R3':   dict(code=ttl(TTL_LOCKED_METHODS, locked=True), tests=HAND_TTL + STRESS_LRU),
}

# What each run must show, so a change to the code above cannot silently turn a teaching failure
# into a pass (or the reverse). 'build' = compile errors, 'crash' = unhandled exception.
EXPECT = {'L0': 'crash', 'L1b': 'build', 'L1': 'fail', 'L1f': 'pass', 'L2b': 'crash', 'L2': 'fail', 'L2f': 'pass',
          'L3b': 'build', 'L3': 'fail', 'L3f': 'pass', 'L4b': 'pass', 'L4': 'pass', 'L5b': 'fail', 'L5': 'fail',
          'L5f': 'pass', 'R1b': 'build', 'R1': 'fail', 'R1f': 'pass', 'R2': 'fail', 'R2f': 'pass', 'R3b': 'fail',
          'R3': 'pass'}
