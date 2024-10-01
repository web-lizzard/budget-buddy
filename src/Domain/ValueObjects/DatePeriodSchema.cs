using BudgetBuddy.Domain.Exceptions;

namespace BudgetBuddy.Domain.ValueObjects;

public sealed record DatePeriodSchema

{
    public enum Type
    {
        NTH_WORKING_DAY,
        NTH_REGULAR_DAY
    }
    public const int RegularDayBreakpoint = 20;
    public const int WorkingDayBreakpoint = 28;
    public DatePeriodSchema(int day, Type policy)
    {
        Policy = policy;
        SetDay(day);
    }

    public Type Policy { get; private set; }
    public int Day { get; private set; }

    private void SetDay(int value)
    {
        switch (Policy)
        {
            case Type.NTH_WORKING_DAY:
                if (value > RegularDayBreakpoint)
                {
                    throw new ExceededDayForPeriodSchemaException(value, RegularDayBreakpoint);
                }
                break;
            case Type.NTH_REGULAR_DAY:
                if (value > WorkingDayBreakpoint)
                {
                    throw new ExceededDayForPeriodSchemaException(value, WorkingDayBreakpoint);
                }
                break;
        }
        Day = value;
    }
}