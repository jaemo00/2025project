import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({

    scenarioPrompt: '',
    generatedScenario: '',

    keyframeBlocks: [
      { text: '', imageUrl: '', videoUrl: '', videoPrompt: '' },
    ],

    finalVideoUrl: '',
  }),
  persist: true,

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