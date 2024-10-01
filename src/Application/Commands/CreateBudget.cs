using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Application.Commands;

public sealed record CreateBudget(Date StartDate,
    Date EndDate,
    IEnumerable<User> Users,
    Name Name,
    Limit Limit,
    DatePeriodSchema DatePeriodSchema);