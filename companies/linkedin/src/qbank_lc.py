# -*- coding: utf-8 -*-
"""Verified LeetCode cross-reference for the InterviewDB question list.

Every number, title, slug and difficulty below was read from LeetCode's own problem index
(https://leetcode.com/api/problems/all/, 4,068 problems, fetched 29 Sep 2026) - not typed
from memory. A wrong slug is a 404; a wrong number is worse, because it looks right.

`rel` is deliberately allowed to say the mapping is weak or absent. A number appearing on a
LinkedIn-tagged list does not make it one of the 17 questions below it, and forcing a mapping
would send the reader to revise the wrong problem.

  exact    - the same problem, allowing for wording
  variation- the same core, with a changed constraint or return value
  pattern  - a different problem that trains the same technique
  followup - the natural harder sibling
  none     - no meaningful relation to any of the 17; a separately tagged LinkedIn classic
"""

FETCHED = '29 Sep 2026'
INDEX_SIZE = 4068

# (number, title, slug, difficulty, premium, linked question ids, relation, note)
ROWS = [
    (17, 'Letter Combinations of a Phone Number', 'letter-combinations-of-a-phone-number', 'Medium', False,
     ['q11'], 'variation',
     'The **inverse** of Q11. LeetCode generates every letter string a number could spell; Q11 asks which '
     '*known words* it spells. Generating is exponential, looking up is O(1) - and noticing that the '
     'direction is reversed is the whole insight of Q11. Reader-reported independently.'),

    (46, 'Permutations', 'permutations', 'Medium', False,
     [], 'none',
     'Backtracking. No relation to any of the 17; a separately LinkedIn-tagged classic. Worth a rep '
     'because it is the template for "enumerate all arrangements".'),

    (47, 'Permutations II', 'permutations-ii', 'Medium', False,
     [], 'followup',
     'Follow-up to 46: duplicates in the input. The de-duplication trick (sort, then skip a value equal '
     'to the previous one at the same depth) is the only new idea.'),

    (57, 'Insert Interval', 'insert-interval', 'Medium', False,
     ['q9'], 'variation',
     'The closest public problem to Q9. Identical merge-on-insert logic. The difference is what is '
     'returned: 57 rebuilds and returns the list in O(n); Q9 must keep a **running covered total** so '
     'the query is O(1) and the insert stays O(log n). LeetCode 715 Range Module (Hard) is the version '
     'that keeps state across calls.'),

    (72, 'Edit Distance', 'edit-distance', 'Medium', False,
     ['q8'], 'variation',
     'Q8 fixes the cost model to one substitution per step and asks for the shortest path, so it is BFS. '
     '72 allows insert, delete and replace and asks for a distance, so it is DP. **Q8’s third '
     'follow-up - letters may be added or removed - is exactly the bridge**: adjacency becomes '
     '"edit distance 1", and the dictionary graph now links words of different lengths.'),

    (76, 'Minimum Window Substring', 'minimum-window-substring', 'Hard', False,
     ['q3'], 'pattern',
     'Same two-pointer window as Q3, with a much harder validity predicate (a multiset of required '
     'characters rather than a count of zeros). If Q3 feels easy, this is the one that proves you '
     'understand *why* the left pointer never moves backwards. Reader-reported independently.'),

    (88, 'Merge Sorted Array', 'merge-sorted-array', 'Easy', False,
     ['q17'], 'pattern',
     'The two-pointer merge, in its simplest form. Related to Q17 only in instinct - walk two inputs '
     'together rather than concatenating and re-sorting. Q17 merges by key, not by order.'),

    (100, 'Same Tree', 'same-tree', 'Easy', False,
     ['q17'], 'pattern',
     'The lockstep two-tree recursion that Q17 is built on. Same Tree returns a bool at the point where '
     'Q17 returns a merged node, and it is worth writing once to see that the shape is identical.'),

    (103, 'Binary Tree Zigzag Level Order Traversal', 'binary-tree-zigzag-level-order-traversal', 'Medium', False,
     ['q10'], 'pattern',
     'Level-by-level processing, measured from the **root**. Q10’s levels are measured from the '
     '**leaves**, which is why BFS does not work for it and a post-order pass does. Doing both back to '
     'back is the cleanest way to feel that difference.'),

    (127, 'Word Ladder', 'word-ladder', 'Hard', False,
     ['q8'], 'exact',
     'The same problem as Q8. **One difference that will cost you marks if you miss it:** LeetCode 127 '
     'returns the number of *words* in the sequence; Q8 as stated returns the number of '
     '*transformations*. For hit → cog those are 5 and 4. Say which you are returning. Two '
     'independent reports in the existing research.'),

    (149, 'Max Points on a Line', 'max-points-on-a-line', 'Hard', False,
     [], 'none',
     'No relation to the 17. Included here because it is the most likely public equivalent of '
     '*Minimize Points Distance*, one of the interviewdb titles whose statement is still unknown - '
     'a hint to follow, not a claim.'),

    (156, 'Binary Tree Upside Down', 'binary-tree-upside-down', 'Medium', True,
     ['q10', 'q17'], 'pattern',
     'Tree re-pointing rather than tree reading. The same care Q17’s side-heavy follow-up needs: '
     'reassign links in an order where nothing you still need has been overwritten. Reader-reported, '
     'with a noted variant using a 0/1 right child.'),

    (160, 'Intersection of Two Linked Lists', 'intersection-of-two-linked-lists', 'Easy', False,
     ['q5'], 'pattern',
     'Two traversals that must meet. The classic solution equalises the lengths first - the same '
     'instinct as Q5’s follow-up, where you expand the smaller frontier because the cost of a '
     'round is the size of the side you expand.'),

    (205, 'Isomorphic Strings', 'isomorphic-strings', 'Easy', False,
     ['q11'], 'pattern',
     'A stronger link than it looks. Q11’s keypad signature is a character → class mapping '
     'used to build a canonical key; isomorphism checks whether such a mapping exists. Both are the '
     '"reduce to a canonical form, then compare in O(1)" move.'),

    (215, 'Kth Largest Element in an Array', 'kth-largest-element-in-an-array', 'Medium', False,
     ['q13'], 'pattern',
     'Selection by rank. Q13 keeps the k highest-ranked items alive under a capacity, which is the '
     'streaming form of the same question: a bounded structure that always knows its weakest member.'),

    (235, 'Lowest Common Ancestor of a Binary Search Tree', 'lowest-common-ancestor-of-a-binary-search-tree', 'Medium', False,
     [], 'none',
     'A separately tagged LinkedIn classic, not one of the 17. The BST version is the one where the '
     'answer is a single descent with no recursion needed.'),

    (236, 'Lowest Common Ancestor of a Binary Tree', 'lowest-common-ancestor-of-a-binary-tree', 'Medium', False,
     [], 'none',
     'Also a separately tagged classic. Already worked in the existing coding page, including the '
     'k-node follow-up.'),

    (243, 'Shortest Word Distance', 'shortest-word-distance', 'Easy', True,
     [], 'none',
     'The one-shot version. Only interesting as the setup for 244.'),

    (244, 'Shortest Word Distance II', 'shortest-word-distance-ii', 'Medium', True,
     ['q11', 'q13'], 'pattern',
     'The design lesson behind Q11 and Q13: **preprocess once, answer many queries cheaply.** 244 '
     'indexes word → positions; Q11 indexes signature → words. Reader-reported independently.'),

    (256, 'Paint House', 'paint-house', 'Medium', True,
     ['q14'], 'pattern',
     'A weak link, stated as such. Both walk a line under an adjacency constraint, but 256 is DP over '
     'costs and Q14 is a greedy count. Do not use 256 to prepare Q14.'),

    (261, 'Graph Valid Tree', 'graph-valid-tree', 'Medium', True,
     ['q2', 'q15'], 'pattern',
     'Cycle detection plus connectivity. Q2 needs the *undirected* walk over every component; Q15 needs '
     'the *directed* one, where a cycle means a back edge to a node still on the current path. 261 is '
     'the cleanest place to get the undirected version right.'),

    (270, 'Closest Binary Search Tree Value', 'closest-binary-search-tree-value', 'Easy', True,
     [], 'none',
     'A separately tagged LinkedIn classic, not one of the 17.'),

    (272, 'Closest Binary Search Tree Value II', 'closest-binary-search-tree-value-ii', 'Hard', True,
     [], 'followup',
     'Follow-up to 270: the k closest, which turns a descent into an in-order walk with a bounded '
     'deque or heap. A genuinely good LinkedIn question; just not one of the 17.'),

    (273, 'Integer to English Words', 'integer-to-english-words', 'Hard', False,
     [], 'none',
     'A separately tagged classic. Pure case analysis; no relation to the 17. Worth one rep because it '
     'is almost entirely about decomposing the problem cleanly, which is what the Staff Coding module '
     'says it scores.'),

    (277, 'Find the Celebrity', 'find-the-celebrity', 'Medium', True,
     [], 'none',
     'A separately tagged classic, already worked in the existing coding page. Reader-reported.'),

    (297, 'Serialize and Deserialize Binary Tree', 'serialize-and-deserialize-binary-tree', 'Hard', False,
     ['q17'], 'variation',
     '**Q17’s first follow-up, exactly.** 297 is the binary case with positional children; Q17 needs '
     'keyed children with unique sibling keys, which changes what has to be written: a key per child and '
     'a child count or terminator, rather than null markers.'),

    (323, 'Number of Connected Components in an Undirected Graph', 'number-of-connected-components-in-an-undirected-graph', 'Medium', True,
     ['q2'], 'pattern',
     'Q2 fails on hidden components if you only walk from one start node, which is the mistake 323 is '
     'designed to catch. Same outer loop over every unvisited vertex.'),

    (344, 'Reverse String', 'reverse-string', 'Easy', False,
     [], 'none',
     'A warm-up. Listed for completeness; no relation to the 17.'),

    (347, 'Top K Frequent Elements', 'top-k-frequent-elements', 'Medium', False,
     ['q13'], 'pattern',
     'Map plus heap - the two structures Q13 combines. 347 counts then selects; Q13 must keep the '
     'selection correct while items arrive and leave.'),

    (364, 'Nested List Weight Sum II', 'nested-list-weight-sum-ii', 'Medium', True,
     ['q10'], 'pattern',
     '**The strongest non-obvious link in this table.** 364 weights each element by depth measured '
     '*from the bottom*, which is precisely what Q10’s peel round is. Both need one pass that '
     'computes height bottom-up rather than passing depth top-down. Reader-reported independently. '
     '(Supplied twice in the list.)'),

    (380, 'Insert Delete GetRandom O(1)', 'insert-delete-getrandom-o1', 'Medium', False,
     ['q12'], 'exact',
     'The same structure as Q12: list plus index map, swap-with-last on delete. Q12 replaces GetRandom '
     'with **RemoveRandom**, which is the composition of the two and needs no new idea. LeetCode 381 is '
     'the duplicates-allowed version, which is Q12’s follow-up and is Hard. Reader-reported.'),

    (384, 'Shuffle an Array', 'shuffle-an-array', 'Medium', False,
     ['q4', 'q12'], 'pattern',
     'Fisher-Yates. Related to Q4 and Q12 through the same demand: every outcome equally likely, and a '
     'plausible-looking shortcut that is subtly biased. The classic wrong shuffle picks any index rather '
     'than one from the unshuffled tail.'),

    (432, 'All O`one Data Structure', 'all-oone-data-structure', 'Hard', False,
     ['q1', 'q13'], 'pattern',
     'The hardest of the "ordered structure in O(1)" family, and reader-reported. It is the right '
     'preparation for the Q13 follow-up where ranks stop being static: buckets of equal-count keys in a '
     'doubly-linked list, which is also how LFU is built.'),

    (460, 'LFU Cache', 'lfu-cache', 'Hard', False,
     ['q1', 'q13'], 'variation',
     'Same cache skeleton as Q1 and Q13; only the eviction key changes - frequency instead of recency, '
     'TTL or rank. Reported twice in the existing research, once with a **GetRank()** method and LRU as '
     'the tiebreaker, which sits almost exactly between Q1 and Q13.'),

    (490, 'The Maze', 'the-maze', 'Medium', True,
     ['q5', 'q8'], 'pattern',
     'BFS where generating the neighbours is the work - the ball rolls until it hits a wall. Q8 has the '
     'same shape: the neighbour function (wildcard buckets) is where the thinking goes, not the search. '
     'Reader-reported and already worked in the coding page.'),

    (528, 'Random Pick with Weight', 'random-pick-with-weight', 'Medium', False,
     ['q4'], 'pattern',
     'The **mirror image of Q4**. 528 turns a uniform source into a biased one (prefix sums plus binary '
     'search); Q4 turns a biased source into a uniform one (debiasing plus rejection). Prepare them '
     'together - being able to go both ways is what the question is really testing.'),

    (617, 'Merge Two Binary Trees', 'merge-two-binary-trees', 'Easy', False,
     ['q17'], 'variation',
     'The binary case of Q17: overlap and the values are summed, otherwise the non-null node is used. '
     'Q17 generalises it in the direction that matters - children identified by **key** rather than by '
     'position, so child lookup becomes a dictionary probe and "absent branch" becomes a real case. '
     'Reader-reported, and the reader\u2019s own note already describes the n-ary keyed variant.'),

    (636, 'Exclusive Time of Functions', 'exclusive-time-of-functions', 'Medium', False,
     ['q6', 'q7'], 'pattern',
     'A stack over a log of start/end events. Shares Q6’s nesting discipline and Q7’s '
     'time-ordering, without the concurrency.'),

    (695, 'Max Area of Island', 'max-area-of-island', 'Medium', False,
     ['q3'], 'none',
     '**A name collision, not a match - check this before you revise it.** 695 is 2-D flood fill over a '
     'grid. Q3 "Artificial Island" is a 1-D sliding window with a conversion budget. They share only the '
     'word *island*. The real public equivalent of Q3 is **1004 Max Consecutive Ones III**, which is in '
     'the existing research as a reader-reported question.'),

    (706, 'Design HashMap', 'design-hashmap', 'Easy', False,
     ['q11', 'q12', 'q13'], 'pattern',
     'Building the structure that Q11, Q12 and Q13 all use. Worth one rep so that "I would use a '
     'dictionary" is backed by knowing what the dictionary costs.'),

    (1117, 'Building H2O', 'building-h2o', 'Medium', False,
     ['q7'], 'pattern',
     'Condition-variable signalling with nothing else in the way - the exact skill Q7 needs. In C# this '
     'is `SemaphoreSlim` or `Monitor.Wait`/`Pulse`; getting H2O right makes Q7’s wait loop obvious.'),

    (1188, 'Design Bounded Blocking Queue', 'design-bounded-blocking-queue', 'Medium', True,
     ['q7'], 'pattern',
     'The closest public problem to Q7 minus the delays. Same `lock` plus `Monitor.Wait`/`PulseAll` '
     'skeleton; Q7 adds a priority queue keyed on deadline and a **timed** wait, which is the part '
     'candidates get wrong.'),
]

REL_LABEL = {
    'exact':    ('hi',  'Exact match'),
    'variation': ('med', 'Variation'),
    'pattern':  ('',    'Similar pattern'),
    'followup': ('',    'Follow-up'),
    'none':     ('low', 'Unrelated to the 17'),
}

# Public equivalents that are NOT in the supplied list but are the real match for a question.
MISSING = [
    ('q3',  1004, 'Max Consecutive Ones III', 'max-consecutive-ones-iii', 'Medium', False,
     'The actual public twin of Artificial Island: longest window with at most k zeros. Already in the '
     'existing research as reader-reported. **1004, not 695.**'),
    ('q2',  886, 'Possible Bipartition', 'possible-bipartition', 'Medium', False,
     'Literally Q2 with people instead of animals: a dislike list, split into two groups. The closest '
     'public statement there is.'),
    ('q2',  785, 'Is Graph Bipartite?', 'is-graph-bipartite', 'Medium', False,
     'The same check given an adjacency list directly, so it skips the "build a symmetric graph from a '
     'one-way map" step that Q2 hides its difficulty in.'),
    ('q10', 366, 'Find Leaves of Binary Tree', 'find-leaves-of-binary-tree', 'Medium', True,
     'Exactly Q10. Reader-reported and already worked in the coding page.'),
    ('q14', 605, 'Can Place Flowers', 'can-place-flowers', 'Easy', False,
     'Exactly Q14, flowers instead of theatre seats, same greedy and the same boundary traps.'),
    ('q16', 671, 'Second Minimum Node In a Binary Tree', 'second-minimum-node-in-a-binary-tree', 'Easy', False,
     '**Exactly Q16’s tree** - LeetCode defines it as root.val = min(children), which is a '
     'tournament tree. Marked Easy only because LeetCode accepts an O(n) scan of every node; Q16 wants '
     'the O(h) walk down the winner’s path, which is the whole point.'),
    ('q9',  715, 'Range Module', 'range-module', 'Hard', False,
     'Q9 with removal as well, and the honest difficulty rating for maintaining merged intervals across '
     'calls. If Q9 goes well, this is the follow-up they reach for.'),
    ('q1',  146, 'LRU Cache', 'lru-cache', 'Medium', False,
     'The base Q1 extends. Reported in the existing research as an AI-round question, built with the '
     'assistant available.'),
    ('q12', 381, 'Insert Delete GetRandom O(1) - Duplicates allowed', 'insert-delete-getrandom-o1-duplicates-allowed', 'Hard', False,
     'Q12’s duplicates follow-up. Reader-reported and already worked in the coding page.'),
    ('q11', 208, 'Implement Trie (Prefix Tree)', 'implement-trie-prefix-tree', 'Medium', False,
     'The structure behind Q11’s prefix follow-up. Build it once by hand.'),
    ('q6',  20, 'Valid Parentheses', 'valid-parentheses', 'Easy', False,
     'Q6’s multi-bracket sibling. Tagged by LinkedIn in the six-month list; one 2025 report '
     'described a variant with integers and special characters, which is Q6.'),
]

def url(slug):
    return 'https://leetcode.com/problems/%s/' % slug
