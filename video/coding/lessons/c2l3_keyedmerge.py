# -*- coding: utf-8 -*-
"""Chapter 2, Lesson 3 — Merge two keyed trees, summing values."""
from lib import *

A = {'ta': (0, 0, 'root 10'), 'ta1': (1, -0.85, 'a: 4'), 'ta2': (1, 0.85, 'b: 6'), 'ta3': (2, -1.3, 'x: 4')}
AE = [('ta', 'ta1'), ('ta', 'ta2'), ('ta1', 'ta3')]
B = {'tb': (0, 0, 'root 7'), 'tb1': (1, -0.85, 'b: 3'), 'tb2': (1, 0.85, 'c: 4')}
BE = [('tb', 'tb1'), ('tb', 'tb2')]

lesson_header('2.3', 'Merge two keyed trees, summing values', 'N-ary trees · recursion with a combiner',
              'High', 'Your own list, with the exact wording', '2026', 'High', 16,
              """Chapter two, lesson three. Merging two trees. Now, there is a LeetCode problem called Merge Two Binary Trees """
              """that most people have seen, and it is about six lines long. That is not this problem. The version on your own """
              """list is phrased very specifically, and every clause in the phrasing changes the solution. So this lesson is """
              """really about a skill that matters more than tree recursion: reading a problem statement precisely, and """
              """noticing when the interviewer has quietly replaced the easy version with a harder one.""")

# ---------------------------------------------------------------- the wording
sid = cards('The wording — every clause changes the code', [
 (0, 'Nodes have a **key and a value**', 'So children are identified by key, not by position.', 'ok'),
 (0, '"Values represent the sum of this and child node values"', 'A stated invariant. Ask whether it must still hold afterwards.', 'shared'),
 (1, '"Absent branches should be created"', 'A branch in only one tree survives into the result.', 'ok'),
 (1, '"Keys are unique among child nodes of a single parent"', 'So a dictionary per node is safe — no duplicate-key case.', 'info'),
 (2, '"Child nodes could be stored in any order"', 'The clause that kills positional recursion. This is the whole problem.', 'deny'),
], cols=2)
seg(sid, 0, """Here is the exact wording, clause by clause, because this is how you should read any problem statement. Nodes have """
            """a key and a value. That single clause tells you children are identified by key, not by being left or right.""")
seg(sid, 1, """Values represent the sum of this node and its children. That is an invariant the data satisfies — and it is worth """
            """asking whether it has to still hold after the merge, because that is a different problem.""")
seg(sid, 2, """Absent branches should be created, which means a branch that exists in only one of the two trees survives into the """
            """result. Keys are unique among the children of one parent, which is your permission to use a dictionary per """
            """node without worrying about collisions.""")
seg(sid, 3, """And then the clause that actually decides the algorithm: child nodes could be stored in any order. The moment you """
            """read that, positional recursion is dead. You cannot pair up first-child with first-child. You have to match by """
            """key. If you only notice one thing in the statement, notice that.""")

# ---------------------------------------------------------------- think
think('Merge two trees whose nodes carry a key and a value. Matching keys sum their values; branches present in only one tree '
      'are created in the result. Children are keyed uniquely within a parent and stored in any order.', 30,
      """Timer. Two things to decide before you write anything, and I want you to say both out loud: how do you match children """
      """between the two trees, and does your function mutate one of the inputs or build a new tree? Both of those are """
      """questions for the interviewer, not assumptions for you.""",
      """Let us work through it. And if the second question did not occur to you — mutate or copy — that is the one that """
      """separates a correct answer from a careful one, and I will show you why in a moment.""")

# ---------------------------------------------------------------- the two trees
D = Diagram('Two trees, matched by key')
tree(D, A, AE, x=470, y=150, step=0, node_w=170, dx=250)
D.label(230, 560, '**Tree A**', kind='info', step=0, w=480, size='l', align='center')
tree(D, B, BE, x=1430, y=150, step=1, node_w=170, dx=250)
D.label(1190, 560, '**Tree B**', kind='dp', step=1, w=480, size='l', align='center')
D.label(120, 660, 'Key **b** exists in both → values sum (6 + 3 = 9).   Key **a** only in A, key **c** only in B → both survive.',
        kind='ok', step=2, w=1700, size='m', align='center')
D.label(120, 740, 'Nothing about **position** is usable: b is second in A and first in B.', kind='deny', step=3, w=1700, size='m', align='center')
sid = D.build()
seg(sid, 0, """Let me make it concrete. Tree A has a root with value ten, and two children keyed a and b, with a having a child """
            """keyed x.""")
seg(sid, 1, """Tree B has a root with value seven, and children keyed b and c.""")
seg(sid, 2, """Now merge them. Key b exists in both, so its values sum: six plus three is nine. Key a exists only in A and key c """
            """only in B, so both of those survive into the result untouched.""")
seg(sid, 3, """And here is the trap made visible. In tree A, b is the second child. In tree B, b is the first. If you had written """
            """the classic left-and-right recursion, you would have merged a with b and produced silent nonsense — no crash, no """
            """exception, just wrong data. That is the worst kind of bug and it is exactly what the any-order clause is warning """
            """you about.""")

# ---------------------------------------------------------------- observation
sid = steps_list('Problem → observation → pattern → structure → algorithm', [
 (0, '**Problem:** merge two keyed trees, summing matched keys', 'info'),
 (0, '**Observation:** matching is by key, so each node needs key-addressable children', 'shared'),
 (1, '**Pattern:** parallel recursion over two structures, driven by the union of the keys', 'dp'),
 (1, '**Structure:** `Dictionary<string, Node>` for children — O(1) match, no ordering assumption', 'ok'),
 (2, '**Algorithm:** walk A\'s children; for each, merge if B has the key, else copy. Then add B\'s leftovers.', 'ok'),
 (2, '**Complexity:** O(a + b) nodes touched, plus the copy cost for one-sided branches', 'info'),
])
seg(sid, 0, """The chain, then. Problem: merge two keyed trees. Observation: matching happens by key, which means every node needs """
            """its children addressable by key.""")
seg(sid, 1, """Pattern: parallel recursion over two structures at once, driven not by position but by the union of the key sets. """
            """Structure: a dictionary from key to child node, which gives you constant-time matching and, importantly, carries """
            """no ordering assumption at all.""")
seg(sid, 2, """Algorithm: walk A's children. For each key, if B has the same key, merge the two subtrees recursively; if not, """
            """take A's subtree as is. Then sweep B's children for keys that A did not have, and add those. Complexity: you """
            """touch each node once across both trees, plus whatever copying you decide to do — and that is the next question.""")

# ---------------------------------------------------------------- mutate or copy
sid = compare('The question most candidates never ask',
 ('Mutate tree A in place', 'shared', 0, ['Fastest, no allocation', 'Caller\'s tree A is silently changed',
                                          'B\'s subtrees become **aliased** into A',
                                          'Later edit of B changes A — a bug found weeks later']),
 ('Return a new tree', 'ok', 1, ['Inputs untouched, no aliasing', 'Costs a copy of every one-sided branch',
                                 'Safe default when ownership is unclear',
                                 '**Say which you chose and why**']))
seg(sid, 0, """Now the question I promised. When a branch exists only in tree B and you attach it to the result, do you attach """
            """B's actual subtree, or a copy of it? If you attach the real one, that subtree now lives in two trees at once. """
            """Change it through B later and the merged tree changes too. That is aliasing, and it produces the kind of bug """
            """that gets found weeks later by someone else.""")
seg(sid, 1, """The safe default when ownership is unclear is to return a new tree and copy what you take. It costs you a copy of """
            """the one-sided branches. The point is not that copying is always right — if one tree is disposable, mutating it """
            """is a perfectly good optimisation. The point is that this is a decision, and the interviewer wants to hear you """
            """make it rather than stumble into it. This is precisely the extensibility-and-ownership thinking the pack says """
            """this module scores.""")

# ---------------------------------------------------------------- code
CODE = '''public sealed class Node {
    public string Key;
    public long Value;
    public Dictionary<string, Node> Children = new();   // keyed: order never matters
}

// Returns a NEW tree. Neither input is mutated and no subtree is shared.
public static Node Merge(Node a, Node b) {
    if (a is null) return Clone(b);
    if (b is null) return Clone(a);

    var merged = new Node { Key = a.Key, Value = a.Value + b.Value };

    foreach (var pair in a.Children) {
        merged.Children[pair.Key] = b.Children.TryGetValue(pair.Key, out var other)
            ? Merge(pair.Value, other)       // key in both: recurse
            : Clone(pair.Value);             // key only in A: copy it across
    }

    foreach (var pair in b.Children)
        if (!a.Children.ContainsKey(pair.Key))
            merged.Children[pair.Key] = Clone(pair.Value);   // the "absent branch" clause

    return merged;
}'''
code_slide('The C# implementation', CODE, [
 ('1-5', """The node type first, and the one line that matters is the children dictionary. Keyed, so order never enters the """
           """picture. If you write this type on the whiteboard before you write the algorithm, you have already answered the """
           """hardest part of the question."""),
 ('7-11', """The comment states the contract — new tree, nothing mutated, nothing shared — and the two null guards handle the """
            """case where one side is missing. Notice they clone rather than return the input directly, which keeps the """
            """promise the comment just made. If you returned `b` there, you would have aliased it, and your contract would be """
            """a lie on the very first line."""),
 ('11', """Then the node itself: same key, values summed. Widening to long here is deliberate — summing two large values is """
          """where a silent overflow would live."""),
 ('13-17', """Now the union walk. For each of A's children, we ask B whether it has the same key. If it does, we recurse, and """
             """that recursive call handles the whole subtree. If it does not, we copy A's subtree across. Two branches, one """
             """line each, and the ternary keeps them side by side so a reader can see the symmetry."""),
 ('19-21', """And this loop is the absent-branches clause from the problem statement, written down: anything in B whose key A """
             """did not have gets copied in. It is easy to forget this loop entirely, and if you do, your merge silently drops """
             """half of tree B. Worth writing a test for that specific case."""),
 ('23', """Return the merged node. The recursion has already built everything underneath it."""),
])

# ---------------------------------------------------------------- edges
sid = cards('Edge cases', [
 (0, 'One tree null', 'Return a copy of the other — not the other itself, or you alias it.', 'ok'),
 (0, 'Different root keys', 'Ask: is that legal? Usually you merge roots regardless, but say so.', 'shared'),
 (1, 'Deep chains', 'Recursion depth. Offer an explicit stack for a 10⁵-deep tree.', 'deny'),
 (1, 'Value overflow', 'Summing two large values — widen to long, and say that you did.', 'deny'),
 (2, 'The stated invariant', '"Value = this + children" — does it still hold? Summing pairwise preserves it.', 'info'),
 (2, 'Cycles in the input', 'A "tree" from an untrusted source may not be one. Say it; do not code it unless asked.', 'info'),
], cols=2)
seg(sid, 0, """Edge cases. One tree null: return a copy, for the aliasing reason we just covered. Different root keys: that is a """
            """question, not an assumption — usually you merge the roots anyway, but make the interviewer confirm it.""")
seg(sid, 1, """Deep chains mean recursion depth, same as every tree problem in this chapter. And value overflow is a real one """
            """here because we are summing: widen to long, and say out loud that you did it on purpose.""")
seg(sid, 2, """Now the nice one. The problem says a node's value is the sum of itself and its children. Does that invariant """
            """survive the merge? Think about it for a second... yes, it does, because if it held in A and it held in B, then """
            """summing matched nodes pairwise preserves it — the sum of the sums is the sum. Being able to say that in one """
            """sentence is a genuinely strong moment in an interview. And cycles: a tree from an untrusted source may not be a """
            """tree. Mention it; do not code for it unless they ask.""")

# ---------------------------------------------------------------- complexity
sid = table('Complexity', ['', 'Answer', 'Say it like this'], [
 (0, ['Time', 'O(a + b)', 'Every node in both trees is touched once — plus the clone of one-sided branches'], [None, 'ok', None]),
 (1, ['Space', 'O(result) + O(depth)', 'The new tree, plus the recursion stack'], [None, 'info', None]),
 (2, ['If you mutate instead', 'O(shared nodes)', 'No cloning — faster, and you inherit the aliasing risk'], [None, 'shared', None]),
], widths=[22, 24, 54])
seg(sid, 0, """Complexity. Order a plus b: every node in both trees is visited once. Then be precise about the extra term — """
            """cloning the branches that exist on only one side. Most candidates forget to mention the clone cost at all.""")
seg(sid, 1, """Space is the new tree itself, plus the recursion stack proportional to depth.""")
seg(sid, 2, """And if you take the mutating version instead, you drop the clone cost entirely and pay for it in aliasing risk. """
            """Saying that trade in one sentence — faster, and here is what I would be accepting — is the answer that sounds """
            """like someone who has maintained code rather than just written it.""")

# ---------------------------------------------------------------- follow-ups
followups(
 ['"Merge k trees, not two" — fold pairwise, or walk all k key sets at once',
  '"Do it iteratively" — an explicit stack of node pairs',
  '"What if values should be maxed, not summed?" — pass in a combiner'],
 ['"Make the merge rule pluggable" — `Func<long,long,long>` for sum, max, or last-write-wins',
  '"The trees are huge and on disk" — merge streams of sorted key paths instead of loading both',
  '"Two threads merge into the same result" — immutability makes this free; mutation does not'],
 """Follow-ups. Merging k trees instead of two: you can fold pairwise, which is simple, or walk all k key sets at once, """
 """which is one pass but fiddlier — mention both and pick. Doing it iteratively means an explicit stack of node pairs. And """
 """the max-instead-of-sum question is the one they use to see whether your code has a seam.""",
 """Which brings me to the staff-level version of that. Instead of hard-coding the plus, take a combiner function — sum, """
 """max, last-write-wins — as a parameter. One line of change, and now the same function serves three requirements. That is """
 """the modularity-and-extensibility signal the pack names, and this problem is an unusually clean place to demonstrate it. """
 """The disk version is a nice systems answer: merge streams of sorted key paths rather than loading both trees. And the """
 """threading question answers itself if you returned a new tree — immutable inputs are thread-safe for free, which is a """
 """second payoff for the decision you made early.""")

# ---------------------------------------------------------------- script
interview_script([
 '"Let me check a few things in the statement: children are keyed and unordered, keys are unique among siblings, and branches in one tree only should survive?"',
 '"Since children are unordered, I will match by key, which means a dictionary of children per node rather than left and right."',
 '"Do you want me to mutate one of the inputs or return a new tree? I will build a new tree unless you prefer otherwise, because attaching a subtree from B would alias it."',
 '"The walk is: for each of A\'s children, merge if B has the key, otherwise copy; then add B\'s keys that A did not have."',
 '"O(a+b) nodes touched plus the clone cost for one-sided branches; space is the result plus recursion depth."',
 '"The stated invariant — value equals this plus children — still holds, because summing pairwise preserves it."',
 '"If you want max instead of sum later, I would take the combiner as a parameter rather than editing this function."',
], [
 """The script. You open by reading the statement back with the three clauses that matter, as questions. That is not """
 """padding — it is you demonstrating that you spotted the unordered-children clause, which is the entire difficulty.""",
 """Then you name the consequence: dictionary of children, not left and right. Then the ownership question, with your """
 """default and your reason. Notice you are not asking permission — you are stating a default and inviting correction, which """
 """is how a senior person handles an underspecified spec.""",
 """Then the algorithm in one sentence, the complexity with the clone term, the invariant observation, and finally the """
 """combiner seam. That last line is what makes this answer staff-level rather than correct: you have told them the code is """
 """ready for the requirement that has not arrived yet.""",
])

sid = statement('Take this with you', 'Read the clauses. One of them is always load-bearing.',
                '"Children could be stored in any order" is the whole problem. Next lesson: nested structures, and a phone-screen question from 2026.',
                kind='ok')
seg(sid, 0, """One sentence. Read the clauses — one of them is always load-bearing.""")
seg(sid, 1, """Here it was children could be stored in any order, and everything else followed from it. Next lesson we take on """
            """nested structures: a 2026 phone-screen report, plus the compact-tree question from your own list. Same family, """
            """different disguise. See you there.""")
