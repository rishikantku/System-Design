# -*- coding: utf-8 -*-
"""Chapter 5 recap — sliding window and two pointers."""
from lib import *

lesson_header('5.R', 'Chapter 5 recap: windows and pointers', 'Recap · templates · mini mock',
              'High', '3 reported questions · the cheapest patterns to master', '2026', 'Medium', 11,
              """Chapter five recap. Three reported questions in this chapter, and it is the cheapest chapter in the course """
              """to master — the code is short and the ideas are few. What makes people lose marks here is not difficulty, """
              """it is speed: candidates reach for a window before they have said what the window means, and then debug a """
              """loop whose invariant they never wrote down. So this recap is mostly about how to start, not how to """
              """finish.""")

sid = beat('Pattern summary', 'The chapter in one page',
           '<div class="bigidea">Both patterns work because <b>one pointer never goes backwards</b>. '
           'That is what turns something that looks nested into something linear.</div>'
           '<div style="margin-top:26px;font-size:30px;line-height:1.7">'
           '<b>Sliding window</b> &mdash; both pointers travel the same direction; the window carries a counter and an '
           'invariant.<br>'
           '<b>Two pointers inward</b> &mdash; the pointers travel toward each other; each comparison eliminates one end.'
           '<br><br>'
           'Choosing between them is the same question every time: <i>is the thing I am looking for a contiguous run, or '
           'a pair?</i></div>',
           """One page. Both patterns in this chapter work for the same reason: one pointer never goes backwards. That is """
           """what turns something which looks nested into something linear, and it is the sentence to say when an """
           """interviewer asks why your two loops are not quadratic.""", step=0)
seg(sid, 1, """A sliding window has both pointers travelling the same direction, with a counter and an invariant attached. """
            """Two pointers inward has them travelling toward each other, with each comparison eliminating one end. And """
            """choosing between them is the same question every time: am I looking for a contiguous run, or for a pair?""")

sid = table('The three problems, and what made each one work',
 ['Problem', 'Shape', 'The move that mattered', 'Reported'],
 [(0, ['Max Consecutive Ones III', 'Window + counter', 'Translate "flip k zeros" into "window with at most k zeros"', 'Yes'], None),
  (1, ['Valid Palindrome II', 'Pointers inward', 'At the single mismatch, test both deletions &mdash; branch once, never recurse', 'Yes'], None),
  (2, ['Valid Triangle Number', 'Sort + pointers inward', 'Sort deletes two conditions; success counts b &minus; a triplets at once', 'Yes'], None)],
 widths=[26, 18, 44, 12])
seg(sid, 0, """Side by side. Max Consecutive Ones was a translation: flipping k zeros became a window containing at most k """
            """zeros, and once translated, the code was fifteen lines.""")
seg(sid, 1, """Valid Palindrome was about the single decision point — at the one mismatch, test both deletions, and never """
            """recurse, because spending the budget removes all remaining freedom.""")
seg(sid, 2, """And Valid Triangle was about sorting doing real work: it deleted two of the three conditions, and then success """
            """counted a whole range of triplets in a single step rather than enumerating them.""")

sid = steps_list('Recognition checklist',
 [(0, '&ldquo;longest / shortest **contiguous**&hellip; with at most k&hellip;&rdquo; &rarr; **sliding window**, counter = the thing bounded by k', 'ok'),
  (0, '&ldquo;subarray&rdquo; or &ldquo;substring&rdquo; &rarr; contiguous &rarr; window. &ldquo;subsequence&rdquo; &rarr; **not** a window; usually DP', 'ok'),
  (1, '&ldquo;pair / triplet summing to&hellip;&rdquo; on sortable data &rarr; **sort, then pointers inward**', 'ok'),
  (1, '&ldquo;at most one / at most k edits&rdquo; &rarr; branch while k is tiny; at k &ge; 2 switch to DP', 'ok'),
  (2, '&ldquo;**count** how many&hellip;&rdquo; &rarr; look for the step that counts a whole range at once', 'ok'),
  (2, 'Palindrome anything &rarr; pointers inward, and ask about case, punctuation and Unicode', 'shared'),
  (3, 'A window question where the answer can **shrink** &rarr; you need a deque (monotonic queue), not a counter', 'shared'),
  (3, 'Negative numbers in a &ldquo;sum at most k&rdquo; window &rarr; **the window breaks**; prefix sums instead (chapter 6)', 'deny')],
 numbered=False)
seg(sid, 0, """The recognition checklist. Longest or shortest contiguous something with at most k of something means a sliding """
            """window, and the counter counts whatever k bounds. And a vocabulary point that costs people real marks: """
            """subarray and substring mean contiguous, so a window applies. Subsequence does not mean contiguous, and a """
            """window will silently give the wrong answer — that is usually dynamic programming.""")
seg(sid, 1, """Pair or triplet summing to something, on data you can sort, means sort and then pointers inward. At most one """
            """or at most k edits means branch while k is tiny, and switch to a dynamic program at two or more.""")
seg(sid, 2, """When the question says count how many, look for the step that counts a whole range at once. And any palindrome """
            """question means pointers inward — plus the clarifying questions about case, punctuation and Unicode.""")
seg(sid, 3, """Two traps at the end. If the quantity you are tracking can shrink as the window grows — a maximum, for """
            """instance — a counter is not enough and you need a monotonic deque. And if a "sum at most k" window can """
            """contain negative numbers, the window approach breaks outright, because growing the window no longer """
            """monotonically grows the sum. That one becomes prefix sums, which is the next chapter.""")

sid = cards('The mistakes that actually cost people', [
 (0, 'Coding before stating the invariant', 'The number one failure here. Say "the window always contains at most k zeros" <i>out loud</i>, then write the loop that maintains it.', 'deny'),
 (0, 'Using a window on a subsequence problem', 'Silent wrong answers. Contiguity is a precondition, not a detail.', 'deny'),
 (1, 'Forgetting the window can be empty', 'When left passes right, length is 0, not negative. Check your arithmetic on that case.', 'deny'),
 (1, 'Taking substrings inside the loop', 'Turns O(1) space into O(n) and O(n) time into O(n²). Pass indices.', 'shared'),
 (2, 'Not asking whether you may sort', 'Sorting mutates the caller&rsquo;s array and costs n log n. Both are worth one sentence.', 'shared'),
 (2, 'Missing integer overflow', 'a + b in a comparison. Rearrange to a > c − b, or use long. Cheap to say, strong signal.', 'ok'),
], cols=2)
seg(sid, 0, """The mistakes. Number one in this chapter: coding before stating the invariant. Say "the window always contains """
            """at most k zeros" out loud, and then write the loop that maintains that sentence. Candidates who do this """
            """finish in four minutes; candidates who do not spend fifteen debugging. And using a window on a subsequence """
            """problem gives silent wrong answers — contiguity is a precondition, not a detail.""")
seg(sid, 1, """Forgetting that the window can be empty, so its length is zero rather than negative. And taking substrings """
            """inside the loop, which turns constant space into linear and linear time into quadratic — pass indices.""")
seg(sid, 2, """Not asking whether you may sort, when sorting mutates the caller's data and costs n log n. And missing """
            """overflow in a comparison of sums, which is cheap to mention and a disproportionately strong signal.""")

T1 = '''// TEMPLATE J - sliding window with a budget. Works for: at most k zeros / k distinct / k replacements.
int left = 0, best = 0;
var state = new Counter();                        // whatever "at most k of X" needs

for (int right = 0; right < n; right++) {
    state.Add(a[right]);                          // expand

    while (state.Violates(k)) {                   // restore the invariant
        state.Remove(a[left]);
        left++;                                   // left NEVER rewinds -> O(n) total
    }

    best = Math.Max(best, right - left + 1);      // legal here, by construction
}'''
code_slide('Template J &mdash; sliding window with a budget', T1, [
 (None, """Template J. Expand right, restore the invariant with a while loop, then record — and the comment on the last """
          """line is the important one: the window is legal at that point by construction, which is why you can record """
          """unconditionally. Swap the counter for a frequency map, a distinct-count or a running sum and you have solved """
          """the whole family. Left never rewinds, which is your linearity argument."""),
])

T2 = '''// TEMPLATE K - two pointers inward, with a single budgeted branch.
int i = 0, j = n - 1;
while (i < j) {
    if (a[i] == a[j]) { i++; j--; continue; }     // matching ends: shrink both
    return Check(i + 1, j) || Check(i, j - 1);    // spend the one unit of budget, both ways
}
return true;

// TEMPLATE L - sort, fix one, count a range at once.
Array.Sort(a);
for (int c = n - 1; c >= 2; c--) {
    int lo = 0, hi = c - 1;
    while (lo < hi) {
        if (a[lo] + a[hi] > a[c]) { count += hi - lo; hi--; }   // count, do not enumerate
        else lo++;
    }
}'''
code_slide('Templates K and L &mdash; pointers inward, and sort-then-count', T2, [
 ('1-6', """Template K: pointers inward with one unit of budget. Matching ends shrink both. A mismatch spends the budget """
           """both ways and returns — and the fact that it returns is what keeps this linear rather than exponential."""),
 ('8-17', """Template L: sort, fix the largest, and count a range in one step instead of enumerating it. That `count += hi """
            """- lo` line is the one worth having in your fingers, because it is the difference between n squared and n """
            """cubed, and the same shape appears in every "count the pairs or triplets satisfying an inequality" """
            """question."""),
])

sid = table('The reported questions, ranked',
 ['#', 'Question', 'Evidence', 'Revise'],
 [(0, ['1', 'Max Consecutive Ones III', 'Your own list + the LinkedIn tagged set', '**First**'], None),
  (0, ['2', 'Valid Palindrome II (+ k edits)', 'Reported with the k-edits extension', 'Second'], None),
  (1, ['3', 'Valid Triangle Number', 'A LinkedIn phone-screen write-up', 'Second'], None),
  (2, ['&mdash;', 'Minimum window substring, longest k-distinct', 'Not reported for LinkedIn &mdash; but they are the same template', 'Free'], 'dim'),
  (2, ['&mdash;', 'Trapping rain water, container with most water', 'Not reported &mdash; general preparation', 'If time'], 'dim')],
 widths=[6, 42, 40, 12])
seg(sid, 0, """Ranked. Max Consecutive Ones first — your own list and the tagged set. Then Valid Palindrome with its k """
            """extension.""")
seg(sid, 1, """Then Valid Triangle.""")
seg(sid, 2, """And the honest lines again: minimum window substring and longest substring with k distinct characters are not """
            """reported for LinkedIn, but they are literally template J with a different counter, so you get them almost """
            """free. Trapping rain water and container with most water are general preparation — worth an hour, not a """
            """day.""")

sid = steps_list('Five-minute rapid revision &mdash; say each of these out loud',
 [(0, 'Contiguous, or not? Subarray means window; subsequence does not.', 'ok'),
  (0, 'What is the invariant, in one sentence?', 'ok'),
  (1, 'What does the counter count, and what refunds it?', 'ok'),
  (1, 'Which pointer moves on success, and which on failure?', 'ok'),
  (2, 'Why is this O(n) and not O(n²)? — because one pointer never rewinds.', 'shared'),
  (2, 'Empty window, k = 0, k ≥ n, all-same input.', 'shared'),
  (3, 'Am I allowed to sort? Am I allowed to mutate?', 'info'),
  (3, 'Overflow, Unicode, and allocation inside the loop.', 'info')],
 numbered=True)
seg(sid, 0, """Rapid revision. Contiguous or not. What is the invariant, in one sentence.""")
seg(sid, 1, """What does the counter count and what refunds it. Which pointer moves on success and which on failure — get """
            """that backwards and the loop runs forever.""")
seg(sid, 2, """Why is this linear rather than quadratic, with the answer being that one pointer never rewinds. Then the """
            """degenerate inputs: empty window, k zero, k at least n, and an all-same array.""")
seg(sid, 3, """Am I allowed to sort, am I allowed to mutate. And the three details: overflow, Unicode, and allocation inside """
            """the loop.""")

sid = beat('Mini mock &mdash; 12 minutes', 'Pause here and actually do it',
           '<div class="qwrap"><div class="qlabel">The interviewer asks</div>'
           '<div class="qtext" style="font-size:34px">&ldquo;Given a list of a member&rsquo;s daily activity counts and a '
           'number k, find the longest stretch of days in which <b>at most k days had zero activity</b> &mdash; but a '
           'stretch is only valid if it also <b>starts and ends on an active day</b>.&rdquo;</div></div>',
           """Mini mock, twelve minutes. Given a member's daily activity counts and a number k, find the longest stretch of """
           """days in which at most k days had zero activity — but the stretch is only valid if it starts and ends on an """
           """active day. Pause, talk out loud, write real C sharp. There is one clause in there that changes the standard """
           """template, and finding it is the point of the exercise.""", kicker='Chapter 5 recap')
think('Twelve minutes. State the invariant first. Then find the clause that breaks the plain template.', 40,
      """Go. State the invariant before you write anything, then look hard at the second clause.""",
      """Right. Here is the grading.""")

sid = cards('How I would grade that', [
 (0, 'The base is template J', 'Window with a counter of zero-activity days, bounded by k. If you got here, you have the pattern.', 'ok'),
 (0, 'The clause that changes it', 'The window must <b>start and end on an active day</b>. The plain template reports windows that begin or end on a zero &mdash; and those are longer, so it will systematically over-report.', 'deny'),
 (1, 'The fix', 'Before recording, trim zeros off <b>both ends</b> of the current window. Trimming only shortens, so it cannot break the invariant.', 'ok'),
 (1, 'Keep it O(n)', 'Do not trim inside a loop each step. Track the index of the first and last active day in the window as you go &mdash; both move forward only.', 'ok'),
 (2, 'Edge cases I wanted named', 'All zeros (answer 0, not k); k = 0; a single active day (answer 1); no active days at all.', 'shared'),
 (2, 'The staff close', '&ldquo;In production this is a streak query over an activity table &mdash; I would ask whether it is computed per request or maintained incrementally, because that decides everything.&rdquo;', 'ok'),
], cols=2)
seg(sid, 0, """The base is template J: a window counting zero-activity days, bounded by k. If you got there, you have the """
            """pattern.""")
seg(sid, 1, """The clause that changes it is the requirement to start and end on an active day. The plain template happily """
            """reports a window that begins or ends on a zero — and crucially, those windows are longer, so the standard """
            """code does not fail loudly, it systematically over-reports. That is the kind of bug that passes a quick test """
            """and reaches production.""")
seg(sid, 2, """The fix is to trim zeros off both ends before recording a length. Trimming only ever shortens the window, so """
            """it cannot break the invariant you already maintain — and saying that sentence is how you show the fix is """
            """safe rather than hopeful.""")
seg(sid, 3, """Keep it linear by not trimming with an inner loop on every step. Track the first and last active index inside """
            """the window as you go; both move forward only.""")
seg(sid, 4, """Edge cases I wanted named: all zeros gives zero rather than k, k equals zero, a single active day gives one, """
            """and no active days at all. Then the staff close, one sentence: in production this is a streak query over an """
            """activity table, and I would ask whether it is computed per request or maintained incrementally — because """
            """that decides the entire design, and the loop we just wrote is the small part. Chapter five done.""")
