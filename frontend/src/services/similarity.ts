import { API_URL, fetchWithTimeout, getAuthHeaders } from '@/services/api'

export type SimilarityRepositoryItem = {
  repository_id: string
  student_id: string
  student_name: string | null
  student_email: string | null
  repo_url: string
  branch: string
}

export type SimilarityPair = {
  left_repository_id: string
  right_repository_id: string
  left_student_name: string
  right_student_name: string
  left_file: string
  right_file: string
  similarity: number | null
  similarity_percent: number | null
  level: 'normal' | 'review' | 'relevant' | 'high'
  label: string
  extra: Record<string, unknown>
}

export type SimilarityAnalysisResponse = {
  project_id: string
  status: string
  message: string
  repositories_count: number
  repositories: SimilarityRepositoryItem[]
  pairs: SimilarityPair[]
  provider: string
  executed: boolean
  raw_output?: string | null
  output_files?: string[]
  summary?: Record<string, unknown> | null
}

export type SimilarityRunResponse = {
  id: string
  project_id: string
  status: string
  result_json: SimilarityAnalysisResponse | null
  error_message: string | null
  started_at: string | null
  finished_at: string | null
  created_at: string
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

  return 'No se pudo analizar la similitud'
}

const SIMILARITY_ANALYSIS_TIMEOUT_MS = 120000

export async function analyzeProjectSimilarity(projectId: string): Promise<SimilarityRunResponse> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesion para analizar similitud')
  }

  const response = await fetchWithTimeout(
    `${API_URL}/projects/${projectId}/similarity/analyze`,
    {
      method: 'POST',
      headers,
    },
    SIMILARITY_ANALYSIS_TIMEOUT_MS,
  )

  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }

  return response.json()
}

export async function getLatestSimilarityAnalysis(projectId: string): Promise<SimilarityRunResponse> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesion para ver el analisis de similitud')
  }

  const response = await fetchWithTimeout(`${API_URL}/projects/${projectId}/similarity/latest`, {
    headers,
  })

  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }

  return response.json()
}
