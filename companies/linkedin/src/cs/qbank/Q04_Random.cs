// Q4 — a uniform integer in [0,6] built from a biased coin.
public class UniformFromBiased {

    private readonly Func<int> _biased;    // returns 0 with probability p, 1 with probability 1-p
    public long BiasedCalls { get; private set; }

    public UniformFromBiased(Func<int> biasedBit) { _biased = biasedBit; }

    // Von Neumann debiasing. Draw two bits:
    //   "01" has probability p(1-p);  "10" has probability (1-p)p.  Identical, whatever p is.
    //   "00" and "11" carry the bias, so throw the pair away and draw again.
    public int FairBit() {
        while (true) {
            int a = _biased(); int b = _biased();
            BiasedCalls += 2;
            if (a != b) return a;
        }
    }

    // Three fair bits give 0..7 uniformly. 7 values are wanted, so reject 7 and redraw.
    // Rejecting is what keeps it uniform: rescaling 8 outcomes onto 7 cannot be.
    public int Next0To6() {
        while (true) {
            int v = (FairBit() << 2) | (FairBit() << 1) | FairBit();
            if (v <= 6) return v;
        }
    }
}
