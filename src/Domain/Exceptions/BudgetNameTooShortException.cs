namespace BudgetBuddy.Domain.Exceptions;

public class BudgetNameTooShortException(string name) : DomainException($"Budget name: {name} is too short") { }