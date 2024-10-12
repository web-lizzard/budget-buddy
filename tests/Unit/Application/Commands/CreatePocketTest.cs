using BudgetBuddy.Adapters.Repositories;
using BudgetBuddy.Application.Commands;
using BudgetBuddy.Application.Commands.Handlers;
using BudgetBuddy.Domain.Eniities;
using BudgetBuddy.Domain.Exceptions;
using BudgetBuddy.Domain.Ports;
using BudgetBuddy.Domain.Snapshots;
using BudgetBuddy.Domain.ValueObjects;
using Shouldly;
using Unit.Shared;

public sealed class CreatePocketTest
{

    private readonly BudgetRepository _repository;
    private readonly CreatePocketHandler _handler;

    private readonly Clock _clock;

    public CreatePocketTest()
    {
        _repository = new InMemoryBudgetRepository();

        _clock = new TestClock();
        _handler = new CreatePocketHandler(_repository);
    }


    [Fact]
    public async void should_fail_if_parent_budget_does_not_exist()
    {
        var limit = new Limit(
            new Monetary(200000000, Currency.USD)
        );
        var command = new CreatePocket(Guid.Empty, limit);
        var record = await Record.ExceptionAsync(async () => await _handler.Handle(command));

        record.ShouldBeOfType<BudgetNotExistsException>();

    }

    [Fact]
    public async void should_fail_if_pocket_limit_is_higher_than_remaining_in_budget()
    {
        var id = Guid.NewGuid();
        var pocketLimit = new Limit(
            new Monetary(200000000, Currency.USD)
        );
        var budgetLimit = new Limit(new Monetary(200000, Currency.USD));
        var command = new CreatePocket(id, pocketLimit);
        var budget = GetBudget(id, budgetLimit);
        await _repository.Save(budget);

        var record = await Record.ExceptionAsync(async () => await _handler.Handle(command));

        record.ShouldBeOfType<PocketLimitExceedBudgetLimitException>();
    }

    private Budget GetBudget(Guid id, Limit limit)
    {
        var startDate = new Date(_clock.Current());
        return Budget.From(new BudgetSnapshot(id,
            "Test",
            limit,
            [new User(Guid.Empty)],
            new DatePeriod(startDate, startDate.AddDays(10)),
            new PeriodSchema(10, PeriodSchema.Type.NTH_WORKING_DAY)));
    }
}