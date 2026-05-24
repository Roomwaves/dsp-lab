import { createI18n } from 'vue-i18n'
import es from './locales/es.json'
import en from './locales/en.json'

const savedLanguage = localStorage.getItem('app-language') || 'es'

export const i18n = createI18n({
  legacy: false,
  locale: savedLanguage,
  fallbackLocale: 'es',
  messages: {
    es,
    en
  }
})
