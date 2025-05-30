<template>
  <div class="p-6 max-w-3xl mx-auto bg-white min-h-screen">
    <h2 class="text-2xl font-bold mb-6">시나리오 작업</h2>

    <!-- 새 시나리오 입력 -->
    <div class="flex gap-8 mb-10">
      <div class="w-1/2 flex flex-col space-y-4">
        <h3 class="text-xl font-semibold">AI 시나리오 생성</h3>
        <textarea
          v-model="store.scenarioPrompt"
          placeholder="시나리오 아이디어를 입력하세요..."
          class="w-full border rounded p-4 text-base"
          rows="6"
        ></textarea>

        <div class="flex gap-2">
          <button @click="generateScenario" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            시나리오 생성
          </button>
          <button
            v-if="store.generatedScenario"
            @click="generateScenario"
            class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
          >
            다시 생성
          </button>
        </div>
      </div>

      <!-- 생성된 시나리오 표시 -->
      <div class="w-1/2 bg-gray-100 rounded shadow p-4" v-if="store.generatedScenario">
        <h3 class="font-semibold mb-2">생성된 시나리오</h3>
        <p class="whitespace-pre-line text-gray-800">{{ store.generatedScenario }}</p>
      </div>
       <!-- 기존 시나리오 불러오기 버튼 -->
    <div class="mb-4">
      <button
        @click="showExisting = !showExisting"
        class="bg-gray-300 text-black px-4 py-2 rounded hover:bg-gray-400"
      >
        기존 시나리오 불러오기
      </button>
    </div>

    <!-- 기존 시나리오 목록 -->
    <div v-if="showExisting && store.scenarioList.length" class="bg-gray-50 p-4 rounded shadow">
      <h3 class="font-semibold mb-2">기존 시나리오 목록</h3>
      <ul class="space-y-1">
        <li
          v-for="s in store.scenarioList"
          :key="s.id"
          @click="loadScenario(s.id)"
          class="cursor-pointer text-blue-600 hover:underline"
        >
          {{ s.title }}
        </li>
      </ul>
    </div>
    <div v-else-if="showExisting" class="text-gray-500">
      불러올 시나리오가 없습니다.
  </div>
  </div>

      <ArrowNextButton direction="next" to="/keyframes" class="fixed bottom-6 right-6" />
      <ArrowNextButton direction="prev" to="/login" class="fixed bottom-6 left-6" />
    </div>
  </template>
  
  <script setup>
  import { useAppStore } from '@/stores/appStore'
  import ArrowNextButton from '@/components/ArrowNextButton.vue'
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  const store = useAppStore()
  

  async function generateScenario() {
  if (!store.scenarioPrompt.trim()) return

  try {
    const res = await axios.post('/api/generate-scenario', {
      userid: localStorage.getItem('userId'),
      prompt: store.scenarioPrompt
    })

    store.generatedScenario = res.data.scenario
  } catch (err) {
    console.error('시나리오 생성 실패:', err)
    alert('시나리오 생성 중 오류가 발생했습니다.')
  }
}
  const userId = ref('')
const socket = ref(null)
const socketStatus = ref('')

onMounted(() => {
  store.initWebSocket()
})
  </script>
