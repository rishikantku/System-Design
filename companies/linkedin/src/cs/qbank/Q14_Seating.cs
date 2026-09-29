// Q14 — how many more people can sit, with nobody next to anybody.
public static class TheatreSeating {

    public static int MaxAdditional(int[] seats) {
        if (seats == null || seats.Length == 0) return 0;

        var row = (int[])seats.Clone();     // never mutate the caller's array
        int placed = 0;

        for (int i = 0; i < row.Length; i++) {
            if (row[i] != 0) continue;

            bool leftFree  = i == 0               || row[i - 1] == 0;
            bool rightFree = i == row.Length - 1  || row[i + 1] == 0;

            if (leftFree && rightFree) {
                row[i] = 1;                 // seat taken; the scan sees it when checking i+1
                placed++;
            }
        }
        return placed;
    }

    public static bool CanSeat(int[] seats, int n) {
        if (n <= 0) return true;
        return MaxAdditional(seats) >= n;
    }

    // Constant space: the only history needed is the index of the last occupied seat.
    public static int MaxAdditionalNoCopy(int[] seats) {
        if (seats == null || seats.Length == 0) return 0;

        int placed = 0, lastTaken = -2;     // -2 so index 0 has no left neighbour

        for (int i = 0; i < seats.Length; i++) {
            if (seats[i] == 1) { lastTaken = i; continue; }

            bool leftFree  = lastTaken < i - 1;
            bool rightFree = i == seats.Length - 1 || seats[i + 1] == 0;

            if (leftFree && rightFree) { placed++; lastTaken = i; }
        }
        return placed;
    }
}
