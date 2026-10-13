namespace SnippetFixtures.Logging01;

using Microsoft.Extensions.Logging;

internal static partial class Log01
{
// snippet:begin
[LoggerMessage(Level = LogLevel.Information, Message = "Published {Count} order events")]
internal static partial void PublishedOrderEvents(this ILogger logger, int count);
// snippet:end

}
