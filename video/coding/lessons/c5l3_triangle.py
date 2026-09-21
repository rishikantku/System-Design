# -*- coding: utf-8 -*-
"""Chapter 5, Lesson 3 — Valid Triangle Number."""
from lib import *

lesson_header('5.3', 'Valid Triangle Number — sort, then collapse a loop', 'Two pointers after sorting',
              'High', 'LinkedIn phone-screen write-up', '2026', 'Medium', 14,
              """Chapter five, lesson three. Valid Triangle Number, which appeared in a LinkedIn phone-screen write-up """
              """alongside the compact tree and Binary Tree Upside Down. Confidence is medium — one write-up, not several """
              """— but the technique is worth the fourteen minutes regardless, because it is the cleanest example in the """
              """course of a pattern that keeps recurring: sort the input, and an entire inner loop collapses into one """
              """piece of arithmetic.""")

sid = beat('Question', 'The problem, as they pose it',
           '<div class="qwrap"><div class="qtext" style="font-size:36px;line-height:1.4">'
           'Given an array of integers, count the number of <b>triplets</b> that can form a triangle with '
           'non-zero area.</div></div>',
           """The question. Given an array of integers, count the triplets that can form a triangle with non-zero area. """
           """Count them, not list them — which matters, and we will come back to why.""")

sid = beat('Understanding it', 'Three conditions, or one?',
           '<div style="font-size:31px;line-height:1.7">'
           'The triangle inequality says all three must hold:<br>'
           '<code>a + b &gt; c</code> &nbsp;&nbsp; <code>a + c &gt; b</code> &nbsp;&nbsp; <code>b + c &gt; a</code>'
           '<br><br>'
           'But if you <b>sort</b> so that <code>a &le; b &le; c</code>, the other two are automatic: '
           'c is the largest, so <code>a + c &gt; b</code> and <code>b + c &gt; a</code> cannot fail.<br><br>'
           '<b>One condition survives: a + b &gt; c.</b> Sorting did not just organise the data &mdash; it deleted '
           'two thirds of the problem.</div>',
           """First, understand the condition. The triangle inequality says all three sums must exceed the third side. """
           """Three conditions to check per triplet.""", step=0)
seg(sid, 1, """But sort the three values so that a is at most b is at most c, and two of those conditions become automatic. """
            """c is the largest, so a plus c must exceed b, and b plus c must exceed a — neither can fail.""")
seg(sid, 2, """One condition survives: a plus b greater than c. And notice what happened there. Sorting did not merely """
            """organise the data, it deleted two thirds of the problem. That is the kind of observation to say out loud, """
            """because it justifies the sort before you have written any loops.""")

think('One condition, a + b > c, over all triplets. Can you do better than three nested loops?', 30,
      """Pause. You now have one condition over all triplets, and the array is sorted. Three nested loops is n cubed. See """
      """whether you can get rid of one of them — and think about which loop is the one to remove.""",
      """Here is the move, and it is the same two-pointer idea as the last lesson, used differently.""")

sid = beat('Key observation', 'Fix the largest side. Then two pointers count a whole range at once.',
           '<div class="bigidea">Fix c as the largest. Put a pointer at each end of the range below it. '
           'If <code>a + b &gt; c</code>, then <b>every</b> value between a and b also works with b &mdash; '
           'that is <code>b &minus; a</code> triplets counted in one step.</div>'
           '<div style="margin-top:24px;font-size:30px;line-height:1.7">'
           'You never enumerate them. You count them. That is the difference between O(n&sup3;) and O(n&sup2;).</div>',
           """Fix c as the largest side and look at the range below it. Put one pointer at the smallest value and one just """
           """below c. Now if a plus b is greater than c, then every value between a and b is at least as big as a, so """
           """every one of them also works when paired with b. That is b minus a triplets, counted in a single step.""",
           step=0)
seg(sid, 1, """You never enumerate them — you count them. That is exactly the difference between n cubed and n squared, and """
            """"count, do not enumerate" is the sentence to remember, because the question asked for a count. If it had """
            """asked you to list the triplets, this shortcut would be illegal and the output size alone would be cubic.""")

D = Diagram('Sorted [2, 2, 3, 4, 7] with c = 4 fixed')
vals = ['2','2','3','4','7']
ids = array_row(D, vals, x=250, y=170, cw=180, ch=110, step=0, kind='info')
hl_cells(D, [ids[3]], x=250, y=170, cw=180, ch=110, marks={3: 0}, kind='shared')
D.label(250, 310, 'c = 4 at index 3. Search the range [0 .. 2] with a=0, b=2.',
        kind='neutral', step=0, w=1500, size='m')
D.label(250, 400, 'a=2, b=3 &rarr; 2 + 3 = 5 &gt; 4 ✓', kind='ok', step=1, w=1500, size='m')
D.label(250, 470, 'So **every** value from index a to index b&minus;1, paired with b, also works:\n'
                  'that is b &minus; a = **2** triplets &mdash; (2,3,4) twice, one per copy of 2.',
        kind='ok', step=2, w=1600, size='m')
D.label(250, 590, 'Then move **b** down (not a): b=1 &rarr; 2 + 2 = 4, **not** &gt; 4 ✗',
        kind='deny', step=3, w=1600, size='m')
D.label(250, 670, 'Fails &rarr; move **a** up. a meets b &rarr; done with this c.',
        kind='neutral', step=4, w=1600, size='m')
D.label(250, 760, 'Success shrinks from the top, failure shrinks from the bottom. Each c costs one linear sweep.',
        kind='dp', step=5, w=1600, size='l')
sid = D.build()
seg(sid, 0, """Concretely. Sorted array two, two, three, four, seven. Fix c as the four at index three, and search the range """
            """below it with a at the left end and b just below c.""")
seg(sid, 1, """a is two, b is three. Two plus three is five, which is greater than four. Success.""")
seg(sid, 2, """So every value from index a up to index b minus one, paired with b, also works — because they are all at """
            """least as large as a. That is b minus a, which is two triplets, counted in one step. Here it is the triple """
            """two, three, four counted once for each copy of the two.""")
seg(sid, 3, """Now move b down, not a. b becomes the value at index one, which is two. Two plus two is four, which is not """
            """greater than four — fail.""")
seg(sid, 4, """On failure we move a up. When a meets b, this c is finished.""")
seg(sid, 5, """So the rule is: success shrinks from the top, failure shrinks from the bottom. Each pointer only moves one """
            """direction, so each choice of c costs one linear sweep, and the whole algorithm is n squared.""")

CODE = '''public int TriangleNumber(int[] nums) {
    Array.Sort(nums);                                   // O(n log n), and it deletes two of the three conditions
    int count = 0;

    for (int c = nums.Length - 1; c >= 2; c--) {        // fix the LARGEST side, walking down
        int a = 0, b = c - 1;

        while (a < b) {
            if (nums[a] + nums[b] > nums[c]) {
                count += b - a;                         // every index in [a, b-1] also works with b
                b--;                                    // success: shrink from the top
            } else {
                a++;                                    // failure: the smallest value is hopeless here
            }
        }
    }
    return count;
}'''
code_slide('The C# implementation', CODE, [
 ('2', """Sort first. Say why as you type it: with a sorted triple, two of the three triangle conditions are automatic, so """
         """only a plus b greater than c remains. The sort is not housekeeping, it is the algorithm."""),
 ('5-6', """Fix the largest side and walk it downward. Stopping at index two is not an off-by-one guess — you need at """
           """least two values below c to form a triplet."""),
 ('8-11', """The success case, and this is the line the whole lesson is about. When a plus b beats c, you add b minus a in """
            """one go, because every index between them also works. Then you move b down, because every larger b with this """
            """same a has already been counted."""),
 ('12-14', """The failure case: if the smallest available value cannot make it work with the largest partner available, it """
             """cannot work with any smaller partner either, so a moves up and that value is gone for good."""),
 ('17', """Return the count. Sorting is n log n, the double walk is n squared, so n squared dominates — and zeros in the """
          """input are handled for free, since a zero can never satisfy a plus b greater than c when c is the largest. Worth """
          """mentioning; people often add a special case that is not needed."""),
])

sid = cards('Clarify and watch', [
 (0, 'Duplicates count separately', 'Two copies of 2 give two distinct triplets. Confirm that is what they want &mdash; some phrasings want distinct <i>values</i>.', 'deny'),
 (0, 'Zeros and degenerate triangles', '&ldquo;Non-zero area&rdquo; means strict inequality. A zero side can never work, and the code handles it without a special case.', 'ok'),
 (1, 'Count, not list', 'If they ask for the triplets themselves, the counting shortcut is illegal &mdash; output alone is O(n&sup3;).', 'deny'),
 (1, 'Overflow', 'a + b can exceed int range for large values. In C#, cast to long or compare as <code>nums[a] &gt; nums[c] - nums[b]</code>.', 'shared'),
 (2, 'Negative numbers', 'Ask. Side lengths are normally positive; if negatives are possible, filter them first and say why.', 'shared'),
 (2, 'Can I modify the input?', 'Sorting mutates the caller&rsquo;s array. Ask, or sort a copy and say you did.', 'ok'),
], cols=2)
seg(sid, 0, """Things to clarify. Duplicates count separately — two copies of the value two give two distinct triplets — and """
            """some phrasings of this question want distinct values instead, so confirm. Zeros need no special handling, """
            """because non-zero area means strict inequality and a zero side can never satisfy it.""")
seg(sid, 1, """If they ask you to list the triplets rather than count them, your shortcut becomes illegal, because the output """
            """alone is cubic. And overflow is a real one in C sharp: a plus b can exceed the integer range, so either cast """
            """to long or rearrange the comparison to a greater than c minus b. Raising overflow unprompted is a """
            """disproportionately good signal for the effort.""")
seg(sid, 2, """Ask about negatives — side lengths are normally positive, but say what you would do. And ask whether you may """
            """modify the input, because sorting mutates the caller's array. If in doubt, sort a copy and tell them you """
            """did.""")

sid = beat('Why this pattern recurs', 'Sort-then-two-pointer is a family, not a trick',
           '<div style="font-size:30px;line-height:1.7">'
           'The same skeleton solves a surprising range of questions:<br><br>'
           '<b>&bull;</b> Two Sum on a sorted array &rarr; pointers from both ends<br>'
           '<b>&bull;</b> 3Sum / 3Sum Closest &rarr; fix one, two-pointer the rest<br>'
           '<b>&bull;</b> Valid Triangle &rarr; fix the largest, count a range at once<br>'
           '<b>&bull;</b> Container With Most Water &rarr; move the limiting side<br><br>'
           'The shared idea: <b>sorting makes one pointer&rsquo;s movement monotone</b>, so a failed comparison rules out '
           'a whole block of candidates rather than one.</div>',
           """Step back for a second, because this is a family rather than a trick.""", step=0)
seg(sid, 1, """Two Sum on a sorted array is pointers from both ends. Three Sum fixes one element and two-pointers the rest. """
            """Valid Triangle fixes the largest and counts a range at once. Container With Most Water moves whichever side """
            """is limiting.""")
seg(sid, 2, """The shared idea is that sorting makes one pointer's movement monotone, so a failed comparison rules out a """
            """whole block of candidates rather than a single one. If you can say that sentence when you reach for the """
            """technique, you are demonstrating the pattern recognition this course is actually about.""")

followups(
 ['"Return the triplets, not the count" — the counting shortcut dies; O(n³) output is unavoidable',
  '"Distinct values only" — deduplicate after sorting, then the same sweep',
  '"What if the array is already sorted?" — drop the sort; O(n²) and say so'],
 ['"n is 10⁶" — O(n²) is a trillion operations; ask whether an approximate count or a bucketed/binned answer is acceptable',
  '"Streaming values" — you cannot sort a stream; maintain a sorted structure, or bucket by magnitude and count approximately',
  '"Parallelise it" — the outer loop over c is embarrassingly parallel once the array is sorted; partition c, sum the counts'],
 """Follow-ups. Returning the triplets kills the shortcut, because the output itself is cubic — that is a genuine """
 """complexity lower bound, not a limitation of your approach, and saying so is the right answer. Distinct values only """
 """means deduplicating after the sort. And if the array arrives sorted, drop the sort and say that your complexity """
 """improves to a clean n squared.""",
 """At staff level, the useful pushback is scale. A million elements makes n squared a trillion operations, which is not """
 """happening, so the right response is to ask whether an approximate or bucketed count is acceptable rather than to """
 """micro-optimise a doomed loop. Streaming values cannot be sorted, so you maintain a sorted structure or bucket by """
 """magnitude. And the outer loop over c is embarrassingly parallel once sorted, which is a clean answer for an infra """
 """interviewer — partition the choices of c, sum the counts, no coordination needed.""")

interview_script([
 '"First, sorting: with a ≤ b ≤ c, two of the three triangle conditions are automatic. Only a + b > c remains."',
 '"Then I fix c as the largest side and use two pointers in the range below it."',
 '"When a + b > c, every index between a and b also works with b — so I add b − a in one step rather than enumerating."',
 '"On success I move b down; on failure I move a up. Each c is one linear sweep, so O(n²) overall."',
 '"This counts duplicates as separate triplets — is that what you want?"',
 '"One thing I would guard: a + b can overflow int, so I would compare as a > c − b."',
], [
 """The script. Lead with the sort and its justification, because that single observation is the difference between a """
 """cubic answer and a quadratic one, and an interviewer who hears the justification knows you did not just remember the """
 """solution.""",
 """Then the counting step, stated as counting rather than enumerating, with the pointer rule and the complexity.""",
 """Then two short questions that show care: the duplicates clarification, and the overflow guard. Both take five seconds """
 """and both are the sort of thing that separates a candidate who has shipped code from one who has only solved """
 """puzzles.""",
])

sid = statement('Lesson 5.3', 'Sorting is not housekeeping. It deletes conditions and makes movement monotone.',
                'And when a question asks you to count, look for the step that counts a whole range at once.',
                kind='ok')
seg(sid, 0, """One line, in two halves. Sorting is not housekeeping — it deletes conditions and makes pointer movement """
            """monotone.""")
seg(sid, 1, """And when a question asks you to count rather than to list, look for the step that counts a whole range at """
            """once. That is usually where the factor of n you are looking for is hiding. Next is the chapter five recap, """
            """then we move to hashing and prefix sums.""")
