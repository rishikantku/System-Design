// Tutorial — modern C# (12–14, .NET 9–10) worth using in a pad. Compiled under net10.0 / LangVersion latest.

// A record: value equality, a readable ToString, and non-destructive `with` copies — ideal for keys and results.
public sealed record Order(string Id, decimal Amount, string Status = "new");

// A primary constructor (C# 12): parameters available to the whole class, no boilerplate fields.
public sealed class Inventory(int capacity) {
    private readonly Dictionary<string, int> _stock = new(capacity);
    public int Capacity => capacity;

    // TryGetValue with an inline `out var`, and GetValueOrDefault: no double lookup.
    public int Add(string sku, int qty) => _stock[sku] = _stock.GetValueOrDefault(sku) + qty;
    public bool TryTake(string sku, int qty) {
        if (!_stock.TryGetValue(sku, out var have) || have < qty) return false;
        _stock[sku] = have - qty;
        return true;
    }
}

public static class Modern {
    // Switch expression with property and relational patterns.
    public static string Classify(Order o) => o switch {
        { Amount: <= 0 }                 => "invalid",
        { Status: "cancelled" }          => "ignore",
        { Amount: > 1000 }               => "large",
        _                                => "normal",
    };

    // Collection expressions (C# 12) and the spread operator `..`.
    public static int[] Merge(int[] a, List<int> b) => [.. a, .. b, 99];

    // `required` members: the compiler forces callers to set them.
    public sealed class Config { public required string Name { get; init; } public int Retries { get; init; } = 3; }
}
