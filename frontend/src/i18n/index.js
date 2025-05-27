import { createI18n } from 'vue-i18n'
import translations from './translations'

const i18n = createI18n({
  locale: localStorage.getItem('language') || 'ko', // 기본 언어 설정 (저장된 설정 확인)
  fallbackLocale: 'en', // 번역이 없을 경우 대체 언어
  messages: translations,
  legacy: false, // Vue 3 Composition API와 함께 사용
  globalInjection: true, // 전역 주입 활성화
  silentTranslationWarn: false, // 번역 누락 경고 활성화 (개발 중 유용)
  silentFallbackWarn: false // 폴백 경고 활성화 (개발 중 유용)
})

export default i18n