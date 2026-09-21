# -*- coding: utf-8 -*-
"""Problems taken straight from LinkedIn's own Staff SI onsite prep pack,
plus drills for the two things the Staff Coding module says it scores:
modularity/extensibility, and finding and fixing bugs."""

OFFICIAL_PROBLEMS = [
 dict(id='firefight', title='Firefighting Strategy — the official example question', level='med',
  topic='Grids · Components · Extensibility',
  why='**This is the example question printed in LinkedIn\'s own Staff Coding prep pack.** The module scores modularity, '
      'extensibility, bug-finding, edge cases and abstraction — so separating the traversal from the ordering policy matters '
      'more than the algorithm, and the recursion-depth question is a real trap.',
  question='You are a firefighting chief. Input: a grid of integers where 1 means fire and 0 means no fire. Extinguishing one '
           'fire (one unit of water) also extinguishes every fire connected to it horizontally or vertically. Output: the best '
           'firefighting order as a list of coordinates — the minimum number of water units, attacking the largest group first, '
           'then the next largest. For `[[1,1,1],[1,0,0],[1,0,1]]` the answer is a cell of the five-cell group, then (2,2).',
  think='The minimum number of units is fixed — it is the number of connected components — so "minimum water" is not a choice '
        'you make. The only freedom is the order. Where does that leave the complexity? And what is the one structural seam that '
        'makes this code survive the interviewer changing the rule?',
  approach='Two observations, said out loud before any code:\n\n'
           '1. **Every component costs exactly one unit**, so the minimum is the component count. This is a grouping plus a sort, '
           'not an optimisation problem.\n'
           '2. **Any cell of a component is a valid attack point**, so the answer is one representative per component, ordered by '
           'size descending.\n\n'
           'Then the decision this module actually scores: keep three concerns separate — **finding components** (BFS/DFS/union-find), '
           '**choosing the representative**, and **ordering the attacks**. Pass the ordering in as a strategy rather than hard-coding '
           '`OrderByDescending(size)`. That seam is the difference between a correct answer and a Staff-level one here.',
  edges=['Empty or null grid; zero rows or zero columns.',
         'All zeros → empty order, zero water. All ones → one coordinate.',
         'Jagged arrays — handle bounds per row, or reject explicitly.',
         'Ties in size — state your tiebreak (row-major keeps output deterministic and testable).',
         'A 1000×1000 all-ones grid → recursive DFS overflows the stack; use an explicit stack or BFS.',
         'Do not mutate the caller\'s grid — keep a separate visited array, and say why.'],
  code='''public readonly record struct Cell(int Row, int Col);
public sealed record FireGroup(Cell Representative, int Size, IReadOnlyList<Cell> Cells);

public interface IAttackOrder {                        // the extensibility seam
    IEnumerable<FireGroup> Order(IReadOnlyList<FireGroup> groups);
}

public sealed class LargestFirst : IAttackOrder {
    public IEnumerable<FireGroup> Order(IReadOnlyList<FireGroup> groups) =>
        groups.OrderByDescending(g => g.Size)
              .ThenBy(g => g.Representative.Row)       // deterministic tiebreak keeps tests stable
              .ThenBy(g => g.Representative.Col);
}

public sealed class FireGrid {
    private static readonly (int dr, int dc)[] Neighbours = { (1, 0), (-1, 0), (0, 1), (0, -1) };  // no diagonals

    private readonly int[][] _grid;
    public FireGrid(int[][] grid) => _grid = grid ?? throw new ArgumentNullException(nameof(grid));

    // Every connected group of fires, discovered in row-major order.
    public IReadOnlyList<FireGroup> FindGroups() {
        var groups = new List<FireGroup>();
        if (_grid.Length == 0) return groups;

        var visited = new bool[_grid.Length][];        // never mutate the caller's grid
        for (int r = 0; r < _grid.Length; r++) visited[r] = new bool[_grid[r].Length];

        for (int r = 0; r < _grid.Length; r++)
            for (int c = 0; c < _grid[r].Length; c++)
                if (_grid[r][c] == 1 && !visited[r][c])
                    groups.Add(Collect(new Cell(r, c), visited));

        return groups;
    }

    private FireGroup Collect(Cell start, bool[][] visited) {
        var cells = new List<Cell>();
        var stack = new Stack<Cell>();                 // iterative: recursion would overflow on a large grid
        stack.Push(start);
        visited[start.Row][start.Col] = true;

        while (stack.Count > 0) {
            var cell = stack.Pop();
            cells.Add(cell);
            foreach (var (dr, dc) in Neighbours) {
                int nr = cell.Row + dr, nc = cell.Col + dc;
                if (!InBounds(nr, nc) || visited[nr][nc] || _grid[nr][nc] != 1) continue;
                visited[nr][nc] = true;                // mark on push, not on pop: no duplicates in the stack
                stack.Push(new Cell(nr, nc));
            }
        }
        return new FireGroup(start, cells.Count, cells);
    }

    private bool InBounds(int r, int c) =>
        r >= 0 && r < _grid.Length && c >= 0 && c < _grid[r].Length;   // jagged-safe
}

public sealed class FirefightingPlanner {
    private readonly IAttackOrder _order;
    public FirefightingPlanner(IAttackOrder order = null) => _order = order ?? new LargestFirst();

    // Attack coordinates in order. Count == units of water == number of groups.
    public IReadOnlyList<Cell> Plan(int[][] grid) =>
        _order.Order(new FireGrid(grid).FindGroups())
              .Select(g => g.Representative)
              .ToList();
}''',
  complexity='O(R·C): every cell is visited and pushed once. Sorting groups is O(G log G) with G ≤ R·C. Space is O(R·C) for the '
             'visited array plus the largest group held on the stack.',
  follow=['**What if diagonals count?** Add four entries to the neighbour table — and point at the seam as you say it.',
          '**What if the ordering rule changes** (nearest to the station, highest-value property first)? Inject a different '
          '`IAttackOrder`. This is the follow-up the module exists for.',
          '**What if the grid does not fit in memory?** Stream by rows with union-find across row boundaries, or tile and merge '
          'components at the seams.',
          '**What if fires spread between attacks?** It becomes a simulation, re-grouping after each step, and greedy "largest '
          'first" is no longer obviously optimal. Say so.',
          '**How would you test it?** Empty, all-zero, all-one, single cell, jagged, two equal groups (tiebreak), 1000×1000 stress.'],
  optimise='If only the count is needed, drop the cell lists and keep a running size. For a huge sparse grid, union-find over the '
           'fire cells avoids allocating a visited array the size of the grid. If the same grid is replanned with different rules, '
           'compute groups once and re-order — which the class split already allows.',
  evalpts=['Did you say "minimum water = number of components" before writing code?',
           'Did you separate traversal, representative choice and ordering?',
           'Did you use an explicit stack and explain the recursion-depth risk?',
           'Did you avoid mutating the input grid?',
           'Did you give a deterministic tiebreak so the output is testable?',
           'Did you name the tests you would write, including the stress case?']),

 dict(id='bugfix', title='Find and fix the bugs: a rate-limited job runner', level='med',
  topic='Bug-finding · Pointers · Edge cases',
  why='The pack says these sessions are about **finding and fixing bugs and other errors**, and often involve pointers, edge '
      'cases and abstraction. This drill is a small class with five real defects — practise reading before rewriting.',
  question='Here is a job runner that should execute at most `maxPerWindow` jobs per time window, retrying failures up to '
           '`maxRetries` times. Find every bug, fix them, and say how you would test each fix.',
  think='Read it twice before touching it. Ask: what is the window boundary rule? What happens at exactly the limit? What does '
        'the retry count mean — attempts or retries? What is shared across threads? Which of these is a *bug* and which is an '
        '*unstated requirement* you should ask about?',
  approach='Work in this order, out loud: (1) restate the intended contract, (2) list the defects you can see by reading, '
           '(3) write a failing test for the one that matters most, (4) fix, (5) re-read for the ones you missed. Name each bug '
           'as you find it rather than silently editing — the interviewer is scoring the diagnosis, not the keystrokes.\n\n'
           '**The five defects:** off-by-one at the limit (`<=` admits one too many); the window never resets because '
           '`_windowStart` is only set in the constructor; `maxRetries` is used as total attempts, so a value of 0 never runs; '
           'the catch swallows cancellation as if it were a job failure; and `_count` is mutated without synchronisation while '
           'the class is documented as thread-safe.',
  edges=['`maxPerWindow` of 0 or negative → reject in the constructor.',
         'Exactly at the limit — the classic `<` versus `<=` decision.',
         'A job that throws `OperationCanceledException` — not a failure, do not retry.',
         'A job that always fails → bounded retries, then surfaced, not swallowed.',
         'Clock: use a monotonic source, never `DateTime.Now` (it moves with the time zone and NTP).',
         'Concurrency: two threads entering `TryRun` at the same instant.'],
  code='''// BEFORE — five defects. Read it before you fix it.
public class JobRunner {
    private readonly int _maxPerWindow, _maxRetries;
    private readonly TimeSpan _window;
    private int _count;
    private DateTime _windowStart = DateTime.Now;        // (5) wall clock, set once

    public JobRunner(int maxPerWindow, int maxRetries, TimeSpan window) {
        _maxPerWindow = maxPerWindow; _maxRetries = maxRetries; _window = window;
    }

    public bool TryRun(Action job) {
        if (_count <= _maxPerWindow) {                   // (1) off-by-one: admits maxPerWindow + 1
            _count++;                                    // (4) unsynchronised read-modify-write
            for (int attempt = 0; attempt < _maxRetries; attempt++) {   // (3) maxRetries used as attempts
                try { job(); return true; }
                catch (Exception) { }                    // (2) swallows cancellation, and hides the last failure
            }
        }
        return false;
    }
}

// AFTER — contract stated, defects fixed, still small.
/// <summary>Runs at most <paramref name="maxPerWindow"/> jobs per window, retrying failures
/// <paramref name="maxRetries"/> times (so up to maxRetries + 1 attempts). Thread-safe.</summary>
public sealed class JobRunner {
    private readonly int _maxPerWindow, _maxRetries;
    private readonly long _windowTicks;
    private readonly object _gate = new();
    private int _count;
    private long _windowStart;                            // monotonic

    public JobRunner(int maxPerWindow, int maxRetries, TimeSpan window) {
        if (maxPerWindow <= 0) throw new ArgumentOutOfRangeException(nameof(maxPerWindow));
        if (maxRetries < 0)    throw new ArgumentOutOfRangeException(nameof(maxRetries));
        if (window <= TimeSpan.Zero) throw new ArgumentOutOfRangeException(nameof(window));
        _maxPerWindow = maxPerWindow; _maxRetries = maxRetries;
        _windowTicks = (long)(window.TotalSeconds * Stopwatch.Frequency);
        _windowStart = Stopwatch.GetTimestamp();
    }

    public bool TryRun(Action job, CancellationToken ct = default) {
        ArgumentNullException.ThrowIfNull(job);
        lock (_gate) {                                    // admission is the only shared state
            var now = Stopwatch.GetTimestamp();
            if (now - _windowStart >= _windowTicks) { _windowStart = now; _count = 0; }   // window resets
            if (_count >= _maxPerWindow) return false;    // strictly less than the limit may run
            _count++;
        }

        Exception last = null;
        for (int attempt = 0; attempt <= _maxRetries; attempt++) {     // retries, not attempts
            ct.ThrowIfCancellationRequested();
            try { job(); return true; }
            catch (OperationCanceledException) { throw; }              // cancellation is not a failure
            catch (Exception ex) { last = ex; }
        }
        throw new JobFailedException($"job failed after {_maxRetries + 1} attempts", last);
    }
}''',
  complexity='Admission is O(1) under a short lock; the retry loop is bounded by `maxRetries + 1`. The lock covers only the '
             'counter, not the job execution — running the job inside the lock would serialise every caller, which is the '
             'performance bug people add while fixing the correctness ones.',
  follow=['Why not run the job inside the lock? (It would serialise everything and hold the lock across arbitrary user code.)',
          'Is a fixed window the right policy? A burst at the boundary can admit 2× the limit — offer a sliding window or token bucket.',
          'How would you make it async without blocking a thread pool thread? (`SemaphoreSlim` instead of `lock`.)',
          'How do you test the window reset deterministically? (Inject a time provider — another extensibility seam.)'],
  optimise='Inject an `ITimeProvider` so the window is testable without sleeping, and consider `Interlocked` on the counter if '
           'profiling shows lock contention — but only after measuring, and only if the window reset can still be made atomic.',
  evalpts=['Did you read the whole class before editing?',
           'Did you name each defect as a defect, with the reason?',
           'Did you find the silent ones (window never resets, cancellation swallowed)?',
           'Did you state the contract in a comment or docstring?',
           'Did you avoid the new bug of holding the lock across the job?',
           'Did you say how each fix would be tested?']),

 dict(id='extensible', title='Make it extensible: a notification dispatcher that keeps growing', level='med',
  topic='Abstraction · Modularity · Design in code',
  why='The pack says the Staff Coding module is about **modularity and extensibility** — day-to-day coding after the design is '
      'settled. This drill is the shape that keeps appearing: one class that a new requirement is about to break.',
  question='Here is a dispatcher that sends notifications by email. Product now wants push and SMS, per-channel retry rules, '
           'per-user quiet hours, and the ability to add a channel without touching the dispatcher. Refactor it.',
  think='Where is the seam? What is stable (dispatch, ordering, quotas) and what varies (channels, formatting, retry policy)? '
        'How do you avoid a switch statement that grows forever — and how do you keep the change small enough to review?',
  approach='Separate the stable pipeline from the varying parts: a channel becomes a plug-in registered by name, formatting '
           'lives with the channel, and cross-cutting rules (quiet hours, quotas, retries) sit in the pipeline where they apply '
           'to every channel exactly once.\n\n'
           'Say the rule out loud: **the dispatcher should not need editing to add a channel.** That is the testable definition '
           'of "extensible" here, and it is what the interviewer is listening for.',
  edges=['An unknown channel name → fail loudly at registration, not silently at send time.',
         'A channel that is down → per-channel retry and isolation, so email failure does not block push.',
         'Quiet hours across time zones — whose clock?',
         'A user with no address for a channel → skip that channel, not the whole notification.',
         'Duplicate sends after a retry → idempotency key per (user, notification, channel).'],
  code='''public interface INotificationChannel {
    string Name { get; }                                   // "email", "push", "sms"
    bool CanDeliver(Recipient r);                          // has an address/token for this channel
    Task<DeliveryResult> SendAsync(Recipient r, Notification n, CancellationToken ct);
    RetryPolicy Retry { get; }                             // varies per channel
}

public sealed class Dispatcher {
    private readonly IReadOnlyDictionary<string, INotificationChannel> _channels;
    private readonly IQuietHours _quietHours;              // cross-cutting, applied once
    private readonly IQuota _quota;
    private readonly IClock _clock;

    public Dispatcher(IEnumerable<INotificationChannel> channels, IQuietHours quietHours, IQuota quota, IClock clock) {
        _channels = channels.ToDictionary(c => c.Name, StringComparer.OrdinalIgnoreCase);
        _quietHours = quietHours; _quota = quota; _clock = clock;
    }

    public async Task<IReadOnlyList<DeliveryResult>> DispatchAsync(
            Notification n, Recipient r, IReadOnlyList<string> channelNames, CancellationToken ct) {

        var results = new List<DeliveryResult>();
        foreach (var name in channelNames) {
            if (!_channels.TryGetValue(name, out var channel))
                throw new InvalidOperationException($"unknown channel '{name}'");   // loud, at the boundary

            if (!channel.CanDeliver(r))                    { results.Add(DeliveryResult.Skipped(name, "no address")); continue; }
            if (_quietHours.IsQuiet(r, _clock.UtcNow) && !n.BypassesQuietHours)
                                                           { results.Add(DeliveryResult.Deferred(name)); continue; }
            if (!_quota.TryConsume(r, name))               { results.Add(DeliveryResult.Suppressed(name, "quota")); continue; }

            results.Add(await SendWithRetryAsync(channel, r, n, ct));   // one channel failing cannot block the others
        }
        return results;
    }

    private static async Task<DeliveryResult> SendWithRetryAsync(
            INotificationChannel channel, Recipient r, Notification n, CancellationToken ct) {
        for (int attempt = 0; ; attempt++) {
            try { return await channel.SendAsync(r, n, ct); }
            catch (OperationCanceledException) { throw; }
            catch (Exception ex) when (channel.Retry.ShouldRetry(attempt, ex)) {
                await Task.Delay(channel.Retry.Backoff(attempt), ct);
            }
            catch (Exception ex) { return DeliveryResult.Failed(channel.Name, ex); }
        }
    }
}''',
  complexity='Linear in the number of channels requested; each channel does its own IO. The important property is not Big-O — '
             'it is that adding a channel touches one new file and the registration, and nothing else.',
  follow=['How do you add a channel now? (Implement the interface, register it. The dispatcher does not change.)',
          'Where would you put templating and localisation? (With the channel, or a formatter injected into it — justify.)',
          'How do you send to all channels in parallel while keeping per-channel isolation? (`Task.WhenAll` over independent tasks, aggregate results.)',
          'Where does deduplication live — dispatcher or channel? (Dispatcher: it is cross-cutting, like quotas.)',
          'How do you test this without real providers? (A fake channel that records calls, plus an injected clock.)'],
  optimise='Parallelise across channels once ordering does not matter, and batch per channel where the provider supports it. '
           'Both are local changes because the pipeline and the channels are already separate.',
  evalpts=['Did you identify the seam (channel) before writing code?',
           'Can a new channel be added without editing the dispatcher?',
           'Are cross-cutting rules applied once rather than per channel?',
           'Did you keep failures isolated per channel?',
           'Did you inject the clock so quiet hours are testable?',
           'Did you keep it simple rather than clever — no reflection, no over-abstraction?']),
]
