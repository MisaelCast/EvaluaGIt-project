<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import type { User } from '@supabase/supabase-js'

import { getCurrentUser, signOut } from '@/services/auth'
import { getProject, updateProject, type ProjectRequirements } from '@/services/projects'

const route = useRoute()
const router = useRouter()
const projectId = route.params.projectId as string

type IconName =
  | 'bar-chart'
  | 'bell'
  | 'chevron-left'
  | 'folder'
  | 'hash'
  | 'home'
  | 'list'
  | 'save'
  | 'search'
  | 'settings'
  | 'sparkles'
  | 'text'
  | 'upload-cloud'

const iconPaths: Record<IconName, string[]> = {
  'bar-chart': ['M3 3v18h18', 'M7 15v2', 'M12 10v7', 'M17 6v11'],
  bell: ['M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9', 'M13.73 21a2 2 0 0 1-3.46 0'],
  'chevron-left': ['M15 18l-6-6 6-6'],
  folder: ['M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z'],
  hash: ['M10 4 6 20', 'M18 4l-4 16', 'M4 9h16', 'M3 15h16'],
  home: ['M3 10.5 12 3l9 7.5', 'M5 10v10h14V10', 'M9 20v-6h6v6'],
  list: ['M8 6h13', 'M8 12h13', 'M8 18h13', 'M3 6h.01', 'M3 12h.01', 'M3 18h.01'],
  save: ['M5 3h11l3 3v15H5z', 'M8 3v6h8', 'M8 15h8'],
  search: ['M21 21l-4.35-4.35', 'M10.5 18a7.5 7.5 0 1 0 0-15 7.5 7.5 0 0 0 0 15Z'],
  settings: ['M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z', 'M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 1.55V21a2 2 0 1 1-4 0v-.05a1.7 1.7 0 0 0-1-1.55 1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.55-1H3a2 2 0 1 1 0-4h.05A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.55V3a2 2 0 1 1 4 0v.05A1.7 1.7 0 0 0 15 4.6a1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.55 1H21a2 2 0 1 1 0 4h-.05A1.7 1.7 0 0 0 19.4 15Z'],
  sparkles: ['M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8Z', 'M5 3v4', 'M3 5h4', 'M19 17v4', 'M17 19h4'],
  text: ['M4 7V4h16v3', 'M8 20h8', 'M12 4v16'],
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

type ProjectFormRequirements = ProjectRequirements

const loading = ref(true)
const saving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const user = ref<User | null>(null)
const projectName = ref('')
const projectDescription = ref('')
const requiredFilesText = ref('')
const forbiddenFilesText = ref('')
const requiredFeaturesText = ref('')
const minimumCommits = ref(0)
const joinCode = ref('')

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
  void loadProject()
})

function emptyRequirements(): ProjectFormRequirements {
  return {
    requiredFiles: [],
    forbiddenFiles: [],
    requiredFeatures: [],
    minimumCommits: 0,
  }
}

function normalizeList(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value.map((item) => String(item).trim()).filter(Boolean)
  }

  if (typeof value === 'string') {
    return value
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
  }

  return []
}

function normalizeRequirements(requirements: unknown): ProjectFormRequirements {
  const base = emptyRequirements()

  if (!requirements || Array.isArray(requirements) || typeof requirements !== 'object') {
    return base
  }

  const raw = requirements as Record<string, unknown>
  return {
    requiredFiles: normalizeList(raw.requiredFiles),
    forbiddenFiles: normalizeList(raw.forbiddenFiles),
    requiredFeatures: normalizeList(raw.requiredFeatures),
    minimumCommits: Number.isFinite(Number(raw.minimumCommits)) ? Math.max(0, Math.floor(Number(raw.minimumCommits))) : 0,
  }
}

function syncFormValues(project: {
  name: string
  description: string | null
  requirements: unknown
  join_code: string
}) {
  projectName.value = project.name
  projectDescription.value = project.description ?? ''

  const requirements = normalizeRequirements(project.requirements)
  requiredFilesText.value = requirements.requiredFiles.join('\n')
  forbiddenFilesText.value = requirements.forbiddenFiles.join('\n')
  requiredFeaturesText.value = requirements.requiredFeatures.join('\n')
  minimumCommits.value = requirements.minimumCommits
  joinCode.value = project.join_code
}

async function loadUser() {
  try {
    user.value = await getCurrentUser()
  } catch {
    user.value = null
  }
}

async function loadProject() {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const project = await getProject(projectId)
    syncFormValues(project)
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'No se pudo cargar la configuración del proyecto'
  } finally {
    loading.value = false
  }
}

function parseList(text: string): string[] {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
}

function buildRequirements(): ProjectFormRequirements {
  return {
    requiredFiles: parseList(requiredFilesText.value),
    forbiddenFiles: parseList(forbiddenFilesText.value),
    requiredFeatures: parseList(requiredFeaturesText.value),
    minimumCommits: Math.max(0, Number(minimumCommits.value) || 0),
  }
}

async function handleSave() {
  errorMessage.value = ''
  successMessage.value = ''
  saving.value = true

  const name = projectName.value.trim()
  if (!name) {
    errorMessage.value = 'El nombre del proyecto no puede estar vacío'
    saving.value = false
    return
  }

  try {
    const updated = await updateProject(projectId, {
      name,
      description: projectDescription.value.trim(),
      requirements: buildRequirements(),
    })
    syncFormValues(updated)
    successMessage.value = 'Configuración actualizada correctamente'
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'No se pudo guardar la configuración'
  } finally {
    saving.value = false
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
        <div class="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 class="text-2xl font-black text-slate-950">Configuración del proyecto</h1>
            <p class="mt-1 max-w-2xl text-sm text-slate-500">
              Edita la información general y los criterios de análisis de este proyecto.
            </p>
            <div v-if="joinCode" class="mt-3 inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-700">
              <Icon name="hash" class="h-4 w-4" />
              Código para alumnos: {{ joinCode }}
            </div>
          </div>

          <div class="flex flex-col gap-2 sm:flex-row">
            <RouterLink
              :to="`/projects/${projectId}`"
              class="inline-flex items-center justify-center rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-bold text-slate-700 transition hover:border-slate-950 hover:text-slate-950"
            >
              Volver al proyecto
            </RouterLink>
            <button
              type="button"
              class="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="loading || saving"
              @click="handleSave"
            >
              <Icon name="save" class="h-4 w-4" />
              {{ saving ? 'Guardando...' : 'Guardar cambios' }}
            </button>
          </div>
        </div>

        <p v-if="errorMessage" class="mb-5 rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
          {{ errorMessage }}
        </p>
        <p v-if="successMessage" class="mb-5 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2.5 text-sm text-emerald-700">
          {{ successMessage }}
        </p>

        <div v-if="loading" class="rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-500 shadow-sm shadow-slate-900/5">
          Cargando configuración...
        </div>

        <div v-else class="grid gap-5">
          <section class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-900/5">
            <div class="mb-5 flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
                <Icon name="folder" class="h-5 w-5" />
              </div>
              <div>
                <h2 class="text-lg font-black text-slate-950">Información general</h2>
                <p class="text-sm text-slate-500">Nombre y descripción visibles para el profesor y los alumnos.</p>
              </div>
            </div>

            <div class="grid gap-4 lg:grid-cols-2">
              <label class="grid gap-1.5 text-sm font-bold text-slate-700">
                Nombre del proyecto
                <input
                  v-model="projectName"
                  type="text"
                  class="rounded-xl border border-slate-200 px-3 py-2.5 text-sm font-medium text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100"
                  placeholder="Proyecto final"
                />
              </label>

              <label class="grid gap-1.5 text-sm font-bold text-slate-700 lg:col-span-2">
                Descripción
                <textarea
                  v-model="projectDescription"
                  rows="4"
                  class="min-h-[112px] resize-y rounded-xl border border-slate-200 px-3 py-2.5 text-sm font-medium text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100"
                  placeholder="Breve descripción del proyecto"
                />
              </label>
            </div>
          </section>

          <section class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-900/5">
            <div class="mb-5 flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
                <Icon name="settings" class="h-5 w-5" />
              </div>
              <div>
                <h2 class="text-lg font-black text-slate-950">Requerimientos técnicos</h2>
                <p class="text-sm text-slate-500">Define las reglas que usará el análisis técnico.</p>
              </div>
            </div>

            <div class="grid gap-4 lg:grid-cols-2">
              <label class="grid gap-1.5 text-sm font-bold text-slate-700">
                Mínimo de commits
                <input
                  v-model.number="minimumCommits"
                  type="number"
                  min="0"
                  class="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm font-medium text-slate-900 outline-none transition focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100"
                />
              </label>

              <label class="grid gap-1.5 text-sm font-bold text-slate-700">
                Archivos requeridos
                <textarea
                  v-model="requiredFilesText"
                  rows="5"
                  class="min-h-[124px] resize-y rounded-xl border border-slate-200 px-3 py-2.5 text-sm font-medium text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100"
                  placeholder="README.md&#10;requirements.txt"
                />
              </label>

              <label class="grid gap-1.5 text-sm font-bold text-slate-700">
                Archivos prohibidos
                <textarea
                  v-model="forbiddenFilesText"
                  rows="5"
                  class="min-h-[124px] resize-y rounded-xl border border-slate-200 px-3 py-2.5 text-sm font-medium text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100"
                  placeholder=".env&#10;*.pem&#10;secrets.json"
                />
              </label>

              <label class="grid gap-1.5 text-sm font-bold text-slate-700 lg:col-span-2">
                Criterios adicionales
                <textarea
                  v-model="requiredFeaturesText"
                  rows="5"
                  class="min-h-[124px] resize-y rounded-xl border border-slate-200 px-3 py-2.5 text-sm font-medium text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100"
                  placeholder="login&#10;CRUD de proyectos&#10;validación de formulario"
                />
              </label>
            </div>
          </section>

          <section class="rounded-2xl border border-dashed border-slate-300 bg-white p-5 shadow-sm shadow-slate-900/5">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div class="text-sm text-slate-500">
                <p class="font-bold text-slate-700">Zona de acciones</p>
                <p>Guarda los cambios o vuelve al proyecto para revisar las entregas y análisis.</p>
              </div>

              <div class="flex flex-col gap-2 sm:flex-row">
                <RouterLink
                  :to="`/projects/${projectId}`"
                  class="inline-flex items-center justify-center rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-bold text-slate-700 transition hover:border-slate-950 hover:text-slate-950"
                >
                  Volver al proyecto
                </RouterLink>
                <button
                  type="button"
                  class="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
                  :disabled="loading || saving"
                  @click="handleSave"
                >
                  <Icon name="save" class="h-4 w-4" />
                  {{ saving ? 'Guardando...' : 'Guardar cambios' }}
                </button>
              </div>
            </div>
          </section>
        </div>
      </div>
    </section>
  </main>
</template>
