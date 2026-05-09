const API_URL = import.meta.env.VITE_API_URL

if (!API_URL) {
  throw new Error('VITE_API_URL no está configurada')
}

export type HealthResponse = {
  status: string
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/health`)

  if (!response.ok) {
    throw new Error('No se pudo conectar con el backend')
  }

  return response.json()
}
