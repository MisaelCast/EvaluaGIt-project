import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { supabase } from './lib/supabase'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

supabase.auth.onAuthStateChange((event, session) => {
  console.log('Auth event:', event, session)
})
