# -*- coding: utf-8 -*-
"""Chapter 6, Lesson 2 — the booths / experience-factor problem."""
from lib import *

lesson_header('6.2', 'The booths problem — maximise the experience factor', 'Prefix products · range queries',
              'High', 'Your own list, first-hand', '2026', 'High', 17,
              """Chapter six, lesson two, and this one is from your own list, so it is first-hand evidence rather than a """
              """scraped tag. The wording you recorded is: booths and groups, maximise the experience factor, where the """
              """factor over a range is the number of drones multiplied by the number of robots. And I am going to teach """
              """this one differently from every other lesson in the course, because the honest first observation is that """
              """the question as stated is ambiguous — and how you handle that ambiguity is the interview.""")

sid = beat('Question', 'The problem, as you recorded it',
           '<div class="qwrap"><div class="qtext" style="font-size:34px;line-height:1.4">'
           'There is a row of booths. Each booth contains some <b>drones</b> and some <b>robots</b>.<br><br>'
           'The <b>experience factor</b> of a range of booths is<br>'
           '<b>(total drones in the range) &times; (total robots in the range)</b>.<br><br>'
           'Maximise the experience factor.</div></div>',
           """Here is the question as recorded. A row of booths, each containing some drones and some robots. The """
           """experience factor of a range of booths is the total drones in that range multiplied by the total robots in """
           """that range. Maximise the experience factor.""")

sid = beat('Read it again', 'Three different questions are hiding in that sentence',
           '<div style="font-size:31px;line-height:1.7">'
           '<b>1. Ranges are given to you.</b> Many queries arrive; answer each fast. &rarr; a <b>prefix-sum</b> problem.'
           '<br><br>'
           '<b>2. You choose the range.</b> Find the contiguous range with the largest factor. &rarr; a <b>search</b> '
           'problem, and the objective is <i>not</i> monotone.<br><br>'
           '<b>3. You choose any subset</b>, not necessarily contiguous. &rarr; then the answer is trivially '
           '<b>everything</b>, since counts are non-negative &mdash; which is a strong hint that this reading is wrong.'
           '</div>',
           """Read it again, because three different questions are hiding in that one sentence, and they have three """
           """different answers.""", step=0)
seg(sid, 1, """Reading one: the ranges are given to you, many queries arrive, and you answer each one fast. That is a prefix """
            """sum problem, and it is easy once you see it.""")
seg(sid, 2, """Reading two: you choose the range, and you want the contiguous range with the largest factor. That is a """
            """search problem, and — this is the part that matters — the objective is not monotone, which kills the """
            """obvious techniques.""")
seg(sid, 3, """Reading three: you choose any subset, not necessarily contiguous. Then the answer is trivially everything, """
            """because counts are non-negative and adding a booth can never reduce either total. And when a reading makes """
            """the problem trivial, that is strong evidence it is the wrong reading — say that out loud, because noticing """
            """it is exactly the kind of reasoning being tested.""")

think('Which reading would you ask about first — and how would you phrase the question?', 30,
      """Pause here, and do not think about code. Think about the single question you would ask to disambiguate, and how """
      """you would phrase it so it does not sound like you are stuck.""",
      """Here is how I would open, and then we will solve both real readings.""")

sid = beat('How to open', 'The clarifying question, phrased like an engineer',
           '<div style="font-size:31px;line-height:1.7">'
           '<i>&ldquo;Before I start &mdash; am I being given ranges to evaluate, or am I choosing the best range myself? '
           'Those are different problems: the first is prefix sums with O(1) queries, the second is a search over ranges '
           'and the objective is not monotone, so a sliding window will not work. I will assume I am choosing the range '
           'unless you say otherwise.&rdquo;</i><br><br>'
           'That is not asking for help. It is <b>naming both problems and committing to one</b> &mdash; which is what '
           'you would do on a real ticket.</div>',
           """Here is how I would open. Before I start — am I being given ranges to evaluate, or am I choosing the best """
           """range myself? Those are different problems: the first is prefix sums with constant-time queries, the second """
           """is a search over ranges where the objective is not monotone, so a sliding window will not work. I will assume """
           """I am choosing the range unless you say otherwise.""", step=0)
seg(sid, 1, """Notice what that does. It is not asking for help — it names both problems, shows you can already see the """
            """shape of each answer, and commits to one so the interview can proceed. That is exactly what you would do on """
            """a real ticket with an ambiguous requirement, and it is the single most transferable thing in this lesson.""")

sid = beat('Reading 1', 'Ranges are given — prefix sums, O(1) per query',
           '<div style="font-size:31px;line-height:1.7">'
           'Build two prefix arrays, one for drones and one for robots:<br>'
           '<code>D[i]</code> = drones in booths 0..i&minus;1, &nbsp; <code>R[i]</code> = robots in booths 0..i&minus;1.'
           '<br><br>'
           'Then for the range [l, r]:<br>'
           '<code>factor = (D[r+1] &minus; D[l]) &times; (R[r+1] &minus; R[l])</code><br><br>'
           '<b>O(m) build, O(1) per query.</b> The whole thing is four lines &mdash; the work is in seeing that the '
           'product of two sums decomposes into two independent range sums.</div>',
           """Reading one, the given-ranges version. Build two prefix arrays, one for drones and one for robots, where """
           """entry i holds the total across the first i booths.""", step=0)
seg(sid, 1, """Then the factor for any range is the difference of the drone prefixes multiplied by the difference of the """
            """robot prefixes.""")
seg(sid, 2, """Linear build, constant per query, four lines of code. The only real insight is that the product of two sums """
            """decomposes into two independent range sums, so you never need a combined structure — and notice that this """
            """would not be true if the factor were, say, the sum over booths of drones times robots. That distinction is """
            """worth stating, because it shows you checked rather than assumed.""")

D = Diagram('Reading 2: why the objective is not monotone')
D.box('b0', 130, 170, 320, 140, 'booth 0', 'drones 10\nrobots 0', kind='info', step=0)
D.box('b1', 490, 170, 320, 140, 'booth 1', 'drones 0\nrobots 10', kind='info', step=0)
D.box('b2', 850, 170, 320, 140, 'booth 2', 'drones 10\nrobots 0', kind='info', step=0)
D.label(130, 340, 'range [0,0] &rarr; 10 &times; 0 = **0**', kind='deny', step=1, w=1000, size='m')
D.label(130, 410, 'range [0,1] &rarr; 10 &times; 10 = **100**', kind='ok', step=2, w=1000, size='m')
D.label(130, 480, 'range [0,2] &rarr; 20 &times; 10 = **200**', kind='ok', step=3, w=1000, size='m')
D.label(1230, 340, 'Growing the range\nnever hurts here &mdash;\ncounts are non-negative.',
        kind='neutral', step=4, w=560, size='m')
D.label(130, 570, 'So if the range is **unconstrained**, the answer is the whole row. The question is only interesting '
                  'with a constraint: a length limit, a budget, or a cost per booth.',
        kind='deny', step=5, w=1660, size='l')
D.label(130, 690, 'That is the second thing to ask: **what stops me taking every booth?**',
        kind='dp', step=6, w=1660, size='l')
sid = D.build()
seg(sid, 0, """Now reading two, and here is the trap. Take three booths: ten drones and no robots, then no drones and ten """
            """robots, then ten drones again.""")
seg(sid, 1, """The single first booth scores zero, because one of the factors is zero.""")
seg(sid, 2, """The first two booths score a hundred.""")
seg(sid, 3, """All three score two hundred.""")
seg(sid, 4, """And the pattern generalises: because counts are non-negative, growing the range can never reduce either """
            """total, so it can never reduce the product.""")
seg(sid, 5, """Which means that if the range is unconstrained, the answer is the whole row, trivially. The question is only """
            """interesting if something stops you — a maximum length, a budget, or a cost per booth.""")
seg(sid, 6, """So that is the second thing to ask, and it follows naturally from the first: what stops me taking every """
            """booth? Arriving at that question by reasoning, rather than by being told, is the strongest possible thing """
            """you can do with this problem.""")

sid = table('Once they give you the constraint, the technique follows',
 ['Constraint they add', 'Technique', 'Cost'],
 [(0, ['Range length exactly k', 'Slide a window of width k over both prefix arrays', 'O(m)'], None),
  (0, ['Range length at most k', 'Same &mdash; and since growing helps, the best is always exactly k', 'O(m)'], None),
  (1, ['Each booth has a cost; total budget B', 'Not a window &mdash; a knapsack over contiguous ranges; two pointers if costs are positive', 'O(m) two-pointer'], None),
  (1, ['Pick any j booths (non-contiguous)', 'Greedy fails &mdash; it is a trade-off between two sums; sort by one, sweep the other', 'O(m log m)'], None),
  (2, ['Many queries, updatable booths', '<b>Fenwick tree</b> (BIT) per quantity &mdash; this was your recorded follow-up', 'O(log m) update and query'], None)],
 widths=[34, 44, 22])
seg(sid, 0, """Once they give you the constraint, the technique follows immediately. A range of exactly length k is a window """
            """of width k slid over both prefix arrays — linear. At most length k is the same, and here is a nice """
            """observation to offer: since growing the range never hurts, the best range is always exactly k, so the two """
            """constraints give the same answer.""")
seg(sid, 1, """A cost per booth with a total budget is not a window; it is a knapsack restricted to contiguous ranges, which """
            """collapses back to two pointers if all costs are positive. Picking any j booths without contiguity is the """
            """hardest variant, because it is a genuine trade-off between two sums and greedy on either one alone fails.""")
seg(sid, 2, """And your own recorded follow-up was updatable booths with many queries, which is a Fenwick tree — a binary """
            """indexed tree — one per quantity, giving logarithmic updates and logarithmic prefix queries. We will write """
            """that, because it is the follow-up you were actually asked.""")

CODE = '''// Reading 1: ranges given. Build once, answer each query in O(1).
public sealed class Booths {
    private readonly long[] _d, _r;                        // prefix sums, length m+1

    public Booths(int[] drones, int[] robots) {
        int m = drones.Length;
        _d = new long[m + 1]; _r = new long[m + 1];        // long: the product can exceed int
        for (int i = 0; i < m; i++) {
            _d[i + 1] = _d[i] + drones[i];
            _r[i + 1] = _r[i] + robots[i];
        }
    }

    public long Factor(int l, int r) =>                    // inclusive range [l, r]
        (_d[r + 1] - _d[l]) * (_r[r + 1] - _r[l]);
}

// Reading 2 with a length cap of k: slide the window, best is always exactly k.
public static long BestOfWidth(int[] drones, int[] robots, int k) {
    long d = 0, r = 0, best = 0;
    for (int i = 0; i < drones.Length; i++) {
        d += drones[i]; r += robots[i];
        if (i >= k) { d -= drones[i - k]; r -= robots[i - k]; }   // drop the element leaving the window
        if (i >= k - 1) best = Math.Max(best, d * r);
    }
    return best;
}'''
code_slide('Both readings, in C#', CODE, [
 ('2-3', """Reading one as a small class, because the question implies repeated queries. Two prefix arrays of length m plus """
           """one — the plus one is what lets you write the query without a special case at index zero."""),
 ('5-12', """The build is one pass. Note the arrays are long, not int: drones times robots can overflow a thirty-two-bit """
            """integer easily, and this is the single most likely correctness bug in the whole problem."""),
 ('14-15', """The query is one expression. Inclusive range, hence the r plus one — and I would say the convention out loud """
             """as I write it, because half of all off-by-one bugs in range problems are an unstated convention."""),
 ('18-26', """Reading two with a length cap. A fixed-width window over both quantities at once: add the entering booth, """
             """subtract the leaving booth, and record once the window is full. Linear, constant space, and it reuses the """
             """window discipline from chapter five rather than inventing anything."""),
])

sid = beat('The reported follow-up', 'Updatable booths &rarr; Fenwick tree',
           '<div style="font-size:30px;line-height:1.7">'
           'Your recorded follow-ups were <b>10&#8310; queries</b> and <b>updatable booths</b>. Prefix arrays answer '
           'queries in O(1) but an update costs O(m), because every later prefix shifts.<br><br>'
           'A <b>Fenwick tree</b> gives O(log m) for both &mdash; one tree for drones, one for robots. '
           'The factor for [l, r] is then two prefix queries per quantity: four log-time lookups.<br><br>'
           '<b>&bull;</b> update: add a delta at one index<br>'
           '<b>&bull;</b> query: prefix sum up to an index<br>'
           '<b>&bull;</b> range: prefix(r) &minus; prefix(l&minus;1), per quantity, then multiply</div>',
           """Now the follow-up you actually recorded: a million queries, and booths that can be updated. Prefix arrays """
           """answer queries in constant time but an update costs linear time, because every later prefix shifts.""",
           step=0)
seg(sid, 1, """A Fenwick tree — a binary indexed tree — gives you logarithmic time for both operations. One tree for drones, """
            """one for robots. The factor for a range is then two prefix queries per quantity, so four logarithmic lookups """
            """and a multiply.""")
seg(sid, 2, """Update adds a delta at one index. Query returns a prefix sum. A range is the difference of two prefixes, per """
            """quantity, and then you multiply. If you can sketch that structure and say why the multiplication still """
            """decomposes, you have answered the follow-up completely — and the decomposition is the part people forget to """
            """justify.""")

followups(
 ['"10⁶ queries" — recorded; prefix sums give O(1) per query after an O(m) build',
  '"Updatable booths" — recorded; a Fenwick tree per quantity, O(log m) update and query',
  '"k types instead of two" — recorded; k prefix arrays, and the objective becomes a product of k range sums'],
 ['"What if a booth can have negative drones (removals)?" — prefix sums still work; the window argument does not, because growing can now hurt',
  '"Booths arrive over time" — append-only prefix sums are free; that is exactly why log-structured stores like this shape',
  '"Distribute it" — partition the row; each shard keeps its own prefix totals, and a cross-shard range is a sum of whole shards plus two partial ends'],
 """Follow-ups, and the first three are the ones you recorded. A million queries is handled by the prefix build. """
 """Updatable booths is the Fenwick tree. And k types instead of two means k prefix arrays, with the objective becoming a """
 """product of k range sums — and note the arithmetic still decomposes, which is the reason the whole approach """
 """survives.""",
 """At staff level, the interesting one is negative values: if a booth can lose drones, prefix sums still work perfectly, """
 """but the window argument collapses, because growing the range can now hurt. Knowing which of your two arguments """
 """survives a change in assumptions is real understanding. Booths arriving over time is free with append-only prefix """
 """sums, which is exactly why log-structured storage likes this shape. And distributing it is clean: partition the row, """
 """each shard keeps its own totals, and a cross-shard range is a sum of whole shards plus two partial ends — the same """
 """decomposition, one level up.""")

interview_script([
 '"First, a clarification: am I given ranges to evaluate, or choosing the best range myself? Those are different problems."',
 '"If ranges are given: two prefix arrays, and the factor is a product of two range sums. O(m) build, O(1) query."',
 '"If I choose the range: note that counts are non-negative, so growing a range never hurts — unconstrained, the answer is the whole row."',
 '"So there must be a constraint. A length cap? A budget? That decides the technique."',
 '"With a length cap it is a fixed-width window over both quantities: O(m), O(1) space."',
 '"I will use long — drones × robots overflows int quickly."',
 '"If booths can be updated, prefix arrays cost O(m) per update, so I would switch to a Fenwick tree per quantity."',
], [
 """The script, and this one is mostly talking rather than coding, which is correct for this question. Open with the """
 """clarification that names both problems.""",
 """Give the easy reading in one sentence with its complexity. Then give the observation that makes the hard reading """
 """degenerate, and turn it into the next question rather than into a complaint — a constraint must exist, what is """
 """it?""",
 """Then the technique, the overflow guard, and the update follow-up with the structure named. A candidate who does all """
 """of that has demonstrated requirements analysis, two algorithms, a correctness guard and a scaling answer, on a """
 """question whose statement was three lines long. That is what a Staff coding round is actually looking for.""",
])

sid = statement('Lesson 6.2', 'An ambiguous question is not an obstacle. It is the question.',
                'Name every reading, say what each would cost, commit to one, and keep moving.',
                kind='ok')
seg(sid, 0, """One line. An ambiguous question is not an obstacle in the way of the interview — it is the interview.""")
seg(sid, 1, """Name every reading, say what each one would cost, commit to one, and keep moving. That is what senior """
            """engineers do with an underspecified ticket, and it is what the interviewer is trying to find out. Next is """
            """the chapter six recap.""")
