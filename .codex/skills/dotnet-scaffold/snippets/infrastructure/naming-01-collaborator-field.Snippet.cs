namespace SnippetFixtures.Naming01;

internal interface IUserService { }

#pragma warning disable CS0169, CS8618

internal sealed class InvoiceSender
{
// snippet:begin
private readonly IUserService userService;
// snippet:end

}

#pragma warning restore CS0169, CS8618
