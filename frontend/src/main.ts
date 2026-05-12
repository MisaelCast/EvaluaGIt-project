import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { supabase } from './lib/supabase'
import { syncUser } from './services/users'

/**
 * Listener global de cambios de estado de autenticación.
 * Se registra ANTES de montar la aplicación para no perder
 * el evento SIGNED_IN que ocurre inmediatamente después
 * de un redirect OAuth de Google.
 */
supabase.auth.onAuthStateChange(async (event, session) => {
  if (event === 'SIGNED_IN') {
    const user = session?.user
    if (user) {
      try {
        await syncUser(user)
      } catch (err) {
        console.error('Error al sincronizar usuario:', err)
      }
    }
  }
})

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
