using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Exceptions;

public class InvalidDateException(Date date) : DomainException($"Invalid Date {date}") { }