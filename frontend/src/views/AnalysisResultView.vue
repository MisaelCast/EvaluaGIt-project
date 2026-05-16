<script setup lang="ts">
import { useRoute } from 'vue-router'
import { RouterLink } from 'vue-router'

const route = useRoute()
const projectId = route.params.projectId as string
const analysisRunId = route.params.analysisRunId as string
</script>

<template>
  <main class="page">
    <header class="header">
      <h1>Resultado de analisis</h1>
      <nav class="nav-links">
        <RouterLink :to="`/projects/${projectId}`" class="link">Volver al proyecto</RouterLink>
        <RouterLink to="/projects" class="link">Volver a proyectos</RouterLink>
      </nav>
    </header>

    <section class="card">
      <div class="info-grid">
        <div class="info-item">
          <span class="label">Proyecto</span>
          <span class="value">{{ projectId }}</span>
        </div>
        <div class="info-item">
          <span class="label">Analisis ID</span>
          <span class="value">{{ analysisRunId }}</span>
        </div>
      </div>

      <p class="notice">
        La vista completa de analisis se implementara cuando exista endpoint
        para consultar AnalysisRun por ID.
      </p>
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
  display: flex;
  justify-content: space-between;
  align-items: center;
}

h1 {
  margin: 0;
  font-size: 2rem;
}

.nav-links {
  display: flex;
  gap: 16px;
}

.link {
  color: #2f8f5b;
  text-decoration: none;
  font-weight: 700;
  font-size: 0.9rem;
}

.link:hover {
  text-decoration: underline;
}

.card {
  max-width: 1080px;
  margin: 0 auto;
  background: #ffffff;
  border: 1px solid #dfe6e1;
  border-radius: 8px;
  padding: 22px;
  box-shadow: 0 10px 30px rgb(25 35 30 / 6%);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.info-item {
  display: grid;
  gap: 4px;
}

.label {
  color: #6c7770;
  font-size: 0.82rem;
  font-weight: 700;
}

.value {
  color: #17201b;
  font-size: 0.95rem;
  word-break: break-all;
}

.notice {
  margin: 0;
  padding: 16px;
  background: #fff3e0;
  border: 1px solid #ffe0b2;
  border-radius: 6px;
  color: #b25a00;
  line-height: 1.6;
}

@media (max-width: 760px) {
  .page {
    padding: 28px 18px;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .nav-links {
    flex-direction: column;
    gap: 8px;
  }
}
</style>