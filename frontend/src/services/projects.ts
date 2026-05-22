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

export type ProjectUpdateRequest = {
  name?: string
  description?: string | null
  requirements?: Record<string, unknown>
  due_date?: string | null
}

export type ProjectUpdate = ProjectUpdateRequest

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
 * Obtiene los proyectos del profesor
 * Requiere sesion activa
 */
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

/**
 * Obtiene los detalles de un proyecto
 * Solo el profesor propietario puede verlos
 */
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

/**
 * Crea un proyecto para el profesor autenticado
 * El profesor queda como propietario
 */
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

/**
 * Actualiza un proyecto existente
 * Solo el profesor propietario puede modificarlo
 */
export async function updateProject(projectId: string, data: ProjectUpdateRequest): Promise<ProjectResponse> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesión para actualizar el proyecto')
  }

  const response = await fetchWithTimeout(`${API_URL}/projects/${projectId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await parseApiError(response)
    throw new Error(error === 'No se pudo completar la solicitud' ? 'No se pudo actualizar el proyecto' : error)
  }

  return response.json()
}

/**
 * Permite unirse a un proyecto con codigo de acceso
 * El profesor comparte el codigo con sus alumnos
 */
export async function joinProject(joinCode: string): Promise<ProjectResponse> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesion para unirte a un proyecto')
  }

  const response = await fetchWithTimeout(`${API_URL}/projects/join`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ join_code: joinCode }),
  })

  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }

  return response.json()
}

/**
 * Obtiene los proyectos unidos del estudiante
 * Incluye proyectos con repositorios vinculados
 */
export async function getJoinedProjects(): Promise<ProjectResponse[]> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesion para ver tus proyectos')
  }

  const response = await fetchWithTimeout(`${API_URL}/projects/joined`, {
    headers,
  })

  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }

  return response.json()
}

export async function deleteProject(projectId: string): Promise<void> {
  const headers = await getAuthHeaders()

  if (!headers.Authorization) {
    throw new Error('Inicia sesión para eliminar proyectos')
  }

  const response = await fetchWithTimeout(`${API_URL}/projects/${projectId}`, {
    method: 'DELETE',
    headers,
  })

  if (!response.ok) {
    let message = 'No se pudo eliminar el proyecto'
    try {
      const body = await response.json()
      if (typeof body.detail === 'string') {
        message = body.detail
      }
    } catch {
      // Si el backend no devuelve JSON usamos el mensaje generico
    }
    throw new Error(message)
  }
}
