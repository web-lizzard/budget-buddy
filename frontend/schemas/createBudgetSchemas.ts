import * as z from 'zod';
import { CalendarDate, type DateValue } from '@internationalized/date';
import { dateValueToDate } from '@/utils/dateHelpers'; // Import the helper

// --- Zod Schema Definitions ---

export const categorySchema = z.object({
  name: z.string().min(1, 'Category name is required'),
  limit: z.coerce.number({
      invalid_type_error: 'Limit must be a number.',
      required_error: 'Limit is required.'
    })
    .positive('Limit must be a positive number.'),
});

export const budgetFormSchema = z.object({
  name: z.string()
    .min(3, 'Budget name must be at least 3 characters long.')
    .max(100, 'Budget name cannot exceed 100 characters.'),
  totalLimit: z.coerce.number({
      invalid_type_error: 'Total limit must be a number.',
    })
    .positive('Total limit must be a positive number.')
    .nullable(),
  currency: z.enum(['PLN', 'USD', 'EUR'] as const, {
    required_error: 'Please select a currency.',
  }),
  startDate: z.custom<DateValue>((val) => val instanceof CalendarDate,
      {
        message: 'Start date is required.',
      }
    )
    .transform(dateValueToDate) // Use imported helper
    .refine(val => val !== undefined, { message: 'Start date is required.' })
    .pipe(z.date()),
  strategyType: z.enum(['monthly', 'yearly'] as const, {
    required_error: 'Please select a budget strategy.',
  }),
  categories: z.array(categorySchema)
    .max(5, 'You can add a maximum of 5 categories.')
    .optional(),
}).superRefine((data, ctx) => {

  // Category Validations
  if (data.categories && data.categories.length > 0) {
    let totalCategoryLimit = 0;
    const categoryNames = new Set<string>();
    const duplicateNameIndices = new Set<number>();

    data.categories.forEach((category, index) => {
      if (category.limit && category.limit > 0) {
           totalCategoryLimit += category.limit;
      }
       const lowerCaseName = category.name.toLowerCase();
       if (category.name && categoryNames.has(lowerCaseName)) {
           duplicateNameIndices.add(index);
           data.categories?.forEach((prevCat, prevIndex) => {
               if (prevIndex < index && prevCat.name.toLowerCase() === lowerCaseName) {
                   duplicateNameIndices.add(prevIndex);
               }
           });
       } else if (category.name) {
           categoryNames.add(lowerCaseName);
       }
    });

     if (duplicateNameIndices.size > 0) {
         duplicateNameIndices.forEach(index => {
             ctx.addIssue({
               code: z.ZodIssueCode.custom,
               message: 'Category names must be unique.',
               path: ['categories', index, 'name'],
             });
         });
     }

    if (data.totalLimit && totalCategoryLimit > data.totalLimit) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: `Total category limits (${totalCategoryLimit}) cannot exceed the budget limit (${data.totalLimit}).`,
        path: ['totalLimit'],
      });
    }
  }
});

// Infer types (can also be moved or kept here)
export type BudgetFormData = z.output<typeof budgetFormSchema>;
export type BudgetFormInput = z.input<typeof budgetFormSchema>;
export type CategoryFormData = z.infer<typeof categorySchema>;
