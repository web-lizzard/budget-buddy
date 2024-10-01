namespace BudgetBuddy.Domain.ValueObjects;
public record Name
{
    public Name(string value)
    {
        Value = value;
    }

    public string Value { get; private set; }

    public static implicit operator string(Name name) => name.Value;
    public static implicit operator Name(string value) => new(value);
}