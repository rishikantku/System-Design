# -*- coding: utf-8 -*-
"""Chapter 2, Lesson 1 — Find Leaves of Binary Tree."""
from lib import *

TREE = {'n1': (0, 0, 1), 'n2': (1, -1.1, 2), 'n3': (1, 1.1, 3), 'n4': (2, -1.8, 4), 'n5': (2, -0.45, 5)}
EDGES = [('n1', 'n2'), ('n1', 'n3'), ('n2', 'n4'), ('n2', 'n5')]

lesson_header('2.1', 'Find Leaves of Binary Tree', 'Trees · post-order accumulation',
              'High', 'Your own list + LeetCode LinkedIn tag', '2026', 'High', 14,
              """Welcome to chapter two, lesson one. Find Leaves of Binary Tree. This one is on your own list of past LinkedIn """
              """questions and it sits in LeetCode's LinkedIn tagged set, so it is about as high a signal as this course has. """
              """But I am not here to give you the solution. I am here to show you how to find it, because the interviewer is """
              """watching you find it, not recite it. The whole lesson turns on one observation, and if you learn to look for """
              """that kind of observation you will solve three other problems in this chapter with the same move.""")

# ---------------------------------------------------------------- 1. question
sid = beat('Question', 'The question',
           statement_body := '<div class="qwrap"><div class="qtext" style="font-size:40px;line-height:1.35">'
           'Given the root of a binary tree, collect the nodes as if you repeatedly removed all the leaves: '
           'the first list is the leaves, the second is the leaves after removing those, and so on.</div></div>',
           """Here is the question as an interviewer would say it. Given the root of a binary tree, collect the nodes as if you """
           """repeatedly removed all of the leaves. So the first list you return is the current leaves. Then you imagine deleting """
           """them, look at what is a leaf now, and that is your second list. You keep going until the tree is empty. Notice the """
           """words as if. Nobody said you have to actually delete anything. Hold on to that; it is the crack we are going to """
           """open the problem with.""")

# ---------------------------------------------------------------- 2. interview context
sid = cards('Why this is in your course', [
 (0, 'On your own list', 'You collected it from past LinkedIn questions — first-party signal.', 'ok'),
 (0, 'LinkedIn tagged', 'Also in LeetCode\'s LinkedIn set, so it has stayed current.', 'info'),
 (1, 'What it scores', 'Whether you reframe, or simulate. Simulation is the trap.', 'shared'),
 (1, 'Pattern it teaches', 'Post-order accumulation: return a summary from each subtree.', 'dp'),
], cols=2)
seg(sid, 0, """Before we solve it, why is this lesson here at all? Two reasons. It is on your own list of questions LinkedIn has """
            """asked, and it also appears in the LinkedIn tagged set on LeetCode, which means it has not gone stale.""")
seg(sid, 1, """And here is what it actually scores. There are two ways to answer this problem. One is to simulate the process the """
            """question describes. The other is to notice that the process has a closed form. Candidates who simulate get a """
            """working answer and a mediocre grade. The pattern underneath is post-order accumulation, which means every """
            """recursive call returns a small summary of its subtree, and the parent combines those summaries. Four of the """
            """problems in this chapter are that same pattern wearing different clothes.""")

# ---------------------------------------------------------------- 3. think
think('Given the root of a binary tree, return the nodes layer by layer as if you repeatedly stripped the leaves.', 25,
      """Now, before I say anything else, this is the part of the lesson that actually matters. I am going to put the question """
      """on screen and start a timer. Do not watch me think. Say your first approach out loud, even if it is the clumsy one. """
      """The clumsy one is where every good interview starts.""",
      """Right. Let us work through the reasoning together. And if what you said was, I would find the leaves, remove them, and """
      """repeat, then you said exactly the right first thing. That is the brute force, and naming it early is a point in your """
      """favour, not against you.""")

# ---------------------------------------------------------------- 4. brute force
D = Diagram('Brute force: actually strip the leaves')
tree(D, TREE, EDGES, x=560, y=120, step=0, hls={'n4': 1, 'n5': 1, 'n3': 1, 'n2': 2, 'n1': 3})
D.label(1300, 200, 'Pass 1 → **[4, 5, 3]**\nthen delete them', kind='ok', step=1, w=520, size='m')
D.label(1300, 340, 'Pass 2 → **[2]**\nthen delete it', kind='ok', step=2, w=520, size='m')
D.label(1300, 480, 'Pass 3 → **[1]**', kind='ok', step=3, w=520, size='m')
D.label(120, 700, 'Each pass walks the **whole** tree again.', kind='deny', step=4, w=1700, size='l', align='center')
sid = D.build()
seg(sid, 0, """Here is a small tree. One at the top, two and three below it, and four and five hanging off the two. Let us do """
            """exactly what the question says.""")
seg(sid, 1, """Pass one. Which nodes are leaves right now? Four, five and three. That is our first list. Now delete them.""")
seg(sid, 2, """Pass two. With four and five gone, node two has become a leaf. So the second list is just two, and we delete it.""")
seg(sid, 3, """Pass three. Now one is a leaf. Third list, node one, and the tree is empty. Three passes, and the answer is four """
            """five three, then two, then one. This is correct. Write it down in the interview if it is all you have.""")
seg(sid, 4, """But look at what it cost. Every single pass walks the entire tree to find out which nodes are currently leaves. """
            """That repetition is the thing to be suspicious of.""")

# ---------------------------------------------------------------- 5. why not enough
sid = compare('Why the brute force is not good enough',
 ('Cost', 'deny', 0, ['Each pass is O(n) to find the leaves', 'Number of passes = height of the tree',
                      'Skewed tree → n passes → **O(n²)**', '10⁵ nodes in a chain → 10¹⁰ operations']),
 ('The smell', 'shared', 1, ['You are recomputing the same facts', 'Nothing about the tree changed between passes',
                             'The answer for a node never changes', 'So why discover it repeatedly?']))
seg(sid, 0, """Let us price it honestly, because that is what you would say out loud. Each pass costs order n to walk the tree. """
            """How many passes are there? One per layer, which is the height. On a balanced tree that is log n and you would """
            """probably get away with it. But on a skewed tree, a tree that is basically a long chain, the height is n. So you """
            """get n passes of n work: order n squared. With a hundred thousand nodes, that is ten billion operations. That is """
            """the sentence that ends the brute force.""")
seg(sid, 1, """But here is the more useful way to feel it, and this is a habit worth building. Ask yourself: am I recomputing """
            """something that never changed? Between pass one and pass two, the tree did not grow. The nodes did not move. The """
            """answer for node four, that it belongs in the first list, was already determined the moment we saw the tree. So """
            """why are we rediscovering facts? Whenever you catch yourself re-deriving a fact that was fixed all along, there """
            """is usually a single pass hiding underneath.""")

# ---------------------------------------------------------------- 6. key observation
D = Diagram('The key observation')
tree(D, TREE, EDGES, x=560, y=120, step=0)
D.label(1220, 140, 'Which pass removes a node?', kind='shared', step=0, w=620, size='m')
D.label(1220, 220, 'Node 4 → pass 1\nNode 5 → pass 1\nNode 3 → pass 1', kind='ok', step=1, w=620, size='m')
D.label(1220, 400, 'Node 2 → pass 2\n(it waits for its children)', kind='ok', step=2, w=620, size='m')
D.label(1220, 540, 'Node 1 → pass 3', kind='ok', step=3, w=620, size='m')
D.label(120, 690, 'A node is removed in the pass equal to its **height above the deepest leaf below it**.',
        kind='dp', step=4, w=1700, size='l', align='center')
D.label(120, 760, 'Leaf = height 0 → pass 1.  A node = 1 + max(height of children).', kind='info', step=5, w=1700, size='m', align='center')
sid = D.build()
seg(sid, 0, """So let us ask a different question. Not which nodes are leaves now, but: for each node, which pass removes it? """
            """Answer that once per node and we never need a second pass.""")
seg(sid, 1, """Nodes four, five and three go in pass one. What do they have in common? Nothing below them. They are at the bottom.""")
seg(sid, 2, """Node two goes in pass two. Why does it have to wait? Because it has children, and a node cannot be a leaf until """
            """every child underneath it is gone. So node two waits exactly one pass longer than its deepest child.""")
seg(sid, 3, """And node one goes in pass three, one later than node two, for exactly the same reason.""")
seg(sid, 4, """There is the observation, and I want you to hear it as a sentence you could say in an interview. A node is removed """
            """in the pass that matches its height above the deepest leaf underneath it. Not its depth from the root. Its """
            """height from the bottom.""")
seg(sid, 5, """And height from the bottom has a beautifully simple definition. A leaf has height zero. Any other node has height """
            """one plus the maximum height of its children. That is a recursive definition, which means it is a single """
            """post-order traversal. We just turned repeated stripping into one pass.""")

# ---------------------------------------------------------------- 7. pattern chain
sid = steps_list('Problem → observation → pattern → structure → algorithm', [
 (0, '**Problem:** repeatedly strip leaves and record each layer', 'info'),
 (0, '**Observation:** a node\'s layer is fixed by the tree — height from the bottom', 'shared'),
 (1, '**Pattern:** post-order accumulation — each call returns a summary of its subtree', 'dp'),
 (1, '**Structure:** a list of lists, indexed by that height', 'ok'),
 (2, '**Algorithm:** one DFS; append the node into `result[height]`; return height to the parent', 'ok'),
 (2, '**Complexity:** O(n) time, O(h) stack', 'info'),
])
seg(sid, 0, """Let me show you the chain, because this is the shape I want you to reuse. Problem: strip leaves layer by layer. """
            """Observation: the layer a node lands in was fixed the moment the tree existed, and it equals height from the bottom.""")
seg(sid, 1, """Pattern: post-order accumulation. Every recursive call returns a small summary about its subtree, and the parent """
            """combines those summaries into its own. Structure: a list of lists, where the index is that height.""")
seg(sid, 2, """Algorithm: one depth-first walk. Compute the height of each node after its children, append the node's value into """
            """the list at that index, and return the height upward. Time, order n, because every node is touched once. Space, """
            """order h for the recursion stack. When you can say that chain out loud, you own the problem — and you can rebuild """
            """the code from it even if you have forgotten it.""")

# ---------------------------------------------------------------- 8. walkthrough
D = Diagram('Walkthrough: one post-order pass')
tree(D, TREE, EDGES, x=560, y=120, step=0, hls={'n4': 1, 'n5': 2, 'n2': 3, 'n3': 4, 'n1': 5})
D.label(1220, 150, 'height(4) = 0 → result[0] = [4]', kind='ok', step=1, w=640, size='m')
D.label(1220, 230, 'height(5) = 0 → result[0] = [4, 5]', kind='ok', step=2, w=640, size='m')
D.label(1220, 310, 'height(2) = 1 + max(0, 0) = 1\n→ result[1] = [2]', kind='ok', step=3, w=640, size='m')
D.label(1220, 440, 'height(3) = 0 → result[0] = [4, 5, 3]', kind='ok', step=4, w=640, size='m')
D.label(1220, 530, 'height(1) = 1 + max(1, 0) = 2\n→ result[2] = [1]', kind='ok', step=5, w=640, size='m')
D.label(120, 700, 'Result: **[[4, 5, 3], [2], [1]]** — identical to the three passes, in one walk.',
        kind='dp', step=6, w=1700, size='l', align='center')
sid = D.build()
seg(sid, 0, """Now let us run it. Post-order means children before parent, so the walk goes down the left side first.""")
seg(sid, 1, """We reach node four. No children, so its height is zero. The list at index zero does not exist yet, so we create it, """
            """and we put four in it. Then we return zero to the parent.""")
seg(sid, 2, """Node five, same story. Height zero, so it joins the list at index zero, which now holds four and five.""")
seg(sid, 3, """Back up at node two. Both of its children returned zero, so node two's height is one plus zero, which is one. """
            """Index one does not exist yet, so we create it and put two in it. Node two returns one to its parent.""")
seg(sid, 4, """Now the right side. Node three has no children, so height zero, and it joins the list at index zero, which becomes """
            """four, five, three. Notice the order inside a list depends on traversal order, and the question does not care — """
            """but say that out loud, because an interviewer may ask whether the order within a layer matters.""")
seg(sid, 5, """Finally node one. Its children returned one and zero, so its height is one plus the max of those, which is two. """
            """Index two gets node one.""")
seg(sid, 6, """And the result is four five three, then two, then one. The same answer the three passes produced, from a single """
            """walk of the tree, with no deletion anywhere.""")

# ---------------------------------------------------------------- 9. edge cases
sid = cards('Edge cases — say these before you are asked', [
 (0, 'Null root', 'Return an empty list. Decide the height convention: null = −1 so a leaf is 0.', 'info'),
 (0, 'Single node', 'One layer, one value. Trivial, but it catches an off-by-one in the index.', 'info'),
 (1, 'Skewed tree', 'n layers, recursion depth n. At 10⁵ nodes this stack-overflows — offer the explicit stack.', 'deny'),
 (1, 'Duplicate values', 'Fine. You collect values, not identities — unless asked to return nodes.', 'shared'),
 (2, 'Order within a layer', 'Determined by traversal order; ask whether it matters.', 'shared'),
 (2, 'Very wide tree', 'Memory is the output itself, O(n). Nothing else grows.', 'info'),
], cols=2)
seg(sid, 0, """Before the code, the edge cases — and I want you to volunteer these in the interview rather than wait. Null root: """
            """return an empty list, and state your height convention, because there are two. I use null equals minus one, """
            """which makes a leaf zero, and that keeps the index arithmetic clean. Single node: trivial, but it is exactly """
            """where an off-by-one in the index shows up.""")
seg(sid, 1, """Skewed tree. This is the one that matters. If the tree is a chain of a hundred thousand nodes, your recursion is a """
            """hundred thousand frames deep and you will blow the stack. Say so, and offer the iterative version with an """
            """explicit stack. Duplicate values are fine because we collect values — but ask whether they want nodes instead.""")
seg(sid, 2, """And the order of values within one layer. That falls out of the traversal order. The question does not specify it, """
            """so name the assumption. Asking a question like that costs you five seconds and signals care.""")

# ---------------------------------------------------------------- 10. code
CODE = '''public IList<IList<int>> FindLeaves(TreeNode root) {
    var result = new List<IList<int>>();
    Height(root, result);
    return result;
}

// Returns the height of this node above the deepest leaf below it.
// Convention: null = -1, so a leaf is 0.
private int Height(TreeNode node, List<IList<int>> result) {
    if (node == null) return -1;

    int left  = Height(node.left,  result);
    int right = Height(node.right, result);
    int height = 1 + Math.Max(left, right);

    if (result.Count == height) result.Add(new List<int>());
    result[height].Add(node.val);

    return height;
}'''
code_slide('The C# implementation', CODE, [
 ('1-5', """Here is the whole thing, and it is shorter than the explanation, which is usually a good sign. The public method """
           """does almost nothing: it makes the result list, kicks off the recursion, and returns. I keep the public surface """
           """clean and put the work in a private helper — in an interview that reads as someone who writes code other people """
           """maintain."""),
 ('7-9', """The comment above the helper is doing real work. It states what the function returns and the convention I chose. """
          """If an interviewer reads only one thing in your code, let it be a line that says what a function returns."""),
 ('10', """Base case. A null child has height minus one. That is the choice that makes a leaf come out at zero, which is the """
          """index we want for the first layer."""),
 ('12-14', """Then the two recursive calls, children first — that is what makes it post-order — and the node's own height is one """
             """plus the larger of the two. This single line is the observation we derived, written down."""),
 ('16-17', """Now the accumulation. If the result list does not yet have an entry at this height, we create it. Because we go """
             """bottom-up, heights arrive in order, so a simple count check is enough; we never need to resize by a jump. Then """
             """we add the value into its layer."""),
 ('19', """And we return the height so the parent can compute its own. Notice what is not here: no deletion, no second pass, no """
          """visited set. The recursion carries all the state we need."""),
])

# ---------------------------------------------------------------- 11. complexity
sid = table('Complexity — and how to say it', ['', 'Answer', 'What to say out loud'], [
 (0, ['Time', '**O(n)**', 'Every node is visited exactly once; the work per node is constant'], [None, 'ok', None]),
 (1, ['Space', '**O(h)** stack', 'Height of the tree — O(log n) balanced, O(n) skewed'], [None, 'shared', None]),
 (2, ['Output', 'O(n)', 'The result holds every value once; usually excluded, but say so'], [None, 'info', None]),
 (3, ['Brute force', 'O(n²) worst case', 'One O(n) pass per layer, and layers equal height'], [None, 'deny', None]),
], widths=[16, 26, 58])
seg(sid, 0, """Complexity. Time is order n, and the sentence to use is: every node is visited exactly once and does constant """
            """work. Do not just say linear — say why it is linear.""")
seg(sid, 1, """Space is order h for the recursion stack, where h is the height. Balanced, that is log n. Skewed, it is n. """
            """Saying both shows you know the stack is not free.""")
seg(sid, 2, """The output itself is order n. Most interviewers exclude output size, but say which convention you are using rather """
            """than leaving it ambiguous.""")
seg(sid, 3, """And keep the brute force number in your pocket: order n squared in the worst case. The contrast is what makes your """
            """optimisation land.""")

# ---------------------------------------------------------------- 12. follow-ups
followups(
 ['"Return the nodes, not the values" — trivial change, but it forces you to talk about identity',
  '"Do it iteratively" — explicit stack, for a 10⁵-deep chain',
  '"What if it is an n-ary tree?" — max over all children instead of two'],
 ['"Now the tree does not fit in memory" — stream by subtree, or partition and merge heights at boundaries',
  '"Do it without recursion and without extra space" — Morris-style threading, and say what it costs in clarity',
  '"Could you compute it during construction?" — maintain height on insert, amortising the whole problem away'],
 """Follow-ups. These first three are the ones actually reported or obviously adjacent, and you should have them ready. """
 """Return nodes instead of values, which is a one-word change but makes you talk about identity versus value. Do it """
 """iteratively, because of that skewed-tree stack problem you already raised. And the n-ary version, where instead of max """
 """of left and right you take the max over all children — same line, different loop.""",
 """These are the staff-level extensions. What if the tree does not fit in memory? Now you are streaming subtrees, or """
 """partitioning the tree and reconciling heights at the boundaries. What if you cannot use recursion or extra space? That """
 """is Morris traversal territory, and the right answer includes what it costs: the code becomes much harder to read for a """
 """constant-factor memory win, which is usually a bad trade in production. And the nicest one: could you maintain the """
 """height as nodes are inserted? Then this whole problem becomes a lookup. Interviewers love that move because it shows you """
 """think about where the work belongs, not just how to do it.""")

# ---------------------------------------------------------------- 13. how they modify it
sid = table('How the interviewer may modify the question', ['They say', 'What is actually changing', 'Your move'], [
 (0, ['"Only return the last layer"', 'You no longer need the lists at all', 'Track max height; return the nodes at it'], None),
 (1, ['"Return layer counts, not values"', 'Output shrinks to O(h)', 'Keep an int array; drop the lists'], None),
 (2, ['"The tree is enormous and mostly a chain"', 'Recursion depth, not time', 'Explicit stack with an iterative post-order'], None),
 (3, ['"Nodes can have a parent pointer"', 'You could go bottom-up from leaves', 'BFS from leaves inward — same layers, different walk'], None),
 (4, ['"Do it for a forest"', 'Multiple roots', 'Same function per root; merge the layer lists'], None),
], widths=[30, 32, 38])
seg(sid, 0, """Interviewers rarely ask a second, unrelated question. They modify the one you just solved, and they are watching """
            """whether your solution bends or breaks. Only return the last layer? Then you do not need the lists at all — just """
            """track the maximum height.""")
seg(sid, 1, """Return counts instead of values? Your output collapses to an array of integers, size h. Notice how each of these """
            """simplifies your code rather than complicating it. That is a sign your structure was right.""")
seg(sid, 2, """The tree is enormous and mostly a chain? Now the problem is recursion depth, not time — and you already flagged """
            """that in edge cases, so you just collect on a promise you made earlier. That is a very good feeling in an interview.""")
seg(sid, 3, """Parent pointers available? Then you could start at the leaves and walk inward, which is a genuinely different """
            """algorithm — a BFS from the boundary. Worth saying even if you do not code it.""")
seg(sid, 4, """And a forest instead of a tree? Run the same function per root and merge the layer lists. If your answer needs """
            """redesigning for that, your abstraction was too tight.""")

# ---------------------------------------------------------------- 14. what to say
interview_script([
 '"Let me restate it: repeatedly strip leaves, and record each stripped layer in order. Should the order within a layer matter?"',
 '"The obvious approach is to simulate it: find leaves, remove, repeat. That is O(n) per pass and up to n passes, so O(n²) on a chain."',
 '"But nothing about the tree changes between passes — so each node\'s layer is fixed from the start. Let me find what fixes it."',
 '"A node can only be stripped after everything below it, so its layer is its height above the deepest leaf below."',
 '"That gives me one post-order pass: height is 1 plus the max of the children, and I append the node to result[height]."',
 '"O(n) time, O(h) stack. On a skewed tree the stack is O(n), so if that is a concern I would switch to an explicit stack."',
 '"Let me test it on a single node, then on a chain of three, then on the example."',
], [
 """And finally, the script. This is what you actually say, in order, and I want you to practise it out loud rather than """
 """read it. You start by restating the problem and asking one clarifying question. One is enough here — the order within a """
 """layer — and it proves you are listening rather than pattern matching.""",
 """Then you name the brute force and price it immediately. Do not apologise for it. Naming a working solution and its cost """
 """in one breath is what a senior engineer does. Then you make the pivot explicit: nothing changes between passes, so the """
 """answer must be fixed from the start.""",
 """Then the observation, then the algorithm in one sentence, then the complexity with the honest caveat about the stack. """
 """And then — this is the part people skip — you test out loud on the small cases before you say you are done. Single node, """
 """short chain, the example. If you do nothing else differently after this lesson, do that.""",
])

# ---------------------------------------------------------------- 15. recap
sid = statement('Take this with you', 'A node\'s layer is its height above the deepest leaf below it.',
                'Post-order accumulation: return a summary upward, combine it in the parent. Three more lessons in this chapter are the same move.',
                kind='ok')
seg(sid, 0, """One sentence to take with you. A node's layer is its height above the deepest leaf below it.""")
seg(sid, 1, """And the transferable pattern is post-order accumulation: each call returns a small summary, the parent combines """
            """them. In the next lesson we use exactly that move on a problem that looks completely different — turning a tree """
            """upside down — and you will see the same shape appear about two minutes in. See you there.""")
