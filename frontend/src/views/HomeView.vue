<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import type { User } from '@supabase/supabase-js'

import { supabase } from '@/lib/supabase'
import { getHealth, type HealthResponse, getMe } from '@/services/api'
import { getCurrentUser, signInWithGoogle, signOut } from '@/services/auth'
import { syncUser } from '@/services/users'

const router = useRouter()
const loading = ref(true)
const healthError = ref('')
const health = ref<HealthResponse | null>(null)
const user = ref<User | null>(null)
const authError = ref('')

const backendStatus = computed(() => {
  if (loading.value) return 'Cargando'
  if (health.value) return 'Conectado'
  return 'Error'
})

const backendStatusClass = computed(() => {
  if (loading.value) return 'status-loading'
  if (health.value) return 'status-ok'
  return 'status-error'
})

const displayName = computed(() => {
  return (
    user.value?.user_metadata?.full_name ||
    user.value?.email ||
    'Usuario autenticado'
  )
})

onMounted(() => {
  void loadInitialData()
})

async function loadInitialData() {
  loading.value = true
  healthError.value = ''
  authError.value = ''

  try {
    try {
      health.value = await getHealth()
    } catch (err) {
      healthError.value =
        err instanceof Error ? err.message : 'Error desconocido'
      health.value = null
    }

try {
        user.value = await getCurrentUser()
        if (user.value) {
          const { data: sessionData } = await supabase.auth.getSession()
          const token = sessionData?.session?.access_token
          if (token) {
            await syncUser(user.value, token)
            const me = await getMe()
            if (me.role === 'UNASSIGNED') {
              router.push('/onboarding')
              return
            }
            if (me.role === 'STUDENT') {
              router.push('/student/dashboard')
              return
            }
          }
        }
      } catch {
        user.value = null
      }
  } finally {
    loading.value = false
  }
}

async function handleSignIn() {
  authError.value = ''

  try {
    await signInWithGoogle()
  } catch (err) {
    authError.value =
      err instanceof Error ? err.message : 'Error al iniciar sesion'
  }
}

async function handleSignOut() {
  authError.value = ''

  try {
    await signOut()
    user.value = null
  } catch (err) {
    authError.value =
      err instanceof Error ? err.message : 'Error al cerrar sesion'
  }
}
</script>

<template>
  <main class="page">
    <header class="header">
      <div>
        <p class="eyebrow">EvaluaGit</p>
        <h1>EvaluaGit</h1>
        <p class="subtitle">Plataforma de evaluacion de repositorios Git</p>
      </div>
    </header>

    <section class="hero">
      <div class="features">
        <h2>Que permite EvaluaGit</h2>
        <ul>
          <li>Crear proyectos y definir requerimientos</li>
          <li>Vincular repositorios GitHub de tus alumnos</li>
          <li>Analizar la estructura de cada repositorio</li>
          <li>Ver resultados basicos del analisis</li>
        </ul>
      </div>
    </section>

    <section class="auth-section">
      <div v-if="loading" class="muted">Cargando...</div>

      <div v-else-if="user" class="user-panel">
        <div class="user-info">
          <p class="label">Sesion activa</p>
          <p class="user-name">{{ displayName }}</p>
        </div>
        <nav class="user-nav">
          <RouterLink to="/dashboard" class="button primary">
            Ir al dashboard
          </RouterLink>
          <button class="button secondary" type="button" @click="handleSignOut">
            Cerrar sesion
          </button>
        </nav>
      </div>

      <div v-else class="auth-panel">
        <p class="muted">Inicia sesion con tu cuenta de Google para comenzar.</p>
        <button class="button primary" type="button" @click="handleSignIn">
          Iniciar con Google
        </button>
      </div>

      <p v-if="authError" class="error-text">{{ authError }}</p>
    </section>

    <section class="status-section">
      <div class="section-title">
        <h2>Estado del sistema</h2>
        <span class="status-pill" :class="backendStatusClass">
          {{ backendStatus }}
        </span>
      </div>

      <p v-if="loading" class="muted">Revisando conexion con el backend...</p>
      <p v-else-if="health" class="muted">
        Backend disponible. Respuesta: {{ health.status }}
      </p>
      <p v-else class="error-text">{{ healthError }}</p>
    </section>
  </main>
</template>

<style scoped>
.page {
  min-height: 100vh;
  padding: 48px;
  background: #f3f5f4;
  color: #17201b;
}

.header {
  max-width: 720px;
  margin: 0 auto 40px;
  text-align: center;
}

.eyebrow {
  margin: 0 0 8px;
  color: #2f8f5b;
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: 3rem;
  line-height: 1.1;
}

h1,
h2,
p {
  margin: 0;
}

.subtitle {
  margin-top: 10px;
  color: #5d6962;
  font-size: 1.1rem;
}

.hero {
  max-width: 720px;
  margin: 0 auto 40px;
  padding: 32px;
  background: #ffffff;
  border: 1px solid #dfe6e1;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgb(25 35 30 / 6%);
}

.hero h2 {
  margin: 0 0 16px;
  font-size: 1.1rem;
}

.hero ul {
  margin: 0;
  padding-left: 20px;
}

.hero li {
  margin-bottom: 8px;
  color: #4b5650;
}

.hero li:last-child {
  margin-bottom: 0;
}

.auth-section {
  max-width: 720px;
  margin: 0 auto 24px;
  padding: 24px;
  background: #ffffff;
  border: 1px solid #dfe6e1;
  border-radius: 8px;
  text-align: center;
}

.user-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

.user-info {
  text-align: center;
}

.user-nav {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.auth-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

.status-section {
  max-width: 720px;
  margin: 0 auto;
  padding: 22px;
  background: #ffffff;
  border: 1px solid #dfe6e1;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgb(25 35 30 / 6%);
}

.section-title {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 700;
}

.status-ok {
  background: #e3f5eb;
  color: #17633d;
}

.status-loading {
  background: #eef1ef;
  color: #5d6962;
}

.status-error {
  background: #fde8e8;
  color: #9b2525;
}

.muted {
  color: #5d6962;
  line-height: 1.6;
}

.error-text {
  color: #9b2525;
  line-height: 1.6;
  margin-top: 12px;
}

.label {
  margin-bottom: 4px;
  color: #6c7770;
  font-size: 0.82rem;
}

.user-name {
  color: #17201b;
  font-weight: 700;
}

.button {
  border: 0;
  border-radius: 6px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
}

.button.primary {
  background: #2f8f5b;
  color: #ffffff;
}

.button.secondary {
  background: #eef1ef;
  color: #17201b;
}

.button:hover {
  filter: brightness(0.96);
}

@media (max-width: 760px) {
  .page {
    padding: 28px 18px;
  }

  h1 {
    font-size: 2.2rem;
  }
}
</style>