// A04 — "Implement an LRU cache. Later, add a validation method for keys." Reported on LeetCode
// Discuss (supplied by the reader, Oct 2026); the same phrase appears in the earlier research.
// The statement is ambiguous, so clarify first. The reading implemented here: reject invalid
// keys at the boundary, with a reason, using a rule the caller supplies. It is added by
// COMPOSITION — the LRU itself does not change, which is the extensibility the round rewards,
// and it stops "add another feature" from turning into a rewrite.

public sealed class ValidatedLruCache<TKey, TValue> {
    private readonly LruCache<TKey, TValue> _inner;
    private readonly Func<TKey, string> _why;            // null = valid, otherwise the reason

    public ValidatedLruCache(int capacity, Func<TKey, string> rule) {
        _inner = new LruCache<TKey, TValue>(capacity);
        _why = rule ?? throw new ArgumentNullException(nameof(rule));
    }

    public string Validate(TKey key) => _why(key);        // the "validation method", usable on its own

    public void Put(TKey key, TValue value) {
        var reason = _why(key);
        if (reason != null) throw new ArgumentException($"invalid key: {reason}", nameof(key));
        _inner.Put(key, value);
    }

    // An invalid key can never have been stored, so a lookup is simply a miss — reads do not throw.
    public bool TryGet(TKey key, out TValue value) {
        if (_why(key) != null) { value = default; return false; }
        return _inner.TryGet(key, out value);
    }

    public int Count => _inner.Count;
}

public static class KeyRules {
    // A sensible default for string keys. State each rule and why; do not invent more.
    public static string Strings(string k) =>
        k is null ? "null" :
        k.Length == 0 ? "empty" :
        k.Length > 256 ? "longer than 256 characters" :
        k.Any(char.IsControl) ? "contains control characters" :
        null;
}
