// Q15 — a task manager over a dependency graph.
public interface ITask {
    string GetId();
    IList<ITask> GetSubTasks();     // these must all finish before the task itself can run
}

public class CycleException : Exception {
    public IReadOnlyList<string> Cycle { get; }
    public CycleException(IReadOnlyList<string> cycle)
        : base("Adding this task creates a cycle: " + string.Join(" -> ", cycle)) { Cycle = cycle; }
}

public class TaskManager {

    private readonly Dictionary<string, ITask> _tasks = new(StringComparer.Ordinal);
    private readonly Dictionary<string, List<string>> _dependsOn = new(StringComparer.Ordinal);
    private readonly Dictionary<string, List<string>> _blocks    = new(StringComparer.Ordinal);
    private readonly Dictionary<string, int> _outstanding = new(StringComparer.Ordinal);
    private readonly Queue<string> _ready = new();
    private readonly HashSet<string> _queued    = new(StringComparer.Ordinal);   // in _ready right now
    private readonly HashSet<string> _issued    = new(StringComparer.Ordinal);   // handed out already
    private readonly HashSet<string> _completed = new(StringComparer.Ordinal);

    public int ReadyCount => _ready.Count;
    public int TaskCount  => _tasks.Count;

    /// Registers the task and every subtask reachable from it.
    /// Throws CycleException and changes nothing if the result would contain a cycle.
    public void AddTask(ITask task) {
        if (task == null) throw new ArgumentNullException(nameof(task));

        // ---- phase 1: collect the new material without touching any field
        var newTasks = new Dictionary<string, ITask>(StringComparer.Ordinal);
        var newEdges = new Dictionary<string, List<string>>(StringComparer.Ordinal);
        Collect(task, newTasks, newEdges);

        // ---- phase 2: cycle-check the MERGED graph, still without committing
        // The merged graph is the UNION of both edge sets. Overwriting instead of unioning was a
        // real bug: re-adding an existing task with new subtasks would drop its original edges,
        // and a cycle closed across two AddTask calls would go undetected.
        var merged = new Dictionary<string, List<string>>(StringComparer.Ordinal);
        foreach (var kv in _dependsOn) merged[kv.Key] = new List<string>(kv.Value);
        foreach (var kv in newEdges) {
            if (!merged.TryGetValue(kv.Key, out var deps)) merged[kv.Key] = deps = new List<string>();
            foreach (string d in kv.Value) if (!deps.Contains(d)) deps.Add(d);
        }

        var cycle = FindCycleFrom(task.GetId(), merged);
        if (cycle != null) throw new CycleException(cycle);

        // Adding a dependency to a task that has already been handed out or finished is
        // ambiguous: re-run it, or leave it? Refuse rather than silently pick one.
        foreach (var kv in newEdges) {
            if (!_issued.Contains(kv.Key) && !_completed.Contains(kv.Key)) continue;
            List<string> known = _dependsOn[kv.Key];
            foreach (string dep in kv.Value)
                if (!known.Contains(dep))
                    throw new InvalidOperationException(
                        $"Task '{kv.Key}' has already been issued; cannot add dependency '{dep}'.");
        }

        // ---- phase 3: commit. Nothing below can fail, so the manager is never half-updated.
        foreach (var kv in newTasks) {
            if (_tasks.ContainsKey(kv.Key)) continue;      // already registered; keep its state
            _tasks[kv.Key]       = kv.Value;
            _dependsOn[kv.Key]   = new List<string>();
            _outstanding[kv.Key] = 0;
        }

        foreach (var kv in newEdges) {
            string id = kv.Key;
            List<string> known = _dependsOn[id];

            foreach (string dep in kv.Value) {
                if (known.Contains(dep)) continue;         // the same edge declared twice
                known.Add(dep);

                if (!_blocks.TryGetValue(dep, out var waiting)) _blocks[dep] = waiting = new List<string>();
                waiting.Add(id);

                if (!_completed.Contains(dep)) _outstanding[id]++;
            }
        }

        foreach (string id in newTasks.Keys)
            if (_outstanding[id] == 0) MarkReady(id);
    }

    private void MarkReady(string id) {
        if (_issued.Contains(id) || _completed.Contains(id)) return;
        if (_queued.Add(id)) _ready.Enqueue(id);           // never queue the same task twice
    }

    /// The next task whose subtasks have all completed, or null if none is runnable right now.
    /// null and "nothing left" are different states: use TaskCount and _completed to tell them apart.
    public ITask PollNextTask() {
        while (_ready.Count > 0) {
            string id = _ready.Dequeue();
            _queued.Remove(id);

            if (_completed.Contains(id)) continue;
            if (_outstanding[id] > 0)    continue;   // gained a dependency after being queued
            if (!_issued.Add(id))        continue;   // already handed to a worker

            return _tasks[id];
        }
        return null;
    }

    /// The interface as given has no completion signal, so nothing would ever become runnable
    /// after the first batch. This is the missing half.
    public void CompleteTask(string id) {
        if (!_tasks.ContainsKey(id)) throw new KeyNotFoundException(id);
        if (!_completed.Add(id)) return;                  // idempotent: a retry must be harmless

        if (!_blocks.TryGetValue(id, out var waiting)) return;

        foreach (string waiter in waiting)
            if (--_outstanding[waiter] == 0) MarkReady(waiter);
    }

    /// A worker that failed must hand the task back, or it is issued once and lost.
    public void RequeueTask(string id) {
        if (!_tasks.ContainsKey(id)) throw new KeyNotFoundException(id);
        if (_completed.Contains(id)) return;
        _issued.Remove(id);
        if (_outstanding[id] == 0) MarkReady(id);
    }

    // Iterative walk of the new subtree. Iterative on purpose: a deep chain would blow the
    // stack in a recursive version, and dependency chains are exactly the shape that gets deep.
    private static void Collect(ITask root, Dictionary<string, ITask> tasks,
                                Dictionary<string, List<string>> edges) {
        var stack = new Stack<ITask>();
        stack.Push(root);

        while (stack.Count > 0) {
            ITask cur = stack.Pop();
            string id = cur.GetId();
            if (id == null) throw new ArgumentException("Task id must not be null.");
            if (tasks.ContainsKey(id)) continue;

            tasks[id] = cur;
            var deps = new List<string>();

            foreach (ITask sub in cur.GetSubTasks() ?? new List<ITask>()) {
                if (sub == null) continue;
                deps.Add(sub.GetId());
                stack.Push(sub);
            }
            edges[id] = deps;
        }
    }

    // Three-colour DFS. Grey means "on the current path", so meeting grey is a back edge.
    private static List<string> FindCycleFrom(string start, Dictionary<string, List<string>> edges) {
        var state = new Dictionary<string, int>(StringComparer.Ordinal);   // 1 = grey, 2 = black
        var path  = new List<string>();

        bool Visit(string id) {
            state[id] = 1;
            path.Add(id);

            if (edges.TryGetValue(id, out var deps))
                foreach (string next in deps) {
                    state.TryGetValue(next, out int s);
                    if (s == 1) { path.Add(next); return true; }        // back edge
                    if (s == 0 && Visit(next)) return true;
                }

            state[id] = 2;
            path.RemoveAt(path.Count - 1);
            return false;
        }

        if (!Visit(start)) return null;

        int first = path.IndexOf(path[^1]);                              // trim the tail to the loop
        return path.GetRange(first, path.Count - first);
    }
}
