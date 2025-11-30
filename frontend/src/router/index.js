import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

// Views
import Home from '@/views/Home.vue'
import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'
import UserDashboard from '@/views/user/Dashboard.vue'
import UserSummary from '@/views/user/Summary.vue'
import AdminDashboard from '@/views/admin/Dashboard.vue'
import AdminSummary from '@/views/admin/Summary.vue'
import Profile from '@/views/Profile.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresGuest: true }
  },
  {
    path: '/login',
    name: 'Login',
    redirect: '/' // Redirect to home which has login form
  },
  {
    path: '/register',
    name: 'Register',
    redirect: '/' // Redirect to home which has register form
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true, requiresUser: true }
  },
  {
    path: '/admin/profile',
    name: 'AdminProfile',
    component: Profile,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/user/dashboard',
    name: 'UserDashboard',
    component: UserDashboard,
    meta: { requiresAuth: true, requiresUser: true }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/summary',
    name: 'AdminSummary',
    component: AdminSummary,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/user/summary',
    name: 'UserSummary',
    component: UserSummary,
    meta: { requiresAuth: true, requiresUser: true }
  },
  {
    path: '/admin/parking-lots',
    name: 'AdminParkingLots',
    component: () => import('@/views/admin/ParkingLots.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/parking-lots/create',
    name: 'CreateParkingLot',
    component: () => import('@/views/admin/ParkingLots.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/parking-lots/:id/spots',
    name: 'ViewLotSpots',
    component: () => import('@/views/admin/LotSpots.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('@/views/admin/Users.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/reservations',
    name: 'AdminReservations',
    component: () => import('@/views/admin/Reservations.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/user/reservations',
    name: 'UserReservations',
    component: () => import('@/views/user/Reservations.vue'),
    meta: { requiresAuth: true, requiresUser: true }
  },
  {
    path: '/user/book-parking',
    name: 'BookParking',
    component: () => import('@/views/user/BookParking.vue'),
    meta: { requiresAuth: true, requiresUser: true }
  },
  {
    path: '/user/book-parking/:id',
    name: 'BookParkingLot',
    component: () => import('@/views/user/BookParking.vue'),
    meta: { requiresAuth: true, requiresUser: true }
  },
  // 404 Page
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  // Use Vite's BASE_URL exposed on import.meta.env
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  const requiresUser = to.matched.some(record => record.meta.requiresUser)

  // Check if user needs to be loaded
  if (localStorage.getItem('access_token') && !store.getters.user) {
    try {
      await store.dispatch('auth/fetchCurrentUser')
    } catch (error) {
      // Token invalid, continue with unauthenticated state
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  // Re-check authentication state after potentially loading user
  const isAuthenticated = store.getters.isAuthenticated
  const isAdmin = store.getters.isAdmin

  if (requiresGuest && isAuthenticated) {
    if (isAdmin) {
      next('/admin/dashboard')
    } else {
      next('/user/dashboard')
    }
    return
  }

  // Require authentication
  if (requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }
  // Role-based access control
  if (requiresAdmin && !isAdmin) {
    next('/user/dashboard')
    return
  }

  if (requiresUser && isAdmin) {
    next('/admin/dashboard')
    return
  }

  next()
})

export default router