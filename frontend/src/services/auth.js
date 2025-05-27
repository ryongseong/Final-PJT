// API service for authentication related calls
import axios from 'axios'

const API_URL = 'http://localhost:8000/accounts/'

// Create axios instance with auth header
const apiClient = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Important for cookies/sessions
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor to add token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Interceptor to refresh token if expired
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // If error is 401 and not a retry, try to refresh token
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) {
          throw new Error('No refresh token available')
        }

        const response = await axios.post(`${API_URL}token/refresh/`, {
          refresh: refreshToken,
        })

        if (response.status === 200) {
          // Save the new token
          localStorage.setItem('access_token', response.data.access)

          // Update the authorization header
          originalRequest.headers['Authorization'] = `Bearer ${response.data.access}`

          // Retry the original request
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        console.error('Token refresh failed', refreshError)
        // Force logout on token refresh failure
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location = '/login'
      }
    }

    return Promise.reject(error)
  },
)

export default {
  // Get current user from localStorage
  getCurrentUser() {
    try {
      const userStr = localStorage.getItem('user')
      return userStr ? JSON.parse(userStr) : null
    } catch (error) {
      console.error('Error parsing user from localStorage', error)
      return null
    }
  },

  // Check if user is logged in
  isLoggedIn() {
    return !!localStorage.getItem('access_token')
  },

  // Check if user is authenticated
  checkAuth: async () => {
    try {
      const response = await apiClient.post('check-auth/')
      return response.data.is_authenticated
    } catch (error) {
      console.error('Auth check failed:', error)
      return false
    }
  }, // Get user profile  // Get user profile
  getProfile: async () => {
    try {
      // Add timestamp to prevent caching
      const response = await apiClient.post(
        'profile/',
        {},
        {
          params: { _t: new Date().getTime() },
        },
      )

      // Import the utility function directly to avoid circular dependencies
      const { processUserWithImage } = await import('@/utils/imageUtils')

      // Process the user data to fix profile image URLs
      const userData = processUserWithImage(response.data.user)
      return userData
    } catch (error) {
      throw error.response?.data || error
    }
  },

  // Register user
  register: async (username, email, password, nickname, age, gender) => {
    try {
      const response = await apiClient.post('register/', {
        username,
        email,
        password,
        nickname,
        age,
        gender,
      })

      if (response.data.tokens) {
        localStorage.setItem('access_token', response.data.tokens.access)
        localStorage.setItem('refresh_token', response.data.tokens.refresh)
        localStorage.setItem('user', JSON.stringify(response.data.user))
      }

      return response.data
    } catch (error) {
      throw error.response?.data || error
    }
  },

  // Login user
  login: async (username, password) => {
    try {
      const response = await apiClient.post('login/', {
        username,
        password,
      })

      if (response.data.tokens) {
        localStorage.setItem('access_token', response.data.tokens.access)
        localStorage.setItem('refresh_token', response.data.tokens.refresh)
        localStorage.setItem('user', JSON.stringify(response.data.user))
      }

      return response.data
    } catch (error) {
      throw error.response?.data || error
    }
  },

  // Logout user
  logout: async () => {
    try {
      await apiClient.post('logout/')
    } catch (error) {
      console.error('Logout error', error)
    } finally {
      // Always clear local storage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  },

  // Google login
  googleLogin: async (code) => {
    try {
      const response = await apiClient.post('google/login/', {
        code,
      })

      if (response.data.tokens) {
        localStorage.setItem('access_token', response.data.tokens.access)
        localStorage.setItem('refresh_token', response.data.tokens.refresh)
        localStorage.setItem('user', JSON.stringify(response.data.user))
      }

      return response.data
    } catch (error) {
      throw error.response?.data || error
    }
  },

  // Kakao login
  kakaoLogin: async (code) => {
    try {
      const response = await apiClient.post('kakao/login/', {
        code,
      })

      if (response.data.tokens) {
        localStorage.setItem('access_token', response.data.tokens.access)
        localStorage.setItem('refresh_token', response.data.tokens.refresh)
        localStorage.setItem('user', JSON.stringify(response.data.user))
      }

      return response.data
    } catch (error) {
      throw error.response?.data || error
    }
  }, // Update user profile
  updateProfile: async (profileData) => {
    try {
      // For file uploads, we need FormData
      if (profileData instanceof FormData) {
        console.log(profileData)
        const response = await axios.post(`${API_URL}update-profile/`, profileData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
          withCredentials: true,
          // Prevent browser caching
          params: { _t: new Date().getTime() },
        })

        // Import the utility function directly to avoid circular dependencies
        const { processUserWithImage } = await import('@/utils/imageUtils')

        // Process the user data to ensure image URLs are absolute
        if (response.data.user) {
          response.data.user = processUserWithImage(response.data.user)
          localStorage.setItem('user', JSON.stringify(response.data.user))
        }

        return response.data
      } else {
        // Regular JSON data
        const response = await apiClient.post('update-profile/', profileData)

        // Import the utility function directly to avoid circular dependencies
        const { processUserWithImage } = await import('@/utils/imageUtils')

        // Process the user data to ensure image URLs are absolute
        if (response.data.user) {
          response.data.user = processUserWithImage(response.data.user)
          localStorage.setItem('user', JSON.stringify(response.data.user))
        }

        return response.data
      }
    } catch (error) {
      console.error('Profile update error:', error.response || error)
      throw error.response?.data || error
    }
  },

  // Reset profile image to default (remove it)
  resetProfileImage: async () => {
    try {
      const response = await apiClient.post('reset-profile-image/', {})

      // Import the utility function directly to avoid circular dependencies
      const { processUserWithImage } = await import('@/utils/imageUtils')

      // Process the user data to ensure image URLs are correct
      if (response.data.user) {
        response.data.user = processUserWithImage(response.data.user)
        localStorage.setItem('user', JSON.stringify(response.data.user))
      }

      return response.data
    } catch (error) {
      console.error('Profile image reset error:', error.response || error)
      throw error.response?.data || error
    }
  },
}
