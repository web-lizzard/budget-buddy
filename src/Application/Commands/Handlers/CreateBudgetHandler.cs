using System.Collections.Concurrent;
using BudgetBuddy.Domain.Eniities;
using BudgetBuddy.Domain.Exceptions;
using BudgetBuddy.Domain.Ports;
using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Application.Commands.Handlers;

public sealed class CreateBudgetHandler(Clock clock)
{
    public ConcurrentDictionary<Guid, Budget> budgets = new();
    private readonly Clock _clock = clock;

    public Task Handle(CreateBudget command)
    {
        var now = new Date(_clock.Current());

        if (command.StartDate < now)
        {
            throw new InvalidDateException(command.StartDate);
        }
        var exists = false;

        foreach (var item in budgets)
        {
            if (item.Value.Name != command.Name)
            {
                continue;
            }

            exists = item.Value.Users.Any(x => command.Users.Any(y => y == x));
        }

        if (exists)
        {
            throw new BudgetAlreadyExistsException(command.Name);
        }

        return Task.CompletedTask;
    }
}