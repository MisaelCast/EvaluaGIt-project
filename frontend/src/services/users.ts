import type { User } from '@supabase/supabase-js'

const API_URL = import.meta.env.VITE_API_URL

if (!API_URL) {
  throw new Error('VITE_API_URL no está configurada')
}

export async function syncUser(user: User): Promise<void> {
  const response = await fetch(`${API_URL}/auth/sync-user`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
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
