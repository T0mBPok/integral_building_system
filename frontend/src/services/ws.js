let ws = null
let reconnectTimeout = null
let listeners = new Set()

const WS_URL = 'ws://localhost:9000/chat/ws'

export function connectWebSocket() {
  if (ws && ws.readyState === WebSocket.OPEN) return ws

  ws = new WebSocket(WS_URL)

  ws.onopen = () => {
    console.log('WebSocket подключен:', WS_URL)
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    listeners.forEach(cb => cb(data))
  }

  ws.onclose = () => {
    console.warn('WebSocket закрыт, переподключение...')
    ws = null
    if (!reconnectTimeout) {
      reconnectTimeout = setTimeout(() => {
        reconnectTimeout = null
        connectWebSocket()
      }, 2000)
    }
  }

  ws.onerror = (err) => {
    console.error('Ошибка WebSocket:', err)
  }

  return ws
}

export function sendWSMessage(payload) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(payload))
  } else {
    console.warn('WebSocket не подключен')
  }
}

export function subscribeWS(callback) {
  listeners.add(callback)
  return () => listeners.delete(callback) 
}

export function isWSConnected() {
  return ws && ws.readyState === WebSocket.OPEN
}

export function disconnectWebSocket() {
  console.log('🔌 Отключение WebSocket')
  if (ws) {
    ws.onclose = null
    ws.onerror = null
    ws.onmessage = null
    ws.close()
    ws = null
  }
  listeners.clear()
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout)
    reconnectTimeout = null
  }
}