<template>
  <div class="chat-header">
    <div class="chat-user">
      <div class="avatar">{{ chat.name[0] }}</div>
      <div>
        <div class="name">{{ chat.name }}</div>
        <div class="status">в сети</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  chat: Object
})
</script>
