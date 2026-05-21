import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/rta' },
  { path: '/rta',               name: 'rta',               component: () => import('../views/tools/RTAView.vue') },
  { path: '/transfer-function', name: 'transfer-function', component: () => import('../views/tools/TransferFunctionView.vue') },
  { path: '/spectrogram',       name: 'spectrogram',       component: () => import('../views/tools/SpectrogramView.vue') },
  { path: '/coherence',         name: 'coherence',         component: () => import('../views/tools/CoherenceView.vue') },
  { path: '/filter-designer',   name: 'filter-designer',   component: () => import('../views/tools/FilterDesignerView.vue') },
  { path: '/signal-generator',  name: 'signal-generator',  component: () => import('../views/tools/SignalGeneratorView.vue') },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
