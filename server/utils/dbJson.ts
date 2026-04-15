export function parseJsonArray<T = unknown>(value: unknown, fallback: T[] = []): T[] {
  if (Array.isArray(value)) return value as T[]
  if (typeof value !== 'string' || value.trim() === '') return fallback
  try {
    const parsed = JSON.parse(value)
    return Array.isArray(parsed) ? (parsed as T[]) : fallback
  } catch {
    return fallback
  }
}

export function stringifyJsonArray(value: unknown): string {
  if (typeof value === 'string') return value
  if (Array.isArray(value)) return JSON.stringify(value)
  return '[]'
}

export function parseJsonObject<T extends Record<string, unknown>>(
  value: unknown,
  fallback: T
): T {
  if (value && typeof value === 'object' && !Array.isArray(value)) return value as T
  if (typeof value !== 'string' || value.trim() === '') return fallback
  try {
    const parsed = JSON.parse(value)
    return parsed && typeof parsed === 'object' && !Array.isArray(parsed)
      ? (parsed as T)
      : fallback
  } catch {
    return fallback
  }
}

export function stringifyJsonObject(value: unknown): string {
  if (typeof value === 'string') return value
  if (value && typeof value === 'object' && !Array.isArray(value))
    return JSON.stringify(value)
  return '{}'
}
