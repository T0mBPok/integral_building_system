<script setup>
import { computed } from 'vue'
import { modelStore, randomizeWeights } from '../../store/modelStore'

const toggleIndicator = (id) => {
  const list = modelStore.weightsConfig.indicatorIds
  const idx = list.indexOf(id)
  if (idx === -1) list.push(id)
  else list.splice(idx, 1)
}
</script>

<template>
  <div class="panel">
    <h3>{{ modelStore.weightsConfig.title }}</h3>

    <label>Показатели</label>
    <div
      v-for="ind in modelStore.indicators"
      :key="ind.id"
      class="row-inline"
    >
      <input
        type="checkbox"
        :checked="modelStore.weightsConfig.indicatorIds.includes(ind.id)"
        @change="toggleIndicator(ind.id)"
      />
      <span class="name-input">{{ ind.shortTitle || ind.title }}</span>
      <input
        v-if="modelStore.weightsConfig.indicatorIds.includes(ind.id)"
        type="number"
        min="0"
        step="0.001"
        v-model.number="ind.weight"
      />
    </div>

    <label>Метод расчета весов</label>
    <select v-model="modelStore.weightsConfig.method">
      <option value="manual">Вручную</option>
      <option value="random">Энтропийный метод</option>
    </select>

    <button
      v-if="modelStore.weightsConfig.method === 'random'"
      @click="randomizeWeights()"
    >
      Рассчитать
    </button>
  </div>
</template>

<style src="../../assets/styles/panel.css"></style>