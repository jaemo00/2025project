<template>
  <div class="p-6 min-h-screen bg-white">
    <div class="p-6 max-w-md mx-auto">
      <h2 class="text-2xl font-bold mb-4">아이디 입력</h2>

      <div class="flex gap-2">
        <input
          v-model="userId"
          placeholder="아이디를 입력하세요"
          class="flex-1 border p-2 rounded"
        />
        <button
          @click="login"
          class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          로그인
        </button>
      </div>
    </div>

        <ArrowNextButton direction="next" to="/create" class="fixed bottom-6 right-6" />
        </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/appStore'
import { ref } from 'vue'
import axios from 'axios'
import ArrowNextButton from '@/components/ArrowNextButton.vue'

const router = useRouter()
const store = useAppStore()
const userId = ref('')

async function login() {
  if (!userId.value.trim()) return

  const trimmedId = userId.value.trim()
  store.setUserId(trimmedId)
  localStorage.setItem('userId', trimmedId)

  try {
    await axios.post('http://192.168.0.5:8000/api/init-user', {
      userid: trimmedId
    })
    
    const res = await axios.get(`http://192.168.0.5:8000/api/scenario-list?user_id=${userId.value.trim()}`)
    store.scenarioList = res.data.scenarios
  } catch (e) {
    console.error('시나리오 목록 로딩 실패:', e)
  }

  router.push('/create')
}
</script>