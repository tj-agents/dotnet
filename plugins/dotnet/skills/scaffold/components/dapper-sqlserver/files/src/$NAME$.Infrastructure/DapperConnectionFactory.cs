using System.Data.Common;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Configuration;

namespace $NAME$.Infrastructure;

internal sealed class DapperConnectionFactory : IDapperConnectionFactory
{
    private readonly string connectionString;

    public DapperConnectionFactory(IConfiguration configuration)
    {
        connectionString = configuration.GetConnectionString("SqlServer")
            ?? throw new InvalidOperationException("Connection string 'SqlServer' is required.");
    }

    public DbConnection CreateConnection() => new SqlConnection(connectionString);
}
