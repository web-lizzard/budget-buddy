namespace BudgetBuddy.Domain.Exceptions;

public class ExceededDayForPeriodSchemaException(int day, int breakpoint) : DomainException($"Exceeded day {day} for policy. For this policy breakpoint is {breakpoint}") { }