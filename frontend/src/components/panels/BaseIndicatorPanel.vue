<script setup>
import { computed } from 'vue'
import { modelStore } from '../../store/modelStore'

const selected = computed(() =>
  modelStore.indicators.find(i => i.id === modelStore.selectedId)
)
</script>
<style src="../../assets/styles/panel.css"></style>

<template>
  <div class="panel" v-if="selected">
    <h3>Базовый показатель</h3>

    <label>Короткое название</label>
    <input v-model="selected.shortTitle" />

    <label>Цвет</label>
    <input type="color" v-model="selected.color" />

    <label>Описание</label>
    <textarea v-model="selected.description" />

    <label>Данные</label>
    <div
      v-for="(src, idx) in selected.dataSources"
      :key="idx"
      class="row-inline"
    >
      <input
        class="code-input"
        v-model="src.code"
        placeholder="R"
      />
      <input
        class="name-input"
        v-model="src.name"
        placeholder="Название показателя"
      />
    </div>

    <label>Диапазон</label>
    <div class="row-inline">
      <span class="muted">c</span>
      <input v-model="selected.range.from" />
      <span class="muted">по</span>
      <input v-model="selected.range.to" />
    </div>

    <label>Формула</label>
    <input v-model="selected.formula" />
  </div>
</template>
