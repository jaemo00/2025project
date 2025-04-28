<template>
    <div>
      <ScenarioSection />
      <ArrowNextButton target="/keyframes" />
    </div>
  </template>
  
  <script>
  import ScenarioSection from '@/components/ScenarioSection.vue';
  import ArrowNextButton from '@/components/ArrowNextButton.vue';
  
  export default {
    components: {
      ScenarioSection,
      ArrowNextButton,
    },
  };
  </script>