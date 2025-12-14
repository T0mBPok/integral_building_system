<template>
  <div class="sidebar">
    <div class="sidebar-header">Мои чаты</div>
    <ul class="chat-list">
      <li
        v-for="chat in chats"
        :key="chat.id"
        class="chat-item"
        :class="{ active: chat.id === activeChatId }"
        @click="$emit('selectChat', chat.id)"
      >
        <div class="avatar">{{ chat.username[0].toUpperCase() }}</div>
        <!-- <div class="avatar">{{ chat.name[0] }}</div> -->
        <div class="chat-info">
          <div class="chat-name">{{ chat.username }}</div>
           <!-- <div class="chat-name">{{ chat.name }}</div> 
           <div class="chat-last">{{ chat.last }}</div> -->
        </div>
      </li>
    </ul>
    <button class="logout-button" @click="logout">
        Выйти
    </button>
  </div>
</template>

<script setup> 
import { useRouter } from 'vue-router'
import api from '../services/api'
import router from '../router'
import { disconnectWebSocket } from '../services/ws'

defineProps({
  chats: Array,
  activeChatId: Number
})

async function logout() {
  try {
    await api.post('/user/logout/')
  } catch (e) {
    console.error('Ошибка при выходе:', e)
  } 
  disconnectWebSocket()
  router.push('/login')
}
</script>
