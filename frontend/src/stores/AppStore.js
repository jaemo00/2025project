import { defineStore } from 'pinia'
import { v4 as uuidv4 } from 'uuid'

export const useAppStore = defineStore('app', {
  state: () => ({
    // 기존 상태
    scenarioPrompt: '',
    generatedScenario: '',
    keyframeBlocks: [
      {
        text: '',
        imageUrl: '',
        videoUrl: '',
        videoPrompt: '',
        setup: { width: 640, height: 360 },
        modelName: '' 
      },
    ],
    finalVideoUrl: '',

    // WebSocket 관련 상태
    socket: null,
    socketStatus: '',
    progressMap: {}, // blockIndex: progress 값 저장용
    userId: '',
  }),

  persist: {
    storage: sessionStorage,
  },

  actions: {
    // 시나리오 초기화
    resetScenario() {
      this.scenarioPrompt = ''
      this.generatedScenario = ''
    },

      setUserId(id) {
    this.userId = id
  },

    // 키프레임 초기화
    resetKeyframes() {
      this.keyframeBlocks = [
      {
        text: '',
        imageUrl: '',
        videoUrl: '',
        videoPrompt: '',
        setup: { width: 640, height: 360 },
        modelName: '' 
      },
      ]
    },

     initWebSocket() {
  const savedId = localStorage.getItem('userId')
  if (!this.userId && savedId) {
    this.userId = savedId
  }

      // 이미 연결돼 있으면 다시 연결하지 않음
      if (this.socket && this.socket.readyState <= 1) return

      this.socket = new WebSocket(`ws://192.168.0.5:8000/ws?user_id=${this.userId}`)

      this.socket.onopen = () => {
        console.log('✅ WebSocket 연결 성공')
        this.socketStatus = 'connected'
      }

      this.socket.onclose = () => {
        console.warn('❌ WebSocket 연결 종료됨')
        this.socketStatus = 'disconnected'
      }

      this.socket.onerror = (error) => {
        console.error('⚠️ WebSocket 에러 발생:', error)
        this.socketStatus = 'error'
      }

      this.socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)

          // 예: image_progress 라는 타입이 왔을 때
          if (msg.type === 'image_progress') {
            const { blockIndex, progress } = msg
            this.progressMap[blockIndex] = progress
          }
        } catch (err) {
          console.warn('메시지 JSON 파싱 실패:', event.data)
        }
      }
    }
  }
})