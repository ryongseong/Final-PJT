import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import i18n from './i18n' // i18n 추가
import './assets/variables.css' // CSS 변수 파일 import

// Import Vue Toast Notification
import ToastPlugin from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'

// Font imports are now handled via Google Fonts in index.html

import { library } from '@fortawesome/fontawesome-svg-core'
import { faHeart as fasHeart, faMoon, faSun, faGlobe } from '@fortawesome/free-solid-svg-icons'
import { faHeart as farHeart } from '@fortawesome/free-regular-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

// particles.js는 이제 index.html에서 CDN으로 로드됩니다

library.add(fasHeart, farHeart, faMoon, faSun, faGlobe)

// i18n 인스턴스를 전역에서 접근 가능하도록 설정
window.i18nInstance = i18n

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ToastPlugin)
app.use(i18n) // i18n 사용
app.component('font-awesome-icon', FontAwesomeIcon)

app.mount('#app')
