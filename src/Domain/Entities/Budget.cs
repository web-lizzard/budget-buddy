using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Eniities;
public sealed class Budget(Guid id,
    Name name,
    Limit limit,
    IEnumerable<User> users,
    DatePeriod datePeriod,
    DatePeriodSchema datePeriodSchema)
{
    public Guid Id { get; } = id;
    public Name Name { get; } = name;
    public Limit Limit { get; } = limit;
    public IEnumerable<User> Users { get; } = users;
    public DatePeriod datePeriod { get; } = datePeriod;
    public DatePeriodSchema DatePeriodSchema { get; } = datePeriodSchema;
}