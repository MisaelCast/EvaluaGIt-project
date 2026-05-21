import { API_URL, fetchWithTimeout, getAuthHeaders } from '@/services/api'

export type AiIssue = {
  severity: string
  category: string
  file: string
  description: string
  suggestion: string
}

export type AiAnalysisResponse = {
  enabled: boolean
  provider: string
  summary: string | null
  quality_score: number | null
  strengths: string[]
  issues: AiIssue[]
  suggestions: string[]
  risk_level: string | null
  files_count: number | null
  message: string | null
  error: string | null
}

async function parseApiError(response: Response): Promise<string> {
  try {
    const body = await response.json()
    if (typeof body.detail === 'string') {
      return body.detail
    }
  } catch {
    // Si el backend no devuelve JSON usamos un mensaje generico
  }

  return 'No se pudo completar el analisis IA'
}

const AI_ANALYSIS_TIMEOUT_MS = 120000

export async function analyzeRepositoryWithAi(repositoryId: string): Promise<AiAnalysisResponse> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesion para analizar con IA')
  }

  const response = await fetchWithTimeout(
    `${API_URL}/repositories/${repositoryId}/ai-analysis`,
    {
      method: 'POST',
      headers,
    },
    AI_ANALYSIS_TIMEOUT_MS,
  )

  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }

  return response.json()
}
