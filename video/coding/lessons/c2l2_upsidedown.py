# -*- coding: utf-8 -*-
"""Chapter 2, Lesson 2 — Binary Tree Upside Down."""
from lib import *

BEFORE = {'b1': (0, 0, 1), 'b2': (1, -0.9, 2), 'b3': (1, 0.9, 3), 'b4': (2, -1.5, 4), 'b5': (2, -0.35, 5)}
BEDGES = [('b1', 'b2'), ('b1', 'b3'), ('b2', 'b4'), ('b2', 'b5')]
AFTER = {'a4': (0, 0, 4), 'a5': (1, -0.9, 5), 'a2': (1, 0.9, 2), 'a3': (2, 0.35, 3), 'a1': (2, 1.5, 1)}
AEDGES = [('a4', 'a5'), ('a4', 'a2'), ('a2', 'a3'), ('a2', 'a1')]

lesson_header('2.2', 'Binary Tree Upside Down', 'Trees · pointer rewiring',
              'High', 'Your own list — twice, including a 0/1 right-child variant', '2026', 'High', 15,
              """Lesson two of chapter two. Binary Tree Upside Down. This one appears twice on your own list of past LinkedIn """
              """questions, once phrased around a right child that is either a leaf or empty, which is the standard form. Two """
              """appearances on a first-party list makes it one of the highest-signal tree problems in the whole course. And it """
              """is a different kind of difficulty from the last lesson. There is no clever insight to find here. This is pure """
              """pointer surgery, and the official pack says the Staff Coding module is scored on exactly that: pointers, edge """
              """cases and abstraction. So the skill I want to build in this lesson is not finding a trick. It is being """
              """systematic when three pointers have to move at once and any one of them can silently create a cycle.""")

# ---------------------------------------------------------------- question
D = Diagram('The transformation')
tree(D, BEFORE, BEDGES, x=440, y=180, step=0)
D.label(240, 560, '**Before**', kind='info', step=0, w=400, size='l', align='center')
tree(D, AFTER, AEDGES, x=1320, y=180, step=1)
D.label(1120, 560, '**After**', kind='ok', step=1, w=400, size='l', align='center')
D.label(120, 680, 'The old **left child** becomes the new root.  The old **root** becomes its right child.  '
                  'The old **right child** becomes its left child.', kind='dp', step=2, w=1700, size='m', align='center')
D.label(120, 760, 'Precondition: every right child is a **leaf or empty**.', kind='shared', step=3, w=1700, size='m', align='center')
sid = D.build()
seg(sid, 0, """Here is the question, and it is one of those where the picture does more work than the words. On the left is the """
            """tree we are given. One at the root, two and three below it, four and five under the two.""")
seg(sid, 1, """And on the right is what we have to produce. Notice that four, the deepest left node, is now the root. Look at it """
            """for a moment before I explain it, because the relationship is easier to see than to say.""")
seg(sid, 2, """Here is the rule in words. For any node, its old left child becomes the new root of that piece. The node itself """
            """becomes that child's right child. And the node's old right child becomes that child's left child. Three moves, """
            """happening at every level as you come back up.""")
seg(sid, 3, """And there is a precondition, which you should repeat back to the interviewer to make sure you heard it: every right """
            """child is either a leaf or empty. That is what makes the transformation well defined. If a right child had """
            """children of its own, the rule would not say where they go — and asking about that is a clarifying question worth """
            """the ten seconds.""")

# ---------------------------------------------------------------- think
think('Turn this binary tree upside down: the left child becomes the root, the old root becomes its right child, '
      'and the old right child becomes its left child.', 30,
      """Timer time. This problem rewards drawing before coding more than almost anything else in the course, so do not try to """
      """hold it in your head. Draw three levels on paper, pick one node, and write down what its new left, new right and new """
      """parent are. Pause here if you need longer than the timer.""",
      """Let us go. And if you found yourself confused about which pointer to move first, that is exactly the right confusion. """
      """The whole difficulty of this problem is ordering the assignments so you never lose a reference you still need.""")

# ---------------------------------------------------------------- naive attempt
sid = compare('The naive attempt, and why it goes wrong',
 ('"Just swap the pointers"', 'deny', 0, ['`root.left.left = root.right;`', '`root.left.right = root;`',
                                          'Looks done — and now the tree has a **cycle**',
                                          'A traversal never terminates']),
 ('What you forgot', 'shared', 1, ['`root.left` and `root.right` still point down',
                                   'So node 1 → node 2 → node 1', 'You must **null the old pointers**',
                                   'And you need the new root from the bottom, not the top']))
seg(sid, 0, """Most people\'s first attempt is two assignments. Set the left child\'s left to the old right child, set the left """
            """child\'s right to the node itself. And at that point the picture on the whiteboard looks correct, so it feels """
            """finished.""")
seg(sid, 1, """But it is not, and the failure is nasty because it is invisible. Node one still points down to node two, and now """
            """node two points to node one as well. You have made a cycle. Any traversal of that tree runs forever. So the """
            """rule to burn in is: when you rewire a node in, you must also null out the pointers it used to have. And the """
            """second thing you forgot is the return value. The new root is the deepest left node, which you do not have at the """
            """top of the call — you get it from the bottom.""")

# ---------------------------------------------------------------- key observation
D = Diagram('The key observation')
D.box('o1', 120, 140, 800, 150, 'The new root never changes', 'It is the deepest node down the left spine — found once, '
      'passed back up untouched', kind='ok', step=0)
D.box('o2', 120, 330, 800, 150, 'Each node rewires only its own child', 'So this is a recursion that returns the new root '
      'and rewires on the way back up', kind='dp', step=1)
D.box('o3', 120, 520, 800, 170, 'Order matters', 'Read what you need, write, then null. Do it in the wrong order and you '
      'lose a reference or build a cycle', kind='shared', step=2)
tree(D, BEFORE, BEDGES, x=1400, y=140, step=0, hls={'b4': '0,1,2'})
D.label(1120, 620, 'Node 4 — the deepest left node — is the answer, before any rewiring happens.',
        kind='ok', step=0, w=700, size='m', align='center')
sid = D.build()
seg(sid, 0, """So let us find the observations that make this writable. First: the new root never changes. It is the deepest node """
            """down the left spine — here, node four. You find it once, at the bottom of the recursion, and then you pass that """
            """same reference all the way back up without touching it. That single sentence removes most of the confusion, """
            """because it separates what we return from what we rewire.""")
seg(sid, 1, """Second: each node only rewires its own left child. Node one fixes node two. Node two fixes node four. Nobody """
            """reaches two levels down. That is what makes this a clean recursion: go down the left spine, and on the way back """
            """up, each frame does three assignments.""")
seg(sid, 2, """And third, the one that actually bites: order matters. Within a frame you must read the references you still """
            """need, then write the new ones, then null the old ones. Get that order wrong and you either lose a subtree or """
            """build a cycle. I am going to write the code in exactly that order and say it out loud as I do.""")

# ---------------------------------------------------------------- walkthrough
D = Diagram('Walkthrough: rewiring on the way back up')
tree(D, BEFORE, BEDGES, x=560, y=140, step=0, hls={'b4': 1, 'b2': '2,3', 'b1': 4})
D.label(1160, 160, '1 · Recurse down the left spine: 1 → 2 → 4', kind='info', step=1, w=700, size='m')
D.label(1160, 250, '2 · Node 4 has no left child → **it is the new root**', kind='ok', step=2, w=700, size='m')
D.label(1160, 350, '3 · Back in node 2\'s frame:\n   4.left = 5   ·   4.right = 2   ·   2.left = 2.right = null',
        kind='dp', step=3, w=700, size='m')
D.label(1160, 500, '4 · Back in node 1\'s frame:\n   2.left = 3   ·   2.right = 1   ·   1.left = 1.right = null',
        kind='dp', step=4, w=700, size='m')
D.label(120, 720, 'Return value all the way up: **node 4**, untouched since step 2.', kind='ok', step=5, w=1700, size='l', align='center')
sid = D.build()
seg(sid, 0, """Let us run it on our tree.""")
seg(sid, 1, """Step one. We recurse down the left spine. From one we go to two, from two we go to four. We do no work on the way """
            """down. That is worth saying out loud in the interview, because it tells the interviewer you know this is a """
            """post-order algorithm.""")
seg(sid, 2, """Step two. Node four has no left child, so the recursion stops and node four is the new root. We hold that """
            """reference and we will return it unchanged from every frame above.""")
seg(sid, 3, """Step three. We are now back inside node two's frame, and node two rewires its own left child, which is four. """
            """Four's new left becomes node five — that is two's old right child. Four's new right becomes node two itself. """
            """And then, critically, we null both of node two's own pointers, because everything that used to hang off two has """
            """been re-parented onto four.""")
seg(sid, 4, """Step four. Same three moves one level up. We are in node one's frame. Two's new left becomes three, two's new """
            """right becomes one, and one's own pointers are nulled. The tree is now the picture we wanted.""")
seg(sid, 5, """And through all of that, the return value has been node four, sitting untouched since step two. Two separate """
            """things travelling in opposite directions: the rewiring goes up level by level, the answer just rides along. """
            """Keeping those two ideas apart is what makes this code short.""")

# ---------------------------------------------------------------- code (recursive)
CODE1 = '''public TreeNode UpsideDownBinaryTree(TreeNode root) {
    // Base case: empty tree, or we have reached the deepest left node.
    if (root == null || root.left == null) return root;

    // Find the new root first. It comes from the bottom and never changes.
    TreeNode newRoot = UpsideDownBinaryTree(root.left);

    // Rewire this level: read, write, then null.
    root.left.left  = root.right;   // old right child becomes the new left
    root.left.right = root;         // this node becomes the new right

    root.left  = null;              // without these two lines we build a cycle
    root.right = null;

    return newRoot;                 // pass the same reference all the way up
}'''
code_slide('The recursive solution', CODE1, [
 ('1-3', """Here is the recursive version. The base case carries two conditions and it is worth pausing on. Root being null """
           """handles the empty tree. Root's left being null means we have hit the bottom of the left spine — that node is the """
           """new root, so we return it as is."""),
 ('5-6', """Then the recursive call, and notice we make it before we touch anything. We need the new root before we start """
           """destroying pointers. If you rewire first and recurse second, you have already broken the path you were about to """
           """walk down."""),
 ('8-10', """Now the three rewiring assignments, in the order I promised. Root dot left dot left becomes root dot right — the """
            """old right child moves to become the left child. Then root dot left dot right becomes root itself. Read both of """
            """those out loud as you type them; it is easy to transpose them and the compiler will not help you."""),
 ('11-13', """And here are the two lines people forget. We null this node's own pointers. If you skip these, node one still """
             """points at node two while node two points back at node one, and you have built a cycle that no test of the """
             """returned tree will notice until something traverses it."""),
 ('15', """Finally we return the new root — the same reference every frame returns, unchanged. The rewiring climbed the tree; """
          """the answer just came along for the ride."""),
])

# ---------------------------------------------------------------- iterative
CODE2 = '''public TreeNode UpsideDownIterative(TreeNode root) {
    TreeNode current = root, prev = null, prevRight = null;

    while (current != null) {
        TreeNode next = current.left;      // save before we overwrite anything

        current.left  = prevRight;         // the previous level's right child
        prevRight     = current.right;     // remember ours for the next level
        current.right = prev;              // the previous node becomes our right

        prev = current;                    // walk one step down the left spine
        current = next;
    }
    return prev;                            // the last node we touched is the new root
}'''
code_slide('The iterative version — O(1) space', CODE2, [
 ('1-2', """Now the version to have ready before they ask for it. Three references: where we are, the node we came from, and """
           """that node's old right child. That is the entire state we need."""),
 ('4-5', """We walk down the left spine. The first line inside the loop saves the next node before we overwrite the pointer """
           """we are standing on. Every in-place pointer algorithm starts with a line like this, and forgetting it is the """
           """single most common bug in linked-structure code."""),
 ('7-9', """Then the same three moves as the recursive version, just expressed with the carried state instead of the call """
           """stack. Our left becomes the previous level's right child. We remember our own right child for the next """
           """iteration. And our right becomes the node we came from."""),
 ('11-12', """Then we step down: the current node becomes the previous one, and we move to the saved next node."""),
 ('14', """When the loop ends, the last node we touched is the deepest left node — the new root. Same answer, order n time, """
          """but constant space instead of a recursion stack that is order n on this shape of tree. And that is exactly why """
          """this version matters here: the tree in this problem is a left spine, so the recursive version's stack is as deep """
          """as the tree is tall."""),
])

# ---------------------------------------------------------------- edges + complexity
sid = cards('Edge cases and the test you must run', [
 (0, 'Empty tree', 'Return null. One line, and it is the first thing a test hits.', 'info'),
 (0, 'Single node', 'Returns itself; no rewiring happens at all.', 'info'),
 (1, 'No right children anywhere', 'A pure left spine — the common shape. prevRight stays null throughout.', 'shared'),
 (1, 'Right child with children', 'Violates the precondition. Ask, do not assume.', 'deny'),
 (2, 'The cycle test', 'After transforming, traverse the result and assert it visits exactly n nodes and terminates.', 'ok'),
 (2, 'Deep tree', 'Recursive version is O(n) stack on a left spine — the reason to offer the iterative one.', 'deny'),
], cols=2)
seg(sid, 0, """Edge cases. Empty tree returns null, single node returns itself — both fall out of the base case, but say them """
            """because they are free points.""")
seg(sid, 1, """A tree with no right children anywhere is the common shape, and it is worth tracing because prevRight stays null """
            """the whole way through. And if the interviewer gives you a right child that has children of its own, the """
            """transformation is undefined — that is a clarifying question, not an assumption.""")
seg(sid, 2, """But this one is the test I really want you to name: after the transformation, traverse the result and assert that """
            """it terminates and visits exactly n nodes. That is the test that catches the cycle bug, and saying it out loud """
            """tells the interviewer you know what the dangerous failure mode is here. And then the depth point: on a left """
            """spine the recursive stack is order n, which is why you offer the iterative version.""")

sid = table('Complexity', ['Version', 'Time', 'Space', 'When to offer it'], [
 (0, ['Recursive', 'O(n)', 'O(h) — and h = n here', 'Write this first; it reads better'], [None, 'ok', 'deny', None]),
 (1, ['Iterative', 'O(n)', '**O(1)**', 'Offer immediately after, unprompted'], [None, 'ok', 'ok', None]),
], widths=[22, 16, 26, 36])
seg(sid, 0, """Complexity. Both versions visit each node once, so both are order n time. The recursive one costs order h in stack """
            """space, and because this tree is essentially a left spine, h is n.""")
seg(sid, 1, """The iterative one is constant space. My advice: write the recursive version first because it is easier to explain """
            """and easier to get right under pressure, then say — and I can do this iteratively in constant space if you want """
            """— and write it. Offering it before being asked is worth more than writing it first.""")

# ---------------------------------------------------------------- follow-ups
followups(
 ['"Do it iteratively" — the most likely next question, which is why we wrote it',
  '"Reverse the transformation" — the same three moves, mirrored',
  '"What if a right child has children?" — the precondition, made explicit'],
 ['"How would you test it?" — the terminates-and-visits-n test, plus a round trip through the reverse',
  '"Make it work on an n-ary tree" — the rule stops being well defined; say why rather than inventing one',
  '"Do it without recursion and without mutating the input" — now you are building a new tree, O(n) extra space, and that is the honest trade'],
 """Follow-ups. The iterative version is the one they actually ask for, and you have it. Reversing the transformation is the """
 """same three assignments with the roles swapped — worth sketching, not worth coding unless asked. And the precondition """
 """question is one you should have raised yourself at the start.""",
 """At staff level the interesting one is testing, because this problem has a silent failure mode. The answer is the """
 """traversal test plus a round trip: transform, reverse, and assert you get the original tree back. The n-ary version is a """
 """trap worth spotting — the rule does not generalise, and saying so is better than inventing a definition. And if they ask """
 """you not to mutate the input, be honest: you are building a new tree, that is order n extra space, and the in-place """
 """version existed precisely to avoid it.""")

# ---------------------------------------------------------------- what to say
interview_script([
 '"Let me restate the rule with a picture: left child becomes root, old root becomes its right child, old right child becomes its left."',
 '"Can I confirm the precondition — every right child is a leaf or empty?"',
 '"The new root is the deepest node down the left spine, and it never changes, so I will find it first and pass it up."',
 '"Each frame rewires only its own left child: three assignments, in read-write-null order."',
 '"The two lines people forget are nulling the old pointers — without them the tree has a cycle."',
 '"That is O(n) time and O(h) stack, and since this tree is a left spine, h is n. Let me also give you the O(1)-space iterative version."',
 '"To test it I would traverse the result and assert it terminates and visits exactly n nodes — that is the cycle check."',
], [
 """The script. Start by restating the rule while drawing it, then ask the precondition question. Those two moves take """
 """twenty seconds and they buy you the rest of the problem.""",
 """Then state the two structural facts before you write anything: the new root comes from the bottom and never changes, """
 """and each frame only touches its own left child. Then narrate the three assignments in read, write, null order — and """
 """explicitly call out the nulling as the part people forget. Saying that while you type it is a small flex and it is true.""",
 """Then complexity, with the honest note that h equals n here, and offer the iterative version before they ask. Finish on """
 """the test. If you say the traversal test out loud, you have told the interviewer that you know the dangerous bug in this """
 """problem and that you would catch it. That is the whole lesson.""",
])

sid = statement('Take this with you', 'Read what you need, write the new pointers, null the old ones.',
                'Every in-place pointer problem is that order. Next lesson: the same discipline, but the tree is n-ary and the merge rule is yours to define.',
                kind='ok')
seg(sid, 0, """One sentence to carry out of this lesson. Read what you still need, write the new pointers, then null the old ones.""")
seg(sid, 1, """That order is the whole of in-place pointer work, and it will come back in the linked-list drills later in the """
            """course. Next lesson we stay with trees but the shape changes: an n-ary tree, matched by key, where the merge """
            """rule itself is something you have to pin down with the interviewer before you write a line. See you there.""")
