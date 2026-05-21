<template>
  <div class="board-canvas" :style="canvasStyle">
    <section class="tree-root aggregate-level">
      <article class="flow-node aggregate-node top-node" :class="{ selected: selectedNodeId === 'aggregate' }" @click="$emit('select-node', 'aggregate', 'aggregate')">
        <h3 :style="titleStyle('Интегральный показатель')">Интегральный показатель</h3>
        <strong class="node-value">{{ aggregateValue }}</strong>
      </article>
    </section>

    <section v-if="indicatorBranches.length" class="indicator-branches">
      <div v-for="branch in indicatorBranches" :key="branch.id" class="indicator-branch">
        <article
          class="flow-node weight-node branch-node"
          :class="{ selected: selectedNodeId === `weight:${branch.entry.indicator_name}` }"
          @click="$emit('select-node', 'weight', `weight:${branch.entry.indicator_name}`)"
        >
          <div class="node-kicker">{{ weightLabel(branch.entry) }}</div>
          <h3 :style="titleStyle(branch.entry.output_name || branch.entry.indicator_name)">{{ branch.entry.output_name || branch.entry.indicator_name }}</h3>
          <strong class="node-value">{{ weightedValue(branch.entry) }}</strong>
        </article>

        <article
          class="flow-node norm-node branch-node"
          :class="{ selected: selectedNodeId === `norm:${branch.entry.indicator_name}` }"
          @click="$emit('select-node', 'normalization', `norm:${branch.entry.indicator_name}`)"
        >
          <div class="node-kicker">{{ methodLabel(branch.entry.method, normalizationMethods) }}</div>
          <h3 :style="titleStyle(branch.entry.output_name || branch.entry.indicator_name)">{{ branch.entry.output_name || branch.entry.indicator_name }}</h3>
          <strong class="node-value">{{ normalizedValue(branch.entry) }}</strong>
        </article>

        <article
          class="flow-node branch-node"
          :class="[branch.kind === 'function' ? 'function-node' : 'base-node', { selected: selectedNodeId === branch.nodeId }]"
          @click="$emit('select-node', branch.kind, branch.nodeId)"
        >
          <div class="node-kicker">{{ branch.kind === 'function' ? 'Функция' : 'Базовый' }}</div>
          <h3 :style="titleStyle(branch.title)">{{ branch.title }}</h3>
          <strong class="node-value">{{ branch.kind === 'function' ? functionValue(branch.func) : baseValue(branch.indicator) }}</strong>
        </article>
      </div>
    </section>

    <div v-else class="empty-node" @click="$emit('open-indicators')">
      Добавьте показатели из загруженных файлов
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
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
  customIndicators: { type: Array, default: () => [] },
  availableIndicators: { type: Array, default: () => [] },
  calculationYear: { type: String, default: '' },
  methodLabel: { type: Function, required: true },
  formatNumber: { type: Function, required: true }
})

defineEmits(['select-node', 'open-indicators'])

const targetYear = computed(() => props.lastResult?.year || props.calculationYear)

const indicatorBranches = computed(() => [
  ...props.projectIndicators.map((indicator) => {
    const entry = entryForName(indicator.name)
    return {
      id: indicator.indicator_id,
      nodeId: indicator.indicator_id,
      kind: 'base',
      title: indicator.name,
      indicator,
      entry
    }
  }),
  ...props.customIndicators.map((func) => {
    const entry = entryForName(func.name)
    return {
      id: `func:${func.name}`,
      nodeId: `func:${func.name}`,
      kind: 'function',
      title: func.name,
      func,
      entry
    }
  })
])

function entryForName(name) {
  return props.normalizationSettings.find((item) => item.indicator_name === name) || {
    indicator_name: name,
    output_name: name,
    method: 'minmax'
  }
}

const aggregateValue = computed(() => {
  if (props.lastResult?.integral_value !== null && props.lastResult?.integral_value !== undefined) {
    return props.formatNumber(props.lastResult.integral_value)
  }
  const values = props.lastResult?.integral_values || []
  if (!values.length) return '—'
  const average = values.reduce((sum, item) => sum + Number(item.value || 0), 0) / values.length
  return props.formatNumber(average)
})

function titleStyle(title) {
  const length = String(title || '').length
  const size = length > 44 ? 8 : length > 38 ? 9 : length > 32 ? 10 : length > 26 ? 11 : length > 20 ? 13 : 15
  return { fontSize: `${size}px` }
}

function weightLabel(entry) {
  const name = entry.output_name || entry.indicator_name
  const weight = props.effectiveWeights.find((item) => item.indicator_name === name)
  return weight ? `Вес ${props.formatNumber(weight.weight)}` : props.methodLabel(props.weightMethod, props.weightMethods)
}

function baseValue(indicator) {
  const source = props.availableIndicators.find((item) => item.id === indicator.indicator_id)
  if (!source?.table) return '—'
  return tableAverage(source.table)
}

function functionValue(func) {
  return calculatedAverage(props.lastResult?.base_indicators, func.name)
}

function normalizedValue(entry) {
  return calculatedAverage(props.lastResult?.normalized_indicators, entry.output_name || entry.indicator_name)
}

function weightedValue(entry) {
  return calculatedAverage(props.lastResult?.weighted_components, entry.output_name || entry.indicator_name)
}

function calculatedAverage(items = [], name) {
  const item = items.find((entry) => entry.name === name)
  if (!item) return '—'
  return tableAverage(item)
}

function tableAverage(table) {
  const yearIndex = targetYear.value && table.years?.includes(targetYear.value)
    ? table.years.indexOf(targetYear.value)
    : 0
  const values = (table.values || [])
    .map((row) => row?.[yearIndex])
    .filter((value) => value !== null && value !== undefined && !Number.isNaN(Number(value)))
    .map(Number)
  if (!values.length) return '—'
  return props.formatNumber(values.reduce((sum, value) => sum + value, 0) / values.length)
}
</script>
