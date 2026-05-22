<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import type { User } from '@supabase/supabase-js'

import { supabase } from '@/lib/supabase'
import { getHealth, type HealthResponse, getMe } from '@/services/api'
import { getCurrentUser, signInWithGoogle } from '@/services/auth'
import { syncUser } from '@/services/users'

const router = useRouter()
const loading = ref(true)
const healthError = ref('')
const health = ref<HealthResponse | null>(null)
const user = ref<User | null>(null)
const authError = ref('')
const userRole = ref<string | null>(null)

const dashboardRoute = computed(() => {
  if (userRole.value === 'PROFESSOR') return '/dashboard'
  if (userRole.value === 'STUDENT') return '/student/dashboard'
  if (userRole.value === 'UNASSIGNED') return '/onboarding'
  return '/dashboard'
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
          userRole.value = me.role
          if (me.role === 'UNASSIGNED') {
            router.push('/onboarding')
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

const navLinks = [
  { label: 'Caracteristicas', href: '#caracteristicas' },
  { label: 'Como funciona', href: '#como-funciona' },
  { label: 'Tecnologias', href: '#tecnologias' },
  { label: 'Demo', href: '#demo' },
]

const problemItems = [
  'Revisar repositorios uno por uno consume tiempo',
  'Detectar similitudes entre entregas es dificil',
  'Validar commits y estructura puede ser repetitivo',
  'Los resultados pueden ser poco consistentes',
]

const solutionItems = [
  'Analisis automatico de repositorios',
  'Validacion de requerimientos tecnicos',
  'Retroalimentacion IA sobre calidad de codigo',
  'Deteccion de similitudes con Dolos',
  'Reportes mas claros para el profesor',
]

const features = [
  {
    title: 'Analisis tecnico',
    description: 'Revisa estructura archivos requeridos archivos prohibidos dependencias README y actividad Git',
    icon: '⌘',
  },
  {
    title: 'Retroalimentacion IA',
    description: 'Detecta malas practicas hardcodeos problemas de mantenibilidad y riesgos tecnicos',
    icon: 'IA',
  },
  {
    title: 'Similitud entre entregas',
    description: 'Compara repositorios de alumnos y clasifica coincidencias por nivel',
    icon: '≈',
  },
  {
    title: 'Gestion de proyectos',
    description: 'Crea proyectos comparte codigos de union y revisa entregas de alumnos',
    icon: '▣',
  },
  {
    title: 'Resultados guardados',
    description: 'Consulta analisis anteriores sin perder informacion al recargar',
    icon: '✓',
  },
]

const steps = [
  'El profesor crea un proyecto',
  'Los alumnos se unen con un codigo',
  'Los alumnos vinculan su repositorio Git',
  'EvaluaGit analiza la entrega',
  'El profesor revisa resultados claros',
]

const technologies = [
  { name: 'Vue 3', icon: 'V' },
  { name: 'TypeScript', icon: 'TS' },
  { name: 'Tailwind CSS', icon: '~' },
  { name: 'FastAPI', icon: '⚡' },
  { name: 'PostgreSQL', icon: 'DB' },
  { name: 'Supabase', icon: 'S' },
  { name: 'Gemini API', icon: '✦' },
  { name: 'Docker', icon: '▣' },
  { name: 'Dolos', icon: '≈' },
  { name: 'GitHub', icon: 'Git' },
]
</script>

<template>
  <main class="min-h-screen bg-white text-slate-950">
    <header class="sticky top-0 z-40 border-b border-slate-200/70 bg-white/85 backdrop-blur-xl">
      <nav class="mx-auto flex max-w-7xl items-center justify-between px-6 py-3 lg:px-8">
        <a href="#inicio" class="flex items-center gap-3 font-bold text-slate-950">
          <span class="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-600 text-lg font-black text-white shadow-sm shadow-emerald-900/20">E</span>
          <span class="text-xl">EvaluaGit</span>
        </a>

        <div class="hidden items-center gap-8 text-sm font-medium text-slate-600 md:flex">
          <a
            v-for="link in navLinks"
            :key="link.href"
            :href="link.href"
            class="transition hover:text-emerald-700"
          >
            {{ link.label }}
          </a>
        </div>

        <div class="flex items-center gap-3">
          <RouterLink
            v-if="user"
            :to="dashboardRoute"
            class="hidden rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-emerald-200 hover:text-emerald-700 sm:inline-flex"
          >
            Ir al panel
          </RouterLink>
          <button
            v-else
            type="button"
            class="hidden rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-emerald-200 hover:text-emerald-700 sm:inline-flex"
            @click="handleSignIn"
          >
            Iniciar sesion
          </button>
          <a
            href="#demo"
            class="rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm shadow-emerald-900/20 transition hover:bg-emerald-700"
          >
            Ver demo
          </a>
        </div>
      </nav>
    </header>

    <section id="inicio" class="relative overflow-hidden border-b border-slate-100 bg-gradient-to-br from-white via-white to-emerald-50/50">
      <div class="absolute right-0 top-12 h-64 w-64 rounded-full bg-emerald-100/35 blur-3xl"></div>
      <div class="relative mx-auto grid max-w-7xl grid-cols-1 items-center gap-10 px-6 pb-16 pt-10 lg:grid-cols-2 lg:gap-14 lg:px-8 lg:pb-20 lg:pt-14">
        <div class="flex flex-col justify-center">
          <h1 class="max-w-3xl text-5xl font-black tracking-tight text-slate-950 sm:text-6xl lg:text-7xl">
            Analiza proyectos Git <span class="text-emerald-600">automaticamente</span>
          </h1>
          <p class="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
            EvaluaGit ayuda a profesores a revisar repositorios académicos, validar requerimientos técnicos, analizar actividad Git, obtener retroalimentación con IA y detectar similitudes entre entregas.
          </p>

          <div class="mt-9 flex flex-col gap-3 sm:flex-row">
            <RouterLink
              v-if="user"
              :to="dashboardRoute"
              class="inline-flex items-center justify-center rounded-xl bg-emerald-600 px-6 py-3 text-sm font-bold text-white shadow-lg shadow-emerald-900/15 transition hover:bg-emerald-700"
            >
              Ir al panel
              <span class="ml-2">→</span>
            </RouterLink>
            <button
              v-else
              type="button"
              class="inline-flex items-center justify-center rounded-xl bg-emerald-600 px-6 py-3 text-sm font-bold text-white shadow-lg shadow-emerald-900/15 transition hover:bg-emerald-700"
              @click="handleSignIn"
            >
              Iniciar sesion
              <span class="ml-2">→</span>
            </button>
            <a
              href="#demo"
              class="inline-flex items-center justify-center rounded-xl border border-slate-200 bg-white px-6 py-3 text-sm font-bold text-slate-900 shadow-sm transition hover:border-emerald-200 hover:text-emerald-700"
            >
              Ver demo
            </a>
          </div>

          <p v-if="authError" class="mt-4 text-sm font-medium text-red-600">{{ authError }}</p>

          <div class="mt-10 flex flex-wrap gap-3 text-sm font-medium text-slate-500">
            <span class="inline-flex items-center gap-2 rounded-full bg-slate-50 px-3 py-2"><span class="text-emerald-600">●</span>Hecho para profesores</span>
            <span class="inline-flex items-center gap-2 rounded-full bg-slate-50 px-3 py-2"><span class="text-emerald-600">●</span>Ahorra tiempo de revision</span>
            <span class="inline-flex items-center gap-2 rounded-full bg-slate-50 px-3 py-2"><span class="text-emerald-600">●</span>Enfocado en educacion</span>
          </div>
        </div>

        <div class="flex items-center justify-center">
          <img
            src="/hero.png"
            alt="Ilustracion de EvaluaGit analizando repositorios Git"
            class="mx-auto w-full max-w-xl object-contain lg:max-w-2xl"
          />
        </div>
      </div>
    </section>

    <section id="demo" class="mx-auto max-w-7xl px-6 py-20 lg:px-8">
      <div class="mx-auto max-w-3xl text-center">
        <h2 class="text-3xl font-black tracking-tight text-slate-950 sm:text-4xl">Deja de revisar repositorios manualmente</h2>
      </div>

      <div class="mx-auto mt-10 grid max-w-5xl gap-6 lg:grid-cols-2">
        <article class="rounded-3xl border border-red-100 bg-red-50/40 p-8 shadow-sm">
          <h3 class="text-xl font-bold text-red-700">El problema de siempre</h3>
          <ul class="mt-6 space-y-4 text-sm leading-6 text-slate-700">
            <li v-for="item in problemItems" :key="item" class="flex gap-3"><span class="font-bold text-red-500">×</span>{{ item }}</li>
          </ul>
        </article>
        <article class="rounded-3xl border border-emerald-100 bg-emerald-50/40 p-8 shadow-sm">
          <h3 class="text-xl font-bold text-emerald-700">Con EvaluaGit</h3>
          <ul class="mt-6 space-y-4 text-sm leading-6 text-slate-700">
            <li v-for="item in solutionItems" :key="item" class="flex gap-3"><span class="font-bold text-emerald-600">✓</span>{{ item }}</li>
          </ul>
        </article>
      </div>
    </section>

    <section id="caracteristicas" class="border-y border-slate-100 bg-slate-50/60">
      <div class="mx-auto max-w-7xl px-6 py-20 lg:px-8">
        <div class="mx-auto max-w-3xl text-center">
          <h2 class="text-3xl font-black tracking-tight text-slate-950 sm:text-4xl">Todo lo que necesitas para evaluar mejor</h2>
        </div>
        <div class="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-5">
          <article
            v-for="feature in features"
            :key="feature.title"
            class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg hover:shadow-slate-900/5"
          >
            <div class="mb-6 flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-lg font-black text-emerald-600">{{ feature.icon }}</div>
            <h3 class="font-bold text-slate-950">{{ feature.title }}</h3>
            <p class="mt-3 text-sm leading-6 text-slate-600">{{ feature.description }}</p>
          </article>
        </div>
      </div>
    </section>

    <section id="como-funciona" class="mx-auto max-w-7xl px-6 py-20 lg:px-8">
      <div class="mx-auto max-w-3xl text-center">
        <h2 class="text-3xl font-black tracking-tight text-slate-950 sm:text-4xl">Asi funciona EvaluaGit</h2>
      </div>
      <div class="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-5">
        <article
          v-for="(step, index) in steps"
          :key="step"
          class="relative rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <span class="absolute -top-3 left-6 flex h-8 w-8 items-center justify-center rounded-full bg-emerald-600 text-sm font-bold text-white">{{ index + 1 }}</span>
          <p class="pt-4 text-sm font-bold leading-6 text-slate-900">{{ step }}</p>
        </article>
      </div>
    </section>

    <section id="tecnologias" class="border-y border-slate-100 bg-slate-50/60">
      <div class="mx-auto max-w-7xl px-6 py-20 lg:px-8">
        <div class="mx-auto max-w-3xl text-center">
          <h2 class="text-3xl font-black tracking-tight text-slate-950 sm:text-4xl">Tecnologias utilizadas</h2>
        </div>
        <div class="mx-auto mt-10 flex max-w-5xl flex-wrap justify-center gap-3">
          <span
            v-for="technology in technologies"
            :key="technology.name"
            class="inline-flex items-center gap-3 rounded-full border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:-translate-y-0.5 hover:border-emerald-200 hover:text-emerald-700 hover:shadow-md hover:shadow-slate-900/5"
          >
            <span class="flex h-7 min-w-7 items-center justify-center rounded-full bg-emerald-50 px-2 text-xs font-black text-emerald-700">
              {{ technology.icon }}
            </span>
            {{ technology.name }}
          </span>
        </div>
      </div>
    </section>

    <section class="mx-auto max-w-7xl px-6 py-20 lg:px-8">
      <div class="rounded-[2rem] border border-emerald-100 bg-emerald-50/60 p-8 shadow-sm md:flex md:items-center md:justify-between md:p-12">
        <div class="max-w-3xl">
          <h2 class="text-3xl font-black tracking-tight text-slate-950">Una herramienta academica para revisar proyectos de software</h2>
          <p class="mt-4 text-base leading-7 text-slate-600">EvaluaGit centraliza entregas analisis y resultados para que el profesor tenga una vision mas clara del avance calidad y similitud de los proyectos.</p>
        </div>
        <RouterLink
          v-if="user"
          :to="dashboardRoute"
          class="mt-8 inline-flex rounded-xl bg-emerald-600 px-6 py-3 text-sm font-bold text-white shadow-lg shadow-emerald-900/15 transition hover:bg-emerald-700 md:mt-0"
        >
          Ir al panel
        </RouterLink>
        <button
          v-else
          type="button"
          class="mt-8 inline-flex rounded-xl bg-emerald-600 px-6 py-3 text-sm font-bold text-white shadow-lg shadow-emerald-900/15 transition hover:bg-emerald-700 md:mt-0"
          @click="handleSignIn"
        >
          Iniciar sesion
        </button>
      </div>
    </section>

    <footer class="border-t border-slate-200 bg-white">
      <div class="mx-auto grid max-w-7xl gap-8 px-6 py-10 md:grid-cols-[1.5fr_1fr] lg:px-8">
        <div>
          <div class="flex items-center gap-3 font-bold text-slate-950">
            <span class="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-600 text-lg font-black text-white">E</span>
            <span class="text-xl">EvaluaGit</span>
          </div>
          <p class="mt-4 max-w-md text-sm leading-6 text-slate-600">Plataforma academica de analisis de repositorios Git</p>
        </div>
        <div class="grid grid-cols-2 gap-4 text-sm font-medium text-slate-600 sm:grid-cols-4">
          <a
            v-for="link in navLinks"
            :key="link.href"
            :href="link.href"
            class="hover:text-emerald-700"
          >
            {{ link.label }}
          </a>
        </div>
      </div>
    </footer>
  </main>
</template>
