import type { User } from '@supabase/supabase-js'

import { API_URL, fetchWithTimeout, getAuthHeaders } from './api'

/**
 * Sincroniza el usuario de Supabase con el backend
 * Envia el token JWT en Authorization
 * El backend lo usa para verificar la identidad
 */
export async function syncUser(user: User, accessToken: string): Promise<void> {
  const response = await fetchWithTimeout(`${API_URL}/auth/sync-user`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      supabase_id: user.id,
      email: user.email,
      full_name: user.user_metadata?.full_name || user.user_metadata?.name || '',
      avatar_url: user.user_metadata?.avatar_url || null,
    }),
  })

  if (!response.ok) {
    throw new Error('Error al sincronizar usuario')
  }
}

/**
 * Actualiza el rol del usuario autenticado
 * Solo requiere sesion activa
 */
export async function updateMyRole(role: 'PROFESSOR' | 'STUDENT'): Promise<void> {
  const headers = await getAuthHeaders()
  const response = await fetchWithTimeout(`${API_URL}/auth/me/role`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: JSON.stringify({ role }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Error al actualizar el rol')
  }
}
