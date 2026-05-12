import { supabase } from '@/lib/supabase'

/**
 * Inicia el flujo de autenticación OAuth con Google.
 * El redirectTo asegura que Supabase redirija de vuelta al frontend
 * después de que el usuario complete el login en el proveedor.
 */
export async function signInWithGoogle(): Promise<void> {
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: window.location.origin,
    },
  })

  if (error) {
    throw new Error(error.message)
  }
}

export async function signOut(): Promise<void> {
  const { error } = await supabase.auth.signOut()

  if (error) {
    throw new Error(error.message)
  }
}

/**
 * Consulta si existe un usuario autenticado en la sesión actual.
 * Útil para restaurar el estado de auth al cargar la página.
 */
export async function getCurrentUser() {
  const { data, error } = await supabase.auth.getUser()

  if (error) {
    throw new Error(error.message)
  }

  return data.user
}
