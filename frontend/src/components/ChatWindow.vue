<!-- <template>
  <div class="chat-window">
    <template v-if="messages && messages.length">
      <div class="messages">
        <div
          v-for="m in messages"
          :key="m.id"
          :class="['message', m.sender === 'me' ? 'sent' : 'received']" 
        >
          <div class="bubble">{{ m.text }}</div>
        </div>
      </div>
      <div class="input-area">
        <input
          v-model="newMessage"
          type="text"
          placeholder="Напишите сообщение..."
          @keyup.enter="submit"
        />
        <button class="send-btn" @click="submit">➤</button>
      </div>
    </template>

    <div v-else class="chat-empty">
      <p>Выберите чат, чтобы начать переписку</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  messages: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['sendMessage'])
const newMessage = ref('')

function submit() {
  if (!newMessage.value.trim()) return
  emit('sendMessage', newMessage.value)
  newMessage.value = ''
}
</script> -->
<template>
  <div class="chat-window">
    <!-- Сообщения -->
    <div class="messages" v-if="messages && messages.length">
      <div
        v-for="m in messages"
        :key="m.id"
        :class="['message', m.sender === 'me' ? 'sent' : 'received']" 
      >
        <div class="bubble">{{ m.text }}</div>
      </div>
    </div>

    <!-- Надпись "Пока нет сообщений" для пустого чата -->
    <div v-if="(!messages || !messages.length)" class="chat-empty">
      <p>Пока нет сообщений</p>
    </div>

    <!-- Поле ввода всегда показываем, если выбран чат -->
    <div class="input-area" v-if="messages !== null">
      <input
        v-model="newMessage"
        type="text"
        placeholder="Напишите сообщение..."
        @keyup.enter="submit"
      />
      <button class="send-btn" @click="submit">➤</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  messages: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['sendMessage'])
const newMessage = ref('')

function submit() {
  if (!newMessage.value.trim()) return
  emit('sendMessage', newMessage.value)
  newMessage.value = ''
}
</script>
