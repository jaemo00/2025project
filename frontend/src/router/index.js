import { createRouter, createWebHistory } from 'vue-router'

// 각 View 컴포넌트 import
import LoginView from '../views/LoginView.vue'
import ScenarioView from '../views/ScenarioView.vue'
import KeyframeView from '../views/KeyframeView.vue'
import FinalVideoView from '../views/FinalVideoView.vue'

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path:'/login',
    name: 'Login',
    component: LoginView,
  },
  {
    path: '/create',
    name: 'Scenario',
    component: ScenarioView,
  },
  {
    path: '/keyframes',
    name: 'Keyframes',
    component: KeyframeView,
  },
  {
    path: '/final',
    name: 'FinalVideo',
    component: FinalVideoView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router