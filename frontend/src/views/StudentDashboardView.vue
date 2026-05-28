<script setup lang="ts">
import { computed, h, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import type { User } from '@supabase/supabase-js'

import { getMe, type MeResponse } from '@/services/api'
import { getCurrentUser, signOut } from '@/services/auth'
import { getLatestAiAnalysis, type AiAnalysisRunResponse } from '@/services/aiAnalysis'
import { getJoinedProjects, joinProject, leaveJoinedProject, type ProjectResponse } from '@/services/projects'
import {
  createRepository,
  deleteRepository,
  getMyRepositories,
  type RepositoryResponse,
} from '@/services/repositories'

type IconName =
  | 'bar-chart'
  | 'brain'
  | 'chevron-right'
  | 'folder'
  | 'folder-open'
  | 'git-branch'
  | 'home'
  | 'log-out'
  | 'search'
  | 'settings'
  | 'zap'

const iconPaths: Record<IconName, string[]> = {
  'bar-chart': ['M3 3v18h18', 'M7 15v3', 'M12 10v8', 'M17 6v12'],
  brain: ['M9 3a3 3 0 0 0-3 3v1a3 3 0 0 0 0 6v1a3 3 0 0 0 3 3', 'M15 3a3 3 0 0 1 3 3v1a3 3 0 0 1 0 6v1a3 3 0 0 1-3 3', 'M9 3v18', 'M15 3v18', 'M9 8h2', 'M13 8h2', 'M9 16h2', 'M13 16h2'],
  'chevron-right': ['M9 18l6-6-6-6'],
  folder: ['M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z'],
  'folder-open': ['M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v2', 'M3 17l3-6h16l-3 8H5a2 2 0 0 1-2-2Z'],
  'git-branch': ['M6 3v12', 'M18 9v12', 'M6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z', 'M18 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z', 'M8.5 7.5h5a4.5 4.5 0 0 1 4.5 4.5'],
  home: ['M3 10.5 12 3l9 7.5', 'M5 10v10h14V10', 'M9 20v-6h6v6'],
  'log-out': ['M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4', 'M16 17l5-5-5-5', 'M21 12H9'],
  search: ['M21 21l-4.35-4.35', 'M10.5 18a7.5 7.5 0 1 0 0-15 7.5 7.5 0 0 0 0 15Z'],
  settings: ['M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z', 'M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 1.55V21a2 2 0 1 1-4 0v-.05a1.7 1.7 0 0 0-1-1.55 1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.55-1H3a2 2 0 1 1 0-4h.05A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.55V3a2 2 0 1 1 4 0v.05A1.7 1.7 0 0 0 15 4.6a1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.55 1H21a2 2 0 1 1 0 4h-.05A1.7 1.7 0 0 0 19.4 15Z'],
  zap: ['M13 2 3 14h8l-1 8 10-12h-8Z'],
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

const router = useRouter()

const user = ref<User | null>(null)
const me = ref<MeResponse | null>(null)

const loading = ref(true)
const loadingRepos = ref(false)
const projectsError = ref('')
const repositoriesError = ref('')
const resultsError = ref('')

const joinedProjects = ref<ProjectResponse[]>([])
const myRepositories = ref<RepositoryResponse[]>([])
const latestAiByRepository = ref<Record<string, AiAnalysisRunResponse | null>>({})

const searchQuery = ref('')
const selectedProjectId = ref<string | null>(null)

const joinCodeInput = ref('')
const joining = ref(false)
const joinError = ref('')
const joinSuccess = ref('')

const repositoryForms = reactive<Record<string, { repo_url: string; branch: string }>>({})
const repositoryErrors = reactive<Record<string, string>>({})
const repositorySuccess = reactive<Record<string, string>>({})
const creatingRepoId = ref<string | null>(null)
const deletingProjectId = ref<string | null>(null)

const studentName = computed(() => {
  const metadataName = user.value?.user_metadata?.full_name
  return me.value?.full_name || metadataName || user.value?.email || 'Alumno'
})

const initials = computed(() => {
  const source = studentName.value.trim()
  if (!source) return 'A'

  return source
    .split(/\s+/)
    .slice(0, 2)
    .map((part: string) => part.charAt(0).toUpperCase())
    .join('')
})

const profileImageUrl = computed(() => {
  const metadataAvatar = user.value?.user_metadata?.avatar_url
  if (typeof metadataAvatar === 'string' && metadataAvatar) return metadataAvatar
  return me.value?.avatar_url || null
})

const repositoryByProjectId = computed(() => {
  const map = new Map<string, RepositoryResponse>()
  for (const repository of myRepositories.value) {
    map.set(repository.project_id, repository)
  }
  return map
})

const filteredProjects = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return joinedProjects.value

  return joinedProjects.value.filter((project) => {
    return [project.name, project.description || '', project.join_code].some((value) =>
      value.toLowerCase().includes(query),
    )
  })
})

const latestTechnicalResult = computed(() => {
  return myRepositories.value
    .filter((repository) => Boolean(repository.last_analyzed_at))
    .sort((left, right) => {
      return new Date(right.last_analyzed_at || 0).getTime() - new Date(left.last_analyzed_at || 0).getTime()
    })[0] || null
})

const latestAiResult = computed(() => {
  return Object.values(latestAiByRepository.value)
    .filter((run): run is AiAnalysisRunResponse => Boolean(run))
    .sort((left, right) => {
      const leftDate = left.finished_at || left.created_at
      const rightDate = right.finished_at || right.created_at
      return new Date(rightDate).getTime() - new Date(leftDate).getTime()
    })[0] || null
})

onMounted(() => {
  void loadDashboard()
})

async function loadDashboard() {
  loading.value = true
  projectsError.value = ''
  repositoriesError.value = ''
  resultsError.value = ''

  try {
    user.value = await getCurrentUser()
  } catch {
    user.value = null
  }

  try {
    me.value = await getMe()
  } catch {
    me.value = null
  }

  await Promise.all([loadJoinedProjects(), loadMyRepositories()])

  if (!selectedProjectId.value && joinedProjects.value.length) {
    selectedProjectId.value = joinedProjects.value[0]?.id || null
  }

  await loadLatestAiAnalyses()
  loading.value = false
}

async function loadJoinedProjects() {
  projectsError.value = ''

  try {
    joinedProjects.value = await getJoinedProjects()
    for (const project of joinedProjects.value) {
      repositoryForms[project.id] = repositoryForms[project.id] || { repo_url: '', branch: 'main' }
    }
  } catch (err) {
    joinedProjects.value = []
    projectsError.value = err instanceof Error ? err.message : 'No se pudieron cargar tus proyectos'
  }
}

async function loadMyRepositories() {
  loadingRepos.value = true
  repositoriesError.value = ''

  try {
    myRepositories.value = await getMyRepositories()
  } catch (err) {
    myRepositories.value = []
    repositoriesError.value = err instanceof Error ? err.message : 'No se pudieron cargar tus repositorios'
  } finally {
    loadingRepos.value = false
  }
}

async function loadLatestAiAnalyses() {
  resultsError.value = ''

  if (!myRepositories.value.length) {
    latestAiByRepository.value = {}
    return
  }

  const entries = await Promise.all(
    myRepositories.value.map(async (repository) => {
      try {
        const run = await getLatestAiAnalysis(repository.id)
        return [repository.id, run] as const
      } catch (err) {
        if (err instanceof Error && /404|No hay analisis IA/i.test(err.message)) {
          return [repository.id, null] as const
        }

        resultsError.value = 'No se pudieron cargar algunos resultados de IA'
        return [repository.id, null] as const
      }
    }),
  )

  latestAiByRepository.value = Object.fromEntries(entries)
}

async function handleJoinProject() {
  const code = joinCodeInput.value.trim().toUpperCase()
  if (!code) {
    joinError.value = 'Ingresa un código de proyecto'
    return
  }

  joining.value = true
  joinError.value = ''
  joinSuccess.value = ''

  try {
    await joinProject(code)
    joinCodeInput.value = ''
    joinSuccess.value = 'Te uniste al proyecto correctamente'
    await loadJoinedProjects()
  } catch (err) {
    joinError.value = err instanceof Error ? err.message : 'No se pudo unir al proyecto'
  } finally {
    joining.value = false
  }
}

async function handleLinkRepo(projectId: string) {
  const form = repositoryForms[projectId]
  if (!form || !form.repo_url.trim()) {
    repositoryErrors[projectId] = 'La URL del repositorio es obligatoria'
    return
  }

  creatingRepoId.value = projectId
  repositoryErrors[projectId] = ''
  repositorySuccess[projectId] = ''

  try {
    await createRepository({
      project_id: projectId,
      repo_url: form.repo_url.trim(),
      branch: form.branch.trim() || 'main',
    })
    form.repo_url = ''
    form.branch = 'main'
    repositorySuccess[projectId] = 'Repositorio vinculado correctamente'
    await loadMyRepositories()
    await loadLatestAiAnalyses()
  } catch (err) {
    repositoryErrors[projectId] = err instanceof Error ? err.message : 'No se pudo vincular el repositorio'
  } finally {
    creatingRepoId.value = null
  }
}

async function handleDeleteRepo(repositoryId: string) {
  const confirmed = window.confirm('¿Eliminar este repositorio vinculado?')
  if (!confirmed) return

  try {
    await deleteRepository(repositoryId)
    await loadMyRepositories()
    await loadLatestAiAnalyses()
  } catch (err) {
    repositoriesError.value = err instanceof Error ? err.message : 'No se pudo eliminar el repositorio'
  }
}

async function handleLeaveProject(project: ProjectResponse) {
  const confirmed = window.confirm(`¿Eliminar "${project.name}" de tus proyectos?`)
  if (!confirmed) return

  deletingProjectId.value = project.id
  projectsError.value = ''

  try {
    await leaveJoinedProject(project.id)
    if (selectedProjectId.value === project.id) {
      selectedProjectId.value = null
    }
    delete repositoryForms[project.id]
    delete repositoryErrors[project.id]
    delete repositorySuccess[project.id]
    await Promise.all([loadJoinedProjects(), loadMyRepositories()])
    await loadLatestAiAnalyses()
  } catch (err) {
    projectsError.value = err instanceof Error ? err.message : 'No se pudo eliminar el proyecto'
  } finally {
    deletingProjectId.value = null
  }
}

async function handleSignOut() {
  try {
    await signOut()
    me.value = null
    user.value = null
    await router.replace('/')
  } catch {
    // ignore
  }
}

function focusRepositoryForm(projectId: string) {
  selectedProjectId.value = projectId
  const target = document.getElementById(`repo-url-${projectId}`) as HTMLInputElement | null
  if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'center' })
    target.focus()
  }
}

function selectProject(projectId: string) {
  selectedProjectId.value = projectId
  const target = document.getElementById(`project-${projectId}`)
  target?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

function formatDate(value: string | null): string {
  if (!value) return 'No disponible'
  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
  }).format(new Date(value))
}

function formatDateTime(value: string | null): string {
  if (!value) return 'No disponible'
  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function getProjectRepository(projectId: string): RepositoryResponse | null {
  return repositoryByProjectId.value.get(projectId) || null
}

function getProjectAnalysisCount(projectId: string): number {
  const repository = getProjectRepository(projectId)
  if (!repository) return 0

  let count = repository.last_analyzed_at ? 1 : 0
  if (latestAiByRepository.value[repository.id]) count += 1
  return count
}

function getProjectStatus(projectId: string): 'Vinculado' | 'Pendiente' {
  return getProjectRepository(projectId) ? 'Vinculado' : 'Pendiente'
}

function getStatusBadgeClass(status: string): string {
  const normalized = status.toUpperCase()
  if (normalized === 'COMPLETED' || normalized === 'ANALYZED') {
    return 'border-emerald-200 bg-emerald-50 text-emerald-800'
  }
  if (normalized === 'FAILED') {
    return 'border-red-200 bg-red-50 text-red-700'
  }
  if (normalized === 'RUNNING' || normalized === 'ANALYZING') {
    return 'border-amber-200 bg-amber-50 text-amber-700'
  }
  return 'border-slate-200 bg-slate-100 text-slate-700'
}

function getStatusLabel(status: string): string {
  const normalized = status.toUpperCase()
  if (normalized === 'COMPLETED') return 'Completado'
  if (normalized === 'FAILED') return 'Fallido'
  if (normalized === 'RUNNING') return 'En curso'
  if (normalized === 'PENDING') return 'Pendiente'
  if (normalized === 'ANALYZED') return 'Analizado'
  if (normalized === 'ANALYZING') return 'Analizando'
  return status
}

function getProjectName(projectId: string): string {
  return joinedProjects.value.find((project) => project.id === projectId)?.name || 'Proyecto'
}

function getProjectNameByRepositoryId(repositoryId: string): string {
  const repository = myRepositories.value.find((item) => item.id === repositoryId)
  return repository ? getProjectName(repository.project_id) : 'Proyecto'
}

function getRepositoryForm(projectId: string) {
  return repositoryForms[projectId] || { repo_url: '', branch: 'main' }
}
</script>

<template>
  <main class="min-h-screen bg-neutral-50 text-slate-950 lg:grid lg:grid-cols-[240px_1fr]">
    <aside class="border-b border-slate-200 bg-white/95 px-4 py-4 shadow-sm lg:min-h-screen lg:border-b-0 lg:border-r">
      <div class="flex items-center justify-between lg:block">
        <RouterLink to="/student/dashboard" class="flex cursor-pointer items-center gap-2.5">
          <span class="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-700 text-base font-black text-white">E</span>
          <span class="text-xl font-black tracking-tight">Evalua<span class="text-emerald-700">Git</span></span>
        </RouterLink>
      </div>

      <nav class="mt-5 flex gap-2 overflow-x-auto lg:mt-8 lg:flex-col lg:overflow-visible">
        <a
          href="#unirse-proyecto"
          class="flex min-w-fit cursor-pointer items-center gap-2.5 rounded-xl bg-emerald-100 px-3 py-2.5 text-sm font-bold text-emerald-800"
        >
          <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-200/70">
            <Icon name="home" class="h-4 w-4" />
          </span>
          Mi panel
        </a>
        <a
          href="#mis-proyectos"
          class="flex min-w-fit cursor-pointer items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 hover:text-emerald-800"
        >
          <span class="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200">
            <Icon name="folder" class="h-4 w-4" />
          </span>
          Mis proyectos
        </a>
        <a
          href="#resultados-recientes"
          class="flex min-w-fit cursor-pointer items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 hover:text-emerald-800"
        >
          <span class="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200">
            <Icon name="bar-chart" class="h-4 w-4" />
          </span>
          Resultados
        </a>
        <span class="flex min-w-fit items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-400">
          <span class="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200">
            <Icon name="settings" class="h-4 w-4" />
          </span>
          Configuración
        </span>
      </nav>

      <button
        type="button"
        class="mt-6 hidden w-full cursor-pointer items-center justify-center rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm font-bold text-slate-700 transition hover:border-emerald-700 hover:bg-white hover:text-emerald-800 lg:inline-flex"
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
              v-model="searchQuery"
              type="search"
              placeholder="Buscar proyectos repositorios resultados..."
              class="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-emerald-600 focus:ring-4 focus:ring-emerald-100"
            />
          </label>

          <div class="flex items-center gap-3">
            <button
              type="button"
              class="hidden cursor-pointer items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:border-emerald-700 hover:text-emerald-800 md:inline-flex"
              @click="handleSignOut"
            >
              <Icon name="log-out" class="h-4 w-4" />
              Cerrar sesión
            </button>
            <div class="flex items-center gap-2.5">
              <img
                v-if="profileImageUrl"
                :src="profileImageUrl"
                :alt="studentName"
                class="h-10 w-10 rounded-full object-cover ring-2 ring-white"
              />
              <div
                v-else
                class="flex h-10 w-10 items-center justify-center rounded-full bg-slate-900 text-sm font-bold text-white"
              >
                {{ initials }}
              </div>
              <div class="hidden sm:block">
                <p class="text-sm font-bold text-slate-950">{{ studentName }}</p>
                <p class="text-xs text-slate-500">Alumno</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div class="mx-auto max-w-6xl px-4 py-6 lg:px-8 lg:py-7">
        <p v-if="projectsError" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ projectsError }}</p>
        <p v-if="repositoriesError" class="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ repositoriesError }}</p>
        <p v-if="resultsError" class="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">{{ resultsError }}</p>

        <section class="mt-7 grid gap-7 xl:grid-cols-[0.95fr_1.05fr]">
          <article id="unirse-proyecto" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-900/5">
            <div class="flex items-center gap-3">
              <span class="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-50 text-emerald-800">
                <Icon name="zap" class="h-5 w-5" />
              </span>
              <div>
                <h2 class="text-xl font-black text-slate-950">Unirme a un proyecto</h2>
                <p class="mt-1 text-sm text-slate-500">Ingresa el código que te compartió tu profesor.</p>
              </div>
            </div>

            <div class="mt-6 flex flex-col gap-3 sm:flex-row">
              <input
                v-model="joinCodeInput"
                type="text"
                maxlength="10"
                placeholder="Código del proyecto"
                class="flex-1 rounded-xl border border-slate-200 px-4 py-3 font-mono text-sm uppercase text-slate-900 outline-none transition focus:border-emerald-600 focus:ring-4 focus:ring-emerald-100"
                :disabled="joining"
                @keyup.enter="handleJoinProject"
              />
              <button
                type="button"
                :disabled="joining"
                class="inline-flex cursor-pointer items-center justify-center rounded-xl bg-emerald-700 px-5 py-3 text-sm font-bold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-60"
                @click="handleJoinProject"
              >
                {{ joining ? 'Uniendo...' : 'Unirme a un proyecto' }}
              </button>
            </div>

            <p v-if="joinError" class="mt-3 text-sm text-red-600">{{ joinError }}</p>
            <p v-if="joinSuccess" class="mt-3 text-sm font-medium text-emerald-800">{{ joinSuccess }}</p>
          </article>

          <article id="resultados-recientes" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-900/5">
            <div class="flex items-center gap-3">
              <span class="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-50 text-emerald-800">
                <Icon name="brain" class="h-5 w-5" />
              </span>
              <div>
                <h2 class="text-xl font-black text-slate-950">Resultados recientes</h2>
                <p class="mt-1 text-sm text-slate-500">Consulta el estado más reciente de tus análisis técnico e IA.</p>
              </div>
            </div>

            <div v-if="!latestTechnicalResult && !latestAiResult" class="mt-6 rounded-2xl border border-dashed border-slate-300 px-6 py-10 text-center text-sm text-slate-500">
              Aún no tienes resultados disponibles.
            </div>

            <div v-else class="mt-6 grid gap-4 lg:grid-cols-2">
              <article class="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div class="flex items-center gap-3">
                  <span class="flex h-10 w-10 items-center justify-center rounded-full bg-white text-emerald-800">
                    <Icon name="bar-chart" class="h-5 w-5" />
                  </span>
                  <div>
                    <h3 class="text-lg font-bold text-slate-950">Último análisis técnico</h3>
                    <p class="text-sm text-slate-500">{{ latestTechnicalResult ? getProjectName(latestTechnicalResult.project_id) : 'No disponible' }}</p>
                  </div>
                </div>

                <div v-if="latestTechnicalResult" class="mt-5 space-y-3">
                  <div class="flex items-center justify-between">
                    <span class="text-sm text-slate-500">Estado</span>
                    <span class="inline-flex items-center rounded-full border px-3 py-1 text-xs font-bold" :class="getStatusBadgeClass(latestTechnicalResult.status)">
                      {{ getStatusLabel(latestTechnicalResult.status) }}
                    </span>
                  </div>
                  <div class="flex items-center justify-between gap-4">
                    <span class="text-sm text-slate-500">Fecha</span>
                    <span class="text-sm font-semibold text-slate-900">{{ formatDateTime(latestTechnicalResult.last_analyzed_at) }}</span>
                  </div>
                  <div class="flex items-center justify-between gap-4">
                    <span class="text-sm text-slate-500">Rama</span>
                    <span class="text-sm font-semibold text-slate-900">{{ latestTechnicalResult.branch }}</span>
                  </div>
                </div>

                <p v-else class="mt-5 text-sm text-slate-500">Aún no tienes resultados disponibles.</p>
              </article>

              <article class="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div class="flex items-center gap-3">
                  <span class="flex h-10 w-10 items-center justify-center rounded-full bg-white text-emerald-800">
                    <Icon name="brain" class="h-5 w-5" />
                  </span>
                  <div>
                    <h3 class="text-lg font-bold text-slate-950">Último análisis IA</h3>
                    <p class="text-sm text-slate-500">{{ latestAiResult ? getProjectNameByRepositoryId(latestAiResult.repository_id) : 'No disponible' }}</p>
                  </div>
                </div>

                <div v-if="latestAiResult" class="mt-5 space-y-3">
                  <div class="flex items-center justify-between">
                    <span class="text-sm text-slate-500">Estado</span>
                    <span class="inline-flex items-center rounded-full border px-3 py-1 text-xs font-bold" :class="getStatusBadgeClass(latestAiResult.status)">
                      {{ getStatusLabel(latestAiResult.status) }}
                    </span>
                  </div>
                  <div class="flex items-center justify-between gap-4">
                    <span class="text-sm text-slate-500">Fecha</span>
                    <span class="text-sm font-semibold text-slate-900">{{ formatDateTime(latestAiResult.finished_at || latestAiResult.created_at) }}</span>
                  </div>
                  <div class="flex items-center justify-between gap-4">
                    <span class="text-sm text-slate-500">Resumen</span>
                    <span class="text-sm font-semibold text-slate-900">
                      {{ latestAiResult.result_json?.risk_level || latestAiResult.result_json?.message || 'Disponible' }}
                    </span>
                  </div>
                </div>

                <p v-else class="mt-5 text-sm text-slate-500">Aún no tienes resultados disponibles.</p>
              </article>
            </div>
          </article>
        </section>

        <section id="mis-proyectos" class="mt-7 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-900/5">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div class="flex items-center gap-3">
              <span class="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-50 text-emerald-800">
                <Icon name="folder-open" class="h-5 w-5" />
              </span>
              <div>
                <h2 class="text-xl font-black text-slate-950">Mis proyectos</h2>
                <p class="mt-1 text-sm text-slate-500">Revisa tu estado actual y vincula tu repositorio cuando haga falta.</p>
              </div>
            </div>
            <p class="text-sm text-slate-500">
              {{ filteredProjects.length }} {{ filteredProjects.length === 1 ? 'proyecto visible' : 'proyectos visibles' }}
            </p>
          </div>

          <div v-if="loading" class="mt-6 text-sm text-slate-500">Cargando proyectos...</div>
          <div v-else-if="!filteredProjects.length" class="mt-6 rounded-2xl border border-dashed border-slate-300 px-6 py-10 text-center text-sm text-slate-500">
            Aún no tienes proyectos para mostrar con este filtro.
          </div>

          <div v-else class="mt-6 grid gap-5 lg:grid-cols-2">
            <article
              v-for="project in filteredProjects"
              :id="`project-${project.id}`"
              :key="project.id"
              class="rounded-2xl border p-5 transition"
              :class="selectedProjectId === project.id ? 'border-emerald-300 bg-emerald-50/40' : 'border-slate-200 bg-white'"
            >
              <div class="flex flex-col gap-4">
                <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h3 class="text-lg font-bold text-slate-950">{{ project.name }}</h3>
                    <p class="mt-1 text-sm text-slate-500">{{ project.description || 'Sin descripción disponible.' }}</p>
                  </div>
                  <span
                    class="inline-flex items-center rounded-full border px-3 py-1 text-xs font-bold"
                    :class="getProjectStatus(project.id) === 'Vinculado' ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-amber-200 bg-amber-50 text-amber-700'"
                  >
                    {{ getProjectStatus(project.id) }}
                  </span>
                </div>

                <div class="grid gap-3 sm:grid-cols-3">
                  <div class="rounded-2xl bg-slate-50 px-4 py-3">
                    <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Código del proyecto</p>
                    <p class="mt-1 font-mono text-sm font-bold text-slate-900">{{ project.join_code }}</p>
                  </div>
                  <div class="rounded-2xl bg-slate-50 px-4 py-3">
                    <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Repositorio</p>
                    <p class="mt-1 text-sm font-semibold text-slate-900">{{ getProjectStatus(project.id) }}</p>
                  </div>
                  <div class="rounded-2xl bg-slate-50 px-4 py-3">
                    <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Análisis disponibles</p>
                    <p class="mt-1 text-sm font-semibold text-slate-900">{{ getProjectAnalysisCount(project.id) }}</p>
                  </div>
                </div>

                <div v-if="getProjectRepository(project.id)" class="rounded-2xl border border-slate-200 bg-white px-4 py-3">
                  <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p class="text-sm font-semibold text-slate-900">{{ getProjectRepository(project.id)?.repo_url }}</p>
                      <p class="mt-1 text-xs text-slate-500">
                        Rama {{ getProjectRepository(project.id)?.branch }} · Último análisis {{ formatDate(getProjectRepository(project.id)?.last_analyzed_at || null) }}
                      </p>
                    </div>
                    <button
                      type="button"
                      class="inline-flex cursor-pointer items-center justify-center rounded-lg border border-red-200 px-3 py-2 text-xs font-bold text-red-600 transition hover:bg-red-50"
                      @click="handleDeleteRepo(getProjectRepository(project.id)!.id)"
                    >
                      Quitar vínculo
                    </button>
                  </div>
                </div>

                <div v-else class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-3">
                  <p class="text-sm font-semibold text-slate-800">Aún no has vinculado un repositorio.</p>
                  <p class="mt-1 text-xs text-slate-500">Agrega la URL de tu repositorio Git para habilitar los análisis.</p>
                </div>

                <div class="flex flex-col gap-3 sm:flex-row">
                  <button
                    type="button"
                    class="inline-flex cursor-pointer items-center justify-center rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-emerald-300 hover:text-emerald-800"
                    @click="selectProject(project.id)"
                  >
                    Ver proyecto
                  </button>
                  <button
                    type="button"
                    :disabled="deletingProjectId === project.id"
                    class="inline-flex cursor-pointer items-center justify-center rounded-xl border border-red-200 px-4 py-2.5 text-sm font-bold text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60"
                    @click="handleLeaveProject(project)"
                  >
                    {{ deletingProjectId === project.id ? 'Eliminando...' : 'Eliminar proyecto' }}
                  </button>
                  <button
                    v-if="!getProjectRepository(project.id)"
                    type="button"
                    class="inline-flex cursor-pointer items-center justify-center rounded-xl bg-emerald-700 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-emerald-800"
                    @click="focusRepositoryForm(project.id)"
                  >
                    Vincular repositorio
                  </button>
                </div>

                <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
                  <h4 class="text-sm font-bold text-slate-900">Vincular mi repositorio</h4>
                  <div class="mt-3 grid gap-3 xl:grid-cols-[minmax(0,1fr)_9rem_auto]">
                    <input
                      :id="`repo-url-${project.id}`"
                      v-model="getRepositoryForm(project.id).repo_url"
                      type="url"
                      placeholder="https://github.com/usuario/repositorio"
                      class="min-w-0 rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-600 focus:ring-4 focus:ring-emerald-100"
                      :disabled="creatingRepoId === project.id"
                    />
                    <input
                      v-model="getRepositoryForm(project.id).branch"
                      type="text"
                      placeholder="main"
                      class="min-w-0 rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-600 focus:ring-4 focus:ring-emerald-100"
                      :disabled="creatingRepoId === project.id"
                    />
                    <button
                      type="button"
                      :disabled="creatingRepoId === project.id"
                      class="inline-flex w-full cursor-pointer items-center justify-center rounded-xl bg-emerald-700 px-4 py-3 text-sm font-bold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-60 xl:w-auto"
                      @click="handleLinkRepo(project.id)"
                    >
                      {{ creatingRepoId === project.id ? 'Vinculando...' : 'Vincular repositorio' }}
                    </button>
                  </div>
                  <p v-if="repositoryErrors[project.id]" class="mt-3 text-sm text-red-600">{{ repositoryErrors[project.id] }}</p>
                  <p v-if="repositorySuccess[project.id]" class="mt-3 text-sm font-medium text-emerald-800">{{ repositorySuccess[project.id] }}</p>
                </div>
              </div>
            </article>
          </div>
        </section>

      </div>
    </section>
  </main>
</template>
