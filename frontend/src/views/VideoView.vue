<template>
    <VideoPage />
    <ArrowBackButton target="/keyframes" />
    <HomeButton target="/" />
  </template>
  
  <script>
  import VideoPage from '@/components/VideoPage.vue';
  import ArrowBackButton from '@/components/ArrowBackButton.vue';
  import HomeButton from '@/components/HomeButton.vue'
  
  export default {
    components: {
      VideoPage,
      ArrowBackButton,
      HomeButton,
    },
  };
  </script>