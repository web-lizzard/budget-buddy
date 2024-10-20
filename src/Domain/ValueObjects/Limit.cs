using BudgetBuddy.Domain.Exceptions;

namespace BudgetBuddy.Domain.ValueObjects;

public sealed record Limit
{
    public Monetary Value { get; private set; }
    public Currency Currency
    {
        get
        {
            return Value.Currency;
        }
    }
    public const int LimitBreakpoint = 30000;

    public Limit(Monetary value) => SetValue(value);


    private void SetValue(Monetary value)
    {
        if (value.Value < LimitBreakpoint)
        {
            throw new TooShortLimitException(value);
        }
        Value = value;
    }


    public static implicit operator Limit(Monetary monetary) => new(monetary);
    public static implicit operator Monetary(Limit value) => new(value.Value, value.Currency);

    public static Limit operator +(Limit limit1, Limit limit2)
    {
        return new Limit(limit1.Value + limit2.Value);
    }

    public static Limit operator -(Limit limit1, Limit limit2)
    {
        return new Limit(limit1.Value - limit2.Value);
    }


    public static bool operator >(Limit Limit1, Limit Limit2)
    {
        return Limit1.Value > Limit2.Value;
    }

    public static bool operator <(Limit Limit1, Limit Limit2)
    {
        return Limit1.Value < Limit2.Value;
    }

    public static bool operator >=(Limit Limit1, Limit Limit2)
    {
        return Limit1.Value >= Limit2.Value;
    }

    public static bool operator <=(Limit Limit1, Limit limit2)
    {
        return Limit1.Value <= limit2.Value;
    }

}