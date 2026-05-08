<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getHealth, type HealthResponse } from '@/services/api'

const loading = ref(true)
const error = ref('')
const health = ref<HealthResponse | null>(null)

onMounted(async () => {
  try {
    health.value = await getHealth()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error desconocido'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="home">
    <h1>EVALUGIT</h1>
    <p v-if="loading">Conectando con el backend...</p>
    <p v-else-if="error">Backend status: error</p>
    <p v-else>Backend status: conectado</p>
    <p v-if="health">Respuesta: {{ health.status }}</p>
    <p v-if="error">{{ error }}</p>
  </section>
</template>

<style scoped>
.home {
  padding: 2rem;
}
</style>
