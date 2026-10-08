# -*- coding: utf-8 -*-
"""Chapter 11 — the complete guide to the Coding-with-AI round: tutorial, concurrency, ten questions.

Every listing on screen is sliced out of the C# that `dotnet run` compiled and tested
(companies/linkedin/src/cs/aicoding: 126 assertions; cs/qbank: 269), via qbank_cs, so the
video cannot show code that was never verified. The "AI output" listings are the planted-
defect review exercises from Review.cs, each reproduced by a test.

Evidence is stated per question and nothing is claimed to be guaranteed: LRU and the logger
are reported for the AI round, LFU+rank once at Staff, the scheduler is a LinkedIn coding
question with the round unstated, and the window counter is pattern practice.
"""
import os, sys
from lib import *
import engine as E

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'companies', 'linkedin', 'src')))
import qbank_cs as CS


def ln(code, needle, after=0):
    """1-based line of the first line containing `needle` (at or after line `after`)."""
    for i, l in enumerate(code.split('\n'), 1):
        if i > after and needle in l:
            return i
    raise KeyError(needle)

def rng(code, a, b):
    s = ln(code, a)
    return '%d-%d' % (s, ln(code, b, s - 1))

def strip_comments(code):
    """Whole-line comments only; the listings keep their trailing comments."""
    return '\n'.join(l for l in code.split('\n') if not l.strip().startswith('//'))

WIDTH = 96

def fit(code, width=WIDTH):
    """Whitespace-only reflow for a 1080p slide: the tokens are exactly the compiled ones.
    A trailing comment moves onto its own line above; an over-long line breaks after '{', '=>' or ', '."""
    out = []
    for line in code.split('\n'):
        ind = line[:len(line) - len(line.lstrip())]
        code_part, comment = line, ''
        i = line.find('//')
        if i > 0 and line[:i].strip() and line.count('"', 0, i) % 2 == 0:
            code_part, comment = line[:i].rstrip(), line[i:]
        if comment and len(line) > width:
            out.append(ind + comment)
            line = code_part
        while len(line) > width:
            cut = -1
            for tok in (' { ', ' => ', ', ', ' = new '):
                j = line.rfind(tok, len(ind) + 8, width)
                if j > cut: cut, t = j, tok
            if cut < 0: break
            keep = len(t) if t.strip() in ('{', ',') else 0
            head = line[:cut + keep].rstrip() if keep else line[:cut].rstrip()
            rest = line[cut + keep:].lstrip() if keep else line[cut:].lstrip()
            out.append(head)
            line = ind + '    ' + rest
        out.append(line)
    return '\n'.join(out)

def halves(code, text, more='And the rest of the listing.'):
    """Narration blocks that let a long listing paginate: split at the last blank line before line 17."""
    n = len(code.split('\n'))
    if n <= 17: return [(None, text)]
    lines = code.split('\n')
    cut = max([i for i, l in enumerate(lines[:16], 1) if not l.strip()] or [16])
    return [('1-%d' % cut, text), ('%d-%d' % (cut + 1, n), more)]

def join(*parts):
    return '\n\n'.join(p.strip('\n') for p in parts)

def ship(title, code, ctx, narr_ctx, think_q, answer, fix, test, narr_answer):
    """'Would you ship this?' — AI-written code, a pause, then the defect and the test that proves it."""
    code = fit(code)
    code_slide(title, code, halves(code, narr_ctx), kicker='AI output · would you ship this?')
    think(think_q, 25, 'Pause here. Would you ship this? Find the defect before I tell you.',
          'Here is what is wrong with it.')
    sid = cards('What the assistant got wrong', [
        (0, 'The defect', answer, 'deny'),
        (1, 'The fix', fix, 'ok'),
        (2, 'The test that proves it', test, 'shared'),
    ], cols=1, kicker='Review')
    for i, t in enumerate(narr_answer):
        seg(sid, i, t)


lesson_header('11', 'The LinkedIn AI-assisted coding round — the complete guide',
              'Data structures · concurrency · caches · logger · scheduler · intervals · data', 'Highest',
              'Official pack + research pass 5 (Oct 2026)', 'Oct 2026', 'High', 70,
              """This is the complete guide to one round: LinkedIn's Coding with A I module. Sixty minutes, CoderPad, an A I """
              """assistant beside the editor, and you are expected to use it. It runs in order. What the round expects, from """
              """the recruiter pack and from candidate reports up to October twenty twenty-six. How to work with the assistant: """
              """what to delegate, four prompt templates, how to review, what to say. The C sharp data structures these """
              """questions are built from. Concurrency in C sharp from the ground up, because every question ends with "now make """
              """it thread-safe". How to test in the pad. Then ten questions, small systems rather than puzzles, each with the """
              """design, the prompt, the code, the assistant's mistake and the follow-ups. Then debugging code you did not write, """
              """and finally the whole sixty minutes run end to end. Every listing compiled and passed its tests, and every """
              """concurrency number was measured.""")

# ======================================================================== part 0: the round
E.chapter(0, 'What the round expects', 'Official pack · how it runs · how to work',
          """First, what the round expects, in the recruiter's own words, and then how to work inside it.""")

sid = cards('What the official pack says is evaluated', [
    (0, 'Fundamentals', 'Apply strong engineering fundamentals to solve technical problems', 'info'),
    (1, 'Intentional AI use', 'Use AI intentionally to support and accelerate your workflow', 'ok'),
    (2, 'Critical evaluation', 'Evaluate AI-generated output critically, not at face value', 'deny'),
    (3, 'Iterate', 'Identify issues, make improvements, iterate', 'shared'),
    (4, 'Communicate', 'Explain technical decisions and trade-offs clearly', 'dp'),
    (5, 'Own it', 'Correct, maintainable, well-reasoned — you own the final solution', 'cp'),
], cols=2, kicker='LinkedIn recruiter pack · CWAI')
seg(sid, 0, """This is from the recruiter pack for the Staff onsite. Six things are evaluated. First, fundamentals: you still """
            """have to be able to solve the problem.""")
seg(sid, 1, """Second, using A I intentionally. The pack is explicit that using it is expected, not optional.""")
seg(sid, 2, """Third, and this is the one the round is built around: evaluating A I output critically, rather than accepting it """
            """at face value.""")
seg(sid, 3, """Fourth, finding issues and iterating.""")
seg(sid, 4, """Fifth, communicating decisions and trade-offs as you go.""")
seg(sid, 5, """And sixth: you own the final solution. You must understand it, validate it, explain it and fix it. If you paste """
            """code you cannot explain, you have failed the one thing the round is measuring.""")

sid = steps_list('How the round runs (reports to Oct 2026)', [
    (0, '**CoderPad + an AI chat panel**; Claude models reported among the options. It cannot edit your code — you paste', 'info'),
    (1, 'Often **boilerplate + test cases provided**, or a small codebase: fix → extend → optimise. **Optimal solutions weigh more**', 'info'),
    (2, 'Requirements **escalate**, and almost always end in "now make it thread-safe / production-ready"', 'shared'),
    (3, 'The interviewer **interrupts**: why that prompt, and how do you know it works?', 'shared'),
    (4, 'Reported scale: **4 points, 3 passes** — prompts, verification, production thinking, communication', 'ok'),
    (5, 'Most-reported mistake: **too long on the first task**, no time for the follow-ups', 'deny'),
])
seg(sid, 0, """How it runs, from candidate reports up to October twenty twenty-six. CoderPad, with an A I chat panel; Claude """
            """models are reported among the options. The assistant cannot edit your code. You copy what you choose, which """
            """means every line that lands in the editor passed through your hands.""")
seg(sid, 1, """Several reports describe a starting point rather than a blank editor: boilerplate code and test cases already """
            """provided, or a small codebase, with tasks that escalate: fix a bug, add a feature, then optimise. And one LeetCode """
            """Discuss report adds a useful detail: implementing the optimal solution carries more weight. Working but slow is not """
            """enough.""")
seg(sid, 2, """And it almost always ends with production concerns: make it thread-safe, make it scale.""")
seg(sid, 3, """The interviewer will interrupt. Why did you ask for that? How do you know the generated code is correct?""")
seg(sid, 4, """Hello Interview reports a four-point scale where three passes, scored on prompt quality, verification of A I """
            """output, production thinking and communication. That comes from candidate reports, not from LinkedIn.""")
seg(sid, 5, """And the most repeated mistake: spending too long on the first task and running out of time for the follow-ups, """
            """which is where the Staff signal is.""")

EVID = [
    ['Logging library: severity, throttle, aggregate', '5 reports, Aug–Sep 2026, one Staff', 'Q4'],
    ['LRU → concurrency → production; "add key validation"', 'AI-round reports, guides, LeetCode Discuss', 'Q1'],
    ['LRU with counters: predict hit / miss', 'PracHub (Sep 2026) + LeetCode Discuss', 'Q2'],
    ['LFU cache, eviction by rank', 'Reported at Staff (Feb 2026)', 'Q3'],
    ['Modified merge intervals, 3 incremental parts', '2 sources + LeetCode Discuss; "next interval" named', 'Q7'],
    ['Structured data: JSON-like records + tests', '2 independent sources', 'Q8'],
    ['Friendship graph: path → distance → suggestions', 'LeetCode Discuss, Oct 2026 — tests provided', 'Q9'],
    ['Router placement among houses · robots capturing "Sara"', 'Named once in a 2026 list — no statement found', 'Named only'],
]
EVNARR = [
    """What is reported, and how strongly. The logging library is the freshest and strongest: five reports in August and """
    """September, one of them Staff. That is question four.""",
    """The L R U cache with concurrency follow-ups, from A I-round reports, guides and a LeetCode Discuss report that adds a """
    """key-validation step. Question one.""",
    """The L R U cache with counters, where you predict the hit and miss ratio for different workloads. Reported twice. """
    """Question two.""",
    """The L F U cache with a rank function, reported at Staff level. Question three.""",
    """A modified merge intervals question in three incremental parts, which matches the interval manager reported by two """
    """other sources. Question seven.""",
    """Structured data processing, from two independent sources. Question eight.""",
    """A friendship graph in three parts, path, distance and suggestions, with boilerplate and tests provided. Question """
    """nine.""",
    """And two names that appear in one twenty twenty-six list with no statement anywhere: router placement among houses, """
    """and robots capturing Sara. This video does not invent them. If you meet them, they look like graph and grid search: """
    """clarify the rules first, then design."""]
for title, lo, hi in [('What is reported for this round (1 of 2)', 0, 4), ('What is reported for this round (2 of 2)', 4, 8)]:
    sid = table(title, ['Question', 'Evidence', 'In this video'], [(k - lo, EVID[k]) for k in range(lo, hi)],
                kicker='Research pass 5 · Oct 2026 + your LeetCode Discuss reports')
    for k in range(lo, hi):
        seg(sid, k - lo, EVNARR[k])

sid = steps_list('The loop I use for every phase', [
    (0, '**Understand** — restate it, ask what the answer changes, write 3 test cases by hand', 'info'),
    (1, '**Design** — data structures and the invariant, out loud, before any prompt', 'info'),
    (2, '**Prompt narrowly** — language, types, complexity, what NOT to do yet', 'ok'),
    (3, '**Read every line** — would I ship this? Check the invariant, not the style', 'deny'),
    (4, '**Verify** — run my hand-written cases + the edge that breaks it', 'shared'),
    (5, '**Defend** — say the trade-off, then take the next phase', 'dp'),
])
seg(sid, 0, """Here is the loop I use for every phase. Understand: restate the problem and write three test cases by hand, """
            """before the assistant writes anything. Those three cases are your independent check.""")
seg(sid, 1, """Design: name the data structures and the invariant out loud. That is your contribution, and it is what lets you """
            """judge the code that comes back.""")
seg(sid, 2, """Prompt narrowly: the language, the types, the complexity you want, and what not to do yet. A narrow prompt """
            """gets code you can read in a minute.""")
seg(sid, 3, """Read every line, and ask: would I ship this? Check it against the invariant, not the formatting.""")
seg(sid, 4, """Verify: run your hand-written cases, plus the one edge case most likely to break it.""")
seg(sid, 5, """And defend: say the trade-off you made, then take the next phase. Six steps, and on a good phase the whole loop """
            """takes ten to twelve minutes.""")

sid = table('A 60-minute plan (my estimate)', ['Minutes', 'What', 'Why'], [
    (0, ['0–5', 'Clarify, 3 hand cases, design out loud', 'Your design is what you judge the AI against']),
    (1, ['5–20', 'Phase 1 with AI, read, run, fix', 'Correct and tested — not perfect']),
    (2, ['20–35', 'Phase 2 and 3 (TTL, rank, throttle…)', 'Where most candidates run out of time']),
    (3, ['35–50', 'Thread-safety and production', 'Where the Staff signal is']),
    (4, ['50–60', 'Trade-offs, what you would change', 'Leave them with a decision, not code']),
], kicker='Time plan · INFERENCE')
seg(sid, 0, """A time plan. Nobody has published real timings for this round, so treat this as my estimate. Five minutes to """
            """clarify and design.""")
seg(sid, 1, """Fifteen minutes for phase one, including reading and running what the assistant gives you.""")
seg(sid, 2, """Fifteen for the next phases.""")
seg(sid, 3, """Fifteen for thread-safety and production questions, because that is where the Staff signal is.""")
seg(sid, 4, """And the last ten for trade-offs. If you are behind, cut polish, never the follow-ups.""")

sid = compare('What marks you down, and what marks you up',
    ('Marks you down', 'deny', 0, ['Asking for the full solution before stating a design',
                                    'Pasting code you then cannot explain line by line',
                                    'Never running anything — "it looks right"',
                                    'Accepting "it is thread-safe" because the assistant said so']),
    ('Marks you up', 'ok', 1, ['Using AI for the mechanical parts: boilerplate, tests, a second opinion',
                                'Catching a real defect in AI output, and proving it with a test',
                                'Saying what you checked, and why',
                                'Naming the trade-off before the interviewer asks']))
seg(sid, 0, """What marks you down. Asking for the whole solution before you have said a design. Pasting code you cannot then """
            """explain. Never running anything. And accepting the assistant's claim that something is thread-safe.""")
seg(sid, 1, """What marks you up. Using the assistant for the mechanical work, boilerplate and tests and a second opinion. """
            """Catching a real defect in its output and proving it with a test. Saying what you checked. And naming the trade-off """
            """before you are asked. Every question that follows has a moment where the assistant gets something subtly """
            """wrong, because that moment is the round.""")

# ======================================================================== Q1 LRU
# ======================================================================== part A: the C# toolbox
# ======================================================================== working with the assistant
E.chapter(1, 'Working with the assistant', 'What to delegate, the prompts, how to review, what to say',
          """Chapter one: working with the assistant itself. What to hand it, what never to hand it, the four prompts that """
          """cover almost everything, how to review what comes back, and what to say out loud while you do it.""")

sid = compare('Delegate, or keep',
    ('Delegate — you can check it faster than you can write it', 'ok', 0,
     ['Implementing a design **you** specified', 'Boilerplate: model classes, parsing, test scaffolding',
      'Two alternative approaches to compare, no code', 'A second reader hunting a **named** class of bug', 'A complexity check']),
    ('Keep — this is what is being scored', 'deny', 1,
     ['The data structure, and why', 'The invariant the structure maintains', 'The synchronisation boundary',
      'The API contract: what happens on a miss and on bad input', 'The decision about what "correct" means']))
seg(sid, 0, """What to delegate. The test is simple: could you check the answer faster than you could write it? Implementing a """
            """design you specified, boilerplate like model classes and test scaffolding, alternatives to compare, a second """
            """reader hunting a named class of bug, and a complexity check.""")
seg(sid, 1, """And what to keep, because it is exactly what is being scored: the data structure, the invariant, the """
            """synchronisation boundary, the API contract, and the decision about what correct means. If you find yourself """
            """reading the assistant's output to learn what your design is, you handed over the wrong thing.""")

PROMPTS = [
    ('Implement', 'Implement this C# interface. First state your assumptions, the data structures and the complexity of each '
                  'method. Minimal and testable: no extra public members. <interface + my field declarations>',
     """The implementation prompt. Give it your interface and your own field declarations, which pins the data structures """
     """so the design stays yours. Ask it to state its assumptions before writing code: you catch a wrong assumption """
     """before reading sixty lines. And no extra public members, so it cannot widen your API."""),
    ('Review', 'Review this for correctness, edge cases, complexity and concurrency. Do not rewrite it. List problems, most '
               'severe first, each with the input that triggers it. <code>',
     """The review prompt. Do not rewrite it keeps the answer short enough to verify. And the input that triggers it turns """
     """a vague worry into a test you can run in ten seconds, which also exposes false alarms."""),
    ('Tests', 'Generate adversarial tests as plain assertions: boundaries, duplicates, empty, capacity one, concurrent access. '
              'For each, say in a comment why the expected value is correct. <code + my contract>',
     """The test prompt. Plain assertions, because the pad may have no test framework. And the line that matters: say why """
     """the expected value is correct. Wrong expected values are the assistant's most common test defect."""),
    ('Optimise', 'Analyse this for bottlenecks under <workload>. Do not change the public API. For each suggestion give the '
                 'complexity before and after, and what it costs. <code>',
     """And the optimisation prompt, for when the interviewer says millions of requests. Name the workload, freeze the """
     """API, and ask what each change costs, so you can say the trade-off rather than just apply it."""),
]
for name, text, narr in PROMPTS:
    sid = statement('Prompt template · ' + name, text, None, kind='ok', kicker='Working with the assistant')
    seg(sid, 0, narr)

sid = steps_list('Reviewing AI output: the order that matches what bugs cost', [
    (0, '**Contract on the edges** — empty, one, capacity, duplicate, a miss', 'deny'),
    (1, '**Complexity** — against the target **you** stated', 'shared'),
    (2, '**Shared state** — what is mutated, and what protects it', 'deny'),
    (3, '**Bad input** — what happens, and is it reported?', 'shared'),
    (4, '**Growth** — what is unbounded: a map, a queue, a list of windows?', 'info'),
])
for i, t in enumerate([
    """How to review what comes back, in the order the bugs cost you. First the contract on the edges: empty, one, """
    """capacity, a duplicate, a miss.""",
    """Then complexity, against the target you stated before the assistant did.""",
    """Then shared state: what is mutated, and what protects it.""",
    """Then bad input: what happens, and is it reported or swallowed?""",
    """And growth: anything unbounded, a map, a queue, a table of windows. Say each check out loud, in one sentence."""]):
    seg(sid, i, t)

interview_script([
    'Before prompting: "I\'ll design first — dictionary plus linked list, invariant is both hold the same keys."',
    'While prompting: "I\'m giving it my interface and fields, and asking only for the list manipulation."',
    'Reviewing: "Checking the eviction path first — that\'s where this usually goes wrong."',
    'Rejecting: "This uses a ConcurrentDictionary but the list is unprotected, so I\'m not taking it."',
    'Verifying: "Running my three cases plus eviction-after-read."',
    'Deciding: "One lock is enough here; if contention shows up, I\'d shard by key."',
], ["""What to say out loud while you work. Before prompting, say your design. While prompting, say what you asked for and """
    """why only that.""",
    """While reviewing, say which part you are checking first and why. When you reject something, give the reason in one """
    """sentence.""",
    """And when you verify and decide, say what you ran and what you chose. The interviewer is scoring your judgement, and """
    """they can only score what they hear."""])

E.chapter(2, 'The C# toolbox', 'Data structures these questions are built from',
          """Chapter two is a tutorial. Before any question, the data structures in C sharp that every one of these designs is """
          """built from, and the single property of each that decides whether your design is constant time, log n, or """
          """quietly linear. The assistant knows these APIs. Your job is to know which property matters, so you can catch it """
          """when it picks the wrong one.""")

sid = table('The collections, and what each costs', ['Collection', 'Cost that matters', 'Used for'], [
    (0, ['`Dictionary<K,V>` / `HashSet<T>`', 'O(1) lookup, add, remove', 'Every key → state map']),
    (1, ['`LinkedList<T>` + `LinkedListNode<T>`', 'O(1) remove **only with the node**', 'LRU recency, LFU buckets']),
    (2, ['`PriorityQueue<T, P>`', 'O(log n) enqueue/dequeue · **no update, no remove**', 'Scheduler, top-k, timers']),
    (3, ['`SortedSet<T>` / `SortedDictionary`', 'O(log n) · floor/ceiling via views', 'Intervals, ranks, ordered keys']),
    (4, ['`Queue<T>` / `Stack<T>`', 'O(1) ends', 'BFS, buffers, undo']),
    (5, ['`T[]` used as a ring', 'Fixed memory, O(1) slot', 'Sliding windows, rate limits']),
], kicker='Toolbox')
for i, t in enumerate([
    """Dictionary and hash set: constant time lookup, add and remove. Every one of these questions has a key to state map """
    """at its centre.""",
    """Linked list: constant time removal, but only if you hold the node. That one condition is why an L R U stores node """
    """handles in its dictionary.""",
    """Priority queue: log n in and out, and no update and no remove. That shapes the scheduler, as you will see.""",
    """Sorted set and sorted dictionary: red-black trees, log n, and floor and ceiling queries through views. Intervals and """
    """ranks live here.""",
    """Queue and stack: constant time at the ends. Breadth-first search, buffers, undo.""",
    """And a plain array used as a ring: fixed memory, constant time per slot. Sliding windows and rate limiters."""]):
    seg(sid, i, t)

def slice_file(rel, first, last):
    """Lines of a tested source file from the one containing `first` to the one containing `last`."""
    lines = CS._read(rel).split('\n')
    i = next(k for k, l in enumerate(lines) if first in l)
    j = next(k for k, l in enumerate(lines) if k >= i and last in l)
    return '\n'.join(lines[i:j + 1])

DS1 = fit(slice_file('tutorial/DataStructures.cs', '// ---- DS1', 'public readonly record struct LogKey'))
code_slide('Composite keys: a record struct', DS1, [
    (None, """A composite key. The logger needs four fields to decide that two logs are identical. A record struct gives you """
           """value equality and hashing for free, so a new instance with the same four fields finds the same dictionary """
           """entry. A tuple works too. A class does not: two equal-looking class keys are two different entries, and an """
           """assistant will sometimes hand you exactly that. The test for this is one line: put with one instance, look up """
           """with another."""),
], kicker='Toolbox · Dictionary keys')

DS2 = fit(join(CS.cs_type('tutorial/DataStructures.cs', 'JobQueue', comment=False)))
code_slide('PriorityQueue: tie-breaks and lazy removal', DS2, [
    (rng(DS2, 'private readonly PriorityQueue', 'private long _seq;'),
     """The priority is a tuple: due time, then a sequence number."""),
    (rng(DS2, 'public Job Add', 'return j;'),
     """Each add takes the next sequence number. Without it, equal priorities come out in no guaranteed order, and a test """
     """that expects submission order fails at random."""),
    ('%d-%d' % (ln(DS2, 'public Job PopDue'), len(DS2.split('\n'))),
     """The priority queue cannot remove an arbitrary item. So cancelling is lazy: mark the job, and drop it when it """
     """reaches the head. This is exactly how the scheduler later handles cancel."""),
], kicker='Toolbox · PriorityQueue')

DS4 = fit(CS.cs_type('tutorial/DataStructures.cs', 'SortedOps', comment=False))
code_slide('SortedSet: floor and ceiling in O(log n)', DS4, [
    (rng(DS4, 'public static int? Floor', 'return s.GetViewBetween(s.Min, x).Max;'),
     """Floor: the largest element at or below x. Guard the empty and out-of-range cases, then take a view up to x and ask """
     """for its max. Log n."""),
    (rng(DS4, 'public static int? Ceiling', 'return s.GetViewBetween(x, s.Max).Min;'),
     """Ceiling is the mirror image. One trap worth knowing: a view's Count walks the whole range. It is linear, not log n. """
     """Our own question bank shipped an insert that called it and was quietly order n, until a ten-million-element test """
     """timed out. Use Min and Max on views, never Count."""),
], kicker='Toolbox · SortedSet')

DS5 = fit(CS.cs_type('tutorial/DataStructures.cs', 'Ring', comment=False))
code_slide('An array as a ring buffer', DS5, [
    (rng(DS5, 'private readonly long[] _stamp', 'public Ring(int n)'),
     """A ring: two fixed arrays, a stamp for which time each slot holds, and the value."""),
    (rng(DS5, 'public void Add', '_value[i] += v;'),
     """The slot is time modulo N. If the slot holds an older time, reset it before adding. Memory is N forever, whatever the """
     """event rate. That is the whole trick behind the window counter and most rate limiters."""),
], kicker='Toolbox · arrays')

sid = cards('Five traps an assistant walks into', [
    (0, 'LinkedList.Remove(value)', 'Linear search. Remove the **node** you stored', 'deny'),
    (1, 'PriorityQueue order', 'Equal priorities are unordered. Add a sequence number', 'deny'),
    (2, 'SortedSet uniqueness', 'Two items comparing equal → the second is **silently dropped**', 'deny'),
    (3, 'View.Count', 'O(view size). Use Min / Max', 'deny'),
    (4, 'Dictionary order', 'Enumeration order is not a contract. Sort if order matters', 'deny'),
], cols=2, kicker='Toolbox · traps')
for i, t in enumerate([
    """Five traps. Removing from a linked list by value is a linear search; remove the node.""",
    """A priority queue does not order equal priorities; add a sequence number.""",
    """A sorted set treats two items that compare equal as the same item, and silently drops the second. If your comparer """
    """looks only at a start time, two intervals with the same start collapse into one.""",
    """A view's count is linear.""",
    """And dictionary enumeration order is not a contract. If the output order matters, sort it."""]):
    seg(sid, i, t)

# ======================================================================== part B: concurrency
E.chapter(3, 'Concurrency in C#, from the ground up', 'Every follow-up in this round ends here',
          """Chapter three, and the most important tutorial in this video: concurrency in C sharp. Every question in this round """
          """ends with "now make it thread-safe" or "now productionise it", and that is where the Staff signal is. Every """
          """number you will hear in this part was measured by a test, not quoted from memory.""")

C1 = fit(join(CS.cs_type('tutorial/Concurrency.cs', 'UnsafeCounter', comment=False),
              CS.cs_type('tutorial/Concurrency.cs', 'LockedCounter', comment=False),
              CS.cs_type('tutorial/Concurrency.cs', 'AtomicCounter', comment=False)))
code_slide('1 · A race condition, and the two fixes', C1, [
    (rng(C1, 'public sealed class UnsafeCounter', 'public sealed class UnsafeCounter'),
     """The simplest race. Count plus plus looks like one step. It is three: read, add, write. Two threads read the same """
     """value, both add one, both write, and one increment is lost. Eight threads each incrementing a million times lost """
     """sixty-eight percent of the increments in our test."""),
    (rng(C1, 'public sealed class LockedCounter', 'public long Value { get { lock'),
     """Fix one: a lock. Note the lock object is private. Never lock on this, or on a string, because code you do not own """
     """can take the same lock. And the read takes the lock too: a lock gives you mutual exclusion and visibility."""),
    (rng(C1, 'public sealed class AtomicCounter', 'public long Value => Interlocked.Read'),
     """Fix two: Interlocked dot increment, a single atomic instruction. For a single number it is the natural tool. Under """
     """this heavy contention it was not faster than the lock in our measurement, about two hundred and fifty milliseconds """
     """either way for eight million increments, so do not claim it is free. Claim it is simple."""),
], kicker='Concurrency · races')

C2 = fit(join(CS.cs_type('tutorial/Concurrency.cs', 'UnsafePageViews', comment=False),
              CS.cs_type('tutorial/Concurrency.cs', 'PageViews', comment=False)))
code_slide('2 · Thread-safe collection, unsafe code', C2, [
    (rng(C2, 'public sealed class UnsafePageViews', '_d[page] = n + 1;'),
     """The most common wrong answer in this round. A concurrent dictionary makes each call atomic. Two calls in a row are """
     """not. Between the try-get and the set, another thread can do the same thing, and a hit is lost. Measured: one point """
     """six million hits recorded as two hundred and eighty-three thousand."""),
    (rng(C2, 'public sealed class PageViews', 'public int Get(string page)'),
     """The fix is to make the whole read-modify-write one call: add or update. Exact. The general rule: the unit of """
     """atomicity must cover the whole invariant, not each individual call."""),
], kicker='Concurrency · check-then-act')

C3 = fit(join(CS.cs_type('tutorial/Concurrency.cs', 'UnsafeLoader', comment=False),
              CS.cs_type('tutorial/Concurrency.cs', 'OnceLoader', comment=False)))
code_slide('3 · GetOrAdd runs the factory more than once', C3, [
    (rng(C3, 'public sealed class UnsafeLoader', 'public string Get(string key) => _cache.GetOrAdd(key, _load);'),
     """A read-through cache. Get or add looks atomic, and it is, for the stored value. But the factory can run once per """
     """racing thread. Eight concurrent first reads made eight calls to the slow service in our test. At a cache miss storm, """
     """that is a stampede on your database."""),
    (rng(C3, 'public sealed class OnceLoader', 'LazyThreadSafetyMode.ExecutionAndPublication'),
     """The fix: store a Lazy of the value. Get or add may create several Lazy wrappers, but only one is stored, and only """
     """the stored one ever runs its load. Exactly one call, measured."""),
], kicker='Concurrency · caches')

C4 = fit(CS.cs_type('tutorial/Concurrency.cs', 'Gate', comment=False))
code_slide('4 · Waiting for a condition: Monitor.Wait and PulseAll', C4, [
    (rng(C4, 'public void WaitOpen', 'Monitor.Wait(_lock);'),
     """Waiting for something to become true. Monitor dot wait releases the lock while you sleep and takes it back before it """
     """returns. And it always sits inside a while loop, never an if. Wakes can be spurious, and by the time you run, another """
     """thread may have taken what you woke up for."""),
    (rng(C4, 'public void Open', 'Monitor.PulseAll'),
     """Change the state under the lock, then pulse all. A single pulse wakes one arbitrary waiter, which may be the wrong """
     """kind of waiter. This is the pattern under every blocking queue and the scheduler."""),
], kicker='Concurrency · conditions')

C5 = fit(CS.cs_type('tutorial/Concurrency.cs', 'Transfers', comment=False))
code_slide('5 · Deadlock, and lock ordering', C5, [
    (rng(C5, 'public static void Unsafe', 'lock (from.Lock)'),
     """Deadlock. Thread A transfers from X to Y and locks X. Thread B transfers from Y to X and locks Y. Each now waits for """
     """the other's lock, forever. Our test reproduces it every time."""),
    (rng(C5, 'public static void Ordered', 'lock (first.Lock) lock (second.Lock)'),
     """The fix: every thread takes locks in one global order, here by account id. Two hundred thousand opposite transfers """
     """finish, and the money is conserved. If you ever need two locks, say the order out loud."""),
], kicker='Concurrency · deadlock')

C6 = fit(CS.cs_member('tutorial/Concurrency.cs', 'AsyncCache', 'public async Task<string> GetAsync', comment=False))
code_slide('6 · Async: SemaphoreSlim, and Release in finally', C6, [
    (rng(C6, 'public async Task<string> GetAsync', 'await _gate.WaitAsync();'),
     """Async code cannot hold a lock across an await; the compiler rejects it. The async mutex is a semaphore slim with """
     """a count of one, and you await wait-async."""),
    (rng(C6, 'try {', '_gate.Release();'),
     """And the release must be in a finally. Without it, one failed load leaves the semaphore held, and every later caller """
     """waits forever. Our test makes the first load throw and checks that the next call still completes."""),
], kicker='Concurrency · async')

C7 = fit(CS.cs_type('tutorial/Concurrency.cs', 'Config', comment=False))
code_slide('7 · Many readers, rare writers: ReaderWriterLockSlim', C7, [
    (rng(C7, 'public string Get', 'finally { _rw.ExitReadLock(); }'),
     """When reads vastly outnumber writes, and reads do not change anything, a reader-writer lock lets every reader run """
     """at once. Enter and exit always pair up in a try-finally."""),
    (rng(C7, 'public void Set', 'finally { _rw.ExitWriteLock(); }'),
     """A writer waits for readers to leave and then has the structure alone. This fits the interval manager's queries. It """
     """does not fit an L R U, because an L R U's get moves a node: every get is a write."""),
], kicker='Concurrency · read-mostly')

C11 = fit(CS.cs_type('tutorial/Concurrency.cs', 'SnapshotConfig', comment=False))
code_slide('8 · No locks at all: swap an immutable snapshot', C11, [
    (rng(C11, 'private Dictionary<string, string> _current', 'public IReadOnlyDictionary'),
     """An even simpler read-mostly answer. Readers read one reference, with no lock, and never mutate what they read."""),
    (rng(C11, 'public void Publish', 'public void Publish'),
     """A writer builds a complete new dictionary and swaps the reference in one atomic write. Readers see the old version """
     """or the new one, never a mix. Our test ran four readers against twenty thousand swaps and found zero torn reads. """
     """This is how feature flags and denylists are usually shipped to a fleet."""),
], kicker='Concurrency · snapshots')

C8 = fit(CS.cs_member('tutorial/Concurrency.cs', 'Pipeline', 'public static async Task<long> RunAsync', comment=False))
code_slide('9 · Producer and consumer: a bounded Channel', C8, [
    (rng(C8, 'var ch = Channel.CreateBounded', 'FullMode = BoundedChannelFullMode.Wait'),
     """Producer and consumer, the production way: a bounded channel. Bounded is the important word. An unbounded queue """
     """hides a slow consumer until you run out of memory."""),
    (rng(C8, 'var producer = Task.Run', 'ch.Writer.Complete();'),
     """Write-async waits when the channel is full. That wait is back-pressure, the producer slows to the consumer's pace. """
     """Complete tells the reader no more items are coming."""),
    (rng(C8, 'long sum = 0;', 'return sum;'),
     """The reader drains until the writer completes. A hundred thousand items, each delivered exactly once, tested."""),
], kicker='Concurrency · pipelines')

C9 = fit(CS.cs_type('tutorial/Concurrency.cs', 'StripedCounts', comment=False))
code_slide('10 · When one lock is the bottleneck: stripe it', C9, [
    (rng(C9, 'private readonly object[] _locks', 'for (int i = 0; i < stripes; i++)'),
     """Lock striping. N locks and N small maps instead of one of each."""),
    (rng(C9, 'private int Stripe', 'public long Get'),
     """The key's hash picks a stripe. Two operations on the same key always take the same lock, so each key stays exact, """
     """while different keys mostly take different locks, so contention divides by N. The sharded L R U is the same idea."""),
], kicker='Concurrency · contention')

C10 = fit(CS.cs_type('tutorial/Concurrency.cs', 'Worker', comment=False))
code_slide('11 · Stopping work: CancellationToken', C10, [
    (None, """Stopping a worker. Use a cancellation token, not a plain boolean. A plain boolean read in a tight loop can be """
           """hoisted by the compiler and never re-read, so the loop never ends. The token is thread-safe, and it composes: """
           """the same token can stop a channel read, a delay and an H T T P call. Graceful shutdown in every follow-up starts """
           """here."""),
], kicker='Concurrency · shutdown')

sid = cards('Three async traps to name if asked', [
    (0, '.Result / .Wait() on async code', 'Blocks a thread waiting for work that may need that thread → thread-pool starvation, or deadlock under a sync context. Await all the way down', 'deny'),
    (1, 'async void', 'Exceptions cannot be caught by the caller and can crash the process. Return Task', 'deny'),
    (2, 'Fire-and-forget Task.Run', 'Nobody observes its failure. Keep the Task, or log inside it', 'deny'),
], cols=1, kicker='Concurrency · async · general knowledge')
for i, t in enumerate([
    """Three async traps worth naming if the conversation goes there. This is general knowledge, not something we measured. """
    """Calling dot result or dot wait on async code blocks a thread while waiting for work that may need a thread, which """
    """starves the thread pool or deadlocks under a synchronisation context. Await all the way down.""",
    """Async void: the caller cannot catch its exceptions, and they can take down the process. Return a task.""",
    """And fire-and-forget: a task nobody keeps is a failure nobody sees. Keep it, or log inside it."""]):
    seg(sid, i, t)

sid = table('Which primitive, when', ['Situation', 'Reach for', 'Say this'], [
    (0, ['One number', '`Interlocked`', 'Atomic, no lock — simple, not magic']),
    (1, ['Several fields that change together', '`lock` around the whole operation', 'The lock covers the invariant']),
    (2, ['Many readers, rare writers, reads do not mutate', '`ReaderWriterLockSlim`', 'Not for LRU — its Get writes']),
    (3, ['Wait until a condition holds', '`Monitor.Wait` in a **while** + `PulseAll`', 'Re-check after every wake']),
    (4, ['Producer / consumer', 'Bounded `Channel<T>`', 'Back-pressure, clean completion']),
    (5, ['Async critical section', '`SemaphoreSlim(1,1)` + finally', 'No lock across await']),
    (6, ['One lock is the bottleneck', 'Stripe / shard by key', 'Exact per key, contention ÷ N']),
    (7, ['Stop a worker', '`CancellationToken`', 'Not a plain bool flag']),
], kicker='Concurrency · cheat sheet')
for i, t in enumerate([
    """The cheat sheet. One number: Interlocked.""",
    """Several fields that must change together: one lock around the whole operation. This is the L R U, the L F U and the """
    """logger.""",
    """Many readers, rare writers, and reads that do not mutate: a reader-writer lock. Not for an L R U, whose get moves a """
    """node.""",
    """Waiting for a condition: monitor wait inside a while loop, with pulse all.""",
    """Producer and consumer: a bounded channel, which gives you back-pressure and a clean completion signal.""",
    """An async critical section: a semaphore slim, released in finally.""",
    """When one lock becomes the bottleneck: stripe or shard by key.""",
    """And to stop a worker: a cancellation token, not a plain boolean, which the compiler may cache and never re-read."""]):
    seg(sid, i, t)

think('Your LRU uses one lock. The interviewer says it is too slow at 50,000 requests per second. What do you say first?', 20,
      """Pause. Your L R U uses one lock, and the interviewer says it is too slow at fifty thousand requests a second. What """
      """do you say first?""",
      """First, measure: is the lock actually the bottleneck, or is it the work done under it? Keep the critical section to """
      """the pointer moves, nothing slow. Then shard by key hash, and say the cost: the cache becomes approximately L R U. """
      """Do not reach for a reader-writer lock: every get is a write.""")

# ======================================================================== testing in the pad
E.chapter(4, 'Testing your code in CoderPad', 'No framework needed: a ten-line harness and a stress test',
          """Chapter four, and it is short. How to test in the pad. There may be no test framework, and you do not want to debug """
          """test infrastructure in an interview. Ten lines of harness and one stress helper are enough for everything in """
          """this video.""")

HARNESS = fit(CS.cs_type('aicoding/Tests.cs', 'T', comment=False))
code_slide('A ten-line assertion harness', HARNESS, [
    (rng(HARNESS, 'static int pass', 'else { fail++;'),
     """A static class with a pass and fail count. Eq compares and prints only failures, with what it got and what it """
     """wanted."""),
    (rng(HARNESS, 'public static void True', 'public static int Report()'),
     """True is Eq with a boolean, and Report prints the totals. Type this yourself or have the assistant generate it in """
     """the first minute: it is boilerplate, exactly what to delegate. Every C sharp file behind this video is tested with """
     """this harness."""),
], kicker='Testing')

STRESS = fit(CS.cs_type('tutorial/Concurrency.cs', 'Stress', comment=False))
code_slide('Proving thread-safety: a stress helper', STRESS, [
    (rng(STRESS, 'public static void Run', 'using var start = new Barrier(threads);'),
     """A stress helper. A barrier holds every thread until all of them are ready, so they start at the same instant and """
     """overlap as much as possible."""),
    (rng(STRESS, 'var ts = Enumerable.Range', 'ts.ForEach(t => t.Join());'),
     """Each thread runs the operation many times, then you check an invariant: a count is exact, money is conserved, a """
     """cache's map and list hold the same number of entries. Eight threads, two hundred and fifty thousand increments """
     """each: the atomic counter was exact, and the unsafe one recorded three hundred thousand of two million."""),
], kicker='Testing')

sid = table('What to test, for every question in this video', ['Kind', 'Examples'], [
    (0, ['The edges', 'Empty · one · capacity 1 · duplicate key · a miss']),
    (1, ['The invariant', 'Evict-after-read (LRU) · contained interval (merge) · exactly at the boundary (window)']),
    (2, ['Bad input', 'Capacity 0 · inverted interval · malformed record — reported, not swallowed']),
    (3, ['Time', 'Injected clock: exactly at TTL, one before, one after — never Thread.Sleep']),
    (4, ['Concurrency', 'Stress with a Barrier, then check an invariant that a race would break']),
], kicker='Testing')
for i, t in enumerate([
    """What to test, for every question here. The edges: empty, one, capacity one, a duplicate, a miss.""",
    """The invariant: eviction after a read for an L R U, a contained interval for a merge, exactly at the boundary for a """
    """window.""",
    """Bad input: and check it is reported, not swallowed.""",
    """Time: with an injected clock, exactly at the expiry, one before and one after. Never a sleep.""",
    """And concurrency: a stress run, then an invariant a race would break."""]):
    seg(sid, i, t)

E.chapter(5, 'Question 1 — LRU cache → TTL → thread-safe', 'Reported for the AI round · strongest evidence',
          """Question one. The L R U cache, which then grows a time to live, and then has to be thread-safe. This is the best """
          """attested question for the A I round: a first-hand A I-round report, two guides, and more LinkedIn reports of the """
          """same family.""")

sid = steps_list('The question, as it arrives in phases', [
    (0, '**Phase 1:** LRU cache, capacity N — Get and Put in O(1)', 'info'),
    (1, '**Phase 2:** each entry has a TTL — an expired key reads as missing, even if still stored', 'info'),
    (2, '**Phase 3:** "now make it thread-safe"', 'shared'),
    (3, '**Phase 4:** millions of requests per second — what changes?', 'deny'),
])
seg(sid, 0, """It arrives in phases. Phase one: an L R U cache with a fixed capacity, get and put in constant time.""")
seg(sid, 1, """Phase two, from the InterviewDB wording: each entry has a time to live, and get must report a miss for an """
            """expired key even if it is still in the cache.""")
seg(sid, 2, """Phase three: make it thread-safe.""")
seg(sid, 3, """And phase four: millions of requests a second. What changes?""")

think('Before any AI: which two data structures, and what is the one rule a Get must obey?', 20,
      """Before you open the assistant, say the design. Which two data structures, and what is the one rule get must obey?""",
      """A dictionary for lookup, and a doubly linked list for recency. And the rule people forget: a get is a use. Reading a """
      """key must move it to the front, or the cache evicts the thing you just read.""")

sid = statement('The prompt I would actually type',
                'C#. Generic LruCache<TKey,TValue>, capacity N. TryGet and Put in O(1) using Dictionary + LinkedList<T> '
                'node handles. A TryGet counts as a use. Throw on capacity ≤ 0. No thread-safety yet. '
                'Then give me tests: eviction after a read, update of an existing key, capacity 1.',
                'Narrow · states the invariant · says what not to do yet · asks for tests that would catch the classic bug',
                kind='ok', kicker='Prompt')
seg(sid, 0, """Here is the prompt I would type. It names the language and the types, the complexity, the data structures, and """
            """the invariant: a get counts as a use. It says what not to do yet, no thread safety, so the answer stays small """
            """enough to read. And it asks for three tests, chosen because they catch the classic L R U bugs.""")

LRU = CS.cs_type('aicoding/A01_Lru.cs', 'LruCache', comment=False)
LRU = fit(LRU)
code_slide('Phase 1 — LRU cache', LRU, [
    (rng(LRU, 'private readonly int _capacity', 'LinkedList<(TKey'),
     """Three fields. Capacity, a dictionary from key to the list node, and the list itself, where the first node is the """
     """most recently used. Storing the node handle in the dictionary is what makes every operation constant time."""),
    (rng(LRU, 'public bool TryGet', 'return true;'),
     """Try get. A miss returns false. A hit removes the node and adds it back at the front: the read is a use. Those two """
     """lines are the whole point of the data structure, and they are exactly what the assistant tends to leave out."""),
    (rng(LRU, 'public void Put', 'return;'),
     """Put on an existing key updates the value in place and also counts as a use."""),
    (rng(LRU, 'if (_map.Count == _capacity)', '_map[key] = _order.AddFirst'),
     """Otherwise, if we are full, the victim is the last node, the least recently used. Remove it from both structures, """
     """then add the new key at the front. The node carries its key precisely so this delete is possible."""),
])

R1 = CS.cs_type('aicoding/Review.cs', 'R1_LruCache', comment=False)
ship('"Here is an O(1) LRU cache using a dictionary and a doubly linked list."', R1,
     'It compiles and passes put-then-get.',
     """Here is what an assistant plausibly returns for a quick L R U. Tidy, commented, constant time, and it passes the """
     """obvious put then get test.""",
     'Put 1, put 2, get 1, put 3. Which key is evicted — and which should be?',
     '**Get never moves the node to the front.** Reads do not count as use, so put 1, put 2, get 1, put 3 evicts key 1 — the key just read.',
     'Move the node to the front in Get, exactly as Put does.',
     'Tests.cs R1: "Get does not refresh recency, so the just-read key 1 is evicted" — fails before the fix, passes after.',
     ["""The defect: get never moves the node to the front, so reads do not count as a use. Put one, put two, get one, put """
      """three, and key one is evicted, the one you just read.""",
      """The fix is two lines, the same two lines put already has.""",
      """And the point: your hand-written test case, eviction after a read, catches it in seconds. That is why you write """
      """those cases before you prompt."""])

TTL = join(CS.cs_member('aicoding/A01_Lru.cs', 'LruTtlCache', 'public bool TryGet', comment=False),
           CS.cs_member('aicoding/A01_Lru.cs', 'LruTtlCache', 'private void EvictOne', comment=False))
TTL = fit(TTL)
code_slide('Phase 2 — TTL: lazy expiry, preferring expired victims', TTL, [
    (rng(TTL, 'public bool TryGet', 'return false;'),
     """Phase two. Each entry stores an absolute expiry time. On a read, if the entry is dead, I remove it right there and """
     """report a miss. Removing it, not just returning minus one, is the requirement the assistant tends to half-meet."""),
    (rng(TTL, '_order.Remove(node);', 'return true;'),
     """A live hit is a use, exactly as before."""),
    (rng(TTL, 'private void EvictOne', 'Remove(_order.Last);'),
     """When the cache is full, I look at only the last four entries for an expired one, and evict that if found, otherwise """
     """the least recently used. Looking at four, not scanning everything, keeps put constant time."""),
])

sid = cards('Two TTL decisions to say out loud', [
    (0, 'Inject the clock', 'An `IClock` instead of `DateTime.Now`. Tests set the time; no `Thread.Sleep`, no flaky tests.', 'ok'),
    (1, 'Bound the cleanup', 'Lazy expiry on read + a sweep with a budget from the cold end. Never a full scan under the lock.', 'shared'),
], cols=2, kicker='Design')
seg(sid, 0, """Two decisions to say out loud. Inject the clock. Without it, every time to live test needs a sleep and becomes """
            """slow and flaky. It is the first thing I would tell the assistant when asking for expiry code.""")
seg(sid, 1, """And bound the cleanup. Expired keys that are never read again would stay forever, so a sweep reclaims them, but """
            """with a budget, walking from the cold end. A sweep that scans the whole cache under the lock just moves the cost """
            """into a latency spike.""")

R3 = CS.cs_type('aicoding/Review.cs', 'R3_ConcurrentLru', comment=False)
R3 = '\n'.join(l for l in R3.split('\n') if 'ListCount' not in l and 'MapCount' not in l)
ship('"To make it thread-safe I switched to ConcurrentDictionary, which is lock-free."', R3,
     'You asked for thread safety.',
     """Phase three: make it thread-safe. This is the answer an assistant gives most often, and it sounds right.""",
     'Is this thread-safe? What exactly does ConcurrentDictionary protect here?',
     '`ConcurrentDictionary` makes each **map** call atomic. The `LinkedList` is unprotected, and **Get mutates it**. Interleaved Remove/AddFirst corrupt the list; Put\'s check-then-evict races.',
     'One lock around each whole operation. The invariant spans two structures, so the lock boundary must too.',
     'Stress test: corrupted or threw in **20 of 20** trials.',
     ["""It is not thread-safe. The concurrent dictionary makes each dictionary call atomic, but the linked list is not """
      """protected, and get writes to it. Two gets interleaving remove and add-first corrupt the list.""",
      """The fix is one lock around each whole operation. The invariant spans two structures, so the lock has to cover """
      """both.""",
      """And the evidence: under a stress test, this version corrupted or threw in twenty out of twenty runs. That is the """
      """sentence that wins this phase: per-operation atomicity is not multi-structure atomicity."""])

SYNC = CS.cs_type('aicoding/A01_Lru.cs', 'SyncLruTtlCache', comment=False)
SYNC = fit(SYNC)
code_slide('Phase 3 — one lock, around the whole operation', SYNC, [
    (rng(SYNC, 'private readonly LruTtlCache', 'private readonly object _gate'),
     """The thread-safe version wraps the single-threaded one. One private lock object."""),
    (rng(SYNC, 'public bool TryGet', 'public int Count'),
     """Every public operation takes the lock for its whole duration. Simple, obviously correct, and the cost is that all """
     """callers serialise. Say that cost out loud, because it sets up phase four."""),
])

sid = compare('Phase 4 — millions of requests per second',
    ('One lock', 'shared', 0, ['Exact LRU', 'Every call contends on one lock', 'Fine to tens of thousands of ops/s']),
    ('N shards by key hash', 'ok', 1, ['Each shard is exact LRU; the whole cache is **approximately** LRU',
                                       'Contention divided by N', 'A hot shard may evict an entry younger than the oldest in a cold shard']))
seg(sid, 0, """Phase four, millions of requests a second. One lock gives you exact L R U but every call contends on it.""")
seg(sid, 1, """So split into N shards by key hash, each with its own lock. Each shard is exact L R U, the whole cache is only """
            """approximately L R U, because a busy shard can evict an entry younger than the oldest one in a quiet shard. That """
            """is the trade, and saying it is the Staff-level answer. Beyond one machine, it becomes a distributed cache with """
            """consistent hashing, which is a design conversation, not code.""")

# ======================================================================== Q2 LFU
sid = steps_list('Phase 5 · "Now add a validation method for keys"', [
    (0, 'Reported on LeetCode Discuss: "Implement an LRU Cache. Later, add a validation method for keys."', 'info'),
    (1, 'Ambiguous. Ask: **reject bad keys on Put**? Or **IsValid(key)**: present and not expired?', 'deny'),
    (2, 'Pick one, say why, and add it **by composition** — the LRU itself does not change', 'ok'),
    (3, 'The same candidate: "the interviewer kept adding features… I ended up over-engineering"', 'shared'),
])
for i, t in enumerate([
    """A follow-up from a LeetCode Discuss report of this exact round: implement an L R U cache, and later, add a """
    """validation method for keys.""",
    """It is ambiguous, so ask. Does it mean rejecting bad keys when they are put? Or a method that says whether a key is """
    """present and still valid, not expired? Each reading is a different method.""",
    """Pick one, say why, and add it by composition, without changing the cache underneath.""",
    """And notice what the same candidate wrote afterwards: the interviewer kept adding features, and they ended up """
    """over-engineering through prompting. The next slide is about that."""]):
    seg(sid, i, t)

KV = fit(join(CS.cs_member('aicoding/A04_KeyValidation.cs', 'ValidatedLruCache', 'public void Put', comment=False),
              CS.cs_member('aicoding/A04_KeyValidation.cs', 'ValidatedLruCache', 'public bool TryGet', comment=False),
              CS.cs_type('aicoding/A04_KeyValidation.cs', 'KeyRules', comment=False)))
code_slide('Validation at the boundary, by composition', KV, [
    (rng(KV, 'public void Put', '_inner.Put(key, value);'),
     """The wrapper owns the plain L R U and a rule supplied by the caller. Put asks the rule for a reason. If there is one, """
     """reject with that reason; otherwise delegate. The tested cache underneath is untouched."""),
    (rng(KV, 'public bool TryGet', 'return _inner.TryGet(key, out value);'),
     """Reads do not throw. An invalid key can never have been stored, so a lookup is simply a miss."""),
    (rng(KV, 'public static class KeyRules', 'null;'),
     """A default rule for string keys: not null, not empty, a length limit, no control characters. Four rules, each with a """
     """reason you can say. Not ten."""),
], kicker='LRU · key validation')

sid = cards('When the interviewer keeps adding features', [
    (0, 'Each feature is a test of judgement, not of typing', 'Ask what problem it solves before you prompt for it', 'ok'),
    (1, 'Prefer extension to modification', 'Wrap or compose; keep the tested core stable', 'ok'),
    (2, 'Say when it is over-engineering', '"I would not add this until we see X" is a Staff answer', 'shared'),
    (3, 'Never let the assistant grow the design', 'If you could not explain the new class in one sentence, do not paste it', 'deny'),
], cols=2, kicker='Scope')
for i, t in enumerate([
    """When the interviewer keeps adding features, treat each one as a test of judgement, not typing. Ask what problem it """
    """solves before you prompt for it.""",
    """Prefer extension to modification: wrap or compose, and keep the tested core stable.""",
    """It is fine to say a feature is over-engineering. I would not add this until we see a real need, is a Staff-level """
    """answer when you can say what the need would be.""",
    """And never let the assistant grow the design for you. If you could not explain the new class in one sentence, do not """
    """paste it."""]):
    seg(sid, i, t)

E.chapter(6, 'Question 2 — LRU with counters: predict the hit ratio', 'Reported Sep 2026 (PracHub) and on LeetCode Discuss · reasoning, not just code',
          """Question two. An L R U cache with counters, and then: given different workloads, predict and calculate the hit and """
          """miss ratio. Reported in September twenty twenty-six, and again in a LeetCode Discuss report of this round, which """
          """described it as combining coding with reasoning about behaviour. The code is small. The point is to predict before """
          """you measure, because that is exactly the reasoning an assistant cannot do for you.""")

CNT = fit(CS.cs_member('aicoding/A02_CountingLru.cs', 'CountingLruCache', 'public TValue GetOrLoad', comment=False))
code_slide('Counters on a read-through LRU', CNT, [
    (rng(CNT, 'public TValue GetOrLoad', 'if (_lru.TryGet(key, out var v))'),
     """Read-through: on a hit, count a hit and return. That is how hit ratio is normally measured, because a miss is a trip """
     """to the slow thing behind the cache."""),
    (rng(CNT, '_misses++;', 'return v;'),
     """On a miss, count it, load, and count an eviction if the cache was full. Reuse the L R U from question one; do not """
     """write a new one. And if this becomes thread-safe, the counters ride inside the same lock, or use Interlocked if a """
     """metrics scraper reads them without it."""),
], kicker='LRU · counters')

think('Capacity 4. Keys 0,1,2,3,4,0,1,2,3,4,… repeated 1,000 times. Predict the hit ratio.', 20,
      """Pause, and predict before anything runs. Capacity four. The keys zero to four, cycled a thousand times. What is the """
      """hit ratio?""",
      """Zero. Every single request misses. Each key is evicted just before it is needed again, because the cache always """
      """holds the four most recent keys and the next one is always the fifth. This is the classic L R U pathology: a scan """
      """even one key larger than the cache gets nothing.""")

sid = table('Predict, then measure (capacity 100 unless stated)', ['Workload', 'Prediction', 'Measured'], [
    (0, ['Cyclic: 5 keys, capacity 4', '0% — every key evicted just before reuse', '**0.0%**']),
    (1, ['Cyclic: 5 keys, capacity 5', 'Only the 5 cold misses', '**5 misses, 0 evictions**']),
    (2, ['Uniform over 1,000 keys', '≈ capacity / distinct = 10%', '**9.8%**']),
    (3, ['Skewed (Zipf) over 1,000 keys', 'Far above 10% — hot keys stay resident', '**57.8%**']),
], kicker='LRU · counters')
for i, t in enumerate([
    """The cyclic scan: predicted zero, measured zero.""",
    """Give it one more slot and only the five cold misses remain, with no evictions at all. One slot is the difference """
    """between nothing and everything.""",
    """Uniform traffic over a thousand keys with a hundred slots: about capacity over distinct keys, ten percent. Measured """
    """nine point eight.""",
    """And skewed traffic, where a few keys take most requests: far better, fifty-seven point eight percent at the same """
    """capacity. Real traffic is usually skewed, which is why small caches work at all."""]):
    seg(sid, i, t)

sid = cards('Follow-ups', [
    (0, 'Fix the scan pathology', 'Scan-resistant policies: LRU-K, 2Q, ARC, or an admission filter (TinyLFU)', 'ok'),
    (1, 'Thread-safe counters', 'Inside the cache lock, or Interlocked if read lock-free', 'shared'),
    (2, 'What capacity do we need?', 'Measure the hit-ratio curve on real traffic; buy capacity until it flattens', 'dp'),
    (3, 'Report it', 'Hit ratio per key class, not one global number — a hot class can hide a cold one', 'info'),
], cols=2, kicker='Follow-ups')
for i, t in enumerate([
    """Fixing the scan: a scan-resistant policy, L R U-K, two-Q, A R C, or an admission filter that refuses one-off keys.""",
    """Thread-safe counters: inside the cache's lock, or Interlocked if they are read without it.""",
    """How much capacity: measure the hit-ratio curve on real traffic and stop buying memory where it flattens.""",
    """And reporting: a hit ratio per kind of key, not one global number, because a hot class can hide a cold one."""]):
    seg(sid, i, t)

E.chapter(7, 'Question 3 — LFU cache with GetRank()', 'Reported once, at Staff level (Feb 2026)',
          """Question three. An L F U cache, least frequently used, with an L R U tie-break, and a get-rank query. Reported once, """
          """specifically as the Staff-level variant of the cache question.""")

sid = steps_list('The question', [
    (0, 'Evict the **least frequently** used key; ties broken by **least recently** used', 'info'),
    (1, 'Get and Put in **O(1)**', 'info'),
    (2, '**GetRank(key)**: the key\'s position in keep order — rank 1 is evicted last', 'shared'),
    (3, 'Clarify first: does GetRank count as a use? (It must not — reading a rank must not change it)', 'deny'),
])
seg(sid, 0, """Evict the least frequently used key, and among equals, the least recently used.""")
seg(sid, 1, """Get and put in constant time.""")
seg(sid, 2, """And get rank: where a key stands. The statement does not define rank, so define it before coding: rank one is """
            """the key the cache would evict last.""")
seg(sid, 3, """And clarify one thing: does get rank count as a use? It must not. Reading a rank must not change it.""")

think('How do you get O(1) LFU — and what will the assistant claim about GetRank?', 20,
      """Pause. How do you make L F U constant time? And what do you think the assistant will claim about get rank?""",
      """One linked list per frequency, plus a running minimum frequency. A touch moves a node from list f to list f plus one. """
      """And the assistant will happily claim get rank is constant time too. It is not, and catching that claim is the """
      """Staff-level moment in this question.""")

LFU = join(CS.cs_member('aicoding/A03_LfuRank.cs', 'LfuRankCache', 'public void Put', comment=False),
           CS.cs_member('aicoding/A03_LfuRank.cs', 'LfuRankCache', 'private void Touch', comment=False))
LFU = fit(LFU)
code_slide('LFU — buckets per frequency, and a minimum frequency', LFU, [
    (rng(LFU, 'public void Put', 'return;'),
     """Put on an existing key updates the value and touches it, raising its frequency."""),
    (rng(LFU, 'if (_byKey.Count == _capacity)', '_byKey.Remove(victim.Value.Key);'),
     """When full, the victim is the last node in the bucket for the minimum frequency: least frequent, and least recent """
     """among those."""),
    (rng(LFU, 'var fresh =', '_minFreq = 1;'),
     """A new key starts at frequency one, so the minimum frequency becomes one. Always."""),
    (rng(LFU, 'private void Touch', 'Attach(node);'),
     """Touch detaches the node from bucket f, raises the minimum only if that bucket just became empty and it was the """
     """minimum, and attaches it to bucket f plus one. All constant time."""),
])

RANK = CS.cs_member('aicoding/A03_LfuRank.cs', 'LfuRankCache', 'public int GetRank', comment=False)
RANK = fit(RANK)
code_slide('GetRank — honest complexity', RANK, [
    (rng(RANK, 'public int GetRank', 'int f = node.Value.Freq'),
     """Get rank does not touch the key. That was the clarification."""),
    (rng(RANK, 'foreach (var (freq, count)', 'if (freq > f) rank += count;'),
     """Everyone with a higher frequency ranks ahead of it, and a sorted map from frequency to count lets me sum them."""),
    (rng(RANK, 'for (var n = _buckets[f].First', 'return rank;'),
     """Then count the more recent keys in its own bucket. That is order of the number of distinct frequencies plus the """
     """bucket size. Not constant. When the assistant says get rank is order one, this is where you push back: either say """
     """the real cost, or offer an order-statistics tree for log n."""),
])

sid = cards('What the interviewer listens for', [
    (0, 'You defined rank', 'Before code: rank 1 = evicted last; GetRank is not a use', 'ok'),
    (1, 'You rejected a false O(1)', 'The assistant claimed it; you stated O(F + B) and offered O(log n)', 'deny'),
    (2, 'Thread-safety', 'Same answer as LRU: one lock per operation — buckets, map and min-freq form one invariant', 'shared'),
], cols=1, kicker='Signal')
seg(sid, 0, """What the interviewer listens for. You defined rank before writing code.""")
seg(sid, 1, """You rejected a false complexity claim from the assistant, with the real number.""")
seg(sid, 2, """And for thread safety, the same answer as L R U: the map, the buckets and the minimum frequency are one """
            """invariant, so one lock covers the whole operation.""")

# ======================================================================== Q3 Logger
E.chapter(8, 'Question 4 — the logging library', '5 reports, Aug–Sep 2026, one Staff · the freshest evidence',
          """Question four, and the freshest evidence in all the research: a logging library with severity filtering, """
          """throttling and aggregation. Five candidate reports in August and September twenty twenty-six, one of them at """
          """Staff level. The four phases you are about to see are the reported ones.""")

sid = steps_list('The four reported phases', [
    (0, '**1.** Logger with a minimum severity (DEBUG, INFO, WARN, ERROR): print only at or above it', 'info'),
    (1, '**2.** Unit tests', 'info'),
    (2, '**3.** Throttle: an identical log (same severity, function, line, message) within a window prints once', 'shared'),
    (3, '**4.** Aggregate: when the window expires and the next identical log arrives, print a summary of what was suppressed, stamped with the first occurrence', 'ok'),
])
seg(sid, 0, """Phase one: a logger initialised with a minimum severity, printing only messages at or above it.""")
seg(sid, 1, """Phase two: unit tests. This is where the assistant genuinely saves you time.""")
seg(sid, 2, """Phase three: throttling. An identical log, meaning same severity, function name, line number and message, """
            """repeated within a time window, prints only once.""")
seg(sid, 3, """Phase four: aggregation. When the window expires and the next identical log arrives, print a summary of how """
            """many were suppressed, using the timestamp of the first occurrence in that window.""")

think('What is the key of the throttle table, and what must NOT happen while you hold its lock?', 20,
      """Pause. What is the key of your throttle table? And what must never happen while you hold its lock?""",
      """The key is the four fields that define identical: severity, function, line and message. And while holding the """
      """lock, you must never do the I O. Decide under the lock, write outside it.""")

LOG = CS.cs_member('aicoding/L01_Logger.cs', 'Logger', 'public void Log', comment=False)
LOG = fit(LOG)
code_slide('Phases 1, 3 and 4 — decide under the lock, write outside it', LOG, [
    (rng(LOG, 'public void Log', 'if (sev < _min) return;'),
     """Phase one is the first line: below the minimum severity, return. No lock, the cheapest possible check, first."""),
    (rng(LOG, 'long now = _clock.NowMs;', 'string summary = null;'),
     """The clock is injected again, so window tests need no sleeps. The key is a record of the four fields."""),
    (rng(LOG, 'lock (_gate)', 'w.Start = now; w.FirstTs = now; w.Suppressed = 0;'),
     """Under the lock: if a window exists and has not expired, count a suppression and return. If it has expired and """
     """something was suppressed, build the summary line, stamped with the first timestamp of that window. Then start a """
     """new window."""),
    (rng(LOG, '} else if (_windowMs > 0)', '_windows[key] = new Window'),
     """First time we see this key: open a window."""),
    (rng(LOG, 'if (summary != null) Emit(summary);', 'Emit($"{now}'),
     """And outside the lock, emit the summary if there is one, then the line itself. A slow sink must never serialise every """
     """caller."""),
])

R11 = CS.cs_type('aicoding/Review.cs', 'R11_Logger', comment=False)
ship('"A thread-safe logger: one lock so lines never interleave."', R11,
     'You asked for a thread-safe logger.',
     """You ask the assistant to make the logger thread-safe. One lock, so lines never interleave. Sounds reasonable.""",
     'This is correct. Why would you still not ship it?',
     'The lock is held **across the sink write** — slow I/O. Every logging thread queues behind the disk.',
     'Hold the lock only for shared decision state; do the I/O outside it. In production: a background writer behind a bounded channel.',
     'Tests.cs R11: 8 threads × 25 logs with a 2 ms sink took **~460 ms** — fully serialised.',
     ["""It is correct, and that is the trap. The lock is held across the sink write, which is slow I O, so every thread """
      """that logs waits for the disk.""",
      """The fix: hold the lock only for the decision, write outside it. In production, a background writer behind a bounded """
      """queue.""",
      """Measured: eight threads logging twenty-five lines each to a two millisecond sink took about four hundred and sixty """
      """milliseconds. Logging just became the bottleneck of every request."""])

R14 = CS.cs_type('aicoding/Review.cs', 'R14_AsyncLogger', comment=False)
ship('"Non-blocking logger: a bounded channel that drops when full, with a drop counter."', R14,
     'Production follow-up: never block callers; report what was dropped.',
     """The production follow-up: logging must never block the caller, and you must know how much you dropped. The """
     """assistant offers a bounded channel that drops when full, with a counter. This one caught me too.""",
     'Under load the dashboard says 0 dropped. Is that true?',
     'With `FullMode = DropWrite`, **`TryWrite` returns true even when it drops the item.** The drop counter never moves.',
     '`FullMode = Wait` with a non-blocking `TryWrite`, which returns false when full — or use the itemDropped callback.',
     'Measured: **accepted 10,000, dropped 0, written about 1,050.** My own first AsyncLogger had this bug; the 10,000-thread test caught it.',
     ["""Under drop-write mode, try-write returns true even when it drops the item. So the counter never moves.""",
      """The fix is to use wait mode with a non-blocking try-write, which does return false when full.""",
      """Measured: accepted ten thousand, dropped zero, written about one thousand and fifty. The dashboard said nothing was """
      """lost while nine in ten logs were. And honestly, my own first version had exactly this bug. A test with ten """
      """thousand concurrent writers caught it, which is the whole argument for verifying A I output with a test rather """
      """than by reading the documentation in your head."""])

sid = cards('Production follow-ups, and the one-line answers', [
    (0, '10,000 threads logging', 'Callers enqueue to a bounded channel and return; one background writer drains to sinks', 'ok'),
    (1, 'Memory of the throttle table', 'Purge windows that expired with nothing suppressed; messages with request ids would grow it forever', 'shared'),
    (2, 'A sink fails', 'Catch per sink, count it, carry on — a broken disk must not take down the request path', 'deny'),
    (3, 'Shutdown', 'Stop accepting, drain what was accepted, bounded wait', 'dp'),
], cols=2, kicker='Follow-ups')
for i, t in enumerate([
    """Ten thousand threads logging: callers enqueue into a bounded channel and return immediately, one background task """
    """writes to the sinks.""",
    """Memory of the throttle table: purge windows that expired with nothing suppressed. Messages that contain request """
    """ids are all distinct, and would grow it forever.""",
    """A sink fails: catch per sink, count the failure, carry on.""",
    """Shutdown: stop accepting, drain what was accepted, with a bound on how long you wait."""]):
    seg(sid, i, t)

# ======================================================================== Q4 Scheduler
E.chapter(9, 'Question 5 — the delay scheduler', 'LinkedIn coding question (InterviewDB) · round not stated',
          """Question five. A delay scheduler, the C sharp version of a scheduled executor: run this action after this delay. """
          """It is a LinkedIn coding question from InterviewDB; which round it appeared in is not stated, but it is the purest """
          """concurrency question in this set, and concurrency is where every A I-round question ends.""")

sid = steps_list('The question', [
    (0, '`Schedule(Action work, TimeSpan delay)` — run `work` once, no earlier than `delay` from now', 'info'),
    (1, 'Many tasks, any order of deadlines; equal deadlines run in submission order', 'info'),
    (2, 'Follow-ups: **cancel** a task · **shutdown** with tasks pending · a task that **throws**', 'shared'),
])
seg(sid, 0, """Schedule an action to run once, no earlier than a delay from now.""")
seg(sid, 1, """Many tasks, deadlines in any order, and equal deadlines run in the order they were scheduled.""")
seg(sid, 2, """The follow-ups: cancel a task, shut down with tasks pending, and a task that throws.""")

think('One worker thread is sleeping until 10:00. A new task is scheduled for 09:59. What must happen?', 20,
      """Pause. The worker thread is sleeping until ten o'clock. Someone schedules a task for nine fifty-nine. What must """
      """happen?""",
      """The worker must be woken so it re-reads the head of the queue. That one detail is the bug in most first drafts, """
      """human or A I.""")

SCHED = join(CS.cs_member('Q07_Scheduler.cs', 'DelayScheduler', 'public Handle Schedule', comment=False),
             CS.cs_member('Q07_Scheduler.cs', 'DelayScheduler', 'private void Loop', comment=False))
SCHED = fit(SCHED)
SCHED = strip_comments(SCHED)
code_slide('A priority queue, one worker, Monitor.Wait with a timeout', SCHED, [
    (rng(SCHED, 'public Handle Schedule', 'DueAt = _clock()'),
     """Schedule computes an absolute deadline from an injectable clock."""),
    (rng(SCHED, 'lock (_gate)', 'Monitor.Pulse(_gate);'),
     """Under the lock: refuse after shutdown, give it a sequence number as a tie-break, enqueue by deadline and sequence, """
     """and pulse. The pulse is the answer to the pause: the worker may be sleeping until a later deadline."""),
    (rng(SCHED, 'private void Loop', 'if (_shutdown && (!_drain'),
     """The worker loop. Exit on shutdown, either immediately or once drained."""),
    (rng(SCHED, 'if (_queue.Count == 0)', 'continue;'),
     """Nothing queued: wait to be poked."""),
    (rng(SCHED, 'ScheduledTask head = _queue.Peek();', 'Monitor.Wait(_gate, (int)Math.Min'),
     """Cancelled tasks are dropped lazily when they reach the head. If the head is due, take it. Otherwise wait until it is """
     """due, and loop. The loop re-checks everything on every wake, so a spurious wake, an early pulse and a real timeout """
     """all behave the same."""),
    (rng(SCHED, 'if (!ready.Cancelled)', 'catch'),
     """And the task runs outside the lock, inside a try-catch. Holding the lock here would block every schedule call for """
     """the length of the task, and a task that schedules another task would deadlock. One bad task must not kill the """
     """worker."""),
])

R9 = CS.cs_type('aicoding/Review.cs', 'R9_BlockingQueue', comment=False)
ship('The same Monitor pattern from an assistant: "A blocking queue with Monitor.Wait/Pulse."', R9,
     'The wait/pulse pattern the scheduler depends on.',
     """The scheduler stands on wait and pulse, so here is the same pattern the way an assistant often writes it, for a """
     """bounded blocking queue.""",
     'Two consumers, one producer. What goes wrong?',
     'Two defects. **`if` instead of `while`** around Wait — a woken thread does not re-check. **`Pulse` on one shared monitor** — a producer can wake another producer while the consumer sleeps forever.',
     '`while` around every Wait; `PulseAll` (or separate conditions).',
     'Stress test: **hung or threw in 10 of 10** trials.',
     ["""Two defects. An if instead of a while around the wait, so a woken thread does not re-check the condition. And a """
      """single pulse on one shared monitor, so a producer can wake another producer while the consumer that needed waking """
      """sleeps forever.""",
      """The fix: a while loop around every wait, and pulse-all.""",
      """Under a stress test it hung or threw ten times out of ten. Notice our scheduler already has the while loop. That is """
      """not luck; it is the rule to check first in any wait-pulse code an assistant gives you."""])

sid = cards('Follow-ups', [
    (0, 'Cancel', 'Mark the task cancelled; drop it lazily when it reaches the head. A running task cannot be stopped — say so', 'ok'),
    (1, 'Shutdown', 'Drain: run what is queued, accept nothing new. ShutdownNow: discard the queue. Both wake the worker', 'shared'),
    (2, 'More throughput', 'A pool of workers taking ready tasks; the timing thread only moves tasks from waiting to ready', 'dp'),
    (3, 'Clock jumps', 'Use a monotonic clock (TickCount64), never wall-clock time, for deadlines', 'deny'),
], cols=2, kicker='Follow-ups')
for i, t in enumerate([
    """Cancel: mark it cancelled and drop it lazily when it reaches the head. A task that is already running cannot be """
    """stopped, and you should say so.""",
    """Shutdown: drain, meaning run what is queued and accept nothing new, or shutdown now, which discards the queue. Both """
    """must wake the worker.""",
    """More throughput: a pool of workers runs ready tasks; the timing thread only moves tasks from waiting to ready.""",
    """And clock jumps: deadlines use a monotonic clock, never the wall clock, or a time change fires everything at once."""]):
    seg(sid, i, t)

# ======================================================================== Q5 Window
E.chapter(10, 'Question 6 — sliding-window counter', 'Pattern practice · not a reported AI-round question',
          """Question six. A sliding window counter: how many events in the last five minutes. To be honest about the """
          """evidence: this is not a reported A I-round question. It is here because counters and metrics are the natural """
          """production follow-up to the cache and logger questions, and it is the smallest problem that forces a time """
          """bucketing decision and a locking decision at once.""")

sid = steps_list('The question', [
    (0, '`Record(now)` an event; `Count(now)` = events in the last 300 seconds', 'info'),
    (1, '10,000 events per second, read by a dashboard', 'info'),
    (2, 'Clarify: exact timestamps, or one-second precision? (It changes memory by 3,000,000×)', 'shared'),
])
seg(sid, 0, """Record an event, and count events in the last three hundred seconds.""")
seg(sid, 1, """At ten thousand events a second, read by a dashboard.""")
seg(sid, 2, """And the clarifying question that matters: do you need exact timestamps, or is one-second precision fine? An """
            """exact queue holds three million entries for five minutes of traffic. Per-second buckets hold three hundred.""")

WIN = strip_comments(CS.cs_type('aicoding/C02_WindowCounter.cs', 'WindowCounter', comment=False))
WIN = fit(WIN)
code_slide('A ring of per-second buckets', WIN, [
    (rng(WIN, 'private readonly int _windowSecs', 'private readonly object _gate'),
     """One slot per second, with the second each slot currently holds. Memory is the window size, not the event count."""),
    (rng(WIN, 'public void Record', '_count[slot] += n;'),
     """Record: the slot is now modulo the window. If the slot holds an old second, reset it first. Then add."""),
    (rng(WIN, 'public long Count', 'return total;'),
     """Count sums the slots whose second is inside the window. Look carefully at the comparison: strictly greater than now """
     """minus the window. Remember that."""),
])

R13 = CS.cs_type('aicoding/Review.cs', 'R13_Window', comment=False)
ship('"Counts events in the last `window` seconds using per-second buckets."', R13,
     'You asked for a five-minute counter.',
     """The assistant's version. Nearly identical, and it passes every test anyone writes in a hurry.""",
     'An event at t = 0. At t = 300, is it inside a 300-second window?',
     '`_stamp[i] >= now - _w` includes the second exactly `window` ago — a **301-second** window. An event at t=0 is still counted at t=300.',
     '`> now - _w`. And test exactly at the boundary, not one past it.',
     'Tests.cs R13: "event from exactly 300 s ago still counted".',
     ["""Greater-or-equal includes the second exactly three hundred seconds ago, so it is a three hundred and one second """
      """window. An event at zero is still counted at three hundred.""",
      """The fix is one character. The real lesson is the test: test exactly at the boundary, not one past it.""",
      """Off-by-one errors at a boundary are the defect an assistant reproduces most confidently, because both versions """
      """look equally plausible."""])

sid = cards('Follow-ups', [
    (0, 'Thread-safety', 'One lock around record and count — or striped counters if writes dominate', 'shared'),
    (1, 'O(1) reads', 'Keep a running total; subtract a slot as it is recycled. Writes do the bookkeeping', 'ok'),
    (2, 'Many keys', 'A ring per key in a dictionary; evict idle keys', 'dp'),
    (3, 'Across machines', 'Each host keeps its ring; aggregate per second centrally — counts are mergeable', 'info'),
], cols=2, kicker='Follow-ups')
for i, t in enumerate([
    """Thread safety: one lock, or striped counters if writes dominate.""",
    """Constant-time reads: keep a running total and subtract each slot as it is recycled, so writes do the bookkeeping. """
    """State which side you optimised.""",
    """Many keys: a ring per key, and evict idle keys.""",
    """Across machines: each host keeps its own ring and the per-second counts are merged centrally, because counts add up """
    """cleanly."""]):
    seg(sid, i, t)

# ======================================================================== close
# ======================================================================== Q6 Intervals
E.chapter(11, 'Question 7 — the interval manager', 'Reported for the AI round (Feb–Jun 2026) · "next interval" named in 2026',
          """Question seven. An interval manager. Reported for this round by two sources: not "merge this list", but a class with """
          """add-interval and insert-interval style methods where you choose the bookkeeping. And a twenty twenty-six list of """
          """LinkedIn A I-round questions names a variant: interval addition and next interval lookup. No statement for that """
          """variant could be found, so I will define next interval myself and say so, which is exactly what you would do in """
          """the room.""")

sid = steps_list('The question, and the clarifications that change the code', [
    (0, '**Part 1** `Add(start, end)` — merge with anything it overlaps or touches', 'info'),
    (1, '**Part 2** `Next(point)` — containing interval, else the first after it **(my definition)** · **Part 3** covered length / remove', 'shared'),
    (2, 'Clarify: **half-open [start, end)** or closed? Does [1,3) + [3,5) merge?', 'deny'),
    (3, 'Clarify: how many intervals, how many queries per add? (Decides list vs sorted structure)', 'deny'),
])
seg(sid, 0, """A LeetCode Discuss report describes this as a modified merge intervals question with three incremental """
            """parts, where the interviewer watched how prompts were given and whether A I output was verified, and where """
            """optimal solutions carried more weight. Part one: add an interval, merging it with anything it overlaps or """
            """touches.""")
seg(sid, 1, """Part two, in the variant named next interval lookup: the interval that contains a point, or else the first """
            """one that starts after it. That definition is mine, stated as an assumption, because no source gives the statement. """
            """Part three is usually total covered length, or removal, both in the follow-ups below.""")
seg(sid, 2, """Clarify the convention. I use half-open intervals, start inclusive, end exclusive, so one to three and three to five """
            """touch and merge, and length is simply end minus start. Closed versus half-open is the most common silent """
            """disagreement with an assistant here.""")
seg(sid, 3, """And clarify the volume. A handful of intervals: a list is fine. Many intervals and many queries: you need a sorted """
            """structure with log n lookups, and that decision is the question.""")

IV = fit(join(CS.cs_member('aicoding/E01_IntervalSet.cs', 'IntervalSet', 'public void Add', comment=False),
              CS.cs_member('aicoding/E01_IntervalSet.cs', 'IntervalSet', 'public (int Start, int End)? Next', comment=False)))
code_slide('A SortedSet of disjoint intervals', IV, [
    (rng(IV, 'public void Add', 'int s = start, e = end;'),
     """The intervals are kept disjoint in a sorted set ordered by start. Adding validates the input first."""),
    (rng(IV, 'if (Floor(start) is { } f', 'Drop(f);'),
     """The one interval that starts before ours may reach into it. Find it with a floor lookup, log n, and absorb it if it """
     """does."""),
    (rng(IV, 'foreach (var iv in _set.GetViewBetween', 'CoveredLength += e - s;'),
     """Then every interval that starts inside our range overlaps or touches, so absorb those too, and insert the merged """
     """one. Each interval is absorbed at most once, so add is amortised log n. Covered length is maintained as we go, so """
     """reading it is constant time."""),
    (rng(IV, 'public (int Start, int End)? Next', 'return _set.GetViewBetween((point + 1, 0), _set.Max).Min;'),
     """Next: if a floor lookup finds an interval containing the point, that is the answer. Otherwise, the ceiling: the """
     """smallest start after the point. Log n, and eight boundary tests, including exactly at an end, which half-open makes """
     """belong to the next interval."""),
], kicker='Intervals')

R4 = CS.cs_type('aicoding/Review.cs', 'R4_Merge', comment=False)
ship('"Merge intervals — sort by start, then merge overlapping neighbours. O(n log n)."', R4,
     'You asked for the classic merge as a starting point.',
     """If you ask the assistant for the classic merge as a starting point, this is a plausible answer. Short, sorted, """
     """familiar.""",
     'Merge [1,10] and [2,3]. What comes out?',
     '`result[^1] = (start, cur.End)` should take `Math.Max(result[^1].End, cur.End)`. **[1,10] + [2,3] becomes [1,3]** — a contained interval shrinks the cover.',
     'Take the max of the two ends. And keep a test where one interval contains another.',
     'Tests.cs R4: "[1,10]+[2,3] collapses to [1,3]".',
     ["""When an interval is contained in the previous one, it overwrites the end with the smaller value. One to ten plus two """
      """to three becomes one to three. The cover shrinks.""",
      """The fix is a max of the two ends.""",
      """And the habit: one of your three hand-written cases should be containment. It is the case assistants miss most in """
      """interval code."""])

sid = cards('Follow-ups', [
    (0, 'Remove an interval', 'Can split one interval into two — handle both sides', 'ok'),
    (1, 'Total covered length', 'Maintain it on every add and remove → O(1) read', 'shared'),
    (2, 'Reads dominate, many threads', 'Queries do not mutate → `ReaderWriterLockSlim` fits here (unlike LRU)', 'dp'),
    (3, 'Millions of intervals', 'Same tree; or bucket by range and shard', 'info'),
], cols=2, kicker='Follow-ups')
for i, t in enumerate([
    """Remove: removing a range can split one interval into two, so handle the left and right remainders.""",
    """Covered length: maintain it on every change, and reading it is constant time.""",
    """Many threads, mostly queries: here a reader-writer lock genuinely fits, because a query does not mutate anything. """
    """That contrast with the L R U is a good thing to say out loud.""",
    """And millions of intervals: the same tree, or bucket by range and shard."""]):
    seg(sid, i, t)

# ======================================================================== Q7 Structured data
E.chapter(12, 'Question 8 — structured data processing', 'Reported for the AI round (Hello Interview, Coditioning) · 2026',
          """Question eight. Structured data processing: you are given JSON-like records and asked to build the classes, """
          """transform them, and write tests, from scratch. Reported by two independent sources. This is where the assistant """
          """saves the most time, on boilerplate, and where trusting it blindly costs the most, through silent data loss.""")

sid = steps_list('The question', [
    (0, 'Input: one JSON object per line — `{"user":"u1","action":"view","ts":…,"ms":120}`', 'info'),
    (1, 'Output: per action — count, mean and max latency, distinct users — sorted', 'info'),
    (2, 'Some rows are malformed: missing fields, wrong types, not JSON at all', 'deny'),
    (3, 'Clarify: drop bad rows, or **count and report** them? (Always report them)', 'shared'),
])
seg(sid, 0, """One JSON object per line: a user, an action, a timestamp and a latency.""")
seg(sid, 1, """The output: per action, the count, the mean and max latency, and the number of distinct users, sorted.""")
seg(sid, 2, """And some rows are malformed: missing fields, wrong types, or not JSON at all.""")
seg(sid, 3, """The clarification that matters: do we drop bad rows silently, or count and report them? Always count and report. A """
            """bad row is data, not an exception, and one malformed record must not abort a batch of a million.""")

PARSE = fit(CS.cs_member('aicoding/C01_Records.cs', 'EventParser', 'public static ParseResult Parse', comment=False))
code_slide('Parse: a result with a reason, never an exception', PARSE, [
    (rng(PARSE, 'public static ParseResult Parse', 'catch (JsonException e)'),
     """Parsing returns a result, not an exception. Invalid JSON becomes a rejection with a reason."""),
    (rng(PARSE, 'var root = doc.RootElement;', 'if (!Long(root, "ms"'),
     """Then the shape: it must be an object, and each field must be present with the right type. Each failure has its own """
     """reason code."""),
    ('%d-%d' % (ln(PARSE, 'if (ms < 0'), len(PARSE.split('\n'))),
     """Range checks, then the typed event. Notice what the assistant is good for here: writing these field checks and the """
     """tests for every rejection reason. Notice what you own: the decision that a bad row is reported, not swallowed."""),
], kicker='Structured data')

AGG = fit(CS.cs_member('aicoding/C01_Records.cs', 'Aggregator', 'public Aggregator Consume', comment=False))
code_slide('Aggregate while streaming', AGG, [
    (rng(AGG, 'public Aggregator Consume', 'continue; }'),
     """Consume takes an enumerable of lines, so a fifty gigabyte file streams through and only the aggregates are held in """
     """memory. Rejections are counted by reason."""),
    (rng(AGG, 'var e = r.Event;', 'Accepted++;'),
     """Accepted events update a small accumulator per action. The one part that grows with the data is the distinct user """
     """set; at scale that becomes a HyperLogLog sketch, and saying so answers the memory follow-up before it is asked."""),
], kicker='Structured data')

R7 = CS.cs_type('aicoding/Review.cs', 'R7_Parse', comment=False)
ship('"Parses each line and skips anything malformed, so bad input never crashes the job."', R7,
     'You asked for a tolerant parser.',
     """You ask for a tolerant parser. The assistant promises that bad input never crashes the job.""",
     'Four lines, the second one malformed. How many are parsed?',
     'The try/catch wraps the **whole loop**. The first bad line ends parsing; every good line after it is dropped — silently, no count, no reason.',
     'Per-line result with a reason, counted. Never a blanket catch around a loop.',
     'Tests.cs R7: 4 lines with the 2nd bad → **1 parsed**.',
     ["""The try-catch wraps the whole loop. So the first bad line ends the parsing, and every good line after it is dropped, """
      """silently. Four lines with the second one bad: one line parsed.""",
      """The fix: a result per line, with a reason, counted.""",
      """It never crashes, exactly as promised. It just loses most of your data. Read what the catch actually covers."""])

sid = cards('Follow-ups', [
    (0, 'A 50 GB file', 'Stream lines; hold only aggregates', 'ok'),
    (1, 'Parallelise', 'Partition lines, aggregate per partition, merge — counts, sums and max all merge', 'shared'),
    (2, 'Distinct users at scale', 'HyperLogLog: ~1–2% error, kilobytes instead of gigabytes', 'dp'),
    (3, 'Schema changes', 'Unknown fields ignored, missing required fields rejected with a reason', 'info'),
], cols=2, kicker='Follow-ups')
for i, t in enumerate([
    """A fifty gigabyte file: stream it and hold only the aggregates.""",
    """Parallelise: partition the lines, aggregate each partition independently, and merge, because counts, sums and maxima """
    """all merge cleanly.""",
    """Distinct users at scale: a HyperLogLog sketch, a percent or two of error in kilobytes instead of gigabytes.""",
    """And schema changes: ignore unknown fields, reject missing required ones, with a reason."""]):
    seg(sid, i, t)

# ======================================================================== Q8 producer/consumer
E.chapter(13, 'Question 9 — the friendship graph, in three parts', 'Reported on LeetCode Discuss (Oct 2026) · boilerplate and tests provided',
          """Question nine, from a LeetCode Discuss report of this round. CoderPad, with boilerplate code and test cases """
          """already provided, and the A I tab. An adjacency list of friendships, in three parts: the shortest path between """
          """two users as the sequence of users, then the distance, then friend suggestions from mutual connections. The """
          """candidate said the interviewer was particularly interested in code reuse, how the solution was structured as """
          """requirements evolved, and whether generated code was checked rather than accepted.""")

sid = steps_list('Three parts, one design', [
    (0, '**Part 1:** shortest path A → B as the list of users', 'info'),
    (1, '**Part 2:** shortest distance — **reuse** part 1, do not write a second BFS', 'ok'),
    (2, '**Part 3:** suggest friends ranked by mutual connections', 'info'),
    (3, 'Clarify: is friendship symmetric? unknown users? ties in suggestions?', 'deny'),
])
for i, t in enumerate([
    """Part one: the shortest path from A to B, as the list of users. Unweighted edges, so breadth-first search.""",
    """Part two: the distance. The interviewer is watching for reuse: the distance is the path length minus one. Do not """
    """write a second search.""",
    """Part three: suggest friends, ranked by how many mutual connections they share.""",
    """And clarify: is friendship symmetric, even if the input lists an edge once? What do unknown users return? How are """
    """ties in suggestions ordered? That last one decides whether the provided tests are deterministic."""]):
    seg(sid, i, t)

FG = fit(join(CS.cs_member('aicoding/G02_FriendGraph.cs', 'FriendGraph', 'private Dictionary<int, int> ParentsUntil', comment=False),
              CS.cs_member('aicoding/G02_FriendGraph.cs', 'FriendGraph', 'public IReadOnlyList<int> ShortestPath', comment=False),
              CS.cs_member('aicoding/G02_FriendGraph.cs', 'FriendGraph', 'public int Distance', comment=False)))
code_slide('One BFS core, reused by path and distance', FG, [
    (rng(FG, 'private Dictionary<int, int> ParentsUntil', 'queue.Enqueue(from);'),
     """The shared core: a breadth-first search that records each user's parent and stops when it reaches the target."""),
    (rng(FG, 'while (queue.Count > 0)', 'return null;'),
     """A user is marked seen when it is enqueued, not when it is dequeued, so each user enters the queue once. That one """
     """detail is the bug the assistant tends to write, coming up next."""),
    (rng(FG, 'public IReadOnlyList<int> ShortestPath', 'return path;'),
     """Part one walks the parent map back from B to A and reverses it. Unknown or unreachable users return an empty list, """
     """and A to A is just A."""),
    (rng(FG, 'public int Distance', 'return path.Count == 0 ? -1 : path.Count - 1;'),
     """Part two is two lines on top of part one: the path length minus one, or minus one for no path. That is the reuse """
     """the interviewer is looking for."""),
], kicker='Graph')

SUG = fit(CS.cs_member('aicoding/G02_FriendGraph.cs', 'FriendGraph', 'public IReadOnlyList<(int User, int Mutual)> SuggestFriends', comment=False))
code_slide('Part 3 — suggestions by mutual friends', SUG, [
    (rng(SUG, 'public IReadOnlyList<(int User, int Mutual)> SuggestFriends', 'var mutual = new Dictionary<int, int>();'),
     """Suggestions: for each of my friends, look at their friends."""),
    (rng(SUG, 'foreach (var f in mine)', 'mutual[ff] = mutual.GetValueOrDefault(ff) + 1;'),
     """Skip me and anyone who is already my friend, and count how many of my friends each candidate is connected to."""),
    (rng(SUG, 'return mutual.OrderByDescending', '.Take(k)'),
     """Rank by mutual count, and break ties by id so the output is deterministic, and therefore testable. All of this, """
     """with the path and distance, is covered by fourteen tests including a ten-thousand-hop chain."""),
], kicker='Graph')

D3 = CS.cs_type('aicoding/Debug.cs', 'D3_Bfs', comment=False)
ship('"BFS for the shortest distance — correct on every test."', D3,
     'It returns the right distance.',
     """Here is breadth-first search the way an assistant often writes it. It returns the right answer on every test.""",
     'The distance is right. Why would you still not ship it?',
     'Cells are marked visited on **dequeue**, so a node is enqueued once **per neighbour** before it is processed.',
     'Mark visited when you **enqueue**.',
     'Debug.cs D3: **7,081 enqueues for 3,600 cells** on a 60×60 grid. In general each node can be queued up to once per neighbour, so on a social graph the waste grows with the average degree.',
     ["""It marks a node visited when it is dequeued, so a node can be enqueued once for every neighbour that reaches it """
      """before it is processed.""",
      """Mark it when you enqueue.""",
      """On a sixty by sixty grid that was seven thousand and eighty-one enqueues for three thousand six hundred cells. On a """
      """social graph a user can be queued once per friend who reaches them, so the waste grows with the number of friends. """
      """The answer is correct; the cost """
      """is not. Only reading the code catches it."""])

sid = cards('Follow-ups', [
    (0, 'Huge graph, one query', 'Bidirectional BFS: search from both ends, meet in the middle — ~2·√ of the frontier', 'ok'),
    (1, 'Graph does not fit in memory', 'Adjacency in a partitioned store; BFS by levels, batching lookups per level', 'shared'),
    (2, 'Suggestions at LinkedIn scale', 'Precompute offline; cap high-degree users; rank by more than mutual count', 'dp'),
    (3, 'Weighted connections', 'Dijkstra with a PriorityQueue', 'info'),
], cols=2, kicker='Follow-ups')
for i, t in enumerate([
    """A huge graph and a single query: bidirectional search from both ends, meeting in the middle, which explores far """
    """fewer users than one search from one end.""",
    """A graph that does not fit in memory: the adjacency lives in a partitioned store, and the search runs level by """
    """level, batching the lookups for each level.""",
    """Suggestions at LinkedIn's scale: precompute them offline, cap very high-degree users so one celebrity does not """
    """dominate, and rank on more than mutual count.""",
    """And weighted connections: Dijkstra with a priority queue."""]):
    seg(sid, i, t)

E.chapter(14, 'Question 10 — a bounded blocking queue', 'The primitive every concurrency follow-up reduces to · adjacent, not reported standalone',
          """Question ten. A bounded blocking queue: producer and consumer. To be precise about the evidence, it is not """
          """reported as a standalone question for this round. It is here because the concurrency pivot is the most """
          """consistent finding in every report, and this is the primitive those follow-ups reduce to. If you can write this """
          """from memory and explain every line, you can answer any of them.""")

sid = steps_list('The question', [
    (0, '`Enqueue` blocks while full; `TryDequeue` blocks while empty', 'info'),
    (1, 'Cancellation: a waiting caller can give up', 'info'),
    (2, 'Shutdown: `Complete()` — no new items; consumers drain the rest, then stop', 'shared'),
    (3, 'Say first: in production this is `Channel.CreateBounded<T>`. Then build it', 'ok'),
])
for i, t in enumerate([
    """Enqueue blocks while the queue is full, and dequeue blocks while it is empty.""",
    """A waiting caller can cancel.""",
    """And complete shuts it down gracefully: no new items, consumers drain what is left, then stop.""",
    """Say first that in production you would use a bounded channel. Then build it, because the interviewer wants to see """
    """you own the synchronisation."""]):
    seg(sid, i, t)

BQ = fit(join(CS.cs_member('aicoding/D01_BoundedQueue.cs', 'BoundedBlockingQueue', 'public void Enqueue', comment=False),
              CS.cs_member('aicoding/D01_BoundedQueue.cs', 'BoundedBlockingQueue', 'public bool TryDequeue', comment=False),
              CS.cs_member('aicoding/D01_BoundedQueue.cs', 'BoundedBlockingQueue', 'public void Complete', comment=False)))
code_slide('One monitor, while loops, PulseAll', BQ, [
    (rng(BQ, 'public void Enqueue', 'using var reg = ct.Register(Wake);'),
     """Monitor wait does not take a cancellation token, so register a callback that wakes the waiters when the token """
     """fires."""),
    (rng(BQ, 'lock (_gate) {', 'Monitor.Wait(_gate);'),
     """Under the lock: while full and not completed, check for cancellation and wait. While, not if."""),
    (rng(BQ, 'ct.ThrowIfCancellationRequested();', 'Monitor.PulseAll(_gate);'),
     """After waking: honour cancellation, refuse after completion so no item is silently lost, enqueue, and pulse all, """
     """because producers and consumers share one monitor and a single pulse can wake the wrong kind."""),
    (rng(BQ, 'public bool TryDequeue', 'return true;'),
     """Dequeue is the mirror image. It returns false only when the queue is completed and drained: that is the signal a """
     """consumer loop needs to stop."""),
    (rng(BQ, 'public void Complete', 'public void Complete'),
     """And complete sets the flag and wakes everyone."""),
], kicker='Producer / consumer')

sid = cards('Follow-ups', [
    (0, 'Async version', 'A bounded Channel; or SemaphoreSlim pairs for slots and items', 'ok'),
    (1, 'Many producers, one consumer', 'Same code; SingleReader = true on a Channel enables a faster path', 'shared'),
    (2, 'Back-pressure in production', 'Blocking the producer IS back-pressure — or drop and count, if callers must never block (the logger)', 'dp'),
    (3, 'Priority', 'PriorityQueue inside the lock; watch for starvation of low priorities', 'info'),
], cols=2, kicker='Follow-ups')
for i, t in enumerate([
    """The async version: a bounded channel, or a pair of semaphores for free slots and available items.""",
    """Many producers and one consumer: the same code, and on a channel, single-reader enables a faster path.""",
    """Back-pressure in production: blocking the producer is back-pressure. If callers must never block, as with the """
    """logger, drop and count instead.""",
    """And priority: a priority queue inside the lock, and watch for low priorities starving."""]):
    seg(sid, i, t)

# ======================================================================== debugging existing code
E.chapter(15, 'Task type: debug an existing codebase', 'Reported format: fix a bug → add a feature → optimise',
          """Chapter fifteen. Several reports describe the round starting from existing code: fix a bug, then add a feature, """
          """then optimise. So here is how to debug code you did not write, with the assistant, using two real defects. Each """
          """is reproduced by a test.""")

sid = steps_list('Debugging with an assistant', [
    (0, '**Reproduce** — turn the symptom into a failing test before reading the code closely', 'ok'),
    (1, '**Hypothesise** — say where you think it is, and why', 'info'),
    (2, '**Ask narrowly** — "explain what happens when X" or "where could Y be lost?", not "fix it"', 'shared'),
    (3, '**Fix the cause**, then run the failing test and the old ones', 'ok'),
    (4, '**Say what changed** so the class of bug cannot recur', 'dp'),
])
for i, t in enumerate([
    """Debugging with an assistant, five steps. Reproduce first: turn the symptom into a failing test before you read the """
    """code closely.""",
    """Hypothesise out loud: where you think the bug is and why.""",
    """Ask narrowly. Explain what happens when two threads do this, or where could this value be lost. Not, fix it: a fix """
    """for a bug you do not understand is a second bug.""",
    """Fix the cause, then run the failing test and every old one.""",
    """And say what changed so this class of bug cannot come back."""]):
    seg(sid, i, t)

D1 = fit(CS.cs_type('aicoding/Debug.cs', 'D1_Lru', comment=False))
code_slide('Bug 1 · "The entry I used most recently is the one that disappears."', D1,
           halves(D1, """Bug one. The user reports: the entry I used most recently is the one that disappears. Here is the """
                      """code. Get moves the node to the front, which is right.""", 'And here is put.'), kicker='Debugging')
think('Which line evicts, and which end of the list does it take?', 20,
      """Pause. Find the line that evicts. Which end of the list does it take?""",
      """Put evicts from the first node, and the first node is the most recently used. It should remove the last. One word, """
      """first versus last, and the test that catches it is the one you always write: put, put, get, put, then check what """
      """survived.""")

D2 = fit(CS.cs_type('aicoding/Debug.cs', 'D2_TtlCache', comment=False))
D2 = '\n'.join(l for l in D2.split('\n') if 'BetweenCheckAndAct = ' not in l)
code_slide('Bug 2 · "Under load, a value I just wrote is sometimes gone."', D2,
           halves(D2, """Bug two, and it only happens under load: a value I just wrote is sometimes gone on the next read. """
                      """Every access takes the lock.""", 'Now look at get.'), kicker='Debugging')
think('Get takes the lock twice. What can happen between the two?', 20,
      """Pause. Get takes the lock twice. What can another thread do in between?""",
      """Get checks expiry under one lock, releases it, then removes by key under a second lock. In the gap, another thread """
      """puts a fresh value for the same key, and the remove deletes the fresh value. The fix: check and remove under one """
      """lock, or remove only if the map still holds the exact entry you judged expired. And the lesson: every lock in a """
      """method can be fine, while the method is still not atomic. The test reproduces it deterministically with a seam """
      """between the check and the act.""")

# ======================================================================== the full run-through
E.chapter(16, 'A full 60 minutes: the logging library, run end to end', 'Everything in this video, in the order it happens',
          """Chapter sixteen. Everything in this video, in the order it would actually happen, using the freshest reported """
          """question: the logging library. Minute by minute, what you do, what you prompt, and what you say.""")

RUN_ROWS = [
    (0, ['0–4', 'Restate; ask: what makes two logs identical? is the window per key?', '"Identical means severity, function, line and message — right?"']),
    (1, ['4–8', 'Write the interface, the Key record, the throttle table; 3 hand cases', '"Decide under the lock, write outside it."']),
    (2, ['8–16', 'Prompt: implement phase 1 + 3 against my interface. Read it. Run cases', '"Checking the expiry boundary first."']),
    (3, ['16–22', 'Prompt: tests with reasons. Fix one wrong expected value', '"That expected count is wrong: the first log prints."']),
    (4, ['22–32', 'Phase 4 aggregation; injected clock; test exactly at window end', '"Summary uses the first timestamp of the window."']),
    (5, ['32–45', 'Thread-safety: lock only the table; reject I/O under the lock', '"A slow sink would serialise every caller."']),
    (6, ['45–55', 'Production: bounded channel, drop counter, purge, sink failure', '"DropWrite hides drops — I\'d use Wait + TryWrite."']),
    (7, ['55–60', 'Trade-offs and what you would do next', '"Next: metrics on drops, and per-sink queues."']),
]
RUN_NARR = [
    """Minutes zero to four. Restate it, and ask the questions that change the code: what makes two logs identical, and is """
    """the window per key?""",
    """Four to eight. Write the interface, the key record and the throttle table yourself, plus three hand cases. Say the """
    """design rule: decide under the lock, write outside it.""",
    """Eight to sixteen. Prompt the implementation of phases one and three against your interface. Read it, starting at """
    """the expiry boundary, and run your cases.""",
    """Sixteen to twenty-two. Ask for tests with a reason for each expected value, and check them. Expect at least one """
    """wrong expected value, and say so when you fix it.""",
    """Twenty-two to thirty-two. Phase four, aggregation, with the injected clock and a test exactly at the end of the """
    """window.""",
    """Thirty-two to forty-five. Thread-safety: lock only the table, and if the assistant puts the sink write inside the """
    """lock, reject it with the reason.""",
    """Forty-five to fifty-five. Production: a bounded channel, a drop counter that actually counts, purging idle windows, """
    """and isolating a failing sink.""",
    """And the last five minutes: the trade-offs, and what you would do next with more time."""]
for title, lo, hi in [('The logging library, minute by minute (1 of 2)', 0, 4), ('The logging library, minute by minute (2 of 2)', 4, 8)]:
    sid = table(title, ['Minutes', 'You do', 'You say'], [(k - lo, RUN_ROWS[k][1]) for k in range(lo, hi)], kicker='Run-through')
    for k in range(lo, hi):
        seg(sid, k - lo, RUN_NARR[k])

sid = cards('If you fall behind', [
    (0, 'Cut polish, not follow-ups', 'Ugly-but-correct code plus a strong concurrency discussion beats perfect phase-1 code', 'ok'),
    (1, 'Say the design you would write', 'If time runs out mid-phase, describe the code and its test in two sentences', 'shared'),
    (2, 'Never paste to catch up', 'Unread pasted code is the clearest way to fail this round', 'deny'),
], cols=1, kicker='Run-through')
for i, t in enumerate([
    """If you fall behind: cut polish, never the follow-ups. Correct but plain code plus a strong concurrency discussion """
    """beats a perfect phase one.""",
    """If time runs out mid-phase, describe the code you would write and its test, in two sentences.""",
    """And never paste unread code to catch up. That is the clearest way to fail this round."""]):
    seg(sid, i, t)

E.chapter(17, 'What to take into the room', 'The pattern across all ten',
          """Last part. What all ten questions have in common, and what to take into the room.""")

ROWS = [
    ['LRU → TTL → threads', 'Dict + linked list; lazy expiry + bounded sweep; one lock; shard to scale', 'Get not a use · ConcurrentDictionary ≠ thread-safe'],
    ['LRU with counters', 'Read-through counters; predict before measuring', 'A cyclic scan one key larger than the cache: 0% hits'],
    ['LFU + GetRank', 'Bucket per frequency + min-freq; rank via sorted counts', 'Claims O(1) GetRank'],
    ['Logging library', 'Throttle table keyed on 4 fields; decide under lock, write outside', 'I/O under the lock · DropWrite hides drops'],
    ['Delay scheduler', 'PriorityQueue + one worker; Pulse on schedule; run outside lock', '`if` not `while` · Pulse wakes the wrong thread'],
    ['Window counter', 'Ring of per-second slots', '>= instead of > — a 301-second window'],
    ['Interval manager', 'SortedSet of disjoint intervals; floor + ceiling', 'Contained interval shrinks the cover'],
    ['Structured data', 'Result-with-reason per line; stream and aggregate', 'One catch around the loop drops everything after'],
    ['Friendship graph', 'One BFS core; path → distance reuse; mutual counts', 'Visited on dequeue: correct answer, wasted work'],
    ['Blocking queue', 'One monitor; while + PulseAll; Complete to drain', '`if` not `while` · Pulse wakes a producer'],
]
NARR = [
    """L R U: dictionary plus linked list, lazy expiry with a bounded sweep, one lock, shard to scale. The assistant forgot """
    """that a get is a use, and claimed a concurrent dictionary made it thread-safe.""",
    """L R U with counters: predict before you measure. The scan one key larger than the cache gets nothing.""",
    """L F U: a bucket per frequency and a minimum frequency. The assistant claims a constant time rank.""",
    """The logger: a throttle table keyed on four fields, decide under the lock and write outside it. The assistant held the """
    """lock across I O, and its drop-write channel hid every drop.""",
    """The scheduler: a priority queue, one worker, pulse on schedule, run outside the lock. Assistants write if instead of """
    """while, and pulse the wrong thread.""",
    """The counter: a ring of per-second slots, and an off-by-one at the boundary.""",
    """The interval manager: a sorted set of disjoint intervals with floor and ceiling lookups. The assistant let a contained """
    """interval shrink the cover.""",
    """And structured data: a result with a reason for every line. The assistant's catch around the whole loop dropped """
    """everything after the first bad row.""",
    """The friendship graph: one search reused for path and distance, and mutual counts for suggestions. The assistant's """
    """search marked nodes on dequeue: right answer, wasted work.""",
    """And the blocking queue: one monitor, while loops, pulse all, and complete to drain. The assistant's version used if """
    """and a single pulse."""]
for title, lo, hi in [('The ten, in one table (1 of 3)', 0, 4), ('The ten, in one table (2 of 3)', 4, 7), ('The ten, in one table (3 of 3)', 7, 10)]:
    sid = table(title, ['Question', 'Design in one line', 'What the AI got wrong'],
                [(k - lo, ROWS[k]) for k in range(lo, hi)], kicker='Recap')
    for k in range(lo, hi):
        seg(sid, k - lo, NARR[k])

sid = steps_list('Take into the room', [
    (0, 'Say the design and write **three test cases by hand** before the first prompt', 'ok'),
    (1, 'Prompt **narrowly**: types, complexity, the invariant, what not to do yet', 'ok'),
    (2, 'Read every line against the invariant — **"would I ship this?"**', 'deny'),
    (3, 'Prove a defect with a **test**, not an opinion', 'shared'),
    (4, 'Leave **15 minutes** for thread-safety and production — that is the Staff signal', 'dp'),
    (5, 'Never say "the AI says it is thread-safe". Say what the lock protects', 'info'),
], numbered=True)
for i, t in enumerate([
    """Say the design and write three test cases by hand before your first prompt.""",
    """Prompt narrowly: the types, the complexity, the invariant, and what not to do yet.""",
    """Read every line against the invariant, and ask: would I ship this?""",
    """Prove a defect with a test, not an opinion.""",
    """Leave fifteen minutes for thread-safety and production, because that is where the Staff signal is.""",
    """And never say the A I says it is thread-safe. Say what the lock protects. Good luck."""]):
    seg(sid, i, t)
