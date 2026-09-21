# -*- coding: utf-8 -*-
"""Chapter 3, Lesson 2 — The Maze."""
from lib import *

# 5x5 maze: 0 empty, 1 wall
GRID = [[0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [1, 1, 0, 1, 1],
        [0, 0, 0, 0, 0]]

def draw_grid(D, x=140, y=150, cell=92, step=0, stops=None, start=None, end=None):
    for r, row in enumerate(GRID):
        for c, v in enumerate(row):
            kind = 'com' if v == 1 else 'info'
            text = ''
            if start == (r, c): kind, text = 'ok', 'S'
            if end == (r, c): kind, text = 'shared', 'E'
            hl = (stops or {}).get((r, c))
            D.box('g%d%d' % (r, c), x + c * cell, y + r * cell, cell - 8, cell - 8, text, '',
                  kind=kind, step=step, small=True, hl=(str(hl) if hl is not None else None))

lesson_header('3.2', 'The Maze — when the edges are not the cells', 'Graphs · modelling the state space',
              'High', 'Your own list + a 2026 AI-round maze class', '2026', 'High', 15,
              """Chapter three, lesson two. The Maze. This is on your list, and a maze class turned up in a 2026 AI-coding round """
              """report where the candidate had to debug it and then extend it — so the topic is live in two different """
              """formats. The reason I put it right after Word Ladder is that it teaches the same lesson from the opposite """
              """direction. In Word Ladder the graph was hidden and you had to find it. Here the graph looks obvious, and the """
              """obvious reading is wrong. That is a more dangerous situation, because you can write a hundred lines of """
              """confident, working code that solves a different problem.""")

# ---------------------------------------------------------------- question
D = Diagram('The question')
draw_grid(D, step=0, start=(0, 4), end=(4, 4))
D.label(760, 190, 'A ball starts at **S** and rolls.', kind='info', step=0, w=900, size='m')
D.label(760, 270, 'It **does not stop** until it hits a wall\nor the edge of the grid.', kind='deny', step=1, w=900, size='m')
D.label(760, 400, 'Can the ball **stop** at **E**?', kind='ok', step=2, w=900, size='l')
D.label(760, 500, 'Rolling over E does not count.\nIt has to come to rest there.', kind='shared', step=3, w=900, size='m')
sid = D.build()
seg(sid, 0, """Here is the setup. A grid of empty cells and walls, a ball at the start position marked S.""")
seg(sid, 1, """The ball rolls in one of four directions, and here is the clause that defines the problem: it does not stop until """
            """it hits a wall or the edge of the grid. You cannot roll one cell and change your mind. Once it is moving, it """
            """keeps going.""")
seg(sid, 2, """The question: can the ball stop at the destination E?""")
seg(sid, 3, """And read that word stop carefully, because it is doing all the work. Rolling straight through the destination """
            """does not count. The ball has to come to rest exactly there. Say that back to the interviewer when you restate """
            """the problem — it proves you read it rather than pattern-matched it.""")

# ---------------------------------------------------------------- think
think('A ball in a maze rolls until it hits a wall. Given a start and a destination, can the ball stop at the destination?', 25,
      """Pause. And I want you to answer one specific question out loud: in your traversal, what is a node? Not the code — """
      """just what one node represents. Get that wrong and everything after it is wrong, so it is worth twenty-five seconds.""",
      """Right. If your answer was "a cell", that is the trap, and almost everyone falls into it the first time. Let me show """
      """you exactly what breaks.""")

# ---------------------------------------------------------------- the trap
sid = compare('The mistake that looks like a solution',
 ('BFS over neighbouring cells', 'deny', 0, ['Treats every empty neighbour as reachable',
                                             'But the ball cannot stop on most of them',
                                             'Reports "yes" for destinations it can only roll past',
                                             '**It solves a different problem, silently**']),
 ('What the ball actually does', 'ok', 1, ['From a resting place, it picks a direction',
                                           'It travels until something stops it',
                                           'It has no choice in between',
                                           'So the **choice points** are the resting places']))
seg(sid, 0, """Here is the trap. You write a standard grid BFS: from each cell, look at the four neighbouring cells, enqueue the """
            """empty ones. That code is short, familiar, and it runs. It also answers a different question — it tells you """
            """whether a path of single steps exists, and it will happily report success for a destination the ball can only """
            """ever roll past. No crash, no exception. Just a wrong answer that looks right on the example.""")
seg(sid, 1, """Now think about what the ball actually does. From a resting position it chooses a direction. Then it has no """
            """further choices at all until it stops. So the points where decisions happen — the only places the ball can ever """
            """branch — are the resting positions. That is your node set. Cells the ball merely passes over are not nodes; """
            """they are the inside of an edge.""")

# ---------------------------------------------------------------- key observation
D = Diagram('The key observation')
D.box('k1', 120, 150, 1680, 130, 'Nodes are **stopping positions**, not cells.',
      'An edge from a stop is "roll in direction d until blocked" — and the landing cell is the neighbour.', kind='ok', step=0)
D.box('k2', 120, 320, 1680, 130, 'Each node has at most four edges.',
      'One per direction. Some directions may not move at all — that is a self-loop and must be skipped.', kind='dp', step=1)
D.box('k3', 120, 490, 1680, 130, 'Visited means "we have already been stopped here".',
      'Mark stopping positions, not cells travelled through, or you will prune paths that were still alive.', kind='shared', step=2)
D.label(120, 670, 'One sentence for the interview: *"The graph is over resting positions; rolling is the edge."*',
        kind='ok', step=3, w=1700, size='l', align='center')
sid = D.build()
seg(sid, 0, """So the observation, in one line: the nodes are stopping positions, and an edge means roll in this direction until """
            """something blocks you. The cell where you come to rest is the neighbour. Everything the ball passed over on the """
            """way is inside the edge, not on it.""")
seg(sid, 1, """Each node has at most four outgoing edges, one per direction. And watch for the degenerate case: if the ball is """
            """already against a wall in that direction, it does not move at all. That is a self-loop and you must skip it, or """
            """you will enqueue the node you are standing on and spin.""")
seg(sid, 2, """And visited means we have already been stopped here. Do not mark the cells the ball travels through — those cells """
            """may well be reachable as resting places by some other route, and marking them would prune a path that was """
            """still alive. That is a subtle bug and a good thing to say out loud, because it shows you understand what your """
            """visited set actually represents.""")
seg(sid, 3, """If you say only one sentence about this problem, say this one: the graph is over resting positions, and rolling """
            """is the edge.""")

# ---------------------------------------------------------------- walkthrough
D = Diagram('Walkthrough: rolling from the start')
draw_grid(D, step=0, start=(0, 4), end=(4, 4), stops={(1, 4): 1, (0, 4): 2, (4, 4): 3})
D.label(760, 170, 'Start at (0,4). Roll **down**: it travels to (1,4)\nbecause (2,4)… keeps going? No — check the wall.',
        kind='info', step=1, w=900, size='m')
D.label(760, 310, 'Roll **left** from the start: travels across the\nopen row and stops where the wall blocks it.',
        kind='info', step=2, w=900, size='m')
D.label(760, 450, 'Each stop is enqueued **once**; from each we try\nall four directions again.', kind='dp', step=3, w=900, size='m')
D.label(760, 590, 'We answer **yes** only when a stop equals E.', kind='ok', step=4, w=900, size='m')
sid = D.build()
seg(sid, 0, """Let us walk it. The ball starts at the top right.""")
seg(sid, 1, """We try rolling down. The ball travels until the next cell would be a wall or off the grid, and wherever that """
            """leaves it, that cell becomes a neighbour of the start.""")
seg(sid, 2, """We try rolling left. It travels across the open row and stops where the wall blocks it. Notice that we do not """
            """enqueue any of the cells it passed through — only the one where it stopped.""")
seg(sid, 3, """Each stopping position goes into the queue once, and from each one we try all four directions again. This is an """
            """ordinary BFS; it is only the neighbour function that is unusual.""")
seg(sid, 4, """And we answer yes only when a stopping position equals the destination. If the queue empties first, the answer is """
            """no. That final check is where the word stop from the problem statement finally pays off.""")

# ---------------------------------------------------------------- code
CODE = '''public bool HasPath(int[][] maze, int[] start, int[] destination) {
    int rows = maze.Length, cols = maze[0].Length;
    var visited = new bool[rows, cols];              // visited STOPPING positions
    int[] dr = { 1, -1, 0, 0 }, dc = { 0, 0, 1, -1 };

    var queue = new Queue<(int r, int c)>();
    queue.Enqueue((start[0], start[1]));
    visited[start[0], start[1]] = true;

    while (queue.Count > 0) {
        var (r, c) = queue.Dequeue();
        if (r == destination[0] && c == destination[1]) return true;   // stopped here

        for (int d = 0; d < 4; d++) {
            int nr = r, nc = c;
            // roll while the NEXT cell is inside the grid and empty
            while (nr + dr[d] >= 0 && nr + dr[d] < rows &&
                   nc + dc[d] >= 0 && nc + dc[d] < cols &&
                   maze[nr + dr[d]][nc + dc[d]] == 0) {
                nr += dr[d];
                nc += dc[d];
            }
            if (!visited[nr, nc]) {                  // a stopping position we have not had before
                visited[nr, nc] = true;
                queue.Enqueue((nr, nc));
            }
        }
    }
    return false;
}'''
code_slide('The C# implementation', CODE, [
 ('1-4', """Standard BFS scaffolding, with one comment that earns its place: visited holds stopping positions. Write that """
           """comment. It is the difference between this code and the wrong code, and it tells a reviewer which problem you """
           """think you are solving."""),
 ('6-8', """Seed the queue with the start, and mark it visited immediately. Marking on enqueue rather than on dequeue is the """
           """usual BFS discipline — otherwise the same position can sit in the queue several times."""),
 ('10-12', """The loop, and the success test placed at dequeue time. Because we only ever enqueue stopping positions, reaching """
             """this line means the ball genuinely came to rest here, which is exactly what the question asked."""),
 ('14-21', """This inner while loop is the whole problem in six lines. We look at the next cell in direction d; if it is inside """
             """the grid and empty, we move there and look again. When the loop exits, nr and nc hold the last empty cell """
             """before the blockage — the resting place. Notice we test the next cell rather than the current one; writing it """
             """the other way round is the classic off-by-one here and it makes the ball stop one cell early."""),
 ('22-25', """Then the ordinary BFS step: if this resting place is new, mark it and enqueue it. If the ball did not move at """
             """all in this direction, nr and nc are unchanged, the position is already visited, and we correctly skip it — """
             """the self-loop handles itself, but say that out loud rather than leaving it to luck."""),
 ('28', """And if the queue drains without hitting the destination, no sequence of rolls stops there, so we return false."""),
])

# ---------------------------------------------------------------- complexity
sid = table('Complexity — the part most candidates get wrong', ['', 'Answer', 'Why'], [
 (0, ['Time', '**O(R·C·max(R,C))**', 'Each of R·C stopping positions may roll up to max(R,C) cells in each of 4 directions'], [None, 'ok', None]),
 (1, ['Common wrong answer', 'O(R·C)', 'Forgets that an edge is a roll, not a step — the rolling factor is real'], [None, 'deny', None]),
 (2, ['Space', 'O(R·C)', 'Visited grid plus the queue'], [None, 'info', None]),
], widths=[26, 24, 50])
seg(sid, 0, """Complexity, and this is where you can separate yourself in about eight seconds. Time is order R times C times the """
            """max of R and C. There are R times C possible stopping positions, and from each one you may roll up to the length """
            """of the grid in each of four directions.""")
seg(sid, 1, """Almost everyone says order R times C, because that is what grid BFS normally costs. It is wrong here, and it is """
            """wrong for the same reason the naive solution is wrong: an edge is a roll, not a step. Getting this right signals """
            """that you understood the model rather than recognising the template.""")
seg(sid, 2, """Space is order R times C for the visited grid and the queue.""")

sid = cards('Edge cases', [
 (0, 'Start equals destination', 'True — the ball is already stopped there.', 'ok'),
 (0, 'Destination only passed through', 'False. This is the case the naive solution gets wrong.', 'deny'),
 (1, 'A 1×N maze', 'Rolling immediately hits the boundary; make sure the bounds test handles it.', 'info'),
 (1, 'Start surrounded by walls', 'No moves at all; the queue drains after one dequeue.', 'info'),
 (2, 'Large maze', 'Iterative BFS, not recursion — the roll makes depth unpredictable.', 'shared'),
 (2, 'Destination is a wall', 'Validate inputs, or at least say you would.', 'info'),
], cols=2)
seg(sid, 0, """Edge cases. Start equals destination is true, because the ball is already at rest there. And the one to name """
            """explicitly: a destination the ball can only pass through must return false. That is the test that distinguishes """
            """your solution from the naive one, so offer it as your own test case before anyone asks.""")
seg(sid, 1, """A one-by-N maze rolls straight into the boundary, which exercises your bounds check. A start surrounded by walls """
            """produces no moves at all.""")
seg(sid, 2, """Large mazes want iterative BFS rather than recursion, because the rolling makes recursion depth hard to reason """
            """about. And a destination that is itself a wall is an input-validation question — mention it even if you do not """
            """code it.""")

followups(
 ['"Return the shortest distance to stop at the destination" (Maze II) — Dijkstra, because a roll has length',
  '"How would you make sure the maze is well formed, including the outer wall?" — reported verbatim in 2026',
  '"Generate a maze so there is always a path from start to end" — reported verbatim in 2026'],
 ['"The grid is 10⁶ × 10⁶ and sparse" — store walls in a hash set; the algorithm is unchanged, the representation is not',
  '"Now the ball can stop early on request" — the node set changes back to cells; say how the model shifts',
  '"How would you test each change?" — reported verbatim; property tests plus a brute-force oracle on small grids'],
 """Follow-ups, and two of these are quoted word for word from the 2026 report, so rehearse them. Maze Two asks for the """
 """shortest distance rather than a yes or no. The important point is that it stops being breadth-first search, because """
 """rolls have different lengths — so the edges are weighted and you need Dijkstra. Saying that transition out loud is worth """
 """real credit.""",
 """The generation and validation questions came from a candidate who had to debug and extend a maze class with an AI """
 """assistant. Well-formed means every border cell is a wall — a linear scan. Guaranteed-path generation means carving with """
 """a randomised depth-first search or union-find, which by construction leaves everything connected. And the testing """
 """question, also quoted: small grids where you can brute-force every answer, property tests that a well-formed maze stays """
 """well formed, and a specific test for the roll-past-the-destination case. If you remember nothing else from the staff """
 """column, remember that a brute-force oracle on small inputs is the most convincing test answer you can give.""")

interview_script([
 '"Let me restate: the ball rolls until it hits a wall, and it has to come to rest on the destination — rolling past does not count."',
 '"So the nodes in my graph are not cells. They are stopping positions, and an edge is one roll in one direction."',
 '"If I did a normal grid BFS over neighbouring cells, I would answer a different question and it would look correct."',
 '"BFS over stopping positions, marking visited on enqueue, and I check the destination when I dequeue."',
 '"Complexity is R·C·max(R,C), not R·C, because each edge is a roll across the grid."',
 '"A test I would insist on: a destination the ball can only roll past. That is the case the naive version gets wrong."',
 '"If you want the shortest distance instead, the rolls are weighted, so it becomes Dijkstra rather than BFS."',
], [
 """The script. You start by restating the two clauses that matter — rolls until blocked, and must come to rest. Then you """
 """immediately name the modelling decision: nodes are stopping positions.""",
 """Then, and this is a move worth stealing, you name the trap you are avoiding. Saying "if I did the obvious grid BFS I """
 """would be answering a different question" tells the interviewer you considered it and rejected it, which is far stronger """
 """than never mentioning it.""",
 """Then the algorithm, the corrected complexity, the test that distinguishes right from wrong, and the Dijkstra transition """
 """for the shortest-distance variant. Seven sentences and you have covered the model, the trap, the cost and the """
 """extension.""",
])

sid = statement('Take this with you', 'Ask what a node is before you ask how to traverse.',
                'Word Ladder hid the graph. The Maze disguised it. Both are modelling questions wearing traversal clothes.', kind='ok')
seg(sid, 0, """One sentence: ask what a node is before you ask how to traverse.""")
seg(sid, 1, """In Word Ladder the graph was hidden and you had to construct it. Here the graph was disguised and you had to """
            """reject the obvious reading. Both are modelling questions wearing traversal clothes — and the traversal itself """
            """was textbook in each case. Next lesson: minimum degree of connection, which is the most LinkedIn question in """
            """this entire course, because the product is a graph of people. See you there.""")
