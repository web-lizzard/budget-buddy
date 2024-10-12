namespace BudgetBuddy.Domain.Exceptions;

public sealed class BudgetNotExistsException(string id) : DomainException($"Budget for given id: {id} doest not exist");