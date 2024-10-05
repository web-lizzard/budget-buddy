using BudgetBuddy.Domain.ValueObjects;

namespace BudgetBuddy.Domain.Ports;


public interface WorkingDayChecker


{

    Task<bool> isWorkingDay(Date day);

};