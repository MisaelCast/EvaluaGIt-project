<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getAnalysisRun, type AnalysisRunResponse } from '@/services/analysis'

const route = useRoute()
const projectId = route.params.projectId as string
const analysisRunId = route.params.analysisRunId as string

const loading = ref(true)
const error = ref('')
const analysisRun = ref<AnalysisRunResponse | null>(null)

onMounted(() => {
  void loadAnalysis()
})

async function loadAnalysis() {
  loading.value = true
  error.value = ''

  try {
    analysisRun.value = await getAnalysisRun(analysisRunId)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'No se pudo cargar el analisis'
  } finally {
    loading.value = false
  }
}

function formatDate(value: string | null): string {
  if (!value) return 'Sin fecha'

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function getResult() {
  return analysisRun.value?.result_json as Record<string, unknown> | null
}

function getRequiredFiles() {
  const result = getResult()
  if (!result) return { found: [] as string[], missing: [] as string[] }
  const rf = result.required_files as Record<string, unknown> | null
  return {
    found: (rf?.found as string[] | null) || [],
    missing: (rf?.missing as string[] | null) || [],
  }
}

function getForbiddenFiles() {
  const result = getResult()
  if (!result) return [] as string[]
  const ff = result.forbidden_files as Record<string, unknown> | null
  return (ff?.found as string[] | null) || []
}

function getWarnings() {
  const result = getResult()
  if (!result) return [] as string[]
  return (result.warnings as string[] | null) || []
}

function getScore() {
  const result = getResult()
  if (!result) return null
  const score = result.score as Record<string, unknown> | null
  if (!score) return null
  return score.structure as number | null
}

function getDependencies() {
  const result = getResult()
  if (!result) return [] as string[]
  return (result.dependencies as string[] | null) || []
}
</script>

<template>
  <main class="page">
    <header class="header">
      <h1>Resultado de analisis</h1>
      <nav class="nav-links">
        <RouterLink :to="`/projects/${projectId}`" class="link">
          Volver al proyecto
        </RouterLink>
        <RouterLink to="/projects" class="link">
          Volver a proyectos
        </RouterLink>
      </nav>
    </header>

    <section class="card">
      <p v-if="loading" class="muted">Cargando analisis...</p>
      <p v-else-if="error" class="error-text">{{ error }}</p>

      <div v-else-if="analysisRun">
        <div class="info-grid">
          <div class="info-item">
            <span class="label">Status</span>
            <span class="value">{{ analysisRun.status }}</span>
          </div>
          <div v-if="analysisRun.commit_hash" class="info-item">
            <span class="label">Commit</span>
            <span class="value commit">{{ analysisRun.commit_hash.substring(0, 7) }}</span>
          </div>
          <div class="info-item">
            <span class="label">Iniciado</span>
            <span class="value">{{ formatDate(analysisRun.started_at) }}</span>
          </div>
          <div class="info-item">
            <span class="label">Finalizado</span>
            <span class="value">{{ formatDate(analysisRun.finished_at) }}</span>
          </div>
        </div>

        <p v-if="analysisRun.error_message" class="error-box">
          {{ analysisRun.error_message }}
        </p>

        <div class="result-sections">
          <div class="result-section">
            <h3>Resumen</h3>
            <div class="summary-grid">
              <div class="summary-item">
                <span class="label">Lenguaje</span>
                <span class="value">{{ getResult()?.language || 'No detectado' }}</span>
              </div>
              <div class="summary-item">
                <span class="label">Framework</span>
                <span class="value">{{ getResult()?.framework || 'No detectado' }}</span>
              </div>
              <div class="summary-item">
                <span class="label">Tiene README</span>
                <span class="value">{{ getResult()?.has_readme ? 'Si' : 'No' }}</span>
              </div>
              <div class="summary-item">
                <span class="label">Score estructura</span>
                <span class="value">{{ getScore() !== null ? `${getScore()}%` : 'N/A' }}</span>
              </div>
            </div>
          </div>

          <div class="result-section">
            <h3>Dependencias</h3>
            <ul v-if="getDependencies().length" class="list">
              <li v-for="dep in getDependencies()" :key="dep">{{ dep }}</li>
            </ul>
            <p v-else class="muted">Sin dependencias detectadas</p>
          </div>

          <div class="result-section">
            <h3>Archivos requeridos</h3>
            <div v-if="getRequiredFiles().found.length" class="list-group">
              <p class="label-sm">Encontrados:</p>
              <ul class="list success-list">
                <li v-for="file in getRequiredFiles().found" :key="file">{{ file }}</li>
              </ul>
            </div>
            <div v-if="getRequiredFiles().missing.length" class="list-group">
              <p class="label-sm">Faltantes:</p>
              <ul class="list error-list">
                <li v-for="file in getRequiredFiles().missing" :key="file">{{ file }}</li>
              </ul>
            </div>
            <p v-if="!getRequiredFiles().found.length && !getRequiredFiles().missing.length" class="muted">
              Sin informacion de archivos requeridos
            </p>
          </div>

          <div class="result-section">
            <h3>Archivos prohibidos</h3>
            <ul v-if="getForbiddenFiles().length" class="list error-list">
              <li v-for="file in getForbiddenFiles()" :key="file">{{ file }}</li>
            </ul>
            <p v-else class="muted">No se encontraron archivos prohibidos</p>
          </div>

          <div class="result-section">
            <h3>Advertencias</h3>
            <ul v-if="getWarnings().length" class="list warning-list">
              <li v-for="w in getWarnings()" :key="w">{{ w }}</li>
            </ul>
            <p v-else class="muted">Sin advertencias</p>
          </div>

          <div class="result-section">
            <h3>JSON completo</h3>
            <pre class="json-block">{{ JSON.stringify(analysisRun.result_json, null, 2) }}</pre>
          </div>
        </div>
      </div>
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
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
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
}

.commit {
  font-family: monospace;
  background: #f3f5f4;
  padding: 2px 6px;
  border-radius: 4px;
}

.error-box {
  margin: 0 0 24px;
  padding: 14px;
  background: #fde8e8;
  border: 1px solid #f8cdcd;
  border-radius: 6px;
  color: #9b2525;
  line-height: 1.6;
}

.result-sections {
  display: grid;
  gap: 24px;
}

.result-section {
  padding-top: 20px;
  border-top: 1px solid #dfe6e1;
}

.result-section h3 {
  margin: 0 0 14px;
  font-size: 1rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.summary-item {
  display: grid;
  gap: 4px;
}

.label-sm {
  margin: 0 0 6px;
  color: #6c7770;
  font-size: 0.82rem;
  font-weight: 700;
}

.list-group {
  margin-bottom: 10px;
}

.list {
  margin: 0;
  padding-left: 20px;
}

.list li {
  margin-bottom: 4px;
  font-size: 0.9rem;
}

.success-list li {
  color: #17633d;
}

.error-list li {
  color: #9b2525;
}

.warning-list li {
  color: #b25a00;
}

.json-block {
  margin: 0;
  padding: 14px;
  background: #1e1e1e;
  color: #d4d4d4;
  border-radius: 6px;
  font-size: 0.8rem;
  overflow-x: auto;
  line-height: 1.5;
}

.muted {
  color: #5d6962;
  line-height: 1.6;
}

.error-text {
  color: #9b2525;
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