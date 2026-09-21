# -*- coding: utf-8 -*-
"""CWAI drills: ordinary data-structure and algorithm problems, run the way the
Coding with AI module runs them — plan yourself, delegate deliberately, verify
everything, narrate throughout.

Each drill: problem, clarify, plan (before prompting), prompts (verbatim),
verify (the tests you run), code (C# reference), traps (what assistants get
wrong on this specific problem), follow-ups, self-evaluation."""

DRILLS = [
 dict(id='lfurank', title='LFU cache with GetRank()', topic='Design · Caches', mins=35,
  problem='Implement a cache with `Get`, `Put` and `GetRank(key)`, evicting the least frequently used entry and breaking ties by '
          'least recently used. `GetRank` returns the position of a key when entries are ordered by frequency (most frequent = rank 1). '
          'Get and Put should stay O(1).',
  clarify=['Is rank 1 the most frequent or the least?', 'What does GetRank return for a missing key — 0, -1, or an exception?',
           'Does GetRank itself count as an access (does it change frequency)?', 'What is the capacity, and can it be zero?',
           'Do ties in frequency need a defined rank order, or is any consistent order fine?'],
  plan='Decide the structure before you type a prompt: a map `key → node`, a map `frequency → doubly linked list of nodes`, and a '
       '`minFrequency` counter. That gives O(1) get and put. Then be honest out loud that **GetRank cannot be O(1)** with that '
       'structure — ranking needs either a walk over frequency buckets (O(distinct frequencies)) or a separate order-statistics '
       'structure (a Fenwick tree over frequencies, O(log n)). Saying which trade you are making, before the assistant offers one, '
       'is the whole point of this round.',
  prompts=['"I am implementing an LFU cache in C#: Dictionary<TKey,Node>, Dictionary<int,LinkedList<Node>> by frequency, and a '
           'minFreq field. Write just the Put method, keeping O(1), and do not change my field names."',
           '"Now write xunit tests for: capacity 1, updating an existing key, eviction when two keys share the lowest frequency '
           '(LRU must lose), and GetRank on a missing key."',
           '"I need GetRank. Give me two options — walking frequency buckets, and a Fenwick tree over frequency counts — with the '
           'complexity of each. Do not write the code yet."',
           '"Review this method for off-by-one errors in the minFreq update after an eviction."'],
  verify=['Capacity 1 — put, put, get: the first key must be gone.',
          'Two keys at frequency 1, one touched more recently: eviction must drop the other.',
          'minFreq after evicting the last node of its bucket — does it reset to 1 on the next insert?',
          'GetRank on a missing key, and on the only key.',
          'GetRank after a Get (did frequency change, and did you say it would?).'],
  code='''public sealed class LfuCache<TKey, TValue> {
    private sealed class Node {
        public TKey Key; public TValue Value; public int Freq;
        public LinkedListNode<Node> Handle;               // position inside its frequency list
    }

    private readonly int _capacity;
    private readonly Dictionary<TKey, Node> _byKey;
    private readonly Dictionary<int, LinkedList<Node>> _byFreq = new();
    private readonly SortedDictionary<int, int> _countPerFreq = new();   // frequency -> how many keys (for GetRank)
    private int _minFreq;

    public LfuCache(int capacity) {
        if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        _capacity = capacity;
        _byKey = new Dictionary<TKey, Node>(capacity);
    }

    public bool TryGet(TKey key, out TValue value) {
        if (!_byKey.TryGetValue(key, out var n)) { value = default; return false; }
        Touch(n);
        value = n.Value;
        return true;
    }

    public void Put(TKey key, TValue value) {
        if (_byKey.TryGetValue(key, out var existing)) { existing.Value = value; Touch(existing); return; }

        if (_byKey.Count == _capacity) {
            var victimList = _byFreq[_minFreq];
            var victim = victimList.Last.Value;            // least recently used within the lowest frequency
            victimList.RemoveLast();
            if (victimList.Count == 0) _byFreq.Remove(_minFreq);
            Decrement(_minFreq);
            _byKey.Remove(victim.Key);
        }

        var node = new Node { Key = key, Value = value, Freq = 1 };
        node.Handle = ListFor(1).AddFirst(node);
        _byKey[key] = node;
        Increment(1);
        _minFreq = 1;                                      // a brand-new key always resets the floor
    }

    /// <summary>1 = most frequent. O(distinct frequencies) — say so, and offer the O(log n) variant.</summary>
    public int GetRank(TKey key) {
        if (!_byKey.TryGetValue(key, out var n)) return -1;
        int ahead = 0;
        foreach (var (freq, count) in _countPerFreq)       // ascending
            if (freq > n.Freq) ahead += count;
        return ahead + 1;
    }

    private void Touch(Node n) {
        var list = _byFreq[n.Freq];
        list.Remove(n.Handle);
        if (list.Count == 0) {
            _byFreq.Remove(n.Freq);
            if (_minFreq == n.Freq) _minFreq = n.Freq + 1; // the only place minFreq can advance
        }
        Decrement(n.Freq);
        n.Freq++;
        n.Handle = ListFor(n.Freq).AddFirst(n);
        Increment(n.Freq);
    }

    private LinkedList<Node> ListFor(int freq) =>
        _byFreq.TryGetValue(freq, out var l) ? l : _byFreq[freq] = new LinkedList<Node>();

    private void Increment(int freq) => _countPerFreq[freq] = _countPerFreq.GetValueOrDefault(freq) + 1;
    private void Decrement(int freq) {
        if (--_countPerFreq[freq] == 0) _countPerFreq.Remove(freq);
    }
}''',
  traps=['Assistants routinely produce an LFU where `minFreq` is never reset after an eviction — the next insert then evicts the '
         'wrong key. Test it before you trust it.',
         'They often drop the LRU tiebreak inside a frequency bucket, or use a `HashSet` (which has no order) instead of a list.',
         'They will happily claim GetRank is O(1). It is not, with this structure. Correct that out loud.',
         'Watch for a rank that counts the key itself, giving an off-by-one.'],
  follow=['Make GetRank O(log n) with a Fenwick tree over frequency counts.',
          'Make the whole thing thread-safe — and say what that costs on the hot path.',
          'Add TTL: does expiry change frequency accounting?'],
  evalpts=['Did you choose the structure before prompting?',
           'Did you say GetRank cannot be O(1) here, before the assistant told you?',
           'Did you test the minFreq-after-eviction case specifically?',
           'Did you reject at least one suggestion out loud, with a reason?']),

 dict(id='records', title='Parse and aggregate semi-structured records with malformed rows', topic='Parsing · Aggregation', mins=35,
  problem='You are given a stream of JSON-ish records: `{"user":"u1","event":"click","ts":1699999999,"value":3}`. Some rows are '
          'malformed, some are missing fields, some have the wrong type. Produce per-user totals of `value` for a given event '
          'type, and a report of how many rows were rejected and why.',
  clarify=['Reject a bad row, or fail the batch?', 'Are duplicate records possible — do we deduplicate by an id?',
           'Is `ts` seconds or milliseconds, and do we need a time window?', 'Should a missing `value` count as 0 or as a rejection?',
           'How large is the input — does it fit in memory?'],
  plan='Model it as three separate things and say so: a **reader** (line in, `Result<Record>` out), a **validator** (typed errors, '
       'not exceptions), and an **aggregator** (per-user totals). Rejections need a reason code, because "we skipped 412 rows" with '
       'no breakdown is the answer that fails the follow-up. Decide up front that one bad row never kills the run.',
  prompts=['"Write a C# record type and a TryParse that turns a JSON line into it, returning a typed failure reason instead of '
           'throwing, for these failure classes: unparseable JSON, missing required field, wrong type, out-of-range timestamp."',
           '"Generate 15 test inputs for this parser, including a truncated line, a nested object where a scalar is expected, a '
           'numeric string, a negative value and a duplicate id."',
           '"Given this aggregator, what happens if the same record arrives twice? Show me the failure, do not fix it yet."'],
  verify=['A truncated line, a line with a trailing comma, a completely empty line.',
          '`"value": "3"` — a numeric string. Accept or reject? Decide and test it.',
          'A record whose event type does not match the filter (must not count, must not be reported as rejected).',
          'Unicode in the user id, and a very long user id.',
          'Duplicates, if you decided to deduplicate.',
          'Totals when a user has only rejected rows — the user should not appear at all.'],
  code='''public enum RejectReason { None, Unparseable, MissingField, WrongType, BadTimestamp, Duplicate }

public readonly record struct ParseResult(EventRecord? Record, RejectReason Reason, string Detail) {
    public bool Ok => Reason == RejectReason.None;
    public static ParseResult Good(EventRecord r) => new(r, RejectReason.None, null);
    public static ParseResult Bad(RejectReason why, string detail) => new(null, why, detail);
}

public sealed record EventRecord(string User, string Event, long Ts, long Value, string Id);

public static class RecordParser {
    public static ParseResult TryParse(string line) {
        if (string.IsNullOrWhiteSpace(line)) return ParseResult.Bad(RejectReason.Unparseable, "blank line");

        JsonElement root;
        try { root = JsonDocument.Parse(line).RootElement; }
        catch (JsonException ex) { return ParseResult.Bad(RejectReason.Unparseable, ex.Message); }

        if (root.ValueKind != JsonValueKind.Object) return ParseResult.Bad(RejectReason.WrongType, "not an object");
        if (!root.TryGetProperty("user", out var user) || user.ValueKind != JsonValueKind.String)
            return ParseResult.Bad(RejectReason.MissingField, "user");
        if (!root.TryGetProperty("event", out var ev) || ev.ValueKind != JsonValueKind.String)
            return ParseResult.Bad(RejectReason.MissingField, "event");
        if (!root.TryGetProperty("ts", out var ts) || !ts.TryGetInt64(out var tsv))
            return ParseResult.Bad(RejectReason.WrongType, "ts");
        if (tsv <= 0 || tsv > 4_102_444_800) return ParseResult.Bad(RejectReason.BadTimestamp, tsv.ToString());

        long value = 0;
        if (root.TryGetProperty("value", out var v)) {
            if (!v.TryGetInt64(out value))                       // a numeric string is a WrongType by our contract
                return ParseResult.Bad(RejectReason.WrongType, "value");
        }
        var id = root.TryGetProperty("id", out var idEl) && idEl.ValueKind == JsonValueKind.String ? idEl.GetString() : null;
        return ParseResult.Good(new EventRecord(user.GetString(), ev.GetString(), tsv, value, id));
    }
}

public sealed class Aggregator {
    private readonly string _eventType;
    private readonly HashSet<string> _seenIds = new();
    private readonly Dictionary<string, long> _totals = new();
    private readonly Dictionary<RejectReason, int> _rejects = new();

    public Aggregator(string eventType) => _eventType = eventType;

    public void Add(string line) {
        var parsed = RecordParser.TryParse(line);
        if (!parsed.Ok) { Bump(parsed.Reason); return; }

        var r = parsed.Record!;
        if (r.Event != _eventType) return;                        // filtered, not rejected — different thing
        if (r.Id is not null && !_seenIds.Add(r.Id)) { Bump(RejectReason.Duplicate); return; }

        _totals[r.User] = _totals.GetValueOrDefault(r.User) + r.Value;
    }

    private void Bump(RejectReason why) => _rejects[why] = _rejects.GetValueOrDefault(why) + 1;

    public IReadOnlyDictionary<string, long> Totals => _totals;
    public IReadOnlyDictionary<RejectReason, int> Rejections => _rejects;
}''',
  traps=['Assistants tend to wrap everything in try/catch and return `null`, losing the reason. Insist on typed failures.',
         'They will silently accept `"value": "3"`. That is a product decision, not a parser detail — make it explicit.',
         'They often conflate "filtered out by event type" with "rejected", which corrupts your report.',
         'Generated tests usually cover the happy path and one bad case. Ask for the nasty ones by name.'],
  follow=['The file is 200 GB — stream it, and keep memory bounded.',
          'Now aggregate per user *and* per hour.', 'Now run it across 16 threads: what breaks in this code?',
          'Rejected rows need to be replayable after a fix — where do they go?'],
  evalpts=['Did you separate read, validate and aggregate?',
           'Are rejection reasons typed and counted?',
           'Did you decide the numeric-string question explicitly?',
           'Did you ask for adversarial test inputs rather than accepting the first three?']),

 dict(id='timekv', title='Time-based key-value store', topic='Design · Binary search', mins=25,
  problem='Implement `Set(key, value, timestamp)` and `Get(key, timestamp)` where Get returns the value with the largest '
          'timestamp less than or equal to the requested one, or empty if none exists.',
  clarify=['Are timestamps strictly increasing per key? (It changes everything.)',
           'Can the same (key, timestamp) be set twice — overwrite or reject?',
           'What is returned when no value qualifies — null, empty string, or a TryGet pattern?',
           'Read-heavy or write-heavy? That decides list-plus-binary-search versus a sorted structure.'],
  plan='If timestamps arrive in increasing order per key, a `List<(long ts, TValue v)>` plus binary search is O(1) write and '
       'O(log n) read, with excellent cache behaviour. If they can arrive out of order, either insert in position (O(n) memmove, '
       'still fast in practice) or use a `SortedList`. State the assumption before you code, because the assistant will assume '
       'the easy case silently.',
  prompts=['"Implement a time-based key-value store in C#. Assume per-key timestamps are strictly increasing; use List plus binary '
           'search. Include a TryGet-style API rather than returning null."',
           '"Write the binary search as a separate method and give me the invariant as a comment — I want to check the boundary '
           'behaviour myself."',
           '"What happens in your implementation if Set is called with a timestamp lower than the last one for that key? Answer, '
           'do not fix."'],
  verify=['Get before any Set for that key.', 'Get at exactly a stored timestamp (must return that value, not the previous one).',
          'Get below the earliest timestamp.', 'Get above the latest timestamp.',
          'Two values at the same timestamp, if you allowed it.', 'A key with one entry.'],
  code='''public sealed class TimeMap<TValue> {
    private readonly Dictionary<string, List<(long Ts, TValue Value)>> _store = new();

    /// <summary>Assumes timestamps are non-decreasing per key. Throws if that contract is broken.</summary>
    public void Set(string key, TValue value, long timestamp) {
        if (!_store.TryGetValue(key, out var list)) _store[key] = list = new List<(long, TValue)>();
        if (list.Count > 0 && timestamp < list[^1].Ts)
            throw new ArgumentOutOfRangeException(nameof(timestamp), "timestamps must be non-decreasing per key");
        if (list.Count > 0 && timestamp == list[^1].Ts) list[^1] = (timestamp, value);   // overwrite, stated contract
        else list.Add((timestamp, value));
    }

    public bool TryGet(string key, long timestamp, out TValue value) {
        value = default;
        if (!_store.TryGetValue(key, out var list) || list.Count == 0) return false;

        // last index whose Ts <= timestamp; invariant: answer is in [lo, hi]
        int lo = 0, hi = list.Count - 1, found = -1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            if (list[mid].Ts <= timestamp) { found = mid; lo = mid + 1; }
            else hi = mid - 1;
        }
        if (found < 0) return false;
        value = list[found].Value;
        return true;
    }
}''',
  traps=['The classic generated bug is returning the value *after* the timestamp when an exact match exists — test the exact-match case.',
         'Assistants often return `""` for "not found", which hides a real empty value. Use TryGet.',
         'They rarely enforce the non-decreasing contract, so out-of-order writes corrupt the search silently.'],
  follow=['Now timestamps can arrive out of order.', 'Now support deletion at a timestamp (a tombstone).',
          'Now it must be thread-safe for many readers and occasional writers.',
          'Now the history must be trimmed to the last 24 hours.'],
  evalpts=['Did you state the ordering assumption before coding?',
           'Did you test the exact-match boundary?',
           'Did you keep the binary search invariant visible?',
           'Did you choose a TryGet API rather than a magic return value?']),

 dict(id='iterator', title='Debug and extend: a flattening iterator over nested data', topic='Iterators · Pointers · Edge cases', mins=30,
  problem='Here is a `NestedIterator` that should flatten arbitrarily nested lists of integers lazily. It has bugs. Fix them, '
          'then add `Peek()` and support for `Remove()` semantics being unsupported (throw properly).',
  clarify=['Must it be lazy, or may it flatten eagerly into a list first? (Laziness is usually the point.)',
           'Are empty nested lists allowed? (They are the bug magnet.)', 'Is the input mutable while iterating?',
           'Should `HasNext` be idempotent? (It must be.)'],
  plan='Hold a stack of iterators, not a stack of values, so nothing is materialised. The hard part is that `HasNext` has to do '
       'the work of skipping empty lists — and it must be safe to call twice. Say that before you prompt: it is the single '
       'decision the whole class turns on.',
  prompts=['"Here is my NestedIterator using a Stack<IEnumerator<NestedInteger>>. Review HasNext for the case of nested empty '
           'lists — [[],[[]],[1]] — and tell me what breaks. Do not rewrite the class."',
           '"Write a test that fails for the empty-nested-list case, using xunit."',
           '"Now add Peek() without breaking laziness, keeping HasNext idempotent."'],
  verify=['`[[], [[]], [1]]` — the empty-list gauntlet.', '`[]` — HasNext must be false immediately.',
          'Calling `HasNext` three times in a row, then `Next` once.', '`[1, [2, [3, [4]]]]` — deep nesting.',
          'Calling `Next` when exhausted → a clear exception, not an empty value.'],
  code='''public sealed class NestedIterator : IEnumerator<int> {
    private readonly Stack<IEnumerator<NestedInteger>> _stack = new();
    private int? _peeked;                                  // buffer used by Peek and HasNext

    public NestedIterator(IList<NestedInteger> list) => _stack.Push(list.GetEnumerator());

    public bool HasNext() {
        if (_peeked.HasValue) return true;                 // idempotent: already buffered

        while (_stack.Count > 0) {
            var top = _stack.Peek();
            if (!top.MoveNext()) { _stack.Pop().Dispose(); continue; }   // exhausted level: drop it

            var item = top.Current;
            if (item.IsInteger()) { _peeked = item.GetInteger(); return true; }
            _stack.Push(item.GetList().GetEnumerator());   // descend; empty lists are skipped on the next loop
        }
        return false;
    }

    public int Next() {
        if (!HasNext()) throw new InvalidOperationException("iterator is exhausted");
        var value = _peeked!.Value;
        _peeked = null;                                    // consume the buffer
        return value;
    }

    public int Peek() {
        if (!HasNext()) throw new InvalidOperationException("iterator is exhausted");
        return _peeked!.Value;
    }

    public int Current => _peeked ?? throw new InvalidOperationException("call MoveNext first");
    object IEnumerator.Current => Current;
    public bool MoveNext() => HasNext() && Next() is var _ ;   // adapter for IEnumerator
    public void Reset() => throw new NotSupportedException("this iterator is forward-only");
    public void Dispose() { while (_stack.Count > 0) _stack.Pop().Dispose(); }
}''',
  traps=['Generated versions usually flatten into a `List<int>` in the constructor. That passes the tests and fails the follow-up '
         '("the input is a million elements and you only need the first ten") — reject it and say why.',
         'A `HasNext` that mutates state without buffering breaks when called twice. This is the defect to look for.',
         'Enumerators are `IDisposable`; generated code leaks them. Dispose as you pop.',
         'The empty-nested-list case is almost never in generated tests. Ask for it by name.'],
  follow=['Support `Remove()` semantics, or refuse it explicitly and say why.',
          'Make it work over a tree structure instead of nested lists.',
          'Now the iterator must be resumable across requests — what state would you persist?'],
  evalpts=['Did you keep it lazy?', 'Is HasNext idempotent, and did you test it twice in a row?',
           'Did you handle the empty-nested-list case?', 'Did you dispose enumerators?',
           'Did you refuse the eager rewrite the assistant offered?']),

 dict(id='topk', title='Top-K frequent items in a stream', topic='Heaps · Streaming', mins=30,
  problem='Given a stream of item ids, report the K most frequent at any time. Then: the stream is unbounded and you cannot keep '
          'every id.',
  clarify=['Exact or approximate?', 'Is K fixed, or asked per query?', 'Over all time, or a sliding window?',
           'How many distinct items — millions? Memory budget?', 'Ties: any order, or deterministic?'],
  plan='Two phases, and say both before prompting. Exact and bounded: a count map plus a size-K min-heap, O(n log k). Unbounded: '
       'you cannot store every count, so it becomes approximate — count-min sketch plus a heap, or space-saving (Misra-Gries) with '
       'a bounded counter table, and you state the error bound. Interviewers reward the second half; assistants jump straight to '
       'the first and stop.',
  prompts=['"C#: maintain top-K frequent items with a Dictionary count map and a size-K PriorityQueue min-heap. Show the update '
           'path only, and keep ties deterministic by id."',
           '"Now assume we cannot hold all counts. Compare count-min sketch and space-saving for this, with memory and error '
           'characteristics. No code yet."',
           '"Write a property-based test that compares the approximate top-K against an exact implementation on 100k synthetic '
           'events and reports the overlap."'],
  verify=['Fewer than K distinct items seen so far.', 'All items equally frequent (tie behaviour).',
          'An item that rises into the top-K after being outside it.', 'K = 1 and K = 0.',
          'Approximate mode: measure overlap against exact on a synthetic stream rather than asserting equality.'],
  code='''public sealed class TopKExact {
    private readonly int _k;
    private readonly Dictionary<string, long> _counts = new();

    public TopKExact(int k) {
        if (k <= 0) throw new ArgumentOutOfRangeException(nameof(k));
        _k = k;
    }

    public void Add(string id) => _counts[id] = _counts.GetValueOrDefault(id) + 1;

    /// <summary>O(n log k): the heap never grows past k, so memory is bounded by k, not by n.</summary>
    public IReadOnlyList<(string Id, long Count)> Top() {
        var heap = new PriorityQueue<(string Id, long Count), (long, string)>();
        foreach (var (id, count) in _counts) {
            heap.Enqueue((id, count), (count, id));              // deterministic tiebreak by id
            if (heap.Count > _k) heap.Dequeue();                 // drop the current smallest
        }
        var result = new List<(string, long)>(heap.Count);
        while (heap.Count > 0) result.Add(heap.Dequeue());
        result.Reverse();                                        // heap pops ascending
        return result;
    }
}

// Unbounded stream: bounded memory, approximate counts (space-saving / Misra-Gries).
public sealed class TopKApprox {
    private readonly int _capacity;                              // counters kept; error shrinks as this grows
    private readonly Dictionary<string, long> _counters = new();

    public TopKApprox(int capacity) => _capacity = capacity;

    public void Add(string id) {
        if (_counters.TryGetValue(id, out var c)) { _counters[id] = c + 1; return; }
        if (_counters.Count < _capacity) { _counters[id] = 1; return; }

        // evict the smallest counter and inherit its count: the classic space-saving step
        var min = _counters.MinBy(kv => kv.Value);
        _counters.Remove(min.Key);
        _counters[id] = min.Value + 1;                           // overestimate, bounded by min.Value
    }

    public IReadOnlyList<(string Id, long Count)> Top(int k) =>
        _counters.OrderByDescending(kv => kv.Value).ThenBy(kv => kv.Key)
                 .Take(k).Select(kv => (kv.Key, kv.Value)).ToList();
}''',
  traps=['Assistants sort the whole count map (O(n log n)) and call it top-K. Correct it to a size-K heap and say why.',
         'They use a max-heap of everything, which defeats the memory bound.',
         'C# `PriorityQueue` is a min-heap with no decrease-key — generated code often assumes otherwise.',
         'For the approximate version they will invent guarantees. Ask for the error bound explicitly, then sanity-check it.'],
  follow=['Sliding window of one hour instead of all time.',
          'Distributed: each node has its own stream — how do you merge top-K? (Merging approximate top-K is lossy; say so.)',
          'Now K is 10,000 — does your structure still make sense?'],
  evalpts=['Did you give exact and approximate, unprompted?',
           'Did you keep the heap bounded at K?',
           'Did you make ties deterministic?',
           'Did you test approximate mode statistically rather than by equality?']),

 dict(id='bounded', title='Thread-safe bounded blocking queue', topic='Concurrency', mins=35,
  problem='Implement a bounded queue with blocking `Put` (waits when full) and `Take` (waits when empty), plus a non-blocking '
          '`TryPut`/`TryTake`, safe for many producers and consumers.',
  clarify=['Blocking threads, or async (no thread blocked)?', 'Must FIFO order be strict?',
           'Is there a shutdown/complete signal, and what happens to waiters?', 'Do we need cancellation?',
           'Fairness between producers — is starvation acceptable?'],
  plan='Decide the mechanism before prompting: `Monitor` with `Wait`/`PulseAll` for a blocking version, or two `SemaphoreSlim`s '
       '(free slots and available items) for an async version. Name the failure you are guarding against — lost wakeups and '
       'spurious wakeups — and say that every wait must be inside a `while`, never an `if`. In C#, note you cannot `await` inside '
       'a `lock`, which is precisely why the async version needs semaphores.',
  prompts=['"C#: bounded blocking queue using Monitor.Wait/PulseAll with a capacity limit. Include TryPut and TryTake with '
           'timeouts, and CompleteAdding semantics."',
           '"Write a stress test: 4 producers, 4 consumers, 100k items, asserting no item is lost or duplicated and the queue '
           'never exceeds capacity."',
           '"Explain what breaks if I use Pulse instead of PulseAll here." (Then check the answer against your own reasoning.)'],
  verify=['Capacity 1 with one producer and one consumer.',
          'Consumers waiting when empty, producer arrives — exactly one consumer wakes with the item.',
          'Producers waiting when full, consumer takes — space is granted once, not twice.',
          'Shutdown while consumers are blocked — they must return, not hang.',
          'Stress test asserting no loss and no duplication, run repeatedly.'],
  code='''public sealed class BoundedQueue<T> {
    private readonly Queue<T> _items = new();
    private readonly int _capacity;
    private readonly object _gate = new();
    private bool _completed;

    public BoundedQueue(int capacity) {
        if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        _capacity = capacity;
    }

    public void Put(T item, CancellationToken ct = default) {
        lock (_gate) {
            while (_items.Count == _capacity) {            // while, never if: spurious and stolen wakeups
                ct.ThrowIfCancellationRequested();
                if (_completed) throw new InvalidOperationException("queue completed");
                Monitor.Wait(_gate);
            }
            if (_completed) throw new InvalidOperationException("queue completed");
            _items.Enqueue(item);
            Monitor.PulseAll(_gate);                       // PulseAll: producers and consumers share one monitor
        }
    }

    public bool TryTake(out T item, TimeSpan timeout, CancellationToken ct = default) {
        var deadline = DateTime.UtcNow + timeout;
        lock (_gate) {
            while (_items.Count == 0) {
                if (_completed) { item = default; return false; }      // drained and closed
                var left = deadline - DateTime.UtcNow;
                if (left <= TimeSpan.Zero) { item = default; return false; }
                ct.ThrowIfCancellationRequested();
                Monitor.Wait(_gate, left);
            }
            item = _items.Dequeue();
            Monitor.PulseAll(_gate);
            return true;
        }
    }

    public void CompleteAdding() {
        lock (_gate) { _completed = true; Monitor.PulseAll(_gate); }   // wake every waiter so nobody hangs
    }

    public int Count { get { lock (_gate) return _items.Count; } }
}''',
  traps=['`if` instead of `while` around `Monitor.Wait` — the defect that only shows under load. Assistants produce it often.',
         '`Pulse` instead of `PulseAll` when producers and consumers share one monitor: a consumer can wake a consumer and the '
         'producer sleeps forever.',
         'Forgetting to wake waiters on shutdown, so consumers hang at process exit.',
         'Suggesting `lock` around `await` for the async variant — it does not compile, and the fix is `SemaphoreSlim`.',
         'A `Count` property that reads without the lock (torn/stale reads).'],
  follow=['Write the async version with no thread blocked.',
          'Make it fair (FIFO among waiters) — what does that cost?',
          'Now it must support multiple priorities.',
          'Compare with `System.Threading.Channels` — when would you just use that?'],
  evalpts=['Did you name the lost/spurious wakeup problem before coding?',
           'Is every wait inside a while loop?',
           'Did you handle shutdown of blocked waiters?',
           'Did you run a stress test rather than a single-threaded test?',
           'Could you say why `Channels` might be the right production answer?']),

 dict(id='buildwaves', title='Dependency build order, AI-assisted', topic='Graphs · Topological sort', mins=30,
  problem='Given `GetDependencies(target)`, produce a build order. Then: report cycles usefully, and group the output into '
          'parallel waves.',
  clarify=['Can dependencies be discovered lazily, or is the full graph given?',
           'Are duplicate edges possible? Self-dependencies?', 'Should the order be deterministic across runs?',
           'How deep can the graph be? (Recursion risk.)'],
  plan='Kahn with in-degrees, discovered lazily from the requested targets. Decide before prompting: cycles are reported by '
       'naming the stuck nodes, and waves come free from the algorithm. This is a problem where the assistant will give you '
       'correct textbook code that fails your two follow-ups — so ask for the follow-ups first.',
  prompts=['"C#: Kahn topological sort, discovering the graph lazily via GetDependencies(target). Return List<List<string>> waves '
           'rather than a flat list, and throw naming the nodes involved in any cycle."',
           '"Show me the case where your in-degree calculation double counts duplicate edges, and write a test for it."',
           '"Make each wave deterministic, and tell me what that costs."'],
  verify=['A diamond (A→B, A→C, B→D, C→D): D must be in the last wave, once.',
          'A duplicate edge declared twice — in-degree must not double count.', 'A self-dependency.',
          'Two disconnected components — both must appear.', 'A chain of 10,000 nodes (no recursion).',
          'A cycle — the error must list the members.'],
  code='''public IReadOnlyList<IReadOnlyList<string>> BuildWaves(IEnumerable<string> targets) {
    var dependents = new Dictionary<string, HashSet<string>>();   // HashSet: duplicate edges cannot double count
    var indegree   = new Dictionary<string, int>();
    var seen       = new HashSet<string>();
    var pending    = new Stack<string>(targets);

    while (pending.Count > 0) {
        var node = pending.Pop();
        if (!seen.Add(node)) continue;
        indegree.TryAdd(node, 0);
        foreach (var dep in GetDependencies(node)) {
            if (dep == node) throw new InvalidOperationException($"self-dependency on '{node}'");
            if (!dependents.TryGetValue(dep, out var set)) dependents[dep] = set = new HashSet<string>();
            if (set.Add(node)) indegree[node] = indegree.GetValueOrDefault(node) + 1;   // only new edges count
            pending.Push(dep);
        }
    }

    var ready = indegree.Where(kv => kv.Value == 0).Select(kv => kv.Key).OrderBy(x => x, StringComparer.Ordinal).ToList();
    var waves = new List<IReadOnlyList<string>>();
    int emitted = 0;

    while (ready.Count > 0) {
        waves.Add(ready);
        emitted += ready.Count;
        var next = new List<string>();
        foreach (var done in ready)
            foreach (var dependent in dependents.GetValueOrDefault(done, new HashSet<string>()))
                if (--indegree[dependent] == 0) next.Add(dependent);
        next.Sort(StringComparer.Ordinal);                        // determinism, cheap at this size
        ready = next;
    }

    if (emitted != indegree.Count)
        throw new InvalidOperationException("cycle involves: " +
            string.Join(", ", indegree.Where(kv => kv.Value > 0).Select(kv => kv.Key).OrderBy(x => x, StringComparer.Ordinal)));

    return waves;
}''',
  traps=['Textbook answers use `List<string>` for adjacency, so a duplicate edge inflates in-degree and the node never becomes '
         'ready — a hang that looks like a cycle. This is the single most valuable bug to catch here.',
         'Recursive DFS variants blow the stack on deep chains.',
         'Assistants return `false` or an empty list on a cycle instead of naming the members.',
         'Non-deterministic dictionary iteration makes output order vary between runs — bad for build systems and for tests.'],
  follow=['Cap parallelism at N workers per wave.',
          'One dependency changed — what is the minimal rebuild set?',
          'Make it incremental across runs with a cache.',
          'Now dependencies come from a remote service that can fail — what changes?'],
  evalpts=['Did you get edge direction right first time?',
           'Did you catch the duplicate-edge in-degree bug?',
           'Did you name cycle members?',
           'Did you produce waves and determinism without being asked twice?']),

 dict(id='mergek', title='Merge K sorted streams with a bounded memory budget', topic='Heaps · Streams', mins=30,
  problem='Merge K sorted sources into one sorted output. The sources are streams (you cannot load them), K can be 10,000, and '
          'memory is bounded.',
  clarify=['Are the sources in memory, files, or network streams?', 'Can K exceed what one machine can hold open?',
           'Duplicates: keep all, or deduplicate?', 'Is the output consumed lazily, or written to a file?',
           'Is stability required (equal keys keep source order)?'],
  plan='A K-way merge with a min-heap of one cursor per source: memory is O(K), not O(total). If K is enormous, merge in rounds '
       '(a merge tree) so you never hold 10,000 open handles. Decide the tie rule up front, because "stable by source index" is a '
       'requirement the assistant will not invent for you.',
  prompts=['"C#: K-way merge over IAsyncEnumerable<T> sources using a PriorityQueue holding one element per source. Yield lazily, '
           'keep memory O(K), and break ties by source index for stability."',
           '"Now assume K = 10,000 and we can only hold 100 sources open. Sketch the merge-tree approach — no code."',
           '"What happens in your code when one source throws halfway through? Show me, do not fix."'],
  verify=['One empty source among several.', 'All sources empty.', 'K = 1.',
          'Equal keys across sources (stability).', 'One source much longer than the others.',
          'A source that throws mid-stream — is the partial output consistent, and are the rest disposed?'],
  code='''public static async IAsyncEnumerable<T> MergeAsync<T>(
        IReadOnlyList<IAsyncEnumerator<T>> sources,
        IComparer<T> comparer,
        [EnumeratorCancellation] CancellationToken ct = default) {

    // (value, sourceIndex) with the index as the tiebreak: stable across equal keys
    var heap = new PriorityQueue<(T Value, int Source), (T, int)>(
        Comparer<(T, int)>.Create((a, b) => {
            int c = comparer.Compare(a.Item1, b.Item1);
            return c != 0 ? c : a.Item2.CompareTo(b.Item2);
        }));

    try {
        for (int i = 0; i < sources.Count; i++)                    // prime: one element per source, O(K) memory
            if (await sources[i].MoveNextAsync()) heap.Enqueue((sources[i].Current, i), (sources[i].Current, i));

        while (heap.Count > 0) {
            ct.ThrowIfCancellationRequested();
            var (value, source) = heap.Dequeue();
            yield return value;
            if (await sources[source].MoveNextAsync()) {            // refill only the source we drained
                var next = sources[source].Current;
                heap.Enqueue((next, source), (next, source));
            }
        }
    }
    finally {
        foreach (var s in sources) await s.DisposeAsync();          // every source, even on failure
    }
}''',
  traps=['Generated code materialises the sources into lists — which is the one thing the problem forbids. Reject it immediately.',
         'Tie handling is usually undefined, so equal keys come out in heap order and the merge is unstable.',
         'Sources are often not disposed on the failure path.',
         'With K = 10,000 the assistant will keep suggesting a bigger heap rather than a merge tree — hold your ground.'],
  follow=['Deduplicate equal keys, keeping the first source.',
          'Merge 10,000 sources with only 100 open handles.',
          'Parallelise the merge — where does the ordering guarantee break?',
          'Back-pressure: the consumer is slower than the producers.'],
  evalpts=['Did you keep memory O(K) and prove it?',
           'Did you define the tie rule before coding?',
           'Did you dispose sources in a finally?',
           'Did you handle the K-too-large case with a different algorithm, not a bigger heap?']),
]
