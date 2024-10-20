using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Eniities;

public sealed class Pocket
{
    public Limit Limit { get; }


    public Pocket(Limit limit)
    {
        Limit = limit;
    }
}