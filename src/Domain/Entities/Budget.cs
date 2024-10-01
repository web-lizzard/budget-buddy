using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Eniities;
public sealed class Budget(Guid id, string name, int limit, IEnumerable<User> users, Date startDate, Date endDate, string creationPolicy)
{
    public Guid Id { get; } = id;
    public Name Name { get; } = name;
    public int Limit { get; } = limit;
    public IEnumerable<User> Users { get; } = users;
    public Date StartDate { get; } = startDate;
    public Date EndDate { get; } = endDate;
    public string CreationPolicy { get; } = creationPolicy;
}