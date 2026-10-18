namespace SnippetFixtures.TestingUnit01;

using Xunit;

internal sealed class StockCatalog;

internal sealed class Inventory(StockCatalog catalog)
{
    private readonly StockCatalog catalog = catalog;
    private readonly Dictionary<string, int> stock = [];

    public void Receive(string sku, int quantity) => stock[sku] = stock.GetValueOrDefault(sku) + quantity;

    public int StockOf(string sku) => stock.GetValueOrDefault(sku);
}

// snippet:begin
public sealed class InventoryTests
{
    private readonly Inventory inventory;

    public InventoryTests()
    {
        inventory = new Inventory(new StockCatalog());
    }

    #region Receive

    [Theory]
    [InlineData(5, 3, 8)]
    [InlineData(0, 4, 4)]
    public void Receive_PositiveQuantity_IncreasesStock(int initialStock, int quantity, int expected)
    {
        inventory.Receive("sku-1", initialStock);

        inventory.Receive("sku-1", quantity);

        Assert.Equal(expected, inventory.StockOf("sku-1"));
    }

    #endregion
}
// snippet:end
