using BudgetBuddy.Adapters.Repositories;
using BudgetBuddy.Application.Commands;
using BudgetBuddy.Application.Commands.Handlers;
using BudgetBuddy.Domain.Eniities;
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
    private readonly BudgetRepository _repository;
    public CreateBudgetTests()
    {
        _clock = new TestClock();
        _repository = new InMemoryBudgetRepository();
        _handler = new CreateBudgetHandler(_clock, _repository);
    }

    [Fact]
    public async void should_fail_if_date_is_past()
    {
        var command = new CreateBudget(
            new Date(_clock.Current()).AddDays(-1),
            [Guid.Empty],
            "test");
        var record = await Record.ExceptionAsync(async () => await _handler.Handle(command));

        record.ShouldBeOfType<InvalidDateException>();
    }

    [Fact]
    public async void should_fail_if_budget_with_given_name_for_given_users_already_exist()
    {
        var command = new CreateBudget(new Date(_clock.Current()), [Guid.Empty], "test");
        var id = Guid.NewGuid();
        await _repository.Save(new Budget(id,
            "test",
            100000,
            [Guid.Empty],
            command.StartDate,
            command.StartDate.AddDays(40),
            "Every 5th working day")
            );
        var record = await Record.ExceptionAsync(async () => await _handler.Handle(command));

        record.ShouldBeOfType<BudgetAlreadyExistsException>();
    }


}