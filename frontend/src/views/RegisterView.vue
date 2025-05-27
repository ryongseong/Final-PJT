<!-- src/views/RegisterView.vue -->
<template>
  <div class="register-container">
    <div class="register-card">
      <h2>회원가입</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">아이디</label>
          <input 
            type="text" 
            id="username" 
            v-model="registerForm.username" 
            placeholder="사용할 아이디"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="email">이메일</label>
          <input 
            type="email" 
            id="email" 
            v-model="registerForm.email" 
            placeholder="이메일 주소"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="nickname">닉네임</label>
          <input 
            type="text" 
            id="nickname" 
            v-model="registerForm.nickname" 
            placeholder="사용할 닉네임"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password">비밀번호</label>
          <input 
            type="password" 
            id="password" 
            v-model="registerForm.password" 
            placeholder="비밀번호"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="passwordConfirm">비밀번호 확인</label>
          <input 
            type="password" 
            id="passwordConfirm" 
            v-model="registerForm.passwordConfirm" 
            placeholder="비밀번호 확인"
            required
            :class="{ 'input-error': passwordMismatch }"
          />
          <p v-if="passwordMismatch" class="error-message">비밀번호가 일치하지 않습니다.</p>
        </div>
        
        <div class="form-row">
          <div class="form-group half">
            <label for="age">나이</label>
            <input 
              type="number" 
              id="age" 
              v-model="registerForm.age" 
              placeholder="나이"
            />
          </div>
          
          <div class="form-group half">
            <label for="gender">성별</label>
            <select id="gender" v-model="registerForm.gender">
              <option value="">선택 안함</option>
              <option value="M">남성</option>
              <option value="F">여성</option>
            </select>
          </div>
        </div>

        <p v-if="error" class="error-message">{{ error }}</p>
        
        <button type="submit" class="register-btn" :disabled="loading || passwordMismatch">
          {{ loading ? '처리 중...' : '회원가입' }}
        </button>
      </form>
      
      <div class="login-link">
        이미 계정이 있으신가요? <router-link to="/login">로그인</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  passwordConfirm: '',
  nickname: '',
  age: '',
  gender: ''
})

const loading = ref(false)
const error = ref(null)

const passwordMismatch = computed(() => {
  return (registerForm.password || registerForm.passwordConfirm) && 
         registerForm.password !== registerForm.passwordConfirm
})

const handleRegister = async () => {
  // Validation
  if (passwordMismatch.value) {
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
    error.value = err.error || '회원가입에 실패했습니다. 입력 내용을 확인해주세요.'
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
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 480px;
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

.form-row {
  display: flex;
  gap: 15px;
}

.half {
  flex: 1;
}

label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #555;
}

input, select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

input.input-error {
  border-color: #e53e3e;
}

.register-btn {
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

.register-btn:hover {
  background-color: #4338ca;
}

.register-btn:disabled {
  background-color: #a5a5a5;
  cursor: not-allowed;
}

.error-message {
  color: #e53e3e;
  font-size: 14px;
  margin-top: 5px;
  margin-bottom: 16px;
}

.login-link {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.login-link a {
  color: #4f46e5;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
