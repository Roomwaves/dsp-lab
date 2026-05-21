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

  // Initialize panel visibility from localStorage
  const savedVisibility = localStorage.getItem('panel-visibility')
  const panelVisibility = ref(savedVisibility ? JSON.parse(savedVisibility) : {
    magnitude: true,
    phase: true,
    coherence: true,
    rta: true,
    waveform: false
  })

  // Bottom tools drawer state
  const savedDrawerOpen = localStorage.getItem('tools-drawer-open')
  const isToolsDrawerOpen = ref(savedDrawerOpen ? JSON.parse(savedDrawerOpen) : false)
  
  const savedDrawerTab = localStorage.getItem('tools-drawer-tab')
  const activeToolsDrawerTab = ref<'generator' | 'filter'>(
    (savedDrawerTab as 'generator' | 'filter') || 'generator'
  )

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

  function togglePanelVisibility(panel: 'magnitude' | 'phase' | 'coherence' | 'rta' | 'waveform') {
    panelVisibility.value[panel] = !panelVisibility.value[panel]
    localStorage.setItem('panel-visibility', JSON.stringify(panelVisibility.value))
  }

  function toggleToolsDrawer() {
    isToolsDrawerOpen.value = !isToolsDrawerOpen.value
    localStorage.setItem('tools-drawer-open', JSON.stringify(isToolsDrawerOpen.value))
  }

  function setToolsDrawerOpen(isOpen: boolean) {
    isToolsDrawerOpen.value = isOpen
    localStorage.setItem('tools-drawer-open', JSON.stringify(isOpen))
  }

  function setActiveToolsDrawerTab(tab: 'generator' | 'filter') {
    activeToolsDrawerTab.value = tab
    localStorage.setItem('tools-drawer-tab', tab)
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
    panelVisibility,
    isToolsDrawerOpen,
    activeToolsDrawerTab,
    setActiveTool,
    toggleSettings,
    togglePanelVisibility,
    toggleToolsDrawer,
    setToolsDrawerOpen,
    setActiveToolsDrawerTab,
    setTheme,
    setLanguage
  }
})
