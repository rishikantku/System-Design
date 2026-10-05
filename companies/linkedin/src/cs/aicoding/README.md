# C# for the Coding-with-AI training platform

Every listing on `02-ai-coding.html` and in the simulator's "Would you ship this?" round is read
from this directory at build time (via `qbank_cs.py`, with an `aicoding/` path prefix), so the page
cannot drift from code that was compiled and run.

```
cd companies/linkedin/src/cs/aicoding
dotnet run -c Release
```

126 assertions, 0 failures on .NET 10.0.103.

| File | Holds |
|---|---|
| `A01_Lru.cs` … `L01_Logger.cs` | The worked solutions (LRU ladder + resize, counting LRU, LFU+rank, intervals, records, bounded queue, maze, sampling, window counter, logging library) |
| `Review.cs` | R1–R14: plausible assistant output, each with one defect that matters |
| `Debug.cs` | D1–D8: broken implementations, plus the `Fixes` class |
| `Tests.cs` | Proves every solution, **reproduces every planted defect**, and verifies every fix |

The race-condition reviews (R3, R9) and D4 are nondeterministic by nature, so their tests print how
often the defect appeared rather than asserting it. Everything else is asserted, and the sampling
tests are exact enumerations rather than statistical.

**One real bug was found in my own code.** The first `AsyncLogger` used
`BoundedChannelFullMode.DropWrite` and counted drops on `TryWrite == false`. Under DropWrite,
`TryWrite` returns true even when it drops, so the 10,000-thread test reported 10,000 accepted,
0 dropped, 1,026 written. Fixed with `FullMode = Wait` and kept as review exercise R14, because it
is exactly the kind of plausible API assumption the round is testing for.
