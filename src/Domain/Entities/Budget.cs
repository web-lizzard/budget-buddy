using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Eniities;
public sealed class Budget(Guid id,
    Name name,
    Limit limit,
    IEnumerable<User> users,
    Date startDate,
    Date endDate,
    DatePeriodSchema datePeriodSchema)
{
    public Guid Id { get; } = id;
    public Name Name { get; } = name;
    public Limit Limit { get; } = limit;
    public IEnumerable<User> Users { get; } = users;
    public Date StartDate { get; } = startDate;
    public Date EndDate { get; } = endDate;
    public DatePeriodSchema DatePeriodSchema { get; } = datePeriodSchema;
}