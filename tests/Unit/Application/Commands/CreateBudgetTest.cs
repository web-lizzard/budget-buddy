using BudgetBuddy.Application.Commands;
using BudgetBuddy.Application.Commands.Handlers;
using BudgetBuddy.Domain.Exceptions;
using BudgetBuddy.Domain.ValueObjects;
using Shouldly;

namespace Unit.Application.Commands;
public class CreateBudgetTests
{
    [Fact]
    public async void should_fail_if_date_is_past()
    {
        // Given
        var command = new CreateBudget(
           Date.Now.AddDays(-1)
        );
        var handler = new CreateBudgetHandler();
        // When
        var record = await Record.ExceptionAsync(async () => await handler.Handle(command));

        // Then
        record.ShouldBeOfType<InvalidDateException>();
    }
}