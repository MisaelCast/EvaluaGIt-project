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
  const response = await fetch(`${API_URL}/health`)

  if (!response.ok) {
    throw new Error('No se pudo conectar con el backend')
  }

  return response.json()
}
