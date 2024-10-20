using BudgetBuddy.Domain.Snapshots;
using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Eniities;
public sealed class Budget
{

    private Guid Id { get; }
    private Name Name { get; }
    private Limit Limit { get; }
    private IEnumerable<User> Users { get; }
    private DatePeriod DatePeriod { get; }
    private PeriodSchema DatePeriodSchema { get; }

    private Currency Currency
    {
        get
        {
            return Limit.Currency;
        }
    }

    private readonly HashSet<Pocket> _pockets = [];

    private Budget(Guid id,
        Name name,
        Limit limit,
        IEnumerable<User> users,
        DatePeriod datePeriod,
        PeriodSchema datePeriodSchema)
    {
        Id = id;
        Name = name;
        Limit = limit;
        Users = users;
        DatePeriod = datePeriod;
        DatePeriodSchema = datePeriodSchema;
    }

    public BudgetSnapshot Snapshot
    {
        get
        {
            return new BudgetSnapshot(Id, Name, Limit, Users, DatePeriod, DatePeriodSchema);
        }
    }

    internal static Budget From(BudgetSnapshot snapshot)
    {
        return new Budget(
            snapshot.Id, snapshot.Name, snapshot.Limit, snapshot.Users, snapshot.DatePeriod, snapshot.DatePeriodSchema
        );
    }

    public bool IsLimitExceedingBudgetRemainsLimit(Limit limit)
    {
        var pocketLimits = ComputeSumOfPocketsLimit();
        var remainLimit = Limit.Value - pocketLimits;
        return limit.Value > remainLimit;
    }


    private Monetary ComputeSumOfPocketsLimit()
    {
        return _pockets.Aggregate(new Monetary(0, Currency), (total, next) => total + next.Limit.Value);
    }
}