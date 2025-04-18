<template>
    <div>
      <KeyframePage />    
      <ArrowBackButton target="/" />
      <ArrowNextButton target="/video" />
    </div>
  </template>
  
  <script>
  import KeyframePage from '@/components/KeyframePage.vue';
  import ArrowBackButton from '@/components/ArrowBackButton.vue';
  import ArrowNextButton from '@/components/ArrowNextButton.vue';
  
  export default {
    components: {
      KeyframePage,
      ArrowNextButton,
      ArrowBackButton,
    },
  };
  </script>