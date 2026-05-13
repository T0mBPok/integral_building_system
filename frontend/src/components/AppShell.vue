<template>
  <div class="app-shell">
    <aside class="app-nav">
      <div class="app-brand">
        <strong>IBS</strong>
        <span>Integral Build System</span>
      </div>
      <nav>
        <router-link to="/projects">Проекты</router-link>
        <router-link to="/files">Файлы</router-link>
      </nav>
      <button class="nav-logout" @click="logout">Выйти</button>
    </aside>
    <main class="app-content">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

async function logout() {
  try {
    await api.post('/user/logout/')
  } finally {
    router.push('/login')
  }
}
</script>
