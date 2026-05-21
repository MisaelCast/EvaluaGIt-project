<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
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
        <RouterLink
          :to="`/projects/${projectId}/settings`"
          class="settings-link"
        >
          Configurar requerimientos
        </RouterLink>
      </div>

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

      <div v-if="aiAnalysisResult || aiAnalysisError" class="ai-result-section">
        <h3>Resultado del analisis IA</h3>

        <p v-if="aiAnalysisError" class="error-text">{{ aiAnalysisError }}</p>

        <div v-if="aiAnalysisRun" class="ai-meta">
          <span><strong>Status:</strong> {{ aiAnalysisRun.status }}</span>
          <span><strong>Creado:</strong> {{ formatDate(aiAnalysisRun.created_at) }}</span>
          <span v-if="aiAnalysisRun.finished_at">
            <strong>Finalizado:</strong> {{ formatDate(aiAnalysisRun.finished_at) }}
          </span>
          <span v-if="aiAnalysisRun.error_message" class="error-text">
            <strong>Error:</strong> {{ aiAnalysisRun.error_message }}
          </span>
        </div>

        <div v-if="aiAnalysisResult" class="ai-data">
          <p v-if="aiAnalysisResult.enabled === false && aiAnalysisResult.message" class="muted">
            {{ aiAnalysisResult.message }}
          </p>

          <p v-if="aiAnalysisResult.error" class="ai-error">
            {{ aiAnalysisResult.error }}
          </p>

          <div class="ai-meta">
            <span><strong>Provider:</strong> {{ aiAnalysisResult.provider }}</span>
            <span v-if="aiAnalysisResult.files_count !== null">
              <strong>Archivos:</strong> {{ aiAnalysisResult.files_count }}
            </span>
            <span v-if="aiAnalysisResult.quality_score !== null">
              <strong>Quality score:</strong> {{ aiAnalysisResult.quality_score }}
            </span>
            <span v-if="aiAnalysisResult.risk_level">
              <strong>Riesgo:</strong> {{ aiAnalysisResult.risk_level }}
            </span>
          </div>

          <p v-if="aiAnalysisResult.summary" class="ai-summary">
            {{ aiAnalysisResult.summary }}
          </p>

          <section v-if="aiAnalysisResult.strengths.length" class="ai-block">
            <h4>Fortalezas</h4>
            <ul>
              <li v-for="strength in aiAnalysisResult.strengths" :key="strength">
                {{ strength }}
              </li>
            </ul>
          </section>

          <section class="ai-block">
            <h4>Problemas detectados</h4>
            <p v-if="!aiAnalysisResult.issues.length" class="muted">
              No se detectaron problemas importantes en el contexto revisado
            </p>
            <div v-else class="issues-list">
              <article
                v-for="(issue, index) in aiAnalysisResult.issues"
                :key="`${issue.file}-${index}`"
                class="issue-card"
              >
                <div class="issue-header">
                  <span class="issue-badge">{{ issue.severity }}</span>
                  <span class="issue-category">{{ issue.category }}</span>
                </div>
                <p class="issue-file">{{ issue.file }}</p>
                <p class="issue-description">{{ issue.description }}</p>
                <p class="issue-suggestion">
                  <strong>Sugerencia:</strong> {{ issue.suggestion }}
                </p>
              </article>
            </div>
          </section>

          <section v-if="aiAnalysisResult.suggestions.length" class="ai-block">
            <h4>Sugerencias generales</h4>
            <ul>
              <li v-for="suggestion in aiAnalysisResult.suggestions" :key="suggestion">
                {{ suggestion }}
              </li>
            </ul>
          </section>
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

.ai-result-section {
  margin-top: 24px;
  padding: 16px;
  background: #fbfcfb;
  border: 1px solid #dfe6e1;
  border-radius: 8px;
}

.ai-result-section h3 {
  margin: 0 0 14px;
  font-size: 0.95rem;
}

.ai-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  margin-bottom: 14px;
  font-size: 0.88rem;
  color: #4b5650;
}

.ai-summary {
  margin: 0 0 18px;
  color: #17201b;
  line-height: 1.6;
}

.ai-error {
  margin: 0 0 14px;
  padding: 10px 12px;
  border-radius: 6px;
  background: #fde8e8;
  color: #9b2525;
  line-height: 1.5;
}

.ai-block {
  margin-top: 18px;
}

.ai-block h4 {
  margin: 0 0 10px;
  font-size: 0.9rem;
}

.ai-block ul {
  margin: 0;
  padding-left: 20px;
  color: #4b5650;
  line-height: 1.6;
}

.issues-list {
  display: grid;
  gap: 12px;
}

.issue-card {
  border: 1px solid #dfe6e1;
  border-radius: 8px;
  padding: 12px;
  background: #ffffff;
}

.issue-header {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.issue-badge,
.issue-category {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.issue-badge {
  background: #fff3e0;
  color: #8a4700;
}

.issue-category {
  background: #eef1ef;
  color: #4b5650;
}

.issue-file {
  margin: 0 0 8px;
  font-family: monospace;
  font-size: 0.82rem;
  color: #244579;
  word-break: break-all;
}

.issue-description,
.issue-suggestion {
  margin: 0 0 8px;
  color: #4b5650;
  line-height: 1.5;
}

.issue-suggestion {
  margin-bottom: 0;
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
