# -*- coding: utf-8 -*-
"""Chapter 7, Lesson 2 — Find the Celebrity."""
from lib import *

lesson_header('7.2', 'Find the Celebrity — elimination, and the cost of an API call', 'Elimination · adversary argument',
              'High', 'Your list + a Taro DSA-round report', '2025', 'High', 16,
              """Chapter seven, lesson two. Find the Celebrity, which is on your own list and also appeared in a Taro """
              """report describing DSA rounds covering linked lists, breadth-first search and this. It is the only question """
              """in the course where the thing you are optimising is not time or memory — it is the number of API calls. """
              """That makes it unusually relevant to an infrastructure interview, because calls to another service are """
              """exactly what you budget for in real systems.""")

sid = beat('Question', 'The problem, as they pose it',
           '<div class="qwrap"><div class="qtext" style="font-size:34px;line-height:1.4">'
           'Among n people there may be one <b>celebrity</b>: someone whom <b>everyone else knows</b>, and who '
           '<b>knows nobody</b>.<br><br>'
           'You may only ask one kind of question: <b>Knows(a, b)</b> — does a know b? Each call is expensive.<br><br>'
           'Find the celebrity, or report that there is none, using as few calls as possible.</div></div>',
           """The question. Among n people there may be one celebrity — someone whom everyone else knows, and who knows """
           """nobody. You have exactly one primitive available: Knows of a and b, does a know b. Each call is expensive. """
           """Find the celebrity, or report that there is none, in as few calls as you can.""")

think('The brute force is n² calls. What does a single call actually tell you?', 30,
      """Pause. The brute force asks every pair, which is n squared calls. Before optimising, ask the sharper question: """
      """what does one single call actually tell you? Be precise about both outcomes.""",
      """This is the question that unlocks it, so let us answer it carefully.""")

sid = beat('Key observation', 'Every call eliminates a candidate — whatever the answer is',
           '<div class="bigidea">Ask <b>Knows(a, b)</b>.<br><br>'
           'If <b>yes</b>: a knows someone, so <b>a is not the celebrity</b>.<br>'
           'If <b>no</b>: someone does not know b, so <b>b is not the celebrity</b>.</div>'
           '<div style="margin-top:24px;font-size:30px;line-height:1.7">'
           'Either way, <b>one call removes exactly one candidate</b>. So n &minus; 1 calls leave one survivor &mdash; '
           'and the celebrity, if one exists, is guaranteed to be that survivor.</div>',
           """Ask Knows of a and b. If the answer is yes, then a knows somebody, and a celebrity knows nobody, so a is """
           """eliminated. If the answer is no, then somebody does not know b, and a celebrity is known by everybody, so b """
           """is eliminated.""", step=0)
seg(sid, 1, """Either way — and this is the beautiful part — one call removes exactly one candidate. There is no wasted """
            """call, no branch where you learn nothing. So n minus one calls leave exactly one survivor, and if a celebrity """
            """exists at all, it must be that survivor. You have gone from n squared to n minus one just by noticing what a """
            """single answer tells you.""")

D = Diagram('The elimination sweep over 5 people')
D.box('c0', 130, 160, 340, 120, 'candidate = 0', 'no calls yet', kind='info', step=0)
D.label(520, 180, 'Knows(0, 1)?', kind='neutral', step=1, w=420, size='m')
D.box('c1', 980, 160, 480, 120, 'yes &rarr; 0 is out', 'candidate = 1', kind='ok', step=1)
D.label(520, 300, 'Knows(1, 2)?', kind='neutral', step=2, w=420, size='m')
D.box('c2', 980, 280, 480, 120, 'no &rarr; 2 is out', 'candidate stays 1', kind='ok', step=2)
D.label(520, 420, 'Knows(1, 3)?', kind='neutral', step=3, w=420, size='m')
D.box('c3', 980, 400, 480, 120, 'yes &rarr; 1 is out', 'candidate = 3', kind='ok', step=3)
D.label(520, 540, 'Knows(3, 4)?', kind='neutral', step=4, w=420, size='m')
D.box('c4', 980, 520, 480, 120, 'no &rarr; 4 is out', 'candidate stays 3', kind='ok', step=4)
D.label(130, 680, '4 calls, 4 eliminations, one survivor: **3**. But &ldquo;survivor&rdquo; is **not** the same as '
                  '&ldquo;celebrity&rdquo; &mdash; we have only shown nobody else can be.',
        kind='deny', step=5, w=1700, size='l')
D.label(130, 790, 'So a **verification pass** is mandatory: check 3 against everyone, both directions.',
        kind='dp', step=6, w=1700, size='m')
sid = D.build()
seg(sid, 0, """Let us sweep five people. Start with person zero as the candidate.""")
seg(sid, 1, """Does zero know one? Yes — so zero is out, and one becomes the candidate.""")
seg(sid, 2, """Does one know two? No — so two is out, and one survives.""")
seg(sid, 3, """Does one know three? Yes — one is out, three becomes the candidate.""")
seg(sid, 4, """Does three know four? No — four is out, three survives.""")
seg(sid, 5, """Four calls, four eliminations, one survivor: person three. But — and this is where candidates lose the """
            """question — survivor is not the same as celebrity. All we have shown is that nobody else can be the """
            """celebrity. We have not shown that this one is.""")
seg(sid, 6, """So a verification pass is mandatory: check the survivor against everyone, in both directions. Skipping it is """
            """the single most common failure on this problem, and it is a correctness bug, not a polish issue.""")

sid = cards('Why verification is not optional', [
 (0, 'The sweep proves a negative', 'It proves &ldquo;these n&minus;1 people are not the celebrity&rdquo;. It never proves anything positive about the survivor.', 'deny'),
 (0, 'There may be no celebrity at all', 'The problem says <i>may</i>. With no celebrity, the sweep still returns a survivor &mdash; confidently and wrongly.', 'deny'),
 (1, 'Verify both directions', 'The survivor must know <b>nobody</b>, and <b>everybody</b> must know them. Two conditions, both needed.', 'ok'),
 (1, 'Skip self-comparisons', 'Knows(i, i) is meaningless and some graders throw on it. Guard it.', 'shared'),
 (2, 'You can skip half the checks', 'For people eliminated <i>before</i> the survivor became candidate, one direction is already known. Mention it; only implement it if they want it.', 'ok'),
 (2, 'Total calls', 'n&minus;1 for the sweep, up to 2(n&minus;1) to verify &rarr; <b>at most 3n</b>. Still O(n).', 'ok'),
], cols=2)
seg(sid, 0, """Why verification is not optional. The sweep proves a negative — these n minus one people are not the celebrity """
            """— and it never proves anything positive about the survivor. And the problem says there may be a celebrity, """
            """which means there may not be, and in that case the sweep still hands you a survivor, confidently and """
            """wrongly.""")
seg(sid, 1, """Verify in both directions: the survivor must know nobody, and everybody must know the survivor. Two """
            """conditions, and you need both. Skip self-comparisons, because asking whether someone knows themselves is """
            """meaningless and some implementations throw.""")
seg(sid, 2, """There is an optimisation available — for people eliminated before the survivor became the candidate, one """
            """direction is already known from the sweep — and my advice is to mention it and only implement it if they """
            """ask, because it complicates the code for a constant factor. Total calls are n minus one for the sweep plus """
            """at most two n minus two for verification, so at most about three n. Still linear.""")

CODE = '''public int FindCelebrity(int n) {
    int candidate = 0;

    for (int i = 1; i < n; i++)                        // PASS 1: n-1 calls, one elimination each
        if (Knows(candidate, i))                       // candidate knows someone -> candidate is out
            candidate = i;                             // otherwise i is out; candidate survives

    for (int i = 0; i < n; i++) {                      // PASS 2: verification is mandatory
        if (i == candidate) continue;                  // never ask Knows(x, x)
        if (Knows(candidate, i)) return -1;            // a celebrity knows nobody
        if (!Knows(i, candidate)) return -1;           // everybody must know a celebrity
    }
    return candidate;
}'''
code_slide('The C# implementation', CODE, [
 ('2-6', """Pass one is four lines and it is the whole insight. Walk once. If the current candidate knows i, the candidate """
           """is eliminated and i takes over; otherwise i is eliminated and the candidate stays. Exactly one call per step, """
           """exactly one elimination per call."""),
 ('8-10', """Pass two, and the comment is doing real work here: verification is mandatory. Skip the self-comparison first, """
            """because it is meaningless and can throw."""),
 ('11-12', """Then the two conditions. If the survivor knows anyone, there is no celebrity. If anyone does not know the """
             """survivor, there is no celebrity. Note that we return minus one rather than the survivor — a wrong """
             """confident answer is worse than an honest none."""),
 ('14', """And only after surviving both checks do we return the candidate. Fourteen lines, at most three n calls, and the """
          """correctness argument is two sentences long — which is why this is such a well-liked interview question."""),
])

sid = beat('The part that impresses', 'Prove you cannot do better than n &minus; 1',
           '<div style="font-size:30px;line-height:1.7">'
           'Suppose an algorithm makes fewer than n &minus; 1 calls. Model each call as an edge between two people. '
           'With fewer than n &minus; 1 edges, the graph of "people you have asked about" is <b>disconnected</b> '
           '&mdash; there are at least two components.<br><br>'
           'An adversary can then <b>relabel one component</b> so that the celebrity sits in the other one, and every '
           'answer you received stays consistent. You cannot distinguish the two worlds.<br><br>'
           '<b>So n &minus; 1 calls are necessary, and our sweep achieves it.</b> The algorithm is optimal, not just '
           'fast.</div>',
           """Now the part that impresses, and it is worth thirty seconds of your interview. Can you do better than n """
           """minus one calls? No, and here is the argument.""", step=0)
seg(sid, 1, """Suppose an algorithm makes fewer than n minus one calls. Model each call as an edge between two people. With """
            """fewer than n minus one edges the graph is disconnected — there are at least two components, because """
            """connecting n nodes requires n minus one edges.""")
seg(sid, 2, """An adversary can then relabel one component so that the celebrity sits in the other one, and every answer """
            """you already received stays consistent with the new labelling. You cannot tell the two worlds apart, so you """
            """cannot be certain of your answer.""")
seg(sid, 3, """Therefore n minus one calls are necessary, and our sweep achieves exactly that. The algorithm is not merely """
            """fast, it is optimal. Being able to give a lower-bound argument is rare in candidates and it is exactly the """
            """kind of reasoning a staff-level interviewer remembers afterwards.""")

sid = table('Complexity, in the units that matter',
 ['Measure', 'Cost', 'Note'],
 [(0, ['API calls', 'n &minus; 1 + up to 2(n&minus;1)', 'The only expensive resource. <b>Optimal</b> for pass 1'], None),
  (1, ['Time', 'O(n)', 'Assuming each call is O(1); if not, the call cost dominates everything'], None),
  (2, ['Space', 'O(1)', 'One integer. No caching, no matrix &mdash; and that is worth pointing out'], None),
  (3, ['Brute force', 'O(n&sup2;) calls', 'What you are being compared against'], 'dim')],
 widths=[22, 28, 50])
seg(sid, 0, """Complexity, stated in the units the problem cares about. API calls: n minus one for the sweep, up to two more """
            """per person to verify, and pass one is provably optimal.""")
seg(sid, 1, """Time is linear assuming each call is constant — and if calls are not constant, which is the realistic case, """
            """then the call cost dominates everything else you do.""")
seg(sid, 2, """Space is a single integer. No caching, no adjacency matrix. That is worth pointing out, because a candidate """
            """who builds an n-by-n matrix has both used quadratic memory and made quadratically many calls to fill it.""")
seg(sid, 3, """And the brute force you are being compared against is n squared calls.""")

followups(
 ['"What if there can be more than one celebrity?" — impossible: two celebrities would have to know each other, contradicting "knows nobody"',
  '"Prove the lower bound" — the adversary/connectivity argument above',
  '"Reduce the verification calls" — reuse what pass 1 already told you; a constant-factor win'],
 ['"Knows() is a network call with 50 ms latency" — 3n sequential calls is minutes; batch the verification pass and run it concurrently',
  '"Knows() can fail or time out" — now you need retries and a policy for an unknown answer; an unknown answer eliminates nobody, so the sweep must handle it',
  '"Knows() is eventually consistent" — the relation can change mid-algorithm; your answer is then only valid as of a snapshot, and you should say so'],
 """Follow-ups. Can there be more than one celebrity? No, and the proof is one line: two celebrities would each have to """
 """know the other, contradicting the requirement that a celebrity knows nobody. Proving the lower bound is the adversary """
 """argument. And reducing verification calls is a constant-factor win by reusing what pass one already told you.""",
 """The staff-level follow-ups are where this question becomes an infrastructure question, and I would prepare these """
 """carefully because they suit LinkedIn. If Knows is a network call with fifty milliseconds of latency, then three n """
 """sequential calls is minutes of wall clock — so you batch the verification pass and issue it concurrently, while """
 """noting that pass one is inherently sequential because each call depends on the previous result. If Knows can fail or """
 """time out, an unknown answer eliminates nobody, and your sweep needs an explicit policy for that. And if the relation """
 """is eventually consistent, it can change while you are running, which means your answer is only valid as of a """
 """snapshot — saying that out loud is the difference between a coding answer and an engineering one.""")

interview_script([
 '"One call eliminates exactly one candidate: if a knows b, a is out; if not, b is out."',
 '"So a single sweep of n−1 calls leaves one survivor, and only that person can possibly be the celebrity."',
 '"But the sweep only proves a negative, so I must verify the survivor in both directions — and there may be no celebrity at all."',
 '"That is n−1 plus at most 2(n−1) calls, so O(n), against O(n²) for the brute force."',
 '"n−1 is also optimal: with fewer calls the query graph is disconnected and an adversary can move the celebrity."',
 '"If Knows() is a real network call, I would batch and parallelise the verification pass — pass 1 has to stay sequential."',
], [
 """The script, and the first two lines are the algorithm. Say the elimination property before you describe any loop, """
 """because the loop is obvious once the property is stated.""",
 """Then the verification, framed as "the sweep proves a negative", which is the phrasing that makes the necessity """
 """obvious rather than pedantic. Give the call counts.""",
 """Then the two lines that set you apart: the optimality argument, and the systems observation about latency. Either one """
 """alone would be a strong finish; together they turn a fifteen-line function into a conversation about how you think """
 """about calling other people's services.""",
])

sid = statement('Lesson 7.2', 'Ask what one answer eliminates, before asking what the algorithm is.',
                'And when a proof shows you cannot do better, say it — optimality is a stronger claim than speed.',
                kind='ok')
seg(sid, 0, """One line. Ask what a single answer eliminates, before asking what the algorithm is. That question solves this """
            """problem, and it solves most elimination problems.""")
seg(sid, 1, """And when you can show that nobody could do better, say so — optimality is a much stronger claim than speed. """
            """Next is the chapter seven recap, and then backtracking and maths.""")
