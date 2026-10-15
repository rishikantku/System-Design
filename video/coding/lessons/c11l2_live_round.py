# -*- coding: utf-8 -*-
"""Lesson 11.2 — the AI round, step by step, on a CoderPad screen.

Two reported questions (the logging library, then LRU → TTL → thread-safe), worked the way the round
runs. At every step: a BAD prompt and what it produced, how to review it, the GOOD prompt, its output,
the real test run, and the fix.

Honesty rules, stated on screen once:
  * every console on screen is the real output of compiling and running that exact code
    (live_run.py → live_out.json; the lesson refuses to build if a run does not match EXPECT);
  * every listing on the pad is a slice of the code that was run (live_cs.py);
  * the assistant replies are written to show the mistakes assistants typically make. They are not
    a transcript of one particular model.
"""
import io, json, os, sys
from lib import *
import engine as E
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_cs as L

OUT = json.load(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live_out.json'), encoding='utf-8'))
for rid, want in L.EXPECT.items():
    assert OUT[rid]['verdict'] == want, 'run %s is %s, lesson needs %s — re-run live_run.py' % (rid, OUT[rid]['verdict'], want)


def con(rid, max_lines=7):
    """Real console text for a run. Long compiler output is cut to its first errors, and says so."""
    lines = OUT[rid]['out'].split('\n')
    if len(lines) > max_lines:
        extra = len(lines) - (max_lines - 1)
        lines = lines[:max_lines - 1] + ['… %d more error%s' % (extra, 's' if extra > 1 else '')]
    return '\n'.join(lines)

def build_errors(rid, n=3):
    lines = OUT[rid]['out'].split('\n')
    short = [l.replace(' (are you missing a using directive or an assembly reference?)', '') for l in lines[:n]]
    if len(lines) > n: short.append('… %d more errors' % (len(lines) - n))
    return '\n'.join(short)

def part(code, first, last=None):
    """The lines of `code` from the first line containing `first` to the next containing `last`."""
    ls = code.strip('\n').split('\n')
    a = next(i for i, l in enumerate(ls) if first in l)
    b = a if last is None else next(i for i in range(a, len(ls)) if last in ls[i])
    import textwrap
    return textwrap.dedent('\n'.join(ls[a:b + 1]))   # a method slice keeps no class indent

def P(text):   return '<div class="pt">%s</div>' % esc(text)
def X(text):   return rich(text)
def UL(*its):  return '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(i) for i in its)

LOG_TABS = ['Logger.cs', 'Models.cs', 'Tests.cs']


lesson_header('11.2', 'The AI round, step by step — prompts, reviews and real test runs',
              'Logging library · LRU → TTL → thread-safe', 'Highest',
              'Logging library: 5 reports (Aug–Sep 2026) · LRU: AI-round reports', 'Sep 2026', 'High', 27,
              """Lesson eleven point two. The last lesson explained the round. This one does the round. Two questions that """
              """candidates reported for LinkedIn's A I round: the logging library, and the L R U cache that grows a time to live """
              """and then has to be thread-safe. We work them on a screen laid out like CoderPad: your code on the left, the A I """
              """assistant on the right, the console underneath. At every step you will see a bad prompt and what it gives back, """
              """how to review it, then a good prompt, its output, and the real test run. Every console on screen is the real """
              """output of running that exact code. The assistant's replies are written to show the mistakes assistants """
              """typically make, so you learn to catch them.""")

# ================================================================================ chapter 1: the method
E.chapter(1, 'The method', 'One loop, run for every requirement',
          """Chapter one. The method. It is one short loop, and you run it again every time the interviewer adds a """
          """requirement. Learn the loop here, then watch it run fourteen times.""")

sid = steps_list('The loop — run it for every new requirement', [
    (0, '**Restate and ask** — what is "identical"? what happens at the boundary? · no AI', 'info'),
    (1, '**Write the shape yourself** — fields, signatures, one comment per rule · no AI', 'info'),
    (2, '**Write two or three tests yourself** — the cases that prove the rule · no AI', 'info'),
    (3, '**Prompt narrowly** — paste your class, state the rules, ask for assumptions first', 'cp'),
    (4, '**Review before you run** — assumptions, the rule\'s line, the lock, what grows', 'shared'),
    (5, '**Run your tests** — read every FAIL: is the code wrong, or the test?', 'deny'),
    (6, '**Fix and say it** — ≤ 2 lines: by hand · more: one narrow follow-up prompt', 'ok'),
])
for i, t in enumerate([
    """Step one. Restate the question and ask what changes the code. What makes two logs identical? What happens """
    """exactly at the boundary? No A I yet.""",
    """Step two. Write the shape yourself: the fields, the method signatures, and a comment for each rule. This is your """
    """design, and it is what the interviewer is scoring. Still no A I.""",
    """Step three. Write two or three tests yourself. The cases that prove the rule. They take one minute, and they are """
    """what will catch the assistant's mistakes.""",
    """Step four. Now prompt. Narrowly. Paste your class, state the rules, and ask for the assumptions before the code.""",
    """Step five. Review before you run. Read its assumptions. Find the one line that holds the rule. Check what runs """
    """under a lock, and what can grow without limit.""",
    """Step six. Run your tests, and read every failure. Ask one question: is the code wrong, or is the test wrong? """
    """Both happen.""",
    """Step seven. Fix it, and say it out loud. One or two lines, fix it by hand: it is faster, and it shows you understood. """
    """More than that, send one narrow follow-up prompt."""]):
    seg(sid, i, t)

sid = table('What makes a prompt good', ['Bad prompt', 'Good prompt', 'Why it matters'], [
    (0, ['"Write a logger"', '"Implement **Log** in **this** class" + the class pasted', 'It cannot invent its own design']),
    (1, ['No rules', 'Every rule, in one sentence each', 'It cannot guess the rule wrong silently']),
    (2, ['Any shape', '"Keep my fields. No new public members."', 'Your API and your tests still fit']),
    (3, ['Code only', '"List your assumptions before the code"', 'You catch a wrong idea before reading code']),
    (4, ['"Write tests"', '"Plain asserts, my clock, why each value is right"', 'Tests run in the pad, and you can check them']),
], kicker='The method')
for i, t in enumerate([
    """What makes a prompt good. Five differences. A bad prompt says write a logger. A good one says implement Log in this """
    """class, with the class pasted in. Now the assistant cannot invent its own design.""",
    """A bad prompt has no rules. A good one states every rule in one sentence. Otherwise the assistant guesses, and a """
    """wrong guess looks exactly like a right one.""",
    """A good prompt says keep my fields, add no public members. So your interface, and your tests, still fit what comes """
    """back.""",
    """A good prompt asks for the assumptions before the code. A wrong assumption is one sentence to read. The same """
    """mistake in code is twenty lines.""",
    """And for tests: plain asserts, my injected clock, and a comment saying why each expected value is right. That last """
    """part is how you catch a wrong test."""]):
    seg(sid, i, t)

sid = cards('Reviewing a reply in sixty seconds — in this order', [
    (0, '1 · Its assumptions', 'Does any assumption contradict the question? That is the bug, found before reading code.', 'cp'),
    (1, '2 · Did it keep my shape?', 'Same class, same signatures, my injected clock — not DateTime.Now, not a new static class.', 'info'),
    (2, '3 · The line that holds the rule', 'The boundary (< or <=), the eviction, the timestamp. Find it and read it slowly.', 'shared'),
    (3, '4 · The lock', 'What is inside it? A sink write, a network call, a sleep inside a lock is a bug even when tests pass.', 'deny'),
    (4, '5 · What grows', 'A map, a queue, a task per call. Anything with no limit is a production incident later.', 'ok'),
], cols=1, kicker='The method')
for i, t in enumerate([
    """How to review any reply, in sixty seconds, in this order. One. Read its assumptions. If one contradicts the """
    """question, you have found the bug without reading any code.""",
    """Two. Did it keep your shape? Same class, same signatures, your injected clock. Not date time now. Not a brand new """
    """static class.""",
    """Three. Find the one line that holds the rule, and read it slowly. Less than, or less than or equal. Which node gets """
    """evicted. Which timestamp is printed.""",
    """Four. The lock. What is inside it? Writing to a sink, a network call, a sleep inside a lock is a bug, even when every """
    """test passes.""",
    """Five. What grows. A map, a queue, a task per call. Anything without a limit becomes a production incident."""]):
    seg(sid, i, t)

sid = compare('Fix it by hand, or prompt again?',
    ('Fix by hand', 'ok', 0, ['One or two lines, and you know the fix', 'Faster than writing a prompt',
                             'Shows you understood the defect', 'Say: "One character — I\'ll fix it myself"']),
    ('Prompt again — narrowly', 'cp', 1, ['The change touches several lines', 'Name the defect and the rule it breaks',
                                          '"Change only X. Show the diff."', 'Never: "It\'s wrong, fix it"']))
seg(sid, 0, """When a test fails, fix it by hand if it is one or two lines and you know the fix. It is faster than writing a """
            """prompt, and it shows the interviewer you understood the defect.""")
seg(sid, 1, """If the change touches several lines, prompt again. But narrowly: name the defect, name the rule it breaks, and """
            """say change only this, show me the diff. Never send it's wrong, fix it. That gives the assistant nothing to work """
            """with, and gives the interviewer nothing to score.""")

# ================================================================================ chapter 2: logging library
E.chapter(2, 'Round 1 — the logging library', 'Five requirements · five prompts · every run real',
          """Chapter two. The logging library, the freshest reported question: five reports in August and September twenty """
          """twenty-six, one at Staff. It arrives in phases. Severity filtering. Throttling identical logs. A summary of what """
          """was suppressed. Then threads, and then production. We run the loop for each one.""")

sid = cards('The question, and what you ask first', [
    (0, 'The question', 'Build a logging library. Filter by severity. Then: throttle identical logs inside a time window. '
                        'Then: when the window ends, print a summary of what was suppressed.', 'info'),
    (1, 'You ask', '"What makes two logs identical?" → same severity, function, line and message.', 'shared'),
    (2, 'You ask', '"Is a log exactly at the minimum severity written?" → yes, only **below** is dropped.', 'shared'),
    (3, 'You ask', '"Can I inject the clock, so tests control time?" → yes.', 'shared'),
], cols=1, kicker='Minutes 0–4 · no AI')
for i, t in enumerate([
    """Here is the question as reported. Build a logging library. Filter by severity. Then throttle identical logs inside a """
    """time window. Then, when the window ends, print a summary of what was suppressed.""",
    """Before any A I, you ask three things. What makes two logs identical? The reported answer: same severity, function, """
    """line and message.""",
    """Is a log at exactly the minimum severity written? Yes. Only logs below it are dropped. Remember this one.""",
    """And can I inject the clock, so my tests control time instead of sleeping? Yes. Three questions, under two minutes, """
    """and every answer changes the code."""]):
    seg(sid, i, t)

# ---- step 1: severity filter -----------------------------------------------------------------------------
pad('Write the shape yourself', 'Logger.cs', L.LOGGER1 % L.P1_SKEL, tabs=LOG_TABS, clock='min 4', phase='Phase 1 · severity',
    kicker='Steps 2–3 · no AI',
    hl=[(1, ['Writes "{now}', 'A sink that throws'])],
    chat=[(0, 'rev', 'You, out loud', X('"The logger takes a minimum severity, an **injected clock**, and a list of sinks. '
                                         'I\'ll write the class shape myself, then ask the assistant for the body."'))],
    narr=[(0, """Minute four. No A I yet. You write the class shape yourself: a minimum severity, an injected clock, and an """
              """array of sinks. The provided Models file already has the clock, the severity enum and a list sink for tests."""),
          (1, """Then one comment for each rule: the exact output format, and that a failing sink must not stop the others. """
              """These two comments become your prompt in a minute. You are writing the specification, not the code.""")])

pad('Your three tests, before any AI', 'Tests.cs', L.HAND1.replace('T.Section("my cases: severity");\n', ''),
    tabs=LOG_TABS, clock='min 6', phase='Phase 1 · severity', kicker='Step 3 · no AI',
    hl=[(0, ['Severity.Debug', 'below the minimum']), (1, ['"format"']), (2, ['at the minimum', 'minimum itself'])],
    console=(3, con('L0')),
    chat=[(3, 'rev', 'Why run it now', X('It fails with **NotImplementedException**. Good: the harness is wired, and '
                                         'the tests will run the moment code exists.'))],
    narr=[(0, """Now three tests, written by you. A debug log is below the minimum, so nothing is written."""),
          (1, """A warning at time forty-two must print exactly this line. That pins the format."""),
          (2, """And the one people skip: a log at exactly the minimum must be written. That is the boundary you asked about. """
              """It will matter in two minutes."""),
          (3, """Run it once now. It fails with not implemented, which is what you want: the harness is wired up, and the """
              """tests will run the moment there is code.""")])

pad('Bad prompt → a different library', 'Logger.cs', L.P1_BAD, tabs=LOG_TABS, clock='min 7', phase='Phase 1 · severity',
    kicker='Step 4 · bad prompt', ai=True,
    hl=[(2, ['public static class Logger']), (3, ['DateTime.Now']), (4, ['Console.WriteLine'])],
    console=(5, build_errors('L1b')),
    chat=[(0, 'bad', 'Bad prompt', P('Write a logger in C# with severity filtering.')),
          (1, 'ai', 'Assistant', X('Here\'s a simple, flexible static logger with six levels, timestamps and helper '
                                   'methods. Call `Logger.Info("...")` from anywhere.')),
          (2, 'rev', 'Your review', UL('A **new static class** — not my Logger, not my sinks',
                                       '**DateTime.Now** — my clock is ignored, so time cannot be tested',
                                       '**Console.WriteLine** — the sinks are gone'))],
    narr=[(0, """Here is the prompt most people type first. Write a logger in C sharp with severity filtering."""),
          (1, """And the assistant does exactly that. A tidy static logger, six levels, timestamps, helper methods. It looks """
              """professional."""),
          (2, """Review it. First question: did it keep my shape? No. It is a new static class with its own enum. Your """
              """class, your constructor and your sinks are gone."""),
          (3, """It reads date time now, so your injected clock does nothing, and no test can control time."""),
          (4, """And it writes to the console, so there are no sinks to test against."""),
          (5, """Run your tests, and they do not even compile. Cannot create an instance of a static class. The prompt asked """
              """for a logger, so it got a logger. Just not yours.""")])

prompt_compare('The same step, prompted properly',
    'Write a logger in C# with severity filtering.',
    ['No class pasted: it invents its own design', 'No rules: format, sinks and boundary all guessed',
     'No assumptions asked: you find out by reading code'],
    'C#. Implement Log in the Logger class below. Drop any log below _min. Write "{now} {sev} {func}:{line} {msg}" '
    '(now = _clock.NowMs) to every sink. A sink that throws must not stop the others. Keep my fields and signatures; '
    'add no public members. List your assumptions before the code.\n<Logger.cs pasted>',
    ['Scope: **one method**, in **your** class', 'Every rule stated once', 'Shape frozen: your tests still compile',
     '**Assumptions first** — the cheapest place to catch a mistake'],
    narr=[(0, """Side by side. The bad prompt pasted no class, so the assistant invented one. It stated no rules, so the """
              """format, the sinks and the boundary were all guessed. And it asked for no assumptions, so the only way to """
              """find a mistake is reading code."""),
          (1, """The good prompt. Implement one method, in your class, pasted underneath. Every rule in one sentence. Keep my """
              """fields, add no public members, so your tests still compile. And list your assumptions before the code. """
              """Watch what that last line buys you.""")])

pad('Good prompt → read the assumptions first', 'Logger.cs', part(L.LOGGER1 % L.P1_AI, 'public void Log', 'catch (Exception)'),
    tabs=LOG_TABS, clock='min 8', phase='Phase 1 · severity', kicker='Steps 4–6 · good prompt', ai=True,
    hl=[(2, ['if (sev <= _min)']), (3, ['catch (Exception)'])],
    console=(4, con('L1')),
    chat=[(0, 'good', 'Good prompt', P('Implement Log in the Logger class below. Drop any log below _min. Write '
                                       '"{now} {sev} {func}:{line} {msg}" to every sink. A throwing sink must not stop the '
                                       'others. Keep my fields; no new public members. Assumptions first.')),
          (1, 'ai', 'Assistant', X('**Assumptions:** 1) Debug < Info < Warn < Error. 2) "Below the minimum" is filtered, '
                                   'so a log **at exactly _min is dropped too**. 3) Sink exceptions are swallowed.')),
          (2, 'rev', 'Your review', X('Assumption 2 contradicts what the interviewer told me. The code will have `<=`. '
                                      'Found before reading a line.'))],
    narr=[(0, """Minute eight. The good prompt, with the class pasted underneath."""),
          (1, """The reply starts with three assumptions. Read them before the code. Number two: below the minimum is """
              """filtered, so a log at exactly the minimum is dropped too."""),
          (2, """That contradicts what the interviewer told you two minutes ago. And there it is in the code: less than or """
              """equal. You found the bug from one sentence, without reading a line of code. That is why you ask for """
              """assumptions."""),
          (3, """The rest is fine. Each sink is in its own try catch, so a failing sink cannot stop the others."""),
          (4, """Run your tests anyway, so it is proven and not just argued. The minimum itself is written: got one, want two. """
              """Your boundary test caught it, as designed.""")])

pad('One character — fix it by hand', 'Logger.cs', part(L.LOGGER1 % L.P1_FIXED, 'public void Log', 'catch (Exception)'),
    tabs=LOG_TABS, clock='min 9', phase='Phase 1 · severity', kicker='Step 7 · fix and say it', ai=True,
    hl=[(0, ['if (sev < _min)'])],
    console=(1, con('L1f')),
    chat=[(0, 'fix', 'You, out loud', X('"The assistant read **below** as **at or below**. It\'s one character, so I\'ll fix it '
                                         'myself rather than prompt."'))],
    narr=[(0, """One character. Do not write a prompt for one character. Fix it by hand, and say what happened: the assistant """
              """read below as at or below, so I changed it myself."""),
          (1, """Run. Three passed, none failed. Phase one, done in five minutes, and the interviewer has heard you design, """
              """test, catch a defect and fix it.""")])

# ---- step 2: throttle + summary -------------------------------------------------------------------------
pad('New requirement: extend the shape yourself', 'Logger.cs',
    part(L.LOGGER2 % L.P2_AI, '// "Identical"', 'private readonly object _gate'),
    tabs=LOG_TABS, clock='min 11', phase='Phase 2–3 · throttle', kicker='Steps 1–2 · no AI',
    hl=[(1, ['record struct LogKey']), (2, ['class Window']), (3, ['_windows', '_gate'])],
    chat=[(0, 'iv', 'Interviewer', X('"Now throttle identical logs inside a window. When the window ends and the same log '
                                      'comes again, first print a summary: the **first** time, and how many were suppressed."')),
          (3, 'rev', 'You, out loud', X('"One table of windows behind one lock. **Decide under the lock, write outside it**, '
                                         'so a slow sink never blocks other callers."'))],
    narr=[(0, """Minute eleven. The interviewer adds phases two and three. Throttle identical logs inside a window. When the """
              """window ends and the same log arrives again, first print a summary, stamped with the first time, and how many """
              """were suppressed."""),
          (1, """Again, you write the shape. A key record: severity, function, line and message. That is the definition of """
              """identical you asked for, written as a type."""),
          (2, """A window: when it started, and how many were suppressed."""),
          (3, """A dictionary from key to window, and one lock object that guards only that dictionary. Then say the design """
              """rule out loud: decide under the lock, write outside it, so a slow sink never blocks the other callers.""")])

pad('Your throttle tests', 'Tests.cs', L.HAND2.replace('T.Section("my cases: throttle");\n', ''),
    tabs=LOG_TABS, clock='min 13', phase='Phase 2–3 · throttle', kicker='Step 3 · no AI',
    hl=[(0, ['t=0', 'suppressed']), (1, ['only the first prints']), (2, ['FIRST time'])],
    narr=[(0, """Your tests. A manual clock and a window of one thousand milliseconds. Log at zero, at ten and at twenty."""),
          (1, """Inside the window only the first one prints."""),
          (2, """Then at fifteen hundred, after the window, the summary comes first and carries the first time, zero, with """
              """two suppressed. Then the new line. You wrote the exact expected strings, because that is the rule.""")])

pad('Bad prompt → wrong key, wrong clock, half the feature', 'Logger.cs', L.P2_BAD,
    tabs=LOG_TABS, clock='min 14', phase='Phase 2–3 · throttle', kicker='Step 4 · bad prompt', ai=True,
    hl=[(2, ['TryGetValue(msg']), (3, ['DateTime.UtcNow - last']), (4, ['Emit($"'])],
    console=(5, con('L2b')),
    chat=[(0, 'bad', 'Bad prompt', P("Add rate limiting so duplicate logs don't spam.")),
          (1, 'ai', 'Assistant', X('Added duplicate suppression: a message seen in the last second is dropped. Thread-safe '
                                   'with a lock.')),
          (2, 'rev', 'Your review', UL('Keyed by **message only** — a Warn and an Error collide',
                                       '**DateTime.UtcNow** — my clock ignored again', 'Writes to sinks **inside the lock**',
                                       '**No count, no summary** — half the requirement'))],
    narr=[(0, """The bad prompt: add rate limiting so duplicate logs don't spam."""),
          (1, """The reply sounds right. Duplicates in the last second are dropped, and it is thread-safe."""),
          (2, """Review it. The key is the message alone. So a warning and an error with the same text are treated as the """
              """same log. That breaks the definition of identical you clarified."""),
          (3, """It reads the real clock again, so your manual clock does nothing."""),
          (4, """It writes to the sinks while holding the lock. And it counts nothing, so there is no summary. Half the """
              """requirement is missing."""),
          (5, """Run. It crashes: index out of range. Your test moved the manual clock to fifteen hundred, but the code was """
              """looking at the real clock, where barely a millisecond had passed. So the log was still suppressed, and the """
              """summary line never existed.""")])

prompt_compare('Throttling, prompted properly',
    "Add rate limiting so duplicate logs don't spam.",
    ['"Duplicate" undefined: it picked the message', '"Rate limiting" is not the requirement: no count, no summary',
     'Nothing about the clock or the lock'],
    'Add throttling to Log using the _windows table and _gate I added. Identical = equal LogKey. Inside windowMs of a '
    'window\'s start: count it, write nothing. After the window: if any were suppressed, first write '
    '"{firstTs} {sev} {func}:{line} {msg} [suppressed N]", then the line, and start a new window. Decide under _gate; '
    'call the sinks outside it. Show only Log.',
    ['Uses **your** table, **your** key, **your** lock', 'States both halves: suppress **and** summarise',
     'Names the timestamp: **firstTs**', 'States the lock rule', '"Show only Log" — a reply short enough to review'],
    narr=[(0, """Side by side. The bad prompt never said what duplicate means, so the assistant picked the message. Rate """
              """limiting is not even the requirement: nothing is counted and nothing is summarised. And there is nothing """
              """about the clock or the lock."""),
          (1, """The good prompt uses your table, your key and your lock. It states both halves of the requirement. It names """
              """the timestamp, the first one. It states the lock rule. And show only Log keeps the reply short enough to """
              """review in a minute.""")])

pad('Good prompt → review, then run', 'Logger.cs', L.P2_AI,
    tabs=LOG_TABS, clock='min 16', phase='Phase 2–3 · throttle', kicker='Steps 4–6 · good prompt', ai=True,
    hl=[(2, ['now < w.Start + _windowMs']), (3, ['lock (_gate)', '...write outside it']), (4, ['summary = $"{now}'])],
    console=(5, con('L2')),
    chat=[(0, 'good', 'Good prompt', P('Add throttling to Log using my _windows and _gate. Identical = equal LogKey. '
                                       'Inside the window: count, write nothing. After it: summary "{firstTs} … '
                                       '[suppressed N]", then the line. Decide under _gate; sinks outside. Show only Log.')),
          (1, 'ai', 'Assistant', X('Updated Log. Lookups and counters happen under `_gate`; sink writes happen after the '
                                   'lock is released. Exactly at start + window counts as a new window.')),
          (4, 'rev', 'Your review', X('Boundary ✓ · lock ✓ · but the summary uses **now**, and I asked for the **first** '
                                      'time. Suspicious — run it.'))],
    narr=[(0, """Minute sixteen. The good prompt."""),
          (1, """The reply even tells you its boundary choice: exactly at the end of the window counts as a new window."""),
          (2, """Review, in order. The rule's line: now less than start plus window. Strictly less than, so exactly at the end """
              """is a new window. That matches what it said."""),
          (3, """The lock. Lookups and counters inside, and both writes after the closing brace. Exactly what you asked."""),
          (4, """The summary line. It uses now. You asked for the first time. That looks wrong. Do not argue about it: run the """
              """test you already wrote."""),
          (5, """Summary carries the first time: got fifteen hundred, want zero. The test settles it in one second. Reading """
              """found the suspect; the test proved it.""")])

pad('A narrow follow-up prompt', 'Logger.cs', part(L.LOGGER2 % L.P2_FIXED, 'if (w.Suppressed > 0)', 'summary = $"'),
    tabs=LOG_TABS, clock='min 18', phase='Phase 2–3 · throttle', kicker='Step 7 · follow-up', ai=True,
    hl=[(1, ['{w.Start}'])],
    console=(2, con('L2f')),
    chat=[(0, 'good', 'Follow-up prompt', P("The summary must use the window's first timestamp, w.Start, not now. "
                                            "Change only that line.")),
          (1, 'ai', 'Assistant', X('Right — fixed. `summary = $"{w.Start} …"`. Nothing else changed.')),
          (0, 'bad', 'Not this', P("That's wrong, fix it.")),
          (2, 'fix', 'You, out loud', X('"Summary now carries the first occurrence. All six pass."'))],
    narr=[(0, """This one you could fix by hand as well. But here is what a good follow-up prompt looks like, because you will """
              """need it when the fix is bigger. Name the defect, name the rule, and say change only that line. Underneath, in """
              """red: that's wrong, fix it. Never send that. It tells the assistant nothing, and the interviewer hears """
              """nothing."""),
          (1, """The reply changes one line, and says nothing else changed. Check that it is true."""),
          (2, """Run. Six passed. Say it in one sentence, and move on.""")])

# ---- step 3: tests from the assistant --------------------------------------------------------------------
pad('Bad prompt → tests that cannot run here', 'LoggerTests.cs', part(L.AITESTS_BAD, 'using Xunit', 'Assert.Equal(3'),
    tabs=['Logger.cs', 'Tests.cs', 'LoggerTests.cs'], clock='min 19', phase='Tests', kicker='Step 4 · bad prompt', ai=True,
    hl=[(2, ['using Xunit']), (3, ['new SystemClock()']), (4, ['Thread.Sleep(1100)'])],
    console=(5, build_errors('L3b')),
    chat=[(0, 'bad', 'Bad prompt', P('Write unit tests for the logger.')),
          (1, 'ai', 'Assistant', X('Here are xUnit tests covering duplicate suppression and the summary.')),
          (2, 'rev', 'Your review', UL('**xUnit** — the pad has no test framework', '**SystemClock** — a type that does not '
                                       'exist here', '**Thread.Sleep(1100)** — slow and flaky', 'Two happy paths, no reasons'))],
    narr=[(0, """Minute nineteen. You want more tests than your own three. The bad prompt: write unit tests for the logger."""),
          (1, """You get xUnit tests. Normal on a real project."""),
          (2, """But the pad has no test framework."""),
          (3, """It invented a system clock type that does not exist in your code."""),
          (4, """And it sleeps for over a second to wait for the window. Slow, and flaky on a busy machine. Only two happy """
              """paths, and no reason given for any expected value."""),
          (5, """It does not compile: the type or namespace Xunit could not be found. Five errors before a single test runs.""")])

prompt_compare('Tests, prompted properly',
    'Write unit tests for the logger.',
    ['Picks a framework you do not have', 'Real time → Thread.Sleep → slow and flaky', 'No edges named → happy paths',
     'No reasons → you cannot check a wrong expected value'],
    'Write tests for the throttling as plain T.Eq calls — no test framework. Use my ManualClock and ListSink; no '
    'Thread.Sleep. Cover: exactly at the window end, a different line number, three identical logs in one window, a '
    'sink that throws. Above each, one comment saying why the expected value is correct.',
    ['Runs in **this** pad, with **your** harness', 'Your clock: instant and deterministic', 'You name the **edges**',
     '**Why each value is right** — so you can check it'],
    narr=[(0, """Side by side. The bad prompt let it pick a framework you do not have. It used real time, so it had to sleep. """
              """It named no edges, so you got happy paths. And no reasons, so a wrong expected value is invisible."""),
          (1, """The good prompt: plain asserts with your harness. Your manual clock, so it is instant and deterministic. You """
              """name the edges. And one comment above each test saying why the expected value is correct. That comment is """
              """how you will catch the next mistake.""")])

# The generated tests minus the section line and the throwing-sink block (which passes).
AIT_SHOWN = L.AITESTS.strip('\n').split('\n', 1)[1].split('\n{\n    var after')[0]
pad('Good prompt → a test fails. Code or test?', 'Tests.cs', AIT_SHOWN,
    tabs=['Logger.cs', 'Tests.cs'], clock='min 21', phase='Tests', kicker='Steps 5–6 · is the test wrong?', ai=True,
    hl=[(1, ['exactly at the window end', 'start + window']), (3, ['all suppressed', '3 identical'])],
    console=(2, con('L3')),
    chat=[(0, 'good', 'Good prompt', P('Tests for the throttling as plain T.Eq calls. My ManualClock and ListSink; no '
                                       'sleep. Cover: the window end, a different line, three identical, a throwing sink. '
                                       'A comment on why each expected value is right.')),
          (3, 'rev', 'Your review', X('Its reason: "all suppressed". But the **first** log opens the window and **prints**. '
                                      'The code is right; **the test is wrong**.'))],
    narr=[(0, """The good prompt. And the tests come back as plain asserts, each with a comment."""),
          (1, """Read one. At exactly start plus window, a new window begins, so the second log prints. That reason is right, """
              """and it matches the code."""),
          (2, """Run. One failure. Three identical inside one window: got one, want zero."""),
          (3, """Now the question that matters. Is the code wrong, or the test? Read the test's own reason: all three are """
              """suppressed, so nothing is written. But the first log opens the window, and it prints. Your own test from """
              """minute thirteen says so. The code is right. The test is wrong. Assistants get expected values wrong more """
              """often than they get code wrong.""")])

pad('Fix the test, and say why', 'Tests.cs', part(L.AITESTS_FIXED, 'var log = new Logger(Severity.Info, new ManualClock(), 1000, sink);', 'T.Eq("3 identical'),
    tabs=['Logger.cs', 'Tests.cs'], clock='min 22', phase='Tests', kicker='Step 7 · fix and say it', ai=True,
    hl=[(0, ['opens the window and prints', 'sink.Lines.Count, 1'])],
    console=(1, con('L3f')),
    chat=[(0, 'fix', 'You, out loud', X('"That expected value is wrong: the first log opens the window and prints. I\'ve '
                                         'changed it to one. The code was right."'))],
    narr=[(0, """Fix the test, not the code, and say why: the first log opens the window and prints, so the count is one. """
              """Interviewers listen for exactly this sentence. It shows you check the checks."""),
          (1, """Run. Ten passed, none failed. Your three, your three throttle cases, and four generated ones you verified.""")])

# ---- step 4: threads -------------------------------------------------------------------------------------
pad('Bad prompt → passes every test, still wrong', 'Logger.cs', L.P4_BAD,
    tabs=LOG_TABS, clock='min 32', phase='Threads', kicker='Step 4 · bad prompt', ai=True,
    hl=[(2, ['lock (_gate)']), (3, ['Emit($"{w.Start}', 'Emit($"{now}'])],
    console=(4, con('L4b')),
    chat=[(0, 'iv', 'Interviewer', X('"Many threads call Log at once. Is it safe?"')),
          (1, 'bad', 'Bad prompt', P('Make the logger thread-safe.')),
          (1, 'ai', 'Assistant', X('Wrapped all of Log in one lock so lines never interleave.')),
          (3, 'rev', 'Your review', X('Every sink write is **inside** the lock. A 5 ms sink makes **every caller queue**. '
                                      'Tests pass — the review is what catches it.'))],
    narr=[(0, """Minute thirty-two. The interviewer: many threads call Log at once. Is it safe?"""),
          (1, """The bad prompt: make the logger thread-safe. The reply wraps the whole method in one lock, so lines never """
              """interleave. That sounds responsible."""),
          (2, """And it is safe. That is what makes it dangerous."""),
          (3, """Look at what is inside the lock: both writes to the sinks. If a sink takes five milliseconds, a disk or a """
              """network call, every other thread waits in line behind it."""),
          (4, """Run. Every test passes. Then the timing: eight threads, twenty-five logs each, a five millisecond sink. Over """
              """eleven hundred milliseconds. The callers were serialised. No test failed. Only the review caught it.""")])

pad('Good prompt → keep the rule, prove it with a stress test', 'Tests.cs',
    part(L.STRESS_LOG, 'const int threads', 'no lost counts'),
    tabs=['Logger.cs', 'Tests.cs'], clock='min 35', phase='Threads', kicker='Steps 4–6 · good prompt', ai=True,
    hl=[(1, ['SignalAndWait']), (2, ['suppressed 79999'])],
    console=(3, con('L4')),
    chat=[(0, 'good', 'Good prompt', P('Log is called from many threads. Check that the _windows lookup and the counters are '
                                       'under _gate and the sinks are outside it. Then write a stress test: 8 threads on a '
                                       'Barrier, each logs the same message 10,000 times; move the clock past the window, '
                                       'log once more, and assert the summary says 79,999 suppressed.')),
          (0, 'ai', 'Assistant', X('Your Log already decides under the lock and writes outside it — no change needed. '
                                   'Here is the stress test.'))],
    narr=[(0, """The good prompt does two things. It states the lock rule and asks the assistant to check your code against """
              """it. And it asks for a stress test with an invariant that a race would break. The reply: your code already """
              """follows the rule, here is the test."""),
          (1, """Eight threads wait on a barrier, so they all start together and really overlap."""),
          (2, """Each logs the same message ten thousand times. Exactly one line prints. Every other call must be counted. So """
              """the summary must say seventy-nine thousand, nine hundred and ninety-nine. If any increment were lost to a """
              """race, this number would be lower."""),
          (3, """Run. Both pass. And the same timing as before: one hundred and forty-one milliseconds instead of eleven """
              """hundred. Same correctness, eight times faster, because the sinks are called outside the lock.""")])

sid = cards('Both passed. Only one is right.', [
    (0, 'Bad output — one big lock', 'Correct. Every test passes. **1,128 ms**: eight callers queue behind one slow sink.', 'deny'),
    (1, 'Good output — decide under, write outside', 'Correct. Every test passes. **141 ms**: callers only wait for a '
                                                     'dictionary lookup.', 'ok'),
    (2, 'What this teaches', 'Tests prove **correctness**. Only the review catches **what runs under the lock**. Say: '
                             '"A slow sink would serialise every caller."', 'shared'),
], cols=1, kicker='Bad output vs good output')
for i, t in enumerate([
    """Put the two side by side. One big lock: correct, every test passes, eleven hundred and twenty-eight milliseconds.""",
    """Decide under the lock, write outside it: correct, every test passes, one hundred and forty-one milliseconds. Both """
    """numbers are real runs.""",
    """Tests prove correctness. Only reading the code catches what runs under a lock. The sentence to say: a slow sink """
    """would serialise every caller."""]):
    seg(sid, i, t)

# ---- step 5: production ----------------------------------------------------------------------------------
pad('Bad prompt → a task per call', 'AsyncLogger.cs', L.ASYNC_BAD,
    tabs=['Logger.cs', 'AsyncLogger.cs', 'Tests.cs'], clock='min 45', phase='Production', kicker='Step 4 · bad prompt', ai=True,
    hl=[(2, ['Task.Run'])],
    console=(3, con('L5b')),
    chat=[(0, 'iv', 'Interviewer', X('"Logging must never block a request. What changes?"')),
          (1, 'bad', 'Bad prompt', P("Make logging async so it doesn't block.")),
          (1, 'ai', 'Assistant', X('Each call now runs on the thread pool, so the caller returns immediately.')),
          (2, 'rev', 'Your review', UL('**No limit** — a burst of a million logs is a million queued tasks',
                                       '**No order** — tasks run in any order', '**No way to flush** at shutdown',
                                       'A failing sink → an exception nobody sees'))],
    narr=[(0, """Minute forty-five. Production. Logging must never block a request."""),
          (1, """The bad prompt: make logging async so it doesn't block. The reply: every call runs on the thread pool, so the """
              """caller returns immediately. True."""),
          (2, """Review. There is no limit: a burst of a million logs is a million queued tasks in memory. There is no order: """
              """tasks run whenever the pool gets to them. There is no way to wait for them at shutdown. And a sink that """
              """throws raises an exception nobody ever sees."""),
          (3, """Run. Written in the order they were logged: false. Your log file is now shuffled. And the test had to sleep """
              """for half a second, because there is nothing to wait on.""")])

prompt_compare('Production, prompted properly',
    "Make logging async so it doesn't block.",
    ['"Async" is a mechanism, not a requirement', 'No bound → unbounded memory', 'Nothing about full, drops, or shutdown'],
    'Write AsyncLogger: Log(string) must never block. Put lines in a bounded Channel<string> of the given capacity; one '
    'background task writes them to the sinks. If the channel is full, drop the line and count it. Expose Metrics '
    '(Accepted, Dropped, Written). DisposeAsync stops accepting and drains.',
    ['**Bounded**: memory has a ceiling', '**One writer**: order is kept', '**Full = drop and count** — an honest signal',
     '**Shutdown drains** what was accepted'],
    narr=[(0, """Side by side. Async is a mechanism, not a requirement. With no bound, memory has no ceiling. And nothing says """
              """what happens when it is full, or at shutdown."""),
          (1, """The good prompt states the requirement: never block. Then the design: a bounded channel, so memory has a """
              """ceiling. One background writer, so order is kept. When full, drop and count, so you have an honest signal. """
              """And shutdown drains what was accepted.""")])

pad('Good prompt → it reads right. Test it anyway.', 'AsyncLogger.cs', part(L.ASYNC_AI, 'public AsyncLogger(int capacity', 'else Interlocked.Increment'),
    tabs=['Logger.cs', 'AsyncLogger.cs', 'Tests.cs'], clock='min 48', phase='Production', kicker='Steps 4–6 · good prompt', ai=True,
    hl=[(1, ['DropWrite']), (2, ['if (_ch.Writer.TryWrite', 'else Interlocked.Increment']), (4, ['DropWrite'])],
    console=(3, con('L5')),
    chat=[(0, 'good', 'Good prompt', P('AsyncLogger: Log(string) never blocks. Bounded Channel<string>; one background '
                                       'writer. Full → drop and count. Metrics (Accepted, Dropped, Written). DisposeAsync '
                                       'drains.')),
          (0, 'ai', 'Assistant', X('Bounded channel with **DropWrite**, so callers never block. Drops are counted when '
                                   '`TryWrite` fails.')),
          (3, 'rev', 'You, reading the numbers', X('Accepted 10,000 + dropped 0, but only **1,024 written**. Drops happened '
                                                    'that `TryWrite` **did not report**.'))],
    narr=[(0, """The good prompt, and a reply that reads well."""),
          (1, """The channel is bounded, with full mode drop write, so callers never block."""),
          (2, """When try write returns false, it counts a drop. This looks right. Most people would ship it. So you write one """
              """check yourself: ten thousand calls into a channel of one thousand and twenty-four, with a slow sink. Three """
              """numbers must add up."""),
          (3, """Run. Accepted ten thousand, dropped zero, written one thousand and twenty-four. That cannot be right. Ten """
              """thousand accepted, but only one thousand and twenty-four written, and zero drops reported. Almost nine """
              """thousand log lines vanished, and the counter that was supposed to tell you says nothing happened."""),
          (4, """The reason: in drop write mode, try write returns true even when it drops the line. So the else branch never """
              """runs. You could not find this by reading. The test found it.""")])

pad('Follow-up prompt: name the defect, name the fix', 'AsyncLogger.cs', part(L.ASYNC_FIXED, 'public AsyncLogger(int capacity', 'else Interlocked.Increment'),
    tabs=['Logger.cs', 'AsyncLogger.cs', 'Tests.cs'], clock='min 51', phase='Production', kicker='Step 7 · follow-up', ai=True,
    hl=[(1, ['FullMode.Wait'])],
    console=(2, con('L5f')),
    chat=[(0, 'good', 'Follow-up prompt', P('Under DropWrite, TryWrite returns true even when it drops the line, so Dropped '
                                            'stays 0. Use FullMode.Wait — TryWrite never waits and returns false when full — '
                                            'and keep counting on false. Change only the options.')),
          (1, 'ai', 'Assistant', X('Changed to `FullMode.Wait`. `Log` still never blocks: it only calls `TryWrite`.')),
          (2, 'fix', 'You, out loud', X('"Drop-write hides drops. With Wait plus TryWrite the counter is honest: 1,024 + '
                                         '8,976 = 10,000."'))],
    narr=[(0, """The follow-up prompt names the defect: under drop write, try write returns true even when it drops. Names the """
              """fix: full mode wait, where try write never waits and returns false when full. And says change only the """
              """options."""),
          (1, """The reply changes one line. Check one more thing: Log still never blocks, because it only ever calls try """
              """write, never the waiting version."""),
          (2, """Run. Accepted one thousand and twenty-four, dropped eight thousand nine hundred and seventy-six, written one """
              """thousand and twenty-four. They add up to ten thousand. All pass. Say it in one sentence: drop write hides """
              """drops, wait plus try write makes the counter honest.""")])

sid = table('Round 1 — every prompt, bad and good', ['Step', 'Bad prompt', 'Good prompt (the key words)'], [
    (0, ['Phase 1', '"Write a logger…"', 'Implement **Log in this class** · rules · keep my fields · **assumptions first**']),
    (1, ['Phase 2–3', '"Add rate limiting…"', 'Use **my table and lock** · identical = LogKey · **firstTs** · sinks outside']),
    (2, ['Tests', '"Write unit tests"', '**Plain T.Eq** · my clock · named edges · **why each value is right**']),
    (3, ['Threads', '"Make it thread-safe"', '**Decide under, write outside** · stress test with an **invariant**']),
    (4, ['Production', '"Make it async"', '**Bounded** channel · one writer · **drop and count** · drain on dispose']),
], kicker='Round 1 · recap')
for i, t in enumerate([
    """Round one, every prompt on one slide. Phase one: implement Log in this class, the rules, keep my fields, assumptions """
    """first.""",
    """Phases two and three: use my table and my lock, identical means the log key, the first timestamp, sinks outside the """
    """lock.""",
    """Tests: plain asserts, my clock, named edges, and why each value is right.""",
    """Threads: decide under the lock, write outside it, and a stress test with an invariant.""",
    """Production: bounded, one writer, drop and count, drain on dispose. In every case, the good prompt is longer by one """
    """or two sentences, and those sentences are your design."""]):
    seg(sid, i, t)

# ================================================================================ chapter 3: LRU
E.chapter(3, 'Round 2 — LRU → TTL → thread-safe', 'Faster now: the same loop, three phases',
          """Chapter three. The L R U cache that grows a time to live and then has to be thread-safe. The best attested """
          """question for the A I round. Same loop, a little faster.""")

pad('Your shape, and your tests', 'LruCache.cs', L.LRU % L.LRU_SKEL,
    tabs=['LruCache.cs', 'Tests.cs'], clock='min 3', phase='Phase 1 · LRU', kicker='Steps 1–3 · no AI',
    hl=[(1, ['A TryGet counts as a use']), (2, ['_map', '_order'])],
    chat=[(0, 'rev', 'You, out loud', X('"A dictionary for lookup and a linked list for recency. The rule people forget: '
                                         '**a read is a use** — it moves the entry to the front."')),
          (2, 'rev', 'Your tests (Tests.cs)', X('Put 1, Put 2, **read 1**, Put 3 → **2** must be evicted, 1 must survive. '
                                                 'An update must not grow the cache.'))],
    narr=[(0, """Minute three. You have restated the question: capacity N, get and put in constant time. You say the design: a """
              """dictionary for lookup, a linked list for recency."""),
          (1, """And you write the rule people forget into the class comment: a try get counts as a use. Reading a key must """
              """move it to the front."""),
          (2, """Your fields: the dictionary of list nodes and the list, most recent first. And your tests: put one, put two, """
              """read one, put three. Two must be evicted, because one was just read. That single test checks the rule.""")])

pad('Bad prompt → the LeetCode answer', 'LruCache.cs', L.LRU_BAD,
    tabs=['LruCache.cs', 'Tests.cs'], clock='min 6', phase='Phase 1 · LRU', kicker='Step 4 · bad prompt', ai=True,
    hl=[(2, ['public class LRUCache', 'public int Get(int key)']), (3, ['return -1'])],
    console=(4, build_errors('R1b')),
    chat=[(0, 'bad', 'Bad prompt', P('Implement an LRU cache in C#.')),
          (1, 'ai', 'Assistant', X('Classic O(1) LRU with a dictionary and a doubly linked list.')),
          (3, 'rev', 'Your review', UL('**int keys only**, not my generic class', '**-1 means missing** — so a stored -1 '
                                       'looks missing', 'Capacity 0 is not rejected'))],
    narr=[(0, """The bad prompt: implement an L R U cache in C sharp."""),
          (1, """You get the textbook answer. And it is correct, as a LeetCode answer."""),
          (2, """But review it. Integer keys only. Not your generic class, not your try get."""),
          (3, """Minus one means missing, so a cached value of minus one looks like a miss. And capacity zero is not rejected."""),
          (4, """Your tests do not compile: L R U cache with two type parameters could not be found. A correct answer to a """
              """different question.""")])

pad('Good prompt → you can see the bug before running', 'LruCache.cs', L.LRU_AI,
    tabs=['LruCache.cs', 'Tests.cs'], clock='min 8', phase='Phase 1 · LRU', kicker='Steps 4–6 · good prompt', ai=True,
    hl=[(1, ['public bool TryGet', 'value = node.Value.Value;']), (2, ['_order.Remove(node); _order.AddFirst(node);'])],
    console=(3, con('R1')),
    chat=[(0, 'good', 'Good prompt', P('Implement TryGet and Put in this LruCache. O(1) each, with my Dictionary and '
                                       'LinkedList node handles. A TryGet counts as a use. When full, evict the least '
                                       'recently used. Keep my fields; no new public members; no thread-safety yet.')),
          (1, 'rev', 'Your review', X('The rule\'s line: **TryGet never moves the node.** A read is not a use here.')),
          (3, 'fix', 'You, out loud', X('"TryGet doesn\'t refresh recency, so the key I just read gets evicted. Two lines — '
                                         'I\'ll add the move myself."'))],
    narr=[(0, """The good prompt: your class, constant time, your data structures, the rule that a get is a use, and no """
              """thread-safety yet, so the reply stays small."""),
          (1, """Review. Go straight to the rule's line. Try get finds the node and returns the value. It never moves the node. """
              """So a read is not a use, despite the prompt saying so."""),
          (2, """Put does move it. So the assistant knew how; it just forgot in the method that matters."""),
          (3, """Run. Two was evicted: false. One survived its read: false. The key you just read was thrown out. Two lines to """
              """fix, so fix it by hand, and say so.""")])

pad('Two lines, by hand', 'LruCache.cs', part(L.LRU % L.LRU_FIXED, 'public bool TryGet', 'return false;'),
    tabs=['LruCache.cs', 'Tests.cs'], clock='min 10', phase='Phase 1 · LRU', kicker='Step 7 · fix and say it', ai=True,
    hl=[(0, ['a read is a use'])],
    console=(1, con('R1f')),
    narr=[(0, """Move the node to the front inside try get, with a comment: a read is a use."""),
          (1, """Run. Three passed. Phase one done by minute ten.""")])

pad('TTL: bad prompt → rejected on reading', 'LruTtlCache.cs', L.TTL_BAD_TIMER,
    tabs=['LruTtlCache.cs', 'Tests.cs'], clock='min 12', phase='Phase 2 · TTL', kicker='Step 4 · bad prompt', ai=True,
    hl=[(2, ['TimeSpan ttl']), (3, ['new Timer']), (4, ['foreach (var kv in _map)', 'DateTime.UtcNow'])],
    console=(5, '(not run — rejected on reading)'),
    chat=[(0, 'iv', 'Interviewer', X('"Now each entry has a time to live. An expired key reads as missing."')),
          (1, 'bad', 'Bad prompt', P('Add expiry to the cache.')),
          (1, 'ai', 'Assistant', X('Added a TTL and a background timer that sweeps expired entries every second.')),
          (2, 'rev', 'Your review', UL('**One TTL for the whole cache** — the question is per entry',
                                       'A **timer thread** changes the map with **no lock**',
                                       '**Removing while iterating** the map throws', '**DateTime.UtcNow** — untestable'))],
    narr=[(0, """Minute twelve. The interviewer: now each entry has a time to live, and an expired key reads as missing."""),
          (1, """The bad prompt: add expiry to the cache. The reply adds a timer that sweeps expired entries every second."""),
          (2, """Review. One time to live for the whole cache, passed to the constructor. The question says each entry has """
              """its own."""),
          (3, """A timer callback runs on another thread, and it changes the dictionary with no lock. You have just made a """
              """single-threaded cache multi-threaded by accident."""),
          (4, """It removes entries while iterating the same dictionary, which throws. And it reads the real clock again."""),
          (5, """You do not need to run this. Four problems, found by reading. Rejecting code without running it is a """
              """perfectly good outcome. Say why in one sentence and prompt again.""")])

pad('Good prompt → the boundary test catches it', 'LruTtlCache.cs', part(L.ttl(L.TTL_METHODS), 'public bool TryGet', 'return true;'),
    tabs=['LruTtlCache.cs', 'Tests.cs'], clock='min 15', phase='Phase 2 · TTL', kicker='Steps 4–6 · good prompt', ai=True,
    hl=[(1, ['_clock.NowMs > node.Value.ExpiresAt'])],
    console=(2, con('R2')),
    chat=[(0, 'good', 'Good prompt', P('Add a TTL to each entry: Put(key, value, ttlMs). Use my injected IClock — no '
                                       'DateTime, no timers. An expired entry reads as a miss and is removed on that read.')),
          (0, 'rev', 'Your test', X('Put with ttl 100. At **99**: alive. At exactly **100**: dead, and removed.')),
          (2, 'fix', 'You, out loud', X('"It treats the expiry instant as still alive. Dead **at** the TTL, so `>=`. One '
                                         'character."'))],
    narr=[(0, """The good prompt: a time to live per entry, your injected clock, no date time and no timers, and an expired """
              """entry is a miss and is removed on that read. Your test: put with a time to live of one hundred. At ninety-nine """
              """it is alive. At exactly one hundred it is dead, and gone."""),
          (1, """The reply. Read the rule's line: now greater than expires at. Strictly greater. So at exactly one hundred, the """
              """entry is still alive."""),
          (2, """Run. Dead exactly at the time to live: false. The dead entry was removed: count one, want zero. The """
              """boundary test exists for exactly this. One character: greater than or equal. Fix it by hand.""")])

pad('Thread-safe: bad prompt → a crash', 'LruTtlCache.cs', part(L.ttl(L.TTL_CONC_METHODS, conc=True), 'private readonly ConcurrentDictionary', 'return true;'),
    tabs=['LruTtlCache.cs', 'Tests.cs'], clock='min 20', phase='Phase 3 · threads', kicker='Step 4 · bad prompt', ai=True,
    hl=[(1, ['ConcurrentDictionary']), (2, ['_order.Remove(node); _order.AddFirst(node);'])],
    console=(3, con('R3b')),
    chat=[(0, 'bad', 'Bad prompt', P('Make it thread-safe.')),
          (0, 'ai', 'Assistant', X('Switched to `ConcurrentDictionary`, which is thread-safe and lock-free.')),
          (2, 'rev', 'Your review', X('The map is safe. **The linked list is not** — and TryGet **writes** to it. Two threads '
                                      'move the same node at once.'))],
    narr=[(0, """Minute twenty. Make it thread-safe. The bad prompt is just those words. The reply swaps in a concurrent """
              """dictionary, which is thread-safe and lock-free."""),
          (1, """The most common wrong answer in this round. The dictionary is now safe."""),
          (2, """But the linked list is not. And try get writes to it: it moves a node to the front. Two threads move the same """
              """node at the same moment, and the list is corrupted."""),
          (3, """Run the stress test: eight threads, twenty thousand operations each. Invalid operation exception: the linked """
              """list node does not belong to the current linked list. And the cache grew past its capacity. A real crash, """
              """from a real run.""")])

pad('Good prompt → one lock, around everything', 'LruTtlCache.cs', part(L.ttl(L.TTL_LOCKED_METHODS, locked=True), 'public bool TryGet', 'if (_map.Count == _capacity)'),
    tabs=['LruTtlCache.cs', 'Tests.cs'], clock='min 23', phase='Phase 3 · threads', kicker='Steps 4–7 · good prompt', ai=True,
    hl=[(1, ['TryGet WRITES']), (2, ['lock (_lock) {'])],
    console=(3, con('R3')),
    chat=[(0, 'good', 'Good prompt', P('Make LruTtlCache thread-safe with one private lock around the whole of TryGet, Put '
                                       'and Count. TryGet also writes — it moves a node — so it needs the lock too. Keep the '
                                       'plain Dictionary; no ConcurrentDictionary.')),
          (3, 'fix', 'You, out loud', X('"One lock, because every operation changes the list. If it becomes a bottleneck, '
                                         'I\'d shard by key — each shard exact LRU, the whole cache approximately LRU."'))],
    narr=[(0, """The good prompt names the mechanism and the reason: one private lock around all of try get, put and count, """
              """because try get also writes. And it rules out the wrong answer by name: no concurrent dictionary."""),
          (1, """The reply even keeps your reason as a comment: try get writes, it moves a node."""),
          (2, """Every public method takes the same lock, for its whole body."""),
          (3, """Run the same stress test. Five passed, none failed. Then say the next step before you are asked: if one lock """
              """becomes the bottleneck, shard by key. Each shard is exact L R U, the whole cache is only approximately L R U, """
              """and that is the trade-off.""")])

sid = table('Round 2 — every prompt, bad and good', ['Step', 'Bad prompt', 'Good prompt (the key words)'], [
    (0, ['LRU', '"Implement an LRU cache"', '**This class** · my Dictionary + LinkedList · **a TryGet is a use** · no threads yet']),
    (1, ['TTL', '"Add expiry"', 'TTL **per entry** · **my IClock** · no DateTime, **no timers** · miss + remove on read']),
    (2, ['Threads', '"Make it thread-safe"', '**One lock, whole operation** · TryGet writes · **no ConcurrentDictionary**']),
], kicker='Round 2 · recap')
for i, t in enumerate([
    """Round two on one slide. The cache: this class, my data structures, a try get is a use, no threads yet.""",
    """The time to live: per entry, my clock, no date time and no timers, a miss and a removal on read.""",
    """Threads: one lock around the whole operation, because try get writes, and no concurrent dictionary."""]):
    seg(sid, i, t)

# ================================================================================ chapter 4: the checklist
E.chapter(4, 'Your checklist for the room', 'The prompts, the review, the sentences',
          """Last chapter. Everything from the two rounds, as a checklist you can follow in the room.""")

sid = table('The good-prompt template', ['Part', 'Write', 'Example'], [
    (0, ['Scope', 'Which method, in which class — paste it', '"Implement Log in the Logger class below"']),
    (1, ['Rules', 'Every rule, one sentence each, edges included', '"Drop any log below _min"']),
    (2, ['Shape', 'What must not change', '"Keep my fields; no new public members"']),
    (3, ['Exclusions', 'The wrong answers, by name', '"No DateTime, no timers, no ConcurrentDictionary"']),
    (4, ['Check', 'Assumptions first, or reasons per test', '"List your assumptions before the code"']),
    (5, ['Size', 'Keep the reply reviewable', '"Show only Log" · "Change only that line"']),
], kicker='Checklist')
for i, t in enumerate([
    """The good prompt has six parts. Scope: which method, in which class, with the class pasted.""",
    """Rules: every rule in one sentence, including the edge.""",
    """Shape: what must not change. Keep my fields, no new public members.""",
    """Exclusions: name the wrong answers you expect. No date time, no timers, no concurrent dictionary.""",
    """Check: ask for assumptions first, or a reason for each expected value.""",
    """And size: keep the reply small enough to review. Show only this method. Change only that line."""]):
    seg(sid, i, t)

sid = cards('What every bad output had in common', [
    (0, 'It answered a different question', 'A static logger. A LeetCode LRU. Correct code — not your class.', 'deny'),
    (1, 'It ignored your clock', 'DateTime.Now three times. Untestable — and your tests crashed.', 'deny'),
    (2, 'It hid work under a lock — or took the lock away', 'Sinks inside the lock (slow). A concurrent map with a bare list (crash).', 'deny'),
    (3, 'It got one boundary wrong', '<= vs <. > vs >=. now vs w.Start. DropWrite\'s silent true. Your **boundary tests** caught every one.', 'shared'),
], cols=1, kicker='Bad output vs good output')
for i, t in enumerate([
    """What every bad output had in common. It answered a different question: a static logger, a LeetCode cache. Correct """
    """code, not your class. Good prompts fixed this.""",
    """It ignored your clock. Date time now, three times. Good prompts fixed this too, by naming the clock.""",
    """It hid slow work under a lock, or took the lock away. Good prompts fixed this by stating the lock rule.""",
    """And even good prompts got one boundary wrong: less than or equal, greater than, the wrong timestamp, drop write's """
    """silent true. Your own boundary tests caught every one. That is why you write them before you prompt."""]):
    seg(sid, i, t)

interview_script([
    'Before prompting: "I\'ll write the shape first — a table of windows behind one lock."',
    'Prompting: "I\'m giving it my class and the rules, and asking for assumptions first."',
    'Reviewing: "Assumption two contradicts the spec — that\'s the bug."',
    'A failing test: "The code is right; the expected value is wrong. The first log prints."',
    'Fixing: "One character — I\'ll fix it myself."',
    'Threads: "Decide under the lock, write outside it. A slow sink would serialise every caller."',
], ["""And what to say out loud. Before prompting, say the shape. While prompting, say what you gave it and what you asked """
    """for.""",
    """While reviewing, say what you found and where. When a test fails, say whether the code or the test is wrong, and why.""",
    """When you fix it, say how and why that way. And on threads, say the rule. The interviewer can only score what they """
    """hear. That is the whole round."""])
