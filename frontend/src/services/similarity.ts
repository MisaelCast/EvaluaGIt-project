import { API_URL, fetchWithTimeout, getAuthHeaders } from '@/services/api'

export type SimilarityRepositoryItem = {
  repository_id: string
  student_id: string
  student_name: string | null
  student_email: string | null
  repo_url: string
  branch: string
}

export type SimilarityAnalysisResponse = {
  project_id: string
  status: string
  message: string
  repositories_count: number
  repositories: SimilarityRepositoryItem[]
  pairs: unknown[]
  provider: string
  executed: boolean
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

export async function analyzeProjectSimilarity(projectId: string): Promise<SimilarityAnalysisResponse> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesion para analizar similitud')
  }

  const response = await fetchWithTimeout(`${API_URL}/projects/${projectId}/similarity/analyze`, {
    method: 'POST',
    headers,
  })

  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }

  return response.json()
}
