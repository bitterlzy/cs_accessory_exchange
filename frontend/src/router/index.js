import { createRouter, createWebHashHistory } from 'vue-router'
import { getToken } from '../api'

const routes = [
  { path: '/login', component: () => import('../views/Login.vue') },
  { path: '/register', component: () => import('../views/Register.vue') },
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: () => import('../views/Dashboard.vue'), meta: { requiresAuth: true } },
  { path: '/inventory', component: () => import('../views/Inventory.vue'), meta: { requiresAuth: true } },
  { path: '/listings', component: () => import('../views/Listings.vue'), meta: { requiresAuth: true } },
  { path: '/my-listings', component: () => import('../views/MyListings.vue'), meta: { requiresAuth: true } },
  { path: '/offers', component: () => import('../views/Offers.vue'), meta: { requiresAuth: true } },
  { path: '/trades', component: () => import('../views/Trades.vue'), meta: { requiresAuth: true } },
  { path: '/notifications', component: () => import('../views/Notifications.vue'), meta: { requiresAuth: true } },
  { path: '/kyc', component: () => import('../views/KYC.vue'), meta: { requiresAuth: true } },
  { path: '/steam', component: () => import('../views/Steam.vue'), meta: { requiresAuth: true } },
]

var router = createRouter({ history: createWebHashHistory(), routes })
router.beforeEach(function(to, from, next) {
  if (to.meta.requiresAuth && !getToken()) next('/login')
  else next()
})
export default router