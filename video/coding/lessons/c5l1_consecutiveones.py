# -*- coding: utf-8 -*-
"""Chapter 5, Lesson 1 — Max Consecutive Ones III."""
from lib import *

lesson_header('5.1', 'Max Consecutive Ones III — the window that never shrinks', 'Sliding window',
              'High', 'Your list + the LinkedIn tagged set', '2026', 'High', 15,
              """Chapter five, lesson one. Sliding window, and we start with Max Consecutive Ones Three, which is on your own """
              """list and on the LinkedIn tagged set. I want to be honest about why this chapter exists at a Staff level. """
              """The window is not hard. What is hard is that under interview pressure people reach for it before they have """
              """stated what the window means, and then they spend ten minutes debugging a loop whose invariant they never """
              """wrote down. This lesson is about the invariant, and the code is four lines.""")

sid = beat('Question', 'The problem, as they pose it',
           '<div class="qwrap"><div class="qtext" style="font-size:36px;line-height:1.4">'
           'Given a binary array and an integer <b>k</b>, return the length of the longest run of 1s you can get '
           'if you may flip <b>at most k</b> zeros to ones.</div></div>',
           """The question. A binary array and a number k. Return the length of the longest run of ones you can get if you """
           """are allowed to flip at most k zeros to ones. That is the whole statement, and it is deceptively friendly.""")

think('What does "flip at most k zeros" actually mean about a subarray?', 25,
      """Pause, and answer a translation question rather than an algorithm question. Forget flipping for a moment. What """
      """property does a subarray need to have in order to be a legal answer?""",
      """Here is the reframing, and it is the whole lesson.""")

sid = beat('Key observation', 'Do not think about flipping. Think about a window with a budget.',
           '<div class="bigidea">A subarray is a valid answer if and only if it contains <b>at most k zeros</b>. '
           'The flipping never has to happen.</div>'
           '<div style="margin-top:26px;font-size:30px;line-height:1.7">'
           'So the question becomes: <b>what is the longest window containing at most k zeros?</b> '
           'That is a sliding window with a counter, and the counter is the only state you need.</div>',
           """Do not think about flipping. A subarray is a valid answer if and only if it contains at most k zeros — because """
           """if it has at most k zeros you can flip them all, and if it has more you cannot. The flipping never actually """
           """happens in your code.""", step=0)
seg(sid, 1, """So the question becomes: what is the longest window containing at most k zeros? That is a sliding window with """
            """a counter, and that counter is the only state you need. Translating a problem into a window with a budget is """
            """the single most reusable move in this chapter — you will do exactly the same thing with at most k distinct """
            """characters, at most k edits, at most k replacements.""")

D = Diagram('The window on [1,1,0,0,1,1,1,0,1] with k = 2')
vals = ['1','1','0','0','1','1','1','0','1']
ids = array_row(D, vals, x=130, y=180, cw=170, ch=110, step=0, kind='info')
D.label(130, 320, 'right expands every step. zeros counts the 0s **inside** the window.',
        kind='neutral', step=0, w=1600, size='m')
hl_cells(D, ids[0:6], x=130, y=180, cw=170, ch=110, marks={5: 1}, kind='ok')
D.label(130, 420, 'right = 5 &rarr; window [0..5] holds two 0s. Budget spent exactly &mdash; still legal. Length **6**.',
        kind='ok', step=1, w=1700, size='m')
D.label(130, 500, 'right = 7 &rarr; a third 0 arrives. **Now** the window is illegal.',
        kind='deny', step=2, w=1700, size='m')
D.label(130, 580, 'So left advances &mdash; but only far enough to drop **one** zero, not to rebuild the window.',
        kind='ok', step=3, w=1700, size='m')
D.label(130, 680, 'The window **never shrinks below the best seen**: each step moves right once and left at most once. '
                  'That is why the whole thing is O(n) with two pointers and no nesting.',
        kind='dp', step=4, w=1700, size='l')
sid = D.build()
seg(sid, 0, """Let us walk it. The array is one, one, zero, zero, one, one, one, zero, one, and k is two. The right pointer """
            """expands every step, and we count the zeros currently inside the window.""")
seg(sid, 1, """At right equals five the window holds two zeros. The budget is spent exactly, which is still legal, and the """
            """length is six.""")
seg(sid, 2, """At right equals seven a third zero arrives, and now the window is illegal.""")
seg(sid, 3, """So the left pointer advances — but only far enough to drop one zero, not far enough to rebuild the window from """
            """scratch. That restraint is what keeps the algorithm linear.""")
seg(sid, 4, """And here is the property worth saying out loud: the window never shrinks below the best length seen so far. """
            """Each step moves right once and left at most once, so each index is visited at most twice, and the whole """
            """algorithm is linear with two pointers and no nesting.""")

sid = compare('Two ways to write it &mdash; know both, pick one',
 ('Shrink with a while loop', 'info', 0,
  ['`while (zeros > k) { if (a[left]==0) zeros--; left++; }`',
   'The window is **always legal**',
   '`best = max(best, right-left+1)` each step',
   'Easier to explain; slightly more code']),
 ('Shrink with a single if &mdash; the &ldquo;never shrink&rdquo; trick', 'ok', 1,
  ['`if (zeros > k) { if (a[left]==0) zeros--; left++; }`',
   'The window may stay **illegal**, but never gets shorter',
   '`return n - left` at the end',
   'Four lines. Explain it or do not use it']))
seg(sid, 0, """There are two standard ways to write this and you should know both. The first shrinks with a while loop, so the """
            """window is always legal, and you take the maximum length at every step. It is slightly longer and much easier """
            """to explain.""")
seg(sid, 1, """The second replaces the while with a single if. The window may temporarily be illegal, but it never gets """
            """shorter, so at the end its length is the answer and you can simply return n minus left. It is four lines and """
            """it looks like magic. My advice: use it only if you can explain why it works, because an interviewer who asks """
            """"why is the if enough?" and gets silence has learned something worse than if you had written the while. I """
            """would write the while version and then mention the trick.""")

CODE = '''public int LongestOnes(int[] nums, int k) {
    int left = 0, zeros = 0, best = 0;

    for (int right = 0; right < nums.Length; right++) {
        if (nums[right] == 0) zeros++;              // the window's budget is spent here

        while (zeros > k) {                         // restore the invariant: at most k zeros
            if (nums[left] == 0) zeros--;
            left++;                                 // left only ever moves forward -> O(n) total
        }

        best = Math.Max(best, right - left + 1);    // window is legal here, by construction
    }
    return best;
}'''
code_slide('The C# implementation', CODE, [
 ('2', """Three variables: the left edge, the number of zeros currently inside, and the best length seen. If you can name """
         """the three before writing the loop, the loop writes itself."""),
 ('4-5', """Expand right every step. A zero entering the window spends budget. Note there is no flipping anywhere in this """
           """code — that is the translation paying off."""),
 ('7-10', """Restore the invariant. While there are too many zeros, walk left forward, refunding budget when the element """
            """leaving is a zero. Left only ever moves forward, which is why two nested-looking loops are still linear — """
            """say that explicitly, because it looks quadratic to a reader who is not paying attention."""),
 ('12', """And here the window is legal by construction, so its length is a candidate answer. The comment matters more than """
          """the line: the reason you can take the maximum here without checking anything is that the while loop above """
          """guaranteed it."""),
 ('14', """Return the best. Linear time, constant space, and every variable in it has a one-sentence meaning."""),
])

sid = cards('Edge cases and clarifications', [
 (0, 'k = 0', 'The longest run of existing 1s. The same code handles it; say so rather than special-casing.', 'ok'),
 (0, 'k &ge; number of zeros', 'The whole array. Again, no special case needed &mdash; but check that your code returns n, not n&minus;1.', 'ok'),
 (1, 'All zeros', 'The answer is min(k, n). A good three-second test of your loop.', 'shared'),
 (1, 'Empty array', 'Return 0. Ask whether it can happen; the constraint list usually says no.', 'shared'),
 (2, '&ldquo;At most k&rdquo; vs &ldquo;exactly k&rdquo;', 'The wording says at most. If they say exactly, the answer changes and the window is no longer monotone &mdash; ask.', 'deny'),
 (2, 'Return the window, not the length', 'Keep the left index of the best window. One extra variable, asked often.', 'ok'),
], cols=2)
seg(sid, 0, """Edge cases. k equals zero gives you the longest run of existing ones, and the same code handles it — say that """
            """rather than adding a special case, because unnecessary special cases are themselves a smell. k greater than """
            """or equal to the number of zeros gives the whole array, and it is worth checking your off-by-one returns n """
            """rather than n minus one.""")
seg(sid, 1, """All zeros gives the minimum of k and n, which is a good three-second test of your loop. Empty array returns """
            """zero, and ask whether it can happen.""")
seg(sid, 2, """Two clarifications worth raising. At most k versus exactly k — the wording says at most, and if they change it """
            """to exactly, the problem stops being monotone and the window approach needs rethinking, so ask rather than """
            """assume. And they often follow up by asking for the window itself rather than its length, which is one extra """
            """variable if you think of it now and a rewrite if you do not.""")

sid = beat('Why this is the template for a whole family', 'Same code, different budget',
           '<div style="font-size:30px;line-height:1.7">'
           'Change what the counter counts and you have solved a different reported question:<br><br>'
           '<b>&bull;</b> zeros in the window &le; k &rarr; <i>Max Consecutive Ones III</i><br>'
           '<b>&bull;</b> distinct characters &le; k &rarr; <i>longest substring with k distinct</i><br>'
           '<b>&bull;</b> character-frequency deficit &le; k &rarr; <i>longest repeating character replacement</i><br>'
           '<b>&bull;</b> sum &le; target &rarr; <i>shortest/longest subarray with a sum bound</i><br><br>'
           'The window is never the hard part. <b>Choosing the counter is.</b></div>',
           """Before we finish, notice that this is a template rather than a problem. Change what the counter counts and you """
           """have solved a different question with the same fifteen lines.""", step=0)
seg(sid, 1, """Zeros in the window bounded by k is this problem. Distinct characters bounded by k is the longest substring """
            """with k distinct characters. A character-frequency deficit bounded by k is longest repeating character """
            """replacement. A running sum bounded by a target is the subarray-sum family. The window is never the hard part. """
            """Choosing the counter is, and that is the sentence to carry into the interview.""")

followups(
 ['"Return the actual window" — track the left index whenever you improve the best',
  '"What if flips are expensive and you want the fewest?" — different question: minimise flips for a target length, binary search on length',
  '"Stream the array — you cannot go back" — the window still works; left never rewinds, so it is streaming-safe'],
 ['"The array is 10⁹ long and mostly ones" — run-length encode it; the window then slides over runs, not elements',
  '"Generalise to at most k replacements of any value" — the counter becomes a frequency map; same skeleton',
  '"Parallelise it" — split into chunks with overlapping boundaries; the merge needs the best prefix and suffix run per chunk'],
 """Follow-ups. Returning the actual window is one tracked index. If they ask for the fewest flips to reach a target length """
 """instead, that is genuinely a different question — you binary search on the length and test feasibility with this same """
 """window. And a nice one: if the array streams and you cannot go back, this still works, because the left pointer never """
 """rewinds. Saying "this algorithm is streaming-safe" is a strong throwaway line.""",
 """At staff level, a billion elements that are mostly ones invites run-length encoding, after which the window slides over """
 """runs rather than elements. Generalising from zeros to any value replaces the counter with a frequency map and leaves """
 """the skeleton untouched. And parallelising it is a good systems answer: chunk it with overlapping boundaries, and the """
 """merge needs each chunk's best prefix and suffix run — which is the same reasoning you would use in a MapReduce job.""")

interview_script([
 '"I will restate it: a subarray is valid if it has at most k zeros. The flipping never has to happen."',
 '"So this is the longest window with at most k zeros — a sliding window with a counter."',
 '"Expand right, count zeros. When the count exceeds k, advance left until it does not."',
 '"Left only moves forward, so although there are two loops, each index is touched at most twice — O(n)."',
 '"k = 0 and k larger than the number of zeros both fall out of the same code; I would not special-case them."',
 '"If you want the window itself rather than its length, I would track the left index of the best window."',
], [
 """The script, and the first line is the one that matters: restate the problem as a property of a window before you write """
 """anything. That translation is what you are being scored on; the loop is not.""",
 """Then the mechanics in two sentences, followed immediately by the complexity argument — because two nested loops """
 """looks quadratic, and pre-empting that question shows you know why it is not.""",
 """Close by naming the degenerate cases and offering the variant they usually ask for next. Offering the follow-up before """
 """they ask it is one of the cheapest ways to sound senior.""",
])

sid = statement('Lesson 5.1', 'The window is never the hard part. Choosing the counter is.',
                'Translate the constraint into "at most k of something inside the window", and the code is fifteen lines.',
                kind='ok')
seg(sid, 0, """One line. The window is never the hard part; choosing the counter is.""")
seg(sid, 1, """Translate the constraint into "at most k of something inside the window" and the code is fifteen lines you """
            """already know. Next lesson: Valid Palindrome Two, where two pointers move toward each other instead of """
            """chasing, and where the interesting part is what you do at the first mismatch.""")
