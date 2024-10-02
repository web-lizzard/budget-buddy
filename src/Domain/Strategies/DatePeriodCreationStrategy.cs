using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Strategies;

public interface DatePeriodCreationStrategy
{
    public bool CanApply(DatePeriodSchema.Type schema);

    public Task<DatePeriod> CreatePeriod(Date startDate, DatePeriodSchema day);
}
