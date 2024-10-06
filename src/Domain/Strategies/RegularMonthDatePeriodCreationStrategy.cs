using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Strategies;


internal sealed class RegularMonthDatePeriodComputingStrategy : DatePeriodComputingStrategy
{
    public bool CanApply(PeriodSchema.Type schema)
    {
        return schema is PeriodSchema.Type.NTH_REGULAR_DAY;
    }

    public Task<DatePeriod> ComputeDatePeriod(Date startDate, PeriodSchema schema)
    {
        var year = startDate.Value.Month == 12 ? startDate.Value.Year + 1 : startDate.Value.Year;
        var month = startDate.Value.Month == 12 ? 1 : startDate.Value.Month + 1;
        var startMonth = new DateTime(year, month, schema.Day);

        return Task.FromResult(new DatePeriod(startDate, new Date(startMonth)));
    }
}