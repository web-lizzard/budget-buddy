using BudgetBuddy.Application.Commands;
using BudgetBuddy.Domain.Eniities;
using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Application.Factories;


public sealed class BudgetFactory
{

    public Budget From(CreateBudget command)
    {
        var id = Guid.NewGuid();
        var datePeriod = new DatePeriod(command.StartDate, command.EndDate);
        return new Budget(id, command.Name, command.Limit, command.Users, datePeriod, command.DatePeriodSchema);
    }

}