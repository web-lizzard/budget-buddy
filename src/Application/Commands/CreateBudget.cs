using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Application.Commands;

public sealed record CreateBudget(Date StartDate, IEnumerable<string> Users, string Name);