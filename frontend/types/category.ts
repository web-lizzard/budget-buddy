import type { Money } from '@/types/money'

// Category type corresponding to CategoryDTO
export interface Category {
  id: string // UUID
  name: string
  limit: Money
  // Add other fields if necessary based on full CategoryDTO
}

// Zod schema for validating Category objects
