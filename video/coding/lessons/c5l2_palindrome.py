# -*- coding: utf-8 -*-
"""Chapter 5, Lesson 2 — Valid Palindrome II."""
from lib import *

lesson_header('5.2', 'Valid Palindrome II — one deletion, two pointers', 'Two pointers',
              'High', 'Reported with a k-edits extension', '2026', 'Medium', 13,
              """Chapter five, lesson two. Valid Palindrome Two: can this string be made a palindrome by deleting at most one """
              """character? It was reported with an extension to k edits, and I will be straight with you about the """
              """confidence — the base question is well attested on the tagged set, the k-edits extension comes from a """
              """single write-up, so treat the extension as likely rather than certain. It is worth preparing anyway, """
              """because the jump from one to k is exactly the jump from a clever trick to a general method, and """
              """interviewers love that seam.""")

sid = beat('Question', 'The problem, as they pose it',
           '<div class="qwrap"><div class="qtext" style="font-size:36px;line-height:1.4">'
           'Given a string s, return true if it can be a palindrome after deleting <b>at most one</b> character.'
           '</div></div>',
           """The question. Given a string, return true if it can be a palindrome after deleting at most one character. """
           """That is it.""")

think('Two pointers from both ends. What do you do at the first mismatch?', 25,
      """Pause. Two pointers walking inward is obvious. The interesting question — and the only question — is what you do """
      """at the first mismatch. Think about how many possibilities there really are.""",
      """Here is the observation that makes it small.""")

sid = beat('Key observation', 'At the first mismatch there are exactly two choices, and you can test both',
           '<div class="bigidea">Walk inward while characters match. At the first mismatch, either you delete the '
           '<b>left</b> character or you delete the <b>right</b> one. Nothing else can help.</div>'
           '<div style="margin-top:26px;font-size:30px;line-height:1.7">'
           'And once you have used your one deletion, the remainder must be a <b>plain palindrome</b> &mdash; no more '
           'choices. So each branch is a single linear check, and the whole thing stays O(n).</div>',
           """Walk inward while the characters match. At the first mismatch you have exactly two options: delete the """
           """character on the left, or delete the one on the right. Deleting anything else cannot help, because these two """
           """characters differ and they must either match each other or one of them must go.""", step=0)
seg(sid, 1, """And here is the part that keeps it linear: once you have spent your one deletion, the remainder must be a plain """
            """palindrome, with no further choices. So each of the two branches is a single linear check. Two branches, """
            """each linear, and only one mismatch point ever triggers them — so the whole thing is linear, not quadratic.""")

D = Diagram('"abcdba" — the first mismatch and the two branches')
chars = ['a','b','c','d','b','a']
ids = array_row(D, chars, x=200, y=170, cw=180, ch=110, step=0, kind='info')
D.label(200, 300, 'left and right walk inward: a=a ✓, b=b ✓', kind='ok', step=0, w=1400, size='m')
hl_cells(D, ids[2:4], x=200, y=170, cw=180, ch=110, marks={2: 1, 3: 1}, kind='deny')
D.label(200, 380, 'Mismatch at c vs d. One deletion left. **Two branches:**',
        kind='deny', step=1, w=1400, size='m')
D.box('b1', 200, 460, 640, 170, 'Delete the left (c)', 'Is "db" a palindrome? **No**',
      kind='deny', step=2)
D.box('b2', 920, 460, 640, 170, 'Delete the right (d)', 'Is "cb" a palindrome? **No**',
      kind='deny', step=3)
D.label(200, 670, 'Both fail &rarr; return false. For "abcba<b>a</b>" one branch would succeed and you return true.',
        kind='neutral', step=4, w=1600, size='m')
D.label(200, 760, 'You never recurse. The deletion budget is 1, and spending it removes all remaining freedom.',
        kind='dp', step=5, w=1600, size='l')
sid = D.build()
seg(sid, 0, """Take a b c d b a. The pointers walk inward: a matches a, b matches b.""")
seg(sid, 1, """Then c against d — a mismatch, with one deletion still available. Two branches.""")
seg(sid, 2, """Branch one: delete the left character, the c, and ask whether the remaining span is a palindrome. It is not.""")
seg(sid, 3, """Branch two: delete the right character, the d, and ask the same question. Also not. So we return false.""")
seg(sid, 4, """On a string where one branch succeeds, you return true immediately — you do not need to test the other.""")
seg(sid, 5, """And notice what you never do: recurse. The budget is one, and spending it removes all remaining freedom. That """
            """is precisely why this problem is easy and why the k version, which we will get to, is not.""")

CODE = '''public bool ValidPalindrome(string s) {
    int i = 0, j = s.Length - 1;

    while (i < j) {
        if (s[i] != s[j])                                   // the one and only decision point
            return IsPalindrome(s, i + 1, j)                // delete the left character
                || IsPalindrome(s, i, j - 1);               // or delete the right one
        i++; j--;
    }
    return true;                                            // already a palindrome: 0 deletions used
}

private static bool IsPalindrome(string s, int i, int j) {
    while (i < j) {
        if (s[i] != s[j]) return false;
        i++; j--;
    }
    return true;
}'''
code_slide('The C# implementation', CODE, [
 ('2-3', """Two pointers at the ends. The loop condition is i less than j, which handles both odd and even lengths without """
           """a special case — the middle character of an odd-length string is never compared with itself, and it never """
           """needs to be."""),
 ('5-8', """The whole problem is these four lines. At the first mismatch, try both deletions with the helper. The """
           """short-circuit or means the second check only runs if the first fails, and either way this branch executes at """
           """most once in the entire call."""),
 ('9-11', """Otherwise step inward. Reaching the end means the string was already a palindrome and we used zero deletions, """
            """which the at-most-one contract allows — worth saying out loud, because "at most" versus "exactly" is a """
            """clarification I would raise."""),
 ('14-20', """And the helper is an ordinary palindrome check on a range. Writing it as a named helper rather than inlining """
             """it is deliberate: it makes the main function read exactly like the reasoning you just explained, which is """
             """the modularity the Staff module scores."""),
])

sid = table('Complexity, and the objection you should pre-empt',
 ['', 'Cost', 'Why'],
 [(0, ['Time', 'O(n)', 'The outer walk is O(n); the two helper checks run <b>at most once each</b>, and each is O(n)'], None),
  (1, ['&ldquo;Isn&rsquo;t that O(n&sup2;)?&rdquo;', 'No', 'Because the branch is reached once. After it, we return &mdash; there is no second mismatch to handle'], None),
  (2, ['Space', 'O(1)', 'Indices only. No substring allocation &mdash; <b>do not</b> write s.Substring here'], None)],
 widths=[24, 14, 62])
seg(sid, 0, """Complexity. Linear: the outer walk is linear, and the two helper checks each run at most once.""")
seg(sid, 1, """Pre-empt the objection, because an interviewer may well raise it: is this not quadratic? No — the branch is """
            """reached once, and after it we return. There is no second mismatch to handle, so there is no nesting.""")
seg(sid, 2, """Space is constant, and there is one thing to be careful about: pass indices, do not take substrings. Calling """
            """Substring here allocates a copy and quietly makes your space linear. That is a small detail, and small """
            """details about allocation are exactly what an infrastructure interviewer notices.""")

sid = beat('The reported extension', 'Now allow k deletions',
           '<div style="font-size:30px;line-height:1.7">'
           'The trick <b>dies</b> at k &ge; 2. With two deletions you can delete on the left, then later on the right, '
           'and the branches multiply.<br><br>'
           'The general answer: <b>the minimum number of deletions to make s a palindrome is '
           'n &minus; LPS(s)</b>, where LPS is the longest palindromic subsequence &mdash; which is the longest common '
           'subsequence of s and its reverse. So:<br><br>'
           '<b>&bull;</b> Compute LPS with the standard O(n&sup2;) DP.<br>'
           '<b>&bull;</b> Answer is <code>n &minus; LPS &le; k</code>.<br>'
           '<b>&bull;</b> Or, if k is small, an O(n&middot;k) two-pointer recursion with a deletion budget.</div>',
           """Now the extension that was reported: allow k deletions. And the first thing to say is that the trick dies. """
           """With two deletions you can delete once on the left and later once on the right, so the branches multiply and """
           """the clean two-branch argument no longer holds.""", step=0)
seg(sid, 1, """The general answer is worth memorising because it is elegant. The minimum number of deletions needed to make a """
            """string a palindrome is n minus the length of its longest palindromic subsequence. And the longest """
            """palindromic subsequence is just the longest common subsequence of the string and its reverse.""")
seg(sid, 2, """So you compute that with the standard quadratic dynamic program and check whether n minus it is at most k. """
            """Alternatively, if k is small, you can write the two-pointer recursion with a budget, which costs n times k """
            """and is often the better answer in an interview because it is a three-line change to the code you already """
            """wrote. Offer both and let them choose — that is a stronger answer than picking one silently.""")

followups(
 ['"Now allow k deletions" — reported; n − LPS, or an O(n·k) budgeted recursion',
  '"Return the resulting palindrome, not just true/false" — carry the branch that succeeded',
  '"What about deletions from only one side?" — then it is a suffix/prefix check, strictly easier'],
 ['"Unicode, not ASCII" — compare by grapheme cluster, not by char; "é" may be two code units in C#',
  '"Case and punctuation insensitive" — that is Valid Palindrome I\'s filter; do it with two skipping pointers, not by building a cleaned copy',
  '"A 10 GB string on disk" — two file handles reading from both ends; the algorithm is already streaming-friendly in both directions'],
 """Follow-ups. The k extension we just covered. Returning the actual palindrome rather than a boolean means carrying the """
 """branch that succeeded, which is a small change if you thought about it in advance. And if deletions are allowed from """
 """one side only, the problem collapses to a prefix or suffix check and gets easier — a good sanity question to ask, """
 """because it tells you whether they meant what you assumed.""",
 """The staff-level follow-ups here are about text, which suits LinkedIn. Unicode is the real one: in C sharp a character """
 """is a UTF-sixteen code unit, so an accented letter or an emoji can be two of them, and a naive two-pointer walk splits """
 """them. Say that you would compare by grapheme cluster. Case and punctuation insensitivity should be done with skipping """
 """pointers rather than by building a cleaned copy, which would cost linear space. And a ten-gigabyte string is a nice """
 """systems answer: two file handles reading inward from both ends, because this algorithm never needs random access.""")

interview_script([
 '"Two pointers inward. The only decision is at the first mismatch."',
 '"There, I either delete the left character or the right one — nothing else can help, since those two differ."',
 '"After spending the single deletion, the rest must be a plain palindrome, so each branch is one linear check."',
 '"That keeps it O(n), not O(n²), because the branch is reached at most once."',
 '"I will pass indices rather than substrings so it stays O(1) space."',
 '"If you extend it to k deletions, the trick breaks — then it is n − longest palindromic subsequence, or an O(n·k) budgeted recursion."',
], [
 """The script. Name the single decision point immediately — that framing is what makes this problem sound easy when you """
 """explain it, and it is what the interviewer wants to hear before any code exists.""",
 """Give the two-branch argument with its justification, then the complexity claim with the reason the nesting does not """
 """happen, then the allocation detail.""",
 """And volunteer the k extension yourself. It was reported as a follow-up, so raising it first is both accurate and """
 """confident — you are showing that you know where this problem generalises and where the clean trick stops working.""",
])

sid = statement('Lesson 5.2', 'When the budget is 1, you can afford to try every branch.',
                'The technique only survives while the branching factor stays tiny. Know exactly where it breaks — that is the follow-up.',
                kind='ok')
seg(sid, 0, """One line. When the budget is one, you can afford to try every branch exhaustively.""")
seg(sid, 1, """The technique survives only while the branching factor stays tiny, and knowing exactly where it breaks is what """
            """the follow-up is about. Next lesson: Valid Triangle Number, where sorting first turns a triple loop into a """
            """double one, and where one line of arithmetic replaces an entire inner scan.""")
