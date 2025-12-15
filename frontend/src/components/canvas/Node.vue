<script setup>
import { modelStore } from '../../store/modelStore'

const props = defineProps({
  title: String,
  weight: Number,
  type: String
})

const onNodeClick = () => {
  // клик по самой ноде – вызываем обычный click (Canvas его уже ловит)
}

const onWeightClick = (event) => {
  event.stopPropagation()
  // показываем панель весов
  modelStore.mode = 'weights'
}
</script>

<template>
  <div class="node-wrapper" @click="onNodeClick">
    <div
      v-if="weight !== undefined"
      class="weight"
      @click="onWeightClick"
    >
      {{ weight }}
    </div>

    <div :class="['node', type]">
      {{ title }}
    </div>
  </div>
</template>
