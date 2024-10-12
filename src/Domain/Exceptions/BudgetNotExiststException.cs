namespace BudgetBuddy.Domain.Exceptions;

public sealed class BudgetNotExistsException(Guid id) : DomainException($"Budget for given id: {id} doest not exist");