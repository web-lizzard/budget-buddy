import type { Money } from '~/types/money'

/**
 * Formats a Money object into a localized currency string.
 * Example: { amount: 1234.56, currency: 'PLN' } -> "1,234.56 PLN"
 *
 * @param money - The Money object to format.
 * @param locale - Optional locale string (e.g., 'pl-PL', 'en-US'). Defaults to system locale.
 * @returns Formatted currency string or 'N/A' if input is invalid.
 */
export function formatCurrency(money: Money | null | undefined, locale?: string): string {
  if (!money || typeof money.amount !== 'number' || typeof money.currency !== 'string') {
    return 'N/A'
  }

  try {
    return money.amount.toLocaleString(locale, {
      style: 'currency',
      currency: money.currency,
      // minimumFractionDigits: 2, // Default for most currencies
      // maximumFractionDigits: 2,
    })
  } catch (error) {
    console.error(`Error formatting currency (${money.currency}):`, error)
    // Fallback to simple formatting if Intl fails
    return `${money.amount.toFixed(2)} ${money.currency}`
  }
}
