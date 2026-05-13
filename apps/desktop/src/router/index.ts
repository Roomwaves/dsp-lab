import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import AnalysisView from '../views/AnalysisView.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: AnalysisView
    }
  ]
});

export default router;