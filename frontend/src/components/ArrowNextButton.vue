<!--<template>
    <div class="flex justify-center mt-10">
      <button
        @click="$router.push(target)"
        class="animate-bounce text-4xl text-blue-500 hover:text-blue-700"
        :aria-label="'다음 페이지로 이동'"
      >
        ➡️
      </button>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      target: {
        type: String,
        required: true,
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
</style>-->


<template>
    <button @click="goNext" class="arrow-next-button">
      다음 →
    </button>
  </template>
  
  <script>
  export default {
    name: 'ArrowNextButton',
    methods: {
      goNext() {
        this.$router.go(1);
      },
    },
  };
  </script>
  
  <style scoped>
  .arrow-next-button {
    font-size: 1.2rem;
    padding: 0.5rem 1rem;
    margin: 1rem;
    background-color: #eee;
    border: none;
    border-radius: 8px;
    cursor: pointer;
  }
  .arrow-next-button:hover {
    background-color: #ddd;
  }
  </style>