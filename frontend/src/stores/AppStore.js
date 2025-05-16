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

    // 키프레임 초기화
    resetKeyframes() {
      this.keyframeBlocks = [
        { text: '', imageUrl: '', videoUrl: '', videoPrompt: '' },
      ]
    },

    // ✅ WebSocket 연결 초기화
    initWebSocket() {
      let savedId = localStorage.getItem('userId')
      if (!savedId) {
        savedId = uuidv4()
        localStorage.setItem('userId', savedId)
      }
      this.userId = savedId

      this.socket = new WebSocket(`ws://192.168.0.3:8000/ws?user_id=${savedId}`)

      this.socket.onopen = () => {
        console.log('✅ 웹소켓 연결됨')
        this.socketStatus = '✅ 연결됨'
      }

      this.socket.onclose = () => {
        console.log('❌ 웹소켓 종료됨')
        this.socketStatus = '❌ 연결 종료됨'
      }

      this.socket.onerror = (e) => {
        console.error('⚠️ 웹소켓 에러 발생:', e)
        this.socketStatus = '⚠️ 에러 발생'
      }

      this.socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          if (msg.type === 'image_progress') {
            this.progressMap[msg.blockIndex] = msg.progress
          }
        } catch (e) {
          console.warn('메시지 파싱 실패:', event.data)
        }
      }
    },
  },
})