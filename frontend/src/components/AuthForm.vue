<template>
  <div class="auth-container">
    <h2>Вход</h2>
    <form class="auth-form" @submit.prevent="onSubmit">
      <input v-model="email" type="text" placeholder="Почта" />
      <input v-model="password" type="password" placeholder="Пароль" />
      <p v-if="error" class="error">{{ error }}</p>
      <button type="submit">Войти</button>
      <router-link to="/register" class="register-link">
        Нет аккаунта? Зарегистрироваться
      </router-link>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const error = ref('')

const router = useRouter()

async function onSubmit() {
  error.value = ''
  try {
    const res = await api.post('/user/login/', {
      email: email.value,
      password: password.value
    })

    // Если сервер вернул ok === true, переходим в чат
    if (res.data.ok) {
      router.push('/chat')
    } else {
      error.value = 'Неверные данные для авторизации'
    }
  } catch (e) {
    console.error(e)
    error.value = 'Неверные данные для авторизации'
  }
}
</script>

<style scoped>
.error {
  color: red;
  margin-bottom: 10px;
}
</style>
