<template>
  <div class="p-6 min-h-screen bg-[#12100E] text-gray-100">
    <h2 class="text-2xl font-bold mb-6 text-[#FFB224]">🎬 최종 결과물</h2>

    <div class="space-y-8">
      <div
        v-for="(block, index) in store.keyframes"
        :key="index"
        class="rounded-lg p-4 bg-[#1A1816] shadow border border-[#FFB224]/20"
      >
        <h3 class="font-semibold text-lg mb-2 text-[#FFB224]">
          🎨 프롬프트: {{ block.prompt }}
        </h3>
        <p class="mb-2 text-gray-300">🎞️ 행동 설명: {{ block.actionPrompt }}</p>

        <div class="flex flex-col md:flex-row gap-6 items-start">
          <!-- 선택한 이미지 -->
          <div class="w-48 h-48 overflow-hidden rounded border border-[#FFB224]/30">
            <img
              :src="block.selectedImageUrl"
              alt="선택한 이미지"
              class="w-full h-full object-cover"
            />
          </div>

          <!-- 비디오 영역 -->
          <div class="flex-1">
            <video
              :src="block.videoUrl"
              controls
              autoplay
              loop
              muted
              class="w-full max-w-xl rounded border border-[#FFB224]/30"
            />
            <a
              :href="block.videoUrl"
              :download="`video_${index + 1}.mp4`"
              class="inline-block mt-3 bg-[#FFB224] text-[#12100E] px-4 py-2 rounded font-semibold 
                     hover:bg-[#e6a020] transition-colors"
            >
              비디오 다운로드
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- 홈으로 돌아가기 버튼 -->
    <div class="mt-10 flex justify-center">
      <button
        @click="goHome"
        class="px-6 py-3 rounded font-semibold 
               bg-transparent text-[#FFB224] border border-[#FFB224]/60 
               hover:bg-[#FFB224]/10 transition-colors"
      >
        ⬅️ 처음으로 돌아가기
      </button>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '@/stores/appStore'
import { useRouter } from 'vue-router'

const store = useAppStore()
const router = useRouter()

function goHome() {
  router.push('/')
}
</script>
