# C# for the LinkedIn coding question bank

Every listing rendered on `09-question-bank.html` is read from this directory at build time,
so the page cannot drift from code that was actually compiled and run.

```
cd companies/linkedin/src/cs/qbank
dotnet run -c Release
```

269 assertions, 0 failures on .NET 10.0.103. `Tests.cs` is not shown on the page; it exists so
the claims on the page are checkable. Three of the checks are property tests rather than fixed
expectations — the covered-size structure against a brute-force bitmap, the four island variants
against brute force over every window, and the tournament tree against its sorted leaves.

Two of the original failures were wrong expectations in this test file, not wrong code. One was a
real bug: `TaskManager.AddTask` overwrote an existing task's dependency edges instead of unioning
them, so a cycle closed across two calls went undetected. Both are documented on the page.
