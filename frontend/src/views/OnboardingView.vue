<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { updateMyRole } from '@/services/users'

const router = useRouter()
const loading = ref(false)
const error = ref('')

async function selectRole(role: 'PROFESSOR' | 'STUDENT') {
  loading.value = true
  error.value = ''

  try {
    await updateMyRole(role)
    if (role === 'PROFESSOR') {
      router.push('/dashboard')
    } else {
      router.push('/student/dashboard')
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error al seleccionar rol'
    loading.value = false
  }
}
</script>

<template>
  <main class="min-h-screen bg-slate-50 flex items-center justify-center px-6 py-12">
    <div class="max-w-lg w-full text-center">
      <h1 class="text-3xl font-bold text-slate-900 mb-3">¿Cómo usarás EvaluaGit?</h1>
      <p class="text-slate-500 mb-8">
        Selecciona tu rol para personalizar tu experiencia en la plataforma.
      </p>

      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-6">
        {{ error }}
      </div>

      <div class="space-y-4">
        <button
          type="button"
          :disabled="loading"
          class="w-full p-6 bg-white border-2 border-slate-200 rounded-xl text-left hover:border-emerald-500 hover:shadow-md transition-all disabled:opacity-50"
          @click="selectRole('PROFESSOR')"
        >
          <div class="flex items-center gap-3 mb-2">
            <span class="text-2xl">👨‍🏫</span>
            <h2 class="text-xl font-semibold text-slate-900">Soy profesor</h2>
          </div>
          <p class="text-slate-500 text-sm">
            Crear proyectos, configurar requerimientos y revisar repositorios.
          </p>
        </button>

        <button
          type="button"
          :disabled="loading"
          class="w-full p-6 bg-white border-2 border-slate-200 rounded-xl text-left hover:border-emerald-500 hover:shadow-md transition-all disabled:opacity-50"
          @click="selectRole('STUDENT')"
        >
          <div class="flex items-center gap-3 mb-2">
            <span class="text-2xl">👨‍🎓</span>
            <h2 class="text-xl font-semibold text-slate-900">Soy alumno</h2>
          </div>
          <p class="text-slate-500 text-sm">
            Unirme a proyectos y vincular mis repositorios.
          </p>
        </button>
      </div>
    </div>
  </main>
</template>