<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import AiAnalysisResult from '@/components/AiAnalysisResult.vue'
import {
  analyzeRepositoryWithAi,
  getLatestAiAnalysis,
  type AiAnalysisRunResponse,
  type AiAnalysisResponse,
} from '@/services/aiAnalysis'
import {
  analyzeRepository,
  type AnalysisRunResponse,
} from '@/services/analysis'
import {
  deleteRepository,
  getProjectRepositories,
  type RepositoryWithStudent,
} from '@/services/repositories'
import { getProject, type ProjectResponse } from '@/services/projects'
import {
  analyzeProjectSimilarity,
  type SimilarityAnalysisResponse,
} from '@/services/similarity'

const route = useRoute()
const projectId = route.params.projectId as string

const project = ref<ProjectResponse | null>(null)
const repositories = ref<RepositoryWithStudent[]>([])
const repositoriesLoading = ref(false)
const repositoriesError = ref('')

const analyzingRepositoryId = ref<string | null>(null)
const analysisResult = ref<AnalysisRunResponse | null>(null)
const analysisError = ref('')
const aiAnalysisRun = ref<AiAnalysisRunResponse | null>(null)
const aiAnalysisResult = ref<AiAnalysisResponse | null>(null)
const aiAnalysisError = ref('')
const aiAnalyzingRepositoryId = ref<string | null>(null)
const aiLoadingLatestRepositoryId = ref<string | null>(null)
const similarityResult = ref<SimilarityAnalysisResponse | null>(null)
const similarityError = ref('')
const analyzingSimilarity = ref(false)
const failedAvatars = ref<Set<string>>(new Set())

function handleAvatarError(studentId: string) {
  failedAvatars.value.add(studentId)
}

function avatarHasFailed(studentId: string): boolean {
  return failedAvatars.value.has(studentId)
}

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
      err instanceof Error ? err.message : 'No se pudieron cargar las entregas'
  } finally {
    repositoriesLoading.value = false
  }
}

async function handleDeleteRepository(repo: RepositoryWithStudent) {
  const confirmed = window.confirm(
    `¿Eliminar el repositorio ${repo.repo_url}?`,
  )
  if (!confirmed) return

  repositoriesError.value = ''

  try {
    await deleteRepository(repo.id)
    analysisResult.value = null
    analysisError.value = ''
    aiAnalysisRun.value = null
    aiAnalysisResult.value = null
    aiAnalysisError.value = ''
    similarityResult.value = null
    similarityError.value = ''
    await loadRepositories()
  } catch (err) {
    repositoriesError.value =
      err instanceof Error ? err.message : 'No se pudo eliminar el repositorio'
  }
}

async function handleAnalyze(repo: RepositoryWithStudent) {
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

async function handleAiAnalysis(repo: RepositoryWithStudent) {
  aiAnalyzingRepositoryId.value = repo.id
  aiAnalysisError.value = ''
  aiAnalysisRun.value = null
  aiAnalysisResult.value = null

  try {
    const result = await analyzeRepositoryWithAi(repo.id)
    aiAnalysisRun.value = result
    aiAnalysisResult.value = result.result_json
  } catch (err) {
    aiAnalysisError.value =
      err instanceof Error ? err.message : 'No se pudo completar el analisis IA'
  } finally {
    aiAnalyzingRepositoryId.value = null
  }
}

async function handleLatestAiAnalysis(repo: RepositoryWithStudent) {
  aiLoadingLatestRepositoryId.value = repo.id
  aiAnalysisError.value = ''
  aiAnalysisRun.value = null
  aiAnalysisResult.value = null

  try {
    const result = await getLatestAiAnalysis(repo.id)
    aiAnalysisRun.value = result
    aiAnalysisResult.value = result.result_json
  } catch (err) {
    const message = err instanceof Error ? err.message : 'No se pudo cargar el analisis IA'
    aiAnalysisError.value =
      message === 'No hay analisis IA para este repositorio'
        ? 'Este repositorio aun no tiene analisis IA'
        : message
  } finally {
    aiLoadingLatestRepositoryId.value = null
  }
}

async function handleSimilarityAnalysis() {
  if (!project.value) return

  analyzingSimilarity.value = true
  similarityError.value = ''
  similarityResult.value = null

  try {
    similarityResult.value = await analyzeProjectSimilarity(project.value.id)
  } catch (err) {
    similarityError.value =
      err instanceof Error ? err.message : 'No se pudo analizar la similitud'
  } finally {
    analyzingSimilarity.value = false
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
        <p v-if="project?.join_code" class="join-code-display">
          Codigo para alumnos: <code>{{ project.join_code }}</code>
          <span class="join-code-hint">Comparti este codigo con tus alumnos para que se unan al proyecto.</span>
        </p>
      </div>
      <RouterLink to="/projects" class="back-link">Volver a proyectos</RouterLink>
    </header>

    <section class="card">
      <div class="section-title">
        <h2>Entregas</h2>
        <div class="flex flex-col items-end gap-2 sm:flex-row sm:items-center">
          <button
            class="button primary"
            type="button"
            :disabled="analyzingSimilarity || repositories.length < 2"
            @click="handleSimilarityAnalysis"
          >
            {{ analyzingSimilarity ? 'Analizando similitud...' : 'Analizar similitud' }}
          </button>
          <RouterLink
            :to="`/projects/${projectId}/settings`"
            class="settings-link"
          >
            Configurar requerimientos
          </RouterLink>
        </div>
      </div>
      <p
        v-if="repositories.length < 2"
        class="mb-4 text-sm text-slate-500"
      >
        Se necesitan al menos 2 entregas para analizar similitud
      </p>

      <p v-if="repositoriesError" class="error-text">{{ repositoriesError }}</p>

      <div v-if="repositoriesLoading" class="muted">
        Cargando entregas...
      </div>

      <div v-else-if="repositories.length" class="repositories-list">
        <p class="entregas-count">Entregas recibidas: {{ repositories.length }}</p>
        <article
          v-for="repo in repositories"
          :key="repo.id"
          class="repo-card"
        >
          <div class="repo-info">
            <div class="student-info">
              <img
                v-if="repo.student.avatar_url && !avatarHasFailed(repo.student.id)"
                :src="repo.student.avatar_url"
                :alt="repo.student.full_name"
                class="student-avatar"
                @error="handleAvatarError(repo.student.id)"
              />
              <div v-else class="student-avatar-placeholder">
                {{ repo.student.full_name.charAt(0).toUpperCase() }}
              </div>
              <div>
                <p class="student-name">{{ repo.student.full_name }}</p>
                <p class="student-email">{{ repo.student.email }}</p>
              </div>
            </div>
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
              class="button ai-button"
              type="button"
              :disabled="aiAnalyzingRepositoryId === repo.id || aiLoadingLatestRepositoryId === repo.id"
              @click="handleAiAnalysis(repo)"
            >
              {{ aiAnalyzingRepositoryId === repo.id ? 'Analizando con IA...' : 'Analizar con IA' }}
            </button>
            <button
              class="button secondary"
              type="button"
              :disabled="aiAnalyzingRepositoryId === repo.id || aiLoadingLatestRepositoryId === repo.id"
              @click="handleLatestAiAnalysis(repo)"
            >
              {{ aiLoadingLatestRepositoryId === repo.id ? 'Cargando IA...' : 'Ver ultimo IA' }}
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
        Este proyecto aun no tiene entregas de alumnos.
      </p>

      <section
        v-if="similarityResult || similarityError"
        class="mt-6 rounded-lg border border-slate-200 bg-white p-5"
      >
        <h3 class="text-base font-semibold text-slate-950">Resultado del analisis de similitud</h3>

        <p
          v-if="similarityError"
          class="mt-3 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700"
        >
          {{ similarityError }}
        </p>

        <div v-if="similarityResult" class="mt-4 space-y-4">
          <div class="grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
            <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
              <p class="text-xs font-semibold uppercase text-slate-500">Proveedor</p>
              <p class="mt-1 font-semibold text-slate-950">{{ similarityResult.provider }}</p>
            </div>
            <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
              <p class="text-xs font-semibold uppercase text-slate-500">Estado</p>
              <p class="mt-1 font-semibold text-slate-950">{{ similarityResult.status }}</p>
            </div>
            <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
              <p class="text-xs font-semibold uppercase text-slate-500">Entregas encontradas</p>
              <p class="mt-1 font-semibold text-slate-950">{{ similarityResult.repositories_count }}</p>
            </div>
            <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
              <p class="text-xs font-semibold uppercase text-slate-500">Ejecucion</p>
              <p class="mt-1 font-semibold text-slate-950">
                {{ similarityResult.executed ? 'Ejecutado' : 'Pendiente' }}
              </p>
            </div>
          </div>

          <p class="rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
            {{ similarityResult.message }}
          </p>

          <p
            v-if="!similarityResult.executed"
            class="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm font-medium text-amber-800"
          >
            Dolos todavia no se ha ejecutado en este paso
          </p>

          <div>
            <h4 class="text-sm font-semibold text-slate-950">Entregas que se compararian</h4>
            <div class="mt-3 grid gap-3">
              <article
                v-for="repo in similarityResult.repositories"
                :key="repo.repository_id"
                class="rounded-lg border border-slate-200 bg-slate-50 p-4"
              >
                <div class="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p class="font-semibold text-slate-950">
                      {{ repo.student_name || 'Alumno sin nombre' }}
                    </p>
                    <p class="text-sm text-slate-500">{{ repo.student_email || 'Correo no disponible' }}</p>
                  </div>
                  <span class="mt-1 w-fit rounded-full bg-slate-200 px-3 py-1 text-xs font-semibold text-slate-700">
                    Rama {{ repo.branch }}
                  </span>
                </div>
                <p class="mt-3 break-all font-mono text-xs text-slate-600">{{ repo.repo_url }}</p>
              </article>
            </div>
          </div>
        </div>
      </section>

      <div v-if="analysisResult || analysisError" class="analysis-result-section">
        <h3>Resultado del ultimo analisis</h3>

        <p v-if="analysisError" class="error-text">{{ analysisError }}</p>

        <div v-if="analysisResult" class="analysis-data">
          <div class="analysis-info">
            <span><strong>Estado:</strong> {{ analysisResult.status }}</span>
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

      <div v-if="aiAnalysisRun || aiAnalysisResult || aiAnalysisError" class="mt-6">
        <p v-if="aiAnalysisError" class="error-text">{{ aiAnalysisError }}</p>
        <AiAnalysisResult
          v-if="aiAnalysisRun || aiAnalysisResult"
          :result="aiAnalysisResult"
          :status="aiAnalysisRun?.status"
          :created-at="aiAnalysisRun?.created_at"
          :finished-at="aiAnalysisRun?.finished_at"
        />
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

.join-code-display {
  margin: 4px 0 0;
  font-size: 0.9rem;
  color: #17633d;
}

.join-code-display code {
  background: #e3f5eb;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: monospace;
  font-weight: 700;
}

.join-code-hint {
  display: block;
  font-size: 0.8rem;
  font-weight: normal;
  color: #5d6962;
  margin-top: 2px;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.section-title h2 {
  margin: 0;
  font-size: 1.05rem;
}

.entregas-count {
  margin: 0 0 14px;
  font-size: 0.88rem;
  color: #5d6962;
}

.settings-link {
  color: #2f8f5b;
  text-decoration: none;
  font-weight: 700;
  font-size: 0.85rem;
}

.settings-link:hover {
  text-decoration: underline;
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

.student-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.student-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
}

.student-avatar-placeholder {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e3f5eb;
  color: #17633d;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
}

.student-name {
  margin: 0;
  font-weight: 600;
  font-size: 0.9rem;
}

.student-email {
  margin: 0;
  font-size: 0.8rem;
  color: #6c7770;
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

.ai-button {
  background: #e8eefc;
  color: #244579;
}

.ai-button:hover:not(:disabled) {
  background: #d6e2fa;
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

  .repo-card {
    flex-direction: column;
  }

  .repo-actions {
    width: 100%;
    flex-direction: column;
  }
}
</style>
