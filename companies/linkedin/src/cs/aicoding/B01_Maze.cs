// B01 — debug, then extend, a maze class. Reported ≈Mar 2026 (Exponent, Senior SWE, US) for
// LinkedIn's AI round on HackerRank. The follow-ups were: is the maze well formed including the
// outer wall; generate a maze that always has a path; why did you choose the AI's approach;
// how would you test each change; what would you change for production.

public sealed class Maze {
    private readonly bool[,] _wall;                    // true = wall
    public int Rows { get; }
    public int Cols { get; }
    public (int R, int C) Start { get; }
    public (int R, int C) End { get; }

    public Maze(string[] rows) {
        if (rows == null || rows.Length == 0) throw new ArgumentException("empty maze");
        Rows = rows.Length; Cols = rows[0].Length;
        if (rows.Any(r => r.Length != Cols)) throw new ArgumentException("ragged maze");
        _wall = new bool[Rows, Cols];
        for (int r = 0; r < Rows; r++)
            for (int c = 0; c < Cols; c++) {
                char ch = rows[r][c];
                _wall[r, c] = ch == '#';
                if (ch == 'S') Start = (r, c);
                if (ch == 'E') End = (r, c);
            }
    }

    public bool IsWall(int r, int c) => _wall[r, c];

    // Well formed: the whole border is wall, except that S and E may sit on it as openings,
    // and S and E are distinct open cells. "Including the outer wall" was the reported wording.
    public bool IsWellFormed() {
        if (Rows < 3 || Cols < 3 || Start == End) return false;
        for (int r = 0; r < Rows; r++)
            for (int c = 0; c < Cols; c++) {
                bool border = r == 0 || c == 0 || r == Rows - 1 || c == Cols - 1;
                bool opening = (r, c) == Start || (r, c) == End;
                if (border && !opening && !_wall[r, c]) return false;
            }
        return !_wall[Start.R, Start.C] && !_wall[End.R, End.C];
    }

    // BFS: fewest steps from S to E, or -1. Visited is marked when a cell is ENQUEUED.
    // Marking on dequeue still returns the right number, but lets the same cell enter the
    // queue many times — on an open grid that is the difference between O(cells) and much worse.
    public int ShortestPath() {
        var dist = new int[Rows, Cols];
        for (int r = 0; r < Rows; r++) for (int c = 0; c < Cols; c++) dist[r, c] = -1;
        var q = new Queue<(int R, int C)>();
        dist[Start.R, Start.C] = 0;
        q.Enqueue(Start);
        ReadOnlySpan<(int, int)> dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)];
        while (q.Count > 0) {
            var (r, c) = q.Dequeue();
            if ((r, c) == End) return dist[r, c];
            foreach (var (dr, dc) in dirs) {
                int nr = r + dr, nc = c + dc;
                if (nr < 0 || nc < 0 || nr >= Rows || nc >= Cols) continue;   // bounds before indexing
                if (_wall[nr, nc] || dist[nr, nc] >= 0) continue;
                dist[nr, nc] = dist[r, c] + 1;
                q.Enqueue((nr, nc));
            }
        }
        return -1;
    }

    // Extension: generate a maze that ALWAYS has a path. Randomised depth-first carving over a
    // grid of odd dimensions produces a spanning tree of the cells, so every open cell —
    // including S and E — is connected. Iterative, so a large maze cannot overflow the stack.
    public static Maze Generate(int rows, int cols, int seed) {
        if (rows < 5 || cols < 5 || rows % 2 == 0 || cols % 2 == 0)
            throw new ArgumentException("use odd dimensions >= 5");
        var g = new char[rows, cols];
        for (int r = 0; r < rows; r++) for (int c = 0; c < cols; c++) g[r, c] = '#';
        var rnd = new Random(seed);
        var stack = new Stack<(int R, int C)>();
        g[1, 1] = '.';
        stack.Push((1, 1));
        (int, int)[] steps = [(2, 0), (-2, 0), (0, 2), (0, -2)];
        while (stack.Count > 0) {
            var (r, c) = stack.Peek();
            var options = steps.Where(s => {
                int nr = r + s.Item1, nc = c + s.Item2;
                return nr > 0 && nc > 0 && nr < rows - 1 && nc < cols - 1 && g[nr, nc] == '#';
            }).ToList();
            if (options.Count == 0) { stack.Pop(); continue; }
            var (dr, dc) = options[rnd.Next(options.Count)];
            g[r + dr / 2, c + dc / 2] = '.';               // knock down the wall between
            g[r + dr, c + dc] = '.';
            stack.Push((r + dr, c + dc));
        }
        g[1, 1] = 'S';
        g[rows - 2, cols - 2] = 'E';
        var lines = new string[rows];
        for (int r = 0; r < rows; r++) {
            var row = new char[cols];
            for (int c = 0; c < cols; c++) row[c] = g[r, c];
            lines[r] = new string(row);
        }
        return new Maze(lines);
    }
}
