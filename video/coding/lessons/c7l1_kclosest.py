# -*- coding: utf-8 -*-
"""Chapter 7, Lesson 1 — Find K Closest Elements."""
from lib import *

lesson_header('7.1', 'Find K Closest Elements — binary search on the answer', 'Binary search on a window start',
              'High', 'Your list + the LinkedIn tagged set', '2026', 'High', 16,
              """Chapter seven, lesson one. Binary search and elimination — two reported questions that are really the same """
              """idea, which is throwing away half the candidates with a single comparison. We start with Find K Closest """
              """Elements, on your list and on the tagged set. There are three solutions to this problem, they are all """
              """correct, and they are not equally good. Knowing which one to reach for, and being able to say why, is the """
              """lesson.""")

sid = beat('Question', 'The problem, as they pose it',
           '<div class="qwrap"><div class="qtext" style="font-size:35px;line-height:1.4">'
           'Given a <b>sorted</b> array, an integer <b>k</b> and a target <b>x</b>, return the k elements closest to x, '
           '<b>sorted ascending</b>.<br><br>'
           'Closer means smaller |a &minus; x|. On a tie, the <b>smaller value</b> wins.</div></div>',
           """The question. Given a sorted array, a number k and a target x, return the k elements closest to x, in """
           """ascending order. Closer means a smaller absolute difference, and on a tie the smaller value wins. Note that """
           """tie-break — it is stated, it is easy to skip, and it changes the answer.""")

sid = beat('Key observation', 'The answer is a contiguous window',
           '<div class="bigidea">Because the array is sorted, the k closest elements are always <b>k consecutive '
           'elements</b>. There is no scenario where you take two from the left, skip one, and take one more.</div>'
           '<div style="margin-top:26px;font-size:30px;line-height:1.7">'
           'So the question is not &ldquo;which k elements?&rdquo; &mdash; it is <b>&ldquo;where does the window '
           'start?&rdquo;</b><br>'
           'One unknown, an integer between 0 and n&minus;k. That is a very different problem, and a much smaller one.'
           '</div>',
           """The observation that reframes everything. Because the array is sorted, the k closest elements are always k """
           """consecutive elements. There is no situation where you take two from the left, skip one, and take another — """
           """if you skipped an element, it was closer than one you took, which is a contradiction.""", step=0)
seg(sid, 1, """So the question is not which k elements. It is where does the window start. That is one unknown, an integer """
            """between zero and n minus k, and it is a far smaller problem than the one you were handed. Reducing a """
            """selection problem to a single index is the move worth remembering.""")

sid = compare('Three correct solutions. They are not equal.',
 ('Heap, or sort by distance', 'deny', 0,
  ['Push all n, keep the k best: **O(n log k)**',
   'Ignores the sortedness entirely',
   'Then you must sort the output again',
   'Correct, and it tells the interviewer you did not notice the array was sorted']),
 ('Two pointers from the ends', 'info', 1,
  ['Shrink from whichever end is further from x',
   '**O(n &minus; k)** &mdash; linear in what you discard',
   'Very easy to explain; no index arithmetic',
   'Good answer. Offer it first if binary search is not landing']))
seg(sid, 0, """Solution one: a heap, or sorting by distance. It is order n log k, it works, and it completely ignores the """
            """fact that the array is sorted — which is the one gift the problem gave you. An interviewer hearing this as """
            """your only answer learns that you did not notice.""")
seg(sid, 1, """Solution two: two pointers at the ends, repeatedly discarding whichever end is further from x until k remain. """
            """That is linear in the number you discard, it is genuinely easy to explain, and it has no fiddly index """
            """arithmetic. This is a good answer, and if the binary search is not coming to you in the room, offer this one """
            """confidently rather than fumbling.""")

sid = beat('The best solution', 'Binary search over the window start',
           '<div style="font-size:31px;line-height:1.7">'
           'Search for the start index <b>lo</b> in the range [0, n&minus;k]. At each candidate mid, compare the '
           '<b>two boundary candidates</b>:<br><br>'
           '<code>x &minus; a[mid]</code> &nbsp;versus&nbsp; <code>a[mid + k] &minus; x</code><br><br>'
           '<b>&bull;</b> If the left one is strictly larger, the window is too far left &rarr; move right.<br>'
           '<b>&bull;</b> Otherwise the window is fine where it is, or too far right &rarr; move left.<br><br>'
           '<b>O(log(n &minus; k) + k)</b> &mdash; the log to find the start, then k to copy the answer out.</div>',
           """And the best solution: binary search over the window start itself. You search for the start index in the """
           """range zero to n minus k. At each candidate, you compare the two boundary candidates — the element just inside """
           """the left edge and the element just outside the right edge.""", step=0)
seg(sid, 1, """Specifically, x minus the element at mid, against the element at mid plus k minus x.""")
seg(sid, 2, """If the left distance is strictly larger, this window reaches too far left and should slide right. Otherwise """
            """it is correctly placed or too far right, so you move left.""")
seg(sid, 3, """That gives logarithmic time to find the start plus k to copy the answer out. And notice what makes this """
            """subtle and worth practising: the comparison is not "is a of mid closer to x" — it is a comparison between """
            """the element you would drop and the element you would gain. Getting that phrasing right is the difference """
            """between writing this in two minutes and debugging it for ten.""")

D = Diagram('Why compare a[mid] with a[mid+k]')
vals = ['1','2','3','4','5']
ids = array_row(D, vals, x=280, y=170, cw=180, ch=110, step=0, kind='info')
D.label(280, 300, 'k = 4, x = 3 &rarr; the window start is somewhere in [0, 1]', kind='neutral', step=0, w=1400, size='m')
D.label(280, 380, 'mid = 0 &rarr; window would be [1,2,3,4]. Compare **x &minus; a[0] = 2** with **a[4] &minus; x = 2**.',
        kind='neutral', step=1, w=1600, size='m')
D.label(280, 460, 'Equal &rarr; not strictly larger &rarr; keep the left window. The tie-break (smaller value wins) '
                  'falls out of using a **strict** comparison.',
        kind='ok', step=2, w=1600, size='m')
D.label(280, 570, 'The comparison asks: *if I slide right, I lose a[mid] and gain a[mid+k]. Is that a good trade?*',
        kind='dp', step=3, w=1650, size='l')
D.label(280, 680, 'It never compares a[mid] to x directly &mdash; that would be the wrong question, because the '
                  'window is chosen as a whole.', kind='deny', step=4, w=1650, size='m')
sid = D.build()
seg(sid, 0, """A small example that exposes the tie-break. Array one through five, k is four, x is three, so the window start """
            """is either zero or one.""")
seg(sid, 1, """At mid zero, the window would be one, two, three, four. Compare x minus the first element, which is two, """
            """against the element at index four minus x, which is also two.""")
seg(sid, 2, """They are equal, so the left distance is not strictly larger, so we keep the left window — and that is exactly """
            """the stated tie-break, smaller values preferred. Notice the tie-break was not handled with a special case; it """
            """fell out of choosing a strict comparison. Say that in the interview, because it looks like luck otherwise.""")
seg(sid, 3, """The comparison is asking one question: if I slide right by one, I lose the element at mid and gain the """
            """element at mid plus k — is that trade good?""")
seg(sid, 4, """And it never compares the element at mid to x directly, which would be the wrong question, because the window """
            """is chosen as a whole rather than element by element.""")

CODE = '''public IList<int> FindClosestElements(int[] arr, int k, int x) {
    int lo = 0, hi = arr.Length - k;                     // the window START, not an element index

    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;                    // no overflow

        if (x - arr[mid] > arr[mid + k] - x)             // strict: ties keep the left window
            lo = mid + 1;                                // sliding right is a better trade
        else
            hi = mid;                                    // mid may be the answer - do not exclude it
    }

    var result = new List<int>(k);
    for (int i = lo; i < lo + k; i++) result.Add(arr[i]);
    return result;                                       // already ascending, since arr is sorted
}'''
code_slide('The C# implementation', CODE, [
 ('2', """The search space is the window start, from zero to n minus k inclusive. Writing that line correctly is most of """
         """the problem — say out loud that hi is a valid start index, not an element index, because that is the thing that """
         """confuses readers of this code."""),
 ('4-5', """Standard binary search, with mid computed as lo plus half the gap so it cannot overflow. That habit costs """
           """nothing and gets noticed."""),
 ('7-8', """The comparison. Strictly greater, which is what implements the tie-break: when the two distances are equal we """
           """do not slide right, so the smaller values win. One character carries the whole tie-break rule."""),
 ('9-10', """And the other branch sets hi to mid rather than mid minus one, because mid is still a candidate answer. That """
            """asymmetry is the classic binary-search bug; the rule I use is that whichever side might still contain the """
            """answer keeps its endpoint."""),
 ('13-16', """Then copy out k elements from the found start. They are already ascending because the source array is """
             """sorted, so no sort call is needed — worth saying, since the problem explicitly asks for sorted output and a """
             """nervous candidate adds a redundant sort."""),
])

sid = cards('Edge cases and clarifications', [
 (0, 'k equals n', 'The whole array. hi starts at 0, the loop never runs, and it works &mdash; check it rather than special-casing.', 'ok'),
 (0, 'x outside the array range', 'The window pins to one end. Both branches handle it; a good two-second test.', 'ok'),
 (1, 'Duplicates', 'Harmless here &mdash; the window is by position, not by value.', 'ok'),
 (1, 'The tie-break', 'Stated in the problem and easy to miss. Read it back to the interviewer.', 'deny'),
 (2, 'Overflow in the distance', 'x − arr[mid] can overflow with extreme values. Mention it; use long if they care.', 'shared'),
 (2, '"Unsorted input?"', 'Then it is a different problem: quickselect on distance, O(n) average, and you sort the k at the end.', 'shared'),
], cols=2)
seg(sid, 0, """Edge cases. k equals n gives the whole array: hi starts at zero, the loop never executes, and the copy returns """
            """everything. Check that rather than adding a special case. x outside the array range pins the window to one """
            """end, and both branches handle it naturally.""")
seg(sid, 1, """Duplicates are harmless because the window is chosen by position rather than by value. And the tie-break is """
            """stated in the problem and is the thing most candidates skim — read it back to the interviewer, which takes """
            """three seconds and prevents a wrong answer.""")
seg(sid, 2, """Distance subtraction can overflow with extreme values; mention it. And a good question to ask: what if the """
            """input were not sorted? Then this is a completely different problem — quickselect on distance, linear on """
            """average, with a sort of the k results at the end. Knowing that the sortedness is load-bearing is the point """
            """of asking.""")

followups(
 ['"Do it without binary search" — two pointers from the ends, O(n − k); have this ready as your fallback',
  '"What if the array is not sorted?" — quickselect by distance, O(n) average, then sort the k',
  '"Return the indices instead of the values" — you already have the start index'],
 ['"The array is on disk / too large for memory" — binary search is ideal: O(log n) seeks rather than a full scan',
  '"Many queries with different x" — each is still O(log n + k); if k is large, consider returning a cursor instead of copying',
  '"k closest in a stream" — a bounded max-heap by distance, size k, O(log k) per element; the sorted-array trick is gone'],
 """Follow-ups. Doing it without binary search is the two-pointer answer, linear in what you discard, and you should have """
 """it ready as a fallback rather than as an afterthought. Unsorted input turns it into quickselect. And returning indices """
 """rather than values is free, because the start index is exactly what your search produced.""",
 """At staff level, notice that this problem is unusually friendly to real systems. If the array is on disk, binary search """
 """is exactly what you want — logarithmically many seeks rather than a full scan — and saying that connects the technique """
 """to why database indexes are shaped the way they are. Many queries with different targets stay cheap. And k closest in """
 """a stream is a genuinely different problem: a bounded max-heap by distance, because you have lost the sortedness that """
 """everything here depended on.""")

interview_script([
 '"Because the array is sorted, the answer is k consecutive elements — so the only unknown is where the window starts."',
 '"That turns it into a binary search over the start index, from 0 to n − k."',
 '"At each candidate I compare the element I would drop with the element I would gain: x − a[mid] against a[mid+k] − x."',
 '"A strict comparison implements the stated tie-break, so equal distances keep the smaller values."',
 '"O(log(n−k)) to find the start plus O(k) to copy out. The output is already ascending."',
 '"If the binary search feels risky, the two-pointer version from both ends is O(n−k) and I can write that instead."',
], [
 """The script. Lead with the contiguity argument, because that is the insight, and the interviewer wants to hear it """
 """before any search appears.""",
 """Then frame the search as being over the start index, and state the comparison in terms of drop and gain rather than """
 """in terms of distance to x — that phrasing is what keeps the code correct.""",
 """Mention that the tie-break falls out of strictness, give the complexity, and keep the two-pointer version in your back """
 """pocket. Offering an alternative you can definitely write, while attempting the better one, is a professional move """
 """rather than a hedge.""",
])

sid = statement('Lesson 7.1', 'Do not search for the elements. Search for the index that defines them.',
                'Whenever the answer is a contiguous block of a sorted array, the real unknown is one number.',
                kind='ok')
seg(sid, 0, """One line. Do not search for the elements — search for the index that defines them.""")
seg(sid, 1, """Whenever the answer is a contiguous block of a sorted array, the real unknown is a single number, and """
            """single numbers are what binary search is for. Next lesson: Find the Celebrity, where the elimination is even """
            """sharper — one question removes one candidate permanently — and where the interesting constraint is the cost """
            """of the API call itself.""")
