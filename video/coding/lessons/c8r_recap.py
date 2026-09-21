# -*- coding: utf-8 -*-
"""Chapter 8 recap — backtracking and maths."""
from lib import *

lesson_header('8.R', 'Chapter 8 recap: backtracking and reasoning out loud', 'Recap · templates · mini mock',
              'High', '2 reported questions · both easy to code, hard to score well on', '2026', 'Medium', 11,
              """Chapter eight recap. Two reported questions, and they share an awkward property: both are easy to code and """
              """hard to score well on. Letter Combinations takes four minutes to write, so the marks are entirely in the """
              """follow-ups. Bulb Switcher is one line, so the marks are entirely in the reasoning. This recap is therefore """
              """less about technique than the others, and more about what to do with the time an easy question leaves """
              """you.""")

sid = beat('Pattern summary', 'The chapter in one page',
           '<div class="bigidea">When a problem is exponential, you cannot out-compute it. You can only '
           '<b>prune</b>, <b>defer</b>, or <b>replace it with maths</b>.</div>'
           '<div style="margin-top:26px;font-size:30px;line-height:1.7">'
           '<b>Prune</b> &mdash; cut branches that cannot lead to an answer (the trie in 8.1).<br>'
           '<b>Defer</b> &mdash; produce results lazily so the caller decides how many exist (yield return).<br>'
           '<b>Replace</b> &mdash; find the closed form and skip the search entirely (8.2).<br><br>'
           'Backtracking itself is three words: <b>choose, explore, un-choose</b>. That part is not the skill.</div>',
           """One page. When a problem is exponential you cannot out-compute it. You have exactly three moves: prune, """
           """defer, or replace it with maths.""", step=0)
seg(sid, 1, """Prune means cutting branches that cannot lead to an answer — the trie in lesson one. Defer means producing """
            """results lazily so the caller decides how many get computed. Replace means finding the closed form and """
            """skipping the search entirely, which is lesson two. And backtracking itself is three words — choose, explore, """
            """un-choose. That part is not the skill, and treating it as the skill is why candidates underperform on easy """
            """questions.""")

sid = table('The two problems, and where the marks actually are',
 ['Problem', 'Code time', 'Where the marks are', 'Reported'],
 [(0, ['Letter Combinations', '~4 min', 'The lazy version (memory), and trie pruning (real words, ranked). Volunteer both', 'Tagged + your list'], None),
  (1, ['Bulb Switcher', '~10 sec', 'Baseline, stated budget, the divisor reframe, and <b>verifying</b> the pattern out loud', '**Your list**'], None)],
 widths=[24, 14, 50, 12])
seg(sid, 0, """Letter Combinations takes about four minutes to write, and the marks are in the lazy version and in trie """
            """pruning — both of which you should volunteer rather than wait for.""")
seg(sid, 1, """Bulb Switcher takes ten seconds to write once you know it, and the marks are in giving a baseline, stating a """
            """time budget out loud, reframing toggles into divisors, and verifying the pattern on a concrete case. Same """
            """lesson from both: on an easy question, the code is the ticket, not the answer.""")

sid = steps_list('Recognition checklist',
 [(0, '&ldquo;all combinations / permutations / subsets&rdquo; &rarr; **backtracking**, and the output size <b>is</b> your lower bound', 'ok'),
  (0, 'Output is exponential &rarr; say so **before** coding; it pre-empts &ldquo;can you do better?&rdquo;', 'ok'),
  (1, 'A dictionary, a validity rule, or a constraint &rarr; **prune early**; pruning beats enumerating every time', 'ok'),
  (1, 'The caller may want only a few &rarr; **lazy** (yield return); memory drops from O(4&#8319;) to O(n)', 'ok'),
  (2, 'Small cases show a clean pattern &rarr; look for a **closed form** &mdash; but set a time budget out loud', 'shared'),
  (2, 'A puzzle with a suspiciously tidy setup &rarr; probably maths, not simulation', 'shared'),
  (3, 'Recursion on user input &rarr; mention **stack depth**; an iterative queue version is the answer', 'shared'),
  (3, 'Any &ldquo;count how many&rdquo; with a number-theory smell &rarr; think **divisors, parity, pairing**', 'info')],
 numbered=False)
seg(sid, 0, """The recognition checklist. All combinations, permutations or subsets means backtracking, and the output size """
            """is your complexity lower bound — say that before coding, because it pre-empts the "can you do better" """
            """question and reframes it as a memory question.""")
seg(sid, 1, """A dictionary, a validity rule or any constraint means prune early, because pruning beats enumerating every """
            """single time. And if the caller may want only a few results, go lazy: memory drops from exponential to """
            """linear.""")
seg(sid, 2, """If small cases show a clean pattern, look for a closed form — but set a time budget out loud so that looking """
            """is a plan rather than a stall. A puzzle with a suspiciously tidy setup is usually maths rather than """
            """simulation.""")
seg(sid, 3, """Recursion whose depth depends on user input deserves a mention of stack depth, with the iterative queue """
            """version as your answer. And any "count how many" question with a number-theory smell should make you think """
            """about divisors, parity and pairing.""")

sid = cards('The mistakes that actually cost people', [
 (0, 'Forgetting the un-choose', 'Silent garbage rather than a crash. Say &ldquo;choose, explore, un-choose&rdquo; as you write the three lines.', 'deny'),
 (0, 'Quoting output size as space complexity', 'Working space is O(n); the output is separate. Keep them apart when you answer.', 'deny'),
 (1, 'The empty-input case', 'Returning a list containing one empty string is a different answer. It is the first test they run.', 'deny'),
 (1, 'Going silent on the maths question', 'The only unrecoverable failure in 8.2. Narrate the dead ends.', 'deny'),
 (2, 'Asserting a pattern without checking it', 'Verify on one case out loud. Ten seconds, and it converts a guess into evidence.', 'shared'),
 (2, 'Finishing early and stopping', 'Four spare minutes is an invitation. Offer the lazy version, the pruning, the parallel fan-out.', 'shared'),
], cols=2)
seg(sid, 0, """The mistakes. Forgetting the un-choose, which produces silent garbage rather than a crash — say the three words """
            """as you write the three lines. And quoting the output size as your space complexity, when the working space """
            """is linear and separate.""")
seg(sid, 1, """The empty-input case, which returns an empty list rather than a list containing an empty string, and which is """
            """the first thing a grader tests. And going silent on the maths question, which is the only unrecoverable """
            """failure in this chapter.""")
seg(sid, 2, """Asserting a pattern without checking it — ten seconds of verification converts a guess into evidence. And the """
            """last one is specific to easy questions: finishing early and then stopping. Four spare minutes is an """
            """invitation, and the candidates who use it are the ones who get the level.""")

T1 = '''// TEMPLATE R - backtracking: choose, explore, un-choose.
void Walk(int i, List<T> path, List<List<T>> out) {
    if (i == n) { out.Add(new List<T>(path)); return; }   // leaf: COPY the path, do not store it

    foreach (var option in OptionsAt(i)) {
        if (!Allowed(path, option)) continue;             // PRUNE here - this is where the win is
        path.Add(option);                                 // choose
        Walk(i + 1, path, out);                           // explore
        path.RemoveAt(path.Count - 1);                    // un-choose
    }
}

// TEMPLATE S - the same walk, lazily. Memory O(n) instead of O(branches^n).
IEnumerable<string> Walk(int i, char[] path) {
    if (i == n) { yield return new string(path); yield break; }
    foreach (char c in OptionsAt(i)) {
        path[i] = c;                                      // no un-choose: the slot is overwritten
        foreach (var s in Walk(i + 1, path)) yield return s;
    }
}'''
code_slide('Templates R and S &mdash; backtracking, and the lazy version', T1, [
 ('1-11', """Template R. Two details carry it. At the leaf, copy the path — storing the live buffer means every result """
            """ends up identical, which is the single most common backtracking bug. And the prune line is where all the """
            """performance lives: a check that rejects a branch early saves everything below it."""),
 ('13-20', """Template S is the same walk written lazily, and it is worth being able to write from memory, because it is """
             """the follow-up on every enumeration question. Memory becomes linear, the caller controls how much is """
             """computed, and the un-choose disappears because you overwrite the slot rather than appending to a list."""),
])

sid = beat('The five-sentence routine for a maths-flavoured question', 'Use this when you do not know the answer yet',
           '<div style="font-size:31px;line-height:1.7">'
           '<b>1.</b> &ldquo;The brute force is X, costing O(&hellip;). I can write that now if you want a baseline.&rdquo;<br>'
           '<b>2.</b> &ldquo;But the structure suggests a closed form &mdash; give me two minutes on small cases.&rdquo;<br>'
           '<b>3.</b> <i>Tabulate out loud.</i> &ldquo;n=1 gives 1, n=2 gives 1, n=4 gives 2&hellip;&rdquo;<br>'
           '<b>4.</b> &ldquo;That looks like &lt;pattern&gt;. Let me work out <b>why</b>, not just that.&rdquo;<br>'
           '<b>5.</b> &ldquo;Check against n = 10: &hellip; ✓. And here is the edge case I would guard.&rdquo;<br><br>'
           '<i>If step 2&rsquo;s budget runs out, write the brute force and keep thinking. You always land somewhere.</i>',
           """Here is a routine worth memorising, because it works on any maths-flavoured question including ones you have """
           """never seen. Five sentences.""", step=0)
seg(sid, 1, """One: the brute force is this, costing that, and I can write it now if you want a baseline. Two: but the """
            """structure suggests a closed form, so give me two minutes on small cases.""")
seg(sid, 2, """Three: tabulate out loud. Actually say the numbers. Four: that looks like a pattern — let me work out why, """
            """not just that.""")
seg(sid, 3, """Five: check it against a concrete case, and name the edge case you would guard.""")
seg(sid, 4, """And the safety net: if the budget in step two runs out, write the brute force and keep thinking while it sits """
            """on the board. With this routine you always land somewhere, which is the entire point — the failure mode on """
            """these questions is not being wrong, it is having nothing.""")

sid = table('The reported questions, ranked',
 ['#', 'Question', 'Evidence', 'Revise'],
 [(0, ['1', 'Letter Combinations of a Phone Number', 'Your own list + the LinkedIn tagged set', '**First** &mdash; and rehearse the two follow-ups'], None),
  (1, ['2', 'Bulb Switcher', 'Your own list', 'Second &mdash; rehearse the <i>routine</i>, not the answer'], None),
  (2, ['&mdash;', 'Subsets, permutations, N-queens, word search', 'Not reported for LinkedIn &mdash; all template R', 'Free'], 'dim')],
 widths=[6, 44, 38, 12])
seg(sid, 0, """Ranked. Letter Combinations first, and specifically rehearse the two follow-ups rather than the base """
            """solution.""")
seg(sid, 1, """Bulb Switcher second, and here the thing to rehearse is the routine rather than the answer — because if you """
            """only memorise the answer, a slightly different puzzle leaves you with nothing.""")
seg(sid, 2, """Subsets, permutations, N-queens and word search are not reported for LinkedIn, and they are all template R """
            """with a different options function, so an hour on any one of them covers the rest.""")

sid = steps_list('Five-minute rapid revision',
 [(0, 'How big is the output? That is my complexity floor.', 'ok'),
  (0, 'Choose, explore, un-choose — and copy at the leaf.', 'ok'),
  (1, 'Where can I prune? What makes a branch hopeless?', 'ok'),
  (1, 'Does the caller need all of them, or the first few?', 'ok'),
  (2, 'Empty input. Single element. Recursion depth.', 'shared'),
  (2, 'Working space versus output space — state both separately.', 'shared'),
  (3, 'If it smells like maths: baseline, budget, tabulate, reframe, verify.', 'info'),
  (3, 'What will I offer with my spare four minutes?', 'info')],
 numbered=True)
seg(sid, 0, """Rapid revision. How big is the output, because that is your complexity floor. Choose, explore, un-choose, and """
            """copy at the leaf.""")
seg(sid, 1, """Where can I prune, and what makes a branch hopeless. Does the caller need all of them or just the first """
            """few.""")
seg(sid, 2, """Empty input, single element, recursion depth. Working space versus output space, stated separately.""")
seg(sid, 3, """If it smells like maths: baseline, budget, tabulate, reframe, verify. And the question that is unique to this """
            """chapter — what will I offer with my spare four minutes? Decide that in advance.""")

sid = beat('Mini mock &mdash; 12 minutes', 'Pause here and actually do it',
           '<div class="qwrap"><div class="qlabel">The interviewer asks</div>'
           '<div class="qtext" style="font-size:33px">&ldquo;Given a member&rsquo;s skills and a job&rsquo;s required '
           'skills, list every <b>minimal</b> set of skills the member could add to qualify &mdash; minimal meaning '
           'no proper subset of it also qualifies. Then: some skills <b>imply</b> others, so adding one may satisfy '
           'several requirements.&rdquo;</div></div>',
           """Mini mock, twelve minutes. Given a member's skills and a job's required skills, list every minimal set of """
           """skills the member could add in order to qualify — minimal meaning no proper subset of it also qualifies. And """
           """then the twist: some skills imply others, so adding one skill may satisfy several requirements at once. """
           """Pause and work it.""", kicker='Chapter 8 recap')
think('Twelve minutes. What is the search space, and where is the pruning?', 40,
      """Go. Two questions to answer before you write anything: what exactly is the search space, and where is the """
      """pruning. And watch for the moment the twist changes the shape of the problem.""",
      """Right. Here is the grading.""")

sid = cards('How I would grade that', [
 (0, 'Without implications, it is not a search at all', 'The missing skills are exactly required minus held, and the <b>only</b> minimal set is all of them. Saying that immediately is the strongest possible opening.', 'ok'),
 (0, 'The implications are what create the search', 'Now a skill can cover several requirements, so different additions cover different subsets &mdash; this is a <b>set cover</b> problem, and minimal set covers are what you are enumerating.', 'deny'),
 (1, 'Name the hardness honestly', 'Minimum set cover is NP-hard, and enumerating all minimal covers is exponential in the worst case. Say it &mdash; do not pretend a greedy loop is exact.', 'ok'),
 (1, 'Template R with pruning', 'Backtrack over candidate skills; prune any branch whose remaining skills cannot cover what is left, and skip a skill whose coverage is a subset of one already chosen.', 'ok'),
 (2, 'Minimality needs an explicit check', 'A backtracking enumeration produces non-minimal sets too. Either prune them during the walk, or filter at the leaf &mdash; and say which you chose and why.', 'deny'),
 (2, 'The staff close', '&ldquo;In production I would not enumerate at all &mdash; I would return the <b>cheapest few</b> by a greedy with a ranking signal, because a member wants three suggestions, not every minimal set.&rdquo;', 'ok'),
], cols=2)
seg(sid, 0, """First, the opening I was hoping for. Without implications, this is not a search problem at all: the missing """
            """skills are exactly the required ones minus the held ones, and the only minimal set is all of them. Saying """
            """that in the first thirty seconds is the strongest possible start, because it shows you solved the stated """
            """problem before reaching for machinery.""")
seg(sid, 1, """The implications are what create the search. Once one skill can cover several requirements, different """
            """additions cover different subsets, and you are enumerating minimal set covers.""")
seg(sid, 2, """Then name the hardness honestly: minimum set cover is NP-hard, and enumerating all minimal covers is """
            """exponential in the worst case. Do not present a greedy loop as if it were exact — that is the thing an """
            """interviewer is specifically watching for on this kind of question.""")
seg(sid, 3, """The implementation is template R with two prunes: cut any branch whose remaining candidate skills cannot """
            """possibly cover what is left, and skip a skill whose coverage is a subset of one you already chose.""")
seg(sid, 4, """And minimality needs an explicit check, because a plain backtracking enumeration happily produces """
            """non-minimal sets. Either prune them during the walk or filter at the leaf — and say which you chose and """
            """why, because that is a real trade-off between code complexity and wasted work.""")
seg(sid, 5, """Then the staff close, which is the same move as lesson one: in production I would not enumerate at all. I """
            """would return the cheapest few by a greedy with a ranking signal, because a member wants three suggestions, """
            """not the complete set of minimal covers. Say the algorithm, then say what you would actually ship. Chapter """
            """eight done — next is concurrency, which is the reported pivot.""")
