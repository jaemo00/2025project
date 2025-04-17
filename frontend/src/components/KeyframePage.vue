<template>
    <div class="max-w-3xl mx-auto p-6">
      <h2 class="text-2xl font-bold mb-4">키프레임 이미지 생성</h2>
  
      <div v-for="(keyframe, index) in keyframes" :key="keyframe.id" :ref="el => setPromptRef(el, index)">
        <KeyframePrompt @remove="removeKeyframe(index)" />
      </div>
  
      <button @click="addKeyframe" class="bg-green-600 text-white px-4 py-2 mt-4 rounded hover:bg-green-700">
        프롬프트 추가
      </button>
  
      <div class="text-center mt-8">
        <button @click="goToVideoPage" class="bg-purple-700 text-white px-6 py-3 rounded hover:bg-purple-800">
          🎬 동영상 제작
        </button>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, nextTick } from 'vue';
  import KeyframePrompt from './KeyframePrompt.vue';
  import { useRouter } from 'vue-router';
  
  export default {
    components: {
      KeyframePrompt,
    },
    setup() {
      const router = useRouter();
      const keyframes = ref([{ id: Date.now() }]);
      const promptRefs = ref([]);
  
      const setPromptRef = (el, index) => {
        if (el) {
          promptRefs.value[index] = el;
        }
      };
  
      const addKeyframe = () => {
        keyframes.value.push({ id: Date.now() });
  

        nextTick(() => {
          const lastIndex = keyframes.value.length - 1;
          const el = promptRefs.value[lastIndex];
          if (el && el.scrollIntoView) {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        });
      };
  
      const removeKeyframe = (index) => {
        keyframes.value.splice(index, 1);
        promptRefs.value.splice(index, 1);
      };
  
      const goToVideoPage = () => {
        router.push('/video');
      };
  
      return {
        keyframes,
        addKeyframe,
        removeKeyframe,
        goToVideoPage,
        setPromptRef,
      };
    },
  };
  </script>