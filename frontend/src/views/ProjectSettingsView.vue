<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const projectId = route.params.projectId
</script>

<template>
  <main class="page">
    <header class="header">
      <h1>Configuracion del proyecto</h1>
    </header>

    <section class="content">
      <p class="muted">Proyecto ID: {{ projectId }}</p>
      <p class="muted">Aqui se configuraran requerimientos del proyecto.</p>
    </section>
  </main>
</template>

<style scoped>
.page {
  min-height: 100vh;
  padding: 48px;
  background: #f3f5f4;
  color: #17201b;
}

.header {
  max-width: 1080px;
  margin: 0 auto 28px;
}

h1 {
  margin: 0;
  font-size: 2rem;
}

.content {
  max-width: 1080px;
  margin: 0 auto;
}

.muted {
  color: #5d6962;
}
</style>