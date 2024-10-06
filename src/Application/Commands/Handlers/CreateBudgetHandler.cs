using BudgetBuddy.Domain.Exceptions;
using BudgetBuddy.Domain.Ports;
using BudgetBuddy.Domain.Services;
using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Application.Commands.Handlers;

public sealed class CreateBudgetHandler(Clock clock,
    BudgetRepository repository,
    CreateBudgetService createBudgetService)
{
    private readonly Clock _clock = clock;
    private readonly BudgetRepository _repository = repository;
    private readonly CreateBudgetService _createBudgetService = createBudgetService;


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

        var budget = await _createBudgetService.CreateBudget(
            command.StartDate, command.Users, command.Name, command.Limit, command.DatePeriodSchema
        );
        await _repository.Save(budget);
    }
}