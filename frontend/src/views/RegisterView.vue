<template>
  <div class="auth-container">
    <RegisterForm @submit="handleRegister" />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import RegisterForm from '../components/RegisterForm.vue'
import '../assets/styles/auth.css'
import api from '../services/api'
import { ref, onMounted } from 'vue'

const router = useRouter()

async function handleRegister(data) {
  try {
    const res = await api.post('/user/register/', data)

    alert('Регистрация успешна! Авторизуйтесь.')
    router.push('/login')
  } catch (err) {
    alert(err)
  }
}

onMounted(async () => {
  try{
    const response = await api.get('/user/check/')
    if (response.data.ok) router.push('/chat')
  } catch (error) {
    console.error("Вы не авторизированы!", error)
  }
})
</script>
