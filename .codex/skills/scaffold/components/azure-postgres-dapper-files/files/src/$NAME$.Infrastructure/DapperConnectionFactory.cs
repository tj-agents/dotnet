using System.Data.Common;
using Npgsql;

namespace $NAME$.Infrastructure;

internal sealed class DapperConnectionFactory : IDapperConnectionFactory
{
    private readonly NpgsqlDataSource dataSource;

    public DapperConnectionFactory(NpgsqlDataSource dataSource)
    {
        this.dataSource = dataSource;
    }

    public DbConnection CreateConnection() => this.dataSource.CreateConnection();
}
