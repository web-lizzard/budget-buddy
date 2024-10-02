using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Strategies;

public interface DatePeriodComputingStrategy
{
    public bool CanApply(DatePeriodSchema.Type schema);

    public Task<DatePeriod> ComputeDatePeriod(Date startDate, DatePeriodSchema schema);
}
