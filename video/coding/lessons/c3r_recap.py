# -*- coding: utf-8 -*-
"""Chapter 3 recap — graphs, BFS and ordering."""
from lib import *

lesson_header('3.R', 'Chapter 3 recap: graphs, BFS and ordering', 'Recap · templates · mini mock',
              'Highest', 'Word Ladder, The Maze, minimum degree of connection, build order', '2026', 'High', 14,
              """Chapter three recap. This is the densest chapter in the course for reported questions — Word Ladder, The """
              """Maze, minimum degree of connection and build order all came from your own list or from first-hand """
              """write-ups, and LinkedIn is a graph company, so this is not a coincidence. Same seven parts as before: """
              """pattern, recognition, mistakes, templates, ranked questions, rapid revision, mini mock.""")

# ------------------------------------------------------------------ 1. pattern
sid = beat('Pattern summary', 'The chapter in one page',
           '<div class="bigidea">Every graph problem in this chapter was solved by answering two questions: '
           '<b>what is a node, and what is an edge?</b></div>'
           '<div style="margin-top:26px;font-size:30px;line-height:1.7">'
           'Get those right and the algorithm is almost always already known to you. Get them wrong &mdash; a cell instead of '
           'a cell-plus-direction, a word instead of a wildcard pattern &mdash; and no amount of correct BFS will save you.</div>',
           """One page. Every problem in this chapter came down to two questions: what is a node, and what is an edge. That is """
           """it. Once the graph is defined properly the algorithm is something you already know — breadth-first search, or a """
           """topological sort. But if you model it wrong, and the two classic wrong models are a maze cell instead of a cell """
           """plus a direction, and a word instead of a wildcard pattern, then no amount of perfectly written breadth-first """
           """search will rescue you. The modelling is the interview.""", step=0)
seg(sid, 1, """So in a real round, say the node and the edge out loud before you write anything. It is the single highest-value """
            """sentence you can say in a graph question.""")

sid = table('The four problems, and how each defined its graph',
 ['Problem', 'Node', 'Edge', 'Algorithm'],
 [(0, ['Word Ladder', 'a word', 'one letter differs &mdash; found via **wildcard buckets**, not pairwise', 'BFS, bidirectional'], None),
  (1, ['The Maze', 'a stopping cell (ball rolls until a wall)', 'a roll in one of four directions', 'BFS / DFS on stops'], None),
  (2, ['Minimum degree of connection', 'a member', 'a connection, undirected', '**Bidirectional BFS** + parent map'], None),
  (3, ['Build order', 'a build target', 'a dependency, directed', 'Kahn&rsquo;s topological sort'], None)],
 widths=[26, 24, 34, 16])
seg(sid, 0, """Word Ladder: the node is a word, and the edge is one letter differing — but you find those edges through """
            """wildcard buckets rather than comparing every pair of words, which is the difference between passing and timing """
            """out.""")
seg(sid, 1, """The Maze: the node is not a cell, it is a stopping cell, because the ball rolls until it hits a wall. Get that """
            """wrong and you have solved a different, easier problem.""")
seg(sid, 2, """Minimum degree of connection: a member and an undirected connection — the LinkedIn question, essentially — solved """
            """with bidirectional breadth-first search, and with a parent map so you can answer the reported follow-up, which """
            """was to return the path rather than just the distance.""")
seg(sid, 3, """And build order: a target and a directed dependency, solved with Kahn's topological sort, where the queue of """
            """zero-in-degree nodes is also your parallelism answer.""")

# ------------------------------------------------------------------ 2. recognition
sid = steps_list('Recognition checklist',
 [(0, '&ldquo;shortest / fewest / minimum number of steps&rdquo; on an **unweighted** graph &rarr; **BFS**, never DFS', 'ok'),
  (0, 'Both endpoints known and the graph branches hard &rarr; **bidirectional BFS**; frontier sizes roughly b^(d/2) not b^d', 'ok'),
  (1, '&ldquo;return the path, not just the length&rdquo; &rarr; keep a **parent map** as you go; never store paths in the queue', 'ok'),
  (1, '&ldquo;order / dependencies / prerequisites / must come before&rdquo; &rarr; **topological sort**; cycle detection is free', 'ok'),
  (2, '&ldquo;how many can run in parallel&rdquo; &rarr; the **size of each Kahn wave**', 'ok'),
  (2, 'Movement with momentum, sliding, or rolling &rarr; the node carries **state beyond position**', 'shared'),
  (3, 'Implicit graph (words, board states, configurations) &rarr; **generate neighbours**, never build the edge list', 'shared'),
  (3, 'Weighted edges appear &rarr; BFS is wrong; say **Dijkstra**, and 0/1 weights means **0-1 BFS with a deque**', 'info')],
 numbered=False)
seg(sid, 0, """The recognition checklist. Shortest, fewest or minimum steps on an unweighted graph means breadth-first search, """
            """never depth-first — depth-first finds a path, not the shortest one. If both endpoints are known and the graph """
            """branches hard, bidirectional, because your frontier grows like b to the d over two instead of b to the d.""")
seg(sid, 1, """Return the path rather than the length means keep a parent map as you go, and it specifically does not mean """
            """putting whole paths in the queue, which is the memory mistake that shows up in every Word Ladder write-up. """
            """Order, dependencies, prerequisites or must-come-before means topological sort, where cycle detection comes for """
            """free.""")
seg(sid, 2, """How many can run in parallel is the size of each Kahn wave. And anything involving momentum, sliding or rolling """
            """means the node carries state beyond position.""")
seg(sid, 3, """An implicit graph — words, board states, configurations — means you generate neighbours on demand and never """
            """materialise the edge list. And the moment weights appear, breadth-first search is wrong: say Dijkstra, and if """
            """the weights are only zero and one, say zero-one breadth-first search with a deque. That last answer is a """
            """cheap way to sound like you have done this before.""")

# ------------------------------------------------------------------ 3. mistakes
sid = cards('The mistakes that actually cost people', [
 (0, 'DFS for a shortest path', 'It terminates and returns <i>a</i> path. Silently wrong, and it looks like it works on small inputs.', 'deny'),
 (0, 'Building the edge list pairwise', 'Word Ladder with n&sup2; comparisons is the classic timeout. Wildcard buckets make it linear in the word count.', 'deny'),
 (1, 'Marking visited on dequeue, not enqueue', 'Duplicates pile into the queue. On a dense graph this is the difference between fine and out of memory.', 'deny'),
 (1, 'Storing paths in the queue', 'O(V&middot;path) memory instead of O(V). Parent map, then reconstruct once.', 'deny'),
 (2, 'Bidirectional BFS expanded from the wrong side', 'Always expand the **smaller** frontier, and check intersection at the right moment or you report a distance that is off by one.', 'deny'),
 (2, 'Topological sort without a cycle check', 'If fewer nodes come out than went in, there is a cycle &mdash; and that is usually the follow-up.', 'shared'),
], cols=2)
seg(sid, 0, """The mistakes. Using depth-first search for a shortest path — it terminates, it returns a path, and it looks correct """
            """on any small example you try. Building the edge list pairwise, which is the Word Ladder timeout everyone """
            """reports.""")
seg(sid, 1, """Marking visited when you dequeue rather than when you enqueue, so duplicates pile up in the queue. And storing """
            """whole paths in the queue instead of keeping a parent map.""")
seg(sid, 2, """On bidirectional search, expanding the wrong side — you always expand the smaller frontier — and getting the """
            """intersection check in the wrong place, which gives you a distance that is off by one. And finally, a """
            """topological sort with no cycle check. If fewer nodes come out than went in, there is a cycle, and being asked """
            """about cycles is not a possibility, it is the follow-up.""")

# ------------------------------------------------------------------ 4. templates
T1 = '''// TEMPLATE D - level-counting BFS on an implicit graph.
int ShortestSteps(string start, string end, HashSet<string> allowed) {
    if (!allowed.Contains(end)) return 0;

    var queue = new Queue<string>(); queue.Enqueue(start);
    var seen  = new HashSet<string> { start };              // mark on ENQUEUE
    int steps = 1;

    while (queue.Count > 0) {
        int size = queue.Count;                             // freeze the level
        for (int i = 0; i < size; i++) {
            var cur = queue.Dequeue();
            if (cur == end) return steps;
            foreach (var next in Neighbours(cur)) {         // generated, never stored
                if (allowed.Contains(next) && seen.Add(next)) queue.Enqueue(next);
            }
        }
        steps++;                                            // one increment per level
    }
    return 0;
}'''
code_slide('Template D &mdash; level-counting BFS', T1, [
 (None, """Template D. Three details carry it. Mark on enqueue, not on dequeue. Freeze the level size so that one increment """
          """of the step counter equals one level of the graph. And generate neighbours rather than storing edges, which is """
          """what makes this work on an implicit graph of words or board states that you could never materialise."""),
])

T2 = '''// TEMPLATE E - bidirectional BFS with a parent map, so you can return the PATH.
var fwd = new Dictionary<string,string> { [start] = null };   // node -> parent
var bwd = new Dictionary<string,string> { [end]   = null };
var a = new HashSet<string> { start };
var b = new HashSet<string> { end };

while (a.Count > 0 && b.Count > 0) {
    if (a.Count > b.Count) { (a, b) = (b, a); (fwd, bwd) = (bwd, fwd); }   // expand the SMALLER side

    var next = new HashSet<string>();
    foreach (var cur in a)
        foreach (var n in Neighbours(cur)) {
            if (bwd.ContainsKey(n)) return Stitch(fwd, bwd, cur, n);       // met in the middle
            if (fwd.ContainsKey(n)) continue;
            fwd[n] = cur; next.Add(n);
        }
    a = next;
}'''
code_slide('Template E &mdash; bidirectional BFS + parent map', T2, [
 (None, """Template E is the one I would practise writing cold, because it is the shape of the reported LinkedIn question. """
          """Two parent maps and two frontiers. Swap so you always expand the smaller side — that single line is where the """
          """speed-up lives. When a neighbour is already in the other side's map, the searches have met, and you stitch the """
          """two halves into one path: walk the forward parents back to the start, reverse, then walk the backward parents to """
          """the end. Returning the path was the actual follow-up, so the parent map is not optional."""),
])

T3 = '''// TEMPLATE F - Kahn's topological sort, with cycle detection and parallel waves.
var indeg = new Dictionary<string,int>();
foreach (var t in targets) indeg.TryAdd(t, 0);
foreach (var (from, to) in deps) { indeg[to] = indeg.GetValueOrDefault(to) + 1; adj[from].Add(to); }

var ready = new Queue<string>(indeg.Where(kv => kv.Value == 0).Select(kv => kv.Key));
var waves = new List<List<string>>();
int emitted = 0;

while (ready.Count > 0) {
    int size = ready.Count;                     // this whole wave can run in PARALLEL
    var wave = new List<string>(size);
    for (int i = 0; i < size; i++) {
        var cur = ready.Dequeue(); wave.Add(cur); emitted++;
        foreach (var next in adj[cur]) if (--indeg[next] == 0) ready.Enqueue(next);
    }
    waves.Add(wave);
}
if (emitted != indeg.Count) throw new InvalidOperationException("cycle: " + string.Join(",", Unemitted(indeg)));'''
code_slide('Template F &mdash; Kahn, with waves and cycle detection', T3, [
 (None, """And template F, Kahn's algorithm, written the way a staff candidate should write it. Notice it does three jobs at """
          """once with almost no extra code. It produces a valid order. Its level structure gives you the parallel waves, """
          """which is the answer to "how many of these can build at the same time". And the emitted count versus the node """
          """count detects a cycle — and rather than just throwing, it names the nodes still holding a non-zero in-degree, """
          """because "there is a cycle" is a much worse error message than "these four targets form a cycle". That last """
          """detail is a staff-level instinct and it costs one line."""),
])

# ------------------------------------------------------------------ 5. top reported
sid = table('The reported graph questions, ranked',
 ['#', 'Question', 'Evidence', 'Revise'],
 [(0, ['1', 'Minimum degree of connection (+ return the path)', 'Your own list, with the path follow-up stated', '**First**'], None),
  (0, ['2', 'Word Ladder', 'Your own list + LinkedIn tagged set, recurring', '**First**'], None),
  (1, ['3', 'The Maze', 'Your own list; rolling-ball variant', 'Second'], None),
  (1, ['4', 'Build order / dependency resolution', 'Reported as a Staff-level design-flavoured coding question', 'Second'], None),
  (2, ['5', 'Find the Celebrity', 'Your own list &mdash; graph-shaped, but an elimination argument (chapter 7)', 'With ch 7'], None),
  (2, ['&mdash;', 'Dijkstra, MST, articulation points', 'Not reported for LinkedIn &mdash; general preparation', 'If time'], 'dim')],
 widths=[6, 44, 38, 12])
seg(sid, 0, """Ranked. Minimum degree of connection first, and specifically with the path follow-up, because that is how it was """
            """reported. Word Ladder next — it recurs.""")
seg(sid, 1, """Then The Maze and build order.""")
seg(sid, 2, """Find the Celebrity is on your list and looks like a graph question, but it is really an elimination argument, so """
            """it lives in chapter seven and I would revise it there. And again the honest last row: Dijkstra, minimum """
            """spanning trees and articulation points are not reported for LinkedIn. Know Dijkstra well enough to name it when """
            """weights appear. Do not spend a week on articulation points.""")

# ------------------------------------------------------------------ 6. rapid revision
sid = steps_list('Five-minute rapid revision &mdash; say each of these out loud',
 [(0, 'What is a node? What is an edge? &mdash; before anything else', 'ok'),
  (0, 'Unweighted shortest path &rarr; BFS. Weighted &rarr; Dijkstra. 0/1 &rarr; deque BFS.', 'ok'),
  (1, 'Mark visited on enqueue. Freeze the level size. One increment per level.', 'ok'),
  (1, 'Path needed &rarr; parent map, reconstruct once at the end.', 'ok'),
  (2, 'Both ends known &rarr; bidirectional, always expand the smaller frontier.', 'shared'),
  (2, 'Neighbours generated, never an O(n&sup2;) edge build.', 'shared'),
  (3, 'Ordering &rarr; Kahn. Waves = parallelism. Emitted &ne; total = cycle, and name the nodes.', 'info'),
  (3, 'Disconnected graph, self-loop, duplicate edge, node absent from the graph.', 'info')],
 numbered=True)
seg(sid, 0, """Rapid revision, out loud. What is a node, what is an edge. Unweighted means breadth-first, weighted means """
            """Dijkstra, zero-one means a deque.""")
seg(sid, 1, """Mark on enqueue, freeze the level, one increment per level. Path needed means parent map and one reconstruction """
            """at the end.""")
seg(sid, 2, """Both ends known means bidirectional, expanding the smaller frontier. Neighbours generated, never an n-squared """
            """edge build.""")
seg(sid, 3, """Ordering means Kahn, waves are your parallelism answer, and emitted not equal to total means a cycle whose nodes """
            """you name. And the edge cases that get skipped: a disconnected graph, a self-loop, a duplicate edge, and a node """
            """that is not in the graph at all — which in the LinkedIn connection question means a member with no """
            """connections, and that is a real account state, not a hypothetical.""")

# ------------------------------------------------------------------ 7. mini mock
sid = beat('Mini mock &mdash; 15 minutes', 'Pause here and actually do it',
           '<div class="qwrap"><div class="qlabel">The interviewer asks</div>'
           '<div class="qtext" style="font-size:34px">&ldquo;Given a member and a set of skills, find the shortest '
           'introduction path to <b>anyone</b> who has all of those skills. Connections are undirected. Return the path. '
           'If several are equally short, prefer the one whose endpoint has the most skills in common beyond the required '
           'set.&rdquo;</div></div>',
           """Mini mock, fifteen minutes. Given a member and a set of skills, find the shortest introduction path to anyone """
           """who has all of those skills. Connections are undirected. Return the path. And if several are equally short, """
           """prefer the endpoint with the most skills in common beyond the required set. This is deliberately close to """
           """something LinkedIn would actually build. Pause, talk out loud, write real C sharp.""", kicker='Chapter 3 recap')
think('Fifteen minutes. Node, edge, algorithm, tie-break, path, complexity, edge cases.', 45,
      """Go. And I will tell you in advance that there is one modelling decision here that changes the whole answer, and one """
      """trap in the tie-break. If you find both, you are in good shape for this round.""",
      """Right. Here is the grading.""")

sid = cards('How I would grade that', [
 (0, '&ldquo;Anyone with all the skills&rdquo; = multi-target BFS', 'Not one BFS per candidate. One BFS from the member, stop at the first node satisfying the predicate. The target is a <b>test</b>, not an identity.', 'ok'),
 (0, 'Bidirectional does <i>not</i> apply cleanly here', 'You do not know the endpoint. You could seed the reverse side with <i>all</i> qualifying members &mdash; and saying that, then pricing it, is the strongest answer available.', 'deny'),
 (1, 'Tie-break is per level, not global', 'Finish the entire level in which the first match appears, collect every match at that distance, then rank. Returning the first match you dequeue is the trap.', 'deny'),
 (1, 'Path via parent map', 'Parent map, then walk back and reverse. Do not carry paths in the queue &mdash; a member can have thousands of connections.', 'ok'),
 (2, 'Clarifying questions I wanted to hear', 'Is the graph in memory or a service? Degree cap &mdash; do we search past 2nd or 3rd degree at all? Are blocked or private members traversable?', 'shared'),
 (2, 'Staff-level close', 'Real answer: precompute up to 2nd degree, cap the search, and treat the skill predicate as a filter over an index &mdash; not a BFS over the live social graph.', 'ok'),
], cols=2)
seg(sid, 0, """The modelling decision first. Anyone with all the skills means this is a multi-target breadth-first search — one """
            """search from the member, stopping at the first node that satisfies a predicate. The target is a test, not an """
            """identity. If you ran one search per candidate member, that is the mistake this question is built to catch.""")
seg(sid, 1, """And note that bidirectional search does not apply cleanly, because you do not know your endpoint. You could seed """
            """the reverse frontier with every qualifying member, and if you said that and then priced it honestly, that is """
            """the strongest answer available here — it shows you know the technique and know its precondition.""")
seg(sid, 2, """The trap is the tie-break. It is per level, not global. You must finish the entire level in which the first match """
            """appears, collect every match at that distance, and then rank them. Returning the first match you happen to """
            """dequeue is wrong, and it will pass a small test. Path comes from the parent map, not from paths in the queue, """
            """because a well-connected member has thousands of edges.""")
seg(sid, 3, """Then the questions I wanted to hear: is this graph in memory or behind a service, is there a degree cap — do we """
            """even search past second or third degree — and are blocked or private members traversable. And the staff-level """
            """close, which is the sentence that separates this from a LeetCode answer: in production you precompute to second """
            """degree, you cap the search, and you treat the skill requirement as a filter over an index rather than running """
            """breadth-first search over a live social graph. Say the algorithm, then say what you would actually build. """
            """That is chapter three done.""")
