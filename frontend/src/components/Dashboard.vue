<template>
  <div class="project-board">
    <BoardTopbar
      v-model:project-draft="projectDraft"
      :project-id="project?.id"
      :is-busy="isBusy"
      @back="goToProjects"
      @reload="loadProject"
      @save="saveProjectMeta"
    />

    <div class="board-shell">
      <main class="board-canvas-wrap" ref="canvasWrapper">
        <ProjectTree
          ref="canvas"
          :canvas-style="canvasStyle"
          :selected-node-id="selectedNodeId"
          :integral-title="integralTitle"
          :result-summary="resultSummary"
          :last-result="lastResult"
          :weight-method="weightMethod"
          :weight-methods="weightMethods"
          :effective-weights="effectiveWeights"
          :normalization-settings="normalizationSettings"
          :normalization-methods="normalizationMethods"
          :project-indicators="projectIndicators"
          :method-label="methodLabel"
          :format-number="formatNumber"
          @select-node="selectNode"
          @open-indicators="openIndicatorDialog"
        />

        <BottomToolPanel
          v-model:bulk-normalization-method="bulkNormalizationMethod"
          v-model:weight-method="weightMethod"
          v-model:calculation-year="calculationYear"
          :normalization-methods="normalizationMethods"
          :weight-methods="weightMethods"
          :aggregation-method="aggregationMethod"
          :project-id="project?.id"
          :is-busy="isBusy"
          :can-calculate="canCalculate"
          :zoom-label="zoomLabel"
          @apply-normalization="applyBulkNormalization"
          @open-indicators="openIndicatorDialog"
          @calculate="calculateProject"
          @zoom="setZoom"
          @fit="fitToView"
        />

        <FloatingSettingsPanels
          v-model:manual-weights="manualWeights"
          v-model:normalization-settings="normalizationSettings"
          :weight-method="weightMethod"
          :normalization-methods="normalizationMethods"
          :status-message="statusMessage"
          :status-tone="statusTone"
        />
      </main>
    </div>

    <IndicatorDialog
      v-model:selected-indicator-ids="selectedIndicatorIds"
      v-model:upload-name="uploadName"
      v-model:selected-years="selectedFileYears"
      :open="indicatorDialogOpen"
      :available-indicators="availableIndicators"
      :indicator-files="indicatorFiles"
      :selected-file-id="selectedIndicatorFileId"
      :attached-indicator-ids="attachedIndicatorIds"
      :selected-file="selectedFile"
      :file-preview="selectedIndicatorFile"
      :is-busy="isBusy"
      @close="indicatorDialogOpen = false"
      @select-file="selectIndicatorFile"
      @file-change="handleFileUpload"
      @upload="storeSelectedFile"
      @extract="extractSelectedYearsAndAttach"
      @attach="attachSelectedIndicators"
    />
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import BoardTopbar from './dashboard/BoardTopbar.vue'
import BottomToolPanel from './dashboard/BottomToolPanel.vue'
import FloatingSettingsPanels from './dashboard/FloatingSettingsPanels.vue'
import IndicatorDialog from './dashboard/IndicatorDialog.vue'
import ProjectTree from './dashboard/ProjectTree.vue'

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
const indicatorFiles = ref([])
const selectedIndicatorIds = ref([])
const selectedIndicatorFileId = ref('')
const selectedFileYears = ref([])
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
const bulkNormalizationMethod = ref('minmax')
const normalizationSettings = ref([])
const manualWeights = ref([])

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
const selectedIndicatorFile = computed(() => indicatorFiles.value.find((file) => file.id === selectedIndicatorFileId.value) || { sheets: [], years: [] })
const canCalculate = computed(() => Boolean(project.value?.id && projectIndicators.value.length > 0))
const zoomLabel = computed(() => `${Math.round(canvasScale.value * 100)}%`)
const integralTitle = computed(() => project.value?.name ? `ИП: ${project.value.name}` : 'ИП проекта')
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

async function loadIndicatorFiles() {
  try {
    const { data } = await api.get('/indicator/files/')
    indicatorFiles.value = data
    if (data.length && !data.some((file) => file.id === selectedIndicatorFileId.value)) {
      selectIndicatorFile(data[0].id)
    } else if (!data.length) {
      selectedIndicatorFileId.value = ''
      selectedFileYears.value = []
    }
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
  await loadIndicatorFiles()
  selectedIndicatorIds.value = []
  selectedFileYears.value = selectedIndicatorFile.value?.years ? [...selectedIndicatorFile.value.years] : []
  indicatorDialogOpen.value = true
}

function handleFileUpload(event) {
  const file = event.target.files?.[0]
  selectedFile.value = file || null
  if (file && !uploadName.value) {
    uploadName.value = file.name.replace(/\.[^.]+$/, '')
  }
}

function selectIndicatorFile(fileId) {
  selectedIndicatorFileId.value = fileId
  const file = indicatorFiles.value.find((item) => item.id === fileId)
  selectedFileYears.value = file?.years ? [...file.years] : []
}

async function storeSelectedFile() {
  if (!selectedFile.value || !uploadName.value) return
  isBusy.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('name', uploadName.value)
    const { data } = await api.post('/indicator/files/', formData)
    indicatorFiles.value.unshift(data)
    selectIndicatorFile(data.id)
    selectedFile.value = null
    uploadName.value = ''
    showStatus('Файл сохранен, выберите годы для добавления', 'success')
  } catch (error) {
    showStatus(errorMessage(error), 'danger')
  } finally {
    isBusy.value = false
  }
}

async function extractSelectedYearsAndAttach() {
  await createProjectIfNeeded()
  if (!selectedIndicatorFileId.value || selectedFileYears.value.length === 0) return
  isBusy.value = true
  try {
    const file = selectedIndicatorFile.value
    const { data } = await api.post(`/indicator/files/${selectedIndicatorFileId.value}/extract`, {
      name: file.name,
      years: selectedFileYears.value
    })
    availableIndicators.value.unshift(...data.indicators)
    let updatedProject = project.value
    for (const indicator of data.indicators) {
      const response = await api.post(`/project/${project.value.id}/indicators`, { indicator_id: indicator.id })
      updatedProject = response.data
    }
    project.value = updatedProject
    indicatorDialogOpen.value = false
    showStatus(`Добавлено показателей из годов: ${data.created_count}`, 'success')
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

function applyBulkNormalization() {
  normalizationSettings.value = normalizationSettings.value.map((entry) => ({
    ...entry,
    method: bulkNormalizationMethod.value
  }))
}

function syncManualWeights() {
  const previous = new Map(manualWeights.value.map((entry) => [entry.indicator_name, entry.weight]))
  const count = normalizationSettings.value.length || 1
  manualWeights.value = normalizationSettings.value.map((entry) => ({
    indicator_name: entry.output_name || entry.indicator_name,
    weight: previous.get(entry.output_name || entry.indicator_name) ?? Number((1 / count).toFixed(4))
  }))
}

function selectNode(sectionId, nodeId) {
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
  const content = canvas.value?.$el || canvas.value
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
