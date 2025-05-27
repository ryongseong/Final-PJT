// User auth store using Pinia
import { defineStore } from 'pinia'
import authService from '@/services/auth'
import router from '@/router'
// Integrate with imageUtils for consistent image URL handling
// import { processUserWithImage } from '@/utils/imageUtils'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: authService.getCurrentUser(),
    loading: false,
    error: null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.user,
    isAdmin: (state) => state.user && (state.user.is_admin || state.user.is_superuser),
    userInitials: (state) => {
      if (!state.user) return ''
      if (state.user.nickname) {
        return state.user.nickname.charAt(0).toUpperCase()
      }
      return state.user.username.charAt(0).toUpperCase()
    },
    profileImage: (state) => {
      if (!state.user) return null
      return state.user.profile_img
    },
  },

  actions: {
    async register(userData) {
      this.loading = true
      this.error = null
      try {
        const { username, email, password, nickname, age, gender } = userData
        const response = await authService.register(
          username,
          email,
          password,
          nickname,
          age,
          gender,
        )
        this.user = response.user
        router.push('/')
        return response
      } catch (error) {
        this.error = error.error || 'Registration failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    async login(username, password) {
      this.loading = true
      this.error = null
      try {
        const response = await authService.login(username, password)
        this.user = response.user
        router.push('/')
        return response
      } catch (error) {
        this.error = error.error || 'Login failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    async googleLogin(token) {
      this.loading = true
      this.error = null
      try {
        const response = await authService.googleLogin(token)
        this.user = response.user
        router.push('/')
        return response
      } catch (error) {
        this.error = error.error || 'Google login failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    async kakaoLogin(code) {
      this.loading = true
      this.error = null
      try {
        const response = await authService.kakaoLogin(code)
        this.user = response.user
        router.push('/')
        return response
      } catch (error) {
        this.error = error.error || 'Kakao login failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout() {
      this.loading = true
      try {
        await authService.logout()
        this.user = null
        router.push('/login')
      } catch (error) {
        console.error('Logout error', error)
      } finally {
        this.loading = false
      }
    },

    async updateProfile(profileData) {
      this.loading = true
      this.error = null
      try {
        // If we're updating with FormData (including images), log the process
        if (profileData instanceof FormData) {
          // Check if there's an image in the FormData
          let hasImage = false
          if (profileData.has('profile_img')) {
            hasImage = true
          }

          // If there's an image, we need to make sure caching doesn't interfere
          if (hasImage) {
            console.log('Image update detected, adding cache-busting')
          }
        }

        const response = await authService.updateProfile(profileData)

        // Import the processUserWithImage function directly to avoid circular dependencies
        const { processUserWithImage } = await import('@/utils/imageUtils')

        // Process the user data to ensure image URLs are correct
        if (response && response.user) {
          response.user = processUserWithImage(response.user)
          this.user = response.user
        }

        return response
      } catch (error) {
        this.error = error.error || 'Profile update failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchUserProfile() {
      this.loading = true
      try {
        const userData = await authService.getProfile()

        // Import the processUserWithImage function directly to avoid circular dependencies
        const { processUserWithImage } = await import('@/utils/imageUtils')

        // Process user data to ensure image URLs are consistent
        this.user = processUserWithImage(userData)
        return userData
      } catch (error) {
        console.error('Error fetching user profile', error)
        if (error.response?.status === 401) {
          this.user = null
        }
      } finally {
        this.loading = false
      }
    },

    async checkAuth() {
      try {
        const isAuthenticated = await authService.checkAuth()
        if (!isAuthenticated) {
          this.user = null
        } else if (!this.user) {
          // If authenticated but no user data, fetch it
          await this.fetchUserProfile()
        }
        return isAuthenticated
      } catch (error) {
        console.error('Auth check error', error)
        this.user = null
        return false
      }
    },

    setUser(user) {
      this.user = user
    },

    async resetProfileImage() {
      this.loading = true
      this.error = null
      try {
        const response = await authService.resetProfileImage()

        // Import the processUserWithImage function directly to avoid circular dependencies
        const { processUserWithImage } = await import('@/utils/imageUtils')

        // Process the user data to ensure image URLs are correct
        if (response && response.user) {
          response.user = processUserWithImage(response.user)
          this.user = response.user
        }

        return response
      } catch (error) {
        this.error = error.error || 'Profile image reset failed'
        throw error
      } finally {
        this.loading = false
      }
    },
  },
})
