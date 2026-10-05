// G01 — rejection sampling. Reported for LinkedIn's AI coding round (LeetCode Discuss,
// SWE-ML, read via search summary — the page blocks fetching): a problem "very similar to
// rand7() → rand10()", with the expectation to explain it mathematically before coding.

public static class Sampling {
    // Two rand7 calls give 49 equally likely outcomes. 40 of them split evenly into 10 groups
    // of 4; the other 9 are rejected and we draw again. Accept probability 40/49, so the
    // expected number of rand7 calls is 2 × 49/40 ≈ 2.45.
    public static int Rand10(Func<int> rand7) {
        while (true) {
            int a = rand7(), b = rand7();                // each uniform in 1..7
            int idx = (a - 1) * 7 + (b - 1);             // uniform in 0..48
            if (idx < 40) return idx % 10 + 1;           // 0..39 → 1..10, four outcomes each
        }
    }

    // The general form: uniform in [0, n) from any uniform source in [0, m). Builds a base-m
    // number until its range is at least n, then rejects the tail that would cause bias.
    public static int UniformBelow(int n, int m, Func<int> source) {
        if (n <= 0 || m < 2) throw new ArgumentOutOfRangeException();
        while (true) {
            long range = 1, value = 0;
            while (range < n) { value = value * m + source(); range *= m; }
            long limit = range - range % n;              // largest multiple of n that fits
            if (value < limit) return (int)(value % n);
        }
    }
}

// Q4 in the question bank is the inverse problem — fair output from a BIASED source.
// Von Neumann: flip twice; HT → 0, TH → 1, HH/TT → discard. Both orders have probability p(1-p).
public static class FairCoin {
    public static int Flip(Func<int> biased) {
        while (true) {
            int a = biased(), b = biased();
            if (a != b) return a;
        }
    }
}
