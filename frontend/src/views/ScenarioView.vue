<template>
    <div class="flex gap-8 p-6 min-h-screen bg-white">
      <div class="w-1/2 flex flex-col space-y-4">
        <h2 class="text-2xl font-bold">환영합니다!</h2>
        <p class="text-gray-600">AI 시나리오를 생성해보세요.</p>
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
  

      <div class="w-1/2 bg-gray-100 rounded shadow p-4" v-if="store.generatedScenario">
        <h3 class="font-semibold mb-2">생성된 시나리오</h3>
        <p class="whitespace-pre-line text-gray-800">{{ store.generatedScenario }}</p>
      </div>
  

      <ArrowNextButton direction="next" to="/keyframes" class="absolute bottom-6 right-6" />
    </div>
  </template>
  
  <script setup>
  import { useAppStore } from '@/stores/appStore'
  import ArrowNextButton from '@/components/ArrowNextButton.vue'
  import { v4 as uuidv4 } from 'uuid';
  import { ref, onMounted } from 'vue'
  import axios from 'axios'

  const store = useAppStore()
  
  async function generateScenario() { 
    if (store.scenarioPrompt.trim()) {
      try {
          const res = await axios.post('/api/generate-scenario', {
            userid: userId.value,
            scenarioPrompt: store.scenarioPrompt,
          })
          store.generatedScenario = res.data.scenario
        } catch (err) {
          console.error('시나리오 생성 실패:', err)
          alert('시나리오 생성 중 오류가 발생했습니다.')
        }  
    }
  }

const userId = ref('')
const socket = ref(null)
const socketStatus = ref('')

onMounted(() => {
  // UUID 생성 및 저장
  let savedId = localStorage.getItem('userId')
  if (!savedId) {
    savedId = uuidv4()
    console.log("생성된 사용자 ID:", savedId)
    localStorage.setItem('userId', savedId)
  }
  console.log("사용자 ID:", savedId)
  userId.value = savedId

  // 웹소켓 연결
  socket.value = new WebSocket(`ws://192.168.0.8:8000/ws?user_id=${savedId}`)

  socket.value.onopen = () => {
    console.log("웹소켓 연결 성공")
    socketStatus.value = '✅ 웹소켓 연결됨'
  }

  socket.value.onclose = () => {
    console.log("웹소켓 연결 종료")
    socketStatus.value = '❌ 연결 종료됨'
  }

  socket.value.onerror = (error) => {
    console.error("웹소켓 에러 발생:", error)
    socketStatus.value = '⚠️ 연결 중 에러'
  }

  socket.value.onmessage = (event) => {
    console.log("서버로부터 받은 메시지:", event.data)
  }
})
  </script>
