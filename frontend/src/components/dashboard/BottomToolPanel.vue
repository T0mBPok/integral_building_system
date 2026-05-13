<template>
  <div class="bottom-tool-panel">
    <div class="tool-group">
      <span>Нормализация</span>
      <select :value="bulkNormalizationMethod" @change="updateBulkNormalization($event.target.value)">
        <option v-for="method in normalizationMethods" :key="method.value" :value="method.value">
          {{ method.label }}
        </option>
      </select>
    </div>
    <div class="tool-group">
      <span>Веса</span>
      <select :value="weightMethod" @change="$emit('update:weightMethod', $event.target.value)">
        <option v-for="method in weightMethods" :key="method.value" :value="method.value">
          {{ method.label }}
        </option>
      </select>
    </div>
    <div class="tool-group compact-tool">
      <span>Свертка</span>
      <select :value="aggregationMethod" disabled>
        <option value="sum">Сумма</option>
      </select>
    </div>
    <div class="tool-group year-tool">
      <span>Год</span>
      <input :value="calculationYear" placeholder="2024" @input="$emit('update:calculationYear', $event.target.value)" />
    </div>
    <button class="toolbar-button" @click="$emit('open-indicators')" :disabled="!projectId || isBusy">
      + Показатели
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
  bulkNormalizationMethod: { type: String, required: true },
  normalizationMethods: { type: Array, required: true },
  weightMethod: { type: String, required: true },
  weightMethods: { type: Array, required: true },
  aggregationMethod: { type: String, required: true },
  calculationYear: { type: String, default: '' },
  projectId: { type: String, default: null },
  isBusy: { type: Boolean, default: false },
  canCalculate: { type: Boolean, default: false },
  zoomLabel: { type: String, required: true }
})

const emit = defineEmits([
  'update:bulkNormalizationMethod',
  'update:weightMethod',
  'update:calculationYear',
  'apply-normalization',
  'open-indicators',
  'calculate',
  'zoom',
  'fit'
])

function updateBulkNormalization(value) {
  emit('update:bulkNormalizationMethod', value)
  emit('apply-normalization', value)
}
</script>
