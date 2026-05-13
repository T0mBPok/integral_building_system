<template>
  <AppShell>
    <section class="page-header">
      <div>
        <h1>Файлы и показатели</h1>
        <p>Загружайте Excel/CSV таблицы. Годы из файла выбираются позже при добавлении показателей в проект.</p>
      </div>
      <button class="page-primary-button" @click="uploadDialogOpen = true">+ Загрузить файл</button>
    </section>

    <section class="files-layout">
      <div class="files-list">
        <article
          v-for="indicator in indicators"
          :key="indicator.id"
          class="file-card"
          :class="{ active: selectedIndicator?.id === indicator.id }"
          @click="selectedIndicator = indicator"
        >
          <div>
            <strong>{{ indicator.name }}</strong>
            <span>{{ indicator.original_file_name || 'Загруженный файл' }}</span>
          </div>
          <small>{{ indicator.years?.length || 0 }} годов</small>
        </article>
        <div v-if="indicators.length === 0" class="empty-list">
          Загруженных файлов пока нет
        </div>
      </div>

      <aside class="file-preview">
        <div v-if="selectedIndicator">
          <div class="preview-header">
            <div>
              <h2>{{ selectedIndicator.name }}</h2>
              <p>{{ selectedIndicator.description || selectedIndicator.original_file_name || 'Без описания' }}</p>
            </div>
            <button class="toolbar-button subtle" @click="deleteIndicatorFile(selectedIndicator.id)" :disabled="isBusy">Удалить</button>
          </div>
          <div class="file-sheets">
            <article v-for="sheet in selectedIndicator.sheets" :key="sheet.name || 'sheet'" class="file-sheet-card">
              <strong>{{ sheet.name || 'CSV' }}</strong>
              <span>{{ sheet.region_count }} регионов</span>
              <div class="sheet-years">
                <small v-for="year in sheet.years" :key="year">{{ year }}</small>
              </div>
            </article>
          </div>
        </div>
        <div v-else class="preview-placeholder">
          Выберите файл, чтобы посмотреть найденные листы и годы
        </div>
      </aside>
    </section>

    <div v-if="statusMessage" class="page-status" :class="statusTone">{{ statusMessage }}</div>

    <div v-if="uploadDialogOpen" class="modal-backdrop" @click.self="uploadDialogOpen = false">
      <section class="create-project-modal">
        <div class="modal-header">
          <div>
            <h2>Загрузка файла</h2>
            <p>Поддерживаются .xls, .xlsx и .csv. Формат: первая строка годы, первый столбец регионы.</p>
          </div>
          <button class="icon-button" @click="uploadDialogOpen = false">×</button>
        </div>
        <div class="create-form">
          <label>Файл</label>
          <input type="file" accept=".csv,.xls,.xlsx" @change="handleFileChange" />
          <label>Название файла</label>
          <input v-model="uploadForm.name" placeholder="Например, Численность населения" />
          <label>Описание</label>
          <textarea v-model="uploadForm.description" placeholder="Необязательно" />
          <div v-if="filePreview.years.length" class="year-picker">
            <div class="year-picker-header">
              <strong>Найдены годы</strong>
            </div>
            <label v-for="year in filePreview.years" :key="year">
              {{ year }}
            </label>
          </div>
        </div>
        <div class="modal-actions">
          <button class="toolbar-button subtle" @click="uploadDialogOpen = false">Отмена</button>
          <button class="toolbar-button primary" :disabled="!uploadForm.file || !uploadForm.name || isBusy" @click="uploadIndicator">
            Загрузить
          </button>
        </div>
      </section>
    </div>
  </AppShell>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import api from '../services/api'

const indicators = ref([])
const selectedIndicator = ref(null)
const uploadDialogOpen = ref(false)
const isBusy = ref(false)
const statusMessage = ref('')
const statusTone = ref('neutral')
const uploadForm = ref({
  file: null,
  name: '',
  description: '',
  years: []
})

onMounted(loadIndicators)

async function loadIndicators() {
  isBusy.value = true
  try {
    const { data } = await api.get('/indicator/files/')
    indicators.value = data
    if (!selectedIndicator.value && data.length) selectedIndicator.value = data[0]
  } catch (error) {
    showStatus(errorMessage(error), 'danger')
  } finally {
    isBusy.value = false
  }
}

function handleFileChange(event) {
  const file = event.target.files?.[0]
  uploadForm.value.file = file || null
  uploadForm.value.years = []
  filePreview.value = { sheets: [], years: [] }
  if (file && !uploadForm.value.name) {
    uploadForm.value.name = file.name.replace(/\.[^.]+$/, '')
  }
  if (file) previewFile(file)
}

const filePreview = ref({ sheets: [], years: [] })

async function previewFile(file) {
  try {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post('/indicator/preview', formData)
    filePreview.value = data
    uploadForm.value.years = [...data.years]
  } catch (error) {
    showStatus(errorMessage(error), 'danger')
  }
}

async function uploadIndicator() {
  if (!uploadForm.value.file || !uploadForm.value.name) return
  isBusy.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadForm.value.file)
    formData.append('name', uploadForm.value.name)
    if (uploadForm.value.description) formData.append('description', uploadForm.value.description)
    const { data } = await api.post('/indicator/files/', formData)
    indicators.value.unshift(data)
    selectedIndicator.value = data
    uploadDialogOpen.value = false
    uploadForm.value = { file: null, name: '', description: '', years: [] }
    filePreview.value = { sheets: [], years: [] }
    showStatus('Файл загружен. Годы можно выбрать при добавлении в проект.', 'success')
  } catch (error) {
    showStatus(errorMessage(error), 'danger')
  } finally {
    isBusy.value = false
  }
}

async function deleteIndicatorFile(id) {
  isBusy.value = true
  try {
    await api.delete(`/indicator/files/${id}`)
    indicators.value = indicators.value.filter((indicator) => indicator.id !== id)
    selectedIndicator.value = indicators.value[0] || null
    showStatus('Файл удален', 'success')
  } catch (error) {
    showStatus(errorMessage(error), 'danger')
  } finally {
    isBusy.value = false
  }
}

function showStatus(message, tone = 'neutral') {
  statusMessage.value = message
  statusTone.value = tone
}

function errorMessage(error) {
  return error?.response?.data?.detail || error?.message || 'Ошибка запроса'
}
</script>
