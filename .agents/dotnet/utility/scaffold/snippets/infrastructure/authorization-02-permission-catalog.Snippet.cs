namespace SnippetFixtures.Authorization02;

using System.Collections.Frozen;

// snippet:begin
public readonly record struct Permission
{
    public const string SettlementTriggerName = "settlement.trigger";

    public static Permission SettlementTrigger { get; } = new(SettlementTriggerName);

    public static IReadOnlySet<Permission> All { get; } = new[] { SettlementTrigger }.ToFrozenSet();

    private Permission(string value) => Value = value;

    public string Value { get; }
}
// snippet:end
