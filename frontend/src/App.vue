  <template>
    <div class="min-h-screen bg-gray-100 text-gray-900">
      <header class="bg-white shadow p-4">
        <h1 class="text-2xl font-bold text-blue-600">AI 비디오 제작</h1>
      </header>

      <div id="app">
    <nav class="bg-gray-800 text-white p-4 flex gap-4">
      <router-link to="/" class="hover:underline">홈</router-link>
      <router-link to="/keyframes" class="hover:underline">키프레임</router-link>
      <router-link to="/video" class="hover:underline">영상 생성</router-link>
    </nav>


      <main class="p-4">
        <router-view />
      </main>
    </div>
    </div>
  </template>

  <script>
  export default {
    name: 'App',
  }
  </script>

  <style scoped>
  </style>