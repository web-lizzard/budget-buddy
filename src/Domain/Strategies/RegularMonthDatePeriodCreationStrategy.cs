using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Strategies;


internal sealed class RegularMonthDatePeriodCreationStrategy : DatePeriodCreationStrategy
{
    public bool CanApply(DatePeriodSchema.Type schema)
    {
        throw new NotImplementedException();
    }

    public Task<DatePeriod> CreatePeriod(Date startDate)
    {
        throw new NotImplementedException();
    }
}