import { z } from 'zod';
import { CalendarDate } from '@internationalized/date';

// Helper function to convert standard Date to CalendarDate
// Keep this helper local to the schema definition if it's only used here
const dateToCalendarDate = (date: Date): CalendarDate => {
  return new CalendarDate(date.getFullYear(), date.getMonth() + 1, date.getDate());
};

// Define the Zod schema for the form view model
export const createTransactionFormSchema = (budgetStartDate: Date, budgetEndDate: Date) => {
    const startDateValue = dateToCalendarDate(budgetStartDate);
    const endDateValue = dateToCalendarDate(budgetEndDate);

    return z.object({
      // Allow null initially, but refine to ensure it's not null upon submission
      categoryId: z.string({ invalid_type_error: "Invalid category ID." })
                      .uuid({ message: "Invalid category UUID." })
                      .nullable()
                      .refine(val => val !== null, { message: "Category is required." }),
      // Map empty input to null, but ensure positive number
      amount: z.number({ required_error: "Amount is required.", invalid_type_error: "Amount must be a number." })
                 .positive({ message: "Amount must be positive." })
                 .nullable(), // Allow null from input binding
                 // Refine ensures it's not null for submission (covered by required_error)
      type: z.enum(['INCOME', 'EXPENSE'], { required_error: "Type is required." }),
      // Simplify date validation: ensure it's a CalendarDate instance and within range.
      occurredDate: z.instanceof(CalendarDate, { message: "Date is required." })
                       .refine(date => date && (date.compare(startDateValue) >= 0), {
                           message: `Date must be on or after ${startDateValue.toString()}`,
                       })
                       .refine(date => date && (date.compare(endDateValue) <= 0), {
                           message: `Date must be on or before ${endDateValue.toString()}`,
                       }),
      description: z.string().max(255, "Description too long (max 255 chars).").optional(),
    });
}

// Define the type for the form input based on the schema
// Use `| null` where the schema allows null
export type TransactionFormInput = {
    categoryId: string | null;
    amount: number | null;
    type: 'INCOME' | 'EXPENSE';
    occurredDate: CalendarDate | null; // Keep DateValue/CalendarDate internally
    description?: string | undefined;
};

// This describes the props coming into the composable/component
export type InitialTransactionFormData = Partial<Omit<TransactionFormInput, 'occurredDate' | 'amount'> & { occurredDate?: Date, amount?: number | null }>;
