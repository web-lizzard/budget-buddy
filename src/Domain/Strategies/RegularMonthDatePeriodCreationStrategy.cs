using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Strategies;


internal sealed class RegularMonthDatePeriodCreationStrategy : DatePeriodCreationStrategy
{
    public bool CanApply(DatePeriodSchema.Type schema)
    {
        return schema is DatePeriodSchema.Type.NTH_REGULAR_DAY;
    }

    public Task<DatePeriod> CreatePeriod(Date startDate, DatePeriodSchema day)
    {
        var year = startDate.Value.Month == 12 ? startDate.Value.Year + 1 : startDate.Value.Year;
        var month = startDate.Value.Month == 12 ? 1 : startDate.Value.Month + 1;
        var startMonth = new DateTime(year, month, day.Day);

        return Task.FromResult(new DatePeriod(startDate, new Date(startMonth)));
    }
}