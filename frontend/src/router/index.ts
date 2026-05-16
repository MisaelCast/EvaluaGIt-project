import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
    },
    {
      path: '/projects',
      name: 'projects',
      component: () => import('@/views/ProjectsView.vue'),
    },
    {
      path: '/projects/:projectId',
      name: 'project-detail',
      component: () => import('@/views/ProjectDetailView.vue'),
    },
    {
      path: '/projects/:projectId/settings',
      name: 'project-settings',
      component: () => import('@/views/ProjectSettingsView.vue'),
    },
    {
      path: '/projects/:projectId/analysis/:analysisRunId',
      name: 'analysis-result',
      component: () => import('@/views/AnalysisResultView.vue'),
    },
  ],
})

export default router