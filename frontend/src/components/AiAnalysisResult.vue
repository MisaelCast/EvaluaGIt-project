<script setup lang="ts">
import { computed } from 'vue'
import type { AiAnalysisResponse } from '@/services/aiAnalysis'

const props = defineProps<{
  result?: AiAnalysisResponse | null
  status?: string | null
  createdAt?: string | null
  finishedAt?: string | null
}>()

const hasResult = computed(() => Boolean(props.result))
const provider = computed(() => props.result?.provider ?? '')
const qualityScore = computed(() => props.result?.quality_score ?? null)
const riskLevel = computed(() => props.result?.risk_level ?? null)
const filesCount = computed(() => props.result?.files_count ?? null)
const summary = computed(() => props.result?.summary ?? '')
const message = computed(() => props.result?.message ?? '')
const error = computed(() => props.result?.error ?? '')
const strengths = computed(() => props.result?.strengths ?? [])
const issues = computed(() => props.result?.issues ?? [])
const suggestions = computed(() => props.result?.suggestions ?? [])

function getSeverityClasses(severity: string): string {
  switch (severity) {
    case 'critical':
      return 'bg-red-100 text-red-700 border-red-200'
    case 'high':
      return 'bg-orange-100 text-orange-700 border-orange-200'
    case 'medium':
      return 'bg-amber-100 text-amber-700 border-amber-200'
    case 'low':
      return 'bg-emerald-100 text-emerald-700 border-emerald-200'
    default:
      return 'bg-slate-100 text-slate-700 border-slate-200'
  }
}

function getRiskClasses(riskLevel: string | null | undefined): string {
  return getSeverityClasses(riskLevel ?? '')
}

function formatRiskLevel(value: string | null | undefined): string {
  switch (value) {
    case 'low':
      return 'bajo'
    case 'medium':
      return 'medio'
    case 'high':
      return 'alto'
    case 'critical':
      return 'critico'
    default:
      return value || 'No disponible'
  }
}

function formatSeverity(value: string | null | undefined): string {
  return formatRiskLevel(value)
}

function formatCategory(value: string | null | undefined): string {
  switch (value) {
    case 'security':
      return 'seguridad'
    case 'architecture':
      return 'arquitectura'
    case 'maintainability':
      return 'mantenibilidad'
    case 'performance':
      return 'rendimiento'
    case 'validation':
      return 'validacion'
    case 'cleanup':
      return 'limpieza'
    case 'readability':
      return 'legibilidad'
    default:
      return value || 'No disponible'
  }
}

function formatStatus(value: string | null | undefined): string {
  switch (value) {
    case 'PENDING':
      return 'Pendiente'
    case 'RUNNING':
      return 'En proceso'
    case 'COMPLETED':
      return 'Completado'
    case 'FAILED':
      return 'Fallido'
    default:
      return value || 'No disponible'
  }
}

function formatDate(value: string | null | undefined): string {
  if (!value) return 'No disponible'

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
  }).format(new Date(value))
}
</script>

<template>
  <section class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
    <div class="flex flex-col gap-2 border-b border-slate-100 pb-5 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h3 class="text-lg font-semibold text-slate-950">Resultado del analisis IA</h3>
        <p class="mt-1 text-sm text-slate-500">
          <span v-if="provider">Proveedor: {{ provider }}</span>
          <span v-if="provider && filesCount !== null"> · </span>
          <span v-if="filesCount !== null">Archivos revisados: {{ filesCount }}</span>
        </p>
      </div>
      <span
        v-if="riskLevel"
        class="inline-flex w-fit items-center rounded-full border px-3 py-1 text-xs font-semibold"
        :class="getRiskClasses(riskLevel)"
      >
        Riesgo {{ formatRiskLevel(riskLevel) }}
      </span>
    </div>

    <div class="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Calificacion tecnica</p>
        <p class="mt-2 text-2xl font-semibold text-slate-950">
          {{ qualityScore ?? 'No disponible' }}
        </p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Riesgo</p>
        <p class="mt-2 text-base font-semibold text-slate-950">
          {{ formatRiskLevel(riskLevel) }}
        </p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Archivos revisados</p>
        <p class="mt-2 text-base font-semibold text-slate-950">
          {{ filesCount ?? 'No disponible' }}
        </p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Estado</p>
        <p class="mt-2 text-base font-semibold text-slate-950">
          {{ formatStatus(status) }}
        </p>
      </div>
    </div>

    <div v-if="createdAt || finishedAt" class="mt-4 flex flex-wrap gap-3 text-sm text-slate-500">
      <span v-if="createdAt">Creado: {{ formatDate(createdAt) }}</span>
      <span v-if="finishedAt">Finalizado: {{ formatDate(finishedAt) }}</span>
    </div>

    <div v-if="props.result?.enabled === false && message" class="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
      {{ message }}
    </div>

    <div v-if="error" class="mt-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {{ error }}
    </div>

    <div v-if="summary" class="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4">
      <h4 class="text-sm font-semibold text-slate-950">Resumen</h4>
      <p class="mt-2 text-sm leading-6 text-slate-600">{{ summary }}</p>
    </div>

    <section v-if="strengths.length" class="mt-6">
      <h4 class="text-sm font-semibold text-slate-950">Fortalezas</h4>
      <ul class="mt-3 grid gap-2 text-sm text-slate-600">
        <li
          v-for="strength in strengths"
          :key="strength"
          class="flex gap-2"
        >
          <span class="mt-1 h-2 w-2 flex-shrink-0 rounded-full bg-emerald-500"></span>
          <span>{{ strength }}</span>
        </li>
      </ul>
    </section>

    <section class="mt-6">
      <h4 class="text-sm font-semibold text-slate-950">Problemas detectados</h4>
      <p v-if="!issues.length" class="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
        No se detectaron problemas importantes en el contexto revisado
      </p>
      <div v-else class="mt-3 grid gap-3">
        <article
          v-for="(issue, index) in issues"
          :key="`${issue.file}-${index}`"
          class="rounded-xl border border-slate-200 bg-white p-4"
        >
          <div class="flex flex-wrap items-center gap-2">
            <span
              class="inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold"
              :class="getSeverityClasses(issue.severity)"
            >
              {{ formatSeverity(issue.severity) }}
            </span>
            <span class="inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
              {{ formatCategory(issue.category) }}
            </span>
          </div>
          <p class="mt-3 break-all font-mono text-xs text-slate-500">{{ issue.file }}</p>
          <p class="mt-3 text-sm leading-6 text-slate-700">{{ issue.description }}</p>
          <p class="mt-3 text-sm leading-6 text-slate-600">
            <span class="font-semibold text-slate-950">Sugerencia:</span>
            {{ issue.suggestion }}
          </p>
        </article>
      </div>
    </section>

    <section v-if="suggestions.length" class="mt-6">
      <h4 class="text-sm font-semibold text-slate-950">Sugerencias generales</h4>
      <ul class="mt-3 grid gap-2 text-sm text-slate-600">
        <li
          v-for="suggestion in suggestions"
          :key="suggestion"
          class="flex gap-2"
        >
          <span class="mt-1 h-2 w-2 flex-shrink-0 rounded-full bg-slate-400"></span>
          <span>{{ suggestion }}</span>
        </li>
      </ul>
    </section>

    <p v-if="!hasResult" class="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
      No hay resultado IA disponible
    </p>
  </section>
</template>
