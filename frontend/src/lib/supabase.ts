import { createClient } from '@supabase/supabase-js'

/**
 * Variables de entorno requeridas para conectar con Supabase.
 * Se validan en tiempo de importación para fallar temprano
 * si falta alguna configuración.
 */
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl) {
  throw new Error('VITE_SUPABASE_URL no está configurada')
}

if (!supabaseAnonKey) {
  throw new Error('VITE_SUPABASE_ANON_KEY no está configurada')
}

/**
 * Cliente singleton de Supabase. Se importa desde cualquier parte
 * del frontend que necesite autenticación o acceso a la API.
 */
export const supabase = createClient(supabaseUrl, supabaseAnonKey)
