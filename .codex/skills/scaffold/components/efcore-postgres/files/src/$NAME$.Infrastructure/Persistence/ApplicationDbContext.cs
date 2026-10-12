using Microsoft.EntityFrameworkCore;

namespace $NAME$.Infrastructure.Persistence;

public sealed class ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : DbContext(options);
