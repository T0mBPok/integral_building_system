<script setup>
import { modelStore } from '../../store/modelStore'

const calcX = (idx) => {
  const count = modelStore.indicators.length || 1
  const step = 220
  const totalWidth = (count - 1) * step
  const start = -totalWidth / 2
  return 800 + start + idx * step
}
</script>

<template>
  <svg class="connections" viewBox="0 0 1600 900">
    <line
      v-for="(ind, idx) in modelStore.indicators"
      :key="ind.id"
      x1="800"
      y1="220"
      :x2="calcX(idx)"
      y2="450"
    />
  </svg>
</template>


<style src="../../assets/styles/lines.css"></style>