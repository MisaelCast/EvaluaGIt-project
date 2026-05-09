<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { User } from '@supabase/supabase-js'

import { getHealth, type HealthResponse } from '@/services/api'
import { getCurrentUser, signInWithGoogle, signOut } from '@/services/auth'

const loading = ref(true)
const error = ref('')
const health = ref<HealthResponse | null>(null)
const user = ref<User | null>(null)

onMounted(async () => {
  try {
    health.value = await getHealth()
    user.value = await getCurrentUser()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error desconocido'
  } finally {
    loading.value = false
  }
})

async function handleSignIn() {
  try {
    await signInWithGoogle()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error al iniciar sesión'
  }
}

async function handleSignOut() {
  try {
    await signOut()
    user.value = null
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error al cerrar sesión'
  }
}
</script>

<template>
  <section class="home">
    <h1>EVALUGIT</h1>
    <p v-if="loading">Conectando con el backend...</p>
    <p v-else-if="error">Backend status: error</p>
    <p v-else>Backend status: conectado</p>
    <p v-if="health">Respuesta: {{ health.status }}</p>
    <p v-if="error">{{ error }}</p>

    <div class="auth">
      <div v-if="user">
        <p>Usuario: {{ user.email }}</p>
        <button @click="handleSignOut">Cerrar sesión</button>
      </div>
      <div v-else>
        <button @click="handleSignIn">Iniciar con Google</button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.home {
  padding: 2rem;
}

.auth {
  margin-top: 1rem;
}
</style>
