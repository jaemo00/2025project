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
  
  const store = useAppStore()
  
  function generateScenario() {
    if (store.scenarioPrompt.trim()) {
      store.generatedScenario = `Lorem ipsum dolor sit amet, consectetur adipiscing elit.
  "${store.scenarioPrompt}" 기반으로 시나리오가 이렇게 나올 수 있습니다.
  
  Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.`
    }
  }
  </script>
  