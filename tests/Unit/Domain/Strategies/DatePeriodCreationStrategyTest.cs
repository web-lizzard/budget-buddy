using BudgetBuddy.Domain.Ports;
using BudgetBuddy.Domain.Strategies;
using BudgetBuddy.Domain.ValueObjects;
using Shouldly;

namespace Unit.Domain.Strategies;

public class DatePeriodCreationStrategyTest
{
    private readonly Clock _clock;

    public DatePeriodCreationStrategyTest()
    {
        _clock = new TestClock();
    }

    [Fact]
    public void should_returns_true_when_input_match_to_schema_type()
    {
        var inputType = DatePeriodSchema.Type.NTH_REGULAR_DAY;
        var strategy = new RegularMonthDatePeriodCreationStrategy();

        var canApply = strategy.CanApply(inputType);

        canApply.ShouldBe(true);
    }

    [Fact]
    public async void should_returns_computed_date_period_calculated_by_strategy()
    {
        var now = new Date(_clock.Current());
        var schema = new DatePeriodSchema(5, DatePeriodSchema.Type.NTH_WORKING_DAY);
        var strategy = new RegularMonthDatePeriodCreationStrategy();
        var expectedDateRange = new DatePeriod(now, GetEndDate(5));

        var result = await strategy.CreatePeriod(now, schema);

        result.ShouldBe(expectedDateRange);
    }

    private Date GetEndDate(int day)
    {
        return new Date(
            new DateTime(2022, 09, day, 0, 0, 0)
        );
    }



    private class TestClock : Clock
    {
        public DateTime Current()
        {
            return new(2022, 08, 11, 0, 0, 0);
        }
    }

}