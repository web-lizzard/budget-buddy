using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Strategies;


internal sealed class RegularMonthDatePeriodComputingStrategy : DatePeriodComputingStrategy
{
    public bool CanApply(DatePeriodSchema.Type schema)
    {
        return schema is DatePeriodSchema.Type.NTH_REGULAR_DAY;
    }

    public Task<DatePeriod> ComputeDatePeriod(Date startDate, DatePeriodSchema schema)
    {
        var year = startDate.Value.Month == 12 ? startDate.Value.Year + 1 : startDate.Value.Year;
        var month = startDate.Value.Month == 12 ? 1 : startDate.Value.Month + 1;
        var startMonth = new DateTime(year, month, schema.Day);

        return Task.FromResult(new DatePeriod(startDate, new Date(startMonth)));
    }
}