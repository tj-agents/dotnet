namespace SnippetFixtures.ErrorsCarriers04;

internal abstract record ChangePasswordError
{
    public sealed record InvalidPassword : ChangePasswordError;
}

internal sealed class User
{
    public Guid Id { get; init; }
}

internal sealed class UserStore
{
    private readonly List<User> users = [];

    private static bool IsAllowed(string password) => true;
    private void SetPassword(string password) { }

// snippet:begin
public Option<User> Find(Guid id)
{
    User? user = users.SingleOrDefault(x => x.Id == id);
    return user;
}

public UnitResult<ChangePasswordError> ChangePassword(string password)
{
    if (!IsAllowed(password))
        return new ChangePasswordError.InvalidPassword();

    SetPassword(password);
    return new Success();
}
// snippet:end

}
