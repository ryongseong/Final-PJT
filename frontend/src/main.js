import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import { useKakao } from 'vue3-kakao-maps/@utils'

const app = createApp(App)

const API_KEY = import.meta.env.VITE_KAKAO_API
useKakao(API_KEY)

app.use(createPinia())
app.use(router)

app.mount('#app')
