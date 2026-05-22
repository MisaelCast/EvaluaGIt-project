<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import type { User } from '@supabase/supabase-js'
import AiAnalysisResult from '@/components/AiAnalysisResult.vue'
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
import { getProject, type ProjectResponse } from '@/services/projects'
import {
  analyzeProjectSimilarity,
  getLatestSimilarityAnalysis,
  type SimilarityRunResponse,
} from '@/services/similarity'
import { getCurrentUser, signOut } from '@/services/auth'

const route = useRoute()
const router = useRouter()
const projectId = route.params.projectId as string

type IconName =
  | 'bar-chart'
  | 'bell'
  | 'brain'
  | 'chevron-right'
  | 'code'
  | 'copy'
  | 'folder'
  | 'git-compare'
  | 'home'
  | 'inbox'
  | 'key'
  | 'search'
  | 'settings'
  | 'trash'
  | 'upload-cloud'
  | 'users'

const iconPaths: Record<IconName, string[]> = {
  'bar-chart': ['M3 3v18h18', 'M7 15v2', 'M12 10v7', 'M17 6v11'],
  bell: ['M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9', 'M13.73 21a2 2 0 0 1-3.46 0'],
  brain: ['M9 3a3 3 0 0 0-3 3v1a3 3 0 0 0 0 6v1a3 3 0 0 0 3 3', 'M15 3a3 3 0 0 1 3 3v1a3 3 0 0 1 0 6v1a3 3 0 0 1-3 3', 'M9 3v18', 'M15 3v18', 'M9 8h2', 'M13 8h2', 'M9 16h2', 'M13 16h2'],
  'chevron-right': ['M9 18l6-6-6-6'],
  code: ['M16 18l6-6-6-6', 'M8 6l-6 6 6 6'],
  copy: ['M5 3h12a2 2 0 0 1 2 2v12', 'M3 7a2 2 0 0 1 2-2h1', 'M3 7v12a2 2 0 0 0 2 2h12'],
  folder: ['M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z'],
  'git-compare': ['M6 3v12', 'M18 9v12', 'M6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z', 'M18 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z', 'M8.5 7.5h5a4.5 4.5 0 0 1 4.5 4.5', 'M15.5 16.5h-5A4.5 4.5 0 0 1 6 12'],
  home: ['M3 10.5 12 3l9 7.5', 'M5 10v10h14V10', 'M9 20v-6h6v6'],
  inbox: ['M4 4h16l2 10v6H2v-6Z', 'M2 14h6a4 4 0 0 0 8 0h6'],
  key: ['M15 7a4 4 0 1 0-2.5 3.7L4 19.2V22h3v-2h2v-2h2l3.3-3.3A4 4 0 0 0 15 7Z', 'M18 5h.01'],
  search: ['M21 21l-4.35-4.35', 'M10.5 18a7.5 7.5 0 1 0 0-15 7.5 7.5 0 0 0 0 15Z'],
  settings: ['M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z', 'M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 1.55V21a2 2 0 1 1-4 0v-.05a1.7 1.7 0 0 0-1-1.55 1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.55-1H3a2 2 0 1 1 0-4h.05A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.55V3a2 2 0 1 1 4 0v.05A1.7 1.7 0 0 0 15 4.6a1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.55 1H21a2 2 0 1 1 0 4h-.05A1.7 1.7 0 0 0 19.4 15Z'],
  trash: ['M3 6h18', 'M8 6V4h8v2', 'M19 6l-1 14H6L5 6', 'M10 11v5', 'M14 11v5'],
  'upload-cloud': ['M16 16l-4-4-4 4', 'M12 12v9', 'M20 16.6A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25'],
  users: ['M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2', 'M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75', 'M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z'],
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
const project = ref<ProjectResponse | null>(null)
const repositories = ref<RepositoryWithStudent[]>([])
const repositoriesLoading = ref(false)
const repositoriesError = ref('')

const analyzingRepositoryId = ref<string | null>(null)
const analysisResult = ref<AnalysisRunResponse | null>(null)
const analysisError = ref('')
const aiAnalysisRun = ref<AiAnalysisRunResponse | null>(null)
const aiAnalysisResult = ref<AiAnalysisResponse | null>(null)
const aiAnalysisError = ref('')
const aiAnalyzingRepositoryId = ref<string | null>(null)
const aiLoadingLatestRepositoryId = ref<string | null>(null)
const similarityRun = ref<SimilarityRunResponse | null>(null)
const similarityError = ref('')
const analyzingSimilarity = ref(false)
const loadingLatestSimilarity = ref(false)
const failedAvatars = ref<Set<string>>(new Set())
const activeTab = ref('entregas')
const copiedCode = ref(false)
const showSimilarityDetails = ref(false)

const similarityResult = computed(() => similarityRun.value?.result_json ?? null)

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

const analyzedCount = computed(() =>
  repositories.value.filter((r) => r.status === 'ANALYZED' || r.last_analyzed_at).length,
)

const pendingCount = computed(() =>
  repositories.value.filter((r) => r.status !== 'ANALYZED' && !r.last_analyzed_at).length,
)

const relevantSimilarityCount = computed(() => {
  const pairs = similarityResult.value?.pairs
  if (!pairs) return null
  return pairs.filter((p) => p.level === 'relevant' || p.level === 'high').length
})

const summaryCards = computed(() => [
  { title: 'Entregas recibidas', value: repositories.value.length, icon: 'inbox' as IconName, tone: 'emerald' },
  { title: 'Analizadas', value: analyzedCount.value, icon: 'code' as IconName, tone: 'emerald' },
  { title: 'Pendientes', value: pendingCount.value, icon: 'folder' as IconName, tone: 'emerald' },
  { title: 'Similitudes relevantes', value: relevantSimilarityCount.value, icon: 'git-compare' as IconName, tone: 'emerald' },
])

const tabs = [
  { key: 'resumen', label: 'Resumen', icon: 'home' as IconName },
  { key: 'entregas', label: 'Entregas', icon: 'inbox' as IconName },
  { key: 'ai', label: 'Análisis IA', icon: 'brain' as IconName },
  { key: 'similitud', label: 'Similitud', icon: 'git-compare' as IconName },
]

function handleAvatarError(studentId: string) {
  failedAvatars.value.add(studentId)
}

function avatarHasFailed(studentId: string): boolean {
  return failedAvatars.value.has(studentId)
}

onMounted(() => {
  void loadUser()
  void loadProject()
  void loadRepositories()
})

async function loadUser() {
  try {
    user.value = await getCurrentUser()
  } catch {
    user.value = null
  }
}

async function loadProject() {
  try {
    project.value = await getProject(projectId)
  } catch {
    project.value = null
  }
}

async function loadRepositories() {
  repositoriesLoading.value = true
  repositoriesError.value = ''

  try {
    repositories.value = await getProjectRepositories(projectId)
  } catch (err) {
    repositories.value = []
    repositoriesError.value =
      err instanceof Error ? err.message : 'No se pudieron cargar las entregas'
  } finally {
    repositoriesLoading.value = false
  }
}

async function handleDeleteRepository(repo: RepositoryWithStudent) {
  const confirmed = window.confirm(
    `¿Eliminar el repositorio ${repo.repo_url}?`,
  )
  if (!confirmed) return

  repositoriesError.value = ''

  try {
    await deleteRepository(repo.id)
    analysisResult.value = null
    analysisError.value = ''
    aiAnalysisRun.value = null
    aiAnalysisResult.value = null
    aiAnalysisError.value = ''
    similarityRun.value = null
    similarityError.value = ''
    await loadRepositories()
  } catch (err) {
    repositoriesError.value =
      err instanceof Error ? err.message : 'No se pudo eliminar el repositorio'
  }
}

async function handleAnalyze(repo: RepositoryWithStudent) {
  analyzingRepositoryId.value = repo.id
  analysisError.value = ''
  analysisResult.value = null

  try {
    const result = await analyzeRepository(repo.id)
    analysisResult.value = result
    await loadRepositories()
  } catch (err) {
    analysisError.value =
      err instanceof Error ? err.message : 'No se pudo analizar el repositorio'
  } finally {
    analyzingRepositoryId.value = null
  }
}

async function handleAiAnalysis(repo: RepositoryWithStudent) {
  aiAnalyzingRepositoryId.value = repo.id
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
    aiAnalyzingRepositoryId.value = null
  }
}

async function handleLatestAiAnalysis(repo: RepositoryWithStudent) {
  aiLoadingLatestRepositoryId.value = repo.id
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
    aiLoadingLatestRepositoryId.value = null
  }
}

async function handleSimilarityAnalysis() {
  if (!project.value) return

  analyzingSimilarity.value = true
  similarityError.value = ''
  similarityRun.value = null

  try {
    similarityRun.value = await analyzeProjectSimilarity(project.value.id)
    activeTab.value = 'similitud'
  } catch (err) {
    similarityError.value =
      err instanceof Error ? err.message : 'No se pudo analizar la similitud'
  } finally {
    analyzingSimilarity.value = false
  }
}

async function handleLatestSimilarityAnalysis() {
  if (!project.value) return

  loadingLatestSimilarity.value = true
  similarityError.value = ''
  similarityRun.value = null

  try {
    similarityRun.value = await getLatestSimilarityAnalysis(project.value.id)
    activeTab.value = 'similitud'
  } catch (err) {
    const message = err instanceof Error ? err.message : 'No se pudo cargar el análisis de similitud'
    similarityError.value =
      message === 'No hay analisis de similitud para este proyecto'
        ? 'Este proyecto aún no tiene análisis de similitud guardado'
        : message
  } finally {
    loadingLatestSimilarity.value = false
  }
}

async function handleCopyCode() {
  if (!project.value?.join_code) return
  try {
    await navigator.clipboard.writeText(project.value.join_code)
    copiedCode.value = true
    setTimeout(() => { copiedCode.value = false }, 2000)
  } catch {
    // ignore
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

function formatSimilarityStatus(value: string): string {
  switch (value) {
    case 'COMPLETED': return 'Completado'
    case 'RUNNING': return 'En proceso'
    case 'PENDING': return 'Pendiente'
    case 'READY': return 'Listo'
    case 'FAILED': return 'Fallido'
    default: return value || 'No disponible'
  }
}

function formatSimilarityProvider(value: string): string {
  return value === 'dolos' ? 'Dolos' : value || 'No disponible'
}

function getSummaryNumber(key: string): number | null {
  const value = similarityResult.value?.summary?.[key]
  return typeof value === 'number' ? value : null
}

function getSimilarityLevelClasses(level: string): string {
  switch (level) {
    case 'high':
      return 'border-red-200 bg-red-50 text-red-700'
    case 'relevant':
      return 'border-orange-200 bg-orange-50 text-orange-700'
    case 'review':
      return 'border-amber-200 bg-amber-50 text-amber-800'
    default:
      return 'border-slate-200 bg-slate-100 text-slate-700'
  }
}

function hasRelevantSimilarityPairs(): boolean {
  return Boolean(
    similarityResult.value?.pairs.some((pair) => pair.level === 'relevant' || pair.level === 'high'),
  )
}

const filteredSimilarityPairs = computed(() => {
  const pairs = similarityResult.value?.pairs
  if (!pairs) return []
  return pairs.filter((p) => p.level === 'review' || p.level === 'relevant' || p.level === 'high')
})

const similarityInterpretation = computed(() => {
  const s = similarityResult.value?.summary
  if (!s) return null
  const high = typeof s.high_pairs_count === 'number' ? s.high_pairs_count : 0
  const relevant = typeof s.relevant_pairs_count === 'number' ? s.relevant_pairs_count : 0
  const review = typeof s.review_pairs_count === 'number' ? s.review_pairs_count : 0

  if (high > 0) return { text: 'Se encontraron similitudes altas que conviene revisar manualmente.', tone: 'red' }
  if (relevant > 0) return { text: 'Se encontraron similitudes relevantes entre entregas.', tone: 'orange' }
  if (review > 0) return { text: 'Hay coincidencias moderadas. Revisar solo si existe contexto adicional.', tone: 'amber' }
  if (similarityResult.value?.executed) return { text: 'Dolos se ejecutó correctamente pero no se encontraron similitudes relevantes entre entregas diferentes.', tone: 'slate' }
  return null
})

function getPairLevelLabel(level: string): string {
  switch (level) {
    case 'high': return 'Similitud alta o muy sospechosa'
    case 'relevant': return 'Similitud relevante'
    case 'review': return 'Revisar solo si hay contexto'
    case 'normal': return 'Coincidencia normal o irrelevante'
    default: return level || 'No disponible'
  }
}

function getPairLevelBadgeClasses(level: string): string {
  switch (level) {
    case 'high':
      return 'bg-red-50 text-red-700'
    case 'relevant':
      return 'bg-orange-50 text-orange-700'
    case 'review':
      return 'bg-amber-50 text-amber-800'
    default:
      return 'bg-slate-100 text-slate-600'
  }
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
        <p v-if="repositoriesError" class="mb-6 rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">{{ repositoriesError }}</p>

        <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-2xl font-black text-slate-950">Detalle del proyecto</h1>
            <p v-if="project" class="mt-1 text-base font-semibold text-slate-600">{{ project.name }}</p>
            <p v-if="project?.description" class="mt-1.5 text-sm text-slate-500">{{ project.description }}</p>
          </div>
          <div class="flex items-center gap-2.5">
            <RouterLink to="/projects" class="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold text-slate-700 transition hover:bg-slate-50 shadow-sm">
              <Icon name="chevron-right" class="h-4 w-4 rotate-180" />
              Volver a proyectos
            </RouterLink>
            <RouterLink :to="`/projects/${projectId}/settings`" class="inline-flex items-center gap-1.5 rounded-xl bg-emerald-600 px-3 py-2 text-sm font-bold text-white transition hover:bg-emerald-700 shadow-sm shadow-emerald-900/15">
              <Icon name="settings" class="h-4 w-4" />
              Configurar
            </RouterLink>
          </div>
        </div>

        <section v-if="project" class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-900/5">
          <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div class="flex items-center gap-2.5">
                <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
                  <Icon name="key" class="h-4 w-4" />
                </span>
                <span class="text-sm font-semibold text-slate-600">Código para alumnos</span>
              </div>
              <div class="mt-2 flex items-center gap-2">
                <code class="rounded-lg bg-emerald-50 px-3 py-1.5 font-mono text-lg font-black text-emerald-700">{{ project.join_code }}</code>
                <button
                  type="button"
                  class="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-bold text-slate-600 transition hover:bg-slate-50"
                  @click="handleCopyCode"
                >
                  <Icon :name="copiedCode ? 'copy' : 'copy'" class="h-3.5 w-3.5" />
                  {{ copiedCode ? 'Copiado' : 'Copiar' }}
                </button>
              </div>
              <p class="mt-2 text-xs text-slate-500">Comparte este código con tus alumnos para que se unan al proyecto.</p>
            </div>
          </div>
        </section>

        <section class="mb-6 grid gap-4 lg:grid-cols-4">
          <article
            v-for="card in summaryCards"
            :key="card.title"
            class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-900/5"
          >
            <div class="flex items-start gap-3">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-lg"
                :class="card.tone === 'red' ? 'bg-red-50 text-red-600' : 'bg-emerald-50 text-emerald-700'"
              >
                <Icon :name="card.icon" class="h-5 w-5" />
              </div>
              <div>
                <p class="text-xs font-medium text-slate-600">{{ card.title }}</p>
                <p class="mt-0.5 text-xl font-black text-slate-950">
                  {{ card.value !== null ? card.value : 'No disponible' }}
                </p>
              </div>
            </div>
          </article>
        </section>

        <nav class="mb-6 flex gap-1 overflow-x-auto rounded-xl border border-slate-200 bg-white p-1 shadow-sm shadow-slate-900/5">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            type="button"
            class="flex min-w-fit items-center gap-1.5 rounded-lg px-4 py-2.5 text-sm font-semibold transition"
            :class="activeTab === tab.key ? 'bg-emerald-50 text-emerald-700' : 'text-slate-600 hover:bg-slate-50'"
            @click="activeTab = tab.key"
          >
            <Icon :name="tab.icon" class="h-4 w-4" />
            {{ tab.label }}
          </button>
        </nav>

        <section v-if="activeTab === 'resumen'" class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-900/5 space-y-6">
          <div>
            <h2 class="text-lg font-black text-slate-950">Información del proyecto</h2>
            <p class="mt-1 text-sm text-slate-500">Resumen general y flujo de trabajo del proyecto.</p>
            <div class="mt-4 grid gap-4 text-sm sm:grid-cols-2">
              <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase text-slate-500">Nombre</p>
                <p class="mt-1 font-bold text-slate-950">{{ project?.name || 'No disponible' }}</p>
              </div>
              <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase text-slate-500">Descripción</p>
                <p class="mt-1 font-bold text-slate-950">{{ project?.description || 'Sin descripción' }}</p>
              </div>
              <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase text-slate-500">Código de acceso</p>
                <p class="mt-1 font-mono font-bold text-emerald-700">{{ project?.join_code || 'No disponible' }}</p>
              </div>
              <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase text-slate-500">Fecha de creación</p>
                <p class="mt-1 font-bold text-slate-950">{{ formatDate(project?.created_at ?? null) }}</p>
              </div>
            </div>
          </div>

          <div>
            <h2 class="text-lg font-black text-slate-950">Flujo de trabajo</h2>
            <div class="mt-4 grid gap-3 rounded-lg border border-slate-200 bg-slate-50 p-5 text-sm text-slate-600">
              <p class="flex items-center gap-2"><span class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-700">1</span> Comparte el código de acceso con tus alumnos.</p>
              <p class="flex items-center gap-2"><span class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-700">2</span> Los alumnos vinculan su repositorio al proyecto.</p>
              <p class="flex items-center gap-2"><span class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-700">3</span> Revisa las entregas en la pestaña Entregas.</p>
              <p class="flex items-center gap-2"><span class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-700">4</span> Ejecuta análisis técnico e IA sobre cada entrega.</p>
              <p class="flex items-center gap-2"><span class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-700">5</span> Compara similitud entre entregas en la pestaña Similitud.</p>
            </div>
          </div>
        </section>

        <section v-if="activeTab === 'entregas'" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-900/5">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-black text-slate-950">Entregas del proyecto</h2>
            <p class="text-sm text-slate-500">{{ repositories.length }} entregas recibidas</p>
          </div>

          <div v-if="repositoriesLoading" class="py-8 text-center text-sm text-slate-500">
            Cargando entregas...
          </div>

          <div v-else-if="repositories.length" class="grid gap-3">
            <article
              v-for="repo in repositories"
              :key="repo.id"
              class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
            >
              <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div class="min-w-0 flex-1">
                  <div class="flex items-center gap-3">
                    <img
                      v-if="repo.student.avatar_url && !avatarHasFailed(repo.student.id)"
                      :src="repo.student.avatar_url"
                      :alt="repo.student.full_name"
                      class="h-9 w-9 rounded-full object-cover"
                      @error="handleAvatarError(repo.student.id)"
                    />
                    <div
                      v-else
                      class="flex h-9 w-9 items-center justify-center rounded-full bg-slate-200 text-xs font-bold text-slate-600"
                    >
                      {{ repo.student.full_name.charAt(0).toUpperCase() }}
                    </div>
                    <div>
                      <p class="text-sm font-bold text-slate-950">{{ repo.student.full_name }}</p>
                      <p class="text-xs text-slate-500">{{ repo.student.email }}</p>
                    </div>
                  </div>

                  <div class="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
                    <span class="font-mono font-medium text-slate-700">{{ repo.repo_url }}</span>
                    <span>Rama: <span class="font-medium text-slate-700">{{ repo.branch }}</span></span>
                    <span v-if="repo.last_commit_hash">
                      Commit: <span class="font-mono font-medium text-slate-700">{{ repo.last_commit_hash.substring(0, 7) }}</span>
                    </span>
                    <span v-if="repo.last_analyzed_at">
                      Último análisis: {{ formatDate(repo.last_analyzed_at) }}
                    </span>
                  </div>
                </div>

                <div class="flex flex-col items-start gap-1.5 sm:items-end">
                  <span
                    class="inline-flex rounded-full px-2.5 py-0.5 text-[10px] font-bold"
                    :class="getStatusClasses(repo.status)"
                  >
                    {{ getStatusLabel(repo.status) }}
                  </span>
                </div>
              </div>

              <div class="mt-4 flex flex-wrap gap-2">
                <button
                  class="inline-flex items-center justify-center rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-bold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
                  type="button"
                  :disabled="analyzingRepositoryId === repo.id || repo.status === 'ANALYZING'"
                  @click="handleAnalyze(repo)"
                >
                  {{ analyzingRepositoryId === repo.id || repo.status === 'ANALYZING' ? 'Analizando...' : 'Análisis técnico' }}
                </button>
                <button
                  class="inline-flex items-center justify-center rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                  type="button"
                  :disabled="aiAnalyzingRepositoryId === repo.id || aiLoadingLatestRepositoryId === repo.id"
                  @click="handleAiAnalysis(repo)"
                >
                  {{ aiAnalyzingRepositoryId === repo.id ? 'Analizando con IA...' : 'Análisis IA' }}
                </button>
                <button
                  class="inline-flex items-center justify-center rounded-lg bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-700 transition hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-60"
                  type="button"
                  :disabled="aiAnalyzingRepositoryId === repo.id || aiLoadingLatestRepositoryId === repo.id"
                  @click="handleLatestAiAnalysis(repo)"
                >
                  {{ aiLoadingLatestRepositoryId === repo.id ? 'Cargando IA...' : 'Ver último IA' }}
                </button>
                <button
                  class="inline-flex items-center justify-center rounded-lg bg-red-50 px-3 py-1.5 text-xs font-bold text-red-600 transition hover:bg-red-100"
                  type="button"
                  @click="handleDeleteRepository(repo)"
                >
                  <Icon name="trash" class="mr-1 h-3 w-3" />
                  Eliminar
                </button>
              </div>
            </article>
          </div>

          <div v-else-if="!repositoriesError" class="rounded-xl border border-dashed border-slate-300 bg-slate-50/50 p-8 text-center">
            <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
              <Icon name="inbox" class="h-6 w-6" />
            </div>
            <h3 class="mt-4 text-lg font-black text-slate-950">Aún no hay entregas</h3>
            <p class="mx-auto mt-2 max-w-md text-sm leading-5 text-slate-500">Este proyecto aún no tiene entregas de alumnos.</p>
          </div>

          <div v-if="analysisResult || analysisError" class="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4">
            <h3 class="text-base font-bold text-slate-950">Resultado del análisis técnico</h3>
            <p v-if="analysisError" class="mt-2 text-sm text-red-700">{{ analysisError }}</p>
            <div v-if="analysisResult" class="mt-3 grid gap-3 text-sm">
              <div class="flex flex-wrap gap-x-4 gap-y-1 text-slate-600">
                <span><strong>Estado:</strong> {{ analysisResult.status }}</span>
                <span v-if="analysisResult.commit_hash"><strong>Commit:</strong> {{ analysisResult.commit_hash.substring(0, 7) }}</span>
                <span v-if="analysisResult.started_at"><strong>Iniciado:</strong> {{ formatDate(analysisResult.started_at) }}</span>
                <span v-if="analysisResult.finished_at"><strong>Finalizado:</strong> {{ formatDate(analysisResult.finished_at) }}</span>
              </div>
              <p v-if="analysisResult.error_message" class="text-sm text-red-700"><strong>Error:</strong> {{ analysisResult.error_message }}</p>
              <RouterLink v-if="analysisResult.id" :to="`/projects/${projectId}/analysis/${analysisResult.id}`" class="inline-flex w-fit items-center rounded-lg bg-slate-200 px-3 py-1.5 text-xs font-bold text-slate-700 transition hover:bg-slate-300">
                Ver análisis completo
              </RouterLink>
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
        </section>

        <section v-if="activeTab === 'ai'" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-900/5">
          <div class="mb-4">
            <h2 class="text-lg font-black text-slate-950">Análisis con inteligencia artificial</h2>
            <p class="mt-1 text-sm text-slate-500">Selecciona una entrega y ejecuta un análisis IA para obtener retroalimentación automatizada.</p>
          </div>

          <div v-if="repositoriesLoading" class="py-8 text-center text-sm text-slate-500">
            Cargando entregas...
          </div>

          <div v-else-if="repositories.length" class="grid gap-3">
            <article
              v-for="repo in repositories"
              :key="repo.id"
              class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
            >
              <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div class="flex items-center gap-3">
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
                    <p class="text-xs text-slate-500">{{ repo.repo_url }}</p>
                  </div>
                </div>
                <div class="flex gap-2">
                  <button
                    class="rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                    type="button"
                    :disabled="aiAnalyzingRepositoryId === repo.id || aiLoadingLatestRepositoryId === repo.id"
                    @click="handleAiAnalysis(repo)"
                  >
                    {{ aiAnalyzingRepositoryId === repo.id ? 'Analizando con IA...' : 'Analizar con IA' }}
                  </button>
                  <button
                    class="rounded-lg bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-700 transition hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-60"
                    type="button"
                    :disabled="aiAnalyzingRepositoryId === repo.id || aiLoadingLatestRepositoryId === repo.id"
                    @click="handleLatestAiAnalysis(repo)"
                  >
                    {{ aiLoadingLatestRepositoryId === repo.id ? 'Cargando...' : 'Ver último IA' }}
                  </button>
                </div>
              </div>
            </article>
          </div>

          <div v-else-if="!repositoriesError" class="rounded-xl border border-dashed border-slate-300 bg-slate-50/50 p-8 text-center">
            <p class="text-sm text-slate-500">No hay entregas para analizar con IA.</p>
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

          <div v-if="!aiAnalysisRun && !aiAnalysisResult && !aiAnalysisError && repositories.length" class="rounded-xl border border-dashed border-slate-300 bg-slate-50/50 p-6 text-center">
            <p class="text-sm text-slate-500">Selecciona una entrega y ejecuta un análisis IA para ver la retroalimentación.</p>
          </div>
        </section>

        <section v-if="activeTab === 'similitud'" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-900/5">
          <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 class="text-lg font-black text-slate-950">Análisis de similitud</h2>
              <p class="mt-1 text-sm text-slate-500">Compara entregas entre alumnos y detecta coincidencias relevantes.</p>
            </div>
            <div class="flex gap-2">
              <button
                class="rounded-lg bg-emerald-600 px-3 py-2 text-xs font-bold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
                type="button"
                :disabled="analyzingSimilarity || loadingLatestSimilarity || repositories.length < 2"
                @click="handleSimilarityAnalysis"
              >
                {{ analyzingSimilarity ? 'Analizando...' : 'Analizar similitud' }}
              </button>
              <button
                class="rounded-lg bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700 transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
                type="button"
                :disabled="analyzingSimilarity || loadingLatestSimilarity"
                @click="handleLatestSimilarityAnalysis"
              >
                {{ loadingLatestSimilarity ? 'Cargando...' : 'Ver último análisis' }}
              </button>
            </div>
          </div>

          <p v-if="repositories.length < 2" class="mb-4 text-sm text-slate-500">
            Se necesitan al menos 2 entregas para analizar similitud.
          </p>

          <p v-if="similarityError" class="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {{ similarityError }}
          </p>

          <p v-if="similarityRun?.error_message" class="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {{ similarityRun.error_message }}
          </p>

          <div v-if="!similarityRun && !similarityResult && !similarityError" class="rounded-xl border border-dashed border-slate-300 bg-slate-50/50 p-8 text-center">
            <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
              <Icon name="git-compare" class="h-6 w-6" />
            </div>
            <h3 class="mt-4 text-base font-bold text-slate-950">Sin análisis de similitud</h3>
            <p class="mx-auto mt-2 max-w-md text-sm leading-5 text-slate-500">Ejecuta un análisis de similitud para comparar las entregas de tus alumnos.</p>
          </div>

          <div v-if="similarityRun && similarityResult" class="space-y-4">
            <p class="text-xs text-slate-500">
              Último análisis: {{ formatSimilarityStatus(similarityRun.status) }} · {{ formatDate(similarityRun.finished_at || similarityRun.created_at) }}
            </p>

            <p v-if="!similarityResult.executed" class="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm font-medium text-amber-800">
              Dolos todavía no se ha ejecutado en este paso.
            </p>

            <div v-if="similarityResult.summary" class="grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
              <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase text-slate-500">Entregas comparadas</p>
                <p class="mt-1 font-semibold text-slate-950">{{ similarityResult.repositories_count || getSummaryNumber('total_pairs_between_submissions') }}</p>
              </div>
              <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase text-slate-500">Pares para revisar</p>
                <p class="mt-1 font-semibold text-slate-950">{{ getSummaryNumber('review_pairs_count') ?? 0 }}</p>
              </div>
              <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase text-slate-500">Similitudes relevantes</p>
                <p class="mt-1 font-semibold text-slate-950">{{ getSummaryNumber('relevant_pairs_count') ?? 0 }}</p>
              </div>
              <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase text-slate-500">Similitudes altas</p>
                <p class="mt-1 font-semibold text-slate-950">{{ getSummaryNumber('high_pairs_count') ?? 0 }}</p>
              </div>
            </div>

            <div
              v-if="similarityInterpretation"
              class="rounded-lg border p-3 text-sm font-medium"
              :class="{
                'border-red-200 bg-red-50 text-red-800': similarityInterpretation.tone === 'red',
                'border-orange-200 bg-orange-50 text-orange-800': similarityInterpretation.tone === 'orange',
                'border-amber-200 bg-amber-50 text-amber-800': similarityInterpretation.tone === 'amber',
                'border-slate-200 bg-slate-50 text-slate-600': similarityInterpretation.tone === 'slate',
              }"
            >
              {{ similarityInterpretation.text }}
            </div>

            <div v-if="filteredSimilarityPairs.length">
              <h4 class="text-sm font-semibold text-slate-950">Pares principales para revisar</h4>
              <div class="mt-3 grid gap-3">
                <article
                  v-for="(pair, index) in filteredSimilarityPairs"
                  :key="`${pair.left_repository_id}-${pair.right_repository_id}-${pair.left_file}-${pair.right_file}-${index}`"
                  class="rounded-lg border border-slate-200 bg-slate-50 p-4"
                >
                  <p class="text-sm font-semibold text-slate-950">
                    {{ pair.left_student_name || 'Alumno A' }} vs {{ pair.right_student_name || 'Alumno B' }}
                  </p>
                  <p class="mt-2 text-sm font-semibold text-slate-700">
                    Similitud:
                    {{ pair.similarity_percent !== null ? `${pair.similarity_percent}%` : 'No disponible' }}
                  </p>
                  <span
                    class="mt-3 inline-flex w-fit rounded-full px-3 py-1 text-xs font-semibold"
                    :class="getPairLevelBadgeClasses(pair.level)"
                  >
                    {{ getPairLevelLabel(pair.level) }}
                  </span>
                  <div class="mt-3 grid gap-3 text-sm md:grid-cols-2">
                    <p class="break-all font-mono text-xs text-slate-700">{{ pair.left_file || 'No disponible' }}</p>
                    <p class="break-all font-mono text-xs text-slate-700">{{ pair.right_file || 'No disponible' }}</p>
                  </div>
                </article>
              </div>
            </div>

            <p v-else-if="similarityResult.executed" class="rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
              No se encontraron coincidencias que requieran revisión entre entregas diferentes.
            </p>

            <div v-if="similarityResult.output_files?.length" class="border-t border-slate-200 pt-4">
              <button
                type="button"
                class="flex items-center gap-1 text-xs font-semibold text-slate-500 transition hover:text-slate-700"
                @click="showSimilarityDetails = !showSimilarityDetails"
              >
                Detalles técnicos
                <svg
                  class="h-3 w-3 transition-transform"
                  :class="{ 'rotate-180': showSimilarityDetails }"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M6 9l6 6 6-6" />
                </svg>
              </button>
              <div v-if="showSimilarityDetails" class="mt-3 grid gap-3">
                <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <p class="text-xs font-semibold uppercase text-slate-500">Archivos generados por Dolos</p>
                  <ul class="mt-2 grid gap-1 text-xs text-slate-600">
                    <li v-for="file in similarityResult.output_files" :key="file" class="break-all font-mono">{{ file }}</li>
                  </ul>
                </div>
                <div v-if="similarityResult.summary" class="grid gap-3 text-sm sm:grid-cols-3">
                  <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <p class="text-xs font-semibold uppercase text-slate-500">Pares internos</p>
                    <p class="mt-1 font-semibold text-slate-950">{{ getSummaryNumber('total_pairs_raw') ?? 'No disponible' }}</p>
                  </div>
                  <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <p class="text-xs font-semibold uppercase text-slate-500">Proveedor</p>
                    <p class="mt-1 font-semibold text-slate-950">{{ formatSimilarityProvider(similarityResult.provider) }}</p>
                  </div>
                  <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <p class="text-xs font-semibold uppercase text-slate-500">Ejecución</p>
                    <p class="mt-1 font-semibold text-slate-950">{{ similarityResult.executed ? 'Ejecutado' : 'Pendiente' }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </section>
  </main>
</template>
