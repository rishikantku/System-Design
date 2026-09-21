# -*- coding: utf-8 -*-
"""Chapter 3, Lesson 3 — Minimum degree of connection."""
from lib import *

PEOPLE = {'p1': (160, 400, 'S'), 'p2': (420, 250, 'A'), 'p3': (420, 550, 'B'),
          'p4': (700, 180, 'C'), 'p5': (700, 400, 'D'), 'p6': (700, 620, 'E'),
          'p7': (980, 300, 'F'), 'p8': (980, 520, 'G'), 'p9': (1260, 400, 'P')}
LINKS = [('p1', 'p2'), ('p1', 'p3'), ('p2', 'p4'), ('p2', 'p5'), ('p3', 'p5'), ('p3', 'p6'),
         ('p4', 'p7'), ('p5', 'p7'), ('p5', 'p8'), ('p6', 'p8'), ('p7', 'p9'), ('p8', 'p9')]

lesson_header('3.3', 'Minimum degree of connection (and return the path)', 'Bidirectional BFS · path reconstruction',
              'High', 'Your own list, with the expected answer named', '2026', 'High', 17,
              """Chapter three, lesson three. Minimum degree of connection between two members. This is the most LinkedIn """
              """question in the entire course, because it is not a puzzle borrowed from a textbook — it is the product. """
              """First-degree, second-degree, third-degree connections are a feature you can see on every profile page. And """
              """your own note on this question says the expected answer is bidirectional BFS with a follow-up to return the """
              """path. So we already know the destination. What this lesson is really about is what happens when a textbook """
              """algorithm meets a billion-node graph with hub members who have thirty thousand connections.""")

# ---------------------------------------------------------------- question
sid = beat('Question', 'The question',
           '<div class="qwrap"><div class="qtext" style="font-size:38px;line-height:1.35">'
           'You are given users and their direct connections. For two users S and P, find the minimum degree of connection. '
           'Directly connected users are degree 1.<br><br>'
           '<b>Follow-up:</b> return the path.</div></div>',
           """The question. Users and their direct connections, and for two given users you return the minimum degree of """
           """connection, where directly connected means degree one. Then the follow-up your note already tells us is """
           """coming: return the actual path, not just the number. Keep that follow-up in mind while we design, because it """
           """changes one decision early on — and if you design without it, you will have to redo work when it arrives.""")

# ---------------------------------------------------------------- think
think('Given users and their direct connections, find the minimum degree of connection between S and P. '
      'Directly connected is degree 1. Then: return the path.', 30,
      """Pause. Two things to say out loud. First, which traversal and why. Second — and this is the one that matters — what """
      """you would keep during the search so that returning the path afterwards is free rather than a second search.""",
      """Right. Breadth-first search is the obvious core, and it is correct. But let us go straight to the version that makes """
      """this a Staff answer, because plain BFS on this graph does not survive contact with production.""")

# ---------------------------------------------------------------- the graph
D = Diagram('The graph is the product')
graph(D, PEOPLE, LINKS, step=0, node_w=110, node_h=80)
D.label(120, 720, 'S → A → D → G → P: **degree 4**. BFS finds it because every edge costs the same.',
        kind='ok', step=1, w=1700, size='m', align='center')
D.label(120, 790, 'One billion members, average hundreds of connections. The frontier is the problem, not the algorithm.',
        kind='deny', step=2, w=1700, size='m', align='center')
sid = D.build()
seg(sid, 0, """Here is a small version of the graph. S on the left, P on the right, and people in between.""")
seg(sid, 1, """A shortest chain here is S to A to D to G to P — degree four. Breadth-first search finds it because every edge """
            """costs exactly one hop, so the first time you reach a node is by a shortest path. That is the guarantee that """
            """makes BFS the right tool, and it is worth stating rather than assuming.""")
seg(sid, 2, """Now scale it up. A billion members, each with hundreds of connections. The algorithm does not change — but the """
            """frontier does, and the frontier is what will kill you. That is what the rest of this lesson is about.""")

# ---------------------------------------------------------------- why bidirectional
D = Diagram('Why one-directional BFS falls over')
D.label(120, 140, 'Branching factor **b ≈ 300** (average connections)', kind='info', step=0, w=1700, size='m')
D.box('d1', 160, 230, 360, 110, 'Degree 1', '300', kind='ok', step=0, small=True)
D.box('d2', 560, 230, 360, 110, 'Degree 2', '90 000', kind='shared', step=1, small=True)
D.box('d3', 960, 230, 360, 110, 'Degree 3', '27 000 000', kind='deny', step=2, small=True)
D.box('d4', 1360, 230, 400, 110, 'Degree 4', '8 100 000 000', kind='deny', step=3, small=True)
D.label(120, 400, 'Degree 4 exceeds the number of members — the frontier saturates the graph.', kind='deny', step=3, w=1700, size='m', align='center')
D.label(120, 490, 'From both ends, each side only needs **depth 2**: 90 000 + 90 000 = 180 000 nodes.',
        kind='ok', step=4, w=1700, size='m', align='center')
D.label(120, 590, '27 million → 180 thousand. That is the difference between a feature and an outage.',
        kind='dp', step=5, w=1700, size='l', align='center')
sid = D.build()
seg(sid, 0, """Let us do the arithmetic out loud, because this is the moment that makes the answer convincing. Take an average """
            """branching factor of three hundred. At degree one you have looked at three hundred people.""")
seg(sid, 1, """Degree two: ninety thousand.""")
seg(sid, 2, """Degree three: twenty-seven million.""")
seg(sid, 3, """Degree four: eight billion, which is more people than exist. Your frontier has saturated the entire graph. That """
            """is why a one-directional search is not merely slow here; it is unusable.""")
seg(sid, 4, """Now search from both ends. Each side only has to reach depth two before they meet, and depth two is ninety """
            """thousand per side.""")
seg(sid, 5, """Twenty-seven million versus a hundred and eighty thousand. Say those two numbers in the interview. It is the """
            """difference between a feature that renders on a profile page and one that takes the site down.""")

# ---------------------------------------------------------------- designing for the path
sid = compare('Designing for the follow-up you know is coming',
 ('Visited as a HashSet', 'com', 0, ['Enough to return the degree', 'Tells you nothing about how you got there',
                                     'The path follow-up forces a second search', 'You end up rewriting under time pressure']),
 ('Visited as a Dictionary node → parent', 'ok', 1, ['Same cost, same lookups', 'Every node remembers who discovered it',
                                                     'Path = walk parents back from the meeting point',
                                                     '**The follow-up becomes free**']))
seg(sid, 0, """Now the decision I told you to keep in mind. Most people write visited as a hash set, which is enough to return """
            """the degree. But the moment the interviewer says "now return the path", a set tells you nothing about how you """
            """arrived anywhere, and you are rewriting the search with the clock running.""")
seg(sid, 1, """Instead, make visited a dictionary from node to the node that discovered it. Exactly the same lookups, exactly """
            """the same cost, and now every node remembers its parent. When the frontiers meet, the path is just walking """
            """parents backwards from the meeting point on both sides. You get the follow-up for free — and because your note """
            """says that follow-up was actually asked, this is not a hypothetical optimisation.""")

# ---------------------------------------------------------------- walkthrough
D = Diagram('The two frontiers meeting')
graph(D, PEOPLE, LINKS, step=0, node_w=110, node_h=80)
D.label(120, 700, 'Round 1: expand from **S** → {A, B}.   Expand from **P** → {F, G}.', kind='info', step=1, w=1700, size='m', align='center')
D.label(120, 760, 'Round 2: expand the smaller side. D appears from both sides → **they meet**.', kind='ok', step=2, w=1700, size='m', align='center')
D.label(120, 820, 'Path = S…D from one parent map, then D…P reversed from the other.', kind='dp', step=3, w=1700, size='m', align='center')
sid = D.build()
seg(sid, 0, """Let us run it on the small graph.""")
seg(sid, 1, """Round one. From S we reach A and B. From P we reach F and G. Two frontiers, each of size two.""")
seg(sid, 2, """Round two. We expand whichever side is smaller — here they are equal, so either. Expanding from S's side reaches """
            """C, D and E; expanding from P's side reaches C, D and E as well. The moment we find a node that already appears """
            """in the other side's map, the searches have met.""")
seg(sid, 3, """And now the path. Walk parents back from the meeting node through the first map to get S to D. Walk parents """
            """through the second map to get D to P, and reverse it. Join them, skipping the duplicate meeting node, and you """
            """have the full chain. No second search anywhere.""")

# ---------------------------------------------------------------- code
CODE = '''public (int Degree, IReadOnlyList<string> Path) MinDegree(string s, string p) {
    if (s == p) return (0, new[] { s });

    var fromS = new Dictionary<string, string> { [s] = null };   // node -> parent, also the visited set
    var fromP = new Dictionary<string, string> { [p] = null };
    var frontierS = new List<string> { s };
    var frontierP = new List<string> { p };
    int degree = 0;

    while (frontierS.Count > 0 && frontierP.Count > 0) {
        bool expandS = frontierS.Count <= frontierP.Count;        // always expand the smaller side
        var frontier = expandS ? frontierS : frontierP;
        var ours     = expandS ? fromS : fromP;
        var theirs   = expandS ? fromP : fromS;

        var next = new List<string>();
        degree++;

        foreach (var node in frontier)
            foreach (var neighbour in Connections(node)) {
                if (ours.ContainsKey(neighbour)) continue;        // we already have a shorter way here
                ours[neighbour] = node;                           // remember who discovered it
                if (theirs.ContainsKey(neighbour))
                    return (degree, BuildPath(neighbour, fromS, fromP));
                next.Add(neighbour);
            }

        if (expandS) frontierS = next; else frontierP = next;
    }
    return (-1, Array.Empty<string>());                            // not connected
}'''
code_slide('The C# implementation', CODE, [
 ('1-2', """The signature returns both the degree and the path, because we know the follow-up is coming. Same person twice """
           """is degree zero — a case worth handling on line one rather than discovering later."""),
 ('4-8', """The two parent maps, doubling as visited sets, and the two frontiers as plain lists because we only ever iterate """
           """them. Degree starts at zero and increments once per expansion round."""),
 ('10-14', """The loop continues while both sides still have somewhere to go. If either empties, the two people are not """
             """connected. And this is the line that makes it genuinely bidirectional: pick the smaller frontier and expand """
             """that one. Without it you are running two independent searches and paying full price for both."""),
 ('19-22', """For each node in the smaller frontier, we walk its connections. If we have already recorded this neighbour, we """
             """skip — we reached it by an equal or shorter route already. Otherwise we record who discovered it, which is """
             """the line that makes the path free."""),
 ('23-25', """And the meeting test. If the other side has already seen this neighbour, the two searches have touched, and we """
             """return the degree along with the reconstructed path."""),
 ('28-31', """Otherwise the neighbour joins the next frontier. When the round finishes we swap in the new frontier, and if we """
             """ever run out we return minus one for "no connection" — which the caller must handle explicitly rather than """
             """treating as a degree."""),
])

CODE2 = '''private static IReadOnlyList<string> BuildPath(
        string meet, Dictionary<string, string> fromS, Dictionary<string, string> fromP) {

    var left = new List<string>();
    for (var n = meet; n != null; n = fromS[n]) left.Add(n);
    left.Reverse();                       // now s ... meet

    for (var n = fromP[meet]; n != null; n = fromP[n]) left.Add(n);   // skip meet, avoid duplicating it
    return left;                          // s ... meet ... p
}'''
code_slide('Reconstructing the path', CODE2, [
 ('4-7', """Walk parents back from the meeting node through the first map. That gives you the chain from the meeting point """
           """back to S, so you reverse it to get S to the meeting point."""),
 ('9-10', """Then walk the second map from the meeting node's parent — note, its parent, not the meeting node itself, or you """
            """would duplicate it in the middle of the path. Append those, and because that map was built outward from P, the """
            """order already runs meeting point to P."""),
 (None, """Eight lines, and the follow-up is answered. The reason it is eight lines instead of a second search is the decision """
          """you made at the start: store parents, not just membership. That is the whole lesson — design for the follow-up """
          """you know is coming."""),
])

# ---------------------------------------------------------------- production
sid = cards('What breaks at a billion members', [
 (0, 'Hub members', 'Someone with 30 000 connections explodes the frontier. Cap or sample, and say what you traded.', 'deny'),
 (0, 'Depth cap', 'The product shows up to 3rd degree — so cap the search at 3 and return "3rd+" beyond it.', 'ok'),
 (1, 'Privacy', 'Some connections are not visible to the searcher. Filter during traversal, not after.', 'shared'),
 (1, 'The graph does not fit on one machine', 'Partitioned BFS with cross-machine frontiers, or precomputed 2nd-degree sets.', 'info'),
 (2, 'Repeated queries from one member', 'Cache their 1st and 2nd degree sets — that is how the product actually serves it.', 'ok'),
 (2, 'Weighted edges', 'If connection strength matters it is Dijkstra, not BFS. Know when your tool stops applying.', 'info'),
], cols=2)
seg(sid, 0, """Now the part that turns a correct answer into a Staff answer: what breaks in production. Hub members. One person """
            """with thirty thousand connections blows the frontier up on their own. You can cap the expansion, or sample """
            """their edges — but whichever you choose, say what you are trading, because you are trading completeness.""")
seg(sid, 1, """A depth cap. The product only shows up to third degree, so the search can stop at three and report "third plus" """
            """beyond that. That single product fact bounds the entire computation, and noticing it is a very strong move.""")
seg(sid, 2, """Privacy: some connections are not visible to the person searching, and that filtering has to happen during the """
            """traversal, not as a post-processing step, or you leak the existence of relationships through timing and counts.""")
seg(sid, 3, """And then the distributed question: a billion-node graph does not sit on one machine, so you are either doing a """
            """partitioned BFS with frontiers crossing machines, or you have precomputed second-degree sets offline. That """
            """second answer is how the real product does it, and it connects directly to the People You May Know design in """
            """the system design course.""")
seg(sid, 4, """Repeated queries from the same member should hit a cache of their first and second degree sets.""")
seg(sid, 5, """And if edges ever gain weights — connection strength, interaction recency — then BFS stops being correct and you """
            """need Dijkstra. Knowing the boundary of your algorithm is worth as much as knowing the algorithm.""")

sid = table('Complexity', ['', 'Answer', 'Say it like this'], [
 (0, ['One-directional', 'O(b^d)', 'At b=300, d=4 that is 8 billion — larger than the member base'], [None, 'deny', None]),
 (1, ['Bidirectional', '~O(2·b^(d/2))', 'Same class, but 27 million becomes 180 thousand at realistic numbers'], [None, 'ok', None]),
 (2, ['Space', 'O(frontier + visited)', 'Two parent maps — the cost of making the path follow-up free'], [None, 'info', None]),
 (3, ['With a depth cap of 3', 'Bounded', 'The product only shows 3 degrees, so the work is bounded by design'], [None, 'ok', None]),
], widths=[24, 22, 54])
seg(sid, 0, """Complexity. One-directional is b to the d, and at realistic numbers that exceeds the member base.""")
seg(sid, 1, """Bidirectional is the same asymptotic class but roughly two times b to the d over two — and quote the concrete """
            """numbers, because they are the argument.""")
seg(sid, 2, """Space is the frontiers plus the two parent maps. Name that cost as the price of the free path reconstruction; """
            """it shows you know what you bought.""")
seg(sid, 3, """And with a depth cap of three, the whole thing becomes bounded by design rather than by hope.""")

followups(
 ['"Return the path" — your own note says this was the follow-up; the parent maps make it eight lines',
  '"Why bidirectional?" — the b^d versus 2·b^(d/2) arithmetic with real numbers',
  '"What about someone with 30 000 connections?" — cap or sample, and name the trade'],
 ['"The graph is sharded across machines" — frontier exchange per round, or precomputed 2nd-degree sets',
  '"Third-degree only, for 100 million daily queries" — this becomes a caching and precomputation problem, not a traversal one',
  '"How do you keep it correct as the graph changes under you?" — snapshot versus live reads, and what a user would accept'],
 """Follow-ups. Returning the path is the one your note recorded, and you have it. Why bidirectional is answered with """
 """arithmetic. And the hub question is one you should raise before they do.""",
 """At Staff level the conversation moves off the algorithm entirely. Sharded graph: you exchange frontiers between machines """
 """once per round, and suddenly network round trips dominate. A hundred million daily queries with a three-degree cap is """
 """not a traversal problem at all any more — it is precomputation and caching, and the honest answer is that you would """
 """not run a live BFS per page view. And the consistency question is a lovely one: the graph changes while you traverse """
 """it, so do you read a snapshot or live data? A user will happily accept a connection added ten seconds ago not showing """
 """up; they will not accept the page timing out. Saying that is product judgement, and it is exactly what this round """
 """rewards.""")

interview_script([
 '"Nodes are members, edges are connections, all edges cost one hop — so BFS gives the minimum degree."',
 '"One-directional BFS is not viable here: at b≈300, degree 4 is 8 billion nodes, more than the member base."',
 '"So I would search from both ends and always expand the smaller frontier. Depth 2 from each side is ~90 000 per side."',
 '"I will store visited as node-to-parent rather than a set, so returning the path later costs nothing extra."',
 '"When a node appears in the other side\'s map, the frontiers have met: degree is the rounds taken, and the path is two parent walks."',
 '"In production I would cap at 3rd degree, because that is all the product shows, and cap or sample hub members."',
 '"If connection strength ever mattered, this stops being BFS and becomes Dijkstra."',
], [
 """The script. You open with the model and the justification for BFS in one sentence. Then — before anyone challenges you """
 """— you kill the naive version with arithmetic. That is the strongest opening move available on this problem.""",
 """Then bidirectional with the smaller-frontier rule, and the parent-map decision explained by the follow-up it enables. """
 """Notice you are telling the interviewer you anticipated their next question. That lands well.""",
 """Then the meeting condition, then production: the depth cap justified by a product fact, hub handling with the trade """
 """named, and the Dijkstra boundary. Seven sentences that go from graph theory to product judgement — which is exactly the """
 """arc a Staff interviewer is listening for.""",
])

sid = statement('Take this with you', 'Design for the follow-up you know is coming.',
                'A parent map costs the same as a visited set and makes "return the path" free. Next: build order, cycles, and parallel waves.',
                kind='ok')
seg(sid, 0, """One sentence: design for the follow-up you know is coming.""")
seg(sid, 1, """A parent map costs exactly what a visited set costs and turns a second search into eight lines. Next lesson is """
            """the last of this chapter: get build order, reported first-hand from a LinkedIn infrastructure screen — """
            """topological sort, reporting cycles usefully, and emitting parallel waves. See you there.""")
