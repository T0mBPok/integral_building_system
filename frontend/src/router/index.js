import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProjectsView from '../views/ProjectsView.vue'
import FilesView from '../views/FilesView.vue'
import Dashboard from '../components/Dashboard.vue'
import api from '../services/api'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/projects' },
    { path: '/login', name: 'Login', component: LoginView, meta: { public: true } },
    { path: '/register', name: 'Register', component: RegisterView, meta: { public: true } },
    { path: '/projects', name: 'Projects', component: ProjectsView },
    { path: '/files', name: 'Files', component: FilesView },
    { path: '/project/:id', name: 'ProjectDashboard', component: Dashboard },
    { path: '/:pathMatch(.*)*', redirect: '/projects' }
  ]
})

router.beforeEach(async (to) => {
  const isPublic = to.meta.public
  try {
    const { data } = await api.get('/user/check/')
    if (isPublic && data.ok) return '/projects'
    return true
  } catch (error) {
    if (isPublic) return true
    return {
      path: '/login',
      query: { redirect: to.fullPath }
    }
  }
})

export default router
