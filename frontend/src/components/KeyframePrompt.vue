<template>
    <div class="border p-4 rounded mb-4 shadow-sm bg-white">
      <textarea
        v-model="prompt"
        placeholder="키프레임을 생성할 프롬프트를 입력하세요"
        class="w-full border rounded p-2 mb-3"
        rows="2"
      ></textarea>
  
      <div class="flex gap-2">
        <button @click="generateImage" class="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">
          이미지 생성
        </button>
        <button @click="$emit('remove')" class="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600">
          삭제
        </button>
      </div>
  
      <div v-if="imageUrl" class="mt-4">
        <img :src="imageUrl" alt="생성된 이미지" class="w-full max-h-60 object-cover rounded shadow" />
        <button @click="generateImage" class="mt-2 bg-gray-700 text-white px-3 py-1 rounded hover:bg-gray-800">
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
        imageUrl: '',
      };
    },
    methods: {
      generateImage() {
        if (this.prompt.trim() !== '') {
          // 이미지 생성 api 연동
          const seed = Math.floor(Math.random() * 1000);
          this.imageUrl = `https://picsum.photos/seed/${seed}/600/300`;
        }
      },
    },
  };
  </script>