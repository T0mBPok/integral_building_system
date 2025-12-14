<template>
  <div class="auth-container">
    <h2>Регистрация</h2>
    <form class="auth-form" @submit.prevent="submitForm">
      <input
        v-model="form.username"
        type="text"
        placeholder="Логин"
        required
      />
      <p v-if="errors.username" class="error">{{ errors.username }}</p>

      <input
        v-model="form.email"
        type="email"
        placeholder="Email"
        required
      />
      <p v-if="errors.email" class="error">{{ errors.email }}</p>

      <input
        v-model="form.password"
        type="password"
        placeholder="Пароль"
        required
      />
      <p v-if="errors.password" class="error">{{ errors.password }}</p>

      <input
        v-model="form.confirmPassword"
        type="password"
        placeholder="Повторите пароль"
        required
      />
      <p v-if="errors.confirmPassword" class="error">{{ errors.confirmPassword }}</p>

      <button type="submit">Зарегистрироваться</button>

      <p class="auth-switch">
        Уже есть аккаунт?
        <router-link to="/login">Войти</router-link>
      </p>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

const emit = defineEmits(['submit'])

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const errors = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// Валидация формы
function validateForm() {
  let valid = true

  // Сбрасываем ошибки
  Object.keys(errors).forEach(key => errors[key] = '')

  // Username: 3-20 символов
  if (form.username.length < 3 || form.username.length > 20) {
    errors.username = 'Имя от 3 до 20 символов'
    valid = false
  }

  // Email: простой RegExp
  const emailPattern = /^\S+@\S+\.\S+$/
  if (!emailPattern.test(form.email)) {
    errors.email = 'Неверный формат email'
    valid = false
  }

  // Пароль: 5-50 символов
  if (form.password.length < 5 || form.password.length > 50) {
    errors.password = 'Пароль от 5 до 50 символов'
    valid = false
  }

  // Подтверждение пароля
  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Пароли не совпадают'
    valid = false
  }

  return valid
}

function submitForm() {
  if (!validateForm()) return

  emit('submit', {
    username: form.username,
    email: form.email,
    password: form.password
  })
}
</script>

<style scoped>
.error {
  color: red;
  font-size: 0.9rem;
  margin: 0 0 10px;
}
</style>
