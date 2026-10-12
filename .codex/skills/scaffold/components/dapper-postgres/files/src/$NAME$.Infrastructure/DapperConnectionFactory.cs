using System.Data.Common;
using Microsoft.Extensions.Configuration;
using Npgsql;

namespace $NAME$.Infrastructure;

internal sealed class DapperConnectionFactory : IDapperConnectionFactory
{
    private readonly string connectionString;

    public DapperConnectionFactory(IConfiguration configuration)
    {
        this.connectionString = configuration.GetConnectionString("Postgres")
            ?? throw new InvalidOperationException("Connection string 'Postgres' is required.");
    }

    public DbConnection CreateConnection() => new NpgsqlConnection(this.connectionString);
}
