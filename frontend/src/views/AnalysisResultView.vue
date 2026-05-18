<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getAnalysisRun, type AnalysisRunResponse } from '@/services/analysis'

const route = useRoute()
const projectId = route.params.projectId as string
const analysisRunId = route.params.analysisRunId as string

const loading = ref(true)
const error = ref('')
const analysisRun = ref<AnalysisRunResponse | null>(null)

const result = computed(() => analysisRun.value?.result_json ?? null)

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

function getString(res: Record<string, unknown> | null, key: string): string {
  if (!res) return 'No detectado'
  return (res[key] as string) || 'No detectado'
}

function getArray(res: Record<string, unknown> | null, key: string): string[] {
  if (!res) return []
  const value = res[key]
  return Array.isArray(value) ? value.filter((item) => typeof item === 'string') : []
}

function getRequiredFiles() {
  if (!result.value) return { found: [] as string[], missing: [] as string[] }
  const rf = result.value.required_files as Record<string, unknown> | null
  return {
    found: (rf?.found as string[] | null) || [],
    missing: (rf?.missing as string[] | null) || [],
  }
}

function getForbiddenFiles() {
  if (!result.value) return []
  const ff = result.value.forbidden_files as Record<string, unknown> | null
  return (ff?.found as string[] | null) || []
}

function getWarnings() {
  return getArray(result.value, 'warnings')
}

function getScore(): number | null {
  if (!result.value) return null
  const score = result.value.score as Record<string, unknown> | null
  if (!score) return null
  return score.structure as number | null
}

function getGit() {
  if (!result.value) return null
  const git = result.value.git
  return typeof git === 'object' && git !== null ? git as Record<string, unknown> : null
}

function getGitCommits(): number {
  const git = getGit()
  if (!git) return 0
  return typeof git.total_commits === 'number' ? git.total_commits : 0
}

function getMinCommitsRequired(): number {
  const git = getGit()
  if (!git) return 0
  const min = git.minimum_commits
  if (typeof min === 'object' && min !== null) {
    return typeof (min as Record<string, unknown>).required === 'number' ? (min as Record<string, unknown>).required as number : 0
  }
  return 0
}

function getMinCommitsPassed(): boolean {
  const git = getGit()
  if (!git) return true
  const min = git.minimum_commits
  if (typeof min === 'object' && min !== null) {
    return typeof (min as Record<string, unknown>).passed === 'boolean' ? (min as Record<string, unknown>).passed as boolean : true
  }
  return true
}

function getGitAuthors(): string[] {
  const git = getGit()
  if (!git) return []
  return Array.isArray(git.authors) ? git.authors.filter((a) => typeof a === 'string') : []
}

function getLastCommit(): Record<string, unknown> | null {
  const git = getGit()
  if (!git) return null
  const lc = git.last_commit
  return typeof lc === 'object' && lc !== null ? (lc as Record<string, unknown>) : null
}

function getGitWarnings(): string[] {
  const git = getGit()
  if (!git) return []
  return Array.isArray(git.warnings) ? git.warnings.filter((w) => typeof w === 'string') : []
}
</script>

<template>
  <main class="min-h-screen bg-slate-50 text-slate-900 px-6 py-8">
    <header class="max-w-6xl mx-auto mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <h1 class="text-3xl font-bold">Resultado de analisis</h1>
      <nav class="flex gap-4">
        <RouterLink
          :to="`/projects/${projectId}`"
          class="text-emerald-600 hover:text-emerald-700 font-semibold text-sm"
        >
          Volver al proyecto
        </RouterLink>
        <RouterLink
          to="/projects"
          class="text-emerald-600 hover:text-emerald-700 font-semibold text-sm"
        >
          Volver a proyectos
        </RouterLink>
      </nav>
    </header>

    <section class="max-w-6xl mx-auto bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
      <p v-if="loading" class="text-slate-500">Cargando analisis...</p>
      <p v-else-if="error" class="text-red-600">{{ error }}</p>

      <div v-else-if="analysisRun">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
          <div class="flex flex-col gap-1">
            <span class="text-xs font-semibold text-slate-500 uppercase">Status</span>
            <span class="text-sm font-medium">{{ analysisRun.status }}</span>
          </div>
          <div v-if="analysisRun.commit_hash" class="flex flex-col gap-1">
            <span class="text-xs font-semibold text-slate-500 uppercase">Commit</span>
            <span class="text-sm font-mono bg-slate-100 px-2 py-1 rounded inline-block w-fit">
              {{ analysisRun.commit_hash.substring(0, 7) }}
            </span>
          </div>
          <div class="flex flex-col gap-1">
            <span class="text-xs font-semibold text-slate-500 uppercase">Iniciado</span>
            <span class="text-sm">{{ formatDate(analysisRun.started_at) }}</span>
          </div>
          <div class="flex flex-col gap-1">
            <span class="text-xs font-semibold text-slate-500 uppercase">Finalizado</span>
            <span class="text-sm">{{ formatDate(analysisRun.finished_at) }}</span>
          </div>
        </div>

        <div v-if="analysisRun.error_message" class="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-6">
          <p class="font-semibold mb-1">Error del analisis:</p>
          <p class="text-sm">{{ analysisRun.error_message }}</p>
        </div>

        <div class="flex flex-col gap-6">
          <div class="border-t border-slate-200 pt-6">
            <h3 class="text-lg font-semibold mb-4">Resumen</h3>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div class="flex flex-col gap-1">
                <span class="text-xs font-semibold text-slate-500 uppercase">Lenguaje</span>
                <span class="text-sm">{{ getString(result, 'language') }}</span>
              </div>
              <div class="flex flex-col gap-1">
                <span class="text-xs font-semibold text-slate-500 uppercase">Framework</span>
                <span class="text-sm">{{ getString(result, 'framework') }}</span>
              </div>
              <div class="flex flex-col gap-1">
                <span class="text-xs font-semibold text-slate-500 uppercase">Tiene README</span>
                <span class="text-sm">{{ result?.has_readme ? 'Si' : 'No' }}</span>
              </div>
              <div class="flex flex-col gap-1">
                <span class="text-xs font-semibold text-slate-500 uppercase">Score estructura</span>
                <span class="text-sm">{{ getScore() !== null ? `${getScore()}%` : 'N/A' }}</span>
              </div>
            </div>
          </div>

          <div class="border-t border-slate-200 pt-6">
            <h3 class="text-lg font-semibold mb-4">Dependencias</h3>
            <ul v-if="getArray(result, 'dependencies').length" class="list-disc list-inside text-sm space-y-1">
              <li v-for="dep in getArray(result, 'dependencies')" :key="dep">{{ dep }}</li>
            </ul>
            <p v-else class="text-slate-500 text-sm">Sin dependencias detectadas</p>
          </div>

          <div class="border-t border-slate-200 pt-6">
            <h3 class="text-lg font-semibold mb-4">Archivos requeridos</h3>
            <div v-if="getRequiredFiles().found.length" class="mb-3">
              <p class="text-xs font-semibold text-slate-500 uppercase mb-2">Encontrados:</p>
              <ul class="list-disc list-inside text-sm space-y-1 text-emerald-700">
                <li v-for="file in getRequiredFiles().found" :key="file">{{ file }}</li>
              </ul>
            </div>
            <div v-if="getRequiredFiles().missing.length" class="mb-3">
              <p class="text-xs font-semibold text-slate-500 uppercase mb-2">Faltantes:</p>
              <ul class="list-disc list-inside text-sm space-y-1 text-red-600">
                <li v-for="file in getRequiredFiles().missing" :key="file">{{ file }}</li>
              </ul>
            </div>
            <p v-if="!getRequiredFiles().found.length && !getRequiredFiles().missing.length" class="text-slate-500 text-sm">
              Sin informacion de archivos requeridos
            </p>
          </div>

          <div class="border-t border-slate-200 pt-6">
            <h3 class="text-lg font-semibold mb-4">Archivos prohibidos</h3>
            <ul v-if="getForbiddenFiles().length" class="list-disc list-inside text-sm space-y-1 text-red-600">
              <li v-for="file in getForbiddenFiles()" :key="file">{{ file }}</li>
            </ul>
            <p v-else class="text-slate-500 text-sm">No se encontraron archivos prohibidos</p>
          </div>

          <div class="border-t border-slate-200 pt-6">
            <h3 class="text-lg font-semibold mb-4">Historial Git</h3>
            <div class="space-y-4">
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div class="flex flex-col gap-1">
                  <span class="text-xs font-semibold text-slate-500 uppercase">Total commits</span>
                  <span class="text-sm font-medium">{{ getGitCommits() }}</span>
                </div>
                <div class="flex flex-col gap-1">
                  <span class="text-xs font-semibold text-slate-500 uppercase">Minimo requerido</span>
                  <span class="text-sm">{{ getMinCommitsRequired() > 0 ? getMinCommitsRequired() : 'Sin configurar' }}</span>
                </div>
                <div class="flex flex-col gap-1">
                  <span class="text-xs font-semibold text-slate-500 uppercase">Cumple minimo</span>
                  <span v-if="getMinCommitsRequired() > 0" :class="getMinCommitsPassed() ? 'text-emerald-700 font-medium' : 'text-red-600 font-medium'">
                    {{ getMinCommitsPassed() ? 'Si' : 'No' }}
                  </span>
                  <span v-else class="text-slate-500 text-sm">N/A</span>
                </div>
                <div v-if="getMinCommitsRequired() > 0 && !getMinCommitsPassed()" class="flex flex-col gap-1">
                  <span class="text-xs font-semibold text-slate-500 uppercase">Commits faltantes</span>
                  <span class="text-sm text-red-600">{{ getMinCommitsRequired() - getGitCommits() }}</span>
                </div>
              </div>

              <div v-if="getGitAuthors().length" class="bg-slate-50 border border-slate-200 rounded-xl p-4">
                <p class="text-xs font-semibold text-slate-500 uppercase mb-2">Autores detectados</p>
                <div class="flex flex-wrap gap-2">
                  <span v-for="author in getGitAuthors()" :key="author" class="bg-slate-200 text-slate-700 px-2 py-1 rounded text-sm">
                    {{ author }}
                  </span>
                </div>
              </div>
              <p v-else class="text-slate-500 text-sm">Sin autores detectados</p>

              <div v-if="getLastCommit()" class="bg-slate-50 border border-slate-200 rounded-xl p-4">
                <p class="text-xs font-semibold text-slate-500 uppercase mb-2">Ultimo commit</p>
                <div class="space-y-1 text-sm">
                  <div class="flex items-center gap-2">
                    <span class="text-slate-500">Hash:</span>
                    <span class="font-mono bg-slate-100 px-2 py-0.5 rounded text-xs">{{ String(getLastCommit()?.hash || '').substring(0, 7) }}</span>
                  </div>
                  <div>
                    <span class="text-slate-500">Mensaje:</span>
                    <span class="ml-2">{{ String(getLastCommit()?.message || 'Sin mensaje') }}</span>
                  </div>
                  <div>
                    <span class="text-slate-500">Autor:</span>
                    <span class="ml-2">{{ String(getLastCommit()?.author || 'Desconocido') }}</span>
                  </div>
                  <div>
                    <span class="text-slate-500">Fecha:</span>
                    <span class="ml-2">{{ formatDate(String(getLastCommit()?.date || '')) }}</span>
                  </div>
                </div>
              </div>
              <p v-else class="text-slate-500 text-sm">Sin informacion del ultimo commit</p>

              <div v-if="getGitWarnings().length" class="bg-amber-50 border border-amber-200 rounded-xl p-4">
                <p class="text-xs font-semibold text-amber-700 uppercase mb-2">Advertencias Git</p>
                <ul class="list-disc list-inside text-sm text-amber-700 space-y-1">
                  <li v-for="w in getGitWarnings()" :key="w">{{ w }}</li>
                </ul>
              </div>
            </div>
          </div>

          <div class="border-t border-slate-200 pt-6">
            <h3 class="text-lg font-semibold mb-4">Advertencias</h3>
            <ul v-if="getWarnings().length" class="list-disc list-inside text-sm space-y-1 text-amber-700">
              <li v-for="w in getWarnings()" :key="w">{{ w }}</li>
            </ul>
            <p v-else class="text-slate-500 text-sm">Sin advertencias</p>
          </div>

          <div class="border-t border-slate-200 pt-6">
            <h3 class="text-lg font-semibold mb-4">JSON completo</h3>
            <pre class="bg-slate-950 text-slate-100 rounded-xl p-4 overflow-x-auto text-sm leading-relaxed">{{ JSON.stringify(analysisRun.result_json, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>