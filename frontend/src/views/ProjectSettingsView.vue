<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getProject, updateProject, type ProjectRequirements } from '@/services/projects'

const route = useRoute()
const projectId = route.params.projectId as string

const projectName = ref('')
const loading = ref(true)
const saving = ref(false)
const saveError = ref('')
const saveSuccess = ref('')

const requiredFiles = ref('')
const forbiddenFiles = ref('')
const requiredFeatures = ref('')
const minimumCommits = ref(0)

onMounted(() => {
  void loadProject()
})

async function loadProject() {
  loading.value = true

  try {
    const project = await getProject(projectId)
    projectName.value = project.name
    const req = project.requirements || getEmptyRequirements()

    requiredFiles.value = (req.requiredFiles || []).join('\n')
    forbiddenFiles.value = (req.forbiddenFiles || []).join('\n')
    requiredFeatures.value = (req.requiredFeatures || []).join('\n')
    minimumCommits.value = req.minimumCommits || 0
  } catch (err) {
    saveError.value = err instanceof Error ? err.message : 'No se pudo cargar el proyecto'
  } finally {
    loading.value = false
  }
}

function getEmptyRequirements(): ProjectRequirements {
  return {
    requiredFiles: [],
    forbiddenFiles: [],
    requiredFeatures: [],
    minimumCommits: 0,
  }
}

function parseList(text: string): string[] {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
}

async function handleSave() {
  saveError.value = ''
  saveSuccess.value = ''

  const requirements: ProjectRequirements = {
    requiredFiles: parseList(requiredFiles.value),
    forbiddenFiles: parseList(forbiddenFiles.value),
    requiredFeatures: parseList(requiredFeatures.value),
    minimumCommits: Math.max(0, Number(minimumCommits.value) || 0),
  }

  saving.value = true

  try {
    await updateProject(projectId, { requirements })
    saveSuccess.value = 'Configuracion guardada correctamente'
  } catch (err) {
    saveError.value = err instanceof Error ? err.message : 'No se pudo guardar la configuracion'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <main class="page">
    <header class="header">
      <div>
        <h1>Configuracion del proyecto</h1>
        <p v-if="projectName" class="project-name">{{ projectName }}</p>
      </div>
      <nav class="nav-links">
        <RouterLink to="/projects" class="link">Volver a proyectos</RouterLink>
        <RouterLink :to="`/projects/${projectId}`" class="link">Volver al detalle</RouterLink>
      </nav>
    </header>

    <section class="card">
      <p v-if="loading" class="muted">Cargando...</p>

      <form v-else class="settings-form" @submit.prevent="handleSave">
        <label class="field">
          <span>Archivos requeridos</span>
          <span class="hint">Uno por linea. Ej: README.md, requirements.txt</span>
          <textarea
            v-model="requiredFiles"
            rows="5"
            placeholder="README.md&#10;requirements.txt&#10;app/main.py"
          />
        </label>

        <label class="field">
          <span>Archivos prohibidos</span>
          <span class="hint">Uno por linea. Ej: .env, *.pem</span>
          <textarea
            v-model="forbiddenFiles"
            rows="5"
            placeholder=".env&#10;*.pem&#10;secrets.json"
          />
        </label>

        <label class="field">
          <span>Caracteristicas requeridas</span>
          <span class="hint">Una por linea. Ej: login, CRUD de proyectos</span>
          <textarea
            v-model="requiredFeatures"
            rows="5"
            placeholder="login&#10;CRUD de proyectos&#10;validacion de formulario"
          />
        </label>

        <label class="field field-number">
          <span>Minimo de commits</span>
          <input
            v-model.number="minimumCommits"
            type="number"
            min="0"
          />
        </label>

        <div class="form-actions">
          <p v-if="saveError" class="error-text">{{ saveError }}</p>
          <p v-if="saveSuccess" class="success-text">{{ saveSuccess }}</p>
          <button class="button primary" type="submit" :disabled="saving">
            {{ saving ? 'Guardando...' : 'Guardar configuracion' }}
          </button>
        </div>
      </form>
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
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header > div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

h1 {
  margin: 0;
  font-size: 2rem;
}

.project-name {
  margin: 0;
  color: #5d6962;
  font-size: 1rem;
}

.nav-links {
  display: flex;
  gap: 16px;
}

.link {
  color: #2f8f5b;
  text-decoration: none;
  font-weight: 700;
  font-size: 0.9rem;
}

.link:hover {
  text-decoration: underline;
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

.settings-form {
  display: grid;
  gap: 20px;
}

.field {
  display: grid;
  gap: 8px;
  color: #4b5650;
  font-size: 0.88rem;
  font-weight: 700;
}

.field-number {
  max-width: 200px;
}

.hint {
  color: #6c7770;
  font-size: 0.82rem;
  font-weight: 400;
}

.field textarea,
.field input {
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

.field input {
  width: 120px;
}

.field textarea:focus,
.field input:focus {
  border-color: #2f8f5b;
  outline: 2px solid #d9f0e4;
}

.form-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid #dfe6e1;
}

.button {
  border: 0;
  border-radius: 6px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
}

.button.primary {
  background: #2f8f5b;
  color: #ffffff;
}

.button:hover {
  filter: brightness(0.96);
}

.button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.muted {
  color: #5d6962;
  line-height: 1.6;
}

.error-text {
  color: #9b2525;
  line-height: 1.6;
}

.success-text {
  color: #17633d;
  line-height: 1.6;
}

@media (max-width: 760px) {
  .page {
    padding: 28px 18px;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .nav-links {
    flex-direction: column;
    gap: 8px;
  }

  .form-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .field-number {
    max-width: unset;
  }

  .field input {
    width: 100%;
  }
}
</style>