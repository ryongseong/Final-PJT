// Theme store for managing dark mode
import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    darkMode: localStorage.getItem('darkMode') === 'true',
  }),

  getters: {
    isDarkMode: (state) => state.darkMode,
  },

  actions: {
    toggleDarkMode() {
      this.darkMode = !this.darkMode
      this.applyDarkMode()
      localStorage.setItem('darkMode', this.darkMode)
    },
    
    initDarkMode() {
      // Initialize dark mode from localStorage or user preference
      const savedDarkMode = localStorage.getItem('darkMode') === 'true'
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      
      this.darkMode = savedDarkMode !== null ? savedDarkMode : prefersDark
      this.applyDarkMode()
    },
    
    applyDarkMode() {
      // Apply dark mode to document
      if (this.darkMode) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  }
})