<template>
  <div class="p-6 min-h-screen bg-white">
    <h2 class="text-2xl font-bold mb-6">최종 결과 영상</h2>

    <div v-if="store.finalVideoUrl" class="flex flex-col items-center gap-4">
      <video :src="store.finalVideoUrl" controls class="w-full max-w-xl rounded shadow" />
      <a
        :href="store.finalVideoUrl"
        download="final-video.mp4"
        class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
      >
        비디오 다운로드
      </a>
    </div>

    <div v-else class="text-gray-500 text-center">
      아직 생성된 비디오가 없습니다. 2페이지에서 비디오를 만들어주세요.
    </div>

    <ArrowNextButton direction="prev" to="/keyframes" class="fixed bottom-6 left-6" />
  </div>
</template>

<script setup>
import ArrowNextButton from '@/components/ArrowNextButton.vue'
import { useAppStore } from '@/stores/appStore'

const store = useAppStore()
</script>
