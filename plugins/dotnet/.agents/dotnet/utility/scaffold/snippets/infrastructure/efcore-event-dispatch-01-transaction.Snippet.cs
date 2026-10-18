namespace SnippetFixtures.EfEventDispatch01;

using Microsoft.EntityFrameworkCore;

internal static class Example
{
    public static async Task SaveAndCommitAsync(DbContext context, CancellationToken ct = default)
    {
// snippet:begin
var transaction = await context.Database.BeginTransactionAsync(ct).ConfigureAwait(false);
await using (transaction.ConfigureAwait(false))
{
    await context.SaveChangesAsync(ct).ConfigureAwait(false);
    await transaction.CommitAsync(ct).ConfigureAwait(false);
}
// snippet:end

    }
}
