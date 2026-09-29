// Q17 — merge two metadata trees keyed by child key, summing values.
public class MetaNode {
    public string Key;
    public long   Value;                       // this node plus the sum of its children
    public Dictionary<string, MetaNode> Children = new(StringComparer.Ordinal);

    public MetaNode(string key, long value) { Key = key; Value = value; }
}

public static class MetaTreeMerge {

    /// Pure merge: builds a new tree and mutates neither input.
    /// That is what makes Merge(x, x) safe, and what makes concurrent readers safe.
    public static MetaNode Merge(MetaNode s, MetaNode t) {
        if (s == null) return Clone(t);
        if (t == null) return Clone(s);
        if (!string.Equals(s.Key, t.Key, StringComparison.Ordinal))
            throw new ArgumentException($"Root keys differ: '{s.Key}' vs '{t.Key}'.");

        // Summing at every node preserves the invariant for free: if value = own + children on
        // both sides, then the sums also satisfy value = own + children. Nothing to recompute.
        var merged = new MetaNode(s.Key, s.Value + t.Value);

        foreach (var kv in s.Children) {
            merged.Children[kv.Key] = t.Children.TryGetValue(kv.Key, out var other)
                ? Merge(kv.Value, other)         // present in both: recurse
                : Clone(kv.Value);               // only in s: whole branch carried over
        }

        foreach (var kv in t.Children)
            if (!merged.Children.ContainsKey(kv.Key))
                merged.Children[kv.Key] = Clone(kv.Value);   // only in t: branch created

        return merged;
    }

    public static MetaNode Clone(MetaNode n) {
        if (n == null) return null;
        var copy = new MetaNode(n.Key, n.Value);
        foreach (var kv in n.Children) copy.Children[kv.Key] = Clone(kv.Value);
        return copy;
    }

    /// In-place variant: cheaper, and dangerous. Kept here to name the trap rather than hide it.
    /// MergeInto(x, x) double-counts and can enumerate a dictionary it is writing to.
    public static void MergeInto(MetaNode target, MetaNode source) {
        if (target == null || source == null) return;
        if (ReferenceEquals(target, source))
            throw new InvalidOperationException("Self-merge in place would double-count.");

        target.Value += source.Value;

        foreach (var kv in source.Children) {
            if (target.Children.TryGetValue(kv.Key, out var child)) MergeInto(child, kv.Value);
            else target.Children[kv.Key] = Clone(kv.Value);
        }
    }

    /// Iterative merge for trees deep enough to overflow the stack — the 1 GB follow-up.
    public static MetaNode MergeIterative(MetaNode s, MetaNode t) {
        if (s == null) return Clone(t);
        if (t == null) return Clone(s);

        var root = new MetaNode(s.Key, s.Value + t.Value);
        var work = new Stack<(MetaNode S, MetaNode T, MetaNode Out)>();
        work.Push((s, t, root));

        while (work.Count > 0) {
            var (a, b, into) = work.Pop();

            foreach (var kv in a.Children) {
                if (b.Children.TryGetValue(kv.Key, out var other)) {
                    var child = new MetaNode(kv.Key, kv.Value.Value + other.Value);
                    into.Children[kv.Key] = child;
                    work.Push((kv.Value, other, child));
                } else {
                    into.Children[kv.Key] = Clone(kv.Value);
                }
            }
            foreach (var kv in b.Children)
                if (!into.Children.ContainsKey(kv.Key)) into.Children[kv.Key] = Clone(kv.Value);
        }
        return root;
    }

    /// The stated invariant, checkable. Worth writing: it is the assertion a reviewer asks for.
    public static bool IsConsistent(MetaNode n, out string offender) {
        offender = null;
        if (n == null) return true;

        long childSum = 0;
        foreach (var kv in n.Children) {
            if (!IsConsistent(kv.Value, out offender)) return false;
            childSum += kv.Value.Value;
        }
        if (n.Value < childSum) { offender = n.Key; return false; }   // own contribution cannot be negative
        return true;
    }

    public static long OwnValue(MetaNode n) {
        long childSum = 0;
        foreach (var kv in n.Children) childSum += kv.Value.Value;
        return n.Value - childSum;
    }
}

// Follow-up — "side-heavy" form: left child / right sibling. Every n-ary node becomes a binary
// node whose Left is its first child and whose Right is its next sibling. The tree leans right
// exactly as far as the widest sibling list, which is why it is worth naming the cost.
public class BinaryMetaNode {
    public string Key;
    public long   Value;
    public BinaryMetaNode Left, Right;        // Left = first child, Right = next sibling
    public BinaryMetaNode(string key, long value) { Key = key; Value = value; }
}

public static class SideHeavy {

    public static BinaryMetaNode Encode(MetaNode n) {
        if (n == null) return null;

        var node = new BinaryMetaNode(n.Key, n.Value);
        BinaryMetaNode prev = null;

        // Deterministic order: the source dictionary has none, and a serialised tree needs one.
        foreach (var kv in n.Children.OrderBy(k => k.Key, StringComparer.Ordinal)) {
            var child = Encode(kv.Value);
            if (prev == null) node.Left = child;
            else prev.Right = child;
            prev = child;
        }
        return node;
    }

    public static MetaNode Decode(BinaryMetaNode b) {
        if (b == null) return null;

        var node = new MetaNode(b.Key, b.Value);

        // Walk the sibling chain at this level; Decode(child) handles that child's own subtree.
        for (BinaryMetaNode child = b.Left; child != null; child = child.Right)
            node.Children[child.Key] = Decode(child);

        return node;
    }
}
