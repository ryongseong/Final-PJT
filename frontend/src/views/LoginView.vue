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
            <img
              src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/1024px-Google_%22G%22_logo.svg.png"
              alt="Google"
            />
            Google로 로그인
          </button>
          <button @click="kakaoLogin" class="kakao-btn">
            <img
              src="https://developers.kakao.com/assets/img/about/logos/kakaolink/kakaolink_btn_medium.png"
              alt="Kakao"
            />
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
  password: '',
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
  background-color: var(--background-primary); /* Themed background */
  padding: 2rem; /* Consistent padding */
  font-family: var(--font-family-base);
}

.login-card {
  width: 100%;
  max-width: 450px; /* Slightly wider for better spacing */
  background-color: var(--card-bg);
  border-radius: var(--border-radius-lg); /* Consistent border radius */
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
  padding: 2.5rem; /* Increased padding */
}

.login-card h2 {
  text-align: center;
  margin-bottom: 2rem; /* Increased margin */
  color: var(--text-primary);
  font-family: 'Pretendard Variable', serif; /* Title font */
  font-size: 2rem; /* Adjusted size */
  font-weight: 700;
}

.form-group {
  margin-bottom: 1.5rem; /* Consistent margin */
}

.form-group label {
  display: block;
  margin-bottom: 0.6rem; /* Adjusted margin */
  font-size: 0.9rem; /* Adjusted size */
  color: var(--text-secondary);
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.8rem 1rem; /* Adjusted padding */
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: 1rem;
  background-color: var(--background-primary);
  color: var(--text-primary);
  transition:
    border-color var(--transition-speed),
    box-shadow var(--transition-speed);
}

.form-group input::placeholder {
  color: var(--text-secondary);
  opacity: 0.7;
}

.form-group input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(var(--accent-color-rgb, 163, 184, 153), 0.2);
}

.error-message {
  color: #ef4444; /* Consistent error color */
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 0.8rem 1rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  text-align: center;
}

/* Using global .action-btn styles where appropriate */
.login-btn,
.social-btn {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.8rem 1.5rem;
  border-radius: var(--border-radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-speed);
  font-size: 1rem;
  border: 1px solid transparent;
}

.login-btn {
  background-color: var(--accent-color);
  color: var(--button-text);
  border-color: var(--accent-color);
}

.login-btn:hover:not(:disabled) {
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.login-btn:disabled {
  background-color: var(--accent-color);
  opacity: 0.6;
  cursor: not-allowed;
}

.social-login {
  margin-top: 2rem;
  text-align: center;
}

.social-login p {
  margin-bottom: 1rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.social-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.social-btn {
  gap: 0.8rem;
  background-color: var(--background-primary);
  color: var(--text-primary);
  border-color: var(--border-color);
}

.social-btn:hover {
  border-color: var(--accent-color);
  background-color: var(--card-bg); /* Slightly different hover for distinctiveness */
}

.social-btn img {
  height: 20px;
  width: 20px;
}

.google-btn,
.kakao-btn {
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
  background-color: #fee500;
  color: #000000;
  border-color: #fee500;
}

.kakao-btn:hover {
  background-color: #fdd800;
}

.google-btn img,
.kakao-btn img {
  height: 20px;
  width: 20px;
}

.register-link {
  margin-top: 2rem;
  text-align: center;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.register-link a {
  color: var(--accent-color);
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover {
  text-decoration: underline;
  color: var(--accent-hover);
}

@media (max-width: 480px) {
  .login-card {
    padding: 2rem 1.5rem;
  }
  .login-card h2 {
    font-size: 1.8rem;
  }
}
</style>
