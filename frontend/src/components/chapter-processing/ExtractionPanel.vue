<script setup lang="ts">
/**
 * 角色提取面板
 * 显示提取进度、结果预览和操作按钮
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ProcessingProgress, ChapterExtractionResult } from '@/types'

interface Props {
  progress: ProcessingProgress
  results: ChapterExtractionResult[]
  totalChapters: number
}

interface Emits {
  (e: 'process', options: { startChapter: number; endChapter?: number }): void
  (e: 'process-single', chapterId: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { t } = useI18n()

const progressPercent = computed(() => {
  if (props.totalChapters === 0) return 0
  return Math.round((props.progress.currentChapter / props.totalChapters) * 100)
})

const isProcessing = computed(() => props.progress.status === 'processing')
const isCompleted = computed(() => props.progress.status === 'completed')
const isFailed = computed(() => props.progress.status === 'failed')

const totalEntities = computed(() =>
  props.results.reduce((sum, r) => sum + r.entities.length, 0)
)

const totalAliases = computed(() =>
  props.results.reduce((sum, r) => sum + r.aliasRelations.length, 0)
)

function handleProcessAll(): void {
  emit('process', { startChapter: 1 })
}
</script>

<template>
  <div class="space-y-6">
    <!-- 标题和操作 -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
          {{ t('chapterProcessing.extraction.title') }}
        </h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {{ t('chapterProcessing.extraction.description') }}
        </p>
      </div>
      <button
        @click="handleProcessAll"
        :disabled="isProcessing"
        class="btn-primary flex items-center gap-2"
      >
        <svg
          v-if="isProcessing"
          class="w-4 h-4 animate-spin"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          />
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M13 10V3L4 14h7v7l9-11h-7z"
          />
        </svg>
        {{ isProcessing ? t('chapterProcessing.extraction.processing') : t('chapterProcessing.extraction.startExtraction') }}
      </button>
    </div>

    <!-- 进度条 -->
    <div v-if="isProcessing || isCompleted" class="space-y-2">
      <div class="flex items-center justify-between text-sm">
        <span class="text-gray-600 dark:text-gray-400">{{ progress.message }}</span>
        <span class="font-medium text-gray-900 dark:text-white">{{ progressPercent }}%</span>
      </div>
      <div class="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          class="h-full transition-all duration-300 ease-out rounded-full"
          :class="[
            isCompleted ? 'bg-green-500' : 'bg-primary-500',
            isProcessing ? 'animate-pulse' : '',
          ]"
          :style="{ width: `${progressPercent}%` }"
        />
      </div>
    </div>

    <!-- 错误提示 -->
    <div
      v-if="isFailed"
      class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
      role="alert"
    >
      <div class="flex items-center gap-2 text-red-700 dark:text-red-400">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path
            fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
            clip-rule="evenodd"
          />
        </svg>
        <span class="font-medium">{{ t('chapterProcessing.extraction.extractionFailed') }}</span>
      </div>
      <p class="mt-1 text-sm text-red-600 dark:text-red-300">{{ progress.message }}</p>
    </div>

    <!-- 统计卡片 -->
    <div v-if="results.length > 0" class="grid grid-cols-3 gap-4">
      <div class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div class="text-2xl font-bold text-gray-900 dark:text-white">
          {{ results.length }}
        </div>
        <div class="text-sm text-gray-500 dark:text-gray-400">
          {{ t('chapterProcessing.extraction.processedChapters') }}
        </div>
      </div>
      <div class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div class="text-2xl font-bold text-primary-600 dark:text-primary-400">
          {{ totalEntities }}
        </div>
        <div class="text-sm text-gray-500 dark:text-gray-400">
          {{ t('chapterProcessing.extraction.identifiedEntities') }}
        </div>
      </div>
      <div class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div class="text-2xl font-bold text-amber-600 dark:text-amber-400">
          {{ totalAliases }}
        </div>
        <div class="text-sm text-gray-500 dark:text-gray-400">
          {{ t('chapterProcessing.extraction.aliasRelations') }}
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div
      v-else-if="!isProcessing"
      class="text-center py-12 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
    >
      <svg
        class="w-12 h-12 mx-auto text-gray-400 dark:text-gray-600"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.5"
          d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
        />
      </svg>
      <h4 class="mt-4 text-base font-medium text-gray-900 dark:text-white">
        {{ t('chapterProcessing.extraction.noCharactersYet') }}
      </h4>
      <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
        {{ t('chapterProcessing.extraction.startHint') }}
      </p>
    </div>
  </div>
</template>
