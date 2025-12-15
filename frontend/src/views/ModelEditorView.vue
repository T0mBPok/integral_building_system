<script setup>
import Canvas from '../components/canvas/Canvas.vue'
import BaseIndicatorPanel from '../components/panels/BaseIndicatorPanel.vue'
import WeightPanel from '../components/panels/WeightPanel.vue'
import AggregatedPanel from '../components/panels/AggregatedPanel.vue'
import { modelStore, addIndicator } from '../store/modelStore'
</script>

<template>
  <div class="editor-layout">
    <!-- КАНВАЗ -->
    <div class="canvas-wrap">
      <Canvas />
    </div>  

    <!-- ПРАВАЯ ПАНЕЛЬ -->
    <aside class="right-panel">
      <BaseIndicatorPanel v-if="modelStore.mode === 'base'" />
      <WeightPanel v-if="modelStore.mode === 'weights'" />
      <AggregatedPanel v-if="modelStore.mode === 'aggregate'" />
    </aside>

    <!-- НИЖНЕЕ МЕНЮ-КАПСУЛА -->
    <div class="bottom-menu">
      <button
        :class="{ active: modelStore.mode === 'base' }"
        @click="() => { modelStore.mode = 'base'; addIndicator() }"
      >
        Базовый показатель
      </button>

      <button
        :class="{ active: modelStore.mode === 'weights' }"
        @click="modelStore.mode = 'weights'"
      >
        Рассчитать веса
      </button>

      <button
        :class="{ active: modelStore.mode === 'aggregate' }"
        @click=" () => {modelStore.mode = 'aggregate'
        modelStore.aggregateVisible = true}"
      >
        Свертка
      </button>
    </div>
  </div>
</template>

<style src="../assets/styles/editor.css"></style>
