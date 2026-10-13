namespace Azure.Messaging.ServiceBus;

public sealed class ServiceBusReceivedMessage
{
    public ServiceBusMessageBody Body { get; } = new();
}

public sealed class ServiceBusMessageBody
{
    public T ToObjectFromJson<T>() => default!;
}

public sealed class ProcessMessageEventArgs
{
    public ServiceBusReceivedMessage Message { get; } = new();
    public CancellationToken CancellationToken { get; }

    public Task CompleteMessageAsync(ServiceBusReceivedMessage message, CancellationToken ct = default) => Task.CompletedTask;
}

public sealed class ProcessErrorEventArgs
{
    public string EntityPath { get; } = "";
    public Exception Exception { get; } = new();
}

public delegate Task ProcessMessageEventHandler(ProcessMessageEventArgs args);
public delegate Task ProcessErrorEventHandler(ProcessErrorEventArgs args);

public sealed class ServiceBusProcessor
{
    public event ProcessMessageEventHandler? ProcessMessageAsync;
    public event ProcessErrorEventHandler? ProcessErrorAsync;

    public Task StartProcessingAsync(CancellationToken ct = default) => Task.CompletedTask;
    public Task StopProcessingAsync(CancellationToken ct = default) => Task.CompletedTask;
}
