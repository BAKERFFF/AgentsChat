import { ref, onUnmounted } from 'vue'

export function useWebSocket() {
  const ws = ref(null)
  const connected = ref(false)
  const error = ref(null)
  const listeners = new Map()

  function connect(url = 'ws://127.0.0.1:8000/ws') {
    return new Promise((resolve, reject) => {
      const socket = new WebSocket(url)

      socket.onopen = () => {
        connected.value = true
        error.value = null
        ws.value = socket
        resolve()
      }

      socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          const handlers = listeners.get(msg.type) || []
          handlers.forEach(fn => fn(msg))
          const globalHandlers = listeners.get('*') || []
          globalHandlers.forEach(fn => fn(msg))
        } catch (e) {
          console.error('Failed to parse WS message:', e)
        }
      }

      socket.onerror = (e) => {
        error.value = 'WebSocket connection error'
        reject(e)
      }

      socket.onclose = () => {
        connected.value = false
        ws.value = null
      }
    })
  }

  function send(msg) {
    if (ws.value && connected.value) {
      ws.value.send(JSON.stringify(msg))
    }
  }

  function on(msgType, handler) {
    if (!listeners.has(msgType)) {
      listeners.set(msgType, [])
    }
    listeners.get(msgType).push(handler)
    return () => {
      const handlers = listeners.get(msgType)
      if (handlers) {
        const idx = handlers.indexOf(handler)
        if (idx !== -1) handlers.splice(idx, 1)
      }
    }
  }

  function disconnect() {
    if (ws.value) {
      ws.value.close()
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return { connected, error, connect, send, on, disconnect }
}
