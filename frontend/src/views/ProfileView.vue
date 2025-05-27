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
  age: 0,
  gender: '',
  salary: 0,
  money: 0,  // Add money field
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
  align-items: flex-start; /* Align card to the top */
  min-height: 100vh;
  background-color: var(--background-primary); /* Themed background */
  padding: 2rem; /* Consistent padding */
  font-family: var(--font-family-base);
}

.profile-card {
  width: 100%;
  max-width: 650px; /* Wider for more content */
  background-color: var(--card-bg);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
  padding: 2.5rem; /* Increased padding */
}

.profile-card h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--text-primary);
  font-family: 'Pretendard Variable', serif;
  font-size: 2rem;
  font-weight: 700;
}

.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 2.5rem; /* Increased margin */
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.profile-avatar {
  position: relative;
  margin-right: 1.5rem;
}

.profile-image, .avatar-placeholder {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  cursor: pointer;
  border: 3px solid var(--accent-color); /* Accent border */
  transition: opacity 0.3s ease;
}

.profile-image:hover, .avatar-placeholder:hover {
  opacity: 0.8;
}

.avatar-placeholder {
  background-color: var(--accent-color);
  color: var(--button-text);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2.5rem; /* Larger initials */
  font-weight: 600;
}

.avatar-edit-hint {
  position: absolute;
  bottom: -20px; /* Adjusted position */
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.8rem;
  color: var(--text-secondary);
  background-color: rgba(var(--card-bg-rgb), 0.8);
  padding: 2px 6px;
  border-radius: var(--border-radius-sm);
  white-space: nowrap;
}

.reset-image-btn {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: var(--error-color, #ef4444);
  color: white;
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  font-size: 0.8rem;
  cursor: pointer;
  opacity: 0.9;
  transition: opacity 0.2s, transform 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.reset-image-btn:hover {
  opacity: 1;
  transform: scale(1.1);
}

.reset-image-btn span {
  font-size: 0.7rem; /* Adjust if text is too large */
}

.profile-info {
  flex: 1;
}

.profile-info h3 {
  margin: 0 0 0.5rem;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-family: 'Pretendard Variable', serif;
}

.profile-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-group.half {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 0.6rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.form-group input, .form-group select {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: 1rem;
  background-color: var(--background-primary);
  color: var(--text-primary);
  transition: border-color var(--transition-speed), box-shadow var(--transition-speed);
}

.form-group input::placeholder {
  color: var(--text-secondary);
  opacity: 0.7;
}

.form-group input:focus, .form-group select:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(var(--accent-color-rgb, 163, 184, 153), 0.2); /* Adjusted shadow */
}

.error-message, .success-message {
  padding: 0.8rem 1rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  text-align: center;
}

.error-message {
  color: var(--error-text, #ef4444);
  background-color: var(--error-bg, rgba(239, 68, 68, 0.1));
  border: 1px solid var(--error-border, rgba(239, 68, 68, 0.2));
}

.success-message {
  color: var(--success-text, #38a169);
  background-color: var(--success-bg, rgba(56, 161, 105, 0.1));
  border: 1px solid var(--success-border, rgba(56, 161, 105, 0.2));
}

.update-btn, .logout-btn {
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

.update-btn {
  background-color: var(--accent-color);
  color: var(--button-text);
  border-color: var(--accent-color);
  margin-bottom: 1.5rem; /* Spacing before account info */
}

.update-btn:hover:not(:disabled) {
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.update-btn:disabled {
  background-color: var(--accent-color);
  opacity: 0.6;
  cursor: not-allowed;
}

.account-info {
  border-top: 1px solid var(--border-color);
  padding-top: 1.5rem;
  margin-bottom: 1.5rem;
}

.account-info h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-family: 'Pretendard Variable', serif;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.8rem;
  font-size: 0.95rem;
}

.info-item span:first-child {
  color: var(--text-secondary);
  font-weight: 500;
}

.info-item span:last-child {
  color: var(--text-primary);
}

.logout-btn {
  background-color: var(--card-bg);
  color: var(--error-text, #ef4444);
  border-color: var(--error-border, rgba(239, 68, 68, 0.3));
}

.logout-btn:hover {
  background-color: var(--error-bg, rgba(239, 68, 68, 0.1));
  border-color: var(--error-text, #ef4444);
}

@media (max-width: 768px) {
  .profile-card {
    padding: 2rem 1.5rem;
  }
  .profile-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  .profile-avatar {
    margin-right: 0;
    margin-bottom: 1rem;
  }
  .avatar-edit-hint {
    bottom: -15px;
  }
  .form-row {
    flex-direction: column;
    gap: 0; /* Remove gap for stacked elements */
  }
  .form-group.half {
    margin-bottom: 1.5rem; /* Ensure spacing when stacked */
  }
  .form-group.half:last-child {
    margin-bottom: 0; /* Remove bottom margin for the last stacked item */
  }
}
</style>
