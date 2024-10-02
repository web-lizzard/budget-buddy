using BudgetBuddy.Application.Factories;
using BudgetBuddy.Domain.Eniities;
using BudgetBuddy.Domain.Exceptions;
using BudgetBuddy.Domain.Ports;
using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Application.Commands.Handlers;

public sealed class CreateBudgetHandler(Clock clock, BudgetRepository repository, BudgetFactory budgetFactory)


{
    private readonly Clock _clock = clock;
    private readonly BudgetRepository _repository = repository;
    private readonly BudgetFactory _budgetFactory = budgetFactory;

    async public Task Handle(CreateBudget command)
    {
        var now = new Date(_clock.Current());

        if (command.StartDate < now)
        {
            throw new InvalidDateException(command.StartDate);
        }

        var exists = await _repository.isBudgetExist(command.Name, command.Users);

        if (exists)
        {
            throw new BudgetAlreadyExistsException(command.Name);
        }

        var budget = _budgetFactory.From(command);

        await _repository.Save(budget);
    }
}