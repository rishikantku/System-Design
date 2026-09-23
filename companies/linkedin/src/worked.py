# -*- coding: utf-8 -*-
"""08-worked-questions.html — questions you were actually given, worked end to end.

One section per question: the brief exactly as it was handed over, what to clarify,
the approach method by method, the code in both languages, complexity, edge cases,
follow-ups, and the sentences to say.

This page is for questions with first-party provenance - ones the reader was given
directly, with signatures - which makes them worth more than anything scraped.
"""
import lib
from lib import esc, rich, card, sec, note, grid, table, code, tags, tag, acc, titled

# ---------------------------------------------------------------- Alert Monitor
JAVA_SIG = '''public class AlertMonitor {

    public enum SeverityLevel { LOW, MEDIUM, HIGH }

    public AlertMonitor() { }

    // Record an alert with a timestamp (seconds) and severity.
    public void recordAlert(int currentTimestamp, SeverityLevel severity) { }

    // Number of alerts received in the last 900 seconds.
    public int reportAlertsLast15Min(int currentTimestamp) { }

    // Counts by severity within the 3600-second block containing the most
    // recent timestamp encountered. If the latest timestamp is 3720, that
    // block is 3600..7199.
    public Map<SeverityLevel, Integer> reportSeverityDistribution(int currentTimestamp) { }

    // For each minute in the last 15 minutes of data, the index of the next
    // minute to its right with greater alert volume, or -1 if none.
    // Every minute has at least one alert.
    public List<Integer> detectAlertVolumeSpike() { }
}'''

JAVA_SOLUTION = '''public class AlertMonitor {

    public enum SeverityLevel { LOW, MEDIUM, HIGH }

    private static final int WINDOW = 900;    // 15 minutes
    private static final int HOUR   = 3600;

    private final Deque<int[]> recent = new ArrayDeque<>();      // {timestamp, severityOrdinal}
    private final Map<Integer, int[]> byHour = new HashMap<>();  // hourBucket -> [low, med, high]
    private int maxTs = Integer.MIN_VALUE;                       // most recent timestamp SEEN

    public void recordAlert(int currentTimestamp, SeverityLevel severity) {
        recent.addLast(new int[]{ currentTimestamp, severity.ordinal() });

        byHour.computeIfAbsent(currentTimestamp / HOUR, k -> new int[3])[severity.ordinal()]++;

        if (currentTimestamp > maxTs) maxTs = currentTimestamp;
        evict(currentTimestamp);
    }

    // Amortised O(1): every alert is added once and removed once.
    private void evict(int now) {
        while (!recent.isEmpty() && recent.peekFirst()[0] <= now - WINDOW) recent.pollFirst();
    }

    public int reportAlertsLast15Min(int currentTimestamp) {
        evict(currentTimestamp);
        return recent.size();
    }

    public Map<SeverityLevel, Integer> reportSeverityDistribution(int currentTimestamp) {
        Map<SeverityLevel, Integer> out = new EnumMap<>(SeverityLevel.class);
        for (SeverityLevel s : SeverityLevel.values()) out.put(s, 0);
        if (maxTs == Integer.MIN_VALUE) return out;              // nothing recorded yet

        int[] c = byHour.get(maxTs / HOUR);
        if (c != null) {
            out.put(SeverityLevel.LOW, c[0]);
            out.put(SeverityLevel.MEDIUM, c[1]);
            out.put(SeverityLevel.HIGH, c[2]);
        }
        return out;
    }

    public List<Integer> detectAlertVolumeSpike() {
        // 1. alerts per minute, in minute order
        TreeMap<Integer, Integer> perMinute = new TreeMap<>();
        for (int[] a : recent) perMinute.merge(a[0] / 60, 1, Integer::sum);
        List<Integer> counts = new ArrayList<>(perMinute.values());

        // 2. next greater element, via a monotonic stack
        int n = counts.size();
        Integer[] answer = new Integer[n];
        Deque<Integer> stack = new ArrayDeque<>();               // indices, counts decreasing
        for (int i = 0; i < n; i++) {
            // '<' here means STRICTLY greater wins. Use '<=' for greater-or-equal.
            while (!stack.isEmpty() && counts.get(stack.peek()) < counts.get(i))
                answer[stack.pop()] = i;
            stack.push(i);
        }
        while (!stack.isEmpty()) answer[stack.pop()] = -1;
        return Arrays.asList(answer);
    }
}'''

CSHARP_SOLUTION = '''public class AlertMonitor {

    public enum SeverityLevel { LOW, MEDIUM, HIGH }

    private const int Window = 900;      // 15 minutes
    private const int Hour   = 3600;

    private readonly Queue<(int Ts, SeverityLevel Sev)> _recent = new();
    private readonly Dictionary<int, int[]> _byHour = new();     // hour bucket -> [low, med, high]
    private int _maxTs = int.MinValue;                           // most recent timestamp SEEN

    public void RecordAlert(int currentTimestamp, SeverityLevel severity) {
        _recent.Enqueue((currentTimestamp, severity));

        int bucket = currentTimestamp / Hour;
        if (!_byHour.TryGetValue(bucket, out var counts)) {
            counts = new int[3];
            _byHour[bucket] = counts;
        }
        counts[(int)severity]++;

        if (currentTimestamp > _maxTs) _maxTs = currentTimestamp;
        Evict(currentTimestamp);
    }

    private void Evict(int now) {
        while (_recent.Count > 0 && _recent.Peek().Ts <= now - Window) _recent.Dequeue();
    }

    public int ReportAlertsLast15Min(int currentTimestamp) {
        Evict(currentTimestamp);
        return _recent.Count;
    }

    public Dictionary<SeverityLevel, int> ReportSeverityDistribution(int currentTimestamp) {
        var result = new Dictionary<SeverityLevel, int> {
            [SeverityLevel.LOW] = 0, [SeverityLevel.MEDIUM] = 0, [SeverityLevel.HIGH] = 0
        };
        if (_maxTs == int.MinValue) return result;

        if (_byHour.TryGetValue(_maxTs / Hour, out var c)) {
            result[SeverityLevel.LOW]    = c[0];
            result[SeverityLevel.MEDIUM] = c[1];
            result[SeverityLevel.HIGH]   = c[2];
        }
        return result;
    }

    public IList<int> DetectAlertVolumeSpike() {
        var perMinute = new SortedDictionary<int, int>();
        foreach (var a in _recent) {
            perMinute.TryGetValue(a.Ts / 60, out int c);
            perMinute[a.Ts / 60] = c + 1;
        }
        var counts = new List<int>(perMinute.Values);

        var answer = new int[counts.Count];
        var stack = new Stack<int>();
        for (int i = 0; i < counts.Count; i++) {
            while (stack.Count > 0 && counts[stack.Peek()] < counts[i]) answer[stack.Pop()] = i;
            stack.Push(i);
        }
        while (stack.Count > 0) answer[stack.Pop()] = -1;
        return answer;
    }
}'''


def alert_monitor():
    body = ''

    # ---- the brief
    body += card(
        '<p class="lead">You were handed the full class with all four signatures, which makes this '
        'the most precisely specified question in the workspace. Everything below follows from '
        'reading all four methods <b>before</b> writing the first one.</p>'
        + code(JAVA_SIG, file='AlertMonitor.java — as given'),
        title='The brief, as given')

    # ---- why it is strong
    body += grid([
        card(rich(
          'It looks like four small problems. It is really **one design decision followed by four '
          'small problems**, and the decision is made in `recordAlert` &mdash; before you have '
          'thought about the three readers it has to serve.\n\n'
          'Each method tests something different:\n'
          '**1.** choosing state that serves all three readers\n'
          '**2.** a sliding window over *time*, so eviction\n'
          '**3.** *bucketing*, which is a different idea from windowing\n'
          '**4.** a **monotonic stack** &mdash; a pure algorithm dropped into a design question'),
          title='Why this is a strong question'),
        note(rich(
          'The trap is writing `recordAlert` before reading methods 2, 3 and 4. Your state has to '
          'serve all of them, and two of them want **different shapes**: a 15-minute window and a '
          '60-minute bucket are different retentions.\n\n'
          'Read the whole class first. Obvious, and almost nobody does it under time pressure.'),
          kind='warn', label='The trap'),
    ], 'g2')

    # ---- the contradiction
    body += note(rich(
        'The prose says *&ldquo;the index of the next minute with **greater** alert volume&rdquo;*. '
        'Its own example says otherwise.\n\n'
        'Counts `[1, 2, 5, 2, 2, 1]` with stated answer `[1, 2, -1, 4, -1, -1]`.\n\n'
        'Look at index **3**: its count is **2**, and the answer maps it to index **4**, whose count '
        'is also **2**. Two is not *greater than* two.\n\n'
        '&bull; strictly greater &rarr; `[1, 2, -1, -1, -1, -1]`\n'
        '&bull; greater **or equal** &rarr; `[1, 2, -1, 4, -1, -1]` &mdash; the stated answer\n\n'
        '**Do not silently pick one.** Say that the prose and the example disagree, say which you are '
        'implementing, and offer to switch &mdash; it is one character in the comparison. Either the '
        'interviewer planted it to see whether you would notice, or they had not spotted it. In both '
        'cases you have just been more useful than every candidate who guessed.'),
        kind='bad', label='The specification contradicts itself — this is the question')

    # ---- clarify
    body += '<h3>What I would clarify first</h3>'
    body += table(
        ['Ask', 'What the answer changes'],
        [['Is the 900-second window inclusive or exclusive at the boundary?',
          'Decides `ts > now - 900` versus `>=`. One character, and it is the case a test targets.'],
         ['Do timestamps always arrive in non-decreasing order?',
          'If they can go backwards, a queue with front-eviction is **wrong**. Ask &mdash; do not assume.'],
         ['For method 3, is &ldquo;most recent&rdquo; the max ever seen, or the argument passed in?',
          'The wording says most recent *encountered*. They differ whenever alerts have stopped.'],
         ['For method 4, are only minutes containing alerts included?',
          'The note says every minute has at least one alert, so gaps are out of scope. Say you saw the note.'],
         ['Method 4 says &ldquo;greater&rdquo; but the example needs &ldquo;greater or equal&rdquo;. Which?',
          '**The contradiction above.** The single most valuable thing to raise.']],
        cls='t-ask')

    # ---- the state
    body += '<h3>The approach: decide the state once</h3>'
    body += grid([
        card(rich('**1. A queue of recent alerts** &mdash; `(timestamp, severity)`\n\n'
                  'Serves method 2 (count them) and method 4 (bucket them by minute). Evicted from '
                  'the front once older than 900 s, so it stays bounded no matter how long the '
                  'monitor runs.'), title='Queue'),
        card(rich('**2. Counts per hour bucket, per severity** &mdash; `Map<int, int[3]>`\n\n'
                  'Serves method 3. Key is `ts / 3600`. O(1) to update, O(1) to read.'),
             title='Hour buckets'),
        card(rich('**3. The maximum timestamp seen**\n\n'
                  'Method 3 asks for the block containing the *most recent timestamp encountered* '
                  '&mdash; which is **not** necessarily the argument. Track it explicitly.'),
             title='Max timestamp'),
    ], 'g3')

    body += note(rich(
        '**Why two structures and not one?** A 15-minute window and a 60-minute bucket are different '
        'retentions. Scanning the queue to answer method 3 would be O(n) *and wrong* &mdash; the hour '
        'block is longer than the window, so the alerts you need have already been evicted.\n\n'
        'That single sentence justifies the whole design, and it is the one to say out loud.'),
        kind='', label='The justification an interviewer is listening for')

    # ---- per method
    body += '<h3>Method by method</h3>'
    body += acc(titled('1 &middot; recordAlert', 'append, bucket, track max, evict'), rich(
        'Four things, all O(1) amortised:\n\n'
        '**1.** append `(ts, severity)` to the queue\n'
        '**2.** increment `byHour[ts / 3600][severity]`\n'
        '**3.** update the maximum timestamp seen\n'
        '**4.** evict anything older than the window\n\n'
        'Evicting *here* as well as in the reader matters: it keeps the queue bounded even if nobody '
        'ever calls the reporting methods, which is the realistic case for a long-running monitor.'),
        raw=True)

    body += acc(titled('2 &middot; reportAlertsLast15Min', 'two lines, because the state was right'), rich(
        '`evict(now); return recent.size();`\n\n'
        'That is it. All the work was done by choosing the structure. If this method needs more than '
        'two lines, the state is wrong.\n\n'
        '**Complexity:** amortised O(1). Every alert is added once and removed once, so although the '
        'eviction loop looks unbounded, the total work across all calls is linear in the number of '
        'alerts. Say *amortised* &mdash; it is the precise word.'), raw=True)

    body += acc(titled('3 &middot; reportSeverityDistribution', 'bucketing, not windowing'), rich(
        'One lookup: `byHour[maxTs / 3600]`.\n\n'
        'Two details that are easy to miss:\n\n'
        '&bull; use the **maximum timestamp seen**, not the argument &mdash; the wording is explicit\n'
        '&bull; return a map with **all three severities present**, zeroed, even when nothing was '
        'recorded. A missing key is a different answer from a zero, and a caller will crash on it.\n\n'
        '**Complexity:** O(1). It is a bucket read, not a scan of the window &mdash; which is exactly '
        'what the second structure bought you.'), raw=True)

    body += acc(titled('4 &middot; detectAlertVolumeSpike', 'next greater element, via a monotonic stack'), rich(
        '**Step 1** &mdash; count alerts per minute, in minute order. A sorted map gives you the '
        'minutes in order, and the index in the answer refers to position in that order.\n\n'
        '**Step 2** &mdash; next greater element. The naive answer is, for each minute, scan right '
        'until you find a bigger one: **O(n&sup2;)**. At 15 minutes that is 225 operations and '
        'nobody cares &mdash; *say that*, then do it properly anyway, because the window might grow '
        'and because this is plainly the pattern being tested.\n\n'
        'The tool is a **monotonic stack**: a stack of indices whose counts are always decreasing. '
        'Each index is pushed once and popped at most once, so it is **O(n)**.'), raw=True)

    # ---- stack walkthrough
    body += '<h4>The monotonic stack, step by step</h4>'
    body += note(rich('Counts `[1, 2, 5, 2, 2, 1]`, using the **strictly greater** rule so you can see '
                      'exactly where the contradiction bites.'), kind='')
    body += table(
        ['Step', 'What happens', 'Stack after'],
        [['`i=0` count 1', 'stack empty &rarr; push 0', '`[0]`'],
         ['`i=1` count 2', '2 beats the count at 0 &rarr; **answer[0] = 1**, pop. push 1', '`[1]`'],
         ['`i=2` count 5', '5 beats the count at 1 &rarr; **answer[1] = 2**, pop. push 2', '`[2]`'],
         ['`i=3` count 2', '2 is not &gt; 5 &rarr; push 3', '`[2, 3]`'],
         ['`i=4` count 2', '2 is not &gt; 2 &mdash; **strict** &rarr; push 4. *This is the disputed step: '
          'greater-or-equal would pop 3 and set answer[3] = 4*', '`[2, 3, 4]`'],
         ['`i=5` count 1', 'not greater than anything &rarr; push 5', '`[2, 3, 4, 5]`'],
         ['end', 'everything left never found a greater element &rarr; **&minus;1**', '`[]`']],
        cls='t-walk')

    # ---- code
    body += '<h3>The code</h3>'
    body += note(rich('The question was given in **Java**, so that is the primary version. The C# '
                      'translation is one-to-one and is here because the rest of this workspace is C#.'),
                 kind='')
    body += acc(titled('Java', 'as the question was posed'), code(JAVA_SOLUTION, file='AlertMonitor.java'),
                raw=True, open=True)
    body += acc(titled('C#', 'same design, workspace convention'), code(CSHARP_SOLUTION, file='AlertMonitor.cs'),
                raw=True)

    # ---- complexity
    body += '<h3>Complexity</h3>'
    body += table(
        ['Method', 'Time', 'Why'],
        [['`recordAlert`', '**O(1)** amortised', 'Append, one map update, and eviction that pays for itself'],
         ['`reportAlertsLast15Min`', '**O(1)** amortised', 'Evict, then read the size'],
         ['`reportSeverityDistribution`', '**O(1)**', 'One bucket lookup &mdash; **not** a scan of the window'],
         ['`detectAlertVolumeSpike`', '**O(m)**', '`m` = minutes in the window (&le; 15). Each index pushed and popped once'],
         ['Space', '**O(w + h)**', '`w` = alerts in the window, `h` = distinct hour buckets seen']],
        cls='t-cx')

    # ---- edges
    body += '<h3>Edge cases to name before being asked</h3>'
    body += grid([
        card(rich('**Nothing recorded yet**\n\nAll three readers must work on an empty monitor: `0`, '
                  'three zeros, and an empty list. Not a crash, and not a map with missing keys.')),
        card(rich('**The hour buckets grow for ever**\n\nNothing evicts them. At one per hour that is '
                  '~8,760 a year &mdash; genuinely small. **Say you noticed, then say it does not '
                  'matter.** Noticing and correctly dismissing beats both missing it and '
                  'over-engineering it.')),
        card(rich('**Window boundary**\n\nAn alert exactly 900 seconds old: in or out? Pick one, say '
                  'which, keep it to one comparison.')),
        card(rich('**Timestamps going backwards**\n\nBreaks front-eviction entirely. If it can happen, '
                  'the queue is the wrong structure &mdash; which is why it is a clarifying question.')),
        card(rich('**All minutes equal**\n\nEvery answer is &minus;1 under strict, and a chain under '
                  'greater-or-equal. **The best possible test for the ambiguity.**')),
        card(rich('**One minute only**\n\nReturns a single &minus;1. Cheap, and it catches an '
                  'empty-stack bug.')),
    ], 'g3')

    # ---- follow-ups
    body += '<h3>Follow-ups</h3>'
    body += grid([
        card(rich(
          '&bull; **&ldquo;Make it thread-safe.&rdquo;** The pivot that appears across every '
          'design-flavoured question. One lock around the shared state first; name the invariant '
          'before naming a primitive.\n\n'
          '&bull; **&ldquo;What if the window were an hour?&rdquo;** A constant changes. Nothing else. '
          'Say so confidently.\n\n'
          '&bull; **&ldquo;Return the minutes, not the indices.&rdquo;** Carry the minute keys '
          'alongside the counts.'), title='Likely immediate follow-ups'),
        card(rich(
          '&bull; **&ldquo;A million alerts a second.&rdquo;** Stop storing individual alerts. Keep '
          'per-second counters in a ring buffer of 900 slots &rarr; **O(1) memory regardless of '
          'rate**, and the window becomes a sum over the ring.\n\n'
          '&bull; **&ldquo;An arbitrary window, not 15 minutes.&rdquo;** Prefix sums over per-minute '
          'counts, so any range is two lookups.\n\n'
          '&bull; **&ldquo;Many services, one monitor.&rdquo;** Keyed state per service; the real '
          'question becomes memory per key.\n\n'
          '&bull; **&ldquo;Why not just query a metrics system?&rdquo;** A fair challenge, and often '
          'the right production answer. Being willing to say so is judgement, not evasion.'),
          title='Staff-level follow-ups'),
    ], 'g2')

    # ---- script
    body += '<h3>What I would say</h3>'
    body += card(''.join('<div class="say-line">&ldquo;%s&rdquo;</div>' % rich(s) for s in [
        'Let me read all four methods first, because method one has to choose state that serves the other three.',
        'I will keep two structures: a queue of recent alerts for the window, and per-hour severity counters. A 15-minute window and a 60-minute bucket are different retentions, so one structure cannot serve both.',
        'Method three says the block containing the most recent timestamp *encountered*, so I am tracking the max timestamp seen rather than using the argument.',
        'One thing before I write method four &mdash; the prose says the next minute with **greater** volume, but the example maps index three to index four and those counts are equal. Which do you want: strictly greater, or greater or equal?',
        'For method four I will use a monotonic stack. Each index is pushed once and popped once, so it is linear rather than the quadratic scan.',
        'At 15 minutes the quadratic version would honestly be fine. I am doing it properly because the window could grow and because this is clearly the pattern being tested.',
        'The hour buckets are unbounded. At one per hour that is a few thousand a year, so I would leave it &mdash; but I would rather note it than pretend it is bounded.',
    ]), cls='say-card')

    return sec('alertmonitor', 'Alert Monitor', body,
               kicker='Given to you, with full signatures',
               why='Four methods, four patterns &middot; and a contradiction in the spec')


def build():
    body = sec('about', 'What this page is',
        card(rich(
          'Questions worked end to end: the brief, what to clarify, the approach, the code, '
          'complexity, edge cases and follow-ups.\n\n'
          'Each section states **how well the question is known**, because that varies enormously. '
          'Alert Monitor came to you with full signatures. Others are titles on a partially-paywalled '
          'list, where the algorithm is public but the exact framing is not. '
          '**Both are worth preparing; only one is worth trusting as a literal question.**')),
        kicker='Worked questions', why='With provenance stated for each')

    body += alert_monitor()
    body += sort_transformed()
    body += lz78()
    body += interval_tree()
    body += backlog()

    return lib.page('08-worked-questions.html', 'Worked questions',
        'Questions worked end to end &mdash; brief, clarifications, approach, code, complexity, follow-ups &mdash; with the provenance of each stated honestly.',
        body, crumb_tail='Worked questions',
        hero_chips=[('done', '4 worked in full'), ('', 'Java'), ('', 'provenance stated')],
        extra_head='<style>'
                   '.say-card .say-line{padding:12px 16px 12px 40px;margin-bottom:10px;position:relative;'
                   'background:var(--ok-bg);border-radius:9px;border-left:4px solid var(--green);'
                   'font-size:14.5px;line-height:1.55}'
                   '.say-card .say-line::before{content:"\\201C";position:absolute;left:13px;top:6px;'
                   'font-size:30px;color:var(--green);opacity:.55}'
                   '.t-ask td:first-child,.t-walk td:first-child{width:34%;font-weight:600}'
                   '.t-cx td:nth-child(2){white-space:nowrap}'
                   '.t-bl td:first-child{width:22%;font-weight:600}'
                   '.t-bl td:nth-child(2){width:20%}'
                   '</style>')


def backlog():
    body = note(rich(
        '**I tried to recover these and could not.** Three web searches for the distinctive titles '
        '&mdash; *Alive Cache*, *Tree Fusion*, *Config Validator*, *Candidate Connection*, *LZ78* '
        '&mdash; returned **no reference to any of them** as LinkedIn questions. Fetching an '
        'individual question page returns *&ldquo;No questions are available yet / Loading practice '
        'workspace&hellip;&rdquo;* &mdash; the statements sit behind login and points.\n\n'
        'What the evidence does support: interviewdb appears to use the **real public name where one '
        'exists** (*Sort Transformed Array*, *Max Stack* are exact LeetCode titles) and an '
        '**invented name where the question is custom**. That is why the odd ones are unfindable '
        '&mdash; there is nothing to find.'),
        kind='warn', label='Why most of this list is not worked below')

    body += table(
        ['Title', 'Status', 'What I can and cannot say'],
        [['**Sort Transformed Array**', '<span class="tag hi">worked above</span>',
          'Exact title match to LeetCode 360. Statement known'],
         ['**LZ78 Compression**', '<span class="tag hi">worked above</span>',
          'Public algorithm (1978). Framing inferred, algorithm certain'],
         ['**Interval Tree**', '<span class="tag hi">worked above</span>',
          'Standard structure. Framing inferred, structure certain'],
         ['**Max Stack**', '<span class="tag hi">on page 01</span>',
          'Exact title match to LeetCode 716. Already a worked problem'],
         ['**Delayed Scheduler**', '<span class="tag med">partly covered</span>',
          'Same shape as the job scheduler in the design research, which has a first-hand Blind report'],
         ['**Word Transformation**', '<span class="tag med">likely covered</span>',
          '*Probably* Word Ladder, which has 2 independent reports and is worked in the coding course. '
          '**Name similarity is not evidence**'],
         ['**Tree Fusion**', '<span class="tag med">likely covered</span>',
          '*Probably* a tree merge. The keyed n-ary merge is already worked. **Unconfirmed**'],
         ['**Candidate Connection**', '<span class="tag med">likely covered</span>',
          '*Probably* degrees of connection, which is on your own list and worked. **Unconfirmed**'],
         ['**Number of Clouds**', '<span class="tag med">likely a grid count</span>',
          '*Probably* a connected-components / flood-fill variant. **Unconfirmed**'],
         ['**Alive Cache**', '<span class="tag low">unknown</span>',
          'Most likely a cache with TTL or liveness-based eviction. I will not write it up as fact'],
         ['**Config Validator**', '<span class="tag low">unknown</span>',
          'Nothing recoverable. Could be schema validation, cycle detection in config references, or '
          'something else'],
         ['**Task Manager**', '<span class="tag low">unknown</span>',
          'Could be a priority-queue design, or a dependency scheduler. Two different problems'],
         ['**Minimize Points Distance**', '<span class="tag low">unknown</span>',
          'Geometry or a BST traversal &mdash; genuinely ambiguous from the title'],
         ['**~8 locked entries**', '<span class="tag low">paywalled</span>',
          'Titles not shown. This is a partial view of the list']],
        cls='t-bl')

    body += note(rich(
        '**What would change this.** If you can get the statements &mdash; a screenshot, a paste, '
        'anything &mdash; I will work each one to the depth of Alert Monitor, including compiling and '
        'testing the code.\n\n'
        'Writing them up from the titles alone would produce confident, well-formatted answers to '
        '**problems nobody asked**, and you would revise the wrong thing. That is worse than an '
        'honest gap.'), kind='', label='The offer')

    return sec('backlog', 'The rest of the interviewdb list', body,
               kicker='Researched, mostly not recoverable',
               why='18 visible titles &middot; ~8 locked &middot; statements gated')


# ---------------------------------------------------------------- Sort Transformed Array
STA_JAVA = '''public int[] sortTransformedArray(int[] nums, int a, int b, int c) {
    int n = nums.length;
    int[] out = new int[n];

    int lo = 0, hi = n - 1;
    // a > 0  -> parabola opens upward,   extremes are at the ENDS -> fill from the back
    // a < 0  -> parabola opens downward, extremes are in the MIDDLE -> fill from the front
    // a == 0 -> linear; the a >= 0 branch handles it for either sign of b
    int idx = (a >= 0) ? n - 1 : 0;

    while (lo <= hi) {
        int fLo = f(nums[lo], a, b, c);
        int fHi = f(nums[hi], a, b, c);

        if (a >= 0) {                       // take the LARGER end, place it at the back
            if (fLo >= fHi) { out[idx--] = fLo; lo++; }
            else            { out[idx--] = fHi; hi--; }
        } else {                            // take the SMALLER end, place it at the front
            if (fLo <= fHi) { out[idx++] = fLo; lo++; }
            else            { out[idx++] = fHi; hi--; }
        }
    }
    return out;
}

private int f(int x, int a, int b, int c) {
    return a * x * x + b * x + c;
}'''


def sort_transformed():
    body = card(rich(
        '**The problem.** You are given an array `nums` **already sorted ascending**, and three '
        'integers `a`, `b`, `c`. Apply the quadratic `f(x) = ax² + bx + c` to every element and '
        'return the results **in sorted order**.\n\n'
        'The easy answer is: map, then sort &mdash; O(n log n). The question is whether you can do it '
        'in **O(n)**, which is the whole point.'), title='Sort Transformed Array')

    body += grid([
        card(rich(
          '**The insight is geometric, not algorithmic.**\n\n'
          '`f` is a parabola. The input is sorted, so it walks along the x-axis left to right.\n\n'
          '&bull; If **a &gt; 0** the parabola opens upward, so the *largest* values sit at the two '
          '**ends** of the input and the smallest in the middle.\n'
          '&bull; If **a &lt; 0** it opens downward, so the *smallest* values sit at the **ends**.\n'
          '&bull; If **a = 0** it is a straight line &mdash; monotonic either way.\n\n'
          'So the extremes are always at the ends. Two pointers, one from each end, and you always '
          'know which end holds the next value you need.'), title='Why two pointers work'),
        note(rich(
          '**Fill direction is the bit people get wrong.**\n\n'
          'With `a > 0` you are taking the *largest* remaining value each step, so you must fill the '
          'output **from the back**.\n\n'
          'With `a < 0` you take the *smallest*, so you fill **from the front**.\n\n'
          'Get this backwards and the array comes out reversed &mdash; and it still passes a '
          'symmetric test case, which is how it slips through.'), kind='warn', label='The trap'),
    ], 'g2')

    body += '<h4>Code</h4>'
    body += code(STA_JAVA, file='SortTransformedArray.java')

    body += '<h4>Complexity, edge cases, follow-ups</h4>'
    body += table(
        ['', 'Answer'],
        [['Time', '**O(n)** &mdash; each element is consumed exactly once'],
         ['Space', '**O(n)** for the output, O(1) extra'],
         ['`a = 0`', 'Linear. The `a >= 0` branch is correct for **both** signs of `b` &mdash; worth '
          'saying, because it looks like a missing case'],
         ['Empty / single', 'Return as-is. The loop handles both without a guard'],
         ['Overflow', '`a*x*x` overflows `int` for large `x`. Mention it; use `long` if asked'],
         ['Follow-up: *&ldquo;what if the input is not sorted?&rdquo;*',
          'Then O(n log n) is optimal &mdash; the sortedness **is** the thing that buys you linear time'],
         ['Follow-up: *&ldquo;arbitrary f(x)?&rdquo;*',
          'Two pointers only work because a quadratic is **unimodal**. For an arbitrary function you '
          'are back to map-then-sort. Say that &mdash; it shows you know *why* the trick works']],
        cls='t-cx')

    return sec('sorttransformed', 'Sort Transformed Array', body,
               kicker='interviewdb title matches LeetCode 360 exactly',
               why='Public problem &middot; statement known &middot; historically LinkedIn-tagged')


# ---------------------------------------------------------------- LZ78
LZ78_JAVA = '''public final class Lz78 {

    /** One output token: the dictionary index of the longest known prefix, plus the next char. */
    public static final class Token {
        public final int index; public final char ch; public final boolean hasChar;
        Token(int index, char ch, boolean hasChar) { this.index = index; this.ch = ch; this.hasChar = hasChar; }
        @Override public String toString() { return "(" + index + "," + (hasChar ? ch : '-') + ")"; }
    }

    public static List<Token> encode(String s) {
        Map<String, Integer> dict = new HashMap<>();   // phrase -> index, 1-based
        List<Token> out = new ArrayList<>();
        StringBuilder w = new StringBuilder();         // longest phrase seen so far

        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            String candidate = w.toString() + ch;

            if (dict.containsKey(candidate)) {         // still a known phrase - keep extending
                w.append(ch);
                continue;
            }
            // emit (index of w, ch); index 0 means "w is empty"
            out.add(new Token(dict.getOrDefault(w.toString(), 0), ch, true));
            dict.put(candidate, dict.size() + 1);      // the new phrase enters the dictionary
            w.setLength(0);
        }

        if (w.length() > 0)                            // trailing phrase with no new char
            out.add(new Token(dict.get(w.toString()), '\\0', false));
        return out;
    }

    public static String decode(List<Token> tokens) {
        List<String> phrases = new ArrayList<>();
        phrases.add("");                               // index 0 is the empty phrase
        StringBuilder out = new StringBuilder();

        for (Token t : tokens) {
            String prefix = phrases.get(t.index);
            String phrase = t.hasChar ? prefix + t.ch : prefix;
            out.append(phrase);
            if (t.hasChar) phrases.add(phrase);        // only full phrases are added
        }
        return out.toString();
    }
}'''


def lz78():
    body = card(rich(
        '**The problem.** Implement LZ78 compression: `encode` a string into a list of tokens, and '
        '`decode` those tokens back into the original string.\n\n'
        'LZ78 is a dictionary compressor published by Lempel and Ziv in 1978. It is well documented '
        'public material, so unlike most titles on that list the algorithm itself is not in doubt '
        '&mdash; only the exact interview framing is.'), title='LZ78 Compression')

    body += grid([
        card(rich(
          '**How it works, in one paragraph.**\n\n'
          'Walk the input left to right holding the longest phrase `w` you have already seen. For each '
          'character `ch`, ask whether `w + ch` is in the dictionary.\n\n'
          '&bull; **Yes** &rarr; extend: `w = w + ch`, and read on.\n'
          '&bull; **No** &rarr; emit the token `(index of w, ch)`, add `w + ch` to the dictionary, '
          'and reset `w` to empty.\n\n'
          'Index **0** is reserved for the empty phrase, which is how the very first token works.'),
          title='The algorithm'),
        card(rich(
          '**Decoding is the mirror, and it is simpler.**\n\n'
          'Keep a list of phrases with the empty string at index 0. For each token `(i, ch)`, the '
          'phrase is `phrases[i] + ch`. Append it to the output **and** to the phrase list.\n\n'
          'The dictionary rebuilds itself from the tokens alone &mdash; **it is never transmitted**. '
          'That is the elegant part, and it is worth saying out loud: encoder and decoder construct '
          'the same table in the same order.'), title='Decoding'),
    ], 'g2')

    body += note(rich(
        '**The edge case that breaks naive implementations:** the trailing phrase.\n\n'
        'If the input ends while `w` is non-empty, that phrase has no following character to emit with '
        'it. You must emit a token carrying the index but **no character**, and the decoder has to know '
        'not to add it to the dictionary.\n\n'
        'Input `"aaa"` is the smallest case that exposes it. Most implementations that "work" on '
        '`"abab"` silently drop the last character here.'), kind='bad', label='Where this goes wrong')

    body += '<h4>Code</h4>'
    body += code(LZ78_JAVA, file='Lz78.java')

    body += '<h4>Complexity, and what an interviewer will push on</h4>'
    body += table(
        ['', 'Answer'],
        [['Time', '**O(n)** average &mdash; one hash lookup per character. Worst case depends on '
                  'string hashing, since keys grow'],
         ['Space', '**O(n)** &mdash; the dictionary holds at most one phrase per token'],
         ['*&ldquo;Why does the decoder not need the dictionary?&rdquo;*',
          'Because it rebuilds it in the same order from the tokens. **The best question here**'],
         ['*&ldquo;Does this always compress?&rdquo;*',
          '**No.** On short or random input the tokens are larger than the text. Say so &mdash; '
          'claiming universal compression is provably wrong'],
         ['*&ldquo;Bound the dictionary.&rdquo;*',
          'Real implementations cap it and reset when full. That is one line, and it is what makes '
          'it usable on a stream'],
         ['*&ldquo;How would you serialise tokens?&rdquo;*',
          'Fixed-width indices waste space early; variable-width bit packing is the real answer, and '
          'it is where LZW improves on LZ78']],
        cls='t-cx')

    return sec('lz78', 'LZ78 Compression', body,
               kicker='Public algorithm (Lempel–Ziv, 1978)',
               why='The algorithm is documented &middot; the exact interview framing is not')


# ---------------------------------------------------------------- Interval Tree
ITREE_JAVA = '''public class IntervalTree {

    private static class Node {
        final int lo, hi;
        int maxEnd;                 // largest hi anywhere in this subtree - the pruning key
        Node left, right;
        Node(int lo, int hi) { this.lo = lo; this.hi = hi; this.maxEnd = hi; }
    }

    private Node root;

    public void insert(int lo, int hi) { root = insert(root, lo, hi); }

    private Node insert(Node n, int lo, int hi) {
        if (n == null) return new Node(lo, hi);
        if (lo < n.lo) n.left  = insert(n.left,  lo, hi);
        else           n.right = insert(n.right, lo, hi);
        n.maxEnd = Math.max(n.maxEnd, hi);            // maintain the augmentation on the way back up
        return n;
    }

    /** All stored intervals overlapping [lo, hi], inclusive. */
    public List<int[]> queryOverlapping(int lo, int hi) {
        List<int[]> found = new ArrayList<>();
        collect(root, lo, hi, found);
        return found;
    }

    private void collect(Node n, int lo, int hi, List<int[]> found) {
        if (n == null) return;
        if (n.maxEnd < lo) return;                    // PRUNE: nothing in here reaches lo

        collect(n.left, lo, hi, found);

        if (n.lo <= hi && lo <= n.hi)                 // the overlap test
            found.add(new int[]{ n.lo, n.hi });

        if (n.lo <= hi) collect(n.right, lo, hi, found);   // PRUNE: everything right starts after hi
    }
}'''


def interval_tree():
    body = card(rich(
        '**The problem.** Build a structure that stores intervals and answers: *which stored intervals '
        'overlap `[lo, hi]`?* &mdash; faster than checking every one.\n\n'
        'The naive answer is a list and a linear scan: O(n) per query. An interval tree gets you '
        '**O(log n + k)**, where `k` is the number of results.'), title='Interval Tree')

    body += grid([
        card(rich(
          '**It is a BST, augmented.**\n\n'
          'Order nodes by interval **start**. Then store one extra field per node: `maxEnd`, the '
          'largest endpoint anywhere in that subtree.\n\n'
          'That single field is the whole data structure. It is maintained on insert as you unwind '
          'the recursion, and it is what makes pruning possible.'), title='The structure'),
        card(rich(
          '**Two prunes, and the first one is the clever one.**\n\n'
          '**1.** If `node.maxEnd < lo`, nothing in this entire subtree reaches far enough right to '
          'overlap. **Skip the whole subtree.**\n\n'
          '**2.** If `node.lo > hi`, this node starts after the query ends &mdash; and because the '
          'tree is ordered by start, so does everything to its right. **Skip the right subtree.**\n\n'
          'Be ready to justify prune 1 out loud; it is the question.'), title='Why it is fast'),
    ], 'g2')

    body += note(rich(
        '**The overlap test itself.** Two intervals `[a1,a2]` and `[b1,b2]` overlap when '
        '`a1 <= b2 && b1 <= a2`.\n\n'
        'Write it that way rather than enumerating cases. Candidates who enumerate "b starts inside a, '
        'or a starts inside b, or one contains the other" almost always miss a case and almost always '
        'take five minutes doing it.'), kind='', label='Say this and move on')

    body += '<h4>Code</h4>'
    body += code(ITREE_JAVA, file='IntervalTree.java')

    body += '<h4>Complexity, and the follow-up that matters</h4>'
    body += table(
        ['', 'Answer'],
        [['Insert', '**O(h)** &mdash; `h` is height, so O(log n) balanced, **O(n) if the input arrives sorted**'],
         ['Query', '**O(log n + k)** &mdash; `k` results, because pruning skips everything else'],
         ['Space', '**O(n)**'],
         ['*&ldquo;What if intervals arrive in sorted order?&rdquo;*',
          '**The tree degenerates into a linked list.** This is the follow-up. You need self-balancing '
          '&mdash; a red-black or AVL tree &mdash; and the `maxEnd` field must be recomputed on '
          'rotation. Naming *that* is the real answer'],
         ['*&ldquo;Just find any one overlap.&rdquo;*',
          'Then it is **O(log n)**: descend once, using `maxEnd` to choose the branch'],
         ['*&ldquo;Deletion?&rdquo;*',
          'Standard BST delete, then recompute `maxEnd` up the path. The augmentation is the fiddly part'],
         ['*&ldquo;Why not just sort and binary search?&rdquo;*',
          'Fine for a **static** set &mdash; and genuinely better. The tree earns its place only when '
          'intervals are inserted and queried interleaved']],
        cls='t-cx')

    return sec('intervaltree', 'Interval Tree', body,
               kicker='Standard data structure',
               why='Well-defined problem &middot; exact interview framing unknown')
