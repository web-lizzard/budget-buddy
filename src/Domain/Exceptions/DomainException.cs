namespace BudgetBuddy.Domain.Exceptions;

public abstract class DomainException(string message) : Exception(message) { }