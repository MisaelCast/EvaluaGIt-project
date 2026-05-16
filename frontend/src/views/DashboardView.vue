<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import type { User } from '@supabase/supabase-js'
import { getCurrentUser, signOut } from '@/services/auth'

const user = ref<User | null>(null)
const loading = ref(true)

onMounted(() => {
  void loadUser()
})

async function loadUser() {
  loading.value = true
  try {
    user.value = await getCurrentUser()
  } catch {
    user.value = null
  } finally {
    loading.value = false
  }
}

async function handleSignOut() {
  try {
    await signOut()
    user.value = null
  } catch {
    // ignore
  }
}
</script>

<template>
  <main class="page">
    <header class="header">
      <h1>Dashboard</h1>
    </header>

    <section class="cards">
      <article class="card">
        <h2>Proyectos</h2>
        <p class="muted">Gestiona tus proyectos y requerimientos.</p>
        <RouterLink to="/projects" class="button primary">Ir a proyectos</RouterLink>
      </article>

      <article class="card">
        <h2>Repositorios</h2>
        <p class="muted">Vincuta repositorios GitHub a tus proyectos.</p>
        <RouterLink to="/projects" class="button secondary">Ver repositorios</RouterLink>
      </article>

      <article class="card">
        <h2>Analisis</h2>
        <p class="muted">Ejecuta analisis sobre repositorios vinculados.</p>
        <RouterLink to="/projects" class="button secondary">Ver analisis</RouterLink>
      </article>
    </section>

    <section v-if="user" class="user-section">
      <p>Sesion activa: <strong>{{ user.email }}</strong></p>
      <button class="button secondary" type="button" @click="handleSignOut">
        Cerrar sesion
      </button>
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

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 18px;
  max-width: 1080px;
  margin: 0 auto;
}

.card {
  background: #ffffff;
  border: 1px solid #dfe6e1;
  border-radius: 8px;
  padding: 22px;
  box-shadow: 0 10px 30px rgb(25 35 30 / 6%);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card h2 {
  margin: 0;
  font-size: 1.05rem;
}

.muted {
  color: #5d6962;
  margin: 0;
  flex: 1;
}

.button {
  border: 0;
  border-radius: 6px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
}

.button.primary {
  background: #2f8f5b;
  color: #ffffff;
}

.button.secondary {
  background: #eef1ef;
  color: #17201b;
}

.user-section {
  max-width: 1080px;
  margin: 24px auto 0;
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-section p {
  margin: 0;
}

@media (max-width: 760px) {
  .page {
    padding: 28px 18px;
  }
}
</style>