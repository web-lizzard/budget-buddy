using BudgetBuddy.Adapters.Repositories;
using BudgetBuddy.Application.Commands;
using BudgetBuddy.Application.Commands.Handlers;
using BudgetBuddy.Domain.Exceptions;
using BudgetBuddy.Domain.Ports;
using Shouldly;

public sealed class CreatePocketTest
{

    private readonly BudgetRepository _repository;
    private readonly CreatePocketHandler _handler;

    public CreatePocketTest()
    {
        _repository = new InMemoryBudgetRepository();

        _handler = new CreatePocketHandler(_repository);
    }


    [Fact]
    public async void should_fail_if_parent_budget_does_not_exist()
    {
        var command = new CreatePocket(Guid.Empty);
        var record = await Record.ExceptionAsync(async () => await _handler.Handle(command));

        record.ShouldBeOfType<BudgetNotExistsException>();

    }
}