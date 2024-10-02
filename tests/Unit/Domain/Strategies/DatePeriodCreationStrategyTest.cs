using BudgetBuddy.Domain.Exceptions;
using BudgetBuddy.Domain.Strategies;
using BudgetBuddy.Domain.ValueObjects;
using Shouldly;

namespace Unit.Domain.Strategies;

public class RegularDatePeriodComputingStrategyTest
{

    private readonly RegularMonthDatePeriodComputingStrategy _strategy;
    public RegularDatePeriodComputingStrategyTest()
    {
        _strategy = new RegularMonthDatePeriodComputingStrategy();
    }

    [Fact]
    public void should_returns_true_when_input_match_to_schema_type()
    {
        var inputType = DatePeriodSchema.Type.NTH_REGULAR_DAY;

        var canApply = _strategy.CanApply(inputType);

        canApply.ShouldBe(true);
    }

    [Fact]
    public void should_fail_if_expected_day_is_above_breakpoint()
    {
        var record = Record.Exception(() => new DatePeriodSchema(29, DatePeriodSchema.Type.NTH_REGULAR_DAY));

        record.ShouldBeOfType<ExceededDayForPeriodSchemaException>();

    }

    [Theory]
    [InlineData("2022-08-15", "2022-09-0", 6)]
    [InlineData("2022-12-03", "2023-01-", 16)]
    public async void should_returns_computed_date_period_calculated_by_strategy(string startDate, string endDate, int expectedEndDay)
    {
        var now = new Date(DateTime.Parse(startDate));
        var schema = new DatePeriodSchema(expectedEndDay, DatePeriodSchema.Type.NTH_REGULAR_DAY);
        var expectedDateRange = new DatePeriod(now, new Date(DateTime.Parse(endDate + expectedEndDay)));

        var result = await _strategy.ComputeDatePeriod(now, schema);

        result.ShouldBe(expectedDateRange);
    }
}


public class WorkingDayDatePeriodComputingStrategyTest
{
    private readonly WorkingDayDatePeriodComputingStrategy _strategy;

    public WorkingDayDatePeriodComputingStrategyTest()
    {
        _strategy = new WorkingDayDatePeriodComputingStrategy();
    }

    [Fact]
    public void should_returns_true_when_input_match_to_schema_type()
    {
        // Given
        var inputType = DatePeriodSchema.Type.NTH_WORKING_DAY;
        // When
        var canApply = _strategy.CanApply(inputType);
        // Then

        canApply.ShouldBe(true);
    }
}
