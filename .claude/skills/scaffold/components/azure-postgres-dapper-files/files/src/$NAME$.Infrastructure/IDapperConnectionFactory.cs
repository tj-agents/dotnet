using System.Data.Common;

namespace $NAME$.Infrastructure;

public interface IDapperConnectionFactory
{
    DbConnection CreateConnection();
}
