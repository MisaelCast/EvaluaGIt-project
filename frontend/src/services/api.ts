import { supabase } from '@/lib/supabase'

/**
 * URL base del backend. Se lee desde variables de entorno de Vite.
 * Lanza error en tiempo de importación si no está configurada.
 */
export const API_URL = import.meta.env.VITE_API_URL

if (!API_URL) {
  throw new Error('VITE_API_URL no está configurada')
}

export type HealthResponse = {
  status: string
}

const API_TIMEOUT_MS = 8000

export async function fetchWithTimeout(
  input: RequestInfo | URL,
  init: RequestInit = {},
): Promise<Response> {
  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => controller.abort(), API_TIMEOUT_MS)

  try {
    return await fetch(input, {
      ...init,
      signal: controller.signal,
    })
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new Error('Tiempo de espera agotado al conectar con el backend')
    }

    throw err
  } finally {
    window.clearTimeout(timeoutId)
  }
}

/**
 * Obtiene los headers de autenticación incluyendo el Bearer token
 * desde la sesión activa de Supabase. Si no hay sesión, solo envía
 * Content-Type sin Authorization.
 */
export async function getAuthHeaders(): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return headers
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetchWithTimeout(`${API_URL}/health`)

  if (!response.ok) {
    throw new Error('No se pudo conectar con el backend')
  }

  return response.json()
}
