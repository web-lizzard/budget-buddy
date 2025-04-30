import { type DateValue, getLocalTimeZone } from '@internationalized/date';

// Można tu dodać inne funkcje pomocnicze związane z datami, np. formatowanie do YYYY-MM-DD
import { format } from 'date-fns';

/**
 * Safely converts a DateValue object (from @internationalized/date used by shadcn-vue Calendar)
 * to a standard JavaScript Date object in the local time zone.
 *
 * @param value - The DateValue object or undefined/null.
 * @returns A Date object or undefined.
 */
export const dateValueToDate = (value: DateValue | undefined | null): Date | undefined => {
  if (!value) {
    return undefined;
  }
  try {
    // Use the built-in .toDate() method of DateValue
    console.log("Hello")
    return value.toDate(getLocalTimeZone());
  } catch (error) {
    console.error("Error converting DateValue to Date:", error);
    return undefined; // Return undefined if conversion fails
  }
};

/**
 * Formats a Date object or a DateValue object into 'YYYY-MM-DD' string format.
 *
 * @param dateInput - The Date or DateValue object.
 * @returns The formatted date string or an empty string if input is invalid.
 */
export const formatDateToYYYYMMDD = (dateInput: Date | DateValue | undefined | null): string => {
    let dateObject: Date | undefined;
    if (!dateInput) {
        return '';
    }
    if (dateInput instanceof Date) {
        dateObject = dateInput;
    } else {
        // Attempt to convert if it's a DateValue
        try {
            dateObject = dateInput.toDate(getLocalTimeZone());
        } catch (error) {
            console.error("Error converting DateValue for formatting:", error);
            return '';
        }
    }

    if (dateObject && !isNaN(dateObject.getTime())) {
        return format(dateObject, 'yyyy-MM-dd');
    } else {
        console.error("Invalid date provided for formatting YYYY-MM-DD");
        return '';
    }
};
