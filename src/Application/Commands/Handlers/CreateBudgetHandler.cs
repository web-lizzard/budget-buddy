using System.Reflection.Metadata;

namespace BudgetBuddy.Application.Commands.Handlers;

public sealed class CreateBudgetHandler
{

    public Task Handle(CreateBudget command)
    {
        return Task.CompletedTask;
    }
}