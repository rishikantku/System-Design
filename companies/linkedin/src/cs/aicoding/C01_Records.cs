// C01 — structured data processing. Reported Feb–Jun 2026 (Hello Interview, Coditioning):
// build classes from scratch for JSON-like objects, transform them, handle malformed data.
//
// Input: one JSON object per line, e.g.
//   {"user":"u1","action":"view","ts":1700000000,"ms":120}
// Output: per-action count, mean and max latency, distinct users — plus an account of every
// line that was rejected and why. A bad line is DATA, not an exception: one malformed record
// must not abort a batch of a million.

using System.Text.Json;

public sealed record Event(string User, string Action, long Ts, int Ms);

public enum Reject { NotJson, NotAnObject, MissingField, WrongType, OutOfRange }

public readonly record struct ParseResult(Event Event, Reject? Error, string Detail) {
    public bool Ok => Error is null;
}

public static class EventParser {
    public static ParseResult Parse(string line) {
        JsonDocument doc;
        try { doc = JsonDocument.Parse(line); }
        catch (JsonException e) { return new(null, Reject.NotJson, e.Message); }

        using (doc) {
            var root = doc.RootElement;
            if (root.ValueKind != JsonValueKind.Object) return new(null, Reject.NotAnObject, root.ValueKind.ToString());

            if (!Str(root, "user", out var user, out var err)) return err;
            if (!Str(root, "action", out var action, out err)) return err;
            if (!Long(root, "ts", out var ts, out err)) return err;
            if (!Long(root, "ms", out var ms, out err)) return err;
            if (ms < 0 || ms > int.MaxValue) return new(null, Reject.OutOfRange, $"ms={ms}");

            return new(new Event(user, action, ts, (int)ms), null, null);
        }
    }

    private static bool Str(JsonElement o, string name, out string v, out ParseResult err) {
        v = null; err = default;
        if (!o.TryGetProperty(name, out var p)) { err = new(null, Reject.MissingField, name); return false; }
        if (p.ValueKind != JsonValueKind.String || string.IsNullOrWhiteSpace(p.GetString())) {
            err = new(null, Reject.WrongType, name); return false;
        }
        v = p.GetString();
        return true;
    }

    private static bool Long(JsonElement o, string name, out long v, out ParseResult err) {
        v = 0; err = default;
        if (!o.TryGetProperty(name, out var p)) { err = new(null, Reject.MissingField, name); return false; }
        if (p.ValueKind != JsonValueKind.Number || !p.TryGetInt64(out v)) {
            err = new(null, Reject.WrongType, name); return false;
        }
        return true;
    }
}

public sealed record ActionSummary(string Action, int Count, double MeanMs, int MaxMs, int DistinctUsers);

public sealed class Aggregator {
    private sealed class Acc { public int Count; public long SumMs; public int MaxMs; public HashSet<string> Users = new(); }

    private readonly Dictionary<string, Acc> _byAction = new(StringComparer.Ordinal);
    public Dictionary<Reject, int> Rejected { get; } = new();
    public int Accepted { get; private set; }

    // Streaming: takes IEnumerable, holds only the aggregates — never the whole input.
    // (Distinct users per action is the one part that grows with the data; at scale it
    // becomes a HyperLogLog sketch. Say that when asked about memory.)
    public Aggregator Consume(IEnumerable<string> lines) {
        foreach (var line in lines) {
            if (string.IsNullOrWhiteSpace(line)) continue;
            var r = EventParser.Parse(line);
            if (!r.Ok) { Rejected[r.Error.Value] = Rejected.GetValueOrDefault(r.Error.Value) + 1; continue; }
            var e = r.Event;
            if (!_byAction.TryGetValue(e.Action, out var a)) _byAction[e.Action] = a = new Acc();
            a.Count++; a.SumMs += e.Ms; a.MaxMs = Math.Max(a.MaxMs, e.Ms); a.Users.Add(e.User);
            Accepted++;
        }
        return this;
    }

    public IReadOnlyList<ActionSummary> Summary() =>
        _byAction.Select(kv => new ActionSummary(kv.Key, kv.Value.Count,
                                                 (double)kv.Value.SumMs / kv.Value.Count,
                                                 kv.Value.MaxMs, kv.Value.Users.Count))
                 .OrderByDescending(s => s.Count).ThenBy(s => s.Action, StringComparer.Ordinal)
                 .ToList();
}
