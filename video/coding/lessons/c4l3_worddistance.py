# -*- coding: utf-8 -*-
"""Chapter 4, Lesson 3 — Shortest Word Distance II."""
from lib import *

lesson_header('4.3', 'Shortest Word Distance II — design for repeated queries', 'Data structure design · precomputed index + merge',
              'High', 'Your list + the LinkedIn tagged set', '2026', 'High', 15,
              """Chapter four, lesson three. Shortest Word Distance Two. On your own list, and on the LinkedIn tagged set. """
              """The reason this is a data structure lesson rather than an array lesson is the number two in the title: """
              """version one asks the question once, version two builds a class that answers it repeatedly. That single """
              """change is the entire interview, and it is the most transferable idea in this chapter — when the same """
              """question will be asked many times, you stop optimising the answer and start optimising the shape you keep.""")

sid = beat('Question', 'The problem, as they pose it',
           '<div class="qwrap"><div class="qtext" style="font-size:34px;line-height:1.4">'
           'You are given an array of words, once, at construction time.<br><br>'
           'Then <b>Shortest(word1, word2)</b> will be called <b>many times</b>, each time returning the smallest '
           'index distance between an occurrence of word1 and an occurrence of word2. The two words are always '
           'present and always different.<br><br>'
           'Make the repeated query fast.</div></div>',
           """The question. You get an array of words once, at construction time. Then a Shortest method is called many """
           """times, each call naming two words and asking for the smallest index distance between an occurrence of one and """
           """an occurrence of the other. The words are always present and always different. And the instruction that """
           """matters: make the repeated query fast.""")

sid = beat('Interview context', 'What this question is really testing',
           '<div style="font-size:31px;line-height:1.7">'
           'Nobody is testing whether you can scan an array. They are testing whether you notice that <b>the cost model '
           'changed</b>.<br><br>'
           'Version one is a single query: scan once, O(n), done. Version two is the same problem with a <b>workload</b> '
           'attached &mdash; and a workload is what turns an algorithm question into a design question. '
           'That is exactly the jump from L5 to Staff: <i>what are we optimising, and for whom?</i></div>',
           """Some context on what is actually being tested. Nobody is checking whether you can scan an array. They are """
           """checking whether you notice that the cost model changed. Version one is a single query — scan once, linear, """
           """done. Version two is the same problem with a workload attached, and a workload is what turns an algorithm """
           """question into a design question. That is precisely the jump from senior to staff: what are we optimising, and """
           """for whom?""")

think('Constructor gets the array once. Shortest is called many times. What do you precompute?', 30,
      """Pause here. The constructor sees the array once and the query runs many times. Ask yourself what you would """
      """precompute, and — the harder half — what you would deliberately not precompute.""",
      """Let us take both extremes seriously, because the answer is neither of them.""")

sid = compare('The two extremes, and why the answer sits between them',
 ('Precompute nothing', 'info', 0,
  ['Constructor: **O(1)**',
   'Query: **O(n)** scan, every time',
   'Fine for a handful of queries',
   'This is version one, resubmitted']),
 ('Precompute every pair', 'deny', 1,
  ['Query: **O(1)** lookup ✓',
   'Constructor: **O(d&sup2;)** pairs over d distinct words',
   '10,000 distinct words &rarr; **100 million** entries ✗',
   'You have traded a time problem for a memory problem']))
seg(sid, 0, """Precompute nothing and you have version one again: constant constructor, linear query, every time. Perfectly """
            """fine if there are three queries, and you should say so rather than dismissing it.""")
seg(sid, 1, """Precompute every pair and the query becomes a lookup — but the constructor is quadratic in the number of """
            """distinct words. Ten thousand distinct words is a hundred million pairs, and most of them will never be """
            """asked. You have traded a time problem for a much worse memory problem. Naming that trade explicitly is worth """
            """more than either answer.""")

sid = beat('Key observation', 'Precompute the *inputs* to the answer, not the answer',
           '<div class="bigidea">Group the indices by word once. Then a query is a <b>merge of two sorted lists</b> — '
           'which is linear in the two lists, not in the whole array.</div>'
           '<div style="margin-top:24px;font-size:30px;line-height:1.7">'
           'The indices of each word come out of a left-to-right pass <b>already sorted</b>. That is free, and it is what '
           'makes the two-pointer merge legal.</div>',
           """The observation. Do not precompute the answer, precompute the inputs to the answer. Group the indices by """
           """word, once, in the constructor. Then a query is a merge of two sorted lists, which costs the length of those """
           """two lists rather than the length of the whole array.""", step=0)
seg(sid, 1, """And here is the free lunch: because you built those lists in a left-to-right pass, they come out already """
            """sorted. You pay nothing for the sortedness, and the sortedness is exactly what makes the two-pointer merge """
            """legal. Noticing that the data arrives sorted is the kind of small observation that separates a clean answer """
            """from a slow one.""")

D = Diagram('The merge, and why you always advance the smaller index')
D.box('l1', 130, 170, 700, 130, 'word1 &rarr; indices', '[1, 4, 11]', kind='ok', step=0)
D.box('l2', 130, 330, 700, 130, 'word2 &rarr; indices', '[3, 12]', kind='shared', step=0)
D.label(900, 180, 'i=0, j=0 &rarr; |1 &minus; 3| = **2** &nbsp; best = 2', kind='neutral', step=1, w=900, size='m')
D.label(900, 250, '1 &lt; 3, so advance **i** &mdash; only a later word1 can beat this',
        kind='ok', step=2, w=900, size='m')
D.label(900, 330, 'i=1 &rarr; |4 &minus; 3| = **1** &nbsp; best = 1', kind='neutral', step=3, w=900, size='m')
D.label(900, 400, '3 &lt; 4, advance **j** &rarr; |4 &minus; 12| = 8 &nbsp; best stays 1',
        kind='neutral', step=4, w=900, size='m')
D.label(900, 470, '4 &lt; 12, advance i &rarr; |11 &minus; 12| = **1** &nbsp; best = 1',
        kind='neutral', step=5, w=900, size='m')
D.label(130, 560, 'Why advancing the smaller one is safe: pairing the smaller index with a **larger** '
                  'partner can only increase the gap. So that pairing is already finished.',
        kind='dp', step=6, w=1700, size='l')
D.label(130, 690, 'Early exit: a distance of 1 is the minimum possible for distinct words &mdash; return immediately.',
        kind='ok', step=7, w=1700, size='m')
sid = D.build()
seg(sid, 0, """Let us merge. Word one sits at indices one, four and eleven. Word two sits at three and twelve.""")
seg(sid, 1, """Start both pointers at the front. One and three give a distance of two. Best so far, two.""")
seg(sid, 2, """One is smaller than three, so we advance the first pointer. And the reason is the part to say out loud, """
            """because it is the correctness argument.""")
seg(sid, 3, """Four against three gives one. Best is now one.""")
seg(sid, 4, """Three is smaller, so advance the second pointer. Four against twelve is eight — no improvement.""")
seg(sid, 5, """Four is smaller, advance the first. Eleven against twelve is one again.""")
seg(sid, 6, """Now the argument. Advancing the smaller index is safe because pairing that smaller index with any larger """
            """partner can only increase the gap. Its best possible partner has already been considered, so that pairing is """
            """finished. If you can state that in one sentence, you have proved the algorithm correct, and interviewers """
            """notice when a candidate proves rather than asserts.""")
seg(sid, 7, """One optional extra: for two distinct words the smallest possible distance is one, so you can return the """
            """instant you see it. Small, but it is the sort of thing you mention and then let them decide whether they """
            """want it.""")

sid = cards('What to ask, and what to watch', [
 (0, 'Ask: how many queries, and how many distinct words?', 'This is the question that justifies your whole design. If they say "three queries", the honest answer is the linear scan.', 'ok'),
 (0, 'Ask: can word1 equal word2?', 'The stated spec says no. If they relax it, the merge breaks &mdash; you need consecutive indices within one list instead.', 'shared'),
 (1, 'Ask: is the word list mutable?', 'If words can be appended, indices stay valid and you append to one list. If they can be edited, your index is stale.', 'shared'),
 (1, 'Watch: the "always present" clause', 'Do not build defensive code for absent words unless they ask &mdash; but say that you noticed the clause.', 'ok'),
 (2, 'Watch: memory', 'The index groups hold exactly n integers in total. It is the same order as the input, not a multiple of it.', 'ok'),
 (2, 'Watch: the caching temptation', 'Memoising answered pairs is reasonable <i>if</i> the same pairs repeat. Say when it pays, not that it is always better.', 'shared'),
], cols=2)
seg(sid, 0, """Before coding, two questions. How many queries, and how many distinct words — that is the question that """
            """justifies your entire design, and if they answer "about three" then the honest recommendation is the linear """
            """scan and you should say so. And can the two words be equal? The stated spec says no. If they relax it, the """
            """merge breaks and you need the minimum gap between consecutive indices within a single list instead.""")
seg(sid, 1, """Ask whether the word list is mutable. Appending is fine — indices stay valid and you append to one group. """
            """Editing in place makes your index stale, and that is a real design conversation. And on the always-present """
            """clause: do not write defensive code for absent words unless asked, but do say that you noticed it.""")
seg(sid, 2, """Two things to watch. Memory is fine — the index groups hold exactly n integers in total, the same order as """
            """the input. And resist the temptation to add a cache of answered pairs unless the workload repeats pairs; say """
            """when it pays rather than claiming it always does.""")

CODE = '''public class WordDistance {
    private readonly Dictionary<string, List<int>> _at = new();     // word -> its indices, ascending

    public WordDistance(string[] words) {
        for (int i = 0; i < words.Length; i++) {                    // one left-to-right pass
            if (!_at.TryGetValue(words[i], out var list)) {
                list = new List<int>(); _at[words[i]] = list;
            }
            list.Add(i);                                            // appended in order -> already sorted
        }
    }

    public int Shortest(string word1, string word2) {
        List<int> a = _at[word1], b = _at[word2];
        int i = 0, j = 0, best = int.MaxValue;

        while (i < a.Count && j < b.Count) {
            best = Math.Min(best, Math.Abs(a[i] - b[j]));
            if (best == 1) return 1;                                // the minimum possible for distinct words
            if (a[i] < b[j]) i++;                                   // advance the SMALLER index
            else j++;                                               // its best partner is already behind it
        }
        return best;
    }
}'''
code_slide('The C# implementation', CODE, [
 ('2', """One field: a dictionary from word to the list of indices where it occurs. That declaration is the design, and I """
         """would write it while explaining rather than after."""),
 ('4-11', """The constructor is a single left-to-right pass. Because we append as we go, each list comes out ascending for """
            """free — no sort call anywhere, and that is worth saying, because a sort here would be the one unnecessary """
            """log n in the solution."""),
 ('13-15', """The query pulls the two lists and walks them with two pointers. Note we index the dictionary directly, """
             """because the spec guarantees both words exist — and I would say that out loud rather than silently relying """
             """on it."""),
 ('17-19', """Each step measures the current pair and keeps the best. The early return at distance one is optional; it costs """
             """a comparison and saves a scan in the common dense case."""),
 ('20-22', """And the move that makes it correct: advance whichever pointer holds the smaller index, because that index's """
             """best possible partner has already been seen. This is three lines of code and one sentence of reasoning, and """
             """the sentence is what you are being marked on."""),
])

sid = table('Complexity',
 ['Phase', 'Cost', 'Note'],
 [(0, ['Constructor', 'O(n) time, O(n) space', 'One pass; total indices stored is exactly n'], None),
  (1, ['Shortest(w1, w2)', 'O(|a| + |b|)', '<b>Not</b> O(n) &mdash; only the two words&rsquo; occurrence lists'], None),
  (2, ['Worst case for one query', 'O(n)', 'When the two words are most of the array &mdash; say this, do not hide it'], None),
  (3, ['Naive alternative', 'O(n) per query, O(1) build', 'Better when queries are few. Know when your design loses'], 'dim')],
 widths=[28, 26, 46])
seg(sid, 0, """Complexity. The constructor is one linear pass and linear space — exactly n indices stored in total, spread """
            """across the groups.""")
seg(sid, 1, """The query is the sum of the two lists' lengths, not the length of the array. That distinction is the payoff of """
            """the whole design.""")
seg(sid, 2, """Be honest about the worst case: if the two words make up most of the array, one query is still linear. Say """
            """that yourself rather than letting them find it — an interviewer who has to point out your worst case learns """
            """something different about you than one who hears it from you.""")
seg(sid, 3, """And keep the naive alternative in the conversation. It wins when queries are few. Knowing the conditions under """
            """which your own design loses is a staff-level answer.""")

followups(
 ['"What if word1 can equal word2?" — the merge breaks; scan one list for the minimum gap between consecutive indices',
  '"Return the actual positions, not just the distance" — keep the pair that produced the best',
  '"Words stream in over time" — indices stay valid on append; append to the group and nothing else changes'],
 ['"Millions of queries, skewed to a few pairs" — memoise answered pairs in a bounded LRU; now the hit rate decides the design',
  '"The corpus does not fit in memory" — this becomes an inverted index on disk, which is roughly how search engines store postings',
  '"Give me the k closest pairs, not the closest" — the same merge, keeping a bounded max-heap of size k'],
 """Follow-ups. If the two words can be equal, the merge breaks and you scan one list for the minimum gap between """
 """consecutive indices — a different, simpler loop. Returning the actual positions is just carrying the winning pair """
 """alongside the best value. And if words stream in over time, appends are painless: indices stay valid and you append to """
 """one group.""",
 """At staff level, the interesting follow-up is millions of queries skewed to a few pairs, where memoising answered pairs """
 """in a bounded cache becomes worth it — and note that the hit rate, not the algorithm, now decides the design. If the """
 """corpus does not fit in memory, this structure is an inverted index with postings lists, which is roughly how a search """
 """engine stores exactly this; saying that connects the toy problem to real infrastructure. And the k-closest-pairs """
 """variant is the same merge with a bounded heap.""")

interview_script([
 '"Version one is a single scan. Version two attaches a workload, so I should precompute — the question is what."',
 '"Precomputing every pair is O(d²) memory for answers that will mostly never be asked. I would not do that."',
 '"I will group indices by word in the constructor. They come out sorted for free from a left-to-right pass."',
 '"A query is then a two-pointer merge of two sorted lists: O(|a| + |b|), not O(n)."',
 '"Advancing the smaller index is safe because its best partner is already behind it."',
 '"How many queries, and how many distinct words? If it is only a few queries, the plain scan is the better answer."',
], [
 """The script. Open by naming the change: version two attaches a workload. Then reject the full precomputation and give """
 """the reason in terms of memory for answers nobody asks for — that is a product sentence as much as an engineering one.""",
 """Then the design, the free sortedness, and the query cost stated precisely as the two lists rather than the array.""",
 """Give the correctness argument in one line, and finish by asking the workload question. Ending on "if it is only a few """
 """queries, the plain scan is better" is not weakness. It shows you know what your design costs and when it is not worth """
 """paying — which is the thing a staff interviewer is actually listening for.""",
])

sid = statement('Lesson 4.3', 'A workload turns an algorithm question into a design question.',
                'Precompute the inputs to the answer, not the answer. And know the query count at which your design stops being worth it.',
                kind='ok')
seg(sid, 0, """One line. A workload turns an algorithm question into a design question.""")
seg(sid, 1, """Precompute the inputs to the answer, not the answer itself — and know the query count at which your design """
            """stops being worth it. Next lesson: LFU cache, which is the same chapter idea again, at the hardest setting, """
            """with a ranking follow-up that was actually reported.""")
