import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { supabase } from './lib/supabase'
import { syncUser } from './services/users'
import './assets/main.css'

/**
 * Listener global de cambios de estado de autenticación.
 * Se registra ANTES de montar la aplicación para no perder
 * el evento SIGNED_IN que ocurre inmediatamente después
 * de un redirect OAuth de Google.
 */
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'SIGNED_IN') {
    const user = session?.user
    const token = session?.access_token

    if (user && token) {
      setTimeout(() => {
        void syncUser(user, token).catch(() => undefined)
      }, 0)
    }
  }
})

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
