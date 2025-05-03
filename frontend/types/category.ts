import type { Money } from './money'

/**
 * Frontend representation of a category with consistent camelCase naming
 */
export interface Category {
  id: string
  name: string
  limit: Money
}

// Zod schema for validating Category objects
