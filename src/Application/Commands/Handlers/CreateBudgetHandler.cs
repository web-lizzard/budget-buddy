using BudgetBuddy.Domain.Exceptions;

namespace BudgetBuddy.Application.Commands.Handlers;

public sealed class CreateBudgetHandler
{

    public Task Handle(CreateBudget command)
    {
        var now = DateTime.UtcNow;

        if (command.StartDate < now)
        {
            throw new InvalidDateException();
        }

        return Task.CompletedTask;
    }
}