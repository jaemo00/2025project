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
    socket: null    // WebSocket 객체 보관
  }),
  actions: {
    loadProject(data) {
      this.project_id = data.project_id ? Number(data.project_id) : null
    },

    async ensureProjectId({ title }) {
      if (this.project_id) return this.project_id
      if (!this.user_id) throw new Error('로그인이 필요합니다.')

      // 새 프로젝트 생성
      const res = await axios.post('/api/project', {
        user_id: this.user_id,
        title: title || 'Untitled'
      })
      const pid = Number(res.data?.project_id)
      if (!pid) throw new Error('프로젝트 생성 실패: project_id 누락')
      this.project_id = pid
      return pid
    },
    connectWebSocket() {
      if (this.socket) return  // 중복 연결 방지
      const ws = new WebSocket(`ws://localhost:8000/ws?user_id=${this.user_id}`)

      ws.onopen = () => {
        console.log('✅ WebSocket 연결됨')
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'image_progress') {
          const block = this.keyframes[data.blockIndex]
          if (block) block.progress = data.progress
        }

        if (data.type === 'video_progress') {
          const block = this.keyframes[data.blockIndex]
          if (block) block.videoProgress = data.progress
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