import { z } from 'zod'

export const MoneySchema = z.object({
    amount: z.number(),
    currency: z.string().length(3), // Assuming ISO 4217 currency codes
  })
