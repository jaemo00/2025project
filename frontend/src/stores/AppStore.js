import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAppStore = defineStore('app', {
  state: () => ({
    user_id: '',
    project_id: null,
    scenario: '',
    keyframes: [], // 각 프롬프트 블록의 정보들
    characterImage:'',
    socket: null,    // WebSocket 객체 보관
    imgProgress:0,
    videoProgress: 0
  }),
  actions: {
    loadProject(data) {
      this.project_id = data.project_id ? Number(data.project_id) : null
    },


    connectWebSocket() {
      if (this.socket) return  // 중복 연결 방지
      const ws = new WebSocket(`ws://localhost:8080/ws?user_id=${this.user_id}`)

      ws.onopen = () => {
        console.log('✅ WebSocket 연결됨')
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'img_progress') {
          this.imgProgress = Number(data.progress ?? 0)
        }
 
        if (data.type === 'video_progress') {
          console.log('받은 영상 생성 진행률:', data.progress)
          this.videoProgress = Number(data.progress ?? 0)
        }
      }

      ws.onclose = () => {
        console.log('❌ WebSocket 종료')
        this.socket = null
      }

      this.socket = ws
    },
    sendMessage(message) {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(message)
      }
    },
    disconnectWebSocket() {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.close()
      }
      this.socket = null
    }
  }
})