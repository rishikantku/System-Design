# -*- coding: utf-8 -*-
"""Chapter 11 — the Coding-with-AI round, worked through five design questions in one video.

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


lesson_header('11', 'The AI-assisted coding round — five design questions, end to end',
              'Caches · logger · scheduler · counters', 'Highest',
              'Official pack + 5 logging reports (Aug–Sep 2026) + LRU AI-round reports', 'Sep 2026', 'High', 28,
              """This video is about one round: LinkedIn's Coding with A I module. Sixty minutes, CoderPad, with an A I """
              """assistant built in, and you are expected to use it. We will do two things. First, what the round """
              """actually expects, and a way of working that fits it. Then five questions, the kind this round favours: """
              """not puzzle algorithms, but small systems. An L R U cache with a time to live. An L F U cache with a rank """
              """query. A logging library. A delay scheduler. And a sliding window counter. For each one: the requirements, """
              """how I would design it before touching the assistant, the prompt I would actually type, the C sharp, the """
              """mistake the assistant makes, and the follow-ups. Every listing you will see compiled and passed its tests.""")

# ======================================================================== part 0: the round
E.chapter(0, 'What the round expects', 'Official pack · how it runs · how to work',
          """Part one. What the round expects, in the recruiter's own words, and then how to work inside it.""")

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

sid = steps_list('How the round runs', [
    (0, '**CoderPad with AI Assist** — a chat assistant beside the editor. Not a prompt-engineering test', 'info'),
    (1, 'Requirements arrive **in phases** — build, then extend, then "now make it thread-safe"', 'info'),
    (2, 'The interviewer **interrupts** to ask why you prompted that, and how you know it works', 'shared'),
    (3, 'Reported Staff questions: **logging library**, **LRU cache → TTL → threads**, LFU with rank', 'ok'),
    (4, 'Most-reported mistake: **too long on the first phase**, no time for the follow-ups', 'deny'),
])
seg(sid, 0, """How it runs. CoderPad, with its built-in assistant beside the editor. The pack says plainly that this is not a """
            """prompt engineering test.""")
seg(sid, 1, """Requirements come in phases. You build the core, then it is extended, and almost always it ends with: now """
            """make it thread-safe, or now productionise it.""")
seg(sid, 2, """The interviewer will interrupt. Why did you ask for that? How do you know the generated code is correct?""")
seg(sid, 3, """And the questions reported for this round are exactly the kind in this video: a logging library with """
            """severity, throttling and aggregation, five reports in August and September twenty twenty-six, one of them """
            """Staff. An L R U cache climbing to time to live and threads. An L F U cache with a rank query at Staff level.""")
seg(sid, 4, """The most repeated mistake in candidate reports: spending too long on phase one and running out of time for """
            """the follow-ups, which is where the Staff signal is.""")

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
E.chapter(1, 'Question 1 — LRU cache → TTL → thread-safe', 'Reported for the AI round · strongest evidence',
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
E.chapter(2, 'Question 2 — LFU cache with GetRank()', 'Reported once, at Staff level (Feb 2026)',
          """Question two. An L F U cache, least frequently used, with an L R U tie-break, and a get-rank query. Reported once, """
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
E.chapter(3, 'Question 3 — the logging library', '5 reports, Aug–Sep 2026, one Staff · the freshest evidence',
          """Question three, and the freshest evidence in all the research: a logging library with severity filtering, """
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
E.chapter(4, 'Question 4 — the delay scheduler', 'LinkedIn coding question (InterviewDB) · round not stated',
          """Question four. A delay scheduler, the C sharp version of a scheduled executor: run this action after this delay. """
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
E.chapter(5, 'Question 5 — sliding-window counter', 'Pattern practice · not a reported AI-round question',
          """Question five. A sliding window counter: how many events in the last five minutes. To be honest about the """
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
E.chapter(6, 'What to take into the room', 'The pattern across all five',
          """Last part. What all five questions have in common, and what to take into the room.""")

sid = table('The five, in one table', ['Question', 'Design in one line', 'What the AI got wrong'], [
    (0, ['LRU → TTL → threads', 'Dict + linked list; lazy expiry + bounded sweep; one lock; shard to scale', 'Get not a use · ConcurrentDictionary ≠ thread-safe']),
    (1, ['LFU + GetRank', 'Bucket per frequency + min-freq; rank via sorted counts', 'Claims O(1) GetRank']),
    (2, ['Logging library', 'Throttle table keyed on 4 fields; decide under lock, write outside', 'I/O under the lock · DropWrite hides drops']),
    (3, ['Delay scheduler', 'PriorityQueue + one worker; Pulse on schedule; run outside lock', '`if` not `while` · Pulse wakes the wrong thread']),
    (4, ['Window counter', 'Ring of per-second slots', '>= instead of > — a 301-second window']),
], kicker='Recap')
for i, t in enumerate([
    """L R U: dictionary plus linked list, lazy expiry with a bounded sweep, one lock, shard to scale. The assistant forgot """
    """that a get is a use, and claimed a concurrent dictionary made it thread-safe.""",
    """L F U: a bucket per frequency and a minimum frequency. The assistant claims a constant time rank.""",
    """The logger: a throttle table keyed on four fields, decide under the lock and write outside it. The assistant held the """
    """lock across I O, and its drop-write channel hid every drop.""",
    """The scheduler: a priority queue, one worker, pulse on schedule, run outside the lock. Assistants write if instead of """
    """while, and pulse the wrong thread.""",
    """The counter: a ring of per-second slots, and an off-by-one at the boundary."""]):
    seg(sid, i, t)

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
