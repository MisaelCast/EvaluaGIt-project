import type { User } from '@supabase/supabase-js'

import { API_URL, fetchWithTimeout } from './api'

/**
 * Sincroniza el usuario autenticado en Supabase con la base de datos
 * local del backend. Se llama típicamente después del login exitoso.
 * Requiere token JWT válido; el backend extrae la identidad del token.
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
