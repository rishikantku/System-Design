# -*- coding: utf-8 -*-
"""Chapter 4, Lesson 1 — All O`one Data Structure."""
from lib import *

lesson_header('4.1', 'All O`one — every operation in O(1)', 'Data structure design · doubly linked list of buckets',
              'Highest', 'Your list + a LeetCode Staff report (Jul 2025)', '2026', 'High', 18,
              """Chapter four, lesson one. This chapter is data structure design, and it is the cluster I would revise """
              """hardest, because four separate reported questions live here and because it is where LinkedIn stops asking """
              """whether you can recall an algorithm and starts asking whether you can design something. We open with All """
              """O-one, which is on your own list and was reported independently by a Staff candidate in July twenty """
              """twenty-five. It is the purest version of the chapter's idea: the interviewer hands you the complexity """
              """requirement first, and the requirement is the question.""")

sid = beat('Question', 'The problem, as they pose it',
           '<div class="qwrap"><div class="qtext" style="font-size:34px;line-height:1.4">'
           'Design a structure holding string keys and their counts, supporting four operations:<br><br>'
           '<b>Inc(key)</b> — add one to the key\'s count, inserting it at 1 if absent.<br>'
           '<b>Dec(key)</b> — subtract one; remove the key entirely when the count hits 0.<br>'
           '<b>GetMaxKey()</b> — any key with the largest count, or "" if empty.<br>'
           '<b>GetMinKey()</b> — any key with the smallest count, or "" if empty.<br><br>'
           '<b>All four must run in O(1)</b> — average, and ideally worst case.</div></div>',
           """Here is the question. A structure of string keys and counts, four operations. Inc adds one, inserting the key """
           """at one if it is not there. Dec subtracts one and removes the key when it reaches zero. GetMaxKey and GetMinKey """
           """return any key with the largest or smallest count. And the constraint that defines the whole problem: all four """
           """must run in constant time. Not amortised-ish, not log n. Constant.""")

sid = beat('Interview context', 'Why LinkedIn likes this one',
           '<div style="font-size:31px;line-height:1.7">'
           'It is a <b>design</b> question wearing a data-structures costume. There is no clever trick to recall — '
           'the answer is assembled from two structures you already know, and the interesting part is the reasoning that '
           'picks them.<br><br>'
           'The official pack says Staff Coding scores <b>modularity, extensibility, and finding and fixing bugs</b>. '
           'This question hands you all three: the structure has real invariants, the pointer surgery is where bugs live, '
           'and "now add GetRank" is a natural extension.</div>',
           """A word on why this question keeps coming back. It is a design question wearing a data structures costume. """
           """There is no clever trick to recall — the answer is built from two structures you already know, and the """
           """interesting part is the reasoning that selects them. And it fits what the official pack says the Staff coding """
           """module scores: modularity, extensibility, and finding and fixing bugs. This structure has real invariants, the """
           """pointer work is exactly where bugs hide, and there is a natural extension waiting at the end.""")

think('Four operations, all O(1). What is your first instinct — and what does it cost?', 30,
      """Pause here and think about your first instinct. Mine, and probably yours, is a dictionary from key to count. """
      """Work out what that gives you and, more importantly, what it does not.""",
      """Right. Let us take the naive answer seriously first, because saying it out loud is part of the answer.""")

sid = compare('The naive answer, priced honestly',
 ('Dictionary from key &rarr; count', 'info', 0, ['Inc: **O(1)** ✓', 'Dec: **O(1)** ✓',
                                                  'GetMaxKey: **O(n)** &mdash; scan every key ✗',
                                                  'GetMinKey: **O(n)** ✗']),
 ('Dictionary + a heap', 'deny', 1, ['Inc / Dec: **O(log n)** ✗', 'GetMax: O(1) peek ✓',
                                     'GetMin: needs a *second* heap ✗',
                                     'Stale entries: a count changes, the heap does not know']))
seg(sid, 0, """A dictionary from key to count gives you Inc and Dec immediately, both constant. But the two Get operations """
            """force a full scan, which is linear. So two of four operations fail the requirement.""")
seg(sid, 1, """The reflex fix is a heap, and I want you to reject it out loud rather than silently, because the reasons are """
            """the good part. A heap makes Inc and Dec logarithmic, which breaks the requirement in the other direction. You """
            """need two heaps to get both ends. And worst of all, when a key's count changes, the heap has no idea — you get """
            """stale entries, and lazy deletion turns your constant-time operation into an unbounded one. Heap is the wrong """
            """shape here, and knowing why is worth more than knowing the answer.""")

sid = beat('Key observation', 'Stop storing counts. Store *groups of keys that share a count*.',
           '<div class="bigidea">Many keys share the same count. If keys with count 5 live together in one bucket, '
           'then Inc is not "change a number" — it is <b>move a key to the next bucket</b>.</div>'
           '<div style="margin-top:24px;font-size:30px;line-height:1.7">'
           'And if the buckets are kept in a <b>sorted doubly linked list</b>, then the next bucket is always '
           'right next door: count+1 is the neighbour on the right, count−1 the neighbour on the left. '
           'Max and min are the two ends of the list.</div>',
           """Here is the observation that unlocks it, and it is worth arriving at rather than reciting. Stop thinking about """
           """storing counts. Think about storing groups of keys that share a count. Many keys have count five; put them in """
           """one bucket together. Now Inc is not changing a number — it is moving a key from the bucket for five to the """
           """bucket for six.""", step=0)
seg(sid, 1, """And if you keep the buckets in a doubly linked list, sorted by count, then the bucket you need is always right """
            """next door. Count plus one is the neighbour on the right. Count minus one is the neighbour on the left. You """
            """never search for it. And the maximum and minimum counts are simply the two ends of the list, which is why """
            """both Get operations become a single pointer read.""")

D = Diagram('The structure')
D.box('b1', 120, 200, 300, 150, 'count = 1', '{"hello", "world"}', kind='info', step=0)
D.box('b3', 500, 200, 300, 150, 'count = 3', '{"leet"}', kind='info', step=0)
D.box('b7', 880, 200, 300, 150, 'count = 7', '{"code", "in"}', kind='info', step=0)
D.arrow('b1', 'b3', step=0)
D.arrow('b3', 'b7', step=0)
D.label(120, 390, 'head &rarr; **min count**', kind='ok', step=1, w=300, size='m', align='center')
D.label(880, 390, 'tail &rarr; **max count**', kind='ok', step=1, w=300, size='m', align='center')
D.box('map', 1300, 200, 480, 150, 'Dictionary: key &rarr; its bucket',
      '"leet" &rarr; the count-3 node', kind='shared', step=2)
D.label(120, 500, '**Inc("leet")**: look up its bucket (O(1)), check whether the right neighbour is count 4.\n'
                  'If yes, move the key there. If no, splice a new node in. Then drop the old bucket if it is empty.',
        kind='ok', step=3, w=1660, size='m')
D.label(120, 640, 'Every step is a pointer read or a pointer write. Nothing is searched. **That** is where O(1) comes from.',
        kind='dp', step=4, w=1660, size='l')
sid = D.build()
seg(sid, 0, """So the picture is this. A doubly linked list of buckets, in increasing count order. Count one holds hello and """
            """world. Count three holds leet. Count seven holds code and in.""")
seg(sid, 1, """The head of the list is the minimum count, the tail is the maximum. Both Get operations are now one pointer """
            """read and one element pulled out of a set.""")
seg(sid, 2, """Alongside it, a dictionary from key to the bucket node that contains it. That is the piece that makes lookup """
            """constant — given a key, you land directly on its bucket without walking the list.""")
seg(sid, 3, """Now watch an Inc. Look up leet's bucket, which is count three. Check whether its right neighbour is count """
            """four. If it is, move the key into that bucket. If it is not, splice a new count-four node in between. Then, if """
            """the old bucket is now empty, unlink it.""")
seg(sid, 4, """And that is the whole thing. Every step is a pointer read or a pointer write. Nothing is ever searched. That """
            """is where the constant time comes from, and if you can say that sentence in the interview you have shown you """
            """understand the design rather than remembering it.""")

D = Diagram('Walkthrough: Inc("world") when count 2 does not exist yet')
D.box('a1', 140, 170, 280, 120, 'count = 1', '{hello, **world**}', kind='info', step=0)
D.box('a3', 700, 170, 280, 120, 'count = 3', '{leet}', kind='info', step=0)
D.arrow('a1', 'a3', step=0)
D.label(140, 320, '1 &mdash; map["world"] lands on the count-1 node.', kind='neutral', step=1, w=900, size='m')
D.box('a2', 420, 400, 280, 120, 'count = 2', '{**world**}', kind='ok', step=2)
D.label(140, 550, '2 &mdash; right neighbour is count 3, not 2 &rarr; **splice a new node** between them.',
        kind='ok', step=2, w=1100, size='m')
D.label(140, 620, '3 &mdash; move "world" into it, update map["world"].', kind='ok', step=3, w=1100, size='m')
D.label(140, 690, '4 &mdash; count-1 still holds {hello}, so it stays. Had it emptied, unlink it.',
        kind='shared', step=4, w=1400, size='m')
D.label(1150, 320, 'Four pointer writes.\nNo loop anywhere.', kind='dp', step=5, w=620, size='l')
sid = D.build()
seg(sid, 0, """Let us walk one concrete operation. The list holds count one with hello and world, and count three with leet. """
            """We call Inc on world.""")
seg(sid, 1, """Step one: the map takes us straight to the count-one node. No search.""")
seg(sid, 2, """Step two: we need the count-two bucket. The right neighbour is count three, so count two does not exist yet, """
            """and we splice a new node in between the two. Splicing into a doubly linked list is four pointer writes and """
            """it is constant time.""")
seg(sid, 3, """Step three: move world into the new bucket and point the map entry at it.""")
seg(sid, 4, """Step four: the old bucket still holds hello, so it survives. If it had emptied, we would unlink it — and that """
            """cleanup is not optional, because an empty bucket left at the head would make GetMinKey return garbage.""")
seg(sid, 5, """Four pointer writes, no loop anywhere. That is the operation.""")

sid = cards('Edge cases &mdash; name these before they ask', [
 (0, 'Dec on a key with count 1', 'The key leaves the structure entirely. Remove it from the map <b>and</b> the bucket, then drop the bucket if empty.', 'deny'),
 (0, 'Dec on a key that is not present', 'The spec says nothing happens. Say so out loud; an interviewer who wanted an exception will tell you.', 'shared'),
 (1, 'Empty structure', 'Both Get operations return "". A sentinel head and tail make this one comparison instead of four null checks.', 'ok'),
 (1, 'The bucket that empties in the middle', 'Unlink it. If you skip this, the list slowly fills with empty nodes and Get returns a key that is not there.', 'deny'),
 (2, 'Inc on a brand new key', 'It goes into the count-1 bucket, which may itself need creating at the head.', 'ok'),
 (2, 'Same key Inc\'d twice', 'It must not appear in two buckets. The map is the single source of truth for where a key lives.', 'deny'),
], cols=2)
seg(sid, 0, """Edge cases, and I would name these unprompted because the pack says this module scores finding bugs. Dec on a """
            """key with count one removes it entirely, from the map and the bucket. Dec on a key that is not there does """
            """nothing — say that out loud, because if the interviewer wanted an exception they will correct you, and now """
            """you have had the conversation instead of guessing.""")
seg(sid, 1, """Empty structure returns empty strings from both Gets. Use sentinel head and tail nodes and that becomes one """
            """comparison instead of a scatter of null checks. And the bucket that empties in the middle must be unlinked — """
            """skip it and the list slowly fills with empty buckets until GetMinKey returns a key that no longer exists.""")
seg(sid, 2, """A brand new key goes into the count-one bucket, which may itself need creating at the head. And the same key """
            """must never appear in two buckets: the map is the single source of truth for where a key lives. Most bugs in """
            """this problem are a violation of that one sentence.""")

CODE = '''public class AllOne {
    private sealed class Bucket {
        public int Count;
        public readonly HashSet<string> Keys = new();
        public Bucket Prev, Next;
    }

    private readonly Bucket _head = new(), _tail = new();          // sentinels: never removed
    private readonly Dictionary<string, Bucket> _at = new();       // key -> the bucket holding it

    public AllOne() { _head.Next = _tail; _tail.Prev = _head; }

    private static Bucket InsertAfter(Bucket node, int count) {
        var b = new Bucket { Count = count, Prev = node, Next = node.Next };
        node.Next.Prev = b; node.Next = b;                         // four pointer writes
        return b;
    }

    private void Unlink(Bucket b) { b.Prev.Next = b.Next; b.Next.Prev = b.Prev; }

    public void Inc(string key) {
        if (!_at.TryGetValue(key, out var cur)) {                  // new key -> count 1, at the head
            var first = _head.Next;
            var target = (first != _tail && first.Count == 1) ? first : InsertAfter(_head, 1);
            target.Keys.Add(key); _at[key] = target;
            return;
        }
        var next = (cur.Next != _tail && cur.Next.Count == cur.Count + 1)
                 ? cur.Next : InsertAfter(cur, cur.Count + 1);     // neighbour, or splice one in
        next.Keys.Add(key); _at[key] = next;
        cur.Keys.Remove(key);
        if (cur.Keys.Count == 0) Unlink(cur);                      // never leave an empty bucket
    }

    public void Dec(string key) {
        if (!_at.TryGetValue(key, out var cur)) return;            // absent: the spec says do nothing
        if (cur.Count == 1) { _at.Remove(key); }                   // falls out of the structure
        else {
            var prev = (cur.Prev != _head && cur.Prev.Count == cur.Count - 1)
                     ? cur.Prev : InsertAfter(cur.Prev, cur.Count - 1);
            prev.Keys.Add(key); _at[key] = prev;
        }
        cur.Keys.Remove(key);
        if (cur.Keys.Count == 0) Unlink(cur);
    }

    public string GetMaxKey() => _tail.Prev == _head ? "" : _tail.Prev.Keys.First();
    public string GetMinKey() => _head.Next == _tail ? "" : _head.Next.Keys.First();
}'''
code_slide('The C# implementation', CODE, [
 ('2-6', """The bucket: a count, a set of keys sharing it, and previous and next pointers. A set rather than a list, because """
           """removing a key by value must be constant, and removing from a list is not."""),
 ('8-9', """Two sentinels that are never removed, and the dictionary from key to bucket. The sentinels are worth the two """
           """extra objects — they turn every "is this the first node" question into an ordinary comparison."""),
 ('13-17', """Splice: create a node and write four pointers. Constant time, and it is the only place new buckets are born, """
             """so if the list is ever malformed you know exactly where to look."""),
 ('19', """Unlink is the mirror image, two writes. Notice both helpers are tiny and named — that is the modularity the pack """
          """says this module scores, and it makes the operations below readable."""),
 ('21-27', """Inc, new key first: it belongs at count one, which is either the existing head bucket or a new one spliced """
             """after the head. Getting this branch right is what makes the empty-structure case work."""),
 ('28-33', """Inc, existing key: the target is the right neighbour if it happens to be count plus one, otherwise a fresh """
             """node spliced in. Add to the new bucket, update the map, remove from the old — and unlink the old bucket if """
             """it emptied. That last line is the one people forget, and it is the bug that makes GetMinKey lie."""),
 ('36-45', """Dec is the mirror image with one asymmetry: at count one the key leaves the structure altogether, so we drop """
             """it from the map rather than moving it. Everything else is the same shape, walking left instead of right."""),
 ('47-48', """And the two Gets are pointer reads. Tail-previous is the largest count, head-next the smallest, with the """
             """sentinel comparison handling empty. Any key from the set satisfies the spec — it says any key, and saying """
             """that you noticed is free credit."""),
])

sid = table('Complexity, stated the way an interviewer wants to hear it',
 ['Operation', 'Time', 'Why it is genuinely O(1)'],
 [(0, ['Inc', 'O(1)', 'One dictionary lookup, one set insert, one set remove, at most one splice'], None),
  (0, ['Dec', 'O(1)', 'Same shape, mirrored'], None),
  (1, ['GetMaxKey / GetMinKey', 'O(1)', 'One pointer read plus one element taken from a set'], None),
  (2, ['Space', 'O(n)', 'Every key sits in exactly one bucket; at most n buckets, since a bucket without keys is unlinked'], None)],
 widths=[26, 14, 60])
seg(sid, 0, """Complexity. Inc and Dec are a dictionary lookup, a set insert, a set remove, and at most one splice. All """
            """constant.""")
seg(sid, 1, """The two Gets are a pointer read and one element taken from a set.""")
seg(sid, 2, """Space is linear: each key sits in exactly one bucket, and because we unlink empty buckets there are never more """
            """buckets than keys. Now, one honest caveat you should raise yourself: dictionary and set operations are """
            """constant on average, not worst case, because of hashing. If the interviewer wants true worst case you talk """
            """about the hash function and about adversarial keys. Raising that before they do is a strong signal.""")

followups(
 ['"Add GetRank(key) — the key\'s position by count" — reported as a follow-up on the LFU variant of this question',
  '"Make it thread-safe" — see lesson 9.1; the answer is a lock per structure, then the case for finer grain',
  '"What if counts can jump by k, not 1?" — the neighbour shortcut dies; you need a map from count to bucket'],
 ['"Return all keys with the max count" — the bucket already is that set; O(size of the answer)',
  '"Persist it across restarts" — an append-only log of Inc/Dec, replayed; the structure is a materialised view of the log',
  '"A million keys, mostly count 1" — the structure is fine, but profile the set overhead; one huge bucket is the common shape'],
 """Follow-ups. Add GetRank, meaning the key's position when ranked by count — that was reported as a follow-up on the LFU """
 """variant, and the honest answer is that this structure does not give it in constant time; you would need order statistics, """
 """and saying "that changes the data structure" is better than pretending. Make it thread-safe is the pivot we cover in """
 """chapter nine. And counts jumping by k rather than one kills the neighbour shortcut, because the bucket you want is no """
 """longer next door — you need a map from count to bucket.""",
 """At staff level: return all keys with the max count is free, because the bucket already is that set. Persisting across """
 """restarts is a nice one to answer well — an append-only log of the operations, replayed on start, with the structure """
 """treated as a materialised view of that log. And the realistic-scale question, a million keys mostly at count one, is """
 """less about complexity and more about memory: one enormous bucket is the normal shape, and the per-entry overhead of the """
 """set is what you would actually profile.""")

interview_script([
 '"All four in O(1) rules out a heap — that makes Inc logarithmic and leaves stale entries when a count changes."',
 '"The insight is to store groups of keys that share a count, not the counts themselves."',
 '"Buckets in a sorted doubly linked list: count+1 is the right neighbour, count−1 the left, so I never search."',
 '"A dictionary from key to its bucket makes the lookup constant. The map is the single source of truth for where a key lives."',
 '"Max and min are the two ends of the list. I will use sentinels so empty is one comparison."',
 '"The bug to watch for is a bucket that empties and is not unlinked — GetMinKey would then return a key that is gone."',
], [
 """The script. Open by rejecting the heap and saying why, because that is the reasoning they are listening for, and it """
 """takes ten seconds. Then state the insight as a sentence about groups, not about pointers.""",
 """Then the structure, and note the phrasing: I never search. That is the claim that earns the constant time, so say it """
 """explicitly rather than leaving them to infer it. The map being the single source of truth is the invariant your code """
 """maintains, and naming an invariant out loud is a staff-level habit.""",
 """Close on the bug. Volunteering the failure mode — a bucket that empties and is not unlinked, making GetMinKey lie — """
 """tells the interviewer you have thought about where this code goes wrong, which is literally one of the things the """
 """official pack says this module scores.""",
])

sid = statement('Lesson 4.1', 'When the complexity requirement is stated first, it is the question.',
                'O(1) for both ends means the ends must be pointers. Everything else in the design follows from that one sentence.',
                kind='ok')
seg(sid, 0, """One line to take away. When the interviewer states the complexity requirement first, the requirement is the """
            """question.""")
seg(sid, 1, """Constant time at both ends means the ends have to be pointers, and once you have said that, every other """
            """decision in this design follows from it. Next lesson: GetRandom with duplicates, where the constraint is """
            """again the question, but the answer is an array.""")
