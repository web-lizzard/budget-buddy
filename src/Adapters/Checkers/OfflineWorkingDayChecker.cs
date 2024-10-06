using BudgetBuddy.Domain.Ports;
using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Adapters.Checkers;

internal sealed class OfflineWorkingDayChecker : WorkingDayChecker
{
    private readonly Dictionary<string, string> worldWideHolidays;

    public OfflineWorkingDayChecker()
    {
        worldWideHolidays = new Dictionary<string, string> {
        { "01-01", "New Year's Day" },
        { "01-06", "Epiphany" },
        { "05-01", "International Workers' Day" },
        { "11-01", "All Saints' Day" },
        { "11-11", "Armistice Day / Veterans Day" },
        { "12-25", "Christmas" },
        { "12-26", "Boxing Day" },
    };
    }

    public Task<bool> isWorkingDay(Date day)
    {
        var isWorkingDay = !isWekend(day) && !isPublicHoliday(day);
        return Task.FromResult(isWorkingDay);
    }

    private bool isWekend(Date day)
    {
        var dayOfWeek = day.Value.DayOfWeek;

        return dayOfWeek is DayOfWeek.Sunday | dayOfWeek is DayOfWeek.Saturday;
    }

    private bool isPublicHoliday(Date day)
    {

        var key = BuildKey(day);
        return worldWideHolidays.ContainsKey(key);

    }

    private string BuildKey(Date day)
    {
        var monthPrefix = day.Value.Month is <= 9 ? $"0{day.Value.Month}" : $"{day.Value.Month}";
        var daySufix = day.Value.Day is <= 9 ? $"0{day.Value.Day}" : $"{day.Value.Day}";

        return monthPrefix + "-" + daySufix;
    }
}