<template>
  <div class="api-key-settings card">
    <h3 class="settings-title">{{ $t('settings.apiSettings') }}</h3>
    <p class="settings-description">{{ $t('settings.apiSettingsDescription') }}</p>
    
    <div class="api-key-form">
      <div class="form-group">
        <label for="bokApiKey">{{ $t('settings.bokApiKey') }}</label>
        <div class="input-with-button">
          <input 
            :type="showBokKey ? 'text' : 'password'" 
            id="bokApiKey" 
            v-model="bokApiKey" 
            :placeholder="$t('settings.enterApiKey')"
          />
          <button @click="toggleBokKeyVisibility" class="toggle-visibility-btn">
            <i :class="showBokKey ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
          </button>
        </div>
      </div>
      
      <div class="form-group">
        <label for="exchangeRateApiKey">{{ $t('settings.exchangeRateApiKey') }}</label>
        <div class="input-with-button">
          <input 
            :type="showExchangeKey ? 'text' : 'password'" 
            id="exchangeRateApiKey" 
            v-model="exchangeRateApiKey" 
            :placeholder="$t('settings.enterApiKey')"
          />
          <button @click="toggleExchangeKeyVisibility" class="toggle-visibility-btn">
            <i :class="showExchangeKey ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
          </button>
        </div>
      </div>
      
      <div class="button-group">
        <button @click="saveApiKeys" class="save-btn">
          {{ $t('settings.saveApiKeys') }}
        </button>
        <button @click="clearApiKeys" class="clear-btn">
          {{ $t('settings.clearApiKeys') }}
        </button>
      </div>
    </div>
    
    <div v-if="saveStatus" :class="['save-status', saveStatus === 'success' ? 'success' : 'error']">
      {{ saveMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useSettingsStore } from '@/stores/settings';
import { useI18n } from 'vue-i18n';

const settingsStore = useSettingsStore();
const { t } = useI18n();

// 입력값 상태
const bokApiKey = ref('');
const exchangeRateApiKey = ref('');
const showBokKey = ref(false);
const showExchangeKey = ref(false);
const saveStatus = ref('');
const saveMessage = ref('');

// 초기화
onMounted(() => {
  loadApiKeys();
});

// API 키 불러오기
const loadApiKeys = () => {
  bokApiKey.value = settingsStore.getApiKey('bok');
  exchangeRateApiKey.value = settingsStore.getApiKey('exchangeRate');
};

// API 키 저장
const saveApiKeys = () => {
  try {
    settingsStore.setApiKey('bok', bokApiKey.value);
    settingsStore.setApiKey('exchangeRate', exchangeRateApiKey.value);
    
    saveStatus.value = 'success';
    saveMessage.value = t('settings.apiKeysSaved');
    
    // 저장 성공 메시지 3초 후 사라짐
    setTimeout(() => {
      saveStatus.value = '';
      saveMessage.value = '';
    }, 3000);
    
  } catch (error) {
    console.error('API 키 저장 중 오류 발생:', error);
    
    saveStatus.value = 'error';
    saveMessage.value = t('settings.apiKeysError');
  }
};

// API 키 초기화
const clearApiKeys = () => {
  bokApiKey.value = '';
  exchangeRateApiKey.value = '';
  settingsStore.setApiKey('bok', '');
  settingsStore.setApiKey('exchangeRate', '');
  
  saveStatus.value = 'success';
  saveMessage.value = t('settings.apiKeysCleared');
  
  // 초기화 성공 메시지 3초 후 사라짐
  setTimeout(() => {
    saveStatus.value = '';
    saveMessage.value = '';
  }, 3000);
};

// 비밀번호 표시 전환
const toggleBokKeyVisibility = () => {
  showBokKey.value = !showBokKey.value;
};

const toggleExchangeKeyVisibility = () => {
  showExchangeKey.value = !showExchangeKey.value;
};
</script>

<style scoped>
.api-key-settings {
  background-color: var(--card-bg);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
}

.settings-title {
  font-family: 'Pretendard Variable', serif;
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.settings-description {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-primary);
}

.input-with-button {
  display: flex;
  position: relative;
}

.input-with-button input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 0.95rem;
  background-color: var(--card-bg);
  color: var(--text-primary);
}

.toggle-visibility-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
}

.button-group {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.save-btn, .clear-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-btn {
  background-color: var(--accent-color);
  color: white;
  border: none;
}

.save-btn:hover {
  background-color: var(--accent-hover);
  transform: translateY(-2px);
}

.clear-btn {
  background-color: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.clear-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.save-status {
  margin-top: 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  text-align: center;
}

.save-status.success {
  background-color: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.save-status.error {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* 다크 모드 */
.dark .input-with-button input {
  background-color: var(--card-bg);
  color: var(--text-primary);
}

.dark .clear-btn:hover {
  background-color: rgba(255, 255, 255, 0.05);
}
</style>