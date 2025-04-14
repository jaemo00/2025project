<template>
    <div class="max-w-2xl mx-auto p-6">
      <h2 class="text-2xl font-bold mb-4">시나리오 생성</h2>
      
      <textarea
        v-model="prompt"
        placeholder="프롬프트를 입력하세요..."
        class="w-full border rounded p-3 mb-4"
        rows="4"
      ></textarea>
  
      <button @click="generateScenario" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        시나리오 생성
      </button>
  
      <div v-if="scenario" class="mt-6 bg-gray-100 p-4 rounded shadow">
        <h3 class="font-semibold mb-2">생성된 시나리오</h3>
        <p class="whitespace-pre-line">{{ scenario }}</p>
  
        <button @click="generateScenario" class="mt-4 bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700">
          다시 출력
        </button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        prompt: '',
        scenario: '',
      };
    },
    methods: {
      generateScenario() {
        if (this.prompt.trim() !== '') {
          this.scenario = `📽️ [${this.prompt}]\n이 프롬프트를 바탕으로 한 시나리오가 여기에 출력됩니다.`;
        } else {
          this.scenario = '';
        }
      },
    },
  };
  </script>
  
  <style scoped>
  </style>