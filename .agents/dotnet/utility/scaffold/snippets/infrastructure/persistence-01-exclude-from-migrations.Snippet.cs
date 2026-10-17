namespace SnippetFixtures.Persistence01;

using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

internal sealed class SellerRatingProjection;

internal sealed class SellerRatingProjectionConfiguration : IEntityTypeConfiguration<SellerRatingProjection>
{
    public void Configure(EntityTypeBuilder<SellerRatingProjection> builder)
    {
// snippet:begin
// in the BORROWING module's configuration - read-only, never migrated from here
builder.ToTable("SellerRatingProjections", "seller", t => t.ExcludeFromMigrations());
// snippet:end

    }
}
