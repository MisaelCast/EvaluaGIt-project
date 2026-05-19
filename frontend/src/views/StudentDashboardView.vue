<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { getJoinedProjects, joinProject, type ProjectResponse } from '@/services/projects'

const joinedProjects = ref<ProjectResponse[]>([])
const loadingProjects = ref(false)
const projectsError = ref('')

const joinCodeInput = ref('')
const joining = ref(false)
const joinError = ref('')
const joinSuccess = ref('')

onMounted(() => {
  void loadJoinedProjects()
})

async function loadJoinedProjects() {
  loadingProjects.value = true
  projectsError.value = ''

  try {
    joinedProjects.value = await getJoinedProjects()
  } catch (err) {
    joinedProjects.value = []
    projectsError.value = err instanceof Error ? err.message : 'No se pudieron cargar los proyectos'
  } finally {
    loadingProjects.value = false
  }
}

async function handleJoinProject() {
  const code = joinCodeInput.value.trim().toUpperCase()
  if (!code) {
    joinError.value = 'Ingresa un codigo de proyecto'
    return
  }

  joining.value = true
  joinError.value = ''
  joinSuccess.value = ''

  try {
    await joinProject(code)
    joinCodeInput.value = ''
    joinSuccess.value = 'Te has unido al proyecto correctamente'
    await loadJoinedProjects()
  } catch (err) {
    joinError.value = err instanceof Error ? err.message : 'No se pudo unir al proyecto'
  } finally {
    joining.value = false
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
  <main class="min-h-screen bg-slate-50 px-6 py-12">
    <div class="max-w-2xl mx-auto">
      <header class="mb-8">
        <h1 class="text-3xl font-bold text-slate-900 mb-2">Panel de alumno</h1>
        <p class="text-slate-500">
          Ingresa el codigo de union del proyecto que te compartio tu profesor.
        </p>
      </header>

      <section class="bg-white border border-slate-200 rounded-xl p-6 mb-6">
        <h2 class="text-lg font-semibold text-slate-900 mb-4">Unirse a un proyecto</h2>

        <div class="flex gap-3">
          <input
            v-model="joinCodeInput"
            type="text"
            placeholder="Codigo de proyecto (ej: ABC123)"
            maxlength="10"
            class="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 uppercase font-mono"
            :disabled="joining"
            @keyup.enter="handleJoinProject"
          />
          <button
            type="button"
            :disabled="joining"
            class="px-6 py-2 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 disabled:opacity-50"
            @click="handleJoinProject"
          >
            {{ joining ? 'Uniendo...' : 'Unirme' }}
          </button>
        </div>

        <p v-if="joinError" class="mt-3 text-red-600 text-sm">{{ joinError }}</p>
        <p v-if="joinSuccess" class="mt-3 text-emerald-700 text-sm font-medium">{{ joinSuccess }}</p>
      </section>

      <section class="bg-white border border-slate-200 rounded-xl p-6">
        <h2 class="text-lg font-semibold text-slate-900 mb-4">Proyectos unidos</h2>

        <p v-if="loadingProjects" class="text-slate-500">Cargando proyectos...</p>
        <p v-else-if="projectsError" class="text-red-600">{{ projectsError }}</p>

        <div v-else-if="joinedProjects.length" class="space-y-4">
          <div
            v-for="project in joinedProjects"
            :key="project.id"
            class="border border-slate-200 rounded-lg p-4"
          >
            <h3 class="font-semibold text-slate-900">{{ project.name }}</h3>
            <p class="text-sm text-slate-500 mt-1">
              {{ project.description || 'Sin descripcion' }}
            </p>
            <div class="mt-2 flex items-center gap-4 text-xs text-slate-400">
              <span>Creado: {{ formatDate(project.created_at) }}</span>
              <span class="font-mono bg-slate-100 px-2 py-0.5 rounded">Codigo: {{ project.join_code }}</span>
            </div>
          </div>
        </div>

        <p v-else class="text-slate-500 text-sm">
          Aun no te has unido a ningun proyecto.
        </p>
      </section>

      <div class="mt-6 text-center">
        <RouterLink
          to="/"
          class="text-emerald-600 hover:text-emerald-700 font-semibold"
        >
          Volver al inicio
        </RouterLink>
      </div>
    </div>
  </main>
</template>