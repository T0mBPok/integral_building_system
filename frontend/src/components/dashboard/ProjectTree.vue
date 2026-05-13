<template>
  <div class="board-canvas" :style="canvasStyle">
    <section class="tree-level aggregate-level">
      <article class="flow-node aggregate-node top-node" :class="{ selected: selectedNodeId === 'aggregate' }" @click="$emit('select-node', 'aggregate', 'aggregate')">
        <div class="node-kicker">Интегральный показатель</div>
        <h3>{{ integralTitle }}</h3>
        <p>{{ resultSummary }}</p>
        <div v-if="lastResult?.ranking?.length" class="top-result">
          <span>{{ lastResult.ranking[0].region }}</span>
          <strong>{{ formatNumber(lastResult.ranking[0].value) }}</strong>
        </div>
      </article>
    </section>

    <section class="tree-level weight-level">
      <article class="flow-node weight-node central-node" :class="{ selected: selectedNodeId === 'weights' }" @click="$emit('select-node', 'weights', 'weights')">
        <div class="node-kicker">{{ methodLabel(weightMethod, weightMethods) }}</div>
        <h3>Расчет весов</h3>
        <div class="weight-stack">
          <span v-for="weight in effectiveWeights" :key="weight.indicator_name">
            {{ weight.indicator_name }} · {{ formatNumber(weight.weight) }}
          </span>
          <span v-if="effectiveWeights.length === 0">Веса появятся после выбора показателей</span>
        </div>
      </article>
    </section>

    <section class="tree-level normalization-level">
      <article
        v-for="entry in normalizationSettings"
        :key="entry.indicator_name"
        class="flow-node norm-node"
        :class="{ selected: selectedNodeId === `norm:${entry.indicator_name}` }"
        @click="$emit('select-node', 'normalization', `norm:${entry.indicator_name}`)"
      >
        <div class="node-kicker">{{ methodLabel(entry.method, normalizationMethods) }}</div>
        <h3>{{ entry.output_name || entry.indicator_name }}</h3>
        <p>{{ entry.indicator_name }}</p>
      </article>
      <div v-if="normalizationSettings.length === 0" class="empty-node">
        Нормализованные показатели появятся после добавления базовых
      </div>
    </section>

    <section class="tree-level base-level">
      <article
        v-for="indicator in projectIndicators"
        :key="indicator.indicator_id"
        class="flow-node base-node"
        :class="{ selected: selectedNodeId === indicator.indicator_id }"
        @click="$emit('select-node', 'base', indicator.indicator_id)"
      >
        <div class="node-kicker">Файл</div>
        <h3>{{ indicator.name }}</h3>
        <p>{{ indicator.description || 'Базовый показатель' }}</p>
      </article>
      <div v-if="projectIndicators.length === 0" class="empty-node" @click="$emit('open-indicators')">
        Добавьте показатели из загруженных файлов
      </div>
    </section>
  </div>
</template>

<script setup>
defineProps({
  canvasStyle: { type: Object, required: true },
  selectedNodeId: { type: String, default: null },
  integralTitle: { type: String, required: true },
  resultSummary: { type: String, required: true },
  lastResult: { type: Object, default: null },
  weightMethod: { type: String, required: true },
  weightMethods: { type: Array, required: true },
  effectiveWeights: { type: Array, required: true },
  normalizationSettings: { type: Array, required: true },
  normalizationMethods: { type: Array, required: true },
  projectIndicators: { type: Array, required: true },
  methodLabel: { type: Function, required: true },
  formatNumber: { type: Function, required: true }
})

defineEmits(['select-node', 'open-indicators'])
</script>
