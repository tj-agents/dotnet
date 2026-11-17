---
name: parallelism
description: Bounded concurrency for independent per-item I/O. Use when writing or reviewing collection loops, async fan-out, batch processing, Parallel.ForEachAsync or Task.WhenAll in .NET.
kind: contract
domain: dotnet
profile: core
applicability: writing or reviewing .NET collection loops, independent per-item I/O and async fan-out
requires: dotnet
provenance: house, platform
---

# Bounded parallelism

Owns concurrency bounds, cancellation and outcome collection for independent per-item work.

```csharp
public static async Task<UserEnsureOutcome> EnsureUsersAsync(
    HttpClient httpClient, IReadOnlyList<int> userIds, CancellationToken ct)
{
    var ensured = 0;
    var failures = new ConcurrentBag<UserEnsureFailure>();
    var parallelOptions = new ParallelOptions
    {
        // This downstream permits five concurrent requests per batch within the shared capacity budget.
        MaxDegreeOfParallelism = 5,
        CancellationToken = ct
    };

    await Parallel.ForEachAsync(userIds, parallelOptions, async (userId, token) =>
    {
        try
        {
            using var response = await httpClient.PostAsync($"users/{userId}/ensure", null, token);
            if (response.IsSuccessStatusCode)
                Interlocked.Increment(ref ensured);
            else
                failures.Add(new UserEnsureFailure(userId, $"Ensure returned {(int)response.StatusCode}."));
        }
        catch (Exception exception) when (exception is not OperationCanceledException)
        {
            failures.Add(new UserEnsureFailure(userId, exception.Message));
        }
    });

    return new UserEnsureOutcome(ensured, failures.OrderBy(failure => failure.UserId).ToList());
}
```

This best-effort batch records an outcome for each user; cancellation still aborts the operation.
`UserEnsureOutcome` and `UserEnsureFailure` are the caller's ordinary result shapes. Five is an example
downstream budget, never a universal default.

## Choose and size the bound

Independent per-item I/O over a collection whose size comes from data uses bounded concurrency by
default. Use `Parallel.ForEachAsync` with an explicit positive `MaxDegreeOfParallelism`; choose the
degree from downstream capacity and observed latency, with the reason beside the value. Account for
simultaneous batches, workers and replicas: a per-loop bound is not a global service quota or a
requests-per-second rate limiter. Respect those separately when the downstream requires them.
Why: data growth must not turn one invocation into unlimited in-flight I/O.
Sources: Microsoft [`ForEachAsync`](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.parallel.foreachasync),
[`MaxDegreeOfParallelism`](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.paralleloptions.maxdegreeofparallelism).

Sequential execution is right when items depend on earlier items, side effects must occur in order,
or the downstream requires one request at a time; state that constraint beside the loop. Cheap work
with measured negligible I/O may also stay sequential. Do not parallelize access to a shared
non-thread-safe collaborator; give iterations independently owned resources where appropriate.
Why: concurrency is useful only when the work is independent and its cost justifies it.
Source: Microsoft [parallelism pitfalls](https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/potential-pitfalls-in-data-and-task-parallelism).

Do not use unbounded `Task.WhenAll(items.Select(...))` for data-sized input. `Task.WhenAll` is fine for
a small fixed set of independent operations whose combined demand fits the downstream budget; it
joins tasks and supplies no throttle. Await asynchronous I/O directly rather than wrapping it in
`Task.Run`. Why: awaiting completion does not constrain how much work was started.
Sources: Microsoft [`WhenAll`](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.whenall),
[async scenarios](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-scenarios).

## Preserve cancellation and outcomes

Build `ParallelOptions` per call with the caller's `CancellationToken`. Pass the body's token to
every awaited operation that accepts cancellation, including waits and retries: the loop can cancel
that token independently of the caller. Never share static options or discard the body token in
favour of an outer token. Why: cancellation must stop active work as well as further scheduling.
Sources: Microsoft [`ForEachAsync`](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.parallel.foreachasync),
[runtime implementation](https://github.com/dotnet/runtime/blob/main/src/libraries/System.Threading.Tasks.Parallel/src/System/Threading/Tasks/Parallel.ForEachAsync.cs).

Use `Interlocked` for shared counters and concurrent collections or independently owned slots for
results. After awaiting the loop, order reported results by a stable key or original input position;
include a tie-breaker when keys can repeat. Never append concurrently to an ordinary `List<T>` or rely
on completion order. Why: correct counts and repeatable reports must survive scheduling differences.
Sources: Microsoft [thread-safe collections](https://learn.microsoft.com/en-us/dotnet/standard/collections/thread-safe/),
[`Interlocked`](https://learn.microsoft.com/en-us/dotnet/api/system.threading.interlocked).

For a best-effort batch of independent outcomes, handle unsuccessful responses and item exceptions
inside the body, retaining the item's identity so its failure does not discard successful items.
A broad catch belongs only at that explicit batch isolation boundary; exclude
`OperationCanceledException` and let cancellation propagate. If the operation requires atomic success,
preserve that failure contract instead of silently converting it to partial success.
Why: item rejection and cancellation have different meanings.
Sources: Microsoft [`WhenAll`](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.whenall),
[task cancellation](https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/task-cancellation).

## Review production volume and prove the limit

Ask "how long does this take at production volume?" Estimate waves from item count and degree, then
include downstream latency, retries and overhead. Compare with the actual host execution budget and
request timeouts. Where Functions is used, check configured invocation/activity limits and hosting
plan rather than assuming a default; Durable activity timeouts are failures. Chunk or checkpoint work
when safe concurrency cannot fit the budget. Why: bounded work can still exceed its host's lifetime.
Sources: Microsoft [Functions timeouts](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale#timeout),
[Durable performance](https://learn.microsoft.com/en-us/azure/azure-functions/durable-functions-perf-and-scale#function-timeouts).

Where the bound protects capacity or completion time, test the real batch entry point with more items
than its limit. Use a controlled asynchronous downstream that counts in-flight calls and holds the
first wave until the limit is reached; assert peak equals the limit and never exceeds it across later
waves. Use signals and a bounded test timeout, not sleeps or a barrier waiting for every input item.
Also prove an item failure preserves other outcomes, caller cancellation reaches active work, and
reported ordering is stable. Follow `dotnet:testing` and the selected test tier for test shape.
Why: a test that merely inspects the configured number proves no execution bound.
