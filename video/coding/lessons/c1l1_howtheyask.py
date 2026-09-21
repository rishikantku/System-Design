# -*- coding: utf-8 -*-
"""Chapter 1, Lesson 1 — How LinkedIn coding rounds actually work."""
from lib import *

lesson_header('1.1', 'How LinkedIn coding rounds actually work', 'Orientation',
              'High', 'Official prep pack + 8 candidate reports', '2026', 'High', 16,
              """Welcome to the LinkedIn coding course. Before we solve a single problem, I want to spend fifteen minutes on """
              """something more valuable than any algorithm: what this round actually is. Because the mistake I see most often """
              """is a candidate preparing brilliantly for the wrong interview — grinding hard dynamic programming for a round """
              """that has never asked one, and skipping the thing it asks every single time. Everything in this lesson comes """
              """either from the prep pack LinkedIn sent you, or from candidate reports we catalogued. I will tell you which is """
              """which as we go, because one of those is authoritative and the other is evidence.""")

# ---------------------------------------------------------------- the modules
sid = table('The onsite, from LinkedIn\'s own pack', ['Module', 'Length', 'What it scores'], [
 (0, ['**Staff Coding**', '60 min', 'Modularity and extensibility; finding and fixing bugs; pointers, edge cases, abstraction'], [None, None, 'ok']),
 (1, ['**Coding with AI (CWAI)**', '60 min', 'Fundamentals plus intentional AI use; you must use AI and you own the result'], [None, None, 'ok']),
 (2, ['**Systems and Infrastructure Design**', '60 min', 'Completeness, quality of decisions, reasoning about scale and failure'], [None, None, 'info']),
 (3, ['**Host Leader**', '60 min', 'Communication, culture, influence, mentorship, conflict'], [None, None, 'shared']),
], widths=[34, 12, 54])
seg(sid, 0, """Four modules, each an hour. The first is Staff Coding, and read what the pack says it scores, because it is not """
            """what most people assume. Modularity and extensibility. Finding and fixing bugs. Pointers, edge cases, """
            """abstraction. Nowhere does it say speed, and nowhere does it say hard algorithms.""")
seg(sid, 1, """The second is Coding with AI, where you are expected to use an assistant and remain accountable for every line.""")
seg(sid, 2, """Third is systems and infrastructure design, which has its own course.""")
seg(sid, 3, """And fourth is the host leader round. This course covers the two coding modules, and mostly the first one.""")

# ---------------------------------------------------------------- the sentence
sid = quote_slide('From the pack, quoted',
                  'The focus of this interview should be on the modularity and extensibility of the code that you write, as well '
                  'as finding and fixing bugs and other errors. Many of these sessions involve pointers, edge cases, abstraction, '
                  'or all of the above.',
                  sub='"…intended to imitate the kind of day-to-day coding that happens once the design and implementation '
                      'strategy for a project has been settled on."')
seg(sid, 0, """This is the sentence the whole course is built on, quoted from the pack. Read it slowly. Modularity and """
            """extensibility of the code you write. Finding and fixing bugs. Pointers, edge cases, abstraction.""")
seg(sid, 1, """And then this second line, which tells you the mood of the round: it is meant to imitate day-to-day coding after """
            """the design is settled. Not a puzzle sprint. The interviewer is trying to find out what you are like to work with """
            """on a Tuesday afternoon. That changes what a good answer looks like — it means the person who writes a clean, """
            """well-named, tested solution to a medium problem beats the person who speed-runs a hard one and leaves it """
            """unreadable.""")

# ---------------------------------------------------------------- what the research shows
sid = cards('What the question research actually shows', [
 (0, 'Trees and n-ary structures', 'The single biggest cluster — Find Leaves, Upside Down, keyed merge, nested traversal, compact tree.', 'ok'),
 (0, 'Graphs and BFS', 'Word Ladder, The Maze, degrees of connection, build order. The product is a graph.', 'ok'),
 (1, 'Data-structure design', 'All O`one, GetRandom with duplicates, LFU with rank, word-distance index.', 'dp'),
 (1, 'Sliding window and two pointers', 'Max consecutive ones, palindrome with edits, minimum window.', 'dp'),
 (2, 'Hashing, prefix sums, binary search', 'Repeated DNA, the booths problem, K closest elements.', 'info'),
 (2, 'Dynamic programming', 'Appears in **none** of the reports we found. Do not spend your last week here.', 'deny'),
], cols=2)
seg(sid, 0, """Now the evidence. We catalogued forty-two reported questions across two research passes, including your own list of """
            """past LinkedIn questions, which is the strongest signal we have because it is first-party. Here is the """
            """distribution. Trees and n-ary structures are the biggest cluster by a clear margin.""")
seg(sid, 1, """Graphs and breadth-first search are second — which makes sense, because LinkedIn's product is literally a graph """
            """of people. Then data-structure design: implement something with these operations in these complexities.""")
seg(sid, 2, """Then windows, hashing, prefix sums and binary search. And then the finding that changes how you spend your last """
            """week: dynamic programming appears in none of the reports we found. None. I am not telling you it is impossible. """
            """I am telling you that if you have limited hours, the evidence says put them into trees, graphs and design """
            """problems, and treat DP as insurance rather than as the main event.""")

# ---------------------------------------------------------------- the four follow-ups
D = Diagram('The four follow-ups that appear again and again')
D.box('f1', 120, 130, 800, 140, '"Now make it thread-safe"', 'Reported even on a phone screen (Mar 2026)', kind='deny', step=0)
D.box('f2', 120, 300, 800, 140, '"What if the input is 1000× bigger?"', 'Memory, streaming, recursion depth', kind='shared', step=1)
D.box('f3', 120, 470, 800, 140, '"Do it iteratively / in O(1) space"', 'Because the recursive stack is not free', kind='info', step=2)
D.box('f4', 120, 640, 800, 140, '"How would you test this?"', 'Name the cases before you are asked', kind='ok', step=3)
D.label(1000, 200, 'These are not four questions.\nThey are one question:', kind='neutral', step=4, w=820, size='m')
D.label(1000, 320, '**Can this person take a working\nsolution into production?**', kind='ok', step=4, w=820, size='l')
D.label(1000, 520, 'Answer the production pivot **before** it is asked,\nand you have made the interviewer\'s decision for them.',
        kind='dp', step=5, w=820, size='m')
sid = D.build()
seg(sid, 0, """Now the most useful pattern in the whole research. Across the reports, the same four follow-ups keep appearing. """
            """First: now make it thread-safe. One candidate got that on a phone screen in March 2026, after a medium string """
            """question. Not onsite. Phone screen.""")
seg(sid, 1, """Second: what if the input is a thousand times bigger? That is a question about memory, about streaming, and very """
            """often about recursion depth.""")
seg(sid, 2, """Third: do it iteratively, or do it in constant space. Which is really the same question wearing a different hat — """
            """they want to know if you think about the stack as a real resource.""")
seg(sid, 3, """And fourth: how would you test this?""")
seg(sid, 4, """Here is the thing. Those are not four different questions. They are one question asked four ways: can this person """
            """take a working solution into production?""")
seg(sid, 5, """So the single highest-leverage habit in this entire course is this. When your solution works, do not stop and wait. """
            """Say: this is order n, the recursion is order h which is order n on a skewed input so I would switch to an """
            """explicit stack, here is what I would test, and if this were shared across threads here is what I would change. """
            """You have just answered all four follow-ups unprompted, and you have made the interviewer's decision for them.""")

# ---------------------------------------------------------------- the learning loop
sid = steps_list('The loop every lesson follows', [
 (0, 'See the question — as the interviewer would say it', 'info'),
 (0, '**Think** — a timed pause, before any hint', 'shared'),
 (1, 'Brute force, and why it is not enough', 'com'),
 (1, '**The key observation** — the one sentence the solution comes from', 'ok'),
 (2, 'Pattern → data structure → algorithm', 'dp'),
 (2, 'C# implementation, walked line by line', 'info'),
 (3, 'Complexity, said the way you should say it', 'info'),
 (3, 'Follow-ups: reported, then staff-level', 'shared'),
 (4, '**How to say it in the interview** — the verbal script', 'ok'),
])
seg(sid, 0, """Every lesson in this course follows the same loop, and the loop is the product. You see the question as an """
            """interviewer would say it. Then a timed pause where you think, out loud, before I say anything.""")
seg(sid, 1, """Then the brute force, honestly priced — because naming it is a point in your favour, not a confession. Then the """
            """key observation, which I will always try to compress into a single sentence you could say in a room.""")
seg(sid, 2, """Then the chain: pattern, data structure, algorithm. Then the code in C#, walked block by block.""")
seg(sid, 3, """Then complexity, phrased the way you should phrase it out loud. Then follow-ups, split into ones candidates """
            """actually reported and ones a staff interviewer might add.""")
seg(sid, 4, """And every lesson ends with the verbal script: what you actually say, in order. Because the thing being graded is """
            """not your solution. It is your solution plus your explanation of it, and most people only practise half of that.""")

# ---------------------------------------------------------------- how to use
sid = compare('How to use this course',
 ('Do', 'ok', 0, ['Pause on the think slide and answer out loud',
                  'Write the code yourself before the code slide',
                  'Say complexity before I do',
                  'Rewatch one chapter the night before, not everything']),
 ('Do not', 'deny', 1, ['Watch it like television',
                        'Skip the brute-force section because you "know" the answer',
                        'Memorise my sentences — steal the structure instead',
                        'Treat the reported questions as predictions']))
seg(sid, 0, """How to use it. Pause on the think slide, every time, and say something out loud even if it is wrong. Write the """
            """code before I show you mine. Try to beat me to the complexity. And when revision time comes, watch one chapter, """
            """not the whole course — that is why each lesson is its own file.""")
seg(sid, 1, """And what not to do. Do not watch this like television; the pause is where the learning happens. Do not skip the """
            """brute-force section when you already know the answer, because naming and pricing the brute force is a scored """
            """behaviour, not a formality. Do not memorise my exact sentences — take the structure and use your own words. And """
            """above all, do not treat these questions as predictions. They are the shape of what has been asked. Prepare the """
            """shape, not the list.""")

# ---------------------------------------------------------------- chapter map
sid = table('The chapters, ordered by the evidence', ['Chapter', 'Why it is here', 'Lessons'], [
 (0, ['**2 · Trees and n-ary structures**', 'Biggest cluster in the research', 'Find Leaves · Upside Down · keyed merge · nested and compact'], [None, None, None]),
 (1, ['**3 · Graphs and BFS**', 'Second biggest; the product is a graph', 'Word Ladder · The Maze · degrees of connection · build order'], [None, None, None]),
 (2, ['4 · Data-structure design', 'The "implement X with these complexities" family', 'All O`one · GetRandom · word distance · LFU with rank'], [None, None, None]),
 (3, ['5–8 · Windows, hashing, search, backtracking', 'The remaining reported clusters', 'Coming after chapters 2 and 3'], [None, None, None]),
 (4, ['9–10 · Concurrency and the mock', 'The production pivot, then a timed 50-minute mock', 'Coming after chapters 2 and 3'], [None, None, None]),
], widths=[32, 30, 38])
seg(sid, 0, """Here is the map. Chapter two is trees, because that is where the evidence points hardest, and we start there """
            """immediately.""")
seg(sid, 1, """Chapter three is graphs and breadth-first search.""")
seg(sid, 2, """Chapter four is data-structure design — the implement-this-with-these-complexities family that LinkedIn has been """
            """asking for years.""")
seg(sid, 3, """Chapters five through eight cover the remaining clusters: windows, hashing and prefix sums, binary search and """
            """elimination, backtracking and the occasional maths problem.""")
seg(sid, 4, """And chapters nine and ten are the production pivot — concurrency, thread-safety, testing — and then a full """
            """fifty-minute mock. Chapters two and three are ready now; the rest follow.""")

sid = statement('Before the first problem', 'The round imitates day-to-day coding, not a puzzle sprint.',
                'Clean, testable, explained. Then answer the production follow-up before it is asked.', kind='ok')
seg(sid, 0, """So, before we touch the first problem, hold this in your head. The round is imitating day-to-day coding.""")
seg(sid, 1, """Clean, testable, explained out loud — and then the production pivot, volunteered rather than dragged out of you. """
            """That is the whole grading rubric in one sentence. Next lesson: Find Leaves of Binary Tree, and the first key """
            """observation of the course. See you there.""")
