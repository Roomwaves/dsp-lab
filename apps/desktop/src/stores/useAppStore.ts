import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ToolId = 'rta' | 'tf' | 'spec' | 'coh' | 'flt' | 'gen'
export type Theme = 'light' | 'dark' | 'system'
export type Language = 'en' | 'es'

export const useAppStore = defineStore('app', () => {
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const activeTool = ref<ToolId>('rta')
  const isSettingsOpen = ref(false)
  const theme = ref<Theme>('system')
  const language = ref<Language>('es')

  function setActiveTool(tool: ToolId) {
    activeTool.value = tool
  }

  function toggleSettings() {
    isSettingsOpen.value = !isSettingsOpen.value
  }

  function setTheme(newTheme: Theme) {
    theme.value = newTheme
    if (newTheme !== 'system') {
      document.documentElement.setAttribute('data-theme', newTheme)
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light')
    }
  }

  function setLanguage(newLanguage: Language) {
    language.value = newLanguage
  }

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
