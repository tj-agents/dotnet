namespace SnippetFixtures.ErrorsTerminals01;

using Microsoft.AspNetCore.Mvc;

internal sealed record ArtistDetails
{
    public object ToDetailsResponse() => this;
}

internal abstract record GetArtistError : IError
{
    public sealed record ArtistNotFound : GetArtistError;
    public ErrorDefinition Definition => ErrorDefinition.NotFound<GetArtistError>();
}

internal static class ResultWebExtensions
{
    public static IActionResult ToOkOr<T>(this Option<T> option, Func<IActionResult> onNone) =>
        option.Match(value => new OkObjectResult(value), onNone);

    public static IActionResult ToOkOr<T, TMapped>(this Option<T> option, Func<T, TMapped> map, Func<IActionResult> onNone) =>
        option.Match(value => (IActionResult)new OkObjectResult(map(value)), onNone);

    public static IActionResult ToOkOrProblem<T, TMapped, TError>(this Result<T, TError> result, Func<T, TMapped> map)
        where TError : IError =>
        result.Match(
            value => (IActionResult)new OkObjectResult(map(value)),
            error => new ObjectResult(error.Definition.Message) { StatusCode = 400 });
}

internal sealed class ArtistController : ControllerBase
{
    private static IActionResult Unauthorized2() => new UnauthorizedResult();
    private static IActionResult NotFound2() => new NotFoundResult();

    public IActionResult Get(Option<string> user, Option<ArtistDetails> artist, Result<ArtistDetails, GetArtistError> artistResult)
    {
#pragma warning disable CS0162
// snippet:begin
return user.ToOkOr(Unauthorized);
return artist.ToOkOr(value => value.ToDetailsResponse(), NotFound);
return artistResult.ToOkOrProblem(value => value.ToDetailsResponse());
// snippet:end

        return Unauthorized2();
#pragma warning restore CS0162
    }
}
