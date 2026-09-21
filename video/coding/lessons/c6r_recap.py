# -*- coding: utf-8 -*-
"""Chapter 6 recap — hashing and prefix sums."""
from lib import *

lesson_header('6.R', 'Chapter 6 recap: hashing and prefix sums', 'Recap · templates · mini mock',
              'High', '2 reported questions · one of them first-hand', '2026', 'High', 11,
              """Chapter six recap. Two questions in this chapter, but one of them is from your own list, which makes it """
              """first-party evidence and the strongest kind we have. The chapter's real subject is not hashing or prefix """
              """sums as techniques — you already know both. It is two judgement calls: when a clever encoding is worth """
              """the risk, and what to do when the question itself is ambiguous.""")

sid = beat('Pattern summary', 'The chapter in one page',
           '<div class="bigidea">Both techniques buy the same thing: they turn a <b>repeated computation</b> into a '
           '<b>lookup</b>.</div>'
           '<div style="margin-top:26px;font-size:30px;line-height:1.7">'
           '<b>Hashing</b> replaces "have I seen this before?" with one set operation.<br>'
           '<b>Prefix sums</b> replace "what is the total over this range?" with one subtraction.<br><br>'
           'The skill is not writing either one. It is <b>noticing the repeated computation</b> in the first place '
           '&mdash; and knowing what each shortcut costs you.</div>',
           """One page. Both techniques in this chapter buy exactly the same thing: they turn a repeated computation into a """
           """lookup.""", step=0)
seg(sid, 1, """Hashing replaces "have I seen this before" with one set operation. Prefix sums replace "what is the total """
            """over this range" with one subtraction. Neither is hard to write. The skill is noticing the repeated """
            """computation in the first place, and knowing what each shortcut costs you — an exact encoding costs nothing, """
            """a real hash costs you collision risk, and a prefix array costs you cheap updates.""")

sid = table('The two problems, and the judgement each one demanded',
 ['Problem', 'Technique', 'The judgement call', 'Reported'],
 [(0, ['Repeated DNA Sequences', 'Fixed-window hashing, or 2-bit packing', 'Both are O(n). Say what the clever version buys &mdash; allocation, not asymptotics &mdash; and offer the simple one first', 'Tagged set'], None),
  (1, ['Booths / experience factor', 'Prefix sums per quantity', 'The question is ambiguous. Name all three readings, show that one is degenerate, commit to one', '**Your list**'], None)],
 widths=[22, 22, 44, 12])
seg(sid, 0, """Repeated DNA Sequences: a fixed-width window with a set, or the two-bit packing. Both linear. The judgement """
            """call is to say what the clever version actually buys — allocation, not asymptotics — and to offer the simple """
            """one first.""")
seg(sid, 1, """The booths problem: prefix sums, one per quantity. The judgement call is that the question is ambiguous, and """
            """the right move is to name all three readings, show that one of them is degenerate because growing a range """
            """never hurts, and commit to one. That is the lesson from the only first-hand question in this chapter, which """
            """is worth taking seriously.""")

sid = steps_list('Recognition checklist',
 [(0, '&ldquo;occurring more than once&rdquo; / &ldquo;duplicate&rdquo; / &ldquo;seen before&rdquo; &rarr; a **set**, and ask what a false positive would cost', 'ok'),
  (0, 'Fixed-length substrings over a small alphabet &rarr; consider **bit packing**; it is exact, so no collisions', 'ok'),
  (1, 'Variable-length substrings &rarr; a **polynomial rolling hash**, and now you must **verify** a match', 'shared'),
  (1, '&ldquo;sum / count over a range&rdquo;, many queries &rarr; **prefix sums**, O(1) per query after O(n) build', 'ok'),
  (2, 'Ranges **and** updates &rarr; **Fenwick tree** (O(log n) both) or a segment tree if you need more than sums', 'ok'),
  (2, 'A product of two range totals &rarr; it **decomposes**; keep one prefix array per quantity, never a combined one', 'ok'),
  (3, 'Non-negative values &rarr; growing a range never hurts &rarr; **there must be a constraint** &mdash; find it', 'deny'),
  (3, 'Negative values in a range problem &rarr; windows break, prefix sums survive. Know which argument you were relying on', 'deny')],
 numbered=False)
seg(sid, 0, """The recognition checklist. Occurring more than once, duplicate, or seen before means a set — and the question """
            """to attach is what a false positive would cost, because that decides whether a probabilistic filter is """
            """allowed. Fixed-length substrings over a small alphabet invites bit packing, which is exact and therefore """
            """collision-free.""")
seg(sid, 1, """Variable-length substrings need a real polynomial rolling hash, and there you must verify a match rather than """
            """trusting it. Sum or count over a range with many queries means prefix sums.""")
seg(sid, 2, """Ranges together with updates means a Fenwick tree, or a segment tree if you need something richer than sums. """
            """And a product of two range totals decomposes, so you keep one prefix array per quantity rather than trying """
            """to build a combined structure — people waste ten minutes there.""")
seg(sid, 3, """The last two are the traps. Non-negative values mean growing a range never hurts, which means an """
            """unconstrained maximisation is degenerate, which means there is a constraint you have not been told — go and """
            """find it. And negative values break windows while leaving prefix sums intact, so know which of the two """
            """arguments your solution was leaning on.""")

sid = cards('The mistakes that actually cost people', [
 (0, 'Integer overflow', 'Products of sums overflow int fast. Use long, and say so while you type it.', 'deny'),
 (0, 'Trusting a hash match', 'A real rolling hash can collide. If you did not verify, your answer is wrong sometimes &mdash; the worst kind of wrong.', 'deny'),
 (1, 'Optimising before pricing', 'Bit packing a 10-mer is fine. Bit packing because it feels clever, without saying what it saves, is not.', 'shared'),
 (1, 'Off-by-one in prefix ranges', 'Decide the convention out loud &mdash; prefix[i] is the sum of the first i elements &mdash; then every query is prefix[r+1] − prefix[l].', 'deny'),
 (2, 'Solving before disambiguating', 'The booths question has three readings. Picking one silently means you may answer a question nobody asked.', 'deny'),
 (2, 'Rebuilding prefixes on update', 'O(n) per update. If updates exist at all, say &ldquo;Fenwick&rdquo; immediately.', 'shared'),
], cols=2)
seg(sid, 0, """The mistakes. Integer overflow, which in this chapter is not a theoretical concern — a product of two range """
            """sums overflows a thirty-two-bit integer very quickly. Use long and say so while you type it. And trusting a """
            """hash match without verification, which makes your answer wrong sometimes, which is the worst kind of """
            """wrong.""")
seg(sid, 1, """Optimising before pricing — bit packing is fine, bit packing without saying what it saves is not. And """
            """off-by-one errors in prefix ranges, which you prevent by stating the convention out loud before writing the """
            """query.""")
seg(sid, 2, """Solving before disambiguating, which on the booths question means you may answer a question nobody asked. And """
            """rebuilding prefixes on every update, which is linear per update — the moment updates are mentioned, say """
            """Fenwick.""")

T1 = '''// TEMPLATE M - fixed-window exact encoding (small alphabet, fixed length k).
const int Mask = (1 << (2 * K)) - 1;                 // 2 bits per symbol; K ≤ 16 for int, 32 for long
int window = 0;
var seen = new HashSet<int>(); var reported = new HashSet<int>();

for (int i = 0; i < s.Length; i++) {
    window = ((window << 2) | Code(s[i])) & Mask;    // roll in O(1), no allocation
    if (i < K - 1) continue;                         // window not full yet
    if (!seen.Add(window) && reported.Add(window))   // seen before AND not yet output
        result.Add(s.Substring(i - K + 1, K));       // materialise only for answers
}'''
code_slide('Template M &mdash; rolling exact encoding', T1, [
 (None, """Template M. Two bits per symbol, a mask that keeps the last k symbols, and a roll that is one expression with """
          """no allocation. The two-set idiom in the last two lines gives you "seen before and not yet reported" for free. """
          """And the guard on k matters: sixteen symbols for an int, thirty-two for a long, and beyond that you need a real """
          """hash with verification."""),
])

T2 = '''// TEMPLATE N - prefix sums per quantity, and the Fenwick upgrade when updates appear.
long[] pre = new long[n + 1];                        // pre[i] = sum of the first i elements
for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];
long RangeSum(int l, int r) => pre[r + 1] - pre[l];  // inclusive [l, r]

// Updates? Fenwick tree: O(log n) update, O(log n) prefix.
void Add(int i, long delta) { for (i++; i <= n; i += i & -i) bit[i] += delta; }
long Prefix(int i)          { long s = 0; for (i++; i > 0; i -= i & -i) s += bit[i]; return s; }
long Range(int l, int r) => Prefix(r) - Prefix(l - 1);'''
code_slide('Template N &mdash; prefix sums, and the Fenwick upgrade', T2, [
 ('1-3', """Template N. The prefix array is length n plus one so that the query needs no special case at zero, and the """
           """convention — prefix i is the sum of the first i elements — is what makes the query line obviously correct """
           """rather than fiddly."""),
 ('5-8', """And the Fenwick tree, which is four lines and worth having memorised, because the moment an interviewer says """
           """"and the values can change", writing these four lines is the entire answer. The `i & -i` isolates the lowest """
           """set bit, which is the jump size; update walks up, prefix walks down. If you only remember one advanced """
           """structure for this round, make it this one."""),
])

sid = steps_list('Five-minute rapid revision',
 [(0, 'What repeated computation am I removing — a membership test, or a range total?', 'ok'),
  (0, 'Is my encoding exact, or a hash? If a hash, where do I verify?', 'ok'),
  (1, 'Long, not int. Say it out loud.', 'ok'),
  (1, 'What is my prefix convention, and does the query match it?', 'ok'),
  (2, 'Do updates exist? Then Fenwick, not a prefix array.', 'shared'),
  (2, 'Are values non-negative? Then an unconstrained maximisation is degenerate — find the constraint.', 'shared'),
  (3, 'What does the clever version buy, in one sentence?', 'info'),
  (3, 'Which reading of the question am I answering?', 'info')],
 numbered=True)
seg(sid, 0, """Rapid revision. What repeated computation am I removing — a membership test or a range total. Is my encoding """
            """exact or a hash, and if it is a hash, where do I verify.""")
seg(sid, 1, """Long, not int, said out loud. What is my prefix convention, and does my query line match it.""")
seg(sid, 2, """Do updates exist — then Fenwick rather than a prefix array. Are the values non-negative — then an """
            """unconstrained maximisation is degenerate and there is a constraint I have not been told.""")
seg(sid, 3, """What does the clever version buy, in one sentence. And which reading of the question am I answering. Those """
            """last two are the chapter.""")

sid = beat('Mini mock &mdash; 12 minutes', 'Pause here and actually do it',
           '<div class="qwrap"><div class="qlabel">The interviewer asks</div>'
           '<div class="qtext" style="font-size:34px">&ldquo;Given a member&rsquo;s feed as a list of post categories, '
           'find the <b>shortest contiguous stretch</b> of posts that contains <b>at least one of every category</b> '
           'that appears in the whole feed. Then: the feed is 10&#8310; posts and new posts arrive '
           'continuously.&rdquo;</div></div>',
           """Mini mock, twelve minutes. Given a member's feed as a list of post categories, find the shortest contiguous """
           """stretch containing at least one of every category that appears in the whole feed. And then the second half: """
           """the feed is a million posts and new posts keep arriving. Pause, talk out loud, write real C sharp.""",
           kicker='Chapter 6 recap')
think('Twelve minutes. Which chapter does this belong to — five or six? And does the streaming half change the answer?', 40,
      """Go. And here is a hint about what I am actually testing: decide which chapter this problem belongs to before you """
      """start writing, and then decide whether the streaming half changes your answer or only your data structure.""",
      """Right. Here is the grading.""")

sid = cards('How I would grade that', [
 (0, 'It is a window, with a hash-map counter', 'Chapter five&rsquo;s template J, with a frequency map plus a &ldquo;how many categories are satisfied&rdquo; counter. Recognising that it is a window question dressed in hashing language is half the mark.', 'ok'),
 (0, 'Shortest, not longest — so shrink aggressively', 'Expand until valid, then shrink <b>while still valid</b>, recording each time. The longest-window habit from 5.1 gives the wrong loop here.', 'deny'),
 (1, 'One pre-pass to count the distinct categories', 'You cannot know "every category" without it. Two passes, still O(n) &mdash; say that rather than trying to do it in one.', 'ok'),
 (1, 'Edge cases', 'One category only (answer 1); every post the same; empty feed; a category appearing exactly once (it pins one end of the window).', 'shared'),
 (2, 'The streaming half — the honest answer', '&ldquo;Shortest stretch so far&rdquo; is still computable online, but the <b>set of all categories</b> changes as new ones appear, which retroactively invalidates earlier answers. Say that out loud.', 'deny'),
 (2, 'The staff close', '&ldquo;So I would define it over a window &mdash; shortest stretch in the last N posts or last 24 hours &mdash; which makes the answer well-defined and bounds memory. That is a product decision I would want confirmed.&rdquo;', 'ok'),
], cols=2)
seg(sid, 0, """First: this is a window question wearing hashing clothes. Template J from chapter five, with a frequency map """
            """and a counter of how many categories are currently satisfied. Recognising that across chapter boundaries is """
            """half the mark.""")
seg(sid, 1, """Second: it asks for the shortest, not the longest, which inverts the loop. You expand until the window is """
            """valid, then shrink while it stays valid, recording as you go. If you reused the longest-window habit from """
            """lesson five point one unchanged, you got the wrong loop — and that is a deliberate trap, because that is """
            """how it happens in a real interview.""")
seg(sid, 2, """You need a pre-pass to count the distinct categories, because you cannot recognise "every category" without """
            """knowing how many there are. Two passes, still linear — say that rather than contorting to do it in one.""")
seg(sid, 3, """Edge cases: a single category gives one, every post the same, an empty feed, and the nice one — a category """
            """appearing exactly once pins one end of the window, which is a good sanity check on your shrink logic.""")
seg(sid, 4, """Now the streaming half, and this is what I was really testing. The shortest stretch so far is computable """
            """online, but the set of all categories can grow as new posts arrive, and a new category retroactively """
            """invalidates every earlier answer. Noticing that the problem is not well-defined on an unbounded stream is """
            """the insight.""")
seg(sid, 5, """And the close, which is what a staff engineer says next: so I would define it over a window — the shortest """
            """stretch within the last N posts, or the last twenty-four hours — which makes the answer well-defined and """
            """bounds memory at the same time. And that is a product decision, so I would want it confirmed rather than """
            """assumed. Chapter six done.""")
