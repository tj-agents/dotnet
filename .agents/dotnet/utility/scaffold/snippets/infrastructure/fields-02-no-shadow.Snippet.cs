namespace SnippetFixtures.Fields02;

internal sealed class StockLevels;
internal sealed class Inventory(StockLevels stockLevels)
{
    private readonly StockLevels stockLevels = stockLevels;
}

internal sealed class InventoryTests
{
// snippet:begin
// CORRECT — no parameter shares the field's name, so there is nothing to disambiguate
private readonly Inventory inventory;

public InventoryTests()
{
    inventory = new Inventory(new StockLevels());
}
// snippet:end

}
