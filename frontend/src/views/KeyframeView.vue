<template>
    <div class="p-6 min-h-screen bg-white">
      <h2 class="text-2xl font-bold mb-4">키프레임 생성</h2>
  
      <div
        v-if="store.generatedScenario"
        class="mb-6 p-4 bg-gray-100 border border-gray-300 rounded-lg text-sm text-gray-700 whitespace-pre-line"
      >

        <strong class="block text-gray-900 mb-1">생성된 시나리오:</strong>

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

      <div class="mt-8 flex justify-center">
      <button
        @click="generateFinalVideo"
        class="bg-purple-600 text-white px-6 py-3 rounded-lg shadow hover:bg-purple-700 transition"
      >
        최종 결과물 제작
      </button>
    </div>
  
      <ArrowNextButton direction="next" to="/final" class="fixed bottom-6 right-6" />
      <ArrowNextButton direction="prev" to="/create" class="fixed bottom-6 left-6" />
    </div>
  </template>
  
  <script setup>
import { useAppStore } from '@/stores/appStore'
import KeyframePage from '@/components/KeyframePage.vue'
import ArrowNextButton from '@/components/ArrowNextButton.vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

// Pinia store 및 router 사용
const store = useAppStore()
const router = useRouter()

// 이미지 생성
async function generateImage(index) {
  const block = store.keyframeBlocks[index]
  if (!block.text?.trim()) return

  try {
    const res = await axios.post('http://192.168.0.3:8000/api/generate-image', {
      prompt: block.text,
      setup: block.setup,
      userid:userId,
    })
    block.imageUrl = res.data.imageUrl
  } catch (err) {
    console.error('이미지 생성 실패:', err)
    alert('이미지 생성 중 오류가 발생했습니다.')
  }
}

// 비디오 생성
async function generateVideo(index) {
  const block = store.keyframeBlocks[index]
  if (!block.text?.trim() || !block.videoPrompt?.trim()) return

  try {
    const res = await axios.post('http://192.168.0.3:8000/api/generate-video', {
      imageUrl: block.imageUrl,
      videoPrompt: block.videoPrompt,
      userid:userId,
    })
    block.videoUrl = res.data.videoUrl
  } catch (err) {
    console.error('비디오 생성 실패:', err)
    alert('비디오 생성 중 오류가 발생했습니다.')
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
    width: 640,
    height: 360,
  })
}


async function generateFinalVideo() {
  const videoUrls = store.keyframeBlocks.map(b => b.videoUrl).filter(Boolean)

  if (!videoUrls.length) {
    alert('비디오가 하나 이상 필요합니다.')
    return
  }

  try {
    const res = await axios.post('http://192.168.0.3:8000/api/generate-video', {
  imageUrl: block.imageUrl,
  videoPrompt: block.videoPrompt, 
  userid: userId,
})

    store.finalVideoUrl = res.data.finalVideoUrl
    router.push('/final')
  } catch (err) {
    console.error('최종 비디오 생성 실패:', err)
    alert('최종 비디오 생성 중 오류가 발생했습니다.')
  }
}
</script>