// Q12 — Insert, Remove and RemoveRandom, all expected O(1).
public class RandomBag {

    private readonly List<int> _items = new();                 // the values, in no meaningful order
    private readonly Dictionary<int, int> _indexOf = new();     // value -> its slot in _items
    private readonly Random _rng;

    public RandomBag(int? seed = null) { _rng = seed.HasValue ? new Random(seed.Value) : new Random(); }

    public int Count => _items.Count;

    public bool Insert(int value) {
        if (_indexOf.ContainsKey(value)) return false;
        _indexOf[value] = _items.Count;
        _items.Add(value);
        return true;
    }

    // The whole technique: never shift the list. Move the LAST element into the hole.
    public bool Remove(int value) {
        if (!_indexOf.TryGetValue(value, out int slot)) return false;

        int last = _items[^1];
        _items[slot] = last;
        _indexOf[last] = slot;          // must run BEFORE the removal below, for slot == last index

        _items.RemoveAt(_items.Count - 1);
        _indexOf.Remove(value);
        return true;
    }

    public int RemoveRandomElement() {
        if (_items.Count == 0) throw new InvalidOperationException("Empty.");

        int slot  = _rng.Next(_items.Count);   // uniform only because the list is gap-free
        int value = _items[slot];
        Remove(value);
        return value;
    }

    public int PeekRandom() {
        if (_items.Count == 0) throw new InvalidOperationException("Empty.");
        return _items[_rng.Next(_items.Count)];
    }
}

// Follow-up — duplicates allowed. The value now maps to a SET of slots, and any one of them
// may be evicted. Random selection stays uniform over occurrences, not over distinct values.
public class RandomMultiBag {

    private readonly List<int> _items = new();
    private readonly Dictionary<int, HashSet<int>> _slots = new();
    private readonly Random _rng;

    public RandomMultiBag(int? seed = null) { _rng = seed.HasValue ? new Random(seed.Value) : new Random(); }

    public int Count => _items.Count;

    public bool Insert(int value) {
        if (!_slots.TryGetValue(value, out var set)) _slots[value] = set = new HashSet<int>();
        bool firstCopy = set.Count == 0;
        set.Add(_items.Count);
        _items.Add(value);
        return firstCopy;
    }

    public bool Remove(int value) {
        if (!_slots.TryGetValue(value, out var set) || set.Count == 0) return false;

        int slot     = set.First();
        int lastSlot = _items.Count - 1;
        int last     = _items[lastSlot];

        set.Remove(slot);

        if (slot != lastSlot) {
            _items[slot] = last;
            _slots[last].Remove(lastSlot);
            _slots[last].Add(slot);
        }
        _items.RemoveAt(lastSlot);
        if (set.Count == 0) _slots.Remove(value);
        return true;
    }

    public int RemoveRandomElement() {
        if (_items.Count == 0) throw new InvalidOperationException("Empty.");
        int value = _items[_rng.Next(_items.Count)];
        Remove(value);
        return value;
    }
}
