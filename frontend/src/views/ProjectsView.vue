<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import type { User } from '@supabase/supabase-js'

import { getCurrentUser, signOut } from '@/services/auth'
import { createProject, deleteProject, getProjects, type ProjectResponse } from '@/services/projects'

const router = useRouter()

type IconName =
  | 'bar-chart'
  | 'bell'
  | 'chevron-right'
  | 'folder'
  | 'home'
  | 'key'
  | 'plus'
  | 'search'
  | 'settings'
  | 'trash'
  | 'upload-cloud'

const iconPaths: Record<IconName, string[]> = {
  'bar-chart': ['M3 3v18h18', 'M7 15v2', 'M12 10v7', 'M17 6v11'],
  bell: ['M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9', 'M13.73 21a2 2 0 0 1-3.46 0'],
  'chevron-right': ['M9 18l6-6-6-6'],
  folder: ['M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z'],
  home: ['M3 10.5 12 3l9 7.5', 'M5 10v10h14V10', 'M9 20v-6h6v6'],
  key: ['M15 7a4 4 0 1 0-2.5 3.7L4 19.2V22h3v-2h2v-2h2l3.3-3.3A4 4 0 0 0 15 7Z', 'M18 5h.01'],
  plus: ['M12 5v14', 'M5 12h14'],
  search: ['M21 21l-4.35-4.35', 'M10.5 18a7.5 7.5 0 1 0 0-15 7.5 7.5 0 0 0 0 15Z'],
  settings: ['M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z', 'M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 1.55V21a2 2 0 1 1-4 0v-.05a1.7 1.7 0 0 0-1-1.55 1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.55-1H3a2 2 0 1 1 0-4h.05A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.55V3a2 2 0 1 1 4 0v.05A1.7 1.7 0 0 0 15 4.6a1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.55 1H21a2 2 0 1 1 0 4h-.05A1.7 1.7 0 0 0 19.4 15Z'],
  trash: ['M3 6h18', 'M8 6V4h8v2', 'M19 6l-1 14H6L5 6', 'M10 11v5', 'M14 11v5'],
  'upload-cloud': ['M16 16l-4-4-4 4', 'M12 12v9', 'M20 16.6A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25'],
}

const Icon = (props: { name: IconName; class?: string }) =>
  h(
    'svg',
    {
      class: props.class ?? 'h-5 w-5',
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2',
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round',
      'aria-hidden': 'true',
    },
    iconPaths[props.name].map((d) => h('path', { d })),
  )

const user = ref<User | null>(null)
const projects = ref<ProjectResponse[]>([])
const projectsLoading = ref(false)
const projectsError = ref('')
const creatingProject = ref(false)
const newProjectName = ref('')
const newProjectDescription = ref('')
const deletingProjectId = ref<string | null>(null)

const professorName = computed(() => {
  return user.value?.user_metadata?.full_name || user.value?.email || 'Profesor'
})

const initials = computed(() => {
  const source = professorName.value.trim()
  if (!source) return 'P'

  return source
    .split(/\s+/)
    .slice(0, 2)
    .map((part: string) => part.charAt(0).toUpperCase())
    .join('')
})

const profileImageUrl = computed(() => {
  const avatarUrl = user.value?.user_metadata?.avatar_url
  return typeof avatarUrl === 'string' && avatarUrl ? avatarUrl : null
})

onMounted(() => {
  void loadUser()
  void loadProjects()
})

async function loadUser() {
  try {
    user.value = await getCurrentUser()
  } catch {
    user.value = null
  }
}

async function loadProjects() {
  projectsLoading.value = true
  projectsError.value = ''

  try {
    projects.value = await getProjects()
  } catch (err) {
    projects.value = []
    projectsError.value =
      err instanceof Error ? err.message : 'No se pudieron cargar los proyectos'
  } finally {
    projectsLoading.value = false
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
      requirements: {
        requiredFiles: [],
        forbiddenFiles: [],
        requiredFeatures: [],
        minimumCommits: 0,
      },
      due_date: null,
    })
    newProjectName.value = ''
    newProjectDescription.value = ''
    await loadProjects()
  } catch (err) {
    projectsError.value =
      err instanceof Error ? err.message : 'No se pudo crear el proyecto'
  } finally {
    creatingProject.value = false
  }
}

async function handleDeleteProject(project: ProjectResponse) {
  const confirmed = window.confirm(
    `¿Eliminar el proyecto "${project.name}"? Esta acción no se puede deshacer.`,
  )
  if (!confirmed) return

  deletingProjectId.value = project.id
  projectsError.value = ''

  try {
    await deleteProject(project.id)
    await loadProjects()
  } catch (err) {
    projectsError.value =
      err instanceof Error ? err.message : 'No se pudo eliminar el proyecto'
  } finally {
    deletingProjectId.value = null
  }
}

async function handleSignOut() {
  try {
    await signOut()
    user.value = null
    await router.replace('/')
  } catch {
    // ignore
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
  <main class="min-h-screen bg-neutral-50 text-slate-950 lg:grid lg:grid-cols-[240px_1fr]">
    <aside class="border-b border-slate-200 bg-white/95 px-4 py-4 shadow-sm lg:min-h-screen lg:border-b-0 lg:border-r">
      <RouterLink to="/dashboard" class="flex items-center gap-2.5">
        <span class="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-600 text-base font-black text-white">E</span>
        <span class="text-xl font-black tracking-tight">Evalua<span class="text-emerald-600">Git</span></span>
      </RouterLink>

      <nav class="mt-5 flex gap-2 overflow-x-auto lg:mt-8 lg:flex-col lg:overflow-visible">
        <RouterLink to="/dashboard" class="flex min-w-fit items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 hover:text-emerald-700">
          <span class="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200">
            <Icon name="home" class="h-4 w-4" />
          </span>
          Dashboard
        </RouterLink>
        <RouterLink to="/projects" class="flex min-w-fit items-center gap-2.5 rounded-xl bg-emerald-50 px-3 py-2.5 text-sm font-bold text-emerald-700">
          <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-100">
            <Icon name="folder" class="h-4 w-4" />
          </span>
          Proyectos
        </RouterLink>
        <RouterLink to="/deliveries" class="flex min-w-fit items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 hover:text-emerald-700">
          <span class="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200">
            <Icon name="upload-cloud" class="h-4 w-4" />
          </span>
          Entregas
        </RouterLink>
        <span class="flex min-w-fit items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-400">
          <span class="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200">
            <Icon name="bar-chart" class="h-4 w-4" />
          </span>
          Resultados
        </span>
        <span class="flex min-w-fit items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-400">
          <span class="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200">
            <Icon name="settings" class="h-4 w-4" />
          </span>
          Configuración
        </span>
      </nav>

      <button
        type="button"
        class="mt-6 hidden w-full items-center justify-center rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm font-bold text-slate-700 transition hover:border-slate-950 hover:bg-white hover:text-slate-950 lg:inline-flex"
        @click="handleSignOut"
      >
        Cerrar sesión
      </button>
    </aside>

    <section class="min-w-0">
      <header class="border-b border-slate-200 bg-white/90 px-4 py-3 backdrop-blur-xl lg:px-8">
        <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <label class="relative w-full max-w-lg">
            <Icon name="search" class="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="search"
              placeholder="Buscar proyectos entregas estudiantes..."
              class="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100"
            />
          </label>

          <div class="flex items-center gap-3">
            <div class="relative hidden h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-600 md:flex">
              <Icon name="bell" class="h-4 w-4" />
              <span class="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-emerald-600 text-[10px] font-bold text-white">2</span>
            </div>
            <div class="flex items-center gap-2.5">
              <img
                v-if="profileImageUrl"
                :src="profileImageUrl"
                :alt="professorName"
                class="h-10 w-10 rounded-full object-cover ring-2 ring-white"
              />
              <div
                v-else
                class="flex h-10 w-10 items-center justify-center rounded-full bg-slate-900 text-sm font-bold text-white"
              >
                {{ initials }}
              </div>
              <div class="hidden sm:block">
                <p class="text-sm font-bold text-slate-950">{{ professorName }}</p>
                <p class="text-xs text-slate-500">Docente</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div class="mx-auto max-w-6xl px-4 py-6 lg:px-8 lg:py-7">
        <p v-if="projectsError" class="mb-6 rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">{{ projectsError }}</p>

        <section id="crear-proyecto" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-900/5">
          <div class="mb-5 flex items-center justify-between gap-4">
            <div>
              <h2 class="text-lg font-black text-slate-950">Crear proyecto</h2>
              <p class="mt-1 text-xs text-slate-500">Define un proyecto y comparte el código de acceso con tus alumnos.</p>
            </div>
          </div>

          <form class="grid gap-4 lg:grid-cols-[1fr_1.4fr_auto] lg:items-end" @submit.prevent="handleCreateProject">
            <label class="grid gap-1.5 text-xs font-bold text-slate-700">
              Nombre del proyecto
              <input
                v-model="newProjectName"
                type="text"
                placeholder="Proyecto final"
                autocomplete="off"
                class="rounded-xl border border-slate-200 px-3 py-2.5 text-sm font-medium text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100"
              />
            </label>

            <label class="grid gap-1.5 text-xs font-bold text-slate-700">
              Descripción
              <textarea
                v-model="newProjectDescription"
                rows="1"
                placeholder="Breve descripción del proyecto"
                class="min-h-[42px] resize-y rounded-xl border border-slate-200 px-3 py-2.5 text-sm font-medium text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100"
              />
            </label>

            <button
              class="inline-flex h-[42px] items-center justify-center rounded-xl bg-emerald-600 px-4 text-sm font-bold text-white shadow-sm shadow-emerald-900/15 transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
              type="submit"
              :disabled="creatingProject"
            >
              {{ creatingProject ? 'Creando...' : 'Crear proyecto' }}
            </button>
          </form>
        </section>

        <section class="mt-6">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-xl font-black text-slate-950">Listado de proyectos</h2>
            <p v-if="projectsLoading" class="text-sm text-slate-500">Cargando proyectos...</p>
          </div>

          <div v-if="projectsLoading" class="rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-500 shadow-sm shadow-slate-900/5">
            Cargando proyectos...
          </div>

          <div v-else-if="projects.length" class="grid gap-4 lg:grid-cols-2">
            <article
              v-for="project in projects"
              :key="project.id"
              class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-900/5"
            >
              <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <h3 class="text-base font-bold text-slate-950">{{ project.name }}</h3>
                  <p class="mt-1 line-clamp-2 text-xs leading-4 text-slate-500">{{ project.description || 'Sin descripción' }}</p>
                </div>
                <span v-if="project.join_code" class="mt-1 inline-flex w-fit items-center gap-1 rounded-full bg-emerald-50 px-2 py-1 font-mono text-[10px] font-black text-emerald-700 sm:mt-0">
                  <Icon name="key" class="h-3 w-3" />
                  {{ project.join_code }}
                </span>
              </div>

              <div class="mt-3 flex flex-wrap gap-2 text-[10px] text-slate-500">
                <span>{{ formatDate(project.created_at) }}</span>
              </div>

              <div class="mt-3 flex flex-col gap-1.5 sm:flex-row">
                <RouterLink
                  :to="`/projects/${project.id}`"
                  class="inline-flex items-center justify-center rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-bold text-white transition hover:bg-emerald-700"
                >
                  Ver detalle
                </RouterLink>
                <RouterLink
                  :to="`/projects/${project.id}/settings`"
                  class="inline-flex items-center justify-center gap-1 rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-700 transition hover:bg-slate-200"
                >
                  <Icon name="settings" class="h-3 w-3" />
                  Config
                </RouterLink>
                <button
                  class="inline-flex items-center justify-center gap-1 rounded-lg bg-red-50 px-3 py-1.5 text-xs font-bold text-red-600 transition hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-60"
                  :disabled="deletingProjectId === project.id"
                  @click="handleDeleteProject(project)"
                >
                  <Icon name="trash" class="h-3 w-3" />
                  {{ deletingProjectId === project.id ? 'Eliminando...' : 'Eliminar' }}
                </button>
              </div>
            </article>
          </div>

          <article v-else-if="!projectsError" class="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center shadow-sm shadow-slate-900/5">
            <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
              <Icon name="folder" class="h-6 w-6" />
            </div>
            <h3 class="mt-4 text-lg font-black text-slate-950">Aún no tienes proyectos</h3>
            <p class="mx-auto mt-2 max-w-md text-sm leading-5 text-slate-500">Crea tu primer proyecto para comenzar a recibir repositorios de alumnos.</p>
            <a href="#crear-proyecto" class="mt-5 inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-emerald-700">
              <Icon name="plus" class="h-4 w-4" />
              Crear proyecto
            </a>
          </article>
        </section>
      </div>
    </section>
  </main>
</template>
