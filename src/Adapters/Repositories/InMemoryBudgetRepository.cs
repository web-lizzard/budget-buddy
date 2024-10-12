using System.Collections.Concurrent;
using BudgetBuddy.Domain.Eniities;
using BudgetBuddy.Domain.Ports;
using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Adapters.Repositories;

internal sealed class InMemoryBudgetRepository : BudgetRepository
{
    private readonly ConcurrentDictionary<Guid, Budget> budgets = new();

    public Task<Budget?> GetById(Guid budgetId)
    {
        return Task.FromResult(budgets.GetValueOrDefault(budgetId));
    }

    public Task<bool> isBudgetExist(Name name, IEnumerable<User> users)
    {
        var exists = false;
        foreach (var item in budgets)
        {
            var snapshot = item.Value.Snapshot;
            if (snapshot.Name != name)
            {
                continue;
            }

            exists = snapshot.Users.Any(x => users.Any(y => y == x));
        }

        return Task.FromResult(exists);
    }

    public Task Save(Budget budget)
    {
        var id = budget.Snapshot.Id;
        budgets.TryAdd(id, budget);
        return Task.CompletedTask;
    }
}