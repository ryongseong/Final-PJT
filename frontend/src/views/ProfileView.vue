<!-- src/views/ProfileView.vue -->
<template>
  <div class="profile-container">
    <div class="profile-card">
      <h2>프로필 관리</h2>
      
      <div class="profile-header">
        <div class="profile-avatar">
          <img 
            v-if="profileImage" 
            :src="profileImage" 
            alt="프로필 이미지"
            @click="triggerImageUpload"
            @error="handleImageError"
            class="profile-image"
          />
          <div v-else class="avatar-placeholder" @click="triggerImageUpload">
            {{ userInitials }}
          </div>
          <input 
            type="file" 
            ref="fileInput" 
            style="display: none" 
            @change="handleImageChange" 
            accept="image/*"
          />
          <div class="avatar-edit-hint">클릭하여 변경</div>
          <button 
            v-if="user?.profile_img"
            @click.prevent="resetProfileImage" 
            class="reset-image-btn"
            title="기본 이미지로 변경"
          >
            <span>초기화</span>
          </button>
        </div>
        <div class="profile-info">
          <h3>{{ user?.nickname || user?.username }}</h3>
          <p>{{ user?.email }}</p>
        </div>
      </div>
      
      <form @submit.prevent="updateProfile">
        <div class="form-group">
          <label for="nickname">닉네임</label>
          <input 
            type="text" 
            id="nickname" 
            v-model="profileForm.nickname" 
            placeholder="닉네임" 
          />
        </div>
        
        <div class="form-row">
          <div class="form-group half">
            <label for="age">나이</label>
            <input 
              type="number" 
              id="age" 
              v-model="profileForm.age" 
              placeholder="나이"
            />
          </div>
          
          <div class="form-group half">
            <label for="gender">성별</label>
            <select id="gender" v-model="profileForm.gender">
              <option value="">선택 안함</option>
              <option value="M">남성</option>
              <option value="F">여성</option>
            </select>
          </div>
        </div>
        
        <div class="form-group">
          <label for="salary">월 소득 (원)</label>
          <input 
            type="number" 
            id="salary" 
            v-model="profileForm.salary" 
            placeholder="월 소득" 
          />
        </div>
        
        <div class="form-group">
          <label for="money">계좌 잔액 (원)</label>
          <input 
            type="number" 
            id="money" 
            v-model="profileForm.money" 
            placeholder="계좌 잔액" 
          />
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">{{ success }}</div>
        
        <button type="submit" class="update-btn" :disabled="loading">
          {{ loading ? '업데이트 중...' : '프로필 업데이트' }}
        </button>
      </form>
      
      <div class="account-info">
        <h3>계정 정보</h3>
        <div class="info-item">
          <span>아이디:</span>
          <span>{{ user?.username }}</span>
        </div>
        <div class="info-item">
          <span>가입일:</span>
          <span>{{ formattedJoinDate }}</span>
        </div>
        <div class="info-item">
          <span>계좌 잔액:</span>
          <span>{{ formatCurrency(user?.money) }}</span>
        </div>
      </div>
      
      <button @click="logout" class="logout-btn">로그아웃</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import * as imageUtils from '@/utils/imageUtils'
import { getAbsoluteImageUrl } from '@/utils/imageUtils'

const userStore = useUserStore()

const user = computed(() => userStore.user)
const userInitials = computed(() => userStore.userInitials)
const profileImage = computed(() => {
  if (imagePreview.value) return imagePreview.value

  
  // Get the profile image URL
  const imgUrl = user.value?.profile_img || user.value?.social_avatar || null
  console.log('Profile image URL from user object:', imgUrl)
  
  // If there's an image URL, add a timestamp to prevent caching
  if (imgUrl) {
    // Use our utility function to get the absolute URL with cache busting
    const absoluteUrl = getAbsoluteImageUrl(imgUrl)
    console.log('Absolute profile image URL:', absoluteUrl)
    return absoluteUrl
  }
  
  return null
})

const profileForm = reactive({
  nickname: '',
  age: '',
  gender: '',
  salary: '',
  money: '',  // Add money field
})

const fileInput = ref(null)
const loading = ref(false)
const error = ref(null)
const success = ref(null)
const imagePreview = ref(null)
const imageFile = ref(null)

onMounted(async () => {
  loading.value = true
  try {
    await userStore.fetchUserProfile()
    
    // Initialize form with user data
    profileForm.nickname = user.value?.nickname || ''
    profileForm.age = user.value?.age || ''
    profileForm.gender = user.value?.gender || ''
    profileForm.salary = user.value?.salary || ''
    profileForm.money = user.value?.money || ''  // Initialize money field
  } catch (error) {
    error.value = '프로필을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
})

const formatCurrency = (amount) => {
  if (amount === undefined || amount === null) return '0원'
  return new Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW' }).format(amount)
}

const formattedJoinDate = computed(() => {
  if (!user.value?.join_date) return '정보 없음'
  return new Date(user.value.join_date).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const triggerImageUpload = () => {
  fileInput.value.click()
}

const handleImageChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // Preview the image
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)
  
  // Store the file for form submission
  imageFile.value = file
}

const updateProfile = async () => {
  error.value = null
  success.value = null
  
  // Validate money field
  if (profileForm.money !== '' && isNaN(Number(profileForm.money))) {
    error.value = '계좌 잔액은 숫자여야 합니다.'
    return
  }
  
  loading.value = true
  try {
    // Create form data for file upload
    const formData = new FormData()
    
    // Always output what we're sending for debugging
    console.log('Updating profile with image:', imageFile.value)
    
    // If there's a new image, add it to formData
    if (imageFile.value) {
      console.log('Adding profile image to form data:', imageFile.value.name)
      formData.append('profile_img', imageFile.value)
    }
    
    // Only append changed fields
    if (profileForm.nickname && profileForm.nickname !== user.value?.nickname) {
      formData.append('nickname', profileForm.nickname)
    }
    
    if (profileForm.age !== user.value?.age) {
      formData.append('age', profileForm.age)
    }
    
    if (profileForm.gender !== user.value?.gender) {
      formData.append('gender', profileForm.gender)
    }
    
    if (profileForm.salary !== user.value?.salary) {
      formData.append('salary', profileForm.salary)
    }
    
    if (profileForm.money !== user.value?.money) {
      formData.append('money', profileForm.money)
    }
    
    // Send update request with formData
    const response = await userStore.updateProfile(formData)
    console.log('Profile update response:', response)
    
    // If we got a successful response, explicitly fetch fresh user data
    await userStore.fetchUserProfile()
    
    success.value = '프로필이 성공적으로 업데이트되었습니다.'
    
    // Reset file input and preview
    if (fileInput.value) {
      fileInput.value.value = null
    }
    imageFile.value = null
    imagePreview.value = null
  } catch (err) {
    console.error('Profile update error:', err)
    error.value = err.error || '프로필 업데이트에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

const logout = () => {
  userStore.logout()
}

const resetProfileImage = async () => {
  if (!confirm('프로필 이미지를 기본 이미지로 초기화하시겠습니까?')) {
    return
  }
  
  error.value = null
  success.value = null
  loading.value = true
  
  try {
    await userStore.resetProfileImage()
    
    // Reset preview if it exists
    imagePreview.value = null
    imageFile.value = null
    
    // Refresh user data to update UI
    await userStore.fetchUserProfile()
    
    success.value = '프로필 이미지가 초기화되었습니다.'
  } catch (err) {
    console.error('Profile image reset error:', err)
    error.value = err.error || '프로필 이미지 초기화에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

const handleImageError = (e) => {
  console.error('Error loading profile image:', e)
  // If the image fails to load, try alternative approaches
  const imgElement = e.target
  console.log('Image that failed to load:', imgElement.src)
  
  // Use the fallback URL generator function
  const fallbackUrl = imageUtils.generateFallbackImageUrl(imgElement.src)
  
  // Try with another approach - get a fallback URL
  const imgUrl = user.value?.profile_img || user.value?.social_avatar
  if (imgUrl) {
    if (fallbackUrl && fallbackUrl !== imgElement.src) {
      console.log('Retrying with fallback URL:', fallbackUrl)
      imgElement.src = fallbackUrl
    } else {
      // If we've already tried the fallback, try a direct URL
      if (imgUrl.startsWith('/media')) {
        imgElement.src = `http://localhost:8000${imgUrl}`
        console.log('Retrying with direct URL:', imgElement.src)
      } else if (imgUrl.includes('?')) {
        imgElement.src = imgUrl.split('?')[0]
        console.log('Retrying without cache busting:', imgElement.src)
      }
    }
  } else {
    // If all else fails, remove the image
    imagePreview.value = null
  }
}
</script>

<style scoped>
.profile-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 40px 20px;
}

.profile-card {
  width: 100%;
  max-width: 600px;
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

.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.profile-avatar {
  position: relative;
  margin-right: 20px;
}

.profile-avatar img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  cursor: pointer;
  border: 3px solid #4f46e5;
}

.avatar-placeholder {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background-color: #4f46e5;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 36px;
  cursor: pointer;
  border: 3px solid #4f46e5;
}

.avatar-edit-hint {
  position: absolute;
  bottom: -20px;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 12px;
  color: #666;
}

.reset-image-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
  opacity: 0.8;
  transition: opacity 0.2s, transform 0.2s;
}

.reset-image-btn:hover {
  opacity: 1;
  transform: scale(1.05);
}

.profile-info {
  flex: 1;
}

.profile-info h3 {
  margin: 0 0 5px;
  color: #333;
}

.profile-info p {
  margin: 0;
  color: #666;
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

.update-btn {
  width: 100%;
  padding: 12px;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-bottom: 30px;
}

.update-btn:hover {
  background-color: #4338ca;
}

.update-btn:disabled {
  background-color: #a5a5a5;
  cursor: not-allowed;
}

.account-info {
  border-top: 1px solid #ddd;
  padding-top: 20px;
  margin-bottom: 30px;
}

.account-info h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
}

.info-item span:first-child {
  color: #666;
}

.info-item span:last-child {
  font-weight: 500;
  color: #333;
}

.error-message {
  color: #e53e3e;
  font-size: 14px;
  margin-bottom: 16px;
}

.success-message {
  color: #38a169;
  font-size: 14px;
  margin-bottom: 16px;
}

.logout-btn {
  width: 100%;
  padding: 12px;
  background-color: #f3f4f6;
  color: #4b5563;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.logout-btn:hover {
  background-color: #e5e7eb;
}
</style>
