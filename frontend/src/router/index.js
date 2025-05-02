import { createRouter, createWebHistory } from 'vue-router'

// 각 View 컴포넌트 import
import ScenarioView from '../views/ScenarioView.vue'
import KeyframeView from '../views/KeyframeView.vue'
import FinalVideoView from '../views/FinalVideoView.vue'

const routes = [
  {
    path: '/',
    redirect: '/create',
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