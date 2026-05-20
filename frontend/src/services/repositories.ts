import { API_URL, fetchWithTimeout, getAuthHeaders } from '@/services/api'

/**
 * Datos del estudiante dentro de un repositorio
 * Se incluyen como parte de RepositoryWithStudent cuando el profesor
 * consulta repositorios de su proyecto
 */
export type RepositoryStudent = {
  id: string
  full_name: string
  email: string
  avatar_url: string | null
}

/**
 * Respuesta de repositorio usada por el profesor
 * Incluye datos del estudiante para mostrar al owner
 * sin hacer requests separadas
 */
export type RepositoryWithStudent = {
  id: string
  project_id: string
  student_id: string
  repo_url: string
  branch: string
  status: string
  last_commit_hash: string | null
  last_analyzed_at: string | null
  created_at: string
  updated_at: string
  student: RepositoryStudent
}

/**
 * Respuesta de repositorio para el estudiante propietario
 * No incluye student porque el estudiante ya conoce sus datos
 */
export type RepositoryResponse = {
  id: string
  project_id: string
  student_id: string
  repo_url: string
  branch: string
  status: string
  last_commit_hash: string | null
  last_analyzed_at: string | null
  created_at: string
  updated_at: string
}

export type RepositoryCreate = {
  project_id: string
  repo_url: string
  branch: string
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

  return 'No se pudo completar la solicitud'
}

/**
 * Obtiene repositorios de un proyecto
 * Incluye datos del estudiante
 */
export async function getProjectRepositories(projectId: string): Promise<RepositoryWithStudent[]> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesion para ver los repositorios')
  }

  const response = await fetchWithTimeout(`${API_URL}/repositories/projects/${projectId}/repositories`, {
    headers,
  })

  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }

  return response.json()
}

/**
 * Obtiene los repositorios propios del estudiante
 * No incluye datos del estudiante
 */
export async function getMyRepositories(): Promise<RepositoryResponse[]> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesion para ver tus repositorios')
  }

  const response = await fetchWithTimeout(`${API_URL}/repositories/mine`, {
    headers,
  })

  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }

  return response.json()
}

/**
 * Vincula un repositorio al proyecto del estudiante
 * El estudiante solo puede tener uno por proyecto
 */
export async function createRepository(data: RepositoryCreate): Promise<RepositoryResponse> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesion para vincular repositorios')
  }

  const response = await fetchWithTimeout(`${API_URL}/repositories`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await parseApiError(response)
    throw new Error(error)
  }

  return response.json()
}

/**
 * Elimina el repositorio vinculado al estudiante
 * Solo el propietario puede eliminarlo
 */
export async function deleteRepository(repositoryId: string): Promise<void> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesion para eliminar repositorios')
  }

  const response = await fetchWithTimeout(`${API_URL}/repositories/${repositoryId}`, {
    method: 'DELETE',
    headers,
  })

  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }
}
