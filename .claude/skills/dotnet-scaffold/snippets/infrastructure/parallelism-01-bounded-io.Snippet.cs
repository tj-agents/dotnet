namespace SnippetFixtures.Parallelism01;

using System.Collections.Concurrent;
using System.Net.Http;

public sealed record UserEnsureFailure(int UserId, string Message);
public sealed record UserEnsureOutcome(int Ensured, IReadOnlyList<UserEnsureFailure> Failures);

public static class UserEnsurer
{
// snippet:begin
public static async Task<UserEnsureOutcome> EnsureUsersAsync(
    HttpClient httpClient, IReadOnlyList<int> userIds, CancellationToken ct)
{
    var ensured = 0;
    var failures = new ConcurrentBag<UserEnsureFailure>();
    var parallelOptions = new ParallelOptions
    {
        // This downstream permits five concurrent requests per batch within the shared capacity budget.
        MaxDegreeOfParallelism = 5,
        CancellationToken = ct
    };

    await Parallel.ForEachAsync(userIds, parallelOptions, async (userId, token) =>
    {
        try
        {
            using var response = await httpClient.PostAsync($"users/{userId}/ensure", null, token).ConfigureAwait(false);
            if (response.IsSuccessStatusCode)
                Interlocked.Increment(ref ensured);
            else
                failures.Add(new UserEnsureFailure(userId, $"Ensure returned {(int)response.StatusCode}."));
        }
        catch (Exception exception) when (exception is not OperationCanceledException || !token.IsCancellationRequested)
        {
            failures.Add(new UserEnsureFailure(userId, exception.Message));
        }
    }).ConfigureAwait(false);

    return new UserEnsureOutcome(ensured, failures
        .OrderBy(failure => failure.UserId)
        .ThenBy(failure => failure.Message, StringComparer.Ordinal)
        .ToList());
}
// snippet:end

}
