# -*- coding: utf-8 -*-
"""Chapter 4, Lesson 4 — LFU Cache, and the GetRank follow-up."""
from lib import *

lesson_header('4.4', 'LFU Cache, and the GetRank follow-up', 'Data structure design · frequency buckets',
              'Highest', 'Taro Staff report (Jul 2025), with the ranking follow-up', '2025', 'High', 18,
              """Chapter four, lesson four, and the hardest question in this chapter. LFU cache — evict the least """
              """frequently used entry — reported by a Staff candidate on Taro in July twenty twenty-five, and reported """
              """with a follow-up asking for a rank. Two things make this the right closing lesson for the chapter. It is """
              """the same bucket idea as All O-one, so you get to see a structure reused rather than a trick relearned. And """
              """it is a cache, which means the follow-ups go straight into production territory, where a staff interview """
              """wants to be anyway.""")

sid = beat('Question', 'The problem, as they pose it',
           '<div class="qwrap"><div class="qtext" style="font-size:34px;line-height:1.4">'
           'Design a cache with a fixed <b>capacity</b>:<br><br>'
           '<b>Get(key)</b> — return the value or &minus;1; a hit <b>counts as a use</b>.<br>'
           '<b>Put(key, value)</b> — insert or update; an update also counts as a use.<br><br>'
           'When full, evict the entry with the <b>lowest use count</b>. If several tie, evict the '
           '<b>least recently used</b> among them.<br><br>'
           'Both operations in <b>O(1)</b> average.</div></div>',
           """The question. A cache with a fixed capacity. Get returns the value or minus one, and a hit counts as a use. """
           """Put inserts or updates, and an update also counts as a use. When the cache is full you evict the entry with """
           """the lowest use count — and when several tie on count, you evict the least recently used among them. Both """
           """operations in constant time.""")

sid = beat('Interview context', 'The tie-break is the question',
           '<div style="font-size:31px;line-height:1.7">'
           'Plain LFU is a dictionary plus a heap, and it is slow. The clause that makes this a Staff question is '
           '<b>"if several tie, evict the least recently used"</b> &mdash; because it means each frequency bucket needs its '
           'own <b>recency order</b>.<br><br>'
           'So this is <b>LFU built out of LRUs</b>: a list of buckets ordered by frequency, and inside each bucket, an '
           'ordering by recency. Say that sentence and most of the design is done.</div>',
           """Here is the framing I want you to carry in. Plain LFU is a dictionary plus a heap, and it is slow. The clause """
           """that turns this into a Staff question is the tie-break: when several entries share the lowest count, evict the """
           """least recently used among them. That means each frequency bucket needs its own recency order.""", step=0)
seg(sid, 1, """So the structure is LFU built out of LRUs. A collection of buckets ordered by frequency, and inside each """
            """bucket, an ordering by recency. If you can say that one sentence early, most of the design is already done, """
            """and the rest of the interview is you filling in pointers.""")

think('LFU with an LRU tie-break, both operations O(1). What does each bucket have to be?', 30,
      """Pause. You have seen the bucket idea in lesson one of this chapter. Ask yourself what each bucket has to be here """
      """that it did not have to be there, and why.""",
      """In All O-one, a bucket was a set — order inside it did not matter. Here it does. Let us build it.""")

sid = compare('Two shapes, and why one of them is wrong',
 ('Dictionary + min-heap on frequency', 'deny', 0,
  ['Get / Put: **O(log n)** ✗',
   'A hit changes a frequency &rarr; **sift the heap**',
   'The LRU tie-break needs a second key in the comparator',
   'Stale entries unless you do lazy deletion, which is unbounded']),
 ('Frequency buckets, each an LRU list', 'ok', 1,
  ['Get / Put: **O(1)** ✓',
   'A hit moves an entry to the **next** bucket &mdash; neighbour, no search',
   'Inside a bucket: a doubly linked list, newest at the front',
   'Eviction = the **tail of the minimum-frequency bucket**']))
seg(sid, 0, """The heap answer first, so you can reject it for reasons. Every hit changes a frequency, which means sifting the """
            """heap, which makes both operations logarithmic. The tie-break forces a second key into the comparator. And you """
            """get stale entries unless you do lazy deletion, which makes your worst case unbounded. It is a real design, """
            """it is just not the one they asked for.""")
seg(sid, 1, """The bucket design: frequency buckets, each holding a doubly linked list ordered by recency, newest at the """
            """front. A hit moves an entry to the next bucket — which is the neighbour, so no search. And eviction is the """
            """tail of the minimum-frequency bucket, which is a single pointer read once you track the minimum.""")

D = Diagram('The structure, and where eviction happens')
D.box('f1', 120, 170, 480, 190, 'freq = 1', 'front &rarr; [C] &rarr; [B] &rarr; [A] &larr; back\n'
      '**A is the eviction victim**', kind='deny', step=0)
D.box('f2', 680, 170, 420, 190, 'freq = 2', 'front &rarr; [E] &rarr; [D]', kind='info', step=0)
D.box('f5', 1180, 170, 420, 190, 'freq = 5', 'front &rarr; [F]', kind='info', step=0)
D.arrow('f1', 'f2', step=0)
D.arrow('f2', 'f5', step=0)
D.label(120, 390, '**minFreq = 1** &mdash; tracked in one integer, not searched for',
        kind='ok', step=1, w=900, size='m')
D.box('map', 120, 470, 620, 150, 'Dictionary: key &rarr; node', 'value, freq, prev, next',
      kind='shared', step=2)
D.label(800, 470, 'Get(B): read the node via the map, unlink it from freq 1,\n'
                  'push it to the **front** of freq 2. Newest of its new bucket.',
        kind='ok', step=3, w=1000, size='m')
D.label(800, 600, 'If freq 1 is now empty **and** minFreq was 1 &rarr; minFreq becomes 2.',
        kind='deny', step=4, w=1000, size='m')
D.label(120, 700, 'Evict: tail of the minFreq bucket. Lowest count, and least recent among the ties. Both rules, one pointer.',
        kind='dp', step=5, w=1700, size='l')
sid = D.build()
seg(sid, 0, """The picture. Frequency one holds C, B and A, newest at the front, so A at the back is the oldest. Frequency """
            """two holds E and D. Frequency five holds F.""")
seg(sid, 1, """We track the minimum frequency in a single integer. Not searched for — maintained. That is the piece that """
            """makes eviction constant.""")
seg(sid, 2, """And the dictionary maps a key to its node, where the node carries the value, its frequency, and its list """
            """pointers.""")
seg(sid, 3, """Now a Get on B. Read the node through the map, unlink it from frequency one, and push it to the front of """
            """frequency two — front, because it has just been used, so it is the newest of its new bucket.""")
seg(sid, 4, """Then the maintenance line people forget: if frequency one is now empty and the minimum was one, the minimum """
            """becomes two. Notice the "and" — you only raise the minimum when the bucket you emptied was the minimum """
            """bucket.""")
seg(sid, 5, """And eviction is the tail of the minimum-frequency bucket, which satisfies both rules at once: lowest count, """
            """and least recently used among the ties. Two rules, one pointer read. That is the design.""")

sid = cards('The five places this goes wrong', [
 (0, 'minFreq after an eviction', 'Evicting from the min bucket does <b>not</b> change minFreq &mdash; the new entry arrives at frequency 1, so minFreq becomes 1 anyway.', 'deny'),
 (0, 'minFreq after a promotion', 'Only raise it when the emptied bucket <i>was</i> the minimum. Otherwise leave it alone.', 'deny'),
 (1, 'capacity = 0', 'Put must store nothing and Get must always miss. It is a real test case and it crashes naive code.', 'deny'),
 (1, 'Put on an existing key', 'It is an update <b>and</b> a use. Change the value, then promote. Forgetting the promotion is a silent correctness bug.', 'deny'),
 (2, 'Eviction order when everything is new', 'All at frequency 1, so it degenerates to plain LRU. Good sanity check to state.', 'ok'),
 (2, 'Removing an emptied bucket', 'Optional if you index buckets by frequency in a dictionary; mandatory if you keep them in a linked list.', 'shared'),
], cols=2)
seg(sid, 0, """The five places this goes wrong, and they are all about one variable. After an eviction, the minimum frequency """
            """does not need raising — the new entry arrives at frequency one, so the minimum becomes one regardless. """
            """Candidates often add code here that is wrong.""")
seg(sid, 1, """After a promotion, only raise the minimum if the bucket you just emptied was the minimum bucket. And capacity """
            """zero is a genuine test case that crashes naive implementations: Put stores nothing and Get always misses.""")
seg(sid, 2, """Put on an existing key is both an update and a use — change the value, then promote, and forgetting the """
            """promotion is a silent correctness bug that no simple test catches. When everything is new, all entries sit at """
            """frequency one and the cache degenerates to plain LRU, which is a nice sanity check to say aloud. And whether """
            """you remove emptied buckets depends on how you store them.""")

CODE = '''public class LFUCache {
    private sealed class Node {
        public int Key, Value, Freq = 1;
        public Node Prev, Next;
    }

    private sealed class DList {                                  // recency order inside one frequency
        public readonly Node Head = new(), Tail = new();
        public int Count;
        public DList() { Head.Next = Tail; Tail.Prev = Head; }
        public void PushFront(Node n) {
            n.Next = Head.Next; n.Prev = Head;
            Head.Next.Prev = n; Head.Next = n; Count++;
        }
        public void Unlink(Node n) { n.Prev.Next = n.Next; n.Next.Prev = n.Prev; Count--; }
        public Node Back => Tail.Prev;                            // least recently used in this bucket
    }

    private readonly int _cap;
    private int _minFreq;
    private readonly Dictionary<int, Node> _nodes = new();
    private readonly Dictionary<int, DList> _buckets = new();     // frequency -> its recency list

    public LFUCache(int capacity) { _cap = capacity; }

    private void Promote(Node n) {
        var from = _buckets[n.Freq];
        from.Unlink(n);
        if (from.Count == 0 && _minFreq == n.Freq) _minFreq++;     // only when the MIN bucket empties
        n.Freq++;
        if (!_buckets.TryGetValue(n.Freq, out var to)) { to = new DList(); _buckets[n.Freq] = to; }
        to.PushFront(n);                                          // newest of its new bucket
    }

    public int Get(int key) {
        if (!_nodes.TryGetValue(key, out var n)) return -1;
        Promote(n);
        return n.Value;
    }

    public void Put(int key, int value) {
        if (_cap <= 0) return;                                    // capacity 0: store nothing

        if (_nodes.TryGetValue(key, out var existing)) {
            existing.Value = value;                               // an update is also a USE
            Promote(existing);
            return;
        }

        if (_nodes.Count == _cap) {                               // evict before inserting
            var victim = _buckets[_minFreq].Back;                 // lowest freq, least recent among ties
            _buckets[_minFreq].Unlink(victim);
            _nodes.Remove(victim.Key);
        }

        var fresh = new Node { Key = key, Value = value };
        if (!_buckets.TryGetValue(1, out var ones)) { ones = new DList(); _buckets[1] = ones; }
        ones.PushFront(fresh);
        _nodes[key] = fresh;
        _minFreq = 1;                                             // a new entry always resets the minimum
    }
}'''
code_slide('The C# implementation', CODE, [
 ('2-5', """The node carries its key as well as its value. That looks redundant until eviction, where you have a node and """
           """need to delete its dictionary entry — without the key stored, that lookup is impossible."""),
 ('7-17', """A small doubly linked list class with sentinels, push-front and unlink, and a Back property. Writing this as """
            """its own type rather than inline pointer code is the modularity the official pack scores, and it makes the """
            """operations below read like the design."""),
 ('19-22', """The fields: capacity, the current minimum frequency, key to node, and frequency to bucket. Four fields, and """
             """each one earns its place — I would name them while explaining the design, before writing a method."""),
 ('26-33', """Promote is the heart of it, and it is shared by Get and Put, which is why the two public methods stay short. """
             """Unlink from the current bucket, raise the minimum only if the minimum bucket just emptied, increment the """
             """frequency, create the next bucket if needed, and push to its front."""),
 ('35-39', """Get is then three lines: miss returns minus one, hit promotes and returns. All of the difficulty lives in one """
             """private method, which is exactly where you want it under interview pressure."""),
 ('41-48', """Put. Capacity zero returns immediately. An existing key is updated and promoted — both, and that second half """
             """is the silent bug if you skip it."""),
 ('50-54', """Eviction: the back of the minimum-frequency bucket, removed from both the list and the dictionary. This one """
             """expression is where both eviction rules are enforced, so it is worth narrating when you write it."""),
 ('56-61', """And insertion: a fresh node at frequency one, pushed to the front of the frequency-one bucket, with the """
             """minimum reset to one. That last assignment is unconditional, and being able to say why — a brand new entry """
             """always has the lowest possible count — is the difference between understanding it and having memorised it."""),
])

sid = beat('The reported follow-up', '&ldquo;Now add GetRank(key)&rdquo;',
           '<div style="font-size:30px;line-height:1.7">'
           'The Taro report pairs this question with a <b>ranking</b> follow-up. The honest answer is the strong one:'
           '<br><br>'
           '<b>1.</b> This structure gives you the min and the max in O(1), but <b>not</b> a rank &mdash; nothing counts how '
           'many entries sit below a frequency.<br>'
           '<b>2.</b> Exact rank in O(log n) needs an <b>order-statistic tree</b> or a Fenwick tree over frequencies, '
           'maintained on every promotion.<br>'
           '<b>3.</b> If an <i>approximate</i> rank is acceptable, keep a count per frequency bucket and a running total '
           '&mdash; that is a prefix sum over a small array, and frequencies are usually few.<br><br>'
           '<i>Saying "that changes the data structure, here is what to" beats pretending the current one does it.</i>',
           """Now the reported follow-up: add GetRank. And this is where I want to teach you a habit rather than an """
           """algorithm. The honest answer is the strong answer.""", step=0)
seg(sid, 1, """One: this structure gives you the minimum and the maximum in constant time, but it does not give you a rank, """
            """because nothing in it counts how many entries sit below a given frequency. Say that first.""")
seg(sid, 2, """Two: an exact rank in logarithmic time needs an order-statistic tree, or a Fenwick tree indexed by frequency, """
            """maintained on every promotion. Name the structure and name the cost.""")
seg(sid, 3, """Three: if an approximate rank is acceptable, keep a count per bucket and a running total, which is a prefix """
            """sum over a small array — and frequencies in a real cache are few, so that is often the practical answer.""")
seg(sid, 4, """The habit is this: saying "that changes the data structure, and here is what to" is much stronger than """
            """pretending your current design covers it. Interviewers ask extension questions partly to see whether you """
            """will bluff.""")

followups(
 ['"Add GetRank(key)" — reported; see above',
  '"Make it thread-safe" — lesson 9.1; start with one lock, then argue about striping',
  '"What if two entries tie on frequency AND recency?" — impossible; recency is a total order within a bucket'],
 ['"Why does nobody run pure LFU in production?" — it never forgets; an entry hot last year outranks one hot today',
  '"Fix that" — aging: halve all counts periodically, or use a windowed count. This is what TinyLFU does',
  '"Cache this across a fleet, not one process" — now it is admission policy plus a shared store; the eviction rule is the small part'],
 """Follow-ups. GetRank we have just covered. Thread-safety is chapter nine. And a nice small one: can two entries tie on """
 """both frequency and recency? No — recency is a total order inside a bucket, so the tie-break always resolves. Noticing """
 """that the spec cannot be ambiguous is a good sign.""",
 """The staff-level follow-ups are where this question gets interesting, so prepare them. Why does nobody run pure LFU in """
 """production? Because it never forgets — an entry that was hot a year ago outranks one that is hot today, and the cache """
 """ossifies. How would you fix it? Ageing: halve all counts periodically, or count over a sliding window, which is """
 """essentially what TinyLFU does. And if the cache spans a fleet rather than one process, the eviction rule becomes the """
 """small part of the problem; admission policy and the shared store become the design. If you get one of these, you are """
 """no longer being asked a coding question.""")

interview_script([
 '"The tie-break is the interesting clause: lowest frequency, then least recently used. So this is LFU built out of LRUs."',
 '"A heap makes every hit O(log n) and leaves stale entries. I will use frequency buckets instead."',
 '"Each bucket is a doubly linked list, newest at the front. Eviction is the tail of the minimum-frequency bucket."',
 '"I track minFreq in an integer. I raise it only when the minimum bucket empties, and I reset it to 1 on every insert."',
 '"Put on an existing key is an update and a use — both."',
 '"One caveat: pure LFU never forgets. In production I would age the counts."',
], [
 """The script. Open on the tie-break, because that is the clause that chooses the structure, and give the one-sentence """
 """summary: LFU built out of LRUs. Then reject the heap with its two specific costs.""",
 """Then the mechanics, stated as invariants rather than steps: buckets are recency lists, eviction is the tail of the """
 """minimum bucket, and the minimum is maintained by two rules you can state in one breath.""",
 """Mention the update-is-also-a-use rule, because it is the bug they are watching for. And close on the production """
 """caveat. You have just built exactly what they asked for and then told them why nobody ships it unmodified — that is a """
 """staff signal, and it takes one sentence.""",
])

sid = statement('Lesson 4.4', 'Two orderings at once means two structures, nested.',
                'Frequency buckets in a list; recency inside each bucket. Any question with a primary and a secondary ordering has this shape.',
                kind='ok')
seg(sid, 0, """One line to take away, and it generalises well beyond this question. When you need two orderings at once, you """
            """need two structures, nested.""")
seg(sid, 1, """Frequency across the buckets, recency inside each one. Any problem with a primary and a secondary ordering """
            """has this shape, and recognising it saves you the five minutes most candidates spend trying to force a single """
            """comparator to do both jobs. Next up is the chapter four recap, with the templates and a mini mock.""")
