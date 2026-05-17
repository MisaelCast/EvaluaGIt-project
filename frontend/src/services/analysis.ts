import { API_URL, fetchWithTimeout, getAuthHeaders } from '@/services/api'

export type AnalysisRunResponse = {
  id: string
  repository_id: string
  status: string
  result_json: Record<string, unknown> | null
  error_message: string | null
  commit_hash: string | null
  started_at: string | null
  finished_at: string | null
  created_at: string
  updated_at: string
}

async function parseApiError(response: Response): Promise<string> {
  try {
    const body = await response.json()
    if (typeof body.detail === 'string') {
      return body.detail
    }
  } catch {
    // Si el backend no devuelve JSON, usamos un mensaje genérico.
  }

  return 'No se pudo completar la solicitud'
}

const ANALYZE_TIMEOUT_MS = 60000

export async function analyzeRepository(repositoryId: string): Promise<AnalysisRunResponse> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesión para analizar repositorios')
  }

  const response = await fetchWithTimeout(
    `${API_URL}/repositories/${repositoryId}/analyze`,
    {
      method: 'POST',
      headers,
    },
    ANALYZE_TIMEOUT_MS,
  )

  if (!response.ok) {
    const error = await parseApiError(response)
    throw new Error(error)
  }

  return response.json()
}

export async function getAnalysisRun(analysisRunId: string): Promise<AnalysisRunResponse> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesión para ver el análisis')
  }

  const response = await fetchWithTimeout(
    `${API_URL}/analysis-runs/${analysisRunId}`,
    {
      headers,
    },
  )

  if (!response.ok) {
    const error = await parseApiError(response)
    throw new Error(error)
  }

  return response.json()
}