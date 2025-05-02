<template>
    <div class="p-6 min-h-screen bg-white">
      <h2 class="text-2xl font-bold mb-4">키프레임 생성</h2>
  
      <div
        v-if="store.generatedScenario"
        class="mb-6 p-4 bg-gray-100 border border-gray-300 rounded-lg text-sm text-gray-700 whitespace-pre-line"
      >
        <strong class="block text-gray-900 mb-1">📘 생성된 시나리오:</strong>
        {{ store.generatedScenario }}
      </div>
  

      <div class="flex flex-col gap-6">
        <KeyframePage
          v-for="(block, index) in store.keyframeBlocks"
          :key="index"
          :block="block"
          :isLast="index === store.keyframeBlocks.length - 1"
          @updateImage="generateImage(index)"
          @updateVideo="generateVideo(index)"
          @addPrompt="addPrompt"
          @regenerateImage="regenerateImage(index)"
          @regenerateVideo="regenerateVideo(index)"
        />
      </div>
  
      <ArrowNextButton direction="next" to="/final" class="fixed bottom-6 right-6" />
      <ArrowNextButton direction="prev" to="/create" class="fixed bottom-6 left-6" />
    </div>
  </template>
  
  <script>
  import { useAppStore } from '@/stores/appStore'
  import KeyframePage from '@/components/KeyframePage.vue'
  import ArrowNextButton from '@/components/ArrowNextButton.vue'
  
  export default {
    name: 'KeyframeView',
    components: {
      KeyframePage,
      ArrowNextButton,
    },
    setup() {
      const store = useAppStore()
  
      function generateImage(index) {
        const block = store.keyframeBlocks[index]
        if (block.text?.trim()) {
          block.imageUrl = `https://picsum.photos/seed/${Math.random()}/600/300`
        }
      }
  
      function generateVideo(index) {
        const block = store.keyframeBlocks[index]
        if (block.text?.trim()) {
          block.videoUrl = `https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4`
        }
      }
  
      function regenerateImage(index) {
        generateImage(index)
      }
  
      function regenerateVideo(index) {
        generateVideo(index)
      }
  
      function addPrompt() {
        store.keyframeBlocks.push({
          text: '',
          imageUrl: '',
          videoUrl: '',
          videoPrompt: '',
        })
      }
  
      return {
        store,
        generateImage,
        generateVideo,
        regenerateImage,
        regenerateVideo,
        addPrompt,
      }
    },
  }
  </script>