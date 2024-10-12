using BudgetBuddy.Domain.Exceptions;
using BudgetBuddy.Domain.Ports;

namespace BudgetBuddy.Application.Commands.Handlers;


public sealed class CreatePocketHandler(BudgetRepository repository)
{

    private readonly BudgetRepository _repository = repository;


    public async Task Handle(CreatePocket command)
    {
        var budget = await _repository.GetById(command.BudgetId);

        if (budget is null)
        {
            throw new BudgetNotExistsException(command.BudgetId);
        }

    }
}