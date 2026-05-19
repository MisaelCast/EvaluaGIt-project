import { API_URL, fetchWithTimeout, getAuthHeaders } from '@/services/api'

export type ProjectRequirements = {
  requiredFiles: string[]
  forbiddenFiles: string[]
  requiredFeatures: string[]
  minimumCommits: number
}

export type ProjectResponse = {
  id: string
  professor_id: string
  name: string
  description: string | null
  requirements: ProjectRequirements
  due_date: string | null
  join_code: string
  created_at: string
  updated_at: string
}

export type ProjectCreate = {
  name: string
  description: string | null
  requirements: ProjectRequirements
  due_date: string | null
}

export type ProjectUpdate = {
  name?: string
  description?: string | null
  requirements?: ProjectRequirements
  due_date?: string | null
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

export async function getProjects(): Promise<ProjectResponse[]> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesión para ver tus proyectos')
  }

  const response = await fetchWithTimeout(`${API_URL}/projects`, {
    headers,
  })

  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }

  return response.json()
}

export async function getProject(projectId: string): Promise<ProjectResponse> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesión para ver los detalles del proyecto')
  }

  const response = await fetchWithTimeout(`${API_URL}/projects/${projectId}`, {
    headers,
  })

  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }

  return response.json()
}

export async function createProject(data: ProjectCreate): Promise<ProjectResponse> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesión para crear proyectos')
  }

  const response = await fetchWithTimeout(`${API_URL}/projects`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }

  return response.json()
}

export async function updateProject(projectId: string, data: ProjectUpdate): Promise<ProjectResponse> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesión para editar proyectos')
  }

  const response = await fetchWithTimeout(`${API_URL}/projects/${projectId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }

  return response.json()
}
