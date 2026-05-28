import { createRouter, createWebHistory } from 'vue-router'

import { supabase } from '@/lib/supabase'
import { getMe } from '@/services/api'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/onboarding',
      name: 'onboarding',
      component: () => import('@/views/OnboardingView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true, role: 'PROFESSOR' },
    },
    {
      path: '/student/dashboard',
      name: 'student-dashboard',
      component: () => import('@/views/StudentDashboardView.vue'),
      meta: { requiresAuth: true, role: 'STUDENT' },
    },
    {
      path: '/projects',
      name: 'projects',
      component: () => import('@/views/ProjectsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/deliveries',
      name: 'deliveries',
      component: () => import('@/views/DeliveriesView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/projects/:projectId',
      name: 'project-detail',
      component: () => import('@/views/ProjectDetailView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/projects/:projectId/settings',
      name: 'project-settings',
      component: () => import('@/views/ProjectSettingsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/projects/:projectId/analysis/:analysisRunId',
      name: 'analysis-result',
      component: () => import('@/views/AnalysisResultView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth) return true

  const { data } = await supabase.auth.getSession()
  if (!data.session) {
    return { path: '/', replace: true }
  }

  const expectedRole = typeof to.meta.role === 'string' ? to.meta.role : null
  if (!expectedRole) return true

  try {
    const me = await getMe()

    if (me.role === 'UNASSIGNED') {
      return { path: '/onboarding', replace: true }
    }

    if (me.role === expectedRole) return true

    if (me.role === 'STUDENT') {
      return { path: '/student/dashboard', replace: true }
    }

    if (me.role === 'PROFESSOR') {
      return { path: '/dashboard', replace: true }
    }
  } catch {
    return { path: '/', replace: true }
  }

  return true
})

export default router
