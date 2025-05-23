<!-- src/views/LoginView.vue -->
<template>
  <div class="login-container">
    <div class="login-card">
      <h2>{{ currentLanguage === 'ko' ? '로그인' : 'Login' }}</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">{{ currentLanguage === 'ko' ? '아이디 또는 이메일' : 'Username or Email' }}</label>
          <input 
            type="text" 
            id="username" 
            v-model="loginForm.username" 
            :placeholder="currentLanguage === 'ko' ? '아이디 또는 이메일 주소' : 'Username or email address'"
            required
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label for="password">{{ currentLanguage === 'ko' ? '비밀번호' : 'Password' }}</label>
          <div class="password-input-wrapper">
            <input 
              :type="showPassword ? 'text' : 'password'" 
              id="password" 
              v-model="loginForm.password" 
              :placeholder="currentLanguage === 'ko' ? '비밀번호' : 'Password'"
              required
              class="form-input"
            />
            <button 
              type="button" 
              class="toggle-password" 
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
        </div>

        <div class="remember-forgot">
          <label class="remember-me">
            <input type="checkbox" v-model="rememberMe">
            <span>{{ currentLanguage === 'ko' ? '로그인 상태 유지' : 'Remember me' }}</span>
          </label>
          <a href="#" class="forgot-password">{{ currentLanguage === 'ko' ? '비밀번호 찾기' : 'Forgot password?' }}</a>
        </div>

        <p v-if="error" class="error-message">{{ error }}</p>
        
        <button type="submit" class="login-btn" :disabled="loading" :class="{ 'loading': loading }">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? (currentLanguage === 'ko' ? '로그인 중...' : 'Logging in...') : (currentLanguage === 'ko' ? '로그인' : 'Login') }}
        </button>
      </form>
      
      <div class="divider">
        <span>{{ currentLanguage === 'ko' ? '또는' : 'OR' }}</span>
      </div>
      
      <div class="social-login">
        <button @click="googleLogin" class="social-btn google-btn">
          <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" alt="Google">
          {{ currentLanguage === 'ko' ? 'Google로 계속하기' : 'Continue with Google' }}
        </button>
        <button @click="kakaoLogin" class="social-btn kakao-btn">
          <img src="https://developers.kakao.com/assets/img/about/logos/kakaolink/kakaolink_btn_medium.png" alt="Kakao">
          {{ currentLanguage === 'ko' ? 'Kakao로 계속하기' : 'Continue with Kakao' }}
        </button>
      </div>
      
      <div class="register-link">
        {{ currentLanguage === 'ko' ? '계정이 없으신가요?' : 'Don\'t have an account?' }} 
        <router-link to="/register">{{ currentLanguage === 'ko' ? '회원가입' : 'Sign up' }}</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRoute, useRouter } from 'vue-router'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

// 언어 설정 관련
const currentLanguage = ref('ko')

// 로그인 폼
const loginForm = reactive({
  username: '',
  password: ''
})

// 상태 관리
const loading = ref(false)
const error = ref(null)
const showPassword = ref(false)
const rememberMe = ref(false)

// 컴포넌트 마운트 시 언어 설정 확인
onMounted(() => {
  const savedLanguage = localStorage.getItem('language')
  if (savedLanguage) {
    currentLanguage.value = savedLanguage
  }
})

const handleLogin = async () => {
  error.value = null
  loading.value = true
  
  try {
    await userStore.login(loginForm.username, loginForm.password, rememberMe.value)
    
    // Redirect to the page the user was trying to access, or to home
    const redirectPath = route.query.redirect || '/'
    router.push(redirectPath)
  } catch (err) {
    error.value = err.error || (currentLanguage.value === 'ko' 
      ? '로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.' 
      : 'Login failed. Please check your username and password.')
  } finally {
    loading.value = false
  }
}

const googleLogin = () => {
  // Google OAuth URL
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
  const redirectUri = `${window.location.origin}/login/google/callback`
  const scope = 'email profile'
  
  if (!googleClientId) {
    error.value = currentLanguage.value === 'ko' 
      ? 'Google 로그인 설정이 되어있지 않습니다.' 
      : 'Google login is not configured.'
    return
  }
  
  const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${googleClientId}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code&scope=${encodeURIComponent(scope)}`
  
  window.location.href = googleAuthUrl
}

const kakaoLogin = () => {
  // Kakao OAuth URL
  const kakaoClientId = import.meta.env.VITE_KAKAO_CLIENT_ID
  const redirectUri = `${window.location.origin}/login/kakao/callback`
  
  if (!kakaoClientId) {
    error.value = currentLanguage.value === 'ko' 
      ? 'Kakao 로그인 설정이 되어있지 않습니다.' 
      : 'Kakao login is not configured.'
    return
  }
  
  const kakaoAuthUrl = `https://kauth.kakao.com/oauth/authorize?client_id=${kakaoClientId}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code`
  
  window.location.href = kakaoAuthUrl
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 160px); /* Account for header and footer */
  background: linear-gradient(135deg, var(--color-background-start) 0%, var(--color-background-end) 100%);
  padding: 40px 20px;
}

.login-card {
  width: 100%;
  max-width: 450px;
  background-color: var(--color-white);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  padding: 40px;
  position: relative;
  overflow: hidden;
  animation: fadeIn 0.8s ease-out;
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background: linear-gradient(to right, var(--color-primary), var(--color-primary-dark));
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: var(--color-accent);
  font-family: var(--font-heading);
  font-size: var(--font-size-2xl);
  position: relative;
  display: inline-block;
  width: 100%;
}

h2::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 50px;
  height: 2px;
  background-color: var(--color-primary);
}

.form-group {
  margin-bottom: 24px;
  position: relative;
}

label {
  display: block;
  margin-bottom: 8px;
  font-size: var(--font-size-sm);
  color: var(--color-text);
  font-family: var(--font-body);
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid var(--color-secondary);
  border-radius: 8px;
  font-size: var(--font-size-base);
  font-family: var(--font-body);
  color: var(--color-text);
  background-color: var(--color-white);
  transition: all var(--transition-fast);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(163, 141, 119, 0.2);
}

.password-input-wrapper {
  position: relative;
}

.toggle-password {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--color-text-light);
  transition: color var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
}

.toggle-password:hover {
  color: var(--color-primary);
  background-color: var(--color-secondary);
}

.remember-forgot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-size: var(--font-size-sm);
}

.remember-me {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.remember-me input {
  margin-right: 8px;
  accent-color: var(--color-primary);
}

.forgot-password {
  color: var(--color-primary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.forgot-password:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

.login-btn {
  width: 100%;
  padding: 14px;
  background-color: var(--color-primary);
  color: var(--color-white);
  border: none;
  border-radius: 8px;
  font-size: var(--font-size-base);
  font-weight: 600;
  font-family: var(--font-body);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.3) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  transition: left 0.6s;
}

.login-btn:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.login-btn:hover::before {
  left: 100%;
}

.login-btn:active:not(:disabled) {
  transform: translateY(-1px);
}

.login-btn.loading {
  background-color: var(--color-secondary);
  cursor: not-allowed;
}

.login-btn:disabled {
  background-color: var(--color-secondary);
  color: var(--color-text-light);
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: var(--color-white);
  animation: spin 0.8s linear infinite;
  margin-right: 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  color: var(--color-error);
  font-size: var(--font-size-sm);
  margin-bottom: 16px;
  padding: 10px;
  background-color: rgba(214, 48, 49, 0.1);
  border-radius: 4px;
  text-align: center;
}

.divider {
  position: relative;
  margin: 30px 0;
  text-align: center;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  width: 100%;
  height: 1px;
  background-color: var(--color-secondary);
}

.divider span {
  position: relative;
  background-color: var(--color-white);
  padding: 0 15px;
  color: var(--color-text-light);
  font-size: var(--font-size-sm);
}

.social-login {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 25px;
}

.social-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 15px;
  border-radius: 8px;
  font-size: var(--font-size-base);
  font-family: var(--font-body);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.google-btn {
  background-color: var(--color-white);
  color: var(--color-text);
  border: 1px solid var(--color-secondary);
}

.google-btn:hover {
  background-color: #f5f5f5;
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.kakao-btn {
  background-color: #FEE500;
  color: #000000;
  border: 1px solid #FEE500;
}

.kakao-btn:hover {
  background-color: #FDD800;
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.social-btn img {
  height: 22px;
  width: 22px;
  object-fit: contain;
}

.register-link {
  margin-top: 25px;
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--color-text);
  font-family: var(--font-body);
}

.register-link a {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
  transition: all var(--transition-fast);
  margin-left: 5px;
}

.register-link a:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

/* 다크 모드 추가 스타일 */
:global(.dark-mode) .login-card {
  background-color: #2D2D2D;
}

:global(.dark-mode) .divider span {
  background-color: #2D2D2D;
}

:global(.dark-mode) .google-btn {
  background-color: #333333;
  color: #E0E0E0;
  border-color: #444444;
}

:global(.dark-mode) .google-btn:hover {
  background-color: #3D3D3D;
}

/* 반응형 스타일 */
@media (max-width: 576px) {
  .login-card {
    padding: 30px 20px;
  }
  
  h2 {
    font-size: var(--font-size-xl);
  }
  
  .form-input {
    padding: 12px 14px;
  }
  
  .login-btn {
    padding: 12px;
  }
  
  .remember-forgot {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
