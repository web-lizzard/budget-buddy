using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Strategies;

internal sealed class WorkingDayDatePeriodComputingStrategy : DatePeriodComputingStrategy
{
    public bool CanApply(DatePeriodSchema.Type schema)
    {
        return schema is DatePeriodSchema.Type.NTH_WORKING_DAY;
    }

    public Task<DatePeriod> ComputeDatePeriod(Date startDate, DatePeriodSchema schema)
    {
        throw new NotImplementedException();
    }
}