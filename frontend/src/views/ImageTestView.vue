<template>
  <div class="image-test-container">
    <h1>프로필 이미지 디버깅</h1>
    
    <div class="test-section">
      <h2>직접 링크 테스트</h2>
      <div class="image-container">
        <img 
          :src="directImageUrl" 
          alt="직접 링크" 
          @error="handleImageError($event, 'direct')"
        />
        <div>URL: {{ directImageUrl }}</div>
      </div>
    </div>
    
    <div class="test-section">
      <h2>캐시버스팅 링크 테스트</h2>
      <div class="image-container">
        <img 
          :src="cacheBustedUrl" 
          alt="캐시버스팅 링크" 
          @error="handleImageError($event, 'cacheBusted')"
        />
        <div>URL: {{ cacheBustedUrl }}</div>
      </div>
    </div>
    
    <div class="test-section">
      <h2>폴백 링크 테스트</h2>
      <div class="image-container">
        <img 
          :src="fallbackUrl" 
          alt="폴백 링크" 
          @error="handleImageError($event, 'fallback')"
        />
        <div>URL: {{ fallbackUrl }}</div>
      </div>
    </div>
    
    <div class="test-section">
      <h2>유틸리티 함수 테스트</h2>
      <div class="image-container">
        <img 
          :src="utilityProcessedUrl" 
          alt="유틸리티 처리 링크" 
          @error="handleImageError($event, 'utility')"
        />
        <div>URL: {{ utilityProcessedUrl }}</div>
      </div>
    </div>
    
    <button @click="refreshUrls" class="refresh-btn">URL 새로고침</button>
    
    <div v-if="error" class="error-message">
      <h3>에러 로그</h3>
      <pre>{{ error }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as imageUtils from '@/utils/imageUtils'

// Example image path - we'll use a known profile image
const imagePath = '/media/profile_images/스크린샷_2025-05-22_093253.png'
const baseUrl = 'http://localhost:8000'

const directImageUrl = ref('')
const cacheBustedUrl = ref('')
const fallbackUrl = ref('')
const utilityProcessedUrl = ref('')
const error = ref(null)

// Generate URLs with different approaches
const refreshUrls = () => {
  // Direct URL
  directImageUrl.value = `${baseUrl}${imagePath}`
  
  // Cache-busted URL
  const timestamp = new Date().getTime()
  cacheBustedUrl.value = `${baseUrl}${imagePath}?t=${timestamp}`
  
  // Fallback URL (similar to what our error handler would generate)
  fallbackUrl.value = imageUtils.generateFallbackImageUrl(imagePath)
  
  // URL processed by our utility function
  utilityProcessedUrl.value = imageUtils.getAbsoluteImageUrl(imagePath)
  
  console.log('URLs refreshed:', {
    direct: directImageUrl.value,
    cacheBusted: cacheBustedUrl.value,
    fallback: fallbackUrl.value,
    utility: utilityProcessedUrl.value
  })
}

// Handle image errors
const handleImageError = (e, type) => {
  console.error(`Error loading ${type} image:`, e)
  error.value = `이미지 로딩 실패 (${type}): ${e.target.src}`
  
  // Try with alternative URL
  const fallback = imageUtils.generateFallbackImageUrl(e.target.src)
  if (fallback && fallback !== e.target.src) {
    console.log(`Retrying ${type} image with fallback:`, fallback)
    e.target.src = fallback
  }
}

onMounted(() => {
  refreshUrls()
})
</script>

<style scoped>
.image-test-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.test-section {
  margin-bottom: 30px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.image-container {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.image-container img {
  max-width: 200px;
  max-height: 200px;
  border: 2px solid #4f46e5;
  border-radius: 8px;
  margin-bottom: 10px;
}

.refresh-btn {
  display: block;
  margin: 20px auto;
  padding: 10px 20px;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-btn:hover {
  background-color: #4338ca;
}

.error-message {
  margin-top: 20px;
  padding: 15px;
  background-color: #fee2e2;
  border: 1px solid #ef4444;
  border-radius: 8px;
}

.error-message pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: monospace;
}
</style>
