import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { supabase } from './lib/supabase'
import { syncUser } from './services/users'

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
