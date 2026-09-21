# -*- coding: utf-8 -*-
"""Chapter 10, Lesson 1 — rapid revision across every pattern."""
from lib import *

lesson_header('10.1', 'Rapid revision — every pattern in one pass', 'Revision',
              '—', 'Covers all 26 reported questions in the database', '2026', '—', 20,
              """Chapter ten, lesson one. This is the lesson to play the morning of the interview, and it is the only one """
              """that teaches nothing new. Twenty minutes, every pattern in the course, in the order you would meet them. """
              """For each one: the trigger phrase that should make you reach for it, the shape of the answer, and the one """
              """mistake that costs people the question. If a section makes you uneasy, that is your signal — go back to """
              """that chapter rather than pushing on.""")

sid = beat('How to use this', 'Say the answers before I do',
           '<div style="font-size:31px;line-height:1.7">'
           'Each pattern gets about ninety seconds. When the trigger appears on screen, <b>say the answer out loud '
           'before I say it</b>.<br><br>'
           'Anything you cannot say in one breath is not revised &mdash; it is recognised. Those are different things, '
           'and only one of them survives a live interview.<br><br>'
           '<i>Nothing new is introduced here. If something sounds unfamiliar, the chapter is where it lives.</i></div>',
           """How to use this. Each pattern gets about ninety seconds. When the trigger appears on screen, say the answer """
           """out loud before I do.""", step=0)
seg(sid, 1, """And be strict with yourself: anything you cannot say in one breath is not revised, it is merely recognised. """
            """Those are different things, and only one of them survives a live interview where somebody is watching you """
            """type.""")

# ---- trees
sid = table('Chapter 2 &mdash; trees and recursion',
 ['Trigger', 'Reach for', 'The mistake'],
 [(0, ['&ldquo;group by distance from the leaves&rdquo;', 'Return a <b>height</b>; bucket on the way up', 'Two passes when one suffices'], None),
  (0, ['&ldquo;reverse / flip / re-root&rdquo;', 'Return the <b>new root</b>; the parent rewires', 'Rewiring before recursing &mdash; you destroy the links you need'], None),
  (1, ['&ldquo;merge two trees&rdquo;', 'Build <b>new</b> nodes; children keyed in a dictionary', 'Assuming children are ordered; aliasing a shared child'], None),
  (1, ['&ldquo;prune / compact&rdquo;', 'Bottom-up; return the <b>possibly-new</b> subtree root', 'Forgetting the root case &mdash; the reported miss'], None),
  (2, ['&ldquo;weight by depth&rdquo;', 'BFS with a <b>frozen level size</b>, or DFS with a depth argument', 'Resetting the running sum; not freezing the level'], None)],
 widths=[30, 40, 30])
seg(sid, 0, """Chapter two, trees. Group by distance from the leaves: return a height and bucket on the way up. Reverse or """
            """re-root: return the new root, the parent does the rewiring, and recurse before you rewire.""")
seg(sid, 1, """Merge two trees: build new nodes, key the children in a dictionary, never assume they are ordered. Prune or """
            """compact: bottom-up, return the possibly-new subtree root, and remember the root case — that was the edge """
            """case the reporting candidate missed.""")
seg(sid, 2, """Weight by depth: breadth-first with a frozen level size, or depth-first carrying a depth. One sentence each. """
            """If you hesitated on any of those, chapter two is a re-watch.""")

# ---- graphs
sid = table('Chapter 3 &mdash; graphs, BFS and ordering',
 ['Trigger', 'Reach for', 'The mistake'],
 [(0, ['&ldquo;fewest steps&rdquo;, unweighted', '<b>BFS</b>, level counting, mark on <b>enqueue</b>', 'DFS &mdash; it returns <i>a</i> path, not the shortest'], None),
  (0, ['Both endpoints known', '<b>Bidirectional BFS</b>; expand the smaller frontier', 'Expanding the wrong side; off-by-one at the meeting point'], None),
  (1, ['&ldquo;return the path&rdquo;', '<b>Parent map</b>, reconstruct once at the end', 'Storing whole paths in the queue'], None),
  (1, ['&ldquo;dependencies / must come before&rdquo;', '<b>Kahn</b>; waves = parallelism; emitted &ne; total = cycle', 'No cycle check &mdash; and it is always the follow-up'], None),
  (2, ['Weighted edges appear', 'Dijkstra; 0/1 weights &rarr; deque BFS', 'Using BFS anyway and getting a wrong answer silently'], None)],
 widths=[30, 40, 30])
seg(sid, 0, """Chapter three, graphs. Fewest steps on an unweighted graph: breadth-first, counting levels, marking visited on """
            """enqueue. Both endpoints known: bidirectional, always expanding the smaller frontier.""")
seg(sid, 1, """Return the path: parent map, reconstruct once. Dependencies: Kahn's algorithm, where the waves give you the """
            """parallelism answer and a shortfall in the emitted count detects a cycle — and the cycle question is always """
            """the follow-up.""")
seg(sid, 2, """And the moment weights appear, breadth-first is wrong; say Dijkstra, or deque breadth-first for zero-one """
            """weights.""")

# ---- data structure design
sid = table('Chapter 4 &mdash; data structure design',
 ['Trigger', 'Reach for', 'The mistake'],
 [(0, ['&ldquo;all operations O(1)&rdquo;', 'Pointers or indices &mdash; <b>never</b> a heap', 'Reaching for a heap and breaking the stated requirement'], None),
  (0, ['&ldquo;uniform random&rdquo;', '<b>Dense array</b> + index map; remove by swapping with the last', 'Repairing only one of the two values in the map'], None),
  (1, ['&ldquo;min and max, both O(1)&rdquo;', '<b>Bucket list</b>: sorted doubly linked list + key&rarr;bucket map', 'Leaving an empty bucket linked &mdash; the ends then lie'], None),
  (1, ['&ldquo;if several tie, then&hellip;&rdquo;', 'Two orderings &rarr; <b>nest</b>: buckets of LRU lists', 'Trying to force one comparator to do both jobs'], None),
  (2, ['A constructor in the signature', 'Precompute the <b>inputs</b> to the answer; ask how many queries', 'Precomputing every pair &mdash; O(d&sup2;) memory nobody asked for'], None)],
 widths=[30, 40, 30])
seg(sid, 0, """Chapter four, data structure design, the biggest reported cluster after trees and graphs. All operations """
            """constant means pointers or indices and never a heap. Uniform random means a dense array with an index map, """
            """removing by swapping with the last element — and repairing both values in the map, not one.""")
seg(sid, 1, """Minimum and maximum both constant means a bucket list, and never leave an empty bucket linked or the ends """
            """start lying. A stated tie-break means two orderings, which means nesting one structure inside another """
            """rather than forcing a single comparator to do both jobs.""")
seg(sid, 2, """And a constructor in the signature is the interviewer telling you to precompute — the inputs to the answer, """
            """not the answer, and ask how many queries before deciding how much.""")

# ---- windows
sid = table('Chapters 5&ndash;6 &mdash; windows, pointers, hashing, prefixes',
 ['Trigger', 'Reach for', 'The mistake'],
 [(0, ['&ldquo;longest contiguous with at most k&hellip;&rdquo;', '<b>Sliding window</b>; the counter counts what k bounds', 'Coding before stating the invariant'], None),
  (0, ['&ldquo;subsequence&rdquo; (not subarray)', '<b>Not</b> a window &mdash; usually DP', 'Using a window anyway; silently wrong'], None),
  (1, ['&ldquo;pair / triplet with an inequality&rdquo;', '<b>Sort</b>, then pointers inward; count ranges, do not enumerate', 'Enumerating and paying an extra factor of n'], None),
  (1, ['&ldquo;seen before&rdquo;', 'A set. Exact encoding if you can; a real hash needs <b>verification</b>', 'Trusting a hash match without verifying'], None),
  (2, ['&ldquo;range totals, many queries&rdquo;', '<b>Prefix sums</b>; with updates, a <b>Fenwick tree</b>', 'Rebuilding prefixes on every update'], None),
  (2, ['Non-negative values, unconstrained maximum', 'It is <b>degenerate</b> &mdash; find the missing constraint', 'Solving the wrong reading of the question'], None)],
 widths=[30, 40, 30])
seg(sid, 0, """Chapters five and six. Longest contiguous with at most k of something: a sliding window whose counter counts """
            """exactly what k bounds — and state the invariant before writing the loop. Subsequence rather than subarray """
            """is not a window at all.""")
seg(sid, 1, """Pair or triplet with an inequality: sort, then pointers inward, counting whole ranges rather than """
            """enumerating. Seen before: a set, with an exact encoding if the alphabet allows it, and verification if you """
            """are using a real hash.""")
seg(sid, 2, """Range totals with many queries: prefix sums, upgraded to a Fenwick tree the moment updates exist. And """
            """non-negative values with an unconstrained maximum is degenerate — go and find the constraint you were not """
            """told about.""")

# ---- search
sid = table('Chapters 7&ndash;8 &mdash; search, elimination, enumeration',
 ['Trigger', 'Reach for', 'The mistake'],
 [(0, ['Sorted, and you want a position', 'Binary search &mdash; for the <b>index</b>, not the value', 'Mismatching rounding with the update rule &rarr; infinite loop'], None),
  (0, ['&ldquo;smallest x such that P(x)&rdquo;', '<b>Binary search on the answer</b> &mdash; no array needed', 'Not checking that P is monotone'], None),
  (1, ['An expensive oracle', 'Ask what <b>one answer eliminates</b>; count calls, not time', 'Skipping verification &mdash; the sweep proves only a negative'], None),
  (1, ['&ldquo;all combinations&rdquo;', 'Backtracking: choose, explore, <b>un-choose</b>; copy at the leaf', 'Quoting output size as working space; forgetting the un-choose'], None),
  (2, ['Output is exponential', '<b>Prune</b>, <b>defer</b> (lazy), or <b>replace with maths</b>', 'Not volunteering the lazy version on an easy question'], None)],
 widths=[30, 40, 30])
seg(sid, 0, """Chapters seven and eight. Sorted input where you want a position: binary search for the index rather than the """
            """value, and match your rounding to your update rule or you will loop forever. Smallest x such that some """
            """property holds: binary search on the answer, with no array required — but check that the property is """
            """monotone.""")
seg(sid, 1, """An expensive oracle: ask what a single answer eliminates, count calls rather than time, and never skip """
            """verification, because a sweep proves only a negative. All combinations: backtracking with choose, explore, """
            """un-choose, copying at the leaf.""")
seg(sid, 2, """And when the output is exponential, your three moves are prune, defer, or replace with maths — and on an easy """
            """question, volunteer the lazy version rather than waiting to be asked.""")

# ---- concurrency
sid = cards('Chapter 9 &mdash; the pivot, and the fundamentals', [
 (0, '&ldquo;Now make it thread-safe&rdquo;', 'Name the <b>invariant</b> first. One lock, correct, with its cost stated. Then measure. Then stripe, naming what the semantics lose.', 'ok'),
 (0, 'Why not a concurrent collection?', 'It makes each <b>access</b> atomic, not each <b>operation</b>. Your invariant spans three structures.', 'deny'),
 (1, 'TCP vs UDP', 'Reliable ordered stream vs unordered datagrams. TCP pays in latency: handshake plus head-of-line blocking. Hence QUIC.', 'info'),
 (1, 'Paging', 'Isolation and over-commit, paid for in variance: ~1 ns TLB hit vs ~100 &micro;s page fault. Hence thrashing collapses services.', 'info'),
], cols=2)
seg(sid, 0, """Chapter nine, the pivot. Now make it thread-safe: name the invariant first, then one lock with its cost stated """
            """out loud, then measure, then stripe while naming what the semantics lose. And the reason a concurrent """
            """collection does not save you: it makes each access atomic, not each operation, while your invariant spans """
            """three structures.""")
seg(sid, 1, """The two fundamentals reported by name. TCP versus UDP: reliable ordered stream versus unordered datagrams, """
            """with TCP paying in handshake latency and head-of-line blocking — hence QUIC. Paging: isolation and """
            """over-commit paid for in variance, a nanosecond against a hundred microseconds — hence thrashing collapses a """
            """service rather than slowing it gently.""")

# ---- universal
sid = steps_list('The eight sentences that work on <i>any</i> question',
 [(0, 'Restate the problem in my own words, and name what is actually being asked.', 'ok'),
  (0, 'Ask the one clarifying question whose answer would change my approach.', 'ok'),
  (1, 'Give the brute force with its cost, so a working answer exists from minute two.', 'ok'),
  (1, 'Name the insight in one sentence before writing any code.', 'ok'),
  (2, 'Write it, narrating the invariant &mdash; not the syntax.', 'ok'),
  (2, 'State time and space separately, and say average versus worst case.', 'shared'),
  (3, 'Walk one concrete example through, and name the edge cases unprompted.', 'shared'),
  (3, 'Offer the follow-up before they ask: scale, concurrency, or what I would ship instead.', 'info')],
 numbered=True)
seg(sid, 0, """Now the part that matters more than any pattern: eight sentences that work on any question, including one you """
            """have never seen. Restate the problem in your own words. Ask the one clarifying question whose answer would """
            """change your approach.""")
seg(sid, 1, """Give the brute force with its cost, so that a working answer exists from minute two and you are never """
            """empty-handed. Name the insight in one sentence before writing code.""")
seg(sid, 2, """Write it while narrating the invariant rather than the syntax — nobody needs to hear "now I loop over the """
            """array". State time and space separately, and say whether you mean average or worst case.""")
seg(sid, 3, """Walk one concrete example through out loud, and name the edge cases before they ask. Then offer the follow-up """
            """yourself: scale, concurrency, or what you would actually ship instead. Those eight sentences are the """
            """course. Everything else is which pattern fits.""")

sid = cards('The five behaviours that decide the round', [
 (0, 'Never be silent for more than ~15 seconds', 'Narrate dead ends. &ldquo;That would be O(n²), so let me look for structure instead.&rdquo;', 'ok'),
 (0, 'Never have nothing on the board', 'Brute force first buys you a floor. Elegance is an upgrade, not an entry ticket.', 'ok'),
 (1, 'Take hints gracefully', '&ldquo;Divisors &mdash; yes, that is the right lens.&rdquo; Taking a hint well is scored; resisting one is scored too, badly.', 'ok'),
 (1, 'Say what you would ship, not just what passes', 'One sentence at the end: production caveat, or the real design. It is the clearest Staff signal available.', 'ok'),
 (2, 'Ask before assuming', 'Mutability, ordering, duplicates, scale, and what the caller actually needs.', 'shared'),
 (2, 'Finish early &rarr; keep going', 'Offer concurrency, laziness, scale, testing. Spare minutes are an invitation, not a break.', 'shared'),
], cols=2)
seg(sid, 0, """And the five behaviours that decide the round, which have nothing to do with algorithms. Never be silent for """
            """more than about fifteen seconds — narrate the dead ends too. Never have nothing on the board; the brute """
            """force buys you a floor, and elegance is an upgrade rather than an entry ticket.""")
seg(sid, 1, """Take hints gracefully and say so, because taking a hint well is scored — and resisting one is also scored, """
            """badly. Say what you would ship rather than only what passes the tests: one sentence of production caveat at """
            """the end is the clearest staff signal available to you.""")
seg(sid, 2, """Ask before assuming — mutability, ordering, duplicates, scale, and what the caller actually needs. And if you """
            """finish early, keep going: offer concurrency, laziness, scale, testing. Spare minutes are an invitation.""")

sid = statement('Lesson 10.1', 'You are not being tested on recall. You are being watched while you think.',
                'The patterns get you to a correct answer. The eight sentences are what gets you the level.',
                kind='ok')
seg(sid, 0, """One line to close the revision. You are not being tested on recall — you are being watched while you """
            """think.""")
seg(sid, 1, """The patterns get you to a correct answer. The eight sentences are what gets you the level. Next, and last: a """
            """full fifty-minute mock, run in real time, with the clock and the grading. Do that one when you are rested — """
            """it is the closest thing here to the real round.""")
