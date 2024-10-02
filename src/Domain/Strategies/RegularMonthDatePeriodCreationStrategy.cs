using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Strategies;


internal sealed class RegularMonthDatePeriodCreationStrategy : DatePeriodCreationStrategy
{
    public bool CanApply(DatePeriodSchema.Type schema)
    {
        return schema is DatePeriodSchema.Type.NTH_REGULAR_DAY;
    }

    public Task<DatePeriod> CreatePeriod(Date startDate)
    {
        throw new NotImplementedException();
    }
}