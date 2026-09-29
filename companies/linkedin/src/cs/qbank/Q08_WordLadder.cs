// Q8 — minimum single-character transformations from start to end, every step a dictionary word.
public class WordTransformer {

    private readonly Dictionary<string, List<string>> _buckets;   // "*PE" -> words matching it
    private readonly HashSet<string> _words;

    // Preprocessing once, so each query is pure BFS with O(1) neighbour lookup.
    public WordTransformer(IEnumerable<string> dictionary) {
        _words   = new HashSet<string>(dictionary, StringComparer.Ordinal);
        _buckets = new Dictionary<string, List<string>>(StringComparer.Ordinal);
        foreach (string w in _words) Index(w);
    }

    private void Index(string word) {
        var chars = word.ToCharArray();
        for (int i = 0; i < chars.Length; i++) {
            char keep = chars[i];
            chars[i] = '*';
            string pattern = new string(chars);
            if (!_buckets.TryGetValue(pattern, out var list)) _buckets[pattern] = list = new List<string>();
            list.Add(word);
            chars[i] = keep;
        }
    }

    // Returns the number of TRANSFORMATIONS (edges), not the number of words. -1 if impossible.
    public int MinTransformations(string start, string end) {
        if (start == null || end == null || start.Length != end.Length) return -1;
        if (start == end) return 0;
        if (!_words.Contains(end)) return -1;

        var seen  = new HashSet<string>(StringComparer.Ordinal) { start };
        var queue = new Queue<string>();
        queue.Enqueue(start);
        int steps = 0;

        while (queue.Count > 0) {
            int levelSize = queue.Count;
            steps++;

            for (int i = 0; i < levelSize; i++) {
                string cur = queue.Dequeue();

                foreach (string next in Neighbours(cur)) {
                    if (next == end) return steps;
                    if (seen.Add(next)) queue.Enqueue(next);
                }
            }
        }
        return -1;
    }

    private IEnumerable<string> Neighbours(string word) {
        var chars = word.ToCharArray();
        for (int i = 0; i < chars.Length; i++) {
            char keep = chars[i];
            chars[i] = '*';
            if (_buckets.TryGetValue(new string(chars), out var list))
                foreach (string w in list) if (w != word) yield return w;
            chars[i] = keep;
        }
    }

    // Follow-up — bidirectional BFS. Same answer, far fewer nodes touched: two searches of
    // depth d/2 instead of one of depth d, so b^(d/2) + b^(d/2) instead of b^d.
    public int MinTransformationsBidirectional(string start, string end) {
        if (start == null || end == null || start.Length != end.Length) return -1;
        if (start == end) return 0;
        if (!_words.Contains(end)) return -1;

        var frontA = new HashSet<string>(StringComparer.Ordinal) { start };
        var frontB = new HashSet<string>(StringComparer.Ordinal) { end };
        var seenA  = new HashSet<string>(StringComparer.Ordinal) { start };
        var seenB  = new HashSet<string>(StringComparer.Ordinal) { end };
        int steps = 0;

        while (frontA.Count > 0 && frontB.Count > 0) {
            if (frontA.Count > frontB.Count) {        // always expand the smaller frontier
                (frontA, frontB) = (frontB, frontA);
                (seenA,  seenB)  = (seenB,  seenA);
            }

            var next = new HashSet<string>(StringComparer.Ordinal);
            steps++;

            foreach (string cur in frontA)
                foreach (string nb in Neighbours(cur)) {
                    if (seenB.Contains(nb)) return steps;
                    if (seenA.Add(nb)) next.Add(nb);
                }

            frontA = next;
        }
        return -1;
    }

    // Follow-up — the dictionary changes while the service is running.
    public void AddWord(string word) {
        if (_words.Add(word)) Index(word);
    }
}
