using BudgetBuddy.Domain.Exceptions;
using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Application.Commands.Handlers;

public sealed class CreateBudgetHandler
{

    public Task Handle(CreateBudget command)
    {
        var now = Date.Now;

        if (command.StartDate < now)
        {
            throw new InvalidDateException(command.StartDate);
        }

        return Task.CompletedTask;
    }
}