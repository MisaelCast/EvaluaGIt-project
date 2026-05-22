<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import type { User } from '@supabase/supabase-js'

import { getCurrentUser, signOut } from '@/services/auth'
import { getProjects, type ProjectResponse } from '@/services/projects'

const router = useRouter()
const user = ref<User | null>(null)
const projects = ref<ProjectResponse[]>([])
const loading = ref(true)
const projectsError = ref('')

type IconName =
  | 'alert-triangle'
  | 'bar-chart'
  | 'bell'
  | 'bell-ring'
  | 'brain'
  | 'chevron-right'
  | 'clock'
  | 'code'
  | 'folder'
  | 'folder-open'
  | 'git-compare'
  | 'home'
  | 'inbox'
  | 'layout-dashboard'
  | 'plus'
  | 'search'
  | 'settings'
  | 'sparkles'
  | 'upload-cloud'
  | 'zap'

const iconPaths: Record<IconName, string[]> = {
  'alert-triangle': ['M12 9v4', 'M12 17h.01', 'M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z'],
  'bar-chart': ['M3 3v18h18', 'M7 15v2', 'M12 10v7', 'M17 6v11'],
  bell: ['M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9', 'M13.73 21a2 2 0 0 1-3.46 0'],
  'bell-ring': ['M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9', 'M13.73 21a2 2 0 0 1-3.46 0', 'M4 4 2 2', 'M20 4l2-2'],
  brain: ['M9 3a3 3 0 0 0-3 3v1a3 3 0 0 0 0 6v1a3 3 0 0 0 3 3', 'M15 3a3 3 0 0 1 3 3v1a3 3 0 0 1 0 6v1a3 3 0 0 1-3 3', 'M9 3v18', 'M15 3v18', 'M9 8h2', 'M13 8h2', 'M9 16h2', 'M13 16h2'],
  'chevron-right': ['M9 18l6-6-6-6'],
  clock: ['M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20Z', 'M12 6v6l4 2'],
  code: ['M16 18l6-6-6-6', 'M8 6l-6 6 6 6'],
  folder: ['M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z'],
  'folder-open': ['M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v2', 'M3 17l3-6h16l-3 8H5a2 2 0 0 1-2-2Z'],
  'git-compare': ['M6 3v12', 'M18 9v12', 'M6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z', 'M18 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z', 'M8.5 7.5h5a4.5 4.5 0 0 1 4.5 4.5', 'M15.5 16.5h-5A4.5 4.5 0 0 1 6 12'],
  home: ['M3 10.5 12 3l9 7.5', 'M5 10v10h14V10', 'M9 20v-6h6v6'],
  inbox: ['M4 4h16l2 10v6H2v-6Z', 'M2 14h6a4 4 0 0 0 8 0h6'],
  'layout-dashboard': ['M3 3h8v8H3Z', 'M13 3h8v5h-8Z', 'M13 10h8v11h-8Z', 'M3 13h8v8H3Z'],
  plus: ['M12 5v14', 'M5 12h14'],
  search: ['M21 21l-4.35-4.35', 'M10.5 18a7.5 7.5 0 1 0 0-15 7.5 7.5 0 0 0 0 15Z'],
  settings: ['M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z', 'M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 1.55V21a2 2 0 1 1-4 0v-.05a1.7 1.7 0 0 0-1-1.55 1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.55-1H3a2 2 0 1 1 0-4h.05A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.55V3a2 2 0 1 1 4 0v.05A1.7 1.7 0 0 0 15 4.6a1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.55 1H21a2 2 0 1 1 0 4h-.05A1.7 1.7 0 0 0 19.4 15Z'],
  sparkles: ['M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8Z', 'M5 3v4', 'M3 5h4', 'M19 17v4', 'M17 19h4'],
  'upload-cloud': ['M16 16l-4-4-4 4', 'M12 12v9', 'M20 16.6A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25'],
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

const activeProjectsCount = computed(() => projects.value.length)
const recentProjects = computed(() => projects.value.slice(0, 3))
const enabledQuickActions = computed(() => quickActions.filter((action) => !action.disabled))
const upcomingQuickActions = computed(() => quickActions.filter((action) => action.disabled))

const statCards = computed(() => [
  {
    title: 'Proyectos activos',
    value: activeProjectsCount.value,
    link: 'Ver proyectos',
    to: '/projects',
    icon: 'folder-open' as IconName,
    tone: 'emerald',
  },
  {
    title: 'Entregas recibidas',
    value: 'Próximamente',
    link: 'Ver entregas',
    to: '/deliveries',
    icon: 'inbox' as IconName,
    tone: 'emerald',
  },
  {
    title: 'Análisis realizados',
    value: 'Próximamente',
    link: 'Ver proyectos',
    to: '/projects',
    icon: 'code' as IconName,
    tone: 'emerald',
  },
  {
    title: 'Alertas relevantes',
    value: 'Próximamente',
    link: 'Ver proyectos',
    to: '/projects',
    icon: 'bell-ring' as IconName,
    tone: 'red',
  },
])

const activities = [
  {
    title: 'Análisis técnico completado',
    description: 'Revisión técnica finalizada correctamente',
    time: 'Hoy',
    icon: 'code' as IconName,
  },
  {
    title: 'Nueva entrega recibida',
    description: 'Un alumno vinculó su repositorio al proyecto',
    time: 'Hoy',
    icon: 'inbox' as IconName,
  },
  {
    title: 'Análisis IA completado',
    description: 'Retroalimentación generada para una entrega',
    time: 'Reciente',
    icon: 'brain' as IconName,
  },
  {
    title: 'Análisis de similitud ejecutado',
    description: 'Dolos comparó entregas entre alumnos',
    time: 'Reciente',
    icon: 'git-compare' as IconName,
  },
]

const quickActions = [
  {
    title: 'Crear proyecto',
    to: '/projects',
    icon: 'plus' as IconName,
    disabled: false,
  },
  {
    title: 'Ver entregas',
    to: '/deliveries',
    icon: 'inbox' as IconName,
    disabled: false,
  },
  {
    title: 'Ver resultados',
    to: '/projects',
    icon: 'bar-chart' as IconName,
    disabled: true,
  },
  {
    title: 'Analizar similitud',
    to: '/projects',
    icon: 'git-compare' as IconName,
    disabled: true,
  },
]

const analysisSummary = [
  {
    label: 'Técnico',
    detail: 'Resumen en preparación',
    icon: 'code' as IconName,
  },
  {
    label: 'IA',
    detail: 'Resumen en preparación',
    icon: 'brain' as IconName,
  },
  {
    label: 'Similitud',
    detail: 'Resumen en preparación',
    icon: 'git-compare' as IconName,
  },
]

onMounted(() => {
  void loadDashboard()
})

async function loadDashboard() {
  loading.value = true
  projectsError.value = ''

  try {
    user.value = await getCurrentUser()
  } catch {
    user.value = null
  }

  try {
    projects.value = await getProjects()
  } catch (err) {
    projects.value = []
    projectsError.value =
      err instanceof Error ? err.message : 'No se pudieron cargar los proyectos'
  } finally {
    loading.value = false
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
</script>

<template>
  <main class="min-h-screen bg-neutral-50 text-slate-950 lg:grid lg:grid-cols-[280px_1fr]">
    <aside class="border-b border-slate-200 bg-white/95 px-5 py-5 shadow-sm lg:min-h-screen lg:border-b-0 lg:border-r">
      <div class="flex items-center justify-between lg:block">
        <RouterLink to="/dashboard" class="flex items-center gap-3">
          <span class="flex h-10 w-10 items-center justify-center rounded-2xl bg-emerald-600 text-lg font-black text-white">E</span>
          <span class="text-2xl font-black tracking-tight">Evalua<span class="text-emerald-600">Git</span></span>
        </RouterLink>
      </div>

      <nav class="mt-6 flex gap-2 overflow-x-auto lg:mt-10 lg:flex-col lg:overflow-visible">
        <RouterLink to="/dashboard" class="flex min-w-fit items-center gap-3 rounded-2xl bg-emerald-50 px-4 py-3 text-sm font-bold text-emerald-700">
          <span class="flex h-8 w-8 items-center justify-center rounded-xl bg-emerald-100">
            <Icon name="layout-dashboard" class="h-4 w-4" />
          </span>
          Dashboard
        </RouterLink>
        <RouterLink to="/projects" class="flex min-w-fit items-center gap-3 rounded-2xl px-4 py-3 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 hover:text-emerald-700">
          <span class="flex h-8 w-8 items-center justify-center rounded-xl border border-slate-200">
            <Icon name="folder" class="h-4 w-4" />
          </span>
          Proyectos
        </RouterLink>
        <RouterLink to="/deliveries" class="flex min-w-fit items-center gap-3 rounded-2xl px-4 py-3 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 hover:text-emerald-700">
          <span class="flex h-8 w-8 items-center justify-center rounded-xl border border-slate-200">
            <Icon name="upload-cloud" class="h-4 w-4" />
          </span>
          Entregas
        </RouterLink>
        <span class="flex min-w-fit items-center justify-between gap-3 rounded-2xl px-4 py-3 text-sm font-semibold text-slate-400">
          <span class="flex items-center gap-3">
            <span class="flex h-8 w-8 items-center justify-center rounded-xl border border-slate-200">
              <Icon name="bar-chart" class="h-4 w-4" />
            </span>
            Resultados
          </span>
          <span class="hidden rounded-full bg-slate-100 px-2 py-1 text-[10px] font-bold text-slate-500 lg:inline-flex">Próximamente</span>
        </span>
        <span class="flex min-w-fit items-center justify-between gap-3 rounded-2xl px-4 py-3 text-sm font-semibold text-slate-400">
          <span class="flex items-center gap-3">
            <span class="flex h-8 w-8 items-center justify-center rounded-xl border border-slate-200">
              <Icon name="settings" class="h-4 w-4" />
            </span>
            Configuración
          </span>
          <span class="hidden rounded-full bg-slate-100 px-2 py-1 text-[10px] font-bold text-slate-500 lg:inline-flex">Próximamente</span>
        </span>
      </nav>

      <button
        type="button"
        class="mt-8 hidden w-full items-center justify-center rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-bold text-slate-700 transition hover:border-slate-950 hover:bg-white hover:text-slate-950 lg:inline-flex"
        @click="handleSignOut"
      >
        Cerrar sesion
      </button>
    </aside>

    <section class="min-w-0">
      <header class="border-b border-slate-200 bg-white/90 px-5 py-4 backdrop-blur-xl lg:px-10">
        <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <label class="relative w-full max-w-xl">
            <Icon name="search" class="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
            <input
              type="search"
              placeholder="Buscar proyectos entregas estudiantes..."
              class="w-full rounded-2xl border border-slate-200 bg-white py-3 pl-11 pr-4 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100"
            />
          </label>

          <div class="flex items-center gap-4">
            <div class="relative hidden h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-600 md:flex">
              <Icon name="bell" class="h-5 w-5" />
              <span class="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-emerald-600 text-xs font-bold text-white">2</span>
            </div>
            <div class="flex items-center gap-3">
              <img
                v-if="profileImageUrl"
                :src="profileImageUrl"
                :alt="professorName"
                class="h-11 w-11 rounded-full object-cover ring-2 ring-white"
              />
              <div
                v-else
                class="flex h-11 w-11 items-center justify-center rounded-full bg-slate-900 text-sm font-bold text-white"
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

      <div class="mx-auto max-w-7xl px-5 py-8 lg:px-10 lg:py-10">
        <p v-if="projectsError" class="mb-8 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ projectsError }}</p>

        <section class="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          <article
            v-for="card in statCards"
            :key="card.title"
            class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-900/5"
          >
            <div class="flex items-start gap-4">
              <div
                class="flex h-12 w-12 items-center justify-center rounded-xl font-black"
                :class="card.tone === 'red' ? 'bg-red-50 text-red-600' : 'bg-emerald-50 text-emerald-700'"
              >
                <Icon :name="card.icon" class="h-6 w-6" />
              </div>
              <div>
                <p class="text-sm font-medium text-slate-600">{{ card.title }}</p>
                <p
                  class="mt-1 font-black text-slate-950"
                  :class="typeof card.value === 'number' ? 'text-3xl' : 'text-base'"
                >
                  {{ loading ? '...' : card.value }}
                </p>
              </div>
            </div>
            <RouterLink :to="card.to" class="mt-4 inline-flex items-center gap-2 text-sm font-bold text-emerald-700">
              {{ card.link }}
              <Icon name="chevron-right" class="h-4 w-4" />
            </RouterLink>
          </article>
        </section>

        <section class="mt-7 grid gap-7 xl:grid-cols-[1.35fr_1fr]">
          <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-900/5">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-50 text-emerald-700">
                  <Icon name="clock" class="h-5 w-5" />
                </span>
                <h2 class="text-xl font-black text-slate-950">Actividad reciente</h2>
              </div>
              <RouterLink to="/projects" class="text-sm font-bold text-emerald-700">Ver todas</RouterLink>
            </div>

            <div class="mt-7 space-y-5">
              <div
                v-for="activity in activities"
                :key="activity.title"
                class="grid grid-cols-[44px_1fr_auto] items-start gap-4"
              >
                <div class="flex h-11 w-11 items-center justify-center rounded-full bg-emerald-50 text-sm font-black text-emerald-700">
                  <Icon :name="activity.icon" class="h-5 w-5" />
                </div>
                <div>
                  <p class="font-bold text-slate-950">{{ activity.title }}</p>
                  <p class="mt-1 text-sm text-slate-500">{{ activity.description }}</p>
                </div>
                <p class="text-sm text-slate-400">{{ activity.time }}</p>
              </div>
            </div>
          </article>

          <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-900/5">
            <div class="flex items-center gap-3">
              <span class="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-50 text-emerald-700">
                <Icon name="zap" class="h-4 w-4" />
              </span>
              <h2 class="text-lg font-black text-slate-950">Acciones rápidas</h2>
            </div>

            <div class="mt-5 space-y-2">
              <RouterLink
                v-for="action in enabledQuickActions"
                :key="action.title"
                :to="action.to"
                class="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm text-slate-800 transition hover:border-emerald-200 hover:bg-emerald-50/40"
              >
                <span class="flex items-center gap-4 font-semibold">
                  <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50 font-black text-emerald-700">
                    <Icon :name="action.icon" class="h-4 w-4" />
                  </span>
                  {{ action.title }}
                </span>
                <Icon name="chevron-right" class="h-4 w-4 text-slate-400" />
              </RouterLink>
              <div
                v-for="action in upcomingQuickActions"
                :key="action.title"
                class="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 text-sm text-slate-400"
              >
                <span class="flex items-center gap-4 font-semibold">
                  <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-white text-slate-400">
                    <Icon :name="action.icon" class="h-4 w-4" />
                  </span>
                  <span>
                    {{ action.title }}
                    <span class="ml-2 text-xs font-bold text-slate-400">Próximamente</span>
                  </span>
                </span>
                <Icon name="chevron-right" class="h-4 w-4 text-slate-300" />
              </div>
            </div>
          </article>
        </section>

        <section class="mt-7 grid gap-7 xl:grid-cols-[1.35fr_1fr]">
          <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-900/5">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-50 text-emerald-700">
                  <Icon name="folder" class="h-5 w-5" />
                </span>
                <h2 class="text-xl font-black text-slate-950">Proyectos recientes</h2>
              </div>
              <RouterLink to="/projects" class="text-sm font-bold text-emerald-700">Ver todos</RouterLink>
            </div>

            <div class="mt-6 overflow-hidden rounded-2xl border border-slate-200">
              <table class="w-full text-left text-sm">
                <thead class="bg-slate-50 text-xs font-bold uppercase text-slate-500">
                  <tr>
                    <th class="px-4 py-3">Nombre del proyecto</th>
                    <th class="px-4 py-3">Código</th>
                    <th class="px-4 py-3">Entregas</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-200 bg-white text-slate-700">
                  <tr v-if="!recentProjects.length">
                    <td colspan="3" class="px-4 py-5 text-slate-500">Aún no hay proyectos recientes.</td>
                  </tr>
                  <tr v-for="project in recentProjects" :key="project.id">
                    <td class="px-4 py-4 font-medium text-slate-900">{{ project.name }}</td>
                    <td class="px-4 py-4">{{ project.join_code }}</td>
                    <td class="px-4 py-4">—</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </article>

          <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-900/5">
            <div class="flex items-center gap-3">
              <span class="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-50 text-emerald-700">
                <Icon name="bar-chart" class="h-5 w-5" />
              </span>
              <h2 class="text-xl font-black text-slate-950">Resumen de análisis</h2>
            </div>

            <div class="mt-7 space-y-6">
              <div v-for="item in analysisSummary" :key="item.label" class="grid grid-cols-[40px_1fr] gap-4">
                <div class="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-50 text-sm font-black text-emerald-700">
                  <Icon :name="item.icon" class="h-5 w-5" />
                </div>
                <div>
                  <div class="flex items-center justify-between">
                    <p class="font-bold text-slate-950">{{ item.label }}</p>
                    <p class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-500">En preparación</p>
                  </div>
                  <p class="mt-2 text-sm text-slate-500">{{ item.detail }}</p>
                </div>
              </div>
            </div>
          </article>
        </section>
      </div>
    </section>
  </main>
</template>
