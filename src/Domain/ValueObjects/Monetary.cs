using BudgetBuddy.Domain.Exceptions;

namespace BudgetBuddy.Domain.ValueObjects;

public sealed record Monetary
{

    public int Value { get; private set; }
    public Currency Currency { get; private set; }

    public Monetary(int value, Currency currency)
    {
        SetMonetary(value);
        Currency = currency;
    }

    public Monetary(Limit value, Currency currency)
    {
        SetMonetary(value.Value.Value);
        Currency = currency;
    }


    private void SetMonetary(int value)
    {
        if (value < 100)
        {
            throw new InvalidMonetaryValueException(value);
        }

        Value = value;
    }


}