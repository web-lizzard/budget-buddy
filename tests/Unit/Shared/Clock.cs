using BudgetBuddy.Domain.Ports;

namespace Unit.Shared;

internal class TestClock : Clock
{
    public DateTime Current() => new(2022, 08, 11, 16, 0, 0);
}