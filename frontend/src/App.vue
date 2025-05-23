<template>
  <div id="app" :class="{ 'dark': isDarkMode }">
    <!-- 피싱 경고 모달 -->
    <div v-if="showPhishingWarning" class="modal-backdrop">
      <div class="modal phishing-warning">
        <div class="modal-header">
          <h3 class="modal-title">⚠️ 금융사기 주의 안내</h3>
        </div>
        <div class="modal-body">
          <p>최근 금융기관을 사칭한 피싱 사이트와 문자 메시지가 증가하고 있습니다.</p>
          <p>본 사이트는 절대 전화나 문자로 금융정보 입력을 요청하지 않습니다.</p>
          <ul class="phishing-tips">
            <li>금융정보를 요구하는 링크를 클릭하지 마세요.</li>
            <li>의심스러운 연락은 즉시 금융감독원(1332)에 신고하세요.</li>
            <li>공식 웹사이트 주소(URL)를 확인하세요.</li>
          </ul>
        </div>
        <div class="modal-footer">
          <label class="dont-show-checkbox">
            <input type="checkbox" v-model="dontShowToday">
            <span>오늘 하루 보지 않기</span>
          </label>
          <button @click="closePhishingWarning" class="btn btn-primary">확인</button>
        </div>
      </div>
    </div>

    <header class="app-header" v-if="showHeader">
      <div class="header-container">
        <router-link to="/" class="logo">
          <span class="logo-text">Bank</span>
          <span class="logo-text-kr">뱅크</span>
        </router-link>

        <nav class="main-nav">
          <router-link to="/" class="nav-link">홈</router-link>
          <router-link to="/products" class="nav-link">금융상품</router-link>
          <router-link to="/articles" class="nav-link">커뮤니티</router-link>
          <router-link to="/map" class="nav-link">지도</router-link>
          <router-link v-if="isAdmin" to="/admin" class="nav-link">관리자</router-link>
        </nav>

        <div class="user-menu">
          <!-- 언어 선택 -->
          <div class="language-selector">
            <button @click="toggleLanguage" class="lang-btn">
              {{ currentLanguage === 'ko' ? 'KR' : 'EN' }}
            </button>
          </div>

          <!-- 다크모드 토글 -->
          <button @click="toggleDarkMode" class="theme-toggle">
            <span v-if="isDarkMode">☀️</span>
            <span v-else>🌙</span>
          </button>

          <template v-if="isLoggedIn">
            <div class="user-dropdown" @click="toggleDropdown" ref="dropdown">
              <div v-if="profileImage" class="user-avatar">
                <img :src="profileImage" alt="프로필" />
              </div>
              <div v-else class="user-initials">
                {{ userInitials }}
              </div>

              <div class="dropdown-menu" v-show="dropdownOpen">
                <router-link to="/profile" class="dropdown-item">
                  <i class="icon">👤</i> {{ currentLanguage === 'ko' ? '프로필 관리' : 'Profile' }}
                </router-link>
                <router-link to="/favorites" class="dropdown-item">
                  <i class="icon">⭐</i> {{ currentLanguage === 'ko' ? '즐겨찾기' : 'Favorites' }}
                </router-link>
                <div class="dropdown-divider"></div>
                <button @click="logout" class="dropdown-item logout">
                  <i class="icon">🚪</i> {{ currentLanguage === 'ko' ? '로그아웃' : 'Logout' }}
                </button>
              </div>
            </div>
          </template>

          <template v-else>
            <router-link to="/login" class="auth-btn login">
              {{ currentLanguage === 'ko' ? '로그인' : 'Login' }}
            </router-link>
            <router-link to="/register" class="auth-btn register">
              {{ currentLanguage === 'ko' ? '회원가입' : 'Register' }}
            </router-link>
          </template>
        </div>
      </div>
    </header>

    <main>
      <router-view />
    </main>

    <footer class="app-footer" v-if="showFooter">
      <div class="footer-container">
        <div class="footer-links">
          <div class="footer-section">
            <h4>{{ currentLanguage === 'ko' ? '뱅크' : 'Bank' }}</h4>
            <ul>
              <li><a href="#">{{ currentLanguage === 'ko' ? '회사 소개' : 'About Us' }}</a></li>
              <li><a href="#">{{ currentLanguage === 'ko' ? '공지사항' : 'Announcements' }}</a></li>
              <li><a href="#">{{ currentLanguage === 'ko' ? '이용약관' : 'Terms of Service' }}</a></li>
              <li><a href="#">{{ currentLanguage === 'ko' ? '개인정보처리방침' : 'Privacy Policy' }}</a></li>
            </ul>
          </div>
          <div class="footer-section">
            <h4>{{ currentLanguage === 'ko' ? '고객센터' : 'Customer Service' }}</h4>
            <ul>
              <li><a href="#">{{ currentLanguage === 'ko' ? '자주 묻는 질문' : 'FAQ' }}</a></li>
              <li><a href="#">{{ currentLanguage === 'ko' ? '1:1 문의' : 'Contact Us' }}</a></li>
              <li><a href="#">{{ currentLanguage === 'ko' ? '금융사기 신고' : 'Report Fraud' }}</a></li>
            </ul>
          </div>
          <div class="footer-section">
            <h4>{{ currentLanguage === 'ko' ? '소셜 미디어' : 'Social Media' }}</h4>
            <div class="social-links">
              <a href="#" class="social-link">Instagram</a>
              <a href="#" class="social-link">Twitter</a>
              <a href="#" class="social-link">Facebook</a>
              <a href="#" class="social-link">LinkedIn</a>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2025 Bank. {{ currentLanguage === 'ko' ? '모든 권리 보유.' : 'All rights reserved.' }}</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'
// import { useRoute } from 'vue-router'

const userStore = useUserStore()
const themeStore = useThemeStore()
// const route = useRoute()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const isAdmin = computed(() => userStore.isAdmin)
const user = computed(() => userStore.user)
const userInitials = computed(() => userStore.userInitials)
const profileImage = computed(() => userStore.profileImage)

const dropdownOpen = ref(false)
const dropdown = ref(null)

// 다크 모드 상태 (전역 스토어 사용)
const isDarkMode = computed(() => themeStore.isDarkMode)
// 언어 설정 (ko: 한국어, en: 영어)
const currentLanguage = ref('ko')

// 피싱 경고 모달
const showPhishingWarning = ref(false)
const dontShowToday = ref(false)

// 다크 모드 토글 함수
const toggleDarkMode = () => {
  themeStore.toggleDarkMode()
}

// 언어 변경 함수
const toggleLanguage = () => {
  currentLanguage.value = currentLanguage.value === 'ko' ? 'en' : 'ko'
  localStorage.setItem('language', currentLanguage.value)
}

// 피싱 경고 모달 닫기
const closePhishingWarning = () => {
  showPhishingWarning.value = false
  if (dontShowToday.value) {
    const now = new Date()
    const expiryDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59)
    localStorage.setItem('phishingWarningDismissed', expiryDate.getTime().toString())
  }
}

// 피싱 경고 모달 표시 여부 확인
const checkPhishingWarning = () => {
  const dismissed = localStorage.getItem('phishingWarningDismissed')
  if (dismissed) {
    const dismissedTime = parseInt(dismissed)
    const now = new Date().getTime()
    if (now > dismissedTime) {
      // 설정된 시간이 지났으면 모달 표시
      localStorage.removeItem('phishingWarningDismissed')
      showPhishingWarning.value = true
    }
  } else {
    // 설정된 적이 없으면 모달 표시
    showPhishingWarning.value = true
  }
}

// Determine if header/footer should be shown based on route
const showHeader = computed(() => {
  // Hide for certain routes if needed
  return true
})

const showFooter = computed(() => {
  // Hide for certain routes if needed
  return true
})

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value
}

const closeDropdown = (event) => {
  if (dropdown.value && !dropdown.value.contains(event.target)) {
    dropdownOpen.value = false
  }
}

const logout = () => {
  userStore.logout()
  dropdownOpen.value = false
}

onMounted(() => {
  // 다크 모드 초기화
  themeStore.initDarkMode()
  
  // 언어 설정 불러오기
  const savedLanguage = localStorage.getItem('language')
  if (savedLanguage) {
    currentLanguage.value = savedLanguage
  }

  // 피싱 경고 모달 확인
  checkPhishingWarning()

  // Check authentication status
  userStore.checkAuth()

  // Add event listener for closing dropdown
  document.addEventListener('click', closeDropdown)
})

onBeforeUnmount(() => {
  // Remove event listener
  document.removeEventListener('click', closeDropdown)
})

// 언어 변경 시 로컬 스토리지에 저장
watch(currentLanguage, (newValue) => {
  localStorage.setItem('language', newValue)
})

// 다크 모드 변경 시 로컬 스토리지에 저장
watch(isDarkMode, (newValue) => {
  localStorage.setItem('darkMode', newValue ? 'true' : 'false')
})
</script>

<style>
/* App.vue 스타일은 메인 스타일시트를 사용하며, 이곳에는 컴포넌트 특화 스타일만 정의합니다 */

/* 헤더 스타일 */
.app-header {
  background-color: var(--color-white);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: background-color var(--transition-normal);
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1.2;
}

.logo-text {
  font-family: var(--font-heading);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--color-accent);
}

.logo-text-kr {
  font-family: var(--font-body);
  font-size: 0.9rem;
  color: var(--color-text-light);
}

.main-nav {
  display: flex;
  gap: 30px;
}

.nav-link {
  font-family: var(--font-body);
  font-weight: 500;
  color: var(--color-text);
  padding: 8px 12px;
  position: relative;
  transition: color var(--transition-fast);
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background-color: var(--color-primary);
  transition: width var(--transition-normal);
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--color-primary);
}

.nav-link:hover::after,
.nav-link.router-link-active::after {
  width: 100%;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 15px;
}

.auth-btn {
  padding: 8px 20px;
  border-radius: 25px;
  font-weight: 500;
  font-family: var(--font-body);
  transition: all var(--transition-normal);
}

.auth-btn.login {
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.auth-btn.register {
  background-color: var(--color-primary);
  color: var(--color-white);
}

.auth-btn:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.language-selector {
  margin-right: 5px;
}

.lang-btn {
  background: none;
  border: 1px solid var(--color-secondary);
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 12px;
  cursor: pointer;
  color: var(--color-text);
  transition: all var(--transition-fast);
}

.lang-btn:hover {
  background-color: var(--color-secondary);
}

.theme-toggle {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px;
  transition: transform var(--transition-fast);
}

.theme-toggle:hover {
  transform: rotate(15deg);
}

.user-dropdown {
  position: relative;
  cursor: pointer;
}

.user-avatar,
.user-initials {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--transition-fast);
}

.user-avatar:hover,
.user-initials:hover {
  transform: scale(1.1);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-initials {
  background-color: var(--color-primary);
  color: var(--color-white);
  font-weight: 600;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 220px;
  background-color: var(--color-white);
  border-radius: 8px;
  box-shadow: var(--shadow-md);
  overflow: hidden;
  z-index: 10;
  animation: slideInUp var(--transition-normal);
}

.dropdown-username {
  padding: 15px;
  font-weight: 600;
  color: var(--color-text);
  border-bottom: 1px solid var(--color-secondary);
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  color: var(--color-text);
  transition: background-color var(--transition-fast);
  width: 100%;
  text-align: left;
  border: none;
  background: none;
  font-size: 14px;
  cursor: pointer;
}

.dropdown-item:hover {
  background-color: var(--color-secondary);
}

.dropdown-item.logout {
  color: var(--color-error);
}

.dropdown-divider {
  height: 1px;
  background-color: var(--color-secondary);
  margin: 5px 0;
}

.icon {
  margin-right: 10px;
  font-style: normal;
}

/* 푸터 스타일 */
.app-footer {
  background-color: var(--color-background-end);
  padding: 50px 0 20px;
  border-top: 1px solid var(--color-secondary);
  margin-top: 60px;
  transition: background-color var(--transition-normal);
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.footer-section h4 {
  font-family: var(--font-heading);
  font-size: 1.2rem;
  margin-bottom: 20px;
  color: var(--color-accent);
}

.footer-section ul {
  list-style: none;
  padding: 0;
}

.footer-section ul li {
  margin-bottom: 10px;
}

.footer-section ul li a {
  color: var(--color-text);
  transition: color var(--transition-fast);
}

.footer-section ul li a:hover {
  color: var(--color-primary);
}

.social-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.social-link {
  padding: 5px 10px;
  background-color: var(--color-secondary);
  border-radius: 4px;
  font-size: 14px;
  transition: all var(--transition-fast);
}

.social-link:hover {
  background-color: var(--color-primary);
  color: var(--color-white);
}

.footer-bottom {
  padding-top: 20px;
  border-top: 1px solid var(--color-secondary);
  text-align: center;
  color: var(--color-text-light);
  font-size: 14px;
}

/* 피싱 경고 모달 스타일 */
.phishing-warning .modal-header {
  border-bottom-color: #f0ad4e;
}

.phishing-warning .modal-title {
  color: #8a6d3b;
}

.phishing-tips {
  margin: 15px 0;
  padding-left: 20px;
}

.phishing-tips li {
  margin-bottom: 10px;
}

.dont-show-checkbox {
  display: flex;
  align-items: center;
  margin-right: auto;
  font-size: 14px;
  color: var(--color-text-light);
  cursor: pointer;
}

.dont-show-checkbox input {
  margin-right: 8px;
}

/* 미디어 쿼리 */
@media (max-width: 992px) {
  .header-container {
    padding: 0 15px;
  }
  
  .main-nav {
    gap: 15px;
  }
  
  .nav-link {
    padding: 8px;
  }
}

@media (max-width: 768px) {
  .header-container {
    height: auto;
    flex-wrap: wrap;
    padding: 15px;
  }
  
  .logo {
    margin-bottom: 10px;
  }
  
  .main-nav {
    order: 3;
    width: 100%;
    margin-top: 15px;
    justify-content: space-between;
  }
  
  .footer-links {
    grid-template-columns: 1fr;
    text-align: center;
  }
  
  .social-links {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .user-menu {
    gap: 8px;
  }
  
  .auth-btn {
    padding: 6px 12px;
    font-size: 14px;
  }
  
  .language-selector,
  .theme-toggle {
    margin-right: 5px;
  }
}
</style>
