using BudgetBuddy.Domain.Strategies;
using BudgetBuddy.Domain.ValueObjects;
using Shouldly;

namespace Unit.Domain.Strategies;

public class DatePeriodCreationStrategyTest
{

    [Fact]
    public void should_returns_true_when_input_match_to_schema_type()
    {
        var inputType = DatePeriodSchema.Type.NTH_REGULAR_DAY;
        var strategy = new RegularMonthDatePeriodCreationStrategy();

        var canApply = strategy.CanApply(inputType);

        canApply.ShouldBe(true);
    }

}