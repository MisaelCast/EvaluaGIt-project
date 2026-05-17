<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import type { User } from '@supabase/supabase-js'
import { getCurrentUser, signOut } from '@/services/auth'

const user = ref<User | null>(null)
const loading = ref(true)

onMounted(() => {
  void loadUser()
})

async function loadUser() {
  loading.value = true
  try {
    user.value = await getCurrentUser()
  } catch {
    user.value = null
  } finally {
    loading.value = false
  }
}

async function handleSignOut() {
  try {
    await signOut()
    user.value = null
  } catch {
    // ignore
  }
}
</script>

<template>
  <main class="min-h-screen bg-slate-50 p-8">
    <header class="max-w-6xl mx-auto mb-8">
      <h1 class="text-3xl font-bold text-slate-900">Dashboard</h1>
    </header>

    <section class="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <article class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col gap-3">
        <h2 class="text-lg font-semibold text-slate-900">Proyectos</h2>
        <p class="text-slate-500 flex-1">Gestiona tus proyectos y requerimientos.</p>
        <RouterLink to="/projects" class="inline-block text-center bg-emerald-600 text-white font-bold py-2 px-4 rounded hover:bg-emerald-700 transition-colors">
          Ir a proyectos
        </RouterLink>
      </article>

      <article class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col gap-3">
        <h2 class="text-lg font-semibold text-slate-900">Repositorios</h2>
        <p class="text-slate-500 flex-1">Vincuta repositorios GitHub a tus proyectos.</p>
        <RouterLink to="/projects" class="inline-block text-center bg-slate-100 text-slate-900 font-bold py-2 px-4 rounded hover:bg-slate-200 transition-colors">
          Ver repositorios
        </RouterLink>
      </article>

      <article class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col gap-3">
        <h2 class="text-lg font-semibold text-slate-900">Analisis</h2>
        <p class="text-slate-500 flex-1">Ejecuta analisis sobre repositorios vinculados.</p>
        <RouterLink to="/projects" class="inline-block text-center bg-slate-100 text-slate-900 font-bold py-2 px-4 rounded hover:bg-slate-200 transition-colors">
          Ver analisis
        </RouterLink>
      </article>
    </section>

    <section v-if="user" class="max-w-6xl mx-auto flex items-center gap-4">
      <p class="text-slate-700">
        Sesion activa: <strong class="font-semibold">{{ user.email }}</strong>
      </p>
      <button
        class="bg-slate-100 text-slate-900 font-bold py-2 px-4 rounded hover:bg-slate-200 transition-colors"
        type="button"
        @click="handleSignOut"
      >
        Cerrar sesion
      </button>
    </section>
  </main>
</template>