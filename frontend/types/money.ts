import { z } from 'zod'

// Basic Money type corresponding to MoneyDTO
export interface Money {
  amount: number
  currency: string
}

// Zod schema for validating Money objects from API
export const MoneySchema = z.object({
  amount: z.number(),
  currency: z.string().length(3), // Assuming ISO 4217 currency codes
})
