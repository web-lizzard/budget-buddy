import { z } from 'zod'
import { MoneySchema } from './moneySchema'

export const CategorySchema = z.object({
    id: z.string().uuid(),
    name: z.string().min(1),
    limit: MoneySchema,
  })
