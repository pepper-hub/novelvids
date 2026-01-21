import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN'
import enUS from './locales/en-US'

// Get saved language from localStorage or use browser language
const savedLocale = localStorage.getItem('locale')
const browserLocale = navigator.language

// Determine initial locale
let initialLocale = 'zh-CN'
if (savedLocale) {
    initialLocale = savedLocale
} else if (browserLocale.startsWith('en')) {
    initialLocale = 'en-US'
}

const i18n = createI18n({
    legacy: false, // Use Composition API mode
    locale: initialLocale,
    fallbackLocale: 'en-US',
    messages: {
        'zh-CN': zhCN,
        'en-US': enUS,
    },
    globalInjection: true, // Enable global $t
})

export default i18n
