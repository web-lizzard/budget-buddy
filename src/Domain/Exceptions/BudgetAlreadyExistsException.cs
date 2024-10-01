namespace BudgetBuddy.Domain.Exceptions;

public class BudgetAlreadyExistsException(string name) : DomainException($"Budget already Exists: {name}") { }