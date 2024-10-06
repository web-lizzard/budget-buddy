using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Application.Commands;

public sealed record CreateBudget(Date StartDate,
    IEnumerable<User> Users,
    Name Name,
    Limit Limit,
    PeriodSchema DatePeriodSchema);