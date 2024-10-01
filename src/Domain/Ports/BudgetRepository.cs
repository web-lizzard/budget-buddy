using BudgetBuddy.Domain.Eniities;
using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Ports;


public interface BudgetRepository
{
    Task<bool> isBudgetExist(Name name, IEnumerable<User> users);

    Task Save(Budget budget);
}