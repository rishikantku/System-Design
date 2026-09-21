# -*- coding: utf-8 -*-
"""Extra Staff Coding drills, weighted the way the pack describes the module:
modularity and extensibility, finding and fixing bugs, pointers, edge cases."""

DRILLS = [
 dict(id='bug_lru', title='Bug hunt: an LRU cache with four defects', level='med', topic='Bug-finding · Pointers',
  why='The pack says these sessions involve **pointers, edge cases and abstraction**, and that finding and fixing bugs is half '
      'the module. A doubly linked list with a map is where pointer bugs live.',
  question='This LRU cache passes a naive test and is wrong in four ways. Find every defect, fix them, and say how you would '
           'test each fix.',
  think='Trace one eviction by hand on paper before you read the code again: put, put, get the first key, put a third. Which '
        'structure is updated, and which is left stale? Then ask what happens at capacity 1, and what `Get` returns for a value '
        'that legitimately equals the miss sentinel.',
  approach='Restate the contract first: O(1) get and put, most-recently-used at the front, and eviction removes from **both** the '
           'list and the map. Then read for the four classes of defect that live in this shape of code — stale map entries, '
           'missing recency updates, boundary capacities, and a return value that cannot distinguish "missing" from "stored".\n\n'
           '**The four defects:** `Get` does not move the node to the front (so it is a FIFO cache, not LRU); eviction removes the '
           'node from the list but never from `_map` (a slow leak that also returns dead nodes); the constructor accepts capacity 0 '
           'and then divides the logic by an empty list on the first put; and `Get` returns `-1` as a sentinel, which is '
           'indistinguishable from a stored `-1`.',
  edges=['Capacity 0 or negative → reject in the constructor.',
         'Capacity 1 → every put evicts; the list must never be left with a dangling head.',
         'Put on an existing key → update the value *and* the recency, without inserting a duplicate node.',
         'Get on a missing key → must be distinguishable from a stored default value.',
         'Evicting the only node → head and tail sentinels must still be linked.'],
  code='''// BEFORE — four defects. Read the whole class before you touch it.
public class LruCache {
    private class Node { public int Key, Value; public Node Prev, Next; }

    private readonly int _capacity;
    private readonly Dictionary<int, Node> _map = new();
    private readonly Node _head = new(), _tail = new();

    public LruCache(int capacity) {                       // (3) accepts 0 and negative
        _capacity = capacity;
        _head.Next = _tail; _tail.Prev = _head;
    }

    public int Get(int key) {
        if (!_map.TryGetValue(key, out var n)) return -1; // (4) -1 collides with a stored -1
        return n.Value;                                   // (1) no recency update: this is FIFO, not LRU
    }

    public void Put(int key, int value) {
        if (_map.TryGetValue(key, out var existing)) { existing.Value = value; MoveToFront(existing); return; }
        if (_map.Count == _capacity) {
            var victim = _tail.Prev;
            Unlink(victim);                               // (2) removed from the list, never from _map
        }
        var node = new Node { Key = key, Value = value };
        _map[key] = node;
        AddFront(node);
    }

    private void MoveToFront(Node n) { Unlink(n); AddFront(n); }
    private static void Unlink(Node n) { n.Prev.Next = n.Next; n.Next.Prev = n.Prev; }
    private void AddFront(Node n) { n.Next = _head.Next; n.Prev = _head; _head.Next.Prev = n; _head.Next = n; }
}

// AFTER — contract stated, four defects fixed, shape unchanged.
/// <summary>Least-recently-used cache. Get and Put are O(1). Get counts as a use.</summary>
public sealed class LruCache<TKey, TValue> {
    private sealed class Node { public TKey Key; public TValue Value; public Node Prev, Next; }

    private readonly int _capacity;
    private readonly Dictionary<TKey, Node> _map;
    private readonly Node _head = new(), _tail = new();

    public LruCache(int capacity) {
        if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity), "capacity must be positive");
        _capacity = capacity;
        _map = new Dictionary<TKey, Node>(capacity);
        _head.Next = _tail; _tail.Prev = _head;
    }

    public bool TryGet(TKey key, out TValue value) {       // no sentinel: missing is a distinct outcome
        if (!_map.TryGetValue(key, out var n)) { value = default; return false; }
        MoveToFront(n);                                    // Get is a use
        value = n.Value;
        return true;
    }

    public void Put(TKey key, TValue value) {
        if (_map.TryGetValue(key, out var existing)) { existing.Value = value; MoveToFront(existing); return; }
        if (_map.Count == _capacity) {
            var victim = _tail.Prev;
            Unlink(victim);
            _map.Remove(victim.Key);                       // both structures, always together
        }
        var node = new Node { Key = key, Value = value };
        _map[key] = node;
        AddFront(node);
    }

    public int Count => _map.Count;                        // useful for the leak test

    private void MoveToFront(Node n) { Unlink(n); AddFront(n); }
    private static void Unlink(Node n) { n.Prev.Next = n.Next; n.Next.Prev = n.Prev; }
    private void AddFront(Node n) { n.Next = _head.Next; n.Prev = _head; _head.Next.Prev = n; _head.Next = n; }
}''',
  complexity='Unchanged: O(1) per operation, O(capacity) memory. The leak in the original is the interesting one — it is not a '
             'complexity bug, it is an unbounded-memory bug that only shows up after thousands of evictions.',
  follow=['Which defect would production notice first? (The leak — memory grows and stale nodes are returned.)',
          'Write the one test that catches the FIFO-versus-LRU defect. (Put A, put B, get A, put C: B must be evicted.)',
          'How would you prove the leak is fixed? (Assert `Count` never exceeds capacity after N puts.)',
          'Now make Get thread-safe — and say why Get is a write.'],
  optimise='Nothing here needs to be faster; it needs to be right. If asked, the real optimisation is removing the `_map.Remove` '
           'foot-gun entirely by making eviction a single method that owns both structures — a design fix rather than a patch.',
  evalpts=['Did you find all four, including the silent leak?',
           'Did you name each defect before editing?',
           'Did you replace the sentinel return rather than documenting it?',
           'Did you write the LRU-versus-FIFO test?',
           'Did you keep the class shape rather than rewriting it from scratch?']),

 dict(id='bug_range', title='Bug hunt: a date-range utility with off-by-one and overflow', level='med', topic='Bug-finding · Edge cases',
  why='"Pointers, edge cases, or all of the above" — this is the edge-case half. Range arithmetic is where boundary defects hide, '
      'and every one of these bugs has shipped in real systems.',
  question='This utility decides whether ranges overlap, merges them, and splits a range into buckets. It has five defects, '
           'including one that only appears near `int.MaxValue` and one that depends on the machine\'s time zone.',
  think='Write down the contract for "overlap" before reading: are ranges half-open `[start, end)` or closed `[start, end]`? '
        'Almost every defect below comes from the code not deciding. Then ask: where does arithmetic leave the range of the type, '
        'and where does the code trust the ambient clock?',
  approach='State the convention: **half-open `[start, end)`**, which makes adjacent buckets tile without overlap and makes '
           '"touching" ranges unambiguous. Then hunt.\n\n'
           '**The five defects:** `Overlaps` uses `<=` on both sides, so `[1,2)` and `[2,3)` are reported as overlapping; '
           '`Merge` assumes the input is sorted and silently produces garbage if it is not; `Bucket` computes `(end - start) / size` '
           'with ints, so a wide range overflows; `Contains` uses `DateTime.Now` instead of an injected clock, so tests are '
           'time-zone dependent and flaky; and an empty range (`start == end`) is treated as containing its start.',
  edges=['Touching ranges `[1,2)` and `[2,3)` — overlap or not? Decide, then encode.',
         'Empty range where `start == end` — contains nothing.',
         'Inverted range where `end < start` — reject loudly at construction.',
         'A range spanning almost the whole `int` domain (overflow in subtraction).',
         'Bucket size 0 or negative.',
         'A range that does not divide evenly into buckets — is the last bucket short, or dropped?'],
  code='''// BEFORE — five defects.
public class Ranges {
    public static bool Overlaps(int aStart, int aEnd, int bStart, int bEnd)
        => aStart <= bEnd && bStart <= aEnd;                       // (1) treats touching ranges as overlapping

    public static List<(int, int)> Merge(List<(int Start, int End)> ranges) {
        var result = new List<(int, int)>();
        foreach (var r in ranges) {                                // (2) assumes sorted input
            if (result.Count > 0 && r.Start <= result[^1].Item2)
                result[^1] = (result[^1].Item1, Math.Max(result[^1].Item2, r.End));
            else result.Add(r);
        }
        return result;
    }

    public static int BucketCount(int start, int end, int size)
        => (end - start) / size;                                   // (3) overflows; (6) no size validation

    public static bool Contains(int start, int end, int point)
        => point >= start && point <= end;                         // (5) empty range "contains" its start

    public static bool IsExpired(DateTime expiry) => expiry < DateTime.Now;   // (4) local clock, not injected
}

// AFTER — one stated convention, defects fixed.
/// <summary>Half-open ranges [Start, End). Adjacent ranges touch but do not overlap.</summary>
public readonly record struct Range {
    public int Start { get; }
    public int End { get; }

    public Range(int start, int end) {
        if (end < start) throw new ArgumentException($"inverted range [{start}, {end})");
        Start = start; End = end;
    }

    public bool IsEmpty => Start == End;
    public bool Contains(int point) => point >= Start && point < End;          // half-open: empty contains nothing

    public bool Overlaps(Range other) => Start < other.End && other.Start < End;   // strict: touching is not overlap

    public static IReadOnlyList<Range> Merge(IEnumerable<Range> ranges) {
        var sorted = ranges.Where(r => !r.IsEmpty).OrderBy(r => r.Start).ThenBy(r => r.End).ToList();  // sort, do not assume
        var result = new List<Range>();
        foreach (var r in sorted) {
            if (result.Count > 0 && r.Start <= result[^1].End)                  // <= merges touching ranges deliberately
                result[^1] = new Range(result[^1].Start, Math.Max(result[^1].End, r.End));
            else result.Add(r);
        }
        return result;
    }

    public long BucketCount(int size) {
        if (size <= 0) throw new ArgumentOutOfRangeException(nameof(size));
        long span = (long)End - Start;                                          // widen before subtracting
        return (span + size - 1) / size;                                        // last bucket may be short, by contract
    }
}

public interface IClock { DateTime UtcNow { get; } }
public sealed class SystemClock : IClock { public DateTime UtcNow => DateTime.UtcNow; }

public sealed class Expiry {
    private readonly IClock _clock;
    public Expiry(IClock clock) => _clock = clock;                              // injected: tests are deterministic
    public bool IsExpired(DateTime expiryUtc) => expiryUtc <= _clock.UtcNow;
}''',
  complexity='`Merge` is O(n log n) once you stop assuming sorted input — and that is the correct trade: a silent wrong answer is '
             'worse than a sort. Everything else is O(1).',
  follow=['Which convention did you choose, and what would change if the interviewer insists on closed ranges?',
          'Write the overflow test. (`new Range(int.MinValue, int.MaxValue).BucketCount(1000)`.)',
          'Why does injecting the clock matter beyond testing? (Time-zone and NTP jumps in production.)',
          'Should `Merge` combine touching ranges? Defend either answer — just be consistent with `Overlaps`.'],
  optimise='If `Merge` is called in a hot loop with already-sorted input, expose an overload that documents the precondition '
           'rather than sorting — but make the unsafe one the explicit, named choice, not the default.',
  evalpts=['Did you state the half-open convention before hunting bugs?',
           'Did you find the overflow and the ambient clock?',
           'Did you reject inverted ranges at construction instead of defending everywhere?',
           'Did you notice that `Overlaps` and `Merge` disagreed about touching ranges?',
           'Did you name the tests for each fix?']),

 dict(id='ext_parser', title='Extensibility: a file-import pipeline that keeps gaining formats', level='med', topic='Abstraction · Modularity',
  why='The pack\'s exact words: **modularity and extensibility**. This is the shape that recurs — a switch statement that a new '
      'requirement is about to make unmaintainable.',
  question='This importer handles CSV. Product wants JSON lines and a fixed-width legacy format, per-format validation, and the '
           'ability to add a format without touching the importer. It also needs to report per-row errors instead of failing the '
           'whole file. Refactor it.',
  think='Which parts are stable and which vary? Reading bytes, iterating rows, collecting errors and writing to the sink are '
        'stable. Detecting the format, turning a line into fields, and format-specific validation vary. Where is the seam, and '
        'what is the smallest interface that expresses it?',
  approach='Introduce `IRecordFormat` with `CanHandle` and `TryRead`, register implementations, and keep the pipeline (streaming, '
           'error collection, batching, sink writes) in one place. Validation splits into two: **structural** (the format\'s job) '
           'and **business rules** (the pipeline\'s job, applied to every format identically).\n\n'
           'Say the acceptance test out loud: *adding a format means adding one class and one registration, and changing nothing '
           'else.* That sentence is what the interviewer is listening for.',
  edges=['An unknown or ambiguous format — fail at detection with a clear message, not halfway through the file.',
         'A file where row 3 of 100,000 is malformed — report and continue, do not abort.',
         'An empty file, and a file with only a header.',
         'A format whose rows span multiple lines (quoted newlines in CSV) — does your seam still hold?',
         'Duplicate rows across a resumed import (idempotency).',
         'Encoding: UTF-8 with a BOM, and a legacy file in Windows-1252.'],
  code='''public readonly record struct RowError(long LineNumber, string Reason, string Raw);

public interface IRecordFormat {
    string Name { get; }
    bool CanHandle(ReadOnlySpan<char> firstLine, string fileName);
    /// <summary>Structural parse only. Business rules live in the pipeline.</summary>
    bool TryRead(string line, long lineNumber, out ImportRecord record, out string error);
}

public sealed class CsvFormat : IRecordFormat { /* ... */
    public string Name => "csv";
    public bool CanHandle(ReadOnlySpan<char> firstLine, string fileName)
        => fileName.EndsWith(".csv", StringComparison.OrdinalIgnoreCase) || firstLine.Contains(',');
    public bool TryRead(string line, long lineNumber, out ImportRecord record, out string error) { /* ... */ }
}

public sealed class Importer {
    private readonly IReadOnlyList<IRecordFormat> _formats;
    private readonly IReadOnlyList<IRecordRule> _rules;         // business rules, applied to every format
    private readonly IRecordSink _sink;
    private readonly int _batchSize;

    public Importer(IEnumerable<IRecordFormat> formats, IEnumerable<IRecordRule> rules,
                    IRecordSink sink, int batchSize = 500) {
        _formats = formats.ToList(); _rules = rules.ToList(); _sink = sink; _batchSize = batchSize;
    }

    public async Task<ImportReport> ImportAsync(Stream stream, string fileName, CancellationToken ct) {
        using var reader = new StreamReader(stream, detectEncodingFromByteOrderMarks: true);

        var first = await reader.ReadLineAsync(ct);
        if (first is null) return ImportReport.Empty;

        var format = _formats.FirstOrDefault(f => f.CanHandle(first, fileName))
            ?? throw new NotSupportedException($"no registered format handles '{fileName}'");   // fail at the boundary

        var errors = new List<RowError>();
        var batch = new List<ImportRecord>(_batchSize);
        long line = 0;

        for (var text = first; text is not null; text = await reader.ReadLineAsync(ct)) {
            line++;
            if (!format.TryRead(text, line, out var record, out var structural)) {
                errors.Add(new RowError(line, structural, text));               // report and continue
                continue;
            }
            var broken = _rules.FirstOrDefault(r => !r.IsSatisfied(record));
            if (broken is not null) { errors.Add(new RowError(line, broken.Describe(record), text)); continue; }

            batch.Add(record);
            if (batch.Count == _batchSize) { await _sink.WriteAsync(batch, ct); batch.Clear(); }
        }
        if (batch.Count > 0) await _sink.WriteAsync(batch, ct);

        return new ImportReport(format.Name, line, errors);
    }
}''',
  complexity='One pass over the file, O(1) memory beyond one batch. The extensibility property matters more here than the '
             'complexity: adding a format touches one new class plus registration.',
  follow=['Add the fixed-width legacy format — how many existing files do you change? (One: the registration.)',
          'Two formats both claim `CanHandle` — how do you resolve it? (Ordered registration, or explicit selection; say which.)',
          'Where would you put per-format business rules that genuinely differ?',
          'How do you test the pipeline without real files or a real sink? (A fake format and an in-memory sink.)',
          'Make it resumable after a crash at row 80,000.'],
  optimise='If profiling shows the allocation of one string per line hurts, move to `ReadOnlySequence<byte>` and span-based '
           'parsing behind the same interface — the seam is what lets you do that without touching callers.',
  evalpts=['Can a new format be added without editing `Importer`?',
           'Did you separate structural parsing from business rules?',
           'Are errors per row, with line numbers and the raw text?',
           'Did you decide the ambiguous-format rule explicitly?',
           'Did you keep it simple — no reflection-based auto-discovery unless asked?']),

 dict(id='ext_retry', title='Extensibility: one retry policy, five callers, no copy-paste', level='med', topic='Abstraction · Reliability',
  why='Extensibility in the small: the abstraction everyone reinvents badly. It also sets up the AI-round and design-round '
      'conversations about failure handling, so it pays twice.',
  question='Five call sites each have their own retry loop, with subtly different backoff, different ideas of what is retryable, '
           'and two of them retrying non-idempotent operations. Design one mechanism they can all use, and say what you would '
           'refuse to make configurable.',
  think='What genuinely varies (how many attempts, how long to wait, what counts as transient) and what must never vary (never '
        'retry a non-idempotent operation without an idempotency key, always respect cancellation, always bound total time)? '
        'The second list is the interesting one: good abstractions make the dangerous thing impossible, not configurable.',
  approach='A small policy object plus an executor. The policy owns attempts, backoff and the transient-error predicate. The '
           'executor owns cancellation, the total deadline, and the rule that only operations declared idempotent may be retried. '
           'Expose named presets rather than a dozen knobs, so call sites converge on three shapes instead of five.',
  edges=['Zero retries configured — the operation must still run once.',
         'A caller\'s deadline shorter than the backoff — do not sleep past it.',
         'Cancellation during the backoff delay.',
         'An exception that is transient sometimes and fatal other times (a 429 versus a 400).',
         'A non-idempotent operation — the API should make retrying it awkward, not easy.',
         'Nested retries (a retrying client called inside a retrying handler) — bound the multiplication, and say it out loud.'],
  code='''public sealed record RetryPolicy(
    int MaxRetries,
    Func<int, TimeSpan> Backoff,
    Func<Exception, bool> IsTransient) {

    public static readonly RetryPolicy None = new(0, _ => TimeSpan.Zero, _ => false);

    public static RetryPolicy Exponential(int retries, TimeSpan baseDelay, Func<Exception, bool> transient) =>
        new(retries,
            attempt => TimeSpan.FromMilliseconds(
                baseDelay.TotalMilliseconds * Math.Pow(2, attempt) + Random.Shared.Next(0, 100)),   // jitter built in
            transient);

    // Named presets: call sites pick a shape, not fifteen knobs.
    public static RetryPolicy FastNetwork => Exponential(3, TimeSpan.FromMilliseconds(100), IsTransientHttp);
    public static RetryPolicy Patient     => Exponential(6, TimeSpan.FromMilliseconds(500), IsTransientHttp);

    private static bool IsTransientHttp(Exception ex) => ex switch {
        HttpRequestException { StatusCode: HttpStatusCode.TooManyRequests } => true,
        HttpRequestException { StatusCode: >= HttpStatusCode.InternalServerError } => true,
        TimeoutException => true,
        _ => false
    };
}

public static class Retry {
    /// <summary>Only idempotent work may be retried — the type system nudges you, the name shouts at you.</summary>
    public static async Task<T> IdempotentAsync<T>(
            Func<CancellationToken, Task<T>> operation,
            RetryPolicy policy,
            TimeSpan totalBudget,
            CancellationToken ct = default) {

        var deadline = DateTime.UtcNow + totalBudget;
        Exception last = null;

        for (int attempt = 0; attempt <= policy.MaxRetries; attempt++) {
            ct.ThrowIfCancellationRequested();
            try { return await operation(ct); }
            catch (OperationCanceledException) { throw; }                 // never a retryable failure
            catch (Exception ex) when (policy.IsTransient(ex)) {
                last = ex;
                if (attempt == policy.MaxRetries) break;
                var wait = policy.Backoff(attempt);
                if (DateTime.UtcNow + wait >= deadline) break;            // do not sleep past the caller's deadline
                await Task.Delay(wait, ct);
            }
        }
        throw new RetryExhaustedException($"failed after {policy.MaxRetries + 1} attempts", last);
    }
}

// Non-idempotent work must carry a key — retrying is then safe by construction.
public static Task<T> WithIdempotencyKeyAsync<T>(
        Func<string, CancellationToken, Task<T>> operation, string key,
        RetryPolicy policy, TimeSpan budget, CancellationToken ct = default)
    => Retry.IdempotentAsync(c => operation(key, c), policy, budget, ct);''',
  complexity='Not a complexity question. The property that matters: total wall-clock time is bounded by the budget, not by '
             'attempts × per-attempt timeout — which is the bug the five hand-rolled loops all had.',
  follow=['What did you refuse to make configurable, and why? (Retrying non-idempotent work; ignoring cancellation.)',
          'What happens when a retrying client sits inside a retrying handler? (Multiplication — bound it, or disable the inner one.)',
          'Where does a circuit breaker fit, and why is it not the same thing as a retry?',
          'How do you test backoff without waiting? (Inject the delay function, or a virtual clock.)',
          'Should the policy be per call site or per dependency? Defend it.'],
  optimise='Nothing to optimise; the win is deletion. Count the lines removed from the five call sites and say that number — '
           '"this deleted 140 lines and one class of production incident" is a strong closing sentence.',
  evalpts=['Did you separate what varies from what must not?',
           'Is the dangerous case (non-idempotent retry) hard to do by accident?',
           'Did you bound total time, not just attempts?',
           'Did you offer presets rather than raw knobs?',
           'Did you say how to test it without sleeping?']),

 dict(id='bug_list', title='Bug hunt: doubly linked list splice and merge', level='hard', topic='Pointers · Edge cases',
  why='The pack names **pointers** first. This is the purest pointer drill: four sentinel and boundary defects that a debugger '
      'finds slowly and a careful reading finds fast.',
  question='`Splice` moves a sub-range of one list into another; `MergeSorted` merges two sorted lists in place. Both have '
           'defects around the boundaries. Find and fix them, then write the tests that prove it.',
  think='Draw the pointers for the smallest cases: splicing a single node, splicing the entire list, and merging when one list is '
        'empty. Every defect here is a case where a pointer is updated in one direction but not the other, or where the sentinel '
        'is treated as a real node.',
  approach='Work with sentinels and never special-case null. State the invariant out loud: **after any operation, for every node '
           '`n`, `n.Prev.Next == n` and `n.Next.Prev == n`, and both sentinels are reachable.** Then write that invariant as a '
           'debug-only assertion and run it after every test — that single helper finds all four defects faster than a debugger.\n\n'
           '**The four defects:** `Splice` does not update `to`\'s backward pointer when inserting at the end; splicing a range '
           'that includes the source\'s last node leaves the source tail dangling; `MergeSorted` loses the tail of the longer list; '
           'and merging a list with itself silently builds a cycle.',
  edges=['Splice a single node.', 'Splice the entire source list (source must end up empty and still valid).',
         'Splice into an empty destination.', 'Splice a range that ends at the source tail.',
         'Merge where one list is empty, and where both are.', 'Merge a list with itself — reject it explicitly.',
         'Equal keys across the two lists (stability).'],
  code='''public sealed class DList<T> {
    public sealed class Node { public T Value; public Node Prev, Next; }

    private readonly Node _head = new(), _tail = new();            // sentinels: never null-check in the middle
    public DList() { _head.Next = _tail; _tail.Prev = _head; }

    public bool IsEmpty => _head.Next == _tail;

    /// <summary>Moves [first..last] out of <paramref name="source"/> and inserts it after <paramref name="after"/>.</summary>
    public void Splice(DList<T> source, Node first, Node last, Node after) {
        if (ReferenceEquals(source, this) ) throw new ArgumentException("splicing within one list needs the in-place overload");
        if (first is null || last is null || after is null) throw new ArgumentNullException();

        // 1. unlink the range from the source — both directions
        first.Prev.Next = last.Next;
        last.Next.Prev = first.Prev;                                // the defect people miss when last is the final node

        // 2. link it into this list after `after` — both directions
        var following = after.Next;
        after.Next = first;  first.Prev = after;
        last.Next = following; following.Prev = last;               // the defect people miss when inserting at the end

        AssertInvariant(); source.AssertInvariant();
    }

    /// <summary>Merges <paramref name="other"/> into this list, both assumed sorted. Stable: ties keep this list first.</summary>
    public void MergeSorted(DList<T> other, IComparer<T> cmp) {
        if (ReferenceEquals(other, this)) throw new ArgumentException("cannot merge a list with itself");

        var a = _head.Next;
        var b = other._head.Next;

        while (a != _tail && b != other._tail) {
            if (cmp.Compare(b.Value, a.Value) < 0) {
                var move = b;
                b = b.Next;                                          // advance before relinking, or you lose the rest
                Unlink(move);
                InsertBefore(a, move);
            } else {
                a = a.Next;
            }
        }
        while (b != other._tail) {                                   // the tail of the longer list: the classic loss
            var move = b;
            b = b.Next;
            Unlink(move);
            InsertBefore(_tail, move);
        }
        AssertInvariant();
    }

    private static void Unlink(Node n) { n.Prev.Next = n.Next; n.Next.Prev = n.Prev; }
    private static void InsertBefore(Node at, Node n) {
        n.Prev = at.Prev; n.Next = at;
        at.Prev.Next = n; at.Prev = n;
    }

    [Conditional("DEBUG")]
    public void AssertInvariant() {                                  // the helper that finds every pointer bug
        for (var n = _head; n != _tail; n = n.Next) {
            Debug.Assert(n.Next is not null, "forward chain broken");
            Debug.Assert(ReferenceEquals(n.Next.Prev, n), "backward pointer does not match");
        }
    }
}''',
  complexity='Splice is O(1) — that is the entire reason to use a linked list here, and it is worth saying, because an interviewer '
             'may ask why not a `List<T>`. Merge is O(n + m) with no allocation.',
  follow=['Why a linked list at all? (O(1) splice with stable node identity — otherwise use an array.)',
          'Make `AssertInvariant` cheap enough to leave on in tests but off in release. (It already is: `[Conditional("DEBUG")]`.)',
          'Make the list support an in-place splice within the same list.',
          'Now make it thread-safe — and explain why that is much harder than it looks.'],
  optimise='If nodes are allocated and freed constantly, pool them. But the real optimisation here is the invariant helper: it '
           'turns a class of bug that takes an hour in a debugger into a failing assertion.',
  evalpts=['Did you write the invariant before hunting?',
           'Did you find the dangling tail and the lost remainder?',
           'Did you reject merging a list with itself rather than producing a cycle?',
           'Did you test splice-the-whole-list and merge-with-empty?',
           'Did you justify the linked list over an array?']),
]
