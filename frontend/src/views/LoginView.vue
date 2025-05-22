<!-- src/views/LoginView.vue -->
<template>
  <div class="login-container">
    <div class="login-card">
      <h2>로그인</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">아이디 또는 이메일</label>
          <input 
            type="text" 
            id="username" 
            v-model="loginForm.username" 
            placeholder="아이디 또는 이메일 주소"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password">비밀번호</label>
          <input 
            type="password" 
            id="password" 
            v-model="loginForm.password" 
            placeholder="비밀번호"
            required
          />
        </div>

        <p v-if="error" class="error-message">{{ error }}</p>
        
        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>
      </form>
      
      <div class="social-login">
        <p>소셜 계정으로 로그인</p>
        <div class="social-buttons">
          <button @click="googleLogin" class="google-btn">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" alt="Google">
            Google로 로그인
          </button>
          <button @click="kakaoLogin" class="kakao-btn">
            <img src="https://developers.kakao.com/assets/img/about/logos/kakaolink/kakaolink_btn_medium.png" alt="Kakao">
            Kakao로 로그인
          </button>
        </div>
      </div>
      
      <div class="register-link">
        계정이 없으신가요? <router-link to="/register">회원가입</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRoute, useRouter } from 'vue-router'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

const loginForm = reactive({
  username: '',
  password: ''
})

const loading = ref(false)
const error = ref(null)

const handleLogin = async () => {
  error.value = null
  loading.value = true
  
  try {
    await userStore.login(loginForm.username, loginForm.password)
    
    // Redirect to the page the user was trying to access, or to home
    const redirectPath = route.query.redirect || '/'
    router.push(redirectPath)
  } catch (err) {
    error.value = err.error || '로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.'
  } finally {
    loading.value = false
  }
}

const googleLogin = () => {
  // Google OAuth URL
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
  const redirectUri = `${window.location.origin}/login/google/callback`
  const scope = 'email profile'
  
  const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${googleClientId}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code&scope=${encodeURIComponent(scope)}`
  
  window.location.href = googleAuthUrl
}

const kakaoLogin = () => {
  // Kakao OAuth URL
  const kakaoClientId = import.meta.env.VITE_KAKAO_CLIENT_ID
  const redirectUri = `${window.location.origin}/login/kakao/callback`
  
  const kakaoAuthUrl = `https://kauth.kakao.com/oauth/authorize?client_id=${kakaoClientId}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code`
  
  window.location.href = kakaoAuthUrl
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

h2 {
  text-align: center;
  margin-bottom: 24px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #555;
}

input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.login-btn:hover {
  background-color: #4338ca;
}

.login-btn:disabled {
  background-color: #a5a5a5;
  cursor: not-allowed;
}

.error-message {
  color: #e53e3e;
  font-size: 14px;
  margin-bottom: 16px;
}

.social-login {
  margin-top: 24px;
  text-align: center;
}

.social-login p {
  margin-bottom: 12px;
  color: #666;
  font-size: 14px;
}

.social-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.google-btn, .kakao-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.google-btn:hover {
  background-color: #f5f5f5;
}

.kakao-btn {
  background-color: #FEE500;
  color: #000000;
  border-color: #FEE500;
}

.kakao-btn:hover {
  background-color: #FDD800;
}

.google-btn img, .kakao-btn img {
  height: 20px;
  width: 20px;
}

.register-link {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.register-link a {
  color: #4f46e5;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>
