<template>
  <div>
    <!-- 플로팅 버튼 - 페이지 하단에 고정 -->
    <button @click="togglePhishingModal" class="phishing-button" :class="{ 'dark': isDarkMode }">
      <span class="icon">⚠️</span>
      <span class="text">{{ $t('phishing.title') }}</span>
    </button>
    
    <!-- 피싱 경고 모달 - 하단에 표시 -->
    <div v-if="showPhishingModal" class="phishing-modal phishing-modal-bottom" @keyup.esc="closePhishingModal">
      <div class="phishing-modal-content" :class="{ 'dark': isDarkMode }">
        <button class="close-button" @click="closePhishingModal">&times;</button>
        <h3>⚠️ {{ $t('phishing.title') }}</h3>
        <p>📢 {{ $t('phishing.content') }}</p>
        <p class="report-number">{{ $t('phishing.reportNumber') }}</p>
        <div class="phishing-modal-footer">
          <label class="checkbox-container">
            <input type="checkbox" v-model="doNotShowToday" />
            <span class="checkbox-text">{{ $t('phishing.dontShowToday') }}</span>
          </label>
          <button class="btn-primary" @click="closePhishingModal">
            {{ $t('phishing.closeButton') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useI18n } from 'vue-i18n'

const showPhishingModal = ref(true) // 기본값을 true로 변경하여 자동으로 표시
const doNotShowToday = ref(false)
const settingsStore = useSettingsStore()
const { t } = useI18n()

const isDarkMode = computed(() => settingsStore.isDarkMode)

onMounted(() => {
  // 저장된 설정 확인
  const lastShown = localStorage.getItem('phishingModalLastShown')
  const today = new Date().toDateString()
  
  // 오늘 하루 보지 않기를 선택했는지 확인
  if (lastShown === today) {
    showPhishingModal.value = false
  } else {
    // 첫 페이지 로드 시 모달 표시
    showPhishingModal.value = true
  }

  // ESC 키 이벤트 등록
  document.addEventListener('keydown', handleKeyDown)
  
  // 언어 변경 이벤트 리스너 추가
  window.addEventListener('languageChanged', updateModalContent)
})

function handleKeyDown(event) {
  if (event.key === 'Escape' && showPhishingModal.value) {
    closePhishingModal()
  }
}

function togglePhishingModal() {
  showPhishingModal.value = true
}

function closePhishingModal() {
  showPhishingModal.value = false

  if (doNotShowToday.value) {
    const today = new Date().toDateString()
    localStorage.setItem('phishingModalLastShown', today)
  }
}

// 언어 변경 시 모달 내용 업데이트
function updateModalContent() {
  // 모달이 열려있을 때만 업데이트 필요
  if (showPhishingModal.value) {
    // 필요한 경우 여기에 추가 로직 구현
    console.log('언어가 변경되어 모달 내용 업데이트됨')
  }
}

// 컴포넌트 언마운트 시 이벤트 리스너 제거
onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('languageChanged', updateModalContent)
})
</script>

<style scoped>
.phishing-button {
  position: fixed;
  bottom: 30px;
  right: 30px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: var(--card-bg);
  color: var(--text-primary);
  border: none;
  border-radius: 50px;
  box-shadow: 0 4px 15px var(--shadow-color);
  cursor: pointer;
  z-index: 1000;
  transition: all 0.3s;
}

.phishing-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px var(--shadow-color);
}

.phishing-button .icon {
  font-size: 1.2rem;
}

.phishing-button .text {
  font-weight: 600;
}

.phishing-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(3px);
}

.phishing-modal-bottom {
  align-items: flex-end;
  padding-bottom: 20px;
}

.phishing-modal-content {
  background-color: var(--card-bg);
  border-radius: 16px;
  box-shadow: 0 12px 40px var(--shadow-color);
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  border: 1px solid var(--border-color);
  position: relative;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.close-button {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.phishing-modal-content h3 {
  color: #d97706;
  margin-bottom: 1rem;
  font-size: 1.5rem;
  font-family: 'Playfair Display', serif;
}

.phishing-modal-content p {
  color: var(--text-primary);
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  line-height: 1.6;
}

.report-number {
  font-weight: 700;
  color: #d97706;
  text-align: center;
  padding: 10px;
  border-radius: 8px;
  background-color: rgba(217, 119, 6, 0.1);
  margin-top: 0;
}

.phishing-modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
}

.checkbox-container {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: var(--text-secondary);
}

.checkbox-container input {
  margin-right: 0.5rem;
}

.btn-primary {
  background: var(--accent-color);
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  opacity: 0.9;
}

@media (max-width: 480px) {
  .phishing-modal-footer {
    flex-direction: column;
    gap: 15px;
  }
  
  .btn-primary {
    width: 100%;
  }
  
  .phishing-button {
    bottom: 20px;
    right: 20px;
    padding: 10px 14px;
  }
}
</style>
