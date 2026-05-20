import { supabase } from '@/lib/supabase'
import type { User } from '@supabase/supabase-js'

/**
 * Inicia el flujo de autenticacion OAuth con Google
 * redirectTo hace que Supabase redirija al usuario de vuelta a esta
 * aplicacion al completar el login en Google
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

/**
 * Cierra la sesion en Supabase
 * No afecta la sesion del backend
 */
export async function signOut(): Promise<void> {
  const { error } = await supabase.auth.signOut()

  if (error) {
    throw new Error(error.message)
  }
}

/**
 * Obtiene el usuario actual desde Supabase
 * Sirve para restaurar auth al recargar la pagina
 */
export async function getCurrentUser(): Promise<User | null> {
  const { data, error } = await supabase.auth.getSession()

  if (error) {
    throw new Error(error.message)
  }

  return data.session?.user ?? null
}
