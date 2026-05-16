<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { User } from '@supabase/supabase-js'

import { getHealth, type HealthResponse } from '@/services/api'
import { getCurrentUser, signInWithGoogle, signOut } from '@/services/auth'
import { createProject, getProjects, type ProjectResponse } from '@/services/projects'

const loading = ref(true)
const healthError = ref('')
const health = ref<HealthResponse | null>(null)
const user = ref<User | null>(null)
const authError = ref('')
const projects = ref<ProjectResponse[]>([])
const projectsLoading = ref(false)
const projectsError = ref('')
const creatingProject = ref(false)
const newProjectName = ref('')
const newProjectDescription = ref('')

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
  return user.value?.user_metadata?.full_name || user.value?.email || 'Usuario autenticado'
})

onMounted(() => {
  void loadInitialData()
})

async function loadInitialData() {
  loading.value = true
  healthError.value = ''
  authError.value = ''
  projectsError.value = ''
  health.value = null
  user.value = null
  projects.value = []

  try {
    try {
      health.value = await getHealth()
    } catch (err) {
      healthError.value = err instanceof Error ? err.message : 'Error desconocido'
      health.value = null
    }

    try {
      user.value = await getCurrentUser()
    } catch (err) {
      authError.value = err instanceof Error ? err.message : 'No se pudo revisar la sesión'
      user.value = null
    }

  } finally {
    loading.value = false
  }

  if (user.value) {
    void loadProjects()
  }
}

async function loadProjects() {
  projectsLoading.value = true
  projectsError.value = ''

  try {
    projects.value = await getProjects()
  } catch (err) {
    projects.value = []
    projectsError.value = err instanceof Error ? err.message : 'No se pudieron cargar los proyectos'
  } finally {
    projectsLoading.value = false
  }
}

async function handleSignIn() {
  authError.value = ''

  try {
    await signInWithGoogle()
  } catch (err) {
    authError.value = err instanceof Error ? err.message : 'Error al iniciar sesión'
  }
}

async function handleSignOut() {
  authError.value = ''

  try {
    await signOut()
    user.value = null
    projects.value = []
    projectsError.value = ''
  } catch (err) {
    authError.value = err instanceof Error ? err.message : 'Error al cerrar sesión'
  }
}

async function handleCreateProject() {
  const name = newProjectName.value.trim()
  const description = newProjectDescription.value.trim()

  if (!name) {
    projectsError.value = 'El nombre del proyecto es obligatorio'
    return
  }

  creatingProject.value = true
  projectsError.value = ''

  try {
    await createProject({
      name,
      description: description || null,
      requirements: {},
      due_date: null,
    })
    newProjectName.value = ''
    newProjectDescription.value = ''
    await loadProjects()
  } catch (err) {
    projectsError.value = err instanceof Error ? err.message : 'No se pudo crear el proyecto'
  } finally {
    creatingProject.value = false
  }
}

function formatDate(value: string | null): string {
  if (!value) return 'Sin fecha'

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
  }).format(new Date(value))
}
</script>

<template>
  <main class="page">
    <header class="header">
      <div>
        <p class="eyebrow">EvaluaGit</p>
        <h1>EvaluaGit</h1>
        <p class="subtitle">Plataforma de evaluación de repositorios Git</p>
      </div>
    </header>

    <section class="grid">
      <article class="card">
        <div class="section-title">
          <h2>Estado del sistema</h2>
          <span class="status-pill" :class="backendStatusClass">{{ backendStatus }}</span>
        </div>

        <p v-if="loading" class="muted">Revisando conexión con el backend...</p>
        <p v-else-if="health" class="muted">Backend disponible. Respuesta: {{ health.status }}</p>
        <p v-else class="error-text">{{ healthError }}</p>
      </article>

      <article class="card">
        <div class="section-title">
          <h2>Sesión</h2>
          <span class="status-pill" :class="user ? 'status-ok' : 'status-loading'">
            {{ user ? 'Activa' : 'Sin sesión' }}
          </span>
        </div>

        <div v-if="loading" class="session-row">
          <p class="muted">Revisando sesión actual...</p>
        </div>

        <div v-else-if="user" class="session-row">
          <div>
            <p class="label">Usuario</p>
            <p class="user-name">{{ displayName }}</p>
          </div>
          <button class="button secondary" type="button" @click="handleSignOut">
            Cerrar sesión
          </button>
        </div>

        <div v-else class="session-row">
          <p class="muted">Inicia sesión para probar el flujo autenticado.</p>
          <button class="button primary" type="button" @click="handleSignIn">
            Iniciar con Google
          </button>
        </div>

        <p v-if="authError" class="error-text">{{ authError }}</p>
      </article>
    </section>

    <section class="card main-area">
      <div class="section-title">
        <h2>Mis proyectos</h2>
      </div>

      <p v-if="!user" class="muted">Inicia sesión para ver tus proyectos.</p>

      <div v-else class="projects-content">
        <form class="project-form" @submit.prevent="handleCreateProject">
          <div class="form-grid">
            <label class="field">
              <span>Nombre del proyecto</span>
              <input
                v-model="newProjectName"
                type="text"
                placeholder="Proyecto final"
                autocomplete="off"
              />
            </label>

            <label class="field">
              <span>Descripción</span>
              <textarea
                v-model="newProjectDescription"
                rows="3"
                placeholder="Breve descripción del proyecto"
              />
            </label>
          </div>

          <button class="button primary" type="submit" :disabled="creatingProject">
            {{ creatingProject ? 'Creando...' : 'Crear proyecto' }}
          </button>
        </form>

        <p v-if="projectsError" class="error-text">{{ projectsError }}</p>
        <p v-if="projectsLoading" class="muted">Cargando proyectos...</p>

        <div v-else-if="projects.length" class="projects-list">
          <article v-for="project in projects" :key="project.id" class="project-card">
            <h3>{{ project.name }}</h3>
            <p class="muted">{{ project.description || 'Sin descripción' }}</p>
            <div class="project-meta">
              <span>Entrega: {{ formatDate(project.due_date) }}</span>
              <span>Creado: {{ formatDate(project.created_at) }}</span>
            </div>
          </article>
        </div>

        <p v-else-if="!projectsError" class="muted">Aún no tienes proyectos.</p>
      </div>
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
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  max-width: 1080px;
  margin: 0 auto 28px;
}

.eyebrow {
  margin: 0 0 8px;
  color: #2f8f5b;
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
}

h1,
h2,
p {
  margin: 0;
}

h1 {
  font-size: 2.6rem;
  line-height: 1.1;
}

h2 {
  font-size: 1.05rem;
}

.subtitle {
  margin-top: 10px;
  color: #5d6962;
  font-size: 1.05rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  max-width: 1080px;
  margin: 0 auto;
}

.card {
  background: #ffffff;
  border: 1px solid #dfe6e1;
  border-radius: 8px;
  padding: 22px;
  box-shadow: 0 10px 30px rgb(25 35 30 / 6%);
}

.section-title {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
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
}

.session-row {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: space-between;
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
}

.button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
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

.main-area {
  max-width: 1080px;
  margin: 18px auto 0;
}

.projects-content {
  display: grid;
  gap: 18px;
}

.project-form {
  display: grid;
  gap: 16px;
  padding-bottom: 18px;
  border-bottom: 1px solid #dfe6e1;
}

.form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 2fr);
  gap: 16px;
}

.field {
  display: grid;
  gap: 8px;
  color: #4b5650;
  font-size: 0.88rem;
  font-weight: 700;
}

.field input,
.field textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #cfd8d2;
  border-radius: 6px;
  padding: 10px 12px;
  color: #17201b;
  font: inherit;
}

.field textarea {
  resize: vertical;
}

.field input:focus,
.field textarea:focus {
  border-color: #2f8f5b;
  outline: 2px solid #d9f0e4;
}

.projects-list {
  display: grid;
  gap: 12px;
}

.project-card {
  border: 1px solid #dfe6e1;
  border-radius: 8px;
  padding: 16px;
  background: #fbfcfb;
}

.project-card h3 {
  margin: 0 0 8px;
  font-size: 1rem;
}

.project-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  margin-top: 14px;
  color: #6c7770;
  font-size: 0.86rem;
}

@media (max-width: 760px) {
  .page {
    padding: 28px 18px;
  }

  .grid {
    grid-template-columns: 1fr;
  }

  .session-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  h1 {
    font-size: 2.1rem;
  }
}
</style>
