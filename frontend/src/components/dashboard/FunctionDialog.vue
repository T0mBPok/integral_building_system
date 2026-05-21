<template>
  <div v-if="open" class="modal-backdrop" @click.self="$emit('close')">
    <section class="function-modal">
      <div class="modal-header">
        <div>
          <h2>Функция</h2>
          <p>Создайте расчетный показатель на основе базовых показателей проекта</p>
        </div>
        <button class="icon-button" title="Закрыть" @click="$emit('close')">×</button>
      </div>

      <div class="function-form">
        <label>
          <span>Короткое название</span>
          <input :value="draft.name" placeholder="Например, ОКР" @input="updateField('name', $event.target.value)" />
        </label>
        <label>
          <span>Описание</span>
          <textarea :value="draft.description" placeholder="Что считает функция" @input="updateField('description', $event.target.value)" />
        </label>

        <div class="function-indicators">
          <div class="year-picker-header">
            <strong>Показатели</strong>
          </div>
          <button
            v-for="indicator in projectIndicators"
            :key="indicator.name"
            type="button"
            class="function-chip"
            @click="insertIndicator(indicator.name)"
          >
            {{ indicator.name }}
          </button>
        </div>

        <label>
          <span>Формула</span>
          <input :value="draft.formula" placeholder='"Показатель 1" / "Показатель 2" * 1000' @input="updateField('formula', $event.target.value)" />
        </label>
      </div>

      <div class="modal-actions">
        <button class="toolbar-button subtle" @click="$emit('close')">Отмена</button>
        <button class="toolbar-button primary" :disabled="!draft.name || !draft.formula || isBusy" @click="$emit('save')">
          Сохранить функцию
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
const props = defineProps({
  open: { type: Boolean, default: false },
  draft: { type: Object, required: true },
  projectIndicators: { type: Array, default: () => [] },
  isBusy: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'save', 'update:draft'])

function updateField(field, value) {
  emit('update:draft', { ...props.draft, [field]: value })
}

function insertIndicator(name) {
  const token = `"${name}"`
  const formula = props.draft.formula ? `${props.draft.formula}${token}` : token
  updateField('formula', formula)
}
</script>
