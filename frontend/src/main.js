import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'   // ✅ 라우터를 import

const app = createApp(App)

app.use(router)                 // ✅ 라우터를 등록
app.mount('#app')
