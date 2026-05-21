import { defineStore } from 'pinia'
import { ref } from 'vue'
import { i18n } from '../i18n'

export type ToolId = 'rta' | 'tf' | 'spec' | 'coh' | 'flt' | 'gen'
export type Theme = 'light' | 'dark' | 'system'
export type Language = 'en' | 'es'

export const useAppStore = defineStore('app', () => {
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const activeTool = ref<ToolId>('rta')
  const isSettingsOpen = ref(false)

  // Initialize theme from localStorage
  const savedTheme = (localStorage.getItem('app-theme') as Theme) || 'system'
  const theme = ref<Theme>(savedTheme)
  
  // Initialize language from localStorage
  const savedLanguage = (localStorage.getItem('app-language') as Language) || 'es'
  const language = ref<Language>(savedLanguage)

  function setActiveTool(tool: ToolId) {
    activeTool.value = tool
  }

  function toggleSettings() {
    isSettingsOpen.value = !isSettingsOpen.value
  }

  function setTheme(newTheme: Theme) {
    theme.value = newTheme
    localStorage.setItem('app-theme', newTheme)
    if (newTheme !== 'system') {
      document.documentElement.setAttribute('data-theme', newTheme)
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light')
    }
  }

  function setLanguage(newLanguage: Language) {
    language.value = newLanguage
    localStorage.setItem('app-language', newLanguage)
    // @ts-ignore
    i18n.global.locale.value = newLanguage
  }

  // Apply initial theme
  setTheme(theme.value)

  return {
    isLoading,
    error,
    activeTool,
    isSettingsOpen,
    theme,
    language,
    setActiveTool,
    toggleSettings,
    setTheme,
    setLanguage
  }
})
