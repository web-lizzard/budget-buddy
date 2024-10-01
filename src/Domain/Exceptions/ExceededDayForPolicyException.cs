using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Exceptions;

public class ExceededDayForPolicy(int day, int breakpoint) : DomainException($"Exceeded day {day} for policy. For this policy breakpoint is {breakpoint}") { }