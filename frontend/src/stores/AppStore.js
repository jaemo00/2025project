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
  },
})