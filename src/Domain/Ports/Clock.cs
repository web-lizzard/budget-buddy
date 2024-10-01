namespace BudgetBuddy.Domain.Ports;

public interface Clock
{
    DateTime Current();
}