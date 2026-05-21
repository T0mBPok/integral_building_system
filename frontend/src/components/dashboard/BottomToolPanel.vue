<template>
  <div class="bottom-tool-panel">
    <button class="toolbar-button" @click="$emit('open-indicators')" :disabled="!projectId || isBusy">
      + Показатели
    </button>
    <button class="icon-button function-button" title="Функция" @click="$emit('open-function')" :disabled="!projectId || isBusy">
      f()
    </button>
    <button class="toolbar-button primary" @click="$emit('calculate')" :disabled="!canCalculate || isBusy">
      Рассчитать
    </button>
    <div class="zoom-tools">
      <button class="icon-button" title="Уменьшить" @click="$emit('zoom', -0.1)">−</button>
      <button class="icon-button zoom-label-button" title="По размеру" @click="$emit('fit')">{{ zoomLabel }}</button>
      <button class="icon-button" title="Увеличить" @click="$emit('zoom', 0.1)">+</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  projectId: { type: String, default: null },
  isBusy: { type: Boolean, default: false },
  canCalculate: { type: Boolean, default: false },
  zoomLabel: { type: String, required: true }
})

const emit = defineEmits([
  'open-indicators',
  'open-function',
  'calculate',
  'zoom',
  'fit'
])
</script>
