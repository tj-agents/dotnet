namespace SnippetFixtures.Fields02;

internal sealed class StockCatalog;
internal sealed class Inventory(StockCatalog catalog)
{
    private readonly StockCatalog catalog = catalog;
}

internal sealed class InventoryTests
{
// snippet:begin
// CORRECT — no parameter shares the field's name, so there is nothing to disambiguate
private readonly Inventory inventory;

public InventoryTests()
{
    inventory = new Inventory(new StockCatalog());
}
// snippet:end

}
