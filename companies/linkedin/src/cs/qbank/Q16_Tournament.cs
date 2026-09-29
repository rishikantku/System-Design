// Q16 — second smallest value in a tournament tree (each parent holds the min of its children).
public static class TournamentTree {

    public static int SecondSmallest(TreeNode root) {
        if (root == null) throw new ArgumentNullException(nameof(root));
        if (root.Left == null && root.Right == null)
            throw new InvalidOperationException("A single leaf has no second smallest.");

        int best = int.MaxValue;
        TreeNode cur = root;

        // Walk the winner's path from the root to its leaf. Every node it beat on the way is a
        // candidate, and nothing else can be: any other value lost to something that lost to
        // the minimum, so it is at least the third smallest.
        while (cur.Left != null || cur.Right != null) {
            TreeNode winner, loser;

            if (cur.Left != null && cur.Left.Value == cur.Value) { winner = cur.Left;  loser = cur.Right; }
            else                                                 { winner = cur.Right; loser = cur.Left;  }

            if (loser != null) best = Math.Min(best, loser.Value);
            cur = winner;
        }
        return best;
    }
}
