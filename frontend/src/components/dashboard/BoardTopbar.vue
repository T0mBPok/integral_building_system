<template>
  <header class="board-topbar">
    <div class="topbar-left">
      <button class="icon-button" title="К списку проектов" @click="$emit('back')">←</button>
      <div class="project-title-block">
        <input
          :value="projectDraft.name"
          class="project-title-input"
          :disabled="isBusy"
          placeholder="Новый проект"
          @input="updateDraft('name', $event.target.value)"
          @change="$emit('save')"
        />
        <input
          :value="projectDraft.description"
          class="project-description-input"
          :disabled="isBusy"
          placeholder="Описание проекта"
          @input="updateDraft('description', $event.target.value)"
          @change="$emit('save')"
        />
      </div>
    </div>

    <button class="toolbar-button subtle" @click="$emit('reload')" :disabled="!projectId || isBusy">
      Обновить
    </button>
  </header>
</template>

<script setup>
const props = defineProps({
  projectDraft: { type: Object, required: true },
  projectId: { type: String, default: null },
  isBusy: { type: Boolean, default: false }
})

const emit = defineEmits(['back', 'reload', 'save', 'update:projectDraft'])

function updateDraft(field, value) {
  emit('update:projectDraft', {
    ...props.projectDraft,
    [field]: value
  })
}
</script>
