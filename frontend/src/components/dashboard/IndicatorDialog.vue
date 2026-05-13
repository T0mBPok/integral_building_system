<template>
  <div v-if="open" class="modal-backdrop" @click.self="$emit('close')">
    <section class="indicator-modal">
      <div class="modal-header">
        <div>
          <h2>Показатели из файлов</h2>
          <p>Выберите загруженный файл и годы, которые нужно добавить в проект</p>
        </div>
        <button class="icon-button" title="Закрыть" @click="$emit('close')">×</button>
      </div>

      <div class="upload-strip">
        <input type="file" accept=".csv,.xls,.xlsx" @change="$emit('file-change', $event)" />
        <input :value="uploadName" placeholder="Название файла" @input="$emit('update:uploadName', $event.target.value)" />
        <button class="toolbar-button" @click="$emit('upload')" :disabled="!selectedFile || !uploadName || isBusy">
          Сохранить файл
        </button>
      </div>

      <div class="indicator-file-list">
        <button
          v-for="file in indicatorFiles"
          :key="file.id"
          type="button"
          class="indicator-file-option"
          :class="{ active: file.id === selectedFileId }"
          @click="$emit('select-file', file.id)"
        >
          <strong>{{ file.name }}</strong>
          <span>{{ file.original_file_name || 'Загруженный файл' }} · {{ file.years.length }} годов</span>
        </button>
        <div v-if="indicatorFiles.length === 0" class="empty-list compact">
          Сначала загрузите файл на странице файлов или прямо здесь
        </div>
      </div>

      <div v-if="filePreview.years?.length" class="dialog-year-picker">
        <div class="year-picker-header">
          <strong>Какие годы добавить как показатели</strong>
          <button type="button" @click="$emit('update:selectedYears', [...filePreview.years])">Все</button>
          <button type="button" @click="$emit('update:selectedYears', [])">Снять</button>
        </div>
        <label v-for="year in filePreview.years" :key="year">
          <input
            type="checkbox"
            :value="year"
            :checked="selectedYears.includes(year)"
            @change="toggleYear(year, $event.target.checked)"
          />
          {{ year }}
        </label>
        <button class="toolbar-button primary extract-button" @click="$emit('extract')" :disabled="!selectedFileId || selectedYears.length === 0 || isBusy">
          Добавить выбранные годы в проект
        </button>
      </div>

      <div class="indicator-picker">
        <div class="year-picker-header">
          <strong>Уже созданные показатели</strong>
        </div>
        <label
          v-for="indicator in availableIndicators"
          :key="indicator.id"
          class="indicator-option"
          :class="{ checked: selectedIndicatorIds.includes(indicator.id), attached: attachedIndicatorIds.has(indicator.id) }"
        >
          <input
            type="checkbox"
            :value="indicator.id"
            :checked="selectedIndicatorIds.includes(indicator.id)"
            :disabled="attachedIndicatorIds.has(indicator.id)"
            @change="toggleIndicator(indicator.id, $event.target.checked)"
          />
          <div>
            <strong>{{ indicator.name }}</strong>
            <span>{{ indicator.source_file_name || indicator.description || 'Ручной показатель' }}</span>
          </div>
        </label>
      </div>

      <div class="modal-actions">
        <button class="toolbar-button subtle" @click="$emit('close')">Отмена</button>
        <button class="toolbar-button primary" @click="$emit('attach')" :disabled="selectedIndicatorIds.length === 0 || isBusy">
          Добавить выбранные
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
const props = defineProps({
  open: { type: Boolean, default: false },
  availableIndicators: { type: Array, required: true },
  indicatorFiles: { type: Array, default: () => [] },
  selectedIndicatorIds: { type: Array, required: true },
  selectedFileId: { type: String, default: '' },
  attachedIndicatorIds: { type: Object, required: true },
  uploadName: { type: String, default: '' },
  selectedFile: { type: Object, default: null },
  filePreview: { type: Object, default: () => ({ sheets: [], years: [] }) },
  selectedYears: { type: Array, default: () => [] },
  isBusy: { type: Boolean, default: false }
})

const emit = defineEmits([
  'close',
  'select-file',
  'file-change',
  'upload',
  'extract',
  'attach',
  'update:uploadName',
  'update:selectedIndicatorIds',
  'update:selectedYears'
])

function toggleIndicator(indicatorId, checked) {
  if (checked) {
    emit('update:selectedIndicatorIds', [...props.selectedIndicatorIds, indicatorId])
    return
  }
  emit('update:selectedIndicatorIds', props.selectedIndicatorIds.filter((id) => id !== indicatorId))
}

function toggleYear(year, checked) {
  if (checked) {
    emit('update:selectedYears', [...props.selectedYears, year])
    return
  }
  emit('update:selectedYears', props.selectedYears.filter((item) => item !== year))
}
</script>
