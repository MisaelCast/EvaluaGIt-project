import { supabase } from '@/lib/supabase'

/**
 * URL base del backend
 * Se lee desde variables de entorno de Vite
 */
export const API_URL = import.meta.env.VITE_API_URL

if (!API_URL) {
  throw new Error('VITE_API_URL no está configurada')
}

export type HealthResponse = {
  status: string
}

const API_TIMEOUT_MS = 8000

/**
 * Wrapper sobre fetch con timeout
 * Aborta la peticion si tarda demasiado
 * Limpia el timeout al terminar
 */
export async function fetchWithTimeout(
  input: RequestInfo | URL,
  init: RequestInit = {},
  timeoutMs: number = API_TIMEOUT_MS,
): Promise<Response> {
  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs)

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
 * Obtiene headers para requests autenticadas
 * Agrega el token de Supabase si hay sesion
 * Siempre incluye Content-Type
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

/**
 * Verifica que el backend este disponible
 */
export async function getHealth(): Promise<HealthResponse> {
  const response = await fetchWithTimeout(`${API_URL}/health`)

  if (!response.ok) {
    throw new Error('No se pudo conectar con el backend')
  }

  return response.json()
}

export type MeResponse = {
  id: string
  supabase_id: string
  email: string
  full_name: string
  avatar_url: string | null
  role: string
}

/**
 * Obtiene los datos del usuario actual desde el backend
 * Usa el token de Supabase para validar la sesion
 */
export async function getMe(): Promise<MeResponse> {
  const headers = await getAuthHeaders()
  const response = await fetchWithTimeout(`${API_URL}/auth/me`, {
    headers,
  })

  if (!response.ok) {
    throw new Error('No se pudo obtener información del usuario')
  }

  return response.json()
}
