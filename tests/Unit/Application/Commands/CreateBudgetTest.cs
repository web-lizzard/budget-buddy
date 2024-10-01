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
            new Date(_clock.Current()).AddDays(-1),
            [Guid.Empty],
            "test", new Monetary(100000, Currency.USD), new DatePeriodSchema(10, DatePeriodSchema.Type.NTH_WORKING_DAY));
        var record = await Record.ExceptionAsync(async () => await _handler.Handle(command));

        record.ShouldBeOfType<InvalidDateException>();
    }

    [Fact]
    public async void should_fail_if_budget_with_given_name_for_given_users_already_exist()
    {
        var command = new CreateBudget(new Date(_clock.Current()), new Date(_clock.Current()), [Guid.Empty], "test", new Monetary(
            100000, Currency.USD), new DatePeriodSchema(1, DatePeriodSchema.Type.NTH_WORKING_DAY));
        var id = Guid.NewGuid();
        await _repository.Save(new Budget(id,
            "test",
            new Monetary(100000, Currency.USD),
            [Guid.Empty],
            command.StartDate,
            command.StartDate.AddDays(40),
            command.DatePeriodSchema)
            );
        var record = await Record.ExceptionAsync(async () => await _handler.Handle(command));

        record.ShouldBeOfType<BudgetAlreadyExistsException>();
    }

    [Fact]
    public void should_fail_if_budget_name_is_too_short()
    {
        var record = Record.Exception(() => new CreateBudget(new Date(_clock.Current()), new Date(_clock.Current()),
            [Guid.Empty],
            "sh",
            new Monetary(100000, Currency.USD), new DatePeriodSchema(11, DatePeriodSchema.Type.NTH_WORKING_DAY)));

        record.ShouldBeOfType<BudgetNameTooShortException>();
    }

    [Fact]
    public void should_fail_if_limit_is_too_low()
    {
        var record = Record.Exception(() => new CreateBudget
        (new Date(_clock.Current()),
        new Date(_clock.Current()).AddDays(40),
            [Guid.Empty],
            "test",
            new Monetary(10000, Currency.USD), new DatePeriodSchema(12, DatePeriodSchema.Type.NTH_WORKING_DAY)));

        record.ShouldBeOfType<TooShortLimitException>();
    }


    [Fact]
    public async void should_succed_with_correct_command()
    {
        var command = new CreateBudget(
            new Date(_clock.Current()), new Date(_clock.Current()).AddDays(50), [Guid.Empty], "test", new Monetary(100000,
                Currency.USD), new DatePeriodSchema(10, DatePeriodSchema.Type.NTH_WORKING_DAY)
        );

        await _handler.Handle(command);
        (await _repository.isBudgetExist(command.Name, command.Users)).ShouldBe(true);
    }

}