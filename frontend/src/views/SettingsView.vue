<template>
  <div class="settings-page container">
    <h1 class="page-title">{{ $t('settings.title') }}</h1>
    
    <div class="settings-grid">
      <!-- API 키 설정 섹션 -->
      <ApiKeySettings />
      
      <!-- 테마 설정 섹션 -->
      <div class="settings-card">
        <h3 class="settings-title">{{ $t('settings.themeSettings') }}</h3>
        <p class="settings-description">{{ $t('settings.themeSettingsDescription') }}</p>
        
        <div class="theme-settings">
          <div class="theme-option">
            <label for="darkModeToggle">{{ $t('common.darkMode') }}</label>
            <div class="toggle-switch">
              <input 
                type="checkbox" 
                id="darkModeToggle" 
                :checked="settingsStore.isDarkMode"
                @change="settingsStore.toggleDarkMode"
              />
              <span class="toggle-slider"></span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 언어 설정 섹션 -->
      <div class="settings-card">
        <h3 class="settings-title">{{ $t('settings.languageSettings') }}</h3>
        <p class="settings-description">{{ $t('settings.languageSettingsDescription') }}</p>
        
        <div class="language-settings">
          <div class="language-option">
            <span class="current-language">{{ currentLanguage }}</span>
            <button @click="settingsStore.toggleLanguage" class="language-toggle-btn">
              {{ $t('settings.switchLanguage') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useSettingsStore } from '@/stores/settings';
import { useI18n } from 'vue-i18n';
import ApiKeySettings from '@/components/settings/ApiKeySettings.vue';

const settingsStore = useSettingsStore();
const { locale } = useI18n();

// 현재 언어 표시
const currentLanguage = computed(() => {
  return locale.value === 'ko' ? '한국어' : 'English';
});
</script>

<style scoped>
.settings-page {
  padding: 2rem 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-family: 'Pretendard Variable', serif;
  font-size: 2.5rem;
  margin-bottom: 2rem;
  color: var(--text-primary);
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 1rem;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
}

.settings-card {
  background-color: var(--card-bg);
  border-radius: 16px;
  padding: 1.5rem;
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

/* 테마 설정 스타일 */
.theme-option, .language-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 34px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: var(--accent-color);
}

input:focus + .toggle-slider {
  box-shadow: 0 0 1px var(--accent-color);
}

input:checked + .toggle-slider:before {
  transform: translateX(26px);
}

/* 언어 설정 스타일 */
.current-language {
  font-weight: 500;
}

.language-toggle-btn {
  background-color: var(--accent-color);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.language-toggle-btn:hover {
  background-color: var(--accent-hover);
  transform: translateY(-2px);
}

/* 반응형 */
@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .page-title {
    font-size: 2rem;
  }
}
</style>