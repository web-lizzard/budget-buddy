using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Strategies;

public interface DatePeriodComputingStrategy
{
    public bool CanApply(PeriodSchema.Type schema);

    public Task<DatePeriod> ComputeDatePeriod(Date startDate, PeriodSchema schema);
}
