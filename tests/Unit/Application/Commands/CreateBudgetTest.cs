using BudgetBuddy.Adapters.Checkers;
using BudgetBuddy.Adapters.Repositories;
using BudgetBuddy.Application.Commands;
using BudgetBuddy.Application.Commands.Handlers;
using BudgetBuddy.Domain.Exceptions;
using BudgetBuddy.Domain.Ports;
using BudgetBuddy.Domain.Services;
using BudgetBuddy.Domain.Strategies;
using BudgetBuddy.Domain.ValueObjects;
using Shouldly;
using Unit.Shared;

namespace Unit.Application.Commands;
public class CreateBudgetTests
{

    private readonly Clock _clock;
    private readonly CreateBudgetHandler _handler;
    private readonly BudgetRepository _repository;

    private readonly CreateBudgetService _service;

    public CreateBudgetTests()
    {
        _clock = new TestClock();
        _repository = new InMemoryBudgetRepository();

        var checker = new OfflineWorkingDayChecker();
        IEnumerable<DatePeriodComputingStrategy> strategies = [new WorkingDayDatePeriodComputingStrategy(checker), new RegularMonthDatePeriodComputingStrategy()];
        _service = new CreateBudgetService(strategies);
        _handler = new CreateBudgetHandler(_clock, _repository, _service);
    }

    [Fact]
    public async void should_fail_if_date_is_past()
    {
        var command = new CreateBudget(
            new Date(_clock.Current()).AddDays(-1),
            [Guid.Empty],
            "test", new Monetary(100000, Currency.USD), new DatePeriodSchema(10, DatePeriodSchema.Type.NTH_WORKING_DAY));
        var record = await Record.ExceptionAsync(async () => await _handler.Handle(command));

        record.ShouldBeOfType<InvalidDateException>();
    }

    [Fact]
    public async void should_fail_if_budget_with_given_name_for_given_users_already_exist()
    {
        var command = new CreateBudget(new Date(_clock.Current()), [Guid.Empty], "test", new Monetary(
            100000, Currency.USD), new DatePeriodSchema(1, DatePeriodSchema.Type.NTH_WORKING_DAY));


        await _repository.Save(
            await _service.CreateBudget(command.StartDate, command.Users, command.Name, command.Limit, command.DatePeriodSchema)
        );
        var record = await Record.ExceptionAsync(async () => await _handler.Handle(command));

        record.ShouldBeOfType<BudgetAlreadyExistsException>();
    }

    [Fact]
    public void should_fail_if_budget_name_is_too_short()
    {
        var record = Record.Exception(() => new CreateBudget(new Date(_clock.Current()),
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
            [Guid.Empty],
            "test",
            new Monetary(10000, Currency.USD), new DatePeriodSchema(12, DatePeriodSchema.Type.NTH_WORKING_DAY)));

        record.ShouldBeOfType<TooShortLimitException>();
    }

    [Theory]
    [InlineData(30, DatePeriodSchema.Type.NTH_REGULAR_DAY)]
    [InlineData(21, DatePeriodSchema.Type.NTH_WORKING_DAY)]
    public void should_faild_if_day_in_budget_schema_is_exceeded(int day, DatePeriodSchema.Type type)
    {
        var record = Record.Exception(() =>
        {
            DatePeriodSchema datePeriodSchema = new DatePeriodSchema(day, type);
            return new CreateBudget(new Date(_clock.Current()), [Guid.Empty], "test", new Monetary(
                100000, Currency.USD), datePeriodSchema);
        });

        record.ShouldBeOfType<ExceededDayForPeriodSchemaException>();
    }


    [Fact]
    public async void should_succed_with_correct_command()
    {
        var command = new CreateBudget(
            new Date(_clock.Current()), [Guid.Empty], "test", new Monetary(100000,
                Currency.USD), new DatePeriodSchema(10, DatePeriodSchema.Type.NTH_WORKING_DAY)
        );

        await _handler.Handle(command);
        (await _repository.isBudgetExist(command.Name, command.Users)).ShouldBe(true);
    }


}