# -*- coding: utf-8 -*-
"""Chapter 10, Lesson 2 — the 50-minute mock, run in real time."""
from lib import *

lesson_header('10.2', 'The 50-minute mock, run in real time', 'Mock interview',
              '—', 'Structured like the reported Staff Coding module', '2026', '—', 22,
              """Chapter ten, lesson two — the last lesson. A full fifty-minute mock, run in real time, structured the way """
              """the official pack describes the Staff Coding module: modularity, extensibility, finding and fixing bugs, """
              """rather than an algorithm sprint. I will give you the problem, then stay quiet while you work, then grade """
              """it in detail. Do this once when you are rested, with a real editor open and a timer running. Watching it """
              """without doing it is worth almost nothing.""")

sid = beat('Before we start', 'Set it up like the real thing',
           '<div style="font-size:31px;line-height:1.7">'
           '<b>&bull;</b> A plain editor. No autocomplete beyond syntax, no internet.<br>'
           '<b>&bull;</b> A timer at 50 minutes, visible.<br>'
           '<b>&bull;</b> <b>Talk out loud.</b> Record yourself if you can &mdash; the playback is where the real '
           'feedback is.<br>'
           '<b>&bull;</b> C#, since that is the language you will use.<br><br>'
           'The problem arrives in three parts, the way a real round does: a core, an extension, and a bug. '
           '<b>You will not be told when to move on</b> &mdash; managing the clock is part of what is being graded.</div>',
           """Before we start, set it up like the real thing. A plain editor with no autocomplete beyond syntax and no """
           """internet. A timer at fifty minutes, visible.""", step=0)
seg(sid, 1, """Talk out loud, and record yourself if you can, because the playback is where the real feedback is — most """
            """people are shocked by how much of their thinking never reaches the room.""")
seg(sid, 2, """Use C sharp. The problem comes in three parts, the way a real round does: a core, an extension, and a bug. """
            """And you will not be told when to move on — managing the clock is part of what is being graded.""")

sid = beat('The problem', 'Part 1 of 3 &mdash; the core',
           '<div class="qwrap"><div class="qlabel">The interviewer says</div>'
           '<div class="qtext" style="font-size:31px;line-height:1.45">&ldquo;We run a feature-flag service. Every '
           'request carries a <b>member id</b> and asks: <b>is flag F on for this member?</b><br><br>'
           'A flag has rules, evaluated in order. The first rule that matches wins. A rule is one of:<br>'
           '&bull; <b>member is in this list</b> &rarr; on/off<br>'
           '&bull; <b>member is in this segment</b> (a named set) &rarr; on/off<br>'
           '&bull; <b>percentage rollout</b> &mdash; on for X% of members, <b>stably</b> (the same member always gets '
           'the same answer)<br>'
           '&bull; <b>default</b> &rarr; on/off<br><br>'
           'Design and implement the evaluator. It is called millions of times a minute.&rdquo;</div></div>',
           """Here is part one. We run a feature-flag service. Every request carries a member id and asks whether a given """
           """flag is on for that member. A flag has rules, evaluated in order, and the first rule that matches wins. A """
           """rule is one of four kinds: the member is in an explicit list; the member is in a named segment; a percentage """
           """rollout, which must be stable so that the same member always gets the same answer; or a default. Design and """
           """implement the evaluator. It is called millions of times a minute.""")

think('Part 1. Clarify, design, implement. Aim to be done in about 20 minutes.', 60,
      """Pause the video now and work part one. Aim to be done in about twenty minutes, including your clarifying """
      """questions. Do not skip talking out loud — if you do this silently you are practising the wrong thing. Come back """
      """when you have something working.""",
      """Welcome back. Before the extension, let me tell you what I was watching for in part one.""")

sid = cards('Part 1 &mdash; what I was grading', [
 (0, 'Did you ask about the percentage rollout?', 'It is the only <i>interesting</i> rule. Stable means hash(memberId + flagName) mod 100 &mdash; and salting with the <b>flag name</b> matters, or every 10% flag hits the same unlucky members.', 'ok'),
 (0, 'Is it one class per rule, or one big switch?', 'The pack says <b>modularity and extensibility</b>. An <code>IRule</code> with an <code>Evaluate</code> method is the answer, and adding a fifth rule type should touch no existing code.', 'ok'),
 (1, 'Did you separate evaluation from loading?', 'Rules come from config that changes. Parsing per request is the obvious performance bug; the evaluator should take an already-built rule list.', 'deny'),
 (1, 'What does &ldquo;millions a minute&rdquo; force?', 'No allocation per request, no string concatenation in the hash path if avoidable, and segments as <b>set lookups</b>, not scans. ~17k/s is not extreme &mdash; say that rather than over-engineering.', 'ok'),
 (2, 'Did you handle: unknown flag, empty rules, member not in any rule?', 'Unknown flag should not throw on a hot path &mdash; return a safe default and record a metric. That answer alone is a strong signal.', 'shared'),
 (2, 'Tri-state or boolean?', 'A rule either <b>matches</b> (giving on/off) or <b>does not match</b> (falling through). Modelling that as <code>bool?</code> or a small struct is cleaner than two booleans, and it is the kind of modelling choice they watch for.', 'ok'),
], cols=2)
seg(sid, 0, """First: did you ask about the percentage rollout? It is the only interesting rule. Stable means hashing the """
            """member id together with the flag name and taking it modulo one hundred — and salting with the flag name """
            """specifically matters, because otherwise every ten-percent flag in your system hits exactly the same unlucky """
            """ten percent of members. That is a real production concern and a great thing to raise unprompted.""")
seg(sid, 1, """Second: one class per rule, or one big switch statement? The official pack says this module scores modularity """
            """and extensibility, so an interface with an Evaluate method is the answer, and the test is whether adding a """
            """fifth rule type touches any existing code.""")
seg(sid, 2, """Third: did you separate evaluation from loading? Rules come from configuration that changes, and parsing """
            """config per request is the obvious performance bug. Fourth: what does millions a minute actually force? No """
            """allocation per request, no avoidable string concatenation in the hash path, and segments as set lookups """
            """rather than scans. But do the arithmetic out loud — a million a minute is about seventeen thousand a """
            """second, which is not extreme, and saying so keeps you from over-engineering.""")
seg(sid, 3, """Fifth: the edge cases. Unknown flag, empty rule list, a member matching no rule. And the answer I most want """
            """to hear is that an unknown flag must not throw on a hot path — return a safe default and record a metric. """
            """That single sentence tells an interviewer you have operated a service.""")
seg(sid, 4, """And sixth, a modelling point: a rule either matches, giving an on or off answer, or does not match and falls """
            """through. Representing that as a nullable boolean or a small struct is cleaner than juggling two separate """
            """booleans, and the modelling choice is exactly what they are watching.""")

CODE = '''public interface IRule {
    bool? Evaluate(string memberId);       // null = "does not match, fall through"
}

public sealed class MemberListRule : IRule {
    private readonly HashSet<string> _members; private readonly bool _value;
    public bool? Evaluate(string m) => _members.Contains(m) ? _value : null;
}

public sealed class SegmentRule : IRule {
    private readonly ISegmentIndex _segments; private readonly string _segment; private readonly bool _value;
    public bool? Evaluate(string m) => _segments.Contains(_segment, m) ? _value : null;
}

public sealed class PercentageRule : IRule {
    private readonly string _flag; private readonly int _percent;
    public bool? Evaluate(string m) => StableBucket(m, _flag) < _percent;   // always matches
    private static int StableBucket(string member, string flag) {
        // salt with the flag so different flags pick different members
        uint h = Fnv1a(member, flag);
        return (int)(h % 100);
    }
}

public sealed class DefaultRule : IRule {
    private readonly bool _value;
    public bool? Evaluate(string m) => _value;                              // always matches
}

public sealed class Flag {
    private readonly IReadOnlyList<IRule> _rules;                           // built once, at load time
    public bool IsOn(string memberId) {
        foreach (var rule in _rules) {                                      // first match wins
            var r = rule.Evaluate(memberId);
            if (r.HasValue) return r.Value;
        }
        return false;                                                       // no rule matched: safe default
    }
}'''
code_slide('A solution for part 1', CODE, [
 ('1-3', """The interface, and the whole design is in that comment: null means this rule does not match, so fall through. """
           """One method, one meaning, and every rule type becomes trivial."""),
 ('5-13', """The list and segment rules are three lines each. Note the segment rule depends on an index abstraction rather """
            """than a concrete store — that is the seam you will be glad of when the extension arrives, and it costs """
            """nothing now."""),
 ('15-24', """The percentage rule always matches, which is worth saying out loud, because it means any rule after it is """
             """unreachable and that is a validation rule you could offer. The bucket is salted with the flag name, and a """
             """cheap non-cryptographic hash is right here — this is not a security boundary, and saying that you chose """
             """FNV deliberately rather than SHA is a good detail."""),
 ('26-29', """The default rule also always matches, which makes it the natural terminator."""),
 ('31-40', """And the flag itself is a loop over pre-built rules: first match wins, and a safe default if nothing matched. """
             """Notice there is no parsing, no allocation and no branching on rule type here. Adding a new rule kind means """
             """adding one class and touching nothing in this file, which is exactly the extensibility the module """
             """scores."""),
])

sid = beat('Part 2 of 3', 'The extension',
           '<div class="qwrap"><div class="qlabel">The interviewer says</div>'
           '<div class="qtext" style="font-size:32px;line-height:1.45">&ldquo;Good. Now two changes.<br><br>'
           '<b>1.</b> Segments can be <b>nested</b> &mdash; a segment may include other segments.<br>'
           '<b>2.</b> Product wants to know <b>why</b> a member got their answer: which rule matched, and for a '
           'segment, the path through the nesting.&rdquo;</div></div>',
           """Part two, the extension. Two changes. First, segments can be nested: a segment may include other segments. """
           """Second, product wants to know why a member got their answer — which rule matched, and for a segment, the """
           """path through the nesting.""")
think('Part 2. About 15 minutes. What do those two requirements do to your design?', 50,
      """Pause again, about fifteen minutes. And think about the two requirements separately, because one of them is a """
      """graph problem you have already solved in this course, and the other is a design problem about return types.""",
      """Right. Here is what part two was testing.""")

sid = cards('Part 2 &mdash; what I was grading', [
 (0, 'Nested segments are a graph', 'Membership becomes reachability &mdash; a DFS or BFS over the segment graph. Chapter 3, in disguise.', 'ok'),
 (0, 'Did you ask about cycles?', 'A segment graph <b>can</b> contain a cycle if someone misconfigures it. Detect at load time and reject, rather than looping forever on a hot path. This is the single best thing you could say in part 2.', 'deny'),
 (1, 'Where does the cost go?', 'Traversing per request is wasteful. Flatten at load time into a set per segment, or cache per (segment, member). Say which and why &mdash; flattening costs memory, caching costs invalidation.', 'ok'),
 (1, 'The &ldquo;why&rdquo; requirement changes the return type', 'Not a bool any more &mdash; an <code>Evaluation</code> carrying the value, the matching rule and the path. Changing the return type of every rule is the <b>right</b> move; hacking it into an out-parameter is not.', 'ok'),
 (2, 'Did you keep the hot path clean?', 'Explaining is not needed on every request. An <code>IsOn</code> fast path plus an <code>Explain</code> method &mdash; or a flag on the call &mdash; keeps the millions-a-minute case allocation-free.', 'ok'),
 (2, 'Extensibility, tested', 'If part 1 was an interface per rule, part 2 is small. If it was a switch statement, part 2 is a rewrite. That contrast <b>is</b> the grading.', 'shared'),
], cols=2)
seg(sid, 0, """Nested segments are a graph, and membership becomes reachability — a depth-first or breadth-first walk over """
            """the segment graph. That is chapter three in disguise, and recognising it quickly is the first mark.""")
seg(sid, 1, """Then the question I most wanted to hear: did you ask about cycles? A segment graph can absolutely contain a """
            """cycle if somebody misconfigures it, and the right answer is to detect that at load time and reject the """
            """configuration, rather than discovering it by looping forever on a hot path serving millions of requests. """
            """That is the single best sentence available in part two.""")
seg(sid, 2, """Where does the cost go? Traversing on every request is wasteful. You either flatten each segment into a """
            """concrete member set at load time, or cache per segment and member — and the good answer names the cost of """
            """each: flattening costs memory, caching costs invalidation.""")
seg(sid, 3, """The why requirement changes your return type. It is no longer a boolean, it is an evaluation object """
            """carrying the value, the rule that matched, and the path. Changing the return type across the rule interface """
            """is the right move; bolting it on with an out parameter is the move that tells an interviewer you are """
            """avoiding a refactor.""")
seg(sid, 4, """Did you keep the hot path clean? Explanation is not needed on every request, so an IsOn fast path alongside """
            """an Explain method keeps the common case allocation-free.""")
seg(sid, 5, """And the meta-point: if part one gave you an interface per rule, part two is a small change. If part one was a """
            """switch statement, part two is a rewrite. That contrast is the grading. This is what the official pack means """
            """when it says the module scores extensibility.""")

sid = beat('Part 3 of 3', 'The bug',
           '<div class="qwrap"><div class="qlabel">The interviewer says</div>'
           '<div class="qtext" style="font-size:31px;line-height:1.45">&ldquo;We shipped this. Support reports that '
           'a <b>small number of members see the flag flip back and forth</b> between requests &mdash; on, then off, '
           'then on &mdash; even though nobody changed the config.<br><br>'
           'The percentage rollout is supposed to be stable. Find the bug.&rdquo;</div></div>',
           """Part three, and this is the part the pack explicitly names: finding and fixing bugs. We shipped this, and """
           """support reports that a small number of members see the flag flip back and forth between requests — on, then """
           """off, then on — even though nobody changed the configuration. The percentage rollout is supposed to be """
           """stable. Find the bug.""")
think('Part 3. Ten minutes. Do not guess — form hypotheses and say how you would test each one.', 45,
      """Pause, ten minutes. And here is the instruction that is really being tested: do not guess. Form hypotheses and """
      """say how you would distinguish them, the same way you would on a real incident.""",
      """Here is the answer, and more importantly the method.""")

sid = cards('Part 3 &mdash; the method, then the bug', [
 (0, 'Method first: what is stable, what is not?', 'The answer depends on member id, flag name, the rule list, and the hash. Config is unchanged, so suspect the <b>hash</b> or the <b>inputs to it</b>.', 'ok'),
 (0, '&ldquo;A small number of members&rdquo; is the clue', 'Not everyone &mdash; so it is not the algorithm. It is something that varies <i>between requests</i> for <i>some</i> ids. That points at the boundary, or at the id itself.', 'ok'),
 (1, 'Bug 1 &mdash; a non-deterministic hash', 'In .NET, <code>string.GetHashCode()</code> is <b>randomised per process</b>. Two servers bucket the same member differently, so a load-balanced member flips as they hit different hosts. This is the intended bug.', 'deny'),
 (1, 'The fix', 'A defined, stable hash &mdash; FNV-1a, xxHash, or MD5 truncated. Never a runtime hash whose contract does not promise stability across processes.', 'ok'),
 (2, 'Bug 2 &mdash; the id is not canonical', 'If ids arrive with different casing or whitespace from different call sites, the same member hashes two ways. Normalise at the boundary.', 'shared'),
 (2, 'What I hoped you would add', '&ldquo;I would write a test that hashes the same id in two processes and asserts equality &mdash; this class of bug cannot be caught in a single-process unit test.&rdquo;', 'ok'),
], cols=2)
seg(sid, 0, """Method first. What is stable and what is not? The answer depends on the member id, the flag name, the rule """
            """list and the hash function. Configuration is unchanged by assumption, so suspect the hash or the inputs to """
            """it.""")
seg(sid, 1, """And the phrase "a small number of members" is the clue. If it were everyone, the algorithm would be wrong. A """
            """small number means something varies between requests for some ids — which points either at the percentage """
            """boundary, or at the id itself.""")
seg(sid, 2, """Here is the intended bug. In dot NET, the default string hash code is randomised per process. Two servers """
            """therefore bucket the same member differently, and a member whose requests are load-balanced across hosts """
            """flips between on and off. It is a genuinely nasty bug: it passes every unit test, because within one """
            """process the hash is perfectly consistent.""")
seg(sid, 3, """The fix is a hash with a defined, stable contract — FNV-1a, xxHash, or a truncated MD5 — and never a runtime """
            """hash whose documentation does not promise stability across processes.""")
seg(sid, 4, """There is a second plausible bug worth mentioning: if member ids arrive with different casing or stray """
            """whitespace from different call sites, the same member hashes two different ways. Normalise at the """
            """boundary.""")
seg(sid, 5, """And the sentence I was hoping for at the end: I would write a test that hashes the same id in two separate """
            """processes and asserts they agree — because this entire class of bug is invisible to a single-process unit """
            """test. Naming the test that would have caught it is the strongest possible finish to a debugging """
            """question.""")

sid = table('The 50 minutes, scored',
 ['Band', 'What it looks like'],
 [(0, ['<b>Below the bar</b>', 'Part 1 only, as one switch statement. No clarifying questions. Silent stretches. Percentage rule not salted with the flag name'], None),
  (1, ['<b>Senior</b>', 'Parts 1 and 2 working. Rules as an interface. Asked about cycles when prompted. Found the hash bug with a hint'], None),
  (2, ['<b>Staff</b>', 'All three parts. Asked about the rollout salt <i>unprompted</i>. Rejected cyclic config <b>at load time</b>. Kept the hot path allocation-free while adding explanations. Found the bug by hypothesis rather than by guessing, and named the cross-process test'], None),
  (3, ['<b>The extra sentence</b>', '&ldquo;Config changes need a safe rollout too &mdash; I would version the rule set, evaluate both for a sample, and compare, before switching over.&rdquo;'], None)],
 widths=[20, 80])
seg(sid, 0, """Scoring, honestly. Below the bar: part one only, written as one switch statement, with no clarifying questions, """
            """silent stretches, and a percentage rule that is not salted with the flag name.""")
seg(sid, 1, """Senior: parts one and two working, rules behind an interface, asked about cycles when prompted, and found the """
            """hash bug after a hint.""")
seg(sid, 2, """Staff: all three parts. Asked about the rollout salt unprompted. Rejected cyclic configuration at load time """
            """rather than defending against it per request. Kept the hot path allocation-free while adding explanations. """
            """And found the bug by forming hypotheses rather than guessing, then named the cross-process test that would """
            """catch it.""")
seg(sid, 3, """And the extra sentence, if you had time: configuration changes need a safe rollout too — I would version the """
            """rule set, evaluate both versions for a sample of traffic, and compare before switching over. That is a """
            """sentence about shipping rather than about code, and it is the one that makes an interviewer write "staff" """
            """in their notes.""")

sid = beat('What to do with the recording', 'The part most people skip',
           '<div style="font-size:31px;line-height:1.7">'
           'Play it back and count four things:<br><br>'
           '<b>1.</b> Your longest silence. Anything over ~20 seconds is a habit to fix.<br>'
           '<b>2.</b> How long until <b>something worked</b>. Should be under ten minutes.<br>'
           '<b>3.</b> How many questions <b>you</b> asked. Under three is too few.<br>'
           '<b>4.</b> Whether you ever said what you would <b>ship</b>, not just what passes.<br><br>'
           '<i>Those four numbers improve faster than your algorithm knowledge, and they move the level more.</i></div>',
           """And the part most people skip: what to do with the recording. Play it back and count four things.""",
           step=0)
seg(sid, 1, """One, your longest silence — anything over about twenty seconds is a habit worth fixing. Two, how long until """
            """something worked; that should be under ten minutes. Three, how many questions you asked, where fewer than """
            """three is too few. And four, whether you ever said what you would ship rather than only what passes.""")
seg(sid, 2, """Those four numbers improve much faster than your algorithm knowledge does, and they move the level more. """
            """That is the honest summary of this entire course.""")

sid = statement('The end of the course', 'Patterns get you a correct answer. Behaviour gets you the level.',
                'Ten chapters, thirty-four lessons, every reported question covered. Go and be the candidate who talks while they think.',
                kind='ok')
seg(sid, 0, """That is the end of the course. One line to leave you with: patterns get you a correct answer, and behaviour """
            """gets you the level.""")
seg(sid, 1, """Ten chapters, thirty-four lessons, and every question in the research database covered. You have the """
            """templates, you have the eight sentences, and you have the reported questions ranked by evidence. Go and be """
            """the candidate who talks while they think. Good luck.""")
