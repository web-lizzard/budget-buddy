using BudgetBuddy.Domain.Exceptions;

namespace BudgetBuddy.Domain.ValueObjects;
public record Name
{
    public Name(string value)
    {
        SetName(value);
    }

    private void SetName(string value)
    {
        if (value.Length is < 3)
        {
            throw new BudgetNameTooShortException(value);
        }

        Value = value;
    }

    public string Value { get; private set; }

    public static implicit operator string(Name name) => name.Value;
    public static implicit operator Name(string value) => new(value);
}