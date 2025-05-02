<template>
    <div class="w-full rounded-xl bg-[#f5f5dc] p-6 shadow-md flex gap-6 items-start">
      <!-- 왼쪽: 프롬프트 입력 -->
      <div class="w-1/3 flex flex-col gap-3">
        <textarea
          v-model="block.text"
          placeholder="프롬프트를 입력하세요"
          class="w-full h-36 bg-white border border-gray-300 rounded-lg p-3 text-base text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-400"
        ></textarea>
  
        <button
          @click="$emit('updateImage')"
          v-if="!block.imageUrl"
          class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          이미지 생성
        </button>
  
        <button
          v-if="isLast"
          @click="$emit('addPrompt')"
          class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        >
          프롬프트 추가
        </button>
      </div>
  
     <!-- 오른쪽: 이미지 + 비디오 설명 + 비디오 (수평 정렬) -->
<div v-if="block.imageUrl" class="flex gap-4 items-start">
  <!-- 이미지 -->
  <div class="relative">
    <img :src="block.imageUrl" class="w-60 h-36 object-cover rounded shadow" />
    <button
      @click="$emit('regenerateImage')"
      class="absolute top-2 right-2 text-sm bg-white px-2 py-1 rounded shadow"
    >
      다시 생성
    </button>
  </div>

  <!-- 비디오 프롬프트 + 버튼 -->
  <div class="flex flex-col gap-2 w-60">
    <textarea
      v-model="block.videoPrompt"
      placeholder="키프레임 설명 (비디오용 프롬프트)"
      class="w-full h-36 bg-white border border-gray-300 rounded-lg p-3 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-green-400"
    ></textarea>

    <button
      v-if="!block.videoUrl"
      @click="$emit('updateVideo')"
      class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
    >
      비디오 생성
    </button>
  </div>

  <!-- 비디오 -->
  <div v-if="block.videoUrl" class="relative">
  <img
    v-if="block.videoUrl.endsWith('.gif')"
    :src="block.videoUrl"
    class="w-60 h-36 object-cover rounded shadow"
  />
  <video
    v-else
    :src="block.videoUrl"
    controls
    class="w-60 h-36 object-cover rounded shadow"
  />
  <button
    @click="$emit('regenerateVideo')"
    class="absolute top-2 right-2 text-sm bg-white px-2 py-1 rounded shadow"
  >
    다시 생성
  </button>
</div>
</div>
</div>
  </template>
  
  <script>
  export default {
    name: 'KeyframePage',
    props: {
      block: Object,
      isLast: Boolean,
    },
  }
  </script>
  