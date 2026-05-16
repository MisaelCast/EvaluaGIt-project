<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { createProject, getProjects, type ProjectResponse } from '@/services/projects'

const projects = ref<ProjectResponse[]>([])
const projectsLoading = ref(false)
const projectsError = ref('')
const creatingProject = ref(false)
const newProjectName = ref('')
const newProjectDescription = ref('')

onMounted(() => {
  void loadProjects()
})

async function loadProjects() {
  projectsLoading.value = true
  projectsError.value = ''

  try {
    projects.value = await getProjects()
  } catch (err) {
    projects.value = []
    projectsError.value =
      err instanceof Error ? err.message : 'No se pudieron cargar los proyectos'
  } finally {
    projectsLoading.value = false
  }
}

async function handleCreateProject() {
  const name = newProjectName.value.trim()
  const description = newProjectDescription.value.trim()

  if (!name) {
    projectsError.value = 'El nombre del proyecto es obligatorio'
    return
  }

  creatingProject.value = true
  projectsError.value = ''

  try {
    await createProject({
      name,
      description: description || null,
      requirements: {
        requiredFiles: [],
        forbiddenFiles: [],
        requiredFeatures: [],
        minimumCommits: 0,
      },
      due_date: null,
    })
    newProjectName.value = ''
    newProjectDescription.value = ''
    await loadProjects()
  } catch (err) {
    projectsError.value =
      err instanceof Error ? err.message : 'No se pudo crear el proyecto'
  } finally {
    creatingProject.value = false
  }
}

function formatDate(value: string | null): string {
  if (!value) return 'Sin fecha'

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
  }).format(new Date(value))
}
</script>

<template>
  <main class="page">
    <header class="header">
      <h1>Mis proyectos</h1>
    </header>

    <section class="card">
      <form class="project-form" @submit.prevent="handleCreateProject">
        <div class="form-grid">
          <label class="field">
            <span>Nombre del proyecto</span>
            <input
              v-model="newProjectName"
              type="text"
              placeholder="Proyecto final"
              autocomplete="off"
            />
          </label>

          <label class="field">
            <span>Descripcion</span>
            <textarea
              v-model="newProjectDescription"
              rows="3"
              placeholder="Breve descripcion del proyecto"
            />
          </label>
        </div>

        <button class="button primary" type="submit" :disabled="creatingProject">
          {{ creatingProject ? 'Creando...' : 'Crear proyecto' }}
        </button>
      </form>

      <p v-if="projectsError" class="error-text">{{ projectsError }}</p>
      <p v-if="projectsLoading" class="muted">Cargando proyectos...</p>

      <div v-else-if="projects.length" class="projects-list">
        <article v-for="project in projects" :key="project.id" class="project-card">
          <div class="project-info">
            <h3>{{ project.name }}</h3>
            <p class="muted">{{ project.description || 'Sin descripcion' }}</p>
            <div class="project-meta">
              <span>Creado: {{ formatDate(project.created_at) }}</span>
            </div>
          </div>
          <div class="project-actions">
            <RouterLink
              :to="`/projects/${project.id}`"
              class="button primary"
            >
              Ver detalle
            </RouterLink>
            <RouterLink
              :to="`/projects/${project.id}/settings`"
              class="button secondary"
            >
              Configuracion
            </RouterLink>
          </div>
        </article>
      </div>

      <p v-else-if="!projectsError" class="muted">
        Aun no tienes proyectos.
      </p>
    </section>
  </main>
</template>

<style scoped>
.page {
  min-height: 100vh;
  padding: 48px;
  background: #f3f5f4;
  color: #17201b;
}

.header {
  max-width: 1080px;
  margin: 0 auto 28px;
}

h1 {
  margin: 0;
  font-size: 2rem;
}

.card {
  max-width: 1080px;
  margin: 0 auto;
  background: #ffffff;
  border: 1px solid #dfe6e1;
  border-radius: 8px;
  padding: 22px;
  box-shadow: 0 10px 30px rgb(25 35 30 / 6%);
}

.project-form {
  display: grid;
  gap: 16px;
  padding-bottom: 18px;
  border-bottom: 1px solid #dfe6e1;
  margin-bottom: 18px;
}

.form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 2fr);
  gap: 16px;
}

.field {
  display: grid;
  gap: 8px;
  color: #4b5650;
  font-size: 0.88rem;
  font-weight: 700;
}

.field input,
.field textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #cfd8d2;
  border-radius: 6px;
  padding: 10px 12px;
  color: #17201b;
  font: inherit;
}

.field textarea {
  resize: vertical;
}

.field input:focus,
.field textarea:focus {
  border-color: #2f8f5b;
  outline: 2px solid #d9f0e4;
}

.projects-list {
  display: grid;
  gap: 12px;
}

.project-card {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  border: 1px solid #dfe6e1;
  border-radius: 8px;
  padding: 16px;
  background: #fbfcfb;
}

.project-info {
  flex: 1;
  min-width: 0;
}

.project-card h3 {
  margin: 0 0 8px;
  font-size: 1rem;
}

.project-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  margin-top: 14px;
  color: #6c7770;
  font-size: 0.86rem;
}

.project-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.button {
  border: 0;
  border-radius: 6px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  text-align: center;
}

.button.primary {
  background: #2f8f5b;
  color: #ffffff;
}

.button.secondary {
  background: #eef1ef;
  color: #17201b;
}

.button:hover {
  filter: brightness(0.96);
}

.muted {
  color: #5d6962;
  line-height: 1.6;
}

.error-text {
  color: #9b2525;
  line-height: 1.6;
}

@media (max-width: 760px) {
  .page {
    padding: 28px 18px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .project-card {
    flex-direction: column;
  }

  .project-actions {
    width: 100%;
    flex-direction: column;
  }

  .button {
    text-align: center;
  }
}
</style>