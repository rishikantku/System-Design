# -*- coding: utf-8 -*-
"""Teaching content for the CWAI training platform: the model of the round, the playbook, the
workflow, prompting, rejection patterns, the checklist, timing, the rubric and the roadmap.

The rubric and time plans are shared with the simulator page (aisim.py), so they live here once.
"""

# ---------------------------------------------------------------- the two loops
TRADITIONAL = ['Problem', 'Think', 'Code', 'Test', 'Optimise']
AI_ASSISTED = ['Understand', 'Clarify', 'Design', 'Decide what to delegate', 'Prompt', 'Inspect output',
               'Validate', 'Test', 'Debug', 'Absorb a requirement change', 'Refactor',
               'Reason about production', 'Explain the trade-offs']

WHAT_CHANGES = [
 ('Typing is no longer the bottleneck',
  'In a normal round, writing a correct LRU takes most of the 45 minutes, so finishing it is the signal. Here an assistant produces a plausible '
  'one in thirty seconds. Finishing stops being evidence of anything. The interviewer has to look somewhere else for signal, and they look at '
  'the decisions around the code: what you asked for, what you accepted, what you caught.'),
 ('The interviewer gets more code to judge, not less',
  'A LinkedIn employee put it bluntly: "it\'s a lot more code to write". Because the typing is cheap, the problem is bigger, and the '
  'requirements keep arriving. You will be extending code you did not fully write, which is a reading skill as much as a writing one.'),
 ('Your judgement is now visible',
  'In CoderPad the AI conversation sits on screen next to your code. Every prompt is evidence of how you decompose a problem. Every accepted '
  'answer is evidence of what you checked. A silent paste is evidence too.'),
 ('Follow-ups decide the result',
  'Every source agrees the follow-ups are where the round is won: concurrency, synchronisation, scale, "how would you productionise this?". '
  'Candidates who spend 35 minutes getting the first version working run out of room for the part that is actually scored.'),
]

PRINCIPLE = ('AI is a tool, not a substitute for engineering judgement. You may let it type almost everything. You may not let it decide '
             'anything you cannot defend.')

# ---------------------------------------------------------------- staff vs senior
STAFF = [
 ('Problem decomposition', 'Breaks the problem into the parts the interviewer named', 'Names the part that will change next and keeps it behind an interface'),
 ('API design', 'Methods that work', '`TryGet(out)` instead of a magic -1; says what each method guarantees and what it does not'),
 ('Correctness', 'Tests the happy path and one edge', 'States the invariant ("map and list always hold the same keys") and tests that'),
 ('Concurrency', 'Adds a lock when asked', 'Names the synchronization boundary before writing it, and what it costs under contention'),
 ('Production', 'Mentions metrics', 'Says which metric pages someone, what the failure mode is, and how memory is bounded'),
 ('Requirement change', 'Rewrites the class', 'Changes the smallest component, and says which components did not need to change'),
 ('AI use', 'Asks for code', 'Asks for a specific piece, with constraints, and rejects an answer with a reason'),
 ('Trade-offs', 'Picks one', 'Prices both, picks one, and says what would make them change their mind'),
]

# ---------------------------------------------------------------- the 8-step workflow
WORKFLOW = [
 dict(n=1, name='Understand', mins='0–5',
      do=['Restate the problem in one sentence, out loud.', 'List the operations and what each returns, including on a miss.',
          'Write down the constraints you have been given and the ones you are assuming.', 'Ask the two or three clarifying questions that change the code.'],
      say='"So this is a cache with two reasons to forget: capacity and time. Before I write anything — does a re-put renew the TTL, and does an expired entry still count toward capacity?"',
      ai='Usually none. If the statement is long or the starter code is unfamiliar, it is fine to ask the assistant to summarise the code — then check the summary against the code.',
      trap='Pasting the statement into the assistant before you have read it. The pack allows exploring with AI first; it does not reward skipping the reading.'),
 dict(n=2, name='Design', mins='5–10',
      do=['Write the interface — signatures only — in the editor.', 'Name the data structures and why each one is there.',
          'State the invariant the structure maintains.', 'State the complexity target.', 'Say how you will test it.'],
      say='"Dictionary for lookup, LinkedList for recency; the invariant is that both hold the same keys. O(1) for both operations. I\'ll test capacity one, update-in-place, and eviction after a read."',
      ai='Optional: "Give me two other ways to structure this and their complexity — no code." Useful at Staff level because it shows you considered alternatives.',
      trap='Letting the assistant pick the data structure. That is the decision being scored.'),
 dict(n=3, name='Decide what to delegate', mins='—',
      do=['Delegate: implementation of a design you specified, boilerplate, parsing, test scaffolding, alternative approaches, bug hunts, complexity review.',
          'Keep: the data structure choice, the invariant, the synchronization boundary, the API contract, the decision about what "correct" means.'],
      say='"I\'ll have it write the list manipulation — that\'s mechanical. The eviction rule I\'ll check by hand."',
      ai='The test of a good delegation: could you check the answer in less time than writing it yourself? If not, write it yourself.',
      trap='"Solve this problem completely." You will spend the next ten minutes reading code you did not ask for.'),
 dict(n=4, name='Generate', mins='10–20',
      do=['Give context (the interface you wrote), constraints (complexity, no new public members), and the output shape (only this method; a diff; no prose).'],
      say='"I\'m giving it my interface and asking only for Put, keeping the field names."',
      ai='See the prompt templates below. A precise prompt is shorter to verify, which is the real time saving.',
      trap='Re-prompting the same request with small wording changes, hoping. If the second answer is wrong, write it yourself.'),
 dict(n=5, name='Review', mins='as you go',
      do=['Read it before running it. Out loud, briefly.', 'Check: correctness on the edges, complexity, thread safety, API behaviour on bad input, error handling, resource use.',
          'Look for the defects assistants produce on this kind of problem (each question below lists them).'],
      say='"It used ConcurrentDictionary. That protects the map, not the recency list, so this isn\'t thread-safe — I\'m rejecting it."',
      ai='Ask it to review its own output for one named class of bug. Never "is this correct?" — it will say yes.',
      trap='Running it, seeing green, and moving on. Tests you did not write test what the assistant thought of.'),
 dict(n=6, name='Test', mins='20–28',
      do=['Run the happy path, then the boundaries: empty, one, capacity, duplicate, invalid.', 'Ask the assistant for adversarial tests, then read each one and check the expected value yourself.',
          'Add the one test that would have caught the bug you fixed.'],
      say='"It generated eight tests. Two of these expected values are wrong — it thinks an expired key still counts as present."',
      ai='Generated tests are the highest-value delegation in the round — and generated expected values are the most common thing to be wrong.',
      trap='Treating generated tests as verification. A test with a wrong expected value verifies the bug.'),
 dict(n=7, name='Modify', mins='28–45',
      do=['Restate the new requirement and which part of the design it touches.', 'Change that part. Keep the tests that still apply; add ones for the new behaviour.',
          'Say what did not need to change — that is the evidence the design was right.'],
      say='"TTL only touches the entry and the read path. Eviction and the list don\'t change, which is why I kept recency separate."',
      ai='"The requirement changed to X. Modify the existing code with minimal disruption; list which members change and which do not."',
      trap='Asking the assistant to regenerate the whole class with the new requirement. You lose the code you already verified.'),
 dict(n=8, name='Defend', mins='45–60',
      do=['Why this approach, this data structure, this locking strategy.', 'What happens under concurrency, at scale, when the dependency is slow, when memory grows.',
          'What you would change for production, in priority order.'],
      say='"One lock is right until it shows up in a profile. The next step is sharding by key hash, which makes LRU approximate — I\'d accept that and measure the hit-ratio cost."',
      ai='None. This part is yours.',
      trap='"The AI chose it." Every accepted line is your decision now.'),
]

# ---------------------------------------------------------------- prompt templates
PROMPTS = [
 dict(name='Implementation', when='After you have written the interface and named the structures.',
      text='Implement the following C# interface. Before writing code, state your assumptions, the data structures you will use and the expected complexity of each method. '
           'Keep the implementation minimal and testable: no extra public members, no logging, no comments beyond one line per method.\n\n<paste interface + your field declarations>',
      why=['"State assumptions first" makes the assistant expose the decisions it would otherwise make silently — you catch a wrong assumption before reading 60 lines.',
           '"No extra public members" stops it widening your API, which you would then have to defend.',
           'Pasting your own field declarations pins the data structures — the design stays yours.']),
 dict(name='Review', when='When you have code — yours or generated — and want a second reader.',
      text='Review this implementation for correctness, edge cases, complexity and concurrency issues. Do not rewrite it. First list the problems you find, most severe first, '
           'each with the input that triggers it.\n\n<paste code>',
      why=['"Do not rewrite it" keeps the output short enough to verify, and keeps your code your code.',
           '"The input that triggers it" turns a vague concern into a test you can run in ten seconds — and exposes false alarms.',
           'Ranking by severity tells you which finding to spend your limited minutes on.']),
 dict(name='Tests', when='After the first working version.',
      text='Generate adversarial test cases for this implementation as plain assertions: boundary conditions, duplicate keys, empty input, capacity one, and concurrent access where applicable. '
           'For each test, state in a comment why the expected value is correct.\n\n<paste code + the contract you stated>',
      why=['"Why the expected value is correct" is the line that matters: it makes the assistant\'s reasoning checkable, and wrong expected values are its most common test defect.',
           'Plain assertions rather than a framework — CoderPad may not have xUnit, and you do not want to debug test infrastructure.',
           'Giving it your contract stops it testing behaviour you never promised.']),
 dict(name='Optimisation', when='When the interviewer says "now assume millions of requests" or you see a hotspot.',
      text='Analyse this implementation for performance bottlenecks under <workload>. Suggest improvements without changing the external API. For each, give the complexity before and after and what it costs.',
      why=['Naming the workload stops generic advice. "Read-heavy, 10:1" and "write-heavy" have different answers.',
           '"Without changing the external API" is the constraint a Staff engineer imposes on every refactor.',
           '"What it costs" forces the trade-off into the answer — which is what you will have to say out loud anyway.']),
 dict(name='Concurrency', when='The concurrency follow-up, which you should expect.',
      text='Analyse this implementation for race conditions and thread-safety issues if Get and Put are called from multiple threads. For each race, give the interleaving that breaks it. '
           'Then identify the smallest synchronization boundary that preserves correctness. Do not write code yet.',
      why=['"The interleaving that breaks it" separates a real race from a vague worry, and gives you the sentence to say.',
           '"Smallest boundary" is the Staff-level question: not "add locks" but "where exactly".',
           '"Do not write code yet" — you decide the boundary, then ask for it.']),
 dict(name='Requirement change', when='Every time the interviewer adds something.',
      text='The requirements have changed: <new requirement>. Modify the existing design with minimal disruption. First list which types and members need to change and which do not, then show only the changed members.',
      why=['Asking for the impact list first means you can disagree before any code exists.',
           '"Only the changed members" protects everything you already verified.',
           'The "which do not change" half is the evidence your original design was right — say it to the interviewer.']),
 dict(name='Bug hunt', when='A test fails and the cause is not obvious within a minute.',
      text='This test fails: <test>. Expected <x>, got <y>. Here is the code. Give the two most likely causes, each with the line responsible and the reasoning. Do not fix it.',
      why=['Two hypotheses, not one: stops it anchoring on the first idea and gives you a choice to make.',
           '"Do not fix it" — you verify the cause, then fix it yourself or ask for the specific fix.']),
 dict(name='Explain unfamiliar code', when='Debug-and-extend rounds that start with existing code.',
      text='Summarise what this class does, its invariants, and any method whose behaviour looks inconsistent with the others. Quote line numbers.',
      why=['Line numbers make the summary checkable against the code in seconds.',
           '"Inconsistent with the others" is a cheap way to find the planted bug in a debug-first round.']),
]

# ---------------------------------------------------------------- rejection patterns
REJECTED = [
 ('Asking AI to solve everything immediately',
  '"Implement an LRU cache with TTL that is thread-safe." → 80 lines, three decisions you never made, ten minutes reading them.',
  'Write the interface and the invariant. "Implement Put for this interface, O(1), keep my field names." → 15 lines you can check in one pass.'),
 ('Copy-pasting code without understanding it',
  'Pastes the response, runs it, says "looks good".',
  'Pastes it, then: "It evicts from `_order.Last` — that\'s the LRU end, right. It doesn\'t remove from the map on update — fine, the key is the same."'),
 ('Not checking generated code',
  'Accepts a "thread-safe" version that swapped `Dictionary` for `ConcurrentDictionary`.',
  '"ConcurrentDictionary makes each map call atomic, but Get also moves a list node. Two threads can corrupt the list. Rejecting."'),
 ('Missing edge cases',
  'Tests put-then-get.',
  'Tests capacity one, update-in-place, eviction after a read, an expired key exactly at the TTL boundary, and an empty cache.'),
 ('Accepting incorrect complexity',
  'The assistant says GetRank is O(1); the candidate repeats it.',
  '"It walks the frequency map — that\'s O(distinct frequencies). Not O(1). Fine for this; an order-statistics tree gives log n."'),
 ('Not running tests', 'Explains why the code is correct instead of running it.', 'Runs the tests first, then explains — and lets a failure change the plan.'),
 ('Not explaining generated code',
  'Long silence while reading 60 lines of output.',
  'Narrates while reading: what each part does, what was expected, what was surprising.'),
 ('Restarting after every follow-up',
  '"Add TTL" → asks for a new class with TTL. "Make it thread-safe" → asks for a new thread-safe class. Three versions, none verified.',
  'Adds an expiry field and one check in the read path. Wraps the same class in a lock. Each change is ten lines and keeps the old tests.'),
 ('Overengineering',
  'The interviewer asks for key validation; the candidate prompts for a validator interface, a strategy pattern and a factory. (Reported: a 2025 AI-round candidate did exactly this.)',
  'A private method and a sentence: "if validation rules start varying by caller, then it becomes an injected `Func<TKey,bool>`."'),
 ('Ignoring interviewer hints',
  'The interviewer asks "what if two threads call Put at once?" — the candidate says "it\'s fine, ConcurrentDictionary".',
  'Treats every question as a hint: "Let me trace that. Thread A evicts, thread B…"'),
 ('Spending too long prompting', 'Five rounds of re-prompting for a 10-line method.', 'Second wrong answer → writes it by hand. Says so: "Faster to write this one myself."'),
 ('Treating AI as authoritative', '"The AI says this is the standard approach."', '"The assistant suggested X. I checked it against Y and chose it because Z."'),
]

# ---------------------------------------------------------------- playbook sections (15)
PLAYBOOK = [
 ('What the round tests', 'Engineering fundamentals, used through an assistant. The pack lists six things: fundamentals; intentional AI use; critical evaluation of AI output; '
  'iterating on issues; communicating decisions and trade-offs; and a correct, maintainable, well-reasoned result. Note what is not on that list: speed of prompting, number of '
  'prompts, or cleverness with the tool. Production thinking is not in the pack\'s list, but every candidate report says the follow-ups go there.'),
 ('Likely interview format', '60 minutes in CoderPad with AI Assist (pack). The editor is in the middle, the chat panel is on the right, and you copy code across yourself (reported). '
  'Expect a familiar problem, then requirements added one at a time, then a concurrency or production pivot (reported). You may instead be handed existing code with a bug '
  '(reported once, ≈Mar 2026). The pack says "one or more coding problems", so plan for a second, smaller problem if the first finishes early.'),
 ('How to use AI', 'For things you can verify faster than you can write: implementing a design you specified, boilerplate (parsing, model classes, test scaffolding), alternative approaches '
  'to compare, a second pair of eyes on a named class of bug, and a complexity check. Each use should have a stated purpose you could say out loud.'),
 ('How not to use AI', 'Not to choose the data structure, the invariant, the synchronization boundary or the API contract. Not to "solve the problem". Not to re-ask a question until the '
  'answer looks right. Not to explain code to the interviewer for you. If you find yourself reading output to learn what your design is, you have handed over the wrong thing.'),
 ('Prompting strategy', 'Context, constraint, output shape. Give it your interface. Tell it what must not change. Ask for only the piece you need. Ask it to state assumptions before '
  'writing code. Prefer several small prompts you can verify over one large one you cannot. Templates are below.'),
 ('Code-review strategy', 'Read before running. Check in this order, because this is the order the bugs cost you: (1) does it do what the contract says on the edges; (2) the '
  'complexity, against the target you stated; (3) shared state and thread safety; (4) behaviour on bad input; (5) resource growth. Say each check out loud in one sentence.'),
 ('Testing strategy', 'Happy path, boundaries, empty, invalid, duplicates, large, concurrent. Write the two or three that pin the core invariant yourself. Let the assistant generate the '
  'rest, then audit every expected value — a generated test with a wrong expectation is worse than no test. Inject time (`IClock`) and randomness (`Func<int>`) so tests are '
  'deterministic.'),
 ('Debugging strategy', 'Reproduce first: a failing test before any change. Form two hypotheses, not one. Read the code path for the failing input. Use the assistant for '
  'hypotheses, never for the fix you have not understood. After the fix, keep the test.'),
 ('Requirement-change strategy', 'Restate the change. Name the component it touches and the ones it does not. Change the smallest thing. Keep the old tests passing; add new ones. '
  'If the change does not fit the design, say so and say what you would refactor — that is a Staff signal, not a failure.'),
 ('Concurrency strategy', 'Ask "what happens if two threads run this at once?" for every method that writes — including reads that write, like an LRU Get. Name the shared state. '
  'Name the invariant that spans it. That invariant is your synchronization boundary. Start with one lock; say what you would do when it contends (shard, read-mostly structures, '
  'lock-free counters). Full section below.'),
 ('Productionisation strategy', 'Bounded memory, bounded latency, observable behaviour, safe failure. For each: what grows without limit; what can block; what you would measure; what '
  'happens when the dependency is slow or down. Give a priority order, not a list.'),
 ('Time-management strategy', 'The most-reported failure is spending too long on the first version. Have a working, tested first version by about minute 25 of 60. If you are '
  'stuck on a mechanical piece for more than two minutes, delegate it; if an assistant answer is wrong twice, write it yourself.'),
 ('Common failure modes', 'Silent pasting; letting the assistant choose the design; accepting a wrong complexity; tests with wrong expectations; restarting on each follow-up; '
  'overengineering a small addition; running out of time before the concurrency question. Bad-versus-good examples are below.'),
 ('Staff-level behaviours', 'Owning decisions out loud. Naming the invariant. Pricing trade-offs. Changing the smallest component. Rejecting at least one AI suggestion with a reason. '
  'Raising the production concern before being asked — once, briefly, then returning to the task.'),
 ('Mock interview framework', 'Ten rounds per problem on the simulator page — problem, implement, requirement change, test, "would you ship this?", then five follow-up levels '
  '(correctness, complexity, concurrency, scale, production) — timed against the 60-minute module and scored on the Staff standard: 15 dimensions, 7 AI-collaboration '
  'checks, eight headline scores out of 10, with gates that make blind acceptance of AI output fail.'),
]

# ---------------------------------------------------------------- checklist
CHECKLIST = [
 ('Problem', ['Did I understand the requirements — can I restate them in one sentence?', 'Did I clarify the ambiguity that changes the code?']),
 ('Design', ['Is my API clean — does every method say what it does on a miss and on bad input?', 'Is the data structure appropriate, and can I say why in one sentence?',
             'Is the complexity acceptable, and did I state it before the assistant did?']),
 ('AI', ['Did I tell the assistant what I actually needed — and only that?', 'Did I review its output before running it?', 'Do I understand every important line?',
         'Did I reject or correct at least one suggestion, with a reason?']),
 ('Correctness', ['Did I test the edges: empty, one, capacity, duplicate, invalid?', 'Did I check every generated expected value?', 'Did I test the failure scenario I fixed?']),
 ('Production', ['What happens under concurrency — where is the boundary?', 'What happens under high load — what contends first?', 'What happens when a dependency fails or is slow?',
                 'What happens when memory grows — what bounds it?']),
 ('Communication', ['Can I explain each choice in one sentence?', 'Did I say what I would do next with more time?']),
]

# ---------------------------------------------------------------- time plans
# The pack fixes 60 minutes. Nothing published fixes the split, so these are my plans.
TIME_PLANS = {
 60: [('0–5', 'Understand + clarify', 'Restate, ask 2–3 questions, write the interface'),
      ('5–10', 'Design', 'Structures, invariant, complexity, test plan — out loud'),
      ('10–22', 'Implement', 'Delegate the mechanical parts; review each before running'),
      ('22–28', 'Test', 'Your 2–3 invariant tests + generated adversarial tests, audited'),
      ('28–40', 'Requirement changes', 'One or two additions on the same code'),
      ('40–52', 'Concurrency + production', 'Boundary, contention, memory, failure'),
      ('52–60', 'Wrap-up + their questions', 'What you would do next; questions for them')],
 45: [('0–4', 'Understand + clarify', ''), ('4–8', 'Design', ''), ('8–18', 'Implement', ''), ('18–23', 'Test', ''),
      ('23–33', 'Requirement change', ''), ('33–42', 'Concurrency + production', ''), ('42–45', 'Wrap-up', '')],
 30: [('0–3', 'Understand + clarify', ''), ('3–6', 'Design', ''), ('6–14', 'Implement', ''), ('14–18', 'Test', ''),
      ('18–24', 'Requirement change', ''), ('24–30', 'Concurrency + production', '')],
}

# ---------------------------------------------------------------- scoring — the Staff Engineer standard
# The reader's standard (Oct 2026): 15 dimensions, the 7 AI-collaboration checks, eight headline
# scores out of 10, a verdict, and the three biggest areas to improve.
# Each: (key, name, what 1 looks like, what 3 looks like, what 5 looks like)
STAFF15 = [
 ('understand', 'Problem understanding', 'Starts from a misread problem', 'Restates it; catches the main constraint', 'Finds the hidden requirement (e.g. "expired still occupies capacity")'),
 ('clarify', 'Requirements clarification', 'Asks nothing that changes the code', 'Asks the obvious questions', 'Asks the 2–3 questions that change the code, and says what each answer changes'),
 ('algo', 'Algorithm', 'Cannot justify the approach', 'A correct approach', 'Compares alternatives, picks one for a stated reason'),
 ('ds', 'Data structure choice', 'Wrong or unjustified structure', 'Right structure', 'Right structure, the invariant stated, the C# type justified'),
 ('correct', 'Correctness', 'Fails basic cases', 'Works on the main path and obvious edges', 'Correct at the boundaries, with the invariant tested'),
 ('quality', 'Code quality', 'Tangled; leaky API', 'Readable, sensible names', 'Small API with clear contracts; the next change fits without a rewrite'),
 ('csharp', 'C# proficiency', 'Misuses core types', 'Idiomatic for the basics', 'Right primitive for each job, and can explain how it behaves (atomicity, complexity, allocation)'),
 ('test', 'Testing', 'None, or happy path only', 'Edges covered and run', 'Invariant tests + audited generated tests; time and randomness injected'),
 ('aiuse', 'AI usage', '"Solve this" prompts; many re-prompts', 'Specific asks with some context', 'Each prompt has a stated purpose: context + constraint + output shape'),
 ('verify', 'AI-output verification', 'Pastes and runs; accepts a wrong answer', 'Reads output; catches the obvious', 'Reads before running; rejects a plausible-but-wrong suggestion with the input that breaks it'),
 ('conc', 'Concurrency', '"Use ConcurrentDictionary"', 'A correct lock', 'Names the shared invariant, the boundary, the contention cost and the next step'),
 ('scale', 'Scalability', 'No view beyond one machine and small N', 'Names the first bottleneck', 'Orders what breaks at 10× and 100×, with the fix and its cost'),
 ('prod', 'Production thinking', 'None', 'Mentions metrics when asked', 'Raises memory bounds, failure modes and alerts unprompted, in priority order'),
 ('comm', 'Communication', 'Long silences', 'Explains when asked', 'Narrates decisions continuously and concisely'),
 ('judge', 'Engineering judgment', 'Defers to the tool', 'Owns most decisions', 'Owns every decision, prices trade-offs, knows when not to use AI'),
]
AI7 = [
 ('ai_prompt', 'Prompt quality', 'Did I give the assistant enough context?', 'No code or constraints given', 'Interface and constraints given', 'Context, constraint and output shape every time'),
 ('ai_deleg', 'Delegation', 'Did I delegate the right tasks?', 'Delegated the design', 'Delegated mostly mechanical work', 'Delegated only what was faster to verify than to write'),
 ('ai_verify', 'Verification', 'Did I verify the generated code?', 'Ran it, did not read it', 'Read most of it', 'Read every accepted line before running; said what was checked'),
 ('ai_crit', 'Critical thinking', 'Did I catch incorrect assumptions?', 'Repeated its claims', 'Questioned some', 'Caught a wrong claim (complexity, API behaviour) and proved it'),
 ('ai_test', 'Testing with AI', 'Did I ask for or create tests?', 'No tests', 'Asked for tests and ran them', 'Asked for tests, audited every expected value, added the regression test'),
 ('ai_own', 'Architecture ownership', 'Did I stay responsible for the design?', 'The tool chose the design', 'Mostly my design', 'Every structural decision was mine and stated before prompting'),
 ('ai_adapt', 'Adaptability', 'Could I modify AI code when requirements changed?', 'Regenerated from scratch', 'Modified with some churn', 'Changed the smallest component; named what did not change'),
]
# Headline scores out of 10 = 2 × the mean of the listed 1–5 scores.
HEADLINES = [
 ('Technical Score', ['algo', 'ds', 'correct']),
 ('AI Collaboration', [k for k, *_ in AI7] + ['aiuse', 'verify']),
 ('Code Quality', ['quality', 'csharp']),
 ('Concurrency', ['conc']),
 ('Scalability', ['scale']),
 ('Production Readiness', ['prod', 'test']),
 ('Communication', ['comm']),
 ('Staff-Level Judgment', ['judge', 'understand', 'clarify']),
]
# Verdict rules — my calibration, stated on the page.
#   PASS        mean of the eight headlines ≥ 7.0 AND AI Collaboration ≥ 6 AND Staff-Level Judgment ≥ 6
#               AND AI-output verification ≥ 3 AND no 1 anywhere
#   BORDERLINE  mean ≥ 5.5, or a PASS mean that failed a gate
#   FAIL        otherwise
VERDICT = dict(pass_mean=7.0, border_mean=5.5, gate_headlines={'AI Collaboration': 6, 'Staff-Level Judgment': 6}, gate_dims={'verify': 3})

# Each scored key → anchors on 02-ai-coding.html that train it
TRAIN = {
 'understand': ['wf-1', 'q-lru'], 'clarify': ['wf-1', 'q-records'], 'algo': ['q-lfurank', 'q-intervals'], 'ds': ['q-intervals', 'csharp'],
 'correct': ['testing', 'debugging'], 'quality': ['wf-2', 'staff'], 'csharp': ['csharp', 'concurrency'], 'test': ['testing', 'q-records'],
 'aiuse': ['prompts', 'rejected'], 'verify': ['review', 'rejected'], 'conc': ['concurrency', 'q-queue'], 'scale': ['followups', 'q-lru'],
 'prod': ['q-logging', 'followups'], 'comm': ['wf-8', 'checklist'], 'judge': ['staff', 'checklist'],
 'ai_prompt': ['prompts'], 'ai_deleg': ['wf-3', 'rejected'], 'ai_verify': ['review', 'wf-5'], 'ai_crit': ['review', 'q-lfurank'],
 'ai_test': ['testing'], 'ai_own': ['wf-2', 'staff'], 'ai_adapt': ['wf-7', 'q-logging'],
}

# ---------------------------------------------------------------- roadmap
ROADMAP = [
 dict(n=1, name='AI workflow fundamentals', days='Day 1',
      study='This page, top to bottom once: the model of the round, the eight-step workflow, the prompt templates, the rejection patterns.',
      practice='Run the LRU question in study mode with an assistant open beside it, using only the templates.',
      measure='Could you say the purpose of every prompt before sending it?',
      exit='You can recite the eight steps and the six templates from memory.'),
 dict(n=2, name='Core coding patterns', days='Days 2–3',
      study='Tier 1 questions in study mode: LRU ladder, counting LRU, LFU+rank, interval manager, records.',
      practice='Re-implement each from the interface without looking, with the assistant allowed for mechanical parts only.',
      measure='Time to a working, tested first version.',
      exit='Every Tier 1 question working and tested in under 20 minutes.'),
 dict(n=3, name='AI-assisted implementation', days='Day 4',
      study='The "what assistants get wrong" list for each Tier 1 question.',
      practice='The same questions, prompting for whole methods and verifying every one out loud.',
      measure='How many generated defects did you catch before running the code?',
      exit='You catch the listed trap for each question before a test does.'),
 dict(n=4, name='Code review + debugging', days='Day 5',
      study='Nothing new — this phase is practice.',
      practice='All ten review exercises and all eight debugging exercises, answer hidden, three minutes each.',
      measure='Defects found without revealing.',
      exit='8/10 review and 6/8 debugging found unaided.'),
 dict(n=5, name='Concurrency', days='Day 6',
      study='The concurrency section: the two questions, the C# primitives table, lock granularity, the boundary walkthroughs.',
      practice='Make each Tier 1 solution thread-safe and say the boundary before writing it. Then shard one.',
      measure='Can you give the breaking interleaving for each unsafe version?',
      exit='You name the boundary in one sentence for every Tier 1 question.'),
 dict(n=6, name='Production follow-ups', days='Day 7',
      study='Each question\'s follow-up ladder and production notes.',
      practice='Answer every ladder out loud to the last level, two minutes per level.',
      measure='Did you raise memory bounds and slow dependencies unprompted?',
      exit='Every ladder answered to level 5 without notes.'),
 dict(n=7, name='Timed mocks', days='Days 8–9',
      study='The time plan for 60 minutes.',
      practice='Simulator mocks 1–4, timed, scored, copied to Claude for a second opinion.',
      measure='The weakness tracker: your three lowest dimensions.',
      exit='Two consecutive mocks at PASS.'),
 dict(n=8, name='Full LinkedIn simulation', days='Day 10, and the day before',
      study='Only the checklist.',
      practice='Simulator mock 5: no hints, strict timing, interviewer prompt in a separate Claude chat.',
      measure='Verdict and the verification score.',
      exit='PASS on mock 5. If not, go back to the phase that trains your lowest dimension.'),
]

# ---------------------------------------------------------------- concurrency section
CONC_PRIMS = [
 ('`lock` (Monitor)', 'The default. Mutual exclusion around a multi-step invariant.', 'LRU Get/Put — map and list must change together'),
 ('`Monitor.Wait` / `PulseAll`', 'Wait for a condition inside a lock. Always in a `while` loop.', 'Bounded queue: wait while full / empty'),
 ('`SemaphoreSlim`', 'Count-limited access; has `WaitAsync`, so works across `await`.', 'Limit concurrent calls to a slow dependency; async producer/consumer'),
 ('`ReaderWriterLockSlim`', 'Many readers or one writer. Only wins when reads truly do not write and dominate.', 'NOT an LRU — its reads move nodes. A config map read 1000:1'),
 ('`ConcurrentDictionary`', 'Per-call atomic map operations; `AddOrUpdate`, `GetOrAdd`.', 'Counters, registries. Not enough when an invariant spans two structures'),
 ('`Interlocked`', 'Lock-free single-word read-modify-write.', 'Hit/miss counters read by a metrics scraper'),
 ('`Lazy<T>` (ExecutionAndPublication)', 'Run a factory exactly once even under a race.', '`GetOrAdd(key, _ => new Lazy<…>(…))` to stop a cache stampede'),
 ('`Channel<T>`', 'Production producer/consumer with bounded capacity and async back-pressure.', 'The answer you name before building a queue by hand'),
 ('`CancellationToken`', 'Cooperative cancellation; register a callback to wake blocked waiters.', 'Shutdown of a consumer loop; a blocked producer'),
 ('`Task` / `async`/`await`', 'Do not block threads on I/O. Never `.Result` inside a lock or on a sync context.', 'A read-through cache over a slow service'),
]

CONC_TOPICS = [
 ('Lock granularity', 'One lock for the whole cache is correct and simple. It serialises everything. Striping by key hash (N shards, N locks) cuts contention by roughly N, and '
  'costs global ordering — each shard is exact LRU, the cache is approximately LRU. Finer than that (a lock per node) is where deadlocks and bugs live; say why you are not going there.'),
 ('Reader/writer trade-offs', 'A reader/writer lock helps when reads are frequent, writes rare, and reads genuinely do not mutate. An LRU read mutates (it moves the node), so a '
  'reader/writer lock does not help it. Saying that out loud is a strong signal. Read-mostly alternatives: approximate recency (a "touched" bit, CLOCK), or buffering reads and '
  'applying them in batches (what Caffeine does).'),
 ('Deadlocks and lock ordering', 'Two locks taken in different orders by different threads will eventually deadlock. Fix by a global order (by id), by never calling out while holding '
  'a lock, or by not needing two locks. Debugging exercise D5 reproduces one.'),
 ('Atomic operations', 'Check-then-act across two calls is a race even if each call is atomic — `ContainsKey` then indexer, `TryGetValue` then assignment. The fix is one atomic call '
  '(`AddOrUpdate`) or one lock around both. Debugging exercises D2 and D4.'),
 ('Concurrent collections', 'They make each call atomic. They do not make your *sequence* of calls atomic, and they do not protect a second structure. That is why '
  '`ConcurrentDictionary` + `LinkedList` is not a thread-safe LRU (review exercise R3 corrupted in 20 of 20 trials).'),
 ('Background cleanup', 'A sweeper that scans everything under the lock stalls every reader for the length of the scan. Bound the work per tick (a budget), or piggy-back a few '
  'entries of cleanup on each write. Review exercise R10.'),
 ('Cancellation and shutdown', 'Every blocking call needs a way out: a `CancellationToken` (and a registration that wakes waiters), and a `Complete()` that lets consumers drain and '
  'exit. "How do you shut this down?" is a common production follow-up.'),
 ('Slow dependencies', 'A read-through cache in front of a slow service turns a burst of misses into a burst of identical slow calls (a stampede). Cache the in-flight `Lazy`/`Task`, '
  'not just the value; add a timeout; decide what to serve when the dependency is down. Review exercise R8: eight concurrent first reads made eight calls.'),
]

TESTING = [
 ('Happy path', 'The documented example, and one more you derived by hand.', 'Put two, get one, put a third: the right one is evicted.'),
 ('Boundary cases', 'Capacity one; exactly at the TTL; first and last element; half-open ends.', '`now == expiresAt` must be expired. Test exactly there, not one past.'),
 ('Empty input', 'Empty cache, empty list, empty file, no events in the window.', '`GetRank` on an empty cache; `Merge([])`.'),
 ('Invalid input', 'Capacity 0, negative TTL, inverted interval, malformed JSON.', 'Decide: throw, or return a result type. Then test that decision.'),
 ('Large input', 'Enough to expose complexity, and memory.', '100,000 entries with 10 expired: does the sweep examine 10 or 100,000?'),
 ('Duplicate input', 'Same key twice, same interval twice, same event twice.', 'Re-put must update in place, not grow the count.'),
 ('Concurrent access', 'Many threads, then assert an invariant — never an exact interleaving.', 'Count ≤ capacity; total consumed = total produced; no torn values.'),
]
