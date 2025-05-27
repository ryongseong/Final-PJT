<!-- src/views/auth/GoogleCallback.vue -->
<template>
  <div class="callback-container">
    <div class="loading-box">
      <div class="spinner"></div>
      <p>Google 계정으로 로그인 중...</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

onMounted(async () => {
  try {
    // The access token is in the URL fragment
    // const hash = window.location.hash.substring(1)
    // const params = new URLSearchParams(hash)
    const token = new URLSearchParams(window.location.search).get('code');
    
    if (!token) {
      throw new Error('No access token found in callback URL')
    }
    
    // Use the token to authenticate with our backend
    await userStore.googleLogin(token)
    
    // Redirect to home or the page the user was trying to access
    router.push('/')
  } catch (error) {
    console.error('Google authentication error:', error)
    router.push({
      path: '/login',
      query: { error: 'google_auth_failed' }
    })
  }
})
</script>

<style scoped>
.callback-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.loading-box {
  text-align: center;
  padding: 30px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #4f46e5;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

p {
  color: #666;
  font-size: 16px;
}
</style>
