<template>
    <div class="p-6 min-h-screen bg-white">
  <div class="p-6 max-w-md mx-auto">
    <h2 class="text-2xl font-bold mb-4">아이디 입력</h2>
    <input
      v-model="userId"
      placeholder="아이디를 입력하세요"
      class="w-full border p-2 rounded"
    />

  </div>

        <ArrowNextButton direction="next" to="/create" class="absolute bottom-6 right-6" />
        </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/appStore'
import { ref } from 'vue'

const store = useAppStore()
const router = useRouter()
const userId = ref('')

</script>