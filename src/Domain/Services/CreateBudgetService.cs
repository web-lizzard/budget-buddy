using BudgetBuddy.Domain.Eniities;
using BudgetBuddy.Domain.Snapshots;
using BudgetBuddy.Domain.Strategies;
using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Services;


public sealed class CreateBudgetService(IEnumerable<DatePeriodComputingStrategy> strategies)
{

    private readonly IEnumerable<DatePeriodComputingStrategy> _strategies = strategies;

    public async Task<Budget> CreateBudget(Date startDate,
                               IEnumerable<User> users,
                               Name name,
                               Limit limit,
                               DatePeriodSchema datePeriodSchema)
    {
        var strategy = _strategies.Single((s) => s.CanApply(datePeriodSchema.Policy));
        var datePeriod = await strategy.ComputeDatePeriod(startDate, datePeriodSchema);
        var id = Guid.NewGuid();
        var snapshot = new BudgetSnapshot(id, name, limit, users, datePeriod, datePeriodSchema);
        return Budget.From(snapshot);
    }

}