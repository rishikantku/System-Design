# -*- coding: utf-8 -*-
"""Chapter 2, Lesson 4 — Nested List Weight Sum II, and the compact tree."""
from lib import *

lesson_header('2.4', 'Nested List Weight Sum II, and the compact tree', 'Nested structures · level accumulation',
              'High', 'Exponent 2026 phone screen + LeetCode tag + your list', '2026', 'High', 17,
              """Chapter two, lesson four — the last problem lesson of this chapter, and it is two problems, because they """
              """teach the same muscle. The first is Nested List Weight Sum Two, which is on the LinkedIn tagged set and whose """
              """cousin — a tree traversal over a nested object structure — was reported in a 2026 phone screen. The second is """
              """the compact tree question from your own list, from a LinkedIn phone-screen write-up where the candidate noted """
              """they missed one edge case. Two problems, one skill: handling structures whose shape you do not know in """
              """advance, and where the awkward cases are empty and the root.""")

# ---------------------------------------------------------------- problem 1
sid = beat('Question', 'Part one: Nested List Weight Sum II',
           '<div class="qwrap"><div class="qtext" style="font-size:36px;line-height:1.35">'
           'You are given a nested list of integers. The weight of an integer is <b>maxDepth − depth + 1</b>, '
           'so the <b>deepest</b> integers have weight 1 and the shallowest have the largest weight.<br><br>'
           'Return the sum of each integer multiplied by its weight.</div></div>',
           """Part one. A nested list of integers — lists inside lists, to any depth. In the first version of this problem, """
           """weight equals depth, so deeper means more. This is version two, where the weighting is inverted: the deepest """
           """integers have weight one and the shallowest have the largest weight. That inversion is the entire difficulty, """
           """because you cannot know an integer's weight until you have seen the whole structure.""")

think('Nested list, weight = maxDepth − depth + 1. Return the weighted sum. Can you do it in one pass?', 25,
      """Pause. Get the two-pass solution clear in your head first — find the maximum depth, then walk again applying the """
      """weight. That is a perfectly good answer. Then ask yourself the interesting question: is there something that """
      """accumulates naturally, level by level, that gives the inverse weighting without knowing maxDepth at all?""",
      """Let us go. And if you did not see the one-pass trick, do not worry — I want you to see the two-pass answer as """
      """legitimate, because saying it first is what a good candidate does.""")

sid = compare('Two ways, and both are worth saying',
 ('Two passes — say this first', 'info', 0, ['Pass 1: find maxDepth', 'Pass 2: add value × (maxDepth − depth + 1)',
                                             'O(n) twice, obviously correct', 'Nobody has ever been dinged for this']),
 ('One pass — the running-sum trick', 'ok', 1, ['BFS level by level', '`levelSum += values at this level`',
                                                '`total += levelSum` **after every level**',
                                                'Shallow values get added once more per remaining level']))
seg(sid, 0, """Two passes first. Walk the structure once to find the maximum depth, then walk again and add value times max """
            """depth minus depth plus one. Two linear passes. It is correct, it is obvious, and no interviewer has ever """
            """penalised a candidate for offering it — as long as you offer it and then keep thinking.""")
seg(sid, 1, """Now the one-pass version, and I want you to see why it works rather than memorise it. You do a breadth-first """
            """walk, level by level. You keep a running level sum, adding each level's integers into it as you go. And after """
            """every level, you add the current level sum into the total. So an integer at level one gets added into the """
            """total once for every level that still exists below it — which is exactly the inverse weighting, produced """
            """without ever computing maxDepth.""")

D = Diagram('Why the running sum produces inverse weights')
D.box('l1', 180, 160, 520, 110, 'Level 1: value a', 'levelSum = a → total += a', kind='info', step=0, small=True)
D.box('l2', 180, 300, 520, 110, 'Level 2: value b', 'levelSum = a+b → total += a+b', kind='info', step=1, small=True)
D.box('l3', 180, 440, 520, 110, 'Level 3: value c', 'levelSum = a+b+c → total += a+b+c', kind='info', step=2, small=True)
D.label(800, 180, 'total = 3a + 2b + c', kind='ok', step=3, w=900, size='l')
D.label(800, 280, 'a is at depth 1 with maxDepth 3 → weight 3 ✓\nb → weight 2 ✓\nc → weight 1 ✓',
        kind='ok', step=3, w=900, size='m')
D.label(800, 460, 'The weights fall out of **how many times** each value\nis still in the running sum.',
        kind='dp', step=4, w=900, size='m')
sid = D.build()
seg(sid, 0, """Let us prove it with three levels. Level one has value a. The level sum is a, and we add a to the total.""")
seg(sid, 1, """Level two has value b. The level sum is now a plus b, and we add that to the total. Notice a has now been counted """
            """twice.""")
seg(sid, 2, """Level three has value c. The level sum is a plus b plus c, added again.""")
seg(sid, 3, """Add it up: three a, two b, one c. And check against the definition — a is at depth one with a maximum depth of """
            """three, so its weight should be three. It is. b gets two, c gets one. Exactly right.""")
seg(sid, 4, """The weights are not computed anywhere. They emerge from how many times each value is still sitting in the """
            """running sum. That is a genuinely lovely trick, and being able to explain why it works — rather than just that """
            """it works — is what makes it worth showing.""")

CODE1 = '''public int DepthSumInverse(IList<NestedInteger> nestedList) {
    var queue = new Queue<NestedInteger>(nestedList);
    int levelSum = 0, total = 0;

    while (queue.Count > 0) {
        int size = queue.Count;             // freeze the level boundary before we add to it

        for (int i = 0; i < size; i++) {
            var item = queue.Dequeue();
            if (item.IsInteger()) levelSum += item.GetInteger();
            else foreach (var child in item.GetList()) queue.Enqueue(child);
        }

        total += levelSum;                  // every deeper level re-adds the shallow sums
    }
    return total;
}'''
code_slide('Part one: the C# implementation', CODE1, [
 ('1-3', """Seed the queue with the top-level items, and keep two accumulators: the running level sum and the total."""),
 ('5-6', """Freeze the level size before the inner loop. This is the standard level-order discipline — if you do not capture """
           """it, the loop will consume the children you just enqueued and your level boundaries dissolve."""),
 ('8-12', """For each item at this level: integers go into the level sum, lists get their children enqueued for the next """
            """level. Note that the level sum is never reset — that is deliberate, and it is the whole trick."""),
 ('14', """And after each level, add the running sum into the total. One line, and it produces the inverse weighting."""),
 ('16', """Return the total. Order n time, order of the widest level in space. If the interviewer asks for the original """
          """weighting instead, it is a depth counter and one multiplication — say that, because showing you can flip between """
          """the two versions proves you understood rather than memorised."""),
])

# ---------------------------------------------------------------- problem 2
sid = beat('Question', 'Part two: build a compact tree',
           '<div class="qwrap"><div class="qtext" style="font-size:36px;line-height:1.35">'
           'From a LinkedIn phone screen: <i>"form compact tree from a given tree; every node will have N nodes and at least '
           'a node can have 0–N nodes."</i><br><br>'
           'The reporter noted: <b>"did well in this round, missed one edge case."</b></div></div>',
           """Part two, and this one comes with a warning attached. Here is the question as the candidate wrote it up: form a """
           """compact tree from a given tree, where nodes can have between zero and N children. And their own note says: did """
           """well in this round, missed one edge case. That tells you something important — the algorithm was not the """
           """problem. The edge case was. So this part of the lesson is mostly about which edge case it probably was, and how """
           """to not be that candidate.""")

sid = cards('Before you write anything: pin down "compact"', [
 (0, 'Ask what compaction means', 'Collapse single-child chains? Merge identical labels? Drop empty subtrees? The wording is loose.', 'deny'),
 (0, 'Ask what a node carries', 'Does it have a payload, or is it purely structural? That decides what may be collapsed.', 'shared'),
 (1, 'Ask about child order', 'Preserved, or free? This changed everything in the last lesson.', 'shared'),
 (1, 'Ask what the output is', 'A new tree, or the input mutated in place?', 'info'),
 (2, 'Then restate it back', '"So: a node with exactly one child and no payload of its own is merged into that child." Get a yes.', 'ok'),
], cols=2)
seg(sid, 0, """So: before writing a line, pin down what compact means. Collapsing chains of single-child nodes? Merging children """
            """with identical labels? Dropping empty subtrees? The reported wording does not say, and each reading is a """
            """different algorithm.""")
seg(sid, 1, """Ask what a node carries, because a node with a payload cannot be silently collapsed away — you would lose data. """
            """Ask about child order, which mattered enormously in the last lesson. Ask whether you are returning a new tree """
            """or mutating.""")
seg(sid, 2, """And then restate it back as a single precise sentence and wait for the yes. On an ambiguous question, that """
            """restatement is not politeness — it is the difference between solving their problem and solving a different """
            """one confidently.""")

D = Diagram('The edge case that is usually missed')
D.box('e1', 140, 150, 780, 200, 'A node whose children all disappear', 'It becomes a leaf. Should it survive, or vanish too? '
      'If it has no payload, it should vanish — and that recursion must be bottom-up.', kind='shared', step=0)
D.box('e2', 140, 400, 780, 230, '**The root collapsing into its only child**',
      'Every non-root case works, the root special-cases itself, and the bug hides until someone passes a chain. '
      'This is the classic missed case.', kind='deny', step=1)
D.label(1000, 200, 'Others worth naming:', kind='info', step=2, w=820, size='m')
D.label(1000, 270, '• empty tree, single node\n• a single-child node **with** a payload → must not collapse\n'
                   '• a 10⁵-deep chain → recursion depth\n• child order preserved or not',
        kind='neutral', step=2, w=820, size='m')
D.label(140, 700, 'Property test: **compacting twice equals compacting once.** Idempotence catches most of these.',
        kind='ok', step=3, w=1680, size='l', align='center')
sid = D.build()
seg(sid, 0, """Now, which edge case? Here are the two candidates. First: a node whose children all disappear during compaction. """
            """It has just become a leaf. Should it survive or vanish? If it has no payload of its own, it should vanish — """
            """and that only works if your recursion is bottom-up, children before parent.""")
seg(sid, 1, """And second, the one I would bet on: the root collapsing into its only child. Every internal node works fine, """
            """because its parent handles the reattachment. The root has no parent, so unless your function returns the """
            """possibly-new root and the caller uses it, the root silently stays. And it hides, because most test trees do """
            """not have a collapsible root.""")
seg(sid, 2, """Then the usual suspects: empty tree, single node, a single-child node that does have a payload and therefore must """
            """not be collapsed, a very deep chain, and the child-order question.""")
seg(sid, 3, """And here is the test that catches nearly all of them at once, which I would offer unprompted: compacting twice """
            """must equal compacting once. Idempotence. If your first pass left something collapsible behind, the second pass """
            """finds it and the property fails. That single property test is worth more than five hand-written examples.""")

CODE2 = '''public sealed class NTreeNode {
    public string Label;
    public object Payload;              // null means "structural only"
    public List<NTreeNode> Children = new();
}

/// <summary>Collapses structural single-child chains. Returns the (possibly new) subtree root,
/// or null if the subtree disappears entirely. Callers MUST use the return value.</summary>
public static NTreeNode Compact(NTreeNode node) {
    if (node is null) return null;

    var kept = new List<NTreeNode>(node.Children.Count);
    foreach (var child in node.Children) {
        var compacted = Compact(child);       // bottom-up: children first
        if (compacted is not null) kept.Add(compacted);
    }
    node.Children = kept;

    if (kept.Count == 0 && node.Payload is null) return null;      // structural leaf: drop it

    if (kept.Count == 1 && node.Payload is null) {                 // structural chain link: collapse
        var only = kept[0];
        only.Label = node.Label + "/" + only.Label;                // confirm this merge rule first
        return only;                                               // <- this is what fixes the ROOT case
    }
    return node;
}'''
code_slide('Part two: the C# implementation', CODE2, [
 ('1-5', """The node type: a label, an optional payload, and a list of children. The payload being nullable is what lets us """
           """distinguish a structural node, which may be collapsed, from a meaningful one, which may not."""),
 ('7-9', """Read this comment, because it is the fix. The function returns the possibly-new subtree root, and callers must use """
           """the return value. Written that way, the root case is handled by the same code path as everything else — there """
           """is no special case to forget."""),
 ('12-17', """Bottom-up recursion: compact every child first, keep the ones that survived. Doing this before any decision """
             """about the current node is what lets a node discover that all its children have vanished."""),
 ('19', """A node with no children left and no payload is structural and empty, so it disappears. This is the first of the two """
          """edge cases we discussed."""),
 ('21-25', """And here is the collapse: exactly one child and no payload of its own, so this node merges into its child. We """
             """join the labels — and I would confirm that merge rule with the interviewer rather than invent it. Then we """
             """return the child, which is precisely why the root case works."""),
 ('26', """Otherwise the node stays as it is. Order n time, order of depth in stack, and if the interviewer mentions a very """
          """deep chain you offer the explicit-stack version."""),
])

followups(
 ['Nested sum: "do the original weighting (weight = depth)" — one counter, one multiplication',
  'Nested sum: "do it recursively instead" — depth-indexed array of level sums',
  'Compact: "what if two siblings end up with the same label?" — merge or keep; ask'],
 ['"The nested input is a 200 MB JSON document" — stream it; the BFS version holds a whole level, the DFS version holds a path',
  '"Make compaction configurable" — pass a predicate for what counts as collapsible, rather than hard-coding the payload check',
  '"How would you test compaction?" — idempotence, node-count invariants, and a brute-force oracle on small trees'],
 """Follow-ups. On the nested sum, flipping back to the original weighting is one counter and one multiplication, and doing """
 """it recursively means keeping an array of level sums indexed by depth. Both are quick, and being able to switch between """
 """them shows the structure is yours. On the compact tree, sibling labels colliding after compaction is a genuine """
 """question — merge them or keep both — and it is the interviewer's call, not yours.""",
 """At staff level the questions move to scale and to seams. A two-hundred-megabyte nested document means streaming, and """
 """there the BFS version's memory profile — one whole level — may be worse than DFS's, which holds only a path. Making """
 """compaction configurable with a predicate is the extensibility move the pack explicitly scores. And the testing answer """
 """is the one I want you to remember from this whole chapter: idempotence, invariants, and a brute-force oracle on small """
 """inputs beats a handful of examples every time.""")

interview_script([
 '"For the inverse weighting: the two-pass version finds maxDepth then applies it. That is O(n) twice and obviously correct."',
 '"There is a one-pass version: BFS, keep a running level sum, and add it into the total after every level."',
 '"That works because a shallow value stays in the running sum for every remaining level — which is exactly the inverse weight."',
 '"For the compact tree, before I code: what does compact mean here — collapsing single-child chains? And do nodes carry a payload?"',
 '"I will go bottom-up and return the possibly-new subtree root, so the root collapsing is handled by the same code path."',
 '"The test I would write is idempotence: compacting twice must equal compacting once."',
], [
 """The script for part one. Offer the two-pass version, price it, then give the one-pass version and — this is the part """
 """that matters — explain why it works in one sentence. An interviewer cannot tell whether you derived a trick or """
 """memorised it, except by whether you can explain it.""",
 """For part two, the script starts with questions, because the question as posed is genuinely ambiguous. Then you state """
 """the structural decision that removes the edge case rather than patching it: return the new root, bottom-up, same path """
 """for everyone.""",
 """And you close on the property test. The candidate who reported this question said they missed an edge case. Idempotence """
 """is the test that would have found it — and saying so out loud is how you demonstrate that you know where this kind of """
 """code goes wrong.""",
])

sid = statement('Chapter 2 in one line', 'Decide what each call returns — then the tree code writes itself.',
                'Find Leaves returned a height. Upside Down returned the new root. The merge returned a new node. Compact returned the possibly-new subtree.',
                kind='ok')
seg(sid, 0, """That is chapter two. One line: decide what each recursive call returns, and the rest of the code follows.""")
seg(sid, 1, """Find Leaves returned a height. Upside Down returned the new root from the bottom. The keyed merge returned a """
            """freshly built node. And compaction returned the possibly-new subtree root, which is what made the root case """
            """disappear as a special case. Four problems, four different return values, one habit. Next is the chapter recap """
            """with the templates, the checklist and a mini mock. See you there.""")
