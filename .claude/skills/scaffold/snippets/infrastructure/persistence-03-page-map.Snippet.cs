namespace SnippetFixtures.Persistence03;

internal sealed record QueueItem;
internal sealed record QueueItemDto;
internal static class QueueItemMappers
{
    extension(QueueItem item)
    {
        public QueueItemDto ToDto() => new();
    }
}
internal sealed record PageParams;
internal interface IReportRepository { Task<IPagination<QueueItem>> GetQueueAsync(PageParams pageParams); }

internal static class Example
{
    public static async Task<IPagination<QueueItemDto>> Run(IReportRepository reportRepository, PageParams pageParams)
    {
        // snippet:begin
return (await reportRepository.GetQueueAsync(pageParams).ConfigureAwait(false)).Map(r => r.ToDto());
// snippet:end

    }
}
