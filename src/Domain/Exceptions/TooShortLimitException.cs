
using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Exceptions;

public class TooShortLimitException(Monetary limit) : DomainException($"Limit is too short {limit}")
{
}