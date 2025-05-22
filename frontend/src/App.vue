<template>
  <div id="app">
    <header class="app-header" v-if="showHeader">
      <div class="header-container">
        <router-link to="/" class="logo"> FinanceApp </router-link>

        <nav class="main-nav">
          <router-link to="/" class="nav-link">홈</router-link>
          <router-link to="/products" class="nav-link">금융상품</router-link>
          <router-link to="/articles" class="nav-link">커뮤니티</router-link>
          <router-link to="/map" class="nav-link">지도</router-link>
          <router-link v-if="isAdmin" to="/admin" class="nav-link">관리자</router-link>
        </nav>

        <div class="user-menu">
          <template v-if="isLoggedIn">
            <div class="user-dropdown" @click="toggleDropdown" ref="dropdown">
              <div v-if="profileImage" class="user-avatar">
                <img :src="profileImage" alt="프로필" />
              </div>
              <div v-else class="user-initials">
                {{ userInitials }}
              </div>

              <div class="dropdown-menu" v-show="dropdownOpen">
                <div class="dropdown-username">{{ user?.nickname || user?.username }}</div>
                <router-link to="/profile" class="dropdown-item">
                  <i class="icon">👤</i> 프로필 관리
                </router-link>
                <router-link to="/favorites" class="dropdown-item">
                  <i class="icon">⭐</i> 즐겨찾기
                </router-link>
                <div class="dropdown-divider"></div>
                <button @click="logout" class="dropdown-item logout">
                  <i class="icon">🚪</i> 로그아웃
                </button>
              </div>
            </div>
          </template>

          <template v-else>
            <router-link to="/login" class="auth-btn login">로그인</router-link>
            <router-link to="/register" class="auth-btn register">회원가입</router-link>
          </template>
        </div>
      </div>
    </header>

    <main>
      <router-view />
    </main>

    <footer class="app-footer" v-if="showFooter">
      <div class="footer-container">
        <p>&copy; 2025 FinanceApp. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useUserStore } from '@/stores/user'
// import { useRoute } from 'vue-router'

const userStore = useUserStore()
// const route = useRoute()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const isAdmin = computed(() => userStore.isAdmin)
const user = computed(() => userStore.user)
const userInitials = computed(() => userStore.userInitials)
const profileImage = computed(() => userStore.profileImage)

const dropdownOpen = ref(false)
const dropdown = ref(null)

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
  // Check authentication status
  userStore.checkAuth()

  // Add event listener for closing dropdown
  document.addEventListener('click', closeDropdown)
})

onBeforeUnmount(() => {
  // Remove event listener
  document.removeEventListener('click', closeDropdown)
})
</script>

<style>
/* Global styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family:
    'Noto Sans KR',
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    Helvetica,
    Arial,
    sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f5f5f5;
}

a {
  text-decoration: none;
  color: inherit;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex: 1;
}

/* Header styles */
.app-header {
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  color: #4f46e5;
}

.main-nav {
  display: flex;
  gap: 20px;
}

.nav-link {
  font-weight: 500;
  color: #666;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.2s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #4f46e5;
  background-color: #f5f5f8;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 10px;
}

.auth-btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 500;
  transition: all 0.2s;
}

.auth-btn.login {
  color: #4f46e5;
}

.auth-btn.register {
  background-color: #4f46e5;
  color: white;
}

.auth-btn:hover {
  opacity: 0.9;
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
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-initials {
  background-color: #4f46e5;
  color: white;
  font-weight: 600;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 5px);
  right: 0;
  width: 220px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  z-index: 10;
}

.dropdown-username {
  padding: 12px 16px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #eee;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  color: #333;
  transition: background-color 0.2s;
  width: 100%;
  text-align: left;
  border: none;
  background: none;
  font-size: 14px;
  cursor: pointer;
}

.dropdown-item:hover {
  background-color: #f5f5f8;
}

.dropdown-item.logout {
  color: #e53e3e;
}

.dropdown-divider {
  height: 1px;
  background-color: #eee;
  margin: 4px 0;
}

.icon {
  margin-right: 10px;
  font-style: normal;
}

/* Footer styles */
.app-footer {
  background-color: #f9fafb;
  padding: 20px 0;
  border-top: 1px solid #eaeaea;
  margin-top: 60px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  text-align: center;
  color: #666;
  font-size: 14px;
}

/* Media queries */
@media (max-width: 768px) {
  .header-container {
    height: auto;
    flex-wrap: wrap;
    padding: 10px 20px;
  }

  .logo {
    margin-bottom: 10px;
  }

  .main-nav {
    order: 3;
    width: 100%;
    margin-top: 10px;
    justify-content: space-around;
  }
}

@media (max-width: 480px) {
  .auth-btn {
    padding: 6px 12px;
    font-size: 14px;
  }
}
</style>
