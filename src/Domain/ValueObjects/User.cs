namespace BudgetBuddy.Domain.ValueObjects;

public record User(Guid Value)
{
    public static implicit operator Guid(User user) => user.Value;
    public static implicit operator User(Guid id) => new(id);
}