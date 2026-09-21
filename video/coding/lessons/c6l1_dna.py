# -*- coding: utf-8 -*-
"""Chapter 6, Lesson 1 — Repeated DNA Sequences."""
from lib import *

lesson_header('6.1', 'Repeated DNA Sequences — hashing, and when not to be clever', 'Hashing · rolling hash · bit packing',
              'High', 'LinkedIn tagged set', '2026', 'Medium', 15,
              """Chapter six, lesson one. Hashing and prefix sums — the chapter where a quadratic answer quietly passes """
              """every example you try and then fails on the real input. We open with Repeated DNA Sequences, which is on """
              """the LinkedIn tagged set. Medium confidence: it is a tagged question rather than a first-hand report, so """
              """treat it as likely rather than reported. The reason it earns a lesson is that it is the best question I """
              """know for practising a specific judgement call — when to be clever, and when being clever is just risk you """
              """took for no reason.""")

sid = beat('Question', 'The problem, as they pose it',
           '<div class="qwrap"><div class="qtext" style="font-size:36px;line-height:1.4">'
           'Given a DNA string over the alphabet <b>A, C, G, T</b>, return every <b>10-letter</b> substring that occurs '
           '<b>more than once</b>. Order does not matter, and each answer appears once.</div></div>',
           """The question. Given a DNA string over the four-letter alphabet A, C, G and T, return every ten-letter """
           """substring that occurs more than once. Order does not matter and each answer appears once in the output.""")

think('The obvious solution is four lines. What is its actual cost — and is that a problem?', 30,
      """Pause. The obvious solution here is about four lines, and I want you to work out its real cost rather than its """
      """apparent cost. Then ask the harder question: is that cost actually a problem for this input?""",
      """Let us be precise, because the precision is the interview.""")

sid = compare('The obvious solution, priced properly',
 ('Slide a window, hash the substring', 'ok', 0,
  ['`seen` and `twice`, two HashSets of string',
   'n &minus; 9 windows, each a 10-char substring',
   'Time: **O(10n)** = O(n) &mdash; the 10 is a constant',
   'Space: O(10n) worst case &mdash; the substrings themselves']),
 ('What people wrongly say about it', 'deny', 1,
  ['&ldquo;Substring makes it O(n&sup2;)&rdquo; &mdash; no: the substring is **fixed length 10**',
   '&ldquo;Hashing a string is O(1)&rdquo; &mdash; also no: it is O(10), which is fine',
   'The real cost is **allocation**: n strings of 10 chars',
   'That is the thing worth optimising &mdash; if it is worth optimising at all']))
seg(sid, 0, """The obvious solution: slide a ten-character window across the string, keep a set of substrings seen and a set """
            """of those seen twice. That is linear — n minus nine windows, each doing ten characters of work, and ten is a """
            """constant.""")
seg(sid, 1, """Now, two things candidates say here that are wrong, and getting them right is worth marks. People say """
            """"substring makes it quadratic" — it does not, because the substring is a fixed ten characters, not a growing """
            """prefix. And people say "hashing a string is constant" — it is not, it is proportional to the length, which """
            """here is ten, which is fine. The real cost of this solution is allocation: you create roughly n strings of """
            """ten characters each. That is the thing worth optimising, if anything is.""")

sid = beat('Key observation', 'Four letters fit in two bits. Ten letters fit in an int.',
           '<div class="bigidea">A, C, G, T &rarr; 00, 01, 10, 11. Ten letters &rarr; <b>20 bits</b>, which fits '
           'comfortably in a 32-bit int. So each window becomes a <b>number</b>, and the whole set becomes a '
           '<code>HashSet&lt;int&gt;</code>.</div>'
           '<div style="margin-top:24px;font-size:30px;line-height:1.7">'
           'Sliding is then two operations: shift left by 2, OR in the new letter, and mask off the top &mdash; '
           'a genuine <b>rolling hash</b>, except it is not a hash at all. It is <b>exact</b>, so there are no '
           'collisions to worry about.</div>',
           """Now the clever version. The alphabet has four letters, and four values fit in two bits. Ten letters is """
           """therefore twenty bits, which fits comfortably inside a thirty-two-bit integer. So each window becomes a """
           """number, and your set becomes a set of integers instead of a set of strings.""", step=0)
seg(sid, 1, """Sliding the window is then two operations: shift left by two, OR in the new letter's code, and mask off the """
            """bits that fell out of range. That is a rolling hash — except that it is not a hash at all. It is an exact """
            """encoding, which means there are no collisions to reason about, and that distinction is worth stating """
            """explicitly because it is the reason this trick is safe.""")

D = Diagram('Rolling the 20-bit window')
D.box('enc', 130, 160, 700, 180, 'Encoding', 'A=00  C=01  G=10  T=11\nten letters &times; 2 bits = **20 bits**',
      kind='info', step=0)
D.box('roll', 900, 160, 880, 180, 'One slide', 'code = ((code &lt;&lt; 2) | next) &amp; 0xFFFFF\n'
      '&lt;&lt;2 drops nothing; the mask drops the oldest letter', kind='ok', step=1)
D.label(130, 400, '"AACCGGTTAA" &rarr; 00 00 01 01 10 10 11 11 00 00', kind='neutral', step=2, w=1600, size='m')
D.label(130, 480, 'slide onto the next letter C &rarr; shift left 2 &rarr; the leading 00 moves past bit 19 &rarr; '
                  'masked away. New code ends in 01.', kind='neutral', step=3, w=1650, size='m')
D.label(130, 590, '**Exact, not a hash** &mdash; two different 10-mers can never share a code, because the map is a '
                  'bijection onto 20 bits.', kind='ok', step=4, w=1650, size='l')
D.label(130, 700, 'Cost: one int per window instead of one 10-char string. No allocation in the loop.',
        kind='dp', step=5, w=1650, size='m')
sid = D.build()
seg(sid, 0, """The encoding: A is zero-zero, C is zero-one, G is one-zero, T is one-one. Ten letters at two bits each is """
            """twenty bits.""")
seg(sid, 1, """One slide is a single expression: shift the code left by two, OR in the next letter, and mask to twenty bits. """
            """The shift does not drop anything by itself — the mask is what discards the oldest letter.""")
seg(sid, 2, """So a sequence like A A C C G G T T A A becomes that bit pattern.""")
seg(sid, 3, """Slide onto the next letter and the leading pair moves past bit nineteen, where the mask removes it.""")
seg(sid, 4, """And the property that makes this safe: it is exact, not a hash. Two different ten-mers can never share a """
            """code, because the mapping is a bijection onto twenty bits. If an interviewer asks about collisions, that is """
            """your answer, and it is a complete one.""")
seg(sid, 5, """The gain is one integer per window instead of one ten-character string — no allocation inside the loop at """
            """all.""")

CODE = '''public IList<string> FindRepeatedDnaSequences(string s) {
    var result = new List<string>();
    if (s.Length < 10) return result;                       // no window exists

    var code = new Dictionary<char, int> { ['A'] = 0, ['C'] = 1, ['G'] = 2, ['T'] = 3 };
    const int Mask = (1 << 20) - 1;                         // keep the low 20 bits = 10 letters

    var seen = new HashSet<int>();
    var reported = new HashSet<int>();
    int window = 0;

    for (int i = 0; i < s.Length; i++) {
        window = ((window << 2) | code[s[i]]) & Mask;       // roll: O(1), no allocation

        if (i < 9) continue;                                // the first full window ends at index 9

        if (!seen.Add(window) && reported.Add(window))      // seen before, and not yet reported
            result.Add(s.Substring(i - 9, 10));             // materialise the string only for answers
    }
    return result;
}'''
code_slide('The C# implementation', CODE, [
 ('2-3', """Guard the short input first. A string shorter than ten characters has no window at all, and that is a real """
           """test case rather than a formality."""),
 ('5-6', """The letter-to-two-bit map, and the mask. Writing the mask as one shifted left twenty minus one says what it """
           """means; writing the hex literal directly does not."""),
 ('8-10', """Two sets and the rolling window. Two sets rather than one is deliberate: the first records what we have seen, """
            """the second records what we have already added to the answer, so a sequence appearing five times is reported """
            """once."""),
 ('12-13', """The roll itself, one line, no allocation. This is the line that replaced building a ten-character string """
             """every iteration."""),
 ('15', """Skip until the window is actually full. Index nine is the first position at which ten letters have been """
          """consumed — an off-by-one worth saying out loud as you write it."""),
 ('17-19', """And the reporting condition, which reads nicely once you know the trick: `seen.Add` returns false when the """
             """value was already there, and `reported.Add` returns true only the first time. So the whole "seen before and """
             """not yet reported" rule is one short-circuited expression. Note we only build a string for an actual """
             """answer — usually a handful, not n of them."""),
])

sid = beat('The judgement call', 'Should you actually write the clever version?',
           '<div style="font-size:30px;line-height:1.7">'
           'Both are O(n). The bit version saves <b>allocation</b>, not asymptotic time.<br><br>'
           '<b>Say this:</b> &ldquo;The straightforward version with a HashSet&lt;string&gt; is already O(n). The bit '
           'encoding removes n string allocations, which matters if this runs on a large genome or in a hot path. '
           'Shall I write the simple one first and then optimise?&rdquo;<br><br>'
           '<i>That sentence is worth more than either implementation.</i> It shows you know what you are buying and '
           'what it costs in readability &mdash; which is exactly what the Staff module says it scores.</div>',
           """Now the judgement call, which is why I chose this question. Both versions are linear. The bit encoding saves """
           """allocation, not asymptotic time.""", step=0)
seg(sid, 1, """So here is what I would actually say in the room. The straightforward version with a set of strings is """
            """already linear. The bit encoding removes n string allocations, which matters on a large genome or in a hot """
            """path. Shall I write the simple one first and then optimise?""")
seg(sid, 2, """That sentence is worth more than either implementation. It shows you know what the optimisation buys, what """
            """it costs in readability, and that you will not reach for cleverness reflexively — which is precisely what """
            """the official pack means when it says this module scores modularity and quality of decisions rather than """
            """speed of recall.""")

sid = cards('Edge cases and clarifications', [
 (0, 'String shorter than 10', 'Return empty. First test case, and it crashes a loop written carelessly.', 'deny'),
 (0, 'Characters outside ACGT', 'Ask. Real genomic data contains N for unknown. A dictionary lookup will throw &mdash; decide whether to skip or reject.', 'shared'),
 (1, 'A sequence repeated many times', 'Report it once. That is what the second set is for.', 'ok'),
 (1, 'Overlapping repeats', '"AAAAAAAAAAA" contains the same 10-mer twice, overlapping. It counts &mdash; nothing forbids overlap.', 'ok'),
 (2, 'Why 10 and not k?', 'At k &gt; 16 the code exceeds 32 bits. Use long for k &le; 32, then a real rolling hash with collision handling.', 'deny'),
 (2, 'Case sensitivity', 'Lowercase acgt appears in real FASTA files. One sentence to ask.', 'shared'),
], cols=2)
seg(sid, 0, """Edge cases. A string shorter than ten returns empty, and it is the first case that crashes careless code. """
            """Characters outside the four letters: real genomic data contains N for unknown, and a dictionary lookup will """
            """throw — so ask whether to skip those windows or reject the input. Knowing that N exists in real data is a """
            """nice touch if you have it.""")
seg(sid, 1, """A sequence repeated many times is reported once, which is what the second set handles. And overlapping """
            """repeats count — a run of eleven identical letters contains the same ten-mer twice, overlapping, and nothing """
            """in the problem forbids that.""")
seg(sid, 2, """Then the question that exposes the limits of the trick: why ten? Because above sixteen letters the code """
            """exceeds thirty-two bits. Up to thirty-two letters you can use a long; beyond that you need a genuine rolling """
            """hash with collision handling, which is a different problem with a different risk profile. Being able to say """
            """where your encoding stops working is a strong answer. And ask about case, because lowercase appears in real """
            """files.""")

followups(
 ['"Generalise to length k" — long up to k=32, then a polynomial rolling hash; now collisions are possible and you must verify matches',
  '"Return the counts, not just the repeats" — Dictionary<int,int> instead of two sets',
  '"Find the most frequent 10-mer" — same pass, track the max'],
 ['"A 3 GB genome that does not fit in memory" — stream it; the window state is 4 bytes, but the seen-set is the memory problem — that is where a Bloom filter earns its place',
  '"Distribute it across machines" — shard by the code\'s high bits so identical 10-mers land on the same machine; this is exactly a shuffle key',
  '"False positives are unacceptable" — then a Bloom filter needs a verification pass; say that a probabilistic filter is a pre-filter, never the answer'],
 """Follow-ups. Generalising to length k is the natural one: a long carries you to thirty-two letters, and beyond that you """
 """need a polynomial rolling hash — at which point collisions become possible and you must verify a match rather than """
 """trusting it. Returning counts instead of repeats is a dictionary instead of two sets. And the most frequent ten-mer """
 """is the same pass with a running maximum.""",
 """At staff level this question opens straight into systems, which suits an infrastructure interview. A three-gigabyte """
 """genome streams fine — the window state is four bytes — but the set of seen codes is the memory problem, and that is """
 """precisely where a Bloom filter earns its place. Distributing it is a lovely answer: shard by the high bits of the """
 """code so identical ten-mers land on the same machine, which is exactly choosing a shuffle key in a MapReduce job. And """
 """if false positives are unacceptable, say plainly that a probabilistic filter is a pre-filter and never the final """
 """answer — you follow it with verification.""")

interview_script([
 '"Sliding a 10-character window with a HashSet<string> is already O(n) — the window length is a constant, not a factor of n."',
 '"The real cost is allocating n short strings. I can remove that with a bit encoding."',
 '"A, C, G, T fit in two bits, so ten letters fit in twenty bits — the window becomes an int, rolled with a shift, an OR and a mask."',
 '"That is exact, not a hash, so there are no collisions to handle."',
 '"Shall I write the simple version first and then optimise? Both are O(n); the second just avoids allocation."',
 '"Above 16 letters the code overflows an int, and above 32 you need a real rolling hash — with collision verification."',
], [
 """The script. Start by pricing the simple solution correctly, because the two common mis-statements about its """
 """complexity are things an interviewer is listening for.""",
 """Then offer the optimisation with its actual benefit named — allocation, not asymptotics — and point out that the """
 """encoding is exact.""",
 """Then ask whether to write the simple one first. That question is not hedging; it is scoping, and it is what a staff """
 """engineer does before optimising. Close by naming where the trick breaks, which shows you understand its """
 """precondition rather than its syntax.""",
])

sid = statement('Lesson 6.1', 'Knowing a trick is common. Knowing when it is not worth it is rare.',
                'Both versions are O(n). Say what the clever one buys, what it costs, and let the interviewer choose.',
                kind='ok')
seg(sid, 0, """One line. Knowing a trick is common; knowing when the trick is not worth using is rare, and rarer is what """
            """gets hired.""")
seg(sid, 1, """Both versions here are linear. Say what the clever one buys, say what it costs in readability, and let the """
            """interviewer choose. Next lesson is the booths problem from your own list — where the first and hardest task """
            """is working out what is even being asked.""")
