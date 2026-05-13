<template>
  <div class="auth-container">
    <AuthForm @submit="handleLogin" />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import AuthForm from '../components/AuthForm.vue'
import '../assets/styles/login.css' 
import api from '../services/api'
import { onMounted } from 'vue'

const router = useRouter()

async function handleLogin(data) {
  try {
    const res = await api.post('/user/login/', data)

    router.push(router.currentRoute.value.query.redirect || '/projects')
  } catch (err) {
    console.error('Ошибка логина:', err)
  }
}

onMounted(async () => {
  try {
    const response = await api.get('/user/check/')
    if (response.data.ok) router.push('/projects')
  } catch (error) {
    console.error("Вы не авторизированы!", error)
  }
})
</script>
