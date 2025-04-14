<template>
    <button @click="goBack" class="arrow-back-button">
      ← 이전
    </button>
  </template>
  
  <script>
  export default {
    name: 'ArrowBackButton',
    methods: {
      goBack() {
        this.$router.back();
      },
    },
  };
  </script>
  
  <style scoped>
  .arrow-back-button {
    font-size: 1.2rem;
    padding: 0.5rem 1rem;
    margin: 1rem;
    background-color: #eee;
    border: none;
    border-radius: 8px;
    cursor: pointer;
  }
  .arrow-back-button:hover {
    background-color: #ddd;
  }
  </style>