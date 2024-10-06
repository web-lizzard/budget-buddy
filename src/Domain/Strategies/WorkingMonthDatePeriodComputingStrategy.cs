using BudgetBuddy.Domain.Ports;
using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Strategies;

internal sealed class WorkingDayDatePeriodComputingStrategy(WorkingDayChecker workingDayChecker) : DatePeriodComputingStrategy
{

    private readonly WorkingDayChecker _workingDayChecker = workingDayChecker;
    public bool CanApply(PeriodSchema.Type schema)
    {
        return schema is PeriodSchema.Type.NTH_WORKING_DAY;
    }

    public async Task<DatePeriod> ComputeDatePeriod(Date startDate, PeriodSchema schema)
    {
        var year = startDate.Value.Month is 12 ? startDate.Value.Year + 1 : startDate.Value.Year;
        var month = startDate.Value.Month is 12 ? 1 : startDate.Value.Month + 1;
        var workingDayCount = 0;
        var currentDate = new DateTime(year, month, 1);

        while (currentDate.Month == month)
        {
            var date = new Date(currentDate);
            if (await _workingDayChecker.isWorkingDay(date))
            {
                workingDayCount++;
            }

            if (workingDayCount == schema.Day)
            {
                break;
            }

            currentDate = currentDate.AddDays(1);
        }

        return new DatePeriod(startDate, new Date(currentDate));
    }
}