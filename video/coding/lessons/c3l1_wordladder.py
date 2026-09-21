# -*- coding: utf-8 -*-
"""Chapter 3, Lesson 1 — Word Ladder, and why bidirectional BFS."""
from lib import *

lesson_header('3.1', 'Word Ladder, and why bidirectional BFS', 'Graphs · BFS on an implicit graph',
              'High', 'Your own list + a LeetCode Staff report (Jul 2025)', '2025', 'High', 18,
              """Chapter three, lesson one. Word Ladder. It is on your own list, and it was reported in a LeetCode write-up of a """
              """LinkedIn Staff screening in July 2025, so two independent sources. This lesson carries two ideas that pay for """
              """themselves across the whole chapter. The first is the implicit graph: there is no graph in the input, so you """
              """have to notice that one exists. The second is bidirectional search, which is the upgrade the interviewer is """
              """waiting for — and the reason it matters is arithmetic you can do out loud in about ten seconds.""")

# ---------------------------------------------------------------- question
sid = beat('Question', 'The question',
           '<div class="qwrap"><div class="qtext" style="font-size:38px;line-height:1.35">'
           'Given <code>beginWord</code>, <code>endWord</code> and a word list, return the number of words in the shortest '
           'transformation sequence from begin to end, changing exactly one letter at a time, where every intermediate word '
           'must be in the list. Return 0 if there is no such sequence.</div></div>',
           """Here is the question. You are given a start word, an end word, and a dictionary. You transform one word into """
           """another by changing exactly one letter, and every word along the way has to exist in the dictionary. Return the """
           """length of the shortest chain, or zero if there is not one. Hit, hot, dot, dog, cog is the classic example: five """
           """words, so the answer is five.""")

# ---------------------------------------------------------------- think
think('beginWord = "hit", endWord = "cog", wordList = [hot, dot, dog, lot, log, cog]. '
      'Return the length of the shortest transformation sequence.', 30,
      """Pause here. Two questions to answer out loud before I say anything. What are the nodes and edges in this problem — """
      """because there is no graph in the input. And once you have a graph, which traversal gives you a shortest path on it, """
      """and why that one rather than the other?""",
      """Good. If you said the words are nodes, two words are connected when they differ by one letter, and breadth-first """
      """search gives shortest paths on unweighted graphs — you have the core. Now let us find the two places where the naive """
      """version falls over, because that is where the interview actually happens.""")

# ---------------------------------------------------------------- implicit graph
D = Diagram('Nobody gave you a graph. You have to see one.')
graph(D, {'w1': (140, 180, 'hit'), 'w2': (480, 180, 'hot'), 'w3': (820, 100, 'dot'), 'w4': (820, 280, 'lot'),
          'w5': (1160, 100, 'dog'), 'w6': (1160, 280, 'log'), 'w7': (1500, 180, 'cog')},
      [('w1', 'w2'), ('w2', 'w3'), ('w2', 'w4'), ('w3', 'w5'), ('w4', 'w6'), ('w5', 'w7'), ('w6', 'w7')], step=0)
D.label(120, 430, '**Nodes:** the words.   **Edges:** differ by exactly one letter.', kind='ok', step=1, w=1700, size='m', align='center')
D.label(120, 510, 'Unweighted edges → **BFS gives the shortest path**. Dijkstra would be the wrong tool and a slower one.',
        kind='info', step=2, w=1700, size='m', align='center')
D.label(120, 610, 'The cost nobody mentions: **finding the neighbours**.', kind='deny', step=3, w=1700, size='l', align='center')
D.label(120, 690, 'Comparing every pair of words is O(N²·L). With 10⁵ words that is 10¹⁰ character comparisons.',
        kind='deny', step=4, w=1700, size='m', align='center')
sid = D.build()
seg(sid, 0, """Here is the graph hiding in the input. Hit connects to hot. Hot connects to dot and lot. Those connect onward to """
            """dog and log, and both of those reach cog.""")
seg(sid, 1, """Nodes are the words. Edges exist between two words that differ by exactly one letter. Saying that sentence out """
            """loud is the moment you have converted a string puzzle into a graph problem, and it is worth saying explicitly """
            """in the interview rather than silently assuming it.""")
seg(sid, 2, """The edges are unweighted — every transformation costs one step — and on an unweighted graph, breadth-first search """
            """gives you the shortest path. If you reach for Dijkstra here, you are using a more expensive tool for no benefit, """
            """and an interviewer will notice.""")
seg(sid, 3, """But here is the cost that nobody mentions when they describe this as a simple BFS. How do you find a word's """
            """neighbours?""")
seg(sid, 4, """The obvious way is to compare it against every other word in the list. That is order N squared times L character """
            """comparisons. With a hundred thousand words, that is ten billion comparisons before your BFS has taken a single """
            """step. Your traversal was never the bottleneck; neighbour discovery was.""")

# ---------------------------------------------------------------- buckets
D = Diagram('Fixing neighbour discovery: wildcard buckets')
D.box('b1', 160, 160, 620, 120, '"h*t"', '→ hit, hot', kind='ok', step=0)
D.box('b2', 160, 310, 620, 120, '"*ot"', '→ hot, dot, lot', kind='ok', step=1)
D.box('b3', 160, 460, 620, 120, '"do*"', '→ dot, dog', kind='ok', step=2)
D.label(860, 180, 'For each word, for each position,\nreplace one letter with `*`.', kind='info', step=0, w=900, size='m')
D.label(860, 320, 'Words in the same bucket differ by\nexactly one letter — by construction.', kind='dp', step=1, w=900, size='m')
D.label(860, 470, 'Neighbours of a word = union of its L buckets.\nA dictionary lookup, not a scan.', kind='ok', step=2, w=900, size='m')
D.label(120, 660, 'Build: **O(N·L²)** once.   Lookup: **O(1)** per pattern.   Replaces an O(N²·L) scan.',
        kind='ok', step=3, w=1700, size='l', align='center')
sid = D.build()
seg(sid, 0, """So we fix neighbour discovery with a preprocessing trick. For every word, for every position in it, we make a """
            """pattern by replacing that letter with a star. Hit gives us star-i-t, h-star-t, and h-i-star. We bucket words """
            """under those patterns.""")
seg(sid, 1, """Now look at what the bucket means. Any two words sitting in the same bucket differ in exactly one position, """
            """because every other position matched the pattern. Adjacency is not something we compute any more; it is """
            """something the bucket structure guarantees by construction.""")
seg(sid, 2, """So a word's neighbours are just the union of the buckets for its L patterns. That is L dictionary lookups instead """
            """of a scan over the whole word list.""")
seg(sid, 3, """Building the buckets costs order N times L squared once — N words, L patterns each, and each pattern is L """
            """characters to build. After that, every lookup is constant. We have replaced an order N squared times L scan """
            """with a one-time linear-ish build, and that is the first real optimisation in this problem.""")

# ---------------------------------------------------------------- bidirectional
D = Diagram('The second optimisation: search from both ends')
D.label(120, 130, 'One-directional BFS explores about **b^d** nodes', kind='deny', step=0, w=1700, size='m')
D.box('u1', 220, 210, 180, 100, 'depth 1', 'b', kind='com', step=0, small=True)
D.box('u2', 430, 210, 200, 100, 'depth 2', 'b²', kind='com', step=0, small=True)
D.box('u3', 660, 210, 220, 100, 'depth 3', 'b³', kind='shared', step=0, small=True)
D.box('u4', 910, 210, 240, 100, 'depth 4', 'b⁴ = 100 000 000', kind='deny', step=0, small=True)
D.label(120, 360, 'Bidirectional: two frontiers meeting in the middle, about **2·b^(d/2)**', kind='ok', step=1, w=1700, size='m')
D.box('v1', 220, 440, 300, 100, 'from begin', 'b² = 10 000', kind='ok', step=1, small=True)
D.box('v2', 560, 440, 300, 100, 'from end', 'b² = 10 000', kind='ok', step=1, small=True)
D.label(900, 460, '= 20 000 nodes instead of 100 000 000', kind='ok', step=1, w=900, size='m')
D.label(120, 600, 'Same asymptotic class. **Five thousand times less work** at b = 100, d = 4.', kind='dp', step=2, w=1700, size='l', align='center')
D.label(120, 690, 'Rule: always expand the **smaller** frontier. That is what makes it bidirectional rather than two searches.',
        kind='shared', step=3, w=1700, size='m', align='center')
sid = D.build()
seg(sid, 0, """Now the second optimisation, and this is the one the interviewer is waiting for. A one-directional breadth-first """
            """search explores roughly b to the power d nodes, where b is the branching factor and d is the depth of the """
            """answer. Put real numbers in: branching factor one hundred, answer at depth four, and you touch a hundred """
            """million nodes.""")
seg(sid, 1, """Now search from both ends at once and let the frontiers meet in the middle. Each side only has to get to depth """
            """two. That is b squared from each side — ten thousand plus ten thousand.""")
seg(sid, 2, """Twenty thousand instead of a hundred million. Now, be precise about what you are claiming, because this matters: """
            """it is the same asymptotic class. You have not changed the big-O. What you have done is cut the constant by a """
            """factor of five thousand on realistic inputs. Interviewers like candidates who can say exactly that — the """
            """asymptotics are unchanged and here is why I would still do it.""")
seg(sid, 3, """And one rule makes it work: always expand the smaller of the two frontiers. If you just alternate sides blindly, """
            """you are running two searches. Expanding the smaller one is what keeps both sides shallow, and it is the """
            """implementation detail people most often get wrong.""")

# ---------------------------------------------------------------- code
CODE = '''public int LadderLength(string beginWord, string endWord, IList<string> wordList) {
    var dict = new HashSet<string>(wordList);
    if (!dict.Contains(endWord)) return 0;           // cheap exit: no path can exist

    // 1. Bucket every word under its wildcard patterns: "h*t" -> [hit, hot]
    var buckets = new Dictionary<string, List<string>>();
    foreach (var w in dict)
        for (int i = 0; i < w.Length; i++) {
            var key = w.Substring(0, i) + "*" + w.Substring(i + 1);
            if (!buckets.TryGetValue(key, out var list)) buckets[key] = list = new List<string>();
            list.Add(w);
        }

    // 2. Two frontiers, one visited set, always expand the smaller side
    var front = new HashSet<string> { beginWord };
    var back  = new HashSet<string> { endWord };
    var seen  = new HashSet<string> { beginWord, endWord };
    int steps = 1;

    while (front.Count > 0 && back.Count > 0) {
        if (front.Count > back.Count) (front, back) = (back, front);

        var next = new HashSet<string>();
        foreach (var word in front)
            for (int i = 0; i < word.Length; i++) {
                var key = word.Substring(0, i) + "*" + word.Substring(i + 1);
                if (!buckets.TryGetValue(key, out var neighbours)) continue;
                foreach (var nb in neighbours) {
                    if (back.Contains(nb)) return steps + 1;   // the frontiers met
                    if (seen.Add(nb)) next.Add(nb);
                }
            }
        front = next;
        steps++;
    }
    return 0;
}'''
code_slide('The C# implementation', CODE, [
 ('1-3', """We start with a set of the dictionary for constant-time membership, and one cheap exit: if the end word is not in """
           """the dictionary, no path can possibly exist. Saying "let me handle the impossible case first" costs one line and """
           """it is the kind of thing that reads as experience."""),
 ('5-12', """Then the bucket build. For each word, for each position, we make the wildcard key and append the word to that """
            """bucket. This is the preprocessing that replaced the quadratic neighbour scan, so narrate it as such — do not let """
            """it look like incidental setup."""),
 ('14-18', """Now the two frontiers. Front starts at the begin word, back starts at the end word, and one shared seen set stops """
             """either side revisiting. Steps starts at one because the problem counts words, not transitions — that is an """
             """off-by-one worth stating out loud, because it is the single most common wrong answer here."""),
 ('20-21', """The loop runs while both sides still have something to explore. And this line is the heart of bidirectional """
             """search: if the front frontier is larger, swap the two. From here on we are always expanding the smaller side."""),
 ('23-27', """For each word in the smaller frontier, we generate its patterns and look up the bucket. That is the O(1) """
             """neighbour lookup we bought earlier."""),
 ('28-31', """And here is the meeting test. If a neighbour is already in the other side's frontier, the two searches have """
             """touched, and the answer is the steps taken so far plus one. Otherwise, if we have not seen it, it joins the """
             """next frontier. Note that `seen.Add` returns false when the item was already there, so the check and the insert """
             """are one operation rather than two."""),
 ('33-36', """Swap in the new frontier, increment the step count, and loop. If either side ever runs dry, the graphs are """
             """disconnected and there is no ladder, so we return zero."""),
])

# ---------------------------------------------------------------- complexity & edges
sid = table('Complexity — and the honest caveats', ['', 'Answer', 'Say it like this'], [
 (0, ['Bucket build', 'O(N·L²)', 'N words, L patterns each, L characters per pattern — and it is memory too'], [None, 'info', None]),
 (1, ['Search', 'O(N·L²) worst case', 'Each word is expanded once; each expansion makes L patterns'], [None, 'info', None]),
 (2, ['Bidirectional', 'Same class', '**Constant-factor** win: ~2·b^(d/2) instead of b^d explored'], [None, 'ok', None]),
 (3, ['Space', 'O(N·L²)', 'Dominated by the buckets — the trade you accepted for fast lookups'], [None, 'shared', None]),
], widths=[20, 20, 60])
seg(sid, 0, """Complexity, and I want you to give all four of these lines. The bucket build is order N times L squared, and """
            """notice that is memory as well as time — you are storing every pattern.""")
seg(sid, 1, """The search itself is the same bound in the worst case: every word gets expanded once, and each expansion """
            """generates L patterns of length L.""")
seg(sid, 2, """Bidirectional search does not change the class. It is a constant-factor win, and a huge one on realistic inputs. """
            """Being precise here is a signal in itself.""")
seg(sid, 3, """And space is dominated by the buckets. That is the trade you consciously made: memory for lookup speed. If the """
            """interviewer says memory is tight, the answer is to drop the buckets and generate the twenty-five neighbours of """
            """each word directly by trying every letter at every position, testing membership in the dictionary. More CPU, """
            """far less memory — and having that alternative ready is exactly the kind of trade-off conversation this round is """
            """built for.""")

sid = cards('Edge cases', [
 (0, 'endWord not in the list', 'Return 0 immediately — the cheap exit.', 'ok'),
 (0, 'beginWord may not be in the list', 'Do not require it; it is a start, not an intermediate.', 'shared'),
 (1, 'beginWord == endWord', 'Ask. The problem usually excludes it; say what you would return.', 'info'),
 (1, 'Words of different lengths', 'Filter them out — they can never be one letter apart.', 'info'),
 (2, 'Duplicates in the list', 'The HashSet handles it. Say that it does.', 'info'),
 (2, 'Disconnected graph', 'A frontier empties → return 0. Test this case explicitly.', 'deny'),
], cols=2)
seg(sid, 0, """Edge cases. End word missing is the cheap exit. Begin word not being in the dictionary is fine and you should not """
            """require it — it is the starting point, not an intermediate step, and requiring it is a bug people ship.""")
seg(sid, 1, """Begin equals end is a question for the interviewer. Different-length words can never be one letter apart, so """
            """filter them.""")
seg(sid, 2, """Duplicates are absorbed by the set. And the disconnected case — where one frontier empties — is the one to """
            """actually test, because it is the path where your loop must terminate and return zero rather than spin.""")

# ---------------------------------------------------------------- follow-ups
followups(
 ['"Return all shortest ladders" (Word Ladder II) — keep parent lists and backtrack at the end',
  '"Why bidirectional?" — the b^d versus 2·b^(d/2) arithmetic, out loud',
  '"What if the dictionary has 10⁷ words?" — drop the buckets, generate neighbours on the fly'],
 ['"The dictionary lives on another service" — batch the membership checks; latency, not CPU, is now the cost',
  '"Transformations have different costs" — it stops being BFS and becomes Dijkstra; say why',
  '"Run it for millions of queries on the same dictionary" — build the buckets once and keep them warm; the per-query cost is what matters'],
 """Follow-ups. Word Ladder Two — return every shortest ladder — is the standard escalation, and the change is that you """
 """keep parent lists during the search and backtrack at the end rather than returning a count. Why bidirectional is a """
 """question you should welcome, because the arithmetic is the answer. And the ten-million-word version pushes you off """
 """buckets and onto generating the twenty-five neighbours directly.""",
 """The staff-level versions are about where the work happens. If the dictionary is a remote service, your bottleneck is """
 """network latency, so you batch membership checks per frontier rather than per word — a completely different optimisation """
 """from anything we have discussed. If transformations have different costs, breadth-first search is simply the wrong """
 """algorithm and you switch to Dijkstra; knowing when your tool stops applying is worth more than knowing the tool. And if """
 """you are serving millions of queries against one dictionary, the build cost amortises to nothing and only the per-query """
 """search matters — which is an argument for spending even more on preprocessing.""")

interview_script([
 '"There is no graph in the input, so first: nodes are words, and two words are adjacent if they differ in exactly one letter."',
 '"Edges are unweighted, so BFS gives the shortest path — Dijkstra would be overkill."',
 '"The hidden cost is neighbour discovery. Comparing all pairs is O(N²·L), so I will preprocess wildcard buckets instead."',
 '"Then I would search from both ends, always expanding the smaller frontier."',
 '"That does not change the asymptotics — it is a constant-factor win, roughly 2·b^(d/2) explored instead of b^d."',
 '"Careful with the count: the answer is words, not transitions, so I start the counter at one."',
 '"If memory is tight I would drop the buckets and generate the 25·L candidate neighbours directly, testing dictionary membership."',
], [
 """The script, and this one has a particular shape worth copying. You open by naming the modelling step explicitly — there """
 """is no graph in the input, so here is the graph I am constructing. Then you justify BFS in one clause and dismiss """
 """Dijkstra in another.""",
 """Then the move that separates this answer from an average one: you name neighbour discovery as the hidden cost before """
 """anyone points it out, and you fix it. Then bidirectional search, with the smaller-frontier rule stated, and the honest """
 """asymptotic caveat.""",
 """Then the off-by-one, said deliberately rather than discovered by a failing test. And you finish by offering the """
 """memory-versus-CPU alternative. Seven sentences, and every one of them is a decision with a reason attached. That is """
 """what the transcript of a strong candidate actually looks like.""",
])

sid = statement('Take this with you', 'When the input has no graph, say what the nodes and edges are — out loud.',
                'Then ask what neighbour discovery costs. In implicit graphs, that is usually the real bottleneck.', kind='ok')
seg(sid, 0, """One sentence to keep. When the input has no graph, say what the nodes and edges are, out loud, before you code.""")
seg(sid, 1, """And then immediately ask what it costs to find a node's neighbours, because in implicit graphs that is almost """
            """always where the real complexity hides. Next lesson: The Maze — where the nodes are not what they appear to be """
            """either, and the mistake is much easier to make. See you there.""")
