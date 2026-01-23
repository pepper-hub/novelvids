<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores'
import { fetchDashboardStats } from '@/api/dashboard'
import type { DashboardStats } from '@/types'

const { t } = useI18n()
const authStore = useAuthStore()

const isLoading = ref(true)
const dashboardData = ref<DashboardStats>({
  total_novels: 0,
  total_videos: 0,
  processing_time: 0,
  balance: 0,
  recent_novels: [],
})

const stats = computed(() => [
  { label: t('dashboard.stats.totalNovels'), value: dashboardData.value.total_novels.toString(), change: '' },
  { label: t('dashboard.stats.totalVideos'), value: dashboardData.value.total_videos.toString(), change: '' },
  { label: t('dashboard.stats.processingTasks'), value: `${dashboardData.value.processing_time}h`, change: '' },
  { label: t('dashboard.stats.accountBalance'), value: `$${dashboardData.value.balance.toFixed(2)}`, change: '' },
])

onMounted(async () => {
  try {
    isLoading.value = true
    dashboardData.value = await fetchDashboardStats()
  } catch (error) {
    console.error('Failed to fetch dashboard stats:', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ t('dashboard.title') }}</h1>
      <p class="text-gray-500 dark:text-gray-400 mt-1">{{ t('dashboard.welcome', { username: authStore.user?.username || '' }) }}</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div
        v-for="stat in stats"
        :key="stat.label"
        class="card p-6"
      >
        <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ stat.label }}</p>
        <div class="flex items-baseline gap-2 mt-2">
          <span class="text-3xl font-bold text-gray-900 dark:text-white">{{ stat.value }}</span>
          <span v-if="stat.change" class="text-sm text-green-500">{{ stat.change }}</span>
        </div>
      </div>
    </div>

    <div class="grid lg:grid-cols-2 gap-6">
      <div class="card p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('dashboard.recentNovels') }}</h2>
        
        <div v-if="isLoading" class="flex justify-center py-12">
           <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div>
        </div>

        <div v-else-if="dashboardData.recent_novels.length > 0" class="space-y-4">
          <router-link
            v-for="novel in dashboardData.recent_novels"
            :key="novel.id"
            :to="`/novels/${novel.id}`"
            class="block p-4 rounded-lg bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <div class="flex justify-between items-start">
              <div>
                <h3 class="font-medium text-gray-900 dark:text-white">{{ novel.title }}</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {{ novel.totalChapters ?? novel.total_chapters }} {{ t('novels.chapters') }} • {{ novel.processedChapters ?? novel.processed_chapters }} {{ t('novels.processedChapters') }}
                </p>
              </div>
              <span 
                class="px-2 py-1 text-xs font-medium rounded-full"
                :class="{
                  'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400': novel.status === 'pending',
                  'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400': novel.status === 'completed',
                  'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400': novel.status === 'failed',
                  'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400': (novel.status as string) === 'processing'
                }"
              >
                {{ t(`novels.novelStatus.${novel.status}`) }}
              </span>
            </div>
          </router-link>
        </div>

        <div v-else class="text-center py-12 text-gray-500 dark:text-gray-400">
          <svg class="w-12 h-12 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p>{{ t('common.noData') }}</p>
        </div>
      </div>

      <div class="card p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('dashboard.quickActions') }}</h2>
        <div class="space-y-3">
          <router-link to="/novels" class="flex items-center gap-4 p-4 rounded-lg bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
            <div class="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-900 dark:text-white">{{ t('dashboard.uploadNovel') }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('novels.uploadFirst') }}</p>
            </div>
          </router-link>

          <router-link to="/generate" class="flex items-center gap-4 p-4 rounded-lg bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
            <div class="w-10 h-10 bg-accent-100 dark:bg-accent-900/30 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-accent-600 dark:text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-900 dark:text-white">{{ t('dashboard.generateVideo') }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('generate.options') }}</p>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>
