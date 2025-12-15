<script setup>
import { modelStore } from '../../store/modelStore'
import Node from './Node.vue'

const onIndicatorClick = (ind) => {
  modelStore.selectedId = ind.id
  modelStore.mode = 'base'        // меняем только правую панель
}
</script>

<template>
  <div class="canvas">
    <!-- ЛИНИИ ВСЕГДА -->
    <svg class="connections">
      <line
        v-for="(ind, i) in modelStore.indicators"
        :key="ind.id"
        x1="50%"
        y1="170"
        :x2="calcX(i)"
        y2="360"
      />
    </svg>

    <!-- АГРЕГИРОВАННЫЙ УЗЕЛ -->
    <div class="level" v-if="modelStore.aggregateVisible">
        <Node
            type="aggregate"
            :title="modelStore.aggregate.title"
            @click="() => { modelStore.mode = 'aggregate' }"
        />
    </div>

    <!-- БАЗОВЫЕ ПОКАЗАТЕЛИ ВСЕГДА -->
    <div class="level bottom">
      <Node
        v-for="(ind, i) in modelStore.indicators"
        :key="ind.id"
        :title="ind.title"
        :weight="(modelStore.mode === 'weights' || modelStore.mode === 'aggregate') &&
                modelStore.weightsConfig?.indicatorIds?.includes(ind.id)
                ? ind.weight
                : undefined"
        @click="onIndicatorClick(ind)"
      />
    </div>
  </div>
</template>


<script>
export default {
  methods: {
    calcX(i) {
      const count = this.$store?.indicators?.length || 1
      return `${50 + (i - (count - 1) / 2) * 18}%`
    }
  }
}
</script>

<style src="../../assets/styles/canvas.css"></style>
