# -*- coding: utf-8 -*-
"""Chapter 4, Lesson 2 — Insert Delete GetRandom O(1), duplicates allowed."""
from lib import *

lesson_header('4.2', 'Insert Delete GetRandom O(1), duplicates allowed', 'Data structure design · array + index set',
              'High', 'Your list + a Taro Senior Infra report ("design a random set")', '2025', 'High', 16,
              """Chapter four, lesson two. Insert, Delete and GetRandom, all in constant time, with duplicates allowed. This """
              """is on your own list, and a Senior Infrastructure candidate reported the same question in October twenty """
              """twenty-five phrased as "design a random set", which is worth knowing because the phrasing hides the """
              """duplicates clause and candidates walk into the easy version. Same lesson as the last one: the complexity """
              """requirement is the question. But the answer this time is an array, and the reason is uniform randomness.""")

sid = beat('Question', 'The problem, as they pose it',
           '<div class="qwrap"><div class="qtext" style="font-size:34px;line-height:1.4">'
           'Design a collection supporting three operations, <b>all in average O(1)</b>:<br><br>'
           '<b>Insert(val)</b> — add a value; <b>duplicates are allowed</b>. Return whether the value was newly present.<br>'
           '<b>Remove(val)</b> — remove <i>one</i> occurrence if present. Return whether anything was removed.<br>'
           '<b>GetRandom()</b> — return a value, where each <i>element</i> (not each distinct value) is '
           '<b>equally likely</b>.</div></div>',
           """The question. A collection with three operations, all average constant time. Insert adds a value and """
           """duplicates are allowed. Remove takes out one occurrence. And GetRandom returns a value where every element is """
           """equally likely — and listen to that word, element. If the collection holds four and four and nine, then four """
           """must come back two-thirds of the time. Not half. That single clause is the difference between this and a """
           """much easier problem.""")

think('GetRandom must be uniform over elements. What does that immediately rule out?', 30,
      """Pause. Ask yourself what uniform random selection in constant time actually requires of a structure, and which of """
      """the structures you know can do it. This is the whole problem in one question.""",
      """Here is the reasoning I would want to hear out loud.""")

sid = compare('What the random requirement forces',
 ('Hash set, or dictionary of counts', 'deny', 0,
  ['Insert / Remove: **O(1)** ✓',
   'GetRandom: there is **no way to pick the i-th element** of a hash set in O(1)',
   'Iterating to position i is **O(n)** ✗',
   'With counts, picking uniformly needs a **weighted** draw ✗']),
 ('An array', 'ok', 1,
  ['GetRandom: `arr[rnd.Next(arr.Count)]` &mdash; **O(1) and exactly uniform** ✓',
   'Insert: append &mdash; **O(1)** ✓',
   'Remove at an arbitrary index: **O(n)** shift ✗ &mdash; <i>unless you do not shift</i>',
   'And we know where each value lives if we index it']))
seg(sid, 0, """A hash set does Insert and Remove beautifully and then fails completely at the third operation, because there """
            """is no way to ask a hash set for its i-th element in constant time. You would have to iterate, which is """
            """linear. And a dictionary of value to count is worse for this purpose: picking uniformly over elements from """
            """counts is a weighted draw, which needs a prefix sum and a binary search.""")
seg(sid, 1, """An array is the opposite. Uniform random selection is one index into an array — constant and exactly uniform, """
            """no cleverness required. Appending is constant. The only problem is removal, which normally means shifting """
            """everything after the gap, and that is linear. So the whole design reduces to one question: can you remove """
            """from the middle of an array without shifting?""")

sid = beat('Key observation', 'You can remove from an array in O(1) — if you are allowed to reorder it',
           '<div class="bigidea">Nothing in the spec says the array has an order. So do not close the gap: '
           '<b>move the last element into it</b> and shorten the array by one.</div>'
           '<div style="margin-top:24px;font-size:30px;line-height:1.7">'
           'That is one write and one truncation. The array stays dense, which is all GetRandom needs. '
           'The remaining question is how you find the index to overwrite &mdash; and that is what the second structure '
           'is for: a dictionary from <b>value &rarr; the set of indices where it currently sits</b>.</div>',
           """And here is the observation. Nothing in the specification says the collection has an order. So when you remove """
           """an element, do not close the gap by shifting. Move the last element into the hole and shorten the array by """
           """one. One write, one truncation, constant time, and the array stays dense — which is the only property """
           """GetRandom actually needs.""", step=0)
seg(sid, 1, """That leaves one question: how do you find the index to overwrite? That is what the second structure is for. A """
            """dictionary from a value to the set of indices where that value currently sits. Set, not a single index, """
            """because duplicates are the whole point of this variant.""")

D = Diagram('Remove(4) from [7, 4, 9, 4, 2]')
xs = [140, 400, 660, 920, 1180]
vals = ['7', '4', '9', '4', '2']
for i, (x, v) in enumerate(zip(xs, vals)):
    D.box('a%d' % i, x, 180, 220, 110, v, 'index %d' % i,
          kind='ok' if i == 1 else ('shared' if i == 4 else 'info'), step=0)
D.label(140, 320, 'map: 7&rarr;{0} &nbsp; 4&rarr;{1,3} &nbsp; 9&rarr;{2} &nbsp; 2&rarr;{4}',
        kind='neutral', step=0, w=1400, size='m')
D.label(140, 420, '1 &mdash; pick **any** index of 4 from its set: say index 1.', kind='ok', step=1, w=1500, size='m')
D.label(140, 490, '2 &mdash; copy the **last** element (2, at index 4) into index 1.', kind='ok', step=2, w=1500, size='m')
D.label(140, 560, '3 &mdash; fix the map for the value that moved: 2&rarr;{1}, not {4}. '
                  '<i>This is the line everybody forgets.</i>', kind='deny', step=3, w=1600, size='m')
D.label(140, 630, '4 &mdash; drop index 1 from 4&rsquo;s set, truncate the array. 4&rarr;{3} remains.',
        kind='ok', step=4, w=1600, size='m')
D.label(140, 720, 'Result: [7, **2**, 9, 4] &mdash; reordered, dense, and still uniform.',
        kind='dp', step=5, w=1600, size='l')
sid = D.build()
seg(sid, 0, """Let us do it concretely. The array holds seven, four, nine, four, two. The map says four lives at indices one """
            """and three. We call Remove on four.""")
seg(sid, 1, """Step one: pick any index of four from its set. Say index one. Any is fine — the spec says remove one """
            """occurrence, and they are indistinguishable.""")
seg(sid, 2, """Step two: copy the last element, the two at index four, into index one.""")
seg(sid, 3, """Step three, and this is the line everybody forgets: fix the map for the value that moved. Two no longer lives """
            """at index four, it lives at index one. If you skip this, the map points at an index past the end of the array, """
            """and the failure shows up much later in a completely unrelated Remove. It is the classic bug in this problem, """
            """and if you write it correctly the first time, say why you were careful.""")
seg(sid, 4, """Step four: drop index one from four's index set, and truncate the array. Four still lives at index three, so it """
            """stays in the map.""")
seg(sid, 5, """Result: seven, two, nine, four. Reordered, dense, and GetRandom is still exactly uniform over the four """
            """remaining elements.""")

sid = cards('The traps, in the order they bite', [
 (0, 'Removing the last element itself', 'You copy it onto its own slot and then must not re-add its index. Handle it, or your map gains a ghost entry.', 'deny'),
 (0, 'Forgetting to update the moved value', 'The most common bug. Every swap touches <b>two</b> values in the map, not one.', 'deny'),
 (1, 'Leaving an empty index set behind', 'Remove the key when its set empties, or Insert will report the value as already present.', 'deny'),
 (1, 'Using a List for the index set', 'Removing a specific index from a list is O(n). Use a HashSet so the whole thing stays constant.', 'shared'),
 (2, 'GetRandom on an empty collection', 'Undefined in the spec. Say what you will do &mdash; throw &mdash; and move on.', 'ok'),
 (2, '"Return whether it was newly present"', 'Insert returns <b>false</b> for a duplicate but still stores it. Easy to misread under pressure.', 'ok'),
], cols=2)
seg(sid, 0, """The traps. Removing the last element itself: you copy it onto its own slot, and then you must be careful not to """
            """re-add its index afterwards, or the map gains a ghost entry pointing past the end. And the big one again — """
            """every swap touches two values in the map, not one.""")
seg(sid, 1, """When a value's index set empties, remove the key entirely, otherwise Insert will report an absent value as """
            """already present. And use a hash set for the index set, not a list, because removing a specific index from a """
            """list is linear and quietly destroys your complexity claim.""")
seg(sid, 2, """GetRandom on an empty collection is undefined in the spec — say what you will do, throw, and move on. And read """
            """the Insert contract carefully: it returns false for a duplicate but it still stores it. That sentence trips """
            """people who are coding fast.""")

CODE = '''public class RandomizedCollection {
    private readonly List<int> _items = new();                       // dense; order is meaningless
    private readonly Dictionary<int, HashSet<int>> _where = new();   // value -> indices holding it
    private readonly Random _rng = new();

    public bool Insert(int val) {
        if (!_where.TryGetValue(val, out var idx)) { idx = new HashSet<int>(); _where[val] = idx; }
        bool isNew = idx.Count == 0;
        idx.Add(_items.Count);
        _items.Add(val);                                             // append: O(1)
        return isNew;                                                // false for a duplicate - still stored
    }

    public bool Remove(int val) {
        if (!_where.TryGetValue(val, out var idx) || idx.Count == 0) return false;

        int hole = idx.First();                                      // any occurrence will do
        idx.Remove(hole);

        int last = _items.Count - 1;
        if (hole != last) {                                          // skip the self-move
            int moved = _items[last];
            _items[hole] = moved;
            _where[moved].Remove(last);                              // the value that MOVED
            _where[moved].Add(hole);                                 // <- the line people forget
        }

        _items.RemoveAt(last);                                       // truncate: O(1) at the end
        if (idx.Count == 0) _where.Remove(val);                      // no empty sets left behind
        return true;
    }

    public int GetRandom() {
        if (_items.Count == 0) throw new InvalidOperationException("empty");
        return _items[_rng.Next(_items.Count)];                      // exactly uniform over ELEMENTS
    }
}'''
code_slide('The C# implementation', CODE, [
 ('2-4', """Two structures. A dense list whose order means nothing, and a dictionary from value to the set of indices """
           """holding it. That pairing is the whole design, and I would say it in one sentence before writing anything."""),
 ('6-12', """Insert. Note the return value is computed before the add: it is true only when this value had no occurrences, """
            """and a duplicate returns false while still being stored. Appending to the end is what keeps it constant."""),
 ('15-18', """Remove. Take any index of the value — they are indistinguishable — and drop it from the set immediately, so """
             """the bookkeeping cannot drift later in the method."""),
 ('20-26', """The swap. Guard against the case where the hole is already the last slot, otherwise you would remove and """
             """re-add the same index in the wrong order. Then copy the last element into the hole and repair the map for """
             """the value that moved. Those two lines are where this problem is won or lost."""),
 ('28-30', """Truncate from the end, which is constant for a list. Drop the value's key when its set is empty, so Insert's """
             """return value stays honest. Then report success."""),
 ('33-36', """And GetRandom is one index into the array. Because every element occupies exactly one slot, picking a slot """
             """uniformly picks an element uniformly — duplicates included, with no weighting anywhere. Say that sentence in """
             """the interview; it is the proof that your structure satisfies the spec."""),
])

sid = table('Complexity',
 ['Operation', 'Time', 'Note'],
 [(0, ['Insert', 'O(1) average', 'Dictionary and set operations; amortised append'], None),
  (0, ['Remove', 'O(1) average', 'One set read, one set remove, two map repairs, one truncation'], None),
  (1, ['GetRandom', 'O(1) worst case', 'One RNG call and one array index &mdash; no hashing involved'], None),
  (2, ['Space', 'O(n)', 'Each element appears once in the list and once in an index set'], None)],
 widths=[24, 20, 56])
seg(sid, 0, """Complexity. Insert and Remove are average constant, because hashing is average constant — be precise about """
            """that word rather than claiming worst case.""")
seg(sid, 1, """GetRandom is genuinely worst-case constant: one random number and one array index, no hashing on that path at """
            """all. That asymmetry is a nice detail to mention.""")
seg(sid, 2, """And space is linear — each element appears once in the list and once in an index set.""")

followups(
 ['"Now without duplicates" — the index set collapses to a single int; simpler, and often asked first',
  '"Prove GetRandom is uniform" — every element occupies exactly one slot, so a uniform slot is a uniform element',
  '"Make it thread-safe" — the reported pivot; see lesson 9.1'],
 ['"Weighted random, by value frequency" — prefix sums plus binary search, O(log n); say that the requirement changed the structure',
  '"Random sample of k elements without replacement" — partial Fisher–Yates over the dense array, O(k)',
  '"It must survive a restart" — the array is derivable; log the operations and rebuild, since order does not matter'],
 """Follow-ups. Without duplicates, the index set collapses to a single integer, and that easier version is often asked """
 """first with the duplicates clause added as the follow-up — expect the pivot. Prove GetRandom is uniform: every element """
 """occupies exactly one slot, so a uniform slot is a uniform element, and that is a complete proof in one sentence. And """
 """thread-safety, which is chapter nine.""",
 """At staff level, weighted random by frequency is a genuinely different structure — prefix sums and a binary search, """
 """logarithmic — and the right answer names that the requirement changed the data structure rather than pretending the """
 """array still works. A random sample of k without replacement is a partial Fisher-Yates shuffle over the dense array, """
 """order k. And surviving a restart is easy here precisely because order is meaningless: log the operations and rebuild """
 """in any order you like.""")

interview_script([
 '"GetRandom in O(1) rules out a hash set — there is no way to pick the i-th element of one without iterating."',
 '"So the elements live in a dense array, because a uniform index into an array is exactly uniform selection."',
 '"Removal from the middle would shift, unless I reorder: I move the last element into the hole and truncate."',
 '"Nothing in the spec requires order, so reordering is free — I would confirm that with you."',
 '"A map from value to the set of indices lets me find a hole in O(1); the set is what makes duplicates work."',
 '"Every swap updates two values in the map. That is where the bug in this problem usually is."',
], [
 """The script. Start by eliminating the hash set and saying why — no i-th element — then name the array and say the """
 """sentence about uniformity, because that is the requirement the array exists to satisfy.""",
 """Then the reordering move, and notice the fourth line: I would confirm that with you. Reordering is an assumption about """
 """the contract, and checking an assumption you are relying on is exactly the habit these rounds reward.""",
 """Then the map, with the set making duplicates work. And close by naming the bug before you write it. An interviewer who """
 """hears "every swap updates two values" knows you have written this before, and they stop watching for that particular """
 """mistake.""",
])

sid = statement('Lesson 4.2', 'The requirement picks the structure. Uniform random in O(1) means a dense array.',
                'Everything else in the design exists to make an array survive removal.',
                kind='ok')
seg(sid, 0, """One line. The requirement picks the structure: uniform random selection in constant time means a dense array, """
            """and nothing else will do.""")
seg(sid, 1, """Every other piece of this design — the index map, the swap with the last element, the two-value repair — """
            """exists only to make an array survive removal. Next lesson: Shortest Word Distance Two, where the constraint """
            """is not one operation but the fact that the query is asked over and over.""")
