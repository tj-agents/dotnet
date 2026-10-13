namespace SnippetFixtures.ErrorsCarriers03;

internal sealed record User;
internal abstract record LookupUserError
{
    public sealed record NotFound : LookupUserError;
}
internal abstract record CreateUserError
{
    public sealed record EmailInUse : CreateUserError;
}
internal abstract record ChangePasswordError
{
    public sealed record InvalidPassword : ChangePasswordError;
}

internal static class Example
{
    public static void Run(User user)
    {
// snippet:begin
Result<User, LookupUserError> found = user;
Result<User, LookupUserError> failed = new LookupUserError.NotFound();

UnitResult<CreateUserError> completed = new Success();
UnitResult<CreateUserError> rejected = new CreateUserError.EmailInUse();

Option<User> present = user;
Option<User> absent = null;
// snippet:end

    }
}
