# -*- coding: utf-8 -*-
"""Chapter 7 recap — binary search and elimination."""
from lib import *

lesson_header('7.R', 'Chapter 7 recap: search and elimination', 'Recap · templates · mini mock',
              'High', '2 reported questions · one idea underneath both', '2026', 'High', 11,
              """Chapter seven recap. Two reported questions, and one idea underneath both of them: make a single """
              """comparison rule out a whole set of candidates rather than one. Binary search does it by halving. The """
              """celebrity sweep does it by eliminating one per call, which sounds weaker until you notice that one per """
              """call is provably the best anyone can do. Same seven parts as always.""")

sid = beat('Pattern summary', 'The chapter in one page',
           '<div class="bigidea">Before writing a loop, ask: <b>what does one comparison rule out?</b> '
           'If the answer is &ldquo;one candidate&rdquo;, you get O(n). If it is &ldquo;half of them&rdquo;, '
           'you get O(log n).</div>'
           '<div style="margin-top:26px;font-size:30px;line-height:1.7">'
           'Binary search needs a <b>monotone</b> property &mdash; something true on one side of a boundary and false on '
           'the other. Elimination needs only that <b>every answer is informative</b>.<br><br>'
           'Most candidates look for a sorted array. The better habit is to look for the <b>boundary</b>.</div>',
           """One page. Before writing any loop in this chapter, ask what a single comparison rules out. If the answer is """
           """one candidate, you get a linear algorithm. If it is half the candidates, you get a logarithmic one.""",
           step=0)
seg(sid, 1, """Binary search needs a monotone property — something that is true on one side of a boundary and false on the """
            """other. Elimination needs something weaker: only that every answer teaches you something. And here is the """
            """habit worth changing: most candidates scan for a sorted array before considering binary search. The better """
            """habit is to look for the boundary, because plenty of binary-search problems have no sorted array anywhere in """
            """them.""")

sid = table('The two problems, and what each comparison bought',
 ['Problem', 'One comparison rules out', 'Result', 'Reported'],
 [(0, ['Find K Closest Elements', 'Half of the possible <b>window starts</b>', 'O(log(n&minus;k) + k)', 'Yes'], None),
  (1, ['Find the Celebrity', 'Exactly one person &mdash; whichever way the answer goes', 'O(n), and provably optimal', 'Yes'], None)],
 widths=[26, 40, 22, 12])
seg(sid, 0, """Find K Closest Elements: each comparison rules out half of the possible window starts, giving logarithmic """
            """time plus the cost of copying the answer out.""")
seg(sid, 1, """Find the Celebrity: each call rules out exactly one person, whichever way the answer goes, giving linear time """
            """— which is provably optimal, because with fewer calls the query graph is disconnected and an adversary can """
            """move the celebrity. Both are the same question asked twice: what does one answer buy me?""")

sid = steps_list('Recognition checklist',
 [(0, 'Sorted input **and** you want a position &rarr; binary search &mdash; but search for the **index**, not the value', 'ok'),
  (0, '&ldquo;Minimum x such that P(x) is true&rdquo; &rarr; **binary search on the answer**, even with no array in sight', 'ok'),
  (1, 'The answer is a contiguous block &rarr; search for **where it starts**; one unknown, not k', 'ok'),
  (1, 'An expensive oracle you may call &rarr; ask what **each possible answer eliminates**, then count calls, not time', 'ok'),
  (2, 'Tie-breaks stated in the problem &rarr; implement them with **strict vs non-strict** comparisons, not special cases', 'ok'),
  (2, 'Unsorted, but you want the k best &rarr; **quickselect**, O(n) average &mdash; not a sort', 'shared'),
  (3, '`lo = mid + 1` vs `hi = mid` &rarr; whichever side may still hold the answer **keeps its endpoint**', 'deny'),
  (3, 'Anything with &ldquo;as few calls as possible&rdquo; &rarr; there is probably a **lower-bound argument** to give', 'shared')],
 numbered=False)
seg(sid, 0, """The recognition checklist. Sorted input where you want a position means binary search — and search for the """
            """index rather than the value, which is what lesson one was about. And the most under-used trigger: minimum x """
            """such that some property holds means binary search on the answer, even when there is no array anywhere in the """
            """problem.""")
seg(sid, 1, """If the answer is a contiguous block, search for where it starts: one unknown rather than k. And if you are """
            """given an expensive oracle, ask what each possible answer eliminates, and then count calls rather than """
            """time — because calls are the currency the question cares about.""")
seg(sid, 2, """Tie-breaks stated in the problem should be implemented by choosing strict or non-strict comparisons, not by """
            """bolting on special cases. Unsorted data where you want the k best is quickselect, linear on average, not a """
            """sort.""")
seg(sid, 3, """Then the rule that prevents the classic bug: when you update lo to mid plus one versus hi to mid, whichever """
            """side may still contain the answer keeps its endpoint. And any question phrased as "using as few calls as """
            """possible" is hinting that a lower-bound argument exists and that they would like to hear it.""")

sid = cards('The mistakes that actually cost people', [
 (0, 'The infinite loop', 'Writing <code>hi = mid</code> with <code>mid = (lo+hi+1)/2</code>, or the mirror image. Pick a convention and test it on two elements.', 'deny'),
 (0, 'Skipping verification', 'The celebrity sweep proves a negative. Returning the survivor unverified is a correctness bug, not a shortcut.', 'deny'),
 (1, 'Binary searching on a non-monotone property', 'Silently wrong. Say the monotone claim out loud &mdash; "if a window starting here is too far left, so is every earlier one".', 'deny'),
 (1, 'Ignoring the stated tie-break', 'It is in the problem text. Read it back before coding.', 'deny'),
 (2, 'Counting time when they asked about calls', 'If the oracle is expensive, O(n) time with O(n²) calls is a failing answer.', 'deny'),
 (2, 'Overflow in mid', '<code>lo + (hi − lo)/2</code> costs nothing and gets noticed.', 'ok'),
], cols=2)
seg(sid, 0, """The mistakes. The infinite loop, which comes from mismatching your midpoint rounding with your update rule — """
            """pick one convention and test it on a two-element input, every time. And skipping verification on the """
            """celebrity problem, which is a correctness bug rather than a missing optimisation.""")
seg(sid, 1, """Binary searching on a property that is not monotone, which is silently wrong — so say the monotone claim out """
            """loud, in the form "if a window starting here is too far left, then so is every earlier one". If you cannot """
            """say that sentence, you cannot use binary search. And ignoring a stated tie-break.""")
seg(sid, 2, """Counting the wrong resource: if the oracle is expensive, a solution that is linear in time but quadratic in """
            """calls is a failing answer. And overflow in the midpoint, which costs nothing to avoid.""")

T1 = '''// TEMPLATE O - binary search for a BOUNDARY (not a value).
int lo = 0, hi = n - k;                       // the search space is the ANSWER's range
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;             // rounds down, pairs with hi = mid
    if (TooFarLeft(mid)) lo = mid + 1;        // mid is ruled out
    else                 hi = mid;            // mid may still be the answer - keep it
}
return lo;                                    // lo == hi == the boundary

// TEMPLATE P - binary search on the ANSWER (no array required).
long lo = minPossible, hi = maxPossible;
while (lo < hi) {
    long mid = lo + (hi - lo) / 2;
    if (Feasible(mid)) hi = mid;              // mid works -> the answer is mid or smaller
    else               lo = mid + 1;          // mid fails -> the answer is larger
}
return lo;                                    // smallest feasible value'''
code_slide('Templates O and P &mdash; boundary search, and search on the answer', T1, [
 ('1-7', """Template O: search the range of the answer rather than the contents of an array. The pairing to memorise is """
           """rounding down with hi equals mid; the other pairing is rounding up with lo equals mid. Mixing them is the """
           """infinite loop."""),
 ('9-17', """Template P is the one that wins interviews, because it applies where no sorted array exists. You define a """
            """feasibility predicate, check that it is monotone — false, false, false, true, true — and search for the """
            """switch. Minimum capacity to ship in d days, minimum speed to finish in h hours, smallest maximum page count: """
            """all the same eight lines with a different Feasible."""),
])

T2 = '''// TEMPLATE Q - elimination with an oracle: one call, one candidate gone.
int candidate = 0;
for (int i = 1; i < n; i++)
    if (Knows(candidate, i)) candidate = i;   // whichever way it goes, one person is eliminated

for (int i = 0; i < n; i++) {                 // the sweep proves a NEGATIVE - verify the survivor
    if (i == candidate) continue;
    if (Knows(candidate, i) || !Knows(i, candidate)) return -1;
}
return candidate;'''
code_slide('Template Q &mdash; elimination with an oracle', T2, [
 (None, """Template Q. One sweep where every answer eliminates somebody, then a verification pass, because the sweep only """
          """proved that everyone else is disqualified. The shape generalises to any problem with a pairwise oracle and a """
          """uniqueness property — find the majority element with an equality oracle is the same skeleton, and so is """
          """finding a single faulty machine with a pairwise health check."""),
])

sid = table('The reported questions, ranked',
 ['#', 'Question', 'Evidence', 'Revise'],
 [(0, ['1', 'Find the Celebrity', 'Your own list + a Taro DSA-round report', '**First**'], None),
  (0, ['2', 'Find K Closest Elements', 'Your own list + the LinkedIn tagged set', '**First**'], None),
  (1, ['&mdash;', 'Search in a rotated sorted array, peak element', 'Not reported for LinkedIn &mdash; but they are template O', 'Free'], 'dim'),
  (1, ['&mdash;', 'Koko eating bananas, ship within D days', 'Not reported &mdash; but they are template P, which is worth one hour', 'If time'], 'dim')],
 widths=[6, 42, 40, 12])
seg(sid, 0, """Ranked, and both are first-tier: Find the Celebrity and Find K Closest Elements are each on your own list.""")
seg(sid, 1, """And the honest notes. Rotated sorted array and peak element are not reported for LinkedIn, but they are """
            """template O with a different predicate, so you get them nearly free. The binary-search-on-the-answer """
            """classics are also not reported — but I would spend an hour on one of them anyway, because template P is the """
            """single most transferable thing in this chapter and it shows up disguised more often than it shows up """
            """openly.""")

sid = steps_list('Five-minute rapid revision',
 [(0, 'What does one comparison rule out — one candidate, or half?', 'ok'),
  (0, 'What exactly am I searching over — values, indices, or the answer itself?', 'ok'),
  (1, 'Say the monotone claim as a sentence. If I cannot, binary search is wrong here.', 'ok'),
  (1, 'Which endpoint keeps mid, and does my rounding match it?', 'ok'),
  (2, 'Test on n = 1 and n = 2 before saying "done".', 'shared'),
  (2, 'Did the problem state a tie-break? Strict or non-strict?', 'shared'),
  (3, 'Is the expensive resource time, or calls?', 'info'),
  (3, 'Can I argue a lower bound? If so, say it.', 'info')],
 numbered=True)
seg(sid, 0, """Rapid revision. What does one comparison rule out. What am I searching over — values, indices, or the answer """
            """itself.""")
seg(sid, 1, """Say the monotone claim as a sentence, and if you cannot, binary search is the wrong tool. Which endpoint """
            """keeps mid, and does your rounding match it.""")
seg(sid, 2, """Test on one element and two elements before you say done — those two inputs catch nearly every """
            """binary-search bug. Did the problem state a tie-break, and is your comparison strict or not.""")
seg(sid, 3, """Is the expensive resource time or calls. And can I argue a lower bound — because if you can, it is thirty """
            """seconds well spent.""")

sid = beat('Mini mock &mdash; 15 minutes', 'Pause here and actually do it',
           '<div class="qwrap"><div class="qlabel">The interviewer asks</div>'
           '<div class="qtext" style="font-size:33px">&ldquo;We deploy a build to 1,000 hosts in order. Some build '
           'introduced a regression, and every host deployed <b>from that build onward</b> is unhealthy. '
           '<b>IsHealthy(host)</b> takes 30 seconds to run and may occasionally return a <b>false negative</b>. '
           'Find the first bad build.&rdquo;</div></div>',
           """Mini mock, fifteen minutes, and this one is deliberately infrastructure-flavoured because that is your """
           """round. We deploy a build to a thousand hosts in order. Some build introduced a regression, and every host """
           """deployed from that build onward is unhealthy. A health check takes thirty seconds and may occasionally """
           """return a false negative. Find the first bad build. Pause and work it.""", kicker='Chapter 7 recap')
think('Fifteen minutes. What is monotone here? And what does the false negative do to your argument?', 45,
      """Go. Two things to nail: what exactly is monotone here, and what an unreliable oracle does to the argument that """
      """made binary search valid in the first place.""",
      """Right. Here is the grading.""")

sid = cards('How I would grade that', [
 (0, 'The monotone claim, said explicitly', '&ldquo;Healthy, healthy, &hellip;, unhealthy, unhealthy&rdquo; &mdash; one boundary. That sentence is what licenses binary search, and I want to hear it before any code.', 'ok'),
 (0, 'Template O, with the right units', '~10 checks instead of 1,000. At 30 s each that is <b>5 minutes instead of 8 hours</b>. Say the wall-clock number, not just the log.', 'ok'),
 (1, 'The false negative breaks monotonicity', 'A spurious &ldquo;unhealthy&rdquo; moves your boundary left and you never revisit it &mdash; binary search <b>cannot recover</b> from a wrong answer. This is the whole point of the question.', 'deny'),
 (1, 'The fix', 'Repeat each check r times and treat healthy-if-any-pass (since only <i>negatives</i> are false). Cost goes from log n to r·log n checks &mdash; still tiny.', 'ok'),
 (2, 'What I hoped you would ask', 'Are false <b>positives</b> possible too? If both directions can lie, the boundary is fuzzy and you need a statistical answer, not a search.', 'ok'),
 (2, 'The staff close', '&ldquo;I would also run the two neighbours of the found boundary to confirm, and I would parallelise the repeats &mdash; they are independent, so r repeats cost one round-trip, not r.&rdquo;', 'ok'),
], cols=2)
seg(sid, 0, """First, the monotone claim said explicitly: healthy, healthy, and then unhealthy from some point onward — one """
            """boundary. I want to hear that sentence before any code, because it is what licenses the technique.""")
seg(sid, 1, """Then template O, with the units stated properly: about ten checks instead of a thousand, and at thirty seconds """
            """each that is five minutes instead of eight hours. Say the wall-clock number. In an infrastructure interview, """
            """"five minutes instead of eight hours" lands harder than "log n instead of n".""")
seg(sid, 2, """Now the real content. The false negative breaks monotonicity. A spurious unhealthy answer moves your boundary """
            """left, and binary search never revisits a region it has discarded, so it cannot recover from a single wrong """
            """answer. If you spotted that, you understood the chapter; if you binary searched happily over an unreliable """
            """oracle, this is the lesson.""")
seg(sid, 3, """The fix is to repeat each check some number of times and treat a host as healthy if any run passes — which is """
            """valid precisely because only negatives can be false. The cost goes from log n checks to r times log n, which """
            """is still tiny.""")
seg(sid, 4, """What I was hoping you would ask: are false positives possible too? If the oracle can lie in both directions, """
            """the boundary is fuzzy and you need a statistical answer rather than a search — and recognising when the """
            """technique simply does not apply is worth more than applying it well.""")
seg(sid, 5, """And the staff close: confirm by testing the two neighbours of the boundary you found, and parallelise the """
            """repeats, since they are independent — so r repeats cost one round trip rather than r. Chapter seven done.""")
