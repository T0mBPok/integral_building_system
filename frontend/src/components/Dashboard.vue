<template>
  <div class="workspace-container">
    <!-- Основная рабочая область -->
    <main class="main-workspace">
      <div class="canvas-wrapper">
        <div 
          class="canvas" 
          ref="canvas"
          :style="canvasStyle"
        >
          <div
            v-for="element in elements"
            :key="element.id"
            :data-id="element.id"
            class="element"
            :style="getElementStyle(element)"
          >
            {{ element.text }}
          </div>
        </div>
      </div>
      
      <!-- Панель добавления элементов (плавающая снизу) -->
      <div class="add-panel">
        <input 
          v-model="newElementText" 
          placeholder="Введите текст элемента" 
          class="add-input"
          @keyup.enter="addElement"
        />
        <button @click="addElement" class="btn-primary">
          + Добавить элемент
        </button>
      </div>
    </main>
    <!-- Боковая панель -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>Элементы</h2>
      </div>
      
      <div class="sidebar-content">
        <div class="elements-list">
          <div 
            v-for="element in elements" 
            :key="element.id"
            class="element-item"
          >
            <span>{{ element.text }}</span>
          </div>
          <div v-if="elements.length === 0" class="empty-state">
            Нет элементов
          </div>
        </div>
      </div>
      
      <div class="sidebar-footer">
        <div class="zoom-controls">
          <span>Масштаб: {{ Math.round(zoom * 100) }}%</span>
        </div>
        <div class="action-buttons">
          <button @click="fitToView" class="btn-secondary">📐 Fit to View</button>
          <button @click="clearAll" class="btn-danger">Очистить</button>
        </div>
      </div>
    </aside>

    
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'

const canvas = ref(null)
const elements = ref([])
const newElementText = ref('Lareum')
let idCounter = 0

const canvasScale = ref(1)
const canvasTransform = ref({ x: 0, y: 0 })

const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const transformStart = ref({ x: 0, y: 0 })

watch(elements, async () => {
  await nextTick()

  const canvasEl = canvas.value
  const wrapperRect = canvas.value?.parentElement?.getBoundingClientRect()
  
  if (canvasEl && wrapperRect) {
    const canvasContentWidth = canvasEl.scrollWidth
    const scale = Math.min(1, wrapperRect.width / canvasContentWidth)
    canvasScale.value = scale
  }
}, {deep:true})

const canvasStyle = computed(() => ({
  transform: `translate(${canvasTransform.value.x}px, ${canvasTransform.value.y}px) scale(${canvasScale.value})`,
  transformOrigin: 'top left'
}))

const getElementStyle = (element) => {
  // Можно добавить кастомные стили для элементов
  return {}
}

const addElement = async () => {
  if (!newElementText.value.trim()) return
  
  const text = newElementText.value.trim()
  elements.value.push({
    id: `el-${Date.now()}-${idCounter++}`,
    text: text
  })
  
  newElementText.value = 'Lareum'
}

const clearAll = () => { 
  elements.value = []
  canvasTransform.value = { x: 0, y: 0 }
  canvasScale.value = 1
}

const handleWheel = (event) => {
  event.preventDefault()
  const delta = event.deltaY > 0 ? 0.9 : 1.1
  canvasScale.value = Math.max(0.1, Math.min(3, canvasScale.value * delta))
}

const zoom = computed(() => canvasScale.value)  

onMounted(() => {
  const wrapper = canvas.value?.closest('.canvas-wrapper')
  if (wrapper) {
    wrapper.addEventListener('wheel', handleWheel, { passive: false })
    
    wrapper.addEventListener('mousedown', startDragging)
    document.addEventListener('mousemove', handleDragging) 
    document.addEventListener('mouseup', stopDragging) 
    
    wrapper.addEventListener('dragstart', (e) => e.preventDefault())
    
    wrapper.style.userSelect = 'none'
  }
})

const startDragging = (event) => {
  if (event.button !== 0) return
  
  isDragging.value = true
  dragStart.value = {
    x: event.clientX,
    y: event.clientY
  }
  transformStart.value = { ...canvasTransform.value }
  
  event.target.style.cursor = 'grabbing'
}

const handleDragging = (event) => {
  if (!isDragging.value) return
  
  const deltaX = event.clientX - dragStart.value.x
  const deltaY = event.clientY - dragStart.value.y
  
  canvasTransform.value = {
    x: transformStart.value.x + deltaX,
    y: transformStart.value.y + deltaY
  }
}

const stopDragging = (event) => {
  if (!isDragging.value) return
  
  isDragging.value = false
  
  const wrapper = canvas.value?.closest('.canvas-wrapper')
  if (wrapper) {
    wrapper.style.cursor = 'grab'
  }
}

onUnmounted(() => {
  const wrapper = canvas.value?.closest('.canvas-wrapper')
  if (wrapper) {
    wrapper.removeEventListener('wheel', handleWheel)
    wrapper.removeEventListener('mousedown', startDragging)
    document.removeEventListener('mousemove', handleDragging)
    document.removeEventListener('mouseup', stopDragging)
  }
})

const fitToView = async () => {
  await nextTick()
  
  const canvasEl = canvas.value
  const wrapperRect = canvas.value?.parentElement?.getBoundingClientRect()
  
  if (canvasEl && wrapperRect) {
    const canvasContentWidth = canvasEl.scrollWidth
    const scale = Math.min(1, wrapperRect.width / canvasContentWidth)
    
    canvasScale.value = scale > 0 ? scale : 1
    canvasTransform.value = { x: 0, y: 0 }
  }
}
</script>