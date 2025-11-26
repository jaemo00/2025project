<template>
  <div class="min-h-screen flex flex-col justify-center items-center bg-[#12100E] px-4">
    <div class="bg-[#1A1816] rounded-xl shadow-xl p-8 max-w-md w-full space-y-6 border border-[#FFB224]/20">
      <h1 class="text-2xl font-bold text-center text-[#FFB224]">AI 영상 프로젝트 시작</h1>

      <!-- 사용자 ID 입력 -->
      <input
        v-model="user_id"
        type="text"
        placeholder="아이디를 입력하세요"
        class="w-full rounded px-4 py-2 bg-[#12100E] text-gray-100 placeholder-gray-400
               border border-[#FFB224]/30 focus:outline-none focus:ring-2 focus:ring-[#FFB224] focus:border-transparent"
      />

      <!-- 로그인 -->
      <button
        @click="initUser"
        class="w-full py-2 rounded font-semibold 
               bg-[#FFB224] text-[#12100E] hover:bg-[#e6a020] 
               transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        로그인
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/appStore'
import axios from 'axios'

const user_id = ref('')
const router = useRouter()
const store = useAppStore()

async function initUser() {
  if (!user_id.value.trim()) return alert('아이디를 입력해주세요.')

  try {
    const res = await axios.post('/api/init-user', {
      user_id: user_id.value.trim()
    })

    const pid = Number(res.data?.project_id)
    
    if (!pid) {
      alert('프로젝트 생성에 실패했습니다.')
      return
    }
    
    store.user_id = user_id.value.trim()
    store.project_id = pid
    store.connectWebSocket()

    router.push('/scenario')
  } catch (e) {
    alert(e?.response?.data?.detail || '초기화 실패')
  }
}
</script>