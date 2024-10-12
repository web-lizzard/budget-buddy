namespace BudgetBuddy.Domain.Exceptions;


public sealed class PocketLimitExceedBudgetLimitException() : DomainException("Limit of the pocket exceed parent budget limit");