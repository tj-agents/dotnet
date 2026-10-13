namespace Microsoft.Extensions.Hosting;

public abstract class BackgroundService
{
    protected abstract Task ExecuteAsync(CancellationToken stoppingToken);

    public virtual Task StartAsync(CancellationToken ct) => ExecuteAsync(ct);

    public virtual Task StopAsync(CancellationToken ct) => Task.CompletedTask;
}
