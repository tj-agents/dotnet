namespace SnippetFixtures.Validation03;

using Dunet;

// snippet:begin
[Union(EnableImplicitConversions = false)]
public abstract partial record PlaceOrderError : IError
{
    public ErrorDefinition Definition => this switch
    {
        Invalid(var errors) => ErrorDefinition.Validation<Invalid>(errors)
    };

    public partial record Invalid(ValidationErrors Errors);
}
// snippet:end
