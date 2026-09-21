# -*- coding: utf-8 -*-
"""Chapter 8, Lesson 1 — Letter Combinations of a Phone Number."""
from lib import *

lesson_header('8.1', 'Letter Combinations — backtracking, and making it lazy', 'Backtracking · generators',
              'High', 'Your list + the LinkedIn tagged set', '2026', 'High', 16,
              """Chapter eight, lesson one. Letter Combinations of a Phone Number, which is on your own list and on the """
              """LinkedIn tagged set. The base problem is one of the easiest questions in this course — you will write it """
              """in four minutes. So I am going to spend most of the lesson on the two follow-ups that actually get asked, """
              """because on an easy question, the follow-ups are the interview. The base solution is the ticket to the """
              """conversation, not the conversation.""")

sid = beat('Question', 'The problem, as they pose it',
           '<div class="qwrap"><div class="qtext" style="font-size:35px;line-height:1.4">'
           'On an old phone keypad, 2 maps to <i>abc</i>, 3 to <i>def</i>, and so on up to 9.<br><br>'
           'Given a string of digits, return <b>every</b> letter combination the number could spell. '
           'Any order. An empty input returns an empty list.</div></div>',
           """The question. On an old phone keypad, two maps to a, b, c, three maps to d, e, f, and so on up to nine. Given """
           """a string of digits, return every letter combination the number could spell, in any order. Empty input returns """
           """an empty list — and that empty case is the first thing people get wrong, so note it now.""")

sid = beat('Understanding the shape', 'This is a tree, and you are listing its leaves',
           '<div style="font-size:31px;line-height:1.7">'
           'Each digit is a <b>level</b>. Each letter on that digit is a <b>branch</b>. A complete combination is a '
           '<b>path from the root to a leaf</b>.<br><br>'
           'So the count is the product of the branch factors: <b>3&#8319; or 4&#8319;</b> depending on the digits. '
           'For 4 digits that is 81 to 256. For 10 digits, up to a million.<br><br>'
           '<b>The output itself is exponential</b> &mdash; which means no algorithm can be better than exponential, '
           'and that is worth saying before you start.</div>',
           """Understand the shape before writing anything. Each digit is a level of a tree, each letter on that digit is a """
           """branch, and a complete combination is a path from the root to a leaf. You are listing the leaves.""",
           step=0)
seg(sid, 1, """So the count is the product of the branch factors: three or four to the power of n depending on which digits """
            """appear. Four digits gives you between eighty-one and two hundred and fifty-six results. Ten digits gives up """
            """to a million.""")
seg(sid, 2, """And here is the sentence to say before you start coding: the output itself is exponential, so no algorithm """
            """can be better than exponential. That frames your complexity answer correctly and it pre-empts the "can you """
            """do better" question — you can only do better on memory, not on time, which is exactly where the second """
            """follow-up goes.""")

D = Diagram('The tree for "23"')
tree(D, {
  'r':  (0, 0, 'start'),
  'a':  (1, -1, '"a"'), 'b': (1, 0, '"b"'), 'c': (1, 1, '"c"'),
  'ad': (2, -1.6, 'ad'), 'ae': (2, -1.0, 'ae'), 'af': (2, -0.4, 'af'),
  'bd': (2, 0.2, 'bd'), 'be': (2, 0.8, 'be'), 'bf': (2, 1.4, 'bf'),
}, [('r','a'), ('r','b'), ('r','c'), ('a','ad'), ('a','ae'), ('a','af'),
    ('b','bd'), ('b','be'), ('b','bf')],
   x=760, y=130, dx=230, dy=190, step=0, kind='dp', node_w=104, node_h=64)
D.label(120, 620, 'Digit 2 &rarr; three branches. Digit 3 &rarr; three more from each. Leaves = answers.',
        kind='neutral', step=1, w=1700, size='m')
D.label(120, 700, 'Backtracking = walk down appending a letter, and **remove it again** on the way back up.',
        kind='ok', step=2, w=1700, size='l')
D.label(120, 790, 'One buffer, reused for every path. That is why the extra space is O(n), not O(4&#8319;).',
        kind='dp', step=3, w=1700, size='m')
sid = D.build()
seg(sid, 0, """Here is the tree for the digits two then three, with the c branch left unexpanded so it fits on screen.""")
seg(sid, 1, """Digit two gives three branches. Digit three gives three more from each of those. The leaves are your answers.""")
seg(sid, 2, """And backtracking is exactly what the picture suggests: walk down appending a letter, and remove it again on """
            """the way back up.""")
seg(sid, 3, """That remove-on-the-way-up is why you use one buffer for every path, and it is why your extra space is linear """
            """in the number of digits rather than exponential. Say that when you are asked about space, because people """
            """conflate the output size with the working memory.""")

CODE = '''private static readonly string[] Pad = {
    "", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"
};

public IList<string> LetterCombinations(string digits) {
    var result = new List<string>();
    if (string.IsNullOrEmpty(digits)) return result;      // empty input -> empty list, not [""]

    Walk(digits, 0, new StringBuilder(digits.Length), result);
    return result;
}

private static void Walk(string digits, int i, StringBuilder path, List<string> result) {
    if (i == digits.Length) {                             // a leaf: one complete combination
        result.Add(path.ToString());
        return;
    }

    foreach (char c in Pad[digits[i] - '0']) {
        path.Append(c);                                   // choose
        Walk(digits, i + 1, path, result);                // explore
        path.Length--;                                    // un-choose: this is the "backtrack"
    }
}'''
code_slide('The C# implementation', CODE, [
 ('1-3', """The keypad as a lookup table, with empty strings at zero and one so the digit itself is the index. Small """
           """detail, but it removes an arithmetic adjustment from the hot path and makes the code read better."""),
 ('5-11', """The entry point. The empty-input guard is not decoration: without it you return a list containing one empty """
            """string, which is a different answer and a real test case. Pre-sizing the buffer to the digit count costs """
            """nothing."""),
 ('13-17', """The recursion's base case is reaching the end of the digits, at which point the buffer holds one complete """
             """combination and we materialise it. Note this is the only place we allocate a string."""),
 ('19-23', """And the three lines that are the whole technique: choose, explore, un-choose. I say those three words out """
             """loud as I write them, every time, because that rhythm is what keeps backtracking code correct — and the """
             """un-choose line is the one people forget, which silently produces garbage rather than crashing."""),
])

sid = table('Complexity, stated carefully',
 ['Measure', 'Cost', 'The nuance'],
 [(0, ['Time', 'O(4&#8319; &middot; n)', 'Up to 4&#8319; leaves, each costing n to copy into a string'], None),
  (1, ['Output space', 'O(4&#8319; &middot; n)', 'Unavoidable &mdash; it <b>is</b> the answer'], None),
  (2, ['Working space', 'O(n)', 'One buffer plus the recursion stack. Do not quote the output size here'], None),
  (3, ['Can you do better?', 'Not in time', 'The output is exponential. You can only improve <b>memory</b> &mdash; which is the next follow-up'], None)],
 widths=[22, 20, 58])
seg(sid, 0, """Complexity, and be careful here because it is easy to say something sloppy. Time is four to the n times n: up """
            """to four to the n leaves, each costing n to copy into a string.""")
seg(sid, 1, """Output space is the same, and it is unavoidable, because it is the answer.""")
seg(sid, 2, """But working space is only linear — one buffer plus the recursion stack. Do not quote the output size as your """
            """space complexity; distinguish the two.""")
seg(sid, 3, """And when they ask whether you can do better: not in time, because the output is exponential. You can only """
            """improve memory, and that is precisely the follow-up we are about to do.""")

sid = beat('Follow-up 1', 'Make it lazy: do not build the list at all',
           '<div style="font-size:30px;line-height:1.7">'
           'The caller often wants <b>the first few</b> combinations, or wants to filter them &mdash; and building a '
           'million strings to then discard 999,990 of them is the actual problem in production.<br><br>'
           'In C#, <b>yield return</b> turns the same recursion into a stream:<br>'
           '&bull; memory becomes <b>O(n)</b> instead of O(4&#8319;&middot;n)<br>'
           '&bull; the caller can <code>.Take(10)</code> and the rest is <b>never computed</b><br>'
           '&bull; it composes with LINQ filters for free<br><br>'
           '<i>This is the follow-up most likely to be asked, and the one most candidates have never written.</i></div>',
           """Follow-up one, and this is the one I would prepare hardest, because it is where the question goes and most """
           """candidates have never written it. Make it lazy — do not build the list at all.""", step=0)
seg(sid, 1, """The reason is practical. The caller often wants the first few combinations, or wants to filter them against a """
            """dictionary, and building a million strings in order to discard nine hundred and ninety thousand of them is """
            """the actual problem in production.""")
seg(sid, 2, """In C sharp, yield return turns the same recursion into a stream. Memory drops from exponential to linear. The """
            """caller can take ten and the rest is never computed at all. And it composes with LINQ filters for free.""")
seg(sid, 3, """That last property is the one to mention: laziness is not just a memory trick, it changes who decides how """
            """much work gets done. The caller does, instead of you.""")

CODE2 = '''public static IEnumerable<string> Combinations(string digits) {
    if (string.IsNullOrEmpty(digits)) yield break;        // nothing to stream

    var path = new char[digits.Length];
    foreach (var s in Walk(digits, 0, path)) yield return s;
}

private static IEnumerable<string> Walk(string digits, int i, char[] path) {
    if (i == digits.Length) {
        yield return new string(path);                    // materialise ONE result, then pause
        yield break;
    }

    foreach (char c in Pad[digits[i] - '0']) {
        path[i] = c;                                      // choose (no un-choose needed: we overwrite)
        foreach (var s in Walk(digits, i + 1, path))      // explore, streaming each leaf upward
            yield return s;
    }
}

// The caller decides how much work happens:
//   Combinations("2345678").Take(10)                  -> computes ~10 leaves, not 8,748
//   Combinations(d).Where(w => dictionary.Contains(w)) -> filters without materialising
//   Combinations(d).FirstOrDefault(IsAWord)            -> stops at the first hit'''
code_slide('The lazy version', CODE2, [
 ('1-5', """The public method yields rather than returning a list. `yield break` on empty input preserves the same """
           """contract as before — an empty sequence, not a sequence containing an empty string."""),
 ('7-12', """Each leaf is materialised one at a time and then the method pauses, holding its position in the recursion. """
            """That suspension is what makes memory linear: at any instant, exactly one result string exists."""),
 ('14-19', """Note there is no un-choose here, because we write into a fixed array by index and the next iteration """
             """overwrites the slot. Mentioning that you removed the backtracking step and why is a nice detail — it shows """
             """you understand what the un-choose was actually for."""),
 ('21-25', """And this is the payoff to show the interviewer. Take ten computes about ten leaves out of eight thousand. """
             """A Where filter never materialises the rejects. FirstOrDefault stops at the first hit. The algorithm did not """
             """get smarter — you moved the decision about how much work to do from your function to its caller, which is """
             """usually where it belongs."""),
])

sid = beat('Follow-up 2', 'Rank the combinations, or restrict them to real words',
           '<div style="font-size:30px;line-height:1.7">'
           'The realistic version of this question &mdash; and it is genuinely a LinkedIn-shaped problem &mdash; is '
           '<b>T9 predictive text</b>: return only combinations that are real words, best first.<br><br>'
           '<b>&bull;</b> Put the dictionary in a <b>trie</b>. At each digit, descend to the children reachable by that '
           'digit&rsquo;s letters.<br>'
           '<b>&bull;</b> A path with no trie node is <b>pruned immediately</b> &mdash; this is the whole win, and it '
           'turns 4&#8319; into &ldquo;however many real prefixes exist&rdquo;, which is tiny.<br>'
           '<b>&bull;</b> Store a frequency on each word node, and emit in rank order with a heap.<br><br>'
           '<i>Pruning beats enumerating. That is the transferable idea.</i>',
           """Follow-up two, and this is the realistic version of the question — genuinely LinkedIn-shaped, because it is a """
           """search-and-ranking problem. Return only combinations that are real words, best first. That is T9 predictive """
           """text.""", step=0)
seg(sid, 1, """Put the dictionary in a trie. At each digit, descend to whichever children are reachable via that digit's """
            """letters.""")
seg(sid, 2, """A path that has no corresponding trie node is pruned immediately, and that is the entire win. It turns four """
            """to the n into however many real prefixes exist, which for an English dictionary is a tiny fraction — most """
            """letter sequences are not prefixes of any word.""")
seg(sid, 3, """Then store a frequency on each word node and emit in rank order with a heap, which is how predictive text """
            """puts the common word first.""")
seg(sid, 4, """And the transferable idea, which is worth stating explicitly: pruning beats enumerating. In every """
            """exponential search problem, the question is not how fast you enumerate, it is how early you can stop.""")

followups(
 ['"Write it iteratively" — a queue/BFS build-up: start with [""] and expand level by level; same complexity, no recursion depth',
  '"Make it lazy" — yield return, above; the memory win is the point',
  '"Only real words, ranked" — trie-guided pruning plus a frequency heap'],
 ['"10-digit input" — a million results; ask what the caller actually needs before producing any of them',
  '"Produce them in parallel" — partition on the first digit; each branch is independent, so it is a clean fan-out with no shared state',
  '"Internationalise it" — keypad maps differ per locale, and some scripts have no keypad convention; the map becomes configuration, not a constant'],
 """Follow-ups. Writing it iteratively with a queue is a fair request — you start with a single empty string and expand """
 """level by level, which has the same complexity and removes the recursion depth. Making it lazy we covered. And """
 """restricting to real words with ranking is the trie answer.""",
 """At staff level the questions are about restraint and scale. A ten-digit input means a million results, and the right """
 """response is to ask what the caller actually needs before producing any of them — that is the lazy conversation again, """
 """in product language. Parallelising is unusually clean here: partition on the first digit, and each branch is """
 """independent with no shared state, which is a genuine fan-out. And internationalising it turns the keypad map from a """
 """constant into configuration, which is the sort of extensibility point the official pack says this module scores.""")

interview_script([
 '"Each digit is a level of a tree and each letter is a branch, so I am enumerating leaves — the output is 3ⁿ to 4ⁿ."',
 '"That means no algorithm can beat exponential time; the only thing I can improve is memory."',
 '"Backtracking with one shared buffer: choose, explore, un-choose. Working space is O(n), separate from the output."',
 '"Empty input returns an empty list, not a list containing an empty string."',
 '"If the caller only needs a few, I would make it lazy with yield return — then Take(10) computes ten leaves, not a million."',
 '"And if you want only real words, I would guide it with a trie and prune dead prefixes, which is what actually makes this fast."',
], [
 """The script. State the tree framing and the output size first, because that is your complexity answer and it """
 """pre-empts the "can you do better" question before it is asked.""",
 """Then the three-word rhythm — choose, explore, un-choose — and the distinction between working space and output """
 """space, which is the detail that separates a careful answer from a rote one.""",
 """Then, without being prompted, offer the lazy version and the trie version. On an easy question, volunteering the two """
 """follow-ups is how you convert four minutes of coding into a Staff-level conversation. If you wait to be asked, you """
 """have spent the round on something a mid-level candidate also solves.""",
])

sid = statement('Lesson 8.1', 'When the output is exponential, the interview is about everything except the algorithm.',
                'Laziness, pruning, and asking what the caller actually needs — those are the answers that separate levels.',
                kind='ok')
seg(sid, 0, """One line. When the output is exponential, the interview is about everything except the algorithm, because the """
            """algorithm is forced.""")
seg(sid, 1, """Laziness, pruning, and asking what the caller actually needs — those are the answers that separate levels on """
            """a question this easy. Next lesson: Bulb Switcher, where the code is one line and the entire interview is """
            """the reasoning that gets you there.""")
