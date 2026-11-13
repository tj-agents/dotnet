namespace SnippetFixtures.UnitOfWork01;

// snippet:begin
public interface IUnitOfWork
{
    Task SaveChangesAsync(CancellationToken ct = default);

    Task<T> ExecuteAsync<T>(Func<CancellationToken, Task<T>> work, CancellationToken ct = default);
}
// snippet:end
