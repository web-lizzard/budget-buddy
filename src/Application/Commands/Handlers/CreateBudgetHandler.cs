using BudgetBuddy.Domain.Exceptions;
using BudgetBuddy.Domain.Ports;
using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Application.Commands.Handlers;

public sealed class CreateBudgetHandler(Clock clock)
{
    private readonly Clock _clock = clock;

    public Task Handle(CreateBudget command)
    {
        var now = new Date(_clock.Current());

        if (command.StartDate < now)
        {
            throw new InvalidDateException(command.StartDate);
        }

        return Task.CompletedTask;
    }
}