<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import type { User } from '@supabase/supabase-js'

import { analyzeRepository } from '@/services/analysis'
import { analyzeRepositoryWithAi, getLatestAiAnalysis } from '@/services/aiAnalysis'
import { getCurrentUser, signOut } from '@/services/auth'
import { getProjects, type ProjectResponse } from '@/services/projects'
import {
  deleteRepository,
  getProjectRepositories,
  type RepositoryWithStudent,
} from '@/services/repositories'

const router = useRouter()

type IconName =
  | 'bar-chart'
  | 'bell'
  | 'brain'
  | 'chevron-right'
  | 'code'
  | 'external-link'
  | 'eye'
  | 'folder'
  | 'home'
  | 'inbox'
  | 'play'
  | 'search'
  | 'settings'
  | 'sparkles'
  | 'trash'
  | 'upload-cloud'

const iconPaths: Record<IconName, string[]> = {
  'bar-chart': ['M3 3v18h18', 'M7 15v2', 'M12 10v7', 'M17 6v11'],
  bell: ['M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9', 'M13.73 21a2 2 0 0 1-3.46 0'],
  brain: ['M9 3a3 3 0 0 0-3 3v1a3 3 0 0 0 0 6v1a3 3 0 0 0 3 3', 'M15 3a3 3 0 0 1 3 3v1a3 3 0 0 1 0 6v1a3 3 0 0 1-3 3', 'M9 3v18', 'M15 3v18', 'M9 8h2', 'M13 8h2', 'M9 16h2', 'M13 16h2'],
  'chevron-right': ['M9 18l6-6-6-6'],
  code: ['M16 18l6-6-6-6', 'M8 6l-6 6 6 6'],
  'external-link': ['M15 3h6v6', 'M10 14 21 3', 'M21 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5'],
  eye: ['M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z', 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z'],
  folder: ['M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z'],
  home: ['M3 10.5 12 3l9 7.5', 'M5 10v10h14V10', 'M9 20v-6h6v6'],
  inbox: ['M4 4h16l2 10v6H2v-6Z', 'M2 14h6a4 4 0 0 0 8 0h6'],
  play: ['M5 3l14 9-14 9Z'],
  search: ['M21 21l-4.35-4.35', 'M10.5 18a7.5 7.5 0 1 0 0-15 7.5 7.5 0 0 0 0 15Z'],
  settings: ['M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z', 'M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 1.55V21a2 2 0 1 1-4 0v-.05a1.7 1.7 0 0 0-1-1.55 1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.55-1H3a2 2 0 1 1 0-4h.05A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.55V3a2 2 0 1 1 4 0v.05A1.7 1.7 0 0 0 15 4.6a1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.55 1H21a2 2 0 1 1 0 4h-.05A1.7 1.7 0 0 0 19.4 15Z'],
  sparkles: ['M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8Z', 'M5 3v4', 'M3 5h4', 'M19 17v4', 'M17 19h4'],
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

type DeliveryItem = RepositoryWithStudent & {
  project_name: string
}

const user = ref<User | null>(null)
const projects = ref<ProjectResponse[]>([])
const deliveries = ref<DeliveryItem[]>([])
const loading = ref(false)
const deliveriesError = ref('')
const actionMessage = ref('')
const searchTerm = ref('')
const selectedProjectId = ref('all')
const selectedStatus = ref('all')
const analyzingTechnicalId = ref<string | null>(null)
const analyzingAiId = ref<string | null>(null)
const loadingLatestAiId = ref<string | null>(null)
const deletingRepositoryId = ref<string | null>(null)

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
  const query = searchTerm.value.trim().toLowerCase()

  return deliveries.value.filter((delivery) => {
    const matchesProject =
      selectedProjectId.value === 'all' || delivery.project_id === selectedProjectId.value
    const matchesStatus =
      selectedStatus.value === 'all' || delivery.status === selectedStatus.value
    const searchable = [
      delivery.student.full_name,
      delivery.student.email,
      delivery.repo_url,
      delivery.branch,
      delivery.project_name,
    ]
      .join(' ')
      .toLowerCase()

    return matchesProject && matchesStatus && (!query || searchable.includes(query))
  })
})

const analyzedDeliveriesCount = computed(() => {
  return deliveries.value.filter((delivery) => delivery.status === 'ANALYZED' || delivery.last_analyzed_at).length
})

const pendingDeliveriesCount = computed(() => {
  return deliveries.value.filter((delivery) => !delivery.last_analyzed_at && delivery.status !== 'ANALYZED').length
})

const projectsWithDeliveriesCount = computed(() => {
  return new Set(deliveries.value.map((delivery) => delivery.project_id)).size
})

const statCards = computed(() => [
  {
    title: 'Entregas recibidas',
    value: deliveries.value.length,
    icon: 'inbox' as IconName,
  },
  {
    title: 'Entregas analizadas',
    value: analyzedDeliveriesCount.value,
    icon: 'code' as IconName,
  },
  {
    title: 'Pendientes de análisis',
    value: pendingDeliveriesCount.value,
    icon: 'bell' as IconName,
  },
  {
    title: 'Proyectos con entregas',
    value: projectsWithDeliveriesCount.value,
    icon: 'folder' as IconName,
  },
])

onMounted(() => {
  void loadDeliveries()
})

async function loadDeliveries() {
  loading.value = true
  deliveriesError.value = ''
  actionMessage.value = ''

  try {
    user.value = await getCurrentUser()
  } catch {
    user.value = null
  }

  try {
    const loadedProjects = await getProjects()
    projects.value = loadedProjects

    const repositoryResults = await Promise.allSettled(
      loadedProjects.map(async (project) => {
        const repositories = await getProjectRepositories(project.id)
        return repositories.map((repository) => ({
          ...repository,
          project_name: project.name,
        }))
      }),
    )

    deliveries.value = repositoryResults.flatMap((result) =>
      result.status === 'fulfilled' ? result.value : [],
    )

    if (repositoryResults.some((result) => result.status === 'rejected')) {
      deliveriesError.value = 'Algunas entregas no se pudieron cargar'
    }
  } catch (err) {
    deliveries.value = []
    deliveriesError.value =
      err instanceof Error ? err.message : 'No se pudieron cargar las entregas'
  } finally {
    loading.value = false
  }
}

async function handleAnalyzeTechnical(delivery: DeliveryItem) {
  analyzingTechnicalId.value = delivery.id
  deliveriesError.value = ''
  actionMessage.value = ''

  try {
    await analyzeRepository(delivery.id)
    actionMessage.value = 'Análisis técnico ejecutado correctamente'
    await loadDeliveries()
  } catch (err) {
    deliveriesError.value =
      err instanceof Error ? err.message : 'No se pudo ejecutar el análisis técnico'
  } finally {
    analyzingTechnicalId.value = null
  }
}

async function handleAnalyzeAi(delivery: DeliveryItem) {
  analyzingAiId.value = delivery.id
  deliveriesError.value = ''
  actionMessage.value = ''

  try {
    await analyzeRepositoryWithAi(delivery.id)
    actionMessage.value = 'Análisis IA ejecutado correctamente'
  } catch (err) {
    deliveriesError.value =
      err instanceof Error ? err.message : 'No se pudo ejecutar el análisis IA'
  } finally {
    analyzingAiId.value = null
  }
}

async function handleLatestAi(delivery: DeliveryItem) {
  loadingLatestAiId.value = delivery.id
  deliveriesError.value = ''
  actionMessage.value = ''

  try {
    const result = await getLatestAiAnalysis(delivery.id)
    actionMessage.value =
      result.status === 'COMPLETED'
        ? `Último análisis IA encontrado para ${delivery.student.full_name}`
        : `Último análisis IA en estado ${formatRunStatus(result.status)}`
  } catch (err) {
    deliveriesError.value =
      err instanceof Error ? err.message : 'No se pudo consultar el último análisis IA'
  } finally {
    loadingLatestAiId.value = null
  }
}

async function handleDeleteDelivery(delivery: DeliveryItem) {
  const confirmed = window.confirm(
    `¿Eliminar la entrega de ${delivery.student.full_name}? Esta acción no se puede deshacer.`,
  )
  if (!confirmed) return

  deletingRepositoryId.value = delivery.id
  deliveriesError.value = ''
  actionMessage.value = ''

  try {
    await deleteRepository(delivery.id)
    actionMessage.value = 'Entrega eliminada correctamente'
    await loadDeliveries()
  } catch (err) {
    deliveriesError.value = err instanceof Error ? err.message : 'No se pudo eliminar la entrega'
  } finally {
    deletingRepositoryId.value = null
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
  if (!value) return 'No disponible'

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function shortCommit(value: string | null): string {
  return value ? value.slice(0, 8) : 'No disponible'
}

function formatRepositoryUrl(value: string): string {
  return value.replace(/^https?:\/\//, '').replace(/^www\./, '')
}

function formatStatus(value: string): string {
  const labels: Record<string, string> = {
    LINKED: 'Vinculado',
    ANALYZED: 'Analizado',
    ANALYZING: 'Analizando',
    FAILED: 'Fallido',
  }

  return labels[value] ?? value
}

function formatRunStatus(value: string): string {
  const labels: Record<string, string> = {
    PENDING: 'Pendiente',
    RUNNING: 'En proceso',
    COMPLETED: 'Completado',
    FAILED: 'Fallido',
  }

  return labels[value] ?? value
}

function statusClass(value: string): string {
  if (value === 'ANALYZED') return 'bg-emerald-50 text-emerald-700 ring-emerald-100'
  if (value === 'FAILED') return 'bg-red-50 text-red-700 ring-red-100'
  if (value === 'ANALYZING') return 'bg-amber-50 text-amber-700 ring-amber-100'
  return 'bg-slate-100 text-slate-600 ring-slate-200'
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
              v-model="searchTerm"
              type="search"
              placeholder="Buscar alumno correo o repositorio..."
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

      <div class="mx-auto max-w-7xl px-4 py-6 lg:px-8 lg:py-7">
        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <article
            v-for="card in statCards"
            :key="card.title"
            class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-900/5"
          >
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
                <Icon :name="card.icon" class="h-5 w-5" />
              </div>
              <div>
                <p class="text-xs font-semibold text-slate-500">{{ card.title }}</p>
                <p class="mt-1 text-2xl font-black text-slate-950">{{ card.value }}</p>
              </div>
            </div>
          </article>
        </div>

        <section class="mt-5 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-900/5">
          <div class="grid gap-3 md:grid-cols-[1fr_220px_180px]">
            <label class="relative">
              <Icon name="search" class="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                v-model="searchTerm"
                type="search"
                placeholder="Buscar por alumno correo o repositorio"
                class="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-sm outline-none transition focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100"
              />
            </label>

            <select
              v-model="selectedProjectId"
              class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-medium text-slate-700 outline-none transition focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100"
            >
              <option value="all">Todos los proyectos</option>
              <option v-for="project in projects" :key="project.id" :value="project.id">
                {{ project.name }}
              </option>
            </select>

            <select
              v-model="selectedStatus"
              class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-medium text-slate-700 outline-none transition focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100"
            >
              <option value="all">Todos los estados</option>
              <option value="LINKED">Vinculado</option>
              <option value="ANALYZED">Analizado</option>
              <option value="FAILED">Fallido</option>
            </select>
          </div>
        </section>

        <p v-if="deliveriesError" class="mt-5 rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">{{ deliveriesError }}</p>
        <p v-if="actionMessage" class="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2.5 text-sm text-emerald-700">{{ actionMessage }}</p>

        <section class="mt-5 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm shadow-slate-900/5">
          <div class="flex items-center justify-between border-b border-slate-100 px-4 py-3">
            <div>
              <h2 class="text-lg font-black text-slate-950">Listado de entregas</h2>
              <p class="text-xs text-slate-500">
                {{ filteredDeliveries.length }} entrega{{ filteredDeliveries.length === 1 ? '' : 's' }} visible{{ filteredDeliveries.length === 1 ? '' : 's' }}
              </p>
            </div>
            <button
              type="button"
              class="rounded-lg border border-slate-200 px-3 py-2 text-xs font-bold text-slate-600 transition hover:border-emerald-200 hover:text-emerald-700"
              @click="loadDeliveries"
            >
              Actualizar
            </button>
          </div>

          <div v-if="loading" class="p-6 text-sm text-slate-500">Cargando entregas...</div>

          <div v-else-if="filteredDeliveries.length" class="hidden overflow-x-auto lg:block">
            <table class="min-w-full divide-y divide-slate-100 text-left text-sm">
              <thead class="bg-slate-50 text-xs font-bold uppercase tracking-wide text-slate-500">
                <tr>
                  <th class="px-4 py-3">Alumno</th>
                  <th class="px-4 py-3">Proyecto</th>
                  <th class="px-4 py-3">Repositorio</th>
                  <th class="px-4 py-3">Rama</th>
                  <th class="px-4 py-3">Estado</th>
                  <th class="px-4 py-3">Último commit</th>
                  <th class="px-4 py-3">Último análisis</th>
                  <th class="px-4 py-3">Acciones</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="delivery in filteredDeliveries" :key="delivery.id" class="align-top">
                  <td class="px-4 py-4">
                    <div class="flex items-center gap-3">
                      <img
                        v-if="delivery.student.avatar_url"
                        :src="delivery.student.avatar_url"
                        :alt="delivery.student.full_name"
                        class="h-9 w-9 rounded-full object-cover"
                      />
                      <div v-else class="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-50 text-xs font-black text-emerald-700">
                        {{ delivery.student.full_name.charAt(0).toUpperCase() }}
                      </div>
                      <div>
                        <p class="font-bold text-slate-900">{{ delivery.student.full_name }}</p>
                        <p class="text-xs text-slate-500">{{ delivery.student.email }}</p>
                      </div>
                    </div>
                  </td>
                  <td class="px-4 py-4 font-medium text-slate-700">{{ delivery.project_name }}</td>
                  <td class="max-w-[220px] px-4 py-4">
                    <a
                      :href="delivery.repo_url"
                      target="_blank"
                      rel="noreferrer"
                      class="inline-flex max-w-full items-center gap-1.5 truncate font-bold text-emerald-700 hover:text-emerald-800"
                    >
                      <span class="truncate">{{ formatRepositoryUrl(delivery.repo_url) }}</span>
                      <Icon name="external-link" class="h-3.5 w-3.5 shrink-0" />
                    </a>
                  </td>
                  <td class="px-4 py-4 text-slate-600">{{ delivery.branch }}</td>
                  <td class="px-4 py-4">
                    <span class="inline-flex rounded-full px-2.5 py-1 text-xs font-black ring-1" :class="statusClass(delivery.status)">
                      {{ formatStatus(delivery.status) }}
                    </span>
                  </td>
                  <td class="px-4 py-4 font-mono text-xs text-slate-600">{{ shortCommit(delivery.last_commit_hash) }}</td>
                  <td class="px-4 py-4 text-xs text-slate-500">{{ formatDate(delivery.last_analyzed_at) }}</td>
                  <td class="px-4 py-4">
                    <div class="flex flex-wrap gap-2">
                      <RouterLink
                        :to="`/projects/${delivery.project_id}`"
                        class="inline-flex h-8 items-center gap-1.5 rounded-lg border border-slate-200 px-2.5 text-xs font-bold text-slate-700 transition hover:border-emerald-200 hover:text-emerald-700"
                      >
                        <Icon name="eye" class="h-3.5 w-3.5" />
                        Ver proyecto
                      </RouterLink>
                      <button
                        type="button"
                        class="inline-flex h-8 items-center gap-1.5 rounded-lg bg-emerald-600 px-2.5 text-xs font-bold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
                        :disabled="analyzingTechnicalId === delivery.id"
                        @click="handleAnalyzeTechnical(delivery)"
                      >
                        <Icon name="play" class="h-3.5 w-3.5" />
                        {{ analyzingTechnicalId === delivery.id ? 'Analizando...' : 'Técnico' }}
                      </button>
                      <button
                        type="button"
                        class="inline-flex h-8 items-center gap-1.5 rounded-lg bg-slate-100 px-2.5 text-xs font-bold text-slate-700 transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
                        :disabled="analyzingAiId === delivery.id || loadingLatestAiId === delivery.id"
                        @click="handleAnalyzeAi(delivery)"
                      >
                        <Icon name="sparkles" class="h-3.5 w-3.5" />
                        {{ analyzingAiId === delivery.id ? 'Analizando...' : 'IA' }}
                      </button>
                      <button
                        type="button"
                        class="inline-flex h-8 items-center gap-1.5 rounded-lg bg-slate-100 px-2.5 text-xs font-bold text-slate-700 transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
                        :disabled="analyzingAiId === delivery.id || loadingLatestAiId === delivery.id"
                        @click="handleLatestAi(delivery)"
                      >
                        <Icon name="brain" class="h-3.5 w-3.5" />
                        {{ loadingLatestAiId === delivery.id ? 'Cargando...' : 'Último IA' }}
                      </button>
                      <button
                        type="button"
                        class="inline-flex h-8 items-center gap-1.5 rounded-lg bg-red-50 px-2.5 text-xs font-bold text-red-600 transition hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-60"
                        :disabled="deletingRepositoryId === delivery.id"
                        @click="handleDeleteDelivery(delivery)"
                      >
                        <Icon name="trash" class="h-3.5 w-3.5" />
                        {{ deletingRepositoryId === delivery.id ? 'Eliminando...' : 'Eliminar' }}
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else-if="!deliveriesError" class="p-8 text-center">
            <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
              <Icon name="inbox" class="h-6 w-6" />
            </div>
            <h3 class="mt-4 text-lg font-black text-slate-950">Aún no hay entregas</h3>
            <p class="mx-auto mt-2 max-w-md text-sm leading-5 text-slate-500">
              Cuando tus alumnos vinculen repositorios aparecerán aquí.
            </p>
            <RouterLink to="/projects" class="mt-5 inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-emerald-700">
              Ver proyectos
              <Icon name="chevron-right" class="h-4 w-4" />
            </RouterLink>
          </div>

          <div v-if="!loading && filteredDeliveries.length" class="grid gap-3 p-4 lg:hidden">
            <article
              v-for="delivery in filteredDeliveries"
              :key="delivery.id"
              class="rounded-xl border border-slate-200 p-4"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-center gap-3">
                  <img
                    v-if="delivery.student.avatar_url"
                    :src="delivery.student.avatar_url"
                    :alt="delivery.student.full_name"
                    class="h-10 w-10 rounded-full object-cover"
                  />
                  <div v-else class="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-50 text-sm font-black text-emerald-700">
                    {{ delivery.student.full_name.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <h3 class="font-black text-slate-950">{{ delivery.student.full_name }}</h3>
                    <p class="text-xs text-slate-500">{{ delivery.student.email }}</p>
                  </div>
                </div>
                <span class="inline-flex rounded-full px-2.5 py-1 text-xs font-black ring-1" :class="statusClass(delivery.status)">
                  {{ formatStatus(delivery.status) }}
                </span>
              </div>

              <dl class="mt-4 grid gap-2 text-sm">
                <div>
                  <dt class="text-xs font-bold text-slate-400">Proyecto</dt>
                  <dd class="font-medium text-slate-700">{{ delivery.project_name }}</dd>
                </div>
                <div>
                  <dt class="text-xs font-bold text-slate-400">Repositorio</dt>
                  <dd>
                    <a :href="delivery.repo_url" target="_blank" rel="noreferrer" class="font-bold text-emerald-700">
                      {{ formatRepositoryUrl(delivery.repo_url) }}
                    </a>
                  </dd>
                </div>
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <dt class="text-xs font-bold text-slate-400">Rama</dt>
                    <dd class="text-slate-700">{{ delivery.branch }}</dd>
                  </div>
                  <div>
                    <dt class="text-xs font-bold text-slate-400">Último commit</dt>
                    <dd class="font-mono text-xs text-slate-700">{{ shortCommit(delivery.last_commit_hash) }}</dd>
                  </div>
                </div>
                <div>
                  <dt class="text-xs font-bold text-slate-400">Último análisis</dt>
                  <dd class="text-slate-700">{{ formatDate(delivery.last_analyzed_at) }}</dd>
                </div>
              </dl>

              <div class="mt-4 grid gap-2 sm:grid-cols-2">
                <RouterLink :to="`/projects/${delivery.project_id}`" class="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-bold text-slate-700">
                  <Icon name="eye" class="h-4 w-4" />
                  Ver proyecto
                </RouterLink>
                <button type="button" class="inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-3 py-2 text-xs font-bold text-white" @click="handleAnalyzeTechnical(delivery)">
                  <Icon name="play" class="h-4 w-4" />
                  Análisis técnico
                </button>
                <button type="button" class="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700" @click="handleAnalyzeAi(delivery)">
                  <Icon name="sparkles" class="h-4 w-4" />
                  Análisis IA
                </button>
                <button type="button" class="inline-flex items-center justify-center gap-2 rounded-lg bg-red-50 px-3 py-2 text-xs font-bold text-red-600" @click="handleDeleteDelivery(delivery)">
                  <Icon name="trash" class="h-4 w-4" />
                  Eliminar
                </button>
              </div>
            </article>
          </div>
        </section>
      </div>
    </section>
  </main>
</template>
