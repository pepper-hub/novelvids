<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores'
import LanguageSwitcher from '../LanguageSwitcher.vue'

const { t } = useI18n()

const emit = defineEmits<{
  toggleSidebar: []
}>()

const router = useRouter()
const authStore = useAuthStore()

function handleLogout(): void {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <header class="sticky top-0 z-30 h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
    <div class="flex items-center justify-between h-full px-4">
      <button
        @click="emit('toggleSidebar')"
        class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      <div class="flex items-center gap-4">
        <LanguageSwitcher />
        
        <button class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        </button>

        <div class="relative">
          <button
            @click="handleLogout"
            class="flex items-center gap-2 px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors"
          >
            <div class="w-8 h-8 bg-gradient-to-br from-primary-400 to-accent-400 rounded-full flex items-center justify-center">
              <span class="text-white text-sm font-medium">U</span>
            </div>
            <span class="text-sm font-medium">{{ t('auth.logout') }}</span>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
