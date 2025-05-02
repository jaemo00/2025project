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
<<<<<<< HEAD
  persist: {
    storage: sessionStorage,
  },
=======
  persist: true,
>>>>>>> be6f12f0023d55478d6b83545fdbff6ba267a386

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