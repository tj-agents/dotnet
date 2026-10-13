namespace SnippetFixtures.Style07;

using Microsoft.EntityFrameworkCore;

#pragma warning disable CS0162

internal class Entity
{
    public bool IsActive { get; set; }
}

internal class RepositoryBase
{
    protected IQueryable<Entity> CurrentScope { get; } = new List<Entity>().AsQueryable();
}

internal sealed class Repository : RepositoryBase
{
    public async Task<List<Entity>> GetActiveAsync(CancellationToken ct)
    {
// snippet:begin
// CORRECT — CurrentScope is defined on the base, not here
return await base.CurrentScope.Where(x => x.IsActive).ToListAsync(ct).ConfigureAwait(false);

// WRONG — reads like a local member
return await CurrentScope.Where(x => x.IsActive).ToListAsync(ct).ConfigureAwait(false);
// snippet:end

    }
}

#pragma warning restore CS0162
