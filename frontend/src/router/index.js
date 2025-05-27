import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import authService from '@/services/auth'

// Define routes
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: false }, // Everyone can access
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresGuest: true }, // Only non-logged in users can access
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true }, // Only logged in users can access
  },
  {
    path: '/map',
    name: 'Map',
    component: () => import('@/views/MapView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/articles',
    name: 'Articles',
    component: () => import('@/views/ArticlesView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/articles/create',
    name: 'ArticleCreate',
    component: () => import('@/views/ArticleCreateView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/articles/:id',
    name: 'ArticleDetail',
    component: () => import('@/views/ArticleDetailView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/youtube/search',
    name: 'YoutubeSearch',
    component: () => import('@/views/youtube/YoutubeSearchView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/youtube/saved',
    name: 'SavedVideos',
    component: () => import('@/views/youtube/SavedVideosView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/articles/:id/edit',
    name: 'ArticleEdit',
    component: () => import('@/views/ArticleCreateView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/login/google/callback',
    name: 'GoogleCallback',
    component: () => import('@/views/auth/GoogleCallback.vue'),
  },
  {
    path: '/login/kakao/callback',
    name: 'KakaoCallback',
    component: () => import('@/views/auth/KakaoCallback.vue'),
  },
  {
    path: '/debug-image',
    name: 'DebugImage',
    component: {
      template: `
        <div>
          <h1>Image Debug</h1>
          <img src="http://localhost:8000/media/profile_images/스크린샷_2025-05-22_093253.png" alt="Direct Image Test" />
          <p>If you can see the image above, the direct URL is working</p>
        </div>
      `,
    },
  },
  {
    path: '/image-test',
    name: 'image-test',
    component: () => import('../views/ImageTestView.vue'),
  },
  {
    path: '/products',
    name: 'Products',
    component: () => import('@/views/products/ProductsView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/products/dashboard',
    name: 'ProductDashboard',
    component: () => import('@/views/products/ProductDashboardView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/products/:type/:id',
    name: 'ProductDetail',
    component: () => import('@/views/products/ProductDetailView.vue'),
    meta: { requiresAuth: false },
    props: true,
  },
  {
    path: '/products/ai-recommendations',
    name: 'AIRecommendations',
    component: () => import('@/views/products/AIRecommendationsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('@/views/products/FavoritesView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/products/compare',
    name: 'ProductComparison',
    component: () => import('@/views/products/ProductComparisonView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/products/stocks',
    name: 'stockRankings',
    component: () => import('@/views/products/StockView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/products/stocks/:stockCode',
    name: 'stockDetail',
    component: () => import('@/views/products/StockDetail.vue'),
    meta: { requiresAuth: false },
    props: true,
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/admin/AdminDashboardView.vue'),
    meta: { requiresAdmin: true },
  },
  {
    path: '/admin/financial-products',
    name: 'AdminFinancialProducts',
    component: () => import('@/views/admin/FinancialProductsView.vue'),
    meta: { requiresAdmin: true },
  },
  {
    path: '/admin/deposits',
    name: 'AdminDepositProducts',
    component: () => import('@/views/admin/DepositProductsView.vue'),
    meta: { requiresAdmin: true },
  },
  {
    path: '/admin/savings',
    name: 'AdminSavingProducts',
    component: () => import('@/views/admin/SavingProductsView.vue'),
    meta: { requiresAdmin: true },
  },
  {
    path: '/admin/loans',
    name: 'AdminLoanProducts',
    component: () => import('@/views/admin/LoanProductsView.vue'),
    meta: { requiresAdmin: true },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  // Check for auth state
  const isLoggedIn = authService.isLoggedIn()
  const userStore = useUserStore()

  // For routes that require authentication
  if (to.meta.requiresAuth && !isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // For routes that require guest (non-logged in)
  if (to.meta.requiresGuest && isLoggedIn) {
    next({ name: 'Home' })
    return
  }

  // For routes that require admin access
  if (to.meta.requiresAdmin) {
    // If not logged in, redirect to login
    if (!isLoggedIn) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }

    // Check if user is admin
    try {
      // If user data exists in store and has admin flag
      if (userStore.user && (userStore.user.is_admin || userStore.user.is_superuser)) {
        next()
      } else {
        // Try to fetch user profile if we don't have it
        await userStore.fetchUserProfile()
        // Check again after fetching
        if (userStore.user && (userStore.user.is_admin || userStore.user.is_superuser)) {
          next()
        } else {
          // Not an admin, redirect to home
          next({ name: 'Home' })
        }
      }
    } catch (error) {
      console.error('Error checking admin status', error)
      next({ name: 'Home' })
    }
    return
  }

  next()
})

export default router
