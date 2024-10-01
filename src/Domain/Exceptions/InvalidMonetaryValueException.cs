namespace BudgetBuddy.Domain.Exceptions;

public class InvalidMonetaryValueException(int value) : DomainException($"Monetary can't be lower than 100, which is correspond for small monetary unit: {value}") { }