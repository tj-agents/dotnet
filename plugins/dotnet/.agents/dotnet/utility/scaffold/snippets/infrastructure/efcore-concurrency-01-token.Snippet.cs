namespace SnippetFixtures.Concurrency01;

using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

internal sealed class Membership { public uint Version { get; set; } }
internal static class MembershipErrors { public const string Superseded = "superseded"; }

internal sealed class MembershipWriter
{
    public async Task<string?> SaveAsync(EntityTypeBuilder<Membership> builder, DbContext context, CancellationToken ct)
    {
// snippet:begin
builder.Property(membership => membership.Version).IsConcurrencyToken();

try
{
    await context.SaveChangesAsync(ct);
}
catch (DbUpdateConcurrencyException)
{
    return MembershipErrors.Superseded;
}
// snippet:end


        return null;
    }
}
