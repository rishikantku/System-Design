# -*- coding: utf-8 -*-
"""Questions 10-17 of the InterviewDB LinkedIn set. Same shape as qbank_data.py."""

QUESTIONS = []

# ============================================================ Q10
QUESTIONS.append(dict(
    id='q10', n=10, name='Remove leaf levels',
    tags=['TREE', 'DFS', 'RECURSION'],
    diff='MEDIUM', prio='HIGH',
    verdict_short='InterviewDB + Find Leaves on your own list + 364 twice',
    prio_why=(
        '`366 Find Leaves of Binary Tree` is on your own list of past LinkedIn questions and is already '
        'worked in this workspace. `364 Nested List Weight Sum II` appears **twice** in the supplied '
        'number list and needs the identical bottom-up height idea. Two independent routes to the same '
        'insight, one of them first-party. High priority, and it is a fifteen-minute question once the '
        'insight lands.'),
    idb=(
        'Given an imbalanced binary tree:\n\n'
        'Print the leaf nodes.\n\n'
        'Remove those leaves.\n\n'
        'Print the new leaf nodes.\n\n'
        'Continue until only the root remains.\n\n'
        'Follow-up:\n\n'
        'Solve for an N-ary tree.'),
    dd=dict(elsewhere=[
        ('idb', 'The wording is procedural — print, remove, repeat — which is a hint about the '
                'expected *answer* rather than about the problem. Taking it literally leads to an O(n·h) '
                'solution; noticing that it describes a property leads to O(n).'),
        ('reported', '**Find Leaves of Binary Tree (LeetCode 366)** — on your own list, first-party, '
                     'and already worked in the coding page.'),
        ('reported', '**Nested List Weight Sum II (LeetCode 364)** — on the supplied list twice, and '
                     'independently reader-reported. Weighting by depth **from the bottom** is exactly '
                     'this problem’s recurrence in different clothing.'),
        ('lc', '366 is the exact match. 103 Binary Tree Zigzag is on the supplied list and is the '
               'instructive contrast — levels from the top, which BFS gives you and this problem '
               'cannot use.'),
    ],
        verdict='**InterviewDB reported and independently first-party reported.** High confidence, and '
                'the cheapest high-value question on the page after Q6.'),
    ambiguity=(
        'The statement says "continue until only the root remains", which implies the root is never '
        'removed — but a root with no children *is* a leaf, so the first round would print it.\n\n'
        'Both readings produce the same grouping; they differ only in whether the last round is emitted. '
        'I include the root as its own final level, because the sequence of levels is the natural output '
        'and stopping one short makes the single-node tree return nothing. Say which you chose.\n\n'
        'The second, larger question: **does the tree actually have to be mutated?** "Remove those '
        'leaves" sounds like it must. It does not, and that is the point of the question.'),
    understand=dict(
        what='Peel the tree like an onion. Take all the leaves, then all the nodes that became leaves, '
             'and so on, until nothing is left.',
        compute='A list of lists: the nodes removed in each round, in order. Round 0 is the original '
                'leaves.',
        constraints=[
            'The tree is explicitly **imbalanced**, so the number of rounds is the height, which can be '
            'n. That makes a per-round pass O(n²) in the worst case.',
            'Rounds are determined by the tree’s shape, not by the order you process nodes.',
            'Mutation is optional — and deciding that is the question.',
            'Recursion depth equals the height, which for a degenerate tree is n.',
        ],
        assume=[
            ['The root is emitted as its own final round.',
             'The alternative stops one round early. Same grouping; only the last line differs. A '
             'single-node tree is the test that distinguishes them.'],
            ['Order within a round does not matter.',
             'The recursion produces one particular order. If a specific order were required — '
             'left-to-right, say — the traversal order would have to be pinned, which the post-order '
             'walk happens to give anyway.'],
            ['Values are not unique.',
             'Nothing here depends on uniqueness. If nodes had to be identified rather than valued, the '
             'lists would hold nodes instead of ints.'],
            ['The caller does not need the tree afterwards.',
             'If it does, the non-mutating version is not merely faster, it is the only correct one. Ask '
             '— this is a cheap clarification with a real consequence.'],
        ]),
    examples=[
        ('Tree', '1 with children 2 and 3; 2 with children 4 and 5', ''),
        ('Round 0', 'the leaves', '[3, 4, 5]'),
        ('Round 1', '2 is now a leaf', '[2]'),
        ('Round 2', 'only the root is left', '[1]'),
        ('Mine', 'right-leaning chain 1 → 2 → 3', '[[3], [2], [1]] — one node per round, h = n'),
        ('Mine', 'a single node', '[[9]] — the root counts as a leaf'),
        ('N-ary', '1 with children 2 and 3; 2 with child 4', '[[3, 4], [2], [1]]'),
    ],
    examples_note='No example came with the statement; the tree above is the standard shape for this '
                  'problem and the rest are mine. The mutating and non-mutating implementations are '
                  'cross-checked against each other in the test suite, because "I refactored it to avoid '
                  'mutation and it still agrees" is the only claim worth making here.',
    observation=(
        'The statement describes a procedure, and the procedure is not the answer.\n\n'
        'Ask instead: **which round does a given node belong to?** A node leaves in round 0 if it is a '
        'leaf. Otherwise it cannot go until all its children have gone, so it leaves one round after its '
        'slowest child. That is\n\n'
        '`round(node) = 1 + max(round(left), round(right))`, with `round(null) = -1`\n\n'
        'and that expression is **exactly the height of the node measured from the bottom**. So the '
        'rounds are not something you perform — they are a property every node already has, and one '
        'post-order pass computes all of them. Bucket each node by its height as the recursion returns '
        'and you have the whole answer in O(n), with the tree untouched.\n\n'
        'The distinction that makes this click: **depth is passed down, height is returned up.** A BFS '
        'level counter gives you depth from the root, which is why `103 Binary Tree Zigzag` is BFS and '
        'this is not. Anything asking about the *last* level, peeling leaves, or weighting by distance '
        'from the bottom needs the post-order return value. That is also precisely why `364 Nested List '
        'Weight Sum II` is harder than `339`, its top-down sibling — same problem, same fix.\n\n'
        'So the answer to "remove those leaves" is: I do not have to. And saying that, rather than doing '
        'it, is the whole question.'),
    brute=dict(
        how='Follow the statement literally. Walk the tree collecting leaves, then walk it again cutting '
            'the links to them, and repeat until empty.',
        cx='O(n) per round × h rounds = **O(n · h)**, which on the imbalanced tree the '
            'statement specifies is O(n²). O(h) space.',
        why_not='It is correct, and on a balanced tree it is O(n log n), which is fine. The statement '
                'says *imbalanced*, and a degenerate chain of 10,000 nodes makes it 100 million '
                'operations for something achievable in 10,000. The deeper objection is that it destroys '
                'the input, and nothing in the problem requires that — the caller may well want the '
                'tree afterwards.'),
    optimal=dict(pipeline=[
        ('INPUT', 'The root of a binary tree'),
        ('TRANSFORMATION', 'Each node’s peel round is recognised as its height from the bottom'),
        ('DATA STRUCTURE', '`List<List<int>>`, indexed by height. No queue, no visited set, no mutation.'),
        ('ALGORITHM', 'One post-order recursion returning height; append each node to `levels[height]`'),
        ('OUTPUT', 'The list of rounds, and an untouched tree'),
    ],
        why=[
            ['`List<List<int>>` indexed by height',
             'Height values arrive in no particular order, but they are dense from 0 upwards, so a list '
             'indexed by height is the natural bucket. A dictionary would work and would need sorting at '
             'the end.'],
            ['Post-order, specifically',
             'A node’s height depends on its children, so the children must be resolved first. That '
             'is the definition of post-order — the traversal is not a choice here, it is forced by '
             'the recurrence.'],
            ['`return -1` for null',
             'So a leaf returns 0 and becomes round 0. Returning 0 for null would make every leaf round '
             '1 and every list index off by one.'],
            ['No mutation',
             'The tree is only read. That makes the function safe to call twice, safe to call on a shared '
             'tree, and trivially thread-safe for concurrent readers — none of which the literal '
             'reading gives you.'],
        ],
        steps=[
            '`Height(null)` returns -1.',
            'Recurse into both children first.',
            '`h = 1 + max(leftHeight, rightHeight)`.',
            'If `h == levels.Count`, this is the first node seen at that height — append a new list.',
            'Add the node’s value to `levels[h]`.',
            'Return `h`.',
        ]),
    walk=dict(
        intro='The example tree: root 1, children 2 and 3, and 2 has children 4 and 5. Post-order, so '
              'the deepest nodes resolve first.',
        headers=['Visit', 'Children heights', 'h', 'levels', 'Note'],
        rows=[
            ['4', '-1, -1', '0', '[[4]]', 'leaf → round 0; list created'],
            ['5', '-1, -1', '0', '[[4, 5]]', 'also round 0'],
            ['2', '0, 0', '1', '[[4, 5], [2]]', 'one round after its slowest child'],
            ['3', '-1, -1', '0', '[[4, 5, 3], [2]]', '**round 0, although it is shallower than 4 and 5**'],
            ['1', '1, 0', '2', '[[4, 5, 3], [2], [1]]', 'root → final round'],
        ],
        close='Node 3 is the case worth pointing at. It sits at depth 1 while nodes 4 and 5 sit at depth '
              '2, yet all three leave in round 0 — because round is height from the bottom, not '
              'depth from the top. Any solution driven by BFS levels gets this wrong, and it is the '
              'single fastest way to check whether someone has the right mental model.'),
    code=[
        ('Binary, non-mutating, plus the mutating version for comparison', 'Q10_Leaves.cs', 'LeafPeeling'),
        ('The N-ary follow-up — the recurrence does not change', 'Q10_Leaves.cs', 'NaryLeafPeeling'),
    ],
    codewalk=[
        ('`if (node == null) return -1;`',
         'The base case that makes the indices line up. A leaf has two null children, so '
         '`1 + max(-1, -1) = 0`, and round 0 is index 0. Return 0 for null and every level shifts by '
         'one — the classic off-by-one in this problem, and it produces an answer that is wrong in '
         'a way that looks structured.'),
        ('`if (h == levels.Count) levels.Add(new List<int>());`',
         'Heights arrive in whatever order the recursion reaches them, but a node of height h can only '
         'be reached after a node of height h-1 has been (its own child), so `levels.Count` is never '
         'more than one short. That is why a single `if` suffices rather than a while loop or a '
         'pre-sized list — and it is worth stating, because it looks like a bug that happens to '
         'work.'),
        ('Why `PeelLevels` takes the list as a parameter',
         'The recursion needs to write into shared state and return the height. Passing the accumulator '
         'down is the cheapest way; the alternative is returning a tuple of `(height, levels)` and '
         'merging, which allocates per node for no benefit.'),
        ('`PeelAndMutate` uses `ref TreeNode root`',
         'The last round removes the root itself, so the caller’s reference has to be nulled. '
         'Without `ref` the caller is left holding a node that the function believes it deleted — '
         'the kind of API detail that is invisible in a test and obvious in a code review.'),
        ('`Strip` returns the replacement node',
         'Returning `null` for a leaf is what lets the parent do `node.Left = Strip(node.Left, picked)` '
         'and cut the link without needing a parent pointer or a special case for "my child was a leaf". '
         'It is the standard shape for tree mutation in a functional style and it removes every null '
         'check.'),
        ('The N-ary version is the same function',
         '`h = -1; foreach (child) h = max(h, Height(child)); h += 1;` is `1 + max(children)` with an '
         'empty-children base case folded in. Nothing else changes — not the bucketing, not the '
         'base case, not the complexity. That is the answer to the follow-up, and the fact that it is '
         'this small is the point.'),
    ],
    cx=dict(rows=[
        ['`PeelLevels`', 'O(n)', 'O(n + h)', 'Each node visited once; output is n values, recursion is h '
                                            'deep'],
        ['`PeelAndMutate`', 'O(n · h)', 'O(h)', 'One full pass per round, h rounds'],
        ['`NaryLeafPeeling.PeelLevels`', 'O(n)', 'O(n + h)', 'Each node and each child link visited once'],
    ],
        note='**The O(h) recursion depth is the real risk here, not the time.** The statement says '
             '*imbalanced*, and a degenerate chain of 100,000 nodes will overflow the default 1 MB stack. '
             'The fix is an explicit stack, or a `Thread` created with a larger stack size. Worth '
             'raising — the question hands you the word "imbalanced" and it is the only reason it is '
             'there.'),
    edges=[
        ['Null root', 'Returns an empty list, no exception.'],
        ['Single node', 'Returns `[[value]]` — the root is its own round. This is the case that '
                        'distinguishes the two readings of "until only the root remains".'],
        ['A degenerate chain', 'h = n, so n rounds of one node each. Correct, and the stack-depth risk.'],
        ['A perfect tree', 'h = log n rounds, with half the nodes in round 0.'],
        ['Duplicate values', 'Fine; nothing is keyed on value.'],
        ['One-sided nodes', 'A node with only a left child has height `1 + max(hL, -1)` = `1 + hL`. The '
                            'null side contributes nothing, which is what the -1 base case buys.'],
        ['N-ary node with no children', 'The loop does not execute, `h` stays -1 and becomes 0 — a '
                                        'leaf. The base case works without a special case for empty '
                                        'children.'],
        ['100,000-node chain', 'Recursion overflows. Needs an iterative post-order walk or a bigger '
                               'stack.'],
    ],
    fups=[
        dict(given=True, q='Solve it for an N-ary tree.',
             thinking='The instinct is that fan-out changes something. It does not — the recurrence '
                      'is "one more than my slowest child", and the number of children is irrelevant to '
                      'that.',
             approach='`h = 1 + max over all children`, with -1 when there are none. The bucketing, the '
                      'base case and the complexity are all unchanged.',
             tradeoff='None. The whole point is that the generalisation is free, and it is free because '
                      'the original solution was written against the recurrence rather than against the '
                      'binary shape. If the original had been the literal remove-and-repeat version, this '
                      'follow-up would have needed the removal logic rewritten for a child list.',
             code=[('N-ary', 'Q10_Leaves.cs', 'NaryLeafPeeling')],
             t='O(n)', s='O(n + h)'),
        dict(given=True, q='Does the tree actually have to be mutated?',
             thinking='This is the question behind the question, and it should be raised before writing '
                      'anything rather than waiting to be asked.',
             approach='No. The rounds are a property of the shape, so one read-only pass computes them. '
                      'If the caller genuinely wants the tree destroyed, `PeelAndMutate` does it '
                      'explicitly — but as a separate, clearly-named operation, not as a side effect '
                      'of a query.',
             tradeoff='O(n) versus O(n·h), and a preserved input versus a destroyed one. There is no '
                      'case where the mutating version is better *for computing the answer*; it is only '
                      'better if destruction is itself the goal. Separating the two is the design point.',
             code=[('The mutating version, as a separate operation', 'Q10_Leaves.cs',
                    'LeafPeeling|public static List<List<int>> PeelAndMutate')],
             t='O(n) non-mutating; O(n·h) mutating', s='O(n + h) / O(h)'),
        dict(q='The tree has 100,000 nodes in a chain. Your recursion overflows.',
             thinking='The statement said imbalanced, so this is not hypothetical. The recurrence is fine; '
                      'the implementation of it is not.',
             approach='Convert to an iterative post-order traversal with an explicit `Stack`, carrying '
                      'computed heights in a `Dictionary<TreeNode, int>` or by pushing each node twice '
                      'with a visited marker. Alternatively, run the recursion on a `Thread` constructed '
                      'with a larger stack — which is a legitimate and much shorter answer in C#, and '
                      'worth offering as the pragmatic option.',
             tradeoff='The explicit stack is robust and roughly doubles the code, and it moves the memory '
                      'from the stack to the heap where it is bounded by available memory rather than by '
                      'a 1 MB default. The bigger-thread trick is three lines and only moves the cliff. '
                      'For a library I would write the iterative version; for a one-off I would raise the '
                      'stack and document why.',
             t='O(n)', s='O(n) heap instead of O(n) stack'),
        dict(q='Return the nodes, not the values. And what if you need the parent of each?',
             thinking='A small change that reveals whether the traversal was written for the answer or '
                      'for the output format.',
             approach='Bucket `TreeNode` references instead of ints — a type change and nothing '
                      'else. For parents, pass the parent down as a second argument; it costs one '
                      'parameter and no extra pass, because the recursion already visits every node with '
                      'its parent on the stack.',
             tradeoff='Holding node references keeps the whole tree alive from the result, which matters '
                      'if the caller expected the values to be a lightweight snapshot. Worth a sentence '
                      'about lifetime, not more.',
             t='O(n)', s='O(n)'),
        dict(q='Why is this not just BFS with levels?',
             thinking='Being able to answer this precisely is the clearest evidence of understanding, and '
                      'it is worth volunteering.',
             approach='BFS gives **depth from the root**; this needs **height from the leaves**. In the '
                      'worked example, node 3 is at depth 1 and nodes 4 and 5 at depth 2, yet all three '
                      'leave in round 0. No function of depth produces that grouping, because two nodes '
                      'at different depths can share a round and two nodes at the same depth can be in '
                      'different ones.',
             tradeoff='It is not a trade, it is a correctness distinction. `103 Binary Tree Zigzag` is on '
                      'the supplied list and is the BFS version of a level question; doing the two back '
                      'to back is the fastest way to internalise which is which.',
             t='—', s='—'),
    ],
    testing=dict(skills=[
        '**Not implementing the statement literally** — recognising that a procedural description '
        'describes a property.',
        '**Bottom-up versus top-down recursion** — height returned up, depth passed down. The core '
        'skill, and the link to 364.',
        '**Base-case discipline** — -1 for null, and why.',
        '**Knowing when not to mutate**, and raising it as a question rather than assuming.',
        '**Stack-depth awareness** — the word "imbalanced" is in the statement for a reason.',
    ],
        senior='Writes the post-order height solution, buckets by height, gets the -1 base case right, '
               'and generalises to N-ary in two lines.',
        staff='Does that, and: says up front that the tree does not need mutating and asks whether the '
              'caller needs it afterwards; explains why BFS cannot produce this grouping, with node 3 as '
              'the counterexample; notices that "imbalanced" implies a stack-depth risk and offers the '
              'iterative version; and connects it to 364, which is on the supplied list twice. The '
              '"I do not need to mutate it" observation, made before being asked, is the signal.'),
    say=[
        "Let me ask about the round the statement describes rather than perform it. Which round does a "
        "given node leave in?",
        "A leaf leaves in round 0. Any other node cannot leave until all its children have, so it leaves "
        "one round after its slowest child. That is one plus the max over children — which is just the "
        "node's height measured from the bottom.",
        "So the rounds are not something I do, they are something every node already has. One post-order "
        "pass computes every height, I bucket nodes by height, and I am done in O(n) with the tree "
        "untouched.",
        "Which raises the question — do you want the tree mutated? I do not need to, and if the caller "
        "wants it afterwards then not mutating is the only correct answer. If you do want it destroyed I "
        "would do that as a separate, explicitly named operation rather than as a side effect of this one.",
        "Base case is minus one for null, so a leaf comes out as zero and the list indices line up.",
        "Worth saying why this is not BFS. BFS gives me depth from the root, and I need height from the "
        "leaves. In this tree node 3 is at depth 1 while 4 and 5 are at depth 2, and all three leave in "
        "round 0. No function of depth gives me that grouping.",
        "For N-ary the recurrence does not change at all — one plus the max over the children, however "
        "many there are. Same bucketing, same base case, same complexity.",
        "One thing I would flag: you said imbalanced, so the height can be n. That means my recursion is n "
        "deep, and at a hundred thousand nodes it overflows the default stack. I would either write it "
        "iteratively with an explicit stack or run it on a thread with a bigger one.",
    ],
    video=dict(title='LinkedIn Coding — Peeling the Leaves (Height from the Bottom)', mins=14,
               objective='Show that a procedural statement is describing a property, and make the '
                         'height-versus-depth distinction concrete enough that 364 becomes easy.',
               beats=[('0:00', 'The question as stated'),
                      ('1:20', 'The literal reading, and what it costs'),
                      ('2:50', 'Asking a different question: which round does a node leave in?'),
                      ('4:20', 'The recurrence, and that it is just height'),
                      ('5:40', 'Depth goes down, height comes up'),
                      ('7:00', 'Why BFS cannot do this — node 3'),
                      ('8:20', 'The C# implementation, and the -1 base case'),
                      ('10:00', 'Walking the tree post-order'),
                      ('11:10', 'N-ary for free'),
                      ('12:10', 'Imbalanced means a stack-depth problem'),
                      ('13:10', 'How to say it')]),
))

# ============================================================ Q11
QUESTIONS.append(dict(
    id='q11', n=11, name='Phone keypad words',
    tags=['STRING', 'HASHING', 'TRIE', 'DESIGN'],
    diff='MEDIUM', prio='MEDIUM',
    verdict_short='InterviewDB; the inverse of 17, which is reader-reported',
    prio_why=(
        '`17 Letter Combinations of a Phone Number` is on your own list, but **this is its inverse** and '
        'the inverse has a completely different answer — so the reported question does not prepare '
        'you for this one. `244 Shortest Word Distance II` and `205 Isomorphic Strings`, both on the '
        'supplied list, train the two ideas this needs. Medium: the framing is single-source, and the '
        'insight is a thirty-second realisation once you see it.'),
    idb=(
        'Given:\n\n'
        'KNOWN_WORDS =\n'
        '[\n'
        '"careers",\n'
        '"linkedin",\n'
        '"hiring",\n'
        '"interview",\n'
        '"linkedgo"\n'
        ']\n\n'
        'Given a phone number, return all known words matching the phone keypad mapping.\n\n'
        'Examples:\n\n'
        '2273377 → ["careers"]\n\n'
        '54653346 → ["linkedin", "linkedgo"]'),
    dd=dict(elsewhere=[
        ('idb', 'Supplied with a dictionary and two examples, and **the second example is the whole '
                'point**: two different words produce the same number, so the answer is a list rather '
                'than a word. I verified both examples digit by digit against the standard keypad; both '
                'check out.'),
        ('reported', '`17 Letter Combinations of a Phone Number` is on your own list. **It is the '
                     'opposite direction** — generate every possible letter string — which is '
                     'exponential and is the wrong instinct here.'),
        ('reported', '`244 Shortest Word Distance II` is reader-reported and is the same design lesson: '
                     'preprocess once, answer many queries in O(1).'),
        ('lc', '208 Implement Trie is the structure for the prefix follow-up. 205 Isomorphic Strings, on '
               'the supplied list, is the same canonical-mapping idea.'),
    ],
        verdict='**InterviewDB reported. The inverse problem is independently reader-reported**, which is '
                'suggestive but is not evidence for this framing. Prepare both directions — they '
                'share nothing but the keypad.'),
    understand=dict(
        what='A keypad maps letters onto digits, many to one. Given a number, find which of a known set '
             'of words someone could have been typing.',
        compute='Every word in the dictionary whose digit signature equals the input. A list, because the '
                'mapping is many-to-one — `linkedin` and `linkedgo` are indistinguishable on a '
                'keypad.',
        constraints=[
            'The dictionary is known **up front**, which is the constraint the whole design turns on.',
            'Word length equals number length in the base problem — an exact match, not a prefix.',
            'Many words collapse onto one signature, so the return type is plural.',
            'Queries are expected to outnumber dictionary changes by a wide margin. That ratio is the '
            'argument for preprocessing.',
        ],
        assume=[
            ['Letters only, case-insensitive, mapped a–z.',
             'A word with an apostrophe or a hyphen has no keypad representation. I skip such words at '
             'build time rather than throwing, so one odd dictionary entry cannot break the service.'],
            ['Digits 2–9 only; 0 and 1 carry no letters.',
             'A number containing 0 or 1 can never match a word, so it returns empty. Worth saying, '
             'because it is a free early exit.'],
            ['Exact-length match in the base problem.',
             'The prefix version — which is what a phone actually does while you type — needs a '
             'trie, not a hash map. That is the follow-up.'],
            ['The dictionary is large and the query rate is high.',
             'The justification for O(N·L) preprocessing. If the dictionary changed on every query, '
             'the preprocessing would be waste and a scan would be better — state the ratio you are '
             'assuming.'],
        ]),
    examples=[
        ('Given', '2273377', '["careers"]'),
        ('Given', '54653346', '["linkedin", "linkedgo"]'),
        ('Check', 'c-a-r-e-e-r-s', '2-2-7-3-3-7-7 ✓'),
        ('Check', 'l-i-n-k-e-d-i-n', '5-4-6-5-3-3-4-6 ✓'),
        ('Check', 'l-i-n-k-e-d-g-o', '5-4-6-5-3-3-4-6 ✓ — g=4 like i, o=6 like n, so the last two digits collide'),
        ('Mine', '9999999', '[] — no word matches'),
        ('Mine', '227337', '[] — a prefix is not a match in the base problem'),
        ('Mine', 'prefix 5465 with the trie', '2 words — the follow-up'),
    ],
    examples_note='The two supplied examples are verified digit by digit in the test suite, along with '
                  '`hiring` → 447464 and `interview` → 468378439. The `linkedin`/`linkedgo` '
                  'collision is the load-bearing one: positions 7 and 8 are `i,n` versus `g,o`, and '
                  'i→4, n→6, g→4, o→6 — so both end `4,6` and the signatures are '
                  'identical.',
    observation=(
        'The reflex, especially if you have seen LeetCode 17, is to generate every letter string the '
        'number could spell and test each against the dictionary. `54653346` has 3×3×3×3'
        '×3×3×3×3 ≈ 6,500 candidates for eight digits, and a longer number is '
        'far worse. **That is the wrong direction**, and noticing that is the insight.\n\n'
        'Go the other way. The letter → digit mapping is a **function**: every word has exactly one '
        'digit signature, and computing it is O(L). The number **is** a signature. So precompute the '
        'signature of every dictionary word, index the words by it, and a query becomes a single hash '
        'lookup.\n\n'
        'Two things make this the right answer and both are worth saying. The direction with the '
        'many-to-one mapping is the cheap direction — you compute the canonical form rather than '
        'enumerating its preimages. And the work depends only on the **dictionary**, not on the query, so '
        'it happens once.\n\n'
        'That is the same move as Q8’s wildcard index and the same as `244 Shortest Word Distance '
        'II`: *find a canonical key under which the expensive comparison becomes a hash lookup.* Three '
        'questions on this page use it, which is why it is worth naming as a pattern.\n\n'
        'The hash map is exact-match only. A real phone shows candidates **while you type**, which is a '
        'prefix query, and a hash map cannot do prefixes at all. That is what the trie is for — and '
        'it is worth introducing it as the answer to a requirement rather than as the fancier structure.'),
    brute=dict(
        how='Two options, both bad in different ways. **Generate**: enumerate every letter combination of '
            'the number and check each against the dictionary. **Scan**: for each query, compute every '
            'dictionary word’s signature and compare.',
        cx='Generate is O(4^L) — up to 4 letters per digit. Scan is O(N · L) **per query**.',
        why_not='Generating is exponential and is the trap the LeetCode-17 instinct leads you into: it '
                'enumerates up to 65,000 strings for a nine-digit number to find at most a handful of '
                'real words. Scanning is merely wasteful, and the waste has a name — it recomputes '
                'per query something that is a property of the dictionary. Both are worth stating, '
                'because the *reason* each is wrong is different, and the second reason is the one that '
                'leads to the answer.'),
    optimal=dict(pipeline=[
        ('INPUT', 'A known word list at construction; a digit string per query'),
        ('TRANSFORMATION', 'Each word → its digit signature, via a 26-entry lookup table'),
        ('DATA STRUCTURE', '`Dictionary<string, List<string>>` from signature to the words sharing it'),
        ('ALGORITHM', 'Build once; a query is one hash lookup'),
        ('OUTPUT', 'Every known word matching the number'),
    ],
        why=[
            ['`Dictionary<string, List<string>>`, value a **list**',
             'Because the mapping is many-to-one — the supplied example proves it. A '
             '`Dictionary<string, string>` would silently keep only the last word per signature and pass '
             'the first example.'],
            ['A 26-entry `int[]` for letter → digit',
             'Built once, statically. Array indexing beats a dictionary lookup or a chain of range '
             'comparisons, and it makes `Signature` a tight loop.'],
            ['`StringComparer.Ordinal`',
             'Signatures are digit strings, so culture-aware comparison is meaningless overhead — '
             'and in the general case it can treat distinct strings as equal, which would merge buckets.'],
            ['`Signature` returns null for an untypable word',
             'Rather than throwing. One word with an apostrophe should not fail the whole build. Skipping '
             'is the total, defensive choice.'],
            ['A trie **only** for the prefix follow-up',
             'The hash map is strictly better for exact match: O(L) versus O(L) but with no per-character '
             'node hop and far less memory. The trie earns its place when prefixes are required, and not '
             'before.'],
        ],
        steps=[
            'Build the 26-entry digit table from the eight keypad groups.',
            'For each known word, compute its signature; skip it if untypable.',
            'Append the word to `_bySignature[signature]`.',
            'Query: look up the number. Return a copy of the bucket, or an empty list.',
        ]),
    walk=dict(
        intro='Building the index from the five supplied words, then answering both supplied queries.',
        headers=['Word', 'Signature', 'Bucket after insert', ''],
        rows=[
            ['careers', '2273377', '{2273377: [careers]}', 'c=2 a=2 r=7 e=3 e=3 r=7 s=7'],
            ['linkedin', '54653346', '… {54653346: [linkedin]}', 'l=5 i=4 n=6 k=5 e=3 d=3 i=4 n=6'],
            ['hiring', '447464', '… {447464: [hiring]}', 'h=4 i=4 r=7 i=4 n=6 g=4'],
            ['interview', '468378439', '… {468378439: [interview]}', ''],
            ['linkedgo', '54653346', '{54653346: [linkedin, **linkedgo**]}', 'g=4 o=6 — same last two digits as i,n'],
            ['query 2273377', '', '→ [careers]', 'one hash lookup'],
            ['query 54653346', '', '→ [linkedin, linkedgo]', '**the bucket already holds both**'],
        ],
        close='The collision was created at build time, not discovered at query time — which is why '
              'the query is a single lookup regardless of how many words collide. Note also that '
              '`linkedgo` is not a word; the dictionary is arbitrary, and nothing in the design cares.'),
    code=[
        ('The exact-match index', 'Q11_Keypad.cs', 'KeypadDictionary'),
        ('The trie, for the prefix follow-up', 'Q11_Keypad.cs', 'KeypadTrie'),
    ],
    codewalk=[
        ('`BuildDigitTable` runs once, statically',
         'A `static readonly int[] DigitOf` initialised from the eight group strings. Writing the 26 '
         'entries by hand would be a transcription error waiting to happen; deriving them from `"abc"`, '
         '`"def"`, … makes the keypad layout the single source of truth and is self-documenting.'),
        ('Why the bucket value is a `List<string>`',
         'The supplied example requires it. A `Dictionary<string, string>` would pass the first example, '
         'fail the second, and the failure would look like a data problem rather than a design one.'),
        ('`Signature` returns null rather than throwing',
         'A dictionary of real words will eventually contain `o’brien` or `well-known`. Returning '
         'null and skipping means one unusual entry does not take the build down. The caller-visible '
         'behaviour is "that word can never be matched", which is exactly true.'),
        ('`new List<string>(hits)` on the way out',
         'Returning the internal list would let a caller mutate the index. One copy per query is cheap '
         'and the bucket is tiny; handing out internal state is the kind of thing that causes a bug six '
         'months later in an unrelated file.'),
        ('The trie is indexed by **digit**, not by letter',
         '`Node.Next` is a 10-element array indexed `0..9`, so walking the trie consumes the query '
         'directly with no translation. Indexing by letter would need the query converted to letters '
         'first, which is the exponential direction again — the structure choice quietly encodes '
         'the insight.'),
        ('`cur.Next[i] ??= new Node();`',
         'Null-coalescing assignment: create the child if absent, then use it. Three lines in one, and '
         'it is the idiomatic C# for trie insertion.'),
        ('`Words` is a list on the node, and is lazily allocated',
         '`(cur.Words ??= new List<string>()).Add(word)` — most trie nodes are internal and hold no '
         'words, so allocating a list per node would multiply the memory for nothing. On a large '
         'dictionary that is the difference between a trie that fits and one that does not.'),
        ('`WithPrefix` collects the whole subtree',
         '`Collect` walks every descendant. That is O(matches + nodes below), which is the honest cost: '
         'a one-digit prefix on a large dictionary returns almost everything. A real autocomplete caps '
         'the result count, and the cap has to be applied **during** the walk to be worth anything.'),
    ],
    cx=dict(rows=[
        ['build', 'O(N · L)', 'O(N · L)', 'One signature per word, each O(L)'],
        ['`WordsFor` (exact)', 'O(L + m)', 'O(m)', 'One hash of an L-digit string, plus copying m matches'],
        ['`Signature`', 'O(L)', 'O(L)', 'One table lookup per character'],
        ['trie `Add`', 'O(L)', 'O(L) nodes worst case', 'One node per digit, shared with existing words'],
        ['trie `Exact`', 'O(L)', 'O(m)', 'L node hops'],
        ['trie `WithPrefix`', 'O(L + nodes in the subtree)', 'O(m)', 'The subtree walk is the cost'],
    ],
        note='**The hash map and the trie are both O(L) for exact match, and the hash map is still the '
             'right choice.** One hash computation beats L pointer dereferences for cache reasons, and '
             'the trie costs far more memory. The trie wins exactly one thing — prefix queries — '
             'and that is the entire argument for it. Reaching for the trie on the exact-match problem '
             'because it is the more sophisticated structure is the mistake this question is set up to '
             'catch.'),
    edges=[
        ['Empty number', 'Returns empty, checked first.'],
        ['Number containing 0 or 1', 'No word can match; returns empty. A free early exit.'],
        ['Number shorter than every word', 'Empty in the base problem — a prefix is not a match.'],
        ['No matching word', 'Empty list, not null. A caller should never have to null-check a collection '
                             'return.'],
        ['Several words, one signature', 'All returned. The supplied second example.'],
        ['Untypable word in the dictionary', 'Skipped at build time, never matched.'],
        ['Mixed-case dictionary', 'Lower-cased in `Signature`, so `LinkedIn` and `linkedin` share a '
                                  'signature.'],
        ['Duplicate word in the dictionary', 'Appears twice in its bucket. De-duplicate at build time if '
                                             'that is wrong — state the choice.'],
        ['Very large dictionary', 'Build is O(N·L) and memory is the signature strings plus the word '
                                  'references. The trie would be considerably larger.'],
    ],
    fups=[
        dict(q='Return matches while the user is still typing.',
             thinking='This is what a phone actually does, and it is the requirement the hash map cannot '
                      'meet — not slowly, but at all. A hash map has no notion of a partial key.',
             approach='A trie keyed on digits. Each node is a digit; words hang off the node where they '
                      'end. Walk the prefix in O(L), then collect the subtree. In production, cap the '
                      'results during the walk and order the node’s words by frequency so the cap '
                      'keeps the best ones.',
             tradeoff='Prefix capability for memory and cache locality. The trie is much larger than the '
                      'hash map and each step is a pointer chase. It is also the structure that makes '
                      '"show me something useful after three digits" possible at all, so when the '
                      'requirement is there it is not really a trade.',
             code=[('The digit trie', 'Q11_Keypad.cs', 'KeypadTrie')],
             t='O(L) to walk, plus O(matches) to collect', s='O(total digits across all words)'),
        dict(q='The dictionary is 500,000 words and must be memory-efficient.',
             thinking='Both structures grow with the dictionary, but they grow in different things — '
                      'worth separating before optimising.',
             approach='For the hash map, the waste is the signature **strings**: one allocation per '
                      'distinct signature. For words up to 9 digits a signature fits in a `long` (9 '
                      'digits × 4 bits, or just base-8 since digits are 2–9), so the key '
                      'becomes a value type and the string allocations disappear along with their hashing '
                      'cost. For the trie, the fix is a compressed form — a radix tree merging '
                      'single-child chains, or a double-array trie — which cuts node count '
                      'substantially.',
             tradeoff='The `long` key is a large, cheap win and caps word length at 9 digits, which has '
                      'to be checked rather than assumed. A radix tree is a real reduction and much more '
                      'code. I would do the `long` key first and measure before touching the trie.',
             t='unchanged', s='materially lower with a long key'),
        dict(q='The dictionary changes at runtime.',
             thinking='Additions are trivial, removals are the interesting half, and the difference is '
                      'worth stating.',
             approach='Adding a word is one signature and one list append, O(L). Removing needs the word '
                      'pulled from its bucket, which is a linear scan of that bucket — fine, since '
                      'buckets are tiny, but worth naming. In the trie, removal means unlinking from the '
                      'terminal node and optionally pruning now-empty nodes upward.',
             tradeoff='For a mostly-static dictionary with occasional additions, do nothing clever. If '
                      'updates were frequent I would rebuild into a new index and swap the reference '
                      'atomically, so readers never see a half-built structure — which is cheaper to '
                      'reason about than making the index itself thread-safe.',
             t='O(L) add; O(L + bucket) remove', s='unchanged'),
        dict(q='Also match words that are longer than the number, or allow one typo.',
             thinking='The first is the prefix query again. The second changes the problem — it is no '
                      'longer an exact lookup and hashing stops applying.',
             approach='One typo means "signatures within edit distance 1", which cannot be hashed for '
                      'directly. The wildcard-index trick from Q8 applies: index each signature under '
                      'every single-digit blanking, so `2273377` also goes under `*273377`, `2*73377` and '
                      'so on. A query then does L lookups. For general edit distance, the trie plus a '
                      'bounded DFS with an edit budget is the standard answer.',
             tradeoff='The wildcard index multiplies memory by L and handles exactly one substitution. '
                      'The trie walk with a budget handles any distance and costs a search rather than a '
                      'lookup. Both are big steps up from exact match, so I would want to know how many '
                      'typos actually need handling before choosing — "one substitution" and "any '
                      'edit" are very different bills.',
             t='O(L) lookups for one substitution; O(trie nodes visited) for general distance',
             s='O(N · L) for the wildcard index'),
    ],
    testing=dict(skills=[
        '**Direction of computation** — recognising that the many-to-one direction is the cheap one, '
        'and resisting the LeetCode-17 instinct.',
        '**Preprocess versus per-query** — identifying what depends on the dictionary and what '
        'depends on the query.',
        '**Return-type reasoning** — the supplied example forces a list, and a candidate who returns '
        'a single word has not read it.',
        '**Structure choice on requirements** — hash map for exact, trie for prefix, and being able '
        'to say the hash map is *better* for the stated problem.',
        '**Defensive building** — one odd dictionary entry should not break the service.',
    ],
        senior='Computes signatures, indexes by signature, returns a list, and reaches for a trie when '
               'prefixes come up.',
        staff='Does that, and: explicitly rejects the generate-and-test direction with its cost; states '
              'that the work depends on the dictionary rather than the query, and that this is the same '
              'pattern as 244; says the hash map **beats** the trie for exact match rather than treating '
              'the trie as the better answer; notices the many-to-one mapping from the supplied example '
              'before writing the return type; and on the large-dictionary follow-up, proposes packing '
              'the signature into a `long` with the length caveat stated. The "the trie is worse here, '
              'and here is when it becomes better" point is the discriminating one.'),
    say=[
        "The instinct — especially if you know Letter Combinations of a Phone Number — is to generate every "
        "letter string this number could spell and check each against the dictionary. That is exponential: "
        "about six and a half thousand candidates for these eight digits.",
        "But the mapping only goes one way cheaply. Every word has exactly one digit signature, and "
        "computing it is linear in the word. So I go in that direction instead: precompute the signature of "
        "every known word and index the words by it. A query is then one hash lookup.",
        "The other thing that matters is what the work depends on. Signatures depend only on the "
        "dictionary, not on the query, so they get computed once at startup rather than per request.",
        "From your second example — linkedin and linkedgo both come out as 54653346, because i and g are "
        "both on the four and n and o are both on the six. So the value in my index has to be a list of "
        "words, not a word. That is the detail I would get wrong if I skimmed the examples.",
        "Build is O(N times L), and every query is O(L) to hash plus the number of matches.",
        "If you want matches while the user is still typing, that is a prefix query, and a hash map cannot "
        "do prefixes at all — not slowly, at all. That is what a trie is for, and I would key it on digits "
        "rather than letters so the query walks it directly.",
        "But for the exact-match problem you asked, the hash map is genuinely better than the trie — one "
        "hash beats L pointer hops, and it uses far less memory. I would not reach for the trie until the "
        "requirement asks for prefixes.",
        "At half a million words I would pack the signature into a long instead of a string, since digits "
        "are two to nine and nine of them fit. That removes an allocation and a string hash per entry — "
        "though it does cap word length at nine, which I would want to check.",
    ],
    video=dict(title='LinkedIn Coding — Phone Keypad Words', mins=13,
               objective='Show that the direction of the mapping decides the algorithm, and that the '
                         'sophisticated structure is the wrong one until the requirement changes.',
               beats=[('0:00', 'The question and the two examples'),
                      ('1:20', 'The collision hiding in the second example'),
                      ('2:40', 'The LeetCode 17 instinct, and why it is exponential'),
                      ('4:00', 'Going the other way: words have one signature'),
                      ('5:30', 'Preprocess once — what depends on the dictionary'),
                      ('6:50', 'The C# index, and why the value is a list'),
                      ('8:20', 'Building the index from the five words'),
                      ('9:30', 'Prefix matching: what a hash map cannot do'),
                      ('10:50', 'Why the trie is worse until it is better'),
                      ('12:00', 'How to say it')]),
))

# ============================================================ Q12
QUESTIONS.append(dict(
    id='q12', n=12, name='Random data structure',
    tags=['DESIGN', 'DATA STRUCTURE DESIGN', 'ARRAY', 'HASHING', 'RANDOMIZATION'],
    diff='MEDIUM', prio='HIGH',
    verdict_short='InterviewDB + 380/381 on your own list',
    prio_why=(
        '`380 Insert Delete GetRandom O(1)` and `381`, its duplicates-allowed version, are **both on your '
        'own list** of past LinkedIn questions, and 380 is on the supplied number list as well. Already '
        'worked in the coding page. High priority for the same reason as Q6 — short, '
        'well-attested, and there is no excuse for a wobble on it.'),
    idb=(
        'Implement:\n\n'
        'insert(val) → expected O(1)\n\n'
        'remove(val) → expected O(1)\n\n'
        'removeRandomElement() → expected O(1)'),
    dd=dict(elsewhere=[
        ('idb', 'Note the word **expected** in all three requirements. That is doing real work: it '
                'concedes that the structure is hash-based and therefore has no worst-case guarantee, '
                'which is exactly the distinction to make out loud.'),
        ('reported', '**Insert Delete GetRandom O(1), duplicates allowed (LeetCode 381)** — on your '
                     'own list, first-party, and already worked in the coding page.'),
        ('lc', '380 is the standard version and is on the supplied list. **The difference here is '
               '`removeRandomElement` instead of `getRandom`**, which needs no new idea — it is '
               '`Remove(PeekRandom())`.'),
    ],
        verdict='**InterviewDB reported and independently first-party reported.** High confidence. The '
                'variation — remove-random rather than get-random — is trivial once the base '
                'structure is right.'),
    ambiguity=(
        'Are duplicates allowed? The statement says `insert(val)` with no return type and does not say.\n\n'
        'I take **no duplicates** in the base design, because that is LeetCode 380 and it is the simpler '
        'structure, and then give the duplicates version as a follow-up. The distinction matters more than '
        'it looks: with duplicates, `remove(val)` has to choose *which* copy to remove, the value-to-index '
        'map becomes a value-to-**set**-of-indices map, and uniform random selection becomes uniform over '
        'occurrences rather than over distinct values. Ask.\n\n'
        'Second: what should `removeRandomElement` do on an empty structure? Throwing is the honest answer '
        'for a method that must return a value; returning a sentinel means a caller cannot distinguish '
        '"empty" from "the element was the sentinel".'),
    understand=dict(
        what='A bag you can add to, delete a specific item from, and pull a random item out of — all '
             'in constant time.',
        compute='Not a value so much as a set of guarantees. The interesting one is uniform randomness '
                'together with O(1) deletion, because the obvious structures give you one or the other.',
        constraints=[
            'All three operations O(1) **expected**, which the statement is careful to say.',
            'The random choice must be uniform over the current contents.',
            'A specific value must be deletable, not just an arbitrary one.',
        ],
        assume=[
            ['No duplicates in the base version.',
             'With duplicates the index map becomes a map to a **set** of positions, and "remove this '
             'value" needs a policy for which copy. Both are implemented here; the base one is 380.'],
            ['`insert` returns whether it changed the structure.',
             'LeetCode 380 does this and it is genuinely useful — the caller can tell an insert from '
             'a no-op without a second lookup.'],
            ['`removeRandomElement` throws when empty.',
             'A sentinel return conflates "nothing here" with "the element was the sentinel". If the '
             'signature must not throw, it should return `bool TryRemoveRandom(out int)`.'],
            ['`Random` is seedable.',
             'Otherwise the uniformity cannot be tested. The test suite runs 40,000 trials and a '
             'chi-square check, which needs determinism per trial.'],
        ]),
    examples=[
        ('Sequence', 'Insert(5)', 'true'),
        ('', 'Insert(5) again', 'false — already present'),
        ('', 'Insert(6); Insert(7); Remove(6)', 'true; count is 2'),
        ('', 'Remove(6) again', 'false'),
        ('Critical', 'Insert(1); Insert(2); Remove(2)', 'removing the **last** slot — the case that breaks a careless swap'),
        ('Drain', '500 values inserted, then drained by RemoveRandom', 'every value comes out exactly once'),
        ('Uniformity', '40,000 trials of "insert 0–9, remove one at random"', 'chi-square 9 dof, passes'),
    ],
    examples_note='The "Critical" row is the one to write a test for before anything else: when the slot '
                  'being removed *is* the last slot, the swap-with-last becomes a self-assignment and the '
                  'index bookkeeping has to still be right. The uniformity check is a chi-square test '
                  'over 40,000 seeded trials, because "it looks random" is not a claim worth making.',
    observation=(
        'Take the three requirements one at a time and notice that each rules out the structure that '
        'serves the others.\n\n'
        '**A dictionary** gives O(1) insert and O(1) delete by value. It cannot give you a uniform random '
        'element — there is no way to pick the i-th entry of a hash table in constant time, and '
        'iterating to the i-th is O(n).\n\n'
        '**An array** gives O(1) random selection, because a uniform index is one call to the random '
        'generator. But deleting a specific value means finding it, O(n), and then closing the hole, also '
        'O(n).\n\n'
        'So hold both: **the array holds the values, and the dictionary maps each value to its index in '
        'the array.** Random selection uses the array. Finding a value uses the dictionary.\n\n'
        'That leaves the one real problem: deleting from the middle of an array without shifting. And the '
        'insight is that **nothing requires the array to be ordered.** Its only job is to be a gap-free '
        'list of the current contents, so that a uniform index is a uniform element. So instead of '
        'shifting, **move the last element into the hole** and shorten the array by one. O(1), and the '
        'array is still gap-free.\n\n'
        'The gap-free property is the load-bearing one and is worth naming explicitly: it is what makes '
        '`_rng.Next(_items.Count)` uniform. Tombstones or a free-list would break it, because a random '
        'index could land on a hole.\n\n'
        'Then `removeRandomElement` is just the composition: pick a uniform index, read the value, and '
        'run the same removal. No new machinery at all.'),
    brute=dict(
        how='A `List<int>` alone. Insert appends. Remove scans for the value and calls `RemoveAt`. Random '
            'picks an index.',
        cx='Insert O(1), remove O(n) — O(n) to find plus O(n) to shift — random O(1). Space O(n).',
        why_not='Only `remove` is wrong, and it is wrong twice, for two independent reasons: finding the '
                'value is linear, and closing the hole is linear. The dictionary fixes the first and the '
                'swap-with-last fixes the second, and separating them is the cleanest way to explain the '
                'design — each structure exists to kill one of the two linear costs.'),
    optimal=dict(pipeline=[
        ('INPUT', '`Insert(val)`, `Remove(val)`, `RemoveRandomElement()`'),
        ('TRANSFORMATION', 'Values live in an unordered, gap-free array; the dictionary remembers where '
                           'each one is'),
        ('DATA STRUCTURE', '`List<int> _items` and `Dictionary<int, int> _indexOf`'),
        ('ALGORITHM', 'Insert appends and records the index. Remove looks up the index, overwrites it with '
                      'the last element, fixes that element’s index, and truncates. Random picks a '
                      'uniform index and removes that value.'),
        ('OUTPUT', 'O(1) expected for all three'),
    ],
        why=[
            ['`List<int>` for the values',
             'Contiguous, so a uniform index is a uniform element, and `Count` is O(1). The order is '
             'meaningless and that is exactly what permits the swap.'],
            ['`Dictionary<int, int>` value → index',
             'Kills the linear search. Storing the index rather than anything else is what makes the '
             'removal O(1) — it is the same trick as Q1 storing the *node* rather than the value.'],
            ['Swap-with-last rather than shifting',
             'O(1) instead of O(n), available only because the array’s order carries no meaning.'],
            ['No tombstones, no free list',
             'The array must stay gap-free or `Next(Count)` stops being uniform. This is the reason to '
             'reject the tombstone approach, and it is worth saying rather than just not doing it.'],
        ],
        steps=[
            '`Insert`: if present, return false. Otherwise record `_indexOf[val] = _items.Count` and '
            'append.',
            '`Remove`: look up `slot`; absent → false.',
            'Read `last = _items[^1]`. Write `_items[slot] = last`.',
            '**Set `_indexOf[last] = slot` before truncating** — the ordering that makes the '
            'last-slot case work.',
            'Truncate the list and remove `val` from the dictionary.',
            '`RemoveRandomElement`: `slot = rng.Next(Count)`, read the value, call `Remove`.',
        ]),
    walk=dict(
        intro='The case that matters. Contents `[1, 2, 3]` with `_indexOf = {1:0, 2:1, 3:2}`. First remove '
              'a middle element, then remove the last one.',
        headers=['Step', '_items', '_indexOf', 'Note'],
        rows=[
            ['start', '[1, 2, 3]', '{1:0, 2:1, 3:2}', ''],
            ['Remove(2): slot = 1', '[1, 2, 3]', '', 'last = 3'],
            ['write last into the hole', '[1, **3**, 3]', '', 'slot 1 now holds 3'],
            ['fix the moved index', '', '{1:0, 2:1, **3:1**}', '3 is now at slot 1'],
            ['truncate, drop 2', '[1, 3]', '{1:0, 3:1}', 'gap-free, and correct'],
            ['Remove(3): slot = 1', '[1, 3]', '', 'last is **also** 3 — slot == last index'],
            ['write, fix, truncate', '[1]', '{1:0}', '`_indexOf[3] = 1` then `Remove(3)` deletes it anyway'],
        ],
        close='The last two rows are the whole test. When `slot` is the last index, the write is a '
              'self-assignment and `_indexOf[last] = slot` sets the index of the very value being '
              'deleted — which is harmless **only because the dictionary removal comes after**. '
              'Reverse those two lines and the entry is re-inserted after being removed, leaving a '
              'dictionary entry pointing past the end of the array. It passes every test where the '
              'removed element is not last.'),
    code=[
        ('The structure', 'Q12_RandomBag.cs', 'RandomBag'),
        ('The duplicates variant', 'Q12_RandomBag.cs', 'RandomMultiBag'),
    ],
    codewalk=[
        ('The ordering of the four lines in `Remove`',
         '`_items[slot] = last;` then `_indexOf[last] = slot;` then `RemoveAt`, then '
         '`_indexOf.Remove(value)`. When `slot` is the last index, `last == value`, so line 2 writes an '
         'index for the value being deleted and line 4 removes it. Swap lines 2 and 4 and you are left '
         'with a dictionary entry pointing at a slot that no longer exists — a bug that only fires '
         'when the removed element happens to be last.'),
        ('`_items[^1]` and then `RemoveAt(Count - 1)`',
         'The C# index-from-end operator for the read, and an explicit index for the removal. '
         '`List<T>.RemoveAt` on the final element is O(1) — there is nothing after it to shift — '
         'which is what keeps the whole operation constant time.'),
        ('Why `PeekRandom` and `RemoveRandomElement` are separate',
         '`RemoveRandomElement` is `Remove(PeekRandom())` in effect, and keeping the peek available is '
         'what makes the structure also answer LeetCode 380. The requirement asked for remove-random; '
         'having both costs three lines and makes the relationship obvious.'),
        ('Uniformity comes from the gap-free invariant',
         '`_rng.Next(_items.Count)` is uniform over indices, and uniform over indices is uniform over '
         'elements **only if every index holds a live element**. That is the invariant the swap preserves '
         'and that a tombstone scheme would destroy. It is the one-sentence justification for the whole '
         'design.'),
        ('The duplicates version: `Dictionary<int, HashSet<int>>`',
         'One value now owns several slots. `Remove` takes `set.First()` — an arbitrary copy, which '
         'is fine because the copies are indistinguishable. The delicate part is when the moved element '
         'has the **same value** as the one being removed: then `set` and `_slots[last]` are the same '
         'object, and the remove-then-add sequence has to leave exactly the right slot behind. The test '
         'suite covers that case specifically.'),
        ('`if (slot != lastSlot)` in the duplicates version',
         'Guarding the swap. Without it, removing the last slot would do `_slots[last].Remove(lastSlot)` '
         'followed by `.Add(slot)` with `slot == lastSlot`, re-adding the slot that was just removed. The '
         'base version does not need the guard because the dictionary removal comes last; the duplicates '
         'version does, because the set is shared.'),
    ],
    cx=dict(rows=[
        ['`Insert`', 'O(1) expected', 'O(1)', 'One dictionary write plus an amortised list append'],
        ['`Remove`', 'O(1) expected', 'O(1)', 'One lookup, one write, one truncate'],
        ['`RemoveRandomElement`', 'O(1) expected', 'O(1)', 'One random index plus a `Remove`'],
        ['space', '—', 'O(n)', 'One list slot and one dictionary entry per value'],
    ],
        note='**"Expected" is doing real work in all three, and the statement itself says so.** The bound '
             'rests on hashing: adversarial or pathological keys degrade a dictionary to O(n). The list '
             'operations are genuinely worst-case O(1) — appending is amortised because of resizing, '
             'and `RemoveAt` on the last element shifts nothing. So the honest summary is: O(1) worst case '
             'on the array side, O(1) expected on the dictionary side, and the composition is therefore '
             'expected. Saying that unprompted reads very differently from being corrected on it.'),
    edges=[
        ['Insert a duplicate', 'Returns false, changes nothing, in the base version.'],
        ['Remove an absent value', 'Returns false.'],
        ['**Remove the last slot**', 'The critical case. Works because the dictionary removal comes after '
                                     'the index fix.'],
        ['Remove the only element', 'Leaves both structures empty and consistent.'],
        ['`RemoveRandomElement` on empty', 'Throws. State the choice, or expose a `Try` variant.'],
        ['Drain the whole structure', 'Every value comes out exactly once — tested with 500 values.'],
        ['Re-insert a removed value', 'Fine; it gets a fresh slot at the end.'],
        ['Duplicates version, remove when the moved element shares the value',
         'The subtle case; the `slot != lastSlot` guard handles it.'],
        ['Very large n', 'Bounded by memory. The list resizing is amortised O(1) and doubles capacity, so '
                         'peak memory is up to 2× the live set — worth knowing if memory is '
                         'tight.'],
    ],
    fups=[
        dict(q='Allow duplicates.',
             thinking='Which part of the design stops working? The value → index map, because a value '
                      'no longer has *an* index. Everything else survives.',
             approach='`Dictionary<int, HashSet<int>>` from value to the set of slots holding it. '
                      '`Remove` picks any slot from the set — copies are indistinguishable — and '
                      'performs the same swap, updating the moved element’s slot in its own set. The '
                      'array stays gap-free, so randomness is unchanged and is now uniform over '
                      '**occurrences**: a value present three times is three times as likely, which is '
                      'usually what is wanted and should be stated either way.',
             tradeoff='A `HashSet` per distinct value instead of an `int`, so materially more memory and '
                      'an extra indirection on every operation. This is LeetCode 381 and it is rated '
                      'Hard, entirely because of the bookkeeping when the moved element shares the value '
                      'being removed. Everything stays O(1) expected.',
             code=[('Duplicates allowed', 'Q12_RandomBag.cs', 'RandomMultiBag')],
             t='O(1) expected', s='O(n) with a larger constant'),
        dict(q='Make it thread-safe.',
             thinking='The two structures have to move together. Any window in which the array has been '
                      'truncated but the dictionary has not is a window in which a random pick can read '
                      'past the end.',
             approach='One lock around each operation. The critical section is a handful of writes, so it '
                      'is short even under contention, and `ConcurrentDictionary` alone would be '
                      '**wrong** — it makes each dictionary operation atomic without making the '
                      'pair atomic, which is the actual requirement.',
             tradeoff='Simple and correct, and it serialises everything including the random reads. '
                      'Sharding is much harder here than for a cache: a uniform random pick across shards '
                      'has to be weighted by each shard’s size, and reading those sizes without a '
                      'lock reintroduces the race. The pragmatic answer is one lock and, if reads dominate '
                      'and slight staleness is acceptable, a snapshot for the random path.',
             t='O(1) plus lock acquisition', s='unchanged'),
        dict(q='Weight the random selection.',
             thinking='The gap-free array gives uniformity for free, and weighting is exactly the thing '
                      'it cannot do.',
             approach='Two options. If weights are small integers, insert each value **w times** — '
                      'the duplicates version already handles it and uniformity over occurrences becomes '
                      'weighting for free. For arbitrary weights, prefix sums plus binary search, which '
                      'is `528 Random Pick with Weight` and is on the supplied list.',
             tradeoff='Repeated insertion keeps every operation O(1) and costs memory proportional to the '
                      'total weight. Prefix sums cost O(log n) per pick and O(n) to rebuild after any '
                      'change, which makes them poor for a mutable structure. Since this structure’s '
                      'whole point is mutation, repeated insertion is the better fit here — and that '
                      'is the reasoning, not the answer, that matters.',
             t='O(1) for repeated insertion; O(log n) for prefix sums', s='O(total weight) or O(n)'),
        dict(q='It must be a snapshot — callers iterate while others mutate.',
             thinking='Iteration was never in the requirements, and adding it changes the structure’s '
                      'character from a bag to a collection.',
             approach='Copy-on-write: mutations build a new array and dictionary and publish the pair '
                      'atomically behind a single reference, so an iterator holds a consistent immutable '
                      'snapshot. Alternatively hand out an explicit `ToArray()` copy and keep mutation '
                      'cheap.',
             tradeoff='Copy-on-write makes every mutation O(n), which destroys the entire point of the '
                      'structure. The explicit-copy option keeps mutations O(1) and makes the snapshot '
                      'O(n) at the moment it is taken, which is almost certainly the right trade — '
                      'iteration is rare, mutation is the hot path. Worth saying plainly that '
                      'copy-on-write would be the wrong call here.',
             t='O(n) per mutation for CoW; O(n) per snapshot otherwise', s='O(n) per live snapshot'),
    ],
    testing=dict(skills=[
        '**Structure composition** — two structures each covering the other’s weakness.',
        '**Recognising which properties are not required** — the array need not be ordered, and that '
        'is what unlocks O(1) deletion.',
        '**Invariant identification** — gap-free is what makes the randomness uniform.',
        '**Index bookkeeping** — the last-slot case, which is where this is actually implemented '
        'wrongly.',
        '**Expected versus worst case** — the statement raises it, so it should be addressed.',
    ],
        senior='Builds list plus dictionary, gets the swap-with-last right including the last-slot case, '
               'and composes remove-random from the pieces.',
        staff='Does that, and: says explicitly that the array’s order is meaningless and that this is '
              'what permits the swap; names the gap-free invariant as the justification for uniformity and '
              'uses it to reject tombstones; asks about duplicates before choosing the map type; addresses '
              '"expected" by separating the worst-case array operations from the expected-case hashing; '
              'and on the weighting follow-up, argues from *this structure being mutable* rather than '
              'reciting both options. Naming the invariant is the discriminating move — it is what '
              'turns a memorised trick into a design.'),
    say=[
        "Let me take the three requirements one at a time, because each one rules out the structure that "
        "serves the others.",
        "A dictionary gives me O(1) insert and O(1) delete by value, but there is no way to pick a uniform "
        "random entry of a hash table in constant time.",
        "An array gives me the uniform pick for free — one call to the random generator — but deleting a "
        "specific value means finding it, which is linear, and then closing the hole, which is also linear.",
        "So I hold both: the array holds the values, and the dictionary maps each value to its index in the "
        "array. That kills the linear search.",
        "The remaining problem is the hole. And the key realisation is that nothing requires the array to "
        "be ordered — its only job is to be a gap-free list of the current contents. So instead of "
        "shifting, I move the last element into the hole and shorten the array.",
        "That gap-free property is the invariant the whole thing rests on, because a uniform index is only "
        "a uniform element if every index holds something live. It is also why I would not use tombstones — "
        "a random index could land on a hole.",
        "One detail I would write a test for first: when the slot I am removing is the last slot. The swap "
        "becomes a self-assignment, and I have to fix the moved element's index before removing the value "
        "from the dictionary — otherwise I re-insert the entry I just deleted and leave it pointing past "
        "the end of the array. It passes every test where the element is not last.",
        "Then remove-random is just the composition: uniform index, read the value, same removal path. No "
        "new machinery.",
        "One thing on the complexity — you said expected, and that is right. The array operations are "
        "genuinely worst-case constant; it is the hashing that is only expected. Worth separating.",
        "And I would ask about duplicates, because that changes the map from value-to-index to "
        "value-to-set-of-indices, and it changes what uniform means — uniform over occurrences rather than "
        "over distinct values.",
    ],
    video=dict(title='LinkedIn Coding — Insert, Remove and Remove-Random in O(1)', mins=13,
               objective='Derive the pairing from the three requirements, name the gap-free invariant, and '
                         'spend real time on the last-slot bug.',
               beats=[('0:00', 'The three requirements'),
                      ('1:10', 'Why a dictionary alone cannot do it'),
                      ('2:20', 'Why an array alone cannot do it'),
                      ('3:30', 'Holding both — value to index'),
                      ('4:50', 'The order is meaningless: swap with last'),
                      ('6:10', 'The gap-free invariant, and why it means no tombstones'),
                      ('7:30', 'The C# implementation'),
                      ('8:40', 'The last-slot case, line by line'),
                      ('10:10', 'Remove-random for free'),
                      ('11:00', 'Duplicates: value to set of slots'),
                      ('12:10', 'How to say it')]),
))

# ============================================================ Q13
QUESTIONS.append(dict(
    id='q13', n=13, name='Rank-based cache',
    tags=['DESIGN', 'DATA STRUCTURE DESIGN', 'CACHE', 'HEAP', 'HASHING'],
    diff='MEDIUM', prio='HIGH',
    verdict_short='InterviewDB + a first-hand report of an LFU cache with GetRank()',
    prio_why=(
        'A LeetCode Discuss report from a **LinkedIn Staff SWE with an offer, June 2025**, describes an '
        '"LFU cache with a GetRank() function, LRU as the tiebreaker" — first-hand, recent, and '
        'strikingly close to this. `432 All O’one`, `460 LFU` and `215 Kth Largest` are all on the '
        'supplied list. High priority: the ranked-eviction cache is one of the best-attested shapes at '
        'LinkedIn, and it composes with Q1.'),
    idb=(
        'Create a cache with:\n\n'
        '• fixed capacity\n'
        '• static distinct integer ranks\n'
        '• key/value\n'
        '• slow DataSource\n\n'
        'If cache is full:\n\n'
        'evict the item with the lowest rank.\n\n'
        'If the requested item is not cached:\n\n'
        'retrieve from DataSource.'),
    dd=dict(elsewhere=[
        ('idb', 'The two words that matter are **static** and **distinct**. Static means ranks never '
                'change, which removes the hardest part of LFU. Distinct means a rank-ordered structure '
                'can compare on rank alone and lose nothing. Both are gifts, and both should be '
                'acknowledged out loud — they are what make this Medium rather than Hard.'),
        ('reported', '**"LFU cache with a GetRank() function, LRU as the tiebreaker"** — LeetCode '
                     'Discuss, LinkedIn Staff SWE with offer, Jun 2025. First-hand. That question is '
                     'harder than this one (frequency is dynamic) but the shape is the same.'),
        ('reported', '**All O’one Data Structure (LeetCode 432)** — on your own list. It is the '
                     'answer to the follow-up where ranks stop being static.'),
        ('lc', '460 LFU Cache and 215 Kth Largest are both on the supplied list. 460 is this with a '
               'dynamic rank; 215 is the selection half in isolation.'),
    ],
        verdict='**InterviewDB reported, with a very close first-hand report from a successful Staff '
                'candidate.** The strongest evidence on the page after Q5 and Q17.'),
    ambiguity=(
        'The interesting gap: **what happens when the new item’s rank is lower than everything in '
        'the cache?**\n\n'
        'Taken literally, "if the cache is full, evict the lowest rank" would have you evict a better '
        'item and store a worse one — and if the next request is for that same low-ranked key, you '
        'would do it again, thrashing the cache with the least valuable data. That is clearly not '
        'intended, but the statement does not rule it out.\n\n'
        'I **decline to cache** in that case and return the value anyway, which is an admission policy '
        'rather than an eviction policy, and I would say so explicitly. It is the single best thing to '
        'raise on this question, because it is a real design decision hiding in an under-specified '
        'sentence.\n\n'
        'Also unstated: is rank available without a fetch? `GetRank(key)` as a separate method implies '
        'yes, which matters — if rank were only known *after* the expensive fetch, you could not '
        'decide admission before paying for the data.'),
    understand=dict(
        what='A cache in front of something slow, where importance is given rather than inferred. Unlike '
             'LRU or LFU, the cache is told what each item is worth and never has to guess.',
        compute='`Get(key)` returns the value, from the cache if present and from the source otherwise. '
                'The design content is the eviction and admission policy around it.',
        constraints=[
            'Ranks are **static** — they never change for a key. This is what makes a heap or sorted '
            'set viable, because nothing ever needs re-prioritising.',
            'Ranks are **distinct**, so comparing on rank alone is a total order.',
            'Fixed capacity; eviction is by lowest rank.',
            'The data source is slow, so a miss is expensive and the hit rate is the thing being '
            'optimised.',
        ],
        assume=[
            ['`GetRank(key)` is cheap and available without fetching the value.',
             'If rank came only with the data, admission could not be decided before paying the fetch '
             'cost — the policy would have to become "fetch, then decide whether to keep", which is '
             'still correct but much less useful.'],
            ['A low-ranked newcomer is **not** cached when the cache is full.',
             'The literal reading would evict something better to store something worse. This is the '
             'clarification to raise.'],
            ['Ranks really are distinct.',
             '**The comparer depends on it.** Comparing on rank alone means two items with equal rank '
             'look identical to the sorted set, and one would be silently dropped. If ranks could '
             'collide, the comparer must fall back to the key.'],
            ['No TTL, no invalidation.',
             'With static ranks and immutable values there is nothing to expire. If values could change '
             'behind the cache, this becomes Q1 and needs a TTL or an invalidation hook.'],
        ]),
    examples=[
        ('Setup', 'capacity 3, ranks a=10 b=20 c=30 d=5 e=40', ''),
        ('', 'Get(a), Get(b), Get(c)', '3 source calls; cache full'),
        ('', 'Get(a) again', 'hit — no source call'),
        ('', 'Get(e), rank 40', 'a (rank 10, the lowest) evicted; e admitted'),
        ('Key case', 'Get(d), rank 5', '**not cached** — 5 is below every rank held; value still returned'),
        ('', 'cache still holds b, c, e', 'nothing was evicted for d'),
    ],
    examples_note='No examples were supplied. The "Key case" row is the ambiguity above, and the test '
                  'suite asserts both halves of it: that `d` is not admitted, and that `Get(d)` still '
                  'returns the correct value. A cache that declines to store something must still answer '
                  'the question.',
    observation=(
        'Two observations, and the first one is a gift you should notice out loud.\n\n'
        '**Static ranks remove the hard part of LFU.** In an LFU cache, every access changes a key’s '
        'frequency, so the priority structure must support "increase the priority of this arbitrary '
        'element", which a plain heap cannot do in better than O(n). That is why LFU needs the '
        'bucket-of-equal-counts construction from `432 All O’one`. Here, rank never changes. So '
        'nothing is ever re-prioritised, and a simple ordered structure is enough. Saying "this is much '
        'easier than LFU, and here is exactly why" is a strong opening.\n\n'
        '**Distinct ranks let you compare on rank alone.** The eviction victim is the minimum rank, so '
        'you need a structure that yields its minimum cheaply, plus a dictionary for O(1) lookup by key. '
        'Same pairing as Q1 and Q12: one structure for the ordering, one for the lookup.\n\n'
        'A min-heap gives O(1) peek and O(log n) pop. A `SortedSet` gives O(log n) minimum and, unlike a '
        'heap, supports removing an arbitrary element — which a heap cannot do without an auxiliary '
        'index. Since nothing here needs arbitrary removal yet, either works; the sorted set costs '
        'nothing extra and keeps the door open.\n\n'
        'And then the third thing, which the statement does not ask and which is the actual design '
        'judgement: **eviction policy and admission policy are different questions.** "Evict the lowest '
        'rank" says what leaves. It does not say what is allowed in. If a newcomer ranks below everything '
        'held, admitting it means evicting something better — so the right policy is to serve the '
        'value and not cache it. Recognising that an under-specified sentence conceals a second policy is '
        'the staff-level move here.'),
    brute=dict(
        how='A `Dictionary<TKey, (value, rank)>`. On a miss when full, scan every entry to find the lowest '
            'rank and evict it.',
        cx='`Get` O(1) on a hit, O(capacity) on an eviction. Space O(capacity).',
        why_not='At capacity 100 the scan is irrelevant and this is a perfectly good answer to give '
                'first. It stops being fine at capacity 100,000 — and more importantly, it is the '
                'same self-defeating shape as Q1’s brute force: the larger you make the cache to '
                'improve the hit rate, the more each miss costs. A structure that knows its own minimum '
                'removes that coupling.'),
    optimal=dict(pipeline=[
        ('INPUT', '`Get(key)`, a capacity, and an `IRankedDataSource`'),
        ('TRANSFORMATION', 'Each entry is stored twice: by key for lookup, and by rank for eviction'),
        ('DATA STRUCTURE', '`Dictionary<TKey, (TValue, int)>` plus `SortedSet<(int Rank, TKey Key)>` with '
                           'a rank-only comparer'),
        ('ALGORITHM', 'Hit → return. Miss → fetch, then admit only if the rank beats the '
                      'current minimum; admitting evicts the minimum.'),
        ('OUTPUT', 'The value, always; caching is a separate decision'),
    ],
        why=[
            ['`Dictionary` for lookup',
             'O(1) hit path, which is the whole reason a cache exists.'],
            ['`SortedSet<(int Rank, TKey Key)>` for eviction order',
             'O(log n) minimum and O(log n) arbitrary removal. A `PriorityQueue` would give a cheaper '
             'peek and **cannot remove an arbitrary element**, which forecloses the invalidation '
             'follow-up. The sorted set costs a log factor on peek and keeps the option.'],
            ['A comparer on **rank only**',
             'Avoids requiring `TKey : IComparable`, which would be an unnecessary constraint on the '
             'cache’s users. Safe **because ranks are distinct** — and if that guarantee '
             'failed, the comparer would silently drop entries, which is the thing to flag.'],
            ['Admission check before eviction',
             'The policy decision. Comparing the newcomer’s rank against the current minimum is one '
             'line and it is what stops the cache being thrashed by low-value keys.'],
            ['Counters for hits, misses, admissions and rejections',
             'A cache you cannot observe is a cache you cannot tune. Four increments, and they turn "is '
             'the policy working" from an argument into a measurement.'],
        ],
        steps=[
            '`Get`: dictionary hit → count it and return.',
            'Miss → fetch the value and the rank from the source.',
            'If the cache is not full, store and index it.',
            'If full, compare the new rank with `_byRank.Min.Rank`.',
            'Lower → count a rejection and return the value **without caching**.',
            'Higher → evict the minimum from both structures, then store and index the newcomer.',
        ]),
    walk=dict(
        intro='Capacity 3. Ranks: a=10, b=20, c=30, d=5, e=40. The two interesting steps are the '
              'admission of `e` and the rejection of `d`.',
        headers=['Call', 'Source?', 'Entries', 'byRank (min first)', 'Note'],
        rows=[
            ['Get(a)', 'yes', 'a', '(10,a)', ''],
            ['Get(b)', 'yes', 'a b', '(10,a) (20,b)', ''],
            ['Get(c)', 'yes', 'a b c', '(10,a) (20,b) (30,c)', 'full'],
            ['Get(a)', '**no**', 'a b c', 'unchanged', 'hit — the point of the cache'],
            ['Get(e) rank 40', 'yes', 'b c **e**', '(20,b) (30,c) (40,e)', '40 > min 10 → evict a, admit e'],
            ['Get(d) rank 5', 'yes', 'b c e', 'unchanged', '**5 < min 20 → not admitted**; value returned'],
            ['Get(d) again', 'yes', 'b c e', 'unchanged', 'still a miss — the cost of the policy'],
        ],
        close='The last two rows are the trade. Rejecting `d` protects three better-ranked entries, and '
              'the price is that every request for `d` pays the source. That is correct under the '
              'assumption that rank reflects value — and if `d` were requested a thousand times a '
              'second, rank would be the wrong signal and the cache would need to combine rank with '
              'frequency. Worth naming as the limit of the policy rather than defending it absolutely.'),
    code=[
        ('The data source interface', 'Q13_RankCache.cs', 'IRankedDataSource'),
        ('The cache', 'Q13_RankCache.cs', 'RankCache'),
    ],
    codewalk=[
        ('The `ByRank` comparer, and the guarantee it leans on',
         'It compares `a.Rank.CompareTo(b.Rank)` and ignores the key. A `SortedSet` treats '
         '"compares equal" as "is the same element", so two entries with the same rank would collapse and '
         'one would be silently lost. **Distinct ranks are what make this safe**, and the comment says so '
         'in the code. If the guarantee were dropped, the comparer would need `?: a.Key.CompareTo(b.Key)` '
         'and `TKey` would have to be comparable.'),
        ('Why the value is returned even when not cached',
         '`Get` fetches, calls `Admit`, and returns the value regardless of what `Admit` decided. Caching '
         'is an optimisation, not part of the contract — conflating the two is how a cache ends up '
         'unable to serve keys it has chosen not to store.'),
        ('`if (rank < lowest.Rank) { Rejected++; return; }`',
         'The admission policy, in one line. Everything before it is mechanism; this is the judgement. '
         'Note `<` rather than `<=`: an equal rank cannot occur given the distinctness guarantee, so the '
         'choice is moot — but writing `<` rather than `<=` means the code would prefer the incumbent '
         'on a tie, which is the conservative behaviour.'),
        ('Eviction touches both structures',
         '`_byRank.Remove(lowest)` and `_entries.Remove(lowest.Key)`. The invariant is that the two hold '
         'the same key set at all times, and the tuple in the sorted set carries the key precisely so the '
         'dictionary entry can be found from it — the same reason Q1’s node carries its key.'),
        ('The four counters',
         '`Hits`, `Misses`, `Admitted`, `Rejected`. The last two are the ones that matter for this design: '
         'a high rejection count means capacity is too small for the rank distribution, and that is not '
         'visible from the hit rate alone. It is two lines of code and it is the difference between a '
         'policy you can tune and one you can only argue about.'),
        ('`LowestRank` as a public property',
         'Exposed for tests, and useful in production for the same reason — it is the admission '
         'threshold, so it answers "what rank do I need to get cached right now".'),
    ],
    cx=dict(rows=[
        ['`Get` (hit)', 'O(1) expected', 'O(1)', 'One dictionary probe'],
        ['`Get` (miss, not full)', 'O(log n)', 'O(1)', 'Source fetch plus one sorted-set insert'],
        ['`Get` (miss, admitted)', 'O(log n)', 'O(1)', 'One `Min`, one remove, one insert'],
        ['`Get` (miss, rejected)', 'O(log n)', 'O(1)', 'One `Min`, then nothing'],
        ['space', '—', 'O(capacity)', 'One dictionary entry and one set entry per cached key'],
    ],
        note='**The source fetch dominates everything on this table and it is worth saying so.** A slow '
             'data source is by definition orders of magnitude above a log-n in-memory operation, so '
             'optimising O(log n) to O(1) here would be pointless. What matters is the **hit rate**, '
             'which is a function of the policy rather than of the data structures — which is why '
             'the admission decision deserves more of the discussion than the choice between a heap and a '
             'sorted set.'),
    edges=[
        ['Capacity 0 or negative', 'Throws in the constructor.'],
        ['First `Get` on an empty cache', 'Miss, fetch, store. No eviction path taken.'],
        ['Cache full, newcomer ranks highest', 'Minimum evicted, newcomer admitted.'],
        ['Cache full, newcomer ranks lowest', '**Not admitted**; value still returned. The design '
                                              'decision.'],
        ['Repeated request for a rejected key', 'Every one is a miss. The cost of the policy, and a '
                                                'counter makes it visible.'],
        ['Same key requested twice', 'Second is a hit; the source is called once.'],
        ['Equal ranks, despite the guarantee', 'The comparer would treat them as one entry and silently '
                                               'lose one. Flag it — the code depends on the '
                                               'guarantee the statement gave.'],
        ['Source throws', 'Propagates. The cache is unchanged, because nothing is stored until the fetch '
                          'succeeds.'],
        ['Capacity 1', 'Works: every miss with a higher rank replaces the single entry.'],
    ],
    fups=[
        dict(q='Ranks are no longer static — they change as items are accessed. Now what?',
             thinking='This is the question that turns it into LFU, and the structure that made it easy '
                      'stops working. Say what breaks before saying what to do.',
             approach='A heap cannot increase the priority of an arbitrary element without an index into '
                      'it, and a `SortedSet` needs remove-then-reinsert, O(log n) per access — on the '
                      '**hit** path, which was O(1). That is the real cost: the hot path gets slower.\n\n'
                      'The proper answer is the `432 All O’one` construction: a doubly linked list of '
                      'count buckets, each bucket holding the keys with that count, plus a map from key to '
                      'its bucket. Incrementing a count is unlinking from one bucket and linking into the '
                      'adjacent one — O(1). The minimum is the head bucket. That is also how LFU '
                      'caches are built, and the reported LinkedIn question adds LRU ordering *within* a '
                      'bucket, which the bucket’s own list gives you for free.',
             tradeoff='O(1) everything, for considerably more code and a structure that is genuinely '
                      'fiddly to get right. With static ranks none of it is needed, which is exactly why '
                      'the word "static" in the statement is worth acknowledging — it is the '
                      'difference between this question and a Hard one.',
             t='O(1) with buckets; O(log n) per access with a sorted set', s='O(capacity)'),
        dict(q='Combine rank with recency, so a low-ranked but very hot key can still be cached.',
             thinking='The walkthrough exposed the weakness: a rejected key requested constantly pays the '
                      'source every time. Rank alone cannot see that.',
             approach='Score each entry as a function of both, for example `rank + w · recencyBonus`, '
                      'and evict the lowest score. Or segment the cache: reserve most of the capacity for '
                      'rank-ordered entries and a small window for recently-requested ones, promoting a '
                      'key out of the window if it is requested again. The segmented approach is what '
                      'production caches actually do — it is the shape of both ARC and W-TinyLFU.',
             tradeoff='A combined score makes the priority dynamic, so the previous follow-up’s '
                      'problem arrives with it. Segmentation keeps each structure simple and static, at '
                      'the cost of a tuning parameter — how big the window is — which nobody '
                      'can set correctly without measurement. I would segment, and instrument it, and let '
                      'the rejection counter tell me the window size.',
             t='O(log n) per eviction', s='O(capacity)'),
        dict(q='It is distributed across many nodes.',
             thinking='"Evict the globally lowest rank" needs global knowledge, and no cache pays for that '
                      'on the eviction path.',
             approach='Partition by key with consistent hashing; each node runs this cache over its own '
                      'shard. Eviction becomes per-shard, so the item evicted is the lowest rank **on that '
                      'node**, not globally. Ranks being static helps enormously here — they need no '
                      'coordination or replication, so every node can decide independently and no node '
                      'ever disagrees with another about an item’s worth.',
             tradeoff='Per-shard eviction is approximate: a globally high-ranked item can be evicted '
                      'because its shard happens to be full of even better items. That is the same '
                      'approximation as sharded LRU and it is universally accepted. Static ranks make this '
                      'the easiest distributed cache of the three on this page, and that is worth saying.',
             t='O(log n) local plus one network hop', s='O(capacity) per node'),
        dict(q='Values can change in the source. Keep the cache correct.',
             thinking='The statement gave no invalidation requirement, so this changes the contract rather '
                      'than the implementation — worth saying before answering.',
             approach='Either a TTL per entry, which is Q1 and composes directly, or an explicit '
                      '`Invalidate(key)` that removes from both structures. **This is where the choice of '
                      '`SortedSet` over `PriorityQueue` pays off**: arbitrary removal is O(log n) on a '
                      'sorted set and impossible on a heap without an auxiliary index.',
             tradeoff='TTL is self-healing and serves stale data for up to the TTL. Explicit invalidation '
                      'is exact and needs the source to notify the cache, which is a coupling that does '
                      'not always exist. Most systems use both — invalidation where a signal exists, '
                      'TTL as the backstop — and saying that is better than picking one.',
             t='O(log n) for invalidation', s='unchanged'),
    ],
    testing=dict(skills=[
        '**Reading the gift in the statement** — "static" and "distinct" are load-bearing, and '
        'noticing them is the difference between this and LFU.',
        '**Structure pairing** — dictionary for lookup, ordered structure for eviction. The third '
        'question on this page with that shape.',
        '**Separating eviction from admission** — the under-specified case, and the best thing to '
        'raise.',
        '**Library knowledge** — why `SortedSet` rather than `PriorityQueue`, and what that choice '
        'buys later.',
        '**Knowing where the time actually goes** — the source fetch dominates, so hit rate beats '
        'asymptotics.',
        '**Observability** — a policy without counters cannot be tuned.',
    ],
        senior='Builds dictionary plus heap or sorted set, evicts the minimum rank, and handles the miss '
               'path correctly.',
        staff='Does that, and: says up front that static ranks make this much easier than LFU and why; '
              'raises the low-ranked-newcomer case as an **admission** policy distinct from eviction, and '
              'chooses not to cache; notes that the rank-only comparer depends on the distinctness '
              'guarantee and would silently lose entries without it; picks `SortedSet` over '
              '`PriorityQueue` for the arbitrary-removal capability and says which follow-up that enables; '
              'observes that the source fetch dominates so the hit rate matters more than the log factor; '
              'and adds rejection counters so the policy is measurable. The admission-versus-eviction '
              'distinction is the discriminating one — it is a real design decision that the '
              'statement leaves out.'),
    say=[
        "Two words in the statement are doing a lot of work, and I want to acknowledge them. Static and "
        "distinct.",
        "Static ranks make this much easier than LFU. In an LFU cache every access changes a key's "
        "frequency, so the priority structure has to support increasing the priority of an arbitrary "
        "element, which a heap cannot do cheaply — that is why LFU needs the bucket construction from All "
        "O'one. Here rank never changes, so nothing is ever re-prioritised.",
        "Distinct ranks mean I can compare on rank alone, which saves me from requiring the key type to be "
        "comparable. Worth flagging though: a sorted set treats compares-equal as same-element, so if "
        "ranks could collide I would silently lose entries. My comparer depends on your guarantee.",
        "So: a dictionary from key to value and rank for the O(1) hit path, and a sorted set ordered by "
        "rank so the eviction victim is the minimum.",
        "Now the part your statement does not specify, and I think it is the interesting one. What happens "
        "when the new item's rank is lower than everything already cached? Taken literally I would evict "
        "something better to store something worse, and if that key were requested again I would do it "
        "again.",
        "So I would separate two policies. Eviction says what leaves — lowest rank. Admission says what is "
        "allowed in, and I would decline to cache a newcomer that ranks below the current minimum. I still "
        "return the value; caching is an optimisation, not part of the contract.",
        "The cost of that is real: a rejected key pays the source on every request. So I would count "
        "rejections, because a high rejection rate tells me the capacity is too small for the rank "
        "distribution, and the hit rate alone would not show that.",
        "One more thing on complexity — the source is slow, so it dominates everything here. Optimising "
        "the log n to constant would be pointless. What matters is the hit rate, which comes from the "
        "policy rather than the structures.",
        "I chose SortedSet over PriorityQueue deliberately. A heap has a cheaper peek and cannot remove an "
        "arbitrary element, and I would want that if you later asked for invalidation.",
    ],
    video=dict(title='LinkedIn Coding — A Cache That Is Told What Matters', mins=15,
               objective='Read the gift in the statement, then spend the lesson on the policy decision '
                         'the statement leaves out.',
               beats=[('0:00', 'The question'),
                      ('1:00', 'Why "static" makes this much easier than LFU'),
                      ('2:40', 'Why "distinct" lets the comparer ignore the key'),
                      ('4:00', 'The pairing: dictionary plus sorted set'),
                      ('5:20', 'SortedSet or PriorityQueue — and what the choice buys later'),
                      ('6:40', 'The gap: what if the newcomer ranks lowest?'),
                      ('8:20', 'Eviction policy versus admission policy'),
                      ('9:40', 'The C# implementation'),
                      ('11:10', 'Walking the admission and the rejection'),
                      ('12:20', 'Why the source fetch dominates the complexity table'),
                      ('13:20', 'Follow-up: dynamic ranks, and All O’one'),
                      ('14:20', 'How to say it')]),
))

# ============================================================ Q14
QUESTIONS.append(dict(
    id='q14', n=14, name='Theatre seating',
    tags=['ARRAY', 'GREEDY'],
    diff='EASY', prio='LOWER',
    verdict_short='InterviewDB only; no corroboration anywhere',
    prio_why=(
        '**Nothing else in this workspace mentions it**, and its public twin — `605 Can Place '
        'Flowers` — is not on the supplied number list either. `256 Paint House` is the only '
        'adjacency-along-a-line problem in the supplied numbers and it is a weak link, being DP rather '
        'than greedy. Lower priority, but do it anyway: it is ten minutes, and the boundary handling is '
        'the kind of thing that costs marks on an easy question.'),
    idb=(
        'Given:\n\n'
        '[1,0,0,0,0,0,1,0,0]\n\n'
        'Determine whether N additional people can be seated where no new person sits next to another '
        'person.\n\n'
        'Expected:\n\n'
        '3 → true\n'
        '4 → false\n\n'
        'Also handle:\n\n'
        '[1,0,0,1,0,0,1,0,0]\n\n'
        'and:\n\n'
        '[0]'),
    dd=dict(elsewhere=[
        ('idb', 'Supplied with three arrays and two expected answers for the first, which is enough to '
                'pin the semantics down completely. I verified all three by hand and by test.'),
        ('inference', 'No report anywhere else in this workspace. Not on Glassdoor, Blind, Taro, LeetCode '
                      'Discuss or Exponent for LinkedIn.'),
        ('lc', '**605 Can Place Flowers** is this problem exactly — flowers instead of theatre seats. '
               'It is **not** on the supplied number list. 256 Paint House is the nearest supplied '
               'number and is only loosely related.'),
    ],
        verdict='**InterviewDB reported. Not corroborated at all.** The weakest evidence on the page, '
                'alongside Q16. Low cost to prepare, so the weak evidence matters little.'),
    ambiguity=(
        'Does the existing arrangement have to be valid? `[1,1,0]` has two people already adjacent. The '
        'question asks only about **new** people — "no new person sits next to another person" '
        '— so an already-invalid row is simply the starting state and is not rejected.\n\n'
        'That reading is confirmed by the phrasing and it is worth stating, because the alternative '
        '(validate first, throw if invalid) changes the contract. My tests skip pre-invalid rows when '
        'cross-checking the two implementations, which is a deliberate choice about what is in scope '
        'rather than an oversight.\n\n'
        'Second, minor: `N = 0` is trivially true, and negative N should be too. One line.'),
    understand=dict(
        what='A row of seats, some taken. Fit as many more people in as possible with nobody ever seated '
             'directly beside anybody, then compare against N.',
        compute='A boolean, but compute the **maximum** first and compare. Returning the maximum is more '
                'useful, more testable, and no more work.',
        constraints=[
            'A new person needs both neighbours free. Out-of-bounds counts as free, which is where the '
            'bugs live.',
            'Existing people constrain but are not removed.',
            'One pass, O(1) extra space, is achievable.',
        ],
        assume=[
            ['The existing arrangement may already be invalid.',
             'The question is only about new people. Validating first would be a different contract — '
             'state the reading.'],
            ['Out-of-bounds neighbours count as free.',
             'So position 0 has only a right neighbour. Getting this wrong makes `[0]` return 0 instead of '
             '1, which is one of the supplied cases.'],
            ['The input must not be mutated.',
             'The greedy needs to mark seats as it goes, so it works on a clone. A caller whose array is '
             'silently modified by a query is a real bug, and the test asserts it does not happen.'],
            ['`N <= 0` is true.',
             'Trivially. One line, and it avoids an unnecessary scan.'],
        ]),
    examples=[
        ('Given', '[1,0,0,0,0,0,1,0,0], N=3', 'true — seats at 2, 4 and 8'),
        ('Given', '[1,0,0,0,0,0,1,0,0], N=4', 'false — the maximum is 3'),
        ('Given', '[1,0,0,1,0,0,1,0,0]', 'maximum 1 — only index 8 works'),
        ('Given', '[0]', 'maximum 1 — a lone empty seat, both neighbours out of bounds'),
        ('Mine', '[1]', '0'),
        ('Mine', '[1,0,1] / [1,0,0,1] / [1,0,0,0,1]', '0 / 0 / 1 — gaps of 1, 2 and 3 between people'),
        ('Mine', '[0,0,0,0,0]', '3 — seats at 0, 2 and 4'),
    ],
    examples_note='All three supplied arrays are in the test suite with the expected values above. The '
                  'gap-size row is the useful one for reasoning: a gap of three between two occupied '
                  'seats admits exactly one person, and gaps of one or two admit none. The O(1)-space '
                  'variant is cross-checked against the cloning one on every valid random row up to '
                  'length 12 — 4,000 trials.',
    observation=(
        'Scan left to right and take every seat you legally can. That is the whole algorithm, and the '
        'question is **why it is optimal** — because "greedy works here" is the claim an interviewer '
        'will push on.\n\n'
        'The exchange argument: suppose some optimal seating does *not* use the leftmost available seat '
        '`i`, and instead uses some seat `j > i`. Occupying `i` only constrains `i-1` and `i+1`. Since `i` '
        'was the leftmost available seat, `i-1` was not available anyway. So moving that person from `j` '
        'to `i` can only free up seats to the right, never block any — the count does not decrease. '
        'Repeat, and any optimal solution can be rewritten into the leftmost-first one without losing '
        'anybody. Therefore leftmost-first is optimal.\n\n'
        'The mechanical point is that the scan must **see its own decisions**. Having seated someone at '
        '`i`, the check at `i+1` has to know that. Working on a clone and writing the seat back is the '
        'simplest way; carrying the index of the last occupied seat is the O(1)-space way. Either is fine; '
        'reading the original array while pretending it was updated is the bug.\n\n'
        'And then the boundaries, which is where this is actually got wrong: **position 0 has no left '
        'neighbour and the last position has no right neighbour**, and both count as free. `[0]` returns 1 '
        'precisely because of that, which is presumably why it was supplied as a case.'),
    brute=dict(
        how='Enumerate every subset of the free seats, check each for adjacency violations, and take the '
            'largest valid one.',
        cx='O(2^n · n). O(n) space.',
        why_not='Exponential for a problem that is linear, and it also teaches nothing — it cannot '
                'answer "why is greedy right" because it never makes a choice. The useful intermediate '
                'thought is per-gap arithmetic: a run of `g` free seats bounded by occupied seats admits '
                '`(g-1)/2` people, and a run at the end of the array admits `g/2`. That closed form is '
                'correct and is a fine alternative answer, but it needs four cases depending on which '
                'ends are bounded, and the greedy scan handles all four without enumerating them.'),
    optimal=dict(pipeline=[
        ('INPUT', 'A 0/1 array and an integer N'),
        ('TRANSFORMATION', 'None — the array is already the state'),
        ('DATA STRUCTURE', 'None. A clone of the array, or a single integer for the last occupied index.'),
        ('ALGORITHM', 'Left to right, seat at any free position whose neighbours are both free, counting '
                      'out-of-bounds as free'),
        ('OUTPUT', 'The maximum number of additional people, compared against N'),
    ],
        why=[
            ['A clone rather than mutating the input',
             'The scan must see its own decisions, and a query that modifies its argument is a bug '
             'waiting to happen. One allocation, and the test asserts the original is untouched.'],
            ['Or a single `lastTaken` index for O(1) space',
             'The only history the check needs is whether the immediately preceding seat is occupied, '
             'which one integer records. Initialised to -2 so index 0 correctly has no left neighbour.'],
            ['Compute the maximum, then compare',
             'More useful than a bare boolean, identical cost, and far easier to test — you can '
             'assert a number rather than probing a predicate.'],
        ],
        steps=[
            '`N <= 0` → true.',
            'Clone the array.',
            'For each index `i` with `row[i] == 0`: check `i == 0 || row[i-1] == 0`, and '
            '`i == n-1 || row[i+1] == 0`.',
            'If both hold, set `row[i] = 1` and increment the count.',
            'Return whether the count is at least N.',
        ]),
    walk=dict(
        intro='`[1,0,0,0,0,0,1,0,0]`. The two things to watch: the scan seeing its own seat at index 2, '
              'and index 8 having no right neighbour.',
        headers=['i', 'row[i]', 'left free?', 'right free?', 'Action', 'Count'],
        rows=[
            ['0', '1', '—', '—', 'occupied, skip', '0'],
            ['1', '0', 'no (index 0 taken)', 'yes', 'skip', '0'],
            ['2', '0', 'yes', 'yes', '**seat**', '1'],
            ['3', '0', 'no (**we just seated 2**)', 'yes', 'skip', '1'],
            ['4', '0', 'yes', 'yes', '**seat**', '2'],
            ['5', '0', 'no', 'no (index 6 taken)', 'skip', '2'],
            ['6', '1', '—', '—', 'occupied, skip', '2'],
            ['7', '0', 'no (index 6 taken)', 'yes', 'skip', '2'],
            ['8', '0', 'yes', '**yes — no right neighbour**', '**seat**', '**3**'],
        ],
        close='Maximum 3, so N=3 is true and N=4 is false, matching the supplied answers. The two rows to '
              'point at are index 3, where the check depends on a seat this scan itself just filled, and '
              'index 8, where the missing right neighbour counts as free. Those are the two bugs this '
              'question exists to catch.'),
    code=[
        ('The greedy scan, plus the constant-space variant', 'Q14_Seating.cs', 'TheatreSeating'),
    ],
    codewalk=[
        ('`(int[])seats.Clone()`',
         'The scan writes `row[i] = 1` so that the check at `i+1` sees it. Doing that to the caller’s '
         'array would make a read-only-looking query destructive. The test asserts `row[2]` is still 0 '
         'afterwards, because this is exactly the kind of thing that passes review and surprises someone '
         'later.'),
        ('`i == 0 || row[i-1] == 0` — short-circuit as the boundary check',
         'The `||` is doing the out-of-bounds handling: at `i == 0` the left is treated as free without '
         'ever indexing `-1`. Same on the right with `i == row.Length - 1`. Writing it this way means '
         'there are no special cases and no separate first/last handling — which is why `[0]` works '
         'with no extra code.'),
        ('Why `row[i] = 1` and not just a counter',
         'The decision has to be visible to the next iteration. A version that counts without marking '
         'would seat people at both `i` and `i+1`, which is the single most common bug here and produces '
         'roughly double the correct answer on an empty row.'),
        ('`lastTaken = -2` in the constant-space version',
         '`leftFree` is `lastTaken < i - 1`. At `i = 0` that needs `lastTaken < -1`, so -1 would be wrong '
         'and -2 is the smallest value that works. An off-by-one in a sentinel, and the reason the two '
         'implementations are cross-checked on 4,000 random rows rather than trusted.'),
        ('Returning the maximum rather than the boolean',
         '`MaxAdditional` is the real function and `CanSeat` is a one-line wrapper. Every test asserts a '
         'number, which localises a failure to the exact row rather than to a yes/no.'),
    ],
    cx=dict(rows=[
        ['`MaxAdditional`', 'O(n)', 'O(n)', 'One pass; the clone is the space'],
        ['`MaxAdditionalNoCopy`', 'O(n)', 'O(1)', 'One pass, one integer of history'],
        ['`CanSeat`', 'O(n)', 'O(1) or O(n)', 'Delegates'],
    ],
        note='**There is an early-exit worth mentioning and not taking.** `CanSeat` could stop as soon as '
             'the count reaches N, which is faster on a true answer and identical on a false one. I '
             'return the maximum instead, because the maximum is the more useful value and the input is a '
             'row of seats — the constant factor is irrelevant. Saying you noticed and chose not to '
             'is better than either doing it silently or missing it.'),
    edges=[
        ['`[0]`', '1. Both neighbours out of bounds. A supplied case, and the boundary test.'],
        ['`[1]`', '0.'],
        ['Empty array', '0, guarded first.'],
        ['Null', '0. State the choice.'],
        ['`N = 0`', 'True without scanning.'],
        ['Negative N', 'True.'],
        ['All free, length 5', '3 — seats at 0, 2, 4.'],
        ['`[1,0,1]`', '0 — a gap of one admits nobody.'],
        ['`[1,0,0,1]`', '0 — a gap of two admits nobody.'],
        ['`[1,0,0,0,1]`', '1 — a gap of three admits exactly one.'],
        ['Already-invalid row `[1,1,0]`', 'Accepted as the starting state; only new placements are '
                                          'constrained.'],
    ],
    fups=[
        dict(q='Prove the greedy is optimal.',
             thinking='The question that actually gets asked, and "it just works" is not an answer. The '
                      'standard tool is an exchange argument.',
             approach='Take any optimal seating that does not use the leftmost available seat `i`, and let '
                      '`j > i` be the first seat it does use. Occupying `i` constrains only `i-1` and '
                      '`i+1`, and `i-1` was already unavailable since `i` was leftmost. So moving that '
                      'person from `j` to `i` keeps the seating valid and frees space to the right rather '
                      'than blocking it. The count is unchanged, so the result is still optimal. Repeat '
                      'until the seating is leftmost-first — therefore leftmost-first achieves the '
                      'optimum.',
             tradeoff='None; it is a proof, not a choice. Being able to give it in three sentences is what '
                      'separates "I remembered this is greedy" from "I know why".',
             t='—', s='—'),
        dict(q='People need k empty seats between them, not 1.',
             thinking='The check generalises from "both neighbours" to "a window", and the boundary logic '
                      'is the part that gets messy.',
             approach='Seat at `i` if no occupied seat lies within distance `k` on either side. With the '
                      '`lastTaken` formulation it is one comparison: `lastTaken < i - k`, plus a forward '
                      'check that the next `k` seats hold nobody. Keeping a **next occupied index** '
                      'alongside `lastTaken`, precomputed in one backward pass, makes the forward check '
                      'O(1) and the whole thing still one pass.',
             tradeoff='Naively the forward check is O(k) per position, so O(nk) overall — fine for '
                      'small k. The precomputed next-occupied array makes it O(n) at the cost of O(n) '
                      'space. The exchange argument still holds, so the greedy is still optimal, which is '
                      'the thing worth confirming rather than assuming.',
             t='O(nk) naive, O(n) with a next-occupied array', s='O(1) or O(n)'),
        dict(q='The row is circular — it is a round table.',
             thinking='Wrapping breaks the exchange argument, because there is no longer a leftmost '
                      'position to anchor it. This is the same structural break as Q3’s circular '
                      'follow-up.',
             approach='With no occupied seats, a circle of n admits `floor(n/2)`, which the linear greedy '
                      'gets wrong on an all-empty row (it would seat both ends, which are adjacent on a '
                      'circle). The standard fix is to case-split on the first position: run the linear '
                      'algorithm once assuming seat 0 is used and once assuming it is not, and take the '
                      'better. If any seat is already occupied, cut the circle there and the problem '
                      'becomes linear with both ends bounded.',
             tradeoff='Two passes instead of one, still O(n). The real point is that the greedy’s '
                      'optimality proof depended on the array having an end, so the circular case needs '
                      'the argument redone rather than the code tweaked — which is exactly the same '
                      'lesson as the obstacle follow-up in Q3.',
             t='O(n)', s='O(1)'),
        dict(q='Return the seat positions, not just the count.',
             thinking='Free — the greedy already knows them.',
             approach='Collect `i` into a list when seating. Note that the positions are not unique: for '
                      '`[0,0,0]` both `{0,2}` and, with a different greedy, other pairs of size 1 '
                      'exist — so the count is unique and the arrangement is not. Say which one you '
                      'return (leftmost-first).',
             tradeoff='O(k) extra space for k seats. The only subtlety is stating that ties exist, which '
                      'matters if a caller is going to compare against an expected arrangement rather '
                      'than an expected count.',
             t='O(n)', s='O(k)'),
    ],
    testing=dict(skills=[
        '**Greedy recognition, and justification** — the exchange argument is the real question.',
        '**Boundary handling** — first and last positions, which is why `[0]` was supplied.',
        '**Making the scan see its own decisions** — the mark-as-you-go bug.',
        '**Not mutating the input.**',
        '**Warm-up discipline** — an easy question done cleanly, with the proof, in ten minutes.',
    ],
        senior='Writes the greedy scan, handles the boundaries, and gets all three supplied cases right.',
        staff='Does that, and: gives the exchange argument unprompted rather than asserting the greedy '
              'works; works on a clone and says why; notes the early exit in `CanSeat` and explains the '
              'choice not to take it; and on the circular follow-up, observes that the **optimality proof '
              'breaks** rather than just that the code needs a modulo. On a question this easy, the '
              'justification is the only place signal can come from.'),
    say=[
        "The algorithm is: scan left to right and take every seat I legally can. A seat is legal if both "
        "neighbours are free, and off the end of the array counts as free — which is why your single-zero "
        "case gives one.",
        "Let me justify the greedy rather than assert it. Suppose an optimal seating skips the leftmost "
        "available seat i and uses some later seat j. Occupying i only constrains i-1 and i+1, and i-1 was "
        "already unavailable, because i was the leftmost. So moving that person from j to i stays valid and "
        "frees space to the right rather than blocking it — the count does not go down. Repeat, and any "
        "optimal solution rewrites into leftmost-first.",
        "Two implementation details. The scan has to see its own decisions: after seating at i, the check "
        "at i+1 must know. I do that by marking a clone of the array — a clone, because a caller should not "
        "find their array modified by what looks like a query.",
        "And the boundaries. Index 0 has no left neighbour, the last index has no right one, and I handle "
        "both with a short-circuit rather than special cases, so there is no separate first-and-last code.",
        "I compute the maximum and then compare against N, rather than returning a bare boolean. Same cost, "
        "more useful, and much easier to test.",
        "I could exit early once the count reaches N. I have not, because the maximum is the more useful "
        "value and the input is a row of seats.",
        "If it were a round table, I would want to redo the proof rather than just add a modulo — the "
        "exchange argument leaned on the array having an end. I would case-split on whether seat zero is "
        "used and take the better of the two runs.",
    ],
    video=dict(title='LinkedIn Coding — Theatre Seating, and Proving a Greedy', mins=11,
               objective='Use the easiest question on the page to practise the thing easy questions are '
                         'really for: justifying the algorithm and getting the boundaries exactly right.',
               beats=[('0:00', 'The question and the three supplied arrays'),
                      ('1:10', 'The greedy, in one sentence'),
                      ('2:20', 'The exchange argument — why leftmost-first is optimal'),
                      ('4:10', 'The scan must see its own decisions'),
                      ('5:30', 'Boundaries, and why [0] is 1'),
                      ('6:40', 'The C# implementation'),
                      ('7:50', 'Walking the supplied row to 3'),
                      ('9:00', 'Circular: the proof breaks, not just the code'),
                      ('10:10', 'How to say it')]),
))

# ============================================================ Q15
QUESTIONS.append(dict(
    id='q15', n=15, name='Task manager — dependency graph',
    tags=['GRAPH', 'DFS', 'DESIGN', 'DATA STRUCTURE DESIGN', 'QUEUE'],
    diff='HARD', prio='HIGH',
    verdict_short='InterviewDB + getBuildOrder reported + 261 on the list',
    prio_why=(
        '**"Implement getBuildOrder() given getDependencies()"** is independently reported in the existing '
        'research — the same problem, different wording. `261 Graph Valid Tree` is on the supplied '
        'list and is cycle detection, and `210 Course Schedule II` is already worked in the coding page. '
        'High priority, and it is one of the two questions on the page where the interesting content is '
        '**API design** rather than algorithm.'),
    idb=(
        'Given:\n\n'
        'interface Task {\n'
        '    String getId();\n'
        '    List<Task> getSubTasks();\n'
        '}\n\n'
        'A task depends on completion of all subtasks.\n\n'
        'Implement:\n\n'
        'addTask(Task t)\n\n'
        'Throws if adding the task creates a cycle.\n\n'
        'pollNextTask()\n\n'
        'Returns the next executable task whose dependencies are completed.'),
    dd=dict(elsewhere=[
        ('idb', 'Supplied with the interface and both method contracts. **The contract has a hole in it** '
                '— there is no way to signal that a task has finished, so nothing can ever become '
                'executable after the first batch. That is the most important thing to notice.'),
        ('reported', '**"Implement getBuildOrder() given getDependencies()"** — independently reported '
                     'in the existing research. Same dependency graph, asked as a package build order.'),
        ('reported', '`210 Course Schedule II` is already a worked problem in the coding page and is the '
                     'batch version of this.'),
        ('lc', '261 Graph Valid Tree is on the supplied list — undirected cycle detection. This needs '
               'the **directed** version, where a cycle is a back edge to a node still on the current '
               'path. Different algorithm, same word.'),
    ],
        verdict='**InterviewDB reported and independently reported under a different name.** High '
                'confidence in the problem; the incremental `addTask`/`pollNextTask` framing is what '
                'InterviewDB adds over the batch topological sort.'),
    ambiguity=(
        '**The interface cannot work as given, and saying so is the question.**\n\n'
        '`pollNextTask()` returns a task whose dependencies are complete. Nothing in the interface ever '
        'says a task *became* complete. So the first call returns a leaf, and every subsequent call '
        'returns either the same leaf forever or nothing — the system cannot make progress. A '
        '`CompleteTask(id)` (or a callback, or having `pollNextTask` mark the task complete on return) is '
        'required, and which one you pick changes the semantics.\n\n'
        'I add `CompleteTask(string id)` and say why. Two smaller gaps follow from it: does '
        '`pollNextTask` hand the same task out twice if it is called twice before completion (I say no, '
        'tracked by an issued set), and what happens if a worker takes a task and dies (I add '
        '`RequeueTask`, because without it the task is lost forever).\n\n'
        'Also: **what does `addTask` do if the task is already registered with different subtasks?** I '
        'union the edges, and refuse if the task has already been issued — see the follow-up, because '
        'this is where the real bug was.'),
    understand=dict(
        what='A work queue that understands dependencies. Tasks arrive with their subtasks, a task cannot '
             'run until all its subtasks have, and a dependency that would make progress impossible must '
             'be rejected at the moment it is introduced.',
        compute='Not a value — a component with three or four operations. The interesting parts are '
                'cycle detection on insert, and the atomicity of a rejected insert.',
        constraints=[
            'Cycle detection happens on **`addTask`**, not at execution time. That is the design '
            'difference from a batch topological sort and it is what the question is about.',
            'A rejected `addTask` must leave the manager exactly as it was. Half-applying a change and '
            'then throwing is worse than not validating.',
            'Subtasks arrive as objects, so the whole reachable closure gets registered, not just the top '
            'task.',
            'A task reachable by two paths is one task, registered once.',
        ],
        assume=[
            ['`CompleteTask(id)` exists, because the interface as given cannot make progress.',
             'Without it, `pollNextTask` returns the first leaf and nothing ever unblocks. **This is the '
             'clarification to raise before writing any code.**'],
            ['`pollNextTask` issues each task at most once.',
             'Otherwise two workers polling concurrently both run the same task. Tracked with an issued '
             'set; a dropped task needs an explicit `RequeueTask`.'],
            ['Ids are unique and identify a task; the object is incidental.',
             'Two `Task` objects with the same id are the same task. That is what lets a cycle be closed '
             'across two `addTask` calls with different objects.'],
            ['Re-adding a registered task unions its dependencies.',
             'The alternative — first registration wins — silently ignores what the caller '
             'asked for. Unioning is the defensible choice, and it is what exposed a real bug; see the '
             'follow-up.'],
        ]),
    examples=[
        ('Chain', 'deploy → build → compile', 'poll gives compile; after CompleteTask(compile), build; then deploy'),
        ('Diamond', 'top → {a, b}', 'a and b both runnable; top only after **both** complete'),
        ('Cycle', 'x → y and y → x', 'addTask throws; manager still holds 0 tasks'),
        ('Cross-batch', 'add p→q, then add q→p', '**throws** — the cycle is only closed by combining the two calls'),
        ('Shared', 'root → {l, r}, both l and r → shared', 'shared registered once; completing it unblocks both'),
        ('Self', 's → s', 'throws'),
    ],
    examples_note='The cross-batch row is the one that found a real bug in my first implementation — '
                  'see the code walkthrough. Every row above is a test, including the assertions that the '
                  'manager is **unchanged** after each throw, which is the part that is easy to get wrong '
                  'and impossible to notice without testing for it.',
    observation=(
        'Three observations, and only the first is the algorithm.\n\n'
        '**One: it is a dependency graph, so readiness is an in-degree count.** A task is runnable when '
        'the number of its subtasks that are not yet complete reaches zero. Keep that count per task, '
        'keep a reverse map from each subtask to the tasks waiting on it, and completing a task is a '
        'decrement of each waiter — O(1) per edge, and any waiter that hits zero goes on the ready '
        'queue. That is Kahn’s algorithm, run incrementally instead of in a batch.\n\n'
        '**Two: cycle detection is on insert, which is a different problem from topological sorting.** A '
        'batch topological sort detects a cycle by *failing to sort* — if fewer than n tasks come '
        'out, there was a cycle. That does not work here, because the graph is built incrementally and '
        'you must reject at the moment the bad edge is added. So it needs an explicit directed cycle '
        'check: three-colour DFS, where grey means "on the current path" and meeting grey is a back edge.\n\n'
        '**Three, and this is the staff-level part: the insert must be atomic.** Check the whole merged '
        'graph first, commit second. It is tempting to register as you walk and unwind on failure, and '
        'unwinding is exactly where the bug lives — a partially-registered rejected task leaves the '
        'manager in a state no caller can reason about. Collect into locals, validate, and only then touch '
        'the fields. Then nothing after the validation can fail, so there is nothing to unwind.\n\n'
        'And the reason the cycle check must run over the **union** of the existing and new edges rather '
        'than the new ones alone: a cycle can be closed by an edge whose other half was added in an '
        'earlier call. That is not hypothetical — my first implementation overwrote the existing '
        'edges instead of unioning them, and that exact case passed silently.'),
    brute=dict(
        how='Store the tasks. On `pollNextTask`, run a full topological sort over the whole graph and '
            'return the first task whose dependencies are all complete. Detect cycles then, by the sort '
            'failing.',
        cx='`addTask` O(1), `pollNextTask` O(V + E). Space O(V + E).',
        why_not='Two problems, and the second is the real one. The performance objection is that '
                '`pollNextTask` is the hot operation — called once per task — so an O(V+E) poll '
                'makes the whole run O(V·(V+E)). The **correctness** objection is that the '
                'specification says `addTask` throws on a cycle, and deferring detection to poll time '
                'means the bad edge has already been accepted: the caller gets no error at the point where '
                'they could still do something about it, and by the time poll fails you cannot tell which '
                'of the accepted tasks caused it.'),
    optimal=dict(pipeline=[
        ('INPUT', '`AddTask(ITask)`, `PollNextTask()`, `CompleteTask(id)`'),
        ('TRANSFORMATION', 'The task closure is walked into id-keyed nodes and edges; readiness becomes an '
                           'outstanding-dependency count'),
        ('DATA STRUCTURE', 'Five dictionaries and a queue: tasks, dependsOn, blocks (reverse), '
                           'outstanding, plus `_ready`, `_queued`, `_issued`, `_completed`'),
        ('ALGORITHM', 'Collect → cycle-check the merged graph → commit. Completion decrements '
                      'waiters and enqueues those reaching zero.'),
        ('OUTPUT', 'A runnable task, or null; `CycleException` on a cycle'),
    ],
        why=[
            ['`_dependsOn` and `_blocks`, both directions',
             '`_dependsOn` is needed for the cycle check; `_blocks` is needed so completion is O(waiters) '
             'rather than a scan of every task. Keeping both is the standard cost of incremental '
             'readiness.'],
            ['`_outstanding` count per task',
             'The in-degree, restricted to incomplete dependencies. A set of incomplete dependencies would '
             'also work and costs more memory for no extra capability.'],
            ['`Queue` plus a `_queued` set',
             'The queue gives FIFO fairness among ready tasks. The set stops a task being queued twice, '
             'which becomes possible once edges can be added to an already-ready task.'],
            ['`_issued` separate from `_completed`',
             'A task handed to a worker is neither ready nor done. Without the distinction, two polls '
             'return the same task and two workers run it.'],
            ['Three-colour DFS for the cycle check',
             'Grey = on the current path, black = finished and clean. Re-entering a **black** node must not '
             'be a failure — that is a diamond, not a cycle — and conflating the two is the '
             'classic error here.'],
        ],
        steps=[
            '**Phase 1** — walk the new task’s closure into local `newTasks` and `newEdges`. '
            'Touch no fields.',
            '**Phase 2** — build `merged` as the **union** of existing and new edges; run the '
            'three-colour DFS from the new task’s id; throw `CycleException` if a back edge is found.',
            'Also refuse if a new edge would be added to a task already issued or completed — '
            'ambiguous, so reject rather than guess.',
            '**Phase 3** — commit. Register unseen tasks, then add each new edge, updating `_blocks` '
            'and `_outstanding`.',
            'Mark ready any task whose outstanding count is zero.',
            '`PollNextTask`: pop from `_ready`, skipping completed, still-blocked, or already-issued '
            'entries.',
            '`CompleteTask`: idempotent; decrement each waiter and mark ready at zero.',
        ]),
    walk=dict(
        intro='The cross-batch cycle, which is the case that matters. `p` depends on `q` is added first; '
              'then a second call says `q` depends on `p`.',
        headers=['Step', 'newEdges', 'merged (the union)', 'DFS from', 'Result'],
        rows=[
            ['AddTask(p→q)', 'p:[q], q:[]', 'p:[q], q:[]', 'p', 'no cycle → commit; 2 tasks'],
            ['AddTask(q→p)', 'q:[p], p:[]', '', '', 'phase 1 collects the new material'],
            ['union', '', 'p:[**q**], q:[**p**]', '', 'both edges survive'],
            ['DFS', '', '', 'q → grey', 'visit p'],
            ['', '', '', 'p → grey', 'p depends on q'],
            ['', '', '', 'q is **grey**', '**back edge → throw**'],
            ['after', '', 'p:[q], q:[]', '', 'manager unchanged — still 2 tasks, 0 edges added'],
        ],
        close='The bug in my first version was in the union row. It built `merged` by copying the existing '
              'edges and then **assigning** the new ones, so `p:[q]` was overwritten by `p:[]` and the DFS '
              'from `q` found `q → p` and stopped. No cycle reported, the edge accepted, and the manager '
              'left in a state where `p` and `q` each wait on the other forever — detected only when '
              'nothing ever became runnable. One character of difference between `merged[k] = new` and a '
              'union, and it is the reason that test exists.'),
    code=[
        ('The interface and the exception', 'Q15_TaskManager.cs', 'ITask'),
        ('The manager', 'Q15_TaskManager.cs', 'TaskManager'),
    ],
    codewalk=[
        ('The three phases, and why the order is the design',
         'Phase 1 collects into locals. Phase 2 validates. Phase 3 commits, and **nothing in phase 3 can '
         'fail** — it is only dictionary writes. So a rejected `addTask` cannot leave the manager '
         'half-updated, and there is no unwind path to get wrong. The test asserts `TaskCount` is '
         'unchanged after every throw, because this property is invisible otherwise.'),
        ('The union in phase 2 — where the real bug was',
         '`foreach (string d in kv.Value) if (!deps.Contains(d)) deps.Add(d);` rather than '
         '`merged[kv.Key] = kv.Value`. Assignment dropped an existing task’s original edges, so a '
         'cycle closed across two calls went undetected. **This was found by a test, not by reading.** '
         'The comment in the code says so, because a future reader will otherwise be tempted to simplify '
         'it back.'),
        ('Refusing a new dependency on an issued task',
         'If a task has already been handed to a worker and someone adds a dependency to it, should it '
         're-run? There is no good answer, so it throws `InvalidOperationException`. The check sits in '
         'phase 2, before any commit, so the refusal is atomic like the cycle rejection. Guessing either '
         'way here would be worse than refusing.'),
        ('`MarkReady` and the `_queued` set',
         'A task can reach zero outstanding dependencies more than once — add an edge, complete it, '
         'add another. Without `_queued`, it would sit in `_ready` twice and `PollNextTask` would hand it '
         'out twice. The `_issued` check inside `MarkReady` covers the other direction.'),
        ('Why `PollNextTask` re-verifies',
         'It skips entries that are completed, still blocked, or already issued. Entries in `_ready` can '
         'go stale: a task queued as ready can gain a dependency before it is polled. Re-checking '
         '`_outstanding[id] > 0` at the point of use is cheaper and more robust than trying to remove it '
         'from the middle of the queue.'),
        ('`CompleteTask` is idempotent',
         '`if (!_completed.Add(id)) return;` — a retried completion, which any distributed worker '
         'will eventually send, must not decrement the waiters twice. Double-decrementing would drive '
         '`_outstanding` negative and a task would become ready before its dependencies finished: silent, '
         'and catastrophic.'),
        ('`Collect` is iterative on purpose',
         'An explicit `Stack<ITask>` rather than recursion, because dependency chains are exactly the '
         'shape that gets deep. Note that `FindCycleFrom` **is** recursive, which is the standard shape '
         'for three-colour DFS and is the one place a very deep graph could still overflow — worth '
         'naming rather than claiming the whole class is stack-safe.'),
        ('`FindCycleFrom` returns the cycle, not a bool',
         '`path.IndexOf(path[^1])` trims the trailing tail so the exception names the actual loop. "There '
         'is a cycle" is not actionable; "a → b → c → a" is. It costs a list and it is what '
         'makes the error message worth reading.'),
    ],
    cx=dict(rows=[
        ['`AddTask`', 'O(Vₙ + Eₘ)', 'O(V + E)',
         'Collects the new closure, then DFS over the merged graph'],
        ['`PollNextTask`', 'O(1) amortised', 'O(1)', 'Pops until a valid entry; each is skipped once'],
        ['`CompleteTask`', 'O(waiters)', 'O(1)', 'One decrement per task blocked on it'],
        ['whole run', 'O(V + E) total for polls and completions', 'O(V + E)',
         'Each edge relaxed exactly once across the run'],
        ['`RequeueTask`', 'O(1)', 'O(1)', 'Clears the issued flag and re-queues'],
    ],
        note='**The cycle check dominates `AddTask` and it is not free.** It is O(V + E) over the merged '
             'graph each time, so adding n tasks one at a time is O(n(V+E)) overall — worse than the '
             'single O(V+E) of a batch topological sort. That is the price of rejecting at insert time, '
             'and it is the right price because the alternative is accepting a cycle you cannot '
             'attribute. Restricting the DFS to the component reachable from the new task, which is what '
             'the code does, keeps it proportional to the affected subgraph rather than the whole '
             'manager — worth saying, because it is the difference between acceptable and not.'),
    edges=[
        ['Null task', 'Throws `ArgumentNullException`.'],
        ['Null id', 'Throws during `Collect`, before any commit.'],
        ['Self-dependency', '`CycleException`. Caught by the grey check with no special case.'],
        ['Cycle within one `addTask`', 'Caught; nothing registered.'],
        ['**Cycle across two `addTask` calls**', 'Caught, because the check runs over the union. The bug '
                                                'case.'],
        ['Diamond (two paths to one task)', 'Registered once, and completing it unblocks both parents. '
                                            'Must **not** be reported as a cycle — that is the '
                                            'grey-versus-black distinction.'],
        ['`pollNextTask` with nothing runnable', 'Returns null. Note that null does not distinguish '
                                                '"blocked" from "finished"; a caller needing that should '
                                                'check `TaskCount` against completed.'],
        ['Polling the same task twice', 'Issued once. `RequeueTask` is the way back.'],
        ['`CompleteTask` on an unknown id', 'Throws `KeyNotFoundException`.'],
        ['`CompleteTask` twice', 'Idempotent — the second is a no-op, and must be.'],
        ['Adding a dependency to an issued task', 'Refused, rather than guessed at.'],
        ['A very deep chain', '`Collect` is iterative and safe; the recursive cycle check is the remaining '
                             'depth risk.'],
    ],
    fups=[
        dict(q='Several workers poll concurrently. Make it safe.',
             thinking='Almost every field is mutated by both `pollNextTask` and `completeTask`, so the '
                      'shared state is everything. Worth being concrete about what the race actually '
                      'produces.',
             approach='One lock around each public method is the right first answer: the critical sections '
                      'are dictionary operations, so they are short. The `_issued` set is what makes '
                      'concurrent polling correct — without it two workers get the same task.\n\n'
                      'For throughput, `_ready` could be a `BlockingCollection` so workers block instead '
                      'of polling and getting null, which also removes a busy-wait loop from every '
                      'caller.',
             tradeoff='A single lock serialises polls, which is unlikely to matter because the tasks '
                      'themselves are the expensive part. Finer-grained locking is genuinely hard here: '
                      'the invariant spans four dictionaries, so per-task locks would need a consistent '
                      'acquisition order to avoid deadlock, and the ready-queue transition would still '
                      'need to be atomic with the outstanding-count decrement. I would take the single '
                      'lock and measure.',
             t='unchanged plus lock acquisition', s='unchanged'),
        dict(q='A worker takes a task and dies. What happens?',
             thinking='With `_issued` and nothing else, the task is lost permanently and every task '
                      'downstream of it waits forever. Worth raising unprompted, because it is the '
                      'failure mode that turns a correct component into a stuck one.',
             approach='`RequeueTask(id)` clears the issued flag and re-queues if the dependencies are '
                      'still satisfied. To detect the death rather than be told about it, issue a lease '
                      'with a deadline and requeue automatically when it expires — which needs a '
                      'timer, and that timer is Q7.',
             tradeoff='Explicit requeue is simple and needs a cooperative worker or a supervisor. Leases '
                      'are automatic and introduce **at-least-once** execution: a slow worker can have '
                      'its lease expire while still running, so the task runs twice. That forces tasks to '
                      'be idempotent, which is a requirement on the caller rather than on this class, and '
                      'it should be stated as such rather than hidden.',
             code=[('Requeue', 'Q15_TaskManager.cs', 'TaskManager|public void RequeueTask')],
             t='O(1)', s='O(1) plus a timer per lease'),
        dict(q='A task fails. Should its dependents run?',
             thinking='The specification says nothing about failure, which means the contract is '
                      'incomplete in a second place. Both answers are defensible and the choice belongs '
                      'to the caller.',
             approach='`FailTask(id)` with a policy. **Abort**: mark the whole dependent subtree '
                      'unrunnable and report it, which is what a build system does — a failed compile '
                      'must not produce a deploy. **Retry**: requeue with a backoff and an attempt limit, '
                      'then abort. **Continue**: treat failure as completion, which is almost always '
                      'wrong and occasionally right for optional work.',
             tradeoff='Abort is the safe default and it needs a reverse traversal to find everything '
                      'downstream, which `_blocks` already supports. Retry needs the attempt count and a '
                      'timer. I would implement abort, expose the policy as a parameter, and say clearly '
                      'that treating a failure as a completion is the one option I would not offer '
                      'without the caller asking for it by name.',
             t='O(dependent subtree) for abort', s='O(1) extra'),
        dict(q='Why detect the cycle on insert rather than at execution time?',
             thinking='The question is really "do you know what you bought". It is not free, so the '
                      'justification matters.',
             approach='Insert-time detection gives an error **at the point where the caller can act on '
                      'it** — they are holding the task that caused it, and the exception can name '
                      'the loop. Execution-time detection means the bad edge was accepted, so the failure '
                      'surfaces later, in a different stack, attributed to nothing in particular; and by '
                      'then you cannot tell which of the accepted tasks was at fault.',
             tradeoff='The cost is O(V + E) per add instead of once, making n adds O(n(V+E)) rather than '
                      'O(V+E). Restricting the DFS to the reachable component keeps that proportional to '
                      'the affected subgraph. If adds were extremely hot and cycles genuinely impossible '
                      'by construction, batching the validation would be defensible — but the '
                      'specification says `addTask` throws, so it is not an option here.',
             t='O(V + E) per add, versus O(V + E) once for a batch', s='O(V + E)'),
        dict(q='Priorities: some ready tasks matter more than others.',
             thinking='A small change with one non-obvious consequence.',
             approach='Replace `_ready` with a priority queue keyed on priority. Readiness logic is '
                      'untouched — only the order among already-ready tasks changes.',
             tradeoff='O(log n) instead of O(1) per poll, which is irrelevant next to running the task. '
                      'The real consequence is **starvation**: a steady stream of high-priority tasks can '
                      'keep a low-priority one waiting forever. Ageing — raising effective priority '
                      'with waiting time — is the standard fix, and mentioning starvation unprompted '
                      'is the signal here, because the data-structure swap is trivial and the fairness '
                      'problem is not.',
             t='O(log n) per poll', s='unchanged'),
    ],
    testing=dict(skills=[
        '**Spotting an incomplete contract** — the missing completion signal. The primary thing being '
        'tested.',
        '**Directed cycle detection** — and specifically the grey-versus-black distinction, so a '
        'diamond is not mistaken for a cycle.',
        '**Atomicity** — validate then commit, so a rejection changes nothing.',
        '**Incremental versus batch** — Kahn’s algorithm run online, and knowing what that costs.',
        '**Lifecycle thinking** — issued, completed, failed, requeued. The states the interface does '
        'not mention.',
        '**Concurrency** — identifying that the invariant spans four dictionaries.',
    ],
        senior='Builds the dependency graph, detects cycles with a DFS on insert, tracks in-degrees, and '
               'produces a working poll/complete cycle.',
        staff='Does that, and: raises the missing completion signal **before writing code**; structures '
              '`addTask` as collect-validate-commit and says why, rather than unwinding on failure; runs '
              'the cycle check over the **union** of old and new edges and can say what breaks '
              'otherwise; distinguishes issued from completed and asks what happens when a worker dies; '
              'refuses the ambiguous case (a new dependency on an issued task) rather than guessing; and '
              'justifies insert-time detection with what it costs. Noticing that the given interface '
              'cannot make progress is the single highest-value observation available on this question.'),
    say=[
        "Before I write anything — the interface as given cannot make progress. pollNextTask returns a task "
        "whose dependencies are complete, but nothing ever says a task became complete. So the first call "
        "returns a leaf and then either the same leaf forever or nothing. I need a completion signal. I "
        "will add CompleteTask by id; the alternative is pollNextTask marking the task complete when it "
        "returns, which loses the ability to fail.",
        "With that, the structure is Kahn's algorithm run incrementally. Each task has a count of "
        "dependencies not yet complete, and I keep the reverse map too, so completing a task is a decrement "
        "of everything waiting on it. Anything hitting zero goes on the ready queue.",
        "Cycle detection is the interesting half, because you want it on add rather than at execution. A "
        "batch topological sort detects cycles by failing to sort, and I cannot do that here — I have to "
        "reject the edge at the moment it arrives. So it is a three-colour DFS: grey means on the current "
        "path, and hitting grey is a back edge. Hitting black is fine, that is a diamond.",
        "The part I would emphasise is atomicity. I collect the new material into locals, validate, and "
        "only then commit — and nothing in the commit can fail, it is just dictionary writes. If I "
        "registered as I walked and unwound on failure, the unwind is where the bug would be, and a "
        "half-registered rejected task leaves the manager in a state nobody can reason about.",
        "One thing I got wrong first time and want to flag. The cycle check has to run over the union of "
        "the existing edges and the new ones. I originally overwrote instead of unioning, and a cycle "
        "closed across two separate addTask calls went undetected — add p depends on q, then add q depends "
        "on p, and it accepted it. A test caught it, not reading the code.",
        "I also separate issued from completed, so two polls do not hand out the same task. Which raises "
        "the question of what happens if a worker takes a task and dies — without something, that task and "
        "everything downstream waits forever. I would add an explicit requeue, and if you want it "
        "automatic, a lease with a deadline. That makes execution at-least-once, so tasks have to be "
        "idempotent, and that is a requirement on the caller I would state rather than bury.",
        "And one case I deliberately refuse rather than guess: adding a dependency to a task that has "
        "already been handed out. Should it re-run? There is no good answer, so it throws.",
    ],
    video=dict(title='LinkedIn Coding — Task Manager with Cycle Detection', mins=18,
               objective='Notice the hole in the contract first, then build the incremental Kahn plus '
                         'insert-time cycle check, and use a real bug to show why the union matters.',
               beats=[('0:00', 'The question and the interface'),
                      ('1:20', 'The contract cannot make progress — the missing signal'),
                      ('3:00', 'Readiness as an in-degree count'),
                      ('4:40', 'Why cycle detection on insert is a different problem'),
                      ('6:10', 'Three-colour DFS, and grey versus black'),
                      ('8:00', 'Collect, validate, commit — and why not unwind'),
                      ('9:40', 'The union bug, and the test that found it'),
                      ('11:30', 'The C# implementation'),
                      ('13:30', 'Issued versus completed, and the dying worker'),
                      ('15:00', 'Refusing the ambiguous case'),
                      ('16:10', 'What insert-time detection costs'),
                      ('17:20', 'How to say it')]),
))

# ============================================================ Q16
QUESTIONS.append(dict(
    id='q16', n=16, name='Tournament tree — second smallest',
    tags=['TREE', 'DFS'],
    diff='MEDIUM', prio='LOWER',
    verdict_short='InterviewDB only; but it is LeetCode 671, which is public',
    prio_why=(
        'Nothing else in this workspace reports it, and none of the tree problems in the supplied number '
        'list is this one. But it **is** a public LeetCode problem — `671 Second Minimum Node In a '
        'Binary Tree` defines exactly this tree — so it is cheap to practise. Lower priority on '
        'evidence; worth twenty minutes because the insight is a genuinely nice piece of reasoning and it '
        'is the kind of thing that turns up as a phone screen.'),
    idb=(
        'A tournament tree is a binary tree where every parent contains the minimum of its two children.\n\n'
        'Leaves have unique values.\n\n'
        'Find the second smallest value.\n\n'
        'Explain why the second smallest must appear among the nodes that lost directly to the minimum.'),
    dd=dict(elsewhere=[
        ('idb', 'The statement **tells you the insight** — "explain why the second smallest must '
                'appear among the nodes that lost directly to the minimum". So the question is not to find '
                'the trick but to *justify* it, which changes what a good answer looks like.'),
        ('inference', 'Not reported elsewhere in this workspace for LinkedIn.'),
        ('lc', '**671 Second Minimum Node In a Binary Tree** defines the identical structure: '
               '`root.val = min(left.val, right.val)`. It is rated **Easy** only because LeetCode accepts '
               'an O(n) scan of every node. This question wants the O(h) walk, which is the whole point, '
               'and 671 is not on the supplied list.'),
    ],
        verdict='**InterviewDB reported. Not corroborated for LinkedIn**, but the problem is public and '
                'the statement is unambiguous, so there is nothing to recover or guess at.'),
    understand=dict(
        what='A knockout tournament, stored as a tree. Every internal node holds the winner of the match '
             'between its two children, and winning means being smaller. The overall winner is at the '
             'root. Who came second?',
        compute='The second smallest **leaf** value. Equivalently, the second smallest distinct value in '
                'the tree — they are the same, because every internal value is a copy of some leaf '
                'value.',
        constraints=[
            'Leaf values are **unique**, which is what makes the winner’s path unambiguous.',
            'Every internal node holds the minimum of its children, so the root is the global minimum.',
            'At least two leaves are needed for an answer to exist.',
            'The tree need not be perfect, though a tournament usually is.',
        ],
        assume=[
            ['Internal nodes have two children; leaves have none.',
             'A single-child internal node would break "minimum of its two children". The code guards '
             'against it anyway, because a malformed tree should not produce a plausible wrong answer.'],
            ['Leaf values are unique, as stated.',
             'This is load-bearing. With duplicate leaves, two children could both equal the parent and '
             'the winner’s path would fork — the walk-down approach would have to branch, or you '
             'fall back to O(n).'],
            ['"Second smallest" means the runner-up leaf, not the second smallest node.',
             'Every internal value duplicates a leaf value, so the second smallest **distinct** value in '
             'the whole tree equals the second smallest leaf. Worth confirming, because "second smallest '
             'node" could be read as the minimum again.'],
            ['At least two leaves.',
             'One leaf has no runner-up. Throwing is more honest than returning a sentinel that could be a '
             'real value.'],
        ]),
    examples=[
        ('Tree', 'root 2; left subtree 2 over (2, 5); right subtree 7 over (7, 9)', ''),
        ('', 'leaves are 2, 5, 7, 9', 'answer **5**'),
        ('Mine', 'root 1; left 1 over (1, 50); right 3 over (3, 4)', 'answer **3** — the runner-up is on the far side'),
        ('Mine', 'root 4 with leaves 4 and 9', 'answer 9 — two leaves only'),
        ('Mine', 'a single leaf', 'throws — no runner-up exists'),
        ('Check', '500 random tournaments of 2–32 leaves', 'matches the second element of the sorted leaves'),
    ],
    examples_note='The second row is the one that matters for understanding: the runner-up is 3, sitting '
                  'at depth 1 on the opposite side of the tree from the winner, and 50 is a leaf that lost '
                  'to the winner directly and is **not** the answer. Both facts follow from the same rule. '
                  'The implementation is cross-checked against sorting the leaves on 500 randomly '
                  'generated tournaments.',
    observation=(
        'The statement asks you to justify the insight, so here is the justification, which is the answer.\n\n'
        'Call the minimum `m`. Take any leaf `x` other than `m`. Because `m` reached the root, `m` won '
        'every match on its path. Now trace `x` upward: it keeps winning until it meets the path of `m`, '
        'and at that point it loses — either directly to `m`, or to something that itself lost to '
        '`m` further up.\n\n'
        'If `x` lost directly to `m`, it is a candidate. If `x` lost to some other value `y` first, then '
        '`y < x`, and `y` went on to lose to `m`. So `y` is smaller than `x` and is *also* not the '
        'minimum — which means `x` is at best **third**. Therefore the second smallest can only be a '
        'value that faced `m` directly.\n\n'
        'That gives the algorithm: walk from the root down the winner’s path, and at each step the '
        'sibling is one of the values that lost to `m`. There are exactly `h` of them, so the answer is '
        '`min` over the h siblings — O(h) time, O(1) space. On a perfect tournament of n leaves that '
        'is O(log n), against O(n) for scanning every node.\n\n'
        'Two details that make the walk work. The winner’s path is identifiable because the parent '
        'equals exactly one child — **unique leaves is what guarantees "exactly"**, and it is the '
        'reason that constraint is in the statement. And the siblings are exactly the losers, because a '
        'match is a parent with two children and the one that did not become the parent lost it.\n\n'
        'The reason LeetCode rates its version Easy is that it accepts an O(n) traversal looking for the '
        'smallest value greater than the root. Same answer, and it throws away the structure — which '
        'is precisely what this statement is asking you not to do.'),
    brute=dict(
        how='Traverse every node, collect the values, and return the second smallest distinct one. Or '
            'collect all the leaves and sort them.',
        cx='O(n) traversal, or O(n log n) with a sort. O(n) space for the collection, or O(1) if you track '
            'the best two as you go.',
        why_not='It is correct, it is what LeetCode 671 accepts, and it is worth stating as the baseline. '
                'It is also the answer that ignores the one thing you were told about the input. The tree '
                'is not an arbitrary bag of numbers — it is the record of a tournament, and that '
                'record already contains the answer along a single path. Scanning n nodes to find '
                'something that h comparisons will give you is the difference between using the structure '
                'and merely visiting it. On a tournament of a million players that is 20 comparisons '
                'against a million.'),
    optimal=dict(pipeline=[
        ('INPUT', 'The root of a tournament tree'),
        ('TRANSFORMATION', 'The winner’s path from root to leaf is identified by following the child '
                           'whose value equals its parent'),
        ('DATA STRUCTURE', 'None — one running minimum and one pointer'),
        ('ALGORITHM', 'Walk down the winner’s path; at each step take the minimum of the sibling '
                      'values'),
        ('OUTPUT', 'The smallest value that lost directly to the minimum'),
    ],
        why=[
            ['No data structure at all',
             'Worth saying. The answer is a walk with two variables, and reaching for a heap or a list is '
             'the reflex to resist.'],
            ['Following the child equal to the parent',
             'The parent is the minimum of its children, so it equals one of them. Unique leaves means '
             'exactly one — so the path is well defined and needs no search.'],
            ['`best` as a running minimum over the siblings',
             'There are h candidates and only the smallest matters, so nothing needs storing.'],
            ['Iterative rather than recursive',
             'It is a single path, so there is no branching to recurse over. A `while` loop is both '
             'shorter and immune to stack depth on a degenerate tree.'],
        ],
        steps=[
            'Reject a null root, and reject a lone leaf — no runner-up exists.',
            'Start at the root with `best = int.MaxValue`.',
            'While the current node has children: identify which child equals the current value — '
            'that is the winner; the other is the loser.',
            '`best = min(best, loser.Value)`.',
            'Move to the winner and repeat.',
            'Return `best`.',
        ]),
    walk=dict(
        intro='The example tree. Root 2; its left child is 2 over leaves (2, 5); its right child is 7 over '
              'leaves (7, 9).',
        headers=['At', 'Value', 'Winner child', 'Loser child', 'best'],
        rows=[
            ['root', '2', 'left (2)', 'right (**7**)', 'min(∞, 7) = 7'],
            ['left child', '2', 'left leaf (2)', 'right leaf (**5**)', 'min(7, 5) = **5**'],
            ['leaf', '2', '— (no children)', '—', 'stop'],
            ['result', '', '', '', '**5**'],
        ],
        close='Two comparisons for a four-leaf tournament, and the answer is 5. The nodes never visited '
              'are leaf 9 and the internal node holding 7 — and 9 can be skipped safely precisely '
              'because it lost to 7, which lost to 2, so 9 is at best third. That is the argument doing '
              'work rather than sitting in a comment.'),
    code=[
        ('The walk', 'Q16_Tournament.cs', 'TournamentTree'),
    ],
    codewalk=[
        ('`cur.Left.Value == cur.Value` picks the winner',
         'The parent holds the minimum of its children, so it equals one of them. Because leaves are '
         'unique, no two internal nodes can carry the same value from different leaves, so exactly one '
         'child matches and the path never forks. **If leaves could repeat, this line would silently pick '
         'the left one** and the walk could follow the wrong path — which is why the uniqueness '
         'constraint is in the statement and worth repeating back.'),
        ('`while (cur.Left != null || cur.Right != null)`',
         'Either-or rather than both, deliberately. A well-formed tournament node has two children, but a '
         'malformed one might have one, and this condition still terminates rather than dereferencing '
         'null. The `if (loser != null)` inside then skips the missing sibling instead of crashing.'),
        ('`best` starts at `int.MaxValue`',
         'And is guaranteed to be overwritten, because the guard has already established that at least '
         'one match exists. Without that guard, returning `int.MaxValue` from a single-leaf tree would be '
         'a wrong answer disguised as a real one — which is why the throw is better than a sentinel.'),
        ('Why this is O(h) and not O(n)',
         'The loop advances to one child per iteration and never branches, so it touches exactly one node '
         'per level. Every other node in the tree is skipped, and the justification for skipping them is '
         'the argument in the observation — the code is short precisely because the reasoning was '
         'done first.'),
        ('Throwing for a single leaf',
         '`InvalidOperationException` rather than returning `int.MaxValue` or -1. A sentinel cannot be '
         'distinguished from a real value, and for a function whose whole job is to return a value, '
         '"there is no answer" is genuinely exceptional.'),
    ],
    cx=dict(rows=[
        ['`SecondSmallest`', 'O(h)', 'O(1)', 'One node per level, two variables'],
        ['on a perfect tournament', 'O(log n)', 'O(1)', 'h = log₂(n) for n leaves'],
        ['brute-force scan', 'O(n)', 'O(1)', 'Every node visited — the baseline to beat'],
    ],
        note='**h, not log n, is the honest bound.** The statement does not promise a balanced tree, and a '
             'degenerate one has h = n, at which point the walk is no better than the scan. For a real '
             'tournament the tree is perfect by construction and it is O(log n) — but writing O(log n) '
             'without the balance assumption is the kind of imprecision worth avoiding, especially when '
             'the neighbouring question on this page (Q10) hands you an explicitly imbalanced tree.'),
    edges=[
        ['Null root', 'Throws `ArgumentNullException`.'],
        ['Single leaf', 'Throws — no runner-up exists.'],
        ['Two leaves', 'One comparison; the loser is the answer.'],
        ['Runner-up adjacent to the winner', 'Found on the last step of the walk.'],
        ['Runner-up at the top of the tree', 'Found on the first step. My second example — the '
                                            'answer is 3, at depth 1, while 50 sits next to the winner '
                                            'and is not the answer.'],
        ['Duplicate leaf values', '**Outside the stated constraints.** The winner’s path could fork '
                                  'and the walk may pick the wrong branch. The fallback is the O(n) scan; '
                                  'say so rather than claiming the walk still works.'],
        ['Imbalanced tree', 'Correct, but O(h) = O(n) in the worst case.'],
        ['Malformed node with one child', 'Handled defensively: the loop still terminates and the missing '
                                          'sibling is skipped.'],
    ],
    fups=[
        dict(given=True,
             q='Explain why the second smallest must appear among the nodes that lost directly to the '
               'minimum.',
             thinking='This **is** the question — the statement asks for the proof, not just the '
                      'algorithm. Give it as a short chain rather than a hand-wave.',
             approach='Let `m` be the minimum and let `x` be any other leaf. Trace `x` upward: it wins '
                      'until it meets `m`’s path, where it loses. Either it loses directly to `m`, '
                      'in which case it is a candidate; or it first loses to some `y ≠ m`, which '
                      'means `y < x`, and `y` later loses to `m`. Then `m < y < x`, so `x` is at least '
                      'third. Hence only the direct losers to `m` can be second, and there are exactly '
                      '`h` of them — one per level of `m`’s path.',
             tradeoff='None; it is the justification. Note what it depends on: that the tournament is a '
                      'genuine knockout, so every non-winner loses exactly once and to a strictly smaller '
                      'value. Change the tournament to best-of-three, or allow a losing value to continue, '
                      'and the argument fails immediately.',
             t='O(h)', s='O(1)'),
        dict(q='Find the third smallest.',
             thinking='The obvious generalisation, and it does **not** work the same way — which is '
                      'the most useful thing to know here.',
             approach='The third smallest is **not** simply the second smallest of the h direct losers. '
                      'Suppose `s` is the runner-up. The third smallest is either another direct loser to '
                      '`m`, or it is something that lost directly to `s` on `s`’s own path back down '
                      'to its leaf. So you need `m`’s losers **plus** `s`’s losers — which '
                      'means locating `s`’s leaf and walking its subtree path.\n\n'
                      'Generalising to the k-th, this becomes the classic **tournament selection**: '
                      'repeatedly remove the current winner and replay only the affected path, which is '
                      'O(k log n) overall and is exactly how a selection tree works.',
             tradeoff='O(h) for the second, O(k log n) for the k-th. Beyond a fairly small k the O(n) scan '
                      'with a bounded heap wins, and the crossover is around k ≈ n / log n. The '
                      'valuable part of this answer is recognising that the clean structure of the '
                      'second-smallest argument does not simply extend — candidates who assume it '
                      'does give a confidently wrong algorithm.',
             t='O(k log n) for the k-th', s='O(k)'),
        dict(q='Duplicate leaf values are allowed now.',
             thinking='The uniqueness constraint was load-bearing in a specific place, and naming that '
                      'place is the answer.',
             approach='With duplicates, a parent can equal **both** children, so the winner’s path '
                      'forks and "follow the child equal to the parent" is no longer well defined. Also '
                      '"second smallest" becomes ambiguous: the second smallest *distinct* value, or the '
                      'second element of the sorted multiset (which could equal the minimum)?\n\n'
                      'The robust answer is to fall back to an O(n) traversal tracking the two smallest '
                      'distinct values. Attempting to fix the walk means exploring both branches at every '
                      'tie, which in the worst case — all leaves equal — degenerates to O(n) '
                      'anyway, with considerably more code.',
             tradeoff='O(n) instead of O(h), and it is the correct trade rather than a defeat: the '
                      'structure genuinely stops carrying enough information. Saying "the constraint was '
                      'doing real work and here is exactly which line it supported" is the answer being '
                      'looked for.',
             t='O(n)', s='O(1)'),
        dict(q='Return who the runner-up lost to, and the match path.',
             thinking='A small extension that confirms the walk is understood as a tournament rather than '
                      'as a pointer trick.',
             approach='Record the node where `best` was updated. Everything on the winner’s path from '
                      'the root down to that point is the sequence of matches the runner-up would have had '
                      'to win, and the runner-up lost to the minimum at that node. Collect the path into a '
                      'list as you walk.',
             tradeoff='O(h) extra space for the path, which is nothing. It is also the more useful API for '
                      'anything actually displaying a tournament bracket, and it is free because the walk '
                      'already visits exactly those nodes.',
             t='O(h)', s='O(h)'),
    ],
    testing=dict(skills=[
        '**Using the structure you were given** — the difference between O(h) and O(n) here is '
        'entirely about whether you exploit what the tree means.',
        '**Constructing a proof** — the statement asks for it explicitly, so this is the main skill '
        'under test.',
        '**Identifying which constraint is load-bearing** — unique leaves, and the exact line it '
        'supports.',
        '**Not over-generalising** — the third smallest does not follow the same argument.',
        '**Bound precision** — O(h), not O(log n), unless balance is promised.',
    ],
        senior='Finds the walk-down-the-winner’s-path solution and implements it correctly, including '
               'the two-leaf case.',
        staff='Does that, and: gives the three-line proof as a chain of inequalities rather than an '
              'assertion; says that O(h) becomes O(log n) only for a balanced tree; identifies unique '
              'leaves as the constraint that makes the path unambiguous and names the exact comparison it '
              'supports; knows that the third smallest needs `s`’s losers as well and that the '
              'general case is tournament selection at O(k log n); and throws rather than returning a '
              'sentinel from a single-leaf tree. Declining to generalise the argument to the third '
              'smallest is the sharpest signal, because the generalisation is tempting and wrong.'),
    say=[
        "The root is the overall minimum, since every parent is the smaller of its children. So the "
        "question is who the runner-up is.",
        "Here is the argument you asked for. Take any leaf other than the minimum. Trace it upward — it "
        "keeps winning until it meets the minimum's path, and there it loses. Either it loses directly to "
        "the minimum, or it first loses to something else, call it y. But then y is smaller than it, and y "
        "goes on to lose to the minimum too. So there are at least two values below it and it is at best "
        "third.",
        "Therefore only values that faced the minimum directly can be second. And those are exactly the "
        "siblings along the minimum's path from the root down to its leaf — one per level.",
        "So: walk down from the root following the child whose value equals the parent, and take the minimum "
        "of the siblings as I go. That is O(h) time and constant space, against O(n) for scanning the tree.",
        "The unique-leaves constraint is doing real work, and it is doing it in one specific line. It "
        "guarantees the parent equals exactly one child, so the winner's path never forks. With duplicates "
        "that line could pick the wrong branch, and I would fall back to the O(n) scan rather than pretend "
        "the walk still works.",
        "I should say O(h) rather than O(log n) — a real tournament is balanced by construction, but the "
        "statement does not promise it.",
        "One thing worth flagging: this does not generalise cleanly to the third smallest. The third is "
        "either another of the minimum's losers, or something that lost to the runner-up on its own path. "
        "The k-th case is tournament selection, replaying the affected path each time, which is O(k log n).",
    ],
    video=dict(title='LinkedIn Coding — Tournament Tree, Second Smallest', mins=12,
               objective='Make the proof the content, and show that the O(h) answer comes from taking the '
                         'structure seriously rather than from a trick.',
               beats=[('0:00', 'The question, and what a tournament tree is'),
                      ('1:20', 'The brute-force scan, and what it throws away'),
                      ('2:40', 'The argument: who can possibly be second'),
                      ('4:40', 'Exactly h candidates, one per level'),
                      ('5:50', 'Walking the winner’s path'),
                      ('7:00', 'The C# implementation'),
                      ('8:10', 'Tracing the example to 5'),
                      ('9:00', 'Which line the uniqueness constraint supports'),
                      ('10:00', 'Why the third smallest is a different problem'),
                      ('11:10', 'How to say it')]),
))

# ============================================================ Q17
QUESTIONS.append(dict(
    id='q17', n=17, name='Merge two metadata trees',
    tags=['TREE', 'HASHING', 'DESIGN', 'CONCURRENCY', 'SYSTEM DESIGN'],
    diff='HARD', prio='HIGH',
    verdict_short='InterviewDB + your own list (first-party) + 617 on the supplied list',
    prio_why=(
        '**On your own list**: "merge two keyed trees, summing values — the n-ary variant of Merge '
        'Two Binary Trees" — first-party, and already worked in this workspace. `617` and `297` are '
        'both on the supplied number list, and 297 is literally the first follow-up. Highest confidence on '
        'the page alongside Q5, and the **seven** supplied follow-ups take it from a twenty-line recursion '
        'to a systems conversation, which is exactly what a Staff loop wants.'),
    idb=(
        'Merge two trees containing:\n\n'
        '• key\n'
        '• value\n\n'
        'The value represents the sum of this node and its child node values.\n\n'
        'When merging:\n\n'
        '• absent branches are created\n'
        '• existing branch values are summed\n'
        '• child ordering is arbitrary\n'
        '• keys are unique among siblings\n\n'
        'Implement:\n\n'
        'merge(TreeNode s, TreeNode t)\n\n'
        'Follow-ups:\n'
        '1. Best serialization format and trade-offs\n'
        '2. Transform result into a side-heavy tree\n'
        '3. Concurrent merges\n'
        '4. Same tree used as source by one thread and target by another\n'
        '5. Very large serialized trees (1GB+)\n'
        '6. Performance optimization\n'
        '7. Memory considerations'),
    dd=dict(elsewhere=[
        ('idb', 'Supplied with four precise rules and **seven follow-ups**, which is more than any other '
                'question here. Follow-ups 3 and 4 are concurrency, 5 and 7 are memory, 1 is encoding — '
                'so most of the question is not the recursion.'),
        ('reported', '**"Merge two keyed trees, summing values (n-ary variant of Merge Two Binary '
                     'Trees)"** — on your own list of past LinkedIn questions. First-party, and '
                     'already worked in the coding page.'),
        ('reported', '**Tree Fusion** was one of the visible interviewdb titles before you bought access, '
                     'and was guessed in this workspace as "probably a tree merge, unconfirmed". The full '
                     'statement now confirms that guess.'),
        ('lc', '617 Merge Two Binary Trees (on the supplied list) is the binary case. 297 Serialize and '
               'Deserialize Binary Tree (also supplied) **is follow-up 1**. 100 Same Tree is the lockstep '
               'two-tree recursion.'),
    ],
        verdict='**InterviewDB reported, independently first-party reported, and it resolves an earlier '
                'unknown title in this workspace.** Highest confidence on the page.'),
    ambiguity=(
        '"The value represents the sum of this node and its child node values" is an **invariant**, not '
        'just a description, and it has a consequence worth stating: the value is partly derived. A '
        'node’s own contribution is `value − sum(children.value)`.\n\n'
        'The good news is that the invariant is preserved automatically by summing. If both inputs satisfy '
        '`value = own + Σ children`, then adding them gives `(own₁+own₂) + Σ '
        '(children₁+children₂)`, which satisfies it too. So **nothing has to be recomputed** '
        '— and saying that is better than either silently relying on it or writing a fix-up pass.\n\n'
        'What the statement does not say: whether the merge may mutate its inputs, and what to do if the '
        'two roots have different keys. I build a new tree and mutate nothing — which is what makes '
        'follow-up 4 answerable — and I throw on mismatched roots rather than inventing a parent.'),
    understand=dict(
        what='Two trees describing the same hierarchy, each holding partial totals. Merge them into one '
             'tree whose values are the combined totals, creating branches that exist on only one side.',
        compute='A merged tree. Same shape as the union of the two inputs; values summed where both have a '
                'node.',
        constraints=[
            'Children are identified by **key**, not by position. That is the whole difference from '
            'LeetCode 617 and it is what makes child lookup a dictionary probe.',
            'Keys are unique among siblings, so a key identifies at most one child — which is what '
            'lets the children be a dictionary at all.',
            'Child ordering is arbitrary, so the output order carries no meaning. That matters for '
            'serialisation, where you have to *choose* an order.',
            'The value invariant is additive, so summing preserves it.',
        ],
        assume=[
            ['Neither input is mutated; the merge returns a new tree.',
             'The statement does not say. It is what makes `Merge(x, x)` safe and concurrent readers safe, '
             'and it is the answer to follow-up 4 — so it is worth choosing deliberately and saying '
             'why.'],
            ['Both roots have the same key.',
             'Otherwise there is no single tree to produce. I throw; the alternative is inventing a '
             'synthetic parent, which silently changes the data.'],
            ['Values are non-negative and fit in a `long`.',
             '`int` would overflow on a merge of large totals, and the whole point is that values are '
             'sums. Negative values would break the `IsConsistent` check but not the merge.'],
            ['Trees are deep enough to matter.',
             'Follow-up 5 says 1 GB, so recursion depth is a real risk and an iterative version has to '
             'exist. Assuming shallow trees would make follow-up 5 unanswerable.'],
        ]),
    examples=[
        ('Tree s', 'root 10 { a 6 { x 2 }, b 1 }', 'own(root) = 10 − 6 − 1 = 3'),
        ('Tree t', 'root 12 { a 4, c 5 }', 'own(root) = 12 − 4 − 5 = 3'),
        ('Merged', 'root 22 { a 10 { x 2 }, b 1, c 5 }', ''),
        ('', 'a exists in both', '6 + 4 = 10 — summed'),
        ('', 'b only in s', 'carried across unchanged'),
        ('', 'c only in t', 'branch created'),
        ('', 'x under a, only in s', 'grandchild survives the merge'),
    ],
    examples_note='The statement referred to a supplied example that did not come through, so this one is '
                  'mine — built to exercise all four stated rules at once, plus a grandchild to '
                  'confirm the recursion goes deeper than one level. The invariant is checked on the '
                  'result by `IsConsistent`, and the iterative and recursive merges are asserted to agree.',
    observation=(
        'Two observations. The first is small and the second is what the follow-ups are built on.\n\n'
        '**One: children keyed rather than positional turns the merge into three cases.** At each node, '
        'look at every child key on both sides. In both → recurse. Only in `s` → copy the branch. '
        'Only in `t` → copy the branch. That is the same three-case shape as merging two sorted lists '
        'or comparing two trees, and with a dictionary of children each case is an O(1) probe. LeetCode '
        '617 has the same three cases hidden in its null checks; making the children keyed just makes '
        'them explicit.\n\n'
        '**Two: build a new tree rather than mutating either input.** This looks like a style choice and '
        'it is the load-bearing decision of the whole question, because it answers three of the seven '
        'supplied follow-ups at once.\n\n'
        'Follow-up 4 asks what happens when one thread uses a tree as a source while another uses it as a '
        'target. If the merge mutates the target, the first thread is reading a tree that is changing '
        'underneath it — torn reads, double counting, and if the two are the *same* tree, potentially '
        'a dictionary being enumerated while it is written, which throws. If the merge only ever reads its '
        'inputs, all of that disappears: any number of threads may merge from the same trees '
        'simultaneously, and `Merge(x, x)` is well defined.\n\n'
        'So: **choose the pure version first and let it answer the concurrency follow-ups**, rather than '
        'writing the in-place version and then trying to lock it. The in-place variant is worth keeping '
        'to name the trap — which is why `MergeInto` is in the listing and refuses a self-merge '
        'explicitly.\n\n'
        'And the invariant needs no maintenance, because summation is additive. That is worth noticing '
        'rather than defending: if the invariant had been "value is the *maximum* of this node and its '
        'children", merging would have needed a fix-up pass, and this question would be materially harder.'),
    brute=dict(
        how='Serialise both trees to flat lists of `(path, value)` pairs, merge the lists by path, then '
            'rebuild a tree from the merged paths.',
        cx='O(n log n) for the sort, plus O(n · depth) to build and compare the path strings. O(n) '
            'space, with the paths often larger than the trees.',
        why_not='It works, and it is genuinely how you would do this **out of core** for follow-up 5 '
                '— so it is worth stating rather than dismissing. In memory it is strictly worse: it '
                'materialises a path string per node, which for a deep tree costs more than the tree, and '
                'it pays a sort for an ordering the recursion gets for free. The recursion is O(n) with no '
                'sort and no path strings. But keep this approach in your pocket, because it is the '
                'external-merge answer.'),
    optimal=dict(pipeline=[
        ('INPUT', 'Two `MetaNode` roots, each with `Dictionary<string, MetaNode>` children'),
        ('TRANSFORMATION', 'None. The keyed children are already the index the merge needs.'),
        ('DATA STRUCTURE', '`Dictionary<string, MetaNode>` per node for O(1) child lookup'),
        ('ALGORITHM', 'Recurse in lockstep: sum the values, recurse on shared keys, clone branches present '
                      'on one side only'),
        ('OUTPUT', 'A new tree; both inputs untouched'),
    ],
        why=[
            ['`Dictionary<string, MetaNode>` for children',
             'Keys are unique among siblings, so a dictionary is the exact model, and "is this key on the '
             'other side" becomes O(1). A list of children would make the merge O(c²) per node.'],
            ['`StringComparer.Ordinal`',
             'Keys are identifiers. Culture-aware comparison is both slower and, in the general case, '
             'capable of treating distinct keys as equal — which here would merge two different '
             'branches into one and silently corrupt the totals.'],
            ['A new tree rather than in-place',
             'The decision that answers follow-ups 3 and 4. Inputs are read-only, so concurrent merges '
             'from shared trees need no locking at all.'],
            ['`long` values',
             'The values are sums of sums. `int` overflows, silently and negatively.'],
            ['An iterative variant alongside the recursive one',
             'Follow-up 5 specifies 1 GB trees, and the recursion depth is the height. The iterative '
             'version with an explicit stack is the one that survives a 60,000-deep chain — tested.'],
        ],
        steps=[
            'Either side null → return a clone of the other.',
            'Root keys differ → throw; there is no single tree to produce.',
            'Create a new node with `s.Value + t.Value`.',
            'For each child of `s`: present in `t` → recurse; otherwise clone the branch.',
            'For each child of `t` not already handled → clone the branch.',
            'Return the new node.',
        ]),
    walk=dict(
        intro='The example. `s = root 10 { a 6 { x 2 }, b 1 }` and `t = root 12 { a 4, c 5 }`.',
        headers=['At', 's', 't', 'Action', 'Result'],
        rows=[
            ['root', '10', '12', 'sum', 'new node root = 22'],
            ['child a', '6', '4', 'in both → recurse', 'a = 10'],
            ['  child x under a', '2', '—', 'only in s → clone the branch', 'x = 2'],
            ['child b', '1', '—', 'only in s → clone', 'b = 1'],
            ['child c', '—', '5', 'only in t → clone', 'c = 5'],
            ['done', '', '', '', 'root 22 { a 10 { x 2 }, b 1, c 5 }'],
        ],
        close='Check the invariant on the result: `own(root) = 22 − 10 − 1 − 5 = 6`, which '
              'is exactly `own(s.root) + own(t.root) = 3 + 3`. Nothing recomputed it — it fell out of '
              'the summation, which is the additivity point made concrete. Also note that `s` still reads '
              '10 and `t` still has two children: nothing was mutated, and that is what makes the '
              'concurrency follow-ups easy.'),
    code=[
        ('The node', 'Q17_MergeTrees.cs', 'MetaNode'),
        ('The merge, plus the in-place trap and the iterative version', 'Q17_MergeTrees.cs', 'MetaTreeMerge'),
        ('Follow-up 2 — the side-heavy form', 'Q17_MergeTrees.cs', 'SideHeavy'),
    ],
    codewalk=[
        ('Why `Merge` allocates a new node before looking at any child',
         '`new MetaNode(s.Key, s.Value + t.Value)` first, then the children are filled in. Nothing reads '
         'from the inputs after they have been written to, because they are never written to at all. That '
         'is the property the concurrency follow-ups need, and it comes from this line rather than from a '
         'lock.'),
        ('The two loops, and the `ContainsKey` guard on the second',
         'The first loop handles "in s" — recursing when `t` also has the key, cloning otherwise. The '
         'second handles "only in t", guarded by `!merged.Children.ContainsKey(kv.Key)` so shared keys are '
         'not processed twice. Without the guard, a shared child would be overwritten by a clone of '
         '`t`’s branch and `s`’s subtree would vanish — with a plausible-looking result.'),
        ('`MergeInto` exists to name the trap, not to be used',
         'It throws on `ReferenceEquals(target, source)`. Self-merging in place double-counts, and worse, '
         'it enumerates `source.Children` while writing to `target.Children` — the same dictionary '
         '— which throws `InvalidOperationException` at an unpredictable point, leaving the tree '
         'half-merged. **This is follow-up 4 in miniature** and it is why the pure version is the answer.'),
        ('`MergeIterative` and the work stack of triples',
         '`Stack<(MetaNode S, MetaNode T, MetaNode Out)>` — the output node is carried alongside the '
         'two inputs, so children can be attached without a parent pointer. Tested on a 60,000-deep chain, '
         'which the recursive version would not survive. Note that `Clone` is **still recursive**, so a '
         'deep branch present on only one side would still overflow — an honest gap, and the fix is '
         'an iterative clone.'),
        ('`IsConsistent` checks the invariant, and only one direction',
         'It verifies `value >= sum(children)`, i.e. that a node’s own contribution is non-negative. '
         'It cannot verify more without knowing the intended own-values. Writing the invariant as a '
         'checkable function is worth doing precisely because the statement gave it as prose — it is '
         'the assertion a reviewer would ask for.'),
        ('`SideHeavy.Encode` orders siblings before encoding',
         '`OrderBy(k => k.Key, StringComparer.Ordinal)`. The statement says child ordering is arbitrary, '
         'and a dictionary has no order at all — so any serialised or linked form must **choose** '
         'one, or two encodings of the same tree will differ. That determinism is what makes the encoding '
         'comparable, hashable and diffable, and it is the detail that connects follow-up 2 to follow-up 1.'),
        ('`Decode` walks the sibling chain, and the recursion handles the subtree',
         '`for (child = b.Left; child != null; child = child.Right)` iterates one level; `Decode(child)` '
         'handles that child’s own children via `child.Left`. Getting this wrong — recursing in a '
         'way that also follows `Right` — duplicates siblings into the wrong level, which is why the '
         'round trip is asserted in the tests rather than eyeballed.'),
    ],
    cx=dict(rows=[
        ['`Merge`', 'O(nₛ + nₜ)', 'O(nₛ + nₜ)',
         'Every node of both inputs visited once; the output is a full copy'],
        ['`MergeInto`', 'O(nₛ + nₜ)', 'O(nₜ) new nodes only',
         'Reuses the target, so only cloned branches allocate'],
        ['`MergeIterative`', 'O(nₛ + nₜ)', 'O(n) heap stack',
         'Same work; the stack moves from the thread stack to the heap'],
        ['`Clone`', 'O(n)', 'O(n)', 'One new node per source node'],
        ['`IsConsistent`', 'O(n)', 'O(h)', 'One pass, recursive'],
        ['`SideHeavy.Encode`', 'O(n log c)', 'O(n)', 'The `log c` is sorting each node’s c children'],
    ],
        note='**The pure merge allocates a node for every node in both inputs, and that is its real '
             'cost — not the time.** For 1 GB trees the copy is the problem, not the traversal: you '
             'need roughly 2× the memory of the result live at once. `MergeInto` avoids it by reusing '
             'the target, which is exactly the trade the concurrency follow-ups make you choose about. '
             'Naming memory rather than time as the binding constraint is the right framing for follow-ups '
             '5 and 7.'),
    edges=[
        ['Either input null', 'Returns a clone of the other. A **clone**, not the same reference, so the '
                              'caller cannot accidentally alias an input into the result.'],
        ['Both null', 'Returns null.'],
        ['Root keys differ', 'Throws. Inventing a synthetic parent would change the data silently.'],
        ['`Merge(x, x)`', 'Safe — values double, `x` untouched. The pure version handles it with no '
                          'special case.'],
        ['`MergeInto(x, x)`', '**Refused explicitly.** Double-counts and can throw mid-merge, leaving the '
                              'tree half-updated.'],
        ['Deep chain (60,000 nodes)', 'Recursive merge overflows; `MergeIterative` handles it. Tested. '
                                      '`Clone` is still recursive — a stated gap.'],
        ['One tree a single node', 'The other’s children are all cloned across.'],
        ['Value overflow', '`long`. `int` would wrap negative on large sums.'],
        ['Duplicate sibling keys', 'Impossible by the stated constraint, and the dictionary enforces it.'],
        ['Empty children on both sides', 'A leaf whose value is the sum of the two.'],
    ],
    fups=[
        dict(given=True, q='What is the best serialization format, and what are the trade-offs?',
             thinking='**This is LeetCode 297, which is on the supplied number list.** The thing that makes '
                      'it interesting here is that children are keyed and unordered, which 297 does not '
                      'have to deal with.',
             approach='Whatever the format, two problems have to be solved: **key and value per node**, and '
                      '**where a node’s children end**. Positional null markers (297’s approach) '
                      'do not work, because the arity is unbounded — so either a child count per node '
                      'or an explicit terminator.\n\n'
                      'A length-prefixed binary format is the right answer for size and speed: '
                      '`[keyLen][key][value][childCount]` then the children, depth-first. JSON is the right '
                      'answer for debuggability and for crossing a service boundary you do not own. '
                      'Protobuf sits between and buys schema evolution, which matters if this format '
                      'outlives the code.\n\n'
                      'And **sibling order must be canonicalised** — sorted by key — or two '
                      'serialisations of the same tree differ, which breaks hashing, diffing and any '
                      'content-addressed cache.',
             tradeoff='Binary is compact and fast and unreadable, and versioning it is on you. JSON is '
                      'roughly 3–5× larger and parses far slower, and any engineer can debug it '
                      'with `cat`. For 1 GB trees the size difference is the deciding factor and I would '
                      'go binary with a version byte; for an API I would take JSON and not think about it '
                      'again. The canonical ordering is not a trade — it is required either way.',
             t='O(n) to write and read', s='O(depth) streaming, rather than O(n)'),
        dict(given=True, q='Transform the result into a side-heavy tree.',
             thinking='"Side-heavy" is not standard terminology, so the honest move is to state the '
                      'interpretation. The one that makes sense for an n-ary tree is the '
                      '**left-child / right-sibling** encoding, which is LeetCode 431 and turns an n-ary '
                      'tree into a binary one that leans right.',
             approach='Each node’s `Left` is its first child and its `Right` is its next sibling. '
                      'Every n-ary tree maps to a binary tree uniquely and reversibly, and the tree leans '
                      'right by exactly the width of the widest sibling list. Siblings are sorted first, '
                      'so the encoding is deterministic.',
             tradeoff='The binary form has fixed arity, so it serialises with positional markers and fits '
                      'any binary-tree algorithm — which is the point. The cost is depth: a node with '
                      '1,000 children becomes a right chain of 1,000, so a recursive walk over the encoded '
                      'form is far deeper than over the original. If the interviewer meant something else '
                      'by side-heavy — a deliberate imbalance, or all children on one side — I '
                      'would ask, because the word is not standard and guessing would waste the answer.',
             code=[('Left-child / right-sibling', 'Q17_MergeTrees.cs', 'SideHeavy')],
             t='O(n log c) to encode, O(n) to decode', s='O(n)'),
        dict(given=True, q='Several threads merge concurrently.',
             thinking='With the pure merge, this is nearly a non-question — and explaining *why* it '
                      'is a non-question is the answer.',
             approach='`Merge` only reads its inputs and only writes nodes it has just allocated, so any '
                      'number of threads may merge from the same trees with **no synchronisation at '
                      'all**. Nothing is shared and mutable.\n\n'
                      'The work also parallelises naturally: each child subtree is independent, so '
                      '`Parallel.ForEach` over the children of the root, with a depth cutoff so small '
                      'subtrees are merged inline rather than scheduled.',
             tradeoff='Purity buys lock-free concurrency and costs a full copy. `MergeInto` avoids the '
                      'copy and immediately needs locking — and locking a tree correctly means either '
                      'one lock (no concurrency) or per-node locks with a consistent acquisition order '
                      '(deadlock risk, and hard to review). Parallelising has a real cutoff: below a few '
                      'thousand nodes the task overhead exceeds the merge, so measure rather than '
                      'parallelise everything.',
             t='O(n) work, O(depth) span with full parallelism', s='O(n) for the result'),
        dict(given=True,
             q='The same tree is used as a source by one thread and as a target by another.',
             thinking='**This is the sharpest of the seven**, and with the pure version the answer is '
                      'already in place — which is the reward for having chosen it.',
             approach='With `Merge`, there is no target. Nothing is written to either input, so the '
                      'scenario cannot arise: both threads read, both produce their own result.\n\n'
                      'With `MergeInto` it is a genuine race, and it is worth being concrete about the '
                      'damage. The reader sees some children already summed and others not — a torn '
                      'read, producing a total that corresponds to no point in time. And if the source '
                      'and target are the same object, a dictionary is enumerated while being written, '
                      'which throws `InvalidOperationException` partway through and leaves the tree '
                      'half-merged with no way to roll back.',
             tradeoff='If in-place is unavoidable for memory reasons, the answer is **copy-on-write with '
                      'an atomic publish**: build the merged tree, then swap the root reference with '
                      '`Interlocked.Exchange`. Readers hold whichever root they picked up and see a '
                      'consistent snapshot; there is no locking and no torn read. The cost is that the '
                      'copy is back, which is the honest circle: you can have immutability or you can '
                      'have the memory saving, not both.',
             code=[('The in-place version, which refuses the self-merge rather than hiding it',
                    'Q17_MergeTrees.cs', 'MetaTreeMerge|public static void MergeInto')],
             t='O(n)', s='O(n) for the snapshot'),
        dict(given=True, q='The serialized trees are over 1 GB.',
             thinking='At this size the constraints invert: memory becomes binding and the recursion '
                      'becomes a liability. Neither tree may be fully materialised.',
             approach='Three things.\n\n'
                      '**Do not recurse.** `MergeIterative` moves the stack to the heap; it is tested on a '
                      '60,000-deep chain. (`Clone` is still recursive — that would need fixing too.)\n\n'
                      '**Stream instead of materialising.** If both files are written with siblings in '
                      'canonical key order, the merge is a **single synchronised pass** over the two '
                      'streams, writing the output as it goes — exactly a sorted-list merge, with '
                      'O(depth) memory rather than O(n). That is the real answer, and it is why the '
                      'canonical ordering from follow-up 1 matters here.\n\n'
                      '**If they are not ordered**, sort externally first, or fall back to the '
                      'path-keyed external merge from the brute-force section — which is exactly '
                      'where that approach earns its place.',
             tradeoff='Streaming is O(depth) memory instead of O(n) and needs the inputs canonically '
                      'ordered, so it pushes a requirement back onto whoever writes the files. It also '
                      'gives up random access: you cannot answer "what is the value at this path" without '
                      'a full pass. In .NET there is a further specific: any buffer over 85 KB lands on '
                      'the **Large Object Heap**, which is not compacted by default, so a 1 GB merge that '
                      'allocates large arrays fragments the heap. Use pooled buffers and `Span<T>` slices '
                      'rather than fresh arrays per node.',
             code=[('Iterative merge, for depth', 'Q17_MergeTrees.cs',
                    'MetaTreeMerge|public static MetaNode MergeIterative')],
             t='O(n) with one pass', s='O(depth) streaming versus O(n) in memory'),
        dict(given=True, q='Optimise the performance.',
             thinking='Say what the bottleneck is before optimising, because for this problem it is '
                      'allocation rather than comparison.',
             approach='In order of payoff. **Iterate the smaller tree** and probe the larger, so the '
                      'number of dictionary lookups is bounded by the smaller side. **Pre-size the child '
                      'dictionaries** to the combined child count, avoiding rehashing as they fill. '
                      '**Intern or pool the key strings**, since the same keys recur across a large tree '
                      'and each one is otherwise a separate allocation. **Parallelise across the '
                      'root’s children** with a size cutoff. And **`StringComparer.Ordinal`**, which '
                      'is both faster and the correct comparer.',
             tradeoff='The first three are close to free and I would do them without measuring. '
                      'Parallelism has a real cutoff and can be slower on small trees. String interning '
                      'trades a permanent table for reduced allocation, which is right for a long-lived '
                      'service and wrong for a one-off tool. The honest headline is that the merge is '
                      '**allocation-bound, not compute-bound** — so the biggest single win is not '
                      'allocating, which means `MergeInto` where the semantics allow it.',
             t='O(min(nₛ, nₜ)) lookups', s='unchanged'),
        dict(given=True, q='What about memory?',
             thinking='The .NET specifics matter here and are what distinguish an answer from a generic '
                      'one.',
             approach='The pure merge needs both inputs plus the full result live simultaneously '
                      '— roughly 2× the result. Per node the overhead is the object header, the '
                      'key string and a `Dictionary` instance, and **the dictionary is the expensive '
                      'part**: an empty `Dictionary<string, MetaNode>` is around 80 bytes, which on a tree '
                      'of mostly-leaf nodes can exceed the data. Allocating it lazily, only when a node '
                      'actually gains a child, is a large and easy saving.\n\n'
                      'Beyond that: pool and reuse buffers rather than allocating per node, keep '
                      'allocations under the 85 KB Large Object Heap threshold, and if the trees are '
                      'genuinely huge, consider a flattened representation — arrays of nodes indexed '
                      'by integer rather than object references — which removes the per-object '
                      'overhead entirely and is much less pleasant to work with.',
             tradeoff='Lazy dictionaries save a lot and add a null check on every access. A flattened '
                      'array representation saves the most and costs readability and every existing '
                      'traversal. `MergeInto` halves peak memory and gives up the concurrency properties. '
                      'These are the same trade seen from three directions, and the right answer depends '
                      'on whether the trees are held long-term or merged once and discarded.',
             t='unchanged', s='~2× the result for the pure merge; ~1× for in-place'),
    ],
    testing=dict(skills=[
        '**Keyed versus positional recursion** — the three-case merge, made explicit by the '
        'dictionary.',
        '**Immutability as a design tool** — choosing the pure version and having it answer three '
        'later follow-ups.',
        '**Invariant reasoning** — noticing that additivity preserves the stated property for free.',
        '**Concurrency** — naming the concrete damage of the in-place race, including the '
        'enumerate-while-writing throw.',
        '**Encoding design** — unbounded arity, canonical ordering, and why 297’s null markers '
        'do not transfer.',
        '**Memory at scale** — recursion depth, streaming, and .NET specifics like the LOH and the '
        'per-node dictionary cost.',
    ],
        senior='Writes the keyed three-case recursion correctly, handles absent branches on both sides, '
               'and answers the follow-ups one at a time as they come.',
        staff='Does that, and: chooses immutability up front **and says that it is what will answer the '
              'concurrency follow-ups**, rather than arriving there when asked; notices that summation '
              'preserves the invariant so nothing needs recomputing; states the interpretation of '
              '"side-heavy" instead of guessing; describes the in-place race concretely, including that '
              'the same-tree case throws mid-merge; sees that the canonical sibling ordering required for '
              'serialisation is what makes the 1 GB streaming merge possible — connecting follow-ups '
              '1 and 5; and frames the merge as **allocation-bound rather than compute-bound**. Answering '
              'follow-up 4 by pointing at a decision made in the first two minutes is the strongest thing '
              'available on this question.'),
    say=[
        "Children are keyed rather than positional, so at each node I have three cases: the key is in both, "
        "in the source only, or in the target only. In both, I recurse and sum. Otherwise I copy the branch "
        "across. That is the same shape as merging two sorted lists.",
        "One thing worth noticing about the invariant. You said the value is the sum of the node and its "
        "children. That is additive, so if both inputs satisfy it, summing satisfies it too — I do not need "
        "a fix-up pass. If the invariant had been a maximum rather than a sum, I would.",
        "Now a decision I want to make explicitly, because I think it answers several of your follow-ups. I "
        "am going to build a new tree and not mutate either input.",
        "That is what makes your fourth follow-up — one thread using a tree as source while another uses it "
        "as target — not a problem at all. There is no target. Nothing is written to either input, so any "
        "number of threads can merge from the same trees with no locking.",
        "If I had done it in place, that is a real race, and worth being specific about the damage: the "
        "reader sees some children summed and others not, so it gets a total that corresponds to no point "
        "in time. And if source and target are the same object, I am enumerating a dictionary while writing "
        "to it, which throws partway through and leaves the tree half-merged.",
        "On serialisation — that is essentially LeetCode 297, but harder in one respect. Arity is unbounded, "
        "so I cannot use positional null markers; I need a child count or a terminator per node. I would "
        "use a length-prefixed binary format for size, or JSON if it crosses a boundary I do not own.",
        "And critically, I have to canonicalise the sibling order, because a dictionary has none. Otherwise "
        "two serialisations of the same tree differ and I lose hashing and diffing.",
        "That canonical ordering then pays off on your 1 GB follow-up. If both files have siblings in key "
        "order, the merge becomes a single synchronised pass over the two streams, writing output as it "
        "goes — O(depth) memory instead of O(n). That is the real answer at that size, and it is why the "
        "ordering decision matters.",
        "I would also not recurse at that scale — the depth is the height, so I want an explicit stack.",
        "On performance and memory: this is allocation-bound, not compute-bound. The biggest single cost is "
        "a Dictionary per node, about eighty bytes empty, which on a mostly-leaf tree exceeds the data. I "
        "would allocate it lazily. And in .NET, anything over 85 kilobytes goes on the Large Object Heap, "
        "which is not compacted, so I would pool buffers rather than allocate per node.",
        "On side-heavy — that is not standard terminology, so let me say what I am assuming. I read it as "
        "left-child right-sibling: each node's left pointer is its first child and its right pointer is its "
        "next sibling. That turns the n-ary tree into a binary one reversibly. If you meant something else "
        "I would rather ask than guess.",
    ],
    video=dict(title='LinkedIn Coding — Merging Keyed Trees, and Seven Follow-ups', mins=18,
               objective='Write the twenty-line recursion in five minutes, then show that one early '
                         'decision — immutability — answers three of the seven follow-ups, and '
                         'that canonical ordering connects two more.',
               beats=[('0:00', 'The question, four rules and seven follow-ups'),
                      ('1:30', 'Keyed children: the three-case merge'),
                      ('3:00', 'The invariant is additive — nothing to recompute'),
                      ('4:20', 'The decision: build new, mutate nothing'),
                      ('5:40', 'The C# implementation'),
                      ('7:10', 'Walking the example, and checking the invariant'),
                      ('8:30', 'Follow-up 4 — already answered, and why'),
                      ('10:00', 'What the in-place race actually does to you'),
                      ('11:20', 'Serialisation: unbounded arity, and canonical order'),
                      ('13:00', '1 GB: streaming, and why the ordering just paid off'),
                      ('14:40', 'Side-heavy: stating the interpretation'),
                      ('15:50', 'Allocation-bound, not compute-bound'),
                      ('17:00', 'How to say it')]),
))
