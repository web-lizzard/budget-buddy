using BudgetBuddy.Domain.Exceptions;

namespace BudgetBuddy.Domain.ValueObjects;

public sealed record PeriodSchema

{
    public enum Type
    {
        NTH_WORKING_DAY,
        NTH_REGULAR_DAY
    }
    public const int RegularDayBreakpoint = 20;
    public const int WorkingDayBreakpoint = 28;
    public PeriodSchema(int day, Type strategy)
    {
        Strategy = strategy;
        SetDay(day);
    }

    public Type Strategy { get; private set; }
    public int Day { get; private set; }

    private void SetDay(int value)
    {
        switch (Strategy)
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