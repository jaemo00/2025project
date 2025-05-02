  <template>
    <div class="min-h-screen bg-gray-100 text-gray-900">
      <header class="bg-white shadow p-4">
        <h1 class="text-2xl font-bold text-blue-600">AI 비디오 제작</h1>
      </header>

      <main class="p-4">
        <router-view />
      </main>
    </div>
  </template>

  <script>
  export default {
    name: 'App',
  }
  </script>

  <style scoped>
  </style>