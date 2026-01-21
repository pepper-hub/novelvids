<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ref, onMounted, onUnmounted } from 'vue'

const { locale } = useI18n()
const showDropdown = ref(false)

const languages = [
  { code: 'zh-CN', name: '中文', flag: '🇨🇳' },
  { code: 'en-US', name: 'English', flag: '🇺🇸' },
]

const currentLanguage = ref(languages.find(lang => lang.code === locale.value) || languages[0])

function changeLanguage(lang: typeof languages[0]) {
  locale.value = lang.code
  currentLanguage.value = lang
  localStorage.setItem('locale', lang.code)
  showDropdown.value = false
}

function toggleDropdown() {
  showDropdown.value = !showDropdown.value
}

// 点击外部区域关闭下拉菜单
function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.language-switcher')) {
    showDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="language-switcher relative">
    <button
      @click="toggleDropdown"
      class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
      type="button"
    >
      <span class="text-xl">{{ currentLanguage.flag }}</span>
      <span class="text-sm text-gray-700 dark:text-gray-300">{{ currentLanguage.name }}</span>
      <svg
        class="w-4 h-4 text-gray-500 dark:text-gray-400 transition-transform"
        :class="{ 'rotate-180': showDropdown }"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="showDropdown"
        class="absolute right-0 mt-2 w-48 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-lg z-50"
      >
        <div class="py-1">
          <button
            v-for="lang in languages"
            :key="lang.code"
            @click="changeLanguage(lang)"
            class="w-full flex items-center gap-3 px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            :class="{
              'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white': currentLanguage.code === lang.code,
              'text-gray-700 dark:text-gray-300': currentLanguage.code !== lang.code,
            }"
          >
            <span class="text-xl">{{ lang.flag }}</span>
            <span>{{ lang.name }}</span>
            <svg
              v-if="currentLanguage.code === lang.code"
              class="w-4 h-4 ml-auto text-primary-500"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fill-rule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>
