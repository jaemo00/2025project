<template>
    <button @click="Home" class="home-button">
      홈으로
    </button>
  </template>
  
  <script>
  export default {
    name: 'HomeButton',
    methods: {
      Home() {
        this.$router.push('/');
      },
    },
  };
  </script>
  
  <style scoped>
  .home-button {
    font-size: 1.2rem;
    padding: 0.5rem 1rem;
    margin: 1rem;
    background-color: #eee;
    border: none;
    border-radius: 8px;
    cursor: pointer;
  }
  .home-button:hover {
    background-color: #ddd;
  }
  </style>