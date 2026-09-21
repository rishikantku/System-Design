# -*- coding: utf-8 -*-
"""Chapter 4 recap — data structure design."""
from lib import *

lesson_header('4.R', 'Chapter 4 recap: data structure design', 'Recap · templates · mini mock',
              'Highest', '4 reported questions — the biggest cluster after trees and graphs', '2026', 'High', 12,
              """Chapter four recap. Four reported questions live in this chapter, which makes it the biggest cluster after """
              """trees and graphs, and it is the one where the interview stops being about recall. Same seven parts as the """
              """other recaps: the pattern in one page, the recognition checklist, the mistakes, the templates, the reported """
              """questions ranked, a five-minute rapid revision, and a mini mock.""")

sid = beat('Pattern summary', 'The chapter in one page',
           '<div class="bigidea">Every question in this chapter handed you a <b>complexity requirement</b> first. '
           'The requirement is not a constraint on the answer &mdash; it <b>is</b> the question.</div>'
           '<div style="margin-top:26px;font-size:30px;line-height:1.7">'
           'O(1) at both ends &rarr; the ends are pointers. Uniform random in O(1) &rarr; a dense array. '
           'A repeated query &rarr; precompute the inputs to the answer. Two orderings at once &rarr; two structures, '
           'nested.</div>',
           """One page. Every question in this chapter handed you a complexity requirement before it handed you the problem. """
           """And the habit I want you to leave with is to read that requirement as the question rather than as a constraint """
           """on your answer.""", step=0)
seg(sid, 1, """Constant time at both ends means the ends must be pointers. Uniform random selection in constant time means a """
            """dense array. A query that repeats means precompute the inputs to the answer rather than the answer. And two """
            """orderings at once means two structures, nested. Four questions, four requirements, four structures that fall """
            """straight out of them.""")

sid = table('The four problems, and what the requirement forced',
 ['Problem', 'The requirement', 'What it forced', 'Reported'],
 [(0, ['All O`one', 'O(1) for max <b>and</b> min', 'Sorted doubly linked list of count buckets + key&rarr;bucket map', 'Yes &times;2'], None),
  (1, ['GetRandom, duplicates', 'Uniform random in O(1)', 'Dense array + value&rarr;index-set map; remove by swapping with the last', 'Yes &times;2'], None),
  (2, ['Shortest Word Distance II', 'Many queries, one build', 'Word&rarr;sorted indices; query is a two-pointer merge', 'Yes'], None),
  (3, ['LFU Cache', 'Lowest count, then least recent', 'Frequency buckets, each an LRU list, + a maintained minFreq', 'Yes'], None)],
 widths=[22, 22, 44, 12])
seg(sid, 0, """Side by side. All O-one needed constant time at both ends, which forced a sorted doubly linked list of buckets """
            """with a map into it.""")
seg(sid, 1, """GetRandom needed uniform random selection, which forced a dense array, and then the array forced the """
            """swap-with-the-last removal trick and the index map that makes it possible.""")
seg(sid, 2, """Shortest Word Distance needed many queries off one build, which forced precomputed index lists and a merge.""")
seg(sid, 3, """And LFU needed two orderings, which forced buckets of lists plus a maintained minimum. Notice that in every """
            """row, the third column is derivable from the second. That is the chapter.""")

sid = steps_list('Recognition checklist &mdash; what the wording is telling you',
 [(0, '&ldquo;All operations in O(1)&rdquo; &rarr; **no heap, no sorting, no scanning**. Something must be a pointer or an index.', 'ok'),
  (0, '&ldquo;Any key with the max&hellip;&rdquo; &rarr; **any** is a gift. A set is enough; you do not need an order inside.', 'ok'),
  (1, '&ldquo;Random&rdquo; or &ldquo;uniformly&rdquo; &rarr; **dense array**. Hash sets cannot be indexed.', 'ok'),
  (1, '&ldquo;Duplicates allowed&rdquo; &rarr; wherever you kept one thing, keep a **set** of them.', 'ok'),
  (2, 'A **constructor** in the signature &rarr; they are telling you to precompute. Ask how many queries.', 'ok'),
  (2, '&ldquo;If several tie, then&hellip;&rdquo; &rarr; a **second ordering**. Nest a structure inside the first.', 'ok'),
  (3, '&ldquo;Least recently used&rdquo; &rarr; doubly linked list, newest at the front, victim at the back.', 'shared'),
  (3, 'Any cache question &rarr; have the **production caveat** ready: pure LFU never forgets; pure LRU thrashes on a scan.', 'shared')],
 numbered=False)
seg(sid, 0, """The recognition checklist. All operations in constant time rules out heaps, sorting and scanning — something in """
            """your answer has to be a pointer or an index. And when the spec says any key with the maximum, that word any """
            """is a gift: a set is enough, you do not need an order inside it.""")
seg(sid, 1, """Random or uniformly means a dense array, because hash sets cannot be indexed. Duplicates allowed means that """
            """wherever you were keeping one thing, you now keep a set of them — that is the entire delta between the two """
            """GetRandom variants.""")
seg(sid, 2, """A constructor in the signature is the interviewer telling you to precompute; ask how many queries before you """
            """decide how much. And "if several tie, then" announces a second ordering, which means nesting a structure """
            """inside the first.""")
seg(sid, 3, """Least recently used means a doubly linked list with the newest at the front and the victim at the back. And """
            """for any cache question, have the production caveat ready — pure LFU never forgets, pure LRU thrashes on a """
            """single large scan. One sentence, and it moves the conversation to where a staff interview wants to be.""")

sid = cards('The mistakes that actually cost people', [
 (0, 'Reaching for a heap', 'It is the reflex, and it breaks the stated requirement. Reject it out loud <i>with reasons</i> — that is worth marks by itself.', 'deny'),
 (0, 'Updating one side of a two-sided invariant', 'The swap in GetRandom touches two values. The promotion in LFU touches a bucket and minFreq. Half an update is a silent bug.', 'deny'),
 (1, 'Leaving empty containers behind', 'An empty bucket at the head makes GetMinKey lie. An empty index set makes Insert lie. Clean up in the same method that emptied it.', 'deny'),
 (1, 'Claiming O(1) worst case', 'Hashing is O(1) <i>average</i>. Say &ldquo;average&rdquo; and mention adversarial keys before they do.', 'shared'),
 (2, 'Designing before asking the workload', 'Precomputing every pair is wrong for three queries and right for three million. Ask.', 'deny'),
 (2, 'Silence during pointer surgery', 'This is the chapter where candidates go quiet for four minutes. Narrate the invariant you are preserving.', 'shared'),
], cols=2)
seg(sid, 0, """The mistakes. Reaching for a heap is the reflex, and it breaks the stated requirement — rejecting it out loud """
            """with reasons is worth marks on its own. And updating one side of a two-sided invariant: the swap in GetRandom """
            """touches two values, the promotion in LFU touches a bucket and the minimum. Half an update is a silent bug """
            """that your examples will not catch.""")
seg(sid, 1, """Leaving empty containers behind — an empty bucket at the head makes GetMinKey lie, an empty index set makes """
            """Insert lie — and the rule that prevents it is to clean up in the same method that emptied the thing. And do """
            """not claim constant worst case when you mean average; say average and mention adversarial keys before they """
            """ask.""")
seg(sid, 2, """Designing before asking about the workload: precomputing every pair is wrong for three queries and right for """
            """three million, so ask. And the one specific to this chapter — silence. This is where candidates go quiet for """
            """four minutes doing pointer surgery. Narrate the invariant you are preserving while your hands move.""")

T1 = '''// TEMPLATE G - bucket list: group items that share a key, move between neighbours.
sealed class Bucket { public int Key; public HashSet<string> Items = new(); public Bucket Prev, Next; }

Bucket InsertAfter(Bucket node, int key) {                 // splice: 4 pointer writes
    var b = new Bucket { Key = key, Prev = node, Next = node.Next };
    node.Next.Prev = b; node.Next = b;
    return b;
}
void Unlink(Bucket b) { b.Prev.Next = b.Next; b.Next.Prev = b.Prev; }

// move an item from its bucket to the key+1 bucket
var next = (cur.Next != tail && cur.Next.Key == cur.Key + 1) ? cur.Next : InsertAfter(cur, cur.Key + 1);
next.Items.Add(item); at[item] = next;
cur.Items.Remove(item);
if (cur.Items.Count == 0) Unlink(cur);                     // never leave an empty bucket'''
code_slide('Template G &mdash; the bucket list (All O`one, LFU, any &ldquo;group by count&rdquo; problem)', T1, [
 (None, """Template G, and it covers both of the hard questions in this chapter. Buckets keyed by a count, held in a sorted """
          """doubly linked list, with a map from item to its bucket. The move is always to a neighbour, so it is constant. """
          """Sentinels at both ends, splice with four writes, unlink with two, and the final line — never leave an empty """
          """bucket — is the one that keeps the ends honest."""),
])

T2 = '''// TEMPLATE H - dense array + index map: O(1) insert, remove and uniform random.
List<int> items = new();
Dictionary<int, HashSet<int>> where = new();               // value -> indices (a set, for duplicates)

void Remove(int val) {
    int hole = where[val].First();  where[val].Remove(hole);
    int last = items.Count - 1;
    if (hole != last) {
        int moved = items[last];
        items[hole] = moved;
        where[moved].Remove(last);                         // repair BOTH values
        where[moved].Add(hole);
    }
    items.RemoveAt(last);
    if (where[val].Count == 0) where.Remove(val);
}
int GetRandom() => items[rng.Next(items.Count)];           // uniform over ELEMENTS'''
code_slide('Template H &mdash; dense array + index map', T2, [
 (None, """Template H. A dense array whose order means nothing, plus a map from value to the set of indices holding it. """
          """Removal is a swap with the last element and a truncation — and the two lines that repair the moved value's """
          """indices are the ones to practise, because that is where this template is won. GetRandom is then a single """
          """index, exactly uniform, with no weighting anywhere."""),
])

T3 = '''// TEMPLATE I - precompute the inputs, answer with a merge.
Dictionary<string, List<int>> at = new();                  // built in ONE left-to-right pass: sorted for free

int Closest(List<int> a, List<int> b) {
    int i = 0, j = 0, best = int.MaxValue;
    while (i < a.Count && j < b.Count) {
        best = Math.Min(best, Math.Abs(a[i] - b[j]));
        if (a[i] < b[j]) i++;                              // advance the smaller: its best partner is behind it
        else j++;
    }
    return best;
}'''
code_slide('Template I &mdash; precomputed index + two-pointer merge', T3, [
 (None, """And template I, for the repeated-query shape. Build the index in one left-to-right pass, which leaves each list """
          """sorted for free. Then the query is a merge whose cost is the two lists rather than the whole input. Advance """
          """the smaller index, because its best possible partner is already behind it — and that one sentence is the """
          """correctness proof, so say it rather than just writing the loop."""),
])

sid = table('The reported questions, ranked by what I would revise first',
 ['#', 'Question', 'Evidence', 'Revise'],
 [(0, ['1', 'LFU Cache (+ GetRank)', 'Taro Staff report, Jul 2025, with the ranking follow-up', '**First**'], None),
  (0, ['2', 'All O`one Data Structure', 'Your own list + an independent LeetCode Staff report', '**First**'], None),
  (1, ['3', 'Insert/Delete/GetRandom, duplicates', 'Your list + a Taro Senior Infra report ("design a random set")', 'Second'], None),
  (1, ['4', 'Shortest Word Distance II', 'Your list + the LinkedIn tagged set', 'Second'], None),
  (2, ['&mdash;', 'LRU Cache', 'Not reported for LinkedIn, but it is inside LFU &mdash; you get it free', 'Free'], 'dim'),
  (2, ['&mdash;', 'Trie, skip list, union-find', 'Not reported for LinkedIn &mdash; general preparation', 'If time'], 'dim')],
 widths=[6, 42, 40, 12])
seg(sid, 0, """Ranked. LFU first, because it is the hardest and because the reported follow-up gives you somewhere to shine. """
            """All O-one next — two independent reports and it shares the bucket template, so the two together cost less """
            """than twice one.""")
seg(sid, 1, """Then GetRandom with duplicates and Shortest Word Distance.""")
seg(sid, 2, """Two honest notes. Plain LRU is not separately reported for LinkedIn, but you get it free from LFU, since a """
            """single bucket is an LRU. And tries, skip lists and union-find are general preparation here, not reported. I """
            """would rather you knew the four reported ones cold than the whole textbook shallowly.""")

sid = steps_list('Five-minute rapid revision &mdash; say each of these out loud',
 [(0, 'What is the stated complexity, and what does it forbid?', 'ok'),
  (0, 'Which structure gives me O(1) at the end I care about &mdash; pointer, index, or neither?', 'ok'),
  (1, 'What is my single source of truth for where an item lives?', 'ok'),
  (1, 'Which invariants must hold after every operation? Say them as sentences.', 'ok'),
  (2, 'Empty container, capacity 0, single element, duplicate key.', 'shared'),
  (2, 'Average or worst case? Hashing is average.', 'shared'),
  (3, 'What is the workload &mdash; how many queries, how skewed?', 'info'),
  (3, 'What is the production caveat for this structure?', 'info')],
 numbered=True)
seg(sid, 0, """Rapid revision, out loud. What is the stated complexity and what does it forbid. Which structure gives me """
            """constant time at the end I care about.""")
seg(sid, 1, """What is my single source of truth for where an item lives — that one sentence prevents most of this chapter's """
            """bugs. And which invariants must hold after every operation, stated as sentences rather than as code.""")
seg(sid, 2, """Empty container, capacity zero, single element, duplicate key. Average or worst case, remembering that """
            """hashing is average.""")
seg(sid, 3, """What is the workload. And what is the production caveat for this structure. Eight questions; if you can """
            """answer all eight for a structure you have just designed, you are done.""")

sid = beat('Mini mock &mdash; 15 minutes', 'Pause here and actually do it',
           '<div class="qwrap"><div class="qlabel">The interviewer asks</div>'
           '<div class="qtext" style="font-size:34px">&ldquo;Design a structure over member profiles supporting '
           '<b>AddSkill(member, skill)</b>, <b>RemoveSkill(member, skill)</b>, and <b>SampleMemberWithSkill(skill)</b> '
           '&mdash; a uniformly random member who currently has that skill. All three in O(1) average.&rdquo;</div></div>',
           """Mini mock, fifteen minutes. Design a structure over member profiles with three operations: add a skill to a """
           """member, remove a skill from a member, and sample a uniformly random member who currently has a given skill. """
           """All three average constant. This is deliberately LinkedIn-shaped and it is deliberately a combination of two """
           """things you have just learned. Pause, talk out loud, write real C sharp.""", kicker='Chapter 4 recap')
think('Fifteen minutes. Requirement first, then structure, then invariants, then edge cases.', 45,
      """Go. Requirement first, then structure, then the invariants, then the edge cases. And there is one detail in this """
      """question that makes it harder than a straight copy of lesson two — see whether you find it.""",
      """Right. Here is the grading.""")

sid = cards('How I would grade that', [
 (0, 'Per skill: a dense array of members + member&rarr;index map', 'Template H, one instance <b>per skill</b>. Sampling is then one index into that skill&rsquo;s array.', 'ok'),
 (0, 'The detail that makes it harder', 'The index map must be keyed by <b>(skill, member)</b>, not by member &mdash; a member appears in many skills, at a different index in each.', 'deny'),
 (1, 'RemoveSkill = swap with the last', 'Within that skill&rsquo;s array only. Repair the moved member&rsquo;s index <b>for that skill</b>.', 'ok'),
 (1, 'Drop the skill when its array empties', 'Otherwise sampling a dead skill divides by zero. Name this.', 'deny'),
 (2, 'Edge cases worth saying', 'Unknown skill; member who already has the skill (idempotent add?); removing a skill the member lacks; sampling a skill nobody has.', 'shared'),
 (2, 'The staff close', '&ldquo;At LinkedIn scale this is a posting list per skill, and sampling uniformly from a distributed posting list is a different problem &mdash; you would sample a shard first, weighted by size.&rdquo;', 'ok'),
], cols=2)
seg(sid, 0, """The structure is template H, one instance per skill: a dense array of members who have that skill, plus an """
            """index map. Sampling is then one index into that skill's array, which is exactly uniform among members with """
            """the skill.""")
seg(sid, 1, """And here is the detail I was hoping you would find. The index map cannot be keyed by member, because a member """
            """appears in many skills and sits at a different index in each one. It has to be keyed by the pair — skill and """
            """member. Candidates who copy lesson two mechanically get this wrong and the bug is invisible until a member """
            """has two skills.""")
seg(sid, 2, """Removal is the same swap with the last element, within that one skill's array, repairing the moved member's """
            """index for that skill. And drop the skill entirely when its array empties, otherwise sampling a dead skill """
            """divides by zero.""")
seg(sid, 3, """Edge cases worth saying out loud: unknown skill, a member who already has the skill and whether add is """
            """idempotent, removing a skill the member does not have, and sampling a skill nobody has. And then the staff """
            """close, which costs one sentence: at LinkedIn scale this is a posting list per skill, and sampling uniformly """
            """from a distributed posting list is a genuinely different problem — you would pick a shard first, weighted by """
            """its size, and then sample within it. Say the algorithm, then say what you would actually build. Chapter four """
            """done.""")
