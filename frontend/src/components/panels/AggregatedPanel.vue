<script setup>
import { aggregatedValue, modelStore } from '../../store/modelStore'
</script>

<template>
  <div class="panel">
    <h3>Показатель роста населения</h3>

    <label>Короткое название</label>
    <input v-model="modelStore.aggregate.shortTitle" />

    <label>Описание</label>
    <textarea v-model="modelStore.aggregate.description" />

    <label>Базовые показатели</label>
    <div
      v-for="ind in modelStore.indicators"
      :key="ind.id"
      class="row-inline"
    >
      <input
        class="code-input"
        v-model="ind.shortTitle"
      />
      <input
        class="name-input"
        v-model="ind.title"
      />
    </div>

    <label>Формула</label>
    <input v-model="modelStore.aggregate.formula" />

    <label>Метод нормализации</label>
    <select v-model="modelStore.aggregate.normalizationMethod">
      <option value="minmax">Min/max method</option>
      <option value="none">Без нормализации</option>
    </select>

    <label>Экспорт</label>
    <select v-model="modelStore.aggregate.exportFormat">
      <option value="txt">TXT</option>
      <option value="csv">CSV</option>
      <option value="json">JSON</option>
    </select>

    <label>Результат</label>
    <input :value="aggregatedValue" readonly />
  </div>
</template>
