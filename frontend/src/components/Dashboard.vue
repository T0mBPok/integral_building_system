<template>
  <div class="project-board">
    <header class="board-topbar">
      <div class="topbar-left">
        <button class="icon-button" title="К списку проектов" @click="goToProjects">←</button>
        <div class="project-title-block">
          <input
            v-model="projectDraft.name"
            class="project-title-input"
            :disabled="isBusy"
            placeholder="Новый проект"
            @change="saveProjectMeta"
          />
          <input
            v-model="projectDraft.description"
            class="project-description-input"
            :disabled="isBusy"
            placeholder="Описание проекта"
            @change="saveProjectMeta"
          />
        </div>
      </div>

      <div class="topbar-actions">
        <button class="toolbar-button" @click="openIndicatorDialog" :disabled="!project?.id || isBusy">
          + Показатели
        </button>
        <button class="toolbar-button subtle" @click="loadProject" :disabled="!project?.id || isBusy">
          Обновить
        </button>
        <button class="toolbar-button primary" @click="calculateProject" :disabled="!canCalculate || isBusy">
          Рассчитать
        </button>
      </div>
    </header>

    <div class="board-shell">
      <aside class="left-rail">
        <button
          v-for="section in sections"
          :key="section.id"
          class="rail-button"
          :class="{ active: selectedSection === section.id }"
          :title="section.title"
          @click="selectSection(section.id)"
        >
          <span class="rail-icon">{{ section.icon }}</span>
          <span>{{ section.short }}</span>
        </button>
      </aside>

      <main class="board-canvas-wrap" ref="canvasWrapper">
        <div class="board-canvas" ref="canvas" :style="canvasStyle">
          <section class="flow-column base-column">
            <div class="column-heading">
              <span>Базовые показатели</span>
              <button class="mini-button" @click="openIndicatorDialog" :disabled="!project?.id">+</button>
            </div>
            <article
              v-for="indicator in projectIndicators"
              :key="indicator.indicator_id"
              class="flow-node base-node"
              :class="{ selected: selectedNodeId === indicator.indicator_id }"
              @click="selectNode('base', indicator.indicator_id)"
            >
              <div class="node-kicker">Файл</div>
              <h3>{{ indicator.name }}</h3>
              <p>{{ indicator.description || 'Без описания' }}</p>
            </article>
            <div v-if="projectIndicators.length === 0" class="empty-node" @click="openIndicatorDialog">
              Добавьте показатели из загруженных файлов
            </div>
          </section>

          <section class="flow-column">
            <div class="column-heading">
              <span>Нормализация</span>
            </div>
            <article
              v-for="entry in normalizationSettings"
              :key="entry.indicator_name"
              class="flow-node norm-node"
              :class="{ selected: selectedNodeId === `norm:${entry.indicator_name}` }"
              @click="selectNode('normalization', `norm:${entry.indicator_name}`)"
            >
              <div class="node-kicker">{{ methodLabel(entry.method, normalizationMethods) }}</div>
              <h3>{{ entry.output_name || entry.indicator_name }}</h3>
              <p>{{ entry.indicator_name }}</p>
            </article>
          </section>

          <section class="flow-column">
            <div class="column-heading">
              <span>Весовые коэффициенты</span>
            </div>
            <article class="flow-node weight-node" :class="{ selected: selectedSection === 'weights' }" @click="selectSection('weights')">
              <div class="node-kicker">{{ methodLabel(weightMethod, weightMethods) }}</div>
              <h3>Веса показателей</h3>
              <div class="weight-stack">
                <span v-for="weight in effectiveWeights" :key="weight.indicator_name">
                  {{ weight.indicator_name }} · {{ formatNumber(weight.weight) }}
                </span>
              </div>
            </article>
          </section>

          <section class="flow-column">
            <div class="column-heading">
              <span>Свертка</span>
            </div>
            <article class="flow-node aggregate-node" :class="{ selected: selectedSection === 'aggregate' }" @click="selectSection('aggregate')">
              <div class="node-kicker">sum</div>
              <h3>Интегральный показатель</h3>
              <p>{{ resultSummary }}</p>
            </article>
            <article v-if="lastResult?.ranking?.length" class="result-card">
              <div class="result-card-title">Рейтинг</div>
              <ol>
                <li v-for="item in lastResult.ranking.slice(0, 5)" :key="item.region">
                  <span>{{ item.region }}</span>
                  <strong>{{ formatNumber(item.value) }}</strong>
                </li>
              </ol>
            </article>
          </section>
        </div>
      </main>

      <aside class="right-panel">
        <div class="panel-header">
          <span>{{ activePanelTitle }}</span>
          <small>{{ zoomLabel }}</small>
        </div>

        <div v-if="statusMessage" class="status-message" :class="statusTone">{{ statusMessage }}</div>

        <section v-if="selectedSection === 'base'" class="panel-section">
          <div class="section-title">Показатели проекта</div>
          <button class="wide-button" @click="openIndicatorDialog" :disabled="!project?.id">Добавить из файлов</button>
          <div class="compact-list">
            <div v-for="indicator in projectIndicators" :key="indicator.indicator_id" class="compact-row">
              <div>
                <strong>{{ indicator.name }}</strong>
                <span>{{ indicator.description || 'Базовый показатель' }}</span>
              </div>
            </div>
          </div>
        </section>

        <section v-else-if="selectedSection === 'normalization'" class="panel-section">
          <div class="section-title">Методы нормализации</div>
          <div v-for="entry in normalizationSettings" :key="entry.indicator_name" class="settings-card">
            <label>{{ entry.indicator_name }}</label>
            <select v-model="entry.method">
              <option v-for="method in normalizationMethods" :key="method.value" :value="method.value">
                {{ method.label }}
              </option>
            </select>
            <input v-model="entry.output_name" placeholder="Название после нормализации" />
          </div>
        </section>

        <section v-else-if="selectedSection === 'weights'" class="panel-section">
          <div class="section-title">Расчет весов</div>
          <div class="segmented">
            <button
              v-for="method in weightMethods"
              :key="method.value"
              :class="{ active: weightMethod === method.value }"
              @click="weightMethod = method.value"
            >
              {{ method.label }}
            </button>
          </div>
          <div v-if="weightMethod === 'manual'" class="settings-card">
            <div v-for="weight in manualWeights" :key="weight.indicator_name" class="weight-input-row">
              <label>{{ weight.indicator_name }}</label>
              <input v-model.number="weight.weight" type="number" min="0" step="0.01" />
            </div>
          </div>
          <div class="compact-list">
            <div v-for="weight in effectiveWeights" :key="weight.indicator_name" class="compact-row">
              <span>{{ weight.indicator_name }}</span>
              <strong>{{ formatNumber(weight.weight) }}</strong>
            </div>
          </div>
        </section>

        <section v-else class="panel-section">
          <div class="section-title">Свертка</div>
          <div class="settings-card">
            <label>Метод агрегации</label>
            <select v-model="aggregationMethod" disabled>
              <option value="sum">Аддитивная сумма</option>
            </select>
            <label>Год расчета</label>
            <input v-model="calculationYear" placeholder="Например, 2024" />
          </div>
          <button class="wide-button primary" @click="calculateProject" :disabled="!canCalculate || isBusy">
            Рассчитать интегральный показатель
          </button>
          <div v-if="lastResult?.integral_values?.length" class="compact-list">
            <div v-for="item in lastResult.integral_values" :key="item.region" class="compact-row">
              <span>{{ item.region }}</span>
              <strong>{{ formatNumber(item.value) }}</strong>
            </div>
          </div>
        </section>

        <div class="panel-footer">
          <button class="icon-button" title="Уменьшить" @click="setZoom(-0.1)">−</button>
          <button class="icon-button" title="По размеру" @click="fitToView">□</button>
          <button class="icon-button" title="Увеличить" @click="setZoom(0.1)">+</button>
        </div>
      </aside>
    </div>

    <div v-if="indicatorDialogOpen" class="modal-backdrop" @click.self="indicatorDialogOpen = false">
      <section class="indicator-modal">
        <div class="modal-header">
          <div>
            <h2>Показатели из файлов</h2>
            <p>Выберите загруженные таблицы или добавьте новый файл</p>
          </div>
          <button class="icon-button" title="Закрыть" @click="indicatorDialogOpen = false">×</button>
        </div>

        <div class="upload-strip">
          <input ref="fileInput" type="file" accept=".csv,.xls,.xlsx" @change="handleFileUpload" />
          <input v-model="uploadName" placeholder="Название показателя" />
          <button class="toolbar-button" @click="uploadSelectedFile" :disabled="!selectedFile || !uploadName || isBusy">
            Загрузить
          </button>
        </div>

        <div class="indicator-picker">
          <label
            v-for="indicator in availableIndicators"
            :key="indicator.id"
            class="indicator-option"
            :class="{ checked: selectedIndicatorIds.includes(indicator.id), attached: attachedIndicatorIds.has(indicator.id) }"
          >
            <input
              type="checkbox"
              :value="indicator.id"
              v-model="selectedIndicatorIds"
              :disabled="attachedIndicatorIds.has(indicator.id)"
            />
            <div>
              <strong>{{ indicator.name }}</strong>
              <span>{{ indicator.source_file_name || indicator.description || 'Ручной показатель' }}</span>
            </div>
          </label>
        </div>

        <div class="modal-actions">
          <button class="toolbar-button subtle" @click="indicatorDialogOpen = false">Отмена</button>
          <button class="toolbar-button primary" @click="attachSelectedIndicators" :disabled="selectedIndicatorIds.length === 0 || isBusy">
            Добавить выбранные
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'

const route = useRoute()
const router = useRouter()

const canvas = ref(null)
const canvasWrapper = ref(null)
const canvasScale = ref(1)
const canvasTransform = ref({ x: 24, y: 24 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const transformStart = ref({ x: 0, y: 0 })

const project = ref(null)
const projectDraft = ref({ name: 'Новый проект', description: '' })
const availableIndicators = ref([])
const selectedIndicatorIds = ref([])
const selectedSection = ref('base')
const selectedNodeId = ref(null)
const indicatorDialogOpen = ref(false)
const isBusy = ref(false)
const statusMessage = ref('')
const statusTone = ref('neutral')
const selectedFile = ref(null)
const uploadName = ref('')
const calculationYear = ref('')
const aggregationMethod = ref('sum')
const weightMethod = ref('equal')
const normalizationSettings = ref([])
const manualWeights = ref([])

const sections = [
  { id: 'base', title: 'Базовые показатели', short: 'База', icon: 'B' },
  { id: 'normalization', title: 'Нормализация', short: 'Норма', icon: 'N' },
  { id: 'weights', title: 'Весовые коэффициенты', short: 'Веса', icon: 'W' },
  { id: 'aggregate', title: 'Свертка', short: 'Итог', icon: 'Σ' }
]

const normalizationMethods = [
  { value: 'minmax', label: 'Min-Max' },
  { value: 'z-score', label: 'Z-score' },
  { value: 'robust', label: 'Robust' }
]

const weightMethods = [
  { value: 'equal', label: 'Равные' },
  { value: 'manual', label: 'Вручную' },
  { value: 'std', label: 'СКО' },
  { value: 'pca', label: 'PCA' },
  { value: 'modified_pca', label: 'Mod PCA' },
  { value: 'entropy', label: 'Энтропия' }
]

const projectId = computed(() => route.params.id || route.query.projectId || project.value?.id)
const projectIndicators = computed(() => project.value?.indicators || [])
const lastResult = computed(() => project.value?.last_result)
const attachedIndicatorIds = computed(() => new Set(projectIndicators.value.map((indicator) => indicator.indicator_id)))
const canCalculate = computed(() => Boolean(project.value?.id && projectIndicators.value.length > 0))
const zoomLabel = computed(() => `${Math.round(canvasScale.value * 100)}%`)
const activePanelTitle = computed(() => sections.find((section) => section.id === selectedSection.value)?.title || 'Проект')
const resultSummary = computed(() => {
  if (!lastResult.value?.integral_values?.length) return 'Расчет еще не выполнен'
  return `${lastResult.value.integral_values.length} объектов, ${lastResult.value.year}`
})

const effectiveWeights = computed(() => {
  if (lastResult.value?.weights?.length) return lastResult.value.weights
  if (weightMethod.value === 'manual') return manualWeights.value
  const count = normalizationSettings.value.length || projectIndicators.value.length
  if (!count) return []
  const weight = 1 / count
  return normalizationSettings.value.map((entry) => ({
    indicator_name: entry.output_name || entry.indicator_name,
    weight
  }))
})

const canvasStyle = computed(() => ({
  transform: `translate(${canvasTransform.value.x}px, ${canvasTransform.value.y}px) scale(${canvasScale.value})`
}))

watch(projectIndicators, () => {
  syncCalculationSettings()
  nextTick(fitToView)
}, { deep: true })

watch(weightMethod, (method) => {
  if (method === 'manual') syncManualWeights()
})

onMounted(async () => {
  bindCanvasPan()
  await initializeBoard()
})

onUnmounted(() => {
  unbindCanvasPan()
})

async function initializeBoard() {
  await loadIndicators()
  if (projectId.value) {
    await loadProject()
  } else {
    project.value = null
    projectDraft.value = { name: 'Новый проект', description: '' }
    showStatus('Создайте проект, чтобы добавить показатели', 'neutral')
  }
}

async function createProjectIfNeeded() {
  if (project.value?.id) return project.value
  isBusy.value = true
  try {
    const { data } = await api.post('/project/', {
      name: projectDraft.value.name || 'Новый проект',
      description: projectDraft.value.description || ''
    })
    project.value = data
    projectDraft.value = { name: data.name, description: data.description || '' }
    router.replace({ path: route.path, query: { ...route.query, projectId: data.id } })
    showStatus('Проект создан', 'success')
    return data
  } catch (error) {
    showStatus(errorMessage(error), 'danger')
    throw error
  } finally {
    isBusy.value = false
  }
}

async function loadProject() {
  if (!projectId.value) return
  isBusy.value = true
  try {
    const { data } = await api.get(`/project/${projectId.value}`)
    project.value = data
    projectDraft.value = { name: data.name, description: data.description || '' }
    calculationYear.value = data.calculation_year || data.last_result?.year || ''
    weightMethod.value = data.weight_method || data.last_result?.weight_method || 'equal'
    aggregationMethod.value = data.aggregation_method || 'sum'
    syncCalculationSettings()
    showStatus('Проект загружен', 'success')
  } catch (error) {
    showStatus(errorMessage(error), 'danger')
  } finally {
    isBusy.value = false
  }
}

async function loadIndicators() {
  try {
    const { data } = await api.get('/indicator/')
    availableIndicators.value = data
  } catch (error) {
    showStatus(errorMessage(error), 'danger')
  }
}

async function saveProjectMeta() {
  if (!project.value?.id) {
    await createProjectIfNeeded()
    return
  }
  isBusy.value = true
  try {
    const { data } = await api.put(`/project/${project.value.id}`, {
      name: projectDraft.value.name,
      description: projectDraft.value.description
    })
    project.value = data
    showStatus('Проект сохранен', 'success')
  } catch (error) {
    showStatus(errorMessage(error), 'danger')
  } finally {
    isBusy.value = false
  }
}

async function openIndicatorDialog() {
  await createProjectIfNeeded()
  await loadIndicators()
  selectedIndicatorIds.value = []
  indicatorDialogOpen.value = true
}

function handleFileUpload(event) {
  const file = event.target.files?.[0]
  selectedFile.value = file || null
  if (file && !uploadName.value) {
    uploadName.value = file.name.replace(/\.[^.]+$/, '')
  }
}

async function uploadSelectedFile() {
  if (!selectedFile.value || !uploadName.value) return
  isBusy.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('name', uploadName.value)
    const { data } = await api.post('/indicator/upload', formData)
    availableIndicators.value.unshift(data)
    selectedIndicatorIds.value = [data.id]
    selectedFile.value = null
    uploadName.value = ''
    showStatus('Файл загружен', 'success')
  } catch (error) {
    showStatus(errorMessage(error), 'danger')
  } finally {
    isBusy.value = false
  }
}

async function attachSelectedIndicators() {
  await createProjectIfNeeded()
  isBusy.value = true
  try {
    let updatedProject = project.value
    const idsToAttach = selectedIndicatorIds.value.filter((id) => !attachedIndicatorIds.value.has(id))
    for (const indicatorId of idsToAttach) {
      const { data } = await api.post(`/project/${project.value.id}/indicators`, { indicator_id: indicatorId })
      updatedProject = data
    }
    project.value = updatedProject
    indicatorDialogOpen.value = false
    showStatus('Показатели добавлены', 'success')
  } catch (error) {
    showStatus(errorMessage(error), 'danger')
  } finally {
    isBusy.value = false
  }
}

async function calculateProject() {
  if (!canCalculate.value) return
  isBusy.value = true
  try {
    const payload = {
      year: calculationYear.value || null,
      normalization_settings: normalizationSettings.value,
      weight_method: weightMethod.value
    }
    if (weightMethod.value === 'manual') {
      payload.weight_settings = manualWeights.value
    }
    const { data } = await api.post(`/project/${project.value.id}/calculate`, payload)
    project.value = data
    calculationYear.value = data.last_result?.year || calculationYear.value
    showStatus('Интегральный показатель рассчитан', 'success')
  } catch (error) {
    showStatus(errorMessage(error), 'danger')
  } finally {
    isBusy.value = false
  }
}

function syncCalculationSettings() {
  const existingNorm = new Map(normalizationSettings.value.map((entry) => [entry.indicator_name, entry]))
  normalizationSettings.value = projectIndicators.value.map((indicator) => {
    const previous = existingNorm.get(indicator.name)
    return {
      indicator_name: indicator.name,
      method: previous?.method || 'minmax',
      output_name: previous?.output_name || indicator.name
    }
  })
  syncManualWeights()
}

function syncManualWeights() {
  const previous = new Map(manualWeights.value.map((entry) => [entry.indicator_name, entry.weight]))
  const count = normalizationSettings.value.length || 1
  manualWeights.value = normalizationSettings.value.map((entry) => ({
    indicator_name: entry.output_name || entry.indicator_name,
    weight: previous.get(entry.output_name || entry.indicator_name) ?? Number((1 / count).toFixed(4))
  }))
}

function selectSection(sectionId) {
  selectedSection.value = sectionId
  selectedNodeId.value = null
}

function selectNode(sectionId, nodeId) {
  selectedSection.value = sectionId
  selectedNodeId.value = nodeId
}

function goToProjects() {
  router.push('/projects')
}

function showStatus(message, tone = 'neutral') {
  statusMessage.value = message
  statusTone.value = tone
}

function errorMessage(error) {
  return error?.response?.data?.detail || error?.message || 'Ошибка запроса'
}

function methodLabel(value, methods) {
  return methods.find((method) => method.value === value)?.label || value
}

function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—'
  return Number(value).toLocaleString('ru-RU', { maximumFractionDigits: 4 })
}

function setZoom(delta) {
  canvasScale.value = Math.max(0.5, Math.min(1.8, canvasScale.value + delta))
}

async function fitToView() {
  await nextTick()
  const wrapper = canvasWrapper.value
  const content = canvas.value
  if (!wrapper || !content) return
  const scale = Math.min(1, (wrapper.clientWidth - 48) / Math.max(content.scrollWidth, 1))
  canvasScale.value = Math.max(0.65, scale)
  canvasTransform.value = { x: 24, y: 24 }
}

function bindCanvasPan() {
  const wrapper = canvasWrapper.value
  if (!wrapper) return
  wrapper.addEventListener('wheel', handleWheel, { passive: false })
  wrapper.addEventListener('mousedown', startDragging)
  document.addEventListener('mousemove', handleDragging)
  document.addEventListener('mouseup', stopDragging)
}

function unbindCanvasPan() {
  const wrapper = canvasWrapper.value
  if (!wrapper) return
  wrapper.removeEventListener('wheel', handleWheel)
  wrapper.removeEventListener('mousedown', startDragging)
  document.removeEventListener('mousemove', handleDragging)
  document.removeEventListener('mouseup', stopDragging)
}

function handleWheel(event) {
  event.preventDefault()
  setZoom(event.deltaY > 0 ? -0.08 : 0.08)
}

function startDragging(event) {
  if (event.button !== 0 || event.target.closest('button, input, select, textarea, .flow-node, .empty-node')) return
  isDragging.value = true
  dragStart.value = { x: event.clientX, y: event.clientY }
  transformStart.value = { ...canvasTransform.value }
}

function handleDragging(event) {
  if (!isDragging.value) return
  canvasTransform.value = {
    x: transformStart.value.x + event.clientX - dragStart.value.x,
    y: transformStart.value.y + event.clientY - dragStart.value.y
  }
}

function stopDragging() {
  isDragging.value = false
}
</script>
