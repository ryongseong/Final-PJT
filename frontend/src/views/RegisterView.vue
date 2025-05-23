<!-- src/views/RegisterView.vue -->
<template>
  <div class="register-container">
    <div class="register-card">
      <h2>{{ currentLanguage === 'ko' ? '회원가입' : 'Sign Up' }}</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">{{ currentLanguage === 'ko' ? '아이디' : 'Username' }}</label>
          <input 
            type="text" 
            id="username" 
            v-model="registerForm.username" 
            :placeholder="currentLanguage === 'ko' ? '사용할 아이디' : 'Choose a username'"
            required
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label for="email">{{ currentLanguage === 'ko' ? '이메일' : 'Email' }}</label>
          <input 
            type="email" 
            id="email" 
            v-model="registerForm.email" 
            :placeholder="currentLanguage === 'ko' ? '이메일 주소' : 'Email address'"
            required
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label for="nickname">{{ currentLanguage === 'ko' ? '닉네임' : 'Nickname' }}</label>
          <input 
            type="text" 
            id="nickname" 
            v-model="registerForm.nickname" 
            :placeholder="currentLanguage === 'ko' ? '사용할 닉네임' : 'Choose a nickname'"
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
              v-model="registerForm.password" 
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
          <div class="password-strength" v-if="registerForm.password">
            <div class="strength-bar">
              <div 
                class="strength-progress" 
                :style="{ width: `${passwordStrength}%` }"
                :class="getPasswordStrengthClass()"
              ></div>
            </div>
            <span class="strength-text" :class="getPasswordStrengthClass()">
              {{ getPasswordStrengthText() }}
            </span>
          </div>
        </div>
        
        <div class="form-group">
          <label for="passwordConfirm">{{ currentLanguage === 'ko' ? '비밀번호 확인' : 'Confirm Password' }}</label>
          <div class="password-input-wrapper">
            <input 
              :type="showPasswordConfirm ? 'text' : 'password'" 
              id="passwordConfirm" 
              v-model="registerForm.passwordConfirm" 
              :placeholder="currentLanguage === 'ko' ? '비밀번호 확인' : 'Confirm password'"
              required
              class="form-input"
              :class="{ 'input-error': passwordMismatch && registerForm.passwordConfirm }"
            />
            <button 
              type="button" 
              class="toggle-password" 
              @click="showPasswordConfirm = !showPasswordConfirm"
            >
              {{ showPasswordConfirm ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
          <p v-if="passwordMismatch && registerForm.passwordConfirm" class="field-error">
            {{ currentLanguage === 'ko' ? '비밀번호가 일치하지 않습니다.' : 'Passwords do not match.' }}
          </p>
        </div>
        
        <div class="form-row">
          <div class="form-group half">
            <label for="age">{{ currentLanguage === 'ko' ? '나이' : 'Age' }}</label>
            <input 
              type="number" 
              id="age" 
              v-model="registerForm.age" 
              :placeholder="currentLanguage === 'ko' ? '나이' : 'Age'"
              class="form-input"
              min="1"
              max="120"
            />
          </div>
          
          <div class="form-group half">
            <label for="gender">{{ currentLanguage === 'ko' ? '성별' : 'Gender' }}</label>
            <select id="gender" v-model="registerForm.gender" class="form-input">
              <option value="">{{ currentLanguage === 'ko' ? '선택 안함' : 'Not specified' }}</option>
              <option value="M">{{ currentLanguage === 'ko' ? '남성' : 'Male' }}</option>
              <option value="F">{{ currentLanguage === 'ko' ? '여성' : 'Female' }}</option>
            </select>
          </div>
        </div>

        <div class="terms-agreement">
          <label class="checkbox-container">
            <input type="checkbox" v-model="agreeTerms" required>
            <span class="checkmark"></span>
            <span>
              {{ currentLanguage === 'ko' ? '이용약관 및 개인정보 처리방침에 동의합니다.' : 'I agree to the Terms of Service and Privacy Policy.' }}
              <a href="#" class="terms-link">{{ currentLanguage === 'ko' ? '자세히 보기' : 'Read more' }}</a>
            </span>
          </label>
        </div>

        <p v-if="error" class="error-message">{{ error }}</p>
        
        <button 
          type="submit" 
          class="register-btn" 
          :disabled="loading || passwordMismatch || !agreeTerms"
          :class="{ 'loading': loading }"
        >
          <span v-if="loading" class="spinner"></span>
          {{ loading 
            ? (currentLanguage === 'ko' ? '처리 중...' : 'Processing...') 
            : (currentLanguage === 'ko' ? '회원가입' : 'Sign Up') }}
        </button>
      </form>
      
      <div class="login-link">
        {{ currentLanguage === 'ko' ? '이미 계정이 있으신가요?' : 'Already have an account?' }} 
        <router-link to="/login">{{ currentLanguage === 'ko' ? '로그인' : 'Log in' }}</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

// 언어 설정 관련
const currentLanguage = ref('ko')

// 회원가입 폼
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  passwordConfirm: '',
  nickname: '',
  age: '',
  gender: ''
})

// 상태 관리
const loading = ref(false)
const error = ref(null)
const showPassword = ref(false)
const showPasswordConfirm = ref(false)
const agreeTerms = ref(false)

// 비밀번호 불일치 체크
const passwordMismatch = computed(() => {
  return (registerForm.password || registerForm.passwordConfirm) && 
         registerForm.password !== registerForm.passwordConfirm
})

// 비밀번호 강도 측정 (0-100)
const passwordStrength = computed(() => {
  if (!registerForm.password) return 0
  
  let strength = 0
  const password = registerForm.password
  
  // 길이 체크 (최대 40점)
  const lengthScore = Math.min(password.length * 4, 40)
  strength += lengthScore
  
  // 문자 다양성 체크 (최대 60점)
  if (/[0-9]/.test(password)) strength += 15 // 숫자
  if (/[a-z]/.test(password)) strength += 15 // 소문자
  if (/[A-Z]/.test(password)) strength += 15 // 대문자
  if (/[^a-zA-Z0-9]/.test(password)) strength += 15 // 특수문자
  
  return Math.min(strength, 100)
})

// 비밀번호 강도 클래스 반환
const getPasswordStrengthClass = () => {
  const strength = passwordStrength.value
  if (strength < 30) return 'weak'
  if (strength < 60) return 'medium'
  return 'strong'
}

// 비밀번호 강도 텍스트 반환
const getPasswordStrengthText = () => {
  const strength = passwordStrength.value
  
  if (currentLanguage.value === 'ko') {
    if (strength < 30) return '약함'
    if (strength < 60) return '보통'
    return '강함'
  } else {
    if (strength < 30) return 'Weak'
    if (strength < 60) return 'Medium'
    return 'Strong'
  }
}

// 컴포넌트 마운트 시 언어 설정 확인
onMounted(() => {
  const savedLanguage = localStorage.getItem('language')
  if (savedLanguage) {
    currentLanguage.value = savedLanguage
  }
})

const handleRegister = async () => {
  // Validation
  if (passwordMismatch.value) {
    return
  }
  
  if (!agreeTerms.value) {
    error.value = currentLanguage.value === 'ko' 
      ? '이용약관 및 개인정보 처리방침에 동의해주세요.' 
      : 'Please agree to the Terms of Service and Privacy Policy.'
    return
  }
  
  error.value = null
  loading.value = true
  
  try {
    await userStore.register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      nickname: registerForm.nickname,
      age: registerForm.age || null,
      gender: registerForm.gender || null
    })
    
    // Registration successful, redirect to home
    router.push('/')
  } catch (err) {
    error.value = err.error || (currentLanguage.value === 'ko' 
      ? '회원가입에 실패했습니다. 입력 내용을 확인해주세요.' 
      : 'Registration failed. Please check your information.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 160px); /* Account for header and footer */
  background: linear-gradient(135deg, var(--color-background-start) 0%, var(--color-background-end) 100%);
  padding: 40px 20px;
}

.register-card {
  width: 100%;
  max-width: 520px;
  background-color: var(--color-white);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  padding: 40px;
  position: relative;
  overflow: hidden;
  animation: fadeIn 0.8s ease-out;
}

.register-card::before {
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
  margin-bottom: 22px;
  position: relative;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 22px;
}

.half {
  flex: 1;
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

.form-input.input-error {
  border-color: var(--color-error);
  background-color: rgba(214, 48, 49, 0.05);
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

.password-strength {
  margin-top: 10px;
}

.strength-bar {
  height: 5px;
  background-color: var(--color-secondary);
  border-radius: 3px;
  margin-bottom: 5px;
  overflow: hidden;
}

.strength-progress {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.strength-progress.weak { background-color: #e74c3c; }
.strength-progress.medium { background-color: #f39c12; }
.strength-progress.strong { background-color: #27ae60; }

.strength-text {
  font-size: var(--font-size-xs);
  display: flex;
  justify-content: flex-end;
}

.strength-text.weak { color: #e74c3c; }
.strength-text.medium { color: #f39c12; }
.strength-text.strong { color: #27ae60; }

.field-error {
  color: var(--color-error);
  font-size: var(--font-size-xs);
  margin-top: 6px;
  margin-left: 2px;
}

.terms-agreement {
  margin-bottom: 25px;
}

.checkbox-container {
  display: flex;
  align-items: flex-start;
  position: relative;
  padding-left: 30px;
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-text);
  user-select: none;
}

.checkbox-container input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  position: absolute;
  top: 2px;
  left: 0;
  height: 20px;
  width: 20px;
  background-color: var(--color-white);
  border: 1px solid var(--color-secondary);
  border-radius: 4px;
  transition: all var(--transition-fast);
}

.checkbox-container:hover input ~ .checkmark {
  border-color: var(--color-primary);
}

.checkbox-container input:checked ~ .checkmark {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
}

.checkbox-container input:checked ~ .checkmark:after {
  display: block;
}

.checkbox-container .checkmark:after {
  left: 7px;
  top: 3px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.terms-link {
  color: var(--color-primary);
  margin-left: 5px;
  text-decoration: none;
  font-weight: 600;
  transition: color var(--transition-fast);
}

.terms-link:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
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

.register-btn {
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

.register-btn::before {
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

.register-btn:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.register-btn:hover::before {
  left: 100%;
}

.register-btn:active:not(:disabled) {
  transform: translateY(-1px);
}

.register-btn.loading {
  background-color: var(--color-secondary);
  cursor: not-allowed;
}

.register-btn:disabled {
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

.login-link {
  margin-top: 25px;
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--color-text);
  font-family: var(--font-body);
}

.login-link a {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
  transition: all var(--transition-fast);
  margin-left: 5px;
}

.login-link a:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

/* 다크 모드 추가 스타일 */
:global(.dark-mode) .register-card {
  background-color: #2D2D2D;
}

:global(.dark-mode) .form-input {
  background-color: #333333;
  border-color: #444444;
}

:global(.dark-mode) .checkmark {
  background-color: #333333;
  border-color: #444444;
}

/* 반응형 스타일 */
@media (max-width: 576px) {
  .register-card {
    padding: 30px 20px;
  }
  
  h2 {
    font-size: var(--font-size-xl);
  }
  
  .form-input {
    padding: 12px 14px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 15px;
  }
  
  .register-btn {
    padding: 12px;
  }
}
</style>
