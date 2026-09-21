# -*- coding: utf-8 -*-
"""Chapter 2 recap — trees and recursion."""
from lib import *

lesson_header('2.R', 'Chapter 2 recap: trees and recursion', 'Recap · templates · mini mock',
              'Highest', '9 of the reported LinkedIn questions are tree problems', '2026', 'High', 13,
              """Chapter two recap. This is the revision lesson — the one to replay the morning of the interview rather than """
              """the morning you start studying. Seven parts: the pattern in one page, the recognition checklist, the mistakes """
              """that actually cost people offers, the C# templates worth having in your fingers, the reported questions """
              """ranked, a five-minute rapid revision, and a mini mock at the end. Nothing new is taught here. Everything here """
              """was earned in lessons one through four.""")

# ------------------------------------------------------------------ 1. pattern
sid = beat('Pattern summary', 'The chapter in one page',
           '<div class="bigidea">Every tree problem in this chapter was solved by answering one question: '
           '<b>what does each recursive call return?</b></div>'
           '<div style="margin-top:26px;font-size:30px;line-height:1.7">'
           'Once the return value is chosen, the body is forced: combine the children\'s returns, do the local work, '
           'return your own. There is no cleverness left to find.</div>',
           """One page. Every tree problem in this chapter came down to a single question: what does each recursive call """
           """return? Not what does the function do — what does it hand back. Once you have chosen that, the body of the """
           """function is essentially forced. Combine what the children returned, do the local work, return your own value. """
           """There is no cleverness left to find, which is exactly why this is a good habit rather than a trick.""", step=0)
seg(sid, 1, """And notice what that gives you in an interview: you can say the return value out loud before you write anything, """
            """and the interviewer immediately knows whether you are on a path that works.""")

sid = table('The four problems, and what each call returned',
 ['Problem', 'Each call returns', 'Why that choice', 'Reported'],
 [(0, ['Find Leaves', 'the node&rsquo;s **height**', 'Height <b>is</b> the output bucket &mdash; no second pass needed', 'Yes &times;2'], None),
  (1, ['Binary Tree Upside Down', 'the **new root** of the flipped subtree', 'Rewiring is done by the parent; the root comes from the bottom', 'Yes'], None),
  (2, ['Keyed n-ary merge', 'a **newly built node**', 'Inputs stay immutable; a shared child would alias', 'Yes'], None),
  (3, ['Compact tree', 'the **possibly-new subtree root**, or null', 'Makes the root case ordinary instead of special', 'Yes'], None)],
 widths=[26, 26, 34, 14])
seg(sid, 0, """Here they are side by side. Find Leaves returned the node's height — and the insight was that the height is the """
            """output bucket, so there is no second pass at all.""")
seg(sid, 1, """Upside Down returned the new root of the flipped subtree, because the rewiring is done by the parent, and the """
            """final root comes from the deepest left node.""")
seg(sid, 2, """The keyed merge returned a freshly built node, because the inputs must stay untouched and sharing a child would """
            """alias two trees into one.""")
seg(sid, 3, """And compaction returned the possibly-new subtree root, which is the move that turned the root special case — the """
            """one the reporting candidate missed — into an ordinary case. Four problems, four different return values, one """
            """habit.""")

# ------------------------------------------------------------------ 2. recognition
sid = steps_list('Recognition checklist &mdash; what in the wording tells you which shape',
 [(0, '&ldquo;collect / group / by distance from the leaves&rdquo; &rarr; **return a height**, bucket on the way up', 'ok'),
  (0, '&ldquo;reverse / flip / re-root&rdquo; &rarr; **return the new root**; draw three nodes before coding', 'ok'),
  (1, '&ldquo;merge / combine two trees&rdquo; &rarr; **build new nodes**; ask about mutability and about duplicate keys', 'ok'),
  (1, '&ldquo;children are unordered / keyed&rdquo; &rarr; a **dictionary keyed by child key**, not index-by-index', 'ok'),
  (2, '&ldquo;prune / collapse / compact&rdquo; &rarr; **bottom-up, return the possibly-new node**, null means gone', 'ok'),
  (2, '&ldquo;level / depth / weight by depth&rdquo; &rarr; **BFS with a frozen level size**, or DFS with a depth argument', 'ok'),
  (3, 'Deep and skinny input mentioned at all &rarr; say &ldquo;recursion depth&rdquo; **before** they ask', 'shared')],
 numbered=False)
seg(sid, 0, """The recognition checklist. These are the phrases and what they should trigger. Collect or group by distance from """
            """the leaves means return a height and bucket on the way up. Reverse, flip or re-root means return the new root — """
            """and draw three nodes before you write anything, because nobody does that transformation correctly in their head.""")
seg(sid, 1, """Merge or combine two trees means build new nodes, and ask about mutability and duplicate keys before you start. """
            """If the children are described as unordered or keyed, you want a dictionary keyed by the child key, not a """
            """position-by-position walk — that was the whole trap in lesson three.""")
seg(sid, 2, """Prune, collapse or compact means bottom-up with a possibly-new node returned, where null means the subtree """
            """disappeared. Anything about levels, depths or weight-by-depth means breadth-first with a frozen level size, or """
            """depth-first with a depth argument.""")
seg(sid, 3, """And the last one is a habit rather than a pattern. If the problem mentions deep or skinny input at all, say """
            """"recursion depth" before they do. It costs five seconds and it moves you from candidate who writes recursion to """
            """engineer who knows where recursion breaks.""")

# ------------------------------------------------------------------ 3. mistakes
sid = cards('The mistakes that actually cost people', [
 (0, 'Coding before the return value is chosen', 'The single most common failure. You end up with a function that does everything and returns nothing useful.', 'deny'),
 (0, 'Forgetting the root case', 'The reported compact-tree candidate missed an edge case. Return the new root and the root stops being special.', 'deny'),
 (1, 'Mutating an input that was meant to be immutable', 'Never announced, always penalised. Ask, then state your choice out loud.', 'deny'),
 (1, 'Assuming children are ordered', 'The keyed merge is a correctness bug, not a style issue &mdash; and it is silent on symmetric examples.', 'deny'),
 (2, 'Not freezing the level size in BFS', 'Your level boundaries dissolve as you enqueue children. One line, easy to forget under pressure.', 'deny'),
 (2, 'Silence while thinking', 'The interviewer cannot score an empty room. Narrate the shape even before you have the answer.', 'shared'),
], cols=2)
seg(sid, 0, """Now the mistakes, and these are ranked by how much they cost. Number one: coding before you have chosen the return """
            """value. You end up with a function that does a bit of everything and returns nothing useful, and then you debug """
            """your own design live. Number two: forgetting the root case — the candidate who reported the compact tree """
            """question said exactly this, and returning the new root makes it disappear.""")
seg(sid, 1, """Mutating an input that was supposed to stay untouched. Nobody announces this and everybody notices it. And """
            """assuming children are ordered, which in the keyed merge is a genuine correctness bug that stays hidden on any """
            """symmetric example you happen to try.""")
seg(sid, 2, """Forgetting to freeze the level size in breadth-first search — one line, and it is the line people drop under """
            """pressure. And the last one is not about trees at all: silence. The interviewer cannot score an empty room. """
            """Narrate the shape of your thinking even before you have an answer.""")

# ------------------------------------------------------------------ 4. templates
T1 = '''// TEMPLATE A - bottom-up value: each call returns something the parent needs.
int Walk(TreeNode node, List<IList<int>> buckets) {
    if (node is null) return -1;                        // empty: one below a leaf

    int h = 1 + Math.Max(Walk(node.left, buckets),      // children first
                         Walk(node.right, buckets));

    while (buckets.Count <= h) buckets.Add(new List<int>());
    buckets[h].Add(node.val);                           // local work, using the children's answer
    return h;                                           // hand the parent what it needs
}'''
code_slide('Template A &mdash; bottom-up value (Find Leaves, heights, diameters, pruning)', T1, [
 (None, """Template A, and it covers more problems than any other shape in this chapter. Base case returns the identity value """
          """— here minus one, because one below a leaf makes a leaf's height zero. Then recurse into both children, combine """
          """their answers into your own, do the local work using that answer, and return it upward. Find Leaves, tree height, """
          """diameter, and every pruning problem is this template with a different combine step."""),
])

T2 = '''// TEMPLATE B - structural rewrite: each call returns the (possibly new) subtree root.
TreeNode Rebuild(TreeNode node) {
    if (node is null || node.left is null) return node;   // the node that becomes the new root

    TreeNode newRoot = Rebuild(node.left);                // recurse FIRST, before rewiring

    node.left.left  = node.right;                         // the parent does the rewiring
    node.left.right = node;
    node.left = node.right = null;                        // and cuts the old links

    return newRoot;                                       // the same root travels all the way up
}'''
code_slide('Template B &mdash; structural rewrite (Upside Down, re-rooting, compaction)', T2, [
 (None, """Template B is the structural rewrite. Two things to notice, because they are the two things people get wrong. """
          """First, recurse before rewiring — if you rewire first you have destroyed the links you were about to recurse """
          """through. Second, the rewiring is done by the parent on its children, and the new root found at the bottom travels """
          """unchanged all the way up. Upside Down, re-rooting and compaction are all this shape."""),
])

T3 = '''// TEMPLATE C - two-tree merge into fresh nodes, children keyed not ordered.
Node Merge(Node a, Node b) {
    if (a is null && b is null) return null;
    var node = new Node(Key(a ?? b), Val(a) + Val(b));    // build, never mutate

    var kids = new Dictionary<string, (Node A, Node B)>();
    foreach (var c in a?.Children ?? Empty) kids[c.Key] = (c, null);
    foreach (var c in b?.Children ?? Empty)
        kids[c.Key] = (kids.TryGetValue(c.Key, out var e) ? e.A : null, c);

    foreach (var (key, pair) in kids)                      // order: ask, then sort if asked
        node.Children.Add(Merge(pair.A, pair.B));
    return node;
}'''
code_slide('Template C &mdash; keyed merge of two structures', T3, [
 (None, """And template C, the keyed merge. Build a new node rather than mutating either input. Then the part that is easy to """
          """miss under pressure: collect the children of both sides into a dictionary keyed by child key, pairing them up, """
          """and recurse once per key. That handles a child present on one side only, and it does not depend on the two trees """
          """listing their children in the same order. If output order matters, ask, and then sort deliberately."""),
])

# ------------------------------------------------------------------ 5. top reported
sid = table('The reported tree questions, ranked by what I would revise first',
 ['#', 'Question', 'Evidence', 'Revise'],
 [(0, ['1', 'Find Leaves of Binary Tree', 'Your own list + LinkedIn tag, repeatedly reported', '**First**'], None),
  (0, ['2', 'Binary Tree Upside Down', 'Your own list + a phone-screen write-up', '**First**'], None),
  (1, ['3', 'Merge two binary trees / keyed n-ary merge', 'Your own list, with the n-ary keyed wording', 'Second'], None),
  (1, ['4', 'Compact tree from a given tree', 'Phone-screen write-up; reporter missed an edge case', 'Second'], None),
  (2, ['5', 'Nested List Weight Sum II', 'LinkedIn tagged set; nested-structure walk reported 2026', 'Third'], None),
  (2, ['&mdash;', 'Tree diameter, LCA, serialize/deserialize', 'Not reported for LinkedIn &mdash; general preparation', 'If time'], 'dim')],
 widths=[6, 44, 38, 12])
seg(sid, 0, """The reported questions, ranked by what I would revise first. Find Leaves and Binary Tree Upside Down are top, """
            """because they are on your own list and on the tagged set and they have been reported more than once.""")
seg(sid, 1, """Then the keyed merge and the compact tree, both from first-hand write-ups.""")
seg(sid, 2, """Then Nested List Weight Sum Two. And the last row matters as much as the others: diameter, lowest common """
            """ancestor and serialise-deserialise are not reported for LinkedIn. They are general preparation. I am marking """
            """them that way deliberately, because a revision list that quietly promotes unreported questions to reported """
            """ones is worse than no list.""")

# ------------------------------------------------------------------ 6. rapid revision
sid = steps_list('Five-minute rapid revision &mdash; say each of these out loud',
 [(0, 'What does each call return? &mdash; height &middot; new root &middot; fresh node &middot; possibly-new subtree', 'ok'),
  (0, 'Bottom-up or top-down? Pruning and heights are bottom-up. Depth weighting is top-down.', 'ok'),
  (1, 'Am I allowed to mutate the input? If unsure, ask; if you cannot ask, build and say so.', 'ok'),
  (1, 'Are the children ordered? If keyed, use a dictionary.', 'ok'),
  (2, 'Base case: null, single node, one-sided chain.', 'shared'),
  (2, 'Recursion depth on a 10&#8309; chain &mdash; name it, offer the explicit stack.', 'shared'),
  (3, 'Complexity: O(n) time, O(h) stack &mdash; and h is n in the worst case.', 'info'),
  (3, 'Test: idempotence, invariants, a brute-force oracle on small trees.', 'info')],
 numbered=True)
seg(sid, 0, """Five-minute rapid revision. These are meant to be said out loud, not read. What does each call return. Bottom-up """
            """or top-down — pruning and heights go up, depth weighting comes down.""")
seg(sid, 1, """Am I allowed to mutate the input. Are the children ordered.""")
seg(sid, 2, """Base cases: null, single node, one-sided chain. Recursion depth on a hundred-thousand-node chain, named before """
            """they ask, with the explicit stack offered.""")
seg(sid, 3, """Complexity, order n time and order h stack, remembering that h is n in the worst case. And the testing line: """
            """idempotence, invariants, and a brute-force oracle on small trees. Eight sentences. If you can say all eight """
            """cold, this chapter is revised.""")

# ------------------------------------------------------------------ 7. mini mock
sid = beat('Mini mock &mdash; 12 minutes', 'Pause here and actually do it',
           '<div class="qwrap"><div class="qlabel">The interviewer asks</div>'
           '<div class="qtext" style="font-size:36px">&ldquo;Given a binary tree, return the values of the nodes that have '
           'exactly one child, grouped by how far they are from the nearest leaf below them. You may not modify the '
           'tree.&rdquo;</div></div>',
           """And a mini mock. This is a question you have not seen, deliberately assembled out of this chapter's parts. Given """
           """a binary tree, return the values of nodes that have exactly one child, grouped by how far they are from the """
           """nearest leaf below them, and you may not modify the tree. Twelve minutes. Pause the video, talk out loud, write """
           """real C sharp. I will grade it when you come back.""", kicker='Chapter 2 recap')
think('Twelve minutes. Clarify, choose the return value, code it, price it, test it.', 45,
      """Off you go. And the order matters: clarify, choose the return value, code, price, test. If you jump to code you will """
      """be doing this chapter's number one mistake in the lesson that just told you not to.""",
      """Right. Here is what I was looking for.""")

sid = cards('How I would grade that', [
 (0, '&ldquo;Nearest leaf below&rdquo; is not height', 'Height is the <b>longest</b> path down; this asks for the <b>shortest</b>. So the combine step is Min, not Max &mdash; and a one-child node must ignore its missing side rather than taking min with &minus;1.', 'deny'),
 (1, 'Return value: min distance to a leaf', 'Template A with two changes: Min instead of Max, and skip the null child when exactly one child exists.', 'ok'),
 (1, 'Filter, do not restructure', 'Only bucket the node when exactly one child is non-null. Everything else still returns its distance.', 'ok'),
 (2, 'You may not modify the tree', 'So no marking, no nulling out. Buckets are the only state. Say this back to them.', 'shared'),
 (2, 'Edge cases to name unprompted', 'empty tree; single node (no one-child nodes at all); a pure chain (<i>every</i> node qualifies); deep chain &rarr; stack.', 'shared'),
 (3, 'Complexity', 'O(n) time, O(h) stack, O(n) output. One pass &mdash; no second traversal needed.', 'info'),
], cols=2)
seg(sid, 0, """First, the trap, and it is a real one: nearest leaf below is not the height. Height is the longest path down; this """
            """asks for the shortest. So your combine step is Min, not Max. And there is a second-order catch — a node with """
            """exactly one child must ignore its missing side entirely, because taking the minimum with the empty side's minus """
            """one would give you nonsense. If you spotted that, you did better than most.""")
seg(sid, 1, """The return value is the minimum distance to a leaf below. That is template A with two changes. And notice this is """
            """a filter, not a restructure: you bucket the node only when exactly one child is non-null, but every node still """
            """returns its distance, because its parent needs it.""")
seg(sid, 2, """You may not modify the tree, so no marking and no nulling out — the buckets are your only state, and saying that """
            """constraint back to them is free credit. Then the edge cases, named before they ask: empty tree, single node """
            """where nothing qualifies at all, a pure chain where every node qualifies, and a deep chain for the stack.""")
seg(sid, 3, """Order n time, order h stack, order n output, in one pass. If you got there talking out loud, this chapter is """
            """done and you are ready for graphs — which is chapter three, and where your own reported list gets denser than """
            """anywhere else.""")
