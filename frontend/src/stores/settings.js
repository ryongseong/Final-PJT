import { defineStore } from 'pinia'
import { ref, inject } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  // 다크모드 설정
  const isDarkMode = ref(false)
  
  // API 키 설정
  const apiKeys = ref({
    bokApiKey: localStorage.getItem('bokApiKey') || '',
    exchangeRateApiKey: localStorage.getItem('exchangeRateApiKey') || ''
  })
  
  // 다크모드 전환
  function toggleDarkMode() {
    try {
      isDarkMode.value = !isDarkMode.value
      
      if (isDarkMode.value) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
      
      // 사용자 설정 저장
      localStorage.setItem('darkMode', isDarkMode.value ? 'dark' : 'light')
      
      // 다크모드 변경 이벤트 발생
      window.dispatchEvent(new CustomEvent('themeChanged', { 
        detail: { isDark: isDarkMode.value } 
      }))
      
      console.log('Theme toggled to:', isDarkMode.value ? 'dark' : 'light')
      return true
    } catch (error) {
      console.error('Error toggling dark mode:', error)
      return false
    }
  }
  
  // 초기화 함수
  function initTheme() {
    try {
      // 사용자 저장 설정 확인
      const savedTheme = localStorage.getItem('darkMode')
      
      // 시스템 다크모드 설정 확인
      const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      
      if (savedTheme === 'dark' || (savedTheme === null && prefersDark)) {
        isDarkMode.value = true
        document.documentElement.classList.add('dark')
      } else {
        isDarkMode.value = false
        document.documentElement.classList.remove('dark')
      }
      
      console.log('Theme initialized to:', isDarkMode.value ? 'dark' : 'light')
      return isDarkMode.value
    } catch (error) {
      console.error('Error initializing theme:', error)
      return false
    }
  }
  
  // 언어 설정
  function toggleLanguage() {
    try {
      // i18n 직접 import
      const i18n = window.i18nInstance
      if (!i18n) {
        console.error('i18n instance not found')
        return false
      }
      
      // 현재 언어가 한국어면 영어로, 영어면 한국어로
      const currentLocale = i18n.global.locale.value
      const newLocale = currentLocale === 'ko' ? 'en' : 'ko'
      
      console.log('Changing language from', currentLocale, 'to', newLocale)
      
      // 언어 변경
      i18n.global.locale.value = newLocale
      
      // 사용자 설정 저장
      localStorage.setItem('language', newLocale)
      
      // 페이지 새로고침 없이 즉시 언어 변경이 적용되도록 강제 업데이트
      window.dispatchEvent(new CustomEvent('languageChanged', { detail: { locale: newLocale } }))
      
      // 언어 변경 후 다시 로드해야 하는 컴포넌트가 있을 수 있으므로 이벤트 발생
      document.dispatchEvent(new CustomEvent('localeChanged', { detail: { locale: newLocale } }))
      
      console.log('Language changed to:', newLocale)
      
      return true
    } catch (error) {
      console.error('Error toggling language:', error)
      return false
    }
  }
  
  // 초기 언어 설정
  function initLanguage() {
    try {
      const i18n = window.i18nInstance
      const savedLanguage = localStorage.getItem('language')
      
      if (savedLanguage) {
        console.log('Initializing language to:', savedLanguage)
        i18n.global.locale.value = savedLanguage
      } else {
        // 기본값으로 한국어 설정
        console.log('No saved language, defaulting to Korean')
        i18n.global.locale.value = 'ko'
        localStorage.setItem('language', 'ko')
      }
      
      return i18n.global.locale.value
    } catch (error) {
      console.error('Error initializing language:', error)
      return 'ko' // 오류 발생 시 기본값
    }
  }

  // API 키 설정 함수
  function setApiKey(keyType, value) {
    try {
      if (keyType === 'bok') {
        apiKeys.value.bokApiKey = value
        localStorage.setItem('bokApiKey', value)
      } else if (keyType === 'exchangeRate') {
        apiKeys.value.exchangeRateApiKey = value
        localStorage.setItem('exchangeRateApiKey', value)
      }
      return true
    } catch (error) {
      console.error(`Error setting ${keyType} API key:`, error)
      return false
    }
  }

  // API 키 가져오기 함수
  function getApiKey(keyType) {
    try {
      if (keyType === 'bok') {
        return apiKeys.value.bokApiKey
      } else if (keyType === 'exchangeRate') {
        return apiKeys.value.exchangeRateApiKey
      }
      return ''
    } catch (error) {
      console.error(`Error getting ${keyType} API key:`, error)
      return ''
    }
  }

  return { 
    isDarkMode, 
    apiKeys,
    toggleDarkMode, 
    initTheme,
    toggleLanguage,
    initLanguage,
    setApiKey,
    getApiKey
  }
})