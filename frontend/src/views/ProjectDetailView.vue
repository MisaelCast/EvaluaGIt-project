<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import {
  analyzeRepository,
  type AnalysisRunResponse,
} from '@/services/analysis'
import {
  createRepository,
  deleteRepository,
  getProjectRepositories,
  type RepositoryResponse,
} from '@/services/repositories'
import { getProject, type ProjectResponse } from '@/services/projects'

const route = useRoute()
const projectId = route.params.projectId as string

const project = ref<ProjectResponse | null>(null)
const repositories = ref<RepositoryResponse[]>([])
const repositoriesLoading = ref(false)
const repositoriesError = ref('')
const creatingRepo = ref(false)
const newRepoUrl = ref('')
const newRepoBranch = ref('main')

const analyzingRepositoryId = ref<string | null>(null)
const analysisResult = ref<AnalysisRunResponse | null>(null)
const analysisError = ref('')

onMounted(() => {
  void loadProject()
  void loadRepositories()
})

async function loadProject() {
  try {
    project.value = await getProject(projectId)
  } catch {
    project.value = null
  }
}

async function loadRepositories() {
  repositoriesLoading.value = true
  repositoriesError.value = ''

  try {
    repositories.value = await getProjectRepositories(projectId)
  } catch (err) {
    repositories.value = []
    repositoriesError.value =
      err instanceof Error ? err.message : 'No se pudieron cargar los repositorios'
  } finally {
    repositoriesLoading.value = false
  }
}

async function handleCreateRepository() {
  const repoUrl = newRepoUrl.value.trim()
  const branch = newRepoBranch.value.trim() || 'main'

  if (!repoUrl) {
    repositoriesError.value = 'La URL del repositorio es obligatoria'
    return
  }

  creatingRepo.value = true
  repositoriesError.value = ''

  try {
    await createRepository({
      project_id: projectId,
      repo_url: repoUrl,
      branch,
    })
    newRepoUrl.value = ''
    newRepoBranch.value = 'main'
    await loadRepositories()
  } catch (err) {
    repositoriesError.value =
      err instanceof Error ? err.message : 'No se pudo vincular el repositorio'
  } finally {
    creatingRepo.value = false
  }
}

async function handleDeleteRepository(repo: RepositoryResponse) {
  const confirmed = window.confirm(
    `¿Eliminar el repositorio ${repo.repo_url}?`,
  )
  if (!confirmed) return

  repositoriesError.value = ''

  try {
    await deleteRepository(repo.id)
    analysisResult.value = null
    analysisError.value = ''
    await loadRepositories()
  } catch (err) {
    repositoriesError.value =
      err instanceof Error ? err.message : 'No se pudo eliminar el repositorio'
  }
}

async function handleAnalyze(repo: RepositoryResponse) {
  analyzingRepositoryId.value = repo.id
  analysisError.value = ''
  analysisResult.value = null

  try {
    const result = await analyzeRepository(repo.id)
    analysisResult.value = result
    await loadRepositories()
  } catch (err) {
    analysisError.value =
      err instanceof Error ? err.message : 'No se pudo analizar el repositorio'
  } finally {
    analyzingRepositoryId.value = null
  }
}

function getStatusClass(status: string): string {
  switch (status) {
    case 'LINKED':
      return 'status-linked'
    case 'ANALYZING':
      return 'status-analyzing'
    case 'ANALYZED':
      return 'status-analyzed'
    case 'FAILED':
      return 'status-failed'
    default:
      return 'status-unknown'
  }
}

function formatDate(value: string | null): string {
  if (!value) return 'Sin fecha'

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
  }).format(new Date(value))
}
</script>

<template>
  <main class="page">
    <header class="header">
      <div>
        <h1>Detalle del proyecto</h1>
        <p v-if="project" class="project-name">{{ project.name }}</p>
      </div>
      <RouterLink to="/projects" class="back-link">Volver a proyectos</RouterLink>
    </header>

    <section class="card">
      <div class="section-title">
        <h2>Repositorios</h2>
      </div>

      <form class="repo-form" @submit.prevent="handleCreateRepository">
        <label class="field">
          <span>URL del repositorio</span>
          <input
            v-model="newRepoUrl"
            type="text"
            placeholder="https://github.com/usuario/repositorio"
            autocomplete="off"
          />
        </label>

        <label class="field field-small">
          <span>Rama</span>
          <input
            v-model="newRepoBranch"
            type="text"
            placeholder="main"
            autocomplete="off"
          />
        </label>

        <button class="button primary" type="submit" :disabled="creatingRepo">
          {{ creatingRepo ? 'Vinculando...' : 'Vincular repositorio' }}
        </button>
      </form>

      <p v-if="repositoriesError" class="error-text">{{ repositoriesError }}</p>

      <div v-if="repositoriesLoading" class="muted">
        Cargando repositorios...
      </div>

      <div v-else-if="repositories.length" class="repositories-list">
        <article
          v-for="repo in repositories"
          :key="repo.id"
          class="repo-card"
        >
          <div class="repo-info">
            <p class="repo-url">{{ repo.repo_url }}</p>
            <div class="repo-meta">
              <span
                class="status-pill"
                :class="getStatusClass(repo.status)"
              >{{ repo.status }}</span>
              <span>Rama: {{ repo.branch }}</span>
              <span v-if="repo.last_commit_hash">
                Commit: {{ repo.last_commit_hash.substring(0, 7) }}
              </span>
              <span v-if="repo.last_analyzed_at">
                Analizado: {{ formatDate(repo.last_analyzed_at) }}
              </span>
            </div>
          </div>
          <div class="repo-actions">
            <button
              class="button analyze-button"
              type="button"
              :disabled="analyzingRepositoryId === repo.id || repo.status === 'ANALYZING'"
              @click="handleAnalyze(repo)"
            >
              {{ analyzingRepositoryId === repo.id || repo.status === 'ANALYZING' ? 'Analizando...' : 'Analizar' }}
            </button>
            <button
              class="button danger-button"
              type="button"
              @click="handleDeleteRepository(repo)"
            >
              Eliminar
            </button>
          </div>
        </article>
      </div>

      <p v-else-if="!repositoriesError" class="muted">
        Este proyecto aun no tiene repositorios vinculados.
      </p>

      <div v-if="analysisResult || analysisError" class="analysis-result-section">
        <h3>Resultado del ultimo analisis</h3>

        <p v-if="analysisError" class="error-text">{{ analysisError }}</p>

        <div v-if="analysisResult" class="analysis-data">
          <div class="analysis-info">
            <span><strong>Status:</strong> {{ analysisResult.status }}</span>
            <span v-if="analysisResult.commit_hash">
              <strong>Commit:</strong> {{ analysisResult.commit_hash.substring(0, 7) }}
            </span>
            <span v-if="analysisResult.started_at">
              <strong>Iniciado:</strong> {{ formatDate(analysisResult.started_at) }}
            </span>
            <span v-if="analysisResult.finished_at">
              <strong>Finalizado:</strong> {{ formatDate(analysisResult.finished_at) }}
            </span>
            <span v-if="analysisResult.error_message" class="error-text">
              <strong>Error:</strong> {{ analysisResult.error_message }}
            </span>
          </div>

          <div v-if="analysisResult.id" class="analysis-link">
            <RouterLink
              :to="`/projects/${projectId}/analysis/${analysisResult.id}`"
              class="button secondary"
            >
              Ver analisis completo
            </RouterLink>
          </div>

          <pre v-if="analysisResult.result_json" class="result-json">{{ JSON.stringify(analysisResult.result_json, null, 2) }}</pre>
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

.header > div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

h1 {
  margin: 0;
  font-size: 2rem;
}

.project-name {
  margin: 0;
  color: #5d6962;
  font-size: 1rem;
}

.back-link {
  color: #2f8f5b;
  text-decoration: none;
  font-weight: 700;
  font-size: 0.9rem;
}

.back-link:hover {
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

.section-title {
  margin-bottom: 18px;
}

.section-title h2 {
  margin: 0;
  font-size: 1.05rem;
}

.repo-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
  padding: 16px;
  background: #fbfcfb;
  border: 1px solid #dfe6e1;
  border-radius: 8px;
  margin-bottom: 18px;
}

.repo-form .field {
  flex: 1;
  min-width: 200px;
}

.field-small {
  flex: 0 0 120px !important;
}

.repo-form .button {
  flex-shrink: 0;
}

.field {
  display: grid;
  gap: 8px;
  color: #4b5650;
  font-size: 0.88rem;
  font-weight: 700;
}

.field input {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #cfd8d2;
  border-radius: 6px;
  padding: 10px 12px;
  color: #17201b;
  font: inherit;
}

.field input:focus {
  border-color: #2f8f5b;
  outline: 2px solid #d9f0e4;
}

.repositories-list {
  display: grid;
  gap: 12px;
}

.repo-card {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  border: 1px solid #dfe6e1;
  border-radius: 8px;
  padding: 14px 16px;
  background: #ffffff;
}

.repo-info {
  flex: 1;
  min-width: 0;
}

.repo-url {
  margin: 0 0 8px;
  font-size: 0.9rem;
  font-weight: 600;
  word-break: break-all;
}

.repo-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  color: #6c7770;
  font-size: 0.82rem;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 700;
}

.status-linked {
  background: #eef1ef;
  color: #5d6962;
}

.status-analyzing {
  background: #fff3e0;
  color: #b25a00;
}

.status-analyzed {
  background: #e3f5eb;
  color: #17633d;
}

.status-failed {
  background: #fde8e8;
  color: #9b2525;
}

.status-unknown {
  background: #eef1ef;
  color: #5d6962;
}

.repo-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.analyze-button {
  background: #e3f5eb;
  color: #17633d;
}

.analyze-button:hover:not(:disabled) {
  background: #cce9db;
}

.danger-button {
  background: #fde8e8;
  color: #9b2525;
}

.danger-button:hover {
  background: #f8cdcd;
}

.analysis-result-section {
  margin-top: 24px;
  padding: 16px;
  background: #fbfcfb;
  border: 1px solid #dfe6e1;
  border-radius: 8px;
}

.analysis-result-section h3 {
  margin: 0 0 14px;
  font-size: 0.95rem;
}

.analysis-info {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  margin-bottom: 14px;
  font-size: 0.88rem;
  color: #4b5650;
}

.analysis-link {
  margin-bottom: 14px;
}

.result-json {
  margin: 0;
  padding: 14px;
  background: #1e1e1e;
  color: #d4d4d4;
  border-radius: 6px;
  font-size: 0.8rem;
  overflow-x: auto;
  line-height: 1.5;
}

.button {
  border: 0;
  border-radius: 6px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  text-align: center;
}

.button.primary {
  background: #2f8f5b;
  color: #ffffff;
}

.button.secondary {
  background: #eef1ef;
  color: #17201b;
}

.button:hover {
  filter: brightness(0.96);
}

.button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
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
    gap: 12px;
  }

  .repo-form {
    flex-direction: column;
    align-items: stretch;
  }

  .repo-form .field {
    min-width: unset;
  }

  .field-small {
    flex: unset !important;
  }

  .repo-form .button {
    width: 100%;
  }

  .repo-card {
    flex-direction: column;
  }

  .repo-actions {
    width: 100%;
    flex-direction: column;
  }
}
</style>