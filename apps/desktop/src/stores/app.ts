import { defineStore } from 'pinia';
import { ref } from 'vue';

export type ToolId = 'rta' | 'tf' | 'spec' | 'coh' | 'flt' | 'gen';
export type Theme = 'light' | 'dark';
export type Language = 'en' | 'es';

export const useAppStore = defineStore('app', () => {
  const activeTool = ref<ToolId>('rta');
  const isSettingsOpen = ref(false);
  const theme = ref<Theme>('light');
  const language = ref<Language>('en');

  function setActiveTool(tool: ToolId) {
    activeTool.value = tool;
  }

  function toggleSettings() {
    isSettingsOpen.value = !isSettingsOpen.value;
  }

  function setTheme(newTheme: Theme) {
    theme.value = newTheme;
    document.documentElement.setAttribute('data-theme', newTheme);
  }

  function setLanguage(newLanguage: Language) {
    language.value = newLanguage;
  }

  return {
    activeTool,
    isSettingsOpen,
    theme,
    language,
    setActiveTool,
    toggleSettings,
    setTheme,
    setLanguage
  };
});
