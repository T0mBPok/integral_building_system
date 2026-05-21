<template>
  <AppShell>
    <section class="page-header">
      <div>
        <h1>Проекты</h1>
        <p>Создавайте модели интегральных показателей и переходите к доске расчета.</p>
      </div>
      <button class="page-primary-button" @click="createDialogOpen = true">+ Новый проект</button>
    </section>

    <section class="projects-grid">
      <article v-for="project in projects" :key="project.id" class="project-card" @click="openProject(project.id)">
        <div class="card-topline">
          <strong>{{ project.name }}</strong>
          <span>{{ project.last_result ? 'Рассчитан' : 'Черновик' }}</span>
        </div>
        <p>{{ project.description || 'Описание не задано' }}</p>
        <div class="card-meta">
          <span>{{ project.indicators?.length || 0 }} показателей</span>
        </div>
      </article>

      <button class="project-card project-card-empty" @click="createDialogOpen = true">
        <strong>Создать проект</strong>
        <span>Пустой проект, куда потом добавляются показатели из файлов</span>
      </button>
    </section>

    <div v-if="statusMessage" class="page-status" :class="statusTone">{{ statusMessage }}</div>

    <div v-if="createDialogOpen" class="modal-backdrop" @click.self="createDialogOpen = false">
      <section class="create-project-modal">
        <div class="modal-header">
          <div>
            <h2>Новый проект</h2>
            <p>Проект создается пустым. Показатели добавляются уже на доске.</p>
          </div>
          <button class="icon-button" @click="createDialogOpen = false">×</button>
        </div>
        <div class="create-form">
          <label>Название</label>
          <input v-model="newProject.name" placeholder="Например, Демография регионов" @keyup.enter="createProject" />
          <label>Описание</label>
          <textarea v-model="newProject.description" placeholder="Коротко о модели" />
        </div>
        <div class="modal-actions">
          <button class="toolbar-button subtle" @click="createDialogOpen = false">Отмена</button>
          <button class="toolbar-button primary" :disabled="!newProject.name.trim() || isBusy" @click="createProject">
            Создать и открыть
          </button>
        </div>
      </section>
    </div>
  </AppShell>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import api from '../services/api'

const router = useRouter()
const projects = ref([])
const isBusy = ref(false)
const createDialogOpen = ref(false)
const statusMessage = ref('')
const statusTone = ref('neutral')
const newProject = ref({ name: '', description: '' })

onMounted(loadProjects)

async function loadProjects() {
  isBusy.value = true
  try {
    const { data } = await api.get('/project/')
    projects.value = data
  } catch (error) {
    showStatus(errorMessage(error), 'danger')
  } finally {
    isBusy.value = false
  }
}

async function createProject() {
  if (!newProject.value.name.trim()) return
  isBusy.value = true
  try {
    const { data } = await api.post('/project/', {
      name: newProject.value.name.trim(),
      description: newProject.value.description || ''
    })
    router.push(`/project/${data.id}`)
  } catch (error) {
    showStatus(errorMessage(error), 'danger')
  } finally {
    isBusy.value = false
  }
}

function openProject(id) {
  router.push(`/project/${id}`)
}

function showStatus(message, tone = 'neutral') {
  statusMessage.value = message
  statusTone.value = tone
}

function errorMessage(error) {
  return error?.response?.data?.detail || error?.message || 'Ошибка запроса'
}
</script>
