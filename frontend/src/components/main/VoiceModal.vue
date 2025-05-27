<template>
  <div>
    <!-- 플로팅 버튼 - 페이지 하단에 고정 -->
    <button @click="togglePhishingModal" class="phishing-button" :class="{ dark: isDarkMode }">
      <span class="icon">⚠️</span>
      <span class="text">{{ $t('phishing.title') }}</span>
    </button>

    <!-- 피싱 경고 모달 - 하단에 표시 -->
    <div
      v-if="showPhishingModal"
      class="phishing-modal phishing-modal-bottom"
      @keyup.esc="closePhishingModal"
    >
      <div class="phishing-modal-content" :class="{ dark: isDarkMode }">
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
// import { useI18n } from 'vue-i18n' // 주석 처리 또는 삭제

const showPhishingModal = ref(true) // 기본값을 true로 변경하여 자동으로 표시
const doNotShowToday = ref(false)
const settingsStore = useSettingsStore()
// const { t } = useI18n() // 주석 처리 또는 삭제

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
  top: 0; left: 0; width: 100%; height: 100%;
  background-color: var(--overlay-bg, rgba(0, 0, 0, 0.6));
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
  padding: 1rem;
}

.phishing-modal-bottom {
  align-items: flex-end;
}

.phishing-modal-content {
  background-color: var(--modal-bg, var(--card-bg));
  border-radius: var(--modal-border-radius, var(--card-border-radius, 16px));
  box-shadow: var(--shadow-xl, 0 12px 40px rgba(0,0,0,0.25));
  padding: var(--spacing-xl, 2rem);
  max-width: 550px;
  width: 95%;
  border: 1px solid var(--modal-border, var(--border-color));
  position: relative;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  font-family: var(--font-body);
}

.close-button {
  position: absolute;
  top: var(--spacing-md, 1rem);
  right: var(--spacing-md, 1rem);
  background: none;
  border: none;
  font-size: var(--icon-size-xl, 1.8rem);
  color: var(--text-secondary);
  cursor: pointer;
  padding: var(--spacing-xs, 0.3rem);
  border-radius: 50%;
  transition: color var(--transition-speed), background-color var(--transition-speed);
  line-height: 1;
}

.close-button:hover {
  color: var(--text-primary);
  background-color: var(--button-hover-bg-light, rgba(0, 0, 0, 0.08));
}

.phishing-modal-content h3 {
  color: var(--warning-color-text, #d97706);
  margin-bottom: var(--spacing-lg, 1.25rem);
  font-size: var(--font-size-xxl, 1.6rem);
  font-family: var(--font-heading, 'Pretendard Variable', serif);
  font-weight: 700;
}

.phishing-modal-content p {
  color: var(--text-primary);
  margin-bottom: var(--spacing-lg, 1.25rem);
  font-size: var(--font-size-md-lg, 1.05rem);
  line-height: 1.7;
}

.report-number {
  font-weight: 700;
  color: var(--warning-color-text, #d97706);
  text-align: center;
  padding: var(--spacing-sm, 0.6rem) var(--spacing-md, 0.8rem);
  border-radius: var(--border-radius-md, 8px);
  background-color: var(--warning-color-bg-light, rgba(217, 119, 6, 0.1));
  margin-top: 0;
  margin-bottom: var(--spacing-lg, 1.25rem);
  font-size: var(--font-size-md, 1rem);
}

.phishing-modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-xl, 1.8rem);
  padding-top: var(--spacing-lg, 1.25rem);
  border-top: 1px solid var(--border-color);
}

.checkbox-container {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: var(--font-size-sm, 0.9rem);
}

.checkbox-container input[type="checkbox"] {
  margin-right: var(--spacing-sm, 0.6rem);
  accent-color: var(--accent-color);
  width: 16px;
  height: 16px;
}
.checkbox-text {
  line-height: 1;
}

.btn-primary {
  background-color: var(--button-bg, var(--accent-color));
  color: var(--button-text, white);
  padding: var(--button-padding-y-lg, 0.7rem) var(--button-padding-x-lg, 1.4rem);
  border-radius: var(--button-border-radius, var(--border-radius-md, 8px));
  border: 1px solid transparent;
  font-weight: 600;
  font-size: var(--button-font-size, 0.95rem);
  cursor: pointer;
  transition: background-color var(--transition-speed), opacity var(--transition-speed);
}

.btn-primary:hover {
  background-color: var(--button-hover, var(--accent-hover));
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
