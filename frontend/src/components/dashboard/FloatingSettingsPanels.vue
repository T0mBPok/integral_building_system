<template>
  <div v-if="weightMethod === 'manual' && manualWeights.length" class="manual-weights-panel">
    <div v-for="weight in manualWeights" :key="weight.indicator_name" class="weight-input-row">
      <label>{{ weight.indicator_name }}</label>
      <input
        :value="weight.weight"
        type="number"
        min="0"
        step="0.01"
        @input="updateManualWeight(weight.indicator_name, Number($event.target.value))"
      />
    </div>
  </div>

  <div v-if="normalizationSettings.length" class="normalization-details-panel">
    <div v-for="entry in normalizationSettings" :key="entry.indicator_name" class="norm-detail">
      <span>{{ entry.indicator_name }}</span>
      <select :value="entry.method" @change="updateNormalization(entry.indicator_name, 'method', $event.target.value)">
        <option v-for="method in normalizationMethods" :key="method.value" :value="method.value">
          {{ method.label }}
        </option>
      </select>
      <input
        :value="entry.output_name"
        placeholder="Название"
        @input="updateNormalization(entry.indicator_name, 'output_name', $event.target.value)"
      />
    </div>
  </div>

  <div v-if="statusMessage" class="floating-status" :class="statusTone">{{ statusMessage }}</div>
</template>

<script setup>
const props = defineProps({
  weightMethod: { type: String, required: true },
  manualWeights: { type: Array, required: true },
  normalizationSettings: { type: Array, required: true },
  normalizationMethods: { type: Array, required: true },
  statusMessage: { type: String, default: '' },
  statusTone: { type: String, default: 'neutral' }
})

const emit = defineEmits(['update:manualWeights', 'update:normalizationSettings'])

function updateManualWeight(indicatorName, value) {
  emit('update:manualWeights', props.manualWeights.map((weight) => (
    weight.indicator_name === indicatorName ? { ...weight, weight: value } : weight
  )))
}

function updateNormalization(indicatorName, field, value) {
  emit('update:normalizationSettings', props.normalizationSettings.map((entry) => (
    entry.indicator_name === indicatorName ? { ...entry, [field]: value } : entry
  )))
}
</script>
