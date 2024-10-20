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

    public Monetary(Limit limit, Currency currency)
    {
        SetMonetary(limit.Value.Value);
        Currency = currency;
    }


    private void SetMonetary(int value)
    {
        if (value % 100 != 0 && value != 0)
        {
            throw new InvalidMonetaryValueException(value);
        }

        Value = value;
    }



    public static Monetary operator +(Monetary monetary1, Monetary monetary2)
    {
        return new Monetary(monetary1.Value + monetary2.Value, monetary1.Currency);
    }

    public static Monetary operator -(Monetary monetary1, Monetary monetary2)
    {
        return new Monetary(monetary1.Value - monetary2.Value, monetary1.Currency);
    }

    public static bool operator >(Monetary monetary1, Monetary monetary2)
    {
        return monetary1.Value > monetary2.Value;
    }

    public static bool operator <(Monetary monetary1, Monetary monetary2)
    {
        return monetary1.Value < monetary2.Value;
    }

    public static bool operator >=(Monetary monetary1, Monetary monetary2)
    {
        return monetary1.Value >= monetary2.Value;
    }

    public static bool operator <=(Monetary monetary1, Monetary monetary2)
    {
        return monetary1.Value <= monetary2.Value;
    }

}