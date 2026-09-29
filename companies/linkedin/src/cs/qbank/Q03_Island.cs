// Q3 — artificial island: longest run of land after converting at most `material` ocean cells.
public static class ArtificialIsland {

    public static int MaxIsland(int[] cells, int material) {
        if (cells == null || cells.Length == 0) return 0;

        int best = 0, ocean = 0, left = 0;

        for (int right = 0; right < cells.Length; right++) {
            if (cells[right] == 0) ocean++;

            while (ocean > material) {          // window became unaffordable: shrink from the left
                if (cells[left] == 0) ocean--;
                left++;
            }
            best = Math.Max(best, right - left + 1);
        }
        return best;
    }

    // Follow-up 1 — the array wraps. Walk two copies, but never let the window exceed n.
    public static int MaxIslandCircular(int[] cells, int material) {
        if (cells == null || cells.Length == 0) return 0;
        int n = cells.Length;

        int totalOcean = 0;
        foreach (int c in cells) if (c == 0) totalOcean++;
        if (totalOcean <= material) return n;   // the whole ring is affordable; guard the wrap-around

        int best = 0, ocean = 0, left = 0;
        for (int right = 0; right < 2 * n; right++) {
            if (cells[right % n] == 0) ocean++;

            while (ocean > material || right - left + 1 > n) {
                if (cells[left % n] == 0) ocean--;
                left++;
            }
            best = Math.Max(best, right - left + 1);
        }
        return best;
    }

    // Follow-up 2 — -1 is an obstacle: it is never land and can never be converted.
    // So no window may contain one. The array becomes independent segments.
    public static int MaxIslandWithObstacles(int[] cells, int material) {
        if (cells == null || cells.Length == 0) return 0;

        int best = 0, ocean = 0, left = 0;
        for (int right = 0; right < cells.Length; right++) {
            if (cells[right] == -1) {           // hard wall: restart the window past it
                left = right + 1;
                ocean = 0;
                continue;
            }
            if (cells[right] == 0) ocean++;
            while (ocean > material) {
                if (cells[left] == 0) ocean--;
                left++;
            }
            best = Math.Max(best, right - left + 1);
        }
        return best;
    }

    // Follow-up 3 — each ocean cell has its own conversion cost. Costs are non-negative,
    // so the window sum is still monotonic and the same two pointers work.
    public static int MaxIslandWeighted(int[] cells, int[] cost, int budget) {
        if (cells == null || cells.Length == 0) return 0;

        int best = 0, left = 0;
        long spent = 0;

        for (int right = 0; right < cells.Length; right++) {
            if (cells[right] == 0) spent += cost[right];

            while (spent > budget) {
                if (cells[left] == 0) spent -= cost[left];
                left++;
            }
            best = Math.Max(best, right - left + 1);
        }
        return best;
    }
}
