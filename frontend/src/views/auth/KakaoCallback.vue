<!-- src/views/auth/KakaoCallback.vue -->
<template>
  <div class="callback-container">
    <div class="loading-box">
      <div class="spinner"></div>
      <p>Kakao 계정으로 로그인 중...</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter, useRoute } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

onMounted(async () => {
  try {
    // The authorization code is in the URL query parameters
    const code = route.query.code
    
    if (!code) {
      throw new Error('No authorization code found in callback URL')
    }
    
    // Use the code to authenticate with our backend
    await userStore.kakaoLogin(code)
    
    // Redirect to home or the page the user was trying to access
    router.push('/')
  } catch (error) {
    console.error('Kakao authentication error:', error)
    router.push({
      path: '/login',
      query: { error: 'kakao_auth_failed' }
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
  border-top: 4px solid #FEE500;
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
