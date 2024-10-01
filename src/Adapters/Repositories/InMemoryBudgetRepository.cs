using System.Collections.Concurrent;
using BudgetBuddy.Domain.Eniities;
using BudgetBuddy.Domain.Ports;
using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Adapters.Repositories;

internal sealed class InMemoryBudgetRepository : BudgetRepository
{
    private readonly ConcurrentDictionary<Guid, Budget> budgets = new();
    public Task<bool> isBudgetExist(Name name, IEnumerable<User> users)
    {
        var exists = false;
        foreach (var item in budgets)
        {
            if (item.Value.Name != name)
            {
                continue;
            }

            exists = item.Value.Users.Any(x => users.Any(y => y == x));
        }

        return Task.FromResult(exists);
    }

    public Task Save(Budget budget)
    {
        budgets.TryAdd(budget.Id, budget);
        return Task.CompletedTask;
    }
}