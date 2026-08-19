# Logging

## Every message is a source-generated `[LoggerMessage]` method

No inline `logger.LogInformation/LogWarning/LogError(...)` calls. Each project owns one `Log.cs` —
`internal static partial class Log` — holding a `[LoggerMessage]` method per message, called as
`logger.PublishedOrderEvents(count)`. The generator gates on `IsEnabled(level)`, so a switched-off level
costs nothing, and the message template is checked against its arguments at compile time.

```csharp
[LoggerMessage(Level = LogLevel.Information, Message = "Published {Count} order events")]
internal static partial void PublishedOrderEvents(this ILogger logger, int count);
```

Set `CA1848` to `error` in `.editorconfig`. That makes the inline form a build failure rather than a
convention someone has to remember, and it is the reason the debugging rule below has no exception.

`Log.cs` is the one file where `#region` is right — one region per emitting class, named for that class.
See the `csharp-style` skill.

## Observability is production code, including a probe

When a problem is hard to trace, inject `ILogger<T>` into the relevant class and log the key state rather
than relying on exceptions or test output alone. Those loggers stay in production code permanently; they
make the system observable and are not debug-only scaffolding.

A one-off investigation probe follows the same route: add its `[LoggerMessage]` method to `Log.cs`, use
it, then **delete that entry once the bug is fixed**. An inline `logger.Log*` call for "just a quick
probe" does not compile.
