<template>
  <div class="flex justify-center mt-10">
    <button
      @click="goTarget"
      class="animate-bounce text-4xl text-blue-500 hover:text-blue-700"
      :aria-label="'다음 페이지로 이동'"
    >
      ➡️
    </button>
  </div>
</template>

<script>
export default {
  name: 'ArrowNextButton',
  props: {
    target: {
      type: String,
      required: true,
    },
  },
  methods: {
    goTarget() {
      this.$router.push(this.target);
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