import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({

    scenarioPrompt: '',
    generatedScenario: '',

    keyframeBlocks: [
      { text: '', imageUrl: '', videoUrl: '', videoPrompt: '', setup: { width: 640, height: 360  },},
    ],

    finalVideoUrl: '',
  }),
  persist: {
    storage: sessionStorage,
  },


  actions: {
    resetScenario() {
      this.scenarioPrompt = ''
      this.generatedScenario = ''
    },
    resetKeyframes() {
      this.keyframeBlocks = [
        { text: '', imageUrl: '', videoUrl: '', videoPrompt: '' }
      ]
    },
  },
})