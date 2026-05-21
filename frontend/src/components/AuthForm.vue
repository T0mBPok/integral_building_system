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

const email = ref('')
const password = ref('')
const error = ref('')

const emit = defineEmits(['submit'])

async function onSubmit() {
  error.value = ''
  if (!email.value || !password.value) {
    error.value = 'Неверные данные для авторизации'
    return
  }
  emit('submit', {
    email: email.value,
    password: password.value
  })
}
</script>

<style scoped>
.error {
  color: red;
  margin-bottom: 10px;
}
</style>
