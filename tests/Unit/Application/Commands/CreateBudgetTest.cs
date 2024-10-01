using BudgetBuddy.Application.Commands;
using BudgetBuddy.Application.Commands.Handlers;
using BudgetBuddy.Domain.Exceptions;
using BudgetBuddy.Domain.Ports;
using BudgetBuddy.Domain.ValueObjects;
using Shouldly;
using Unit.Shared;

namespace Unit.Application.Commands;
public class CreateBudgetTests
{

    private readonly Clock _clock;
    private readonly CreateBudgetHandler _handler;
    public CreateBudgetTests()
    {
        _clock = new TestClock();
        _handler = new CreateBudgetHandler(_clock);
    }

    [Fact]
    public async void should_fail_if_date_is_past()
    {
        var command = new CreateBudget(
           new Date(_clock.Current()).AddDays(-1)
        );
        var record = await Record.ExceptionAsync(async () => await _handler.Handle(command));

        record.ShouldBeOfType<InvalidDateException>();
    }

    [Fact]
    public async void should_fail_if_budget_already_exist()
    {
        var command = new CreateBudget(new Date(_clock.Current()));
        var record = await Record.ExceptionAsync(async () => await _handler.Handle(command));

        record.ShouldBeOfType<BudgetAlreadyExistsException>();
    }


}