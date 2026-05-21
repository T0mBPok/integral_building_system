<template>
  <aside class="project-settings-panel">
    <header class="settings-panel-header">
      <div>
        <span>{{ selectedNode.subtitle }}</span>
        <h3>{{ selectedNode.title }}</h3>
      </div>
      <button class="icon-button" title="Закрыть" @click="$emit('close')">×</button>
    </header>

    <section v-if="selectedNode.type === 'aggregate'" class="settings-section">
      <div class="settings-readonly integral-total">
        <span>Интегральный показатель по всем годам и регионам</span>
        <strong>{{ integralValue }}</strong>
      </div>
      <div class="settings-result-list">
        <strong>Состав расчета</strong>
        <details class="settings-details">
          <summary>
            <span>Показатели-годы</span>
            <b>{{ calculationIndicators.length }}</b>
          </summary>
          <div class="settings-detail-list">
            <div v-for="indicator in calculationIndicators" :key="`${indicator.name}:${indicator.year}`" class="settings-detail-row">
              <span>{{ indicator.name }}</span>
              <b>{{ indicator.year || '—' }}</b>
            </div>
          </div>
        </details>
        <details class="settings-details">
          <summary>
            <span>Регионы</span>
            <b>{{ calculationRegions.length }}</b>
          </summary>
          <div class="settings-detail-list">
            <span v-for="region in calculationRegions" :key="region">{{ region }}</span>
          </div>
        </details>
      </div>
    </section>

    <section v-if="selectedNode.type === 'aggregation'" class="settings-section">
      <label>
        <span>Метод свертки</span>
        <select :value="aggregationMethod" disabled>
          <option value="sum">Сумма</option>
        </select>
      </label>
      <div class="settings-result-list">
        <strong>Компоненты</strong>
        <div v-for="weight in effectiveWeights" :key="weight.indicator_name" class="settings-result-row">
          <span>{{ weight.indicator_name }}</span>
          <b>{{ formatNumber(weight.weight) }}</b>
        </div>
      </div>
    </section>

    <section v-if="selectedNode.type === 'weights'" class="settings-section">
      <label>
        <span>Метод весов</span>
        <select :value="weightMethod" @change="$emit('update:weightMethod', $event.target.value)">
          <option v-for="method in weightMethods" :key="method.value" :value="method.value">
            {{ method.label }}
          </option>
        </select>
      </label>
      <div class="settings-result-list">
        <strong>Текущие веса</strong>
        <div v-for="weight in effectiveWeights" :key="weight.indicator_name" class="settings-result-row">
          <span>{{ weight.indicator_name }}</span>
          <b>{{ formatNumber(weight.weight) }}</b>
        </div>
      </div>
      <div v-if="weightMethod === 'manual' && manualWeights.length" class="settings-section nested">
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
    </section>

    <section v-if="selectedNode.type === 'weight'" class="settings-section">
      <label>
        <span>Метод весов</span>
        <select :value="weightMethod" @change="$emit('update:weightMethod', $event.target.value)">
          <option v-for="method in weightMethods" :key="method.value" :value="method.value">
            {{ method.label }}
          </option>
        </select>
      </label>
      <div class="settings-readonly">
        <span>Вес показателя</span>
        <strong>{{ selectedNode.weight ? formatNumber(selectedNode.weight.weight) : '—' }}</strong>
      </div>
      <div v-if="weightMethod === 'manual' && selectedNode.weight" class="weight-input-row">
        <label>{{ selectedNode.weight.indicator_name }}</label>
        <input
          :value="selectedNode.weight.weight"
          type="number"
          min="0"
          step="0.01"
          @input="updateManualWeight(selectedNode.weight.indicator_name, Number($event.target.value))"
        />
      </div>
    </section>

    <section v-if="selectedNode.type === 'normalization'" class="settings-section">
      <label>
        <span>Метод нормализации</span>
        <select :value="selectedNode.entry.method" @change="updateNormalization(selectedNode.entry.indicator_name, 'method', $event.target.value)">
          <option v-for="method in normalizationMethods" :key="method.value" :value="method.value">
            {{ method.label }}
          </option>
        </select>
      </label>
      <label>
        <span>Название после нормализации</span>
        <input
          :value="selectedNode.entry.output_name"
          placeholder="Название"
          @input="updateNormalization(selectedNode.entry.indicator_name, 'output_name', $event.target.value)"
        />
      </label>
      <button class="toolbar-button subtle" type="button" @click="updateBulkNormalization(selectedNode.entry.method)">
        Применить метод ко всем
      </button>
    </section>

    <section v-if="selectedNode.type === 'base'" class="settings-section">
      <div class="settings-readonly">
        <span>Название</span>
        <strong>{{ selectedNode.indicator.name }}</strong>
      </div>
      <div class="settings-readonly">
        <span>Описание</span>
        <strong>{{ selectedNode.indicator.description || 'Базовый показатель' }}</strong>
      </div>
      <div class="settings-readonly">
        <span>Файл</span>
        <strong>{{ selectedNode.sourceIndicator?.source_file_name || 'Не указан' }}</strong>
      </div>
      <div class="settings-readonly">
        <span>ID показателя</span>
        <strong>{{ selectedNode.indicator.indicator_id }}</strong>
      </div>
    </section>

    <section v-if="isFunctionNode" class="settings-section">
      <div class="settings-readonly">
        <span>Значение функции</span>
        <strong>{{ functionValue }}</strong>
      </div>
      <div class="settings-readonly">
        <span>Формула</span>
        <strong>{{ selectedNode.func?.formula || 'Формула не задана' }}</strong>
      </div>
      <div class="settings-result-list">
        <strong>Показатели в формуле</strong>
        <div v-for="name in functionInputs" :key="name" class="settings-result-row">
          <span>{{ name }}</span>
        </div>
        <div v-if="functionInputs.length === 0" class="settings-result-row">
          <span>Показатели не найдены</span>
        </div>
      </div>
      <label>
        <span>Короткое название</span>
        <input v-model="functionDraft.name" placeholder="Название функции" />
      </label>
      <label>
        <span>Описание</span>
        <textarea v-model="functionDraft.description" placeholder="Что считает функция" />
      </label>
      <label>
        <span>Формула</span>
        <input v-model="functionDraft.formula" placeholder='"Показатель 1" / "Показатель 2" * 1000' />
      </label>
      <button class="toolbar-button primary" type="button" @click="saveFunction">
        Сохранить функцию
      </button>
    </section>

    <div v-if="statusMessage" class="floating-status" :class="statusTone">{{ statusMessage }}</div>
  </aside>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  selectedNode: { type: Object, required: true },
  weightMethod: { type: String, required: true },
  weightMethods: { type: Array, required: true },
  manualWeights: { type: Array, required: true },
  normalizationSettings: { type: Array, required: true },
  normalizationMethods: { type: Array, required: true },
  bulkNormalizationMethod: { type: String, required: true },
  calculationYear: { type: String, default: '' },
  aggregationMethod: { type: String, required: true },
  effectiveWeights: { type: Array, required: true },
  projectIndicators: { type: Array, default: () => [] },
  customIndicators: { type: Array, default: () => [] },
  availableIndicators: { type: Array, default: () => [] },
  lastResult: { type: Object, default: null },
  methodLabel: { type: Function, required: true },
  formatNumber: { type: Function, required: true },
  statusMessage: { type: String, default: '' },
  statusTone: { type: String, default: 'neutral' }
})

const emit = defineEmits([
  'close',
  'update:manualWeights',
  'update:normalizationSettings',
  'update:bulkNormalizationMethod',
  'update:weightMethod',
  'update:calculationYear',
  'apply-normalization',
  'save-function'
])

const functionDraft = ref({ originalName: '', name: '', description: '', formula: '' })

watch(() => props.selectedNode, (node) => {
  if (!node?.func) return
  functionDraft.value = {
    originalName: node.func.name,
    name: node.func.name,
    description: node.func.description || '',
    formula: node.func.formula || ''
  }
}, { immediate: true })

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

function updateBulkNormalization(value) {
  emit('update:bulkNormalizationMethod', value)
  emit('apply-normalization', value)
}

function saveFunction() {
  emit('save-function', { ...functionDraft.value })
}

const integralValue = computed(() => {
  if (props.lastResult?.integral_value !== null && props.lastResult?.integral_value !== undefined) {
    return props.formatNumber(props.lastResult.integral_value)
  }
  const values = props.lastResult?.integral_values || []
  if (!values.length) return '—'
  const average = values.reduce((sum, item) => sum + Number(item.value || 0), 0) / values.length
  return props.formatNumber(average)
})

const weights = computed(() => props.lastResult?.weights || props.effectiveWeights || [])

const calculationIndicators = computed(() => {
  const weightedNames = props.lastResult?.weights?.length
    ? props.lastResult.weights.map((weight) => weight.indicator_name)
    : props.effectiveWeights.map((weight) => weight.indicator_name)

  const names = []
  for (const name of weightedNames) {
    const func = props.customIndicators.find((item) => item.name === name)
    if (func) {
      names.push(...formulaInputs(func.formula))
    } else {
      names.push(name)
    }
  }

  const uniqueNames = [...new Set(names)]
  return uniqueNames.map((name) => ({
    name,
    year: yearForIndicatorName(name)
  }))
})

const calculationRegions = computed(() => {
  const regions = props.lastResult?.integral_values?.map((item) => item.region) || []
  return [...new Set(regions)]
})

const functionInputs = computed(() => {
  if (!isFunctionNode.value) return []
  return formulaInputs(props.selectedNode.func?.formula || '')
})

const functionValue = computed(() => {
  if (!isFunctionNode.value) return '—'
  const item = props.lastResult?.base_indicators?.find((entry) => entry.name === props.selectedNode.func?.name)
  if (!item) return '—'
  return tableAverage(item)
})

const isFunctionNode = computed(() => Boolean(props.selectedNode?.func))

function tableAverage(table) {
  const year = props.lastResult?.year || props.calculationYear
  const yearIndex = year && table.years?.includes(year) ? table.years.indexOf(year) : 0
  const values = (table.values || [])
    .map((row) => row?.[yearIndex])
    .filter((value) => value !== null && value !== undefined && !Number.isNaN(Number(value)))
    .map(Number)
  if (!values.length) return '—'
  return props.formatNumber(values.reduce((sum, value) => sum + value, 0) / values.length)
}

function formulaInputs(formula) {
  return [...String(formula || '').matchAll(/"([^"]+)"/g)].map((match) => match[1])
}

function yearForIndicatorName(name) {
  const projectIndicator = props.projectIndicators.find((indicator) => indicator.name === name)
  const source = props.availableIndicators.find((indicator) => indicator.id === projectIndicator?.indicator_id)
  if (source?.table?.years?.length === 1) return source.table.years[0]
  if (source?.table?.years?.length) return source.table.years.join(', ')
  const yearMatch = String(name).match(/(?:^|\D)(\d{4})(?:\.0)?(?:\D|$)/)
  return yearMatch?.[1] || ''
}
</script>
