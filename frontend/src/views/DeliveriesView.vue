<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import type { User } from '@supabase/supabase-js'
import {
  analyzeRepositoryWithAi,
  getLatestAiAnalysis,
  type AiAnalysisRunResponse,
  type AiAnalysisResponse,
} from '@/services/aiAnalysis'
import {
  analyzeRepository,
  type AnalysisRunResponse,
} from '@/services/analysis'
import {
  deleteRepository,
  getProjectRepositories,
  type RepositoryWithStudent,
} from '@/services/repositories'
import { getProjects, type ProjectResponse } from '@/services/projects'
import AiAnalysisResult from '@/components/AiAnalysisResult.vue'
import { getCurrentUser, signOut } from '@/services/auth'

const router = useRouter()

type IconName =
  | 'bar-chart'
  | 'bell'
  | 'brain'
  | 'code'
  | 'folder'
  | 'home'
  | 'inbox'
  | 'search'
  | 'settings'
  | 'trash'
  | 'upload-cloud'

const iconPaths: Record<IconName, string[]> = {
  'bar-chart': ['M3 3v18h18', 'M7 15v2', 'M12 10v7', 'M17 6v11'],
  bell: ['M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9', 'M13.73 21a2 2 0 0 1-3.46 0'],
  brain: ['M9 3a3 3 0 0 0-3 3v1a3 3 0 0 0 0 6v1a3 3 0 0 0 3 3', 'M15 3a3 3 0 0 1 3 3v1a3 3 0 0 1 0 6v1a3 3 0 0 1-3 3', 'M9 3v18', 'M15 3v18', 'M9 8h2', 'M13 8h2', 'M9 16h2', 'M13 16h2'],
  code: ['M16 18l6-6-6-6', 'M8 6l-6 6 6 6'],
  folder: ['M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z'],
  home: ['M3 10.5 12 3l9 7.5', 'M5 10v10h14V10', 'M9 20v-6h6v6'],
  inbox: ['M4 4h16l2 10v6H2v-6Z', 'M2 14h6a4 4 0 0 0 8 0h6'],
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

type DeliveryWithProject = RepositoryWithStudent & {
  project_name: string
}

const user = ref<User | null>(null)
const projects = ref<ProjectResponse[]>([])
const deliveries = ref<DeliveryWithProject[]>([])
const loading = ref(false)
const loadError = ref('')

const searchQuery = ref('')
const selectedProjectId = ref('')
const selectedStatus = ref('')

const analyzingRepoId = ref<string | null>(null)
const analysisResult = ref<AnalysisRunResponse | null>(null)
const analysisError = ref('')
const aiAnalysisRun = ref<AiAnalysisRunResponse | null>(null)
const aiAnalysisResult = ref<AiAnalysisResponse | null>(null)
const aiAnalysisError = ref('')
const aiAnalyzingRepoId = ref<string | null>(null)
const aiLoadingLatestRepoId = ref<string | null>(null)
const deletingRepoId = ref<string | null>(null)
const failedAvatars = ref<Set<string>>(new Set())

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

const filteredDeliveries = computed(() => {
  let result = deliveries.value

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(
      (d) =>
        d.student.full_name.toLowerCase().includes(q) ||
        d.student.email.toLowerCase().includes(q) ||
        d.repo_url.toLowerCase().includes(q) ||
        d.project_name.toLowerCase().includes(q),
    )
  }

  if (selectedProjectId.value) {
    result = result.filter((d) => d.project_id === selectedProjectId.value)
  }

  if (selectedStatus.value) {
    result = result.filter((d) => d.status === selectedStatus.value)
  }

  return result
})

const analyzedCount = computed(() =>
  deliveries.value.filter((d) => d.status === 'ANALYZED' || d.last_analyzed_at).length,
)

const pendingCount = computed(() =>
  deliveries.value.filter((d) => d.status !== 'ANALYZED' && !d.last_analyzed_at).length,
)

const projectsWithDeliveries = computed(() => {
  const ids = new Set(deliveries.value.map((d) => d.project_id))
  return ids.size
})

onMounted(() => {
  void loadUser()
  void loadDeliveries()
})

async function loadUser() {
  try {
    user.value = await getCurrentUser()
  } catch {
    user.value = null
  }
}

async function loadDeliveries() {
  loading.value = true
  loadError.value = ''

  try {
    projects.value = await getProjects()
    const allDeliveries: DeliveryWithProject[] = []

    for (const project of projects.value) {
      try {
        const repos = await getProjectRepositories(project.id)
        const withProject = repos.map((r) => ({
          ...r,
          project_name: project.name,
        }))
        allDeliveries.push(...withProject)
      } catch {
        // skip projects that fail to load repos
      }
    }

    deliveries.value = allDeliveries
  } catch (err) {
    deliveries.value = []
    loadError.value =
      err instanceof Error ? err.message : 'No se pudieron cargar las entregas'
  } finally {
    loading.value = false
  }
}

async function handleDeleteRepository(repo: DeliveryWithProject) {
  const confirmed = window.confirm(
    `¿Eliminar el repositorio ${repo.repo_url}?`,
  )
  if (!confirmed) return

  deletingRepoId.value = repo.id
  loadError.value = ''

  try {
    await deleteRepository(repo.id)
    analysisResult.value = null
    analysisError.value = ''
    aiAnalysisRun.value = null
    aiAnalysisResult.value = null
    aiAnalysisError.value = ''
    await loadDeliveries()
  } catch (err) {
    loadError.value =
      err instanceof Error ? err.message : 'No se pudo eliminar el repositorio'
  } finally {
    deletingRepoId.value = null
  }
}

async function handleAnalyze(repo: DeliveryWithProject) {
  analyzingRepoId.value = repo.id
  analysisError.value = ''
  analysisResult.value = null

  try {
    const result = await analyzeRepository(repo.id)
    analysisResult.value = result
    await loadDeliveries()
  } catch (err) {
    analysisError.value =
      err instanceof Error ? err.message : 'No se pudo analizar el repositorio'
  } finally {
    analyzingRepoId.value = null
  }
}

async function handleAiAnalysis(repo: DeliveryWithProject) {
  aiAnalyzingRepoId.value = repo.id
  aiAnalysisError.value = ''
  aiAnalysisRun.value = null
  aiAnalysisResult.value = null

  try {
    const result = await analyzeRepositoryWithAi(repo.id)
    aiAnalysisRun.value = result
    aiAnalysisResult.value = result.result_json
  } catch (err) {
    aiAnalysisError.value =
      err instanceof Error ? err.message : 'No se pudo completar el análisis IA'
  } finally {
    aiAnalyzingRepoId.value = null
  }
}

async function handleLatestAiAnalysis(repo: DeliveryWithProject) {
  aiLoadingLatestRepoId.value = repo.id
  aiAnalysisError.value = ''
  aiAnalysisRun.value = null
  aiAnalysisResult.value = null

  try {
    const result = await getLatestAiAnalysis(repo.id)
    aiAnalysisRun.value = result
    aiAnalysisResult.value = result.result_json
  } catch (err) {
    const message = err instanceof Error ? err.message : 'No se pudo cargar el análisis IA'
    aiAnalysisError.value =
      message === 'No hay analisis IA para este repositorio'
        ? 'Este repositorio aún no tiene análisis IA'
        : message
  } finally {
    aiLoadingLatestRepoId.value = null
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

function handleAvatarError(studentId: string) {
  failedAvatars.value.add(studentId)
}

function avatarHasFailed(studentId: string): boolean {
  return failedAvatars.value.has(studentId)
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'LINKED': return 'Vinculado'
    case 'ANALYZING': return 'Analizando'
    case 'ANALYZED': return 'Analizado'
    case 'FAILED': return 'Fallido'
    default: return status
  }
}

function getStatusClasses(status: string): string {
  switch (status) {
    case 'LINKED':
      return 'bg-slate-100 text-slate-600'
    case 'ANALYZING':
      return 'bg-amber-50 text-amber-700'
    case 'ANALYZED':
      return 'bg-emerald-50 text-emerald-700'
    case 'FAILED':
      return 'bg-red-50 text-red-700'
    default:
      return 'bg-slate-100 text-slate-600'
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
        <RouterLink to="/projects" class="flex min-w-fit items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 hover:text-emerald-700">
          <span class="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200">
            <Icon name="folder" class="h-4 w-4" />
          </span>
          Proyectos
        </RouterLink>
        <RouterLink to="/deliveries" class="flex min-w-fit items-center gap-2.5 rounded-xl bg-emerald-50 px-3 py-2.5 text-sm font-bold text-emerald-700">
          <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-100">
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
        <div class="mb-6">
          <h1 class="text-2xl font-black text-slate-950">Entregas</h1>
          <p class="mt-1 text-sm text-slate-500">Consulta los repositorios vinculados por tus alumnos en todos tus proyectos.</p>
        </div>

        <p v-if="loadError" class="mb-6 rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">{{ loadError }}</p>

        <section class="mb-6 grid gap-4 lg:grid-cols-4">
          <article class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-900/5">
            <div class="flex items-start gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
                <Icon name="inbox" class="h-5 w-5" />
              </div>
              <div>
                <p class="text-xs font-medium text-slate-600">Entregas recibidas</p>
                <p class="mt-0.5 text-xl font-black text-slate-950">{{ deliveries.length }}</p>
              </div>
            </div>
          </article>
          <article class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-900/5">
            <div class="flex items-start gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
                <Icon name="code" class="h-5 w-5" />
              </div>
              <div>
                <p class="text-xs font-medium text-slate-600">Entregas analizadas</p>
                <p class="mt-0.5 text-xl font-black text-slate-950">{{ analyzedCount }}</p>
              </div>
            </div>
          </article>
          <article class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-900/5">
            <div class="flex items-start gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
                <Icon name="upload-cloud" class="h-5 w-5" />
              </div>
              <div>
                <p class="text-xs font-medium text-slate-600">Pendientes de análisis</p>
                <p class="mt-0.5 text-xl font-black text-slate-950">{{ pendingCount }}</p>
              </div>
            </div>
          </article>
          <article class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-900/5">
            <div class="flex items-start gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
                <Icon name="folder" class="h-5 w-5" />
              </div>
              <div>
                <p class="text-xs font-medium text-slate-600">Proyectos con entregas</p>
                <p class="mt-0.5 text-xl font-black text-slate-950">{{ projectsWithDeliveries }}</p>
              </div>
            </div>
          </article>
        </section>

        <section class="mb-6 rounded-xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-900/5">
          <div class="grid gap-3 lg:grid-cols-[1fr_200px_180px]">
            <label class="relative">
              <Icon name="search" class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Buscar por alumno, correo o repositorio..."
                class="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-2 focus:ring-emerald-100"
              />
            </label>
            <select
              v-model="selectedProjectId"
              class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none transition focus:border-emerald-300 focus:ring-2 focus:ring-emerald-100"
            >
              <option value="">Todos los proyectos</option>
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
            <select
              v-model="selectedStatus"
              class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none transition focus:border-emerald-300 focus:ring-2 focus:ring-emerald-100"
            >
              <option value="">Todos los estados</option>
              <option value="LINKED">Vinculado</option>
              <option value="ANALYZED">Analizado</option>
              <option value="FAILED">Fallido</option>
            </select>
          </div>
        </section>

        <div v-if="loading" class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500 shadow-sm shadow-slate-900/5">
          Cargando entregas...
        </div>

        <section v-else-if="filteredDeliveries.length" class="space-y-4">
          <div class="hidden overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm shadow-slate-900/5 lg:block">
            <table class="w-full text-left text-sm">
              <thead class="border-b border-slate-200 bg-slate-50 text-xs font-bold uppercase text-slate-500">
                <tr>
                  <th class="px-4 py-3">Alumno</th>
                  <th class="px-4 py-3">Proyecto</th>
                  <th class="px-4 py-3">Repositorio</th>
                  <th class="px-4 py-3">Rama</th>
                  <th class="px-4 py-3">Estado</th>
                  <th class="px-4 py-3">Último commit</th>
                  <th class="px-4 py-3">Último análisis</th>
                  <th class="px-4 py-3 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 bg-white text-slate-700">
                <tr v-for="repo in filteredDeliveries" :key="repo.id" class="hover:bg-slate-50/50">
                  <td class="px-4 py-3">
                    <div class="flex items-center gap-2">
                      <img
                        v-if="repo.student.avatar_url && !avatarHasFailed(repo.student.id)"
                        :src="repo.student.avatar_url"
                        :alt="repo.student.full_name"
                        class="h-6 w-6 rounded-full object-cover"
                        @error="handleAvatarError(repo.student.id)"
                      />
                      <div
                        v-else
                        class="flex h-6 w-6 items-center justify-center rounded-full bg-slate-200 text-[10px] font-bold text-slate-600"
                      >
                        {{ repo.student.full_name.charAt(0).toUpperCase() }}
                      </div>
                      <div>
                        <p class="text-xs font-bold text-slate-950">{{ repo.student.full_name }}</p>
                        <p class="text-[11px] text-slate-500">{{ repo.student.email }}</p>
                      </div>
                    </div>
                  </td>
                  <td class="px-4 py-3">
                    <span class="text-xs font-medium text-slate-700">{{ repo.project_name }}</span>
                  </td>
                  <td class="px-4 py-3">
                    <a
                      :href="repo.repo_url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="text-xs font-medium text-emerald-700 underline hover:text-emerald-500"
                    >
                      {{ repo.repo_url.length > 30 ? repo.repo_url.substring(0, 30) + '...' : repo.repo_url }}
                    </a>
                  </td>
                  <td class="px-4 py-3">
                    <span class="text-xs font-medium text-slate-500">{{ repo.branch }}</span>
                  </td>
                  <td class="px-4 py-3">
                    <span
                      class="inline-flex rounded-full px-2 py-0.5 text-[10px] font-bold"
                      :class="getStatusClasses(repo.status)"
                    >
                      {{ getStatusLabel(repo.status) }}
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <span v-if="repo.last_commit_hash" class="font-mono text-xs text-slate-600">
                      {{ repo.last_commit_hash.substring(0, 7) }}
                    </span>
                    <span v-else class="text-xs text-slate-400">—</span>
                  </td>
                  <td class="px-4 py-3">
                    <span v-if="repo.last_analyzed_at" class="text-xs text-slate-600">
                      {{ formatDate(repo.last_analyzed_at) }}
                    </span>
                    <span v-else class="text-xs text-slate-400">—</span>
                  </td>
                  <td class="px-4 py-3 text-right">
                    <div class="flex items-center justify-end gap-1">
                      <RouterLink
                        :to="`/projects/${repo.project_id}`"
                        class="rounded-md px-2 py-1 text-[11px] font-bold text-emerald-700 transition hover:bg-emerald-50"
                      >
                        Ver proyecto
                      </RouterLink>
                      <button
                        class="rounded-md px-2 py-1 text-[11px] font-bold text-slate-600 transition hover:bg-slate-100 disabled:opacity-50"
                        type="button"
                        :disabled="analyzingRepoId === repo.id || repo.status === 'ANALYZING'"
                        @click="handleAnalyze(repo)"
                      >
                        {{ analyzingRepoId === repo.id || repo.status === 'ANALYZING' ? 'Analizando...' : 'Análisis técnico' }}
                      </button>
                      <button
                        class="rounded-md px-2 py-1 text-[11px] font-bold text-blue-600 transition hover:bg-blue-50 disabled:opacity-50"
                        type="button"
                        :disabled="aiAnalyzingRepoId === repo.id || aiLoadingLatestRepoId === repo.id"
                        @click="handleAiAnalysis(repo)"
                      >
                        {{ aiAnalyzingRepoId === repo.id ? 'Analizando IA...' : 'Análisis IA' }}
                      </button>
                      <button
                        class="rounded-md px-2 py-1 text-[11px] font-bold text-blue-500 transition hover:bg-blue-50 disabled:opacity-50"
                        type="button"
                        :disabled="aiAnalyzingRepoId === repo.id || aiLoadingLatestRepoId === repo.id"
                        @click="handleLatestAiAnalysis(repo)"
                      >
                        {{ aiLoadingLatestRepoId === repo.id ? 'Cargando...' : 'Ver último IA' }}
                      </button>
                      <button
                        class="rounded-md px-2 py-1 text-[11px] font-bold text-red-500 transition hover:bg-red-50 disabled:opacity-50"
                        type="button"
                        :disabled="deletingRepoId === repo.id"
                        @click="handleDeleteRepository(repo)"
                      >
                        {{ deletingRepoId === repo.id ? 'Eliminando...' : 'Eliminar' }}
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="grid gap-3 lg:hidden">
            <article
              v-for="repo in filteredDeliveries"
              :key="repo.id"
              class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
            >
              <div class="flex items-center gap-2">
                <img
                  v-if="repo.student.avatar_url && !avatarHasFailed(repo.student.id)"
                  :src="repo.student.avatar_url"
                  :alt="repo.student.full_name"
                  class="h-8 w-8 rounded-full object-cover"
                  @error="handleAvatarError(repo.student.id)"
                />
                <div
                  v-else
                  class="flex h-8 w-8 items-center justify-center rounded-full bg-slate-200 text-xs font-bold text-slate-600"
                >
                  {{ repo.student.full_name.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <p class="text-sm font-bold text-slate-950">{{ repo.student.full_name }}</p>
                  <p class="text-xs text-slate-500">{{ repo.student.email }}</p>
                </div>
              </div>
              <div class="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                <span class="font-medium text-emerald-700">{{ repo.project_name }}</span>
                <span class="font-mono">{{ repo.repo_url.length > 25 ? repo.repo_url.substring(0, 25) + '...' : repo.repo_url }}</span>
              </div>
              <div class="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                <span>Rama: {{ repo.branch }}</span>
                <span v-if="repo.last_commit_hash">Commit: {{ repo.last_commit_hash.substring(0, 7) }}</span>
                <span
                  class="rounded-full px-2 py-0.5 text-[10px] font-bold"
                  :class="getStatusClasses(repo.status)"
                >
                  {{ getStatusLabel(repo.status) }}
                </span>
              </div>
              <div class="mt-3 flex flex-wrap gap-1">
                <RouterLink
                  :to="`/projects/${repo.project_id}`"
                  class="rounded-md bg-emerald-50 px-2 py-1 text-[11px] font-bold text-emerald-700"
                >
                  Ver proyecto
                </RouterLink>
                <button
                  class="rounded-md bg-slate-100 px-2 py-1 text-[11px] font-bold text-slate-600 disabled:opacity-50"
                  type="button"
                  :disabled="analyzingRepoId === repo.id || repo.status === 'ANALYZING'"
                  @click="handleAnalyze(repo)"
                >
                  {{ analyzingRepoId === repo.id || repo.status === 'ANALYZING' ? 'Analizando...' : 'Análisis técnico' }}
                </button>
                <button
                  class="rounded-md bg-blue-50 px-2 py-1 text-[11px] font-bold text-blue-600 disabled:opacity-50"
                  type="button"
                  :disabled="aiAnalyzingRepoId === repo.id || aiLoadingLatestRepoId === repo.id"
                  @click="handleAiAnalysis(repo)"
                >
                  {{ aiAnalyzingRepoId === repo.id ? 'Analizando IA...' : 'Análisis IA' }}
                </button>
                <button
                  class="rounded-md bg-blue-50 px-2 py-1 text-[11px] font-bold text-blue-500 disabled:opacity-50"
                  type="button"
                  :disabled="aiAnalyzingRepoId === repo.id || aiLoadingLatestRepoId === repo.id"
                  @click="handleLatestAiAnalysis(repo)"
                >
                  Ver último IA
                </button>
                <button
                  class="rounded-md bg-red-50 px-2 py-1 text-[11px] font-bold text-red-500 disabled:opacity-50"
                  type="button"
                  :disabled="deletingRepoId === repo.id"
                  @click="handleDeleteRepository(repo)"
                >
                  {{ deletingRepoId === repo.id ? 'Eliminando...' : 'Eliminar' }}
                </button>
              </div>
            </article>
          </div>
        </section>

        <section v-else-if="!loadError && !loading" class="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center shadow-sm shadow-slate-900/5">
          <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
            <Icon name="inbox" class="h-6 w-6" />
          </div>
          <h3 class="mt-4 text-lg font-black text-slate-950">Aún no hay entregas</h3>
          <p class="mx-auto mt-2 max-w-md text-sm leading-5 text-slate-500">Cuando tus alumnos vinculen repositorios aparecerán aquí.</p>
          <RouterLink to="/projects" class="mt-5 inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-emerald-700">
            Ver proyectos
          </RouterLink>
        </section>

        <div v-if="analysisResult || analysisError" class="mt-5 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <h3 class="text-base font-bold text-slate-950 mb-3">Resultado del análisis técnico</h3>
          <p v-if="analysisError" class="text-sm text-red-700">{{ analysisError }}</p>
          <div v-if="analysisResult" class="grid gap-3 text-sm">
            <div class="flex flex-wrap gap-x-4 gap-y-1 text-slate-600">
              <span><strong>Estado:</strong> {{ analysisResult.status }}</span>
              <span v-if="analysisResult.commit_hash"><strong>Commit:</strong> {{ analysisResult.commit_hash.substring(0, 7) }}</span>
              <span v-if="analysisResult.started_at"><strong>Iniciado:</strong> {{ formatDate(analysisResult.started_at) }}</span>
              <span v-if="analysisResult.finished_at"><strong>Finalizado:</strong> {{ formatDate(analysisResult.finished_at) }}</span>
            </div>
            <p v-if="analysisResult.error_message" class="text-sm text-red-700"><strong>Error:</strong> {{ analysisResult.error_message }}</p>
            <pre v-if="analysisResult.result_json" class="mt-2 rounded-lg bg-slate-900 p-4 text-xs text-slate-300 overflow-x-auto">{{ JSON.stringify(analysisResult.result_json, null, 2) }}</pre>
          </div>
        </div>

        <div v-if="aiAnalysisRun || aiAnalysisResult || aiAnalysisError" class="mt-5">
          <p v-if="aiAnalysisError" class="mb-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{{ aiAnalysisError }}</p>
          <AiAnalysisResult
            v-if="aiAnalysisRun || aiAnalysisResult"
            :result="aiAnalysisResult"
            :status="aiAnalysisRun?.status"
            :created-at="aiAnalysisRun?.created_at"
            :finished-at="aiAnalysisRun?.finished_at"
          />
        </div>
      </div>
    </section>
  </main>
</template>