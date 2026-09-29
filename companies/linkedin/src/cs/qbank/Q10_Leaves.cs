// Q10 — print the leaves, remove them, repeat until only the root is left.
public class TreeNode {
    public int Value;
    public TreeNode Left, Right;
    public TreeNode(int value) { Value = value; }
}

public static class LeafPeeling {

    // No mutation at all. A node's peel round is 1 + max(round of its children), which is
    // exactly its height measured from the bottom. One post-order pass buckets every node.
    public static List<List<int>> PeelLevels(TreeNode root) {
        var levels = new List<List<int>>();
        Height(root, levels);
        return levels;
    }

    private static int Height(TreeNode node, List<List<int>> levels) {
        if (node == null) return -1;                       // so a leaf comes out as 0

        int h = 1 + Math.Max(Height(node.Left, levels), Height(node.Right, levels));

        if (h == levels.Count) levels.Add(new List<int>());  // first node seen at this depth
        levels[h].Add(node.Value);
        return h;
    }

    // If the interviewer genuinely wants the tree destroyed, do it explicitly: one pass per
    // round, cutting the child links whose subtree was a leaf. O(n) per round, O(n·h) overall.
    public static List<List<int>> PeelAndMutate(ref TreeNode root) {
        var rounds = new List<List<int>>();

        while (root != null) {
            var picked = new List<int>();
            root = Strip(root, picked);
            rounds.Add(picked);
        }
        return rounds;
    }

    private static TreeNode Strip(TreeNode node, List<int> picked) {
        if (node == null) return null;

        if (node.Left == null && node.Right == null) {
            picked.Add(node.Value);
            return null;                                   // the parent's link is cut here
        }
        node.Left  = Strip(node.Left,  picked);
        node.Right = Strip(node.Right, picked);
        return node;
    }
}

// Follow-up — N-ary. The recurrence does not change at all; only the fan-out does.
public class NaryNode {
    public int Value;
    public List<NaryNode> Children = new();
    public NaryNode(int value) { Value = value; }
}

public static class NaryLeafPeeling {

    public static List<List<int>> PeelLevels(NaryNode root) {
        var levels = new List<List<int>>();
        Height(root, levels);
        return levels;
    }

    private static int Height(NaryNode node, List<List<int>> levels) {
        if (node == null) return -1;

        int h = -1;
        foreach (NaryNode child in node.Children) h = Math.Max(h, Height(child, levels));
        h += 1;

        if (h == levels.Count) levels.Add(new List<int>());
        levels[h].Add(node.Value);
        return h;
    }
}
