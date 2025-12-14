import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ChatView from '../views/ChatView.vue'
import api from '../services/api'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'Login', component: LoginView },
    { path: '/register', name: 'Register', component: RegisterView },
    { path: '/chat', name: 'Chat', component: ChatView }
  ]
})

router.beforeEach(async (to, from, next) => {
  if (to.name === 'Chat') {
    try{
      const response = await api.get('/user/check/')
      if (!response.data.ok) return next('/login')
    } catch (error) {
      return next('/login')
    }
  }
  next()
})

export default router