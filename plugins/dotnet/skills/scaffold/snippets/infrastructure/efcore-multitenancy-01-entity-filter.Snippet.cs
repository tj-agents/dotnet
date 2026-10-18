namespace SnippetFixtures.EfMultitenancy01;

using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

// snippet:begin
public sealed class PrivateOrderConfiguration : IEntityTypeConfiguration<PrivateOrder>
{
    private readonly PrivateReadDbContext context;

    public PrivateOrderConfiguration(PrivateReadDbContext context)
    {
        this.context = context;
    }

    public void Configure(EntityTypeBuilder<PrivateOrder> builder) =>
        builder.HasQueryFilter(order => order.TenantId == context.TenantId);
}
// snippet:end
