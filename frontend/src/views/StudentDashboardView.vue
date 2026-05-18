<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <main class="min-h-screen bg-slate-50 flex items-center justify-center px-6 py-12">
    <div class="max-w-lg w-full text-center">
      <h1 class="text-3xl font-bold text-slate-900 mb-3">Panel de alumno</h1>
      <p class="text-slate-500 mb-8">
        Aquí podrás unirte a proyectos y vincular tus repositorios.
      </p>
      <RouterLink
        to="/"
        class="inline-flex items-center gap-2 text-emerald-600 hover:text-emerald-700 font-semibold"
      >
        Volver al inicio
      </RouterLink>
    </div>
  </main>
</template>