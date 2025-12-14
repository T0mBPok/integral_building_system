<template>
  <div class="app">
    <Sidebar
      :chats="chats"
      :activeChatId="activeChatId"
      @selectChat="setActiveChat"
    />
    <div class="chat-area" v-if="activeChat">
      <ChatHeader :chat="activeChat" />
      <ChatWindow
        :messages="activeChat.messages"
        @sendMessage="sendMessage"
      />
    </div>
    <div class="chat-empty" v-else>
      <p>Выберите чат, чтобы начать переписку</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import ChatWindow from '../components/ChatWindow.vue'
import ChatHeader from '../components/ChatHeader.vue'
import api from '../services/api'
import {
  connectWebSocket,
  sendWSMessage,
  subscribeWS
} from '../services/ws'

import '../assets/styles/app.css'
import '../assets/styles/sidebar.css'
import '../assets/styles/chatHeader.css'
import '../assets/styles/chatWindow.css'


const currentUserId = ref(null)
const chats = ref([
  // {
  //   id: 1,
  //   name: 'Алексей',
  //   last: 'Привет!',
  //   messages: [
  //     { id: 1, text: 'Привет!', sender: 'them' },
  //     { id: 2, text: 'Как дела?', sender: 'them' },
  //     { id: 3, text: 'Нормально, а ты?', sender: 'me' }
  //   ]
  // },
  // {
  //   id: 2,
  //   name: 'Марина',
  //   last: 'До встречи!',
  //   messages: [
  //     { id: 1, text: 'Привет 👋', sender: 'me' },
  //     { id: 2, text: 'Когда встретимся?', sender: 'me' },
  //     { id: 3, text: 'Завтра в 7.', sender: 'them' },
  //     { id: 4, text: 'До встречи!', sender: 'them' }
  //   ]
  // }
])

const activeChatId = ref(null)

const activeChat = computed(() =>
  chats.value.find(c => c.id === activeChatId.value)
)

async function loadUsers() {
  try {
    const response = await api.get('/user/list/')
    const meRes = await api.get('/user/me/')
    currentUserId.value = meRes.data.id
    
    chats.value = response.data
      .filter(u => u.id !== currentUserId.value)
      .map(u => ({
        id: u.id,
        username: u.username,
        email: u.email,
        messages: [],
        name: u.username, 
        last: ''           
      }))
  } catch (err) {
    console.error('Ошибка при загрузке пользователей:', err)
  }
}

function handleIncomingMessage(msg) {
  if (!msg) return
  const data = msg
  const senderId = data.sender_id
  const recipientId = data.recipient_id
  const chatId = senderId === currentUserId.value ? recipientId : senderId
  const chat = chats.value.find(c => c.id === chatId)
  if (!chat) return

  chat.messages.push({
    id: data.id,
    text: data.content,
    sender: senderId === currentUserId.value ? 'me' : 'them'
  })
  chat.last = data.content
}

async function setActiveChat(userId) {
  activeChatId.value = userId //кроме этой все комментить для моковых
  const user = chats.value.find(u => u.id === userId)
  if (!user) return

  // Загружаем историю сообщений
  try {
    const response = await api.get(`/chat/messages/${userId}`)
    user.messages = response.data.map(m => ({
      id: m.id,
      text: m.content,
      sender: m.sender_id === currentUserId.value ? 'me' : 'them'
    }))
    console.log(response.data, currentUserId, user.messages)

    user.last = user.messages.length
    ? user.messages[user.messages.length - 1].text
    : ''
    user.name = user.username
  } catch (e) {
    console.error('Ошибка при загрузке сообщений:', e)
    user.messages = []
  }
}

// Для моковых раскомментить ---------------------------------------!!!
// function sendMessage(text) {
//   if (!activeChat.value || !text.trim()) return
//   activeChat.value.messages.push({
//     id: Date.now(),
//     text,
//     sender: 'me'
//   })
//   activeChat.value.last = text
// }

// async function sendMessage(text) {
//   if (!activeChat.value || !text.trim()) return

//   const recipientId = activeChat.value.id
//   try {
//     await api.post('/chat/messages', {
//       recipient_id: recipientId,
//       content: text
//     })
//     // Добавляем сообщение в локальный массив
//     activeChat.value.messages.push({
//       id: Date.now(),
//       text,
//       sender: 'me'
//     })
//   } catch (err) {
//     console.error('Ошибка при отправке сообщения:', err)
//   }
// }

function sendMessage(text) {
  if (!activeChat.value || !text.trim()) return
  sendWSMessage({
    recipient_id: activeChat.value.id,
    content: text
  })
  // activeChat.value.messages.push({
  //   id: Date.now(),
  //   text,
  //   sender: 'me'
  // })
  // activeChat.value.last = text
}

onMounted(async () => {
  await loadUsers()
  connectWebSocket()
  subscribeWS(handleIncomingMessage)
})
</script>
