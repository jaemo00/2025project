<template>
    <div class="max-w-3xl mx-auto p-6 text-center">
      <h2 class="text-2xl font-bold mb-4">🎬 동영상 미리보기</h2>
  
      <video
        ref="videoPlayer"
        class="w-full rounded shadow mb-4"
        controls
        :src="videoUrl"
      >
        브라우저가 video 태그를 지원하지 않습니다.
      </video>
  
      <div class="flex justify-center gap-4">
        <button @click="playVideo" class="bg-blue-600 text-white px-5 py-2 rounded hover:bg-blue-700">
          ▶ 재생
        </button>
        <a :href="videoUrl" download class="bg-green-600 text-white px-5 py-2 rounded hover:bg-green-700">
          💾 다운로드
        </a>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        // 실제 영상이 있다면 여기에 해당 URL을 연결
        videoUrl: 'https://www.w3schools.com/html/mov_bbb.mp4', // 샘플 영상
      };
    },
    methods: {
      playVideo() {
        this.$refs.videoPlayer.play();
      },
    },
  };
  </script>