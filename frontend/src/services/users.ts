import type { User } from '@supabase/supabase-js'

import { API_URL, getAuthHeaders } from './api'

export async function syncUser(user: User): Promise<void> {
  const response = await fetch(`${API_URL}/auth/sync-user`, {
    method: 'POST',
    headers: await getAuthHeaders(),
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
