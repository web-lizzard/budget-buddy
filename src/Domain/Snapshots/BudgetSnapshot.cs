using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Snapshots;

public sealed class BudgetSnapshot(Guid id,
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
    public DatePeriod DatePeriod { get; } = datePeriod;
    public DatePeriodSchema DatePeriodSchema { get; } = datePeriodSchema;


}