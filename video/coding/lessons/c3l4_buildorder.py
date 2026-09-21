# -*- coding: utf-8 -*-
"""Chapter 3, Lesson 4 — getBuildOrder: topological sort, cycles and waves."""
from lib import *

DAG = {'a': (200, 180, 'A'), 'b': (200, 420, 'B'), 'c': (560, 180, 'C'), 'd': (560, 420, 'D'),
       'e': (920, 300, 'E'), 'f': (1280, 300, 'F')}
DEDGES = [('a', 'c'), ('b', 'c'), ('b', 'd'), ('c', 'e'), ('d', 'e'), ('e', 'f')]

lesson_header('3.4', 'getBuildOrder — topological sort, cycles and parallel waves', 'Graphs · topological sort',
              'High', 'Blind infra report (Sep 2025) + Glassdoor', '2025', 'High', 17,
              """Chapter three, lesson four. Implement get build order. This was reported first-hand by a candidate """
              """interviewing for Senior Software Engineer, Infrastructure at LinkedIn in September 2025, and the same package """
              """build-order problem shows up in Glassdoor summaries, so two independent sources. Two things make this lesson """
              """different from a textbook topological sort. First, the input is a function, not a graph — you have to build """
              """the graph yourself, and there is a bug waiting in how you do it. Second, the two follow-ups are where the """
              """interview actually is, and both of them are things a real build system needs.""")

# ---------------------------------------------------------------- question
sid = beat('Question', 'The question, as reported',
           '<div class="qwrap"><div class="qtext" style="font-size:38px;line-height:1.35">'
           'You are given <code>GetDependencies(target)</code>, which returns the things a target depends on.<br><br>'
           'Implement <code>GetBuildOrder(targets)</code> — an order in which every target can be built after everything it '
           'depends on.</div></div>',
           """Here is the question as it was reported. You have a function, get dependencies, which tells you what a given """
           """target depends on. Implement get build order: produce an order in which every target can be built after """
           """everything it needs. Note the shape of the input — a function you call, not a data structure you were handed. """
           """That matters, and we will come back to it.""")

# ---------------------------------------------------------------- think
think('Given GetDependencies(target), implement GetBuildOrder(targets). What do you return when there is a cycle?', 30,
      """Pause. Three questions to answer out loud. How do you discover the graph when all you have is a function? What is """
      """your algorithm? And what do you return when the dependencies contain a cycle — because a build system with a """
      """circular dependency is a real situation, not a trick.""",
      """Good. Let us build it, and I will show you the bug that almost everyone ships in the graph-construction step — """
      """including versions the textbooks print.""")

# ---------------------------------------------------------------- kahn
D = Diagram("Kahn's algorithm: peel off what is ready")
graph(D, DAG, DEDGES, step=0, node_w=120, node_h=80)
D.label(120, 560, 'In-degree = how many things I am still waiting for.', kind='info', step=1, w=1700, size='m', align='center')
D.label(120, 630, 'A: 0   B: 0   C: 2   D: 1   E: 2   F: 1', kind='dp', step=1, w=1700, size='m', align='center')
D.label(120, 700, 'Take everything at 0 → that is a **wave**. Remove it, decrement its dependents, repeat.',
        kind='ok', step=2, w=1700, size='m', align='center')
D.label(120, 770, 'If the queue empties with nodes left over, those nodes are **on or after a cycle**.',
        kind='deny', step=3, w=1700, size='m', align='center')
sid = D.build()
seg(sid, 0, """Here is a small dependency graph. An arrow from A to C means C depends on A — so A has to be built first.""")
seg(sid, 1, """Kahn's algorithm works on in-degree, which in this problem has a very concrete meaning: how many things am I """
            """still waiting for? A and B wait for nothing, so their in-degree is zero. C waits for A and B, so two.""")
seg(sid, 2, """Then the loop. Take everything whose in-degree is zero — those can be built right now. Remove them, decrement """
            """the in-degree of everything that depended on them, and repeat. That is it.""")
seg(sid, 3, """And this is the elegant part. If the process stops while some nodes still have a non-zero in-degree, those nodes """
            """are exactly the ones on or downstream of a cycle. You get cycle detection for free, and more usefully, you get """
            """the identity of the cycle — which is what a build engineer actually needs.""")

# ---------------------------------------------------------------- the bug
sid = compare('The bug almost everyone ships',
 ('`List<string>` for the adjacency', 'deny', 0, ['A duplicate dependency is counted twice',
                                                  'In-degree for that node is now too high',
                                                  'It never reaches zero, so it is never emitted',
                                                  '**Looks exactly like a cycle** — and you will debug the wrong thing']),
 ('`HashSet<string>` for the adjacency', 'ok', 1, ['`set.Add` returns false for a repeat',
                                                   'Count the edge only when it is new',
                                                   'Duplicate declarations become harmless',
                                                   'One character of difference; hours of debugging saved']))
seg(sid, 0, """Now the bug, and I want to dwell on it because it is the thing that separates careful code from code that """
            """compiles. Suppose a target declares the same dependency twice — which happens constantly in real build files, """
            """through transitive includes or a copy-paste. If your adjacency structure is a list, you count that edge twice, """
            """so the dependent node's in-degree is one higher than it should be. It never reaches zero. It is never emitted. """
            """And your cycle-detection logic then reports a cycle that does not exist.""")
seg(sid, 1, """The fix is a hash set for the dependents, and counting the edge only when the add actually inserts something. """
            """One data-structure choice, and a whole class of phantom cycles disappears. If you spot that in an interview """
            """unprompted, say why you are doing it — it is a small thing that signals you have debugged real systems.""")

# ---------------------------------------------------------------- code
CODE = '''public IReadOnlyList<IReadOnlyList<string>> GetBuildWaves(IEnumerable<string> targets) {
    var dependents = new Dictionary<string, HashSet<string>>();   // dep -> things waiting on it
    var indegree   = new Dictionary<string, int>();
    var seen       = new HashSet<string>();
    var pending    = new Stack<string>(targets);

    // 1. Discover the graph lazily through GetDependencies
    while (pending.Count > 0) {
        var node = pending.Pop();
        if (!seen.Add(node)) continue;
        indegree.TryAdd(node, 0);

        foreach (var dep in GetDependencies(node)) {
            if (dep == node) throw new InvalidOperationException($"self-dependency on '{node}'");
            if (!dependents.TryGetValue(dep, out var set)) dependents[dep] = set = new HashSet<string>();
            if (set.Add(node)) indegree[node] = indegree.GetValueOrDefault(node) + 1;  // only NEW edges count
            pending.Push(dep);
        }
    }

    // 2. Peel off waves of ready targets
    var ready = indegree.Where(kv => kv.Value == 0).Select(kv => kv.Key)
                        .OrderBy(x => x, StringComparer.Ordinal).ToList();
    var waves = new List<IReadOnlyList<string>>();
    int emitted = 0;

    while (ready.Count > 0) {
        waves.Add(ready);
        emitted += ready.Count;

        var next = new List<string>();
        foreach (var done in ready)
            foreach (var waiting in dependents.GetValueOrDefault(done, new HashSet<string>()))
                if (--indegree[waiting] == 0) next.Add(waiting);

        next.Sort(StringComparer.Ordinal);     // deterministic output for reproducible builds
        ready = next;
    }

    if (emitted != indegree.Count)
        throw new InvalidOperationException("dependency cycle involves: " +
            string.Join(", ", indegree.Where(kv => kv.Value > 0).Select(kv => kv.Key).OrderBy(x => x)));

    return waves;
}'''
code_slide('The C# implementation', CODE, [
 ('1-5', """The signature returns waves — a list of lists — rather than a flat order, and I will justify that in a moment. """
           """Note `dependents` maps a dependency to the set of things waiting on it. That direction confuses people, so say """
           """it out loud as you write it: the key is the thing that must be built first."""),
 ('7-11', """Graph discovery. We start from the requested targets and walk outward with an explicit stack, not recursion, """
            """because a dependency chain can be thousands deep. `seen.Add` returning false means we already processed this """
            """node, so we skip it."""),
 ('13-19', """For each dependency we check for a self-dependency, which is a cycle of length one and is worth failing on """
             """explicitly. Then this line is the fix we just discussed: `set.Add` returns true only if the edge is new, so a """
             """duplicate declaration does not inflate the in-degree."""),
 ('22-26', """Now the peeling. Everything at in-degree zero forms the first wave. Sorting makes the output deterministic — """
             """which matters more than it sounds, because a build system that produces a different order on each run makes """
             """caching and reproducibility impossible."""),
 ('28-36', """Each round: record the current wave, then decrement every waiting node. When a node's counter hits zero, it """
             """joins the next wave. Note the decrement and the test are one expression, so a node can only ever be added """
             """once."""),
 ('38-41', """And the cycle report. If we emitted fewer nodes than we discovered, the remainder is exactly the nodes still """
             """blocked — so we name them. Not "cycle detected". The actual list. That is the difference between an error """
             """message that helps and one that starts a bug hunt."""),
])

# ---------------------------------------------------------------- waves
D = Diagram('Why waves, not a flat list')
D.box('w1', 160, 170, 420, 110, 'Wave 1', 'A, B', kind='ok', step=0, small=True)
D.box('w2', 640, 170, 420, 110, 'Wave 2', 'C, D', kind='ok', step=1, small=True)
D.box('w3', 1120, 170, 420, 110, 'Wave 3', 'E', kind='ok', step=2, small=True)
D.box('w4', 1120, 320, 420, 110, 'Wave 4', 'F', kind='ok', step=3, small=True)
D.label(160, 490, 'A flat order says: build A, then B, then C…  — **one at a time**.', kind='com', step=4, w=1600, size='m')
D.label(160, 570, 'Waves say: A and B can build **in parallel**. Then C and D. Then E. Then F.', kind='ok', step=5, w=1600, size='m')
D.label(160, 670, 'Same algorithm. One extra list. And it is the thing a real build system needs.',
        kind='dp', step=6, w=1600, size='l')
sid = D.build()
seg(sid, 0, """Now the follow-up that makes this answer stand out, and I want you to volunteer it rather than wait. Wave one: """
            """A and B.""")
seg(sid, 1, """Wave two: C and D.""")
seg(sid, 2, """Wave three: E.""")
seg(sid, 3, """Wave four: F.""")
seg(sid, 4, """A flat topological order would say build A, then B, then C, and so on — implying one at a time.""")
seg(sid, 5, """But everything in a wave has no dependency on anything else in that wave, by construction. So A and B can build """
            """in parallel. That is not an extra algorithm; it falls straight out of Kahn's structure.""")
seg(sid, 6, """Same algorithm, one extra list, and now your answer is what a real build system actually needs. And if you have """
            """ever sequenced a migration across teams, this is the same shape: everything at in-degree zero can move """
            """simultaneously — which is exactly how a large platform migration gets planned.""")

# ---------------------------------------------------------------- edges + complexity
sid = cards('Edge cases', [
 (0, 'Duplicate dependencies', 'The HashSet fix. Otherwise a phantom cycle.', 'deny'),
 (0, 'Self-dependency', 'A cycle of length one — fail explicitly with the name.', 'deny'),
 (1, 'Disconnected components', 'Several roots; waves contain nodes from all of them. Perfectly valid.', 'info'),
 (1, 'A target that does not exist', 'Does GetDependencies throw or return empty? Ask, then handle it.', 'shared'),
 (2, 'Very deep chains', 'Explicit stack, not recursion — say why as you write it.', 'ok'),
 (2, 'Non-deterministic order', 'Dictionary iteration order varies; sort each wave for reproducibility.', 'ok'),
], cols=2)
seg(sid, 0, """Edge cases. Duplicate dependencies and self-dependencies we have covered, and both produce something that looks """
            """like a cycle if you are careless.""")
seg(sid, 1, """Disconnected components are fine and normal — several independent roots, and waves will contain nodes from all """
            """of them. A target that does not exist is a contract question: does get dependencies throw, or return empty? """
            """Ask, and handle whichever they say.""")
seg(sid, 2, """Deep chains mean an explicit stack. And the determinism point is worth making unprompted: dictionary iteration """
            """order is not guaranteed, so without sorting, two runs can produce different valid orders. For a build system """
            """that breaks caching and makes failures irreproducible.""")

sid = table('Complexity', ['', 'Answer', 'Say it like this'], [
 (0, ['Time', 'O(V + E)', 'Every node discovered once, every edge relaxed once'], [None, 'ok', None]),
 (1, ['With sorting', 'O(V log V + E)', 'Sorting each wave; worth it for reproducibility'], [None, 'info', None]),
 (2, ['Space', 'O(V + E)', 'The adjacency sets plus the in-degree map'], [None, 'info', None]),
 (3, ['GetDependencies calls', 'Exactly once per node', 'Because of the seen set — say so if the call is expensive'], [None, 'ok', None]),
], widths=[26, 22, 52])
seg(sid, 0, """Complexity. Order V plus E: each node is discovered once and each edge is relaxed once.""")
seg(sid, 1, """The sorting adds a log factor per wave, and I would pay it and say why.""")
seg(sid, 2, """Space is the adjacency sets plus the in-degree map.""")
seg(sid, 3, """And here is a dimension people forget entirely: how many times do you call get dependencies? Exactly once per """
            """node, because of the seen set. If that function is a network call or reads a file, that count is the real cost """
            """of your algorithm — and noticing that the expensive operation is the API call rather than the CPU work is """
            """exactly the instinct the infrastructure interview is looking for.""")

followups(
 ['"Report the cycle, not just that one exists" — name the blocked nodes',
  '"Produce parallel build waves" — the follow-up this design already answers',
  '"Make it deterministic" — sort each wave'],
 ['"One dependency changed — what is the minimal rebuild set?" — BFS over the dependents map, which you already have',
  '"Cap parallelism at N workers" — waves become a scheduling problem; largest-first within a wave',
  '"GetDependencies is a remote call that sometimes fails" — cache, retry with backoff, and decide whether a partial graph can be trusted'],
 """Follow-ups. Reporting the cycle members, emitting waves, and determinism are all things this implementation already """
 """does — which is why I wrote it that way from the start rather than adding them under pressure.""",
 """The staff-level ones move toward the real system. Incremental rebuild: one dependency changed, what is the minimum set """
 """to rebuild? That is a breadth-first search over the dependents map — the map you already built, walked in the other """
 """direction. Capping parallelism turns a wave into a scheduling problem, where you would want to start the longest jobs """
 """first. And the best one: what if get dependencies is a remote call that sometimes fails? Now you need caching, retries """
 """with backoff, and a decision about whether a partially discovered graph can be trusted at all — and the honest answer """
 """is no, because a missing edge produces a build order that is silently wrong. Say that. Refusing to proceed on partial """
 """data is the kind of judgement this round is scoring.""")

interview_script([
 '"Edges point from dependency to dependent, so in-degree means how many things I am still waiting for."',
 '"I will discover the graph lazily from the requested targets, with an explicit stack — chains can be deep."',
 '"I am using a HashSet for the dependents so a duplicate declaration does not inflate the in-degree and look like a cycle."',
 '"Kahn: everything at in-degree zero is ready. I will emit those as a wave rather than one at a time, because they can build in parallel."',
 '"If the emitted count is less than the node count, the remaining nodes are the cycle — and I will name them, not just report one."',
 '"O(V+E), and exactly one GetDependencies call per node, which matters if that call is remote."',
 '"I sort each wave so the order is reproducible across runs — otherwise build caching breaks."',
], [
 """The script. Start by stating the edge direction, because that is where wrong answers begin, and define in-degree in the """
 """problem's own language rather than graph-theory language.""",
 """Then lazy discovery with an explicit stack, and the HashSet decision with its reason attached. Saying "so a duplicate """
 """does not look like a cycle" in the same breath as the data-structure choice is a compact way to show you have seen this """
 """fail before.""",
 """Then Kahn with waves volunteered, cycles reported by name, the complexity including the API-call count, and """
 """determinism justified by build caching. Every one of those is a small production insight rather than an algorithmic """
 """one — which is precisely the flavour of this round.""",
])

sid = statement('Chapter 3 in one line', 'Model first, traverse second — and design for the follow-up.',
                'Word Ladder: find the graph. The Maze: reject the obvious graph. Degrees: bound the frontier. Build order: build the graph correctly.',
                kind='ok')
seg(sid, 0, """That is chapter three. One line to hold it together: model first, traverse second.""")
seg(sid, 1, """Word Ladder was about finding a graph nobody gave you. The Maze was about rejecting the obvious graph. Degrees of """
            """connection was about bounding a frontier that would otherwise eat the whole product. And build order was about """
            """constructing the graph correctly, where one data-structure choice decides whether your cycle detection tells """
            """the truth. In every one of them the traversal itself was textbook — the interview was in the modelling. Next """
            """up is the chapter recap, with the templates and a mini mock. See you there.""")
