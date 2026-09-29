// Q11 — which known words does a phone number spell?
public class KeypadDictionary {

    private static readonly string[] Groups = {
        "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"   // digits 2..9
    };

    private static readonly int[] DigitOf = BuildDigitTable();

    private static int[] BuildDigitTable() {
        var table = new int[26];
        for (int g = 0; g < Groups.Length; g++)
            foreach (char c in Groups[g]) table[c - 'a'] = g + 2;
        return table;
    }

    // Signature -> every word that types to it. Many words share one signature, which is why
    // the value is a list: "linkedin" and "linkedgo" both come out as 54653346.
    private readonly Dictionary<string, List<string>> _bySignature = new(StringComparer.Ordinal);

    public KeypadDictionary(IEnumerable<string> words) {
        foreach (string w in words) {
            string sig = Signature(w);
            if (sig == null) continue;                     // not typable on a keypad
            if (!_bySignature.TryGetValue(sig, out var list)) _bySignature[sig] = list = new List<string>();
            list.Add(w);
        }
    }

    public static string Signature(string word) {
        var sb = new System.Text.StringBuilder(word.Length);
        foreach (char raw in word) {
            char c = char.ToLowerInvariant(raw);
            if (c < 'a' || c > 'z') return null;
            sb.Append((char)('0' + DigitOf[c - 'a']));
        }
        return sb.ToString();
    }

    // The lookup the question asks for: exact-length match, O(L) for the hash of the number.
    public List<string> WordsFor(string number) {
        if (string.IsNullOrEmpty(number)) return new List<string>();
        return _bySignature.TryGetValue(number, out var hits)
            ? new List<string>(hits)
            : new List<string>();
    }
}

// Follow-up — a trie over digits, which the hash map cannot do: prefix search as the
// user is still typing, which is the actual LinkedIn-app use for this.
public class KeypadTrie {

    private sealed class Node {
        public readonly Node[] Next = new Node[10];
        public List<string> Words;                         // words ENDING here
    }

    private readonly Node _root = new();

    public void Add(string word) {
        string sig = KeypadDictionary.Signature(word);
        if (sig == null) return;

        Node cur = _root;
        foreach (char d in sig) {
            int i = d - '0';
            cur = cur.Next[i] ??= new Node();
        }
        (cur.Words ??= new List<string>()).Add(word);
    }

    public List<string> Exact(string number) {
        Node cur = Walk(number);
        return cur?.Words is null ? new List<string>() : new List<string>(cur.Words);
    }

    // Everything the number could still become — the autocomplete answer.
    public List<string> WithPrefix(string number) {
        var found = new List<string>();
        Node cur = Walk(number);
        if (cur != null) Collect(cur, found);
        return found;
    }

    private Node Walk(string number) {
        Node cur = _root;
        foreach (char d in number) {
            if (d < '2' || d > '9') return null;
            cur = cur.Next[d - '0'];
            if (cur == null) return null;
        }
        return cur;
    }

    private static void Collect(Node node, List<string> into) {
        if (node.Words != null) into.AddRange(node.Words);
        foreach (Node child in node.Next) if (child != null) Collect(child, into);
    }
}
