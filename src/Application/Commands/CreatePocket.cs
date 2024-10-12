using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Application.Commands;


public record CreatePocket(Guid BudgetId, Limit limit);