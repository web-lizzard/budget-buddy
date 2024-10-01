using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Eniities;
public sealed class Budget(Guid id, string name, int limit, IEnumerable<string> users, Date startDate, Date endDate, string creationPolicy)
{
    public Guid Id { get; } = id;
    public string Name { get; } = name;
    public int Limit { get; } = limit;
    public IEnumerable<string> Users { get; } = users;
    public Date StartDate { get; } = startDate;
    public Date EndDate { get; } = endDate;
    public string CreationPolicy { get; } = creationPolicy;
}