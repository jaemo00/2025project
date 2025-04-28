import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import KeyframeView from '../views/KeyframeView.vue';
import VideoView from '../views/VideoView.vue';

const routes = [
  { path: '/', name: 'Home', component: HomeView },
  { path: '/keyframes', name: 'Keyframe', component: KeyframeView },
  { path: '/video', name: 'Video', component: VideoView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;