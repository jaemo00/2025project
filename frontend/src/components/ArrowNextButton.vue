<template>
    <button
      @click="$router.push(to)"
      class="text-5xl text-blue-600 hover:text-blue-800 transition"
      :class="direction === 'next' ? 'rotate-0' : 'rotate-180'"
    >
      ➤
    </button>
  </template>
  
  <script>
  export default {
    props: {
      direction: {
        type: String,
        default: 'next', 
      },
      to: {
        type: String,
        required: true,
      },
    },
  };
  </script>